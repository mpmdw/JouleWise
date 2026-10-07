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
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
import zlib
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import kernel_clock, whole_window
from joulewise.adapters.powermetrics import (
    RAW_SAMPLES_NAME, anchor_records_from_powermetrics, parse_powermetrics_records)
from joulewise.b5 import chain as b5_chain
from joulewise.b5 import harvest as h
from joulewise.idle_admission import NEG8_BRACKET_SCHEMA
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
P42_FAMILY = "df-b5t-p42"  # read from FAMILY's members, as p42 reads the decode members; no member's own tag
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

# Registration 6.9, the flat harvest-threshold block (block-5 draft revision 3).
# RegisteredThresholdTests pins this literal to the design branch's own text.
REGISTERED_HARVEST_THRESHOLDS = {
    "battery_limit_ma": 200, "battery_unmeasured_gap_s": 120.0, "battery_accumulator_watts_per_unit": 0.001,
    "thermal_unmeasured_gap_s": 15.0, "contention_cpu_s_per_s": 0.05, "clock_step_ns": 1000000,
    "clock_unmeasured_gap_s": 3.0, "disk_low_bytes": 10737418240, "clock_systematic_min_recorded": 5}
DESIGN_BRANCH = "design/2026-10-05-v5-claim-block-draft"
SEALED_DIR = "configs/campaigns/v5_claim_25g83"
REGISTRATION_RELATIVE = f"{SEALED_DIR}/registration_block5.md"
CORPUS_RELATIVE = "configs/campaigns/neg8_reference_corpus_v5/derivation/settled_corpus.json"
# The registration 4.3 shape L2's plan writer copies into hazard_window.thresholds
# (nested per hazard module); the harvest must not read it as its own block.
L2_NESTED_THRESHOLDS = {"battery": {"limit_ma": 200, "max_update_age_s": 180, "max_unobserved_s": 120},
                        "clock": {"step_ns": 1000000, "t_stream_max_s": 335},
                        "contention": {"cpu_limit_s_per_s": 0.05}, "disk": {"low_bytes": 10737418240},
                        "instrument": {"frames": 300}, "thermal": {"max_gap_s": 15, "max_level": 0}}
# An idle float publication: no charge or discharge tick between publications
# (BatteryPowerAccumulatorCount held at 4727 from 10-01 to 10-05, L1's units check).
STEADY_TELEMETRY = {"AccumulatedBatteryPower": 1_000_000, "BatteryPowerAccumulatorCount": 4727,
                    "AccumulatedBatteryDischarge": -2_000_000, "BatteryDischargeAccumulatorCount": 22670}


def registration_text(block=None, heading="### 6.9 Harvest thresholds") -> str:
    """A registration document whose 6.9 section carries ``block`` (default: the registered one).

    A later section carries another JSON block, which the reader must not take.
    """
    body = json.dumps(REGISTERED_HARVEST_THRESHOLDS if block is None else block, indent=2)
    return (f"# Registration (test copy)\n\n## 6. Flags and exclusions\n\n### 6.8 Disclosed only\n\nText.\n\n"
            f"{heading}\n\nThe harvest reads its own copy of the in-window thresholds.\n\n```json\n{body}\n```\n\n"
            "## 7. Verdicts\n\n```json\n{\"battery_limit_ma\": 1}\n```\n")


def design_branch_file(relative: str) -> bytes | None:
    """A file of the block-5 design branch, when this clone has the branch (else None)."""
    try:
        result = subprocess.run(["git", "-C", str(ROOT), "show", f"{DESIGN_BRANCH}:{relative}"],
                                capture_output=True, check=False, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


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
    """``contention.interval`` output (kernel_task excluded, as in window), with the
    host-CPU, exited-process and aggregate keys of L1 e880af6d (aggregate journaled,
    not judged: no limit registered)."""
    rows = [{"pid": 310, "command": "WindowServer", "cpu_s_per_s": 0.01, "start": "Mon Sep 21 07:13:20 2026"},
            *({"start": "Mon Oct 05 18:00:00 2026", **row} for row in outside)]
    rows.sort(key=lambda row: (-row["cpu_s_per_s"], row["pid"]))
    elapsed_s = (end_ns - begin_ns) / 1e9
    outside_total = sum(row["cpu_s_per_s"] for row in rows)
    busy = 0.97 + outside_total + kernel_task
    return {"interval": {"monotonic_ns": [begin_ns, end_ns],
                         "monotonic_raw_ns": [begin_ns + RAW_OFFSET_NS, end_ns + RAW_OFFSET_NS],
                         "wall_ns": [begin_ns + WALL_OFFSET_NS, end_ns + WALL_OFFSET_NS]},
            "elapsed_s": elapsed_s, "clean": all(row["cpu_s_per_s"] <= 0.05 for row in rows),
            "max_outside": rows[0], "outside_over_limit": [row for row in rows if row["cpu_s_per_s"] > 0.05],
            "exited_over_limit": [],
            "outside_listed": [row for row in rows if row["cpu_s_per_s"] >= 0.005],
            "outside_total_cpu_s_per_s": outside_total, "outside_process_count": 7,
            "tree_cpu_s_per_s": 0.97, "tree_process_count": 3, "kernel_task_cpu_s_per_s": kernel_task,
            "kernel_task_included": False, "unaccounted": [], "raw": [],
            "host_busy_cpu_s_per_s": busy, "host_idle_cpu_s_per_s": 16 - busy, "host_error": None,
            "host_ticks": {"busy_ticks": round(busy * 100 * elapsed_s), "cpus": 16, "elapsed_s": elapsed_s,
                           "idle_ticks": round((16 - busy) * 100 * elapsed_s), "ticks_per_s": 100.0},
            "outside_aggregate_cpu_s_per_s": outside_total, "unattributed_cpu_s_per_s": 0.0,
            "aggregate_limit_s_per_s": None, "aggregate_over_limit": False}


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
                   clock_steps=(), omit=(), battery_gap=None, contention_gap=None, disk_low=False,
                   telemetry=None, smc_current=None) -> None:
    """Every module from 300 s before the first member to 300 s after the last, in L1's format.

    ``extra_publications``: (monotonic_ns, battery-value overrides); each is a
    gauge publication taking effect at that instant (rounded to L1's whole-second
    UpdateTime).  ``contention_extra``: ((lo, hi), {pid, command, cpu_s_per_s}).
    ``telemetry``: publication monotonic_ns -> its ``PowerTelemetryData``
    accumulators (default: an idle float, no tick of either sign).
    ``smc_current``: monotonic_ns -> B0AC mA; when given, the battery journal
    also holds the monitor's 1 s ``source: smc`` reads (B0AV 12,500 mV) from
    the journal's start to its end (default: none, a registry-only journal).
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
        values = {"power_telemetry": dict(STEADY_TELEMETRY if telemetry is None else telemetry(effect)), **values}
        journals["battery"].write("reading", effect + 2 * NS, effect + 2 * NS + 30_000_000,
                                  values=battery_values(update, **values))
    if smc_current is not None:
        from joulewise.hazards import battery as l1_battery
        for index, poll in enumerate(range(start, end, NS)):
            values = {"B0AC": smc_current(poll), "B0AV": 12500, "PDTR": 60.0, "PSTR": 60.0 + index / 1000,
                      "PPBR": 0.0}
            sample = l1_battery.smc_sample(lambda values=values: {"values": values, "errors": {}})
            journals["battery"].write("reading", poll - 400_000, poll, values={"source": "smc", "smc": sample})
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
                 acceptance_policy=None, sealed_inventory=True, registration=True, registration_block=None,
                 p42_precheck=None):
        self.root = root
        # p42_precheck: also register a second, non-target condition family
        # read from the same members (the floor packs' p42 cells: the decode
        # members' prefill, registration 0.5 and 6.6) with this precheck path.
        self.p42_precheck = p42_precheck
        self.registration = (root / "measurement" / REGISTRATION_RELATIVE) if registration else None
        self.registration_block = registration_block
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
        # The committed 12-member NEG-8 settled corpus, exactly as the floor packs pin it.
        (self.measurement / CORPUS_RELATIVE).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / CORPUS_RELATIVE, self.measurement / CORPUS_RELATIVE)
        if self.registration is not None:
            self.registration.parent.mkdir(parents=True, exist_ok=True)
            self.registration.write_text(registration_text(self.registration_block))
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
        if self.p42_precheck is not None:
            p42 = {"all": {"condition_family_definition": {
                "condition_family_id": P42_FAMILY,
                "workload_profile": {"prompt_tokens": register_prompt_tokens, "output_tokens": 8}}}}
            spec["cells"] += [
                {"cell_id": "b5t-p42-abs", "kind": "absolute", "metric": "phase_energy_j.prefill",
                 "target_precheck_path": self.p42_precheck, "condition_family_id": P42_FAMILY, "expected_n": 2,
                 "condition_family_definitions": p42,
                 "members": [{"slot": row[0], "bundle_id": row[0]} for row in MEMBERS if row[2] is None]},
                {"cell_id": "b5t-p42-cmp", "kind": "comparative", "metric": "phase_energy_j.prefill",
                 "target_precheck_path": self.p42_precheck, "condition_family_id": P42_FAMILY, "expected_n": 1,
                 "condition_family_definitions": p42,
                 "blocks": [{"block_id": "b5t-b01", "members": {row[3]: row[0] for row in MEMBERS if row[2]}}]}]
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
            # The floor packs' bound-derivation stage, as d117_floor_qwen3-1p7b_v5 writes it.
            "stage_graph": [{
                "stage_id": "b5t-bound-derivation", "kind": "bound_derivation", "expected_count": 1,
                "input": {"kind": "external_artifact", "path": CORPUS_RELATIVE, "sha256": sha(ROOT / CORPUS_RELATIVE)},
                "launch": {"schema_version": "joulewise.stage_launch.v1", "commands": [{
                    "command_id": "b5t-bound-derivation.derive", "command_kind": "bound_derivation",
                    "argv_template": {"tool_id": "campaign_runner", "interface_id": "joulewise.run_campaign.cli.v1",
                                      "arguments": [
                                          {"kind": "literal", "value": "--derive-neg8-drift-bound"},
                                          {"kind": "repo_path", "value": CORPUS_RELATIVE},
                                          {"kind": "literal", "value": "--neg8-drift-bound-output"},
                                          {"kind": "binding_path", "value": "bound_runs_root",
                                           "relative": "neg8-drift-bound.json"},
                                          {"kind": "literal", "value": "--runs-dir"},
                                          {"kind": "binding", "value": "bound_runs_root"}]}}]}}],
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
                "thresholds": copy.deepcopy(L2_NESTED_THRESHOLDS),
                # The plan writer's record of the registration it was written from.
                "registration": {"path": str(self.registration), "sha256": sha(self.registration)}
                if self.registration is not None else None,
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
        # the missing pair is the disclosed "covered" case (plan 3.5).  These
        # journals hold no SMC B0AC read, so the registry fallback is disclosed.
        self.assertEqual(member_codes - {"battery.capture_pair_missing_covered", "battery.smc_unavailable",
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
                                        "exclusions", "yield"})
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
        # A charge current: under the battery-assist ruling (2026-10-06) the same
        # discharge would be disclosed (tests/test_harvest_b5_p3harv.py).
        excursion = ((start + end) // 2, {"instant_amperage_ma": 447, "amperage_ma": 380})
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

    def test_sealed_identity_pins_file_is_read_at_its_default_path(self):
        """Integration: the one sealed pins file the arm collector also reads (``--identity-pins``)."""
        identity = derive_model_runtime_config_from_metadata(
            json.loads((template() / MEMBERS[0][0] / "config.json").read_bytes()),
            json.loads((template() / MEMBERS[0][0] / "metadata.json").read_bytes()))[1]
        for label, runtime_pin, expect_mismatch in (("matching", identity["runtime_identity_sha256"], False),
                                                    ("other-runtime", "0" * 64, True)):
            with self.subTest(label):
                window = Window(self.tmp / f"w-{label}", catalog_overrides=self.ISOLATE, frozen_pins=False)
                put(window.measurement / "configs/campaigns/v5_claim_25g83/identity_pins.json", {
                    "schema": h.IDENTITY_PINS_SCHEMA, "runtime_versions_sha256": None,
                    "units": {"b5t-unit": {"model_artifact_sha256": identity["model_artifact_sha256"],
                                           "runtime_identity_sha256": runtime_pin}}})
                window.harvest()
                self.assertNotIn("model.identity_unpinned", window.codes())
                mismatched = {flag["scope"]["run_id"] for flag in window.flags()
                              if flag["code"] == "model.identity_mismatch"}
                self.assertEqual(mismatched, {row[0] for row in MEMBERS} if expect_mismatch else set())

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
        # shows no code, so it is disclosed and blocks nothing (Opus audit F2).
        self.assertIn("model.identity_mismatch", window.exclusions()["reasons"])
        self.assertNotIn("records.malformed_flag", window.window_flags()["flags"]["unclassified"])
        self.assertFalse(window.exclusions()["release_blocked"])

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

    # Refusal-census triage (a), 2026-10-07.  calibration.ledger_snapshot_refused
    # (EXCLUDE_WINDOW) fires on any reason of the harvest's ledger snapshot.  The
    # reasons that can reach it are integrity reasons: the governed writer refuses
    # to append past any ledger reason (below: another window's open session), the
    # terminal-pin derivation refuses every parse or state reason before the
    # snapshot is taken (calibration.no_bracket), and the call passes
    # require_committed_pin=False and verify_custody=False.  What is left is the
    # acceptance cutoff missing from this chain, the ledger changing between two
    # reads, or chain bytes that do not parse.  No split: classified NUMBER_INTEGRITY.
    def test_the_writer_cannot_leave_another_windows_session_open_under_this_one(self):
        dangling = "b5t-earlier-window-session"
        real_append = append_bracket_session_receipt
        opened = []

        def append(ledger, **kwargs):
            if not opened:
                slots = {}
                for slot in ("pre", "post"):
                    capture = Path(kwargs["runs_root"]) / "instrument_validation" / f"{dangling}-{slot}"
                    capture.mkdir(parents=True)
                    slots[slot] = {**kwargs["slots"][slot], "attempt_id": f"{dangling}-{slot}",
                                   "custody_locator": str(capture)}
                real_append(ledger, **{**kwargs, "session_id": dangling, "window_id": "earlier-window",
                                       "slots": slots})
                opened.append(dangling)
                # The earlier window's writer stopped here; its pin was advanced to its head.
                last = json.loads(Path(ledger).read_bytes().splitlines()[-1])
                put(Path(kwargs["head_pin_path"]), {"sequence": last["sequence"],
                                                    "head_digest": last["receipt_digest"],
                                                    "ledger_schema": LEDGER_SCHEMA})
            return real_append(ledger, **kwargs)

        from joulewise.calibration_ledger import CalibrationLedgerError
        with mock.patch(f"{__name__}.append_bracket_session_receipt", side_effect=append), \
                self.assertRaisesRegex(CalibrationLedgerError, "calibration_ledger_bracket_session_open"):
            self.window(prefix_ledger=True)
        self.assertEqual(opened, [dangling])

    def test_a_ledger_integrity_reason_excludes_the_window(self):
        # The real 376-row acceptance prefix; the acceptance's cutoff digest is
        # replaced by one that is not in this chain, so the calibration was not
        # judged on this ledger.
        window = self.window(prefix_ledger=True)
        from joulewise import calibration_ledger
        real_load = calibration_ledger.load_calibration_ledger_snapshot

        def wrong_cutoff(*args, **kwargs):
            return real_load(*args, **{**kwargs, "baseline_digest": "f" * 64})

        with mock.patch.object(calibration_ledger, "load_calibration_ledger_snapshot", side_effect=wrong_cutoff):
            window.harvest()
        flag = next(flag for flag in window.flags() if flag["code"] == "calibration.ledger_snapshot_refused")
        self.assertEqual(flag["observed"]["reasons"], ["calibration_ledger_baseline_missing"])
        self.assertEqual(h.Catalog.load(FIXTURES / "flag_catalog.json").effect("calibration.ledger_snapshot_refused"),
                         "EXCLUDE_WINDOW")

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
        advance_pin(window)  # the desk order: chain exit, pin advance, harvest (registration 11)
        calls = []

        def runner(argv, **kwargs):
            calls.append(argv)
            runs = Path(argv[argv.index("--runs-dir") + 1])
            (runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
            (runs / "campaign_log.jsonl").write_text('{"status":"failed"}\n')
            (runs / "b5t-abs-r01" / "logs" / "controller.log").write_text("tampered\n")
            return SimpleNamespace(returncode=1, stdout="", stderr="")

        window.harvest(seams=desk_seams(runner), prepare_desk=True, run_g3=False)
        self.assertEqual(len(calls), 1)
        argv = calls[0]
        self.assertIn("--whole-window-verdict", argv)
        self.assertEqual(argv[argv.index("--bracket-binding") + 1], str(window.claim / "bracket-binding.json"))
        self.assertTrue((window.claim / "bracket-binding.json").is_file())
        # The desk's own inventory check names the file (the member assessed
        # while the writer ran is assessed again: P2-HARV row 1).
        flag = next(flag for flag in window.flags() if flag["code"] == "records.source_changed_during_harvest"
                    and "changed" in flag["observed"])
        self.assertEqual(flag["observed"]["changed"], ["b5t-abs-r01/logs/controller.log"])
        self.assertIn("whole_window.verdict_unauthenticated", window.codes())

    def test_an_os_metadata_file_appearing_during_the_harvest_changes_no_source(self):
        """Opus triple audit F7: a Finder .DS_Store in a bundle directory is not a changed number.

        Before: records.source_changed_during_harvest (EXCLUDE_WINDOW) removed the window."""
        window = self.window(prefix_ledger=True)
        advance_pin(window)

        def runner(argv, **kwargs):
            runs = Path(argv[argv.index("--runs-dir") + 1])
            (runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
            (runs / "b5t-abs-r01" / ".DS_Store").write_bytes(b"Bud1 finder")
            (runs / "b5t-abs-r01" / "raw" / "._powermetrics.plist").write_bytes(b"appledouble")
            return SimpleNamespace(returncode=1, stdout="", stderr="")

        window.harvest(seams=desk_seams(runner), prepare_desk=True, run_g3=False)
        self.assertNotIn("records.source_changed_during_harvest", window.codes())
        self.assertTrue(h._os_metadata("b5t-abs-r01/.DS_Store"))
        self.assertFalse(h._os_metadata("b5t-abs-r01/logs/controller.log"))

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


# ---------------------------------------------------------------------------
# Fix lane fx-harvest: the NEG-8 bound and screen, the registered thresholds,
# the battery accumulator rule, lineage findings and the emitted codes.
# ---------------------------------------------------------------------------

COMMITTED_CORPUS = json.loads((ROOT / CORPUS_RELATIVE).read_bytes())
CORPUS_IDS = [member["bundle_id"] for member in COMMITTED_CORPUS["members"]]
NEG8_FRESHNESS = {"os_build": "fixture-os", "power_supply_identity_sha256": "e" * 64,
                  "calibration_identity_sha256": "f" * 64}


# The corpus members' measured windows end before the chain starts (epoch
# 1786206000): the HAZARD mint dates its bound by the latest kept member's
# sampling_stopped (whole_window._hazard_bound_derived_at_s) and never by its
# own clock (P2-B1 review F2).
CORPUS_MEASURED_END_S = 1786205000.0


def put_corpus_stub(bundle: Path, bundle_id: str, status: str) -> None:
    """A synthetic NEG-8 corpus bundle: run id, status and a measured window (its sampling markers)."""
    put(bundle / "config.json", {"run_id": bundle_id})
    put(bundle / "metadata.json", {"run_id": bundle_id})
    put(bundle / "summary_metrics.json", {"status": status})
    end = CORPUS_MEASURED_END_S + CORPUS_IDS.index(bundle_id) if bundle_id in CORPUS_IDS else CORPUS_MEASURED_END_S
    (bundle / "events.jsonl").write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in (
        {"timestamp_s": end - 5.0, "event_type": "sampling_started", "phase": "measured_run",
         "message": "sampling_started", "metadata": {}},
        {"timestamp_s": end, "event_type": "sampling_stopped", "phase": "measured_run",
         "message": "sampling_stopped", "metadata": {}})))


def corpus_point(path: Path):
    """A corpus member's two NEG-8 points (the synthetic bundles carry no energies)."""
    value = 30.0 + 0.1 * int(path.name.rsplit("-r", 1)[1])
    return {"point_j": value, "lower_j": value - 0.01, "upper_j": value + 0.01}, value - 20.0, None


@contextlib.contextmanager
def neg8_member_gates():
    """Stub only the per-member energy and strictness gates of the core's NEG-8 mint.

    The manifest grammar, the n >= 10 rule, the bound arithmetic and the
    binding of the corpus identity to the manifest bytes are the core's own
    (tests/test_whole_window.py stubs the same gates).
    """
    with contextlib.ExitStack() as stack:
        for target, kwargs in (("authenticate_bundle_launch_lineage", {"return_value": None}),
                               ("_custody_strict_invalid", {"return_value": False}),
                               ("_current_strict_summary", {"return_value": True}),
                               ("_scientific_config_identity", {"return_value": ("d" * 64, True)}),
                               ("_reference_energy_evidence", {"side_effect": corpus_point}),
                               ("neg8_freshness_bindings_from_metadata", {"return_value": NEG8_FRESHNESS})):
            stack.enter_context(mock.patch.object(whole_window, target, **kwargs))
        yield


