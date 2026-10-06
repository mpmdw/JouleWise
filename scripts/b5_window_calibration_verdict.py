#!/usr/bin/env python3
"""Write a block-5 window's calibration verdict (gate-prune 2, interface J1).

Every member of a window attaches the same pre-slot calibration, and before
this step each member re-ran the same pulse refit of that capture three times
(PLAN2 M1-M3). The chain runs this program once, synchronously, right after
the pre-calibration screen and before the first settle (so it never overlaps a
sampler stream). It:

1. reads the pre-slot directory's ``manifest.json`` and every artifact it
   lists, each bound to the manifest's SHA-256 and kept inside the directory
   (the checks ``controller._load_instrument_calibration_attachment`` makes);
2. runs ``powermetrics_fiducial.verify_stored_evidence_physics`` on the stored
   evidence, the raw powermetrics plist and the events: the refit of the raw
   physics, which returns the widen-only effective bound;
3. writes ``window_calibration_verdict.json`` beside the pre-slot directory,
   create-once: the four artifact digests the members' installed copies must
   match, the estimator code digests the refit ran with, the effective bound,
   and ``flags`` (why it is not verified, when it is not).

The verdict is a cache key, never a gate. A member (lane P2-CTL) uses it only
when its own installed copy hashes to the same four digests and its estimator
code to the same digests; otherwise it refits as before. A verdict that is not
verified changes nothing: members refit and decide exactly as they did. The
harvest never reads this file; it refits from raw bytes.

Exit: 0 verified; 1 written, not verified; 3 a verdict already exists (never
overwritten); 2 usage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SCHEMA = "joulewise.b5_window_calibration_verdict.v1"
VERDICT_BASENAME = "window_calibration_verdict.json"
MANIFEST_SCHEMA = "joulewise.instrument_validation_manifest.v1"
EVIDENCE = "instrument_evidence.json"
RAW_PLIST = "raw/powermetrics.plist"
EVENTS = "events.jsonl"
VERIFIER = "joulewise.powermetrics_fiducial.verify_stored_evidence_physics"
EXIT_VERIFIED, EXIT_NOT_VERIFIED, EXIT_USAGE, EXIT_EXISTS = 0, 1, 2, 3


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def default_output(pre_calibration_dir: Path) -> Path:
    return Path(pre_calibration_dir).parent / VERDICT_BASENAME


def _default_verifier() -> Callable[[Mapping[str, Any], bytes, bytes], float]:
    from joulewise.powermetrics_fiducial import verify_stored_evidence_physics

    return verify_stored_evidence_physics


def _default_estimator_digests() -> dict[str, str] | None:
    from joulewise.calibration_bracketing import _current_estimator_code_sha256

    return _current_estimator_code_sha256()


def read_artifacts(directory: Path) -> tuple[bytes, dict[str, bytes]]:
    """The manifest bytes and every artifact it lists, hash-bound; raises ValueError."""

    root = Path(directory)
    try:
        resolved = root.resolve(strict=True)
        manifest_raw = (root / "manifest.json").read_bytes()
        manifest = json.loads(manifest_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"manifest_unreadable: {type(exc).__name__}") from exc
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if not isinstance(manifest, dict) or manifest.get("schema_version") != MANIFEST_SCHEMA \
            or not isinstance(artifacts, dict):
        raise ValueError("manifest_schema_invalid")
    files: dict[str, bytes] = {}
    for relative, expected in artifacts.items():
        path = Path(relative) if isinstance(relative, str) else None
        if path is None or path.is_absolute() or ".." in path.parts or not isinstance(expected, str) \
                or len(expected) != 64:
            raise ValueError("artifact_descriptor_invalid")
        try:
            candidate = (resolved / path).resolve(strict=True)
            if resolved not in candidate.parents:
                raise ValueError(f"artifact_escapes_directory: {relative}")
            raw = candidate.read_bytes()
        except OSError as exc:
            raise ValueError(f"artifact_unreadable: {relative}") from exc
        if _sha256(raw) != expected:
            raise ValueError(f"artifact_hash_mismatch: {relative}")
        files[path.as_posix()] = raw
    for required in (EVIDENCE, RAW_PLIST, EVENTS):
        if required not in files:
            raise ValueError(f"manifest_omits: {required}")
    return manifest_raw, files


def build_verdict(directory: Path, *, verifier: Callable[[Mapping[str, Any], bytes, bytes], float] | None = None,
                  estimator_digests: Callable[[], dict[str, str] | None] | None = None,
                  now: Callable[[], float] = time.time) -> dict[str, Any]:
    """The verdict for one pre-slot directory. Never raises on the capture's content."""

    started = now()
    verdict: dict[str, Any] = {
        "schema": SCHEMA, "status": "not_verified", "pre_calibration_dir": str(directory),
        "evidence_sha256": None, "manifest_sha256": None, "raw_plist_sha256": None, "events_sha256": None,
        "estimator_files_sha256": None, "stored_b_fiducial_s": None, "effective_b_fiducial_s": None,
        "verifier": VERIFIER, "flags": [], "started_epoch_s": started, "ended_epoch_s": None,
    }
    try:
        manifest_raw, files = read_artifacts(Path(directory))
    except ValueError as exc:
        verdict["flags"].append(str(exc))
        verdict["ended_epoch_s"] = now()
        return verdict
    verdict.update(manifest_sha256=_sha256(manifest_raw), evidence_sha256=_sha256(files[EVIDENCE]),
                   raw_plist_sha256=_sha256(files[RAW_PLIST]), events_sha256=_sha256(files[EVENTS]))
    try:
        digests = (estimator_digests or _default_estimator_digests)()
    except Exception as exc:  # noqa: BLE001 - recorded; the verdict is then unusable as a key
        digests = None
        verdict["flags"].append(f"estimator_code_unreadable: {type(exc).__name__}")
    if not isinstance(digests, dict) or not digests:
        if not any(flag.startswith("estimator_code_unreadable") for flag in verdict["flags"]):
            verdict["flags"].append("estimator_code_unreadable")
        digests = None
    verdict["estimator_files_sha256"] = digests
    try:
        evidence = json.loads(files[EVIDENCE])
    except (UnicodeDecodeError, json.JSONDecodeError):
        evidence = None
    if not isinstance(evidence, dict):
        verdict["flags"].append("evidence_invalid_json")
        verdict["ended_epoch_s"] = now()
        return verdict
    stored = evidence.get("b_fiducial_s")
    verdict["stored_b_fiducial_s"] = stored if isinstance(stored, (int, float)) and not isinstance(stored, bool) \
        else None
    try:
        effective = (verifier or _default_verifier())(evidence, files[RAW_PLIST], files[EVENTS])
    except (KeyError, TypeError, ValueError) as exc:
        verdict["flags"].append(f"physics_not_reproduced: {type(exc).__name__}: {exc}"[:300])
        verdict["ended_epoch_s"] = now()
        return verdict
    except Exception as exc:  # noqa: BLE001 - any other failure is a miss, recorded
        verdict["flags"].append(f"verifier_raised: {type(exc).__name__}: {exc}"[:300])
        verdict["ended_epoch_s"] = now()
        return verdict
    verdict["effective_b_fiducial_s"] = float(effective)
    if digests is not None:
        verdict["status"] = "verified"
    verdict["ended_epoch_s"] = now()
    return verdict


