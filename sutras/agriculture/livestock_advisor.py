"""
sutra_031: Livestock Advisor
Pramana: Shabda (Testimony)
Provides advice on cattle, goat, and poultry farming
"""

def execute(inputs: dict, context: dict = None) -> dict:
    animal = inputs.get('animal', '').lower()
    query = inputs.get('query', '').lower()
    
    livestock_data = {
        'cattle': {
            'feed': 'Green fodder, concentrate, mineral mixture',
            'health': 'Vaccination, deworming, clean water',
            'shelter': 'Ventilated shed, dry bedding',
            'breed': 'Gir, Sahiwal, Jersey, Holstein'
        },
        'goat': {
            'feed': 'Tree leaves, concentrate, minerals',
            'health': 'Foot rot prevention, deworming',
            'shelter': 'Raised floor, dry environment',
            'breed': 'Sirohi, Beetal, Jamunapari, Boer'
        },
        'poultry': {
            'feed': 'Layer/grower feed, clean water',
            'health': 'Vaccination, biosecurity',
            'shelter': 'Dry, ventilated coop',
            'breed': 'Vanaraja, Kuroiler, Rhode Island Red'
        }
    }
    
    animal_info = livestock_data.get(animal, {
        'feed': 'Consult local veterinary officer',
        'health': 'Regular checkups recommended',
        'shelter': 'Clean, dry shelter',
        'breed': 'Local breeds available'
    })
    
    if 'feed' in query:
        output = f"Feed for {animal}: {animal_info['feed']}"
    elif 'health' in query or 'disease' in query:
        output = f"Health advice for {animal}: {animal_info['health']}"
    elif 'shelter' in query or 'housing' in query:
        output = f"Shelter for {animal}: {animal_info['shelter']}"
    elif 'breed' in query:
        output = f"Breeds for {animal}: {animal_info['breed']}"
    else:
        output = f"Livestock advice for {animal}: Feed: {animal_info['feed']}, Health: {animal_info['health']}"
    
    return {
        "status": "success",
        "outputs": {
            "animal": animal,
            "advice": output,
            "details": animal_info
        },
        "trace": {
            "sutra_id": "sutra_031",
            "version": "1.0.0"
        }
    }
