"""
End-to-End Test: Dependency Scheduling
"""

import sys
sys.path.append('sutras')

from planning.dependency_sort import execute as dependency_sort
from planning.schedule_task import execute as schedule_task
from meta.verify_output import execute as verify_output

def test_dependency_scheduling():
    print("=" * 50)
    print("SOCA End-to-End Test: Dependency Scheduling")
    print("=" * 50)
    
    # Input: Dependency graph
    graph_data = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
    }
    
    print(f"\nInput Graph:")
    print(f"  Nodes: {graph_data['nodes']}")
    print(f"  Edges: {graph_data['edges']}")
    
    # Step 1: Sort dependencies
    print(f"\n--- Step 1: Dependency Sort ---")
    result1 = dependency_sort({"graph": graph_data})
    sorted_nodes = result1['outputs'].get('sorted_nodes', [])
    print(f"Sorted nodes: {sorted_nodes}")
    
    # Step 2: Create schedule
    print(f"\n--- Step 2: Schedule Creation ---")
    result2 = schedule_task({
        "graph": graph_data,
        "sorted_nodes": sorted_nodes
    })
    schedule = result2['outputs'].get('schedule', [])
    print(f"Schedule: {schedule}")
    
    # Step 3: Verify
    print(f"\n--- Step 3: Verification ---")
    result3 = verify_output({
        "expected": {
            "schedule": [["A"], ["B", "C"], ["D"]]
        },
        "actual": {
            "schedule": schedule
        }
    })
    print(f"Verified: {result3['outputs']['verified']}")
    if result3['outputs']['mismatches']:
        print(f"Mismatches: {result3['outputs']['mismatches']}")
    
    print("\n" + "=" * 50)
    if result3['outputs']['verified']:
        print("✅ All tests passed!")
    else:
        print("❌ Test failed!")
    print("=" * 50)
    
    return result3['outputs']['verified']

if __name__ == "__main__":
    test_dependency_scheduling()
