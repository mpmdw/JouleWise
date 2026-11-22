"""The frozen acceptance tape and additional prepare/ledger contract cases."""
from functools import partial
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
from scripts import align_v4_session as session, run_campaign


HERE = Path(__file__).parent / 'c1_closure_lite'
ROOT = HERE.parents[2]


class SupplementalConfigAttempt(adapter.Attempt):
    def __init__(self, *args, filename, spare=False):
        self.filename = filename
        self.spare = spare
        super().__init__(*args)

    def prepare(self):
        first = next(stage for stage in self.source['stage_graph'] if stage['kind'] == 'campaign_collection')
        self.directory = closure.PACK / closure.C1_DISPATCH / first['stage_id']
        if self.spare:
            self.directory /= 'spares-1'
        self.extra = self.directory / self.filename
        data = adapter.series.raw_json({'run_id': 'old-run', 'workload_profile': {'name': 'align_episode'}})
        public = self.work / 'public'
        adapter.put(public, self.filename, data)
        manifest = adapter.put(public, 'manifest.json', {
            str(self.extra): {'source': self.filename, 'sha256': closure.digest(data)}})
        adapter.put(self.git_dir, adapter.LEDGER, self.ledger)
        with (self.git_dir / '.git/info/exclude').open('a') as stream:
            stream.write('\n/runs/\n')

        target = self.work / 'prepared'
        target.mkdir()
        old_view, old_stage = self.view, self.stage
        self.view, _, self.handoff, _, paths = adapter.staging.c1_measurement_view(
            self.git_dir, target, kit=adapter.KIT, public_inputs=manifest)
        self.repo = Path(self.handoff['repo'])
        self.stage = Path(self.handoff['stage'])
        self.night = self.stage / self.night.relative_to(old_stage)
        for key, value in self.bindings.items():
            path = Path(value)
            for previous, current in ((old_view, self.view), (old_stage, self.stage)):
                if path.is_relative_to(previous):
                    self.bindings[key] = str(current / path.relative_to(previous))
        declare = closure.declare_outputs
        with patch.object(closure, 'declare_outputs',
                          side_effect=lambda repo, stage, files: declare(repo, stage, set(files) | set(paths))):
            super().prepare()


class DuplicateOptionAttempt(adapter.Attempt):
    def prepare(self):
        render = adapter.chain.render_chain

        def render_for_refusal(**kwargs):
            try:
                return render(**kwargs)
            except adapter.chain.ChainRenderError:
                # Authenticate the invalid attempt to exercise both arm gates.
                return b'# invalid options refuse before launch\n'

        with patch.object(adapter.chain, 'render_chain', side_effect=render_for_refusal):
            super().prepare()


