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

from joulewise import arm_readiness as readiness, battery_float, calibration_bracketing as brackets
from joulewise import network_time_off, v5_qualification as q
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


def prepare_desk(custody, frozen, policy, measurement_root, transcripts, *, runner=subprocess.run, pack=None):
    """Execute registered E1/E2, protecting every pre-existing collection byte.

    This explicit desk phase is before the immutable archive's source census.
    It never runs on re-harvest. Producers' stdout/stderr remain restricted.
    """
    runs = custody / "runs"
    rows = log_rows(runs / "campaign_log.jsonl")
    if any(row.get("record_type") == "idle_admission_whole_window_verdict" for row in rows):
        raise q.HarvestRefusal("existing_verdict_requires_authentication_only")
    if (runs / "bracket-binding.json").exists() or (runs / "whole-window-verdict.json").exists():
        raise q.HarvestRefusal("desk_output_preexists")
    before = q.census_sources({"custody": custody})["custody"]
    old_log = (runs / "campaign_log.jsonl").read_bytes()
    plan, tree, identity = frozen_identity(custody, pack=pack)
    py = measurement_root / ".venv/bin/python"
    ledger = custody / "calibration/calibration_observation_ledger.jsonl"
    pin = custody / "calibration/calibration_ledger_head.json"
    committed_pin = measurement_root / "configs/calibration/calibration_ledger_head.json"
    if pin.read_bytes() != committed_pin.read_bytes():
        raise q.HarvestRefusal("desk_head_pin_copy_mismatch")
    snapshot = physical_snapshot(custody, measurement_root)
    sessions = [session for session in snapshot.bracket_session_by_id.values()
        if (session.window_id, session.plan_id, session.plan_sha256, session.evidence_root_id, session.runs_root)
        == (identity["window_id"], plan["plan_id"], q.sha(frozen), identity["evidence_root_id"], str(runs))
        and session.state == "finalized"]
    if len(sessions) != 1:
        raise q.HarvestRefusal("bracket_session_identity_not_unique")
    session_id = sessions[0].session_id
    binding_argv = [py, "-B", measurement_root / "scripts/build_bracket_binding.py",
        "--custody-root", custody, "--session-id", session_id, "--window-id", identity["window_id"],
        "--plan-id", plan["plan_id"], "--plan-sha256", q.sha(frozen), "--frozen-plan", frozen,
        "--evidence-root-id", identity["evidence_root_id"], "--runs-root", runs,
        "--calibration-ledger", ledger, "--head-pin", pin, "--output", runs / "bracket-binding.json"]
    events = []
    start = time.monotonic_ns()
    result = command(binding_argv, transcripts / "binding.txt", runner=runner)
    if result.returncode != 0:
        raise q.HarvestRefusal("bracket_binding_producer_fault")
    binding_sha = q.sha(runs / "bracket-binding.json")
    events.append({"producer": "build_bracket_binding", "started_ns": start,
                   "completed_ns": time.monotonic_ns(), "exit_code": 0,
                   "output_sha256": binding_sha})
    start = time.monotonic_ns()
    argv = [py, "-B", measurement_root / "scripts/run_campaign.py", "--whole-window-verdict",
        "--runs-dir", runs, "--log", runs / "campaign_log.jsonl", "--campaign-policy", policy,
        "--neg8-drift-bound", runs / "neg8-drift-bound.json", "--bracket-binding", runs / "bracket-binding.json",
        "--whole-window-verdict-output", runs / "whole-window-verdict.json",
        "--calibration-ledger", ledger, "--head-pin", committed_pin]
    result = command(argv, transcripts / "whole-window.txt", runner=runner)
    if result.returncode not in {0, 1}:
        raise q.HarvestRefusal("whole_window_producer_fault")
    row = authoritative_row(runs)
    if not (runs / "campaign_log.jsonl").read_bytes().startswith(old_log):
        raise q.HarvestRefusal("desk_log_prefix_mutated")
    # Existing files other than the append-only campaign log must be identical;
    # the only newly allowed files are the two registered desk outputs.
    after = q.census_sources({"custody": custody})["custody"]
    allowed = {"runs/campaign_log.jsonl", "runs/bracket-binding.json", "runs/whole-window-verdict.json"}
    files = lambda rows: {name: val["sha256"] for name, val in rows.items() if "sha256" in val and name not in allowed}
    if files(before) != files(after):
        raise q.HarvestRefusal("source_tree_mutated")
    if (runs / "campaign_log.jsonl").read_bytes()[len(old_log):] != (runs / "whole-window-verdict.json").read_bytes():
        raise q.HarvestRefusal("desk_appended_more_than_one_row")
    events.append({"producer": "whole_window_verdict", "started_ns": start,
                   "completed_ns": time.monotonic_ns(), "exit_code": result.returncode,
                   "binding_input_sha256": binding_sha, "output_sha256": q.sha(runs / "whole-window-verdict.json")})
    record = {"schema": ORDER_SCHEMA, "runs_root": str(runs), "events": events}
    authenticate_order(record, runs)
    return record


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
        problems = q.captured_call(validator, transcripts / f"{run_id}-strict.txt", path, strict=True)
        clock = anchor_status(path)
        clock = clock if clock in {"bounded", "unbounded", "invalid", "missing", "not recorded"} else "unbounded"
        succeeded = (path / "summary_metrics.json").is_file() and q.read(path / "summary_metrics.json").get("status") == "succeeded"
        valid = not problems and succeeded and clock == "bounded"
        members.append({"run_id": q.identifier(run_id), "strict_valid": not bool(problems),
                        "succeeded": succeeded, "clock_anchor_status": clock, "valid": valid})
        if not valid:
            causes.append("member_not_strict_valid_bounded_success")
        if not problems:
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


