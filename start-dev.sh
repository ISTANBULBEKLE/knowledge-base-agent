#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting Knowledge Base Agent Development Environment"
echo "================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command_exists brew; then
    echo "❌ Homebrew not found. Please install Homebrew first."
    exit 1
fi

if ! command_exists ollama; then
    echo "❌ Ollama not found. Please install Ollama first."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js first."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

# Start PostgreSQL if not running
echo "📊 Starting PostgreSQL..."
if ! brew services list | grep postgresql@15 | grep started > /dev/null; then
    echo "  Starting PostgreSQL service..."
    brew services start postgresql@15 || {
        echo "  Restarting PostgreSQL service..."
        brew services stop postgresql@15 2>/dev/null
        sleep 2
        brew services start postgresql@15
    }
    sleep 3
    echo "  ✅ PostgreSQL started"
else
    echo "  ✅ PostgreSQL already running"
fi

# Ensure database exists
echo "🗄️  Checking database..."
if ! psql -lqt | cut -d \| -f 1 | grep -qw knowledge_base_agent; then
    echo "  Creating database..."
    createdb knowledge_base_agent 2>/dev/null || true
    echo "  ✅ Database created"
else
    echo "  ✅ Database exists"
fi

# Start Ollama service
echo "🤖 Starting Ollama service..."
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "  Starting Ollama server..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 5
    echo "  ✅ Ollama started"
else
    echo "  ✅ Ollama already running"
fi

# Check if required models are available
echo "🧠 Checking AI models..."
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "  Downloading llama3.1:8b model (this may take a while)..."
    ollama pull llama3.1:8b
fi

if ! ollama list | grep -q "nomic-embed-text"; then
    echo "  Downloading nomic-embed-text model..."
    ollama pull nomic-embed-text
fi
echo "  ✅ AI models ready"

# Start backend
echo "🐍 Starting Python backend..."
if port_in_use 8000; then
    echo "  ⚠️  Port 8000 already in use, trying to continue..."
else
    cd knowledge-base-agent-backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if requirements.txt is newer than the last install
    if [ ! -f ".last_install" ] || [ "requirements.txt" -nt ".last_install" ]; then
        echo "  Installing/updating Python dependencies..."
        pip install -r requirements.txt
        touch .last_install
    fi
    
    # Set Python path and start server
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    echo "  Starting FastAPI server..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    sleep 3
    echo "  ✅ Backend started on http://localhost:8000"
    
    cd ..
fi

# Start frontend
echo "⚛️  Starting Next.js frontend..."
if port_in_use 3000; then
    echo "  ⚠️  Port 3000 already in use, trying to continue..."
else
    cd knowledge-base-agent-frontend
    
    # Install dependencies if package.json is newer than node_modules
    if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
        echo "  Installing/updating Node.js dependencies..."
        npm install
    fi
    
    echo "  Starting Next.js development server..."
    npm run dev &
    FRONTEND_PID=$!
    sleep 3
    echo "  ✅ Frontend started on http://localhost:3000"
    
    cd ..
fi

echo ""
echo "🎉 Knowledge Base Agent is now running!"
echo "================================================="
echo "🌐 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🗄️  Database:    PostgreSQL on localhost:5432"
echo "🤖 Ollama:       http://localhost:11434"
echo ""
echo "💡 Tips:"
echo "   • Open http://localhost:3000 to start chatting"
echo "   • Add knowledge sources through the drawer"
echo "   • Press Ctrl+C to stop all services"
echo ""
echo "🔄 Waiting for services (Press Ctrl+C to stop)..."

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down development environment..."
    
    # Kill processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null && echo "  ✅ Backend stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null && echo "  ✅ Frontend stopped"
    fi
    
    if [ ! -z "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null && echo "  ✅ Ollama stopped"
    fi
    
    # Note: We don't stop PostgreSQL as it's a system service
    echo "  ℹ️  PostgreSQL service left running"
    echo ""
    echo "👋 Development environment stopped!"
    exit 0
}

trap cleanup SIGINT SIGTERM
wait