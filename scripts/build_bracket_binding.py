#!/usr/bin/env python3
"""Build one canonical calibration-bracket binding under H6 custody."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import stat
import sys
from pathlib import Path
from typing import Any, Mapping, NoReturn, Sequence

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_bracketing import (  # noqa: E402
    build_calibration_bracket_binding,
    validate_calibration_bracket_binding,
)
from joulewise.calibration_ledger import (  # noqa: E402
    CalibrationLedgerSnapshot,
    canonical_json_bytes,
    canonical_sha256,
    load_calibration_ledger_snapshot,
)


WHOLE_WINDOW_SCHEMA = "joulewise.idle_admission_whole_window_verdict.v1"
DESCRIPTOR_IDENTITY_FIELDS = (
    "bracket_session_id",
    "bracket_window_id",
    "bracket_plan_id",
    "bracket_plan_sha256",
    "bracket_evidence_root_id",
    "bracket_runs_root",
)
DESCRIPTOR_ENDPOINT_FIELDS = (
    "attempt_id",
    "ledger_receipt_digest",
    "content_id",
)

REFUSAL_INPUT_INVALID = "bracket_binding_input_invalid"
REFUSAL_CUSTODY_INVALID = "bracket_binding_custody_invalid"
REFUSAL_DESCRIPTOR_INVALID = "bracket_binding_descriptor_invalid"
REFUSAL_DESCRIPTOR_MISMATCH = "bracket_binding_descriptor_mismatch"
REFUSAL_LEDGER_REFUSED = "bracket_binding_ledger_refused"
REFUSAL_SESSION_IDENTITY_MISMATCH = "bracket_binding_session_identity_mismatch"
REFUSAL_SESSION_NOT_FINALIZED = "bracket_binding_session_not_finalized"
REFUSAL_SESSION_ENDPOINTS_INVALID = "bracket_binding_session_endpoints_invalid"
REFUSAL_ENDPOINT_MISMATCH = "bracket_binding_endpoint_mismatch"
REFUSAL_BUILD_REFUSED = "bracket_binding_build_refused"
REFUSAL_OUTPUT_EXISTS = "bracket_binding_output_exists"
REFUSAL_OUTPUT_FAILED = "bracket_binding_output_failed"
REFUSAL_INVOCATION_INVALID = "bracket_binding_invocation_invalid"
REFUSAL_INTERNAL_ERROR = "bracket_binding_internal_error"


class BracketBindingRefusal(Exception):
    """One registered, operator-visible refusal."""

    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


class JsonArgumentParser(argparse.ArgumentParser):
    """Report invalid invocations through the CLI's refusal protocol."""

    def error(self, message: str) -> NoReturn:
        raise BracketBindingRefusal(REFUSAL_INVOCATION_INVALID, message)


def _refuse(reason: str, detail: str) -> NoReturn:
    raise BracketBindingRefusal(reason, detail)


def _strict_json_object(raw: bytes, *, label: str) -> Mapping[str, Any]:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    def nonfinite(value: str) -> NoReturn:
        raise ValueError(f"non-finite JSON number {value!r}")

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=object_pairs,
            parse_constant=nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _refuse(REFUSAL_INPUT_INVALID, f"{label} is not strict JSON: {exc}")
    if not isinstance(value, Mapping):
        _refuse(REFUSAL_INPUT_INVALID, f"{label} must contain one JSON object")
    return value


def _custody_root(path: Path) -> tuple[Path, Path]:
    lexical = Path(path).absolute()
    try:
        mode = lexical.lstat().st_mode
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise ValueError("must be a non-symlink directory")
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        _refuse(REFUSAL_CUSTODY_INVALID, f"custody root {lexical}: {exc}")
    return lexical, resolved


def _relative_to_custody(
    path: Path, lexical_root: Path, resolved_root: Path, *, label: str
) -> tuple[Path, Path]:
    candidate = Path(path)
    candidate = candidate if candidate.is_absolute() else lexical_root / candidate
    try:
        try:
            relative = candidate.relative_to(lexical_root)
        except ValueError:
            relative = candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise BracketBindingRefusal(
            REFUSAL_CUSTODY_INVALID, f"{label} is outside custody"
        ) from exc
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        _refuse(REFUSAL_CUSTODY_INVALID, f"{label} is not a canonical custody path")
    return candidate, relative


