"""
sutra_091: Dashboard Analytics
Pramana: Anumana (Inference)
Aggregates telemetry for insights
"""

import sys
import sqlite3
import os
import json
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'summary')
    
    db_path = os.path.expanduser("~/soca/registry/soca.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        if action == 'summary':
            return get_summary(cursor)
        
        elif action == 'by_intent':
            return get_by_intent(cursor)
        
        elif action == 'retrieval_stats':
            return get_retrieval_stats(cursor)
        
        elif action == 'repair_stats':
            return get_repair_stats(cursor)
    
    return failure_response(f"Unknown action: {action}")

def get_summary(cursor):
    """Get overall summary statistics."""
    cursor.execute("""
        SELECT 
            COUNT(*) as total_queries,
            AVG(confidence) as avg_confidence,
            AVG(iterations) as avg_iterations,
            AVG(execution_time_ms) as avg_time_ms,
            COUNT(DISTINCT intent) as unique_intents
        FROM telemetry
    """)
    row = cursor.fetchone()
    
    # Get recent queries
    cursor.execute("""
        SELECT query, intent, confidence, timestamp
        FROM telemetry
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    recent = cursor.fetchall()
    
    return success_response(
        outputs={
            'summary': {
                'total_queries': row[0] or 0,
                'avg_confidence': round(row[1] or 0, 3),
                'avg_iterations': round(row[2] or 0, 1),
                'avg_time_ms': round(row[3] or 0, 1),
                'unique_intents': row[4] or 0
            },
            'recent_queries': [
                {
                    'query': r[0][:50],
                    'intent': r[1],
                    'confidence': r[2],
                    'timestamp': r[3]
                }
                for r in recent
            ]
        },
        confidence=0.9
    )

def get_by_intent(cursor):
    """Get statistics by intent."""
    cursor.execute("""
        SELECT 
            intent,
            COUNT(*) as count,
            AVG(confidence) as avg_confidence,
            AVG(iterations) as avg_iterations,
            AVG(execution_time_ms) as avg_time_ms
        FROM telemetry
        GROUP BY intent
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    
    return success_response(
        outputs={
            'by_intent': [
                {
                    'intent': r[0] or 'unknown',
                    'count': r[1],
                    'avg_confidence': round(r[2] or 0, 3),
                    'avg_iterations': round(r[3] or 0, 1),
                    'avg_time_ms': round(r[4] or 0, 1)
                }
                for r in rows
            ]
        },
        confidence=0.9
    )

def get_retrieval_stats(cursor):
    """Get statistics by retrieval strategy."""
    cursor.execute("""
        SELECT 
            retrieval_strategy,
            COUNT(*) as count,
            AVG(confidence) as avg_confidence,
            AVG(iterations) as avg_iterations
        FROM telemetry
        WHERE retrieval_strategy IS NOT NULL
        GROUP BY retrieval_strategy
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    
    return success_response(
        outputs={
            'retrieval_stats': [
                {
                    'strategy': r[0] or 'unknown',
                    'count': r[1],
                    'avg_confidence': round(r[2] or 0, 3),
                    'avg_iterations': round(r[3] or 0, 1)
                }
                for r in rows
            ]
        },
        confidence=0.9
    )

def get_repair_stats(cursor):
    """Get repair effectiveness statistics."""
    cursor.execute("""
        SELECT 
            repair_type,
            COUNT(*) as total,
            SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
            AVG(confidence_delta) as avg_delta
        FROM repair_history
        GROUP BY repair_type
        ORDER BY avg_delta DESC
    """)
    rows = cursor.fetchall()
    
    return success_response(
        outputs={
            'repair_stats': [
                {
                    'repair_type': r[0] or 'unknown',
                    'total': r[1],
                    'successes': r[2],
                    'success_rate': round(r[2] / r[1] * 100, 1) if r[1] > 0 else 0,
                    'avg_delta': round(r[3] or 0, 3)
                }
                for r in rows
            ]
        },
        confidence=0.9
    )
