"""
sutra_077: Retrieval Ranker
Pramana: Anumana (Inference)
Scores and ranks knowledge by relevance
"""

import os
import json
import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '').lower()
    knowledge_results = inputs.get('knowledge_results', [])
    
    if not query:
        return failure_response("Query required")
    
    ranked = []
    query_words = set(query.split())
    
    for item in knowledge_results:
        data = item.get('data', {})
        source = item.get('source', '')
        
        # Calculate relevance score
        score = 0
        data_str = json.dumps(data).lower()
        
        for word in query_words:
            if word in data_str:
                score += 1
        
        # Normalize
        score = min(score / max(len(query_words), 1), 1.0)
        
        ranked.append({
            'source': source,
            'data': data,
            'relevance_score': round(score, 3)
        })
    
    # Sort by relevance
    ranked.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return success_response(
        outputs={
            'ranked_results': ranked,
            'top_result': ranked[0] if ranked else None,
            'count': len(ranked)
        },
        confidence=0.9,
        metadata={'sutra': 'sutra_077', 'version': '1.0.0'}
    )
