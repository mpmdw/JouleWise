"""Frozen synthetic supplement for PR #853. Run from the seat with python3.13 -B.

The adjacent checkout supplies the builder. Only the absent align package comes
from the pinned RL-176 source overlay. No campaign, path to data, or host runner.
Optional CTL_TEST_ADAPTER names a test-only translator for release operations
missing on the draft. Its observable interfaces are documented in SPEC-DELTA.
"""

import dataclasses
import hashlib
import importlib
import json
import os
import sys
import unittest
from copy import deepcopy
from dataclasses import fields, replace
from functools import lru_cache
from pathlib import Path
from unittest.mock import Mock

SEAT = Path(__file__).resolve().parent
if (SEAT / "checkout").is_dir():
    sys.path.insert(0, str(SEAT / "checkout"))
import joulewise

if (SEAT / "tmp/kernel/joulewise/align").is_dir():
    joulewise.__path__.append(str(SEAT / "tmp/kernel/joulewise"))

from joulewise.align import records as rec
from joulewise.align.attribution import EnergyEstimate, EpisodeAttribution, SegmentEnergy
from joulewise.cadence_looks import controls_analysis as analysis, controls_print as controls
from tests.contracts.cadence_looks import synthetic_acceptance as v1
from tests.contracts.cadence_looks import test_controls_analysis as fixture
from tests.contracts.cadence_looks.ctl_print_adapter import check_fixture

NS = 10**9
TYPES = dict(zip(v1.IDS, v1.KINDS, strict=True))
BURNS = {"L003": 30, "L004": 90, "L010": 10}
# Toy delivered counts for hand arithmetic. These are not kit design choices.
DOSES = dict(zip(("L002", "L005", "L008", "L009", "L011", "L012"), (12, 4, 8, 12, 8, 4)))
CHANNELS = ("cpu_rail", "gpu_rail", "rail_sum", "dc_in")
KERNEL = analysis.PhaseKernel.frozen()


def SHA(b):
    return hashlib.sha256(b).hexdigest()


def blob(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def packed(x):
    return json.loads(rec.to_json(x))


def script(leg, **changes):
    d = json.loads(leg.work_bytes)
    d.update(changes)
    b = blob(d)
    return replace(leg, work_bytes=b, work_sha256=SHA(b))


def marked_turn(leg, typ=None, **updates):
    old = leg.episode.turns[0]
    if typ:
        old = typ(**vars(old))
    return replace(leg, episode=replace(leg.episode, turns=(replace(old, **updates),)))


@lru_cache(None)
def make_leg(key, *, watts=3, shift=0, short=False, incomplete=False, hidden_peak=None):
    """Invent a complete physical record with the pinned runner's field inventory."""
    kind = TYPES[key]
    pos = 1 + shift
    rows = []
    caps = iter(v1.CAPS[kind])
    sequence = {
        "cpu": ("turn", "cpu", "turn"),
        "split": ("turn", "gap", "turn", "gap", "turn"),
        "hidden": ("hidden", "turn"),
        "extra-turn": ("turn", "turn"),
        "plain": ("turn",),
    }
    for role in (*sequence[kind], "recovery"):
        if role in ("turn", "hidden"):
            count = next(caps) if role == "turn" else DOSES[key]
            length = 2 if role == "turn" else 4
            first = pos + length // 2
            delivered = count - int(short and role == "hidden")
            row = dict(
                kind=role,
                started_ns=pos * NS,
                ended_ns=(pos + length) * NS,
                first_token_ns=first * NS,
                requested_tokens=count,
                actual_tokens=delivered,
                context_tokens=2000,
                cached_prompt_tokens=17,
                complete=delivered == count,
            )
        else:
            length = {"gap": 7, "cpu": BURNS.get(key), "recovery": 120}[role]
            row = dict(
                kind=role,
                started_ns=pos * NS,
                ended_ns=(pos + length) * NS,
                requested_s=length,
                complete=not (incomplete and role == "recovery"),
            )
            row.update(started_epoch_s=123456 + pos, ended_epoch_s=123456 + pos + length)
            if role == "cpu":
                row["thread_cpu_ns"] = length * NS
        rows.append(row)
        pos += length
    visible = [r for r in rows if r["kind"] == "turn"]
    turn = rec.Turn(
        index=0,
        start_ns=visible[0]["started_ns"],
        first_token_ns=visible[0]["first_token_ns"],
        end_ns=visible[-1]["ended_ns"],
        context_tokens=31,
        prefill_tokens=sum(r["context_tokens"] for r in visible) - 31,
        decode_tokens=sum(r["actual_tokens"] for r in visible),
    )
    # Single interior sample raised by h W above background contributes h J
    # under the trapezoid. The two triangles fall on opposite sides of first-token.
    pulse = {}
    if kind == "hidden":
        peak = DOSES[key] if hidden_peak is None else hidden_peak
        pulse = {shift + 2: watts + 2, shift + 4: watts + peak}
    ticks = tuple(t * NS for t in range(pos + 1))
    values = tuple(pulse.get(t, watts) for t in range(pos + 1))
    channel_pairs = (
        ("powermetrics", "cpu_power"),
        ("powermetrics", "gpu_power"),
        ("powermetrics", "package"),
        ("wall_meter", "dc_in"),
    )
    traces = tuple(rec.PowerTrace(src, ch, "toy", ticks, values, "W", NS) for src, ch in channel_pairs)
    episode = rec.Episode(
        "toy-" + key,
        "controls",
        "benign",
        "toy",
        "fake",
        42,
        "toy",
        0,
        pos * NS,
        (turn,),
        power_traces=traces,
    )
    payload = blob(dict(schema="joulewise.cadence_script_work.v1", leg_id=key, steps=rows))
    leg = analysis.LegInput(key, kind, True, True, episode, payload, SHA(payload))
    return script(
        leg,
        script=dict(
            kind=kind,
            turn_tokens=list(v1.CAPS[kind]),
            hidden_tokens=DOSES.get(key, 0),
            cpu_s=BURNS.get(key, 0),
            gap_s=7 if kind == "split" else 0,
            recovery_s=120,
        ),
        leg_spec_sha256=SHA(key.encode()),
        complete=all(r["complete"] for r in rows),
    )


def roster(*selected):
    loaded = {x.leg_id: x for x in selected}
    return [loaded.get(k, analysis.LegInput(k, v, False, False)) for k, v in TYPES.items()]


def pri(positions, kernel=KERNEL, pooled=None):
    if pooled is None:
        member = ("toy", "a" * 64, "L001")
        pooled = analysis.pool_hold_windows(
            [
                analysis.HoldWindow(member, ch, w, 3, 0.5)
                for ch in CHANNELS
                if ch != "cpu_rail"
                for w in (10, 40, 128)
            ],
            {member},
        )
    return packed(
        analysis.print_controls(
            positions,
            kernel=kernel,
            gap_limits_ns=dict.fromkeys(CHANNELS, 2 * NS),
            pooled=pooled,
            instrument_manifest_sha256=SHA(b"synthetic instrument"),
        )
    )


def one(leg, **kwargs):
    return pri(roster(leg), **kwargs)["legs"][v1.IDS.index(leg.leg_id)]


def instrumented():
    phases = Mock(wraps=KERNEL.phases)
    phases.TIMING_EDGE_J = KERNEL.phases.TIMING_EDGE_J
    return analysis.PhaseKernel(phases, Mock(wraps=KERNEL.attribute_episode), KERNEL.trace_energy)


def closed_envelope(tc, leg, row):
    physical = [r for r in json.loads(leg.work_bytes)["steps"] if r["kind"] == "turn"]
    expected = {
        "prompt_tokens": sum(r["context_tokens"] for r in physical),
        "decode_tokens": sum(r["actual_tokens"] for r in physical),
    }
    tc.assertEqual(blob(row["envelope"]), blob(expected), "visible sums only, exact JSON integers")


def leaves(x, prefix=()):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, (*prefix, k))
    elif isinstance(x, (list, tuple)):
        for i, v in enumerate(x):
            yield from leaves(v, (*prefix, i))
    else:
        yield prefix, x