def neg8_corpus(window: "Window", failed=(), *, manifest_members=None, derive=True) -> str | None:
    """Run the chain's NEG-8 corpus stage on ``window``; return the mint's refusal, if any.

    The 12 committed corpus members become bundles in the bound runs root
    (``failed`` did not succeed; a ``manifest_members`` id outside the
    committed corpus gets a succeeded bundle too).  Then, as the chain and the
    driver do: the chain's own prune helper (``b5.chain.PRUNE_HELPER``) writes
    the collected manifest from the committed one (or from
    ``manifest_members``, a corpus the prune helper never selected); the core's
    ``mint_neg8_drift_bound_artifact`` derives the bound from it (refusing
    under 10 members, as the chain's derivation stage would); the driver's
    ``b5.chain.neg8_corpus_record`` locator goes into night/hazard_result.json.
    """
    ids = set(CORPUS_IDS) | {member["bundle_id"] for member in manifest_members or ()}
    for bundle_id in sorted(ids):
        bundle = window.bound / bundle_id
        bundle.mkdir(parents=True, exist_ok=True)
        for name in ("config.json", "metadata.json", "summary_metrics.json", "events.jsonl"):
            (bundle / name).unlink(missing_ok=True)
        put_corpus_stub(bundle, bundle_id, "failed" if bundle_id in failed else "succeeded")
    night = window.custody / "night"
    collected = night / "transcript" / b5_chain.NEG8_COLLECTED_MANIFEST
    summary = night / "transcript" / b5_chain.NEG8_COLLECTED_SUMMARY
    collected.parent.mkdir(parents=True, exist_ok=True)
    for path in (collected, summary, night / "hazard_result.json"):
        path.unlink(missing_ok=True)
    source = window.measurement / CORPUS_RELATIVE
    if manifest_members is not None:
        source = window.root / "selected-corpus.json"
        source.write_text(json.dumps({**COMMITTED_CORPUS, "members": manifest_members}, indent=2, sort_keys=True)
                          + "\n")
    subprocess.run([sys.executable, "-B", "-c", b5_chain.PRUNE_HELPER, str(source), str(window.bound),
                    str(collected), str(summary)], check=True, capture_output=True)
    refusal = None
    if derive:
        (window.bound / "neg8-drift-bound.json").unlink(missing_ok=True)
        try:
            with neg8_member_gates():
                artifact = whole_window.mint_neg8_drift_bound_artifact(window.bound, collected)
        except ValueError as exc:
            refusal = str(exc)
        else:
            put(window.bound / "neg8-drift-bound.json", artifact)
    put(night / "hazard_result.json", {"schema": "joulewise.b5_hazard_night.v1",
                                       "neg8_corpus": b5_chain.neg8_corpus_record(night)})
    return refusal


def write_verdict(window: "Window", *, status: str, decision: str | None, conditions=(), member_conditions=()):
    """A stored whole-window verdict row with a NEG-8 bracket (``decision`` None: no bracket)."""
    core = {"conditions": sorted({*conditions, *member_conditions})}
    if decision is not None:
        core["neg8_bracket"] = {"schema_version": NEG8_BRACKET_SCHEMA, "decision": decision,
                                "passed": decision == "passed", "conditions": sorted(conditions)}
    # The writer always records member_failures (run_campaign); [] names no failed member.
    put(window.claim / "whole-window-verdict.json", {"status": status, "bundle_ids": [],
                                                     "idle_admission_core": core, "member_failures": []})


class Neg8BoundTests(WindowTestCase):
    """Registration 5.3: a bound derived from at least 10 of the 12 corpus members is valid."""

    def harvest_neg8(self, name: str, failed=(), **kwargs):
        window = Window(self.tmp / name, catalog_overrides=self.ISOLATE)
        refusal = neg8_corpus(window, failed, **kwargs)
        window.harvest()
        return window, json.loads((window.archive / "derived" / "neg8-bound.json").read_bytes()), refusal

    def test_twelve_members_derive_against_the_committed_corpus(self):
        window, check, _refusal = self.harvest_neg8("kept12")
        self.assertNotIn("neg8.bound_not_derived", window.codes())
        self.assertEqual((check["derived_from"], check["problems"]), ("registered_corpus", []))

    def test_eleven_and_ten_members_are_derived_from_the_custodied_collected_manifest(self):
        """Before the fix both ended neg8.bound_not_derived: the core reader authenticates only the 12."""
        for failed in ([CORPUS_IDS[4]], [CORPUS_IDS[0], CORPUS_IDS[11]]):
            kept = 12 - len(failed)
            with self.subTest(kept=kept):
                window, check, refusal = self.harvest_neg8(f"kept{kept}", failed)
                self.assertIsNone(refusal)
                # The core's file reader still refuses the pruned corpus; the harvest does not.
                self.assertIsNone(whole_window.load_neg8_drift_bound_artifact(window.bound / "neg8-drift-bound.json"))
                self.assertEqual(check["derived_from"], "collected_subset", check["problems"])
                self.assertEqual((check["members_committed"], check["members_collected"], check["dropped_bundle_ids"],
                                  check["problems"]), (12, kept, failed, []))
                self.assertNotIn("neg8.bound_not_derived", window.codes())
                self.assertNotIn("neg8.bound_not_derived", window.exclusions()["reasons"])
                self.assertEqual(check["collected_manifest"]["sha256"], sha(
                    window.custody / "night" / "transcript" / b5_chain.NEG8_COLLECTED_MANIFEST))

    def test_nine_members_are_not_derived(self):
        window, check, refusal = self.harvest_neg8("kept9", CORPUS_IDS[:3])
        self.assertIn("requires n >= 10", refusal)  # the chain's derivation stage writes no bound
        flag = next(flag for flag in window.flags() if flag["code"] == "neg8.bound_not_derived")
        self.assertEqual(flag["observed"]["problems"], ["bound_artifact_absent"])
        self.assertIn("neg8.bound_not_derived", window.exclusions()["reasons"])
        # A bound left from an earlier 10-member derivation does not cover a 9-member collection.
        stale = Window(self.tmp / "stale", catalog_overrides=self.ISOLATE)
        self.assertIsNone(neg8_corpus(stale, CORPUS_IDS[:2]))
        neg8_corpus(stale, CORPUS_IDS[:3], derive=False)
        stale.harvest()
        check = json.loads((stale.archive / "derived" / "neg8-bound.json").read_bytes())
        self.assertEqual((check["derived_from"], check["members_collected"]), (None, 9))
        self.assertIn("collected_members_below_minimum", check["problems"])
        self.assertIn("neg8.bound_not_derived", stale.codes())

    def test_tampered_or_selected_corpus_is_not_derived(self):
        collected = Path("night") / "transcript" / b5_chain.NEG8_COLLECTED_MANIFEST
        foreign = [member if member["bundle_id"] != CORPUS_IDS[4] else
                   {"bundle_id": "neg8-refcorpus-r99", "bundle_path": "neg8-refcorpus-r99"}
                   for member in COMMITTED_CORPUS["members"]]
        selected = [member for member in COMMITTED_CORPUS["members"] if member["bundle_id"] != CORPUS_IDS[4]]

        def edit_manifest(window):  # bytes changed after the driver recorded their digest
            path = window.custody / collected
            path.write_bytes(path.read_bytes().replace(b"\n", b"\n ", 1))

        def edit_bound(window):  # one member's point changed after derivation
            path = window.bound / "neg8-drift-bound.json"
            value = json.loads(path.read_bytes())
            value["reference_corpus"]["members"][0]["point_gross_j"] += 0.5
            put(path, value)

        def edit_committed(window):  # the measurement checkout's manifest no longer has its pinned bytes
            path = window.measurement / CORPUS_RELATIVE
            path.write_bytes(path.read_bytes() + b"\n")

        def relabel(field):
            def tamper(window):
                """The collected manifest relabelled over the same member rows, a bound minted on it, its digest recorded."""
                night = window.custody / "night"
                path = window.custody / collected
                value = json.loads(path.read_bytes())
                value[field] = f"{value[field]}-relabelled"
                put(path, value)
                with neg8_member_gates():
                    put(window.bound / "neg8-drift-bound.json",
                        whole_window.mint_neg8_drift_bound_artifact(window.bound, path))
                put(night / "hazard_result.json", {"schema": "joulewise.b5_hazard_night.v1",
                                                   "neg8_corpus": b5_chain.neg8_corpus_record(night)})
            return tamper

        cases = {
            "corpus_id_relabelled": ({"failed": [CORPUS_IDS[4]]}, relabel("corpus_id"),
                                     "collected_manifest_header_differs"),
            "condition_id_relabelled": ({"failed": [CORPUS_IDS[4]]}, relabel("condition_id"),
                                        "collected_manifest_header_differs"),
            "manifest_edited": ({"failed": [CORPUS_IDS[4]]}, edit_manifest,
                                "collected_manifest_differs_from_recorded_sha256"),
            "foreign_member": ({"manifest_members": foreign}, None, "collected_manifest_not_a_member_subset"),
            "succeeded_member_left_out": ({"manifest_members": selected}, None,
                                          f"dropped_member_succeeded:{CORPUS_IDS[4]}"),
            "bound_edited": ({"failed": [CORPUS_IDS[4]]}, edit_bound,
                             "bound_does_not_validate_against_collected_corpus"),
            "committed_manifest_edited": ({"failed": [CORPUS_IDS[4]]}, edit_committed,
                                          "committed_manifest_differs_from_pin"),
        }
        for name, (kwargs, tamper, problem) in cases.items():
            with self.subTest(name):
                window = Window(self.tmp / name, catalog_overrides=self.ISOLATE)
                self.assertIsNone(neg8_corpus(window, **kwargs))  # the core minted a bound over these bytes
                if tamper is not None:
                    tamper(window)
                window.harvest()
                check = json.loads((window.archive / "derived" / "neg8-bound.json").read_bytes())
                self.assertIsNone(check["derived_from"])
                self.assertIn(problem, check["problems"])
                self.assertIn("neg8.bound_not_derived", window.exclusions()["reasons"])

    def test_bound_minted_from_another_manifest_is_not_derived(self):
        """The bound must bind to the window's own collected manifest, not just to some valid subset.

        The window collected 11 members; the bound beside it was minted from a
        10-member manifest that also leaves out a member that succeeded (a
        selected, tighter corpus).  Its arithmetic validates; only the corpus
        identity check against the custodied collected bytes refuses it.
        """
        window = Window(self.tmp / "other-manifest", catalog_overrides=self.ISOLATE)
        self.assertIsNone(neg8_corpus(window, [CORPUS_IDS[4]]))
        ten = window.root / "ten.json"
        put(ten, {**COMMITTED_CORPUS, "members": [member for member in COMMITTED_CORPUS["members"]
                                                  if member["bundle_id"] not in (CORPUS_IDS[4], CORPUS_IDS[7])]})
        with neg8_member_gates():
            artifact = whole_window.mint_neg8_drift_bound_artifact(window.bound, ten)
        self.assertTrue(whole_window.validate_neg8_drift_bound_artifact(artifact))  # structurally a valid bound
        put(window.bound / "neg8-drift-bound.json", artifact)
        window.harvest()
        check = json.loads((window.archive / "derived" / "neg8-bound.json").read_bytes())
        self.assertIsNone(check["derived_from"])
        self.assertEqual(check["members_collected"], 11)
        self.assertIn("bound_does_not_validate_against_collected_corpus", check["problems"])
        self.assertIn("neg8.bound_not_derived", window.exclusions()["reasons"])

    def test_derived_outputs_carry_no_bound_energy(self):
        window, _check, _refusal = self.harvest_neg8("blind", [CORPUS_IDS[4]])
        artifact = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        derived = (window.archive / "derived" / "neg8-bound.json").read_text()
        self.assertNotIn(repr(artifact["bound_j"]), derived)
        self.assertNotIn("point_gross_j", derived)


