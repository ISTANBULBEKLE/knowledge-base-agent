from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.document_processor import DocumentProcessor

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process documents (PDF, TXT, EPUB) - Simplified version"""
    
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
    
    # Validate file size (e.g., 10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        return JSONResponse(
            status_code=400,
            content={"error": "File too large. Maximum size is 10MB"}
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
        
        # Return simplified response without database operations
        return {
            "status": "success",
            "message": f"Document processed successfully: {file.filename}",
            "title": processed_doc.get("filename", file.filename),
            "filename": file.filename,
            "content_type": actual_content_type,
            "processing_status": processed_doc.get("status", "completed"),
            "content_length": len(processed_doc.get("content", "")),
            "preview": processed_doc.get("content", "")[:200] + "..." if len(processed_doc.get("content", "")) > 200 else processed_doc.get("content", "")
        }
        
    except Exception as e:
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
        
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")