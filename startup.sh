#!/bin/bash
# startup.sh — Azure Container Apps startup script for C365 CS Agent
#
# Azure Container Apps injects $PORT dynamically. This script reads it
# and starts uvicorn on the correct port. Falls back to 8000 locally.

set -e

PORT="${PORT:-8000}"

echo "Starting C365 CS Agent on port $PORT"
echo "Environment: ${ENVIRONMENT:-production}"

exec uvicorn server:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 2 \
    --log-level info \
    --access-log