def recover_no_science(inputs, plan, night, pack, runs):
    """Authenticate a named tooling cause and prove no science was dispatched.

    A partial science directory is conservative science custody even without
    metadata: it cannot be called no-science. Missing failure evidence never
    grants a fresh s1. This path does not require a post bracket/desk verdict
    that the pre-science fault prevented from existing.
    """
    locator = inputs.get("pre_science_tooling_failure")
    if locator is None:
        return None
    failure = q.read(q.authenticated_reference(locator))
    if (set(failure) != {"schema", "plan_id", "cause_code", "cause_class", "monotonic_ns", "seam"}
            or failure["schema"] != "joulewise.v5_pre_science_tooling_failure.v1"
            or failure["plan_id"] != plan.plan_id or failure["cause_class"] != "tooling"
            or failure["seam"] not in {"pack_path", "launch"}
            or type(failure["monotonic_ns"]) is not int):
        raise q.HarvestRefusal("pre_science_tooling_failure_invalid")
    q.identifier(failure["cause_code"])
    if failure["cause_code"].startswith(("qualification_", "rehearsal_producer_", "producer_")):
        raise q.HarvestRefusal("observation_fault_is_not_g2b_recovery")
    started = q.read(night / "chain.started")
    if type(started.get("monotonic_ns")) is not int or failure["monotonic_ns"] <= started["monotonic_ns"]:
        raise q.HarvestRefusal("tooling_failure_not_after_chain_start")
    tree = q.read(pack / "plan_tree.json")
    science = tree.get("science")
    if not isinstance(science, list) or len(science) != 80:
        raise q.HarvestRefusal("pre_science_frozen_roster_invalid")
    ids = {q.identifier(row["run_id"]) for row in science}
    if any((runs / run_id).exists() or (runs / run_id).is_symlink() for run_id in ids):
        return None
    # Unknown/partial science custody cannot be hidden by a roster mismatch.
    auxiliary = set(map(q.identifier, inputs["auxiliary_bundle_ids"]))
    for path in runs.iterdir() if runs.exists() else ():
        if path.is_dir() and path.name not in auxiliary | {"campaign_manifests", "instrument_validation"}:
            return None
    return {"verdict": "RECOVER", "recovery_classification": "recover_no_science",
            "cause_codes": [failure["cause_code"]], "cause_classes": ["tooling"],
            "science_sampler_started": False, "science_bytes_present": False,
            "consumes_s2": False, "tooling_failure": locator}


