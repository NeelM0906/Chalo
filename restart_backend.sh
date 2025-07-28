#!/bin/bash

echo "Restarting Local Wander Backend..."

# Kill any running backend processes
pkill -f "python backend/main.py" || true

# Start the backend server
cd backend
python main.py