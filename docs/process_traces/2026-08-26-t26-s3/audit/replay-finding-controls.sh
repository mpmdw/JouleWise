#!/bin/sh
set -eu

/Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'
from pathlib import Path
from unittest import mock

import joulewise.arm_readiness as readiness
from joulewise import arm_readiness_evidence as evidence

raw = (
    "CURRENT_FROZEN_RECEIPT_SHA256 = " + repr("a" * 64) + "\nprint('ok')\n"
).encode()
try:
    evidence._generator_invocation(
        "g.py",
        raw,
        kind="PACK_AUTHENTICATION",
        preserve_current_frozen_bytes=False,
    )
except evidence.EvidenceAuthoringError as exc:
    print("C5", exc.reason_code, str(exc))

pack = Path("configs/campaigns/d117_floor_qwen25_1p5b_v1")
with mock.patch.object(
    readiness.tempfile,
    "TemporaryDirectory",
    side_effect=OSError("simulated tmp exhaustion"),
):
    try:
        readiness.verify_receipt_histsem_pack(pack)
    except Exception as exc:
        print("TMP", type(exc).__name__, getattr(exc, "reason_code", None), str(exc))
PY
