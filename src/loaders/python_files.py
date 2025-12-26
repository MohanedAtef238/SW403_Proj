"""Load Python files from local filesystem."""

from pathlib import Path
from langchain_core.documents import Document


def load_python_files(paths: list[str | Path]) -> list[Document]:
    """
    Load Python files from local paths.
    
    Args:
        paths: List of file paths or directory paths
        
    Returns:
        List of Document objects with source metadata
    """
    documents = []
    
    for path in paths:
        path = Path(path)
        
        if path.is_file() and path.suffix == ".py":
            content = path.read_text(encoding="utf-8")
            documents.append(Document(
                page_content=content,
                metadata={"source": str(path), "file_type": "python"}
            ))
        elif path.is_dir():
            # Load all .py files in directory
            for py_file in path.glob("**/*.py"):
                content = py_file.read_text(encoding="utf-8")
                documents.append(Document(
                    page_content=content,
                    metadata={"source": str(py_file), "file_type": "python"}
                ))
    
    return documents
