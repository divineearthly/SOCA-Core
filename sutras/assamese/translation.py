"""
sutra_033: Assamese Translation
Pramana: Shabda (Testimony)
Translates between Assamese and other languages
"""

def execute(inputs: dict, context: dict = None) -> dict:
    text = inputs.get('text', '')
    target = inputs.get('target', 'en')
    
    translations = {
        'rice': 'ধান',
        'water': 'পানী',
        'soil': 'মাটি',
        'crop': 'শস্য',
        'pest': 'পোক',
        'market': 'বজাৰ',
        'cattle': 'গৰু',
        'goat': 'ছাগলী',
        'poultry': 'কুকুৰা',
        'fertilizer': 'সাৰ',
        'harvest': 'খেতি',
        'farm': 'খেতি'
    }
    
    if target == 'as':
        # English to Assamese
        translated = translations.get(text.lower(), text)
    else:
        # Assamese to English
        reverse = {v: k for k, v in translations.items()}
        translated = reverse.get(text, text)
    
    return {
        "status": "success",
        "outputs": {
            "original": text,
            "translated": translated,
            "target_language": target
        },
        "trace": {
            "sutra_id": "sutra_033",
            "version": "1.0.0"
        }
    }
