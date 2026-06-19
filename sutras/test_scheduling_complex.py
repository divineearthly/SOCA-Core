import sys
sys.path.append('sutras')

from planning.dependency_sort import execute as dependency_sort
from planning.schedule_task import execute as schedule_task

# Complex graph: 10 nodes
graph = {
    "nodes": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "edges": [
        ["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"],
        ["D", "E"], ["E", "F"], ["F", "G"], ["G", "H"],
        ["H", "I"], ["I", "J"]
    ]
}

result1 = dependency_sort({"graph": graph})
sorted_nodes = result1['outputs'].get('sorted_nodes', [])
print(f"Sorted: {sorted_nodes}")

result2 = schedule_task({"graph": graph, "sorted_nodes": sorted_nodes})
schedule = result2['outputs'].get('schedule', [])
print(f"Schedule: {schedule}")
