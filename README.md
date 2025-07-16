# Knowledge Base Agent

A sophisticated personal knowledge management system that intelligently scrapes, processes, and synthesizes information from web sources. The system provides a powerful chat-based interface with chat history management, querying a curated personal knowledge base using locally-run AI models.

## 🏗️ Architecture

**Two-Part Solution:**
1. **Backend (Python/FastAPI)**: Web scraping, vector database, RAG implementation, and PostgreSQL for chat history
2. **Frontend (Next.js 15)**: Modern chat interface with sidebar for previous conversations and real-time communication

## 🚀 Features

- ✅ **Modern UI**: Clean chat interface with sidebar for conversation history
- ✅ **PostgreSQL Integration**: Chat history stored in local database
- ✅ **Real-time Chat**: Instant messaging with AI responses
- ✅ **Source Attribution**: AI responses include relevant source citations
- ✅ **Mobile Responsive**: Works on desktop and mobile devices
- ✅ **Local AI**: Complete privacy with local LLM processing (Ollama)
- ✅ **Vector Search**: Semantic search across knowledge base
- ✅ **Chat Management**: Create, view, and delete chat sessions
- ✅ **Web Scraping**: Intelligent content extraction from web sources
- ✅ **Document Upload**: Upload and process PDF, TXT, and EPUB files

## ⚡ Quick Start

**Run everything with one command:**

```bash
# Start all services (PostgreSQL, Ollama, Backend, Frontend)
make dev
```

**Or use the startup script directly:**

```bash
./start-dev.sh
```

**Available commands:**
- `make dev` - Start all services
- `make stop` - Stop all services  
- `make setup` - Initial setup and installation
- `make clean` - Clean up generated files

The script automatically:
- ✅ Checks system requirements
- ✅ Starts PostgreSQL and creates database
- ✅ Starts Ollama and downloads AI models
- ✅ Installs dependencies if needed
- ✅ Starts backend and frontend servers
- ✅ Provides helpful status messages

**Access points:**
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

Press `Ctrl+C` to stop all services.

## 📋 Prerequisites

- **macOS** (optimized for M4 Pro)
- **Python 3.11**
- **Node.js 18+**
- **PostgreSQL 15**
- **Ollama** (for local AI models)

## 🛠️ Installation

### Option 1: Automated Installation (Recommended)

```bash
# Clone or navigate to the project directory
cd /Users/ekip.kalir/Projects/Personal/knowledge-base-agent

# Run the automated installation script
./install.sh
```

### Option 2: Manual Installation

#### 1. Install System Dependencies

```bash
# Install essential development tools
brew install curl wget tree htop git

# Install PostgreSQL 15
brew install postgresql@15
brew services start postgresql@15

# Install Python 3.11
brew install python@3.11

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 2. Database Setup

```bash
# Create database and user
createdb knowledge_base_agent
psql knowledge_base_agent -c "CREATE USER kba_user WITH PASSWORD 'secure_password';"
psql knowledge_base_agent -c "GRANT ALL PRIVILEGES ON DATABASE knowledge_base_agent TO kba_user;"

