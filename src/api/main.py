"""
FastAPI Backend for RAG Pipeline

Provides API endpoints to interact with different chunking strategies.

Run with: uv run uvicorn src.api.main:app --reload
"""

from contextlib import asynccontextmanager
import zipfile

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    HealthResponse,
    IndexRequest,
    IndexResponse,
    QueryRequest,
    QueryResponse,
    ChunkInfo,
    ChunkingStrategy,
    ConfigUpdateRequest,
    ConfigResponse,
    DatabasesResponse,
    UploadResponse,
)
from .service import rag_service
from src.config import settings


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


@app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_config():
    """Get current configuration."""
    return ConfigResponse(
        chunking_strategy=settings.CHUNKING_STRATEGY,
        retrieval_k=settings.RETRIEVAL_K,
    )


@app.post("/config", response_model=ConfigResponse, tags=["Configuration"])
async def update_config(request: ConfigUpdateRequest):
    """Update configuration settings."""
    if request.chunking_strategy is not None:
        strategy = request.chunking_strategy.value
        settings.CHUNKING_STRATEGY = strategy
        if strategy in ["recursive", "code", "ast"]:
            settings.RETRIEVAL_MODE = "vector"
        elif strategy == "graphrag":
            settings.RETRIEVAL_MODE = "graph"
    if request.retrieval_k is not None:
        settings.RETRIEVAL_K = request.retrieval_k
    
    return ConfigResponse(
        chunking_strategy=settings.CHUNKING_STRATEGY,
        retrieval_k=settings.RETRIEVAL_K,
    )


@app.get("/databases", response_model=DatabasesResponse, tags=["Databases"])
async def list_databases():
    """List available ChromaDB collections."""
    collections = rag_service.list_collections()
    return DatabasesResponse(
        databases=collections,
        count=len(collections),
    )


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


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query(request: QueryRequest):
    """Query the indexed codebase using the RAG agent."""
    try:
        answer, retrieved_docs = rag_service.query_with_agent(
            query=request.query,
            strategy=request.strategy,
            k=request.k,
            collection=request.collection,
        )
        
        # Convert retrieved docs to ChunkInfo
        chunks = []
        for doc in retrieved_docs:
            chunks.append(ChunkInfo(
                content=doc.page_content,
                source=doc.metadata.get("source", ""),
                chunk_type=doc.metadata.get("chunk_type"),
                start_line=doc.metadata.get("start_line"),
                end_line=doc.metadata.get("end_line"),
                name=doc.metadata.get("name"),
            ))
        
        return QueryResponse(
            answer=answer,
            retrieved_chunks=chunks,
            strategy_used=request.strategy,
            num_chunks=len(chunks),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index/upload", response_model=UploadResponse, tags=["Indexing"])
async def upload_zip(file: UploadFile = File(...)):
    """
    Upload a zip file containing Python code to index.
    
    Uses the currently configured chunking strategy from settings.
    """
    # Validate file type
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are accepted")
    
    try:
        num_docs, num_chunks, collection = rag_service.index_from_zip(
            zip_file=file.file,
            zip_name=file.filename,
            strategy=ChunkingStrategy(settings.CHUNKING_STRATEGY),
        )
        
        if num_docs == 0:
            raise HTTPException(status_code=404, detail="No Python files found in archive")
        
        return UploadResponse(
            success=True,
            message=f"Indexed {num_docs} files into {num_chunks} chunks",
            num_documents=num_docs,
            num_chunks=num_chunks,
            strategy_used=settings.CHUNKING_STRATEGY,
            collection_name=collection,
        )
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupted zip file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
