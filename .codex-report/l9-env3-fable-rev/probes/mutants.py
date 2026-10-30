"""Mutation harness: apply one mutant to the scratch tree's whole_window.py, run kill tests, restore."""
import subprocess, sys, os, shutil, json, time
from pathlib import Path
S = Path(__file__).resolve().parent
TREE = S / "tree"; WW = TREE / "joulewise/whole_window.py"; PRISTINE = S / "whole_window.pristine.py"
if not PRISTINE.exists(): shutil.copyfile(WW, PRISTINE)
OUT = S / "out/mutants"; OUT.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, TMPDIR="/tmp/lnine-fable-rev/tmp", JW_B5_SYNTHETIC_ONLY="1", PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(TREE))
MUTANTS = {
 "M01_clamp_to_shifted_start": [("(window.start_s + window.end_s) / 2.0", "window.start_s", 2)],
 "M02_clamp_to_shifted_end": [("(window.start_s + window.end_s) / 2.0", "window.end_s", 2)],
 "M03_clamp_condition_le": [("                    if window.end_s < window.start_s\n                    else window\n                    for window in shifted_windows", "                    if window.end_s <= window.start_s\n                    else window\n                    for window in shifted_windows", 1)],
 "M04_drop_negative_power_guard": [("            or any(point.power_w < 0.0 for point in curve)\n            for curve, windows in contributions\n        )\n    ):\n        return None\n\n    origin_s = contributions[0][0][0].t\n    contributions = [", "            for curve, windows in contributions\n        )\n    ):\n        return None\n\n    origin_s = contributions[0][0][0].t\n    contributions = [", 1)],
 "M05_edge_bound_wrong_sign": [("    edge_bound_s = fiducial_bound_s + wall_minus_monotonic_span_s\n    corner_envelopes: list[dict[str, float | str]] = []\n    for eps_on_s in (-edge_bound_s, edge_bound_s):\n        for eps_off_s in (-edge_bound_s, edge_bound_s):\n            corner_contributions: list[tuple[list[TracePoint], list[Window]]] = []\n            for curve, windows in contributions:\n                shifted_windows = [\n                    Window(\n                        start_s=window.start_s + eps_on_s,\n                        end_s=window.end_s + eps_off_s,\n                    )\n                    for window in windows\n                ]\n                # The one ruled change", "    edge_bound_s = fiducial_bound_s - wall_minus_monotonic_span_s\n    corner_envelopes: list[dict[str, float | str]] = []\n    for eps_on_s in (-edge_bound_s, edge_bound_s):\n        for eps_off_s in (-edge_bound_s, edge_bound_s):\n            corner_contributions: list[tuple[list[TracePoint], list[Window]]] = []\n            for curve, windows in contributions:\n                shifted_windows = [\n                    Window(\n                        start_s=window.start_s + eps_on_s,\n                        end_s=window.end_s + eps_off_s,\n                    )\n                    for window in windows\n                ]\n                # The one ruled change", 1)],
 "M06_mirror_drops_item_family": [("    for item in reader.item_windows():\n        rows.append(\n            (\n                \"/suite_item_energy_j/\"\n                + _json_pointer_token(f\"{item.item_index}:{item.item_id}\"),\n                [(curve, [item.window])],\n            )\n        )\n", "", 1)],
 "M07_mirror_uses_raw_curve_052": [("    curve = anchor_curve if anchor_curve is not None else raw_curve\n", "    curve = raw_curve\n", 1)],
 "M08_restamp_every_group_gate": [("                isinstance(gate, dict)\n                and prefix + _json_pointer_token(str(member)) == pointer\n                and not _restamp_clamped_gate(", "                isinstance(gate, dict)\n                and not _restamp_clamped_gate(", 1)],
 "M09_restamp_ignores_eligible": [("        or _ANCHOR_ENVELOPE_UNRECORDED not in existing\n        or gate.get(\"eligible\") is not False\n    ):", "        or _ANCHOR_ENVELOPE_UNRECORDED not in existing\n    ):", 1)],
 "M10_drop_recorded_reconstruction_check": [("                if _corner_composed_anchor_shift_envelope(\n                    contributions, *bounds\n                ) != recorded:\n                    return summary\n                continue", "                continue", 1)],
 "M11_v062_anchor_shift_sign": [("            anchor_curve[0].t - raw_curve[0].t\n", "            raw_curve[0].t - anchor_curve[0].t\n", 1)],
 "M12_clamped_pointers_appended_last": [("    for pointer, _contributions in rows:\n        if pointer in recorded:\n            ordered[pointer] = recorded[pointer]\n        elif pointer in clamped:\n            ordered[pointer] = clamped[pointer]\n", "    for pointer, _contributions in rows:\n        if pointer in recorded:\n            ordered[pointer] = recorded[pointer]\n    for pointer, _contributions in rows:\n        if pointer in clamped:\n            ordered[pointer] = clamped[pointer]\n", 1)],
 "M13_clamp_disabled": [("    return _clamp_inverted_operative_envelopes(\n        path,\n        summary,\n        authenticated_fiducial_bound_s=authenticated_fiducial_bound_s,\n        instrument_calibration_physics_cache=_instrument_calibration_physics_cache,\n    )\n", "    return summary\n", 1)],
 "M14_always_recompute_body": [("    if minted is not None:\n        return minted\n", "", 1)],
 "M15_restamp_skips_inner_windows": [("    windows = gate.get(\"windows\")\n    if isinstance(windows, list):\n        for inner in windows:\n            if isinstance(inner, dict) and not _restamp_clamped_gate(inner, reasons):\n                return False\n    return True", "    return True", 1)],
 "M16_gate_reasons_without_joint_bound": [("                    gate, _anchor_envelope_gate_reasons(envelope, joint_bound_j)\n", "                    gate, _anchor_envelope_gate_reasons(envelope, None)\n", 1)],
 "M17_v062_summed_curve_instead_of_source": [("                            _shift_curve(\n                                reader.source_curve(source), anchor_shift_s\n                            ),", "                            curve,", 1)],
 "M18_skip_unknown_recorded_pointer_guard": [("        # A recorded member envelope the reconstruction does not know.\n        return summary\n", "        # A recorded member envelope the reconstruction does not know.\n        pass\n", 1)],
}
STRUCTURAL = {"M06_mirror_drops_item_family","M07_mirror_uses_raw_curve_052","M11_v062_anchor_shift_sign","M17_v062_summed_curve_instead_of_source"}
FUNCTION_LEVEL = {"M01_clamp_to_shifted_start","M02_clamp_to_shifted_end","M03_clamp_condition_le","M04_drop_negative_power_guard","M05_edge_bound_wrong_sign","M14_always_recompute_body"}

