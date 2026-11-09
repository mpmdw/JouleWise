#!/usr/bin/env python3
"""Build R12 next-arm evidence from explicit committed Git blobs.

The packet is a pointer, never trusted data (lead ruling 2026-11-08): the ARM calls
``build_packet`` itself from the identities the supplied packet names (record commit and
path, series commit and path, pushed ref), with its own clock and its own artifact-set
digest, and uses its own build; a supplied packet that differs (other than ``pushed_tip``
and ``packet_preflight``) refuses. See docs/align/next_arm_packet.md.
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
from joulewise.align.apple import v4_registration as registration
from joulewise.align.apple.v4_estimands import FROZEN_D_SLOT_KEYS, d_configuration_assertion
from joulewise.arm_retry import terminal_window_release

RECORD_SCHEMA = 'joulewise.align_v4.window_record.v1'
SERIES_SCHEMA = 'joulewise.align_v4.series_state.v1'
SHA = re.compile(r'[0-9a-f]{64}\Z')
ATTEMPT = re.compile(r'^([CTD])([1-9][0-9]*)(?:#([1-9][0-9]*))?$')
IGNORED_FOR_EQUALITY = ('pushed_tip', 'packet_preflight')    # top level; also checks.record_committed.pushed_tip (canonical)
IDENTITY_FIELDS = ('record_commit', 'record_path', 'series_commit', 'series_path', 'pushed_ref')
# The series ledger is ONE canonical append-only file, rewritten by each window's commit. Its latest
# committed version names the latest window record (delta3 G1), so an older packet cannot stay current.
SERIES_PATH = 'series/state.json'
# The frozen series names its two task pairs in full; the count-only predicate keys them spam/bank.
PAIR_NAMES = {'spam': cadence.CAL_PAIRS[0], 'bank': cadence.CAL_PAIRS[1],
              'spam_filter_update': cadence.CAL_PAIRS[0], 'bank_transfer_2': cadence.CAL_PAIRS[1]}
MANIFEST_PATH = 'configs/campaigns/align_v4/series/series_manifest.json'   # the frozen D/C/T series (R15)
FULL_DESK_GATE_EXEMPT = ('v4_B_bar',)     # = align_v4_session.FULL_DESK_GATE_EXEMPT (tested equal)


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
        require(bool(cadence.WINDOW_ID.match(self.window)), 'window id is not a registered id: ' + self.window)
        require(self.record.get('role') in ('development', 'calibration', 'test'), 'window record role missing')
        link = self.record.get('previous_record')
        require(link is None or (isinstance(link, dict) and set(link) == {'commit', 'path', 'sha256'}),
                'previous_record must be null (first record) or {commit, path, sha256}')
        self.previous_link = link

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

    def counted_captures(self):
        """Captured members that count: every capture is authenticated, supplemental (R20) ones excluded."""
        supplemental = {m['run_id'] for m in self.roster() if m.get('supplemental')}
        return len(self.captures() - supplemental)

    def structural_bar(self, captured):
        """R22-2: the STRUCTURAL reason (never a score or a count) that bars a captured calibration window.

        ``u1_u3_fail``: the desk's U1-U3 verdict FAILed for a gated model; ``whole_window_capture_failure``:
        the committed terminal result is not a completed GO chain. A zero-capture refusal is not barred
        here: it is barred by its retry (see ``attempts``).
        """
        if not captured:
            return None
        reports = self.thermal()['model_windows']
        if any(r[f'U{k}']['status'] == 'fail' for r in reports.values() for k in (1, 2, 3)):
            return 'u1_u3_fail'
        result = self.source('result')
        if result.get('verdict') != 'GO' or result.get('chain_exit_code') != 0:
            return 'whole_window_capture_failure'
        return None

    def desk_ceiling(self):
        """The desk's committed provisional eligible counts for this calibration window (an upper bound)."""
        pilot = self.source('pilot')
        row = (pilot.get('extra_checks') or {}).get('series_desk_row')
        require(isinstance(row, dict) and row.get('window_id') == self.window.split('#')[0]
                and isinstance(row.get('desk_eligible_benign'), dict)
                and set(row['desk_eligible_benign']) == set(cadence.CAL_PAIRS)
                and all(type(v) is int and v >= 0 for v in row['desk_eligible_benign'].values()),
                'committed desk provisional counts (series_desk_row) missing or malformed for ' + self.window)
        return dict(row['desk_eligible_benign'])

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
        # R22-1: contention is disclosure-only, so a contention code can never exclude a member here either.
        from joulewise.align.apple import v4_contention
        excluded = {r['run_id']: v4_contention.split_codes(r['codes'])[0] for r in exclusions['members_excluded']}
        require(set(excluded) <= {m['id'] for m in thermal['members']}, 'exclusions outside roster')
        require(len(excluded) == len(exclusions['members_excluded']), 'duplicate exclusions')
        counts = dict.fromkeys(cadence.CAL_PAIRS, 0)
        captured = self.captures()           # every capture is authenticated, supplemental ones included
        # R20: supplemental diagnostics (ordinals 23/24) count toward nothing, not even captured_members.
        supplemental = {m['run_id'] for m in self.roster() if m.get('supplemental')}
        counted = captured - supplemental
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
            desk_codes = v4_contention.split_codes(member['calibration_exclusions'])[0]
            require(member['excluded'] == bool(codes or desk_codes), 'desk and final exclusions disagree')
            if member['id'] not in captured:
                require(member['excluded'], 'uncaptured member cannot be eligible')
            if not member['excluded']:
                require(member.get('tokens') is not None and not any('identity_mismatch' in f
                        for f in member['flags']), 'identity X5 unresolved')
                require(not desk_codes, 'calibration exclusion unresolved')
                model_report = thermal['model_windows'].get(f"{member.get('model')}/{self.window}")
                pool_ok = model_report and all(model_report[f'U{k}']['status'] == 'pass' for k in (1, 2, 3))
                # Only the frozen CALIBRATION pool counts: ordinary and supplemental sentinels, anchors,
                # known-H and test members never enter m. A roster without pool metadata (the W1 kit)
                # keeps the older benign-D reading.
                in_pool = (planned.get('pool_role') == 'calibration' if 'pool_role' in planned
                           else True)
                if (pool_ok and in_pool and not planned.get('supplemental') and planned.get('role') == 'D'
                        and planned.get('condition') == 'benign'):
                    pair = PAIR_NAMES.get(planned.get('task_pair'))
                    require(pair in counts, 'unknown benign task pair')
                    counts[pair] += 1
        return {'window': self.window, 'status': 'final', 'captured_members': len(counted),
                'eligible_benign': counts}


