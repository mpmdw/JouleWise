#!/usr/bin/env python3
"""ALIGN v4 native exporter (release runbook section 6a): one custody -> both builds' inputs, same raw bytes.

For every window attempt of a series this reads only:
- the COMMITTED window record (``git show commit:path`` through ``WindowRecord``, scripts/align_v4_next_arm_packet.py);
- the record-bound finalized tree manifest it names, and the harvest-off restored session at that manifest's
  ``source_root`` (scripts/align_v4_harvest_off.py ``unpack`` restores at the same absolute path);
- the frozen R24 allocation, the registered U3 bar, the registration inputs and the R1 references (config).

It writes, under ``export_root``:
- ``engine-input.json``: the engine manifest (``joulewise.align_v4.analysis_input.v1``, raw-source form);
- ``recompute/``: the independent recompute's input layout (RECOMPUTE-opus.md, "Input layout");
- ``crosswalk.json``: the structure-only crosswalk (``joulewise.v4_release.crosswalk.v1``);
- ``census.json``: every raw reference with its SHA-256 and its custody origin.

Raw files the engine adapter reads directly (production Episode JSON, the NUL-framed powermetrics plist, the
member config, KM003C stream JSONL, the night result) are placed by hard link (or byte copy) and referenced by
``{path, sha256}``; both builds read the SAME file for the plist, the config, the meter streams and the terminal
result. Only layout projections are derived (the recompute's episode/metadata/thermal rows and the engine's
JSON journal), always from the same verified bytes and with production functions; see section 6a.

Incremental: each window exports as it lands (``export --window ATTEMPT``). A landed window's files are never
rewritten; re-exporting it must reproduce them byte for byte or it refuses. The series index files
(engine-input.json, series.json, crosswalk.json, census.json, the analysis-form manifest) are rebuilt from the
landed windows' state each time.

Exit 0 exported (or unchanged); 2 refused with one fixed code. Standard output is one JSON line with structure
only (codes, window ids, counts); details go to standard error.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONFIG_SCHEMA = 'joulewise.v4_export.config.v1'
R1_REFERENCES_SCHEMA = 'joulewise.v4_export.r1_references.v1'
ENGINE_SCHEMA = 'joulewise.align_v4.analysis_input.v1'
CROSSWALK_SCHEMA = 'joulewise.v4_release.crosswalk.v1'
CENSUS_SCHEMA = 'joulewise.v4_export.census.v1'
STATE_SCHEMA = 'joulewise.v4_export.window_state.v1'
RESULT_SCHEMA = 'joulewise.unattended_night_result.v1'
SERIES_PLAN_SCHEMA = 'joulewise.align_v4.series_window.v1'     # scripts/align_v4_series.py:339-340
W1_PLAN = {'schema_version': 'joulewise.align_v4.v1', 'plan_id': 'align-v4'}   # the W1 kit plan
ALLOCATION_SHA256 = '21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c'
R24_ORDER = ('W1', *(f'C{i}' for i in range(1, 15)), *(f'T{i}' for i in range(1, 4)))
H_STAR_GRID = [128, 256, 384, 512, 768, 1024, 1536, 2048]           # R26, registered text
U6_SPLIT_RULE = 'within_pair_episode_order'                        # A16 (R21), the frozen U6 split
D_MODEL = 'qwen3.8-27b'
PAIRS = {'spam_filter_update': 'spam', 'bank_transfer_2': 'bank'}
W1_SENTINEL_ORDINALS = [5, 17]                                     # protocol v4 W1 roster (R23)
DECLARED_BARS = ('u1_u3_fail', 'whole_window_capture_failure')
HEX40, HEX64 = re.compile(r'[0-9a-f]{40}\Z'), re.compile(r'[0-9a-f]{64}\Z')
ATTEMPT = re.compile(r'(W1|C(?:[1-9]|1[0-4])|T[1-3])#([1-9][0-9]*)\Z')
CONFIG_KEYS = {'schema', 'export_root', 'records_repo', 'kit_root', 'allocation', 'u3_bar', 'r1_references',
               'registration_inputs', 'engine_route', 'windows'}
WINDOW_KEYS = {'attempt_id', 'record_commit', 'record_path', 'session_root', 'final_record'}
RECORD_KEYS = {'schema', 'window', 'role', 'finalized_at_epoch_s', 'previous_record', 'sources', 'captures',
               'raw_evidence', 'finalized_manifest', 'code_commit', 'code_config', 'code_config_commit',
               'previous_final', 'barred'}
V4_SERIES_KEYS = {'window_id', 'role', 'manifest_sha256'}
SENSOR_KEYS = {'s_fast', 's_slow', 'fan_keys', 'r0_sha256'}
R1_KEYS = {'schema', 'qualified', 'r1_replay_pair_j', 'delta_slow_c', 'designed_start_states'}
R1_STATE_KEYS = {'designed_slow_c', 'g0_release_slow_c', 'turn_owned_j', 'token_identical'}
MEMBER_FILES = ('config.json', 'metadata.json', 'events.jsonl', 'outputs/align_episode.json',
                'outputs/align_turns.jsonl', 'outputs/align_thermal.jsonl', 'raw/powermetrics.plist')


class Refused(Exception):
    def __init__(self, code, detail=''):
        super().__init__(code)
        self.code, self.detail = code, detail


def require(condition, code, detail=''):
    if not condition:
        raise Refused(code, detail)


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical(value):
    """Canonical JSON bytes (sorted keys, compact, ASCII, finite), newline-terminated."""
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
            + '\n').encode()


def strict_loads(raw, code):
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, code, 'duplicate JSON key')
            out[k] = v
        return out

    def bad(_):
        raise Refused(code, 'non-finite JSON')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)
    except Refused:
        raise
    except ValueError as exc:
        raise Refused(code, str(exc)) from None


def jsonl_rows(raw, code):
    return [strict_loads(line, code) for line in raw.splitlines() if line.strip()]


# --------------------------------------------------------------------------------------- contract digests

def identity_sha256(turn_rows):
    """Export contract (section 6a, lead ruling on reading 1): SHA-256 of the canonical per-turn generation
    ``[[prompt_token_ids, output_token_ids], ...]`` in turn order, from outputs/align_turns.jsonl. Canonical bytes:
    ``json.dumps(value, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')`` (no sort
    is needed for lists; no trailing newline). None when any turn lacks either id list."""
    value = []
    for row in turn_rows:
        g = row.get('generation') or {}
        p, o = g.get('prompt_token_ids'), g.get('output_token_ids')
        if not (isinstance(p, list) and isinstance(o, list)):
            return None
        value.append([p, o])
    raw = json.dumps(value, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')
    return sha256_bytes(raw)


def cohort_sha256(identity, configuration):
    """Export contract (section 6a): the recompute's cohort digest, SHA-256 of
    ``json.dumps({"configuration": ..., "identity": ...}, sort_keys=True, separators=(',', ':'),
    ensure_ascii=True, allow_nan=False)`` over the production cohort identity and the frozen four-slot
    configuration (scripts/align_v4_thermal_desk.py:enrich_record)."""
    raw = json.dumps({'configuration': configuration, 'identity': identity}, sort_keys=True,
                     separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')
    return sha256_bytes(raw)


def registered_span_ns(episode):
    """Export contract (lead ruling on reading 2, WP22 rule scripts/align_v4_w1_synthetic.py:353): the first G0
    start_ns, or the episode start when there is no G0, through the episode end."""
    intervals = ((episode.get('hardware') or {}).get('thermal') or {}).get('intervals') or []
    g0 = [i for i in intervals if isinstance(i, dict) and i.get('kind') == 'G0']
    return [g0[0]['start_ns'] if g0 else episode['start_ns'], episode['end_ns']]


def exact_ns(seconds):
    """Recorded seconds -> integer ns, exactly (A21, P2 ruling): the recorded binary float through Fraction,
    ties to even. Integers stay exact. Strings and bools refuse."""
    require(type(seconds) in (int, float), 'seconds_not_numeric', type(seconds).__name__)
    return round(Fraction(seconds) * 1_000_000_000)


# ------------------------------------------------------------------------------------------- custody paths

class Session:
    """The restored session at the finalized manifest's source_root. Every read is checked lexically (no
    traversal), with lstat on every component (no symlink), and against the finalized manifest digest."""

    def __init__(self, root, finalized):
        self.root = Path(root)
        self.entries = finalized['entries']
        require(self.root.is_absolute() and not self.root.is_symlink() and self.root.is_dir(),
                'session_unavailable', str(root))

    def relative(self, path):
        p = Path(path)
        require(p.is_absolute(), 'path_refused', str(path))
        require('..' not in p.parts, 'path_refused', str(path))
        try:
            rel = p.relative_to(self.root)
        except ValueError:
            raise Refused('path_outside_session', str(path)) from None
        return PurePosixPath(*rel.parts).as_posix()

    def path(self, rel):
        rel = PurePosixPath(rel)
        require(rel.parts and not rel.is_absolute() and not any(x in ('', '.', '..') for x in rel.parts),
                'path_refused', str(rel))
        cursor = self.root
        for part in rel.parts:
            cursor = cursor / part
            require(not cursor.is_symlink(), 'path_refused', 'symlink: ' + str(cursor))
        return cursor

    def has(self, rel):
        row = self.entries.get(str(rel))
        return isinstance(row, dict) and 'sha256' in row

    def read(self, rel, *, missing='member_file_missing'):
        rel = str(rel)
        path = self.path(rel)
        row = self.entries.get(rel)
        require(row is not None or path.exists(), missing, rel)
        require(isinstance(row, dict) and 'sha256' in row, 'file_not_in_finalized_manifest', rel)
        require(path.is_file(), missing, rel)
        raw = path.read_bytes()
        require(sha256_bytes(raw) == row['sha256'] and len(raw) == row['size'], 'digest_mismatch', rel)
        return raw

    def verify_file(self, rel, *, missing='member_file_missing'):
        """A large raw file: hash it streaming against the finalized manifest; returns (path, sha256, size)."""
        rel = str(rel)
        path = self.path(rel)
        row = self.entries.get(rel)
        require(row is not None or path.exists(), missing, rel)
        require(isinstance(row, dict) and 'sha256' in row, 'file_not_in_finalized_manifest', rel)
        require(path.is_file(), missing, rel)
        digest = sha256_file(path)
        require(digest == row['sha256'] and path.stat().st_size == row['size'], 'digest_mismatch', rel)
        return path, digest, row['size']


class Writer:
    """Places files under one staging root; every placed file is recorded as (relative path, sha256)."""

    def __init__(self, stage):
        self.stage = Path(stage)
        self.files = {}

    def _target(self, rel):
        target = self.stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        require(not target.exists(), 'export_layout_collision', rel)
        return target

    def bytes(self, rel, raw):
        self._target(rel).write_bytes(raw)
        self.files[rel] = sha256_bytes(raw)
        return {'path': rel, 'sha256': self.files[rel]}

    def place(self, rel, source, digest):
        """Hard link (same device) or byte copy of a verified custody file, re-verified after placing."""
        target = self._target(rel)
        try:
            os.link(source, target)
        except OSError:
            shutil.copyfile(source, target)
        require(sha256_file(target) == digest, 'digest_mismatch', rel)
        self.files[rel] = digest
        return {'path': rel, 'sha256': digest}


# ------------------------------------------------------------------------------------------------ config

def read_ref_file(ref, code):
    require(isinstance(ref, dict) and isinstance(ref.get('path'), str) and Path(ref['path']).is_absolute(),
            'config_invalid', code)
    path = Path(ref['path'])
    require(not path.is_symlink() and path.is_file(), code, 'missing')
    raw = path.read_bytes()
    if 'sha256' in ref:
        require(ref['sha256'] == sha256_bytes(raw), code, 'digest')
    return raw


def load_config(path):
    config = strict_loads(Path(path).read_bytes(), 'config_invalid')
    require(isinstance(config, dict) and config.get('schema') == CONFIG_SCHEMA, 'config_invalid', 'schema')
    require(set(config) <= CONFIG_KEYS, 'unknown_contract_key', 'config: ' + ','.join(sorted(set(config) - CONFIG_KEYS)))
    # Lead ruling 4 (2026-11-08): the release path exports through raw_source only.
    require(config.get('engine_route', 'raw_source') == 'raw_source', 'thermal_source_refused')
    for key in ('export_root', 'records_repo', 'kit_root'):
        require(isinstance(config.get(key), str) and Path(config[key]).is_absolute(), 'config_invalid', key)
    windows = config.get('windows')
    require(isinstance(windows, list) and windows, 'config_invalid', 'windows')
    seen = set()
    for w in windows:
        require(isinstance(w, dict) and set(w) <= WINDOW_KEYS, 'unknown_contract_key', 'window entry')
        m = ATTEMPT.match(w.get('attempt_id') or '')
        require(m is not None and w['attempt_id'] not in seen, 'config_invalid', str(w.get('attempt_id')))
        seen.add(w['attempt_id'])
        require(isinstance(w.get('record_commit'), str) and HEX40.match(w['record_commit'])
                and isinstance(w.get('record_path'), str), 'config_invalid', w['attempt_id'])
        require(w.get('session_root') is None or (isinstance(w['session_root'], str)
                and Path(w['session_root']).is_absolute()), 'config_invalid', 'session_root')
    return config


# --------------------------------------------------------------------------------------- record + roster

def open_record(config, entry):
    from scripts import align_v4_next_arm_packet as packet
    evidence = packet.GitEvidence(config['records_repo'])
    try:
        record = packet.WindowRecord(evidence, entry['record_commit'], entry['record_path'])
        require(set(record.record) <= RECORD_KEYS, 'unknown_contract_key',
                'record: ' + ','.join(sorted(set(record.record) - RECORD_KEYS)))
        final = entry.get('final_record')
        if final is not None:
            successor = packet.WindowRecord(evidence, final['record_commit'], final['record_path'])
            record.bind_final(successor)
        record.verify_raw()
    except Refused:
        raise
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise Refused('record_unreadable', str(exc)) from None
    slot, attempt = ATTEMPT.match(entry['attempt_id']).groups()
    require(record.window in (slot + '#' + attempt, slot if attempt == '1' else None), 'record_window_differs',
            record.window)
    return record, evidence


def frozen_allocation(config):
    raw = read_ref_file(config.get('allocation'), 'allocation_differs')
    require(sha256_bytes(raw) == ALLOCATION_SHA256, 'allocation_differs', 'digest')
    manifest = strict_loads(raw, 'allocation_differs')
    require(tuple(manifest.get('order') or ()) == R24_ORDER
            and tuple(w.get('id') for w in manifest['windows']) == R24_ORDER, 'allocation_differs', 'order')
    return raw, manifest


def stage_index(stage_id, ordinal):
    """W1 contrast stage (recompute ``contrast.stage``; engine ``stage``): the kit's two episode stages, a -> 0,
    b -> 1 (scripts/align_v4_kit.py stage graph; A19 second-stage indicator)."""
    require(isinstance(stage_id, str) and stage_id[-2:] in ('-a', '-b'), 'roster_differs_from_plan',
            f'stage of ordinal {ordinal}')
    return 0 if stage_id.endswith('-a') else 1


def build_roster(slot, record_rows, allocation):
    """Engine roster rows (R15/R24 fields) and recompute member rows from the committed collection plan, checked
    field by field against the frozen R24 allocation. Run ids are the collection plan's, never renamed."""
    frozen = {r['ordinal']: r for r in next(w for w in allocation['windows'] if w['id'] == slot)['members']}
    rows = sorted(record_rows, key=lambda r: r.get('ordinal', 0))
    ordinals = [r.get('ordinal') for r in rows]
    expected = sorted(frozen) + ([23, 24] if len(rows) == len(frozen) + 2 and slot != 'W1' else [])
    require(ordinals == expected, 'roster_differs_from_manifest', 'ordinals')
    engine, recompute = [], []
    for row in rows:
        o = row['ordinal']
        base = frozen.get(o) or frozen[5]       # R20 escalation sentinels 23/24 replay ordinal 5
        require(row.get('supplemental', False) == (o in (23, 24)), 'roster_differs_from_manifest', f'{o} supplemental')
        for mine, theirs in (('task_pair', 'pair'), ('condition', 'condition'), ('seed_index', 'seed_index'),
                             ('expected_episode_seed', 'episode_seed'), ('model_id', 'model_id')):
            require(row.get(mine) == base[theirs], 'roster_differs_from_manifest', f'ordinal {o} {mine}')
        require(isinstance(row.get('run_id'), str) and ':' not in row['run_id'] and row['run_id'],
                'roster_differs_from_manifest', f'ordinal {o} run_id')
        if slot != 'W1' and base['pool'] != 'anchor':
            # Production run ids (scripts/align_v4_series.py:38, :285); supplemental 23/24 keep their own ordinal.
            require(row['run_id'] == f'align-v4-{slot.lower()}-e{o:02}', 'roster_differs_from_manifest',
                    f'ordinal {o} run_id')
        if slot == 'W1':
            role = base['role']
            series_role = ('anchor' if role == 'anchor' else 'sentinel' if o in W1_SENTINEL_ORDINALS
                           else 'contrast' if role[:2] in ('X-', 'Y-') else 'development')
            require(row.get('role') == role, 'roster_differs_from_manifest', f'ordinal {o} role')
            held = False
        else:
            pool = base['pool']
            series_role = ('supplemental_sentinel' if o in (23, 24) else pool if pool in ('anchor', 'sentinel')
                           else 'sabotage' if base['condition'] == 'sabotage' else 'benign')
            held = o not in (23, 24) and pool in ('calibration', 'known_h', 'test')
        require((series_role == 'anchor') == (1 <= o <= 4), 'roster_differs_from_manifest', f'ordinal {o} anchor')
        local = row['run_id']
        erow = dict(ordinal=o, task_pair=row['task_pair'], condition=row['condition'], model_id=row['model_id'],
                    seed_index=row['seed_index'], expected_episode_seed=row['expected_episode_seed'],
                    held_out=held, series_role=series_role, run_id=local)
        rrow = dict(ordinal=o, run_id=local, kind={'supplemental_sentinel': 'sentinel'}.get(series_role, series_role),
                    model='D' if row['model_id'] == D_MODEL else '30B', pair=PAIRS[row['task_pair']],
                    condition=row['condition'], expected_episode_seed=row['expected_episode_seed'])
        rrow['seed_index'] = row['seed_index']          # every member, 30B included (r23k review ruling 4)
        if series_role == 'contrast':
            rrow['contrast'] = dict(template=base['role'][0], arm=base['role'][2],
                                    stage=stage_index(row.get('stage_id'), o))
        engine.append(erow)
        recompute.append(rrow)
    return engine, recompute


