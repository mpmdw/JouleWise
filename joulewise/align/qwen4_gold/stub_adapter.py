"""Wiring probe only. Intentionally incomplete; can NEVER earn parity PASS."""
GOLD_ADAPTER_VERSION = 1
GOLD_ADAPTER_KIND = "stub"


def run_gold(request, checkpoint):
    import numpy as np
    if request["unit"] == "embed":
        embedding = checkpoint.rows(checkpoint.prefix + "embed_tokens.weight", request["input_ids"])
        return {"embedding": embedding, "output": np.tile(embedding, (1, 1, checkpoint.text["hc_count"]))}, {"device": "numpy stub"}
    hidden = np.load(request["hidden"], allow_pickle=False)
    return {"output": hidden.copy()}, {"device": "numpy stub", "reason": "port adapter not supplied"}
