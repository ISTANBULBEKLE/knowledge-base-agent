#!/bin/bash

echo "🚀 Starting Knowledge Base Agent (Simple Mode)"

# Start backend in background
echo "🐍 Starting backend..."
cd knowledge-base-agent-backend
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "⚛️ Starting frontend..."
cd ../knowledge-base-agent-frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Services started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT
wait