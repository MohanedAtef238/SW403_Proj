"""
Retrieval pipeline: embeddings, vector store, and retrieval tool.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_astradb import AstraDBVectorStore
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
            # Sanitize source_dir: replace non-alphanumeric with underscore
            safe_source = "".join(c if c.isalnum() else "_" for c in source_dir)
            collection_name = f"{safe_source}_{self.chunker.name}_{model_slug}"
        else:
            collection_name = f"{self.chunker.name}_{model_slug}"
        
        if len(collection_name) > 48:
            collection_name = collection_name[:48]
        
        # Initialize vector store
        self.vector_store = AstraDBVectorStore(
            collection_name=collection_name,
            embedding=self.embeddings,
            api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
            token=settings.ASTRA_DB_APPLICATION_TOKEN,
        )
        
        # Initialize Kùzu graph store for GraphRAG mode (P4)
        self.graph_store = None
        if self.chunker.name == "graph":
            from src.retrieval.graph_store import CodeKnowledgeGraph
            self.graph_store = CodeKnowledgeGraph(db_path=settings.KUZU_DB_DIR)
        
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
        
        # Build Neo4j knowledge graph if in graph mode
        if self.graph_store and self.chunker.name == "graph":
            self.graph_store.add_entities(chunks)
            print("Built Kùzu Code Knowledge Graph")
        
        # Add to vector store
        self.document_ids = self.vector_store.add_documents(documents=chunks)
        print(f"Indexed {len(self.document_ids)} documents")
        
        return self.document_ids
            
    def create_retrieval_tool(self):
        """Create a LangChain tool for retrieval."""
        vector_store = self.vector_store
        graph_store = self.graph_store
        k = settings.RETRIEVAL_K
        chunker_name = self.chunker.name
        use_graph = chunker_name == "graph" and graph_store is not None
        pipeline_ref = self
        
        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str):
            """Retrieve information to help answer a query."""
            
            # Use context-aware search for P3
            if chunker_name == "context":
                retrieved_docs = pipeline_ref.search_with_context(query, k=k)
            # Use graph expansion for P4
            elif use_graph and graph_store:
                retrieved_docs = vector_store.similarity_search(query, k=k)
                entity_names = [
                    doc.metadata.get("name") 
                    for doc in retrieved_docs 
                    if doc.metadata.get("name")
                ]
                if entity_names:
                    retrieved_docs = graph_store.hybrid_search(entity_names, max_depth=2)
            # Default vector search for P1/P2
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
        Direct similarity search with optional graph expansion.
        
        Args:
            query: Search query
            k: Number of results (defaults to config)
            
        Returns:
            List of matching documents
        """
        # Vector search first
        vector_results = self.vector_store.similarity_search(query, k=k or settings.RETRIEVAL_K)
        
        # Expand with graph traversal for GraphRAG
        if self.graph_store and self.chunker.name == "graph":
            entity_names = [
                doc.metadata.get("name") 
                for doc in vector_results 
                if doc.metadata.get("name")
            ]
            if entity_names:
                return self.graph_store.hybrid_search(entity_names, max_depth=2)
        
        return vector_results
    
    
    def search_with_context(self, query: str, k: int = 2) -> list[Document]:
        """Search with adjacent chunk expansion for P3."""
        results = self.vector_store.similarity_search(query, k=k)
        expanded = []
        for doc in results:
            expanded.append(doc)
            # Fetch prev/next chunks by ID
            for adj_id in [doc.metadata.get("prev_chunk_id"), doc.metadata.get("next_chunk_id")]:
                if adj_id:
                    adj_docs = self.vector_store.similarity_search(
                        "", k=1, filter={"chunk_id": adj_id}
                    )
                    expanded.extend(adj_docs)
        return expanded