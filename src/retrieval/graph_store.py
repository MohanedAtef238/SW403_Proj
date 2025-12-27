"""Code Knowledge Graph using Neo4j."""

from typing import List
from neo4j import GraphDatabase
from langchain_core.documents import Document


class CodeKnowledgeGraph:
    """Neo4j-backed Code Knowledge Graph for GraphRAG."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for faster lookups."""
        with self.driver.session() as session:
            session.run("CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)")
    
    def close(self):
        self.driver.close()
    
    def clear(self):
        """Clear all nodes and relationships."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def add_entities(self, documents: List[Document]):
        """Build graph from GraphChunker output."""
        with self.driver.session() as session:
            for doc in documents:
                meta = doc.metadata
                name = meta.get("name")
                if not name:
                    continue
                
                # Create entity node
                session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    SET e.entity_type = $entity_type,
                        e.source = $source,
                        e.start_line = $start_line,
                        e.end_line = $end_line,
                        e.content = $content
                    """,
                    name=name,
                    entity_type=meta.get("entity_type", "unknown"),
                    source=meta.get("source", ""),
                    start_line=meta.get("start_line"),
                    end_line=meta.get("end_line"),
                    content=doc.page_content,
                )
                
                # Create CALLS relationships
                for called in meta.get("calls", []):
                    session.run(
                        """
                        MERGE (a:Entity {name: $from_name})
                        MERGE (b:Entity {name: $to_name})
                        MERGE (a)-[:CALLS]->(b)
                        """,
                        from_name=name,
                        to_name=called,
                    )
                
                # Create INHERITS_FROM relationships
                for base in meta.get("inherits_from", []):
                    session.run(
                        """
                        MERGE (a:Entity {name: $from_name})
                        MERGE (b:Entity {name: $to_name})
                        MERGE (a)-[:INHERITS_FROM]->(b)
                        """,
                        from_name=name,
                        to_name=base,
                    )
                
                # Create CONTAINS relationships
                for method in meta.get("contains_methods", []):
                    session.run(
                        """
                        MERGE (a:Entity {name: $from_name})
                        MERGE (b:Entity {name: $to_name})
                        MERGE (a)-[:CONTAINS]->(b)
                        """,
                        from_name=name,
                        to_name=method,
                    )
                    
                # Create IMPORTS relationships
                for imported in meta.get("imports", []):
                    session.run(
                        """
                        MERGE (a:Entity {name: $from_name})
                        MERGE (b:Entity {name: $to_name})
                        MERGE (a)-[:IMPORTS]->(b)
                        """,
                        from_name=name,
                        to_name=imported,
                    )
    
    def get_call_chain(self, start_name: str, max_depth: int = 3) -> List[Document]:
        """Traverse CALLS relationships using Cypher."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = (start:Entity {name: $name})-[:CALLS*0..%d]->(called:Entity)
                WHERE called.content IS NOT NULL
                RETURN DISTINCT called.name as name,
                       called.entity_type as entity_type,
                       called.source as source,
                       called.start_line as start_line,
                       called.end_line as end_line,
                       called.content as content
                """ % max_depth,
                name=start_name,
            )
            return [self._record_to_document(r) for r in result]
    
    def get_callers(self, entity_name: str) -> List[Document]:
        """Find what calls this entity."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (caller:Entity)-[:CALLS]->(target:Entity {name: $name})
                WHERE caller.content IS NOT NULL
                RETURN caller.name as name,
                       caller.entity_type as entity_type,
                       caller.source as source,
                       caller.start_line as start_line,
                       caller.end_line as end_line,
                       caller.content as content
                """,
                name=entity_name,
            )
            return [self._record_to_document(r) for r in result]
    
    def get_class_with_methods(self, class_name: str) -> List[Document]:
        """Get a class and all its methods."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Entity {name: $name})
                WHERE c.content IS NOT NULL
                OPTIONAL MATCH (c)-[:CONTAINS]->(m:Entity)
                WHERE m.content IS NOT NULL
                WITH c, collect(m) as methods
                UNWIND [c] + methods as entity
                RETURN DISTINCT entity.name as name,
                       entity.entity_type as entity_type,
                       entity.source as source,
                       entity.start_line as start_line,
                       entity.end_line as end_line,
                       entity.content as content
                """,
                name=class_name,
            )
            return [self._record_to_document(r) for r in result]
    
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
    
    def _record_to_document(self, record) -> Document:
        """Convert Neo4j record to LangChain Document."""
        return Document(
            page_content=record["content"] or "",
            metadata={
                "name": record["name"],
                "entity_type": record["entity_type"],
                "source": record["source"],
                "start_line": record["start_line"],
                "end_line": record["end_line"],
            }
        )