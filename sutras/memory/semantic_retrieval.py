"""
sutra_055: Semantic Retrieval
Pramana: Anumana (Inference)
Improved vector-based retrieval with better scoring
"""

import sqlite3
import json
import os
import re

def simple_embed(text):
    """Simple embedding based on word frequency."""
    words = re.findall(r'[a-zA-Z]+', text.lower())
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
    query = inputs.get('query', '')
    top_k = inputs.get('top_k', 10)
    
    if not query:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_055",
                "version": "1.0.0",
                "error": "Query required"
            }
        }
    
    db_path = os.path.expanduser("~/soca/registry/vector.db")
    
    if not os.path.exists(db_path):
        return {
            "status": "success",
            "outputs": {
                "query": query,
                "results": [],
                "count": 0
            },
            "trace": {
                "sutra_id": "sutra_055",
                "version": "1.0.0"
            }
        }
    
    query_embedding = simple_embed(query)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, text, embedding, metadata
            FROM vectors
            ORDER BY created_at DESC
            LIMIT 500
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
                    'metadata': json.loads(row[3]) if row[3] else {},
                    'similarity': round(similarity, 3)
                })
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            "status": "success",
            "outputs": {
                "query": query,
                "results": results[:top_k],
                "count": len(results)
            },
            "trace": {
                "sutra_id": "sutra_055",
                "version": "1.0.0"
            }
        }
