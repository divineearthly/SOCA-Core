"""
sutra_057: Yield Predictor
Pramana: Anumana (Inference)
Predicts crop yield based on district and conditions
"""

def execute(inputs: dict, context: dict = None) -> dict:
    district = inputs.get('district', '').lower()
    crop = inputs.get('crop', '').lower()
    rainfall = inputs.get('rainfall', 'normal')
    soil_type = inputs.get('soil_type', '')
    
    # Base yields by district (Assam)
    district_yields = {
        'bongaigaon': {
            'rice': 3.0,
            'jute': 2.2,
            'mustard': 1.0
        },
        'barpeta': {
            'rice': 3.5,
            'jute': 2.5,
            'mustard': 1.2
        },
        'jorhat': {
            'rice': 3.2,
            'tea': 1.8,
            'sugarcane': 45.0
        },
        'dibrugarh': {
            'rice': 3.0,
            'tea': 2.0,
            'mustard': 1.0
        }
    }
    
    # Get base yield
    district_data = district_yields.get(district, {})
    base_yield = district_data.get(crop, 2.5)
    
    # Adjust for rainfall
    rainfall_factors = {
        'low': 0.7,
        'normal': 1.0,
        'high': 1.2,
        'very_high': 1.0
    }
    rainfall_factor = rainfall_factors.get(rainfall, 1.0)
    
    # Adjust for soil
    soil_factors = {
        'loamy': 1.1,
        'clay': 1.0,
        'sandy': 0.7,
        'alluvial': 1.05
    }
    soil_factor = soil_factors.get(soil_type, 1.0)
    
    # Calculate predicted yield
    predicted_yield = base_yield * rainfall_factor * soil_factor
    
    return {
        "status": "success",
        "outputs": {
            "crop": crop,
            "district": district,
            "base_yield": round(base_yield, 1),
            "predicted_yield": round(predicted_yield, 1),
            "unit": "tons/hectare",
            "factors": {
                "rainfall": rainfall,
                "soil": soil_type,
                "rainfall_factor": rainfall_factor,
                "soil_factor": soil_factor
            }
        },
        "trace": {
            "sutra_id": "sutra_057",
            "version": "1.0.0"
        }
    }
