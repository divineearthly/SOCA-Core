"""
sutra_037: Voice Command Handler
Pramana: Pratyaksha (Direct Perception)
Handles voice input for offline use
"""

def execute(inputs: dict, context: dict = None) -> dict:
    command = inputs.get('command', '')
    language = inputs.get('language', 'en')
    
    # Map voice commands to sutras
    command_map = {
        'crop': 'sutra_021',
        'weather': 'sutra_025',
        'pest': 'sutra_026',
        'water': 'sutra_027',
        'market': 'sutra_029',
        'fertilizer': 'sutra_030',
        'livestock': 'sutra_031',
        'math': 'sutra_022',
        'translate': 'sutra_024',
        'medicinal': 'sutra_023'
    }
    
    command_lower = command.lower()
    mapped_sutra = None
    
    for key, sutra_id in command_map.items():
        if key in command_lower:
            mapped_sutra = sutra_id
            break
    
    return {
        "status": "success",
        "outputs": {
            "command": command,
            "language": language,
            "sutra": mapped_sutra,
            "recognized": mapped_sutra is not None
        },
        "trace": {
            "sutra_id": "sutra_037",
            "version": "1.0.0"
        }
    }
