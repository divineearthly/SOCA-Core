"""
Sutra_025: Weather Advisor
Pramana: Anumana (Inference)
Provides weather-based farming advice
"""

def execute(inputs: dict, context: dict = None) -> dict:
    location = inputs.get('location', '')
    season = inputs.get('season', '').lower()
    
    # Simple seasonal weather patterns for India
    weather_patterns = {
        'kharif': {
            'rainfall': 'High (monsoon)',
            'advice': 'Plant rice, cotton, sugarcane. Ensure good drainage.',
            'risks': ['Flooding', 'Pest outbreaks']
        },
        'rabi': {
            'rainfall': 'Low',
            'advice': 'Plant wheat, gram, mustard. Irrigate regularly.',
            'risks': ['Frost damage', 'Water scarcity']
        },
        'summer': {
            'rainfall': 'Minimal',
            'advice': 'Plant heat-tolerant crops. Provide shade and irrigation.',
            'risks': ['Heat stress', 'Water scarcity']
        },
        'winter': {
            'rainfall': 'Low to moderate',
            'advice': 'Plant winter vegetables. Protect from cold.',
            'risks': ['Frost damage', 'Pest outbreaks']
        }
    }
    
    season_info = weather_patterns.get(season, {
        'rainfall': 'Unknown',
        'advice': 'Consult local agricultural officer',
        'risks': ['Unknown']
    })
    
    return {
        "status": "success",
        "outputs": {
            "location": location,
            "season": season,
            "rainfall": season_info['rainfall'],
            "advice": season_info['advice'],
            "risks": season_info['risks']
        },
        "trace": {
            "sutra_id": "sutra_025",
            "version": "1.0.0"
        }
    }
