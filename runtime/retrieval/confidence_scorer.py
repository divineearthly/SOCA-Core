"""
Confidence Scorer for Sutra Retrieval
"""

import sqlite3
import math

class ConfidenceScorer:
    def __init__(self, db_path: str = "registry/soca.db"):
        self.db_path = db_path
    
    def score_sutra(self, sutra_id: str, concept_matches: list) -> float:
        """Calculate confidence score for a sutra based on concept matches."""
        base_score = 0.5
        
        # Get sutra's pramana confidence
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pramana_confidence, usage_count, success_count
                FROM sutra_registry
                WHERE sutra_id = ?
            """, (sutra_id,))
            row = cursor.fetchone()
            if row:
                pramana_conf = row[0] or 0.5
                usage = row[1] or 0
                success = row[2] or 0
                usage_boost = min(0.1, usage * 0.01) if usage > 0 else 0
                success_rate = success / usage if usage > 0 else 0
                success_boost = min(0.1, success_rate * 0.1)
                base_score = pramana_conf + usage_boost + success_boost
        
        # Boost based on concept matches
        concept_boost = min(0.3, len(concept_matches) * 0.05)
        final_score = min(1.0, base_score + concept_boost)
        
        return round(final_score, 2)
    
    def explain_score(self, sutra_id: str, concept_matches: list) -> dict:
        """Explain how confidence was calculated."""
        score = self.score_sutra(sutra_id, concept_matches)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pramana, pramana_confidence, usage_count, success_count
                FROM sutra_registry
                WHERE sutra_id = ?
            """, (sutra_id,))
            row = cursor.fetchone()
        
        return {
            'sutra_id': sutra_id,
            'score': score,
            'pramana': row[0] if row else 'unknown',
            'pramana_confidence': row[1] if row else 0.5,
            'usage_count': row[2] if row else 0,
            'success_count': row[3] if row else 0,
            'concept_matches': concept_matches,
            'factors': {
                'pramana_boost': row[1] if row else 0.5,
                'usage_boost': min(0.1, (row[2] or 0) * 0.01) if row else 0,
                'concept_boost': min(0.3, len(concept_matches) * 0.05)
            }
        }
