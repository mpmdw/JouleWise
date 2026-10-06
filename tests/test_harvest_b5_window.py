"""Lane L5: the block-5 harvest emits numbers plus flags and never refuses on data.

Real code runs unpatched throughout: strict validation, re-reduction, anchor
re-derivation from the raw plist, the calibration ledger and bracket evaluator,
battery-pair authentication, the pack/code/model replays and the monitor joins.
Fakes stand only at the seams the plan names: the hazard-monitor journals (L1,
written here as JSON lines), the exclusion function (L4), the process-group
probe, and the subprocess runner for G3 and the desk producer.

Members are clones of the committed strict-valid seed bundle
(tests/fixtures/d117_v2_production/strict_seed_bundle).  Each clone gets its
own run id and its own monotonic span: the clock stamps are shifted and the
clock-anchor evidence is re-derived from the unchanged raw plist, so every
clone stays strict-valid.
"""
from __future__ import annotations

import base64
import contextlib
import copy
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.adapters.powermetrics import (
    RAW_SAMPLES_NAME, anchor_records_from_powermetrics, parse_powermetrics_records)
from joulewise.b5 import harvest as h
from joulewise.calibration_ledger import (
    GENESIS_DIGEST, IDENTITY_EPOCH_FIELDS, LEDGER_SCHEMA, append_bracket_session_receipt, artifact_hashes,
    finalize_bracket_session_slot, load_calibration_ledger_snapshot)
from joulewise.identity_pins import derive_model_runtime_config_from_metadata
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from joulewise.schemas import BenchmarkConfig
from joulewise.uncertainty_evidence import resolve_clock_evidence_deriver, stamp_from_mapping

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "tests/fixtures/d117_v2_production/strict_seed_bundle"
FIXTURES = ROOT / "tests/fixtures/b5_harvest"
PREFIX = ROOT / "tests/fixtures/v5_qualification_harvest/acceptance-prefix-376.jsonl.zlib.b85"
ACCEPTANCE = "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json"
POLICY = "configs/campaign_policies/quiet_mac_p2_production.json"
B3W1 = Path("/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2")
REAL_TMP = os.path.realpath(tempfile.gettempdir())

PACK_ID = "b5test_floor_v5"
PLAN_ID = "plan-b5test-floor-v5"
EVIDENCE_ROOT_ID = "evidence-b5test-floor-v5"
SESSION_ID = "b5t-session"
FAMILY = "df-b5t-family"
H_CLAIM = "a" * 40
MEMBERS = (
    # run_id, role, block, position, arm, config subdirectory
    ("b5t-abs-r01", "absolute_repeat", None, None, None, "01_abs"),
    ("b5t-abs-r02", "absolute_repeat", None, None, None, "01_abs"),
    ("b5t-cmp-b01-a1", "comparative_abba_member", "b5t-b01", "A1", "A", "02_abba"),
    ("b5t-cmp-b01-b1", "comparative_abba_member", "b5t-b01", "B1", "B", "02_abba"),
    ("b5t-cmp-b01-b2", "comparative_abba_member", "b5t-b01", "B2", "B", "02_abba"),
    ("b5t-cmp-b01-a2", "comparative_abba_member", "b5t-b01", "A2", "A", "02_abba"),
)
QUAD = [row[0] for row in MEMBERS if row[2] == "b5t-b01"]
SHIFT_S = {row[0]: 1000.0 * (index + 1) for index, row in enumerate(MEMBERS)}
# The seed's sampler stream, from its pre_spawn and post_parse clock stamps.
SEED_STREAM_S = (1487916.588365625, 1487921.314305041)
SEED_REQUEST_S = (1487919.701423916, 1487919.860664583)
RAW_OFFSET_NS = 7_000_000_000
WALL_OFFSET_S = 1786206671.102036 - 1487916.588365625
GIB = 2**30


def member_span_ns(run_id: str) -> tuple[int, int]:
    shift = SHIFT_S[run_id]
    return (math.floor((SEED_STREAM_S[0] + shift) * 1e9), math.floor((SEED_STREAM_S[1] + shift) * 1e9))


def request_span_ns(run_id: str) -> tuple[int, int]:
    shift = SHIFT_S[run_id]
    return (math.floor((SEED_REQUEST_S[0] + shift) * 1e9), math.floor((SEED_REQUEST_S[1] + shift) * 1e9))


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path: Path, value) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return raw


def normalized_config(config: dict) -> bytes:
    return (json.dumps(BenchmarkConfig.from_mapping(config).to_dict(), indent=2, sort_keys=True) + "\n").encode()


# ---------------------------------------------------------------------------
# Member template: built once per module.
# ---------------------------------------------------------------------------

_TEMPLATE: Path | None = None


def make_member(target: Path, run_id: str, shift_s: float) -> None:
    shutil.copytree(SEED, target)
    config = json.loads((target / "config.json").read_bytes())
    config["run_id"] = run_id
    config["run_metadata"]["tags"] = [*config["run_metadata"]["tags"], f"df-condition={FAMILY}"]
    raw_config = normalized_config(config)
    (target / "config.json").write_bytes(raw_config)
    metadata = json.loads((target / "metadata.json").read_bytes())
    metadata["run_id"] = run_id
    metadata["config_sha256"] = hashlib.sha256(raw_config).hexdigest()
    metadata["workload_provenance"]["sampler"] = {"name": "greedy", "temperature": 0.0}
    anchor = metadata["uncertainty_evidence"]["clock_anchor"]
    for stamp in anchor["clock_stamps"].values():
        stamp["monotonic_before_s"] += shift_s
        stamp["monotonic_after_s"] += shift_s
    stamps = {name: stamp_from_mapping(value) for name, value in anchor["clock_stamps"].items()}
    records = parse_powermetrics_records((target / "raw" / RAW_SAMPLES_NAME).read_bytes())
    expected, _point = resolve_clock_evidence_deriver(anchor["method"])(
        stamps=stamps, records=anchor_records_from_powermetrics(records))
    metadata["uncertainty_evidence"]["clock_anchor"] = expected["clock_anchor"]
    metadata["uncertainty_evidence"]["sample_phase"] = expected["sample_phase"]
    put(target / "metadata.json", metadata)
    events = (target / "events.jsonl").read_text().replace('"run_id": "seed"', f'"run_id": "{run_id}"')
    (target / "events.jsonl").write_text(events)


def template() -> Path:
    global _TEMPLATE
    if _TEMPLATE is None:
        root = Path(tempfile.mkdtemp(prefix="b5-harvest-template-", dir=REAL_TMP))
        for run_id, *_rest in MEMBERS:
            make_member(root / run_id, run_id, SHIFT_S[run_id])
        _TEMPLATE = root
    return _TEMPLATE


def tearDownModule():  # noqa: N802 (unittest hook)
    if _TEMPLATE is not None:
        shutil.rmtree(_TEMPLATE, ignore_errors=True)


# ---------------------------------------------------------------------------
# Synthetic hazard-monitor journals (the L1 seam).
# ---------------------------------------------------------------------------

def _line(module: str, mono_ns: int, values: dict) -> dict:
    return {"module": module, "monotonic_ns": mono_ns, "monotonic_raw_ns": mono_ns + RAW_OFFSET_NS,
            "wall_s": mono_ns / 1e9 + WALL_OFFSET_S, "values": values, "raw": []}


def clean_battery(**override) -> dict:
    return {"ExternalConnected": "Yes", "IsCharging": "No", "InstantAmperage": 0, "Amperage": 0,
            "Voltage": 12180, **override}


