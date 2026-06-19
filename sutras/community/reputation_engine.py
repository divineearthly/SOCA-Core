"""
sutra_040: Reputation Engine
Pramana: Anumana (Inference)
Tracks contributor reputation
"""

import sqlite3
import os

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'get')
    contributor = inputs.get('contributor', '')
    
    db_path = os.path.expanduser("~/soca/registry/community.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create reputation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reputation (
                contributor TEXT PRIMARY KEY,
                contributions INTEGER DEFAULT 0,
                approved INTEGER DEFAULT 0,
                rejected INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0.0,
                reputation INTEGER DEFAULT 50,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        if action == 'get':
            cursor.execute("""
                SELECT contributor, contributions, approved, rejected, accuracy, reputation
                FROM reputation
                WHERE contributor = ?
            """, (contributor,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "status": "success",
                    "outputs": {
                        "contributor": row[0],
                        "contributions": row[1],
                        "approved": row[2],
                        "rejected": row[3],
                        "accuracy": row[4],
                        "reputation": row[5]
                    },
                    "trace": {
                        "sutra_id": "sutra_040",
                        "version": "1.0.0"
                    }
                }
            else:
                return {
                    "status": "success",
                    "outputs": {
                        "contributor": contributor,
                        "contributions": 0,
                        "approved": 0,
                        "rejected": 0,
                        "accuracy": 0.0,
                        "reputation": 50
                    },
                    "trace": {
                        "sutra_id": "sutra_040",
                        "version": "1.0.0"
                    }
                }
        
        elif action == 'update':
            # Implementation for updating reputation
            pass
        
        elif action == 'top':
            cursor.execute("""
                SELECT contributor, contributions, approved, accuracy, reputation
                FROM reputation
                ORDER BY reputation DESC
                LIMIT 10
            """)
            rows = cursor.fetchall()
            
            return {
                "status": "success",
                "outputs": {
                    "top_contributors": [
                        {
                            "contributor": r[0],
                            "contributions": r[1],
                            "approved": r[2],
                            "accuracy": r[3],
                            "reputation": r[4]
                        }
                        for r in rows
                    ]
                },
                "trace": {
                    "sutra_id": "sutra_040",
                    "version": "1.0.0"
                }
            }
        
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_040",
                "version": "1.0.0",
                "error": "Unknown action"
            }
        }
