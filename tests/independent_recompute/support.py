"""Independent synthetic inputs and file-path loading; no repository estimator imports."""
import contextlib
import datetime
import importlib.util
import hashlib
import io
import json
import math
import os
from pathlib import Path
import plistlib

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/independent_recompute_b5.py"
spec = importlib.util.spec_from_file_location("independent_recompute_b5_test_subject", SCRIPT)
recompute = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recompute)
R = [10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6]
B = [10.4, 10.1, 10.3, 10.2, 10.5, 10.0, 10.2, 10.3, 10.1, 9.9]
D = [.10, -.05, .20, .00, -.10, .05, .15, -.05, .10, .00]
CONTRAST = [3.1, 2.9, 3.3, 3.0, 2.8, 3.2, 3.1, 2.9, 3.0, 2.7]
CORPUS = [99.62, 99.71, 99.80, 99.88, 99.93, 99.97, 100.04, 100.09, 100.15, 100.22, 100.31, 100.38]
KINDS = (.010, .000, .050)


def archive_available(path):
    # Short circuit before even inspecting an external archive in synthetic-only runs.
    return os.environ.get("JW_B5_SYNTHETIC_ONLY") != "1" and path.exists()


def agreement_bar(expected, *, ratio=False, half_width=None):
    # Script-header agreement policy: 1% of the smallest printed half-width, when provided. Otherwise
    # 1e-6 relative / 1e-6 column units near zero. Both exceed 1e6 x double
    # noise (2.2e-16, hence 2.2e-10 relative). Four-decimal rho uses 1e-6
    # absolute, 1% of its 1e-4 printed resolution.
    if half_width is not None:
        return .01 * half_width
    return 1e-6 if ratio else max(1e-6, abs(expected) * 1e-6)


def assert_printed(case, actual, expected, digits):
    # These witnesses specify a rounded printed word, not an unrounded value.
    # Exact words at the stated decimal precision require no agreement slack.
    case.assertEqual(f"{actual:.{digits}f}", f"{expected:.{digits}f}")


def assert_values_agree(case, actual, expected, *, ratio=False, half_width=None):
    """Unrounded numeric witnesses; keep integer counts and labels exact."""
    if isinstance(expected, dict):
        case.assertEqual(actual.keys(), expected.keys())
        for key, value in expected.items():
            assert_values_agree(case, actual[key], value, ratio=ratio, half_width=half_width)
    elif isinstance(expected, (list, tuple)):
        case.assertEqual(len(actual), len(expected))
        for value, target in zip(actual, expected):
            assert_values_agree(case, value, target, ratio=ratio, half_width=half_width)
    elif isinstance(expected, float) or isinstance(actual, float):
        case.assertAlmostEqual(actual, expected, delta=agreement_bar(expected, ratio=ratio, half_width=half_width))
    else:
        case.assertEqual(actual, expected)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def run_cli(archives, out, extra=()):
    args = []
    for pack, archive in archives.items():
        args.extend(("--" + pack.lower(), str(archive)))
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        rc = recompute.main([*args, *extra, "--out", str(out)])
    return rc, json.loads(out.read_text()), stdout.getvalue().strip()


