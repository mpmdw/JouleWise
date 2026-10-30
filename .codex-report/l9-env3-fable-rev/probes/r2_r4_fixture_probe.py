"""R2/R4 on real powermetrics fixtures: 0.5.2 (d078_r01 + suite shape) and 0.6.2 (AXI event-v2 bound to the same bytes).
Usage: python r2_r4_fixture_probe.py <ROOT> <workdir>"""
import json, math, sys, os
from pathlib import Path
from types import SimpleNamespace
ROOT = Path(sys.argv[1]).resolve(); WORK = Path(sys.argv[2]).resolve()
os.chdir(ROOT); sys.path.insert(0, str(ROOT))
import joulewise.reduce as R
import joulewise.whole_window as W
from joulewise.bundle_read import BundleReader
from tests.test_whole_window_inverted_corner_clamp import oracle_module, pristine_module
from tests.test_whole_window_selection import MaxBracketConsumptionTests, _install_synthetic_calibration_defaults

cleanups = []
_install_synthetic_calibration_defaults(SimpleNamespace(addCleanup=cleanups.append))
(WORK / "fixture").mkdir(parents=True, exist_ok=True)
bundle52, minted52, minted_bound, _ = MaxBracketConsumptionTests._build_v052_bundle(WORK / "fixture")
cache = MaxBracketConsumptionTests._physics_cache
bundle62 = MaxBracketConsumptionTests._install_axi_shape(WORK / "axi-v062", calibrated_source=bundle52)
minted62 = R.reduce_bundle(bundle62, reducer_version="0.6.2", _instrument_calibration_physics_cache=cache).to_dict()
(bundle62 / "summary_metrics.json").write_text(json.dumps(minted62, sort_keys=True) + "\n", encoding="utf-8")
fails = []; notes = []
def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond: fails.append(msg)
GROUP = tuple(p for _k, p in W._CLAMP_GROUP_PREFIXES)

def mint_identity(bundle, minted, version):
    cur = R.reduce_bundle(bundle, reducer_version=version, _instrument_calibration_physics_cache=cache).to_dict()
    pri = pristine_module().reduce_bundle(bundle, reducer_version=version, _instrument_calibration_physics_cache=cache).to_dict()
    check(json.dumps(cur) == json.dumps(pri) == json.dumps(minted), f"R3 mint {version}: branch reduce_bundle == pristine origin/main bytes == stored mint (json bytes)")

def durations(summary):
    return {p: [w["window_duration_s"] for w in rec.get("windows", [])] for p, rec in summary["window_evidence_precheck"]["phase"].items()}