def _existing_custody_path(
    path: Path,
    lexical_root: Path,
    resolved_root: Path,
    *,
    label: str,
    directory: bool,
) -> Path:
    candidate, relative = _relative_to_custody(
        path, lexical_root, resolved_root, label=label
    )
    current = resolved_root
    try:
        for part in relative.parts:
            current = current / part
            if stat.S_ISLNK(current.lstat().st_mode):
                raise ValueError("symlinks are forbidden")
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
        mode = resolved.stat().st_mode
    except (OSError, RuntimeError, ValueError) as exc:
        _refuse(REFUSAL_CUSTODY_INVALID, f"{label}: {exc}")
    wanted = stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)
    if not wanted:
        kind = "directory" if directory else "regular file"
        _refuse(REFUSAL_CUSTODY_INVALID, f"{label} must be a {kind}")
    return resolved


def _new_custody_file(
    path: Path, lexical_root: Path, resolved_root: Path, *, label: str
) -> Path:
    candidate, relative = _relative_to_custody(
        path, lexical_root, resolved_root, label=label
    )
    parent_relative = relative.parent
    parent = resolved_root
    try:
        for part in parent_relative.parts:
            parent = parent / part
            mode = parent.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise ValueError("parent components must be non-symlink directories")
        resolved_parent = candidate.parent.resolve(strict=True)
        resolved_parent.relative_to(resolved_root)
    except (OSError, RuntimeError, ValueError) as exc:
        _refuse(REFUSAL_CUSTODY_INVALID, f"{label}: {exc}")
    return resolved_parent / candidate.name


