"""
Sutra_027: Water Management
Pramana: Anumana (Inference)
Provides irrigation advice based on soil and rainfall
"""

def execute(inputs: dict, context: dict = None) -> dict:
    soil_type = inputs.get('soil_type', '').lower()
    rainfall = inputs.get('rainfall', 0)
    
    soil_properties = {
        'sandy': {
            'water_holding': 'Low',
            'irrigation_frequency': 'Frequent, light irrigation',
            'advice': 'Use drip irrigation, add organic matter'
        },
        'loamy': {
            'water_holding': 'Medium',
            'irrigation_frequency': 'Moderate irrigation',
            'advice': 'Maintain consistent moisture'
        },
        'clay': {
            'water_holding': 'High',
            'irrigation_frequency': 'Less frequent, deep irrigation',
            'advice': 'Ensure good drainage'
        }
    }
    
    soil_info = soil_properties.get(soil_type, {
        'water_holding': 'Unknown',
        'irrigation_frequency': 'Consult local expert',
        'advice': 'Conduct soil test'
    })
    
    return {
        "status": "success",
        "outputs": {
            "soil_type": soil_type,
            "rainfall": rainfall,
            "water_holding": soil_info['water_holding'],
            "irrigation_frequency": soil_info['irrigation_frequency'],
            "advice": soil_info['advice']
        },
        "trace": {
            "sutra_id": "sutra_027",
            "version": "1.0.0"
        }
    }
