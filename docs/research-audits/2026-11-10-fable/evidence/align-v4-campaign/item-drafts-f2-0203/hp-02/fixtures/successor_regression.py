"""Timing-only red control or acceptance of an exported successor Start/Run decision map."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import sys

# Support -I (avoid user site, PYTHONPATH and the working-directory import path).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import clocked_occupancy as fixture

CASES = [
    ("noon", "12:00:00", "CEDE_FENCE"),
    ("fence-minus-one", "12:38:29", "CEDE_FENCE"),
    ("fence-equal", "12:38:30", "ELIGIBLE"),
    ("fence-plus-one", "12:38:31", "ELIGIBLE"),
    ("afternoon", "14:00:00", "ELIGIBLE"),
    ("same-arm", "10:54:10", "ELIGIBLE"),
    ("same-arm", "10:54:11", "CEDE_FENCE"),
    ("overnight", "23:59:59", "ELIGIBLE"),
    ("old-band-late-entry", "10:50:00", "CEDE_FENCE"),
    ("unknown-entry", "14:00:00", "WAIT_EVIDENCE"),
]


def vectors():
    for span in fixture.ITEMS:
        for label, wall, want in CASES:
            day = "2026-11-21" if label == "old-band-late-entry" else "2026-11-20"
            t = datetime.fromisoformat(f"{day}T{wall}-08:00")
            phases = ("Start", "Run")
            if label == "same-arm":
                phases = ("Start",) if wall.endswith("10") else ("Run",)
            for phase in phases:
                yield f"{span}/{label}/{phase}", span, label, int(t.timestamp()), want


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--candidate", type=Path, help="JSON object from successor synthetic entry points")
    mode.add_argument("--reference", action="store_true", help="check the composed clock fixture")
    mode.add_argument("--inputs", action="store_true", help="emit inputs for a candidate adapter")
    args = parser.parse_args()
    expected = {}
    observed = {}
    inputs = {}
    for key, span, label, t, want in vectors():
        expected[key] = want
        known = label != "unknown-entry"
        inputs[key] = dict(span=span, phase=key.split("/")[-1], t0=fixture.iso(t),
                           setup_bounds="clocked-profile" if known else None)
        entry_max = 1351 if label == "old-band-late-entry" else None
        if entry_max is not None:
            inputs[key]["selector_sample_max_s_override"] = entry_max
            assert any(lo<=t<=hi and w==fixture.ARGS[0] for lo,hi,w in fixture.ITEMS[span]["bands"])
        if args.inputs or args.candidate:
            continue
        if args.reference:
            observed[key] = fixture.picked(span,t,entry_max)[1]["decision"] if known else "WAIT_EVIDENCE"
        else:
            # Deliberately red: both real planning arguments and existing item
            # deadlines, but only the launcher's minimum-duration test.
            observed[key] = "REFUSE_PLAN"
            for argument in fixture.ARGS:
                p = fixture.plan(span, argument, t)
                if p is not None:
                    if fixture.launcher.cadence_minimum_seconds(p) <= fixture.ITEMS[span]["deadline_s"]:
                        observed[key] = "ELIGIBLE"
                    break
    if args.inputs:
        print(json.dumps({"case_defaults":{
            "all_inputs_synthetic":True,
            "administrative_base":"fixtures/inputs/item-cases.json#/base",
            "queue":"fixture-Q2", "rank":"HP next, all higher entries ineligible",
            "predecessor":"all earlier HP pieces checked clean, current piece wholly unrun, exclusive fence clear",
            "transfer":"verified stopped; no post-fence delay", "dated_pending":[],
            "deadline_s":{"hp-02-s01":18110,"hp-02-s02":20810,"hp-02-s03":23510},
            "clocked-profile":{"runner_start_max_s":60,"selector_sample_max_s":1100,
                "soak_dispatch_max_s":10,"inner_soak_gate_max_s_inside_cap":100,"pre_leg_selector_max_s_per_attempt":12,
                "post_last_cap_max_s":"100 - 10 - 12*(roster_count+2)",
                "all_other_work_overhead_s":0,"restore_and_close_max_s":180,"outer_clear_max_s":190},
            "same-arm":"Start at :10 then fresh Run at :11 on one attempt; other cases are independent"
        },"decisions":inputs}, indent=2))
        return 0
    if args.candidate:
        observed = json.loads(args.candidate.read_bytes())
    failed = [key for key in sorted(set(observed)|set(expected)) if key not in observed or key not in expected
              or observed[key]!=expected[key]]
    for key in failed:
        print(f"{key} expected {expected.get(key)} observed {observed.get(key)}")
    print(f"{'FAIL' if failed else 'PASS'} {len(failed)} mismatches / {len(expected)} decisions; "
          f"subject = {'exported candidate' if args.candidate else 'composed fixture' if args.reference else 'plan-only control'}")
    assert not fixture.NATIVE
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
