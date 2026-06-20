"""
sutra_028: Answer Composer
Pramana: Anumana (Inference)
Synthesizes results from multiple sutras into natural language
"""

def execute(inputs: dict, context: dict = None) -> dict:
    query = inputs.get('query', '')
    results = inputs.get('results', {})
    sutra_ids = inputs.get('sutra_ids', [])
    
    if not results:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_028",
                "version": "1.0.0",
                "error": "No results to synthesize"
            }
        }
    
    # Build natural language answer
    answer_parts = []
    
    for sutra_id, output in results.items():
        if 'error' in output:
            continue
        
        # Extract key information
        for key, value in output.items():
            if key in ['code', 'test_results', 'verified']:
                continue
            
            if isinstance(value, list):
                if value:
                    answer_parts.append(f"{key}: {', '.join(str(v) for v in value)}")
            elif value:
                answer_parts.append(f"{key}: {value}")
    
    # Add synthesis if multiple sutras
    if len(sutra_ids) > 1:
        synthesis = "Based on multiple sources, here is the recommendation:\n"
        synthesis += "\n".join(f"  • {part}" for part in answer_parts)
    else:
        synthesis = "\n".join(answer_parts)
    
    # Add confidence
    confidence = inputs.get('confidence', 0.7)
    
    return {
        "status": "success",
        "outputs": {
            "answer": synthesis,
            "confidence": confidence,
            "sutras_used": sutra_ids,
            "query": query
        },
        "trace": {
            "sutra_id": "sutra_028",
            "version": "1.0.0",
            "sutras_used": sutra_ids,
            "confidence": confidence
        }
    }
