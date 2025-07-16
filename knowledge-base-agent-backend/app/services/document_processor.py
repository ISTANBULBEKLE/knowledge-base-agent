import io
import os
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
import hashlib

class DocumentProcessor:
    """
    Service for processing uploaded documents (PDF, TXT, EPUB)
    Extracts text content for vector storage and knowledge base integration
    """
    
    def __init__(self):
        self.supported_types = {
            "application/pdf": self._process_pdf,
            "text/plain": self._process_text,
            "application/epub+zip": self._process_epub
        }
    
    async def process_document(self, file_content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """
        Process uploaded document and extract text content
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            content_type: MIME type of the file
            
        Returns:
            Dictionary with processed document information
        """
        if content_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {content_type}")
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Create file hash for deduplication
        file_hash = hashlib.md5(file_content).hexdigest()
        
        try:
            # Process the document based on its type
            processor = self.supported_types[content_type]
            extracted_text = await processor(file_content, filename)
            
            # Extract basic metadata
            metadata = {
                "filename": filename,
                "content_type": content_type,
                "file_size": len(file_content),
                "file_hash": file_hash,
                "document_id": doc_id,
                "source_type": "document_upload"
            }
            
            return {
                "document_id": doc_id,
                "filename": filename,
                "content": extracted_text,
                "metadata": metadata,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "document_id": doc_id,
                "filename": filename,
                "content": "",
                "metadata": {"error": str(e)},
                "status": "error"
            }
    
    async def _process_text(self, file_content: bytes, filename: str) -> str:
        """Process plain text files"""
        try:
            # Try UTF-8 first, then fall back to other encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    text = file_content.decode(encoding)
                    # Basic text cleaning
                    text = text.strip()
                    if text:
                        return text
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("Could not decode text file with supported encodings")
            
        except Exception as e:
            raise ValueError(f"Error processing text file: {str(e)}")
    
    async def _process_pdf(self, file_content: bytes, filename: str) -> str:
        """Process PDF files - Basic implementation without external dependencies"""
        # For now, return a placeholder implementation
        # In production, you would use PyPDF2, pdfplumber, or similar
        raise NotImplementedError(
            "PDF processing requires additional dependencies. "
            "Please install PyPDF2 or pdfplumber to enable PDF support."
        )
    
    async def _process_epub(self, file_content: bytes, filename: str) -> str:
        """Process EPUB files - Basic implementation without external dependencies"""
        # For now, return a placeholder implementation
        # In production, you would use ebooklib or similar
        raise NotImplementedError(
            "EPUB processing requires additional dependencies. "
            "Please install ebooklib to enable EPUB support."
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common artifacts
        text = text.replace('\x00', '')  # Remove null bytes
        text = text.replace('\ufeff', '')  # Remove BOM
        
        return text.strip()
    
    def _extract_title_from_content(self, content: str, filename: str) -> str:
        """Extract title from content or use filename as fallback"""
        lines = content.split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            if line and len(line) < 200:  # Reasonable title length
                return line
        
        # Fallback to filename without extension
        return Path(filename).stem