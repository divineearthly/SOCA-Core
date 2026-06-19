"""
Sutra 011: Generate Python Code
Pramana: Anumana (Inference)
Now with LLM-based generation via sutra_012
"""

import ast
import sys
import io
import contextlib
import traceback
import os

# Import the LLM sutra (sutra_012) dynamically
def get_llm_sutra():
    try:
        import importlib
        module = importlib.import_module('sutras.llm.llm_generate')
        return module.execute
    except Exception as e:
        return None

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Generate and verify Python code.
    Uses LLM for generation, then verifies with test cases.
    """
    specification = inputs.get('specification', '')
    test_cases = inputs.get('test_cases', [])
    
    if not specification:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_011",
                "version": "1.0.0",
                "error": "No specification provided"
            }
        }
    
    # First, try template matching (fast path)
    code = generate_code_from_spec(specification)
    
    # If no template match, try LLM generation
    if not code:
        print(f"  🔍 No template match, trying LLM generation...")
        code = generate_via_llm(specification)
    
    if not code:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_011",
                "version": "1.0.0",
                "error": f"Could not generate code for: {specification}"
            }
        }
    
    # Verify the code
    verification_result = verify_code(code, test_cases)
    
    if verification_result['passed']:
        return {
            "status": "success",
            "outputs": {
                "code": code,
                "verified": True,
                "test_results": verification_result['results']
            },
            "trace": {
                "sutra_id": "sutra_011",
                "version": "1.0.0",
                "execution_time_ms": 0,
                "specification": specification,
                "test_cases_passed": len([r for r in verification_result['results'] if r['passed']]),
                "test_cases_total": len(test_cases)
            }
        }
    else:
        return {
            "status": "failure",
            "outputs": {
                "code": code,
                "verified": False,
                "errors": verification_result['errors']
            },
            "trace": {
                "sutra_id": "sutra_011",
                "version": "1.0.0",
                "error": "Code verification failed",
                "specification": specification,
                "test_cases_passed": len([r for r in verification_result['results'] if r['passed']]),
                "test_cases_total": len(test_cases)
            }
        }

def generate_via_llm(specification: str) -> str:
    """
    Call sutra_012 (LLM) to generate code.
    """
    llm_func = get_llm_sutra()
    if not llm_func:
        print("  ⚠️ LLM sutra not available")
        return None
    
    prompt = f"Write a Python function for: {specification}\nReturn only the function, no explanation."
    
    result = llm_func({
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.2
    })
    
    if result.get('status') == 'success':
        raw = result['outputs'].get('generated_text', '')
        # Extract code block if wrapped in ```
        if '```' in raw:
            parts = raw.split('```')
            if len(parts) > 1:
                raw = parts[1]
                if raw.startswith('python'):
                    raw = raw[6:]
        return raw.strip()
    
    print(f"  ❌ LLM generation failed: {result.get('trace', {}).get('error', 'Unknown')}")
    return None

def generate_code_from_spec(specification: str) -> str:
    """
    Generate Python code from a specification using templates.
    """
    spec_lower = specification.lower()
    
    # Prime number check
    if "prime" in spec_lower and ("check" in spec_lower or "is" in spec_lower):
        return '''def is_prime(n):
    """
    Check if a number is prime.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
'''
    
    # Factorial
    if "factorial" in spec_lower:
        return '''def factorial(n):
    """
    Calculate factorial of n.
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''
    
    # Fibonacci
    elif "fibonacci" in spec_lower:
        return '''def fibonacci(n):
    """
    Calculate nth Fibonacci number.
    """
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
'''
    
    # Sum of list
    elif "sum" in spec_lower and "list" in spec_lower:
        return '''def sum_list(numbers):
    """
    Sum all numbers in a list.
    """
    return sum(numbers)
'''
    
    # Palindrome
    elif "palindrome" in spec_lower:
        return '''def is_palindrome(s):
    """
    Check if string is a palindrome.
    """
    s = s.lower().replace(" ", "")
    return s == s[::-1]
'''
    
    # Max of list
    elif "max" in spec_lower and "list" in spec_lower:
        return '''def max_list(numbers):
    """
    Find maximum number in a list.
    """
    if not numbers:
        return None
    return max(numbers)
'''
    
    # Min of list
    elif "min" in spec_lower and "list" in spec_lower:
        return '''def min_list(numbers):
    """
    Find minimum number in a list.
    """
    if not numbers:
        return None
    return min(numbers)
'''
    
    return None

def verify_code(code: str, test_cases: list) -> dict:
    """
    Verify generated code by executing test cases.
    """
    results = []
    errors = []
    
    namespace = {}
    
    try:
        exec(code, namespace)
    except Exception as e:
        return {
            "passed": False,
            "results": [],
            "errors": [f"Compilation error: {str(e)}"]
        }
    
    functions = [name for name, obj in namespace.items() 
                if callable(obj) and not name.startswith('_')]
    
    if not functions:
        return {
            "passed": False,
            "results": [],
            "errors": ["No function defined in the generated code"]
        }
    
    func_name = functions[0]
    func = namespace[func_name]
    
    for i, test_case in enumerate(test_cases):
        test_input = test_case.get('inputs', [])
        expected = test_case.get('expected')
        
        try:
            if isinstance(test_input, (list, tuple)):
                result = func(*test_input)
            else:
                result = func(test_input)
            
            passed = result == expected
            results.append({
                "test_id": i + 1,
                "inputs": test_input,
                "expected": expected,
                "actual": result,
                "passed": passed
            })
            
            if not passed:
                errors.append(f"Test {i+1} failed: expected {expected}, got {result}")
                
        except Exception as e:
            results.append({
                "test_id": i + 1,
                "inputs": test_input,
                "expected": expected,
                "actual": None,
                "passed": False,
                "error": str(e)
            })
            errors.append(f"Test {i+1} raised exception: {str(e)}")
    
    return {
        "passed": len([r for r in results if r['passed']]) == len(test_cases),
        "results": results,
        "errors": errors
    }
