"""Generated sweep: every field frozen R1 derives from a raw record, recorded differently, must refuse.

Lead directive of 2026-11-21 (fix-2), D1 to D3. Part C derives each such field again with the frozen function
and compares; it never takes the recorded value on trust, never passes a required check whose input is missing
or unobservable, and holds the census to the structure ``r1_runtime.Segment.run`` writes.

One clean synthetic attempt is built with the frozen differential suite's own control. ``INVENTORY`` names each
derived field, the frozen code that derives it and the evaluator check that derives it again. For each entry the
sweep generates mutations that change only the recorded value, so the record no longer equals its derivation,
and calls that check on the mutated record. Every mutation must refuse, the clean record must pass, and every
inventory entry must have generated at least one mutation.

    python3.13 -IB tests/align/partc_derived_sweep.py      (JW_PARTC_REPO selects the tree under test)

It prints one `SWEEP <entry> <generated> <refused>` line per entry and exits 1 on any mutation that passed, any
clean record refused, or any entry with nothing generated. The pinned commits must be in the local object
database (see the suite's docstring).
"""
import copy
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SUITE = Path(__file__).resolve().parent / "test_partc_frozen_differential.py"

# name: (frozen derivation, evaluator check)
INVENTORY = {
    "sidecar.session": ("thermal.Sidecar.start: align-<opening monotonic ns>", "_replay_frozen_sidecar"),
    "sidecar.seq": ("thermal.Sidecar._write: row number", "_validate_sidecar"),
    "sidecar.schema_module": ("thermal.Sidecar._write: constants", "_validate_sidecar"),
    "sidecar.error": ("thermal.Sidecar._write: the reading errors joined", "_replay_frozen_sidecar"),
    "sidecar.raw": ("thermal.Sidecar._write: []", "_replay_frozen_sidecar"),
    "sidecar.thermal_policy": ("thermal.Sidecar.start: the validated policy", "_validate_sidecar"),
    "sidecar.reading_projection": ("thermal.sample: source, units, sensors, errors", "_replay_frozen_sidecar"),
    "sidecar.boundary_stamp": ("thermal.Sidecar._write: finished is started", "_validate_sidecar"),
    "sidecar.coverage": ("thermal.Coverage.report at session end", "_validate_sidecar"),
    "sidecar.collector_error": ("thermal.Sidecar.stop: no collector error", "_validate_sidecar"),
    "gate.entry_sensors": ("ThermalSession._entry_values at entry", "_gate_witnesses N5.entry"),
    "gate.entry_slope": ("slow_slope at entry, same view", "_gate_witnesses N5.entry"),
    "gate.exit_sample": ("ThermalSession._wait: latest or release row", "_gate_witnesses exit view"),
    "gate.release": ("ThermalSession._wait: that row's temperatures", "_gate_witnesses exit view"),
    "gate.exit_slope": ("slow_slope at the final poll, same view", "_gate_witnesses exit view"),
    "gate.reference": ("ThermalSession._wait: the window reference, or G0's release", "_gate_witnesses"),
    "gate.outcome": ("ThermalSession._wait: released, timeout, unobserved or deadman", "_gate_witnesses"),
    "census.points": ("Segment.run: start then end, once each", "_check_census"),
    "census.order": ("LoadJournal.snapshot on one monotonic clock around the samples", "_check_census"),
    "load.fields": ("LoadJournal.fields: the receipt's copy of the journal", "_check_load"),
    "window.member": ("r1_runtime.main: terminal bracket around the segment", "_check_member_window"),
    "window.step_wall": ("RL-186: member_wall_s inside the bracket", "_check_member_window"),
    "window.soak": ("r1_runtime.main and Segment.idle: bracket and session hold the idle", "_check_soak_window"),
    "soak.series": ("Segment.k_idle over the sensor journal", "_derive_soak"),
}


def load_suite():
    spec = importlib.util.spec_from_file_location("partc_suite", SUITE)
    suite = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = suite
    spec.loader.exec_module(suite)
    return suite