# Create tables
psql knowledge_base_agent -c "
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    sources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT UNIQUE NOT NULL,
    title VARCHAR(500),
    description TEXT,
    content TEXT,
    metadata JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'error')),
    scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_status ON knowledge_sources(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_url ON knowledge_sources(url);
"
```

#### 3. Backend Setup

```bash
cd knowledge-base-agent-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

#### 4. Frontend Setup

```bash
cd ../knowledge-base-agent-frontend

# Install dependencies
npm install
```

#### 5. Install AI Models

```bash
# Pull required Ollama models
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

## 🚀 Running the Application

### Option 1: Automated Startup (Recommended)

```bash
# Start all services with one command
./start-dev.sh
```

This will start:
- PostgreSQL (if not running)
- Ollama service
- Backend API server (port 8000)
- Frontend development server (port 3000)

### Option 2: Manual Startup

#### Terminal 1: Start Backend (Required)
```bash
# Quick start backend
./start-backend.sh

# OR manually:
cd knowledge-base-agent-backend
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Start Frontend
```bash
cd knowledge-base-agent-frontend
npm run dev
```

#### Optional: Start Ollama (for AI features)
```bash
ollama serve
```

## 🌐 Access Points

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: PostgreSQL on localhost:5432

## 📚 API Endpoints

### Chat Endpoints
- `POST /api/v1/chat/sessions` - Create new chat session
- `GET /api/v1/chat/sessions` - Get recent chat sessions (last 15)
- `GET /api/v1/chat/sessions/{id}/messages` - Get messages for a session
- `POST /api/v1/chat/sessions/{id}/messages` - Send message and get AI response
- `DELETE /api/v1/chat/sessions/{id}` - Delete chat session

### Knowledge Base Endpoints
- `POST /api/v1/scrape` - Scrape web content and add to knowledge base
- `POST /api/v1/upload` - Upload documents (PDF, TXT, EPUB) to knowledge base
- `GET /api/v1/sources` - Get knowledge sources
- `POST /api/v1/query` - Query knowledge base directly

## 🔧 Configuration

### Backend Configuration (.env)
```env
# Application Settings
APP_NAME="Knowledge Base Agent Backend"
APP_VERSION="0.1.0"
DEBUG=true

# Database Settings
DATABASE_URL="postgresql://kba_user:secure_password@localhost:5432/knowledge_base_agent"

# Vector Database
VECTOR_DB_TYPE="chromadb"
CHROMA_DB_PATH="./data/chroma_db"

# Ollama Settings
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_CHAT_MODEL="llama3.1:8b"
OLLAMA_EMBED_MODEL="nomic-embed-text"

# API Settings
API_V1_STR="/api/v1"
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend Configuration (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="Knowledge Base Agent"
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📖 Usage Guide

### 1. First Time Setup
1. Start the application using `./start-dev.sh`
2. Navigate to http://localhost:3000
3. Click "New Chat" to start your first conversation

### 2. Adding Knowledge Sources

#### Web Scraping
```bash
# Using curl to add a web source
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

#### Document Upload
```bash
# Upload a document via curl
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@/path/to/your/document.txt"

# Supported formats: PDF, TXT, EPUB
# Maximum file size: 10MB
```

#### Using the Web Interface
1. Navigate to http://localhost:3000
2. Use the "Upload Documents" section to select and upload files
3. Drag and drop files or click "Choose File" to browse
4. Supported formats: PDF, TXT, EPUB files

### 3. Chatting with Your Knowledge Base
1. Type your question in the chat interface
2. The AI will search your knowledge base for relevant information
3. Responses include source citations when relevant content is found
4. Chat history is automatically saved and accessible from the sidebar

### 4. Managing Chat Sessions
- **Create**: Click "New Chat" in the sidebar
- **View**: Click on any previous chat in the sidebar
- **Delete**: Hover over a chat and click the trash icon

## 🛠️ Development

### Project Structure
```
knowledge-base-agent/
├── knowledge-base-agent-backend/     # Python FastAPI backend
│   ├── app/
│   │   ├── api/endpoints/           # API route handlers
│   │   ├── core/                    # Configuration and database
│   │   ├── models/                  # SQLAlchemy models
│   │   ├── schemas/                 # Pydantic schemas
│   │   └── services/                # Business logic services
│   └── requirements.txt
├── knowledge-base-agent-frontend/    # Next.js 15 frontend
│   ├── src/
│   │   ├── app/                     # Next.js app router
│   │   ├── components/              # React components
│   │   ├── lib/                     # Utilities and API client
│   │   ├── stores/                  # Zustand state management
│   │   └── types/                   # TypeScript definitions
│   └── package.json
├── install.sh                       # Automated installation
├── start-dev.sh                     # Development startup script
└── README.md
```

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, ChromaDB, Playwright, BeautifulSoup
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Zustand, Radix UI
- **AI/ML**: Ollama (llama3.1:8b), Sentence Transformers, ChromaDB
- **Database**: PostgreSQL 15 with JSONB support

## 🔍 Troubleshooting

### Common Issues

1. **PostgreSQL Connection Error**
   ```bash
   brew services restart postgresql@15
   ```

2. **Ollama Models Not Found**
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

3. **Frontend Build Issues**
   ```bash
   cd knowledge-base-agent-frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Backend Import Errors**
   ```bash
   cd knowledge-base-agent-backend
   source venv/bin/activate
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

### Logs and Debugging
- Backend logs: Check terminal running uvicorn
- Frontend logs: Check browser console and terminal running npm
- Database logs: Check PostgreSQL logs via `brew services`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with FastAPI, Next.js, and Ollama
- Uses ChromaDB for vector storage
- Powered by local AI models for privacy