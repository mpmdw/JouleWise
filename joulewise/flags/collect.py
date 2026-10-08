"""Record-only collectors for the desk and the arm.

Each collector checks one thing that used to refuse on the retired arm path
and, instead of refusing, returns flags. Every collector runs in its own
subprocess with a timeout (:func:`run_collector`); an exception, a timeout or
malformed output becomes a ``collector_errors`` entry, never a refusal. The
arm decision never imports this module (``tests/flags/test_flags_import_graph.py``).

Collectors (``COLLECTORS``):

``pack_identity``
    The committed pack tree (the D-134 framing of
    ``arm_readiness.committed_pack_tree_sha256``, ported here, not imported),
    every file digest the plan tree pins (science configs, identity-unit
    config inventories, external inputs, extraction spec, producer contract,
    decode workload, calibration plan, condition families, generator,
    campaign policy, acceptance artifact), run-id uniqueness and the run id
    inside each science config. Any difference is ``pack.identity_mismatch``.
``checkout_identity``
    The measurement checkout's HEAD is H_claim, or descends from it through
    commits that change no window input (code, configuration, the chain-source
    runbook): pin-only commits, the seal commit's three documents, and paths
    no window reads are listed and raise no flag. It has no tracked edits, and
    no untracked files under the executed roots. Otherwise
    ``code.executed_differs_from_sealed``.
    Untracked files elsewhere are disclosed (``records.checkout_untracked``).
``executed_code``
    SHA-256 of tracked files under ``joulewise/``, ``scripts/`` and the pack,
    plus the chain bytes; written create-once to custody and compared with the
    sealed inventory and the chain sidecar. The sealed inventory lists every
    pack of the block; only its entries under this window's roots are
    compared, strictly. Any difference is ``code.executed_differs_from_sealed``.
``model_identity``
    The model artifact digest (``provenance.model_artifact_identity``), the
    declared revision and the tokenizer bytes of each identity unit, and the
    runtime package versions of the measurement interpreter, against their
    pins; when the projection is frozen and asked for, also
    ``identity_pins.verify_frozen_projection``. A difference is
    ``model.identity_mismatch``; no pin is ``model.identity_unpinned``, which
    excludes the window until L6 seals the pins.
``ledger_readiness``
    ``scripts/recover_calibration_ledger.py readiness`` (read-only). A refusal
    is ``calibration.ledger_not_ready`` (disclosed: the chain's own
    reservation is what binds the window).

A NUMBER check that does not run is never silent. A missing input (no
H_claim, no sealed inventory, no registered pack-tree digest) makes the
collector emit ``<family>.identity_unmeasured``; a collector that errs or
times out makes :func:`run_collectors` emit the same code for it. Those codes
exclude the window.
"""

from __future__ import annotations

import hashlib
import json
import os
import signal
import stat
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from joulewise.flags.schema import (
    FlagSchemaError,
    canonical_json_bytes,
    make_flag,
    make_interval,
    make_scope,
    make_source,
    now_stamp,
    validate_flag,
)

COLLECTOR_RUN_SCHEMA = "joulewise.flag_collector_run.v1"
EXECUTED_INVENTORY_SCHEMA = "joulewise.executed_code_inventory.v1"
PACK_DIGEST_DOMAIN = b"joulewise.committed_pack_tree_sha256.v1\n"
DEFAULT_TIMEOUT_S = 120.0
DEFAULT_TIMEOUTS_S = {
    "pack_identity": 120.0,
    "checkout_identity": 60.0,
    "executed_code": 180.0,
    "model_identity": 900.0,
    "ledger_readiness": 120.0,
}
# At the arm the driver kills the whole collector call after 120 s
# (joulewise.b5.driver.COLLECTOR_TIMEOUT_S), so the per-collector budgets must
# fit inside it with room for process start-up: a slow collector then times
# out on its own and leaves its own unmeasured flag and run row, instead of
# the outer kill losing every collector's record (PLAN2 row 12).  The real
# block-5 rehearsals took at most 14.5 s (model_identity, two models).
ARM_TIMEOUTS_S = {
    "pack_identity": 15.0,
    "checkout_identity": 10.0,
    "executed_code": 15.0,
    "model_identity": 55.0,
    "ledger_readiness": 15.0,
}
ARM_OUTER_TIMEOUT_S = 120.0
DEFAULT_PIN_ONLY_PATHS = ("configs/calibration/calibration_ledger_head.json",)
# The head comparison puts every path that differs between H_claim and HEAD in
# one class. The harvest uses the same classes (joulewise.b5.harvest
# head_change_class; tests compare the two).
#
# Seal documents: the sealed inventory names H_claim as its head, and a file
# cannot name the commit that contains it, so the filled inventory and the
# registration and analysis-plan text that name H_claim are committed in the
# seal commit, the child of H_claim. These three paths differ between H_claim
# and every head a window runs from. The seal record pins their SHA-256s.
SEAL_DOCUMENT_PATHS = tuple(
    f"configs/campaigns/v5_claim_25g83/{name}"
    for name in ("sealed_inventory.json", "registration_block5.md", "analysis_plan_block5.md")
)
# Window inputs: code, configuration, and the runbook whose pre-calibration
# screen the plan writer copies into the chain. A changed window input is
# code.executed_differs_from_sealed. Any other changed path (documents, tests,
# status files) cannot change a window's bytes; it is listed in the collector's
# observed record and raises no flag.
WINDOW_INPUT_PREFIXES = ("joulewise/", "scripts/", "configs/")
WINDOW_INPUT_FILES = ("docs/phase_2/window_runbook.md",)
HEAD_CHANGE_CLASSES = ("pin_only", "seal_document", "window_input", "record_only")
GIT_TIMEOUT_S = 30.0
_SHA_KEYS = ("sha256", "byte_sha256", "actual_sha256", "artifact_sha256")
_PIN_FORMS = (
    ("path", _SHA_KEYS),
    ("config_path", ("config_sha256",)),
    ("manifest_path", ("manifest_sha256",)),
)
_MAX_LISTED = 50


