# Multi-stage build for production optimization
FROM python:3.13-slim-bookworm as base

# Install system dependencies and security updates
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    libc6-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Install UV package manager
RUN pip install --no-cache-dir uv

# ================================
# Development stage
# ================================
FROM base as development

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_INTERACT=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Set working directory
WORKDIR /app

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml ./

# Install dependencies including dev dependencies
RUN uv sync --all-extras

# Copy source code
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Development command with auto-reload
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ================================
# Production stage
# ================================
FROM base as production

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_INTERACT=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Set working directory
WORKDIR /app

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user for dependency installation
USER appuser

# Copy dependency files
COPY --chown=appuser:appuser pyproject.toml ./

# Install only production dependencies
RUN uv sync --no-dev --frozen

# Copy source code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser migrations/ ./migrations/
COPY --chown=appuser:appuser alembic.ini ./

# Clean UV cache to reduce image size
RUN rm -rf /tmp/uv-cache

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Production command with optimal settings
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ================================
# Default to production
# ================================
FROM production