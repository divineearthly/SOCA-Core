"""
sutra_021: Crop Advisor
Pramana: Anumana (Inference)
Provides crop recommendations based on soil, season, and location
"""

def execute(inputs: dict, context: dict = None) -> dict:
    soil_type = inputs.get('soil_type', '').lower()
    season = inputs.get('season', '').lower()
    location = inputs.get('location', '').lower()
    
    # Assam-specific recommendations
    assam_crops = {
        'loamy': {
            'kharif': ['Rice (Boro/Sali)', 'Jute', 'Sugarcane', 'Tea'],
            'rabi': ['Mustard', 'Wheat', 'Gram', 'Lentils'],
            'summer': ['Summer Rice', 'Vegetables', 'Pulses']
        },
        'clay': {
            'kharif': ['Rice (Boro)', 'Jute', 'Paddy'],
            'rabi': ['Wheat', 'Lentils', 'Peas'],
            'summer': ['Summer Rice', 'Jute']
        },
        'sandy': {
            'kharif': ['Groundnut', 'Millets', 'Pulses'],
            'rabi': ['Potato', 'Onion', 'Carrot', 'Peas'],
            'summer': ['Watermelon', 'Cucumber', 'Pulses']
        }
    }
    
    # Check if Assam
    if 'assam' in location or 'axom' in location:
        crops = assam_crops.get(soil_type, {}).get(season, ['Rice (Sali)', 'Tea'])
    else:
        # Generic recommendations
        generic = {
            ('loamy', 'kharif'): ['Rice', 'Cotton', 'Sugarcane'],
            ('loamy', 'rabi'): ['Wheat', 'Gram', 'Mustard'],
            ('clay', 'kharif'): ['Rice', 'Jute', 'Paddy'],
            ('clay', 'rabi'): ['Wheat', 'Lentils', 'Peas'],
            ('sandy', 'kharif'): ['Groundnut', 'Millets', 'Pulses'],
            ('sandy', 'rabi'): ['Potato', 'Onion', 'Carrot']
        }
        crops = generic.get((soil_type, season), ['Consult local agricultural officer'])
    
    return {
        "status": "success",
        "outputs": {
            "crops": crops,
            "soil_type": soil_type,
            "season": season,
            "location": location,
            "advice": f"For {location}, recommended crops: {', '.join(crops)}"
        },
        "trace": {
            "sutra_id": "sutra_021",
            "version": "1.0.0"
        }
    }
