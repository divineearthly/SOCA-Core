"""Test dependency scheduling"""
import sys
sys.path.append('runtime')
from soca_runtime import SOCARuntime

def test_scheduling():
    runtime = SOCARuntime()
    graph = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
    }
    expected = [["A"], ["B", "C"], ["D"]]
    
    # Step 1: Get schedule
    schedule_result = runtime.solve_sequence(
        ["sutra_008", "sutra_009"],
        {"graph": graph}
    )
    
    # Check if we got a valid schedule
    assert schedule_result['status'] == 'success', f"Schedule failed: {schedule_result.get('error')}"
    
    # Step 2: Verify the schedule using sutra_010
    # The schedule is in schedule_result['outputs']['schedule']
    # But if outputs doesn't exist, check trace or other fields
    if 'outputs' in schedule_result:
        actual_schedule = schedule_result['outputs'].get('schedule', [])
    else:
        actual_schedule = schedule_result.get('schedule', [])
    
    verify_result = runtime.solve_sequence(
        ["sutra_010"],
        {"expected": {"schedule": expected}, "actual": {"schedule": actual_schedule}}
    )
    
    assert verify_result['status'] == 'success', f"Verification failed: {verify_result.get('error')}"
    assert verify_result['outputs']['verified'] == True, f"Mismatches: {verify_result['outputs'].get('mismatches')}"
    print("✅ Scheduling test passed")

if __name__ == "__main__":
    test_scheduling()
