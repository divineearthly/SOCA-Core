"""Test cycle detection in dependency graph"""
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
    assert result['status'] == 'failure'
    assert 'cycle' in result['error'].lower()
    print("✅ Cycle detection works!")

if __name__ == "__main__":
    test_cycle()
