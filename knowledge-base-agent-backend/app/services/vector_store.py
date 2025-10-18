import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import uuid
import re
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

            # Extract page number from chunk if it's a PDF
            if metadata.get("type") == "pdf":
                page_num = self._extract_page_number(chunk)
                if page_num:
                    chunk_metadata["page_number"] = page_num

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

        # Get more results to see all available documents
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results * 2, 20)  # Get more to debug
        )

        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None
                })

        # Return only the requested number
        return formatted_results[:n_results]

    async def delete_by_source_id(self, source_id: str) -> int:
        """Delete all vectors associated with a source_id

        Args:
            source_id: The UUID of the source to delete vectors for

        Returns:
            Number of vectors deleted
        """
        try:
            # Query all documents with this source_id in metadata
            results = self.collection.get(
                where={"source_id": source_id}
            )

            if results and results['ids']:
                vector_count = len(results['ids'])
                print(f"[VECTOR_DELETE] Found {vector_count} vectors for source {source_id}")

                # Delete all matching documents
                self.collection.delete(ids=results['ids'])
                print(f"[VECTOR_DELETE] Successfully deleted {vector_count} vectors")

                return vector_count

            print(f"[VECTOR_DELETE] No vectors found for source {source_id}")
            return 0

        except Exception as e:
            print(f"[VECTOR_DELETE] Error deleting vectors for source {source_id}: {e}")
            raise
    
    def _extract_page_number(self, chunk: str) -> Optional[int]:
        """Extract page number from chunk text that contains [PAGE X] marker"""
        match = re.search(r'\[PAGE (\d+)\]', chunk)
        if match:
            return int(match.group(1))
        return None

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