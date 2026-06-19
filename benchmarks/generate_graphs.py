"""Generate benchmark graphs of various sizes"""
import json
import random

def generate_dag(n, density=0.3, seed=42):
    random.seed(seed)
    nodes = [f"N{i}" for i in range(n)]
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < density:
                edges.append([nodes[i], nodes[j]])
    return {"nodes": nodes, "edges": edges}

def save_graph(graph, filename):
    with open(filename, 'w') as f:
        json.dump(graph, f, indent=2)

sizes = [10, 50, 100, 500, 1000]
for size in sizes:
    g = generate_dag(size)
    save_graph(g, f"benchmarks/graph_{size}.json")
    print(f"Generated graph_{size}.json: {size} nodes, {len(g['edges'])} edges")