def run(cmd, log, cwd, timeout=2400):
    with open(log, "w") as f:
        t=time.time(); r = subprocess.run(cmd, cwd=cwd, env=ENV, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
    text = Path(log).read_text(errors="replace").splitlines()
    return r.returncode, (text[-1] if text else ""), f"{time.time()-t:.0f}s"

results = {}
names = sys.argv[1:] or list(MUTANTS)
for name in names:
    src = PRISTINE.read_text()
    for old, new, count in MUTANTS[name]:
        assert src.count(old) == count, (name, src.count(old))
        src = src.replace(old, new)
    WW.write_text(src)
    try:
        d = OUT / name; d.mkdir(exist_ok=True)
        res = {}
        rc, tail, dt = run(["python3.13", "-m", "unittest", "tests.test_whole_window_inverted_corner_clamp"], d/"K1_seat_tests.log", TREE)
        ran = [l for l in (d/"K1_seat_tests.log").read_text(errors="replace").splitlines() if l.startswith("Ran ")]
        res["K1_seat_tests"] = {"rc": rc, "ran": ran[-1] if ran else "", "tail": tail, "time": dt}
        if name in FUNCTION_LEVEL:
            rc, tail, dt = run(["python3.13", str(S/"probes/r1_oracle_sweep.py"), str(TREE)], d/"K2_r1_sweep.log", S)
            res["K2_r1_sweep"] = {"rc": rc, "tail": tail, "time": dt}
        if name in STRUCTURAL:
            rc, tail, dt = run(["python3.13", str(S/"probes/r2_v062_structural_probe.py"), str(TREE)], d/"K4_structural.log", S)
            res["K4_structural"] = {"rc": rc, "tail": tail, "time": dt}
        work = Path("/tmp/lnine-fable-rev/tmp/mut-"+name); shutil.rmtree(work, ignore_errors=True)
        rc, tail, dt = run(["python3.13", str(S/"probes/r2_r4_fixture_probe.py"), str(TREE), str(work)], d/"K3_r2r4_probe.log", TREE)
        res["K3_r2r4_probe"] = {"rc": rc, "tail": tail, "time": dt}
        shutil.rmtree(work, ignore_errors=True)
        # (fixed after the run: the first version compared the K1 tail to "OK" exactly, so "OK (skipped=1)"
        # printed every mutant as KILLED; the per-check tails in the logs are authoritative and the
        # report's table recomputes killed = K1 not OK or any probe not "RESULT: PASS".)
        killed = not (res["K1_seat_tests"]["tail"].startswith("OK") and all(v["tail"] == "RESULT: PASS" for k, v in res.items() if k != "K1_seat_tests"))
        res["killed"] = killed
        results[name] = res
        print(name, "KILLED" if killed else "SURVIVED", json.dumps(res), flush=True)
    finally:
        WW.write_text(PRISTINE.read_text())
(OUT / ("summary_%d.json" % os.getpid())).write_text(json.dumps(results, indent=1))
