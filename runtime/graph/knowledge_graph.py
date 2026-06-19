"""
Knowledge Graph for SOCA
Maps concepts to sutras with confidence scores
"""

import sqlite3
import json
import os

class KnowledgeGraph:
    def __init__(self, db_path: str = "registry/soca.db"):
        self.db_path = db_path
        self._ensure_graph()
    
    def _ensure_graph(self):
        """Create graph tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Concepts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concepts (
                    concept_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    domain TEXT,
                    description TEXT
                )
            """)
            
            # Sutra-Concept mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sutra_concepts (
                    sutra_id TEXT,
                    concept_id INTEGER,
                    confidence REAL DEFAULT 0.5,
                    FOREIGN KEY (sutra_id) REFERENCES sutra_registry(sutra_id),
                    FOREIGN KEY (concept_id) REFERENCES concepts(concept_id)
                )
            """)
            
            # Concept relationships
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS concept_relations (
                    from_concept INTEGER,
                    to_concept INTEGER,
                    relation_type TEXT,
                    FOREIGN KEY (from_concept) REFERENCES concepts(concept_id),
                    FOREIGN KEY (to_concept) REFERENCES concepts(concept_id)
                )
            """)
            
            conn.commit()
    
    def add_concept(self, name: str, domain: str, description: str = ""):
        """Add a concept to the graph."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO concepts (name, domain, description)
                VALUES (?, ?, ?)
            """, (name, domain, description))
            conn.commit()
            return cursor.lastrowid
    
    def link_sutra_to_concept(self, sutra_id: str, concept_name: str, confidence: float = 0.5):
        """Link a sutra to a concept."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get concept ID
            cursor.execute("SELECT concept_id FROM concepts WHERE name = ?", (concept_name,))
            row = cursor.fetchone()
            if not row:
                concept_id = self.add_concept(concept_name, 'general')
            else:
                concept_id = row[0]
            
            cursor.execute("""
                INSERT OR REPLACE INTO sutra_concepts (sutra_id, concept_id, confidence)
                VALUES (?, ?, ?)
            """, (sutra_id, concept_id, confidence))
            conn.commit()
    
    def get_sutras_for_concept(self, concept_name: str, min_confidence: float = 0.3) -> list:
        """Get sutras related to a concept."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.sutra_id, s.name, sc.confidence
                FROM sutra_concepts sc
                JOIN sutra_registry s ON sc.sutra_id = s.sutra_id
                JOIN concepts c ON sc.concept_id = c.concept_id
                WHERE c.name = ? AND sc.confidence >= ?
                ORDER BY sc.confidence DESC
            """, (concept_name, min_confidence))
            return cursor.fetchall()
    
    def get_related_concepts(self, concept_name: str, max_depth: int = 2) -> list:
        """Get concepts related to a concept."""
        # Simplified: just return concepts from same domain
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT c2.name
                FROM concepts c1
                JOIN concepts c2 ON c1.domain = c2.domain
                WHERE c1.name = ? AND c2.name != ?
                LIMIT 10
            """, (concept_name, concept_name))
            return [row[0] for row in cursor.fetchall()]
    
    def build_default_graph(self):
        """Build default knowledge graph for core domains."""
        # Agriculture concepts
        concepts = [
            ('crop', 'agriculture'),
            ('soil', 'agriculture'),
            ('season', 'agriculture'),
            ('rainfall', 'agriculture'),
            ('pest', 'agriculture'),
            ('water', 'agriculture'),
            ('fertilizer', 'agriculture'),
            ('harvest', 'agriculture'),
            ('education', 'learning'),
            ('math', 'learning'),
            ('science', 'learning'),
            ('language', 'learning'),
            ('health', 'wellness'),
            ('nutrition', 'wellness')
        ]
        
        for name, domain in concepts:
            self.add_concept(name, domain)
        
        # Link sutras to concepts
        links = [
            ('sutra_021', 'crop', 0.9),
            ('sutra_021', 'soil', 0.7),
            ('sutra_021', 'season', 0.8),
            ('sutra_025', 'rainfall', 0.9),
            ('sutra_025', 'season', 0.9),
            ('sutra_026', 'pest', 0.9),
            ('sutra_027', 'water', 0.9),
            ('sutra_027', 'soil', 0.8),
            ('sutra_022', 'math', 0.9),
            ('sutra_022', 'education', 0.8),
            ('sutra_024', 'language', 0.9)
        ]
        
        for sutra_id, concept, confidence in links:
            self.link_sutra_to_concept(sutra_id, concept, confidence)
        
        print("✅ Knowledge graph built")
