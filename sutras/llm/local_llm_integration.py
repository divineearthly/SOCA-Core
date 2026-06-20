"""
sutra_063: Local LLM Integration
Pramana: Shabda (Testimony)
Integrates with llama.cpp for offline inference
"""

import subprocess
import os

def execute(inputs: dict, context: dict = None) -> dict:
    prompt = inputs.get('prompt', '')
    model = inputs.get('model', 'tinyllama')
    
    if not prompt:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_063",
                "version": "1.0.0",
                "error": "Prompt required"
            }
        }
    
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
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_063",
                "version": "1.0.0",
                "error": "No LLM backend found"
            }
        }
    
    # Run LLM
    try:
        model_path = os.path.expanduser(f"~/soca/models/{model}.gguf")
        if not os.path.exists(model_path):
            return {
                "status": "failure",
                "outputs": {},
                "trace": {
                    "sutra_id": "sutra_063",
                    "version": "1.0.0",
                    "error": f"Model not found: {model_path}"
                }
            }
        
        cmd = [binary, "-m", model_path, "-p", prompt, "-n", "100", "--no-display-prompt"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return {
            "status": "success",
            "outputs": {
                "generated_text": result.stdout.strip(),
                "model": model
            },
            "trace": {
                "sutra_id": "sutra_063",
                "version": "1.0.0"
            }
        }
    except Exception as e:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_063",
                "version": "1.0.0",
                "error": str(e)
            }
        }
