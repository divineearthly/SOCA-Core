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

print("Code Generation Result:")
print(f"  Status: {result['status']}")
print(f"  Outputs keys: {result['outputs'].keys()}")
print(f"  Verified: {result['outputs'].get('verified')}")

# THIS IS THE BUG - we need to read from outputs, not trace
test_results = result['outputs'].get('test_results', [])

print(f"\nTest Results:")
print(f"  Count: {len(test_results)}")
for t in test_results:
    print(f"    Test {t['test_id']}: {t['passed']}")

total = len(test_results)
passed = sum(1 for t in test_results if t['passed'])
print(f"\n  Passed: {passed}/{total}")
