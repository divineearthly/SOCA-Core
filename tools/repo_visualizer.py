#!/usr/bin/env python3
"""
SOCA Repository Visualizer
Generates visual maps of the Sutra repository
Inspired by arxiv:2606.14061
"""

import os
import sys
import sqlite3
import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

def build_sutra_graph():
    """Build dependency graph from Sutra registry."""
    sys.path.append('runtime')
    from registry_manager import RegistryManager
    
    rm = RegistryManager()
    g = nx.DiGraph()
    
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
        g.add_node(sutra_id, name=name, category=category or 'core', pramana=pramana)
    
    # Add edges based on category groupings (approximate dependencies)
    categories = {}
    for node in g.nodes:
        cat = g.nodes[node].get('category', 'core')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(node)
    
    # Connect core to all domains
    for cat, nodes in categories.items():
        if cat != 'core':
            for node in nodes:
                if 'core' in categories:
                    # Connect to first core node
                    g.add_edge(categories['core'][0], node)
    
    return g

def visualize_repo():
    """Generate visual map of SOCA repository."""
    print("📊 SOCA Repository Visualizer")
    print("=" * 40)
    
    try:
        # Build graph
        g = build_sutra_graph()
        
        print(f"Nodes: {len(g.nodes)}")
        print(f"Edges: {len(g.edges)}")
        
        # Create figure
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(g, k=2, iterations=30, seed=42)
        
        # Color by category
        colors = {
            'core': '#4CAF50',
            'agriculture': '#8BC34A',
            'education': '#2196F3',
            'health': '#FF9800',
            'memory': '#9C27B0',
            'reasoning': '#F44336',
            'language': '#00BCD4',
            'planning': '#FF5722',
            'verification': '#795548'
        }
        
        node_colors = []
        node_labels = {}
        for node in g.nodes:
            category = g.nodes[node].get('category', 'core')
            node_colors.append(colors.get(category, '#78909C'))
            # Short label
            node_labels[node] = node.replace('sutra_', 'S')
        
        nx.draw(g, pos, node_color=node_colors, with_labels=True,
                labels=node_labels, node_size=300, font_size=5, 
                font_weight='bold', edge_color='#CCCCCC', alpha=0.8)
        
        plt.title("SOCA Sutra Repository Graph\n(Visual structure for AI agents)", fontsize=14)
        plt.tight_layout()
        plt.savefig("soca_repo_graph.png", dpi=300, bbox_inches='tight')
        print("✅ Saved: soca_repo_graph.png")
        
        # Save also as JSON for programmatic use
        graph_data = {
            'nodes': [{'id': n, **g.nodes[n]} for n in g.nodes],
            'edges': [{'source': u, 'target': v} for u, v in g.edges]
        }
        with open('soca_repo_graph.json', 'w') as f:
            json.dump(graph_data, f, indent=2)
        print("✅ Saved: soca_repo_graph.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have networkx and matplotlib installed:")
        print("  pip install networkx matplotlib")

if __name__ == "__main__":
    visualize_repo()