def run(bundle, minted, version, bounds):
    print(f"\n===== {version}  bundle={bundle.name}")
    print("phase window durations:", durations(minted))
    print("minted envelope pointers:", sorted(minted.get("energy_anchor_shift_envelopes", {})))
    reader = BundleReader(bundle)
    if version == "0.6.2":
        rpw = reader.request_phase_windows()
        print("request_phase_windows keys:", sorted(rpw))
    for b in bounds:
        kw = dict(authenticated_fiducial_bound_s=b, _instrument_calibration_physics_cache=cache)
        old = R._rederive_summary_for_authenticated_fiducial_bound(bundle, **kw)
        new = W._rederive_operative_summary(bundle, **kw)
        orc = oracle_module()._rederive_summary_for_authenticated_fiducial_bound(bundle, **kw)
        tag = f"{version} bound={b:.6f}"
        check(old["status"] == new["status"] == orc["status"] == "succeeded", f"{tag}: all three succeeded")
        same_dict = new == orc; same_bytes = json.dumps(new) == json.dumps(orc)
        check(same_dict, f"{tag}: analysis summary == oracle summary (dict equality)")
        if same_dict and not same_bytes:
            notes.append(f"{tag}: dict-equal to oracle but JSON key order differs (reducer recorded no envelope map; analysis appends the key)")
            print("NOTE " + notes[-1])
        if not same_dict:
            for k in set(new) | set(orc):
                if new.get(k) != orc.get(k): print("   diff key:", k, json.dumps(new.get(k))[:300], "||", json.dumps(orc.get(k))[:300])
        ctx = R._derive_anchor_context(reader, reader.metadata(), strict_calibration=True, reducer_version=version,
                                       authenticated_fiducial_bound_override_s=b, instrument_calibration_physics_cache=cache)
        print(f"   {tag}: anchor detail={ctx.detail} unresolved={ctx.unresolved} g={ (ctx.fiducial_bound_s or 0)+ctx.edge_span_s :.6f} 2g={2*((ctx.fiducial_bound_s or 0)+ctx.edge_span_s):.6f}")
        if ctx.unresolved:
            check(new is old or json.dumps(new) == json.dumps(old), f"{tag}: unresolved anchor -> analysis summary unchanged"); continue
        rows = W._group_envelope_contributions(reader, version, ctx.curve)
        bnds = (ctx.bundle_bound_s, ctx.fiducial_bound_s or 0.0, ctx.edge_span_s)
        old_env = old.get("energy_anchor_shift_envelopes", {}); new_env = new.get("energy_anchor_shift_envelopes", {})
        mirror_ptrs = [p for p, _ in rows]
        rec_group = [p for p in old_env if p.startswith(GROUP)]
        check(set(rec_group) <= set(mirror_ptrs), f"{tag}: every recorded group pointer is produced by the mirror ({len(rec_group)} recorded / {len(mirror_ptrs)} mirrored)")
        check([p for p in mirror_ptrs if p in old_env] == rec_group, f"{tag}: mirror order == reduce mint order for recorded group pointers")
        for p, contribs in rows:
            via_reduce = R._corner_composed_anchor_shift_envelope(contribs, *bnds)
            if p in old_env:
                check(via_reduce == old_env[p] and json.dumps(via_reduce) == json.dumps(old_env[p]), f"{tag}: {p}: reduce(mirror windows) == minted envelope")
            else:
                check(via_reduce is None, f"{tag}: {p}: omitted by reduce and reduce(mirror windows) is None too")
                expect = W._clamped_corner_composed_anchor_shift_envelope(contribs, *bnds)
                check((p in new_env) == (expect is not None) and (expect is None or json.dumps(new_env[p]) == json.dumps(expect)), f"{tag}: {p}: clamp applied exactly when the clamped function defines an envelope, with that envelope")
                if p in new_env:
                    check(new_env[p]["lower_j"] == 0.0 or len(contribs) > 1 or len(contribs[0][1]) > 1, f"{tag}: {p}: clamped (lower_j={new_env[p]['lower_j']})")
                else:
                    print(f"   {tag}: {p}: not clamped either (clamped function None: coverage/guard)")
        for p in old_env:
            if not p.startswith(GROUP):
                check(json.dumps(new_env[p]) == json.dumps(old_env[p]), f"{tag}: {p} gross-family untouched")
        added = set(new_env) - set(old_env)
        check(added <= set(mirror_ptrs), f"{tag}: every added pointer comes from the mirror: {sorted(added)}")
        resolved_refusal = ctx.detail == "post_window_trace_tail_shorter_than_anchor_bound"
        for grp, prefix in W._CLAMP_GROUP_PREFIXES:
            for member, gate in old["window_evidence_precheck"].get(grp, {}).items():
                ptr = prefix + R._json_pointer_token(str(member))
                ng = new["window_evidence_precheck"][grp][member]; og = orc["window_evidence_precheck"][grp][member]
                if ptr in added and not resolved_refusal:
                    check("anchor_energy_envelope_unrecorded" in gate["reasons"] and "anchor_energy_envelope_unrecorded" not in ng["reasons"], f"{tag}: {ptr}: unrecorded removed from restamped gate")
                    check(set(gate["reasons"]) - {"anchor_energy_envelope_unrecorded"} <= set(ng["reasons"]), f"{tag}: {ptr}: no other reason dropped")
                    check(set(ng["reasons"]) - set(gate["reasons"]) <= {"anchor_energy_envelope_exceeds_quarter_metric"}, f"{tag}: {ptr}: only exceeds_quarter added: {sorted(set(ng['reasons']) - set(gate['reasons']))}")
                    check(ng["eligible"] is False, f"{tag}: {ptr}: still ineligible")
                    check(json.dumps(ng) == json.dumps(og), f"{tag}: {ptr}: gate == oracle gate")
                    for inner in ng.get("windows", []):
                        check("anchor_energy_envelope_unrecorded" not in inner["reasons"] and inner["eligible"] is False, f"{tag}: {ptr}: inner window restamped and ineligible")
                else:
                    check(json.dumps(ng) == json.dumps(gate), f"{tag}: {ptr}: gate untouched")
        for key in ("gross_request", "gross_batch_group", "idle_subtracted_request"):
            if key in old["window_evidence_precheck"]:
                check(json.dumps(new["window_evidence_precheck"][key]) == json.dumps(old["window_evidence_precheck"][key]), f"{tag}: {key} gate untouched")
        go, lo = W._classify_precheck_refusals(old); gn, ln = W._classify_precheck_refusals(new); gc, lc = W._classify_precheck_refusals(orc)
        check(go == gn == gc, f"{tag}: global classification equal old/new/oracle: {sorted(go)}")
        check(ln == lc, f"{tag}: local classification new == oracle")
        print(f"   {tag}: added={sorted(added)}")
        for path in sorted(set(lo) | set(ln)):
            if lo.get(path) != ln.get(path): print(f"      local {path}: old={lo.get(path)} new={ln.get(path)}")

