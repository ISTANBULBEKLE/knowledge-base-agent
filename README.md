# Knowledge Base Agent

A sophisticated personal knowledge management system that intelligently scrapes, processes, and synthesizes information from web sources and documents. The system provides a powerful chat-based interface with accordion navigation, full resource management, and chat history, querying a curated personal knowledge base using locally-run AI models.

## 🏗️ Architecture

**Two-Part Solution:**
1. **Backend (Python/FastAPI)**: Web scraping (including PDF URLs), document processing, vector database, RAG implementation, and PostgreSQL for data persistence
2. **Frontend (Next.js 15)**: Modern accordion-based UI with clean navigation, chat interface, and resource management

## 🚀 Features

- ✅ **Accordion-Based UI**: Clean, collapsible navigation reducing visual clutter
- ✅ **PostgreSQL Integration**: Robust data storage with JSONB support for metadata
- ✅ **Real-time Chat**: Instant messaging with AI responses and source attribution
- ✅ **Source Attribution**: AI responses include relevant source citations with URLs
- ✅ **Resource Management**: Full CRUD operations - view, add, and delete knowledge sources
- ✅ **Mobile Responsive**: Works on desktop and mobile devices with wider sidebar (28-36rem)
- ✅ **Local AI**: Complete privacy with local LLM processing (Ollama llama3.1:8b)
- ✅ **Vector Search**: Semantic search with ChromaDB and nomic-embed-text
- ✅ **Chat Management**: Create, view, and delete chat sessions with CASCADE
- ✅ **Web Scraping**: Intelligent content extraction with Playwright + BeautifulSoup
- ✅ **PDF URL Scraping**: Direct scraping of PDF files from web URLs using PyPDF2
- ✅ **Document Upload**: Upload and process PDF, TXT, and EPUB files (up to 100MB)
- ✅ **Retry Logic**: Automatic retry for failed scrapes
- ✅ **Hover Interactions**: Subtle delete buttons with smooth opacity transitions

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
- `POST /api/v1/chat/sessions/{id}/messages` - Send message and get AI response with RAG
- `DELETE /api/v1/chat/sessions/{id}` - Delete chat session (CASCADE deletes messages)

### Knowledge Base Endpoints
- `POST /api/v1/scrape` - Scrape web content (including PDF URLs) and add to knowledge base
- `POST /api/v1/upload` - Upload documents (PDF, TXT, EPUB) to knowledge base
- `GET /api/v1/sources` - Get all knowledge sources with status
- `DELETE /api/v1/sources/{id}` - Delete knowledge source (CASCADE)
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

#### Using the Accordion UI
1. Open the "Add Web Source" accordion
2. Enter a URL (supports both HTML pages and PDF URLs like `https://arxiv.org/pdf/2510.06255`)
3. Click "Scrape URL"

#### Web Scraping (API)
```bash
# Scrape HTML page
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'

# Scrape PDF URL directly
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/pdf/2510.06255"}'
```

#### Document Upload
```bash
# Upload a document via curl
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@/path/to/your/document.pdf"

# Supported formats: PDF, TXT, EPUB
# Maximum file size: 100MB
```

#### Using the Web Interface
1. Navigate to http://localhost:3000
2. Open the "Upload Documents" accordion
3. Drag and drop files or click "Choose File" to browse
4. Supported formats: PDF, TXT, EPUB files

### 3. Managing Resources
- **View**: Open "Your Resources" accordion to see all indexed content
- **Delete**: Hover over any resource card and click the trash icon (becomes visible on hover)
- **Retry Failed**: Resources with "error" status can be re-scraped by deleting and re-adding

### 4. Chatting with Your Knowledge Base
1. Type your question in the chat interface
2. The AI will search your knowledge base for relevant information (top-5 documents)
3. Responses include source citations when relevant content is found
4. Chat history is automatically saved and accessible from the "Recent Conversations" accordion

