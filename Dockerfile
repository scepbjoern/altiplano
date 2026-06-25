FROM ghcr.io/astral-sh/uv:python3.11-alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

ARG UID=1000
ARG GID=1000

# Create non-root group and user
RUN addgroup -g $GID altiplano && \
    adduser -D -u $UID -G altiplano altiplano

WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies (without the package itself)
RUN uv sync --frozen --no-install-project --no-dev

# Copy package source and README
COPY src/ ./src
COPY README.md ./


# Sync project (installs altiplano in the virtual environment as non-editable)
RUN uv sync --frozen --no-dev --no-editable

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV FASTMCP_HOST=0.0.0.0
ENV FASTMCP_PORT=8000
ENV MCP_TRANSPORT=stdio

USER altiplano

EXPOSE 8000

# Healthcheck queries the SSE endpoint (will exit immediately with headers if connection is accepted,
# or we can check the status. If stdio is used, this healthcheck will fail, which is expected
# since stdio is not designed for background container service).
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --fail -s http://localhost:${FASTMCP_PORT:-8000}/sse || exit 1

CMD ["altiplano"]
