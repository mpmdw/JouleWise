"""Additional public-path controls for RL-220, RL-222 and RL-224."""
from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json
from shutil import copytree
from types import SimpleNamespace as NSpace
from unittest.mock import patch

N = 10**9
TASK_FLAGS = ("scratchpad_rule:upstream_closed_pairs:thinking,system_instructions", "upstream_fixed_initial_state")
IDENTICAL = "repetition.identical_call_and_output:2"
OUTPUT = "repetition.identical_output:2"

# Damage names select their writer-produced parent. Each edit follows issuance.
PARENT = {
    "uncarried-impossible": "task-two", "names-disallow": "same-tool", "turn-carried-missing": "identical",
    "length-raised": "identical", "provenance-only": "identical", "turn-only": "same-output",
    "step-extra-budget": "step-cut", "short-extra-budget": "short-cut", "short-drop-cut": "short-cut",
    "finish-stop": "short-cut", "turn-drop-cut": "short-cut", "stop-returned": "short-cut",
    "stop-budget": "short-cut", "added-final-call": "short-cut", "truncated-budget": "budget-full",
    "missing-budget": "budget-full", "clean-stop-cut": "clean-return", "clean-extra-cut": "clean-return",
    "earlier-drop-cut": "cut-then-return",
}


@dataclass(frozen=True)
class Return:
    tool: str = ""
    argument: int = 0
    cut: bool = False
    parse_flags: tuple = ()


def model_plan(v, role, case, spec, existing):
    op = PARENT.get(case.op, case.op)
    if case.rule == "task-flag-record" and case.expected != "pass":
        op = "task-two"
    flags = []
    if case.rule in ("task-flag-record", "repetition-flag-record"):
        flags = list(TASK_FLAGS)
        if op == "task-three":
            flags.append("sabotage_hint:on")
        if op == "task-repeated":
            flags.append(flags[-1])
    # Alternate names after the witnessed prefix so no other repetition is possible.
    length = spec.max_turns if role == v.P else len(existing)
    script = [Return("read_ledger" if i % 2 == 0 else "list_messages", i) for i in range(length)]
    if role != v.P:
        script[-1] = Return()
    if op in ("same-tool", "identical", "same-output", "three-running"):
        a = Return("read_ledger", 0)
        b = Return("read_ledger", 0 if op == "identical" else 2 if op == "same-output" else 1)
        prefix = [a,b,b] if op == "three-running" else [a,b]
        script[:len(prefix)] = prefix
        for i in range(len(prefix), len(script)):
            if script[i].tool:
                name = "list_messages" if (i - len(prefix)) % 2 == 0 else "read_ledger"
                script[i] = Return(name, i + 4)
    if case.rule == "cut-end-stop":
        cut = Return(cut=True, parse_flags=("unclosed_reasoning_span",))
        read = Return("read_ledger")
        cut_call = Return("read_ledger", cut=True, parse_flags=("malformed_tool_call:unclosed_or_unmatched_envelope",))
        if op == "step-cut": script = [cut]
        elif op == "short-cut": script = [read, cut]
        elif op == "budget-cut": script[-1] = Return(cut=True)
        elif op == "cut-then-return": script = [cut_call, Return()]
        elif op == "cut-end-task": script = [read, Return("end_task", cut=True)]
        elif op == "cut-continues": script[4] = cut_call
        elif op == "clean-return": script = [read, Return()]
        elif op != "budget-full": raise ValueError(op)
    return script, flags


