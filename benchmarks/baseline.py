"""Classical baseline comparison"""
import sys
import time
import json
import networkx as nx
from pathlib import Path

def load_graph(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def run_baseline():
    print("=" * 60)
    print("📊 NetworkX Baseline Comparison")
    print("=" * 60)
    
    results = []
    
    for size in [10, 50, 100, 500, 1000]:
        graph_file = f"benchmarks/graph_{size}.json"
        if not os.path.exists(graph_file):
            print(f"⚠️ {graph_file} not found, skipping...")
            continue
        
        graph = load_graph(graph_file)
        
        # Build NetworkX graph
        g = nx.DiGraph()
        for node in graph['nodes']:
            g.add_node(node)
        for edge in graph['edges']:
            g.add_edge(edge[0], edge[1])
        
        start = time.time()
        try:
            sorted_nodes = list(nx.topological_sort(g))
            status = 'success'
        except nx.NetworkXUnfeasible:
            sorted_nodes = []
            status = 'failure (cycle)'
        elapsed = time.time() - start
        
        results.append({
            'size': size,
            'nodes': len(graph['nodes']),
            'edges': len(graph['edges']),
            'time_ms': elapsed * 1000,
            'status': status,
            'nodes_sorted': len(sorted_nodes)
        })
        
        print(f"  {size} nodes: {elapsed*1000:.1f} ms, {status}")
    
    print("-" * 60)
    print("📊 NetworkX Results:")
    print(f"{'Nodes':>6} {'Edges':>6} {'Time (ms)':>10} {'Status':>15}")
    for r in results:
        print(f"{r['nodes']:>6} {r['edges']:>6} {r['time_ms']:>10.1f} {r['status']:>15}")
    
    with open('benchmarks/baseline_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\n✅ Baseline results saved to benchmarks/baseline_results.json")

if __name__ == "__main__":
    import os
    run_baseline()
