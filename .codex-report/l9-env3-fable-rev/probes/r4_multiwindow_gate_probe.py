"""R4 edge: a multi-interval phase where one interval inverts and the clamped envelope passes the quarter-metric gate.
Shows the analysis-side restamp leaves {eligible: False, reasons: []} where e1b3a0510's reduce would stamp nothing (gate eligible)."""
import sys, json
from pathlib import Path
ROOT = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(ROOT))
import joulewise.reduce as R, joulewise.whole_window as W
from joulewise.bundle_read import TracePoint, Window
from tests.test_whole_window_inverted_corner_clamp import oracle_module
curve = [TracePoint(t=-5+(i+0.5)*0.05, power_w=10.0, support_start_s=-5+i*0.05, support_end_s=-5+(i+1)*0.05) for i in range(400)]  # -5 .. 15 s, flat 10 W
g = 0.02; bb = 0.005
for short_d, long_d in ((0.005, 2.0), (0.03, 1.0), (0.001, 8.0)):
    wins = [Window(0.5, 0.5 + short_d), Window(3.0, 3.0 + long_d)]
    origin = R._corner_composed_anchor_shift_envelope([(curve, wins)], bb, g, 0.0)
    clamped = W._clamped_corner_composed_anchor_shift_envelope([(curve, wins)], bb, g, 0.0)
    oracle = oracle_module()._corner_composed_anchor_shift_envelope([(curve, wins)], bb, g, 0.0)
    reasons = R._anchor_envelope_gate_reasons(clamped, None)
    gate_before = {"eligible": False, "reasons": ["anchor_energy_envelope_unrecorded"]}  # what reduce stamps at origin/main for the omitted pointer
    gate = json.loads(json.dumps(gate_before)); W._restamp_clamped_gate(gate, reasons)
    # what e1b3a0510 does: the gate before the envelope merge is eligible with no reasons; _merge_gate_reasons([]) is a no-op
    oracle_gate = {"eligible": True, "reasons": []}; R._merge_gate_reasons(oracle_gate, R._anchor_envelope_gate_reasons(oracle, None))
    print(f"short={short_d}s long={long_d}s 2g={2*g}: origin/main={origin is not None and 'defined' or 'None'}; clamped == oracle: {clamped == oracle}; "
          f"point={clamped['point_j']:.4f} lower={clamped['lower_j']:.4f} upper={clamped['upper_j']:.4f} ratio={(max(clamped['point_j']-clamped['lower_j'], clamped['upper_j']-clamped['point_j'])/clamped['point_j']):.4f}")
    print(f"   clamped-envelope gate reasons: {reasons}; analysis-side gate after restamp: {gate}; e1b3a0510 gate: {oracle_gate}")
    print(f"   _classify_precheck_refusals sees reasons -> {'no refusal' if not gate['reasons'] else gate['reasons']}; analysis_engine.inputs: eligible False + no reasons -> window_evidence_precheck_missing")
