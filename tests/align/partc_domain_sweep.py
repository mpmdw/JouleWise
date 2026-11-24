"""Generated sweeps for Part C's temporal containment (R1) and raw-domain schemas (R2).

Lead fix round r2 of 2026-11-22. The frozen v4 suite builds one clean synthetic control (RL-215 Q1).

- TEMPORAL: for every timestamped source the evaluator reduces, one row shifted outside the member's bound
  interval, one stamp repeated, and, where a count or tail minimum is judged, the tail (or head) dropped. The
  records the mutation touches are kept consistent with each other (the receipt's copies, the battery
  summary, the soak's derived series), so only the temporal rule can refuse. The controller event log may
  repeat an instant (its frozen synthetic control does), so its repeat is replaced by a reversal.
- SCHEMA: for every field of every R2 schema table (``align_r1_part_c``'s ``LOAD_JOURNAL`` with its census and
  process rows, ``BATTERY_READING``, ``BATTERY_ERROR``, ``EPISODE_ENDPOINT``, ``PROVENANCE_ENDPOINT`` and
  ``GENERATION_FINISH``), a wrong type, a value out of range, an unknown enumeration value, a missing field, an
  extra field, and a duplicate JSON key or a duplicate unique key. The load journal and battery rows go through
  the evaluator's reducers (``_check_load``, ``_check_battery``); the endpoint and generation tables, which sit
  inside the member records check, go through ``_conform`` with the evaluator's own table (the native launcher
  regressions F6 and F7 cover them end to end).

Every mutation must refuse, every clean record must pass, and every entry must generate at least one mutation.

    python3.13 -IB tests/align/partc_domain_sweep.py      (JW_PARTC_REPO selects the tree under test)

It prints one `SWEEP <entry> <generated> <refused>` line per entry and exits 1 on any mutation that passed, any
clean record refused, or any entry with nothing generated.
"""
import copy
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
# RL-215 Q1: the writer-produced v4 control succeeds v3.2's, whose clean control exact battery counting refuses.
SUITE = HERE.parents[1] / "tests/frozen/partc-v4/suite-v4/tests/align/test_partc_writer_v4.py"

TEMPORAL = ("cpu.samples", "census.session", "battery.rows", "events.timestamp", "turns.stamps",
            "episode.paired_stamps", "sensor.wall", "sensor.monotonic", "soak.tail")
# Fix round r3: the classes of the confirmation audit of 2026-11-23, each swept as a property. The expected
# outcome is computed independently (the frozen reducer at both ends, the launch order, the next row's start,
# the two Segment.run samples), and the evaluator must refuse exactly the inputs that violate it.
R3_CLASSES = ("soak.close_settled", "launch.origin", "row.nested_stamps", "battery.samples")
SCHEMA = ("load_journal", "battery_reading", "battery_error", "episode_endpoint", "provenance_endpoint",
          "generation_finish")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def at(value, path):
    for key in path:
        value = value[key]
    return value


def wrong_values(pc, rule, current):
    """Values outside ``rule``: wrong types, out of range, an unknown enumeration value."""
    if isinstance(rule, pc._OneOf):
        candidates = ["synthetic.unknown", 1, 1.5, [], {}, "", True, None]
        return [value for value in candidates
                if not any(type(value) is type(option) and value == option for option in rule)]
    return {pc._uint: ["1", 1.5, True, None, -1, [1]],
            pc._finite: ["1", True, None, [], math.inf],
            pc._nonnegative: ["1", True, None, -1, -0.5, math.inf],
            pc._pid: ["1", 1.5, True, None, 0, -1, [1]],
            pc._text: [1, True, None, "", ["x"]],
            pc._string: [1, True, None, ["x"]]}.get(rule, ["1", 1.5, True, -1, 101, []])