def template():
    """Source templates have no asserted triage passes; placeholders refuse."""
    ref = {'path': 'REPLACE', 'sha256': 'REPLACE'}
    return {'record': {'schema': RECORD_SCHEMA, 'window': 'W1', 'finalized_at_epoch_s': None,
            'role': 'development', 'previous_record': None, 'code_commit': 'REPLACE',
            'sources': {n: dict(ref) for n in ('plan', 'collection_plan', 'result', 'chain_started',
                'chain_exited', 'courier', 'courier_sent', 'watchdog_state', 'pilot', 'desk', 'exclusions')},
            'captures': {'RUN_ID': None}, 'raw_evidence': [dict(ref)]},
        'series': {'schema': SERIES_SCHEMA, 'previous_record': {'commit': 'REPLACE', **ref},
            'quiet': dict(ref),
            'quiet_requirements': {'cooldown_s': None, 'display_off_s': None, 'dwell_s': None,
                                   'max_age_s': None},
            'next_plan': dict(ref), 'last_passed_record': {'commit': 'REPLACE', **ref},
            'lead_rulings': [{'ruling_id': 'REPLACE', 'after_window': 'C1',
                              'text': dict(ref), 'lead_signature': 'REPLACE'}],
            'pool_members': [], 'sentinel_ids': [], 'escalations': []},
        'packet': {'schema': cadence.TRIAGE_SCHEMA,
            'checks': {r['id']: {'status': 'fail', 'basis': 'not built from authoritative sources'}
                       for r in cadence.NEXT_ARM_TRIAGE if r['source'] == cadence.PACKET},
            'arm_pending': [r['id'] for r in cadence.NEXT_ARM_TRIAGE if r['source'] == cadence.ARM]}}


