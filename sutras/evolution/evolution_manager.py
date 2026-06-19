"""
Sutra 018: Evolution Manager
Orchestrates the evolution cycle
"""

import json
import os
import glob
import time
from datetime import datetime

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Run the evolution cycle.
    
    Args:
        inputs: dict with:
            - target_domain: domain to evolve
            - max_iterations: max evolution cycles
            - auto_promote: auto promote valid sutras
    
    Returns:
        dict with evolution results
    """
    target_domain = inputs.get('target_domain', 'all')
    max_iterations = inputs.get('max_iterations', 3)
    auto_promote = inputs.get('auto_promote', False)
    
    results = []
    
    for i in range(max_iterations):
        print(f"\n🔄 Evolution Cycle {i+1}/{max_iterations}")
        
        # Step 1: Discover gaps
        discovery_result = run_discovery(target_domain)
        gaps = discovery_result.get('outputs', {}).get('gaps', [])
        
        if not gaps:
            print("  ✅ No gaps found. System is complete.")
            break
        
        print(f"  📊 Found {len(gaps)} gaps")
        
        # Step 2: Generate sutras
        for gap in gaps:
            print(f"    🔨 Generating sutra for: {gap.get('type', 'unknown')}")
            
            generator_result = run_generator(gap)
            sutra = generator_result.get('outputs', {}).get('sutra', {})
            
            if not sutra:
                print(f"      ❌ Failed to generate sutra")
                continue
            
            # Step 3: Validate
            validator_result = run_validator(sutra)
            valid = validator_result.get('outputs', {}).get('valid', False)
            
            if valid:
                print(f"      ✅ Sutra validated: {sutra.get('name', 'unknown')}")
                
                # Step 4: Promote
                if auto_promote:
                    promotion_result = run_promotion(sutra)
                    if promotion_result.get('status') == 'success':
                        print(f"      📦 Promoted: {sutra.get('sutra_id', 'unknown')}")
                        results.append({
                            'sutra_id': sutra.get('sutra_id'),
                            'name': sutra.get('name'),
                            'gap': gap.get('type'),
                            'status': 'promoted'
                        })
                    else:
                        print(f"      ❌ Promotion failed")
                else:
                    print(f"      ⏳ Auto-promotion disabled. Sutra ready for review.")
                    results.append({
                        'sutra_id': sutra.get('sutra_id'),
                        'name': sutra.get('name'),
                        'gap': gap.get('type'),
                        'status': 'generated'
                    })
            else:
                print(f"      ❌ Validation failed")
                results.append({
                    'sutra_id': sutra.get('sutra_id', 'unknown'),
                    'gap': gap.get('type'),
                    'status': 'failed'
                })
    
    return {
        "status": "success",
        "outputs": {
            "cycles_completed": i + 1,
            "results": results,
            "summary": {
                "total_attempts": len(results),
                "promoted": len([r for r in results if r.get('status') == 'promoted']),
                "generated": len([r for r in results if r.get('status') == 'generated']),
                "failed": len([r for r in results if r.get('status') == 'failed'])
            }
        },
        "trace": {
            "sutra_id": "sutra_018",
            "version": "1.0.0",
            "target_domain": target_domain,
            "timestamp": datetime.now().isoformat()
        }
    }

def run_discovery(target_domain):
    """Run the discovery sutra."""
    from sutras.evolution.sutra_discovery import execute as discovery_execute
    return discovery_execute({'target_domain': target_domain})

def run_generator(gap):
    """Run the generator sutra."""
    from sutras.evolution.sutra_generator import execute as generator_execute
    return generator_execute({'gap': gap})

def run_validator(sutra):
    """Run the validator sutra."""
    from sutras.evolution.sutra_validator import execute as validator_execute
    return validator_execute({'sutra': sutra})

def run_promotion(sutra):
    """Promote a sutra to the registry."""
    try:
        # Save to sutras directory
        sutra_id = sutra.get('sutra_id', 'sutra_unknown')
        filename = os.path.expanduser(f"~/soca/sutras/{sutra_id}.json")
        
        with open(filename, 'w') as f:
            json.dump(sutra, f, indent=2)
        
        # Register with registry
        from registry_manager import RegistryManager
        rm = RegistryManager()
        rm.register_sutra(sutra)
        
        return {"status": "success", "sutra_id": sutra_id}
    except Exception as e:
        return {"status": "failure", "error": str(e)}
