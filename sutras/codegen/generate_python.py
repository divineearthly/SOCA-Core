"""
Sutra 011: Generate Python Code
Pramana: Anumana (Inference)
Generates Python code from a specification and verifies it
"""

import ast
import sys
import io
import contextlib
import traceback

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Generate and verify Python code.
    
    Args:
        inputs: dict with:
            - specification: str describing what to generate
            - test_cases: list of dict with 'inputs' and 'expected'
    
    Returns:
        dict with 'status', 'outputs', 'trace'
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
    
    # Parse specification to generate code
    # This is a simple template-based generator for MVP
    # In production, this would use an LLM or more sophisticated generation
    
    code = generate_code_from_spec(specification)
    
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
                "test_cases_passed": len(verification_result['results']),
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
    """
    Generate Python code from a specification.
    MVP: Uses pattern matching for common functions.
    """
    spec_lower = specification.lower()
    
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
    
    # Sum
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
    
    # Default: generic function template
    else:
        return f'''def generated_function():
    """
    {specification}
    """
    # TODO: Implement based on specification
    return None
'''

def verify_code(code: str, test_cases: list) -> dict:
    """
    Verify generated code by executing test cases.
    """
    results = []
    errors = []
    
    # Create a temporary namespace
    namespace = {}
    
    # Compile and execute the code
    try:
        exec(code, namespace)
    except Exception as e:
        return {
            "passed": False,
            "results": [],
            "errors": [f"Compilation error: {str(e)}"]
        }
    
    # Find the function in the namespace
    functions = [name for name, obj in namespace.items() 
                if callable(obj) and not name.startswith('_')]
    
    if not functions:
        return {
            "passed": False,
            "results": [],
            "errors": ["No function defined in the generated code"]
        }
    
    # Use the first function found
    func_name = functions[0]
    func = namespace[func_name]
    
    # Run each test case
    for i, test_case in enumerate(test_cases):
        test_input = test_case.get('inputs', [])
        expected = test_case.get('expected')
        
        try:
            # Execute function with test inputs
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
