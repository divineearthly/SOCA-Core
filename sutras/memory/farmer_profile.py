"""
sutra_054: Farmer Profile
Pramana: Pratyaksha (Direct Perception)
Manages farmer profiles for personalized advice
"""

import sqlite3
import json
import os
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'get')
    farmer_id = inputs.get('farmer_id', 'anonymous')
    
    db_path = os.path.expanduser("~/soca/registry/farmers.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmer_profiles (
                farmer_id TEXT PRIMARY KEY,
                name TEXT,
                district TEXT,
                village TEXT,
                soil_type TEXT,
                land_size REAL,
                crop_history TEXT,
                preferences TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        if action == 'set':
            name = inputs.get('name', '')
            district = inputs.get('district', '')
            village = inputs.get('village', '')
            soil_type = inputs.get('soil_type', '')
            land_size = inputs.get('land_size', 0)
            crop_history = json.dumps(inputs.get('crop_history', []))
            preferences = json.dumps(inputs.get('preferences', {}))
            
            cursor.execute("""
                INSERT OR REPLACE INTO farmer_profiles
                (farmer_id, name, district, village, soil_type, land_size, crop_history, preferences)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (farmer_id, name, district, village, soil_type, land_size, crop_history, preferences))
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "action": "set",
                    "farmer_id": farmer_id,
                    "name": name,
                    "district": district,
                    "soil_type": soil_type
                },
                "trace": {
                    "sutra_id": "sutra_054",
                    "version": "1.0.0"
                }
            }
        
        elif action == 'get':
            cursor.execute("""
                SELECT name, district, village, soil_type, land_size, crop_history, preferences
                FROM farmer_profiles
                WHERE farmer_id = ?
            """, (farmer_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "status": "success",
                    "outputs": {
                        "action": "get",
                        "farmer_id": farmer_id,
                        "name": row[0],
                        "district": row[1],
                        "village": row[2],
                        "soil_type": row[3],
                        "land_size": row[4],
                        "crop_history": json.loads(row[5]) if row[5] else [],
                        "preferences": json.loads(row[6]) if row[6] else {}
                    },
                    "trace": {
                        "sutra_id": "sutra_054",
                        "version": "1.0.0"
                    }
                }
            else:
                return {
                    "status": "failure",
                    "outputs": {},
                    "trace": {
                        "sutra_id": "sutra_054",
                        "version": "1.0.0",
                        "error": f"Farmer '{farmer_id}' not found"
                    }
                }
    
    return {
        "status": "failure",
        "outputs": {},
        "trace": {
            "sutra_id": "sutra_054",
            "version": "1.0.0",
            "error": f"Unknown action: {action}"
        }
    }
