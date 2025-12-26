"""
Chunking module for text splitting strategies.

Available Chunkers:
-------------------
1. RecursiveChunker - LangChain's default text splitter
2. CodeChunker - LangChain's code-aware splitter
3. ASTChunker - Custom AST-based Python code chunker

Usage:
------
    from src.chunking import get_chunker
    
    chunker = get_chunker("recursive", chunk_size=1000, chunk_overlap=200)
    chunks = chunker.split(documents)
"""

from .base import BaseChunker
from .recursive import RecursiveChunker
from .code import CodeChunker
from .ast_chunker import ASTChunker


def get_chunker(strategy: str, **kwargs) -> BaseChunker:
    """
    Factory function to get a chunker by strategy name.
    
    Args:
        strategy: One of "recursive", "code", "ast"
        **kwargs: Strategy-specific parameters
        
    Returns:
        BaseChunker instance
    """
    chunkers = {
        "recursive": RecursiveChunker,
        "code": CodeChunker,
        "ast": ASTChunker,
    }
    
    if strategy not in chunkers:
        raise ValueError(f"Unknown chunking strategy: {strategy}. Available: {list(chunkers.keys())}")
    
    return chunkers[strategy](**kwargs)
