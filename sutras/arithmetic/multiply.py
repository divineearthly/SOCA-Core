def execute(inputs, context=None):
    a = inputs.get('a', 0)
    b = inputs.get('b', 0)
    return {
        "status": "success",
        "outputs": {"product": a * b},
        "trace": {"sutra_id": "sutra_003", "version": "1.0.0"}
    }
