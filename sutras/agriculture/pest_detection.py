"""
Sutra_026: Pest Detection
Pramana: Anumana (Inference)
Identifies pests based on crop and symptoms
"""

def execute(inputs: dict, context: dict = None) -> dict:
    crop = inputs.get('crop', '').lower()
    symptoms = inputs.get('symptoms', '').lower()
    
    pest_data = {
        'rice': {
            'yellowing leaves': {
                'pest': 'Leafhopper',
                'treatment': 'Neem oil spray, remove infected plants',
                'prevention': 'Plant resistant varieties'
            },
            'holes in leaves': {
                'pest': 'Stem borer',
                'treatment': 'Apply neem cake, biological control',
                'prevention': 'Crop rotation'
            }
        },
        'cotton': {
            'white spots': {
                'pest': 'Whitefly',
                'treatment': 'Neem oil spray, trap crops',
                'prevention': 'Intercropping'
            },
            'yellowing': {
                'pest': 'Aphids',
                'treatment': 'Soap water spray',
                'prevention': 'Natural predators'
            }
        }
    }
    
    crop_data = pest_data.get(crop, {})
    pest_info = crop_data.get(symptoms, {
        'pest': 'Unknown',
        'treatment': 'Consult local agricultural officer',
        'prevention': 'Regular monitoring'
    })
    
    return {
        "status": "success",
        "outputs": {
            "crop": crop,
            "symptoms": symptoms,
            "pest": pest_info['pest'],
            "treatment": pest_info['treatment'],
            "prevention": pest_info['prevention']
        },
        "trace": {
            "sutra_id": "sutra_026",
            "version": "1.0.0"
        }
    }
