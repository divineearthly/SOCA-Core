"""
sutra_035: Market Intelligence
Pramana: Shabda (Testimony)
Advanced market data for Assam
"""

def execute(inputs: dict, context: dict = None) -> dict:
    crop = inputs.get('crop', '').lower()
    
    assam_market_data = {
        'rice': {
            'price': '₹22-28 per kg',
            'trend': 'Stable',
            'demand': 'High',
            'best_mandi': 'Guwahati, Jorhat',
            'export_potential': 'Medium',
            'storage': '6-12 months'
        },
        'tea': {
            'price': '₹150-300 per kg',
            'trend': 'Rising',
            'demand': 'Very High',
            'best_mandi': 'Dibrugarh, Jorhat',
            'export_potential': 'High',
            'storage': '12-24 months'
        },
        'sugarcane': {
            'price': '₹350-400 per quintal',
            'trend': 'Stable',
            'demand': 'High',
            'best_mandi': 'Kaziranga, Golaghat',
            'export_potential': 'Low',
            'storage': '1-2 weeks'
        },
        'cotton': {
            'price': '₹5500-6500 per quintal',
            'trend': 'Rising',
            'demand': 'High',
            'best_mandi': 'Guwahati',
            'export_potential': 'Medium',
            'storage': '12+ months'
        }
    }
    
    crop_info = assam_market_data.get(crop, {
        'price': 'Check local mandi',
        'trend': 'Unknown',
        'demand': 'Unknown',
        'best_mandi': 'Local market',
        'export_potential': 'Unknown',
        'storage': 'Consult expert'
    })
    
    return {
        "status": "success",
        "outputs": {
            "crop": crop,
            "assam_price": crop_info['price'],
            "trend": crop_info['trend'],
            "demand": crop_info['demand'],
            "best_mandi": crop_info['best_mandi'],
            "export_potential": crop_info['export_potential'],
            "storage": crop_info['storage'],
            "advice": f"For {crop}, sell when demand is high. Store properly in dry conditions."
        },
        "trace": {
            "sutra_id": "sutra_035",
            "version": "1.0.0"
        }
    }
