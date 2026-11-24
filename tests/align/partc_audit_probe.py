"""Audit reproductions for the Part C evaluator, driven through the synthetic launcher.

The reproductions are audit 2's `semantic_probe.py`, rewritten as a regression runner. It loads the frozen
differential suite by path, uses the suite's own clean control, and changes one input before a member's
producer closes. Each damaged attempt must end `other_failure` with its expected reason. Where the frozen
workload disagrees with the damage, the probe first confirms that disagreement itself, so each case is a
contradiction of the frozen code and not only of the evaluator's own rules.

Two cases are positives and must pass: the clean control, and RL-193 section 1's supplement, a predecessor
trace that is the six-column D-018 interval header with zero rows.

The audit of 2026-11-21 (pl-809 audit 1) adds its five reproductions, each with the control that separates it
from a valid input. Four were false passes: an X_G G1 entry whose sensors and slope come from two different
views of the journal (`x-g-gate-entry-mixed`; `x-g-gate-entry-matched` must pass), a Step D segment closed
before its member wall (`step-d-close-5179`) or its last recovery reading (`step-d-close-before-recovery`), a
duplicate key in an issued template (`issued-template-duplicate-key`), and an issued config that names the
synthetic backend under production receipts (`issued-config-backend-synthetic`). One was a false refusal: a
coherent one-second offset between the epoch and monotonic clocks (`clock-offset-coherent-*` must pass for the
predecessor, D_bank with its tool calls and context checks, and X_G; `clock-offset-incoherent-predecessor`
moves the events alone and must refuse). Step D is not shifted here: its reference record and journal are bound
by digest into the later members' custody, which a one-member edit cannot keep consistent.

Audit 2 of 2026-11-21 adds four false passes, each a recorded value that frozen R1 derives from a raw record:
the idle soak's terminal closed one second after it opened (`idle-closed-one-second`), the quiet predecessor's
census without its closing point, with it twice, or reversed (`predecessor-census-*`), an unobserved X_G G1 whose
exit slope contradicts the frozen reducer on the same view (`x-g-unobserved-exit-slope-contradicted`; the same
gate recording the derived value, `x-g-unobserved-exit-slope-derived`, must pass), and an X_G journal whose session
ID is not the one its opening stamp derives (`x-g-session-id-plus-one`).

Fix round r2 (wide audit round 1 of 2026-11-22) adds ``R2``: the FO and IN reproductions F1 to F11, each damaged
case with its paired control. Its four rule classes are R1 temporal containment (CPU samples, census, soak tail and
load, battery rows), R2 raw-domain schemas (busy cores, process tables and PIDs, endpoint identities, finish
reasons), R3 the complete census and R4 the runtime config resolved once.

    python3.13 -IB tests/align/partc_audit_probe.py [case ...]      (JW_PARTC_REPO selects the tree under test)

It prints one `RESULT <case> <verdict> <reasons>` line and one `FIELDS <case> <reason:field ...>` line per case and
exits 1 on any disagreement (JW_PARTC_PROBE_LOG=1 also prints each refusal's record). The pinned
commits must be in the local object database (see the suite's docstring).
"""
import hashlib
import importlib.util
import os
import shutil
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

