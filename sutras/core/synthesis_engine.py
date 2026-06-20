"""
sutra_084: Synthesis Engine
Pramana: Anumana (Inference)
Generates structured recommendations with reasoning
"""

import sys
sys.path.append('runtime')
from response import success_response, failure_response

def execute(inputs: dict, context: dict = None) -> dict:
    results = inputs.get('results', {})
    slots = inputs.get('slots', {})
    intent = inputs.get('intent', 'general')
    sources = inputs.get('sources', [])
    subgoals = inputs.get('subgoals', [])
    
    if not results:
        return failure_response("No results to synthesize")
    
    if intent == 'agriculture':
        return synthesize_agriculture(results, slots, sources, subgoals)
    
    # Default synthesis
    synthesis = []
    for key, values in results.items():
        if values:
            synthesis.append(f"{key}: {', '.join(str(v) for v in values[:3])}")
    
    return success_response(
        outputs={
            'synthesis': ' | '.join(synthesis),
            'recommendation': ' | '.join(synthesis),
            'confidence': 0.6
        },
        confidence=0.6
    )

def synthesize_agriculture(results, slots, sources, subgoals):
    """Synthesize agriculture recommendation."""
    # Extract crops
    crops = []
    for key, values in results.items():
        if key in ['crops', 'recommended_crops']:
            for item in values:
                if isinstance(item, str):
                    crops.append(item)
                elif isinstance(item, list):
                    crops.extend(item)
    
    # Remove duplicates and normalize
    crops = list(dict.fromkeys(crops))
    
    # Rank crops by suitability
    ranked_crops = rank_crops(crops, slots, results)
    
    # Get district and season
    district = slots.get('district', 'your district')
    season = slots.get('season', 'the current season')
    
    # Generate recommendation
    if ranked_crops:
        top_crop = ranked_crops[0]['name']
        
        reasoning = []
        if season:
            reasoning.append(f"Suitable for {season} season")
        if district:
            reasoning.append(f"Grows well in {district}")
        if slots.get('soil_type'):
            reasoning.append(f"Thrives in {slots['soil_type']} soil")
        
        recommendation = f"Recommended: {top_crop}"
        if reasoning:
            recommendation += f" ({', '.join(reasoning)})"
        
        # Generate alternatives
        alternatives = []
        for crop in ranked_crops[1:3]:
            alternatives.append(crop['name'])
        
        synthesis = f"{recommendation}"
        if alternatives:
            synthesis += f" | Alternatives: {', '.join(alternatives)}"
        
        return success_response(
            outputs={
                'synthesis': synthesis,
                'recommendation': recommendation,
                'ranked_crops': ranked_crops,
                'alternatives': alternatives,
                'confidence': calculate_confidence(ranked_crops, sources, slots)
            },
            confidence=0.8
        )
    
    return success_response(
        outputs={
            'synthesis': 'No specific crop recommendations available',
            'recommendation': 'Consult local agricultural officer',
            'confidence': 0.4
        },
        confidence=0.4
    )

def rank_crops(crops, slots, results):
    """Rank crops by suitability."""
    ranked = []
    
    # Simple scoring based on context
    for crop in crops:
        score = 0.5
        crop_lower = crop.lower()
        
        # Boost for relevant keywords
        if 'rice' in crop_lower:
            score += 0.3
        if 'tea' in crop_lower:
            score += 0.2
        if 'jute' in crop_lower:
            score += 0.15
        if 'mustard' in crop_lower:
            score += 0.1
        if 'wheat' in crop_lower:
            score += 0.1
        
        # Boost if mentioned in multiple sources
        source_count = 0
        for key, values in results.items():
            if key in ['crops', 'recommended_crops']:
                for v in values:
                    if isinstance(v, str) and crop_lower in v.lower():
                        source_count += 1
        score += min(source_count * 0.05, 0.2)
        
        ranked.append({
            'name': crop,
            'score': round(min(score, 1.0), 2)
        })
    
    ranked.sort(key=lambda x: x['score'], reverse=True)
    return ranked[:5]

def calculate_confidence(ranked_crops, sources, slots):
    """Calculate confidence based on evidence."""
    if not ranked_crops:
        return 0.3
    
    confidence = 0.3
    confidence += len(sources) * 0.05
    confidence += len(ranked_crops) * 0.02
    
    if slots.get('season'):
        confidence += 0.1
    if slots.get('district'):
        confidence += 0.1
    if slots.get('soil_type'):
        confidence += 0.05
    
    return round(min(confidence, 1.0), 2)
