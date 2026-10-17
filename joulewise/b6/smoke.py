"""Prepare a reduced, isolated collection and desk its non-claim archive.

The caller launches driver_argv through the production route. This module
never launches the driver and never overrides a physical check.
"""
from __future__ import annotations

import copy
import dataclasses
import datetime as dt
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

from joulewise.b5 import chain, plan
from joulewise.b6 import fingerprint, compose
from joulewise.b6.acceptance_interface import AcceptanceResult, SessionEvidence, load_acceptance
from joulewise.hazards.base import canonical_json, write_create_once

REDUCTION_SCHEMA = "joulewise.b6_smoke_reduction.v1"
KEEP_PATH = Path(__file__).resolve().parents[2] / "configs/b6/smoke_keep.json"
# Block 6 classifies its own codes (the driver's agent.*, sleep.*, idle.*) in its
# own catalog; the sealed block-5 catalog does not list them (stage-1 integration).
CATALOG_PATH = Path(__file__).resolve().parents[2] / "configs/b6/flag_catalog_b6.json"
HARVEST_ARGV = ("scripts/harvest_b6_session.py",)
PHYSICAL_PREFIXES = ("battery.", "thermal.", "clock.", "contention.", "disk.", "instrument.",
                     "sleep.", "member.idle_")


class SmokePrepareError(ValueError):
    """The smoke cannot be prepared safely; no session refusal is implied."""


def _arguments(row):
    return row["launch"]["commands"][0]["argv_template"]["arguments"]


def _runs_binding(row):
    args = _arguments(row)
    for arg, value in zip(args, args[1:]):
        if arg.get("value") == "--runs-dir":
            return value
    return None


def config_keeps(tree, keep):
    known = {row["stage_id"]: row for row in tree["stage_graph"]}
    if set(keep) - set(known):
        raise SmokePrepareError("keep names an unknown stage id")
    mapping = {}
    for stage_id, count in keep.items():
        row = known[stage_id]
        if type(count) is not int or count < 0 or count > row["expected_count"]:
            raise SmokePrepareError(f"keep exceeds expected_count or is invalid: {stage_id}")
        if row["kind"] != "campaign_collection" or count == 0:
            continue
        directory = _arguments(row)[0]["value"]
        if directory in mapping and mapping[directory] != count:
            raise SmokePrepareError("same config directory has different keeps")
        mapping[directory] = count
    return mapping


