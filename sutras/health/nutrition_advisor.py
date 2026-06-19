"""
sutra_088: Nutrition Advisor
Pramana: Shabda (Testimony)
Provides nutritional advice
"""

def execute(inputs: dict, context: dict = None) -> dict:
    age = inputs.get('age', 30)
    activity = inputs.get('activity', 'moderate')
    goal = inputs.get('goal', 'maintain')
    
    nutrition = {
        'calories': {
            'sedentary': age * 24 * 0.9,
            'moderate': age * 24 * 1.1,
            'active': age * 24 * 1.3
        },
        'protein': {
            'maintain': '0.8g per kg body weight',
            'build': '1.6g per kg body weight',
            'lose': '1.2g per kg body weight'
        },
        'water': '2-3 liters per day',
        'vegetables': '5 servings per day'
    }
    
    calorie_estimate = nutrition['calories'].get(activity, age * 24 * 1.1)
    
    return {
        "status": "success",
        "outputs": {
            "estimated_calories": round(calorie_estimate),
            "protein_advice": nutrition['protein'].get(goal, nutrition['protein']['maintain']),
            "water": nutrition['water'],
            "vegetables": nutrition['vegetables']
        },
        "trace": {
            "sutra_id": "sutra_088",
            "version": "1.0.0"
        }
    }
