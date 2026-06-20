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
    
    # Check if trace_log exists
    with sqlite3.connect(rm.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='trace_log'
        """)
        if not cursor.fetchone():
            print("❌ No trace_log table found")
            return
    
    # Get all traces
    with sqlite3.connect(rm.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trace_id, executed_sutras, status
            FROM trace_log
            ORDER BY created_at DESC
            LIMIT 50
        """)
        rows = cursor.fetchall()
    
    if not rows:
        print("❌ No traces found. Run some queries first.")
        return
    
    edges = defaultdict(int)
    nodes = set()
    total_traces = len(rows)
    traces_with_edges = 0
    
    for row in rows:
        trace_id = row[0]
        executed_sutras = row[1]
        status = row[2]
        
        try:
            data = json.loads(executed_sutras)
        except:
            print(f"⚠️ Failed to parse trace {trace_id}")
            continue
        
        # Handle different formats
        sutra_ids = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    sutra_id = item.get('id', '')
                    if sutra_id:
                        sutra_ids.append(sutra_id)
                elif isinstance(item, str):
                    sutra_ids.append(item)
        elif isinstance(data, dict):
            # Maybe it's a dict with 'executed_sutras' key
            sutra_ids = data.get('executed_sutras', [])
        else:
            print(f"⚠️ Unknown format in trace {trace_id}: {type(data)}")
            continue
        
        # Build edges
        if len(sutra_ids) > 1:
            traces_with_edges += 1
            for i, sutra_id in enumerate(sutra_ids):
                if sutra_id:
                    nodes.add(sutra_id)
                    if i > 0:
                        prev = sutra_ids[i-1]
                        if prev and prev != sutra_id:
                            edges[(prev, sutra_id)] += 1
        elif len(sutra_ids) == 1:
            nodes.add(sutra_ids[0])
    
    graph = {
        'nodes': list(nodes),
        'edges': [{'source': src, 'target': dst, 'weight': w} for (src, dst), w in edges.items()],
        'stats': {
            'total_traces': total_traces,
            'traces_with_edges': traces_with_edges,
            'total_nodes': len(nodes),
            'total_edges': len(edges)
        }
    }
    
    with open('execution_graph.json', 'w') as f:
        json.dump(graph, f, indent=2)
    
    print(f"✅ Execution graph generated:")
    print(f"  Total traces: {total_traces}")
    print(f"  Traces with edges: {traces_with_edges}")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")
    
    if len(edges) == 0 and total_traces > 0:
        print("\n⚠️ No edges found. Check trace format.")

if __name__ == "__main__":
    generate_execution_graph()
