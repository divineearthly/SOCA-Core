"""
sutra_032: Assamese NLU (Natural Language Understanding)
Pramana: Shabda (Testimony)
Parses Assamese queries and extracts intent
"""

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '')
    
    # Simple Assamese keyword mapping
    assamese_keywords = {
        'ধান': 'rice',
        'পিঠা': 'rice',
        'কঠিন': 'cotton',
        'গম': 'wheat',
        'আঠা': 'sugarcane',
        'মাটি': 'soil',
        'বৰষুণ': 'rainfall',
        'পোক': 'pest',
        'শাক': 'vegetable',
        'গৰু': 'cattle',
        'ছাগলী': 'goat',
        'কুকুৰা': 'poultry',
        'মাছ': 'fish',
        'বজাৰ': 'market',
        'দাম': 'price',
        'পানী': 'water',
        'ভূমি': 'land',
        'শস্য': 'crop'
    }
    
    extracted = {}
    query_lower = query.lower()
    
    for as_word, en_word in assamese_keywords.items():
        if as_word in query_lower:
            if 'crop' not in extracted:
                extracted['crop'] = en_word
            elif 'soil' not in extracted:
                extracted['soil'] = en_word
    
    return {
        "status": "success",
        "outputs": {
            "original_query": query,
            "extracted": extracted,
            "language": "assamese",
            "confidence": 0.8 if extracted else 0.3
        },
        "trace": {
            "sutra_id": "sutra_032",
            "version": "1.0.0"
        }
    }
