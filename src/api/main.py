"""
FastAPI Backend for RAG Pipeline

Provides API endpoints to interact with different chunking strategies.

Run with: uv run uvicorn src.api.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import HealthResponse


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