def schema_mutations(pc, record, table, path=()):
    """(label, mutate) for every field of ``table`` in the conforming ``record``, recursively."""
    def replace(here, value):
        def change(root):
            at(root, here[:-1])[here[-1]] = copy.deepcopy(value)
        return change

    def drop(here):
        return lambda root: at(root, here[:-1]).pop(here[-1])

    container = at(record, path)
    yield f"{'.'.join(map(str, path)) or 'record'} extra field", lambda root: at(root, path).update(unexpected=1)
    yield f"{'.'.join(map(str, path)) or 'record'} not an object", (
        (lambda root: at(root, path[:-1]).__setitem__(path[-1], [])) if path else None)
    for name, rule in table.items():
        here = (*path, name)
        label = ".".join(map(str, here))
        yield f"{label} missing", drop(here)
        current = container[name]
        if isinstance(rule, dict):
            yield from schema_mutations(pc, record, rule, here)
        elif isinstance(rule, pc._Each):
            item_rule, nonempty, unique, length = rule
            for value in ({}, "x", None):
                yield f"{label} = {value!r}", replace(here, value)
            if nonempty or length:
                yield f"{label} empty", replace(here, [])
            if length is not None and current:
                yield f"{label} with {length + 1} items", lambda root, here=here: at(root, here).append(
                    copy.deepcopy(at(root, here)[0]))
            if current:
                first = (*here, 0)
                if isinstance(item_rule, dict):
                    yield from schema_mutations(pc, record, item_rule, first)
                else:
                    for value in wrong_values(pc, item_rule, current[0]):
                        yield f"{label}.0 = {value!r}", replace(first, value)
                if unique is not None:
                    yield f"{label} duplicate {unique}", lambda root, here=here: at(root, here).append(
                        copy.deepcopy(at(root, here)[0]))
        else:
            for value in wrong_values(pc, rule, current):
                yield f"{label} = {value!r}", replace(here, value)


def duplicate_key(raw_object, key, value):
    """The record's JSON text with ``key`` written twice, the first time as ``value`` (last-wins hides it)."""
    text = raw_object.decode() if isinstance(raw_object, bytes) else raw_object
    assert text.startswith("{")
    return ("{" + json.dumps(key) + ": " + json.dumps(value) + ", " + text[1:]).encode()


