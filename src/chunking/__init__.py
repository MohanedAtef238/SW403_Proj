"""
Chunking module for text splitting strategies.

Available Chunkers:
-------------------
P1: FunctionChunker - Simple function-level baseline
P2: ASTChunker - cAST semantic chunking
P3: ContextEnrichedChunker - cAST with relative positioning
P4: GraphChunker - Code Knowledge Graph extraction

- RecursiveChunker - Character-based splitting
- CodeChunker - Language-aware character splitting
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
from .function_chunker import FunctionChunker
from .context_chunker import ContextEnrichedChunker
from .graph_chunker import GraphChunker


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
        "function": FunctionChunker,   # P1
        "ast": ASTChunker,             # P2
        "context": ContextEnrichedChunker,  # P3
        "graph": GraphChunker,         # P4
    }
    
    if strategy not in chunkers:
        raise ValueError(f"Unknown chunking strategy: {strategy}. Available: {list(chunkers.keys())}")
    
    return chunkers[strategy](**kwargs)
