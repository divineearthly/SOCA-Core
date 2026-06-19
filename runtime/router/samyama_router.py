"""
Samyama Router: Three-Stage Retrieval
Based on Patanjali's Yoga Sutras 3.4
- Dharana (Concentration): Exact match
- Dhyana (Meditation): Semantic similarity
- Samadhi (Absorption): Combined ranking
"""

import sqlite3
import os
import re
from difflib import SequenceMatcher

class SamyamaRouter:
    def __init__(self, db_path: str = "registry/soca.db"):
        self.db_path = db_path
    
    def route(self, query: str, top_k: int = 5) -> list:
        """
        Three-stage retrieval:
        1. Dharana - Exact matches
        2. Dhyana - Semantic/pattern matches
        3. Samadhi - Combined ranking with Pramana weights
        """
        results = []
        
        # Stage 1: Dharana (Concentration) - Exact matches
        dharana_results = self._dharana(query)
        results.extend(dharana_results)
        
        # Stage 2: Dhyana (Meditation) - Semantic matches
        dhyana_results = self._dhyana(query)
        results.extend(dhyana_results)
        
        # Stage 3: Samadhi (Absorption) - Combined ranking
        samadhi_results = self._samadhi(query, results, top_k)
        
        return samadhi_results
    
    def _dharana(self, query: str) -> list:
        """Stage 1: Exact match concentration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Exact matches in name or category
            cursor.execute("""
                SELECT sutra_id, name, category, pramana, pramana_confidence
                FROM sutra_registry
                WHERE is_active = TRUE
                AND (name LIKE ? OR category LIKE ?)
                ORDER BY pramana_confidence DESC
                LIMIT 10
            """, (f'%{query}%', f'%{query}%'))
            
            rows = cursor.fetchall()
            
            return [{
                'sutra_id': row[0],
                'name': row[1],
                'category': row[2],
                'pramana': row[3],
                'confidence': row[4],
                'stage': 'dharana',
                'score': 1.0
            } for row in rows]
    
    def _dhyana(self, query: str) -> list:
        """Stage 2: Semantic/pattern matching."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all active sutras
            cursor.execute("""
                SELECT sutra_id, name, category, pramana, pramana_confidence
                FROM sutra_registry
                WHERE is_active = TRUE
            """)
            
            rows = cursor.fetchall()
            
            results = []
            query_lower = query.lower()
            
            for row in rows:
                name_lower = row[1].lower()
                category_lower = row[2].lower()
                
                # Word overlap
                query_words = set(query_lower.split())
                name_words = set(name_lower.split())
                
                overlap = len(query_words.intersection(name_words))
                if overlap > 0:
                    score = overlap / max(len(query_words), 1)
                    results.append({
                        'sutra_id': row[0],
                        'name': row[1],
                        'category': row[2],
                        'pramana': row[3],
                        'confidence': row[4],
                        'stage': 'dhyana',
                        'score': score
                    })
            
            return results
    
    def _samadhi(self, query: str, candidates: list, top_k: int) -> list:
        """Stage 3: Combined ranking with Pramana weights."""
        # Deduplicate by sutra_id
        seen = {}
        for item in candidates:
            sutra_id = item['sutra_id']
            if sutra_id not in seen or item['score'] > seen[sutra_id]['score']:
                seen[sutra_id] = item
        
        # Calculate final score: confidence * stage_weight * score
        stage_weights = {
            'dharana': 1.0,
            'dhyana': 0.8
        }
        
        final_results = []
        for item in seen.values():
            stage_weight = stage_weights.get(item['stage'], 0.5)
            final_score = item['confidence'] * stage_weight * item['score']
            final_results.append({
                **item,
                'final_score': final_score
            })
        
        # Sort by final score and return top_k
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        return final_results[:top_k]
    
    def explain(self, query: str) -> dict:
        """Explain the routing decision."""
        results = self.route(query)
        
        return {
            'query': query,
            'results': results,
            'summary': {
                'total_matches': len(results),
                'top_match': results[0]['name'] if results else None,
                'top_confidence': results[0]['confidence'] if results else None,
                'stages': {
                    'dharana': len([r for r in results if r['stage'] == 'dharana']),
                    'dhyana': len([r for r in results if r['stage'] == 'dhyana'])
                }
            }
        }
