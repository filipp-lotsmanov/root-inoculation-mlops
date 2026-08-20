/**
 * Server-side proxy for Prometheus range queries.
 *
 * Mirrors the backend proxy in app/api/[...path]/route.ts, for the same two
 * reasons:
 *
 * 1. PROMETHEUS_URL is a plain server-side env var (no NEXT_PUBLIC_ prefix), so
 *    it is read at runtime, not inlined at build time. The same frontend image
 *    therefore works in local, on-prem and cloud with only the env var changed.
 *
 * 2. Prometheus is never exposed to the browser. The browser only ever talks to
 *    the Next.js origin, which keeps Prometheus on the internal network (in
 *    cloud it sits behind ACA internal ingress) and avoids any CORS setup.
 *
 * Authentication
 * --------------
 * The session cookie is validated against the backend's /auth/me, not merely
 * checked for presence. A presence check meant any value at all — including a
 * made-up one — granted a caller the ability to run arbitrary PromQL against
 * the internal TSDB, because this route never reaches the backend and so
 * nothing else ever validated the cookie.
 *
 * Batching
 * --------
 * POST accepts several queries in one request. The dashboard needs seven
 * series per refresh; as seven separate GETs on a 15s timer that was 28
 * requests/minute, which both exceeded the backend's default rate limit and
 * multiplied the /auth/me validation cost. One batched POST is 4/minute.
 *
 * Response shapes, per query, in request order:
 *   { status: "disabled" }            -> PROMETHEUS_URL not set in this env
 *   { status: "success", data: ... }  -> passed through from Prometheus
 *   { status: "error", error: ... }   -> bad request, or Prometheus unreachable
 */
import { NextRequest, NextResponse } from "next/server";

// Trailing slashes are stripped so `${PROM}/api/...` never doubles up.
const PROM = (process.env.PROMETHEUS_URL || "").replace(/\/+$/, "");

// Server-side base URL for the backend, same value the catch-all proxy uses.
const BACKEND = (process.env.BACKEND_URL || "http://localhost:8000").replace(
  /\/+$/,
  "",
);

// Backend session cookie name (api/auth/dependencies.py SESSION_COOKIE_NAME).
const SESSION_COOKIE = "session_id";

// Upper bound on a single batch. Prevents a caller turning one authenticated
// request into an unbounded fan-out against Prometheus.
const MAX_QUERIES = 12;

type PromResult =
  | { status: "disabled" }
  | { status: "success"; data: unknown }
  | { status: "error"; error: string };

/**
 * Validate the caller's credentials against the backend.
 *
 * Forwards the cookie and API key to /auth/me and reports whether the backend
 * accepted them. Any transport failure is treated as unauthenticated: failing
 * closed is the right default for an endpoint that fronts internal metrics.
 */
async function isAuthenticated(req: NextRequest): Promise<boolean> {
  const cookie = req.headers.get("cookie");
  const apiKey = req.headers.get("x-api-key");
  if (!req.cookies.get(SESSION_COOKIE) && !apiKey) {
    return false;
  }

  const headers: Record<string, string> = {};
  if (cookie) headers["cookie"] = cookie;
  if (apiKey) headers["x-api-key"] = apiKey;

  try {
    const res = await fetch(`${BACKEND}/auth/me`, {
      headers,
      signal: AbortSignal.timeout(5_000),
      cache: "no-store",
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Run one range query against Prometheus and normalise the outcome.
 */
async function runQuery(
  query: string,
  start: string,
  end: string,
  step: string,
): Promise<PromResult> {
  const url =
    `${PROM}/api/v1/query_range?query=${encodeURIComponent(query)}` +
    `&start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}` +
    `&step=${encodeURIComponent(step)}`;

  try {
    // 10s ceiling: a range query over a small TSDB is fast; if Prometheus is
    // wedged we want a clean error, not a hung dashboard tile.
    const upstream = await fetch(url, { signal: AbortSignal.timeout(10_000) });
    const body = await upstream.json().catch(() => null);
    if (!body) {
      return {
        status: "error",
        error: "Prometheus returned a non-JSON response.",
      };
    }
    if (body.status === "success") {
      return { status: "success", data: body.data };
    }
    return {
      status: "error",
      error: typeof body.error === "string" ? body.error : "Query failed.",
    };
  } catch {
    return { status: "error", error: "Could not reach Prometheus." };
  }
}

/**
 * Run a batch of Prometheus range queries sharing one time window.
 *
 * Body: { queries: string[], start: string, end: string, step: string }
 * Returns: { results: PromResult[] } in the same order as `queries`.
 */
export async function POST(req: NextRequest): Promise<NextResponse> {
  if (!(await isAuthenticated(req))) {
    return NextResponse.json(
      { status: "error", error: "Not authenticated." },
      { status: 401 },
    );
  }

  let payload: unknown;
  try {
    payload = await req.json();
  } catch {
    return NextResponse.json(
      { status: "error", error: "Body must be JSON." },
      { status: 400 },
    );
  }

  const { queries, start, end, step } = (payload ?? {}) as {
    queries?: unknown;
    start?: unknown;
    end?: unknown;
    step?: unknown;
  };

  if (
    !Array.isArray(queries) ||
    queries.length === 0 ||
    !queries.every((q) => typeof q === "string" && q.length > 0) ||
    typeof start !== "string" ||
    typeof end !== "string" ||
    typeof step !== "string"
  ) {
    return NextResponse.json(
      {
        status: "error",
        error: "queries (non-empty string[]), start, end and step are required.",
      },
      { status: 400 },
    );
  }

  if (queries.length > MAX_QUERIES) {
    return NextResponse.json(
      { status: "error", error: `At most ${MAX_QUERIES} queries per batch.` },
      { status: 400 },
    );
  }

  // No Prometheus configured for this environment: report it plainly so the UI
  // shows a "not configured" note instead of a misleading network error.
  if (!PROM) {
    return NextResponse.json({
      results: queries.map(() => ({ status: "disabled" as const })),
    });
  }

  const results = await Promise.all(
    queries.map((q) => runQuery(q as string, start, end, step)),
  );
  return NextResponse.json({ results });
}
