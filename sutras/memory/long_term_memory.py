"""
sutra_048: Long-Term Memory
Pramana: Pratyaksha (Direct Perception)
Remembers user preferences and history
"""

import sqlite3
import json
import os
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'get')
    user_id = inputs.get('user_id', 'anonymous')
    key = inputs.get('key', '')
    value = inputs.get('value', '')
    
    db_path = os.path.expanduser("~/soca/registry/memory.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                user_id TEXT,
                key TEXT,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, key)
            )
        """)
        
        if action == 'set':
            cursor.execute("""
                INSERT OR REPLACE INTO long_term_memory (user_id, key, value)
                VALUES (?, ?, ?)
            """, (user_id, key, value))
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "action": "set",
                    "user_id": user_id,
                    "key": key,
                    "value": value
                },
                "trace": {
                    "sutra_id": "sutra_048",
                    "version": "1.0.0"
                }
            }
        
        elif action == 'get':
            cursor.execute("""
                SELECT value FROM long_term_memory
                WHERE user_id = ? AND key = ?
            """, (user_id, key))
            row = cursor.fetchone()
            
            if row:
                return {
                    "status": "success",
                    "outputs": {
                        "action": "get",
                        "user_id": user_id,
                        "key": key,
                        "value": row[0]
                    },
                    "trace": {
                        "sutra_id": "sutra_048",
                        "version": "1.0.0"
                    }
                }
            else:
                return {
                    "status": "failure",
                    "outputs": {},
                    "trace": {
                        "sutra_id": "sutra_048",
                        "version": "1.0.0",
                        "error": f"Key '{key}' not found for user '{user_id}'"
                    }
                }
        
        elif action == 'get_all':
            cursor.execute("""
                SELECT key, value FROM long_term_memory
                WHERE user_id = ?
            """, (user_id,))
            rows = cursor.fetchall()
            
            memory = {row[0]: row[1] for row in rows}
            
            return {
                "status": "success",
                "outputs": {
                    "action": "get_all",
                    "user_id": user_id,
                    "memory": memory,
                    "count": len(memory)
                },
                "trace": {
                    "sutra_id": "sutra_048",
                    "version": "1.0.0"
                }
            }
    
    return {
        "status": "failure",
        "outputs": {},
        "trace": {
            "sutra_id": "sutra_048",
            "version": "1.0.0",
            "error": f"Unknown action: {action}"
        }
    }
