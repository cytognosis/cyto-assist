# Multi-stage Dockerfile for cyto-assist
# Supports both CPU and GPU environments with optimized builds

# Build stage
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY README.md LICENSE ./

# Build the package
RUN uv build

# Runtime stage
FROM python:3.12-slim as runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy built package
COPY --from=builder /app/dist/*.whl /tmp/

# Install the package
RUN pip install /tmp/*.whl && rm /tmp/*.whl

# Copy source code (for development/debugging)
COPY --from=builder /app/src ./src

# Change ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port for Jupyter/API services
EXPOSE 8888

# Default command
CMD ["python", "-c", "import cyto_assist; print('cyto_assist package is ready!')"]

# Development variant
FROM runtime as dev

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    vim \
    git \
    tmux \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install jupyter jupyterlab ipywidgets

# Copy development files
COPY . .

# Change ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose additional ports for development
EXPOSE 8888 8889

# Default command for development
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