def write_create_once(path: Path, verdict: Mapping[str, Any]) -> None:
    raw = (json.dumps(verdict, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def main(argv: Sequence[str] | None = None, *,
         verifier: Callable[[Mapping[str, Any], bytes, bytes], float] | None = None,
         estimator_digests: Callable[[], dict[str, str] | None] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--pre-calibration-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None,
                        help=f"default: <pre-calibration-dir>/../{VERDICT_BASENAME}")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE if exc.code else 0
    output = args.output if args.output is not None else default_output(args.pre_calibration_dir)
    if os.path.lexists(output):
        print(f"b5 window calibration verdict: {output} exists; never overwritten", file=sys.stderr)
        return EXIT_EXISTS
    verdict = build_verdict(args.pre_calibration_dir, verifier=verifier, estimator_digests=estimator_digests)
    try:
        write_create_once(output, verdict)
    except FileExistsError:
        print(f"b5 window calibration verdict: {output} appeared; never overwritten", file=sys.stderr)
        return EXIT_EXISTS
    print(json.dumps({"path": str(output), "status": verdict["status"], "flags": verdict["flags"]}, sort_keys=True))
    return EXIT_VERIFIED if verdict["status"] == "verified" else EXIT_NOT_VERIFIED


if __name__ == "__main__":
    sys.exit(main())
