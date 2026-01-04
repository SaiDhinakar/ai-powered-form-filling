# ============================================
# AI-Powered Form Filling Backend - Dockerfile
# ============================================
# Multi-stage build for optimized production image

# Stage 1: Base image with Python and uv
FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Stage 2: Production image
FROM python:3.12-slim AS production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy virtual environment from base stage
COPY --from=base /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Create directories for uploads and outputs
RUN mkdir -p /app/uploads /app/outputs && \
    chown -R appuser:appuser /app/uploads /app/outputs

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# Expose ports
# 8000 - FastAPI backend
# 8907 - AI Agent service  
# 8909 - OCR service
EXPOSE 8000 8907 8909

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command - start all services
CMD ["sh", "-c", "python -m uvicorn ai_agents.serve:app --host 0.0.0.0 --port 8907 & python -m uvicorn ocr.server:app --host 0.0.0.0 --port 8909 & python -m uvicorn api.main:app --host 0.0.0.0 --port 8000"]