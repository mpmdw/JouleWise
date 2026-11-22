"""Run the frozen C1 decisions through the production packet and arm entry points."""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
from unittest.mock import patch

from align.test_v4_cadence import write_battery_log
from joulewise.align.apple import powermode, v4_registration as closure
from joulewise.b5 import chain
from scripts import align_v4_next_arm_packet as builder, align_v4_series as series
from scripts import align_v4_session as session, bytes_h_session as staging
from scripts import reserve_calibration_window_bracket as reservation


NOW = 111.0
PACKET = Path(closure.PACKET)
LEDGER = Path(closure.LEDGER)
POLICY = Path('configs/campaign_policies/quiet_mac_p2_production.json')
HEAD = Path('configs/calibration/calibration_ledger_head.json')
DERIVATION = Path('configs/campaigns/fixture-derivation/settled_corpus.json')
KIT = series.kit_path('C1')
SELECTED = {'ledger': LEDGER, 'head_pin': HEAD, 'policy': POLICY, 'derivation': DERIVATION}


def put(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else series.raw_json(data))
    return path


def check_view(request):
    try:
        closure.verify_view(request['git'], request['repo'], request['stage'],
                            delivery_ref=request['delivery_ref'], delivery_commit=request['delivery_commit'],
                            execution_commit=request['commit'])
    except (OSError, ValueError, KeyError, TypeError):
        return {'decision': 'refuse', 'host': 0}
    return {'decision': 'admit', 'host': 0}


def literal(value):
    return {'kind': 'literal', 'value': str(value)}


def arguments(stage):
    return stage['launch']['commands'][0]['argv_template']['arguments']


def option(args, flag, kind, value):
    args.extend([literal(flag), {'kind': kind, 'value': str(value)}])


