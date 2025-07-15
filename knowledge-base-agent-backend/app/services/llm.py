import aiohttp
import json
from typing import List, Dict, Any
from app.core.config import settings

class OllamaLLM:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.chat_model = settings.OLLAMA_CHAT_MODEL
    
    async def generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate response using Ollama with RAG context"""
        
        # Prepare context from retrieved documents
        context_text = "\n\n".join([
            f"Source: {doc['metadata'].get('url', 'Unknown')}\n{doc['content']}"
            for doc in context
        ])
        
        # Create prompt with context
        prompt = f"""You are a helpful AI assistant with access to a personal knowledge base. 
Use the following context to answer the user's question. If the context doesn't contain 
relevant information, say so and provide a general response.

Context:
{context_text}

Question: {query}

Answer:"""
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.chat_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "I couldn't generate a response.")
                else:
                    return "Error connecting to the language model."
    
    async def generate_chat_title(self, first_message: str) -> str:
        """Generate a title for a chat session based on the first message"""
        prompt = f"""Generate a short, descriptive title (max 5 words) for this conversation starter:

"{first_message}"

Title:"""
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.chat_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 20
                }
            }
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    title = result.get("response", "New Chat").strip()
                    return title[:50]  # Limit length
                else:
                    return "New Chat"