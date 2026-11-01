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
CALL = ("                    operative_summary = (\n"
        "                        rederive(\n")
if name == "R4":  # F1: narrow at the call site on archive context; no rebind, no flag store, IfExp text intact
    sub(WW, CALL, "                    operative_summary = (\n"
                  "                        (rederive if self._archive_context is None\n"
                  "                         else _rederive_summary_for_authenticated_fiducial_bound)(\n")
elif name == "R5":  # F2: truthiness slip on lower_j
    sub(WW, GUARD, "            _probe = _corner_composed_anchor_shift_envelope(\n                contributions, *bounds\n            )\n            if _probe is not None and _probe.get(\"lower_j\"):\n                return summary\n")
elif name == "R6":  # F1: same narrowing as R4 but keyed on mode at the call site
    sub(WW, CALL, "                    operative_summary = (\n"
                  "                        (rederive if self.mode != \"read_replay\"\n"
                  "                         else _rederive_summary_for_authenticated_fiducial_bound)(\n")
elif name == "R7":  # F2: guard only when the unclamped mint is strictly wider than zero at both ends
    sub(WW, GUARD, "            _probe = _corner_composed_anchor_shift_envelope(\n                contributions, *bounds\n            )\n            if _probe is not None and min(_probe[\"lower_j\"], _probe[\"upper_j\"]) > 0.0:\n                return summary\n")
else: raise SystemExit("unknown")
print("mutated", name)