class Attempt:
    def __init__(self, work, fixture, form, edit_source):
        self.work = work
        self.git_dir = work / 'authority'
        self.repo = work / 'R'
        self.stage = work / 'S'
        self.view = work / 'launch'
        self.night = self.stage / 'controls/night.json'
        self.host = work / 'host'
        self.handoff_file = work / 'handoff.json'
        self.prepared_file = work / 'prepared.json'
        self.fixture = fixture
        self.form = form
        self.now = 141.0 if fixture == 'expired_141' else NOW
        history = work / 'history.git'
        self.identities = json.loads((Path(__file__).parent / 'suite/history-identity.json').read_bytes())
        subprocess.run(['git', 'clone', '-q', '--local', '--shared', history, self.git_dir], check=True)
        self.git('update-ref', self.identities['pushed_ref'], self.identities['record_commit'])
        self.git('config', 'user.name', 'Invented Fixture')
        self.git('config', 'user.email', 'fixture@invalid')
        self.plan = closure.decode((self.git_dir / KIT / series.C1_PLAN).read_bytes())
        self.source = closure.decode((self.git_dir / KIT / 'plan_tree.json').read_bytes())
        self.bindings = {name: str(work / name) for name in ('claim_runs_root', 'bound_runs_root',
                         'operator_log_root', 'pre_calibration_dir', 'post_calibration_dir',
                         'claim_backup_destination', 'bound_backup_destination')}
        self.bindings.update(repo_root=str(self.view), ledger_path=str(self.view / LEDGER),
                             identity_epoch_json=str(self.stage / 'inputs/epoch.json'),
                             t1_bindings_json=str(self.stage / 'inputs/t1.json'),
                             bracket_session_id='fixture-session', pre_attempt_id='fixture-pre',
                             post_attempt_id='fixture-post')
        self.complete_arguments()
        payloads = edit_source(self.source) if edit_source else {}
        self.ledger = payloads.pop(LEDGER.as_posix(), b'')
        for name, raw in payloads.items():
            put(self.git_dir, name, raw)
        if not (self.git_dir / POLICY).exists():
            put(self.git_dir, POLICY, {'fixture': 'default campaign policy'})
        if not payloads.get(str(HEAD)):
            put(self.git_dir, HEAD, {'sequence': 0, 'head_digest': '0' * 64,
                                   'ledger_schema': 'joulewise.calibration_observation_ledger.v1'})
        runbook = "\n".join([chain.RUNBOOK_SCREEN_START, 'PRE_CAL_FIDUCIAL_MAX_S=1.0',
                             chain.RUNBOOK_SCREEN_FUNCTION, '  value=$(printf 1.0)', '}', ''])
        put(self.git_dir, chain.RUNBOOK_RELATIVE, runbook.encode())
        self.mutate_source()
        put(self.git_dir, KIT / 'plan_tree.json', self.source)
        self.execution = self.commit('Invented C1 execution inputs')
        projection_fixtures = {'ordinary22_relabel', 'sentinels_wrong_positions', 'stale_w1_desk_r1_pointer',
                               'pending_desk_forged_status_and_ready', 'installed_frequency_helper'}
        if fixture in projection_fixtures:
            self.mutate_evidence()
        # Use the execution template for K1. Keep the exact frozen history
        # commits as its evidence ancestors.
        self.identities['series_commit'] = self.rev()
        closure.export_repo(self.git_dir, self.execution, self.repo)
        self.stage.mkdir()
        self.handoff = {'window': 'C1', 'git': str(self.git_dir), 'repo': str(self.repo),
                        'stage': str(self.stage), 'view': str(self.view), 'execution_commit': self.execution}
        self.prepare()
        put(self.work, self.prepared_file.name, self.handoff)

    def git(self, *args):
        return closure.git(self.git_dir, *args)

    def rev(self):
        return self.git('rev-parse', 'HEAD').decode().strip()

    def commit(self, summary):
        self.git('add', '-A')
        self.git('commit', '-qm', summary)
        return self.rev()

    def complete_arguments(self):
        for stage in self.source['stage_graph']:
            args = arguments(stage)
            if stage['kind'] == 'bracket_reservation':
                self.reservation_stage = stage['stage_id']
                for flag, value in (('--session-id', 'bracket_session_id'), ('--runs-root', 'claim_runs_root'),
                                    ('--identity-epoch-json', 'identity_epoch_json'), ('--t1-bindings-json',
                                     't1_bindings_json'), ('--pre-attempt-id', 'pre_attempt_id'),
                                    ('--post-attempt-id', 'post_attempt_id'), ('--pre-custody-locator',
                                     'pre_calibration_dir'), ('--post-custody-locator', 'post_calibration_dir')):
                    if literal(flag) not in args:
                        option(args, flag, 'binding', value)
                for flag, value in (('--window-id', 'C1'), ('--plan-id', self.source['plan']['plan_id']),
                                    ('--plan-sha256', self.source['plan']['actual_sha256']),
                                    ('--evidence-root-id', 'fixture-evidence')):
                    if literal(flag) not in args:
                        option(args, flag, 'literal', value)
            if stage['kind'] == 'bound_derivation':
                if literal('--neg8-drift-bound-output') not in args:
                    option(args, '--neg8-drift-bound-output', 'literal', self.work / 'derived.json')
                if literal('--runs-dir') not in args:
                    option(args, '--runs-dir', 'binding', 'bound_runs_root')

    def mutate_source(self):
        fixture = self.fixture
        if fixture == 'drop_required_derivation_before_build':
            (self.git_dir / DERIVATION).unlink()
        if fixture == 'drop_default_policy_before_build':
            (self.git_dir / POLICY).unlink()
        if fixture == 'installed_frequency_helper':
            source = 'scripts/zero_ntp_frequency.c'
            data = b'/* invented helper identity */\n'
            # This file is already bound in the frozen history. Use that exact
            # fixture source if it exists.
            if (self.git_dir / source).is_file():
                data = (self.git_dir / source).read_bytes()
            else:
                put(self.git_dir, source, data)
            put(self.git_dir, closure.REGISTRATION + 'registration_receipt.json',
                {'artifacts': {source: closure.digest(data)}})

    def mutate_evidence(self):
        state_path = self.identities['series_path']
        state = closure.decode((self.git_dir / state_path).read_bytes())
        if self.fixture in {'ordinary22_relabel', 'sentinels_wrong_positions'}:
            ref = state['next_plan']
            projection = closure.decode((self.git_dir / ref['path']).read_bytes())
            rows = projection['members']
            if self.fixture == 'ordinary22_relabel':
                del rows[22:]
                for row in rows:
                    if row['role'] == 'sentinel':
                        row['role'] = 'D'
                rows[19]['role'] = rows[20]['role'] = 'sentinel'
            else:
                rows[21], rows[20] = rows[20], rows[21]
                for row in rows:
                    row.pop('ordinal', None)
            state['sentinel_ids'] = [row['run_id'] for row in rows if row['role'] == 'sentinel']
            ref['sha256'] = closure.digest(put(self.git_dir, ref['path'], projection).read_bytes())
        elif self.fixture in {'stale_w1_desk_r1_pointer', 'pending_desk_forged_status_and_ready',
                              'installed_frequency_helper'}:
            record_path = self.identities['record_path']
            w1 = closure.decode((self.git_dir / record_path).read_bytes())
            if self.fixture == 'stale_w1_desk_r1_pointer':
                state['last_passed_record'] = w1['previous_record']
                put(self.git_dir, 'scripts/run_night.py', b'invented stale W1 artifact bytes\n')
                w1['code_commit'] = self.commit('Invented stale W1 code')
                original = self.git('show', f'{self.execution}:scripts/run_night.py')
                put(self.git_dir, 'scripts/run_night.py', original)
            elif self.fixture == 'installed_frequency_helper':
                w1['code_commit'] = self.execution
            else:
                desk = w1['sources']['desk']
                desk['sha256'] = closure.digest(put(self.git_dir, desk['path'], {'status': 'pending'}).read_bytes())
            record_sha = closure.digest(put(self.git_dir, record_path, w1).read_bytes())
            record_commit = self.commit('Invented changed W1 evidence')
            self.identities['record_commit'] = record_commit
            self.git('update-ref', self.identities['pushed_ref'], record_commit)
            state['previous_record'] = {'commit': record_commit, 'path': record_path, 'sha256': record_sha}
            if self.fixture != 'stale_w1_desk_r1_pointer':
                state['last_passed_record'] = state['previous_record']
        put(self.git_dir, state_path, state)
        self.commit('Invented coherent series change')

    def prepare(self):
        def read(path):
            return (self.repo / path).read_bytes()

        files, self.tree = staging.render_measurement_files(
            KIT, series.pack_id('C1'), read, lambda path: read(path) if (self.repo / path).is_file() else None)
        for path in sorted((self.repo / KIT).rglob('*')):
            if path.is_file() and path.name != 'plan_tree.json':
                files[closure.PACK / path.relative_to(self.repo / KIT)] = path.read_bytes()
        if self.fixture == 'unrecognized_binding_kind':
            stage = next(row for row in self.tree['stage_graph'] if row['kind'] == 'bound_derivation')
            arguments(stage)[1]['kind'] = 'invented_unknown_kind'
        if self.fixture in {'absolute_external_sidecar', 'ambient_shade_only'}:
            stage = next(row for row in self.tree['stage_graph'] if row['kind'] == 'campaign_collection')
            directory = Path(arguments(stage)[0]['value'])
            order = closure.decode(files[directory / 'order_manifest.json'])
            name = directory / order['executed_order'][0]['config']
            config = closure.decode(files[name])
            if self.fixture == 'absolute_external_sidecar':
                path = put(self.work, 'outside.json', {'invented': True})
                config['workload_profile']['generator_sidecar_ref'] = str(path)
            else:
                config['workload_profile']['prompt_text'] = json.dumps({
                    'task_factory': 'joulewise.align.apple.pilot:offline_shade_task',
                    'task_kwargs': {'task_pair': 'invented'}})
            files[name] = series.raw_json(config)
        if self.fixture == 'closed_stage_wrong_order':
            name = self.second_order()
            order = closure.decode(files[name])
            order['executed_order'] = order['executed_order'][:-2]
            files[name] = series.raw_json(order)
        files[closure.PACK / 'plan_tree.json'] = series.raw_json(self.tree)
        files[closure.PACK / 'plan_tree.sha256'] = (
            closure.digest(files[closure.PACK / 'plan_tree.json']) + '  plan_tree.json\n').encode()
        if self.fixture != 'drop_initial_ledger_before_build':
            files[LEDGER] = self.ledger
        files.update({Path('inputs/epoch.json'): b'{}\n', Path('inputs/t1.json'): b'{}\n'})
        window_env = self.stage / 'controls/window.env'
        window_env_raw = b'WAIVER_PATH=none\n'
        files[window_env.relative_to(self.stage)] = window_env_raw
        chain_path = self.stage / 'controls/chain.zsh'
        tree_digest = closure.digest(files[closure.PACK / 'plan_tree.json'])
        plan_id = self.tree['plan']['plan_id']
        pin = {'path': str(self.stage / LEDGER), 'sha256': closure.digest(self.ledger)}
        try:
            chain_raw = chain.render_chain(
                tree=self.tree, tree_sha256=tree_digest, stages=chain.stage_plan(self.tree),
                bindings=self.bindings, measurement_root=self.view, pack_root=self.view / closure.PACK,
                plan_id=plan_id, runbook_text=(self.repo / chain.RUNBOOK_RELATIVE).read_text(),
                c1_inputs=closure.execution_inputs(self.handoff, pin))
        except chain.ChainRenderError:
            if self.fixture != 'unrecognized_binding_kind':
                raise
            chain_raw = b'# invalid binding refuses before launch\n'
        files[chain_path.relative_to(self.stage)] = chain_raw
        files[Path(str(chain_path.relative_to(self.stage)) + '.sha256')] = chain.sidecar_bytes(chain_raw, chain_path.name)
        self.night_data = {'plan_id': plan_id, 't0_epoch_s': 1000, 'chain_path': str(chain_path),
                           'chain_sha256_path': str(chain_path) + '.sha256', 'hazard_window': {
            'bindings': self.bindings, 'T_stream_max_s': 10, 'settle_s': chain.SETTLE_S,
            'window_env': {'path': str(window_env), 'sha256': closure.digest(window_env_raw)},
            'thresholds': {'clock': {'frequency_error_budget_s': 1}},
            'pack': {'pack_root': str(self.view / closure.PACK), 'plan_tree_sha256': tree_digest}}}
        files[self.night.relative_to(self.stage)] = series.raw_json(self.night_data)
        self.state = {'session_root': str(self.work / 'install'), 'measurement_root': str(self.view), 'source_measurement_root': str(self.repo),
                      'plan_path': str(self.night), 'plan_sha256': closure.digest(series.raw_json(self.night_data)),
                      'v4_series': {'window_id': 'W1' if self.fixture == 'session_downgrade' else 'C1'},
                      'inputs': {'custody_root': str(self.work / 'attempt-custody')}}
        files[Path('session.json')] = series.raw_json(self.state)
        for name, raw in files.items():
            if self.form == 'link' and name == closure.PACK / series.C1_PLAN:
                path = self.stage / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(self.repo / KIT / series.C1_PLAN)
            else:
                put(self.stage, name, raw)
        closure.declare_outputs(self.repo, self.stage, files)
        # Reserve the packet directory before producing the detached blob.
        (self.stage / PACKET.parent).mkdir(exist_ok=True)
        closure.link_launch_view(closure.Roots(self.repo, self.stage), self.view)
        if self.fixture == 'ambient_parent_manifest':
            from scripts import run_campaign
            put(self.work, run_campaign.PROSPECTIVE_ANALYSIS_MANIFEST_V3_NAME,
                {'stage_manifests': [{'manifest_path': f'S/{self.second_order()}'}],
                 'metadata': {'path': '/DO-NOT-FOLLOW', 'sha256': '0' * 64}})

    def second_order(self):
        stages = [row for row in self.tree['stage_graph'] if row['kind'] == 'campaign_collection']
        science_stage = self.plan['members'][-1]['stage_id']
        configured = next(row for row in stages if row['stage_id'] == science_stage)
        return Path(arguments(configured)[0]['value']) / 'order_manifest.json'

    def build(self):
        output = self.work / 'packet-output.json'
        argv = ['--repo', str(self.git_dir), '--output', str(output), '--c1-prepared', str(self.prepared_file)]
        for name, value in self.identities.items():
            argv.extend(['--' + name.replace('_', '-'), value])
        error = io.StringIO()
        with patch('time.time', return_value=NOW), redirect_stderr(error):
            code = builder.main(argv)
        if output.exists():
            packet = closure.decode(output.read_bytes())
        else:
            # Incomplete fixtures must reach the consumers with authenticated
            # bytes of their own. Get all independent semantic gates from the
            # production builder before attaching the incomplete declaration.
            packet = builder.build_packet(
                self.git_dir, **self.identities, now_epoch_s=NOW,
                current_artifact_set_sha256=closure.artifact_set_digest_at(self.git_dir, self.execution))
            pins = closure.declared_pins(self.repo, self.stage)
            packet['c1_closure'] = {'schema': closure.SCHEMA, 'repo': closure.tree_identity(self.git_dir, self.execution),
                                    'stage_files': pins, 'ledger': {'path': str(self.stage / LEDGER),
                                        'sha256': pins.get(str(LEDGER), closure.digest(self.ledger))}}
        self.build_error = error.getvalue()
        return code, packet

    def deliver(self, packet, variant='clean'):
        fixture = self.fixture
        if fixture == 'wrong_start_digest':
            packet['c1_closure']['ledger']['sha256'] = '1' * 64
        if fixture == 'pending_desk_forged_status_and_ready':
            packet['checks']['full_desk_gate']['status'] = 'pass'
            packet['packet_preflight']['ready'] = True
        if fixture == 'wrong_predecessor_hash':
            packet['record_sha256'] = '2' * 64
        if fixture == 'ledger' and variant == 'unbound':
            del packet['c1_closure']['stage_files'][str(LEDGER)]
        raw = series.raw_json(packet)
        put(self.stage, PACKET, raw)
        put(self.git_dir, PACKET, raw)
        self.handoff['delivery_commit'] = self.commit('Finalize the invented C1 attempt')
        self.handoff['delivery_ref'] = 'refs/heads/fixture-delivery'
        self.git('update-ref', self.handoff['delivery_ref'], self.handoff['delivery_commit'])
        put(self.work, self.handoff_file.name, self.handoff)
        if variant != 'clean':
            if fixture == 'ledger' and variant == 'unbound':
                return
            path = (self.stage if fixture == 'ledger' else self.repo) / SELECTED[fixture]
            if variant == 'modified':
                path.write_bytes(path.read_bytes() + b'\n')
            else:
                path.unlink()
        if fixture == 'edit_derivation_after_build':
            path = self.repo / DERIVATION
            data = closure.decode(path.read_bytes())
            data['members'][0]['bundle_path'] = 'different-fixture'
            put(self.repo, DERIVATION, data)
        if fixture == 'swap_second_order_to_22':
            path = self.stage / self.second_order()
            data = closure.decode(path.read_bytes())
            data['executed_order'] = data['executed_order'][:-2]
            put(self.stage, self.second_order(), data)
        if fixture == 'swap_24_kit_to_22':
            name = KIT / series.C1_PLAN
            plan = deepcopy(self.plan)
            plan['members'] = plan['members'][:22]
            put(self.repo, name, plan)
        if fixture == 'unclosed_legacy_source_equals_view':
            put(self.repo, '.unlisted-file', b'anonymous fixture')
            self.handoff['view'] = str(self.repo)
            put(self.work, self.handoff_file.name, self.handoff)

    def context(self):
        verified = closure.verify_view(self.git_dir, self.repo, self.stage,
                                       delivery_ref=self.handoff['delivery_ref'],
                                       delivery_commit=self.handoff['delivery_commit'])
        return closure.prepared_closure(self.git_dir, verified.roots, self.handoff, verified.stage_read)

    def host_args(self):
        log = self.work / 'fixture-battery.jsonl'
        if not log.exists():
            write_battery_log(log, self.now)
        return {'now': lambda: self.now, 'runner': lambda argv: subprocess.CompletedProcess(argv, 0, 'invented', ''),
                'battery_log': [log], 'obc_off_attested_by': 'fixture', 'watchdog_check': lambda **_: {'ok': True},
                'meter_probe': lambda _: {'live': True, 'samples': 40}}

    def host_mocks(self, entered, *, install=False):
        stack = ExitStack()
        hits = 0

        def checkpoint():
            nonlocal hits
            hits += 1
            if hits == 1:
                entered()
            return self.host / 'marker'

        stack.enter_context(patch.object(powermode, 'host_marker_path', side_effect=checkpoint))
        stack.enter_context(patch.object(powermode, 'host_state_dir', return_value=str(self.host)))
        stack.enter_context(patch.object(powermode, 'HostLock'))
        stack.enter_context(patch.object(session, '_termination_handlers', return_value=(lambda: None, lambda: None)))
        stack.enter_context(patch.object(session, 'session_start_restore', return_value={'action': 'none'}))
        stack.enter_context(patch('joulewise.align.apple.powermode.admit_ac_powermode',
                                 return_value={'admitted': True, 'observed': 0}))
        stack.enter_context(patch('joulewise.align.apple.external_volume.census', return_value={}))
        stack.enter_context(patch('joulewise.align.apple.external_volume.arm_check',
                                 return_value={'verdict': 'PASS', 'reasons': []}))
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        stack.enter_context(patch('joulewise.battery_float.observe', return_value=(good, b'invented')))
        if self.fixture == 'installed_frequency_helper':
            stack.enter_context(patch.object(session, 'ZERO_FREQUENCY_ARGV',
                                             ('sudo', '-n', str(self.work / 'installed/frequency-helper'))))
            stack.enter_context(patch.object(session, '_require_night_job_absent'))
        if install:
            stack.enter_context(patch.object(session, 'w1_disk_check', return_value={'fixture': True}))
            stack.enter_context(patch.object(session.pilot, 'install', return_value={'exit_code': 0}))
            stack.enter_context(patch.object(session, '_watchdog_post_install'))
        return stack

    def install(self, entered):
        self.session = self.work / 'install'
        self.session.mkdir()
        opts = self.host_args()
        opts.pop('battery_log')
        opts.pop('obc_off_attested_by')
        opts['frequency_preflight'] = lambda *_, **__: {'ok': True}
        opts['frequency_pre_t0'] = lambda *_, **__: {'ok': True}
        if self.fixture == 'installed_frequency_helper':
            from joulewise import kernel_clock
            from joulewise.hazards import clock
            from ctypes import sizeof

            def reader():
                return {'schema_version': kernel_clock.PROBE_SCHEMA, 'modes': 0, 'raw_word': 0,
                        'call_status': 0, 'timex_status': 0, 'errno': 0, 'ppm': 0.0,
                        'raw_hex': bytes(sizeof(kernel_clock.Timex)).hex()}

            def frequency(state, **_):
                with patch('time.time', return_value=NOW), patch.object(clock, 'frequency_bound',
                                                                       return_value={'passes': True}):
                    return session.frequency_word_preflight(
                        state, reader=reader, runner=lambda argv: subprocess.CompletedProcess(
                            argv, 0, 'Network Time: Off', ''))

            opts['frequency_preflight'] = frequency
        error = io.StringIO()
        real = session.install
        with self.host_mocks(entered, install=True), redirect_stderr(error), redirect_stdout(io.StringIO()), \
                patch.object(session, 'install', side_effect=lambda root, **kw: real(root, **kw, **opts)):
            result = session.main(['install', '--session-root', str(self.session),
                                   '--c1-handoff', str(self.handoff_file), '--next-arm-triage',
                                   str(self.stage / PACKET), '--w1-disk-config', str(self.work / 'disk.json'),
                                   '--obc-off-attested-by', 'fixture', '--battery-log',
                                   str(self.work / 'fixture-battery.jsonl')])
        self.cli_error = error.getvalue()
        return result

    def direct_arm(self, entered):
        with self.host_mocks(entered):
            native = session.arm_checks(self.handoff['view'], self.plan, c1_handoff=self.handoff_file,
                                        next_arm_triage=self.stage / PACKET, **self.host_args())
        self.native = native
        return 'admit' if native['admitted'] else 'refuse'



