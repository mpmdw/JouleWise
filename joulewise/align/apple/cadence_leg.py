"""Campaign leg runtime: one type-A leg of the conditionless calibration campaign (RL-149 section 2.2).

    python -B scripts/cadence_leg_runtime.py --config configs/align/v4/r1_runtime.json \
        --leg-spec SPEC.json --r1-kind cadence-leg --output DIR --soak-reference FILE

One invocation runs one leg: its own G0 under the R1 G0 timeout (1,200 s), the
band recipe's quiet (``quiet_s``), then one turn of the step task with a prompt
of ``prefill_chars`` characters, a decode cap of ``decode_tokens`` and the leg's
seed. It is built on the existing step leg (RL-149 section 5 item 6): the
``StepTask``/``step_spec`` member of ``r1_runtime``, the A-B-A leg's shape (a
native G0 capture, the member deadman re-armed after G0), the same production
backend, journals, terminal custody and signal handling (``r1_runtime.main``).

**No energy.** The leg never calls ``decode_energy``, ``t_decline`` or any
powermetrics or meter reader, and its result is refused if any key names
energy, power, a slot or a transcript. Energy stays in the member bundle's
custody, read only by frozen fit code at a look (RL-149 section 2.6).

**Condition-13 bytes unchanged.** ``r1_runtime.py`` and the R1 driver are
untouched. ``CadenceLegSegment`` subclasses ``r1_runtime.Segment`` and ``main``
has ``r1_runtime.main`` construct it (the class ``main`` resolves by name is
swapped for the life of this process only).

**The episode spec's condition field.** ``step_spec`` sets the workload's
mandatory ``condition``/``warmup_condition`` to the neutral value the workload
accepts (``workload.py`` refuses anything else), so that word is inside each
member bundle's config. The step task ignores it. Nothing this module returns,
and nothing the span driver projects for the desk, carries it: the result and
every projection are scanned with the kit's own condition/slot value rule.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from joulewise.align.apple import r1_runtime as rt
from joulewise.cadence import legs as legsmod

LEG_KIND = legsmod.LEG_KIND
# The fields every leg result carries beside the quiet journal fields
# (r1_runtime_contract.QUIET_FIELDS) the driver's load verdict reads.
RESULT_FIELDS = ("leg_id", "leg_status", "bundle", "member_status", "g0_outcome", "g0_released", "g0_wait_s",
                 "g0_timeout_s", "quiet_s", "prefill_chars", "prefill_tokens", "decode_cap", "decode_tokens",
                 "decode_cap_reached", "os_level_max", "pm_nominal", "episode_flags", "incomplete_reasons",
                 "ac_powermode")
LEG_STATUSES = ("complete", "g0_unreleased", "incomplete")


def _os_status(rows, start_ns, end_ns):
    """Max OS thermal level and whether every observed PM state was Nominal, over [start, end]."""
    levels, states = [], []
    for row in rows:
        if start_ns is not None and row["monotonic_ns"] < start_ns:
            continue
        if end_ns is not None and row["monotonic_ns"] > end_ns:
            continue
        status = row.get("status") or {}
        if type(status.get("os_level")) is int:
            levels.append(status["os_level"])
        if isinstance(status.get("pm_state"), str):
            states.append(status["pm_state"])
    return (max(levels) if levels else None), (all(s == "Nominal" for s in states) if states else None)


class CadenceLegSegment(rt.Segment):
    """The ``cadence-leg`` kind. ``leg`` is the validated leg spec (set by ``main``)."""

    leg = None

    @property
    def g0_cap_s(self):
        """Every campaign leg arms the R1 G0 timeout (runtime config g0_timeout_s)."""
        return rt.g0_timeout_s(self.config)

    def dispatch(self):
        if self.kind != LEG_KIND:
            raise rt.Refused(f"the campaign leg runtime runs --r1-kind {LEG_KIND} only, not {self.kind!r}")
        return self.k_cadence_leg()

    def run(self):
        if self.leg is None:
            raise rt.Refused("cadence-leg needs --leg-spec")
        if self.soak is None:
            raise rt.Refused("cadence-leg needs --soak-reference (the span's fresh soak)")
        self.sensors  # refuse a PENDING R0 sensor selection before any host command
        self.start_journals()
        fields = self.dispatch()
        self.stop_journals()
        result = {"schema": rt.RESULT_SCHEMA, "kind": self.kind, "backend": self.backend.name,
                  "config_sha256": self.config_sha256, **fields, **self.load.fields(),
                  "load_journal_errors": self.load_errors, "battery": self.battery.summary()}
        missing = [k for k in (*RESULT_FIELDS, *rt.contract.QUIET_FIELDS) if k not in result]
        if missing:
            raise rt.RuntimeFailure(f"{self.kind}: leg result misses fields {missing}")
        # Every key at any depth is scanned for energy, power, slot or transcript names; the leg's
        # own fields are also scanned for a condition label (the census and battery journals hold
        # host text the leg did not write, so their values are not).
        legsmod.guard_projection(result, "leg result", values=False)
        legsmod.guard_projection({k: result[k] for k in RESULT_FIELDS}, "leg result")
        return result

    def k_cadence_leg(self):
        leg = self.leg
        template, tspec = self.template("d_spam")
        rt.require_effort(tspec, "d_spam")
        policy = rt.gate_policy(self.sensors, self.bands(), turn_cap_s=300, chunk_tokens=256,
                                heavy=False, per_turn=False, g0_cap_s=self.g0_cap_s)
        deadman_s = self.config["step"]["deadman_s"]
        step = {"prefill_chars": leg["prefill_chars"], "decode_tokens": leg["decode_tokens"], "seed": leg["seed"]}
        spec = rt.step_spec(tspec, step, policy, deadman_s=deadman_s)
        config = rt.member_config(template, spec, run_id=f"cadence-{leg['campaign_id']}-{leg['leg_id']}",
                                  kind=self.kind)
        config["hardware_target"]["notes"] = ("Conditionless calibration campaign leg (RL-149 section 2; "
                                              "non-claim; no v4 member).")
        config["run_metadata"]["tags"] = [*config["run_metadata"]["tags"], "cadence-campaign",
                                          f"cadence-leg={leg['leg_id']}"]
        reference = {}
        hook = self.reference_hook(reference, quiet_s=leg["quiet_s"], rearm_s=deadman_s, capture=True)
        member = self.run_member(config, hook)
        ep = member.ep
        thermal = ep.hardware.get("thermal") or {}
        g0 = next((r for r in thermal.get("intervals", []) if r["kind"] == "G0"), None)
        incomplete = rt.incomplete_member_reasons(member)
        base = {"leg_id": leg["leg_id"], "bundle": str(member.bundle.relative_to(self.out)),
                "member_status": member.status, "g0_outcome": g0["outcome"] if g0 else None,
                "g0_released": bool(g0) and g0["outcome"] == "released",
                **rt.g0_wait_fields(g0, self.armed_g0_cap_s), "quiet_s": leg["quiet_s"],
                "prefill_chars": leg["prefill_chars"], "decode_cap": leg["decode_tokens"],
                "episode_flags": list(ep.flags), "incomplete_reasons": incomplete,
                "ac_powermode": ep.hardware.get("ac_powermode"),
                "quiet_spans_ns": [list(span) for span in self.quiet_spans]}
        rows = rt.journal_rows(member.bundle / "outputs" / "align_thermal.jsonl")
        if not ep.turns:
            level, nominal = _os_status(rows, None, None)
            status = "g0_unreleased" if g0 is not None and rt.only_g0_unreleased(incomplete, g0["outcome"]) \
                else "incomplete"
            return {**base, "leg_status": status, "prefill_tokens": None, "decode_tokens": None,
                    "decode_cap_reached": False, "os_level_max": level, "pm_nominal": nominal}
        turn = ep.turns[0]
        level, nominal = _os_status(rows, turn.start_ns, turn.end_ns)
        decode = sum(t.decode_tokens for t in ep.turns)
        return {**base, "leg_status": "incomplete" if incomplete else "complete",
                "prefill_tokens": turn.prefill_tokens, "decode_tokens": decode,
                "decode_cap_reached": decode >= leg["decode_tokens"], "os_level_max": level,
                "pm_nominal": nominal, "turn_start_ns": turn.start_ns, "turn_end_ns": turn.end_ns,
                "first_token_ns": turn.first_token_ns}


def _split_leg_spec(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--leg-spec", type=Path, required=True)
    known, rest = parser.parse_known_args(argv)
    return known.leg_spec, rest


def load_leg_spec(path):
    return legsmod.validate_leg_spec(json.loads(Path(path).read_text()))


def main(argv=None, *, backend_factory=None, stdout=None):
    """``r1_runtime.main`` with the leg segment. A bad leg spec refuses (exit 2) before any work."""
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        spec_path, rest = _split_leg_spec(argv)
        leg = load_leg_spec(spec_path)
    except (SystemExit, OSError, ValueError) as error:
        print(f"cadence_leg_runtime: refused: {error}", file=sys.stderr)
        return rt.EXIT_REFUSED
    bound = type("BoundCadenceLegSegment", (CadenceLegSegment,), {"leg": leg})
    original = rt.Segment
    rt.Segment = bound
    try:
        return rt.main(rest, backend_factory=backend_factory, stdout=stdout)
    finally:
        rt.Segment = original
