"""
Sutra 014: Continual Learning System
Non-destructive learning with catastrophic forgetting prevention
"""

import json
import sqlite3
import os
import hashlib
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Learn new knowledge without forgetting old knowledge.
    
    Args:
        inputs: dict with:
            - new_knowledge: what to learn
            - domain: which domain this belongs to
            - importance: importance score (1-10)
    
    Returns:
        dict with learning status
    """
    new_knowledge = inputs.get('new_knowledge', {})
    domain = inputs.get('domain', 'general')
    importance = inputs.get('importance', 5)
    
    if not new_knowledge:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No knowledge to learn"}}
    
    try:
        db_path = os.path.expanduser("~/soca/registry/learning.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT,
                    knowledge TEXT,
                    importance INTEGER,
                    layer INTEGER,
                    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    hash TEXT UNIQUE
                )
            """)
            
            # Create index for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_domain ON knowledge(domain)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_layer ON knowledge(layer)
            """)
            
            # Calculate hash for deduplication
            knowledge_hash = hashlib.md5(
                json.dumps(new_knowledge, sort_keys=True).encode()
            ).hexdigest()
            
            # Check if already learned
            cursor.execute("""
                SELECT id, knowledge, domain, importance, layer
                FROM knowledge
                WHERE hash = ?
            """, (knowledge_hash,))
            existing = cursor.fetchone()
            
            if existing:
                return {
                    "status": "success",
                    "outputs": {
                        "learned": False,
                        "message": "Knowledge already learned",
                        "existing": {
                            "domain": existing[2],
                            "importance": existing[3],
                            "layer": get_layer_name(existing[4])
                        }
                    },
                    "trace": {"sutra_id": "sutra_014", "action": "check_existing"}
                }
            
            # Determine layer based on importance
            if importance >= 8:
                layer = 2  # Pranamaya (Domain)
            elif importance >= 5:
                layer = 3  # Manomaya (Session)
            else:
                layer = 4  # Vijnanamaya (Working)
            
            # Store new knowledge
            cursor.execute("""
                INSERT INTO knowledge (domain, knowledge, importance, layer, hash)
                VALUES (?, ?, ?, ?, ?)
            """, (
                domain,
                json.dumps(new_knowledge),
                importance,
                layer,
                knowledge_hash
            ))
            
            # Consolidate if too many items in a layer
            cursor.execute("""
                SELECT COUNT(*) FROM knowledge WHERE layer = 3
            """)
            count = cursor.fetchone()[0]
            
            if count > 100:
                # Move older less-important items to higher layers
                cursor.execute("""
                    UPDATE knowledge 
                    SET layer = layer + 1
                    WHERE layer = 3 AND importance < 5
                    ORDER BY access_count ASC
                    LIMIT 20
                """)
            
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "learned": True,
                    "layer": get_layer_name(layer),
                    "domain": domain,
                    "importance": importance
                },
                "trace": {
                    "sutra_id": "sutra_014",
                    "action": "learn",
                    "domain": domain,
                    "layer": layer
                }
            }
            
    except Exception as e:
        return {"status": "failure", "outputs": {}, "trace": {"error": str(e)}}

def get_layer_name(layer):
    """Convert layer number to name"""
    layers = {
        1: "Annamaya (Core)",
        2: "Pranamaya (Domain)",
        3: "Manomaya (Session)",
        4: "Vijnanamaya (Working)",
        5: "Anandamaya (Meta)"
    }
    return layers.get(layer, f"Layer {layer}")
