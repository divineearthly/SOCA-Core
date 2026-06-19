"""
sutra_076: Persistent Profile Manager
Pramana: Pratyaksha (Direct Perception)
Loads and saves farmer profiles from disk
"""

import os
import json
import sys
sys.path.append('runtime')
from response import success_response, failure_response

PROFILE_DIR = os.path.expanduser("~/soca/data/profiles")

def execute(inputs: dict, context: dict = None) -> dict:
    action = inputs.get('action', 'load')
    user_id = inputs.get('user_id', 'anonymous')
    profile_data = inputs.get('profile_data', {})
    
    os.makedirs(PROFILE_DIR, exist_ok=True)
    profile_path = os.path.join(PROFILE_DIR, f"{user_id}.json")
    
    if action == 'load':
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            return success_response(
                outputs={
                    'profile_loaded': True,
                    'profile': profile,
                    'user_id': user_id
                },
                confidence=1.0,
                metadata={'sutra': 'sutra_076', 'version': '1.0.0'}
            )
        else:
            # Return default profile for new user
            default_profile = {
                'district': 'bongaigaon',
                'soil_type': 'loamy',
                'crop_history': [],
                'land_size': 0,
                'preferences': {}
            }
            return success_response(
                outputs={
                    'profile_loaded': False,
                    'profile': default_profile,
                    'user_id': user_id,
                    'is_new': True
                },
                confidence=0.8,
                metadata={'sutra': 'sutra_076', 'version': '1.0.0'}
            )
    
    elif action == 'save':
        if not profile_data:
            return failure_response("No profile data to save")
        
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f, indent=2)
        
        return success_response(
            outputs={
                'saved': True,
                'user_id': user_id,
                'profile': profile_data
            },
            confidence=1.0,
            metadata={'sutra': 'sutra_076', 'version': '1.0.0'}
        )
    
    return failure_response(f"Unknown action: {action}")
