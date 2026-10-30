"""Q1/Q2 probe on the suite's synthetic 0.5.2 bundle (tests.test_whole_window_selection).
(a) to_dict JSON round trip is lossless; (b) at a non-inverting dominating bound the
analysis re-derivation returns reduce's object itself; (c) at an inverting bound only
energy_anchor_shift_envelopes and the clamped members' precheck reasons differ; every
energy figure is identical; (d) the clamped member's envelope: lower_j == 0, point_j equal
to reduce's phase figure at mint; gate stays ineligible."""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, ".")
import joulewise.reduce as R
import joulewise.whole_window as W
from tests.test_whole_window_inverted_corner_clamp import _bundle_fixture, _phase_durations, PREFILL

class T(unittest.TestCase):
    def runTest(self): pass
t = T()
tmp = tempfile.TemporaryDirectory(); root = Path(tmp.name)
bundle, minted, minted_bound = _bundle_fixture(t, root / "fixture")
span = minted["energy_anchor_shift_envelopes"][PREFILL]["wall_minus_monotonic_independent_edge_span_s"]
dur = _phase_durations(minted)
print("phase durations:", {k: round(v, 4) for k, v in dur.items()}, "minted bound", minted_bound, "span", span)
inverting = dur["prefill"] / 2.0 - span + 0.002
non_inverting = dur["prefill"] / 2.0 - span - 0.002
cache = {}
def flat(d, prefix=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items(): out.update(flat(v, f"{prefix}/{k}"))
    elif isinstance(d, list):
        for i, v in enumerate(d): out.update(flat(v, f"{prefix}[{i}]"))
    else: out[prefix] = d
    return out
for label, bound in (("non-inverting", non_inverting), ("inverting", inverting)):
    old = R._rederive_summary_for_authenticated_fiducial_bound(bundle, authenticated_fiducial_bound_s=bound, _instrument_calibration_physics_cache=cache)
    new = W._rederive_operative_summary(bundle, authenticated_fiducial_bound_s=bound, _instrument_calibration_physics_cache=cache)
    rt = json.loads(json.dumps(old))
    print(f"== {label} bound={bound:.5f}: round-trip lossless={rt == old}; new is old={new is old}; new == old={new == old}")
    fo, fn = flat(old), flat(new)
    changed = sorted(set(fo) ^ set(fn) | {k for k in fo if k in fn and fo[k] != fn[k]})
    print("   changed leaf paths:", len(changed))
    for k in changed[:40]: print("     ", k, fo.get(k, "<absent>"), "->", fn.get(k, "<absent>"))
    energies = [k for k in changed if "energy_j" in k and "envelopes" not in k]
    print("   energy figures changed (must be 0):", len(energies))
    if label == "inverting":
        env = new["energy_anchor_shift_envelopes"].get(PREFILL)
        print("   prefill clamped envelope:", env and {k: env[k] for k in ("point_j", "lower_j", "upper_j", "anchor_bound_s")})
        print("   reduce phase_energy_j[prefill] =", new["phase_energy_j"]["prefill"], "minted point_j =", minted["energy_anchor_shift_envelopes"][PREFILL]["point_j"])
        gate = new["window_evidence_precheck"]["phase"]["prefill"]
        print("   prefill gate:", gate["eligible"], gate["reasons"], [w["reasons"] for w in gate["windows"]])
        print("   old prefill gate:", old["window_evidence_precheck"]["phase"]["prefill"]["reasons"])
        print("   global refusals old/new:", W._classify_precheck_refusals(old)[0], W._classify_precheck_refusals(new)[0])
        print("   key order old:", list(old["energy_anchor_shift_envelopes"]))
        print("   key order new:", list(new["energy_anchor_shift_envelopes"]))
tmp.cleanup()
