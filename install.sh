#!/bin/bash

echo "🔧 Setting up Knowledge Base Agent..."

# Setup backend
echo "📦 Setting up backend..."
cd knowledge-base-agent-backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install

# Setup frontend
echo "📦 Setting up frontend..."
cd ../knowledge-base-agent-frontend
npm install

# Install Ollama models
echo "🤖 Installing Ollama models..."
ollama pull llama3.1:8b
ollama pull nomic-embed-text

echo "✅ Setup complete! Run './start-dev.sh' to begin development."