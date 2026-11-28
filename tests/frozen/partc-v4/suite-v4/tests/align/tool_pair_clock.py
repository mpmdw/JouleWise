"""RL-219 §4. Script the Air's two clock sources under the frozen workload."""
from collections import deque
from dataclasses import asdict
from math import ulp
from shutil import copytree
from types import SimpleNamespace as Namespace
from unittest.mock import patch

NS = 10**9
WALL_ORIGIN = 1795651200  # 2026-11-26 UTC, fixed for portable replay
WALL_RESOLUTION = 1.0000000000000002e-6
MONO_RESOLUTION = 4.166666666666666e-8  # mach_absolute_time, 125/3 ns
WORK_NS = 64_000


class ScriptedClock:
    """Use CK's stamp implementation. Ordinary reads cost 42 ns. The selected hold spans 40 us."""
    def __init__(self, start_ns, target, side):
        self.next_ns = start_ns
        self.target = target
        self.side = side
        self.pending = deque()
        self.witness = {}
        self.count = 0

    def seek(self, ns):
        assert self.next_ns <= ns and ns % 1000 == 0
        self.next_ns = ns

    def get_clock_info(self, name):
        return Namespace(resolution={"time": WALL_RESOLUTION, "monotonic": MONO_RESOLUTION}[name])

    def monotonic(self):
        self.reads.append("monotonic")
        tick = (self.physical_ns * 3 + 62) // 125
        self.physical_ns += self.costs.popleft()
        return (tick * 125) / (3 * NS)

    def time(self):
        self.reads.append("wall")
        micros, self.lost_ns = divmod(self.physical_ns, 1000)
        self.physical_ns += self.costs.popleft()
        return (WALL_ORIGIN * 1_000_000 + micros) / 1_000_000

    def stamp(self, label=None, *, fraction=None):
        from joulewise import clock as ck
        if self.pending:
            assert label is None
            label = self.pending.popleft()
        # Ordinary stamps stay close to one another in grid phase. Isolate
        # exactly one event on the opposite side of its two mapping witnesses.
        self.count += 1
        if fraction is None:
            fraction = (17 * self.count) % 31
            if self.side in ("low", "minus"):
                fraction = 999 - fraction
            if label == self.target and label is not None:
                fraction = 0 if self.side in ("low", "minus") else 999
            if self.count == 1:
                fraction = 0  # Arm the workload's deadman at the fixture's G0 origin.
        costs = (42, 42, 42)
        held = label is not None and label == self.target and self.side.startswith("held-")
        if held:
            # Keep each read nonzero-cost: the wall read lands on the first
            # or last monotonic tick of a 40 us bracket.
            costs = (1, 39_999, 42) if self.side == "held-before" else (39_999, 1, 42)
        self.costs = deque(costs)
        self.physical_ns = self.next_ns + fraction - costs[0]
        self.reads = []
        with patch.object(ck, "time", self):
            stamp = ck.SystemClock.stamp(self)
        assert self.reads == ["monotonic", "wall", "monotonic"]
        assert self.lost_ns == fraction and round(ulp(stamp.epoch_s) * NS) == 238
        if held:
            width = round((stamp.monotonic_after_s - stamp.monotonic_before_s) * NS)
            assert width == 40_000
        self.next_ns += WORK_NS
        self.last_reading = stamp, fraction
        if label is not None:
            assert label not in self.witness
            self.witness[label] = (stamp, fraction)
        return stamp


