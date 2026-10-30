"""RC-CMP10-FABLE-REV FS4 probes at 1affc4208 (synthetic only): history lines keyed on the window index; the two
lines conditional on L9's own line (question 4)."""
import copy
import sys

sys.path.insert(0, "/home/user/JouleWise")
from tests.independent_recompute import producer_fixtures, test_rc_cmp10  # noqa: E402
from tests.independent_recompute.test_comparator import cmp, item  # noqa: E402
from tests.independent_recompute.test_input_gate import CODED  # noqa: E402
from tests.independent_recompute.test_rc_cmp10 import HISTORY, attempt, history_case  # noqa: E402
from tests.independent_recompute.test_review_fixes import DISCLOSURE  # noqa: E402


class P(test_rc_cmp10.Case):
    def runTest(self):
        pass


def run(c):
    try:
        code, err, out = c.exit_code(CODED)
    except cmp.Refusal as exc:
        return 2, f"refused={exc}", {}
    return code, err.strip(), out


def show(label, attempts=HISTORY, records=None, edit=None, after=None):
    c = P(); c.base()
    with history_case(c, attempts, records, edit):
        if after:
            after(c)
        code, err, out = run(c)
    bad = [r for r in out.get("comparisons", []) if r["verdict"] != "AGREE"][:4]
    print(f"{label}: exit={code} err={err!r}" + (" rows: " + "; ".join(r["key"] for r in bad) if bad else ""))
    return code


RECORDS = {"plan-beta": {"g10_codes": {"g10.redraw": 1}}}
show("H0 control (6-attempt index, G10 requested on plan-beta with codes)", records=RECORDS)
# g10 for an attempt the index does not request: printed from the archive's flag codes (conditional on L9's line).
UNREQ = dict(RECORDS, **{"plan-alpha": {"g10_codes": {"g10.redraw": 4, "g10.other": 1}}})
show("H1 an unrequested g10 line (plan-alpha, codes from the archive, redraw_cycles null as the index)", records=UNREQ)


def set_g10(plan, **fields):
    def edit(lines):
        line = next(l for l in lines if l["line"] == "g10" and l["plan_id"] == plan)
        line.update(fields)
    return edit


show("H2 the unrequested g10 line's redraw_cycles 7 against the index's null", records=UNREQ, edit=set_g10("plan-alpha", redraw_cycles=7))
show("H3 the unrequested g10 line's codes changed (g10.redraw 40, a code added)", records=UNREQ,
     edit=set_g10("plan-alpha", codes={"g10.redraw": 40, "g10.invented": 2}))
show("H3b the requested g10 line's codes emptied", records=RECORDS, edit=set_g10("plan-beta", codes={}))


def add_line(**fields):
    def edit(lines):
        lines.append(item(fields.pop("line"), False, "x", **fields))
    return edit


show("H4 a g10 line for a plan the index lacks", records=RECORDS,
     edit=add_line(line="g10", pack="alpha", plan_id="plan-nowhere", codes={}, redraw_cycles=None))
show("H5 the requested g10 line printed twice", records=RECORDS,
     edit=lambda lines: lines.append(copy.deepcopy(next(l for l in lines if l["line"] == "g10"))))
show("H6 a g10 line for a registered plan under the wrong pack", records=RECORDS,
     edit=add_line(line="g10", pack="gamma", plan_id="plan-alpha", codes={}, redraw_cycles=None))


def harvest_twice(c, accounts):
    lines = c.files[DISCLOSURE]["block_lines"]
    next(l for l in lines if l["line"] == "harvest_once")["no_analysed_window_harvested_twice"] = False
    for a in accounts:
        lines.append(item("reharvest_account", False, "x", **dict(dict(pack="alpha", original_pin="a", deciding_pin="b",
                     original_harvest_sha256="ab" * 32, deciding_harvest_sha256="cd" * 32, reason="r",
                     survivors_before=3, survivors_after=2), **a)))


show("H7 harvest_once false, one alpha re-harvest account", after=lambda c: harvest_twice(c, [{}]))
show("H8 the account's survivors and reason changed (12 -> 1, reason 'because')",
     after=lambda c: harvest_twice(c, [dict(survivors_before=12, survivors_after=1, reason="because")]))
show("H9 two accounts for alpha", after=lambda c: harvest_twice(c, [{}, dict(original_pin="c")]))
show("H10 an account for an unregistered pack", after=lambda c: harvest_twice(c, [dict(pack="delta")]))
show("H11 harvest_once false, no account at all", after=lambda c: harvest_twice(c, []))
show("H12 accounts for alpha and beta", after=lambda c: harvest_twice(c, [{}, dict(pack="beta")]))
# attempt_history / attempt_count against the index: the index is what L9's record names.
show("H13 attempt_history verdict COLLECTED where the index says HARVEST_FAULT (beta a1)",
     edit=lambda lines: next(l for l in lines if l["line"] == "attempt_history" and l["plan_id"] == "plan-beta-a1").update(verdict="COLLECTED"))
show("H14 attempt_count causes reordered (alpha superseded: [NEG8+cell.below_minimum, null] -> [null, NEG8+...])",
     edit=lambda lines: next(l for l in lines if l["line"] == "attempt_count" and l["pack"] == "alpha" and l["superseded"]).update(causes=[None, "NEG8+cell.below_minimum"]))
# The recompute's side plays no part in the history rows beyond the window anchor.
show("H15 the recompute's windows/ALPHA removed (anchor)", after=lambda c: c.ours["windows"].pop("ALPHA"))