def paths(doc, needle):
    # Include key names as well as scalar leaves; bool and number are distinct.
    def scan(x, p):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(needle, str) and needle in k:
                    yield (*p, k)
                yield from scan(v, (*p, k))
        elif isinstance(x, (tuple, list)):
            for i, v in enumerate(x):
                yield from scan(v, (*p, i))
        elif (
            (type(needle) is str and type(x) is str and needle in x)
            or (type(needle) in (int, float) and type(x) in (int, float) and x == needle)
            or (type(needle) in (int, float) and type(x) is str and str(needle) == x)
        ):
            yield p

    return set(scan(doc, ()))


def draft_design(inputs, append, issue):
    """Observe the only design operation at cace94b5, including its absent append."""
    try:
        result = analysis.read_parameters(**inputs)
    except ValueError as exc:
        if str(exc) not in {
            "missing_token_floor",
            "missing_instrument_timing",
            "dose_requires_ruling",
            "prefill_requires_ruling",
        }:
            raise
        return
    issue(result)


def bridge(name):
    module = os.environ.get("CTL_TEST_ADAPTER", "tests.contracts.cadence_looks.ctl_v2_adapter")
    try:
        adapter = importlib.import_module(module)
    except ModuleNotFoundError as e:
        if e.name != module:
            raise
        if name == "apply_design" and "CTL_TEST_ADAPTER" not in os.environ:
            return draft_design
        raise AssertionError(f"builder has no synthetic binding for {name}") from None
    if not hasattr(adapter, name):
        raise AssertionError(f"builder has no synthetic binding for {name}")
    return getattr(adapter, name)


class Suite(unittest.TestCase):
    maxDiff = 700


def case(id, fn, *args):
    name = "test_" + id
    if hasattr(Suite, name):
        raise RuntimeError("duplicate case " + id)
    setattr(Suite, name, lambda self: fn(self, *args))


def reject_leg(tc, leg, expected=None):
    k = instrumented()
    row = one(leg, kernel=k)
    tc.assertEqual(row["disposition"], "not_evaluable")
    tc.assertEqual(set(row), {"leg_id", "kind", "reason", "disposition"})
    tc.assertTrue(type(row["reason"]) is str and row["reason"])
    if expected:
        tc.assertEqual(row["reason"], expected)
    k.attribute_episode.assert_not_called()
    k.phases.phase_table.assert_not_called()
    k.phases.qualify_ctl01.assert_called_once_with([])


# Every actual no-hidden position, both input representations. Also exercise the
# visible-only envelope of hidden legs without forbidding their physical dose.
def hidden_test(tc, key, mode, value):
    leg = make_leg(key)
    if mode == "native":
        event = packed(leg.episode)
        event["turns"][0]["hidden_tokens"] = value
        try:
            episode = rec.from_json(rec.Episode, blob(event))
        except rec.RecordError:
            if type(value) is int and value >= 0 and value <= leg.episode.turns[0].decode_tokens:
                raise
            return  # Native schema refused before a leg could reach the print.
        leg = replace(leg, episode=episode)
    else:
        leg = marked_turn(leg, fixture.Turn, hidden_tokens=value)
    if type(value) is int and value == 0:
        row = one(leg)
        tc.assertEqual(row["disposition"], "admitted")
        if "hidden_tokens" in row["envelope"]:
            tc.assertIs(type(row["envelope"]["hidden_tokens"]), int)
            tc.assertEqual(row["envelope"]["hidden_tokens"], 0)
    else:
        reject_leg(tc, leg, "envelope_counts")


for key in TYPES:
    for mode in ("native", "memory"):
        for label, val in (
            ("zero", 0),
            ("positive", 37),
            ("negative", -1),
            ("false", False),
            ("true", True),
            ("integral_float", 0.0),
            ("fraction", 0.5),
            ("null", None),
            ("digits", "0"),
            ("detected", "detected"),
            ("K", "K_outcome"),
            ("S", "S_score"),
        ):
            case(f"H_{key}_{mode}_{label}", hidden_test, key, mode, val)


def valid_projection(tc, key):
    leg = make_leg(key)
    row = one(leg)
    tc.assertEqual(row["disposition"], "admitted")
    closed_envelope(tc, leg, row)


for key in TYPES:
    case("P_envelope_" + key, valid_projection, key)


def envelope_field(tc, name, mode):
    key = "L010"
    leg = make_leg(key)
    t = leg.episode.turns[0]
    # Index is constrained to zero by the native Episode constructor. Use the
    # memory Episode for the index-only test, retaining a real native phase view.
    if name == "index":
        if mode == "native":
            d = packed(leg.episode)
            d["turns"][0]["index"] = 71003
            with tc.assertRaises(rec.RecordError):
                rec.from_json(rec.Episode, blob(d))
            return
        t = replace(fixture.Turn(**vars(t)), index=71003)
        leg = replace(leg, episode=unchecked(leg.episode, turns=(t,)))
        tc.assertFalse(paths(one(leg), 71003))
        return
    change = {
        "start_ns": {"start_ns": t.start_ns + 971},
        "first_token_ns": {"first_token_ns": t.first_token_ns + 973},
        "end_ns": {"end_ns": t.end_ns + 977},
        "logged": {"logged": False},
        "tool_calls": {"tool_calls": (rec.ToolCall("ctl_probe_tool", 1, 2, 0, 0),)},
        "context_tokens": {"context_tokens": 983, "prefill_tokens": 3017},
        "prefill_tokens": {"prefill_tokens": 997, "context_tokens": 3003},
        "decode_tokens": {"decode_tokens": 1009},
        "hidden_tokens": {"hidden_tokens": 37},
    }[name]
    leg = marked_turn(leg, fixture.Turn if mode == "memory" else None, **change)
    if mode == "native":
        leg = replace(leg, episode=rec.from_json(rec.Episode, rec.to_json(leg.episode)))
    if name in ("logged", "tool_calls", "start_ns", "first_token_ns", "decode_tokens", "hidden_tokens"):
        reason = (
            "envelope_stamps"
            if name in ("start_ns", "first_token_ns")
            else "logged_envelope"
            if name in ("logged", "tool_calls")
            else "envelope_counts"
        )
        reject_leg(tc, leg, reason)
    else:
        row = one(leg)
        tc.assertEqual(row["disposition"], "admitted")
        tc.assertFalse(paths(row, change[name]))
        closed_envelope(tc, leg, row)


def unchecked(obj, **changes):
    # The flexible builder path accepts objects before native decoder validation.
    clone = deepcopy(obj)
    for k, v in changes.items():
        object.__setattr__(clone, k, v)
    return clone


for mode, cls in (("native", rec.Turn), ("memory", fixture.Turn)):
    for f in fields(cls):
        case("P_turn_" + mode + "_" + f.name, envelope_field, f.name, mode)


def count_type(tc, field, label, value):
    leg = make_leg("L010")
    patch = {field: value}
    if field in ("context_tokens", "prefill_tokens") and type(value) in (int, float, bool):
        patch["prefill_tokens" if field == "context_tokens" else "context_tokens"] = 4000 - value
    leg = marked_turn(leg, fixture.Turn, **patch)
    reject_leg(tc, leg, "envelope_counts")


for f in ("context_tokens", "prefill_tokens", "decode_tokens"):
    for label, val in (
        ("bool", True),
        ("float", 1024.0 if f == "decode_tokens" else 965.0),
        ("negative", -7),
    ):
        case("P_count_" + f + "_" + label, count_type, f, label, val)


