#!/usr/bin/env python3
"""Read-only desk assertions for one collected window's provenance joins."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.analysis_engine.inputs import (  # noqa: E402
    BundleEvidence,
    _finalized_runs_root,
    _manifest_collection_id,
    campaign_cooldown_evidence,
    supersession_visibility_scan,
    window_evidence_precheck,
)
from joulewise.analysis_manifest_v3 import (  # noqa: E402
    AnalysisManifestFinalizationError,
    _directory_under_root,
    _path_under_root,
    _read_strict_object,
    _strict_json_bytes,
    calculate_manifest_id,
    canonical_json_bytes,
    finalize_prospective_analysis_manifest_v3,
)
from joulewise.calibration_ledger import load_calibration_ledger_snapshot  # noqa: E402
from joulewise.schemas import CampaignPolicy  # noqa: E402
from joulewise.whole_window import (  # noqa: E402
    AuthenticatedConsumptionSession,
    _registered_policy,
    occurrence_descriptor_identity,
    supersession_entry_validation_results,
    whole_window_refusal_reasons,
)
ASSERTION_IDS = (
    "NR14-LAYOUT",
    "S11-A1",
    "S11-A2",
    "S11-A3",
    "S11-A4",
    "S11-A5",
    "F5-1",
    "F5-2",
    "F5-3",
    "F5-4",
)
DEFAULT_NULL_BOUND_STAGES = (
    "neg8_reference_corpus",
    "window_references/start_triplet",
    "window_references/midpoint",
    "window_references/end_triplet",
    "d117_floor_qwen25_1p5b_v1",
    "d117_floor_qwen25_1p5b_v2",
    "d117_floor_qwen25_1p5b_v3",
    "d117_floor_qwen25_7b_v1",
    "d117_floor_qwen25_7b_v2",
    "d117_floor_qwen25_7b_v3",
    "qwen25_7b_decode_floor_v1",
    "metrology_v1",
)
DEFAULT_EXPECTED_REFUSALS = frozenset(
    {"analysis_finalization_member_cover_mismatch"}
)
MANIFEST_ID_RE = re.compile(r"^am-[0-9a-f]{64}$")


class AssertionFailure(RuntimeError):
    """A governed assertion failed without escaping as a traceback."""


class Reporter:
    def __init__(self) -> None:
        self.passed = 0
        self.skipped = 0
        self.failed = 0

    def assertion(self, assertion_id: str, check: Callable[[], str]) -> bool:
        try:
            evidence = check()
        except Exception as exc:  # Every exception belongs to its assertion.
            self.failed += 1
            print(f"FAIL {assertion_id} {type(exc).__name__}: {exc}")
            return False
        else:
            self.passed += 1
            print(f"PASS {assertion_id} {evidence}")
            return True

    def skip(self, assertion_id: str, evidence: str) -> None:
        self.skipped += 1
        print(f"SKIP {assertion_id} {evidence}")

    def summary(self) -> int:
        print(
            f"SUMMARY pass={self.passed} skip={self.skipped} fail={self.failed}"
        )
        return 0 if self.failed == 0 else 1


def _read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssertionFailure(f"{label} unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise AssertionFailure(f"{label} is not a JSON object")
    return value


def _campaign_records(runs_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    manifest_dir = runs_root / "campaign_manifests"
    records = [
        (path, _read_object(path, f"campaign manifest {path.name}"))
        for path in sorted(manifest_dir.glob("*.json"))
    ]
    if not records:
        raise AssertionFailure("no campaign manifests found")
    return records


def _member_bundle_ids(manifest: Mapping[str, Any]) -> list[str]:
    result: list[str] = []
    members = manifest.get("members")
    if not isinstance(members, list):
        raise AssertionFailure("campaign manifest members is not a list")
    for member in members:
        if not isinstance(member, Mapping):
            raise AssertionFailure("campaign manifest member is not an object")
        if member.get("execution") == "blocked_before_invoke":
            continue
        bundle_ids = member.get("bundle_ids")
        if not isinstance(bundle_ids, list) or any(
            not isinstance(item, str) or not item for item in bundle_ids
        ):
            raise AssertionFailure("campaign member has invalid bundle_ids")
        result.extend(bundle_ids)
    return result


def _member_run_ids(manifest: Mapping[str, Any]) -> list[str]:
    """Enumerate collected run ids without consulting the cooldown join."""

    result: list[str] = []
    members = manifest.get("members")
    if not isinstance(members, list):
        raise AssertionFailure("campaign manifest members is not a list")
    for member in members:
        if not isinstance(member, Mapping):
            raise AssertionFailure("campaign manifest member is not an object")
        if member.get("execution") == "blocked_before_invoke":
            continue
        run_id = member.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise AssertionFailure("campaign member has invalid run_id")
        result.append(run_id)
    return result


def _authenticated_order_rows(
    pack_root: Path,
    binding: Mapping[str, Any],
    *,
    path_key: str,
    sha_key: str,
    label: str,
) -> tuple[list[Mapping[str, Any]], str]:
    relative = binding.get(path_key)
    expected_sha = binding.get(sha_key)
    if not isinstance(relative, str) or not relative:
        raise AssertionFailure(f"{label} path is absent or malformed")
    if not isinstance(expected_sha, str) or re.fullmatch(r"[0-9a-f]{64}", expected_sha) is None:
        raise AssertionFailure(f"{label} sha256 is absent or malformed")
    root = pack_root.resolve(strict=True)
    path = (root / relative).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise AssertionFailure(f"{label} resolves outside the pack root") from exc
    raw = path.read_bytes()
    observed_sha = hashlib.sha256(raw).hexdigest()
    if observed_sha != expected_sha:
        raise AssertionFailure(
            f"{label} sha256 mismatch observed={observed_sha} expected={expected_sha}"
        )
    value = _read_object(path, label)
    rows = value.get("executed_order")
    if not isinstance(rows, list) or not rows or any(
        not isinstance(row, Mapping) for row in rows
    ):
        raise AssertionFailure(f"{label} executed_order is absent or malformed")
    manifest_id = binding.get("manifest_id")
    if not isinstance(manifest_id, str) or value.get("manifest_id") != manifest_id:
        raise AssertionFailure(f"{label} manifest_id disagrees with the pack binding")
    return rows, observed_sha


def _frozen_expected_roster(
    pack_root: Path,
    prospective: Mapping[str, Any],
    *,
    one_block: bool,
) -> tuple[list[str], str, str]:
    if one_block:
        stages = prospective.get("stage_manifests")
        if not isinstance(stages, list):
            raise AssertionFailure("pack stage_manifests is absent or malformed")
        first = [
            stage
            for stage in stages
            if isinstance(stage, Mapping) and stage.get("index") == 1
        ]
        if len(first) != 1:
            raise AssertionFailure("pack must bind exactly one index-1 stage manifest")
        rows, digest = _authenticated_order_rows(
            pack_root,
            first[0],
            path_key="manifest_path",
            sha_key="manifest_sha256",
            label="frozen index-1 stage order manifest",
        )
        rows = [row for row in rows if row.get("block_index") == 1]
        if not rows:
            raise AssertionFailure("frozen index-1 stage has no block-1 members")
        source = "stage_index=1 block_index=1"
    else:
        root_order = prospective.get("root_order_manifest")
        if not isinstance(root_order, Mapping):
            raise AssertionFailure("pack root_order_manifest is absent or malformed")
        rows, digest = _authenticated_order_rows(
            pack_root,
            root_order,
            path_key="path",
            sha_key="sha256",
            label="frozen root order manifest",
        )
        source = "root_order_manifest"
    roster = [row.get("run_id") for row in rows]
    if any(not isinstance(run_id, str) or not run_id for run_id in roster):
        raise AssertionFailure(f"{source} contains an invalid run_id")
    if len(roster) != len(set(roster)):
        raise AssertionFailure(f"{source} contains duplicate run_ids")
    return roster, source, digest


def _science_records(
    records: Sequence[tuple[Path, Mapping[str, Any]]],
    prospective: Mapping[str, Any],
) -> list[tuple[Path, Mapping[str, Any]]]:
    stages = prospective.get("stage_manifests")
    stage_ids = {
        str(stage.get("subcampaign_id"))
        for stage in stages or []
        if isinstance(stage, Mapping)
        and isinstance(stage.get("subcampaign_id"), str)
    }
    return [
        (path, value)
        for path, value in records
        if any(_stage_matches(stage, value.get("config_dir")) for stage in stage_ids)
    ]


def _stage_matches(stage: str, config_dir: Any) -> bool:
    if not isinstance(config_dir, str) or not config_dir:
        return False
    needle = stage.strip("/")
    candidate = config_dir.rstrip("/")
    return (
        candidate == needle
        or candidate.endswith(f"/{needle}")
        or Path(candidate).name == Path(needle).name
    )


def _stage_present(
    stage: str, records: Sequence[tuple[Path, Mapping[str, Any]]]
) -> list[tuple[Path, Mapping[str, Any]]]:
    needle = stage.strip("/")
    return [
        (path, value)
        for path, value in records
        if _stage_matches(needle, value.get("config_dir"))
    ]


def _assert_exact_member_set(
    label: str, expected: set[str], observed: set[str]
) -> None:
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing or extra:
        raise AssertionFailure(
            f"{label} member set mismatch missing={missing} extra={extra}"
        )


def _ratified_g2_boundary_snapshot(
    args: argparse.Namespace,
    binding: Mapping[str, Any],
) -> tuple[Any, Mapping[str, Any]]:
    """Authenticate the R-6 physical-ahead stop without advancing its pin."""

    record = _read_object(
        args.terminal_boundary_record, "post-bracket terminal boundary record"
    )
    snapshot = load_calibration_ledger_snapshot(
        args.calibration_ledger,
        args.head_pin,
        require_committed_pin=False,
        verify_custody=False,
    )
    if snapshot.refusal_reasons:
        raise AssertionFailure(
            "reviewed-refresh ledger snapshot is not exact "
            f"reasons={list(snapshot.refusal_reasons)}"
        )
    session_id = binding.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        raise AssertionFailure("bracket binding session_id is absent or malformed")
    candidate = record.get("terminal_head_pin_candidate")
    if (
        record.get("session_id") != session_id
        or record.get("session_state") != "finalized"
        or record.get("pin_relation") != "physical_ahead"
        or record.get("refusal_code") != "calibration_ledger_head_mismatch"
        or not isinstance(candidate, Mapping)
    ):
        raise AssertionFailure(
            "ratified post-bracket boundary record is not the expected mismatch shape "
            f"session_state={record.get('session_state')} "
            f"pin_relation={record.get('pin_relation')} "
            f"refusal_code={record.get('refusal_code')} candidate={candidate}"
        )
    expected_candidate = {
        "sequence": snapshot.head_sequence,
        "head_digest": snapshot.head_digest,
        "ledger_schema": snapshot.ledger_schema,
    }
    if dict(candidate) != expected_candidate:
        raise AssertionFailure(
            "terminal head candidate disagrees with physical head "
            f"candidate={dict(candidate)} expected={expected_candidate}"
        )
    return snapshot, dict(candidate)


def _parse_expected_refusals(value: str) -> frozenset[str]:
    result = frozenset(item.strip() for item in value.split(",") if item.strip())
    if not result:
        raise argparse.ArgumentTypeError("expected refusal set must not be empty")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Re-drive S11/F-5 provenance joins without modifying runs or custody. "
            "S11-A4 stages absent from a shakedown root are SKIP and do not affect "
            "the exit status."
        ),
        epilog=(
            "Lineage inputs: S11-A1/A4/A5 use the prospective pack; S11-A2/A3 "
            "and F5-1 use finalized lineage.collection_manifest_id when a "
            "finalized manifest is supplied, otherwise the prospective id; "
            "F5-2/F5-4 use the authoritative whole-window row; F5-3 uses the "
            "finalized consumer loader when supplied and the prospective "
            "whole-window evaluator loader otherwise."
        ),
    )
    parser.add_argument("--runs-root", required=True, type=Path)
    parser.add_argument(
        "--pack-root",
        type=Path,
        help=(
            "gamma successor pack directory containing analysis_manifest_v3.json "
            "(required outside refusal mode)"
        ),
    )
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--bracket-binding", required=True, type=Path)
    parser.add_argument("--whole-window-verdict", required=True, type=Path)
    parser.add_argument("--calibration-ledger", required=True, type=Path)
    parser.add_argument("--head-pin", type=Path)
    parser.add_argument(
        "--terminal-boundary-record",
        type=Path,
        help=(
            "required for non-finalized G2 checks; the preserved session-status "
            "record captured before the desk reviewed-refresh pin advance"
        ),
    )
    parser.add_argument(
        "--finalized-manifest",
        type=Path,
        help=(
            "optional finalized v3; when present S11-A2 uses "
            "lineage.collection_manifest_id, otherwise it uses the prospective "
            "pack manifest_id"
        ),
    )
    parser.add_argument(
        "--null-bound-stage",
        action="append",
        help=(
            "null-bound pack/stage id to scan (repeatable); omitted uses the "
            "exact S11-A4 calibration/reference/floor/metrology roster. The "
            "option may be repeated with stages from the window's frozen "
            "before_midpoint_stages.txt/after_midpoint_stages.txt lists; absence "
            "is a non-failing SKIP and the checker does not derive those lists. "
            "A stage matches the production campaign manifest's config_dir when "
            "that field is equal to, ends with, or has the same basename as the "
            "supplied stage."
        ),
    )
    parser.add_argument(
        "--expect-finalize-refusal",
        action="store_true",
        help="run only the copy-safe finalizer refusal assertion",
    )
    parser.add_argument(
        "--expected-refusals",
        type=_parse_expected_refusals,
        help=(
            "exact comma-separated observable reason-code set (default: "
            "analysis_finalization_member_cover_mismatch); one finalizer call "
            "can expose only one AnalysisManifestFinalizationError reason_code"
        ),
    )
    parser.add_argument(
        "--scratch-dir",
        type=Path,
        help="required for refusal mode; receives an automatically removed custody copy",
    )
    # Mirror scripts/finalize_analysis_manifest.py exactly.
    parser.add_argument("--prospective-manifest", type=Path)
    parser.add_argument("--plan-tree", type=Path)
    parser.add_argument("--aggregate-floor-artifact", type=Path)
    parser.add_argument("--output-dir", type=Path)
    return parser


def _require_args(args: argparse.Namespace, names: Sequence[str]) -> bool:
    missing = [f"--{name.replace('_', '-')}" for name in names if getattr(args, name) is None]
    if missing:
        print(f"FAIL CLI missing required argument(s): {', '.join(missing)}")
        print("SUMMARY pass=0 skip=0 fail=1")
        return False
    return True


def _copy_path(path: Path, custody_root: Path, copied_root: Path) -> Path:
    try:
        relative = path.absolute().relative_to(custody_root.absolute())
    except ValueError as exc:
        raise AssertionFailure(
            f"finalizer input is outside --custody-root and cannot be copy-safe: {path}"
        ) from exc
    return copied_root / relative


def _run_expect_refusal(args: argparse.Namespace) -> int:
    required = (
        "prospective_manifest",
        "plan_tree",
        "custody_root",
        "runs_root",
        "whole_window_verdict",
        "bracket_binding",
        "calibration_ledger",
        "aggregate_floor_artifact",
        "output_dir",
        "scratch_dir",
    )
    if not _require_args(args, required):
        return 2
    custody_root = args.custody_root.absolute()
    scratch_dir = args.scratch_dir.absolute()
    try:
        scratch_dir.mkdir(parents=True, exist_ok=True)
        if scratch_dir == custody_root or custody_root in scratch_dir.parents:
            raise AssertionFailure("--scratch-dir must be outside real custody")
        expected = args.expected_refusals or DEFAULT_EXPECTED_REFUSALS
        with tempfile.TemporaryDirectory(
            prefix="window-provenance-finalize-", dir=scratch_dir
        ) as tmp:
            copied_root = Path(tmp) / "custody"
            shutil.copytree(custody_root, copied_root)
            paths = {
                name: _copy_path(getattr(args, name), custody_root, copied_root)
                for name in (
                    "prospective_manifest",
                    "plan_tree",
                    "runs_root",
                    "whole_window_verdict",
                    "bracket_binding",
                    "calibration_ledger",
                    "aggregate_floor_artifact",
                    "output_dir",
                )
            }
            observed: frozenset[str]
            detail = ""
            try:
                finalize_prospective_analysis_manifest_v3(
                    paths["prospective_manifest"],
                    plan_tree_path=paths["plan_tree"],
                    custody_root=copied_root,
                    runs_root=paths["runs_root"],
                    whole_window_verdict_path=paths["whole_window_verdict"],
                    bracket_binding_path=paths["bracket_binding"],
                    calibration_ledger_path=paths["calibration_ledger"],
                    aggregate_floor_artifact_path=paths["aggregate_floor_artifact"],
                    output_dir=paths["output_dir"],
                )
            except AnalysisManifestFinalizationError as exc:
                observed = frozenset({exc.reason_code})
                detail = exc.detail
            else:
                observed = frozenset()
        expected_text = ",".join(sorted(expected)) or "<none>"
        observed_text = ",".join(sorted(observed)) or "<none>"
        if observed != expected:
            print(
                "FAIL FINALIZE-REFUSAL "
                f"observed={{{observed_text}}} expected={{{expected_text}}} "
                f"detail={detail}"
            )
            print("SUMMARY pass=0 skip=0 fail=1")
            return 1
        print(
            "PASS FINALIZE-REFUSAL "
            f"observed={{{observed_text}}} expected={{{expected_text}}}"
        )
        print("SUMMARY pass=1 skip=0 fail=0")
        return 0
    except Exception as exc:
        print(f"FAIL FINALIZE-REFUSAL {type(exc).__name__}: {exc}")
        print("SUMMARY pass=0 skip=0 fail=1")
        return 1


def _run_assertions(args: argparse.Namespace) -> int:
    required = (
        "runs_root",
        "pack_root",
        "custody_root",
        "bracket_binding",
        "whole_window_verdict",
        "calibration_ledger",
        "head_pin",
    )
    if not _require_args(args, required):
        return 2
    if args.finalized_manifest is None and not _require_args(
        args, ("terminal_boundary_record",)
    ):
        return 2
    reporter = Reporter()
    # A relative --runs-root is anchored under --custody-root, exactly as the
    # finalizer anchors relative paths under its custody root
    # (analysis_manifest_v3.py:1428-1436, :1482-1490), never under the CWD.
    runs_root_input = args.runs_root
    if not runs_root_input.is_absolute() and args.custody_root is not None:
        runs_root_input = args.custody_root.absolute() / runs_root_input
    manifest_path = args.pack_root / "analysis_manifest_v3.json"
    try:
        runs_root = runs_root_input.resolve(strict=True)
        prospective = _read_object(manifest_path, "prospective analysis manifest")
        pack_manifest_id = prospective.get("manifest_id")
        records = _campaign_records(runs_root)
        finalized = (
            _read_object(args.finalized_manifest, "finalized analysis manifest")
            if args.finalized_manifest is not None
            else None
        )
        collection_id = (
            _manifest_collection_id(finalized)
            if finalized is not None
            else pack_manifest_id
        )
        if not isinstance(pack_manifest_id, str) or not isinstance(collection_id, str):
            raise AssertionFailure("manifest lineage id is absent or malformed")
    except Exception as exc:
        for assertion_id in ASSERTION_IDS:
            reporter.assertion(
                assertion_id,
                lambda exc=exc: (_ for _ in ()).throw(exc),
            )
        return reporter.summary()

    science = _science_records(records, prospective)
    selected_ids: set[str] = set()
    cooldowns: dict[str, Mapping[str, Any]] = {}
    f5_membership_probe_ready = False

    def check_nr14_layout() -> str:
        # Preserve the caller's lexical spelling just as the finalizer does at
        # analysis_manifest_v3.py:3752-3768 and :3282-3284.
        custody_input = args.custody_root.absolute()
        custody = custody_input.resolve(strict=True)
        runs = _directory_under_root(runs_root_input, custody_input, "runs root")
        if runs == custody:
            raise AssertionFailure("runs root must be beneath, not equal to, custody root")
        resolved_inputs = {}
        for label, supplied in (
            ("bracket binding", args.bracket_binding),
            ("whole-window verdict", args.whole_window_verdict),
        ):
            resolved, _relative = _path_under_root(supplied, runs_root_input, label)
            resolved_inputs[label] = resolved
        # Mirror the finalizer's strict verdict/log admission at
        # analysis_manifest_v3.py:3289 and :3447-3504.
        verdict, _verdict_raw = _read_strict_object(
            resolved_inputs["whole-window verdict"], "whole-window verdict"
        )
        try:
            campaign_rows = [
                _strict_json_bytes(line.encode("utf-8"), "campaign-log verdict")
                for line in (runs / "campaign_log.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]
        except (OSError, UnicodeDecodeError, AnalysisManifestFinalizationError) as exc:
            raise AssertionFailure(f"campaign log unreadable: {exc}") from exc
        matches = [
            row
            for row in campaign_rows
            if isinstance(row, Mapping)
            and row.get("record_type") == "idle_admission_whole_window_verdict"
            and canonical_json_bytes(row) == canonical_json_bytes(verdict)
        ]
        if len(matches) != 1:
            raise AssertionFailure(
                "whole-window verdict object does not equal exactly one authoritative "
                f"campaign-log row (matches={len(matches)})"
            )
        return "runs_beneath_custody=true inputs_beneath_runs=true verdict_log_rows=1"

    reporter.assertion("NR14-LAYOUT", check_nr14_layout)

    def check_a1() -> str:
        if not science:
            raise AssertionFailure("no science-stage campaign manifests found")
        expected_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        for path, value in science:
            if value.get("analysis_manifest_id") != pack_manifest_id:
                raise AssertionFailure(
                    f"{path.name} analysis_manifest_id={value.get('analysis_manifest_id')!r} "
                    f"expected={pack_manifest_id}"
                )
            if value.get("analysis_manifest_sha256") != expected_sha:
                raise AssertionFailure(
                    f"{path.name} analysis_manifest_sha256 mismatch"
                )
        return f"manifests={len(science)} manifest_id={pack_manifest_id} sha256={expected_sha}"

    reporter.assertion("S11-A1", check_a1)

    def check_a2() -> str:
        nonlocal selected_ids, cooldowns, f5_membership_probe_ready
        pack_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        if not any(
            manifest.get("analysis_manifest_sha256") == pack_sha
            for _path, manifest in science
        ):
            raise AssertionFailure(
                "science campaign records do not authenticate the selected pack digest"
            )
        roster, roster_source, roster_sha = _frozen_expected_roster(
            args.pack_root,
            prospective,
            one_block=finalized is None,
        )
        expected_ids = set(roster)
        # Preserve the authenticated frozen roster as the downstream comparison
        # basis even when the first real consumer join is add/delete divergent.
        # F5-1..4 are independent exact-set assertions, not aliases that may be
        # skipped after S11-A2 finds the first mismatch.
        selected_ids = expected_ids
        missing_bundles = sorted(
            run_id
            for run_id in expected_ids
            if not (runs_root / run_id / "summary_metrics.json").is_file()
        )
        f5_membership_probe_ready = finalized is None and not missing_bundles
        cooldowns = campaign_cooldown_evidence(runs_root, collection_id)
        if not cooldowns:
            raise AssertionFailure(
                "campaign_cooldown_evidence returned empty for "
                f"collection_manifest_id={collection_id}"
            )
        _assert_exact_member_set(
            "S11-A2 collection join", expected_ids, set(cooldowns)
        )
        if missing_bundles:
            raise AssertionFailure(f"frozen roster bundles missing={missing_bundles}")
        return (
            f"collection_manifest_id={collection_id} "
            f"pack_sha256={pack_sha} roster_source={roster_source} "
            f"roster_sha256={roster_sha} expected={len(expected_ids)} "
            f"covered={len(selected_ids)}"
        )

    a2_passed = reporter.assertion("S11-A2", check_a2)

    def check_a3() -> str:
        if not selected_ids or not cooldowns:
            raise AssertionFailure("S11-A2 did not produce a collection join")
        failures = []
        for bundle_id in sorted(selected_ids):
            bundle = runs_root / bundle_id
            evidence = BundleEvidence(
                entry={},
                bundle_id=bundle_id,
                relative_path=bundle_id,
                path=bundle,
                summary=_read_object(bundle / "summary_metrics.json", f"{bundle_id} summary"),
                metadata=None,
                raw_config=None,
                strict_problems=(),
                base_reason_codes=(),
                config_sha256=None,
                summary_sha256=None,
                replacement_classification="registered",
                inclusion_status="included",
                campaign_cooldown=cooldowns.get(bundle_id),
            )
            result = window_evidence_precheck(
                evidence,
                {"metric_tag": "window-provenance-cooldown", "name": "gross_energy_j"},
            )
            if "campaign_cooldown_evidence_missing" in result["reasons"]:
                failures.append(bundle_id)
        if failures:
            raise AssertionFailure(
                f"campaign_cooldown_evidence_missing bundles={failures}"
            )
        return f"production precheck clear={len(selected_ids)}"

    if a2_passed:
        reporter.assertion("S11-A3", check_a3)
    else:
        reporter.skip("S11-A3", "prerequisite=S11-A2")

    null_stages = args.null_bound_stage or list(DEFAULT_NULL_BOUND_STAGES)
    present_null_records: list[tuple[Path, Mapping[str, Any]]] = []
    for stage in null_stages:
        present_null_records.extend(_stage_present(stage, records))

    def check_a4() -> str:
        null_join = campaign_cooldown_evidence(runs_root, None)
        expected_ids: set[str] = set()
        for path, value in present_null_records:
            if value.get("analysis_manifest_id") is not None:
                raise AssertionFailure(
                    f"{path.name} analysis_manifest_id is not null"
                )
            expected_ids.update(_member_bundle_ids(value))
        missing = sorted(expected_ids - null_join.keys())
        if missing:
            raise AssertionFailure(f"null-bound scan omitted bundles={missing}")
        return f"manifests={len(present_null_records)} bundles={len(expected_ids)}"

    if present_null_records:
        reporter.assertion("S11-A4", check_a4)
    else:
        reporter.skip("S11-A4", "present_stages=0 assertion_not_exercised")

    def check_a5() -> str:
        manifest_id = prospective.get("manifest_id")
        if not isinstance(manifest_id, str) or MANIFEST_ID_RE.fullmatch(manifest_id) is None:
            raise AssertionFailure(f"invalid top-level manifest_id={manifest_id!r}")
        calculated = calculate_manifest_id(prospective)
        if manifest_id != calculated:
            raise AssertionFailure(
                f"manifest_id={manifest_id} calculated={calculated}"
            )
        return f"manifest_id={manifest_id}"

    reporter.assertion("S11-A5", check_a5)

    def check_f51() -> str:
        if not selected_ids:
            raise AssertionFailure("S11-A2 did not identify collected bundles")
        joined = campaign_cooldown_evidence(runs_root, collection_id)
        _assert_exact_member_set("F5-1 cooldown join", selected_ids, set(joined))
        bad = {
            bundle_id: joined.get(bundle_id)
            for bundle_id in sorted(selected_ids)
            if not isinstance(joined.get(bundle_id), Mapping)
            or joined[bundle_id].get("verified") is not True
            or joined[bundle_id].get("result")
            not in {"recovered", "first_run_exempt", "cap_hit"}
        }
        if bad:
            raise AssertionFailure(f"raw disposition disagreement={bad}")
        counts = Counter(str(joined[item]["result"]) for item in selected_ids)
        return "dispositions=" + ",".join(
            f"{key}:{counts[key]}" for key in sorted(counts)
        )

    if a2_passed or f5_membership_probe_ready:
        reporter.assertion("F5-1", check_f51)
    else:
        reporter.skip("F5-1", "prerequisite=S11-A2")

    verdict: dict[str, Any] = {}

    def check_f52() -> str:
        nonlocal verdict
        verdict = _read_object(args.whole_window_verdict, "whole-window verdict")
        verdict_ids = {
            item for item in verdict.get("bundle_ids", []) if isinstance(item, str)
        }
        _assert_exact_member_set("F5-2 verdict", selected_ids, verdict_ids)
        basis = verdict.get("evaluation_basis")
        basis_sha = basis.get("sha256") if isinstance(basis, Mapping) else None
        semantics_id = (
            basis.get("consumption_semantics_id")
            if isinstance(basis, Mapping)
            else None
        )
        policy_record = verdict.get("campaign_policy")
        policy_sha = (
            policy_record.get("sha256")
            if isinstance(policy_record, Mapping)
            else None
        )
        registered_policy = _registered_policy(policy_sha)
        if not isinstance(registered_policy, Mapping):
            raise AssertionFailure("whole-window campaign policy is not registered")
        candidate: Mapping[str, Any] | None = None
        if finalized is None:
            binding = _read_object(args.bracket_binding, "bracket binding")
            snapshot, candidate = _ratified_g2_boundary_snapshot(args, binding)
        else:
            snapshot = load_calibration_ledger_snapshot(
                args.calibration_ledger,
                args.head_pin,
                require_committed_pin=False,
                verify_custody=False,
            )
        session = AuthenticatedConsumptionSession(
            runs_root,
            selected_ids,
            evaluation_basis_sha256=basis_sha if isinstance(basis_sha, str) else None,
            consumption_semantics_id=str(semantics_id),
            calibration_ledger_snapshot=snapshot,
        )
        session._prepare(
            bundle_paths={bundle_id: runs_root / bundle_id for bundle_id in selected_ids},
            policy=CampaignPolicy.from_mapping(dict(registered_policy)),
        )
        reasons = whole_window_refusal_reasons(
            runs_root,
            selected_ids,
            evaluation_basis_sha256=basis_sha if isinstance(basis_sha, str) else None,
            consumption_session=session,
            consumption_semantics_id=str(semantics_id),
        )
        status = verdict.get("status", verdict.get("verdict"))
        if status != "passed" or reasons:
            raise AssertionFailure(
                f"verdict is not an independently clean pass: "
                f"status={status} reasons={list(reasons)}"
            )
        boundary = (
            f" boundary=physical_ahead candidate_sequence={candidate['sequence']}"
            if candidate is not None
            else ""
        )
        return (
            f"status={status} reasons={list(reasons)} attachment=recomputed{boundary}"
        )

    if a2_passed or f5_membership_probe_ready:
        reporter.assertion("F5-2", check_f52)
    else:
        reporter.skip("F5-2", "prerequisite=S11-A2")

    def check_f53() -> str:
        collected_ids = {
            run_id
            for _path, record in science
            for run_id in _member_run_ids(record)
        }
        _assert_exact_member_set(
            "F5-3 science campaign records", selected_ids, collected_ids
        )
        if finalized is not None:
            authenticated = _finalized_runs_root(
                finalized,
                args.finalized_manifest,
                runs_root,
            )
            return f"finalized_authenticated_runs_root={authenticated}"
        from scripts.run_campaign import _validated_bracket_binding_input

        binding_input = _read_object(args.bracket_binding, "bracket binding")
        snapshot, candidate = _ratified_g2_boundary_snapshot(args, binding_input)
        binding, identity = _validated_bracket_binding_input(
            args.bracket_binding,
            snapshot=snapshot,
            runs_root=runs_root,
        )
        if not binding or identity is None:
            raise AssertionFailure(
                "production bracket-binding loader refused runs_root identity"
            )
        return (
            f"runs_root={identity['runs_root']} binding_digest={binding['binding_digest']} "
            f"boundary=physical_ahead candidate_sequence={candidate['sequence']}"
        )

    if a2_passed or f5_membership_probe_ready:
        reporter.assertion("F5-3", check_f53)
    else:
        reporter.skip("F5-3", "prerequisite=S11-A2")

    def check_f54() -> str:
        basis = verdict.get("evaluation_basis")
        basis_sha = basis.get("sha256") if isinstance(basis, Mapping) else None
        if not isinstance(basis_sha, str):
            raise AssertionFailure("whole-window evaluation basis sha256 missing")
        scans = {
            scope: supersession_visibility_scan(
                runs_root,
                scope=scope,
                evidence_root_id=None,
                authenticated_basis={"sha256": basis_sha},
            )
            for scope in ("whole_window", "analysis_corpus")
        }
        refused = {scope: scan for scope, scan in scans.items() if scan.get("status") != "clean"}
        if refused:
            raise AssertionFailure(f"supersession scans refused: {refused}")
        read = supersession_entry_validation_results(runs_root)
        if read is None:
            raise AssertionFailure("supersession validation reader refused")
        entries, validations = read
        valid = [entry for entry, ok in zip(entries, validations, strict=True) if ok]
        policy = verdict.get("campaign_policy")
        policy_sha = policy.get("sha256") if isinstance(policy, Mapping) else None
        if not isinstance(policy_sha, str):
            raise AssertionFailure("whole-window policy sha256 missing")
        from scripts.run_campaign import _whole_window_campaign_membership

        membership = _whole_window_campaign_membership(runs_root, policy_sha)
        if membership.conditions:
            raise AssertionFailure(
                f"whole-window membership refused: {list(membership.conditions)}"
            )
        selected_by_id = {
            source.run_id or source.path.name: occurrence_descriptor_identity(
                source.occurrence
            )
            for source in membership.sources
        }
        _assert_exact_member_set(
            "F5-4 whole-window membership", selected_ids, set(selected_by_id)
        )
        excluded: list[str] = []
        survivors: list[str] = []
        for entry in valid:
            bundle_id = entry.get("bundle_id")
            superseded = entry.get("superseded_occurrences")
            excluded.append(str(bundle_id))
            selected = selected_by_id.get(str(bundle_id))
            expected_selected = occurrence_descriptor_identity(
                entry.get("selected_occurrence")
            )
            if selected != expected_selected or any(
                occurrence_descriptor_identity(row) == selected
                for row in superseded or []
            ):
                survivors.append(str(bundle_id))
        if survivors:
            raise AssertionFailure(f"conflicted bundles survived={sorted(survivors)}")
        ids = sorted(set(excluded))
        return (
            "scopes=whole_window,analysis_corpus "
            f"excluded_count={len(ids)} excluded_ids={ids}"
        )

    if a2_passed or f5_membership_probe_ready:
        reporter.assertion("F5-4", check_f54)
    else:
        reporter.skip("F5-4", "prerequisite=S11-A2")
    return reporter.summary()


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.expect_finalize_refusal:
        return _run_expect_refusal(args)
    return _run_assertions(args)


if __name__ == "__main__":
    raise SystemExit(main())
