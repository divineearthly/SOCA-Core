"""
sutra_056: Crop Rotation Advisor
Pramana: Anumana (Inference)
Recommends crop rotation based on history and soil
"""

def execute(inputs: dict, context: dict = None) -> dict:
    soil_type = inputs.get('soil_type', '').lower()
    crop_history = inputs.get('crop_history', [])
    district = inputs.get('district', '')
    
    # Rotation rules
    rotation_rules = {
        'rice': {
            'next': ['Mustard', 'Black Gram', 'Pulses'],
            'reason': 'Legumes fix nitrogen after rice'
        },
        'mustard': {
            'next': ['Rice', 'Wheat', 'Gram'],
            'reason': 'Rice follows mustard well'
        },
        'wheat': {
            'next': ['Pulses', 'Rice', 'Cotton'],
            'reason': 'Pulses restore soil nutrients'
        },
        'cotton': {
            'next': ['Wheat', 'Pulses', 'Rice'],
            'reason': 'Cotton depletes nutrients, pulses restore'
        },
        'sugarcane': {
            'next': ['Pulses', 'Rice', 'Wheat'],
            'reason': 'Sugarcane exhausts soil, need legumes'
        },
        'pulses': {
            'next': ['Rice', 'Wheat', 'Mustard'],
            'reason': 'Pulses enrich soil for cereals'
        }
    }
    
    # Get current crop (last in history)
    current_crop = crop_history[-1].lower() if crop_history else ''
    
    if current_crop in rotation_rules:
        rule = rotation_rules[current_crop]
        next_crops = rule['next']
        reason = rule['reason']
    else:
        next_crops = ['Rice', 'Pulses', 'Mustard']
        reason = 'General rotation: cereals followed by legumes'
    
    # Soil-specific adjustment
    if soil_type == 'sandy':
        next_crops = ['Pulses', 'Groundnut', 'Millet']
        reason = 'Sandy soil benefits from legume rotation'
    elif soil_type == 'clay':
        next_crops = ['Rice', 'Wheat', 'Jute']
        reason = 'Clay soil supports cereal rotation'
    
    return {
        "status": "success",
        "outputs": {
            "current_crop": current_crop,
            "recommended_crops": next_crops[:3],
            "reason": reason,
            "soil_type": soil_type,
            "crop_history": crop_history
        },
        "trace": {
            "sutra_id": "sutra_056",
            "version": "1.0.0"
        }
    }