def bundle(root, run_id, power=10., model="Qwen3-1.7B-4bit", prompt=2048, bop=.045,
           records=None, edges=None, config_tag=None, status="succeeded"):
    path = root / run_id
    path.mkdir(parents=True, exist_ok=True)
    # Exactly representable quarters keep closed-form energies unambiguous.
    records = records or [(i / 4, (i + 1) / 4, power) for i in range(16)]
    edges = edges or {"prefill": (1., 2.), "decode": (2., 3.), "request": (1., 3.)}
    bpre = bop - .014531
    metadata = {"run_id": run_id, "model": {"name": model},
                "instrument_calibration": {"b_fiducial_s": bpre},
                "uncertainty_evidence": {"clock_anchor": {
                    "status": "bounded", "first_sample_end_point_epoch_s": records[0][1],
                    "effective_clock_anchor_bound_s": .001, "wall_minus_monotonic_span_s": .0003}},
                "workload_observed": {"output_token_count": 512, "token_count": prompt + 512},
                "workload_provenance": {"prompt": {"realized_token_count": prompt}}}
    dump(path / "metadata.json", metadata)
    events = [{"event_type": "phase_end", "phase": "tokenize", "timestamp_s": .9,
               "metadata": {"prompt_tokens": prompt}}]
    for phase, (on, off) in edges.items():
        start, end = ("sampling_started", "sampling_stopped") if phase == "request" else ("phase_start", "phase_end")
        event_phase = "measured_run" if phase == "request" else phase
        events.extend([{"event_type": start, "phase": event_phase, "timestamp_s": on,
                        "metadata": {"prompt_tokens": prompt}},
                       {"event_type": end, "phase": event_phase, "timestamp_s": off, "metadata": {}}])
    (path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    summary = {"status": status, "phase_energy_j": {}, "energy_anchor_shift_envelopes": {},
               "energy_bound_terms_j": {"E_interpolation_joint_edge_bound_j": 0.0}}
    for phase, (on, off) in edges.items():
        energy = recompute.overlap(records, on, off)[0]
        if phase == "request":
            summary["gross_energy_j"] = energy
            key = "/gross_energy_j"
        else:
            summary["phase_energy_j"][phase] = energy
            key = "/phase_energy_j/" + phase
        summary["energy_anchor_shift_envelopes"][key] = recompute.shift_envelope(records, on, off, bpre, .0003, .001)
    dump(path / "summary_metrics.json", summary)
    dump(path / "config.json", {"run_metadata": {"tags": [config_tag] if config_tag else []}})
    frames = []
    csv = ["timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"]
    for start, end, power in records:
        frames.append(plistlib.dumps({"elapsed_ns": round((end - start) * 1e9),
                     "timestamp": datetime.datetime.fromtimestamp(math.floor(end), datetime.timezone.utc).replace(tzinfo=None),
                     "processor": {"cpu_power": power * 1000, "gpu_power": 0., "ane_power": 0.}}))
        for rail, p in (("cpu_power", power), ("gpu_power", 0.), ("ane_power", 0.)):
            csv.append(f"{end},{p},powermetrics,{rail},{start},{end}\n")
    (path / "raw").mkdir(exist_ok=True)
    (path / "raw/powermetrics.plist").write_bytes(b"\x00".join(frames))
    (path / "power_trace.csv").write_text("".join(csv))
    return path


def full_pack(parent, pack, n=10):
    """100 science members per floor pack, 80 for GAMMA; tiny raw streams."""
    archive = parent / pack
    claim, bound = archive / "sources/claim-runs", archive / "sources/bound-runs"
    model_tag = "qwen3-1p7b" if pack == "ALPHA" else "qwen3-8b"
    bop = .045
    pre = bop - .014531
    cells, members, exclusions = [], [], []
    for arm in ("decode", "prefill-p2048"):
        gamma = pack == "GAMMA"
        cid = (f"ctr-d117-{arm}-qwen3-1p7b-vs-qwen3-8b" if gamma else f"df-ph-{arm}-{model_tag}")
        strata = ["quad"] if gamma else ["repeat", "quad"]
        cells.append({"cell_id": cid, "strata": strata, "target": True})
        kept = {s: [] for s in strata}
        for stratum in strata:
            for i in range(1, n + 1):
                uid = f"fixture-{arm}-{'r' if stratum == 'repeat' else 'b'}{i:02}"
                kept[stratum].append(uid)
                for position in (recompute.POSITIONS if stratum == "quad" else ("",)):
                    rid = uid + ("-" + position if position else "")
                    if gamma:
                        model = recompute.SIDE_MODELS[position[0]]
                        power = 10. + .1 * i + (3. + .02 * i if position.startswith("b") else 0.)
                        tag_model = "qwen3-1p7b" if position.startswith("a") else "qwen3-8b"
                        tag = f"df-condition=sw-{arm}-{position[0]}-{tag_model}"
                    else:
                        model, tag = recompute.MODELS[pack], None
                        power = 10. + .1 * i + (.2 if stratum == "quad" else 0.) + (
                            .05 * i if position.startswith("b") else 0.)
                        if pack == "BETA":
                            power += 2.
                    edges = {"request": (1., 3.), "decode": (2., 3.),
                             "prefill": (1., 1.03125) if arm == "decode" else (1., 2.)}
                    bundle(claim, rid, power, model, 42 if arm == "decode" else 2048, bop,
                           edges=edges, config_tag=tag)
                    units = [{"cell_id": cid, "stratum": stratum, "unit_id": uid}]
                    if arm == "decode" and not gamma:
                        units.append({"cell_id": f"df-ph-prefill-p42-{model_tag}", "stratum": stratum, "unit_id": uid})
                    members.append({"kind": "science", "run_id": rid, "stage_id": arm, "units": units})
        exclusions.append({"cell_id": cid, "kept_units": kept, "dropped_units": [], "target": True})
        if arm == "decode" and not gamma:
            p42 = f"df-ph-prefill-p42-{model_tag}"
            cells.append({"cell_id": p42, "strata": strata, "target": False})
            exclusions.append({"cell_id": p42, "kept_units": {s: list(v) for s, v in kept.items()}, "target": False})
    corpus_ids = []
    energies = [10. + i * .03 for i in range(12)]
    for i, energy in enumerate(energies, 1):
        rid = f"neg8-refcorpus-r{i:02}"
        corpus_ids.append(rid)
        bundle(bound, rid, energy / 2, "Qwen2.5-1.5B-Instruct-4bit", bop=bop)
    for which in ("start", "midpoint", "end"):
        for i in range(1, 2 if which == "midpoint" else 4):
            rid = f"neg8-window-{which}" + (f"-r{i}" if which != "midpoint" else "")
            bundle(claim, rid, 5., "Qwen2.5-1.5B-Instruct-4bit", bop=bop)
            members.append({"kind": "auxiliary", "run_id": rid, "stage_id": which + "_reference", "units": []})
    allowance = recompute.neg8_bound(energies, 3, 3)["bound_j"]
    dump(archive / "harvest.json", {"pack_id": pack, "attempt": 1, "harvest_checkout": {
        "status_clean": True, "status_lines": 0, "errors": []}})
    dump(archive / "derived/roster.json", {"pack_id": pack, "attempt": 1, "cells": cells, "members": members})
    dump(archive / "derived/exclusions.json", {"schema": "joulewise.exclusions.v1", "pack_id": pack,
         "attempt": 1, "claim_usable": True, "members_excluded": [], "cells": exclusions})
    (archive / "derived/flags.jsonl").write_text("")
    dump(archive / "derived/neg8-allowance.json", {"source": "survivor_rescreen", "clean_bound": {"path": "fixture"}})
    dump(archive / "derived/neg8-clean-corpus.json", {"members": [{"bundle_id": rid} for rid in corpus_ids]})
    dump(archive / "derived/neg8-screen.json", {"rescreen": {"decision": "passed", "survivors": {
         "reference_losses": [], "reference_counts": {"start": 3, "midpoint": 1, "end": 3}, "midpoint_lost": False}}})
    dump(archive / "withheld/neg8-rescreen-bracket.json", {"bracket": {
         "drift_allowances": {"gross_energy": {"allowance_j": allowance}}}})
    dump(archive / "withheld/bracket-evaluation.json", {"assessment": {"b_fiducial_s": bop}})
    dump(claim / "whole-window-verdict.json", {"bundle_ids": [m["run_id"] for m in members],
         "evaluation_basis": {"member_occurrences": [{"bundle_id": m["run_id"]} for m in members]}})
    stages, external = [], []
    for which in ("start", "midpoint", "end"):
        manifest = "fixture/" + which + "/order_manifest.json"
        refs = [m for m in members if m["kind"] == "auxiliary" and which in m["stage_id"]]
        stages.append({"input": {"path": manifest}, "spare_retry": {"slot": which, "members": [
            {"run_id": "neg8-window-" + which + "-spare-1"}]}})
        external.append({"manifest": {"path": manifest}, "members": [{"run_id": m["run_id"]} for m in refs]})
    tree_path = archive / "sources/repo/configs/campaigns" / pack / "plan_tree.json"
    dump(tree_path, {"stage_graph": stages, "external_inputs": {"manifests": external}})
    dump(archive / "sources/repo/configs/campaigns/v5_claim_25g83/sizing_b5.json", {
         "packs": {pack: {"plan_tree": {"sha256": hashlib.sha256(tree_path.read_bytes()).hexdigest()}}}})
    dump(archive / "derived/bracket-binding.json", {"endpoints": {
        s: {"attempt_id": "fixture-cal-" + s} for s in ("pre", "post")}})
    dump(archive / "derived/terminal-pin.json", {"sequence": 400})
    dump(archive / "sources/repo/configs/calibration/calibration_acceptance_fixture.json", {
         "acceptance_id": "d079_calibration_acceptance_v2_n24_25g83_r2", "identity_epoch": {"test": "epoch"},
         "derivation_corpus": {"members": [{"member_id": str(i), "b_fiducial_s": ".035"} for i in range(24)]}})
    ledger = archive / "sources/ledger/calibration_observation_ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(json.dumps({"sequence": 400, "disposition": "valid", "identity_epoch": {"test": "epoch"},
                                 "exact_bound_lexeme_s": ".035", "attempt_id": "fixture"}) + "\n")
    for slot in ("pre", "post"):
        dump(claim / f"instrument_validation/fixture-cal-{slot}/instrument_evidence.json", {
            "b_fiducial_s": pre, "validation_id": "fixture-cal-" + slot})
    return archive


def remove_member(archive, rid, codes=("member.admission_aborted",)):
    path = archive / "derived/exclusions.json"
    exclusions = json.loads(path.read_text())
    exclusions["members_excluded"].append({"run_id": rid, "codes": list(codes)})
    roster = json.loads((archive / "derived/roster.json").read_text())
    row = next(m for m in roster["members"] if m["run_id"] == rid)
    for unit in row["units"]:
        cell = next(c for c in exclusions["cells"] if c["cell_id"] == unit["cell_id"])
        uid, stratum = unit["unit_id"], unit["stratum"]
        cell["kept_units"][stratum].remove(uid)
        cell.setdefault("dropped_units", []).append({"unit_id": uid, "stratum": stratum, "codes": list(codes)})
    dump(path, exclusions)
