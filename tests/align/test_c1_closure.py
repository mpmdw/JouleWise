"""The frozen acceptance tape and additional prepare/ledger contract cases."""
import argparse
import ast
import contextlib
import fnmatch
import functools
from functools import partial
import hashlib
import io
import json
import os
import re
import shlex
import shutil
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

# What a chain consumer would read, evaluated by the consumers' own code in a
# fresh interpreter after the rendered C1 environment block.
CONSUMED_PROBE = r'''
import json, os, sys
sys.path.insert(0, sys.argv[1])
from joulewise.align.apple.v4_registration import runtime_input_context
from joulewise.align.shade.upstream import PinnedUpstream
print(json.dumps({
    'environment': dict(os.environ),
    'interpreter': repr(sys.flags),
    'shade_cache': str(PinnedUpstream(allow_fetch=False).cache_dir),
    'c1_context': runtime_input_context(),
    # joulewise/controller.py reads this plan whenever the name is set.
    'g2a_context': os.environ['JOULEWISE_G2A_PRE_BRACKET_PLAN']
    if 'JOULEWISE_G2A_PRE_BRACKET_PLAN' in os.environ else None,
}, sort_keys=True))
'''


def environment_block(chain_text):
    """The rendered chain's C1 environment block, exactly as emitted."""
    lines = chain_text.splitlines()
    start = lines.index('# C1 closed environment: every variable a chain consumer reads is exported')
    end = next(index for index in range(start, len(lines)) if lines[index].startswith('export REPO='))
    return lines[start:end]


def run_closed_environment(environment, ambient, work, *, block=None):
    """Apply a C1 environment block under zsh, then report what consumers read."""
    probe = Path(work) / 'consumed-probe.py'
    probe.write_text(CONSUMED_PROBE)
    block = adapter.chain.c1_environment_lines(environment) if block is None else block
    script = '\n'.join(['set -u', *block, ' '.join(shlex.quote(word) for word in (
        'exec', sys.executable, str(probe), str(ROOT)))])
    base = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': os.environ.get('HOME', '/'),
            'NIGHT_DIR': str(work)}
    completed = subprocess.run(['/bin/zsh', '-f', '-c', script], env={**base, **ambient},
                               capture_output=True, text=True, check=True)
    return json.loads(completed.stdout)


def rendered_environment(attempt):
    """The closed environment that the attempt's chain renders."""
    night = closure.decode((attempt.stage / 'controls/night.json').read_bytes())
    ledger = attempt.stage / adapter.LEDGER
    pin = {'path': str(ledger), 'sha256': closure.digest(ledger.read_bytes())}
    environment, _ = adapter.chain.c1_chain_environment(
        stages=adapter.chain.stage_plan(attempt.tree, c1=True), bindings=night['hazard_window']['bindings'],
        tree=attempt.tree, measurement_root=attempt.view, plan_id=night['plan_id'],
        c1_inputs=closure.execution_inputs(attempt.handoff, pin))
    return environment


# Reads whose variable name is computed at run time. Each is justified here;
# any other computed name fails the inventory test.
KNOWN_COMPUTED_READS = {
    # Arm-time evidence: iterates fixed names or records the whole environment.
    ('joulewise/arm_readiness_evidence.py', 'name'),
    # An endpoint credential named by its caller; no module or config supplies one.
    ('joulewise/align/endpoints.py', 'self.api_key_env'),
}
ENVIRONMENT_READERS = ('os.environ.get', 'os.getenv', 'environ.get', 'os.environ.pop', 'os.environ.setdefault')


def chain_programs(chain_text, view):
    """The repository programs that the rendered chain runs."""
    return tuple(sorted(set(re.findall(re.escape(str(view)) + r'/(scripts/[A-Za-z0-9_]+\.py)', chain_text))))


@functools.cache
def chain_environment_reads(programs):
    """Variables read by the chain's programs, inline helpers and everything they import."""
    chain = adapter.chain

    def module_file(name):
        parts = name.split('.')
        for count in range(len(parts), 0, -1):
            base = ROOT.joinpath(*parts[:count])
            for candidate in (base.with_suffix('.py'), base / '__init__.py'):
                if candidate.is_file():
                    return candidate
        return None

    def imported(tree, path):
        names = set()
        package = path.relative_to(ROOT).with_suffix('').parts if path else ()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ''
                if node.level:
                    keep = len(package) - node.level + (path.name == '__init__.py')
                    base = '.'.join([*package[:keep], *([node.module] if node.module else [])])
                names.add(base)
                names.update(f'{base}.{alias.name}' for alias in node.names)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and ':' in node.value:
                # Task factories named as module:callable strings.
                module = node.value.split(':', 1)[0]
                if module.startswith('joulewise.') and module.replace('.', '').replace('_', '').isalnum():
                    names.add(module)
        return {name for name in names if name.split('.')[0] in ('joulewise', 'scripts')}

    sources = [(ROOT / program, None) for program in programs]
    sources += [(None, helper) for helper in (chain.PRUNE_HELPER, chain.BUDGET_HELPER, chain.FLAG_HELPER,
                                              chain.CORPUS_RETRY_HELPER, chain.SPARE_RETRY_HELPER,
                                              chain.SETTLE_MARK_HELPER)]
    trees, pending = {}, list(sources)
    while pending:
        path, text = pending.pop()
        label = path.relative_to(ROOT).as_posix() if path else 'joulewise/b5/chain.py (inline helper)'
        if (label, text) in trees:
            continue
        tree = ast.parse(path.read_bytes() if path else text)
        trees[label, text] = tree
        for name in imported(tree, path):
            parts = name.split('.')
            for count in range(1, len(parts) + 1):
                candidate = module_file('.'.join(parts[:count]))
                if candidate and (candidate.relative_to(ROOT).as_posix(), None) not in trees:
                    pending.append((candidate, None))
    constants = {}
    for tree in trees.values():
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                    and isinstance(node.value.value, str):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        constants.setdefault(target.id, set()).add(node.value.value)

    def names_of(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value}
        key_name = node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else None
        return constants.get(key_name)

    reads, computed = {}, set()
    for (label, _), tree in trees.items():
        for node in ast.walk(tree):
            target = None
            if isinstance(node, ast.Call) and ast.unparse(node.func) in ENVIRONMENT_READERS and node.args:
                target = node.args[0]
            elif isinstance(node, ast.Subscript) and ast.unparse(node.value) in ('os.environ', 'environ') \
                    and not isinstance(node.ctx, ast.Store):
                target = node.slice
            elif isinstance(node, ast.Compare) and any(
                    ast.unparse(item) in ('os.environ', 'environ') for item in node.comparators):
                target = node.left
            if target is None:
                continue
            if (resolved := names_of(target)) is None:
                computed.add((label, ast.unparse(target)))
                continue
            for name in resolved:
                reads.setdefault(name, set()).add(label)
    return reads, computed, len(trees)


