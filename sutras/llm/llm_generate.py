"""
Sutra 012: LLM Creative Generation
Uses the built llama-llava-cli (working)
"""

import subprocess
import os

def execute(inputs: dict, context: dict = None) -> dict:
    prompt = inputs.get('prompt', '')
    max_tokens = inputs.get('max_tokens', 50)
    temperature = inputs.get('temperature', 0.7)
    
    if not prompt:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No prompt"}}
    
    # Find model
    model_path = find_model()
    if not model_path:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No model found"}}
    
    # Use the built binary
    binary = os.path.expanduser("~/llama.cpp/build/bin/llama-llava-cli")
    
    if not os.path.exists(binary):
        return {"status": "failure", "outputs": {}, "trace": {"error": f"Binary not found: {binary}"}}
    
    # Run
    try:
        cmd = [
            binary,
            "-m", model_path,
            "-p", prompt,
            "-n", str(max_tokens),
            "--temp", str(temperature)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip()
        
        # Remove prompt echo if present
        if output.startswith(prompt):
            output = output[len(prompt):].strip()
        
        return {
            "status": "success",
            "outputs": {"generated_text": output},
            "trace": {"sutra_id": "sutra_012", "binary": "llama-llava-cli"}
        }
    except subprocess.TimeoutExpired:
        return {"status": "failure", "outputs": {}, "trace": {"error": "Timeout"}}
    except Exception as e:
        return {"status": "failure", "outputs": {}, "trace": {"error": str(e)}}

def find_model():
    """Find a GGUF model file"""
    paths = [
        "~/soca/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "~/soca/models/phi-2.Q4_K_M.gguf"
    ]
    for path in paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            return expanded
    return None
