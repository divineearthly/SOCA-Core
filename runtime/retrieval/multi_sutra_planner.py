"""
Multi-Sutra Planner
Plans and executes multiple sutras for a single query
"""

import sys
sys.path.append('runtime')
from retrieval.enhanced_retriever import EnhancedRetriever
from soca_runtime import SOCARuntime

class MultiSutraPlanner:
    def __init__(self):
        self.retriever = EnhancedRetriever()
        self.runtime = SOCARuntime()
    
    def plan_and_execute(self, query: str, inputs: dict = None) -> dict:
        """
        Plan and execute multiple sutras for a query.
        """
        if inputs is None:
            inputs = {}
        
        # Step 1: Retrieve relevant sutras
        sutra_ids, details = self.retriever.retrieve(query, top_k=5)
        
        if not sutra_ids:
            return {
                'status': 'failure',
                'error': 'No relevant sutras found',
                'query': query
            }
        
        # Step 2: Plan execution order
        # For now, execute in retrieval order
        # In future, this could use dependency analysis
        
        # Step 3: Execute each sutra
        results = {}
        for sutra_id in sutra_ids:
            try:
                result = self.runtime.solve_sequence([sutra_id], inputs)
                if result.get('status') == 'success':
                    results[sutra_id] = result.get('outputs', {})
                else:
                    results[sutra_id] = {'error': result.get('error', 'Unknown error')}
            except Exception as e:
                results[sutra_id] = {'error': str(e)}
        
        # Step 4: Synthesize results
        synthesis = self._synthesize(query, results)
        
        return {
            'status': 'success',
            'query': query,
            'executed_sutras': sutra_ids,
            'results': results,
            'synthesis': synthesis,
            'trace': {
                'retrieved': details,
                'execution_order': sutra_ids
            }
        }
    
    def _synthesize(self, query: str, results: dict) -> str:
        """Synthesize results from multiple sutras."""
        parts = []
        
        for sutra_id, output in results.items():
            if 'error' in output:
                continue
            for key, value in output.items():
                if key not in ['code', 'test_results']:
                    if isinstance(value, list):
                        parts.append(f"{key}: {', '.join(str(v) for v in value)}")
                    else:
                        parts.append(f"{key}: {value}")
        
        if not parts:
            return "No synthesis available."
        
        return " | ".join(parts)