REFUSALS = {
    'ordinary22_relabel': 'sentinel_roster',
    'sentinels_wrong_positions': 'sentinel_roster',
    'stale_w1_desk_r1_pointer': 'full_desk_gate',
    'swap_24_kit_to_22': 'repository blob mismatch',
    'swap_second_order_to_22': 'staged SHA-256 mismatch',
    'edit_derivation_after_build': 'repository blob mismatch',
    'drop_required_derivation_before_build': DERIVATION.name,
    'drop_initial_ledger_before_build': LEDGER.name,
    'drop_default_policy_before_build': POLICY.name,
    'pending_desk_forged_status_and_ready': 'full_desk_gate',
    'wrong_predecessor_hash': 'differs from the arm rebuild',
    'expired_141': 'expir',
    'external_calibration_ledger': 'outside R/S',
    'absolute_external_sidecar': 'outside R/S',
    'unrecognized_binding_kind': 'invented_unknown_kind',
    'session_downgrade': 'requires a C1 prepared session',
    'unclosed_legacy_source_equals_view': 'unexpected repository path',
    'ambient_shade_only': 'SHADE dependency is absent',
    'wrong_start_digest': 'starting ledger',
    'closed_stage_wrong_order': 'member count differs',
}


def expected_refusal(fixture, variant):
    if variant == 'modified':
        return 'staged SHA-256 mismatch' if fixture == 'ledger' else 'repository blob mismatch'
    if variant == 'unbound':
        return 'unlisted staged file' if fixture == 'ledger' else 'missing repository path'
    return REFUSALS.get(fixture)

