"""P4: GraphRAG chunker that extracts code relationships."""

import ast
from typing import Dict, List, Set
from langchain_core.documents import Document
from .base import BaseChunker


class GraphChunker(BaseChunker):
    """
    P4: Extracts code entities and relationships for GraphRAG.
    Builds a Code Knowledge Graph with CALLS, IMPORTS, INHERITS relationships.
    """
    
    name = "graph"
    
    def __init__(self, **kwargs):
        pass
    
    def split(self, documents: list[Document]) -> list[Document]:
        """Extract entities with relationship metadata."""
        result = []
        
        for doc in documents:
            source = doc.metadata.get("source", "")
            entities = self._extract_entities_with_relations(doc.page_content, source)
            result.extend(entities)
        
        return result
    
    def _extract_entities_with_relations(self, code: str, source: str) -> list[Document]:
        """Extract functions/classes with their relationships."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        lines = code.split("\n")
        chunks = []
        
        # First pass: collect all defined names
        defined_names: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined_names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                defined_names.add(node.name)
        
        # Extract imports
        imports: List[str] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.append(module)
        
        # Process classes
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                chunk = self._process_class(node, lines, source, defined_names, imports)
                chunks.append(chunk)
        
        # Process top-level functions
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                chunk = self._process_function(node, lines, source, defined_names, imports)
                chunks.append(chunk)
        
        return chunks
    
    def _process_function(self, node, lines, source, defined_names, imports) -> Document:
        """Extract function with CALLS relationships."""
        start = node.lineno - 1
        end = node.end_lineno or start + 1
        chunk_text = "\n".join(lines[start:end])
        
        # Find all function calls within this function
        calls = self._extract_calls(node, defined_names)
        
        return Document(
            page_content=chunk_text,
            metadata={
                "source": source,
                "entity_type": "function",
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                # Graph relationships
                "calls": list(calls),  # CALLS relationship
                "imports": imports,     # IMPORTS relationship
            }
        )
    
    def _process_class(self, node: ast.ClassDef, lines, source, defined_names, imports) -> Document:
        """Extract class with INHERITS and contains relationships."""
        start = node.lineno - 1
        end = node.end_lineno or start + 1
        chunk_text = "\n".join(lines[start:end])
        
        # Extract base classes
        inherits = []
        for base in node.bases:
            try:
                inherits.append(ast.unparse(base))
            except:
                pass
        
        # Extract method names
        methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        
        # Find all calls within the class
        calls = self._extract_calls(node, defined_names)
        
        return Document(
            page_content=chunk_text,
            metadata={
                "source": source,
                "entity_type": "class",
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                # Graph relationships
                "inherits_from": inherits,  # INHERITS relationship
                "contains_methods": methods, # CONTAINS relationship
                "calls": list(calls),        # CALLS relationship
                "imports": imports,
            }
        )
    
    def _extract_calls(self, node, defined_names: Set[str]) -> Set[str]:
        """Find all calls to known functions/classes within a node."""
        calls = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in defined_names:
                        calls.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.add(child.func.attr)
        return calls