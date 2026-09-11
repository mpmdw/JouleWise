"""Single-test writer/G2/registry cuts, restoring exact source bytes each time."""

from __future__ import annotations

import hashlib
import argparse
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
ORDINARY_KEYS = (
    "tests.test_validate_powermetrics_fiducial_derivation_only."
    "DerivationOnlyLiveCaptureTests.test_ordinary_artifact_top_level_key_sets_require_deliberate_schema_changes"
)

# Path, unique original expression, replacement, one defect-shaped test.
CUTS = (
    (WRITER, "identity_epoch not in judged_epochs", "identity_epoch != expected_epoch",
     CAPTURE),
    (WRITER, "identity_epoch not in judged_epochs", "False",
     PREFLIGHT + "unregistered_or_rotated_continuation_refuses_with_epoch_reason"),
    (WRITER, "if preflight_record is not None:", "if False:",
     PREFLIGHT + "ordinary_preflight_accepts_continuation_with_unchanged_screen"),
    (WRITER, '"ledger_snapshot" if ledger_snapshot is not None else "registry_pins_only"',
     '"ledger_snapshot"',
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
    (WRITER, "artifact, ledger_snapshot=ledger_snapshot, refusal_details=continuation_refusals,",
     "artifact, ledger_snapshot=None, refusal_details=continuation_refusals,",
     PREFLIGHT + "snapshot_preflight_refuses_absent_or_nonterminal_continuation_session"),
    (WRITER, '"ledger_snapshot" if ledger_snapshot is not None else "registry_pins_only"',
     '"registry_pins_only"', PREFLIGHT + "snapshot_preflight_authenticates_terminal_session_and_records_basis"),
    (WRITER, "        ledger_snapshot=ledger_snapshot,\n", "        ledger_snapshot=None,\n",
     PREFLIGHT + "derivation_basis_forwards_snapshot_and_refuses_unbacked_continuation"),
    (WRITER, "not isinstance(expected_epoch, Mapping)\n        or not isinstance(acceptance_id, str)",
     "not isinstance(expected_epoch, Mapping)\n        or False",
     PREFLIGHT + "invalid_acceptance_id_returns_named_cli_refusal_without_traceback"),
    (WRITER, 'expected_epoch = artifact.get("identity_epoch")\n    acceptance_id = artifact.get("acceptance_id")',
     'expected_epoch = artifact.get("identity_epoch")\n    acceptance_id = artifact["acceptance_id"]',
     PREFLIGHT + "invalid_acceptance_id_returns_named_cli_refusal_without_traceback"),
    (WRITER, 'evidence_payload["acceptance_preflight"] = acceptance_preflight',
     'evidence_payload["acceptance_preflight"] = acceptance_preflight\n        evidence_payload["unexpected"] = True',
     ORDINARY_KEYS),
    (WRITER, 'manifest["acceptance_preflight"] = acceptance_preflight',
     'manifest["acceptance_preflight"] = acceptance_preflight\n        manifest["unexpected"] = True',
     ORDINARY_KEYS),
    ("docs/contracts/powermetrics_fiducial.md", '["acceptance_id", "artifact_sha256", "preflight_level_screen_s", "epoch", "judged_epochs", "judged_epochs_basis", "continuation_refusals"]',
     '["acceptance_id", "artifact_sha256", "preflight_level_screen_s", "epoch"]',
     PREFLIGHT + "contract_documented_key_lists_equal_emitted_preflight_and_screen_basis"),
    ("docs/contracts/powermetrics_fiducial.md", '["acceptance_id", "judged_epochs", "judged_epochs_basis", "continuation_refusals"]',
     '["acceptance_id", "judged_epochs", "judged_epochs_basis"]',
     PREFLIGHT + "contract_documented_key_lists_equal_emitted_preflight_and_screen_basis"),
    ("scripts/write_derivation_night_inputs.py", "            planned_epoch, acceptance_path=acceptance_path\n",
     '            {**planned_epoch, "os_build": "new-unjudged-build"}, acceptance_path=acceptance_path\n',
     "tests.test_write_derivation_night_inputs.WriteDerivationNightInputsTests.test_continued_epoch_is_an_ordinary_night_and_writes_no_derivation_inputs"),
    (WRITER, "not isinstance(expected_epoch, Mapping)\n        or not isinstance(acceptance_id, str)\n        or not acceptance_id",
     "not isinstance(expected_epoch, Mapping)\n        or not isinstance(acceptance_id, str)\n        or False",
     PREFLIGHT + "invalid_acceptance_id_returns_named_cli_refusal_without_traceback"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cuts", nargs="+", choices=[f"W{i:02d}" for i in range(1, len(CUTS) + 1)],
                        help="Run only these cuts, leaving every other path untouched.")
    args = parser.parse_args()
    selected = [(index, cut) for index, cut in enumerate(CUTS, 1)
                if args.cuts is None or f"W{index:02d}" in args.cuts]
    originals = {ROOT / relative: (ROOT / relative).read_bytes() for _, (relative, *_) in selected}
    hashes = {path: hashlib.sha256(raw).digest() for path, raw in originals.items()}
    failures = []
    for index, (relative, expression, replacement, test) in selected:
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
    print(f"cuts={len(selected)} killed={len(selected) - len(failures)} survivors={len(failures)} source_sha256_restored=true", flush=True)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
