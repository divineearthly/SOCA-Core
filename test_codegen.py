"""
Test: Verified Code Generation (Stage 1)
"""

import sys
sys.path.append('runtime')
sys.path.append('sutras')

from registry_manager import RegistryManager
from soca_runtime import SOCARuntime

def test_code_generation():
    print("=" * 60)
    print("🔨 STAGE 1: Verified Code Generation")
    print("=" * 60)
    
    # Initialize runtime
    runtime = SOCARuntime()
    
    # Register the code generation sutra
    print("\n📦 Registering Sutra 011...")
    runtime.register_sutras_from_directory("sutras")
    
    # Test Case 1: Generate factorial function
    print("\n--- Test 1: Generate Factorial Function ---")
    
    result = runtime.solve_sequence(
        ["sutra_011"],
        {
            "specification": "Calculate factorial of n",
            "test_cases": [
                {"inputs": [0], "expected": 1},
                {"inputs": [1], "expected": 1},
                {"inputs": [5], "expected": 120},
                {"inputs": [7], "expected": 5040}
            ]
        }
    )
    
    if result['status'] == 'success':
        code = result['outputs'].get('code', '')
        verified = result['outputs'].get('verified', False)
        test_results = result['outputs'].get('test_results', [])
        
        print(f"✅ Code generated successfully!")
        print(f"📝 Code:\n{code}")
        print(f"🔍 Verified: {verified}")
        print(f"📊 Test Results: {len([r for r in test_results if r['passed']])}/{len(test_results)} passed")
        
        for r in test_results:
            status = "✅" if r['passed'] else "❌"
            print(f"  {status} Test {r['test_id']}: {r['inputs']} → expected {r['expected']}, got {r['actual']}")
    else:
        print(f"❌ Generation failed: {result.get('error')}")
    
    # Test Case 2: Generate Fibonacci function
    print("\n--- Test 2: Generate Fibonacci Function ---")
    
    result = runtime.solve_sequence(
        ["sutra_011"],
        {
            "specification": "Calculate nth Fibonacci number",
            "test_cases": [
                {"inputs": [0], "expected": 0},
                {"inputs": [1], "expected": 1},
                {"inputs": [6], "expected": 8},
                {"inputs": [10], "expected": 55}
            ]
        }
    )
    
    if result['status'] == 'success':
        code = result['outputs'].get('code', '')
        verified = result['outputs'].get('verified', False)
        test_results = result['outputs'].get('test_results', [])
        
        print(f"✅ Code generated successfully!")
        print(f"📝 Code:\n{code}")
        print(f"🔍 Verified: {verified}")
        print(f"📊 Test Results: {len([r for r in test_results if r['passed']])}/{len(test_results)} passed")
        
        for r in test_results:
            status = "✅" if r['passed'] else "❌"
            print(f"  {status} Test {r['test_id']}: {r['inputs']} → expected {r['expected']}, got {r['actual']}")
    else:
        print(f"❌ Generation failed: {result.get('error')}")
    
    # Test Case 3: Generate Palindrome function
    print("\n--- Test 3: Generate Palindrome Function ---")
    
    result = runtime.solve_sequence(
        ["sutra_011"],
        {
            "specification": "Check if a string is a palindrome",
            "test_cases": [
                {"inputs": ["racecar"], "expected": True},
                {"inputs": ["hello"], "expected": False},
                {"inputs": ["A man a plan a canal Panama"], "expected": True}
            ]
        }
    )
    
    if result['status'] == 'success':
        code = result['outputs'].get('code', '')
        verified = result['outputs'].get('verified', False)
        test_results = result['outputs'].get('test_results', [])
        
        print(f"✅ Code generated successfully!")
        print(f"📝 Code:\n{code}")
        print(f"🔍 Verified: {verified}")
        print(f"📊 Test Results: {len([r for r in test_results if r['passed']])}/{len(test_results)} passed")
        
        for r in test_results:
            status = "✅" if r['passed'] else "❌"
            print(f"  {status} Test {r['test_id']}: '{r['inputs'][0]}' → expected {r['expected']}, got {r['actual']}")
    else:
        print(f"❌ Generation failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("🏁 Stage 1 Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_code_generation()
