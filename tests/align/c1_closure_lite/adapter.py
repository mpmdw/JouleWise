"""Run the frozen C1 decisions through the production packet and arm entry points."""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from copy import deepcopy
from functools import partial
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from unittest.mock import patch

from tests.align.test_v4_cadence import write_battery_log
from joulewise import night_gate
from joulewise.align.apple import powermode, v4_registration as closure
from joulewise.b5 import chain
from scripts import align_v4_next_arm_packet as builder, align_v4_series as series
from scripts import align_v4_session as session, bytes_h_session as staging
from scripts import reserve_calibration_window_bracket as reservation


NOW = 111.0
ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(closure.PACKET)
LEDGER = Path(closure.LEDGER)
POLICY = Path('configs/campaign_policies/quiet_mac_p2_production.json')
HEAD = Path('configs/calibration/calibration_ledger_head.json')
DERIVATION = Path('configs/campaigns/fixture-derivation/settled_corpus.json')
KIT = series.kit_path('C1')
SELECTED = {'ledger': LEDGER, 'head_pin': HEAD, 'policy': POLICY, 'derivation': DERIVATION}
# The installer module and the launchd templates it reads (CAP 10 I3).
INSTALLER_FILES = ('joulewise/night_agent_install.py', 'configs/launchd/com.joulewise.night.plist.template',
                   'configs/launchd/com.joulewise.night-probe.plist.template')
SYSTEM_PATH = '/usr/bin:/bin:/usr/sbin:/sbin'


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


def staged_pack_digest(root):
    """D-134 framing (arm_readiness.committed_pack_tree_sha256) over the staged pack's bytes.

    An independent copy of the framing, so the invented clean attempt checks
    the production recomputation rather than reusing it.
    """
    from joulewise.arm_readiness import PACK_DIGEST_DOMAIN

    root = Path(os.path.realpath(root))
    framed = bytearray(PACK_DIGEST_DOMAIN)
    # Logical names: a linked file or directory is framed as what it reaches.
    files = [Path(parent) / name for parent, _, names in os.walk(root, followlinks=True) for name in names]
    for path in sorted((p for p in files if p.is_file()), key=lambda p: p.relative_to(root).as_posix().encode()):
        raw = path.read_bytes()
        mode = b'100755' if path.stat().st_mode & 0o100 else b'100644'
        framed += (path.relative_to(root).as_posix().encode() + b'\0' + mode + b'\0'
                   + str(len(raw)).encode() + b'\0' + hashlib.sha256(raw).hexdigest().encode() + b'\n')
    return hashlib.sha256(bytes(framed)).hexdigest()


def option(args, flag, kind, value):
    args.extend([literal(flag), {'kind': kind, 'value': str(value)}])


