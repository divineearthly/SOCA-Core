"""
Sutra 009: Schedule Task
Pramana: Anumana (Inference)
"""

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Schedule a task based on sorted dependencies.
    
    Args:
        inputs: dict with 'graph' and 'sorted_nodes' keys
    
    Returns:
        dict with 'status', 'outputs', 'trace'
    """
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
    
    # Create schedule levels (parallel execution)
    schedule = []
    remaining = set(sorted_nodes)
    executed = set()
    
    while remaining:
        # Find nodes whose dependencies are all satisfied
        ready = []
        for node in remaining:
            deps = [edge[0] for edge in graph_data.get('edges', []) 
                    if len(edge) >= 2 and edge[1] == node]
            if all(dep in executed for dep in deps):
                ready.append(node)
        
        if not ready:
            # Should not happen with valid topological sort
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
        for node in ready:
            remaining.remove(node)
            executed.add(node)
    
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