def exercise(work, request, edit_source):
    from lite_adapter import consumer_decisions

    fixture, form, variant = (request[name] for name in ('fixture', 'form', 'variant'))
    with patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
                                 'GIT_AUTHOR_DATE': '2001-01-02T00:00:00Z',
                                 'GIT_COMMITTER_DATE': '2001-01-02T00:00:00Z'}):
        for name in ('CALIBRATION_LEDGER', 'LEDGER_HEAD_PIN', 'JOULEWISE_C1_INPUTS', 'XDG_CACHE_HOME'):
            os.environ.pop(name, None)
        attempt = Attempt(work, fixture, form, edit_source)
        code, packet = attempt.build()
        attempt.deliver(packet, variant)
        if fixture == 'ambient_shade_only':
            from joulewise.align.shade.upstream import UPSTREAM_COMMIT
            cache = work / 'external-cache'
            put(cache / 'joulewise/shade' / UPSTREAM_COMMIT, 'fixture.py', b'# invented external cache\n')
            os.environ['XDG_CACHE_HOME'] = str(cache)
        if fixture == 'external_calibration_ledger':
            os.environ['CALIBRATION_LEDGER'] = str(put(work, 'external-ledger.jsonl', attempt.ledger))
        result = consumer_decisions(attempt.install, attempt.direct_arm)
        if request['report_build']:
            result['build'] = code
        if detail := expected_refusal(fixture, variant):
            direct = attempt.native.get('packet_kit', {}).get('detail', '')
            if (result['cli'], result['arm'], result['host_cli'], result['host_arm']) != (2, 'refuse', 0, 0):
                raise AssertionError((result, attempt.cli_error, direct))
            if ('packet_kit_mismatch' not in attempt.cli_error or detail not in attempt.cli_error
                    or detail not in direct):
                raise AssertionError((detail, attempt.cli_error, direct, attempt.build_error))
        if result['cli'] == 1:
            raise AssertionError((attempt.cli_error, attempt.build_error, attempt.native.get('reasons')))
        if edit_source and variant == 'clean' and result['cli'] == 0:
            selected = attempt.context()[-1][fixture]
            result['selected'] = selected if fixture == 'session_kind' else closure.digest(selected.read_bytes())
        if fixture == 'ledger' and form == 'default' and variant == 'clean':
            result['one_live_file'] = observe_reservation(attempt, packet)
        if fixture == 'wrong_start_digest':
            result['reservation'], result['appended'] = wrong_reservation(attempt, packet)
        if fixture == 'installed_frequency_helper':
            installed = closure.decode((attempt.session / 'session.json').read_bytes())
            record = Path(installed['v4_arm_records'][0]['path'])
            result['external'] = closure.decode(record.read_bytes())['external_inputs'][0]
        return result