def identities(packet):
    """The five identities a supplied packet names; the arm rebuilds from exactly these."""
    require(isinstance(packet, dict), 'packet is not an object')
    found = {name: packet.get(name) for name in IDENTITY_FIELDS}
    require(all(isinstance(v, str) and v for v in found.values()), 'packet does not name its record/series identities')
    return found


def canonical(packet):
    """The packet without the fields the arm ignores when comparing a supplied packet with its own build."""
    kept = {k: v for k, v in packet.items() if k not in IGNORED_FOR_EQUALITY}
    # The builder emits the informational pushed tip inside the record_committed check; that exact field is
    # the same volatile pointer as the top-level one (delta4 S1 L1 / S2 F3). Reachability from the named
    # remote-tracking ref is still re-proved by the rebuild itself.
    checks = kept.get('checks')
    entry = checks.get('record_committed') if isinstance(checks, dict) else None
    if isinstance(entry, dict) and 'pushed_tip' in entry:
        kept = {**kept, 'checks': {**checks, 'record_committed': {k: v for k, v in entry.items() if k != 'pushed_tip'}}}
    return json.dumps(kept, sort_keys=True, separators=(',', ':'), allow_nan=False)


def rebuild_and_compare(repo, supplied, *, now_epoch_s, current_artifact_set_sha256):
    """The arm's own build from the supplied packet's identities, and whether the supplied packet equals it."""
    built = build_packet(repo, **identities(supplied), now_epoch_s=now_epoch_s,
                         current_artifact_set_sha256=current_artifact_set_sha256)
    return built, canonical(supplied) == canonical(built)


def committed_artifact_set_digest(evidence, commit):
    """``v4_registration.artifact_set_digest`` computed from the committed bytes at ``commit``."""
    return registration.artifact_set_digest_at(evidence.repo, commit)


def attempts(chain):
    """The counted-order check over a chain of calibration attempts (oldest first).

    ``chain``: ``(record, captured_members, barred)`` triples. Frozen order is unchanged: slots are C1..C8,
    then (R22-2 / R24) the replacement windows C9-C14 only while fewer than 8 windows are counted. A
    zero-capture attempt keeps its window id with an attempt suffix (``C3`` then ``C3#2``); a slot whose
    retry is also a zero capture is barred. A barred slot is not counted and owes a replacement. An
    omitted attempt breaks the sequence.
    """
    primary = [f'C{n}' for n in range(1, cadence.CAL_WINDOWS+1)]
    replacements = [f'C{n}' for n in range(cadence.CAL_WINDOWS+1, cadence.CAL_WINDOWS+cadence.REPLACEMENT_WINDOWS+1)]
    consumed, zeros = {}, {}

    def next_slot():
        for slot in primary:
            if slot not in consumed:
                return slot
        if sum(v == 'counted' for v in consumed.values()) < cadence.CAL_WINDOWS:
            for slot in replacements:
                if slot not in consumed:
                    return slot
        return None

    for record, captured, barred in chain:
        match = ATTEMPT.match(record.window)
        require(match and match.group(1) == 'C', 'calibration chain contains a non-calibration id: ' + record.window)
        slot, attempt = f'C{int(match.group(2))}', int(match.group(3) or 1)
        expected = next_slot()
        require(slot == expected and attempt == zeros.get(slot, 0) + 1,
                f'calibration attempts out of order or omitted: expected {expected}'
                + ('' if zeros.get(slot, 0) == 0 else f'#{zeros[slot] + 1}') + f', found {record.window}')
        if captured > 0:
            consumed[slot] = 'barred' if barred else 'counted'
        else:
            zeros[slot] = zeros.get(slot, 0) + 1
            if zeros[slot] >= 2:
                consumed[slot] = 'barred'


