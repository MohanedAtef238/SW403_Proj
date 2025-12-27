"""Code Knowledge Graph using Kùzu embedded graph database."""

from typing import List
import kuzu
from langchain_core.documents import Document


class CodeKnowledgeGraph:
    """Kùzu-backed Code Knowledge Graph for GraphRAG.
    
    Uses Kùzu embedded database - no external server required.
    """
    
    # Singleton storage for Database instances to prevent file locking issues
    _db_instances = {}

    def __init__(self, db_path: str):
        """Initialize with path to Kùzu database folder.
        
        Args:
            db_path: Path to folder where Kùzu stores data (created if not exists)
        """
        # Ensure only one Database object exists per path to prevent locking errors
        if db_path not in self._db_instances:
            self._db_instances[db_path] = kuzu.Database(db_path)
            
        self.db = self._db_instances[db_path]
        self.conn = kuzu.Connection(self.db)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create node and relationship tables if they don't exist."""
        # Create Entity node table
        try:
            self.conn.execute("""
                CREATE NODE TABLE Entity (
                    name STRING,
                    entity_type STRING,
                    source STRING,
                    start_line INT64,
                    end_line INT64,
                    content STRING,
                    PRIMARY KEY (name)
                )
            """)
        except RuntimeError:
            pass  # Table already exists
        
        # Create relationship tables
        for rel in ["CALLS", "INHERITS_FROM", "CONTAINS", "IMPORTS"]:
            try:
                self.conn.execute(f"CREATE REL TABLE {rel} (FROM Entity TO Entity)")
            except RuntimeError:
                pass  # Table already exists
    
    def close(self):
        """Close database connection."""
        # Kùzu handles cleanup automatically
        pass
    
    def clear(self):
        """Clear all nodes and relationships."""
        self.conn.execute("MATCH (n) DETACH DELETE n")
    
    def add_entities(self, documents: List[Document]):
        """Build graph from GraphChunker output."""
        for doc in documents:
            meta = doc.metadata
            name = meta.get("name")
            if not name:
                continue
            
            # Create entity node using MERGE
            self.conn.execute(
                """
                MERGE (e:Entity {name: $name})
                SET e.entity_type = $entity_type,
                    e.source = $source,
                    e.start_line = $start_line,
                    e.end_line = $end_line,
                    e.content = $content
                """,
                {
                    "name": name,
                    "entity_type": meta.get("entity_type", "unknown"),
                    "source": meta.get("source", ""),
                    "start_line": meta.get("start_line") or 0,
                    "end_line": meta.get("end_line") or 0,
                    "content": doc.page_content,
                }
            )
            
            # Create CALLS relationships
            for called in meta.get("calls", []):
                self._create_relationship(name, called, "CALLS")
            
            # Create INHERITS_FROM relationships
            for base in meta.get("inherits_from", []):
                self._create_relationship(name, base, "INHERITS_FROM")
            
            # Create CONTAINS relationships
            for method in meta.get("contains_methods", []):
                self._create_relationship(name, method, "CONTAINS")
                
            # Create IMPORTS relationships
            for imported in meta.get("imports", []):
                self._create_relationship(name, imported, "IMPORTS")
    
    def _create_relationship(self, from_name: str, to_name: str, rel_type: str):
        """Create a relationship between two entities."""
        self.conn.execute(
            f"""
            MERGE (a:Entity {{name: $from_name}})
            MERGE (b:Entity {{name: $to_name}})
            MERGE (a)-[:{rel_type}]->(b)
            """,
            {"from_name": from_name, "to_name": to_name}
        )
    
    def get_call_chain(self, start_name: str, max_depth: int = 3) -> List[Document]:
        """Traverse CALLS relationships using Cypher."""
        result = self.conn.execute(
            f"""
            MATCH (start:Entity {{name: $name}})-[:CALLS*0..{max_depth}]->(called:Entity)
            WHERE called.content IS NOT NULL
            RETURN DISTINCT called.name AS name,
                   called.entity_type AS entity_type,
                   called.source AS source,
                   called.start_line AS start_line,
                   called.end_line AS end_line,
                   called.content AS content
            """,
            {"name": start_name}
        )
        return self._results_to_documents(result)
    
    def get_callers(self, entity_name: str) -> List[Document]:
        """Find what calls this entity."""
        result = self.conn.execute(
            """
            MATCH (caller:Entity)-[:CALLS]->(target:Entity {name: $name})
            WHERE caller.content IS NOT NULL
            RETURN caller.name AS name,
                   caller.entity_type AS entity_type,
                   caller.source AS source,
                   caller.start_line AS start_line,
                   caller.end_line AS end_line,
                   caller.content AS content
            """,
            {"name": entity_name}
        )
        return self._results_to_documents(result)
    
    def get_class_with_methods(self, class_name: str) -> List[Document]:
        """Get a class and all its methods."""
        result = self.conn.execute(
            """
            MATCH (c:Entity {name: $name})
            WHERE c.content IS NOT NULL
            OPTIONAL MATCH (c)-[:CONTAINS]->(m:Entity)
            WHERE m.content IS NOT NULL
            WITH c, collect(m) AS methods
            UNWIND [c] + methods AS entity
            RETURN DISTINCT entity.name AS name,
                   entity.entity_type AS entity_type,
                   entity.source AS source,
                   entity.start_line AS start_line,
                   entity.end_line AS end_line,
                   entity.content AS content
            """,
            {"name": class_name}
        )
        return self._results_to_documents(result)
    
    def hybrid_search(self, entity_names: List[str], max_depth: int = 2) -> List[Document]:
        """Expand vector search results with graph context."""
        all_docs = []
        seen = set()
        
        for name in entity_names:
            docs = self.get_call_chain(name, max_depth)
            for doc in docs:
                doc_name = doc.metadata.get("name")
                if doc_name not in seen:
                    all_docs.append(doc)
                    seen.add(doc_name)
        
        return all_docs
    
    def _results_to_documents(self, result) -> List[Document]:
        """Convert Kùzu query result to LangChain Documents."""
        docs = []
        while result.has_next():
            row = result.get_next()
            docs.append(Document(
                page_content=row[5] or "",  # content
                metadata={
                    "name": row[0],
                    "entity_type": row[1],
                    "source": row[2],
                    "start_line": row[3],
                    "end_line": row[4],
                }
            ))
        return docs