def write_journals(directory: Path, *, extra_publications=(), thermal_levels=(), contention_extra=(),
                   clock_steps=(), omit=(), battery_gap=None, contention_gap=None, disk_low=False) -> None:
    """Every module from 300 s before the first member to 300 s after the last."""
    directory.mkdir(parents=True, exist_ok=True)
    spans = [member_span_ns(row[0]) for row in MEMBERS]
    # An odd offset keeps the journal's sampling grid off every span edge.
    start, end = spans[0][0] - 300 * 10**9 - 1_234_567, spans[-1][1] + 300 * 10**9
    step5, step10, step60 = 5 * 10**9, 10 * 10**9, 60 * 10**9
    rows: dict[str, list[dict]] = {name: [] for name in ("battery", "thermal", "contention", "clock", "disk")}
    publications = [(stamp, clean_battery()) for stamp in range(start, end, step60)]
    publications += [(stamp, clean_battery(**values)) for stamp, values in extra_publications]
    if battery_gap is not None:
        publications = [(stamp, values) for stamp, values in publications
                        if not battery_gap[0] <= stamp <= battery_gap[1]]
    publications.sort(key=lambda item: item[0])
    for poll in range(start, end, step5):
        current = [item for item in publications if item[0] <= poll]
        if not current:
            continue
        stamp, values = current[-1]
        if battery_gap is not None and battery_gap[0] <= poll <= battery_gap[1]:
            continue
        rows["battery"].append(_line("battery", poll, {**values, "UpdateTime": int(stamp / 1e9 + WALL_OFFSET_S)}))
    levels = dict(thermal_levels)
    for poll in range(start, end, step5):
        level = next((value for (lo, hi), value in levels.items() if lo <= poll <= hi), 0)
        rows["thermal"].append(_line("thermal", poll, {"level": level}))
    extra = list(contention_extra)
    for begin in range(start, end, step10):
        if contention_gap is not None and begin < contention_gap[1] and contention_gap[0] < begin + step10:
            continue
        processes = [{"pid": 0, "comm": "kernel_task", "cpu_s_per_s": 0.31, "outside": True},
                     {"pid": 88, "comm": "WindowServer", "cpu_s_per_s": 0.01, "outside": True},
                     {"pid": 4242, "comm": "python3.13", "cpu_s_per_s": 0.97, "in_measurement_tree": True}]
        processes += [row for (lo, hi), row in extra if lo < begin + step10 and begin < hi]
        rows["contention"].append({**_line("contention", begin + step10, {"processes": processes}),
                                   "interval": {"monotonic_ns": [begin, begin + step10]}})
    anchor0 = 1_784_718_754_513_670_000
    offset = 0
    steps = sorted(clock_steps)
    for poll in range(start, end, step5):
        offset = sum(size for at, size in steps if at <= poll)
        raw = poll + RAW_OFFSET_NS
        anchor = anchor0 + round(-3.17e-6 * (raw - start - RAW_OFFSET_NS)) + offset
        rows["clock"].append(_line("clock", poll, {"anchor_ns": anchor, "ppm": -3.17}))
    for poll in range(start, end, step60):
        rows["disk"].append(_line("disk", poll, {"free_bytes": (5 if disk_low else 200) * GIB}))
    for name, lines in rows.items():
        if name in omit:
            continue
        (directory / f"{name}.jsonl").write_text("".join(json.dumps(line, sort_keys=True) + "\n" for line in lines))


# ---------------------------------------------------------------------------
# One synthetic window: measurement checkout, pack, ledger, custody, plan.
# ---------------------------------------------------------------------------

def fake_exclusions(flags, roster, spans, catalog):
    """A stand-in for L4's exclusions.compute: catalog effects, quad rule, 8-of-10 minimum."""
    excluded: dict[str, set] = {}
    window = set()
    for flag in flags:
        effect = catalog.effect(flag["code"])
        if effect == "EXCLUDE_WINDOW":
            window.add(flag["code"])
        elif effect == "EXCLUDE_MEMBER" and flag["scope"].get("run_id"):
            excluded.setdefault(flag["scope"]["run_id"], set()).add(flag["code"])
    units: dict[str, dict[tuple, set]] = {}
    for member in roster["members"]:
        for cell in member["cells"]:
            units.setdefault(cell["cell_id"], {}).setdefault((cell["unit_kind"], cell["unit_id"]), set()).add(
                member["run_id"])
    dropped = {run_id: set(codes) for run_id, codes in excluded.items()}
    cells = []
    for cell_id, cell_units in sorted(units.items()):
        kept = {key: members for key, members in cell_units.items() if not members & set(excluded)}
        for key, members in cell_units.items():
            if key[0] == "quad" and members & set(excluded):
                for run_id in members:
                    dropped.setdefault(run_id, set()).add("quad.member_flagged")
        planned = {kind: sum(key[0] == kind for key in cell_units) for kind in ("repeat", "quad")}
        n = {kind: sum(key[0] == kind for key in kept) for kind in ("repeat", "quad")}
        resolvable = all(n[kind] >= math.ceil(0.8 * planned[kind]) for kind in planned)
        cells.append({"cell_id": cell_id, "n_repeats": n["repeat"], "n_quads": n["quad"], "resolvable": resolvable})
        if not resolvable:
            window.add("cell.below_minimum")
    return {"members_excluded": [{"run_id": run_id, "codes": sorted(codes)} for run_id, codes in sorted(dropped.items())],
            "cells": cells, "claim_usable": not window, "reasons": sorted(window)}


