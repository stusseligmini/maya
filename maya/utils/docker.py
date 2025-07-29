"""
Docker configuration update for Maya system.

This module provides updated Docker configuration for the Maya system
with multi-stage builds and optimized container setup.
"""

import os
import shutil
from pathlib import Path
import subprocess
from typing import Dict, Any, List, Optional

from maya.core.logging import get_logger
from maya.core.exceptions import ConfigurationError

logger = get_logger()


def generate_docker_compose():
    """Generate an updated docker-compose.yml file."""
    
    docker_compose_content = """version: '3.8'

services:
  # API Service
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
      target: api
    image: maya-api:latest
    container_name: maya-api
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://maya:${POSTGRES_PASSWORD}@db:5432/maya
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    volumes:
      - ./storage:/app/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # Worker Service
  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile
      target: worker
    image: maya-worker:latest
    container_name: maya-worker
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://maya:${POSTGRES_PASSWORD}@db:5432/maya
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./storage:/app/storage
    healthcheck:
      test: ["CMD", "python", "-c", "import redis; redis.Redis.from_url(os.environ['REDIS_URL']).ping()"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # Database Service
  db:
    image: postgres:16-alpine
    container_name: maya-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=maya
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=maya
    volumes:
      - maya-postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U maya"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # Redis Service
  redis:
    image: redis:7-alpine
    container_name: maya-redis
    restart: unless-stopped
    volumes:
      - maya-redis-data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: maya-prometheus
    restart: unless-stopped
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - maya-prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    depends_on:
      - api
      - worker

  grafana:
    image: grafana/grafana:latest
    container_name: maya-grafana
    restart: unless-stopped
    volumes:
      - maya-grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    depends_on:
      - prometheus

volumes:
  maya-postgres-data:
  maya-redis-data:
  maya-prometheus-data:
  maya-grafana-data:
"""
    
    docker_file_content = """# Multi-stage build for Maya AI System

# Base stage with common dependencies
FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install pip dependencies (will be cached if requirements don't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage - includes dev tools
FROM base AS development

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# API stage
FROM base AS api

# Copy application code
COPY . .

# Run the API server
CMD ["python", "maya_run.py", "api"]

# Worker stage
FROM base AS worker

# Copy application code
COPY . .

# Run the worker
CMD ["python", "maya_run.py", "worker"]
"""
    
    # Create directories
    docker_dir = Path("docker")
    os.makedirs(docker_dir, exist_ok=True)
    
    # Write docker-compose.yml
    with open("docker/docker-compose.yml", "w") as f:
        f.write(docker_compose_content)
    
    # Write Dockerfile
    with open("docker/Dockerfile", "w") as f:
        f.write(docker_file_content)
    
    logger.info("Docker configuration files generated")
    
    return {
        "docker_compose": "docker/docker-compose.yml",
        "dockerfile": "docker/Dockerfile"
    }


def setup_ci_cd():
    """Generate GitHub Actions CI/CD workflow files."""
    
    github_dir = Path(".github/workflows")
    os.makedirs(github_dir, exist_ok=True)
    
    ci_workflow_content = """name: Maya CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_maya
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Test with pytest
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_maya
        REDIS_URL: redis://localhost:6379/0
        ENVIRONMENT: testing
        SECRET_KEY: testingsecretkey
      run: |
        pytest -v
"""
    
    cd_workflow_content = """name: Maya CD

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_HUB_USERNAME }}
        password: ${{ secrets.DOCKER_HUB_TOKEN }}
    
    - name: Build and push API image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/Dockerfile
        target: api
        push: true
        tags: ${{ secrets.DOCKER_HUB_USERNAME }}/maya-api:latest
    
    - name: Build and push Worker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/Dockerfile
        target: worker
        push: true
        tags: ${{ secrets.DOCKER_HUB_USERNAME }}/maya-worker:latest
    
    - name: Deploy to production
      if: startsWith(github.ref, 'refs/tags/v')
      run: |
        echo "Deploying version $(echo $GITHUB_REF | cut -d / -f 3) to production"
        # Add deployment scripts here
"""
    
    # Write GitHub Actions workflow files
    with open(".github/workflows/ci.yml", "w") as f:
        f.write(ci_workflow_content)
    
    with open(".github/workflows/cd.yml", "w") as f:
        f.write(cd_workflow_content)
    
    logger.info("GitHub Actions CI/CD workflow files generated")
    
    return {
        "ci_workflow": ".github/workflows/ci.yml",
        "cd_workflow": ".github/workflows/cd.yml"
    }


def build_docker_images():
    """Build Docker images using the new configuration."""
    try:
        logger.info("Building Docker images")
        
        # Build API image
        subprocess.run(
            ["docker", "build", "-f", "docker/Dockerfile", "-t", "maya-api:latest", "--target", "api", "."],
            check=True
        )
        
        # Build worker image
        subprocess.run(
            ["docker", "build", "-f", "docker/Dockerfile", "-t", "maya-worker:latest", "--target", "worker", "."],
            check=True
        )
        
        logger.info("Docker images built successfully")
        
        return {
            "api_image": "maya-api:latest",
            "worker_image": "maya-worker:latest"
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build Docker images: {str(e)}")
        raise ConfigurationError(f"Docker build failed: {str(e)}")
