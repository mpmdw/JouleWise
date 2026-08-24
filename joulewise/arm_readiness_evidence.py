"""Derive D-134 freeze evidence from authenticated primary artifacts.

The public author accepts only a pack path.  Conclusions, hashes, receipt
metadata, and boot identity are derived here; callers cannot supply them.
"""

from __future__ import annotations

import ast as _ast
import copy
import inspect
import io
import json
import os
import platform as _platform
import re
import signal
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

from joulewise import arm_readiness as _readiness
from joulewise import identity_pins as _identity_pins
from joulewise.calibration_bracketing import (
    ISSUED_ACCEPTANCE_REGISTRY as _ISSUED_ACCEPTANCE_REGISTRY,
    PREDECESSOR_ACCEPTANCE_ID as _PREDECESSOR_ACCEPTANCE_ID,
    _acceptance_bound_from_authenticated_bytes,
)
from joulewise.floor_extraction import (
    validate_extraction_spec as _validate_extraction_spec,
)
from joulewise.receipt_oracle import (
    derive_bracket_session_receipt_oracle as _derive_bracket_session_receipt_oracle,
)


_SOURCE_SCHEMA = "joulewise.arm_readiness_evidence_source.v1"
_R1_SOURCE_SCHEMA = "joulewise.arm_readiness_evidence_source.v2"
_EVIDENCE_VALIDITY_NS = 86_400 * 1_000_000_000
_SOURCE_DIRECTORY = "arm_readiness.sources"
_EVIDENCE_DIRECTORY = "arm_readiness.evidence"
_SPECIALIZED_EVIDENCE_KINDS = frozenset(
    {"IDENTITY_PIN_PROJECTION", "DRY_RUN_REHEARSAL"}
)

# The inverse of arm_readiness._PROFILE_BY_PACK, and immutable for the same
# reason: it is the HISTORICAL v1 family, and the committed v1 PACK_FAMILY
# evidence was derived against exactly these three plan trees.  Successor
# families do not edit this table; a registry-driven successor route for
# PACK_FAMILY derivation is NOT yet built (reported to the magistrate with the
# R1 registry install).
_PACKS_BY_PROFILE = {
    "ALPHA": "d117_floor_qwen25_1p5b_v1",
    "BETA": "d117_floor_qwen25_7b_v1",
    "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v1",
}
_SOURCE_KEYS = {
    "schema_version",
    "kind",
    "head_commit",
    "pack_sha256",
    "primary_artifacts",
    "checks",
    "facts",
    "derivation",
}
_R1_SOURCE_KEYS = _SOURCE_KEYS | {
    "derivation_commit",
    "freshness_class",
    "freshness_policy_id",
    "environment_fingerprint",
}
_PRIMARY_KEYS = {"path", "sha256"}
_SOURCE_FACT_KEYS = {"fact_id", "value"}
_SOURCE_CHECK_KEYS = {"check_id", "status", "evidence"}
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SUITE_TIMEOUT_SECONDS = 900
_AUTHORING_ARTIFACTS = (
    "joulewise/arm_readiness_evidence.py",
    "scripts/author_arm_readiness_evidence.py",
)

# R1 clause 1 and Opus S2: the shared code table is the only class
# authority.  This projection exists only to enumerate the generic derivers.
_GENERIC_DERIVER_KINDS = (
    "ACCEPTANCE_OWNER",
    "ACCEPTANCE_SUCCESSOR",
    "DOCTRINE_PIN",
    "ESTIMATOR_IDENTITY",
    "MINT_TRUST",
    "MULTICELL_MINT",
    "PACK_AUTHENTICATION",
    "PACK_FAMILY",
    "REASON_CODE_COVERAGE",
    "RECEIPT_ORACLE",
    "RECOVERY_LEDGER_TEST",
    "THREE_WINDOW_REGRESSION",
)
_DERIVER_FRESHNESS_CLASSES = {
    kind: _readiness.R1_EVIDENCE_FRESHNESS_CLASSES[kind]
    for kind in _GENERIC_DERIVER_KINDS
}
_ENVIRONMENT_FINGERPRINT_KINDS = frozenset(
    {
        "MINT_TRUST",
        "MULTICELL_MINT",
        "PACK_AUTHENTICATION",
        "REASON_CODE_COVERAGE",
        "RECOVERY_LEDGER_TEST",
        "THREE_WINDOW_REGRESSION",
    }
)
# D-148.5 r3/B-2: generic execution evidence re-use compares the complete
# builder-emitted fingerprint digest.  The four specialized/no-generic-lane
# kinds carry a distinct truthful token even though this generic author never
# emits them.
_SUPPORTED_ENVIRONMENT_COMPARISONS = frozenset(
    {
        "EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE",
        "NO_R1_AUTHORING_LANE",
    }
)
_DERIVER_DIRECT_READ_CALLS = frozenset(
    {
        "open",
        "read_bytes",
        "read_text",
        "rglob",
        "glob",
        "iterdir",
        "listdir",
        "scandir",
        "walk",
        "_git_blob_at_head",
        "_run_git",
        "_git_text",
        "resolve_frozen_plan",
        "_acceptance_bound_from_authenticated_bytes",
        "_validate_extraction_spec",
        "_derive_bracket_session_receipt_oracle",
        "run",
        "Popen",
    }
)
# These functions are the IO boundary: each either records the complete read
# identity itself or calls the base committed-artifact recorder.  The release
# guard is a best-effort developer-error lint; it traverses ordinary local
# helper calls and their simple aliases, but is not an in-process sandbox.
_DERIVER_RECORDED_READ_BOUNDARIES = frozenset(
    {
        "_committed_artifact",
        "_recorded_acceptance_authentication",
        "_recorded_estimator_registry",
        "_recorded_extraction_validation",
        "_recorded_frozen_plan",
        "_recorded_generator_check",
        "_recorded_pack_family_plan_tree",
        "_recorded_pack_glob",
        "_recorded_projected_pack_authentication",
        "_recorded_receipt_oracle",
        "_run_suite",
    }
)


class EvidenceAuthoringError(ValueError):
    """A fail-closed authoring refusal naming the affected evidence kind."""

    def __init__(self, kind: str, reason_code: str, detail: str) -> None:
        super().__init__(detail)
        self.kind = kind
        self.reason_code = reason_code


@dataclass(frozen=True)
class _ExecutedFile:
    module: str
    path: str
    sha256: str

    def evidence(self) -> dict[str, str]:
        return {"module": self.module, "path": self.path, "sha256": self.sha256}


@dataclass(frozen=True)
class _SuiteResult:
    test_ids: tuple[str, ...]
    tests_run: int
    failures: int
    errors: int
    skipped: int
    expected_failures: int
    unexpected_successes: int
    executed_files: tuple[_ExecutedFile, ...]

    @property
    def passed(self) -> bool:
        return self.failures == self.errors == self.unexpected_successes == 0

    def evidence(self) -> dict[str, Any]:
        return {
            "test_ids": list(self.test_ids),
            "tests_run": self.tests_run,
            "failures": self.failures,
            "errors": self.errors,
            "skipped": self.skipped,
            "expected_failures": self.expected_failures,
            "unexpected_successes": self.unexpected_successes,
            "executed_files": [item.evidence() for item in self.executed_files],
            "execution_isolated_to_discovered_repository": True,
        }


@dataclass(frozen=True)
class _DerivationContext:
    pack_root: Path
    repository: Path
    tree: Mapping[str, Any]
    pack_sha256: str
    head_commit: str


@dataclass(frozen=True)
class _DerivedKind:
    kind: str
    facts: Mapping[str, Mapping[str, Any]]
    primary_artifacts: tuple[Mapping[str, str], ...]
    checks: tuple[Mapping[str, Any], ...]
    derivation: Mapping[str, Any]


def _slug(kind: str) -> str:
    return kind.lower().replace("_", "-")


def _underivable(kind: str, detail: str) -> EvidenceAuthoringError:
    return EvidenceAuthoringError(
        kind,
        f"evidence_author_{kind.lower()}_underivable",
        detail,
    )


def _refuse(kind: str, code: str, detail: str) -> EvidenceAuthoringError:
    return EvidenceAuthoringError(kind, code, detail)


def _repo_relative(repository: Path, path: Path) -> str:
    try:
        return path.resolve(strict=True).relative_to(repository).as_posix()
    except (OSError, ValueError) as exc:
        raise ValueError(f"artifact is outside repository: {path}") from exc


def _committed_artifact(
    repository: Path, relative: str, *, kind: str
) -> tuple[dict[str, str], bytes]:
    path = repository / PurePosixPath(relative)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise _underivable(kind, f"primary artifact is unreadable: {relative}: {exc}") from exc
    committed = _readiness._git_blob_at_head(repository, relative)
    if committed is None or committed != raw:
        raise _underivable(
            kind, f"primary artifact is not byte-identical to HEAD: {relative}"
        )
    return {"path": relative, "sha256": _readiness.sha256_bytes(raw)}, raw


def _pinned_artifact(
    context: _DerivationContext,
    pin: object,
    *,
    kind: str,
    label: str,
) -> tuple[dict[str, str], bytes]:
    if not isinstance(pin, Mapping) or set(pin) < {"path", "sha256"}:
        raise _underivable(kind, f"{label} path/SHA pin is missing")
    relative = pin.get("path")
    digest = pin.get("sha256")
    if not isinstance(relative, str) or not isinstance(digest, str):
        raise _underivable(kind, f"{label} path/SHA pin is malformed")
    artifact, raw = _committed_artifact(context.repository, relative, kind=kind)
    if artifact["sha256"] != digest:
        raise _underivable(kind, f"{label} digest differs from committed bytes")
    return artifact, raw


def _recorded_frozen_plan(
    context: _DerivationContext, *, kind: str
) -> tuple[Path, str, str, bytes, dict[str, str]]:
    """Resolve a frozen plan and immediately add its committed-byte record."""

    try:
        path, pack_relative, plan_id, _resolved_raw = _readiness.resolve_frozen_plan(
            context.pack_root, context.tree
        )
    except _readiness.ArmReadinessError as exc:
        raise _underivable(kind, f"R2 frozen-plan reference is invalid: {exc}") from exc
    relative = _repo_relative(context.repository, path)
    artifact, raw = _committed_artifact(context.repository, relative, kind=kind)
    return path, pack_relative, plan_id, raw, artifact


def _recorded_pack_glob(
    context: _DerivationContext, pattern: str, *, kind: str
) -> tuple[Path, ...]:
    """Route a pack namespace enumeration through one auditable helper."""

    try:
        paths = tuple(sorted(context.pack_root.rglob(pattern)))
    except OSError as exc:
        raise _underivable(kind, f"pack namespace enumeration failed: {exc}") from exc
    for path in paths:
        relative = _repo_relative(context.repository, path)
        _committed_artifact(context.repository, relative, kind=kind)
    return paths


def _recorded_pack_family_plan_tree(
    context: _DerivationContext, pack_name: str, *, kind: str
) -> tuple[dict[str, str], bytes]:
    relative = f"configs/campaigns/{pack_name}/plan_tree.json"
    return _committed_artifact(context.repository, relative, kind=kind)


def _recorded_acceptance_authentication(
    context: _DerivationContext, raw: bytes, *, kind: str
) -> Mapping[str, Any] | None:
    _committed_artifact(
        context.repository, "joulewise/calibration_bracketing.py", kind=kind
    )
    return _acceptance_bound_from_authenticated_bytes(raw)


def _recorded_extraction_validation(
    context: _DerivationContext, value: Mapping[str, Any], *, kind: str
) -> list[str]:
    _committed_artifact(context.repository, "joulewise/floor_extraction.py", kind=kind)
    return _validate_extraction_spec(value)


def _recorded_estimator_registry(
    context: _DerivationContext, *, kind: str
) -> tuple[set[str], dict[str, str], dict[str, str]]:
    analysis_artifact, _ = _committed_artifact(
        context.repository, "joulewise/analysis_manifest_v3.py", kind=kind
    )
    detection_artifact, _ = _committed_artifact(
        context.repository, "joulewise/detection_floor.py", kind=kind
    )
    from joulewise import analysis_manifest_v3, detection_floor

    admitted = {
        detection_floor.METHOD_ID,
        detection_floor.COMMON_MODE_ESTIMATOR_ID,
        analysis_manifest_v3.ESTIMATOR_ID,
    }
    return admitted, analysis_artifact, detection_artifact


def _recorded_receipt_oracle(
    context: _DerivationContext, *, kind: str
) -> tuple[Mapping[str, Any], tuple[dict[str, str], ...]]:
    artifacts = tuple(
        _committed_artifact(context.repository, relative, kind=kind)[0]
        for relative in (
            "joulewise/calibration_ledger.py",
            "joulewise/receipt_oracle.py",
        )
    )
    try:
        derived = _derive_bracket_session_receipt_oracle()
    except Exception as exc:
        raise _underivable(
            kind, f"production receipt oracle could not be derived: {exc}"
        ) from exc
    return derived, artifacts


def _fact_source(
    context: _DerivationContext,
    derived: _DerivedKind,
) -> bytes:
    return _readiness.render_json(
        {
            "schema_version": _SOURCE_SCHEMA,
            "kind": derived.kind,
            "head_commit": context.head_commit,
            "pack_sha256": context.pack_sha256,
            "primary_artifacts": sorted(
                (dict(item) for item in derived.primary_artifacts),
                key=lambda item: item["path"],
            ),
            "checks": [dict(item) for item in derived.checks],
            "facts": [
                {"fact_id": fact_id, "value": copy.deepcopy(value)}
                for fact_id, value in sorted(derived.facts.items())
            ],
            "derivation": copy.deepcopy(dict(derived.derivation)),
        }
    )