def run():
    s = load("partc_suite", SUITE)
    generated = {name: 0 for name in (*TEMPORAL, *R3_CLASSES, *SCHEMA)}
    refused = {name: 0 for name in generated}
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
            try:
                check()
                found = None
            except EvidenceFailure as error:
                found = f"{error.reason} {error.field}"
            if clean:
                if found:
                    failures.append(f"{entry} clean {label}: refused {found}")
                return
            generated[entry] += 1
            if found:
                refused[entry] += 1
            else:
                failures.append(f"{entry} {label}: passed")

        def raw_rows(rows):
            return b"".join(json.dumps(row, sort_keys=True).encode() + b"\n" for row in rows)

        def terminal(kind):
            record = s.read(base / kind / s.rt.CUSTODY_NAME)
            return SimpleNamespace(kind=kind, started_epoch_s=record["started_epoch_s"],
                                   ended_epoch_s=record["ended_epoch_s"])

        def member(kind):
            """The member's receipt and the bound records the window and anchors read, by bundle-relative name."""
            receipt = s.read(base / kind / s.RECEIPT)
            data = {}
            if kind == "idle":
                data["sensors/align_thermal.jsonl"] = (base / kind / "sensors/align_thermal.jsonl").read_bytes()
                return receipt, data
            bundle = base / kind / receipt["bundle"]
            for name in ("events.jsonl", "outputs/align_episode.json", "outputs/align_turns.jsonl",
                         "outputs/align_thermal.jsonl"):
                if (bundle / name).is_file():
                    data[name] = (bundle / name).read_bytes()
            for name in ("recovery/align_thermal.jsonl", "inventory/inventory_journal.jsonl"):
                if (base / kind / name).is_file():
                    data[name] = (base / kind / name).read_bytes()
            return receipt, data

        def wall_of(kind):
            if kind in (s.P, s.S):
                window = terminal(kind)
                return window.ended_epoch_s - window.started_epoch_s
            if kind == "idle":
                row = s.read(base / "soak" / "soak_row.json")
                return (row["ended_ns"] - row["started_ns"]) / s.N
            return None

        kinds = ("idle", s.P, s.S, s.D, s.X)

        # ================= R1 TEMPORAL =================
        for kind in kinds:
            journal = s.read(base / kind / "load_journal.json")
            receipt, data = member(kind)
            anchors = pc._monotonic_anchors(data)
            wall = wall_of(kind)

            def loaded(document, kind=kind, receipt=receipt, wall=wall, anchors=anchors):
                claim = {**receipt, **{key: document[key] for key in ("cpu_busy_cores", "cpu_busy_t_s", "census")
                                       if key in document}}
                return lambda: pc._check_load(json.dumps(document).encode(), claim, kind, wall, anchors=anchors)

            expect("cpu.samples", f"{kind} clean", loaded(journal), clean=True)
            times, census = journal["cpu_busy_t_s"], journal["census"]
            opened, closed = census[0]["t_s"], census[1]["t_s"]
            span = closed - opened

            def samples(change, label, kind=kind, journal=journal):
                document = copy.deepcopy(journal)
                change(document)
                expect("cpu.samples", f"{kind} {label}", loaded(document))

            if times:
                middle = len(times) // 2
                samples(lambda d: d["cpu_busy_t_s"].__setitem__(0, d["cpu_busy_t_s"][0] - span - 10),
                        "first sample before the session")
                samples(lambda d: d["cpu_busy_t_s"].__setitem__(-1, d["cpu_busy_t_s"][-1] + span + 10),
                        "last sample after the session")
                samples(lambda d: d["cpu_busy_t_s"].__setitem__(middle, d["cpu_busy_t_s"][middle - 1]),
                        "middle sample repeats the one before")
                if wall is not None:
                    # Twenty samples: more than twice the frozen 5 s maximum gap. The origin is not recorded, so a
                    # head of up to 10 s is the same journal begun from an earlier origin, which no record refutes.
                    for label, part in (("tail", slice(None, -20)), ("head", slice(20, None))):
                        samples(lambda d, part=part: [d.__setitem__(key, d[key][part])
                                                      for key in ("cpu_busy_cores", "cpu_busy_t_s")],
                                f"{label} of twenty samples dropped")

            def session(points, label, kind=kind, journal=journal):
                expect("census.session", f"{kind} {label}", loaded({**journal, "census": points}))

            end = census[1]
            session([census[0], {**end, "t_s": opened}], "end repeats start")
            session([census[0], {**end, "t_s": opened - 1}], "end before start")
            if anchors:
                first, last = min(stamp for *_, stamp in anchors), max(stamp for *_, stamp in anchors)
                session([{**census[0], "t_s": first + 1e-3}, end], "opened after the member's first stamp")
                session([census[0], {**end, "t_s": last - 1e-3}], "closed before the member's last stamp")
                session([{**census[0], "t_s": opened - 2 * span - 10}, {**end, "t_s": opened - span - 10}],
                        "whole session moved before the member")

            # Battery rows: every row inside the bracket, strictly later than the one before.
            bound = terminal(kind)
            battery = s.rows(base / kind / s.pc.BATTERY_SOURCE)

            def battery_check(rows, kind=kind, receipt=receipt, bound=bound):
                claim = {**receipt, "battery": s.rt.battery_summary(rows)}
                return lambda: pc._check_battery(raw_rows(rows), claim, kind, bound)

            expect("battery.rows", f"{kind} clean", battery_check(battery), clean=True)
            for index in (0, len(battery) - 1):
                for label, epoch in (("before the bracket", bound.started_epoch_s - 1),
                                     ("after the bracket", bound.ended_epoch_s + 1)):
                    rows = copy.deepcopy(battery)
                    rows[index]["epoch_s"] = epoch
                    expect("battery.rows", f"{kind} row {index} {label}", battery_check(rows))
            rows = copy.deepcopy(battery)
            rows[1]["epoch_s"] = rows[0]["epoch_s"]
            expect("battery.rows", f"{kind} row 1 repeats row 0", battery_check(rows))
            rows = [{**row, "epoch_s": row["epoch_s"] + 1e6} for row in battery]
            expect("battery.rows", f"{kind} whole journal shifted", battery_check(rows))

            if kind == "idle":
                continue
            # The window: events, turn stamps, paired stamps and sensor rows on the wall clock.
            def windowed(changed, kind=kind, receipt=receipt, data=data, bound=bound):
                return lambda: pc._check_member_window(bound, receipt, {**data, **changed})

            expect("events.timestamp", f"{kind} clean", windowed({}), clean=True)
            events = s.rows(base / kind / receipt["bundle"] / "events.jsonl")
            for index, label, stamp in ((0, "before the bracket", bound.started_epoch_s - 1),
                                        (len(events) - 1, "after the bracket", bound.ended_epoch_s + 1)):
                rows = copy.deepcopy(events)
                rows[index]["timestamp_s"] = stamp
                expect("events.timestamp", f"{kind} event {index} {label}", windowed({"events.jsonl": raw_rows(rows)}))
            rows = copy.deepcopy(events)
            rows[1]["timestamp_s"] = rows[0]["timestamp_s"] - 1e-3
            expect("events.timestamp", f"{kind} event 1 before event 0", windowed({"events.jsonl": raw_rows(rows)}))

            turns = s.rows(base / kind / receipt["bundle"] / "outputs/align_turns.jsonl")
            for label, change in (
                    ("first start before the bracket", lambda t: t[0]["start_stamp"].update(epoch_s=bound.started_epoch_s - 1)),
                    ("last end after the bracket", lambda t: t[-1]["end_stamp"].update(epoch_s=bound.ended_epoch_s + 1)),
                    ("last end repeats its start", lambda t: t[-1]["end_stamp"].update(
                        epoch_s=t[-1]["start_stamp"]["epoch_s"]))):
                rows = copy.deepcopy(turns)
                change(rows)
                expect("turns.stamps", f"{kind} {label}", windowed({"outputs/align_turns.jsonl": raw_rows(rows)}))

            episode = s.read(base / kind / receipt["bundle"] / "outputs/align_episode.json")
            low, high = round(bound.started_epoch_s * s.N), round(bound.ended_epoch_s * s.N)
            for label, index, epoch in (("opening before the bracket", 0, low - s.N),
                                        ("closing after the bracket", 1, high + s.N),
                                        ("closing repeats the opening", 1, None)):
                document = copy.deepcopy(episode)
                stamps = document["hardware"]["paired_clock_stamps_ns"]
                stamps[index]["epoch_ns"] = stamps[0]["epoch_ns"] if epoch is None else epoch
                expect("episode.paired_stamps", f"{kind} {label}", windowed(
                    {"outputs/align_episode.json": json.dumps(document).encode()}))

            for source in sorted(name for name in data if name.endswith("align_thermal.jsonl")):
                rows = s.rows(base / kind / receipt["bundle"] / source) if source.startswith("outputs/") else s.rows(
                    base / kind / source)
                readings = [i for i, row in enumerate(rows) if row["kind"] == "reading"]
                if len(readings) < 2:
                    continue
                for label, change in (
                        ("reading before the bracket", lambda r: [r[readings[0]][end].update(wall_ns=low - s.N)
                                                                  for end in ("started", "finished")]),
                        ("reading after the bracket", lambda r: [r[readings[-1]][end].update(wall_ns=high + s.N)
                                                                 for end in ("started", "finished")]),
                        ("reading repeats the one before", lambda r: r[readings[1]]["started"].update(
                            wall_ns=r[readings[0]]["started"]["wall_ns"]))):
                    mutated = copy.deepcopy(rows)
                    change(mutated)
                    expect("sensor.wall", f"{kind} {source} {label}", windowed({source: raw_rows(mutated)}))

        # Sensor readings on the monotonic clock, inside their own session (``_validate_sidecar``).
        journals = [("idle", base / "idle" / "sensors/align_thermal.jsonl", False)]
        for kind in (s.S, s.D, s.X):
            receipt = s.read(base / kind / s.RECEIPT)
            journals.append((kind, base / kind / receipt["bundle"] / "outputs/align_thermal.jsonl", True))
        for kind, path, gated in journals:
            rows = s.rows(path)
            source = str(path.relative_to(path.parents[1]))
            readings = [i for i, row in enumerate(rows) if row["kind"] == "reading"]
            expect("sensor.monotonic", f"{kind} clean", lambda rows=rows, kind=kind, source=source, gated=gated:
                   pc._validate_sidecar(rows, sensors, kind, source, gated=gated), clean=True)
            closing = rows[-1]["finished"]["monotonic_ns"]
            for label, change in (
                    ("reading repeats the one before", lambda r: r[readings[1]]["started"].update(
                        monotonic_ns=r[readings[0]]["started"]["monotonic_ns"])),
                    ("reading after the session", lambda r: [r[readings[-1]][end].update(monotonic_ns=closing + s.N)
                                                             for end in ("started", "finished")])):
                mutated = copy.deepcopy(rows)
                change(mutated)
                expect("sensor.monotonic", f"{kind} {label}", lambda mutated=mutated, kind=kind, source=source,
                       gated=gated: pc._validate_sidecar(mutated, sensors, kind, source, gated=gated))

        # The soak's tail, judged at the session close: the frozen minimum is 0.9 reads per second.
        from joulewise.align.apple.thermal import Coverage, keys

        soak_rows = s.rows(base / "idle" / "sensors/align_thermal.jsonl")
        soak_receipt = s.read(base / "idle" / s.RECEIPT)
        soak_window = terminal("idle")
        expect("soak.tail", "clean", lambda: pc._derive_soak(raw_rows(soak_rows), soak_receipt, sensors, soak_window),
               clean=True)
        start, close = soak_rows[0], soak_rows[-1]
        observed = [row for row in soak_rows if row["kind"] == "reading"]
        for keep in (1201, 1601, 1661):
            kept = observed[:keep]
            sampling = s.tg.sample_rows(kept)
            origin = sampling[0]["monotonic_ns"]
            coverage = Coverage(start["started"]["monotonic_ns"], keys(start["values"]["thermal"]))
            for row in kept:
                coverage.observe(row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"], row["values"])
            closed_row = copy.deepcopy(close)
            closed_row["values"]["coverage"] = coverage.report(close["values"]["coverage"]["span_ns"][1])
            closed_row["seq"] = len(kept) + 2
            claim = copy.deepcopy(soak_receipt)
            for key in (sensors["s_fast"], sensors["s_slow"]):
                good = s.rt.valid_series(sampling, key)
                claim["sensor_series_c"][key] = [value for _, value in good]
                claim["sensor_series_t_s"][key] = [(ns - origin) / s.N for ns, _ in good]
                claim["sensor_series_failed_reads"][key] = len(kept) - len(good)
            claim["sensor_series_end_t_s"] = (sampling[-1]["monotonic_ns"] - origin) / s.N
            rows = [start, *kept, closed_row]
            expect("soak.tail", f"last {len(observed) - keep} readings dropped", lambda rows=rows, claim=claim:
                   pc._derive_soak(raw_rows(rows), claim, sensors, soak_window))

        # ================= R3 CLASSES =================
        def judge(entry, label, check, refuses):
            """A property case: ``refuses`` is the independently computed outcome the evaluator must match."""
            expect(entry, label, check, clean=not refuses)

        # The soak's settling test at the session close, for tails that stop short of it and rise at slopes
        # straddling the frozen 0.2 C/min limit. The frozen reducer at the last reading and at the close decides.
        fast = sensors["s_fast"]
        for keep in (1661, 1701, 1741, 1781):
            for amplitude in (0.15, 0.19, 0.199, 0.2005, 0.201, 0.21, 0.3):
                kept = copy.deepcopy(observed[:keep])
                for index, row in enumerate(kept):
                    # The issued ALIGN reader's bytes for the value (EI ``smc-wire``), as the suite's control writes.
                    s.set_sensor_value(row, fast, 35.0 + amplitude * max(index - 600, 0) / 60)
                sampling = s.tg.sample_rows(kept)
                origin = sampling[0]["monotonic_ns"]
                coverage = Coverage(start["started"]["monotonic_ns"], keys(start["values"]["thermal"]))
                for row in kept:
                    coverage.observe(row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"], row["values"])
                closed_row = copy.deepcopy(close)
                closed_row["values"]["coverage"] = coverage.report(close["values"]["coverage"]["span_ns"][1])
                closed_row["seq"] = len(kept) + 2
                claim = copy.deepcopy(soak_receipt)
                for key in (sensors["s_fast"], sensors["s_slow"]):
                    good = s.rt.valid_series(sampling, key)
                    claim["sensor_series_c"][key] = [value for _, value in good]
                    claim["sensor_series_t_s"][key] = [(ns - origin) / s.N for ns, _ in good]
                    claim["sensor_series_failed_reads"][key] = len(kept) - len(good)
                claim["sensor_series_end_t_s"] = (sampling[-1]["monotonic_ns"] - origin) / s.N
                ends = (claim["sensor_series_end_t_s"], (close["started"]["monotonic_ns"] - origin) / s.N)
                try:
                    refuses = any(stat["settled"] is not True for end in ends for stat in s.r1.soak_detrended(
                        claim["sensor_series_c"], claim["sensor_series_t_s"], end).values())
                except s.r1.Refusal:
                    refuses = True
                rows = [start, *kept, closed_row]

                def soak_check(rows=rows, claim=claim):
                    # _check_native_soak's own test of the frozen derivation, after _derive_soak's at the close.
                    if any(stat["settled"] is not True for stat in pc._derive_soak(
                            raw_rows(rows), claim, sensors, soak_window).values()):
                        raise EvidenceFailure("soak_unsettled", "idle", "sensors/align_thermal.jsonl")

                judge("soak.close_settled", f"keep {keep} rise {amplitude}", soak_check, refuses)

        # Launch order on the monotonic clock: each member's census and CPU origin lie after the previous
        # member's close (the soak's after 0). Offsets shifted later move the origin earlier by the same amount.
        prior = 0.0
        for kind in kinds:
            journal = s.read(base / kind / "load_journal.json")
            receipt, data = member(kind)
            anchors, wall = pc._monotonic_anchors(data), wall_of(kind)
            opened, closed = (point["t_s"] for point in journal["census"])

            def launched(document, kind=kind, receipt=receipt, wall=wall, anchors=anchors, after=prior):
                claim = {**receipt, **{key: document[key] for key in ("cpu_busy_t_s", "census")}}
                return lambda: pc._check_load(json.dumps(document).encode(), claim, kind, wall, anchors=anchors,
                                              after=after)

            judge("launch.origin", f"{kind} clean", launched(journal), False)
            if journal["cpu_busy_t_s"]:
                first = journal["cpu_busy_t_s"][0]
                for delay in (1, 50, 199, 200, 201, 500, 4000):
                    document = {**journal, "cpu_busy_t_s": [t + delay for t in journal["cpu_busy_t_s"]]}
                    # The edges fix the origin at opened - first - delay; it must not precede the prior close.
                    judge("launch.origin", f"{kind} offsets +{delay}", launched(document),
                          opened - first - delay < prior)
            else:
                for label, moved in (("census opened at the prior close", prior), ("one second before it", prior - 1),
                                     ("whole census before it", None)):
                    points = copy.deepcopy(journal["census"])
                    if moved is None:
                        points[0]["t_s"], points[1]["t_s"] = prior - 2, prior - 1
                    else:
                        points[0]["t_s"] = moved
                    judge("launch.origin", f"{kind} {label}", launched({**journal, "census": points}), points[0]["t_s"] < prior)
            prior = closed

        # Producer order inside a journal row: every nested observation stamp is no later than the next row's
        # start (for the last reading, the session_end row). One past it refuses; exactly at it passes. A PM
        # stamp is taken inside the status call, so its own bound is the row's status stamp (EI ``pm-before``,
        # RL-215 Q4): exactly at that passes.
        def place(root, field, value):
            parts = [int(part) if part.isdigit() else part for part in field.split(".")]
            at(root, parts[:-1])[parts[-1]] = value

        for kind, path, gated in journals:
            rows = s.rows(path)
            source = str(path.relative_to(path.parents[1]))
            stamped = [i for i, row in enumerate(rows[:-1]) if any(True for _ in pc._nested_stamps(row["values"]))]
            for i in sorted({*stamped[:2], *stamped[len(stamped) // 2:][:1], *stamped[-2:]}):
                following = rows[i + 1]["started"]["monotonic_ns"]
                for field, _ in pc._nested_stamps(rows[i]["values"]):
                    ceiling = (rows[i]["values"]["status"]["monotonic_ns"] if field == "status.pm_observed_ns"
                               else following)
                    for value, refuses in ((following + 1, True), (ceiling, False)):
                        if not refuses and not field.startswith("status."):
                            continue                 # a gate row's paired stamps have their own later checks
                        mutated = copy.deepcopy(rows)
                        place(mutated[i]["values"], field, value)
                        judge("row.nested_stamps", f"{kind} {source} row {i} {field} {'+1' if refuses else '=0'}",
                              lambda mutated=mutated, kind=kind, source=source, gated=gated:
                              pc._validate_sidecar(mutated, sensors, kind, source, gated=gated), refuses)

        # Structural completeness, RL-215 Q4: Segment.run's opening and closing battery samples and one periodic
        # sample per ``battery_poll_s`` ticks, exactly 2 + T // p rows for every member. Any row dropped refuses.
        period = int(s.CONFIG.get("battery_poll_s", 30))
        for kind in kinds:
            receipt, data = member(kind)
            bound, battery = terminal(kind), s.rows(base / kind / s.pc.BATTERY_SOURCE)
            load_raw = (base / kind / "load_journal.json").read_bytes()
            ticks = len(json.loads(load_raw)["cpu_busy_t_s"]) + len(json.loads(load_raw)["errors"])
            for dropped in range(len(battery)):
                rows = [row for index, row in enumerate(battery) if index != dropped]
                claim = {**receipt, "battery": s.rt.battery_summary(rows)}
                judge("battery.samples", f"{kind} row {dropped} dropped", lambda rows=rows, claim=claim, kind=kind,
                      bound=bound, load_raw=load_raw, data=data: pc._check_battery(
                          raw_rows(rows), claim, kind, bound, load=load_raw, configured=s.CONFIG, data=data),
                      len(rows) != 2 + ticks // period)

        # ================= R2 SCHEMA =================
        def refuse(field):
            raise EvidenceFailure("schema", "sweep", "table", field=field)

        for kind in ("idle", s.P, s.D):
            journal = s.read(base / kind / "load_journal.json")
            receipt, data = member(kind)
            anchors, wall = pc._monotonic_anchors(data), wall_of(kind)

            def check(document, kind=kind, receipt=receipt, wall=wall, anchors=anchors):
                claim = dict(receipt)
                for key in ("cpu_busy_cores", "cpu_busy_t_s", "census"):
                    if isinstance(document, dict) and key in document:
                        claim[key] = document[key]
                if isinstance(document, dict) and "errors" in document:
                    claim["load_journal_errors"] = document["errors"]
                raw = document if isinstance(document, bytes) else json.dumps(document).encode()
                return lambda: pc._check_load(raw, claim, kind, wall, anchors=anchors)

            expect("load_journal", f"{kind} clean", check(journal), clean=True)
            for label, change in schema_mutations(pc, journal, pc.LOAD_JOURNAL):
                if change is None:
                    continue
                document = copy.deepcopy(journal)
                change(document)
                expect("load_journal", f"{kind} {label}", check(document))
            for key in pc.LOAD_JOURNAL:
                expect("load_journal", f"{kind} duplicate key {key}", check(
                    duplicate_key(json.dumps(journal), key, journal[key])))

        for kind in ("idle", s.P):
            receipt, _ = member(kind)
            bound = terminal(kind)
            battery = s.rows(base / kind / s.pc.BATTERY_SOURCE)

            def battery_rows(rows, kind=kind, receipt=receipt, bound=bound, raw=None):
                try:
                    summary = s.rt.battery_summary(rows)
                except Exception:                                    # noqa: BLE001 - a broken row: keep the clean one
                    summary = receipt["battery"]
                return lambda: pc._check_battery(raw or raw_rows(rows), {**receipt, "battery": summary}, kind, bound)

            failed = {"epoch_s": battery[0]["epoch_s"], "error": "pmset: synthetic", "soc_pct": None, "state": None}
            for entry, first, table in (("battery_reading", battery[0], pc.BATTERY_READING),
                                        ("battery_error", failed, pc.BATTERY_ERROR)):
                clean = [first, *battery[1:]]
                expect(entry, f"{kind} clean", battery_rows(clean), clean=True)
                for label, change in schema_mutations(pc, first, table):
                    if change is None:
                        continue
                    row = copy.deepcopy(first)
                    change(row)
                    expect(entry, f"{kind} row 0 {label}", battery_rows([row, *battery[1:]]))
                for key in table:
                    raw = duplicate_key(json.dumps(first, sort_keys=True), key, first[key]) + b"\n" + raw_rows(battery[1:])
                    expect(entry, f"{kind} duplicate key {key}", battery_rows(clean, raw=raw))

        receipt, data = member(s.D)
        episode = json.loads(data["outputs/align_episode.json"])
        provenance = s.read(base / s.D / receipt["bundle"] / "metadata.json")["workload_provenance"]
        generation = s.rows(base / s.D / receipt["bundle"] / "outputs/align_turns.jsonl")[-1]["generation"]
        for entry, record, table in (("episode_endpoint", episode, pc.EPISODE_ENDPOINT),
                                     ("provenance_endpoint", provenance, pc.PROVENANCE_ENDPOINT),
                                     ("generation_finish", generation, pc.GENERATION_FINISH)):
            def conform(value, table=table):
                return lambda: pc._conform(value, table, refuse, closed=False)

            expect(entry, "clean", conform(record), clean=True)
            for label, change in schema_mutations(pc, record, table):
                if change is None or label.endswith("extra field"):   # an open table: other fields have their own checks
                    continue
                mutated = copy.deepcopy(record)
                change(mutated)
                expect(entry, label, conform(mutated))
            for key in table:
                raw = duplicate_key(json.dumps(record), key, record[key])
                expect(entry, f"duplicate key {key}", lambda raw=raw: pc._strict_object(raw, s.D, entry, "schema"))
        for finish in (*pc.CLEAN_FINISH, *pc.BUDGET_FINISH, *pc.CUT_FINISH, None):
            expect("generation_finish", f"known {finish!r}", lambda finish=finish: pc._conform(
                {"finish_reason": finish}, pc.GENERATION_FINISH, refuse, closed=False), clean=True)

    for name in generated:
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
