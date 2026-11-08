"""Delta2: the dynamic execution closure (audit-hook trace) stays inside the strict receipt.

The committed trace is evidence from the repository's own synthetic W1/D/R1 paths
(``scripts/align_v4_dynamic_trace.py``). Strict is the default tier, so a dynamically executed
path must be bound and must not be on the amendment allowlist.
"""
import json
from pathlib import Path
import subprocess
import sys
import unittest

from joulewise.align.apple import v4_registration as registration

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / 'docs/align/v4/dynamic_closure_trace.json'
ALLOWED_CENSUS = {'retired', 'analysis', 'mock', 'other_hardware', 'acceptance', 'desk'}


class CommittedTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace = json.loads(TRACE.read_text())

    def test_the_trace_covers_the_synthetic_w1_r1_and_arm_paths_and_all_passed(self):
        self.assertEqual(self.trace['schema'], 'joulewise.align_v4.dynamic_closure_trace.v1')
        self.assertTrue({'wp22_synthetic_w1_chain', 'r1_synthetic_arm', 'r1_to_w1_chain',
                         'arm_install_session'} <= set(self.trace['scenarios']))
        for name, scenario in self.trace['scenarios'].items():
            self.assertTrue(scenario['ok'], name)
            self.assertGreater(scenario['tests_run'], 0)

    def test_every_dynamically_executed_path_is_bound_and_strict(self):
        executed = set(self.trace['executed'])
        self.assertEqual([p for p in executed if p not in registration.ARTIFACTS], [])
        self.assertEqual([p for p in executed if not registration.is_strict(p)], [])
        self.assertEqual(self.trace['not_bound'], [])
        self.assertEqual(self.trace['not_strict'], [])
        # a child process (the real R1 runtime) is part of the set, not just this process
        self.assertIn('scripts/align_r1_runtime.py', executed)
        self.assertTrue(self.trace['child_process_paths'])

    def test_bulk_reads_are_evidence_only(self):
        self.assertIn('opened', self.trace['by_event'])
        executed = set(self.trace['executed'])
        for bucket in ('compiled', 'exec_targets', 'argv_scripts', 'modules'):
            self.assertTrue(set(self.trace['by_event'][bucket]) <= executed)


class AllowlistTests(unittest.TestCase):
    def test_every_amendable_path_is_a_reviewed_not_executed_class_and_never_traced(self):
        census = json.loads((ROOT / 'configs/gates/hazard_refusals.json').read_text())['scan']['not_scanned']
        executed = set(json.loads(TRACE.read_text())['executed'])
        for path in registration.AMENDMENT_ALLOWLIST:
            with self.subTest(path=path):
                self.assertIn(path, registration.ARTIFACTS)
                self.assertIn(census.get(path), ALLOWED_CENSUS, 'not classified as not-run by the refusal census')
                self.assertNotIn(path, executed)
        self.assertEqual(len(registration.AMENDMENT_ALLOWLIST), len(set(registration.AMENDMENT_ALLOWLIST)))


class IndependentSpineTests(unittest.TestCase):
    def test_launch_spine_inventory_is_bound_and_strict(self):
        for path in registration.STRICT_SCRIPTS:
            with self.subTest(path=path):
                self.assertIn(path, registration.ARTIFACTS)
                self.assertTrue(registration.is_strict(path))

    def test_configured_r1_entry_and_config_are_bound_and_strict(self):
        inputs = json.loads((ROOT / registration.REGISTRATION / 'inputs.json').read_text())
        argv = inputs['WP15']['runtime_entrypoint']
        config = argv[argv.index('--config')+1]
        for path in (argv[0], config):
            self.assertIn(path, registration.ARTIFACTS)
            self.assertTrue(registration.is_strict(path))

    def test_chain_tools_named_by_the_w1_plan_are_bound_and_strict(self):
        from joulewise.b5 import chain
        tree = json.loads((ROOT / 'configs/campaigns/align_v4/plan_tree.json').read_bytes())
        tools = {c['argv_template']['tool_id'] for stage in tree['stage_graph']
                 if stage['kind'] in chain.IN_CHAIN_KINDS for c in stage['launch']['commands']}
        programs = {chain.TOOLS[t].program for t in tools} | {chain.WINDOW_CALIBRATION_VERDICT_PROGRAM}
        self.assertTrue(programs)
        for path in programs:
            with self.subTest(path=path):
                self.assertIn(path, registration.ARTIFACTS)
                self.assertTrue(registration.is_strict(path))

    def test_python_dash_m_launch_targets_are_bound(self):
        from scripts.run_campaign import command_for
        argv = command_for(Path('synthetic.json'), Path('synthetic-runs'), None)
        self.assertEqual(argv[1:3], ['-m', 'joulewise'])
        self.assertIn('joulewise/__main__.py', registration.ARTIFACTS)


class LiveTraceTests(unittest.TestCase):
    def test_a_fresh_process_running_the_minimal_dry_run_stays_inside_the_committed_trace(self):
        code = ('import json\n'
                'from scripts import align_v4_dynamic_trace as t\n'
                'scenario = ("live", {}, ["tests.align.test_v4_w1_synthetic.MinimalDryRunTests"])\n'
                'report, recorder, children = t.run_scenarios([scenario])\n'
                'print("TRACE" + json.dumps({"ok": report["live"]["ok"], "executed": sorted(set(recorder.paths()) | set(children))}))\n')
        result = subprocess.run([sys.executable, '-B', '-c', code], cwd=ROOT, capture_output=True, text=True, timeout=300)
        line = next(l for l in result.stdout.splitlines() if l.startswith('TRACE'))
        live = json.loads(line[5:])
        self.assertTrue(live['ok'], result.stderr[-500:])
        self.assertTrue(live['executed'])
        committed = set(json.loads(TRACE.read_text())['executed'])
        self.assertEqual([p for p in live['executed'] if p not in registration.ARTIFACTS], [])
        self.assertEqual([p for p in live['executed'] if not registration.is_strict(p)], [])
        self.assertEqual([p for p in live['executed'] if p not in committed], [])


if __name__ == '__main__':
    unittest.main()
