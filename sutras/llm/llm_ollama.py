"""
Sutra 012: LLM Generation via Ollama
"""

import subprocess

def execute(inputs: dict, context: dict = None) -> dict:
    prompt = inputs.get('prompt', '')
    max_tokens = inputs.get('max_tokens', 100)
    temperature = inputs.get('temperature', 0.7)
    model = inputs.get('model', 'tinyllama')
    
    if not prompt:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No prompt"}}
    
    try:
        cmd = ["ollama", "run", model, prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return {"status": "failure", "outputs": {}, "trace": {"error": result.stderr}}
        
        return {
            "status": "success",
            "outputs": {"generated_text": result.stdout.strip()},
            "trace": {"sutra_id": "sutra_012", "model": model}
        }
    except Exception as e:
        return {"status": "failure", "outputs": {}, "trace": {"error": str(e)}}