def check_model_shape(v, bundle, case, script, task_flags):
    episode = v.read(bundle / "outputs/align_episode.json")
    turns = v.rows(bundle / "outputs/align_turns.jsonl")
    assert len(episode["turns"]) == len(turns) == len(script)
    for item, turn, raw in zip(script, episode["turns"], turns, strict=True):
        assert [c["name"] for c in turn["tool_calls"]] == ([item.tool] if item.tool else [])
        assert (raw["generation"]["finish_reason"] == "length") == item.cut
        if item.cut:
            assert len(raw["generation"]["output_token_ids"]) == turn["decode_tokens"]
            assert f"turn_token_budget_reached:{raw['turn']}" in raw["flags"]
    if case.rule not in ("task-flag-record", "repetition-flag-record"):
        return
    assert episode["hardware"]["task_diagnostics"]["flags"] == task_flags
    assert [f[5:] for f in episode["flags"] if f.startswith("task.")] == list(dict.fromkeys(task_flags))
    repetition = [[f for f in row["flags"] if f.startswith("repetition.")] for row in turns]
    op = PARENT.get(case.op, case.op)
    expected = {"identical": (1, IDENTICAL), "same-output": (1, OUTPUT),
                "three-running": (2, IDENTICAL)}.get(op)
    assert [(i, f) for i, flags in enumerate(repetition) for f in flags] == ([expected] if expected else [])
    assert [f for f in episode["flags"] if f.startswith("repetition.")] == ([expected[1]] if expected else [])


def stage_tree(v, base, work, case):
    stage = work / "fixture"
    stage.mkdir()
    for role in [*v.ROLE.values(), "soak"]:
        if role == case.role:
            copytree(base / role, stage / role)
        else:
            (stage / role).symlink_to(base / role, target_is_directory=True)
    (stage / v.pc.KINDS[v.S]).symlink_to(stage / v.S, target_is_directory=True)
    return stage


