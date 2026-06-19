"""Test cycle detection"""
import sys
sys.path.append('runtime')
from soca_runtime import SOCARuntime

def test_cycle():
    runtime = SOCARuntime()
    graph = {
        "nodes": ["A", "B", "C"],
        "edges": [["A", "B"], ["B", "C"], ["C", "A"]]  # Cycle
    }
    result = runtime.solve_sequence(
        ["sutra_008", "sutra_009"],
        {"graph": graph}
    )
    
    # Should fail with cycle detection
    assert result['status'] == 'failure', f"Expected failure but got {result['status']}"
    
    # Check error message for cycle
    error_msg = result.get('error', '').lower()
    assert 'cycle' in error_msg, f"Expected 'cycle' in error message, got: {error_msg}"
    
    print("✅ Cycle detection test passed")

if __name__ == "__main__":
    test_cycle()
