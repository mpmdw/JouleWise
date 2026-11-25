"""Frozen v4 Part C writer invariants on synthetic inputs.

Set JW_PARTC_REPO to the candidate checkout. Set JW_PARTC_GIT_DIR to a local
object database containing the writer and fixture pins. Run this module with
Python 3.13 -IB. JW_V4_PROOF=1 runs the clean proof, JW_PARTC_INVENTORY=only
checks the case manifest, JW_PARTC_CASE selects names and JW_PARTC_SHARD=i/n
partitions cases. JW_V4_OBSERVE=1 prints the native and archive publications.
The historical runner and separately preserved v3.2 corpus are documented in
BUILDER-BRIEF.md. No checkout, fetch, live hardware call or external model.
"""
from __future__ import annotations

import ast
from bisect import bisect_right
from collections import Counter, defaultdict
from contextlib import ExitStack, contextmanager, redirect_stdout
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import shutil
import io
import importlib
import importlib.abc
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace as NSpace
import unittest
from unittest.mock import patch

ISSUED = "b2e01464d6d4fbf2901ff4d4154df9455104a12a"
FIXTURE = "2d02a6f0e42b7ac7a51ea5d5830867eea9ff2911"
N = 10**9
P, S, D, X = "capture-predecessor-30b", "step-d", "d-bank-benign-s1", "x-g"
SUBJECTS = ("scripts.align_r1_part_c", "scripts.align_r1_part_c_evidence")
RECEIPT = "runtime_result.json"
OUTER = ("soak_reference.json", "soak_row.json")
DESCRIPTOR_FIELD = "model_descriptor_sha256"
LIMIT_FIELD = "context_limits.max_position_embeddings"
REG = "joulewise/align/apple/v4_registration.py"
HERE = Path(__file__).resolve()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def read(path):
    return json.loads(path.read_bytes())


def rows(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()]


def write(path, value):
    path.write_bytes(encode(value) + b"\n")


def write_rows(path, records):
    path.write_bytes(b"".join(encode(row) + b"\n" for row in records))


def git(*args):
    override = os.environ.get("JW_PARTC_GIT_DIR")
    return subprocess.check_output(
        ["git", *(["--git-dir=" + override] if override else ["-C", str(repo())]), *args],
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0",
             "GIT_ALLOW_PROTOCOL": ""}, cwd=tempfile.gettempdir())


def repo():
    if "JW_PARTC_REPO" in os.environ:
        return Path(os.environ["JW_PARTC_REPO"]).resolve()
    return next(root for root in (Path.cwd(), *HERE.parents)
                if (root / "scripts/align_r1_part_c.py").is_file())


class Sources(importlib.abc.MetaPathFinder):
    """Materialize only imported Python source and explicit public kit templates."""

    def __init__(self, directory):
        self.root = directory
        self.blobs = {}
        for rev in (FIXTURE, ISSUED):
            tree = git("ls-tree", "-r", rev, "--", "joulewise", "scripts", "tests", "configs")
            self.blobs[rev] = {path.decode(): desc.split()[2].decode() for line in tree.splitlines()
                               for desc, path in [line.split(b"\t", 1)] if desc.startswith(b"100")}
        self.put(REG, ISSUED)
        tree = ast.parse((directory / REG).read_bytes())
        self.frozen = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                           and any(getattr(t, "id", None) == "R1_EXECUTED_SOURCES" for t in n.targets))
        if len(set(self.frozen)) != 10:
            raise RuntimeError("issued R1 executed-source inventory changed")
        for path in self.frozen:
            self.put(path, ISSUED)
        for path in self.blobs[FIXTURE]:
            if (path == "configs/campaigns/align_v4/night_plan.template.json" or re.fullmatch(
                    r"configs/campaigns/align_v4/stages/episodes-[ab]/align-[\w-]+-e\d+\.json",
                    path)):
                self.put(path, FIXTURE)

    def put(self, path, rev):
        target = self.root / path
        if target.is_file():
            return target
        oid = self.blobs[rev][path]
        # An optional source cache saves a cat-file process. Git's blob ID must match.
        cache = os.environ.get("JW_PARTC_SOURCE_CACHE")
        payload = None
        if cache and (Path(cache) / path).is_file():
            raw = (Path(cache) / path).read_bytes()
            if hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == oid:
                payload = raw
        if payload is None:
            payload = git("cat-file", "blob", oid)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return target

    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition(".")[0] not in {"joulewise", "scripts", "tests"}:
            return None
        stem = fullname.replace(".", "/")
        if fullname in SUBJECTS:
            return importlib.util.spec_from_file_location(fullname, repo() / (stem + ".py"))
        for relative in (stem + "/__init__.py", stem + ".py"):
            rev = ISSUED if (relative in self.frozen or fullname.startswith("joulewise.")) else FIXTURE
            if relative not in self.blobs[rev]:
                continue
            return importlib.util.spec_from_file_location(fullname, self.put(relative, rev))
        if any(name.startswith(stem + "/") for name in self.blobs[FIXTURE]):
            spec = importlib.machinery.ModuleSpec(fullname, None, is_package=True)
            spec.submodule_search_locations = [str(self.root / stem)]
            return spec
        return None


class Disagreement(Exception):
    """An independently observed contradiction in a synthetic attempt."""


def need(condition, field):
    if not condition:
        raise Disagreement(field)


def agree(actual, expected, field):
    # Distinguish bool from int and a missing key from a present null. The
    # producer emits both integer and floating JSON numbers for real scalars.
    if isinstance(expected, dict):
        need(isinstance(actual, dict), field)
        for key, value in expected.items():
            need(key in actual, field + "." + key)
            agree(actual[key], value, field + "." + key)
    elif isinstance(expected, (list, tuple)):
        need(isinstance(actual, (list, tuple)) and len(actual) == len(expected), field)
        for i, value in enumerate(expected):
            agree(actual[i], value, f"{field}[{i}]")
    else:
        need(actual == expected and isinstance(actual, bool) == isinstance(expected, bool), field)


def import_world(directory):
    global rt, r1, tg, wl, desk, fixture, evidence, pc, ClockStamp, BundleReadError
    finder = Sources(directory)
    sys.meta_path.insert(0, finder)
    for path in finder.frozen:
        if path.endswith(".py"):
            importlib.import_module(path[:-3].replace("/", "."))
    from joulewise.align.apple import r1_runtime as rt, thermal_gates as tg, workload as wl, thermal_desk as desk
    from joulewise.clock import ClockStamp
    from joulewise.bundle_read import BundleReadError
    from scripts import align_r1_rehearsal as r1, align_r1_part_c as pc, align_r1_part_c_evidence as evidence
    from tests.align import test_rl145_part_c as fixture
    return finder


def stamp(ns):
    sec = ns / N
    return ClockStamp(sec, sec, sec, 1e-9, 1e-9)


