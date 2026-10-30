"""F1 probe: simulate a per-pointer mirror discrepancy on an OMITTED pointer only.
`_group_envelope_contributions` is wrapped so that the prefill row's window is
stretched to 0.14 s (just over 2*edge at the inverting bound) while every
recorded row is untouched (so the O-F3 proof still passes).  reduce omitted
prefill (it inverts); the mirror's reduce call now defines an UNCLAMPED
envelope (lower_j > 0) that exceeds the quarter gate, and the clamp adds it.
With the proposed one-line guard the summary would be returned unchanged."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, ".")
import joulewise.whole_window as W
import joulewise.reduce as R
from joulewise.bundle_read import Window
from tests.test_whole_window_inverted_corner_clamp import _bundle_fixture, _phase_durations, PREFILL
class T(unittest.TestCase):
    def runTest(self): pass
tmp = tempfile.TemporaryDirectory(); root = Path(tmp.name)
bundle, minted, minted_bound = _bundle_fixture(T(), root / "fixture")
span = minted["energy_anchor_shift_envelopes"][PREFILL]["wall_minus_monotonic_independent_edge_span_s"]
bound = _phase_durations(minted)["prefill"] / 2.0 - span + 0.002   # prefill inverts here
orig = W._group_envelope_contributions
def skewed(reader, version, curve):
    rows = orig(reader, version, curve)
    out = []
    for pointer, contribs in rows:
        if pointer == PREFILL:
            (c, ws), = contribs
            ws = [Window(start_s=w.start_s, end_s=w.start_s + 0.14) for w in ws]
            contribs = [(c, ws)]
        out.append((pointer, contribs))
    return out
W._group_envelope_contributions = skewed
old = R._rederive_summary_for_authenticated_fiducial_bound(bundle, authenticated_fiducial_bound_s=bound)
new = W._rederive_operative_summary(bundle, authenticated_fiducial_bound_s=bound)
env = new["energy_anchor_shift_envelopes"].get(PREFILL)
print("reduce omitted prefill:", PREFILL not in (old.get("energy_anchor_shift_envelopes") or {}))
print("clamp added prefill envelope:", env is not None, "lower_j =", env and env["lower_j"], "(unclamped: lower_j > 0)")
print("prefill gate reasons:", new["window_evidence_precheck"]["phase"]["prefill"]["reasons"])
tmp.cleanup()
