"""
sutra_090: Agent Telemetry
Pramana: Pratyaksha (Direct Perception)
Records runtime metrics for every query
"""

import sys
import sqlite3
import os
import json
from datetime import datetime
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'record')
    
    db_path = os.path.expanduser("~/soca/registry/soca.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                intent TEXT,
                confidence REAL,
                iterations INTEGER,
                retrieval_strategy TEXT,
                clarification_needed BOOLEAN,
                execution_time_ms REAL,
                weaknesses TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        if action == 'record':
            query = inputs.get('query', '')
            intent = inputs.get('intent', 'general')
            confidence = inputs.get('confidence', 0.0)
            iterations = inputs.get('iterations', 0)
            retrieval_strategy = inputs.get('retrieval_strategy', 'bm25')
            clarification_needed = inputs.get('clarification_needed', False)
            execution_time_ms = inputs.get('execution_time_ms', 0)
            weaknesses = json.dumps(inputs.get('weaknesses', []))
            
            cursor.execute("""
                INSERT INTO telemetry (
                    query, intent, confidence, iterations, 
                    retrieval_strategy, clarification_needed, 
                    execution_time_ms, weaknesses
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (query, intent, confidence, iterations, 
                  retrieval_strategy, clarification_needed, 
                  execution_time_ms, weaknesses))
            conn.commit()
            
            return success_response(
                outputs={
                    'recorded': True,
                    'id': cursor.lastrowid
                },
                confidence=1.0
            )
        
        elif action == 'stats':
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(confidence) as avg_confidence,
                    AVG(iterations) as avg_iterations,
                    AVG(execution_time_ms) as avg_time_ms,
                    SUM(CASE WHEN clarification_needed THEN 1 ELSE 0 END) as clarifications,
                    COUNT(DISTINCT intent) as unique_intents
                FROM telemetry
            """)
            row = cursor.fetchone()
            
            return success_response(
                outputs={
                    'total_queries': row[0] or 0,
                    'avg_confidence': round(row[1] or 0, 3),
                    'avg_iterations': round(row[2] or 0, 1),
                    'avg_time_ms': round(row[3] or 0, 1),
                    'clarifications': row[4] or 0,
                    'clarification_rate': round((row[4] or 0) / (row[0] or 1), 3),
                    'unique_intents': row[5] or 0
                },
                confidence=0.9
            )
    
    return failure_response(f"Unknown action: {action}")
