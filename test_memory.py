"""
Test: Stage 3 - Kosha-Net Memory System
"""

import sys
sys.path.append('runtime')
sys.path.append('sutras')

from soca_runtime import SOCARuntime

def test_kosha_memory():
    print("=" * 60)
    print("🔨 STAGE 3: Kosha-Net Memory System")
    print("=" * 60)
    
    runtime = SOCARuntime()
    
    # Register sutras
    print("\n📦 Registering Sutras...")
    runtime.register_sutras_from_directory("sutras")
    
    stats = runtime.get_stats()
    print(f"\n📊 Stats: {stats}")
    
    # Test 1: Store memory
    print("\n--- Test 1: Store Memory ---")
    
    result = runtime.solve_sequence(
        ["sutra_013"],
        {
            "action": "store",
            "key": "user_preference",
            "value": {"language": "Python", "style": "functional"},
            "layer": "manomaya",
            "ttl": 3600
        }
    )
    
    if result['status'] == 'success':
        print(f"✅ Memory stored!")
        print(f"Layer: {result['outputs'].get('layer')}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 2: Retrieve memory
    print("\n--- Test 2: Retrieve Memory ---")
    
    result = runtime.solve_sequence(
        ["sutra_013"],
        {
            "action": "retrieve",
            "key": "user_preference"
        }
    )
    
    if result['status'] == 'success':
        if result['outputs'].get('found'):
            print(f"✅ Memory retrieved!")
            print(f"Value: {result['outputs'].get('value')}")
            print(f"Layer: {result['outputs'].get('layer')}")
        else:
            print("ℹ️ Memory not found")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 3: Continual Learning
    print("\n--- Test 3: Continual Learning ---")
    
    result = runtime.solve_sequence(
        ["sutra_014"],
        {
            "new_knowledge": {
                "concept": "compositional generation",
                "description": "Building complex outputs from verified components"
            },
            "domain": "cognitive_architecture",
            "importance": 9
        }
    )
    
    if result['status'] == 'success':
        if result['outputs'].get('learned'):
            print(f"✅ New knowledge learned!")
            print(f"Layer: {result['outputs'].get('layer')}")
            print(f"Domain: {result['outputs'].get('domain')}")
        else:
            print(f"ℹ️ {result['outputs'].get('message', 'Already learned')}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 4: Prevent Forgetting
    print("\n--- Test 4: Prevent Forgetting ---")
    
    # Learn the same knowledge again (should be deduplicated)
    result = runtime.solve_sequence(
        ["sutra_014"],
        {
            "new_knowledge": {
                "concept": "compositional generation",
                "description": "Building complex outputs from verified components"
            },
            "domain": "cognitive_architecture",
            "importance": 9
        }
    )
    
    if result['status'] == 'success':
        if result['outputs'].get('learned') == False:
            print(f"✅ Catastrophic forgetting prevented!")
            print(f"Message: {result['outputs'].get('message', 'Knowledge preserved')}")
        else:
            print("⚠️ Knowledge was re-learned (potential forgetting risk)")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("🏁 Stage 3 - Kosha-Net Memory Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_kosha_memory()
