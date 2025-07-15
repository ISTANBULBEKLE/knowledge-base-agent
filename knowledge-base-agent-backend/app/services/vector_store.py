import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the vector store"""
        # Split content into chunks
        chunks = self._chunk_text(content)
        
        doc_ids = []
        for i, chunk in enumerate(chunks):
            doc_id = str(uuid.uuid4())
            embedding = self.embedder.encode(chunk).tolist()
            
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[chunk_metadata]
            )
            doc_ids.append(doc_id)
        
        return doc_ids[0] if doc_ids else None
    
    async def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        query_embedding = self.embedder.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        
        return formatted_results
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks