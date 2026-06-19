"""Generate benchmark report"""
import json

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return []

print("=" * 60)
print("📊 SOCA Benchmark Report")
print("=" * 60)

soca_results = load_json('benchmarks/results.json')
nx_results = load_json('benchmarks/baseline_results.json')

print("\n📈 SOCA Performance:")
print(f"{'Nodes':>6} {'Time (ms)':>12} {'Memory (MB)':>12} {'Status':>12}")
for r in soca_results:
    print(f"{r['nodes']:>6} {r['time_ms']:>12.1f} {r['memory_mb']:>12.1f} {r['status']:>12}")

print("\n📈 NetworkX Baseline:")
print(f"{'Nodes':>6} {'Time (ms)':>12} {'Status':>15}")
for r in nx_results:
    print(f"{r['nodes']:>6} {r['time_ms']:>12.1f} {r['status']:>15}")

if len(soca_results) > 0 and len(nx_results) > 0:
    print("\n📊 Comparison:")
    for s, n in zip(soca_results, nx_results):
        if s['size'] == n['size']:
            ratio = s['time_ms'] / n['time_ms'] if n['time_ms'] > 0 else float('inf')
            print(f"  {s['size']} nodes: SOCA {s['time_ms']:.1f}ms, NetworkX {n['time_ms']:.1f}ms (ratio: {ratio:.1f}x)")