def reduce_tree(tree, keep):
    config_keeps(tree, keep)
    reduced = copy.deepcopy(tree)
    graph = reduced["stage_graph"]
    removed = {row["stage_id"] for row in graph
               if row["kind"] == "campaign_collection" and keep.get(row["stage_id"], 0) == 0}
    for row in graph:
        if row["kind"] == "bound_derivation":
            binding = _runs_binding(row)
            corpus = [item for item in graph if item["kind"] == "campaign_collection"
                      and _runs_binding(item) == binding and item["ordinal"] < row["ordinal"]]
            if corpus and max(corpus, key=lambda item: item["ordinal"])["stage_id"] in removed:
                removed.add(row["stage_id"])
    kept = sorted((row for row in graph if row["stage_id"] not in removed), key=lambda row: row["ordinal"])
    for index, row in enumerate(kept):
        row["ordinal"] = index + 1
        row["predecessor"] = kept[index - 1]["stage_id"] if index else None
        row["successor"] = kept[index + 1]["stage_id"] if index + 1 < len(kept) else None
        if row["kind"] == "campaign_collection":
            row["expected_count"] = keep[row["stage_id"]]
            row.pop("spare_retry", None)
    reduced["stage_graph"] = kept
    reduced["smoke_reduction"] = {"schema": REDUCTION_SCHEMA, "keep": dict(keep),
                                  "removed": [row["stage_id"] for row in graph if row["stage_id"] in removed]}
    chain.stage_plan(reduced)
    return reduced


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def copy_ledger(claim_measurement_root, measurement, smoke_dir):
    """Copy the ledger and head pin, proving isolation and leaving the source intact."""
    smoke_dir = Path(smoke_dir).resolve()
    copied = []
    for relative in (plan.DEFAULT_LEDGER_RELATIVE, plan.HEAD_PIN_RELATIVE):
        source = Path(claim_measurement_root) / relative
        destination = Path(measurement) / relative
        if not destination.resolve().is_relative_to(smoke_dir):
            raise SmokePrepareError("ledger destination is outside smoke_dir")
        before = source.stat()
        if destination.exists():
            target = destination.stat()
            if (before.st_dev, before.st_ino) == (target.st_dev, target.st_ino):
                raise SmokePrepareError("ledger source and destination are the same file")
        before_hash = _sha256(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        after = destination.stat()
        if (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino):
            raise SmokePrepareError("ledger copy shares source inode")
        if _sha256(source) != before_hash or _sha256(destination) != before_hash:
            raise SmokePrepareError("ledger source changed during copy")
        copied.append(str(destination))
    return tuple(copied)


def _git(root, *args, run=subprocess.run):
    result = run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
                 timeout=120, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    return result.stdout.strip()


def clone_checkout(repo, commit, destination, *, run=subprocess.run):
    run(["git", "clone", "--no-local", "--quiet", Path(repo).resolve().as_uri(), str(destination)],
        check=True, capture_output=True, text=True, timeout=120)
    _git(destination, "checkout", "--quiet", "--detach", commit, run=run)
    _git(destination, "remote", "remove", "origin", run=run)
    _git(destination, "config", "--local", "user.name", "B6 Smoke", run=run)
    _git(destination, "config", "--local", "user.email", "smoke@invalid", run=run)
    _git(destination, "config", "--local", "commit.gpgsign", "false", run=run)
    for key, value in (("maintenance.auto", "false"), ("gc.auto", "0"),
                       ("maintenance.autoDetach", "false"), ("gc.autoDetach", "false")):
        _git(destination, "config", "--local", key, value, run=run)


def reduce_ordered(ordered, directory, keep, *, log_path=None):
    """Member-count interposition after the production order resolver."""
    relative = str(directory)
    kept = list(ordered)[:keep[relative]] if relative in keep else list(ordered)
    if log_path is not None:
        with Path(log_path).open("a") as handle:
            handle.write(json.dumps({"config_dir": relative, "listed": len(ordered), "kept": len(kept),
                                     "kept_configs": [Path(item).name for item in kept]}, sort_keys=True) + "\n")
    return kept


# A standalone runner: only the result of apply_order_manifest is reduced.
REDUCED_RUNNER = '''import importlib.util, json, os, sys
from pathlib import Path
script = Path(sys.argv[1]).resolve()
root = script.parent.parent
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location("b6_smoke_campaign", script)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from joulewise.b6.smoke import reduce_ordered
original = module.apply_order_manifest
keep = json.loads(os.environ["JW_B6_SMOKE_KEEP"])
def apply_order_manifest(configs, order_entries):
    ordered = original(configs, order_entries)
    if not ordered:
        return ordered
    directory = Path(ordered[0]).resolve().parent.relative_to(root).as_posix()
    return reduce_ordered(ordered, directory, keep, log_path=os.environ["JW_B6_SMOKE_REDUCTION_LOG"])
module.apply_order_manifest = apply_order_manifest
sys.argv = [str(script), *sys.argv[2:]]
raise SystemExit(module.main())
'''


def wrapper_text(real_python, runner, keep, log_path):
    return ('#!/bin/sh\n'
            f'export JW_B6_SMOKE_KEEP={shlex.quote(json.dumps(keep))}\n'
            f'export JW_B6_SMOKE_REDUCTION_LOG={shlex.quote(str(log_path))}\n'
            'case "$1" in\n'
            f'  */scripts/run_campaign.py) exec {shlex.quote(str(real_python))} -B {shlex.quote(str(runner))} "$@";;\n'
            'esac\n'
            f'exec {shlex.quote(str(real_python))} "$@"\n')


def write_wrapper(measurement, claim_measurement_root, smoke_dir, keep, *, run=subprocess.run,
                  python="/opt/homebrew/bin/python3.13"):
    venv = Path(measurement) / ".venv"
    run([python, "-m", "venv", "--without-pip", str(venv)], check=True, timeout=120)
    sites = list((venv / "lib").glob("python*/site-packages"))
    claim_sites = list((Path(claim_measurement_root) / ".venv/lib").glob("python*/site-packages"))
    if len(sites) != 1 or len(claim_sites) != 1:
        raise SmokePrepareError("measurement venv site-packages cannot be resolved uniquely")
    (sites[0] / "smoke_session_packages.pth").write_text(str(claim_sites[0].resolve()) + "\n")
    runner = Path(smoke_dir) / "run_campaign_reduced.py"
    runner.write_text(REDUCED_RUNNER)
    # Preserve the clone's own venv interpreter so sys.prefix and .pth apply.
    real_python = venv / "bin/python3.13"
    wrapper = venv / "bin/python"
    wrapper.unlink()
    wrapper.write_text(wrapper_text(real_python, runner, keep, Path(smoke_dir) / "reduction.jsonl"))
    wrapper.chmod(0o755)


@dataclasses.dataclass(frozen=True)
class SmokePrepared:
    smoke_dir: Path
    measurement: Path
    plan_path: Path
    custody: Path
    state_root: Path
    pack_id: str
    bracket_session_id: str
    fingerprint: dict
    keep: dict
    registration_dir: Path

    def to_json(self):
        return {field.name: str(getattr(self, field.name)) if isinstance(getattr(self, field.name), Path)
                else getattr(self, field.name) for field in dataclasses.fields(self)}

    @classmethod
    def from_json(cls, value):
        fields = {field.name: value[field.name] for field in dataclasses.fields(cls)}
        for key in ("smoke_dir", "measurement", "plan_path", "custody", "state_root", "registration_dir"):
            fields[key] = Path(fields[key])
        return cls(**fields)


def prepare(pack_id, code_commit, claim_measurement_root, smoke_root, *, plan_inputs=None,
            fp=None, state_root=None, now=None, run=subprocess.run, plan_writer=plan.write_window_plan,
            wrapper_writer=write_wrapper, registration_dir=None, defer_plan=False, keep=None):
    """Plan inputs carry the session's registered sizing, thresholds and identities.

    They may be supplied by the loop or read from the checkout's
    configs/b6/smoke_inputs.json; no registration values are invented here.
    """
    claim = Path(claim_measurement_root).resolve()
    inputs = copy.deepcopy(plan_inputs if plan_inputs is not None else json.loads(
        (claim / "configs/b6/smoke_inputs.json").read_text()))
    fp = fp if fp is not None else inputs.pop("fingerprint", None)
    if fp is None:
        raise SmokePrepareError("prepare requires the precheck fingerprint")
    when = now or dt.datetime.now(dt.timezone.utc)
    stamp = when.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%MZ")
    smoke_dir = (Path(smoke_root) / f"{pack_id}-{stamp}").resolve()
    smoke_dir.mkdir(parents=True, exist_ok=False)
    measurement = smoke_dir / "measurement"
    clone_checkout(claim, code_commit, measurement, run=run)
    copy_ledger(claim, measurement, smoke_dir)
    _git(measurement, "add", plan.HEAD_PIN_RELATIVE, run=run)
    _git(measurement, "-c", "user.name=B6 Smoke", "-c", "user.email=smoke@invalid",
         "commit", "--quiet", "--allow-empty", "-m", "SMOKE ledger pin copy", run=run)
    keep = dict(keep) if keep is not None else compose.registered_smoke_keep(pack_id, path=KEEP_PATH)
    pack_root = measurement / "configs/campaigns" / pack_id
    tree = json.loads((pack_root / "plan_tree.json").read_text())
    keeps = config_keeps(tree, keep)
    reduced = reduce_tree(tree, keep)
    (pack_root / "plan_tree.json").write_text(json.dumps(reduced, indent=2) + "\n")
    # Readiness authenticates exact bytes, not the parsed tree. Commit its
    # authenticator in the same clone commit before the plan writer binds both
    # the tree digest and the committed pack digest.
    (pack_root / "plan_tree.sha256").write_text(_sha256(pack_root / "plan_tree.json")
                                               + "  plan_tree.json\n")
    _git(measurement, "add", *(str(pack_root.relative_to(measurement) / name)
                              for name in ("plan_tree.json", "plan_tree.sha256")), run=run)
    _git(measurement, "-c", "user.name=B6 Smoke", "-c", "user.email=smoke@invalid",
         "commit", "--quiet", "-m", "SMOKE reduced stage tree", run=run)
    wrapper_writer(measurement, claim, smoke_dir, keeps, run=run)
    tag = f"SMOKE-{pack_id}-{stamp}"
    for key in ("identity_epoch_json", "t1_bindings_json"):
        source = Path(inputs[key]["path"])
        dest = smoke_dir / "inputs" / source.name
        dest.parent.mkdir(exist_ok=True)
        shutil.copy2(source, dest)
        inputs[key] = {"path": str(dest), "sha256": _sha256(dest)}
    inputs.update(plan_id=tag, bracket_session_id=tag + "-calibration", pre_attempt_id=tag + "-pre",
                  post_attempt_id=tag + "-post", measurement_root=str(measurement), pack_root=str(pack_root),
                  measurement_head=_git(measurement, "rev-parse", "HEAD", run=run), repo_head=code_commit,
                  custody_root=str(smoke_dir / "custody"), runs_parent=str(smoke_dir / "runs-parent"),
                  claim_backup_destination=str(smoke_dir / "backup-claim"),
                  bound_backup_destination=str(smoke_dir / "backup-bound"),
                  ledger_path=str(measurement / plan.DEFAULT_LEDGER_RELATIVE))
    Path(inputs["runs_parent"]).mkdir()
    record = {"plan": {"path": str(Path(inputs["custody_root"]) / plan.PLAN_BASENAME)}} if defer_plan else plan_writer(inputs)
    # The block-6 registration directory of the smoke's own clone (stage-1
    # integration), unless the caller names one (a non-claim machine test).
    from joulewise.b6.registration import DEFAULT_DIR_RELATIVE
    registration = Path(registration_dir).resolve() if registration_dir else measurement / DEFAULT_DIR_RELATIVE
    prepared = SmokePrepared(smoke_dir, measurement, Path(record["plan"]["path"]), Path(inputs["custody_root"]),
                             Path(state_root or Path(smoke_root).parent).resolve(), pack_id,
                             inputs["bracket_session_id"], fp, keep, registration)
    bin_dir = smoke_dir / "bin"
    bin_dir.mkdir()
    courier = bin_dir / "smoke-courier"
    # Exercise the session's mail-free program and its courier.sent protocol.
    courier.write_text('#!/bin/sh\nexec /bin/sh '
                       + shlex.quote(str(measurement / "scripts/b6_courier.sh")) + ' "$@"\n')
    courier.chmod(0o755)
    write_create_once(smoke_dir / "smoke-state.json", canonical_json(
        {**prepared.to_json(), "driver_argv": driver_argv(prepared), "config_keep": keeps,
         "plan_inputs": inputs}) + b"\n")
    return prepared


def driver_argv(prepared):
    return [str(prepared.measurement / ".venv/bin/python"), str(prepared.measurement / "scripts/run_night.py"),
            "run", "--plan", str(prepared.plan_path), "--courier-bin", str(prepared.smoke_dir / "bin/smoke-courier")]


def _harvest_hooks():
    if importlib.util.find_spec("joulewise.b6.acceptance") is None:
        return None, _is_physical
    module = importlib.import_module("joulewise.b6.acceptance")
    return getattr(module, "evidence_from_archive", None), getattr(module, "is_physical", _is_physical)


def _session_desk():
    """The harvest lane's archive acceptance (joulewise.b6.session.accept_archive), if present."""
    if importlib.util.find_spec("joulewise.b6.session") is None:
        return None
    return importlib.import_module("joulewise.b6.session").accept_archive


def _is_physical(code):
    try:
        codes = json.loads(CATALOG_PATH.read_text())["codes"]
        if code in codes:
            row = codes[code]
            return row["klass"] == "PHYSICS" and row["effect"] in {"EXCLUDE_MEMBER", "EXCLUDE_WINDOW"}
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return code.startswith(PHYSICAL_PREFIXES)


def _flag_codes(value):
    if isinstance(value, dict):
        if isinstance(value.get("code"), str):
            yield value["code"]
        if isinstance(value.get("by_code"), dict):
            yield from (code for code, count in value["by_code"].items() if count)
        for key, item in value.items():
            if key in ("flags", "findings", "refusals", "would_refuse", "reasons", "arm", "verdict", "monitor",
                       "flags_emitted"):
                yield from _flag_codes(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _flag_codes(item)
    elif isinstance(value, str) and re.fullmatch(r"[a-z0-9_]+(\.[a-z0-9_]+)+", value):
        yield value


def stages_succeeded(stage_results, *, tree, repo_root, evidence):
    """Explain campaign exit 1 only from the exact dispatched members' losses.

    The campaign returns 1 for unsuccessful members. Other exits, unresolved
    dispatches, missing records and any other failed member remain stage faults.
    """
    from joulewise.b6.acceptance import recorded_wait_cap_skip

    dispatches = {row.stage_id: row for row in plan.resolve_stage_dispatches(tree, repo_root)}
    stages = {stage.stage_id: stage for stage in evidence.stages}
    graph = {stage["stage_id"]: stage for stage in tree["stage_graph"]}
    for result in stage_results:
        if result["rc"] in result["success_exit_codes"]:
            continue
        stage_id = result["stage_id"]
        dispatch, stage = dispatches.get(stage_id), stages.get(stage_id)
        run_ids = dispatch.run_ids if dispatch is not None else None
        expected = graph.get(stage_id, {}).get("expected_count")
        # The smoke runner applies this registered prefix after ordering; its
        # copied order manifests deliberately retain the full campaign order.
        reduction = tree.get("smoke_reduction") or {}
        if (run_ids and reduction.get("schema") == REDUCTION_SCHEMA
                and reduction.get("keep", {}).get(stage_id) == expected):
            run_ids = run_ids[:expected]
        if (result["rc"] != 1 or dispatch is None or dispatch.error or stage is None
                or not run_ids or len(run_ids) != expected
                or len(set(run_ids)) != len(run_ids)
                or len(stage.members) != len(run_ids)
                or {m.run_id for m in stage.members} != set(run_ids)):
            return False
        skipped = [m for m in stage.members if m.status != "succeeded"]
        if not skipped or not all(m.status == "failed" and recorded_wait_cap_skip(m) for m in skipped):
            return False
    return True


def classify(*, stages_ok, driver_exit, harvest_exit, acceptance_result, flags, is_physical=None,
             physical_arm_refusal=False, bundles_produced=False):
    # Retain the keyword for callers; bundle existence cannot explain a crash.
    physical = is_physical or _is_physical
    # A chance member flag cannot explain a failed stage or harvest, even
    # after earlier bundles. Only a named stop or arm refusal explains it.
    # Smoke acceptance uses physics_stop for incidental member exclusions too;
    # physical_stop_kind identifies an actual physical chain stop.
    # Harvest exit 6 is "registration pending" (queue.outcome), not a fault.
    if not stages_ok or harvest_exit not in (0, 6):
        return "physics" if physical_arm_refusal or acceptance_result.record.get("physical_stop_kind") else "fail"
    if acceptance_result.structural:
        return "fail"
    if physical_arm_refusal or acceptance_result.record.get("physics_stop") or any(physical(code) for code in flags):
        return "physics"
    if stages_ok and driver_exit in (0, 6) and harvest_exit in (0, 6) and not acceptance_result.structural:
        return "pass"
    return "fail"


def desk(prepared, *, driver_exit=None, run=subprocess.run, acceptance=None,
         advance_pin=plan.advance_ledger_pin, evidence_loader=None, is_physical=None):
    night = prepared.custody / "night"
    tree = json.loads((prepared.measurement / "configs/campaigns" /
                       prepared.pack_id / "plan_tree.json").read_text())
    stages = chain.stage_plan(tree)
    journal = {row["stage_id"]: row for row in chain.stage_journal(night)}
    stage_results = [{"stage_id": stage.stage_id, "rc": journal.get(stage.stage_id, {}).get("rc"),
                      "success_exit_codes": list(stage.commands[0].success_exit_codes)}
                     for stage in stages if stage.in_chain]
    stages_ok = all(row["rc"] in row["success_exit_codes"] for row in stage_results)
    hazard = {}
    result_record = {}
    for path, target in ((night / "hazard_result.json", hazard), (night / "result.json", result_record)):
        try:
            target.update(json.loads(path.read_text()))
        except (OSError, ValueError, TypeError):
            pass
    if driver_exit is None:
        driver_exit = result_record.get("exit_code", hazard.get("driver_exit_code"))
        if driver_exit is None:
            try:
                courier = json.loads((night / "courier.json").read_text())
            except (OSError, ValueError):
                courier = {}
            if courier.get("sent") is False:
                driver_exit = 6
            elif (courier.get("sent") is True and result_record.get("verdict") == "GO"
                  and result_record.get("chain_exit_code") == 0):
                driver_exit = 0
    errors = []
    record_flags = []
    try:
        advance_pin(prepared.measurement, session_id=prepared.bracket_session_id,
                    operator_identity="b6-smoke-desk", attestation_reason="non-claim smoke chain exited")
    except Exception as exc:
        record_flags.append("records.pin_ledger")
    archive = prepared.smoke_dir / "archive"
    argv = [str(prepared.measurement / ".venv/bin/python"),
            *(str(prepared.measurement / item) if index == 0 else item for index, item in enumerate(HARVEST_ARGV)),
            "--plan", str(prepared.plan_path), "--archive-root", str(archive),
            "--registration-dir", str(prepared.registration_dir),
            "--pack-records-root", str(prepared.state_root / "packs"),
            "--export-dir", str(prepared.smoke_dir / "export"), "--smoke"]
    harvest_exit = None
    try:
        harvest_exit = run(argv, check=False).returncode
    except OSError as exc:
        errors.append(f"harvest: {exc}")
    loader, physical = _harvest_hooks()
    physical = is_physical or physical
    try:
        if acceptance is None and evidence_loader is None:
            record = json.loads((archive / "derived/b6-acceptance.json").read_text())
            window_exclusions = [item["code"] for item in record.get("excluding", [])
                                 if item.get("scope") == "window"]
            structural = bool(record.get("structural_failures")) or any(
                not physical(code) for code in window_exclusions)
            a_result = AcceptanceResult(record["verdict"],
                tuple(sorted(set(window_exclusions))), tuple(record["flag_counts"]), structural,
                record.get("counting", False), record)
        else:
            loader = evidence_loader or loader
            acceptance = acceptance or load_acceptance()
            if loader and harvest_exit == 0:
                evidence = loader(archive) if evidence_loader else loader(
                    archive, Path(prepared.plan_path), prepared.registration_dir)
            else:
                evidence = SessionEvidence(prepared.pack_id, (), (), {}, False, ())
            prepared_a = acceptance.prepare(ledger_path=prepared.measurement / plan.DEFAULT_LEDGER_RELATIVE,
                                            plan_tree=json.loads((prepared.measurement / "configs/campaigns" /
                                                                  prepared.pack_id / "plan_tree.json").read_text()),
                                            registration_dir=prepared.registration_dir, code_identity=prepared.fingerprint,
                                            pack_root=prepared.measurement / "configs/campaigns" / prepared.pack_id)
            a_result = acceptance.evaluate(prepared_a, evidence)
        if not stages_ok and "idle.wait_cap_skip" in a_result.flags and loader and harvest_exit in (0, 6):
            stage_evidence = loader(archive) if evidence_loader else loader(
                archive, Path(prepared.plan_path), prepared.registration_dir)
            stages_ok = stages_succeeded(stage_results, tree=tree, repo_root=prepared.measurement,
                                         evidence=stage_evidence)
    except Exception as exc:
        errors.append(f"acceptance: {type(exc).__name__}: {exc}")
        a_result = AcceptanceResult("UNAVAILABLE", ("acceptance failed",), (), True)
    flags = record_flags + list(_flag_codes(hazard)) + list(a_result.flags)
    arm_record = hazard.get("arm") or {}
    physical_arm_refusal = arm_record.get("go") is False and any(
        str(reason).startswith("agent census") for reason in arm_record.get("reasons", []))
    for module, verdict in (arm_record.get("verdicts") or {}).items():
        status = verdict.get("status") if isinstance(verdict, dict) else verdict
        measured_refusal = status == "REFUSE" or (status == "UNMEASURED" and any(
            str(reason).startswith(module + " ") for reason in arm_record.get("reasons", [])))
        if arm_record.get("go") is False and measured_refusal:
            flags.append(f"{module}.arm_refusal")
            physical_arm_refusal |= physical(f"{module}.arm_refusal")
    for report_path in (archive / "harvest-report.json", archive / "harvest.json",
                        archive / "derived/window_flags.json"):
        try:
            flags.extend(_flag_codes(json.loads(report_path.read_text())))
        except (OSError, ValueError):
            pass
    try:
        for line in (archive / "derived/flags.jsonl").read_text().splitlines():
            flags.extend(_flag_codes(json.loads(line)))
    except (OSError, ValueError):
        pass
    status = classify(stages_ok=stages_ok and not errors, driver_exit=driver_exit,
                      harvest_exit=harvest_exit, acceptance_result=a_result, flags=flags, is_physical=physical,
                      physical_arm_refusal=physical_arm_refusal)
    report = {"schema": "joulewise.b6_smoke_result.v1", "status": status, "pack_id": prepared.pack_id,
              "stages": stage_results, "driver_exit": driver_exit, "harvest_exit": harvest_exit,
              "acceptance": dataclasses.asdict(a_result), "flags": flags, "errors": errors,
              "driver_reason": "courier_failed_but_collected" if driver_exit == 6 else "driver_exit",
              "archive": str(archive)}
    target = prepared.smoke_dir / "smoke-result.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_bytes(canonical_json(report) + b"\n")
    temporary.replace(target)
    if status == "pass":
        fingerprint.record_pass(prepared.fingerprint, prepared.smoke_dir, prepared.state_root / "smoke-passes.jsonl")
    return report
