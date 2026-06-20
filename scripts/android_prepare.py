#!/usr/bin/env python3
"""
SOCA Android Preparation Script
Prepares the system for Android deployment
"""

import os
import sys
import json
from pathlib import Path

def prepare_android():
    print("📱 SOCA Android Preparation")
    print("=" * 40)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing = []
    
    try:
        import networkx
        print("✅ networkx")
    except:
        missing.append("networkx")
    
    try:
        import sqlite3
        print("✅ sqlite3")
    except:
        missing.append("sqlite3")
    
    if missing:
        print(f"\n❌ Missing dependencies: {missing}")
        print("Install with: pip install " + " ".join(missing))
    
    # Check database
    db_path = os.path.expanduser("~/soca/registry/soca.db")
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / 1024 / 1024
        print(f"\n📊 Database size: {size:.2f} MB")
        
        # Check tables
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📊 Tables: {', '.join(tables)}")
    
    # Check JSON files
    json_files = list(Path("sutras").glob("*.json"))
    print(f"\n📄 Sutra definitions: {len(json_files)}")
    
    # Create Android package structure
    android_dir = Path("android")
    android_dir.mkdir(exist_ok=True)
    
    # Check for soca_agent script
    if os.path.exists("soca_agent"):
        print("✅ soca_agent script found")
    
    print("\n📱 Android preparation complete!")
    print(f"   Database: {db_path}")
    print(f"   Sutras: {len(json_files)}")
    print(f"   Ready for packaging")

if __name__ == "__main__":
    prepare_android()
