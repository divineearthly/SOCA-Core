"""
Sutra 024: Basic Translator
Pramana: Shabda (Testimony)
Simple translations between languages
"""

def execute(inputs: dict, context: dict = None) -> dict:
    word = inputs.get('word', '').lower()
    target = inputs.get('target_lang', 'hi')
    
    translations = {
        'hello': {'hi': 'नमस्ते', 'bn': 'নমস্কার', 'as': 'নমস্কাৰ', 'sa': 'नमः'},
        'water': {'hi': 'पानी', 'bn': 'পানি', 'as': 'পানী', 'sa': 'जलम्'},
        'food': {'hi': 'भोजन', 'bn': 'খাদ্য', 'as': 'আহাৰ', 'sa': 'अन्नम्'},
        'earth': {'hi': 'पृथ्वी', 'bn': 'পৃথিবী', 'as': 'পৃথিৱী', 'sa': 'पृथ्वी'},
        'sky': {'hi': 'आकाश', 'bn': 'আকাশ', 'as': 'আকাশ', 'sa': 'आकाशः'},
        'friend': {'hi': 'मित्र', 'bn': 'বন্ধু', 'as': 'বন্ধু', 'sa': 'मित्रम्'}
    }
    
    result = translations.get(word, {})
    output = result.get(target, f'Word "{word}" not found for {target}')
    
    return {
        "status": "success",
        "outputs": {
            "word": word,
            "target_lang": target,
            "translation": output
        },
        "trace": {
            "sutra_id": "sutra_024",
            "version": "1.0.0"
        }
    }
