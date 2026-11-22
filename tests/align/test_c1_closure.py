"""The frozen acceptance tape and additional prepare/ledger contract cases."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests.align.c1_closure_lite import adapter
from joulewise.align.apple import v4_registration as closure
from scripts import align_v4_session as session


HERE = Path(__file__).parent / 'c1_closure_lite'
ROOT = HERE.parents[2]


class C1ClosureTests(unittest.TestCase):
    def attempt(self):
        work = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.enterContext(patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}))
        for name in ('CALIBRATION_LEDGER', 'LEDGER_HEAD_PIN', 'JOULEWISE_C1_INPUTS'):
            os.environ.pop(name, None)
        subprocess.run(['git', 'clone', '-q', '--bare', HERE / 'suite/history.bundle', work / 'history.git'], check=True)
        return adapter.Attempt(work, 'valid_24_closure', 'copy', None)

    def assert_refuses_before_host(self, attempt, detail):
        from joulewise.align.apple import powermode
        with patch.object(powermode, 'host_marker_path', side_effect=AssertionError('host')) as host:
            with self.assertRaisesRegex(session.PacketKitMismatch, detail):
                session.install(attempt.work / 'install', now=lambda: adapter.NOW, c1_handoff=attempt.handoff_file)
            record = session.arm_checks(attempt.view, attempt.plan, now=lambda: adapter.NOW,
                                        c1_handoff=attempt.handoff_file)
        self.assertFalse(record['admitted'])
        self.assertRegex(record['packet_kit']['detail'], detail)
        host.assert_not_called()

    def test_c2a_finalizer_cannot_pin_a_stray_present_at_finalization(self):
        attempt = self.attempt()
        name = closure.PACK / '.stray-prepared-input'
        adapter.put(attempt.stage, name, b'unused fixture')
        code, packet = attempt.build()
        self.assertEqual(code, 0, attempt.build_error)
        self.assertNotIn(str(name), packet['c1_closure']['stage_files'])
        attempt.deliver(packet)
        self.assert_refuses_before_host(attempt, 'unlisted staged file')

    def test_o2a_separate_same_byte_ledger_refuses_in_a_fully_pinned_stage(self):
        attempt = self.attempt()
        copy = adapter.put(attempt.stage, 'ledger-copy.jsonl', attempt.ledger)
        manifest = attempt.stage / closure.OUTPUTS
        pins = closure.decode(manifest.read_bytes())
        pins['ledger-copy.jsonl'] = closure.digest(attempt.ledger)
        manifest.unlink()
        closure.declare_outputs(attempt.repo, attempt.stage, pins)
        closure.link_launch_view(closure.Roots(attempt.repo, attempt.stage), attempt.view)
        code, packet = attempt.build()
        self.assertEqual(code, 0, attempt.build_error)
        attempt.deliver(packet)
        with patch.dict(os.environ, {'CALIBRATION_LEDGER': str(copy)}):
            self.assert_refuses_before_host(attempt, 'canonical C1 path')
        with adapter.ledger_environment(attempt, packet):
            with self.assertRaisesRegex(ValueError, 'canonical C1 path'):
                closure.runtime_ledger(copy, starting=True)
            with self.assertRaisesRegex(ValueError, 'canonical C1 path'):
                closure.runtime_ledger(copy)
            self.assertEqual(closure.runtime_ledger(attempt.view / adapter.LEDGER), attempt.stage / adapter.LEDGER)

    def test_k1_post_publication_kit_members_and_ordinals_remain_bound(self):
        attempt = self.attempt()
        code, packet = attempt.build()
        self.assertEqual(code, 0, attempt.build_error)
        self.assertEqual(packet['c1_kit']['member_count'], 24)
        self.assertEqual(packet['c1_kit']['sentinel_ordinals'], [5, 22, 23, 24])
        attempt.deliver(packet)
        plan = attempt.repo / adapter.KIT / 'collection_plan.json'
        raw = plan.read_bytes()
        for delta in (-2, -1, 0, 1, 2):
            with self.subTest(delta=delta):
                updated = json.loads(raw)
                members = updated['members']
                if delta < 0:
                    del members[delta:]
                elif delta > 0:
                    members.extend(members[-delta:])
                else:
                    members[22], members[23] = members[23], members[22]
                plan.write_bytes(adapter.series.raw_json(updated))
                self.assert_refuses_before_host(attempt, 'repository blob mismatch')
        plan.write_bytes(raw)
        leaf = next((attempt.repo / adapter.KIT / 'registration').glob('*.json'))
        leaf.write_bytes(leaf.read_bytes() + b' ')
        self.assert_refuses_before_host(attempt, 'repository blob mismatch')

    def test_k2_each_stage_order_rejects_modified_bytes_or_order(self):
        attempt = self.attempt()
        code, packet = attempt.build()
        self.assertEqual(code, 0, attempt.build_error)
        attempt.deliver(packet)
        for dispatch in packet['c1_kit']['execution']['order_manifests']:
            relative = closure.PACK / 'members' / dispatch['stage_id'] / 'order_manifest.json'
            path = attempt.stage / relative
            raw = path.read_bytes()
            order = json.loads(raw)
            order['executed_order'].reverse()
            for changed in (raw + b' ', adapter.series.raw_json(order)):
                with self.subTest(stage=dispatch['stage_id']):
                    path.write_bytes(changed)
                    self.assert_refuses_before_host(attempt, 'staged SHA-256 mismatch')
            path.write_bytes(raw)

    def test_frozen_lite_decisions(self):
        completed = subprocess.run([sys.executable, '-B', str(HERE / 'suite/run.py'),
                                    '--adapter', str(HERE / 'adapter.py')], cwd=ROOT,
                                   env={**os.environ, 'PYTHONPATH': os.pathsep.join([str(ROOT / 'tests'), str(ROOT)])},
                                   capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, (HERE / 'suite/expected.jsonl').read_bytes())