### 5. Managing Chat Sessions
- **Create**: Click "New Chat" button
- **View**: Click on any previous chat in the "Recent Conversations" accordion
- **Delete**: Hover over a chat and click the trash icon

## 🛠️ Development

### Project Structure
```
knowledge-base-agent/
├── knowledge-base-agent-backend/     # Python FastAPI backend
│   ├── app/
│   │   ├── api/endpoints/           # API route handlers
│   │   │   ├── chat.py             # Chat endpoints
│   │   │   ├── scrape.py           # Scraping (HTML + PDF URLs)
│   │   │   ├── upload.py           # Document upload
│   │   │   ├── sources.py          # Resource management (+ DELETE)
│   │   │   └── query.py            # Direct queries
│   │   ├── core/                    # Configuration and database
│   │   ├── models/                  # SQLAlchemy models
│   │   ├── schemas/                 # Pydantic schemas
│   │   └── services/                # Business logic services
│   │       ├── scraper.py          # Web + PDF scraping
│   │       ├── document_processor.py
│   │       ├── vector_store.py     # ChromaDB integration
│   │       └── llm.py              # Ollama integration
│   └── requirements.txt
├── knowledge-base-agent-frontend/    # Next.js 15 frontend
│   ├── src/
│   │   ├── app/                     # Next.js app router
│   │   │   └── page.tsx            # Main layout with accordions
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   └── Accordion.tsx   # Collapsible component
│   │   │   ├── chat/
│   │   │   │   └── ChatInterface.tsx
│   │   │   ├── sources/
│   │   │   │   └── ResourcesList.tsx # With delete functionality
│   │   │   ├── scraping/
│   │   │   │   └── ScrapeForm.tsx
│   │   │   └── documents/
│   │   │       └── DocumentUpload.tsx
│   │   ├── lib/                     # Utilities and API client
│   │   ├── stores/                  # Zustand state management
│   │   ├── styles/                  # Sass/SCSS files
│   │   │   ├── accordion.scss      # Accordion & resource styles
│   │   │   ├── sidebar.scss
│   │   │   └── layout.scss
│   │   └── types/                   # TypeScript definitions
│   └── package.json
├── docs/                            # Documentation
│   ├── analysis_summary.md
│   ├── architecture_analysis.md
│   ├── business_logic_flow.md
│   ├── technical_integration.md
│   └── PRESENTATION_SLIDES.md
├── install.sh                       # Automated installation
├── start-dev.sh                     # Development startup script
├── README.md
└── STATUS.md
```

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, ChromaDB, Playwright, BeautifulSoup, PyPDF2
- **Frontend**: Next.js 15, React 19, TypeScript, Sass/SCSS, Zustand
- **AI/ML**: Ollama (llama3.1:8b, nomic-embed-text), ChromaDB
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

5. **ChromaDB Schema Errors**
   ```bash
   # Delete and recreate vector database
   rm -rf knowledge-base-agent-backend/data/chroma_db
   mkdir -p knowledge-base-agent-backend/data/chroma_db
   ```

### Logs and Debugging
- Backend logs: Check terminal running uvicorn
- Frontend logs: Check browser console and terminal running npm
- Database logs: Check PostgreSQL logs via `brew services`
- API Testing: Use http://localhost:8000/docs (Swagger UI)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with FastAPI, Next.js 15, and Ollama
- Uses ChromaDB for vector storage
- Powered by local AI models for complete privacy
- PDF processing with PyPDF2
- Web scraping with Playwright and BeautifulSoup

## 📝 Recent Updates

- ✅ Added accordion-based navigation for clean UI
- ✅ Implemented resource deletion with CASCADE
- ✅ Added PDF URL scraping support
- ✅ Widened sidebar for better content display (28-36rem)
- ✅ Added hover-based delete buttons with smooth transitions
- ✅ Improved text overflow handling with ellipsis
- ✅ Added retry logic for failed scrapes
- ✅ Enhanced resource cards with distinct visual separation