SUITE = Path(__file__).resolve().parent / "test_partc_frozen_differential.py"
EXPECTED = {
    "control": None,
    "interval-header-zero-rows": None,
    "raw-runner-fault": "workload_replay",
    "raw-turn-budget-flag": "workload_replay",
    "last-turn-unclosed": "workload_replay",
    "other-run-id": "execution_config",
    "duplicate-predecessor": "sequence",
    "predecessor-timeout": "gate_cardinality",
    "extra-stop-flag": "flag_source",
    "gate-before-entry": "gate_journal_disagreement",
    "finalized-after-close": "member_order",
    # pl-809 audit 1 (2026-11-21). A tuple also names the finding's field.
    "x-g-gate-entry-matched": None,
    "x-g-gate-entry-mixed": ("evidence_unverifiable", "N5.entry"),
    "step-d-close-5179": "member_order",
    "step-d-close-before-recovery": "member_order",
    "issued-template-duplicate-key": ("issued_inputs", "strict_parse"),
    "issued-config-backend-synthetic": ("issued_identity", "backend"),
    "clock-offset-coherent-predecessor": None,
    "clock-offset-coherent-d-bank": None,
    "clock-offset-coherent-x-g": None,
    "clock-offset-incoherent-predecessor": ("turn_boundary_recompute", "paired_clock"),
    # Audit 2 of 2026-11-21.
    "idle-closed-one-second": "member_order",
    "predecessor-census-end-omitted": ("quiet_load", "census"),
    "predecessor-census-end-twice": ("quiet_load", "census"),
    "predecessor-census-reversed": ("quiet_load", "census"),
    "x-g-unobserved-exit-slope-derived": None,
    "x-g-unobserved-exit-slope-contradicted": ("evidence_unverifiable", "N5.exit_slope"),
    "x-g-session-id-plus-one": ("sidecar_derivation", "session"),
    # RL-186's member wall bound alone, judged directly: no synthetic journal can isolate it.
    "step-d-member-wall-over-bracket": ("member_order", "member_wall_s"),
    # The episode's two paired stamps in reverse order, both inside the bracket (v3.1's predecessor
    # `paired_clock_stamps_ns.0.epoch_ns/shift`, which a first draft of the window check let through).
    "episode-stamps-reversed": ("member_order", "episode_bracket"),
}
# Fix round r2 (wide audit round 1 of 2026-11-22). Each damaged case refuses; each control passes.
R2 = {
    # F1 (R1): CPU samples that cannot lie inside the census.
    "census-enclosure-disjoint": "member_order",
    "census-enclosure-too-narrow": ("evidence_unverifiable", "cpu_busy_t_s"),
    "census-literal": "member_order",
    "cpu-negative-offsets": ("evidence_unverifiable", "cpu_busy_t_s"),
    # F2, F3 (R1): the soak's tail and load judged against its own session.
    "soak-tail-missing": "soak_readings",
    "soak-short-load": ("soak_load", "cpu_busy_t_s"),
    # F4 (R1): repeated t=0 samples, cool and hot.
    "cpu-instant": ("quiet_load", "cpu_busy_t_s"),
    "cpu-hot": "quiet_load",
    # F5 (R1): battery rows outside the member.
    "battery-row-ordered": None,
    "battery-row-outside": ("battery_evidence", "epoch_s"),
    "battery-journal-shifted": ("battery_evidence", "epoch_s"),
    "battery-reduced": ("battery_evidence", "epoch_s"),
    # F6 (R2): endpoint identities that are not one nonempty string in both records.
    "endpoint-list": ("episode_binding", "endpoint"),
    "endpoint-mixed-type": ("episode_binding", "endpoint"),
    "endpoint-integer-pair": ("episode_binding", "endpoint"),
    "endpoint-boolean-pair": ("episode_binding", "endpoint"),
    "endpoint-array-pair": ("episode_binding", "endpoint"),
    "endpoint-one-copy": ("episode_binding", "endpoint"),
    # F7 (R2): the own-stop exception for a clean finish only.
    "ownstop-short-clean": None,
    "ownstop-short-cut": ("member_cut", "finish_reason"),
    "stop-cut": ("member_cut", "finish_reason"),
    "stop-unknown": "stop_evidence",
    "stop-deadman": ("member_cut", "finish_reason"),
    # F8, F9 (R2): busy cores, process tables and PIDs.
    "cpu-negative": ("quiet_load", "cpu_busy_cores.0"),
    "process-empty": ("quiet_load", "census.0.processes"),
    "census-pid-distinct": None,
    "census-pid-conflicting": ("quiet_load", "census.0.processes.pid"),
    "census-pid-duplicate-row": ("quiet_load", "census.0.processes.pid"),
    # F10 (R3): every completed member's census is start then end.
    "census-complete": None,
    "census-omit-idle": ("soak_load", "census"),
    "census-omit-d-bank-benign-s1": ("load_evidence", "census"),
    "census-omit-x-g": ("load_evidence", "census"),
    # F11 (R4): the runtime config the ledgers record is the one the child consumes.
    "config-separate": None,
    "config-equals": ("issued_inputs", "--config"),
    "config-repeated": ("issued_inputs", "--config"),
}
EXPECTED.update(R2)
# Fix round r3 (confirmation audit of 2026-11-23). Each damaged case refuses; each control passes.
R3 = {
    # A derivation at the bound session close is a verdict: the soak's tail must be settled there too.
    "soak-close-settled": None,
    "soak-close-unsettled": ("soak_unsettled", "session_close"),
    # Launch order on the monotonic clock: the predecessor's CPU origin lies after the soak closed.
    "origin-control": None,
    "origin-during-soak": ("evidence_unverifiable", "cpu_busy_t_s"),
    "origin-negative": ("evidence_unverifiable", "cpu_busy_t_s"),
    # Nested observation stamps lie no later than the next row (producer order) and the session close.
    "status-control": None,
    "status-future": ("reading_record", "values.status.monotonic_ns"),
    "status-pm-future": ("reading_record", "values.status.pm_observed_ns"),
    # Structural completeness: the opening and closing battery samples Segment.run takes.
    "closing-battery-kept": None,
    "closing-battery-dropped": ("battery_evidence", "samples"),
    # Exactly the one excluded PID Segment.__init__ passes.
    "roots-single": None,
    "roots-repeated": ("quiet_load", "exclude_roots"),
    "roots-empty": ("quiet_load", "exclude_roots"),
}
EXPECTED.update(R3)
DIRECT = ("step-d-member-wall-over-bracket", "episode-stamps-reversed")
AUDIT_2 = ("control", "interval-header-zero-rows", "raw-runner-fault", "raw-turn-budget-flag", "last-turn-unclosed",
           "other-run-id", "duplicate-predecessor", "predecessor-timeout", "extra-stop-flag", "gate-before-entry",
           "finalized-after-close")
AUDIT_2026_11_21 = tuple(name for name in EXPECTED if name not in AUDIT_2)


def member_wall(s, wall, opened=4_001_000_000_000, closed=4_002_000_000_000):
    """Step D's window with every recorded instant inside it, and the receipt's member wall ``wall``."""
    import json
    from types import SimpleNamespace

    bound = SimpleNamespace(kind=s.S, started_epoch_s=4000.0, ended_epoch_s=5180.0)
    stamps = [{"epoch_ns": opened}, {"epoch_ns": closed}]
    data = {"events.jsonl": json.dumps({"timestamp_s": 4001.0}).encode() + b"\n",
            "outputs/align_episode.json": json.dumps({"hardware": {"paired_clock_stamps_ns": stamps}}).encode(),
            "outputs/align_turns.jsonl": b""}
    s.pc._check_member_window(bound, {"slot_detail": {"member_wall_s": wall}}, data)


def load_suite():
    spec = importlib.util.spec_from_file_location("partc_suite", SUITE)
    suite = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = suite
    spec.loader.exec_module(suite)
    return suite


