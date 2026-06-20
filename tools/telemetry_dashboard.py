#!/usr/bin/env python3
"""
SOCA Telemetry Dashboard
Generates human-readable reports from telemetry
"""

import sys
import os
import sqlite3
import json
from datetime import datetime

def generate_dashboard():
    """Generate telemetry dashboard report."""
    sys.path.append('runtime')
    from registry_manager import RegistryManager
    
    rm = RegistryManager()
    db_path = rm.db_path
    
    print("=" * 60)
    print("🕉️ SOCA TELEMETRY DASHBOARD")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check if telemetry exists
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='telemetry'
        """)
        if not cursor.fetchone():
            print("\n❌ No telemetry data found. Run some queries first.")
            return
        
        # Overall stats
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
        
        print("\n📊 OVERALL STATISTICS")
        print("-" * 40)
        print(f"  Total Queries:        {row[0] or 0}")
        print(f"  Average Confidence:   {row[1] or 0:.3f}")
        print(f"  Average Iterations:   {row[2] or 0:.1f}")
        print(f"  Average Time (ms):    {row[3] or 0:.1f}")
        print(f"  Clarifications:       {row[4] or 0}")
        print(f"  Unique Intents:       {row[5] or 0}")
        
        # By intent
        cursor.execute("""
            SELECT 
                intent,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence,
                AVG(iterations) as avg_iterations
            FROM telemetry
            GROUP BY intent
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        
        print("\n📊 BY INTENT")
        print("-" * 40)
        for r in rows[:10]:
            intent = r[0] or 'unknown'
            print(f"  {intent:15} | {r[1]:4} queries | conf: {r[2]:.3f} | avg iter: {r[3]:.1f}")
        
        # Retrieval strategy
        cursor.execute("""
            SELECT 
                retrieval_strategy,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence
            FROM telemetry
            WHERE retrieval_strategy IS NOT NULL
            GROUP BY retrieval_strategy
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        
        print("\n📊 RETRIEVAL STRATEGIES")
        print("-" * 40)
        for r in rows:
            print(f"  {r[0]:10} | {r[1]:4} queries | avg conf: {r[2]:.3f}")
        
        # Recent queries
        cursor.execute("""
            SELECT query, intent, confidence, timestamp
            FROM telemetry
            ORDER BY timestamp DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        
        print("\n📊 RECENT QUERIES")
        print("-" * 40)
        for r in rows:
            print(f"  {r[0][:40]:40} | {r[1]:12} | {r[2]:.3f}")
        
        # Repair stats (if available)
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
        
        if rows:
            print("\n📊 REPAIR EFFECTIVENESS")
            print("-" * 40)
            for r in rows[:5]:
                print(f"  {r[0]:15} | success: {r[2]}/{r[1]} ({r[2]/r[1]*100:.1f}%) | avg delta: {r[3]:+.3f}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    generate_dashboard()