class Window:
    def __init__(self, root: Path, *, prefix_ledger=False, target_precheck=None, catalog_overrides=None,
                 journals=None, executed_overrides=None, frozen_pins=True, register_prompt_tokens=32):
        self.root = root
        self.measurement = root / "measurement"
        self.pack = self.measurement / "configs" / "campaigns" / PACK_ID
        self.custody = root / "custody"
        self.claim = self.custody / "runs_claim"
        self.bound = self.custody / "runs_bound"
        self.archive = root / "archive"
        self.ledger = self.measurement / "runs" / "calibration_observation_ledger.jsonl"
        self.pin = self.measurement / "configs" / "calibration" / "calibration_ledger_head.json"
        self.plan_path = self.custody / "night_plan.json"
        self._build_repo(target_precheck, register_prompt_tokens, frozen_pins)
        self._build_catalog(catalog_overrides or {})
        self._build_runs()
        self._build_ledger(prefix_ledger)
        self._build_night(executed_overrides or {})
        write_journals(self.custody / "hazards" / "monitor", **(journals or {}))

    # -- measurement checkout and pack -------------------------------------
    def _build_repo(self, target_precheck, register_prompt_tokens, frozen_pins):
        for relative in (POLICY, ACCEPTANCE):
            target = self.measurement / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        for relative in ("joulewise/b5t_stub.py", "scripts/b5t_stub.py"):
            target = self.measurement / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"# {relative}\n")
        plan = put(self.pack / "calibration_plan.json", {"plan_id": PLAN_ID, "kind": "b5-test-calibration-plan"})
        science, inventory = [], []
        for ordinal, (run_id, role, block, position, arm, subdir) in enumerate(MEMBERS, 1):
            config_raw = (template() / run_id / "config.json").read_bytes()
            relative = f"{subdir}/{run_id}.json"
            (self.pack / subdir).mkdir(parents=True, exist_ok=True)
            (self.pack / relative).write_bytes(config_raw)
            digest = hashlib.sha256(config_raw).hexdigest()
            science.append({"ordinal": ordinal, "stage_id": subdir, "run_id": run_id, "role": role,
                            "config_path": f"configs/campaigns/{PACK_ID}/{relative}", "config_sha256": digest,
                            "block_id": block, "block_index": 1 if block else ordinal, "position": position,
                            "arm": arm})
            inventory.append({"path": relative, "sha256": digest})
        family = {"all": {"condition_family_definition": {
            "condition_family_id": FAMILY,
            "workload_profile": {"prompt_tokens": register_prompt_tokens, "output_tokens": 8}}}}
        spec = {"schema_version": "joulewise.detection_floor_extraction_spec.v1", "cells": [
            {"cell_id": "b5t-abs", "kind": "absolute", "metric": "phase_energy_j.decode",
             "target_precheck_path": target_precheck, "condition_family_id": FAMILY, "expected_n": 2,
             "condition_family_definitions": family,
             "members": [{"slot": row[0], "bundle_id": row[0]} for row in MEMBERS if row[2] is None]},
            {"cell_id": "b5t-cmp", "kind": "comparative", "metric": "phase_energy_j.decode",
             "target_precheck_path": target_precheck, "condition_family_id": FAMILY, "expected_n": 1,
             "condition_family_definitions": family,
             "blocks": [{"block_id": "b5t-b01", "members": {row[3]: row[0] for row in MEMBERS if row[2]}}]}]}
        put(self.pack / "extraction_spec.json", spec)
        identity = derive_model_runtime_config_from_metadata(
            json.loads((template() / MEMBERS[0][0] / "config.json").read_bytes()),
            json.loads((template() / MEMBERS[0][0] / "metadata.json").read_bytes()))[1]
        tree = {
            "schema_version": "b5-test-plan-tree",
            "plan": {"path": "calibration_plan.json", "plan_id": PLAN_ID,
                     "actual_sha256": hashlib.sha256(plan).hexdigest(),
                     "declared_sha256": hashlib.sha256(plan).hexdigest()},
            "window_identity": {"window_id": PLAN_ID, "evidence_root_id": EVIDENCE_ROOT_ID},
            "campaign_policy": {"path": POLICY, "sha256": sha(ROOT / POLICY)},
            "acceptance_policy": {"issued_acceptance": {"path": ACCEPTANCE, "artifact_sha256": sha(ROOT / ACCEPTANCE)}},
            "science": science,
            "external_inputs": {"manifests": [], "artifacts": []},
            "arm_attachments": {"identity_pin_projection": {"identity_units": [{
                "identity_unit_id": "b5t-unit", "config_inventory": inventory,
                "model_runtime_config": {
                    "model_artifact_sha256": identity["model_artifact_sha256"] if frozen_pins else None,
                    "runtime_identity_sha256": identity["runtime_identity_sha256"] if frozen_pins else None,
                    "config_set_sha256": None}}]}},
            "downstream_contract": {"extraction_spec": {
                "path": f"configs/campaigns/{PACK_ID}/extraction_spec.json",
                "sha256": sha(self.pack / "extraction_spec.json")}},
        }
        put(self.pack / "plan_tree.json", tree)
        (self.pack / "plan_tree.sha256").write_text(f"{sha(self.pack / 'plan_tree.json')}  plan_tree.json\n")
        files = {path.relative_to(self.measurement).as_posix(): sha(path)
                 for path in sorted(self.measurement.rglob("*")) if path.is_file()}
        self.sealed_files = files
        put(self.measurement / "configs/campaigns/v5_claim_25g83/sealed_inventory.json",
            {"head": H_CLAIM, "files": files})

    def _build_catalog(self, overrides):
        catalog = json.loads((FIXTURES / "flag_catalog.json").read_bytes())
        for code, effect in overrides.items():
            catalog["codes"][code]["effect"] = effect
        put(self.measurement / "configs/campaigns/v5_claim_25g83/flag_catalog.json", catalog)

    # -- runs roots ----------------------------------------------------------
    def _build_runs(self):
        self.claim.mkdir(parents=True)
        self.bound.mkdir(parents=True)
        for run_id, *_rest in MEMBERS:
            subprocess.run(["/bin/cp", "-c", "-R", str(template() / run_id), str(self.claim / run_id)], check=True)

    def _build_ledger(self, prefix_ledger):
        from joulewise.calibration_bracketing import load_calibration_acceptance_bound
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        if prefix_ledger:
            self.ledger.write_bytes(zlib.decompress(base64.b85decode(PREFIX.read_bytes())))
            cutoff = load_calibration_acceptance_bound(ROOT / ACCEPTANCE)["ledger_cutoff"]
            put(self.pin, {"sequence": cutoff["sequence"], "head_digest": cutoff["head_digest"],
                           "ledger_schema": LEDGER_SCHEMA})
        else:
            self.ledger.write_bytes(b"")
            put(self.pin, {"sequence": 0, "head_digest": GENESIS_DIGEST, "ledger_schema": LEDGER_SCHEMA})
        epoch = dict(zip(IDENTITY_EPOCH_FIELDS, ("25F84", "Mac15,9", "ac_high_power", 100, "estimator-v1",
                                                 "pulse-v3"), strict=True))
        t1 = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        t1.update(epoch)
        slots = {}
        for slot in ("pre", "post"):
            capture = self.claim / "instrument_validation" / f"{SESSION_ID}-{slot}"
            (capture / "raw").mkdir(parents=True)
            (capture / "raw" / "powermetrics.plist").write_bytes(f"raw-{slot}".encode())
            (capture / "events.jsonl").write_text('{"timestamp_s":99.0}\n')
            put(capture / "instrument_evidence.json", {"slot": slot})
            put(capture / "manifest.json", {"slot": slot})
            slots[slot] = {"attempt_id": f"{SESSION_ID}-{slot}", "custody_locator": str(capture),
                           "identity_epoch": epoch, "t1_bindings": t1}
        append_bracket_session_receipt(
            self.ledger, session_id=SESSION_ID, window_id=PLAN_ID, plan_id=PLAN_ID,
            plan_sha256=sha(self.pack / "calibration_plan.json"), evidence_root_id=EVIDENCE_ROOT_ID,
            runs_root=self.claim, slots=slots, head_pin_path=self.pin, require_committed_pin=False)
        for slot in ("pre", "post"):
            capture = Path(slots[slot]["custody_locator"])
            finalize_bracket_session_slot(
                self.ledger, session_id=SESSION_ID, slot=slot, disposition="valid",
                custody_locator=str(capture), artifact_sha256=artifact_hashes(capture), identity_epoch=epoch,
                t1_bindings=t1, capture_wall_time_s="99.0" if slot == "pre" else "111.0",
                exact_bound_lexeme_s="0.025")

    # -- night custody, hazards, plan ------------------------------------------
    def _build_night(self, executed_overrides):
        night = self.custody / "night"
        put(night / "chain.started", {"epoch_s": 1786206000.0, "pgid": 999_999, "pid": 999_999})
        put(night / "chain.exited", {"epoch_s": 1786216000.0, "exit_code": 0, "monotonic_ns": 1})
        put(night / "result.json", {"aborted_reason": None, "artifacts": []})
        chain = self.custody / "chain.zsh"
        chain.write_text("#!/bin/zsh\necho b5 test chain\n")
        (self.custody / "chain.zsh.sha256").write_text(f"{sha(chain)}  chain.zsh\n")
        put(self.custody / "hazards" / "arm.json", {
            "schema": "joulewise.hazard_arm.v1", "verdict": "GO",
            "modules": {name: {"verdict": "PASS", "measurement": {"probe": name}, "thresholds": {}, "raw": []}
                        for name in ("clock", "battery", "thermal", "contention", "disk", "instrument")}})
        executed = {"head": H_CLAIM, "status_porcelain": "", "files": dict(self.sealed_files)}
        executed["files"].update(executed_overrides.get("files", {}))
        for key in ("head", "status_porcelain"):
            if key in executed_overrides:
                executed[key] = executed_overrides[key]
        put(self.custody / "hazards" / "executed_inventory.json", executed)
        plan = {
            "schema": "joulewise.hazard_window_plan.v1", "plan_id": PLAN_ID, "receipt_class": "HAZARD_PACK",
            "t0_epoch_s": 1786205000.0, "window_max_s": 36000,
            "measurement_root": str(self.measurement), "custody_root": str(self.custody),
            "chain_path": str(chain), "chain_sha256_path": str(self.custody / "chain.zsh.sha256"),
            "hazard_window": {
                "pack": {"pack_id": PACK_ID, "pack_root": str(self.pack)},
                "bracket_session_id": SESSION_ID, "h_claim": H_CLAIM, "attempt": 1,
                "sealed_inventory_path": "configs/campaigns/v5_claim_25g83/sealed_inventory.json",
                "executed_inventory_path": "hazards/executed_inventory.json",
                "thresholds": {},
                "bindings": {"claim_runs_root": str(self.claim), "bound_runs_root": str(self.bound),
                             "ledger_path": str(self.ledger), "pre_attempt_id": f"{SESSION_ID}-pre",
                             "post_attempt_id": f"{SESSION_ID}-post"}},
        }
        put(self.plan_path, plan)

    # -- running ---------------------------------------------------------------
    def harvest(self, *, seams=None, **kwargs):
        seams = seams or h.Seams(group_alive=lambda pgid: False, exclusions_compute=fake_exclusions,
                                 boot_session_uuid=lambda: "B5-TEST-BOOT")
        inputs = h.resolve_inputs(self.plan_path)
        return h.harvest(inputs, self.archive, seams=seams, **kwargs)

    def flags(self) -> list[dict]:
        return [json.loads(line) for line in (self.archive / "derived" / "flags.jsonl").read_text().splitlines()]

    def codes(self, run_id=None) -> set[str]:
        return {flag["code"] for flag in self.flags()
                if run_id is None or flag["scope"].get("run_id") == run_id}

    def window_flags(self) -> dict:
        return json.loads((self.archive / "derived" / "window_flags.json").read_bytes())

    def exclusions(self) -> dict:
        return json.loads((self.archive / "derived" / "exclusions.json").read_bytes())


_REAL_ASSESS = h.assess_member
_ASSESS_CACHE: dict[str, dict] = {}


def _bundle_key(bundle: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in bundle.rglob("*") if item.is_file()):
        digest.update(path.relative_to(bundle).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def cached_assess(task):
    """The real assessment, computed once per distinct bundle content.

    The key covers every byte of the bundle, so any test that changes a byte
    gets a fresh, real assessment.  A cache hit rebases the paths and writes
    the cached re-reduced bytes into this harvest's restricted custody.
    """
    bundle = Path(task["bundle_path"])
    if not bundle.is_dir():
        return _REAL_ASSESS(task)
    key = _bundle_key(bundle)
    cached = _ASSESS_CACHE.get(key)
    if cached is None:
        result = _REAL_ASSESS(task)
        stored = copy.deepcopy(result)
        if isinstance(result.get("rereduced"), dict):
            stored["_rereduced_bytes"] = Path(result["rereduced"]["path"]).read_bytes()
        _ASSESS_CACHE[key] = stored
        return result
    result = copy.deepcopy(cached)
    raw = result.pop("_rereduced_bytes", None)
    result["bundle_path"] = str(bundle)
    if raw is not None:
        target = Path(task["withheld_dir"]) / "reductions" / f"{task['run_id']}.summary_metrics.rereduced.json"
        h.write_once(target, raw)
        result["rereduced"]["path"] = str(target)
    return result


class WindowTestCase(unittest.TestCase):
    # The synthetic window has no campaign log, so the cooldown join cannot
    # verify (member.cooldown_unverified fires on every member, correctly).
    # Tests that isolate one member rule mark that code DISCLOSE.
    ISOLATE = {"member.cooldown_unverified": "DISCLOSE"}
    CACHE_ASSESSMENTS = True

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="b5-harvest-", dir=REAL_TMP)
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        if self.CACHE_ASSESSMENTS:
            patcher = mock.patch.object(h, "assess_member", cached_assess)
            patcher.start()
            self.addCleanup(patcher.stop)

    def window(self, **kwargs) -> Window:
        kwargs.setdefault("catalog_overrides", self.ISOLATE)
        return Window(self.tmp / "w", **kwargs)