# Each source slot has its own case. "absent" checks keys and nested leaves;
# "project" checks the destination of every matching leaf and a positive witness.
# Field names in the transport are the draft's. A translator can supply semantic
# paths for a renamed scientific projection, without changing any private value.
def check_probe(tc, leg, marker, policy, allowed=(), expected=None):
    doc = pri(roster(leg))
    row = doc["legs"][v1.IDS.index(leg.leg_id)]
    if policy == "reject":
        tc.assertIn(row["disposition"], ("not_dispatched", "not_evaluable", "episode_missing"))
        tc.assertFalse("channels" in row or "envelope" in row or "calls" in row)
    else:
        if policy == "project":
            tc.assertIn(row["disposition"], ("admitted", "unadmitted"))
    found = paths(doc, marker)
    if policy == "project":
        # The tuple patterns match complete locations, including source leg.
        patterns = [("legs", v1.IDS.index(leg.leg_id), *suffix) for suffix in allowed]
        unexpected = {
            p
            for p in found
            if not any(
                len(p) == len(pattern) and all(a == b or b == "*" for a, b in zip(p, pattern))
                for pattern in patterns
            )
        }
        tc.assertFalse(unexpected, f"unruled marker destinations: {sorted(map(str, unexpected))}")
        tc.assertTrue(found, "missing authorized private witness")
    else:
        tc.assertFalse(found, f"source marker reached {found}")
    if expected:
        expected(tc, row)


def episode_probe(tc, field):
    leg = make_leg("L010")
    ep = leg.episode
    marker = "ctl_marker_episode_" + field
    updates = {
        "episode_id": marker,
        "task_pair": marker,
        "condition": "sabotage",
        "agent_model": marker,
        "endpoint": marker,
        "seed": 71123,
        "main_task_score": 0.7123493,
        "side_task_success": True,
        "monitor_verdicts": (rec.MonitorVerdict(marker, "full", 37, "e" * 64),),
        "hardware": {"ctl_probe": marker},
        "flags": (marker,),
        "router_log": rec.RouterLog(marker, 1, 1, (0,), ("decode",), (((0,),),)),
        "clock_mappings": (rec.ClockMapping(marker, ep.clock_domain, 1234, 1, "toy"),),
        "power_traces": tuple(replace(t, notes=marker) for t in ep.power_traces),
        "start_ns": 1003,
        "end_ns": ep.end_ns + 1009,
        "turns": (replace(ep.turns[0], end_ns=ep.turns[0].end_ns + 1013),),
        "clock_domain": marker,
        "schema": marker,
    }
    val = updates[field]
    if field == "schema":
        with tc.assertRaises(rec.RecordError):
            replace(ep, schema=marker)
        return
    if field == "clock_domain":
        ep = replace(
            ep,
            clock_domain=marker,
            power_traces=tuple(replace(t, clock_domain=marker) for t in ep.power_traces),
        )
    else:
        ep = replace(ep, **{field: val})
    if field in ("condition", "seed", "main_task_score", "start_ns", "end_ns"):
        marker = val
    if field == "turns":
        marker = val[0].end_ns
    if field == "side_task_success":
        # Boolean value already occurs as dispositions. Change only this bit
        # and require byte-identical private bytes; also deny its key.
        tc.assertEqual(blob(pri(roster(leg))), blob(pri(roster(replace(leg, episode=ep)))))
        marker = field
    check_probe(tc, replace(leg, episode=ep), marker, "absent")


for f in fields(rec.Episode):
    case("P_episode_" + f.name, episode_probe, f.name)


def position_probe(tc, field):
    leg = make_leg("L010")
    if field == "leg_id":
        pos = roster(leg)
        pos[9] = replace(leg, leg_id="ctl_foreign_leg")
        with tc.assertRaisesRegex(ValueError, "roster"):
            pri(pos)
    elif field == "kind":
        for dispatched in (False, True):
            pos = roster(leg)
            pos[9] = replace(leg, kind="detected", g0_released=dispatched)
            with tc.assertRaises(ValueError):
                pri(pos)
        tc.assertEqual(one(leg)["kind"], "cpu")
    elif field == "admitted":
        row = one(replace(leg, admitted=False))
        tc.assertEqual(row["disposition"], "unadmitted")
        tc.assertNotIn("admitted", row)
    elif field == "g0_released":
        check_probe(tc, replace(leg, g0_released=False), "g0_released", "reject")
    elif field == "episode":
        check_probe(tc, replace(leg, episode=None), "work_bytes", "reject")
    elif field == "work_bytes":
        reject_leg(tc, replace(leg, work_bytes=leg.work_bytes + b" ctl_bad_payload"), "script_digest")
    elif field == "work_sha256":
        reject_leg(tc, replace(leg, work_sha256=SHA(b"ctl_other")), "script_digest")
    else:
        tc.fail("unclassified LegInput field " + field)


for f in fields(analysis.LegInput):
    case("P_leg_" + f.name, position_probe, f.name)


def short_counts(leg, member, value, context=False):
    d = json.loads(leg.work_bytes)
    row = d["steps"][member]
    visible = row["kind"] == "turn"
    key = "context_tokens" if context else "actual_tokens"
    diff = value - row[key]
    row[key] = value
    row["complete"] = row["actual_tokens"] == row["requested_tokens"]
    d["complete"] = all(s["complete"] for s in d["steps"])
    if visible:
        t = leg.episode.turns[0]
        field = "prefill_tokens" if context else "decode_tokens"
        leg = marked_turn(leg, **{field: getattr(t, field) + diff})
    return script(leg, **d)