class CollectorError(RuntimeError):
    """A collector could not run (an I/O or tool failure, not a finding)."""


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(repo: Path, *args: str, timeout_s: float = GIT_TIMEOUT_S) -> bytes:
    try:
        completed = subprocess.run(
            ("git", "-C", str(repo), *args),
            check=False,
            capture_output=True,
            timeout=timeout_s,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CollectorError(f"git {' '.join(args)} could not run: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise CollectorError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout


def _context_scope(params: Mapping[str, Any], level: str = "window", **extra: Any) -> dict[str, Any]:
    return make_scope(level, plan_id=params.get("plan_id"), attempt=params.get("attempt"), **extra)


def _flag(
    params: Mapping[str, Any],
    collector: str,
    *,
    code: str,
    family: str,
    klass: str,
    observed: Any,
    expected: Any,
    detail: str,
    legacy_site: str | None,
    legacy_code: str | None = None,
    level: str = "window",
    evidence: Iterable[Mapping[str, str]] = (),
    **scope_extra: Any,
) -> dict[str, Any]:
    return make_flag(
        code=code,
        family=family,
        klass=klass,
        scope=_context_scope(params, level, **scope_extra),
        source=make_source(
            params.get("stage", "desk"),
            f"joulewise.flags.collect.{collector}",
            legacy_site=legacy_site,
            legacy_code=legacy_code,
        ),
        observed=observed,
        expected=expected,
        evidence=evidence,
        detail=detail,
        interval=make_interval(),
        catalog_sha256=params.get("catalog_sha256"),
    )


def _unmeasured(
    params: Mapping[str, Any],
    collector: str,
    *,
    code: str,
    family: str,
    check: str,
    detail: str,
    missing_input: str | None = None,
    klass: str = "NUMBER",
    **observed: Any,
) -> dict[str, Any]:
    """A NUMBER check that did not run; the window is not claim-usable without it."""

    return _flag(
        params, collector, code=code, family=family, klass=klass,
        observed={"check": check, "missing_input": missing_input, **observed},
        expected={"check_ran": True}, detail=detail, legacy_site=None,
    )


def _require(params: Mapping[str, Any], key: str) -> Any:
    value = params.get(key)
    if not value:
        raise CollectorError(f"input {key} was not given")
    return value


def _repo_root_of(path: Path) -> Path:
    raw = _git(path, "rev-parse", "--show-toplevel").rstrip(b"\n")
    return Path(raw.decode("utf-8")).resolve(strict=True)


# --------------------------------------------------------------------------
# pack identity
# --------------------------------------------------------------------------


class PackTreeProblem(Exception):
    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(detail)
        self.reason = reason
        self.detail = detail


def committed_pack_tree_sha256(pack_root: Path) -> str:
    """D-134 framing of the committed pack tree, ported from ``arm_readiness``.

    Raises :class:`PackTreeProblem` with reason ``not_committed`` (untracked
    entry, no committed files), ``unreadable``, ``namespace_anomalous`` or
    ``digest_mismatch`` (disk bytes or mode differ from the committed blob).
    The digest is byte-for-byte the one ``arm_readiness`` computes; a test
    compares the two on the committed packs.
    """

    try:
        root = pack_root.resolve(strict=True)
        repository = _repo_root_of(root)
        relative = root.relative_to(repository).as_posix()
    except (OSError, ValueError, CollectorError) as exc:
        raise PackTreeProblem("not_committed", f"pack root is not below a Git worktree: {exc}") from exc
    try:
        tree_raw = _git(repository, "ls-tree", "-rz", "--full-tree", "HEAD", "--", relative)
    except CollectorError as exc:
        raise PackTreeProblem("not_committed", str(exc)) from exc
    prefix = relative.encode("utf-8") + b"/"
    committed: dict[bytes, tuple[str, str]] = {}
    for record in tree_raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, repository_path = record.split(b"\t", 1)
            mode_raw, type_raw, oid_raw = metadata.split(b" ", 2)
        except ValueError as exc:
            raise PackTreeProblem("namespace_anomalous", "malformed Git tree entry") from exc
        if not repository_path.startswith(prefix):
            raise PackTreeProblem("namespace_anomalous", "Git returned an out-of-pack path")
        relative_raw = repository_path[len(prefix):]
        mode = mode_raw.decode("ascii")
        if mode not in {"100644", "100755"} or type_raw != b"blob":
            raise PackTreeProblem("namespace_anomalous", f"inadmissible mode/type for {relative_raw!r}")
        committed[relative_raw] = (mode, oid_raw.decode("ascii"))
    if not committed:
        raise PackTreeProblem("not_committed", "pack contains no committed files")
    disk: dict[bytes, Path] = {}
    directories: set[bytes] = set()
    try:
        for path in root.rglob("*"):
            relative_path = path.relative_to(root).as_posix().encode("utf-8")
            status = path.lstat()
            if stat.S_ISLNK(status.st_mode):
                raise PackTreeProblem("namespace_anomalous", f"pack symlink is forbidden: {path}")
            if stat.S_ISREG(status.st_mode):
                disk[relative_path] = path
            elif stat.S_ISDIR(status.st_mode):
                directories.add(relative_path)
            else:
                raise PackTreeProblem("namespace_anomalous", f"special pack entry: {path}")
    except OSError as exc:
        raise PackTreeProblem("unreadable", f"cannot inventory pack bytes: {exc}") from exc
    committed_dirs = {
        b"/".join(item.split(b"/")[:index])
        for item in committed
        for index in range(1, len(item.split(b"/")))
    }
    if directories - committed_dirs:
        raise PackTreeProblem(
            "not_committed", f"untracked pack directory: {min(directories - committed_dirs)!r}"
        )
    if set(disk) - set(committed):
        raise PackTreeProblem("not_committed", f"untracked pack entry: {min(set(disk) - set(committed))!r}")
    if set(committed) - set(disk):
        raise PackTreeProblem("unreadable", f"committed pack entry is missing: {min(set(committed) - set(disk))!r}")
    framed = bytearray(PACK_DIGEST_DOMAIN)
    for relative_raw in sorted(committed):
        mode, oid = committed[relative_raw]
        path = disk[relative_raw]
        try:
            raw = path.read_bytes()
            blob = _git(repository, "cat-file", "blob", oid)
            disk_mode = "100755" if path.stat().st_mode & 0o111 else "100644"
        except (OSError, CollectorError) as exc:
            raise PackTreeProblem("unreadable", f"cannot authenticate pack file {path}: {exc}") from exc
        if raw != blob or disk_mode != mode:
            raise PackTreeProblem(
                "digest_mismatch", f"disk and committed bytes/mode differ for {relative_raw!r}"
            )
        framed.extend(relative_raw + b"\0" + mode.encode("ascii") + b"\0")
        framed.extend(str(len(raw)).encode("ascii") + b"\0")
        framed.extend(hashlib.sha256(raw).hexdigest().encode("ascii") + b"\n")
    return hashlib.sha256(bytes(framed)).hexdigest()


def plan_tree_pins(tree: Any, trail: str = "") -> list[tuple[str, str, str]]:
    """Every ``(json_pointer, path, sha256)`` file pin in a plan tree.

    A pin is an object carrying ``path`` with one of ``sha256``,
    ``byte_sha256``, ``actual_sha256`` or ``artifact_sha256``;
    ``config_path`` with ``config_sha256``; or ``manifest_path`` with
    ``manifest_sha256``.
    """

    pins: list[tuple[str, str, str]] = []
    if isinstance(tree, Mapping):
        for path_key, sha_keys in _PIN_FORMS:
            if not isinstance(tree.get(path_key), str):
                continue
            sha_key = next((key for key in sha_keys if isinstance(tree.get(key), str)), None)
            if sha_key is not None:
                pins.append((f"{trail}/{path_key}", tree[path_key], tree[sha_key]))
        for key in sorted(tree):
            pins.extend(plan_tree_pins(tree[key], f"{trail}/{key}"))
    elif isinstance(tree, list):
        for index, item in enumerate(tree):
            pins.extend(plan_tree_pins(item, f"{trail}/{index}"))
    return pins


def roster_run_ids(tree: Mapping[str, Any]) -> list[str | None]:
    """Run ids of the science roster plus every external-input member list."""

    run_ids: list[str | None] = [
        row.get("run_id") for row in tree.get("science", []) if isinstance(row, Mapping)
    ]

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            members = value.get("members")
            if isinstance(members, list):
                run_ids.extend(m.get("run_id") for m in members if isinstance(m, Mapping))
            for key in sorted(value):
                if key != "members":
                    walk(value[key])
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(tree.get("external_inputs"))
    return run_ids


def _resolve_pin_path(raw: str, pack_root: Path, repo_root: Path) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    repo_candidate = repo_root / candidate
    pack_candidate = pack_root / candidate
    if raw.startswith(("configs/", "scripts/", "joulewise/", "docs/")) or (
        repo_candidate.exists() and not pack_candidate.exists()
    ):
        return repo_candidate
    return pack_candidate


def collect_pack_identity(params: Mapping[str, Any]) -> dict[str, Any]:
    pack_root = Path(_require(params, "pack_root"))
    repo_root = Path(params["repo_root"]) if params.get("repo_root") else _repo_root_of(pack_root)
    name = "pack_identity"
    flags: list[dict[str, Any]] = []
    observed: dict[str, Any] = {"pack_root": str(pack_root)}

    def mismatch(check: str, obs: Any, exp: Any, detail: str, legacy: str, legacy_code: str) -> None:
        flags.append(
            _flag(
                params, name, code="pack.identity_mismatch", family="PACK_IDENTITY",
                klass="NUMBER", observed={"check": check, **obs}, expected=exp,
                detail=detail, legacy_site=legacy, legacy_code=legacy_code,
            )
        )

    # 1. committed pack tree
    try:
        digest = committed_pack_tree_sha256(pack_root)
        observed["committed_pack_tree_sha256"] = digest
        expected_digest = params.get("expected_pack_tree_sha256")
        if not expected_digest:
            # The file pins below do not cover plan_tree.json itself, so
            # without the registered digest the pack is not verified.
            flags.append(
                _unmeasured(
                    params, name, code="pack.identity_unmeasured", family="PACK_IDENTITY",
                    check="pack_tree_digest", missing_input="expected_pack_tree_sha256",
                    detail="no registered pack-tree digest given; the committed tree was not compared",
                    pack_tree_sha256=digest,
                )
            )
        elif digest != expected_digest:
            mismatch(
                "pack_tree_digest", {"pack_tree_sha256": digest},
                {"pack_tree_sha256": expected_digest},
                "committed pack tree differs from the digest registered at H_claim",
                "joulewise/arm_readiness.py:committed_pack_tree_sha256", "readiness_pack_digest_mismatch",
            )
    except PackTreeProblem as problem:
        observed["committed_pack_tree_sha256"] = None
        mismatch(
            "pack_committed", {"reason": problem.reason, "problem": problem.detail}, {"committed": True},
            f"pack tree is not the committed tree: {problem.detail}",
            "joulewise/arm_readiness.py:committed_pack_tree_sha256",
            f"readiness_pack_{problem.reason}",
        )

    # 2. plan tree file pins
    tree_path = pack_root / "plan_tree.json"
    try:
        tree = json.loads(tree_path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        mismatch(
            "plan_tree_readable", {"problem": str(exc)}, {"path": "plan_tree.json"},
            "plan_tree.json is unreadable", "scripts/write_v5_qualification_plan.py:pack_roster",
            "plan_tree_unreadable",
        )
        return {"flags": flags, "observed": observed}
    pins = plan_tree_pins(tree)
    differing = []
    missing = []
    for pointer, raw_path, expected_sha in pins:
        target = _resolve_pin_path(raw_path, pack_root, repo_root)
        try:
            actual = _sha256_file(target)
        except OSError:
            missing.append({"pointer": pointer, "path": raw_path})
            continue
        if actual != expected_sha:
            differing.append({"pointer": pointer, "path": raw_path, "sha256": actual, "pinned": expected_sha})
    observed["pins_checked"] = len(pins)
    if missing:
        mismatch(
            "pinned_file_missing", {"missing": missing[:_MAX_LISTED], "n_missing": len(missing)},
            {"present": True}, f"{len(missing)} pinned pack file(s) missing (e.g. {missing[0]['path']})",
            "joulewise/arm_readiness_evidence.py:_pinned_artifact", "evidence_author_<kind>_underivable",
        )
    if differing:
        mismatch(
            "pinned_file_digest", {"differing": differing[:_MAX_LISTED], "n_differing": len(differing)},
            {"sha256": "as pinned in plan_tree.json"},
            f"{len(differing)} pack file(s) differ from their plan-tree pins (e.g. {differing[0]['path']})",
            "joulewise/arm_readiness_evidence.py:_pinned_artifact",
            "evidence_author_pack_authentication_underivable",
        )

    # 3. roster: run-id uniqueness, and the run id inside each science config
    run_ids = roster_run_ids(tree)
    duplicates = sorted(rid for rid, count in Counter(run_ids).items() if rid is not None and count > 1)
    observed["run_ids"] = len(run_ids)
    if duplicates:
        mismatch(
            "run_id_unique", {"duplicate_run_ids": duplicates[:_MAX_LISTED]}, {"duplicates": 0},
            f"duplicate run_id in the pack roster: {duplicates[0]}",
            "scripts/write_v5_qualification_plan.py:pack_roster", "pack_roster_duplicate_run_id",
        )
    wrong_ids = []
    for row in tree.get("science", []):
        if not isinstance(row, Mapping) or not isinstance(row.get("config_path"), str):
            continue
        target = _resolve_pin_path(row["config_path"], pack_root, repo_root)
        try:
            config = json.loads(target.read_bytes())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue  # already reported as missing or differing
        if isinstance(config, Mapping) and config.get("run_id") != row.get("run_id"):
            wrong_ids.append({"config_path": row["config_path"], "run_id": config.get("run_id"),
                              "roster_run_id": row.get("run_id")})
    if wrong_ids:
        mismatch(
            "config_run_id", {"differing": wrong_ids[:_MAX_LISTED]}, {"run_id": "as in roster"},
            f"{len(wrong_ids)} science config(s) carry a run_id other than the roster's",
            "scripts/write_v5_qualification_plan.py:pack_roster", "pack_roster_run_id_mismatch",
        )
    return {"flags": flags, "observed": observed}


# --------------------------------------------------------------------------
# checkout identity and executed code
# --------------------------------------------------------------------------


def _executed_roots(params: Mapping[str, Any], repo: Path) -> list[str]:
    """``joulewise``, ``scripts`` (or ``params["roots"]``) and the pack, repo-relative."""

    roots = list(params.get("roots") or ["joulewise", "scripts"])
    if params.get("pack_root"):
        try:
            pack = Path(params["pack_root"]).resolve()
            roots.append(pack.relative_to(repo.resolve()).as_posix())
        except (OSError, ValueError):
            pass
    return roots


def _under(path: str, roots: Sequence[str]) -> bool:
    return any(path == root or path.startswith(root.rstrip("/") + "/") for root in roots)


def head_change_class(path: str, pin_only: Iterable[str] = DEFAULT_PIN_ONLY_PATHS) -> str:
    """The class of one path that differs between H_claim and HEAD (see ``SEAL_DOCUMENT_PATHS``)."""

    if path in pin_only:
        return "pin_only"
    if path in SEAL_DOCUMENT_PATHS:
        return "seal_document"
    # Letter case is ignored here: the measurement Mac's volume does not
    # distinguish case, so a tracked "Joulewise/x.py" lands in joulewise/.
    folded = path.casefold()
    if folded.startswith(WINDOW_INPUT_PREFIXES) or folded in WINDOW_INPUT_FILES:
        return "window_input"
    return "record_only"


def collect_checkout_identity(params: Mapping[str, Any]) -> dict[str, Any]:
    """HEAD descends from H_claim and no window input changed; no tracked edits; no importable strays.

    The paths that differ between H_claim and HEAD are classed by
    :func:`head_change_class`. A changed window input, or a HEAD that does not
    descend from H_claim, is ``code.executed_differs_from_sealed``. Pin-only
    paths, the three seal documents and paths no window reads are listed in
    ``observed`` and raise no flag.

    Tracked edits anywhere, and untracked files under the executed roots
    (``joulewise/``, ``scripts/``, the pack: Python can import them), are
    ``code.executed_differs_from_sealed``. Other untracked files (notes,
    backups) cannot change what runs; they are disclosed as
    ``records.checkout_untracked`` (plan 3.5 "has tracked edits"; inventory
    row night_gate.py:1503).
    """

    repo = Path(params["repo_root"])
    h_claim = params.get("h_claim")
    pin_only = tuple(params.get("pin_only_paths") or DEFAULT_PIN_ONLY_PATHS)
    name = "checkout_identity"
    roots = _executed_roots(params, repo)
    head = _git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    tracked = [
        line for line in _git(repo, "status", "--porcelain", "--untracked-files=no")
        .decode("utf-8", "replace").splitlines() if line.strip()
    ]
    untracked = sorted(
        item.decode("utf-8", "replace")
        for item in _git(repo, "ls-files", "-z", "--others", "--exclude-standard").split(b"\0")
        if item
    )
    importable = [path for path in untracked if _under(path, roots)]
    elsewhere = [path for path in untracked if not _under(path, roots)]
    observed: dict[str, Any] = {
        "head": head, "tracked_edits": len(tracked), "untracked_in_executed_roots": len(importable),
        "untracked_elsewhere": len(elsewhere), "executed_roots": roots,
    }
    flags = []
    if tracked:
        flags.append(
            _flag(
                params, name, code="code.executed_differs_from_sealed", family="CODE_IDENTITY",
                klass="NUMBER", observed={"check": "checkout_clean", "head": head,
                                          "status": tracked[:_MAX_LISTED]},
                expected={"status": []},
                detail=f"measurement checkout has {len(tracked)} tracked edit(s)",
                legacy_site="joulewise/night_gate.py:1503", legacy_code="night_plan_stale",
            )
        )
    if importable:
        flags.append(
            _flag(
                params, name, code="code.executed_differs_from_sealed", family="CODE_IDENTITY",
                klass="NUMBER", observed={"check": "untracked_in_executed_roots", "head": head,
                                          "untracked": importable[:_MAX_LISTED]},
                expected={"untracked": [], "roots": roots},
                detail=f"{len(importable)} untracked file(s) under the executed roots",
                legacy_site="joulewise/night_gate.py:1503", legacy_code="night_plan_stale",
            )
        )
    if elsewhere:
        flags.append(
            _flag(
                params, name, code="records.checkout_untracked", family="RECORDS",
                klass="REPRESENTATION", observed={"check": "untracked_elsewhere", "head": head,
                                                  "untracked": elsewhere[:_MAX_LISTED]},
                expected=None,
                detail=f"{len(elsewhere)} untracked file(s) outside the executed roots (disclosed)",
                legacy_site="joulewise/night_gate.py:1503", legacy_code="night_plan_stale",
            )
        )
    if not h_claim:
        flags.append(
            _unmeasured(
                params, name, code="code.identity_unmeasured", family="CODE_IDENTITY",
                check="head_is_h_claim", missing_input="h_claim", head=head,
                detail="no H_claim given; the checkout HEAD was not compared with the sealed commit",
            )
        )
    else:
        changed: list[str] = []
        ancestor = True
        if head != h_claim:
            try:
                _git(repo, "merge-base", "--is-ancestor", h_claim, head)
            except CollectorError:
                ancestor = False
            if ancestor:
                # --no-renames lists both paths of a moved file, so a window
                # input moved out of its directory is still listed; -z never
                # quotes a path, so each is classed by its real first characters.
                changed = sorted(
                    item.decode("utf-8", "replace")
                    for item in _git(repo, "diff", "--name-only", "--no-renames", "-z", h_claim, head).split(b"\0")
                    if item
                )
        classes: dict[str, list[str]] = {klass: [] for klass in HEAD_CHANGE_CLASSES}
        for path in changed:
            classes[head_change_class(path, pin_only)].append(path)
        extra = classes["window_input"]
        observed.update({"h_claim": h_claim, "descends_from_h_claim": ancestor,
                         "changed_paths": changed[:_MAX_LISTED],
                         "changed_path_counts": {klass: len(paths) for klass, paths in classes.items()},
                         "seal_document_changes": classes["seal_document"],
                         "record_only_changes": classes["record_only"][:_MAX_LISTED]})
        if not ancestor or extra:
            flags.append(
                _flag(
                    params, name, code="code.executed_differs_from_sealed", family="CODE_IDENTITY",
                    klass="NUMBER",
                    observed={"check": "head_is_h_claim", "head": head, "descends": ancestor,
                              "window_input_changes": extra[:_MAX_LISTED]},
                    expected={"head": h_claim, "pin_only_paths": list(pin_only),
                              "seal_document_paths": list(SEAL_DOCUMENT_PATHS)},
                    detail="measurement checkout HEAD does not descend from H_claim, or a window input "
                           "(code, configuration or the chain-source runbook) changed since H_claim",
                    legacy_site="joulewise/night_gate.py:1470", legacy_code="night_plan_stale",
                )
            )
    return {"flags": flags, "observed": observed}


def executed_inventory(repo: Path, roots: Sequence[str], extra_files: Sequence[Path] = ()) -> dict[str, str]:
    """``{repo-relative path: sha256}`` of tracked files under ``roots`` plus ``extra_files``."""

    listed = _git(repo, "ls-files", "-z", "--", *roots).split(b"\0")
    files: dict[str, str] = {}
    for raw in listed:
        if not raw:
            continue
        relative = raw.decode("utf-8")
        target = repo / relative
        try:
            files[relative] = _sha256_file(target)
        except FileNotFoundError:
            files[relative] = "MISSING"
    for path in extra_files:
        key = str(path)
        try:
            resolved = Path(path).resolve()
            key = resolved.relative_to(repo.resolve()).as_posix()
        except (OSError, ValueError):
            key = str(Path(path).resolve())
        files[key] = _sha256_file(Path(path))
    return dict(sorted(files.items()))


def _sealed_files(document: Any) -> tuple[dict[str, str], list[str] | None]:
    if not isinstance(document, Mapping):
        raise CollectorError("sealed inventory must be a JSON object")
    files = document.get("files", document.get("inventory"))
    if isinstance(files, Mapping):
        mapping = {str(k): str(v) for k, v in files.items()}
    elif isinstance(files, list):
        mapping = {str(item["path"]): str(item["sha256"]) for item in files}
    else:
        raise CollectorError("sealed inventory needs files as {path: sha256} or [{path, sha256}]")
    roots = document.get("roots")
    return mapping, (list(roots) if isinstance(roots, list) else None)


def _window_scope(
    roots: Sequence[str], sealed_roots: Sequence[str] | None, params: Mapping[str, Any]
) -> Callable[[str], bool]:
    """Which repo-relative paths this window's inventory is compared on.

    A window inventories only its own roots (``joulewise/``, ``scripts/`` and
    its own pack), while the sealed inventory lists every pack of the block
    and the flag catalog. A sealed entry outside the window's roots is not
    code this window executes, so it is neither missing nor added here
    (registration 14 Q2). Within the window's roots the comparison stays
    strict: every sealed file must be present with its digest and every
    inventoried file must be sealed. When the sealed inventory declares
    ``roots``, a path must lie under those too. Pin-only paths are data.
    """

    pin_only = set(params.get("pin_only_paths") or DEFAULT_PIN_ONLY_PATHS)

    def in_scope(path: str) -> bool:
        if path in pin_only or not _under(path, roots):
            return False
        return sealed_roots is None or _under(path, sealed_roots)

    return in_scope


def collect_executed_code(params: Mapping[str, Any]) -> dict[str, Any]:
    """Executed files against the sealed inventory, within this window's roots.

    ``changed`` is every path both list with different digests; ``missing``
    and ``added`` are counted only under the window's own roots
    (:func:`_window_scope`), so a sealed inventory that lists all three packs
    does not make every window differ.
    """

    repo = Path(params["repo_root"])
    name = "executed_code"
    roots = _executed_roots(params, repo)
    extra = [Path(params["chain_path"])] if params.get("chain_path") else []
    inventory = executed_inventory(repo, roots, extra)
    head = _git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    document = {
        "schema_version": EXECUTED_INVENTORY_SCHEMA,
        "repo_root": str(repo),
        "head": head,
        "roots": roots,
        "files": inventory,
    }
    raw = canonical_json_bytes(document) + b"\n"
    inventory_sha = hashlib.sha256(raw).hexdigest()
    evidence = []
    custody = params.get("custody_root")
    if custody:
        relative = f"flags/executed_inventory.{params.get('stage', 'desk')}.{inventory_sha[:12]}.json"
        target = Path(custody) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            fd = None  # identical content already preserved (name carries the digest)
        if fd is not None:
            try:
                os.write(fd, raw)
                os.fsync(fd)
            finally:
                os.close(fd)
        evidence.append({"path": relative, "sha256": inventory_sha})
    observed: dict[str, Any] = {"head": head, "files": len(inventory), "inventory_sha256": inventory_sha}
    flags = []
    sealed_path = params.get("sealed_inventory")
    if not sealed_path:
        flags.append(
            _unmeasured(
                params, name, code="code.identity_unmeasured", family="CODE_IDENTITY",
                check="executed_inventory", missing_input="sealed_inventory",
                inventory_sha256=inventory_sha,
                detail="no sealed inventory given; the executed files were not compared",
            )
        )
    else:
        sealed, sealed_roots = _sealed_files(json.loads(Path(sealed_path).read_bytes()))
        in_scope = _window_scope(roots, sealed_roots, params)
        changed = sorted(p for p, sha in sealed.items() if p in inventory and inventory[p] != sha)
        missing = sorted(p for p in sealed if p not in inventory and in_scope(p))
        added = sorted(p for p in inventory if p not in sealed and in_scope(p))
        observed.update({"sealed_files": len(sealed),
                         "sealed_files_in_window_roots": sum(1 for p in sealed if in_scope(p)),
                         "changed": len(changed), "missing": len(missing), "added": len(added)})
        if changed or missing or added:
            flags.append(
                _flag(
                    params, name, code="code.executed_differs_from_sealed", family="CODE_IDENTITY",
                    klass="NUMBER",
                    observed={"check": "executed_inventory", "changed": changed[:_MAX_LISTED],
                              "missing": missing[:_MAX_LISTED], "added": added[:_MAX_LISTED]},
                    expected={"sealed_inventory": str(sealed_path)},
                    detail=(f"executed files differ from the sealed inventory: {len(changed)} changed, "
                            f"{len(missing)} missing, {len(added)} added"),
                    legacy_site="joulewise/arm_readiness.py:_r1_rederive_at_arm",
                    legacy_code="readiness_r1_dependency_manifest", evidence=evidence,
                )
            )
    sidecar = params.get("chain_sidecar")
    if bool(params.get("chain_path")) != bool(sidecar):
        flags.append(
            _unmeasured(
                params, name, code="code.identity_unmeasured", family="CODE_IDENTITY",
                check="chain_sidecar",
                missing_input="chain_sidecar" if params.get("chain_path") else "chain_path",
                detail="only one of the chain and its sidecar was given; the chain digest was not compared",
            )
        )
    if params.get("chain_path") and sidecar:
        chain_sha = _sha256_file(Path(params["chain_path"]))
        sidecar_text = Path(sidecar).read_text(encoding="utf-8", errors="replace").strip()
        pinned = sidecar_text.split()[0] if sidecar_text else ""
        observed.update({"chain_sha256": chain_sha, "chain_sidecar_sha256": pinned})
        if chain_sha != pinned:
            flags.append(
                _flag(
                    params, name, code="code.executed_differs_from_sealed", family="CODE_IDENTITY",
                    klass="NUMBER",
                    observed={"check": "chain_sidecar", "chain_sha256": chain_sha},
                    expected={"chain_sha256": pinned},
                    detail="chain bytes differ from their sidecar digest",
                    legacy_site="scripts/run_night.py:4022", legacy_code="night_chain_digest_mismatch",
                    evidence=evidence,
                )
            )
    return {"flags": flags, "observed": observed}


# --------------------------------------------------------------------------
# model identity
# --------------------------------------------------------------------------


RUNTIME_PACKAGES = (
    "mlx", "mlx-lm", "mlx-metal", "transformers", "tokenizers", "safetensors", "numpy",
)
RUNTIME_PROBE_TIMEOUT_S = 60.0
_RUNTIME_PROBE = (
    "import importlib.metadata as m, json, platform, sys\n"
    "out = {}\n"
    "for name in json.loads(sys.argv[1]):\n"
    "    try:\n"
    "        out[name] = m.version(name)\n"
    "    except m.PackageNotFoundError:\n"
    "        out[name] = None\n"
    "print(json.dumps({'python': platform.python_version(), 'packages': out}, sort_keys=True))\n"
)


def _artifact_digest(identity: Mapping[str, Any]) -> str | None:
    if identity.get("status") != "ok":
        return None
    return identity.get("sha256") or identity.get("folded_sha256")


def runtime_versions(python: str, packages: Sequence[str] = RUNTIME_PACKAGES,
                     timeout_s: float = RUNTIME_PROBE_TIMEOUT_S) -> dict[str, Any]:
    """Installed versions of the runtime packages, read from package metadata.

    Runs the measurement interpreter (``<repo>/.venv/bin/python`` by default)
    with ``importlib.metadata`` only: nothing is imported from MLX, no model
    is loaded and no machine state changes. Raises :class:`CollectorError`
    when the interpreter cannot answer.
    """

    try:
        completed = subprocess.run(
            [python, "-B", "-c", _RUNTIME_PROBE, json.dumps(list(packages))],
            capture_output=True, timeout=timeout_s, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise CollectorError(f"runtime probe with {python} could not run: {exc}") from exc
    if completed.returncode != 0:
        raise CollectorError(
            f"runtime probe with {python} exited {completed.returncode}: "
            + completed.stderr.decode("utf-8", "replace").strip()[-300:]
        )
    try:
        value = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CollectorError(f"runtime probe with {python} printed no JSON: {exc}") from exc
    return value


def runtime_versions_sha256(versions: Mapping[str, Any]) -> str:
    """The pin L6 seals: SHA-256 of the canonical JSON of :func:`runtime_versions`."""

    return hashlib.sha256(canonical_json_bytes(dict(versions))).hexdigest()


def recorded_download_revisions(source: str | None) -> list[str]:
    """Commit hashes the Hugging Face download recorded for a local model directory.

    ``huggingface_hub`` writes ``.cache/huggingface/download/<file>.metadata``
    whose first line is the commit the file was fetched at. An empty list
    means nothing was recorded (the artifact digest pin still governs).
    """

    if not source:
        return []
    directory = Path(source) / ".cache" / "huggingface" / "download"
    revisions: set[str] = set()
    try:
        entries = sorted(directory.rglob("*.metadata"))
    except OSError:
        return []
    for entry in entries:
        try:
            first = entry.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
        except OSError:
            continue
        if first and first[0].strip():
            revisions.add(first[0].strip())
    return sorted(revisions)


IDENTITY_PINS_SCHEMA = "joulewise.b5_identity_pins.v1"


def _is_sha256_hex(value: Any) -> bool:
    return (isinstance(value, str) and len(value) == 64
            and all(character in "0123456789abcdef" for character in value))


def read_identity_pins(path: str | Path | None) -> dict[str, Any]:
    """The sealed model and runtime pins: ``{"model_artifact_sha256": {unit: sha}, "runtime_versions_sha256": sha|None}``.

    The file (L6 seals it beside the flag catalog; the driver passes it with
    ``--identity-pins``, the harvest reads it as ``identity_pins.json``) is::

        {"schema": "joulewise.b5_identity_pins.v1",
         "units": {"<identity_unit_id>": {"model_artifact_sha256": "<hex>",
                                          "runtime_identity_sha256": "<hex>", ...}},
         "runtime_versions_sha256": "<hex>" | null}

    ``units`` feeds the arm collector's model artifact check and the harvest's
    per-bundle check; ``runtime_versions_sha256`` is the digest of
    :func:`runtime_versions`. No path gives no pins. A file that cannot be
    read or does not have this shape raises :class:`CollectorError`, which
    leaves ``model.identity_unmeasured``: the check did not run.
    """

    empty: dict[str, Any] = {"model_artifact_sha256": {}, "runtime_versions_sha256": None}
    if not path:
        return empty
    try:
        document = json.loads(Path(path).read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CollectorError(f"identity pins {path} cannot be read: {exc}") from exc
    units = document.get("units") if isinstance(document, Mapping) else None
    runtime = document.get("runtime_versions_sha256") if isinstance(document, Mapping) else None
    if (not isinstance(document, Mapping) or document.get("schema") != IDENTITY_PINS_SCHEMA
            or not isinstance(units, Mapping)
            or not all(isinstance(entry, Mapping) and _is_sha256_hex(entry.get("model_artifact_sha256"))
                       for entry in units.values())
            or not (runtime is None or _is_sha256_hex(runtime))):
        raise CollectorError(f"identity pins {path} are not a {IDENTITY_PINS_SCHEMA} document with "
                             "lowercase SHA-256 pins")
    return {"model_artifact_sha256": {str(unit): entry["model_artifact_sha256"] for unit, entry in units.items()},
            "runtime_versions_sha256": runtime}


def collect_model_identity(
    params: Mapping[str, Any],
    *,
    artifact_identity: Callable[[str], Mapping[str, Any]] | None = None,
    verify_frozen: Callable[..., Mapping[str, Any]] | None = None,
    probe_runtime: Callable[[str, Sequence[str]], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Model artifact, revision, tokenizer and runtime versions against their pins.

    Per identity unit: the model artifact digest
    (``provenance.model_artifact_identity``) against the frozen pin or
    ``expected_model_artifact_sha256[unit]`` or the sealed ``identity_pins_path``
    (:func:`read_identity_pins`); the declared ``model_revision``
    against each config's ``model.revision`` and the revision the download
    recorded; the tokenizer bytes against the configs' pins. Once per run:
    the runtime package versions of the measurement interpreter
    (``runtime_python``, default ``<repo>/.venv/bin/python``) against
    ``expected_runtime_versions_sha256``. A difference is
    ``model.identity_mismatch``; a missing pin is ``model.identity_unpinned``
    (excluding until L6 seals the pins); a check that could not run is
    ``model.identity_unmeasured``. When the projection is frozen and asked
    for, ``identity_pins.verify_frozen_projection`` also runs.

    ``artifact_identity``, ``verify_frozen`` and ``probe_runtime`` default to
    production code; tests inject fakes.
    """

    if artifact_identity is None:
        from joulewise.provenance import model_artifact_identity as artifact_identity
    if probe_runtime is None:
        probe_runtime = runtime_versions
    pack_root = Path(_require(params, "pack_root"))
    repo_root = Path(params["repo_root"]) if params.get("repo_root") else _repo_root_of(pack_root)
    name = "model_identity"
    tree = json.loads((pack_root / "plan_tree.json").read_bytes())
    projection = ((tree.get("arm_attachments") or {}).get("identity_pin_projection")) or {}
    units = projection.get("identity_units") or []
    # The sealed pins file (read_identity_pins); explicit parameters win over it.
    sealed = read_identity_pins(params.get("identity_pins_path"))
    expected_overrides = {**sealed["model_artifact_sha256"], **(params.get("expected_model_artifact_sha256") or {})}
    flags: list[dict[str, Any]] = []
    observed_units = []
    if not units:
        flags.append(
            _unmeasured(
                params, name, code="model.identity_unmeasured", family="MODEL_IDENTITY",
                check="identity_units", missing_input="identity_pin_projection.identity_units",
                detail="the plan tree lists no identity units; no model was checked",
            )
        )
    for unit in units:
        unit_id = unit.get("identity_unit_id")
        declared = unit.get("declared_identity") or {}
        source = declared.get("model_source")
        declared_revision = declared.get("model_revision")
        identity = artifact_identity(source)
        digest = _artifact_digest(identity)
        pinned = (unit.get("model_runtime_config") or {}).get("model_artifact_sha256") or expected_overrides.get(unit_id)
        unit_observed = {"identity_unit_id": unit_id, "model_source": source,
                         "model_artifact_sha256": digest, "pinned": pinned,
                         "declared_model_revision": declared_revision}
        if digest is None:
            flags.append(
                _flag(
                    params, name, code="model.identity_mismatch", family="MODEL_IDENTITY", klass="NUMBER",
                    observed={"check": "model_artifact", "unit": unit_id,
                              "reason": identity.get("reason")},
                    expected={"model_artifact_sha256": pinned},
                    detail=f"model artifact for unit {unit_id} is unavailable: {identity.get('reason')}",
                    legacy_site="joulewise/identity_pins.py:verify_frozen_projection",
                    legacy_code="readiness_identity_artifact_unreadable",
                )
            )
        elif pinned is None:
            flags.append(
                _flag(
                    params, name, code="model.identity_unpinned", family="MODEL_IDENTITY",
                    klass="NUMBER",
                    observed={"check": "model_artifact", "unit": unit_id, "model_artifact_sha256": digest},
                    expected={"model_artifact_sha256": "a sealed pin"},
                    detail=f"no frozen model artifact pin for unit {unit_id}; digest recorded",
                    legacy_site="joulewise/identity_pins.py:verify_frozen_projection",
                    legacy_code="readiness_identity_pinset_frozen_mismatch",
                )
            )
        elif digest != pinned:
            flags.append(
                _flag(
                    params, name, code="model.identity_mismatch", family="MODEL_IDENTITY", klass="NUMBER",
                    observed={"check": "model_artifact", "unit": unit_id, "model_artifact_sha256": digest},
                    expected={"model_artifact_sha256": pinned},
                    detail=f"model artifact for unit {unit_id} differs from its frozen pin",
                    legacy_site="joulewise/identity_pins.py:verify_frozen_projection",
                    legacy_code="readiness_identity_environment_dirty",
                )
            )
        # Declared revision against the recorded download commit.
        recorded = recorded_download_revisions(source)
        unit_observed["recorded_download_revisions"] = recorded
        if declared_revision and recorded and recorded != [declared_revision]:
            flags.append(
                _flag(
                    params, name, code="model.identity_mismatch", family="MODEL_IDENTITY", klass="NUMBER",
                    observed={"check": "model_revision_download", "unit": unit_id,
                              "recorded_download_revisions": recorded},
                    expected={"model_revision": declared_revision},
                    detail=f"model files for unit {unit_id} were downloaded at another revision",
                    legacy_site="joulewise/identity_pins.py:verify_frozen_projection",
                    legacy_code="readiness_identity_environment_dirty",
                )
            )
        # Tokenizer bytes and revision against the configs' pins.
        tokenizer_pins = set()
        config_revisions = set()
        for row in unit.get("config_inventory") or []:
            target = _resolve_pin_path(row["path"], pack_root, repo_root)
            try:
                config = json.loads(target.read_bytes())
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                continue  # pack_identity reports unreadable configs
            model = (config.get("model") or {}) if isinstance(config, Mapping) else {}
            pin = model.get("tokenizer_json_sha256")
            if pin:
                tokenizer_pins.add(pin)
            if "revision" in model:
                config_revisions.add(model.get("revision"))
        if declared_revision and config_revisions and config_revisions != {declared_revision}:
            flags.append(
                _flag(
                    params, name, code="model.identity_mismatch", family="MODEL_IDENTITY", klass="NUMBER",
                    observed={"check": "model_revision_config", "unit": unit_id,
                              "config_revisions": sorted(str(r) for r in config_revisions)},
                    expected={"model_revision": declared_revision},
                    detail=f"configs of unit {unit_id} name another model revision than declared",
                    legacy_site="joulewise/identity_pins.py:_derive_projection_units",
                    legacy_code="readiness_identity_environment_dirty",
                )
            )
        if tokenizer_pins and source:
            tokenizer_path = Path(source) / "tokenizer.json"
            try:
                tokenizer_sha = _sha256_file(tokenizer_path)
            except OSError:
                tokenizer_sha = None
            unit_observed["tokenizer_json_sha256"] = tokenizer_sha
            if tokenizer_sha is None or tokenizer_pins != {tokenizer_sha}:
                flags.append(
                    _flag(
                        params, name, code="model.identity_mismatch", family="MODEL_IDENTITY",
                        klass="NUMBER",
                        observed={"check": "tokenizer_json", "unit": unit_id,
                                  "tokenizer_json_sha256": tokenizer_sha},
                        expected={"tokenizer_json_sha256": sorted(tokenizer_pins)},
                        detail=f"tokenizer.json for unit {unit_id} differs from the config pins",
                        legacy_site="joulewise/identity_pins.py:_derive_projection_units",
                        legacy_code="readiness_identity_environment_dirty",
                    )
                )
        observed_units.append(unit_observed)
    observed: dict[str, Any] = {"units": observed_units, "projection_state": projection.get("state")}

    # Runtime versions of the measurement interpreter, recorded even when the
    # projection is unprojected (review 2026-10-05).
    python = params.get("runtime_python") or str(repo_root / ".venv" / "bin" / "python")
    packages = list(params.get("runtime_packages") or RUNTIME_PACKAGES)
    expected_runtime = params.get("expected_runtime_versions_sha256") or sealed["runtime_versions_sha256"]
    try:
        versions = dict(probe_runtime(python, packages))
    except CollectorError as exc:
        observed["runtime"] = {"python": python, "error": str(exc)}
        flags.append(
            _unmeasured(
                params, name, code="model.identity_unmeasured", family="MODEL_IDENTITY",
                check="runtime_versions", missing_input=None, python=python, error=str(exc)[:500],
                detail="the measurement interpreter's runtime versions could not be read",
            )
        )
    else:
        versions_sha = runtime_versions_sha256(versions)
        observed["runtime"] = {"python": python, "versions": versions, "versions_sha256": versions_sha}
        if not expected_runtime:
            flags.append(
                _flag(
                    params, name, code="model.identity_unpinned", family="MODEL_IDENTITY", klass="NUMBER",
                    observed={"check": "runtime_versions", "versions": versions,
                              "versions_sha256": versions_sha},
                    expected={"runtime_versions_sha256": "a sealed pin"},
                    detail="no sealed runtime-versions pin; versions recorded",
                    legacy_site="joulewise/identity_pins.py:verify_frozen_projection",
                    legacy_code="readiness_identity_pinset_frozen_mismatch",
                )
            )
        elif versions_sha != expected_runtime:
            flags.append(
                _flag(
                    params, name, code="model.identity_mismatch", family="MODEL_IDENTITY", klass="NUMBER",
                    observed={"check": "runtime_versions", "versions": versions,
                              "versions_sha256": versions_sha},
                    expected={"runtime_versions_sha256": expected_runtime},
                    detail="runtime package versions differ from the sealed pin",
                    legacy_site="joulewise/identity_pins.py:verify_frozen_projection",
                    legacy_code="readiness_identity_environment_dirty",
                )
            )

    if params.get("verify_frozen_projection"):
        if projection.get("state") != "frozen":
            observed["frozen_projection"] = "not_frozen"
        else:
            if verify_frozen is None:
                from joulewise.identity_pins import verify_frozen_projection as verify_frozen
            result = verify_frozen(pack_root, params["custody_root"], params["bracket_session_id"])
            observed["frozen_projection"] = {
                "status": result.get("status"),
                "reason_codes": list(result.get("reason_codes") or []),
                "receipt_sha256": result.get("receipt_sha256"),
            }
            if result.get("status") != "PASS":
                flags.append(
                    _flag(
                        params, name, code="model.identity_mismatch", family="MODEL_IDENTITY",
                        klass="NUMBER",
                        observed={"check": "frozen_projection",
                                  "reason_codes": list(result.get("reason_codes") or []),
                                  "identity_units": result.get("identity_units")},
                        expected={"status": "PASS"},
                        detail="live model/runtime/config identity differs from the frozen projection",
                        legacy_site="joulewise/identity_pins.py:verify_frozen_projection",
                        legacy_code=",".join(result.get("reason_codes") or []) or None,
                    )
                )
    return {"flags": flags, "observed": observed}


# --------------------------------------------------------------------------
# ledger readiness
# --------------------------------------------------------------------------


def collect_ledger_readiness(params: Mapping[str, Any]) -> dict[str, Any]:
    repo = Path(params["repo_root"])
    argv = params.get("argv")
    if not argv:
        argv = [sys.executable, "-B", str(repo / "scripts" / "recover_calibration_ledger.py")]
        if params.get("ledger_path"):
            argv += ["--ledger", str(params["ledger_path"])]
        if params.get("head_pin_path"):
            argv += ["--head-pin", str(params["head_pin_path"])]
        argv += ["readiness", "--phase", params.get("phase", "pre-reserve")]
        if params.get("calibration_plan"):
            argv += ["--plan", str(params["calibration_plan"])]
        if params.get("session_id"):
            argv += ["--session-id", str(params["session_id"])]
    timeout_s = float(params.get("tool_timeout_s", 90.0))
    try:
        completed = subprocess.run(
            list(argv), cwd=str(repo), capture_output=True, timeout=timeout_s, check=False
        )
    except subprocess.TimeoutExpired as exc:
        raise CollectorError(f"ledger readiness timed out after {timeout_s} s") from exc
    stdout = completed.stdout.decode("utf-8", "replace").strip()
    parsed: Any = None
    for line in reversed(stdout.splitlines()):
        try:
            parsed = json.loads(line)
            break
        except json.JSONDecodeError:
            continue
    refusal = None
    if isinstance(parsed, Mapping):
        refusal = parsed.get("refusal_code") or parsed.get("code") or (
            (parsed.get("readiness") or {}).get("refusal_code") if isinstance(parsed.get("readiness"), Mapping) else None
        )
    observed = {"returncode": completed.returncode, "status": (parsed or {}).get("status")
                if isinstance(parsed, Mapping) else None, "refusal_code": refusal}
    flags = []
    if completed.returncode != 0:
        flags.append(
            _flag(
                params, "ledger_readiness", code="calibration.ledger_not_ready", family="CALIBRATION",
                klass="REPRESENTATION",
                observed={"check": "ledger_readiness", "returncode": completed.returncode,
                          "refusal_code": refusal},
                expected={"returncode": 0, "status": "ready"},
                detail=f"calibration ledger readiness refused: {refusal or 'nonzero exit'}",
                legacy_site="docs/phase_2/window_runbook.md:1367",
                legacy_code=str(refusal) if refusal else None,
            )
        )
    return {"flags": flags, "observed": observed}


COLLECTORS: Mapping[str, Callable[[Mapping[str, Any]], dict[str, Any]]] = {
    "pack_identity": collect_pack_identity,
    "checkout_identity": collect_checkout_identity,
    "executed_code": collect_executed_code,
    "model_identity": collect_model_identity,
    "ledger_readiness": collect_ledger_readiness,
}


# --------------------------------------------------------------------------
# subprocess runner
# --------------------------------------------------------------------------


@dataclass
class CollectorOutcome:
    name: str
    status: str  # ok | error | timeout
    elapsed_s: float
    flags: list[dict[str, Any]] = field(default_factory=list)
    observed: Any = None
    error: str | None = None

    def as_record(self, written: int | None = None) -> dict[str, Any]:
        return {
            "collector": self.name,
            "status": self.status,
            "elapsed_s": round(self.elapsed_s, 3),
            "flags_emitted": len(self.flags),
            "flags_written": written,
            "error": self.error,
            "observed": self.observed,
        }


def _package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_collector(
    name: str,
    params: Mapping[str, Any],
    *,
    timeout_s: float | None = None,
    python: str | None = None,
    module: str = "joulewise.flags.collect",
) -> CollectorOutcome:
    """Run one collector in a fresh process group; never raises on collector failure."""

    timeout = float(timeout_s if timeout_s is not None else DEFAULT_TIMEOUTS_S.get(name, DEFAULT_TIMEOUT_S))
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(_package_root())] + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
    )
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.monotonic()
    try:
        payload = json.dumps({"name": name, "params": dict(params)}, sort_keys=True).encode("utf-8")
    except (TypeError, ValueError) as exc:
        return CollectorOutcome(name, "error", 0.0, error=f"params are not JSON: {exc}")
    try:
        process = subprocess.Popen(
            [python or sys.executable, "-B", "-m", module, "--run-collector"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            start_new_session=True,
        )
    except OSError as exc:
        return CollectorOutcome(name, "error", time.monotonic() - started, error=f"spawn failed: {exc}")
    try:
        stdout, stderr = process.communicate(payload, timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        process.communicate()
        return CollectorOutcome(
            name, "timeout", time.monotonic() - started, error=f"timed out after {timeout} s"
        )
    elapsed = time.monotonic() - started
    try:
        result = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        tail = stderr.decode("utf-8", "replace").strip().splitlines()[-3:]
        return CollectorOutcome(
            name, "error", elapsed,
            error=f"exit {process.returncode}, no result: {' | '.join(tail)}"[:2000],
        )
    if not isinstance(result, Mapping) or result.get("ok") is not True:
        error = result.get("error") if isinstance(result, Mapping) else "malformed result"
        return CollectorOutcome(name, "error", elapsed, error=str(error)[:2000])
    flags = []
    bad = []
    for flag in result.get("flags") or []:
        problems = validate_flag(flag)
        if problems:
            bad.append("; ".join(problems))
        else:
            flags.append(flag)
    if bad:
        return CollectorOutcome(
            name, "error", elapsed, flags=flags, observed=result.get("observed"),
            error=f"{len(bad)} malformed flag(s): {bad[0]}"[:2000],
        )
    return CollectorOutcome(name, "ok", elapsed, flags=flags, observed=result.get("observed"))


# The flag a collector that did not finish leaves behind. The identity
# collectors' checks are NUMBER: unverified identity excludes the window.
# Ledger readiness is disclosed anyway. A collector this table does not know
# gets "collector.unmeasured", which is never classified and blocks release.
UNMEASURED_BY_COLLECTOR: Mapping[str, tuple[str, str, str]] = {
    "pack_identity": ("pack.identity_unmeasured", "PACK_IDENTITY", "NUMBER"),
    "checkout_identity": ("code.identity_unmeasured", "CODE_IDENTITY", "NUMBER"),
    "executed_code": ("code.identity_unmeasured", "CODE_IDENTITY", "NUMBER"),
    "model_identity": ("model.identity_unmeasured", "MODEL_IDENTITY", "NUMBER"),
    "ledger_readiness": ("calibration.ledger_readiness_unmeasured", "CALIBRATION", "REPRESENTATION"),
}
UNKNOWN_COLLECTOR_UNMEASURED = ("collector.unmeasured", "DIAGNOSTIC", "REPRESENTATION")


def collector_unmeasured_flag(outcome: "CollectorOutcome", params: Mapping[str, Any]) -> dict[str, Any]:
    """The flag recording that ``outcome``'s checks did not (all) run."""

    code, family, klass = UNMEASURED_BY_COLLECTOR.get(outcome.name, UNKNOWN_COLLECTOR_UNMEASURED)
    return make_flag(
        code=code,
        family=family,
        klass=klass,
        scope=_context_scope(params),
        source=make_source(params.get("stage", "desk"), "joulewise.flags.collect.run_collectors"),
        observed={"check": "collector_run", "collector": outcome.name, "status": outcome.status,
                  "error": (outcome.error or "")[:500]},
        expected={"status": "ok"},
        detail=f"collector {outcome.name} did not finish ({outcome.status}): {outcome.error}",
        interval=make_interval(),
        catalog_sha256=params.get("catalog_sha256"),
    )


def run_collectors(
    specs: Sequence[tuple[str, Mapping[str, Any]]],
    *,
    stage: str,
    sink: Any,
    runs_log: Path | str | None = None,
    timeout_s: Mapping[str, float] | None = None,
    python: str | None = None,
    module: str = "joulewise.flags.collect",
) -> list[CollectorOutcome]:
    """Run each collector; write its flags to ``sink``; log one run record. Never raises.

    A collector that errs or times out (or whose flags could not all be
    written) also leaves a flag (:func:`collector_unmeasured_flag`), so an
    unverified identity reaches the exclusion function instead of only the
    run log.
    """

    from joulewise.flags.sink import append_json_line

    started = now_stamp()
    outcomes = []
    records = []
    for name, params in specs:
        merged = {**dict(params), "stage": stage}
        budget = (timeout_s or {}).get(name)
        if budget is None and stage == "arm":
            budget = ARM_TIMEOUTS_S.get(name)
        outcome = run_collector(name, merged, timeout_s=budget, python=python, module=module)
        written = 0
        for flag in outcome.flags:
            try:
                written += 1 if sink.append(flag) else 0
            except (OSError, FlagSchemaError) as exc:
                outcome.status = "error"
                outcome.error = f"sink write failed: {exc}"
                break
        if outcome.status != "ok":
            try:
                unmeasured = collector_unmeasured_flag(outcome, merged)
                outcome.flags.append(unmeasured)
                written += 1 if sink.append(unmeasured) else 0
            except (OSError, FlagSchemaError, TypeError, ValueError):
                pass  # the run record below still carries the error
        outcomes.append(outcome)
        records.append(outcome.as_record(written))
    if runs_log is not None:
        record = {
            "schema_version": COLLECTOR_RUN_SCHEMA,
            "stage": stage,
            "started": started,
            "finished": now_stamp(),
            "collectors": records,
            "collector_errors": [
                {"collector": r["collector"], "error": r["error"], "elapsed_s": r["elapsed_s"]}
                for r in records if r["status"] != "ok"
            ],
        }
        try:
            append_json_line(runs_log, record)
        except OSError:
            pass  # record-only: a log failure never stops anything
    return outcomes


def _child_main() -> int:
    """Subprocess entry: read ``{name, params}`` on stdin, print one JSON result."""

    try:
        request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        collector = COLLECTORS[request["name"]]
        result = collector(request["params"])
        output = {"ok": True, "flags": result.get("flags", []), "observed": result.get("observed")}
    except Exception as exc:  # noqa: BLE001 - every failure is a collector error entry
        output = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    sys.stdout.write(json.dumps(output, sort_keys=True, allow_nan=False))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through run_collector
    if sys.argv[1:] == ["--run-collector"]:
        raise SystemExit(_child_main())
    raise SystemExit("usage: python -m joulewise.flags.collect --run-collector < request.json")