# ---------------------------------------------------------------------------
# End to end.
# ---------------------------------------------------------------------------

class CollectedWindowTests(WindowTestCase):
    def test_clean_window_emits_numbers_flags_and_exclusions(self):
        window = self.window()
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", window.window_flags()["collector_errors"])
        self.assertEqual(record["members_assessed"], len(MEMBERS))
        # Numbers: every member re-reduced into restricted custody, byte-identical.
        for run_id, *_rest in MEMBERS:
            rereduced = window.archive / "withheld" / "reductions" / f"{run_id}.summary_metrics.rereduced.json"
            self.assertEqual(rereduced.read_bytes(), (window.claim / run_id / "summary_metrics.json").read_bytes())
        # Flags: schema keys exact; no physics or validity flag on any member.
        flags = window.flags()
        self.assertTrue(flags)
        for flag in flags:
            self.assertEqual(set(flag), h.FLAG_KEYS)
            self.assertEqual(len(flag["flag_id"]), 20)
            self.assertIn(flag["blinding"], (h.STRUCTURE, h.RESTRICTED))
        member_codes = {flag["code"] for flag in flags if flag["scope"]["level"] == "member"}
        self.assertEqual(member_codes - {"battery.capture_pair_missing", "member.cooldown_unverified"}, set())
        self.assertNotIn("pack.identity_mismatch", window.codes())
        self.assertNotIn("code.executed_differs_from_sealed", window.codes())
        self.assertNotIn("model.identity_mismatch", window.codes())
        self.assertNotIn("clock.systematic", window.codes())
        # Window summary and exclusions are written; the scheduler reads claim_usable.
        summary = window.window_flags()
        self.assertEqual(summary["schema"], "joulewise.window_flags.v1")
        self.assertEqual(set(summary), {"schema", "window", "catalog", "hazards", "flags", "collector_errors",
                                        "exclusions"})
        self.assertEqual(summary["hazards"]["battery"]["arm"]["verdict"], "PASS")
        self.assertEqual(summary["hazards"]["battery"]["continuous"]["journal"]["malformed"], 0)
        self.assertEqual(summary["flags"]["unclassified"], [])
        exclusions = window.exclusions()
        self.assertEqual(exclusions["members_excluded"], [])
        self.assertTrue(all(cell["resolvable"] for cell in exclusions["cells"]))
        # The fixture cannot produce a real bracket, NEG-8 bound or verdict, so
        # window-level calibration/NEG-8 flags keep it from being claim-usable.
        self.assertFalse(summary["exclusions"]["claim_usable"])
        self.assertTrue({"neg8.bound_not_derived", "whole_window.verdict_absent"} <= set(exclusions["reasons"]))
        # Archive: SHA256SUMS proves every archived byte.
        sums = (window.archive / "sources" / "SHA256SUMS").read_text().splitlines()
        self.assertTrue(sums)
        for line in sums[:50]:
            digest, name = line.split("  ", 1)
            self.assertEqual(sha(window.archive / "sources" / name), digest)
        harvest_json = json.loads((window.archive / "harvest.json").read_bytes())
        for relative, digest in harvest_json["outputs"].items():
            self.assertEqual(sha(window.archive / relative), digest, relative)

    def test_derived_outputs_carry_no_energy_and_no_span_edges(self):
        lo, hi = member_span_ns("b5t-abs-r01")
        request = request_span_ns("b5t-abs-r02")
        window = self.window(journals={"battery_gap": (lo - 200 * 10**9, hi + 200 * 10**9),
                                       "contention_gap": (request[0] - 10**9, request[1] + 10**9)})
        window.harvest()
        derived = "".join(path.read_text() for path in sorted((window.archive / "derived").iterdir()))
        self.assertIn("battery.unmeasured", window.codes("b5t-abs-r01"))
        self.assertIn("contention.unmeasured", window.codes("b5t-abs-r02"))
        for run_id, *_rest in MEMBERS:  # stream and request timing stay in withheld/
            for edge in (*member_span_ns(run_id), *request_span_ns(run_id)):
                self.assertNotIn(str(edge), derived, run_id)
        self.assertIn(str(lo), (window.archive / "withheld" / "spans.json").read_text())
        summary = json.loads((window.claim / MEMBERS[0][0] / "summary_metrics.json").read_bytes())
        for key in ("gross_energy_j", "idle_subtracted_energy_j", "phase_energy_j", "energy_request_j"):
            self.assertNotIn(key, derived)
        numbers = []

        def walk(value):
            if isinstance(value, dict):
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
            elif isinstance(value, float) and abs(value) > 1e-3:
                numbers.append(repr(value))

        walk({key: summary[key] for key in summary if "energy" in key or key == "idle_baseline"})
        self.assertTrue(numbers)
        self.assertEqual([number for number in numbers if number in derived], [])

    def test_battery_excursion_excludes_the_named_member_and_its_quad(self):
        target = "b5t-cmp-b01-b1"
        start, end = member_span_ns(target)
        excursion = ((start + end) // 2, {"InstantAmperage": -447, "Amperage": -380})
        window = self.window(journals={"extra_publications": [excursion]})
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        flagged = {flag["scope"]["run_id"] for flag in window.flags() if flag["code"] == "battery.member_span"}
        self.assertEqual(flagged, {target})
        battery = next(flag for flag in window.flags() if flag["code"] == "battery.member_span")
        self.assertEqual(battery["family"], "PHYSICS_IN_SPAN")
        self.assertIn("instant_amperage_above_limit", battery["observed"]["violations"][0]["reasons"])
        excluded = {row["run_id"] for row in window.exclusions()["members_excluded"]}
        self.assertEqual(excluded, set(QUAD))
        cells = {cell["cell_id"]: cell for cell in window.exclusions()["cells"]}
        self.assertEqual(cells["b5t-cmp"]["n_quads"], 0)
        self.assertEqual(cells["b5t-abs"]["n_repeats"], 2)
        roster = json.loads((window.archive / "derived" / "roster.json").read_bytes())
        member = next(row for row in roster["members"] if row["run_id"] == target)
        self.assertEqual(member["cells"][0]["unit_kind"], "quad")
        self.assertEqual(member["cells"][0]["unit_id"], "b5t-b01")

    def test_missing_bundle_file_is_bytes_missing_and_harvest_completes(self):
        window = self.window()
        (window.claim / "b5t-abs-r02" / "events.jsonl").unlink()
        shutil.rmtree(window.claim / "b5t-cmp-b01-a2")
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        self.assertIn("member.bytes_missing", window.codes("b5t-abs-r02"))
        self.assertIn("member.bytes_missing", window.codes("b5t-cmp-b01-a2"))
        excluded = {row["run_id"] for row in window.exclusions()["members_excluded"]}
        self.assertIn("b5t-abs-r02", excluded)
        self.assertTrue(set(QUAD) <= excluded)
        self.assertNotIn("b5t-abs-r01", excluded)

    def test_flipped_raw_plist_byte_is_a_member_exclusion_not_a_fault(self):
        window = self.window()
        plist = window.claim / "b5t-abs-r01" / "raw" / RAW_SAMPLES_NAME
        raw = bytearray(plist.read_bytes())
        marker = b"<key>elapsed_ns</key>\n\t<integer>"
        index = raw.index(marker) + len(marker)  # the first record's elapsed time
        raw[index] = ord("9") if raw[index] != ord("9") else ord("8")
        plist.write_bytes(bytes(raw))
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        self.assertEqual(record["faults"], [])
        codes = window.codes("b5t-abs-r01")
        self.assertIn("member.strict_invalid", codes)
        self.assertIn("b5t-abs-r01", {row["run_id"] for row in window.exclusions()["members_excluded"]})
        self.assertNotIn("member.strict_invalid", window.codes("b5t-abs-r02"))

    def test_tampered_pack_config_is_pack_identity_mismatch_and_not_claim_usable(self):
        window = self.window()
        config = window.pack / "01_abs" / "b5t-abs-r01.json"
        value = json.loads(config.read_bytes())
        value["workload_profile"]["output_tokens"] = 9
        config.write_bytes(normalized_config(value))
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        flag = next(flag for flag in window.flags() if flag["code"] == "pack.identity_mismatch")
        paths = {row["path"] for row in flag["observed"]["mismatches"]}
        self.assertIn(f"configs/campaigns/{PACK_ID}/01_abs/b5t-abs-r01.json", paths)
        self.assertIn("member.config_bytes_mismatch", window.codes("b5t-abs-r01"))
        self.assertIn("pack.identity_mismatch", window.exclusions()["reasons"])
        self.assertFalse(window.window_flags()["exclusions"]["claim_usable"])
        self.assertFalse(record["claim_usable"])

    def test_clock_systematic_fires_when_most_recorded_anchors_are_not_bounded(self):
        window = self.window()
        for run_id in [row[0] for row in MEMBERS][:4]:
            path = window.claim / run_id / "metadata.json"
            metadata = json.loads(path.read_bytes())
            metadata["uncertainty_evidence"]["clock_anchor"]["status"] = "unbounded"
            put(path, metadata)
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "clock.systematic")
        self.assertEqual(flag["observed"], {"recorded": 6, "non_bounded": 4})
        self.assertIn("member.anchor_not_bounded", window.codes(MEMBERS[0][0]))
        self.assertIn("clock.systematic", window.exclusions()["reasons"])

    def test_clock_systematic_does_not_fire_at_half(self):
        window = self.window()
        for run_id in [row[0] for row in MEMBERS][:3]:
            path = window.claim / run_id / "metadata.json"
            metadata = json.loads(path.read_bytes())
            metadata["uncertainty_evidence"]["clock_anchor"]["status"] = "unbounded"
            put(path, metadata)
        window.harvest()
        self.assertNotIn("clock.systematic", window.codes())

    def test_physics_in_span_thermal_contention_and_clock_step(self):
        thermal_member, contention_member, step_member = "b5t-abs-r01", "b5t-abs-r02", "b5t-cmp-b01-a1"
        lo, hi = member_span_ns(thermal_member)
        request = request_span_ns(contention_member)
        step_at = (member_span_ns(step_member)[0] + member_span_ns(step_member)[1]) // 2
        window = self.window(journals={
            "thermal_levels": [((lo - 10**9, hi + 10**9), 1)],
            "contention_extra": [((request[0] - 10**9, request[1] + 10**9),
                                  {"pid": 77, "comm": "fseventsd", "cpu_s_per_s": 1.84, "outside": True})],
            "clock_steps": [(step_at, 6_000_000)]})
        window.harvest()
        self.assertEqual({flag["scope"]["run_id"] for flag in window.flags() if flag["code"] == "thermal.os_level_nonzero"},
                         {thermal_member})
        self.assertEqual({flag["scope"]["run_id"] for flag in window.flags()
                          if flag["code"] == "contention.request_overlap"}, {contention_member})
        self.assertEqual({flag["scope"]["run_id"] for flag in window.flags() if flag["code"] == "clock.step_overlap"},
                         {step_member})
        self.assertNotIn("contention.request_overlap", window.codes("b5t-cmp-b01-b2"))  # kernel_task is exempt

    def test_missing_monitor_journal_is_recorded_and_members_unmeasured(self):
        window = self.window(journals={"omit": ("battery",)})
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        self.assertIn("records.monitor_journal_absent", window.codes())
        self.assertEqual({flag["scope"]["run_id"] for flag in window.flags() if flag["code"] == "battery.unmeasured"},
                         {row[0] for row in MEMBERS})

    def test_token_count_mismatch_against_registered_workload(self):
        window = self.window(register_prompt_tokens=33)
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "member.token_count_mismatch")
        self.assertEqual(flag["observed"], {"prompt_realized": 32})
        self.assertEqual(flag["expected"]["prompt_tokens"], 33)

    def test_target_precheck_failures_split_into_instrument_and_member_codes(self):
        window = self.window(target_precheck=["phase", "decode"])
        window.harvest()
        codes = window.codes("b5t-abs-r01")
        self.assertIn("instrument.cadence_ratio_below_threshold", codes)
        precheck = next(flag for flag in window.flags() if flag["code"] == "member.precheck_failed"
                        and flag["scope"]["run_id"] == "b5t-abs-r01")
        self.assertEqual(precheck["observed"], {"target": "phase/decode", "reasons": ["instrument_calibration_missing"]})
        self.assertEqual(precheck["blinding"], h.STRUCTURE)

    def test_executed_inventory_and_chain_sidecar_replay(self):
        window = self.window(executed_overrides={"files": {"joulewise/b5t_stub.py": "f" * 64},
                                                 "status_porcelain": " M joulewise/b5t_stub.py\n?? scratch.txt\n"})
        (window.custody / "chain.zsh").write_text("#!/bin/zsh\necho edited\n")
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "code.executed_differs_from_sealed")
        checks = {row["check"] for row in flag["observed"]["differences"]}
        self.assertEqual(checks, {"executed_inventory", "chain_sidecar", "tracked_edits"})
        self.assertIn("code.executed_differs_from_sealed", window.exclusions()["reasons"])

    def test_model_identity_mismatch_against_frozen_pins(self):
        window = self.window()
        tree = json.loads((window.pack / "plan_tree.json").read_bytes())
        unit = tree["arm_attachments"]["identity_pin_projection"]["identity_units"][0]
        unit["model_runtime_config"]["runtime_identity_sha256"] = "0" * 64
        put(window.pack / "plan_tree.json", tree)
        (window.pack / "plan_tree.sha256").write_text(f"{sha(window.pack / 'plan_tree.json')}  plan_tree.json\n")
        window.harvest()
        mismatched = {flag["scope"]["run_id"] for flag in window.flags() if flag["code"] == "model.identity_mismatch"}
        self.assertEqual(mismatched, {row[0] for row in MEMBERS})
        # The sealed inventory still pins the original plan tree bytes.
        self.assertIn("pack.identity_mismatch", window.codes())

    def test_absent_frozen_pins_are_recorded(self):
        window = self.window(frozen_pins=False)
        window.harvest()
        self.assertIn("model.frozen_pins_absent", window.codes())
        self.assertNotIn("model.identity_mismatch", window.codes())

    def test_earlier_flag_files_are_absorbed_and_malformed_lines_recorded(self):
        window = self.window()
        ledger = h.FlagLedger(plan_id=PLAN_ID, attempt=1, catalog=h.Catalog.load(None), boot_session_uuid="X")
        earlier = ledger.emit("records.collector_failed", level="window", collector="arm:pack_tree", stage="arm",
                              observed={"collector": "pack_tree", "error_type": "TimeoutExpired"})
        flags_dir = window.custody / "flags"
        flags_dir.mkdir(parents=True)
        (flags_dir / "arm.jsonl").write_text(json.dumps(earlier) + "\n{not json\n")
        window.harvest()
        ids = {flag["flag_id"] for flag in window.flags()}
        self.assertIn(earlier["flag_id"], ids)
        self.assertIn("records.flag_line_malformed", window.codes())

    def test_unknown_catalog_entry_is_reported_unclassified(self):
        window = self.window()
        catalog_path = window.measurement / "configs/campaigns/v5_claim_25g83/flag_catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        del catalog["codes"]["battery.capture_pair_missing"]
        put(catalog_path, catalog)
        window.harvest()
        self.assertIn("battery.capture_pair_missing", window.window_flags()["flags"]["unclassified"])

    def test_bundle_outside_roster_is_ignored_and_recorded(self):
        window = self.window()
        subprocess.run(["/bin/cp", "-c", "-R", str(window.claim / "b5t-abs-r01"), str(window.claim / "stray-r99")],
                       check=True)
        window.harvest()
        self.assertIn("roster.bundle_not_in_roster", window.codes("stray-r99"))
        self.assertNotIn("stray-r99", json.loads((window.archive / "withheld" / "spans.json").read_bytes())["spans"])

    def test_exclusion_function_unavailable_still_emits_numbers_and_flags(self):
        window = self.window()

        def unavailable(*_args):
            raise ImportError("joulewise.flags.exclusions")

        record = window.harvest(seams=h.Seams(group_alive=lambda pgid: False, exclusions_compute=unavailable,
                                              boot_session_uuid=lambda: None))
        self.assertEqual(record["verdict"], "COLLECTED")
        self.assertFalse(record["claim_usable"])
        self.assertEqual(window.exclusions()["status"], "UNAVAILABLE")
        self.assertIn("exclusions", {row["collector"] for row in window.window_flags()["collector_errors"]})
        self.assertTrue((window.archive / "withheld" / "reductions").is_dir())

    def test_program_failure_on_present_bytes_is_harvest_fault_with_outputs(self):
        window = self.window()
        (window.pack / "plan_tree.json").unlink()
        record = window.harvest()
        self.assertEqual(record["verdict"], "HARVEST_FAULT")
        self.assertFalse(record["claim_usable"])
        self.assertTrue((window.archive / "derived" / "window_flags.json").is_file())
        self.assertIn("harvest.fault", window.window_flags()["exclusions"]["reasons"])