def work_probe(tc, group, field):
    kind_key = {"call": "L010", "hidden": "L005", "cpu": "L010", "gap": "L006", "recovery": "L007"}
    leg = make_leg(kind_key.get(group, "L010"))
    d = json.loads(leg.work_bytes)
    marker = "ctl_marker_" + group + "_" + field
    if group == "record":
        if field in ("schema", "leg_id"):
            d[field] = marker
            reject_leg(tc, script(leg, **d), "script_identity")
        elif field == "steps":
            d["steps"] = list(reversed(d["steps"]))
            reject_leg(tc, script(leg, **d), "script_order")
        elif field == "complete":
            a = one(leg)
            d["complete"] = False
            b = one(script(leg, **d))
            tc.assertNotIn("leg_spec_sha256", b)
            tc.assertNotIn("complete", b)
            tc.assertEqual(a["kind"], b["kind"])
        elif field == "failed_envelope":
            d[field] = {"future_member": [marker]}
            assert_absent_or_refused(tc, script(leg, **d), marker)
        elif field == "script":
            d["script"][marker] = marker
            check_probe(tc, script(leg, **d), marker, "absent")
        else:
            d[field] = SHA(marker.encode()) if field == "leg_spec_sha256" else marker
            check_probe(tc, script(leg, **d), d[field], "absent")
        return
    if group == "script":
        if field == "kind":
            d["script"][field] = marker
            reject_leg(tc, script(leg, **d), "script_identity")
        elif field in ("turn_tokens", "hidden_tokens", "cpu_s", "gap_s", "recovery_s"):
            # Put the prescribed amount and the physical delivery in agreement.
            code = {
                "turn_tokens": "L001",
                "hidden_tokens": "L005",
                "cpu_s": "L004",
                "gap_s": "L006",
                "recovery_s": "L007",
            }[field]
            leg = make_leg(code)
            d = json.loads(leg.work_bytes)
            role = {
                "turn_tokens": "turn",
                "hidden_tokens": "hidden",
                "cpu_s": "cpu",
                "gap_s": "gap",
                "recovery_s": "recovery",
            }[field]
            marker = {"turn": 1024, "hidden": 4, "cpu": 90, "gap": 7, "recovery": 120}[role]
            row = one(leg)
            doses = [s for s in row["calls"] if s["kind"] == role]
            label = "requested_tokens" if role in ("turn", "hidden") else "requested_s"
            tc.assertEqual(
                [s[label] for s in doses], [marker] * len([s for s in d["steps"] if s["kind"] == role])
            )
            # A forbidden string in a prescribed numeric slot cannot reach any
            # print path even if the authenticated script hash matches.
            marker_text = f"ctl_script_{field}"
            d["script"][field] = [marker_text] if field == "turn_tokens" else marker_text
            assert_absent_or_refused(tc, script(leg, **d), marker_text)
        else:
            d["script"][field] = marker
            assert_absent_or_refused(tc, script(leg, **d), marker)
        return
    role = "turn" if group == "call" else group
    i = next(i for i, s in enumerate(d["steps"]) if s["kind"] == role)
    step = d["steps"][i]
    if field == "kind":
        step[field] = marker
        reject_leg(tc, script(leg, **d), "script_order")
    elif field in ("context_tokens", "actual_tokens"):
        marker = {"context_tokens": 1879, "actual_tokens": (3 if role == "hidden" else 479)}[field]
        leg = short_counts(leg, i, marker, context=field == "context_tokens")
        # 3 is common. Use a larger hidden count for the location probe.
        if role == "hidden" and field == "actual_tokens":
            d["script"]["hidden_tokens"] = 379
            step["requested_tokens"] = 379
            leg = short_counts(script(leg, **d), i, 367)
            marker = 367
        allowed = [("calls", i, "context_tokens" if field == "context_tokens" else "delivered_tokens")]
        if role == "hidden" and field == "actual_tokens":
            allowed.append(("channels", "*", "hidden", "delivered_tokens"))
        if role == "turn":
            allowed.append(("envelope", "prompt_tokens" if field == "context_tokens" else "decode_tokens"))
        check_probe(tc, leg, marker, "project", allowed)
    elif field == "requested_tokens":
        step[field] = 2039
        step["complete"] = False
        d["script"]["hidden_tokens" if role == "hidden" else "turn_tokens"] = (
            2039 if role == "hidden" else [2039, 512]
        )
        check_probe(
            tc,
            script(leg, **d),
            2039,
            "project",
            [("calls", i, "requested_tokens"), ("script", "hidden_tokens"), ("script", "turn_tokens", 0)],
        )
    elif field in ("started_ns", "ended_ns", "first_token_ns"):
        # Translate the entire physical record with its envelope. Durations,
        # context and delivery persist. No absolute clock stamp is disclosed.
        shift = 3
        shifted = make_leg(leg.leg_id, shift=shift)
        marker = json.loads(shifted.work_bytes)["steps"][i][field] + 12347
        sd = json.loads(shifted.work_bytes)
        for s in sd["steps"]:
            for name in ("started_ns", "first_token_ns", "ended_ns"):
                if name in s:
                    s[name] += 12347
        t = shifted.episode.turns[0]
        shifted = marked_turn(
            shifted,
            start_ns=t.start_ns + 12347,
            first_token_ns=t.first_token_ns + 12347,
            end_ns=t.end_ns + 12347,
        )
        shifted = replace(shifted, episode=replace(shifted.episode, end_ns=shifted.episode.end_ns + 12347))
        check_probe(tc, script(shifted, **sd), marker, "absent")
    elif field == "requested_s":
        row = one(leg)
        tc.assertEqual(row["calls"][i]["requested_s"], step[field])
        step[field] = marker
        reject_leg(tc, script(leg, **d), "interval_dose")
    elif field == "complete":
        step[field] = marker
        reject_leg(tc, script(leg, **d), "step_bounds")
    else:
        value = {
            "cached_prompt_tokens": 1711,
            "started_epoch_s": 17770011,
            "ended_epoch_s": 17770013,
            "thread_cpu_ns": 10000110073,
        }.get(field, marker)
        step[field] = value
        assert_absent_or_refused(tc, script(leg, **d), value)


def assert_absent_or_refused(tc, leg, marker):
    try:
        doc = pri(roster(leg))
    except (controls.ControlsRefusal, analysis.ViewError) as exc:
        tc.assertNotIn(str(marker), str(exc))
    else:
        tc.assertFalse(paths(doc, marker))


outer = (
    "schema",
    "leg_id",
    "leg_spec_sha256",
    "script",
    "complete",
    "steps",
    "failed_envelope",
    "ctl_future_member",
)
prescribed = ("kind", "turn_tokens", "hidden_tokens", "cpu_s", "gap_s", "recovery_s", "ctl_future_member")
for group, keys in (("record", outer), ("script", prescribed)):
    for f in keys:
        case(f"P_{group}_{f}", work_probe, group, f)
for group in ("call", "hidden", "gap", "cpu", "recovery"):
    actual = {"call": "turn"}.get(group, group)
    source = make_leg(
        {"call": "L010", "hidden": "L005", "gap": "L006", "cpu": "L010", "recovery": "L007"}[group]
    )
    step = next(s for s in json.loads(source.work_bytes)["steps"] if s["kind"] == actual)
    for f in (*sorted(step), "ctl_future_member"):
        case(f"P_{group}_{f}", work_probe, group, f)


def additional_slot(tc, name):
    leg = make_leg("L010")
    source = leg.episode.turns[0]
    cls = dataclasses.make_dataclass(
        "AugmentedTurn", [(name, object)], bases=(fixture.Turn,), frozen=True, kw_only=True
    )
    marker = "ctl_undisclosed_payload_" + name
    turn = cls(**vars(source), **{name: {"nested": [marker]}})
    assert_absent_or_refused(tc, replace(leg, episode=replace(leg.episode, turns=(turn,))), marker)


for f in (
    "generated_text",
    "token_ids",
    "series_member",
    "K_threshold",
    "S_score",
    "detected",
    "future_field",
):
    case("P_extended_turn_" + f, additional_slot, f)


def vocabulary(tc, word, location):
    leg = make_leg("L010")
    if location == "hold":
        member = ("toy", "c" * 64, "L001")
        with tc.assertRaises(ValueError):
            analysis.pool_hold_windows([analysis.HoldWindow(member, "gpu_rail", 40, 0, None, word)], {member})
    elif location == "pooled":
        pool = analysis.pool_hold_windows([], set())
        pool["gpu_rail", 40] = (None, (word,))
        with tc.assertRaises(ValueError):
            one(leg, pooled=pool)
    else:
        with tc.assertRaises(ValueError):
            pri([replace(x, kind=word) if x.leg_id == "L001" else x for x in roster(leg)])


for loc in ("hold", "pooled", "undispatched"):
    for word in ("detected", "K_outcome", "S_score", "unnamed_diagnostic"):
        case("V_" + loc + "_" + word, vocabulary, word, loc)


# Capture the candidate encoder called by the builder adapter. Mutate just one
# private energy cell plus its consequent qualifier. No test calls the encoder
# on an unchanged public record twice in place of running the builder.
def candidate_bytes(c, x):
    from unittest.mock import patch

    original = controls.encode_public_projection
    emitted = []

    def capture(*args):
        raw = original(*args)
        emitted.append(raw)
        return raw

    with patch.object(controls, "encode_public_projection", capture):
        check_fixture(c, x)
    if len(emitted) != 1 or type(emitted[0]) is not bytes:
        raise AssertionError("expected one candidate public serialization")
    return emitted[0]


def public_v1(tc, location, key, idx):
    c, x = v1.example()
    original = candidate_bytes(c, x)
    tc.assertEqual(x["private"]["qualifier"], "yes")
    if idx is None:
        x["private"][location][key] = {10: 7, 30: 2, 90: 4}[key]
    else:
        x["private"][location][key][idx] = {"phases": 96, "totals": 106}[location]
    x["private"]["qualifier"] = "no"
    tc.assertEqual(candidate_bytes(c, x), original)


for grid in ("phases", "totals"):
    for ch in CHANNELS:
        for i, key in enumerate(v1.IDS):
            case(f"U_{grid}_{ch}_{key}", public_v1, grid, ch, i)
for dose in (10, 30, 90):
    case(f"U_burn_{dose}", public_v1, "cpu_other_by_seconds", dose, None)