class C1ClosureTests(unittest.TestCase):
    def attempt(self, fixture='valid_24_closure', *, make_attempt=adapter.Attempt, edit_source=None):
        work = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.enterContext(patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}))
        for name in ('CALIBRATION_LEDGER', 'LEDGER_HEAD_PIN', 'JOULEWISE_C1_INPUTS'):
            os.environ.pop(name, None)
        subprocess.run(['git', 'clone', '-q', '--bare', HERE / 'suite/history.bundle', work / 'history.git'], check=True)
        return make_attempt(work, fixture, 'copy', edit_source)

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
            relative = closure.PACK / closure.C1_DISPATCH / dispatch['stage_id'] / 'order_manifest.json'
            path = attempt.stage / relative
            raw = path.read_bytes()
            order = json.loads(raw)
            order['executed_order'].reverse()
            for changed in (raw + b' ', adapter.series.raw_json(order)):
                with self.subTest(stage=dispatch['stage_id']):
                    path.write_bytes(changed)
                    self.assert_refuses_before_host(attempt, 'staged SHA-256 mismatch')
            path.write_bytes(raw)

    def test_spare_dispatch_uses_the_same_scoped_ancestor_lookup_and_pin(self):
        attempt = self.attempt('with_spare')
        code, packet = attempt.build()
        self.assertEqual(code, 0, attempt.build_error)
        attempt.deliver(packet)
        validated = session.c1_arm_preflight(attempt.handoff_file, now_epoch_s=adapter.NOW)
        first = validated['kit']['execution']['order_manifests'][0]
        path, signed = next(iter(first['spares'].items()))
        target = attempt.stage / path
        self.assertEqual(closure.digest(target.read_bytes()), signed['sha256'])
        target.write_bytes(target.read_bytes() + b' ')
        self.assert_refuses_before_host(attempt, 'staged SHA-256 mismatch')

    def consumer_outcomes(self, attempt):
        entries = []

        def host_entry():
            entries.append('host')

        cli = attempt.install(host_entry)
        cli_entries = len(entries)
        entries.clear()
        arm = attempt.direct_arm(host_entry)
        return cli, arm, cli_entries, len(entries)

    def test_declared_extra_json_refuses_in_main_and_spare_dispatch(self):
        for spare in (False, True):
            with self.subTest(spare=spare):
                attempt = self.attempt('with_spare' if spare else 'valid_24_closure',
                                       make_attempt=partial(SupplementalConfigAttempt,
                                                            filename='old-config.json', spare=spare))
                directory = attempt.view / attempt.directory
                order, warning = run_campaign.load_order_entries(directory)
                self.assertIsNone(warning)
                reason = 'config(s) absent from manifest: old-config.json'
                with self.assertRaises(ValueError) as error:
                    run_campaign.apply_order_manifest(run_campaign.discover_configs(directory), order)
                self.assertEqual(str(error.exception), reason)

                code, packet = attempt.build()
                self.assertIn(str(attempt.extra), packet['c1_closure']['stage_files'])
                attempt.deliver(packet)
                result = self.consumer_outcomes(attempt)
                self.assertEqual((code, *result), (2, 2, 'refuse', 0, 0), attempt.cli_error)
                self.assertIn(reason, attempt.build_error)
                self.assertIn(reason, attempt.native['packet_kit']['detail'])

    def test_dispatch_ignores_declared_file_outside_runner_config_glob(self):
        attempt = self.attempt(make_attempt=partial(SupplementalConfigAttempt, filename='old-config.txt'))
        code, packet = attempt.build()
        attempt.deliver(packet)
        self.assertEqual((code, *self.consumer_outcomes(attempt)), (0, 0, 'admit', 1, 1), attempt.cli_error)

    def assert_duplicate_option_refuses(self, edit, flag):
        attempt = self.attempt(make_attempt=DuplicateOptionAttempt, edit_source=edit)
        code, packet = attempt.build()
        attempt.deliver(packet)
        self.assertEqual((code, *self.consumer_outcomes(attempt)), (2, 2, 'refuse', 0, 0), attempt.cli_error)
        for detail in (attempt.build_error, attempt.cli_error, attempt.native['packet_kit']['detail']):
            self.assertIn(f'duplicate option {flag}', detail)

    def test_duplicate_reservation_head_pin_refuses(self):
        for attached in (False, True):
            with self.subTest(attached=attached):
                def edit(tree):
                    stage = next(row for row in tree['stage_graph'] if row['kind'] == 'bracket_reservation')
                    argv = adapter.arguments(stage)
                    if adapter.literal('--head-pin') in argv:
                        index = argv.index(adapter.literal('--head-pin'))
                        del argv[index:index + 2]
                    adapter.option(argv, '--head-pin', 'repo_path', adapter.HEAD.with_name('retired-head.json'))
                    if attached:
                        argv.append(adapter.literal(f'--head-pin={adapter.HEAD}'))
                    else:
                        adapter.option(argv, '--head-pin', 'repo_path', adapter.HEAD)
                    return {}

                self.assert_duplicate_option_refuses(edit, '--head-pin')

    def test_duplicate_derivation_corpus_manifest_refuses(self):
        def edit(tree):
            row = next(stage for stage in tree['stage_graph'] if stage['kind'] == 'bound_derivation')
            argv = adapter.arguments(row)
            index = argv.index(adapter.literal('--derive-neg8-drift-bound')) + 1
            argv[index] = {'kind': 'repo_path', 'value': str(adapter.DERIVATION.with_name('retired-corpus.json'))}
            argv.append(adapter.literal(f'--derive-neg8-drift-bound={adapter.DERIVATION}'))
            return {}

        self.assert_duplicate_option_refuses(edit, '--derive-neg8-drift-bound')

    def test_duplicate_campaign_runs_root_refuses(self):
        def edit(tree):
            row = next(stage for stage in tree['stage_graph'] if stage['stage_id'] == 'align-v4-c1-episodes-a')
            adapter.arguments(row).append(adapter.literal('--runs-dir=/synthetic-previous-attempt-runs'))
            return {}

        self.assert_duplicate_option_refuses(edit, '--runs-dir')

    def test_duplicate_option_spellings_in_every_launch_stage(self):
        attempt = self.attempt('with_spare')
        stages = [stage for stage in adapter.chain.stage_plan(attempt.tree) if stage.in_chain]
        for stage in stages:
            parsed = adapter.chain.c1_stage_command(stage, attempt.bindings, attempt.tree, attempt.view)
            self.assertTrue(parsed.options)
            for flag, (index, attached) in parsed.options.items():
                self.assertFalse(attached)
                value = parsed.argv[index + 1:index + 2] if parsed.takes_value(flag) else []
                variants = {'duplicate': [flag, *value]}
                variants['equals'] = [flag + '=' + (value[0] if value else 'invented')]
                for end in range(3, len(flag)):
                    prefix = flag[:end]
                    if parsed.option_for(prefix) == flag:
                        variants['abbreviation'] = [prefix, *value]
                        break
                for spelling, duplicate in variants.items():
                    with self.subTest(stage=stage.stage_id, flag=flag, spelling=spelling):
                        argv = list(parsed.argv) + duplicate
                        with self.assertRaisesRegex(adapter.chain.ChainRenderError, f'duplicate option {flag}'):
                            parsed.reparse(argv)

    def test_frozen_lite_decisions(self):
        completed = subprocess.run([sys.executable, '-B', str(HERE / 'suite/run.py'),
                                    '--adapter', str(HERE / 'adapter.py')], cwd=ROOT,
                                   env={**os.environ, 'PYTHONPATH': os.pathsep.join([str(ROOT / 'tests'), str(ROOT)])},
                                   capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, (HERE / 'suite/expected.jsonl').read_bytes())
