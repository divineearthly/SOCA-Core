"""
sutra_097: Result Cache
Pramana: Pratyaksha (Direct Perception)
Caches query results for speed
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime, timedelta

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'get')
    query = inputs.get('query', '')
    result = inputs.get('result', {})
    ttl = inputs.get('ttl', 3600)  # 1 hour
    
    db_path = os.path.expanduser("~/soca/registry/soca.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        if action == 'get':
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cursor.execute("""
                SELECT result, created_at FROM query_cache
                WHERE query_hash = ?
            """, (query_hash,))
            row = cursor.fetchone()
            
            if row:
                result_data = json.loads(row[0])
                created = datetime.fromisoformat(row[1])
                if (datetime.now() - created).total_seconds() < ttl:
                    return {
                        "status": "success",
                        "outputs": {
                            "cached": True,
                            "result": result_data
                        },
                        "trace": {
                            "sutra_id": "sutra_097",
                            "version": "1.0.0"
                        }
                    }
            
            return {
                "status": "success",
                "outputs": {
                    "cached": False
                },
                "trace": {
                    "sutra_id": "sutra_097",
                    "version": "1.0.0"
                }
            }
        
        elif action == 'set':
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cursor.execute("""
                INSERT OR REPLACE INTO query_cache (query_hash, query, result)
                VALUES (?, ?, ?)
            """, (query_hash, query, json.dumps(result)))
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "cached": True,
                    "set": True
                },
                "trace": {
                    "sutra_id": "sutra_097",
                    "version": "1.0.0"
                }
            }
    
    return {
        "status": "failure",
        "outputs": {},
        "trace": {
            "sutra_id": "sutra_097",
            "version": "1.0.0",
            "error": f"Unknown action: {action}"
        }
    }
