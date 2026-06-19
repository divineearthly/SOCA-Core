"""
Test: Stage 4 - Autonomous Sutra Evolution
"""

import sys
import json
sys.path.append('runtime')
sys.path.append('sutras')

from soca_runtime import SOCARuntime

def test_evolution():
    print("=" * 60)
    print("🔨 STAGE 4: Autonomous Sutra Evolution")
    print("=" * 60)
    
    runtime = SOCARuntime()
    
    # Register sutras
    print("\n📦 Registering Sutras...")
    runtime.register_sutras_from_directory("sutras")
    
    stats = runtime.get_stats()
    print(f"\n📊 Stats: {stats}")
    
    print("\n--- Test 1: Sutra Discovery ---")
    result = runtime.solve_sequence(
        ["sutra_015"],
        {"target_domain": "all", "max_gaps": 3}
    )
    
    if result['status'] == 'success':
        print(f"✅ Discovery complete!")
        print(f"Total Sutras: {result['outputs'].get('total_sutras')}")
        print(f"Gaps found: {result['outputs'].get('gap_count')}")
        
        gaps = result['outputs'].get('gaps', [])
        for i, gap in enumerate(gaps):
            print(f"  {i+1}. {gap.get('type')}: {gap.get('suggestion', '')}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n--- Test 2: Sutra Generation ---")
    if gaps:
        result = runtime.solve_sequence(
            ["sutra_016"],
            {"gap": gaps[0]}
        )
        
        if result['status'] == 'success':
            print(f"✅ Generation complete!")
            sutra = result['outputs'].get('sutra', {})
            print(f"Generated Sutra: {sutra.get('name', 'unknown')}")
            print(f"  ID: {sutra.get('sutra_id', 'unknown')}")
            print(f"  Type: {sutra.get('type', 'unknown')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    print("\n--- Test 3: Sutra Validation ---")
    if 'sutra' in locals() and sutra:
        result = runtime.solve_sequence(
            ["sutra_017"],
            {"sutra": sutra}
        )
        
        if result['status'] == 'success':
            print(f"✅ Validation complete!")
            print(f"Valid: {result['outputs'].get('valid')}")
            if result['outputs'].get('errors'):
                print(f"Errors: {result['outputs'].get('errors')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    print("\n--- Test 4: Full Evolution Cycle ---")
    result = runtime.solve_sequence(
        ["sutra_018"],
        {
            "target_domain": "all",
            "max_iterations": 2,
            "auto_promote": False
        }
    )
    
    if result['status'] == 'success':
        print(f"✅ Evolution complete!")
        summary = result['outputs'].get('summary', {})
        print(f"  Attempts: {summary.get('total_attempts')}")
        print(f"  Generated: {summary.get('generated')}")
        print(f"  Promoted: {summary.get('promoted')}")
        print(f"  Failed: {summary.get('failed')}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("🏁 Stage 4 - Evolution Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_evolution()
