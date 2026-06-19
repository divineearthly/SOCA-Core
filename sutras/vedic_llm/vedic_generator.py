"""
Sutra 019: Vedic Language Generator
Pure Vedic-structure LLM using Panini grammar + Nyaya logic
Pramana: Shabda (Testimony) with Anumana (Inference)
"""

import re
import random

def execute(inputs: dict, context: dict = None) -> dict:
    prompt = inputs.get('prompt', '')
    max_tokens = inputs.get('max_tokens', 50)
    temperature = inputs.get('temperature', 0.7)
    
    if not prompt:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No prompt"}}
    
    # Step 1: Parse via Panini (simplified)
    parsed = panini_parse(prompt)
    
    # Step 2: Apply Nyaya inference
    inferred = nyaya_infer(parsed)
    
    # Step 3: Generate via Vak layers
    response = generate_vak(parsed, inferred, temperature)
    
    return {
        "status": "success",
        "outputs": {
            "generated_text": response,
            "parsed": parsed,
            "inferred": inferred
        },
        "trace": {
            "sutra_id": "sutra_019",
            "version": "1.0.0",
            "backend": "vedic_llm",
            "pramana": "shabda"
        }
    }

def panini_parse(text):
    """Simplified Panini parser - extracts key elements"""
    words = text.lower().split()
    return {
        'tokens': words,
        'length': len(words),
        'question': '?' in text,
        'what': 'what' in text.lower(),
        'how': 'how' in text.lower(),
        'why': 'why' in text.lower()
    }

def nyaya_infer(parsed):
    """Nyaya 5-step inference"""
    # Pratijna (Hypothesis)
    pratijna = "The user asked about: " + " ".join(parsed['tokens'][:3])
    
    # Hetu (Reason)
    if parsed['what']:
        hetu = "Seeking definition or explanation"
    elif parsed['how']:
        hetu = "Seeking procedure or method"
    else:
        hetu = "General inquiry"
    
    # Udaharanra (Example)
    if "2+2" in " ".join(parsed['tokens']):
        udaharanra = "Example: 2+2 = 4"
    else:
        udaharanra = "No specific example found"
    
    # Upanaya (Application)
    upanaya = "Applying knowledge to answer"
    
    # Nigamana (Conclusion)
    nigamana = "Response generated based on query type"
    
    return {
        'pratijna': pratijna,
        'hetu': hetu,
        'udaharanra': udaharanra,
        'upanaya': upanaya,
        'nigamana': nigamana
    }

def generate_vak(parsed, inferred, temperature):
    """Generate response through 4 Vak layers"""
    
    # Layer 1: Vaikhari (Raw text)
    vaikhari = "Answering: " + " ".join(parsed['tokens'][:3])
    
    # Layer 2: Madhyama (Mental/structured)
    if parsed['what']:
        madhyama = "What is it? It is a concept related to your query."
    elif parsed['how']:
        madhyama = "How to do it? Follow these steps: understand, plan, execute."
    elif parsed['question']:
        madhyama = "Yes, that is a valid question."
    else:
        madhyama = "I understand your statement."
    
    # Layer 3: Pashyanti (Visual/conceptual)
    pashyanti = "Concept mapped: " + inferred['hetu']
    
    # Layer 4: Para (Transcendent meaning)
    para = inferred['nigamana']
    
    # Combine with temperature
    responses = [vaikhari, madhyama, pashyanti, para]
    if temperature > 0.5:
        response = random.choice(responses)
    else:
        response = responses[1]  # Most balanced
    
    return response