class WorkerPoolTests(WindowTestCase):
    CACHE_ASSESSMENTS = False

    def test_worker_pool_matches_serial_assessment(self):
        window = self.window()
        tasks = [{"run_id": run_id, "bundle_path": str(window.claim / run_id), "withheld_dir": str(self.tmp / f"w{n}")}
                 for n, (run_id, *_rest) in enumerate(MEMBERS[:2])]
        serial = h.assess_members(tasks[:1], workers=1)
        pooled = h.assess_members([{**tasks[0], "withheld_dir": str(self.tmp / "pool")}, tasks[1]], workers=2)
        strip = lambda row: {k: v for k, v in row.items() if k != "rereduced"}  # noqa: E731
        self.assertEqual(strip(serial[0]), strip(pooled[0]))
        self.assertEqual(serial[0]["rereduced"]["sha256"], pooled[0]["rereduced"]["sha256"])
        self.assertTrue(pooled[1]["strict_valid"])


class CalibrationBaselineTests(WindowTestCase):
    """Memo 3.3: the bracket decision carries the acceptance's ledger cutoff."""

    def test_bracket_replay_carries_the_acceptance_cutoff_baseline(self):
        from joulewise import calibration_bracketing as brackets
        from joulewise.schemas import CalibrationBracketingPolicy
        window = self.window(prefix_ledger=True)
        seen = []
        real = brackets.calibration_bracket_for_bundles

        def spy(*args, **kwargs):
            assessment, reasons = real(*args, **kwargs)
            seen.append((kwargs["ledger_snapshot"].baseline_sequence, kwargs["ledger_snapshot"].baseline_digest,
                         reasons))
            return assessment, reasons

        with mock.patch.object(brackets, "calibration_bracket_for_bundles", side_effect=spy):
            window.harvest()
        cutoff = brackets.load_calibration_acceptance_bound(ROOT / ACCEPTANCE)["ledger_cutoff"]
        self.assertEqual(len(seen), 1)
        sequence, digest, reasons = seen[0]
        self.assertEqual((sequence, digest), (cutoff["sequence"], cutoff["head_digest"]))
        self.assertNotIn("calibration_ledger_baseline_missing", reasons)
        boundary = json.loads((window.archive / "derived" / "terminal-boundary.json").read_bytes())
        self.assertEqual(boundary["pin_relation"], "physical_ahead")
        self.assertEqual(boundary["refusal_code"], "calibration_ledger_head_mismatch")
        archived = window.archive / "sources" / "ledger" / "calibration_observation_ledger.jsonl"
        rows = len([line for line in archived.read_bytes().splitlines() if line.strip()])
        self.assertEqual(boundary["terminal_head_pin_candidate"]["sequence"], rows)
        self.assertGreater(rows, cutoff["sequence"])
        self.assertTrue((window.archive / "derived" / "bracket-binding.json").is_file())
        self.assertNotIn("calibration.session_not_bound_to_plan", window.codes())
        self.assertNotIn("calibration.capture_invalid", window.codes())
        # Negative control: the same ledger without the cutoff baseline is the
        # memo-3.3 refusal the harvest must not reproduce.
        ledger = window.archive / "sources" / "ledger" / "calibration_observation_ledger.jsonl"
        missing = load_calibration_ledger_snapshot(ledger, window.archive / "derived" / "terminal-pin.json",
                                                   require_committed_pin=False, verify_custody=False)
        policy = CalibrationBracketingPolicy(require_bracket=True, calibration_bracket_max_drift_s=0.05)
        _assessment, without = brackets.evaluate_calibration_bracket(
            [], window_start_s=1.0, window_end_s=2.0, bindings={}, policy=policy, ledger_snapshot=missing)
        self.assertIn("calibration_ledger_baseline_missing", without)

    def test_session_bound_to_another_runs_root_is_flagged(self):
        window = self.window(prefix_ledger=True)
        plan = json.loads(window.plan_path.read_bytes())
        moved = window.root / "elsewhere_runs"
        shutil.move(str(window.claim), str(moved))
        plan["hazard_window"]["bindings"]["claim_runs_root"] = str(moved)
        put(window.plan_path, plan)
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "calibration.session_not_bound_to_plan")
        self.assertIn("runs_root", flag["observed"])

    def test_capture_artifact_change_is_capture_invalid(self):
        window = self.window(prefix_ledger=True)
        (window.claim / "instrument_validation" / f"{SESSION_ID}-post" / "manifest.json").write_text('{"slot":"x"}\n')
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "calibration.capture_invalid")
        self.assertEqual(flag["observed"]["slot"], "post")