def _read_custody_object(path: Path, *, label: str) -> Mapping[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise BracketBindingRefusal(
            REFUSAL_INPUT_INVALID, f"cannot read {label}: {exc}"
        ) from exc
    return _strict_json_object(raw, label=label)


def _window_descriptors(
    verdict: Mapping[str, Any],
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    basis = verdict.get("evaluation_basis")
    bracket_set = (
        basis.get("calibration_bracket_set")
        if isinstance(basis, Mapping)
        else None
    )
    core = verdict.get("idle_admission_core")
    stored_bracket = (
        core.get("instrument_calibration_bracket")
        if isinstance(core, Mapping)
        else None
    )
    stored_pre = (
        stored_bracket.get("pre") if isinstance(stored_bracket, Mapping) else None
    )
    stored_post = (
        stored_bracket.get("post") if isinstance(stored_bracket, Mapping) else None
    )
    pre = bracket_set.get("pre") if isinstance(bracket_set, Mapping) else None
    post = bracket_set.get("post") if isinstance(bracket_set, Mapping) else None
    if (
        verdict.get("schema_version") != WHOLE_WINDOW_SCHEMA
        or verdict.get("record_type") != "idle_admission_whole_window_verdict"
        or verdict.get("status") != "passed"
        or verdict.get("claim_licensing") is not True
        or not isinstance(basis, Mapping)
        or basis.get("sha256")
        != canonical_sha256(
            {key: value for key, value in basis.items() if key != "sha256"}
        )
        or not isinstance(pre, Mapping)
        or not isinstance(post, Mapping)
        or stored_pre != pre
        or stored_post != post
    ):
        _refuse(
            REFUSAL_DESCRIPTOR_INVALID,
            "whole-window verdict lacks one self-authenticating pre/post bracket set",
        )
    if pre.get("bracket_slot") != "pre" or post.get("bracket_slot") != "post":
        _refuse(
            REFUSAL_DESCRIPTOR_INVALID,
            "whole-window bracket descriptors have invalid slot roles",
        )
    values = [
        pre.get(field)
        for field in (*DESCRIPTOR_IDENTITY_FIELDS, *DESCRIPTOR_ENDPOINT_FIELDS)
    ] + [post.get(field) for field in DESCRIPTOR_ENDPOINT_FIELDS]
    if any(not isinstance(value, str) or not value for value in values):
        _refuse(
            REFUSAL_DESCRIPTOR_INVALID,
            "whole-window bracket descriptors are missing required string fields",
        )
    disagreements = [
        field
        for field in DESCRIPTOR_IDENTITY_FIELDS
        if pre.get(field) != post.get(field)
    ]
    if disagreements:
        _refuse(
            REFUSAL_DESCRIPTOR_MISMATCH,
            "pre/post bracket descriptors disagree on: " + ", ".join(disagreements),
        )
    return pre, post


def _session_preflight(
    snapshot: CalibrationLedgerSnapshot, descriptor: Mapping[str, Any]
) -> None:
    if snapshot.refusal_reasons:
        _refuse(
            REFUSAL_LEDGER_REFUSED,
            "calibration ledger snapshot refused: "
            + ", ".join(snapshot.refusal_reasons),
        )
    session = snapshot.bracket_session_by_id.get(
        str(descriptor["bracket_session_id"])
    )
    if session is None or (
        session.window_id,
        session.plan_id,
        session.plan_sha256,
        session.evidence_root_id,
        session.runs_root,
    ) != (
        descriptor["bracket_window_id"],
        descriptor["bracket_plan_id"],
        descriptor["bracket_plan_sha256"],
        descriptor["bracket_evidence_root_id"],
        descriptor["bracket_runs_root"],
    ):
        _refuse(
            REFUSAL_SESSION_IDENTITY_MISMATCH,
            "no ledger session matches the whole-window frozen identity",
        )
    if session.state != "finalized":
        _refuse(
            REFUSAL_SESSION_NOT_FINALIZED,
            f"bracket session state is {session.state!r}, not 'finalized'",
        )
    if any(
        (observation := session.finalized_slots.get(role)) is None
        or observation.disposition != "valid"
        or observation.content_id is None
        for role in ("pre", "post")
    ):
        _refuse(
            REFUSAL_SESSION_ENDPOINTS_INVALID,
            "bracket session does not contain valid pre and post endpoints",
        )


def _build_binding(
    snapshot: CalibrationLedgerSnapshot,
    pre: Mapping[str, Any],
    post: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        binding = build_calibration_bracket_binding(
            snapshot,
            session_id=str(pre["bracket_session_id"]),
            window_id=str(pre["bracket_window_id"]),
            plan_id=str(pre["bracket_plan_id"]),
            plan_sha256=str(pre["bracket_plan_sha256"]),
            evidence_root_id=str(pre["bracket_evidence_root_id"]),
            runs_root=str(pre["bracket_runs_root"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise BracketBindingRefusal(REFUSAL_BUILD_REFUSED, str(exc)) from exc
    if binding.get("binding_digest") != canonical_sha256(
        {key: value for key, value in binding.items() if key != "binding_digest"}
    ):
        _refuse(
            REFUSAL_BUILD_REFUSED,
            "in-memory producer returned a non-authenticating binding digest",
        )
    if validate_calibration_bracket_binding(
        binding,
        snapshot,
        window_id=str(pre["bracket_window_id"]),
        plan_id=str(pre["bracket_plan_id"]),
        plan_sha256=str(pre["bracket_plan_sha256"]),
        evidence_root_id=str(pre["bracket_evidence_root_id"]),
        runs_root=str(pre["bracket_runs_root"]),
    ) is None:
        _refuse(
            REFUSAL_BUILD_REFUSED,
            "authoritative validator rejected the in-memory binding",
        )
    for role, descriptor in (("pre", pre), ("post", post)):
        endpoint = binding["endpoints"][role]
        if (
            endpoint["attempt_id"] != descriptor.get("attempt_id")
            or endpoint["receipt_digest"]
            != descriptor.get("ledger_receipt_digest")
            or endpoint["content_digest"] != descriptor.get("content_id")
        ):
            _refuse(
                REFUSAL_ENDPOINT_MISMATCH,
                f"{role} descriptor does not authenticate against the ledger endpoint",
            )
    return binding


def _publish_no_clobber(path: Path, raw: bytes) -> None:
    descriptor: int | None = None
    directory_descriptor: int | None = None
    temporary: Path | None = None
    target_installed = False
    succeeded = False
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        for _ in range(100):
            candidate = path.with_name(
                f"{path.name}.tmp-{os.getpid()}-{secrets.token_hex(8)}"
            )
            try:
                descriptor = os.open(candidate, flags, 0o600)
            except FileExistsError:
                continue
            temporary = candidate
            break
        else:
            raise OSError("cannot allocate an exclusive temporary output")

        remaining = memoryview(raw)
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:
                raise OSError("zero-byte write")
            remaining = remaining[written:]
        os.fsync(descriptor)
        closing_descriptor = descriptor
        descriptor = None
        os.close(closing_descriptor)

        # A hard link creates the target atomically and fails with EEXIST;
        # unlike rename/replace, it can never clobber an existing target.
        os.link(temporary, path, follow_symlinks=False)
        target_installed = True
        os.unlink(temporary)
        temporary = None

        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        os.fsync(directory_descriptor)
        closing_directory = directory_descriptor
        directory_descriptor = None
        os.close(closing_directory)
        succeeded = True
    except FileExistsError as exc:
        raise BracketBindingRefusal(
            REFUSAL_OUTPUT_EXISTS, f"refusing to overwrite existing output {path}"
        ) from exc
    except OSError as exc:
        raise BracketBindingRefusal(
            REFUSAL_OUTPUT_FAILED, f"cannot publish {path}: {exc}"
        ) from exc
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if directory_descriptor is not None:
            try:
                os.close(directory_descriptor)
            except OSError:
                pass
        if not succeeded and target_installed:
            try:
                os.unlink(path)
            except OSError:
                pass
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description=__doc__)
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--whole-window-verdict", required=True, type=Path)
    parser.add_argument("--calibration-ledger", required=True, type=Path)
    parser.add_argument(
        "--head-pin",
        type=Path,
        help=(
            "authenticated ledger head pin (default: calibration_ledger_head.json "
            "beside --calibration-ledger)"
        ),
    )
    parser.add_argument(
        "--calibration-custody-store",
        type=Path,
        help="optional authenticated content-addressed calibration custody store",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        lexical_root, resolved_root = _custody_root(args.custody_root)
        verdict_path = _existing_custody_path(
            args.whole_window_verdict,
            lexical_root,
            resolved_root,
            label="whole-window verdict",
            directory=False,
        )
        ledger_path = _existing_custody_path(
            args.calibration_ledger,
            lexical_root,
            resolved_root,
            label="calibration ledger",
            directory=False,
        )
        head_pin_path = _existing_custody_path(
            args.head_pin
            if args.head_pin is not None
            else ledger_path.with_name("calibration_ledger_head.json"),
            lexical_root,
            resolved_root,
            label="calibration ledger head pin",
            directory=False,
        )
        custody_store = (
            _existing_custody_path(
                args.calibration_custody_store,
                lexical_root,
                resolved_root,
                label="calibration custody store",
                directory=True,
            )
            if args.calibration_custody_store is not None
            else None
        )
        output_path = _new_custody_file(
            args.output,
            lexical_root,
            resolved_root,
            label="bracket binding output",
        )
        verdict = _read_custody_object(verdict_path, label="whole-window verdict")
        pre, post = _window_descriptors(verdict)
        runs_text = str(pre["bracket_runs_root"])
        if not Path(runs_text).is_absolute():
            _refuse(
                REFUSAL_CUSTODY_INVALID,
                "authenticated runs root must use its absolute ledger spelling",
            )
        _existing_custody_path(
            Path(runs_text),
            lexical_root,
            resolved_root,
            label="bracket-authenticated runs root",
            directory=True,
        )
        snapshot = load_calibration_ledger_snapshot(
            ledger_path,
            head_pin_path,
            require_committed_pin=False,
            verify_custody=True,
            calibration_custody_store=custody_store,
        )
        if custody_store is not None:
            if snapshot.refusal_reasons:
                _refuse(
                    REFUSAL_LEDGER_REFUSED,
                    "calibration custody store snapshot refused: "
                    + ", ".join(snapshot.refusal_reasons),
                )
            # The current finalizer has no custody-store argument. A store-only
            # success would therefore manufacture a binding H6 cannot consume.
            # Re-run its exact ledger load and make that compatibility a gate.
            finalizer_snapshot = load_calibration_ledger_snapshot(
                ledger_path,
                head_pin_path,
                require_committed_pin=False,
                verify_custody=True,
            )
            if not snapshot.refusal_reasons and finalizer_snapshot.refusal_reasons:
                _refuse(
                    REFUSAL_LEDGER_REFUSED,
                    "calibration custody store passes but the current finalizer "
                    "would refuse the ledger snapshot: "
                    + ", ".join(finalizer_snapshot.refusal_reasons),
                )
            snapshot = finalizer_snapshot
        _session_preflight(snapshot, pre)
        binding = _build_binding(snapshot, pre, post)
        _publish_no_clobber(output_path, canonical_json_bytes(binding) + b"\n")
    except BracketBindingRefusal as exc:
        print(
            json.dumps(
                {"status": "REFUSE", "reason": exc.reason, "detail": exc.detail},
                sort_keys=True,
            )
        )
        return 2
    except Exception as exc:  # Total CLI boundary: never expose a traceback.
        print(
            json.dumps(
                {
                    "status": "REFUSE",
                    "reason": REFUSAL_INTERNAL_ERROR,
                    "detail": f"{type(exc).__name__}: {exc}",
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "status": "BUILT",
                "binding_digest": binding["binding_digest"],
                "output": str(output_path),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
