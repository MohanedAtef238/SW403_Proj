"""Pydantic models for API request/response schemas."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""
    RECURSIVE = "recursive"
    CODE = "code"
    AST = "ast"


class IndexRequest(BaseModel):
    """Request model for indexing files."""
    file_paths: list[str] = Field(
        ...,
        description="List of file paths to index"
    )
    strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.CODE,
        description="Chunking strategy to use"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "file_paths": ["simple_test_case.py"],
                    "strategy": "ast"
                }
            ]
        }
    }


class IndexResponse(BaseModel):
    """Response model for indexing."""
    success: bool = Field(..., description="Whether indexing was successful")
    message: str = Field(..., description="Status message")
    num_documents: int = Field(default=0, description="Number of documents indexed")
    num_chunks: int = Field(default=0, description="Number of chunks created")
    strategy_used: ChunkingStrategy = Field(..., description="Chunking strategy used")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy")
    version: str = Field(default="0.1.0")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error info")
