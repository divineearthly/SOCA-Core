"""
sutra_081: Generic Slot Extractor
Pramana: Anumana (Inference)
Extracts slots from natural language query
"""

import sys
import re
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '').lower()
    
    if not query:
        return failure_response("Query required")
    
    slots = {
        'season': None,
        'district': None,
        'soil_type': None,
        'crop': None,
        'intent': None
    }
    
    # Extract season
    season_patterns = {
        'kharif': ['kharif', 'monsoon', 'rainy', 'july', 'august', 'september'],
        'rabi': ['rabi', 'winter', 'october', 'november', 'december', 'january', 'february'],
        'summer': ['summer', 'march', 'april', 'may', 'june'],
        'winter': ['winter', 'december', 'january', 'february']
    }
    
    for season, keywords in season_patterns.items():
        for kw in keywords:
            if kw in query:
                slots['season'] = season
                break
        if slots['season']:
            break
    
    # Extract district
    districts = [
        'bongaigaon', 'barpeta', 'jorhat', 'nagaon', 'dibrugarh',
        'sonitpur', 'dhubri', 'goalpara', 'kokrajhar', 'tinsukia',
        'sivasagar', 'golaghat', 'lakhimpur', 'dhemaji', 'morigaon',
        'nalbari', 'kamrup', 'cachar', 'hailakandi', 'karimganj',
        'karbi_anglong', 'dima_hasao', 'chirang', 'udalguri', 'baksa'
    ]
    
    for district in districts:
        if district in query:
            slots['district'] = district
            break
    
    # Extract soil type
    soils = ['loamy', 'clay', 'sandy', 'alluvial', 'laterite']
    for soil in soils:
        if soil in query:
            slots['soil_type'] = soil
            break
    
    # Extract crop
    crops = ['rice', 'wheat', 'cotton', 'sugarcane', 'tea', 'jute', 
             'mustard', 'gram', 'lentils', 'potato', 'onion', 'maize']
    for crop in crops:
        if crop in query:
            slots['crop'] = crop
            break
    
    # Extract intent (simple classification)
    if any(word in query for word in ['crop', 'plant', 'grow', 'farm']):
        slots['intent'] = 'agriculture'
    elif any(word in query for word in ['translate', 'meaning', 'word']):
        slots['intent'] = 'translation'
    elif any(word in query for word in ['math', 'add', 'subtract']):
        slots['intent'] = 'education'
    elif any(word in query for word in ['price', 'market', 'sell']):
        slots['intent'] = 'market'
    
    return success_response(
        outputs={
            'slots': slots,
            'query': query,
            'extracted_count': sum(1 for v in slots.values() if v)
        },
        confidence=0.9,
        metadata={'sutra': 'sutra_081', 'version': '1.0.0'}
    )
