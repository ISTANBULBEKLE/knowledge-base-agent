from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "Knowledge Base Agent Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "info"
    
    # Database
    DATABASE_URL: str = "postgresql://kba_user:secure_password@localhost:5432/knowledge_base_agent"
    
    # Vector Database
    VECTOR_DB_TYPE: str = "chromadb"
    CHROMA_DB_PATH: str = "./data/chroma_db"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_MODEL: str = "llama3.1:8b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    
    # API
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()