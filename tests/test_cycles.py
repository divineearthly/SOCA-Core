"""Test cycle detection"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from runtime.soca_runtime import SOCARuntime

def test_cycle():
    runtime = SOCARuntime()
    graph = {
        "nodes": ["A", "B", "C"],
        "edges": [["A", "B"], ["B", "C"], ["C", "A"]]
    }
    result = runtime.solve_sequence(
        ["sutra_008", "sutra_009"],
        {"graph": graph}
    )
    
    assert result['status'] == 'failure', f"Expected failure but got {result['status']}"
    
    error_msg = result.get('error', '').lower()
    assert 'cycle' in error_msg, f"Expected 'cycle' in error message, got: {error_msg}"
    
    print("✅ Cycle detection test passed")

if __name__ == "__main__":
    test_cycle()