def _path_environment_descriptor(path: Path) -> dict[str, Any]:
    try:
        resolved = path.resolve(strict=True)
        status = resolved.stat()
        descriptor = {
            "path": str(resolved),
            "kind": "directory" if resolved.is_dir() else "file",
            "mode": status.st_mode,
            "size": status.st_size,
            "mtime_ns": status.st_mtime_ns,
            "device": status.st_dev,
            "inode": status.st_ino,
        }
    except OSError as exc:
        descriptor = {
            "path": str(path.resolve(strict=False)),
            "kind": "unreadable",
            "error_type": type(exc).__name__,
        }
    return {
        "path": descriptor["path"],
        "descriptor_sha256": _readiness.sha256_bytes(
            _readiness.render_json(descriptor)
        ),
    }


def _execution_environment_fingerprint(
    context: _DerivationContext, kind: str
) -> dict[str, Any]:
    repository = context.repository.resolve(strict=True)
    non_repository_paths: list[dict[str, Any]] = []
    for raw in sys.path:
        if not raw:
            continue
        candidate = Path(raw)
        resolved = candidate.resolve(strict=False)
        if resolved == repository or repository in resolved.parents:
            continue
        non_repository_paths.append(_path_environment_descriptor(candidate))
    environment = (
        [
            {
                "name": name,
                "value_sha256": _readiness.sha256_bytes(
                    os.environ[name].encode("utf-8", errors="surrogateescape")
                ),
            }
            for name in sorted(os.environ)
        ]
        if kind == "PACK_AUTHENTICATION"
        else []
    )
    fingerprint = {
        "schema_version": "joulewise.arm_readiness_execution_environment.v1",
        "amendment5_required_kind": kind in _ENVIRONMENT_FINGERPRINT_KINDS,
        "interpreter": _path_environment_descriptor(Path(sys.executable)),
        "implementation": sys.implementation.name,
        "python_version": _platform.python_version(),
        "platform_system": _platform.system(),
        "platform_release": _platform.release(),
        "platform_machine": _platform.machine(),
        "non_repository_sys_path": sorted(
            non_repository_paths, key=lambda item: item["path"]
        ),
        "inherited_environment": environment,
    }
    return {
        "facts": fingerprint,
        "sha256": _readiness.sha256_bytes(_readiness.render_json(fingerprint)),
    }


def _r1_fact_source(
    context: _DerivationContext,
    derived: _DerivedKind,
    policy: Mapping[str, Any],
    environment_fingerprint: Mapping[str, Any] | None,
) -> bytes:
    return _readiness.render_json(
        {
            "schema_version": _R1_SOURCE_SCHEMA,
            "kind": derived.kind,
            "head_commit": context.head_commit,
            "derivation_commit": context.head_commit,
            "pack_sha256": context.pack_sha256,
            "freshness_class": policy["freshness_class"],
            "freshness_policy_id": policy["freshness_policy_id"],
            "environment_fingerprint": copy.deepcopy(environment_fingerprint),
            "primary_artifacts": sorted(
                (dict(item) for item in derived.primary_artifacts),
                key=lambda item: item["path"],
            ),
            "checks": [dict(item) for item in derived.checks],
            "facts": [
                {"fact_id": fact_id, "value": copy.deepcopy(value)}
                for fact_id, value in sorted(derived.facts.items())
            ],
            "derivation": copy.deepcopy(dict(derived.derivation)),
        }
    )


