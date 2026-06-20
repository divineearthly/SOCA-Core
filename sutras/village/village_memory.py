"""
sutra_061: Village Memory
Pramana: Pratyaksha (Direct Perception)
Stores and retrieves village-level knowledge
"""

import sqlite3
import json
import os
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'get')
    village = inputs.get('village', '')
    district = inputs.get('district', '')
    data = inputs.get('data', {})
    
    db_path = os.path.expanduser("~/soca/registry/village.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS villages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                village TEXT,
                district TEXT,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(village, district)
            )
        """)
        
        if action == 'set':
            cursor.execute("""
                INSERT OR REPLACE INTO villages (village, district, data)
                VALUES (?, ?, ?)
            """, (village, district, json.dumps(data)))
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "action": "set",
                    "village": village,
                    "district": district,
                    "data": data
                },
                "trace": {
                    "sutra_id": "sutra_061",
                    "version": "1.0.0"
                }
            }
        
        elif action == 'get':
            cursor.execute("""
                SELECT data FROM villages
                WHERE village = ? AND district = ?
            """, (village, district))
            row = cursor.fetchone()
            
            if row:
                return {
                    "status": "success",
                    "outputs": {
                        "action": "get",
                        "village": village,
                        "district": district,
                        "data": json.loads(row[0])
                    },
                    "trace": {
                        "sutra_id": "sutra_061",
                        "version": "1.0.0"
                    }
                }
            else:
                return {
                    "status": "failure",
                    "outputs": {},
                    "trace": {
                        "sutra_id": "sutra_061",
                        "version": "1.0.0",
                        "error": f"Village '{village}' not found"
                    }
                }
        
        elif action == 'list':
            cursor.execute("""
                SELECT village, district FROM villages
                ORDER BY village
            """)
            rows = cursor.fetchall()
            
            return {
                "status": "success",
                "outputs": {
                    "villages": [
                        {"village": row[0], "district": row[1]}
                        for row in rows
                    ]
                },
                "trace": {
                    "sutra_id": "sutra_061",
                    "version": "1.0.0"
                }
            }
    
    return {
        "status": "failure",
        "outputs": {},
        "trace": {
            "sutra_id": "sutra_061",
            "version": "1.0.0",
            "error": f"Unknown action: {action}"
        }
    }