class ReadinessAndNullTests(WindowTestCase):
    def test_null_window_without_chain_start(self):
        window = self.window()
        (window.custody / "night" / "chain.started").unlink()
        record = window.harvest()
        self.assertEqual(record["verdict"], "NULL")
        self.assertFalse(record["claim_usable"])
        self.assertEqual(window.exclusions()["reasons"], ["window.null"])
        self.assertFalse((window.archive / "withheld" / "reductions").exists())
        self.assertTrue((window.archive / "sources" / "SHA256SUMS").is_file())

    def test_alive_chain_group_is_not_ready_and_writes_nothing(self):
        window = self.window()
        with self.assertRaises(h.NotReady):
            window.harvest(seams=h.Seams(group_alive=lambda pgid: True))
        self.assertFalse(window.archive.exists())

    def test_missing_terminal_record_waits_unless_allowed(self):
        window = self.window()
        (window.custody / "night" / "result.json").unlink()
        with self.assertRaises(h.NotReady):
            window.harvest()
        record = window.harvest(allow_missing_terminal=True)
        self.assertEqual(record["verdict"], "COLLECTED")
        self.assertIn("records.terminal_record_absent", window.codes())

    def test_archive_root_is_created_once(self):
        window = self.window()
        window.archive.mkdir()
        with self.assertRaises(h.HarvestFault):
            window.harvest()

    def test_sources_are_unchanged_by_the_harvest(self):
        window = self.window()
        before = h.tree_inventory(window.custody)
        window.harvest()
        self.assertEqual(h.tree_inventory(window.custody), before)
        self.assertNotIn("records.source_changed_during_harvest", window.codes())


class DeskAndG3Tests(WindowTestCase):
    def test_prepare_desk_runs_the_production_writer_and_guards_sources(self):
        window = self.window(prefix_ledger=True)
        calls = []

        def runner(argv, **kwargs):
            calls.append(argv)
            runs = Path(argv[argv.index("--runs-dir") + 1])
            (runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
            (runs / "campaign_log.jsonl").write_text('{"status":"failed"}\n')
            (runs / "b5t-abs-r01" / "logs" / "controller.log").write_text("tampered\n")
            return SimpleNamespace(returncode=1, stdout="", stderr="")

        window.harvest(seams=h.Seams(group_alive=lambda pgid: False, exclusions_compute=fake_exclusions,
                                     runner=runner), prepare_desk=True, run_g3=False)
        self.assertEqual(len(calls), 1)
        argv = calls[0]
        self.assertIn("--whole-window-verdict", argv)
        self.assertEqual(argv[argv.index("--bracket-binding") + 1], str(window.claim / "bracket-binding.json"))
        self.assertTrue((window.claim / "bracket-binding.json").is_file())
        flag = next(flag for flag in window.flags() if flag["code"] == "records.source_changed_during_harvest")
        self.assertEqual(flag["observed"]["changed"], ["b5t-abs-r01/logs/controller.log"])
        self.assertIn("whole_window.verdict_unauthenticated", window.codes())

    def test_g3_is_not_applicable_to_a_floor_pack(self):
        window = self.window()
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "g3.not_applicable")
        self.assertEqual(flag["observed"]["reason"], "pack_has_no_analysis_manifest")

    def test_g3_failures_become_flags(self):
        window = self.window(prefix_ledger=True)
        (window.pack / "analysis_manifest_v3.json").write_text("{}\n")
        (window.claim / "whole-window-verdict.json").write_text("{}\n")
        (window.claim / "bracket-binding.json").write_text("{}\n")

        def runner(argv, **kwargs):
            report = Path(argv[argv.index("--report-json") + 1])
            report.write_text(json.dumps({"assertions": [{"id": "S11-A1", "status": "PASS"},
                                                         {"id": "F5-2", "status": "FAIL"},
                                                         {"id": "S11-A5", "status": "FAIL"}]}))
            return SimpleNamespace(returncode=1, stdout="", stderr="")

        window.harvest(seams=h.Seams(group_alive=lambda pgid: False, exclusions_compute=fake_exclusions,
                                     runner=runner))
        self.assertIn("g3.recompute_failed", window.codes())
        self.assertIn("g3.assertion_failed", window.codes())
        self.assertTrue((window.archive / "withheld" / "transcripts" / "g3.txt").is_file())


_REAL_SEAMS = h.Seams


