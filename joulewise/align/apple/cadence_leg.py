"""Campaign leg runtime: one type-A leg of the conditionless calibration campaign (RL-149 section 2.2).

    python -B scripts/cadence_leg_runtime.py --config configs/align/v4/r1_runtime.json \
        --leg-spec SPEC.json --r1-kind cadence-leg --output DIR --soak-reference FILE \
        [--span-reference FIRST_LEG_ATTEMPT_DIR]

One invocation runs one leg: its G0 under the R1 G0 timeout (1,200 s), the
band recipe's quiet (``quiet_s``), then one turn of the step task with a prompt
of ``prefill_chars`` characters, a decode cap of ``decode_tokens`` and the leg's
seed.

**The G0 reference** (RL-150 R1; design doc section 14.5). A v1 leg spec, and a
``span`` leg whose role is ``capture``, judge the G0 against the leg's own capture
(the 60 s median before warm-up entry). A ``span`` leg whose role is ``consume``
judges it against the span's reference: the capture of the span's first leg,
read from that leg's accepted attempt (``--span-reference DIR``) through the same
``consume`` path an R1 consumer takes R_D by (``Segment.consume_d_reference``:
W1's verifier, ``thermal_gates.load_window_reference``, with the source config
bound by the source runtime's terminal custody). ``thermal_gates.py`` and
``r1_runtime.py`` are unchanged. A consumer whose reference is missing, unbound or
unobserved refuses before any work; it never falls back to its own capture.

It is built on the existing step leg (RL-149 section 5 item 6): the
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
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

from joulewise.align.apple import r1_runtime as rt
from joulewise.cadence import legs as legsmod

LEG_KIND = legsmod.LEG_KIND
# The fields every leg result carries beside the quiet journal fields
# (r1_runtime_contract.QUIET_FIELDS) the driver's load verdict reads.
RESULT_FIELDS = ("leg_id", "leg_status", "bundle", "member_status", "g0_outcome", "g0_released", "g0_wait_s",
                 "g0_timeout_s", "quiet_s", "prefill_chars", "prefill_tokens", "decode_cap", "decode_tokens",
                 "decode_cap_reached", "os_level_max", "pm_nominal", "episode_flags", "incomplete_reasons",
                 "ac_powermode", "g0_shape", "g0_role", "g0_reference_source", "g0_reference_record_sha256")
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
    span_source = None      # --span-reference: the span's first leg's accepted attempt dir (consumers only)
    span_custody = None     # the verified reference's custody (record_sha256, source run id, journal sha256)

    @property
    def g0_role(self):
        return self.leg.get("g0_role", "capture")

    @property
    def g0_cap_s(self):
        """Every campaign leg arms the R1 G0 timeout (runtime config g0_timeout_s)."""
        return rt.g0_timeout_s(self.config)

    def span_reference(self, session=None):
        """The span's reference (RL-150 R1 part 2): the first leg's capture, read and verified exactly as
        ``Segment.consume_d_reference`` reads step-D's R_D, with the span's first leg in step-D's place."""
        from joulewise.align.apple.thermal_gates import WindowReferenceRefused, load_window_reference
        if self.span_source is None:
            raise rt.Refused("a span-reference consumer needs --span-reference (the span's first leg's attempt)")
        source_dir = Path(self.span_source)
        # The source is a leg of this span: <span>/legs/<first>/runtime beside <span>/legs/<this>/runtime
        # (#788 F8: a hand-run leg must not consume another span's capture).
        if source_dir.name != "runtime" or source_dir.resolve().parent.parent != self.out.resolve().parent.parent:
            raise rt.Refused(f"span reference {source_dir}: not a leg attempt of this span ({self.out.parent.parent})")
        try:
            raw = (source_dir / rt.RESULT_NAME).read_bytes()
            value = json.loads(raw)
            custody = json.loads((source_dir / rt.CUSTODY_NAME).read_bytes())
        except (OSError, ValueError) as error:
            raise rt.Refused(f"span reference {source_dir}: no readable result and custody ({error})") from error
        if not (isinstance(value, dict) and isinstance(custody, dict) and value.get("kind") == LEG_KIND
                and custody.get("schema") == rt.CUSTODY_SCHEMA and custody.get("status") == "complete"
                and (custody.get("files") or {}).get(rt.RESULT_NAME) == hashlib.sha256(raw).hexdigest()):
            raise rt.Refused(f"span reference {source_dir}: not a cadence-leg result bound by complete runtime custody")
        if value.get("g0_role", "capture") != "capture" or not isinstance(value.get("bundle"), str):
            raise rt.Refused(f"span reference {source_dir}: the source leg did not capture its own reference")
        bundle = Path(value["bundle"])
        source = source_dir / bundle
        expected_config = (custody.get("files") or {}).get((bundle / "config.json").as_posix())
        if not expected_config:
            raise rt.Refused("span reference: the source custody does not bind its config")
        policy = self.observe_policy()
        policy["window_reference"] = {"role": "consume", "source_run_id": source.name,
                                      "source_config_sha256": expected_config}
        context = SimpleNamespace(bundle_path=source.parent / "cadence-span-reference-consumer",
                                  run_id="cadence-span-reference-consumer")
        try:
            reference, verified = load_window_reference(policy, context)
        except WindowReferenceRefused as error:
            raise rt.Refused(f"span reference {source.name}: {error}") from error
        self.span_custody = verified
        if session is not None:
            session.reference, session.custody = reference, verified
        return reference

    def consume_d_reference(self, session=None):
        """``reference_hook(capture=False)`` calls this: for a campaign consumer it is the span's reference."""
        return self.span_reference(session)

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
        if self.g0_role == "consume":
            self.span_reference()   # verify the span's reference before any work (refuses on any defect)
        elif self.span_source is not None:
            raise rt.Refused("--span-reference is for a span-reference consumer (g0_role consume) only")
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
        hook = self.reference_hook(reference, quiet_s=leg["quiet_s"], rearm_s=deadman_s,
                                   capture=self.g0_role != "consume")
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
                "quiet_spans_ns": [list(span) for span in self.quiet_spans],
                "g0_shape": leg.get("g0_shape", "own"), "g0_role": self.g0_role,
                "g0_reference_source": reference.get("source_member"),
                "g0_reference_record_sha256": (self.span_custody or {}).get("record_sha256")
                if self.g0_role == "consume" else None}
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
    parser.add_argument("--span-reference", type=Path)
    known, rest = parser.parse_known_args(argv)
    return known.leg_spec, known.span_reference, rest


def load_leg_spec(path):
    return legsmod.validate_leg_spec(json.loads(Path(path).read_text()))


def main(argv=None, *, backend_factory=None, stdout=None):
    """``r1_runtime.main`` with the leg segment. A bad leg spec refuses (exit 2) before any work."""
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        spec_path, span_source, rest = _split_leg_spec(argv)
        leg = load_leg_spec(spec_path)
    except (SystemExit, OSError, ValueError) as error:
        print(f"cadence_leg_runtime: refused: {error}", file=sys.stderr)
        return rt.EXIT_REFUSED
    bound = type("BoundCadenceLegSegment", (CadenceLegSegment,), {"leg": leg, "span_source": span_source})
    original = rt.Segment
    rt.Segment = bound
    try:
        return rt.main(rest, backend_factory=backend_factory, stdout=stdout)
    finally:
        rt.Segment = original
