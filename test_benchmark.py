"""
Benchmark: SOCA vs Classical Scheduler
"""

import sys
import time
import networkx as nx
sys.path.append('runtime')

from soca_runtime import SOCARuntime

def generate_graph(size, density=0.3):
    """Generate a random DAG with 'size' nodes."""
    # Create a random DAG
    g = nx.DiGraph()
    nodes = [chr(65 + i) for i in range(size)]  # A, B, C, ...
    edges = []
    
    for i in range(size):
        for j in range(i+1, size):
            if __import__('random').random() < density:
                edges.append([nodes[i], nodes[j]])
    
    return {"nodes": nodes, "edges": edges}

def benchmark_soca(size=10):
    """Run SOCA scheduling benchmark."""
    runtime = SOCARuntime()
    graph = generate_graph(size)
    
    start = time.time()
    result = runtime.solve_sequence(
        ["sutra_008", "sutra_009"],
        {"graph": graph}
    )
    end = time.time()
    
    if result['status'] == 'success':
        return {
            'time': end - start,
            'status': 'success',
            'schedule': result['outputs'].get('schedule', [])
        }
    else:
        return {'time': end - start, 'status': 'failed', 'error': result.get('error')}

def benchmark_classical(size=10):
    """Run classical topological sort."""
    graph = generate_graph(size)
    g = nx.DiGraph()
    
    for node in graph['nodes']:
        g.add_node(node)
    for edge in graph['edges']:
        g.add_edge(edge[0], edge[1])
    
    start = time.time()
    try:
        sorted_nodes = list(nx.topological_sort(g))
        # Simple schedule: each node in its own level
        schedule = [[node] for node in sorted_nodes]
        end = time.time()
        return {'time': end - start, 'status': 'success', 'schedule': schedule}
    except nx.NetworkXUnfeasible:
        end = time.time()
        return {'time': end - start, 'status': 'failed', 'error': 'Cycle detected'}

def run_benchmark():
    print("=" * 60)
    print("📊 SOCA vs Classical Scheduler Benchmark")
    print("=" * 60)
    
    sizes = [5, 10, 20, 50]
    results = []
    
    for size in sizes:
        print(f"\n--- Size: {size} nodes ---")
        
        # SOCA
        soca_result = benchmark_soca(size)
        print(f"  SOCA: {soca_result['time']:.4f}s - {soca_result['status']}")
        
        # Classical
        classical_result = benchmark_classical(size)
        print(f"  Classical: {classical_result['time']:.4f}s - {classical_result['status']}")
        
        results.append({
            'size': size,
            'soca_time': soca_result['time'],
            'classical_time': classical_result['time'],
            'soca_status': soca_result['status'],
            'classical_status': classical_result['status']
        })
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    for r in results:
        soca_ok = r['soca_status'] == 'success'
        classical_ok = r['classical_status'] == 'success'
        print(f"  Size {r['size']}: SOCA {r['soca_time']:.4f}s ({'✅' if soca_ok else '❌'}) | Classical {r['classical_time']:.4f}s ({'✅' if classical_ok else '❌'})")

if __name__ == "__main__":
    run_benchmark()
