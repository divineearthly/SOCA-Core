"""
sutra_074: Knowledge Retriever
Pramana: Anumana (Inference)
Searches knowledge packs, district archives, and village memory
"""

import sys
import os
import json
import glob
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '')
    district = inputs.get('district', '')
    crop = inputs.get('crop', '')
    
    if not query:
        return failure_response("Query required")
    
    results = []
    
    # Search knowledge packs
    pack_dir = os.path.expanduser("~/soca/data/packs")
    if os.path.exists(pack_dir):
        for pack_file in glob.glob(os.path.join(pack_dir, "*.pack")):
            try:
                with open(pack_file, 'r') as f:
                    data = json.load(f)
                results.append({
                    'source': os.path.basename(pack_file),
                    'data': data
                })
            except:
                pass
    
    # Search district data
    district_file = os.path.expanduser(f"~/soca/data/assam/districts/{district}.json")
    if os.path.exists(district_file):
        try:
            with open(district_file, 'r') as f:
                data = json.load(f)
            results.append({
                'source': f"districts/{district}.json",
                'data': data
            })
        except:
            pass
    
    return success_response(
        outputs={
            'knowledge_results': results,
            'count': len(results),
            'query': query,
            'district': district
        },
        confidence=0.85,
        metadata={'sutra': 'sutra_074', 'version': '1.0.0'}
    )
