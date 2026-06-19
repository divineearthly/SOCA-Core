"""
Sutra 001: Integer Addition
Pramana: Pratyaksha (Direct Perception)
"""

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Add two integers.
    
    Args:
        inputs: dict with 'a' and 'b' keys
        context: optional dict for state
    
    Returns:
        dict with 'status', 'outputs', 'trace'
    """
    a = inputs.get('a')
    b = inputs.get('b')
    
    # Validate inputs
    if not isinstance(a, int) or not isinstance(b, int):
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_001",
                "version": "1.0.0",
                "error": "Inputs must be integers",
                "inputs": inputs
            }
        }
    
    # Execute
    result = a + b
    
    return {
        "status": "success",
        "outputs": {"sum": result},
        "trace": {
            "sutra_id": "sutra_001",
            "version": "1.0.0",
            "execution_time_ms": 0,
            "inputs": inputs,
            "outputs": {"sum": result}
        }
    }
