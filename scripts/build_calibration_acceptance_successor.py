#!/usr/bin/env python3
"""Build and optionally publish one deterministic D-102 successor artifact.

Dry-run is the default. Issuance creates one commit containing the immutable
artifact and registry transition, atomically advances HEAD, and verifies the
successor through committed-mode loading. It never writes the ledger head pin.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_bracketing import (  # noqa: E402
    ACCEPTANCE_IDENTITY_FIELDS,
    ACCEPTANCE_REGISTRY_SCHEMA,
    ACCEPTANCE_REGISTRY_AUTHORITY,
    ACCEPTANCE_SUCCESSOR_SCHEMA,
    DEFAULT_ACCEPTANCE_REGISTRY_PATH,
    SUCCESSOR_CORPUS_SELECTION,
    SUCCESSOR_COUNT_BOUNDARY_RULE,
    SUCCESSOR_DECISION_IDS,
    SUCCESSOR_MINIMUM_CORPUS_SIZE,
    SUCCESSOR_PUBLICATION_POLICY,
    SUCCESSOR_QUANTILE_METHOD,
    _active_registry_entry,
    _artifact_count_boundary,
    _canonical_sha256,
    _group_probe_observations,
    _governed_noncontent_rows,
    _git_head_bytes,
    _observation_custody_authentic,
    _probe_observation_universe,
    _valid_acceptance_bound,
    _valid_registry,
    derive_successor_decimal_derivation,
    load_calibration_acceptance_registry,
    probe_calibration_acceptance_trigger,
)
from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    LEDGER_SCHEMA,
    CalibrationLedgerSnapshot,
    LedgerObservation,
    load_calibration_ledger_snapshot,
)
from joulewise.powermetrics_fiducial import PROTOCOL_ID, protocol_sha256  # noqa: E402


BUILD_OUTPUT_SCHEMA = "joulewise.calibration_acceptance_successor_build.v1"
CONTENT_IDENTITY_METHOD = (
    "sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))"
)


@dataclass(frozen=True)
class SuccessorBuild:
    artifact: Mapping[str, Any]
    artifact_bytes: bytes
    artifact_sha256: str
    registry: Mapping[str, Any]
    registry_bytes: bytes
    registry_sha256: str
    artifact_path: str
    head_pin: Mapping[str, Any]
    parent_probe: Mapping[str, Any]
    successor_probe: Mapping[str, Any]

    def output_record(self) -> dict[str, Any]:
        return {
            "schema_version": BUILD_OUTPUT_SCHEMA,
            "publication_policy": SUCCESSOR_PUBLICATION_POLICY,
            "artifact_path": self.artifact_path,
            "artifact_sha256": self.artifact_sha256,
            "derivation_sha256": self.artifact["derivation_sha256"],
            "artifact_file_content": self.artifact_bytes.decode("utf-8"),
            "registry_sha256": self.registry_sha256,
            "registry_file_content": self.registry_bytes.decode("utf-8"),
            "proposed_registry_entry": next(
                entry
                for entry in self.registry["entries"]
                if entry["active"] is True
            ),
            "proposed_head_pin": dict(self.head_pin),
            "parent_probe": dict(self.parent_probe),
            "successor_probe": dict(self.successor_probe),
        }


class SuccessorDurabilityUncertain(RuntimeError):
    """The authority commit landed, but post-commit verification failed."""


def _pretty_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            dict(value),
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def _epoch_id(epoch: Mapping[str, Any], active: Mapping[str, Any]) -> str:
    if dict(epoch) == dict(active):
        return "active_epoch"
    raw = json.dumps(
        dict(epoch),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return f"epoch_{hashlib.sha256(raw).hexdigest()[:16]}"


def _attempt_row(observation: LedgerObservation) -> dict[str, Any]:
    return {
        "attempt_id": observation.attempt_id,
        "finalization_sequence": observation.sequence,
        "receipt_digest": observation.receipt_digest,
        "observation_kind": observation.observation_kind,
        "custody_locator": observation.custody_locator,
        "exact_bound_lexeme_s": observation.exact_bound_lexeme_s,
        "manifest_sha256": observation.artifact_sha256.get("manifest.json"),
        "instrument_evidence_sha256": observation.artifact_sha256.get(
            "instrument_evidence.json"
        ),
    }


def _load_parent_artifact(
    registry: Mapping[str, Any], repo_root: Path
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    active = _active_registry_entry(registry)
    if active is None:
        raise ValueError("acceptance registry does not have one active entry")
    path = repo_root / str(active["artifact_path"])
    try:
        raw = path.read_bytes()
        artifact = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("active acceptance artifact is unreadable") from exc
    if (
        hashlib.sha256(raw).hexdigest() != active["artifact_sha256"]
        or not _valid_acceptance_bound(artifact)
    ):
        raise ValueError("active acceptance artifact is not registry-authenticated")
    return active, artifact


def _assert_terminal_committed_snapshot(snapshot: CalibrationLedgerSnapshot) -> None:
    if (
        not snapshot.valid
        or snapshot.head_sequence < 1
        or snapshot.head_sequence != len(snapshot.receipts)
        or snapshot.committed_head_sequence != snapshot.head_sequence
        or snapshot.committed_head_digest != snapshot.head_digest
        or snapshot.receipts[-1].get("receipt_digest") != snapshot.head_digest
        or snapshot.receipts[-1].get("event")
        in {"reservation", "bracket-session-open", "bracket-session-slot-claim"}
    ):
        raise ValueError("successor issuance requires a committed terminal ledger head")


def _probe_proposed_successor(
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    observed_identity_epoch: Mapping[str, Any],
    proposed_registry: Mapping[str, Any],
    artifact_path: str,
    artifact_bytes: bytes,
    repo_root: Path,
    verify_custody: bool,
) -> dict[str, Any]:
    """Run the production probe against an isolated copy of proposed bytes."""

    with tempfile.TemporaryDirectory(prefix="joulewise-successor-probe-") as tmp:
        probe_root = Path(tmp)
        for entry in proposed_registry["entries"]:
            relative = str(entry["artifact_path"])
            destination = probe_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            payload = (
                artifact_bytes
                if relative == artifact_path
                else (repo_root / relative).read_bytes()
            )
            destination.write_bytes(payload)
        registry_path = (
            probe_root
            / "configs"
            / "calibration"
            / "calibration_acceptance_registry.json"
        )
        registry_path.write_bytes(_pretty_json_bytes(proposed_registry))
        result = probe_calibration_acceptance_trigger(
            ledger_snapshot,
            observed_identity_epoch=observed_identity_epoch,
            registry_path=registry_path,
            repo_root=probe_root,
            require_committed_registry=False,
            verify_custody=verify_custody,
        )
    if result.get("outcome") != "accepted_under_active_artifact":
        reasons = ",".join(result.get("refusal_reasons", ()))
        raise ValueError(
            f"successor_real_probe_refused:{result.get('outcome')}:{reasons}"
        )
    return result


def build_calibration_acceptance_successor(
    ledger_snapshot: CalibrationLedgerSnapshot,
    *,
    observed_identity_epoch: Mapping[str, Any],
    registry_path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
    repo_root: Path = REPO_ROOT,
    require_committed_registry: bool = True,
    verify_custody: bool = True,
) -> SuccessorBuild:
    """Build deterministic artifact and registry buffers without writing."""

    repo_root = Path(repo_root).resolve()
    registry_path = Path(registry_path).resolve(strict=False)
    _assert_terminal_committed_snapshot(ledger_snapshot)
    registry = load_calibration_acceptance_registry(
        registry_path,
        repo_root=repo_root,
        require_committed=require_committed_registry,
    )
    if registry is None:
        raise ValueError("acceptance registry is invalid or uncommitted")
    parent_entry, parent = _load_parent_artifact(registry, repo_root)
    parent_probe = probe_calibration_acceptance_trigger(
        ledger_snapshot,
        observed_identity_epoch=observed_identity_epoch,
        registry_path=registry_path,
        repo_root=repo_root,
        require_committed_registry=require_committed_registry,
        verify_custody=verify_custody,
    )
    if parent_probe["outcome"] != "successor_required":
        refusal_reasons = ",".join(parent_probe.get("refusal_reasons", ()))
        raise ValueError(
            "active artifact does not require a successor: "
            f"{parent_probe['outcome']}:{refusal_reasons}"
        )

    grouped_result = _group_probe_observations(
        _probe_observation_universe(ledger_snapshot)
    )
    if grouped_result is None:
        raise ValueError("content identity has conflicting classifications or bytes")
    grouped, noncontent = grouped_result
    noncontent_rows = _governed_noncontent_rows(
        noncontent, ledger_snapshot, ledger_snapshot.head_sequence
    )
    active_epoch = dict(parent["identity_epoch"])
    if dict(observed_identity_epoch) != active_epoch:
        raise ValueError("observed identity epoch differs from the parent artifact")

    epoch_values: dict[str, dict[str, Any]] = {"active_epoch": active_epoch}
    prior_rows: list[dict[str, Any]] = []
    corpus_members: list[dict[str, Any]] = []
    parent_new_ids = set(parent_probe["new_content_ids"])
    parent_prior_ids = {
        row["content_id"]
        for row in parent["prior_observation_set"]["observations"]
    }
    if set(grouped) - parent_prior_ids != parent_new_ids:
        raise ValueError("successor_parent_judgment_content_set_mismatch")
    for content_id, aliases in grouped.items():
        representative = aliases[0]
        epoch_id = _epoch_id(representative.identity_epoch, active_epoch)
        epoch_values.setdefault(epoch_id, dict(representative.identity_epoch))
        prior_rows.append(
            {
                "content_id": content_id,
                "epoch_id": epoch_id,
                "disposition": representative.classification_disposition,
                "representative_attempt_id": representative.attempt_id,
                "attempts": [_attempt_row(alias) for alias in aliases],
            }
        )
        if (
            representative.classification_disposition != "valid"
            or epoch_id != "active_epoch"
        ):
            continue
        # COLD-GATE-Q11: conservative default. A trigger observation enters
        # the corpus only after the real parent probe has dispositioned it
        # under the prior artifact (D-109 R2.6). This isolated predicate is
        # the flippable site for the re-convened conjunct-scope ruling.
        if content_id in parent_new_ids and parent_probe["outcome"] != "successor_required":
            raise ValueError("successor_trigger_lacks_parent_disposition")
        if verify_custody and any(
            not _observation_custody_authentic(alias) for alias in aliases
        ):
            raise ValueError("selected corpus member fails custody reauthentication")
        bound = representative.exact_bound_lexeme_s
        if not isinstance(bound, str):
            raise ValueError("selected corpus member lacks an exact bound lexeme")
        corpus_members.append(
            {
                "content_id": content_id,
                "attempt_id": representative.attempt_id,
                "finalization_sequence": representative.sequence,
                "receipt_digest": representative.receipt_digest,
                "custody_locator": representative.custody_locator,
                "b_fiducial_s": bound,
                "manifest_sha256": representative.artifact_sha256.get(
                    "manifest.json"
                ),
                "instrument_evidence_sha256": representative.artifact_sha256.get(
                    "instrument_evidence.json"
                ),
            }
        )
    prior_rows.sort(key=lambda row: row["content_id"])
    corpus_members.sort(key=lambda member: member["content_id"])
    if len(corpus_members) < SUCCESSOR_MINIMUM_CORPUS_SIZE:
        raise ValueError("successor_corpus_below_pending_q13_minimum_19")

    derivation = derive_successor_decimal_derivation(corpus_members)
    parent_boundary = _artifact_count_boundary(parent)
    count = len(corpus_members)
    next_boundary = parent_boundary if count < parent_boundary else 2 * count
    cutoff_core = {
        "sequence": ledger_snapshot.head_sequence,
        "head_digest": ledger_snapshot.head_digest,
        "ledger_schema": LEDGER_SCHEMA,
    }
    acceptance_id = (
        f"d079_calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
        f"{ledger_snapshot.head_digest[:16]}"
    )
    artifact_path = (
        "configs/calibration/"
        f"calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
        f"{ledger_snapshot.head_digest[:16]}.json"
    )
    root_acceptance_id = (
        parent["lineage"]["root_acceptance_id"]
        if parent.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA
        else parent["acceptance_id"]
    )
    parent_cutoff = {
        key: parent["ledger_cutoff"][key]
        for key in ("sequence", "head_digest", "ledger_schema")
    }
    artifact: dict[str, Any] = {
        "schema_version": ACCEPTANCE_SUCCESSOR_SCHEMA,
        "acceptance_id": acceptance_id,
        "decision_ids": list(SUCCESSOR_DECISION_IDS),
        "artifact_role": "issued",
        "issuance": {
            "status": "issued",
            "claim_eligible": True,
            "reason": (
                "authenticated live-prefix trigger judged under the parent "
                "artifact and rederived under D-102/D-109/D-117"
            ),
        },
        "lineage": {
            "generation": int(parent_entry["generation"]) + 1,
            "root_acceptance_id": root_acceptance_id,
            "parent_acceptance_id": parent["acceptance_id"],
            "parent_artifact_sha256": parent_entry["artifact_sha256"],
            "parent_derivation_sha256": parent["derivation_sha256"],
            "parent_ledger_cutoff": parent_cutoff,
            "trigger_judgment": {
                "judged_under_acceptance_id": parent["acceptance_id"],
                "judged_under_artifact_sha256": parent_entry["artifact_sha256"],
                "result": "successor_required",
                "new_content_ids": list(parent_probe["new_content_ids"]),
                "triggers": list(parent_probe["observed_triggers"]),
            },
        },
        "ledger_cutoff": {**cutoff_core, "role": "issued_acceptance_baseline"},
        "identity_epoch": active_epoch,
        "prospective_rederivation": {
            "calendar_expiry": None,
            "trigger_observation_rule": "judge_under_prior_artifact_never_self_fit",
            "triggers": [
                "identity_field_change",
                "protocol_or_estimator_byte_change",
                "new_valid_same_identity_capture_expands_observed_range",
                "content_distinct_valid_same_epoch_count_boundary",
                "new_systematic_failure_challenges_preflight_screen",
            ],
            "protocol_sha256": protocol_sha256(PROTOCOL_ID),
            "estimator_code_sha256": parent["prospective_rederivation"][
                "estimator_code_sha256"
            ],
            "count_trigger": {
                "source_corpus_count": count,
                "next_boundary": next_boundary,
                "rule": SUCCESSOR_COUNT_BOUNDARY_RULE,
            },
        },
        "derivation_corpus": {
            "selection": SUCCESSOR_CORPUS_SELECTION,
            "n": count,
            "members": corpus_members,
        },
        "prior_observation_set": {
            "cutoff": cutoff_core,
            "content_identity_method": CONTENT_IDENTITY_METHOD,
            "epoch_catalog": dict(sorted(epoch_values.items())),
            "observations": prior_rows,
            "noncontent_attempts": noncontent_rows,
        },
        "decimal_derivation": derivation,
    }
    artifact["derivation_sha256"] = _canonical_sha256(artifact)
    if not _valid_acceptance_bound(artifact):
        raise ValueError("constructed successor fails the production loader")
    artifact_bytes = _pretty_json_bytes(artifact)
    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()

    registry_entries = []
    for entry in registry["entries"]:
        registry_entries.append({**entry, "active": False})
    registry_entries.append(
        {
            "acceptance_id": acceptance_id,
            "artifact_path": artifact_path,
            "artifact_sha256": artifact_sha256,
            "derivation_sha256": artifact["derivation_sha256"],
            "artifact_schema": ACCEPTANCE_SUCCESSOR_SCHEMA,
            "generation": int(parent_entry["generation"]) + 1,
            "active": True,
            "parent_acceptance_id": parent["acceptance_id"],
            "parent_artifact_sha256": parent_entry["artifact_sha256"],
            "count_boundary_rule": SUCCESSOR_COUNT_BOUNDARY_RULE,
            "ledger_cutoff": cutoff_core,
        }
    )
    proposed_registry = {
        "schema_version": ACCEPTANCE_REGISTRY_SCHEMA,
        "authority": ACCEPTANCE_REGISTRY_AUTHORITY,
        "entries": registry_entries,
    }
    if not _valid_registry(proposed_registry):
        raise ValueError("constructed registry fails ancestry validation")
    registry_bytes = _pretty_json_bytes(proposed_registry)

    successor_probe = _probe_proposed_successor(
        ledger_snapshot,
        observed_identity_epoch=observed_identity_epoch,
        proposed_registry=proposed_registry,
        artifact_path=artifact_path,
        artifact_bytes=artifact_bytes,
        repo_root=repo_root,
        verify_custody=verify_custody,
    )
    return SuccessorBuild(
        artifact=artifact,
        artifact_bytes=artifact_bytes,
        artifact_sha256=artifact_sha256,
        registry=proposed_registry,
        registry_bytes=registry_bytes,
        registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
        artifact_path=artifact_path,
        head_pin=cutoff_core,
        parent_probe=parent_probe,
        successor_probe=successor_probe,
    )


def _stage_bytes(destination: Path, payload: bytes) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".stage", dir=destination.parent
    )
    staged = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        staged.unlink(missing_ok=True)
        raise
    return staged


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def publish_successor(
    build: SuccessorBuild,
    *,
    artifact_destination: Path,
    registry_destination: Path,
    expected_registry_bytes: bytes,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Co-land artifact and registry in one commit and verify committed mode."""

    repo_root = Path(repo_root).resolve()
    artifact_destination = Path(artifact_destination)
    registry_destination = Path(registry_destination)
    expected_artifact = repo_root / build.artifact_path
    expected_registry = (
        repo_root / "configs/calibration/calibration_acceptance_registry.json"
    )
    if (
        artifact_destination.resolve(strict=False)
        != expected_artifact.resolve(strict=False)
        or registry_destination.resolve(strict=False)
        != expected_registry.resolve(strict=False)
        or artifact_destination.is_symlink()
        or registry_destination.is_symlink()
    ):
        raise ValueError("issuance destinations changed or are substituted")
    artifact_destination = artifact_destination.resolve(strict=False)
    registry_destination = registry_destination.resolve(strict=False)
    try:
        registry_stat = registry_destination.stat()
    except OSError as exc:
        raise ValueError("registry destination is absent") from exc
    if not stat.S_ISREG(registry_stat.st_mode) or registry_stat.st_nlink != 1:
        raise ValueError("registry destination is not one regular unaliased file")
    try:
        top_level = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        old_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        git_lock_name = subprocess.run(
            ["git", "rev-parse", "--git-path", "joulewise-successor-publish.lock"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("successor_publication_git_repository_invalid") from exc
    if Path(top_level).resolve() != repo_root:
        raise ValueError("successor_publication_repo_root_mismatch")
    lock_path = Path(git_lock_name)
    if not lock_path.is_absolute():
        lock_path = repo_root / lock_path
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    try:
        lock_descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise ValueError("registry lock is unavailable or substituted") from exc
    try:
        lock_stat = os.fstat(lock_descriptor)
        if not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_nlink != 1:
            raise ValueError("registry lock is not one regular unaliased file")
        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
        artifact_relative = artifact_destination.relative_to(repo_root).as_posix()
        registry_relative = registry_destination.relative_to(repo_root).as_posix()
        if _git_head_bytes(registry_destination, repo_root) != expected_registry_bytes:
            raise ValueError("acceptance_registry_expected_parent_commit_mismatch")
        if _git_head_bytes(artifact_destination, repo_root) is not None:
            raise ValueError("successor_artifact_already_committed_without_registry")
        initial_registry_bytes = registry_destination.read_bytes()
        if initial_registry_bytes not in {
            expected_registry_bytes,
            build.registry_bytes,
        }:
            raise ValueError("registry changed since the successor was built")
        artifact_already_published = artifact_destination.exists()
        if (
            artifact_already_published
            and artifact_destination.read_bytes() != build.artifact_bytes
        ):
            raise ValueError("immutable successor artifact path is occupied")
        try:
            staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "-z"],
                cwd=repo_root,
                check=True,
                capture_output=True,
            ).stdout
            tracked_dirty = subprocess.run(
                ["git", "diff", "--name-only", "-z"],
                cwd=repo_root,
                check=True,
                capture_output=True,
            ).stdout
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard", "-z"],
                cwd=repo_root,
                check=True,
                capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ValueError("successor_publication_git_preflight_failed") from exc

        def names(raw: bytes) -> set[str]:
            return {
                item.decode("utf-8")
                for item in raw.split(b"\0")
                if item
            }

        if names(staged):
            raise ValueError("successor_publication_index_not_clean")
        if names(tracked_dirty) - {registry_relative}:
            raise ValueError("successor_publication_worktree_not_clean")
        if names(untracked) - {artifact_relative}:
            raise ValueError("successor_publication_untracked_paths_present")
        artifact_stage = (
            None
            if artifact_already_published
            else _stage_bytes(artifact_destination, build.artifact_bytes)
        )
        registry_stage = _stage_bytes(registry_destination, build.registry_bytes)
        ref_advanced = False
        try:
            if artifact_stage is not None:
                os.replace(artifact_stage, artifact_destination)
                _fsync_directory(artifact_destination.parent)
            os.replace(registry_stage, registry_destination)
            _fsync_directory(registry_destination.parent)

            index_descriptor, index_name = tempfile.mkstemp(
                prefix="joulewise-successor-index-"
            )
            os.close(index_descriptor)
            index_path = Path(index_name)
            index_path.unlink()
            index_environment = dict(os.environ)
            index_environment["GIT_INDEX_FILE"] = str(index_path)
            try:
                subprocess.run(
                    ["git", "read-tree", old_head],
                    cwd=repo_root,
                    env=index_environment,
                    check=True,
                    capture_output=True,
                )
                subprocess.run(
                    ["git", "add", "--", artifact_relative, registry_relative],
                    cwd=repo_root,
                    env=index_environment,
                    check=True,
                    capture_output=True,
                )
                committed_paths_raw = subprocess.run(
                    ["git", "diff", "--cached", "--name-only", "-z", old_head],
                    cwd=repo_root,
                    env=index_environment,
                    check=True,
                    capture_output=True,
                ).stdout
                if names(committed_paths_raw) != {
                    artifact_relative,
                    registry_relative,
                }:
                    raise ValueError("successor_publication_commit_pathset_invalid")
                tree = subprocess.run(
                    ["git", "write-tree"],
                    cwd=repo_root,
                    env=index_environment,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                commit_message = (
                    "Issue calibration acceptance successor "
                    f"{build.artifact['acceptance_id']}"
                )
                commit = subprocess.run(
                    ["git", "commit-tree", tree, "-p", old_head, "-m", commit_message],
                    cwd=repo_root,
                    env=index_environment,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            except (OSError, subprocess.CalledProcessError) as exc:
                raise ValueError("successor_publication_commit_creation_failed") from exc
            finally:
                index_path.unlink(missing_ok=True)

            try:
                committed_paths = names(
                    subprocess.run(
                        [
                            "git",
                            "diff-tree",
                            "--no-commit-id",
                            "--name-only",
                            "-r",
                            "-z",
                            commit,
                        ],
                        cwd=repo_root,
                        check=True,
                        capture_output=True,
                    ).stdout
                )
            except (OSError, subprocess.CalledProcessError) as exc:
                raise ValueError(
                    "successor_publication_commit_inspection_failed"
                ) from exc
            if committed_paths != {artifact_relative, registry_relative}:
                raise ValueError("successor_publication_commit_pathset_invalid")
            try:
                subprocess.run(
                    ["git", "update-ref", "HEAD", commit, old_head],
                    cwd=repo_root,
                    check=True,
                    capture_output=True,
                )
            except (OSError, subprocess.CalledProcessError) as exc:
                raise ValueError("successor_publication_head_update_failed") from exc
            ref_advanced = True

            try:
                loaded = load_calibration_acceptance_registry(
                    registry_destination,
                    repo_root=repo_root,
                    require_committed=True,
                )
                active = _active_registry_entry(loaded)
            except (OSError, TypeError, ValueError) as exc:
                raise SuccessorDurabilityUncertain(
                    "successor_post_commit_selection_verification_failed"
                ) from exc
            if (
                active is None
                or active.get("acceptance_id") != build.artifact["acceptance_id"]
                or _git_head_bytes(artifact_destination, repo_root)
                != build.artifact_bytes
            ):
                raise SuccessorDurabilityUncertain(
                    "successor_post_commit_selection_verification_failed"
                )
            return {
                "policy": SUCCESSOR_PUBLICATION_POLICY,
                "commit": commit,
                "committed_paths": sorted(committed_paths),
                "committed_mode_active_acceptance_id": active["acceptance_id"],
                "committed_mode_verified": True,
            }
        except BaseException:
            if not ref_advanced:
                registry_destination.write_bytes(initial_registry_bytes)
                if not artifact_already_published:
                    artifact_destination.unlink(missing_ok=True)
            raise
        finally:
            if artifact_stage is not None:
                artifact_stage.unlink(missing_ok=True)
            registry_stage.unlink(missing_ok=True)
    finally:
        os.close(lock_descriptor)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    parser.add_argument(
        "--registry", type=Path, default=DEFAULT_ACCEPTANCE_REGISTRY_PATH
    )
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--observed-identity", type=Path, required=True)
    parser.add_argument("--issue", action="store_true")
    parser.add_argument("--artifact-out", type=Path)
    parser.add_argument("--registry-out", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        registry_raw = args.registry.read_bytes()
        registry = load_calibration_acceptance_registry(
            args.registry,
            repo_root=args.repo_root,
            require_committed=True,
        )
        if registry is None:
            raise ValueError("registry is not committed or authenticated")
        _, parent = _load_parent_artifact(registry, Path(args.repo_root).resolve())
        cutoff = parent["ledger_cutoff"]
        snapshot = load_calibration_ledger_snapshot(
            args.ledger,
            args.head_pin,
            baseline_sequence=cutoff["sequence"],
            baseline_digest=cutoff["head_digest"],
            require_committed_pin=True,
            verify_custody=True,
            repo_root=args.repo_root,
        )
        observed_identity = json.loads(args.observed_identity.read_bytes())
        if not isinstance(observed_identity, Mapping):
            raise ValueError("observed identity must be a JSON object")
        build = build_calibration_acceptance_successor(
            snapshot,
            observed_identity_epoch=observed_identity,
            registry_path=args.registry,
            repo_root=args.repo_root,
            require_committed_registry=True,
            verify_custody=True,
        )
        publication_verification: dict[str, Any] | None = None
        if args.issue:
            if args.artifact_out is None or args.registry_out is None:
                raise ValueError("--issue requires --artifact-out and --registry-out")
            publication_verification = publish_successor(
                build,
                artifact_destination=args.artifact_out,
                registry_destination=args.registry_out,
                expected_registry_bytes=registry_raw,
                repo_root=args.repo_root,
            )
        elif args.artifact_out is not None or args.registry_out is not None:
            raise ValueError("dry-run forbids output destinations")
        output = build.output_record()
        if publication_verification is not None:
            output["publication_verification"] = publication_verification
        sys.stdout.buffer.write(_pretty_json_bytes(output))
        return 0
    except SuccessorDurabilityUncertain as exc:
        print(f"committed_durability_uncertain: {exc}", file=sys.stderr)
        return 3
    except (OSError, TypeError, ValueError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
