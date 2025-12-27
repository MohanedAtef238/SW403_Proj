"""P3: cAST with relative positioning for context-enriched retrieval."""

from langchain_core.documents import Document
from .ast_chunker import ASTChunker, ASTTextSplitter


class ContextEnrichedChunker(ASTChunker):
    """
    P3: AST-based chunker with prev/next chunk references.
    Enables retrieval of adjacent chunks for local context.
    """
    
    name = "context"
    
    def split(self, documents: list[Document]) -> list[Document]:
        """Split with relative positioning metadata."""
        result = []
        
        for doc in documents:
            source = doc.metadata.get("source", "")
            chunks = self.splitter.split_text(doc.page_content, source=source)
            
            # Sort by line number for proper ordering
            chunks.sort(key=lambda c: c.start_line)
            
            # Build documents with prev/next references
            for i, chunk in enumerate(chunks):
                prev_id = f"{source}:{chunks[i-1].start_line}" if i > 0 else None
                next_id = f"{source}:{chunks[i+1].start_line}" if i < len(chunks) - 1 else None
                chunk_id = f"{source}:{chunk.start_line}"
                
                result.append(Document(
                    page_content=chunk.get_enhanced_embedding_text(),
                    metadata={
                        "source": source,
                        "chunk_id": chunk_id,
                        "chunk_type": chunk.chunk_type,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "name": getattr(chunk, 'function_name', None) or getattr(chunk, 'class_name', None),
                        # Relative positioning
                        "prev_chunk_id": prev_id,
                        "next_chunk_id": next_id,
                    }
                ))
        
        return result