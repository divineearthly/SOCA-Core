"""
Sutra 008: Dependency Sort (Topological Sort)
Pramana: Anumana (Inference)
"""

import networkx as nx

def execute(inputs: dict, context: dict = None) -> dict:
    graph_data = inputs.get('graph')
    
    if not graph_data:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_008",
                "version": "1.0.0",
                "error": "Missing graph input"
            }
        }
    
    try:
        g = nx.DiGraph()
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        for node in nodes:
            g.add_node(node)
        for edge in edges:
            if len(edge) >= 2:
                g.add_edge(edge[0], edge[1])
        
        try:
            sorted_nodes = list(nx.topological_sort(g))
            has_cycle = False
        except nx.NetworkXUnfeasible:
            return {
                "status": "failure",
                "outputs": {},
                "trace": {
                    "sutra_id": "sutra_008",
                    "version": "1.0.0",
                    "error": "Graph contains a cycle"
                }
            }
        
        return {
            "status": "success",
            "outputs": {
                "sorted_nodes": sorted_nodes,
                "has_cycle": has_cycle
            },
            "trace": {
                "sutra_id": "sutra_008",
                "version": "1.0.0",
                "execution_time_ms": 0,
                "inputs": inputs,
                "outputs": {"sorted_nodes": sorted_nodes}
            }
        }
    except Exception as e:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_008",
                "version": "1.0.0",
                "error": str(e)
            }
        }
