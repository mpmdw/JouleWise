"""R12 next-arm packet builder and the arm's rebuild of it. Synthetic Git records only.

The arm rebuilds the packet from the identities the supplied one names (a packet is a pointer,
never trusted data), judges its own build, and refuses a supplied packet that differs. No
measurements, probes, models or network.
"""
from tests.git_fixture import init_git_fixture
from tests.align.test_v4_arm_watchdog_check import acceptance as _watchdog_acceptance
from tests.align.v4_registration_fixtures import session_plan
import builtins
import contextlib
import copy
import hashlib
import io
from itertools import combinations
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import align_v4_kit as w1_kit, align_v4_next_arm_packet as builder
from scripts import align_v4_series as series
from scripts import align_v4_session as session
from scripts import bytes_h_session as staging
from joulewise.b5.chain import TOOLS
from joulewise.b5.plan import resolve_stage_dispatches
from joulewise.schemas import BenchmarkConfig, CONFIG_SCHEMA_VERSION
from joulewise.align.apple import v4_cadence as cad
from joulewise.align.apple import v4_registration as registration

INTERNAL = {r['id']: True for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.ARM}
CONFIG = dict(zip(builder.FROZEN_D_SLOT_KEYS, (4096, 30, 128, 4)))
IDENTITY = {'model_source': 'synthetic-tiny', 'model_revision': 'fixture',
            'runtime_sha256': 'a'*64, 'execution_policy_sha256': 'b'*64}
NOW = 111.0
CODE_PATH = 'scripts/run_night.py'      # a bound artifact: its bytes move the artifact-set digest


def fixture_next_members(manifest, *, extra_sentinels=True):
    window = series.selected(manifest, 'C1')
    allocations = window['members'] + (series.escalation_allocations(window) if extra_sentinels else [])
    roster = []
    for allocation in allocations:
        ordinal, pool = allocation['ordinal'], allocation['pool']
        # The producer preserves the anchors' original IDs.
        run_id = (f'align-pilot-v3-episodes-a-e{ordinal:02}' if pool == 'anchor'
                  else f'{series.pack_id("C1")}-e{ordinal:02}')
        role = {'sentinel': 'sentinel', 'anchor': 'anchor'}.get(pool, 'D')
        roster.append({'ordinal': ordinal, 'run_id': run_id, 'role': role})
    return roster


def synthetic_stage_graph():
    layout = [
        ("reservation", "bracket_reservation", "bracket_reserver", ["fixture"]),
        ("pre", "calibration_capture", "fiducial_capture", ["--slot", "pre"]),
        ("episodes-a", "campaign_collection", "campaign_runner", ["fixture"]),
        ("episodes-b", "campaign_collection", "campaign_runner", ["fixture"]),
        ("derive", "bound_derivation", "campaign_runner", ["fixture"]),
        ("post", "calibration_capture", "fiducial_capture", ["--slot", "post"]),
    ]
    names = ["align-pilot-v3-" + row[0] for row in layout]
    graph = []
    for pos, ((_, kind, tool, args), name) in enumerate(zip(layout, names, strict=True)):
        argv = [{"kind": "literal", "value": value} for value in args]
        if kind == "campaign_collection":
            argv = [dict(kind="repo_path", value="fixture"), dict(kind="literal", value="--runs-dir"),
                    dict(kind="binding", value="claim_runs_root")]
        if kind == "bracket_reservation":
            argv = [dict(kind="literal", value="--plan"), dict(kind="repo_path", value="fixture-plan.json")]
        graph.append(dict(
            stage_id=name, kind=kind, ordinal=pos + 1, expected_count=1,
            predecessor=names[pos - 1] if pos else None,
            successor=names[pos + 1] if pos + 1 < len(names) else None,
            launch=dict(schema_version="joulewise.stage_launch.v1", commands=[dict(
                command_id=name, cwd=dict(kind="binding", value="repo_root"), success_exit_codes=[0],
                argv_template=dict(tool_id=tool, interface_id=TOOLS[tool].interface_id, arguments=argv))]),
        ))
    return {"stage_graph": graph}


def synthetic_stage_config(run_id):
    config = dict(
        schema_version=CONFIG_SCHEMA_VERSION, run_id=run_id,
        model=dict(name="synthetic-anchor"), quantization=dict(name="fixture"),
        hardware_target=dict(id="fixture", transport="local", runtime_backend="mock", telemetry_backend="mock"),
        workload_profile=dict(name=staging.ALIGN_EPISODE, prompt_text=json.dumps(dict(max_turns=12, task_kwargs={}))),
        run_metadata=dict(tags=['align-model=invented-anchor']),
    )
    return w1_kit.bundle_config_bytes(BenchmarkConfig.from_mapping(config))


def seed_materializer(scenario):
    """Invent the v3 inputs used by the normal v4 materializer."""
    write = scenario.write
    for i in range(1, 5):
        run_id = f"align-pilot-v3-episodes-a-e{i:02}"
        write(w1_kit.SOURCE_KIT / "stages/episodes-a" / (run_id + ".json"), synthetic_stage_config(run_id))
    for i in (18, 25):
        run_id = f"align-pilot-v3-episodes-b-e{i:02}"
        write(w1_kit.SOURCE_KIT / "stages/episodes-b" / (run_id + ".json"), synthetic_stage_config(run_id))
    write(w1_kit.SOURCE_KIT / "plan_tree.json", synthetic_stage_graph())
    reg = w1_kit.SOURCE_KIT / "registration"
    write(reg / "identity_pins.json", dict(units=dict(neg8_reference={}, mock={}), runtime_versions={}))
    write(reg / "model_artifact_inventory.json", dict(artifacts=dict(neg8_reference={}, mock={})))
    write(reg / "sizing_b5.json", {"packs": {"align-pilot-v3": dict(
        disk_member_law=dict(intercept=1, slope=1, largest_positive_residual=0),
        disk_derivation=dict(scaffold_bytes=1))}})
    commit = scenario.commit()
    for pin in (w1_kit.ANCHOR_COMMIT, w1_kit.CONTRAST_COMMIT):
        scenario.git("tag", pin, commit)
    write(w1_kit.R1_SLOTS, dict(ac_powermode=0))
    write(w1_kit.INPUTS, dict(
        R0=dict(reasoning_effort=None), R1=dict(B_D=None, T_dead=None, thermal_policy=None),
        WP11=dict(identity_unit=dict(model_source="fixture"), artifact_inventory={}, local_file_verification=None),
        WP15=dict(runtime_entrypoint=None), WP18=dict(X=dict(max_turns=12), Y=dict(max_turns=12)),
    ))
    write(series.MANIFEST, series.raw_json(series.candidate()))



