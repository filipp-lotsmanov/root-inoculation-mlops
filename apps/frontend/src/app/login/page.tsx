"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { API_PREFIX, getHealth } from "@/lib/api";
import styles from "./page.module.css";

type Mode = "sign_in" | "create_account";

/** Login and registration page. Redirects to `/` if already authenticated. */
export default function LoginPage() {
  const router = useRouter();
  const { user, loading, login, register } = useAuth();

  const [mode, setMode] = useState<Mode>("sign_in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [oauthEnabled, setOauthEnabled] = useState(false);

  // /health advertises whether the GitHub flow is configured. Reading it at
  // runtime keeps one frontend image valid across environments, the same
  // reason the Prometheus proxy avoids a NEXT_PUBLIC_ variable.
  useEffect(() => {
    let cancelled = false;
    getHealth().then(({ data }) => {
      if (!cancelled && data?.oauth_enabled) setOauthEnabled(true);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  // Already authenticated — redirect to dashboard.
  useEffect(() => {
    if (!loading && user) {
      router.replace("/");
    }
  }, [loading, user, router]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    if (mode === "sign_in") {
      if (!email.trim() || !password) {
        setError("Enter your email and password.");
        setSubmitting(false);
        return;
      }
      const err = await login(email.trim(), password);
      if (err) {
        setError(err);
        setSubmitting(false);
      } else {
        router.replace("/");
      }
    } else {
      if (!name.trim() || !email.trim() || !password) {
        setError("All fields are required.");
        setSubmitting(false);
        return;
      }
      if (password.length < 8) {
        setError("Password must be at least 8 characters.");
        setSubmitting(false);
        return;
      }
      const err = await register(name.trim(), email.trim(), password);
      if (err) {
        setError(err);
        setSubmitting(false);
      } else {
        router.replace("/");
      }
    }
  }

  if (loading) {
    return (
      <div className={styles.wrapper}>
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      <div className={`card ${styles.card}`}>
        <div className={styles.header}>
          <h1 className={styles.title}>CV Pipeline</h1>
          <p className={styles.subtitle}>NPEC Plant Segmentation</p>
        </div>

        {/* Tab toggle */}
        <div className={styles.tabs}>
          <button
            type="button"
            id="tab-sign-in"
            className={`${styles.tab} ${mode === "sign_in" ? styles.tabActive : ""}`}
            onClick={() => {
              setMode("sign_in");
              setError(null);
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            id="tab-create-account"
            className={`${styles.tab} ${mode === "create_account" ? styles.tabActive : ""}`}
            onClick={() => {
              setMode("create_account");
              setError(null);
            }}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div className={`alert alert-error ${styles.error}`} role="alert">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          {mode === "create_account" && (
            <div className={styles.field}>
              <label htmlFor="input-name">Name</label>
              <input
                id="input-name"
                type="text"
                placeholder="Full name"
                autoComplete="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          )}

          <div className={styles.field}>
            <label htmlFor="input-email">Email</label>
            <input
              id="input-email"
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="input-password">Password</label>
            <input
              id="input-password"
              type="password"
              placeholder={
                mode === "create_account"
                  ? "Min. 8 characters"
                  : "Enter password"
              }
              autoComplete={
                mode === "create_account" ? "new-password" : "current-password"
              }
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            id="btn-submit"
            type="submit"
            className={`btn btn-primary ${styles.submitBtn}`}
            disabled={submitting}
          >
            {submitting ? (
              <>
                <span className="spinner spinner-sm" />
                {mode === "sign_in" ? "Signing in..." : "Creating account..."}
              </>
            ) : mode === "sign_in" ? (
              "Sign In"
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        {/* Rendered only when the backend advertises OAuth support, so a
            deployment without GITHUB_CLIENT_ID / OAUTH_REDIRECT_URI does not
            show a button that leads to a 500. */}
        {oauthEnabled && (
          <>
            <div className={styles.divider}>
              <span>or</span>
            </div>
            <a
              id="btn-github-signin"
              href={`${API_PREFIX}/auth/github/login`}
              className={`btn ${styles.oauthBtn}`}
            >
              Continue with GitHub
            </a>
          </>
        )}
      </div>
    </div>
  );
}
