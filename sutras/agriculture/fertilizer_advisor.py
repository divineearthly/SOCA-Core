"""
sutra_030: Fertilizer Advisor
Pramana: Anumana (Inference)
Recommends fertilizers based on soil and crop
"""

def execute(inputs: dict, context: dict = None) -> dict:
    soil_type = inputs.get('soil_type', '').lower()
    crop = inputs.get('crop', '').lower()
    
    fertilizer_data = {
        'loamy': {
            'rice': 'NPK 10:20:10, organic manure',
            'cotton': 'NPK 20:10:10, gypsum',
            'wheat': 'NPK 12:24:12, DAP',
            'sugarcane': 'NPK 10:10:20, organic compost'
        },
        'clay': {
            'rice': 'NPK 10:10:10, organic matter',
            'cotton': 'NPK 15:15:15, gypsum',
            'wheat': 'NPK 10:20:10, lime'
        },
        'sandy': {
            'rice': 'NPK 15:15:15, frequent small doses',
            'cotton': 'NPK 20:10:10, organic manure',
            'wheat': 'NPK 12:12:12, compost'
        }
    }
    
    soil_crops = fertilizer_data.get(soil_type, {})
    recommendation = soil_crops.get(crop, 'NPK 10:10:10, consult local expert')
    
    return {
        "status": "success",
        "outputs": {
            "soil_type": soil_type,
            "crop": crop,
            "recommendation": recommendation,
            "advice": "Apply fertilizer based on soil test results"
        },
        "trace": {
            "sutra_id": "sutra_030",
            "version": "1.0.0"
        }
    }