@lru_cache(None)
def complete(reverse=False):
    # Largest CPU-other absolute energy moves to the 10-s leg on reversal.
    return tuple(make_leg(k, watts=11 if reverse and k == "L010" else 3) for k in TYPES)


def bytes_only(tc, value):
    tc.assertIs(type(value), bytes, "capture exact public artifact bytes")
    tc.assertTrue(value)
    return value


def published(tc, positions):
    # Both streams are captured at the production orchestration boundary. The
    # adapter may translate path/field names; it must invoke the release writer.
    c, _ = v1.example()
    private, public = bridge("publish")(positions, c["public"], KERNEL, None)
    tc.assertIsInstance(private, dict)
    return private, bytes_only(tc, public)


def public_release(tc):
    p0, b0 = published(tc, complete())
    p1, b1 = published(tc, complete(True))
    tc.assertEqual((p0["aligned_power"]["qualified"], p1["aligned_power"]["qualified"]), ("yes", "no"))
    tc.assertEqual(b0, b1)


case("R_flip_actual_writer", public_release)


def public_leaves(tc):
    # Exercise *each occurrence* (including both endpoints of every range).
    # The injection point is the already-computed scientific document at the
    # public/private fork; no impossible print is offered for scientific admission.
    probe = bridge("public_at_fork")
    blind = v1.example()[0]["public"]
    doc = pri(complete(True))
    yes = pri(complete())
    tc.assertEqual((yes["aligned_power"]["qualified"], doc["aligned_power"]["qualified"]), ("yes", "no"))
    control = bytes_only(tc, probe(blind, yes))
    tc.assertEqual(bytes_only(tc, probe(blind, deepcopy(doc))), control)
    for i, (path, value) in enumerate(leaves(doc)):
        if type(value) not in (int, float, bool):
            continue
        with tc.subTest(path=path):
            node = doc
            for k in path[:-1]:
                node = node[k]
            marker = not value if type(value) is bool else type(value)(800003 + i)
            node[path[-1]] = marker
            try:
                tc.assertEqual(bytes_only(tc, probe(blind, doc)), control)
            finally:
                node[path[-1]] = value


case("R_every_serialized_private_number", public_leaves)


def source_public(tc, fn, args):
    # Record the actual input(s) constructed by the private case. Re-run them
    # through the writer, including a case whose private assertion failed.
    # The boundary reads the original positions, so a direct input-to-public
    # leak remains observable even if the private projection is clean.
    from unittest.mock import patch

    publish = bridge("publish")
    inputs = []
    original = pri

    def capture(positions, kernel=KERNEL, pooled=None):
        inputs.append((tuple(positions), pooled))
        return original(positions, kernel=kernel, pooled=pooled)

    with patch.object(sys.modules[__name__], "pri", capture):
        try:
            fn(tc, *args)
        except AssertionError:
            if not inputs:
                raise
    tc.assertTrue(inputs, "case did not submit any print input")
    blind = v1.example()[0]["public"]
    for pos, pool in inputs:
        # Hold roster, blind census and dispatch status fixed. Only the source
        # fields of the affected legs vary. The adapter captures actual bytes.
        # Roster-level refusals are outside this successful-serialization check.
        clean = [
            make_leg(x.leg_id)
            if x.episode is not None and x.g0_released
            else analysis.LegInput(x.leg_id, TYPES[x.leg_id], False, False)
            for x in pos
        ]
        _, b0 = publish(clean, blind, KERNEL, pool)
        _, b1 = publish(pos, blind, KERNEL, pool)
        tc.assertEqual(bytes_only(tc, b1), bytes_only(tc, b0))


for group, keys in (("record", outer), ("script", prescribed)):
    for f in keys:
        case(f"R_src_{group}_{f}", source_public, work_probe, (group, f))
for group in ("call", "hidden", "cpu", "gap", "recovery"):
    sample = make_leg(
        {"call": "L010", "hidden": "L005", "cpu": "L010", "gap": "L006", "recovery": "L007"}[group]
    )
    role = "turn" if group == "call" else group
    s = next(r for r in json.loads(sample.work_bytes)["steps"] if r["kind"] == role)
    for f in (*sorted(s), "ctl_future_member"):
        case(f"R_src_{group}_{f}", source_public, work_probe, (group, f))
for f in fields(rec.Episode):
    if f.name != "schema":
        case("R_src_episode_" + f.name, source_public, episode_probe, (f.name,))
for f in fields(analysis.LegInput):
    if f.name not in ("kind", "leg_id"):
        case("R_src_leg_" + f.name, source_public, position_probe, (f.name,))
for mode, cls in (("native", rec.Turn), ("memory", fixture.Turn)):
    for f in fields(cls):
        if (mode, f.name) != ("native", "index"):
            case("R_src_turn_" + mode + "_" + f.name, source_public, envelope_field, (f.name, mode))


# The nine independent hand vectors. All expected values below follow from
# areas of rectangles/triangles or small rational sums, never a second call
# to the builder for an expected value.
def hand_cpu(tc):
    leg = make_leg("L010")
    raw = KERNEL.phases.phase_table(leg.episode, KERNEL.phases.CPU)["phases"]
    cpu = one(leg)["channels"]["cpu_rail"]
    phases = cpu["absolute"]["phases"]
    # 135 s at 3 W. Logged decode spans 2..15; visible decode spans
    # 2..3 and 14..15. Other grows by 11 s, including the 10-s burn.
    tc.assertEqual([raw[p]["joules"] for p in ("decode", "other")], [39, 363])
    tc.assertEqual([phases[p]["joules"] for p in ("decode", "other")], [6, 393])
    tc.assertEqual(cpu["other"]["cpu"]["joules"], 30)


def hand_bound(tc, amount, expected):
    ep = make_leg("L010").episode

    def e(j):
        return EnergyEstimate(j, 0, "toy", ())

    seg = SegmentEnergy(None, "gap", 0, ep.end_ns, e(amount))
    attr = EpisodeAttribution(ep.episode_id, "cpu_power", e(200), (seg,), ())
    tc.assertIs(KERNEL.phases.phase_table(ep, KERNEL.phases.CPU, attr)["closes"], expected)


def hand_hidden(tc):
    # 3 W baseline. Two-second prefill/decode rectangles cancel on subtraction.
    # Interior triangles leave 2 J prefill, 12 J decode, 14 J in all.
    h = one(make_leg("L002"))["channels"]
    for ch in CHANNELS:
        row = h[ch]
        tc.assertEqual(row["baseline_w"], 3)
        tc.assertEqual(
            [row["hidden"][s] for s in ("call_j", "prefill_j", "decode_j", "j_per_token")], [14, 2, 12, 1]
        )
        tc.assertIs(row["hidden"]["tail_cut"], ch == "dc_in")


def hand_fit(tc, short):
    # (x,y)=(4,6)x2,(8,10)x2,(12,14),(12,18). With six points,
    # xbar=8; Sxx=64; Sxy=80; ybar=32/3. Refitting at each distinct
    # omitted point gives slopes 9/7, 5/4, 10/7, 1 (smallest/largest 1,10/7).
    legs = [
        make_leg(k, hidden_peak=(16 if k == "L009" else None), short=(short and k == "L009")) for k in DOSES
    ]
    doc = pri(roster(*legs))
    for ch in CHANNELS:
        fit = doc["dose_response"][ch]
        tc.assertEqual(set(fit["legs"]), set(DOSES) - ({"L009"} if short else set()))
        tc.assertAlmostEqual(fit["slope"], 1 if short else 5 / 4)
        tc.assertAlmostEqual(fit["intercept"], 2 if short else 2 / 3)
        for actual, fixed in zip(fit["range"], (1, 1 if short else 10 / 7), strict=True):
            tc.assertAlmostEqual(actual, fixed)
    if short:
        row = doc["legs"][8]
        tc.assertEqual(row["delivery"], "short")
        call = next(c for c in row["calls"] if c["kind"] == "hidden")
        tc.assertEqual((call["requested_tokens"], call["delivered_tokens"]), (12, 11))
        tc.assertAlmostEqual(row["channels"]["gpu_rail"]["hidden"]["j_per_token"], 16 / 11)