def _exclusion_map(entries):
    """run id -> sorted distinct codes, or None when the entries are not a well-formed list."""
    if not isinstance(entries, list):
        return None
    out = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('run_id'), str) or not isinstance(entry.get('codes'), list):
            return None
        out[entry['run_id']] = sorted(set(out.get(entry['run_id'], [])) | {str(c) for c in entry['codes']})
    return out


def effective_desk(desk, exclusions):
    """The native desk with disclosure-only (contention) exclusions neutralized (R22-1), or a refusal.

    A desk written before the exclusion policy (or by a common desk that still listed a contention-only
    member) reports ``harvest_status: members_excluded`` and fails the exclusion-derived checks. It may be
    neutralized ONLY when the committed harvest exclusions hold nothing but disclosure-only codes AND the desk's
    own record of exclusions (``members_excluded`` plus the new desk's ``members_disclosure_only``) is the SAME
    set: same members, same codes. A desk/harvest mismatch (a stale desk recording a real exclusion, or naming
    another member or other codes) is an inconsistent window record and REFUSES; it never passes. A harvest with
    any real exclusion leaves the desk's own verdict untouched.
    """
    from joulewise.align.apple import v4_contention
    if not isinstance(desk, dict) or not isinstance(exclusions, dict) or not isinstance(exclusions.get('members_excluded'), list):
        return desk
    harvest = _exclusion_map(exclusions['members_excluded'])
    if not harvest or any(v4_contention.split_codes(codes)[0] or not codes for codes in harvest.values()):
        return desk                                     # nothing excluded, or a real/unknown exclusion: the desk's verdict stands
    own = _exclusion_map(desk.get('members_excluded') if 'members_excluded' in desk else [])
    disclosed = desk.get('members_disclosure_only')
    if own is not None and isinstance(disclosed, dict):
        for run_id, codes in disclosed.items():
            own[run_id] = sorted(set(own.get(run_id, [])) | {str(c) for c in (codes if isinstance(codes, list) else [])})
    require(own == harvest, 'desk and committed harvest exclusions disagree (inconsistent window record): '
            f'desk {own!r} vs harvest {harvest!r}')
    checks = dict(desk.get('checks') or {})
    for key in ('no_member_exclusions', 'chain_eligibility'):
        if checks.get(key) is False:
            checks[key] = True
    fixed = {**desk, 'checks': checks,
             'harvest_status': 'ok' if desk.get('harvest_status') == 'members_excluded' else desk.get('harvest_status')}
    gate = desk.get('full_desk_gate')
    if isinstance(gate, dict) and gate.get('pass') is False:
        gated = {k: v for k, v in checks.items() if k not in FULL_DESK_GATE_EXEMPT}
        fixed['full_desk_gate'] = {**gate, 'pass': bool(gated) and all(v is True for v in gated.values()),
                                   'recomputed': 'contention-only harvest exclusions are disclosure-only (R22-1)'}
    if all(v is True for v in checks.values()) and desk.get('pilot_status') == 'instrument_incomplete':
        fixed['pilot_status'] = 'instrument_ok'
    return fixed


def desk_passes(desk):
    """Whether a native desk.json counts as a passing full desk.

    Lead ruling 9 (W1-BLOCKERS): a false v4_B_bar alone does not fail the full desk (the triage row
    battery_window governs it). The native desk writes its own evidence-aware verdict
    (``full_desk_gate.pass``, charging-only exclusions removed); without it the recorded checks
    stand, minus the exempt B bar.
    """
    if not isinstance(desk, dict) or desk.get('harvest_status') != 'ok':
        return False
    gate = desk.get('full_desk_gate')
    if isinstance(gate, dict) and isinstance(gate.get('pass'), bool):
        return gate['pass']
    checks = desk.get('checks')
    if not isinstance(checks, dict):
        return False
    gated = {k: v for k, v in checks.items() if k not in FULL_DESK_GATE_EXEMPT}
    only_exempt_failed = any(checks.get(k) is False for k in FULL_DESK_GATE_EXEMPT)
    return (bool(gated) and all(v is True for v in gated.values())
            and (desk.get('pilot_status') == 'instrument_ok' or only_exempt_failed))


