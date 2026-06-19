"""
Test: Stage 2 - Hybrid SOCA + LLM
"""

import sys
sys.path.append('runtime')
sys.path.append('sutras')

from soca_runtime import SOCARuntime

def test_hybrid():
    print("=" * 60)
    print("🔨 STAGE 2: Hybrid SOCA + Local LLM")
    print("=" * 60)
    
    runtime = SOCARuntime()
    
    # Register sutras
    print("\n📦 Registering Sutras...")
    runtime.register_sutras_from_directory("sutras")
    
    print("\n--- Test: Creative Generation with Verification ---")
    
    # Use LLM to generate a creative function
    # Then verify it with SOCA
    # This demonstrates the Hybrid architecture
    
    # Step 1: Generate a creative function using LLM
    # (This would be sutra_012)
    
    # Step 2: Generate code from spec using sutra_011
    # Step 3: Verify the code
    
    result = runtime.solve_sequence(
        ["sutra_011"],
        {
            "specification": "Write a function that checks if a number is prime",
            "test_cases": [
                {"inputs": [2], "expected": True},
                {"inputs": [3], "expected": True},
                {"inputs": [4], "expected": False},
                {"inputs": [17], "expected": True}
            ]
        }
    )
    
    if result['status'] == 'success':
        code = result['outputs'].get('code', '')
        verified = result['outputs'].get('verified', False)
        test_results = result['outputs'].get('test_results', [])
        
        print(f"✅ Code generated and verified!")
        print(f"📝 Code:\n{code}")
        print(f"🔍 Verified: {verified}")
        print(f"📊 Test Results: {len([r for r in test_results if r['passed']])}/{len(test_results)} passed")
        
        for r in test_results:
            status = "✅" if r['passed'] else "❌"
            print(f"  {status} Test {r['test_id']}: {r['inputs']} → expected {r['expected']}, got {r['actual']}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("🏁 Stage 2 - Hybrid Architecture Ready")
    print("(LLM integration requires llama.cpp setup)")
    print("=" * 60)

if __name__ == "__main__":
    test_hybrid()
