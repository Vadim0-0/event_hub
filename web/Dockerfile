# --- Dependencies ---
FROM oven/bun:1 AS deps
WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# --- Build ---
FROM deps AS build
WORKDIR /app

COPY . .

# URL API
ARG NUXT_PUBLIC_API_BASE=
ENV NUXT_PUBLIC_API_BASE=$NUXT_PUBLIC_API_BASE

RUN bun run build

# --- Production ---
  FROM oven/bun:1 AS production
WORKDIR /app

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

COPY --from=build /app/.output ./.output

EXPOSE 3000
CMD ["bun", ".output/server/index.mjs"]

# --- Development ---
FROM deps AS development
WORKDIR /app

EXPOSE 3000
CMD ["bun", "run", "dev", "--host", "0.0.0.0", "--port", "3000"]
