"""
sutra_089: Learning Critic
Pramana: Anumana (Inference)
Learns which repairs work and tracks success rates
"""

import sys
import sqlite3
import os
import json
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'record')
    repair_type = inputs.get('repair_type', '')
    success = inputs.get('success', False)
    confidence_delta = inputs.get('confidence_delta', 0)
    
    db_path = os.path.expanduser("~/soca/registry/learning.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repair_type TEXT,
                success BOOLEAN,
                confidence_delta REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        if action == 'record':
            cursor.execute("""
                INSERT INTO repair_history (repair_type, success, confidence_delta)
                VALUES (?, ?, ?)
            """, (repair_type, success, confidence_delta))
            conn.commit()
            
            return success_response(
                outputs={
                    'recorded': True,
                    'repair_type': repair_type,
                    'success': success,
                    'delta': confidence_delta
                },
                confidence=1.0
            )
        
        elif action == 'stats':
            cursor.execute("""
                SELECT repair_type, 
                       COUNT(*) as total,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                       AVG(confidence_delta) as avg_delta
                FROM repair_history
                GROUP BY repair_type
                ORDER BY avg_delta DESC
            """)
            rows = cursor.fetchall()
            
            stats = []
            for row in rows:
                stats.append({
                    'repair_type': row[0],
                    'total': row[1],
                    'successes': row[2],
                    'success_rate': round(row[2] / row[1] * 100, 1) if row[1] > 0 else 0,
                    'avg_delta': round(row[3], 3) if row[3] else 0
                })
            
            return success_response(
                outputs={
                    'stats': stats,
                    'best_repair': stats[0]['repair_type'] if stats else None
                },
                confidence=0.9
            )
    
    return failure_response(f"Unknown action: {action}")