def hand_recovery(tc):
    row = one(make_leg("L002", incomplete=True))["channels"]
    for ch in CHANNELS:
        d = row[ch]
        tc.assertEqual((d["baseline_w"], d["baseline_reason"]), (None, "incomplete_recovery"))
        tc.assertTrue(all(v is None for v in d["above_baseline_j"].values()))
        tc.assertIs(d["absolute"]["closes"], True)
        tc.assertEqual(d["absolute"]["ungated_j"], 3 * 127 + 14)


def hand_floor(tc, T, w):
    a, b = ("toy", "b" * 64, "L001"), ("toy", "c" * 64, "L002")
    # Retained counts 3,7: denominator 2+6; (2*1²+6*3²)/8=7 W².
    hs = [
        analysis.HoldWindow(k, "gpu_rail", width, n, sd)
        for width in (10, 40, 128)
        for k, n, sd in ((a, 3, 1), (b, 7, 3))
    ]
    p = analysis.pool_hold_windows(hs, {a, b})
    out = analysis.floor_units(2 * T, T, "gpu_rail", p, "a" * 64)
    tc.assertEqual(out["window_s"], w)
    tc.assertEqual(out["under_shortest_window"], T < 10)
    tc.assertAlmostEqual(out["floor_j"], 7**0.5 * T)
    tc.assertAlmostEqual(out["units"], 2 / (7**0.5))


def hand_cpu_floor(tc):
    d = one(make_leg("L010"))["channels"]["cpu_rail"]["other"]["cpu"]
    tc.assertEqual(d["joules"], 30)
    tc.assertEqual(
        (d["floor"]["units"], d["floor"]["floor_j"], d["floor"]["reason"]), (None, None, "no_matched_floor")
    )


def hand_order(tc):
    yes = pri(complete())
    no = pri(complete(True))
    for doc, word, order in ((yes, "yes", True), (no, "no", False)):
        tc.assertEqual(doc["aligned_power"], dict(qualified=word, all_legs_close=True, cpu_burn_order=order))
        # Other is (1 + burn + 120) seconds; 3 W except the perturbed 10-s leg.
        burns = [
            doc["legs"][i]["channels"]["cpu_rail"]["absolute"]["phases"]["other"]["joules"] for i in (9, 2, 3)
        ]
        tc.assertEqual(burns, [393 if order else 1441, 453, 633])


case("A_01_cpu_view", hand_cpu)
for n, y in ((198, True), (197.999, False), (202, True), (202.001, False)):
    case("A_02_closure_" + str(n).replace(".", "p"), hand_bound, n, y)
case("A_03_hidden", hand_hidden)
case("A_04_six_fit", hand_fit, False)
case("A_05_short", hand_fit, True)
case("A_06_incomplete_recovery", hand_recovery)
for T, w in ((9.9, 10), (10, 10), (39.9, 10), (40, 40), (128, 128), (500, 128)):
    case("A_07_window_" + str(T).replace(".", "p"), hand_floor, T, w)
case("A_08_cpu_floor", hand_cpu_floor)
case("A_09_order", hand_order)


# The ledger cases use independent synthetic instrument circumstances. The
# append spy observes the production decision's effect. Only the event type,
# reason, and absence of value are projected; ledger metadata is not prescribed.
REASONS = ("no_dc_in_floor", "no_prefill_size", "dose_under_floor_at_k2")


def observations(reason):
    data = dict(
        gpu_token_floors=[140],
        dc_token_floors=[110],
        qualified_prefills=[2000],
        return_bounds=[25],
        decode_end_lags=[0.3],
    )
    if reason == "no_dc_in_floor":
        data["dc_token_floors"] = []
    elif reason == "no_prefill_size":
        data["qualified_prefills"] = []
    elif reason == "dose_under_floor_at_k2":
        data.update(gpu_token_floors=[513], dc_token_floors=[514])
    return data


def withheld(tc, reason):
    rows = []
    issued = []
    bridge("apply_design")(observations(reason), rows.append, issued.append)
    tc.assertEqual(issued, [])
    tc.assertEqual(rows, [{"kind": "ctl01_withheld", "reason": reason}])


def row_schema(tc, reason, patch, valid):
    row = {"kind": "ctl01_withheld", "reason": reason, **patch}
    append = bridge("append_row")
    recorded = []
    if valid:
        append(row, recorded.append)
        tc.assertEqual(recorded, [row])
    else:
        with tc.assertRaises(ValueError):
            append(row, recorded.append)
        tc.assertEqual(recorded, [])


for reason in REASONS:
    case("W_generate_" + reason, withheld, reason)
    case("W_admit_" + reason, row_schema, reason, {}, True)
for label, val in (
    ("unknown", "other"),
    ("prefixed", "no_dc_in_floor_x"),
    ("case", "NO_PREFILL_SIZE"),
    ("free", "detected"),
    ("empty", ""),
    ("null", None),
    ("bool", True),
    ("list", ["no_prefill_size"]),
):
    case("W_reason_" + label, row_schema, val, {}, False)
for label, val in (("number", 13.25), ("zero", 0), ("text", "invented"), ("object", {"j": 3})):
    case("W_value_" + label, row_schema, REASONS[0], {"value": val}, False)


# Test transport only. The builder adapter maps these semantic roles into its
# actual manifest, blind ledger and closed dispatch, then runs the reader with
# injectable stores. The manifest fixture uses the exact bytes of the builder's
# real manifest/schema format and translate the receipt through its production
# representation; it may never decide a pass/refusal. No real Git writes.
ROLES = (
    "print_code",
    "output_schema",
    "restricted_schema",
    "controls_route",
    "instrument_manifest",
    "hold",
    "edges",
)
CODE_ROLES = ROLES[:4]


def freeze_case(tc, fault, role=None):
    freeze = bridge("read_frozen")
    artifacts = bridge("freeze_artifacts")()
    tc.assertTrue(set(ROLES) <= set(artifacts))
    tc.assertTrue(all(type(raw) is bytes and raw for raw in artifacts.values()))
    tc.assertNotEqual(artifacts["output_schema"], artifacts["restricted_schema"])
    # Examine each independently pinned module of a multi-file print.
    affected = [r for r in artifacts if r == role or (role and r.startswith(role + "/"))] if role else [None]
    for target in affected:
        with tc.subTest(artifact=target):
            attempt_freeze(tc, freeze, artifacts, fault, target)