mint_identity(bundle52, minted52, "0.5.2"); mint_identity(bundle62, minted62, "0.6.2")
span = minted52["energy_anchor_shift_envelopes"]["/phase_energy_j/prefill"]["wall_minus_monotonic_independent_edge_span_s"]
D = durations(minted52)["prefill"][0]; crit = D/2 - span
print("minted bound", minted_bound, "span", span, "prefill D", D, "critical operative bound", crit)
run(bundle52, minted52, "0.5.2", sorted({minted_bound, minted_bound*1.2, crit-0.004, crit-1e-6, crit, crit+1e-6, crit+0.004, crit*1.5, crit*3}))
D62 = durations(minted62); print("0.6.2 durations", D62)
dmin = min(min(v) for v in D62.values() if v); crit62 = dmin/2 - span
run(bundle62, minted62, "0.6.2", sorted({minted_bound, minted_bound*1.2, crit62-0.002, crit62+0.002, crit62*1.5, crit62*3}))

# fail-closed and edge checks (0.5.2, prefill just under 2g: operative bound just over the critical bound)
b = crit + 0.004
kw = dict(authenticated_fiducial_bound_s=b, instrument_calibration_physics_cache=cache)
old = R._rederive_summary_for_authenticated_fiducial_bound(bundle52, authenticated_fiducial_bound_s=b, _instrument_calibration_physics_cache=cache)
check("/phase_energy_j/prefill" not in old["energy_anchor_shift_envelopes"] and "/phase_energy_j/prefill" in W._clamp_inverted_operative_envelopes(bundle52, old, **kw)["energy_anchor_shift_envelopes"], "edge setup: prefill inverts at this bound and is clamped")
foreign = json.loads(json.dumps(old)); foreign["energy_anchor_shift_envelopes"]["/phase_energy_j/ghost"] = foreign["energy_anchor_shift_envelopes"]["/phase_energy_j/decode"]
check(W._clamp_inverted_operative_envelopes(bundle52, foreign, **kw) is foreign, "R2: unknown recorded group pointer -> summary returned unchanged (fail closed)")
t = json.loads(json.dumps(old)); e = t["energy_anchor_shift_envelopes"]["/phase_energy_j/decode"]; e["lower_j"] = math.nextafter(e["lower_j"], 0)
check(W._clamp_inverted_operative_envelopes(bundle52, t, **kw) is t, "R2: one-ulp tamper of a recorded envelope -> fail closed")
g = json.loads(json.dumps(old)); pg = g["window_evidence_precheck"]["phase"]["prefill"]; pg["reasons"] = [r for r in pg["reasons"] if r != "anchor_energy_envelope_unrecorded"]
check(W._clamp_inverted_operative_envelopes(bundle52, g, **kw) is g, "R4: prefill gate without the unrecorded stamp -> fail closed")
g2 = json.loads(json.dumps(old)); g2["window_evidence_precheck"]["phase"]["prefill"]["eligible"] = True
check(W._clamp_inverted_operative_envelopes(bundle52, g2, **kw) is g2, "R4: prefill gate eligible=True -> fail closed")
g3 = json.loads(json.dumps(old)); g3["window_evidence_precheck"]["phase"]["prefill"]["windows"][0]["reasons"] = []
check(W._clamp_inverted_operative_envelopes(bundle52, g3, **kw) is g3, "R4: inner window without the unrecorded stamp -> fail closed")
f = json.loads(json.dumps(old)); f["summary_provenance"]["reducer_version"] = "0.5.1"
check(W._clamp_inverted_operative_envelopes(bundle52, f, **kw) is f, "frozen 0.5.1 summary -> untouched")
f = json.loads(json.dumps(old)); f["status"] = "failed"
check(W._clamp_inverted_operative_envelopes(bundle52, f, **kw) is f, "failed summary -> untouched")
f = json.loads(json.dumps(old)); f["energy_anchor_shift_envelopes"] = []
check(W._clamp_inverted_operative_envelopes(bundle52, f, **kw) is f, "non-mapping envelope map -> untouched")
check(W._clamp_inverted_operative_envelopes(WORK / "absent", old, **kw) is old, "unreadable bundle path -> untouched")
# the override below the mint bound is refused by reduce (unresolved) -> analysis untouched
low = R._rederive_summary_for_authenticated_fiducial_bound(bundle52, authenticated_fiducial_bound_s=minted_bound*0.5, _instrument_calibration_physics_cache=cache)
lown = W._rederive_operative_summary(bundle52, authenticated_fiducial_bound_s=minted_bound*0.5, _instrument_calibration_physics_cache=cache)
check(json.dumps(low) == json.dumps(lown), "override narrower than the mint bound: analysis == reduce (both unresolved)")
gate = {"eligible": False, "reasons": ["anchor_energy_envelope_unrecorded"]}
W._restamp_clamped_gate(gate, [])
print("restamp with empty clamped reasons ->", gate)
check(gate == {"eligible": False, "reasons": []}, "R4-edge (documented): empty clamped reasons -> eligible False with reasons [] (oracle would leave such a gate eligible)")
print("\nNOTES:"); [print("  -", n) for n in notes]
print("FAILS:", len(fails)); [print("  -", m) for m in fails]
print("RESULT:", "PASS" if not fails else "FAIL")