def issue_model(v, stage, case):
    from joulewise.align.apple.endpoint import normalize_model_family
    from joulewise.align.apple.sampler import monotonic_ns, seconds_ns, stamp_mapping
    from joulewise.align.interfaces import ChatMessage, ChatResult, ToolCallRequest
    from joulewise.interfaces import RuntimeEvent
    from joulewise.schemas import BenchmarkConfig

    role = case.role
    root = stage / role
    receipt = v.read(root / v.RECEIPT)
    bundle = root / receipt["bundle"]
    config = BenchmarkConfig.from_mapping(v.read(bundle / "config.json"))
    spec = v.wl.EpisodeSpec.from_text(config.workload_profile.prompt_text)
    ep = v.read(bundle / "outputs/align_episode.json")
    original = ep["turns"]
    thermal = ep["hardware"].get("thermal")
    script, task_flags = model_plan(v, role, case, spec, original)
    gates = thermal["intervals"] if thermal else []
    if gates and len(script) < len(gates):
        del gates[len(script):]
        jp = bundle / "outputs/align_thermal.jsonl"
        journal = []
        for row in v.rows(jp):
            values = row["values"]
            turn = values.get("turn", values.get("gate", {}).get("turn", 0))
            if row["kind"] == "align_thermal_gate" and turn >= len(script):
                continue
            row["seq"] = len(journal) + 1
            journal.append(row)
        v.write_rows(jp, journal)
    budget = ep["hardware"].get("token_budget", {})
    clock = NSpace(ns=gates[0]["start_ns"] if gates else ep["start_ns"])
    def stamp():
        current = v.stamp(clock.ns)
        if role != v.S:
            clock.ns += 1000
        return current
    clock.stamp = stamp
    clock.sleep = lambda s: setattr(clock, "ns", clock.ns+round(s*N))
    def wait(kind, turn=0, deadman=None, **kwargs):
        g, = [g for g in gates if g["kind"] == kind and g["turn"] == turn]
        clock.ns = g["end_ns"]
        if kind == "G0" and role == v.S:
            clock.ns = budget["deadline_ns"]-round(spec.deadman_s*N)
            v.rt.rearm_deadman(deadman, spec.deadman_s, "R1_after_G0_release_and_quiet")
        return g
    session = NSpace(intervals=gates, flags=thermal["flags"] if thermal else [], events=[],
                     episode_reference=thermal["episode_reference"] if thermal else None,
                     start=lambda: None, capture_reference=lambda member: None, wait=wait, record=lambda: thermal)
    def call(tool, raw):
        # Different inputs can intentionally share a response (0 and 2) or differ (0 and 1).
        return json.dumps({"read":tool, "result":json.loads(raw)["page"] % 2},sort_keys=True)
    task = NSpace(task_pair=ep["task_pair"], flags=task_flags, reset=lambda seed:None,
                  system_prompt=lambda condition:"", user_prompt=lambda:"", tool_schemas=lambda:[],
                  call_tool=call, score_main=lambda history:None, score_side=lambda history:None,
                  scratchpad_tags=None, task_description=lambda:"")
    position = 0

    class Endpoint:
        def __init__(self, *args, **kwargs):
            self.model_family = normalize_model_family(config.model.family)
            self.flags, self.events, self.turn_provenance = [], [], []
            self.identity, self.prompt_token_ids = ep["endpoint"], []
            self.tokenizer_provenance, self.cache_policy = {}, {}

        def rendered_prompt_length(self, history, tools):
            return original[min(position,len(original)-1)]["prefill_tokens"]

        def assistant_history_message(self, result):
            return ChatMessage("assistant", "")

        def chat(self, history, **kwargs):
            nonlocal position
            i = position
            item = script[i]
            turn = original[min(i,len(original)-1)]
            # Keep Step D's independently recorded inventory, PM, reference and
            # recovery times. Ungated predecessor turns all fit its 120 s limit.
            offset = i * 5*N if role == v.P else 0
            start = v.stamp(turn["start_ns"] + offset)
            first = v.stamp(turn["first_token_ns"] + offset)
            end = v.stamp(turn["end_ns"] + offset - (0 if role == v.S else 1_000_000))
            clock.ns = monotonic_ns(end) + (0 if role == v.S else 1000)
            mapping, _ = stamp_mapping((start,end),episode_domain=ep["clock_domain"])
            cap = kwargs["max_tokens"]
            count = cap if item.cut else turn["decode_tokens"]
            finish = "length" if item.cut else "stop"
            flags = v.endpoint_classification(finish, count, cap, i) + list(item.parse_flags)
            if item.cut and "unclosed_reasoning_span" in flags:
                flags.append("reasoning_censored_at_token_limit")
            self.flags.extend(flags)
            gen = dict(prompt_token_ids=[30]*turn["prefill_tokens"],output_token_ids=[20]*count,finish_reason=finish)
            self.turn_provenance.append(dict(turn=i,flags=flags,start_stamp=asdict(start),end_stamp=asdict(end),
                                             clock_mapping=asdict(mapping),generation=gen))
            for ts,word,phase,attrs in (
                (start.epoch_s,"phase_start","prefill",{}), (first.epoch_s,"phase_end","prefill",{}),
                (first.epoch_s,"phase_start","decode",{"max_tokens":cap}),
                *((first.epoch_s,"token","decode",{"index":j}) for j in range(count)),
                (end.epoch_s,"phase_end","decode",{"requested_output_tokens":cap,"emitted_tokens":count})):
                self.events.append(RuntimeEvent(ts,word,phase,"synthetic",{"align_turn_index":i,**attrs}))
            calls = (ToolCallRequest(str(i),item.tool,json.dumps({"page":item.argument})),) if item.tool else ()
            position += 1
            return ChatResult(content="",reasoning_text="",tool_calls=calls,prompt_tokens=turn["prefill_tokens"],
                              cached_prompt_tokens=0,completion_tokens=count,reasoning_tokens=0,
                              start_ns=monotonic_ns(start),first_token_ns=seconds_ns(first.epoch_s)+mapping.offset_ns,
                              end_ns=monotonic_ns(end),raw_usage={"joulewise":{"flags":list(flags),"finish_reason":finish}})

    runtime = NSpace(name="synthetic", prepare=lambda *args:v.wl.AdapterResult(ok=True),
                     warmup=lambda *args:v.wl.AdapterResult(ok=True))
    adapter = v.wl.EpisodeRuntimeAdapter(runtime, clock, thermal_factory=lambda *args:session)
    factory = NSpace(**{spec.task_factory.split(":")[1]:lambda **kw:task})
    with patch.object(v.wl,"importlib",NSpace(import_module=lambda _:factory)):
        assert adapter.prepare(config).ok
    assert adapter.warmup(config).ok
    adapter.powermode_reader=lambda:0
    adapter.identity_projection_metadata=lambda cfg:dict(model={},sampler={},output_policy={})
    with patch.object(v.wl,"MlxEndpoint",Endpoint):
        result=adapter.run_workload(config)
    assert position == len(script)
    for name in ("align_episode.json","align_turns.jsonl"):
        (bundle/"outputs"/name).write_text(result.output_artifacts[name])
    check_model_shape(v, bundle, case, script, task_flags)
    extras=[r for r in v.rows(bundle/"events.jsonl") if r["phase"]=="warmup" or r["event_type"]=="run_finalized"
            or (r["phase"]=="align_thermal_gate" and r["metadata"]["turn"]<len(script))]
    events=[*map(asdict,result.events), *extras]
    v.write_rows(bundle/"events.jsonl",sorted(events,key=lambda r:r["timestamp_s"]))
    meta=v.read(bundle/"metadata.json")
    meta["workload_provenance"]=result.workload_provenance
    meta["workload_observed"].update(token_count=result.token_count,output_token_count=result.output_token_count)
    v.write(bundle/"metadata.json",meta)
    return bundle, receipt