# ---------------------------------------------------------------------------------------------- members

def planned_kit(kit_root, plan_row):
    """The member's kit config at the committed plan row's ``config_path`` (relative to the measurement checkout
    ``kit_root``), bound by the row's ``config_sha256`` (scripts/align_v4_series.py:302). Returns its bytes."""
    rel, digest = plan_row.get('config_path'), plan_row.get('config_sha256')
    require(isinstance(rel, str) and isinstance(digest, str) and HEX64.match(digest), 'config_digest_not_planned',
            f"plan row {plan_row.get('run_id')}")
    parts = PurePosixPath(rel).parts
    require(parts and not PurePosixPath(rel).is_absolute() and not any(x in ('', '.', '..') for x in parts),
            'path_refused', rel)
    cursor = Path(kit_root)
    for part in parts:
        cursor = cursor / part
        require(not cursor.is_symlink(), 'path_refused', 'symlink: ' + str(cursor))
    require(cursor.is_file(), 'config_digest_not_planned', 'kit config missing: ' + rel)
    raw = cursor.read_bytes()
    require(sha256_bytes(raw) == digest, 'config_digest_not_planned', 'kit config digest: ' + rel)
    return raw


def writer_config_bytes(kit_raw):
    """The bytes RunBundleWriter.create writes as config.json for this kit config (joulewise/bundle.py:964-967;
    = scripts/align_v4_kit.bundle_config_bytes). None when the digest-verified kit is not a JSON object or fails
    BenchmarkConfig normalization: that is the builds' ``config_invalid`` exclusion, never an exporter judgment."""
    from joulewise.schemas import BenchmarkConfig
    from scripts.align_v4_kit import bundle_config_bytes
    try:
        mapping = json.loads(kit_raw)
        if not isinstance(mapping, dict):
            return None
        return bundle_config_bytes(BenchmarkConfig.from_mapping(mapping))
    except (ValueError, TypeError, KeyError, AttributeError, UnicodeDecodeError):
        return None


