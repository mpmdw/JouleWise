"""MLX-LM adapter for the qwen4 quant-quality harness."""

def teacher_forced_logits(model_path, input_ids):
    import mlx.core as mx
    from mlx_lm import load
    model, _ = load(model_path, lazy=True)
    value = model(mx.array([input_ids]))
    logits = value.logits if hasattr(value, "logits") else value
    mx.eval(logits)
    result = logits.astype(mx.float32)
    # Copy to host before releasing Metal allocations.
    import numpy as np
    output = np.array(result)
    del model, value, logits, result
    mx.clear_cache()
    return output
