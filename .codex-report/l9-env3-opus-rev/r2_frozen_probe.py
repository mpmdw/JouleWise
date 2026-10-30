"""R2 frozen arms: the clamp never touches 0.5.1/0.6.1 (or older) re-derivations."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import joulewise.whole_window as W
for v in ("0.5.0", "0.5.1", "0.6.0", "0.6.1", "0.5.2", "0.6.2"):
    s = {"status": "succeeded", "summary_provenance": {"reducer_version": v}, "energy_anchor_shift_envelopes": {}}
    out = W._clamp_inverted_operative_envelopes(Path("/nonexistent-bundle"), s, authenticated_fiducial_bound_s=0.07)
    print(v, "reducer_version parsed:", W._summary_reducer_version(s), "returned same object:", out is s)
