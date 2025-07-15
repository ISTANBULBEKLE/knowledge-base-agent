# Knowledge Base Agent - Development Commands

.PHONY: help dev start stop clean install setup

# Default target
help:
	@echo "🤖 Knowledge Base Agent - Development Commands"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make dev     - Start all services (PostgreSQL, Ollama, Backend, Frontend)"
	@echo "  make start   - Alias for 'make dev'"
	@echo "  make stop    - Stop all services"
	@echo "  make setup   - Initial setup and installation"
	@echo "  make clean   - Clean up generated files and caches"
	@echo "  make install - Install dependencies only"
	@echo "  make check   - Check system requirements"
	@echo ""
	@echo "Quick start:"
	@echo "  make dev"
	@echo ""

# Start development environment
dev:
	@echo "🚀 Starting Knowledge Base Agent..."
	@./start-dev.sh

# Alias for dev
start: dev

# Stop services
stop:
	@echo "🛑 Stopping all services..."
	@-pkill -f "uvicorn app.main:app"
	@-pkill -f "next dev"
	@-pkill -f "ollama serve"
	@echo "✅ Services stopped"

# System requirements check
check:
	@echo "🔍 Checking system requirements..."
	@command -v brew >/dev/null 2>&1 || (echo "❌ Homebrew not found" && exit 1)
	@command -v node >/dev/null 2>&1 || (echo "❌ Node.js not found" && exit 1)
	@command -v python3 >/dev/null 2>&1 || (echo "❌ Python 3 not found" && exit 1)
	@command -v ollama >/dev/null 2>&1 || (echo "❌ Ollama not found" && exit 1)
	@command -v psql >/dev/null 2>&1 || (echo "❌ PostgreSQL not found" && exit 1)
	@echo "✅ All requirements satisfied"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@cd knowledge-base-agent-backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@cd knowledge-base-agent-frontend && npm install
	@echo "✅ Dependencies installed"

# Initial setup
setup: check install
	@echo "🔧 Setting up Knowledge Base Agent..."
	@brew services start postgresql@15 || true
	@sleep 2
	@createdb knowledge_base_agent 2>/dev/null || true
	@ollama pull llama3.1:8b || true
	@ollama pull nomic-embed-text || true
	@echo "✅ Setup complete! Run 'make dev' to start."

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf knowledge-base-agent-backend/__pycache__
	@rm -rf knowledge-base-agent-backend/**/__pycache__
	@rm -rf knowledge-base-agent-backend/.pytest_cache
	@rm -rf knowledge-base-agent-frontend/.next
	@rm -rf knowledge-base-agent-frontend/node_modules/.cache
	@echo "✅ Cleanup complete"