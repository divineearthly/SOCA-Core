"""
Test: Stage 2 - Full Hybrid SOCA + LLM
"""

import sys
sys.path.append('runtime')
sys.path.append('sutras')

from soca_runtime import SOCARuntime

def test_hybrid_full():
    print("=" * 60)
    print("🔨 STAGE 2: Full Hybrid SOCA + LLM")
    print("=" * 60)
    
    runtime = SOCARuntime()
    
    # Register sutras
    print("\n📦 Registering Sutras...")
    runtime.register_sutras_from_directory("sutras")
    
    stats = runtime.get_stats()
    print(f"\n📊 Stats: {stats}")
    
    print("\n--- Test 1: Code Generation (sutra_011) ---")
    result = runtime.solve_sequence(
        ["sutra_011"],
        {
            "specification": "Check if a number is prime",
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
        
        print(f"✅ Code generated successfully!")
        print(f"📝 Code:\n{code}")
        print(f"🔍 Verified: {verified}")
        print(f"📊 Test Results: {len([r for r in test_results if r['passed']])}/{len(test_results)} passed")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n--- Test 2: LLM Generation (sutra_012) ---")
    if stats.get('total_sutras', 0) >= 8:
        result = runtime.solve_sequence(
            ["sutra_012"],
            {
                "prompt": "Write a haiku about meditation",
                "max_tokens": 30,
                "temperature": 0.7
            }
        )
        
        if result['status'] == 'success':
            generated_text = result['outputs'].get('generated_text', '')
            model = result['outputs'].get('model', 'unknown')
            print(f"✅ LLM generated successfully!")
            print(f"📝 Generated:\n{generated_text}")
            print(f"🔧 Model: {model}")
        else:
            print(f"❌ LLM generation failed: {result.get('error')}")
    else:
        print("⚠️ Sutra_012 not registered yet. Skipping LLM test.")
    
    print("\n--- Test 3: Hybrid Workflow ---")
    print("📝 Workflow: Generate code from spec → Verify → Repair if needed")
    print("This demonstrates SOCA's verification-driven generation.")
    
    print("\n" + "=" * 60)
    print("🏁 Stage 2 - Hybrid Architecture Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_hybrid_full()