def damage(v, bundle, case):
    op=case.op
    ep_file=bundle/"outputs/align_episode.json"
    raw_file=bundle/"outputs/align_turns.jsonl"
    meta_file=bundle/"metadata.json"
    ep,raw,meta=v.read(ep_file),v.rows(raw_file),v.read(meta_file)
    provenance=meta["workload_provenance"]
    flags=(ep["flags"],provenance["flags"])
    diag=ep["hardware"]["task_diagnostics"]
    first="task."+TASK_FLAGS[1]
    last="turn_token_budget_reached:1"
    for f in flags:
        if op=="task-drop":f.remove(first)
        elif op=="task-extra":f.insert(3,"task.planted")
        elif op=="budget-after-task":f.append(f.pop(f.index("turn_budget_reached")))
        elif op=="unknown-flag":f.insert(0,"planted")
        elif op in ("uncarried-impossible","names-disallow"):f.insert(0,OUTPUT)
        elif op=="turn-carried-missing":f.remove(IDENTICAL)
        elif op=="length-raised":f[f.index(IDENTICAL)]=IDENTICAL[:-1]+"3"
        elif op in ("step-extra-budget","short-extra-budget"):f.insert(0,"turn_budget_reached")
        elif op=="short-drop-cut":f.remove(last)
        elif op=="earlier-drop-cut":f.remove("turn_token_budget_reached:0")
        elif op in ("missing-budget","truncated-budget"):f.remove("turn_budget_reached")
        elif op=="clean-extra-cut":f.insert(0,last)
    if op=="diagnostics-drop":diag["flags"].remove(TASK_FLAGS[1])
    elif op=="diagnostics-reorder":diag["flags"].reverse()
    elif op=="diagnostics-type":diag["flags"]=TASK_FLAGS[1]
    elif op=="diagnostics-absent":del ep["hardware"]["task_diagnostics"]
    elif op=="provenance-only":provenance["flags"].remove(IDENTICAL)
    elif op=="turn-only":raw[1]["flags"].remove(OUTPUT)
    elif op=="finish-stop":raw[-1]["generation"]["finish_reason"]="stop"
    elif op=="turn-drop-cut":raw[-1]["flags"].remove(last)
    elif op in ("stop-returned","stop-budget","clean-stop-cut","truncated-budget"):
        provenance["episode_outcome"]["stop_condition"]={"stop-budget":"turn_budget_reached",
            "clean-stop-cut":"turn_token_budget_reached"}.get(op,"episode_returned")
    elif op == "added-final-call":
        turn = ep["turns"][-1]
        calls = turn["tool_calls"]
        begin = calls[-1]["end_ns"] if calls else turn["end_ns"]
        span = ep["end_ns"] - begin
        assert span >= 3
        call = deepcopy(ep["turns"][0]["tool_calls"][0])
        call["start_ns"] = begin + span // 3
        call["end_ns"] = begin + 2 * span // 3
        phase = f"align_tool_{turn['index']}_{len(calls)}"
        metadata = {"align_turn_index": turn["index"], "tool_call_id": "added-final-call"}
        events_path = bundle / "events.jsonl"
        events = v.rows(events_path)
        for key, event_type in (("start_ns", "phase_start"), ("end_ns", "phase_end")):
            events.append(dict(timestamp_s=call[key] / N, event_type=event_type, phase=phase,
                               message=call["name"], metadata=metadata))
        calls.append(call)
        v.write_rows(events_path, sorted(events, key=lambda event: event["timestamp_s"]))
    if op=="truncated-budget":
        del ep["turns"][5:]
        del raw[5:]
        turns = ep["turns"]
        events_path = bundle / "events.jsonl"
        kept_events = []
        guard_events = 0
        for event in v.rows(events_path):
            if event["phase"] == "align_context_check":
                # These pairs have no turn index. They follow admission order.
                guard_events += 1
                if guard_events > 2 * len(turns):
                    continue
            if event["metadata"].get("align_turn_index", -1) < len(turns):
                kept_events.append(event)
        v.write_rows(events_path, kept_events)
        decode = sum(t["decode_tokens"] for t in turns)
        total = decode + sum(t["prefill_tokens"] + t["context_tokens"] for t in turns)
        meta["workload_observed"].update(output_token_count=decode, token_count=total)
        provenance["episode_outcome"]["emitted_tokens"] = decode
        provenance["output_policy"]["emitted_tokens"] = decode
    v.write(ep_file,ep); v.write_rows(raw_file,raw); v.write(meta_file,meta)


