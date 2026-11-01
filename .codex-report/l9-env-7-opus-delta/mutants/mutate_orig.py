import sys, pathlib
root = pathlib.Path(sys.argv[1]); name = sys.argv[2]
def sub(rel, old, new):
    p = root / rel; s = p.read_text()
    assert s.count(old) == 1, (name, rel, s.count(old)); p.write_text(s.replace(old, new))
WW = "joulewise/whole_window.py"
GUARD = ("            if _corner_composed_anchor_shift_envelope(\n"
         "                contributions, *bounds\n"
         "            ) is not None:\n"
         "                return summary\n")
if name == "L1": sub("joulewise/analysis_engine/inputs.py", "        mode=mode,\n        analysis_clamp=True,\n", "        mode=mode,\n")
elif name == "L2": sub("joulewise/floor_mint_estimator.py", "        analysis_clamp=True,\n    )\n    reasons = whole_window_refusal_reasons(", "    )\n    reasons = whole_window_refusal_reasons(")
elif name == "L3": sub(WW, GUARD, "")
elif name == "L4": sub(WW, "            if self.analysis_clamp\n", '            if self.analysis_clamp and self.mode != "read_replay"\n')
elif name == "R1": sub(WW, GUARD, "            _probe = _corner_composed_anchor_shift_envelope(\n                contributions, *bounds\n            )\n            if _probe is not None and _probe[\"lower_j\"] > 0.0:\n                return summary\n")
elif name == "R2": sub(WW, "            else _rederive_summary_for_authenticated_fiducial_bound\n        )\n",
                       "            else _rederive_summary_for_authenticated_fiducial_bound\n        )\n        if self.mode == \"read_replay\":\n            rederive = _rederive_summary_for_authenticated_fiducial_bound\n")
elif name == "R3": sub(WW, "        self.analysis_clamp = analysis_clamp is True\n", "        self.analysis_clamp = analysis_clamp is True and archive_context is None\n")
else: raise SystemExit("unknown")
print("mutated", name)
