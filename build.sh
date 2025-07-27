#!/usr/bin/env bash
# Render.com build script for Maya AI Content Optimization System

set -o errexit  # exit on error

echo "🚀 Building Maya AI for Render deployment..."
echo "============================================="

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
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
