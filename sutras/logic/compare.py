"""
Sutra 005: Integer Comparison
Pramana: Anumana (Inference)
"""

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Compare two integers.
    
    Args:
        inputs: dict with 'a', 'b', and 'operator' keys
            operator: 'eq', 'gt', 'lt', 'gte', 'lte'
    
    Returns:
        dict with 'status', 'outputs', 'trace'
    """
    a = inputs.get('a')
    b = inputs.get('b')
    operator = inputs.get('operator', 'eq')
    
    # Validate inputs
    if not isinstance(a, int) or not isinstance(b, int):
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_005",
                "version": "1.0.0",
                "error": "Inputs must be integers"
            }
        }
    
    # Execute comparison
    operators = {
        'eq': a == b,
        'gt': a > b,
        'lt': a < b,
        'gte': a >= b,
        'lte': a <= b
    }
    
    result = operators.get(operator, False)
    
    return {
        "status": "success",
        "outputs": {"result": result},
        "trace": {
            "sutra_id": "sutra_005",
            "version": "1.0.0",
            "execution_time_ms": 0,
            "inputs": inputs,
            "outputs": {"result": result}
        }
    }
