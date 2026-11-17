"""Scripted conditionless control runtime; no rail or energy reader.

Each member retains the existing sampler, model, G0 and custody machinery. A process-local
endpoint executes the kit's physical calls. The episode's one logged envelope counts the visible
calls; ``script-work.json`` records every physical call (including deliberately unlogged work),
CPU interval, gap and sampled recovery using the same monotonic clock. It contains no model text.
It is sealed ground truth, not a desk projection. No W1/R1 module on disk is changed.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import time

from joulewise.align.apple import cadence_leg, r1_runtime as rt
from joulewise.align.apple.sampler import monotonic_ns
from joulewise.cadence import ctl, legs

AUDIT_NAME = "script-work.json"


def cpu_burn(clock, seconds, *, synthetic):
    """One thread, no worker process. Synthetic time advances without burning a host core."""
    if synthetic:
        clock.sleep(seconds)
        return
    until = time.monotonic() + seconds
    value = 1
    while time.monotonic() < until:
        value = (value * 1664525 + 1013904223) & 0xffffffff


def endpoint_class(base, script, audit, *, synthetic):
    class ScriptEndpoint(base):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.hidden_endpoint = base(*args, **kwargs)
            self.script_used = False

        def stamp(self):
            return monotonic_ns(self.clock.stamp())

        def interval(self, kind, seconds):
            start = self.stamp()
            epoch = self.clock.stamp().epoch_s
            if kind == "cpu":
                cpu_burn(self.clock, seconds, synthetic=synthetic)
            else:
                self.clock.sleep(seconds)
            audit["steps"].append({"kind": kind, "started_ns": start, "ended_ns": self.stamp(),
                                   "started_epoch_s": epoch, "ended_epoch_s": self.clock.stamp().epoch_s,
                                   "requested_s": seconds})

        def physical_call(self, endpoint, messages, kwargs, tokens, *, logged):
            start = self.stamp()
            result = base.chat(endpoint, messages, **{**kwargs, "max_tokens": tokens})
            audit["steps"].append({"kind": "turn" if logged else "hidden", "started_ns": start,
                                   "ended_ns": self.stamp(), "requested_tokens": tokens,
                                   "actual_tokens": result.completion_tokens,
                                   "first_token_ns": result.first_token_ns})
            if result.completion_tokens != tokens:
                raise rt.RuntimeFailure("scripted call did not reach its exact token dose")
            if result.tool_calls:
                raise rt.RuntimeFailure("scripted step unexpectedly returned a tool call")
            return result

        def chat(self, messages, **kwargs):
            if self.script_used:
                raise rt.RuntimeFailure("one control script per member")
            self.script_used = True
            if script["hidden_tokens"]:
                self.physical_call(self.hidden_endpoint, messages, kwargs, script["hidden_tokens"], logged=False)
            visible = []
            for i, tokens in enumerate(script["turn_tokens"]):
                if i:
                    if script["cpu_s"]:
                        self.interval("cpu", script["cpu_s"])
                    if script["gap_s"]:
                        self.interval("gap", script["gap_s"])
                # Fresh identical prompts: one scripted call is one physical turn, no growing history.
                visible.append(self.physical_call(self, messages, kwargs, tokens, logged=True))
            # The model and the member's rail sampler are still alive here. No new session is opened.
            self.interval("recovery", script["recovery_s"])
            audit["complete"] = True
            first, last = visible[0], visible[-1]
            return replace(last, start_ns=first.start_ns, first_token_ns=first.first_token_ns,
                           prompt_tokens=sum(r.prompt_tokens for r in visible),
                           cached_prompt_tokens=sum(r.cached_prompt_tokens for r in visible),
                           completion_tokens=sum(r.completion_tokens for r in visible),
                           reasoning_tokens=sum(r.reasoning_tokens for r in visible))
    return ScriptEndpoint


@contextmanager
def scripted_endpoint(script, audit, *, synthetic):
    # A leg has its own child interpreter. Like cadence_leg's Segment binding, this binding ends
    # even on refusal/interrupt and never modifies a shared module's frozen disk bytes.
    from joulewise.align.apple import workload
    original = workload.MlxEndpoint
    workload.MlxEndpoint = endpoint_class(original, script, audit, synthetic=synthetic)
    try:
        yield
    finally:
        workload.MlxEndpoint = original


class CtlSegment(cadence_leg.CadenceLegSegment):
    def k_cadence_leg(self):
        # The inherited turn deadman covers the entire script, including sampled recovery.
        seconds, calls = ctl.script_seconds(self.leg["script"], legs.TIME_MODEL)
        post_g0 = math.ceil(seconds + calls*self.leg["prefill_tokens"]*legs.TIME_MODEL["prefill_s_per_token"] + 60)
        self.config = {**self.config, "step": {**self.config["step"], "deadman_s": post_g0}}
        result = super().k_cadence_leg()
        raw = (self.out / AUDIT_NAME).read_bytes()
        audit = json.loads(raw)
        if result["g0_released"] and not audit["complete"]:
            raise rt.RuntimeFailure("incomplete control script")
        return {**result, "script_complete": audit["complete"],
                "script_record_sha256": hashlib.sha256(raw).hexdigest()}

    def run_member(self, config_map, hook=None):
        audit = {"schema": "joulewise.cadence_script_work.v1", "leg_id": self.leg["leg_id"],
                 "script": self.leg["script"], "complete": False, "steps": []}
        try:
            with scripted_endpoint(self.leg["script"], audit, synthetic=self.backend.name != "production"):
                return super().run_member(config_map, hook)
        finally:
            (self.out / AUDIT_NAME).write_text(json.dumps(audit, indent=1, sort_keys=True) + "\n")


def main(argv=None, *, backend_factory=None, stdout=None):
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        path, span_source, rest = cadence_leg._split_leg_spec(argv)
        leg = cadence_leg.load_leg_spec(path)
        if leg["schema"] != ctl.SPEC_SCHEMA:
            raise ValueError("cadence-ctl-v1 needs a ctl leg spec")
    except (SystemExit, OSError, ValueError) as error:
        print(f"cadence_ctl: refused: {error}", file=sys.stderr)
        return rt.EXIT_REFUSED
    bound = type("BoundCtlSegment", (CtlSegment,), {"leg": leg, "span_source": span_source})
    original = rt.Segment
    rt.Segment = bound
    try:
        return rt.main(rest, backend_factory=backend_factory, stdout=stdout)
    finally:
        rt.Segment = original