class CliTests(WindowTestCase):
    def run_cli(self, window, alive, *extra):
        from scripts import harvest_b5_window as cli

        def seams(**kwargs):  # the CLI builds Seams(workers=...); only the seams change
            return _REAL_SEAMS(group_alive=lambda pgid: alive, exclusions_compute=fake_exclusions,
                               boot_session_uuid=lambda: "B5-CLI", **kwargs)

        stdout = io.StringIO()
        with mock.patch.object(h, "Seams", seams), contextlib.redirect_stdout(stdout):
            code = cli.main(["--plan", str(window.plan_path), "--archive-root", str(window.archive), *extra])
        return code, stdout.getvalue()

    def test_cli_prints_structure_only_and_exits_zero(self):
        window = self.window()
        code, output = self.run_cli(window, False, "--workers", "1")
        self.assertEqual(code, 0, output)
        lines = output.splitlines()
        self.assertTrue(lines[0].startswith("verdict=COLLECTED claim_usable=false"), lines[0])
        self.assertTrue(any(line.startswith("path=") and "derived/flags.jsonl" in line for line in lines))
        self.assertFalse(any("energy" in line for line in lines))

    def test_cli_not_ready_exit_code(self):
        window = self.window()
        code, output = self.run_cli(window, True)
        self.assertEqual(code, 4)
        self.assertIn("verdict=NOT_READY", output)
        self.assertFalse(window.archive.exists())


# ---------------------------------------------------------------------------
# Pure joins and parsers.
# ---------------------------------------------------------------------------

def _reading(module, mono_s, values, kind="reading", interval=None):
    mono = int(mono_s * 1e9)
    return h.Reading(module, mono, mono + RAW_OFFSET_NS, mono_s + 1000.0, values, kind, interval)


class JoinTests(unittest.TestCase):
    T = h.DEFAULT_THRESHOLDS

    def battery_polls(self, publications, start_s=0, end_s=600):
        """Polls every 5 s report the latest publication (time, values) at or before them."""
        rows = []
        for poll in range(start_s, end_s, 5):
            current = [item for item in publications if item[0] <= poll]
            if current:
                stamp, values = current[-1]
                rows.append(_reading("battery", poll, {**clean_battery(**values), "UpdateTime": stamp + 1000}))
        return rows

    def test_in_force_publications(self):
        self.assertEqual(h.in_force([0, 60, 120, 180], 70, 100), [1, 2])
        self.assertEqual(h.in_force([0, 60, 120, 180], 60, 120), [1, 2])
        self.assertEqual(h.in_force([0, 60, 120, 180], 61, 179), [1, 2, 3])
        self.assertEqual(h.in_force([], 1, 2), [])

    def test_publication_before_the_span_is_in_force(self):
        readings = self.battery_polls([(0, {}), (60, {"InstantAmperage": -447}), (120, {}), (180, {})])
        flags = dict((code, observed) for code, observed, _ in
                     h.battery_member_flags([int(70e9), int(100e9)], readings, self.T))
        self.assertIn("battery.member_span", flags)
        clean = h.battery_member_flags([int(130e9), int(170e9)], readings, self.T)
        self.assertNotIn("battery.member_span", [code for code, *_ in clean])

    def test_charging_and_disconnected_publications(self):
        for values, reason in (({"IsCharging": "Yes"}, "is_charging"),
                               ({"ExternalConnected": "No"}, "external_disconnected"),
                               ({"Amperage": 250}, "amperage_above_limit")):
            readings = self.battery_polls([(0, {}), (60, values), (120, {})])
            ((code, observed, _interval), *_rest) = h.battery_member_flags([int(65e9), int(70e9)], readings, self.T)
            self.assertEqual(code, "battery.member_span")
            self.assertIn(reason, observed["violations"][0]["reasons"])

    def test_float_reading_at_the_limit_passes(self):
        readings = self.battery_polls([(0, {}), (60, {"InstantAmperage": -200}), (120, {})])
        codes = [code for code, *_ in h.battery_member_flags([int(65e9), int(70e9)], readings, self.T)]
        self.assertNotIn("battery.member_span", codes)

    def test_publication_gap_over_120_s_is_unmeasured(self):
        readings = self.battery_polls([(0, {}), (200, {}), (260, {})], end_s=300)
        flagged = [code for code, *_ in h.battery_member_flags([int(100e9), int(110e9)], readings, self.T)]
        self.assertIn("battery.unmeasured", flagged)
        fine = [code for code, *_ in h.battery_member_flags([int(210e9), int(220e9)], readings, self.T)]
        self.assertNotIn("battery.unmeasured", fine)

    def test_monitor_gap_record_is_unmeasured(self):
        readings = self.battery_polls([(0, {}), (60, {}), (120, {}), (180, {})])
        readings.append(_reading("battery", 95, {}, kind="gap", interval=(int(90e9), int(97e9))))
        flagged = [code for code, *_ in h.battery_member_flags([int(92e9), int(96e9)], readings, self.T)]
        self.assertIn("battery.unmeasured", flagged)

    def test_accumulator_is_diagnostic_until_units_are_confirmed(self):
        publications = [(0, {"PowerTelemetryData": {"AccumulatedBatteryPower": 100, "BatteryPowerAccumulatorCount": 10}}),
                        (60, {"PowerTelemetryData": {"AccumulatedBatteryPower": 1300, "BatteryPowerAccumulatorCount": 70}}),
                        (120, {})]
        readings = self.battery_polls(publications)
        unconfirmed = [code for code, *_ in h.battery_member_flags([int(10e9), int(20e9)], readings, self.T)]
        self.assertIn("battery.accumulator_diagnostic", unconfirmed)
        self.assertNotIn("battery.accumulator_span", unconfirmed)
        confirmed = dict(self.T, battery_accumulator_watts_per_unit=1.0)
        codes = [code for code, *_ in h.battery_member_flags([int(10e9), int(20e9)], readings, confirmed)]
        self.assertIn("battery.accumulator_span", codes)  # 1200 W·count / 60 counts = 20 W > 0.2 A × 12.18 V

    def test_thermal_nonzero_and_unmeasured(self):
        readings = [_reading("thermal", second, {"level": 1 if second == 50 else 0}) for second in range(0, 100, 5)]
        codes = [code for code, *_ in h.thermal_member_flags([int(48e9), int(52e9)], readings, self.T)]
        self.assertEqual(codes, ["thermal.os_level_nonzero"])
        sparse = [_reading("thermal", second, {"level": 0}) for second in (0, 40)]
        codes = [code for code, *_ in h.thermal_member_flags([int(10e9), int(20e9)], sparse, self.T)]
        self.assertEqual(codes, ["thermal.unmeasured"])

    def test_contention_counts_only_outside_processes_above_five_percent(self):
        processes = [{"comm": "kernel_task", "cpu_s_per_s": 0.9, "outside": True},
                     {"comm": "python3.13", "cpu_s_per_s": 0.9, "in_measurement_tree": True},
                     {"comm": "mds", "cpu_s_per_s": 0.05, "outside": True}]
        readings = [_reading("contention", 10, {"processes": processes}, interval=(0, int(10e9))),
                    _reading("contention", 20, {"processes": processes + [
                        {"comm": "mediaanalysisd", "cpu_s_per_s": 1.14, "outside": True}]},
                        interval=(int(10e9), int(20e9)))]
        self.assertEqual(h.contention_member_flags([int(2e9), int(3e9)], readings, self.T), [])
        ((code, observed, _interval),) = h.contention_member_flags([int(12e9), int(13e9)], readings, self.T)
        self.assertEqual((code, observed["offenders"][0]["comm"]), ("contention.request_overlap", "mediaanalysisd"))
        ((code, observed, _interval),) = h.contention_member_flags([int(18e9), int(25e9)], readings[:1] + readings[1:],
                                                                   self.T)[-1:]
        self.assertEqual(code, "contention.unmeasured")
        # Named by the last covering interval's end, not by the request's end.
        self.assertEqual(observed["holes_monotonic_ns"], [[int(20e9), None]])
        ((code, observed, interval),) = h.contention_member_flags([int(25e9), int(26e9)], readings, self.T)
        self.assertEqual((code, observed["holes_monotonic_ns"], interval),
                         ("contention.unmeasured", [[int(20e9), None]], {"monotonic_ns": None}))

    def test_clock_steps_net_of_the_frequency_word(self):
        readings = []
        for second in range(0, 20):
            raw = second * 10**9
            anchor = 10**15 + round(-3.17e-6 * raw) + (6_000_000 if second >= 10 else 0)
            values = {"anchor_ns": anchor, "ppm": -3.17 if second < 15 else -3.0}
            readings.append(h.Reading("clock", raw, raw, None, values))
        steps, frequencies = h.clock_steps(readings, self.T)
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["interval_monotonic_ns"], [9 * 10**9, 10 * 10**9])
        self.assertEqual([row["ppm"] for row in frequencies], [-3.17, -3.0])
        drift_only = [h.Reading("clock", s * 10**9, s * 10**9, None, {"anchor_ns": round(-3.17e-6 * s * 10**9 * 300),
                                                                     "ppm": -3.17 * 300}) for s in range(5)]
        self.assertEqual(h.clock_steps(drift_only, self.T)[0], [])

    def test_monitor_line_shapes(self):
        nested = h.parse_monitor_line("thermal", {"measurement": {"values": {"level": 0},
                                                                  "stamps": {"monotonic_ns": 5, "wall_s": 1.0}}})
        self.assertEqual((nested.monotonic_ns, nested.values["level"]), (5, 0))
        gap = h.parse_monitor_line("battery", {"kind": "monitor_restart", "interval": {"monotonic_ns": [1, 9]}})
        self.assertEqual((gap.kind, gap.interval), ("gap", (1, 9)))
        self.assertIsNone(h.parse_monitor_line("battery", {"values": {"x": 1}}))
        contention = h.parse_monitor_line("contention", {"monotonic_ns": 10 * 10**9, "values": {"interval_s": 10}})
        self.assertEqual(contention.interval, (0, 10 * 10**9))

    def test_member_spans_hull_stamps_and_battery_span_events(self):
        metadata = {"uncertainty_evidence": {"clock_anchor": {"clock_stamps": {
            "pre_spawn": {"monotonic_before_s": 10.0, "monotonic_after_s": 10.0},
            "sampling_started": {"monotonic_before_s": 12.0, "monotonic_after_s": 12.0},
            "sampling_stopped": {"monotonic_before_s": 13.0, "monotonic_after_s": 13.5},
            "post_parse": {"monotonic_before_s": 14.0, "monotonic_after_s": 14.25}}}}}
        events = [{"event_type": "stage_started", "phase": "idle_baseline", "metadata": {"monotonic_ns": 9 * 10**9}},
                  {"event_type": "stage_completed", "phase": "idle_drift_sentinel",
                   "metadata": {"monotonic_ns": 20 * 10**9}}]
        self.assertEqual(h.member_spans(metadata, events),
                         {"member": [9 * 10**9, 20 * 10**9], "request": [12 * 10**9, 13_500_000_000]})
        self.assertEqual(h.member_spans(metadata, [])["member"], [10 * 10**9, 14_250_000_000])
        self.assertEqual(h.member_spans({}, []), {"member": None, "request": None})


