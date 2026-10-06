"""Lane L5: the block-5 harvest emits numbers plus flags and never refuses on data.

Real code runs unpatched throughout: strict validation, re-reduction, anchor
re-derivation from the raw plist, the calibration ledger and bracket evaluator,
battery-pair authentication, the pack/code/model replays and the monitor joins.
Fakes stand only at the seams the plan names, and each fake writes or reads the
other lane's own format:

* hazard-monitor journals (L1): written here line for line in the
  ``joulewise.hazard_journal.v1`` form of ``joulewise.hazards.monitor``;
  ``tests/fixtures/b5_harvest/l1_monitor`` holds journals L1's own monitor
  wrote, and ``L1JournalFormatTests`` pins this writer to them;
* the exclusion function (L4): ``joulewise.flags.exclusions.compute`` itself
  whenever ``joulewise.flags`` is importable, else ``fake_exclusions``, which
  reads L4's documented roster and span shape;
* the arm record (L1), executed inventory and driver flags (L2) in their
  writers' shapes; the process-group probe; the G3 and desk subprocesses.

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
import importlib.util
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

from joulewise import kernel_clock
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
L1_JOURNALS = FIXTURES / "l1_monitor"
PREFIX = ROOT / "tests/fixtures/v5_qualification_harvest/acceptance-prefix-376.jsonl.zlib.b85"
ACCEPTANCE = "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json"
POLICY = "configs/campaign_policies/quiet_mac_p2_production.json"
B3W1 = Path("/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2")
REAL_TMP = os.path.realpath(tempfile.gettempdir())


def _importable(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


# Other lanes' modules, present once the lanes are integrated.
L1_AVAILABLE = _importable("joulewise.hazards.monitor")
L4_AVAILABLE = _importable("joulewise.flags.exclusions")

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
WALL_OFFSET_NS = round(WALL_OFFSET_S * 1e9)
CHAIN_STARTED_NS = 1_487_000 * 10**9  # before every member's stream
GIB = 2**30
NS = 10**9


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
# Hazard-monitor journals in L1's format (joulewise.hazards.monitor).
# ---------------------------------------------------------------------------

ACCUMULATOR_FIELDS = (
    "BatteryPower", "AccumulatedBatteryPower", "BatteryPowerAccumulatorCount",
    "AccumulatedBatteryDischarge", "BatteryDischargeAccumulatorCount",
    "SystemPowerIn", "AccumulatedSystemPowerIn", "SystemPowerInAccumulatorCount",
    "SystemLoad", "AccumulatedSystemLoad", "SystemLoadAccumulatorCount",
    "SystemVoltageIn", "SystemCurrentIn", "PowerTelemetryErrorCount",
)
DRIFT_WORD = round(-3.17 * kernel_clock.FREQUENCY_SCALE)


def l1_stamp(monotonic_ns: int) -> dict:
    return {"wall_ns": monotonic_ns + WALL_OFFSET_NS, "monotonic_ns": monotonic_ns,
            "monotonic_raw_ns": monotonic_ns + RAW_OFFSET_NS}


class L1Journal:
    """Lines exactly as ``joulewise.hazards.monitor.Monitor._write`` writes them."""

    def __init__(self, module: str):
        self.module, self.lines, self.seq = module, [], 0

    def write(self, kind: str, started_ns: int, finished_ns: int | None = None, values=None, error=None):
        self.seq += 1
        self.lines.append({"schema": "joulewise.hazard_journal.v1", "module": self.module, "session": "4242-1",
                           "seq": self.seq, "kind": kind, "started": l1_stamp(started_ns),
                           "finished": l1_stamp(started_ns if finished_ns is None else finished_ns),
                           "values": values, "error": error, "raw": []})

    def dump(self, path: Path) -> None:
        path.write_text("".join(json.dumps(line, sort_keys=True, separators=(",", ":")) + "\n" for line in self.lines))


def frequency_probe(raw_word: int) -> dict:
    """A valid ``kernel_clock`` probe record (L1's tests/hazards/fakes.frequency_probe)."""
    value = kernel_clock.Timex()
    value.freq = raw_word
    value.status = 5
    return {"schema_version": kernel_clock.PROBE_SCHEMA, "modes": 0, "raw_word": raw_word,
            "ppm": raw_word / kernel_clock.FREQUENCY_SCALE, "call_status": 5, "timex_status": 5, "errno": 0,
            "raw_hex": bytes(value).hex()}


def battery_values(update_time_s: int, **override) -> dict:
    """``battery.parse_reading`` fields, as L1's monitor journals them."""
    values = {"returncode": 0, "external_connected": True, "is_charging": False, "instant_amperage_ma": 0,
              "amperage_ma": 0, "voltage_mv": 12180, "update_time_s": update_time_s, "update_age_s": 2.0,
              "fully_charged": False, "current_capacity_pct": 80,
              "power_telemetry": {name: None for name in ACCUMULATOR_FIELDS}, "adapter_watts": 140,
              "publication": True}
    telemetry = override.pop("power_telemetry", {})
    values["power_telemetry"].update(telemetry)
    values.update(override)
    return values


def contention_values(begin_ns: int, end_ns: int, outside=(), kernel_task=0.31) -> dict:
    """``contention.interval`` output (kernel_task excluded, as in window)."""
    rows = [{"pid": 310, "command": "WindowServer", "cpu_s_per_s": 0.01}, *outside]
    rows.sort(key=lambda row: (-row["cpu_s_per_s"], row["pid"]))
    return {"interval": {"monotonic_ns": [begin_ns, end_ns],
                         "monotonic_raw_ns": [begin_ns + RAW_OFFSET_NS, end_ns + RAW_OFFSET_NS],
                         "wall_ns": [begin_ns + WALL_OFFSET_NS, end_ns + WALL_OFFSET_NS]},
            "elapsed_s": (end_ns - begin_ns) / 1e9, "clean": all(row["cpu_s_per_s"] <= 0.05 for row in rows),
            "max_outside": rows[0], "outside_over_limit": [row for row in rows if row["cpu_s_per_s"] > 0.05],
            "outside_listed": [row for row in rows if row["cpu_s_per_s"] >= 0.005],
            "outside_total_cpu_s_per_s": sum(row["cpu_s_per_s"] for row in rows), "outside_process_count": 7,
            "tree_cpu_s_per_s": 0.97, "tree_process_count": 3, "kernel_task_cpu_s_per_s": kernel_task,
            "kernel_task_included": False, "unaccounted": [], "raw": []}


def clock_values(raw_ns: int, anchor_ns: int, frequency: bool) -> dict:
    return {"anchor": {"realtime_ns": raw_ns + anchor_ns, "monotonic_raw_ns": raw_ns, "read_skew_ns": 400,
                       "anchor_ns": anchor_ns},
            "frequency": frequency_probe(DRIFT_WORD) if frequency else None}


def disk_values(free_bytes: int, low_bytes: int = 10 * GIB) -> dict:
    target = {"path": "/runs", "copies": 1, "device": 1, "free_bytes": free_bytes, "total_bytes": 4096 * 10**9,
              "f_bavail": free_bytes // 4096, "f_frsize": 4096}
    return {"targets": [target], "low": [{"path": "/runs", "free_bytes": free_bytes, "low_bytes": low_bytes}]
            if free_bytes < low_bytes else []}


def write_journals(directory: Path, *, extra_publications=(), thermal_levels=(), contention_extra=(),
                   clock_steps=(), omit=(), battery_gap=None, contention_gap=None, disk_low=False) -> None:
    """Every module from 300 s before the first member to 300 s after the last, in L1's format.

    ``extra_publications``: (monotonic_ns, battery-value overrides); each is a
    gauge publication taking effect at that instant (rounded to L1's whole-second
    UpdateTime).  ``contention_extra``: ((lo, hi), {pid, command, cpu_s_per_s}).
    """
    directory.mkdir(parents=True, exist_ok=True)
    spans = [member_span_ns(row[0]) for row in MEMBERS]
    # An odd offset keeps the journal's sampling grid off every span edge.
    start, end = spans[0][0] - 300 * NS - 1_234_567, spans[-1][1] + 300 * NS
    journals = {name: L1Journal(name) for name in ("battery", "thermal", "contention", "clock", "disk")}
    for journal in journals.values():
        journal.write("session_start", start - NS, values={"pid": 4242, "argv": ["test"]})

    def update_of(monotonic_ns: int) -> int:
        return round((monotonic_ns + WALL_OFFSET_NS) / 1e9)

    publications = [(update_of(stamp), {}) for stamp in range(start, end, 60 * NS)]
    publications += [(update_of(stamp), dict(values)) for stamp, values in extra_publications]
    if battery_gap is not None:
        publications = [(update, values) for update, values in publications
                        if not battery_gap[0] <= update * NS - WALL_OFFSET_NS <= battery_gap[1]]
    for update, values in sorted(publications, key=lambda item: item[0]):
        effect = update * NS - WALL_OFFSET_NS
        journals["battery"].write("reading", effect + 2 * NS, effect + 2 * NS + 30_000_000,
                                  values=battery_values(update, **values))
    levels = dict(thermal_levels)
    for poll in range(start, end, 5 * NS):
        level = next((value for (lo, hi), value in levels.items() if lo <= poll <= hi), 0)
        journals["thermal"].write("reading", poll - 3_000_000, poll, values={"level": level, "source": "notifyutil"})
    journals["contention"].write("snapshot", start - 10 * NS)
    for begin in range(start, end, 10 * NS):
        if contention_gap is not None and begin < contention_gap[1] and contention_gap[0] < begin + 10 * NS:
            continue
        outside = [dict(row) for (lo, hi), row in contention_extra if lo < begin + 10 * NS and begin < hi]
        journals["contention"].write("interval", begin - 1_000_000, begin + 10 * NS + 1_000_000,
                                     values=contention_values(begin, begin + 10 * NS, outside))
    # Clock: 1 Hz around every member's stream, 5 s elsewhere; f every 5 s.
    dense = set()
    for lo, hi in spans:
        dense.update(range(lo - 30 * NS - 1_234_567, hi + 30 * NS, NS))
    polls = sorted(set(range(start, end, 5 * NS)) | dense)
    raw_start = start + RAW_OFFSET_NS
    anchor0 = 1_784_718_754_513_670_000
    for poll in polls:
        raw = poll + RAW_OFFSET_NS
        offset = sum(size for at, size in clock_steps if at <= poll)
        anchor = anchor0 + DRIFT_WORD * (raw - raw_start) // (kernel_clock.FREQUENCY_SCALE * 1_000_000) + offset
        journals["clock"].write("reading", poll - 600, poll, values=clock_values(raw, anchor, (poll - start) % (5 * NS) == 0))
    for poll in range(start, end, 60 * NS):
        journals["disk"].write("reading", poll - 500_000, poll, values=disk_values((5 if disk_low else 200) * GIB))
    for name, journal in journals.items():
        journal.write("session_end", end + NS, values={"reason": "test end"})
        if name not in omit:
            journal.dump(directory / f"{name}.jsonl")


# ---------------------------------------------------------------------------
# One synthetic window: measurement checkout, pack, ledger, custody, plan.
# ---------------------------------------------------------------------------

def fake_exclusions(flags, roster, spans, catalog):
    """A stand-in for L4's ``exclusions.compute`` reading L4's documented input shape.

    roster: {members: [{run_id, stage_id, units: [{cell_id, stratum,
    unit_id}]}], cells: [{cell_id, target, strata}]}; spans: {run_id:
    {monotonic_ns}}.  Catalog effects; a flagged member drops its whole unit;
    each declared stratum needs ``rules.cell_unit_minimum`` kept units.
    """
    minimum = int(((catalog.raw or {}).get("rules") or {}).get("cell_unit_minimum", 8))
    members = {member["run_id"]: member for member in roster["members"]}
    excluded: dict[str, set] = {}
    window = set()
    for flag in flags:
        effect, scope = catalog.effect(flag["code"]), flag["scope"]
        if effect == "EXCLUDE_WINDOW":
            window.add(flag["code"])
        elif effect == "EXCLUDE_MEMBER" and scope["level"] == "member":
            if scope["run_id"] in members:
                excluded.setdefault(scope["run_id"], set()).add(flag["code"])
        elif effect == "EXCLUDE_MEMBER":
            interval = flag["interval"]["monotonic_ns"]
            for run_id in members:
                span = (spans.get(run_id) or {}).get("monotonic_ns")
                if interval is None or span is None or (span[0] <= interval[1] and interval[0] <= span[1]):
                    excluded.setdefault(run_id, set()).add(flag["code"])
    units: dict[tuple, list] = {}
    for member in roster["members"]:
        for unit in member["units"]:
            units.setdefault((unit["cell_id"], unit["stratum"], unit["unit_id"]), []).append(member["run_id"])
    cells = []
    for cell in roster["cells"]:
        strata = sorted(set(cell["strata"]) | {key[1] for key in units if key[0] == cell["cell_id"]})
        keys = {stratum: sorted(key for key in units if key[:2] == (cell["cell_id"], stratum)) for stratum in strata}
        kept = {stratum: [key[2] for key in keys[stratum] if not any(run in excluded for run in units[key])]
                for stratum in strata}
        dropped = [{"stratum": key[1], "unit_id": key[2], "run_ids": sorted(units[key]),
                    "codes": sorted({code for run in units[key] for code in excluded.get(run, ())})}
                   for stratum in strata for key in keys[stratum] if any(run in excluded for run in units[key])]
        resolvable = bool(strata) and all(len(kept[stratum]) >= minimum for stratum in strata)
        cells.append({"cell_id": cell["cell_id"], "n_repeats": len(kept.get("repeat", [])),
                      "n_quads": len(kept.get("quad", [])), "kept_units": kept, "dropped_units": dropped,
                      "resolvable": resolvable})
        if cell.get("target", True) and not resolvable:
            window.add("cell.below_minimum")
    return {"members_excluded": [{"run_id": run_id, "codes": sorted(codes)} for run_id, codes in sorted(excluded.items())],
            "cells": cells, "claim_usable": not window, "reasons": sorted(window),
            "release_blocked": any(catalog.effect(flag["code"]) == "UNCLASSIFIED" for flag in flags)}


# The production exclusion function when lane L4 is present, else the fake.
EXCLUSIONS = h._l4_exclusions if L4_AVAILABLE else fake_exclusions


def l4_flag_line(code: str, **fields) -> dict:
    """A desk/arm/driver flag as L4's ``joulewise.flags.schema.make_flag`` writes it."""
    if L4_AVAILABLE:
        from joulewise.flags.schema import make_flag, make_scope, make_source
        return make_flag(code=code, family=fields.get("family", "RECORDS"), klass=fields.get("klass", "REPRESENTATION"),
                         scope=make_scope(fields.get("level", "window"), plan_id=PLAN_ID, attempt=1,
                                          run_id=fields.get("run_id")),
                         source=make_source(fields.get("stage", "arm"), fields.get("collector", "pack_tree")),
                         observed=fields.get("observed"), detail="test", emitted={"wall_s": 1.0, "monotonic_ns": 2,
                                                                                  "boot_session_uuid": None})
    ledger = h.FlagLedger(plan_id=PLAN_ID, attempt=1, catalog=h.Catalog.load(None), boot_session_uuid=None,
                          now=lambda: 1.0, monotonic_ns=lambda: 2)
    return ledger.emit(code, level=fields.get("level", "window"), run_id=fields.get("run_id"),
                       collector=fields.get("collector", "pack_tree"), stage=fields.get("stage", "arm"),
                       observed=fields.get("observed"), detail="test")


class Window:
    def __init__(self, root: Path, *, prefix_ledger=False, target_precheck=None, catalog_overrides=None,
                 journals=None, executed_overrides=None, frozen_pins=True, register_prompt_tokens=32,
                 acceptance_policy=None, sealed_inventory=True):
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
        self._build_repo(target_precheck, register_prompt_tokens, frozen_pins, acceptance_policy, sealed_inventory)
        self._build_catalog(catalog_overrides or {})
        self._build_runs()
        self._build_ledger(prefix_ledger)
        self._build_night(executed_overrides or {})
        write_journals(self.custody / "hazards" / "monitor", **(journals or {}))

    # -- measurement checkout and pack -------------------------------------
    def _build_repo(self, target_precheck, register_prompt_tokens, frozen_pins, acceptance_policy, sealed_inventory):
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
            "acceptance_policy": acceptance_policy if acceptance_policy is not None else {
                "issued_acceptance": {"path": ACCEPTANCE, "artifact_sha256": sha(ROOT / ACCEPTANCE)}},
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
        if sealed_inventory:  # L6's sealed inventory at its default location
            put(self.measurement / "configs/campaigns/v5_claim_25g83/sealed_inventory.json",
                {"head": H_CLAIM, "files": files})

    def _build_catalog(self, overrides):
        catalog = json.loads((FIXTURES / "flag_catalog.json").read_bytes())
        # Six members cannot fill the registered 8-of-10 minimum; one unit per
        # stratum keeps the unit rule observable in a window this small.
        catalog["rules"]["cell_unit_minimum"] = 1
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
        # L2's run_night._complete_chain_start record.
        put(night / "chain.started", {"epoch_s": 1786206000.0, "pgid": 999_999, "pid": 999_999,
                                      "monotonic_ns": CHAIN_STARTED_NS, "start_time": None})
        put(night / "chain.exited", {"epoch_s": 1786216000.0, "exit_code": 0, "monotonic_ns": 1})
        put(night / "result.json", {"aborted_reason": None, "artifacts": []})
        chain = self.custody / "chain.zsh"
        chain.write_text("#!/bin/zsh\necho b5 test chain\n")
        (self.custody / "chain.zsh.sha256").write_text(f"{sha(chain)}  chain.zsh\n")
        # L1's hazards.arm record: one entry per module and phase.
        put(self.custody / "hazards" / "arm.json", {
            "schema": "joulewise.hazard_arm.v1", "decision": "GO", "refused_at": None, "reasons": [],
            "hazards": {name: [{"phase": "instant", "measurement": {"schema": "joulewise.hazard_measurement.v1",
                                                                   "module": name, "error": None},
                                "verdict": {"schema": "joulewise.hazard_verdict.v1", "module": name, "status": "PASS",
                                            "reasons": [], "thresholds": {}, "observed": {}}}]
                        for name in ("clock", "battery", "thermal", "contention", "disk", "instrument")}})
        # L2's driver.executed_inventory record (night/executed_inventory.json).
        checkout = {"root": str(self.measurement), "head": H_CLAIM, "status_porcelain": "", "status_clean": True,
                    "files": dict(self.sealed_files), "errors": []}
        checkout["files"].update(executed_overrides.get("files", {}))
        for key in ("head", "status_porcelain"):
            if key in executed_overrides:
                checkout[key] = executed_overrides[key]
        put(night / "executed_inventory.json", {
            "schema": "joulewise.b5_executed_inventory.v1", "taken": {"wall_s": 1.0, "monotonic_ns": 1},
            "measurement_checkout": checkout, "chain": {"path": str(chain), "sha256": sha(chain)},
            "pack_root": str(self.pack)})
        # The shape of L2's write_window_plan.
        plan = {
            "schema": "joulewise.hazard_window_plan.v1", "plan_id": PLAN_ID, "receipt_class": "HAZARD_PACK",
            "t0_epoch_s": 1786205000.0, "window_max_s": 36000, "measurement_head": H_CLAIM,
            "measurement_root": str(self.measurement), "custody_root": str(self.custody),
            "chain_path": str(chain), "chain_sha256_path": str(self.custody / "chain.zsh.sha256"),
            "hazard_window": {
                "attempt": 1,
                "pack": {"pack_id": PACK_ID, "pack_root": str(self.pack)},
                "bracket_session_id": SESSION_ID,
                "thresholds": {},
                "bindings": {"claim_runs_root": str(self.claim), "bound_runs_root": str(self.bound),
                             "ledger_path": str(self.ledger), "pre_attempt_id": f"{SESSION_ID}-pre",
                             "post_attempt_id": f"{SESSION_ID}-post"}},
        }
        put(self.plan_path, plan)

    # -- running ---------------------------------------------------------------
    def harvest(self, *, seams=None, **kwargs):
        seams = seams or h.Seams(group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS,
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

    def dropped(self) -> set[str]:
        """Every member whose unit was dropped from any cell."""
        return {run for cell in self.exclusions()["cells"] for unit in cell["dropped_units"] for run in unit["run_ids"]}


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
    # verify (member.cooldown_evidence_unverified fires on every member, correctly).
    # Tests that isolate one member rule mark that code DISCLOSE.
    ISOLATE = {"member.cooldown_evidence_unverified": "DISCLOSE"}
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
        # The seed bundle has no #421 pair; the journal covers every member, so
        # the missing pair is the disclosed "covered" case (plan 3.5).
        self.assertEqual(member_codes - {"battery.capture_pair_missing_covered",
                                         "member.cooldown_evidence_unverified"}, set())
        for flag in flags:  # L4's flag schema, field for field
            self.assertEqual(h.flag_problems(flag), [], flag["code"])
        if L4_AVAILABLE:
            from joulewise.flags.schema import validate_flag
            self.assertEqual({flag["code"]: validate_flag(flag) for flag in flags if validate_flag(flag)}, {})
        self.assertNotIn("pack.identity_mismatch", window.codes())
        self.assertNotIn("code.executed_differs_from_sealed", window.codes())
        self.assertNotIn("model.identity_mismatch", window.codes())
        self.assertNotIn("clock.systematic", window.codes())
        # Window summary and exclusions are written; the scheduler reads claim_usable.
        summary = window.window_flags()
        self.assertEqual(summary["schema"], "joulewise.window_flags.v1")
        self.assertEqual(set(summary), {"schema", "window", "catalog", "hazards", "flags", "collector_errors",
                                        "exclusions"})
        self.assertEqual([phase["verdict"] for phase in summary["hazards"]["battery"]["arm"]], ["PASS"])
        self.assertEqual(summary["hazards"]["battery"]["continuous"]["journal"]["malformed"], 0)
        self.assertEqual(summary["flags"]["unclassified"], [])
        exclusions = window.exclusions()
        self.assertEqual(exclusions["members_excluded"], [])
        # One floor cell: the condition family, its repeats and its quad.
        self.assertEqual([(cell["cell_id"], cell["n_repeats"], cell["n_quads"], cell["resolvable"])
                          for cell in exclusions["cells"]], [(FAMILY, 2, 1, True)])
        self.assertNotIn("cell.below_minimum", exclusions["reasons"])
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
        excursion = ((start + end) // 2, {"instant_amperage_ma": -447, "amperage_ma": -380})
        window = self.window(journals={"extra_publications": [excursion]})
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        flagged = {flag["scope"]["run_id"] for flag in window.flags() if flag["code"] == "battery.member_span"}
        self.assertEqual(flagged, {target})
        battery = next(flag for flag in window.flags() if flag["code"] == "battery.member_span")
        self.assertEqual(battery["family"], "PHYSICS_IN_SPAN")
        self.assertIn("instant_amperage_above_limit", battery["observed"]["violations"][0]["reasons"])
        self.assertEqual({row["run_id"] for row in window.exclusions()["members_excluded"]}, {target})
        self.assertEqual(window.dropped(), set(QUAD))  # the flagged member takes its whole quad
        (cell,) = window.exclusions()["cells"]
        self.assertEqual((cell["cell_id"], cell["n_repeats"], cell["n_quads"], cell["resolvable"]),
                         (FAMILY, 2, 0, False))
        self.assertIn("cell.below_minimum", window.exclusions()["reasons"])
        roster = json.loads((window.archive / "derived" / "roster.json").read_bytes())
        member = next(row for row in roster["members"] if row["run_id"] == target)
        self.assertEqual(member["units"], [{"cell_id": FAMILY, "stratum": "quad", "unit_id": "b5t-b01"}])
        self.assertEqual(roster["cells"], [{"cell_id": FAMILY, "target": True, "strata": ["quad", "repeat"]}])

    def test_missing_bundle_file_is_bytes_missing_and_harvest_completes(self):
        window = self.window()
        (window.claim / "b5t-abs-r02" / "events.jsonl").unlink()
        shutil.rmtree(window.claim / "b5t-cmp-b01-a2")
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        self.assertIn("member.bytes_missing", window.codes("b5t-abs-r02"))
        self.assertIn("member.bytes_missing", window.codes("b5t-cmp-b01-a2"))
        excluded = {row["run_id"] for row in window.exclusions()["members_excluded"]}
        self.assertTrue({"b5t-abs-r02", "b5t-cmp-b01-a2"} <= excluded)
        self.assertTrue(set(QUAD) <= window.dropped())
        self.assertNotIn("b5t-abs-r01", window.dropped())

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
        self.assertIn("member.strict_validation_failed", codes)
        self.assertIn("b5t-abs-r01", {row["run_id"] for row in window.exclusions()["members_excluded"]})
        self.assertNotIn("member.strict_validation_failed", window.codes("b5t-abs-r02"))

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
        self.assertIn("member.config_not_in_inventory", window.codes("b5t-abs-r01"))
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
                                  {"pid": 77, "command": "fseventsd", "cpu_s_per_s": 1.84})],
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
        precheck = next(flag for flag in window.flags() if flag["code"] == "member.target_phase_precheck_failed"
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
        self.assertIn("model.identity_unpinned", window.codes())
        self.assertNotIn("model.identity_mismatch", window.codes())

    def test_earlier_flag_files_are_absorbed_and_malformed_lines_recorded(self):
        """Desk, arm and driver flags, as L4's make_flag and sink write them, reach the exclusion function."""
        window = self.window()
        arm_flag = l4_flag_line("model.identity_mismatch", family="MODEL_IDENTITY", klass="NUMBER",
                                collector="model_identity", observed={"unit": "b5t-unit"})
        driver_flag = l4_flag_line("records.collector_failed", stage="window", collector="driver",
                                   observed={"collector": "lineage", "error_type": "OSError"})
        self.assertEqual(set(arm_flag), h.FLAG_KEYS)  # schema_version included
        flags_dir = window.custody / "flags"
        flags_dir.mkdir(parents=True)
        (flags_dir / "arm.jsonl").write_text(json.dumps(arm_flag) + "\n{not json\n")
        (flags_dir / "driver.jsonl").write_text(json.dumps(driver_flag) + "\n"
                                                + json.dumps({**driver_flag, "detail": "edited"}) + "\n")
        window.harvest()
        ids = {flag["flag_id"] for flag in window.flags()}
        self.assertTrue({arm_flag["flag_id"], driver_flag["flag_id"]} <= ids)
        malformed = sorted((flag["observed"]["file"], flag["observed"]["line"]) for flag in window.flags()
                           if flag["code"] == "records.malformed_flag")
        self.assertEqual(malformed, [("arm.jsonl", 2)])  # an edited detail keeps a valid flag_id: same fact
        # The arm-time model mismatch excludes the window; the malformed line
        # is never classified, so the release event is blocked until read.
        self.assertIn("model.identity_mismatch", window.exclusions()["reasons"])
        self.assertIn("records.malformed_flag", window.window_flags()["flags"]["unclassified"])

    def test_unknown_catalog_entry_is_reported_unclassified(self):
        window = self.window()
        catalog_path = window.measurement / "configs/campaigns/v5_claim_25g83/flag_catalog.json"
        catalog = json.loads(catalog_path.read_bytes())
        del catalog["codes"]["battery.capture_pair_missing_covered"]
        put(catalog_path, catalog)
        window.harvest()
        self.assertIn("battery.capture_pair_missing_covered", window.window_flags()["flags"]["unclassified"])
        self.assertTrue(window.window_flags()["exclusions"]["release_blocked"])

    def test_bundle_outside_roster_is_ignored_and_recorded(self):
        window = self.window()
        subprocess.run(["/bin/cp", "-c", "-R", str(window.claim / "b5t-abs-r01"), str(window.claim / "stray-r99")],
                       check=True)
        window.harvest()
        self.assertIn("roster.not_in_plan", window.codes("stray-r99"))
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
        self.assertNotIn("calibration.session_not_bound", window.codes())
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
        flag = next(flag for flag in window.flags() if flag["code"] == "calibration.session_not_bound")
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

        window.harvest(seams=h.Seams(group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS,
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

        window.harvest(seams=h.Seams(group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS,
                                     runner=runner))
        self.assertIn("g3.recompute_failed", window.codes())
        self.assertIn("g3.assertion_failed", window.codes())
        self.assertTrue((window.archive / "withheld" / "transcripts" / "g3.txt").is_file())

    def g3_window(self, name: str, runner, **harvest) -> Window:
        window = Window(self.tmp / name, prefix_ledger=True, catalog_overrides=self.ISOLATE)
        (window.pack / "analysis_manifest_v3.json").write_text("{}\n")
        (window.claim / "whole-window-verdict.json").write_text("{}\n")
        (window.claim / "bracket-binding.json").write_text("{}\n")
        window.harvest(seams=h.Seams(group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS,
                                     runner=runner), **harvest)
        return window

    def test_g3_recompute_that_did_not_pass_is_never_silent(self):
        """Review F3: F5-2 is the one independent recompute of the whole-window verdict.

        Unless the report exists and holds F5-2 PASS, g3.recompute_failed
        (EXCLUDE_WINDOW) fires: a crashed checker, a timeout, an exit outside
        {0, 1}, an F5-2 SKIP behind a failed S11-A2, or a skipped G3.
        """
        def report(rows, returncode=0):
            def runner(argv, **kwargs):
                Path(argv[argv.index("--report-json") + 1]).write_text(json.dumps({"assertions": rows}))
                return SimpleNamespace(returncode=returncode, stdout="", stderr="")
            return runner

        def crashed(argv, **kwargs):  # no report: an ImportError traceback
            return SimpleNamespace(returncode=1, stdout="", stderr="Traceback ...\nImportError: x\n")

        def timed_out(argv, **kwargs):
            raise subprocess.TimeoutExpired(argv, 3600)

        cases = {
            "crashed": (crashed, {}, {"reason": "report_absent", "returncode": 1, "f5_2": []}),
            "timed_out": (timed_out, {}, {"reason": "runner_error", "error_type": "TimeoutExpired"}),
            "f52_skipped": (report([{"id": "S11-A2", "status": "FAIL"}, {"id": "F5-2", "status": "SKIP"}], 1), {},
                            {"reason": "f5_2_not_passed", "returncode": 1, "f5_2": ["SKIP"]}),
            "bad_exit": (report([{"id": "F5-2", "status": "PASS"}], 2), {},
                         {"reason": "f5_2_not_passed", "returncode": 2, "f5_2": ["PASS"]}),
            "skipped": (report([{"id": "F5-2", "status": "PASS"}]), {"run_g3": False}, {"reason": "g3_skipped"}),
        }
        for name, (runner, harvest, observed) in cases.items():
            with self.subTest(name):
                window = self.g3_window(name, runner, **harvest)
                (flag,) = [flag for flag in window.flags() if flag["code"] == "g3.recompute_failed"]
                self.assertEqual(flag["observed"], observed)
                self.assertIn("g3.recompute_failed", window.exclusions()["reasons"])
        passed = self.g3_window("passed", report([{"id": "S11-A2", "status": "PASS"}, {"id": "F5-2", "status": "PASS"},
                                                  {"id": "S11-A5", "status": "FAIL"}], 1))
        self.assertNotIn("g3.recompute_failed", passed.codes())
        self.assertIn("g3.assertion_failed", passed.codes())


_REAL_SEAMS = h.Seams


class CliTests(WindowTestCase):
    def run_cli(self, window, alive, *extra):
        from scripts import harvest_b5_window as cli

        def seams(**kwargs):  # the CLI builds Seams(workers=...); only the seams change
            return _REAL_SEAMS(group_alive=lambda pgid: alive, exclusions_compute=EXCLUSIONS,
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
# Pure joins and parsers, on lines in L1's journal format.
# ---------------------------------------------------------------------------

def parsed(journal: L1Journal) -> list:
    return sorted((reading for reading in (h.parse_monitor_line(journal.module, line) for line in journal.lines)
                   if reading is not None), key=lambda item: item.monotonic_ns)


def battery_journal(publications, start_s=0, end_s=600) -> list:
    """A gauge publishing at each (second, overrides); read 2 s after it appears and 30 s later."""
    journal = L1Journal("battery")
    for second, overrides in publications:
        update = second + 10_000
        effect = update * NS - WALL_OFFSET_NS
        for delay in (2, 32):
            if start_s <= second + delay < end_s:
                journal.write("reading", effect + delay * NS, effect + delay * NS + 1_000,
                              values=battery_values(update, **overrides))
    return parsed(journal)


def publication_ns(second: int) -> int:
    return (second + 10_000) * NS - WALL_OFFSET_NS


class JoinTests(unittest.TestCase):
    T = h.DEFAULT_THRESHOLDS

    def test_in_force_publications(self):
        self.assertEqual(h.in_force([0, 60, 120, 180], 70, 100), [1, 2])
        self.assertEqual(h.in_force([0, 60, 120, 180], 60, 120), [1, 2])
        self.assertEqual(h.in_force([0, 60, 120, 180], 61, 179), [1, 2, 3])
        self.assertEqual(h.in_force([], 1, 2), [])

    def test_publication_time_is_update_time_through_the_readings_own_clocks(self):
        readings = battery_journal([(0, {}), (60, {})])
        self.assertEqual([item.monotonic_ns for item in h.battery_publications(readings)],
                         [publication_ns(0), publication_ns(60)])  # one per UpdateTime, not per read

    def test_publication_before_the_span_is_in_force(self):
        readings = battery_journal([(0, {}), (60, {"instant_amperage_ma": -447}), (120, {}), (180, {})])
        span = [publication_ns(70), publication_ns(100)]
        self.assertIn("battery.member_span", [code for code, *_ in h.battery_member_flags(span, readings, self.T)])
        clean = h.battery_member_flags([publication_ns(130), publication_ns(170)], readings, self.T)
        self.assertNotIn("battery.member_span", [code for code, *_ in clean])

    def test_charging_and_disconnected_publications(self):
        for values, reason in (({"is_charging": True}, "is_charging"),
                               ({"external_connected": False}, "external_disconnected"),
                               ({"amperage_ma": 250}, "amperage_above_limit")):
            readings = battery_journal([(0, {}), (60, values), (120, {})])
            ((code, observed, _interval), *_rest) = h.battery_member_flags(
                [publication_ns(65), publication_ns(70)], readings, self.T)
            self.assertEqual(code, "battery.member_span")
            self.assertIn(reason, observed["violations"][0]["reasons"])

    def test_float_reading_at_the_limit_passes(self):
        readings = battery_journal([(0, {}), (60, {"instant_amperage_ma": -200}), (120, {})])
        codes = [code for code, *_ in h.battery_member_flags([publication_ns(65), publication_ns(70)], readings, self.T)]
        self.assertEqual(codes, [])

    def test_publication_gap_over_120_s_is_unmeasured(self):
        readings = battery_journal([(0, {}), (200, {}), (260, {})], end_s=300)
        flagged = [code for code, *_ in h.battery_member_flags([publication_ns(100), publication_ns(110)],
                                                               readings, self.T)]
        self.assertIn("battery.unmeasured", flagged)
        fine = [code for code, *_ in h.battery_member_flags([publication_ns(210), publication_ns(220)],
                                                            readings, self.T)]
        self.assertNotIn("battery.unmeasured", fine)

    def test_failed_ioreg_reads_observe_nothing(self):
        journal = L1Journal("battery")
        for second in (0, 60, 120, 180):
            effect = publication_ns(second)
            journal.write("reading", effect + 2 * NS, values={"returncode": 1}, error="ioreg exit code 1")
        readings = parsed(journal)
        self.assertEqual({reading.status for reading in readings}, {"error"})
        codes = [code for code, *_ in h.battery_member_flags([publication_ns(70), publication_ns(80)], readings, self.T)]
        self.assertEqual(codes, ["battery.unmeasured"])

    def test_accumulator_is_diagnostic_until_units_are_confirmed(self):
        telemetry = [{"AccumulatedBatteryPower": 100, "BatteryPowerAccumulatorCount": 10},
                     {"AccumulatedBatteryPower": 1300, "BatteryPowerAccumulatorCount": 70}, {}]
        readings = battery_journal([(second, {"power_telemetry": values})
                                    for second, values in zip((0, 60, 120), telemetry)])
        span = [publication_ns(10), publication_ns(20)]
        unconfirmed = [code for code, *_ in h.battery_member_flags(span, readings, self.T)]
        self.assertIn("battery.accumulator_diagnostic", unconfirmed)
        self.assertNotIn("battery.accumulator_excursion", unconfirmed)
        confirmed = dict(self.T, battery_accumulator_watts_per_unit=1.0)
        codes = [code for code, *_ in h.battery_member_flags(span, readings, confirmed)]
        self.assertIn("battery.accumulator_excursion", codes)  # 1200 W·count / 60 counts = 20 W > 0.2 A × 12.18 V

    def test_thermal_nonzero_and_unmeasured(self):
        journal = L1Journal("thermal")
        for second in range(0, 100, 5):
            journal.write("reading", second * NS, values={"level": 1 if second == 50 else 0, "source": "notifyutil"})
        readings = parsed(journal)
        codes = [code for code, *_ in h.thermal_member_flags([48 * NS, 52 * NS], readings, self.T)]
        self.assertEqual(codes, ["thermal.os_level_nonzero"])
        sparse = L1Journal("thermal")
        for second in (0, 40):
            sparse.write("reading", second * NS, values={"level": 0, "source": "notifyutil"})
        codes = [code for code, *_ in h.thermal_member_flags([10 * NS, 20 * NS], parsed(sparse), self.T)]
        self.assertEqual(codes, ["thermal.unmeasured"])
        failed = L1Journal("thermal")
        for second in range(0, 100, 5):
            failed.write("reading", second * NS, values={"level": None, "source": "notifyutil"},
                         error="notifyutil exit code 1")
        codes = [code for code, *_ in h.thermal_member_flags([48 * NS, 52 * NS], parsed(failed), self.T)]
        self.assertEqual(codes, ["thermal.unmeasured"])

    def test_contention_counts_only_outside_processes_above_five_percent(self):
        journal = L1Journal("contention")
        journal.write("snapshot", -NS)
        journal.write("interval", 0, 10 * NS, values=contention_values(0, 10 * NS, [
            {"pid": 400, "command": "mds", "cpu_s_per_s": 0.05}], kernel_task=0.9))
        journal.write("interval", 10 * NS, 20 * NS, values=contention_values(10 * NS, 20 * NS, [
            {"pid": 350, "command": "mediaanalysisd", "cpu_s_per_s": 1.14}], kernel_task=0.9))
        readings = parsed(journal)
        self.assertEqual(h.contention_member_flags([2 * NS, 3 * NS], readings, self.T), [])
        ((code, observed, _interval),) = h.contention_member_flags([12 * NS, 13 * NS], readings, self.T)
        self.assertEqual((code, observed["offenders"][0]["command"]), ("contention.request_overlap", "mediaanalysisd"))
        ((code, observed, _interval),) = h.contention_member_flags([18 * NS, 25 * NS], readings, self.T)[-1:]
        self.assertEqual(code, "contention.unmeasured")
        # Named by the last covering interval's end, not by the request's end.
        self.assertEqual(observed["holes_monotonic_ns"], [[20 * NS, None]])
        ((code, observed, interval),) = h.contention_member_flags([25 * NS, 26 * NS], readings, self.T)
        self.assertEqual((code, observed["holes_monotonic_ns"], interval),
                         ("contention.unmeasured", [[20 * NS, None]], {"monotonic_ns": None}))

    def test_a_failed_ps_interval_covers_nothing(self):
        journal = L1Journal("contention")
        journal.write("interval", 0, 10 * NS, values=contention_values(0, 10 * NS))
        journal.write("interval", 10 * NS, 20 * NS, values={"interval": {"monotonic_ns": [10 * NS, 20 * NS]},
                                                            "clean": None}, error="ps exit code 1")
        codes = [code for code, *_ in h.contention_member_flags([12 * NS, 13 * NS], parsed(journal), self.T)]
        self.assertEqual(codes, ["contention.unmeasured"])

    def test_clock_steps_net_of_the_frequency_word(self):
        journal = L1Journal("clock")
        word = DRIFT_WORD
        for second in range(20):
            raw = second * NS + RAW_OFFSET_NS
            anchor = 10**15 + word * (second * NS) // (kernel_clock.FREQUENCY_SCALE * 10**6) \
                + (6_000_000 if second >= 10 else 0)
            values = clock_values(raw, anchor, frequency=second % 5 == 0)
            if second == 15:
                values["frequency"] = frequency_probe(round(-3.0 * kernel_clock.FREQUENCY_SCALE))
            journal.write("reading", second * NS - 600, second * NS, values=values)
        steps, changes = h.clock_steps(parsed(journal), self.T)
        self.assertEqual([step["interval_monotonic_ns"] for step in steps], [[9 * NS - 600, 10 * NS]])
        self.assertEqual([(change["previous_ppm"], change["ppm"]) for change in changes],
                         [(word / kernel_clock.FREQUENCY_SCALE, -3.0)])
        drift_only = L1Journal("clock")
        big = round(-3.17 * 300 * kernel_clock.FREQUENCY_SCALE)  # drift a 1 ms step test would mistake
        for second in range(5):
            drift_only.write("reading", second * NS, values={"anchor": {
                "anchor_ns": big * (second * NS) // (kernel_clock.FREQUENCY_SCALE * 10**6),
                "monotonic_raw_ns": second * NS, "read_skew_ns": 0, "realtime_ns": 0},
                "frequency": frequency_probe(big)})
        self.assertEqual(h.clock_steps(parsed(drift_only), self.T)[0], [])

    def test_disk_low_from_targets_and_marker(self):
        journal = L1Journal("disk")
        journal.write("reading", 0, values=disk_values(200 * GIB))
        journal.write("reading", 60 * NS, values=disk_values(5 * GIB))
        journal.write("event", 61 * NS, values={"code": "disk.low", "low": [], "marker": "x"})
        low, paths = h.disk_low(parsed(journal), self.T)
        self.assertEqual(([reading.monotonic_ns for reading in low], paths), ([60 * NS, 61 * NS], ["/runs"]))

    def test_monitor_line_shapes(self):
        line = {"schema": "joulewise.hazard_journal.v1", "module": "thermal", "session": "1-1", "seq": 2,
                "kind": "reading", "started": l1_stamp(4), "finished": l1_stamp(5),
                "values": {"level": 0, "source": "notify_get_state"}, "error": None, "raw": []}
        reading = h.parse_monitor_line("thermal", line)
        self.assertEqual((reading.monotonic_ns, reading.started_monotonic_ns, reading.values["level"], reading.status),
                         (5, 4, 0, "ok"))
        self.assertIsNone(h.parse_monitor_line("thermal", {**line, "kind": "session_start"}))
        for bad in ({**line, "schema": "x"}, {**line, "module": "battery"}, {**line, "kind": "mystery"},
                    {**line, "finished": {"monotonic_ns": 5}}, {k: v for k, v in line.items() if k != "started"},
                    # the shapes the earlier harvest invented are not L1's
                    {"module": "thermal", "monotonic_ns": 5, "values": {"level": 0}}):
            with self.assertRaises(h.MonitorLineError):
                h.parse_monitor_line("thermal", bad)
        interval = {**line, "module": "contention", "kind": "interval", "values": {"clean": True}}
        with self.assertRaises(h.MonitorLineError):  # an interval line must carry its interval
            h.parse_monitor_line("contention", interval)

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


class L1JournalFormatTests(unittest.TestCase):
    """Review F1: the harvest reads the journals L1's monitor writes.

    ``tests/fixtures/b5_harvest/l1_monitor`` was written by L1's own
    ``joulewise.hazards.monitor.Monitor`` under L1's FakeMac (see its
    generator).  Before this fix the harvest parsed 0 of its readings and
    every member came out battery/thermal/contention.unmeasured.
    """

    T = h.DEFAULT_THRESHOLDS

    @classmethod
    def setUpClass(cls):
        cls.expected = json.loads((L1_JOURNALS / "expected.json").read_bytes())
        cls.journals, cls.malformed = {}, {}
        for module in h.MONITOR_MODULES:
            cls.journals[module], cls.malformed[module] = h.read_monitor_journal(L1_JOURNALS / f"{module}.jsonl", module)

    def l5_codes(self, span, request) -> set[str]:
        codes = set()
        for join, module, window in ((h.battery_member_flags, "battery", span), (h.thermal_member_flags, "thermal", span),
                                     (h.contention_member_flags, "contention", request),
                                     (h.clock_member_flags, "clock", span)):
            codes |= {code for code, *_ in join(window, self.journals[module], self.T)}
        steps, _changes = h.clock_steps(self.journals["clock"], self.T)
        codes |= {"clock.step_overlap" for step in steps if h._overlaps(step["interval_monotonic_ns"], span)}
        return codes

    def test_every_line_parses(self):
        self.assertEqual(self.malformed, {module: 0 for module in h.MONITOR_MODULES})
        counts = {module: sum(reading.status == "ok" for reading in readings)
                  for module, readings in self.journals.items()}
        self.assertEqual(counts, {"battery": 15, "thermal": 84, "contention": 41, "clock": 420, "disk": 7})

    def test_joins_equal_l1s_own_join_on_l1s_bytes(self):
        physics = {"battery.member_span", "battery.unmeasured", "thermal.os_level_nonzero", "thermal.unmeasured",
                   "contention.request_overlap", "contention.unmeasured", "clock.step_overlap", "clock.unmeasured"}
        for name, case in sorted(self.expected["cases"].items()):
            with self.subTest(name):
                span = case["span"]["monotonic_ns"]
                request = (case["request"] or case["span"])["monotonic_ns"]
                self.assertEqual(self.l5_codes(span, request) & physics, set(case["l1_codes"]) & physics)
        # The cases cover each rule firing at least once.
        fired = set().union(*(case["l1_codes"] for case in self.expected["cases"].values()))
        self.assertTrue({"battery.member_span", "contention.request_overlap", "thermal.os_level_nonzero",
                         "clock.step_overlap"} <= fired)

    def test_window_events_clock_step_and_disk_low(self):
        steps, changes = h.clock_steps(self.journals["clock"], self.T)
        self.assertEqual(len(steps), 1)
        self.assertAlmostEqual(steps[0]["residual_move_ns"], 6_000_000, delta=1_000)
        self.assertEqual(changes, [])
        low, paths = h.disk_low(self.journals["disk"], self.T)
        self.assertTrue(low)
        self.assertEqual(paths, ["/runs"])
        self.assertEqual(set(self.expected["window_events"]), {"clock.step", "disk.low"})

    def test_kernel_task_rate_is_read_from_the_interval(self):
        rates = {round(reading.values["kernel_task_cpu_s_per_s"], 3) for reading in self.journals["contention"]}
        self.assertEqual(rates, {self.expected["kernel_task_cpu_s_per_s"]})

    def test_the_synthetic_writer_writes_l1s_line_shapes(self):
        """Every (module, kind, value keys) the test writer emits occurs in L1's own journals."""
        def shape(line):
            values = line.get("values")
            keys = tuple(sorted(values)) if isinstance(values, dict) else None
            nested = tuple(sorted(values["power_telemetry"])) if isinstance(values, dict) \
                and isinstance(values.get("power_telemetry"), dict) else None
            return (line["module"], line["kind"], tuple(sorted(line)), tuple(sorted(line["started"])), keys, nested)

        real = set()
        for module in (*h.MONITOR_MODULES, "monitor"):
            for raw in (L1_JOURNALS / f"{module}.jsonl").read_text().splitlines():
                real.add(shape(json.loads(raw)))
        with tempfile.TemporaryDirectory(dir=REAL_TMP) as scratch:
            directory = Path(scratch)
            write_journals(directory, extra_publications=[(member_span_ns(MEMBERS[0][0])[0], {})])
            synthetic = {shape(json.loads(raw)) for module in h.MONITOR_MODULES
                         for raw in (directory / f"{module}.jsonl").read_text().splitlines()
                         if json.loads(raw)["kind"] not in ("session_start", "session_end")}
        self.assertEqual(synthetic - real, set())

    @unittest.skipUnless(L1_AVAILABLE, "lane L1's joulewise.hazards is not in this tree")
    def test_live_l1_member_findings_agree(self):
        from joulewise.hazards import monitor
        journals = {name: monitor.read_journal(L1_JOURNALS / f"{name}.jsonl")[0] for name in monitor.JOURNALS}
        for name, case in sorted(self.expected["cases"].items()):
            with self.subTest(name):
                live = {finding["code"] for finding in monitor.member_findings(
                    journals, span=case["span"], request=case["request"])}
                self.assertEqual(sorted(live), case["l1_codes"])


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
                                                             first["source"], first["interval"]))
        self.assertEqual(first["schema_version"], "joulewise.flag.v1")
        self.assertEqual(h.flag_problems(first), [])
        # Two intervals are two facts (L4's flag id covers the interval).
        later = ledger.emit("disk.low", level="window", collector="monitor", observed={"readings_below": 1},
                            interval={"monotonic_ns": [5, 6]})
        self.assertNotEqual(later["flag_id"], first["flag_id"])
        self.assertEqual(first["catalog_sha256"], sha(FIXTURES / "flag_catalog.json"))
        self.assertEqual(first["scope"]["attempt"], 2)
        self.assertEqual(catalog.effect("disk.low"), "DISCLOSE")
        self.assertEqual(catalog.effect("not.a.code"), "UNCLASSIFIED")
        with self.assertRaises(KeyError):
            ledger.emit("not.a.code", level="window", collector="x")
        with self.assertRaises(ValueError):
            ledger.emit("disk.low", level="window", collector="x", observed={"bad": float("nan")})

    def test_every_catalog_fixture_code_is_an_emitted_code(self):
        """Review F2: the fixture is a joulewise.flag_catalog.v1 document (L4's loader accepts it)."""
        catalog = json.loads((FIXTURES / "flag_catalog.json").read_bytes())
        self.assertEqual(catalog["schema_version"], "joulewise.flag_catalog.v1")
        self.assertEqual(set(catalog) - {"schema_version", "codes", "rules", "notes"}, set())
        self.assertEqual(catalog["rules"], {"cell_unit_minimum": 8})
        # Every emitted code but the never-classified one, which must block release.
        self.assertEqual(set(catalog["codes"]), set(h.CODES) - h.NEVER_CLASSIFIED_CODES)
        for code, entry in catalog["codes"].items():
            self.assertRegex(code, h.CODE_RE)
            self.assertEqual(set(entry) - {"family", "klass", "effect", "blinding", "note"}, set())
            self.assertIn(entry["effect"], h.EFFECTS)
            self.assertEqual((entry["family"], entry["klass"], entry["blinding"]),
                             (h.CODES[code].family, h.CODES[code].klass, h.CODES[code].blinding))

    @unittest.skipUnless(L4_AVAILABLE, "lane L4's joulewise.flags is not in this tree")
    def test_catalog_and_codes_agree_with_l4(self):
        from joulewise.flags import catalog as l4
        loaded = l4.load_catalog(FIXTURES / "flag_catalog.json")
        self.assertEqual(loaded.cell_unit_minimum, 8)
        draft = l4.draft_catalog()
        self.assertEqual(set(h.CODES) - set(draft.codes), set(h.L5_ONLY_CODES))
        self.assertEqual(h.NEVER_CLASSIFIED_CODES, set(l4.NEVER_CLASSIFIED_CODES) & set(h.CODES))
        for code in set(h.CODES) & set(draft.codes):
            entry = draft.codes[code]
            self.assertEqual((entry["family"], entry["klass"], entry["blinding"]),
                             (h.CODES[code].family, h.CODES[code].klass, h.CODES[code].blinding), code)
            self.assertEqual(loaded.effect(code), entry["effect"], code)

    def test_flag_problems_rejects_what_is_not_a_flag(self):
        ledger = h.FlagLedger(plan_id="p", attempt=1, catalog=h.Catalog.load(None), boot_session_uuid=None)
        good = ledger.emit("battery.member_span", level="member", run_id="r1", collector="t",
                           interval={"monotonic_ns": [1, 2]})
        variants = self.flag_variants(good)
        self.assertEqual(h.flag_problems(good), [])
        for name, variant in variants.items():
            self.assertTrue(h.flag_problems(variant), name)
        if L4_AVAILABLE:  # the same verdicts as L4's validate_flag, which owns the schema
            from joulewise.flags.schema import validate_flag
            self.assertEqual(validate_flag(good), [])
            self.assertEqual({name: bool(validate_flag(variant)) for name, variant in variants.items()},
                             {name: True for name in variants})

    @staticmethod
    def flag_variants(good: dict) -> dict:
        def without(key):
            return {k: v for k, v in good.items() if k != key}
        return {
            "no_schema_version": without("schema_version"),
            "id_without_interval": {**good, "flag_id": h.sha256_bytes(h.canonical_json_bytes(
                {key: good[key] for key in ("code", "scope", "observed", "source")}))[:20]},
            "extra_field": {**good, "note": "x"},
            "wrong_flag_id": {**good, "flag_id": "0" * 20},
            "interval_not_in_id": {**good, "interval": {**good["interval"], "monotonic_ns": [1, 3]}},
            "member_without_run_id": {**good, "scope": {**good["scope"], "run_id": None}},
            "bad_level": {**good, "scope": {**good["scope"], "level": "cell"}},
            "unordered_interval": {**good, "interval": {**good["interval"], "monotonic_ns": [2, 1]}},
            "absolute_evidence": {**good, "evidence": [{"path": "/abs", "sha256": "a" * 64}]},
            "bad_stage": {**good, "source": {**good["source"], "stage": "later"}},
        }

    def test_restricted_reasons(self):
        self.assertTrue(h.restricted_reason("anchor_energy_envelope_exceeds_quarter_metric"))
        self.assertFalse(h.restricted_reason("cadence_ratio_below_threshold"))
        self.assertFalse(h.restricted_reason("instrument_calibration_missing"))

    def test_inventory_shapes(self):
        digest = "b" * 64
        self.assertEqual(h._inventory_map({"head": "h", "files": {"a": digest}}), ({"a": digest}, "h"))
        self.assertEqual(h._inventory_map({"files": [{"path": "a", "sha256": digest}]}), ({"a": digest}, None))
        self.assertEqual(h._inventory_map({"a": digest, "head": "h"}), ({"a": digest}, "h"))
        # L2's driver.executed_inventory record.
        l2 = {"schema": "joulewise.b5_executed_inventory.v1", "chain": {"path": "c", "sha256": digest},
              "measurement_checkout": {"head": "h", "status_porcelain": "", "files": {"joulewise/x.py": digest}}}
        self.assertEqual(h._inventory_map(l2), ({"joulewise/x.py": digest}, "h"))

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


class ExclusionSeamTests(unittest.TestCase):
    """Review F2: the roster and spans reach L4's ``exclusions.compute`` in L4's documented shape.

    Before the fix L4 saw ``cells``/``unit_kind`` instead of
    ``units``/``stratum`` and ``member`` instead of ``monotonic_ns``: zero
    units per cell, so every clean window came out ``cell.below_minimum``.
    """

    ALPHA = ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5"
    GAMMA = ROOT / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"

    def inputs(self, pack, **kwargs):
        roster = h.build_roster(pack, ROOT)
        spans = {member["run_id"]: {"member": [(index + 1) * 100 * NS, (index + 1) * 100 * NS + 50 * NS],
                                    "request": [(index + 1) * 100 * NS + 10 * NS, (index + 1) * 100 * NS + 40 * NS]}
                 for index, member in enumerate(roster["members"])}
        bundles = [{"bundle_id": f"claim/{run_id}", "run_id": run_id, "attempt": None,
                    "created_monotonic_ns": span["member"][0]} for run_id, span in spans.items()]
        document, spans_document = h.l4_exclusion_inputs(roster, spans, plan_id="plan", attempt=1,
                                                         chain_started_monotonic_ns=50 * NS, bundles=bundles, **kwargs)
        return roster, document, spans_document

    def test_floor_cells_are_condition_families_with_repeat_and_quad_strata(self):
        _roster, document, spans = self.inputs(self.ALPHA)
        families = ["df-ph-decode-qwen3-1p7b", "df-ph-prefill-p2048-qwen3-1p7b", "df-ph-prefill-p42-qwen3-1p7b"]
        self.assertEqual(document["cells"], [{"cell_id": family, "target": True, "strata": ["quad", "repeat"]}
                                             for family in families])
        units: dict[tuple, list] = {}
        for member in document["members"]:
            self.assertEqual(set(member), {"run_id", "stage_id", "kind", "units"})
            for unit in member["units"]:
                self.assertEqual(set(unit), {"cell_id", "stratum", "unit_id"})
                units.setdefault((unit["cell_id"], unit["stratum"], unit["unit_id"]), []).append(member["run_id"])
        per_stratum: dict[tuple, int] = {}
        for cell_id, stratum, _unit in units:
            per_stratum[(cell_id, stratum)] = per_stratum.get((cell_id, stratum), 0) + 1
        self.assertEqual(per_stratum, {(family, stratum): 10 for family in families for stratum in ("quad", "repeat")})
        self.assertEqual({len(runs) for (_cell, stratum, _unit), runs in units.items() if stratum == "quad"}, {4})
        self.assertEqual(sum(not member["units"] for member in document["members"]), 19)  # auxiliaries feed no cell
        (first, *_rest) = spans.values()
        self.assertEqual(set(first), {"monotonic_ns", "request_monotonic_ns", "stage_id", "bundle_id"})
        self.assertEqual((document["plan_id"], document["attempt"], document["chain_started_monotonic_ns"]),
                         ("plan", 1, 50 * NS))
        self.assertEqual(len(document["bundles"]), 119)

    def test_contrast_cells_are_quads_only(self):
        _roster, document, _spans = self.inputs(self.GAMMA)
        self.assertEqual([(cell["cell_id"], cell["strata"]) for cell in document["cells"]],
                         [("ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b", ["quad"]),
                          ("ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b", ["quad"])])

    @unittest.skipUnless(L4_AVAILABLE, "lane L4's joulewise.flags is not in this tree")
    def test_l4_compute_on_the_real_alpha_roster(self):
        from joulewise.flags import catalog as l4_catalog
        from joulewise.flags import exclusions
        roster, document, spans = self.inputs(self.ALPHA)
        catalog = l4_catalog.load_catalog(FIXTURES / "flag_catalog.json")
        clean = exclusions.compute([], document, spans, catalog)
        self.assertTrue(clean["claim_usable"], clean["reasons"])
        self.assertEqual({cell["cell_id"]: cell["planned"] for cell in clean["cells"]},
                         {cell["cell_id"]: {"quad": 10, "repeat": 10} for cell in document["cells"]})
        ledger = h.FlagLedger(plan_id="plan", attempt=1, catalog=h.Catalog.load(FIXTURES / "flag_catalog.json"),
                              boot_session_uuid=None)
        quads = [member["run_id"] for member in roster["members"]
                 if any(cell["unit_kind"] == "quad" and "decode" in cell["cell_id"] for cell in member["cells"])]
        one = ledger.emit("battery.member_span", level="member", run_id=quads[0], collector="test")
        result = exclusions.compute([one], document, spans, catalog)
        decode = next(cell for cell in result["cells"] if cell["cell_id"] == "df-ph-decode-qwen3-1p7b")
        self.assertEqual((decode["n_quads"], decode["n_repeats"], decode["resolvable"], result["claim_usable"]),
                         (9, 10, True, True))
        three = [ledger.emit("battery.member_span", level="member", run_id=run_id, collector="test")
                 for run_id in quads[0:12:4]]  # one member of each of three quads
        result = exclusions.compute(three, document, spans, catalog)
        self.assertEqual(result["reasons"], ["cell.below_minimum"])
        foreign = h.FlagLedger(plan_id="another-plan", attempt=1, catalog=h.Catalog.load(None),
                               boot_session_uuid=None).emit("pack.identity_mismatch", level="window", collector="test")
        result = exclusions.compute([foreign], document, spans, catalog)
        self.assertEqual((result["claim_usable"], result["flag_counts"]["foreign_scope"]), (True, 1))
        early = [dict(bundle, created_monotonic_ns=10 * NS) if bundle["run_id"] == quads[0] else bundle
                 for bundle in document["bundles"]]
        result = exclusions.compute([], {**document, "bundles": early}, spans, catalog)
        self.assertEqual([(row["bundle_id"], row["code"]) for row in result["bundles_ignored"]],
                         [(f"claim/{quads[0]}", "roster.before_chain_started")])


class IdentityReplayTests(WindowTestCase):
    def test_acceptance_pin_reads_both_plan_tree_shapes(self):
        floor = json.loads((ExclusionSeamTests.ALPHA / "plan_tree.json").read_bytes())["acceptance_policy"]
        contrast = json.loads((ExclusionSeamTests.GAMMA / "plan_tree.json").read_bytes())["acceptance_policy"]
        self.assertEqual(h.acceptance_pin(floor), (sha(ROOT / ACCEPTANCE),
                                                   "acceptance_policy.issued_acceptance.artifact_sha256"))
        self.assertEqual(h.acceptance_pin(contrast), (sha(ROOT / ACCEPTANCE), "acceptance_policy.issued_artifact_sha256"))
        self.assertEqual(h.acceptance_pin({"selection": "issued_d116_artifact_only"}), (None, None))

    def test_contrast_shaped_acceptance_pin_is_checked_against_the_bytes(self):
        """Review F4: the GAMMA tree pins the acceptance as issued_artifact_sha256."""
        contrast = json.loads((ExclusionSeamTests.GAMMA / "plan_tree.json").read_bytes())["acceptance_policy"]
        window = self.window(acceptance_policy=contrast)
        window.harvest()
        self.assertNotIn("calibration.acceptance_mismatch", window.codes())
        tampered = Window(self.tmp / "tampered", acceptance_policy=contrast, catalog_overrides=self.ISOLATE)
        accept = tampered.measurement / ACCEPTANCE
        accept.write_bytes(accept.read_bytes().replace(b"{", b'{"b5_test_edit": true, ', 1))
        tampered.harvest()
        flag = next(flag for flag in tampered.flags() if flag["code"] == "calibration.acceptance_mismatch")
        self.assertEqual(flag["expected"], {"sha256": sha(ROOT / ACCEPTANCE),
                                            "pin": "acceptance_policy.issued_artifact_sha256"})
        self.assertIn("calibration.acceptance_mismatch", tampered.exclusions()["reasons"])
        unpinned = Window(self.tmp / "unpinned", acceptance_policy={"selection": "issued_d116_artifact_only"},
                          catalog_overrides=self.ISOLATE)
        unpinned.harvest()
        flag = next(flag for flag in unpinned.flags() if flag["code"] == "calibration.acceptance_mismatch")
        self.assertEqual(flag["expected"], {"sha256": None, "pin": None})

    def test_executed_inventory_without_a_head_is_identity_unmeasured(self):
        """Review F5: an executed inventory with no head no longer skips the H_claim check silently."""
        window = self.window(executed_overrides={"head": None})
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "code.identity_unmeasured")
        self.assertEqual(flag["observed"]["unmeasured"], [{"check": "head", "missing_input": "executed_head"}])
        self.assertIn("code.identity_unmeasured", window.exclusions()["reasons"])
        self.assertNotIn("code.executed_differs_from_sealed", window.codes())

    def test_tampered_pinned_config_without_a_sealed_inventory_is_still_a_mismatch(self):
        """Review F6: the plan tree's own pins are compared even when the sealed inventory is absent."""
        window = self.window(sealed_inventory=False)
        config = window.pack / "01_abs" / "b5t-abs-r01.json"
        value = json.loads(config.read_bytes())
        value["workload_profile"]["output_tokens"] = 9
        config.write_bytes(normalized_config(value))
        window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "pack.identity_mismatch")
        self.assertEqual([(row["path"], row.get("pin")) for row in flag["observed"]["mismatches"]],
                         [(f"configs/campaigns/{PACK_ID}/01_abs/b5t-abs-r01.json", None)])
        self.assertIn("pack.identity_unmeasured", window.codes())
        self.assertIn("pack.identity_mismatch", window.exclusions()["reasons"])

    def test_sealed_files_outside_the_executed_roots_are_not_code(self):
        """L2 inventories joulewise/, scripts/ and the pack; a sealed config elsewhere is not executed code."""
        window = self.window()
        executed = window.custody / "night" / "executed_inventory.json"
        value = json.loads(executed.read_bytes())
        del value["measurement_checkout"]["files"][POLICY]
        put(executed, value)
        window.harvest()
        self.assertNotIn("code.executed_differs_from_sealed", window.codes())
        self.assertNotIn("code.identity_unmeasured", window.codes())


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
