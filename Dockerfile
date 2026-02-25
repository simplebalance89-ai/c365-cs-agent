# Dockerfile — C365 CS Agent (Azure Container Apps)
# Python 3.11-slim, production-grade

FROM python:3.11-slim

# Metadata
LABEL maintainer="Peter Wilson"
LABEL app="c365-cs-agent"
LABEL version="1.0.0"

# Security: run as non-root user
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

# System deps for any native packages (e.g. httpx, cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Install Python dependencies first (layer cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port (Container Apps uses TARGET_PORT / 8000)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
