"""Reviewer kill-checks run against the (possibly mutated) joulewise.whole_window."""
import json, random, sys, tempfile, traceback
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _oracle_load import load_e1b
import joulewise.reduce as R
from joulewise.bundle_read import TracePoint, Window, BundleReader

UNREC = "anchor_energy_envelope_unrecorded"


def k_r1_mini(W):
    e1b, _ = load_e1b()
    rng = random.Random(7)
    bad = []
    for epoch in (0.0, 1793232000.123456):
        for interval in (True, False):
            dt = 0.05
            curve = [TracePoint(t=epoch + i*dt + (dt/2 if interval else 0), power_w=rng.uniform(1, 9),
                                support_start_s=(epoch + i*dt) if interval else None,
                                support_end_s=(epoch + (i+1)*dt) if interval else None) for i in range(300)]
            neg = list(curve); neg[10] = TracePoint(t=neg[10].t, power_w=-1.0, support_start_s=neg[10].support_start_s, support_end_s=neg[10].support_end_s)
            for edge in (0.03, 0.0656):
                for L in (0.0, 0.01, 2*edge - 1e-9, 2*edge, 2*edge + 1e-9, 0.5, 3.0):
                    s = epoch + 5.0
                    for contribs in ([(curve, [Window(start_s=s, end_s=s+L)])],
                                     [(curve, [Window(start_s=s, end_s=s+L), Window(start_s=s+1, end_s=s+3)])],
                                     [(curve, [Window(start_s=s, end_s=s+L)]), (curve, [Window(start_s=s+4, end_s=s+4.2)])],
                                     [(neg, [Window(start_s=s, end_s=s+L)])],
                                     [(curve, [Window(start_s=epoch+14.99, end_s=epoch+14.99+L)])]):
                        for span in (0.0, 0.0012):
                            a = W._clamped_corner_composed_anchor_shift_envelope(contribs, 0.0005, edge, span)
                            b = e1b._corner_composed_anchor_shift_envelope(contribs, 0.0005, edge, span)
                            if json.dumps(a) != json.dumps(b):
                                bad.append((epoch, interval, edge, L, span))
    return (not bad), f"{len(bad)} mismatches"


def k_r4_restamp(W):
    msgs = []
    g = {"eligible": False, "reasons": [UNREC, "negative_power_sample"], "windows": [{"eligible": False, "reasons": [UNREC, "negative_power_sample"]}]}
    if not W._restamp_clamped_gate(g, ["anchor_energy_envelope_exceeds_quarter_metric"]):
        msgs.append("restamp refused valid gate")
    exp = ["anchor_energy_envelope_exceeds_quarter_metric", "negative_power_sample"]
    if g["reasons"] != exp or g["windows"][0]["reasons"] != exp or g["eligible"] is not False or g["windows"][0]["eligible"] is not False:
        msgs.append(f"restamp result {g}")
    g2 = {"eligible": False, "reasons": ["clock_bound_exceeds_quarter_window"]}
    if W._restamp_clamped_gate(g2, []) or g2 != {"eligible": False, "reasons": ["clock_bound_exceeds_quarter_window"]}:
        msgs.append("restamp accepted gate w/o unrecorded")
    g3 = {"eligible": True, "reasons": [UNREC]}
    if W._restamp_clamped_gate(g3, []):
        msgs.append("restamp accepted eligible gate")
    g4 = {"eligible": False, "reasons": [UNREC]}
    W._restamp_clamped_gate(g4, [])
    if g4.get("eligible") is not False:
        msgs.append("restamp loosened eligibility")
    return (not msgs), "; ".join(msgs) or "ok"


class FakeReader:
    def __init__(self, rng):
        self.raw = {}
        for src in ("meter-b", "meter-a"):
            self.raw[src] = [TracePoint(t=100.0 + i*0.05, power_w=rng.uniform(1, 9), support_start_s=100.0 + i*0.05,
                                        support_end_s=100.05 + i*0.05) for i in range(400)]
        self.rpw = {}
        for src in ("meter-a", "meter-b"):
            for rid in ("r2", "r1", "r3"):
                for ph, (o, d) in {"prefill": (0.0, 0.1), "decode": (0.12, 1.0), "tokenize": (-0.01, 0.0005)}.items():
                    base = 105.0 + int(rid[1]) * 0.6 + (0.3 if src == "meter-b" else 0.0)
                    self.rpw[(src, rid, ph, 0)] = Window(start_s=base + o, end_s=base + o + d)

    def summed_curve(self):
        return self.raw["meter-a"]

    def source_curve(self, src):
        return self.raw[src]

    def request_phase_windows(self):
        return dict(self.rpw)


