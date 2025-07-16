# Knowledge Base Agent - Architecture Analysis

## 🏗️ System Overview

Your Knowledge Base Agent is a sophisticated RAG (Retrieval-Augmented Generation) system with the following key components:

### Core Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js 15    │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│                 │    │                 │    │                 │
│ • Chat UI       │    │ • REST APIs     │    │ • Chat History  │
│ • File Upload   │    │ • RAG Logic     │    │ • Sessions      │
│ • Session Mgmt  │    │ • Web Scraping  │    │ • Sources       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   ChromaDB      │    │   Ollama        │
                       │   Vector Store  │    │   Local LLM     │
                       │                 │    │                 │
                       │ • Embeddings    │    │ • llama3.1:8b   │
                       │ • Semantic      │    │ • nomic-embed   │
                       │   Search        │    │ • Local AI      │
                       └─────────────────┘    └─────────────────┘
```

## 🔄 Business Logic Flow

### 1. Chat Message Processing Flow
```
User Input → Frontend → Backend API → Vector Search → LLM Generation → Response
    │            │           │             │              │            │
    │            │           │             │              │            └─► Sources Added
    │            │           │             │              └─► Context Injection
    │            │           │             └─► Relevant Docs Retrieved
    │            │           └─► Message Saved to PostgreSQL
    │            └─► Real-time UI Update
    └─► Chat Interface
```

### 2. Knowledge Ingestion Flow
```
Web URL/File → Scraper/Parser → Content Extraction → Text Chunking → Embeddings → Vector Store
     │              │                  │                 │             │            │
     │              │                  │                 │             │            └─► ChromaDB
     │              │                  │                 │             └─► Sentence Transformers
     │              │                  │                 └─► Overlapping Chunks
     │              │                  └─► Clean Text Content
     │              └─► Playwright/BeautifulSoup/PyPDF2
     └─► Multiple Sources Supported
```

## 🧠 AI Integration Architecture

### Local LLM Stack
```
┌─────────────────────────────────────────────────────────────┐
│                        Ollama Service                       │
├─────────────────────────────────────────────────────────────┤
│  Chat Model: llama3.1:8b                                   │
│  • Temperature: 0.7                                        │
│  • Context Window: Large                                   │
│  • Response Generation                                     │
│                                                            │
│  Embedding Model: nomic-embed-text                         │
│  • Vector Embeddings                                       │
│  • Semantic Similarity                                     │
│  • Document Retrieval                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG Implementation                       │
├─────────────────────────────────────────────────────────────┤
│  1. Query Processing                                       │
│     └─► Embedding Generation                               │
│                                                            │
│  2. Vector Search                                          │
│     └─► ChromaDB Similarity Search                         │
│                                                            │
│  3. Context Assembly                                       │
│     └─► Top-K Document Retrieval                           │
│                                                            │
│  4. Prompt Engineering                                     │
│     └─► Context + Query → Structured Prompt               │
│                                                            │
│  5. Response Generation                                    │
│     └─► LLM Processing → Contextual Answer                │
└─────────────────────────────────────────────────────────────┘
```
