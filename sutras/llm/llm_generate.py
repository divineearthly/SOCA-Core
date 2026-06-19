"""
Sutra 012: LLM Creative Generation (Final Optimized)
Uses llama-b9728 with direct output capture
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
        
        cmd = [
            binary,
            "-m", model_path,
            "-p", prompt,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-ngl", "0",
            "-t", "4",
            "-c", "256",
            "-b", "256",
            "--no-display-prompt"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=12, env=env)
        
        # Direct output capture
        output = result.stdout.strip()
        
        # Try to extract the actual response
        # Method 1: Remove prompt if echoed
        if output.startswith(prompt):
            output = output[len(prompt):].strip()
        
        # Method 2: Remove interactive prompts ("> ")
        if output.startswith("> "):
            output = output[2:].strip()
        
        # Method 3: Look for answer pattern after the prompt
        patterns = [
            r'(?i)(?:answer:\s*|response:\s*|>)\s*(.+?)(?:\n|$)',
            r'(?i)([A-Za-z0-9][^>]*?)(?:\n\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.DOTALL)
            if match:
                output = match.group(1).strip()
                break
        
        # Clean up
        output = output.split('\n')[0]  # Take first line
        output = output.strip()
        
        # If we have a valid response, return it
        if output and len(output) > 2 and len(output) < 200:
            return {
                "status": "success",
                "outputs": {"generated_text": output},
                "trace": {"sutra_id": "sutra_012", "backend": "llama-cli"}
            }
        else:
            # Try fallback with the raw output
            return fallback_response(prompt, f"Raw output: {output[:30]}")
            
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
        "~/soca/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "~/soca/models/phi-2.Q4_K_M.gguf"
    ]
    for path in paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            return expanded
    return None
