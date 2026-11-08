"""Tiny synthetic compute and virtual time; never a measurement fixture."""
from pathlib import Path

from joulewise.align.squeeze.config import CONTROL_SCHEMA, load_kit, seal

KIT = Path(__file__).resolve().parents[2] / "configs/align/squeeze"


def variant(name="meter-aware"):
    return load_kit(KIT)[name + ".v1.json"]


def control_config(k=5, call=0):
    return seal({"schema": CONTROL_SCHEMA, "status": "DRAFT", "id": "test-control",
                 "revision": 1, "decode_tokens": k, "prompt_token_ids": [1, 2, 3],
                 "before_chat_call": call, "max_context_tokens": 64})


class VirtualClock:
    def __init__(self):
        self.ns = 100

    def __call__(self):
        return self.ns

    def advance(self, amount=10):
        self.ns += amount


class TinyDecoder:
    """Integer recurrent toy model; fresh state and a real forward per yield.

    Synthetic arithmetic is an execution/accounting test, with no energy model.
    """
    identity = "synthetic-integer-rnn-v1"
    vocab_size = 8
    max_context_tokens = 64

    def __init__(self, clock=None, on_forward=lambda: None):
        self.clock, self.on_forward = clock, on_forward
        self.forward_inputs = []

    def decode(self, prompt, *, max_tokens):
        state, inputs = [0, 0, 0], list(prompt)
        for _ in range(max_tokens):
            self.on_forward()
            self.forward_inputs.append(tuple(inputs))
            for token in inputs:
                state = [sum((i + j + 1) * x for j, x in enumerate(state)) % 17 + token
                         for i in range(3)]
            logits = [sum((i + j + 1) * x for j, x in enumerate(state)) % 23
                      for i in range(self.vocab_size)]
            token = max(range(self.vocab_size), key=logits.__getitem__)
            if self.clock is not None:
                self.clock.advance()
            yield token
            inputs = [token]
