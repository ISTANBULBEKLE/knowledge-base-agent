import aiohttp
import json
import re
from typing import List, Dict, Any
from app.core.config import settings

class OllamaLLM:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.chat_model = settings.OLLAMA_CHAT_MODEL

    def _strip_xml_tags(self, text: str) -> str:
        """Remove XML tags like <plan>, <reflection>, etc. from LLM output"""
        # Remove XML tags and their content (for tags like <thinking>, <reflection>)
        text = re.sub(r'<(thinking|reflection|plan|scratchpad)>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Remove any remaining XML-like tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        return text.strip()

    async def generate_response(self, query: str, context: List[Dict[str, Any]], is_kb_summary: bool = False) -> str:
        """Generate response using Ollama with RAG context"""

        # Prepare context from retrieved documents
        context_text = "\n\n".join([
            f"Source: {doc.get('metadata', {}).get('url', 'Unknown')}\n{doc.get('content', '')}"
            for doc in context
        ])

        # Create specialized prompt for knowledge base summaries
        if is_kb_summary:
            # Extract unique sources from context
            sources = {}
            for doc in context:
                # Safely get metadata (might be missing or structured differently)
                metadata = doc.get('metadata', {})
                if not isinstance(metadata, dict):
                    metadata = {}

                title = metadata.get('title', 'Untitled')
                url = metadata.get('url', 'Unknown')
                source_type = metadata.get('source_type', 'document')

                if url not in sources:
                    sources[url] = {'title': title, 'type': source_type}

            # Only use specialized prompt if we have sources
            if sources:
                sources_list = "\n".join([
                    f"- {info['title']} ({info['type']})"
                    for url, info in sources.items()
                ])

                prompt = f"""You are a helpful AI assistant analyzing a personal knowledge base.

The user has asked you to summarize their knowledge base. You MUST provide a comprehensive overview that covers ALL sources listed below.

AVAILABLE SOURCES ({len(sources)} total):
{sources_list}

IMPORTANT INSTRUCTIONS:
1. You MUST mention and discuss EVERY source listed above
2. For each source, identify the main topics, themes, or key information
3. Group related sources together if they share common themes
4. If a source seems unrelated to others, mention it separately
5. Provide a structured summary that ensures no source is left out
6. Use the context below to understand the content of each source

Context from sources:
{context_text}

Question: {query}

Provide a comprehensive summary that covers ALL {len(sources)} sources:"""
            else:
                # Fallback if no sources found
                prompt = f"""You are a helpful AI assistant with access to a personal knowledge base.

The user asked: {query}

However, the knowledge base appears to be empty or no relevant sources were found. Please inform the user that their knowledge base is empty and they need to add sources first.

Answer:"""
        else:
            # Create standard prompt with context
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
                    raw_response = result.get("response", "I couldn't generate a response.")
                    # Strip XML tags from the response
                    cleaned_response = self._strip_xml_tags(raw_response)
                    return cleaned_response
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