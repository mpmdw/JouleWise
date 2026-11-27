"""Issue a gate through the frozen collector and ThermalSession on a scheduled clock."""
from bisect import bisect_right
from dataclasses import asdict
import os
from random import Random
from types import SimpleNamespace

N = 10**9
READ_NS = 200_000
LEAD_NS = 13_000_000


def bracket(row, start, finish):
    # The synthetic collector's three clocks use the control's common origin.
    for k in row["started"]:
        row["started"][k] = start
        row["finished"][k] = finish
    status = row["values"]["status"]
    status.update(monotonic_ns=finish, pm_observed_ns=finish)


def schedule(v, journal, gate, slow, entering, name):
    s, e = gate["start_ns"], gate["end_ns"]
    rows = [r for r in journal if r["kind"] == "reading"]
    rng = Random(224)
    for row in rows:
        t = row["started"]["monotonic_ns"]
        current = row["values"]["sensors"][slow]
        if entering and t == s:
            bracket(row, s - READ_NS // 2, s + READ_NS // 2)
            v.set_sensor_value(row, slow, current + .1875)
        elif t == e:
            bracket(row, e - LEAD_NS, e - LEAD_NS + READ_NS)
        elif not entering and e - 60*N < t < e:
            v.set_sensor_value(row, slow, current + rng.randrange(-16, 17)/128)
    samples = v.tg.sample_rows(rows)
    starts = [x["monotonic_ns"] for x in samples]
    count = bisect_right(starts, e)
    finish = samples[count-1]["finished"]["monotonic_after_ns"]
    assert finish == e - LEAD_NS + READ_NS
    if entering:
        before = bisect_right(starts, s) - 1
        assert starts[before] < s < samples[before]["finished"]["monotonic_after_ns"]
        excluded = v.tg.slow_slope(samples[:before], s, slow)
        included = v.tg.slow_slope(samples[:before+1], s, slow)
        assert included != excluded and samples[before]["sensors"] != samples[before-1]["sensors"]
        if os.environ.get("JW_V4_OBSERVE"):
            print("ENTRY", name, starts[before], s, samples[before]["finished"]["monotonic_after_ns"],
                  "without", excluded, "with", included, flush=True)
        return e - 1, excluded

    # Independently enumerate the pin's edges and 31 interior instants. The
    # grid, read finish and PM time make this gate's final cell [finish, e].
    # GateWindow includes a superset of the public evaluator's edges here.
    window = v.GateWindow(samples, {"s_fast":slow, "s_slow":slow})
    points = window.points(finish, e)
    instants = set(points)
    for left, right in zip(points, points[1:]):
        instants.update(left + (right-left)*part//32 for part in range(1, 32))
    tried = {window.slope(t, count) for t in instants}
    for _ in range(4096):
        poll = rng.randrange(finish+1, e-1)
        slope = window.slope(poll, count)
        if slope not in tried and min(abs(slope-val) for val in tried) <= 1e-9:
            if os.environ.get("JW_V4_OBSERVE"):
                print("SLOPE", name, "poll_ns", poll, "claim", slope.hex(), "tried_instants",
                      len(instants), "nearest_gap", min(abs(slope-val) for val in tried), flush=True)
            return poll, None
    raise AssertionError("no untried final-poll double in the search")


def write_gate(v, journal, thermal, old_gate, poll):
    """Tick the in-memory Sidecar under its lock; order gate and sensor reads on one clock."""
    from joulewise.hazards.base import Stamp
    start, end = old_gate["start_ns"], old_gate["end_ns"]
    kind, turn = old_gate["kind"], old_gate["turn"]
    def target(r):
        return (r["kind"] == "align_thermal_gate" and
                r["values"].get("gate", r["values"]).get("turn") == turn)
    inputs = iter(r for r in journal[1:-1] if not target(r))
    next_row = next(inputs, None)
    ticks = iter(())
    now = journal[0]["started"]["monotonic_ns"]
    def side_stamp():
        return next(ticks, Stamp(now, now, now))

    def consume(until):
        nonlocal next_row, now, ticks
        while next_row and next_row["started"]["monotonic_ns"] <= until:
            row = next_row
            now = row["finished"]["monotonic_ns"]
            ticks = iter(Stamp.from_json(row[k]) for k in ("started","finished"))
            if row["kind"] == "reading":
                values = row["values"]
                entries = values["readings"]
                reader.read = lambda keys: {
                    "values": values["sensors"], "errors": values["errors"],
                    "raw": {key:{k:v for k,v in entry.items() if k not in ("value","error")}
                            for key,entry in entries.items()}}
                side.status_reader = lambda: values["status"]
                side.tick()
            else:
                side.event(row["kind"], row["values"])
            next_row = next(inputs, None)
        ticks = iter(())
        now = max(now, until)

    initial_poll = start + (poll-start) % N
    times = [start, *range(initial_poll, poll+1, N), end]
    wake = start
    stamps = iter(times)
    def stamp():
        t = next(stamps)
        assert t >= max(now, wake)
        consume(t)  # A concurrent in-progress reading finishes before snapshot acquires the lock.
        return v.stamp(t)
    def sleep(seconds):
        nonlocal wake
        assert 0 < seconds <= 1
        wake = now + round(seconds*N)
    reader = SimpleNamespace()
    session = v.tg.ThermalSession(thermal["policy"], SimpleNamespace(stamp=stamp,sleep=sleep), reader=reader)
    session.reference = thermal["window_reference"]
    session.episode_reference = thermal["episode_reference"]
    side = session.sidecar
    side.ctx = SimpleNamespace(stamp=side_stamp)
    output = []
    append = side._write
    def capture(*args, **kwargs):
        row = append(*args, **kwargs)
        output.append(row)
        return row
    side._write = capture
    side.start(background=False)
    side._thread = SimpleNamespace(is_alive=lambda: True)
    gate = session._wait(kind, turn=turn)
    assert gate["outcome"] == "released" and gate["end_ns"] == end and next(stamps, None) is None
    assert gate["slope_c_per_min"] == v.tg.slow_slope(session.rows, poll, session.policy["sensors"]["s_slow"])
    assert gate["release"] == old_gate["release"]
    consume(journal[-1]["started"]["monotonic_ns"])
    report_end = journal[-1]["values"]["coverage"]["span_ns"][1]
    side._write("session_end", {"coverage":side.counter.report(report_end), "collector_error":None})
    return gate, output, session.events


def issue(v, base, stage, case):
    if case.op == "tried":
        return stage
    root = stage/case.role
    receipt = v.read(root/v.RECEIPT)
    bundle = root/receipt["bundle"]
    ep_path = bundle/"outputs/align_episode.json"
    path = bundle/"outputs/align_thermal.jsonl"
    ep, journal = v.read(ep_path), v.rows(path)
    thermal = ep["hardware"]["thermal"]
    index = int(case.op.startswith("g1-"))
    old = thermal["intervals"][index]
    entering = case.rule == "gate-entry-read"
    poll, excluded = schedule(v, journal, old, thermal["policy"]["sensors"]["s_slow"], entering, case.name)
    gate, output, emitted = write_gate(v, journal, thermal, old, poll)
    if case.op == "off":
        gate["slope_c_per_min"] += 1e-6
    elif case.op.endswith("-mixed"):
        gate["entry_slope_c_per_min"] = excluded
    thermal["intervals"][index] = gate
    events = v.rows(bundle/"events.jsonl")
    replacements = iter(emitted)
    for i, row in enumerate(events):
        if row["phase"] == "align_thermal_gate" and row["metadata"]["turn"] == old["turn"]:
            events[i] = asdict(next(replacements))
    assert next(replacements, None) is None
    v.write(ep_path,ep)
    v.write_rows(path,output)
    v.write_rows(bundle/"events.jsonl",events)
    receipt.update(v.derive(root,case.role,receipt,v.read(stage/"soak/soak_reference.json")))
    v.put_result(root,receipt)
    v.rt.write_custody(root,v.read(root/v.rt.CUSTODY_NAME))
    if case.role == v.S:
        v.propagate_step_digest(base,stage,receipt)
    return stage
