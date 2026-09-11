"""Tool-produced continuation fixtures; never register production evidence."""

from contextlib import contextmanager, redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
from unittest.mock import patch

from joulewise import calibration_bracketing as bracket
from scripts import issue_epoch_continuation as issuer
from tests.fixtures.epoch_bootstrap.build import (
    SESSION_ID, Slot, build_derivation_ledger,
)


def build_issued_continuation(
    root: Path, *, acceptance_path: Path = bracket.DEFAULT_ACCEPTANCE_BOUND_PATH,
) -> tuple[dict, dict]:
    """Prepare with real synthetic primary evidence, then remove the marker.

    A copied writer may re-key its acceptance to its private estimator bytes;
    the temporary pin below authenticates only that private test artifact.
    """
    fixture = build_derivation_ledger(root / "night", [Slot("0.025")] * 12)
    raw_acceptance = acceptance_path.read_bytes()
    acceptance = json.loads(raw_acceptance)
    acceptance_id = acceptance["acceptance_id"]
    entry = dict(bracket.ISSUED_ACCEPTANCE_REGISTRY[acceptance_id])
    entry.update(path=acceptance_path, file_sha256=hashlib.sha256(raw_acceptance).hexdigest())
    candidate = root / "candidate.json"
    stdout, stderr = io.StringIO(), io.StringIO()
    with (
        patch.dict(bracket.ISSUED_ACCEPTANCE_REGISTRY, {acceptance_id: entry}),
        redirect_stdout(stdout), redirect_stderr(stderr),
    ):
        rc = issuer.main([
            "prepare-candidate", "--session-id", SESSION_ID,
            "--ledger", str(fixture["ledger"]), "--head-pin", str(fixture["pin"]),
            "--repo-root", str(fixture["root"]), "--acceptance", str(acceptance_path),
            "--d102-addendum-date", "2026-09-10", "--out", str(candidate),
        ])
    if rc != 0:
        raise AssertionError(f"fixture continuation failed rc={rc}: {stderr.getvalue()}")
    value = json.loads(candidate.read_bytes())
    del value["candidate_not_issued"]
    value["derivation_sha256"] = bracket._canonical_sha256(
        {key: item for key, item in value.items() if key != "derivation_sha256"}
    )
    path = root / "issued.json"
    raw = (json.dumps(value, indent=2) + "\n").encode()
    path.write_bytes(raw)
    registry = {value["continuation_id"]: {
        "path": path, "relative_path": "tests/fixtures/epoch_continuation/issued.json",
        "file_sha256": hashlib.sha256(raw).hexdigest(),
    }}
    return value, registry


@contextmanager
def registered_continuation(root: Path):
    value, registry = build_issued_continuation(root)
    with patch.dict(bracket.EPOCH_CONTINUATION_REGISTRY, registry, clear=True):
        yield value, registry[value["continuation_id"]]["path"]


def append_open_capture_session(fixture: dict):
    """Extend a terminal test ledger with a reserved capture still in flight."""
    from joulewise.calibration_ledger import (
        append_bracket_session_receipt, load_calibration_ledger_snapshot,
    )
    from tests.fixtures.epoch_bootstrap.build import TARGET_EPOCH, T1_BINDINGS

    runs = fixture["runs"]
    append_bracket_session_receipt(
        fixture["ledger"], session_id="capture-in-flight", window_id="capture-window",
        plan_id="capture-plan", plan_sha256="a" * 64, evidence_root_id="capture-evidence",
        runs_root=runs,
        slots={name: {"attempt_id": f"capture-{name}",
                      "custody_locator": str(runs / "instrument_validation" / f"capture-{name}"),
                      "identity_epoch": TARGET_EPOCH, "t1_bindings": T1_BINDINGS}
               for name in ("pre", "post")},
        head_pin_path=fixture["pin"], require_committed_pin=True, repo_root=fixture["root"],
    )
    return load_calibration_ledger_snapshot(
        fixture["ledger"], fixture["pin"], require_committed_pin=True,
        verify_custody=False, mode="read_replay", repo_root=fixture["root"],
    )
