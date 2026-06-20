#!/usr/bin/env python3
"""
SOCA Full Benchmark - Measures performance and telemetry
"""

import sys
import os
import time
import subprocess
import sqlite3
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
    return elapsed, result.stdout, result.stderr

def get_telemetry_stats():
    """Get telemetry statistics."""
    db_path = os.path.expanduser("~/soca/registry/soca.db")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telemetry")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(confidence) FROM telemetry WHERE confidence > 0")
        avg_conf = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM telemetry WHERE clarification_needed = 1")
        clarifications = cursor.fetchone()[0]
        return {
            'total': total,
            'avg_confidence': avg_conf,
            'clarifications': clarifications
        }

def run_benchmark():
    print("=" * 60)
    print("🕉️ SOCA FULL BENCHMARK")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    queries = [
        "What crop should I grow in Assam?",
        "What is the price of rice in Assam?",
        "How to control pests on rice?",
        "What is the weather like in Assam?",
        "Nutrition advice for 30-year-old",
        "What is addition?",
        "Translate hello to Assamese"
    ]
    
    results = []
    total_time = 0
    
    print("\n📊 Query Performance")
    print("-" * 50)
    
    for query in queries:
        print(f"\n📝 Query: {query[:40]}...")
        elapsed, output, error = measure_time(query)
        total_time += elapsed
        
        # Extract confidence
        confidence = "N/A"
        for line in output.split('\n'):
            if "Confidence:" in line:
                confidence = line.split("Confidence:")[-1].strip()
                break
        
        results.append({
            'query': query[:40],
            'time_ms': elapsed * 1000,
            'confidence': confidence,
            'error': error[:100] if error else ""
        })
        
        print(f"  ⏱️  {elapsed*1000:.1f} ms")
        print(f"  📊 Confidence: {confidence}")
    
    # Telemetry stats
    telemetry = get_telemetry_stats()
    
    print("\n" + "=" * 60)
    print("📊 TELEMETRY SUMMARY")
    print("=" * 60)
    print(f"  Total queries recorded: {telemetry['total']}")
    print(f"  Average confidence: {telemetry['avg_confidence']:.3f}")
    print(f"  Clarifications: {telemetry['clarifications']}")
    
    print("\n📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"  Total queries: {len(queries)}")
    print(f"  Total time: {total_time*1000:.1f} ms")
    print(f"  Average: {total_time/len(queries)*1000:.1f} ms")
    print(f"  Fastest: {min(r['time_ms'] for r in results):.1f} ms")
    print(f"  Slowest: {max(r['time_ms'] for r in results):.1f} ms")
    
    # Save results
    with open('benchmark_results.txt', 'w') as f:
        f.write(f"SOCA Benchmark Results\n")
        f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        for r in results:
            f.write(f"{r['query']}: {r['time_ms']:.1f}ms, conf: {r['confidence']}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Total queries: {len(queries)}\n")
        f.write(f"Average: {total_time/len(queries)*1000:.1f} ms\n")
        f.write(f"Telemetry: {telemetry['total']} records\n")
    
    print("\n✅ Results saved to benchmark_results.txt")

if __name__ == "__main__":
    run_benchmark()
