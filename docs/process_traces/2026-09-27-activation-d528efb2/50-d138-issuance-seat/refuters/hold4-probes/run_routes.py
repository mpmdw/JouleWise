import safety
import unittest
names = ['tests.test_claim_hold_routes', 'tests.test_claim_hold_census']
def flat(s):
    for x in s:
        if isinstance(x, unittest.TestSuite): yield from flat(x)
        else: yield x
suite = unittest.TestSuite(x for x in flat(unittest.defaultTestLoader.loadTestsFromNames(names)) if not any(x.id().endswith(n) for n in ['test_e7_go_receipt_refuses_claim_on_held_machine','test_e6e_continuation_into_held_build_is_refused']))
result = unittest.TextTestRunner(verbosity=2).run(suite)
print('route_census_without_git_fixture:', result.testsRun, 'PASS' if result.wasSuccessful() else 'FAIL')
raise SystemExit(not result.wasSuccessful())
