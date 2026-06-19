"""
sutra_038: Local LLM Gateway
Pramana: Shabda (Testimony)
Integrates with local LLM for advanced generation
"""

import subprocess
import os

def execute(inputs: dict, context: dict = None) -> dict:
    prompt = inputs.get('prompt', '')
    model = inputs.get('model', 'tinyllama')
    
    if not prompt:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No prompt"}}
    
    # Check for llama.cpp
    llama_paths = [
        "~/llama.cpp/build/bin/llama-cli",
        "~/llama.cpp/main",
        "~/soca/llama-b9728/llama-cli"
    ]
    
    binary = None
    for path in llama_paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            binary = expanded
            break
    
    if not binary:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No LLM backend found"}}
    
    # Run LLM
    try:
        cmd = [binary, "-m", f"~/soca/models/{model}.gguf", "-p", prompt, "-n", "50"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "status": "success",
            "outputs": {"generated_text": result.stdout.strip()},
            "trace": {"sutra_id": "sutra_038"}
        }
    except Exception as e:
        return {"status": "failure", "outputs": {}, "trace": {"error": str(e)}}
