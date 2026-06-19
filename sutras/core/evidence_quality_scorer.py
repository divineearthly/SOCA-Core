"""
sutra_079: Evidence Quality Scorer
Pramana: Anumana (Inference)
Scores evidence by quality, not just quantity
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    answer = inputs.get('answer', '')
    sources = inputs.get('sources', [])
    ranked_results = inputs.get('ranked_results', [])
    domain = inputs.get('domain', 'general')
    
    # Calculate quality score
    quality_score = 0.0
    
    # Source quality
    if sources:
        quality_score += min(len(sources) * 0.1, 0.3)
    
    # Relevance quality
    if ranked_results and ranked_results[0].get('relevance_score', 0) > 0.5:
        quality_score += 0.2
    
    # Domain weight
    if domain in ['agriculture', 'medicine']:
        quality_score += 0.1
    
    # Answer completeness
    if len(answer) > 50:
        quality_score += 0.1
    
    # Cap at 1.0
    quality_score = min(quality_score, 1.0)
    
    # Determine level
    if quality_score >= 0.8:
        level = "High Quality"
    elif quality_score >= 0.6:
        level = "Medium Quality"
    else:
        level = "Low Quality"
    
    return success_response(
        outputs={
            'quality_score': round(quality_score, 2),
            'level': level,
            'source_count': len(sources),
            'top_relevance': ranked_results[0].get('relevance_score', 0) if ranked_results else 0,
            'recommendation': 'Accept' if quality_score > 0.6 else 'Review Needed'
        },
        confidence=quality_score,
        metadata={'sutra': 'sutra_079', 'version': '1.0.0'}
    )