def harvest(args, *, runner=subprocess.run, now=None, clear=q.group_clear):
    input_path = q.authenticated_reference({"path": str(args.inputs.absolute()), "sha256": args.inputs_sha256})
    inputs = q.read(input_path)
    if inputs.get("schema") != INPUT_SCHEMA or inputs.get("occurrence") not in {"s1", "s2"}:
        raise q.HarvestRefusal("harvest_input_schema_invalid")
    occurrence = inputs["occurrence"]
    plan_path = q.authenticated_reference(inputs["plan"])
    kwargs = {"clear": clear}
    if now is not None:
        kwargs["now"] = now
    plan = q.load_plan(plan_path, "G2B_SHAKEDOWN", **kwargs)
    custody, night = Path(inputs["custody_root"]), Path(plan.custody_root) / "night"
    pack = Path(plan.pack_night["pack_root"])
    if plan.pack_night["pack_id"] != "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5":
        raise q.HarvestRefusal("real_gamma_pack_required")
    policy_path = q.authenticated_reference(inputs["policy"])
    acceptance_path = q.authenticated_reference(inputs["acceptance"])
    sources = {"night-custody": Path(plan.custody_root), "g2b-custody": custody, "pack": pack,
               "harvest-inputs": input_path, "policy": policy_path, "acceptance": acceptance_path,
               "chain": Path(plan.chain_path), "chain-sidecar": Path(plan.chain_sha256_path),
               "bound-runs": Path(inputs["bound_runs_root"])}
    started = (night / "chain.started").exists()
    no_science = recover_no_science(inputs, plan, night, pack, custody / "runs") if started and occurrence == "s1" else None
    missing_after_start = []
    if no_science:
        sources["pre-science-tooling-failure"] = q.authenticated_reference(inputs["pre_science_tooling_failure"])
    if started and not no_science:
        for field in ("terminal_boundary", "go", "consumption", "battery_boundaries"):
            if field not in inputs:
                missing_after_start.append(field + "_missing")
            else:
                sources[field] = q.authenticated_reference(inputs[field])
        if "battery_boundaries" in sources:
            sources.update(q.boundary_sources(sources["battery_boundaries"]))
        if "desk_producer_events" in inputs:
            sources["desk-producer-events"] = q.authenticated_reference(inputs["desk_producer_events"])
        if not args.prepare_desk:
            if "desk-producer-events" not in sources and not args.previous_harvest:
                missing_after_start.append("desk_producer_events_missing")
            for name in ("bracket-binding.json", "whole-window-verdict.json"):
                if not (custody / "runs" / name).is_file():
                    missing_after_start.append(name.replace("-", "_").replace(".json", "_missing"))
    destination = args.archive_root.absolute()
    # No recovery authority is inferred from a harvester's classification.
    if occurrence == "s2":
        authority_path = q.authenticated_reference(inputs["s2_authority"])
        authority = q.read(authority_path)
        prior = q.read(q.authenticated_reference(authority["s1_harvest"]))
        q.authenticated_reference(authority["r3_cure"])
        q.authenticated_reference(authority["head_coverage"])
        if (authority.get("schema") != "joulewise.v5_qualification_s2_authority.v1"
                or authority.get("new_plan_id") != plan.plan_id or authority.get("lead_approved") is not True
                or prior.get("occurrence") != "s1" or prior.get("verdict") != "RECOVER"
                or prior.get("plan_id") == plan.plan_id
                or prior.get("cause_classes") != ["tooling"]
                or authority.get("tooling_cause") not in prior["cause_codes"]
                or prior.get("clock_majority", {}).get("triggered") is True
                or prior.get("recovery_classification") == "recover_no_science"):
            raise q.HarvestRefusal("s2_not_authorized_tooling_cure")
        sources["s2-authority"] = authority_path
    with tempfile.TemporaryDirectory(prefix="desk-", dir=args.scratch_root) as temporary:
        transcripts = Path(temporary)
        events = None
        desk_error = None
        if started and not no_science and not missing_after_start:
            try:
                if args.prepare_desk:
                    if args.previous_harvest:
                        raise q.HarvestRefusal("reharvest_cannot_prepare_desk")
                    events = prepare_desk(custody, custody / "prospective/calibration_plan.json", policy_path,
                                          Path(plan.measurement_root), transcripts, runner=runner, pack=pack)
                elif args.previous_harvest:
                    derived = args.previous_harvest / "derived/desk-producer-events.json"
                    events = q.read(sources["desk-producer-events"] if "desk-producer-events" in sources else derived)
                else:
                    events = q.read(sources["desk-producer-events"])
            except Exception as error:
                # Preserve the collected source census and publish a refusal
                # even when a desk tool fails before producing its order proof.
                desk_error = error
        original = q.archive_sources(sources, destination, previous=args.previous_harvest)
        if events is not None:
            q.write(destination / "derived/desk-producer-events.json", events)
        shutil.copytree(transcripts, destination / "withheld/desk-production")
    record = {"schema": SCHEMA, "occurrence": occurrence, "plan_id": q.identifier(plan.plan_id),
              "plan_sha256": q.sha(plan_path), "inputs_sha256": q.sha(input_path), "head": plan.measurement_head,
              "verdict": "REFUSED", "cause_codes": [], "cause_classes": [], "members": []}
    try:
        if desk_error is not None:
            raise desk_error
        if not (night / "chain.started").exists():
            record.update(verdict="NULL", cause_codes=["chain_never_started"])
        elif no_science:
            record.update(no_science)
        elif missing_after_start:
            # Later artifacts legitimately do not exist after a started-chain
            # crash. Preserve/authenticate the retained occurrence first; this
            # is recovery evidence, not an exception from the harvest tool.
            causes = ["started_chain_incomplete", *missing_after_start]
            if (night / "chain.exited").exists() and q.read(night / "chain.exited").get("exit_code") != 0:
                causes.append("started_chain_crashed")
            record.update(verdict="RECOVER", cause_codes=sorted(causes), cause_classes=["tooling"])
        else:
            terminal = q.authenticated_reference(inputs["terminal_boundary"])
            q.require_terminal_boundary(plan, terminal)
            go_path = q.authenticated_reference(inputs["go"])
            consumed = q.authenticated_reference(inputs["consumption"])
            boundary = q.authenticated_reference(inputs["battery_boundaries"])
            go = authenticate_launch(plan, go_path, consumed)
            runs = custody / "runs"
            if any(custody.glob("**/.campaign.lock")) or (runs / "campaign.lock").exists():
                raise q.HarvestRefusal("campaign_lock_leftover")
            expected, order_sha, causes = science_roster(pack, runs, inputs["auxiliary_bundle_ids"])
            causes += stop_codes(runs, night, expected, {k: go["authorization"][k] for k in ("path", "sha256")})
            authenticate_order(events, runs)
            row = authoritative_row(runs)
            if row["status"] != "passed":
                causes.append("whole_window_not_passed")
            policy = CampaignPolicy.from_mapping(q.read(policy_path))
            if (policy.profile != CampaignPolicyProfile.PRODUCTION or not policy.calibration_bracketing.require_bracket
                    or not policy.idle_admission.enabled or policy.idle_admission.on_fail != AdmissionFailureAction.ABORT):
                raise q.HarvestRefusal("campaign_policy_not_claim_grade")
            snapshot, binding, session, bracket_causes = bracket_assessment(custody, plan, policy, acceptance_path)
            causes += bracket_causes
            bundle_ids = set(expected)
            records = checker._campaign_records(runs)
            declared = {bundle for _, value in records for bundle in checker._member_bundle_ids(value)}
            auxiliary = set(map(q.identifier, inputs["auxiliary_bundle_ids"]))
            if declared != set(expected) | auxiliary:
                causes.append("auxiliary_roster_incomplete_or_extra")
            bundle_ids.update(declared)
            # Old, failed and superseded attempts are enumerated from disk too.
            battery_pass = q.battery_boundaries(boundary, inputs["battery_boundaries"]["sha256"], plan.plan_id, plan_path=plan_path)
            attempt_pass, capture_paths = battery_attempts(custody, Path(inputs["bound_runs_root"]))
            battery_pass = battery_pass and attempt_pass
            if not battery_pass:
                causes.append("battery_observation_not_passed")
            frozen, _tree, identity = frozen_identity(custody, pack=pack)
            off = network_time_off.read_receipt(q.off_receipt_path(plan),
                                              plan_id=plan.plan_id, window_id=identity["window_id"])
            network = network_time_capture_report(off, capture_paths)
            q.write(destination / "withheld/network-time.json", network)
            settled = True
            for _, path in capture_paths:
                filename = "instrument_evidence.json" if (path / "instrument_evidence.json").exists() else "metadata.json"
                evidence = q.read(path / filename)
                pre = evidence.get("battery_float", {}).get("pre", {})
                try:
                    network_time_off.seconds_since_receipt(off, {"boot_id": go["boot_session_id"],
                        "epoch_s": pre.get("wall_time_s"),
                        "monotonic_s": pre.get("monotonic_before_ns", -1) / 1e9})
                except (ValueError, TypeError):
                    settled = False
            if not settled:
                causes.append("network_time_off_not_settled")
            check_transcripts = destination / "withheld/checks"
            desk_passed = desk_check(custody, pack, terminal, check_transcripts,
                                     acceptance=acceptance_path, runner=runner)
            record["desk_check_status"] = "PASS" if desk_passed else "FAIL"
            if not desk_passed:
                causes.append("desk_provenance_not_passed")
            bound_runs = Path(inputs["bound_runs_root"])
            bound_ids = set(map(q.identifier, inputs["bound_bundle_ids"]))
            bound_declared = {bid for _, value in checker._campaign_records(bound_runs) for bid in checker._member_bundle_ids(value)}
            if not bound_ids or bound_ids != bound_declared:
                causes.append("bound_roster_incomplete_or_extra")
            members, l10_causes = l10_a(custody, destination, sorted(bundle_ids), plan.measurement_head, runner=runner,
                additional_bundles={bid: bound_runs / bid for bid in bound_ids | bound_declared})
            if occurrence == "s2":
                (destination / "withheld/s1-reductions.json").rename(destination / "withheld/s2-reductions.json")
            causes += l10_causes
            record.update(l10_a=q.reference(destination / "l10-a/record.json"),
                          bracket_binding_sha256=q.sha(runs / "bracket-binding.json"),
                          whole_window_verdict_sha256=q.sha(runs / "whole-window-verdict.json"))
            record["members"] = members
            valid_paths = [runs / row["run_id"] for row in members if row["valid"] and row["run_id"] in bundle_ids]
            frozen, _tree, identity = frozen_identity(custody, pack=pack)
            bracket, reasons = q.captured_call(brackets.calibration_bracket_for_bundles,
                destination / "withheld/bracket-evaluation.txt", runs, valid_paths, policy.calibration_bracketing,
                mode="read_replay", ledger_snapshot=snapshot, bracket_binding=binding, bracket_window_id=identity["window_id"],
                bracket_plan_id=frozen["plan_id"], bracket_plan_sha256=q.sha(custody / "prospective/calibration_plan.json"),
                bracket_evidence_root_id=identity["evidence_root_id"])
            q.write(destination / "withheld/bracket-evaluation.json", {"assessment": bracket, "reasons": reasons})
            if bracket.get("status") != "passed" or reasons or snapshot.refusal_reasons:
                causes.append("acceptance_bracket_not_passed")
            recorded_ids = {row["run_id"] for row in members}
            for capture_id, path in capture_paths:
                if capture_id not in recorded_ids:
                    if (path / "instrument_evidence.json").exists():
                        clock = q.read(path / "instrument_evidence.json").get("clock_anchor", {}).get("status", "not recorded")
                    else:
                        clock = anchor_status(path)
                    clock = clock if clock in {"bounded", "unbounded", "invalid", "missing", "not recorded"} else "unbounded"
                    members.append({"run_id": q.identifier(capture_id), "clock_anchor_status": clock})
            majority = clock_majority(members)
            if majority["triggered"]:
                causes.append("systematic_clock_majority")
            physical = any(code in causes for code in ("member_not_strict_valid_bounded_success", "battery_observation_not_passed",
                "acceptance_bracket_not_passed", "acceptance_bracket_endpoint_not_passed", "bracket_session_not_complete",
                "network_time_off_not_settled", "outer_chain_not_successful", "whole_window_not_passed", "systematic_clock_majority"))
            record.update(verdict="RECOVER" if causes else "PASS", cause_codes=sorted(set(causes)),
                          cause_classes=["instrument_physics" if physical else "tooling"] if causes else [],
                          clock_majority=majority, science_roster=expected, frozen_order_sha256=order_sha,
                          registered_stage_stop_rc=run_campaign.MAX_BLOCKS_REACHED_RC,
                          stage_stop_rc=next((r["exit_code"] for r in log_rows(runs / "campaign_log.jsonl")
                                             if r.get("record_type") == "campaign_stop" and type(r.get("exit_code")) is int), None),
                          outer_chain_rc=q.read(night / "chain.exited").get("exit_code") if (night / "chain.exited").exists() else None)
        q.unchanged(sources, original)
        if not clear(night, plan_id=plan.plan_id):
            raise q.HarvestRefusal("launcher_group_alive")
    except Exception as error:
        record.update(verdict="REFUSED", cause_codes=[str(error) if isinstance(error, q.HarvestRefusal)
                      else "archive_authentication_or_tool_fault"], cause_classes=["tooling"])
    record.update(q.disposition(occurrence, record["verdict"], record["cause_classes"], record.get("clock_majority")))
    if record["verdict"] == "RECOVER" and record.get("recovery_classification") == "recover_no_science":
        record.update(end_state=False, s2_eligible=False, consumes_s2=False,
                      next_step="r3_cure_then_fresh_s1_plan_authorization_t0_same_code_twice_consult")
    return q.publish(destination, record)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", required=True, type=Path)
    parser.add_argument("--inputs-sha256", required=True)
    parser.add_argument("--archive-root", required=True, type=Path)
    parser.add_argument("--scratch-root", type=Path, default=Path("/tmp/dd5-fold"))
    parser.add_argument("--prepare-desk", action="store_true")
    parser.add_argument("--previous-harvest", type=Path)
    args = parser.parse_args(argv)
    try:
        record = harvest(args)
    except Exception:
        q.preflight_refusal(SCHEMA, args.scratch_root)
        return 3
    q.public_print(record)
    return 0 if record["verdict"] in {"PASS", "NULL"} else 3 if record["verdict"] == "REFUSED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
