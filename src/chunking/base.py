"""Base chunker interface."""

from abc import ABC, abstractmethod
from langchain_core.documents import Document


class BaseChunker(ABC):
    """Abstract base class for all chunking strategies."""
    
    name: str = "base"
    
    @abstractmethod
    def split(self, documents: list[Document]) -> list[Document]:
        """Split documents into chunks."""
        pass
