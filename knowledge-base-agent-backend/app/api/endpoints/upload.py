from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.models.source import KnowledgeSource
from app.core.database import get_db
from app.core.config import settings
from datetime import datetime

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload and process documents (PDF, TXT, EPUB) with database and vector storage"""
    
    # Debug logging
    print(f"DEBUG: Received file: {file.filename}")
    print(f"DEBUG: Content type: {file.content_type}")
    print(f"DEBUG: File size: {file.size}")
    
    # Validate file type - be more flexible with content types
    allowed_types = ["application/pdf", "text/plain", "application/epub+zip"]
    
    # Determine the actual content type
    actual_content_type = file.content_type
    
    # Handle common variations of text files
    if actual_content_type == "text/plain" or actual_content_type == "text/txt" or actual_content_type == "" or actual_content_type is None:
        # For text files, also check file extension
        if file.filename and file.filename.lower().endswith(('.txt', '.text')):
            actual_content_type = "text/plain"  # Normalize content type
    
    # Check filename extension as fallback
    elif file.filename:
        filename_lower = file.filename.lower()
        if filename_lower.endswith(('.txt', '.text')):
            actual_content_type = "text/plain"
        elif filename_lower.endswith('.pdf'):
            actual_content_type = "application/pdf"
        elif filename_lower.endswith('.epub'):
            actual_content_type = "application/epub+zip"
    
    if actual_content_type not in allowed_types:
        print(f"DEBUG: Rejecting file with content type: {actual_content_type}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Unsupported file type",
                "received_type": actual_content_type,
                "allowed_types": allowed_types,
                "filename": file.filename
            }
        )
    
    # Validate file size using configurable limit
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert MB to bytes
    if file.size and file.size > max_size:
        return JSONResponse(
            status_code=400,
            content={"error": f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB"}
        )
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    try:
        # Process the document
        processor = DocumentProcessor()
        processed_doc = await processor.process_document(
            file_content, 
            file.filename, 
            actual_content_type
        )
        
        if processed_doc.get("status") == "error":
            raise HTTPException(status_code=500, detail=f"Failed to process document: {processed_doc.get('metadata', {}).get('error', 'Unknown error')}")
        
        # Create a unique URL identifier for the uploaded document
        document_url = f"file://{file.filename}"
        
        # Check if document already exists in database
        result = await db.execute(select(KnowledgeSource).filter(KnowledgeSource.url == document_url))
        existing_source = result.scalar_one_or_none()
        
        if existing_source:
            # Update existing document
            existing_source.title = processed_doc.get("filename", file.filename)
            existing_source.content = processed_doc.get("content", "")
            existing_source.source_metadata = processed_doc.get("metadata", {})
            existing_source.status = "completed"
            existing_source.scraped_at = datetime.utcnow()
            db_source = existing_source
        else:
            # Create new database entry
            db_source = KnowledgeSource(
                url=document_url,
                title=processed_doc.get("filename", file.filename),
                content=processed_doc.get("content", ""),
                source_metadata=processed_doc.get("metadata", {}),
                status="completed",
                scraped_at=datetime.utcnow()
            )
            db.add(db_source)
        
        # Commit to database
        await db.commit()
        await db.refresh(db_source)
        
        # Add to vector store
        vector_store = VectorStore()
        metadata = {
            "source_id": str(db_source.id),
            "title": db_source.title,
            "url": db_source.url,
            "source_type": "document_upload",
            "filename": file.filename,
            "content_type": actual_content_type
        }
        
        vector_doc_id = await vector_store.add_document(
            content=processed_doc.get("content", ""),
            metadata=metadata
        )
        
        print(f"DEBUG: Document added to vector store with ID: {vector_doc_id}")
        
        return {
            "status": "success",
            "message": f"Document processed and stored successfully: {file.filename}",
            "title": processed_doc.get("filename", file.filename),
            "filename": file.filename,
            "content_type": actual_content_type,
            "processing_status": processed_doc.get("status", "completed"),
            "content_length": len(processed_doc.get("content", "")),
            "source_id": str(db_source.id),
            "vector_doc_id": vector_doc_id,
            "preview": processed_doc.get("content", "")[:200] + "..." if len(processed_doc.get("content", "")) > 200 else processed_doc.get("content", "")
        }
        
    except Exception as e:
        # Rollback database changes on error
        await db.rollback()
        
        # Handle specific error cases
        if "not implemented" in str(e).lower():
            return JSONResponse(
                status_code=501,
                content={
                    "error": "Document type not yet supported",
                    "message": str(e),
                    "supported_types": ["text/plain"]
                }
            )
        
        print(f"DEBUG: Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")