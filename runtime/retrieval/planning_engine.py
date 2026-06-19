"""
Planning Engine: Builds DAG from retrieved sutras
"""

import networkx as nx

class PlanningEngine:
    def __init__(self, retriever):
        self.retriever = retriever
        self.graph = nx.DiGraph()
    
    def plan(self, query: str, inputs: dict) -> dict:
        """
        Build an execution plan for a query.
        
        Args:
            query: Natural language query
            inputs: Input data for execution
        
        Returns:
            dict with 'sutra_sequence' and 'plan' details
        """
        # Step 1: Retrieve sutras
        sutra_ids = self.retriever.retrieve(query, top_k=10)
        
        # Step 2: Build DAG
        self.graph = nx.DiGraph()
        
        # Add nodes
        for sutra_id in sutra_ids:
            self.graph.add_node(sutra_id)
        
        # Step 3: Determine dependencies based on inputs/outputs
        # For now, use sequential order
        for i in range(len(sutra_ids) - 1):
            self.graph.add_edge(sutra_ids[i], sutra_ids[i+1])
        
        # Step 4: Topological sort
        try:
            sequence = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            # If cycle, use original order
            sequence = sutra_ids
        
        return {
            'sutra_sequence': sequence,
            'retrieved_count': len(sutra_ids),
            'plan': {
                'stages': [
                    {
                        'stage': i + 1,
                        'sutra_id': sid
                    }
                    for i, sid in enumerate(sequence)
                ]
            }
        }
