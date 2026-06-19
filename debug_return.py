"""Debug what solve_sequence actually returns"""
import sys
sys.path.append('runtime')
from soca_runtime import SOCARuntime

runtime = SOCARuntime()

# Test 1: Scheduling
graph = {
    "nodes": ["A", "B", "C", "D"],
    "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
}

result = runtime.solve_sequence(
    ["sutra_008", "sutra_009"],
    {"graph": graph}
)

print("=== Scheduling Result ===")
print(f"Status: {result.get('status')}")
print(f"Keys: {result.keys()}")
if 'outputs' in result:
    print(f"Outputs keys: {result['outputs'].keys()}")
    print(f"Schedule: {result['outputs'].get('schedule')}")
else:
    print(f"No 'outputs' key. Full result: {result}")

# Test 2: Code Generation
result2 = runtime.solve_sequence(
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

print("\n=== Code Generation Result ===")
print(f"Status: {result2.get('status')}")
print(f"Keys: {result2.keys()}")
if 'outputs' in result2:
    print(f"Outputs keys: {result2['outputs'].keys()}")
    print(f"Verified: {result2['outputs'].get('verified')}")
    print(f"Test Results: {result2['outputs'].get('test_results')}")
else:
    print(f"No 'outputs' key. Full result: {result2}")

# Test 3: Cycle Detection
graph2 = {
    "nodes": ["A", "B", "C"],
    "edges": [["A", "B"], ["B", "C"], ["C", "A"]]
}

result3 = runtime.solve_sequence(
    ["sutra_008", "sutra_009"],
    {"graph": graph2}
)

print("\n=== Cycle Detection Result ===")
print(f"Status: {result3.get('status')}")
print(f"Keys: {result3.keys()}")
print(f"Error: {result3.get('error')}")
