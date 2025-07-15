from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from app.services.vector_store import VectorStore

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    limit: int = 5

class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]

@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """Query the knowledge base for relevant information"""
    
    vector_store = VectorStore()
    results = await vector_store.search(request.query, n_results=request.limit)
    
    return QueryResponse(results=results)