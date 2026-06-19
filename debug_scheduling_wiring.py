import sys
sys.path.append('runtime')
from soca_runtime import SOCARuntime

runtime = SOCARuntime()

# Step 1: Run scheduling
graph = {
    "nodes": ["A", "B", "C", "D"],
    "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
}

schedule_result = runtime.solve_sequence(
    ["sutra_008", "sutra_009"],
    {"graph": graph}
)

print("Schedule Result:")
print(f"  Status: {schedule_result['status']}")
print(f"  Schedule: {schedule_result['outputs'].get('schedule')}")
print(f"  Outputs keys: {schedule_result['outputs'].keys()}")

# Step 2: Verify
expected_schedule = [["A"], ["B", "C"], ["D"]]

# THIS IS THE BUG - we need to pass the schedule from outputs
verify_inputs = {
    "expected": {"schedule": expected_schedule},
    "actual": {"schedule": schedule_result["outputs"]["schedule"]}  # FIXED
}

print("\nVerify Inputs:")
print(f"  Expected: {verify_inputs['expected']}")
print(f"  Actual: {verify_inputs['actual']}")

verify_result = runtime.solve_sequence(
    ["sutra_010"],
    verify_inputs
)

print("\nVerify Result:")
print(f"  Status: {verify_result['status']}")
print(f"  Verified: {verify_result['outputs'].get('verified')}")
print(f"  Mismatches: {verify_result['outputs'].get('mismatches')}")
