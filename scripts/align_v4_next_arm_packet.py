#!/usr/bin/env python3
"""Build R12 next-arm evidence off the MBP, from explicit committed Git blobs.

See docs/align/next_arm_packet.md for the input inventory and authority map.
No filesystem discovery, hardware commands, harvest, scoring or network access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple import v4_cadence as cadence
from joulewise.align.apple.v4_estimands import FROZEN_D_SLOT_KEYS, d_configuration_assertion
from joulewise.arm_retry import terminal_window_release

RECORD_SCHEMA = 'joulewise.align_v4.window_record.v1'
SERIES_SCHEMA = 'joulewise.align_v4.series_state.v1'
SHA = re.compile(r'[0-9a-f]{64}\Z')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    def duplicate_guard(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('non-finite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=duplicate_guard, parse_constant=invalid)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def number(value):
    return type(value) in (float, int) and math.isfinite(value)


class GitEvidence:
    """Read named regular blobs only. Embedded absolute custody paths are text."""
    def __init__(self, repo):
        self.repo = Path(repo)
        self.inventory = {}
        self.accessed = []
        self._raw = {}
        self._commits = {}

    def git(self, *args):
        result = subprocess.run(['git', '--literal-pathspecs', '-C', str(self.repo), *args],
                                capture_output=True, check=False,
                                env={**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_OPTIONAL_LOCKS': '0'})
        require(result.returncode == 0, 'Git evidence unavailable: ' + ' '.join(args[:2]))
        return result.stdout

    def commit(self, revision):
        require(isinstance(revision, str) and bool(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', revision)),
                'commit must be a full object id')
        if revision not in self._commits:
            self._commits[revision] = self.git('rev-parse', '--verify', revision + '^{commit}').decode().strip()
        return self._commits[revision]

    def read(self, commit, path, expected=None):
        require(isinstance(path, str), 'source path missing')
        parts = PurePosixPath(path).parts
        require(parts and not path.startswith('/') and all(p not in ('.', '..', 'restricted',
                'night-custody', 'night-archive') and not p.startswith('jw-b5-') for p in parts),
                'source must be a safe repository-relative path')
        require(str(PurePosixPath(path)) == path, 'source path must be normalized')
        key = f'{commit}:{path}'
        if key not in self._raw:
            entry = self.git('ls-tree', '-z', commit, '--', path).split(b'\t', 1)[0].split()
            require(len(entry) == 3 and entry[0] in (b'100644', b'100755') and entry[1] == b'blob',
                    'source is not a committed regular blob: ' + path)
            self._raw[key] = self.git('show', key)
        raw = self._raw[key]
        actual = digest(raw)
        if expected is not None:
            require(isinstance(expected, str) and SHA.fullmatch(expected) and expected == actual,
                    'source SHA-256 mismatch: ' + path)
        self.inventory[key] = {'commit': commit, 'path': path, 'sha256': actual, 'bytes': len(raw)}
        self.accessed.append(key)
        return raw

    def source(self, commit, descriptor, *, json_value=True):
        require(isinstance(descriptor, dict) and set(descriptor) == {'path', 'sha256'},
                'source needs path and sha256')
        raw = self.read(commit, descriptor['path'], descriptor['sha256'])
        return decode(raw) if json_value else raw

    def raw_evidence(self, commit, record_path, descriptor):
        """Large raw captures stay in custody; their committed digest is evidence.

        Small exported raw blobs can also be checked byte-for-byte. Never open
        or stat a locator, even if it looks like a local absolute path.
        """
        if isinstance(descriptor, dict) and set(descriptor) == {'locator', 'sha256', 'bytes'}:
            require(isinstance(descriptor['locator'], str) and descriptor['locator'].strip()
                    and isinstance(descriptor['sha256'], str) and SHA.fullmatch(descriptor['sha256'])
                    and type(descriptor['bytes']) is int and descriptor['bytes'] >= 0,
                    'raw custody digest inventory malformed')
            key = f"raw:{commit}:{record_path}:{descriptor['locator']}"
            row = {'commit': commit, 'path': record_path, **descriptor,
                   'verification': 'committed_digest_inventory_only'}
            require(key not in self.inventory or self.inventory[key] == row, 'raw custody digest inventory disagrees')
            self.inventory[key] = row
            self.accessed.append(key)
            return descriptor['bytes']
        raw = self.source(commit, descriptor, json_value=False)
        require(bool(raw.strip()), 'empty captured evidence')
        return len(raw)


class WindowRecord:
    def __init__(self, evidence, commit, path):
        self.evidence, self.commit, self.path = evidence, evidence.commit(commit), path
        raw = evidence.read(self.commit, path)
        self.sha256 = digest(raw)
        self.record = decode(raw)
        require(self.record.get('schema') == RECORD_SCHEMA, 'wrong window record schema')
        require(isinstance(self.record.get('window'), str) and self.record['window'].strip(),
                'window record needs window')
        self.window = self.record['window']
        require(self.record.get('role') in ('development', 'calibration', 'test'), 'window record role missing')

    def source(self, name, *, json_value=True):
        return self.evidence.source(self.commit, self.record.get('sources', {}).get(name),
                                    json_value=json_value)

    def roster(self):
        members = self.source('collection_plan')['members']
        ids = [m['run_id'] for m in members]
        require(bool(ids) and len(ids) == len(set(ids)), 'collection roster missing or duplicate')
        return members

    def captures(self):
        ids = {m['run_id'] for m in self.roster()}
        captures = self.record.get('captures')
        require(isinstance(captures, dict) and set(captures) == ids,
                'capture inventory must cover every planned member (null means no capture)')
        found = set()
        for name, descriptor in captures.items():
            if descriptor is not None:
                size = self.evidence.raw_evidence(self.commit, self.path, descriptor)
                require(size > 0, 'empty captured evidence: ' + name)
                found.add(name)
        return found

    def verify_raw(self):
        rows = self.record.get('raw_evidence')
        require(isinstance(rows, list) and rows, 'raw evidence digest inventory missing')
        for descriptor in rows:
            self.evidence.raw_evidence(self.commit, self.path, descriptor)

    def thermal(self, *, validate_reports=True):
        pilot = self.source('pilot')
        thermal = pilot.get('extra_checks', {}).get('thermal', pilot)
        require(thermal.get('schema') == 'joulewise.align.thermal_desk.v1', 'thermal desk missing')
        members = thermal['members']
        require(len({m['id'] for m in members}) == len(members)
                and {m['id'] for m in members} == {m['run_id'] for m in self.roster()},
                'thermal desk must cover the exact planned roster')
        if not validate_reports:
            return thermal
        reports = thermal.get('model_windows')
        expected = {f"{m['model']}/{self.window}" for m in members if m.get('gated')}
        require(bool(expected) and isinstance(reports, dict) and set(reports) == expected,
                'U1-U5 must cover every gated model/window')
        for report in reports.values():
            require(all(isinstance(report.get(f'U{k}'), dict) and report[f'U{k}'].get('status')
                        in ('pass', 'fail', 'inconclusive') for k in range(1, 6)), 'U1-U5 unevaluated')
        return thermal

    def eligibility(self):
        thermal = self.thermal()
        exclusions = self.source('exclusions')
        require(isinstance(exclusions.get('members_excluded'), list), 'final exclusions missing')
        excluded = {r['run_id']: r['codes'] for r in exclusions['members_excluded']}
        require(set(excluded) <= {m['id'] for m in thermal['members']}, 'exclusions outside roster')
        require(len(excluded) == len(exclusions['members_excluded']), 'duplicate exclusions')
        counts = dict.fromkeys(cadence.CAL_PAIRS, 0)
        captured = self.captures()
        by_id = {m['id']: m for m in thermal['members']}
        # The desk's U3 pair rows do not carry member ids. Reconstruct the
        # registered comparisons from the same immutable roster tags instead.
        groups = {}
        for m in thermal['members']:
            if m.get('identical_work_group'):
                groups.setdefault((m.get('model'), m['identical_work_group']), []).append(m)
        comparisons = [(a, b) for group in groups.values() for i, a in enumerate(group) for b in group[i+1:]]
        for m in thermal['members']:
            if m.get('compare_reference_id'):
                require(m['compare_reference_id'] in by_id, 'U3 comparison reference missing')
                comparisons.append((m, by_id[m['compare_reference_id']]))
        divergent = {}
        for a, b in comparisons:
            if a.get('tokens') is not None and b.get('tokens') is not None and a['tokens'] != b['tokens']:
                divergent[a['model']] = divergent.get(a['model'], 0) + 1
        for model, count in divergent.items():
            pairs = thermal['model_windows'][f'{model}/{self.window}']['U3'].get('pairs', [])
            require(sum(p.get('status') == 'excluded' and p.get('exclusion') == 'X5'
                        and p.get('token_identical') is False for p in pairs) >= count,
                    'identity X5/U3 pair unresolved')
        for member, planned in zip(sorted(thermal['members'], key=lambda m: m['id']),
                                   sorted(self.roster(), key=lambda m: m['run_id'])):
            require(type(member.get('excluded')) is bool
                    and isinstance(member.get('calibration_exclusions'), list)
                    and isinstance(member.get('flags'), list), 'member eligibility unevaluated')
            codes = excluded.get(member['id'], [])
            require(isinstance(codes, list) and all(isinstance(c, str) and c for c in codes),
                    'exclusion codes malformed')
            require(member['excluded'] == bool(codes or member['calibration_exclusions']),
                    'desk and final exclusions disagree')
            if member['id'] not in captured:
                require(member['excluded'], 'uncaptured member cannot be eligible')
            if not member['excluded']:
                require(member.get('tokens') is not None and not any('identity_mismatch' in f
                        for f in member['flags']), 'identity X5 unresolved')
                require(not member['calibration_exclusions'], 'calibration exclusion unresolved')
                model_report = thermal['model_windows'].get(f"{member.get('model')}/{self.window}")
                pool_ok = model_report and all(model_report[f'U{k}']['status'] == 'pass' for k in (1, 2, 3))
                if pool_ok and planned.get('role') == 'D' and planned.get('condition') == 'benign':
                    require(planned.get('task_pair') in counts, 'unknown benign task pair')
                    counts[planned['task_pair']] += 1
        return {'window': self.window, 'status': 'final', 'captured_members': len(captured),
                'eligible_benign': counts}


def template():
    """Source templates have no asserted triage passes; placeholders refuse."""
    ref = {'path': 'REPLACE', 'sha256': 'REPLACE'}
    return {'record': {'schema': RECORD_SCHEMA, 'window': 'W1', 'finalized_at_epoch_s': None,
            'role': 'development', 'code_config': [dict(ref)],
            'sources': {n: dict(ref) for n in ('plan', 'collection_plan', 'result', 'chain_started',
                'chain_exited', 'courier', 'courier_sent', 'watchdog_state', 'pilot', 'desk', 'exclusions')},
            'captures': {'RUN_ID': None}, 'raw_evidence': [dict(ref)]},
        'series': {'schema': SERIES_SCHEMA, 'previous_record': {'commit': 'REPLACE', **ref},
            'prepared_at_epoch_s': None, 'quiet': dict(ref), 'meter_live': dict(ref),
            'quiet_requirements': {'cooldown_s': None, 'display_off_s': None, 'dwell_s': None,
                                   'max_age_s': None},
            'next_plan': dict(ref), 'last_passed_record': {'commit': 'REPLACE', **ref},
            'history': [], 'pool_members': [], 'sentinel_ids': [], 'escalations': []},
        'packet': {'schema': cadence.TRIAGE_SCHEMA,
            'checks': {r['id']: {'status': 'fail', 'basis': 'not built from authoritative sources'}
                       for r in cadence.NEXT_ARM_TRIAGE if r['source'] == cadence.PACKET},
            'arm_pending': [r['id'] for r in cadence.NEXT_ARM_TRIAGE if r['source'] == cadence.ARM]}}


def build_packet(repo, *, record_commit, record_path, series_commit, series_path, pushed_ref):
    evidence = GitEvidence(repo)
    previous = WindowRecord(evidence, record_commit, record_path)
    series_commit = evidence.commit(series_commit)
    series_raw = evidence.read(series_commit, series_path)
    series = decode(series_raw)
    require(series.get('schema') == SERIES_SCHEMA, 'wrong series state schema')
    require(series.get('previous_record') == {'commit': previous.commit, 'path': record_path,
                                            'sha256': previous.sha256}, 'series previous record binding mismatch')
    packet = {'schema': cadence.TRIAGE_SCHEMA, 'record_commit': previous.commit,
        'record_path': record_path, 'record_sha256': previous.sha256,
        'series_commit': series_commit, 'series_path': series_path, 'series_sha256': digest(series_raw),
        'previous_window': previous.window, 'previous_window_is_w1': previous.window == 'W1',
        'code_or_config_changed': True, 'next_window_role': None, 'calibration_windows': [],
        'checks': {}, 'arm_pending': [r['id'] for r in cadence.NEXT_ARM_TRIAGE if r['source'] == cadence.ARM],
        'entry_sources': {r['id']: r['source'] for r in cadence.NEXT_ARM_TRIAGE}}

    def source(name):
        return evidence.source(series_commit, series.get(name))

    def check(name, action):
        before = len(evidence.accessed)
        try:
            details = action()
            status = details.pop('status', 'pass')
            basis = details.pop('basis')
        except (ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
            status, basis, details = 'fail', str(exc), {}
        packet['checks'][name] = {'status': status, 'basis': basis or name + ' unavailable',
                                  **details, 'sources': sorted(set(evidence.accessed[before:]))}

    def committed():
        finalized = previous.record.get('finalized_at_epoch_s')
        require(number(finalized), 'record finalization missing')
        ended = previous.source('result').get('ended_epoch_s')
        require(number(ended) and number(series.get('prepared_at_epoch_s'))
                and ended <= finalized <= series['prepared_at_epoch_s'], 'record finalization out of order')
        require(isinstance(pushed_ref, str) and pushed_ref.startswith('refs/remotes/'),
                'push proof needs an explicit local remote-tracking ref')
        tip = evidence.git('rev-parse', '--verify', pushed_ref + '^{commit}').decode().strip()
        evidence.git('merge-base', '--is-ancestor', previous.commit, tip)
        previous.verify_raw()
        # Authenticate every named source, including sources used by later checks.
        for descriptor in previous.record.get('sources', {}).values():
            if descriptor is not None:
                evidence.source(previous.commit, descriptor, json_value=False)
        previous.captures()
        return {'basis': 'finalized record and raw digests verified; commit reachable from ' + pushed_ref,
                'pushed_ref': pushed_ref, 'pushed_tip': tip}

    def terminal():
        plan, result = previous.source('plan'), previous.source('result')
        require(result.get('schema') == 'joulewise.unattended_night_result.v1', 'terminal result schema missing')
        names = previous.record['sources']
        started, exited = names.get('chain_started') is not None, names.get('chain_exited') is not None
        courier = previous.source('courier')
        previous.source('courier_sent', json_value=False)  # native courier creates an empty marker with touch
        require(courier.get('sent') is True, 'courier delivery missing')
        now = series.get('prepared_at_epoch_s')
        require(number(now), 'series preparation time missing')
        decision = terminal_window_release(result, plan_id=plan['plan_id'], receipt_class=plan['receipt_class'],
                    now_epoch_s=now, chain_started=started, chain_exited=exited, courier_sent=True)
        require(decision.allowed, decision.reason)
        if exited:
            require(previous.source('chain_exited').get('exit_code') == result.get('chain_exit_code'),
                    'chain closure and terminal result disagree')
        key = f"{plan['plan_id']}:{plan['custody_root']}:{digest(evidence.source(previous.commit, names['result'], json_value=False))}"
        latch = previous.source('watchdog_state').get('released_terminal_windows', [])
        require(isinstance(latch, list) and key in latch,
                'watchdog empty-process terminal latch missing or for another result')
        captured = previous.captures()
        require(started or not captured, 'null window carries captured members')
        return {'basis': 'B1 authenticated terminal result, chain closure, delivery and watchdog latch',
                'release_kind': decision.reason}

    def quiet():
        observed, policy = source('quiet'), series['quiet_requirements']
        result = previous.source('result')
        for name in ('cooldown_s', 'display_off_s', 'dwell_s', 'max_age_s'):
            require(number(policy.get(name)) and policy[name] > 0, 'quiet policy missing: ' + name)
        for name in ('cooldown_s', 'display_off_s', 'dwell_s'):
            require(number(observed.get(name)) and observed[name] >= policy[name], 'quiet start short: ' + name)
        require(number(observed.get('observed_at_epoch_s')) and number(result.get('ended_epoch_s'))
                and result['ended_epoch_s'] <= observed['observed_at_epoch_s'] <= series['prepared_at_epoch_s']
                and series['prepared_at_epoch_s'] - observed['observed_at_epoch_s'] <= policy['max_age_s'],
                'quiet start evidence stale or predates terminal completion')
        require(observed.get('active_work') == [], 'desk, hashing or evidence traffic remains on MBP')
        return {'basis': 'post-terminal quiet observation meets frozen cooldown, display-off and dwell policy',
                'valid_until_epoch_s': observed['observed_at_epoch_s'] + policy['max_age_s']}

    def meter():
        pilot = previous.source('pilot')
        report = pilot.get('extra_checks', {}).get('km003c', pilot.get('km003c'))
        require(isinstance(report, dict) and isinstance(report.get('members'), dict), 'meter tabulation missing')
        require(set(report['members']) == {m['run_id'] for m in previous.roster()}, 'meter tabulation roster mismatch')
        gaps = {}
        for rid, row in report['members'].items():
            require(row.get('status') in ('available', 'missing') and isinstance(row.get('flags'), list),
                    'meter coverage unevaluated: ' + rid)
            if row['status'] == 'missing':
                gaps[rid] = row['flags']
        live = source('meter_live')
        require(type(live.get('sample_count')) is int and live['sample_count'] > 0
                and number(live.get('raw_offset_ns')), 'meter not verified live before next arm')
        require(number(live.get('observed_at_epoch_s'))
                and previous.source('result')['ended_epoch_s'] <= live['observed_at_epoch_s'] <= series['prepared_at_epoch_s']
                and series['prepared_at_epoch_s'] - live['observed_at_epoch_s'] <= series['quiet_requirements']['max_age_s'],
                'live meter evidence stale')
        return {'basis': 'SECONDARY coverage tabulated (gaps non-gating); live samples and clock verified',
                'gaps': gaps, 'powermetrics_admissibility_unchanged': True,
                'valid_until_epoch_s': live['observed_at_epoch_s'] + series['quiet_requirements']['max_age_s']}

    def faults():
        rows = previous.thermal(validate_reports=False)['members']
        require(all(isinstance(m.get('flags'), list) and isinstance(m.get('coverage'), list)
                    and isinstance(m.get('calibration_exclusions'), list)
                    and (m['flags'] or m['calibration_exclusions']
                         or (number(m.get('pm_period_s')) and number(m.get('pm_max_gap_s')))) for m in rows),
                'capture coverage or X1-X8 tabulation missing')
        return {'basis': 'sidecar/powermetrics coverage and X1-X8 faults tabulated; faults retained as exclusions',
                'members': {m['id']: {k: m.get(k) for k in ('flags', 'coverage', 'calibration_exclusions',
                    'pm_period_s', 'pm_max_gap_s', 'turn_observation')} for m in rows}}

    def next_plan():
        plan = source('next_plan')
        first = previous.window == 'R1' and plan.get('window') == 'W1' and plan.get('role') == 'development'
        require(first or plan.get('role') in ('calibration', 'test'), 'next plan role missing')
        packet['next_window_role'] = None if first else plan['role']
        last_ref = series.get('last_passed_record')
        require(isinstance(last_ref, dict), 'last desk-passed record missing')
        last_record = WindowRecord(evidence, last_ref['commit'], last_ref['path'])
        require(last_record.sha256 == last_ref.get('sha256'), 'last desk-passed record digest mismatch')
        last = last_record.source('desk')
        require(last.get('pilot_status') == 'instrument_ok' and isinstance(last.get('checks'), dict)
                and last['checks'] and all(v is True for v in last['checks'].values())
                and last.get('harvest_status') == 'ok',
                'last desk-passed state has no passing desk')
        packet['code_or_config_changed'] = state_digest(series_commit, plan) != state_digest(last_record.commit, last_record.record)
        return plan

    def state_digest(commit, owner):
        commit = evidence.commit(owner.get('code_config_commit', commit))
        entries = owner.get('code_config')
        require(isinstance(entries, list) and entries, 'code/config source inventory missing')
        paths = [r['path'] for r in entries]
        require(len(paths) == len(set(paths)), 'duplicate code/config source')
        for row in entries:
            evidence.source(commit, row, json_value=False)
        return digest(json.dumps(sorted((r['path'], r['sha256']) for r in entries),
                                 separators=(',', ':')).encode())

    def thermal():
        reports = previous.thermal()['model_windows']
        failed = [model for model, r in reports.items() if any(r[f'U{k}']['status'] != 'pass' for k in (1, 2, 3))]
        if not failed:
            return {'basis': 'U1-U3 pass; no escalation required'}
        plan = next_plan()
        prior = previous.source('collection_plan')['thermal_policy']
        after = plan['thermal_policy']
        steps = series.get('escalations', [])
        require(any(r.get('window') == previous.window and r.get('next_plan_sha256') == series['next_plan']['sha256']
                    and isinstance(r.get('ruling_id'), str) and r['ruling_id'].strip() for r in steps),
                'U1-U3 failure needs prospective recorded escalation')
        idle = (prior.get('idle_s') == 300 and after.get('idle_s') == 450
                and prior.get('delta_slow_c') == after.get('delta_slow_c')
                and prior.get('quantization_bits') == after.get('quantization_bits'))
        timeout = any(r['U1'].get('g1_h_timeouts', 0) > 0 or r['U1'].get('g0_timeouts', 0) > 0
                      for r in reports.values())
        spread = any(r['U2']['status'] == 'fail' for r in reports.values())
        delta = (prior.get('idle_s') == after.get('idle_s') == 450
                 and number(prior.get('delta_slow_c')) and number(after.get('delta_slow_c'))
                 and ((timeout and after['delta_slow_c'] - prior['delta_slow_c'] == .5)
                      or (spread and prior['delta_slow_c'] - after['delta_slow_c'] == .5))
                 and prior.get('quantization_bits') == after.get('quantization_bits')
                 and 0 < after['delta_slow_c'] <= 2)
        quant = (prior.get('idle_s') == after.get('idle_s') == 450
                 and prior.get('delta_slow_c') == after.get('delta_slow_c')
                 and prior.get('quantization_bits') == 8 and after.get('quantization_bits') == 4)
        require(idle or delta or quant, 'registered idle/delta/one-step quantization ladder not applied')
        return {'basis': 'U1-U3 consequence recorded before next plan; registered ladder applied', 'failed': failed}

    def cohort():
        table = previous.thermal()
        members = [m for m in table['members'] if m.get('role') == 'D']
        require(d_configuration_assertion(members)['instrument_ok'], 'previous D four-slot cohort or identity inconsistent')
        pool = series.get('pool_members')
        require(isinstance(pool, list) and len(pool) == len(set(pool)), 'pool roster missing or duplicated')
        ids = {m['id'] for m in members}
        require(set(pool) <= ids, 'pool members outside previous D roster')
        if any(r[f'U{k}']['status'] != 'pass' for r in table['model_windows'].values() for k in (1, 2, 3)):
            require(not pool, 'U1-U3 failure bars pool entry')
        eligible = previous.eligibility()
        excluded = {m['id'] for m in members if m['excluded']}
        require(not (set(pool) & excluded), 'excluded member entered pool')
        if pool:
            config = next_plan()['configuration']
            require(all(all(m['configuration'].get(k) == config.get(k) for k in FROZEN_D_SLOT_KEYS)
                        and m['cohort_identity'] == config.get('cohort_identity') for m in members if m['id'] in pool),
                    'pool crosses a changed configuration or identity')
        return {'basis': 'one frozen four-slot cohort; failed/excluded members barred and no configuration mixing',
                'eligible_benign': eligible['eligible_benign']}

    def sentinels():
        reports = previous.thermal()['model_windows']
        needed = 4 if any(r[f'U{k}']['status'] == 'inconclusive' for r in reports.values() for k in (4, 5)) else 2
        planned = [m['run_id'] for m in next_plan()['members'] if m.get('role') == 'sentinel']
        frozen = series.get('sentinel_ids')
        require(isinstance(frozen, list) and len(frozen) == len(set(frozen)) and len(frozen) >= needed
                and planned == frozen, 'next frozen roster must include two extra sentinels after U4/U5 inconclusive')
        return {'basis': 'next sentinel roster recorded with U4/U5 consequence', 'sentinel_ids': planned}

    def eligibility():
        return {'basis': 'final desk eligibility, identity X5, U3 pair exclusions and capture inventory reconciled',
                'counts': previous.eligibility()}

    def full_desk():
        desk = previous.source('desk')
        checks = desk.get('checks')
        passing = (desk.get('pilot_status') == 'instrument_ok' and isinstance(checks, dict) and checks
                   and all(v is True for v in checks.values()) and desk.get('harvest_status') == 'ok')
        require(passing or desk.get('status') == 'running_off_mbp',
                'full desk must complete and pass after W1 or a code/config change')
        next_plan()
        required = packet['previous_window_is_w1'] or packet['code_or_config_changed']
        if desk.get('status') == 'running_off_mbp' and not required:
            return {'status': 'deferred', 'basis': 'unchanged later window; full desk running off MBP'}
        require(desk.get('plan_id') == previous.source('plan')['plan_id'], 'full desk plan mismatch')
        require(passing,
                'full desk must complete and pass after W1 or a code/config change')
        require(state_digest(previous.commit, previous.record) == state_digest(series_commit, source('next_plan')),
                'full desk does not cover next code/config state')
        return {'basis': 'full desk completed and passing for next code/config state'}

    for name, action in (('record_committed', committed), ('terminal_completion', terminal),
                         ('quiet_start_state', quiet), ('meter_samples_clock', meter), ('capture_faults', faults)):
        check(name, action)
    for name, action in (('thermal_escalation', thermal), ('cohort_pool_rules', cohort),
                         ('sentinel_roster', sentinels), ('member_eligibility', eligibility)):
        if previous.window == 'R1':
            packet['checks'][name] = {'status': 'not_applicable', 'basis': 'previous window is R1'}
        else:
            check(name, action)
    check('full_desk_gate', full_desk)
    history_error = None
    try:
        require(isinstance(series.get('history'), list), 'series history missing')
        seen = set()
        last_commit = None
        for row in series['history']:
            if row.get('type') == 'lead_ruling':
                packet['calibration_windows'].append(dict(row))
                continue
            record = WindowRecord(evidence, row['record_commit'], row['record_path'])
            require(record.record.get('role') == 'calibration', 'history contains a non-calibration window')
            evidence.git('merge-base', '--is-ancestor', record.commit, previous.commit)
            if last_commit:
                evidence.git('merge-base', '--is-ancestor', last_commit, record.commit)
            last_commit = record.commit
            record.verify_raw()
            require(record.window not in seen, 'duplicate window in series history')
            seen.add(record.window)
            packet['calibration_windows'].append(record.eligibility())
        if previous.window != 'R1' and previous.record.get('role') == 'calibration':
            attempts = [r for r in series['history'] if r.get('type') != 'lead_ruling']
            require(attempts and attempts[-1].get('record_commit') == previous.commit
                    and attempts[-1].get('record_path') == previous.path, 'previous calibration record missing from history tail')
        packet['calibration_decision'] = cadence.calibration_stop(packet['calibration_windows'])
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        history_error = str(exc)
        packet['calibration_windows'] = [{}]  # cannot silently truncate or take R1's N/A shortcut
        packet['calibration_error'] = history_error
    # ARM booleans are deliberately absent from the packet. This evaluation
    # assumes them only to isolate packet readiness; it is never arm authority.
    expiries = [packet['checks'][k].get('valid_until_epoch_s') for k in ('quiet_start_state', 'meter_samples_clock')]
    if all(number(t) for t in expiries):
        packet['valid_until_epoch_s'] = min(expiries)
    evaluation = cadence.next_arm_triage(packet, {name: True for name in packet['arm_pending']},
                                        now_epoch_s=series.get('prepared_at_epoch_s'))
    if history_error:
        evaluation['admitted'] = False
        evaluation['reasons'].append('calibration history: ' + history_error)
    packet['packet_preflight'] = {'ready': evaluation['admitted'], 'reasons': evaluation['reasons'],
                                   'arm_checks_still_required': packet['arm_pending']}
    packet['evidence'] = sorted(evidence.inventory.values(), key=lambda r: (r['commit'], r['path']))
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-triage-template', action='store_true')
    parser.add_argument('--repo', type=Path, default=ROOT)
    for flag in ('record-commit', 'record-path', 'series-commit', 'series-path', 'pushed-ref'):
        parser.add_argument('--' + flag)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if args.emit_triage_template:
        value, code = template(), 0
    else:
        names = ('record_commit', 'record_path', 'series_commit', 'series_path', 'pushed_ref')
        if any(getattr(args, name) is None for name in names):
            parser.error('record/series commits and paths and --pushed-ref are required')
        try:
            value = build_packet(args.repo, **{name: getattr(args, name) for name in names})
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            print('next-arm packet refused: ' + str(exc), file=sys.stderr)
            return 2
        code = 0 if value['packet_preflight']['ready'] else 2
    raw = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    if args.output:
        with args.output.open('x') as stream:
            stream.write(raw)
    else:
        print(raw, end='')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
