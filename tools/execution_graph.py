#!/usr/bin/env python3
"""
SOCA Execution Graph Generator
Generates dependency graph from actual execution traces
"""

import os
import sys
import sqlite3
import json
from collections import defaultdict

def generate_execution_graph():
    """Generate graph from trace logs."""
    sys.path.append('runtime')
    from registry_manager import RegistryManager
    
    rm = RegistryManager()
    
    # Get all traces
    with sqlite3.connect(rm.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT executed_sutras, status, trace_id
            FROM trace_log
            ORDER BY created_at DESC
            LIMIT 50
        """)
        rows = cursor.fetchall()
    
    edges = defaultdict(int)
    nodes = set()
    
    for row in rows:
        executed_sutras = json.loads(row[0])
        status = row[1]
        
        for i, sutra in enumerate(executed_sutras):
            sutra_id = sutra.get('id', '')
            if sutra_id:
                nodes.add(sutra_id)
                if i > 0:
                    prev = executed_sutras[i-1].get('id', '')
                    if prev and prev != sutra_id:
                        edges[(prev, sutra_id)] += 1
    
    graph = {
        'nodes': list(nodes),
        'edges': [{'source': src, 'target': dst, 'weight': w} for (src, dst), w in edges.items()]
    }
    
    with open('execution_graph.json', 'w') as f:
        json.dump(graph, f, indent=2)
    
    print(f"✅ Execution graph generated: {len(nodes)} nodes, {len(edges)} edges")

if __name__ == "__main__":
    generate_execution_graph()
