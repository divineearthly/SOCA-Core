"""
sutra_069: Query Planner
Pramana: Anumana (Inference)
Plans which sutras to execute and returns required slots
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '')
    intent = inputs.get('intent', 'general')
    
    if not query:
        return failure_response("Query required")
    
    # Map intent to sutra sequence and required slots
    intent_map = {
        'agriculture': {
            'sequence': ['sutra_021', 'sutra_025', 'sutra_027', 'sutra_029'],
            'required_slots': ['season', 'district']
        },
        'education': {
            'sequence': ['sutra_022'],
            'required_slots': ['topic']
        },
        'translation': {
            'sequence': ['sutra_024', 'sutra_033'],
            'required_slots': ['language']
        },
        'medicinal': {
            'sequence': ['sutra_023'],
            'required_slots': ['plant']
        },
        'market': {
            'sequence': ['sutra_029', 'sutra_035'],
            'required_slots': ['crop']
        },
        'livestock': {
            'sequence': ['sutra_031'],
            'required_slots': ['animal']
        }
    }
    
    default = {
        'sequence': ['sutra_041'],
        'required_slots': ['query']
    }
    
    plan = intent_map.get(intent, default)
    
    return success_response(
        outputs={
            'sequence': plan['sequence'],
            'intent': intent,
            'query': query,
            'required_slots': plan['required_slots']
        },
        confidence=0.9,
        metadata={'sutra': 'sutra_069', 'version': '1.0.0'}
    )