class Neg8ScreenTests(WindowTestCase):
    """Registration 6.5: the NEG-8 screen held in the whole-window verdict removes the window.

    The aggregate verdict codes are disclosed only (the sealed draft, revision 3).
    """

    ISOLATE = {**WindowTestCase.ISOLATE, "whole_window.not_passed": "DISCLOSE", "g3.recompute_failed": "DISCLOSE"}

    def screen(self, row, derived_from=None) -> list[dict]:
        """The real ``_Harvest.neg8_screen`` on one stored row."""
        run = h._Harvest.__new__(h._Harvest)
        run.flags = h.FlagLedger(plan_id=PLAN_ID, attempt=1, catalog=h.Catalog.load(FIXTURES / "flag_catalog.json"),
                                 boot_session_uuid=None)
        run.neg8 = {"derived_from": derived_from}
        run.neg8_screen(row)
        return [flag for flag in run.flags.records if flag["code"] == "neg8.screen_failed"]

    @staticmethod
    def row(status, decision, conditions=(), member_conditions=()):
        core = {"conditions": sorted({*conditions, *member_conditions})}
        if decision is not None:
            core["neg8_bracket"] = {"schema_version": NEG8_BRACKET_SCHEMA, "decision": decision,
                                    "conditions": sorted(conditions)}
        return {"status": status, "idle_admission_core": core}

    def test_the_registered_conditions_are_the_cores_neg8_condition_codes(self):
        self.assertEqual(whole_window.NEG8_POINT_DRIFT_CONDITION_CODES, {
            whole_window.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED,
            whole_window.CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED, "neg8_bracket_missing",
            "neg8_bracket_reference_invalid", whole_window.CONDITION_NEG8_DRIFT_BOUND_STALE,
            whole_window.CONDITION_NEG8_DRIFT_BOUND_UNDERIVED, whole_window.CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED})

    def test_every_neg8_condition_fails_the_screen(self):
        for condition in sorted(whole_window.NEG8_POINT_DRIFT_CONDITION_CODES
                                | {"neg8_bracket_ambiguous_reference", "neg8_bracket_not_evaluated"}):
            with self.subTest(condition):
                (flag,) = self.screen(self.row("failed", "failed", [condition]))
                self.assertEqual(flag["observed"]["conditions"], [condition])
                self.assertEqual(flag["scope"]["level"], "window")
                # Carried only in the core's list (run_campaign unions the bracket's into it): still failed.
                core_only = self.row("failed", "passed", member_conditions=[condition])
                self.assertEqual(len(self.screen(core_only)), 1)

    def test_a_passed_screen_is_not_failed_by_member_failures(self):
        self.assertEqual(self.screen(self.row("passed", "passed")), [])
        # One member's admission failure fails the aggregate verdict, not the screen.
        self.assertEqual(self.screen(self.row("failed", "passed", member_conditions=["cpu_admission_failed"])), [])
        (flag,) = self.screen(self.row("passed", None))
        self.assertEqual(flag["observed"]["reasons"], ["bracket_absent"])
        (flag,) = self.screen(self.row("failed", "flagged"))
        self.assertEqual(flag["observed"]["reasons"], ["bracket_not_passed"])

    def test_failed_screen_in_the_verdict_removes_the_window(self):
        """Before the fix nothing emitted neg8.screen_failed: a failed screen removed nothing."""
        window = self.window()
        neg8_corpus(window)
        write_verdict(window, status="failed", decision="failed",
                      conditions=[whole_window.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED])
        window.harvest()
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertEqual(flag["observed"]["registered_conditions"],
                         [whole_window.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED])
        reasons = window.exclusions()["reasons"]
        self.assertIn("neg8.screen_failed", reasons)
        self.assertNotIn("whole_window.not_passed", reasons)  # disclosed only
        self.assertNotIn("neg8.bound_not_derived", window.codes())

    def test_passed_verdict_with_a_derived_bound_keeps_the_screen(self):
        window = self.window()
        neg8_corpus(window)
        write_verdict(window, status="failed", decision="passed", member_conditions=["cpu_admission_failed"])
        window.harvest()
        self.assertIn("whole_window.not_passed", window.codes())
        self.assertNotIn("neg8.screen_failed", window.codes())
        self.assertNotIn("neg8.bound_not_derived", window.codes())

    def test_collected_corpus_bound_with_a_verdict_whose_screen_cannot_be_rederived(self):
        """The writer read no bound; a re-evaluation that cannot run leaves the screen failed.

        This stored row names no source manifests and no evaluation time, so
        the screen cannot be re-derived against the 11-member bound
        (Neg8RescreenTests covers rows it can).
        """
        window = self.window()
        neg8_corpus(window, [CORPUS_IDS[4]])
        write_verdict(window, status="failed", decision="failed",
                      conditions=[whole_window.CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
                                  whole_window.CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED])
        window.harvest()
        self.assertNotIn("neg8.bound_not_derived", window.codes())
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        rescreen = flag["observed"]["collected_bound_rescreen"]
        self.assertEqual((rescreen["evaluated"], rescreen["problems"]), (False, ["evaluation_time_unrecorded"]))
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])
        # A screen the writer failed against the committed 12-member bound is never re-evaluated.
        twelve = Window(self.tmp / "twelve", catalog_overrides=self.ISOLATE)
        neg8_corpus(twelve)
        write_verdict(twelve, status="failed", decision="failed",
                      conditions=[whole_window.CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
                                  whole_window.CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED])
        twelve.harvest()
        (flag,) = [flag for flag in twelve.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertNotIn("collected_bound_rescreen", flag["observed"])
        self.assertFalse((twelve.archive / "derived" / "neg8-screen.json").exists())

    def test_unreadable_verdict_fails_the_screen(self):
        window = self.window()
        neg8_corpus(window)
        (window.claim / "whole-window-verdict.json").write_text("{not json\n")
        window.harvest()
        (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
        self.assertEqual(flag["observed"]["reasons"], ["verdict_unreadable"])
        self.assertIn("whole_window.verdict_unauthenticated", window.codes())


# The window's own NEG-8 references (3 start, 1 midpoint, 3 end), as the
# governed campaign manifest roles name them.
NEG8_REFERENCES = (
    *((f"b5t-neg8-start-{index}", "neg8_daily_reference_start") for index in (1, 2, 3)),
    ("b5t-neg8-midpoint", "neg8_daily_reference_midpoint"),
    *((f"b5t-neg8-end-{index}", "neg8_daily_reference_end") for index in (1, 2, 3)),
)
NEG8_REFERENCE_MANIFEST = "campaign_manifests/b5t-neg8-references.json"


def neg8_trajectory(drift_j: float) -> dict[str, float]:
    """Gross points of the window's references: the end endpoint sits ``drift_j`` above the start."""
    start = (30.30, 30.32, 30.34)
    points = {f"b5t-neg8-start-{index}": value for index, value in enumerate(start, 1)}
    points["b5t-neg8-midpoint"] = 30.32 + drift_j / 2
    points.update({f"b5t-neg8-end-{index}": value + drift_j for index, value in enumerate(start, 1)})
    return points


@contextlib.contextmanager
def neg8_reference_gates(points: dict[str, float]):
    """Stub the core's per-bundle NEG-8 gates for the synthetic reference bundles in ``points`` only.

    As ``neg8_member_gates`` does for the corpus: these bundles carry no
    energies, so their strictness, scientific identity, energy evidence and
    freshness bindings are stubbed (idle-subtracted = gross - 20 J).  Every
    other bundle reaches the real functions; the manifest resolution, the
    trajectory shape, the screen and the freshness rule are the core's own.
    """
    real = {name: getattr(whole_window, name) for name in (
        "_custody_strict_invalid", "_current_strict_summary", "_scientific_config_identity",
        "_reference_energy_evidence", "neg8_freshness_bindings_from_metadata")}

    def ours(path) -> bool:
        return path is not None and Path(path).name in points

    def strict_invalid(path, *args, **kwargs):
        return False if ours(path) else real["_custody_strict_invalid"](path, *args, **kwargs)

    def current(summary, bundle_path=None):
        return True if ours(bundle_path) else real["_current_strict_summary"](summary, bundle_path)

    def identity(path):
        return ("d" * 64, True) if ours(path) else real["_scientific_config_identity"](path)

    def energy(path, *args, **kwargs):
        if not ours(path):
            return real["_reference_energy_evidence"](path, *args, **kwargs)
        value = points[Path(path).name]
        return {"point_j": value, "lower_j": value - 0.01, "upper_j": value + 0.01}, value - 20.0, None

    def bindings(metadata):
        if isinstance(metadata, dict) and metadata.get("run_id") in points:
            return dict(NEG8_FRESHNESS)
        return real["neg8_freshness_bindings_from_metadata"](metadata)

    with contextlib.ExitStack() as stack:
        for name, stub in (("_custody_strict_invalid", strict_invalid), ("_current_strict_summary", current),
                           ("_scientific_config_identity", identity), ("_reference_energy_evidence", energy),
                           ("neg8_freshness_bindings_from_metadata", bindings)):
            stack.enter_context(mock.patch.object(whole_window, name, stub))
        yield


def write_neg8_reference_verdict(window: "Window", points: dict[str, float], *, completed_at: str | None = None,
                                 extra_conditions=()) -> dict:
    """The window's NEG-8 references, their campaign manifest, and the verdict a writer with no bound stores.

    The stored bracket is the core's own (``whole_window._derived_neg8_decision``
    with no bound, as ``validate_whole_window_verdict_row`` replays it) over
    ``points``: what ``run_campaign --whole-window-verdict`` writes when the
    bound it was given authenticates only against the 10 or 11 collected
    members.  Returns the bracket.
    """
    members = []
    for bundle_id, role in NEG8_REFERENCES:
        bundle = window.claim / bundle_id
        put(bundle / "config.json", {"run_id": bundle_id})
        put(bundle / "metadata.json", {"run_id": bundle_id})
        put(bundle / "summary_metrics.json", {"status": "succeeded"})
        members.append({"execution": "invoked", "run_id": bundle_id, "bundle_ids": [bundle_id], "role": role,
                        "canonical_neg8_workload": True, "scientific_config_sha256": "d" * 64})
    policy_sha = sha(ROOT / POLICY)
    raw = put(window.claim / NEG8_REFERENCE_MANIFEST, {"schema_version": "joulewise.campaign_provenance.v1",
                                                       "campaign_policy": {"sha256": policy_sha},
                                                       "members": members})
    with neg8_reference_gates(points):
        bracket, problem = whole_window._derived_neg8_decision(
            [json.loads(raw)], window.claim, whole_window._registered_bracket_policy(policy_sha), current=True,
            point_drift=True, drift_bound_artifact=None, return_bracket=True)
    assert problem is None, problem
    # The writer's utc_timestamp() form, taken after the bound was derived.
    completed_at = completed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    put(window.claim / "whole-window-verdict.json", {
        "record_type": "idle_admission_whole_window_verdict", "status": "failed", "timestamp": completed_at,
        "evaluation_scope": {"runs_root": str(window.claim.resolve()), "completed_at": completed_at},
        "campaign_policy": {"sha256": policy_sha},
        "row_provenance": {"source_campaign_manifests": [{"path": NEG8_REFERENCE_MANIFEST,
                                                          "sha256": hashlib.sha256(raw).hexdigest()}]},
        "bundle_ids": [bundle_id for bundle_id, _role in NEG8_REFERENCES],
        "idle_admission_core": {"conditions": sorted({*bracket["conditions"], *extra_conditions}),
                                "neg8_bracket": bracket}})
    return bracket


class Neg8RescreenTests(WindowTestCase):
    """Registration 5.3 with 6.5: a 10/11-member bound that validates decides the screen.

    The verdict writer authenticates a bound only against the committed 12, so
    with a collected-subset bound its screen always carries the two
    ``*_UNDERIVED`` conditions.  The harvest re-derives the screen with the
    core's evaluator against the validated collected bound; that result alone
    decides ``neg8.screen_failed``.
    """

    ISOLATE = Neg8ScreenTests.ISOLATE

    def harvest(self, name, failed, drift=0.0, *, stored_drift=None, **verdict):
        """Harvest a window whose end references sit ``drift`` collected bounds above its start references.

        ``stored_drift``: the verdict was written from references at another drift.
        """
        window = Window(self.tmp / name, catalog_overrides=self.ISOLATE)
        self.assertIsNone(neg8_corpus(window, failed))
        artifact = json.loads((window.bound / "neg8-drift-bound.json").read_bytes())
        bound = max(record["estimator"]["replicated_endpoint_bound_j"]
                    for record in artifact["claim_family_bounds"].values())
        points = neg8_trajectory(drift * bound)
        stored = write_neg8_reference_verdict(
            window, neg8_trajectory((drift if stored_drift is None else stored_drift) * bound), **verdict)
        self.assertEqual(set(stored["conditions"]), {whole_window.CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
                                                     whole_window.CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED})
        with neg8_reference_gates(points):
            window.harvest()
        check = json.loads((window.archive / "derived" / "neg8-bound.json").read_bytes())
        self.assertEqual(check["derived_from"], "collected_subset", check["problems"])
        screen = json.loads((window.archive / "derived" / "neg8-screen.json").read_bytes())
        return window, screen["rescreen"]

    def test_a_screen_that_passes_against_the_collected_bound_keeps_the_window(self):
        """Before the fix both windows were removed by neg8.screen_failed, whatever their drift."""
        for failed in ([CORPUS_IDS[4]], [CORPUS_IDS[0], CORPUS_IDS[11]]):
            with self.subTest(kept=12 - len(failed)):
                window, rescreen = self.harvest(f"pass{12 - len(failed)}", failed, drift=0.5)
                self.assertEqual((rescreen["evaluated"], rescreen["decision"], rescreen["conditions"],
                                  rescreen["problems"], rescreen["freshness"]["decision"]),
                                 (True, "passed", [], [], "fresh"))
                self.assertEqual(rescreen["evaluated_at_source"], "evaluation_scope.completed_at")
                self.assertFalse(rescreen["verdict_authenticated"])  # recorded, not required
                self.assertNotIn("neg8.screen_failed", window.codes())
                self.assertNotIn("neg8.bound_not_derived", window.codes())
                self.assertFalse({"neg8.screen_failed", "neg8.bound_not_derived"} & set(window.exclusions()["reasons"]))

    def test_drift_or_a_stale_bound_against_the_collected_bound_removes_the_window(self):
        cases = {
            "drift": ({"drift": 3.0}, {whole_window.CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED,
                                       whole_window.CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED}),
            # The verdict was written before the bound was derived: the core's freshness rule fails it.
            "stale": ({"completed_at": "2020-01-01T00:00:00.000000Z"}, {whole_window.CONDITION_NEG8_DRIFT_BOUND_STALE}),
        }
        for name, (kwargs, expected) in cases.items():
            with self.subTest(name):
                window, rescreen = self.harvest(name, [CORPUS_IDS[4]], **kwargs)
                self.assertEqual((rescreen["evaluated"], rescreen["decision"], set(rescreen["conditions"])),
                                 (True, "failed", expected))
                (flag,) = [flag for flag in window.flags() if flag["code"] == "neg8.screen_failed"]
                self.assertEqual(flag["observed"]["collected_bound_rescreen"], rescreen)
                self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    def test_a_rederivation_that_does_not_reproduce_the_stored_bracket_evaluates_nothing(self):
        """Reference bundles other than the verdict's (here: other energies) never decide the screen."""
        window, rescreen = self.harvest("other-references", [CORPUS_IDS[4]], drift=0.0, stored_drift=0.5)
        self.assertEqual((rescreen["evaluated"], rescreen["problems"]),
                         (False, ["rederivation_differs_from_stored_bracket"]))
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    def test_any_other_neg8_condition_is_not_re_evaluated(self):
        window, rescreen = self.harvest("other-condition", [CORPUS_IDS[4]],
                                        extra_conditions=["neg8_bracket_reference_invalid"])
        self.assertEqual((rescreen["evaluated"], rescreen["problems"]),
                         (False, ["conditions_beyond_bound_underived"]))
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    def test_a_source_manifest_that_changed_after_the_verdict_evaluates_nothing(self):
        window = Window(self.tmp / "manifest-changed", catalog_overrides=self.ISOLATE)
        neg8_corpus(window, [CORPUS_IDS[4]])
        write_neg8_reference_verdict(window, neg8_trajectory(0.0))
        path = window.claim / NEG8_REFERENCE_MANIFEST
        path.write_bytes(path.read_bytes() + b"\n")
        with neg8_reference_gates(neg8_trajectory(0.0)):
            window.harvest()
        rescreen = json.loads((window.archive / "derived" / "neg8-screen.json").read_bytes())["rescreen"]
        self.assertEqual((rescreen["evaluated"], rescreen["problems"]), (False, ["source_manifest_unauthenticated"]))
        self.assertIn("neg8.screen_failed", window.exclusions()["reasons"])

    def test_the_rederived_bracket_is_withheld_and_derived_outputs_carry_no_energy(self):
        window, _rescreen = self.harvest("blind", [CORPUS_IDS[4]], drift=3.0)
        withheld = json.loads((window.archive / "withheld" / "neg8-rescreen-bracket.json").read_bytes())
        family = withheld["bracket"]["claim_families"][whole_window.NEG8_CLAIM_FAMILY_GROSS]
        screen = (window.archive / "derived" / "neg8-screen.json").read_text()
        derived = screen + (window.archive / "derived" / "flags.jsonl").read_text()
        for value in (family["derived_repeatability_bound_j"], family["point_delta_j"], family["start"]["mean_j"],
                      family["end"]["mean_j"]):
            self.assertNotIn(repr(value), derived)
        self.assertNotIn('_j"', screen)
        self.assertNotIn("_s\"", screen)  # nor the verdict's evaluation time


class RegisteredThresholdTests(unittest.TestCase):
    """Registration 6.9: the harvest reads the registered flat block, never a default."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="b5-thresholds-", dir=REAL_TMP)
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def registration(self, text=None) -> Path:
        path = self.root / REGISTRATION_RELATIVE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(registration_text() if text is None else text)
        return path

    def plan(self, registration=None, recorded_sha=True, **hazard):
        window = {"thresholds": copy.deepcopy(L2_NESTED_THRESHOLDS), **hazard}
        if registration is not None:
            window["registration"] = {"path": str(registration),
                                      "sha256": sha(registration) if recorded_sha is True else recorded_sha}
        return {"plan_id": PLAN_ID, "hazard_window": window}

    def test_l2_nested_thresholds_alone_are_unregistered_not_defaulted(self):
        """Before the fix the nested block was ignored and the defaults applied without a trace."""
        values, provenance = h.resolve_thresholds(self.plan(), self.root)
        self.assertEqual(values, {})
        self.assertEqual(provenance["problems"], ["harvest_thresholds_unregistered",
                                                  *(f"missing:{key}" for key in h.HARVEST_THRESHOLD_KEYS)])

    def test_the_named_registration_is_read(self):
        path = self.registration()
        values, provenance = h.resolve_thresholds(self.plan(path), self.root)
        self.assertEqual(values, REGISTERED_HARVEST_THRESHOLDS)
        self.assertEqual(provenance["problems"], [])
        self.assertEqual(provenance["key_sources"], {key: ["registration"] for key in h.HARVEST_THRESHOLD_KEYS})
        self.assertEqual(provenance["registration"], {"path": str(path), "sha256": sha(path),
                                                      "recorded_sha256": sha(path)})
        relative = self.plan(Path(REGISTRATION_RELATIVE), recorded_sha=sha(path))  # resolves in the checkout
        self.assertEqual(h.resolve_thresholds(relative, self.root)[0], REGISTERED_HARVEST_THRESHOLDS)

    def test_the_design_branch_registration_parses_to_the_registered_block(self):
        raw = design_branch_file(REGISTRATION_RELATIVE)
        if raw is None:
            self.skipTest(f"{DESIGN_BRANCH} is not in this clone")
        self.assertEqual(h.parse_registration_thresholds(raw), REGISTERED_HARVEST_THRESHOLDS)

    def test_problems_are_recorded_and_registered_values_are_never_replaced(self):
        path = self.registration()
        partial = {key: value for key, value in REGISTERED_HARVEST_THRESHOLDS.items()
                   if key != "battery_accumulator_watts_per_unit"}
        cases = {
            "digest_differs": (self.plan(path, recorded_sha="0" * 64), {}, None,
                               "registration_digest_differs_from_plan"),
            "plan_block_disagrees": (self.plan(path, harvest_thresholds=dict(REGISTERED_HARVEST_THRESHOLDS,
                                                                             battery_limit_ma=400)), {}, None,
                                     "sources_disagree:battery_limit_ma"),
            "override_differs": (self.plan(path), {"battery_limit_ma": 400}, None,
                                 "override_differs_from_registered:battery_limit_ma"),
            "override_unknown": (self.plan(path), {"battery_limit": 400}, None, "override_unknown_key:battery_limit"),
            "key_missing": (self.plan(path), {}, registration_text(partial),
                            "missing:battery_accumulator_watts_per_unit"),
            "scale_null": (self.plan(path), {}, registration_text(dict(REGISTERED_HARVEST_THRESHOLDS,
                                                                       battery_accumulator_watts_per_unit=None)),
                           "invalid:battery_accumulator_watts_per_unit:must be a finite number > 0"),
            "unknown_key": (self.plan(path), {}, registration_text(dict(REGISTERED_HARVEST_THRESHOLDS, extra=1)),
                            "unknown_keys:registration:extra"),
            "two_headings": (self.plan(path), {}, registration_text() + "\n### 6.9 Harvest thresholds\n",
                             "registration_block_unreadable:expected one 'Harvest thresholds' heading, found 2"),
            "no_block": (self.plan(path), {}, "# R\n\n### 6.9 Harvest thresholds\n\nNone.\n\n## 7\n\n```json\n{}\n```\n",
                         "registration_block_unreadable:no ```json block under the 'Harvest thresholds' heading"),
        }
        for name, (plan, overrides, text, problem) in cases.items():
            with self.subTest(name):
                self.registration(text)
                if text is not None and name != "digest_differs":
                    plan["hazard_window"]["registration"]["sha256"] = sha(path)
                values, provenance = h.resolve_thresholds(plan, self.root, overrides=overrides)
                self.assertIn(problem, provenance["problems"])
                if name in ("plan_block_disagrees", "override_differs"):
                    self.assertEqual(values["battery_limit_ma"], 200)  # the registration's value stands
                if name in ("key_missing", "scale_null"):
                    self.assertNotIn("battery_accumulator_watts_per_unit", values)
                self.registration()

    def test_the_plans_flat_copy_alone_is_a_registered_source(self):
        values, provenance = h.resolve_thresholds(
            self.plan(harvest_thresholds=dict(REGISTERED_HARVEST_THRESHOLDS)), self.root)
        self.assertEqual((values, provenance["problems"], provenance["sources"]),
                         (REGISTERED_HARVEST_THRESHOLDS, [], ["plan"]))
        path = self.registration()
        values, provenance = h.resolve_thresholds(
            self.plan(path, harvest_thresholds=dict(REGISTERED_HARVEST_THRESHOLDS)), self.root)
        self.assertEqual((provenance["problems"], provenance["sources"]), ([], ["plan", "registration"]))


class ThresholdAndAccumulatorHarvestTests(WindowTestCase):
    def thresholds(self, window) -> dict:
        return json.loads((window.archive / "derived" / "harvest-thresholds.json").read_bytes())

    def test_registered_block_is_used_and_recorded(self):
        window = self.window()
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        recorded = self.thresholds(window)
        self.assertEqual((recorded["values"], recorded["problems"]), (REGISTERED_HARVEST_THRESHOLDS, []))
        self.assertEqual(recorded["registration"]["sha256"], sha(window.registration))
        self.assertEqual(sha(window.archive / "sources" / "inputs" / "registration.md"), sha(window.registration))
        self.assertIn("derived/harvest-thresholds.json", record["outputs"])

    def test_plan_without_the_registered_block_is_a_recorded_harvest_fault(self):
        """Before the fix this window came out COLLECTED on the module's own defaults."""
        window = self.window(registration=False)
        record = window.harvest()
        self.assertEqual(record["verdict"], "HARVEST_FAULT")
        self.assertFalse(record["claim_usable"])
        self.assertIn("thresholds", {fault["collector"] for fault in record["faults"]})
        self.assertIn("harvest_thresholds_unregistered", self.thresholds(window)["problems"])
        self.assertIn("harvest.fault", window.window_flags()["exclusions"]["reasons"])
        self.assertTrue(window.flags())  # numbers and flags are still written
        # The cure: name the registration and re-harvest the same bytes.
        registration = window.root / "registration_block5.md"
        registration.write_text(registration_text())
        inputs = h.resolve_inputs(window.plan_path, {"registration_path": str(registration)})
        cured = h.harvest(inputs, window.root / "archive-cured", seams=h.Seams(
            group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS, boot_session_uuid=lambda: "B5"))
        self.assertEqual(cured["verdict"], "COLLECTED", cured["faults"])

    def test_registration_without_the_scale_faults_and_never_demotes_the_accumulator(self):
        block = {key: value for key, value in REGISTERED_HARVEST_THRESHOLDS.items()
                 if key != "battery_accumulator_watts_per_unit"}
        window = self.window(registration_block=block)
        record = window.harvest()
        self.assertEqual(record["verdict"], "HARVEST_FAULT")
        self.assertEqual({fault["collector"] for fault in record["faults"]}, {"thresholds", "monitor.battery"})
        self.assertIn("missing:battery_accumulator_watts_per_unit", self.thresholds(window)["problems"])
        self.assertEqual({code for code in window.codes() if code.startswith("battery.accumulator")}, set())
        # The other modules' joins still ran.
        self.assertNotIn("monitor", {fault["collector"] for fault in record["faults"]})

    def test_accumulator_excursion_excludes_the_member_at_the_registered_scale(self):
        """Before the fix the plan's nested block left the scale None: a disclosed diagnostic, no exclusion."""
        target = "b5t-abs-r02"
        lo, hi = member_span_ns(target)
        start = lo - 10 * NS

        def telemetry(effect_ns):  # charging at +5,400 mW from 10 s before the target's stream to its end
            ticks = max(0, min(effect_ns, hi) - start) // NS
            return {**STEADY_TELEMETRY, "AccumulatedBatteryPower": 1_000_000 + 5_400 * ticks,
                    "BatteryPowerAccumulatorCount": 4727 + ticks}

        window = self.window(journals={"telemetry": telemetry})
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        flagged = {flag["scope"]["run_id"] for flag in window.flags() if flag["code"] == "battery.accumulator_excursion"}
        self.assertEqual(flagged, {target})
        self.assertNotIn("battery.member_span", window.codes(target))  # InstantAmperage read 0 throughout
        self.assertIn(target, {row["run_id"] for row in window.exclusions()["members_excluded"]})


class LineageFindingTests(WindowTestCase):
    """L3's lineage audit reaches the flag record: every finding a flag, none a refusal."""

    LOCATOR = ".joulewise-launch-lineage.json"

    def publish(self, window):
        from joulewise import window_lineage
        return window_lineage.publish_window_lineage(
            pack_root=window.pack, pack_id=PACK_ID, plan_id=PLAN_ID, window_id=PLAN_ID,
            bracket_session_id=SESSION_ID, pre_attempt_id=f"{SESSION_ID}-pre", post_attempt_id=f"{SESSION_ID}-post",
            claim_runs_root=window.claim, bound_runs_root=window.bound, custody_root=window.custody,
            pack_sha256="c" * 64, boot_session_id=str(uuid.UUID(int=5)))

    def lineage_flags(self, window) -> list[dict]:
        return [flag for flag in window.flags() if flag["code"].startswith("lineage.")]

    def test_an_unpublished_lineage_is_recorded_not_refused(self):
        """Before the fix no lineage finding reached the record."""
        window = self.window()
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED")
        flags = self.lineage_flags(window)
        self.assertEqual(sorted((flag["code"], flag["scope"]["level"], flag["observed"]["root_role"]) for flag in flags),
                         [("lineage.locator_unreadable", "window", "bound_runs_root"),
                          ("lineage.locator_unreadable", "window", "claim_runs_root")])
        self.assertFalse(any(code.startswith("lineage.") for code in window.exclusions()["reasons"]))
        self.assertEqual(window.window_flags()["flags"]["unclassified"], [])

    def test_published_lineage_findings_become_flags_with_archived_evidence(self):
        window = self.window()
        published = self.publish(window)
        # One marker-bearing member without a stamp; the untagged seed members
        # carry none by design and are not findings (rehearsal round 1, B6).
        config = json.loads((window.claim / "b5t-abs-r01" / "config.json").read_bytes())
        config["run_metadata"]["tags"].append("launch_lineage_required")
        (window.claim / "b5t-abs-r01" / "config.json").write_bytes(normalized_config(config))
        sidecar = window.claim / f"{self.LOCATOR}.sha256"
        sidecar.write_text(f"{'0' * 64}  {self.LOCATOR}\n")
        tree = json.loads((window.pack / "plan_tree.json").read_bytes())
        tree["b5t_edited_after_publication"] = True
        put(window.pack / "plan_tree.json", tree)
        (window.pack / "plan_tree.sha256").write_text(f"{sha(window.pack / 'plan_tree.json')}  plan_tree.json\n")
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        flags = self.lineage_flags(window)
        by_code = {}
        for flag in flags:
            by_code.setdefault(flag["code"], []).append(flag)
        self.assertEqual(set(by_code), {"lineage.locator_sidecar_mismatch", "lineage.plan_tree_digest_differs",
                                        "lineage.bundle_stamp_absent"})
        (mismatch,) = by_code["lineage.locator_sidecar_mismatch"]
        self.assertEqual((mismatch["scope"]["level"], mismatch["observed"]["root_role"]), ("window", "claim_runs_root"))
        self.assertEqual(sorted(item["path"] for item in mismatch["evidence"]),
                         [f"sources/night-custody/runs_claim/{self.LOCATOR}",
                          f"sources/night-custody/runs_claim/{self.LOCATOR}.sha256"])
        for item in mismatch["evidence"]:
            self.assertEqual(sha(window.archive / item["path"]), item["sha256"])
        (digest,) = by_code["lineage.plan_tree_digest_differs"]
        self.assertEqual((digest["family"], digest["klass"]), ("PACK_IDENTITY", "NUMBER"))
        self.assertEqual(digest["observed"]["observed"], sha(window.pack / "plan_tree.json"))
        self.assertEqual(digest["expected"], published["launch_lineage"]["plan_tree_sha256"])
        self.assertEqual([item["path"] for item in digest["evidence"]],
                         [f"sources/repo/configs/campaigns/{PACK_ID}/plan_tree.json"])
        # The tagged member carries no lineage stamp: one member-level record, disclosed.
        self.assertEqual({flag["scope"]["run_id"] for flag in by_code["lineage.bundle_stamp_absent"]},
                         {"b5t-abs-r01"})
        reasons = window.exclusions()["reasons"]
        self.assertIn("lineage.plan_tree_digest_differs", reasons)
        self.assertNotIn("lineage.locator_sidecar_mismatch", reasons)
        self.assertFalse(any("lineage.bundle_stamp_absent" in row["codes"]
                             for row in window.exclusions()["members_excluded"]))
        for flag in flags:
            self.assertEqual(h.flag_problems(flag), [], flag["code"])

    def test_an_audit_that_raises_is_a_harvest_fault(self):
        """The plan-tree comparison (a window exclusion) never drops out behind a disclosed collector failure.

        Before the fix the step recorded only records.collector_failed
        (DISCLOSE) and the window stayed claim-usable unaudited.
        """
        from joulewise import window_lineage
        window = self.window()
        self.publish(window)
        with mock.patch.object(window_lineage, "audit_window_lineage", side_effect=RuntimeError("audit bug")):
            record = window.harvest()
        self.assertEqual(record["verdict"], "HARVEST_FAULT")
        self.assertIn("lineage", [fault["collector"] for fault in record["faults"]])
        self.assertFalse(record["claim_usable"])
        self.assertEqual(self.lineage_flags(window), [])
        self.assertTrue((window.archive / "derived" / "flags.jsonl").is_file())  # numbers and flags still written


class EmittedCodeTests(unittest.TestCase):
    """Fix lane fx-harvest (6): every code the harvest can emit, against the catalog."""

    def test_every_code_literal_in_the_harvest_is_listed(self):
        source = (ROOT / "joulewise/b5/harvest.py").read_text()
        families = {code.split(".", 1)[0] for code in h.CODES}
        literals = {match for match in re.findall(r'"([a-z0-9_]+\.[a-z0-9_.]+)"', source)
                    if match.split(".", 1)[0] in families and h.CODE_RE.fullmatch(match)}
        built = {f"{module}.unmeasured" for module in ("battery", "thermal", "contention", "clock")} \
            | {f"instrument.{reason}" for reason in h.INSTRUMENT_REASONS}
        not_codes = {"g3.txt", "roster.json",  # file names
                     "chain.started", "monitor.capture_battery",  # a night record and a collector name
                     "yield.json"}  # a file name
        self.assertEqual((literals | built) - not_codes - set(h.CODES), set())

    def test_every_lineage_finding_code_is_listed_with_l3s_family(self):
        from joulewise import window_lineage
        self.assertEqual(set(window_lineage.FINDING_CODES), set(h.LINEAGE_CODES))
        self.assertEqual({code for code in h.LINEAGE_CODES if h.CODES[code].klass == "NUMBER"},
                         {"lineage.plan_tree_digest_differs"})

    def test_the_sealed_catalog_classifies_every_emitted_code(self):
        raw = (ROOT / SEALED_DIR / "flag_catalog.json").read_bytes() \
            if (ROOT / SEALED_DIR / "flag_catalog.json").is_file() else design_branch_file(f"{SEALED_DIR}/flag_catalog.json")
        if raw is None:
            self.skipTest("neither the sealed catalog nor the block-5 design branch is in this clone")
        codes = json.loads(raw)["codes"]
        # The gate-prune round-2 and round-3 codes reach the draft through the
        # registration row (REG) before the seal; any other unclassified code fails here.
        missing = set(h.CODES) - set(codes)
        self.assertEqual(missing - h.PRUNE2_CODES - h.PRUNE3_CODES - h.AUDFIX1_CODES - h.AUDFIX2_CODES
                         - h.NEG8_SURVIVOR_CODES,
                         set(h.NEVER_CLASSIFIED_CODES))
        self.assertTrue(h.NEVER_CLASSIFIED_CODES.isdisjoint(codes))

    def test_the_design_catalog_classifies_every_int4_code_with_the_drafts_effect(self):
        """int4 sync: no round-2 or round-3 exemption remains; the draft's effects are the catalog's."""
        raw = (ROOT / SEALED_DIR / "flag_catalog.json").read_bytes() \
            if (ROOT / SEALED_DIR / "flag_catalog.json").is_file() else design_branch_file(f"{SEALED_DIR}/flag_catalog.json")
        if raw is None:
            self.skipTest("neither the sealed catalog nor the block-5 design branch is in this clone")
        from joulewise.flags.catalog import DRAFT_CODES
        from joulewise.flags.core import CORE_FLAG_CODES
        codes = json.loads(raw)["codes"]
        emitted = set(h.CODES) | set(DRAFT_CODES) | set(CORE_FLAG_CODES)
        # Audit-fix batches 1 and 2's codes and the NEG-8 survivors codes (ruling
        # 2026-10-07) reach the design catalog through REG before the seal.
        self.assertEqual(emitted - set(codes) - h.AUDFIX1_CODES - h.AUDFIX2_CODES - h.NEG8_SURVIVOR_CODES,
                         set(h.NEVER_CLASSIFIED_CODES))
        self.assertEqual({code: (codes[code]["effect"], DRAFT_CODES[code]["effect"]) for code in DRAFT_CODES
                          if code in codes and codes[code]["effect"] != DRAFT_CODES[code]["effect"]}, {})


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
        overrides = {"power_telemetry": dict(STEADY_TELEMETRY), **overrides}
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
    T = REGISTERED_HARVEST_THRESHOLDS

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
        # A charge current (positive) in force excludes; the battery-assist
        # ruling (2026-10-06) discloses the same magnitude of discharge.
        readings = battery_journal([(0, {}), (60, {"instant_amperage_ma": 447}), (120, {}), (180, {})])
        span = [publication_ns(70), publication_ns(100)]
        self.assertIn("battery.member_span", [code for code, *_ in h.battery_member_flags(span, readings, self.T)])
        clean = h.battery_member_flags([publication_ns(130), publication_ns(170)], readings, self.T)
        self.assertNotIn("battery.member_span", [code for code, *_ in clean])
        discharge = battery_journal([(0, {}), (60, {"instant_amperage_ma": -447}), (120, {}), (180, {})])
        codes = [code for code, *_ in h.battery_member_flags(span, discharge, self.T)]
        self.assertNotIn("battery.member_span", codes)
        self.assertIn("battery.assist", codes)

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
        # No SMC read in these journals: the registry is judged and the fallback disclosed.
        # Neither excludes; a discharge is assist (any negative current, ruling
        # item 1 and review F5), disclosed.
        for current, expected in ((-200, ["battery.smc_unavailable", "battery.assist"]),
                                  (200, ["battery.smc_unavailable"])):
            readings = battery_journal([(0, {}), (60, {"instant_amperage_ma": current}), (120, {})])
            codes = [code for code, *_ in h.battery_member_flags([publication_ns(65), publication_ns(70)],
                                                                 readings, self.T)]
            self.assertEqual(codes, expected, current)

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
        self.assertEqual(codes, ["battery.unmeasured", "battery.smc_unavailable"])

    # Registration 6.4's worked example: between two publications the discharge
    # accumulator gains 40 ticks totalling -216,000 (mW x tick): mean -5,400 mW,
    # above 200 mA x 12.18 V = 2,436 mW.  The calibration-capture assist: 20
    # ticks at -130 mW, below it.
    EXCURSION = [STEADY_TELEMETRY, {**STEADY_TELEMETRY, "AccumulatedBatteryDischarge": -2_216_000,
                                    "BatteryDischargeAccumulatorCount": 22710}]
    ASSIST = [STEADY_TELEMETRY, {**STEADY_TELEMETRY, "AccumulatedBatteryDischarge": -2_002_600,
                                 "BatteryDischargeAccumulatorCount": 22690}]
    RESET = [STEADY_TELEMETRY, {**STEADY_TELEMETRY, "BatteryDischargeAccumulatorCount": 12}]
    # The same mean on the charge accumulator: +216,000 over 40 ticks, +5,400 mW.
    CHARGE_EXCURSION = [STEADY_TELEMETRY, {**STEADY_TELEMETRY, "AccumulatedBatteryPower": 1_216_000,
                                           "BatteryPowerAccumulatorCount": 4767}]

    def accumulator_codes(self, telemetry, thresholds=None):
        """The battery flags but the SMC fallback disclosure (these journals hold no SMC read)."""
        readings = battery_journal([(0, {"power_telemetry": telemetry[0]}), (60, {"power_telemetry": telemetry[1]})],
                                   end_s=120)
        return [flag for flag in h.battery_member_flags([publication_ns(10), publication_ns(20)], readings,
                                                        thresholds or self.T)
                if flag[0] != "battery.smc_unavailable"]

    def test_accumulator_rule_runs_at_the_registered_scale(self):
        """Fix lane fx-harvest (4): one rule with L1; the scale is registered (0.001 W per unit), never None.

        Under the battery-assist ruling (2026-10-06) only the charge
        accumulator above the limit excludes; the discharge accumulator above
        it is battery.assist (DISCLOSE).
        """
        ((code, observed, interval),) = self.accumulator_codes(self.CHARGE_EXCURSION)
        self.assertEqual(code, "battery.accumulator_excursion")
        (row,) = observed["intervals"]
        self.assertEqual((row["accumulator"], row["ticks"], row["mean_per_tick"]), ("charge", 40, 5400.0))
        self.assertAlmostEqual(row["mean_w"], 5.4)
        self.assertAlmostEqual(row["limit_w"], 2.436)
        self.assertEqual(interval, {"monotonic_ns": [publication_ns(0), publication_ns(60)]})
        ((code, observed, _interval),) = self.accumulator_codes(self.EXCURSION)
        self.assertEqual(code, "battery.assist")
        self.assertEqual(observed["phases"]["span"]["accumulator_intervals_over_limit"], 1)
        self.assertEqual([code for code, *_ in self.accumulator_codes(self.ASSIST)], ["battery.accumulator_activity"])
        self.assertEqual([code for code, *_ in self.accumulator_codes([STEADY_TELEMETRY, STEADY_TELEMETRY])], [])
        ((code, observed, _interval),) = self.accumulator_codes(self.RESET)
        self.assertEqual(code, "battery.accumulator_unavailable")
        self.assertIn("went backward", observed["intervals"][0]["unavailable"]["discharge"])
        # Fields not read at a publication: the rule cannot run there, and says so.
        self.assertEqual([code for code, *_ in self.accumulator_codes([{}, {}])], ["battery.accumulator_unavailable"])

    def test_an_unregistered_scale_is_never_a_silent_diagnostic(self):
        """Before the fix, ``battery_accumulator_watts_per_unit = None`` demoted the rule to a diagnostic."""
        for unit in (None, 0, "0.001"):
            with self.subTest(unit=unit), self.assertRaises(ValueError):
                self.accumulator_codes(self.EXCURSION, dict(self.T, battery_accumulator_watts_per_unit=unit))
        missing = {key: value for key, value in self.T.items() if key != "battery_accumulator_watts_per_unit"}
        with self.assertRaises(KeyError):
            self.accumulator_codes(self.EXCURSION, missing)
        self.assertNotIn("battery.accumulator_diagnostic", h.CODES)

    @unittest.skipUnless(L1_AVAILABLE, "lane L1's joulewise.hazards is not in this tree")
    def test_accumulator_verdicts_equal_l1s_span_findings(self):
        """The same intervals, signs and limit as L1's ``battery.span_findings`` (L1 names an excursion member_span)."""
        from joulewise.hazards import battery as l1
        l1_name = {"battery.member_span": "battery.accumulator_excursion"}
        for name, telemetry in (("excursion", self.EXCURSION), ("assist", self.ASSIST), ("reset", self.RESET),
                                ("steady", [STEADY_TELEMETRY, STEADY_TELEMETRY])):
            with self.subTest(name):
                journal = L1Journal("battery")
                for second, values in ((0, telemetry[0]), (60, telemetry[1])):
                    effect = publication_ns(second)
                    journal.write("reading", effect + 2 * NS, effect + 2 * NS + 1_000,
                                  values=battery_values(second + 10_000, power_telemetry=values))
                span = {"monotonic_ns": [publication_ns(10), publication_ns(20)]}
                limits = {"limit_ma": 200, "max_update_age_s": 180, "max_unobserved_s": 120}
                found = {code for code, *_ in h.battery_member_flags(span["monotonic_ns"], parsed(journal), self.T)}
                ours = {code for code in found if code.startswith("battery.accumulator")}
                # battery.smc_unavailable: these journals hold no SMC B0AC reads, so both
                # disclose their registry fallback.
                theirs = {l1_name.get(finding["code"], finding["code"])
                          for finding in l1.span_findings(journal.lines, span, limits)
                          if finding["code"] not in ("battery.unmeasured", "battery.smc_unavailable")}
                if name == "excursion":
                    # A discharge accumulator above the limit is battery assist under the
                    # ruling of 2026-10-06: L1 discloses it (battery.assist), and so does the
                    # harvest copy (no accumulator code); neither excludes it.
                    self.assertIn("battery.assist", theirs)
                    self.assertIn("battery.assist", found)
                    theirs.discard("battery.assist")
                    ours.discard("battery.accumulator_excursion")
                self.assertEqual(ours, theirs)

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

    def test_contention_limit_is_pinned_on_both_sides(self):
        """0.06 CPU-s/s flags and 0.04 does not, under the registered 0.05 (ported from L4's removed join test)."""
        self.assertEqual(self.T["contention_cpu_s_per_s"], 0.05)
        for load, want in ((0.06, ["contention.request_overlap"]), (0.04, []), (0.05, [])):
            journal = L1Journal("contention")
            journal.write("snapshot", -NS)
            journal.write("interval", 0, 10 * NS, values=contention_values(0, 10 * NS, [
                {"pid": 400, "command": "mds", "cpu_s_per_s": load}], kernel_task=0.9))
            codes = [code for code, *_ in h.contention_member_flags([2 * NS, 3 * NS], parsed(journal), self.T)]
            self.assertEqual(codes, want, load)

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

    def preempted_clock_journal(self, sample_30: str, step_at_ns: int | None = None) -> L1Journal:
        """60 samples at 1 Hz, f every 5 s, with sample 30 written as the monitor writes a preempted read.

        ``sample_30``: ``"rejected"`` (every read rejected: no anchor, the reads kept, a
        clock.unmeasured error) or ``"recorded"`` (a journal from before the re-read: an
        8.3 ms skew anchor, 4.15 ms low).
        """
        journal = L1Journal("clock")
        for second in range(60):
            raw = second * NS + RAW_OFFSET_NS
            anchor = 10**15 + DRIFT_WORD * (second * NS) // (kernel_clock.FREQUENCY_SCALE * 10**6) \
                + (2_000_000 if step_at_ns is not None and second * NS >= step_at_ns else 0)
            values, error = clock_values(raw, anchor, frequency=second % 5 == 0), None
            if second == 30 and sample_30 == "rejected":
                rejected = [dict(values["anchor"], read_skew_ns=8_000_400)] * 5
                values, error = {"anchor": None, "frequency": values["frequency"], "rejected_anchors": rejected}, \
                    "clock.unmeasured: anchor read skew above 250000 ns on all 5 reads (8000400-8000400 ns)"
            elif second == 30 and sample_30 == "recorded":
                values["anchor"] = dict(values["anchor"], anchor_ns=anchor - 4_150_000, read_skew_ns=8_300_400)
            journal.write("reading", second * NS - 600, second * NS, values=values, error=error)
        return journal

    def test_a_real_step_beside_a_rejected_clock_read_is_still_seen(self):
        """Review F1: a fully rejected sample used to break the chain and hide a real step."""
        journal = self.preempted_clock_journal("rejected", step_at_ns=30 * NS + NS // 2)
        steps, changes = h.clock_steps(parsed(journal), self.T)
        self.assertEqual([step["interval_monotonic_ns"] for step in steps], [[29 * NS - 600, 31 * NS]])
        self.assertAlmostEqual(steps[0]["residual_move_ns"], 2_000_000, delta=1_000)
        self.assertEqual(changes, [])

    def test_a_preempted_clock_read_is_never_a_step_and_is_disclosed(self):
        """R3-1 in the harvest copy: a recorded anchor over the skew bound is not compared;
        a member over a preempted sample gets clock.unmeasured (read_skew), a clear one nothing."""
        for case in ("rejected", "recorded"):
            with self.subTest(case):
                readings = parsed(self.preempted_clock_journal(case))
                self.assertEqual(h.clock_steps(readings, self.T), ([], []))
                found = h.clock_member_flags([28 * NS, 32 * NS], readings, self.T)
                self.assertEqual([(code, observed.get("rule"), observed.get("samples"))
                                  for code, observed, _interval in found],
                                 [("clock.unmeasured", "read_skew", 1)])
                self.assertEqual(found[0][2], {"monotonic_ns": [30 * NS - 600, 30 * NS]})
                self.assertEqual(h.clock_member_flags([40 * NS, 50 * NS], readings, self.T), [])

    def test_an_f_read_beside_a_rejected_clock_read_still_records_the_change(self):
        """Review F5 in the harvest copy: the f a preempted sample read is still used."""
        journal = self.preempted_clock_journal("rejected")
        line = journal.lines[30]
        line["values"]["frequency"] = frequency_probe(round(-3.0 * kernel_clock.FREQUENCY_SCALE))
        _steps, changes = h.clock_steps(parsed(journal), self.T)
        self.assertEqual([(change["monotonic_ns"], change["ppm"]) for change in changes],
                         [(30 * NS, -3.0), (35 * NS, DRIFT_WORD / kernel_clock.FREQUENCY_SCALE)])

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


@unittest.skipUnless(L1_AVAILABLE, "lane L1's joulewise.hazards is not in this tree")
class BatteryRuleParityTests(unittest.TestCase):
    """The hazard copy (``joulewise.hazards.battery.span_findings``) and the harvest
    copy (``harvest.battery_member_flags``) of the member battery rule decide the
    same way on the same journal (battery-assist ruling 2026-10-06, item 4: no
    contradictory discharge exclusion anywhere).

    The harvest names the accumulator exclusion ``battery.accumulator_excursion``
    where the hazard copy names it ``battery.member_span``; both are
    EXCLUDE_MEMBER, so they are compared as one code.
    """

    T = REGISTERED_HARVEST_THRESHOLDS
    LIMITS = {"limit_ma": 200, "max_update_age_s": 180, "max_unobserved_s": 120}
    SPAN = (10, 20)
    # Discharge accumulator, 40 ticks between publications 0 and 60 (limit 200 mA x
    # 12.18 V = 2,436 mW): -5,400 mW is assist; +5,400 mW (the accumulator rose,
    # which a discharge-only sum cannot do) is sign-inconsistent and excluded.
    DISCHARGE_OVER = {**STEADY_TELEMETRY, "AccumulatedBatteryDischarge": -2_216_000,
                      "BatteryDischargeAccumulatorCount": 22710}
    DISCHARGE_UNDER = {**STEADY_TELEMETRY, "AccumulatedBatteryDischarge": -2_002_600,
                       "BatteryDischargeAccumulatorCount": 22690}
    DISCHARGE_ROSE = {**STEADY_TELEMETRY, "AccumulatedBatteryDischarge": -1_784_000,
                      "BatteryDischargeAccumulatorCount": 22710}
    DISCHARGE_ROSE_UNDER = {**STEADY_TELEMETRY, "AccumulatedBatteryDischarge": -1_997_400,
                            "BatteryDischargeAccumulatorCount": 22690}
    CHARGE_OVER = {**STEADY_TELEMETRY, "AccumulatedBatteryPower": 1_216_000, "BatteryPowerAccumulatorCount": 4767}

    def journal(self, *, later_telemetry=None, registry=None, smc=None):
        """Publications at 0, 60 and 120 s (the span is 10-20 s), each with the ``registry`` overrides;
        the accumulators move between 0 and 60 s; SMC B0AC once a second when given."""
        journal = L1Journal("battery")
        for index, second in enumerate((0, 60, 120)):
            telemetry = dict(STEADY_TELEMETRY if index == 0 or later_telemetry is None else later_telemetry)
            overrides = dict(registry or {})
            effect = publication_ns(second)
            journal.write("reading", effect + 2 * NS, effect + 2 * NS + 1_000,
                          values=battery_values(second + 10_000, power_telemetry=telemetry, **overrides))
        if smc is not None:
            from joulewise.hazards import battery as l1
            for index, second in enumerate(range(-30, 150)):
                poll = publication_ns(0) + second * NS + 500_000_000
                values = {"B0AC": smc(second), "B0AV": 12500, "PDTR": 60.0, "PSTR": 60.0 + index / 1000,
                          "PPBR": 0.0}
                sample = l1.smc_sample(lambda values=values: {"values": values, "errors": {}})
                journal.write("reading", poll - 400_000, poll, values={"source": "smc", "smc": sample})
        journal.lines.sort(key=lambda line: line["finished"]["monotonic_ns"])
        return journal

    def both(self, journal):
        from joulewise.hazards import battery as l1
        span = [publication_ns(self.SPAN[0]), publication_ns(self.SPAN[1])]
        harvest = {"battery.member_span" if code == "battery.accumulator_excursion" else code
                   for code, *_ in h.battery_member_flags(span, parsed(journal), self.T)}
        hazard = {finding["code"] for finding in l1.span_findings(journal.lines, {"monotonic_ns": span},
                                                                  self.LIMITS)}
        return harvest, hazard

    CASES = {
        # name: (journal keywords, expected codes in both copies, smc_unavailable aside)
        "steady": ({}, set()),
        "discharge_accumulator_over_limit": ({"later_telemetry": DISCHARGE_OVER}, {"battery.assist"}),
        "discharge_accumulator_under_limit": ({"later_telemetry": DISCHARGE_UNDER},
                                              {"battery.accumulator_activity"}),
        "discharge_accumulator_rose_over_limit": ({"later_telemetry": DISCHARGE_ROSE}, {"battery.member_span"}),
        "discharge_accumulator_rose_under_limit": ({"later_telemetry": DISCHARGE_ROSE_UNDER},
                                                   {"battery.accumulator_activity"}),
        "charge_accumulator_over_limit": ({"later_telemetry": CHARGE_OVER}, {"battery.member_span"}),
        "registry_discharge": ({"registry": {"instant_amperage_ma": -500, "amperage_ma": -480}},
                               {"battery.assist"}),
        "registry_small_discharge": ({"registry": {"instant_amperage_ma": -50, "amperage_ma": -40}},
                                     {"battery.assist"}),
        "registry_charge": ({"registry": {"instant_amperage_ma": 500, "amperage_ma": 480}},
                            {"battery.member_span"}),
        "charging_state_with_discharge": ({"registry": {"is_charging": True, "instant_amperage_ma": -500,
                                                        "amperage_ma": -480}}, {"battery.member_span"}),
        "smc_zero": ({"smc": lambda second: 0}, set()),
        "smc_discharge": ({"smc": lambda second: -800}, {"battery.assist"}),
        "smc_small_discharge": ({"smc": lambda second: -100}, {"battery.assist"}),
        "smc_charge_inside_span": ({"smc": lambda second: 800 if second == 15 else 0}, {"battery.member_span"}),
        # Cold pass N4: with the 1 Hz SMC reads covering the span, a sign-inconsistent
        # discharge accumulator is disclosed, not excluded (before: battery.member_span).
        "smc_discharge_with_rose_accumulator": ({"smc": lambda second: -800, "later_telemetry": DISCHARGE_ROSE},
                                                {"battery.accumulator_unavailable", "battery.assist"}),
        "smc_zero_with_rose_accumulator": ({"smc": lambda second: 0, "later_telemetry": DISCHARGE_ROSE},
                                           {"battery.accumulator_unavailable"}),
        "smc_charge_with_rose_accumulator": ({"smc": lambda second: 800 if second == 15 else 0,
                                              "later_telemetry": DISCHARGE_ROSE},
                                             {"battery.member_span", "battery.accumulator_unavailable"}),
    }

    def test_hazard_and_harvest_copies_decide_alike(self):
        for name, (keywords, expected) in self.CASES.items():
            with self.subTest(name):
                harvest, hazard = self.both(self.journal(**keywords))
                self.assertEqual(harvest, hazard)
                self.assertEqual(expected, harvest - {"battery.smc_unavailable"})

    def test_a_sign_inconsistent_discharge_accumulator_stays_an_exclusion_in_the_harvest(self):
        """P3-HAZ review F2, mirrored: a positive discharge-accumulator mean over the limit is not assist."""
        flags = h.accumulator_member_flags(
            h.battery_publications(parsed(self.journal(later_telemetry=self.DISCHARGE_ROSE)))[:2], self.T,
            discharge_out=(rows := []))
        self.assertEqual([], rows)
        ((code, observed, _interval),) = flags
        self.assertEqual("battery.accumulator_excursion", code)
        (row,) = observed["intervals"]
        self.assertEqual(("discharge", 40, 5400.0, True),
                         (row["accumulator"], row["ticks"], row["mean_per_tick"], row["sign_inconsistent"]))
        self.assertIn(code, h.BATTERY_EXCLUDING_CODES)
        catalog = json.loads((FIXTURES / "flag_catalog.json").read_text())
        self.assertEqual("EXCLUDE_MEMBER", catalog["codes"][code]["effect"])


    def test_a_sign_inconsistent_accumulator_under_smc_coverage_is_disclosed(self):
        """Cold pass N4: the SMC measured the current over the span; the record disagreeing with itself is disclosed."""
        flags = h.accumulator_member_flags(
            h.battery_publications(parsed(self.journal(later_telemetry=self.DISCHARGE_ROSE)))[:2], self.T,
            discharge_out=(rows := []), smc_covered=True)
        self.assertEqual([], rows)
        ((code, observed, _interval),) = flags
        self.assertEqual("battery.accumulator_unavailable", code)
        (row,) = observed["intervals"]
        self.assertEqual((40, 5400.0), (row["sign_inconsistent"]["ticks"], row["sign_inconsistent"]["mean_per_tick"]))
        catalog = json.loads((FIXTURES / "flag_catalog.json").read_text())
        self.assertEqual("DISCLOSE", catalog["codes"][code]["effect"])


class L1JournalFormatTests(unittest.TestCase):
    """Review F1: the harvest reads the journals L1's monitor writes.

    ``tests/fixtures/b5_harvest/l1_monitor`` was written by L1's own
    ``joulewise.hazards.monitor.Monitor`` under L1's FakeMac (see its
    generator).  Before this fix the harvest parsed 0 of its readings and
    every member came out battery/thermal/contention.unmeasured.
    """

    T = REGISTERED_HARVEST_THRESHOLDS

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
                   "contention.request_overlap", "contention.unmeasured", "clock.step_overlap", "clock.unmeasured",
                   "battery.assist"}
        for name, case in sorted(self.expected["cases"].items()):
            with self.subTest(name):
                span = case["span"]["monotonic_ns"]
                request = (case["request"] or case["span"])["monotonic_ns"]
                # The recorded excursion is the -447 mA discharge (publication 3): L1's
                # recorded join named it battery.member_span; under the battery-assist
                # ruling (2026-10-06) the harvest discloses it as battery.assist.
                expected = {"battery.assist" if code == "battery.member_span" else code for code in case["l1_codes"]}
                if name == "contention_burst":
                    # L1's in-force rule also takes the first publication after
                    # the span; that -447 mA snapshot was taken 35 s after the
                    # span ended, so it is no evidence about the span's current
                    # and assists nothing in it (review F3).
                    expected.discard("battery.assist")
                self.assertEqual(self.l5_codes(span, request) & physics, expected & physics)
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
                # The recorded journals predate the 1 s SMC read: L1 discloses its
                # registry fallback (battery.smc_unavailable) on every span.
                live = {finding["code"] for finding in monitor.member_findings(
                    journals, span=case["span"], request=case["request"])} - {"battery.smc_unavailable"}
                # The recorded excursion is the -447 mA discharge (publication 3): the
                # recorded join named it battery.member_span; under the battery-assist
                # ruling (2026-10-06) L1 discloses it as battery.assist.  For
                # contention_burst the recorded member_span came only from that
                # publication 35 s after the span's stop (the old in-force rule); a
                # snapshot taken after the stop measured a later member (P3-HAZ review
                # F3, the harvest copy's rule), so it is not this member's assist.
                after_stop_only = name == "contention_burst"
                expected = sorted({"battery.assist" if code == "battery.member_span" else code
                                   for code in case["l1_codes"]
                                   if not (after_stop_only and code == "battery.member_span")})
                self.assertEqual(sorted(live), expected)


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
        # 19 corpus and reference members plus the 7 reference spares (NEG-8 ruling 2026-10-07).
        self.assertEqual(sum(row["kind"] == "auxiliary" for row in roster["members"]), 26)
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
        # The p42 cells are not target cells (registration 6.6): they read the
        # decode members' prefill, which is no member's target phase.
        self.assertEqual(document["cells"], [{"cell_id": family, "target": "p42" not in family,
                                              "strata": ["quad", "repeat"]} for family in families])
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
        # auxiliaries feed no cell: 19 corpus and reference members plus the 7 spares (NEG-8 ruling 2026-10-07)
        self.assertEqual(sum(not member["units"] for member in document["members"]), 26)
        (first, *_rest) = spans.values()
        self.assertEqual(set(first), {"monotonic_ns", "request_monotonic_ns", "stage_id", "bundle_id"})
        self.assertEqual((document["plan_id"], document["attempt"], document["chain_started_monotonic_ns"]),
                         ("plan", 1, 50 * NS))
        self.assertEqual(len(document["bundles"]), 126)  # this fixture gives every roster member, spares too, a bundle

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

    def test_declared_sealed_roots_never_widen_the_executed_roots(self):
        """The real seal lists every pack and the catalog; the window inventories only its own (fx-flags 14 Q2).

        Declared roots covering all three packs must not make another pack's
        sealed file missing here, while a sealed file under the window's own
        roots that the window did not execute still differs.  Declared roots
        narrower than the window's never hide a file both inventories list
        with different bytes (the collector's ``changed`` rule).
        """
        other_pack = "configs/campaigns/b5test_other_v5"
        declared = ["joulewise", "scripts", f"configs/campaigns/{PACK_ID}", other_pack,
                    "configs/campaigns/v5_claim_25g83/flag_catalog.json"]
        for name, roots, extra, executed, want in (
                ("other_pack", declared, {f"{other_pack}/01_abs/b5t-other-r01.json": "0" * 64}, {}, []),
                ("own_root", declared, {"joulewise/b5t_sealed_not_executed.py": "1" * 64}, {},
                 ["joulewise/b5t_sealed_not_executed.py"]),
                ("narrow_declared", ["joulewise"], {}, {"scripts/b5t_stub.py": "2" * 64},
                 ["scripts/b5t_stub.py"])):
            with self.subTest(name):
                window = Window(self.tmp / f"declared-{name}", catalog_overrides=self.ISOLATE,
                                executed_overrides={"files": executed})
                sealed = window.measurement / "configs/campaigns/v5_claim_25g83/sealed_inventory.json"
                value = json.loads(sealed.read_bytes())
                value["roots"] = roots
                value["files"].update(extra)
                put(sealed, value)
                window.harvest()
                flags = [flag for flag in window.flags() if flag["code"] == "code.executed_differs_from_sealed"]
                paths = [row.get("path") for flag in flags for row in flag["observed"]["differences"]]
                self.assertEqual(paths, want)
                self.assertNotIn("code.identity_unmeasured", window.codes())


@unittest.skipUnless((B3W1 / "harvest.json").is_file(), "block-3 b3w1 archive is local to the measurement Mac")
class RehearsalRound1Tests(WindowTestCase):
    """The breaks the block-5 end-to-end rehearsal (round 1, 2026-10-06) found, each through the real harvest."""

    GAMMA = ROOT / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"

    def collect(self, window, stage, *extra):
        """L4's record-only collectors, run for real by scripts/collect_window_flags.py into the custody."""
        completed = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts/collect_window_flags.py"), "--stage", stage,
             "--custody", str(window.custody), "--repo", str(window.measurement), "--pack", str(window.pack),
             "--plan-id", PLAN_ID, "--attempt", "1", "--h-claim", H_CLAIM,
             "--catalog", str(window.measurement / SEALED_DIR / "flag_catalog.json"), *extra],
            capture_output=True, text=True, check=False, timeout=900)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads(completed.stdout.splitlines()[-1])

    def test_b2_collector_run_records_are_folded_not_malformed_flags(self):
        """B2: collector_runs.jsonl is a run log, not a flag file.

        Before the fix every one of its lines became records.malformed_flag
        (never classified, so release_blocked on every window) and the
        collectors' own errors never reached window_flags.json.
        """
        window = self.window()
        self.collect(window, "desk")
        arm = self.collect(window, "arm", "--timeout-s", "0.001")  # every arm collector times out
        self.assertTrue(arm["collectors"])
        self.assertEqual({row["status"] for row in arm["collectors"].values()}, {"timeout"})
        runs = [json.loads(line) for line in
                (window.custody / "flags" / "collector_runs.jsonl").read_text().splitlines() if line.strip()]
        self.assertEqual([row["stage"] for row in runs], ["desk", "arm"])
        not_ok = {(row["stage"], f"{row['stage']}.{item['collector']}") for row in runs
                  for item in row["collectors"] if item["status"] != "ok"}
        self.assertTrue({stage for stage, _name in not_ok} >= {"arm"})
        # The driver's own record of the arm call: the subprocess as a whole.
        put(window.custody / "night" / "arm_collectors.json",
            {"schema": "joulewise.b5_arm_collectors.v1", "call": 1, "ran_by": "driver",
             "collector_error": "timed out", "argv": ["collect_window_flags.py"]})
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        self.assertNotIn("records.malformed_flag", window.codes())
        summary = window.window_flags()
        self.assertNotIn("records.malformed_flag", summary["flags"]["unclassified"])
        folded = {(row["stage"], row["collector"]) for row in summary["collector_errors"] if "stage" in row}
        self.assertEqual(folded, not_ok | {("arm", "arm.flags.arm")})
        for row in summary["collector_errors"]:
            if "stage" in row:
                self.assertTrue(row["source"].startswith(("flags/collector_runs.jsonl:", "night/arm_collectors")))
        # Not harvest faults: the collectors are records.
        self.assertEqual(record["faults"], [])
        # Every flag the collectors wrote reached the window's flags, with its writer's id,
        # or was superseded by the harvest's own complete re-derivation (PLAN2 row 12),
        # which records the superseded flag's id.
        written = [json.loads(line) for name in ("desk.jsonl", "arm.jsonl")
                   for line in (window.custody / "flags" / name).read_text().splitlines() if line.strip()]
        self.assertTrue(written)
        superseded = {flag["observed"]["superseded_flag_id"] for flag in window.flags()
                      if flag["code"] == "records.identity_unmeasured_superseded"}
        self.assertTrue({flag["flag_id"] for flag in written}
                        <= {flag["flag_id"] for flag in window.flags()} | superseded)
        failed = {(flag["observed"]["stage"], flag["observed"]["collector"]) for flag in window.flags()
                  if flag["code"] == "records.collector_failed" and "stage" in flag["observed"]}
        self.assertEqual({f"{stage}.{name}" for stage, name in failed}, {name for _stage, name in folded})

    def test_b2_an_arm_run_collector_call_is_folded_once(self):
        """The arm ran the collectors (ran_by arm): its results fold once, not again as the joined error."""
        window = self.window()
        put(window.custody / "night" / "arm_collectors.json",
            {"schema": "joulewise.b5_arm_collectors.v1", "call": 1, "ran_by": "arm", "collector_error": "timed out",
             "results": [{"name": "flags.arm", "timed_out": True, "returncode": None, "error": None,
                          "elapsed_s": 120.0}]})
        window.harvest()
        folded = [row for row in window.window_flags()["collector_errors"] if "stage" in row]
        self.assertEqual([(row["collector"], row["status"], row["error"], row["source"]) for row in folded],
                         [("arm.flags.arm", "timeout", "timed out", "night/arm_collectors.json")])

    def add_duplicate_dispatch(self, window):
        """GAMMA's shape: one external input (one run id) launched by two stages into the claim root."""
        tree = json.loads((window.pack / "plan_tree.json").read_bytes())
        member = {"path": f"configs/campaigns/{PACK_ID}/01_abs/b5t-abs-r01.json", "run_id": "b5t-ref-midpoint",
                  "sha256": "1" * 64}
        tree["external_inputs"]["manifests"] = [{"input_id": "midpoint_reference", "members": [member]}]

        def stage(stage_id, ordinal):
            return {"stage_id": stage_id, "ordinal": ordinal, "kind": "campaign_collection", "expected_count": 1,
                    "input_ref": {"kind": "external_input", "input_id": "midpoint_reference"},
                    "launch": {"schema_version": "joulewise.stage_launch.v1", "commands": [{
                        "command_id": f"{stage_id}.collect", "command_kind": "campaign_collection",
                        "argv_template": {"tool_id": "campaign_runner",
                                          "interface_id": "joulewise.run_campaign.cli.v1",
                                          "arguments": [{"kind": "repo_path", "value": "configs/x/midpoint"},
                                                        {"kind": "literal", "value": "--runs-dir"},
                                                        {"kind": "binding", "value": "claim_runs_root"}]}}]}}
        tree["stage_graph"] += [stage("b5t-reference-decode-midpoint", 2), stage("b5t-reference-arm-boundary", 3)]
        put(window.pack / "plan_tree.json", tree)
        (window.pack / "plan_tree.sha256").write_text(f"{sha(window.pack / 'plan_tree.json')}  plan_tree.json\n")

    def test_b3_a_run_id_launched_twice_is_recorded_not_silently_collapsed(self):
        """B3: GAMMA's interior references are one run id launched by three stages.

        Before the fix the roster collapsed them into one member and the
        harvest said nothing about the two positions never measured.
        """
        window = self.window()
        self.add_duplicate_dispatch(window)
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        (flag,) = [flag for flag in window.flags() if flag["code"] == "roster.duplicate_run_id"]
        self.assertEqual(flag["scope"]["level"], "window")
        self.assertEqual(flag["observed"]["run_id"], "b5t-ref-midpoint")
        self.assertEqual(flag["observed"]["dispatch_count"], 2)
        self.assertEqual(flag["observed"]["stages"], ["b5t-reference-decode-midpoint", "b5t-reference-arm-boundary"])
        self.assertEqual(flag["observed"]["runs_roots"], ["claim_runs_root"])
        self.assertIn("roster.duplicate_run_id", window.exclusions()["reasons"])  # the test catalog's draft effect
        self.assertEqual(h.flag_problems(flag), [])

    def test_b3_the_committed_gamma_pack_launches_each_run_id_once(self):
        tree = json.loads((self.GAMMA / "plan_tree.json").read_bytes())
        dispatches, unresolved = h.stage_dispatches(tree, self.GAMMA)
        self.assertEqual(unresolved, [])
        duplicated = {run_id: [row["stage_id"] for row in rows] for run_id, rows in dispatches.items() if len(rows) > 1}
        # Lane L10 (GAMMA-INTERIOR-REFERENCES-01): the three interior references launch distinct run ids.
        self.assertEqual(duplicated, {})
        self.assertEqual({run_id: rows[0]["stage_id"] for run_id, rows in dispatches.items()
                          if rows[0]["stage_id"] in {"gamma-reference-decode-midpoint", "gamma-reference-arm-boundary",
                                                     "gamma-reference-prefill-midpoint"}},
                         {"gamma-interior-reference-decode-midpoint": "gamma-reference-decode-midpoint",
                          "neg8-window-midpoint": "gamma-reference-arm-boundary",
                          "gamma-interior-reference-prefill-midpoint": "gamma-reference-prefill-midpoint"})
        self.assertEqual(sum(len(rows) for rows in dispatches.values()), 101)
        roster = h.build_roster(self.GAMMA, ROOT)
        self.assertEqual(len(roster["members"]), 108)  # 101 launched by stages + 7 reference spares
        self.assertEqual(roster["duplicate_listings"], {})

    def test_b6_untagged_auxiliary_bundles_are_not_lineage_findings(self):
        """B6: only marker-bearing members carry a lineage stamp.

        Before the fix every untagged member (NEG-8 corpus, window references;
        here the untagged seed members) gave lineage.bundle_stamp_absent.
        """
        window = self.window()
        published = LineageFindingTests.publish(None, window)
        tagged = ("b5t-cmp-b01-a1", "b5t-cmp-b01-b1")
        for run_id in tagged:
            bundle = window.claim / run_id
            config = json.loads((bundle / "config.json").read_bytes())
            config["run_metadata"]["tags"].append("launch_lineage_required")
            (bundle / "config.json").write_bytes(normalized_config(config))
        stamped = window.claim / tagged[0]
        metadata = json.loads((stamped / "metadata.json").read_bytes())
        metadata.setdefault("extra", {})["launch_lineage"] = published["launch_lineage"]
        metadata["extra"]["launch_lineage_locator_sha256"] = published["locators"]["claim_runs_root"]["sha256"]
        put(stamped / "metadata.json", metadata)
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        absent = {flag["scope"]["run_id"] for flag in window.flags() if flag["code"] == "lineage.bundle_stamp_absent"}
        self.assertEqual(absent, {tagged[1]})
        self.assertFalse({flag["code"] for flag in window.flags()
                          if flag["scope"].get("run_id") == tagged[0] and flag["code"].startswith("lineage.")})

    def test_b7_a_member_that_never_reached_the_sampler_is_placed_by_its_own_stamps(self):
        """B7: an admission-aborted member has no sampler stamps.

        Before the fix its creation stamp was None, L4 labelled it
        roster.before_chain_started (it was not early) and counted
        member.bytes_missing; every bundle also went to L4 with attempt None.
        """
        window = self.window()
        plan = json.loads(window.plan_path.read_bytes())
        plan["hazard_window"]["runs_roots"] = {"claim": str(window.claim), "bound": str(window.bound)}
        put(window.plan_path, plan)
        aborted, bare = window.claim / "b5t-abs-r01", window.claim / "b5t-abs-r02"
        for bundle in (aborted, bare):
            metadata = json.loads((bundle / "metadata.json").read_bytes())
            del metadata["uncertainty_evidence"]["clock_anchor"]["clock_stamps"]
            metadata["environment_admission"] = {"decision": "abort", "failure": "admission"}
            put(bundle / "metadata.json", metadata)
        lines = (bare / "events.jsonl").read_text().splitlines()
        (bare / "events.jsonl").write_text("".join(line + "\n" for line in lines
                                                   if json.loads(line)["event_type"] != "run_started"))
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        exclusions = window.exclusions()
        ignored = {(row["run_id"], row["code"]) for row in exclusions.get("bundles_ignored", [])}
        self.assertNotIn(("b5t-abs-r01", "roster.before_chain_started"), ignored)
        inputs = json.loads((window.archive / "withheld" / "exclusion-inputs.json").read_bytes())
        bundles = {row["run_id"]: row for row in inputs["roster"]["bundles"]}
        self.assertEqual(bundles["b5t-abs-r01"]["created_source"], "run_started_wall_via_chain_started")
        self.assertGreater(bundles["b5t-abs-r01"]["created_monotonic_ns"], CHAIN_STARTED_NS)
        self.assertEqual(bundles["b5t-abs-r02"]["created_monotonic_ns"], None)
        self.assertEqual({row["attempt"] for row in bundles.values()}, {1})
        if L4_AVAILABLE:
            self.assertIn(("b5t-abs-r02", "roster.creation_unplaced"), ignored)
            excluded = {row["run_id"]: row["codes"] for row in exclusions["members_excluded"]}
            self.assertNotIn("member.bytes_missing", excluded.get("b5t-abs-r01", []))
            self.assertIn("member.bytes_missing", excluded["b5t-abs-r02"])

    def test_b8_a_non_target_phase_precheck_excludes_nothing(self):
        """B8: the p42 cells read the decode members' prefill, which is no member's target phase.

        Before the fix the p42 precheck failure (insufficient_in_window_samples,
        expected on every member, registration 0.5) removed each decode member
        from its decode cell too, and the p42 cells counted toward the minimum.
        """
        overrides = {**self.ISOLATE, "instrument.cadence_ratio_below_threshold": "DISCLOSE",
                     "member.target_phase_precheck_failed": "DISCLOSE"}
        window = self.window(target_precheck=["phase", "decode"], p42_precheck=["phase", "prefill"],
                             catalog_overrides=overrides)
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        targets = {flag["observed"].get("target") for flag in window.flags()
                   if flag["code"].startswith("instrument.") or flag["code"] == "member.target_phase_precheck_failed"}
        self.assertEqual(targets, {"phase/decode"})
        self.assertNotIn("instrument.insufficient_in_window_samples", window.codes())  # only the prefill fails it
        exclusions = window.exclusions()
        self.assertEqual(exclusions["members_excluded"], [])
        roster = json.loads((window.archive / "derived" / "roster.json").read_bytes())
        self.assertEqual([(cell["cell_id"], cell["target"]) for cell in roster["cells"]],
                         [(FAMILY, True), (P42_FAMILY, False)])
        self.assertNotIn("cell.below_minimum", exclusions["reasons"])
        cells = {cell["cell_id"]: cell for cell in exclusions["cells"]}
        self.assertEqual((cells[FAMILY]["n_repeats"], cells[FAMILY]["n_quads"]), (2, 1))
        # The p42 precheck outcome is still disclosed, in the s1-structural precheck counts.
        counts = next(flag for flag in window.flags() if flag["code"] == "diagnostic.s1_structural"
                      and flag["observed"]["check"] == "precheck_counts")
        self.assertEqual(counts["observed"]["b5t-p42-abs:ineligible"], 2)

    def test_b8_the_real_floor_packs_mark_only_p42_cells_non_target(self):
        for pack, model in (("d117_floor_qwen3-1p7b_v5", "qwen3-1p7b"), ("d117_floor_qwen3-8b_v5", "qwen3-8b")):
            roster = h.build_roster(ROOT / "configs/campaigns" / pack, ROOT)
            targets = {cell["condition_family_id"]: cell["target"] for cell in roster["cells"]}
            self.assertEqual(targets, {f"df-ph-decode-{model}": True, f"df-ph-prefill-p2048-{model}": True,
                                       f"df-ph-prefill-p42-{model}": False}, pack)
        gamma = h.build_roster(self.GAMMA, ROOT)
        self.assertTrue(all(cell["target"] for cell in gamma["cells"]))

    def test_b4_g3_runs_in_full_window_mode_for_a_hazard_pack_window(self):
        """B4: G3's default roster is G2-b's one shakedown block; a claim window holds the whole pack."""
        window = Window(self.tmp / "g3", prefix_ledger=True, catalog_overrides=self.ISOLATE)
        (window.pack / "analysis_manifest_v3.json").write_text("{}\n")
        (window.claim / "whole-window-verdict.json").write_text("{}\n")
        (window.claim / "bracket-binding.json").write_text("{}\n")
        calls = []

        def runner(argv, **kwargs):
            calls.append(list(argv))
            Path(argv[argv.index("--report-json") + 1]).write_text(json.dumps({"assertions": []}))
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        window.harvest(seams=h.Seams(group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS, runner=runner))
        (argv,) = [argv for argv in calls if "--report-json" in argv]
        self.assertIn("--full-window", argv)
        self.assertEqual(argv[argv.index("--plan-tree") + 1], str(window.pack / "plan_tree.json"))
        self.assertEqual(argv[argv.index("--repo-root") + 1], str(window.measurement))


