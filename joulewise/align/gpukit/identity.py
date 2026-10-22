"""Match a configured model ID to an endpoint's serialized serving identity."""

from __future__ import annotations

import re


def model_identity_matches(identity: str, model: str) -> bool:
    """Accept a bare ID or a delimited ID inside a serving identity.

    ChatEndpoint guarantees identity, not a .model attribute. Delimiters preserve
    model identity while excluding similarly named checkpoints (e.g. 8B-FP8).
    """
    return bool(re.search(r"(?:^|[:@|\s])" + re.escape(model) + r"(?=$|[@:|\s])",
                          identity))