class GateWindow:
    """RL-186 §1.3/1.4. Visibility is by read finish; coverage uses the issued grid."""

    def __init__(self, samples, sensors):
        self.samples = samples
        self.t = [r["monotonic_ns"] for r in samples]
        self.f = [r["finished"]["monotonic_after_ns"] for r in samples]
        need(self.t == sorted(set(self.t)) and self.f == sorted(self.f), "sample order")
        self.keys = tuple(sensors[k] for k in ("s_fast", "s_slow"))
        self.grid = self.t[0] if self.t else 0
        # The actual history deque is 3,600 observations. Every generated
        # member is smaller (including the soak, which has no gate).
        assert len(self.samples) < 3600

    def count(self, t, surely=False):
        return bisect_right(self.f, t - (250_000_000 if surely else 0))

    def window(self, t, count):
        # Keep the first observation as the frozen Coverage grid origin even
        # when the rolling window is much later in the journal.
        start = bisect_right(self.t, t - 61*N - 1, 0, count)
        return self.samples[:min(1, start)] + self.samples[start:count]

    def points(self, s, x):
        need(type(s) is int and type(x) is int and 0 <= x-s <= 1800*N, "gate span")
        tolerance = tg.Coverage(0, self.keys).tolerance_ns
        edges = {s, x}
        for t, f in zip(self.t, self.f):
            for edge in (t, f, f + N//4, t+N, t+59*N, t+60*N, t+61*N, f+60*N, f+61*N, f+60*N+N//4, f+61*N+N//4):
                if s-1 <= edge <= x+1:
                    edges.add(edge)
        for i in range((s-self.grid)//N-1, (x-self.grid)//N+2):
            for offset in (0, -tolerance, tolerance, N//2):
                edges.add(self.grid + i*N + offset)
        return sorted({edge+d for edge in edges for d in (-1, 0, 1) if s <= edge+d <= x})

    def coverage(self, t, surely):
        visible = self.window(t, self.count(t, surely))
        return (tg._window_coverage(visible, t, self.keys)["sample_fraction"] or 0) >= .9

    def slope(self, t, count):
        return tg.slow_slope(self.window(t, count), t, self.keys[1])

    def gate(self, g, begin, policy, ref, deadline):
        k = g["kind"]
        s, x = g["start_ns"], g["end_ns"]
        word = g["outcome"]
        is_g0 = k == "G0"
        n = 10 if is_g0 else 5
        cap = policy.get("g0_cap_s", tg.G0_CAP_DEFAULT_S) if is_g0 else policy["turn_cap_s"]
        points = self.points(s, x)
        agree(g["reference"], ref, "bound gate reference")
        agree(g["entry_stamp"], begin["entry_stamp"], "gate begin stamp")
        agree([begin["gate_kind"], begin["turn"], begin["token_count"]],
              [k, g["turn"], g["token_count"]], "gate begin identity")
        need(g["duration_s"] == (x-s)/N, "N6 duration")
        for when, name in ((s, "entry"), (x, "exit")):
            b = g[name+"_stamp"]
            need(b["monotonic_before_ns"] <= when <= b["monotonic_after_ns"] and
                 round(g[name+"_epoch_s"]*N) == b["epoch_ns"], "gate clock")
        lo, hi = self.count(s, True), self.count(s)
        if is_g0:
            def fault(count):
                recent = [r for r in self.samples[:count] if 0 <= s-r["monotonic_ns"] <= 10*N]
                return bool(recent) and not any(tg._status_observed(r.get("status")) for r in recent)
            need(not fault(lo) and not fault(hi), "U2 status source")
        need(any(self.slope(s, count) == g["entry_slope_c_per_min"] and
                 tg.ThermalSession._entry_values(NSpace(rows=self.samples[:count]), s) == g["entry_sensors"]
                 for count in {lo, hi}), "N5 entry")
        if word in ("released", "timeout"):
            need(all(self.coverage(t, True) for t in points), "U1 coverage")
        if word == "deadman":
            need(deadline is not None and s < deadline <= x, "deadman witness")
            return
        need(deadline is None or deadline > x, "U4 deadline")

        def good(i, first=False):
            row = self.samples[i]
            t, f = self.t[i], self.f[i]
            if ref is None or (not first and i and t-self.t[i-1] > 2*N):
                return False
            if not all(tg.valid_value(key, row["sensors"].get(key)) and
                       row["sensors"][key] <= ref[role+"_c"] + policy["delta_"+role+"_c"]
                       for role, key in zip(("fast", "slow"), self.keys)):
                return False
            lower, upper = max(s, f), min(x, f+3*N//2, t+2*N)
            if is_g0:
                status = row["status"]
                pm = status.get("pm_observed_ns")
                slope = self.slope(t, self.count(t))
                if (type(pm) is not int or status.get("os_level") != 0 or status.get("pm_state") != "Nominal"
                        or slope is None or abs(slope) > .2):
                    return False
                lower, upper = max(lower, pm), min(upper, pm+2*N)
            return lower <= upper

        first = max(lo-1, 0)
        if word == "released":
            need(g["exit_sample_ns"] in self.t, "N1 release identity")
            e = self.t.index(g["exit_sample_ns"])
            need(self.f[e]+1.5*N-s < cap*N, "U3 cap")
            need(self.f[e] <= x <= self.f[e]+1.75*N, "N1 release time")
            agree(g["release"], dict(zip(("fast_c", "slow_c"),
                                         (self.samples[e]["sensors"][key] for key in self.keys))), "N1 values")
            need(e-n+1 >= first and all(good(i, i == e-n+1 and i <= max(hi-1,first))
                                        for i in range(e-n+1,e+1)), "N2-N4 streak")
            need(any(self.slope(at, count) == g["slope_c_per_min"]
                     for at in self.points(self.f[e], x)
                     for count in range(max(e+1, self.count(at, True)), self.count(at)+1)), "N5 exit")
        else:
            streak = 0
            earliest = x
            possible_run = False
            for i in range(first, self.count(x)):
                streak = streak+1 if good(i, i <= max(hi-1,first) and not streak) else 0
                if streak >= n:
                    earliest, possible_run = max(s, self.f[i]), True
                    break
            if word == "timeout":
                need(x-s >= cap*N and not possible_run, "timeout witness")
            elif word == "unobserved":
                low_start = None
                forced = ref is None
                for at in points:
                    if at > earliest:
                        break
                    if self.coverage(at, False):
                        low_start = None
                    elif low_start is None:
                        low_start = at
                    elif at-low_start >= 1.25*N:
                        forced = True
                        break
                need(forced and (not is_g0 or x-s >= min(300, cap)*N), "unobserved witness")
            else:
                raise Disagreement("unknown gate word")


@lru_cache(maxsize=8)
def check_sidecar(raw, gated):
    """Replay the producer's in-memory Sidecar.tick / _write and Coverage.report."""
    from joulewise.hazards.base import Stamp
    docs = [json.loads(line) for line in raw.splitlines()]
    first, last = docs[0], docs[-1]
    policy = rt.sensors_policy(CONFIG)
    stamp_for = lambda r, field: Stamp.from_json(r[field])
    cursor = iter([stamp_for(first,"started")])
    ctx = NSpace(stamp=lambda: next(cursor))
    native = tg.thermal.Sidecar(None, policy, reader=NSpace(), ctx=ctx)
    original_write = native._write
    starts = []
    def capture_start(*args):
        starts.append(original_write(*args))
        return starts[-1]
    with patch.object(native,"_write",capture_start):
        native.start(background=False)
    agree(first, starts[0], "issued sidecar start")
    agree(first["values"], {"thermal":policy}, "sidecar start")
    need(first["kind"] == "session_start" and last["kind"] == "session_end", "sidecar terminals")
    need(first["session"] == native.session and first["seq"] == 1, "sidecar session")
    selected = native.selected
    last_finish = first["finished"]["monotonic_ns"]
    for row in docs[1:-1]:
        a, b = stamp_for(row,"started"), stamp_for(row,"finished")
        need(a.monotonic_ns >= last_finish and b.monotonic_ns >= a.monotonic_ns, "sidecar order")
        last_finish = b.monotonic_ns
        cursor = iter((a,b))
        value = row["values"]
        if row["kind"] == "reading":
            entries = value["readings"]
            need(set(entries) == set(selected), "raw sensor keys")
            inputs = {"values":{k:entries[k]["value"] for k in selected},
                      "errors":{k:entries[k]["error"] for k in selected if entries[k]["error"] is not None},
                      "raw":{k:{a:b for a,b in entries[k].items() if a not in ("value","error")} for k in selected}}
            native.reader.read = lambda keys: inputs
            need("status" in value,"ThermalSession attaches its status callback to each reading")
            native.status_reader = lambda: value["status"]
            expected = native.tick()
        else:
            expected = native.event(row["kind"],value)
        agree(row, expected, "issued sidecar row")
    report_end = last["values"]["coverage"]["span_ns"][1]
    need(last_finish <= report_end <= stamp_for(last,"started").monotonic_ns, "coverage report bracket")
    expected = native._write("session_end", {"collector_error":None,"coverage":native.counter.report(report_end)},
                             stamp_for(last,"started"), stamp_for(last,"finished"))
    agree(last,expected,"issued sidecar coverage")


def observed_gates(bundle, ep, kind):
    thermal = ep.hardware.get("thermal")
    if thermal is None:
        need(kind == P, "thermal evidence")
        return
    gate_snapshot((bundle / "outputs/align_thermal.jsonl").read_bytes(), encode(thermal), kind,
                  ep.hardware["token_budget"]["deadline_ns"])


@lru_cache(maxsize=12)
def gate_snapshot(journal_bytes, thermal_bytes, kind, deadline):
    thermal = json.loads(thermal_bytes)
    if thermal is None:
        need(kind == P, "thermal evidence")
        return
    journal = [json.loads(line) for line in journal_bytes.splitlines()]
    policy = thermal["policy"]
    window = GateWindow(tg.sample_rows(journal), policy["sensors"])
    boundaries = [r["values"] for r in journal if r["kind"] in ("align_thermal_gate", "align_thermal_hold")]
    intervals = thermal["intervals"]
    need(len(boundaries) == 2*len(intervals), "gate event count")
    ref = thermal["window_reference"]
    for i, interval in enumerate(intervals):
        begin, end = boundaries[2*i:2*i+2]
        need((begin["state"], end["state"]) == ("begin", "end"), "gate event order")
        agree(end["gate"], interval, "gate end")
        window.gate(interval, begin, policy, ref, None if kind == S and i == 0 else deadline)
        if interval["kind"] == "G0":
            ref = interval["release"] if interval["outcome"] == "released" else None
            agree(thermal["episode_reference"], ref, "G0 episode reference")


def reference_at_warmup(bundle):
    events = [r for r in rows(bundle / "events.jsonl") if r["phase"] == "warmup"]
    need([r["event_type"] for r in events] == ["stage_started", "stage_completed"], "warmup boundaries")
    first, last = [round(r["timestamp_s"]*N) for r in events]
    ref = read(bundle / "outputs/align_window_reference.json")
    end = ref["span_epoch_ns"][1]
    need(first <= last, "warmup order")
    # The exact call time is unrecorded. The claimed span names the only
    # possible anchor that could reproduce itself. Our synthetic clocks coincide.
    when = min(max(end, first), last)
    session = NSpace(policy={"window_reference": {"role": "capture"}, "sensors": rt.sensors_policy(CONFIG)},
                     reference=None, flags=[], context=None, clock=NSpace(stamp=lambda: stamp(when)),
                     rows=rt.journal_rows(bundle / "outputs/align_thermal.jsonl"))
    with tempfile.TemporaryDirectory() as tmp:
        session.context = NSpace(outputs_dir=Path(tmp), bundle_path=bundle, run_id=bundle.name)
        tg.ThermalSession.capture_reference(session, bundle.name)
        expected = read(Path(tmp) / "align_window_reference.json")
        agree(ref,expected,"issued warmup reference")
    need(session.reference is not None, "warmup capture")
    return session.reference

@lru_cache(maxsize=1)
def endpoint_code():
    # The finish flags belong to the endpoint (a dependency of the frozen
    # workload), upstream of the per-turn raw flag projection.
    import inspect
    import textwrap
    tree = ast.parse(textwrap.dedent(inspect.getsource(wl.MlxEndpoint.chat)))
    body = tree.body[0].body
    begin = next(i for i,n in enumerate(body) if isinstance(n, ast.If) and
                 ast.unparse(n.test) == "finish_reason == 'episode.deadman'")
    end = next(i for i in range(begin+1,len(body)) if isinstance(body[i], ast.Expr) and
               isinstance(body[i].value, ast.Call) and ast.unparse(body[i].value.func) == "provenance.update")
    return compile(ast.Module(body=body[begin:end], type_ignores=[]), "issued-finish", "exec")


@lru_cache(maxsize=1)
def gate_flag_code():
    import inspect
    import textwrap
    body = ast.parse(textwrap.dedent(inspect.getsource(tg.ThermalSession._wait))).body[0].body
    start = next(i for i,n in enumerate(body) if isinstance(n,ast.If)
                 and ast.unparse(n.test) == "unobserved and unreferenced")
    return compile(ast.Module(body=body[start:start+2],type_ignores=[]), "issued-gate-flags", "exec")


def endpoint_classification(reason, tokens, limit, index):
    state = dict(finish_reason=reason, completion_tokens=tokens, max_tokens=limit, turn_index=index, flags=[])
    exec(endpoint_code(), state)
    return state["flags"]


def replay_workload(bundle, ep, *, construct=False):
    """Drive the *whole* frozen admission, model-return, tool and stop loop.

    Replace external calls with recorded model results and synthetic tool
    returns. There is no task re-render and no inference or host observation.
    """
    from dataclasses import replace
    from joulewise.schemas import BenchmarkConfig
    from joulewise.align.apple.endpoint import normalize_model_family
    from joulewise.align.interfaces import ChatMessage
    config = BenchmarkConfig.from_mapping(read(bundle / "config.json"))
    raw = rows(bundle / "outputs/align_turns.jsonl")
    controller = rows(bundle / "events.jsonl")
    meta = read(bundle / "metadata.json")
    spec = wl.EpisodeSpec.from_text(config.workload_profile.prompt_text)
    hw = ep.hardware
    gates = hw.get("thermal", {}).get("intervals", [])
    budget = hw.get("token_budget") or {}
    clock = NSpace(ns=gates[0]["start_ns"] if gates else ep.start_ns)
    clock.stamp = lambda: stamp(clock.ns)
    clock.sleep = lambda sec: setattr(clock, "ns", clock.ns+round(sec*N))
    task = NSpace(task_pair=ep.task_pair, reset=lambda seed: None, system_prompt=lambda condition: "",
                  user_prompt=lambda: "", tool_schemas=lambda: [], call_tool=lambda *args: "{}",
                  score_main=lambda messages: None, score_side=lambda messages: None)
    class ReplayThermal(NSpace):
        holds_suppressed = tg.ThermalSession.holds_suppressed
    thermal = ReplayThermal(policy=spec.thermal, intervals=[], flags=[], events=[], episode_reference=None,
                     record=lambda: hw.get("thermal", {}))
    pos = 0

    def wait(kind, turn=0, deadman=None, token_count=None, defer_resume=False):
        matches = [g for g in gates if g["kind"] == kind and g["turn"] == turn and g["token_count"] == token_count]
        need(len(matches) == 1, "gate admission")
        g, = matches
        thermal.intervals.append(g)
        if g["outcome"] != "released":
            state = dict(self=thermal, kind=kind, turn=turn, reason=g["outcome"],
                         unobserved=g["outcome"]=="unobserved", unreferenced=g["reference"] is None and kind!="G0")
            exec(gate_flag_code(), state)
        clock.ns = g["end_ns"]
        if kind == "G0":
            thermal.episode_reference = g["release"] if g["outcome"] == "released" else None
            if budget.get("deadline_origin") == "R1_after_G0_release_and_quiet":
                rearm = budget["deadline_ns"]-round(spec.deadman_s*N)
                need(clock.ns + rt.STEP_QUIET_S*N <= rearm <= ep.start_ns, "Step-D re-arm")
                clock.ns = rearm
                rt.rearm_deadman(deadman, spec.deadman_s, "R1_after_G0_release_and_quiet")
        return g
    thermal.wait = wait
    thermal.resume_hold = thermal.persist_interval = lambda row: None
    # The synthetic controller and endpoint share exact wall/monotonic stamps.
    # Distinct events at the same timestamp retain their sequence on disk.
    need(all(a["timestamp_s"] <= b["timestamp_s"] for a,b in zip(controller, controller[1:])), "event order")
    need(controller[-1]["event_type"] == "run_finalized" and
         sum(e["event_type"] == "run_finalized" for e in controller) == 1, "finalization")
    guards = [r for r in controller if r["phase"] == "align_context_check"]

    class Endpoint:
        def __init__(self, *args, **kwargs):
            self.deadman = kwargs.get("deadman")
            self.model_family = normalize_model_family(config.model.family)
            self.flags, self.events, self.turn_provenance = [], [], []
            self.identity, self.prompt_token_ids = ep.endpoint, []
            self.tokenizer_provenance, self.cache_policy = {}, {}

        def rendered_prompt_length(self, messages, tools):
            nonlocal pos
            need(pos < len(raw), "unwitnessed admission")
            a, b = guards[2*pos:2*pos+2]
            need(a["event_type"] == "phase_start" and b["event_type"] == "phase_end", "context order")
            start, end = (round(r["timestamp_s"]*N) for r in (a, b))
            need(start <= end, "context bracket")
            if spec.deadman_s is not None:
                need(end < budget["deadline_ns"], "admitted context bracket")
            clock.ns = end
            return len(raw[pos]["generation"]["prompt_token_ids"])

        def chat(self, messages, **kwargs):
            nonlocal pos
            need(pos < len(ep.turns) and pos < len(raw), "unwitnessed model call")
            t, r = ep.turns[pos], raw[pos]
            need(r["turn"] == t.index == pos, "turn order")
            ids = r["generation"]
            def mono(name):
                a = r[name]["monotonic_before_s"]
                b = r[name]["monotonic_after_s"]
                need(a <= b, name)
                return round((a + (b-a)/2)*N)
            start, end = mono("start_stamp"), mono("end_stamp")
            need(start <= end and start == t.start_ns and end == t.end_ns, "endpoint clock")
            emitted = [e for e in controller if e.get("metadata", {}).get("align_turn_index") == pos]
            phases = [e for e in emitted if e["phase"] in ("prefill", "decode")]
            count = len(ids["output_token_ids"])
            need([(e["phase"], e["event_type"]) for e in phases] ==
                 [("prefill","phase_start"), ("prefill","phase_end"), ("decode","phase_start"),
                  *[("decode","token")]*count, ("decode","phase_end")], "native phase and token order")
            first_ns = round(phases[1]["timestamp_s"]*N)
            need(start <= first_ns <= end and first_ns == t.first_token_ns, "first token")
            need(phases[0]["timestamp_s"]*N == start and
                 round(phases[-2]["timestamp_s"]*N) <= round(phases[-1]["timestamp_s"]*N) <= end,
                 "native decode-end bracket")
            need([e["metadata"]["index"] for e in phases[3:-1]] == list(range(count)), "token indices")
            need(phases[-1]["metadata"]["emitted_tokens"] == count and
                 phases[-1]["metadata"]["requested_output_tokens"] == kwargs["max_tokens"], "token cap")
            tool_events = [e for e in emitted if e["phase"].startswith("align_tool_")]
            need(len(tool_events) == len(t.tool_calls)*2, "tool event count")
            calls = []
            for i,c in enumerate(t.tool_calls):
                a,b = tool_events[2*i:2*i+2]
                need((a["event_type"],b["event_type"]) == ("phase_start","phase_end") and
                     a["phase"] == b["phase"] == f"align_tool_{pos}_{i}" and
                     a["message"] == b["message"] == c.name and a["metadata"] == b["metadata"] and
                     round(a["timestamp_s"]*N) == c.start_ns and round(b["timestamp_s"]*N) == c.end_ns,
                     "tool order, identity or time")
                if spec.deadman_s is not None:
                    need(b["timestamp_s"]*N < budget["deadline_ns"], "tool deadman bracket")
                calls.append(NSpace(name=a["message"], arguments_json="{}", call_id=a["metadata"]["tool_call_id"]))
            from joulewise.align.apple.endpoint import _StreamObservation
            def stream():
                for j, event in enumerate(phases[3:-1]):
                    clock.ns = round(event["timestamp_s"]*N)
                    yield NSpace(finish_reason=ids.get("finish_reason") if j+1==count else None)
            observed = _StreamObservation(NSpace(stream_generate=stream), deadman=self.deadman,
                                          max_tokens=kwargs["max_tokens"], thermal=thermal if gates else None,
                                          turn_index=pos)
            # There are no live arrays in a synthetic token stream.
            with patch.object(tg, "drain_decode", lambda stream: None):
                need(sum(1 for _ in observed.stream_generate()) == count, "frozen stream cap/deadman")
            capflags = endpoint_classification(observed.finish_reason, count, kwargs["max_tokens"], pos)
            need(all(flag in r["flags"] for flag in capflags) and
                 (f"turn_token_budget_reached:{pos}" in r["flags"]) ==
                 (f"turn_token_budget_reached:{pos}" in capflags), "native finish classification")
            self.flags.extend(r["flags"])
            self.turn_provenance.append({"flags": list(r["flags"])})
            clock.ns, pos = end, pos+1
            return NSpace(prompt_tokens=len(ids["prompt_token_ids"]), cached_prompt_tokens=t.context_tokens,
                          completion_tokens=len(ids["output_token_ids"]), reasoning_tokens=t.hidden_tokens,
                          first_token_ns=t.first_token_ns, start_ns=start, end_ns=end,
                          tool_calls=calls, raw_usage={"joulewise": {"flags": r["flags"]}})

        def assistant_history_message(self, result):
            return ChatMessage("assistant", "")

    # Use an isolated model descriptor and factory. Never import a module or
    # open a model path named by a damaged execution config.
    model_dir = MODEL_DIR
    safe_config = replace(config, model=replace(config.model, source=str(model_dir)))
    task.scratchpad_tags, task.task_description = None, lambda: ""
    fake_factory = NSpace(**{spec.task_factory.split(":")[1]: lambda **kw: task})
    runtime = NSpace(name="synthetic", prepare=lambda *args: wl.AdapterResult(ok=True),
                     warmup=lambda *args: wl.AdapterResult(ok=True))
    thermal.start = thermal.close = lambda: None
    # The real capture is invoked through the Segment replay with its stage bracket.
    thermal.capture_reference = lambda member: None
    adapter = wl.EpisodeRuntimeAdapter(runtime, clock, thermal_factory=lambda *args: thermal)
    with patch.object(wl, "importlib", NSpace(import_module=lambda _: fake_factory)):
        prepared = adapter.prepare(safe_config)
    need(prepared.ok, "frozen preparation")
    agree(hw["context_limits"], {k: adapter.prepared[k] for k in ("max_context_tokens","max_position_embeddings")},
          "native context limits")
    need(adapter.warmup(safe_config).ok, "frozen warmup")
    adapter.powermode_reader = lambda: hw["ac_powermode"]["value"]
    adapter.identity_projection_metadata = lambda config: dict(model={}, sampler={}, output_policy={})
    with patch.object(wl, "MlxEndpoint", Endpoint):
        result = adapter.run_workload(config)
    need(pos == len(raw) == len(ep.turns), "frozen stopped before claimed admissions")
    agree(gates, thermal.intervals, "frozen G0/G1/H sequence")
    provenance = meta["workload_provenance"]
    outcome = result.workload_provenance["episode_outcome"]
    agree(provenance["episode_outcome"]["stop_condition"], outcome["stop_condition"], "primary_stop")
    agree(provenance["episode_outcome"]["emitted_tokens"], outcome["emitted_tokens"], "emitted tokens")
    if budget:
        agree(budget, outcome["token_budget"], "frozen budget")
    flags = result.workload_provenance["flags"]
    if not construct and gates:
        agree(hw["thermal"]["flags"],thermal.flags,"frozen thermal flags")
    if construct:
        raw_ep = read(bundle / "outputs/align_episode.json")
        raw_ep["flags"], provenance["flags"] = flags, flags
        write(bundle / "outputs/align_episode.json", raw_ep)
        write(bundle / "metadata.json", meta)
    else:
        agree(read(bundle / "outputs/align_episode.json")["flags"], flags, "frozen flags")
        agree(provenance["flags"], flags, "provenance flags")


def derive(segment, kind, claim, soak):
    """Dispatch via the same Segment entry point as the issued runtime CLI."""
    from joulewise.schemas import BenchmarkConfig

    class Replay(rt.Segment):
        def __init__(self):
            self.out, self.kind, self.config, self.soak = segment, kind, CONFIG, soak
            self.duration_s = next(d for n, _, d, _ in r1.phase_plan() if n == "idle_soak")
            self.backend = NSpace(name="production", pm_samples=desk.native_pm_samples)
            self.open_session = lambda *args: NSpace(session=None)
            self.close_session = lambda managed: None
            self.idle = lambda *args: None

        def run_member(self, config_map, hook=None):
            bundles = list((self.out / "runs").iterdir())
            need(len(bundles) == 1, "one bundle")
            bundle, = bundles
            ep = wl.read_episode_bundle(bundle)
            summary = read(bundle / "summary_metrics.json")
            need(bundle.name == config_map["run_id"], "frozen bundle identity")
            generated = BenchmarkConfig.from_mapping(config_map).to_dict()
            actual = read(bundle / "config.json")
            # Compare prompt objects independently of their JSON whitespace.
            for cfg in (generated, actual):
                profile = cfg["workload_profile"]
                profile["prompt_text"] = json.loads(profile["prompt_text"])
            need(actual == generated, "frozen member config")
            if hook:
                session = NSpace(reference=reference_at_warmup(bundle) if kind == S else None,
                                 wait=lambda k, **kw: ep.hardware["thermal"]["intervals"][0])
                hook(session)
                if kind == S:
                    # Run the installed capture hook, including its quiet interval.
                    now = [ep.hardware["thermal"]["intervals"][0]["end_ns"]]
                    self.now_ns = lambda: now[0]
                    self.clock = NSpace(sleep=lambda sec: now.__setitem__(0, now[0]+round(sec*N)))
                    self.quiet_spans = []
                    session.wait("G0")
            wall = claim["slot_detail"]["member_wall_s"] if kind == S else 0
            if kind == S:
                need(wall >= (ep.end_ns-ep.start_ns)/N, "member wall lower bound")
            return NSpace(ep=ep, bundle=bundle, wall_s=wall, status=summary["status"],
                          failure_reason=summary["failure_reason"])

        def start_inventory(self):
            directory = self.out / "inventory"
            inv = read(directory / "r1_classification.json")["inventory"]
            self.inventory = NSpace(inventory=inv, rows=rows(directory / "inventory_journal.jsonl"),
                                    keys=[row["key"] for row in inv["keys"]])

        def stop_inventory(self):
            pass

        def observe_recovery(self, member):
            journal = rows(segment / "recovery/align_thermal.jsonl")
            start = journal[0]["started"]["monotonic_ns"]
            end = journal[-1]["finished"]["monotonic_ns"]
            need(journal[-1]["kind"] == "session_end" and
                 end-member.ep.turns[0].end_ns >= rt.RECOVERY_CAP_S*N, "recovery observation")
            self.now_ns = lambda: start
            return super().observe_recovery(member)

        def thermometry(self, member, **kw):
            # The frozen function publishes a classification. Only its *output*
            # path is redirected; its inventory and observations are unchanged.
            with tempfile.TemporaryDirectory() as tmp:
                self.out = Path(tmp)
                (self.out / "inventory").mkdir()
                try:
                    value = super().thermometry(member, **kw)
                    agree(read(segment / "inventory/r1_classification.json"),
                          read(self.out / "inventory/r1_classification.json"), "classifier")
                    return value
                finally:
                    self.out = segment

    replay = Replay()
    replay.config_sha256 = hashlib.sha256((rt.ROOT / r1.DEFAULT_RUNTIME_CONFIG).read_bytes()).hexdigest()
    load = read(segment / "load_journal.json")
    replay.load_errors = load["errors"]
    replay.load = NSpace(fields=lambda: rt.contract.LoadJournal.fields(NSpace(**load)))
    replay.battery = rt.BatteryJournal(None, None, segment / "battery.jsonl")
    replay.battery.rows = rows(segment / "battery.jsonl")
    for item in replay.battery.rows:
        agree(item, rt.parse_pmset_batt(item["raw"]), "battery raw observation")
    replay.start_journals = replay.stop_journals = lambda: None
    return replay.run()


def issue_segment_journals(segment, kind, *, number_of_ticks=None, closing_epoch=None, load_failure=None, battery_failure=None, tick_spacing=1.0):
    """Drive the issued start/tick/final sequence with synthetic ps, pmset and clocks."""
    offset = EPOCH[kind] - (600 if kind == S else 0)
    ticks = EPOCH[kind] + 1801 - offset
    if number_of_ticks is not None: ticks = number_of_ticks
    now = [float(offset)]
    own_pid = 710 + ("idle", P, S, D, X).index(kind)
    table = f"{own_pid} 1 10.0 synthetic-worker\n25 1 10.0 synthetic-other\n"
    def run(argv):
        if tuple(argv) == tuple(rt.contract.PS_ARGV):
            if now[0] == load_failure: raise ValueError("synthetic tick read")
            return NSpace(returncode=0, stdout=table)
        assert tuple(argv) == tuple(rt.PMSET_BATT)
        if now[0] == battery_failure: raise ValueError("synthetic battery read")
        return NSpace(returncode=0, stdout="Now drawing from 'AC Power'\n -InternalBattery-0 80%; charged;")
    callbacks = []
    def ticker(callback):
        callbacks.append(callback)
        return lambda: None
    backend = NSpace(clock=None, ticker=ticker, epoch=lambda: now[0], monotonic=lambda: now[0], run_cmd=run)
    with patch.object(rt.os, "getpid", return_value=own_pid):
        writer = rt.Segment(kind=kind, out=segment, duration_s=None, soak=None, config=CONFIG,
                            config_sha256="", backend=backend)
    battery_path = segment / "battery.jsonl"
    # The upstream test transport emits a placeholder. This is the producer phase,
    # before any test case is selected, copied, bound or judged.
    battery_path.unlink(missing_ok=True)
    writer.start_journals()
    tick, = callbacks
    for i in range(1, ticks + 1):
        now[0] = float(offset + i*tick_spacing)
        tick()
    now[0] = float(offset + ticks + 1) if closing_epoch is None else closing_epoch
    writer.stop_journals()
    load = read(segment / "load_journal.json")
    assert len(load["cpu_busy_t_s"]) + len(load["errors"]) == ticks
    assert len(load["errors"]) == int(load_failure is not None)
    assert [p["label"] for p in load["census"]] == ["start", "end"]
    assert all(own_pid in {p["pid"] for p in point["processes"]} for point in load["census"])
    period = int(CONFIG.get("battery_poll_s", 30))
    assert len(rows(battery_path)) == 2 + ticks // period


def issue_synthetic_control(case, segment, kind, receipt):
    issue_segment_journals(segment, kind)
    if kind in (P, D, X):
        path = segment / receipt["bundle"] / "events.jsonl"
        events = rows(path)
        assert events[-1]["event_type"] == "run_finalized"
        events[-1]["timestamp_s"] = EPOCH[kind] + 1801.5
        write_rows(path, events)
    if kind == P:
        # The predecessor has zero trace rows. Use the issued D-018 writer's
        # header before replay and ledger close, including in the clean launch.
        from joulewise.bundle_read import POWER_TRACE_HEADER
        (segment / receipt["bundle"] / "power_trace.csv").write_bytes(
            (POWER_TRACE_HEADER + "\n").encode("ascii"))
    if kind == S:
        bundle = segment / receipt["bundle"]
        events = rows(bundle / "events.jsonl")
        cfg = read(bundle / "config.json")
        end = read(bundle / "outputs/align_window_reference.json")["span_epoch_ns"][1]/N
        for direction in ("started", "completed"):
            t = end if direction == "started" else end + cfg["sampling"]["warmup_seconds"]
            events.append(dict(event_type="stage_"+direction, phase="warmup", timestamp_s=t,
                               message="stage warmup "+direction, metadata={} if direction == "started" else
                               dict(warmup_runs=cfg["workload_profile"]["warmup_runs"],
                                    warmup_seconds=cfg["sampling"]["warmup_seconds"])))
        write_rows(bundle / "events.jsonl", sorted(events, key=lambda r:r["timestamp_s"]))
        directory = segment / "inventory"
        classifier = read(directory / "r1_classification.json")
        src = directory / "inventory_journal.jsonl"
        original = rows(src)
        keys = sorted(original[0]["values"]["sensors"])
        inventory = dict(complete=True, errors={}, unsupported_types={}, keys=[
            dict(key=k, data_type="flt " if k.startswith("T") else "fpe2",
                 data_size=4 if k.startswith("T") else 2, unit="degC" if k.startswith("T") else "rpm",
                 initial_value=35.0 if k.startswith("T") else 1200.0) for k in keys])
        sensor = NSpace(enumerate_sensors=lambda: inventory)
        now = [0]
        src.unlink()
        producer = rt.InventoryJournal(sensor, lambda: now[0], src)
        producer.start()
        first = original[0]["started"]["monotonic_ns"]
        last = original[-1]["finished"]["monotonic_ns"]
        by_stamp = {row["started"]["monotonic_ns"]:row["values"]["sensors"] for row in original}
        for t in range((EPOCH[kind]-600)*N, (EPOCH[kind]+1802)*N, N):
            now[0] = t
            observed = by_stamp.get(t, original[0 if t < first else -1]["values"]["sensors"])
            sensor.read = lambda selected: sensor_reply({k:observed[k] for k in selected})
            producer.sample()
        classifier["inventory"] = inventory
        # derive() below regenerates the classification using this complete sweep.
        ep = wl.read_episode_bundle(bundle)
        turn, = ep.turns
        policy = rt.sensors_policy(CONFIG)
        classification = rt.classify_step(inventory, producer.rows, prefill_ns=turn.start_ns,
                                           last_decode_ns=turn.end_ns, r0_sensors=policy)
        classifier["classification"] = classification
        write(directory / "r1_classification.json", classifier)
        path = segment / "recovery/align_thermal.jsonl"
        rec = rows(path)
        start = rec[0]["started"]["monotonic_ns"] + N
        sensors = rt.sensors_policy(CONFIG)
        events = [("reading", start+i*N, (38., 38.) if i <= 20 else (35.375, 35.375))
                  for i in range(1, rt.RECOVERY_CAP_S+1)]
        write_rows(path, case.journal(sensors, events, start=start, finish=(EPOCH[kind]+1801)*N + N//2))
    elif kind in (D, X):
        # Add a generated trace so the issuing desk reduction can return its
        # numeric gross/owned claims. Never follow a configured host data path.
        bundle = segment / receipt["bundle"]
        ep = read(bundle / "outputs/align_episode.json")
        times = [t for turn in ep["turns"] for t in (turn["start_ns"]/N+1, turn["end_ns"]/N)]
        (bundle / "power_trace.csv").write_text(
            "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n" +
            "".join(f"{t},0.002,powermetrics,gpu_power,{t-1},{t}\n" for t in times))


def check_workload(segment, kind):
    bundle, = (segment / "runs").iterdir()
    ep = wl.read_episode_bundle(bundle)
    observed_gates(bundle, ep, kind)
    replay_workload(bundle, ep)

def new_fixture():
    case = fixture.SoakLauncherBindingTests("test_native_launcher_passes_through_the_soak_and_member_ledgers")
    case.setUp()
    return case


def issue_model_source():
    """Change only the model.source in private fixture copies of the issued templates."""
    configured, _ = rt.load_config(rt.ROOT / r1.DEFAULT_RUNTIME_CONFIG)
    for key in ("model_30b", "d_spam", "d_bank", "x_g"):
        template = rt.resolve(configured["templates"][key])
        assert template.is_relative_to(rt.ROOT)
        config = read(template)
        config["model"]["source"] = str(MODEL_DIR)
        write(template, config)


def clean_bindings(ledger):
    # A verified bundle can supply the path in a supplemental chained row.
    # Its binding belongs to the preceding member until the next return.
    bindings = {role: [] for role in (P, S, D, X)}
    supplemental = set()
    member = None
    for row in ledger:
        # The terminal verdict closes the ledger. It cannot attest X-G's return.
        if "verdict" in row:
            break
        if "manifest" in row:
            member = row["kind"]
        if DESCRIPTOR_FIELD in row:
            role = row.get("kind")
            if member not in bindings or (role in bindings and role != member):
                raise AssertionError("descriptor binding outside its member's return")
            bindings[member].append(row[DESCRIPTOR_FIELD])
            if "manifest" not in row:
                supplemental.add(member)
    return bindings, supplemental


def control(directory):
    global CONFIG, SUPPLEMENTAL_BINDINGS
    case = new_fixture()
    CONFIG = rt.load_config(case.attempt.config)[0]
    ledger_fixture = importlib.import_module("tests.test_part_c_evidence_ledger")
    native_close = fixture.write_terminal
    receipts = {}
    errors = []
    def issue(*args):
        try:
            return issue_one(*args)
        except Exception as error:
            errors.append(error)
            raise
    def issue_one(segment, kind, receipt, sha):
        issue_synthetic_control(case, segment, kind, receipt)
        ref = None if kind == "idle" else read(case.attempt.reference)
        if kind != "idle":
            bundle = segment / receipt["bundle"]
            assert read(bundle / "config.json")["model"]["source"] == str(MODEL_DIR)
            replay_workload(bundle, wl.read_episode_bundle(bundle), construct=True)
        frozen = derive(segment, kind, receipt, ref)
        receipt.update(frozen)
        if kind != "idle":
            check_workload(segment, kind)
        process = native_close(segment, kind, receipt, sha)
        manifest = read(segment / rt.CUSTODY_NAME)
        begin, end = terminal_window(kind)
        manifest.update(started_epoch_s=begin, ended_epoch_s=end)
        write(segment / rt.CUSTODY_NAME, manifest)
        receipts[kind] = receipt
        return process
    try:
        with patch.object(fixture, "write_terminal", issue), patch.object(ledger_fixture, "write_terminal", issue):
            def model(kind, directory):
                try:
                    return case.make_model_member(kind,directory)
                except Exception as error:
                    errors.append(error)
                    raise
            class LaunchClock:
                def __getattr__(self, name):
                    return getattr(real_clock, name)
            real_clock = fixture.smoke.time
            clock = LaunchClock()
            clock.time_ns = iter(n*N for n in terminal_window("idle")).__next__
            with patch.object(fixture.smoke, "time", clock):
                rc = case.run_launcher(model_transport=model)
        if errors:
            raise errors[0]
        if not (case.attempt.output / "smoke.json").exists():
            raise AssertionError(f"control did not reach native adjudication after {list(receipts)}")
        verdict = published(case, rc)
        need(verdict == "pass", "clean control: " + verdict)
        for kind in receipts:
            source = case.attempt.segment if kind == "idle" else case.attempt.output / pc.KINDS[kind]
            shutil.copytree(source, directory / kind)
        shutil.copytree(case.attempt.directory, directory / "soak")
        write(directory / "reference.json", read(case.attempt.reference))
        bindings, SUPPLEMENTAL_BINDINGS = clean_bindings(rows(case.attempt.output / "evidence_ledger.jsonl"))
        expected = hashlib.sha256((MODEL_DIR / "config.json").read_bytes()).hexdigest()
        return [role for role, seen in bindings.items() if seen != [expected]]
    finally:
        case.doCleanups()


def published(case, rc):
    output = case.attempt.output
    doc = read(output / "smoke.json")
    if doc != read(output / "smoke_part_c.json"):
        raise AssertionError("disagreeing native publications")
    result = doc["evaluation"]
    word = result["verdict"]
    runner = read(case.attempt.root / "runner_receipt.json")
    ledger = rows(output / "evidence_ledger.jsonl")[-1]
    if not (ledger["verdict"] == word and rc == runner["rc"] and
            (rc == 0) is result["pass"] is runner["parts"]["C"] is (word == "pass") and
            f"Part C verdict: {word} (pass: {result['pass']})" in
            (case.attempt.root / "part-c.stdout.log").read_text().splitlines()):
        raise AssertionError("disagreeing evaluator, ledger, stdout or launcher exit")
    if word != "pass" and os.environ.get("JW_PARTC_DEBUG"):
        print("REFUSED", result["evidence_failures"], flush=True)
    return word


# Matrix construction uses only files in the test-created corpus. Names and
# field sets are taken from the serialized records, including heterogeneous
# JSONL rows and the JSON-encoded episode specification.
@dataclass(frozen=True)
class Mutation:
    role: str
    file: str
    path: tuple
    op: str

    @property
    def name(self):
        return "/".join((self.role, self.file, ".".join(map(str, self.path)), self.op))


@dataclass(frozen=True)
class DescriptorCase:
    role: str
    op: str

    @property
    def name(self):
        return f"{self.role}/descriptor/{self.op}"


def load_doc(path):
    import csv
    import plistlib
    if path.suffix == ".jsonl":
        return rows(path)
    if path.suffix == ".csv":
        return list(csv.DictReader(path.read_text().splitlines()))
    if path.suffix == ".plist":
        return [plistlib.loads(payload) for payload in path.read_bytes().split(b"\0")]
    value = read(path)
    if path.name == "config.json":
        profile = value["workload_profile"]
        profile["prompt_text"] = json.loads(profile["prompt_text"])
    return value


def save_doc(path, doc):
    import csv
    import plistlib
    if path.suffix == ".jsonl":
        write_rows(path, doc)
    elif path.suffix == ".csv":
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for row in doc for k in row)))
            writer.writeheader()
            writer.writerows(doc)
    elif path.suffix == ".plist":
        path.write_bytes(b"\0".join(plistlib.dumps(row) for row in doc))
    else:
        if path.name == "config.json" and isinstance(doc.get("workload_profile"), dict):
            profile = doc["workload_profile"]
            if "prompt_text" in profile:
                profile["prompt_text"] = json.dumps(profile["prompt_text"], sort_keys=True)
        write(path, doc)


def shape(value):
    """Find each structural row variant, even when it first occurs late in a stream."""
    if isinstance(value, dict):
        tags = tuple(str(value.get(key, "")) for key in ("kind", "event_type", "phase", "state", "outcome"))
        return (tags, tuple((k, shape(v)) for k, v in sorted(value.items())))
    if isinstance(value, list):
        return ("list", tuple(sorted({str(shape(v)) for v in value})))
    return type(value).__name__


def fields(value, prefix=()):
    # Arrays of samples, tokens and turns contribute every record *field*;
    # repeating an identical schema 1,800 times adds no new field. Preserve
    # acquisition-order tests on the entire array as well.
    if isinstance(value, dict):
        children = value.items()
    elif isinstance(value, list):
        seen = set()
        children = []
        for i, v in enumerate(value):
            sig = shape(v)
            if sig not in seen or os.environ.get("JW_PARTC_ALL_OCCURRENCES") == "1":
                seen.add(sig)
                children.append((i, v))
    else:
        return
    for key, v in children:
        path = prefix+(key,)
        yield path, v
        yield from fields(v, path)


def applicable(path, v, suffix):
    # plist has no null representation; its type, key and deletion probes
    # remain valid plist encodings. CSV has its own string-only wire format.
    yield "delete"
    if suffix not in (".plist", ".csv") and v is not None:
        yield "null"
    if not (suffix == ".csv" and not isinstance(path[-1], str)):
        yield "type"
    if type(v) in (float, int):
        yield "shift"
    if isinstance(v, str) and v in (CONFIG["sensors"]["s_fast"], CONFIG["sensors"]["s_slow"]):
        yield "swap-sensor"
    if isinstance(path[-1], str):
        yield "key"
    if isinstance(v, list) and len(v) > 1 and v != v[::-1]:
        yield "reorder"


def cases(base):
    for kind in ("idle", P, S, D, X):
        directory = base / kind
        for path in sorted(p for p in directory.rglob("*") if p.is_file()):
            relative = path.relative_to(directory).as_posix()
            value = load_doc(path)
            # Also perturb every occurrence in every repeated row. These
            # file-wide sweeps supplement the individually attributable cases.
            if isinstance(value, (list,dict)) and len(value)>1:
                for op in ("type", "null", "shift", "key", "delete", "reorder"):
                    if op == "null" and path.suffix in (".plist",".csv"):
                        continue
                    case = Mutation(kind, relative, (), "every-"+op)
                    if mutate(case, value) != value:
                        yield case
            if isinstance(value, list) and len(value) > 1:
                yield Mutation(kind, relative, (), "reorder")
            for chain, v in fields(value):
                if isinstance(chain[-1], str) and not isinstance(v,(dict,list)):
                    parent = value
                    for key in chain[:-1]:
                        parent = parent[key]
                    other = next((k for k,item in parent.items() if k > chain[-1] and
                                  type(item) is type(v) and item != v), None)
                    if other:
                        yield Mutation(kind, relative, chain, "swap-with="+other)
                for op in applicable(chain, v, path.suffix):
                    yield Mutation(kind, relative, chain, op)
    for name in OUTER:
        for chain, v in fields(read(base / "soak" / name)):
            for op in applicable(chain, v, ".json"):
                yield Mutation("idle", name, chain, op)
    for role, file, ops in (
        (S, "runs/member/events.jsonl", ("warmup-shift", "warmup-delete", "warmup-duplicate")),
        (S, "recovery/align_thermal.jsonl", ("short-recovery",)),
        (D, "runs/member/outputs/align_turns.jsonl", ("xml-malformed",)),
        (S, RECEIPT, ("swap-picks",)),
        (D, "runtime_custody.json", ("overlap-previous",)),
        (D, "runs/member/outputs/align_thermal.jsonl", ("poll-ambiguity",)),
    ):
        if file.startswith("runs/member/"):
            bundle, = (base / role / "runs").iterdir()
            file = file.replace("runs/member/",f"runs/{bundle.name}/",1)
        for op in ops:
            yield Mutation(role, file, (), op)
    for role in (P, S, D, X):
        for op in ("rewritten-after-return", "consistent-40961", "mirror-40961-claim-40960", "no-binding"):
            yield DescriptorCase(role, op)


    yield from extra_cases(base)
    yield from issued_cases()

    # RL-193 §1 adds one positive beside the issued v3 matrix.
    bundle, = (base / P / "runs").iterdir()
    trace = (bundle / "power_trace.csv").relative_to(base / P).as_posix()
    yield DecisionCase(P, "raw", trace, (), "d018-interval-header-zero-rows")


@dataclass(frozen=True)
class DecisionCase:
    role: str
    family: str
    file: str
    path: tuple
    op: str
    value: object = None
    audit: str = ""

    @property
    def predecessor_csv_wire(self):
        return self.role == P and self.family == "raw" and Path(self.file).name == "power_trace.csv"

    @property
    def name(self):
        locus = ".".join(map(str, self.path)) or "file"
        suffix = "/" + self.audit if self.audit else ""
        return f"{self.role}/v3/{self.family}/{self.file}/{locus}/{self.op}{suffix}"


GATE_WORDS = ("released", "timeout", "unobserved", "deadman")
GATE_KINDS = ("G0", "G1", "H")
STOP_WORDS = ("episode_returned", "episode.deadman", "runner.error", "thermal.incomplete",
              "episode.g0_unreleased", "episode.decode_budget", "episode.end_task", "episode.time_guard",
              "episode.context_limit", "turn_token_budget_reached", "episode.malformed_tool_call",
              "turn_budget_reached")
DOMAINS = {
    "segment_status": ("inconclusive",),
    "reference_unobserved": (False, True),
    "g0_released": (False, True),
    "g0_outcome": GATE_WORDS,
    "outcome": GATE_WORDS,
    "gate_kind": GATE_KINDS,
    "t_decline_status": ("declined", "no_decline", "unobserved"),
    "os_level": (0, 1, 2, 3),
    "pm_state": ("Nominal", "Fair", "Serious", "Critical"),
    "stop_reason": STOP_WORDS,
    "stop_condition": STOP_WORDS,
    "finish_reason": ("stop", "eos", "length", "max_tokens", "max_new_tokens", "episode.deadman"),
    "deadline_origin": ("G0_entry", "R1_after_G0_release_and_quiet"),
    "condition": ("benign", "sabotage"),
    "warmup_condition": ("benign",),
    "assistant_history": ("reasoning_content",),
    "prompt_cache": ("episode_prefix",),
    "reasoning_effort": ("low", "medium", "high", "PENDING"),
    "anchor": ("warmup_entry",),
    "event_type": ("stage_started", "stage_completed", "phase_start", "phase_end", "token", "run_finalized"),
}
GATE_FLAGS = ("r1.g0_timeout_run", "r1.preheat_cap_reached", "episode.end_task:0",
              "episode.malformed_tool_call:0", "turn_budget_reached", "turn_token_budget_reached:0",
              "thermal.state_unobserved", "thermal.episode_reference_unobserved",
              "thermal.status_source_missing", "thermal.custody_invalid", "model.position_limit_unread",
              "runner.error:synthetic", "unclosed_reasoning_span")


def branch_values(file, chain, current):
    key = chain[-1]
    if key == "failure_reason" and ("summary_metrics" in file or file == RECEIPT):
        from joulewise.schemas import FailureReason
        return tuple(reason.value for reason in FailureReason)
    if key == "comm" and "processes" in chain:
        return ("synthetic-worker", "codex", "claude", "t3")
    if key == "state" and (file.endswith("battery.jsonl") or "battery" in chain):
        return ("charging", "charged", "discharging", "not_charging")
    if key == "name" and "tool_calls" in chain:
        return ("list_messages", "end_task")
    if key == "backend" and file == RECEIPT:
        return ("production", "synthetic")
    if key == "phase" and file.endswith("events.jsonl"):
        if current and current.startswith("align_tool_"):
            return (current, "prefill", "decode")
        return ("warmup", "align_thermal_gate", "align_thermal_hold", "align_context_check", "prefill",
                "tokenize", "generation_setup", "decode", "run", "align_g0_unreleased_stop_observation",
                "align_context_stop_observation")
    if key in DOMAINS:
        return DOMAINS[key]
    if isinstance(current, bool):
        return (False, True)
    if key == "value" and "ac_powermode" in chain:
        return (0, 1, 2)
    if key in ("status", "member_status"):
        if file == rt.CUSTODY_NAME:
            return ("complete", "refused", "failed", "aborted")
        if file.endswith("summary_metrics.json") or key == "member_status":
            from joulewise.schemas import RunStatus
            return tuple(word.value for word in RunStatus)
        if current in ("pass", "fail"):
            return ("pass", "fail")
        if file.endswith("align_window_reference.json"):
            return ("captured", "unobserved")
    if key == "kind":
        if current in GATE_KINDS:
            return GATE_KINDS
        if current in ("idle", P, S, D, X):
            return ("idle", P, S, D, X)
        if file.endswith("align_thermal.jsonl"):
            return ("session_start", "sample", "reading", "align_thermal_gate", "align_thermal_hold", "session_end")
    if key == "state" and current in ("begin", "end"):
        return ("begin", "end")
    if key == "role" and "window_reference" in chain:
        return ("capture", "consume")
    if key == "class" and current in ("light", "heavy"):
        return ("light", "heavy")
    if key == "class" and "ranking" in chain:
        return ("die", "heatsink", "record-only")
    if key == "phase" and "phases" in chain:
        return ("idle", "load", "recovery")
    if key in ("flags", "episode_flags") and isinstance(current, list):
        cuts = [p + ("0" if p.endswith(":") else "") for p in r1.EPISODE_CUT_FLAGS]
        return tuple([flag] for flag in dict.fromkeys(cuts + list(GATE_FLAGS)))
    return ()


def at(value, path):
    for key in path:
        value = value[key]
    return value


def branch_cases(role, file, doc):
    # V2 already supplies missing/null/wrong-type for open-domain present keys.
    # Add explicit absence/null/outside even for omitted optional discriminants.
    selected = {}
    for path, value in fields(doc):
        domain = branch_values(file, path, value)
        if domain:
            selected[path] = domain
        if isinstance(value, dict):
            if {"window_reference", "turn_cap_s", "sensors"} <= value.keys():
                for key in ("g0_cap_receipt", "contrast_fit", "g0_cap_s"):
                    if key not in value:
                        selected[path+(key,)] = ()
            if path[-1] == "status" and "os_level" in value:
                selected[path+("error",)] = ("synthetic reader error",)
            if path[-1] == "ac_powermode":
                selected[path+("error",)] = ("synthetic observer error",)
            if path[-1] == "thermometry":
                for key in ("s7_for_r1_picks", "registered_picks", "reasons", "night_confirmation"):
                    if key not in value:
                        selected[path+(key,)] = ()
    if file == RECEIPT:
        if role == S:
            selected[("segment_status",)] = DOMAINS["segment_status"]
        if role in (S, D):
            selected[("reference_unobserved",)] = DOMAINS["reference_unobserved"]
        if role in (P, "idle"):
            selected[("episode_flags",)] = branch_values(file, ("episode_flags",), [])
        if role == S:
            # RH:1875 reads this only in the inconclusive branch.
            selected[("reason",)] = ("G0 did not release before its cap (LEAD-RULINGS-2 R6-2)",)
    if file.endswith("/config.json"):
        from dataclasses import fields as dataclass_fields
        root = ("workload_profile", "prompt_text")
        spec = at(doc, root)
        for definition in dataclass_fields(wl.EpisodeSpec):
            key = definition.name
            if key not in spec:
                selected[root + (key,)] = DOMAINS.get(key, (False, True) if key == "enable_thinking" else ())
    for path, domain in selected.items():
        # Keep the JSON type where the operand has an enum. Unknown words can
        # select a different default than a parser-level type failure.
        example = next(iter(domain), None)
        outside = (["synthetic-outside-domain"] if isinstance(example,list) else
                   17 if type(example) in (bool,int,float) else "synthetic-outside-domain")
        for label, operand in [("absent", None), ("null", None), ("outside", outside),
                               *(("set-" + (str(item[0]) if isinstance(item, list) else str(item)).lower(), item)
                                 for item in domain)]:
            audit = ""
            if role == S and path == ("segment_status",) and operand == "inconclusive":
                audit = "audit-step-d-inconclusive-released"
            if path == ("reference_unobserved",) and operand is True:
                audit = "audit-" + role + "-reference-unobserved"
            yield DecisionCase(role, "branch", file, path, label, operand, audit)


def bracket_paths(file, doc):
    # A representative of each record shape, plus every distinct paired phase
    # and gate occurrence. Members with repeated turns can have different ends.
    common = (("start_ns", "end_ns"), ("start_ns", "first_token_ns"), ("first_token_ns", "end_ns"), ("start_s", "end_s"), ("started_ns", "ended_ns"),
              ("started_epoch_s", "ended_epoch_s"), ("entry_epoch_s", "exit_epoch_s"),
              ("interval_start_s", "interval_end_s"), ("monotonic_before_ns", "monotonic_after_ns"),
              ("monotonic_before_s", "monotonic_after_s"),
              ("wall_minus_monotonic_lower_s", "wall_minus_monotonic_upper_s"))
    for path, obj in [((), doc), *fields(doc)]:
        if isinstance(obj, dict):
            for start, end in common:
                if start in obj and end in obj:
                    yield path + (start,), path + (end,)
            for start, end in (("started", "finished"), ("start_stamp", "end_stamp"),
                               ("entry_stamp", "exit_stamp"), ("first", "last")):
                if isinstance(obj.get(start), dict) and isinstance(obj.get(end), dict):
                    for key in ("monotonic_ns", "monotonic_raw_ns", "wall_ns", "epoch_ns", "epoch_s",
                                "monotonic_before_ns", "monotonic_after_ns", "monotonic_before_s", "monotonic_after_s"):
                        if key in obj[start] and key in obj[end]:
                            yield path+(start,key), path+(end,key)
        if not isinstance(obj, list) or len(obj) != 2 or not path:
            continue
        if path[-1] == "paired_clock_stamps_ns":
            for key in ("epoch_ns", "monotonic_before_ns", "monotonic_after_ns"):
                yield path+(0,key), path+(1,key)
        elif (path[-1] in ("span_ns", "span_epoch_ns") or "phase_bounds_ns" in path or "gaps_ns" in path
              ) and all(type(x) in (float, int) for x in obj):
            yield path+(0,), path+(1,)
    if file.endswith("events.jsonl"):
        stacks = defaultdict(list)
        last_token = {}
        for i, row in enumerate(doc):
            identity = row["phase"], row["metadata"].get("align_turn_index")
            word = row["event_type"]
            if word == "token":
                last_token[identity] = i
            if word == "phase_end" and identity in last_token:
                yield (last_token.pop(identity),"timestamp_s"), (i,"timestamp_s")
            if word in ("phase_start", "stage_started"):
                stacks[identity].append(i)
            if word in ("phase_end", "stage_completed") and stacks[identity]:
                j = stacks[identity].pop()
                yield (j, "timestamp_s"), (i, "timestamp_s")
    if file.endswith("align_thermal.jsonl"):
        begins = {}
        for clock in ("monotonic_ns", "monotonic_raw_ns", "wall_ns"):
            yield (0,"started",clock), (len(doc)-1,"finished",clock)
        readings = [i for i,row in enumerate(doc) if row["kind"] == "reading"]
        if len(readings) >= 2:
            for clock in ("monotonic_ns", "monotonic_raw_ns", "wall_ns"):
                yield (readings[0],"finished",clock), (readings[1],"started",clock)
        for i, row in enumerate(doc):
            if row["kind"] not in ("align_thermal_gate", "align_thermal_hold"):
                continue
            event = row["values"]
            if event["state"] == "begin":
                begins[row["kind"]] = i
            elif event["state"] == "end":
                j = begins.pop(row["kind"])
                for clock in ("monotonic_ns", "monotonic_raw_ns", "wall_ns"):
                    yield (j,"started",clock), (i,"started",clock)
    if file.endswith("battery.jsonl") and len(doc) > 1:
        yield (0,"epoch_s"), (len(doc)-1,"epoch_s")


def extra_cases(base):
    for role in ("idle", P, S, D, X):
        root = base / role
        files = {p.relative_to(root).as_posix(): p for p in sorted(root.rglob("*")) if p.is_file()}
        if role == "idle":
            files.update({name:base/"soak"/name for name in OUTER})
        for file, path in files.items():
            for form in ("empty", "truncated", "invalid", "wrong-root", "garbage"):
                audit = "audit-one-byte-predecessor-csv" if (
                    role == P and path.name == "power_trace.csv" and form == "garbage") else ""
                yield DecisionCase(role, "raw", file, (), form, audit=audit)
            if role == P and path.name == "power_trace.csv":
                yield DecisionCase(role, "raw", file, (), "d018-header")
                yield DecisionCase(role, "raw", file, (), "three-column-header")
            doc = load_doc(path)
            yield from branch_cases(role, file, doc)
            for start, end in dict.fromkeys(bracket_paths(file, doc)):
                if (isinstance(start[0], int) and isinstance(end[0], int) and start[0] != end[0]
                        and (end[-1] == "timestamp_s" or end[-1] == "monotonic_ns" or end[-1] == "epoch_s")):
                    yield DecisionCase(role, "interval", file, (end[0],), "end-record-missing-from-" + ".".join(map(str,start)), start)
                for op in ("end-before", "end-equal", "end-missing"):
                    yield DecisionCase(role, "interval", file, end, op + "-from-" + ".".join(map(str,start)), start)
            if role == D and file.endswith("outputs/align_thermal.jsonl"):
                yield DecisionCase(role, "interval", file, (), "audit-g0-begin-after-end")
            if file.endswith("/events.jsonl"):
                yield DecisionCase(role, "branch", file, (), "orphan-tokenize")
                yield DecisionCase(role, "branch", file, (), "empty-final-phase")


@dataclass(frozen=True)
class InputCase:
    role: str
    file: str
    op: str

    @property
    def name(self):
        return f"{self.role}/v3/raw/issued/{self.file}/{self.op}"


@dataclass(frozen=True)
class LaunchCase:
    role: str
    op: str

    @property
    def file(self):
        return "stdout" if self.op.startswith("stdout-") else "argv" if self.op.startswith("duration-") else "process"

    @property
    def name(self):
        family = "raw" if self.file == "stdout" else "branch"
        return f"{self.role}/v3/{family}/launch/{self.op}"


def issued_cases():
    sources = [("idle", str(r1.DEFAULT_RUNTIME_CONFIG)), (D, str(r1.W1_PLAN_TEMPLATE)),
               (P, "model.source/config.json")]
    for kind, template in ((P, "model_30b"), (S, "d_spam"), (D, "d_bank"), (X, "x_g")):
        sources.append((kind, CONFIG["templates"][template]))
    for kind, source in sources:
        for form in ("empty", "truncated", "invalid", "wrong-root", "garbage"):
            yield InputCase(kind, source, form)
    for role in ("idle", P, S, D, X):
        for word in ("exit-0", "exit-2-worked", "exit-3", "exit-143",
                     "stdout-empty", "stdout-truncated", "stdout-invalid", "stdout-wrong-root", "stdout-garbage"):
            yield LaunchCase(role, word)
    for word in ("exit-2-unworked", "oserror-unworked"):
        yield LaunchCase(X, word)
    for word in ("duration-1", "duration-1800", "duration-absent"):
        yield LaunchCase("idle", word)


def launch_observation(case, process):
    if case.op == "oserror-unworked":
        raise OSError("synthetic launch observation")
    if case.file == "process":
        process.returncode = int(case.op.split("-")[1])
    elif case.file == "stdout":
        raw = damaged_bytes(Path("stdout.json"), process.stdout.encode(), case.op.removeprefix("stdout-"))
        process.stdout = raw.decode()
    if case.op == "exit-2-unworked":
        process.stdout = ""
    return process


def soak_argv(argv, case):
    argv = list(argv)
    if case.op == "duration-absent":
        del argv[argv.index("--duration-s"):]
    else:
        argv[argv.index("--duration-s")+1] = case.op.removeprefix("duration-")
    return argv


def launch_oracle(case, probe):
    segment = probe.base / case.role
    record = read(segment / RECEIPT)
    duration = next(d for _,k,d,_ in r1.phase_plan() if k == case.role)
    process = NSpace(returncode=0,stdout=json.dumps(record,sort_keys=True)+"\n",stderr="")
    unworked = case.op.endswith("-unworked")
    try:
        with patch.object(r1, "_run", side_effect=lambda argv: launch_observation(case, process)) as transport:
            r1._invoke(["synthetic-runtime"], case.role, segment, duration,
                       soak_reference=None if case.role == "idle" else probe.base/"reference.json",
                       quiet=True, contract_key="idle_soak" if case.role=="idle" else None)
        if case.file == "argv":
            args, = transport.call_args.args
            need(soak_argv(args, case) == args, "frozen soak invocation")
    except (Disagreement, r1.Refusal, OSError) as error:
        if unworked and case.role == X and process.returncode == 2 and process.stdout == "":
            # The stub returned before creating the member directory. ES:28,
            # RL-183 permit precisely this observed refusal. Run frozen Part C
            # on the worked S and D records to decide the remaining lines.
            return None if issued_verdict(probe, include_x=False)["pass"] else "issued non-run verdict"
        return str(error)
    return None


def issued_trial(case):
    # One source tree and one mirror are shared by the workers. The parent
    # runs these cases only after all outstanding readers have completed.
    mirror = case.file == "model.source/config.json"
    path = MODEL_DIR/"config.json" if mirror else rt.ROOT/case.file
    assert path.is_relative_to(MODEL_DIR if mirror else rt.ROOT)
    original = path.read_bytes()
    mismatch = None
    try:
        path.write_bytes(damaged_bytes(path, original, case.op))
        try:
            if mirror:
                check_workload(WORKER.base / case.role, case.role)
            elif case.file == str(r1.DEFAULT_RUNTIME_CONFIG):
                _, digest = rt.load_config(path)
                agree(digest, read(WORKER.base/"idle"/RECEIPT)["config_sha256"], "issued configuration")
            elif case.file == str(r1.W1_PLAN_TEMPLATE):
                r1.check_w1_schedule(["--config",str(rt.ROOT/r1.DEFAULT_RUNTIME_CONFIG)])
            else:
                # Parse the changed template before the synthetic backend
                # consumes the untouched executed configuration.
                rt.read_template(path)
                root = WORKER.tree / pc.KINDS[case.role]
                claim = read(root/RECEIPT)
                frozen_checks(root, case.role, claim, WORKER.ref)
        except (Disagreement, OSError, ValueError, KeyError, IndexError, TypeError, AttributeError,
                rt.Refused, rt.RuntimeFailure, r1.Refusal, wl.AdapterFailure) as error:
            mismatch = type(error).__name__
        # Rebuild the soak chain so row zero observes these issued bytes.
        WORKER.changed_soak = True
        accepted = WORKER.candidate(None)
    finally:
        path.write_bytes(original)
        WORKER.changed_soak = True
    return differential_result(case, mismatch, accepted)


def differential_result(case, mismatch, accepted):
    if mismatch is None:
        status = "AGREES_PASS" if accepted else "OTHER_REFUSAL"
    else:
        status = "FALSE_PASS" if accepted else "REFUSED"
    return status, case.name, mismatch


@lru_cache(maxsize=1)
def issued_part_c():
    # This is the contemporary Part C *consumer* alongside the ten registered
    # producer sources. It is loaded under its own name, never from the PR.
    name = "scripts/align_r1_part_c.py"
    source = git("show", ISSUED + ":" + name)
    namespace = {"__name__": "issued_part_c", "__file__": name}
    exec(compile(source, ISSUED + ":" + name, "exec"), namespace)
    return NSpace(**namespace)


def issued_verdict(probe, include_x=True):
    issued = issued_part_c()
    physical = {kind: probe.tree/name for name, kind, _, _ in r1.phase_plan() if kind in (S,D,X)}
    receipt = {kind:read(physical[kind]/RECEIPT) for kind in (S,D)}
    bundle = {kind:physical[kind]/receipt[kind]["bundle"] for kind in receipt}
    contrast = None
    if include_x:
        contrast = issued.facts_from_bundle(physical[X]/read(physical[X]/RECEIPT)["bundle"], role="x-g")
    return issued.evaluate(step_d=issued.step_d_facts(bundle[S],receipt[S]),
                           d_bank=issued.facts_from_bundle(bundle[D],role="d-bank"),
                           n_chunk=receipt[S]["slots"]["N_chunk"], x_g=contrast)


def damaged_bytes(path, raw, op):
    import plistlib
    if op == "empty":
        return b""
    if op == "truncated":
        # Remove meaningful content, including when the document ends in LF.
        if path.suffix == ".jsonl":
            line = raw.rstrip().rsplit(b"\n", 1)[-1]
            return raw.rstrip()[:-max(1, len(line)//2)]
        return raw[:max(1, len(raw.rstrip())//2)]
    if op == "invalid":
        return {".csv": b'"unclosed\xff\n', ".plist": b"<plist><dict></array></plist>"}.get(path.suffix,b'{"bad":,}\n')
    if op == "wrong-root":
        return {".csv": b'[]\n', ".plist": plistlib.dumps(["synthetic"])}.get(path.suffix,b'[]\n')
    assert op == "garbage"
    return b"{"


def edit_decision(case, doc):
    if case.op == "empty-final-phase":
        final = next(row for row in doc if row["event_type"] == "run_finalized")
        final["phase"] = ""
        return doc
    if case.op == "orphan-tokenize":
        i = next(i for i, row in enumerate(doc) if row["phase"] == "prefill" and row["event_type"] == "phase_start")
        row = doc[i]
        orphan = dict(row, phase="tokenize", event_type="phase_end")
        row["timestamp_s"] += .000001
        doc.insert(i, orphan)
        return doc
    if case.op == "audit-g0-begin-after-end":
        begin = next(r for r in doc if r["kind"] == "align_thermal_gate" and r["values"]["state"] == "begin")
        end = next(r for r in doc if r["kind"] == "align_thermal_gate" and r["values"]["state"] == "end")
        newest = doc[-1]["finished"]["monotonic_ns"]
        assert begin["started"]["monotonic_ns"] < end["started"]["monotonic_ns"] < newest
        begin["started"]["monotonic_ns"] = begin["finished"]["monotonic_ns"] = newest
        return doc
    parent, key = at(doc, case.path[:-1]), case.path[-1]
    if case.family == "branch":
        if case.op == "absent":
            parent.pop(key, None)
        else:
            parent[key] = case.value
    elif case.op.startswith(("end-missing-", "end-record-missing-")):
        del parent[key]
    else:
        start = at(doc, case.value)
        number = float(start) if isinstance(start, str) else start
        if case.op.startswith("end-before-"):
            number = number - 1 if type(number) is int else math.nextafter(number,-math.inf)
        parent[key] = str(number) if isinstance(start,str) else number
    return doc


def write_decision(path, case):
    if case.predecessor_csv_wire:
        from joulewise.bundle_read import POWER_TRACE_HEADER
        positive = (POWER_TRACE_HEADER + "\n").encode("ascii")
        if case.op == "d018-header":
            wire = positive
        elif case.op == "d018-interval-header-zero-rows":
            from joulewise.bundle_read import POWER_TRACE_INTERVAL_HEADER
            wire = (POWER_TRACE_INTERVAL_HEADER + "\n").encode("ascii")
        elif case.op == "three-column-header":
            wire = b"timestamp_s,power_w,source\n"
        else:
            wire = damaged_bytes(path, positive, case.op)
        path.write_bytes(wire)
    elif case.family == "raw":
        path.write_bytes(damaged_bytes(path, path.read_bytes(), case.op))
    else:
        doc = load_doc(path)
        if case.family == "branch" and case.path:
            parent = at(doc, case.path[:-1])
            key = case.path[-1]
            if case.op == "absent" and key not in parent:
                return
            if case.op != "absent" and key in parent and type(parent[key]) is type(case.value) and parent[key] == case.value:
                return
        save_doc(path, edit_decision(case, doc))


def mutate(case, value):
    if isinstance(case, DecisionCase):
        if case.family == "raw":
            return json.loads(damaged_bytes(Path(case.file), encode(value) + b"\n", case.op))
        return edit_decision(case, value)
    op, path = case.op, case.path
    if op.startswith("warmup-"):
        warm = [r for r in value if r["phase"] == "warmup"]
        if op == "warmup-delete":
            value.remove(warm[0])
        elif op == "warmup-duplicate":
            value.insert(value.index(warm[0]), deepcopy(warm[0]))
        else:
            for r in warm:
                r["timestamp_s"] += 50
            value.sort(key=lambda r:r["timestamp_s"])
    elif op == "short-recovery":
        # Build a self-consistent 21-second journal, including its Coverage report.
        start = value[0]["started"]["monotonic_ns"]
        value = fixture.SoakLauncherBindingTests.journal(rt.sensors_policy(CONFIG), [
            ("reading", start+i*N, (38., 38.) if i <= 20 else (35.375, 35.375)) for i in range(1,22)], start=start)
    elif op == "xml-malformed":
        from joulewise.align.apple.xml_tool_calls import parse_xml_calls
        _, flags = parse_xml_calls("</tool_call>", [])
        value[-1]["flags"].extend(flags)
    elif op == "swap-picks":
        v = value["thermometry"]
        v["s_fast"], v["s_slow"] = v["s_slow"], v["s_fast"]
    elif op == "overlap-previous":
        value["started_epoch_s"] = 5799
    elif op == "poll-ambiguity":
        g = next(r["values"] for r in value if r["kind"] == "align_thermal_gate")
        s = g["entry_stamp"]["monotonic_before_ns"]
        # Six absent readings at entry make the worst admissible view cross
        # the 90% boundary. Recompute journal sequence and coverage.
        value = [r for r in value if not (r["kind"] == "reading" and
                 s-7*N <= r["started"]["monotonic_ns"] < s-N)]
        keys = tg.thermal.keys(value[0]["values"]["thermal"])
        counter = tg.Coverage(value[0]["started"]["monotonic_ns"], keys)
        for i, row in enumerate(value, 1):
            row["seq"] = i
            if row["kind"] == "reading":
                counter.observe(row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"], row["values"])
        value[-1]["values"]["coverage"] = counter.report(value[-1]["started"]["monotonic_ns"])
    elif op == "swap-sensor":
        parent = value
        for key in path[:-1]:
            parent = parent[key]
        k = path[-1]
        fast, slow = (CONFIG["sensors"][name] for name in ("s_fast", "s_slow"))
        parent[k] = slow if parent[k] == fast else fast
    elif op.startswith("every-"):
        mode = op.removeprefix("every-")
        def sweep(v):
            if isinstance(v, list):
                updated = [sweep(item) for item in v]
                return updated[::-1] if mode == "reorder" else updated
            if isinstance(v, dict):
                return {("synthetic_wrong_"+k if mode=="key" else k): sweep(item)
                        for k,item in v.items() if mode!="delete" or isinstance(item,(dict,list))}
            if mode == "type":
                return 17 if isinstance(v,str) else "incorrect-type"
            if mode == "null":
                return None
            if mode == "shift" and type(v) in (int,float):
                return v+1
            return v
        value = sweep(value)
    elif not path:
        value.reverse()
    else:
        parent = value
        for key in path[:-1]:
            parent = parent[key]
        key, v = path[-1], parent[path[-1]]
        if op.startswith("swap-with="):
            other = op.removeprefix("swap-with=")
            parent[key], parent[other] = parent[other], v
        elif op == "key":
            parent["synthetic_wrong_"+key] = parent.pop(key)
        elif op == "delete":
            del parent[key]
        elif op == "null":
            parent[key] = None
        elif op == "type":
            parent[key] = "incorrect-type" if not isinstance(v, str) else 17
        elif op == "shift":
            parent[key] = v + (50*N if any(str(k).endswith("_ns") for k in path) else 1)
        elif op == "reorder":
            v.reverse()
        else:
            raise AssertionError(op)
    return value



@contextmanager
def kit_source(finder):
    gate = "joulewise/align/apple/thermal_gates.py"
    # The kit's historical 82c14c9ea gate blob, independently checked with
    # git rev-parse at authoring. A third historical commit is unnecessary.
    assert finder.blobs[ISSUED][gate] == "b46769d70df02de09dbeb07e4c0020c472477dcb"
    def committed(root, rev, paths):
        assert rev == "82c14c9ea" and paths == [gate]
        return {gate: (finder.root / gate).read_bytes()}
    with patch.object(r1, "executed_commit", return_value=ISSUED), patch.object(
            fixture.kit.reg, "_committed_bytes", committed):
        yield


EPOCH = {"idle": 10, P: 1816, S: 4222, D: 6028, X: 7834}

def journal_open(kind):
    return EPOCH[kind] - (600 if kind == S else 0)

def terminal_window(kind):
    return journal_open(kind) - 1, EPOCH[kind] + 1803


def planned_run_ids():
    """Get the issued names at the backend seam, before any model could run."""
    config = rt.load_config(rt.ROOT / r1.DEFAULT_RUNTIME_CONFIG)[0]
    slots = {"T_dead":1000., "B_D":6144, "N_chunk":4096, "S7":60.}
    names = {}
    class Planned(Exception):
        pass
    def capture(config, hook=None):
        raise Planned(config["run_id"])
    for k in (P,S,D,X):
        plan = object.__new__(rt.Segment)
        plan.kind, plan.config = k, config
        plan.start_inventory = lambda: None
        plan.step_d_result = lambda: {"slots":slots}
        plan.reference = lambda: {}
        plan.bands = lambda: {"delta_fast_c":1., "delta_slow_c":1.}
        plan.run_member = capture
        try:
            plan.dispatch()
        except Planned as seen:
            names[k], = seen.args
    assert set(names) == {P,S,D,X} and len(set(names.values())) == 4
    return names


def scheduled_fixture(names):
    """Place the pinned test fixture's local timelines on one synthetic clock.
    This adapter changes only fixture construction. No issued source is edited.
    """
    import inspect
    import textwrap
    producer = fixture.SoakLauncherBindingTests.make_model_member
    source = textwrap.dedent(inspect.getsource(producer)).replace("35.4","35.375")
    def once(old,new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old,new)
    once("episode_start = 1","member_base_ns = EPOCH[kind]*ns\n    episode_start = member_base_ns+1")
    once("start_ns=ns, first_token_ns=2*ns, end_ns=3*ns",
         "start_ns=member_base_ns+ns, first_token_ns=member_base_ns+2*ns, end_ns=member_base_ns+3*ns")
    once("shift = 120 * ns","shift = member_base_ns + 120*ns")
    once('"source_member": "member", "span_ns": [0, 60 * ns]',
         '"source_member": names["step-d"], "span_ns": [EPOCH["step-d"]*ns,(EPOCH["step-d"]+60)*ns]')
    once('("reading", i * ns, (35.0, 35.0))','("reading", member_base_ns + i*ns, (35.0, 35.0))')
    once("journal = self.journal(sensors, events)","journal = self.journal(sensors, events,start=member_base_ns,finish=max(events[-1][1],turns[-1].end_ns))")
    once("end = 60 * ns","end = member_base_ns + 60*ns")
    once('"span_ns": [0, end], "span_epoch_ns": [0, end]',
         '"span_ns": [member_base_ns,end], "span_epoch_ns": [member_base_ns,end]')
    once('bundle = segment / receipt["bundle"]', """old = segment / receipt["bundle"]
    bundle = old.with_name(names[kind])
    if old != bundle:
        old.rename(bundle)
    receipt["bundle"] = bundle.relative_to(segment).as_posix()""")
    namespace = {**producer.__globals__, "names":names, "EPOCH":EPOCH}
    exec(compile(source, "scheduled-synthetic-fixture", "exec"), namespace)
    return namespace["make_model_member"]


@lru_cache(maxsize=32768)
def issued_smc_key(key, requested):
    """Use the issued ALIGN Reader and its byte decoder with an in-memory IOKit transport."""
    import struct
    from joulewise.align.apple import smc_reader as reader
    type_name,raw = (("flt ",struct.pack("<f",requested)) if key.startswith("T")
                     else ("fpe2",struct.pack(">H",round(requested*4))))
    def call(request):
        assert request.key==reader.fourcc(key)
        if request.data8==reader.CMD_GET_KEY_INFO:
            return NSpace(result=0,keyInfo=NSpace(dataSize=len(raw),dataType=reader.fourcc(type_name)))
        assert request.data8==reader.CMD_READ_KEY
        return NSpace(result=0,bytes=raw)
    device=reader.Reader(transport=NSpace(call=call))
    output=device.read([key]);assert not output["errors"]
    return output["values"][key],output["raw"][key]


def sensor_reply(values):
    issued={k:issued_smc_key(k,float(v)) for k,v in values.items()}
    return {"values":{k:pair[0] for k,pair in issued.items()},"errors":{},
            "raw":{k:dict(pair[1]) for k,pair in issued.items()}}


def set_sensor_value(row,key,requested):
    value,wire=issued_smc_key(key,float(requested))
    row["values"]["sensors"][key]=value
    row["values"]["readings"][key]={**wire,"value":value,"error":None}
    return value


def compact_control():
    # The same admission structure at ordinary margins, with a smaller token
    # stream and wait, dramatically reduces the cost of the generated suite.
    names = planned_run_ids()
    bank = fixture.bank()
    journal = fixture.SoakLauncherBindingTests.journal
    def journal_with_native_identity(sensors, events, **kwargs):
        from joulewise.hazards.base import Stamp
        if "start" not in kwargs and all(event[0] == "reading" for event in events):
            events = [(kind, ns + EPOCH["idle"]*N, value) for kind, ns, value in events]
            kwargs["start"] = EPOCH["idle"]*N
            kwargs["finish"] = EPOCH["idle"]*N + 1801*N + N//2
        hardware = journal(sensors, events, **kwargs)
        def mkstamp(row, key):
            return Stamp.from_json(row[key])
        now = [mkstamp(hardware[0], "started")]
        sensor = NSpace()
        side = tg.thermal.Sidecar(None, sensors, reader=sensor, ctx=NSpace(stamp=lambda: now[0]))
        records = []
        write_one = side._write
        def collect(*args):
            row = write_one(*args)
            records.append(row)
            return row
        side._write = collect
        side.start(background=False)
        gated = any(event[0] != "reading" for event in events)
        # The production backend attaches ThermalSession._status to *every* Sidecar, including
        # observe-only sessions. Its normal fresh-directory fallback returns an empty mapping.
        fresh=rt.ROOT/"v4-empty-observer"
        assert not fresh.exists()
        observer=NSpace(context=NSpace(outputs_dir=fresh),status_reader=None)
        for row in hardware[1:-1]:
            now[0] = mkstamp(row, "started")
            value = row["values"]
            if row["kind"] == "reading":
                assert not value["errors"]
                projected = sensor_reply(value["sensors"])
                sensor.read = lambda keys: projected
                # Idle and recovery create an observe-only session (pm_status defaults to False).
                side.status_reader = (lambda: value["status"]) if gated else (lambda: tg.ThermalSession._status(observer))
                side.tick()
            else:
                side.event(row["kind"], value)
        now[0] = mkstamp(hardware[-1], "started")
        side._write("session_end", dict(coverage=side.counter.report(now[0].monotonic_ns),
                                        collector_error=None))
        return records
    for t in bank["turns"]:
        t["decode_tokens"] = 2
    for g in bank["intervals"]:
        g["duration_s"] = 12.
        g["end_ns"] = 12*N
    contrast = deepcopy(fixture.XG)
    for t in contrast["turns"]:
        t["decode_tokens"] = 2
    with ExitStack() as stack:
        scheduled = scheduled_fixture(names)
        scheduled.__globals__["write_terminal"] = lambda *args: fixture.write_terminal(*args)
        scheduled.__globals__["bank"] = lambda: fixture.bank()
        scheduled.__globals__["XG"] = contrast
        stack.enter_context(patch.object(fixture.SoakLauncherBindingTests, "make_model_member",scheduled))
        stack.enter_context(patch.object(fixture.SoakLauncherBindingTests, "journal",
                                          staticmethod(journal_with_native_identity)))
        stack.enter_context(patch.object(fixture, "bank", return_value=bank))
        stack.enter_context(patch.object(fixture, "XG", contrast))
        stack.enter_context(patch.dict(fixture.STEP, g0_wait_s=12.,release={"fast_c":35.375,"slow_c":35.375}))
        stack.enter_context(patch.dict(scheduled.__globals__["member_record"].__globals__["STEP"],
                                      release={"fast_c":35.375,"slow_c":35.375}))
        return stack.pop_all()


@lru_cache(maxsize=1)
def rehearsal_blocks():
    """The complete issued per-phase loop and per-member close logic, in situ.

    Full-night registration also takes inputs from A/B/A and arms absent from
    Part C. The guard, acquisition, harvest and full-night registration do not
    belong to this five-member synthetic replay.
    """
    source = ast.parse(Path(r1.__file__).read_bytes())
    driver = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    guard = next(n for n in ast.walk(driver) if isinstance(n, ast.With) and
                 any(ast.unparse(i.context_expr) == "guard" for i in n.items))
    loop = next(i for i,n in enumerate(guard.body) if isinstance(n,ast.For) and
                isinstance(n.iter,ast.Call) and ast.unparse(n.iter.func) == "phase_plan")
    guarded = guard.body[:loop+1]
    outer = next(n.body for n in ast.walk(driver) if isinstance(n,ast.Try) and guard in n.body)
    thermo = next(i for i,n in enumerate(outer) if isinstance(n,ast.Assign) and
                  ast.unparse(n.targets[0]) == "thermometry['bar']")
    mode = next(i for i,n in enumerate(outer[thermo:], thermo) if isinstance(n,ast.Assign)
                and ast.unparse(n.targets[0]) == "ac_powermode")
    feeds = next(n for n in outer[mode:] if isinstance(n,ast.For) and
                 ast.unparse(n.iter) == "results.items()")
    return guarded, outer[thermo:mode]+[feeds]


@lru_cache(maxsize=1)
def rehearsal_program():
    return tuple(compile(ast.Module(body=block,type_ignores=[]),r1.__file__,"exec")
                 for block in rehearsal_blocks())


@lru_cache(maxsize=12)
def replay_driver(inputs):
    """Drive the issued rehearsal's decisions over the actual Part C receipts.

    The synthetic subprocess returns the stored stdout bytes. The driver calls
    its own _admission_unit, _invoke, grouping, schedule, quiet-load, redo,
    predecessor and inconclusive logic. The time source never sleeps.
    """
    receipts = {role: readout for role, readout, _, _ in inputs}
    clocks = {role: (start,end) for role, _, start, end in inputs}
    full_plan = r1.phase_plan()
    phases = [row for row in full_plan if row[1] in receipts]
    need([row[1] for row in phases] == ["idle",P,S,D,X], "issued Part C phase order")
    counts = {}
    def subprocess_return(argv):
        kind = argv[argv.index("--r1-kind")+1]
        counts[kind] = counts.get(kind,0)+1
        return NSpace(returncode=0,stdout=receipts[kind].decode(),stderr="")
    # _admission_unit reads start before invoking the transport, end after it.
    # Each admitted unit is independent of the next unit's mocked time source.
    issued_unit = r1._admission_unit
    def unit(args, output, rows, record, **kwargs):
        stamps = [t for _,kind,_,_ in rows for t in clocks[kind]]
        ticks = iter(stamps*3)
        with patch.object(r1,"time",NSpace(time_ns=lambda:next(ticks))):
            return issued_unit(args,output,rows,record,**kwargs)
    config = ["--config",str(rt.ROOT / r1.DEFAULT_RUNTIME_CONFIG)]
    with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()), ExitStack() as stack:
        stack.enter_context(patch.object(r1,"phase_plan",lambda *args, **kwargs: phases))
        stack.enter_context(patch.object(r1,"_run",subprocess_return))
        stack.enter_context(patch.object(r1,"wait_outside_os_batch",return_value=0))
        state = {**vars(r1),"args":NSpace(runtime=config,include_4bit=False),
                 "output":Path(tmp),"schedule":r1.check_w1_schedule(config),
                 "precool_cap":r1.runtime_precool_cap_s(config),"record":{"phases":[]},
                 "results":{},"_admission_unit":unit}
        phase_code, close_code = rehearsal_program()
        exec(phase_code,state)
        results = state["results"]
        need(set(results) == {r[0] for r in phases} and not state["skipped"],"issued driver skipped an admission")
        need(all(counts.get(role) == 1 for role in receipts),"issued driver demanded a load redo")
        state["thermometry_d"] = r1.thermometry_record(r1.STEP_D_NAME,results[r1.STEP_D_NAME])
        state["thermometry"] = {"D":state["thermometry_d"]}
        exec(close_code,state)
        need(not state["inconclusive"],"issued rehearsal inconclusive: " + ",".join(sorted(state["inconclusive"])))
        need(state["thermometry"]["bar"] == "pass","issued rehearsal thermometry bar")


def frozen_checks(segment, kind, claim, ref):
    for source in segment.rglob("align_thermal.jsonl"):
        check_sidecar(source.read_bytes(), source.parent.name == "outputs")
    expected = derive(segment, kind, claim, ref)
    agree(claim, expected, "runtime result")
    process = NSpace(returncode=0, stdout=json.dumps(claim), stderr="")
    with patch.object(r1, "_run", return_value=process):
        r1._invoke(["synthetic"], kind, segment, soak_reference=None if kind=="idle" else segment,
                   quiet=True, contract_key="idle_soak" if kind=="idle" else None)
    if kind == "idle":
        detrended = r1.soak_detrended(expected["sensor_series_c"], expected["sensor_series_t_s"],
                                      expected["sensor_series_end_t_s"])
        need(all(v["settled"] for v in detrended.values()), "frozen soak unsettled")
        agree(ref["detrended"], detrended, "soak detrended")
        need(not r1.os_load_verdict("idle_soak", expected, wall_s=1800)["redo"], "frozen soak redo")
        return
    r1._check_member_powermode(kind, expected, 0)
    check_workload(segment, kind)
    if kind == S:
        r1._check_step_d(expected)
        need(r1.thermometry_record(kind, expected)["status"] == "pass", "thermometry decision")
    if kind in (D, X):
        step = read(segment.parent / pc.KINDS[S] / RECEIPT)
        schedule = r1.check_w1_schedule(["--config", str(rt.ROOT / r1.DEFAULT_RUNTIME_CONFIG)])
        r1._check_d_reference_consumed(kind, expected, step)
        r1._check_schedule(kind, expected, schedule, "D" if kind == D else "X-G")
        if kind == D:
            r1._check_gated_t_dead(kind, expected, step)
            need(r1.deadman_summary(kind, expected)["duty_bar"]["verdict"] == "pass", "duty bar")


def binding_and_order(base, role, segment):
    last = None
    for k in ("idle", P, S, D, X):
        root = segment if k == role else base / k
        m = read(root / rt.CUSTODY_NAME)
        need(m["kind"] == k and m["schema"] == rt.CUSTODY_SCHEMA and m["status"] == "complete"
             and m["config_sha256"] == CONFIG_SHA, "terminal identity")
        s, e = m["started_epoch_s"], m["ended_epoch_s"]
        need(type(s) in (float,int) and type(e) in (float,int) and s <= e and
             (last is None or last <= s), "sequential terminal order")
        last = e
        if k == role:
            if k != "idle":
                bundle, = (root / "runs").iterdir()
                ep = read(bundle / "outputs/align_episode.json")
                first,last_stamp = ep["hardware"]["paired_clock_stamps_ns"]
                need(s*N <= first["epoch_ns"] <= last_stamp["epoch_ns"] <= e*N, "enclosing member bracket")
                if k == S:
                    need(read(root / RECEIPT)["slot_detail"]["member_wall_s"] <= e-s,
                         "RL-186 member wall upper bound")
            expected = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob("*") if p.is_file() and p.name != rt.CUSTODY_NAME}
            need(expected == m["files"], "terminal source binding")


def copy_segment(base, role, destination):
    shutil.copytree(base / role, destination, copy_function=os.link, dirs_exist_ok=True)


def unshared(path):
    # Copy-on-write for a single synthetic hardlink, including its parent manifest.
    raw = path.read_bytes()
    path.unlink()
    path.write_bytes(raw)


def apply_case(base, segment, case):
    path = segment / case.file
    if isinstance(case, DecisionCase):
        unshared(path)
        write_decision(path, case)
    else:
        val = mutate(case, load_doc(path))
        unshared(path)
        save_doc(path, val)
    if case.file != rt.CUSTODY_NAME:
        manifest = segment / rt.CUSTODY_NAME
        m = read(manifest)
        m["files"][case.file] = hashlib.sha256(path.read_bytes()).hexdigest()
        unshared(manifest)
        write(manifest, m)
        if case.op == "short-recovery":
            # Keep the independently recomputable response summaries true.
            # The sole outstanding contradiction is the 600-second claim.
            result_path = segment / RECEIPT
            result = read(result_path)
            bundle = segment / result["bundle"]
            ep = wl.read_episode_bundle(bundle)
            samples = rt.journal_rows(bundle / "outputs/align_thermal.jsonl") + rt.journal_rows(path)
            for role in ("s_fast", "s_slow"):
                result["slot_detail"]["responses"][role] = rt.step_response(
                    samples, rt.sensors_policy(CONFIG)[role], ep.start_ns, ep.end_ns)
            unshared(result_path)
            write(result_path, result)
            m["files"][RECEIPT] = hashlib.sha256(result_path.read_bytes()).hexdigest()
            write(manifest, m)


def descriptor_claim(segment, case, kind):
    # One mirror serves the entire attempt. Keep all peers consistent with its
    # bytes at their own return. Only the selected D4 member retains 40,960.
    if kind == "idle":
        return
    limit = read(MODEL_DIR / "config.json")["max_position_embeddings"]
    receipt = read(segment / RECEIPT)
    bundle = segment / receipt["bundle"]
    assert read(bundle / "config.json")["model"]["source"] == str(MODEL_DIR)
    episode = bundle / "outputs/align_episode.json"
    record = read(episode)
    limits = record["hardware"]["context_limits"]
    assert limits == {"max_context_tokens": 40960, "max_position_embeddings": 40960}
    if limit == 40960 or (kind == case.role and case.op == "mirror-40961-claim-40960"):
        return
    assert limit == 40961
    limits["max_position_embeddings"] = limit
    unshared(episode)
    write(episode, record)
    manifest_path = segment / rt.CUSTODY_NAME
    manifest = read(manifest_path)
    manifest["files"][episode.relative_to(segment).as_posix()] = hashlib.sha256(episode.read_bytes()).hexdigest()
    unshared(manifest_path)
    write(manifest_path, manifest)


@contextmanager
def descriptor_attempt(case):
    descriptor = MODEL_DIR / "config.json"
    baseline = descriptor.read_bytes()
    assert json.loads(baseline) == {"max_position_embeddings": 40960}
    append = evidence.EvidenceLedger._append
    member = None
    rewritten = False

    def write_row(ledger, row):
        nonlocal member, rewritten
        if ledger.mode == "native" and "manifest" in row:
            member = row["kind"]
        target = ledger.mode == "native" and member == case.role
        # Remove before hashing, so the retained row and on-disk chain agree.
        if target and case.op == "no-binding" and DESCRIPTOR_FIELD in row:
            row = dict(row)
            del row[DESCRIPTOR_FIELD]
        stored = append(ledger, row)
        if target and case.op == "rewritten-after-return" and not rewritten:
            # For a pre-RL-189 writer the return is the only row. A writer
            # using the permitted supplemental binding must finish it first.
            if DESCRIPTOR_FIELD in row or ("manifest" in row and member not in SUPPLEMENTAL_BINDINGS):
                assert descriptor.read_bytes() == baseline
                write(descriptor, {"max_position_embeddings": 40961})
                rewritten = True
        return stored

    try:
        if case.op in ("consistent-40961", "mirror-40961-claim-40960"):
            write(descriptor, {"max_position_embeddings": 40961})
        with patch.object(evidence.EvidenceLedger, "_append", write_row):
            yield
        if case.op == "rewritten-after-return":
            assert rewritten, "target row was never written"
    finally:
        descriptor.write_bytes(baseline)


class Probe:
    def __init__(self, base):
        self.base = base
        self.ref = read(base / "reference.json")
        self.expect = {}
        self.tmp = tempfile.TemporaryDirectory(dir=base.parent)
        self.tree = Path(self.tmp.name)
        for k in ("idle", P, S, D, X):
            segment = self.tree / ("idle_soak" if k=="idle" else pc.KINDS[k])
            copy_segment(base, k, segment)
            receipt = read(segment / RECEIPT)
            self.expect[k] = derive(segment, k, receipt, self.ref)
            frozen_checks(segment, k, receipt, self.ref)
            binding_and_order(base, k, segment)
        self.driver_inputs = tuple(self.driver_input(k, base / k) for k in ("idle",P,S,D,X))
        replay_driver(self.driver_inputs)

    @staticmethod
    def driver_input(k, segment):
        terminal = read(segment / rt.CUSTODY_NAME)
        return (k, (segment / RECEIPT).read_bytes(), round(terminal["started_epoch_s"]*N),
                round(terminal["ended_epoch_s"]*N))

    def driver_check(self, m, root):
        if m.file in (RECEIPT, rt.CUSTODY_NAME) or m.op == "short-recovery":
            inputs = tuple(self.driver_input(row[0],root) if row[0] == m.role else row
                           for row in self.driver_inputs)
        else:
            inputs = self.driver_inputs
        replay_driver(inputs)

    def oracle(self, m):
        root = self.tree / ("idle_soak" if m.role=="idle" else pc.KINDS[m.role])
        if m.file in OUTER:
            row = read(self.base / "soak/soak_row.json")
            reference = read(self.base / "soak/soak_reference.json")
            try:
                if m.file == "soak_row.json":
                    row = mutate(m, row)
                else:
                    reference = mutate(m, reference)
                if isinstance(m, DecisionCase):
                    need(isinstance(reference, dict) and isinstance(row,dict), "outer object")
                start, end = row["started_ns"], row["ended_ns"]
                need(type(start) is int and type(end) is int and 0 <= start <= end, "soak row clock")
                need(row["attempt"] == 0 and row["name"] == "idle_soak" and row["class"] == "light" and
                     row["output_dir"] == self.ref["source_output"], "soak row identity")
                receipt = read(self.base / "idle" / RECEIPT)
                agree(row["result"], receipt, "outer receipt")
                expected = self.expect["idle"]
                derived = r1.soak_detrended(expected["sensor_series_c"], expected["sensor_series_t_s"],
                                             expected["sensor_series_end_t_s"])
                agree(row["soak_detrended"], derived, "soak row detrended")
                load = r1.os_load_verdict("idle_soak", expected, wall_s=(end-start)/N)
                agree(row["os_load"], load, "soak os load")
                need(not load["redo"], "soak redo")
                with tempfile.TemporaryDirectory() as tmp:
                    agree(reference, read(r1.write_soak_reference(Path(tmp),row)), "frozen soak reference")
                return None
            except (Disagreement, KeyError, IndexError, TypeError, ValueError, ArithmeticError) as error:
                return str(error)
        try:
            apply_case(self.base, root, m)
            claim = read(root / RECEIPT)
            binding_and_order(self.base, m.role, root)
            if isinstance(m, DecisionCase):
                # Drive the recorded word through the historical loop even when
                # a producer comparison would independently refuse it.
                self.driver_check(m, root)
                if m.predecessor_csv_wire:
                    from joulewise.bundle_read import _check_power_trace
                    bundle = (root / m.file).parent
                    problems = _check_power_trace(bundle, read(bundle / "summary_metrics.json"),
                                                  read(bundle / "metadata.json"))
                    need(not problems, "D-018: " + ", ".join(problems))
            if m.file == RECEIPT and m.path[:2] != ("slot_detail", "member_wall_s"):
                # The entire raw input is byte-identical to that of the frozen
                # execution in __init__. Every derived output is compared here.
                agree(claim, self.expect[m.role], "runtime result")
            else:
                frozen_checks(root, m.role, claim, self.ref)
            self.driver_check(m,root)
            if isinstance(m, DecisionCase) and m.role in (S, D, X):
                if m.role == S:
                    for consumer in (D, X):
                        dependent = self.tree / pc.KINDS[consumer]
                        frozen_checks(dependent, consumer, read(dependent / RECEIPT), self.ref)
                need(issued_verdict(self)["pass"], "issued Part C verdict")
            return None
        except Disagreement as error:
            return str(error)
        except (KeyError, IndexError, ValueError, TypeError, ArithmeticError, AttributeError, OSError,
                BundleReadError, rt.Refused, rt.RuntimeFailure, r1.Refusal, wl.AdapterFailure, tg.WindowReferenceRefused) as error:
            # Typed record-read failures on a damaged attempt, after the very
            # same path has succeeded on the clean control. Never catch asserts.
            frame = error.__traceback__
            while frame.tb_next:
                frame = frame.tb_next
            origin = frame.tb_frame
            return f"{type(error).__name__} in {origin.f_globals.get('__name__')}.{origin.f_code.co_qualname}"
        finally:
            for name in {m.file, rt.CUSTODY_NAME, RECEIPT}:
                path = root / name
                path.unlink()
                os.link(self.base / m.role / name, path)

    def candidate(self, m):
        """Call the public native evaluator with real ledgers and pre-close bytes.
        The full launcher independently exercises this path in control().
        """
        root = self.tree / "native" / "synthetic-run"
        output, soak = root / "part-c", root / "soak"
        config = rt.ROOT / r1.DEFAULT_RUNTIME_CONFIG
        runtime = ["synthetic-runtime", "--config", str(config)]
        ref = soak / "soak_reference.json"
        touched = []

        def produce(kind, segment):
            if isinstance(m, LaunchCase) and m.role == kind and m.op.endswith("-unworked"):
                touched.append(kind)
                assert not segment.exists() or not list(segment.iterdir())
                return launch_observation(m, NSpace(returncode=0, stdout="", stderr=""))
            copy_segment(self.base, kind, segment)
            if isinstance(m, DescriptorCase):
                descriptor_claim(segment, m, kind)
                if kind == m.role:
                    touched.append(kind)
            elif isinstance(m, LaunchCase):
                if m.role == kind:
                    touched.append(kind)
            elif m and m.role == kind and m.file not in OUTER:
                apply_case(self.base, segment, m)
                touched.append(kind)
            # A raw saved-receipt probe damages only that file. The separately
            # observed stdout still carries the clean producer response.
            raw_receipt = (isinstance(m, DecisionCase) and m.family == "raw"
                           and m.role == kind and m.file == RECEIPT)
            receipt = read(getattr(self,"stdout_files",{}).get(kind,(self.base / kind if raw_receipt else segment) / RECEIPT))
            process = NSpace(returncode=0, stdout=json.dumps(receipt, sort_keys=True)+"\n", stderr="")
            if isinstance(m, LaunchCase) and m.role == kind:
                return launch_observation(m, process)
            return process

        if not soak.exists() or (m and m.role == "idle") or getattr(self, "changed_soak", False):
            if soak.exists():
                shutil.rmtree(soak)
            self.changed_soak = bool(m and m.role == "idle")
            segment = soak / "idle_soak"
            process = produce("idle", segment)
            ledger = evidence.EvidenceLedger(soak, ISSUED, config, mode="soak")
            argv = runtime + ["--r1-kind", "idle", "--output", str(segment), "--duration-s", "1800"]
            if isinstance(m, LaunchCase) and m.file == "argv":
                argv = soak_argv(argv, m)
            ledger.member_return("idle", segment, argv, process=process)
            row = read(self.base / "soak/soak_row.json")
            result = read(segment / RECEIPT) if isinstance(m, LaunchCase) else json.loads(process.stdout)
            row.update(output_dir=str(segment), result=result)
            reference = {**deepcopy(self.ref), "source_output": str(segment)}
            for name, value in (("soak_row.json", row), ("soak_reference.json", reference)):
                if m and m.role == "idle" and m.file == name:
                    touched.append("idle")
                    if isinstance(m, DecisionCase) and m.family == "raw":
                        (soak / name).write_bytes(damaged_bytes(Path(name), encode(value) + b"\n", m.op))
                        continue
                    value = mutate(m, value)
                write(soak / name, value)
            ledger.finish_soak("accepted")
        ledger_sha = hashlib.sha256((soak / "evidence_ledger.jsonl").read_bytes()).hexdigest()
        def transport(argv):
            assert argv[0] == runtime[0]
            kind = argv[argv.index("--r1-kind")+1]
            segment = Path(argv[argv.index("--output")+1])
            assert segment == output / pc.KINDS[kind]
            return produce(kind, segment)
        if output.exists():
            shutil.rmtree(output)
        log = io.StringIO()
        with redirect_stdout(log), patch.object(r1, "_run", transport):
            try:
                pc.run_bound_part_c(output, runtime, soak_reference=ref, soak_ledger_sha256=ledger_sha)
                returned = True
            except ValueError:
                returned = False
        if touched != ([m.role] if m else []):
            raise AssertionError(f"candidate did not see mutation {m}")
        first, second = [read(output / name) for name in ("smoke.json", "smoke_part_c.json")]
        assert first == second, "disagreeing native publications"
        result = first["evaluation"]
        word = result["verdict"]
        assert returned is result["pass"] is (word == "pass"), "contradictory native return"
        assert f"Part C verdict: {word} (pass: {returned})" in log.getvalue().splitlines()
        if returned:
            (root / "part-c.stdout.log").write_text(log.getvalue())
            evidence.verify_part_c_publication(root, ledger_sha, hashlib.sha256(ref.read_bytes()).hexdigest())
        if isinstance(m, DescriptorCase):
            self.descriptor_verdict = word
            self.descriptor_findings = [json.loads(line) for line in log.getvalue().splitlines()
                                        if line.startswith("{") and "reason" in json.loads(line)]
        return returned


def profile_graph(finder, action):
    """Walk runtime-resolved edges and their static may-call closure in the ten.
    Dynamic dispatch is resolved by the actual five segment invocations. After
    that dispatch, include alternate record-dependent branches and callees even
    if the control takes only the passing branch. A conditional call through an
    unknown receiver retains all frozen implementations of that method.
    """
    files = {str(finder.root / p): p for p in finder.frozen if p.endswith(".py")}
    definitions, by_name, positions = {}, defaultdict(set), {}
    for path in files.values():
        def visit(node, owner=""):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    name = ".".join(filter(None, (owner, child.name)))
                    if not isinstance(child, ast.ClassDef):
                        key = path, name
                        start = min([child.lineno, *(d.lineno for d in child.decorator_list)])
                        definitions[key] = child
                        positions[path, start] = key
                        by_name[child.name].add(key)
                    visit(child, name)
                else:
                    visit(child, owner)
        visit(ast.parse((finder.root / path).read_bytes()))
    edges = defaultdict(set)
    observed = set()
    def key(frame):
        return positions.get((files.get(frame.f_code.co_filename), frame.f_code.co_firstlineno))
    def trace(frame, event, arg):
        if event == "call" and frame.f_code.co_filename in files:
            callee = key(frame)
            if callee:
                observed.add(callee)
                if frame.f_back:
                    edges[key(frame.f_back)].add(callee)
    previous = sys.getprofile()
    sys.setprofile(trace)
    try:
        result = action()
    finally:
        sys.setprofile(previous)
    reached = set(observed)
    # The driver is executed at its real source lines with the physical phase
    # plan. Follow the call graph of that entire body, including its untaken
    # branches, without introducing the unrelated full-night registration.
    driver_key = next(k for k in definitions if k[0] == "scripts/align_r1_rehearsal.py" and k[1] == "run")
    sections = rehearsal_blocks()
    definitions[driver_key] = ast.Module(body=sections[0]+sections[1],type_ignores=[])
    reached.add(driver_key)
    # _wait's polling loop is replaced at the I/O seam by RL-186's quantified
    # rule. Its entire native decision graph still belongs in the inventory.
    reached.update(by_name["_wait"])
    todo = list(reached)
    inventory = set()
    while todo:
        caller = todo.pop()
        file, name = caller
        func = definitions[caller]
        children = set(edges[caller])
        def sites(node, line):
            line = getattr(node,"lineno",line)
            yield node,line
            for child in ast.iter_child_nodes(node):
                yield from sites(child,line)
        for node,line in sites(func,1):
            if isinstance(node, (ast.If, ast.IfExp, ast.While, ast.For, ast.ExceptHandler, ast.BoolOp,
                                 ast.Compare, ast.Assert, ast.Match, ast.comprehension, ast.Raise, ast.Return)):
                inventory.add((file, name, line, type(node).__name__))
            if not isinstance(node, ast.Call):
                continue
            target = node.func
            attr = getattr(target, "id", None) or getattr(target, "attr", None)
            for candidate in by_name.get(attr, ()):
                # dispatch() also contains other R1 phases. Only targets
                # dispatched for the physical Part C kinds are in this graph.
                if name == "Segment.dispatch" and candidate not in observed:
                    continue
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                    if target.value.id == "self" and (file != candidate[0] or
                            name.split(".")[0] != candidate[1].split(".")[0]):
                        continue
                children.add(candidate)
        for child in children-reached:
            reached.add(child)
            todo.append(child)
    assert all(any(name == "Segment."+method for _, name in observed)
               for method in ("run", "dispatch", "k_idle", "k_step_d", "k_gated_d", "k_x_g",
                              "k_capture_predecessor_30b"))
    return result, sorted(inventory)


def worker_init():
    # Each worker takes a private writable attempt. Only pristine inputs and
    # the frozen output cache are shared across workers.
    global WORKER
    WORKER = object.__new__(Probe)
    WORKER.base, WORKER.ref, WORKER.expect = ORIGINAL.base, ORIGINAL.ref, ORIGINAL.expect
    WORKER.driver_inputs = ORIGINAL.driver_inputs
    WORKER.tree = ORIGINAL.base.parent / ("worker-" + str(os.getpid()))
    WORKER.tree.mkdir()
    for k in ("idle", P, S, D, X):
        copy_segment(WORKER.base, k, WORKER.tree / ("idle_soak" if k=="idle" else pc.KINDS[k]))


def descriptor_trial(m):
    expected = {"rewritten-after-return": "source_integrity", "consistent-40961": "pass",
                "mirror-40961-claim-40960": "admission_recompute", "no-binding": "evidence_unverifiable"}[m.op]
    with descriptor_attempt(m):
        accepted = WORKER.candidate(m)
    findings = WORKER.descriptor_findings
    actual = WORKER.descriptor_verdict
    detail = f"expected={expected} actual={actual} findings={findings}"
    if expected == "pass":
        return ("AGREES_PASS" if accepted else "WRONG_VERDICT"), m.name, detail
    if accepted:
        return "FALSE_PASS", m.name, detail
    # With one mirror, any member already bound at the instant of the rewrite
    # can be the first to report the changed bytes. D1 and D4 are target-local.
    roles = (P, S, D, X)
    affected = roles[:roles.index(m.role)+1] if m.op == "rewritten-after-return" else (m.role,)
    correct = actual == "other_failure" and any(
        f.get("role") in affected and f.get("reason") == expected and
        (m.op != "mirror-40961-claim-40960" or f.get("field") in
         ("max_position_embeddings", LIMIT_FIELD, "hardware." + LIMIT_FIELD)) for f in findings)
    return ("REFUSED" if correct else "WRONG_VERDICT"), m.name, detail


def trial(m):
    try:
        if isinstance(m, DescriptorCase):
            return descriptor_trial(m)
        if isinstance(m, InputCase):
            return issued_trial(m)
        if isinstance(m, LaunchCase):
            return differential_result(m, launch_oracle(m, WORKER), WORKER.candidate(m))
        mismatch = WORKER.oracle(m)
        if not m.path and m.op in ("warmup-shift", "warmup-delete", "warmup-duplicate", "xml-malformed",
                                  "short-recovery", "swap-picks", "poll-ambiguity", "overlap-previous"):
            assert mismatch is not None, "known frozen counterexample went unwitnessed"
        accepted = WORKER.candidate(m)
        if isinstance(m, DecisionCase) and m.predecessor_csv_wire and m.op in (
                "d018-header", "d018-interval-header-zero-rows"):
            assert mismatch is None, "issued D-018 positive control failed"
            if not accepted:
                return "WRONG_VERDICT", m.name, "candidate refused the D-018 positive control"
        status = ("FALSE_PASS" if accepted else "REFUSED") if mismatch is not None else (
            "AGREES_PASS" if accepted else "OTHER_REFUSAL")
        return status, m.name, mismatch
    except Exception as error:
        import traceback
        return "HARNESS_ERROR", m.name, "".join(traceback.format_exception(error))


# V4. Everything below is test input, test expectations or a black-box public call.
# No candidate function participates in forming an expectation.
import csv

ROLE = {"I": "idle", "P": P, "S": S, "D": D, "X": X}
RULE_FILE = HERE.with_name("writer_rules.tsv")
R3_NAMES = {
    ("outer-close","I","one-second"): "r3-01-outer-one-second",
    ("outer-next","I","gt"): "r3-01-soak-overlaps-next-member",
    ("status-after","X","lt"): "r3-02-status-before-read",
    ("pm-before","X","gt"): "r3-02-pm-after-status",
    ("pid-present","P","missing-both"): "r3-03-runtime-absent-both-snapshots",
    ("pid-present","P","missing-close"): "r3-03-runtime-lost-at-close",
    ("battery-work-open","X","gt"): "r3-04-late-opening-battery",
    ("battery-work-close","X","lt"): "r3-04-early-closing-battery",
    ("battery-count","P","minus"): "r3-05-61-not-62",
    ("battery-count","P","plus"): "r3-05-63-not-62",
    ("replay","X","drop-census"): "r3-06-offline-missing-X-closing-census",
    ("battery-count","X","removed-close"): "r3-06-offline-X-battery",
    ("battery-count","P","removed-close"): "r3-06-offline-P-battery",
    ("prior-origin","P","lt"): "r3-06-offline-prior-origin",
    ("census-pair","I","double-start"): "r3-07-duplicate-before-shim",
}
@dataclass(frozen=True)
class WriterCase:
    rule: str
    member: str
    op: str
    expected: str
    family: str

    @property
    def role(self):
        return ROLE[self.member]

    @property
    def name(self):
        alias = R3_NAMES.get((self.rule, self.member, self.op))
        return "/".join(filter(None, ("v4",self.family,self.member,self.rule,self.op,alias)))

def writer_cases():
    with RULE_FILE.open() as file:
        for r in csv.DictReader(file, delimiter="\t"):
            for member in r["roles"]:
                load = {"I":"soak_load","P":"quiet_load","S":"quiet_load"}.get(member,"load_evidence")
                for cell in r["cases"].split():
                    if r["id"]=="turn-wire" and member in "PS" and cell.split("=")[0]=="reorder": continue
                    op, eq, value = cell.partition("=")
                    code = value if eq else r["reason"].replace("LOAD",load)
                    yield WriterCase(r["id"], member, op, code, r["family"])

def shift_cmp(op):
    return {"lt":-1,"eq":0,"gt":1}[op]

def put_result(root, receipt):
    write(root / RECEIPT, receipt)

def work_wall(root, kind, receipt):
    docs = [root / "sensors/align_thermal.jsonl"] if kind == "idle" else []
    stamps = []
    if kind != "idle":
        bundle = root / receipt["bundle"]
        stamps.extend(round(e["timestamp_s"]*N) for e in rows(bundle/"events.jsonl"))
        ep = read(bundle/"outputs/align_episode.json")
        stamps.extend(p["epoch_ns"] for p in ep["hardware"]["paired_clock_stamps_ns"])
        for turn in rows(bundle/"outputs/align_turns.jsonl"):
            stamps.extend(round(turn[k]["epoch_s"]*N) for k in ("start_stamp","end_stamp"))
        if kind != P:
            docs.append(bundle/"outputs/align_thermal.jsonl")
        if kind == S:
            docs.append(root/"recovery/align_thermal.jsonl")
    if kind == S:
        ep=read(bundle/"outputs/align_episode.json")
        pairs=ep["hardware"]["paired_clock_stamps_ns"]
        # This synthetic writer deliberately supplies two exact mapping witnesses.
        offsets={p["epoch_ns"]-p["monotonic_before_ns"] for p in pairs}
        assert len(offsets)==1 and all(p["monotonic_before_ns"]==p["monotonic_after_ns"] for p in pairs)
        offset,=offsets
        stamps.extend(r[key]["monotonic_ns"]+offset for r in rows(root/"inventory/inventory_journal.jsonl")
                      for key in ("started","finished"))
    for path in docs:
        stamps.extend(r[k]["wall_ns"] for r in rows(path) for k in ("started","finished"))
    return min(stamps), max(stamps)

def load_edit(case, root, receipt):
    rule, op, kind = case.rule, case.op, case.role
    data = read(root/"load_journal.json")
    census, times, cores = data["census"], data["cpu_busy_t_s"], data["cpu_busy_cores"]
    own, = data["exclude_roots"]
    a, b = [p["t_s"] for p in census]
    if rule in ("census-pair","replay"):
        if op == "double-start":
            census[1] = deepcopy(census[0])
        elif op in ("missing-close","drop-census"):
            census.pop()
        elif op == "missing-open":
            census.pop(0)
        elif op.startswith("dup-"):
            i = 0 if op.endswith("open") else 1
            census.insert(i,deepcopy(census[i]))
        elif op == "swap":
            census.reverse()
    elif rule == "census-process":
        census[int(op.endswith("close"))]["processes"] = []
    elif rule == "pid-count":
        data["exclude_roots"] = {"one":[own],"zero":[],"two":[own,own],"bool":[True]}[op]
    elif rule == "pid-unique":
        second = deepcopy(census[0]["processes"][0])
        if op == "distinct":
            second["pid"] += 10000
        if op == "conflicting":
            second["comm"] += "-other"
        census[0]["processes"].append(second)
    elif rule == "pid-present":
        for i, point in enumerate(census):
            if op in ("missing-both", ("missing-open","missing-close")[i]):
                next(p for p in point["processes"] if p["pid"] == own)["pid"] += 10000
    elif rule == "census-clock":
        census[1]["t_s"] = a - int(op=="reverse")
    elif rule == "census-copy":
        key = {"census":"census","times":"cpu_busy_t_s","cores":"cpu_busy_cores","errors":"load_journal_errors"}[op]
        receipt[key] = ["changed"] if op=="errors" else receipt[key][:-1]
        return
    elif rule == "cpu-count":
        times.pop() if op=="minus" else times.append(times[-1]+0.5)
    elif rule == "cpu-values":
        cores[2] = {"zero":0.0,"positive":1.0,"negative":-1,"boolean":True}[op]
    elif rule == "cpu-order":
        if op == "negative":
            times[0] = -1
        else:
            times[1] = times[0] - int(op=="reverse")/N
    elif rule == "cpu-gap":
        # Spread five subsequent intervals so all other gaps remain positive.
        for j in range(5):
            times[501+j] = times[500]+5+shift_cmp(op)/N + j/6
    elif rule == "cpu-min":
        data["cpu_busy_t_s"], data["cpu_busy_cores"] = times[:5], cores[:5]
    elif rule == "cpu-hot":
        n = 60 if op == "equality" else int(op)
        cores[100:100+n] = [0.5 if op=="equality" else 0.50001]*n
    elif rule.startswith("prior-"):
        prev = ("idle",P,S,D,X)[("idle",P,S,D,X).index(kind)-1]
        close = read(root.parent / prev / "load_journal.json")["census"][-1]["t_s"]
        if rule == "prior-origin":
            # Bind the upper endpoint of the common origin range to the requested instant.
            origin = close + shift_cmp(op)/N
            data["cpu_busy_t_s"] = [b-origin-(times[-1]-t) for t in times]
        else:
            census[0]["t_s"] = close + shift_cmp(op)/N
    else:
        raise ValueError(rule)
    for key in ("census","cpu_busy_t_s","cpu_busy_cores"):
        receipt[key] = deepcopy(data[key])
    write(root/"load_journal.json",data)

def assert_callback_order(root,kind,receipt):
    """Independent ns interval intersection on this fixture's exact paired clocks."""
    assert kind in (P,S,D,X)
    episode=read(root/receipt["bundle"]/"outputs/align_episode.json")
    pairs=episode["hardware"]["paired_clock_stamps_ns"]
    assert len(pairs)>=2 and all(p["monotonic_before_ns"]==p["monotonic_after_ns"]==p["epoch_ns"] for p in pairs)
    load=read(root/"load_journal.json")
    assert not load["errors"]
    a,b=(round(p["t_s"]*N) for p in load["census"])
    offsets=[round(t*N) for t in load["cpu_busy_t_s"]]
    epochs=[round(p["epoch_s"]*N) for p in rows(root/"battery.jsonl")]
    period=int(CONFIG.get("battery_poll_s",30))
    assert len(epochs)==2+len(offsets)//period
    assert a<=epochs[0] and b<=epochs[-1]
    lo=max(0,a-offsets[0],epochs[0]-offsets[0])
    hi=min(a,b-offsets[-1])
    for which,epoch in enumerate(epochs[1:-1],1):
        i=which*period-1
        hi=min(hi,epoch-offsets[i])
        if i+1<len(offsets): lo=max(lo,epoch-offsets[i+1])
        else: assert epoch<=b
    assert lo<=hi,(kind,lo,hi)
    return lo,hi


def battery_edit(case, root, receipt, terminal):
    rule, op, kind = case.rule, case.op, case.role
    path=root/"battery.jsonl"
    records=rows(path)
    lower, upper=terminal_window(kind)
    if rule=="battery-count":
        if op=="minus":
            del records[len(records)//2]
        elif op=="plus":
            records.insert(1,dict(records[0],epoch_s=records[0]["epoch_s"]+1))
        elif op=="removed-close":
            records.pop()
    elif rule=="battery-census":
        data=read(root/"load_journal.json")
        i=0 if op.startswith("open-") else -1
        # Give the pair room on both sides while keeping dispatch and other samples fixed.
        witness=round(records[i]["epoch_s"]*N)+(-1_000_000 if i==0 else 1_000_000)
        delta={"before":-1,"at":0,"after":1}[op.split("-")[1]]
        data["census"][i]["t_s"]=witness/N
        records[i]["epoch_s"]=(witness+delta)/N
        receipt["census"]=deepcopy(data["census"]);write(root/"load_journal.json",data)
    elif rule=="tick-window":
        data=read(root/"load_journal.json")
        assert not data["errors"]
        a=round(data["census"][0]["t_s"]*N)
        times=[round(t*N) for t in data["cpu_busy_t_s"]]
        period=int(CONFIG.get("battery_poll_s",30))
        # Row 1 at its next CPU stamp implies t0 >= a; the opening census implies t0 <= a.
        records[1]["epoch_s"]=(a+times[period])/N
        if op=="missing": del records[2]
        elif op=="duplicate": records.insert(2,deepcopy(records[2]))
        elif op=="swap": records[2],records[3]=records[3],records[2]
        else:
            side,bound=op.split("-")
            index=2*period-int(side=="lower")
            delta={"minus":-1,"at":0,"plus":1}[bound]
            records[2]["epoch_s"]=(a+times[index]+delta)/N
    elif rule=="battery-terminal" and op.startswith(("open-","close-")):
        start=op.startswith("open-")
        terminal["started_epoch_s" if start else "ended_epoch_s"]=(
            round(records[0 if start else -1]["epoch_s"]*N)+(-1 if start else 1)*int(op.endswith("inside")))/N
    elif rule=="battery-terminal":
        idx=0 if op.endswith("before") else -1
        t=(lower-1/N) if idx==0 else (upper+1/N)
        if op.startswith("error"):
            records[idx]=dict(soc_pct=None,state=None,error="ValueError: synthetic failure",epoch_s=t)
        else:
            records[idx]["epoch_s"]=t
    elif rule=="battery-order":
        mid=len(records)//2
        if op=="duplicate":
            records[mid]["epoch_s"]=records[mid-1]["epoch_s"]
        else:
            records[mid],records[mid-1]=records[mid-1],records[mid]
    elif rule.startswith("battery-work-"):
        begin,end=work_wall(root,kind,receipt)
        idx=0 if rule.endswith("open") else -1
        records[idx]["epoch_s"]=((begin if idx==0 else end)+shift_cmp(op))/N
        # The census precedes each endpoint callback. Move its declared dependent boundary
        # on positive fixtures so an end-of-work equality does not predate its own census.
        if case.expected=="pass":
            load=read(root/"load_journal.json")
            sample=records[idx]["epoch_s"]
            if sample<load["census"][idx]["t_s"]:
                load["census"][idx]["t_s"]=sample
                receipt["census"]=deepcopy(load["census"])
                write(root/"load_journal.json",load)
    elif rule=="drain":
        if op=="missing":
            receipt.pop("battery_drain_pct_per_h")
        else:
            receipt["battery_drain_pct_per_h"]=1.0
        return
    elif rule=="battery-raw":
        if op=="summary":
            receipt["battery"]["samples"]+=1
            return
        if op=="error-shape":
            records[0]["error"]="ValueError: synthetic failure"
        elif op=="raw":
            records[0]["raw"]=records[0]["raw"].replace("80%","79%")
        else:
            records[0]["state"]="charging"
    else:
        raise ValueError(rule)
    write_rows(path,records)
    receipt["battery"]=rt.battery_summary(records)
    if "battery_drain_pct_per_h" in receipt:
        receipt["battery_drain_pct_per_h"]=receipt["battery"]["drain_pct_per_h"]

def journal_edit(case, root, receipt):
    rule,op,kind=case.rule,case.op,case.role
    path=(root/"sensors" if kind=="idle" else root/receipt["bundle"]/"outputs")/"align_thermal.jsonl"
    journal=rows(path)
    if rule=="journal-seq":
        if op=="missing-open": journal.pop(0)
        elif op=="missing-close": journal.pop()
        elif op=="duplicate-open": journal.insert(0, deepcopy(journal[0]))
        else: journal[2:4]=reversed(journal[2:4])
    elif rule=="journal-id":
        name="align-"+str(journal[0]["started"]["monotonic_ns"]+(-1 if op=="minus" else 1))
        for r in journal: r["session"]=name
    elif rule=="journal-project":
        journal[-1]["values"]["coverage"]["period_ns"]+=1
    elif rule=="journal-timing":
        row=next(r for r in journal if r["kind"]=="reading")
        row["finished"]["monotonic_raw_ns"]=row["started"]["monotonic_raw_ns"]+{"invert":-1,"raw-equal":0,"raw-positive":1}[op]
    elif rule=="duration":
        # Retain one full set of monotonic/epoch readings on the same relative series;
        # shorten the final bracket by moving open and removing the first two readings.
        journal=journal[:1]+journal[3:]
        start=journal[0]["started"]["monotonic_ns"]+2*N
        journal[0]["started"]=journal[0]["finished"]=dict.fromkeys(journal[0]["started"],start)
        counter=tg.thermal.Coverage(start,tg.thermal.keys(journal[0]["values"]["thermal"]))
        for i,r in enumerate(journal,1):
            r["seq"]=i
            r["session"]="align-"+str(start)
            if r["kind"]=="reading": counter.observe(r["started"]["monotonic_ns"],r["finished"]["monotonic_ns"],r["values"])
        journal[-1]["values"]["coverage"]=counter.report(journal[-1]["started"]["monotonic_ns"])
    elif rule.startswith(("status-","pm-")):
        indexes=[i for i,r in enumerate(journal) if r["kind"]=="reading"]
        # Use a reading away from a gate boundary with room for +1 ns.
        pos=next(j for j in range(1,len(indexes)) if
                 journal[indexes[j]+1]["started"]["monotonic_ns"]>journal[indexes[j]]["finished"]["monotonic_ns"]+2)
        i=indexes[pos]; row=journal[i]; status=row["values"]["status"]
        prev=journal[indexes[pos-1]]["values"]["status"]
        t=row["finished"]["monotonic_ns"]
        if rule=="status-after":
            if op=="future": status["monotonic_ns"]=journal[-1]["finished"]["monotonic_ns"]+1
            else:
                status["pm_observed_ns"]=prev["pm_observed_ns"]
                status["monotonic_ns"]=t+shift_cmp(op)
        elif rule=="pm-before":
            # Positive lt is a newly observed PM exactly at read finish followed by status at +1 ns.
            status["monotonic_ns"]=t+1
            status["pm_observed_ns"]=t+1+shift_cmp(op)
        elif rule=="pm-cache":
            status["pm_observed_ns"]={"cached":prev["pm_observed_ns"],"fresh":t,"impossible":t-1}[op]
        elif op=="mixed": status["error"]="synthetic"
        else: status.pop({"missing-os":"os_level","missing-pm":"pm_observed_ns","missing-state":"pm_state",
                          "missing-stamp":"monotonic_ns"}[op])
    else:
        raise ValueError(rule)
    write_rows(path,journal)


def from_v4_history(spec, segment, receipt):
    s=sys.modules[__name__]
    case="soak-tail-missing" if spec.rule=="tail-count" else "soak-close-"+spec.op
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
            set_sensor_value(row,key,value)
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

def other_edit(case, root, receipt, outer, terminal):
    kind, rule, op=case.role,case.rule,case.op
    step=shift_cmp(op) if op in ("lt","eq","gt") else 0
    bundle=root/receipt["bundle"] if "bundle" in receipt else None
    if rule.startswith("outer-"):
        start,end=terminal_window("idle")
        if rule=="outer-open": outer["started_ns"]=start*N+step
        elif rule=="outer-close": outer["ended_ns"]=((start+1)*N if op=="one-second" else end*N+step)
        else: outer["ended_ns"]=terminal_window(P)[0]*N+step
        outer["os_load"]=r1.os_load_verdict("idle_soak",receipt,wall_s=(outer["ended_ns"]-outer["started_ns"])/N)
    elif rule=="member-next":
        prev=("idle",P,S,D,X)[("idle",P,S,D,X).index(kind)-1]
        terminal["started_epoch_s"]=(terminal_window(prev)[1]*N+step)/N
    elif rule=="soak-receipt":
        if op=="missing": receipt.pop("sensor_series_end_t_s")
        else: receipt["sensor_series_end_t_s"]+=(1 if op=="plus" else -1)/N
    elif rule=="episode-id":
        path=bundle/"outputs/align_episode.json"
        ep=read(path); ep["episode_id"]+="-other"; write(path,ep)
    elif rule=="endpoint":
        for path,key in ((bundle/"outputs/align_episode.json","endpoint"),(bundle/"metadata.json","endpoint_identity")):
            doc=read(path)
            target=doc if key=="endpoint" else doc["workload_provenance"]
            target[key]={"list":[17],"mixed":True if key=="endpoint" else 1,
                         "integer":17,"boolean":True,"mismatch":"unmatched" if key=="endpoint" else target[key]}[op]
            write(path,doc)
    elif rule=="turn-wire":
        path=bundle/"outputs/align_turns.jsonl"; lines=rows(path)
        if op=="missing": lines.pop()
        elif op=="duplicate": lines.append(deepcopy(lines[-1]))
        else:
            if len(lines)==1:
                # A single-element physical reorder cannot change bytes.
                raise AssertionError("singleton reorder")
            lines.reverse()
        write_rows(path,lines)
    elif rule=="gate-rows":
        path=bundle/"outputs/align_thermal.jsonl"; lines=rows(path)
        i=next(i for i,line in enumerate(lines) if line["kind"]=="align_thermal_gate")
        if op=="missing": lines.pop(i)
        elif op=="duplicate": lines.insert(i,deepcopy(lines[i]))
        else:
            j=next(j for j in range(i+1,len(lines)) if lines[j]["kind"]=="align_thermal_gate")
            lines[i]["values"],lines[j]["values"]=lines[j]["values"],lines[i]["values"]
        for j,line in enumerate(lines,1): line["seq"]=j
        write_rows(path,lines)
    elif rule=="start-state":
        turn=read(bundle/"outputs/align_episode.json")["turns"][0]
        path=bundle/"outputs/align_thermal.jsonl"; lines=rows(path)
        picked=next(row for row in lines if row["kind"]=="reading" and row["started"]["monotonic_ns"]>turn["start_ns"])
        picked["values"]["status"]={"error":"OSError: fixture"};write_rows(path,lines)
    elif rule=="duty":
        receipt["deadman"]["T_dead_s"]+=1
    elif rule=="inventory-start":
        path=root/"inventory/inventory_journal.jsonl"; lines=rows(path)
        start=rows(bundle/"outputs/align_thermal.jsonl")[0]["started"]["monotonic_ns"]
        kept=[r for r in lines if r["started"]["monotonic_ns"]>start]
        for j,r in enumerate(kept,1): r["seq"]=j
        write_rows(path,kept)
        update_classification(root,receipt)
    elif rule=="inventory-wire":
        path=root/"inventory/inventory_journal.jsonl"
        if op=="incomplete":
            p=root/"inventory/r1_classification.json"; value=read(p)
            value["inventory"]["complete"]=False; write(p,value)
        else:
            lines=rows(path)
            if op=="phase": lines[0]["phase"]="prefill"
            else: lines[0]["values"].pop("readings")
            write_rows(path,lines)
    elif rule=="recovery-order":
        p=root/"recovery/align_thermal.jsonl"; lines=rows(p)
        start=read(bundle/"outputs/align_episode.json")["turns"][-1]["end_ns"]-1
        lines[0]["started"]=lines[0]["finished"]=dict.fromkeys(lines[0]["started"],start)
        counter=tg.thermal.Coverage(start,tg.thermal.keys(lines[0]["values"]["thermal"]))
        for r in lines:
            r["session"]="align-"+str(start)
            if r["kind"]=="reading": counter.observe(r["started"]["monotonic_ns"],r["finished"]["monotonic_ns"],r["values"])
        lines[-1]["values"]["coverage"]=counter.report(lines[-1]["started"]["monotonic_ns"])
        write_rows(p,lines)
    elif rule=="pm-records":
        p=bundle/"rich_telemetry.jsonl"; lines=rows(p)
        if op=="missing": lines.pop()
        else: lines[1]["timestamp_s"]+=1/N
        write_rows(p,lines)
    elif rule=="step-reference":
        p=bundle/"outputs/align_window_reference.json"; value=read(p)
        value["samples"][0][0]+=1; write(p,value)
    else:
        raise ValueError(rule)

def update_classification(root,receipt):
    inventory=read(root/"inventory/r1_classification.json")["inventory"]
    writer=NSpace(out=root,config=CONFIG,sensors=rt.sensors_policy(CONFIG),stop_inventory=lambda:None,
                  inventory=NSpace(inventory=inventory,keys=[r["key"] for r in inventory["keys"]],
                                   rows=rows(root/"inventory/inventory_journal.jsonl")))
    member=NSpace(ep=wl.read_episode_bundle(root/receipt["bundle"]))
    receipt["thermometry"]=rt.Segment.thermometry(writer,member,label="step-d",record_only=False)
    receipt["slot_detail"]["thermometry_classification_sha256"]=receipt["thermometry"]["classification_sha256"]

def extra_edit(case, root, receipt, terminal):
    rule,op,kind=case.rule,case.op,case.role
    bundle=root/receipt["bundle"]
    journal=bundle/"outputs/align_thermal.jsonl"
    if rule=="saved-receipt":
        return  # The pre-close raw file is written after the separately observed stdout has been saved.
    if rule=="x-ran":
        (bundle/"outputs/align_episode.json").unlink()
    elif rule=="runtime-cut":
        receipt["episode_flags"].append({"809c-time-guard":"episode.time_guard:3","809b-timeout":"thermal.gate_timeout:3",
                                        "809b-deadman":"episode.deadman:3"}[op])
    elif rule=="release-copy":
        receipt["g0_release"]=dict(fast_c=38.0,slow_c=38.0)
    elif rule=="final-gate":
        docs=rows(journal)
        i=max(i for i,r in enumerate(docs) if r["kind"]=="align_thermal_gate" and r["values"]["state"]=="end")
        del docs[i]
        for j,r in enumerate(docs,1): r["seq"]=j
        write_rows(journal,docs)
    elif rule=="first-status":
        ep=read(bundle/"outputs/align_episode.json");start=ep["turns"][0]["start_ns"]
        docs=rows(journal)
        row=next(r for r in docs if r["kind"]=="reading" and r["started"]["monotonic_ns"]>start)
        if op.endswith("error"): row["values"]["status"]={"error":"OSError: synthetic"}
        else: row["values"]["status"]["os_level"]=2
        write_rows(journal,docs)
    elif rule=="sensor-bracket":
        docs=rows(journal)
        a=docs[0]["started"]["wall_ns"]
        b=docs[-1]["finished"]["wall_ns"]
        ticks=(b-a)//N
        issue_segment_journals(root,kind,number_of_ticks=ticks,closing_epoch=b/N)
        load=read(root/"load_journal.json")
        for key in ("census","cpu_busy_cores","cpu_busy_t_s"):
            receipt[key]=load[key]
        p=bundle/"events.jsonl"; events=rows(p); events[-1]["timestamp_s"]=b/N; write_rows(p,events)
        battery=rows(root/"battery.jsonl")
        if op=="r3-late-sensor-open": battery[0]["epoch_s"]=(a+1)/N
        if op=="r3-early-sensor-close": battery[-1]["epoch_s"]=(b-1)/N
        write_rows(root/"battery.jsonl",battery);receipt["battery"]=rt.battery_summary(battery)
        terminal["ended_epoch_s"]=b/N+0.5
    elif rule=="one-battery":
        battery=rows(root/"battery.jsonl")[:1];write_rows(root/"battery.jsonl",battery)
        receipt["battery"]=rt.battery_summary(battery)
    elif rule=="session-nesting":
        docs=rows(journal); ep=read(bundle/"outputs/align_episode.json")
        t=ep["end_ns"]+{"before-end":-1,"equal-end":0,"after-end":1}[op]
        assert docs[-2]["finished"]["monotonic_ns"]<=t
        docs[-1]["started"]=docs[-1]["finished"]=dict.fromkeys(docs[-1]["started"],t)
        counter=tg.thermal.Coverage(docs[0]["started"]["monotonic_ns"],tg.thermal.keys(rt.sensors_policy(CONFIG)))
        for r in docs:
            if r["kind"]=="reading": counter.observe(r["started"]["monotonic_ns"],r["finished"]["monotonic_ns"],r["values"])
        docs[-1]["values"]["coverage"]=counter.report(t);write_rows(journal,docs)
    elif rule=="inventory-bracket":
        path=root/"inventory/inventory_journal.jsonl"; docs=rows(path)
        census=read(root/"load_journal.json")["census"]
        i=0 if op=="sweep-before" or op.startswith("open-") else -1
        delta={"sweep-before":-1,"sweep-after":1,"open-equal":0,"open-inside":1,"close-equal":0,"close-inside":-1}[op]
        val=round(census[i]["t_s"]*N)+delta
        docs[i]["started"]=docs[i]["finished"]={"monotonic_ns":val}
        write_rows(path,docs);update_classification(root,receipt)
    elif rule=="cached-state":
        docs=rows(journal); readings=[r for r in docs if r["kind"]=="reading"]
        prev,now=(r["values"]["status"] for r in readings[:2])
        now["pm_observed_ns"]=prev["pm_observed_ns"]
        if op=="changed-at-old-pm": now["pm_state"]="Fair"
        write_rows(journal,docs)
    elif rule=="raw-pair":
        import plistlib
        from joulewise.adapters.powermetrics import rich_telemetry_jsonl
        p=bundle/"raw/powermetrics.plist";parts=p.read_bytes().split(b"\x00")
        value=plistlib.loads(parts[0]); rich=bundle/"rich_telemetry.jsonl"
        anchor=rows(rich)[0]["timestamp_s"]
        value["elapsed_ns"]=round((anchor-terminal["started_epoch_s"])*N)+1
        parts[0]=plistlib.dumps(value); raw=b"\x00".join(parts)
        p.write_bytes(raw);rich.write_text(rich_telemetry_jsonl(raw,first_record_endpoint_s=anchor))
    else: raise ValueError(rule)



def threshold_edit(case,root,receipt,outer):
    NANO=10**9
    if case.rule=="cpu-min":
        source=read(root/"load_journal.json")
        opening,closing=(r["t_s"] for r in source["census"])
        low,high=terminal_window(case.role)
        duration=(outer["ended_ns"]-outer["started_ns"])/NANO if case.member=="I" else high-low
        n=math.ceil(r1.CPU_JOURNAL_MIN_RATE*max(duration,closing-opening)-r1.CPU_JOURNAL_SLACK_S)
        n+={"below":-1,"at":0,"above":1}[case.op]
        issue_segment_journals(root,case.role,number_of_ticks=n,closing_epoch=closing,tick_spacing=(closing-opening-1)/n)
        data=read(root/"load_journal.json")
        for key in ("cpu_busy_t_s","cpu_busy_cores","census"): receipt[key]=data[key]
        receipt["battery"]=rt.battery_summary(rows(root/"battery.jsonl"))
        if "battery_drain_pct_per_h" in receipt: receipt["battery_drain_pct_per_h"]=receipt["battery"]["drain_pct_per_h"]
        if case.member=="I" and case.expected=="pass":
            outer["os_load"]=r1.os_load_verdict("idle_soak",receipt,wall_s=duration)
        return
    path=root/"sensors/align_thermal.jsonl"
    docs=rows(path); opening,end=docs[0],docs[-1]; data=docs[1:-1]
    begin=opening["started"]["monotonic_ns"]
    if case.rule=="duration":
        close=begin+round(receipt["duration_s"]*NANO)+{"below":-1,"at":0,"above":1}[case.op]
        end["started"]=end["finished"]=dict.fromkeys(end["started"],close)
        data=[r for r in data if r["finished"]["monotonic_ns"]<=close]
    else:
        close=end["started"]["monotonic_ns"]
        first=close-r1.SOAK_TAIL_S*NANO
        # Remove the oldest common tail samples. The close window is precisely the binding count.
        tail=[r for r in data if r["started"]["monotonic_ns"]>first]
        remove={r["seq"] for r in tail[:len(tail)-int(case.op)]}
        data=[r for r in data if r["seq"] not in remove]
    policy=rt.sensors_policy(CONFIG)
    coverage=tg.thermal.Coverage(begin,tg.thermal.keys(policy))
    for r in data:coverage.observe(r["started"]["monotonic_ns"],r["finished"]["monotonic_ns"],r["values"])
    end["values"]["coverage"]=coverage.report(close)
    docs=[opening,*data,end]
    for pos,r in enumerate(docs,1):r["seq"]=pos
    write_rows(path,docs)
    reads=tg.sample_rows(docs);first=reads[0]["monotonic_ns"]
    for key in (policy["s_fast"],policy["s_slow"]):
        valid=rt.valid_series(reads,key)
        receipt["sensor_series_c"][key]=[v for _,v in valid]
        receipt["sensor_series_t_s"][key]=[(n-first)/NANO for n,_ in valid]
        receipt["sensor_series_failed_reads"][key]=len(reads)-len(valid)
    receipt["sensor_series_end_t_s"]=(reads[-1]["monotonic_ns"]-first)/NANO


def adjunct_edit(case, root, receipt, terminal):
    kind, rule, op = case.role, case.rule, case.op
    bundle = root / receipt.get("bundle", "")
    if rule=="smc-errors":
        from joulewise.align.apple import smc_reader as sr
        path=root/"sensors/align_thermal.jsonl" if kind=="idle" else bundle/"outputs/align_thermal.jsonl"
        points=rows(path)
        row=next(r for r in points if r["kind"]=="reading")
        key=CONFIG["sensors"]["fan_keys"][0]
        def call(request):
            if request.data8==sr.CMD_GET_KEY_INFO:
                return NSpace(result=1 if op=="key-info" else 0,
                              keyInfo=NSpace(dataSize=2,dataType=sr.fourcc("xxxx" if op=="decode" else "fpe2")))
            assert request.data8==sr.CMD_READ_KEY
            return NSpace(result=1 if op.startswith("read") else 0,bytes=b"xx")
        reply=sr.Reader(transport=NSpace(call=call)).read([key])
        error=reply["errors"][key]
        raw=reply["raw"][key]
        assert (not raw if op=="key-info" else raw["raw_hex"] is None if op.startswith("read") else raw["raw_hex"]=="7878")
        if op=="read-no-hex": del raw["raw_hex"]
        row["values"]["sensors"][key]=None
        row["values"]["errors"][key]=row["error"]=error
        row["values"]["readings"][key]={**raw,"value":None,"error":error}
        coverage=tg.thermal.Coverage(points[0]["started"]["monotonic_ns"],tg.thermal.keys(rt.sensors_policy(CONFIG)))
        for point in points:
            if point["kind"]=="reading": coverage.observe(point["started"]["monotonic_ns"],point["finished"]["monotonic_ns"],point["values"])
        span=points[-1]["values"]["coverage"]["span_ns"]
        points[-1]["values"]["coverage"]=coverage.report(span[1])
        write_rows(path,points)
    elif rule in ("smc-wire","inventory-raw"):
        source=(root/"inventory/inventory_journal.jsonl" if rule=="inventory-raw" else
                root/"sensors/align_thermal.jsonl" if kind=="idle" else bundle/"outputs/align_thermal.jsonl")
        points=rows(source)
        row=points[0] if rule=="inventory-raw" else next(r for r in points if r["kind"]=="reading")
        key=CONFIG["sensors"]["s_fast"]
        raw=row["values"]["readings"][key]
        assert raw["raw_hex"] and len(raw["raw_hex"])==2*raw["data_size"]
        if op=="absent": del raw["raw_hex"]
        elif op=="size-minus": raw["data_size"]-=1
        elif op=="size-plus": raw["data_size"]+=1
        elif op=="raw-value": raw["raw_hex"]=issued_smc_key(key,raw["value"]+1)[1]["raw_hex"]
        write_rows(source,points)
    elif rule=="observe-status":
        path=root/("sensors" if kind=="idle" else "recovery")/"align_thermal.jsonl"
        points=rows(path)
        reading=next(r for r in points if r["kind"]=="reading")["values"]
        assert reading["status"]=={}
        if op=="missing": del reading["status"]
        elif op=="null": reading["status"]=None
        elif op=="wrong-type": reading["status"]=[]
        write_rows(path,points)
    elif rule in ("gate-duration","gate-copies"):
        ev=bundle/"events.jsonl"
        ep=bundle/"outputs/align_episode.json"
        side=bundle/"outputs/align_thermal.jsonl"
        journal,events,episode=rows(side),rows(ev),read(ep)
        recs=episode["hardware"]["thermal"]["intervals"]
        gate=recs[0]
        ix=[i for i,r in enumerate(events) if r["phase"] in ("align_thermal_gate","align_thermal_hold")]
        assert len(ix)==2*len(recs)
        if rule=="gate-copies":
            if op=="missing": events.pop(ix[-1])
            elif op=="duplicate": events.insert(ix[-1],deepcopy(events[ix[-1]]))
            elif op=="reordered":
                first,last=events[ix[0]],events[ix[1]]
                events[ix[0]],events[ix[1]]=dict(last,timestamp_s=first["timestamp_s"]),dict(first,timestamp_s=last["timestamp_s"])
        elif op!="issued":
            gate["duration_s"]+=(1 if op=="plus" else -1)/N
            for i in ix[:2]: events[i]["metadata"]=deepcopy(gate)
            next(r for r in journal if r["kind"]=="align_thermal_gate" and r["values"]["state"]=="end")["values"]["gate"]=deepcopy(gate)
        write_rows(side,journal);write_rows(ev,events);write(ep,episode)
    elif rule=="terminal-envelope":
        key={"status":"status","kind":"kind","config":"config_sha256"}[op]
        terminal[key]="failed" if op=="status" else "other-issued-member" if op=="kind" else "9"*64
    elif rule=="outer-statistics":
        # Mutate the launcher record after its child has returned; its independently bound source stays fixed.
        return
    elif rule in ("journal-envelope","journal-report"):
        p=(root/"sensors" if kind=="idle" else bundle/"outputs")/"align_thermal.jsonl"
        docs=rows(p)
        if rule=="journal-envelope":
            row=next(r for r in docs if r["kind"]=="reading")
            field={"nonempty-raw":"raw","wrong-module":"module","wrong-schema":"schema"}[op]
            row[field]=[1] if field=="raw" else "unissued"
        else:
            bound=docs[-2]["finished"]["monotonic_ns"] if op=="before" else docs[-1]["started"]["monotonic_ns"]
            report=docs[-1]["values"]["coverage"]
            report["span_ns"][1]=bound+(-1 if op=="before" else 1)
        write_rows(p,docs)
    elif rule == "bundle-unique":
        if op == "second":
            shutil.copytree(bundle, bundle.with_name(bundle.name+"-additional"), copy_function=os.link)
    elif rule in ("desk-owned", "desk-owned-required", "desk-gross"):
        key = "energy_j" if rule.startswith("desk-owned") else "gross_episode_j"
        if op=="plus": receipt[key]=(receipt[key] or 0)+1
        elif op=="missing": del receipt[key]
    elif rule in ("poll-edge","poll-error"):
        load=read(root/"load_journal.json")
        period=int(CONFIG.get("battery_poll_s",30))
        tick=(len(load["cpu_busy_t_s"])//period)*period
        tick+={"below":-1,"above":1}.get(op,0)
        issue_segment_journals(root,kind,number_of_ticks=tick,closing_epoch=load["census"][-1]["t_s"],
            load_failure=journal_open(kind)+period if op in ("load-error","lost-periodic") else None,
            battery_failure=journal_open(kind)+period if op=="battery-error" else None)
        load=read(root/"load_journal.json")
        for key in ("census","cpu_busy_t_s","cpu_busy_cores"): receipt[key]=load[key]
        receipt["load_journal_errors"]=load["errors"]
        p=root/"battery.jsonl"; stream=rows(p)
        if op in ("at-omit","lost-periodic"): del stream[1]
        elif op=="at-extra": stream.insert(1,dict(stream[0],epoch_s=stream[0]["epoch_s"]+1))
        write_rows(p,stream)
        receipt["battery"]=rt.battery_summary(stream)
        if "battery_drain_pct_per_h" in receipt: receipt["battery_drain_pct_per_h"]=receipt["battery"]["drain_pct_per_h"]
    elif rule == "gate-stamp":
        side=bundle/"outputs/align_thermal.jsonl"
        journal=rows(side); position,delta=op.split("-")
        entry=position=="entry"
        row=next(r for r in journal if r["kind"] in ("align_thermal_gate","align_thermal_hold") and
                 r["values"]["state"]==("begin" if entry else "end"))
        field=position+"_stamp"
        old=(row["values"] if entry else row["values"]["gate"])[field]
        anchor=row["started"]["monotonic_ns"]
        mid=(old["monotonic_before_ns"]+old["monotonic_after_ns"])//2
        assert anchor==mid
        if delta=="before":
            for clock in row["started"]:
                row["started"][clock]+=1
            row["finished"]=dict(row["started"])
        elif delta=="after":
            new=dict(old,monotonic_before_ns=anchor-1,monotonic_after_ns=anchor+1)
            def revise(value):
                if isinstance(value,dict):
                    for key,child in value.items():
                        if key==field and child==old: value[key]=dict(new)
                        else: revise(child)
                elif isinstance(value,list):
                    for child in value: revise(child)
            for p in (bundle/"events.jsonl",bundle/"outputs/align_episode.json"):
                doc=load_doc(p);revise(doc);save_doc(p,doc)
            revise(journal)
            index=journal.index(row)
            if journal[index+1]["started"]["monotonic_ns"]==anchor:
                assert journal[index+1]["finished"]["monotonic_ns"]==anchor
                journal[index],journal[index+1]=journal[index+1],row
        # A simultaneous reader can acquire Sidecar's lock before the delayed gate write.
        journal.sort(key=lambda r:r["started"]["monotonic_ns"])
        for index,point in enumerate(journal,1): point["seq"]=index
        write_rows(side,journal)
    elif rule=="d018":
        fname="power_trace.csv"
        write_decision(bundle/fname,DecisionCase(kind,"raw",fname,(),op))
    else:
        paths={"warmup-events":bundle/"events.jsonl", "recovery-span":root/"recovery/align_thermal.jsonl",
               "bank-poll":bundle/"outputs/align_thermal.jsonl", "turn-parse":bundle/"outputs/align_turns.jsonl",
               "switch-sensors":root/RECEIPT, "overlap-history":root/rt.CUSTODY_NAME}
        p=paths[rule];mutation=Mutation(kind,p.relative_to(root).as_posix(),(),op)
        if rule=="overlap-history":
            prev=root.parent/S
            terminal["started_epoch_s"]=read(prev/rt.CUSTODY_NAME)["ended_epoch_s"]-1
        elif rule=="switch-sensors": mutate(mutation,receipt)
        else:
            apply_case(root.parent,root,mutation)
            if rule=="recovery-span": receipt.update(read(root/RECEIPT))


def assess_transport(base,case):
    with tempfile.TemporaryDirectory(dir=base.parent) as tmp:
        probe=object.__new__(Probe);probe.base=base;probe.tree=Path(tmp);probe.ref=read(base/"reference.json")
        accepted=probe.candidate(LaunchCase(case.role,case.op))
        result=read(probe.tree/"native/synthetic-run/part-c/smoke.json")["evaluation"]
        if case.expected=="pass":
            return "AGREES_PASS" if accepted and result["verdict"]=="pass" else "WRONG_VERDICT"
        if accepted:return "FALSE_PASS"
        return "REFUSED" if case.expected in result["evidence_failures"] else "WRONG_VERDICT"


def assess_descriptor(base, case):
    global WORKER
    with tempfile.TemporaryDirectory(dir=base.parent) as tmp:
        probe=object.__new__(Probe);probe.base=base;probe.tree=Path(tmp);probe.ref=read(base/"reference.json")
        WORKER=probe
        result=descriptor_trial(DescriptorCase(case.role,case.op))[0]
        out=probe.tree/"native/synthetic-run/part-c"
        for role in (P,S,D,X):
            dest=out/pc.KINDS[role]
            if not dest.exists(): copy_segment(base,role,dest)
        archive=pc.replay_archived(out,rt.ROOT/r1.DEFAULT_RUNTIME_CONFIG)
        if archive["verdict"]!="pass" or archive["native_limit"]!=dict.fromkeys((P,S,D,X),"unattested"):
            return "WRONG_VERDICT"
        return result


def field_edit(case, root, receipt, outer):
    with RULE_FILE.open() as stream:
        row = next(r for r in csv.DictReader(stream,delimiter="\t") if r["id"] == case.rule)
    target, address = row["operand"].split(":",1)
    bundle = root / receipt.get("bundle","")
    files = {"ep":bundle/"outputs/align_episode.json", "meta":bundle/"metadata.json",
             "events":bundle/"events.jsonl","ref":bundle/"outputs/align_window_reference.json",
             "journal":bundle/"outputs/align_thermal.jsonl"}
    if target=="rec": doc=receipt
    else:
        path=files[target]; doc=rows(path) if path.suffix==".jsonl" else read(path)
    cur=doc
    keys=address.replace("PHASES","deadman/phases_s" if case.role==D else "phases_s").split("/")
    for key in keys[:-1]:
        if key=="READ": cur=next(r for r in cur if r["kind"]=="reading")
        else: cur=cur[int(key) if key.lstrip("-").isdigit() else key]
    key=int(keys[-1]) if keys[-1].isdigit() else keys[-1]
    old=cur[key]
    if case.op=="missing": del cur[key]
    elif case.op=="null": cur[key]=None
    elif case.op=="wrong-type": cur[key]=[old]
    elif case.op=="different": cur[key]="synthetic-unmatched"
    elif case.op in ("minus","plus"):
        step = 1 if case.op=="plus" else -1
        cur[key]=old+step
    elif case.op!="equal": raise ValueError(case.op)
    if target!="rec":
        (write_rows if path.suffix==".jsonl" else write)(path,doc)



with RULE_FILE.open() as _stream:
    FIELD_RULES = {r["id"] for r in csv.DictReader(_stream,delimiter="\t") if r["operand"] and r["operand"]!="special" and not r["operand"].startswith("closed:")}

def propagate_step_digest(base, stage, receipt):
    """Issue downstream members from the selected Step bytes before the native/archival transport."""
    journal = Path(receipt["bundle"])/"outputs/align_thermal.jsonl"
    new_digest = hashlib.sha256((stage/S/journal).read_bytes()).hexdigest()
    if new_digest == hashlib.sha256((base/S/journal).read_bytes()).hexdigest():
        return
    for role in (D,X):
        member = stage/role
        assert member.is_symlink()
        member.unlink()
        shutil.copytree(base/role, member, copy_function=os.link)
        episode_file = member/read(member/RECEIPT)["bundle"]/"outputs/align_episode.json"
        doc = read(episode_file)
        unshared(episode_file)
        doc["hardware"]["thermal"]["custody"]["source_journal_sha256"] = new_digest
        write(episode_file, doc)
        terminal_file = member/rt.CUSTODY_NAME
        terminal = read(terminal_file)
        unshared(terminal_file)
        rt.write_custody(member, terminal)


def prepare_stage(base, work, case):
    stage=work/"fixture"; stage.mkdir()
    for k in ROLE.values():
        if k==case.role: shutil.copytree(base/k,stage/k)
        else: (stage/k).symlink_to(base/k,target_is_directory=True)
    shutil.copytree(base/"soak",stage/"soak",copy_function=os.link)
    for name in OUTER: unshared(stage/"soak"/name)
    root=stage/case.role
    receipt=read(root/RECEIPT)
    terminal=read(root/rt.CUSTODY_NAME)
    o=stage/"soak/soak_row.json"; outer=read(o)
    if case.rule.startswith("bound-"):
        pass  # Applied after closing the unmodified synthetic member below.
    elif case.rule in ("duration","cpu-min","tail-count") and case.op not in ("short","trim"):
        threshold_edit(case,root,receipt,outer)
    elif case.rule in ('smc-errors','smc-wire','inventory-raw','observe-status','gate-duration','gate-copies','terminal-envelope','journal-envelope','journal-report','outer-statistics','desk-owned-required','bundle-unique', 'desk-owned', 'desk-gross', 'poll-edge', 'poll-error', 'gate-stamp', 'warmup-events', 'recovery-span', 'bank-poll', 'turn-parse', 'switch-sensors', 'overlap-history', 'd018'):
        adjunct_edit(case,root,receipt,terminal)
    elif case.rule in ('saved-receipt', 'x-ran', 'runtime-cut', 'final-gate', 'release-copy', 'first-status', 'sensor-bracket', 'one-battery', 'session-nesting', 'inventory-bracket', 'cached-state', 'raw-pair'):
        extra_edit(case,root,receipt,terminal)
    elif case.rule in FIELD_RULES:
        field_edit(case,root,receipt,outer)
    elif case.rule.startswith(("census-","pid-","cpu-","prior-")) or case.rule=="replay":
        load_edit(case,root,receipt)
    elif case.rule.startswith("battery-") or case.rule in ("drain","tick-window"):
        battery_edit(case,root,receipt,terminal)
    elif case.rule.startswith(("journal-","status-","pm-")) and case.rule!="pm-records" or case.rule=="duration":
        journal_edit(case,root,receipt)
    elif case.rule in ("tail-count","tail-settle"):
        from_v4_history(case,root,receipt)
    else: other_edit(case,root,receipt,outer,terminal)
    if case.rule in ("prior-origin","prior-census") and case.expected=="pass":
        roles=list(ROLE.values())
        previous=roles[roles.index(case.role)-1]
        prev=stage/previous
        prev.unlink()
        shutil.copytree(base/previous,prev,copy_function=os.link)
        q=read(prev/"load_journal.json")["census"][-1]["t_s"]
        old_terminal=read(prev/rt.CUSTODY_NAME)
        old_terminal["ended_epoch_s"]=q
        rt.write_custody(prev,old_terminal)
        terminal["started_epoch_s"]=q
        if previous=="idle":
            outer["ended_ns"]=round(q*N)
            outer["os_load"]=r1.os_load_verdict("idle_soak",read(prev/RECEIPT),
                                                 wall_s=(outer["ended_ns"]-outer["started_ns"])/N)
        load=read(root/"load_journal.json")
        origin=q+shift_cmp(case.op)/N
        if case.rule=="prior-census":
            original_open=read(base/case.role/"load_journal.json")["census"][0]["t_s"]
            load["cpu_busy_t_s"]=[t+(original_open-origin) for t in load["cpu_busy_t_s"]]
            receipt["cpu_busy_t_s"]=deepcopy(load["cpu_busy_t_s"])
            write(root/"load_journal.json",load)
        else:
            # The same absolute tick also issued the corresponding periodic battery stamp.
            bat=rows(root/"battery.jsonl"); period=int(CONFIG.get("battery_poll_s",30))
            for j,point in enumerate(bat[1:-1],1): point["epoch_s"]=origin+load["cpu_busy_t_s"][j*period-1]
            write_rows(root/"battery.jsonl",bat);receipt["battery"]=rt.battery_summary(bat)
            if "battery_drain_pct_per_h" in receipt: receipt["battery_drain_pct_per_h"]=receipt["battery"]["drain_pct_per_h"]
    if case.role!= "idle" and case.expected=="pass" and case.rule in (
            "prior-origin","prior-census","tick-window","battery-census","battery-work-open","battery-work-close","battery-terminal"):
        interval=assert_callback_order(root,case.role,receipt)
        if case.rule.startswith("prior-"): assert interval[1]>=round(q*N)
    put_result(root,receipt)
    if case.rule=="saved-receipt": (root/RECEIPT).write_bytes(b"{")
    rt.write_custody(root,terminal)
    # Outer copies arise before the synthetic evidence ledger and are never repaired during verification.
    if case.role=="idle":
        outer["result"]=receipt
        if case.rule in ("cpu-hot","cpu-values","cpu-gap","prior-census","poll-edge","battery-work-open","battery-work-close","battery-census") and case.expected=="pass":
            outer["os_load"]=r1.os_load_verdict("idle_soak",receipt,wall_s=(outer["ended_ns"]-outer["started_ns"])/N)
        if case.rule=="tail-settle" or case.rule in ("duration","tail-count") and case.op not in ("short","trim","1079"):
            stats=r1.soak_detrended(receipt["sensor_series_c"],receipt["sensor_series_t_s"],
                                    receipt["sensor_series_end_t_s"])
            outer["soak_detrended"]=stats
            refpath=stage/"soak/soak_reference.json"
            refdoc=read(refpath)
            refdoc.update(detrended=stats,sensors_c={k:v["mean_c"] for k,v in stats.items()})
            write(refpath,refdoc)
    if case.rule=="outer-statistics":
        key=CONFIG["sensors"]["s_fast"]
        if case.op=="missing": del outer["soak_detrended"][key]["mean_c"]
        else: outer["soak_detrended"][key]["mean_c"]+=1 if case.op=="mean-plus" else -1
    write(o,outer)
    if case.role == S: propagate_step_digest(base, stage, receipt)
    if case.rule.startswith("bound-") and case.op!="keep":
        binding_edit(case,root,receipt)
    return stage

def binding_edit(case,root,receipt):
    with RULE_FILE.open() as stream:
        rule=next(r for r in csv.DictReader(stream,delimiter="\t") if r["id"]==case.rule)
    relative=rule["operand"].removeprefix("closed:")
    if relative.startswith("bundle/"):
        relative=receipt["bundle"]+"/"+relative.removeprefix("bundle/")
    path=root/relative
    if case.op=="unattested":
        manifest=root/rt.CUSTODY_NAME; document=read(manifest)
        assert document["files"].pop(relative)
        write(manifest,document)
    elif case.op=="missing": path.unlink()
    else:
        raw=path.read_bytes()
        assert raw
        # The bound digest is the independent witness, even for a one-line typed object.
        changed=raw+raw if case.op=="duplicated-bytes" else raw[1:]+raw[:1]
        assert raw!=changed
        path.write_bytes(changed)


def assess_launch_config(case):
    # RL-216 R2: the refusal stage is the kit's start. The soak is dispatched once and no member is.
    fx = new_fixture()
    idle=[];members=[]
    try:
        source=fx.attempt.config
        copy=source.with_name("v4-synthetic-config-copy.json")
        copy.write_bytes(source.read_bytes())
        try:
            fx.runtime=["synthetic-runtime", *(["--config="+str(copy)] if case.op=="equals" else
                                               ["--config",str(source),"--config",str(copy)])]
            make_idle=fx.make_idle
            def observed_idle():
                idle.append("idle")
                return make_idle()
            def observed_member(kind,segment):
                members.append(kind)
                raise OSError("synthetic dispatch witness")
            with patch.object(fx,"make_idle",observed_idle):
                rc=fx.run_launcher(model_transport=observed_member)
            if members or idle!=["idle"]: return "WRONG_VERDICT"  # A member dispatched on an unbound config is too late.
            root,out=fx.attempt.root,fx.attempt.output
            if not all(p.is_file() for p in (out/"smoke.json",out/"smoke_part_c.json",root/"part-c.stdout.log")):
                return "WRONG_VERDICT"
            record=read(out/"smoke.json");result=record["evaluation"];runner=read(root/"runner_receipt.json")
            found={(f.get("reason"),f.get("field")) for f in map(json.loads,(
                line for line in (root/"part-c.stdout.log").read_text().splitlines() if line.startswith("{")))}
            refused=(rc==2 and runner["rc"]==2 and runner["parts"]=={"C":False} and record==read(out/"smoke_part_c.json")
                     and result["verdict"]=="other_failure" and result["pass"] is False
                     and case.expected in result["evidence_failures"] and (case.expected,"--config") in found)
            return "REFUSED" if refused else "WRONG_VERDICT"
        finally: copy.unlink()
    finally: fx.doCleanups()


def assess_case(base,case):
    if case.rule in ("gate-entry-witness","gate-exit-witness"):
        prefix="x-g-gate-entry-" if case.rule=="gate-entry-witness" else "x-g-unobserved-exit-slope-"
        proc=subprocess.run([sys.executable,"-IB",str(HERE.with_name("partc_v4_history.py")),prefix+case.op],
                            text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if proc.returncode!=0:
            if "Traceback (most recent call last)" in proc.stdout: raise AssertionError(proc.stdout)
            return "WRONG_VERDICT"
        return "AGREES_PASS" if case.expected=="pass" else "REFUSED"
    if case.rule=="launch-config": return assess_launch_config(case)
    if case.rule=="return-descriptor": return assess_descriptor(base,case)
    if case.rule in ("return-code","stdout-record","x-absence"): return assess_transport(base,case)
    with tempfile.TemporaryDirectory(dir=base.parent) as tmp:
        work=Path(tmp)
        stage=prepare_stage(base,work,case)
        return judge_stage(base,case,stage,work)

def judge_stage(base,case,stage,work):
    probe=object.__new__(Probe)
    probe.base=stage;probe.tree=work/"actual";probe.ref=read(stage/"soak/soak_reference.json")
    if case.rule=="saved-receipt": probe.stdout_files={case.role:base/case.role/RECEIPT}
    accepted=probe.candidate(None)
    root=probe.tree/"native/synthetic-run"
    native=read(root/"part-c/smoke.json")["evaluation"]
    # A refusal before dispatch has no bytes for later members on the native side.
    # The archive input is assembled independently from the same pre-close synthetic bytes.
    for k in (P,S,D,X):
        dest=root/"part-c"/pc.KINDS[k]
        if not dest.exists(): copy_segment(stage,k,dest)
    replay=pc.replay_archived(root/"part-c",rt.ROOT/r1.DEFAULT_RUNTIME_CONFIG)
    expected=case.expected
    def verdict(word, reasons):
        if expected=="pass": return word=="pass" and not reasons
        if expected=="start_state": return word=="start_state_failed"
        return word==("start_state_failed" if expected=="start_state" else "other_failure") and expected in reasons
    native_ok=verdict(native["verdict"],native["evidence_failures"])
    replay_ok=verdict(replay["verdict"],replay["failing_checks"])
    if os.environ.get("JW_V4_OBSERVE"):
        print("OBS",case.name,native["verdict"],sorted(native["evidence_failures"]),replay["verdict"],
              replay["failing_checks"],flush=True)
    primary=set(native["evidence_failures"])
    archived_classes=archive_refusal_codes(replay,primary)
    if native_ok and replay_ok and native["verdict"]==replay["verdict"] and primary==archived_classes: return "AGREES_PASS" if expected=="pass" else "REFUSED"
    if expected!="pass" and (accepted or replay["verdict"]=="pass"): return "FALSE_PASS"
    return "WRONG_VERDICT"

@lru_cache(maxsize=1)
def refusal_codes():
    with RULE_FILE.open() as stream:
        listed={r["reason"] for r in csv.DictReader(stream,delimiter="\t") if r["reason"]!="LOAD"}
    return listed | {c.expected for c in writer_cases() if c.expected!="pass"} | {
        "source_integrity","issued_driver","issued_part_c","release_conditions","gate_outcome",
        "release_sample","sidecar_derivation","gate_reference","interval_clock","interval_shape",
        "gate_duration","gate_pair","reference_values","turn_boundary_recompute","turn_record",
        "episode_identity","admission_recompute","receipt_pair","step_configuration",
        "pinned_closure_mismatch","pinned_closure_import_escape","pinned_closure_missing_object",
        "context_checks","execution_config","execution_limits_recompute","gate_cardinality",
        "issued_identity","member_cut","sequence","step_energy","tool_boundaries","verdict_binding",
        "x_g_unrun_unproven","frozen_oracle","issued_workload","step_release","gate_time",
        "start_state","x_g_evidence","member_energy"}


def archive_refusal_codes(replay,native):
    # Older wire puts fields and release-line labels in the same list as refusal codes.
    # A separately published typed reason list is authoritative when available.
    typed=replay.get("evidence_failures")
    if typed is not None:
        assert isinstance(typed,list) and all(isinstance(reason,str) for reason in typed)
        return set(typed)
    return set(replay["failing_checks"]) & (set(native) | refusal_codes())


def check_inventory(cases):
    manifest=RULE_FILE.parents[2]/"cases-v4.tsv"
    with manifest.open() as stream:
        rows=[r for r in csv.DictReader(stream,delimiter="\t") if r["case"].startswith("v4/")]
    expected=[(r["case"],r["family"],r["rule"],r["role"],r["expected"]) for r in rows]
    assert expected==[(c.name,c.family,c.rule,c.member,c.expected) for c in cases],"case freeze mismatch"


def report_cases(inventory):
    groups=defaultdict(Counter)
    for c in inventory: groups[c.family]["pass" if c.expected=="pass" else "refuse"]+=1
    for family, counts in sorted(groups.items()):
        print(f"{family}\t{counts['pass']}\t{counts['refuse']}")
    print("matrix",len(inventory),"must refuse",sum(c.expected!="pass" for c in inventory))

def v4_context(root):
    global MODEL_DIR, CONFIG_SHA
    finder=import_world(root/"src")
    MODEL_DIR=root/"synthetic-model";MODEL_DIR.mkdir()
    write(MODEL_DIR/"config.json",{"max_position_embeddings":40960})
    issue_model_source();endpoint_code()
    stack=ExitStack()
    stack.enter_context(kit_source(finder));stack.enter_context(compact_control())
    stack.enter_context(patch.object(rt,"registered_s6",return_value={"slots":{"S6":1.},"s6_tuning":{}}))
    CONFIG_SHA=hashlib.sha256((rt.ROOT/r1.DEFAULT_RUNTIME_CONFIG).read_bytes()).hexdigest()
    return stack

def main():
    inventory=list(writer_cases())
    assert len({c.name for c in inventory})==len(inventory)
    check_inventory(inventory)
    if os.environ.get("JW_PARTC_INVENTORY")=="only":
        report_cases(inventory);return
    if pattern:=os.environ.get("JW_PARTC_CASE"):
        inventory=[c for c in inventory if re.search(pattern,c.name)]
    if shard:=os.environ.get("JW_PARTC_SHARD"):
        index,count=map(int,shard.split("/"))
        assert 0<=index<count
        inventory=[c for c in inventory if int.from_bytes(hashlib.sha256(c.name.encode()).digest()[:4])%count==index]
    assert inventory or os.environ.get("JW_V4_PROOF")=="1","empty selection"
    with tempfile.TemporaryDirectory(prefix="jw-v4-synthetic-") as tmp:
        root=Path(tmp)
        with v4_context(root):
            base=root/"base"
            assert control(base)==[],"four descriptor bindings required"
            probe=Probe(base)
            assert issued_verdict(probe)["pass"]
            assert probe.candidate(None)
            archive=pc.replay_archived(probe.tree/"native/synthetic-run/part-c",rt.ROOT/r1.DEFAULT_RUNTIME_CONFIG)
            assert archive["verdict"]=="pass" and archive["failing_checks"]==[]
            from joulewise.align.apple.smc_reader import decode
            for _,member in ROLE.items():
                rec=read(base/member/RECEIPT)
                paths=([base/member/"sensors/align_thermal.jsonl"] if member=="idle" else
                       [] if member==P else [base/member/rec["bundle"]/"outputs/align_thermal.jsonl"])
                if member==S: paths.extend((base/S/"recovery/align_thermal.jsonl",base/S/"inventory/inventory_journal.jsonl"))
                for path in paths:
                    for row in rows(path):
                        for key,entry in row.get("values",{}).get("readings",{}).items():
                            if entry.get("error") is None:
                                raw=bytes.fromhex(entry["raw_hex"])
                                assert len(raw)==entry["data_size"] and decode(entry["data_type"],raw,key=key)==entry["value"]
            for status_role,subdir in (("idle","sensors"),(S,"recovery")):
                for entry in rows(base/status_role/subdir/"align_thermal.jsonl"):
                    if entry["kind"]=="reading": assert entry["values"]["status"]=={}
            for k in ROLE.values():
                j=read(base/k/"load_journal.json"); bat=rows(base/k/"battery.jsonl")
                begin,end=work_wall(base/k,k,read(base/k/RECEIPT))
                assert round(bat[0]["epoch_s"]*N)<=begin<=end<=round(bat[-1]["epoch_s"]*N)
                assert len(bat)==2+len(j["cpu_busy_t_s"])//int(CONFIG.get("battery_poll_s",30))
                if k!= "idle": assert_callback_order(base/k,k,read(base/k/RECEIPT))
                print("PROOF",k,len(j["cpu_busy_t_s"]),len(bat),len(j["census"]),flush=True)
            print("PROOF frozen_checks, frozen driver, issued verdict, four bindings, native and archive: pass",flush=True)
            if os.environ.get("JW_V4_PROOF")=="1": return
            totals=Counter()
            for case in inventory:
                try: status=assess_case(base,case)
                except Exception as exc:
                    status="HARNESS_ERROR"
                    print(status,case.name,type(exc).__name__,str(exc),flush=True)
                totals[status]+=1
                print(status,case.name,"expected",case.expected,flush=True)
            print("matrix",len(inventory),dict(totals))
            assert not any(totals[k] for k in ("HARNESS_ERROR","WRONG_VERDICT","FALSE_PASS"))

class FrozenWriterInvariants(unittest.TestCase):
    def test_writer_invariants(self):
        result=subprocess.run([sys.executable,"-IB",str(HERE)],cwd=repo())
        self.assertEqual(result.returncode,0)

if __name__=="__main__":
    main()