def thermal_inputs(v, bundle, gates):
    """Put the fixture's external gate observations on the two source clocks."""
    from joulewise.align.apple.sampler import _stamp_record, monotonic_ns

    gate_clock = ScriptedClock(gates[0]["start_ns"], None, "neutral")
    for i, gate in enumerate(gates):
        for j, (edge, when) in enumerate((("entry", "start_ns"), ("exit", "end_ns"))):
            gate_clock.seek(gate[when])
            stamp = gate_clock.stamp(fraction=2*i + j + 1)
            assert monotonic_ns(stamp) == gate[when]
            gate[edge + "_stamp"] = _stamp_record(stamp)
            gate[edge + "_epoch_s"] = stamp.epoch_s
    gate_by_id = {(g["kind"], g["turn"]): g for g in gates}
    journal_file = bundle / "outputs/align_thermal.jsonl"
    journal = v.rows(journal_file)
    for row in journal:
        for tag in ("started", "finished"):
            row[tag]["wall_ns"] += WALL_ORIGIN * NS
        values = row["values"]
        if values.get("state") == "begin":
            values["entry_stamp"] = gate_by_id[values["gate_kind"], values["turn"]]["entry_stamp"]
        elif values.get("state") == "end":
            g = values["gate"]
            values["gate"] = gate_by_id[g["kind"], g["turn"]]
        else:
            continue
        # Sidecar.event persists the completed paired stamp after the simultaneous
        # periodic reading. Timestamps and sequence reflect the acquisition order.
        for tag in ("started", "finished"):
            for domain in ("wall_ns", "monotonic_ns", "monotonic_raw_ns"):
                row[tag][domain] += 1000
    journal.sort(key=lambda row: row["started"]["monotonic_ns"])
    for i, row in enumerate(journal, 1):
        row["seq"] = i
    v.write_rows(journal_file, journal)
    return gate_by_id


