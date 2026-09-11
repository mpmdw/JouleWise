"""Single-test writer/G2/registry cuts, restoring exact source bytes each time."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
WRITER = "scripts/validate_powermetrics_fiducial.py"
PREFLIGHT = "tests.test_validate_powermetrics_fiducial.ContinuedEpochPreflightTests.test_"
CAPTURE = (
    "tests.test_validate_powermetrics_fiducial_derivation_only."
    "DerivationOnlyLiveCaptureTests.test_ordinary_continued_epoch_capture_requires_registered_continuation"
)

# Path, unique original expression, replacement, one defect-shaped test.
CUTS = (
    (WRITER, "identity_epoch not in judged_epochs", "identity_epoch != expected_epoch",
     CAPTURE),
    (WRITER, "identity_epoch not in judged_epochs", "False",
     PREFLIGHT + "unregistered_or_rotated_continuation_refuses_with_epoch_reason"),
    (WRITER, "if preflight_record is not None:", "if False:",
     PREFLIGHT + "ordinary_preflight_accepts_continuation_with_unchanged_screen"),
    (WRITER, '"judged_epochs_basis": "registry_pins_only"', '"judged_epochs_basis": "verified"',
     PREFLIGHT + "ordinary_preflight_accepts_continuation_with_unchanged_screen"),
    (WRITER, '        **preflight_record,\n', '        "judged_epochs": [dict(epoch)],\n',
     PREFLIGHT + "derivation_basis_lists_original_and_continued_judged_epochs"),
    (WRITER, 'if planned_epoch in basis["judged_epochs"]:', 'if planned_epoch == basis["epoch"]:',
     PREFLIGHT + "derivation_only_refuses_continued_epoch_before_capture"),
    (WRITER, 'evidence_payload["acceptance_preflight"] = acceptance_preflight',
     'evidence_payload["acceptance_preflight"] = {}', CAPTURE),
    (WRITER, 'manifest["acceptance_preflight"] = acceptance_preflight',
     'manifest["acceptance_preflight"] = {}', CAPTURE),
    ("scripts/generate_g2a_probe_inputs.py", "        _derive_preflight_systematic_screen_s(planned_epoch)\n",
     "        pass  # mutation: skip writer preflight\n", PREFLIGHT + "g2a_live_vectors_use_real_continuation_preflight"),
    ("docs/contracts/d078_reason_registry_amendment.md", "| `calibration_epoch_continuation_invalid` |",
     "| `continuation_diagnostic_removed` |", "tests.test_d078_reason_registry.D078ReasonRegistryTests.test_epoch_continuation_diagnostic_is_registered"),
)


def main() -> int:
    originals = {ROOT / relative: (ROOT / relative).read_bytes() for relative, *_ in CUTS}
    hashes = {path: hashlib.sha256(raw).digest() for path, raw in originals.items()}
    failures = []
    for index, (relative, expression, replacement, test) in enumerate(CUTS, 1):
        path = ROOT / relative
        source = originals[path].decode()
        if source.count(expression) != 1:
            raise AssertionError(f"W{index:02d}: mutation expression is not unique")
        try:
            path.write_text(source.replace(expression, replacement), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "unittest", test], cwd=ROOT,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True, text=True, check=False,
            )
        finally:
            path.write_bytes(originals[path])
        assert all(hashlib.sha256(item.read_bytes()).digest() == digest for item, digest in hashes.items())
        output = result.stdout + result.stderr
        killed = result.returncode == 1 and "Ran 1 test in " in output and (
            re.search(r"FAILED \(failures=[1-9][0-9]*\)", output) is not None
        )
        print(f"W{index:02d} {'KILLED' if killed else 'SURVIVED'} rc={result.returncode} {test}", flush=True)
        if not killed:
            failures.append(index)
            print(output, flush=True)
    print(f"cuts={len(CUTS)} killed={len(CUTS) - len(failures)} survivors={len(failures)} source_sha256_restored=true", flush=True)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
