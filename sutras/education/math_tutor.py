"""
sutra_087: Math Tutor
Pramana: Pratyaksha (Direct Perception)
Teaches math concepts step by step
"""

def execute(inputs: dict, context: dict = None) -> dict:
    concept = inputs.get('concept', '').lower()
    level = inputs.get('level', 'basic')
    
    concepts = {
        'addition': {
            'basic': 'Adding two numbers: 2 + 3 = 5',
            'intermediate': 'Adding larger numbers: 23 + 45 = 68',
            'advanced': 'Adding decimals: 2.5 + 3.7 = 6.2'
        },
        'subtraction': {
            'basic': 'Taking away: 5 - 3 = 2',
            'intermediate': 'Borrowing: 53 - 27 = 26',
            'advanced': 'Subtracting decimals: 5.3 - 2.7 = 2.6'
        },
        'multiplication': {
            'basic': 'Repeated addition: 3 × 4 = 12',
            'intermediate': 'Two-digit multiplication: 12 × 34 = 408',
            'advanced': 'Algebraic multiplication: (x+2)(x+3) = x²+5x+6'
        },
        'division': {
            'basic': 'Sharing equally: 12 ÷ 4 = 3',
            'intermediate': 'Long division: 144 ÷ 12 = 12',
            'advanced': 'Dividing polynomials: (x²+2x) ÷ x = x+2'
        }
    }
    
    result = concepts.get(concept, {'basic': 'I can teach: addition, subtraction, multiplication, division'})
    explanation = result.get(level, result.get('basic'))
    
    return {
        "status": "success",
        "outputs": {
            "concept": concept,
            "level": level,
            "explanation": explanation,
            "next_topic": get_next_topic(concept)
        },
        "trace": {
            "sutra_id": "sutra_087",
            "version": "1.0.0"
        }
    }

def get_next_topic(concept):
    topics = ['addition', 'subtraction', 'multiplication', 'division']
    if concept in topics:
        idx = topics.index(concept)
        return topics[(idx + 1) % len(topics)]
    return 'addition'
