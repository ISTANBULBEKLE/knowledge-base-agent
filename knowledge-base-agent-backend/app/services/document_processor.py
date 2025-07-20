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
            # Handle empty files
            if not file_content:
                return f"Empty text file: {filename}"
            
            # Try UTF-8 first, then fall back to other encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    text = file_content.decode(encoding)
                    # Basic text cleaning
                    text = text.strip()
                    if text:
                        return self._clean_text(text)
                    else:
                        # File decoded but is empty/whitespace only
                        return f"Text file: {filename}\n\nNote: This file appears to be empty or contains only whitespace."
                except UnicodeDecodeError:
                    continue
            
            # If we get here, no encoding worked
            return f"Text file: {filename}\n\nNote: Could not decode this text file with supported encodings (UTF-8, Latin-1, CP1252, ISO-8859-1)."
            
        except Exception as e:
            return f"Text file: {filename}\n\nError processing text file: {str(e)}"
    
    async def _process_pdf(self, file_content: bytes, filename: str) -> str:
        """Process PDF files - Basic implementation with fallback"""
        try:
            # Try to import PyPDF2 if available
            import PyPDF2
            import io
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text_content = []
            
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
            
            extracted_text = "\n".join(text_content)
            return self._clean_text(extracted_text)
            
        except ImportError:
            # Fallback: extract any readable text from PDF bytes
            try:
                # Simple text extraction - look for readable content
                decoded_content = file_content.decode('latin-1', errors='ignore')
                # Basic text extraction from PDF structure
                import re
                text_patterns = re.findall(r'\(([^)]+)\)', decoded_content)
                text_content = ' '.join(text_patterns)
                
                if len(text_content.strip()) < 50:
                    # If we can't extract much, provide a placeholder
                    return f"PDF document: {filename}\n\nNote: PDF text extraction requires PyPDF2. Install with: pip install PyPDF2"
                
                return self._clean_text(text_content)
            except Exception:
                return f"PDF document: {filename}\n\nNote: Unable to extract text from this PDF. Please install PyPDF2 for better PDF support."
        except Exception as e:
            return f"PDF document: {filename}\n\nError processing PDF: {str(e)}"
    
    async def _process_epub(self, file_content: bytes, filename: str) -> str:
        """Process EPUB files - Basic implementation with fallback"""
        try:
            # Try to import ebooklib if available
            import ebooklib
            from ebooklib import epub
            import io
            
            book = epub.read_epub(io.BytesIO(file_content))
            text_content = []
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # Extract text from HTML content
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text_content.append(soup.get_text())
            
            extracted_text = "\n".join(text_content)
            return self._clean_text(extracted_text)
            
        except ImportError:
            # Fallback for EPUB - it's a ZIP file, try to extract text
            try:
                import zipfile
                import io
                
                with zipfile.ZipFile(io.BytesIO(file_content)) as epub_zip:
                    text_content = []
                    for file_name in epub_zip.namelist():
                        if file_name.endswith('.html') or file_name.endswith('.xhtml'):
                            try:
                                with epub_zip.open(file_name) as html_file:
                                    html_content = html_file.read().decode('utf-8', errors='ignore')
                                    # Basic HTML tag removal
                                    import re
                                    clean_text = re.sub(r'<[^>]+>', ' ', html_content)
                                    text_content.append(clean_text)
                            except Exception:
                                continue
                    
                    if text_content:
                        extracted_text = "\n".join(text_content)
                        return self._clean_text(extracted_text)
                    else:
                        return f"EPUB document: {filename}\n\nNote: Install ebooklib for better EPUB support: pip install ebooklib"
                        
            except Exception:
                return f"EPUB document: {filename}\n\nNote: Unable to extract text from this EPUB. Please install ebooklib for better EPUB support."
        except Exception as e:
            return f"EPUB document: {filename}\n\nError processing EPUB: {str(e)}"
    
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