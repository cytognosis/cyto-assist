# Multi-stage build for cyto-assist
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install dependencies
RUN uv pip install --system -e .

# Development stage
FROM base as development
RUN uv pip install --system -e ".[dev,test,notebooks]"
RUN uv pip install --system -e ".[mlops]"
# Production stage
FROM base as production

# Copy source code
COPY src/ ./src/
COPY experiments/ ./experiments/
# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import cyto_assist; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "cyto_assist"]
