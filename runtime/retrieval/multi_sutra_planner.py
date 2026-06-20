"""
Multi-Sutra Planner with Memory, Confidence, and Parameter Extraction
"""

import sys
sys.path.append('runtime')
from retrieval.enhanced_retriever import EnhancedRetriever
from retrieval.confidence_scorer import ConfidenceScorer
from retrieval.memory_integration import MemoryIntegration
from soca_runtime import SOCARuntime

class MultiSutraPlanner:
    def __init__(self):
        self.retriever = EnhancedRetriever()
        self.confidence = ConfidenceScorer()
        self.memory = MemoryIntegration()
        self.runtime = SOCARuntime()
    
    def plan_and_execute(self, query: str, inputs: dict = None) -> dict:
        """
        Plan and execute multiple sutras for a query with memory and confidence.
        """
        if inputs is None:
            inputs = {}
        
        # Step 1: Extract parameters from query
        params = self.retriever.extract_parameters(query)
        inputs.update(params)
        
        # Step 2: Retrieve relevant sutras
        sutra_ids, details = self.retriever.retrieve(query, top_k=5)
        
        # Step 3: Score each sutra with confidence
        scored_sutras = []
        for sutra_id in sutra_ids:
            concepts = [d['concept'] for d in details if d['sutra_id'] == sutra_id]
            score = self.confidence.score_sutra(sutra_id, concepts)
            scored_sutras.append({
                'sutra_id': sutra_id,
                'score': score,
                'concepts': concepts
            })
        
        # Sort by score
        scored_sutras.sort(key=lambda x: x['score'], reverse=True)
        
        # Step 4: Add memory context
        memory_context = self.memory.get_all_context()
        if memory_context:
            inputs.update(memory_context)
        
        # Step 5: Execute each sutra with extracted parameters
        results = {}
        for item in scored_sutras[:5]:
            sutra_id = item['sutra_id']
            try:
                # Pass extracted parameters to the sutra
                result = self.runtime.solve_sequence([sutra_id], inputs)
                if result.get('status') == 'success':
                    results[sutra_id] = {
                        'outputs': result.get('outputs', {}),
                        'confidence': item['score'],
                        'concepts': item['concepts']
                    }
                else:
                    results[sutra_id] = {'error': result.get('error', 'Unknown error')}
            except Exception as e:
                results[sutra_id] = {'error': str(e)}
        
        # Step 6: Synthesize with confidence
        synthesis = self._synthesize_with_confidence(query, results, scored_sutras)
        
        return {
            'status': 'success',
            'query': query,
            'parameters': params,
            'scored_sutras': scored_sutras[:5],
            'results': results,
            'synthesis': synthesis,
            'memory_used': memory_context,
            'trace': {
                'retrieved': details,
                'confidence_scores': scored_sutras[:5]
            }
        }
    
    def _synthesize_with_confidence(self, query: str, results: dict, scored_sutras: list) -> str:
        """Synthesize results with confidence scores."""
        parts = []
        confidence_parts = []
        
        for item in scored_sutras:
            sutra_id = item['sutra_id']
            if sutra_id in results and 'error' not in results[sutra_id]:
                output = results[sutra_id].get('outputs', {})
                score = item['score']
                
                for key, value in output.items():
                    if key in ['code', 'test_results', 'verified']:
                        continue
                    if isinstance(value, list):
                        if value:
                            parts.append(f"{key}: {', '.join(str(v) for v in value)}")
                            confidence_parts.append(f"({score:.2f})")
                    elif value:
                        parts.append(f"{key}: {value}")
                        confidence_parts.append(f"({score:.2f})")
        
        if not parts:
            return "No synthesis available."
        
        # Build with confidence
        if len(parts) > 1:
            result = "Based on multiple sources:\n"
            for i, part in enumerate(parts):
                conf = confidence_parts[i] if i < len(confidence_parts) else ""
                result += f"  • {part} {conf}\n"
            return result.strip()
        else:
            return parts[0] + f" (confidence: {confidence_parts[0] if confidence_parts else '0.50'})"
    
    def store_memory(self, key: str, value: any):
        """Store context in memory."""
        self.memory.store_context(key, value)
    
    def get_memory(self, key: str):
        """Get context from memory."""
        return self.memory.get_context(key)
