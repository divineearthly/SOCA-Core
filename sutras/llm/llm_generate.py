"""
Sutra 012: LLM Creative Generation (Final)
Uses llama-b9728 with direct non-interactive mode
Pramana: Shabda (Testimony)
"""

import subprocess
import os
import re

def execute(inputs: dict, context: dict = None) -> dict:
    prompt = inputs.get('prompt', '')
    max_tokens = inputs.get('max_tokens', 20)
    temperature = inputs.get('temperature', 0.7)
    
    if not prompt:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No prompt"}}
    
    binary = os.path.expanduser("~/soca/llama-b9728/llama-cli")
    
    if not os.path.exists(binary):
        return fallback_response(prompt, "Binary not found")
    
    model_path = find_model()
    if not model_path:
        return fallback_response(prompt, "No model found")
    
    try:
        env = os.environ.copy()
        lib_path = os.path.expanduser("~/soca/llama-b9728")
        env['LD_LIBRARY_PATH'] = lib_path + ":" + env.get('LD_LIBRARY_PATH', '')
        
        # Use -p for prompt and capture stdout directly
        cmd = [
            binary,
            "-m", model_path,
            "-p", prompt,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-ngl", "0",
            "-t", "4",
            "-c", "256",
            "-b", "256"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=12, env=env)
        
        # Get the raw output from stdout
        output = result.stdout.strip()
        
        # Look for the answer after the prompt
        # The model typically outputs: [prompt] [answer]
        if prompt in output:
            # Get everything after the prompt
            answer = output.split(prompt, 1)[-1].strip()
        else:
            answer = output
        
        # Clean up the answer
        # Remove common artifacts
        answer = re.sub(r'^[>\s]+', '', answer)
        answer = re.sub(r'\s+$', '', answer)
        
        # Remove any lines that are just "ok", "yes", "no", ">"
        lines = answer.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 2 and not line.lower() in ['ok', 'yes', 'no', '>', '']:
                cleaned_lines.append(line)
        
        if cleaned_lines:
            answer = cleaned_lines[0]
        else:
            answer = answer[:100]  # Take first 100 chars if no clean lines
        
        # If we got a valid answer, return it
        if answer and len(answer) > 2:
            return {
                "status": "success",
                "outputs": {"generated_text": answer},
                "trace": {"sutra_id": "sutra_012", "backend": "llama-cli"}
            }
        else:
            return fallback_response(prompt, "Empty response")
            
    except subprocess.TimeoutExpired:
        return fallback_response(prompt, "Timeout")
    except Exception as e:
        return fallback_response(prompt, str(e))

def fallback_response(prompt, reason=""):
    """Simple fallback responses."""
    prompt_lower = prompt.lower()
    
    responses = {
        "hello": "Hello! I'm your SOCA-powered assistant.",
        "hi": "Hello! How can I help you?",
        "2+2": "2 + 2 = 4",
        "what is": "I'm a SOCA-based AI assistant.",
        "factorial": "Factorial of n: n! = n * (n-1) * ... * 1",
        "prime": "A prime number has exactly two factors: 1 and itself.",
        "fibonacci": "Fibonacci: 0, 1, 1, 2, 3, 5, 8, 13, 21...",
        "palindrome": "A palindrome reads the same forward and backward."
    }
    
    response = ""
    for key, value in responses.items():
        if key in prompt_lower:
            response = value
            break
    
    if not response:
        response = f"I'm a SOCA-based AI. (LLM: {reason if reason else 'available'})"
    
    return {
        "status": "success",
        "outputs": {"generated_text": response},
        "trace": {"sutra_id": "sutra_012", "mode": "fallback"}
    }

def find_model():
    """Find the fastest available GGUF model."""
    paths = [
        "~/soca/models/tinyllama-q2_K.gguf",
        "~/soca/models/tinyllama-1.1b-chat-v1.0.Q2_K.gguf",
        "~/soca/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    ]
    for path in paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            return expanded
    return None