def issue_member(v, root, role, selection, soak, arm=None):
    """Keep the fixture's gate and model schedule. WL writes the complete episode,
    turn provenance and controller events before either evaluator sees a byte.
    """
    from joulewise.align.apple.endpoint import normalize_model_family
    from joulewise.align.apple.sampler import monotonic_ns, seconds_ns, stamp_mapping
    from joulewise.align.interfaces import ChatMessage
    from joulewise.interfaces import RuntimeEvent
    from joulewise.schemas import BenchmarkConfig

    receipt = v.read(root / v.RECEIPT)
    bundle = root / receipt["bundle"]
    config = BenchmarkConfig.from_mapping(v.read(bundle / "config.json"))
    spec = v.wl.EpisodeSpec.from_text(config.workload_profile.prompt_text)
    original = v.read(bundle / "outputs/align_episode.json")
    model_rows = v.rows(bundle / "outputs/align_turns.jsonl")
    model_turns = original["turns"]
    assert len(model_turns) >= 2 and any(turn["tool_calls"] for turn in model_turns)
    target = None
    side = "neutral"
    if selection:
        which, boundary, side = selection.split("-", 2)
        target = (0 if which == "next" else len(model_turns) - 1, boundary)

    thermal_record = original["hardware"]["thermal"]
    gates = thermal_record["intervals"]
    gate_by_id = thermal_inputs(v, bundle, gates)
    first_entry = gates[0]["start_ns"]
    clock = ScriptedClock(first_entry - (WORK_NS if arm else 0), target, side)
    position = 0

    class Thermal:
        def wait(self, kind, turn=0, **kwargs):
            g = gate_by_id[kind, turn]
            for edge, direction in (("entry", "start"), ("exit", "end")):
                self.events.append(RuntimeEvent(g[edge + "_epoch_s"], "phase_" + direction,
                                                "align_thermal_gate", kind, g))
            clock.seek(g["end_ns"] + WORK_NS)
            return g

        def record(self):
            return thermal_record

    thermal = Thermal()
    thermal.intervals = gates
    thermal.flags = thermal_record["flags"]
    thermal.episode_reference = thermal_record["episode_reference"]
    thermal.events = []
    thermal.start = lambda: None
    thermal.capture_reference = lambda member: None

    def call_tool(*args):
        clock.pending.append((position - 1, "end"))
        return "{}"

    task = Namespace(task_pair=original["task_pair"], reset=lambda seed: None,
                     system_prompt=lambda condition: "", user_prompt=lambda: "", tool_schemas=lambda: [],
                     call_tool=call_tool, score_main=lambda history: None, score_side=lambda history: None,
                     scratchpad_tags=None, task_description=lambda: "")

    class Endpoint:
        def __init__(self, *args, **kwargs):
            self.model_family = normalize_model_family(config.model.family)
            self.flags, self.events, self.turn_provenance = [], [], []
            self.identity, self.prompt_token_ids = original["endpoint"], []
            self.tokenizer_provenance, self.cache_policy = {}, {}

        def rendered_prompt_length(self, history, tools):
            return len(model_rows[position]["generation"]["prompt_token_ids"])

        def assistant_history_message(self, result):
            return ChatMessage("assistant", "")

        def chat(self, history, **kwargs):
            nonlocal position
            index = position
            t = model_turns[index]
            clock.seek(t["start_ns"])
            start = clock.stamp((index, "model-start"))
            clock.seek(t["first_token_ns"])
            first = clock.stamp().epoch_s
            # Leave time for the final tool and episode close inside the sidecar session.
            clock.seek(t["end_ns"] - WORK_NS * 32)
            end = clock.stamp((index, "model-end"))
            mapping, _ = stamp_mapping((start, end), episode_domain=original["clock_domain"])
            count, cap = t["decode_tokens"], kwargs["max_tokens"]
            for ts, word, phase, attrs in (
                (start.epoch_s, "phase_start", "prefill", {}),
                (first, "phase_end", "prefill", {}),
                (first, "phase_start", "decode", {"max_tokens": cap}),
                *((first, "token", "decode", {"index": j}) for j in range(count)),
                (end.epoch_s, "phase_end", "decode", {"emitted_tokens": count, "requested_output_tokens": cap}),
            ):
                self.events.append(RuntimeEvent(ts, word, phase, "synthetic", {"align_turn_index": index, **attrs}))
            row = dict(turn=index, flags=[], start_stamp=asdict(start), end_stamp=asdict(end),
                       clock_mapping=asdict(mapping), generation=model_rows[index]["generation"])
            self.turn_provenance.append(row)
            name = "end_task" if index == len(model_turns) - 1 else "list_messages"
            call = Namespace(name=name, arguments_json="{}", call_id=str(index))
            # WL checks the deadman once before taking the tool's opening stamp.
            clock.pending.extend((None, (index, "start")))
            position += 1
            return Namespace(start_ns=monotonic_ns(start), end_ns=monotonic_ns(end),
                             first_token_ns=seconds_ns(first) + mapping.offset_ns,
                             prompt_tokens=t["prefill_tokens"], cached_prompt_tokens=t["context_tokens"],
                             completion_tokens=count, reasoning_tokens=t["hidden_tokens"], tool_calls=[call],
                             raw_usage={"joulewise": {"flags": []}})

    runtime = Namespace(name="synthetic", prepare=lambda *args: v.wl.AdapterResult(ok=True),
                        warmup=lambda *args: v.wl.AdapterResult(ok=True))
    adapter = v.wl.EpisodeRuntimeAdapter(runtime, clock, thermal_factory=lambda *args: thermal)
    factory = Namespace(**{spec.task_factory.split(":")[1]: lambda **kwargs: task})
    with patch.object(v.wl, "importlib", Namespace(import_module=lambda _: factory)):
        assert adapter.prepare(config).ok
    assert adapter.warmup(config).ok
    adapter.powermode_reader = lambda: 0
    adapter.identity_projection_metadata = lambda cfg: dict(model={}, sampler={}, output_policy={})
    with patch.object(v.wl, "MlxEndpoint", Endpoint):
        result = adapter.run_workload(config)
    assert position == len(model_rows) and not clock.pending
    for name in ("align_episode.json", "align_turns.jsonl"):
        (bundle / "outputs" / name).write_text(result.output_artifacts[name])
    events = [asdict(event) for event in result.events]
    final = v.rows(bundle / "events.jsonl")[-1]
    assert final["event_type"] == "run_finalized"
    final["timestamp_s"] += WALL_ORIGIN
    v.write_rows(bundle / "events.jsonl", [*events, final])
    meta = v.read(bundle / "metadata.json")
    meta["workload_provenance"] = result.workload_provenance
    anchor = meta["uncertainty_evidence"]["clock_anchor"]
    anchor.update(wall_minus_monotonic_lower_s=WALL_ORIGIN - 2e-6,
                  wall_minus_monotonic_upper_s=WALL_ORIGIN + 2e-6, effective_clock_anchor_bound_s=4e-6)
    v.write(bundle / "metadata.json", meta)

    # Synthetic telemetry and ticker samples on this second wall timeline.
    trace = bundle / "power_trace.csv"
    trace.write_text("timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n" +
                     "".join(f"{t},0.002,powermetrics,gpu_power,{t-1},{t}\n"
                             for turn in model_turns for t in (WALL_ORIGIN + turn["start_ns"]//NS + 1,
                                                              WALL_ORIGIN + turn["end_ns"]//NS)))
    battery = v.rows(root / "battery.jsonl")
    for row in battery:
        row["epoch_s"] += WALL_ORIGIN
    v.write_rows(root / "battery.jsonl", battery)
    receipt.update(v.derive(root, role, receipt, soak))
    v.put_result(root, receipt)

    check_pairs(v, bundle, events, clock)
    if arm:
        adjust_arm(v, bundle, root, receipt, arm, first_entry, spec.deadman_s)
    terminal = v.read(root / v.rt.CUSTODY_NAME)
    for field in ("started_epoch_s", "ended_epoch_s"):
        terminal[field] += WALL_ORIGIN
    v.rt.write_custody(root, terminal)


def adjust_arm(v, bundle, root, receipt, op, entry, duration):
    doc_path = bundle / "outputs/align_episode.json"
    meta_path = bundle / "metadata.json"
    doc, meta = v.read(doc_path), v.read(meta_path)
    budget = doc["hardware"]["token_budget"]
    copied = meta["workload_provenance"]["episode_outcome"]["token_budget"]
    span = round(duration * NS)
    arm = budget["deadline_ns"] - span
    assert copied == budget and arm == entry - WORK_NS
    if op == "before":
        return
    session = v.rows(bundle / "outputs/align_thermal.jsonl")[0]["started"]["monotonic_ns"]
    value = {"after": entry + 1 + span, "early": session - 1 + span,
             "one-copy": budget["deadline_ns"] + 1}[op]
    budget["deadline_ns"] = value
    v.write(doc_path, doc)
    if op != "one-copy":
        copied["deadline_ns"] = value
        v.write(meta_path, meta)
        if "deadman" in receipt:
            receipt["deadman"]["deadline_ns"] = value
            v.put_result(root, receipt)


def check_pairs(v, bundle, events, clock):
    # Independently derive the expected bounds from the frozen sampler, including
    # its integer-record restoration for the closing witness. Check every pair.
    from joulewise.align.apple.sampler import _restore_stamp, _stamp_record, monotonic_ns, seconds_ns, stamp_mapping
    from joulewise.clock import ClockStamp

    doc_path = bundle / "outputs/align_episode.json"
    doc = v.read(doc_path)
    records = v.rows(bundle / "outputs/align_turns.jsonl")
    outer = doc["hardware"]["paired_clock_stamps_ns"][-1]
    tools = {(e["metadata"]["align_turn_index"], e["event_type"]): e for e in events
              if e["phase"].startswith("align_tool_")}
    for i, turn in enumerate(doc["turns"]):
        end = ClockStamp(**records[i]["end_stamp"])
        following = (ClockStamp(**records[i + 1]["start_stamp"]) if i + 1 < len(records)
                     else _restore_stamp(outer))
        mapping, _ = stamp_mapping((end, following), episode_domain=doc["clock_domain"])
        call, = turn["tool_calls"]
        for edge in ("start", "end"):
            label = (i, edge)
            event = tools[i, "phase_" + edge]["timestamp_s"]
            stamp, lost = clock.witness[label]
            value = call[edge + "_ns"]
            assert event == stamp.epoch_s and value == monotonic_ns(stamp)
            center = seconds_ns(event) + mapping.offset_ns
            held = label == clock.target and clock.side.startswith("held-")
            bound = mapping.uncertainty_ns
            if not held:
                assert abs(value - center) <= bound
            if i + 1 == len(records):
                closing = doc["end_ns"]
            else:
                closing = next(g["start_ns"] for g in doc["hardware"]["thermal"]["intervals"]
                               if g["kind"] == "G1" and g["turn"] == i + 1)
            before, after = ((turn["end_ns"], call["end_ns"]) if edge == "start"
                             else (call["start_ns"], closing))
            margin = min(value - before, after - value)
            assert margin >= 0 and abs(value - center) <= bound + margin
            if held:
                assert abs(value - center) > bound
                assert (value > center) == (clock.side == "held-before")
            # The pin's old hull uses the serialized closing record directly.
            following_ns = _stamp_record(following) if i + 1 < len(records) else outer
            pad = round(ulp(event) * NS)
            lo = seconds_ns(event) - pad + min(seconds_ns(end.monotonic_before_s) - seconds_ns(end.epoch_s),
                                              following_ns["monotonic_before_ns"] - following_ns["epoch_ns"])
            hi = seconds_ns(event) + pad + max(seconds_ns(end.monotonic_after_s) - seconds_ns(end.epoch_s),
                                              following_ns["monotonic_after_ns"] - following_ns["epoch_ns"])
            if label == clock.target:
                _, end_loss = clock.witness[i, "model-end"]
                next_reading = (clock.witness[i + 1, "model-start"] if i + 1 < len(records) else clock.last_reading)
                next_stamp, next_loss = next_reading
                assert _stamp_record(next_stamp) == following_ns
                if held:
                    assert value < lo or value > hi
                elif clock.side in ("low", "minus"):
                    assert lost == 0 and min(end_loss, next_loss) >= 969 and value < lo
                else:
                    assert lost == 999 and max(end_loss, next_loss) <= 30 and value > hi
                if clock.side in ("minus", "plus"):
                    # Solve each edge with integer arithmetic. A second boundary
                    # on this call remains an unedited read from the frozen workload.
                    lower = (center - bound + before + 1) // 2
                    upper = (center + bound + after) // 2
                    damaged = lower - 1 if clock.side == "minus" else upper + 1
                    edge_value = lower if clock.side == "minus" else upper
                    for test, agrees in ((edge_value, True), (damaged, False)):
                        slack = min(test - before, after - test)
                        assert slack >= 0 and (abs(test - center) <= bound + slack) == agrees
                    call[edge + "_ns"] = damaged
            else:
                assert lo <= value <= hi, (label, value, lo, hi)
    if clock.side in ("minus", "plus"):
        v.write(doc_path, doc)


def stage(v, base, work, case):
    if case.rule == "g0-entry-arm" and case.op == "equal":
        return base
    root = work / "fixture"
    root.mkdir()
    (root / v.pc.KINDS[v.S]).symlink_to(base / v.S, target_is_directory=True)
    soak = v.read(base / "soak/soak_reference.json")
    # A passing D_bank is followed by X_G, so put that later sibling on the
    # same wall origin with ordinary grid phases and no damaged boundary.
    for role in [*v.ROLE.values(), "soak"]:
        if role == case.role or (case.role == v.D and role == v.X):
            copytree(base / role, root / role)
            selected = case.op if role == case.role else None
            is_arm = case.rule == "g0-entry-arm"
            issue_member(v, root / role, role, None if is_arm else selected, soak, selected if is_arm else None)
        else:
            (root / role).symlink_to(base / role, target_is_directory=True)
    return root
