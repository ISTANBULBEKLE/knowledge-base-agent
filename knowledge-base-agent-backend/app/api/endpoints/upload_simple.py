from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import asyncio

router = APIRouter()

@router.post("/upload-simple")
async def upload_document_simple(file: UploadFile = File(...)):
    """Simple upload endpoint for testing - no database dependencies"""
    
    # Debug logging
    print(f"DEBUG: Received file: {file.filename}")
    print(f"DEBUG: Content type: {file.content_type}")
    print(f"DEBUG: File size: {file.size}")
    
    # Validate file type - be more flexible with content types
    allowed_types = ["application/pdf", "text/plain", "application/epub+zip"]
    
    # Handle common variations of text files
    if file.content_type == "text/plain" or file.content_type == "text/txt" or file.content_type == "" or file.content_type is None:
        # For text files, also check file extension
        if file.filename and file.filename.lower().endswith(('.txt', '.text')):
            file.content_type = "text/plain"  # Normalize content type
    
    # Check filename extension as fallback
    elif file.filename:
        filename_lower = file.filename.lower()
        if filename_lower.endswith(('.txt', '.text')):
            file.content_type = "text/plain"
        elif filename_lower.endswith('.pdf'):
            file.content_type = "application/pdf"
        elif filename_lower.endswith('.epub'):
            file.content_type = "application/epub+zip"
    
    if file.content_type not in allowed_types:
        print(f"DEBUG: Rejecting file with content type: {file.content_type}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Unsupported file type",
                "received_type": file.content_type,
                "allowed_types": allowed_types,
                "filename": file.filename
            }
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process only text files for now
        if file.content_type == "text/plain":
            try:
                text_content = file_content.decode('utf-8')
                
                return {
                    "status": "success",
                    "message": f"Document processed successfully: {file.filename}",
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "text_length": len(text_content),
                    "preview": text_content[:100] + "..." if len(text_content) > 100 else text_content
                }
            except UnicodeDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Could not decode text file"}
                )
        else:
            return JSONResponse(
                status_code=501,
                content={"error": "Only text files are currently supported"}
            )
            
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")