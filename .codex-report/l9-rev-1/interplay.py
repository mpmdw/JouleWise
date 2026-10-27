"""Tripwire x shared cache through the real step_2 + StepRunner (harness from the lane's own test)."""
import json, unittest
from joulewise import whole_window as ww
from tests.b5_analysis import test_deadline_tripwire as t


def main():
    case = t.DeadlineTripwireTests('test_driver_stops_at_the_refused_step')
    t.DeadlineTripwireTests.setUpClass()
    R = {}
    with ww.shared_instrument_calibration_physics_cache({}) as cache:   # cold run cache, firing on call 1
        state, root, rec = case.step_2(forced_calls=(1,))
        R['cold_forced_call1'] = dict(records=[(r['status'], r['refusal']) for r in rec], outputs=list(state.outputs), cache=len(cache))
    with ww.shared_instrument_calibration_physics_cache({}) as cache:   # warm (as after step 1), firing on call 2
        t.quiet_cli('validate-bundle', '--strict', case.member)
        state, root, rec = case.step_2(forced_calls=(2,))
        R['warm_forced_call2'] = dict(records=[(r['status'], r['refusal']) for r in rec], outputs=list(state.outputs), cache=len(cache))
        _, root2, rec2 = case.step_2(forced_calls=())
        R['warm_forced_equals_unforced'] = rec == rec2 and all(
            (root / o['name']).read_bytes() == (root2 / o['name']).read_bytes() for o in rec[0]['outputs'])
    t.DeadlineTripwireTests.tmp.cleanup()
    print(json.dumps(R, indent=1))


if __name__ == '__main__':
    main()
