"""
Configuration settings for the RAG pipeline.
Loads environment variables and defines model/chunking parameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv(Path(__file__).parent.parent.parent / ".env")


class Settings:
    """Central configuration for RAG experiments."""

    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_TRACING: str = os.getenv("LANGSMITH_TRACING", "true")
    
    ASTRA_DB_APPLICATION_TOKEN: str = os.getenv("ASTRA_DB_APPLICATION_TOKEN", "")
    ASTRA_DB_API_ENDPOINT: str = os.getenv("ASTRA_DB_API_ENDPOINT", "")

    # LLM Configuration
    LLM_MODEL: str = "qwen/qwen3-32b"
    LLM_TEMPERATURE: float = 0
    LLM_MAX_RETRIES: int = 2

    # Embeddings Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    
    CHUNKER_NAME: str = "context"

    # Chunking Configuration
    # Options: "function" (P1), "ast" (P2), "context" (P3), "graph" (P4)
    CHUNKING_STRATEGY: str = "function"
    
    # Retrieval Mode: "vector" (P1-P3) or "graph" (P4)
    RETRIEVAL_MODE: str = "vector"

    # Recursive chunker settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Semantic chunker settings (for future use)
    SEMANTIC_BREAKPOINT_THRESHOLD: float = 0.5

    # Retrieval Configuration
    RETRIEVAL_K: int = 2

    # Storage Configuration
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    VECTOR_DB_DIR: str = str(BASE_DIR / "chroma_db")
    KUZU_DB_DIR: str = str(BASE_DIR / "kuzu_db")

    def __init__(self):
        # Set environment variables for LangChain/LangSmith
        os.environ["GROQ_API_KEY"] = self.GROQ_API_KEY
        os.environ["LANGSMITH_API_KEY"] = self.LANGSMITH_API_KEY
        os.environ["LANGSMITH_TRACING"] = self.LANGSMITH_TRACING
        
        os.environ["ASTRA_DB_APPLICATION_TOKEN"] = self.ASTRA_DB_APPLICATION_TOKEN
        os.environ["ASTRA_DB_API_ENDPOINT"] = self.ASTRA_DB_API_ENDPOINT
        



settings = Settings()