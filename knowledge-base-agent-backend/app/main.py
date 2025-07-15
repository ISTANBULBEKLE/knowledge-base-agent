from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import chat, scrape, sources, query
from app.core.config import settings

app = FastAPI(title="Knowledge Base Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(scrape.router, prefix=settings.API_V1_STR, tags=["scrape"])
app.include_router(sources.router, prefix=settings.API_V1_STR, tags=["sources"])
app.include_router(query.router, prefix=settings.API_V1_STR, tags=["query"])

@app.get("/")
def read_root():
    return {"message": "Knowledge Base Agent API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}