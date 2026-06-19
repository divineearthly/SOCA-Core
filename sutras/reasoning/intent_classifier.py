"""
sutra_045: Intent Classifier
Pramana: Anumana (Inference)
Classifies user intent into domains
"""

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '').lower()
    
    if not query:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_045",
                "version": "1.0.0",
                "error": "Query required"
            }
        }
    
    # Domain keywords
    domains = {
        'agriculture': ['crop', 'plant', 'grow', 'soil', 'fertilizer', 'pest', 'water', 'irrigation', 'farm', 'harvest', 'yield'],
        'education': ['math', 'addition', 'subtraction', 'multiplication', 'division', 'science', 'learn', 'study'],
        'translation': ['translate', 'meaning', 'word', 'language', 'hindi', 'assamese', 'bengali', 'sanskrit'],
        'medicinal': ['tulsi', 'neem', 'ginger', 'turmeric', 'amla', 'medicinal', 'plant', 'health', 'remedy'],
        'market': ['price', 'sell', 'buy', 'market', 'mandi', 'rate', 'cost', 'profit'],
        'livestock': ['cattle', 'goat', 'poultry', 'cow', 'buffalo', 'animal'],
        'weather': ['rain', 'rainfall', 'weather', 'monsoon', 'climate', 'temperature'],
        'knowledge_search': ['search', 'find', 'look', 'what is', 'tell me about']
    }
    
    # Score each domain
    scores = {}
    for domain, keywords in domains.items():
        score = 0
        for keyword in keywords:
            if keyword in query:
                score += 1
        if score > 0:
            scores[domain] = score / len(keywords)
    
    # Find best domain
    if scores:
        best_domain = max(scores, key=scores.get)
        confidence = scores[best_domain]
    else:
        best_domain = 'general'
        confidence = 0.3
    
    return {
        "status": "success",
        "outputs": {
            "query": query,
            "intent": best_domain,
            "confidence": round(min(confidence, 1.0), 2),
            "all_scores": {k: round(v, 2) for k, v in scores.items()}
        },
        "trace": {
            "sutra_id": "sutra_045",
            "version": "1.0.0"
        }
    }
