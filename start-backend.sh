#!/bin/bash

echo "🐍 Starting Knowledge Base Agent Backend..."

# Navigate to backend directory
cd knowledge-base-agent-backend

# Activate virtual environment
source venv/bin/activate

# Install minimal dependencies if not installed
pip install fastapi uvicorn pydantic sqlalchemy asyncpg psycopg2-binary python-dotenv pydantic-settings aiohttp

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the backend server
echo "🚀 Starting FastAPI server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000