class RecordTests(unittest.TestCase):
    def test_flag_id_is_the_dedup_key_and_records_are_exact(self):
        catalog = h.Catalog.load(FIXTURES / "flag_catalog.json")
        ledger = h.FlagLedger(plan_id="p", attempt=2, catalog=catalog, boot_session_uuid="B", now=lambda: 1.0,
                              monotonic_ns=lambda: 2)
        first = ledger.emit("disk.low", level="window", collector="monitor", observed={"readings_below": 1})
        again = ledger.emit("disk.low", level="window", collector="monitor", observed={"readings_below": 1})
        other = ledger.emit("disk.low", level="window", collector="monitor", observed={"readings_below": 2})
        self.assertIs(first, again)
        self.assertNotEqual(first["flag_id"], other["flag_id"])
        self.assertEqual(len(ledger.records), 2)
        self.assertEqual(first["flag_id"], h.default_flag_id(first["code"], first["scope"], first["observed"],
                                                             first["source"]))
        self.assertEqual(first["catalog_sha256"], sha(FIXTURES / "flag_catalog.json"))
        self.assertEqual(first["scope"]["attempt"], 2)
        self.assertEqual(catalog.effect("disk.low"), "DISCLOSE")
        self.assertEqual(catalog.effect("not.a.code"), "UNCLASSIFIED")
        with self.assertRaises(KeyError):
            ledger.emit("not.a.code", level="window", collector="x")
        with self.assertRaises(ValueError):
            ledger.emit("disk.low", level="window", collector="x", observed={"bad": float("nan")})

    def test_every_catalog_fixture_code_is_an_emitted_code(self):
        catalog = json.loads((FIXTURES / "flag_catalog.json").read_bytes())
        self.assertEqual(set(catalog["codes"]), set(h.CODES))
        for code, entry in catalog["codes"].items():
            self.assertIn(entry["effect"], h.EFFECTS)
            self.assertEqual((entry["family"], entry["klass"]), (h.CODES[code].family, h.CODES[code].klass))

    def test_restricted_reasons(self):
        self.assertTrue(h.restricted_reason("anchor_energy_envelope_exceeds_quarter_metric"))
        self.assertFalse(h.restricted_reason("cadence_ratio_below_threshold"))
        self.assertFalse(h.restricted_reason("instrument_calibration_missing"))

    def test_inventory_shapes(self):
        digest = "b" * 64
        self.assertEqual(h._inventory_map({"head": "h", "files": {"a": digest}}), ({"a": digest}, "h"))
        self.assertEqual(h._inventory_map({"files": [{"path": "a", "sha256": digest}]}), ({"a": digest}, None))
        self.assertEqual(h._inventory_map({"a": digest, "head": "h"}), ({"a": digest}, "h"))

    def test_pinned_files_resolve_repo_and_pack_relative_paths(self):
        tree = {"plan": {"path": "calibration_plan.json", "actual_sha256": "1" * 64},
                "science": [{"config_path": "configs/campaigns/p/x.json", "config_sha256": "2" * 64}],
                "acceptance_policy": {"issued_ledger_head": {"path": "configs/calibration/calibration_ledger_head.json",
                                                             "head_sha256": "3" * 64}},
                "binding": {"kind": "binding_path", "value": "claim_runs_root", "relative": "x"}}
        rows = h.pinned_files(tree, pack_root=Path("/r/configs/campaigns/p"), repo_root=Path("/r"))
        self.assertEqual(rows, [{"path": "configs/campaigns/p/calibration_plan.json", "sha256": "1" * 64},
                                {"path": "configs/campaigns/p/x.json", "sha256": "2" * 64}])

    def test_real_alpha_pack_roster_has_cells_quads_and_auxiliaries(self):
        pack = ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5"
        roster = h.build_roster(pack, ROOT)
        members = {row["run_id"]: row for row in roster["members"]}
        self.assertEqual(sum(row["kind"] == "science" for row in roster["members"]), 100)
        self.assertEqual(sum(row["kind"] == "auxiliary" for row in roster["members"]), 19)
        quad_member = members["d117fq31p7-df-cmp-abba-ph-decode-b01-a1"]
        self.assertIn({"unit_kind": "quad", "unit_id": "d117-df-cmp-abba-ph-decode-qwen3-1p7b-b01"},
                      [{key: cell[key] for key in ("unit_kind", "unit_id")} for cell in quad_member["cells"]])
        self.assertEqual(quad_member["condition_family_id"], "df-ph-decode-qwen3-1p7b")
        self.assertEqual(len(roster["cells"]), 6)
        rows = h.pinned_files(json.loads((pack / "plan_tree.json").read_bytes()), pack_root=pack, repo_root=ROOT)
        mismatched = [row for row in rows if not (ROOT / row["path"]).is_file() or sha(ROOT / row["path"]) != row["sha256"]]
        self.assertEqual(mismatched, [])

    def test_real_contrast_pack_roster_uses_contrast_blocks(self):
        pack = ROOT / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
        roster = h.build_roster(pack, ROOT)
        science = [row for row in roster["members"] if row["kind"] == "science"]
        self.assertEqual(len(science), 80)
        self.assertTrue(all(cell["unit_kind"] == "quad" for row in science for cell in row["cells"]))
        self.assertEqual(len(roster["cells"]), 2)


@unittest.skipUnless((B3W1 / "harvest.json").is_file(), "block-3 b3w1 archive is local to the measurement Mac")
class RealB3w1BytesTests(unittest.TestCase):
    """On real b3w1 bytes: re-reduction is byte-identical and anchors recompute.

    One bundle by default (about a minute); JW_B5_B3W1_ALL=1 checks all 24.
    """

    def test_rereduced_summaries_and_recomputed_anchors_match_block_3(self):
        block3 = json.loads((B3W1 / "harvest.json").read_bytes())
        recorded = {row["run_id"]: row["clock_anchor_status"] for row in block3["members"]}
        run_ids = sorted(recorded) if os.environ.get("JW_B5_B3W1_ALL") else ["g2a-small-p0512-r01"]
        with tempfile.TemporaryDirectory(prefix="b5-b3w1-", dir=REAL_TMP) as scratch:
            for run_id in run_ids:
                bundle = B3W1 / "g2a-root" / "runs" / run_id
                result = h.assess_member({"run_id": run_id, "bundle_path": str(bundle), "withheld_dir": scratch})
                self.assertEqual(result["errors"], {}, run_id)
                self.assertTrue(result["strict_valid"], run_id)
                self.assertTrue(result["rereduced"]["identical_to_stored"], run_id)
                self.assertEqual(Path(result["rereduced"]["path"]).read_bytes(),
                                 (bundle / "summary_metrics.json").read_bytes())
                self.assertEqual(result["anchor_recomputed"], recorded[run_id])
                self.assertEqual(result["anchor_recorded"], recorded[run_id])


if __name__ == "__main__":
    unittest.main()
