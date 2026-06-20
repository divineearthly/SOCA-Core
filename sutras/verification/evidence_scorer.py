"""
sutra_042: Evidence Scorer
Pramana: Pratyaksha (Direct Perception)
Scores answers based on source reliability
"""

def execute(inputs: dict, context: dict = None) -> dict:
    answer = inputs.get('answer', '')
    sources = inputs.get('sources', [])
    domain = inputs.get('domain', 'general')
    
    confidence = 0.5
    reasons = []
    
    if sources:
        source_score = min(1.0, len(sources) * 0.2)
        confidence += source_score * 0.2
        reasons.append(f"Based on {len(sources)} sources")
    
    if len(answer) > 50:
        confidence += 0.1
        reasons.append("Detailed answer")
    
    domain_boosts = {
        'agriculture': 0.1,
        'medicine': 0.05,
        'education': 0.1
    }
    if domain in domain_boosts:
        confidence += domain_boosts[domain]
        reasons.append(f"{domain.capitalize()} domain knowledge")
    
    confidence = min(1.0, confidence)
    
    return {
        "status": "success",
        "outputs": {
            "confidence": round(confidence, 2),
            "reasons": reasons,
            "sources": sources,
            "domain": domain
        },
        "trace": {
            "sutra_id": "sutra_042",
            "version": "1.0.0"
        }
    }
