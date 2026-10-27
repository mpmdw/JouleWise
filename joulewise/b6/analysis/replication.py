"""The replication word for each GAMMA contrast (registration §11.2).

"replicated" means every counting block-6 GAMMA session gives the same
outcome word as block 5's analysed GAMMA session and the same sign of dbar;
otherwise "not replicated", with each session's word and sign.  If block 5's
contrast is ``not_estimable`` (it has no dbar), no word is used and the
sessions' words are printed.  A GAMMA pack short of its target says so.  The
flagged-inclusive sessions' words are printed beside and never enter the word.
Every value here is restricted until the release (§12.1).
"""
from __future__ import annotations

import math

from joulewise.b6.analysis.adapter import SessionAnalysis

REPLICATED, NOT_REPLICATED = "replicated", "not replicated"
NOT_ESTIMABLE = "not_estimable"
COMMITMENT = 2      # registration §5.1: minimum 2 counting sessions per pack


def sign(value) -> int | None:
    if not isinstance(value, float) or not math.isfinite(value):
        return None
    return (value > 0) - (value < 0)


def _row(analysis: SessionAnalysis, contrast_id: str, floor_from_block5: bool) -> dict:
    contrast = analysis.contrasts.get(contrast_id, {})
    return {"session_id": analysis.session_id, "outcome": contrast.get("outcome"),
            "sign": sign(contrast.get("dbar")), "floor_from_block_5": floor_from_block5}


def contrast_word(contrast_id: str, block5: SessionAnalysis, counting: list[SessionAnalysis], *,
                  target: int, floor_from_block5: dict[str, bool] | None = None,
                  inclusive: list[SessionAnalysis] = ()) -> dict:
    labels = floor_from_block5 or {}
    reference = block5.contrasts.get(contrast_id, {})
    b5_outcome, b5_sign = reference.get("outcome"), sign(reference.get("dbar"))
    rows = [_row(s, contrast_id, labels.get(s.session_id, False)) for s in counting]
    record = {"contrast": contrast_id, "block5": {"outcome": b5_outcome, "sign": b5_sign}, "sessions": rows,
              "flagged_inclusive_sessions": [_row(s, contrast_id, labels.get(s.session_id, False)) for s in inclusive],
              "short": None, "word": None, "reason": None,
              "floor_from_block_5": any(row["floor_from_block_5"] for row in rows)}
    if len(counting) < target:
        record["short"] = f"short: {len(counting)} counting block-6 sessions of the {target} targeted"
        if len(counting) < COMMITMENT:
            record["short"] += "; below the commitment of 2"
    if b5_outcome is None or b5_outcome == NOT_ESTIMABLE or b5_sign is None:
        record["reason"] = "block5_not_estimable"
    elif not rows:
        record["reason"] = "no_counting_session"
    else:
        same = all(row["outcome"] == b5_outcome and row["sign"] == b5_sign for row in rows)
        record["word"] = REPLICATED if same else NOT_REPLICATED
    return record
