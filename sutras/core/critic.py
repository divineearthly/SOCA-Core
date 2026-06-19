"""
sutra_082: Answer Critic
Pramana: Anumana (Inference)
Critiques answer quality and identifies weaknesses
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    answer = inputs.get('answer', '')
    sources = inputs.get('sources', [])
    slots = inputs.get('slots', {})
    intent = inputs.get('intent', 'general')
    
    if not answer:
        return failure_response("No answer to critique")
    
    weaknesses = []
    repair_actions = []
    
    # Check 1: Answer length
    if len(answer) < 50:
        weaknesses.append("Answer is too short")
        repair_actions.append("Add more detail from sources")
    
    # Check 2: Source count
    if len(sources) < 2:
        weaknesses.append("Insufficient sources")
        repair_actions.append("Retrieve more knowledge")
    
    # Check 3: Missing slots for agriculture
    if intent == 'agriculture':
        if not slots.get('soil_type'):
            weaknesses.append("Soil type not specified")
            repair_actions.append("Ask for soil type")
        if not slots.get('district'):
            weaknesses.append("District not specified")
            repair_actions.append("Ask for district")
    
    # Check 4: Generic improvements
    if any(word in answer.lower() for word in ['unknown', 'consult', 'officer']):
        weaknesses.append("Contains vague recommendations")
        repair_actions.append("Provide specific actionable advice")
    
    # Check 5: No specific crop mentioned
    if 'rice' not in answer.lower() and 'wheat' not in answer.lower() and 'cotton' not in answer.lower():
        if intent == 'agriculture':
            weaknesses.append("No specific crop recommended")
            repair_actions.append("Recommend specific crops")
    
    # Generate critique
    quality = "Good"
    if len(weaknesses) >= 3:
        quality = "Poor"
    elif len(weaknesses) >= 1:
        quality = "Needs Improvement"
    
    return success_response(
        outputs={
            'quality': quality,
            'weaknesses': weaknesses,
            'repair_actions': repair_actions,
            'source_count': len(sources),
            'answer_length': len(answer)
        },
        confidence=0.8 if quality == "Good" else 0.5,
        metadata={'sutra': 'sutra_082', 'version': '1.0.0'}
    )