def shift_epoch(value, seconds):
    """Move every epoch-clock value in a record by ``seconds``. Monotonic values are left where they are."""
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if key in ("wall_ns", "span_epoch_ns") or key.endswith("epoch_ns"):
                out[key] = ([part + round(seconds * 1e9) for part in item] if isinstance(item, list)
                            else item + round(seconds * 1e9) if type(item) is int else shift_epoch(item, seconds))
            elif key.endswith("epoch_s") or key == "timestamp_s" or key.startswith("wall_minus_monotonic_"):
                out[key] = item + seconds if type(item) in (int, float) else shift_epoch(item, seconds)
            else:
                out[key] = shift_epoch(item, seconds)
        return out
    if isinstance(value, list):
        return [shift_epoch(item, seconds) for item in value]
    return value


def run(argv):
    s = load_suite()
    wanted = argv or list(EXPECTED)
    changed_member = {"raw-runner-fault": s.D, "raw-turn-budget-flag": s.D, "last-turn-unclosed": s.D,
                      "other-run-id": s.X, "duplicate-predecessor": s.S, "predecessor-timeout": s.P,
                      "extra-stop-flag": s.P, "gate-before-entry": s.D, "finalized-after-close": s.D,
                      "interval-header-zero-rows": s.P, "control": None,
                      "x-g-gate-entry-matched": s.X, "x-g-gate-entry-mixed": s.X,
                      "step-d-close-5179": None, "step-d-close-before-recovery": None,
                      "issued-template-duplicate-key": None, "issued-config-backend-synthetic": None,
                      "clock-offset-coherent-predecessor": s.P, "clock-offset-coherent-d-bank": s.D, "clock-offset-coherent-x-g": s.X,
                      "clock-offset-incoherent-predecessor": s.P,
                      "idle-closed-one-second": None, "predecessor-census-end-omitted": s.P,
                      "predecessor-census-end-twice": s.P, "predecessor-census-reversed": s.P,
                      "x-g-unobserved-exit-slope-derived": s.X, "x-g-unobserved-exit-slope-contradicted": s.X,
                      "x-g-session-id-plus-one": s.X}
    changed_member.update({name: s.P for name in R2})
    changed_member.update({name: "idle" for name in ("soak-tail-missing", "soak-short-load", "census-omit-idle")})
    changed_member.update({name: s.S for name in ("battery-reduced",)})
    changed_member.update({name: s.D for name in ("ownstop-short-clean", "ownstop-short-cut", "stop-cut",
                                                  "stop-unknown", "stop-deadman", "census-omit-d-bank-benign-s1")})
    changed_member.update({"census-omit-x-g": s.X, "census-complete": None, "config-separate": None,
                           "config-equals": None, "config-repeated": None})
    changed_member.update({name: s.P for name in R3})
    changed_member.update({"soak-close-settled": "idle", "soak-close-unsettled": "idle", "status-control": s.X,
                           "status-future": s.X, "status-pm-future": s.X})

    def mutate_r3(case, kind, segment, receipt):
        """The r3 reproductions (confirmation audit's bound_tail, regressions and status_cases scripts)."""
        load_path = segment / "load_journal.json"
        if case.startswith("soak-close-"):
            from joulewise.align.apple.thermal import Coverage, keys

            path = segment / "sensors/align_thermal.jsonl"
            records = s.rows(path)
            start, close = records[0], records[-1]
            sensors = start["values"]["thermal"]
            kept = [row for row in records if row["kind"] == "reading"][:1701]
            # A flat baseline, then a linear rise whose slope over the window at the close straddles 0.2 C/min.
            amplitude, key = (0.201 if case.endswith("unsettled") else 0.19), sensors["s_fast"]
            for index, row in enumerate(kept):
                value = 35.0 + amplitude * max(index - 600, 0) / 60
                row["values"]["sensors"][key] = row["values"]["readings"][key]["value"] = value
            sampling = s.tg.sample_rows(kept)
            origin = sampling[0]["monotonic_ns"]
            coverage = Coverage(start["started"]["monotonic_ns"], keys(sensors))
            for row in kept:
                coverage.observe(row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"], row["values"])
            close["values"]["coverage"] = coverage.report(close["values"]["coverage"]["span_ns"][1])
            close["seq"] = len(kept) + 2
            s.write_rows(path, [start, *kept, close])
            for name in (sensors["s_fast"], sensors["s_slow"]):
                good = s.rt.valid_series(sampling, name)
                receipt["sensor_series_c"][name] = [v for _, v in good]
                receipt["sensor_series_t_s"][name] = [(ns - origin) / s.N for ns, _ in good]
                receipt["sensor_series_failed_reads"][name] = len(kept) - len(good)
            receipt["sensor_series_end_t_s"] = round((sampling[-1]["monotonic_ns"] - origin) / s.N, 9)
        elif case.startswith("origin-"):
            load = s.read(load_path)
            delay = {"origin-control": 0, "origin-during-soak": 500, "origin-negative": 4000}[case]
            load["cpu_busy_t_s"] = receipt["cpu_busy_t_s"] = [t + delay for t in load["cpu_busy_t_s"]]
            s.write(load_path, load)
        elif case.startswith("roots-"):
            load = s.read(load_path)
            valid = load["census"][0]["processes"][0]["pid"]
            load["exclude_roots"] = {"roots-single": [valid], "roots-repeated": [valid, valid], "roots-empty": []}[case]
            s.write(load_path, load)
        elif case.startswith("closing-battery-"):
            path = segment / s.pc.BATTERY_SOURCE
            rows = s.rows(path)
            assert len(rows) == 2
            if case.endswith("dropped"):
                rows.pop()
            receipt["battery"] = s.rt.battery_summary(rows)
            if "battery_drain_pct_per_h" in receipt:
                receipt["battery_drain_pct_per_h"] = receipt["battery"]["drain_pct_per_h"]
            s.write_rows(path, rows)
        elif case.startswith("status-"):
            journal = segment / receipt["bundle"] / "outputs/align_thermal.jsonl"
            rows = s.rows(journal)
            row = [r for r in rows if r["kind"] == "reading" and r["values"].get("status")][1]
            key = "pm_observed_ns" if "-pm-" in case else "monotonic_ns"
            if case != "status-control":
                row["values"]["status"][key] = rows[-1]["finished"]["monotonic_ns"] + 60 * s.N
                s.write_rows(journal, rows)
        else:
            return False
        return True

    def mutate_r2(case, kind, segment, receipt):
        """The r2 reproductions (wide audit FO and IN scripts), one change before the member's producer closes."""
        import copy

        bundle = segment / receipt["bundle"] if "bundle" in receipt else None
        load_path = segment / "load_journal.json"
        if case.startswith("census-omit-"):
            load = s.read(load_path)
            load["census"] = receipt["census"] = load["census"][:1]
            s.write(load_path, load)
        elif case.startswith(("census-enclosure-", "census-literal", "cpu-")):
            load = s.read(load_path)
            times, census = load["cpu_busy_t_s"], load["census"]
            assert ([point["t_s"] for point in census], times[0], times[-1]) == ([2000, 3800], 0, 1800)
            width = times[-1] - times[0]
            if case == "census-enclosure-disjoint":
                times = [500 + t for t in times]
                census[0]["t_s"], census[1]["t_s"] = 0, width
            elif case == "census-enclosure-too-narrow":
                census[1]["t_s"] = census[0]["t_s"] + width - 1
            elif case == "census-literal":
                census[0]["t_s"], census[1]["t_s"] = 0, 100
                times = [500 + t / 20 for t in times]
            elif case == "cpu-negative-offsets":
                times = [t - 2000 for t in times]
            elif case == "cpu-instant":
                times = [0] * len(times)
            elif case in ("cpu-hot", "cpu-negative"):
                load["cpu_busy_cores"] = [3 if case == "cpu-hot" else -10] * len(times)
            load["cpu_busy_t_s"] = times
            for key in ("cpu_busy_t_s", "cpu_busy_cores", "census"):
                receipt[key] = load[key]
            s.write(load_path, load)
        elif case == "process-empty":
            load = s.read(load_path)
            for point in load["census"]:
                point["processes"] = []
            receipt["census"] = load["census"]
            s.write(load_path, load)
        elif case.startswith("census-pid-"):
            load = s.read(load_path)
            processes = load["census"][0]["processes"]
            original = processes[0]
            second = dict(original, pid=max(row["pid"] for row in processes) + 1 if case.endswith("distinct")
                          else original["pid"])
            if not case.endswith("duplicate-row"):
                second["comm"] = "another-fixture-process"
            processes.append(second)
            receipt["census"] = load["census"]
            s.write(load_path, load)
        elif case.startswith("battery-"):
            path = segment / s.pc.BATTERY_SOURCE
            rows = s.rows(path)
            if case.startswith("battery-row-"):
                assert [row["epoch_s"] for row in rows] == [2000, 2120]
                rows.insert(1, dict(rows[0], epoch_s=2060))
                receipt["battery"] = s.rt.battery_summary(rows)
                if case == "battery-row-outside":
                    rows[1]["epoch_s"] = 6100
                assert s.encode(receipt["battery"]) == s.encode(s.rt.battery_summary(rows))   # receipt unchanged
            else:
                shift = {"battery-journal-shifted": None, "battery-reduced": 1_000_000}[case]
                rows = [dict(row, epoch_s=6100 + index if shift is None else row["epoch_s"] + shift)
                        for index, row in enumerate(rows)]
                receipt["battery"] = s.rt.battery_summary(rows)
                if "battery_drain_pct_per_h" in receipt:
                    receipt["battery_drain_pct_per_h"] = receipt["battery"]["drain_pct_per_h"]
            s.write_rows(path, rows)
        elif case.startswith("endpoint-"):
            episode_path, meta_path = bundle / "outputs/align_episode.json", bundle / "metadata.json"
            episode, meta = s.read(episode_path), s.read(meta_path)
            provenance = meta["workload_provenance"]
            assert isinstance(episode["endpoint"], str) and episode["endpoint"] == provenance["endpoint_identity"]
            value = {"endpoint-list": [17], "endpoint-mixed-type": True, "endpoint-integer-pair": 17,
                     "endpoint-boolean-pair": True, "endpoint-array-pair": ["id"], "endpoint-one-copy": True}[case]
            episode["endpoint"] = value
            if case != "endpoint-one-copy":
                provenance["endpoint_identity"] = 1 if case == "endpoint-mixed-type" else copy.deepcopy(value)
            s.write(episode_path, episode)
            s.write(meta_path, meta)
        elif case.startswith(("ownstop-", "stop-")):
            path = bundle / "outputs/align_turns.jsonl"
            turns = s.rows(path)
            generation = turns[-1]["generation"]
            assert generation["finish_reason"] == "stop"
            assert (len(turns) == 2) == case.startswith("ownstop-")
            generation["finish_reason"] = {"ownstop-short-clean": "stop", "ownstop-short-cut": "episode.time_guard",
                                           "stop-cut": "episode.time_guard", "stop-unknown": "synthetic.unknown_stop",
                                           "stop-deadman": "episode.deadman"}[case]
            s.write_rows(path, turns)
        elif case == "soak-tail-missing":
            from joulewise.align.apple.thermal import Coverage, keys

            path = segment / "sensors/align_thermal.jsonl"
            records = s.rows(path)
            start, close = records[0], records[-1]
            sensors = start["values"]["thermal"]
            kept = [row for row in records if row["kind"] == "reading"][:1201]
            sampling = s.tg.sample_rows(kept)
            origin = sampling[0]["monotonic_ns"]
            coverage = Coverage(start["started"]["monotonic_ns"], keys(sensors))
            for row in kept:
                coverage.observe(row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"], row["values"])
            close["values"]["coverage"] = coverage.report(close["values"]["coverage"]["span_ns"][1])
            close["seq"] = len(kept) + 2
            s.write_rows(path, [start, *kept, close])
            for key in (sensors["s_fast"], sensors["s_slow"]):
                good = s.rt.valid_series(sampling, key)
                receipt["sensor_series_c"][key] = [value for _, value in good]
                receipt["sensor_series_t_s"][key] = [(ns - origin) / s.N for ns, _ in good]
                receipt["sensor_series_failed_reads"][key] = len(kept) - len(good)
            receipt["sensor_series_end_t_s"] = round((sampling[-1]["monotonic_ns"] - origin) / s.N, 9)
        elif case == "soak-short-load":
            load = s.read(load_path)
            for key in ("cpu_busy_cores", "cpu_busy_t_s"):
                load[key] = receipt[key] = load[key][:5]
            s.write(load_path, load)
        else:
            return False
        return True

    def frozen_refuses(segment, kind):
        try:
            s.check_workload(segment, kind)
        except (s.Disagreement, s.wl.AdapterFailure):
            return True
        return False

    def gate_entry(bundle, kind, mixed):
        """The auditor's paired G1 entry: one reading finishes inside the visibility window of X_G's first G1,
        so the surely and the possibly visible views differ in both the entry sensors and the entry slope. The
        matched claim takes both from one view; the mixed claim takes the sensors from the other."""
        import copy

        from joulewise.align.apple.thermal import Coverage, keys

        episode_path, journal_path = bundle / "outputs/align_episode.json", bundle / "outputs/align_thermal.jsonl"
        episode, journal, events = s.read(episode_path), s.rows(journal_path), s.rows(bundle / "events.jsonl")
        interval = episode["hardware"]["thermal"]["intervals"][1]
        policy = episode["hardware"]["thermal"]["policy"]
        start, key = interval["start_ns"], policy["sensors"]["s_slow"]
        row, = [r for r in journal if r["kind"] == "reading" and r["started"]["monotonic_ns"] == start]
        for clock in ("monotonic_ns", "monotonic_raw_ns", "wall_ns"):
            row["started"][clock] -= 1
        row["values"]["sensors"][key] += 0.001
        row["values"]["readings"][key]["value"] = row["values"]["sensors"][key]
        journal.sort(key=lambda r: r["started"]["monotonic_ns"])
        for seq, r in enumerate(journal, 1):
            r["seq"] = seq
        coverage = Coverage(journal[0]["started"]["monotonic_ns"], keys(journal[0]["values"]["thermal"]))
        for r in journal:
            if r["kind"] == "reading":
                coverage.observe(r["started"]["monotonic_ns"], r["finished"]["monotonic_ns"], r["values"])
        close = journal[-1]["values"]
        close["coverage"] = coverage.report(close["coverage"]["span_ns"][1])
        window = s.GateWindow(s.tg.sample_rows(journal), policy["sensors"])
        sure, possible = window.count(start, True), window.count(start)
        assert possible == sure + 1

        def view(count):
            return (s.tg.ThermalSession._entry_values(s.NSpace(rows=window.samples[:count]), start),
                    window.slope(start, count))

        definite, maybe = view(sure), view(possible)
        assert definite[0] != maybe[0] and definite[1] != maybe[1]
        claim = (definite[0], maybe[1]) if mixed else maybe

        def assign():
            interval.update(entry_sensors=claim[0], entry_slope_c_per_min=claim[1])
            for r in journal:
                if r["values"].get("state") == "end" and r["values"]["gate"]["start_ns"] == start:
                    r["values"]["gate"] = copy.deepcopy(interval)
            for event in events:
                if event["phase"] == "align_thermal_gate" and event["metadata"].get("start_ns") == start:
                    event["metadata"] = copy.deepcopy(interval)

        assign()
        at = interval["exit_sample_ns"]
        interval["slope_c_per_min"] = window.slope(at, window.count(at))
        assign()
        s.write_rows(journal_path, journal)
        s.write_rows(bundle / "events.jsonl", events)
        s.write(episode_path, episode)
        try:
            s.observed_gates(bundle, s.wl.read_episode_bundle(bundle), kind)
            frozen = None
        except s.Disagreement as error:
            frozen = str(error)
        assert frozen == ("N5 entry" if mixed else None), frozen

    def unobserved_exit(bundle, contradicted):
        """An unobserved X_G G1: the frozen wait's exit slope is ``slow_slope`` on its final view. The derived case
        records that value in every copy; the contradicted case records 1,000,000 instead."""
        episode_path, journal_path = bundle / "outputs/align_episode.json", bundle / "outputs/align_thermal.jsonl"
        episode, journal, events = s.read(episode_path), s.rows(journal_path), s.rows(bundle / "events.jsonl")
        gate, = [row for row in episode["hardware"]["thermal"]["intervals"] if row["outcome"] == "unobserved"]
        assert gate["kind"] == "G1"
        key = episode["hardware"]["thermal"]["policy"]["sensors"]["s_slow"]
        view = [row for row in s.tg.sample_rows(journal) if row["finished"]["monotonic_after_ns"] <= gate["end_ns"]]
        value = 1e6 if contradicted else s.tg.slow_slope(view, gate["end_ns"], key)
        assert value != 1e6 or contradicted
        copies = 0
        gate["slope_c_per_min"] = value
        for row in journal:
            if row["values"].get("state") == "end" and row["values"]["gate"].get("start_ns") == gate["start_ns"]:
                row["values"]["gate"]["slope_c_per_min"] = value
                copies += 1
        for event in events:
            if event["phase"] == "align_thermal_gate" and event["metadata"].get("start_ns") == gate["start_ns"]:
                event["metadata"]["slope_c_per_min"] = value
                copies += 1
        assert copies == 3
        s.write(episode_path, episode)
        s.write_rows(journal_path, journal)
        s.write_rows(bundle / "events.jsonl", events)

    def clock_offset(bundle, coherent):
        """One second between the epoch and monotonic clocks. Coherent: every epoch value moves, the endpoint's
        turn mappings are re-derived with the frozen ``stamp_mapping`` and reproduce each first token. Incoherent:
        the controller events move and nothing else does."""
        from joulewise.align.apple.sampler import seconds_ns, stamp_mapping

        seconds = 1.0
        events = [shift_epoch(event, seconds) for event in s.rows(bundle / "events.jsonl")]
        s.write_rows(bundle / "events.jsonl", events)
        if not coherent:
            # The frozen endpoint's conversion now misses every recorded first token by the offset.
            episode = s.read(bundle / "outputs/align_episode.json")
            for turn, row in zip(episode["turns"], s.rows(bundle / "outputs/align_turns.jsonl"), strict=True):
                mapping, _ = stamp_mapping(tuple(s.ClockStamp(**row[k]) for k in ("start_stamp", "end_stamp")),
                                           episode_domain=episode["clock_domain"])
                prefill, = [e for e in events if e["event_type"] == "phase_end" and e["phase"] == "prefill"
                            and e["metadata"]["align_turn_index"] == turn["index"]]
                assert seconds_ns(prefill["timestamp_s"]) + mapping.offset_ns != turn["first_token_ns"]
            return
        for name in ("outputs/align_episode.json", "metadata.json", "outputs/align_window_reference.json"):
            if (bundle / name).is_file():
                s.write(bundle / name, shift_epoch(s.read(bundle / name), seconds))
        for name in ("outputs/align_thermal.jsonl", "rich_telemetry.jsonl"):
            if (bundle / name).is_file():
                s.write_rows(bundle / name, [shift_epoch(row, seconds) for row in s.rows(bundle / name)])
        trace = bundle / "power_trace.csv"
        lines = trace.read_text().splitlines()
        header = lines[0].split(",")
        moved = [lines[0]]
        for line in lines[1:]:
            fields = dict(zip(header, line.split(",")))
            for name in ("timestamp_s", "interval_start_s", "interval_end_s"):
                if fields.get(name):
                    fields[name] = repr(float(fields[name]) + seconds)
            moved.append(",".join(fields[name] for name in header))
        trace.write_text("\n".join(moved) + "\n")
        episode = s.read(bundle / "outputs/align_episode.json")
        turns = s.rows(bundle / "outputs/align_turns.jsonl")
        for turn, row in zip(episode["turns"], turns, strict=True):
            for stamp in (row["start_stamp"], row["end_stamp"]):
                stamp["epoch_s"] += seconds
            mapping, _ = stamp_mapping(tuple(s.ClockStamp(**row[k]) for k in ("start_stamp", "end_stamp")),
                                       episode_domain=episode["clock_domain"])
            row["clock_mapping"] = mapping.__dict__
            prefill, = [e for e in events if e["event_type"] == "phase_end" and e["phase"] == "prefill"
                        and e["metadata"]["align_turn_index"] == turn["index"]]
            assert mapping.offset_ns == -s.N
            assert seconds_ns(prefill["timestamp_s"]) + mapping.offset_ns == turn["first_token_ns"]
        s.write_rows(bundle / "outputs/align_turns.jsonl", turns)

    def mutate(case, kind, segment, receipt):
        if mutate_r3(case, kind, segment, receipt) or mutate_r2(case, kind, segment, receipt):
            return
        bundle = segment / receipt["bundle"]
        episode_path = bundle / "outputs/align_episode.json"
        turns_path = bundle / "outputs/align_turns.jsonl"
        episode = s.read(episode_path)
        if case.startswith("x-g-gate-entry-"):
            gate_entry(bundle, kind, mixed=case.endswith("mixed"))
        elif case.startswith("predecessor-census-"):
            load = s.read(segment / "load_journal.json")
            census = load["census"]
            assert [point["label"] for point in census] == ["start", "end"]
            census = {"end-omitted": census[:1], "end-twice": census + census[1:],
                      "reversed": census[::-1]}[case.removeprefix("predecessor-census-")]
            s.write(segment / "load_journal.json", {**load, "census": census})
            receipt["census"] = census                  # the receipt's copy agrees with the journal
        elif case.startswith("x-g-unobserved-exit-slope-"):
            unobserved_exit(bundle, contradicted=case.endswith("contradicted"))
        elif case == "x-g-session-id-plus-one":
            path = bundle / "outputs/align_thermal.jsonl"
            journal = s.rows(path)
            opening = journal[0]["started"]["monotonic_ns"]
            assert {row["session"] for row in journal} == {f"align-{opening}"}   # Sidecar.start derives it
            s.write_rows(path, [{**row, "session": f"align-{opening + 1}"} for row in journal])
        elif case.startswith("clock-offset-"):
            clock_offset(bundle, coherent="-coherent-" in case)
        elif case == "interval-header-zero-rows":
            from joulewise.bundle_read import POWER_TRACE_HEADER, POWER_TRACE_INTERVAL_HEADER, _check_power_trace

            trace = bundle / "power_trace.csv"
            assert trace.read_bytes().splitlines()[0].decode() == POWER_TRACE_HEADER
            trace.write_bytes((POWER_TRACE_INTERVAL_HEADER + "\n").encode("ascii"))
            assert _check_power_trace(bundle, s.read(bundle / "summary_metrics.json"),
                                      s.read(bundle / "metadata.json")) == [], "the pinned check refused it"
        elif case in ("last-turn-unclosed", "raw-turn-budget-flag", "raw-runner-fault"):
            turns = s.rows(turns_path)
            assert not episode["turns"][-1]["tool_calls"]
            flag = {"last-turn-unclosed": "unclosed_reasoning_span", "raw-turn-budget-flag": "turn_budget_reached",
                    "raw-runner-fault": "runner.error.synthetic"}[case]
            assert flag not in turns[-1]["flags"]
            turns[-1]["flags"].append(flag)
            s.write_rows(turns_path, turns)
            assert frozen_refuses(segment, kind), "the frozen workload agreed with the damage"
        elif case == "finalized-after-close":
            events_path = bundle / "events.jsonl"
            events = s.rows(events_path)
            close_epoch = s.EPOCH[kind] + 1800
            assert events[-1]["event_type"] == "run_finalized" and events[-1]["timestamp_s"] <= close_epoch
            events[-1]["timestamp_s"] = close_epoch + 1
            s.write_rows(events_path, events)
        elif case == "duplicate-predecessor":
            previous = segment.parent / s.pc.KINDS[s.P]
            extra = previous.with_name(s.r1._fresh_name(segment.parent, previous.name + ".rejected", 1))
            shutil.copytree(previous, extra)
            assert (extra / s.RECEIPT).is_file()
        elif case == "predecessor-timeout":
            assert "thermal" not in episode["hardware"]
            episode["hardware"]["thermal"] = {"intervals": [{"kind": "G0", "turn": 0, "outcome": "timeout"}],
                                              "flags": ["thermal.start_gate_timeout"]}
            s.write(episode_path, episode)
        elif case == "other-run-id":
            assert kind == s.X and bundle.name == "align-v4-r1-x-g"
            other = "align-v4-r1-d-bank-benign-s1"
            config = bundle / "config.json"
            original_digest = hashlib.sha256(config.read_bytes()).hexdigest()
            old, new = bundle.name.encode(), other.encode()
            for rel in ("config.json", "metadata.json", "outputs/align_episode.json", "outputs/align_turns.jsonl",
                        "events.jsonl", "outputs/align_thermal.jsonl"):
                path = bundle / rel
                raw = path.read_bytes()
                if old in raw:
                    path.write_bytes(raw.replace(old, new))
            meta = bundle / "metadata.json"
            meta.write_bytes(meta.read_bytes().replace(
                original_digest.encode(), hashlib.sha256(config.read_bytes()).hexdigest().encode()))
            bundle.rename(bundle.with_name(other))
            receipt["bundle"] = "runs/" + other
            assert s.planned_run_ids()[kind] != other
        elif case == "gate-before-entry":
            path = bundle / "outputs/align_thermal.jsonl"
            rows = s.rows(path)
            for position, row in enumerate(rows):
                if row["kind"] != "align_thermal_gate" or row["values"]["state"] != "begin":
                    continue
                bound = row["values"]["entry_stamp"]["monotonic_before_ns"]
                shift = row["started"]["monotonic_ns"] - (bound - 1_000_000)
                if shift <= 0 or any(row["started"][k] - shift < rows[position - 1]["finished"][k]
                                     for k in row["started"]):
                    continue
                for key in ("started", "finished"):
                    for clock in row[key]:
                        row[key][clock] -= shift
                s.write_rows(path, rows)
                return
            raise AssertionError("no usable synthetic gate bracket")
        elif case == "extra-stop-flag":
            assert not receipt.get("episode_flags")
            receipt["episode_flags"] = ["episode.deadman:0"]
        else:
            raise AssertionError(case)

    def issued_edit(name, stack):
        """Edit one issued file for this attempt only. Returns nothing; the stack restores the original."""
        conf = s.rt.ROOT / s.r1.DEFAULT_RUNTIME_CONFIG
        if name == "issued-config-backend-synthetic":
            raw = conf.read_bytes()
            assert raw.count(b'"production"') == 1
            conf.write_bytes(raw.replace(b'"production"', b'"synthetic"'))
            assert s.read(conf)["backend"] == "synthetic"
            stack.callback(conf.write_bytes, raw)
        elif name == "issued-template-duplicate-key":
            template = s.rt.resolve(s.read(conf)["templates"]["d_bank"])
            raw = template.read_bytes()
            assert raw.count(b'"idle_seconds":') == 1
            template.write_bytes(raw.replace(b'"idle_seconds":', b'"idle_seconds":0,"idle_seconds":'))
            assert s.read(template)["sampling"]["idle_seconds"] == 300     # the frozen reader keeps the last key
            stack.callback(template.write_bytes, raw)
        elif name.startswith("x-g-unobserved-exit-slope-"):
            # The fixture's X_G records its second gate unobserved; the frozen wait then flags the state.
            stack.enter_context(patch.dict(s.fixture.XG["intervals"][1], outcome="unobserved"))
        elif name == "idle-closed-one-second":
            writer = s.write

            def close_soak(path, value):
                if path.name == s.rt.CUSTODY_NAME and path.parent.name == "idle_soak" and value.get("ended_epoch_s") == 1800:
                    assert value["started_epoch_s"] == 0
                    rows = s.rows(path.parent / "sensors/align_thermal.jsonl")
                    assert max(row["finished"]["wall_ns"] for row in rows) > s.N     # the journal runs past it
                    value = dict(value, ended_epoch_s=1)
                return writer(path, value)

            stack.enter_context(patch.object(s, "write", close_soak))
        elif name.startswith("ownstop-"):
            # Wide audit FO ``ownstop.py``: a two-admission D_bank (RL-149), its last turn and interval dropped.
            import copy

            bank = copy.deepcopy(s.fixture.bank())
            bank["turns"].pop()
            bank["intervals"].pop()
            stack.enter_context(patch.object(s.fixture, "bank", return_value=bank))
        elif name.startswith("config-"):
            # Wide audit IN ``config_path.py``: the launcher's runtime argv names an equal copy of the config.
            fresh = s.new_fixture

            def fixture():
                case = fresh()
                config = case.attempt.config
                copied = config.parent / "copied-runtime.json"
                copied.write_bytes(config.read_bytes())
                case.runtime = ["synthetic-runtime", *{
                    "config-separate": ["--config", str(copied)], "config-equals": ["--config=" + str(copied)],
                    "config-repeated": ["--config", str(config), "--config", str(copied)]}[name]]
                return case

            stack.enter_context(patch.object(s, "new_fixture", fixture))
        elif name.startswith("step-d-close-"):
            writer = s.write

            def close_early(path, value):
                if (path.name == s.rt.CUSTODY_NAME and path.parent.name == s.pc.KINDS[s.S]
                        and value.get("ended_epoch_s") == 5800):
                    assert value["started_epoch_s"] == 4000
                    receipt = s.read(path.parent / s.RECEIPT)
                    recovery = s.rows(path.parent / "recovery/align_thermal.jsonl")[-1]["finished"]["wall_ns"] / s.N
                    end = 5179 if name == "step-d-close-5179" else recovery - 1
                    # The frozen suite's RL-186 bound refuses 5179; the recovery journal refuses the later close.
                    assert (end - 4000 < receipt["slot_detail"]["member_wall_s"]) == (name == "step-d-close-5179")
                    value = dict(value, ended_epoch_s=end)
                return writer(path, value)

            stack.enter_context(patch.object(s, "write", close_early))

    failures = []
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        finder = s.import_world(work / "src")
        for name in [name for name in wanted if name in DIRECT]:
            member_wall(s, 1180.0)                          # exactly the bracket, stamps in order: passes
            try:
                if name == "episode-stamps-reversed":
                    member_wall(s, 1000.0, opened=4_002_000_000_000, closed=4_001_000_000_000)
                else:
                    member_wall(s, 1180.5)
                found = set()
            except s.evidence.EvidenceFailure as error:
                found = {(error.reason, error.field)}
            print("RESULT", name, "other_failure" if found else "pass", ",".join(r for r, _ in found) or "-", flush=True)
            if EXPECTED[name] not in found:
                failures.append(name)
        wanted = [name for name in wanted if name not in DIRECT]
        s.MODEL_DIR = work / "synthetic-model"
        s.MODEL_DIR.mkdir()
        s.write(s.MODEL_DIR / "config.json", {"max_position_embeddings": 40960})
        s.issue_model_source()
        s.endpoint_code()
        with s.kit_source(finder), s.compact_control(), patch.object(
                s.rt, "registered_s6", return_value={"slots": {"S6": 1.}, "s6_tuning": {}}):
            for name in wanted:
                changed = changed_member[name]
                terminal, published = s.fixture.write_terminal, s.published
                edits, verdicts, stdout_lines = [], [], []

                def close(segment, kind, receipt, sha):
                    if kind == changed:
                        mutate(name, kind, segment, receipt)
                        edits.append(kind)
                    return terminal(segment, kind, receipt, sha)

                def observe(case, rc):
                    import json

                    if (case.attempt.output / "evidence_ledger.jsonl").exists():
                        verdict = published(case, rc)
                    else:
                        # R4 refuses before Part C opens its ledger: both publications agree, and never on pass.
                        document = s.read(case.attempt.output / "smoke.json")
                        assert document == s.read(case.attempt.output / "smoke_part_c.json")
                        verdict = document["evaluation"]["verdict"]
                        assert verdict != "pass" and rc != 0, (verdict, rc)
                    record = s.read(case.attempt.output / "smoke.json")["evaluation"]
                    stdout = (case.attempt.root / "part-c.stdout.log").read_text().splitlines()
                    stdout_lines[:] = [line for line in stdout if line.startswith("{")]
                    found = {(item["reason"], item["field"]) for item in map(json.loads, (
                        line for line in stdout if line.startswith("{")))}
                    verdicts.append((verdict, record["pass"], rc, sorted(record["evidence_failures"]), found))
                    return verdict

                with ExitStack() as stack:
                    issued_edit(name, stack)
                    stack.enter_context(patch.object(s.fixture, "write_terminal", close))
                    stack.enter_context(patch.object(s, "published", observe))
                    try:
                        s.control(work / name)
                    except s.Disagreement as error:
                        if not str(error).startswith("clean control: "):
                            raise
                assert edits == ([changed] if changed else []) and len(verdicts) == 1, (name, edits, verdicts)
                verdict, passed, code, reasons, found = verdicts[0]
                expected = EXPECTED[name]
                refused = (verdict, passed, code) == ("other_failure", False, 2)
                ok = (verdict, passed, code) == ("pass", True, 0) if expected is None else (
                    refused and expected in found if isinstance(expected, tuple) else refused and expected in reasons)
                print("RESULT", name, verdict, ",".join(reasons) or "-", flush=True)
                print("FIELDS", name, " ".join(sorted(f"{reason}:{field}" for reason, field in found)) or "-",
                      flush=True)
                if os.environ.get("JW_PARTC_PROBE_LOG"):
                    print(stdout_lines[-1] if stdout_lines else "", flush=True)
                if not ok:
                    failures.append(name)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