def reservation_args(attempt):
    stage = next(row for row in chain.stage_plan(attempt.tree) if row.kind == 'bracket_reservation')
    return chain.stage_argv(stage, attempt.bindings, attempt.tree, attempt.view)[2:]


def ledger_environment(attempt, packet):
    return patch.dict(os.environ, {'JOULEWISE_C1_INPUTS': json.dumps({
        'ledger': packet['c1_closure']['ledger'], 'git': str(attempt.git_dir), 'repo': str(attempt.repo),
        'execution_commit': attempt.execution}),
        'CALIBRATION_LEDGER': str(attempt.view / LEDGER), 'LEDGER_HEAD_PIN': str(attempt.view / HEAD)})


def wrong_reservation(attempt, packet):
    before = (attempt.stage / LEDGER).read_bytes()
    error = io.StringIO()
    with ledger_environment(attempt, packet), redirect_stderr(error):
        code = reservation.main([*reservation_args(attempt), '--execute'])
    if code != 2 or 'starting ledger SHA-256 mismatch' not in error.getvalue():
        raise AssertionError(error.getvalue())
    return 'refuse', (attempt.stage / LEDGER).read_bytes() != before


def observe_reservation(attempt, packet):
    from joulewise import calibration_ledger as ledger
    from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS

    epoch = {'os_build': 'invented', 'hardware_model': 'fixture', 'power_policy': 'ac_high_power',
             'sampling_interval_ms': 100, 'estimator_revision': 'joint_loss_sublevel_interval_branch_v2',
             'pulse_protocol_id': 'powermetrics_pulse_fiducial_v3'}
    t1 = {**dict.fromkeys(V2_BINDING_FIELDS, 'invented'), **epoch}
    path = attempt.view / LEDGER
    with ledger_environment(attempt, packet):
        receipt = ledger.append_bracket_session_receipt(
            path, session_id='fixture-session', window_id='C1', plan_id='fixture-plan',
            plan_sha256='a' * 64, evidence_root_id='fixture-evidence', runs_root=attempt.work / 'runs-out',
            head_pin_path=attempt.view / HEAD,
            slots={name: {'attempt_id': f'fixture-{name}', 'identity_epoch': epoch, 't1_bindings': t1,
                          'custody_locator': str(attempt.work / 'runs-out' / 'instrument_validation' / f'fixture-{name}')}
                   for name in ('pre', 'post')})
        snapshot = ledger.load_calibration_ledger_snapshot(
            path, attempt.view / HEAD, verify_custody=False, mode='read_replay')
    return (path.samefile(attempt.stage / LEDGER) and receipt['sequence'] == snapshot.head_sequence
            and 'fixture-session' in snapshot.bracket_session_by_id)
