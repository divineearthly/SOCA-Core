"""
sutra_047: Vector Memory
Pramana: Pratyaksha (Direct Perception)
Semantic search using embeddings
"""

import sqlite3
import json
import os
import hashlib
from datetime import datetime

# Simple embedding function (TF-IDF-like for MVP)
def simple_embed(text):
    """Simple embedding based on word frequency."""
    words = text.lower().split()
    vector = {}
    for word in words:
        vector[word] = vector.get(word, 0) + 1
    return vector

def cosine_similarity(vec1, vec2):
    """Cosine similarity between two sparse vectors."""
    if not vec1 or not vec2:
        return 0
    common = set(vec1.keys()) & set(vec2.keys())
    if not common:
        return 0
    dot = sum(vec1[w] * vec2[w] for w in common)
    norm1 = sum(v ** 2 for v in vec1.values()) ** 0.5
    norm2 = sum(v ** 2 for v in vec2.values()) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'search')
    query = inputs.get('query', '')
    text = inputs.get('text', '')
    metadata = inputs.get('metadata', {})
    
    db_path = os.path.expanduser("~/soca/registry/vector.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    if action == 'store':
        if not text:
            return {"status": "failure", "outputs": {}, "trace": {"error": "Text required for storage"}}
        
        # Generate embedding
        embedding = simple_embed(text)
        embedding_json = json.dumps(embedding)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT,
                    embedding TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                INSERT INTO vectors (text, embedding, metadata)
                VALUES (?, ?, ?)
            """, (text, embedding_json, json.dumps(metadata)))
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "stored": True,
                    "id": cursor.lastrowid
                },
                "trace": {
                    "sutra_id": "sutra_047",
                    "version": "1.0.0"
                }
            }
    
    elif action == 'search':
        if not query:
            return {"status": "failure", "outputs": {}, "trace": {"error": "Query required for search"}}
        
        query_embedding = simple_embed(query)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, text, embedding, metadata
                FROM vectors
                ORDER BY created_at DESC
                LIMIT 100
            """)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                stored_embedding = json.loads(row[2])
                similarity = cosine_similarity(query_embedding, stored_embedding)
                if similarity > 0.1:
                    results.append({
                        'id': row[0],
                        'text': row[1],
                        'metadata': json.loads(row[3]),
                        'similarity': round(similarity, 3)
                    })
            
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                "status": "success",
                "outputs": {
                    "query": query,
                    "results": results[:10],
                    "count": len(results)
                },
                "trace": {
                    "sutra_id": "sutra_047",
                    "version": "1.0.0"
                }
            }
    
    return {
        "status": "failure",
        "outputs": {},
        "trace": {
            "sutra_id": "sutra_047",
            "version": "1.0.0",
            "error": f"Unknown action: {action}"
        }
    }
