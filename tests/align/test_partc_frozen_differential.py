"""Part C differential acceptance test. All attempts are made inside TemporaryDirectory.

From the candidate checkout run python3.13 -B path/to/test_partc_frozen_differential.py.
The two public commits below must exist in the local Git object database. A full
clone containing both objects works. JW_PARTC_GIT_DIR can select a separate,
read-only object database. JW_PARTC_REPO selects the working tree under test.
JW_PARTC_WORKERS=8 runs isolated synthetic attempts in parallel on macOS/Linux.
JW_PARTC_CASE is an optional regex on printed case IDs. JW_PARTC_INVENTORY=only
prints the pinned source location of each decision in the call-graph closure.
The standard matrix isolates each distinct field of each record shape and also
perturbs entire repeated series. JW_PARTC_ALL_OCCURRENCES=1 additionally isolates
every array index; JW_PARTC_SHARD=i/n partitions either matrix (zero-based).
FALSE_PASS means the public native evaluator accepted a contradictory claim.
REFUSED means it rejected one. OTHER_REFUSAL records a stricter native check.
V3 adds finite branch operands, pre-close raw bytes, and ordered stamp pairs.
The PROVISIONAL predecessor CSV wire cases use the issued D-018 validator.
A decision ID identifies its role, source and exact operand. All added cases use
the same independently materialized issued functions as the synthetic control.
RL-189 adds sixteen native descriptor cases. These run serially against the
single synthetic mirror after all concurrent readers finish. A missing clean
binding is reported separately so the full matrix can still be evaluated.
The evaluator comes from the working tree. The versioned fixture and the R1
oracle are materialized separately from Git. No checkout, fetch or host runtime.
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
            native.status_reader = (lambda: value.get("status",{})) if gated or "status" in value else None
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


def repair_synthetic_control(case, segment, kind, receipt):
    if not (segment / "load_journal.json").is_file():
        write(segment / "load_journal.json", {"cpu_busy_cores": [], "cpu_busy_t_s": [],
                                                "census": [], "errors": [], "exclude_roots": []})
    offset = EPOCH[kind]
    if kind in (P,S):
        # The capture pair is one quiet admission unit in the issued driver.
        # Generate a full per-second load journal using only a fake ps result.
        now = [float(offset)]
        table = NSpace(returncode=0, stdout="101 1 0.0 synthetic-worker\n",stderr="")
        journal = rt.contract.LoadJournal(exclude_roots=(),runner=lambda *a,**kw:table,clock=lambda:now[0])
        journal.snapshot("start")
        for second in range(1801):
            now[0] = float(offset+second)
            journal.sample()
        journal.snapshot("end")
        write(segment / "load_journal.json",{**journal.fields(),"exclude_roots":[],"errors":[]})
    times = iter((float(offset),float(offset+120)))
    answer = NSpace(returncode=0, stdout="Now drawing from 'AC Power'\n -InternalBattery-0 80%; charged;")
    battery = rt.BatteryJournal(lambda argv: answer, lambda: next(times), segment / "battery.jsonl")
    battery.sample()
    battery.sample()
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
        path = segment / "recovery/align_thermal.jsonl"
        rec = rows(path)
        start = rec[0]["started"]["monotonic_ns"]
        sensors = rt.sensors_policy(CONFIG)
        events = [("reading", start+i*N, (38., 38.) if i <= 20 else (35.4, 35.4))
                  for i in range(1, rt.RECOVERY_CAP_S+1)]
        write_rows(path, case.journal(sensors, events, start=start))
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
        repair_synthetic_control(case, segment, kind, receipt)
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
        order = ("idle", P, S, D, X).index(kind)
        manifest.update(started_epoch_s=2000*order, ended_epoch_s=2000*order+1800)
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
        marker = "/PROVISIONAL" if self.predecessor_csv_wire else ""
        return f"{self.role}/v3/{self.family}/{self.file}/{locus}/{self.op}{marker}{suffix}"


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
            ("reading", start+i*N, (38., 38.) if i <= 20 else (35.4, 35.4)) for i in range(1,22)], start=start)
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


EPOCH = {k:2000*i for i,k in enumerate(("idle",P,S,D,X))}


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
    source = textwrap.dedent(inspect.getsource(producer))
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
    once("journal = self.journal(sensors, events)","journal = self.journal(sensors, events,start=member_base_ns)")
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


def compact_control():
    # The same admission structure at ordinary margins, with a smaller token
    # stream and wait, dramatically reduces the cost of the generated suite.
    names = planned_run_ids()
    bank = fixture.bank()
    journal = fixture.SoakLauncherBindingTests.journal
    def journal_with_native_identity(sensors, events, **kwargs):
        records = journal(sensors, events, **kwargs)
        name = "align-" + str(records[0]["started"]["monotonic_ns"])
        for row in records:
            row["session"] = name
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
        stack.enter_context(patch.dict(fixture.STEP, g0_wait_s=12.))
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
            receipt = read((self.base / kind if raw_receipt else segment) / RECEIPT)
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
        if isinstance(m, DecisionCase) and m.predecessor_csv_wire and m.op == "d018-header":
            assert mismatch is None, "issued D-018 positive control failed"
            if not accepted:
                return "WRONG_VERDICT", m.name, "candidate refused the D-018 positive control"
        status = ("FALSE_PASS" if accepted else "REFUSED") if mismatch is not None else (
            "AGREES_PASS" if accepted else "OTHER_REFUSAL")
        return status, m.name, mismatch
    except Exception as error:
        import traceback
        return "HARNESS_ERROR", m.name, "".join(traceback.format_exception(error))


def main():
    global CONFIG, CONFIG_SHA, ORIGINAL, WORKER, MODEL_DIR
    with tempfile.TemporaryDirectory(prefix="jw-synthetic-partc-") as tmp:
        root = Path(tmp)
        finder = import_world(root / "src")
        MODEL_DIR = root / "synthetic-model"
        MODEL_DIR.mkdir()
        write(MODEL_DIR / "config.json", {"max_position_embeddings":40960})
        issue_model_source()
        endpoint_code()
        with kit_source(finder), compact_control(), patch.object(rt, "registered_s6", return_value={
                "slots":{"S6":1.}, "s6_tuning":{}}):
            base = root / "base"
            binding_errors = control(base)
            CONFIG_SHA = hashlib.sha256((rt.ROOT / r1.DEFAULT_RUNTIME_CONFIG).read_bytes()).hexdigest()
            probe, inv = profile_graph(finder, lambda: Probe(base))
            need(issued_verdict(probe)["pass"], "issued Part C clean control")
            print("clean control verdict=pass; descriptor rows",
                  ("FAIL " + ", ".join(binding_errors)) if binding_errors else "PASS (4/4)",
                  ";", len(inv), "decision sites in frozen call-graph closure", flush=True)
            inventory_mode = os.environ.get("JW_PARTC_INVENTORY")
            if inventory_mode in ("1","only"):
                for path, func, line, op in inv:
                    print(f"{path}:{line} {func} {op}")
                if inventory_mode == "only":
                    assert not binding_errors, "clean control lacks the four correct descriptor digests"
                    return
            suite = cases(base)
            if shard := os.environ.get("JW_PARTC_SHARD"):
                index, count = map(int, shard.split("/"))
                assert 0 <= index < count
                suite = (m for m in suite if int.from_bytes(hashlib.sha256(m.name.encode()).digest()[:4]) % count == index)
            if selector := os.environ.get("JW_PARTC_CASE"):
                pattern = re.compile(selector)
                suite = (m for m in suite if pattern.search(m.name))
            if os.environ.get("JW_PARTC_ALL_OCCURRENCES") == "1":
                size = "all selected occurrences"
            else:
                suite = list(suite)
                size = len(suite)
                assert size, "no matching mutations"
            if isinstance(suite,list):
                assert len({case.name for case in suite}) == len(suite), "duplicate case ID"
            print("generated", size, "case IDs", flush=True)
            assert probe.candidate(None), "native replay of clean control"
            ORIGINAL = WORKER = probe
            workers = int(os.environ.get("JW_PARTC_WORKERS", "1"))
            totals = Counter()
            with ExitStack() as stack:
                if workers == 1:
                    answers = map(trial, suite)
                else:
                    import multiprocessing
                    from concurrent.futures import ProcessPoolExecutor
                    pool = stack.enter_context(ProcessPoolExecutor(max_workers=workers, initializer=worker_init,
                                              mp_context=multiprocessing.get_context("fork")))
                    from itertools import islice
                    def bounded():
                        it = iter(suite)
                        while batch := list(islice(it, max(128, workers*32))):
                            legacy = [case for case in batch if not isinstance(case, (DescriptorCase, InputCase))]
                            yield from pool.map(trial, legacy, chunksize=4)
                            # All readers of the shared mirror have completed this
                            # batch before the parent starts a descriptor rewrite.
                            yield from map(trial, (case for case in batch if isinstance(case, (DescriptorCase, InputCase))))
                    answers = bounded()
                for position, (status, name, reason) in enumerate(answers, 1):
                    totals[status] += 1
                    if status in ("FALSE_PASS", "HARNESS_ERROR", "WRONG_VERDICT") or "/descriptor/" in name:
                        print(status, name, reason, flush=True)
                    if position % 100 == 0:
                        print("progress", position, "/", size, dict(totals), flush=True)
            assert sum(totals.values()), "no mutations ran"
            print("matrix", sum(totals.values()), sorted(totals.items()), flush=True)
            assert not totals["HARNESS_ERROR"], "incomplete differential comparison"
            assert not binding_errors, "clean control lacks the four correct descriptor digests"
            assert not totals["WRONG_VERDICT"], "descriptor decision or finding disagrees with RL-189"
            assert not totals["FALSE_PASS"], "native evaluator accepted a frozen contradiction"


class FrozenPartCDifferential(unittest.TestCase):
    def test_frozen_differential(self):
        # Keep Git-backed imports and patched synthetic transports out of the
        # enclosing test process, including prior imports of candidate modules.
        proc = subprocess.run([sys.executable, "-IB", str(HERE)], cwd=repo())
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    main()