def k_v062_mirror(W):
    reader = FakeReader(random.Random(3))
    shift = 0.0123
    anchor = R._shift_curve(reader.summed_curve(), shift)
    rows = W._group_envelope_contributions(reader, R.AXI_REDUCER_VERSION, anchor)
    # independent expectation: reduce._reduce_v060 lines (group by (source, phase), union, sort)
    by = {}
    for (src, _rid, ph, _o), w in reader.request_phase_windows().items():
        by.setdefault(ph, {}).setdefault(src, []).append(w)
    exp = []
    for ph in sorted(by):
        exp.append(("/phase_energy_j/" + ph,
                    [(R._shift_curve(reader.source_curve(src), shift), R._union_windows(by[ph][src])) for src in sorted(by[ph])]))
    return rows == exp, f"rows {len(rows)} expected {len(exp)} equal {rows == exp}"


_FIX = {}


def _fixture():
    if not _FIX:
        from tests.test_whole_window_selection import MaxBracketConsumptionTests, _install_synthetic_calibration_defaults
        _install_synthetic_calibration_defaults(SimpleNamespace(addCleanup=lambda f: None))
        root = Path(tempfile.mkdtemp(prefix="rchk-"))
        bundle, minted, mb, _ = MaxBracketConsumptionTests._build_v052_bundle(root)
        _FIX.update(bundle=bundle, minted=minted, mb=mb, cache={})
    return _FIX


def k_fixture(W):
    f = _fixture()
    e1b, _ = load_e1b()
    msgs = []
    for b in (0.068420316696167, 0.1207814474105835, 0.06442031669616699):
        kw = dict(authenticated_fiducial_bound_s=b, _instrument_calibration_physics_cache=f["cache"])
        old = R._rederive_summary_for_authenticated_fiducial_bound(f["bundle"], **kw)
        new = W._rederive_operative_summary(f["bundle"], **kw)
        ora = e1b._rederive_summary_for_authenticated_fiducial_bound(f["bundle"], **kw)
        if json.dumps(new) != json.dumps(ora):
            msgs.append(f"bound {b}: operative != e1b oracle")
        # mirror vs reduce mint calls
        calls = []
        orig = R._corner_composed_anchor_shift_envelope
        R._corner_composed_anchor_shift_envelope = lambda c, *a: (calls.append(c), orig(c, *a))[1]
        try:
            R._rederive_summary_for_authenticated_fiducial_bound(f["bundle"], **kw)
        finally:
            R._corner_composed_anchor_shift_envelope = orig
        reader = BundleReader(f["bundle"])
        ctx = R._derive_anchor_context(reader, reader.metadata(), strict_calibration=True, reducer_version="0.5.2",
                                       authenticated_fiducial_bound_override_s=b, instrument_calibration_physics_cache=f["cache"])
        rows = W._group_envelope_contributions(reader, "0.5.2", ctx.curve)
        if [c for _p, c in rows] != calls[1:]:
            msgs.append(f"bound {b}: mirror rows != reduce mint calls ({len(rows)} vs {len(calls)-1})")
        # unknown recorded member pointer must fail closed
        tam = json.loads(json.dumps(old))
        tam["energy_anchor_shift_envelopes"]["/phase_energy_j/zz_unknown"] = dict(tam["energy_anchor_shift_envelopes"]["/gross_energy_j"])
        if W._clamp_inverted_operative_envelopes(f["bundle"], tam, authenticated_fiducial_bound_s=b,
                                                 instrument_calibration_physics_cache=f["cache"]) is not tam:
            msgs.append(f"bound {b}: unknown recorded member pointer not fail-closed")
        # tail refusal: reduce stamps no envelope reasons -> clamp must not restamp gates
        if b == 0.068420316696167:
            ctx_detail = SimpleNamespace(**{k: getattr(ctx, k) for k in ctx.__dataclass_fields__}) if hasattr(ctx, "__dataclass_fields__") else None
            if ctx_detail is not None:
                ctx_detail.detail = "post_window_trace_tail_shorter_than_anchor_bound"
                real = R._derive_anchor_context
                W._derive_anchor_context = lambda *a, **k: ctx_detail
                try:
                    out = W._clamp_inverted_operative_envelopes(f["bundle"], old, authenticated_fiducial_bound_s=b,
                                                                instrument_calibration_physics_cache=f["cache"])
                finally:
                    W._derive_anchor_context = real
                if out["window_evidence_precheck"] != old["window_evidence_precheck"]:
                    msgs.append("tail-refusal: gates were restamped")
    return (not msgs), "; ".join(msgs) or "ok"


CHECKS = {"K1_r1_mini_oracle": k_r1_mini, "K2_r4_restamp": k_r4_restamp, "K3_v062_mirror": k_v062_mirror,
          "K4_fixture_oracle_mirror_guards": k_fixture}


def run_all(W):
    out = {}
    for name, fn in CHECKS.items():
        try:
            ok, msg = fn(W)
        except Exception as exc:  # noqa: BLE001
            ok, msg = False, f"EXC {type(exc).__name__}: {exc}"[:300]
        out[name] = (ok, msg)
    return out
