"""
sutra_075: Evidence Aggregator
Pramana: Anumana (Inference)
Aggregates evidence from multiple sources and calculates confidence
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    answer = inputs.get('answer', '')
    sources = inputs.get('sources', [])
    knowledge_results = inputs.get('knowledge_results', [])
    domain = inputs.get('domain', 'general')
    
    # Calculate confidence based on evidence
    source_count = len(sources) + len(knowledge_results)
    
    if source_count >= 5:
        confidence = 0.9
        level = "High"
    elif source_count >= 3:
        confidence = 0.7
        level = "Medium"
    elif source_count >= 1:
        confidence = 0.5
        level = "Low"
    else:
        confidence = 0.3
        level = "Very Low"
    
    # Domain boost
    if domain in ['agriculture', 'medicine']:
        confidence = min(1.0, confidence + 0.05)
    
    return success_response(
        outputs={
            'confidence': round(confidence, 2),
            'level': level,
            'source_count': source_count,
            'sources': sources,
            'knowledge_sources': [k.get('source') for k in knowledge_results[:3]],
            'verdict': 'Verified' if confidence > 0.6 else 'Needs Review'
        },
        confidence=confidence,
        metadata={'sutra': 'sutra_075', 'version': '1.0.0'}
    )
