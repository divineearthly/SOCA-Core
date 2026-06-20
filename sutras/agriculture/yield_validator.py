"""
sutra_059: Yield Validator
Pramana: Pratyaksha (Direct Perception)
Validates yield predictions against actual data
"""

import sqlite3
import json
import os
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'record')
    district = inputs.get('district', '')
    crop = inputs.get('crop', '')
    predicted = inputs.get('predicted', 0)
    actual = inputs.get('actual', 0)
    
    db_path = os.path.expanduser("~/soca/registry/yield_data.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS yield_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT,
                crop TEXT,
                predicted REAL,
                actual REAL,
                error REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        if action == 'record':
            if not district or not crop or predicted == 0:
                return {
                    "status": "failure",
                    "outputs": {},
                    "trace": {
                        "sutra_id": "sutra_059",
                        "version": "1.0.0",
                        "error": "District, crop, and predicted required"
                    }
                }
            
            error = predicted - actual if actual > 0 else 0
            error_pct = (error / predicted * 100) if predicted > 0 else 0
            
            cursor.execute("""
                INSERT INTO yield_records (district, crop, predicted, actual, error)
                VALUES (?, ?, ?, ?, ?)
            """, (district, crop, predicted, actual, error_pct))
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "action": "record",
                    "district": district,
                    "crop": crop,
                    "predicted": predicted,
                    "actual": actual,
                    "error_percent": round(error_pct, 1)
                },
                "trace": {
                    "sutra_id": "sutra_059",
                    "version": "1.0.0"
                }
            }
        
        elif action == 'stats':
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(error) as avg_error,
                    MIN(error) as min_error,
                    MAX(error) as max_error
                FROM yield_records
            """)
            row = cursor.fetchone()
            
            return {
                "status": "success",
                "outputs": {
                    "total_records": row[0],
                    "avg_error": round(row[1], 1) if row[1] else 0,
                    "min_error": round(row[2], 1) if row[2] else 0,
                    "max_error": round(row[3], 1) if row[3] else 0
                },
                "trace": {
                    "sutra_id": "sutra_059",
                    "version": "1.0.0"
                }
            }
        
        elif action == 'by_district':
            cursor.execute("""
                SELECT district, COUNT(*) as count, AVG(error) as avg_error
                FROM yield_records
                GROUP BY district
                ORDER BY avg_error
            """)
            rows = cursor.fetchall()
            
            return {
                "status": "success",
                "outputs": {
                    "districts": [
                        {
                            "district": row[0],
                            "count": row[1],
                            "avg_error": round(row[2], 1) if row[2] else 0
                        }
                        for row in rows
                    ]
                },
                "trace": {
                    "sutra_id": "sutra_059",
                    "version": "1.0.0"
                }
            }
    
    return {
        "status": "failure",
        "outputs": {},
        "trace": {
            "sutra_id": "sutra_059",
            "version": "1.0.0",
            "error": f"Unknown action: {action}"
        }
    }
