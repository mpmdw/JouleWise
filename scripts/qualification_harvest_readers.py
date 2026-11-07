#!/usr/bin/env python3
"""Blind, immutable s1/s2 harvest and folded L10-A contract-prefix proof.

Desk binding/verdict production precedes archival. --prepare-desk permits only
the registered new binding and one log row; all collected bytes are checked.
Re-harvest authenticates retained producer events and never appends a row.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import receipt_readers as readiness; from joulewise import battery_float; from joulewise import calibration_bracketing as brackets
from joulewise.hazards import network_time as network_time_off; from joulewise import night_gate; from joulewise import qualification_readers as q
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from joulewise.cli import validate_bundle
from joulewise.reduce import reduce_bundle
from joulewise.schemas import CampaignPolicy, CampaignPolicyProfile, AdmissionFailureAction
from joulewise.whole_window import validate_whole_window_verdict_row
from scripts import check_window_provenance as checker, run_campaign
from scripts.harvest_g2a_window import anchor_status
from scripts.summarize_g2a_prefill_probe import network_time_capture_report

SCHEMA = "joulewise.harvest_v5_g2b_window.v1"
INPUT_SCHEMA = "joulewise.v5_g2b_harvest_inputs.v1"
L10_SCHEMA = "joulewise.v5_l10_a_record.v1"
ORDER_SCHEMA = "joulewise.v5_desk_producer_events.v1"
ACCEPTANCE_ID = "d079_calibration_acceptance_v2_n24_25g83_r2"
ACCEPTANCE_SHA256 = "f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660"
FINALIZER_REASON = "analysis_finalization_member_cover_mismatch"


def command(argv, transcript, *, runner=subprocess.run):
    result = runner(list(map(str, argv)), capture_output=True, text=True, check=False, timeout=600)
    Path(transcript).parent.mkdir(parents=True, exist_ok=True)
    with Path(transcript).open("x") as stream:
        stream.write(result.stdout)
        stream.write(result.stderr)
    return result


def clock_majority(members):
    recorded = [row for row in members if row["clock_anchor_status"] != "not recorded"]
    unbounded = sum(row["clock_anchor_status"] != "bounded" for row in recorded)
    return {"recorded": len(recorded), "non_bounded": unbounded,
            "triggered": len(recorded) >= 5 and 2 * unbounded > len(recorded)}


def log_rows(path):
    return [readiness.parse_json_bytes(line) for line in path.read_bytes().splitlines() if line.strip()]


def authoritative_row(runs):
    raw_rows = [line for line in (runs / "campaign_log.jsonl").read_bytes().splitlines(keepends=True) if line.strip()]
    pairs = [(raw, readiness.parse_json_bytes(raw)) for raw in raw_rows]
    verdicts = [(raw, row) for raw, row in pairs if row.get("record_type") == "idle_admission_whole_window_verdict"]
    if len(verdicts) != 1:
        raise q.HarvestRefusal("authoritative_verdict_count_not_one")
    raw, row = verdicts[0]
    if (runs / "whole-window-verdict.json").read_bytes() != raw:
        raise q.HarvestRefusal("verdict_copy_not_exact")
    validation = validate_whole_window_verdict_row(row, runs, set(row["bundle_ids"]))
    if not validation.authentic:
        raise q.HarvestRefusal("whole_window_row_unauthenticated")
    return row


def authenticate_order(events, runs):
    if (events.get("schema") != ORDER_SCHEMA or events.get("runs_root") != str(runs)
            or [e.get("producer") for e in events.get("events", [])] != ["build_bracket_binding", "whole_window_verdict"]):
        raise q.HarvestRefusal("desk_producer_order_invalid")
    binding, verdict = events["events"]
    if (binding["exit_code"] != 0 or verdict["exit_code"] not in {0, 1}
            or not binding["started_ns"] <= binding["completed_ns"] < verdict["started_ns"] <= verdict["completed_ns"]
            or binding["output_sha256"] != q.sha(runs / "bracket-binding.json")
            or verdict["binding_input_sha256"] != binding["output_sha256"]
            or verdict["output_sha256"] != q.sha(runs / "whole-window-verdict.json")):
        raise q.HarvestRefusal("desk_producer_order_invalid")


def frozen_identity(custody, *, pack=None):
    """Read immutable generator identities from the authenticated plan tree."""
    prospective = custody / "prospective"
    frozen_path = prospective / "calibration_plan.json"
    tree_path = prospective / "plan_tree.json"
    frozen, tree = q.read(frozen_path), q.read(tree_path)
    if pack is not None:
        for path in (frozen_path, tree_path):
            if path.read_bytes() != (pack / path.name).read_bytes():
                raise q.HarvestRefusal("frozen_pack_copy_mismatch")
    reference = tree.get("plan", {})
    if (reference.get("path") != frozen_path.name or reference.get("plan_id") != frozen.get("plan_id")
            or reference.get("actual_sha256") != q.sha(frozen_path)
            or reference.get("declared_sha256") != q.sha(frozen_path)):
        raise q.HarvestRefusal("frozen_plan_tree_binding_invalid")
    identity = tree.get("window_identity", {})
    for key in ("window_id", "evidence_root_id"):
        q.identifier(identity.get(key))
    return frozen, tree, identity


def physical_snapshot(custody, measurement_root):
    # The custody pin is the authenticated seed. The generator does not put a
    # mutable ledger head in calibration_plan.json. Never infer it from fields
    # added to that frozen file.
    snapshot = load_calibration_ledger_snapshot(
        custody / "calibration/calibration_observation_ledger.jsonl",
        custody / "calibration/calibration_ledger_head.json",
        require_committed_pin=False, verify_custody=True, mode="read_replay", repo_root=measurement_root)
    if snapshot.refusal_reasons:
        raise q.HarvestRefusal("physical_ledger_custody_invalid")
    return snapshot




def science_roster(pack, runs, auxiliary=()):
    prospective = q.read(pack / "analysis_manifest_v3.json")
    expected, _source, order_sha = checker._frozen_expected_roster(pack, prospective, one_block=True)
    if len(expected) != 4:
        raise q.HarvestRefusal("first_block_not_four_members")
    records = checker._science_records(checker._campaign_records(runs), prospective)
    observed, bundles = [], []
    for _path, value in records:
        for member in value.get("members", []):
            observed.append(member.get("run_id"))
            bundles.extend(member.get("bundle_ids", []))
    causes = []
    if observed != expected or bundles != expected:
        causes.append("science_roster_or_order_mismatch")
    # Scan ALL directories, not merely the declared manifest cover. A created
    # fifth/partial bundle must not disappear behind a four-member manifest.
    known = set(expected)
    all_science = set()
    stage_ids = {stage["subcampaign_id"] for stage in prospective["stage_manifests"]}
    for path in runs.iterdir():
        if not path.is_dir() or path.name == "campaign_manifests":
            continue
        if path.name in known:
            all_science.add(path.name)
            continue
        if path.name not in set(auxiliary) | {"instrument_validation"}:
            all_science.add(path.name)
        for filename in ("config.json", "metadata.json"):
            if (path / filename).is_file():
                document = q.read(path / filename)
                texts = [document.get("run_id"), document.get("campaign_id"), document.get("config_dir")]
                if any(isinstance(text, str) and any(stage in text for stage in stage_ids) for text in texts):
                    all_science.add(path.name)
    if all_science != known:
        causes.append("fifth_partial_or_missing_science_bundle")
    return expected, order_sha, causes


def stop_codes(runs, night, expected, authorization):
    stops = [row for row in log_rows(runs / "campaign_log.jsonl") if row.get("record_type") == "campaign_stop"]
    expected_binding = {"max_blocks": 1, "source": "authorization", "authorization": authorization,
                        "purpose": "G2B_SHAKEDOWN"}
    valid = (len(stops) == 1 and stops[0].get("schema_version") == run_campaign.CAMPAIGN_STOP_SCHEMA
             and stops[0].get("stop_reason") == "max_blocks_reached"
             and type(stops[0].get("exit_code")) is int
             and stops[0].get("exit_code") == run_campaign.MAX_BLOCKS_REACHED_RC
             and type(stops[0].get("completed_blocks")) is int and type(stops[0].get("last_block_index")) is int
             and stops[0].get("completed_blocks") == 1 and stops[0].get("last_block_index") == 1
             and stops[0].get("last_block_members") == expected and stops[0].get("block_limit") == expected_binding)
    causes = [] if valid else ["governed_one_block_stop_invalid"]
    outer = q.read(night / "chain.exited").get("exit_code") if (night / "chain.exited").exists() else None
    if type(outer) is not int or outer != 0:
        causes.append("outer_chain_not_successful")
    return causes


def authenticate_launch(plan, go_path, consumed_path):
    go = readiness.validate_pack_night_go_receipt(q.read(go_path))
    authorization = q.read(q.authenticated_reference({k: go["authorization"][k] for k in ("path", "sha256")}))
    if (go["purpose"] != "G2B_SHAKEDOWN" or authorization["claim_eligible"] is not False
            or go["plan_id"] != plan.plan_id or go["pack_id"] != plan.pack_night["pack_id"]):
        raise q.HarvestRefusal("launch_purpose_or_identity_invalid")
    record, _raw, _digest, path = readiness._read_launch_consumption(consumed_path, require_current_boot=False)
    if (record["schema_version"] != readiness.CONSUMPTION_RECEIPT_SCHEMA_V3
            or record["go_receipt"]["path"] != str(go_path) or record["go_receipt"]["sha256"] != q.sha(go_path)):
        raise q.HarvestRefusal("launch_consumption_go_mismatch")
    table, digest = readiness._consumed_confirmation_pair(record, None, None)
    arm, arm_path, pack, _ = readiness._replay_consumed_arm(None, record, path, require_current_boot=False,
        require_unexpired=False, replay_arm_semantics=False, step6_confirmation_table=table,
        expected_confirmation_digest=digest)
    readiness.verify_consumed_launch(pack, path, require_current_boot=False)
    candidates = list((Path(plan.custody_root) / go["pack_id"]).rglob("*.consumed.json"))
    if candidates != [consumed_path] or not go["issued_monotonic_ns"] <= record["consumed_at_monotonic_ns"] < go["valid_until_monotonic_ns"]:
        raise q.HarvestRefusal("launch_not_one_use")
    for item in readiness.scan_receipt_namespace(arm_path.parent, "arm"):
        if (item["receipt"]["boot_session_id"] == arm["boot_session_id"]
                and item["number"] > int(arm_path.stem.removeprefix("arm-"))):
            raise q.HarvestRefusal("launch_higher_arm_exists")
    return go


def bracket_assessment(custody, plan, policy, acceptance_path):
    frozen_path = custody / "prospective/calibration_plan.json"
    frozen, tree, identity = frozen_identity(custody, pack=Path(plan.pack_night["pack_root"]))
    binding = q.read(custody / "runs/bracket-binding.json")
    acceptance = brackets.load_calibration_acceptance_bound(acceptance_path)
    if (acceptance is None or acceptance["acceptance_id"] != ACCEPTANCE_ID
            or q.sha(acceptance_path) != ACCEPTANCE_SHA256
            or tree.get("acceptance_policy", {}).get("issued_artifact_sha256") != q.sha(acceptance_path)
            or tree.get("acceptance_policy", {}).get("issued_artifact_id") != ACCEPTANCE_ID):
        raise q.HarvestRefusal("acceptance_r2_binding_invalid")
    ledger = custody / "calibration/calibration_observation_ledger.jsonl"
    pin = custody / "calibration/calibration_ledger_head.json"
    # Authentication first binds the frozen seed; acceptance decisions use a
    # SECOND snapshot whose baseline is explicitly the issuance CUTOFF (#467).
    kwargs = dict(require_committed_pin=False, verify_custody=True, mode="read_replay",
                  repo_root=Path(plan.measurement_root))
    physical = physical_snapshot(custody, Path(plan.measurement_root))
    cutoff = acceptance["ledger_cutoff"]
    snapshot = load_calibration_ledger_snapshot(ledger, pin, baseline_sequence=cutoff["sequence"],
                                               baseline_digest=cutoff["head_digest"], **kwargs)
    session = snapshot.bracket_session_by_id.get(binding["session_id"])
    if (session is None or session.state != "finalized" or session.plan_sha256 != q.sha(frozen_path)
            or session.runs_root != str(custody / "runs") or session.window_id != identity["window_id"]
            or session.plan_id != frozen["plan_id"] or session.evidence_root_id != identity["evidence_root_id"]):
        return snapshot, binding, {"status": "failed"}, ["bracket_session_not_complete"]
    pair = brackets.validate_calibration_bracket_binding(binding, snapshot, window_id=identity["window_id"],
        plan_id=frozen["plan_id"], plan_sha256=q.sha(frozen_path), evidence_root_id=identity["evidence_root_id"],
        runs_root=custody / "runs")
    causes = []
    if pair is None or any(session.finalized_slots.get(role) is None
                          or session.finalized_slots[role].disposition != "valid" for role in ("pre", "post")):
        causes.append("acceptance_bracket_endpoint_not_passed")
    return snapshot, binding, session, causes


def desk_check(custody, pack, terminal, transcripts, *, acceptance=None, runner=subprocess.run, python=sys.executable):
    runs = custody / "runs"
    argv = [python, "-B", ROOT / "scripts/check_window_provenance.py", "--runs-root", runs,
        "--pack-root", pack, "--custody-root", custody, "--bracket-binding", runs / "bracket-binding.json",
        "--whole-window-verdict", runs / "whole-window-verdict.json", "--calibration-ledger",
        custody / "calibration/calibration_observation_ledger.jsonl", "--head-pin",
        custody / "calibration/calibration_ledger_head.json", "--terminal-boundary-record", terminal]
    if acceptance is not None:
        argv += ["--acceptance", acceptance]
    result = command(argv, transcripts / "desk-check.txt", runner=runner)
    lines = result.stdout.splitlines()
    nr14 = sum(line.startswith("PASS NR14-LAYOUT ") for line in lines) == 1
    a4 = [line for line in lines if re.match(r"(PASS|SKIP|FAIL) S11-A4(?: |$)", line)]
    good_a4 = len(a4) == 1 and (a4[0].startswith("PASS S11-A4 ") or a4[0] == "SKIP S11-A4 present_stages=0 assertion_not_exercised")
    return result.returncode == 0 and nr14 and good_a4 and not any(line.startswith("FAIL ") for line in lines)


def empty_floors(path):
    if path.is_symlink() or not path.is_dir() or any(path.iterdir()):
        raise q.HarvestRefusal("l10_floors_not_empty")


def member_assessment(run_id, path, transcript, *, validator=validate_bundle):
    """The shared strict-valid, successful, bounded-clock member predicate."""
    problems = q.captured_call(validator, transcript, path, strict=True)
    clock = anchor_status(path)
    clock = clock if clock in {"bounded", "unbounded", "invalid", "missing", "not recorded"} else "unbounded"
    succeeded = (path / "summary_metrics.json").is_file() and q.read(path / "summary_metrics.json").get("status") == "succeeded"
    return {"run_id": q.identifier(run_id), "strict_valid": not bool(problems),
            "succeeded": succeeded, "clock_anchor_status": clock,
            "valid": not problems and succeeded and clock == "bounded"}




def l10_a(custody, destination, bundle_ids, head, *, runner=subprocess.run, python=sys.executable,
          additional_bundles=None,
          validator=validate_bundle, reducer=reduce_bundle):
    root = destination / "withheld/l10-a"
    root.mkdir(parents=True)
    transcripts = root / "transcripts"
    source_runs = custody / "runs"
    empty_floors(custody / "floors")
    before = q.tree_hash(source_runs)
    reductions, members, causes = [], [], []
    paths = {run_id: source_runs / run_id for run_id in bundle_ids}
    for run_id, path in (additional_bundles or {}).items():
        if run_id in paths:
            raise q.HarvestRefusal("bound_science_identity_overlap")
        paths[run_id] = path
    for run_id, path in sorted(paths.items()):
        member = member_assessment(run_id, path, transcripts / f"{run_id}-strict.txt", validator=validator)
        members.append(member)
        if not member["valid"]:
            causes.append("member_not_strict_valid_bounded_success")
        if member["strict_valid"]:
            metrics = q.captured_call(reducer, transcripts / f"{run_id}-reduce.txt", path)
            if hasattr(metrics, "to_dict"):
                metrics = metrics.to_dict()
            metric_path = root / "reductions" / f"{run_id}.summary_metrics.rereduced.json"
            q.write(metric_path, metrics)
            reductions.append({"run_id": run_id, "source": str(path), "source_tree_sha256": q.tree_hash(path), "metrics": metrics})
    q.write(destination / "withheld/s1-reductions.json",
            {"schema": "joulewise.v5_qualification_reductions.v1", "members": reductions})
    staging = root / "staging"
    staging.mkdir()
    for source, name in ((source_runs, "g2b"), (custody / "prospective", "prospective"),
                         (custody / "calibration", "calibration"), (custody / "floors", "floors")):
        shutil.copytree(source, staging / name)
    empty_floors(staging / "floors")
    if q.tree_hash(staging / "g2b") != before:
        raise q.HarvestRefusal("l10_staging_tree_mismatch")
    required = ["prospective/analysis_manifest_v3.json", "prospective/plan_tree.json", "g2b/whole-window-verdict.json",
                "g2b/bracket-binding.json", "calibration/calibration_observation_ledger.jsonl"]
    if not all((staging / name).is_file() for name in required):
        raise q.HarvestRefusal("l10_staging_incomplete")
    scratch = root / "scratch"
    scratch.mkdir()
    argv = [python, "-B", ROOT / "scripts/check_window_provenance.py", "--expect-finalize-refusal",
        "--scratch-dir", scratch, "--prospective-manifest", staging / required[0], "--plan-tree", staging / required[1],
        "--custody-root", staging, "--runs-root", staging / "g2b", "--whole-window-verdict", staging / required[2],
        "--bracket-binding", staging / required[3], "--calibration-ledger", staging / required[4],
        "--aggregate-floor-artifact", staging / "floors/d117-v5-aggregate-floor.json", "--output-dir", staging]
    result = command(argv, transcripts / "finalization.txt", runner=runner)
    good = (result.returncode == 0 and result.stdout.splitlines() == [
        f"PASS FINALIZE-REFUSAL observed={{{FINALIZER_REASON}}} expected={{{FINALIZER_REASON}}}",
        "SUMMARY pass=1 skip=0 fail=0"] and not result.stderr)
    if not good:
        causes.append("l10_finalizer_not_exact_singleton")
    # Never echo the finalizer's detail: it can include numeric diagnostics.
    known_refusals = {FINALIZER_REASON, "analysis_finalization_attachment_missing", "analysis_finalization_noncanonical"}
    # Parse only the observed set, excluding the checker's expected-set text.
    match = re.search(r"observed=\{([^}]*)\}", result.stdout)
    observed = sorted(set((match.group(1).split(",") if match else [])) & known_refusals)
    empty_floors(custody / "floors")
    empty_floors(staging / "floors")
    after = q.tree_hash(source_runs)
    if after != before or q.tree_hash(staging / "g2b") != before:
        raise q.HarvestRefusal("source_tree_mutated")
    record = {"schema": L10_SCHEMA, "proof_scope": "L10_A_G2B_CONTRACT_PREFIX", "head": head,
              "status": "PASS" if good and not causes else "FAIL", "g2b_tree_before": before,
              "g2b_tree_after": after, "staged_tree_sha256": q.tree_hash(staging / "g2b"),
              "floors_empty_before_after": True, "source_unchanged": True,
              "observed_reason_codes": [FINALIZER_REASON] if good else observed or ["unexpected_finalizer_result"],
              "input_hashes": {name: q.sha(staging / name) for name in required},
              "transcript_sha256": q.sha(transcripts / "finalization.txt")}
    q.write(destination / "l10-a/record.json", record)
    return members, causes


def battery_attempts(custody, bound_runs):
    """Every retained attempt is judged; manifests cannot hide old raw pairs."""
    runs = custody / "runs"
    attempts = {p for p in runs.iterdir() if p.is_dir() and (p / "metadata.json").exists()}
    attempts.update(p for p in bound_runs.iterdir() if p.is_dir() and (p / "metadata.json").exists())
    passed, captures = True, []
    for path in sorted(attempts):
        pair = battery_float.authenticate_bundle(path)
        passed = passed and pair.status == "pass"
        captures.append((path.name, path))
    for evidence in sorted(custody.glob("**/instrument_evidence.json")):
        # Attached calibration copies authenticate with their original capture;
        # they do not contain the capture's raw ioreg pair.
        if any(bundle in evidence.parents and "instrument_calibration" in evidence.relative_to(bundle).parts
               for bundle in attempts):
            continue
        path = evidence.parent
        pair = battery_float.authenticate_capture(path)
        passed = passed and pair.status == "pass"
        captures.append((path.name, path))
    return passed, captures




def native_null_refusals(night, plan):
    """Retain validated native refusal reasons from this occurrence's bytes."""
    from scripts import run_night
    codes, references = set(), []
    paths = sorted({*night.glob("refusal.json"), *night.glob("refusal-[0-9]*.json")})
    for path in paths:
        ref = q.reference(path)
        value = q.read(q.authenticated_reference(ref))
        validator = (run_night.validate_refusal if value.get("schema") == run_night.REFUSAL_SCHEMA
                     else night_gate.validate_receipt)
        if validator(value) or value.get("verdict") != "REFUSED" or not value.get("refusal"):
            raise q.HarvestRefusal("native_refusal_invalid")
        if value.get("plan_id") != plan.plan_id or value.get("receipt_class") != plan.receipt_class:
            raise q.HarvestRefusal("native_refusal_identity_mismatch")
        codes.add(q.identifier(value["refusal"]["reason"]))
        references.append(ref)
    return sorted(codes), references
