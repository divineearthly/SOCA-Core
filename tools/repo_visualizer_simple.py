#!/usr/bin/env python3
"""
SOCA Repository Visualizer (Simple - No matplotlib)
Generates JSON representation of Sutra repository graph
"""

import os
import sys
import sqlite3
import json
from pathlib import Path

def build_sutra_graph():
    """Build dependency graph from Sutra registry."""
    sys.path.append('runtime')
    from registry_manager import RegistryManager
    
    rm = RegistryManager()
    nodes = []
    edges = []
    
    # Get all sutras
    with sqlite3.connect(rm.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sutra_id, name, category, pramana
            FROM sutra_registry
            WHERE is_active = TRUE
            ORDER BY sutra_id
        """)
        rows = cursor.fetchall()
    
    for row in rows:
        sutra_id, name, category, pramana = row
        nodes.append({
            'id': sutra_id,
            'name': name,
            'category': category or 'core',
            'pramana': pramana
        })
    
    # Add edges based on category groupings
    categories = {}
    for node in nodes:
        cat = node['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(node['id'])
    
    # Connect core to all domains
    for cat, node_ids in categories.items():
        if cat != 'core' and 'core' in categories:
            for node_id in node_ids:
                edges.append({'source': categories['core'][0], 'target': node_id})
    
    return {'nodes': nodes, 'edges': edges}

def generate_repo_map():
    """Generate JSON map of SOCA repository."""
    print("📊 SOCA Repository Map Generator")
    print("=" * 40)
    
    try:
        graph = build_sutra_graph()
        
        print(f"Nodes: {len(graph['nodes'])}")
        print(f"Edges: {len(graph['edges'])}")
        
        # Save JSON
        with open('soca_repo_graph.json', 'w') as f:
            json.dump(graph, f, indent=2)
        print("✅ Saved: soca_repo_graph.json")
        
        # Also save a simple Markdown visualization
        md_lines = ["# SOCA Sutra Repository Graph\n", "## Nodes by Category\n"]
        
        categories = {}
        for node in graph['nodes']:
            cat = node['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(node['id'])
        
        for cat, ids in sorted(categories.items()):
            md_lines.append(f"### {cat.upper()} ({len(ids)})")
            md_lines.append("| Sutra ID | Name |")
            md_lines.append("|----------|------|")
            for node in graph['nodes']:
                if node['category'] == cat:
                    md_lines.append(f"| {node['id']} | {node['name']} |")
            md_lines.append("")
        
        with open('soca_repo_graph.md', 'w') as f:
            f.write('\n'.join(md_lines))
        print("✅ Saved: soca_repo_graph.md")
        
        # Print summary
        print("\n📊 Repository Summary:")
        for cat, ids in sorted(categories.items()):
            print(f"  {cat}: {len(ids)} sutras")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_repo_map()
