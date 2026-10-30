"""R2: compare _group_envelope_contributions with the contributions reduce's own
mint passes to _corner_composed_anchor_shift_envelope (recorded by wrapping the
module global in THIS probe process only), on the real 0.5.2 suite fixture."""
import json, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import joulewise.reduce as R
import joulewise.whole_window as W
from joulewise.bundle_read import BundleReader
from tests.test_whole_window_selection import MaxBracketConsumptionTests, _install_synthetic_calibration_defaults

cleanups = []
_install_synthetic_calibration_defaults(SimpleNamespace(addCleanup=cleanups.append))
tmp = Path(tempfile.mkdtemp(prefix="rtwo-"))
bundle, minted, minted_bound, _ = MaxBracketConsumptionTests._build_v052_bundle(tmp)
cache = {}
orig = R._corner_composed_anchor_shift_envelope
calls = []
def rec(contribs, bb, fid, span=0.0):
    calls.append((contribs, (bb, fid, span)))
    return orig(contribs, bb, fid, span)

phase = minted["window_evidence_precheck"]["phase"]
durs = {p: g["windows"][0]["window_duration_s"] for p, g in phase.items()}
print("phase durations", json.dumps(durs, sort_keys=True))
print("minted envelope pointers", sorted(minted["energy_anchor_shift_envelopes"]))
span = minted["energy_anchor_shift_envelopes"]["/gross_energy_j"]["wall_minus_monotonic_independent_edge_span_s"]
bounds = sorted({minted_bound, minted_bound * 1.5} | {d / 2 - span + k for d in durs.values() if d > 0 for k in (-0.002, 0.0, 0.002)})
bounds = [b for b in bounds if b > 0]
bad = 0
for b in bounds:
    calls.clear()
    R._corner_composed_anchor_shift_envelope = rec
    try:
        summ = R._rederive_summary_for_authenticated_fiducial_bound(bundle, authenticated_fiducial_bound_s=b,
                                                                    _instrument_calibration_physics_cache=cache)
    finally:
        R._corner_composed_anchor_shift_envelope = orig
    if summ.get("status") != "succeeded":
        print(f"bound {b!r}: status {summ.get('status')} {summ.get('failure_message','')[:120]}"); continue
    reader = BundleReader(bundle)
    ctx = R._derive_anchor_context(reader, reader.metadata(), strict_calibration=True, reducer_version="0.5.2",
                                   authenticated_fiducial_bound_override_s=b, instrument_calibration_physics_cache=cache)
    rows = W._group_envelope_contributions(reader, "0.5.2", ctx.curve)
    mint_member_calls = calls[1:]  # calls[0] is /gross_energy_j
    bounds_mirror = (ctx.bundle_bound_s, ctx.fiducial_bound_s or 0.0, ctx.edge_span_s)
    same_n = len(rows) == len(mint_member_calls)
    same_contrib = same_n and all(r[1] == c[0] for r, c in zip(rows, mint_member_calls))
    same_bounds = all(c[1] == bounds_mirror for c in calls)
    recorded = set(summ.get("energy_anchor_shift_envelopes") or {})
    pointers = [p for p, _ in rows]
    rec_members = {p for p in recorded if p.startswith(tuple(pre for _k, pre in W._CLAMP_GROUP_PREFIXES))}
    unknown = rec_members - set(pointers)
    missing = [p for p in pointers if p not in recorded]
    ok = same_n and same_contrib and same_bounds and not unknown
    bad += not ok
    new = W._rederive_operative_summary(bundle, authenticated_fiducial_bound_s=b, _instrument_calibration_physics_cache=cache)
    added = sorted(set(new.get("energy_anchor_shift_envelopes") or {}) - recorded)
    print(f"bound {b!r}: mint calls {len(calls)} rows {len(rows)} contrib_equal {same_contrib} bounds_equal {same_bounds} "
          f"unknown_recorded {sorted(unknown)} missing_at_mint {missing} clamp_added {added} ok {ok}")
print("pointer order", pointers)
for c in cleanups: c()
print("RESULT", "FAIL" if bad else "PASS", "bad", bad)