def chain_shell_reads(text):
    """Variables the rendered chain text reads without assigning them."""
    text = re.sub(r"<<'B5_PY'\n.*?\nB5_PY\n", '', text, flags=re.S)
    text = re.sub(r"^B5_SETTLE_MARK_PY='.*?^'$", 'B5_SETTLE_MARK_PY=', text, flags=re.S | re.M)
    referenced = set(re.findall(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)', text))
    assigned = set(re.findall(r'(?:^|[\s;(])(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=', text, flags=re.M))
    assigned |= set(re.findall(r'\bfor\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\b', text))
    assigned |= set(re.findall(r'\bread\s+(?:-[A-Za-z]+\s+)*([A-Za-z_][A-Za-z0-9_]*)', text))
    for match in re.finditer(r'\blocal\s+([^\n]*)', text):
        assigned.update(word.split('=')[0] for word in match.group(1).split())
    return referenced - assigned


def non_exact(raw):
    """Honest near-misses of the exact bytes a digest must cover."""
    variants = {raw[:-1] if raw.endswith(b'\n') else raw + b'\n', raw + b'\n', raw.replace(b'\n', b'\r\n')}
    try:
        variants.add(json.dumps(json.loads(raw), sort_keys=True).encode())
    except ValueError:
        pass
    return sorted(variants - {raw})


class PublicInputAttempt(adapter.Attempt):
    def prepare_public_inputs(self, files):
        manifest = adapter.put(self.work, 'public/manifest.json', files)
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


class SupplementalConfigAttempt(PublicInputAttempt):
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
        self.prepare_public_inputs({
            str(self.extra): {'source': self.filename, 'sha256': closure.digest(data)}})


class ReservationPlanDigestAttempt(adapter.Attempt):
    def __init__(self, *args, exact):
        self.exact = exact
        super().__init__(*args)

    def mutate_source(self):
        super().mutate_source()
        raw = (self.git_dir / adapter.KIT / adapter.series.C1_PLAN).read_bytes()
        if not raw.endswith(b'\n'):
            raise ValueError('invented plan needs its trailing newline')
        stage = next(row for row in self.source['stage_graph'] if row['kind'] == 'bracket_reservation')
        argv = adapter.arguments(stage)
        position = argv.index(adapter.literal('--plan-sha256'))
        argv[position + 1] = adapter.literal(closure.digest(raw if self.exact else raw[:-1]))


class ShadeCacheAttempt(PublicInputAttempt):
    data = b'Synthetic cache export.\n'
    revision = '4' * 40
    entry = Path('joulewise/shade') / revision / 'README.txt'

    def __init__(self, *args, current_cache):
        self.current_cache = current_cache
        super().__init__(*args)

    def mutate_source(self):
        super().mutate_source()
        stage = next(row for row in self.source['stage_graph'] if row['kind'] == 'campaign_collection')
        manifest = self.git_dir / stage['input']['path']
        order = closure.decode(manifest.read_bytes())
        member = order['executed_order'][0]
        config = manifest.parent / member['config']
        data = closure.decode(config.read_bytes())
        spec = json.loads(data['workload_profile']['prompt_text'])
        blob = hashlib.sha1(b'blob ' + str(len(self.data)).encode() + b'\0' + self.data).hexdigest()
        pin = closure.digest(b'README.txt\0' + blob.encode() + b'\n')
        spec.update(task_factory='joulewise.align.apple.pilot:offline_shade_task',
                    task_kwargs={'task_pair': 'invented', 'commit': self.revision, 'file_sha256': pin})
        data['workload_profile']['prompt_text'] = json.dumps(spec)
        member['config_sha256'] = closure.digest(adapter.put(config.parent, config.name, data).read_bytes())
        stage['input']['sha256'] = closure.digest(adapter.put(manifest.parent, manifest.name, order).read_bytes())

    def prepare(self):
        homes = ('old-cache', 'cache') if self.current_cache else ('old-cache',)
        adapter.put(self.work / 'public', 'source.txt', self.data)
        self.prepare_public_inputs({
            str(Path(home) / self.entry): {'source': 'source.txt', 'sha256': closure.digest(self.data)}
            for home in homes})


class DeskPolicyAttempt(adapter.Attempt):
    # The reservation records the desk epoch's power policy before the plan's.
    desk_epoch = adapter.series.raw_json({'power_policy': 'ac_low_power'})


class ResumableSessionAttempt(adapter.Attempt):
    """The starting ledger already holds this attempt's open session (the reservation's resumable route)."""

    def prepare(self):
        from joulewise import calibration_ledger as ledger_module
        from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS

        epoch = {'os_build': 'invented', 'hardware_model': 'fixture', 'power_policy': 'ac_high_power',
                 'sampling_interval_ms': 100, 'estimator_revision': 'invented',
                 'pulse_protocol_id': 'invented'}
        build = self.work / 'starting-ledger'
        path = adapter.put(build, 'ledger.jsonl', b'')
        pin = adapter.put(build, 'pin.json', {'sequence': 0, 'head_digest': '0' * 64,
                                             'ledger_schema': 'joulewise.calibration_observation_ledger.v1'})
        with ledger_module.CalibrationWriterLease(path):
            ledger_module.append_bracket_session_receipt(
                path, session_id=self.bindings['bracket_session_id'], window_id='C1',
                plan_id=self.source['plan']['plan_id'], plan_sha256=self.source['plan']['actual_sha256'],
                evidence_root_id='fixture-evidence', runs_root=self.bindings['claim_runs_root'],
                slots={slot: {'attempt_id': self.bindings[f'{slot}_attempt_id'], 'identity_epoch': epoch,
                              't1_bindings': {**dict.fromkeys(V2_BINDING_FIELDS, 'invented'), **epoch},
                              'custody_locator': self.bindings[f'{slot}_calibration_dir']}
                       for slot in ('pre', 'post')},
                head_pin_path=pin, require_committed_pin=False, pin_relation_record={})
        self.ledger = path.read_bytes()
        super().prepare()


def capture_arguments(tree, slot):
    for row in tree['stage_graph']:
        if row['kind'] == 'calibration_capture':
            arguments = adapter.arguments(row)
            if arguments[arguments.index(adapter.literal('--slot')) + 1]['value'] == slot:
                return arguments
    raise AssertionError(slot)


def set_option(arguments, flag, kind, value):
    if adapter.literal(flag) in arguments:
        index = arguments.index(adapter.literal(flag))
        del arguments[index:index + 2]
    adapter.option(arguments, flag, kind, value)


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

    def test_reservation_plan_digest_covers_the_trailing_newline(self):
        for exact in (True, False):
            with self.subTest(exact=exact):
                attempt = self.attempt(make_attempt=partial(ReservationPlanDigestAttempt, exact=exact))
                code, packet = attempt.build()
                attempt.deliver(packet)
                observed = (code, *self.consumer_outcomes(attempt))
                if exact:
                    self.assertEqual(observed, (0, 0, 'admit', 1, 1), attempt.cli_error)
                else:
                    self.assertEqual(observed, (2, 2, 'refuse', 0, 0), attempt.cli_error)
                    self.assertIn('calibration_plan_hash_mismatch', attempt.build_error)
                    self.assertIn('calibration_plan_hash_mismatch', attempt.native['packet_kit']['detail'])

    def test_shade_uses_the_rendered_cache_instead_of_stale_xdg_cache_home(self):
        for current_cache in (True, False):
            with self.subTest(current_cache=current_cache):
                attempt = self.attempt(make_attempt=partial(ShadeCacheAttempt, current_cache=current_cache))
                stale = attempt.stage / 'old-cache'
                self.assertTrue((stale / attempt.entry).is_file())
                self.assertEqual(attempt.handoff['cache_home'], str(attempt.stage / 'cache'))
                with patch.dict(os.environ, {'XDG_CACHE_HOME': str(stale)}):
                    code, packet = attempt.build()
                    attempt.deliver(packet)
                    observed = (code, *self.consumer_outcomes(attempt))
                if current_cache:
                    self.assertEqual(observed, (0, 0, 'admit', 1, 1), attempt.cli_error)
                else:
                    self.assertEqual(observed, (2, 2, 'refuse', 0, 0), attempt.cli_error)
                    self.assertIn('SHADE', attempt.build_error)
                    self.assertIn('SHADE', attempt.native['packet_kit']['detail'])

    def test_gemini_6_1_shade_check_uses_the_rendered_cache_home(self):
        # Gemini 6.1(1): the caller's XDG_CACHE_HOME names a valid staged
        # cache. The handoff's cache_home, which the chain exports, lacks the
        # dependency. Preflight must judge the exported value.
        attempt = self.attempt(make_attempt=partial(ShadeCacheAttempt, current_cache=False))
        stale = attempt.stage / 'old-cache'
        judged = []
        check = closure.shade_dependency

        def observe(spec):
            judged.append(os.environ.get('XDG_CACHE_HOME'))
            return check(spec)

        with patch.dict(os.environ, {'XDG_CACHE_HOME': str(stale)}), \
                patch.object(closure, 'shade_dependency', side_effect=observe):
            code, packet = attempt.build()
            attempt.deliver(packet)
            observed = (code, *self.consumer_outcomes(attempt))
        self.assertEqual(observed, (2, 2, 'refuse', 0, 0), attempt.cli_error)
        self.assertIn('SHADE dependency is absent', attempt.native['packet_kit']['detail'])
        self.assertTrue(judged)
        self.assertEqual(set(judged), {attempt.handoff['cache_home']})
        rendered = (attempt.stage / 'controls/chain.zsh').read_text()
        self.assertIn('export XDG_CACHE_HOME=' + shlex.quote(attempt.handoff['cache_home']), rendered)

    def test_gemini_6_1_absent_cache_home_is_unset_and_shade_refuses(self):
        # Gemini 6.1(2): no cache_home. The chain must unset XDG_CACHE_HOME,
        # and a SHADE workload must not fall back to the launching user's home.
        attempt = self.attempt(make_attempt=partial(ShadeCacheAttempt, current_cache=True))
        del attempt.handoff['cache_home']
        adapter.put(attempt.work, attempt.prepared_file.name, attempt.handoff)
        with patch.dict(os.environ, {'XDG_CACHE_HOME': str(attempt.stage / 'cache')}):
            code, packet = attempt.build()
        self.assertEqual(code, 2)
        self.assertIn('no cache_home binds its cache', attempt.build_error)
        bindings = closure.decode((attempt.stage / 'controls/night.json').read_bytes())['hazard_window']['bindings']
        stages = adapter.chain.stage_plan(attempt.tree, c1=True)
        environment, _ = adapter.chain.c1_chain_environment(
            stages=stages, bindings=bindings, tree=attempt.tree, measurement_root=attempt.view,
            plan_id=attempt.tree['plan']['plan_id'], c1_inputs=closure.execution_inputs(attempt.handoff, {}))
        self.assertIsNone(environment['XDG_CACHE_HOME'])
        consumed = run_closed_environment(environment, {'XDG_CACHE_HOME': str(attempt.stage / 'cache')},
                                          attempt.work)
        self.assertNotIn('XDG_CACHE_HOME', consumed['environment'])
        self.assertNotEqual(consumed['shade_cache'], str(attempt.stage / 'cache/joulewise/shade'))

    def test_gemini_6_2_g2a_pre_bracket_plan_never_reaches_a_consumer(self):
        attempt = self.attempt()
        outside = adapter.put(attempt.work, 'stale-g2a-plan.json', {'window_id': 'retired'})
        with patch.dict(os.environ, {'JOULEWISE_G2A_PRE_BRACKET_PLAN': str(outside)}):
            code, packet = attempt.build()
            attempt.deliver(packet)
            observed = (code, *self.consumer_outcomes(attempt))
            # Preflight judges the rendered environment, never the caller's.
            seen = []
            # The stubbed consumers return no reservation, so skip the later launch-record check.
            with patch.object(closure, '_check_consumers', side_effect=lambda *a, **k: seen.append(
                    os.environ.get('JOULEWISE_G2A_PRE_BRACKET_PLAN')) or {}), \
                    patch.object(closure, 'check_launch_records'):
                attempt.context()
        self.assertEqual(observed, (0, 0, 'admit', 1, 1), attempt.cli_error)
        self.assertEqual(seen, [None])
        rendered = (attempt.stage / 'controls/chain.zsh').read_text()
        self.assertIn("unset -m 'JOULEWISE_*' 'PYTHON*'", rendered)
        consumed = run_closed_environment(None, {'JOULEWISE_G2A_PRE_BRACKET_PLAN': str(outside)}, attempt.work,
                                          block=environment_block(rendered))
        self.assertIsNone(consumed['g2a_context'])
        self.assertNotIn('JOULEWISE_G2A_PRE_BRACKET_PLAN', consumed['environment'])

    def test_opus_med_1_consumer_input_gates_refuse_before_host(self):
        """The round 11 Opus review's gaps: each consumer's own input gate runs at preflight."""
        def stage(tree, kind):
            return adapter.arguments(next(row for row in tree['stage_graph'] if row['kind'] == kind))

        def replace(arguments, flag, value):
            arguments[arguments.index(adapter.literal(flag)) + 1] = adapter.literal(value)

        def outside_custody(tree):
            replace(stage(tree, 'bracket_reservation'), '--pre-custody-locator', '/synthetic-outside/pre')
            return {}

        def no_execute(tree):
            stage(tree, 'bracket_reservation').remove(adapter.literal('--execute'))
            return {}

        def zero_budget(tree):
            adapter.option(stage(tree, 'calibration_capture'), '--custody-budget-s', 'literal', '0')
            return {}

        def zero_reservation_budget(tree):
            adapter.option(stage(tree, 'bracket_reservation'), '--custody-budget-s', 'literal', '0')
            return {}

        def shakedown(tree):
            adapter.option(stage(tree, 'campaign_collection'), '--shakedown-gate', 'literal',
                           'production_uncertainty_v1')
            return {}

        cases = ((outside_custody, 'C1 reservation refuses: calibration_reservation_input_invalid'),
                 (no_execute, 'C1 reservation must append its session'),
                 (zero_budget, 'custody budget must be finite and positive'),
                 (zero_reservation_budget, 'custody budget must be finite and positive'),
                 (shakedown, 'unsupported C1 campaign mode'))
        for edit, detail in cases:
            with self.subTest(case=edit.__name__):
                attempt = self.attempt(edit_source=edit)
                code, _ = attempt.build()
                self.assertEqual(code, 2, attempt.build_error)
                self.assertIn(detail, attempt.build_error)

    def assert_refused_on_both_routes(self, attempt, detail):
        """Install exits 2 with packet_kit_mismatch; direct arm refuses; no host entry; ledger untouched."""
        ledger = attempt.stage / adapter.LEDGER
        before = ledger.read_bytes()
        code, packet = attempt.build()
        attempt.deliver(packet)
        observed = (code, *self.consumer_outcomes(attempt))
        self.assertEqual(observed, (2, 2, 'refuse', 0, 0), attempt.cli_error)
        self.assertIn('packet_kit_mismatch', attempt.cli_error)
        for text in (attempt.build_error, attempt.cli_error, attempt.native['packet_kit']['detail']):
            self.assertIn(detail, text)
        self.assertEqual(ledger.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in ledger.parent.iterdir()), [ledger.name])

    def assert_admitted_on_both_routes(self, attempt):
        code, packet = attempt.build()
        attempt.deliver(packet)
        self.assertEqual((code, *self.consumer_outcomes(attempt)), (0, 0, 'admit', 1, 1), attempt.cli_error)

    def test_r11_capture_power_policy_must_equal_the_reserved_policy(self):
        """Ruling item 1: each capture's --power-policy equals what the reservation records."""
        for slot in ('pre', 'post'):
            with self.subTest(mismatch=slot):
                def edit(tree, slot=slot):
                    set_option(capture_arguments(tree, slot), '--power-policy', 'literal', 'ac_low_power')
                    return {}

                self.assert_refused_on_both_routes(self.attempt(edit_source=edit),
                                                   'calibration_reserved_slot_mismatch')
        with self.subTest(control='desk epoch policy matched by both captures'):
            def matched(tree):
                for slot in ('pre', 'post'):
                    set_option(capture_arguments(tree, slot), '--power-policy', 'literal', 'ac_low_power')
                return {}

            self.assert_admitted_on_both_routes(self.attempt(make_attempt=DeskPolicyAttempt, edit_source=matched))

    def test_r11_capture_sampler_must_be_the_reserved_sampler(self):
        """Ruling item 1: --sampler-binary selects the reservation's sampler, judged without opening it."""
        from scripts import validate_powermetrics_fiducial as fiducial

        default = Path(fiducial.POWER_METRICS)
        for slot, sampler in (('pre', '/usr/bin/true'), ('post', '/synthetic-absent/powermetrics')):
            with self.subTest(mismatch=slot):
                def edit(tree, slot=slot, sampler=sampler):
                    set_option(capture_arguments(tree, slot), '--sampler-binary', 'literal', sampler)
                    return {}

                self.assert_refused_on_both_routes(self.attempt(edit_source=edit),
                                                   'calibration_reserved_slot_mismatch')
        with self.subTest(control='omitted default'):
            self.assert_admitted_on_both_routes(self.attempt())
        with self.subTest(control='explicit equivalent spelling'):
            spelled = str(default.parent / '..' / default.parent.name / default.name)

            def equivalent(tree):
                for slot in ('pre', 'post'):
                    set_option(capture_arguments(tree, slot), '--sampler-binary', 'literal', spelled)
                return {}

            self.assert_admitted_on_both_routes(self.attempt(edit_source=equivalent))

    def test_r11_sole_rollback_head_pin_refuses_before_host(self):
        """Ruling item 1: the reservation's pre-reserve pin check on the exact parsed --head-pin."""
        retired = 'configs/calibration/retired-head.json'
        pin = adapter.series.raw_json({'sequence': 7, 'head_digest': '7' * 64,
                                       'ledger_schema': 'joulewise.calibration_observation_ledger.v1'})

        def reservation(tree):
            return adapter.arguments(next(row for row in tree['stage_graph'] if row['kind'] == 'bracket_reservation'))

        def rollback(tree):
            set_option(reservation(tree), '--head-pin', 'repo_path', retired)
            return {retired: pin}

        def default(tree):
            return {retired: pin}

        with self.subTest(case='sole retired pin selected'):
            self.assert_refused_on_both_routes(self.attempt(edit_source=rollback), 'calibration_ledger_rollback')
        with self.subTest(control='same tree, default pin selected'):
            self.assert_admitted_on_both_routes(self.attempt(edit_source=default))

    def test_r11_every_consumer_reads_the_reserved_head_pin(self):
        """Review F1: a later consumer's own --head-pin must select the pin the reservation judged."""
        retired = 'configs/calibration/retired-head.json'
        pin = adapter.series.raw_json({'sequence': 7, 'head_digest': '7' * 64,
                                       'ledger_schema': 'joulewise.calibration_observation_ledger.v1'})

        def collection(tree):
            return adapter.arguments(next(row for row in tree['stage_graph'] if row['kind'] == 'campaign_collection'))

        for name, select in (('pre capture', lambda tree: capture_arguments(tree, 'pre')),
                             ('post capture', lambda tree: capture_arguments(tree, 'post')),
                             ('collection', collection)):
            with self.subTest(mismatch=name):
                def edit(tree, select=select):
                    set_option(select(tree), '--head-pin', 'repo_path', retired)
                    return {retired: pin}

                self.assert_refused_on_both_routes(self.attempt(edit_source=edit),
                                                   "differs from the reservation's head pin")
        with self.subTest(control='explicit default pin in a capture'):
            def same(tree):
                set_option(capture_arguments(tree, 'pre'), '--head-pin', 'repo_path', str(adapter.HEAD))
                return {retired: pin}

            self.assert_admitted_on_both_routes(self.attempt(edit_source=same))

    def test_r11_resumable_session_preflight_takes_no_lease(self):
        """Review MED-1: the read-only pre-reserve decision's session-status route takes no lease either."""
        attempt = self.attempt(make_attempt=ResumableSessionAttempt)
        ledger = attempt.stage / adapter.LEDGER
        before = ledger.read_bytes()
        self.assertTrue(before)
        self.assert_admitted_on_both_routes(attempt)
        self.assertEqual(ledger.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in ledger.parent.iterdir()), [ledger.name])

    def test_r11_capture_slot_binding_must_match_the_reservation(self):
        """Review MED-2: each capture's session, attempt and custody locator match its reserved slot."""
        # Since round 14 another output root refuses first, at the write-location check.
        for slot, flag, value, detail in (
                ('pre', '--session-id', 'fixture-other-session', 'calibration_reserved_slot_mismatch'),
                ('post', '--attempt-id', 'fixture-other-attempt', 'calibration_reserved_slot_mismatch'),
                ('pre', '--output-root', 'other_validation', "capture --output-root must be this attempt's")):
            with self.subTest(slot=slot, flag=flag):
                def edit(tree, slot=slot, flag=flag, value=value):
                    set_option(capture_arguments(tree, slot), flag, 'literal', value)
                    return {}

                self.assert_refused_on_both_routes(self.attempt(edit_source=edit), detail)

    def test_audit4_h1_reservation_window_is_the_frozen_c1_window(self):
        """Audit 4 H1: --window-id C2 beside plan_id align-v4-c1 refuses, and the writer asserts it."""
        from joulewise.flags import core
        from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
        from scripts import reserve_calibration_window_bracket as reservation

        def edit(flag, value):
            def apply(tree):
                row = next(row for row in tree['stage_graph'] if row['kind'] == 'bracket_reservation')
                set_option(adapter.arguments(row), flag, 'literal', value)
                return {}
            return apply

        with self.subTest(case='plan id of another window'):
            self.assert_refused_on_both_routes(self.attempt(edit_source=edit('--plan-id', 'align-v4-c2')),
                                               'calibration_plan_hash_mismatch')
        attempt = self.attempt(edit_source=edit('--window-id', 'C2'))
        with self.subTest(case='window id C2 with the C1 plan (audit reproduction)'):
            self.assert_refused_on_both_routes(attempt, 'frozen C1 window')
        with self.subTest(case='the reservation writer refuses the rendered C2 argv'):
            # The audit's writer replay: host identity and the flag sink are simulated.
            name = str(attempt.view / 'scripts/reserve_calibration_window_bracket.py')
            text = (attempt.stage / 'controls/chain.zsh').read_text().replace('\\\n', ' ')
            argv = next(words[words.index(name) + 1:] for line in text.splitlines()
                        if name in line and name in (words := shlex.split(line)))
            self.assertEqual(argv[argv.index('--window-id') + 1], 'C2')
            epoch = dict(os_build='invented', hardware_model='fixture', power_policy='ac_high_power',
                         sampling_interval_ms=100, estimator_revision='fixture', pulse_protocol_id='fixture')
            t1 = {**dict.fromkeys(V2_BINDING_FIELDS, 'invented'), **epoch}
            ledger = attempt.stage / adapter.LEDGER
            before = ledger.read_bytes()
            error = io.StringIO()
            context = core.HazardFlagContext(writer='core-reservation', custody_root=None,
                                             plan_id=attempt.plan['plan_id'], attempt=None, scope_resolved=False)
            with closure.consumer_environment(rendered_environment(attempt), attempt.view), \
                    patch.object(core, 'hazard_flag_context', return_value=context), patch.object(core, 'emit'), \
                    patch.object(reservation, '_hazard_measured_identity', return_value=(epoch, t1, None)), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(error):
                code = reservation.main(argv)
            self.assertEqual(code, 2, error.getvalue())
            self.assertIn('plan_window_mismatch', error.getvalue())
            self.assertEqual(ledger.read_bytes(), before)

    def test_r13_reservation_matches_the_frozen_window_identity(self):
        """Round 13: a tree's window identity binds the reservation's window and evidence root."""
        def identity(window, root=None):
            def apply(tree):
                row = next(row for row in tree['stage_graph'] if row['kind'] == 'bracket_reservation')
                arguments = adapter.arguments(row)
                reserved = arguments[arguments.index(adapter.literal('--evidence-root-id')) + 1]['value']
                tree['window_identity'] = {'window_id': window, 'evidence_root_id': root or reserved}
                return {}
            return apply

        with self.subTest(case='identity names another window'):
            self.assert_refused_on_both_routes(self.attempt(edit_source=identity('C2')),
                                               "window identity 'C2'")
        with self.subTest(case='identity names another evidence root'):
            self.assert_refused_on_both_routes(
                self.attempt(edit_source=identity('C1', 'synthetic-other-evidence')),
                'evidence root differs from the frozen window identity')
        with self.subTest(control='identity agrees with the reservation'):
            attempt = self.attempt(edit_source=identity('C1'))
            code, _ = attempt.build()
            self.assertEqual(code, 0, attempt.build_error)

    def test_audit4_m1_max_blocks_below_one_refuses_before_host(self):
        """Audit 4 M1: preflight refuses --max-blocks 0 with the campaign's own message."""
        def edit(tree):
            row = next(row for row in tree['stage_graph'] if row['kind'] == 'campaign_collection')
            set_option(adapter.arguments(row), '--max-blocks', 'literal', '0')
            return {}

        self.assert_refused_on_both_routes(self.attempt(edit_source=edit), '--max-blocks must be >= 1')

    def test_audit5_high_stale_campaign_log_refuses_before_host(self):
        """Audit 5 HIGH: a collection --log naming a previous attempt's log refuses on both routes."""
        logs = {}

        class PreviousAttempt(adapter.Attempt):
            def __init__(self, work, *rest):
                # An earlier attempt's campaign log beside this attempt (invented bytes).
                previous = work / 'previous-attempt' / 'campaign_log.jsonl'
                previous.parent.mkdir()
                previous.write_bytes(b'{"record_type": "campaign_provenance_attestation", "invented": true}\n')
                logs['previous'] = previous
                super().__init__(work, *rest)

        def stale(spelling):
            def edit(tree):
                row = next(row for row in tree['stage_graph'] if row['kind'] == 'campaign_collection')
                self.assertNotIn(adapter.literal('--log'), adapter.arguments(row))
                adapter.option(adapter.arguments(row), '--log', 'literal', spelling(logs['previous']))
                return {}
            return edit

        for name, spelling in (('absolute path (audit reproduction)', str),
                               ('relative to the launch view', lambda path: '../previous-attempt/campaign_log.jsonl')):
            with self.subTest(case=name):
                attempt = self.attempt(make_attempt=PreviousAttempt, edit_source=stale(spelling))
                before = logs['previous'].read_bytes()
                self.assert_refused_on_both_routes(attempt, "campaign --log must be this attempt's")
                self.assertEqual(logs['previous'].read_bytes(), before)
                self.assertFalse((Path(attempt.bindings['claim_runs_root']) / 'campaign_log.jsonl').exists())

    def test_r14_every_stage_writes_only_where_this_attempt_is_read(self):
        """Round 14 class: each stage writes only this attempt's paths that the harvest reads."""
        def collection(index):
            return lambda tree: adapter.arguments(
                [row for row in tree['stage_graph'] if row['kind'] == 'campaign_collection'][index])

        def derivation(tree):
            return adapter.arguments(next(row for row in tree['stage_graph'] if row['kind'] == 'bound_derivation'))

        def reservation(tree):
            return adapter.arguments(next(row for row in tree['stage_graph'] if row['kind'] == 'bracket_reservation'))

        def under(binding, relative):
            return {'kind': 'binding_path', 'value': binding, 'relative': relative}

        def edit(*changes):
            def apply(tree):
                for select, flag, item in changes:
                    arguments = select(tree)
                    if adapter.literal(flag) in arguments:
                        index = arguments.index(adapter.literal(flag))
                        del arguments[index:index + 2]
                    arguments.extend([adapter.literal(flag), item])
                return {}
            return apply

        pre = lambda tree: capture_arguments(tree, 'pre')  # noqa: E731
        previous = '/synthetic-previous-attempt'
        cases = (
            ('log in the other runs root', edit((collection(0), '--log', under('bound_runs_root', 'campaign_log.jsonl'))),
             "campaign --log must be this attempt's"),
            ('log under another name', edit((collection(0), '--log', under('claim_runs_root', 'campaign-log-2.jsonl'))),
             "campaign --log must be this attempt's"),
            ('second stage logs into a previous attempt',
             edit((collection(1), '--log', adapter.literal(f'{previous}/claim_runs_root/campaign_log.jsonl'))),
             "campaign --log must be this attempt's"),
            ('bound written into a previous attempt',
             edit((derivation, '--neg8-drift-bound-output',
                   adapter.literal(f'{previous}/bound_runs_root/neg8-drift-bound.json'))),
             "campaign --neg8-drift-bound-output must be this attempt's"),
            ('bound written into the claim runs root',
             edit((derivation, '--neg8-drift-bound-output', under('claim_runs_root', 'neg8-drift-bound.json'))),
             "campaign --neg8-drift-bound-output must be this attempt's"),
            # Agreeing reservation and capture: the capture's flag root would leave the runs root.
            ('capture output root below instrument_validation',
             edit((reservation, '--pre-custody-locator', under('claim_runs_root', 'instrument_validation/nested/fixture-pre')),
                  (pre, '--output-root', under('claim_runs_root', 'instrument_validation/nested'))),
             "capture --output-root must be this attempt's"),
        )
        for name, change, detail in cases:
            with self.subTest(case=name):
                attempt = self.attempt(edit_source=change)
                code, _ = attempt.build()
                self.assertEqual(code, 2, attempt.build_error)
                self.assertIn(detail, attempt.build_error)
        with self.subTest(pin='the bound name preflight binds is the one the harvest reads'):
            from joulewise.b5 import harvest
            self.assertEqual(closure.NEG8_BOUND_NAME, harvest.NEG8_BOUND_NAME)
        with self.subTest(control='explicit log at this attempt\'s runs root'):
            attempt = self.attempt(edit_source=edit(
                (collection(0), '--log', under('claim_runs_root', 'campaign_log.jsonl'))))
            code, _ = attempt.build()
            self.assertEqual(code, 0, attempt.build_error)

    def night_attempt(self, change):
        class NightAttempt(adapter.Attempt):
            def edit_night(self, night):
                change(self, night)

        return self.attempt(make_attempt=NightAttempt)

    def test_audit6_high1_night_plan_window_is_the_reserved_window(self):
        """Audit 6 HIGH 1: a night plan whose pack names C2 refuses on both routes before host entry."""
        def to_c2(attempt, night):
            self.assertEqual(night['hazard_window']['pack']['window_id'], 'C1')
            night['hazard_window']['pack']['window_id'] = 'C2'

        self.assert_refused_on_both_routes(self.night_attempt(to_c2),
                                           "night plan hazard_window.pack.window_id is 'C2'")

    def test_r15_night_plan_launch_identity_and_locations_are_this_attempts(self):
        """Round 15 class: each launch field the driver reads from the night plan is this attempt's."""
        def pack(field, value):
            return lambda attempt, night: night['hazard_window']['pack'].__setitem__(field, value)

        def window(field, value):
            return lambda attempt, night: night['hazard_window'].__setitem__(field, value)

        def top(field, value):
            return lambda attempt, night: night.__setitem__(field, value)

        def previous_claim_root(attempt, night):
            night['hazard_window']['runs_roots'] = dict(night['hazard_window']['runs_roots'],
                                                        claim=str(attempt.work / 'previous-attempt/claim_runs_root'))

        cases = (
            ('pack plan id', pack('pack_plan_id', 'align-v4-c2'), 'hazard_window.pack.pack_plan_id'),
            ('pack id', pack('pack_id', 'align-v4-c2'), 'hazard_window.pack.pack_id'),
            ('evidence root', pack('evidence_root_id', 'synthetic-other-evidence'), 'hazard_window.pack.evidence_root_id'),
            ('plan tree digest', pack('plan_tree_sha256', '0' * 64), 'hazard_window.pack.plan_tree_sha256'),
            ('bracket session', window('bracket_session_id', 'fixture-previous-session'),
             'hazard_window.bracket_session_id'),
            ('claim runs root of a previous attempt', previous_claim_root, 'hazard_window.runs_roots'),
            ('attempt ordinal', window('attempt', 2), 'hazard_window.attempt'),
            # Already bound: the chain is re-rendered with this plan id and compared.
            ('window plan id', top('plan_id', 'synthetic-previous-window-plan'),
             'prepared chain differs from the resolved C1 dispatch'),
            ('custody root of a previous attempt', top('custody_root', '/synthetic-previous-attempt/custody'),
             'night plan custody_root'),
            ('measurement root', top('measurement_root', '/synthetic-other-measurement'), 'night plan measurement_root'),
        )
        for name, change, detail in cases:
            with self.subTest(case=name):
                attempt = self.night_attempt(change)
                code, _ = attempt.build()
                self.assertEqual(code, 2, attempt.build_error)
                self.assertIn(detail, attempt.build_error)

    def test_audit6_high2_linked_default_log_refuses_before_host(self):
        """Audit 6 HIGH 2: a link at the default campaign log refuses on both routes; the old log is untouched."""
        attempt = self.attempt()
        previous = attempt.work / 'previous-attempt' / 'campaign_log.jsonl'
        previous.parent.mkdir()
        previous.write_bytes(b'{"record_type": "campaign_provenance_attestation", "invented": true}\n')
        before = previous.read_bytes()
        claim = Path(attempt.bindings['claim_runs_root'])
        claim.mkdir()
        (claim / 'campaign_log.jsonl').symlink_to(previous)
        self.assert_refused_on_both_routes(attempt, 'claim_runs_root is not empty')
        self.assertEqual(previous.read_bytes(), before)
        self.assertTrue((claim / 'campaign_log.jsonl').is_symlink())

    def test_r15_runs_roots_are_fresh_before_arm(self):
        """Round 15 class: each runs root is absent or the empty real directory prepare made."""
        def previous_log(attempt):
            previous = attempt.work / 'previous-attempt' / 'campaign_log.jsonl'
            previous.parent.mkdir(exist_ok=True)
            previous.write_bytes(b'{"invented": true}\n')
            return previous

        def hard_linked_log(attempt):
            claim = Path(attempt.bindings['claim_runs_root'])
            claim.mkdir()
            os.link(previous_log(attempt), claim / 'campaign_log.jsonl')

        def linked_root(attempt):
            previous = previous_log(attempt).parent
            Path(attempt.bindings['claim_runs_root']).symlink_to(previous, target_is_directory=True)

        def stale_bound(attempt):
            bound = Path(attempt.bindings['bound_runs_root'])
            bound.mkdir()
            (bound / closure.NEG8_BOUND_NAME).write_bytes(b'{"invented": true}\n')

        def linked_capture_root(attempt):
            claim = Path(attempt.bindings['claim_runs_root'])
            claim.mkdir()
            (claim / 'instrument_validation').symlink_to(previous_log(attempt).parent, target_is_directory=True)

        cases = (
            ('log hard-linked to a previous attempt', hard_linked_log, 'claim_runs_root is not empty'),
            ('claim runs root links to a previous attempt', linked_root, 'claim_runs_root is a link'),
            ('stale bound in the bound runs root', stale_bound, 'bound_runs_root is not empty'),
            ('capture root links to a previous attempt', linked_capture_root, 'claim_runs_root is not empty'),
        )
        for name, place, detail in cases:
            with self.subTest(case=name):
                attempt = self.attempt()
                place(attempt)
                code, _ = attempt.build()
                self.assertEqual(code, 2, attempt.build_error)
                self.assertIn(detail, attempt.build_error)
        with self.subTest(control='both runs roots exist empty, as prepare leaves them'):
            attempt = self.attempt()
            for name in ('claim_runs_root', 'bound_runs_root'):
                Path(attempt.bindings[name]).mkdir()
            self.assert_admitted_on_both_routes(attempt)

    def test_r15_custody_and_operator_logs_hold_no_links(self):
        """Round 15 class: the launch's own record roots cannot redirect a write through a link."""
        def previous(attempt):
            directory = attempt.work / 'previous-attempt' / 'night'
            directory.mkdir(parents=True, exist_ok=True)
            return directory

        def custody(attempt):
            return attempt.work / 'attempt-custody'

        def linked_night(attempt):
            custody(attempt).mkdir()
            (custody(attempt) / 'night').symlink_to(previous(attempt), target_is_directory=True)

        def linked_custody(attempt):
            custody(attempt).symlink_to(previous(attempt).parent, target_is_directory=True)

        def linked_operator_log(attempt):
            logs = Path(attempt.bindings['operator_log_root'])
            logs.mkdir()
            (logs / 'align-v4-c1-episodes-a.log').symlink_to(previous(attempt) / 'old.log')

        cases = (
            ('custody night directory links to a previous attempt', linked_night, 'custody_root holds a link'),
            ('custody root is a link', linked_custody, 'custody_root is a link'),
            # Since round 16 the operator log root must be fresh, so any entry refuses.
            ('operator log links to a previous attempt', linked_operator_log, 'operator_log_root is not empty'),
        )
        for name, place, detail in cases:
            with self.subTest(case=name):
                attempt = self.attempt()
                place(attempt)
                code, _ = attempt.build()
                self.assertEqual(code, 2, attempt.build_error)
                self.assertIn(detail, attempt.build_error)
        with self.subTest(control='custody holding ordinary records'):
            attempt = self.attempt()
            (custody(attempt) / 'operator-logs').mkdir(parents=True)
            adapter.put(custody(attempt), 'install-record.json', {'invented': True})
            code, _ = attempt.build()
            self.assertEqual(code, 0, attempt.build_error)

    def previous_attempt(self):
        """A previous attempt's directory: a sibling of this attempt, holding its own records."""
        previous = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        adapter.put(previous, 'session.json', {'invented_previous_attempt': True})
        return previous

    @staticmethod
    def tree_bytes(root):
        return {str(path.relative_to(root)): path.read_bytes() if path.is_file() else None
                for path in sorted(root.rglob('*'))}

    def roots_attempt(self, place=None, custody=None):
        """An attempt whose render inputs ``place(attempt)`` changes before prepare."""
        class RootsAttempt(adapter.Attempt):
            def custody_path(self):
                return custody if custody is not None else super().custody_path()

            def prepare(self):
                # One render input changed; every later byte comes from the adapter.
                for name, value in ((place(self) if place else None) or {}).items():
                    self.bindings[name] = str(value)
                    if name == 'claim_runs_root':
                        for slot in ('pre', 'post'):
                            self.bindings[f'{slot}_calibration_dir'] = str(
                                Path(value) / 'instrument_validation' / self.bindings[f'{slot}_attempt_id'])
                return super().prepare()

        return self.attempt(make_attempt=RootsAttempt)

    def test_audit7_high1_stale_pack_digest_refuses_before_reservation(self):
        """Audit 7 HIGH 1: a previous pack's digest in the night plan refuses on both routes."""
        def previous_digest(attempt, night):
            copy = attempt.work / 'previous-pack'
            shutil.copytree(attempt.stage / closure.PACK, copy, symlinks=False)
            tree = copy / 'plan_tree.json'
            tree.write_bytes(tree.read_bytes() + b'\n')  # a prior serialization of the same tree
            previous = adapter.staged_pack_digest(copy)
            self.assertNotEqual(previous, night['hazard_window']['pack']['pack_sha256'])
            night['hazard_window']['pack']['pack_sha256'] = previous

        attempt = self.night_attempt(previous_digest)
        self.assert_refused_on_both_routes(attempt, 'night plan hazard_window.pack.pack_sha256')
        for name in ('claim_runs_root', 'bound_runs_root'):
            self.assertFalse(os.path.lexists(attempt.bindings[name]))

    def test_audit7_high2_stale_operator_log_root_refuses_before_reservation(self):
        """Audit 7 HIGH 2: an operator log root naming a previous attempt's logs refuses on both routes."""
        record = b'2001-01-01T00:00:00Z chain_start plan=previous-attempt\n'

        def previous_logs(root):
            logs = root / 'operator-logs'
            logs.mkdir(parents=True)
            (logs / 'window-chain.log').write_bytes(record)
            return {'operator_log_root': logs}

        outside = self.previous_attempt()
        for name, place, previous, detail in (
                ('previous logs beside this attempt (audit reproduction)',
                 lambda attempt: previous_logs(attempt.work / 'previous-attempt'), None,
                 'operator_log_root is not empty'),
                ('a previous attempt directory', lambda attempt: previous_logs(outside), outside,
                 "operator_log_root resolves outside this attempt's directory")):
            with self.subTest(case=name):
                attempt = self.roots_attempt(place)
                previous = previous or attempt.work / 'previous-attempt'
                before = self.tree_bytes(previous)
                self.assert_refused_on_both_routes(attempt, detail)
                self.assertEqual(self.tree_bytes(previous), before)
                self.assertEqual((previous / 'operator-logs/window-chain.log').read_bytes(), record)

    def test_audit7_med_mixed_launch_markers_refuse_at_prepare(self):
        """Audit 7 MED: a collection selection mixing marked and legacy configs refuses at prepare."""
        def tag_all(work_holder):
            def edit(tree):
                extra = {}
                for stage in tree['stage_graph']:
                    if stage['kind'] != 'campaign_collection':
                        continue
                    manifest = Path(stage['input']['path'])
                    authority = work_holder['work'] / 'authority'
                    for row in closure.decode((authority / manifest).read_bytes())['executed_order']:
                        name = manifest.parent / row['config']
                        config = closure.decode((authority / name).read_bytes())
                        if 'launch_lineage_required' not in config['run_metadata']['tags']:
                            config['run_metadata']['tags'].append('launch_lineage_required')
                            extra[str(name)] = adapter.series.raw_json(config)
                return extra
            return edit

        def staged(attempt):
            return closure.decode((attempt.stage / closure.PACK / 'plan_tree.json').read_bytes())

        with self.subTest(case='the invented first stage mixes 7 marked of 11'):
            attempt = self.attempt()
            with self.assertRaisesRegex(ValueError, 'mixes marker-bearing and legacy configs'):
                closure.campaign_marker_refusal(attempt.view, staged(attempt))
        with self.subTest(control='every dispatched config carries the marker'):
            holder = {}

            class Tagged(adapter.Attempt):
                def __init__(self, work, *rest):
                    holder['work'] = work
                    super().__init__(work, *rest)

            attempt = self.attempt(make_attempt=Tagged, edit_source=tag_all(holder))
            closure.campaign_marker_refusal(attempt.view, staged(attempt))

    def test_r16_staged_pack_digest_is_the_committed_d134_digest(self):
        """The recomputed pack digest is D-134's committed digest of the same bytes, in both forms."""
        from joulewise.arm_readiness import committed_pack_tree_sha256

        for form in ('copy', 'link'):
            with self.subTest(form=form):
                work = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
                subprocess.run(['git', 'clone', '-q', '--bare', HERE / 'suite/history.bundle', work / 'history.git'],
                               check=True)
                attempt = adapter.Attempt(work, 'valid_24_closure', form, None)
                staged = attempt.view / closure.PACK
                reference = work / 'committed'
                shutil.copytree(staged, reference / 'pack', symlinks=False)
                for argv in (['init', '-q'], ['add', '-f', 'pack'], ['-c', 'user.name=invented', '-c',
                             'user.email=invented@invalid', 'commit', '-qm', 'invented pack']):
                    subprocess.run(['git', '-C', str(reference), *argv], check=True, capture_output=True)
                committed = committed_pack_tree_sha256(reference / 'pack')
                self.assertEqual(closure.staged_pack_sha256(staged), committed)
                self.assertEqual(adapter.staged_pack_digest(staged), committed)
                night = closure.decode(attempt.night.read_bytes())
                self.assertEqual(night['hazard_window']['pack']['pack_sha256'], committed)

    def test_r16_previous_attempt_digest_fields_refuse_before_reservation(self):
        """Round 16 class: each digest the night plan carries is recomputed; a previous value refuses."""
        def pack(field, value):
            def change(attempt, night):
                night['hazard_window']['pack'][field] = value(attempt, night) if callable(value) else value
            return change

        def previous_head(attempt, night):
            return attempt.git('rev-parse', attempt.execution + '^').decode().strip()

        def head(field):
            def change(attempt, night):
                night[field] = previous_head(attempt, night)
            return change

        def window_env(attempt, night):
            night['hazard_window']['window_env']['sha256'] = closure.digest(b'WAIVER_PATH=previous\n')

        def registration(attempt, night):
            night['hazard_window']['registration'] = {
                'path': night['hazard_window']['window_env']['path'],
                'sha256': closure.digest(b'WAIVER_PATH=previous\n')}

        tree_digest = lambda attempt, night: closure.digest(  # noqa: E731
            (attempt.stage / closure.PACK / 'plan_tree.json').read_bytes() + b'\n')
        cases = (
            ('pack digest', pack('pack_sha256', '42' * 32), 'night plan hazard_window.pack.pack_sha256'),
            ('pack digest absent', pack('pack_sha256', None), 'night plan hazard_window.pack.pack_sha256'),
            ('plan tree digest', pack('plan_tree_sha256', tree_digest), 'night plan hazard_window.pack.plan_tree_sha256'),
            ('window env digest', window_env, 'prepared control SHA-256 mismatch'),
            ('registration digest', registration, 'prepared control SHA-256 mismatch'),
            ('repository head', head('repo_head'), 'night plan repo_head'),
            ('measurement head', head('measurement_head'), 'night plan measurement_head'),
            ('an unchecked digest field', pack('previous_sha256', '0' * 64), 'unverified digest'),
        )
        for name, change, detail in cases:
            with self.subTest(case=name):
                attempt = self.night_attempt(change)
                code, _ = attempt.build()
                self.assertEqual(code, 2, attempt.build_error)
                self.assertIn(detail, attempt.build_error)

    def test_r16_previous_attempt_write_roots_refuse_before_reservation(self):
        """Round 16 class: each root the launch writes resolves inside this attempt's own directory."""
        for name in ('operator_log_root', 'claim_runs_root', 'bound_runs_root', 'claim_backup_destination',
                     'bound_backup_destination', 'custody_root', 'operator_log_root through a link'):
            with self.subTest(root=name):
                field = name.split()[0]
                previous = self.previous_attempt()
                target = previous / field
                adapter.put(target, 'previous-record.json', {'invented': True})
                before = self.tree_bytes(previous)
                if field == 'custody_root':
                    attempt = self.roots_attempt(custody=target)
                elif name.endswith('through a link'):
                    def through_link(attempt, previous=previous):
                        (attempt.work / 'logs-link').symlink_to(previous, target_is_directory=True)
                        return {field: attempt.work / 'logs-link' / field}
                    attempt = self.roots_attempt(through_link)
                else:
                    attempt = self.roots_attempt(lambda attempt, field=field, target=target: {field: target})
                code, _ = attempt.build()
                self.assertEqual(code, 2, attempt.build_error)
                self.assertIn(f"{field} resolves outside this attempt's directory", attempt.build_error)
                self.assertEqual(self.tree_bytes(previous), before)

    def test_r13_arguments_a_consumer_rejects_or_that_disagree_with_the_plan(self):
        """Round 13 sweep: each such rendered argument refuses at the shared preflight (builder exit 2)."""
        def stage(kind, slot=None):
            def select(tree):
                if slot is not None:
                    return capture_arguments(tree, slot)
                return adapter.arguments(next(row for row in tree['stage_graph'] if row['kind'] == kind))
            return select

        def flag(name):
            return [adapter.literal(name)]

        def value(name, item, kind='literal'):
            return [adapter.literal(name), {'kind': kind, 'value': item}]

        reservation, collection = stage('bracket_reservation'), stage('campaign_collection')
        pre, post = stage(None, 'pre'), stage(None, 'post')
        instrument = value('--instrument-calibration-dir', 'pre_calibration_dir', 'binding')
        cases = (
            ('reservation runs root', reservation, ('--runs-root', '/synthetic-other-runs'),
             "reservation --runs-root must be this attempt's"),
            ('derivation-only capture', pre, flag('--derivation-only'), 'C1 capture is a bracket capture'),
            ('test-only sampler', pre, flag('--sampler-direct-for-test'), 'test-only capture option'),
            ('test-only time scale', post, value('--time-scale-for-test', '0.5'), 'test-only capture option'),
            ('pulse count', pre, value('--pulse-count', '40'), "frozen protocol's pulse count"),
            ('sampler timeout', post, value('--sampler-ready-timeout-s', '0'), 'must be finite and positive'),
            ('dry run', collection, flag('--dry-run'), 'unsupported C1 campaign mode'),
            ('block limit', collection, value('--max-blocks', '1'), 'G2B_SHAKEDOWN'),
            ('instrument power policy', collection, instrument + value('--instrument-power-policy', 'ac_low_power'),
             'instrument power policy differs from the reserved policy'),
        )
        for name, select, extra, detail in cases:
            with self.subTest(case=name):
                def edit(tree, select=select, extra=extra):
                    if isinstance(extra, tuple):  # replace an option the template already carries
                        set_option(select(tree), extra[0], 'literal', extra[1])
                    else:
                        select(tree).extend(extra)
                    return {}

                attempt = self.attempt(edit_source=edit)
                code, _ = attempt.build()
                self.assertEqual(code, 2, attempt.build_error)
                self.assertIn(detail, attempt.build_error)
        with self.subTest(control='instrument power policy equal to the reserved policy'):
            def matched(tree):
                collection(tree).extend(instrument + value('--instrument-power-policy', 'ac_high_power'))
                return {}

            attempt = self.attempt(edit_source=matched)
            code, _ = attempt.build()
            self.assertEqual(code, 0, attempt.build_error)

    def test_r11_caller_ledger_pointer_is_refusal_only(self):
        """Ruling item 2: a caller's CALIBRATION_LEDGER may only refuse; unset imposes nothing."""
        attempt = self.attempt()
        code, packet = attempt.build()
        self.assertEqual(code, 0, attempt.build_error)
        attempt.deliver(packet)
        canonical = attempt.stage / adapter.LEDGER
        outside = adapter.put(attempt.work, 'outside-ledger.jsonl', canonical.read_bytes())
        outside.chmod(0)  # an outside path refuses before its bytes are read
        self.addCleanup(outside.chmod, 0o600)
        cases = (('unset', None, None), ('canonical file', str(canonical), None),
                 ('launch view alias', str(attempt.view / adapter.LEDGER), None),
                 ('empty', '', 'CALIBRATION_LEDGER is empty'),
                 ('missing', str(attempt.view / 'runs/absent-ledger.jsonl'), 'missing'),
                 ('different staged file', str(attempt.view / 'inputs/epoch.json'), 'canonical C1 path'),
                 ('outside', str(outside), 'outside R/S'))
        for name, value, refusal in cases:
            with self.subTest(case=name), patch.dict(os.environ):
                os.environ.pop('CALIBRATION_LEDGER', None)
                if value is not None:
                    os.environ['CALIBRATION_LEDGER'] = value
                if refusal is None:
                    session.c1_arm_preflight(attempt.handoff_file, now_epoch_s=adapter.NOW)
                else:
                    with self.assertRaisesRegex(session.PacketKitMismatch, refusal):
                        session.c1_arm_preflight(attempt.handoff_file, now_epoch_s=adapter.NOW)
        with patch.dict(os.environ, {'CALIBRATION_LEDGER': str(attempt.view / adapter.LEDGER)}):
            self.assertEqual(self.consumer_outcomes(attempt), (0, 'admit', 1, 1), attempt.cli_error)

    def test_frozen_lite_decisions(self):
        completed = subprocess.run([sys.executable, '-B', str(HERE / 'suite/run.py'),
                                    '--adapter', str(HERE / 'adapter.py')], cwd=ROOT,
                                   env={**os.environ, 'PYTHONPATH': os.pathsep.join([str(ROOT / 'tests'), str(ROOT)])},
                                   capture_output=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        self.assertEqual(completed.stdout, (HERE / 'suite/expected.jsonl').read_bytes())


class ReservedIdentityTests(unittest.TestCase):
    def test_reserved_power_policy_precedence(self):
        from joulewise.b5.plan import POWER_POLICY
        from scripts import reserve_calibration_window_bracket as reservation

        cases = (({'power_policy': 'epoch'}, {'power_policy': 't1'}, 'epoch'),
                 ({}, {'power_policy': 't1'}, 't1'), ({'power_policy': ''}, {}, POWER_POLICY), ({}, {}, POWER_POLICY))
        for epoch, t1, expected in cases:
            with self.subTest(epoch=epoch, t1=t1):
                # The HAZARD identity records exactly this value (_hazard_measured_identity).
                self.assertEqual(reservation.reserved_power_policy(epoch, t1), expected)


class C1ClosedEnvironmentTests(unittest.TestCase):
    """A3 and A5 over one invented spare-enabled attempt."""

    @classmethod
    def setUpClass(cls):
        cls.work = Path(cls.enterClassContext(tempfile.TemporaryDirectory())).resolve()
        cls.enterClassContext(patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1'}))
        for name in [name for name in os.environ if name in adapter.chain.C1_ENVIRONMENT_NAMES
                     or any(fnmatch.fnmatchcase(name, p) for p in ('JOULEWISE_*',))]:
            os.environ.pop(name)
        subprocess.run(['git', 'clone', '-q', '--bare', HERE / 'suite/history.bundle', cls.work / 'history.git'],
                       check=True)
        cls.attempt = adapter.Attempt(cls.work, 'with_spare', 'copy', None)
        code, packet = cls.attempt.build()
        if code:
            raise AssertionError(cls.attempt.build_error)
        cls.attempt.deliver(packet)
        cls.chain_text = (cls.attempt.stage / 'controls/chain.zsh').read_text()
        cls.programs = chain_programs(cls.chain_text, cls.attempt.view)

    def sweep_names(self):
        reads, _, _ = chain_environment_reads(self.programs)
        names = set(reads) | set(adapter.chain.C1_ENVIRONMENT_NAMES) | set(rendered_environment(self.attempt))
        # Unlisted names that the patterns close: a future JOULEWISE_ switch
        # and interpreter switches that would change which code or checks run.
        names |= {'JOULEWISE_UNLISTED_SWITCH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'PYTHONPATH',
                  'PYTHONSAFEPATH', 'PYTHONUSERBASE', 'PYTHONWARNINGS'}
        return sorted(names - set(adapter.chain.C1_LAUNCH_ENVIRONMENT))

    def stale(self, name):
        if name == 'PYTHONOPTIMIZE':
            return '2'
        if name == 'PYTHONWARNINGS':
            return 'error'
        return str(self.work / 'stale' / name)

    def test_closed_environment_covers_every_consumer_read(self):
        chain = adapter.chain
        self.assertEqual({Path(program).name for program in self.programs}, {
            'reserve_calibration_window_bracket.py', 'validate_powermetrics_fiducial.py', 'run_campaign.py',
            'recover_calibration_ledger.py', 'b5_window_calibration_verdict.py'})
        reads, computed, modules = chain_environment_reads(self.programs)
        self.assertGreater(modules, 100)
        self.assertEqual(computed, KNOWN_COMPUTED_READS)
        environment = rendered_environment(self.attempt)
        closed = set(environment) | set(chain.C1_LAUNCH_ENVIRONMENT)
        unclosed = sorted(name for name in reads if name not in closed and not any(
            fnmatch.fnmatchcase(name, pattern) for pattern in chain.C1_ENVIRONMENT_PATTERNS))
        self.assertEqual(unclosed, [], 'a chain module reads a variable the C1 chain does not close')
        shell = chain_shell_reads(self.chain_text)
        self.assertEqual(shell, {'NIGHT_DIR', 'NIGHT_VERIFY_ONLY', 'NIGHT_RESERVATION_ARGV_ONLY'})
        # The list is derived from the code: no stale or invented entries.
        self.assertEqual(set(chain.C1_ENVIRONMENT_NAMES) - set(reads) - shell, set())
        self.assertTrue(set(chain.C1_LAUNCH_ENVIRONMENT) <= shell)
        print(f'C1 environment inventory: {len(reads)} variables read across {modules} chain modules')

    def test_renderer_emits_the_environment_that_preflight_judges(self):
        environment = rendered_environment(self.attempt)
        self.assertEqual(environment_block(self.chain_text), adapter.chain.c1_environment_lines(environment))
        judged = []
        check = closure._check_consumers

        def observe(*args, **kwargs):
            judged.append(dict(os.environ))
            return check(*args, **kwargs)

        with patch.object(closure, '_check_consumers', side_effect=observe):
            self.attempt.context()
        self.assertEqual(judged, [adapter.chain.apply_c1_environment(environment, dict(os.environ))])
        consumed = run_closed_environment(None, {}, self.work, block=environment_block(self.chain_text))
        for name, value in environment.items():
            self.assertEqual(consumed['environment'].get(name), value, name)
        self.assertEqual(consumed['c1_context'], json.loads(environment['JOULEWISE_C1_INPUTS']))

    def test_ambient_stale_values_never_change_what_is_consumed(self):
        """A5 sweep: one stale launch value per variable a consumer reads."""
        block = environment_block(self.chain_text)
        baseline = run_closed_environment(None, {}, self.work, block=block)
        check = closure._check_consumers
        judged = []

        def observe(*args, **kwargs):
            judged.append({name: value for name, value in os.environ.items() if name in names
                           or any(fnmatch.fnmatchcase(name, p) for p in adapter.chain.C1_ENVIRONMENT_PATTERNS)})
            return check(*args, **kwargs)

        names = self.sweep_names()
        with patch.object(closure, '_check_consumers', side_effect=observe):
            expected = self.attempt.context()[-1]
        baseline_judged = judged.pop()
        for name in names:
            with self.subTest(variable=name):
                stale = self.stale(name)
                # The chain: the consumers' own readers after the rendered block.
                self.assertEqual(run_closed_environment(None, {name: stale}, self.work, block=block), baseline)
                # Preflight: the environment it judges and what it selects.
                with patch.dict(os.environ, {name: stale}), \
                        patch.object(closure, '_check_consumers', side_effect=observe):
                    if name == 'CALIBRATION_LEDGER':
                        # O2a: a caller's ledger pointer to another file refuses.
                        with self.assertRaisesRegex(ValueError, 'outside R/S'):
                            self.attempt.context()
                        continue
                    self.assertEqual(self.attempt.context()[-1], expected)
                self.assertEqual(judged.pop(), baseline_judged)
        print(f'C1 closed-environment sweep: {len(names)} stale launch variables')

    def test_listed_consumer_checks_refuse_digests_of_non_exact_bytes(self):
        """A3 sweep: each consumer digest check over near-miss bytes.

        The stale-variable half of the sweep is the A5 sweep above: every
        listed check runs inside the one closed consumer environment.
        """
        from joulewise.calibration_exits import RefusalCode
        from joulewise.calibration_ledger import CalibrationLedgerError
        from scripts import reserve_calibration_window_bracket as reservation

        attempt, cases = self.attempt, 0
        # Reservation: --plan-sha256 must cover the exact frozen plan bytes.
        plan = attempt.view / closure.PACK / adapter.series.C1_PLAN
        raw = plan.read_bytes()
        plan_id = json.loads(raw)['plan_id']
        reservation.verify_frozen_plan(plan, plan_id=plan_id, plan_sha256=closure.digest(raw))
        for variant in non_exact(raw):
            with self.subTest(check='reservation frozen plan', variant=variant[-12:]):
                with self.assertRaises(CalibrationLedgerError) as caught:
                    reservation.verify_frozen_plan(plan, plan_id=plan_id, plan_sha256=closure.digest(variant))
                self.assertEqual(caught.exception.code, RefusalCode.PLAN_HASH_MISMATCH)
                with self.assertRaisesRegex(ValueError, 'calibration_plan_hash_mismatch'):
                    closure.consumer_check('reservation', lambda: reservation.verify_frozen_plan(
                        plan, plan_id=plan_id, plan_sha256=closure.digest(variant)))
                cases += 1
        # Reservation and capture: the starting ledger pin covers exact bytes.
        ledger = attempt.stage / adapter.LEDGER
        ledger_raw = ledger.read_bytes() or b'{}\n'
        work = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        copy = adapter.put(work, 'ledger.jsonl', ledger_raw)
        for variant in non_exact(ledger_raw):
            with self.subTest(check='starting ledger', variant=variant[-12:]):
                context = {'ledger': {'path': str(copy), 'sha256': closure.digest(variant)}}
                with patch.dict(os.environ, {'JOULEWISE_C1_INPUTS': json.dumps(context)}):
                    with self.assertRaisesRegex(ValueError, 'starting ledger SHA-256 mismatch'):
                        closure.runtime_ledger(copy, starting=True)
                cases += 1
        # SHADE: the exported manifest pin covers the exact cache file bytes.
        repo, stage = work / 'R', work / 'S'
        repo.mkdir()
        data = b'Synthetic cache export.\n'
        revision = '4' * 40
        adapter.put(stage / 'cache/joulewise/shade' / revision, 'README.txt', data)

        def manifest(raw):
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            return closure.digest(b'README.txt\0' + blob.encode() + b'\n')

        spec = {'task_factory': 'joulewise.align.apple.pilot:offline_shade_task',
                'task_kwargs': {'task_pair': 'invented', 'commit': revision}}
        shade_environment = {'JOULEWISE_C1_INPUTS': json.dumps({'repo': str(repo), 'stage': str(stage)}),
                             'XDG_CACHE_HOME': str(stage / 'cache')}
        with patch.dict(os.environ, shade_environment):
            closure.shade_dependency({**spec, 'task_kwargs': {**spec['task_kwargs'], 'file_sha256': manifest(data)}})
            for variant in non_exact(data):
                with self.subTest(check='SHADE export manifest', variant=variant[-12:]):
                    with self.assertRaisesRegex(ValueError, 'upstream_manifest_mismatch'):
                        closure.shade_dependency(
                            {**spec, 'task_kwargs': {**spec['task_kwargs'], 'file_sha256': manifest(variant)}})
                    cases += 1
        # Config source descriptors: the staged descriptor digest covers exact bytes.
        roots = closure.Roots(repo, stage)
        view = closure.LaunchView(roots, work / 'launch')
        source = adapter.put(stage, 'inputs/source.json', {'invented': True})
        source_raw = source.read_bytes()
        for variant in non_exact(source_raw):
            with self.subTest(check='config source descriptor', variant=variant[-12:]):
                document = {'source': {'path': str(source), 'sha256': closure.digest(variant)}}
                with self.assertRaisesRegex(ValueError, 'staged descriptor SHA-256 mismatch'):
                    closure.config_references(document, stage / 'inputs/config.json', view, run_campaign)
                cases += 1
        print(f'C1 consumer digest sweep: {cases} near-miss digests refused')
