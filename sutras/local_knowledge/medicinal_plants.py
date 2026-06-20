"""
Sutra 023: Medicinal Plants
Pramana: Shabda (Testimony)
Traditional medicinal knowledge
"""

def execute(inputs: dict, context: dict = None) -> dict:
    plant = inputs.get('plant', '').lower()
    
    plants = {
        'tulsi': 'Tulsi (Holy Basil): Used for cough, cold, and respiratory issues. Chew leaves or make tea.',
        'neem': 'Neem: Antibacterial and antifungal. Used for skin conditions and dental care.',
        'aloe vera': 'Aloe Vera: Soothes burns and skin irritation. Gel applied topically.',
        'ginger': 'Ginger: Aids digestion, reduces nausea, and has anti-inflammatory properties.',
        'turmeric': 'Turmeric: Anti-inflammatory and antioxidant. Used in cooking and as a remedy.',
        'amla': 'Amla (Indian Gooseberry): Rich in Vitamin C, boosts immunity and aids digestion.'
    }
    
    info = plants.get(plant, f'I have information about: {", ".join(plants.keys())}')
    
    return {
        "status": "success",
        "outputs": {
            "plant": plant,
            "information": info
        },
        "trace": {
            "sutra_id": "sutra_023",
            "version": "1.0.0",
            "pramana": "shabda"
        }
    }