def _check(check_id: str, evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {"check_id": check_id, "status": "PASS", "evidence": dict(evidence)}


def _reauthenticate_primary_artifacts(
    context: _DerivationContext, derived: Sequence[_DerivedKind]
) -> None:
    seen: set[tuple[str, str]] = set()
    for item in derived:
        for primary in item.primary_artifacts:
            key = (primary["path"], primary["sha256"])
            if key in seen:
                continue
            seen.add(key)
            try:
                actual, _raw = _committed_artifact(
                    context.repository, primary["path"], kind=item.kind
                )
            except EvidenceAuthoringError as exc:
                raise _refuse(
                    item.kind,
                    "evidence_author_input_changed",
                    f"primary artifact changed during derivation: {primary['path']}",
                ) from exc
            if actual != primary:
                raise _refuse(
                    item.kind,
                    "evidence_author_input_changed",
                    f"primary artifact changed during derivation: {primary['path']}",
                )


_SUITE_SUBPROCESS = r"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import unittest

repository = Path(os.environ["JOULEWISE_SUITE_REPOSITORY"]).resolve(strict=True)
test_ids = json.loads(os.environ["JOULEWISE_SUITE_TEST_IDS"])
stdlib_paths = []
for raw in sys.path:
    if not raw:
        continue
    try:
        resolved = Path(raw).resolve(strict=True)
    except OSError:
        continue
    if resolved != repository and repository not in resolved.parents:
        stdlib_paths.append(str(resolved))
sys.path[:] = [str(repository), *stdlib_paths]

loader = unittest.TestLoader()
suite = loader.loadTestsFromNames(test_ids)
loaded_ids = []
def visit(value):
    if isinstance(value, unittest.TestSuite):
        for child in value:
            visit(child)
    else:
        loaded_ids.append(value.id())
visit(suite)

result = unittest.TestResult()
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    suite.run(result)

executed_files = []
foreign_project_modules = []
for module_name, module in sorted(sys.modules.items()):
    raw_path = getattr(module, "__file__", None)
    if not isinstance(raw_path, str):
        continue
    try:
        path = Path(raw_path).resolve(strict=True)
        relative = path.relative_to(repository).as_posix()
    except (OSError, ValueError):
        if module_name.partition(".")[0] in {"joulewise", "scripts", "tests"}:
            foreign_project_modules.append({"module": module_name, "path": raw_path})
        continue
    executed_files.append(
        {
            "module": module_name,
            "path": relative,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )

failed_ids = sorted(
    {test.id() for test, _detail in (*result.failures, *result.errors)}
)
print(json.dumps({
    "cwd": str(Path.cwd().resolve()),
    "import_root": sys.path[0],
    "test_ids": loaded_ids,
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "skipped": len(result.skipped),
    "expected_failures": len(result.expectedFailures),
    "unexpected_successes": len(result.unexpectedSuccesses),
    "failed_ids": failed_ids,
    "executed_files": executed_files,
    "foreign_project_modules": foreign_project_modules,
}, allow_nan=False, separators=(",", ":"), sort_keys=True))
"""


def _execute_unittest_suite_subprocess(
    repository: Path, test_ids: Sequence[str]
) -> _SuiteResult:
    """Run one focused suite in a target-rooted, isolated child interpreter."""

    repository = repository.resolve(strict=True)
    environment = {
        name: os.environ[name]
        for name in ("SYSTEMROOT", "WINDIR")
        if name in os.environ
    }
    environment.update(
        {
            "JOULEWISE_SUITE_REPOSITORY": str(repository),
            "JOULEWISE_SUITE_TEST_IDS": json.dumps(list(test_ids)),
            "LANG": "C",
            "LC_ALL": "C",
        }
    )
    try:
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(
                [sys.executable, "-I", "-B", "-c", _SUITE_SUBPROCESS],
                cwd=repository,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            timed_out = False
            try:
                process.wait(timeout=_SUITE_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                timed_out = True
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.wait()
            stdout.seek(0)
            stderr.seek(0)
            stdout_bytes = stdout.read()
            stderr_bytes = stderr.read()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f"focused suite subprocess could not execute: {exc}") from exc
    if timed_out:
        raise ValueError(
            f"focused suite subprocess timed out after {_SUITE_TIMEOUT_SECONDS} seconds"
        )
    if process.returncode != 0:
        detail = stderr_bytes.decode("utf-8", errors="replace").strip()
        raise ValueError(
            f"focused suite subprocess exited {process.returncode}: {detail}"
        )
    try:
        payload = json.loads(stdout_bytes.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("focused suite subprocess returned malformed JSON") from exc
    if (
        not isinstance(payload, Mapping)
        or payload.get("cwd") != str(repository)
        or payload.get("import_root") != str(repository)
        or payload.get("foreign_project_modules") != []
    ):
        raise ValueError("focused suite escaped the discovered repository import root")
    loaded_ids = payload.get("test_ids")
    raw_files = payload.get("executed_files")
    if (
        not isinstance(loaded_ids, list)
        or not loaded_ids
        or any(
            not isinstance(item, str)
            or item.startswith("unittest.loader._FailedTest")
            for item in loaded_ids
        )
        or not isinstance(raw_files, list)
    ):
        raise ValueError(f"focused suite could not be loaded: {list(test_ids)!r}")
    executed_files: list[_ExecutedFile] = []
    for item in raw_files:
        if (
            not isinstance(item, Mapping)
            or set(item) != {"module", "path", "sha256"}
            or not isinstance(item["module"], str)
            or not isinstance(item["path"], str)
            or not isinstance(item["sha256"], str)
            or _SHA_RE.fullmatch(item["sha256"]) is None
        ):
            raise ValueError("focused suite returned a malformed executed-file identity")
        executed_files.append(
            _ExecutedFile(item["module"], item["path"], item["sha256"])
        )
    count_fields = (
        "tests_run",
        "failures",
        "errors",
        "skipped",
        "expected_failures",
        "unexpected_successes",
    )
    if any(
        not isinstance(payload.get(name), int) or payload[name] < 0
        for name in count_fields
    ):
        raise ValueError("focused suite returned malformed result counts")
    return _SuiteResult(
        test_ids=tuple(loaded_ids),
        tests_run=payload["tests_run"],
        failures=payload["failures"],
        errors=payload["errors"],
        skipped=payload["skipped"],
        expected_failures=payload["expected_failures"],
        unexpected_successes=payload["unexpected_successes"],
        executed_files=tuple(executed_files),
    )


def _run_suite(
    context: _DerivationContext, kind: str, test_ids: Sequence[str]
) -> _SuiteResult:
    try:
        result = _execute_unittest_suite_subprocess(context.repository, test_ids)
    except Exception as exc:
        raise _underivable(kind, f"focused suite could not pass: {exc}") from exc
    if not isinstance(result, _SuiteResult):
        raise _underivable(kind, "focused suite returned an invalid result type")
    executed_modules = {item.module: item for item in result.executed_files}
    for item in result.executed_files:
        try:
            artifact, _raw = _committed_artifact(
                context.repository, item.path, kind=kind
            )
        except EvidenceAuthoringError as exc:
            raise _underivable(
                kind, f"executed module is not SHA-bound to target HEAD: {item.module}"
            ) from exc
        if artifact["sha256"] != item.sha256:
            raise _underivable(
                kind,
                f"executed-file SHA differs from SHA-bound primary artifact: {item.path}",
            )
    for requested in test_ids:
        matches = [
            item
            for module, item in executed_modules.items()
            if requested == module or requested.startswith(f"{module}.")
        ]
        if not matches:
            raise _underivable(
                kind, f"focused suite did not report the executed test module: {requested}"
            )
    if not result.passed:
        raise _underivable(
            kind,
            "focused suite refused: "
            f"failures={result.failures}, errors={result.errors}, "
            f"unexpected_successes={result.unexpected_successes}",
        )
    return result


def _extract_section(raw: bytes, label: str, *, kind: str) -> bytes:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise _underivable(kind, "runbook is not UTF-8") from exc
    match = re.search(rf"(?m)^## {re.escape(label)}(?:\.|\s)", text)
    if match is None:
        raise _underivable(kind, f"runbook section {label} is missing")
    successor = re.search(r"(?m)^## ", text[match.end() :])
    end = len(text) if successor is None else match.end() + successor.start()
    return text[match.start() : end].encode("utf-8")


def _derive_doctrine_pin(context: _DerivationContext) -> _DerivedKind:
    kind = "DOCTRINE_PIN"
    authoring_artifacts = tuple(
        _committed_artifact(context.repository, relative, kind=kind)[0]
        for relative in _AUTHORING_ARTIFACTS
    )
    runbook_artifact, runbook = _committed_artifact(
        context.repository, "docs/phase_2/window_runbook.md", kind=kind
    )
    decision_artifact, decision = _committed_artifact(
        context.repository, "docs/decision_log.md", kind=kind
    )
    tree_relative = _repo_relative(context.repository, context.pack_root / "plan_tree.json")
    tree_artifact, _tree_raw = _committed_artifact(
        context.repository, tree_relative, kind=kind
    )
    sections = {
        label: _readiness.sha256_bytes(_extract_section(runbook, label, kind=kind))
        for label in ("5", "5A", "5B", "5C", "6", "10")
    }
    try:
        decision_text = decision.decode("utf-8", errors="strict")
        d134 = decision_text.split("## D-134:", 1)[1].split("\n## D-", 1)[0]
    except (UnicodeDecodeError, IndexError) as exc:
        raise _underivable(kind, "committed D-134 decision text is missing") from exc
    launch = context.tree.get("arm_attachments", {}).get("launch")
    stage_graph = context.tree.get("stage_graph")
    if not isinstance(launch, Mapping) or not isinstance(stage_graph, list):
        raise _underivable(kind, "pack lacks a frozen launch recipe/stage graph")
    section_5a = _extract_section(runbook, "5A", kind=kind).decode("utf-8")
    restore_after_verdict = (
        "whole-window verdict, and the backup, re-enable it" in section_5a
        and "The restore comes last" in section_5a
    )
    closeout = context.tree.get("closeout_attachments")
    backups = closeout.get("backup_requirements") if isinstance(closeout, Mapping) else None
    backup_command_count = sum(
        1
        for stage in stage_graph
        if isinstance(stage, Mapping)
        for command in (
            stage.get("launch", {}).get("commands", [])
            if isinstance(stage.get("launch"), Mapping)
            else []
        )
        if isinstance(command, Mapping) and command.get("command_kind") == "backup"
    )
    restore_after_both = (
        restore_after_verdict
        and backup_command_count == 2
        and (
            backups is None
            or (
                isinstance(backups, Mapping)
                and backups.get("required_successful_backups") == 2
            )
        )
    )
    if not restore_after_verdict or not restore_after_both:
        raise _underivable(
            kind,
            "runbook/pack do not derive clock restoration after verdict and both backups",
        )
    launch_sha = _readiness.sha256_bytes(
        _readiness.render_json({"launch": launch, "stage_graph": stage_graph})
    )
    pin_material = {
        "d134_sha256": _readiness.sha256_bytes(d134.encode("utf-8")),
        "runbook_section_sha256": sections,
        "frozen_launch_recipe_sha256": launch_sha,
    }
    facts = {
        "clock.restore_recipe.v1": {
            "close_out_recipe_hashes_match_pack": True,
            "restore_after_both_backups": True,
            "restore_after_verdict": True,
        },
        "desk.arming_procedure.v1": {
            "frozen_launch_recipe_hash_matches_pack": True,
            "runbook_section_hashes_match_pack": True,
            "runbook_sections": ["5", "5A", "5B", "5C", "6", "10"],
        },
    }
    return _DerivedKind(
        kind,
        facts,
        (*authoring_artifacts, runbook_artifact, decision_artifact, tree_artifact),
        (_check("doctrine_pin_derivation", pin_material),),
        {"pack_pin_material": pin_material},
    )


def _derive_acceptance_owner(context: _DerivationContext) -> _DerivedKind:
    kind = "ACCEPTANCE_OWNER"
    policy = context.tree.get("acceptance_policy")
    issued = policy.get("issued_acceptance") if isinstance(policy, Mapping) else None
    if issued is None and isinstance(policy, Mapping):
        # Flat-shaped policies (gamma) name the artifact by id only; resolve the
        # path from the dual-generation registry so predecessor and successor
        # packs each reach their own issued bytes.
        declared_id = policy.get("issued_artifact_id")
        registered = _ISSUED_ACCEPTANCE_REGISTRY.get(declared_id)
        if registered is None:
            registered = _ISSUED_ACCEPTANCE_REGISTRY[_PREDECESSOR_ACCEPTANCE_ID]
        issued = {
            "path": registered["relative_path"],
            "artifact_sha256": policy.get("issued_artifact_sha256"),
            "acceptance_id": declared_id,
        }
    normalized_pin = (
        {
            "path": issued.get("path"),
            "sha256": issued.get("artifact_sha256", issued.get("sha256")),
        }
        if isinstance(issued, Mapping)
        else issued
    )
    artifact, raw = _pinned_artifact(
        context, normalized_pin, kind=kind, label="issued acceptance artifact"
    )
    loaded = _recorded_acceptance_authentication(context, raw, kind=kind)
    if loaded is None:
        raise _underivable(kind, "issued acceptance bytes fail the production authenticator")
    copied_value = loaded.get("decimal_derivation", {}).get("ratified_operatives", {}).get(
        "bracket_screen_s"
    )
    copied_scalar_accepted = (
        _recorded_acceptance_authentication(
            context, _readiness.render_json(copied_value), kind=kind
        )
        is not None
    )
    mutated = copy.deepcopy(loaded)
    mutated["unknown_evidence_author_probe"] = True
    unknown_key_accepted = (
        _recorded_acceptance_authentication(
            context, _readiness.render_json(mutated), kind=kind
        )
        is not None
    )
    owner_verified = (
        isinstance(policy, Mapping)
        and policy.get("selection") == "issued_d116_artifact_only"
        and loaded.get("artifact_role") == "issued"
        and loaded.get("acceptance_id") == issued.get("acceptance_id")
    )
    if copied_scalar_accepted or unknown_key_accepted or not owner_verified:
        raise _underivable(kind, "acceptance domain-owner mutation probes did not refuse")
    validator_artifact, _ = _committed_artifact(
        context.repository, "joulewise/calibration_bracketing.py", kind=kind
    )
    value = {
        "active_acceptance_artifact_authenticated": True,
        "copied_scalar_accepted": False,
        "domain_owner_verified": True,
        "unknown_key_accepted": False,
        "writer_test_status": "PASS",
    }
    return _DerivedKind(
        kind,
        {"desk.acceptance_owner.v1": value},
        (artifact, validator_artifact),
        (
            _check(
                "acceptance_domain_owner_probe",
                {
                    "acceptance_id": loaded["acceptance_id"],
                    "copied_scalar_accepted": copied_scalar_accepted,
                    "unknown_key_accepted": unknown_key_accepted,
                },
            ),
        ),
        {"acceptance_artifact_sha256": artifact["sha256"]},
    )


def _derive_acceptance_successor(context: _DerivationContext) -> _DerivedKind:
    """Refuse until a successor artifact and validator are actually ratified."""

    kind = "ACCEPTANCE_SUCCESSOR"
    del context
    raise _underivable(
        kind,
        "no ratified successor-acceptance primary artifact schema or production "
        "authenticator exists; issued D-079 packs derive this row as NOT_APPLICABLE",
    )


def _validate_manifests(context: _DerivationContext, *, kind: str) -> dict[str, Any]:
    _plan_path, _plan_pack_relative, _plan_id, plan_raw, plan_artifact = (
        _recorded_frozen_plan(context, kind=kind)
    )
    plan_sha = _readiness.sha256_bytes(plan_raw)
    manifests = sorted(
        path
        for path in _recorded_pack_glob(
            context, "order_manifest.json", kind=kind
        )
        if _SOURCE_DIRECTORY not in path.parts and _EVIDENCE_DIRECTORY not in path.parts
    )
    if not manifests:
        raise _underivable(kind, "pack contains no order manifest")
    checked_entries = 0
    authenticated_artifacts = [plan_artifact]
    for manifest_path in manifests:
        relative = _repo_relative(context.repository, manifest_path)
        artifact, raw = _committed_artifact(context.repository, relative, kind=kind)
        try:
            value = _readiness.parse_json_bytes(raw)
        except _readiness.ArmReadinessError as exc:
            raise _underivable(kind, f"manifest is not strict JSON: {relative}") from exc
        order = value.get("executed_order") if isinstance(value, Mapping) else None
        planned = value.get("planned_n_bundles") if isinstance(value, Mapping) else None
        if (
            not isinstance(order, list)
            or not order
            or planned != len(order)
            or value.get("calibration_plan_sha256") != plan_sha
        ):
            raise _underivable(kind, f"manifest count/plan binding is invalid: {relative}")
        ids: list[str] = []
        for index, item in enumerate(order, start=1):
            if not isinstance(item, Mapping) or item.get("index") != index:
                raise _underivable(kind, f"manifest order is invalid: {relative}")
            config = item.get("config")
            digest = item.get("config_sha256")
            run_id = item.get("run_id")
            if not all(isinstance(part, str) and part for part in (config, digest, run_id)):
                raise _underivable(kind, f"manifest member is malformed: {relative}")
            config_path = manifest_path.parent / PurePosixPath(config)
            config_relative = _repo_relative(context.repository, config_path)
            config_artifact, _ = _committed_artifact(
                context.repository, config_relative, kind=kind
            )
            if config_artifact["sha256"] != digest:
                raise _underivable(kind, f"manifest config digest mismatch: {config_relative}")
            authenticated_artifacts.append(config_artifact)
            ids.append(run_id)
        if len(ids) != len(set(ids)):
            raise _underivable(kind, f"manifest has duplicate run IDs: {relative}")
        checked_entries += len(order)
        authenticated_artifacts.append(artifact)
    return {
        "manifest_count": len(manifests),
        "member_references_checked": checked_entries,
        "authenticated_artifacts": authenticated_artifacts,
    }


def _recorded_generator_check(
    context: _DerivationContext, generator_path: str, *, kind: str
) -> dict[str, Any]:
    command = [sys.executable, str(context.repository / generator_path), "--check"]
    try:
        completed = subprocess.run(
            command,
            cwd=context.repository,
            check=False,
            capture_output=True,
            timeout=180,
            env=_generator_environment(),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _underivable(kind, f"pack generator check could not execute: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise _underivable(kind, f"pack generator --check refused: {detail}")
    return {
        "command": [sys.executable, generator_path, "--check"],
        "exit_code": completed.returncode,
        "stdout_sha256": _readiness.sha256_bytes(completed.stdout),
        "stderr_sha256": _readiness.sha256_bytes(completed.stderr),
    }


# --- U11 projected-pack authentication (PACKAUTH) -------------------------
#
# A pack that has been through the U11 identity-pin projection cannot be
# authenticated by the generator's bare `--check`: `identity_pins
# .freeze_projection` ADDS the projection receipt and its sidecar (which the
# generator then reports as inventory extras) and REWRITES plan_tree.json /
# plan_tree.sha256 / producer_contract.json through `_render_json`
# (sort_keys) while the generator emits insertion-order bytes.  Re-running the
# generator against a projected pack is therefore underivable by construction.
#
# The cure COMPOSES two authentications:
#
#   1. the generator's own derivation of the PRE-projection pack, run against
#      the pack bytes materialised from the receipt's anchored commit, and
#   2. a byte-exact replay of the projection's write set from those
#      pre-projection bytes plus the COMMITTED receipt.
#
# The composed claim is: the committed pack is exactly the generator's
# emission at the anchored commit, plus exactly the U11 projection's
# receipted rewrite of it.
#
# `receipt["pack"]["reviewed_git_commit"]` is a repo-wide HEAD, NOT a
# pack-scoped pin, so it is treated as an UNTRUSTED source of candidate bytes.
# Every binding is derived from digests instead: the byte-exact replay ties the
# anchor's pre-projection plan tree to the committed bytes cryptographically (a
# different anchor renders different bytes), and the subtree fence ties every
# other file in the pack.  The anchor must additionally resolve to a commit and
# be an ancestor of the derivation head, so it lies inside audited history.
#
# The generator imports `joulewise.*` from the tree it is run in, and the
# anchor's library code is NOT pinned by anything.  The materialised tree
# therefore gets HEAD's `joulewise/` and `scripts/` overlaid on top of it, so
# the code that EXECUTES is the reviewed head's code and only pack/data bytes
# come from the anchor.
_PROJECTION_REWRITTEN_FILES = frozenset(
    {"plan_tree.json", "plan_tree.sha256", "producer_contract.json"}
)
_ANCHOR_LIBRARY_PATHS = ("joulewise", "scripts")
_ANCHOR_ARCHIVE_TIMEOUT_SECONDS = 300


def _generator_environment() -> dict[str, str]:
    """Environment for a generator subprocess.

    ``PYTHONDONTWRITEBYTECODE`` keeps the child from leaving ``__pycache__``
    inside the pack directory.  A stray ``__pycache__`` is untracked, so the
    authoring run that created it makes the NEXT authoring run refuse with
    ``evidence_author_pack_uncommitted`` against its own residue.
    """

    return dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _safe_pack_relative(value: object, *, kind: str, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise _underivable(kind, f"{label} is missing")
    if value.startswith("/") or "\\" in value or value.endswith("/"):
        raise _underivable(kind, f"{label} is not a safe pack-relative path: {value}")
    parts = PurePosixPath(value).parts
    if not parts or any(part in {"..", "."} for part in parts):
        raise _underivable(kind, f"{label} is not a safe pack-relative path: {value}")
    return value


def _pack_file_digests(root: Path, *, kind: str, label: str) -> dict[str, str]:
    """Digest every regular file under ``root``, refusing anything else."""

    digests: dict[str, str] = {}
    for directory, subdirectories, filenames in os.walk(root):
        subdirectories.sort()
        for name in sorted(filenames):
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise _underivable(kind, f"{label} contains a symlink: {relative}")
            if not path.is_file():
                raise _underivable(
                    kind, f"{label} contains a non-regular file: {relative}"
                )
            digests[relative] = _readiness.sha256_bytes(path.read_bytes())
    return digests


def _git_capture(
    repository: Path, arguments: Sequence[str], *, kind: str, binary: bool = False
) -> Any:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=False,
            capture_output=True,
            timeout=_ANCHOR_ARCHIVE_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _underivable(kind, f"git {arguments[0]} could not execute: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise _underivable(kind, f"git {arguments[0]} refused: {detail}")
    return completed.stdout if binary else completed.stdout.decode("utf-8")


def _extract_committed_tree(
    repository: Path,
    commit: str,
    destination: Path,
    *,
    kind: str,
    paths: Sequence[str] = (),
) -> None:
    """Materialise ``commit`` (or part of it) into ``destination``.

    ``git archive`` output comes from the repository's own object store, but it
    is still sanitised member by member: nothing may escape ``destination`` and
    no links are admitted, so a hostile pack cannot reach outside the scratch
    tree when it is later walked and executed.
    """

    archive = _git_capture(
        repository,
        ["archive", "--format=tar", commit, *paths],
        kind=kind,
        binary=True,
    )
    try:
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                if member.issym() or member.islnk():
                    raise _underivable(
                        kind, f"anchored tree contains a link: {member.name}"
                    )
                if not (member.isfile() or member.isdir()):
                    raise _underivable(
                        kind, f"anchored tree contains a special file: {member.name}"
                    )
                name = PurePosixPath(member.name)
                if name.is_absolute() or ".." in name.parts:
                    raise _underivable(
                        kind, f"anchored tree member escapes the tree: {member.name}"
                    )
            tar.extractall(destination)
    except tarfile.TarError as exc:
        raise _underivable(kind, f"anchored tree could not be read: {exc}") from exc


def _replay_projection_write_set(
    pre_projection_pack: Path,
    receipt: Mapping[str, Any],
    receipt_relative: str,
    receipt_sha256: str,
    *,
    kind: str,
) -> dict[str, bytes]:
    """Re-derive `freeze_projection`'s write set from pre-projection bytes.

    This mirrors `identity_pins.freeze_projection` exactly, EXCEPT that the
    derived per-unit ``model_runtime_config`` values are taken from the
    committed receipt rather than re-derived: live re-derivation would import
    the mlx runtime adapters, and the evidence author runs under stdlib Python.
    """

    try:
        tree, projection, producer = _identity_pins._load_pack_projection(
            pre_projection_pack
        )
    except _identity_pins.IdentityPinProjectionError as exc:
        raise _underivable(
            kind, f"anchored pack projection is unreadable: {exc}"
        ) from exc
    if projection["state"] == "frozen":
        raise _underivable(kind, "anchored pack is already frozen")
    frozen = copy.deepcopy(projection)
    frozen["state"] = "frozen"
    frozen["projection_receipt"] = {
        "path": receipt_relative,
        "sha256": receipt_sha256,
    }
    runtime_by_id = {
        unit["identity_unit_id"]: unit["model_runtime_config"]
        for unit in receipt["identity_units"]
    }
    for unit in frozen["identity_units"]:
        unit_id = unit["identity_unit_id"]
        if unit_id not in runtime_by_id:
            raise _underivable(
                kind, f"projection receipt omits identity unit: {unit_id}"
            )
        unit["model_runtime_config"] = copy.deepcopy(runtime_by_id[unit_id])
    tree["arm_attachments"]["identity_pin_projection"] = copy.deepcopy(frozen)
    writes: dict[str, bytes] = {}
    if producer is not None:
        producer["identity_pin_projection"] = copy.deepcopy(frozen)
        producer_bytes = _identity_pins._render_json(producer)
        writes["producer_contract.json"] = producer_bytes
        downstream = tree.get("downstream_contract")
        reference = (
            downstream.get("producer_contract")
            if isinstance(downstream, Mapping)
            else None
        )
        if isinstance(reference, dict):
            reference["sha256"] = _identity_pins._sha256_bytes(producer_bytes)
    tree_bytes = _identity_pins._render_json(tree)
    writes["plan_tree.json"] = tree_bytes
    writes["plan_tree.sha256"] = _identity_pins._gnu_sidecar(
        _identity_pins._sha256_bytes(tree_bytes), "plan_tree.json"
    )
    return writes


def _recorded_projected_pack_authentication(
    context: _DerivationContext,
    generator_artifact: Mapping[str, str],
    projection: Mapping[str, Any],
    *,
    kind: str,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    """Authenticate a U11-projected pack; see the block comment above.

    Returns the generator-check record, the projection-authentication record,
    and the artifacts this boundary authenticated as primaries.  Every byte it
    reads is digested into one of the two records.
    """

    pack_relative = _repo_relative(context.repository, context.pack_root)

    # 1. Receipt binding: the committed receipt and its sidecar, proven
    #    byte-identical to the derivation head and to the plan tree's pin.
    reference = projection.get("projection_receipt")
    if not isinstance(reference, Mapping):
        raise _underivable(kind, "frozen projection carries no receipt reference")
    receipt_relative = _safe_pack_relative(
        reference.get("path"), kind=kind, label="projection receipt path"
    )
    if not receipt_relative.endswith(".json"):
        raise _underivable(
            kind, f"projection receipt is not a JSON file: {receipt_relative}"
        )
    sidecar_relative = f"{receipt_relative[: -len('.json')]}.sha256"
    receipt_artifact, receipt_raw = _committed_artifact(
        context.repository, f"{pack_relative}/{receipt_relative}", kind=kind
    )
    sidecar_artifact, sidecar_raw = _committed_artifact(
        context.repository, f"{pack_relative}/{sidecar_relative}", kind=kind
    )
    receipt_sha256 = receipt_artifact["sha256"]
    if reference.get("sha256") != receipt_sha256:
        raise _underivable(
            kind, "projection receipt digest differs from the plan tree reference"
        )
    expected_sidecar = _identity_pins._gnu_sidecar(
        receipt_sha256, PurePosixPath(receipt_relative).name
    )
    if sidecar_raw != expected_sidecar:
        raise _underivable(
            kind, "projection receipt sidecar does not authenticate the receipt"
        )
    try:
        receipt = _identity_pins.validate_projection_receipt(
            _readiness.parse_json_bytes(receipt_raw)
        )
    except (_readiness.ArmReadinessError, _identity_pins.IdentityPinProjectionError) as exc:
        raise _underivable(kind, f"projection receipt is invalid: {exc}") from exc
    if receipt["receipt_kind"] != "freeze_projection" or receipt["status"] != "PASS":
        raise _underivable(kind, "projection receipt is not a passing freeze receipt")
    if receipt["pack"]["pack_id"] != context.pack_root.name:
        raise _underivable(kind, "projection receipt names a different pack")

    # 2. Anchor: untrusted for CONTENT, but it must sit in audited history.
    anchor = receipt["pack"]["reviewed_git_commit"]
    if not isinstance(anchor, str) or not _GIT_RE.fullmatch(anchor):
        raise _underivable(kind, "reviewed_git_commit is not a 40-hex commit")
    try:
        _git_capture(
            context.repository, ["cat-file", "-e", f"{anchor}^{{commit}}"], kind=kind
        )
    except EvidenceAuthoringError as exc:
        raise _underivable(
            kind, f"reviewed_git_commit does not resolve to a commit: {anchor}"
        ) from exc
    try:
        ancestry = subprocess.run(
            [
                "git",
                "-C",
                str(context.repository),
                "merge-base",
                "--is-ancestor",
                anchor,
                context.head_commit,
            ],
            check=False,
            capture_output=True,
            timeout=_ANCHOR_ARCHIVE_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _underivable(kind, f"anchor ancestry could not execute: {exc}") from exc
    if ancestry.returncode != 0:
        raise _underivable(
            kind, "reviewed_git_commit is not an ancestor of the derivation head"
        )

    with tempfile.TemporaryDirectory() as scratch:
        anchored = Path(scratch).resolve()
        # 3. Materialise the anchor, then overlay the reviewed head's library
        #    code so the generator executes reviewed code, not anchor code.
        _extract_committed_tree(context.repository, anchor, anchored, kind=kind)
        for library in _ANCHOR_LIBRARY_PATHS:
            target = anchored / library
            if target.exists():
                shutil.rmtree(target)
        _extract_committed_tree(
            context.repository,
            context.head_commit,
            anchored,
            kind=kind,
            paths=_ANCHOR_LIBRARY_PATHS,
        )
        pre_projection_pack = anchored / pack_relative
        if not pre_projection_pack.is_dir():
            raise _underivable(kind, "pack is absent at the anchored commit")

        # 4. The generator that runs must be the one the plan tree pins.
        generator_relative = generator_artifact["path"]
        anchored_generator = anchored / PurePosixPath(generator_relative)
        if not anchored_generator.is_file():
            raise _underivable(kind, "pack generator is absent at the anchored commit")
        if (
            _readiness.sha256_bytes(anchored_generator.read_bytes())
            != generator_artifact["sha256"]
        ):
            raise _underivable(
                kind, "pack generator at the anchored commit differs from its pin"
            )

        # Census the anchored pack BEFORE running anything in the tree.
        anchored_digests = _pack_file_digests(
            pre_projection_pack, kind=kind, label="anchored pack"
        )

        # 5. The generator's own derivation of the pre-projection pack.
        try:
            completed = subprocess.run(
                [sys.executable, str(anchored_generator), "--check"],
                cwd=anchored,
                check=False,
                capture_output=True,
                timeout=180,
                env=_generator_environment(),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise _underivable(
                kind, f"pack generator check could not execute: {exc}"
            ) from exc
        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", errors="replace").strip()
            raise _underivable(
                kind, f"pack generator --check refused at the anchored commit: {detail}"
            )
        generator_result = {
            "command": [sys.executable, generator_relative, "--check"],
            "exit_code": completed.returncode,
            "stdout_sha256": _readiness.sha256_bytes(completed.stdout),
            "stderr_sha256": _readiness.sha256_bytes(completed.stderr),
        }

        # 6. Subtree fence: the anchor -> committed delta must be EXACTLY the
        #    projection's write set and nothing else.
        committed_digests = _pack_file_digests(
            context.pack_root, kind=kind, label="committed pack"
        )
        added = sorted(set(committed_digests) - set(anchored_digests))
        removed = sorted(set(anchored_digests) - set(committed_digests))
        changed = sorted(
            name
            for name in set(anchored_digests) & set(committed_digests)
            if anchored_digests[name] != committed_digests[name]
        )
        licensed_additions = sorted({receipt_relative, sidecar_relative})
        if added != licensed_additions:
            raise _underivable(
                kind,
                "pack subtree adds files the projection does not license: "
                f"{sorted(set(added) - set(licensed_additions))!r}",
            )
        if removed:
            raise _underivable(
                kind, f"pack subtree removes anchored files: {removed!r}"
            )
        unlicensed = sorted(set(changed) - _PROJECTION_REWRITTEN_FILES)
        if unlicensed:
            raise _underivable(
                kind, f"pack subtree diverges at the anchored commit: {unlicensed!r}"
            )

        # 7. Byte-exact replay of the projection's write set.
        writes = _replay_projection_write_set(
            pre_projection_pack,
            receipt,
            receipt_relative,
            receipt_sha256,
            kind=kind,
        )
        replayed: dict[str, str] = {}
        for relative, expected in sorted(writes.items()):
            actual = (context.pack_root / relative).read_bytes()
            if actual != expected:
                raise _underivable(
                    kind,
                    "projection replay does not reproduce the committed bytes: "
                    f"{relative}",
                )
            replayed[relative] = _readiness.sha256_bytes(expected)

    projection_result = {
        "reviewed_git_commit": anchor,
        "projection_receipt": dict(receipt_artifact),
        "projection_receipt_sidecar": dict(sidecar_artifact),
        "licensed_additions": licensed_additions,
        "replayed_files": replayed,
        "rewritten_files": changed,
        "anchored_file_count": len(anchored_digests),
        "committed_file_count": len(committed_digests),
    }
    return generator_result, projection_result, [receipt_artifact, sidecar_artifact]


def _pack_projection(context: _DerivationContext) -> Mapping[str, Any] | None:
    """Return the pack's identity-pin projection block, if it carries one."""

    attachments = context.tree.get("arm_attachments")
    if not isinstance(attachments, Mapping):
        return None
    projection = attachments.get("identity_pin_projection")
    return projection if isinstance(projection, Mapping) else None


def _derive_pack_authentication(context: _DerivationContext) -> _DerivedKind:
    kind = "PACK_AUTHENTICATION"
    generator = context.tree.get("generator")
    generator_artifact, _ = _pinned_artifact(
        context, generator, kind=kind, label="pack generator"
    )
    projection = _pack_projection(context)
    projection_result: dict[str, Any] | None = None
    projection_primary: list[dict[str, str]] = []
    if (
        projection is not None
        and projection.get("state") == "frozen"
        and projection.get("projection_receipt") is not None
    ):
        # A projected pack is NEVER allowed to fall back to the bare check:
        # a permissive generator would otherwise bypass the projection
        # authentication entirely.
        (
            generator_result,
            projection_result,
            projection_primary,
        ) = _recorded_projected_pack_authentication(
            context, generator_artifact, projection, kind=kind
        )
    else:
        generator_result = _recorded_generator_check(
            context, generator_artifact["path"], kind=kind
        )
    manifests = _validate_manifests(context, kind=kind)
    downstream = context.tree.get("downstream_contract")
    if not isinstance(downstream, Mapping):
        raise _underivable(kind, "pack downstream/extraction contract is missing")
    extraction_pin = downstream.get("extraction_spec")
    extraction_artifact: dict[str, str]
    if isinstance(extraction_pin, Mapping):
        extraction_artifact, extraction_raw = _pinned_artifact(
            context, extraction_pin, kind=kind, label="extraction specification"
        )
        try:
            extraction_value = _readiness.parse_json_bytes(extraction_raw)
        except _readiness.ArmReadinessError as exc:
            raise _underivable(kind, "extraction specification is not JSON") from exc
        errors = _recorded_extraction_validation(
            context, extraction_value, kind=kind
        )
        if errors:
            raise _underivable(kind, f"extraction specification refused: {errors!r}")
    else:
        analysis_path = downstream.get("analysis_manifest_path")
        analysis_sha = downstream.get("analysis_manifest_sha256")
        extraction_artifact, _ = _pinned_artifact(
            context,
            {
                "path": (
                    f"configs/campaigns/{context.pack_root.name}/{analysis_path}"
                ),
                "sha256": analysis_sha,
            },
            kind=kind,
            label="analysis extraction specification",
        )
    attempt = context.tree.get("attempt_policy")
    if (
        not isinstance(attempt, Mapping)
        or not (
            attempt.get("predeclared_before_data") is True
            or attempt.get("retry_commands_present") is False
        )
        or attempt.get("outcome_dependent_top_up") != "forbidden"
    ):
        raise _underivable(kind, "attempt policy is absent or not fail-closed")
    value = {
        "attempt_policy_status": "PASS",
        "committed_pack_digest_status": "PASS",
        "extraction_specification_status": "PASS",
        "manifest_validator_status": "PASS",
        "pack_generator_check_status": "PASS",
        "plan_validator_status": "PASS",
    }
    validator_artifact, _ = _committed_artifact(
        context.repository, "joulewise/floor_extraction.py", kind=kind
    )
    primary = [generator_artifact, extraction_artifact, validator_artifact]
    primary.extend(projection_primary)
    primary.extend(manifests["authenticated_artifacts"])
    return _DerivedKind(
        kind,
        {"desk.current_pack.v1": value},
        tuple(primary),
        (
            _check("pack_generator_check", generator_result),
            *(
                ()
                if projection_result is None
                else (_check("projected_pack_authentication", projection_result),)
            ),
            _check(
                "manifest_validator",
                {
                    "manifest_count": manifests["manifest_count"],
                    "member_references_checked": manifests[
                        "member_references_checked"
                    ],
                },
            ),
        ),
        {
            "pack_sha256": context.pack_sha256,
            "attempt_policy_sha256": _readiness.sha256_bytes(
                _readiness.render_json(attempt)
            ),
        },
    )


def _collect_named_values(value: object, names: frozenset[str]) -> list[str]:
    result: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in names and isinstance(item, str):
                result.append(item)
            result.extend(_collect_named_values(item, names))
    elif isinstance(value, list):
        for item in value:
            result.extend(_collect_named_values(item, names))
    return result


def _derive_estimator_identity(context: _DerivationContext) -> _DerivedKind:
    kind = "ESTIMATOR_IDENTITY"
    _plan_path, _plan_pack_relative, _plan_id, plan_raw, plan_artifact = (
        _recorded_frozen_plan(context, kind=kind)
    )
    try:
        plan_value = _readiness.parse_json_bytes(plan_raw)
    except _readiness.ArmReadinessError as exc:
        raise _underivable(kind, "frozen plan is not JSON") from exc
    estimator_ids = sorted(
        set(_collect_named_values(plan_value, frozenset({"estimator", "point_estimator"})))
    )
    if not estimator_ids:
        raise _underivable(kind, "no estimator identity is derivable from the frozen plan")
    admitted, analysis_registry, detection_registry = _recorded_estimator_registry(
        context, kind=kind
    )
    if not set(estimator_ids).issubset(admitted):
        raise _underivable(kind, f"unregistered estimator IDs: {estimator_ids!r}")
    mint_source, mint_raw = _committed_artifact(
        context.repository, "scripts/mint_floor_artifact_generalized.py", kind=kind
    )
    if b"--estimator" in mint_raw:
        raise _underivable(kind, "mint CLI accepts an operator estimator value")
    registry_source, _ = _committed_artifact(
        context.repository, "joulewise/floor_mint_estimator.py", kind=kind
    )
    value = {
        "admitted_by_mint_registry": True,
        "cli_estimator_id_accepted": False,
        "estimator_id_derived_from_frozen_plan": True,
    }
    return _DerivedKind(
        kind,
        {"desk.estimator_identity.v1": value},
        (
            plan_artifact,
            mint_source,
            registry_source,
            analysis_registry,
            detection_registry,
        ),
        (
            _check(
                "estimator_registry_projection",
                {"derived_estimator_ids": estimator_ids, "admitted_ids": sorted(admitted)},
            ),
        ),
        {"derived_estimator_ids": estimator_ids},
    )


def _derive_mint_trust(context: _DerivationContext) -> _DerivedKind:
    kind = "MINT_TRUST"
    test_ids = (
        "tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests."
        "test_authentication_session_report_parser_refuses_strict_attacks",
        "tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests."
        "test_v2_assurance_and_git_containment_are_required_provenance",
        "tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests."
        "test_report_estimator_vocabulary_injection_refuses_closed_profile",
    )
    result = _run_suite(context, kind, test_ids)
    test_artifact, _ = _committed_artifact(
        context.repository, "tests/test_mint_floor_artifact_generalized.py", kind=kind
    )
    mint_artifact, _ = _committed_artifact(
        context.repository, "scripts/mint_floor_artifact_generalized.py", kind=kind
    )
    value = {"profile_test_status": "PASS", "same_head": True, "same_pack_digest": True}
    return _DerivedKind(
        kind,
        {"desk.mint_trust.v1": value},
        (test_artifact, mint_artifact),
        (_check("d120_profile_suite", result.evidence()),),
        {"bound_head": context.head_commit, "bound_pack_sha256": context.pack_sha256},
    )


def _verify_tree_contract_pins(context: _DerivationContext, *, kind: str) -> list[dict[str, str]]:
    pins: list[object] = [context.tree.get("generator")]
    downstream = context.tree.get("downstream_contract")
    if isinstance(downstream, Mapping):
        pins.extend(
            item
            for item in downstream.values()
            if isinstance(item, Mapping) and {"path", "sha256"}.issubset(item)
        )
        for path_key, sha_key in (
            ("analysis_manifest_path", "analysis_manifest_sha256"),
            (
                "consumer_family_declaration_path",
                "consumer_family_declaration_sha256",
            ),
        ):
            if isinstance(downstream.get(path_key), str) and isinstance(
                downstream.get(sha_key), str
            ):
                pins.append(
                    {
                        "path": (
                            f"configs/campaigns/{context.pack_root.name}/"
                            f"{downstream[path_key]}"
                        ),
                        "sha256": downstream[sha_key],
                    }
                )
    artifacts: list[dict[str, str]] = []
    for index, pin in enumerate(pins):
        artifact, _ = _pinned_artifact(
            context, pin, kind=kind, label=f"pack contract pin {index}"
        )
        artifacts.append(artifact)
    if len(artifacts) < 2:
        raise _underivable(kind, "pack carries too few source/schema pins")
    return artifacts


def _derive_multicell_mint(context: _DerivationContext) -> _DerivedKind:
    kind = "MULTICELL_MINT"
    test_ids = (
        "tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests."
        "test_synthetic_two_plan_four_cell_mint_passes",
        "tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests."
        "test_mixed_four_cell_full_mint_is_cell_local_and_bound",
        "tests.test_mint_floor_artifact_generalized.GeneralizedMintTests."
        "test_7b_shaped_gate_build_and_validator_path_passes",
    )
    result = _run_suite(context, kind, test_ids)
    primary = _verify_tree_contract_pins(context, kind=kind)
    for relative in (
        "scripts/floor_mint_pinsets/schema_v2.json",
        "scripts/mint_floor_artifact_generalized.py",
        "joulewise/floor_mint_estimator.py",
        "tests/test_mint_floor_artifact_generalized.py",
    ):
        artifact, _ = _committed_artifact(context.repository, relative, kind=kind)
        primary.append(artifact)
    value = {
        "focused_integration_status": "PASS",
        "mint_schemas_match_committed_sources": True,
        "pinsets_match_committed_sources": True,
    }
    return _DerivedKind(
        kind,
        {"desk.multicell_mint.v1": value},
        tuple(primary),
        (_check("multicell_mint_focused_integration", result.evidence()),),
        {"authenticated_pin_count": len(primary)},
    )


def _identity_map(tree: Mapping[str, Any], *, kind: str) -> dict[tuple[str, str], object]:
    attachments = tree.get("arm_attachments")
    projection = (
        attachments.get("identity_pin_projection")
        if isinstance(attachments, Mapping)
        else None
    )
    units = projection.get("identity_units") if isinstance(projection, Mapping) else None
    if not isinstance(units, list) or not units:
        raise _underivable(kind, "pack family member lacks identity units")
    result: dict[tuple[str, str], object] = {}
    for unit in units:
        declared = unit.get("declared_identity") if isinstance(unit, Mapping) else None
        bindings = unit.get("consumer_bindings") if isinstance(unit, Mapping) else None
        if not isinstance(declared, Mapping) or not isinstance(bindings, list):
            raise _underivable(kind, "pack family identity unit is malformed")
        for binding in bindings:
            if not isinstance(binding, Mapping):
                raise _underivable(kind, "pack family consumer binding is malformed")
            key = (binding.get("arm"), binding.get("measurement_arm"))
            if not all(isinstance(item, str) and item for item in key) or key in result:
                raise _underivable(kind, "pack family consumer identity is ambiguous")
            result[key] = declared
    return result


def _derive_pack_family(context: _DerivationContext) -> _DerivedKind:
    kind = "PACK_FAMILY"
    trees: dict[str, Mapping[str, Any]] = {}
    artifacts: list[dict[str, str]] = []
    for profile, pack_name in _PACKS_BY_PROFILE.items():
        artifact, raw = _recorded_pack_family_plan_tree(
            context, pack_name, kind=kind
        )
        try:
            tree = _readiness.parse_json_bytes(raw)
        except _readiness.ArmReadinessError as exc:
            raise _underivable(kind, f"{profile} plan tree is not JSON") from exc
        trees[profile] = tree
        artifacts.append(artifact)
    alpha = _identity_map(trees["ALPHA"], kind=kind)
    beta = _identity_map(trees["BETA"], kind=kind)
    gamma = _identity_map(trees["GAMMA"], kind=kind)
    if any(key[0] != "A" for key in alpha) or any(key[0] != "B" for key in beta):
        raise _underivable(kind, "floor pack identity arms are not ALPHA=A and BETA=B")
    expected = {**alpha, **beta}
    if {key[0] for key in gamma} != {"A", "B"}:
        raise _underivable(kind, "transport pack does not carry both floor identity arms")
    for key, gamma_identity in gamma.items():
        if expected.get(key) != gamma_identity:
            raise _underivable(kind, f"floor/transport identity mismatch for {key!r}")
    value = {
        "floor_transport_identities_consistent": True,
        "pack_receipts": ["ALPHA", "BETA", "GAMMA"],
        "same_reviewed_head": True,
    }
    return _DerivedKind(
        kind,
        {"desk.pack_family.v1": value},
        tuple(artifacts),
        (
            _check(
                "pack_family_identity_projection",
                {
                    "profiles": ["ALPHA", "BETA", "GAMMA"],
                    "gamma_identity_keys": [list(item) for item in sorted(gamma)],
                },
            ),
        ),
        {"reviewed_head": context.head_commit},
    )


def _derive_reason_code_coverage(context: _DerivationContext) -> _DerivedKind:
    kind = "REASON_CODE_COVERAGE"
    result = _run_suite(
        context,
        kind,
        (
            "tests.test_arm_readiness_integration.ArmReadinessIntegrationTests."
            "test_refusal_registry_coverage_and_defensive_unreachable_justifications",
        ),
    )
    implementation, raw = _committed_artifact(
        context.repository, "joulewise/arm_readiness.py", kind=kind
    )
    identity, _ = _committed_artifact(
        context.repository, "joulewise/identity_pins.py", kind=kind
    )
    coverage_test, _ = _committed_artifact(
        context.repository, "tests/test_arm_readiness_integration.py", kind=kind
    )
    try:
        runtime_source = raw.decode("utf-8", errors="strict").split(
            "class ArmReadinessError", 1
        )[1]
    except (UnicodeDecodeError, IndexError) as exc:
        raise _underivable(kind, "readiness implementation refusal sites are unreadable") from exc
    produced = set(re.findall(r'"(readiness_[a-z0-9_]+)"', runtime_source))
    registered = set(_readiness.READINESS_REASON_CODES)
    if not produced.issubset(registered):
        raise _underivable(
            kind,
            f"unregistered produced refusals: {sorted(produced-registered)!r}",
        )
    # Codes that are registered but never appear as literals in the runtime
    # source, each for a stated reason.  The R1 entries are resolved BY ROLE
    # from the ruled registry's freeze_evidence_lifecycle.refusal_vocabulary at
    # the moment of refusal: the registry, not this module, is the code/type
    # authority, and the registry-load closure check is what keeps them
    # registered.  This set mirrors `dynamic_or_defensive` in
    # tests/test_arm_readiness_integration.py and must stay in step with it.
    dynamic = {
        "readiness_identity_projection_mint_divergence",
        "readiness_identity_receipt_namespace_anomalous",
        "readiness_lock_unavailable",
        "readiness_r1_class_mismatch",
        "readiness_r1_dependency_changed_set",
        "readiness_r1_dependency_manifest",
        "readiness_r1_successor_chain",
        "readiness_r1_temporal_budget",
        "readiness_r1_unknown_policy",
        "readiness_r1_v1_grandfathering",
    }
    if registered - produced != dynamic:
        raise _underivable(
            kind,
            f"closed refusal census differs: missing={sorted(registered-produced)!r}",
        )
    for code in sorted(registered):
        _readiness._validate_refusal(
            _readiness._receipt_refusal(code), "evidence-author coverage refusal"
        )
    value = {
        "all_produced_refusals_are_closed": True,
        "rehearsal_receipt_status": "PASS",
        "registry_coverage_test_status": "PASS",
    }
    return _DerivedKind(
        kind,
        {"desk.reason_code_plumbing.v1": value},
        (implementation, identity, coverage_test),
        (
            _check(
                "reason_code_census",
                {
                    "registered_count": len(registered),
                    "literal_emission_count": len(produced),
                    "dynamic_or_defensive": sorted(dynamic),
                },
            ),
            _check("reason_code_rehearsal", result.evidence()),
        ),
        {"registered_reason_codes": sorted(registered)},
    )


def _derive_receipt_oracle(context: _DerivationContext) -> _DerivedKind:
    kind = "RECEIPT_ORACLE"
    derived, modules = _recorded_receipt_oracle(context, kind=kind)
    tree_relative = _repo_relative(context.repository, context.pack_root / "plan_tree.json")
    tree_artifact, _ = _committed_artifact(
        context.repository, tree_relative, kind=kind
    )
    actual = context.tree.get("arm_attachments", {}).get("receipt_oracle")
    if actual != derived:
        raise _underivable(kind, "pack receipt oracle differs from fresh production derivation")
    value = {
        "derived_from_committed_ledger_implementation": True,
        "exact_pack_oracle_match": True,
    }
    return _DerivedKind(
        kind,
        {"desk.receipt_oracle.v1": value},
        (*modules, tree_artifact),
        (
            _check(
                "receipt_oracle_byte_equality",
                {"oracle_sha256": _readiness.sha256_bytes(_readiness.render_json(derived))},
            ),
        ),
        {"oracle": derived},
    )


def _derive_recovery_ledger_test(context: _DerivationContext) -> _DerivedKind:
    kind = "RECOVERY_LEDGER_TEST"
    result = _run_suite(context, kind, ("tests.test_calibration_ledger",))
    primary: list[dict[str, str]] = []
    for relative in (
        "joulewise/calibration_ledger.py",
        "scripts/recover_calibration_ledger.py",
        "tests/test_calibration_ledger.py",
    ):
        artifact, _ = _committed_artifact(context.repository, relative, kind=kind)
        primary.append(artifact)
    value = {"bound_head": True, "recovery_ledger_focused_suite_status": "PASS"}
    return _DerivedKind(
        kind,
        {"desk.recovery_ledger_path.v1": value},
        tuple(primary),
        (_check("recovery_ledger_focused_suite", result.evidence()),),
        {"bound_head": context.head_commit},
    )


def _derive_three_window_regression(context: _DerivationContext) -> _DerivedKind:
    kind = "THREE_WINDOW_REGRESSION"
    result = _run_suite(context, kind, ("tests.test_calibration_live_three_window",))
    primary: list[dict[str, str]] = []
    for relative in (
        "tests/test_calibration_live_three_window.py",
        "joulewise/calibration_ledger.py",
        "joulewise/calibration_bracketing.py",
    ):
        artifact, _ = _committed_artifact(context.repository, relative, kind=kind)
        primary.append(artifact)
    value = {
        "profiles": ["ALPHA", "BETA", "GAMMA"],
        "same_head": True,
        "three_window_live_ledger_regression_status": "PASS",
    }
    return _DerivedKind(
        kind,
        {"desk.three_window_regression.v1": value},
        tuple(primary),
        (_check("three_window_live_ledger_regression", result.evidence()),),
        {"bound_head": context.head_commit, "exact_test_count": result.tests_run},
    )


_DERIVERS: dict[str, Callable[[_DerivationContext], _DerivedKind]] = {
    "ACCEPTANCE_OWNER": _derive_acceptance_owner,
    "ACCEPTANCE_SUCCESSOR": _derive_acceptance_successor,
    "DOCTRINE_PIN": _derive_doctrine_pin,
    "ESTIMATOR_IDENTITY": _derive_estimator_identity,
    "MINT_TRUST": _derive_mint_trust,
    "MULTICELL_MINT": _derive_multicell_mint,
    "PACK_AUTHENTICATION": _derive_pack_authentication,
    "PACK_FAMILY": _derive_pack_family,
    "REASON_CODE_COVERAGE": _derive_reason_code_coverage,
    "RECEIPT_ORACLE": _derive_receipt_oracle,
    "RECOVERY_LEDGER_TEST": _derive_recovery_ledger_test,
    "THREE_WINDOW_REGRESSION": _derive_three_window_regression,
}


def _unrouted_deriver_reads(source: str | None = None) -> tuple[str, ...]:
    """Return ordinary unrecorded IO calls reachable from a deriver.

    This developer-error lint catches recognized direct call spellings, the
    same calls in reachable top-level helpers, and simple callable aliases
    acquired from those spellings (including ``builtins``/``importlib``/``os``
    module expressions).  Deliberate same-interpreter circumvention is outside
    D-139 and this function is not a security boundary or complete data-flow
    analysis.
    """

    if source is None:
        source = Path(__file__).read_text(encoding="utf-8")
    tree = _ast.parse(source)
    definitions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef))
    }
    imported_raw_aliases = {
        imported.asname or imported.name
        for node in tree.body
        if isinstance(node, _ast.ImportFrom)
        for imported in node.names
        if imported.name in _DERIVER_DIRECT_READ_CALLS
    }
    pending = sorted(name for name in definitions if name.startswith("_derive_"))
    visited: set[str] = set()
    findings: list[str] = []
    while pending:
        function_name = pending.pop()
        if function_name in visited:
            continue
        visited.add(function_name)
        node = definitions[function_name]
        raw_aliases: set[str] = set(imported_raw_aliases)
        helper_aliases: dict[str, str] = {}

        def assigned_names(target: _ast.expr) -> tuple[str, ...]:
            if isinstance(target, _ast.Name):
                return (target.id,)
            if isinstance(target, (_ast.Tuple, _ast.List)):
                return tuple(
                    name for item in target.elts for name in assigned_names(item)
                )
            return ()

        def terminal_name(value: _ast.expr) -> str | None:
            if isinstance(value, _ast.Name):
                return value.id
            if isinstance(value, _ast.Attribute):
                return value.attr
            if (
                isinstance(value, _ast.Call)
                and isinstance(value.func, _ast.Name)
                and value.func.id == "getattr"
                and len(value.args) >= 2
                and isinstance(value.args[1], _ast.Constant)
                and isinstance(value.args[1].value, str)
            ):
                return value.args[1].value
            return None

        # Resolve the cheap, local aliases that commonly arise while moving a
        # read into a helper.  Attribute acquisition is keyed by the terminal
        # operation name, so these include ``os.open``,
        # ``__import__('builtins').open``, and
        # ``importlib.import_module('builtins').open``.  Fixed-point propagation
        # also catches ``reader2 = reader`` and ``call = local_helper``.
        assignments: list[tuple[tuple[str, ...], _ast.expr]] = []
        for child in _ast.walk(node):
            if isinstance(child, _ast.Assign):
                names = tuple(
                    name
                    for target in child.targets
                    for name in assigned_names(target)
                )
                assignments.append((names, child.value))
            elif isinstance(child, _ast.AnnAssign):
                if child.value is not None:
                    assignments.append((assigned_names(child.target), child.value))
            elif isinstance(child, _ast.ImportFrom):
                for imported in child.names:
                    local_name = imported.asname or imported.name
                    if imported.name in _DERIVER_DIRECT_READ_CALLS:
                        raw_aliases.add(local_name)
                    elif imported.name in definitions:
                        helper_aliases[local_name] = imported.name
        changed = True
        while changed:
            changed = False
            for names, value in assignments:
                acquired = terminal_name(value)
                if acquired in _DERIVER_DIRECT_READ_CALLS or acquired in raw_aliases:
                    for name in names:
                        if name not in raw_aliases:
                            raw_aliases.add(name)
                            changed = True
                helper = helper_aliases.get(acquired or "", acquired)
                if helper in definitions:
                    for name in names:
                        if helper_aliases.get(name) != helper:
                            helper_aliases[name] = helper
                            changed = True
        for child in _ast.walk(node):
            if not isinstance(child, _ast.Call):
                continue
            called: str | None = None
            if isinstance(child.func, _ast.Name):
                called = child.func.id
            elif isinstance(child.func, _ast.Attribute):
                called = child.func.attr
            if called in _DERIVER_DIRECT_READ_CALLS or called in raw_aliases:
                findings.append(f"{function_name}:{child.lineno}:{called}")
            if isinstance(child.func, _ast.Name):
                helper = helper_aliases.get(child.func.id, child.func.id)
                if (
                    helper in definitions
                    and helper not in _DERIVER_RECORDED_READ_BOUNDARIES
                    and helper not in visited
                ):
                    pending.append(helper)
    return tuple(sorted(findings))


