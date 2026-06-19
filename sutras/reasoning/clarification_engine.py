"""
sutra_046: Clarification Engine
Pramana: Anumana (Inference)
Detects missing information and asks follow-up questions
"""

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '').lower()
    intent = inputs.get('intent', 'general')
    
    if not query:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_046",
                "version": "1.0.0",
                "error": "Query required"
            }
        }
    
    missing = []
    follow_up = []
    
    # Check for location
    locations = ['assam', 'bongaigaon', 'barpeta', 'jorhat', 'dibrugarh', 'tinsukia', 
                'goalpara', 'nagaon', 'silchar', 'tezpur', 'guwahati']
    has_location = any(loc in query for loc in locations)
    
    if not has_location and intent in ['agriculture', 'market']:
        missing.append('location')
        follow_up.append("Which district or village are you in?")
    
    # Check for season (agriculture)
    if intent == 'agriculture':
        seasons = ['kharif', 'rabi', 'summer', 'winter', 'monsoon']
        has_season = any(season in query for season in seasons)
        
        if not has_season:
            missing.append('season')
            follow_up.append("Which season are you planning to grow? (kharif/rabi/summer)")
    
    return {
        "status": "success",
        "outputs": {
            "query": query,
            "intent": intent,
            "missing": missing,
            "follow_up": follow_up,
            "needs_clarification": len(missing) > 0
        },
        "trace": {
            "sutra_id": "sutra_046",
            "version": "1.0.0"
        }
    }
