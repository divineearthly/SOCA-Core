"""
sutra_086: Tri-Nadi Activation
Pramana: Pratyaksha (Direct Perception)
Three-channel activation based on Ida, Pingala, Sushumna
"""

import numpy as np

def execute(inputs: dict, context: dict = None) -> dict:
    """
    Apply Tri-Nadi activation.
    
    Args:
        inputs: dict with 'x' input tensor
    
    Returns:
        dict with activated output
    """
    x = inputs.get('x')
    
    if x is None:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_086",
                "version": "1.0.0",
                "error": "Input required"
            }
        }
    
    try:
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        
        # Tri-Nadi: three activation channels
        # Ida (Moon): inhibitory - negative values emphasized
        # Pingala (Sun): excitatory - positive values emphasized
        # Sushumna (Center): balanced - maintains original values
        
        ida = np.minimum(x, 0) * 0.1      # Inhibitory
        pingala = np.maximum(x, 0) * 1.0   # Excitatory
        sushumna = x * 0.5                 # Balanced
        
        # Combine with gating
        gate = np.tanh(x)  # 0.8 for positive, -0.8 for negative
        output = ida * (gate < -0.3) + pingala * (gate > 0.3) + sushumna * (np.abs(gate) <= 0.3)
        
        return {
            "status": "success",
            "outputs": {
                "result": output.tolist(),
                "shape": list(output.shape),
                "channels": ["ida", "pingala", "sushumna"]
            },
            "trace": {
                "sutra_id": "sutra_086",
                "version": "1.0.0"
            }
        }
    except Exception as e:
        return {
            "status": "failure",
            "outputs": {},
            "trace": {
                "sutra_id": "sutra_086",
                "version": "1.0.0",
                "error": str(e)
            }
        }
