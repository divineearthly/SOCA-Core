"""
Sutra 010: Verify Output
Pramana: Pratyaksha (Direct Perception)
Normalizes schedules before comparison
"""

def execute(inputs: dict, context: dict = None) -> dict:
    expected = inputs.get('expected', {})
    actual = inputs.get('actual', {})
    
    mismatches = []
    
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        
        # Normalize schedule: sort each level for parallel execution
        if key == 'schedule' and isinstance(expected_value, list) and isinstance(actual_value, list):
            normalized_expected = [sorted(level) for level in expected_value]
            normalized_actual = [sorted(level) for level in actual_value]
            
            if normalized_expected != normalized_actual:
                mismatches.append({
                    'key': key,
                    'expected': expected_value,
                    'actual': actual_value,
                    'normalized_expected': normalized_expected,
                    'normalized_actual': normalized_actual
                })
        else:
            if actual_value != expected_value:
                mismatches.append({
                    'key': key,
                    'expected': expected_value,
                    'actual': actual_value
                })
    
    passed = len(mismatches) == 0
    
    return {
        "status": "success",
        "outputs": {
            "verified": passed,
            "mismatches": mismatches
        },
        "trace": {
            "sutra_id": "sutra_010",
            "version": "1.0.0",
            "passed": passed,
            "mismatches": mismatches
        }
    }
