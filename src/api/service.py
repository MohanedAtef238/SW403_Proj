"""
RAG Pipeline Service - manages pipelines for different chunking strategies.
"""

from pathlib import Path
import tempfile
import zipfile
from typing import Any

from langchain_core.documents import Document

from src.api.utils import load_system_prompt
from src.config import settings
from src.loaders import load_python_files
from src.chunking import get_chunker
from src.retrieval import RetrievalPipeline
from src.agents import create_rag_agent

from .models import ChunkingStrategy


class RAGService:
    """Service class that manages RAG pipelines for different strategies."""

    def __init__(self):
        self.pipelines: dict[str, RetrievalPipeline] = {}
        self.indexed_files: dict[str, list[str]] = {}

    def get_or_create_pipeline(
        self, strategy: ChunkingStrategy, source_dir: str | None = None
    ) -> RetrievalPipeline:
        """Get existing pipeline or create a new one."""
        key = f"{source_dir}_{strategy.value}" if source_dir else strategy.value

        if key not in self.pipelines:
            chunker = get_chunker(
                strategy.value,
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
            )
            self.pipelines[key] = RetrievalPipeline(
                chunker=chunker, source_dir=source_dir
            )
            self.indexed_files[key] = []

        return self.pipelines[key]

    def index_files(
        self, file_paths: list[str], strategy: ChunkingStrategy, base_path: str = "data"
    ) -> tuple[int, int]:
        """Index files using the specified strategy."""
        source_dir = None
        if file_paths:
            first_path = Path(file_paths[0])
            if first_path.parts:
                source_dir = first_path.parts[0]

        pipeline = self.get_or_create_pipeline(strategy, source_dir)
        key = f"{source_dir}_{strategy.value}" if source_dir else strategy.value

        full_paths = [str(Path(base_path) / fp) for fp in file_paths]
        docs = load_python_files(full_paths)

        if not docs:
            return 0, 0

        doc_ids = pipeline.index_documents(docs)
        self.indexed_files[key].extend(file_paths)

        return len(docs), len(doc_ids)

    def query_with_agent(
        self,
        query: str,
        strategy: ChunkingStrategy,
        k: int = 3,
        temp: int = settings.LLM_TEMPERATURE,
        collection: str | None = None
    ) -> tuple[str, list[Document]]:
        """Query using the RAG agent.
        
        Args:
            query: The user's question
            strategy: Chunking strategy (used if no collection specified)
            k: Number of documents to retrieve
            collection: Optional ChromaDB collection name to query directly
        """
        if collection:
            # Query a specific collection directly
            pipeline = self._get_pipeline_for_collection(collection)
        else:
            pipeline = self.get_or_create_pipeline(strategy)

        # Temporarily set k
        original_k = settings.RETRIEVAL_K
        settings.RETRIEVAL_K = k

        # initiating and running agents
        retrieval_tool = pipeline.create_retrieval_tool()

        system_prompt = load_system_prompt("./system_prompt")
        agent = create_rag_agent(
            tools=[retrieval_tool], system_prompt=system_prompt, temp=temp
        )

        messages = [{"role": "user", "content": query}]
        result = agent.invoke({"messages": messages})

        # Restore original k because every time we change it, it is changed globally
        settings.RETRIEVAL_K = original_k

        # Extract answer and get retrieved docs
        answer = result["messages"][-1].content
        retrieved_docs = pipeline.search(query, k=k)

        return answer, retrieved_docs

    def _get_pipeline_for_collection(self, collection_name: str) -> RetrievalPipeline:
        """Get or create a pipeline for a specific ChromaDB collection."""
        if collection_name in self.pipelines:
            return self.pipelines[collection_name]
        
        parts = collection_name.split("_")
        strategy_name = "function"  # Default to P1
        for part in parts:
            if part in ("function", "ast", "context", "graph"):
                strategy_name = part
                break
        
        chunker = get_chunker(
            strategy_name,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_astradb import AstraDBVectorStore
        
        embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        vector_store = AstraDBVectorStore(
            collection_name=collection_name,
            embedding=embeddings,
            api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
            token=settings.ASTRA_DB_APPLICATION_TOKEN,
        )
        
        pipeline = RetrievalPipeline(chunker=chunker)
        pipeline.vector_store = vector_store
        pipeline.embeddings = embeddings
        
        self.pipelines[collection_name] = pipeline
        return pipeline

    def index_from_zip(
        self,
        zip_file: Any,
        zip_name: str,
        strategy: ChunkingStrategy,
    ) -> tuple[int, int, str]:
        """
        Extract and index Python files from a zip archive.
        
        Args:
            zip_file: SpooledTemporaryFile from FastAPI's UploadFile
            zip_name: Original filename of the uploaded zip
            strategy: Chunking strategy to use
            
        Returns:
            Tuple of (num_documents, num_chunks, collection_name)
        """
        source_dir = Path(zip_name).stem  # Use zip name as source identifier
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # Extract zip contents
            with zipfile.ZipFile(zip_file) as zf:
                zf.extractall(tmp_path)
            
            # Collect all .py files, excluding common non-source directories
            py_files = [
                f for f in tmp_path.glob("**/*.py")
                if not any(part.startswith('.') or part in ('__pycache__', 'node_modules', 'venv', '.venv')
                           for part in f.parts)
            ]
            
            if not py_files:
                return 0, 0, ""
            
            # Load documents
            docs = load_python_files([str(f) for f in py_files])
            
            if not docs:
                return 0, 0, ""
            
            # Create pipeline and index
            pipeline = self.get_or_create_pipeline(strategy, source_dir)
            doc_ids = pipeline.index_documents(docs)
            
            # Build collection name (matches RetrievalPipeline naming)
            model_slug = settings.LLM_MODEL.split("/")[-1].replace("-", "_").replace(".", "_")
            safe_source = "".join(c if c.isalnum() else "_" for c in source_dir)
            collection_name = f"{safe_source}_{strategy.value}_{model_slug}"
            if len(collection_name) > 48:
                collection_name = collection_name[:48]
            
        return len(docs), len(doc_ids), collection_name

    def check_hallucination(
        self,
        query: str,
        response: str,
        collection: str,
        k: int = 3,
    ) -> tuple[float, bool]:
        """
        Check if a response is hallucinating using SelfCheckGPT.
        
        Args:
            query: The original user query
            response: The response to check for hallucinations
            collection: ChromaDB collection name to use
            k: Number of documents to retrieve for the sampled response
            
        Returns:
            Tuple of (similarity_score, is_hallucinating)
        """
        from src.retrieval.selfcheckgpt import SelfCheckGPT
        
        pipeline = self._get_pipeline_for_collection(collection)
        
        checker = SelfCheckGPT(
            chunker=pipeline.chunker,
            k=k,
        )
        
        similarity, is_hallucinating = checker.is_hallucinating(
            query=query,
            inital_response=response,
        )
        
        return similarity, is_hallucinating

    def list_collections(self) -> list[str]:
        """List all available collections from AstraDB."""
        from langchain_astradb import AstraDBVectorStore
        from langchain_huggingface import HuggingFaceEmbeddings
        from astrapy import DataAPIClient
        
        # Use AstraDB client to list collections
        client = DataAPIClient(settings.ASTRA_DB_APPLICATION_TOKEN)
        db = client.get_database(settings.ASTRA_DB_API_ENDPOINT)
        
        collections = []
        for coll in db.list_collection_names():
            collections.append(coll)
        
        return collections

   


rag_service = RAGService()