# ---------------------------------------------------------------------------
# Gate-prune core prune, lane NONCORE (night-archive core-prune DESIGN.md 3.4).
# ---------------------------------------------------------------------------

class RunnerPopen:
    """A desk verdict child that has already finished: ``runner`` runs at spawn.

    The harvest spawns the desk writer with ``Seams.desk_popen`` in its own
    session and supervises it (``DeskVerdictChild``); this stands in for a
    writer that exits at once, writing ``runner``'s output to the harvest's
    capture files.
    """

    def __init__(self, runner, argv, **kwargs):
        assert kwargs.get("start_new_session") is True, kwargs
        result = runner(argv, **kwargs)
        for name in ("stdout", "stderr"):
            handle, text = kwargs.get(name), getattr(result, name, "") or ""
            if hasattr(handle, "write"):
                handle.write(text.encode("utf-8"))
        self.returncode, self.pid = result.returncode, -1

    def wait(self, timeout=None):
        return self.returncode

    def poll(self):
        return self.returncode


def desk_popen(runner):
    return lambda argv, **kwargs: RunnerPopen(runner, argv, **kwargs)


def desk_seams(desk_runner, **extra):
    return h.Seams(group_alive=lambda pgid: False, exclusions_compute=EXCLUSIONS,
                   desk_popen=desk_popen(desk_runner), **extra)


