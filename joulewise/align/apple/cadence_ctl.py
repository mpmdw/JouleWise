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
import time

from joulewise.align.apple import cadence_leg, r1_runtime as rt
from joulewise.align.apple.sampler import monotonic_ns
from joulewise.cadence import ctl, legs

AUDIT_NAME = ctl.WORK_NAME


def cpu_burn(clock, seconds, *, synthetic):
    """One thread, no worker process. Synthetic time advances without burning a host core."""
    if synthetic:
        clock.sleep(seconds)
        return
    until = time.thread_time_ns() + ctl.duration_ns(seconds)
    value = 1
    while time.thread_time_ns() < until:
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
            started = self.clock.stamp()
            cpu_start = time.thread_time_ns() if kind == "cpu" and not synthetic else None
            row = {"kind": kind, "started_ns": monotonic_ns(started), "started_epoch_s": started.epoch_s,
                   "requested_s": seconds, "complete": False}
            audit["steps"].append(row)
            try:
                if kind == "cpu":
                    cpu_burn(self.clock, seconds, synthetic=synthetic)
                else:
                    self.clock.sleep(seconds)
            finally:
                ended = self.clock.stamp()
                row.update(ended_ns=monotonic_ns(ended), ended_epoch_s=ended.epoch_s)
                if kind == "cpu":
                    row["thread_cpu_ns"] = (time.thread_time_ns() - cpu_start if cpu_start is not None
                                            else row["ended_ns"] - row["started_ns"])
            row["complete"] = ctl.completed_step(row, kind, seconds)

        def physical_call(self, endpoint, messages, kwargs, tokens, *, logged):
            row = {"kind": "turn" if logged else "hidden", "started_ns": self.stamp(),
                   "requested_tokens": tokens, "actual_tokens": None, "complete": False}
            audit["steps"].append(row)
            try:
                result = base.chat(endpoint, messages, **{**kwargs, "max_tokens": tokens})
                row.update(actual_tokens=result.completion_tokens, first_token_ns=result.first_token_ns,
                           context_tokens=result.prompt_tokens)
            finally:
                row["ended_ns"] = self.stamp()
            if result.tool_calls:
                raise rt.RuntimeFailure("scripted step unexpectedly returned a tool call")
            row["complete"] = result.completion_tokens == tokens
            return result

        def chat(self, messages, **kwargs):
            if self.script_used:
                raise rt.RuntimeFailure("one control script per member")
            self.script_used = True
            visible = []
            for kind, dose in ctl.script_steps(script):
                if kind == "hidden":
                    self.physical_call(self.hidden_endpoint, messages, kwargs, dose, logged=False)
                elif kind == "turn":
                    if script["kind"] == "split":
                        # The native sampler derives its seed from the endpoint turn.
                        # Each split call starts at the plain member's logical turn zero.
                        self._turn = 0
                    visible.append(self.physical_call(self, messages, kwargs, dose, logged=True))
                else:
                    self.interval(kind, dose)
            audit["complete"] = ctl.work_complete(audit["steps"], script)
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
        post_g0 = ctl.post_g0_budget_s(self.leg, legs.TIME_MODEL)
        self.config = {**self.config, "step": {**self.config["step"], "deadman_s": post_g0}}
        result = super().k_cadence_leg()
        raw = (self.out / AUDIT_NAME).read_bytes()
        audit = json.loads(raw)
        if result["g0_released"] and not audit["complete"]:
            result.update(leg_status="incomplete", decode_cap_reached=False,
                          incomplete_reasons=[*result["incomplete_reasons"], "script_dose_short"])
        return {**result, "script_complete": audit["complete"],
                "script_record_sha256": hashlib.sha256(raw).hexdigest()}

    def run_member(self, config_map, hook=None):
        audit = {"schema": ctl.WORK_SCHEMA, "leg_id": self.leg["leg_id"],
                 "leg_spec_sha256": ctl.leg_spec_sha256(self.leg),
                 "script": self.leg["script"], "complete": False, "steps": []}
        try:
            with scripted_endpoint(self.leg["script"], audit, synthetic=self.backend.name != "production"):
                return super().run_member(config_map, hook)
        finally:
            (self.out / AUDIT_NAME).write_text(json.dumps(audit, indent=1, sort_keys=True) + "\n")


def main(argv=None, *, backend_factory=None, stdout=None):
    import argparse
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        path, span_source, rest = cadence_leg._split_leg_spec(argv)
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--leg-spec-sha256", required=True)
        proof, rest = parser.parse_known_args(rest)
        leg = cadence_leg.load_leg_spec(path)
        if leg["schema"] != ctl.SPEC_SCHEMA:
            raise ValueError("cadence-ctl-v1 needs a ctl leg spec")
        if ctl.leg_spec_sha256(leg) != proof.leg_spec_sha256:
            raise ValueError("ctl leg spec differs from the span plan")
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
