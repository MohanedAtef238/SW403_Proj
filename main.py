"""
RAG Pipeline Entry Point

This module demonstrates the RAG pipeline with configurable chunking strategies.
Modify src/config/settings.py to experiment with different chunking parameters.

Supported strategies: "recursive", "code", "ast"
"""

from src.config import settings
from src.loaders import load_python_files
from src.chunking import get_chunker
from src.retrieval import RetrievalPipeline
from src.agents import create_rag_agent, run_agent


def main():
    """Run the RAG pipeline."""
    
    # 1. Load Python files from data folder
    print("Loading documents...")
    docs = load_python_files(["data/simple_test_case.py"])
    print(f"Loaded {len(docs)} document(s), {len(docs[0].page_content)} characters")
    
    # 2. Initialize retrieval pipeline with chunking strategy
    print(f"\nUsing chunking strategy: {settings.CHUNKING_STRATEGY}")
    chunker = get_chunker(
        settings.CHUNKING_STRATEGY,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    pipeline = RetrievalPipeline(chunker=chunker)
    
    # 3. Index documents
    print("\nIndexing documents...")
    pipeline.index_documents(docs)
    
    # 4. Create agent with retrieval tool
    print("\nCreating RAG agent...")
    retrieval_tool = pipeline.create_retrieval_tool()
    agent = create_rag_agent(tools=[retrieval_tool])
    
    
    # 5. Run query
    query = (
        "What classes and functions are defined in the code?\n\n"
        "Describe the purpose of the Calculator class."
    )
    print(f"\nQuery: {query}\n")
    print("-" * 50)
    run_agent(agent, query)


if __name__ == "__main__":
    main()
