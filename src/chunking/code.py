"""Code-aware text splitter using LangChain's language-aware splitter."""

from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document
from .base import BaseChunker


class CodeChunker(BaseChunker):
    """Wraps LangChain's code-aware RecursiveCharacterTextSplitter."""
    
    name = "code"
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, language: Language = Language.PYTHON, **kwargs):
        self.splitter = RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    
    def split(self, documents: list[Document]) -> list[Document]:
        return self.splitter.split_documents(documents)