def plan_owner_check(plan, slot, attempt_id):
    """The committed collection plan must be THIS window's producer plan (r23k review refinement 1-2): C/T
    ``series_window.v1`` with plan_id ``align-v4-<window>``, ``window_id`` and the frozen manifest digest
    (scripts/align_v4_series.py:339-340); W1 the kit plan (``joulewise.align_v4.v1``, ``align-v4``). A plan
    ``attempt_id`` must equal the record's attempt."""
    expected = dict(W1_PLAN) if slot == 'W1' else dict(
        schema_version=SERIES_PLAN_SCHEMA, plan_id='align-v4-' + slot.lower(), window_id=slot,
        series_manifest_sha256=ALLOCATION_SHA256)
    require(isinstance(plan, dict) and all(plan.get(k) == v for k, v in expected.items()),
            'config_digest_not_planned:wrong_window', slot)
    require('attempt_id' not in plan or plan['attempt_id'] == attempt_id, 'config_digest_not_planned:wrong_window',
            'plan attempt_id')


def member_export(session, bundle_rel, slot_rows, capture, *, rec_wid, slot, w, battery, meter, desk, kit):
    """One captured member: verify every bundle file against the finalized manifest, place the raw files, derive
    the layout projections with production functions. Returns (engine row, recompute meta, census rows)."""
    from joulewise.align.apple.sampler import _restore_stamp, stamp_mapping
    from joulewise.align.apple.thermal_desk import normalize_journal
    from joulewise.align.apple.diagnostics import cache_statistics
    from joulewise.align.apple import v4_registration as registration
    from joulewise.align.apple.workload import EpisodeSpec
    erow, rrow = slot_rows
    local = erow['run_id']
    raw = {}
    for name in MEMBER_FILES:
        if name in ('raw/powermetrics.plist', 'outputs/align_thermal.jsonl'):
            continue
        raw[name] = session.read(f'{bundle_rel}/{name}')
    plist_path, plist_sha, plist_size = session.verify_file(f'{bundle_rel}/raw/powermetrics.plist')
    # The record's capture descriptor names the member's measurement artifact: the raw plist (section 6a).
    require(capture.get('sha256') == plist_sha and capture.get('bytes', plist_size) == plist_size,
            'capture_digest_differs', local)
    # Config custody chain (r23k review ruling 3): plan row -> kit config digest -> the writer's bundle bytes.
    kit_raw, kit_ref = kit
    expected = writer_config_bytes(kit_raw)
    if expected is not None:      # an invalid kit is the builds' config_invalid exclusion; export it unjudged
        require(expected == raw['config.json'], 'config_digest_not_planned',
                local + ': bundle config.json is not the writer bytes of the planned kit config')
    config = strict_loads(raw['config.json'], 'member_malformed')
    metadata = strict_loads(raw['metadata.json'], 'member_malformed')
    episode = strict_loads(raw['outputs/align_episode.json'], 'member_malformed')
    turn_rows = jsonl_rows(raw['outputs/align_turns.jsonl'], 'member_malformed')
    # The thermal sidecar exists for gated members only (an ungated 30B anchor writes none); production reads it
    # as optional (thermal_desk.read_bundle_record jsonl()). A gated Episode without it refuses.
    gated = bool((episode.get('hardware') or {}).get('thermal'))
    has_sidecar = session.has(f'{bundle_rel}/outputs/align_thermal.jsonl')
    require(has_sidecar or not gated, 'member_file_missing', f'{bundle_rel}/outputs/align_thermal.jsonl')
    sidecar = (jsonl_rows(session.read(f'{bundle_rel}/outputs/align_thermal.jsonl'), 'member_malformed')
               if has_sidecar else [])
    try:
        spec = EpisodeSpec.from_text(config['workload_profile']['prompt_text'])
    except (ValueError, TypeError, KeyError, AttributeError):
        spec = None      # the builds classify the member (config_invalid); the cohort fields stay unavailable
    # Config identity versus the roster is the builds' config_identity_differs exclusion (never judged here);
    # the bundle directory must hold the planned member's Episode (the engine refuses otherwise).
    require(episode.get('episode_id') in (local, local.lower()), 'roster_differs_from_plan', local + ' episode')
    hw = episode.get('hardware') or {}
    thermal = hw.get('thermal') or {}
    sensors = (thermal.get('policy') or {}).get('sensors')
    if sensors is not None:
        require(isinstance(sensors, dict) and set(sensors) <= SENSOR_KEYS and {'s_fast', 's_slow'} <= set(sensors),
                'unknown_contract_key', 'policy.sensors')
    for key in ('registered_span_ns', 'production_offset_ns', 'cache'):
        require(key not in hw, 'unknown_contract_key', 'episode hardware already carries ' + key)
    require(all(r.get('turn') == k for k, r in enumerate(turn_rows)) and len(turn_rows) == len(episode['turns']),
            'turn_rows_mismatch', local)
    evidence = metadata.get('uncertainty_evidence')
    anchor = (evidence or {}).get('clock_anchor') or {}
    endpoint = anchor.get('first_sample_end_point_epoch_s')
    require(type(endpoint) in (int, float), 'seconds_not_numeric', 'first_sample_end_point_epoch_s')
    power_hz = (config.get('sampling') or {}).get('power_hz')
    require(type(power_hz) in (int, float) and power_hz > 0, 'member_malformed', 'sampling.power_hz')
    period_ns = round(1_000_000_000 / power_hz)       # = workload.read_episode_bundle:916
    stamps = [_restore_stamp(s) for s in hw['paired_clock_stamps_ns']]
    mapping, _ = stamp_mapping(stamps, episode_domain=episode['clock_domain'], evidence=evidence)
    span = registered_span_ns(episode)
    gate_rows = normalize_journal(sidecar)
    os_readings = [[r['monotonic_ns'], r.get('status', {}).get('os_level')] for r in gate_rows
                   if r.get('status', {}).get('os_level') is not None]       # = thermal_desk.read_bundle_record:811-813
    identity = registration.cohort_identity(config, spec, hw.get('runtime_identity') or {}) if spec else None
    configuration = ({k: getattr(spec, k) for k in ('max_episode_decode_tokens', 'deadman_s', 'max_tokens', 'max_turns')}
                     if spec else None)
    status = 'incomplete' if (hw.get('token_budget') or {}).get('incomplete', True) else 'completed'
    cache = cache_statistics(turn_rows)
    ident = identity_sha256(turn_rows)
    # Cross-check against the committed desk record of this member (never a second source of truth).
    if desk is not None:
        for key, mine in (('battery', battery), ('cohort_identity', identity), ('configuration', configuration),
                          ('status', status), ('cache_statistics', cache)):
            if key in desk:
                require(desk[key] == json.loads(json.dumps(mine)), 'desk_record_differs', f'{local} {key}')
        require('owned_energy_flags' not in desk, 'owned_energy_flags_unexpected', local)
    mdir = f'recompute/windows/{rec_wid}/members/{rrow["run_id"]}'
    edir = f'engine/windows/{rec_wid}/members/{local}'
    census = []

    def ref(entry, origin):
        census.append(dict(entry, origin=f'{session.root}/{origin}' if origin else None))
        return entry
    plist = ref(w.place(f'{mdir}/raw/powermetrics.plist', plist_path, plist_sha), f'{bundle_rel}/raw/powermetrics.plist')
    cfg = ref(w.place(f'{mdir}/config.json', session.path(f'{bundle_rel}/config.json'),
                      sha256_bytes(raw['config.json'])), f'{bundle_rel}/config.json')
    ep_ref = ref(w.place(f'{edir}/align_episode.json', session.path(f'{bundle_rel}/outputs/align_episode.json'),
                         sha256_bytes(raw['outputs/align_episode.json'])), f'{bundle_rel}/outputs/align_episode.json')
    journal = ref(w.bytes(f'{edir}/journal.json', canonical(sidecar)), None)
    # Recompute projections: production bytes plus the contract fields, nothing removed or recomputed.
    rep = json.loads(raw['outputs/align_episode.json'])
    rep['identity_sha256'] = ident
    rep['cohort_sha256'] = cohort_sha256(identity, configuration) if spec else None
    rep['hardware'].update(registered_span_ns=span, production_offset_ns=mapping.offset_ns, cache=cache)
    require('completed' not in rep, 'unknown_contract_key', 'episode already carries completed')
    rep['completed'] = status == 'completed'          # = the engine's status (enrich_record:74)
    for t in rep['turns']:
        require('reasoning_tokens' not in t, 'unknown_contract_key', 'turn already carries reasoning_tokens')
        t['reasoning_tokens'] = t['hidden_tokens']        # engine reads Episode hidden_tokens (A0)
    w.bytes(f'{mdir}/outputs/align_episode.json', canonical(rep))
    meta = json.loads(raw['metadata.json'])
    require('sampling' not in meta, 'unknown_contract_key', 'metadata already carries sampling')
    meta['sampling'] = {'power_period_ns': period_ns}
    if anchor.get('status') == 'bounded':
        meta['uncertainty_evidence']['clock_anchor']['wall_minus_monotonic_bounds_ns'] = [
            exact_ns(anchor['wall_minus_monotonic_lower_s']), exact_ns(anchor['wall_minus_monotonic_upper_s'])]
    w.bytes(f'{mdir}/metadata.json', canonical(meta))
    if has_sidecar:
        w.bytes(f'{mdir}/outputs/align_thermal.jsonl',
                b''.join((json.dumps(r, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
                         for r in gate_rows))
    row = dict(run_id=erow['run_id_export'], captured=True, status=status, episode=ep_ref, powermetrics=plist,
               config=cfg, planned_config=kit_ref, first_record_endpoint_s=endpoint, nominal_interval_ns=period_ns,
               stamps=[asdict(s) for s in stamps], clock_evidence=evidence, offset_ns=mapping.offset_ns,
               journal=journal, os_readings=os_readings,
               registered_os_readings=[r for r in os_readings if span[0] <= r[0] <= span[1]],
               registered_span_ns=span, turn_rows=turn_rows, identity_sha256=ident, battery=battery,
               cohort_identity=identity, configuration=configuration, cache_statistics=cache,
               exclusion_codes=erow['exclusion_codes'])
    if desk is not None and desk.get('identical_work_group'):
        row['identical_work_group'] = desk['identical_work_group']
    if erow['series_role'] == 'contrast':
        row.update(template=rrow['contrast']['template'], arm=rrow['contrast']['arm'], stage=rrow['contrast']['stage'])
        if desk is not None and 'pilot7_token_identical' in desk:
            row['pilot7_token_identical'] = desk['pilot7_token_identical']
    if erow['condition'] == 'benign' and meter:
        row['dc_streams'] = [dict(m) for m in meter]
        row['member_span_ns'] = [episode['start_ns'], episode['end_ns']]
    codes = list(battery.get('flags', []))
    if battery.get('status') != 'observed':
        codes.append('battery.unobserved')
    return row, dict(battery=codes, cohort=dict(identity=identity, configuration=configuration),
                     tokens_sha=ident), census


# ---------------------------------------------------------------------------------------------- windows

_JOURNAL = {}


def _battery_init(path):
    from joulewise.align.apple import v4_battery
    _JOURNAL['journal'] = v4_battery.load_journal(path) if path else ([], None, 1)


def _battery_job(bundle):
    from joulewise.align.apple import v4_battery
    return v4_battery.bundle_evidence(bundle, _JOURNAL['journal'])


def battery_evidence(bundles, journal_path):
    """Production v4_battery.bundle_evidence per member (the desk's own join), in a process pool: the join scans
    the whole window journal per member, which is most of the export time. Output order = input order."""
    if not bundles:
        return []
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    workers = max(1, min(8, len(bundles), (os.cpu_count() or 2) - 1))
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn'),
                             initializer=_battery_init, initargs=(str(journal_path) if journal_path else None,)) as pool:
        return list(pool.map(_battery_job, [str(b) for b in bundles]))

def terminal_evidence(record, session, custody_rel):
    """The committed night result, cross-checked with chain.exited, courier.sent and (when restored) the custody
    bytes. Returns the verified result.json bytes; never a derived document."""
    try:
        raw = record.source('result', json_value=False)
        exited = record.source('chain_exited')
        record.source('courier_sent', json_value=False)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise Refused('terminal_evidence_missing', str(exc)) from None
    result = strict_loads(raw, 'terminal_evidence_mismatch')
    require(isinstance(result, dict) and result.get('schema') == RESULT_SCHEMA and isinstance(result.get('verdict'), str)
            and type(result.get('chain_exit_code')) is int, 'terminal_evidence_mismatch', 'result shape')
    require(isinstance(exited, dict) and exited.get('exit_code') == result['chain_exit_code'],
            'terminal_evidence_mismatch', 'chain.exited')
    if session is not None:
        require(session.read(f'{custody_rel}/night/result.json', missing='terminal_evidence_missing') == raw,
                'terminal_evidence_mismatch', 'custody result.json')
    return raw


def export_window(config, entry, stage, allocation):
    record, evidence = open_record(config, entry)
    try:
        return _export_window(config, entry, stage, allocation, record, evidence)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        if isinstance(exc, Refused):
            raise
        raise Refused('record_unreadable', f'{type(exc).__name__}: {exc}') from None


def _export_window(config, entry, stage, allocation, record, evidence):
    from joulewise.align.apple import v4_battery, v4_contention
    slot, attempt = ATTEMPT.match(entry['attempt_id']).groups()
    role = 'W1' if slot == 'W1' else 'calibration' if slot[0] == 'C' else 'test'
    require(record.record['role'] == {'W1': 'development'}.get(role, role), 'record_window_differs', 'role')
    why = record.final_evidence()
    require(why is None, 'record_not_final', why or '')
    captured = record.captures()                     # authenticated, covers every planned member
    roster = record.roster()
    declared = record.record.get('barred')
    require(declared is None or declared in DECLARED_BARS, 'unknown_contract_key', 'barred')
    rec_wid = slot if captured else f'{slot}-z{attempt}'
    if declared is not None:
        require(captured and declared == record.structural_bar(True), 'declared_bar_inconsistent', str(declared))
    engine_roster, rec_members = build_roster(slot, roster, allocation)
    # Final adjudication codes (WindowRecord.eligibility: contention is disclosure-only, R22-1).
    exclusions = record.source('exclusions') if record.has_final_sources() else {'members_excluded': []}
    excluded = {r['run_id']: v4_contention.split_codes(r['codes'])[0] for r in exclusions['members_excluded']}
    require(set(excluded) <= {r['run_id'] for r in roster}, 'roster_differs_from_plan', 'exclusions')
    thermal_desk = record.thermal(validate_reports=False) if captured else None
    desk_members = {m['id']: m for m in (thermal_desk or {}).get('members', [])}
    w = Writer(stage)
    session = None
    custody_rel = runs_rel = None
    census = []
    manifest_sha = record.finalized_manifest_sha256
    if captured:
        require(entry.get('session_root') is not None, 'session_unavailable', 'captured attempt needs session_root')
        finalized = evidence.source(record.commit, record.record['finalized_manifest'])
        require(finalized['source_root'] == entry['session_root'], 'session_root_differs', entry['session_root'])
        session = Session(entry['session_root'], finalized)
        state = strict_loads(session.read('session.json', missing='session_unavailable'), 'session_unavailable')
        series = state.get('v4_series')
        require(isinstance(series, dict) and set(series) <= V4_SERIES_KEYS, 'unknown_contract_key', 'v4_series')
        require(series.get('window_id') == slot and series.get('manifest_sha256') == ALLOCATION_SHA256,
                'session_window_differs', str(series.get('window_id')))
        runs_rel = session.relative(state['runs_roots']['claim'])
        custody_rel = session.relative(state['inputs']['custody_root'])
        plan_raw = session.read(session.relative(state['plan_path']), missing='session_unavailable')
        require(plan_raw == record.source('plan', json_value=False), 'roster_differs_from_plan', 'night plan')
        battery_path = None
        if session.has(f'{custody_rel}/hazards/monitor/battery.jsonl'):
            battery_path, _, _ = session.verify_file(f'{custody_rel}/hazards/monitor/battery.jsonl')
        meter = []
        if session.has(f'{custody_rel}/night/hazard_result.json'):
            hazard = strict_loads(session.read(f'{custody_rel}/night/hazard_result.json'), 'meter_custody_invalid')
            for s in (hazard.get('meter') or {}).get('streams') or []:
                require(isinstance(s, dict) and isinstance(s.get('path'), str) and HEX64.match(s.get('sha256') or ''),
                        'meter_custody_invalid', 'stream row')
                path, digest, _ = session.verify_file(f'{custody_rel}/{s["path"]}')
                require(digest == s['sha256'], 'digest_mismatch', s['path'])
                name = PurePosixPath(s['path']).name
                placed = w.place(f'recompute/windows/{rec_wid}/meter/{name}', path, digest)
                census.append(dict(placed, origin=f'{session.root}/{custody_rel}/{s["path"]}'))
                meter.append(placed)
    # Terminal evidence: every captured C attempt (both layouts, by digest; never inline).
    terminal = None
    if captured and slot[0] == 'C':
        raw = terminal_evidence(record, session, custody_rel)
        terminal = w.bytes(f'recompute/windows/{rec_wid}/terminal_result.json', raw)
        census.append(dict(terminal, origin=f'{session.root}/{custody_rel}/night/result.json'))
    # Members.
    plan_raw = record.source('collection_plan', json_value=False)
    plan_owner_check(strict_loads(plan_raw, 'config_digest_not_planned:wrong_window'), slot, f'{slot}#{attempt}')
    plan_ref = w.bytes(f'recompute/windows/{rec_wid}/collection_plan.json', plan_raw)
    census.append(dict(plan_ref, origin=f"git:{record.commit}:{record.record['sources']['collection_plan']['path']}"))
    by_ordinal = {}
    for r in roster:
        require(r.get('ordinal') not in by_ordinal, 'config_digest_not_planned', 'duplicate plan ordinal')
        by_ordinal[r.get('ordinal')] = r
    batteries = {}
    if captured:
        planned = [e['run_id'] for e in engine_roster if record.record['captures'][e['run_id']] is not None]
        for rid in planned:      # the bundle and the files the join reads must be custody before any join runs
            for name in ('metadata.json', 'events.jsonl'):
                session.read(f'{runs_rel}/{rid}/{name}')
        batteries = dict(zip(planned, battery_evidence([session.path(f'{runs_rel}/{rid}') for rid in planned],
                                                       battery_path)))
    engine_members, battery_codes, crosswalk = [], {}, []
    rec_rows, cohorts = [], {}
    for erow, rrow in zip(engine_roster, rec_members):
        local = erow['run_id']
        is_anchor = erow['series_role'] == 'anchor'
        erow = dict(erow, run_id_export=f'{slot}:{local}' if is_anchor else local,
                    exclusion_codes=excluded.get(local, []))
        rrow = dict(rrow, run_id=f'{rec_wid}:{local}' if is_anchor else local)
        capture = record.record['captures'][local]
        bundle_rel = f'{runs_rel}/{local}' if runs_rel is not None else None
        has_plist = session is not None and session.has(f'{bundle_rel}/raw/powermetrics.plist')
        require(capture is not None or not has_plist, 'capture_missing_from_record', local)
        if capture is None:
            engine_members.append(dict(run_id=erow['run_id_export'], captured=False,
                                       exclusion_codes=erow['exclusion_codes']))
            rrow['captured'] = False
        else:
            plan_row = by_ordinal.get(erow['ordinal'])
            require(plan_row is not None and plan_row.get('run_id') == local, 'config_digest_not_planned', local)
            kit_raw = planned_kit(config['kit_root'], plan_row)
            kit_ref = w.bytes(f'recompute/windows/{rec_wid}/kit/{local}.json', kit_raw)
            census.append(dict(kit_ref, origin=f"{config['kit_root']}/{plan_row['config_path']}"))
            rrow['planned_config'] = {'path': f'windows/{rec_wid}/kit/{local}.json', 'sha256': kit_ref['sha256']}
            row, meta, rows = member_export(session, bundle_rel, (erow, rrow), capture, rec_wid=rec_wid, slot=slot,
                                            w=w, battery=batteries[local], meter=meter, kit=(kit_raw, kit_ref),
                                            desk=desk_members.get(local))
            census.extend(rows)
            engine_members.append(row)
            battery_codes[rrow['run_id']] = meta['battery']
            cohorts[erow['ordinal']] = meta['cohort']
            rrow['captured'] = True
        rec_rows.append(rrow)
        crosswalk.append(dict(window=slot, attempt_id=f'{slot}#{attempt}', ordinal=erow['ordinal'],
                              engine_run_id=erow['run_id_export'], recompute_window_id=rec_wid,
                              recompute_run_id=rrow['run_id'], pair=rrow['pair'], condition=rrow['condition'],
                              model=rrow['model'], role=erow['series_role'], captured=rrow['captured'],
                              seed_index=erow['seed_index'], contrast=rrow.get('contrast')))
    # Identity: the committed desk's own token comparison of the registered replay pairs
    # (WindowRecord.eligibility rule, scripts/align_v4_next_arm_packet.py:383-386).
    by_ordinal = {r['ordinal']: r for r in rec_rows}
    pairs = ((5, 17), (6, 16), (9, 13), (7, 15), (10, 12)) if slot == 'W1' else ((5, 22),)
    identity = {}
    for e, r in zip(engine_roster, rec_rows):
        # A19: a W1 contrast run is eligible only if token-identical to its pilot-7 reference (the desk's
        # pilot7_token_identical, scripts/align_v4_thermal_desk.py:133, scripts/align_v4_session.py:333).
        d = desk_members.get(e['run_id']) or {}
        if e['series_role'] == 'contrast' and type(d.get('pilot7_token_identical')) is bool:
            identity[r['run_id']] = 'identical' if d['pilot7_token_identical'] else 'divergent'
    for a, b in pairs:
        da = desk_members.get(engine_roster[a - 1]['run_id']) if a <= len(engine_roster) else None
        db = desk_members.get(engine_roster[b - 1]['run_id']) if b <= len(engine_roster) else None
        if da and db and da.get('tokens') is not None and db.get('tokens') is not None:
            rid = by_ordinal[b]['run_id']
            if da['tokens'] != db['tokens']:
                identity[rid] = 'divergent'
            else:
                identity.setdefault(rid, 'identical')
    raw_doc = w.bytes(f'engine/windows/{rec_wid}/raw.json', canonical(dict(members=engine_members)))
    census.append(dict(raw_doc, origin=None))
    if slot == 'W1':
        require(5 in cohorts, 'cohort_unbound', 'W1 ordinal 5 not captured')
        series_cohort = cohorts[5]
    else:
        w1_state = _state_for(Path(config['export_root']), config['windows'][0])
        require(w1_state is not None and w1_state['slot'] == 'W1', 'window_order_gap', 'W1 must land first')
        series_cohort = w1_state['cohort']
    window_doc = {'schema': 'joulewise.v4_recompute_input.window.v1', 'window_id': rec_wid, 'role': role,
                  'cohort_sha256': cohort_sha256(series_cohort['identity'], series_cohort['configuration']),
                  'members': rec_rows,
                  'adjudication': {'final': True, 'excluded': {r['run_id']: excluded[e['run_id']] for r, e in
                                                               zip(rec_rows, engine_roster) if excluded.get(e['run_id'])}},
                  'identity': identity, 'battery': battery_codes,
                  'meter': {'streams': {PurePosixPath(m['path']).name: m['sha256'] for m in (meter if captured else [])}}}
    if slot == 'W1':
        window_doc['sentinel_ordinals'] = list(W1_SENTINEL_ORDINALS)
    if role == 'calibration':
        window_doc['slot'] = slot
    window_doc['plan_source'] = {'path': f'windows/{rec_wid}/collection_plan.json', 'sha256': plan_ref['sha256']}
    if terminal is not None:
        window_doc['terminal_result_source'] = {'path': f'windows/{rec_wid}/terminal_result.json',
                                                'sha256': terminal['sha256']}
    if declared is not None:
        window_doc['barred'] = declared
    ewin = dict(window=slot, attempt_id=f'{slot}#{attempt}', status='final',
                roster=[{k: (e['run_id'] if k == 'run_id' and e['series_role'] != 'anchor' else
                             f'{slot}:{e["run_id"]}' if k == 'run_id' else v) for k, v in e.items()}
                        for e in engine_roster], raw_source=raw_doc)
    ewin['plan_source'] = plan_ref
    if terminal is not None:
        ewin['terminal_result_source'] = terminal
    if declared is not None:
        ewin['barred'] = declared
    w.bytes(f'recompute/windows/{rec_wid}/window.json', canonical(window_doc))
    extra = {}
    if slot == 'W1':
        # Series cohort: the W1 capture member (ordinal 5), bound to the registered U3 bar's D configuration digest.
        extra['cohort'] = series_cohort
        sentinels = {}
        for o in W1_SENTINEL_ORDINALS:
            d = desk_members.get(engine_roster[o - 1]['run_id']) or {}
            if type(d.get('turn_owned_j')) in (int, float):
                sentinels[str(o)] = d['turn_owned_j']
        extra['w1_sentinel_j'] = sentinels
    state = dict(schema=STATE_SCHEMA, attempt_id=f'{slot}#{attempt}', slot=slot, recompute_window_id=rec_wid,
                 role=role, record=dict(commit=record.commit, path=entry['record_path'], sha256=record.sha256,
                                        finalized_manifest_sha256=manifest_sha),
                 engine_window=ewin, crosswalk=crosswalk, census=census,
                 manifest_slots=ewin['roster'], **extra)
    w.bytes(f'state/{rec_wid}.json', canonical(state))
    return rec_wid, state, w


def landed(stage, root, rec_wid):
    """Commit a staged window: absent -> move into place; present -> byte-identical (unchanged) or refuse."""
    stage, root = Path(stage), Path(root)
    staged = {p.relative_to(stage).as_posix(): sha256_file(p) for p in sorted(stage.rglob('*')) if p.is_file()}
    tops = [f'recompute/windows/{rec_wid}', f'engine/windows/{rec_wid}', f'state/{rec_wid}.json']
    present = [t for t in tops if (root / t).exists()]
    if present:
        require(len(present) == len(tops), 'window_already_exported_differs', rec_wid + ' partial')
        existing = {}
        for t in tops:
            p = root / t
            files = [p] if p.is_file() else sorted(x for x in p.rglob('*') if x.is_file())
            for f in files:
                existing[f.relative_to(root).as_posix()] = sha256_file(f)
        require(existing == staged, 'window_already_exported_differs', rec_wid)
        return 'unchanged'
    for t in tops:
        (root / t).parent.mkdir(parents=True, exist_ok=True)
        os.rename(stage / t, root / t)
    return 'exported'


# ----------------------------------------------------------------------------------------- series index

def series_inputs(config):
    from joulewise.align.apple import v4_u3
    bar = strict_loads(read_ref_file(config.get('u3_bar'), 'u3_bar_invalid'), 'u3_bar_invalid')
    require(isinstance(bar, dict) and isinstance(bar.get('pairs'), list) and isinstance(bar.get('policy'), dict),
            'u3_bar_invalid', 'shape')
    try:
        counts = v4_u3.policy_checks(bar['policy'])
        pilot = [p for p in bar['pairs'] if p.get('phase') == 'pilot']
        r1 = [p for p in bar['pairs'] if p.get('phase') == 'R1' and p.get('population') == 'D']
        require(len(r1) == 1 and len(pilot) + 1 == len(bar['pairs']), 'u3_bar_invalid', 'pair phases')
        relative = v4_u3.relative_pairs(pilot + r1)
    except ValueError as exc:
        raise Refused('u3_bar_invalid', str(exc)) from None
    signed = bar.get('status') == 'registered' and str(bar.get('lead_signature', '')).startswith('lead: ')
    refs = strict_loads(read_ref_file(config.get('r1_references'), 'r1_references_invalid'), 'r1_references_invalid')
    require(isinstance(refs, dict) and set(refs) == R1_KEYS and refs['schema'] == R1_REFERENCES_SCHEMA
            and isinstance(refs['designed_start_states'], list) and len(refs['designed_start_states']) == 3
            and all(isinstance(s, dict) and set(s) == R1_STATE_KEYS for s in refs['designed_start_states'])
            and isinstance(refs['r1_replay_pair_j'], list) and len(refs['r1_replay_pair_j']) == 2,
            'r1_references_invalid', 'shape')
    inputs = strict_loads(read_ref_file(config.get('registration_inputs'), 'registration_inputs_invalid'),
                          'registration_inputs_invalid')
    delta = (((inputs.get('R1') or {}).get('thermal_policy')) or {}).get('delta_slow_c')
    require(type(delta) in (int, float), 'registration_inputs_invalid', 'R1.thermal_policy.delta_slow_c')
    recompute_bar = {'signed': signed, 'beta': bar['policy']['series_alpha'], 'N': counts['30B'] + counts['D'],
                     'f': bar['policy']['d_transfer_factor'], 'pilot_relative_differences': relative[:-1],
                     'r1_d_screen': relative[-1]}
    engine_u3 = dict(pilot_pairs=[dict(session=p['session'], ordinals=p['ordinals'],
                                       prespecified=bar['policy']['selection'] == 'one_prespecified_pair_per_session',
                                       token_identical=p['token_identical'], energies_j=p['energies_j']) for p in pilot],
                     frozen_before_W1=signed,
                     r1_d_screen=dict(token_identical=r1[0]['token_identical'], eligible=r1[0].get('eligible') is True,
                                      relative_difference=relative[-1]))
    states = refs['designed_start_states']
    references = {'r1_replay_pair_j': refs['r1_replay_pair_j'], 'delta_slow_c': refs['delta_slow_c'],
                  'r1_designed_start_states': [dict(designed_slow_c=s['designed_slow_c'],
                                                    g0_release_slow_c=s['g0_release_slow_c'], energy_j=s['turn_owned_j'])
                                               for s in states]}
    sensitivity = dict(states=[dict(token_identical=s['token_identical'], g0_slow_c=s['g0_release_slow_c'],
                                    turn_owned_j=s['turn_owned_j'], designed_target_c=s['designed_slow_c']) for s in states],
                       r1_replay_j=refs['r1_replay_pair_j'], delta_slow_c=refs['delta_slow_c'])
    return dict(bar=bar, recompute_bar=recompute_bar, engine_u3=engine_u3, references=references,
                sensitivity=sensitivity, qualified=refs['qualified'], delta=delta)


def analysis_slots(slot, allocation, landed_slots):
    """Engine analysis-form slots: a landed window's exported roster; an unrun window from the frozen allocation,
    with production run ids (scripts/align_v4_series.py:38, :285; anchors keep the W1 kit ids)."""
    if slot in landed_slots:
        return landed_slots[slot]
    window = next(w for w in allocation['windows'] if w['id'] == slot)
    w1 = {r['ordinal']: r for r in landed_slots.get('W1', [])}
    rows = []
    for r in window['members']:
        o = r['ordinal']
        anchor = r['pool'] == 'anchor'
        local = (w1[o]['run_id'].split(':', 1)[1] if anchor and o in w1 else f'align-v4-{slot.lower()}-e{o:02}')
        rows.append(dict(ordinal=o, task_pair=r['pair'], condition=r['condition'], model_id=r['model_id'],
                         seed_index=r['seed_index'], expected_episode_seed=r['episode_seed'],
                         held_out=r['pool'] in ('calibration', 'known_h', 'test'),
                         series_role=r['pool'] if r['pool'] in ('anchor', 'sentinel')
                         else 'sabotage' if r['condition'] == 'sabotage' else 'benign',
                         run_id=f'{slot}:{local}' if anchor else local))
    return rows


def write_index(config, root, allocation_raw, allocation, states):
    root = Path(root)
    s = series_inputs(config)
    w1 = next((st for st in states if st['slot'] == 'W1'), None)
    require(w1 is not None, 'window_order_gap', 'W1 must land first')
    cohort = w1['cohort']
    d_sha = hashlib.sha256(json.dumps(cohort['identity'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    require(d_sha == s['bar']['policy'].get('d_configuration_sha256'), 'cohort_unbound', 'U3 d_configuration_sha256')
    landed_slots = {}
    for st in states:
        landed_slots[st['slot']] = st['manifest_slots']
    eman = dict(windows=[dict(window=slot, members=analysis_slots(slot, allocation, landed_slots)) for slot in R24_ORDER])

    def put(rel, raw):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name('.' + target.name + '.tmp')
        tmp.write_bytes(raw)
        os.replace(tmp, target)
        return {'path': rel, 'sha256': sha256_bytes(raw)}
    series_source = put('engine/series-manifest.json', canonical(eman))
    put('recompute/allocation/series_manifest.json', allocation_raw)
    payload = dict(schema=ENGINE_SCHEMA, cohort=cohort, windows=[st['engine_window'] for st in states],
                   series_source=series_source, u3_evidence=s['engine_u3'],
                   reference=dict(qualified=s['qualified'], r1_replay_j=s['references']['r1_replay_pair_j'],
                                  w1_sentinel_j=w1['w1_sentinel_j']),
                   r1_sensitivity=s['sensitivity'], delta_slow_c=s['delta'], u6_split_rule=U6_SPLIT_RULE,
                   custody='native export (scripts/export_v4_series.py); records ' + ','.join(
                       st['record']['sha256'][:12] for st in states))
    put('engine-input.json', canonical(payload))
    series = {'schema': 'joulewise.v4_recompute_input.series.v1',
              'windows': [{'window_id': st['recompute_window_id'], 'role': st['role']} for st in states],
              'h_star_grid': list(H_STAR_GRID),
              'allocation_source': {'path': 'allocation/series_manifest.json', 'sha256': ALLOCATION_SHA256}}
    put('recompute/series.json', canonical(series))
    put('recompute/u3_bar.json', canonical(s['recompute_bar']))
    put('recompute/references.json', canonical(s['references']))
    members = [row for st in states for row in st['crosswalk']]
    rec_anchor = [m['recompute_run_id'] for m in members if m['role'] == 'anchor']
    require(len(rec_anchor) == len(set(rec_anchor)), 'anchor_id_collision', 'recompute anchors')
    captured_ids = [(m['recompute_run_id']) for m in members if m['captured']]
    require(len(captured_ids) == len(set(captured_ids)), 'anchor_id_collision', 'captured member ids')
    put('crosswalk.json', canonical(dict(schema=CROSSWALK_SCHEMA, synthetic=False, members=members,
                                         export_notes=list(EXPORT_NOTES))))
    census = [row for st in states for row in st['census']]
    census += [dict(series_source, origin=None),
               {'path': 'recompute/allocation/series_manifest.json', 'sha256': ALLOCATION_SHA256,
                'origin': config['allocation']['path']}]
    put('census.json', canonical(dict(schema=CENSUS_SCHEMA, references=census)))
    return len(members), len(census)


EXPORT_NOTES = (
    'section 6a: production sensor keys policy.sensors.{s_fast, s_slow}; anchors <window>:<run_id> (engine: slot; '
    'recompute: record id, e.g. C3-z1); run ids are the collection plan ids',
    'raw files by digest: Episode JSON, powermetrics plist, config.json, KM003C streams, night result.json; the '
    'recompute projections add contract fields to production bytes and remove nothing',
    'identity_sha256 = sha256(canonical [[prompt_token_ids, output_token_ids], ...]) from align_turns.jsonl',
    'registered_span_ns = [first G0 start (else episode start), episode end] (WP22 rule)',
    'Episode.seed is carried verbatim (the seed index); config.json is a digest-bound member input (lead ruling a)',
)


# ------------------------------------------------------------------------------------------------ driver

def run(config_path, attempts):
    config = load_config(config_path)
    root = Path(config['export_root'])
    root.mkdir(parents=True, exist_ok=True)
    allocation_raw, allocation = frozen_allocation(config)
    order = [w['attempt_id'] for w in config['windows']]
    if attempts == 'all':
        attempts = order
    timings, results = {}, []
    for attempt in attempts:
        require(attempt in order, 'config_invalid', 'attempt not configured: ' + attempt)
        index = order.index(attempt)
        for prior in config['windows'][:index]:
            require(_state_for(root, prior) is not None, 'window_order_gap', prior['attempt_id'])
        stage = Path(tempfile_dir(root))
        started = time.monotonic()
        try:
            rec_wid, state, writer = export_window(config, config['windows'][index], stage, allocation)
            prior = root / 'state' / f'{rec_wid}.json'
            if prior.is_file():
                # Two attempts may never share a record id (series-unique anchors, section 6a).
                require(json.loads(prior.read_bytes()).get('attempt_id') == attempt, 'anchor_id_collision', rec_wid)
            outcome = landed(stage, root, rec_wid)
        finally:
            shutil.rmtree(stage, ignore_errors=True)
        timings[attempt] = time.monotonic() - started
        results.append(dict(attempt_id=attempt, window=rec_wid, outcome=outcome,
                            members=len(state['crosswalk']), captured=sum(r['captured'] for r in state['crosswalk']),
                            files=len(writer.files)))
    states = [st for st in (_state_for(root, w) for w in config['windows']) if st is not None]
    started = time.monotonic()
    members, census = write_index(config, root, allocation_raw, allocation, states)
    timings['index'] = time.monotonic() - started
    log = root / 'state' / 'timings.jsonl'
    with log.open('a') as fh:
        fh.write(json.dumps(dict(at_epoch_s=time.time(), windows_s=timings)) + '\n')
    return dict(status='exported', windows=results, landed=len(states), crosswalk_members=members,
                census_references=census)


def tempfile_dir(root):
    import tempfile
    return tempfile.mkdtemp(prefix='.stage-', dir=root)


def _state_for(root, entry):
    """The landed state of a configured attempt (its record id is not known before reading the record)."""
    slot, attempt = ATTEMPT.match(entry['attempt_id']).groups()
    for name in (slot, f'{slot}-z{attempt}'):
        p = Path(root) / 'state' / f'{name}.json'
        if p.is_file():
            st = json.loads(p.read_bytes())
            if st.get('attempt_id') == entry['attempt_id']:
                return st
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('export')
    p.add_argument('--config', type=Path, required=True)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--window', action='append', help='attempt id as configured (W1#1, C3#2, ...); repeatable')
    group.add_argument('--all', action='store_true')
    args = parser.parse_args(argv)
    try:
        out = run(args.config, 'all' if args.all else args.window)
        print(json.dumps(out, sort_keys=True))
        return 0
    except Refused as exc:
        print(json.dumps({'status': 'refused', 'code': exc.code}, sort_keys=True))
        print(f'refused: {exc.code}: {exc.detail}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