def attempt_freeze(tc, freeze, artifacts, fault, role):
    prepare = bridge("make_manifest")
    pins = {r: SHA(raw) for r, raw in artifacts.items()}
    look, route = "lm-ctl-01", "controls"
    if fault == "missing_pin":
        del pins[role]
    if fault == "foreign_pin":
        pins[role] = SHA(b"another committed artifact")
    if fault == "bad_digest":
        pins[role] = "b" * 40
    if fault == "swap_schemas":
        pins["output_schema"], pins["restricted_schema"] = pins["restricted_schema"], pins["output_schema"]
    if fault == "foreign_look":
        look = "lm-inst-01"
    if fault == "foreign_route":
        route = "qualification"
    manifest = prepare(look, route, dict(pins))
    tc.assertIs(type(manifest), bytes)
    # Two separate revisions. A modified working copy cannot serve as an
    # immutable committed blob, even if the candidate attests its new hash.
    committed = dict(artifacts, manifest=manifest)
    working = dict(committed)
    revision = SHA(b"toy revision one")[:40]
    foreign = SHA(b"toy revision two")[:40]
    other = {**committed, "manifest": manifest + b" "}
    if fault == "changed_bytes":
        working[role] += b" "
    if fault == "uncommitted":
        del committed[role]
    if fault == "manifest_drift":
        working["manifest"] += b" "
    if fault == "manifest_uncommitted":
        del committed["manifest"]
    commits = {revision: committed, foreign: other}
    receipt = dict(look_id="lm-ctl-01", revision=revision, manifest_sha256=SHA(manifest))
    if fault == "receipt_digest":
        receipt["manifest_sha256"] = SHA(b"wrong manifest")
    if fault == "receipt_revision":
        receipt["revision"] = foreign
    if fault == "receipt_look":
        receipt["look_id"] = "lm-stab-01"
    # Order belongs to the ledger fixture. No caller-supplied pair of sequence
    # numbers can manufacture a valid prior entry. Later facts are invisible.
    design = {"kind": "design_pass", "look_id": "lm-ctl-01"}
    byte = {
        "kind": "byte_pass",
        "look_id": "lm-ctl-01",
        "manifest_sha256": SHA(manifest),
        "hand_vectors_passed": True,
    }
    if fault == "stale_byte_pass":
        byte["manifest_sha256"] = SHA(b"previous manifest")
    if fault == "vectors_unverified":
        byte["hand_vectors_passed"] = False
    history = [design, byte, {"kind": "receipt", **receipt}]
    if fault == "no_receipt":
        history.pop()
    if fault == "no_byte_pass":
        history.pop(1)
    if fault == "design_only":
        history = [design]
    if fault == "late_receipt":
        history = [design, byte, {"kind": "first_ctl_read"}, history[-1]]
    if fault == "same_event_receipt":
        history[-1] = {"kind": "first_ctl_read", "coincident": history[-1]}
    if fault == "receipt_on_sibling":
        history.pop()
    siblings = [{"kind": "receipt", **receipt}] if fault == "receipt_on_sibling" else []
    # adapter receives the genuine chronological prefix and a non-ancestor
    # branch. It cannot backdate a receipt into the prefix using working bytes.
    state = dict(
        committed=commits, current_revision=revision, working=working, history=history, sibling=siblings
    )
    opens = []

    def first_read():
        opens.append("synthetic source")
        return b"synthetic first member"

    if fault == "valid":
        freeze(state, first_read)
        tc.assertGreaterEqual(len(opens), 1)
    else:
        try:
            with tc.assertRaises(ValueError):
                freeze(state, first_read)
        finally:
            tc.assertEqual(opens, [], "refusal occurred after first synthetic read")


case("F_valid", freeze_case, "valid")
for r in ROLES:
    for fault in ("missing_pin", "foreign_pin", "bad_digest", "changed_bytes"):
        case(f"F_{fault}_{r}", freeze_case, fault, r)
for r in CODE_ROLES:
    case(f"F_uncommitted_{r}", freeze_case, "uncommitted", r)
for fault in (
    "swap_schemas",
    "foreign_look",
    "foreign_route",
    "manifest_drift",
    "manifest_uncommitted",
    "receipt_digest",
    "receipt_revision",
    "receipt_look",
    "no_receipt",
    "no_byte_pass",
    "design_only",
    "stale_byte_pass",
    "vectors_unverified",
    "late_receipt",
    "same_event_receipt",
    "receipt_on_sibling",
):
    case("F_" + fault, freeze_case, fault)


# Raw source records nested in Episode. Closed domains (enums, booleans,
# structural arrays) do not have unique scalar canaries. For these, require
# byte-for-byte equality with a matched clean print while changing the field.
# These innocuous off-channel rows are ignored by the scientific kernel.
def nested_record(tc, record, field):
    leg = make_leg("L010")
    ep = leg.episode
    tag = "ctl_nested_" + record + "_" + field
    if record == "ToolCall":
        args = dict(
            name=tag,
            start_ns=601,
            end_ns=691,
            args_bytes=1717,
            result_bytes=1721,
            logged=False,
            state_changed=True,
            state_before_sha256=SHA(b"toy before"),
            state_after_sha256=SHA(b"toy after"),
        )
        tool = rec.ToolCall("toy", 1, 2, 1, 1)
        if field == "start_ns":
            tool = replace(tool, end_ns=999)
        tool = replace(tool, **{field: args[field]})
        leg = marked_turn(leg, tool_calls=(tool,))
        reject_leg(tc, leg, "logged_envelope")
        return
    if record == "PowerTrace":
        base = rec.PowerTrace("mock", "toy_spare", ep.clock_domain, (0, NS), (7.0, 7.0), "W", NS)
        mutations = dict(
            source="ina3221",
            channel=tag,
            clock_domain=tag,
            t_ns=(0, 789012345),
            values=(71.125, 83.75),
            unit="J_cumulative",
            nominal_interval_ns=789100031,
            averaging_window_ns=789100033,
            duty_fraction=0.37431,
            resolution=0.012315,
            notes=tag,
        )
        kw = {field: mutations[field]}
        if field == "unit":
            kw["source"] = "nvml_energy"
        if field == "clock_domain":
            ep = replace(ep, clock_mappings=(rec.ClockMapping(tag, ep.clock_domain, 0, 0, "toy"),))

        def attach(x):
            return replace(ep, power_traces=(*ep.power_traces, x))
    elif record == "MonitorVerdict":
        base = rec.MonitorVerdict("toy", "full", 0, SHA(b"toy prompt"))
        mutations = dict(
            monitor_model=tag, visibility="tampered", suspicion=53.78125, prompt_sha256=SHA(tag.encode())
        )
        kw = {field: mutations[field]}

        def attach(x):
            return replace(ep, monitor_verdicts=(x,))
    elif record == "ClockMapping":
        base = rec.ClockMapping("other", ep.clock_domain, 0, 0, "toy")
        mutations = dict(
            trace_domain=tag, episode_domain=tag, offset_ns=991231, uncertainty_ns=991237, method=tag
        )
        kw = {field: mutations[field]}

        def attach(x):
            return replace(ep, clock_mappings=(x,))
    elif record == "RouterLog":
        base = rec.RouterLog("toy", 4, 1, (0,), ("decode",), (((1,),),))
        mutations = dict(
            model=tag, num_experts=7717, top_k=2, layers=(7719,), phase=("prefill",), experts=(((3,),),)
        )
        kw = {field: mutations[field]}
        if field == "top_k":
            kw["experts"] = (((1, 2),),)

        def attach(x):
            return replace(ep, router_log=x)
    else:
        tc.fail("unclassified " + record)
    before = pri(roster(replace(leg, episode=attach(base))))
    after = pri(roster(replace(leg, episode=attach(replace(base, **kw)))))
    tc.assertEqual(blob(before), blob(after), f"raw {record}.{field} changed the scientific print")
    tc.assertFalse(paths(after, tag))


for cls in (rec.ToolCall, rec.PowerTrace, rec.MonitorVerdict, rec.ClockMapping, rec.RouterLog):
    for f in fields(cls):
        case(f"P_nested_{cls.__name__}_{f.name}", nested_record, cls.__name__, f.name)
        case(f"R_src_nested_{cls.__name__}_{f.name}", source_public, nested_record, (cls.__name__, f.name))


def physical_duration(tc, key):
    leg = make_leg(key)
    d = json.loads(leg.work_bytes)
    row = one(leg)
    raw = [s for s in d["steps"] if s["kind"] in ("turn", "hidden")]
    actual = [s for s in row["calls"] if s["kind"] in ("turn", "hidden")]
    tc.assertEqual(len(raw), len(actual))
    for step, shown in zip(raw, actual, strict=True):
        seconds = (step["ended_ns"] - step["started_ns"]) / NS
        # Semantic projection of seconds in common spellings. Alternate
        # layouts can normalize the units/field name at the test binding.
        tc.assertTrue(
            any(
                type(shown.get(k)) in (float, int) and shown[k] == seconds
                for k in ("duration_s", "seconds", "duration_seconds")
            ),
            f"printed {step['kind']} call lacks its realized {seconds:g} s duration",
        )


for kind in sorted(set(TYPES.values())):
    case(
        "P_duration_" + kind.replace("-", "_"),
        physical_duration,
        next(k for k, t in TYPES.items() if t == kind),
    )


