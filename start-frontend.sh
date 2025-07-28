#!/bin/bash

echo "Starting Local Wander Frontend..."

cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the development server
echo "Starting Vite dev server on http://localhost:5173"
npm run dev