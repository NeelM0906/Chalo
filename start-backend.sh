#!/bin/bash

echo "Starting Local Wander Backend..."

cd backend

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create backend/.env with your GOOGLE_MAPS_API_KEY"
    echo "Example: GOOGLE_MAPS_API_KEY=your_api_key_here"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if API key is configured
if ! grep -q "GOOGLE_MAPS_API_KEY=" .env; then
    echo "⚠️  Warning: GOOGLE_MAPS_API_KEY not found in .env file"
    echo "Please add your Google Maps API key to backend/.env"
    exit 1
fi

echo "✓ Environment configured"
echo "✓ Dependencies installed"

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
python main.py