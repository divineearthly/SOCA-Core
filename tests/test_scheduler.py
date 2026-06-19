"""Test dependency scheduling"""
import sys
import os
from pathlib import Path

# Add project root to Python path so we can import runtime modules
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Now we can import from runtime
from runtime.soca_runtime import SOCARuntime

def test_scheduling():
    runtime = SOCARuntime()
    graph = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
    }
    expected = [["A"], ["B", "C"], ["D"]]
    
    schedule_result = runtime.solve_sequence(
        ["sutra_008", "sutra_009"],
        {"graph": graph}
    )
    
    assert schedule_result['status'] == 'success', f"Schedule failed: {schedule_result.get('error')}"
    
    actual_schedule = schedule_result['outputs'].get('schedule', [])
    
    verify_result = runtime.solve_sequence(
        ["sutra_010"],
        {"expected": {"schedule": expected}, "actual": {"schedule": actual_schedule}}
    )
    
    assert verify_result['status'] == 'success', f"Verification failed: {verify_result.get('error')}"
    assert verify_result['outputs']['verified'] == True, f"Mismatches: {verify_result['outputs'].get('mismatches')}"
    print("✅ Scheduling test passed")

if __name__ == "__main__":
    test_scheduling()
