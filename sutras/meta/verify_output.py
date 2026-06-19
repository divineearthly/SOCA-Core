"""
Sutra 010: Verify Output
Pramana: Pratyaksha (Direct Perception)
"""

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Verify that the output matches expectations.
    
    Args:
        inputs: dict with 'expected' and 'actual' keys
    
    Returns:
        dict with 'status', 'outputs', 'trace'
    """
    expected = inputs.get('expected', {})
    actual = inputs.get('actual', {})
    
    mismatches = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
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
            "execution_time_ms": 0,
            "passed": passed,
            "mismatches": mismatches
        }
    }
