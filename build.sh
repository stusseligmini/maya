#!/usr/bin/env bash
# Render.com build script for Maya AI Content Optimization System

set -o errexit  # exit on error

echo "🚀 Building Maya AI for Render deployment..."
echo "============================================="

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp config/prod.env .env
fi

# Generate Docker configuration
echo "🐳 Generating Docker configuration..."
mkdir -p docker

# Check if running on Render
if [ "$RENDER" = "true" ]; then
    echo "🚀 Running on Render.com deployment"
    
    # Initialize database
    echo "🗄️ Initializing database..."
    python maya_run.py init-db
    
    echo "✅ Build completed successfully!"
else
    echo "🖥️ Running local build"
    
    # Initialize database
    echo "🗄️ Initializing database..."
    python maya_run.py init-db
    
    echo "✅ Build completed successfully!"
    echo "💡 Run the API server: python maya_run.py api"
    echo "💡 Run the worker: python maya_run.py worker"
    echo "💡 Visit API docs: http://localhost:8000/docs"
fi
pip install --upgrade pip

# Install Python dependencies
echo "📋 Installing Maya AI dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating application directories..."
mkdir -p logs temp storage input/images_raw input/videos_raw input/captions_raw

# Set permissions for build script
chmod +x build.sh

echo "✅ Maya AI build completed successfully!"
echo "🎉 Ready for Render deployment!"