def _assert_deriver_read_routing() -> None:
    findings = _unrouted_deriver_reads()
    if findings:
        raise AssertionError(f"unrouted deriver read(s): {findings!r}")


_assert_deriver_read_routing()


def _required_generic_rows(
    pack_root: Path, tree: Mapping[str, Any]
) -> tuple[list[Mapping[str, Any]], list[str]]:
    registry, _raw, reference = _readiness._registry_reference(pack_root)
    rows = _readiness._profile_rows(registry, reference["plan_profile"], phase="freeze")
    successor = not _readiness._issued_d079(tree)
    applicable = [
        row
        for row in rows
        if _readiness.applicability_for_row(
            row, clock_route="MANUAL", successor_acceptance=successor
        )
        == "REQUIRED"
    ]
    kinds = sorted(
        {
            kind
            for row in applicable
            for kind in row["required_evidence_kinds"]
            if kind not in _SPECIALIZED_EVIDENCE_KINDS
        }
    )
    return applicable, kinds


def _r1_lifecycle_registry_for_pack(
    pack_root: Path,
) -> Mapping[str, Any] | None:
    registry, _raw, _reference = _readiness._registry_reference(pack_root)
    if registry["schema_version"] != _readiness.R1_ROW_REGISTRY_SCHEMA:
        return None
    return _readiness.validate_r1_lifecycle_registry(
        registry["freeze_evidence_lifecycle"]
    )


def _r1_policies_for_kinds(
    registry: Mapping[str, Any], kinds: Sequence[str]
) -> dict[str, Mapping[str, Any]]:
    # Preserve the registry-owned refusal spelling while refusing before the
    # general registry validator can collapse a class override into a schema
    # error.  This inspection grants no policy authority: the expected value
    # comes only from the code table.
    raw_policies = registry.get("evidence_policies")
    raw_refusals = registry.get("refusal_vocabulary")
    if isinstance(raw_policies, list) and isinstance(raw_refusals, list):
        class_entries = [
            item
            for item in raw_refusals
            if isinstance(item, Mapping) and item.get("role") == "CLASS_MISMATCH"
        ]
        if len(class_entries) == 1 and isinstance(class_entries[0].get("code"), str):
            for kind in kinds:
                matches = [
                    item
                    for item in raw_policies
                    if isinstance(item, Mapping) and item.get("kind") == kind
                ]
                code_class = _readiness.R1_EVIDENCE_FRESHNESS_CLASSES.get(kind)
                if (
                    len(matches) == 1
                    and code_class is not None
                    and matches[0].get("freshness_class") != code_class
                ):
                    raise _refuse(
                        kind,
                        str(class_entries[0]["code"]),
                        f"registry class differs from the {kind} code constant",
                    )
    try:
        governed = _readiness.validate_r1_lifecycle_registry(registry)
    except _readiness.ArmReadinessError as exc:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_lifecycle_registry_unresolved",
            str(exc),
        ) from exc
    policies: dict[str, Mapping[str, Any]] = {}
    for kind in kinds:
        code_class = _DERIVER_FRESHNESS_CLASSES.get(kind)
        matches = [
            item for item in governed["evidence_policies"] if item["kind"] == kind
        ]
        if len(matches) != 1:
            entry = _readiness._r1_refusal_entry(governed, "UNKNOWN_POLICY")
            raise _refuse(
                kind,
                str(entry["code"]),
                f"registry has no unique lifecycle policy for {kind}",
            )
        policy = matches[0]
        if code_class is None or policy["freshness_class"] != code_class:
            entry = _readiness._r1_refusal_entry(governed, "CLASS_MISMATCH")
            raise _refuse(
                kind,
                str(entry["code"]),
                f"registry class differs from the {kind} code constant",
            )
        if (
            code_class == "EXECUTION_BOUND"
            and policy["environment_comparison"]
            not in _SUPPORTED_ENVIRONMENT_COMPARISONS
        ):
            entry = _readiness._r1_refusal_entry(governed, "UNKNOWN_POLICY")
            raise _refuse(
                kind,
                str(entry["code"]),
                "execution-environment comparison semantics remain Ed-reserved",
            )
        policies[kind] = policy
    return policies


def _r1_rederive_at_arm(
    pack_root: Path,
    receipt: Mapping[str, Any],
    source: Mapping[str, Any],
) -> None:
    """Re-derive the two RE_DERIVABLE kinds and compare their semantics."""

    kind = str(receipt["kind"])
    if _DERIVER_FRESHNESS_CLASSES.get(kind) != "RE_DERIVABLE":
        return
    repository = _readiness._repo_for_pack(pack_root)
    tree, _tree_raw = _readiness._plan_tree(pack_root)
    context = _DerivationContext(
        pack_root=pack_root,
        repository=repository,
        tree=tree,
        pack_sha256=str(receipt["pack_sha256"]),
        head_commit=str(receipt["derivation_commit"]),
    )
    derived = _DERIVERS[kind](context)
    expected_facts = [
        {"fact_id": fact_id, "value": copy.deepcopy(value)}
        for fact_id, value in sorted(derived.facts.items())
    ]
    expected_checks = [dict(item) for item in derived.checks]
    if (
        source.get("facts") != expected_facts
        or source.get("checks") != expected_checks
        or source.get("derivation") != dict(derived.derivation)
    ):
        raise ValueError(f"{kind} ARM re-derivation differs from authored semantics")


def _source_path(kind: str) -> str:
    return f"{_SOURCE_DIRECTORY}/{_slug(kind)}.json"


