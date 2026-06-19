"""
Standard Response Contract for all Sutras
"""

def success_response(outputs: dict, confidence: float = 1.0, metadata: dict = None):
    return {
        "status": "success",
        "outputs": outputs,
        "confidence": confidence,
        "metadata": metadata or {}
    }

def failure_response(error: str, metadata: dict = None):
    return {
        "status": "failure",
        "outputs": {"error": error},
        "confidence": 0.0,
        "metadata": metadata or {}
    }