def commit_checkout(window: "Window") -> None:
    """Make the fixture's measurement checkout a git checkout with its pin committed (as H_claim has it)."""
    from tests.git_fixture import init_git_fixture
    git = ["git", "-C", str(window.measurement)]
    if (window.measurement / ".git").exists():
        return
    init_git_fixture(window.measurement, "-q")  # the shared helper: no detached auto-maintenance
    for key, value in (("user.name", "fixture"), ("user.email", "fixture@example.invalid"),
                       ("commit.gpgsign", "false")):
        subprocess.run([*git, "config", "--local", key, value], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture measurement checkout"], check=True)


def advance_pin(window: "Window", *, commit: bool = True) -> dict:
    """The real desk pin advance between chain exit and harvest (registration 11), on the fixture checkout."""
    from joulewise.b5 import plan as b5_plan
    commit_checkout(window)
    return b5_plan.advance_ledger_pin(window.measurement, session_id=SESSION_ID, operator_identity="test",
                                      attestation_reason="test", commit=commit)


class CampaignLockAllowlistTests(WindowTestCase):
    """N4 (sweep V3, harvest half): the producer's own lock is campaign.lock, not .campaign.lock."""

    def test_a_stale_lock_the_producer_clears_is_not_a_source_change(self):
        window = self.window(prefix_ledger=True)
        advance_pin(window)
        (window.claim / "campaign.lock").write_text('pid=999999 start_time="stale"\n')

        def runner(argv, **kwargs):
            runs = Path(argv[argv.index("--runs-dir") + 1])
            (runs / "campaign.lock").unlink()  # the producer reclaims its stale lock (core-prune A9/V3)
            (runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
            (runs / "campaign_log.jsonl").write_text('{"status":"failed"}\n')
            return SimpleNamespace(returncode=1, stdout="", stderr="")

        window.harvest(seams=desk_seams(runner), prepare_desk=True, run_g3=False)
        self.assertNotIn("records.source_changed_during_harvest", window.codes())
        self.assertFalse((window.claim / "campaign.lock").exists())

    def test_any_other_change_is_still_a_source_change(self):
        window = self.window(prefix_ledger=True)
        advance_pin(window)

        def runner(argv, **kwargs):
            runs = Path(argv[argv.index("--runs-dir") + 1])
            (runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
            (runs / ".campaign.lock").write_text("not the producer's lock\n")
            return SimpleNamespace(returncode=1, stdout="", stderr="")

        window.harvest(seams=desk_seams(runner), prepare_desk=True, run_g3=False)
        flag = next(flag for flag in window.flags() if flag["code"] == "records.source_changed_during_harvest")
        self.assertEqual(flag["observed"]["changed"], [".campaign.lock"])


class WholeWindowMemberFailureTests(WindowTestCase):
    """Registration 6.3 and 2: each member the whole-window verdict fails, for a reason no other
    member code carries, is removed by ``member.whole_window_member_failure`` (EXCLUDE_MEMBER).

    Those reasons are the verdict's ``member_failures`` reason codes
    (``whole_window.PROSPECTIVE_MEMBER_FAILURE_REASON_CODES``) except in-window
    thermal pressure (``thermal.powermetrics_pressure_elevated``) and an invalid
    bundle (``member.strict_validation_failed`` and its kin).  The environment
    reasons carry D-078 item 4's display-asleep and screensaver-off observation.
    """

    CODE = "member.whole_window_member_failure"

    def write(self, window, status, failures):
        put(window.claim / "whole-window-verdict.json", {
            "status": status, "bundle_ids": sorted(row[0] for row in MEMBERS),
            "idle_admission_core": {"conditions": sorted({reason for _member, reason, _detail in failures})},
            "member_failures": [{"member_id": member, "reason_code": reason, "detail": detail}
                                for member, reason, detail in sorted(failures)]})

    def test_the_reasons_are_the_verdicts_less_the_two_with_their_own_codes(self):
        from joulewise.flags.catalog import DRAFT_CODES
        self.assertEqual(set(h.WHOLE_WINDOW_MEMBER_FAILURE_REASONS),
                         set(whole_window.PROSPECTIVE_MEMBER_FAILURE_REASON_CODES)
                         - {"thermal_pressure_elevated_in_window", "whole_window_bundle_invalid"})
        self.assertEqual(11, len(h.WHOLE_WINDOW_MEMBER_FAILURE_REASONS))
        fixture = json.loads((FIXTURES / "flag_catalog.json").read_bytes())["codes"]
        self.assertEqual("EXCLUDE_MEMBER", fixture[self.CODE]["effect"])
        self.assertEqual("EXCLUDE_MEMBER", DRAFT_CODES[self.CODE]["effect"])
        self.assertEqual(("MEMBER_VALIDITY", "NUMBER"), (h.CODES[self.CODE].family, h.CODES[self.CODE].klass))

    def test_each_member_the_verdict_fails_is_removed_once_with_its_reasons(self):
        """Before: nothing emitted the code, so a member whose display woke in its request was kept."""
        window = self.window()
        self.write(window, "failed", [
            ("b5t-abs-r01", "environment_admission_failed", "display awake during the request"),
            ("b5t-abs-r02", "cpu_busy_ratio_p95_exceeded", "cpu busy p95 0.31 > 0.25"),
            ("b5t-abs-r02", "gpu_idle_admission_not_passed", "gpu idle admission not passed"),
            # Reasons with their own member codes: not this code.
            ("b5t-cmp-b01-a1", "thermal_pressure_elevated_in_window", "thermal pressure elevated"),
            ("b5t-cmp-b01-b1", "whole_window_bundle_invalid", "bundle invalid"),
        ])
        window.harvest()
        found = {flag["scope"]["run_id"]: flag for flag in window.flags() if flag["code"] == self.CODE}
        self.assertEqual({"b5t-abs-r01", "b5t-abs-r02"}, set(found))
        self.assertEqual(["environment_admission_failed"], found["b5t-abs-r01"]["observed"]["reasons"])
        self.assertEqual(["cpu_busy_ratio_p95_exceeded", "gpu_idle_admission_not_passed"],
                         found["b5t-abs-r02"]["observed"]["reasons"])
        self.assertEqual("member", found["b5t-abs-r01"]["scope"]["level"])
        self.assertEqual("display awake during the request", found["b5t-abs-r01"]["observed"]["details"][0])
        excluded = {row["run_id"]: row["codes"] for row in window.exclusions()["members_excluded"]}
        self.assertIn(self.CODE, excluded["b5t-abs-r01"])
        self.assertIn(self.CODE, excluded["b5t-abs-r02"])
        self.assertNotIn(self.CODE, excluded.get("b5t-cmp-b01-a1", []))
        self.assertIn("whole_window.not_passed", window.codes())
        self.assertNotIn("whole_window.not_passed", window.exclusions()["reasons"])

    def test_a_passed_verdict_with_no_member_failures_removes_nobody(self):
        window = self.window()
        self.write(window, "passed", [])
        window.harvest()
        self.assertNotIn(self.CODE, window.codes())

    def test_a_malformed_member_failure_list_is_recorded_not_guessed(self):
        window = self.window()
        put(window.claim / "whole-window-verdict.json", {
            "status": "failed", "bundle_ids": sorted(row[0] for row in MEMBERS), "idle_admission_core": {},
            "member_failures": [{"member_id": "b5t-abs-r01", "reason_code": "not_a_registered_reason",
                                 "detail": "x"}]})
        window.harvest()
        self.assertNotIn(self.CODE, window.codes())
        (flag,) = [flag for flag in window.flags() if flag["code"] == "whole_window.not_passed"]
        self.assertEqual("malformed", flag["observed"]["member_failures"])
        # P4: no failed member can be named, so the per-member exclusion cannot be
        # applied; the window is excluded (it was only disclosed before).
        (flag,) = [flag for flag in window.flags() if flag["code"] == "whole_window.member_failures_unreadable"]
        self.assertEqual(("failed", "malformed"), (flag["observed"]["status"], flag["observed"]["member_failures"]))
        self.assertIn("whole_window.member_failures_unreadable", window.exclusions()["reasons"])

    def test_p4_a_failed_verdict_without_member_failures_excludes_the_window(self):
        window = self.window()
        put(window.claim / "whole-window-verdict.json", {
            "status": "failed", "bundle_ids": sorted(row[0] for row in MEMBERS),
            "idle_admission_core": {"conditions": ["environment_admission_failed"]}})
        window.harvest()
        (flag,) = [flag for flag in window.flags() if flag["code"] == "whole_window.member_failures_unreadable"]
        self.assertEqual("absent", flag["observed"]["member_failures"])
        self.assertIn("whole_window.member_failures_unreadable", window.exclusions()["reasons"])
        self.assertEqual("EXCLUDE_WINDOW", h.Catalog.load(FIXTURES / "flag_catalog.json").effect(
            "whole_window.member_failures_unreadable"))

    def test_p4_a_listed_or_passed_verdict_keeps_the_window(self):
        for status, failures in (("failed", [("b5t-abs-r01", "environment_admission_failed", "display awake")]),
                                 ("failed", []), ("passed", [])):
            with self.subTest(status=status, failures=len(failures)):
                window = Window(self.tmp / f"p4-{status}-{len(failures)}", catalog_overrides=self.ISOLATE)
                self.write(window, status, failures)
                window.harvest()
                self.assertNotIn("whole_window.member_failures_unreadable", window.codes())


class FixtureCatalogTests(WindowTestCase):
    """N5 (sweep V4): whole_window.not_passed is disclosed, as in the draft catalog (revision 3)."""

    def test_the_fixture_effect_equals_the_draft(self):
        from joulewise.flags.catalog import DRAFT_CODES
        fixture = json.loads((FIXTURES / "flag_catalog.json").read_bytes())["codes"]
        self.assertEqual(fixture["whole_window.not_passed"]["effect"], DRAFT_CODES["whole_window.not_passed"]["effect"])
        self.assertEqual(fixture["whole_window.not_passed"]["effect"], "DISCLOSE")

    def test_a_failed_aggregate_verdict_does_not_remove_the_window_by_itself(self):
        window = self.window()  # the fixture catalog as committed (no override of this code)
        write_verdict(window, status="failed", decision="passed", member_conditions=["member_failed"])
        window.harvest()
        self.assertIn("whole_window.not_passed", window.codes())
        self.assertNotIn("whole_window.not_passed", window.exclusions()["reasons"])


class CaptureBatteryTests(WindowTestCase):
    """N7: the calibration captures' battery, from the continuous journal and the raw-file custody."""

    T = REGISTERED_HARVEST_THRESHOLDS

    def join(self, assessments, readings, thresholds=None):
        emitted, errors = [], []
        fake = SimpleNamespace(capture_assessments=assessments,
                               emit=lambda code, **kwargs: emitted.append((code, kwargs)),
                               _record_error=lambda name, exc, elapsed, fault: errors.append((name, fault)))
        h._Harvest._capture_battery_joins(fake, readings, thresholds or self.T)
        return emitted, errors

    @staticmethod
    def capture(pair, span):
        return {"pre-attempt": {"slot": "pre", "battery_pair": pair, "span": span}}

    def test_discharge_alone_over_the_capture_is_disclosed(self):
        """Battery-assist ruling item 4: a discharge-only excursion over a capture is never an exclusion."""
        readings = battery_journal([(0, {}), (60, {"instant_amperage_ma": -447}), (120, {}), (180, {})])
        span = [publication_ns(70), publication_ns(100)]
        for pair in ("pass", "battery_float_evidence_missing"):
            with self.subTest(pair=pair):
                emitted, errors = self.join(self.capture(pair, span), readings)
                self.assertEqual([code for code, _ in emitted], ["calibration.capture_battery_assist"])
                self.assertTrue(emitted[0][1]["observed"]["request_assist"])
                self.assertEqual(errors, [])

    def test_out_of_float_over_the_capture_removes_the_window(self):
        readings = battery_journal([(0, {}), (60, {"instant_amperage_ma": 447}), (120, {}), (180, {})])
        span = [publication_ns(70), publication_ns(100)]
        for pair in ("pass", "battery_float_evidence_missing"):
            with self.subTest(pair=pair):
                emitted, errors = self.join(self.capture(pair, span), readings)
                self.assertEqual([code for code, _ in emitted], ["calibration.capture_battery_span"])
                (code, kwargs), = emitted
                self.assertEqual((kwargs["level"], kwargs["observed"]["capture"], kwargs["interval"]),
                                 ("window", "pre-attempt", {"monotonic_ns": span}))
                self.assertIn("battery.member_span", kwargs["observed"]["codes"])
                self.assertEqual(errors, [])

    def test_a_pair_that_did_not_pass_without_journal_coverage_removes_the_window(self):
        gap = battery_journal([(0, {}), (200, {}), (260, {})], end_s=300)
        covered = battery_journal([(0, {}), (60, {}), (120, {}), (180, {})])
        span = [publication_ns(100), publication_ns(110)]
        cases = {"journal_gap": (gap, span), "capture_span_unknown": (covered, None),
                 "battery_journal_absent": (None, span)}
        for reason, (readings, capture_span) in cases.items():
            with self.subTest(reason):
                emitted, _errors = self.join(self.capture("battery_float_evidence_missing", capture_span), readings)
                self.assertEqual([code for code, _ in emitted], ["calibration.capture_battery_unmeasured"])
                self.assertEqual(emitted[0][1]["observed"]["reason"], reason)
        # The same holes with a verified pair: the pair measured the capture, nothing is emitted.
        for reason, (readings, capture_span) in cases.items():
            with self.subTest(pair="pass", case=reason):
                self.assertEqual(self.join(self.capture("pass", capture_span), readings)[0], [])

    def test_a_covering_journal_in_float_needs_no_pair(self):
        readings = battery_journal([(0, {}), (60, {}), (120, {}), (180, {})])
        for pair in ("battery_float_evidence_missing", "error:ValueError", None):
            with self.subTest(pair=pair):
                self.assertEqual(self.join(self.capture(pair, [publication_ns(70), publication_ns(100)]),
                                           readings), ([], []))

    def test_a_join_that_cannot_run_is_a_fault_and_leaves_the_capture_unmeasured(self):
        readings = battery_journal([(0, {}), (60, {}), (120, {})])
        thresholds = {key: value for key, value in self.T.items() if key != "battery_limit_ma"}
        emitted, errors = self.join(self.capture("battery_float_evidence_missing",
                                                 [publication_ns(70), publication_ns(100)]), readings, thresholds)
        self.assertEqual(errors, [("monitor.capture_battery", True)])
        self.assertEqual([(code, kwargs["observed"]["reason"]) for code, kwargs in emitted],
                         [("calibration.capture_battery_unmeasured", "join_failed")])

    def test_a_window_whose_captures_carry_no_span_and_no_pair_is_removed(self):
        # The synthetic captures record neither a clock anchor nor a battery pair.
        window = self.window()
        window.harvest()
        flags = [flag for flag in window.flags() if flag["code"] == "calibration.capture_battery_unmeasured"]
        self.assertEqual(sorted(flag["observed"]["slot"] for flag in flags), ["post", "pre"])
        self.assertEqual({flag["observed"]["reason"] for flag in flags}, {"capture_span_unknown"})
        self.assertIn("calibration.capture_battery_unmeasured", window.exclusions()["reasons"])

    def test_a_battery_raw_file_that_changed_is_capture_invalid(self):
        window = self.window(prefix_ledger=True)
        capture = window.claim / "instrument_validation" / f"{SESSION_ID}-pre"
        (capture / "raw" / "battery_float.pre.ioreg").write_bytes(b"changed after finalization")
        put(capture / "instrument_evidence.json", {"slot": "pre", "validation_id": f"{SESSION_ID}-pre",
                                                   "battery_float": {"pre": {
                                                       "phase": "slot_pre", "raw_path": "raw/battery_float.pre.ioreg",
                                                       "raw_stdout_sha256": hashlib.sha256(b"recorded").hexdigest(),
                                                       "wall_time_s": 1786206000.0}}})
        window.harvest()
        custody = [flag for flag in window.flags() if flag["code"] == "calibration.capture_invalid"
                   and flag["observed"].get("reason") == "battery_raw_custody_failed"]
        self.assertEqual([flag["observed"]["slot"] for flag in custody], ["pre"])
        self.assertIn("calibration.capture_invalid", window.exclusions()["reasons"])


class UnwrittenCoreFlagTests(WindowTestCase):
    """N8: a core flag whose write failed is printed behind the marker; the harvest recovers it."""

    @staticmethod
    def unwritten_line(code: str, **kwargs) -> str:
        from joulewise.flags import core as flags_core
        context = flags_core.HazardFlagContext(writer="core-controller", custody_root=None, plan_id=PLAN_ID,
                                               attempt=1, scope_resolved=True)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            assert not flags_core.emit(context, code, **kwargs)
        (line,) = stderr.getvalue().splitlines()
        return line

    def test_marker_lines_in_stage_logs_reach_the_exclusions(self):
        window = self.window()
        run_id = MEMBERS[0][0]
        line = self.unwritten_line("instrument.binary_identity_unmeasured", level="member", run_id=run_id,
                                   observed={"device_metadata": "no executable_sha256"})
        torn = self.unwritten_line("teardown.survivors", level="member", run_id=MEMBERS[1][0], observed={"n": 1})
        logs = window.custody / "operator-logs"
        logs.mkdir(exist_ok=True)
        (logs / "07-b5t-science.log").write_text(
            f"stage output\n{line}\n{torn[:80]}\nnot {h.UNWRITTEN_MARKER}at line start\n")
        window.harvest()
        recovered = [flag for flag in window.flags() if flag["code"] == "instrument.binary_identity_unmeasured"]
        self.assertEqual([flag["scope"]["run_id"] for flag in recovered], [run_id])
        excluded = {row["run_id"]: row["codes"] for row in window.exclusions()["members_excluded"]}
        self.assertIn("instrument.binary_identity_unmeasured", excluded[run_id])
        malformed = [flag["observed"] for flag in window.flags() if flag["code"] == "records.malformed_flag"]
        self.assertEqual([(item["file"], item["line"]) for item in malformed],
                         [("operator-logs/07-b5t-science.log", 3)])
        # Torn one letter into its code ("t"): no EXCLUDE_WINDOW code starts with it and
        # no run id shows, so it is disclosed only and release is not blocked.
        self.assertEqual(["t"], [item["salvaged_code_prefix"] for item in malformed])
        self.assertFalse({"records.malformed_flag_exclusion_possible",
                          "records.malformed_flag_member_exclusion_possible"} & set(window.codes()))
        self.assertFalse(window.exclusions()["release_blocked"])

    def test_a_writers_unbuilt_stand_in_line_rebuilds_its_flag(self):
        """Opus audit F2 (a): the chain's own 'unbuilt' line is a designed output, not a torn flag.

        Before: it failed validation (13 missing fields), became records.malformed_flag,
        which was never classified, so release_blocked stayed True for ever and the
        member exclusion the line names was lost."""
        window = self.window()
        run_id = MEMBERS[0][0]
        chain_line = h.UNWRITTEN_MARKER + json.dumps(
            {"code": "battery.member_span", "level": "member", "observed": {"smc_ma_max": 412}, "run_id": run_id,
             "unbuilt": "flag writer exceeded its wall budget"}, sort_keys=True)
        core_line = h.UNWRITTEN_MARKER + json.dumps(
            {"code": "teardown.survivors", "level": "member", "run_id": None,
             "unbuilt": "FlagSchemaError: bad observed"}, sort_keys=True)
        logs = window.custody / "operator-logs"
        logs.mkdir(exist_ok=True)
        (logs / "07-b5t-science.log").write_text(f"stage output\n{chain_line}\n{core_line}\n")
        window.harvest()
        self.assertNotIn("records.malformed_flag", window.codes())
        rebuilt = [flag for flag in window.flags() if flag["code"] == "battery.member_span"
                   and flag["source"]["collector"] == "unbuilt_marker"]
        self.assertEqual([(run_id, "member")], [(flag["scope"]["run_id"], flag["scope"]["level"]) for flag in rebuilt])
        self.assertEqual({"smc_ma_max": 412}, rebuilt[0]["observed"]["value"])
        excluded = {row["run_id"]: row["codes"] for row in window.exclusions()["members_excluded"]}
        self.assertIn("battery.member_span", excluded[run_id])
        survivors = [flag for flag in window.flags() if flag["code"] == "teardown.survivors"]
        self.assertEqual([("window", True)], [(flag["scope"]["level"], flag["observed"]["run_id_missing"])
                                              for flag in survivors])
        unbuilt = sorted(flag["observed"]["code"] for flag in window.flags() if flag["code"] == "records.flag_unbuilt")
        self.assertEqual(["battery.member_span", "teardown.survivors"], unbuilt)
        self.assertFalse(window.exclusions()["release_blocked"])

    def test_a_torn_flag_line_is_disclosed_or_excluded_by_what_it_still_shows(self):
        """Opus audit F2 (c): a torn line never blocks release; a recoverable exclusion code still excludes."""
        run_id = MEMBERS[1][0]
        full_window = self.unwritten_line("calibration.capture_invalid", level="window", observed={"slot": "post"})
        full_member = self.unwritten_line("battery.member_span", level="member", run_id=run_id,
                                          observed={"smc_ma_max": 412})
        cases = {
            # torn inside the code: the prefix "calibration.capt" could be calibration.capture_invalid
            "window_prefix": (full_window[:full_window.index('"calibration.capt') + len('"calibration.capt')],
                              "records.malformed_flag_exclusion_possible", "window", None),
            # torn after the run id: battery.member_span is EXCLUDE_MEMBER and names its member
            "member_whole": (full_member[:full_member.index(run_id, full_member.index('"run_id"')) + len(run_id) + 1],
                             "records.malformed_flag_member_exclusion_possible", "member", run_id),
            # torn before the code: nothing recoverable, disclosed only
            "no_code": (full_member[:60], None, None, None),
            # a member code but torn before the run id: disclosed only
            "member_unplaced": (full_member[:full_member.index('"battery.member_span"') + 22], None, None, None),
        }
        for label, (torn, extra, level, scoped) in cases.items():
            with self.subTest(label):
                window = Window(self.tmp / f"torn-{label}", catalog_overrides=self.ISOLATE)
                logs = window.custody / "operator-logs"
                logs.mkdir(exist_ok=True)
                (logs / "07-b5t-science.log").write_text(f"stage output\n{torn}\n")
                window.harvest()
                self.assertIn("records.malformed_flag", window.codes())
                exclusions = window.exclusions()
                self.assertFalse(exclusions["release_blocked"])
                self.assertEqual([], exclusions["unclassified"])
                if extra is None:
                    self.assertFalse({"records.malformed_flag_exclusion_possible",
                                      "records.malformed_flag_member_exclusion_possible"} & set(window.codes()))
                    continue
                (flag,) = [flag for flag in window.flags() if flag["code"] == extra]
                self.assertEqual((level, scoped), (flag["scope"]["level"], flag["scope"]["run_id"]))
                if level == "window":
                    self.assertIn(extra, exclusions["reasons"])
                    self.assertIn("calibration.capture_invalid", flag["observed"]["excluding"])
                else:
                    excluded = {row["run_id"]: row["codes"] for row in exclusions["members_excluded"]}
                    self.assertIn(extra, excluded[run_id])

    def test_an_unreadable_log_or_log_directory_is_disclosed(self):
        """Review gap: a log that may hold a marker line but cannot be read is never silently skipped.

        Opus audit F2: it is its own DISCLOSE code, not records.malformed_flag, and blocks nothing."""
        for case in ("file", "directory"):
            with self.subTest(case):
                window = Window(self.tmp / f"unreadable-{case}", catalog_overrides=self.ISOLATE)
                logs = window.custody / "operator-logs"
                logs.mkdir(exist_ok=True)
                (logs / "07-b5t-science.log").write_text("stage output\n")
                target = logs / "07-b5t-science.log" if case == "file" else logs
                target.chmod(0)
                self.addCleanup(target.chmod, 0o755)
                if os.access(target, os.R_OK):
                    self.skipTest("running as a user who can read mode-000 files")
                try:
                    window.harvest()
                finally:
                    target.chmod(0o755)
                unreadable = [flag["observed"] for flag in window.flags()
                              if flag["code"] == "records.operator_log_unreadable"]
                expected = "operator-logs/07-b5t-science.log" if case == "file" else "operator-logs"
                self.assertIn(expected, [item["file"] for item in unreadable])
                self.assertNotIn("records.malformed_flag", window.codes())
                self.assertFalse(window.exclusions()["release_blocked"])

    def test_a_marker_line_in_the_desk_transcript_is_recovered(self):
        window = self.window(prefix_ledger=True)
        advance_pin(window)
        line = self.unwritten_line("campaign.runner_record_flagged", level="window",
                                   observed={"kind": "stale_lock_cleared"})

        def runner(argv, **kwargs):
            runs = Path(argv[argv.index("--runs-dir") + 1])
            (runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
            return SimpleNamespace(returncode=1, stdout="verdict written\n", stderr=line + "\n")

        window.harvest(seams=desk_seams(runner), prepare_desk=True, run_g3=False)
        flag = next(flag for flag in window.flags() if flag["code"] == "campaign.runner_record_flagged")
        self.assertEqual(flag["observed"], {"kind": "stale_lock_cleared"})
        self.assertNotIn("records.malformed_flag", window.codes())


class BinaryIdentityRederivedTests(WindowTestCase):
    """Cold pass N1 / Fable audit F10: an unread runtime powermetrics digest is re-derived at harvest.

    Before: instrument.binary_identity_unmeasured (EXCLUDE_MEMBER) removed the
    member whenever its own digest read failed, though the binary is the OS
    build's and the harvest on the same boot can hash it."""

    def window_with(self, name: str, *, calibrated: bool = True, boot: str = "B5-TEST-BOOT",
                    readable: bool = True) -> tuple[Window, str, str]:
        window = Window(self.tmp / name, catalog_overrides=self.ISOLATE)
        run_id = MEMBERS[0][0]
        sampler = self.tmp / f"{name}-powermetrics"
        sampler.write_bytes(b"stand-in powermetrics executable " + name.encode())
        digest = hashlib.sha256(sampler.read_bytes()).hexdigest()
        bundle = window.claim / run_id
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        metadata.setdefault("device", {})["powermetrics"] = {"executable_path": str(sampler),
                                                             "executable_sha256": None}
        metadata["instrument_calibration"] = {"bindings": {
            "powermetrics_sha256": digest if calibrated else "0" * 64}}
        metadata.setdefault("extra", {})["launch_lineage"] = {"collection_boot_session_id": boot.lower()}
        put(bundle / "metadata.json", metadata)
        if not readable:
            sampler.unlink()
        line = UnwrittenCoreFlagTests.unwritten_line(
            "instrument.binary_identity_unmeasured", level="member", run_id=run_id,
            observed={"runtime_powermetrics_sha256": None})
        logs = window.custody / "operator-logs"
        logs.mkdir(exist_ok=True)
        (logs / "07-b5t-science.log").write_text(line + "\n")
        return window, run_id, digest

    def test_an_equal_digest_on_the_collection_boot_supersedes_the_exclusion(self):
        window, run_id, digest = self.window_with("equal")
        window.harvest()
        self.assertNotIn("instrument.binary_identity_unmeasured", window.codes())
        (flag,) = [flag for flag in window.flags() if flag["code"] == "instrument.binary_identity_rederived"]
        self.assertEqual((run_id, digest, digest), (flag["scope"]["run_id"], flag["observed"]["harvest_sha256"],
                                                    flag["observed"]["calibrated_sha256"]))
        excluded = {row["run_id"]: row["codes"] for row in window.exclusions()["members_excluded"]}
        self.assertNotIn("instrument.binary_identity_unmeasured", excluded.get(run_id, []))

    def test_a_different_digest_boot_or_an_unreadable_binary_keeps_the_exclusion(self):
        for label, kwargs in (("differs", {"calibrated": False}), ("other_boot", {"boot": "OTHER-BOOT"}),
                              ("unreadable", {"readable": False})):
            with self.subTest(label):
                window, run_id, _ = self.window_with(label, **kwargs)
                window.harvest()
                self.assertNotIn("instrument.binary_identity_rederived", window.codes())
                excluded = {row["run_id"]: row["codes"] for row in window.exclusions()["members_excluded"]}
                self.assertIn("instrument.binary_identity_unmeasured", excluded[run_id])


ABSENT = object()  # the core provides no neg8_corpus_mint_drops (as before the b1 lane lands)


def hazard_member_gates(omitted: str | None = None):
    """``neg8_member_gates`` for either mint (the HAZARD mint reads ``neg8_freshness_binding_fields``);
    ``omitted`` is not a current strict mint."""
    stack = contextlib.ExitStack()
    stack.enter_context(neg8_member_gates())
    stack.enter_context(mock.patch.object(whole_window, "neg8_freshness_binding_fields",
                                          return_value=dict(NEG8_FRESHNESS), create=True))
    if omitted is not None:
        stack.enter_context(mock.patch.object(
            whole_window, "_current_strict_summary",
            side_effect=lambda summary, path=None: path is None or Path(path).name != omitted))
    return stack


def mint_drops_patch(drops: object, asked: list | None = None):
    """The core's ``neg8_corpus_mint_drops`` replaced: ``drops`` (rows, an exception to raise, or ABSENT)."""
    def function(runs_root, manifest_path):
        if asked is not None:
            listed = json.loads(Path(manifest_path).read_bytes())["members"]
            asked.append((Path(runs_root), [member["bundle_id"] for member in listed]))
        if isinstance(drops, Exception):
            raise drops
        return drops
    return mock.patch.object(whole_window, "neg8_corpus_mint_drops", None if drops is ABSENT else function,
                             create=True)


def neg8_corpus_in_process(window: "Window", failed=()) -> dict:
    """``neg8_corpus`` with the chain's prune helper and the core's mint run in this process.

    So the caller's patches (the member gates, the mint's drop rule) reach the helper as they reach the
    mint.  Returns the helper's summary; the bound and the driver's locator are written as the chain and
    the driver write them.
    """
    for bundle_id in CORPUS_IDS:
        put_corpus_stub(window.bound / bundle_id, bundle_id, "failed" if bundle_id in failed else "succeeded")
    night = window.custody / "night"
    collected = night / "transcript" / b5_chain.NEG8_COLLECTED_MANIFEST
    summary = night / "transcript" / b5_chain.NEG8_COLLECTED_SUMMARY
    collected.parent.mkdir(parents=True, exist_ok=True)
    argv = ["-c", str(window.measurement / CORPUS_RELATIVE), str(window.bound), str(collected), str(summary)]
    with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
        exec(compile(b5_chain.PRUNE_HELPER, "<b5-prune-helper>", "exec"), {"__name__": "__main__"})
    artifact = whole_window.mint_neg8_drift_bound_artifact(window.bound, collected)
    # The mint bound its bound to exactly the bytes the helper wrote.
    assert artifact["reference_corpus"]["manifest_sha256"] == sha(collected)
    put(window.bound / "neg8-drift-bound.json", artifact)
    put(night / "hazard_result.json", {"schema": "joulewise.b5_hazard_night.v1",
                                       "neg8_corpus": b5_chain.neg8_corpus_record(night)})
    return json.loads(summary.read_bytes())


class Neg8MintDropTests(WindowTestCase):
    """N2 (harvest half of A3): a succeeded corpus member may be left out only when the core's HAZARD
    mint drops it, evaluated on the same bound root; and (b1 lane item F2) a HAZARD bound counts as
    derived only when every member it names re-derives from its bundle in the bound root."""

    OMITTED = CORPUS_IDS[6]
    FAILED = CORPUS_IDS[0]
    DROP = [{"bundle_id": CORPUS_IDS[6], "reason": "not_current_strict_mint"}]

    def corpus_window(self, name: str, *, hazard: bool = True, omit: bool = True) -> "Window":
        """A window whose collected manifest left out FAILED and OMITTED, or, with ``omit=False``, all 12.

        On a HAZARD root the chain's helper drops OMITTED because the (injected) mint drop rule names
        it; on any other root the helper never consults that rule, so the collected manifest is a
        corpus no rule selected (written as the selected input to the helper)."""
        window = Window(self.tmp / name, catalog_overrides=self.ISOLATE)
        if hazard:
            LineageFindingTests.publish(self, window)
            self.assertTrue((window.bound / LineageFindingTests.LOCATOR).is_file())
            with hazard_member_gates(), mint_drops_patch(self.DROP if omit else []):
                summary = neg8_corpus_in_process(window, [self.FAILED] if omit else [])
            self.assertEqual(summary["members_kept"], 10 if omit else 12)
        elif omit:
            members = [member for member in COMMITTED_CORPUS["members"] if member["bundle_id"] != self.OMITTED]
            self.assertIsNone(neg8_corpus(window, [self.FAILED], manifest_members=members))
        else:
            self.assertIsNone(neg8_corpus(window))
        return window

    def harvest(self, window: "Window", drops: object, *extra) -> tuple[dict, list]:
        asked: list = []
        with contextlib.ExitStack() as stack:
            stack.enter_context(hazard_member_gates())
            stack.enter_context(mint_drops_patch(drops, asked))
            for patch in extra:
                stack.enter_context(patch)
            window.harvest()
        return json.loads((window.archive / "derived" / "neg8-bound.json").read_bytes()), asked

    def test_a_member_the_hazard_mint_drops_keeps_the_collected_subset(self):
        """Before: dropped_member_succeeded, neg8.bound_not_derived (EXCLUDE_WINDOW)."""
        window = self.corpus_window("dropped")
        check, asked = self.harvest(window, self.DROP)
        self.assertEqual((check["derived_from"], check["problems"], check["mint_rule"], check["members_rederived"]),
                         ("collected_subset", [], "joulewise.whole_window.neg8_corpus_mint_drops", True))
        self.assertEqual(check["dropped_bundle_ids"], [self.FAILED, self.OMITTED])
        # Asked once, on the bound root, over the committed members that succeeded (as the chain asks).
        self.assertEqual(asked, [(window.bound, [bundle for bundle in CORPUS_IDS if bundle != self.FAILED])])
        self.assertNotIn("neg8.bound_not_derived", window.codes())
        dropped = [flag for flag in window.flags() if flag["code"] == "neg8.corpus_member_dropped"]
        self.assertEqual([(flag["scope"]["level"], flag["scope"]["run_id"], flag["observed"]) for flag in dropped],
                         [("member", self.OMITTED, {"bundle_id": self.OMITTED, "reason": "not_current_strict_mint"})])

    def test_a_mint_drop_for_a_reason_that_is_not_member_validity_is_a_selected_corpus(self):
        """Keeper (review R1): a drop reason that is not evidence about the member's number authorizes nothing."""
        for reason in ("energy_evidence_invalid", "launch_lineage:launch_consumption_invalid",
                       "calibration_identity_unrecorded", "condition_differs", "bundle_inventory_invalid"):
            with self.subTest(reason):
                window = self.corpus_window(reason.replace(":", "-"))
                check, asked = self.harvest(window, [{"bundle_id": self.OMITTED, "reason": reason}])
                self.assertEqual(len(asked), 1)
                self.assertIsNone(check["derived_from"])
                self.assertEqual(check["problems"], [f"dropped_member_succeeded:{self.OMITTED}",
                                                     f"mint_drop_reason_not_accepted:{self.OMITTED}={reason}"])
                self.assertIn("neg8.bound_not_derived", window.exclusions()["reasons"])
                self.assertNotIn("neg8.corpus_member_dropped", window.codes())
        self.assertEqual(h.NEG8_ACCEPTED_DROP_REASONS,
                         {"status_not_succeeded", "not_current_strict_mint", "custody_triangle_disagrees",
                          "precheck_ineligible", "reduction_mismatch"})

    def test_any_other_drop_is_still_a_selected_corpus(self):
        """Keeper: a succeeded member the mint keeps, or a mint that cannot say, selects the corpus."""
        cases = {"mint_keeps_it": ([], True),
                 "mint_drops_another": ([{"bundle_id": CORPUS_IDS[3], "reason": "condition_differs"}], True),
                 "mint_raises": (ValueError("split evenly"), True), "core_without_the_function": (ABSENT, True),
                 "root_not_hazard": (self.DROP, False)}
        for name, (drops, hazard) in cases.items():
            with self.subTest(name):
                window = self.corpus_window(name, hazard=hazard)
                check, asked = self.harvest(window, drops)
                self.assertIsNone(check["derived_from"])
                self.assertIn(f"dropped_member_succeeded:{self.OMITTED}", check["problems"])
                self.assertIn("neg8.bound_not_derived", window.exclusions()["reasons"])
                self.assertNotIn("neg8.corpus_member_dropped", window.codes())
                self.assertEqual(asked != [], hazard and drops is not ABSENT)  # not HAZARD: never asked

    def test_a_hazard_bound_whose_members_do_not_rederive_is_not_derived(self):
        """F2.  Before: the bound validated (arithmetic and manifest identity) and was derived."""
        shifted = CORPUS_IDS[2]

        def energy_differs(path):
            gross, idle, problem = corpus_point(path)
            return ({**gross, "point_j": gross["point_j"] + 0.5} if path.name == shifted else gross), idle, problem

        energy = mock.patch.object(whole_window, "_reference_energy_evidence", side_effect=energy_differs)
        for omit, derived in ((True, "collected_subset"), (False, "registered_corpus")):
            drops = self.DROP if omit else []
            with self.subTest(derived, tamper="energy"):
                window = self.corpus_window(f"energy-{derived}", omit=omit)
                check, _asked = self.harvest(window, drops, energy)
                self.assertEqual((check["derived_from"], check["members_rederived"]), (None, False))
                self.assertEqual(check["problems"], [f"bound_member_energy_differs:{shifted}"])
                self.assertIn("neg8.bound_not_derived", window.exclusions()["reasons"])
            with self.subTest(derived, tamper="bytes"):
                window = self.corpus_window(f"bytes-{derived}", omit=omit)
                put(window.bound / shifted / "metadata.json", {"run_id": shifted, "edited": True})
                check, _asked = self.harvest(window, drops)
                self.assertEqual(check["problems"], [f"bound_member_bytes_differ:{shifted}"])
                self.assertIn("neg8.bound_not_derived", window.codes())
            with self.subTest(derived, tamper="calibration"):
                window = self.corpus_window(f"calibration-{derived}", omit=omit)
                other = {**NEG8_FRESHNESS, "calibration_identity_sha256": "0" * 64}
                fields = lambda metadata: dict(other if metadata.get("run_id") == shifted else NEG8_FRESHNESS)
                check, _asked = self.harvest(
                    window, drops,
                    mock.patch.object(whole_window, "neg8_freshness_bindings_from_metadata", side_effect=fields),
                    mock.patch.object(whole_window, "neg8_freshness_binding_fields", side_effect=fields, create=True))
                self.assertEqual(check["problems"], [f"bound_member_calibration_differs:{shifted}"])
                self.assertIsNone(check["derived_from"])
            with self.subTest(derived, tamper="lineage"):
                window = self.corpus_window(f"lineage-{derived}", omit=omit)

                def lineage(path, **kwargs):
                    if Path(path).name == shifted:
                        raise whole_window.LaunchLineageError("launch_lineage_conflict", "a foreign stamp")
                    return None

                check, _asked = self.harvest(
                    window, drops, mock.patch.object(whole_window, "authenticate_bundle_launch_lineage",
                                                     side_effect=lineage))
                self.assertEqual(check["problems"], [f"bound_member_lineage_unauthenticated:{shifted}"])
                self.assertIsNone(check["derived_from"])
            with self.subTest(derived, tamper="none"):
                window = self.corpus_window(f"clean-{derived}", omit=omit)
                check, _asked = self.harvest(window, drops)
                self.assertEqual((check["derived_from"], check["members_rederived"], check["problems"]),
                                 (derived, True, []))
        # The check is the HAZARD bound's (it has no lineage stamp); a non-HAZARD root is unchanged.
        window = self.corpus_window("energy-not-hazard", hazard=False, omit=False)
        check, _asked = self.harvest(window, [], energy)
        self.assertEqual((check["derived_from"], check.get("members_rederived")), ("registered_corpus", None))


@unittest.skipUnless(hasattr(whole_window, "neg8_corpus_mint_drops"),
                     "the core's HAZARD NEG-8 mint (b1 lane, A3 core) is not in this tree")
class Neg8MintIntegrationTests(WindowTestCase):
    """The chain's prune helper, the core's HAZARD mint and the harvest agree on one corpus (A3, N2).

    One succeeded corpus member fails a mint predicate (not a current strict mint).  The helper drops it,
    the real mint binds its bound to exactly the helper's bytes, and the harvest derives the bound from
    them with one neg8.corpus_member_dropped.  Only the per-member gates are stubbed (as for the mint
    elsewhere in this file); the drop rule, the rendering and the binding are the core's own.
    """

    OMITTED = CORPUS_IDS[6]

    def test_the_helper_the_mint_and_the_harvest_drop_the_same_member(self):
        window = Window(self.tmp / "integrated", catalog_overrides=self.ISOLATE)
        LineageFindingTests.publish(self, window)
        with hazard_member_gates(self.OMITTED):
            summary = neg8_corpus_in_process(window)
        self.assertEqual(summary["dropped"], [{"bundle_id": self.OMITTED, "status": "succeeded",
                                               "mint_drop": "not_current_strict_mint"}])
        self.assertEqual(summary["members_kept"], 11)
        with hazard_member_gates(self.OMITTED):
            window.harvest()
        check = json.loads((window.archive / "derived" / "neg8-bound.json").read_bytes())
        self.assertEqual((check["derived_from"], check["problems"], check["members_rederived"], check["mint_rule"]),
                         ("collected_subset", [], True, "joulewise.whole_window.neg8_corpus_mint_drops"))
        dropped = [flag["observed"] for flag in window.flags() if flag["code"] == "neg8.corpus_member_dropped"]
        self.assertEqual(dropped, [{"bundle_id": self.OMITTED, "reason": "not_current_strict_mint"}])
        self.assertNotIn("neg8.bound_not_derived", window.codes())


# ---------------------------------------------------------------------------
# Rehearsal round 2 (night-archive gate-prune/rehearsal-r2): the desk order
# (R2-1), the window membership binding (R2-2a), G10's result (R2-3) and the
# desk producers' diagnostics (R2-4).
# ---------------------------------------------------------------------------

def verdict_runner(calls: list, *, returncode=1, stdout="", stderr="", probe=None):
    """The desk verdict writer's seam: records its argv and writes a verdict file and one log row."""
    def runner(argv, **kwargs):
        calls.append(list(argv))
        if "--whole-window-verdict" in argv:
            if probe is not None:
                probe(argv)
            runs = Path(argv[argv.index("--runs-dir") + 1])
            (runs / "whole-window-verdict.json").write_text('{"status":"failed"}\n')
            with (runs / "campaign_log.jsonl").open("a") as log:
                log.write('{"status":"failed"}\n')
        return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)
    return runner


def desk_flags(window: "Window", step: str) -> list[dict]:
    return [flag["observed"] for flag in window.flags()
            if flag["code"] == "whole_window.producer_failed" and flag["observed"].get("step") == step]


class DeskOrderTests(WindowTestCase):
    """R2-1: the desk order is chain exit, pin advance, harvest; the desk verdict needs the advanced pin.

    The window's post-calibration moved the ledger past the committed pin.  A
    verdict written then fails its bracket on calibration_ledger_head_mismatch
    (and never reaches the lineage check), and its row stays in the append-only
    campaign log.  The real ledger, the real snapshot and the real desk pin
    advance (git commit included) run here; only the writer is the seam.
    """

    def test_a_pin_behind_the_terminal_head_writes_no_verdict_and_the_advance_cures_it(self):
        window = self.window(prefix_ledger=True)
        commit_checkout(window)  # the pin committed where the window armed: behind its post-calibration
        calls: list = []
        window.harvest(seams=desk_seams(verdict_runner(calls)), prepare_desk=True, run_g3=False)
        self.assertEqual([argv for argv in calls if "--whole-window-verdict" in argv], [])
        (problem,) = desk_flags(window, "head_pin")
        self.assertEqual(problem["reason"], "pin_behind")
        self.assertLess(problem["committed_sequence"], problem["terminal_sequence"])
        self.assertIn("calibration_ledger_head_mismatch", problem["ledger_reasons"])
        # Nothing the writer owns was written, so a re-harvest after the advance starts clean.
        for name in ("bracket-binding.json", "campaign_log.jsonl", "whole-window-verdict.json"):
            self.assertFalse((window.claim / name).exists(), name)
        self.assertIn("whole_window.verdict_absent", window.exclusions()["reasons"])
        # The cure: the desk pin advance, then the harvest again.
        self.assertEqual(advance_pin(window)["status"], "ADVANCED")
        window.archive = window.root / "archive-after-advance"
        window.harvest(seams=desk_seams(verdict_runner(calls)), prepare_desk=True, run_g3=False)
        (argv,) = [argv for argv in calls if "--whole-window-verdict" in argv]
        self.assertEqual(argv[argv.index("--head-pin") + 1], str(window.pin))
        self.assertEqual(desk_flags(window, "head_pin"), [])
        boundary = json.loads((window.archive / "derived" / "terminal-boundary.json").read_bytes())
        self.assertEqual((boundary["pin_relation"], boundary["refusal_code"], boundary["committed_pin_refusal_reasons"]),
                         ("equal", None, []))
        self.assertEqual(json.loads(window.pin.read_bytes())["sequence"],
                         boundary["terminal_head_pin_candidate"]["sequence"])

    def test_an_advance_without_its_pin_only_commit_writes_no_verdict(self):
        window = self.window(prefix_ledger=True)
        self.assertEqual(advance_pin(window, commit=False)["status"], "ADVANCED_UNCOMMITTED")
        calls: list = []
        window.harvest(seams=desk_seams(verdict_runner(calls)), prepare_desk=True, run_g3=False)
        self.assertEqual([argv for argv in calls if "--whole-window-verdict" in argv], [])
        (problem,) = desk_flags(window, "head_pin")
        self.assertEqual((problem["reason"], problem["ledger_reasons"]),
                         ("pin_uncommitted", ["calibration_ledger_head_uncommitted"]))

    def test_a_hazard_window_asks_g3_for_the_advanced_pin_boundary_and_the_desk_binding(self):
        window = Window(self.tmp / "g3-r2", prefix_ledger=True, catalog_overrides=self.ISOLATE)
        (window.pack / "analysis_manifest_v3.json").write_text("{}\n")
        (window.claim / "whole-window-verdict.json").write_text("{}\n")
        (window.claim / "bracket-binding.json").write_text("{}\n")
        (window.claim / h.MEMBERSHIP_BINDING_NAME).write_text("{}\n")
        calls: list = []

        def runner(argv, **kwargs):
            calls.append(list(argv))
            Path(argv[argv.index("--report-json") + 1]).write_text(json.dumps({"assertions": []}))
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        window.harvest(seams=desk_seams(runner, runner=runner))  # int3: G3 runs through ``runner`` (P2-HARV seams)
        (argv,) = [argv for argv in calls if "--report-json" in argv]
        self.assertEqual(argv[argv.index("--expected-pin-relation") + 1], "equal")
        self.assertEqual(argv[argv.index("--window-membership-binding") + 1],
                         str(window.claim / h.MEMBERSHIP_BINDING_NAME))
        from scripts import check_window_provenance as checker
        parsed_args = checker.build_parser().parse_args(argv[3:])  # [python, -B, script, ...]
        self.assertEqual(parsed_args.expected_pin_relation, "equal")


class MembershipBindingTests(WindowTestCase):
    """R2-2a: a floor pack's manifests carry no analysis-manifest identity; the verdict writer needs a binding.

    The probe is the production resolver (run_campaign._whole_window_campaign_membership), called the way the
    verdict writer calls it, with the argv the harvest gave the writer.
    """

    REFERENCES = ("neg8-window-start-r1", "neg8-window-end-r1")

    def manifests(self, window: "Window", identities: dict[str, str | None]) -> str:
        """Campaign manifests in the claim root, one per name: members plus a start and an end reference."""
        from scripts import run_campaign
        policy_sha = sha(window.measurement / POLICY)
        for bundle_id in self.REFERENCES:
            put(window.claim / bundle_id / "config.json", {"run_id": bundle_id})
            put(window.claim / bundle_id / "summary_metrics.json", {"status": "succeeded"})
        science = [{"config": f"{row[0]}.json", "run_id": row[0], "execution": "invoked", "bundle_ids": [row[0]],
                    "role": row[1], "sentinel_position": None, "canonical_neg8_workload": False} for row in MEMBERS]
        references = [{"config": f"{bundle_id}.json", "run_id": bundle_id, "execution": "invoked",
                       "bundle_ids": [bundle_id], "role": run_campaign.NEG8_REFERENCE_ROLE,
                       "sentinel_position": position, "canonical_neg8_workload": True}
                      for bundle_id, position in zip(self.REFERENCES, ("start", "end"))]
        members = {"science": science, "references": references}
        for name, identity in identities.items():
            put(window.claim / "campaign_manifests" / f"{name}.json",
                {"schema_version": "joulewise.campaign_provenance.v1", "analysis_manifest_id": identity,
                 "campaign_policy": {"sha256": policy_sha}, "members": members[name]})
        return policy_sha

    def harvest_with_probe(self, window: "Window", policy_sha: str) -> tuple[list, list]:
        from scripts import run_campaign
        calls, resolved = [], []

        def probe(argv):
            runs = Path(argv[argv.index("--runs-dir") + 1])
            binding = argv[argv.index("--window-membership-binding") + 1] \
                if "--window-membership-binding" in argv else None
            resolution = run_campaign._whole_window_campaign_membership(
                runs, policy_sha, Path(argv[argv.index("--log") + 1]), membership_binding_path=binding)
            resolved.append((binding, tuple(resolution.conditions),
                             sorted(source.run_id or source.path.name for source in resolution.sources)))

        advance_pin(window)
        window.harvest(seams=desk_seams(verdict_runner(calls, probe=probe)), prepare_desk=True, run_g3=False)
        return calls, resolved

    def test_the_desk_binds_a_null_identity_window_and_the_writer_resolves_it(self):
        window = self.window(prefix_ledger=True)
        policy_sha = self.manifests(window, {"science": None, "references": None})
        _calls, resolved = self.harvest_with_probe(window, policy_sha)
        ((binding, conditions, members),) = resolved
        self.assertEqual(conditions, ())  # without a binding: whole_window_campaign_membership_unresolved
        self.assertEqual(members, sorted([row[0] for row in MEMBERS] + list(self.REFERENCES)))
        target = window.claim / h.MEMBERSHIP_BINDING_NAME
        self.assertEqual(binding, str(target))
        value = json.loads(target.read_bytes())
        self.assertEqual((value["schema_version"], value["campaign_policy_sha256"]),
                         ("joulewise.whole_window_membership_binding.v1", policy_sha))
        self.assertEqual([row["path"] for row in value["source_campaign_manifests"]],
                         ["campaign_manifests/references.json", "campaign_manifests/science.json"])
        # Archived with the claim root; the writer's own changes are not source changes.
        archived = window.archive / "sources" / "night-custody" / window.claim.relative_to(window.custody)
        self.assertEqual((archived / h.MEMBERSHIP_BINDING_NAME).read_bytes(), target.read_bytes())
        self.assertNotIn("records.source_changed_during_harvest", window.codes())
        self.assertEqual(desk_flags(window, "membership_binding"), [])

    def test_a_window_the_resolver_groups_by_its_analysis_manifest_gets_no_binding(self):
        window = self.window(prefix_ledger=True)
        policy_sha = self.manifests(window, {"references": "am-window"})
        _calls, resolved = self.harvest_with_probe(window, policy_sha)
        ((binding, conditions, _members),) = resolved
        self.assertEqual((binding, conditions), (None, ()))
        self.assertFalse((window.claim / h.MEMBERSHIP_BINDING_NAME).exists())
        self.assertEqual(desk_flags(window, "membership_binding"), [])

    def test_a_mixed_identity_window_is_not_bound_to_its_references_alone(self):
        """GAMMA's shape (R2-2b, a core or pack decision): a binding would make the verdict cover the references only."""
        window = self.window(prefix_ledger=True)
        policy_sha = self.manifests(window, {"science": "am-gamma", "references": None})
        _calls, resolved = self.harvest_with_probe(window, policy_sha)
        ((binding, conditions, _members),) = resolved
        self.assertIsNone(binding)
        self.assertIn("whole_window_campaign_membership_unresolved", conditions)
        self.assertFalse((window.claim / h.MEMBERSHIP_BINDING_NAME).exists())
        (problem,) = desk_flags(window, "membership_binding")
        self.assertEqual((problem["reason"], problem["identities"], problem["null_identity_manifests"]),
                         ("mixed_analysis_identity", ["am-gamma"], 1))


class G10ResultTests(WindowTestCase):
    """R2-3: G10's result reaches the window's flags (the catalog's g10.* codes, disclosed)."""

    def request_g10(self, window: "Window") -> Path:
        plan = json.loads(window.plan_path.read_bytes())
        plan["hazard_window"]["g10"] = True
        put(window.plan_path, plan)
        return window.custody / "night"

    def run_g10(self, night: Path, result: str | None, *, off_ok=True, returncode=0, flag_code=None) -> None:
        """The driver's real _run_g10 around a G10 process that writes its record as the script renders it."""
        from joulewise.b5 import driver as b5_driver
        from scripts import g10_clock_step_control as g10

        def popen(argv, **kwargs):
            if result is not None:
                record = {"schema": g10.SCHEMA, "result": result, "off_ok": off_ok, "verdict": None,
                          "flag_code": flag_code or g10.FLAG_CODES[result]}
                (night / g10.RECORD_BASENAME).write_bytes(g10.render(record))
            return SimpleNamespace(pid=999_999, wait=lambda timeout=None: returncode)

        notes: list = []
        window = SimpleNamespace(seams=SimpleNamespace(g10_argv=lambda night_dir, t: ["g10"], popen=popen),
                                 note=notes.append)
        b5_driver._run_g10(window, night, 335.0)
        self.assertEqual(notes, [])

    def g10_flags(self, window: "Window") -> list[tuple[str, dict]]:
        return [(flag["code"], flag["observed"]) for flag in window.flags() if flag["code"].startswith("g10.")]

    def test_the_result_codes_are_the_scripts(self):
        from scripts import g10_clock_step_control as g10
        self.assertEqual(h.G10_RESULT_CODES, g10.FLAG_CODES)
        self.assertEqual((h.G10_RECORD_NAME, h.G10_DRIVER_RECORD_NAME), (g10.RECORD_BASENAME, "g10.driver.json"))

    def test_each_result_is_emitted_with_its_code(self):
        for result in ("DISCHARGED", "NOT_DISCHARGED", "UNMEASURED", "INTERRUPTED", "ERROR"):
            with self.subTest(result):
                window = Window(self.tmp / f"g10-{result}", catalog_overrides=self.ISOLATE)
                self.run_g10(self.request_g10(window), result, returncode=0 if result != "INTERRUPTED" else 143)
                window.harvest()
                ((code, observed),) = self.g10_flags(window)
                self.assertEqual(code, h.G10_RESULT_CODES[result])
                self.assertEqual(observed, {"result": result, "off_ok": True,
                                            "returncode": 0 if result != "INTERRUPTED" else 143,
                                            "timed_out": False, "record": "present", "requested": True})
                self.assertNotIn(code, window.exclusions()["reasons"])  # disclosed

    def test_a_requested_g10_without_a_consistent_record_is_g10_error(self):
        window = Window(self.tmp / "g10-skipped", catalog_overrides=self.ISOLATE)
        night = self.request_g10(window)
        # The driver did not run G10 (joulewise.b5.driver, step 7): its reason is in hazard_result.json.
        put(night / "hazard_result.json", {"schema": "joulewise.b5_hazard_night.v1",
                                           "g10": {"ran": False, "requested": True,
                                                   "reason": "chain stopped by the driver"}})
        window.harvest()
        ((code, observed),) = self.g10_flags(window)
        self.assertEqual(code, "g10.error")
        self.assertEqual((observed["record"], observed["ran"], observed["driver_reason"], observed["result"]),
                         ("absent", False, "chain stopped by the driver", None))
        # A record whose code is not its result's code is not trusted either.
        window = Window(self.tmp / "g10-inconsistent", catalog_overrides=self.ISOLATE)
        self.run_g10(self.request_g10(window), "NOT_DISCHARGED", flag_code="g10.discharged")
        window.harvest()
        ((code, observed),) = self.g10_flags(window)
        self.assertEqual((code, observed["record"], observed["result"]), ("g10.error", "inconsistent", "NOT_DISCHARGED"))

    def test_an_unrequested_g10_emits_nothing(self):
        window = self.window()
        window.harvest()
        self.assertEqual(self.g10_flags(window), [])


class DeskDiagnosticsTests(WindowTestCase):
    """R2-4: a failed desk producer is diagnosable from the archive alone."""

    LINEAGE = "error: launch_lineage_conflict: window members do not carry one identical authenticated lineage\n"

    def test_the_verdict_writers_refusal_is_kept_and_named(self):
        window = self.window(prefix_ledger=True)
        advance_pin(window)
        calls: list = []
        window.harvest(seams=desk_seams(verdict_runner(calls, returncode=2, stdout="", stderr=self.LINEAGE)),
                       prepare_desk=True, run_g3=False)
        self.assertEqual((window.archive / "withheld" / "transcripts" / "desk-verdict.txt").read_text(), self.LINEAGE)
        (problem,) = desk_flags(window, "whole_window_verdict")
        self.assertEqual(problem, {"step": "whole_window_verdict", "returncode": 2,
                                   "error_code": "launch_lineage_conflict",
                                   "error_line": "launch_lineage_conflict: window members do not carry one "
                                                 "identical authenticated lineage"})

    def test_numbers_stay_in_the_withheld_transcript(self):
        self.assertEqual(h._first_error("progress 3/4\nerror: neg8_bound_invalid: bound 12.5 J above 1e-3 J\n"),
                         {"error_code": "neg8_bound_invalid", "error_line": "neg8_bound_invalid: bound # J above # J"})
        self.assertEqual(h._first_error("Traceback (most recent call last):\n  x\nValueError: drift 0.25\n"),
                         {"error_code": None, "error_line": "ValueError: drift #"})
        self.assertEqual(h._first_error(""), {"error_code": None, "error_line": None})

    def test_the_bracket_binding_producers_error_is_kept(self):
        from joulewise import calibration_bracketing as brackets
        window = self.window(prefix_ledger=True)
        advance_pin(window)
        calls: list = []
        refusal = ValueError("bracket session b5t-session names runs root 2 of 3")
        with mock.patch.object(brackets, "build_calibration_bracket_binding", side_effect=refusal):
            window.harvest(seams=desk_seams(verdict_runner(calls)), prepare_desk=True, run_g3=False)
        self.assertEqual([argv for argv in calls if "--whole-window-verdict" in argv], [])
        transcript = (window.archive / "withheld" / "transcripts" / "desk-binding.txt").read_text()
        self.assertIn("bracket session b5t-session names runs root 2 of 3", transcript)
        (problem,) = desk_flags(window, "bracket_binding")
        self.assertEqual(problem["error_line"], "ValueError: bracket session b5t-session names runs root # of #")


class Neg8ReferencePhysicsTests(WindowTestCase):
    """A physics exclusion on a NEG-8 window reference no longer excludes the window by itself.

    Audit A1 (batch 1, 2026-10-07) had made it neg8.reference_member_excluded
    (EXCLUDE_WINDOW).  The NEG-8 survivors ruling (registration 0.12)
    supersedes that: the reference is dropped and the screen is re-derived on
    the surviving references, so only the survivors screen
    (neg8.screen_failed) can remove the window
    (tests/test_neg8_survivors.py HarvestSurvivorTests covers the screen).
    The reference here is a real bundle collected over b5t-abs-r02's span.
    """

    CODE = "neg8.reference_member_excluded"
    REFERENCE = "neg8-window-start-r1"

    def window_with_reference(self, subdir: str = "w", **kwargs) -> Window:
        kwargs.setdefault("catalog_overrides", self.ISOLATE)
        window = Window(self.tmp / subdir, **kwargs)
        target = window.claim / self.REFERENCE
        make_member(target, self.REFERENCE, SHIFT_S["b5t-abs-r02"])
        tree_path = window.pack / "plan_tree.json"
        tree = json.loads(tree_path.read_bytes())
        tree["external_inputs"]["manifests"] = [{"input_id": "start_reference", "members": [{
            "run_id": self.REFERENCE, "path": f"configs/campaigns/{PACK_ID}/refs/{self.REFERENCE}.json",
            "sha256": sha(target / "config.json")}]}]
        put(tree_path, tree)
        (window.pack / "plan_tree.sha256").write_text(f"{sha(tree_path)}  plan_tree.json\n")
        # The sealed and executed inventories name the plan tree as written.
        changed = {path.relative_to(window.measurement).as_posix(): sha(path)
                   for path in (tree_path, window.pack / "plan_tree.sha256")}
        sealed = window.measurement / "configs/campaigns/v5_claim_25g83/sealed_inventory.json"
        value = json.loads(sealed.read_bytes())
        value["files"].update(changed)
        put(sealed, value)
        executed = window.custody / "night" / "executed_inventory.json"
        value = json.loads(executed.read_bytes())
        value["measurement_checkout"]["files"].update(changed)
        put(executed, value)
        return window

    def test_contention_over_a_start_reference_request_does_not_exclude_the_window_by_itself(self):
        """Under A1: a window flag, claim_usable False. Now: the member flag only; the screen decides."""
        request = request_span_ns("b5t-abs-r02")
        window = self.window_with_reference(journals={
            "contention_extra": [((request[0] - NS, request[1] + NS),
                                  {"pid": 77, "command": "fseventsd", "cpu_s_per_s": 1.84})]})
        record = window.harvest()
        self.assertEqual(record["verdict"], "COLLECTED", record["faults"])
        roster = {row["run_id"]: row for row in json.loads((window.archive / "derived" / "roster.json")
                                                          .read_bytes())["members"]}
        member = roster[self.REFERENCE]
        self.assertEqual((member["kind"], member["stage_id"], member.get("cells", [])), ("auxiliary", "start_reference", []))
        self.assertIn("contention.request_overlap", window.codes(self.REFERENCE))
        self.assertNotIn(self.CODE, {flag["code"] for flag in window.flags()})
        # No window-level flag is raised from the reference's member flag: every
        # window reason is one the same window has without the contender.
        reference_window = self.window_with_reference("uncontended")
        reference_window.harvest()
        self.assertNotIn("contention.request_overlap", reference_window.codes(self.REFERENCE))
        self.assertEqual(set(window.exclusions()["reasons"]) - {"contention.request_overlap"},
                         set(reference_window.exclusions()["reasons"]))

    def test_the_superseded_code_is_registered_nowhere(self):
        from joulewise.flags.catalog import DRAFT_CODES
        fixture = json.loads((FIXTURES / "flag_catalog.json").read_bytes())["codes"]
        allowlist = json.loads((ROOT / "configs/gates/hazard_refusals.json").read_bytes())
        self.assertNotIn(self.CODE, h.CODES)
        self.assertNotIn(self.CODE, DRAFT_CODES)
        self.assertNotIn(self.CODE, fixture)
        self.assertNotIn(self.CODE, allowlist["window_exclusions"])
        self.assertNotIn(self.CODE, h.AUDFIX1_CODES | h.AUDFIX2_CODES | h.NEG8_SURVIVOR_CODES)
        self.assertFalse(hasattr(h._Harvest, "neg8_reference_exclusions"))
        for code in ("neg8.reference_lost", "neg8.midpoint_lost"):
            self.assertEqual("DISCLOSE", fixture[code]["effect"])
            self.assertEqual("DISCLOSE", DRAFT_CODES[code]["effect"])


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
