#!/bin/bash
# Startup script for Railway/Render deployment
# This ensures proper initialization before gunicorn starts

echo "[STARTUP] Agro Advisor - Starting up..."
echo "[STARTUP] Python version: $(python --version)"
echo "[STARTUP] Current directory: $(pwd)"
echo "[STARTUP] Files: $(ls -la | head -10)"

# Export port if not set
export PORT=${PORT:-5000}
export FLASK_ENV=${FLASK_ENV:-production}

echo "[STARTUP] PORT: $PORT"
echo "[STARTUP] FLASK_ENV: $FLASK_ENV"

# Start gunicorn with proper worker configuration
# For free tier with limited memory, use 1 worker
exec gunicorn \
  --bind 0.0.0.0:${PORT} \
  --workers 1 \
  --worker-class sync \
  --worker-tmp-dir /dev/shm \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  app:app
