# Build stage
FROM elixir:alpine AS builder

WORKDIR /app

# Install hex and rebar
RUN mix local.hex --force && \
    mix local.rebar --force

# Copy mix files
COPY mix.exs mix.lock ./

# Get dependencies
RUN MIX_ENV=prod mix deps.get --only prod

# Copy source
COPY lib lib

# Compile
RUN MIX_ENV=prod mix compile

# Final stage
FROM elixir:alpine

WORKDIR /app

# Install hex in runtime
RUN mix local.hex --force

# Copy compiled app
COPY --from=builder /app/_build/prod /app/_build/prod
COPY --from=builder /app/deps /app/deps
COPY --from=builder /app/lib /app/lib
COPY --from=builder /app/mix.exs /app/mix.exs

# Start the collector
CMD ["mix", "run", "--no-halt"]
