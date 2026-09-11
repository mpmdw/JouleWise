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
