"""
sutra_083: Structured Critic
Pramana: Anumana (Inference)
Returns structured repair actions, not string parsing
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
    actions = []
    
    # Check 1: Source count
    if len(sources) < 2:
        weaknesses.append("Insufficient sources")
        actions.append({
            "type": "retrieve",
            "strategy": "semantic",
            "reason": "Need more evidence to support answer"
        })
    
    # Check 2: Answer length
    if len(answer) < 50:
        weaknesses.append("Answer too brief")
        actions.append({
            "type": "expand",
            "strategy": "detail",
            "reason": "Add more specific information"
        })
    
    # Check 3: Missing slots for agriculture
    if intent == 'agriculture':
        if not slots.get('soil_type'):
            weaknesses.append("Soil type missing")
            actions.append({
                "type": "ask",
                "slot": "soil_type",
                "reason": "Soil type affects crop selection"
            })
        if not slots.get('district'):
            weaknesses.append("District missing")
            actions.append({
                "type": "ask",
                "slot": "district",
                "reason": "District affects climate and crop suitability"
            })
    
    # Check 4: Vague recommendations
    vague_words = ['consult', 'officer', 'expert', 'unknown']
    if any(word in answer.lower() for word in vague_words):
        weaknesses.append("Contains vague recommendations")
        actions.append({
            "type": "specific",
            "strategy": "detail",
            "reason": "Provide concrete actionable advice"
        })
    
    # Check 5: No specific crop
    crops = ['rice', 'wheat', 'cotton', 'sugarcane', 'tea', 'jute', 'mustard']
    if intent == 'agriculture' and not any(crop in answer.lower() for crop in crops):
        weaknesses.append("No specific crop recommended")
        actions.append({
            "type": "specific",
            "strategy": "crop",
            "reason": "Recommend specific crops for the region"
        })
    
    # Calculate critic score
    quality = 1.0 - (len(weaknesses) * 0.12)
    quality = max(0.0, min(1.0, quality))
    
    return success_response(
        outputs={
            'quality': round(quality, 2),
            'weaknesses': weaknesses,
            'actions': actions,
            'action_count': len(actions),
            'source_count': len(sources),
            'answer_length': len(answer)
        },
        confidence=quality,
        metadata={'sutra': 'sutra_083', 'version': '1.0.0'}
    )
