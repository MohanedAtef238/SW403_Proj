"""Custom AST-based Python code chunker."""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC
import logging

from langchain_text_splitters import TextSplitter
from langchain_core.documents import Document
from .base import BaseChunker

logger = logging.getLogger(__name__)


class Chunk(ABC):
    def __init__(self, chunk_size=1000):
        self.chunk_size = chunk_size


class FunctionChunk(Chunk):
    """Container for a function chunk with comprehensive metadata."""

    def __init__(
        self,
        function_name: str,
        function_signature: str,
        start_line: int,
        end_line: int,
        original_chunk_text: str,
        source: str = "",
        docstring: Optional[str] = None,
        decorators: Optional[List[str]] = None,
        ast_node_type: str = "function",
        complexity_score: int = 1,
    ):
        self.function_name = function_name
        self.function_signature = function_signature
        self.start_line = start_line
        self.end_line = end_line
        self.original_chunk_text = original_chunk_text
        self.source = source
        self.docstring = docstring
        self.decorators = decorators or []
        self.ast_node_type = ast_node_type
        self.complexity_score = complexity_score
        self.chunk_type = "function"

    def get_enhanced_embedding_text(self) -> str:
        """Generate enhanced text for embeddings using AST metadata."""
        parts = []
        if self.decorators:
            parts.append("Decorators: " + ", ".join(self.decorators))
        parts.append(f"Signature: {self.function_signature}")
        if self.docstring:
            parts.append(f"Documentation: {self.docstring}")
        if self.complexity_score > 1:
            parts.append(f"Complexity: {self.complexity_score}")
        parts.append(f"Code:\n{self.original_chunk_text}")
        return "\n".join(parts)


class ClassChunk(Chunk):
    """Container for a class chunk with comprehensive metadata."""

    def __init__(
        self,
        class_name: str,
        start_line: int,
        end_line: int,
        original_chunk_text: str,
        source: str = "",
        docstring: Optional[str] = None,
        base_classes: Optional[List[str]] = None,
        decorators: Optional[List[str]] = None,
        methods: Optional[List[str]] = None,
        complexity_score: int = 1,
    ):
        self.class_name = class_name
        self.start_line = start_line
        self.end_line = end_line
        self.original_chunk_text = original_chunk_text
        self.source = source
        self.docstring = docstring
        self.base_classes = base_classes or []
        self.decorators = decorators or []
        self.methods = methods or []
        self.complexity_score = complexity_score
        self.chunk_type = "class"

    def get_enhanced_embedding_text(self) -> str:
        """Generate enhanced text for embeddings using AST metadata."""
        parts = []
        parts.append(f"Class: {self.class_name}")
        if self.base_classes:
            parts.append(f"Inherits from: {', '.join(self.base_classes)}")
        if self.decorators:
            parts.append(f"Decorators: {', '.join(self.decorators)}")
        if self.docstring:
            parts.append(f"Documentation: {self.docstring}")
        if self.methods:
            parts.append(f"Methods: {', '.join(self.methods)}")
        if self.complexity_score > 1:
            parts.append(f"Complexity: {self.complexity_score}")
        parts.append(f"Code:\n{self.original_chunk_text}")
        return "\n".join(parts)


