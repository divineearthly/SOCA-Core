"""
Sutra 011: Generate Python Code
Pramana: Anumana (Inference)
Generates and verifies Python code
"""

import ast
import sys
import io
import contextlib
import traceback

def execute(inputs: dict, context: dict = None) -> dict:
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
    
    # Generate code
    code = generate_code_from_spec(specification)
    
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

def generate_code_from_spec(specification: str) -> str:
    spec_lower = specification.lower()
    
    if "prime" in spec_lower and ("check" in spec_lower or "is" in spec_lower):
        return '''def is_prime(n):
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
    if "factorial" in spec_lower:
        return '''def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''
    if "fibonacci" in spec_lower:
        return '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
'''
    if "sum" in spec_lower and "list" in spec_lower:
        return '''def sum_list(numbers):
    return sum(numbers)
'''
    if "palindrome" in spec_lower:
        return '''def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
'''
    return None

def verify_code(code: str, test_cases: list) -> dict:
    if not test_cases:
        return {
            "passed": False,
            "results": [],
            "errors": ["No test cases provided"]
        }
    
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
