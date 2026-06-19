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
    
    # Build adjacency and indegree
    adjacency = {node: [] for node in sorted_nodes}
    indegree = {node: 0 for node in sorted_nodes}
    
    for src, dst in edges:
        if src in adjacency and dst in adjacency:
            adjacency[src].append(dst)
            indegree[dst] = indegree.get(dst, 0) + 1
    
    # Create schedule levels (parallel execution)
    schedule = []
    remaining = set(sorted_nodes)
    
    while remaining:
        # Find nodes with indegree 0
        ready = [node for node in remaining if indegree.get(node, 0) == 0]
        
        if not ready:
            return {
                "status": "failure",
                "outputs": {},
                "trace": {
                    "sutra_id": "sutra_009",
                    "version": "1.0.0",
                    "error": f"Deadlock detected. Remaining: {list(remaining)[:10]}"
                }
            }
        
        schedule.append(ready)
        
        # Remove ready nodes and update indegrees
        for node in ready:
            remaining.remove(node)
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
