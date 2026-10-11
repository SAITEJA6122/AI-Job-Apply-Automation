#!/bin/bash

echo "========================================"
echo "  Starting Naukri Job Automation"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your API keys before running automation"
    echo ""
fi

# Check if profile.yaml exists
if [ ! -f profile.yaml ]; then
    echo "Creating profile.yaml from profile.example.yaml..."
    cp profile.example.yaml profile.yaml
    echo "Please edit profile.yaml with your details"
    echo ""
fi

# Start Backend (Flask)
echo "Starting Backend (Flask)..."
source .venv/bin/activate
python backend/app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend (React)
echo "Starting Frontend (React)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "  Servers started successfully!"
echo "========================================"
echo ""
echo "Backend URL: http://127.0.0.1:5000"
echo "Frontend URL: http://localhost:3000"
echo ""
echo "Open your browser to http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
