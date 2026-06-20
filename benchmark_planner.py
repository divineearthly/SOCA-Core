"""
Benchmark: Multi-Sutra Planner Accuracy
"""

import sys
import time
sys.path.append('runtime/retrieval')
from multi_sutra_planner import MultiSutraPlanner

def run_benchmark():
    planner = MultiSutraPlanner()
    
    queries = [
        ("What crop should I grow in Assam?", ['sutra_021', 'sutra_025']),
        ("How to treat pest on rice?", ['sutra_026']),
        ("What is addition?", ['sutra_022']),
        ("Translate hello to Hindi", ['sutra_024']),
        ("What is tulsi used for?", ['sutra_023']),
    ]
    
    correct = 0
    total = len(queries)
    
    print("📊 Planner Accuracy Benchmark")
    print("=" * 50)
    
    for query, expected in queries:
        result = planner.plan_and_execute(query, {})
        sutras = result.get('executed_sutras', [])
        
        # Check if expected sutras are in results
        found = all(e in sutras for e in expected)
        if found:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} Query: {query[:30]}... → {sutras}")
    
    print("-" * 50)
    print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
    return correct/total

if __name__ == "__main__":
    run_benchmark()
