FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV_MODE="production" \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and set up directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Install Python dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Switch to non-root user
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Expose the port the app runs on
EXPOSE 8000

# Dynamic worker count for Render.com
# Render Starter: 0.5 CPU, Standard: 1 CPU, Pro: 2 CPU
ENV WORKERS=${WORKERS:-4}
ENV THREADS=${THREADS:-2}
ENV WORKER_CONNECTIONS=${WORKER_CONNECTIONS:-1000}

EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Gunicorn configuration optimized for Render.com
CMD ["sh", "-c", "gunicorn api:app \
     --workers $WORKERS \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:${PORT:-8000} \
     --timeout 300 \
     --graceful-timeout 120 \
     --keep-alive 300 \
     --max-requests 1000 \
     --max-requests-jitter 100 \
     --forwarded-allow-ips '*' \
     --worker-connections $WORKER_CONNECTIONS \
     --worker-tmp-dir /tmp \
     --preload \
     --log-level info \
     --access-logfile - \
     --error-logfile - \
     --capture-output \
     --enable-stdio-inheritance \
     --threads $THREADS"]
