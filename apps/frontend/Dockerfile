# syntax=docker/dockerfile:1.7

# ---- Stage 1: build ----
FROM node:20-alpine AS builder
WORKDIR /app

COPY apps/frontend/package.json apps/frontend/package-lock.json ./
RUN npm ci

COPY apps/frontend/ ./
RUN npm run build

# ---- Stage 2: production ----
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy only what's needed for `next start`, setting ownership as we go.
# node:alpine already ships an unprivileged `node` user, so no useradd is
# needed. Ownership must be set on the COPY itself: a trailing
# `chown -R /app` rewrites every file into a new layer, and node_modules is
# ~700 MB, so that one instruction nearly doubled the image.
COPY --from=builder --chown=node:node /app/package.json ./
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/.next ./.next
COPY --from=builder --chown=node:node /app/public ./public

# /app itself is created by WORKDIR as root; Next.js writes its incremental
# cache under .next/cache at runtime, so the directory needs to be writable.
RUN chown node:node /app
USER node

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=5 \
	CMD wget -qO- http://localhost:3000 || exit 1

CMD ["npm", "start"]
