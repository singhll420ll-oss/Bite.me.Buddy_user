#!/usr/bin/env bash
# build.sh - Render build script

echo "Starting build process..."

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p static/uploads

echo "Build completed successfully!"
