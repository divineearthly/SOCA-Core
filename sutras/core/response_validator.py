"""
sutra_072: Response Validator
Pramana: Pratyaksha (Direct Perception)
Final validation of response
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    response = inputs.get('response', '')
    confidence = inputs.get('confidence', 0.5)
    sources = inputs.get('sources', [])
    
    if not response:
        return failure_response("No response to validate")
    
    # Final quality check
    quality = 0.5
    if len(response) > 10:
        quality += 0.2
    if confidence > 0.6:
        quality += 0.2
    if sources:
        quality += 0.1
    
    quality = min(quality, 1.0)
    
    return success_response(
        outputs={
            'validated': True,
            'response': response,
            'quality': round(quality, 2),
            'sources': sources,
            'approved': quality > 0.6
        },
        confidence=quality,
        metadata={'sutra': 'sutra_072', 'version': '1.0.0'}
    )
