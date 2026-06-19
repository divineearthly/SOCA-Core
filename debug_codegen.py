import sys
sys.path.append('runtime')
from soca_runtime import SOCARuntime

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

print("Status:", result['status'])
print("Outputs:", result['outputs'].keys())
print("Verified:", result['outputs'].get('verified'))
print("Trace:", result.get('trace', {}))
