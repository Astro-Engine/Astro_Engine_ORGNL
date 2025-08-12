# Multi-stage build for production optimization
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY astro_engine/requirements.txt .
COPY requirements-prod.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-prod.txt

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash astro && \
    mkdir -p /var/log && \
    chown -R astro:astro /app /var/log

# Copy application code
COPY astro_engine /app/astro_engine
# COPY .env.production /app/.env

# Create necessary directories
RUN mkdir -p /app/logs && \
    chown -R astro:astro /app

# Switch to non-root user
USER astro

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Copy Gunicorn config
COPY gunicorn.conf.py /app/gunicorn.conf.py

# Production command with Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "astro_engine.app:app"]
