# Multi-stage Dockerfile for Maya AI

FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# API target
FROM base AS api
EXPOSE 8000
CMD ["python", "maya_run.py", "api", "--host", "0.0.0.0", "--port", "8000"]

# Worker target
FROM base AS worker
CMD ["python", "maya_run.py", "worker"]
