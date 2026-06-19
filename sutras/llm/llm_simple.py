"""
Sutra 012: Simple LLM Responses (No binary needed)
"""

def execute(inputs: dict, context: dict = None) -> dict:
    prompt = inputs.get('prompt', '').lower()
    
    responses = {
        "hello": "Hello! I'm your SOCA-powered assistant.",
        "2+2": "2 + 2 = 4",
        "factorial": "Factorial of n: n! = n * (n-1) * ... * 1",
        "prime": "A prime number has exactly two factors: 1 and itself.",
        "fibonacci": "Fibonacci: 0, 1, 1, 2, 3, 5, 8, 13, 21...",
        "palindrome": "A palindrome reads the same forward and backward."
    }
    
    response = "I'm a SOCA-based AI. I understand basic concepts. "
    response += "For advanced generation, a local LLM backend is needed."
    
    for key, value in responses.items():
        if key in prompt:
            response = value
            break
    
    return {
        "status": "success",
        "outputs": {"generated_text": response},
        "trace": {"sutra_id": "sutra_012", "mode": "simple"}
    }