class ASTTextSplitter(TextSplitter):
    """AST-based text splitter that extracts functions and classes."""

    def extract_function_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract clean function signature from AST node."""
        args = []
        for i, arg in enumerate(node.args.args):
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            defaults_offset = len(node.args.args) - len(node.args.defaults)
            if i >= defaults_offset:
                default_idx = i - defaults_offset
                arg_str += f" = {ast.unparse(node.args.defaults[default_idx])}"
            args.append(arg_str)

        if node.args.vararg:
            vararg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                vararg_str += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(vararg_str)

        for i, arg in enumerate(node.args.kwonlyargs):
            kwarg_str = arg.arg
            if arg.annotation:
                kwarg_str += f": {ast.unparse(arg.annotation)}"
            if i < len(node.args.kw_defaults):
                default_val = node.args.kw_defaults[i]
                if default_val is not None:
                    kwarg_str += f" = {ast.unparse(default_val)}"
            args.append(kwarg_str)

        if node.args.kwarg:
            kwarg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                kwarg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(kwarg_str)

        return_annotation = ""
        if node.returns:
            return_annotation = f" -> {ast.unparse(node.returns)}"

        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        return f"{prefix} {node.name}({', '.join(args)}){return_annotation}:"

    def extract_docstring(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Optional[str]:
        """Extract docstring from function node."""
        if (node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return None

    def extract_decorators(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
        """Extract decorator names from function node."""
        decorators = []
        for decorator in node.decorator_list:
            try:
                decorators.append(ast.unparse(decorator))
            except Exception:
                decorators.append(str(decorator))
        return decorators

    def calculate_complexity(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """Calculate rough cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def extract_class_docstring(self, node: ast.ClassDef) -> Optional[str]:
        if (node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return None

    def extract_class_decorators(self, node: ast.ClassDef) -> List[str]:
        decorators = []
        for decorator in node.decorator_list:
            try:
                decorators.append(ast.unparse(decorator))
            except Exception:
                decorators.append(str(decorator))
        return decorators

    def extract_base_classes(self, node: ast.ClassDef) -> List[str]:
        base_classes = []
        for base in node.bases:
            try:
                base_classes.append(ast.unparse(base))
            except Exception:
                base_classes.append(str(base))
        return base_classes

    def extract_class_methods(self, node: ast.ClassDef) -> List[str]:
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
        return methods

    def calculate_class_complexity(self, node: ast.ClassDef) -> int:
        complexity = 1
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity += self.calculate_complexity(item)
        return complexity

    def split_text(self, text: str, source: str = "") -> List[FunctionChunk | ClassChunk]:
        """Split Python code into AST-based chunks."""
        try:
            tree = ast.parse(text)
            source_lines = text.split("\n")
            chunks = []

            # Extract classes
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    start_line = node.lineno
                    end_line = node.end_lineno if node.end_lineno else start_line
                    class_lines = source_lines[start_line - 1 : end_line]
                    original_text = "\n".join(class_lines)

                    class_chunk = ClassChunk(
                        class_name=node.name,
                        start_line=start_line,
                        end_line=end_line,
                        original_chunk_text=original_text,
                        source=source,
                        docstring=self.extract_class_docstring(node),
                        base_classes=self.extract_base_classes(node),
                        decorators=self.extract_class_decorators(node),
                        methods=self.extract_class_methods(node),
                        complexity_score=self.calculate_class_complexity(node),
                    )
                    chunks.append(class_chunk)

            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start_line = node.lineno
                    end_line = node.end_lineno if node.end_lineno else start_line
                    function_lines = source_lines[start_line - 1 : end_line]
                    original_text = "\n".join(function_lines)

                    chunk = FunctionChunk(
                        function_name=node.name,
                        function_signature=self.extract_function_signature(node),
                        start_line=start_line,
                        end_line=end_line,
                        original_chunk_text=original_text,
                        source=source,
                        docstring=self.extract_docstring(node),
                        decorators=self.extract_decorators(node),
                        ast_node_type="async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                        complexity_score=self.calculate_complexity(node),
                    )
                    chunks.append(chunk)

            return chunks

        except SyntaxError as e:
            logger.error(f"Syntax error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error chunking: {e}")
            return []


class ASTChunker(BaseChunker):
    """AST-based chunker that integrates with the chunking pipeline."""
    
    name = "ast"
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, **kwargs):
        self.splitter = ASTTextSplitter()
        self.chunk_size = chunk_size
    
    def split(self, documents: list[Document]) -> list[Document]:
        """Split documents into AST-based chunks, returning LangChain Documents."""
        result = []
        for doc in documents:
            source = doc.metadata.get("source", "")
            chunks = self.splitter.split_text(doc.page_content, source=source)
            
            for chunk in chunks:
                # Convert to LangChain Document with enhanced text
                result.append(Document(
                    page_content=chunk.get_enhanced_embedding_text(),
                    metadata={
                        "source": source,
                        "chunk_type": chunk.chunk_type,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "name": chunk.function_name if isinstance(chunk, FunctionChunk) else chunk.class_name,
                    }
                ))
        return result