def build_packet(repo, *, record_commit, record_path, series_commit, series_path, pushed_ref,
                 now_epoch_s, current_artifact_set_sha256):
    require(number(now_epoch_s), 'arm clock unavailable')
    require(isinstance(current_artifact_set_sha256, str) and SHA.fullmatch(current_artifact_set_sha256),
            'current artifact-set digest unavailable')
    evidence = GitEvidence(repo)
    previous = WindowRecord(evidence, record_commit, record_path)
    require(series_path == SERIES_PATH, 'series state must be the canonical ledger ' + SERIES_PATH)
    series_commit = evidence.commit(series_commit)
    series_raw = evidence.read(series_commit, series_path)
    series = decode(series_raw)
    require(series.get('schema') == SERIES_SCHEMA, 'wrong series state schema')
    require(series.get('previous_record') == {'commit': previous.commit, 'path': record_path,
                                            'sha256': previous.sha256}, 'series previous record binding mismatch')
    prepared = now_epoch_s       # the arm's own clock; never lead-entered
    packet = {'schema': cadence.TRIAGE_SCHEMA, 'record_commit': previous.commit,
        'record_path': record_path, 'record_sha256': previous.sha256,
        'series_commit': series_commit, 'series_path': series_path, 'series_sha256': digest(series_raw),
        'pushed_ref': pushed_ref, 'previous_window': previous.window,
        'next_window_role': None, 'calibration_windows': [], 'lead_rulings': [], 'battery_rulings': [], 'window_chain': [],
        'next_window_id': None, 'series_manifest_sha256': None, 'series_history': [],
        'last_desk_passed_artifact_set_sha256': None,
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
        require(number(ended) and ended <= finalized <= prepared, 'record finalization out of order')
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
        decision = terminal_window_release(result, plan_id=plan['plan_id'], receipt_class=plan['receipt_class'],
                    now_epoch_s=prepared, chain_started=started, chain_exited=exited, courier_sent=True)
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
        # Today's check, until the R16 condition-waits evaluator receipt (align/2026-11-08-condition-waits-impl)
        # replaces it: a committed post-terminal quiet observation against the frozen policy, judged
        # against the arm's own clock.
        observed, policy = source('quiet'), series['quiet_requirements']
        result = previous.source('result')
        for name in ('cooldown_s', 'display_off_s', 'dwell_s', 'max_age_s'):
            require(number(policy.get(name)) and policy[name] > 0, 'quiet policy missing: ' + name)
        for name in ('cooldown_s', 'display_off_s', 'dwell_s'):
            require(number(observed.get(name)) and observed[name] >= policy[name], 'quiet start short: ' + name)
        require(number(observed.get('observed_at_epoch_s')) and number(result.get('ended_epoch_s'))
                and result['ended_epoch_s'] <= observed['observed_at_epoch_s'] <= prepared
                and prepared - observed['observed_at_epoch_s'] <= policy['max_age_s'],
                'quiet start evidence stale or predates terminal completion')
        require(observed.get('active_work') == [], 'desk, hashing or evidence traffic remains on MBP')
        return {'basis': 'post-terminal quiet observation meets frozen cooldown, display-off and dwell policy',
                'valid_until_epoch_s': observed['observed_at_epoch_s'] + policy['max_age_s']}

    def meter_coverage():
        # SECONDARY coverage is a recorded tabulation and never gates (Opus cold MED-2b, MED-3).
        pilot = previous.source('pilot')
        report = pilot.get('extra_checks', {}).get('km003c', pilot.get('km003c'))
        if not (isinstance(report, dict) and isinstance(report.get('members'), dict)):
            return {'status': 'recorded', 'basis': 'meter tabulation missing for the previous window (non-gating)',
                    'gaps': {}, 'tabulation': 'missing'}
        roster = {m['run_id'] for m in previous.roster()}
        gaps = {}
        for rid, row in report['members'].items():
            if not isinstance(row, dict) or row.get('status') not in ('available', 'missing'):
                gaps[rid] = ['meter coverage unevaluated']
            elif row['status'] == 'missing':
                gaps[rid] = list(row.get('flags') or [])
        for rid in sorted(roster - set(report['members'])):
            gaps[rid] = ['meter tabulation row missing']
        return {'status': 'recorded', 'basis': 'SECONDARY coverage tabulated; gaps listed (non-gating)',
                'gaps': gaps, 'powermetrics_admissibility_unchanged': True}

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
        return plan

    def last_desk_state():
        """The last desk-passed record, and the artifact-set digest of its committed code state."""
        last_ref = series.get('last_passed_record')
        require(isinstance(last_ref, dict), 'last desk-passed record missing')
        last_record = WindowRecord(evidence, last_ref['commit'], last_ref['path'])
        require(last_record.sha256 == last_ref.get('sha256'), 'last desk-passed record digest mismatch')
        last = effective_desk(last_record.source('desk'), last_record.source('exclusions'))
        require(desk_passes(last),
                'last desk-passed state has no passing desk')
        code_commit = evidence.commit(last_record.record.get('code_commit', last_record.commit))
        return last_record, committed_artifact_set_digest(evidence, code_commit)

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
        # One shared structural-bar predicate for history, pool admission and calibration (R22-2): a barred
        # window enters no pool and gives no partial use, including the members it did capture.
        bar = previous.structural_bar(eligible['captured_members'])
        if bar:
            require(not pool, f'{bar}: a structurally barred window enters no pool')
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
        # A15 / R21: only a U4 inconclusive triggers the R20 escalation sentinels; U5 is inconclusive by construction
        needed = 4 if any(r['U4']['status'] == 'inconclusive' for r in reports.values()) else 2
        planned = [m['run_id'] for m in next_plan()['members'] if m.get('role') == 'sentinel']
        frozen = series.get('sentinel_ids')
        require(isinstance(frozen, list) and len(frozen) == len(set(frozen)) and len(frozen) >= needed
                and planned == frozen, 'next frozen roster must include two extra sentinels after a U4 inconclusive')
        return {'basis': 'next sentinel roster recorded with the U4 consequence', 'sentinel_ids': planned}

    def eligibility():
        return {'basis': 'final desk eligibility, identity X5, U3 pair exclusions and capture inventory reconciled',
                'counts': previous.eligibility()}

    def full_desk():
        next_plan()
        last_record, last_digest = last_desk_state()
        packet['last_desk_passed_artifact_set_sha256'] = last_digest
        # Same derivation as the consumer: required after W1, or when the arm's current artifact set
        # differs from the one the last desk passed on.
        required = previous.window == 'W1' or last_digest != current_artifact_set_sha256
        desk = effective_desk(previous.source('desk'), previous.source('exclusions'))
        passing = desk_passes(desk)
        if desk.get('status') == 'running_off_mbp' and not required:
            return {'status': 'deferred', 'basis': 'unchanged later window; full desk running off MBP'}
        require(required is False or passing,
                'full desk must complete and pass after W1 or a code/config change')
        require(passing or desk.get('status') == 'running_off_mbp', 'full desk has not passed')
        require(desk.get('plan_id') == previous.source('plan')['plan_id'], 'full desk plan mismatch')
        require(last_digest == current_artifact_set_sha256 or not required,
                'full desk passed on a different code/config state than the arm will run')
        return {'basis': 'full desk completed and passing for the current code/config state'}

    for name, action in (('record_committed', committed), ('terminal_completion', terminal),
                         ('quiet_start_state', quiet), ('meter_coverage', meter_coverage),
                         ('capture_faults', faults)):
        check(name, action)
    for name, action in (('thermal_escalation', thermal), ('cohort_pool_rules', cohort),
                         ('sentinel_roster', sentinels), ('member_eligibility', eligibility)):
        if previous.window == 'R1':
            packet['checks'][name] = {'status': 'not_applicable', 'basis': 'previous window is R1'}
        else:
            check(name, action)
    check('full_desk_gate', full_desk)
    try:
        if packet['last_desk_passed_artifact_set_sha256'] is None:
            _record, packet['last_desk_passed_artifact_set_sha256'] = last_desk_state()
    except (ValueError, KeyError, TypeError, AttributeError):
        packet['last_desk_passed_artifact_set_sha256'] = None
    history_error = None
    battery_chain = None
    try:
        # Hash-linked series history (ruling 3): walk previous_record links from the previous record
        # back to the first record; an omitted attempt cannot be skipped because it is the link.
        chain, record, seen = [], previous, set()
        while True:
            require(record.commit + ':' + record.path not in seen, 'series history loops')
            seen.add(record.commit + ':' + record.path)
            chain.append(record)
            link = record.previous_link
            if link is None:
                break
            commit = evidence.commit(link['commit'])
            parent = WindowRecord(evidence, commit, link['path'])
            require(parent.sha256 == link['sha256'], 'series history link digest mismatch')
            evidence.git('merge-base', '--is-ancestor', parent.commit, record.commit)
            require(parent.commit != record.commit, 'series history link does not precede the record')
            record = parent
        chain.reverse()
        require(chain[0].window in ('R1', 'W1'), 'series history does not reach the first v4 record')
        packet['window_chain'] = [{'window': r.window, 'commit': r.commit, 'path': r.path, 'sha256': r.sha256,
                                   'previous_sha256': (r.previous_link or {}).get('sha256')} for r in chain]
        counted = []
        for record in chain:
            if record.record.get('role') != 'calibration':
                continue
            record.verify_raw()
            row = record.eligibility()
            bar = record.structural_bar(row['captured_members'])
            if bar:
                # R22-2: a window barred for a STRUCTURAL reason enters no pool and is replaced, not counted.
                row = {**row, 'eligible_benign': dict.fromkeys(cadence.CAL_PAIRS, 0), 'barred': bar}
            counted.append((record, row['captured_members'], bar))
            packet['calibration_windows'].append(row)
        attempts(counted)
        if previous.record.get('role') == 'calibration':
            require(chain[-1].commit == previous.commit and chain[-1].path == previous.path,
                    'previous calibration record missing from history tail')
        for row in series.get('lead_rulings', []):
            require(isinstance(row, dict) and set(row) == {'ruling_id', 'after_window', 'text', 'lead_signature'},
                    'lead ruling row malformed')
            text = evidence.source(series_commit, row['text'], json_value=False)
            require(bool(text.strip()), 'lead ruling text empty')
            packet['lead_rulings'].append({'ruling_id': row['ruling_id'], 'text_sha256': digest(text),
                'resets': 'zero_capture_escalation', 'after_window': row['after_window'],
                'lead_signature': row['lead_signature']})
        packet['calibration_decision'] = cadence.calibration_stop(packet['calibration_windows'], packet['lead_rulings'])
        # The frozen series binding (R15) needs the window id the arm will run and the chronological history,
        # DERIVED here from the authenticated hash chain (the arm binds its own rebuild, never a supplied one).
        plan_window = next_plan()['window']
        require(isinstance(plan_window, str) and cadence.WINDOW_ID.match(plan_window), 'next plan window id invalid')
        packet['next_window_id'] = plan_window.split('#')[0]
        try:
            packet['series_manifest_sha256'] = digest(evidence.read(series_commit, MANIFEST_PATH))
        except ValueError:
            packet['series_manifest_sha256'] = None
        by_attempt = {r['window']: r for r in packet['calibration_windows']}
        history = []
        for record in chain:
            if record.window in ('R1', 'W1'):
                continue
            if record.record.get('role') == 'calibration':
                row = by_attempt[record.window]
                # The desk's provisional counts are an upper bound the final adjudication may lower, never
                # raise (R15): carried into the history so the series binding enforces it.
                counts = {'captured_members': row['captured_members'], 'status': row['status'],
                          'eligible_benign': row['eligible_benign'], 'desk_eligible_benign': record.desk_ceiling()}
                if row.get('barred'):
                    counts['barred'] = row['barred']
            else:
                counts = {'captured_members': record.counted_captures(), 'status': 'final',
                          'eligible_benign': dict.fromkeys(cadence.CAL_PAIRS, 0)}
            history.append({'window_id': record.window.split('#')[0], 'attempt_id': record.window, **counts})
            for ruling in packet['lead_rulings']:
                if ruling['after_window'] == record.window:
                    history.append({'lead_release': dict(ruling)})
        packet['series_history'] = history
        for row in series.get('battery_rulings', []):
            require(isinstance(row, dict) and set(row) == {'ruling_id', 'after_window', 'text', 'lead_signature'},
                    'battery ruling row malformed')
            text = evidence.source(series_commit, row['text'], json_value=False)
            require(bool(text.strip()), 'battery ruling text empty')
            packet['battery_rulings'].append({'ruling_id': row['ruling_id'], 'text_sha256': digest(text),
                'after_window': row['after_window'], 'lead_signature': row['lead_signature']})
        battery_chain = chain
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        history_error = str(exc)
        packet['calibration_windows'] = [{}]  # cannot silently truncate or take R1's N/A shortcut
        packet['lead_rulings'] = []
        packet['battery_rulings'] = []
        packet['window_chain'] = []
        packet['series_history'] = []
        packet['calibration_error'] = history_error
    def battery():
        # Lead ruling 9 (R14, rule zero_B_auto_resume_v1): the previous window's B bar. Missing
        # evidence is a non-pass; consecutive_non_pass counts the trailing non-passing windows on
        # the hash-linked chain (R1 has no B bar). The consumer turns a first non-pass into an
        # automatic resume and needs a signed battery_rulings row for a second.
        require(battery_chain is not None, 'window chain unavailable')

        def bar(record):
            try:
                checks = record.source('desk').get('checks')
                return isinstance(checks, dict) and checks.get('v4_B_bar') is True
            except (ValueError, KeyError, TypeError, AttributeError):
                return False
        if bar(previous):
            return {'basis': 'previous window B bar passed'}
        streak = 0
        for record in reversed(battery_chain):
            if record.window == 'R1' or bar(record):
                break
            streak += 1
        return {'status': 'fail', 'consecutive_non_pass': max(streak, 1),
                'basis': f'previous window B bar did not pass ({max(streak, 1)} consecutive non-passing)'}
    if previous.window == 'R1':
        packet['checks']['battery_window'] = {'status': 'not_applicable', 'basis': 'previous window is R1'}
    else:
        check('battery_window', battery)
    # ARM booleans are deliberately absent from the packet. This evaluation assumes them only to
    # isolate packet readiness; it is never arm authority.
    expiry = packet['checks'].get('quiet_start_state', {}).get('valid_until_epoch_s')
    if number(expiry):
        packet['valid_until_epoch_s'] = expiry
    evaluation = cadence.next_arm_triage(
        packet, {name: True for name in packet['arm_pending']},
        {'artifact_set_sha256': current_artifact_set_sha256, 'record_commit_exists': True, 'record_bound': True},
        now_epoch_s=now_epoch_s)
    if history_error:
        evaluation['admitted'] = False
        evaluation['reasons'].append('calibration history: ' + history_error)
    packet['packet_preflight'] = {'ready': evaluation['admitted'], 'reasons': evaluation['reasons'],
                                   'arm_checks_still_required': packet['arm_pending']}
    packet['evidence'] = sorted(evidence.inventory.values(), key=lambda r: (r['commit'], r['path']))
    return packet


def main(argv=None):
    import time
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
            value = build_packet(args.repo, **{name: getattr(args, name) for name in names},
                                 now_epoch_s=time.time(),
                                 current_artifact_set_sha256=registration.artifact_set_digest(args.repo))
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