class Scenario:
    """One window record (and the series state that points at it) in a synthetic Git repository."""

    def __init__(self, directory, window='W1', *, previous=None, captured=True, eligible=True,
                 b_bar=True, provisional=False, previous_final=False):
        self.root = Path(directory)
        if previous is None:
            init_git_fixture(self.root, '-q')
        self.previous = previous
        self.window = window
        self.dir = 'w-' + window.replace('#', '_')
        self.policy = {'idle_s': 300, 'delta_slow_c': 1., 'quantization_bits': 8}
        self.members = [{'run_id': f'{p}-{self.dir}', 'model_id': 'tiny', 'role': 'D', 'condition': 'benign',
                         'task_pair': p} for p in cad.CAL_PAIRS]
        ids = [m['run_id'] for m in self.members]
        plan_id = 'synthetic-' + self.dir
        self.sources = {
            'plan': {'plan_id': plan_id, 'receipt_class': 'HAZARD_PACK', 'custody_root': '/DO-NOT-FOLLOW/custody'},
            'collection_plan': {'members': self.members, 'thermal_policy': dict(self.policy)},
            'result': {'schema': 'joulewise.unattended_night_result.v1', 'plan_id': plan_id,
                       'receipt_class': 'HAZARD_PACK', 'verdict': 'GO', 'chain_exit_code': 0,
                       'chain_sha256': 'c'*64, 'ended_epoch_s': 100},
            'chain_started': {'pgid': 123}, 'chain_exited': {'exit_code': 0},
            'courier': {'sent': True}, 'courier_sent': b'',
            'watchdog_state': {},
            'pilot': {'plan_id': plan_id, 'status': 'instrument_ok', 'checks': {'synthetic_check': True}, 'extra_checks': {
                'thermal': {'schema': 'joulewise.align.thermal_desk.v1',
                    'model_windows': {f'tiny/{window}': {f'U{k}': {'status': 'pass' if k < 4 else 'inconclusive'}
                                                        for k in range(1, 6)}},
                    'members': [{'id': i, 'model': 'tiny', 'gated': True, 'role': 'D',
                        'window': window, 'configuration': dict(CONFIG), 'cohort_identity': dict(IDENTITY),
                        'excluded': False, 'calibration_exclusions': [], 'flags': [], 'coverage': [],
                        'pm_period_s': .1, 'pm_max_gap_s': .1, 'turn_observation': [],
                        'tokens': [[1, 2, 3]]} for i in ids]},
                'km003c': {'members': {i: {'status': 'available', 'flags': []} for i in ids}}}},
            'desk': {'plan_id': plan_id, 'pilot_status': 'instrument_ok',
                     'checks': {'synthetic_check': True, 'v4_B_bar': b_bar}, 'harvest_status': 'ok'},
            'exclusions': {'members_excluded': [], 'reasons': [], 'claim_usable': True}}
        if window not in ('W1', 'R1'):
            # The desk's committed provisional counts: a permissive upper bound by default (7 per pair).
            self.sources['pilot']['extra_checks']['series_desk_row'] = {
                'window_id': window.split('#')[0], 'status': 'provisional', 'flags': [],
                'captured_members': 0, 'desk_eligible_benign': dict.fromkeys(cad.CAL_PAIRS, 7)}
        self.record = {'schema': builder.RECORD_SCHEMA, 'window': window,
                       'role': 'development' if window in ('W1', 'R1') else 'calibration',
                       'finalized_at_epoch_s': 101, 'previous_record': previous.link if previous else None}
        self.quiet = {'observed_at_epoch_s': 110, 'cooldown_s': 300, 'display_off_s': 60,
                      'dwell_s': 60, 'active_work': []}
        self.next_plan = {'role': 'calibration', 'window': 'C1',
                          'configuration': {**CONFIG, 'cohort_identity': dict(IDENTITY)},
                          'thermal_policy': dict(self.policy),
                          'members': fixture_next_members(series.candidate())}
        self.next_plan_slot = 'C1'
        self.series = {'schema': builder.SERIES_SCHEMA,
                       'quiet_requirements': {'cooldown_s': 300, 'display_off_s': 60, 'dwell_s': 60, 'max_age_s': 30},
                       'lead_rulings': [], 'pool_members': [],
                       'sentinel_ids': [m['run_id'] for m in self.next_plan['members'] if m['role'] == 'sentinel'],
                       'escalations': []}
        self.absent_captures = set() if captured else set(ids)
        self.omit_sources = set()
        self.raw_custody = False
        self.provisional, self.previous_final = provisional, previous_final
        if not captured:
            self.sources['result'].update(verdict='REFUSED', chain_exit_code=None, chain_sha256=None)
            self.omit_sources.update(('chain_started', 'chain_exited'))
            for m in self.thermal['members']:
                m.update(excluded=True, calibration_exclusions=['member.runtime_failure'])
            self.sources['exclusions']['members_excluded'] = [{'run_id': i, 'codes': ['member.runtime_failure']} for i in ids]
        if not eligible:
            self.thermal['members'][0].update(excluded=True, calibration_exclusions=['thermal.state_unobserved'])
            self.sources['exclusions']['members_excluded'] = [{'run_id': ids[0], 'codes': ['thermal.state_unobserved']}]

    def git(self, *args):
        result = subprocess.run(['git', '-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                                 '-C', str(self.root), *args], check=True, capture_output=True,
                                env={**os.environ, 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1'})
        return result.stdout.decode().strip()

    def write(self, path, value):
        raw = value if isinstance(value, bytes) else (json.dumps(value, sort_keys=True) + '\n').encode()
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'synthetic evidence', '--allow-empty')
        return self.git('rev-parse', 'HEAD')

    def retarget_next_members(self):
        """Keep fixture member IDs in the named slot, preserving roster mutations."""
        slot = series.slot_of(self.next_plan['window'])
        if slot in (self.next_plan_slot, 'W1'):
            return
        previous_pack, pack = series.pack_id(self.next_plan_slot), series.pack_id(slot)

        def retarget(run_id):
            return pack + run_id[len(previous_pack):] if run_id.startswith(previous_pack + '-e') else run_id

        for member in self.next_plan['members']:
            member['run_id'] = retarget(member['run_id'])
        self.series['sentinel_ids'] = [retarget(run_id) for run_id in self.series['sentinel_ids']]
        self.next_plan_slot = slot

    def finish(self, *, change_code=False, code=b'synthetic-code-v1\n'):
        self.retarget_next_members()
        if not (self.root / series.MANIFEST).exists():
            self.write(series.MANIFEST, series.raw_json(series.candidate()))
        self.write(CODE_PATH, code)
        self.record['code_commit'] = self.code_commit = self.commit()
        d = self.dir
        self.sources['watchdog_state'].setdefault('released_terminal_windows', [
            f"{self.sources['plan']['plan_id']}:/DO-NOT-FOLLOW/custody:"
            f"{builder.digest((json.dumps(self.sources['result'], sort_keys=True) + chr(10)).encode())}"])
        if self.provisional:
            # R17: committed before the Air full desk finished; the light triage stands in.
            self.final_sources = {k: copy.deepcopy(self.sources[k]) for k in builder.FINAL_SOURCES}
            light_thermal = copy.deepcopy(self.thermal)
            for m in light_thermal['members']:
                m['excluded'] = bool(m['calibration_exclusions'])
            self.sources['light_triage'] = {'schema': builder.LIGHT_TRIAGE_SCHEMA, 'window': self.window,
                'thermal': light_thermal, 'checks': {'v4_B_bar': self.sources['desk']['checks']['v4_B_bar']},
                'km003c': self.sources['pilot']['extra_checks']['km003c'],
                'series_desk_row': self.sources['pilot']['extra_checks'].get('series_desk_row')}
            self.sources['desk'] = {'plan_id': self.sources['plan']['plan_id'], 'status': 'running_off_mbp'}
            self.omit_sources.update(('pilot', 'exclusions'))
        if self.previous_final:
            prior = self.previous
            self.record['previous_final'] = {'record_sha256': prior.link['sha256'], 'sources': {
                k: self.write(f'{d}/previous-final/{k}.json', v) for k, v in prior.final_sources.items()}}
        self.record['sources'] = {k: self.write(f'{d}/evidence/{k}.json', v)
                                  for k, v in self.sources.items() if k not in self.omit_sources}
        pairs = [m['run_id'] for m in self.members]
        self.record['captures'] = {i: None if i in self.absent_captures else (
            {'locator': '/DO-NOT-FOLLOW/' + i, 'sha256': builder.digest(b'synthetic'), 'bytes': 9}
            if self.raw_custody else self.write(f'{d}/captures/{i}.jsonl', b'{"monotonic_ns":1,"power_w":1}\n'))
            for i in pairs}
        self.record['raw_evidence'] = [self.write(f'{d}/raw/sidecar.jsonl', b'{"temperature_c":30}\n')]
        if self.window != 'R1' and not getattr(self, 'omit_finalized_manifest', False):
            # R17 review F2: the record binds the finalized (record-bound) tree manifest, canonical bytes.
            finalized = {'schema': builder.FINALIZED_MANIFEST_SCHEMA, 'source_root': '/DO-NOT-FOLLOW/session-' + d,
                         'entries': {'raw/sidecar.jsonl': {'sha256': 'f' * 64, 'size': 21}},
                         'closure': {'links': {}, 'files': {}, 'inputs': [], 'mirror': None}}
            self.record['finalized_manifest'] = self.write(
                f'{d}/evidence/finalized_manifest.json',
                json.dumps(finalized, sort_keys=True, separators=(',', ':')).encode())
        if self.raw_custody:
            self.record['raw_evidence'].extend(self.record['captures'].values())
        self.record_path = f'{d}/record.json'
        index = self.write(self.record_path, self.record)
        self.record_commit = self.commit()
        self.git('update-ref', 'refs/remotes/synthetic/records', self.record_commit)
        self.link = {'commit': self.record_commit, 'path': self.record_path, 'sha256': index['sha256']}
        self.series['last_passed_record'] = dict(self.link)
        if self.provisional:
            # Its desk has not passed yet: the last desk-passed state is the previous record's.
            prior = self.previous
            self.series['last_passed_record'] = dict(prior.passed_ref)
        self.passed_ref = dict(self.series['last_passed_record'])
        if self.previous_final:
            # The previous window's desk passed off the MBP and rides in this record.
            self.previous.passed_ref = {**self.previous.link, 'final_record': dict(self.link)}
        if change_code:
            self.write(CODE_PATH, b'synthetic-code-v2\n')       # the working tree (the arm's code) moves on
        self.series.update(previous_record=dict(self.link),
                           quiet=self.write(f'{d}/series/quiet.json', self.quiet),
                           next_plan=self.write(f'{d}/series/next_plan.json', self.next_plan))
        self.series_path = builder.SERIES_PATH       # one canonical ledger, rewritten by each window
        self.write(self.series_path, self.series)
        self.series_commit = self.commit()
        return self

    def identities(self, **changes):
        args = dict(record_commit=self.record_commit, record_path=self.record_path,
                    series_commit=self.series_commit, series_path=self.series_path,
                    pushed_ref='refs/remotes/synthetic/records')
        args.update(changes)
        return args

    def build(self, *, now=NOW, current=None, **changes):
        current = current or registration.artifact_set_digest(self.root)
        return builder.build_packet(self.root, **self.identities(**changes), now_epoch_s=now,
                                    current_artifact_set_sha256=current)

    @property
    def thermal(self):
        return self.sources['pilot']['extra_checks']['thermal']


def evaluate(scenario, packet, now=NOW, internal=INTERNAL):
    """The gate the arm applies: rebuild from the packet's named identities, compare, judge the rebuild."""
    current = registration.artifact_set_digest(scenario.root)
    try:
        built, matches = builder.rebuild_and_compare(scenario.root, packet, now_epoch_s=now,
                                                     current_artifact_set_sha256=current)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return {'admitted': False, 'reasons': [f'packet could not be rebuilt from its named sources: {exc}']}
    result = cad.next_arm_triage(built, internal, {
        'artifact_set_sha256': current, 'record_commit_exists': True, 'record_bound': True}, now_epoch_s=now)
    if not matches:
        result['admitted'] = False
        result['reasons'].append('packet does not match its committed sources')
    return result


class Base(unittest.TestCase):
    def scenario(self, window='W1', **kwargs):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-synthetic-')
        self.addCleanup(temp.cleanup)
        return Scenario(temp.name, window, **kwargs)

    def calibration_series(self, specs):
        """Successive calibration records in one repository; specs = [(window, captured, eligible), ...]."""
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-series-')
        self.addCleanup(temp.cleanup)
        first = Scenario(temp.name, 'W1').finish()
        previous = first
        for window, captured, eligible, *rest in specs:
            current = Scenario(temp.name, window, previous=previous, captured=captured, eligible=eligible,
                               b_bar=rest[0] if rest else True).finish()
            previous = current
        return previous


class C1PacketRebuildTests(Base):
    """The W1 -> C1 handoff through the CLI, an independent rebuild and the frozen series."""

    def setUp(self):
        self.real_arm = session.arm_checks
        self.fixture_roots = set()
        self.output_dir = Path(self.enterContext(tempfile.TemporaryDirectory(prefix='jw-c1-packets-')))
        self.output_number = 0
        self.enterContext(patch.dict(os.environ, {
            'GIT_AUTHOR_DATE': '2001-01-01T00:00:00+00:00', 'GIT_COMMITTER_DATE': '2001-01-01T00:00:00+00:00',
            'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_DEFAULT_HASH': 'sha1',
            'GIT_TEMPLATE_DIR': '',
        }))
        for module, names in ((builtins, ('open',)), (io, ('open',)),
                              (os, ('open', 'stat', 'lstat', 'readlink', 'listdir', 'scandir'))):
            for name in names:
                original = getattr(module, name)

                def guarded(path='.', *args, operation=original, **kwargs):
                    if not isinstance(path, int) and path is not None:
                        self.assertNotIn('DO-NOT-FOLLOW', os.fsdecode(path), 'custody locator was followed')
                    return operation(path, *args, **kwargs)

                self.enterContext(patch.object(module, name, new=guarded))
        popen = subprocess.Popen

        def fixture_git(argv, *args, **kwargs):
            if isinstance(argv, (tuple, list)) and argv and argv[0] == 'git':
                root = argv[argv.index('-C') + 1] if '-C' in argv else kwargs.get('cwd')
                if root is not None and Path(root) in self.fixture_roots and not kwargs.get('shell'):
                    self.assertTrue(all('DO-NOT-FOLLOW' not in arg for arg in argv))
                    return popen(argv, *args, **kwargs)
            self.fail(f'only fixture-local Git subprocesses are allowed: {argv!r}')

        self.enterContext(patch.object(subprocess, 'Popen', new=fixture_git))
        for target in (
            'scripts.align_v4_session.prepare', 'scripts.align_v4_session._arm_and_install',
            'scripts.align_v4_session.arm_checks', 'scripts.align_v4_session._probe_meter_live',
            'joulewise.align.apple.powermode.admit_ac_powermode', 'joulewise.align.apple.external_volume.census',
            'joulewise.align.apple.external_volume.arm_check', 'joulewise.battery_float.observe',
        ):
            trap = self.enterContext(patch(target, side_effect=AssertionError(f'physical probe or arm: {target}')))
            self.addCleanup(trap.assert_not_called)

    def c1_scenario(self, *, bad_history_link=False, older_desk=False, desk='passed', extra_sentinels=True,
                    wrong_cohort=False, receipt=None, materialized=False):
        root = Path(self.enterContext(tempfile.TemporaryDirectory(prefix='jw-c1-records-')))
        self.fixture_roots.add(root)
        self.enterContext(patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(root / 'host')}))
        r1 = Scenario(root, 'R1')
        if materialized:
            seed_materializer(r1)
        manifest = series.candidate()
        manifest_ref = r1.write(series.MANIFEST, series.raw_json(manifest))
        r1.finish(code=b'synthetic-code-v0\n' if older_desk else b'synthetic-code-v1\n')

        w1 = Scenario(root, 'W1', previous=r1)
        w1.raw_custody = True
        w1.manifest_sha256 = manifest_ref['sha256']
        w1.series['pool_members'] = [member['run_id'] for member in w1.members]
        planned_roster = fixture_next_members(manifest, extra_sentinels=extra_sentinels)
        if materialized:
            plan = self.materialize_c1(w1, 2 if extra_sentinels else 0)
            planned_roster = [{'run_id': row['run_id'],
                               'role': 'sentinel' if row['pool_role'] == 'sentinel' else row['role']}
                              for row in plan['members']]
        w1.next_plan['members'] = planned_roster
        # The omission control must fail the U4 minimum with a consistent plan and ledger.
        w1.series['sentinel_ids'] = [row['run_id'] for row in planned_roster if row['role'] == 'sentinel']
        if bad_history_link:
            w1.record['previous_record'] = {**r1.link, 'sha256': '0' * 64}
        if wrong_cohort:
            w1.next_plan['configuration']['cohort_identity']['model_revision'] = 'different-fixture'
        if desk == 'missing':
            w1.omit_sources.add('desk')
        elif desk == 'pending':
            w1.sources['desk'] = {'plan_id': w1.sources['plan']['plan_id'], 'status': 'running_off_mbp'}
        if receipt is not None:
            w1.sources['registration_receipt'] = receipt
            w1.write(registration.REGISTRATION + 'registration_receipt.json', receipt)
        w1.finish()
        w1.series_sha256 = builder.digest((root / w1.series_path).read_bytes())
        if older_desk:
            # The W1 desk first passes on the current bytes. Only the ledger's last-pass link then moves.
            self.ready_packet(w1)
        if older_desk or desk == 'pending':
            w1.series['last_passed_record'] = dict(r1.link)
            self.commit_series(w1)
        return w1

    def commit_series(self, scenario):
        scenario.series_sha256 = scenario.write(scenario.series_path, scenario.series)['sha256']
        scenario.series_commit = scenario.commit()

    def recommit_predecessor(self, scenario):
        record_sha = scenario.write(scenario.record_path, scenario.record)['sha256']
        scenario.record_commit = scenario.commit()
        scenario.link = {'commit': scenario.record_commit, 'path': scenario.record_path, 'sha256': record_sha}
        scenario.git('update-ref', scenario.identities()['pushed_ref'], scenario.record_commit)
        scenario.series.update(previous_record=dict(scenario.link), last_passed_record=dict(scenario.link))
        self.commit_series(scenario)

    def cli_packet(self, scenario, *, now=NOW, **changes):
        self.output_number += 1
        path = self.output_dir / f'packet-{self.output_number}.json'
        args = ['--repo', str(scenario.root), '--output', str(path)]
        for name, value in scenario.identities(**changes).items():
            args.extend(['--' + name.replace('_', '-'), value])
        error = io.StringIO()
        with patch('time.time', return_value=now), contextlib.redirect_stderr(error):
            code = builder.main(args)
        output = json.loads(path.read_bytes()) if path.exists() else None
        return code, output, error.getvalue()

    def ready_packet(self, scenario):
        code, packet, error = self.cli_packet(scenario)
        self.assertEqual(code, 0, (error, packet and packet['packet_preflight']['reasons']))
        self.assertTrue(packet['packet_preflight']['ready'])
        return packet

    def refused_packet(self, scenario, *, now=NOW):
        code, packet, error = self.cli_packet(scenario, now=now)
        self.assertEqual(code, 2)
        self.assertIsNotNone(packet, error)
        self.assertFalse(packet['packet_preflight']['ready'])
        return packet

    def rebuild(self, scenario, supplied, *, now=NOW):
        return builder.rebuild_and_compare(scenario.root, supplied, now_epoch_s=now,
                                           current_artifact_set_sha256=registration.artifact_set_digest(scenario.root))

    def triage(self, scenario, packet, *, now=NOW):
        return cad.next_arm_triage(packet, {}, {
            'artifact_set_sha256': registration.artifact_set_digest(scenario.root),
            'record_commit_exists': session._commit_exists(scenario.root, packet['record_commit']),
            'record_bound': session._record_bound(scenario.root, packet),
        }, now_epoch_s=now)

    def assert_packet_failure(self, packet, check, text):
        self.assertEqual(packet['checks'][check]['status'], 'fail')
        self.assertIn(text, packet['checks'][check]['basis'])
        self.assertIn(f'triage {check} failed', packet['packet_preflight']['reasons'])


    def materialize_c1(self, scenario, extras):
        directory = scenario.root / series.kit_path('C1')
        if directory.exists():
            shutil.rmtree(directory)
        args = ['--root', str(scenario.root), '--window-id', 'C1', '--extra-sentinels', str(extras)]
        with patch.object(w1_kit, 'r0_heatsink_key', return_value='T002'), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(series.main(['materialize', *args]), 0)
            self.assertEqual(series.main(['materialize', *args, '--check']), 0)
        return json.loads((directory / 'collection_plan.json').read_bytes())

    def k1_arm(self, scenario, packet, plan, *, view=None, night=None):
        # Restore the real guard with only invented host inputs from the arm-rebuild suite.
        with patch.object(session, 'arm_checks', side_effect=lambda root, _, **kw: self.real_arm(root, plan, **kw)):
            return ArmRebuildTests().arm(SimpleNamespace(root=view or scenario.root), packet,
                c1_kit_root=scenario.root, watchdog_plan_path=night, series_bind=lambda rebuilt: (
                series.bind_packet(scenario.root, 'C1', rebuilt, authenticated_by_rebuild=True) and []))

    def assert_k1_refusal(self, scenario, packet, plan):
        record = self.k1_arm(scenario, packet, plan)
        self.assertTrue(record['next_arm_triage']['supplied_packet_matches_rebuild'])
        self.assertEqual(record['series_binding'], [])
        self.assertFalse(record['admitted'], record['reasons'])
        self.assertIn('packet_kit_mismatch', record['reasons'])

    def test_k1_materialized_24_member_packet_rebuild_and_arm_agree(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        rebuilt, matches = self.rebuild(w1, packet)
        self.assertTrue(matches)
        directory = w1.root / series.kit_path('C1')
        plan_raw = (directory / 'collection_plan.json').read_bytes()
        binding = rebuilt['c1_kit']
        self.assertRegex(binding['kit_sha256'], r'^[0-9a-f]{64}$')
        self.assertEqual(binding['plan_sha256'], builder.digest(plan_raw))
        self.assertEqual((binding['member_count'], binding['sentinel_ordinals']), (24, [5, 22, 23, 24]))
        result = self.k1_arm(w1, packet, json.loads(plan_raw))
        self.assertTrue(result['admitted'], result['reasons'])

    def test_k1_ordinary_22_member_kit_cannot_arm_with_the_24_member_packet(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        ordinary = self.materialize_c1(w1, 0)
        self.assertEqual(len(ordinary['members']), 22)
        w1.commit()
        self.assert_k1_refusal(w1, packet, ordinary)

    def assert_k1_cli_refusal(self, w1, packet, selected, state):
        target = self.output_dir / 'cli-session'
        session.pilot.h.write(target / 'session.json', state)
        packet_ref = w1.write('cli-packet.json', packet)
        args = ['install', '--session-root', str(target), '--w1-disk-config', 'unused',
                '--battery-log', 'unused', '--obc-off-attested-by', 'synthetic',
                '--next-arm-triage', str(w1.root / packet_ref['path'])]
        stderr = io.StringIO()
        with patch.object(w1_kit, 'generate'), patch.object(session, 'validate_series_state', return_value=selected), \
             patch('joulewise.align.apple.powermode.host_marker_path', side_effect=ValueError('host access')) as host, \
             contextlib.redirect_stderr(stderr):
            self.assertEqual(session.main(args), 2, stderr.getvalue())
        self.assertIn('packet_kit_mismatch', stderr.getvalue())
        host.assert_not_called()

    def test_k1_cli_refuses_replaced_kit_before_host_access(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        ordinary = self.materialize_c1(w1, 0)
        state = {'measurement_root': str(w1.root), 'source_measurement_root': str(w1.root),
                 'v4_series': {'window_id': 'C1', 'extra_sentinels': 0}}
        self.assert_k1_cli_refusal(w1, packet, ordinary, state)

    def test_k1_cli_refuses_old_staged_tree_when_the_source_kit_matches(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        directory = w1.root / series.kit_path('C1')
        complete = directory.with_name('complete-kit')
        directory.rename(complete)
        ordinary = self.materialize_c1(w1, 0)
        view = self.output_dir / 'measurement'
        pack = view / 'configs/campaigns' / series.pack_id('C1')
        pack.parent.mkdir(parents=True)
        directory.rename(pack)
        complete.rename(directory)
        plan_raw = (directory / 'collection_plan.json').read_bytes()
        (pack / 'collection_plan.json').write_bytes(plan_raw)
        night = self.output_dir / 'synthetic-night.json'
        session.pilot.h.write(night, {'hazard_window': {
            'pack': {'pack_root': str(pack), 'plan_tree_sha256': builder.digest((pack / 'plan_tree.json').read_bytes())},
            'member_count': len(ordinary['members'])}})
        state = {'measurement_root': str(view), 'source_measurement_root': str(w1.root), 'plan_path': str(night),
                 'v4_series': {'window_id': 'C1', 'extra_sentinels': 2}}
        self.assert_k1_cli_refusal(w1, packet, json.loads(plan_raw), state)

    def test_k1_any_kit_byte_swap_after_packet_refuses_even_when_plan_unchanged(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        directory = series.kit_path('C1')
        plan = json.loads((w1.root / directory / 'collection_plan.json').read_bytes())
        path = directory / 'registration/seed_manifest.json'
        w1.write(path, (w1.root / path).read_bytes() + b' ')
        self.assert_k1_refusal(w1, packet, plan)

    def test_k1_member_count_sweep_and_moved_sentinels_refuse(self):
        for mutation in (-2, -1, 1, 2, 'moved'):
            with self.subTest(mutation=mutation):
                w1 = self.c1_scenario(materialized=True)
                packet = self.ready_packet(w1)
                path = series.kit_path('C1') / 'collection_plan.json'
                plan = json.loads((w1.root / path).read_bytes())
                members = plan['members']
                if mutation == 'moved':
                    members[19], members[22] = members[22], members[19]
                elif mutation < 0:
                    del members[mutation:]
                else:
                    members.extend(dict(members[5], run_id=f'fixture-extra-{i}') for i in range(mutation))
                for i, member in enumerate(members, 1):
                    member['ordinal'] = i
                self.assert_k1_refusal(w1, packet, plan)

    def staged_c1(self, w1):
        w1.write(staging.plan.HEAD_PIN_RELATIVE, b'invented fixture pin\n')
        w1.write('configs/campaigns/bytes_v1/roster.json', {'models': []})
        w1.write('configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json',
                 {'arm_attachments': {'launch': {'bindings': []}}, 'external_inputs': {'manifests': []}})
        target = Path(self.enterContext(tempfile.TemporaryDirectory(dir=self.output_dir)))
        view, pack = staging.measurement_view(w1.root, target, kit=series.kit_path('C1'),
                                              pack_id=series.pack_id('C1'))
        self.fixture_roots.add(view)
        tree_raw = (pack / 'plan_tree.json').read_bytes()
        night = target / 'fixture-night.json'
        staging.write(night, {'hazard_window': {'pack': {'pack_root': str(pack),
                                                         'plan_tree_sha256': builder.digest(tree_raw)}}})
        return view, pack, night, json.loads(tree_raw)

    def copy_bound_fixture_links(self, w1, view):
        """Copy the invented linked bytes relevant to the staged digest."""
        for relative in ('scripts', 'configs/campaigns/align_v4'):
            link = view / relative
            self.assertTrue(link.is_symlink())
            link.unlink()
            shutil.copytree(w1.root / relative, link)

    def staged_state(self, w1, view, night):
        return {'measurement_root': str(view), 'source_measurement_root': str(w1.root),
                'plan_path': str(night), 'v4_series': {'window_id': 'C1', 'extra_sentinels': 2}}

    def test_k2_ordinary_manifest_cannot_drop_23_and_24_from_staged_dispatch(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        directory = w1.root / series.kit_path('C1')
        plan = json.loads((directory / series.C1_PLAN).read_bytes())
        view, pack, night, tree = self.staged_c1(w1)
        self.copy_bound_fixture_links(w1, view)
        manifest = pack / 'members' / plan['members'][-1]['stage_id'] / 'order_manifest.json'
        complete = directory.with_name('complete-kit')
        directory.rename(complete)
        self.materialize_c1(w1, 0)
        _, ordinary, _, _ = self.staged_c1(w1)
        raw = (ordinary / manifest.relative_to(pack)).read_bytes()
        shutil.rmtree(directory)
        complete.rename(directory)
        manifest.write_bytes(raw)
        dispatches = resolve_stage_dispatches(tree, view)
        self.assertEqual(sum(len(dispatch.run_ids) for dispatch in dispatches), 22)
        record = self.k1_arm(w1, packet, plan, view=view, night=night)
        self.assertTrue(record['next_arm_triage']['supplied_packet_matches_rebuild'])
        self.assertIn('packet_kit_mismatch', record['reasons'])
        self.assertFalse(record['admitted'])
        self.assert_k1_cli_refusal(w1, packet, plan, self.staged_state(w1, view, night))

    def test_k2_every_stage_manifest_requires_its_exact_bytes_and_order(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        plan = json.loads((w1.root / series.kit_path('C1') / series.C1_PLAN).read_bytes())
        view, _, night, tree = self.staged_c1(w1)
        for dispatch in resolve_stage_dispatches(tree, view):
            path = view / dispatch.config_dir / 'order_manifest.json'
            original = path.read_bytes()
            order = json.loads(original)
            order['executed_order'][:2] = reversed(order['executed_order'][:2])
            for label, raw in (('same roster, edited bytes', original + b' '),
                               ('reordered roster', json.dumps(order).encode())):
                with self.subTest(stage=dispatch.stage_id, mutation=label):
                    path.write_bytes(raw)
                    self.assert_k1_cli_refusal(w1, packet, plan, self.staged_state(w1, view, night))
            path.write_bytes(original)

    def test_k2_staged_kit_copy_must_match_committed_content(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        plan = json.loads((w1.root / series.kit_path('C1') / series.C1_PLAN).read_bytes())
        view, pack, night, _ = self.staged_c1(w1)
        registration_dir = pack / 'registration'
        registration_dir.unlink()
        shutil.copytree(w1.root / series.kit_path('C1') / 'registration', registration_dir)
        changed = registration_dir / 'seed_manifest.json'
        changed.write_bytes(changed.read_bytes() + b' ')
        self.assert_k1_cli_refusal(w1, packet, plan, self.staged_state(w1, view, night))

    def test_k3_real_staged_links_and_identical_copies_both_admit(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        plan = json.loads((w1.root / series.kit_path('C1') / series.C1_PLAN).read_bytes())
        for copies in (False, True):
            with self.subTest(copies=copies):
                view, pack, night, _ = self.staged_c1(w1)
                if copies:
                    self.copy_bound_fixture_links(w1, view)
                    collection = pack / series.C1_PLAN
                    raw = collection.read_bytes()
                    collection.unlink()
                    collection.write_bytes(raw)
                record = self.k1_arm(w1, packet, plan, view=view, night=night)
                self.assertTrue(record['next_arm_triage']['supplied_packet_matches_rebuild'], record['reasons'])
                self.assertTrue(record['admitted'], record['reasons'])

    def test_k3_stage_artifact_link_escaping_roots_refuses_before_host_access(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        self.copy_stage_artifact_escape(w1, packet, CODE_PATH)

    def test_k3_manifest_link_escaping_roots_refuses_before_host_access(self):
        w1 = self.c1_scenario(materialized=True)
        packet = self.ready_packet(w1)
        view, _, _, tree = self.staged_c1(w1)
        path = view / resolve_stage_dispatches(tree, view)[0].config_dir / 'order_manifest.json'
        self.copy_stage_artifact_escape(w1, packet, path.relative_to(view))

    def copy_stage_artifact_escape(self, w1, packet, path):
        view, _, night, _ = self.staged_c1(w1)
        self.copy_bound_fixture_links(w1, view)
        plan = json.loads((w1.root / series.kit_path('C1') / series.C1_PLAN).read_bytes())
        target = view / path
        target.unlink()
        target.symlink_to(self.output_dir / 'DO-NOT-FOLLOW' / 'exit')
        self.assert_k1_cli_refusal(w1, packet, plan, self.staged_state(w1, view, night))

    def test_committed_w1_rebuild_binds_c1_with_live_checks_pending(self):
        w1 = self.c1_scenario()
        supplied = self.ready_packet(w1)
        rebuilt, matches = self.rebuild(w1, supplied)
        self.assertTrue(matches)
        self.assertIs(series.bind_packet(w1.root, 'C1', rebuilt, authenticated_by_rebuild=True), rebuilt)
        self.assertTrue(session._record_bound(w1.root, rebuilt))
        self.assertEqual((rebuilt['previous_window'], rebuilt['next_window_id'], rebuilt['next_window_role']),
                         ('W1', 'C1', 'calibration'))
        self.assertEqual(builder.identities(rebuilt), w1.identities())
        self.assertEqual(rebuilt['record_sha256'], w1.link['sha256'])
        self.assertEqual(rebuilt['series_sha256'], w1.series_sha256)
        self.assertEqual(rebuilt['series_manifest_sha256'], w1.manifest_sha256)
        self.assertEqual(rebuilt['window_chain'], [
            {'window': 'R1', **w1.previous.link, 'previous_sha256': None},
            {'window': 'W1', **w1.link, 'previous_sha256': w1.previous.link['sha256']},
        ])
        self.assertEqual(rebuilt['series_history'], [])
        self.assertEqual(rebuilt['calibration_windows'], [])
        stop = rebuilt['calibration_decision']
        self.assertEqual((stop['decision'], stop['attempted'], stop['windows'], stop['target_per_pair']),
                         ('continue', 0, 8, 39))
        self.assertEqual(stop['eligible_by_pair'], {'spam': 0, 'bank': 0})
        self.assertEqual(stop['replacements_used'], 0)
        self.assertEqual(rebuilt['checks']['cohort_pool_rules']['status'], 'pass')
        self.assertEqual(rebuilt['checks']['cohort_pool_rules']['eligible_benign'], {'spam': 1, 'bank': 1})
        roster = w1.next_plan['members']
        self.assertEqual([row['ordinal'] for row in roster], list(range(1, 25)))
        sentinels = rebuilt['checks']['sentinel_roster']
        self.assertEqual(sentinels['status'], 'pass')
        self.assertEqual(sentinels['sentinel_ids'], ['align-v4-c1-e05', 'align-v4-c1-e22',
                                                     'align-v4-c1-e23', 'align-v4-c1-e24'])
        self.assertEqual(rebuilt['checks']['full_desk_gate']['status'], 'pass')
        self.assertEqual(rebuilt['last_desk_passed_artifact_set_sha256'],
                         registration.artifact_set_digest_at(w1.root, w1.code_commit))
        self.assertEqual(rebuilt['last_desk_passed_artifact_set_sha256'],
                         registration.artifact_set_digest(w1.root))
        self.assertIn(f'{w1.record_commit}:{w1.record["sources"]["desk"]["path"]}',
                      rebuilt['checks']['full_desk_gate']['sources'])
        raw_inventory = [row for row in rebuilt['evidence'] if 'locator' in row]
        self.assertCountEqual(raw_inventory, [
            {'commit': w1.record_commit, 'path': w1.record_path, **raw,
             'verification': 'committed_digest_inventory_only'} for raw in w1.record['captures'].values()
        ])
        live = ['series_powermode', 'external_volume', 'charging_battery', 'meter_reader_live']
        self.assertCountEqual(rebuilt['arm_pending'], live)
        self.assertCountEqual(rebuilt['packet_preflight']['arm_checks_still_required'], live)
        self.assertTrue(set(live).isdisjoint(rebuilt['checks']))
        self.assertTrue(rebuilt['packet_preflight']['ready'])

    def test_r1_pointer_cannot_replace_w1_in_the_series_ledger(self):
        w1 = self.c1_scenario()
        wrong = dict(record_commit=w1.previous.record_commit, record_path=w1.previous.record_path)
        code, output, error = self.cli_packet(w1, **wrong)
        self.assertEqual((code, output), (2, None))
        self.assertIn('series previous record binding mismatch', error)
        supplied = {**self.ready_packet(w1), **wrong}
        with self.assertRaisesRegex(ValueError, 'series previous record binding mismatch'):
            self.rebuild(w1, supplied)

    def test_an_independently_rebuilt_r1_cannot_bind_c1(self):
        w1 = self.c1_scenario()
        supplied = self.ready_packet(w1.previous)
        rebuilt, matches = self.rebuild(w1, supplied)
        self.assertTrue(matches)
        self.assertEqual((rebuilt['previous_window'], rebuilt['next_window_id']), ('R1', 'C1'))
        with self.assertRaisesRegex(ValueError, r'triage does not arm the next frozen window \(C1\)'):
            series.bind_packet(w1.root, 'C1', rebuilt, authenticated_by_rebuild=True)

    def test_forged_w1_digest_in_committed_series_state_refuses(self):
        w1 = self.c1_scenario()
        w1.series['previous_record']['sha256'] = '0' * 64
        self.commit_series(w1)
        code, output, error = self.cli_packet(w1)
        self.assertEqual((code, output), (2, None))
        self.assertIn('series previous record binding mismatch', error)

    def test_corrupt_committed_history_link_refuses(self):
        w1 = self.c1_scenario(bad_history_link=True)
        packet = self.refused_packet(w1)
        self.assertEqual(packet['calibration_error'], 'series history link digest mismatch')
        self.assertIn('calibration history: series history link digest mismatch',
                      packet['packet_preflight']['reasons'])

    def test_edits_to_the_supplied_hash_evidence_or_history_fail_canonical_comparison(self):
        for field in ('record_sha256', 'evidence', 'series_history'):
            with self.subTest(field=field):
                w1 = self.c1_scenario()
                supplied = self.ready_packet(w1)
                changed = {'record_sha256': '0' * 64, 'evidence': [],
                           'series_history': [{'window_id': 'C1'}]}
                rebuilt, matches = self.rebuild(w1, {**supplied, field: changed[field]})
                self.assertFalse(matches)
                self.assertEqual(rebuilt, supplied)
                self.assertTrue(rebuilt['packet_preflight']['ready'])

    def test_a_passing_desk_on_an_older_artifact_set_is_refused(self):
        w1 = self.c1_scenario(older_desk=True)
        packet = self.refused_packet(w1)
        older_digest = registration.artifact_set_digest_at(w1.root, w1.previous.code_commit)
        self.assertNotEqual(older_digest, registration.artifact_set_digest(w1.root))
        self.assertEqual(packet['last_desk_passed_artifact_set_sha256'], older_digest)
        self.assert_packet_failure(packet, 'full_desk_gate', 'different code/config state')

    def test_missing_or_pending_w1_full_desk_refuses(self):
        for desk, reason in (('missing', 'no final sources'), ('pending', 'full desk must complete and pass')):
            with self.subTest(desk=desk):
                w1 = self.c1_scenario(desk=desk)
                packet = self.refused_packet(w1)
                self.assert_packet_failure(packet, 'full_desk_gate', reason)

    def test_omitting_only_the_two_supplemental_sentinels_refuses(self):
        w1 = self.c1_scenario(extra_sentinels=False)
        self.assertEqual([row['ordinal'] for row in w1.next_plan['members']], list(range(1, 23)))
        packet = self.refused_packet(w1)
        self.assertEqual(packet['checks']['full_desk_gate']['status'], 'pass')
        self.assert_packet_failure(packet, 'sentinel_roster', 'two extra sentinels after a U4 inconclusive')

    def assert_wrong_sentinel_positions_refuse(self, *, use_frozen_names):
        w1 = self.c1_scenario(extra_sentinels=False)
        roster = w1.next_plan['members']
        for ordinal, name in zip((20, 21, 22), (22, 23, 24), strict=True):
            member = roster[ordinal - 1]
            member['role'] = 'sentinel'
            if use_frozen_names:
                member['run_id'] = f'align-v4-c1-e{name:02}'
        self.assertEqual(len(roster), 22)
        self.assertEqual([m['ordinal'] for m in roster if m['role'] == 'sentinel'], [5, 20, 21, 22])
        w1.series['sentinel_ids'] = [m['run_id'] for m in roster if m['role'] == 'sentinel']
        w1.series['next_plan'] = w1.write(w1.series['next_plan']['path'], w1.next_plan)
        self.commit_series(w1)

        packet = self.refused_packet(w1)
        rebuilt, matches = self.rebuild(w1, packet)
        self.assertTrue(matches)
        self.assertTrue(session._record_bound(w1.root, rebuilt))
        self.assertFalse(rebuilt['packet_preflight']['ready'])
        self.assertEqual(rebuilt['checks']['full_desk_gate']['status'], 'pass')
        self.assert_packet_failure(rebuilt, 'sentinel_roster', 'two extra sentinels after a U4 inconclusive')

    def test_relabelled_ordinary_members_cannot_substitute_for_escalation_sentinels(self):
        self.assert_wrong_sentinel_positions_refuse(use_frozen_names=False)

    def test_canonical_sentinel_ids_at_wrong_ordinals_refuse(self):
        self.assert_wrong_sentinel_positions_refuse(use_frozen_names=True)

    def test_only_the_frozen_pair_of_supplemental_ordinals_passes(self):
        w1 = self.c1_scenario()
        manifest = json.loads((w1.root / series.MANIFEST).read_bytes())
        expected = w1.series['sentinel_ids']
        base = w1.next_plan['members']
        candidates = [m['ordinal'] for m in base]
        sets = [*combinations(candidates, 2), (), (23,), (24,), (20, 23, 24), tuple(candidates)]
        for positions in sets:
            with self.subTest(positions=positions):
                members = [dict(m, role=(
                    'sentinel' if m['ordinal'] in (5, 22, *positions) else 'D' if m['role'] == 'sentinel' else m['role']
                )) for m in base]
                plan = {**w1.next_plan, 'members': members}
                if positions == (23, 24):
                    self.assertEqual(builder.frozen_sentinel_ids(manifest, plan, needs_supplemental=True), expected)
                else:
                    with self.assertRaisesRegex(ValueError, 'two extra sentinels after a U4 inconclusive'):
                        builder.frozen_sentinel_ids(manifest, plan, needs_supplemental=True)

    def test_frozen_sentinel_ids_cannot_swap_slots(self):
        w1 = self.c1_scenario()
        first, second = w1.next_plan['members'][-2:]
        first['run_id'], second['run_id'] = second['run_id'], first['run_id']
        w1.series['sentinel_ids'][-2:] = [first['run_id'], second['run_id']]
        w1.series['next_plan'] = w1.write(w1.series['next_plan']['path'], w1.next_plan)
        self.commit_series(w1)
        self.assert_packet_failure(self.refused_packet(w1), 'sentinel_roster',
                                   'two extra sentinels after a U4 inconclusive')

    def test_w1_receipt_digest_carries_through_the_rebuild(self):
        receipt = {'schema': registration.RECEIPT_SCHEMA, 'signer': 'invented fixture'}
        w1 = self.c1_scenario(receipt=receipt)
        packet = self.ready_packet(w1)
        rebuilt, matches = self.rebuild(w1, packet)
        self.assertTrue(matches)
        sources = w1.record['sources']
        full_desk = rebuilt['checks']['full_desk_gate']
        self.assertEqual(full_desk['desk_sha256'], sources['desk']['sha256'])
        self.assertEqual(full_desk['registration_receipt_sha256'], sources['registration_receipt']['sha256'])
        self.assertEqual(rebuilt['last_desk_passed_artifact_set_sha256'],
                         registration.artifact_set_digest_at(w1.root, w1.code_commit))
        w1.write(registration.REGISTRATION + 'registration_receipt.json', {'edited': True})
        self.assertEqual(self.ready_packet(w1), packet)

    def commit_projection(self, w1):
        w1.series['next_plan'] = w1.write(w1.series['next_plan']['path'], w1.next_plan)
        self.commit_series(w1)

    def test_v3_w1_desk_cannot_borrow_r1_artifact_state(self):
        w1 = self.c1_scenario(older_desk=True, receipt={'signer': 'invented W1'})
        w1.write(CODE_PATH, b'synthetic-code-v0\n')
        r1_digest = registration.artifact_set_digest_at(w1.root, w1.previous.code_commit)
        w1_digest = registration.artifact_set_digest_at(w1.root, w1.code_commit)
        self.assertEqual(registration.artifact_set_digest(w1.root), r1_digest)
        self.assertNotEqual(w1_digest, r1_digest)

        w1.series['last_passed_record'] = dict(w1.link)
        self.commit_series(w1)
        control = w1.series_commit
        self.assert_packet_failure(self.refused_packet(w1), 'full_desk_gate', 'different code/config state')

        w1.series['last_passed_record'] = dict(w1.previous.link)
        self.commit_series(w1)
        self.assertEqual(w1.git('diff', '--name-only', control, w1.series_commit), w1.series_path)
        code, supplied, error = self.cli_packet(w1)
        self.assertIsNotNone(supplied, error)
        rebuilt, matches = self.rebuild(w1, supplied)
        self.assertTrue(matches)
        self.assertTrue(session._record_bound(w1.root, rebuilt))
        self.assertEqual(rebuilt['checks']['sentinel_roster']['status'], 'pass')
        desk = rebuilt['checks']['full_desk_gate']
        self.assertEqual(code, 2, {
            'ready': rebuilt['packet_preflight']['ready'],
            'full_desk': desk['status'],
            'desk_matches_w1': desk.get('desk_sha256') == w1.record['sources']['desk']['sha256'],
            'artifact_digest_matches_r1': rebuilt['last_desk_passed_artifact_set_sha256'] == r1_digest,
        })
        self.assertFalse(rebuilt['packet_preflight']['ready'])
        self.assertEqual(desk['status'], 'fail')
        self.assertIn('triage full_desk_gate failed', rebuilt['packet_preflight']['reasons'])

    def test_v3_genuine_projection_binds_w1_desk_and_receipt_copies(self):
        receipt = {'schema': registration.RECEIPT_SCHEMA, 'signer': 'invented W1'}
        w1 = self.c1_scenario(receipt=receipt)
        supplied = self.ready_packet(w1)
        rebuilt, matches = self.rebuild(w1, supplied)
        self.assertTrue(matches)
        self.assertIs(series.bind_packet(w1.root, 'C1', rebuilt, authenticated_by_rebuild=True), rebuilt)
        self.assertEqual(w1.series['last_passed_record'], w1.link)
        desk = rebuilt['checks']['full_desk_gate']
        self.assertEqual(desk['desk_sha256'], w1.record['sources']['desk']['sha256'])
        self.assertEqual(desk['registration_receipt_sha256'],
                         w1.record['sources']['registration_receipt']['sha256'])
        self.assertEqual(rebuilt['last_desk_passed_artifact_set_sha256'],
                         registration.artifact_set_digest_at(w1.root, w1.code_commit))

        w1.write(registration.REGISTRATION + 'registration_receipt.json', {**receipt, 'different': True})
        w1.record['finalized_at_epoch_s'] += 1
        self.recommit_predecessor(w1)
        self.assert_packet_failure(self.refused_packet(w1), 'full_desk_gate', 'source SHA-256 mismatch')

    def test_v3_full_ordered_legacy_projection_is_admitted(self):
        w1 = self.c1_scenario()
        for row in w1.next_plan['members']:
            del row['ordinal']
        self.commit_projection(w1)
        supplied = self.ready_packet(w1)
        rebuilt, matches = self.rebuild(w1, supplied)
        self.assertTrue(matches)
        self.assertEqual(rebuilt, supplied)
        self.assertEqual(rebuilt['checks']['sentinel_roster']['sentinel_ids'], w1.series['sentinel_ids'])
        self.assertIs(series.bind_packet(w1.root, 'C1', rebuilt, authenticated_by_rebuild=True), rebuilt)
        self.assertCountEqual(rebuilt['packet_preflight']['arm_checks_still_required'], INTERNAL)
        self.assertTrue(set(INTERNAL).isdisjoint(rebuilt['checks']))

    def test_v3_legacy_projection_cannot_move_or_duplicate_sentinel_ids(self):
        for defect in ('moved', 'duplicate'):
            with self.subTest(defect=defect):
                w1 = self.c1_scenario()
                members = w1.next_plan['members']
                for row in members:
                    del row['ordinal']
                if defect == 'moved':
                    members[19], members[22] = members[22], members[19]
                    members[20], members[23] = members[23], members[20]
                else:
                    members[19]['run_id'] = members[22]['run_id']
                w1.series['sentinel_ids'] = [row['run_id'] for row in members if row['role'] == 'sentinel']
                self.commit_projection(w1)
                self.assert_packet_failure(self.refused_packet(w1), 'sentinel_roster', 'two extra sentinels')

    def test_v3_explicit_ordinal_cannot_contradict_ordered_position(self):
        for bad in (20, True, '23'):
            with self.subTest(bad=bad):
                w1 = self.c1_scenario()
                w1.next_plan['members'][22]['ordinal'] = bad
                self.commit_projection(w1)
                self.assert_packet_failure(self.refused_packet(w1), 'sentinel_roster', 'two extra sentinels')

    def test_a_changed_next_plan_cohort_cannot_carry_the_w1_pool(self):
        w1 = self.c1_scenario(wrong_cohort=True)
        packet = self.refused_packet(w1)
        self.assertEqual(packet['checks']['sentinel_roster']['status'], 'pass')
        self.assert_packet_failure(packet, 'cohort_pool_rules', 'pool crosses a changed configuration or identity')

    def test_uncommitted_edits_cannot_replace_the_bound_w1_predecessor(self):
        w1 = self.c1_scenario()
        supplied = self.ready_packet(w1)
        w1.write(w1.record_path, w1.previous.record)
        w1.write(w1.series_path, {**w1.series, 'previous_record': w1.previous.link})
        w1.write(w1.record['sources']['desk']['path'], {'status': 'running_off_mbp'})
        self.assertEqual(self.ready_packet(w1), supplied)
        rebuilt, matches = self.rebuild(w1, supplied)
        self.assertTrue(matches)
        self.assertEqual(rebuilt, supplied)
        self.assertTrue(session._record_bound(w1.root, rebuilt))

    def test_stale_pointer_rebuilds_but_fails_current_record_binding(self):
        w1 = self.c1_scenario()
        supplied = self.ready_packet(w1)
        self.assertTrue(session._record_bound(w1.root, supplied))
        w1.record['finalized_at_epoch_s'] += 1
        self.recommit_predecessor(w1)
        self.assertTrue(session._record_bound(w1.root, self.ready_packet(w1)))
        rebuilt, matches = self.rebuild(w1, supplied)
        self.assertTrue(matches)
        self.assertTrue(rebuilt['packet_preflight']['ready'])
        result = self.triage(w1, rebuilt)
        self.assertFalse(result['admitted'])
        self.assertFalse(result['derived']['record_bound'])
        self.assertIn('a stale packet refuses', result['checks']['record_committed']['basis'])
        self.assertIn('triage record_committed failed', result['reasons'])

    def test_expired_pointer_and_missing_expiry_are_refused(self):
        w1 = self.c1_scenario()
        supplied = self.ready_packet(w1)
        self.assertEqual(supplied['valid_until_epoch_s'], 140)
        late = 141.0
        self.assertIn('packet expired before this arm', self.triage(w1, supplied, now=late)['reasons'])
        rebuilt, matches = self.rebuild(w1, supplied, now=late)
        self.assertFalse(matches)
        self.assertEqual(rebuilt, self.refused_packet(w1, now=late))
        self.assert_packet_failure(rebuilt, 'quiet_start_state', 'quiet start evidence stale')

        w1 = self.c1_scenario()
        supplied = self.ready_packet(w1)
        del supplied['valid_until_epoch_s']
        rebuilt, matches = self.rebuild(w1, supplied)
        self.assertFalse(matches)
        self.assertEqual(rebuilt['valid_until_epoch_s'], 140)
        self.assertTrue(rebuilt['packet_preflight']['ready'])


class PacketTests(Base):
    def test_w1_record_admits_and_binds_all_raw_bytes_without_following_custody(self):
        s = self.scenario().finish()
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight']['reasons'])
        result = evaluate(s, packet)
        self.assertTrue(result['admitted'], result['reasons'])
        self.assertEqual(packet['record_commit'], s.record_commit)
        self.assertEqual(packet['checks']['sentinel_roster']['sentinel_ids'], s.series['sentinel_ids'])
        self.assertEqual(set(packet['checks']), {r['id'] for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.PACKET})
        self.assertEqual(set(packet['entry_sources']), set(cad.TRIAGE_IDS))
        self.assertEqual(len(cad.TRIAGE_IDS), 16)      # 15 gating + non-gating meter_coverage (battery_window added by ruling 9)
        self.assertEqual(packet['arm_pending'], list(INTERNAL))
        self.assertIn('meter_reader_live', packet['arm_pending'])
        self.assertEqual(packet, s.build())          # reproducible: the arm's clock is not embedded
        for source in packet['evidence']:
            actual = subprocess.run(['git', '-C', str(s.root), 'show', source['commit'] + ':' + source['path']],
                                    check=True, capture_output=True).stdout
            self.assertEqual(hashlib.sha256(actual).hexdigest(), source['sha256'])
        paths = {r['path'] for r in packet['evidence']}
        self.assertTrue({s.record_path, s.series_path, f'{s.dir}/raw/sidecar.jsonl'} <= paths)

    def test_each_packet_entry_refuses_for_its_documented_reason(self):
        mutations = {
            'record_committed': (lambda s: s.record.pop('finalized_at_epoch_s'), 'record finalization missing'),
            'terminal_completion': (lambda s: s.sources['watchdog_state'].update(released_terminal_windows=[]), 'watchdog empty-process'),
            'quiet_start_state': (lambda s: s.quiet.update(active_work=['hashing']), 'evidence traffic remains'),
            'capture_faults': (lambda s: s.thermal['members'][0].pop('coverage'), 'X1-X8 tabulation missing'),
            'thermal_escalation': (lambda s: s.thermal['model_windows']['tiny/W1']['U1'].update(status='fail'), 'prospective recorded escalation'),
            'cohort_pool_rules': (lambda s: s.thermal['members'][0]['configuration'].update(max_turns=5), 'four-slot cohort'),
            'sentinel_roster': (lambda s: s.next_plan['members'].pop(), 'two extra sentinels'),
            'member_eligibility': (lambda s: s.thermal['members'][0].update(excluded=True), 'final exclusions disagree'),
            'full_desk_gate': (lambda s: s.sources['desk'].update(pilot_status='instrument_incomplete'), 'no passing desk'),
        }
        for name, (mutate, reason) in mutations.items():
            with self.subTest(name=name):
                s = self.scenario()
                mutate(s)
                packet = s.finish().build()
                self.assertEqual(packet['checks'][name]['status'], 'fail')
                self.assertIn(reason, packet['checks'][name]['basis'])
                self.assertFalse(packet['packet_preflight']['ready'])
                self.assertIn('triage ' + name + ' failed', evaluate(s, packet)['reasons'])
        s = self.scenario().finish()
        packet = s.build()
        for name in INTERNAL:
            with self.subTest(name=name):
                self.assertIn('triage ' + name + ' failed or unevaluated',
                              evaluate(s, packet, internal={**INTERNAL, name: False})['reasons'])
        packet['next_window_role'] = 'test'
        self.assertFalse(evaluate(s, packet)['admitted'])

    def test_raw_digest_mismatch_and_unpushed_record_refuse(self):
        s = self.scenario().finish()
        record = copy.deepcopy(s.record)
        record['raw_evidence'][0]['sha256'] = '0'*64
        index = s.write(s.record_path, record)
        s.record_commit = s.commit()
        s.git('update-ref', 'refs/remotes/synthetic/records', s.record_commit)
        s.series['previous_record'] = {'commit': s.record_commit, 'path': s.record_path, 'sha256': index['sha256']}
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        self.assertIn('SHA-256 mismatch', s.build()['checks']['record_committed']['basis'])
        s = self.scenario().finish()
        self.assertEqual(s.build(pushed_ref='refs/remotes/missing/records')['checks']['record_committed']['status'], 'fail')
        self.assertIn('remote-tracking', s.build(pushed_ref='HEAD')['checks']['record_committed']['basis'])

    def test_dirty_worktree_does_not_change_committed_evidence(self):
        s = self.scenario().finish()
        original = s.build()
        s.write(f'{s.dir}/evidence/result.json', {'forged': True})
        self.assertEqual(s.build(current=registration.artifact_set_digest(s.root)), original)

    def test_large_raw_custody_digests_are_retained_without_opening_locators(self):
        s = self.scenario()
        s.raw_custody = True
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        rows = [r for r in packet['evidence'] if r.get('locator')]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r['verification'] == 'committed_digest_inventory_only' for r in rows))

    def test_binding_mismatch_nonexistent_commit_and_unsafe_paths_refuse(self):
        s = self.scenario().finish()
        with self.assertRaisesRegex(ValueError, 'Git evidence unavailable'):
            s.build(record_commit='0'*40)
        for path in ('/Users/edr/DO-NOT-READ', '../record.json', 'restricted/record.json',
                     'night-custody/record.json', 'jw-b5-fake/record.json'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'safe repository-relative'):
                s.build(record_path=path)
        s.series['previous_record']['sha256'] = '0'*64
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        with self.assertRaisesRegex(ValueError, 'binding mismatch'):
            s.build()

    def test_secondary_meter_coverage_never_blocks_even_when_missing(self):
        s = self.scenario()
        s.sources['pilot']['extra_checks']['km003c']['members'][s.members[0]['run_id']] = {
            'status': 'missing', 'flags': ['meter.member_gap', 'meter.clock_unresolved']}
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual(packet['checks']['meter_coverage']['status'], 'recorded')
        self.assertEqual(packet['checks']['meter_coverage']['gaps'][s.members[0]['run_id']],
                         ['meter.member_gap', 'meter.clock_unresolved'])
        s = self.scenario()
        del s.sources['pilot']['extra_checks']['km003c']['members'][s.members[0]['run_id']]
        packet = s.finish().build()
        self.assertEqual(packet['checks']['meter_coverage']['status'], 'recorded')
        self.assertTrue(packet['packet_preflight']['ready'])
        s = self.scenario()
        del s.sources['pilot']['extra_checks']['km003c']             # no tabulation at all (R1 -> W1)
        packet = s.finish().build()
        self.assertEqual(packet['checks']['meter_coverage']['tabulation'], 'missing')
        self.assertTrue(evaluate(s, packet)['admitted'])

    def test_first_w1_packet_uses_r1_coverage_without_claiming_u_checks(self):
        s = self.scenario('R1')
        s.next_plan.update(window='W1', role='development')
        del s.thermal['model_windows']
        packet = s.finish().build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        evaluated = evaluate(s, packet)
        self.assertTrue(evaluated['admitted'], evaluated['reasons'])
        self.assertEqual(evaluated['checks']['calibration_stop']['status'], 'not_applicable')
        for name in ('thermal_escalation', 'cohort_pool_rules', 'sentinel_roster', 'member_eligibility'):
            self.assertEqual(packet['checks'][name]['status'], 'not_applicable')

    def test_quiet_cannot_use_old_or_future_observations_judged_at_the_arms_clock(self):
        for epoch in (90, 112, 100):
            with self.subTest(epoch=epoch):
                s = self.scenario()
                s.quiet['observed_at_epoch_s'] = epoch
                s.series['quiet_requirements']['max_age_s'] = 5
                self.assertEqual(s.finish().build()['checks']['quiet_start_state']['status'], 'fail')
        s = self.scenario().finish()
        self.assertEqual(s.build(now=140.0)['checks']['quiet_start_state']['status'], 'pass')   # 30 s old: at the limit
        self.assertEqual(s.build(now=141.0)['checks']['quiet_start_state']['status'], 'fail')

    def test_counts_derived_from_capture_and_final_exclusions_not_series_assertions(self):
        s = self.calibration_series([('C1', True, False)])
        s.series['eligible_benign'] = {'spam': 7, 'bank': 7}          # deliberately ignored
        packet = s.build()
        self.assertEqual(packet['calibration_windows'][0]['eligible_benign'], {'spam': 0, 'bank': 1})
        self.assertEqual(packet['calibration_windows'][0]['captured_members'], 2)

    def test_divergent_u3_pair_requires_x5_adjudication_not_new_member_exclusions(self):
        s = self.scenario()
        for member in s.thermal['members']:
            member['identical_work_group'] = 'pair'
        s.thermal['members'][0]['tokens'] = [[9]]
        self.assertEqual(s.finish().build()['checks']['member_eligibility']['status'], 'fail')
        s = self.scenario()
        for member in s.thermal['members']:
            member['identical_work_group'] = 'pair'
        s.thermal['members'][0]['tokens'] = [[9]]
        s.thermal['model_windows']['tiny/W1']['U3']['pairs'] = [
            {'status': 'excluded', 'exclusion': 'X5', 'token_identical': False}]
        self.assertEqual(s.finish().build()['checks']['member_eligibility']['status'], 'pass')

    def test_l1_a_failing_u1_u3_gives_that_model_zero_eligible_from_the_window(self):
        s = self.calibration_series([])
        s2 = Scenario(s.root, 'C1', previous=s)
        s2.thermal['model_windows']['tiny/C1']['U2']['status'] = 'fail'
        s2.finish()
        self.assertEqual(s2.build()['calibration_windows'][0]['eligible_benign'], {'spam': 0, 'bank': 0})

    def test_template_is_fail_closed_and_cli_never_overwrites(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(builder.main(['--emit-triage-template']), 0)
        template = json.loads(output.getvalue())
        self.assertFalse(cad.next_arm_triage(template['packet'], INTERNAL, now_epoch_s=NOW)['admitted'])
        self.assertIn('record', template)
        self.assertIsNone(template['record']['previous_record'])
        self.assertIn('lead_rulings', template['series'])
        s = self.scenario().finish()
        target = s.root / 'packet.json'
        argv = ['--repo', str(s.root), '--record-commit', s.record_commit, '--record-path', s.record_path,
                '--series-commit', s.series_commit, '--series-path', s.series_path,
                '--pushed-ref', 'refs/remotes/synthetic/records', '--output', str(target)]
        with patch('time.time', return_value=NOW):
            self.assertEqual(builder.main(argv), 0)
            self.assertTrue(json.loads(target.read_text())['packet_preflight']['ready'])
            with self.assertRaises(FileExistsError):
                builder.main(argv)

    def test_duplicate_keys_and_nonfinite_json_refuse(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                builder.decode(raw)

    def test_deadman_delivery_receipt_releases_a_failed_run_path_courier(self):
        for mutation in ('none', 'digest', 'plan', 'ref', 'commit', 'missing'):
            with self.subTest(mutation=mutation):
                s = self.scenario()
                s.sources['courier']['sent'] = False
                raw = (json.dumps(s.sources['result'], sort_keys=True) + '\n').encode()
                receipt = {'transport': 'git-push', 'plan_id': s.sources['plan']['plan_id'],
                           'ref': 'refs/heads/night-results/' + s.sources['plan']['plan_id'],
                           'commit': 'a' * 40, 'result_sha256': builder.digest(raw)}
                if mutation == 'digest':
                    receipt['result_sha256'] = '0' * 64
                elif mutation == 'plan':
                    receipt['plan_id'] = 'other-plan'
                elif mutation == 'ref':
                    receipt['ref'] = 'refs/heads/main'
                elif mutation == 'commit':
                    receipt['commit'] = 'bad'
                if mutation != 'missing':
                    s.sources['courier_delivery'] = receipt
                status = s.finish().build()['checks']['terminal_completion']['status']
                self.assertEqual(status, 'pass' if mutation == 'none' else 'fail')

    def test_missing_source_and_symlink_refuse(self):
        s = self.scenario()
        s.omit_sources.add('courier')
        self.assertEqual(s.finish().build()['checks']['terminal_completion']['status'], 'fail')
        s = self.scenario().finish()
        (s.root / 'link.json').symlink_to('/DO-NOT-OPEN')
        commit = s.commit()
        with self.assertRaisesRegex(ValueError, 'regular blob'):
            builder.GitEvidence(s.root).read(commit, 'link.json')


class HistoryChainTests(Base):
    def test_hash_linked_history_gives_counted_windows_in_order_and_detects_omission(self):
        s = self.calibration_series([('C1', True, True), ('C2', True, True), ('C3', True, True)])
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual([r['window'] for r in packet['calibration_windows']], ['C1', 'C2', 'C3'])
        self.assertEqual(packet['calibration_decision']['attempted'], 3)
        # an omitted attempt (C2 missing between C1 and C3) cannot be hidden: the link is the history
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-omit-')
        self.addCleanup(temp.cleanup)
        first = Scenario(temp.name, 'W1').finish()
        c1 = Scenario(temp.name, 'C1', previous=first).finish()
        c3 = Scenario(temp.name, 'C3', previous=c1).finish()
        omitted = c3.build()
        self.assertFalse(omitted['packet_preflight']['ready'])
        self.assertIn('omitted', omitted['calibration_error'])

    def test_a_forged_link_digest_and_a_chain_that_never_reaches_w1_refuse(self):
        s = self.calibration_series([('C1', True, True)])
        record = copy.deepcopy(s.record)
        record['previous_record'] = {**record['previous_record'], 'sha256': '0'*64}
        index = s.write(s.record_path, record)
        s.record_commit = s.commit()
        s.git('update-ref', 'refs/remotes/synthetic/records', s.record_commit)
        s.series['previous_record'] = {'commit': s.record_commit, 'path': s.record_path, 'sha256': index['sha256']}
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('link digest mismatch', packet['calibration_error'])
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-nochain-')
        self.addCleanup(temp.cleanup)
        orphan = Scenario(temp.name, 'C1').finish()          # a first record that is not R1/W1
        packet = orphan.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('first v4 record', packet['calibration_error'])

    def test_zero_capture_retry_keeps_the_window_id_with_an_attempt_suffix(self):
        s = self.calibration_series([('C1', True, True), ('C2', False, True), ('C2#2', True, True)])
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual([r['window'] for r in packet['calibration_windows']], ['C1', 'C2', 'C2#2'])
        decision = packet['calibration_decision']
        self.assertEqual((decision['attempted'], decision['zero_capture_refusals']), (2, 1))
        # the frozen order is unchanged: a retry cannot take the next number or skip its own
        for bad in ([('C1', True, True), ('C2', False, True), ('C3', True, True)],
                    [('C1', True, True), ('C1#3', False, True)],
                    [('C1', True, True), ('C1#2', True, True)]):
            with self.subTest(bad=[b[0] for b in bad]):
                self.assertFalse(self.calibration_series(bad).build()['packet_preflight']['ready'])

    def test_battery_window_follows_the_desk_b_bar_along_the_chain(self):
        # Lead ruling 9 (W1-BLOCKERS): pass; first non-pass resumes automatically; a second
        # consecutive non-pass needs a signed battery ruling whose text digest the builder computes.
        passed = self.calibration_series([('C1', True, True)]).build()
        self.assertEqual(passed['checks']['battery_window']['status'], 'pass')
        first = self.calibration_series([('C1', True, True), ('C2', True, True, False)]).build()
        self.assertEqual(first['checks']['battery_window']['consecutive_non_pass'], 1)
        self.assertTrue(first['packet_preflight']['ready'], first['packet_preflight'])      # automatic_resume
        s = self.calibration_series([('C1', True, True, False), ('C2', True, True, False)])
        second = s.build()
        self.assertEqual(second['checks']['battery_window']['consecutive_non_pass'], 2)
        self.assertFalse(second['packet_preflight']['ready'])
        text = b'LEAD BATTERY DISPOSITION SYNTHETIC-B1: resume after two non-passing B windows\n'
        ref = s.write(f'{s.dir}/rulings/battery-1.txt', text)
        s.series['battery_rulings'] = [{'ruling_id': 'SYNTHETIC-B1', 'after_window': 'C2', 'text': ref,
                                        'lead_signature': 'lead: synthetic-battery 2026-11-08'}]
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        ruled = s.build()
        self.assertEqual(ruled['battery_rulings'], [{
            'ruling_id': 'SYNTHETIC-B1', 'text_sha256': hashlib.sha256(text).hexdigest(), 'after_window': 'C2',
            'lead_signature': 'lead: synthetic-battery 2026-11-08'}])
        self.assertTrue(ruled['packet_preflight']['ready'], ruled['packet_preflight'])
        # a passing window in between resets the streak; a ruling for another window does not resume
        reset = self.calibration_series([('C1', True, True, False), ('C2', True, True), ('C3', True, True, False)]).build()
        self.assertEqual(reset['checks']['battery_window']['consecutive_non_pass'], 1)
        s.series['battery_rulings'][0]['after_window'] = 'C1'
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        self.assertFalse(s.build()['packet_preflight']['ready'])
        # a failed B bar alone does not fail the full desk (the exempt key matches the session's)
        from scripts import align_v4_session as session
        self.assertEqual(builder.FULL_DESK_GATE_EXEMPT, session.FULL_DESK_GATE_EXEMPT)
        self.assertEqual(first['checks']['full_desk_gate']['status'], 'pass')

    def test_a_zero_capture_retry_that_is_also_zero_bars_the_slot_and_a_replacement_is_owed(self):
        # R22-2: a zero-capture refusal beyond the retry is a STRUCTURAL bar: the slot is replaced (C9), not
        # escalated, and nothing depends on scores or counts.
        s = self.calibration_series([('C1', False, True), ('C1#2', False, True)])
        packet = s.build()
        decision = packet['calibration_decision']
        self.assertEqual(decision['decision'], 'continue')
        self.assertEqual((decision['barred_windows'], decision['replacements_used']), (['C1#2'], 1))
        self.assertEqual(decision['attempted'], 0)
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])

    def test_a_seventh_zero_capture_bar_escalates_until_a_ruling_with_a_committed_text(self):
        # R24: six replacement windows (C9-C14) absorb six bars; the seventh escalates
        spec = [(f'C{n}{suffix}', False, True) for n in range(1, 8) for suffix in ('', '#2')]
        s = self.calibration_series(spec)
        packet = s.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertEqual(packet['calibration_decision']['decision'], 'escalate_to_lead')
        text = b'LEAD RULING SYNTHETIC-1: seven zero-capture bars, all six replacement windows exhausted\n'
        ref = s.write(f'{s.dir}/rulings/synthetic-1.txt', text)
        s.series['lead_rulings'] = [{'ruling_id': 'SYNTHETIC-1', 'after_window': 'C7#2', 'text': ref,
                                     'lead_signature': 'lead: synthetic-ruling 2026-11-08'}]
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertEqual(packet['lead_rulings'], [{
            'ruling_id': 'SYNTHETIC-1', 'text_sha256': hashlib.sha256(text).hexdigest(),
            'resets': 'zero_capture_escalation', 'after_window': 'C7#2',
            'lead_signature': 'lead: synthetic-ruling 2026-11-08'}])        # the digest is computed, not entered
        # the ruling resets the trailing refusal count but cannot repair calibration: 8 counted windows are
        # out of reach once more than two windows are barred
        self.assertEqual(packet['calibration_decision']['decision'], 'insufficient_calibration')
        self.assertEqual(packet['calibration_decision']['zero_capture_refusals'], 14)
        self.assertFalse(packet['packet_preflight']['ready'])
        for bad in ({'ruling_id': 'X', 'after_window': 'C9', 'text': ref, 'lead_signature': 'lead: s 2026-11-08'},
                    {'ruling_id': 'X', 'after_window': 'C7#2', 'text': {**ref, 'sha256': '0'*64},
                     'lead_signature': 'lead: s 2026-11-08'},
                    {'ruling_id': 'X', 'after_window': 'C7#2', 'text': ref, 'lead_signature': 'PENDING'},
                    {'ruling_id': 'X', 'after_window': 'C7#2', 'text': ref}):
            s.series['lead_rulings'] = [bad]
            s.write(s.series_path, s.series)
            s.series_commit = s.commit()
            with self.subTest(bad=str(bad)[:60]):
                self.assertFalse(s.build()['packet_preflight']['ready'])


class SentinelTriggerTests(Base):
    """A15 / R21: the R20 escalation sentinels trigger on a U4 inconclusive only; U5 never does."""

    def roster_check(self, u4, u5):
        s = self.calibration_series([('C1', True, True)])
        s.next_plan['members'] = s.next_plan['members'][:-2]                  # the ordinary roster
        s.series['sentinel_ids'] = s.series['sentinel_ids'][:2]
        s.thermal['model_windows']['tiny/C1']['U4']['status'] = u4
        s.thermal['model_windows']['tiny/C1']['U5']['status'] = u5
        s.finish()
        return s.build()['checks']['sentinel_roster']

    def test_a_u5_inconclusive_alone_does_not_require_the_escalation_sentinels(self):
        self.assertEqual(self.roster_check('pass', 'inconclusive')['status'], 'pass')
        self.assertEqual(self.roster_check('pass', 'pass')['status'], 'pass')

    def test_a_u4_inconclusive_requires_them(self):
        check = self.roster_check('inconclusive', 'pass')
        self.assertEqual(check['status'], 'fail')
        self.assertIn('two extra sentinels after a U4 inconclusive', check['basis'])
        self.assertEqual(self.roster_check('inconclusive', 'inconclusive')['status'], 'fail')

    def test_the_desk_consequence_adds_sentinels_for_u4_only(self):
        from joulewise.align.apple import thermal_desk
        from tests.align.test_thermal_desk import member
        rows = []
        for ordinal in (5, 22):
            row = member(str(ordinal))
            row.update(window='C1', role='D', u3_configuration_sha256='a' * 64)
            rows.append(row)
        for key, cross, expected in (
                ('u4', {'synthetic': {'sentinels': {'status': 'inconclusive'}}}, 'add 2 sentinels per remaining window'),
                ('u5', {'synthetic': {'sentinels': {'status': 'pass', 'W': 8, 'df': 7}}}, None)):
            report = thermal_desk.window_report(rows, v4=True, cross_windows=cross,
                                                sensitivity={'synthetic': {'status': 'inconclusive'}} if key == 'u5' else None)
            consequence = next(iter(report['model_windows'].values()))['consequence']
            if key == 'u4':
                self.assertEqual(consequence, expected)
            else:
                self.assertNotEqual(consequence, 'add 2 sentinels per remaining window')


class DeskDerivationTests(Base):
    def test_last_desk_digest_is_computed_from_committed_bytes_and_drives_the_desk_requirement(self):
        s = self.calibration_series([('C1', True, True)])
        s.series['last_passed_record'] = dict(s.link)
        packet = s.build()
        self.assertEqual(packet['last_desk_passed_artifact_set_sha256'],
                         registration.artifact_set_digest_at(s.root, s.code_commit))
        self.assertNotIn('code_or_config_changed', packet)
        self.assertNotIn('previous_window_is_w1', packet)
        self.assertEqual(packet['last_desk_passed_artifact_set_sha256'], registration.artifact_set_digest(s.root))
        # unchanged later window: a desk still running off the MBP defers
        deferred = s.sources['desk'].update(status='running_off_mbp', pilot_status='instrument_incomplete')
        self.assertIsNone(deferred)
        s.write(f'{s.dir}/evidence/desk.json', s.sources['desk'])
        s.record['sources']['desk'] = {'path': f'{s.dir}/evidence/desk.json',
                                       'sha256': hashlib.sha256((s.root / f'{s.dir}/evidence/desk.json').read_bytes()).hexdigest()}
        index = s.write(s.record_path, s.record)
        s.record_commit = s.commit()
        s.git('update-ref', 'refs/remotes/synthetic/records', s.record_commit)
        s.series['previous_record'] = {'commit': s.record_commit, 'path': s.record_path, 'sha256': index['sha256']}
        s.series['last_passed_record'] = {'commit': first_commit(s), 'path': 'w-W1/record.json',
                                          'sha256': hashlib.sha256(subprocess.run(
                                              ['git', '-C', str(s.root), 'show', f'{first_commit(s)}:w-W1/record.json'],
                                              capture_output=True, check=True).stdout).hexdigest()}
        s.write(s.series_path, s.series)
        s.series_commit = s.commit()
        packet = s.build()
        self.assertEqual(packet['checks']['full_desk_gate']['status'], 'deferred', packet['checks']['full_desk_gate'])

    def test_after_w1_or_a_code_change_the_full_desk_must_have_passed_on_the_current_state(self):
        s = self.scenario().finish()                                   # previous window W1, desk passed, same code
        self.assertEqual(s.build()['checks']['full_desk_gate']['status'], 'pass')
        changed = s.build(current=registration.artifact_set_digest(s.root).replace('0', '1', 1) or 'f'*64)
        if changed['checks']['full_desk_gate']['status'] == 'pass':      # digest happened to lack a 0
            changed = s.build(current='f'*64)
        self.assertEqual(changed['checks']['full_desk_gate']['status'], 'fail')
        self.assertIn('different code/config state', changed['checks']['full_desk_gate']['basis'])


def first_commit(scenario):
    return scenario.git('log', '--format=%H', '--reverse', '--', 'w-W1/record.json').splitlines()[0]


class ArmRebuildTests(Base):
    """The arm calls the builder itself; a supplied packet is a pointer, never trusted data."""

    def arm(self, s, packet, *, now=NOW, **kwargs):
        from scripts import align_v4_session as session
        from tests.align.test_v4_cadence import write_battery_log
        path = s.root / 'supplied-packet.json'
        if path.exists():
            path.unlink()
        path.write_text(json.dumps(packet, indent=2))
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        with patch('joulewise.align.apple.powermode.admit_ac_powermode', return_value={'admitted': True}), \
             patch('joulewise.align.apple.external_volume.census', return_value={}), \
             patch('joulewise.align.apple.external_volume.arm_check', return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', return_value=(good, b'raw')):
            log = write_battery_log(Path(tempfile.mkdtemp(dir=s.root.parent)) / 'battery.jsonl', now)
            return session.arm_checks(s.root, {}, next_arm_triage=path, now=lambda: now, battery_log=log,
                                      watchdog_check=_watchdog_acceptance, runner=lambda argv: subprocess.CompletedProcess(argv, 0, 'pmset', ''),
                                      obc_off_attested_by='synthetic',
                                      meter_probe=kwargs.pop('meter_probe', lambda root: {'live': True, 'samples': 40}),
                                      **kwargs)

    def test_honest_packet_admits_and_the_arm_record_retains_its_own_build(self):
        s = self.scenario().finish()
        record = self.arm(s, s.build())
        self.assertTrue(record['admitted'], record['reasons'])
        triage = record['next_arm_triage']
        self.assertTrue(triage['supplied_packet_matches_rebuild'])
        self.assertEqual(triage['packet']['record_commit'], s.record_commit)
        self.assertEqual(triage['meter_live_evidence']['live'], True)
        self.assertEqual(triage['packet_sha256'], cad._canonical_sha256(triage['packet']))

    def test_the_meter_probe_ends_before_the_quiet_dwell_starts_and_never_during_it(self):
        # Lead ruling 2026-11-08: the 3 s monitor launch is USB and process activity; it runs before the
        # quiet/display dwell starts. The arm stamps both on one monotonic clock and records the order.
        s = self.scenario().finish()
        record = self.arm(s, s.build())
        self.assertTrue(record['admitted'], record['reasons'])
        dwell = record['quiet_dwell']
        self.assertTrue(dwell['meter_probe_before_dwell'])
        evidence = record['next_arm_triage']['meter_live_evidence']
        self.assertLess(evidence['probe_started_ns'], evidence['probe_ended_ns'])
        self.assertLess(evidence['probe_ended_ns'], dwell['start_ns'])
        self.assertEqual(dwell['meter_probe_ended_ns'], evidence['probe_ended_ns'])
        # a dwell that started at or before the probe's end refuses the arm, whatever the meter says
        for label, start in (('dwell already running', lambda: 1), ('dwell starts as the probe ends', None)):
            with self.subTest(label=label):
                kwargs = {'dwell_start': start} if start else {
                    'meter_probe': lambda root: {'live': True, 'probe_ended_ns': 10**15},
                    'dwell_start': lambda: 10**15}
                refused = self.arm(s, s.build(), **kwargs)
                self.assertFalse(refused['admitted'])
                self.assertFalse(refused['quiet_dwell']['meter_probe_before_dwell'])
                self.assertTrue(any('meter probe did not end before the quiet dwell' in r for r in refused['reasons']))
        # a probe that reports a non-integer end (or none that the arm can order) cannot satisfy the ordering
        bad = self.arm(s, s.build(), meter_probe=lambda root: {'live': True, 'probe_ended_ns': 'later'})
        self.assertFalse(bad['admitted'])

    def test_edited_status_swapped_commit_forged_rows_and_planted_desk_digest_all_refuse(self):
        # Opus packet review HIGH-1: each of these armed on the v4 head before the arm rebuilt the packet.
        s = self.scenario()
        s.quiet.update(active_work=['hashing'])
        s.finish()
        honest = s.build()
        self.assertFalse(self.arm(s, honest)['admitted'])
        edited = copy.deepcopy(honest)
        edited['checks']['quiet_start_state'] = {'status': 'pass', 'basis': 'quiet start verified'}
        refused = self.arm(s, edited)
        self.assertFalse(refused['admitted'])
        self.assertFalse(refused['next_arm_triage']['supplied_packet_matches_rebuild'])
        self.assertIn('quiet_start_state', ' '.join(refused['reasons']))          # judged on the arm's own build
        s2 = self.scenario().finish()
        good = s2.build()
        swapped = copy.deepcopy(good)
        swapped['record_commit'] = s2.code_commit                                     # an unrelated commit that exists
        self.assertFalse(self.arm(s2, swapped)['admitted'])
        forged = copy.deepcopy(good)
        forged['calibration_windows'] = [{'window': f'C{i}', 'status': 'final', 'captured_members': 14,
                                          'eligible_benign': {'spam': 7, 'bank': 7}} for i in range(1, 9)]
        forged['next_window_role'] = 'test'
        out = self.arm(s2, forged)
        self.assertFalse(out['admitted'])
        self.assertNotEqual(out['next_arm_triage']['calibration']['decision'], 'calibration_complete')
        planted = copy.deepcopy(good)
        planted['last_desk_passed_artifact_set_sha256'] = registration.artifact_set_digest(s2.root)
        s2.write(CODE_PATH, b'synthetic-code-v2\n')                                   # the code moved after the desk passed
        moved = self.arm(s2, planted)
        self.assertFalse(moved['admitted'])

    def test_stale_packet_expired_packet_and_missing_expiry_refuse(self):
        s = self.scenario().finish()
        packet = s.build()
        self.assertTrue(self.arm(s, packet)['admitted'])
        late = self.arm(s, packet, now=141.0)                  # past the quiet observation's max age
        self.assertFalse(late['admitted'])
        no_expiry = copy.deepcopy(packet)
        del no_expiry['valid_until_epoch_s']
        self.assertFalse(self.arm(s, no_expiry)['admitted'])   # the rebuild restores it, but the supplied one differs
        self.assertFalse(self.arm(s, no_expiry)['next_arm_triage']['supplied_packet_matches_rebuild'])

    def test_unrebuildable_packets_and_a_dead_meter_refuse(self):
        s = self.scenario().finish()
        for bad in (None, {}, {'record_commit': s.record_commit}, {**s.build(), 'series_path': 'nope.json'}):
            with self.subTest(bad=str(bad)[:40]):
                record = self.arm(s, bad)
                self.assertFalse(record['admitted'])
                self.assertIsNotNone(record['next_arm_triage']['rebuild_error'])
        dead = self.arm(s, s.build(), meter_probe=lambda root: {'live': False, 'reason': 'no samples'})
        self.assertFalse(dead['admitted'])
        self.assertIn('next_arm_triage: triage meter_reader_live failed', dead['reasons'])
        broken = self.arm(s, s.build(), meter_probe=lambda root: (_ for _ in ()).throw(OSError('usb')))
        self.assertFalse(broken['admitted'])

    def test_the_default_live_meter_probe_runs_the_monitor_and_parses_its_stream(self):
        from scripts import align_v4_session as session
        from tests.align.test_km003c import fake_stream
        with tempfile.TemporaryDirectory() as tmp:
            def runner(argv, **kwargs):
                fake_stream(Path(argv[argv.index('--out')+1]))
                return subprocess.CompletedProcess(argv, 0, b'', b'')
            result = session._probe_meter_live(tmp, runner=runner)
            self.assertTrue(result['live'], result)
            self.assertGreater(result['samples'], 0)
            def absent(argv, **kwargs):
                fake_stream(Path(argv[argv.index('--out')+1]), status='absent')
                return subprocess.CompletedProcess(argv, 0, b'', b'')
            self.assertFalse(session._probe_meter_live(tmp, runner=absent)['live'])
            self.assertFalse(session._probe_meter_live(tmp, runner=lambda argv, **k: subprocess.CompletedProcess(argv, 2, b'', b''))['live'])


class ArmOrderWitness(Base):
    """Lead ruling on R17 review open item 5: the full order of one real arm through _arm_and_install.

    Every subprocess, file write and disk_usage of the arm precedes the dwell stamp. After it come
    only the single dwell-record write (the stamp value) and the installer handoff. Recorded with a
    Python audit hook (subprocess.Popen, open-for-write, os.rename/replace/remove/mkdir) plus the
    host-observation seams, which stand for subprocesses on the MBP.
    """

    def test_every_subprocess_write_and_disk_usage_precedes_the_dwell_stamp(self):
        import shutil
        import sys
        from scripts import align_v4_session as session, align_v4_kit as kit
        from tests.align.test_v4_cadence import write_battery_log
        from scripts import align_v4_series as series
        s = self.scenario()
        seed_materializer(s)
        with patch.object(kit, 'r0_heatsink_key', return_value='T002'):
            series.generate(s.root, 'C1', extra_sentinels=2)
        plan = json.loads((s.root / series.kit_path('C1') / 'collection_plan.json').read_bytes())
        s.finish()
        packet = s.build()
        target = Path(tempfile.mkdtemp(dir=s.root.parent)) / 'session'
        target.mkdir()
        log = write_battery_log(target.parent / 'battery.jsonl', NOW)
        events, state = [], {'on': False}
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC

        def hook(event, args):
            if not state['on']:
                return
            if event == 'subprocess.Popen':
                events.append(('subprocess', ' '.join(map(str, args[1] or [args[0]]))[:60]))
            elif event == 'open' and len(args) >= 3:
                mode, flags = args[1], args[2]
                if (isinstance(mode, str) and any(c in mode for c in 'wxa+')) or (
                        mode is None and isinstance(flags, int) and flags & write_flags):
                    events.append(('write', str(args[0])))
            elif event in ('os.rename', 'os.replace', 'os.remove', 'os.mkdir', 'shutil.copyfile'):
                events.append(('write', f'{event}:{args[0]}'))
        sys.addaudithook(hook)
        def usage(path):
            events.append(('disk_usage', str(path)))

        def seam(name, value):
            def call(*_args, **_kwargs):
                events.append(('subprocess', 'seam:' + name))
                return value
            return call

        def disk_gate(config, gate=None):
            Path(log).read_bytes()                       # the gate's reads
            shutil.disk_usage(target)
            return {'status': 'pass'}

        def stamp():
            events.append(('DWELL', 'stamp'))
            return time.monotonic_ns()
        good = dict(passed=True, probe_error=False, external_connected=True, is_charging=False,
                    current_capacity_pct=100, instant_amperage_ma=0, update_age_s=1)
        arm_state = session_plan(target, {'v4_series': {'window_id': 'C1'}, 'source_measurement_root': str(s.root)},
                                 now=NOW)
        with patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(target.parent / 'host')}), \
             patch('joulewise.align.apple.powermode.admit_ac_powermode',
                   side_effect=seam('powermode', {'admitted': True, 'observed': 0})), \
             patch('joulewise.align.apple.external_volume.census', side_effect=seam('volumes', {})), \
             patch('joulewise.align.apple.external_volume.arm_check',
                   return_value={'verdict': 'PASS', 'reasons': []}), \
             patch('joulewise.battery_float.observe', side_effect=seam('battery', (good, b'synthetic'))), \
             patch.object(kit, 'arm_powermode_check', side_effect=seam('powermode_check', None)), \
             patch.object(session, 'w1_disk_check', side_effect=disk_gate), \
             patch('shutil.disk_usage', side_effect=usage), \
             patch.object(session.pilot, 'install', side_effect=seam('INSTALL', {'synthetic': True})):
            state['on'] = True
            try:
                session._arm_and_install(target, arm_state, s.root, plan, None,
                    watchdog_check=_watchdog_acceptance, runner=lambda argv: subprocess.CompletedProcess(argv, 0, '', ''), volume_runner=None,
                    now=lambda: NOW, w1_disk_config=None, disk_gate=None, battery_log=log,
                    obc_off_attested_by='synthetic', next_arm_triage=packet,
                    meter_probe=seam('meter_probe', {'live': True, 'samples': 40}), dwell_start=stamp)
            finally:
                state['on'] = False
        kinds = [kind for kind, _ in events]
        self.assertEqual(kinds.count('DWELL'), 1, events)
        cut = kinds.index('DWELL')
        before, after = events[:cut], events[cut + 1:]
        dwell_record = str(target / 'staging/v4-arm-001.dwell.json')
        # After the stamp: exactly the one dwell-record write, then the installer handoff; after the
        # installer returns, only that same dwell record is rewritten with installer_end_ns (lead ruling).
        def dwell_write(event):
            return event[0] == 'write' and dwell_record in event[1]
        install = after.index(('subprocess', 'seam:INSTALL'))
        self.assertEqual(after[:install], [('write', dwell_record)], after)
        self.assertTrue(after[install + 1:] and all(dwell_write(e) for e in after[install + 1:]), after)
        # Before it: the Git work, every host seam, the disk gate's disk_usage and every record write.
        self.assertTrue(any(k == 'subprocess' and 'git' in v for k, v in before), before)
        for name in ('powermode', 'volumes', 'battery', 'meter_probe', 'powermode_check'):
            self.assertIn(('subprocess', 'seam:' + name), before)
        self.assertIn(('disk_usage', str(target)), before)
        written = {v for k, v in before if k == 'write'}
        for name in ('staging/v4-arm-001.json', 'session.json', 'staging/w1_disk_gate.json'):
            # pilot.h.write publishes through a hidden temporary and a rename
            self.assertTrue(any(name.rsplit('/', 1)[-1] in v for v in written), (name, sorted(written)))
        dwell = json.loads(Path(dwell_record).read_bytes())
        self.assertTrue(dwell['admitted'])
        self.assertTrue(dwell['quiet_dwell']['meter_probe_before_dwell'])
        self.assertTrue(dwell['quiet_dwell']['record_checks_and_writes_before_dwell'])
        self.assertEqual(dwell['quiet_dwell']['installer_outcome'], 'returned')
        self.assertGreater(dwell['quiet_dwell']['installer_end_ns'], dwell['quiet_dwell']['start_ns'])
        record = json.loads((target / 'staging/v4-arm-001.json').read_bytes())
        self.assertIsNone(record['quiet_dwell']['start_ns'])
        self.assertEqual(record['quiet_dwell']['dwell_record'], dwell_record)


class R17ProvisionalTests(Base):
    """RUN_STATE 228 R17: provisional eligibility at the arm; window k final before the arm of k+2."""

    def series_of(self, specs):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17-')
        self.addCleanup(temp.cleanup)
        previous = Scenario(temp.name, 'W1').finish()
        for window, kwargs in specs:
            previous = Scenario(temp.name, window, previous=previous, **kwargs).finish()
        return previous

    def test_previous_window_arms_on_the_light_triage(self):
        s = self.series_of([('C1', {}), ('C2', {'provisional': True})])
        packet = s.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'provisional'])
        self.assertIn('R17 provisional', packet['checks']['member_eligibility']['basis'])
        self.assertEqual(packet['checks']['full_desk_gate']['status'], 'deferred')
        self.assertTrue(evaluate(s, packet)['admitted'])

    def test_window_k_must_be_final_before_the_arm_of_k_plus_2(self):
        stale = self.series_of([('C1', {'provisional': True}), ('C2', {})])
        packet = stale.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        bound = self.series_of([('C1', {'provisional': True}), ('C2', {'previous_final': True})])
        packet = bound.build()
        self.assertTrue(packet['packet_preflight']['ready'], packet['packet_preflight'])
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'final'])

    def test_final_counts_come_from_the_successor_and_may_only_be_lower(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17b-')
        self.addCleanup(temp.cleanup)
        w1 = Scenario(temp.name, 'W1').finish()
        c1 = Scenario(temp.name, 'C1', previous=w1, provisional=True)
        c1.sources['exclusions']['members_excluded'] = [{'run_id': c1.members[0]['run_id'], 'codes': ['clock.step']}]
        c1.thermal['members'][0]['excluded'] = True          # the harvest excluded one member
        c1.finish()
        c2 = Scenario(temp.name, 'C2', previous=c1, previous_final=True).finish()
        rows = c2.build()['calibration_windows']
        self.assertEqual(rows[0]['status'], 'final')
        self.assertEqual(sum(rows[0]['eligible_benign'].values()), 1)
        self.assertEqual(sum(c1.build()['calibration_windows'][0]['eligible_benign'].values()), 2)  # provisional

    def test_full_desk_due_refuses_the_provisional_adjudication(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17d-')
        self.addCleanup(temp.cleanup)
        w1 = Scenario(temp.name, 'W1').finish()
        w1.passed_ref = dict(w1.link)
        c1 = Scenario(temp.name, 'C1', previous=w1, provisional=True).finish()
        changed = c1.build(current='f' * 64)          # code/config moved since the last desk pass
        self.assertFalse(changed['packet_preflight']['ready'])
        self.assertIn('member_eligibility', ' '.join(changed['packet_preflight']['reasons']))
        provisional_w1 = Scenario(tempfile.mkdtemp(prefix='jw-triage-r17w-', dir=temp.name), 'W1')
        provisional_w1.provisional = True
        provisional_w1.previous = w1                  # only for its passed_ref; W1 always needs the full desk
        packet = provisional_w1.finish().build()
        self.assertFalse(packet['packet_preflight']['ready'])

    def test_previous_final_must_name_the_record_it_finalizes(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17e-')
        self.addCleanup(temp.cleanup)
        w1 = Scenario(temp.name, 'W1').finish()
        c1 = Scenario(temp.name, 'C1', previous=w1, provisional=True).finish()
        c2 = Scenario(temp.name, 'C2', previous=c1, previous_final=True).finish()
        record = copy.deepcopy(c2.record)
        record['previous_final']['record_sha256'] = '0' * 64
        index = c2.write(c2.record_path, record)
        c2.record_commit = c2.commit()
        c2.git('update-ref', 'refs/remotes/synthetic/records', c2.record_commit)
        c2.series['previous_record'] = {'commit': c2.record_commit, 'path': c2.record_path, 'sha256': index['sha256']}
        c2.write(c2.series_path, c2.series)
        c2.series_commit = c2.commit()
        packet = c2.build()
        self.assertFalse(packet['packet_preflight']['ready'])
        self.assertIn('previous_final must name this record', packet['calibration_error'])

    def test_schema_constants_match_the_light_triage_module(self):
        from joulewise.align.apple import light_triage
        self.assertEqual(builder.LIGHT_TRIAGE_SCHEMA, light_triage.SCHEMA)


class R17ReviewFinalityTests(Base):
    """R17 review (Sol seats 1 and 2): what counts as final, and the record-bound manifest."""

    def root(self):
        temp = tempfile.TemporaryDirectory(prefix='jw-triage-r17r-')
        self.addCleanup(temp.cleanup)
        return temp.name

    def test_constants_match_the_runner_and_the_offload_module(self):
        from joulewise.align.apple import harvest_offload
        from scripts import align_v4_harvest_off as runner
        self.assertEqual(builder.COMPLETED_HARVEST, runner.COMPLETED_HARVEST)
        self.assertEqual(builder.FINALIZED_MANIFEST_SCHEMA, harvest_offload.FINALIZED_SCHEMA)

    def light_with_stale_final_sources(self, root, w1):
        # F4: PILOT/exclusions present, desk still running off the MBP, honest light triage.
        c1 = Scenario(root, 'C1', previous=w1)
        light = copy.deepcopy(c1.thermal)
        for m in light['members']:
            m['excluded'] = bool(m['calibration_exclusions'])
        c1.sources['light_triage'] = {'schema': builder.LIGHT_TRIAGE_SCHEMA, 'window': 'C1', 'thermal': light,
            'checks': {'v4_B_bar': True}, 'km003c': c1.sources['pilot']['extra_checks']['km003c'],
            'series_desk_row': c1.sources['pilot']['extra_checks']['series_desk_row']}
        c1.sources['desk'] = {'plan_id': c1.sources['plan']['plan_id'], 'status': 'running_off_mbp'}
        c1.finish()
        c1.series['last_passed_record'] = dict(w1.passed_ref)
        c1.passed_ref = dict(w1.passed_ref)
        c1.write(c1.series_path, c1.series)
        c1.series_commit = c1.commit()
        return c1

    def test_stale_final_sources_with_a_running_desk_are_provisional_not_final(self):
        root = self.root()
        w1 = Scenario(root, 'W1').finish()
        c1 = self.light_with_stale_final_sources(root, w1)
        first = c1.build()
        self.assertEqual(first['calibration_windows'][-1]['status'], 'provisional')
        self.assertTrue(evaluate(c1, first)['admitted'])          # the one allowed unfinished window
        c2 = Scenario(root, 'C2', previous=c1).finish()
        packet = c2.build()
        self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
        self.assertIn('no completed harvest', packet['calibration_error'])
        self.assertFalse(evaluate(c2, packet)['admitted'])

    def test_a_completed_non_passing_desk_is_final(self):
        root = self.root()
        w1 = Scenario(root, 'W1').finish()
        c1 = Scenario(root, 'C1', previous=w1)
        c1.sources['pilot']['status'] = 'instrument_incomplete'
        c1.sources['desk'].update(pilot_status='instrument_incomplete', checks={'synthetic_check': False})
        c1.finish()
        c1.series['last_passed_record'] = dict(w1.passed_ref)
        c1.write(c1.series_path, c1.series)
        c1.series_commit = c1.commit()
        c2 = Scenario(root, 'C2', previous=c1).finish()
        packet = c2.build()
        self.assertNotIn('calibration_error', packet)
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'final'])

    def test_a_zero_capture_attempt_needs_no_harvest_to_be_final(self):
        root = self.root()
        w1 = Scenario(root, 'W1').finish()
        c1 = Scenario(root, 'C1', previous=w1, captured=False)
        c1.sources['desk']['harvest_status'] = 'not_run'        # nothing was captured, so nothing harvested
        c1.finish()
        c1.series['last_passed_record'] = dict(w1.passed_ref)
        c1.write(c1.series_path, c1.series)
        c1.series_commit = c1.commit()
        c2 = Scenario(root, 'C1#2', previous=c1).finish()
        packet = c2.build()
        self.assertNotIn('calibration_error', packet)
        self.assertNotEqual(packet['checks']['member_eligibility']['status'], 'fail')
        self.assertEqual([r['status'] for r in packet['calibration_windows']], ['final', 'final'])

    def test_previous_final_sources_must_evidence_a_completed_plan_bound_harvest(self):
        for label, change in (('running desk', lambda c: c.final_sources.__setitem__(
                                   'desk', {'plan_id': c.sources['plan']['plan_id'], 'status': 'running_off_mbp'})),
                              ('program fault', lambda c: c.final_sources['desk'].update(harvest_status='program_fault')),
                              ('other plan', lambda c: c.final_sources['desk'].update(plan_id='synthetic-other')),
                              ('other pilot', lambda c: c.final_sources['pilot'].update(plan_id='synthetic-other'))):
            with self.subTest(label):
                root = self.root()
                w1 = Scenario(root, 'W1').finish()
                c1 = Scenario(root, 'C1', previous=w1, provisional=True).finish()
                change(c1)
                c2 = Scenario(root, 'C2', previous=c1, previous_final=True).finish()
                packet = c2.build()
                self.assertIn('R17: final eligibility of C1', packet['calibration_error'])
                self.assertFalse(evaluate(c2, packet)['admitted'])

    def test_record_must_bind_a_canonical_finalized_manifest(self):
        root = self.root()
        w1 = Scenario(root, 'W1').finish()
        c1 = Scenario(root, 'C1', previous=w1)
        c1.omit_finalized_manifest = True
        c1.finish()
        with self.assertRaisesRegex(ValueError, 'must bind the finalized tree manifest'):
            c1.build()
        c1b = Scenario(self.root(), 'W1')
        c1b.omit_finalized_manifest = True
        c1b.record['finalized_manifest'] = c1b.write('w-W1/evidence/finalized_manifest.json', {
            'schema': builder.FINALIZED_MANIFEST_SCHEMA, 'source_root': '/x', 'entries': {}, 'closure': {}})
        c1b.finish()
        with self.assertRaisesRegex(ValueError, 'not a canonical'):
            c1b.build()


if __name__ == '__main__':
    unittest.main()
