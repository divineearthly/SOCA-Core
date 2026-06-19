"""
sutra_036: Knowledge Contributor
Allows users to add knowledge to the system
"""

import json
import sqlite3
import os
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    domain = inputs.get('domain', '')
    data = inputs.get('data', {})
    contributor = inputs.get('contributor', 'anonymous')
    location = inputs.get('location', '')
    
    if not domain or not data:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_036",
                "version": "1.0.0",
                "error": "Domain and data required"
            }
        }
    
    # Store contribution
    db_path = os.path.expanduser("~/soca/registry/community.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT,
                data TEXT,
                contributor TEXT,
                location TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            INSERT INTO contributions (domain, data, contributor, location)
            VALUES (?, ?, ?, ?)
        """, (domain, json.dumps(data), contributor, location))
        conn.commit()
    
    return {
        "status": "success",
        "outputs": {
            "submitted": True,
            "domain": domain,
            "contributor": contributor,
            "status": "pending_review"
        },
        "trace": {
            "sutra_id": "sutra_036",
            "version": "1.0.0"
        }
    }
