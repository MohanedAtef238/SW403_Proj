"""Pydantic models for API request/response schemas."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

# model config parameters are to enhance fastAPI's documentation

class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""
    FUNCTION = "function"   # P1: Baseline
    AST = "ast"             # P2: cAST
    CONTEXT = "context"     # P3: Context-enriched
    GRAPH = "graph"         # P4: GraphRAG


class IndexRequest(BaseModel):
    """Request model for indexing files."""
    file_paths: list[str] = Field(
        ...,
        description="List of file paths to index"
    )
    strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.FUNCTION,
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

class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    query: str = Field(..., description="The question to ask")
    strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.FUNCTION,
        description="Chunking strategy to use for retrieval"
    )
    k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of documents to retrieve"
    )
    collection: Optional[str] = Field(
        default=None,
        description="ChromaDB collection name to query. If not provided, uses default collection."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What classes are defined in the code?",
                    "strategy": "ast",
                    "k": 3,
                    "collection": "my_project_recursive_gemma2_9b_it"
                }
            ]
        }
    }

class ChunkInfo(BaseModel):
    """Information about a retrieved chunk."""
    content: str = Field(..., description="The chunk content")
    source: str = Field(default="", description="Source file")
    chunk_type: Optional[str] = Field(default=None, description="Type of chunk (function, class, etc.)")
    start_line: Optional[int] = Field(default=None, description="Start line in source file")
    end_line: Optional[int] = Field(default=None, description="End line in source file")
    name: Optional[str] = Field(default=None, description="Name of function/class if applicable")

class QueryResponse(BaseModel):
    """Response model for queries."""
    answer: str = Field(..., description="Generated answer from the LLM")
    retrieved_chunks: list[ChunkInfo] = Field(
        default_factory=list,
        description="Retrieved context chunks used to generate the answer"
    )
    strategy_used: ChunkingStrategy = Field(..., description="Chunking strategy that was used")
    num_chunks: int = Field(..., description="Number of chunks retrieved")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy")
    version: str = Field(default="0.1.0")

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error info")


class ConfigUpdateRequest(BaseModel):
    """Request model for updating configuration."""
    chunking_strategy: Optional[ChunkingStrategy] = Field(None, description="Chunking strategy")
    retrieval_k: Optional[int] = Field(None, ge=1, le=10, description="Number of documents to retrieve")


class ConfigResponse(BaseModel):
    """Response model for configuration."""
    chunking_strategy: str = Field(..., description="Current chunking strategy")
    retrieval_k: int = Field(..., description="Current retrieval k value")


class DatabasesResponse(BaseModel):
    """Response model for listing available databases."""
    databases: list[str] = Field(..., description="List of ChromaDB collection names")
    count: int = Field(..., description="Number of available databases")


class UploadResponse(BaseModel):
    """Response for zip file upload and indexing."""
    success: bool = Field(..., description="Whether upload and indexing was successful")
    message: str = Field(..., description="Status message")
    num_documents: int = Field(default=0, description="Number of files extracted and indexed")
    num_chunks: int = Field(default=0, description="Number of chunks created")
    strategy_used: str = Field(..., description="Chunking strategy used")
    collection_name: str = Field(..., description="ChromaDB collection name created")

class SelfCheckRequest(BaseModel):
    """Request model for hallucination self-check."""
    query: str = Field(..., description="The original user query")
    response: str = Field(..., description="The response to check for hallucinations")
    collection: str = Field(..., description="ChromaDB collection name to use for generating the sampled response")
    k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of documents to retrieve for the sampled response"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What classes are defined in this code?",
                    "response": "The code defines a UserService class.",
                    "collection": "my_project_recursive_gemma2_9b_it",
                    "k": 3
                }
            ]
        }
    }


class SelfCheckResponse(BaseModel):
    """Response model for hallucination self-check."""
    is_hallucinating: bool = Field(..., description="True if hallucination detected")
    similarity_score: float = Field(..., description="Cosine similarity between responses (0-1)")

