# Atlas AI Backend Dockerfile for Render.com
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Create data directory for reminders
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Dynamic worker count for Render.com
# Render Starter: 0.5 CPU, Standard: 1 CPU, Pro: 2 CPU
ENV WORKERS=${WORKERS:-4}
ENV THREADS=${THREADS:-2}
ENV WORKER_CONNECTIONS=${WORKER_CONNECTIONS:-1000}

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose port
EXPOSE ${PORT:-8000}

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
