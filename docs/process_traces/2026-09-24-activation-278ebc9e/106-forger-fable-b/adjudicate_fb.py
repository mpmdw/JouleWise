import sys, copy, json
sys.path.insert(0, '/tmp/forger-278ebc9e-fable-b')
sys.path.insert(1, '/Users/edr/code/wt-278ebc9e-a291p3')
import forge_final as f
from joulewise import scored_packer as sp
from tests.scored_ownership_oracle import ownership_violations
from tests.scored_roster_checker import check_roster
cands = [("C1 grandchild single", f.c1_grandchild), ("C2a terminal wrong block", f.c2a_terminal_wrong_block),
 ("C2b terminal no placement", f.c2b_terminal_no_placement), ("C3 phantom terminal", f.c3_phantom_terminal),
 ("C4 split-from-initial same env", lambda: f.c4_split_from_initial(False)), ("C4' split-from-initial new env", lambda: f.c4_split_from_initial(True)),
 ("C5 live ceiling_violation", f.c5_live_ceiling_violation), ("C6 event placements", f.c6_event_placements),
 ("C7 single stage initial", f.c7_single_stage_initial), ("X1", f.x1_parent_and_single_both_live), ("X2", f.x2_single_live_twice),
 ("X3", f.x3_terminal_plus_live), ("X4", f.x4_single_of_unsuperseded_parent), ("X5", f.x5_parent_moved_between_cells),
 ("X6", f.x6_missing_single), ("X7", f.x7_grandchild_without_superseding_single),
 ("C1b grandchild new env", f.c1b_grandchild_new_env), ("C2b fixed", f.c2b_terminal_no_placement_fixed),
 ("X7b grandchild new env single not superseded", f.x7b_grandchild_new_env_single_not_superseded)]
reg = f.reg; g = reg.to_mapping(); pred = f.predictions(reg)
for label, fn in cands:
    try:
        r = fn()
    except Exception as e:
        print(json.dumps([label, f"CONSTRUCTOR ERROR {type(e).__name__}: {e}"])); continue
    try:
        out = sp._seal(reg, copy.deepcopy(r), finalize=True); st = 'ACCEPTED'
    except sp.PackingRefusal as e:
        print(json.dumps([label, f"REFUSED {e}"])); continue
    ov = ownership_violations(g, out)
    try:
        rows = sorted({v.inv_id for v in check_roster(g, out, pred)})
    except Exception as e:
        rows = [f'CHECKER-CRASH {type(e).__name__}: {e}']
    try:
        sp.verify_executed_roster(reg, copy.deepcopy(out)) if False else None
    except Exception: pass
    esc = bool(ov) or any(x in ('INV-10','INV-11') for x in rows)
    print(json.dumps([label, st, [str(v)[:100] for v in ov], rows, 'ESCAPE' if esc else 'OUT_OF_ROUND']))
print("REPLAY CHECK")
for label, fn in cands:
    try:
        r = fn(); out = sp._seal(reg, copy.deepcopy(r), finalize=True)
    except Exception:
        continue
    try:
        sp._replay_roster(reg, copy.deepcopy(out)); print(json.dumps([label, "REPLAY ACCEPTED"]))
    except sp.PackingRefusal as e:
        print(json.dumps([label, f"REPLAY REFUSED {str(e)[:80]}"]))
    except Exception as e:
        print(json.dumps([label, f"REPLAY ERROR {type(e).__name__}: {str(e)[:80]}"]))
