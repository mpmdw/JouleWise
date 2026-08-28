#!/usr/bin/env python3
"""Read-only desk assertions for one collected window's provenance joins."""

from __future__ import annotations

import argparse
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
    _exclude_evidence,
    _finalized_runs_root,
    _manifest_collection_id,
    campaign_cooldown_evidence,
    supersession_visibility_scan,
    window_evidence_precheck,
)
from joulewise.analysis_manifest_v3 import (  # noqa: E402
    AnalysisManifestFinalizationError,
    calculate_manifest_id,
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
from scripts.run_campaign import (  # noqa: E402
    _sha256_bytes,
    _validated_bracket_binding_input,
    _whole_window_campaign_membership,
)


ASSERTION_IDS = (
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
    "d117_floor_qwen25_1p5b_v4",
    "d117_floor_qwen25_7b_v4",
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

    def assertion(self, assertion_id: str, check: Callable[[], str]) -> None:
        try:
            evidence = check()
        except Exception as exc:  # Every exception belongs to its assertion.
            self.failed += 1
            print(f"FAIL {assertion_id} {type(exc).__name__}: {exc}")
        else:
            self.passed += 1
            print(f"PASS {assertion_id} {evidence}")

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


def _science_records(
    records: Sequence[tuple[Path, Mapping[str, Any]]], manifest_id: str
) -> list[tuple[Path, Mapping[str, Any]]]:
    # The digest is the independent marker that keeps a mutated/null id visible
    # to A1.  Exact-id records are included for compatibility with early S11 rows.
    return [
        (path, value)
        for path, value in records
        if value.get("analysis_manifest_id") == manifest_id
        or "analysis_manifest_sha256" in value
    ]


def _selected_bundle_ids(
    records: Sequence[tuple[Path, Mapping[str, Any]]], collection_id: str
) -> set[str]:
    selected: set[str] = set()
    for _path, value in records:
        if value.get("analysis_manifest_id") == collection_id:
            selected.update(_member_bundle_ids(value))
    if not selected:
        raise AssertionFailure(
            f"no collected bundles select collection_manifest_id={collection_id}"
        )
    return selected


def _stage_present(
    stage: str, records: Sequence[tuple[Path, Mapping[str, Any]]]
) -> list[tuple[Path, Mapping[str, Any]]]:
    needle = stage.strip("/")
    basename = Path(needle).name
    result = []
    for path, value in records:
        candidates = {
            path.stem,
            str(value.get("stage_id", "")),
            str(value.get("stage", "")),
            str(value.get("config_dir", "")).rstrip("/"),
        }
        if any(
            candidate == needle
            or candidate.endswith(f"/{needle}")
            or Path(candidate).name == basename
            for candidate in candidates
            if candidate
        ):
            result.append((path, value))
    return result


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
            "gamma _v4 pack directory containing analysis_manifest_v3.json "
            "(required outside refusal mode)"
        ),
    )
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--bracket-binding", required=True, type=Path)
    parser.add_argument("--whole-window-verdict", required=True, type=Path)
    parser.add_argument("--calibration-ledger", required=True, type=Path)
    parser.add_argument("--head-pin", type=Path)
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
            "S11-A4 calibration/reference/floor/metrology ids"
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
    reporter = Reporter()
    runs_root = args.runs_root
    manifest_path = args.pack_root / "analysis_manifest_v3.json"
    try:
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

    science = _science_records(records, pack_manifest_id)
    selected_ids: set[str] = set()
    cooldowns: dict[str, Mapping[str, Any]] = {}

    def check_a1() -> str:
        if not science:
            raise AssertionFailure("no science-stage campaign manifests found")
        expected_sha = _sha256_bytes(manifest_path.read_bytes())
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
        nonlocal selected_ids, cooldowns
        selected_ids = _selected_bundle_ids(records, collection_id)
        cooldowns = campaign_cooldown_evidence(runs_root, collection_id)
        if not cooldowns:
            raise AssertionFailure("campaign_cooldown_evidence returned empty")
        missing = sorted(selected_ids - cooldowns.keys())
        if missing:
            raise AssertionFailure(f"cooldown join missing bundles={missing}")
        return f"collection_manifest_id={collection_id} covered={len(selected_ids)}"

    reporter.assertion("S11-A2", check_a2)

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

    reporter.assertion("S11-A3", check_a3)

    null_stages = args.null_bound_stage or list(DEFAULT_NULL_BOUND_STAGES)
    present_null_records: list[tuple[Path, Mapping[str, Any]]] = []
    for stage in null_stages:
        matched = _stage_present(stage, records)
        if not matched:
            reporter.skip("S11-A4", f"stage={stage} absent")
        else:
            present_null_records.extend(matched)

    def check_a4() -> str:
        if not present_null_records:
            return "present_stages=0 all configured stages absent"
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

    reporter.assertion("S11-A4", check_a4)

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

    reporter.assertion("F5-1", check_f51)

    verdict: dict[str, Any] = {}

    def check_f52() -> str:
        nonlocal verdict
        verdict = _read_object(args.whole_window_verdict, "whole-window verdict")
        verdict_ids = {
            item for item in verdict.get("bundle_ids", []) if isinstance(item, str)
        }
        missing = sorted(selected_ids - verdict_ids)
        if missing:
            raise AssertionFailure(f"verdict omits collected bundles={missing}")
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
        if (status == "passed") != (not reasons):
            raise AssertionFailure(
                f"verdict status={status} disagrees with reasons={list(reasons)}"
            )
        attached = []
        for bundle_id in sorted(selected_ids):
            evidence = BundleEvidence(
                entry={}, bundle_id=bundle_id, relative_path=bundle_id,
                path=runs_root / bundle_id, summary=None, metadata=None,
                raw_config=None, strict_problems=(), base_reason_codes=(),
                config_sha256=None, summary_sha256=None,
                replacement_classification="registered", inclusion_status="included",
            )
            for reason in reasons:
                _exclude_evidence(evidence, reason)
            if not set(reasons).issubset(evidence.base_reason_codes):
                raise AssertionFailure(f"verdict reasons did not attach to {bundle_id}")
            attached.append(bundle_id)
        return (
            f"status={status} reasons={list(reasons)} attached={len(attached)}"
        )

    reporter.assertion("F5-2", check_f52)

    def check_f53() -> str:
        if finalized is not None:
            authenticated = _finalized_runs_root(
                finalized,
                args.finalized_manifest,
                runs_root,
            )
            return f"finalized_authenticated_runs_root={authenticated}"
        snapshot = load_calibration_ledger_snapshot(
            args.calibration_ledger,
            args.head_pin,
            require_committed_pin=False,
            verify_custody=False,
        )
        binding, identity = _validated_bracket_binding_input(
            args.bracket_binding,
            snapshot=snapshot,
            runs_root=runs_root,
        )
        if not binding or identity is None:
            raise AssertionFailure(
                "production bracket-binding loader refused runs_root identity"
            )
        return f"runs_root={identity['runs_root']} binding_digest={binding['binding_digest']}"

    reporter.assertion("F5-3", check_f53)

    def check_f54() -> str:
        basis = verdict.get("evaluation_basis")
        basis_sha = basis.get("sha256") if isinstance(basis, Mapping) else None
        if not isinstance(basis_sha, str):
            raise AssertionFailure("whole-window evaluation basis sha256 missing")
        scan = supersession_visibility_scan(
            runs_root,
            scope="whole_window",
            evidence_root_id=None,
            authenticated_basis={"sha256": basis_sha},
        )
        if scan.get("status") != "clean":
            raise AssertionFailure(f"supersession scan refused: {scan}")
        read = supersession_entry_validation_results(runs_root)
        if read is None:
            raise AssertionFailure("supersession validation reader refused")
        entries, validations = read
        valid = [entry for entry, ok in zip(entries, validations, strict=True) if ok]
        policy = verdict.get("campaign_policy")
        policy_sha = policy.get("sha256") if isinstance(policy, Mapping) else None
        if not isinstance(policy_sha, str):
            raise AssertionFailure("whole-window policy sha256 missing")
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
        return f"excluded_count={len(ids)} excluded_ids={ids}"

    reporter.assertion("F5-4", check_f54)
    return reporter.summary()


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.expect_finalize_refusal:
        return _run_expect_refusal(args)
    return _run_assertions(args)


if __name__ == "__main__":
    raise SystemExit(main())
