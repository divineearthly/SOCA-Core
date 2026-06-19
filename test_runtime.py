"""
Test the full SOCA Runtime
"""

import sys
sys.path.append('runtime')

from soca_runtime import SOCARuntime

def test_runtime():
    print("=" * 50)
    print("SOCA Runtime Test")
    print("=" * 50)
    
    # Initialize runtime
    runtime = SOCARuntime()
    
    # Register sutras from directory
    print("\n--- Registering Sutras ---")
    runtime.register_sutras_from_directory("sutras")
    
    # Get stats
    stats = runtime.get_stats()
    print(f"\nStats: {stats}")
    
    # Test with dependency scheduling
    print("\n--- Test: Dependency Scheduling ---")
    
    graph_data = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
    }
    
    # Execute sequence: dependency_sort -> schedule_task -> verify_output
    result = runtime.solve_sequence(
        ["sutra_008", "sutra_009", "sutra_010"],
        {
            "graph": graph_data,
            "expected": {
                "schedule": [["A"], ["B", "C"], ["D"]]
            }
        }
    )
    
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Outputs: {result['outputs']}")
        print(f"Trace ID: {result['trace']['trace_id']}")
        print(f"Executed Sutras: {len(result['trace']['executed_sutras'])}")
    
    print("\n" + "=" * 50)
    if result['status'] == 'success':
        print("✅ Runtime test passed!")
    else:
        print(f"❌ Runtime test failed: {result.get('error')}")
    print("=" * 50)

if __name__ == "__main__":
    test_runtime()
