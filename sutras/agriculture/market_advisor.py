"""
sutra_029: Market Advisor
Pramana: Shabda (Testimony)
Provides market prices and recommendations for crops
"""

def execute(inputs: dict, context: dict = None) -> dict:
    crop = inputs.get('crop', '').lower()
    location = inputs.get('location', 'Assam')
    
    market_data = {
        'rice': {
            'price': '₹22-28 per kg',
            'trend': 'Stable',
            'best_market': 'Guwahati, Jorhat',
            'profit_margin': 'Good',
            'advice': 'Sell in urban markets for better price'
        },
        'cotton': {
            'price': '₹5500-6500 per quintal',
            'trend': 'Rising',
            'best_market': 'Maharashtra, Gujarat',
            'profit_margin': 'High',
            'advice': 'Store if price is low, sell when high'
        },
        'sugarcane': {
            'price': '₹350-400 per quintal',
            'trend': 'Stable',
            'best_market': 'Sugar mills, local mandi',
            'profit_margin': 'Medium',
            'advice': 'Contract with sugar mills for better price'
        },
        'wheat': {
            'price': '₹1800-2200 per quintal',
            'trend': 'Slight increase',
            'best_market': 'Punjab, UP mandis',
            'profit_margin': 'Medium',
            'advice': 'Sell during harvest season'
        },
        'groundnut': {
            'price': '₹5000-6000 per quintal',
            'trend': 'High demand',
            'best_market': 'Gujarat, Tamil Nadu',
            'profit_margin': 'Good',
            'advice': 'Oil extraction gives better returns'
        }
    }
    
    crop_info = market_data.get(crop, {
        'price': 'Price varies',
        'trend': 'Check local mandi',
        'best_market': 'Local market',
        'profit_margin': 'Unknown',
        'advice': 'Consult local agricultural officer'
    })
    
    return {
        "status": "success",
        "outputs": {
            "crop": crop,
            "price": crop_info['price'],
            "trend": crop_info['trend'],
            "best_market": crop_info['best_market'],
            "profit_margin": crop_info['profit_margin'],
            "advice": crop_info['advice']
        },
        "trace": {
            "sutra_id": "sutra_029",
            "version": "1.0.0"
        }
    }
