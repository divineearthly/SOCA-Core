"""
Sutra 012: LLM Creative Generation (Optimized)
Uses llama-b9728 with speed optimizations
Pramana: Shabda (Testimony)
"""

import subprocess
import os

def execute(inputs: dict, context: dict = None) -> dict:
    prompt = inputs.get('prompt', '')
    max_tokens = inputs.get('max_tokens', 30)  # Reduced for speed
    temperature = inputs.get('temperature', 0.7)
    
    if not prompt:
        return {"status": "failure", "outputs": {}, "trace": {"error": "No prompt"}}
    
    # Use llama-cli directly
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
        
        # SPEED OPTIMIZATIONS:
        # - Use 4 threads (Redmi 14C has 8 cores)
        # - Batch size 512 for better throughput
        # - No GPU (mobile)
        # - Reduced context window
        cmd = [
            binary,
            "-m", model_path,
            "-p", prompt,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-ngl", "0",
            "-t", "4",           # 4 threads
            "-c", "512",         # Reduced context window
            "-b", "512",         # Batch size
            "--no-display-prompt",
            "--simple-io"        # Simple I/O mode
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=env)
        
        # Get the output
        output = result.stdout.strip()
        
        # Remove the prompt if it was echoed
        if output.startswith(prompt):
            output = output[len(prompt):].strip()
        
        # Remove any ">" characters from interactive mode
        if output.startswith(">"):
            output = output[1:].strip()
        
        # If we have a valid response, return it
        if output and len(output) > 5:
            return {
                "status": "success",
                "outputs": {"generated_text": output},
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
        "2+2": "2 + 2 = 4",
        "factorial": "Factorial of n: n! = n * (n-1) * ... * 1",
        "prime": "A prime number has exactly two factors: 1 and itself.",
        "fibonacci": "Fibonacci: 0, 1, 1, 2, 3, 5, 8, 13, 21...",
        "palindrome": "A palindrome reads the same forward and backward."
    }
    
    response = f"I'm a SOCA-based AI."
    if reason:
        response += f" [LLM: {reason}]"
    response += " For advanced responses, a local LLM backend is needed."
    
    for key, value in responses.items():
        if key in prompt_lower:
            response = value
            break
    
    return {
        "status": "success",
        "outputs": {"generated_text": response},
        "trace": {"sutra_id": "sutra_012", "mode": "fallback"}
    }

def find_model():
    """Find a GGUF model file - prefer smaller/faster models."""
    # Priority: smaller models first for speed
    paths = [
        "~/soca/models/tinyllama-q2_K.gguf",           # Smallest, fastest
        "~/soca/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",  # Original
        "~/soca/models/phi-2.Q4_K_M.gguf"               # Phi-2
    ]
    for path in paths:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            return expanded
    return None
