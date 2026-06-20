"""
Enhanced Sutra Retriever with Knowledge Graph and Parameter Extraction
"""

import sqlite3
import os
import sys
import re
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
    
    def extract_parameters(self, query: str) -> dict:
        """Extract parameters from query (location, soil, season, etc.)"""
        query_lower = query.lower()
        params = {}
        
        # Location extraction
        locations = ['assam', 'axom', 'guwahati', 'jorhat', 'dibrugarh', 
                    'tezpur', 'silchar', 'nagaon', 'tinsukia', 'golaghat']
        for loc in locations:
            if loc in query_lower:
                params['location'] = loc
                break
        
        # Soil type extraction
        soil_types = ['loamy', 'clay', 'sandy', 'laterite', 'alluvial']
        for soil in soil_types:
            if soil in query_lower:
                params['soil_type'] = soil
                break
        
        # Season extraction
        seasons = ['kharif', 'rabi', 'summer', 'winter', 'monsoon']
        for season in seasons:
            if season in query_lower:
                params['season'] = season
                break
        
        # Crop extraction (if mentioned)
        crops = ['rice', 'wheat', 'cotton', 'sugarcane', 'tea', 'jute', 
                'mustard', 'gram', 'lentils', 'potato', 'onion']
        for crop in crops:
            if crop in query_lower:
                params['crop'] = crop
                break
        
        return params
    
    def _extract_concepts(self, query: str) -> list:
        """Extract concepts from query."""
        concept_map = {
            'crop': ['crop', 'plant', 'grow', 'cultivate', 'agriculture', 'farming'],
            'soil': ['soil', 'earth', 'ground', 'loamy', 'clay', 'sandy'],
            'season': ['season', 'kharif', 'rabi', 'summer', 'winter', 'monsoon'],
            'rainfall': ['rain', 'rainfall', 'monsoon', 'weather'],
            'pest': ['pest', 'insect', 'disease', 'bug', 'aphid'],
            'water': ['water', 'irrigation', 'drainage', 'flood'],
            'math': ['math', 'numbers', 'addition', 'subtraction', 'multiplication', 'division', 'fraction', 'decimal'],
            'fraction': ['fraction', 'fractions', 'part', 'whole'],
            'decimal': ['decimal', 'decimals', 'point'],
            'language': ['language', 'translate', 'translation', 'hindi', 'assamese', 'bengali', 'sanskrit'],
            'medicinal': ['medicinal', 'tulsi', 'neem', 'aloe', 'ginger', 'turmeric', 'amla'],
            'education': ['education', 'tutor', 'teach', 'learn', 'school'],
            'code': ['code', 'generate', 'python', 'function', 'program'],
            'weather': ['weather', 'rain', 'rainfall', 'climate', 'monsoon', 'assam', 'kharif', 'rabi', 'season'],
            'market': ['market', 'price', 'sell', 'buy', 'mandi', 'profit'],
            'fertilizer': ['fertilizer', 'manure', 'compost', 'npk'],
            'livestock': ['livestock', 'cattle', 'goat', 'poultry', 'cow', 'buffalo']
        }
        
        found = []
        for concept, keywords in concept_map.items():
            for kw in keywords:
                if kw in query:
                    found.append(concept)
                    break
        
        # Special case: if "crop" is found, also include "weather" if location or season mentioned
        if 'crop' in found and ('weather' not in found):
            weather_keywords = ['assam', 'kharif', 'rabi', 'rain', 'monsoon', 'season']
            for kw in weather_keywords:
                if kw in query:
                    found.append('weather')
                    break
        
        return found if found else ['general']
    
    def explain(self, query: str) -> dict:
        """Explain retrieval decisions."""
        sutra_ids, details = self.retrieve(query)
        params = self.extract_parameters(query)
        return {
            'query': query,
            'concepts': self._extract_concepts(query),
            'parameters': params,
            'retrieved_sutras': details
        }
    
    def get_confidence(self, sutra_id: str) -> float:
        """Get confidence score for a sutra."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(confidence) 
                FROM sutra_concepts 
                WHERE sutra_id = ?
            """, (sutra_id,))
            row = cursor.fetchone()
            return row[0] if row[0] else 0.5
