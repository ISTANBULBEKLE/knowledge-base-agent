from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.sql import func
from typing import List
import uuid

from app.core.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatSessionCreate, ChatSessionResponse, ChatMessageResponse
from app.services.llm import OllamaLLM
from app.services.vector_store import VectorStore

router = APIRouter()

@router.post("/chat/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session"""
    session = ChatSession(title=session_data.title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at
    )

@router.get("/chat/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    limit: int = 15,
    db: AsyncSession = Depends(get_db)
):
    """Get recent chat sessions (last 15)"""
    result = await db.execute(
        select(ChatSession)
        .order_by(desc(ChatSession.updated_at))
        .limit(limit)
    )
    sessions = result.scalars().all()
    
    return [
        ChatSessionResponse(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
        for session in sessions
    ]

@router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a specific chat session"""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == str(session_id))
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    
    return [
        ChatMessageResponse(
            id=message.id,
            session_id=message.session_id,
            content=message.content,
            role=message.role,
            sources=message.sources,
            created_at=message.created_at
        )
        for message in messages
    ]

@router.post("/chat/sessions/{session_id}/messages")
async def send_message(
    session_id: uuid.UUID,
    message: dict,
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response"""
    try:
        user_content = message.get("content", "")
        
        if not user_content.strip():
            raise HTTPException(status_code=400, detail="Message content cannot be empty")
        
        # Save user message
        user_message = ChatMessage(
            session_id=str(session_id),
            content=user_content,
            role="user"
        )
        db.add(user_message)
        await db.flush()  # Get the ID
        
        # Check if user is asking about knowledge base contents
        knowledge_base_queries = [
            "list", "show", "what's in my knowledge base", "what resources", 
            "knowledge base contents", "sources", "documents", "what do you know"
        ]
        is_kb_query = any(keyword in user_content.lower() for keyword in knowledge_base_queries)
        
        # Search for relevant context
        vector_store = VectorStore()
        relevant_docs = await vector_store.search(user_content, n_results=5)
        
        # If asking about knowledge base, also get all sources from database
        additional_context = ""
        if is_kb_query:
            # Get all sources from database for comprehensive listing
            from app.models.source import KnowledgeSource
            
            sources_result = await db.execute(
                select(KnowledgeSource)
                .where(KnowledgeSource.status == "completed")
                .order_by(KnowledgeSource.created_at.desc())
            )
            all_sources = sources_result.scalars().all()
            
            if all_sources:
                source_list = []
                for source in all_sources:
                    source_type = "Website" if source.url.startswith("http") else "Document"
                    source_list.append(f"- {source.title or 'Untitled'} ({source_type}): {source.url}")
                
                additional_context = f"\n\nCOMPLETE KNOWLEDGE BASE INVENTORY:\n" + "\n".join(source_list)
        
        # Generate AI response
        llm = OllamaLLM()
        
        # Add knowledge base context if this is a listing query
        context_for_llm = relevant_docs
        if additional_context:
            # Add synthetic document with complete source listing
            context_for_llm.append({
                "content": additional_context,
                "metadata": {
                    "title": "Knowledge Base Inventory",
                    "url": "system://knowledge_base_sources",
                    "source_type": "system"
                },
                "distance": 0.0  # Highest relevance
            })
        
        ai_response = await llm.generate_response(user_content, context_for_llm)
        
        # Save AI message with sources
        sources = [
            {
                "url": doc["metadata"].get("url", ""),
                "title": doc["metadata"].get("title", ""),
                "relevance": 1 - (doc.get("distance", 0) or 0)
            }
            for doc in relevant_docs[:3]  # Top 3 sources
        ]
        
        ai_message = ChatMessage(
            session_id=str(session_id),
            content=ai_response,
            role="assistant",
            sources=sources
        )
        db.add(ai_message)
        await db.flush()  # Get the ID
        
        # Update session timestamp
        session_result = await db.execute(
            select(ChatSession).where(ChatSession.id == str(session_id))
        )
        session = session_result.scalar_one_or_none()
        if session:
            session.updated_at = func.now()
        
        await db.commit()
        
        return {
            "user_message": {
                "id": str(user_message.id),
                "session_id": str(user_message.session_id),
                "content": user_message.content,
                "role": user_message.role,
                "sources": user_message.sources or [],
                "created_at": user_message.created_at.isoformat()
            },
            "ai_message": {
                "id": str(ai_message.id),
                "session_id": str(ai_message.session_id),
                "content": ai_message.content,
                "role": ai_message.role,
                "sources": ai_message.sources or [],
                "created_at": ai_message.created_at.isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    try:
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == str(session_id))
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        await db.delete(session)
        await db.commit()
        
        return {"message": "Chat session deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")