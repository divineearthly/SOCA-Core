#!/usr/bin/env python3
"""
SOCA Cache Cleanup Script
Removes expired cache entries
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta

def cleanup_cache(days=7):
    """Remove cache entries older than days."""
    db_path = os.path.expanduser("~/soca/registry/soca.db")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM query_cache")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📊 No cache entries found")
            return
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            DELETE FROM query_cache
            WHERE created_at < ?
        """, (cutoff,))
        
        deleted = cursor.rowcount
        conn.commit()
        
        print(f"✅ Removed {deleted} expired cache entries")
        
        # Get remaining count
        cursor.execute("SELECT COUNT(*) FROM query_cache")
        remaining = cursor.fetchone()[0]
        print(f"📊 {remaining} entries remaining")

if __name__ == "__main__":
    cleanup_cache()
