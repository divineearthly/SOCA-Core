"""
sutra_073: Profile Context Injector
Pramana: Pratyaksha (Direct Perception)
Injects farmer profile and village context into working memory
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    user_id = inputs.get('user_id', 'anonymous')
    query = inputs.get('query', '')
    working_memory = inputs.get('working_memory', {})
    
    # Simulate profile lookup (in production, this would query the database)
    # For now, use a default profile if not found
    profile = {
        'district': 'bongaigaon',
        'soil_type': 'loamy',
        'crop_history': ['rice', 'mustard'],
        'land_size': 2.5,
        'preferences': {'organic': True}
    }
    
    # Inject into working memory
    working_memory['profile'] = profile
    working_memory['district'] = profile.get('district', '')
    working_memory['soil_type'] = profile.get('soil_type', '')
    working_memory['crop_history'] = profile.get('crop_history', [])
    
    return success_response(
        outputs={
            'profile_loaded': True,
            'district': profile.get('district', ''),
            'soil_type': profile.get('soil_type', ''),
            'crop_history': profile.get('crop_history', []),
            'working_memory': working_memory
        },
        confidence=0.9,
        metadata={'sutra': 'sutra_073', 'version': '1.0.0'}
    )
