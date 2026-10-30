"""R4: gate restamp behaviour, incl. a multi-window phase whose clamped envelope passes the
quarter-metric gate (refutes L9-ENV-3 NEEDS_RULING R2 'only all-zero-power')."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import joulewise.reduce as R
import joulewise.whole_window as W
from joulewise.bundle_read import TracePoint, Window

dt = 0.1
curve = [TracePoint(t=i*dt + dt/2, power_w=10.0, support_start_s=i*dt, support_end_s=(i+1)*dt) for i in range(400)]
edge = 0.0656
# decode of a 5-item suite: four 2 s items and one 0.1 s item (< 2*edge = 0.1312 s)
ws = [Window(start_s=1.0 + 3*k, end_s=3.0 + 3*k) for k in range(4)] + [Window(start_s=20.0, end_s=20.1)]
mint = R._corner_composed_anchor_shift_envelope([(curve, ws)], 0.0005, edge, 0.0)
clamped = W._clamped_corner_composed_anchor_shift_envelope([(curve, ws)], 0.0005, edge, 0.0)
print("mint envelope:", mint)
print("clamped envelope:", json.dumps(clamped, sort_keys=True))
reasons = R._anchor_envelope_gate_reasons(clamped, 0.0)
print("clamped gate reasons (joint 0.0):", reasons)
gate = {"eligible": False, "reasons": ["anchor_energy_envelope_unrecorded"],
        "windows": [{"eligible": False, "reasons": ["anchor_energy_envelope_unrecorded"]}]}
ok = W._restamp_clamped_gate(gate, reasons)
print("restamp ok", ok, "gate after:", json.dumps(gate, sort_keys=True))
summary = {"window_evidence_precheck": {"gross_request": {"eligible": True, "reasons": []},
                                        "idle_subtracted_request": {"eligible": True, "reasons": []},
                                        "phase": {"decode": gate}},
           "phase_energy_j": {"decode": 1.0}}
print("session _classify_precheck_refusals:", W._classify_precheck_refusals(summary))
from joulewise.analysis_engine import inputs as AI
src = Path(AI.__file__).read_text()
print("analysis_engine treats eligible False + [] as:",
      "window_evidence_precheck_missing" if "A failed boolean without a governed reason" in src else "?")
# e1b3a0510's reducer would stamp no reason -> eligible stays True when nothing else refuses
# restamp of a gate WITHOUT unrecorded -> fail closed
g2 = {"eligible": False, "reasons": ["clock_bound_exceeds_quarter_window"]}
print("restamp without unrecorded ->", W._restamp_clamped_gate(g2, reasons), g2)
g3 = {"eligible": True, "reasons": ["anchor_energy_envelope_unrecorded"]}
print("restamp of eligible gate ->", W._restamp_clamped_gate(g3, reasons), g3)
g4 = {"eligible": False, "reasons": ["anchor_energy_envelope_unrecorded", "negative_power_sample"]}
W._restamp_clamped_gate(g4, ["anchor_energy_envelope_exceeds_quarter_metric"])
print("other reasons kept ->", g4)
