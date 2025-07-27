# AI Service Dockerfile for Fooocus and ML models
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies for AI services
COPY requirements-ai.txt .
RUN pip install --no-cache-dir -r requirements-ai.txt

# Install Fooocus (example - adjust based on actual setup)
RUN git clone https://github.com/lllyasviel/Fooocus.git /fooocus && \
    cd /fooocus && \
    pip install -r requirements_versions.txt

# Create directories
RUN mkdir -p /models /output/images /output/videos

# Copy AI service code
COPY ai_service/ ./ai_service/
COPY ai_models/ ./ai_models/

# Expose port
EXPOSE 8080

# Environment variables
ENV PYTHONPATH="/app:/fooocus"
ENV MODEL_CACHE_PATH="/models"
ENV OUTPUT_PATH="/output"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start AI service
CMD ["python", "-m", "ai_service.main"]
