"""Test code generation"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from runtime.soca_runtime import SOCARuntime

def test_codegen():
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
    
    assert result['status'] == 'success', f"Code generation failed: {result.get('error')}"
    
    test_results = result['outputs'].get('test_results', [])
    verified = result['outputs'].get('verified', False)
    
    passed = sum(1 for t in test_results if t.get('passed', False))
    total = len(test_results)
    
    assert verified == True, "Code generation not verified"
    assert passed == total, f"Tests failed: {passed}/{total} passed"
    print(f"✅ Codegen test passed: {passed}/{total}")

if __name__ == "__main__":
    test_codegen()
