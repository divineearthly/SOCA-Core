"""
sutra_044: District Intelligence
Pramana: Anumana (Inference)
Provides district-specific agriculture advice
"""

import os
import json

def execute(inputs: dict, context: dict = None) -> dict:
    district = inputs.get('district', '').lower()
    
    if not district:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_044",
                "version": "1.0.0",
                "error": "District required"
            }
        }
    
    # Load district data
    district_path = os.path.expanduser(f"~/soca/data/assam/districts/{district}.json")
    
    if not os.path.exists(district_path):
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_044",
                "version": "1.0.0",
                "error": f"District {district} not found"
            }
        }
    
    with open(district_path, 'r') as f:
        data = json.load(f)
    
    # Add recommendations
    recommendations = {
        'bongaigaon': {
            'crops': ['Rice (Sali)', 'Jute', 'Mustard'],
            'advice': 'Focus on rice cultivation. Use raised beds for drainage.'
        },
        'barpeta': {
            'crops': ['Rice (Boro)', 'Jute', 'Vegetables'],
            'advice': 'High flood risk. Use flood-tolerant rice varieties.'
        },
        'jorhat': {
            'crops': ['Rice', 'Tea', 'Sugarcane'],
            'advice': 'Good for tea cultivation. Acidic soil suitable.'
        }
    }
    
    district_recommendation = recommendations.get(district, {
        'crops': data.get('major_crops', ['Consult local officer']),
        'advice': 'Consult local agricultural officer for specific advice.'
    })
    
    return {
        "status": "success",
        "outputs": {
            "district": district,
            "soil_type": data.get('soil_type', 'Unknown'),
            "rainfall": data.get('rainfall', 'Unknown'),
            "major_crops": data.get('major_crops', []),
            "flood_risk": data.get('flood_risk', 'Unknown'),
            "recommended_crops": district_recommendation['crops'],
            "advice": district_recommendation['advice']
        },
        "trace": {
            "sutra_id": "sutra_044",
            "version": "1.0.0"
        }
    }
