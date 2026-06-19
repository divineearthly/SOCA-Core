"""SOCA Performance Benchmark"""
import sys
import time
import json
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime.soca_runtime import SOCARuntime

def measure_memory():
    try:
        with open('/proc/self/statm', 'r') as f:
            fields = f.read().split()
            pages = int(fields[1])
            page_size = os.sysconf('SC_PAGE_SIZE')
            return (pages * page_size) / (1024 * 1024)
    except:
        return -1

def load_graph(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def run_benchmark():
    print("=" * 60)
    print("📊 SOCA Performance Benchmark")
    print("=" * 60)
    
    results = []
    
    for size in [10, 50, 100, 500, 1000]:
        graph_file = f"benchmarks/graph_{size}.json"
        if not os.path.exists(graph_file):
            print(f"⚠️ {graph_file} not found, skipping...")
            continue
        
        graph = load_graph(graph_file)
        runtime = SOCARuntime()
        
        # Memory before
        mem_before = measure_memory()
        
        # Run scheduling
        start = time.time()
        result = runtime.solve_sequence(
            ["sutra_008", "sutra_009", "sutra_010"],
            {"graph": graph, "expected": {"schedule": []}}  # Skip verification for speed
        )
        elapsed = time.time() - start
        
        # Memory after
        mem_after = measure_memory()
        mem_used = max(0, mem_after - mem_before)
        
        results.append({
            'size': size,
            'nodes': len(graph['nodes']),
            'edges': len(graph['edges']),
            'time_ms': elapsed * 1000,
            'memory_mb': mem_used,
            'status': result['status'],
            'trace_id': result.get('trace', {}).get('trace_id', '')
        })
        
        print(f"  {size} nodes: {elapsed*1000:.1f} ms, {mem_used:.1f} MB, {result['status']}")
    
    print("-" * 60)
    print("📊 Results:")
    print(f"{'Nodes':>6} {'Edges':>6} {'Time (ms)':>10} {'Memory (MB)':>12} {'Status':>10}")
    for r in results:
        print(f"{r['nodes']:>6} {r['edges']:>6} {r['time_ms']:>10.1f} {r['memory_mb']:>12.1f} {r['status']:>10}")
    
    # Save results
    with open('benchmarks/results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\n✅ Results saved to benchmarks/results.json")

if __name__ == "__main__":
    run_benchmark()
