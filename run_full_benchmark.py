"""Run full benchmark on 45+ queries"""
import sys
import json
import time
sys.path.append('runtime/retrieval')
from multi_sutra_planner import MultiSutraPlanner

def run_full_benchmark():
    planner = MultiSutraPlanner()
    
    with open('benchmark_queries.json', 'r') as f:
        queries = json.load(f)
    
    results = []
    correct = 0
    total = len(queries)
    
    print(f"📊 Running benchmark on {total} queries...")
    print("=" * 50)
    
    for i, item in enumerate(queries):
        query = item['query']
        expected = set(item['expected'])
        domain = item['domain']
        
        start = time.time()
        result = planner.plan_and_execute(query, {})
        elapsed = time.time() - start
        
        # Extract sutra IDs from scored_sutras (list of dicts)
        retrieved = set()
        if 'scored_sutras' in result:
            for s in result['scored_sutras']:
                if 'sutra_id' in s:
                    retrieved.add(s['sutra_id'])
        
        # Also check executed_sutras if scored_sutras is empty
        if not retrieved and 'executed_sutras' in result:
            retrieved = set(result['executed_sutras'])
        
        # Check if all expected sutras are in retrieved
        match = expected.issubset(retrieved)
        if match:
            correct += 1
        
        results.append({
            'query': query[:50],
            'domain': domain,
            'expected': list(expected),
            'retrieved': list(retrieved),
            'match': match,
            'time_ms': elapsed * 1000,
            'synthesis': result.get('synthesis', '')[:100]
        })
        
        # Show progress
        status = "✅" if match else "❌"
        print(f"{status} {i+1}/{total}: {query[:30]}... → {list(retrieved)[:3]}")
    
    print("-" * 50)
    print(f"📊 Results:")
    print(f"  Total queries: {total}")
    print(f"  Correct: {correct}")
    print(f"  Accuracy: {correct/total*100:.1f}%")
    print(f"  Avg time: {sum(r['time_ms'] for r in results)/total:.1f} ms")
    
    # Domain breakdown
    domains = {}
    for r in results:
        d = r['domain']
        if d not in domains:
            domains[d] = {'correct': 0, 'total': 0}
        domains[d]['total'] += 1
        if r['match']:
            domains[d]['correct'] += 1
    
    print("\n📊 Domain breakdown:")
    for d, stats in domains.items():
        acc = stats['correct']/stats['total']*100 if stats['total'] > 0 else 0
        print(f"  {d}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")
    
    # Save results
    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to benchmark_results.json")
    return results

if __name__ == "__main__":
    run_full_benchmark()