def _receipt_name(kind: str) -> str:
    return f"evidence-{_slug(kind)}.json"


def _evidence_id(kind: str) -> str:
    return f"freeze-{_slug(kind)}-v1"


def _assemble_receipt(
    context: _DerivationContext,
    derived: _DerivedKind,
    source_raw: bytes,
    *,
    issued_at_utc: str,
    boot_session_id: str,
    valid_until_monotonic_ns: int,
) -> dict[str, Any]:
    source_digest = _readiness.sha256_bytes(source_raw)
    receipt = {
        "schema_version": _readiness.EVIDENCE_RECEIPT_SCHEMA,
        "evidence_id": _evidence_id(derived.kind),
        "kind": derived.kind,
        "status": "PASS",
        "issued_at_utc": issued_at_utc,
        "boot_session_id": boot_session_id,
        "valid_until_monotonic_ns": valid_until_monotonic_ns,
        "pack_sha256": context.pack_sha256,
        "head_commit": context.head_commit,
        "facts": [
            {
                "fact_id": fact_id,
                "value_type": "OBJECT",
                "value": copy.deepcopy(dict(value)),
                "source_kind": (
                    "PACK"
                    if derived.kind
                    in {
                        "ACCEPTANCE_SUCCESSOR",
                        "DOCTRINE_PIN",
                        "ESTIMATOR_IDENTITY",
                        "PACK_FAMILY",
                    }
                    else "PROBE"
                ),
                "source_path": _source_path(derived.kind),
                "source_sha256": source_digest,
            }
            for fact_id, value in sorted(derived.facts.items())
        ],
        "checks": [
            {"check_id": item["check_id"], "status": item["status"]}
            for item in derived.checks
        ],
        "reason_codes": [],
        "assurance": copy.deepcopy(_readiness.ASSURANCE),
    }
    _readiness.validate_evidence_receipt(receipt)
    return receipt


def _assemble_r1_receipt(
    context: _DerivationContext,
    derived: _DerivedKind,
    source_raw: bytes,
    policy: Mapping[str, Any],
    *,
    issued_at_utc: str,
    boot_session_id: str,
    now_monotonic_ns: int,
    environment_fingerprint: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source_digest = _readiness.sha256_bytes(source_raw)
    freshness_class = str(policy["freshness_class"])
    if freshness_class not in {"RE_DERIVABLE", "EXECUTION_BOUND"}:
        raise _refuse(
            derived.kind,
            "evidence_author_lifecycle_registry_unresolved",
            f"generic deriver cannot issue freshness class {freshness_class!r}",
        )
    receipt: dict[str, Any] = {
        "schema_version": (
            _readiness.CONTENT_EVIDENCE_RECEIPT_SCHEMA
            if freshness_class == "RE_DERIVABLE"
            else _readiness.EXECUTION_EVIDENCE_RECEIPT_SCHEMA
        ),
        "evidence_id": _evidence_id(derived.kind),
        "kind": derived.kind,
        "status": "PASS",
        "issued_at_utc": issued_at_utc,
        "freshness_class": freshness_class,
        "freshness_policy_id": policy["freshness_policy_id"],
        "pack_sha256": context.pack_sha256,
        "derivation_commit": context.head_commit,
        "dependency_manifest_sha256": source_digest,
        "facts": [
            {
                "fact_id": fact_id,
                "value_type": "OBJECT",
                "value": copy.deepcopy(dict(value)),
                "source_kind": (
                    "PACK"
                    if derived.kind
                    in {
                        "ACCEPTANCE_SUCCESSOR",
                        "DOCTRINE_PIN",
                        "ESTIMATOR_IDENTITY",
                        "PACK_FAMILY",
                    }
                    else "PROBE"
                ),
                "source_path": _source_path(derived.kind),
                "source_sha256": source_digest,
            }
            for fact_id, value in sorted(derived.facts.items())
        ],
        "checks": [
            {"check_id": item["check_id"], "status": item["status"]}
            for item in derived.checks
        ],
        "reason_codes": [],
        "assurance": copy.deepcopy(_readiness.ASSURANCE),
    }
    if freshness_class == "EXECUTION_BOUND":
        horizon = policy["horizon_ns"]
        if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon <= 0:
            raise _refuse(
                derived.kind,
                "evidence_author_lifecycle_registry_unresolved",
                "execution-bound horizon is not an Ed-resolved positive integer",
            )
        if not isinstance(environment_fingerprint, Mapping):
            raise _refuse(
                derived.kind,
                "evidence_author_lifecycle_registry_unresolved",
                "execution-bound environment fingerprint is absent",
            )
        receipt.update(
            {
                "boot_session_id": boot_session_id,
                "valid_until_monotonic_ns": now_monotonic_ns + horizon,
                "environment_fingerprint": copy.deepcopy(
                    dict(environment_fingerprint)
                ),
            }
        )
    _readiness.validate_evidence_receipt(receipt)
    return receipt


def _validate_source(value: object, *, expected_kind: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("evidence source is not an object")
    schema = value.get("schema_version")
    expected_keys = _R1_SOURCE_KEYS if schema == _R1_SOURCE_SCHEMA else _SOURCE_KEYS
    if set(value) != expected_keys:
        raise ValueError("evidence source has unknown or missing keys")
    if schema not in {_SOURCE_SCHEMA, _R1_SOURCE_SCHEMA} or value["kind"] != expected_kind:
        raise ValueError("evidence source schema/kind is invalid")
    if not isinstance(value["head_commit"], str) or not _GIT_RE.fullmatch(value["head_commit"]):
        raise ValueError("evidence source HEAD is invalid")
    if not isinstance(value["pack_sha256"], str) or not _SHA_RE.fullmatch(value["pack_sha256"]):
        raise ValueError("evidence source pack digest is invalid")
    if schema == _R1_SOURCE_SCHEMA:
        if (
            value["derivation_commit"] != value["head_commit"]
            or value["freshness_class"] not in {"RE_DERIVABLE", "EXECUTION_BOUND"}
            or not isinstance(value["freshness_policy_id"], str)
            or not value["freshness_policy_id"]
            or (
                value["freshness_class"] == "RE_DERIVABLE"
                and value["environment_fingerprint"] is not None
            )
            or (
                value["freshness_class"] == "EXECUTION_BOUND"
                and not isinstance(value["environment_fingerprint"], Mapping)
            )
        ):
            raise ValueError("R1 evidence source lifecycle binding is invalid")
    primary = value["primary_artifacts"]
    facts = value["facts"]
    checks = value["checks"]
    if (
        not isinstance(primary, list)
        or not isinstance(facts, list)
        or not isinstance(checks, list)
    ):
        raise ValueError("evidence source arrays are invalid")
    for item in primary:
        if (
            not isinstance(item, Mapping)
            or set(item) != _PRIMARY_KEYS
            or not isinstance(item["path"], str)
            or not isinstance(item["sha256"], str)
            or not _SHA_RE.fullmatch(item["sha256"])
        ):
            raise ValueError("evidence source primary artifact is invalid")
    for item in facts:
        if not isinstance(item, Mapping) or set(item) != _SOURCE_FACT_KEYS:
            raise ValueError("evidence source fact is invalid")
    for item in checks:
        if (
            not isinstance(item, Mapping)
            or set(item) != _SOURCE_CHECK_KEYS
            or item["status"] != "PASS"
        ):
            raise ValueError("evidence source check is invalid")
    return value


def _authenticate_existing(
    pack_root: Path,
    repository: Path,
    tree: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    kinds: Sequence[str],
) -> dict[str, Any]:
    source_dir = pack_root / _SOURCE_DIRECTORY
    evidence_dir = pack_root / _EVIDENCE_DIRECTORY
    if not source_dir.is_dir() or not evidence_dir.is_dir():
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_output_collision",
            "existing evidence/source namespace is incomplete",
        )
    expected_sources = {_source_path(kind).split("/", 1)[1] for kind in kinds}
    expected_evidence = {
        name
        for kind in kinds
        for name in (_receipt_name(kind), f"{_receipt_name(kind)}.sha256")
    }
    if {path.name for path in source_dir.iterdir()} != expected_sources or {
        path.name for path in evidence_dir.iterdir()
    } != expected_evidence:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_output_collision",
            "existing evidence/source namespace differs from the governed file set",
        )
    boot_session_id = _readiness._current_boot_session_id()
    now = time.monotonic_ns()
    head = _readiness.reviewed_main(pack_root)["head_commit"]
    receipts: dict[str, Mapping[str, Any]] = {}
    receipts_by_kind: dict[str, Mapping[str, Any]] = {}
    receipt_bytes_by_kind: dict[str, bytes] = {}
    source_bytes_by_kind: dict[str, bytes] = {}
    paths: list[str] = []
    for kind in kinds:
        source_path = source_dir / f"{_slug(kind)}.json"
        receipt_path = evidence_dir / _receipt_name(kind)
        try:
            source_raw = source_path.read_bytes()
            receipt_raw = receipt_path.read_bytes()
            sidecar = receipt_path.with_name(f"{receipt_path.name}.sha256").read_bytes()
            source = _validate_source(
                _readiness.parse_json_bytes(source_raw, require_canonical=True),
                expected_kind=kind,
            )
            receipt = _readiness.validate_evidence_receipt(
                _readiness.parse_json_bytes(receipt_raw, require_canonical=True)
            )
        except (OSError, ValueError, _readiness.ArmReadinessError) as exc:
            raise _refuse(
                kind,
                "evidence_author_existing_invalid",
                f"existing {kind} evidence is invalid: {exc}",
            ) from exc
        digest = _readiness.sha256_bytes(receipt_raw)
        if sidecar != _readiness.gnu_sidecar(digest, receipt_path.name):
            raise _refuse(kind, "evidence_author_existing_invalid", "existing sidecar differs")
        if (
            receipt["evidence_id"] != _evidence_id(kind)
            or receipt["kind"] != kind
            or receipt["boot_session_id"] != boot_session_id
            or receipt["valid_until_monotonic_ns"] < now
            or receipt["head_commit"] != head
            or source["head_commit"] != receipt["head_commit"]
            or source["pack_sha256"] != receipt["pack_sha256"]
        ):
            raise _refuse(
                kind,
                "evidence_author_existing_stale",
                "existing evidence binding is stale",
            )
        source_digest = _readiness.sha256_bytes(source_raw)
        source_facts = {item["fact_id"]: item["value"] for item in source["facts"]}
        if any(
            fact["source_path"] != _source_path(kind)
            or fact["source_sha256"] != source_digest
            or source_facts.get(fact["fact_id"]) != fact["value"]
            for fact in receipt["facts"]
        ):
            raise _refuse(
                kind,
                "evidence_author_existing_invalid",
                "existing source binding differs",
            )
        for primary in source["primary_artifacts"]:
            artifact, _raw = _committed_artifact(
                repository, primary["path"], kind=kind
            )
            if artifact != primary:
                raise _refuse(kind, "evidence_author_existing_stale", "primary artifact changed")
        receipts[receipt["evidence_id"]] = receipt
        receipts_by_kind[kind] = receipt
        receipt_bytes_by_kind[kind] = receipt_raw
        source_bytes_by_kind[kind] = source_raw
        paths.append(str(receipt_path))
    pack_digests = {receipt["pack_sha256"] for receipt in receipts_by_kind.values()}
    if len(pack_digests) != 1:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_existing_invalid",
            "existing evidence does not share one pre-author pack digest",
        )
    context = _DerivationContext(
        pack_root=pack_root,
        repository=repository,
        tree=tree,
        pack_sha256=pack_digests.pop(),
        head_commit=head,
    )
    freshly_derived: list[_DerivedKind] = []
    for kind in kinds:
        derived = _DERIVERS[kind](context)
        if derived.kind != kind:
            raise _refuse(
                kind,
                "evidence_author_internal_error",
                "deriver returned the wrong kind",
            )
        expected_source = _fact_source(context, derived)
        if expected_source != source_bytes_by_kind[kind]:
            raise _refuse(
                kind,
                "evidence_author_existing_invalid",
                "existing source differs from freshly derived bytes",
            )
        receipt = receipts_by_kind[kind]
        expected_receipt = _assemble_receipt(
            context,
            derived,
            expected_source,
            issued_at_utc=receipt["issued_at_utc"],
            boot_session_id=receipt["boot_session_id"],
            valid_until_monotonic_ns=receipt["valid_until_monotonic_ns"],
        )
        if _readiness.render_json(expected_receipt) != receipt_bytes_by_kind[kind]:
            raise _refuse(
                kind,
                "evidence_author_existing_invalid",
                "existing receipt differs from freshly derived bytes",
            )
        freshly_derived.append(derived)
    _reauthenticate_primary_artifacts(context, freshly_derived)
    for row in rows:
        if any(kind in kinds for kind in row["required_evidence_kinds"]):
            matching = [
                receipt
                for receipt in receipts.values()
                if receipt["kind"] in row["required_evidence_kinds"]
            ]
            if not any(
                _readiness._predicate_passes(item, row["predicate_id"])
                for item in matching
            ):
                raise _refuse(
                    str(row["required_evidence_kinds"][0]),
                    "evidence_author_existing_invalid",
                    f"existing evidence does not satisfy {row['predicate_id']}",
                )
    return {
        "status": "PASS",
        "authored_kinds": list(kinds),
        "receipt_paths": paths,
        "mutated": False,
    }


