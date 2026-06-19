"""
Sutra Retriever: Automatic Sutra Selection
Finds relevant sutras based on query intent
"""

import sqlite3
import os
import re
from difflib import SequenceMatcher

class SutraRetriever:
    def __init__(self, db_path: str = "registry/soca.db"):
        self.db_path = db_path
    
    def retrieve(self, query: str, top_k: int = 5) -> list:
        """
        Retrieve relevant sutras for a given query.
        
        Args:
            query: Natural language query
            top_k: Number of sutras to return
        
        Returns:
            List of sutra IDs in order of relevance
        """
        query_lower = query.lower()
        
        # Get all active sutras
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sutra_id, name, category, pramana, pramana_confidence
                FROM sutra_registry
                WHERE is_active = TRUE
            """)
            sutras = cursor.fetchall()
        
        # Score each sutra
        scored = []
        for sutra in sutras:
            sutra_id, name, category, pramana, confidence = sutra
            score = self._score_sutra(query_lower, name, category, confidence)
            scored.append((sutra_id, name, score, confidence))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[2], reverse=True)
        
        # Return top_k
        return [s[0] for s in scored[:top_k]]
    
    def _score_sutra(self, query: str, name: str, category: str, confidence: float) -> float:
        """Score a sutra's relevance to the query."""
        score = 0.0
        
        # Exact match in name
        if query in name.lower():
            score += 0.5
        
        # Exact match in category
        if query in category.lower():
            score += 0.3
        
        # Word overlap
        query_words = set(query.split())
        name_words = set(name.lower().split())
        category_words = set(category.lower().split())
        
        overlap = len(query_words.intersection(name_words))
        if overlap > 0:
            score += overlap * 0.1
        
        # Category match
        category_patterns = {
            'planning': ['schedule', 'plan', 'task', 'dependency', 'graph'],
            'arithmetic': ['add', 'multiply', 'math', 'number', 'count'],
            'logic': ['compare', 'if', 'and', 'or'],
            'memory': ['store', 'retrieve', 'remember', 'kosha'],
            'codegen': ['code', 'generate', 'python', 'function'],
            'evolution': ['discover', 'generate', 'validate', 'evolve']
        }
        
        for cat, keywords in category_patterns.items():
            if category == cat:
                for kw in keywords:
                    if kw in query:
                        score += 0.2
                        break
                break
        
        # Confidence boost
        score *= confidence
        
        return score
    
    def explain(self, query: str) -> dict:
        """Explain the retrieval decision."""
        sutra_ids = self.retrieve(query, top_k=5)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            results = []
            for sid in sutra_ids:
                cursor.execute("""
                    SELECT sutra_id, name, category, pramana_confidence
                    FROM sutra_registry
                    WHERE sutra_id = ?
                """, (sid,))
                row = cursor.fetchone()
                if row:
                    results.append({
                        'sutra_id': row[0],
                        'name': row[1],
                        'category': row[2],
                        'confidence': row[3]
                    })
        return {
            'query': query,
            'retrieved': results
        }
