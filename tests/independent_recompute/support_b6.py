"""Synthetic block-6 session archives for the block-6 recompute; no repository estimator imports.

Every archive carries the synthetic marker the script requires under JW_B5_SYNTHETIC_ONLY=1.
Powers are constant over quarter-second records, so each run's phase energies are closed-form.
"""
import importlib.util
import json
from pathlib import Path

from .support import ROOT, bundle, dump, recompute as b5

SCRIPT = ROOT / "scripts/independent_recompute_b6.py"
_spec = importlib.util.spec_from_file_location("independent_recompute_b6_test_subject", SCRIPT)
b6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b6)

CAMPAIGN = {"ALPHA": "d117_floor_qwen3-1p7b_v5", "BETA": "d117_floor_qwen3-8b_v5",
            "GAMMA": "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"}
# Section 6.1 rotation over three rounds; ALPHA's round-2 attempt fails its drift screen (D1).
NINE = (("ALPHA", 1), ("BETA", 1), ("GAMMA", 1), ("BETA", 2), ("GAMMA", 2), ("ALPHA", 2),
        ("GAMMA", 3), ("ALPHA", 3), ("BETA", 3))
IDLE_W = 0.5
PRE_S = 0.030


def session_id(pack, round_number):
    return f"b6-{pack.lower()}-r{round_number}"


def edges_for(arm):
    return {"request": (1., 3.), "decode": (2., 3.),
            "prefill": (1., 1.03125) if arm == "decode" else (1., 2.)}


def closed_form(power, edges):
    return {phase: power * (end - start) for phase, (start, end) in edges.items()}


def grid(power):
    """Dyadic powers survive the plist's milliwatt round trip exactly, so the CSV and plist agree."""
    return round(power * 64) / 64


def trace(power):
    """Idle records around the request, so a dropped record moves energy across a phase edge."""
    return [(i / 4, (i + 1) / 4, power if 4 <= i < 12 else IDLE_W) for i in range(16)]


def patch_metadata(path, pre):
    metadata = json.loads((path / "metadata.json").read_text())
    metadata["instrument_calibration"]["b_fiducial_s"] = pre
    metadata["idle_baseline"] = {"power_w_mean": IDLE_W}
    dump(path / "metadata.json", metadata)


