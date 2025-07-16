# Knowledge Base Agent - Business Logic Flow Analysis

## 📊 Detailed Business Logic Flows

### 1. Complete Chat Message Processing Pipeline

```mermaid
graph TD
    A[User Types Message] --> B[Frontend Validation]
    B --> C[Send to Backend API]
    C --> D[Save User Message to PostgreSQL]
    D --> E[Generate Query Embedding]
    E --> F[Search Vector Store ChromaDB]
    F --> G[Retrieve Top 5 Relevant Documents]
    G --> H[Assemble Context with Sources]
    H --> I[Create Structured Prompt]
    I --> J[Send to Ollama LLM]
    J --> K[Generate AI Response]
    K --> L[Save AI Message with Sources]
    L --> M[Update Session Timestamp]
    M --> N[Return Response to Frontend]
    N --> O[Display in Chat UI]
    
    style A fill:#e1f5fe
    style J fill:#fff3e0
    style F fill:#f3e5f5
    style D fill:#e8f5e8
```

### 2. Knowledge Ingestion Business Logic

```mermaid
graph TD
    A[Content Input] --> B{Input Type?}
    B -->|Web URL| C[Playwright Browser Launch]
    B -->|PDF File| D[PyPDF2 Processing]
    B -->|TXT File| E[Direct Text Reading]
    B -->|EPUB File| F[EPUB Library Processing]
    
    C --> G[Navigate to URL]
    G --> H[Wait for Network Idle]
    H --> I[Extract Page Content]
    I --> J[BeautifulSoup Parsing]
    
    D --> K[Extract PDF Text]
    E --> L[Read Text Content]
    F --> M[Extract EPUB Content]
    
    J --> N[Clean HTML Content]
    K --> N
    L --> N
    M --> N
    
    N --> O[Text Chunking 1000 chars]
    O --> P[200 char Overlap Processing]
    P --> Q[Generate Embeddings]
    Q --> R[Store in ChromaDB]
    R --> S[Save Metadata to PostgreSQL]
    S --> T[Update Source Status]
    
    style A fill:#e1f5fe
    style Q fill:#fff3e0
    style R fill:#f3e5f5
    style S fill:#e8f5e8
```

### 3. RAG (Retrieval-Augmented Generation) Process

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend API
    participant V as Vector Store
    participant L as LLM (Ollama)
    participant D as PostgreSQL
    
    U->>F: Send Message
    F->>B: POST /chat/sessions/{id}/messages
    B->>D: Save User Message
    B->>V: Generate Query Embedding
    V->>V: Cosine Similarity Search
    V->>B: Return Top 5 Documents
    B->>B: Assemble Context + Prompt
    B->>L: Generate Response
    L->>B: AI Response
    B->>D: Save AI Message + Sources
    B->>D: Update Session Timestamp
    B->>F: Return Complete Response
    F->>U: Display Chat + Sources
```

### 4. Document Processing State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: Document Uploaded/URL Submitted
    Pending --> Processing: Start Processing
    Processing --> Extracting: Content Extraction
    Extracting --> Chunking: Text Chunking
    Chunking --> Embedding: Generate Embeddings
    Embedding --> Storing: Store in Vector DB
    Storing --> Completed: Success
    
    Processing --> Error: Extraction Failed
    Extracting --> Error: Parsing Failed
    Chunking --> Error: Chunking Failed
    Embedding --> Error: Embedding Failed
    Storing --> Error: Storage Failed
    
    Error --> Pending: Retry
    Completed --> [*]
```

### 5. Chat Session Lifecycle

```mermaid
graph LR
    A[New Chat Button] --> B[Create Session]
    B --> C[Generate UUID]
    C --> D[Save to PostgreSQL]
    D --> E[Active Chat Session]
    
    E --> F[Send Messages]
    F --> G[AI Responses]
    G --> H[Update Session Timestamp]
    H --> E
    
    E --> I[Delete Session]
    I --> J[Cascade Delete Messages]
    J --> K[Session Removed]
    
    E --> L[Session Idle]
    L --> M[Show in Sidebar]
    M --> N[Click to Resume]
    N --> E
    
    style B fill:#e8f5e8
    style I fill:#ffebee
```

## 🔧 Service Integration Patterns

### 1. Vector Store Integration Pattern
```python
# Business Logic Flow in VectorStore Service
async def add_document(content: str, metadata: Dict) -> str:
    # 1. Text Chunking Strategy
    chunks = self._chunk_text(content, chunk_size=1000, overlap=200)
    
    # 2. Embedding Generation
    for chunk in chunks:
        embedding = self.embedder.encode(chunk).tolist()
        
        # 3. Metadata Enhancement
        chunk_metadata = {**metadata, "chunk_index": i, "total_chunks": len(chunks)}
        
        # 4. Vector Storage
        self.collection.add(ids=[doc_id], embeddings=[embedding], 
                           documents=[chunk], metadatas=[chunk_metadata])
```

### 2. LLM Integration Pattern
```python
# RAG Context Assembly Business Logic
async def generate_response(query: str, context: List[Dict]) -> str:
    # 1. Context Preparation
    context_text = "\n\n".join([
        f"Source: {doc['metadata'].get('url', 'Unknown')}\n{doc['content']}"
        for doc in context
    ])
    
    # 2. Prompt Engineering
    prompt = f"""You are a helpful AI assistant with access to a personal knowledge base.
    Context: {context_text}
    Question: {query}
    Answer:"""
    
    # 3. LLM Generation with Parameters
    payload = {
        "model": self.chat_model,
        "prompt": prompt,
        "options": {"temperature": 0.7, "top_p": 0.9}
    }
```

### 3. Database Transaction Pattern
```python
# Chat Message Processing Transaction
async def send_message(session_id: UUID, content: str, db: AsyncSession):
    # 1. Save User Message
    user_message = ChatMessage(session_id=session_id, content=content, role="user")
    db.add(user_message)
    
    # 2. Vector Search
    relevant_docs = await vector_store.search(content, n_results=5)
    
    # 3. Generate AI Response
    ai_response = await llm.generate_response(content, relevant_docs)
    
    # 4. Save AI Message with Sources
    ai_message = ChatMessage(session_id=session_id, content=ai_response, 
                           role="assistant", sources=sources)
    db.add(ai_message)
    
    # 5. Update Session Timestamp
    session.updated_at = func.now()
    
    # 6. Commit Transaction
    await db.commit()
```

## 📈 Performance & Scalability Considerations

### 1. Vector Search Performance
- **Chunk Size**: 1000 characters optimal for semantic coherence
- **Overlap**: 200 characters prevents context loss at boundaries
- **Top-K Retrieval**: Limited to 5 documents for response quality
- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions, fast inference)

### 2. Database Optimization
- **Indexes**: session_id, created_at, url for fast queries
- **JSONB**: Flexible metadata storage with efficient querying
- **UUID**: Distributed-friendly primary keys
- **Cascade Deletes**: Automatic cleanup of related records

### 3. LLM Processing
- **Local Processing**: Complete privacy, no external API calls
- **Model Size**: 8B parameters balanced for quality/speed
- **Context Window**: Large enough for multiple document chunks
- **Temperature**: 0.7 for balanced creativity/accuracy

This business logic architecture ensures efficient, scalable, and privacy-focused knowledge management with intelligent retrieval and generation capabilities.
