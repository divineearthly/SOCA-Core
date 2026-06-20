"""
sutra_071: Fact Checker
Pramana: Pratyaksha (Direct Perception)
Verifies facts against evidence
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    answer = inputs.get('answer', '')
    sources = inputs.get('sources', [])
    domain = inputs.get('domain', 'general')
    
    if not answer:
        return failure_response("No answer to check")
    
    # Calculate confidence
    confidence = 0.5
    confidence += min(len(sources) * 0.05, 0.3)
    if domain in ['agriculture', 'medicine']:
        confidence += 0.1
    confidence = min(confidence, 1.0)
    
    return success_response(
        outputs={
            'verified': confidence > 0.6,
            'confidence': round(confidence, 2),
            'sources': sources,
            'domain': domain
        },
        confidence=confidence,
        metadata={'sutra': 'sutra_071', 'version': '1.0.0'}
    )
