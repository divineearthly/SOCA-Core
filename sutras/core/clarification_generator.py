"""
sutra_078: Clarification Generator
Pramana: Anumana (Inference)
Generates follow-up questions for missing information
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '')
    intent = inputs.get('intent', 'general')
    working_memory = inputs.get('working_memory', {})
    
    missing = []
    questions = []
    
    # Check for location
    if not working_memory.get('context', {}).get('district'):
        missing.append('district')
        questions.append("Which district are you in?")
    
    # Check for season (agriculture)
    if intent == 'agriculture':
        if not working_memory.get('context', {}).get('season'):
            missing.append('season')
            questions.append("Which season are you planning to grow in? (kharif/rabi)")
        
        if not working_memory.get('profile', {}).get('soil_type'):
            missing.append('soil_type')
            questions.append("What type of soil do you have? (loamy/clay/sandy)")
    
    return success_response(
        outputs={
            'needs_clarification': len(missing) > 0,
            'missing': missing,
            'questions': questions,
            'question_count': len(questions)
        },
        confidence=0.9,
        metadata={'sutra': 'sutra_078', 'version': '1.0.0'}
    )
