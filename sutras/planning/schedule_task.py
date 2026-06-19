"""
Sutra 009: Schedule Task (Optimized)
Pramana: Anumana (Inference)
Precomputes dependencies for O(V+E) performance
"""

def execute(inputs: dict, context: dict = None) -> dict:
    sorted_nodes = inputs.get('sorted_nodes', [])
    graph_data = inputs.get('graph', {})
    
    if not sorted_nodes:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_009",
                "version": "1.0.0",
                "error": "No sorted nodes provided"
            }
        }
    
    edges = graph_data.get('edges', [])
    
    # OPTIMIZATION: Build adjacency and indegree once
    # Instead of scanning edges for each node
    adjacency = {}
    indegree = {}
    
    for node in sorted_nodes:
        adjacency[node] = []
        indegree[node] = 0
    
    for src, dst in edges:
        if src in adjacency and dst in adjacency:
            adjacency[src].append(dst)
            indegree[dst] = indegree.get(dst, 0) + 1
    
    # Now create schedule levels (parallel execution)
    schedule = []
    remaining = set(sorted_nodes)
    executed = set()
    
    while remaining:
        # Find nodes whose dependencies are satisfied
        ready = []
        for node in remaining:
            if indegree.get(node, 0) == 0:
                ready.append(node)
        
        if not ready:
            return {
                "status": "failure",
                "outputs": {},
                "trace": {
                    "sutra_id": "sutra_009",
                    "version": "1.0.0",
                    "error": "Deadlock detected"
                }
            }
        
        schedule.append(ready)
        
        # Update indegree for nodes that depend on ready nodes
        for node in ready:
            remaining.remove(node)
            executed.add(node)
            # Decrease indegree of downstream nodes
            for dep in adjacency.get(node, []):
                if dep in remaining:
                    indegree[dep] = indegree.get(dep, 0) - 1
    
    return {
        "status": "success",
        "outputs": {"schedule": schedule},
        "trace": {
            "sutra_id": "sutra_009",
            "version": "1.0.0",
            "execution_time_ms": 0,
            "inputs": inputs,
            "outputs": {"schedule": schedule}
        }
    }