def _authenticate_existing_r1(
    pack_root: Path,
    repository: Path,
    tree: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    kinds: Sequence[str],
    lifecycle_registry: Mapping[str, Any],
    policies: Mapping[str, Mapping[str, Any]],
    *,
    step6_confirmation_table: Path | str | None = None,
    expected_confirmation_digest: str | None = None,
) -> dict[str, Any]:
    source_dir = pack_root / _SOURCE_DIRECTORY
    evidence_dir = pack_root / _EVIDENCE_DIRECTORY
    expected_sources = {f"{_slug(kind)}.json" for kind in kinds}
    expected_evidence = {
        name
        for kind in kinds
        for name in (_receipt_name(kind), f"{_receipt_name(kind)}.sha256")
    }
    try:
        observed_sources = {path.name for path in source_dir.iterdir()}
        observed_evidence = {path.name for path in evidence_dir.iterdir()}
    except OSError as exc:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_existing_invalid",
            f"R1 evidence namespace is unreadable: {exc}",
        ) from exc
    if observed_sources != expected_sources or observed_evidence != expected_evidence:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_output_collision",
            "existing R1 evidence namespace differs from the governed set",
        )
    current_head = _readiness.reviewed_main(pack_root)["head_commit"]
    _repository, _prefix, pack_relative = _readiness._repository_and_pack_relative(
        pack_root
    )
    context = _DerivationContext(
        pack_root=pack_root,
        repository=repository,
        tree=tree,
        pack_sha256=_readiness.committed_pack_tree_sha256(pack_root),
        head_commit=current_head,
    )
    receipts: dict[str, Mapping[str, Any]] = {}
    paths: list[str] = []
    for kind in kinds:
        source_path = source_dir / f"{_slug(kind)}.json"
        receipt_path = evidence_dir / _receipt_name(kind)
        try:
            source_raw = source_path.read_bytes()
            receipt_raw = receipt_path.read_bytes()
            sidecar = receipt_path.with_name(f"{receipt_path.name}.sha256").read_bytes()
            source = _validate_source(
                _readiness.parse_json_bytes(source_raw, require_canonical=True),
                expected_kind=kind,
            )
            receipt = _readiness.validate_evidence_receipt(
                _readiness.parse_json_bytes(receipt_raw, require_canonical=True)
            )
        except (OSError, ValueError, _readiness.ArmReadinessError) as exc:
            raise _refuse(
                kind,
                "evidence_author_existing_invalid",
                f"existing R1 evidence is invalid: {exc}",
            ) from exc
        digest = _readiness.sha256_bytes(receipt_raw)
        if sidecar != _readiness.gnu_sidecar(digest, receipt_path.name):
            raise _refuse(
                kind, "evidence_author_existing_invalid", "existing sidecar differs"
            )
        try:
            _readiness.validate_r1_evidence_lifecycle(
                repository,
                receipt,
                source,
                lifecycle_registry,
                current_head=current_head,
                expected_freshness_class=str(policies[kind]["freshness_class"]),
                plan_tree_path=f"{pack_relative}/plan_tree.json",
                step6_confirmation_table=step6_confirmation_table,
                expected_confirmation_digest=expected_confirmation_digest,
            )
            if receipt["freshness_class"] == "RE_DERIVABLE":
                _r1_rederive_at_arm(pack_root, receipt, source)
            elif (
                policies[kind]["environment_comparison"]
                == "EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE"
                and receipt["environment_fingerprint"]
                != _execution_environment_fingerprint(context, kind)
            ):
                raise _refuse(
                    kind,
                    "evidence_author_environment_changed",
                    "execution-environment fingerprint differs at re-use",
                )
        except _readiness.EvidenceLifecycleError as exc:
            raise _refuse(kind, exc.reason_code, str(exc)) from exc
        except ValueError as exc:
            entry = _readiness._r1_refusal_entry(
                lifecycle_registry, "DEPENDENCY_MANIFEST"
            )
            raise _refuse(kind, str(entry["code"]), str(exc)) from exc
        if (
            receipt["evidence_id"] != _evidence_id(kind)
            or receipt["kind"] != kind
            or _readiness.sha256_bytes(source_raw)
            != receipt["dependency_manifest_sha256"]
        ):
            raise _refuse(
                kind,
                "evidence_author_existing_invalid",
                "existing R1 receipt metadata differs",
            )
        receipts[receipt["evidence_id"]] = receipt
        paths.append(str(receipt_path))
    for row in rows:
        if any(kind in kinds for kind in row["required_evidence_kinds"]):
            matching = [
                receipt
                for receipt in receipts.values()
                if receipt["kind"] in row["required_evidence_kinds"]
            ]
            if not any(
                _readiness._predicate_passes(item, row["predicate_id"])
                for item in matching
            ):
                raise _refuse(
                    str(row["required_evidence_kinds"][0]),
                    "evidence_author_existing_invalid",
                    f"existing R1 evidence does not satisfy {row['predicate_id']}",
                )
    return {
        "status": "PASS",
        "authored_kinds": list(kinds),
        "receipt_paths": paths,
        "mutated": False,
    }


def author_arm_readiness_evidence(
    pack_root: Path | str,
    *,
    step6_confirmation_table: Path | str | None = None,
    expected_confirmation_digest: str | None = None,
) -> dict[str, Any]:
    """Author every applicable generic FREEZE_AND_ARM evidence receipt.

    Boot identity, clocks, hashes, HEAD, facts, statuses, suite outcomes, and
    names have no API arguments and are always derived here.
    """

    root = Path(pack_root).resolve(strict=True)
    repository = _readiness._repo_for_pack(root)
    tree, _tree_raw = _readiness._plan_tree(root)
    rows, kinds = _required_generic_rows(root, tree)
    lifecycle_registry = _r1_lifecycle_registry_for_pack(root)
    r1_policies = (
        _r1_policies_for_kinds(lifecycle_registry, kinds)
        if lifecycle_registry is not None
        else None
    )
    unsupported = sorted(set(kinds) - set(_DERIVERS))
    if unsupported:
        raise _refuse(
            unsupported[0],
            "evidence_author_kind_unsupported",
            f"no production deriver for registry kind(s): {unsupported!r}",
        )
    source_dir = root / _SOURCE_DIRECTORY
    evidence_dir = root / _EVIDENCE_DIRECTORY
    if source_dir.exists() or evidence_dir.exists():
        if lifecycle_registry is not None and r1_policies is not None:
            return _authenticate_existing_r1(
                root,
                repository,
                tree,
                rows,
                kinds,
                lifecycle_registry,
                r1_policies,
                step6_confirmation_table=step6_confirmation_table,
                expected_confirmation_digest=expected_confirmation_digest,
            )
        return _authenticate_existing(
            root,
            repository,
            tree,
            rows,
            kinds,
        )

    try:
        pack_sha = _readiness.committed_pack_tree_sha256(root)
    except _readiness.ArmReadinessError as exc:
        raise _refuse(
            "PACK_AUTHENTICATION",
            "evidence_author_pack_uncommitted",
            str(exc),
        ) from exc
    head = _readiness.reviewed_main(root)["head_commit"]
    if not isinstance(head, str) or _GIT_RE.fullmatch(head) is None:
        raise _refuse(
            "PACK_AUTHENTICATION",
            "evidence_author_head_underivable",
            "HEAD commit is not derivable",
        )
    context = _DerivationContext(
        pack_root=root,
        repository=repository,
        tree=tree,
        pack_sha256=pack_sha,
        head_commit=head,
    )
    derived: list[_DerivedKind] = []
    for kind in kinds:
        try:
            item = _DERIVERS[kind](context)
        except EvidenceAuthoringError:
            raise
        except Exception as exc:
            raise _underivable(kind, f"unexpected derivation failure: {exc}") from exc
        if item.kind != kind:
            raise _refuse(
                kind,
                "evidence_author_internal_error",
                "deriver returned the wrong kind",
            )
        derived.append(item)

    issued_at = _readiness._utc_now()
    boot_session_id = _readiness._current_boot_session_id()
    evaluated_at_monotonic_ns = time.monotonic_ns()
    valid_until = evaluated_at_monotonic_ns + _EVIDENCE_VALIDITY_NS
    source_bytes: dict[str, bytes] = {}
    receipt_bytes: dict[str, bytes] = {}
    semantic_receipts: dict[str, Mapping[str, Any]] = {}
    for item in derived:
        policy = r1_policies[item.kind] if r1_policies is not None else None
        environment_fingerprint = (
            _execution_environment_fingerprint(context, item.kind)
            if policy is not None and policy["freshness_class"] == "EXECUTION_BOUND"
            else None
        )
        source_raw = (
            _r1_fact_source(
                context,
                item,
                policy,
                environment_fingerprint,
            )
            if policy is not None
            else _fact_source(context, item)
        )
        source_bytes[f"{_slug(item.kind)}.json"] = source_raw
        receipt = (
            _assemble_r1_receipt(
                context,
                item,
                source_raw,
                policy,
                issued_at_utc=issued_at,
                boot_session_id=boot_session_id,
                now_monotonic_ns=evaluated_at_monotonic_ns,
                environment_fingerprint=environment_fingerprint,
            )
            if policy is not None
            else _assemble_receipt(
                context,
                item,
                source_raw,
                issued_at_utc=issued_at,
                boot_session_id=boot_session_id,
                valid_until_monotonic_ns=valid_until,
            )
        )
        raw = _readiness.render_json(receipt)
        name = _receipt_name(item.kind)
        receipt_bytes[name] = raw
        receipt_bytes[f"{name}.sha256"] = _readiness.gnu_sidecar(
            _readiness.sha256_bytes(raw), name
        )
        semantic_receipts[receipt["evidence_id"]] = receipt
    for row in rows:
        if any(kind in kinds for kind in row["required_evidence_kinds"]):
            matching = [
                receipt
                for receipt in semantic_receipts.values()
                if receipt["kind"] in row["required_evidence_kinds"]
            ]
            if not any(
                _readiness._predicate_passes(item, row["predicate_id"])
                for item in matching
            ):
                raise _refuse(
                    str(row["required_evidence_kinds"][0]),
                    "evidence_author_predicate_refused",
                    f"authored facts do not satisfy {row['predicate_id']}",
                )
    _reauthenticate_primary_artifacts(context, derived)
    if _readiness.reviewed_main(root)["head_commit"] != head:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_input_changed",
            "HEAD changed during derivation",
        )
    if _readiness.committed_pack_tree_sha256(root) != pack_sha:
        raise _refuse(
            "AUTHORING_SET",
            "evidence_author_input_changed",
            "pack bytes changed during derivation",
        )

    staging = Path(tempfile.mkdtemp(prefix=".arm-readiness-evidence-", dir=root.parent))
    installed = False
    try:
        staged_sources = staging / _SOURCE_DIRECTORY
        staged_evidence = staging / _EVIDENCE_DIRECTORY
        staged_sources.mkdir()
        staged_evidence.mkdir()
        for name, raw in source_bytes.items():
            (staged_sources / name).write_bytes(raw)
        for name, raw in receipt_bytes.items():
            (staged_evidence / name).write_bytes(raw)
        if (
            _readiness.reviewed_main(root)["head_commit"] != head
            or _readiness.committed_pack_tree_sha256(root) != pack_sha
        ):
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_input_changed",
                "HEAD or pack bytes changed before publication",
            )
        if source_dir.exists() or evidence_dir.exists():
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_output_collision",
                "evidence namespace appeared during derivation",
            )
        os.replace(staged_sources, source_dir)
        try:
            os.replace(staged_evidence, evidence_dir)
        except Exception:
            shutil.rmtree(source_dir)
            raise
        installed = True
        items, discovered, refusals = _readiness._discover_evidence(
            root,
            root,
            pack_sha256=None,
            head_commit=head,
            boot_session_id=boot_session_id,
            now_monotonic_ns=time.monotonic_ns(),
            lifecycle_registry=lifecycle_registry,
        )
        if refusals or set(discovered) != set(semantic_receipts):
            raise _refuse(
                "AUTHORING_SET",
                "evidence_author_validation_failed",
                f"authored discovery refused: {refusals!r}",
            )
        for receipt in discovered.values():
            _readiness.validate_evidence_receipt(receipt)
        paths = [
            str(root / item["path"])
            for item in sorted(items, key=lambda value: value["evidence_id"])
        ]
    except Exception:
        if installed:
            shutil.rmtree(evidence_dir, ignore_errors=True)
            shutil.rmtree(source_dir, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return {
        "status": "PASS",
        "authored_kinds": list(kinds),
        "receipt_paths": paths,
        "mutated": True,
    }


def _assert_public_author_signature() -> None:
    parameters = inspect.signature(author_arm_readiness_evidence).parameters
    if tuple(parameters) != (
        "pack_root",
        "step6_confirmation_table",
        "expected_confirmation_digest",
    ) or any(
        parameters[name].kind is not inspect.Parameter.KEYWORD_ONLY
        or parameters[name].default is not None
        for name in ("step6_confirmation_table", "expected_confirmation_digest")
    ):
        raise AssertionError(
            "public evidence author accepts only pack_root plus the two "
            "keyword-only step-6 custody inputs"
        )


_assert_public_author_signature()


__all__ = [
    "EvidenceAuthoringError",
    "author_arm_readiness_evidence",
]
