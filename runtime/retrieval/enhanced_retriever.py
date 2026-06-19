"""
Enhanced Sutra Retriever with Knowledge Graph
"""

import sqlite3
import os
import sys
sys.path.append('runtime/graph')
from knowledge_graph import KnowledgeGraph

class EnhancedRetriever:
    def __init__(self, db_path: str = "registry/soca.db"):
        self.db_path = db_path
        self.graph = KnowledgeGraph(db_path)
        self.graph.build_default_graph()
    
    def retrieve(self, query: str, top_k: int = 10) -> list:
        """Retrieve sutras using knowledge graph."""
        query_lower = query.lower()
        
        # Extract concepts from query
        concepts = self._extract_concepts(query_lower)
        
        results = []
        seen = set()
        
        for concept in concepts:
            sutras = self.graph.get_sutras_for_concept(concept, min_confidence=0.3)
            for sutra_id, name, confidence in sutras:
                if sutra_id not in seen:
                    results.append({
                        'sutra_id': sutra_id,
                        'name': name,
                        'confidence': confidence,
                        'concept': concept
                    })
                    seen.add(sutra_id)
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Return top_k sutra IDs
        return [r['sutra_id'] for r in results[:top_k]], results[:top_k]
    
    def _extract_concepts(self, query: str) -> list:
        """Extract concepts from query."""
        # Simple concept extraction
        concept_map = {
            'crop': ['crop', 'plant', 'grow', 'cultivate'],
            'soil': ['soil', 'earth', 'ground'],
            'season': ['season', 'kharif', 'rabi', 'summer', 'winter'],
            'rainfall': ['rain', 'rainfall', 'monsoon'],
            'pest': ['pest', 'insect', 'disease'],
            'water': ['water', 'irrigation', 'drainage'],
            'math': ['math', 'numbers', 'addition', 'subtraction'],
            'language': ['language', 'translate', 'translate', 'hindi', 'assamese']
        }
        
        found = []
        for concept, keywords in concept_map.items():
            for kw in keywords:
                if kw in query:
                    found.append(concept)
                    break
        
        return found if found else ['general']
    
    def explain(self, query: str) -> dict:
        """Explain retrieval decisions."""
        sutra_ids, details = self.retrieve(query)
        return {
            'query': query,
            'concepts': self._extract_concepts(query),
            'retrieved_sutras': details
        }
