#!/bin/bash

echo "Starting LocalWander Frontend2 (Fancy UI)..."

# Check if we're in the right directory
if [ ! -d "frontend2" ]; then
    echo "Error: frontend2 directory not found!"
    exit 1
fi

cd frontend2

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Starting development server on port 3001..."
npm run dev