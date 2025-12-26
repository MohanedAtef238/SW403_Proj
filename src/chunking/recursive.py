"""Recursive character text splitter - LangChain's default."""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from .base import BaseChunker


class RecursiveChunker(BaseChunker):
    """Wraps LangChain's RecursiveCharacterTextSplitter."""
    
    name = "recursive"
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, **kwargs):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    
    def split(self, documents: list[Document]) -> list[Document]:
        return self.splitter.split_documents(documents)
