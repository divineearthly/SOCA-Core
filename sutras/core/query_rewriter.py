"""
sutra_096: Query Rewriter
Pramana: Anumana (Inference)
Rewrites queries for better retrieval
"""

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '')
    intent = inputs.get('intent', 'general')
    
    if not query:
        return {"status": "failure", "outputs": {}, "trace": {"error": "Query required"}}
    
    original = query
    rewritten = query
    
    # Agriculture query expansion
    if intent == 'agriculture':
        expansions = {
            'crop': ['crop', 'plant', 'grow', 'cultivate', 'agriculture'],
            'rice': ['rice', 'paddy', 'sali', 'boro'],
            'pest': ['pest', 'insect', 'disease', 'bug'],
            'weather': ['weather', 'rainfall', 'climate', 'monsoon']
        }
        
        for key, terms in expansions.items():
            if key in query.lower():
                # Expand with synonyms
                for term in terms:
                    if term not in query.lower():
                        rewritten += f" {term}"
                break
    
    return {
        "status": "success",
        "outputs": {
            "original": original,
            "rewritten": rewritten,
            "expanded": rewritten != original
        },
        "trace": {
            "sutra_id": "sutra_096",
            "version": "1.0.0"
        }
    }