def build_session(parent, pack, round_number, k, *, drift_fail=False, exclude=None, assist=(), waited=(), n=10):
    """One session archive; k shifts every power so sessions differ. Returns (archive, closed-form energies)."""
    sid = session_id(pack, round_number)
    archive = parent / sid
    claim, bound = archive / "sources/claim-runs", archive / "sources/bound-runs"
    (archive).mkdir(parents=True)
    (archive / b6.SYNTHETIC_MARKER).write_text("synthetic block-6 fixture\n")
    exclude = dict(exclude or {})
    pre, post = PRE_S + .001 * k, PRE_S + .001 * k + .002
    bop = max(pre, post) + max(abs(post - pre), b6.S_BRACKET_S)
    model_tag = "qwen3-1p7b" if pack == "ALPHA" else "qwen3-8b"
    gamma = pack == "GAMMA"
    cells, members, oracle, kept_counts = [], [], {}, {}
    for arm in ("decode", "prefill-p2048"):
        cid = f"ctr-d117-{arm}-qwen3-1p7b-vs-qwen3-8b" if gamma else f"df-ph-{arm}-{model_tag}"
        strata = ["quad"] if gamma else ["repeat", "quad"]
        cells.append({"cell_id": cid, "strata": strata, "target": True})
        if arm == "decode" and not gamma:
            cells.append({"cell_id": f"df-ph-prefill-p42-{model_tag}", "strata": strata, "target": False})
        counts = {}
        for stratum in strata:
            kept = 0
            for i in range(1, n + 1):
                uid = f"fixture-{arm}-{'r' if stratum == 'repeat' else 'b'}{i:02}"
                ids = []
                for position in (b5.POSITIONS if stratum == "quad" else ("",)):
                    rid = uid + ("-" + position if position else "")
                    ids.append(rid)
                    if gamma:
                        model = b5.SIDE_MODELS[position[0]]
                        power = 10. + .1 * i + .03 * k + (8. + .02 * i + .01 * k if position.startswith("b") else 0.)
                        side_tag = "qwen3-1p7b" if position.startswith("a") else "qwen3-8b"
                        tag = f"df-condition=sw-{arm}-{position[0]}-{side_tag}"
                    else:
                        model, tag = b5.MODELS[pack], None
                        power = 10. + .1 * i + .03 * k + (.2 if stratum == "quad" else 0.) + (
                            .05 * i if position.startswith("b") else 0.) + (2. if pack == "BETA" else 0.)
                    power = grid(power)
                    edges = edges_for(arm)
                    path = bundle(claim, rid, power, model, 42 if arm == "decode" else 2048, pre + .014531,
                                  records=trace(power), edges=edges, config_tag=tag)
                    patch_metadata(path, pre)
                    oracle[rid] = closed_form(power, edges)
                    units = [{"cell_id": cid, "stratum": stratum, "unit_id": uid}]
                    if arm == "decode" and not gamma:
                        units.append({"cell_id": f"df-ph-prefill-p42-{model_tag}", "stratum": stratum, "unit_id": uid})
                    members.append({"kind": "science", "run_id": rid, "stage_id": arm, "units": units})
                kept += not any(rid in exclude for rid in ids)
            counts[stratum] = kept
        kept_counts[cid] = counts
        if arm == "decode" and not gamma:
            kept_counts[f"df-ph-prefill-p42-{model_tag}"] = dict(counts)
    for i in range(1, 19):
        rid = f"neg8-refcorpus-r{i:02}"
        power = grid((10. + .03 * ((i * 7) % 12) + .01 * k) / 2)
        path = bundle(bound, rid, power, b6.REFERENCE_MODEL, bop=pre + .014531, records=trace(power))
        patch_metadata(path, pre)
        oracle[rid] = closed_form(power, {"request": (1., 3.), "decode": (2., 3.), "prefill": (1., 2.)})
        members.append({"kind": "auxiliary", "run_id": rid, "stage_id": "corpus", "units": []})
    for which in ("start", "midpoint", "end"):
        for i in range(1, 2 if which == "midpoint" else 4):
            rid = f"neg8-window-{which}" + (f"-r{i}" if which != "midpoint" else "")
            power = grid(5.0 + .01 * k + (.6 if drift_fail and which == "end" else 0.) + .02 * i)
            path = bundle(claim, rid, power, b6.REFERENCE_MODEL, bop=pre + .014531, records=trace(power))
            patch_metadata(path, pre)
            oracle[rid] = closed_form(power, {"request": (1., 3.), "decode": (2., 3.), "prefill": (1., 2.)})
            members.append({"kind": "auxiliary", "run_id": rid, "stage_id": which + "_reference", "units": []})
    for slot, value in (("pre", pre), ("post", post)):
        dump(claim / f"instrument_validation/{sid}-cal-{slot}/instrument_evidence.json",
             {"b_fiducial_s": value, "validation_id": f"{sid}-cal-{slot}"})
    dump(archive / "derived/bracket-binding.json", {"endpoints": {s: {"attempt_id": f"{sid}-cal-{s}"} for s in ("pre", "post")}})
    dump(archive / "harvest.json", {"pack_id": CAMPAIGN[pack], "session_id": sid})
    dump(archive / "derived/roster.json", {"pack_id": CAMPAIGN[pack], "plan_id": sid, "attempt": round_number,
                                           "cells": cells, "members": members})
    flags = [{"code": "battery.assist", "scope": {"run_id": rid}} for rid in assist]
    flags += [{"code": "idle.waited", "scope": {"run_id": rid}} for rid in waited]
    (archive / "derived").mkdir(exist_ok=True)
    (archive / "derived/flags.jsonl").write_text("".join(json.dumps(f) + "\n" for f in flags))
    excluding = [{"code": code, "scope": "member", "run_id": rid, "why": code}
                 for rid, codes in sorted(exclude.items()) for code in codes]
    if drift_fail:
        excluding.append({"code": "neg8.survivor_screen_failed", "scope": "window", "why": "screen_failed"})
    counting = not drift_fail
    dump(archive / "derived/b6-acceptance.json", {
        "schema": b6.ACCEPTANCE_SCHEMA, "mode": "synthetic", "pack_id": CAMPAIGN[pack], "session_id": sid,
        "verdict": "ACCEPT" if counting else "EXCLUDE", "counting": counting, "physics_stop": False,
        "physical_stop_kind": None, "stop_reason": "completed", "structural_failures": [], "excluding": excluding,
        "flag_counts": {}, "cells": kept_counts,
        "calibration": {"pre_s": repr(pre), "post_s": repr(post), "operative_bound_s": repr(bop)},
        "neg8": {"verdict": "failed" if drift_fail else "passed", "survivors": {"start": 3, "midpoint": 1, "end": 3},
                 "corpus_clean_n": 12}})
    return archive, oracle


def attempts_rows(specs):
    return [{"session_id": session_id(pack, rnd), "round": rnd, "packs": [pack.lower()], "t0": 1.0e9 + i,
             "outcomes": {pack.lower(): {"status": "counting" if counting else "not_counting", "cause": None}}}
            for i, (pack, rnd, counting) in enumerate(specs)]


def write_attempts(path, specs):
    path.write_text("".join(json.dumps(row) + "\n" for row in attempts_rows(specs)))
    return path


def nine_sessions(parent):
    """The nine-session synthetic block: ALPHA_2 is the one non-counting session (D1)."""
    archives, oracles, specs = [], {}, []
    for k, (pack, rnd) in enumerate(NINE):
        options = {}
        if (pack, rnd) == ("ALPHA", 2):
            options["drift_fail"] = True
        if (pack, rnd) == ("ALPHA", 1):
            options.update(exclude={"fixture-decode-r03": ["thermal.os_level_nonzero"],
                                    "fixture-prefill-p2048-b04-b1": ["member.status_not_succeeded"]},
                           assist=["fixture-decode-r05"], waited=["fixture-prefill-p2048-r02"])
        if (pack, rnd) == ("GAMMA", 1):
            options.update(exclude={"fixture-decode-b02-a2": ["thermal.powermetrics_pressure_elevated"]})
        archive, oracle = build_session(parent, pack, rnd, k, **options)
        archives.append(archive)
        oracles[session_id(pack, rnd)] = oracle
        specs.append((pack, rnd, not options.get("drift_fail")))
    attempts = write_attempts(parent / "attempts.jsonl", specs)
    return archives, attempts, oracles
