"""
sutra_034: Assamese Voice Commands
Pramana: Pratyaksha (Direct Perception)
Simple voice command mapping
"""

def execute(inputs: dict, context: dict = None) -> dict:
    command = inputs.get('command', '')
    
    command_map = {
        'crop': 'crop_advisor',
        'weather': 'weather_advisor',
        'pest': 'pest_detection',
        'water': 'water_management',
        'market': 'market_advisor',
        'fertilizer': 'fertilizer_advisor',
        'livestock': 'livestock_advisor'
    }
    
    command_lower = command.lower()
    mapped = None
    
    for key, value in command_map.items():
        if key in command_lower:
            mapped = value
            break
    
    return {
        "status": "success",
        "outputs": {
            "command": command,
            "sutra": mapped,
            "recognized": mapped is not None,
            "language": "assamese"
        },
        "trace": {
            "sutra_id": "sutra_034",
            "version": "1.0.0"
        }
    }