class Attempt:
    def __init__(self, work, fixture, form, edit_source):
        self.work = work
        self.git_dir = work / 'authority'
        self.repo = work / 'R'
        self.stage = work / 'S'
        self.view = work / 'launch'
        self.night = None  # night_plan_path(custody_path()), set by prepare (CAP 10 I2)
        self.host = work / 'host'
        self.handoff_file = work / 'handoff.json'
        self.prepared_file = work / 'prepared.json'
        self.fixture = fixture
        # Desk identity files the reservation reads (empty on the frozen tape).
        self.desk_epoch = getattr(self, 'desk_epoch', b'{}\n')
        self.desk_t1 = getattr(self, 'desk_t1', b'{}\n')
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
        # The reservation requires each custody locator under the claim runs
        # root; b5.plan derives them the same way.
        for slot in ('pre', 'post'):
            self.bindings[f'{slot}_calibration_dir'] = str(
                work / 'claim_runs_root/instrument_validation' / self.bindings[f'{slot}_attempt_id'])
        self.complete_arguments()
        payloads = edit_source(self.source) if edit_source else {}
        self.ledger = payloads.pop(LEDGER.as_posix(), b'')
        for name, raw in payloads.items():
            put(self.git_dir, name, raw)
        if not (self.git_dir / POLICY).exists():
            # The runner's own policy loader runs at preflight. Use the
            # committed default so the invented attempt carries a valid policy.
            put(self.git_dir, POLICY, (ROOT / POLICY).read_bytes())
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

    def edit_night(self, night):
        """A test hook: change the prepared night plan before it is sealed."""

    def complete_night(self, night):
        """The rest of a HAZARD_PACK night plan, so the real installer parses it (CAP 10 I3).

        The values are the shape b5.plan writes; no C1 gate reads them.
        """
        window = night['hazard_window']
        try:
            stages = [stage.summary() for stage in chain.stage_plan(self.tree, c1=True)]
        except chain.ChainRenderError:
            stages = []  # an invalid tree refuses before any installer
        window.update(schema=night_gate.HAZARD_WINDOW_SCHEMA, planned_bytes=1000,
                      member_count=len(self.plan['members']), g10=False, programmed_span_s=3600,
                      t0_stage_cap_s=60, registration=None, chain_deviations=list(chain.DEVIATIONS),
                      disk_volumes=list(window['runs_roots'].values()), stages=stages)
        for module in night_gate.HAZARD_MODULES:
            window['thresholds'].setdefault(module, {})
        night.update(schema=night_gate.HAZARD_PLAN_SCHEMA, schema_version=night_gate.HAZARD_PLAN_SCHEMA_VERSION,
                     receipt_class=night_gate.HAZARD_PACK, authored_epoch_s=100, window_max_s=7200,
                     registration_path=None)

    def custody_path(self):
        """This attempt's custody root (prepare's custody_root input)."""
        return self.work / 'attempt-custody'

    def install_root(self):
        """The session root install writes (the prepared session's session_root)."""
        return self.work / 'install'

    def reserved_value(self, flag, default):
        """The value the tree's reservation passes for ``flag``, as rendered."""
        for stage in self.tree['stage_graph']:
            if stage['kind'] == 'bracket_reservation':
                args = arguments(stage)
                if literal(flag) in args:
                    item = args[args.index(literal(flag)) + 1]
                    return self.bindings[item['value']] if item['kind'] == 'binding' else item['value']
        return default

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
                if literal('--execute') not in args:
                    # The committed reservation templates append the session.
                    args.append(literal('--execute'))
            if stage['kind'] == 'calibration_capture':
                # The capture writer's own argument gates run at preflight.
                # Complete the invented template as align_v4's committed one is.
                slot = args[args.index(literal('--slot')) + 1]['value']
                if literal('--allow-live') not in args:
                    args.insert(0, literal('--allow-live'))
                if literal('--output-root') not in args:
                    args.extend([literal('--output-root'), {'kind': 'binding_path', 'value': 'claim_runs_root',
                                                            'relative': 'instrument_validation'}])
                for flag, value in (('--session-id', 'bracket_session_id'), ('--attempt-id', f'{slot}_attempt_id')):
                    if literal(flag) not in args:
                        option(args, flag, 'binding', value)
                if literal('--power-policy') not in args:
                    option(args, '--power-policy', 'literal', 'ac_high_power')
            if stage['kind'] == 'bound_derivation':
                if literal('--neg8-drift-bound-output') not in args:
                    # The harvest reads this attempt's bound under this name in the bound runs root.
                    args.extend([literal('--neg8-drift-bound-output'), {
                        'kind': 'binding_path', 'value': 'bound_runs_root', 'relative': 'neg8-drift-bound.json'}])
                if literal('--runs-dir') not in args:
                    option(args, '--runs-dir', 'binding', 'bound_runs_root')

    def mutate_source(self):
        fixture = self.fixture
        if fixture == 'with_spare':
            stage = next(row for row in self.source['stage_graph'] if row['kind'] == 'campaign_collection')
            relative = Path('configs/campaigns/invented-spares')
            # The runner validates spare configs at preflight. Reuse one valid
            # dispatched member config under the spare's own run ID.
            manifest = self.git_dir / stage['input']['path']
            member = closure.decode(manifest.read_bytes())['executed_order'][0]
            data = closure.decode((manifest.parent / member['config']).read_bytes())
            data['run_id'] = 'invented-spare'
            put(self.git_dir, relative / 'spare.json', data)
            path = put(self.git_dir, relative / 'order_manifest.json', {
                'executed_order': [{'config': 'spare.json', 'run_id': 'invented-spare'}]})
            stage['spare_retry'] = {'schema_version': chain.SPARE_RETRY_SCHEMA, 'slot': 'start', 'max_spares': 1,
                                    'spare_sets': [{'count': 1, 'order_manifest': {
                                        'path': str(relative / path.name), 'sha256': closure.digest(path.read_bytes())}}]}
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
            KIT, series.pack_id('C1'), read, lambda path: read(path) if (self.repo / path).is_file() else None,
            dispatch_dir=closure.C1_DISPATCH)
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
        files.update({Path('inputs/epoch.json'): self.desk_epoch, Path('inputs/t1.json'): self.desk_t1})
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

        exported = self.repo / KIT / series.C1_PLAN
        staged = self.stage / closure.PACK / series.C1_PLAN

        def write(entries):
            for name, raw in entries.items():
                if self.form == 'pack-link' and name == closure.PACK / series.C1_PLAN:
                    # Negative fixture: a link inside the pack, refused at the first stage (lead L1).
                    path = self.stage / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to(exported)
                else:
                    put(self.stage, name, raw)

        # Stage the pack before the plan, so its digest is of the staged bytes.
        write(files)
        if self.form == 'link':
            # The frozen in-view link to the genuine kit (lead ruling): the pack
            # keeps a regular file with the committed bytes and mode, and the
            # exported R/KIT path, which preflight reads, links to it.
            if staged.read_bytes() != exported.read_bytes():
                raise AssertionError('staged plan differs from the exported kit plan')
            staged.chmod(exported.stat().st_mode & 0o777)
            exported.unlink()
            exported.symlink_to(staged)
        custody_root = str(self.custody_path())
        self.night = night_gate.night_plan_path(custody_root)
        # The launch identity and locations b5.plan writes from the same inputs.
        self.night_data = {'plan_id': plan_id, 't0_epoch_s': 1020, 'chain_path': str(chain_path),
                           'chain_sha256_path': str(chain_path) + '.sha256', 'measurement_root': str(self.view),
                           'repo_head': self.execution, 'measurement_head': self.execution,
                           'custody_root': custody_root, 'hazard_window': {
            'attempt': 1, 'bracket_session_id': self.bindings['bracket_session_id'],
            'runs_roots': {'claim': self.bindings['claim_runs_root'], 'bound': self.bindings['bound_runs_root']},
            'bindings': self.bindings, 'T_stream_max_s': 10, 'settle_s': chain.SETTLE_S,
            'window_env': {'path': str(window_env), 'sha256': closure.digest(window_env_raw)},
            'thresholds': {'clock': {'frequency_error_budget_s': 1}},
            'pack': {'pack_root': str(self.view / closure.PACK), 'plan_tree_sha256': tree_digest,
                     'pack_sha256': staged_pack_digest(self.stage / closure.PACK),
                     'pack_id': closure.PACK.name, 'pack_plan_id': plan_id,
                     'window_id': self.reserved_value('--window-id', 'C1'),
                     'evidence_root_id': self.reserved_value('--evidence-root-id', 'fixture-evidence')}}}
        self.complete_night(self.night_data)
        self.edit_night(self.night_data)
        # Published where the installer admits it, not staged (CAP 10 I2): the
        # staged session.json binds its bytes by plan_sha256.
        put(self.night.parent, self.night.name, self.night_data)
        late = {}
        self.state = {'session_root': str(self.install_root()), 'measurement_root': str(self.view), 'source_measurement_root': str(self.repo),
                      'plan_path': str(self.night), 'plan_sha256': closure.digest(series.raw_json(self.night_data)),
                      'v4_series': {'window_id': 'W1' if self.fixture == 'session_downgrade' else 'C1'},
                      'inputs': {'custody_root': custody_root, 'attempt': 1, 'plan_id': plan_id}}
        late[Path('session.json')] = series.raw_json(self.state)
        write(late)
        files.update(late)
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
            # No installer stub (CAP 10 I3): the real bytes_h_session.install
            # builds the argv, and the real installer validates it in this
            # process (run_installer). Only its host commands are replaced.
            stack.enter_context(patch.object(staging, 'install', partial(
                staging.install, run=self.installer_command, home=self.work / 'fixture-home')))
            stack.enter_context(patch.object(session, '_watchdog_post_install'))
        return stack

    def installer_command(self, argv, **_):
        """bytes_h_session.install's two commands: the launchd job census, then the installer."""
        if argv[:2] == ['launchctl', 'print']:
            return subprocess.CompletedProcess(argv, 113, '', 'Could not find service "com.joulewise.night" '
                                               f'in domain for user gui: {os.getuid()}\n')
        if argv[0] != str(Path(self.state['measurement_root']) / 'scripts/install_night_agent.sh'):
            raise AssertionError(f'unexpected install command: {argv}')
        call = self.run_installer(argv)
        self.installer_calls.append(call)
        return subprocess.CompletedProcess(argv, call['exit'], '', call['stderr'])

    def installer_module(self):
        """The real installer module, loaded from a directory with no .git.

        In production the module resolves into the C1 repo export, which has
        no .git. The synthetic export cannot hold the installer's files: they
        are registered artifacts, and adding them would move the artifact-set
        digest that the frozen W1 desk pins. So the module and the two launchd
        templates it reads are copied byte for byte into a sibling directory.
        """
        root = self.work / 'installer-export'
        if not root.exists():
            for name in INSTALLER_FILES:
                put(root, name, (ROOT / name).read_bytes())
        spec = importlib.util.spec_from_file_location('c1_lite_installer', root / INSTALLER_FILES[0])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_installer(self, argv):
        """Run the real installer on ``argv`` through the end of its validation.

        Real here: its argument parser, plan parse, identity check, schedule,
        battery custody record, plist render, night-record check and
        admission, whose publication check is first. Replaced, because each is
        a host step:
        - the launchd transaction, which publishes and loads the plists;
        - the launchctl lookup;
        - the courier program lookup and the night driver's preflight, which
          run programs of the measurement checkout that this export lacks;
        - the battery probe, and the clock (this attempt's synthetic now).
        Every git command is recorded, and so is the prepared install.
        """
        installer = self.installer_module()
        record = {'argv': list(argv), 'git': [], 'prepared': None, 'courier': [], 'preflight': [],
                  'module_root': Path(installer.__file__).resolve().parents[1]}
        real_run, real_which = subprocess.run, shutil.which

        def command(argv, *args, **kwargs):
            if argv[:1] == ['/usr/bin/git']:
                record['git'].append(list(argv))
                return real_run(argv, *args, **kwargs)
            raise AssertionError(f'unexpected installer subprocess: {argv}')

        def courier(args, plan):
            record['courier'].append(args.courier_bin)
            return str(args.courier_bin), SYSTEM_PATH

        class Transaction:
            def __init__(self, adapter, validate, **_):
                self.validate = validate

            def run(self):
                record['prepared'] = self.validate()
                return 0

        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1,
                    monotonic_before_ns=time.monotonic_ns())  # names this run's battery record
        saved = {number: signal.getsignal(number) for number in installer.SIGNALS}
        errors = io.StringIO()
        try:
            with ExitStack() as stack:
                stack.enter_context(patch.dict(os.environ, {'GIT_CEILING_DIRECTORIES': str(self.work)}))
                stack.enter_context(patch.object(subprocess, 'run', side_effect=command))
                stack.enter_context(patch.object(shutil, 'which', side_effect=lambda name, *args, **kwargs: (
                    '/fixture/launchctl' if name == 'launchctl' else real_which(name, *args, **kwargs))))
                stack.enter_context(patch.object(installer, 'LaunchctlAdapter', lambda *args, **kwargs: None))
                stack.enter_context(patch.object(installer, 'Transaction', Transaction))
                stack.enter_context(patch.object(installer, 'select_courier', side_effect=courier))
                stack.enter_context(patch.object(installer, 'driver_preflight', side_effect=lambda *args: (
                    record['preflight'].append([str(arg) for arg in args]))))
                stack.enter_context(patch('joulewise.battery_float.observe', return_value=(good, b'invented')))
                stack.enter_context(patch.object(Path, 'home', return_value=self.work / 'fixture-home'))
                stack.enter_context(patch('time.time', return_value=self.now))
                stack.enter_context(redirect_stderr(errors))
                stack.enter_context(redirect_stdout(io.StringIO()))
                record['exit'] = installer.main(list(argv[1:]))
        finally:
            for number, handler in saved.items():
                signal.signal(number, handler)
        record['stderr'] = errors.getvalue()
        return record

    def install(self, entered):
        self.session = self.install_root()
        self.session.mkdir()
        # prepare creates the session's staging directory; the install logs go there.
        (self.session / 'staging').mkdir()
        self.installer_calls = []
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
    'closed_stage_wrong_order': 'config(s) absent from manifest',
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