def public_raw_guard(tc, key):
    # Check every actual numerical leaf in the full, independently computed
    # scientific document at this head. Attack both an added key and a legal
    # blind field (including number -> string or hash encodings). This is the
    # real candidate encoder, not evidence of a deployed release writer.
    yes, no = scientific_poles()
    c, x = v1.example()
    blind = c["public"]
    expected = controls.encode_public_projection(x["public"], blind)

    def section(doc):
        return doc["legs"][v1.IDS.index(key)] if key in TYPES else doc[key]

    tc.assertEqual((yes["aligned_power"]["qualified"], no["aligned_power"]["qualified"]), ("yes", "no"))
    seen = 0
    for path, value in leaves(section(no)):
        if type(value) not in (int, float, bool):
            continue
        seen += 1
        with tc.subTest(path=path):
            for patch in ({"private_value": value}, {"stage1_sha256": SHA(blob([key, path, value]))}):
                with tc.assertRaises(controls.ControlsRefusal):
                    controls.encode_public_projection({**x["public"], **patch}, blind)
    tc.assertGreater(seen, 0)
    tc.assertEqual(controls.encode_public_projection(x["public"], blind), expected)


@lru_cache(None)
def scientific_poles():
    return pri(complete()), pri(complete(True))


for key in (*TYPES, "aligned_power", "dose_response", "timing_edge_j"):
    case("Q_exact_candidate_" + key, public_raw_guard, key)


def view_fields(tc):
    # Catch an incidental new input-bearing field that has no classification.
    # HoldWindow is also exercised above and in the floor hand vector.
    tc.assertEqual(
        {f.name for f in fields(analysis.Step)},
        {
            "kind",
            "start_ns",
            "end_ns",
            "complete",
            "first_ns",
            "requested_tokens",
            "delivered_tokens",
            "context_tokens",
            "requested_s",
        },
    )
    tc.assertEqual({f.name for f in fields(analysis.PhysicalView)}, {"episode", "steps"})
    tc.assertEqual(
        {f.name for f in fields(analysis.HoldWindow)},
        {"member", "channel", "window_s", "retained", "sd_w", "reason"},
    )
    tc.assertEqual(
        {f.name for f in fields(fixture.Episode)}, {"episode_id", "turns", "hardware", "start_ns", "end_ns"}
    )
    for group in ("hidden", "call", "cpu", "gap", "recovery"):
        # A runner change introducing a new native key requires reclassifying it.
        key = {"hidden": "L005", "call": "L010", "cpu": "L010", "gap": "L006", "recovery": "L007"}[group]
        kind = "turn" if group == "call" else group
        step = next(x for x in json.loads(make_leg(key).work_bytes)["steps"] if x["kind"] == kind)
        for field in step:
            tc.assertTrue(hasattr(Suite, f"test_P_{group}_{field}"))


case("P_input_field_inventory", view_fields)


def reason_decision(tc, reason):
    # Observe the unadapted head's decision, too. A bare rejection cannot
    # stand in for an appended ledger row. No interpretation of exception
    # messages into made-up ledger evidence is permitted.
    params = observations(reason)
    try:
        chosen = analysis.read_parameters(**params)
    except ValueError:
        chosen = None
    tc.assertNotIsInstance(chosen, analysis.ReadParameters, "a no-kit circumstance produced parameters")


for reason in REASONS:
    case("D_refuses_kit_" + reason, reason_decision, reason)


def detached_counts(tc):
    # A flexible, mutable Turn makes provenance observable even when the
    # aggregate values compare equal at validation. Poison the logged source
    # after the view was built but before private printing/serialization.
    leg = make_leg("L010")
    native = leg.episode.turns[0]
    MutableTurn = dataclasses.make_dataclass("MutableTurn", [(f.name, object) for f in fields(native)])
    source = MutableTurn(**vars(native))
    leg = replace(leg, episode=replace(leg.episode, turns=(source,)))
    k = instrumented()

    def after_validation(view):
        source.context_tokens = 8171
        source.prefill_tokens = 8191
        source.decode_tokens = 8209
        return KERNEL.phases.with_package(view)

    k.phases.with_package.side_effect = after_validation
    row = one(leg, kernel=k)
    k.phases.with_package.assert_called_once()
    tc.assertEqual(row["disposition"], "admitted")
    closed_envelope(tc, leg, row)


case("P_counts_from_physical_after_validation", detached_counts)

for field in (
    "generated_text",
    "token_ids",
    "series_member",
    "K_threshold",
    "S_score",
    "detected",
    "future_field",
):
    case("R_src_extended_turn_" + field, source_public, additional_slot, (field,))


def normal_design(tc, missing):
    data = observations(None)
    data[missing] = []
    rows, issued = [], []
    bridge("apply_design")(data, rows.append, issued.append)
    tc.assertEqual(rows, [])
    tc.assertEqual(len(issued), 1, "single missing non-blocking input with all other prerequisites met")
    # Never inspect or select the resulting doses, gap, recovery, or prefill.


for field in ("gpu_token_floors", "return_bounds", "decode_end_lags"):
    case("W_supported_" + field, normal_design, field)


def missing_reason(tc):
    append = bridge("append_row")
    recorded = []
    with tc.assertRaises(ValueError):
        append({"kind": "ctl01_withheld"}, recorded.append)
    tc.assertEqual(recorded, [])


case("W_reason_missing", missing_reason)


def intact_v1(tc):
    tc.assertEqual(
        SHA(Path(v1.__file__).read_bytes()),
        "a6b991447aa4d564e846d9bb62a532412b52454a9d0711070d8fe07bc5c0d800",
    )


case("I_frozen_v1_bytes", intact_v1)


def floor_source(tc, field):
    member = ("toy-kit", SHA(b"synthetic-floors"), "L001")
    hold = analysis.HoldWindow(member, "gpu_rail", 40, 3, 0.875)
    marker = {
        "member": SHA(b"second member"),
        "channel": "ctl_unknown_channel",
        "window_s": 773,
        "retained": 593,
        "sd_w": 7.015625,
        "reason": "ctl_free_text",
    }[field]
    if field == "member":
        other = (member[0], marker, member[2])
        hold = replace(hold, member=other)
    else:
        hold = replace(hold, **{field: marker})
    if field in ("channel", "window_s", "reason"):
        with tc.assertRaises(ValueError):
            analysis.pool_hold_windows([hold], {hold.member})
        return
    pooled = analysis.pool_hold_windows([hold], {hold.member})
    row = one(make_leg("L010"), pooled=pooled)
    if field == "sd_w":
        tc.assertEqual(row["channels"]["gpu_rail"]["baseline_drift_floor"]["floor_j"], 40 * marker)
    else:
        tc.assertFalse(paths(row, marker))


for f in fields(analysis.HoldWindow):
    case("P_hold_" + f.name, floor_source, f.name)


def print_arg(tc, role):
    leg = make_leg("L010")
    manifest = SHA(b"ctl_distinctive_instrument_identity")
    gap = 2 * NS + 9163
    pool = analysis.pool_hold_windows([], set())
    out = packed(
        analysis.print_controls(
            roster(leg),
            kernel=KERNEL,
            gap_limits_ns=dict.fromkeys(CHANNELS, gap),
            pooled=pool,
            instrument_manifest_sha256=manifest,
        )
    )
    if role == "instrument_manifest":
        where = paths(out, manifest)
        tc.assertTrue(where)
        tc.assertTrue(all(p[-1] == "instrument_manifest_sha256" and "channels" in p for p in where))
    elif role == "gap_limits":
        tc.assertFalse(paths(out, gap))
    else:
        tc.assertEqual(out["timing_edge_j"], 1.0)


for role in ("instrument_manifest", "gap_limits", "kernel_timing_edge"):
    case("P_argument_" + role, print_arg, role)


if __name__ == "__main__":
    unittest.main(verbosity=2)