def close_model(v, stage, case, *, damage_before_receipt=False):
    root = stage / case.role
    bundle, receipt = issue_model(v, stage, case)
    if damage_before_receipt:
        damage(v, bundle, case)
    receipt.update(v.derive(root, case.role, receipt, v.read(stage / "soak/soak_reference.json")))
    if "prefill_tokens" in receipt:
        turns = v.read(bundle / "outputs/align_episode.json")["turns"]
        receipt["prefill_tokens"] = sum(t["prefill_tokens"] for t in turns)
    v.put_result(root, receipt)
    v.rt.write_custody(root, v.read(root / v.rt.CUSTODY_NAME))
    return bundle, receipt


def issue_dependent_bank(v, base, stage, step):
    # The real Step cut changes its decode-rate calibration and the bank's B_D.
    bank = stage / v.D
    bank.unlink()
    copytree(base / v.D, bank)
    bundle = bank / v.read(bank / v.RECEIPT)["bundle"]
    path = bundle / "config.json"
    config = v.read(path)
    profile = config["workload_profile"]
    spec = json.loads(profile["prompt_text"])
    spec["deadman_s"], spec["max_episode_decode_tokens"] = v.rt.gated_budget(step["slots"])
    spec["thermal"]["chunk_tokens"] = int(step["slots"]["N_chunk"])
    profile["prompt_text"] = v.rt.canonical(spec)
    v.write(path, config)
    meta = v.read(bundle / "metadata.json")
    meta["config_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    v.write(bundle / "metadata.json", meta)
    close_model(v, stage, NSpace(role=v.D, rule="step-dependent-bank", op="ordinary"))


def stage(v, base, work, case):
    if case.rule=="g0-entry-arm":
        return v.issuer_control("tool_pair_clock").stage(v,base,work,case)
    stage=stage_tree(v,base,work,case)
    root=stage/case.role
    if case.rule in ("gate-entry-read","exit-slope-instant"):
        return v.issuer_control("gate_control").issue(v,base,stage,case)
    # RL-225 §3. Let the frozen kit derive all receipt copies from these five edits.
    rebuild = case.rule == "cut-end-stop" and case.op in {
        "step-extra-budget", "short-extra-budget", "short-drop-cut", "truncated-budget", "added-final-call",
    }
    bundle, receipt = close_model(v, stage, case, damage_before_receipt=rebuild)
    if case.role == v.S:
        issue_dependent_bank(v, base, stage, receipt)
    if case.expected != "pass" and not rebuild:
        damage(v, bundle, case)
        v.rt.write_custody(root, v.read(root / v.rt.CUSTODY_NAME))
    return stage
