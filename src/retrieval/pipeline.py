"""
Retrieval pipeline: embeddings, vector store, and retrieval tool.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.tools import tool

from src.config import settings
from src.chunking import get_chunker, BaseChunker


class RetrievalPipeline:
    """
    Manages the retrieval pipeline: embeddings, vector store, and indexing.
    
    Args:
        chunker: Chunking strategy to use. If None, uses config default.
        source_dir: Optional source directory name to include in collection name.
    """
    
    def __init__(self, chunker: BaseChunker | None = None, source_dir: str | None = None):
        self.chunker = chunker or get_chunker(settings.CHUNKING_STRATEGY)
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        # Create a safe collection name based on source dir, strategy and model
        model_slug = settings.LLM_MODEL.split("/")[-1].replace("-", "_").replace(".", "_")
        if source_dir:
            collection_name = f"{source_dir}_{self.chunker.name}_{model_slug}"
        else:
            collection_name = f"{self.chunker.name}_{model_slug}"
        
        # Initialize Chroma vector store
        self.chroma = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.VECTOR_DB_DIR,
        )
        
        # Use GraphRAG retriever or standard vector store
        if settings.RETRIEVAL_MODE == "graph":
            from langchain_graph_retriever import GraphRetriever
            self.retriever = GraphRetriever(
                store=self.chroma,
                edges=[("mentions", "mentioned_by")],  # Define relationships
                k=settings.RETRIEVAL_K,
            )
        else:
            self.retriever = None  # Use vector_store directly
        
        self.vector_store = self.chroma
        
        # Track indexed documents
        self.document_ids: list[str] = []
    
    def index_documents(self, documents: list[Document]) -> list[str]:
        """
        Chunk and index documents into the vector store.
        
        Args:
            documents: Raw documents to process
            
        Returns:
            List of document IDs
        """
        # Split documents using chunker
        chunks = self.chunker.split(documents)
        print(f"Split into {len(chunks)} chunks using {self.chunker.name} strategy")
        
        # Add to vector store
        self.document_ids = self.vector_store.add_documents(documents=chunks)
        print(f"Indexed {len(self.document_ids)} documents")
        
        return self.document_ids
    
    def create_retrieval_tool(self):
        """
        Create a LangChain tool for retrieval.
        
        Returns:
            A tool function that can be used with agents
        """
        retriever = self.retriever
        vector_store = self.vector_store
        k = settings.RETRIEVAL_K
        use_graph = settings.RETRIEVAL_MODE == "graph"
        
        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str):
            """Retrieve information to help answer a query."""
            if use_graph and retriever:
                retrieved_docs = retriever.invoke(query)
            else:
                retrieved_docs = vector_store.similarity_search(query, k=k)
            
            serialized = "\n\n".join(
                f"Source: {doc.metadata}\nContent: {doc.page_content}"
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs
        
        return retrieve_context
    
    def search(self, query: str, k: int | None = None) -> list[Document]:
        """
        Direct similarity search.
        
        Args:
            query: Search query
            k: Number of results (defaults to config)
            
        Returns:
            List of matching documents
        """
        if self.retriever and settings.RETRIEVAL_MODE == "graph":
            return self.retriever.invoke(query)
        return self.vector_store.similarity_search(query, k=k or settings.RETRIEVAL_K)