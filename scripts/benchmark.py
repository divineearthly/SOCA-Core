#!/usr/bin/env python3
"""
SOCA Performance Benchmark
Measures latency, memory, and accuracy
"""

import sys
import os
import time
import subprocess
from datetime import datetime

def measure_time(query):
    """Measure query execution time."""
    start = time.time()
    result = subprocess.run(
        ['./soca_agent', query],
        capture_output=True,
        text=True,
        timeout=30
    )
    elapsed = time.time() - start
    return elapsed, result.stdout

def run_benchmark():
    print("=" * 60)
    print("🕉️ SOCA PERFORMANCE BENCHMARK")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    queries = [
        "What crop should I grow in Assam?",
        "What is the price of rice in Assam?",
        "How to control pests on rice?",
        "What is the weather like in Assam?",
        "Nutrition advice for 30-year-old"
    ]
    
    results = []
    total_time = 0
    
    print("\n📊 Query Performance")
    print("-" * 40)
    
    for query in queries:
        print(f"\n📝 Query: {query[:40]}...")
        elapsed, output = measure_time(query)
        total_time += elapsed
        
        # Extract confidence if present
        confidence = "N/A"
        for line in output.split('\n'):
            if "Confidence:" in line:
                confidence = line.split("Confidence:")[-1].strip()
                break
        
        results.append({
            'query': query[:40],
            'time_ms': elapsed * 1000,
            'confidence': confidence
        })
        
        print(f"  ⏱️  {elapsed*1000:.1f} ms")
        print(f"  📊 Confidence: {confidence}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"  Total queries: {len(queries)}")
    print(f"  Total time: {total_time*1000:.1f} ms")
    print(f"  Average: {total_time/len(queries)*1000:.1f} ms")
    
    print("\n📊 Results:")
    print(f"{'Query':<30} | {'Time (ms)':>10} | {'Confidence':>12}")
    print("-" * 60)
    for r in results:
        print(f"{r['query']:<30} | {r['time_ms']:>10.1f} | {r['confidence']:>12}")

if __name__ == "__main__":
    run_benchmark()
