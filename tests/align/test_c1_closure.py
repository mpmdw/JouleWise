"""The frozen acceptance tape and additional prepare/ledger contract cases."""
import argparse
from functools import partial
import json
import os
import shlex
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
        code, packet = attempt.build()
        self.assertEqual(code, 0, attempt.build_error)
        attempt.deliver(packet)
        chain = adapter.chain
        scripts = {}
        parse = chain._c1_parse

        def record(tool, argv, *defaults):
            parsed = parse(tool, argv, *defaults)
            scripts[tuple(argv)] = parsed
            return parsed

        with patch.object(chain, '_c1_parse', side_effect=record):
            attempt.context()
        def shell_words(text):
            return ' '.join(text.replace('\\\n', ' ').split())

        rendered = shell_words((attempt.stage / 'controls/chain.zsh').read_text())
        commands = {
            argv: parsed for argv, parsed in scripts.items()
            if argv[0] and argv[1] and any(
                shell_words(chain._argv_text(candidate)) in rendered
                for candidate in (argv, (argv[0], '-B', *argv[1:]))
            )
        }
        self.assertTrue(any('spares-1' in arg for argv in commands for arg in argv))
        self.assertTrue(any('$TRANSCRIPT_ROOT' in arg for argv in commands for arg in argv))
        programs = {Path(argv[1]).name for argv in commands}
        self.assertEqual(programs, {'reserve_calibration_window_bracket.py',
                                    'validate_powermetrics_fiducial.py', 'run_campaign.py',
                                    'recover_calibration_ledger.py', 'b5_window_calibration_verdict.py'})
        def supports_prefix(parsed, flag, prefix):
            matches = set()
            for parser in parsed.parsers:
                resolved = argparse.ArgumentParser._parse_optional(parser, prefix)
                if resolved and len(resolved) == 1 and resolved[0][0] is not None:
                    matches.add(resolved[0][0].option_strings[-1])
            return matches == {flag}

        total = 0
        for argv, parsed in commands.items():
            self.assertTrue(parsed.options)
            for flag, (index, attached) in parsed.options.items():
                values = []
                action = next(parser._option_string_actions[flag] for parser in parsed.parsers
                              if flag in parser._option_string_actions)
                if action.nargs != 0:
                    values = [argv[index].split('=', 1)[1]] if attached else [argv[index + 1]]
                variants = {'duplicate': [flag, *values],
                            'equals': [flag + '=' + (values[0] if values else 'invented')]}
                for end in range(3, len(flag)):
                    prefix = flag[:end]
                    if supports_prefix(parsed, flag, prefix):
                        variants['abbreviation'] = [prefix, *values]
                        break
                for spelling, duplicate in variants.items():
                    with self.subTest(program=argv[1], flag=flag, spelling=spelling):
                        with self.assertRaisesRegex(chain.ChainRenderError, f'duplicate option {flag}'):
                            parsed.reparse((*argv, *duplicate))
                        total += 1
        print(f'C1 duplicate-option sweep: {total} cases across {len(commands)} command variants')

    def test_single_attached_derivation_option_selects_same_manifest_for_pruning(self):
        def edit(tree):
            row = next(stage for stage in tree['stage_graph'] if stage['kind'] == 'bound_derivation')
            argv = adapter.arguments(row)
            index = argv.index(adapter.literal('--derive-neg8-drift-bound'))
            argv[index:index + 2] = [adapter.literal(f'--derive-neg8-drift-bound={adapter.DERIVATION}')]
            return {}

        attempt = self.attempt(edit_source=edit)
        code, packet = attempt.build()
        attempt.deliver(packet)
        self.assertEqual((code, *self.consumer_outcomes(attempt)), (0, 0, 'admit', 1, 1), attempt.cli_error)
        script = (attempt.stage / 'controls/chain.zsh').read_text().replace('\\\n', ' ')
        prune = next(shlex.split(line) for line in script.splitlines() if '"$B5_PRUNE_PY"' in line)
        manifest = Path(prune[prune.index('$B5_PRUNE_PY') + 1])
        if not manifest.is_absolute():
            manifest = attempt.view / manifest
        self.assertEqual(manifest.resolve(), attempt.context()[-1]['derivation'])
        self.assertEqual(manifest.resolve(), (attempt.repo / adapter.DERIVATION).resolve())

    def test_frozen_lite_decisions(self):
        completed = subprocess.run([sys.executable, '-B', str(HERE / 'suite/run.py'),
                                    '--adapter', str(HERE / 'adapter.py')], cwd=ROOT,
                                   env={**os.environ, 'PYTHONPATH': os.pathsep.join([str(ROOT / 'tests'), str(ROOT)])},
                                   capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, (HERE / 'suite/expected.jsonl').read_bytes())
