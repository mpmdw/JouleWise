"""The fixed five-term designs, with coefficients supplied by the caller.

No fitter or measurement loader is provided. The protocol v4 sequence form is
primary; the older per-turn context product form is an explicit sensitivity.
"""

from dataclasses import dataclass

import numpy as np

from .detection import finite


def nonnegative(value, name):
    value = finite(value, name)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def design(prefill, decode, context, *, form="sequence"):
    """Return [..., 5] rows. Fractional counts support planning boundaries.

    sequence: [1, P, D, (C+P)D+D^2/2, CP+P^2/2]
    turn:     [1, P, D, CD, CP]
    """
    p, d, c = np.broadcast_arrays(*[np.asarray(v, dtype=float)
                                  for v in (prefill, decode, context)])
    if any(not np.isfinite(v).all() or np.any(v < 0) for v in (p, d, c)):
        raise ValueError("token counts must be finite and nonnegative")
    if form == "sequence":
        cd, cp = (c + p) * d + d * d / 2, c * p + p * p / 2
    elif form == "turn":
        cd, cp = c * d, c * p
    else:
        raise ValueError("form must be sequence or turn")
    out = np.stack((np.ones_like(p), p, d, cd, cp), axis=-1)
    if not np.isfinite(out).all():
        raise ValueError("design overflows")
    return out


@dataclass(frozen=True)
class ResidualModel:
    coefficients: tuple
    form: str = "sequence"

    def __post_init__(self):
        beta = tuple(finite(b, "coefficient") for b in self.coefficients)
        if len(beta) != 5:
            raise ValueError("exactly five coefficients are required")
        object.__setattr__(self, "coefficients", beta)
        design(0, 0, 0, form=self.form)

    def predict(self, prefill, decode, context):
        return design(prefill, decode, context, form=self.form) @ self.coefficients

    def hidden_increment(self, hidden_tokens, *, prefill, decode, context):
        """Extra continuation at one carrier call, without another intercept.

        This stable difference keeps the sequence quadratic H^2/2 term.
        It assumes no downstream context propagation or batch changes.
        """
        h = nonnegative(hidden_tokens, "hidden_tokens")
        p = nonnegative(prefill, "prefill")
        d = nonnegative(decode, "decode")
        c = nonnegative(context, "context")
        context_work = (c + p + d) * h + h * h / 2 if self.form == "sequence" else c * h
        return self.coefficients[2] * h + self.coefficients[3] * context_work


@dataclass(frozen=True)
class Carrier:
    """One synthetic representative call; not a full SHADE trajectory."""

    prefill: float = 128.0
    decode: float = 512.0
    context: float = 4096.0

    def __post_init__(self):
        for name in ("prefill", "decode", "context"):
            nonnegative(getattr(self, name), name)
