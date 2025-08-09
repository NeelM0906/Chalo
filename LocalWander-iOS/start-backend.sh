#!/bin/bash

echo "Starting Chalo Backend Server..."
echo "======================================"

cd LocalWanderBackend

# Check if Swift is installed
if ! command -v swift &> /dev/null; then
    echo "Error: Swift is not installed. Please install Xcode Command Line Tools."
    exit 1
fi

# Build and run the server
echo "Building and starting server..."
swift run

echo "Server started on http://localhost:8080"
echo "API endpoints:"
echo "  GET  /api/itineraries?location=NewYork"
echo "  POST /api/refresh-spot" 