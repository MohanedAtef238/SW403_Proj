"""
FastAPI Backend for RAG Pipeline

Provides API endpoints to interact with different chunking strategies.

Run with: uv run uvicorn src.api.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import HealthResponse, IndexRequest, IndexResponse
from .service import rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("RAG API starting up...")
    yield
    print("RAG API shutting down...")


app = FastAPI(
    title="RAG Codebase Q&A API",
    description="API for querying code using RAG pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint returning health status."""
    return HealthResponse()


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@app.post("/index", response_model=IndexResponse, tags=["Indexing"])
async def index_files(request: IndexRequest):
    """Index Python files from the data/ directory."""
    try:
        num_docs, num_chunks = rag_service.index_files(
            file_paths=request.file_paths,
            strategy=request.strategy,
        )
        
        if num_docs == 0:
            raise HTTPException(status_code=404, detail="No files found or files are empty")
        
        return IndexResponse(
            success=True,
            message=f"Successfully indexed {num_docs} file(s) into {num_chunks} chunks",
            num_documents=num_docs,
            num_chunks=num_chunks,
            strategy_used=request.strategy,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
