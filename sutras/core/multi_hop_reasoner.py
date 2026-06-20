"""
sutra_070: Multi-Hop Reasoner
Pramana: Anumana (Inference)
Combines outputs from multiple sutras
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    results = inputs.get('results', {})
    query = inputs.get('query', '')
    
    if not results:
        return failure_response("No results to reason with")
    
    # Combine results
    combined = {}
    for sutra_id, output in results.items():
        if isinstance(output, dict):
            for key, value in output.items():
                if key not in combined:
                    combined[key] = []
                combined[key].append(value)
    
    # Synthesize
    synthesis = []
    for key, values in combined.items():
        if values:
            synthesis.append(f"{key}: {', '.join(str(v) for v in values[:3])}")
    
    return success_response(
        outputs={
            'synthesis': ' | '.join(synthesis),
            'combined': combined,
            'sources': list(results.keys())
        },
        confidence=0.85,
        metadata={'sutra': 'sutra_070', 'version': '1.0.0'}
    )
