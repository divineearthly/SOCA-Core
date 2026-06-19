import sys
sys.path.append('runtime')
from soca_runtime import SOCARuntime

runtime = SOCARuntime()
graph = {
    "nodes": ["A", "B", "C", "D"],
    "edges": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]]
}

result = runtime.solve_sequence(
    ["sutra_008", "sutra_009", "sutra_010"],
    {"graph": graph, "expected": {"schedule": [["A"], ["B", "C"], ["D"]]}}
)

print("Status:", result['status'])
print("Verified:", result['outputs'].get('verified'))
print("Mismatches:", result['outputs'].get('mismatches'))
print("Schedule:", result['outputs'].get('schedule'))
