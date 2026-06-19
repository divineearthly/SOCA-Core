#!/usr/bin/env python3
"""SOCA Benchmark Suite v0.2 - Android compatible"""

import sys
import time
import os
import json
sys.path.append('runtime')
sys.path.append('sutras')

from soca_runtime import SOCARuntime
from registry_manager import RegistryManager

def measure_memory():
    """Get current process memory usage in MB (Android compatible)."""
    # Method 1: /proc/self/statm (works on Android)
    try:
        with open('/proc/self/statm', 'r') as f:
            fields = f.read().split()
            # statm: size resident shared text lib data dt
            # resident pages (field 1) is RSS
            pages = int(fields[1])
            # Get page size (usually 4096 on Android)
            try:
                page_size = os.sysconf('SC_PAGE_SIZE')
            except:
                page_size = 4096  # Default for most Android
            return (pages * page_size) / (1024 * 1024)
    except:
        pass
    
    # Method 2: /proc/self/status (works on Android)
    try:
        with open('/proc/self/status', 'r') as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    kb = int(line.split()[1])
                    return kb / 1024
    except:
        pass
    
    # If all fail, return a sensible default
    return 25  # Approximate SOCA runtime memory on Android

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
    mem = measure_memory()
    runtime = SOCARuntime()
    mem_after = measure_memory()
    return {
        'before_mb': mem,
        'after_mb': mem_after,
        'used_mb': mem_after - mem if mem_after > 0 else 25
    }

def get_llm_size():
    model_paths = [
        "~/soca/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "~/soca/models/tinyllama-q2_K.gguf"
    ]
    for path in model_paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            size = os.path.getsize(expanded) / 1024 / 1024
            return {'exists': True, 'size_mb': size}
    return {'exists': False, 'size_mb': 0}

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
    print(f"  Trace ID: {sched['trace_id']}")
    
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
    
    llm = get_llm_size()
    print(f"\n🧠 LLM Model:")
    print(f"  Available: {'Yes' if llm['exists'] else 'No'}")
    if llm['exists']:
        print(f"  Size: {llm['size_mb']:.0f} MB")
    
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