def run():
    s = load_suite()
    generated = {name: 0 for name in INVENTORY}
    refused = {name: 0 for name in INVENTORY}
    failures = []

    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        finder = s.import_world(work / "src")
        s.MODEL_DIR = work / "synthetic-model"
        s.MODEL_DIR.mkdir()
        s.write(s.MODEL_DIR / "config.json", {"max_position_embeddings": 40960})
        s.issue_model_source()
        s.endpoint_code()
        with s.kit_source(finder), s.compact_control(), patch.object(
                s.rt, "registered_s6", return_value={"slots": {"S6": 1.}, "s6_tuning": {}}):
            base = work / "base"
            assert not s.control(base), "the clean control lost a descriptor binding"
        pc, EvidenceFailure = s.pc, s.evidence.EvidenceFailure
        sensors = s.rt.sensors_policy(s.CONFIG)

        def expect(entry, label, check, *, clean=False):
            """A check refuses by raising EvidenceFailure or, for ``_gate_findings``, by returning findings.
            Any other return (None, or a verdict a check hands back) is a pass. Clean must pass; a mutation must
            refuse."""
            try:
                result = check()
                findings = [f"{item.reason} {item.field}" for item in result] if isinstance(result, list) else []
            except EvidenceFailure as error:
                findings = [f"{error.reason} {error.field}"]
            if clean:
                if findings:
                    failures.append(f"{entry} clean {label}: refused {findings[0]}")
                return
            generated[entry] += 1
            if findings:
                refused[entry] += 1
            else:
                failures.append(f"{entry} {label}: passed")

        def raw(rows):
            return b"".join(json.dumps(row, sort_keys=True).encode() + b"\n" for row in rows)

        def bundle(kind):
            receipt = s.read(base / kind / s.RECEIPT)
            return base / kind / receipt["bundle"], receipt

        def terminal(kind):
            record = s.read(base / kind / s.rt.CUSTODY_NAME)
            return SimpleNamespace(kind=kind, started_epoch_s=record["started_epoch_s"],
                                   ended_epoch_s=record["ended_epoch_s"])

        # ---- the sensor journals: the frozen Sidecar derives every row ----
        journals = [("idle", base / "idle" / "sensors/align_thermal.jsonl", False)]
        for kind in (s.S, s.D, s.X):
            path, _ = bundle(kind)
            journals.append((kind, path / "outputs/align_thermal.jsonl", True))
        journals.append((s.S, base / s.S / "recovery/align_thermal.jsonl", False))
        for kind, path, gated in journals:
            rows = s.rows(path)
            source = str(path.relative_to(path.parents[1]))

            def sidecar(mutated, kind=kind, source=source, gated=gated):
                return lambda: pc._validate_sidecar(mutated, sensors, kind, source, gated=gated)

            expect("sidecar.session", f"{kind} clean", sidecar(rows), clean=True)
            readings = [i for i, row in enumerate(rows) if row["kind"] == "reading"]
            gates = [i for i, row in enumerate(rows) if row["kind"] in ("align_thermal_gate", "align_thermal_hold")]
            picks = sorted({0, readings[0], readings[len(readings) // 2], readings[-1], len(rows) - 1,
                            *gates[:2]})

            def mutate(entry, label, change):
                mutated = copy.deepcopy(rows)
                change(mutated)
                expect(entry, f"{kind} {path.name} {label}", sidecar(mutated))

            opening = rows[0]["started"]["monotonic_ns"]
            for delta in (1, -1):
                mutate("sidecar.session", f"every row align-{opening}{delta:+d}ns",
                       lambda rows, delta=delta: [row.update(session=f"align-{opening + delta}") for row in rows])
            for i in picks:
                mutate("sidecar.session", f"row {i}", lambda rows, i=i: rows[i].update(session=rows[i]["session"] + "0"))
                mutate("sidecar.seq", f"row {i}", lambda rows, i=i: rows[i].update(seq=rows[i]["seq"] + 1))
                for key in ("schema", "module"):
                    mutate("sidecar.schema_module", f"row {i} {key}", lambda rows, i=i, key=key: rows[i].update(
                        {key: rows[i][key] + "x"}))
                mutate("sidecar.error", f"row {i}", lambda rows, i=i: rows[i].update(
                    error=(rows[i]["error"] or "") + "x"))
                mutate("sidecar.raw", f"row {i}", lambda rows, i=i: rows[i].update(raw=["x"]))
            for i in readings[:1] + readings[-1:]:
                key = sensors["s_slow"]
                mutate("sidecar.reading_projection", f"row {i} units", lambda rows, i=i: rows[i]["values"]["units"].update(
                    {key: "raw"}))
                mutate("sidecar.reading_projection", f"row {i} source", lambda rows, i=i: rows[i]["values"].update(
                    source="x"))
                # The projected value alone: the raw reading it is derived from stays as recorded.
                mutate("sidecar.reading_projection", f"row {i} projected sensor", lambda rows, i=i: rows[i]["values"][
                    "sensors"].update({key: (rows[i]["values"]["sensors"][key] or 0.0) + 0.001}))
                mutate("sidecar.reading_projection", f"row {i} extra error",
                       lambda rows, i=i: rows[i]["values"]["errors"].update({key: "x"}))
            mutate("sidecar.thermal_policy", "session_start", lambda rows: rows[0]["values"]["thermal"].update(x=1))
            for i in [0, *gates[:2]]:
                mutate("sidecar.boundary_stamp", f"row {i}", lambda rows, i=i: rows[i]["finished"].update(
                    monotonic_ns=rows[i]["finished"]["monotonic_ns"] + 1))
            coverage = rows[-1]["values"]["coverage"]
            for field, value in coverage.items():
                if type(value) in (int, float) and not isinstance(value, bool):
                    mutate("sidecar.coverage", field, lambda rows, field=field: rows[-1]["values"]["coverage"].update(
                        {field: rows[-1]["values"]["coverage"][field] + (1 if type(value) is int else 0.001)}))
            mutate("sidecar.collector_error", "session_end", lambda rows: rows[-1]["values"].update(
                collector_error="x"))

        # ---- the gates: entry and exit views derived from the journal ----
        for kind in (s.S, s.D, s.X):
            path, _ = bundle(kind)
            episode = s.read(path / "outputs/align_episode.json")
            thermal = episode["hardware"]["thermal"]
            journal = s.rows(path / "outputs/align_thermal.jsonl")
            deadline = episode["hardware"]["token_budget"]["deadline_ns"]
            references = (thermal["window_reference"], thermal["episode_reference"])

            def gates(intervals, kind=kind, journal=journal, thermal=thermal, deadline=deadline, references=references):
                return lambda: pc._gate_findings(kind, journal, intervals, references, thermal["policy"], deadline)

            expect("gate.exit_slope", f"{kind} clean", gates(thermal["intervals"]), clean=True)
            starts = [r["monotonic_ns"] for r in s.tg.sample_rows(journal)]
            for index, interval in enumerate(thermal["intervals"]):
                def mutate(entry, label, change, index=index):
                    intervals = copy.deepcopy(thermal["intervals"])
                    change(intervals[index])
                    expect(entry, f"{kind} {interval['kind']}#{index} {label}", gates(intervals))

                for key in interval["entry_sensors"]:
                    if isinstance(interval["entry_sensors"][key], float):
                        mutate("gate.entry_sensors", key, lambda row, key=key: row["entry_sensors"].update(
                            {key: row["entry_sensors"][key] + 0.001}))
                slope = interval["entry_slope_c_per_min"]
                mutate("gate.entry_slope", "changed", lambda row: row.update(
                    entry_slope_c_per_min=0.0 if slope is None else slope + 0.001))
                at = starts.index(interval["exit_sample_ns"])
                for neighbour in (at - 1, at + 1):
                    if 0 <= neighbour < len(starts):
                        mutate("gate.exit_sample", f"row {neighbour}", lambda row, n=neighbour: row.update(
                            exit_sample_ns=starts[n]))
                mutate("gate.exit_sample", "null", lambda row: row.update(exit_sample_ns=None))
                for key in ("fast_c", "slow_c"):
                    mutate("gate.release", key, lambda row, key=key: row["release"].update(
                        {key: row["release"][key] + 0.001}))
                exit_slope = interval["slope_c_per_min"]
                for label, value in (("plus", None if exit_slope is None else exit_slope + 0.001), ("null", None),
                                     ("one million", 1e6)):
                    if value != exit_slope:
                        mutate("gate.exit_slope", label, lambda row, value=value: row.update(slope_c_per_min=value))
                for key in ("fast_c", "slow_c"):
                    if isinstance((interval["reference"] or {}).get(key), float):
                        mutate("gate.reference", key, lambda row, key=key: row["reference"].update(
                            {key: row["reference"][key] + 0.001}))
                mutate("gate.reference", "null", lambda row: row.update(reference=None))
                for word in ("timeout", "unobserved", "deadman"):
                    if word != interval["outcome"]:
                        mutate("gate.outcome", word, lambda row, word=word: row.update(outcome=word))

        # ---- the census: start then end, once each, around the samples ----
        for kind in ("idle", s.P, s.S, s.D, s.X):
            load = s.read(base / kind / "load_journal.json")
            receipt = s.read(base / kind / s.RECEIPT)
            census = load["census"]
            wall = None
            if kind in (s.P, s.S):
                window = terminal(kind)
                wall = window.ended_epoch_s - window.started_epoch_s
            elif kind == "idle":
                row = s.read(base / "soak" / "soak_row.json")
                wall = (row["ended_ns"] - row["started_ns"]) / s.N

            def loaded(points, kind=kind, load=load, receipt=receipt, wall=wall):
                journal = {**load, "census": points}
                claim = {**receipt, "census": points}
                return lambda: pc._check_load(json.dumps(journal).encode(), claim, kind, wall)

            expect("census.points", f"{kind} clean", loaded(census), clean=True)
            for key in ("cpu_busy_cores", "cpu_busy_t_s"):
                if load[key]:
                    claim = copy.deepcopy(receipt)
                    claim[key][-1] += 1
                    expect("load.fields", f"{kind} receipt {key}", lambda claim=claim, kind=kind, load=load, wall=wall:
                           pc._check_load(json.dumps(load).encode(), claim, kind, wall))
            # The structure each member must keep (``_check_census``): the quiet members both points; the soak
            # at least ``start``; the gated members any prefix of start, end.
            allowed = ([["start", "end"]] if kind in (s.P, s.S) else [["start"], ["start", "end"]] if kind == "idle"
                       else [[], ["start"], ["start", "end"]])
            point = {"t_s": census[0]["t_s"] if census else 0.0, "processes": census[0]["processes"] if census else []}
            start, end = {**point, "label": "start"}, {**point, "label": "end", "t_s": point["t_s"]}
            variants = {"end omitted": census[:-1], "end twice": census + census[-1:],
                        "start twice": census[:1] + census, "start omitted": census[1:],
                        "reversed": census[::-1], "relabelled": [*census[:-1], *[{**p, "label": "stop"} for p in census[-1:]]],
                        "end alone": [end], "end then start": [end, start], "start twice alone": [start, start]}
            for label, points in variants.items():
                if [p["label"] for p in points] not in allowed:
                    expect("census.points", f"{kind} {label}", loaded(points))
            if len(census) == 2:
                late = [census[0], {**census[1], "t_s": census[0]["t_s"] - 1}]
                expect("census.order", f"{kind} end before start", loaded(late))
                if load["cpu_busy_t_s"]:
                    short = [census[0], {**census[1], "t_s": census[0]["t_s"] + (
                        load["cpu_busy_t_s"][-1] - load["cpu_busy_t_s"][0]) - 1}]
                    expect("census.order", f"{kind} span shorter than the samples", loaded(short))

        # ---- the windows ----
        for kind in (s.P, s.S, s.D, s.X):
            path, receipt = bundle(kind)
            data = {name: (path / name).read_bytes() for name in (
                "events.jsonl", "outputs/align_episode.json", "outputs/align_turns.jsonl")}
            if kind != s.P:
                data["outputs/align_thermal.jsonl"] = (path / "outputs/align_thermal.jsonl").read_bytes()
            if kind == s.S:
                data["recovery/align_thermal.jsonl"] = (base / kind / "recovery/align_thermal.jsonl").read_bytes()
            window = terminal(kind)

            def windowed(bound, claim=receipt, data=data):
                return lambda: pc._check_member_window(bound, claim, data)

            expect("window.member", f"{kind} clean", windowed(window), clean=True)
            span = window.ended_epoch_s - window.started_epoch_s
            for label, started, ended in (("closed one second after opening", window.started_epoch_s,
                                           window.started_epoch_s + 1),
                                          ("opened one second before closing", window.ended_epoch_s - 1,
                                           window.ended_epoch_s),
                                          ("shifted later by its span", window.started_epoch_s + span,
                                           window.ended_epoch_s + span)):
                expect("window.member", f"{kind} {label}", windowed(SimpleNamespace(
                    kind=kind, started_epoch_s=started, ended_epoch_s=ended)))
            if kind == s.S:
                wall = receipt["slot_detail"]["member_wall_s"]
                expect("window.step_wall", "member wall one second over the bracket", windowed(
                    window, {**receipt, "slot_detail": {**receipt["slot_detail"], "member_wall_s": span + 1}}))
                expect("window.step_wall", "bracket one second under the member wall", windowed(SimpleNamespace(
                    kind=kind, started_epoch_s=window.ended_epoch_s - wall + 1, ended_epoch_s=window.ended_epoch_s)))

        soak_rows = s.rows(base / "idle" / "sensors/align_thermal.jsonl")
        soak_receipt = s.read(base / "idle" / s.RECEIPT)
        soak_window = terminal("idle")
        expect("window.soak", "clean", lambda: pc._check_soak_window(soak_window, soak_receipt, soak_rows), clean=True)
        for label, bound, claim in (
                ("closed one second after opening", SimpleNamespace(kind="idle", started_epoch_s=soak_window.started_epoch_s,
                                                                    ended_epoch_s=soak_window.started_epoch_s + 1),
                 soak_receipt),
                ("opened one second before closing", SimpleNamespace(kind="idle",
                                                                     started_epoch_s=soak_window.ended_epoch_s - 1,
                                                                     ended_epoch_s=soak_window.ended_epoch_s),
                 soak_receipt),
                ("duration one second over the session", soak_window,
                 {**soak_receipt, "duration_s": soak_receipt["duration_s"] + 1})):
            expect("window.soak", label, lambda bound=bound, claim=claim: pc._check_soak_window(bound, claim, soak_rows))
        raw_soak = (base / "idle" / "sensors/align_thermal.jsonl").read_bytes()
        expect("soak.series", "clean", lambda: pc._derive_soak(raw_soak, soak_receipt, sensors, soak_window), clean=True)
        for key in ("sensor_series_end_t_s",):
            expect("soak.series", key, lambda key=key: pc._derive_soak(
                raw_soak, {**soak_receipt, key: soak_receipt[key] + 1}, sensors, soak_window))
        slow = sensors["s_slow"]
        for key in ("sensor_series_c", "sensor_series_t_s"):
            claim = copy.deepcopy(soak_receipt)
            claim[key][slow][-1] += 0.5
            expect("soak.series", f"{key} last {slow}", lambda claim=claim: pc._derive_soak(
                raw_soak, claim, sensors, soak_window))
        claim = copy.deepcopy(soak_receipt)
        claim["sensor_series_failed_reads"][slow] += 1
        expect("soak.series", "sensor_series_failed_reads", lambda: pc._derive_soak(raw_soak, claim, sensors, soak_window))

    for name in INVENTORY:
        print("SWEEP", name, generated[name], refused[name], flush=True)
        if not generated[name]:
            failures.append(f"{name}: no mutation generated")
    for failure in failures:
        print("FAIL", failure, flush=True)
    print("TOTAL", sum(generated.values()), "generated", sum(refused.values()), "refused", len(failures), "failures",
          flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run())
