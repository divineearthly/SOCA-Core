#!/usr/bin/env python3
"""SOCA Benchmark Suite v0.2"""

import sys
import time
import os
import json
sys.path.append('runtime')
sys.path.append('sutras')

from soca_runtime import SOCARuntime
from registry_manager import RegistryManager

def measure_memory():
    """Get current process memory usage in MB."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except:
        try:
            with open('/proc/self/statm', 'r') as f:
                pages = int(f.read().split()[0])
                page_size = os.sysconf('SC_PAGE_SIZE')
                return (pages * page_size) / 1024 / 1024
        except:
            return -1

def benchmark_scheduling():
    runtime = SOCARuntime()
    graph = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
    }
    start = time.time()
    result = runtime.solve_sequence(
        ["sutra_008", "sutra_009", "sutra_010"],
        {"graph": graph, "expected": {"schedule": [["A"], ["B", "C"], ["D"]]}}
    )
    elapsed = time.time() - start
    return {
        'status': result['status'],
        'time': elapsed,
        'verified': result['outputs'].get('verified', False),
        'trace_id': result['trace'].get('trace_id', '')
    }

def benchmark_cycle_detection():
    runtime = SOCARuntime()
    graph = {
        "nodes": ["A", "B", "C"],
        "edges": [["A", "B"], ["B", "C"], ["C", "A"]]
    }
    start = time.time()
    result = runtime.solve_sequence(
        ["sutra_008", "sutra_009"],
        {"graph": graph}
    )
    elapsed = time.time() - start
    return {
        'status': result['status'],
        'time': elapsed,
        'detected': 'cycle' in result.get('error', '').lower()
    }

def benchmark_code_generation():
    runtime = SOCARuntime()
    result = runtime.solve_sequence(
        ["sutra_011"],
        {
            "specification": "Calculate factorial of n",
            "test_cases": [
                {"inputs": [0], "expected": 1},
                {"inputs": [5], "expected": 120},
                {"inputs": [7], "expected": 5040}
            ]
        }
    )
    return {
        'status': result['status'],
        'verified': result['outputs'].get('verified', False),
        'tests_passed': result.get('trace', {}).get('test_cases_passed', 0),
        'tests_total': result.get('trace', {}).get('test_cases_total', 0)
    }

def benchmark_memory():
    mem_before = measure_memory()
    runtime = SOCARuntime()
    mem_after = measure_memory()
    return {
        'before_mb': mem_before,
        'after_mb': mem_after,
        'used_mb': mem_after - mem_before if mem_after > 0 else 0
    }

def run_benchmark():
    print("=" * 60)
    print("📊 SOCA BENCHMARK SUITE v0.2")
    print("Platform: Android (Termux)")
    print("=" * 60)
    
    mem = benchmark_memory()
    print(f"\n📈 Memory Usage: {mem['used_mb']:.1f} MB")
    
    sched = benchmark_scheduling()
    print(f"\n📋 Dependency Scheduling:")
    print(f"  Status: {sched['status']}")
    print(f"  Verified: {sched['verified']}")
    print(f"  Time: {sched['time']*1000:.1f} ms")
    
    cycle = benchmark_cycle_detection()
    print(f"\n🔄 Cycle Detection:")
    print(f"  Status: {cycle['status']}")
    print(f"  Detected: {cycle['detected']}")
    print(f"  Time: {cycle['time']*1000:.1f} ms")
    
    code = benchmark_code_generation()
    print(f"\n💻 Code Generation:")
    print(f"  Status: {code['status']}")
    print(f"  Verified: {code['verified']}")
    print(f"  Tests: {code['tests_passed']}/{code['tests_total']} passed")
    
    rm = RegistryManager()
    stats = rm.get_stats()
    print(f"\n📊 Registry:")
    print(f"  Total Sutras: {stats['total_sutras']}")
    print(f"  Total Traces: {stats['total_traces']}")
    print(f"  Total Usage: {stats['total_usage']}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"  Memory:            {mem['used_mb']:.1f} MB")
    print(f"  Scheduling:        {'✅' if sched['verified'] else '❌'}")
    print(f"  Cycle Detection:   {'✅' if cycle['detected'] else '❌'}")
    print(f"  Code Generation:   {code['tests_passed']}/{code['tests_total']}")
    print("=" * 60)
    return {'memory': mem, 'scheduling': sched, 'cycle': cycle, 'code': code}

if __name__ == "__main__":
    run_benchmark()
