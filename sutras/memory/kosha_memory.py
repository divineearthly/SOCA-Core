"""
Sutra 013: Kosha-Net Memory System
Implements 5-layer memory with non-destructive learning
"""

import json
import sqlite3
import os
from datetime import datetime

# Memory layers (Koshas)
KOSHA_LAYERS = {
    'annamaya': 1,      # Core - permanent
    'pranamaya': 2,     # Domain - long-term
    'manomaya': 3,      # Session - medium-term
    'vijnanamaya': 4,   # Working - short-term
    'anandamaya': 5     # Meta - immutable
}

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Store and retrieve knowledge with layered memory.
    
    Args:
        inputs: dict with:
            - action: 'store' or 'retrieve'
            - key: memory key
            - value: memory value (for store)
            - layer: which kosha to use
            - ttl: time-to-live in seconds
    
    Returns:
        dict with status and memory data
    """
    action = inputs.get('action', 'retrieve')
    key = inputs.get('key')
    value = inputs.get('value')
    layer = inputs.get('layer', 'manomaya')
    ttl = inputs.get('ttl', 3600)  # 1 hour default
    
    if not key:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No key provided"}}
    
    # Get layer priority
    layer_priority = KOSHA_LAYERS.get(layer, 3)
    
    db_path = os.path.expanduser("~/soca/registry/memory.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    if action == 'store':
        return store_memory(db_path, key, value, layer_priority, ttl)
    else:
        return retrieve_memory(db_path, key, layer_priority)

def store_memory(db_path, key, value, layer_priority, ttl):
    """Store a memory with TTL and layer information"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    layer INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # Calculate expiration
            expires_at = datetime.now().timestamp() + ttl
            
            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO memory (key, value, layer, expires_at, access_count)
                VALUES (?, ?, ?, ?, 0)
            """, (key, json.dumps(value), layer_priority, expires_at))
            
            conn.commit()
            
            return {
                "status": "success",
                "outputs": {
                    "stored": True,
                    "key": key,
                    "layer": get_layer_name(layer_priority)
                },
                "trace": {"sutra_id": "sutra_013", "action": "store"}
            }
    except Exception as e:
        return {"status": "failure", "outputs": {}, "trace": {"error": str(e)}}

def retrieve_memory(db_path, key, max_layer):
    """Retrieve a memory, checking layers from highest priority"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    layer INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # Search from highest layer (1) to max_layer
            current_time = datetime.now().timestamp()
            
            cursor.execute("""
                SELECT value, layer 
                FROM memory 
                WHERE key = ? AND layer <= ? AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY layer DESC
                LIMIT 1
            """, (key, max_layer, current_time))
            
            result = cursor.fetchone()
            
            if result:
                # Increment access count
                cursor.execute("""
                    UPDATE memory SET access_count = access_count + 1
                    WHERE key = ?
                """, (key,))
                conn.commit()
                
                return {
                    "status": "success",
                    "outputs": {
                        "found": True,
                        "value": json.loads(result[0]),
                        "layer": get_layer_name(result[1])
                    },
                    "trace": {"sutra_id": "sutra_013", "action": "retrieve"}
                }
            else:
                return {
                    "status": "success",
                    "outputs": {
                        "found": False,
                        "value": None
                    },
                    "trace": {"sutra_id": "sutra_013", "action": "retrieve"}
                }
    except Exception as e:
        return {"status": "failure", "outputs": {}, "trace": {"error": str(e)}}

def get_layer_name(priority):
    """Convert layer priority to name"""
    reverse_layers = {v: k for k, v in KOSHA_LAYERS.items()}
    return reverse_layers.get(priority, 'unknown')
