"""P1 Baseline: Simple function-level splitting without enrichment."""

import ast
from langchain_core.documents import Document
from .base import BaseChunker


class FunctionChunker(BaseChunker):
    """
    P1 Baseline: Splits code into function/class-level chunks.
    No enrichment, no metadata beyond source location.
    """
    
    name = "function"
    
    def __init__(self, **kwargs):
        pass
    
    def split(self, documents: list[Document]) -> list[Document]:
        """Split documents by top-level functions and classes only."""
        result = []
        
        for doc in documents:
            source = doc.metadata.get("source", "")
            chunks = self._extract_top_level(doc.page_content, source)
            result.extend(chunks)
        
        return result
    
    def _extract_top_level(self, code: str, source: str) -> list[Document]:
        """Extract top-level functions and classes as plain text."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Fallback: return entire file as one chunk
            return [Document(page_content=code, metadata={"source": source})]
        
        lines = code.split("\n")
        chunks = []
        
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = node.end_lineno or start + 1
                chunk_text = "\n".join(lines[start:end])
                
                chunks.append(Document(
                    page_content=chunk_text,
                    metadata={
                        "source": source,
                        "start_line": node.lineno,
                        "end_line": node.end_lineno,
                    }
                ))
        
        return chunks