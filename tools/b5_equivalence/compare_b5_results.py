#!/usr/bin/env python3
"""D-188 block-5 result-equivalence comparator (the acceptance gate for a restructured analysis).

    python3 -I -B tools/b5_equivalence/compare_b5_results.py [--mode blinded|open] REF_CUSTODY CAND_CUSTODY

Each side is a custody root that holds ``dry-run/`` (or ``release/`` with ``--run release``).
The verdict is EQUIVALENT exactly when every input-precondition (P), decision (D),
registered-number (R) and intermediate (I) leaf is token-identical between the two
trees; only audit (A) leaves may differ (docs/decision_log.md D-188).

Exit codes: 0 EQUIVALENT, 1 NOT_EQUIVALENT, 2 COMPARATOR_ERROR.

Independence: stdlib only; imports nothing from joulewise; reads its tier rules,
exemptions and open-mode index list from its OWN checkout (configs/analysis/b5/),
never from either tree. Run it from a separate clone at a comparator tag so the
candidate cannot alter its judge. The header prints this file's sha256 and the
config digests.

Blinded mode (default) prints only fixed grammar: tier MATCH/DIFFER lines and
sorted 'field <role>:<section>' names drawn from the tracked vocabulary V. It never
prints values, counts, list indices, ids, refusal codes or exception text. The full
valued report goes only to <CAND>/equivalence/restricted/ (mode 0600); the blinded
stdout is mirrored to <CAND>/equivalence/BLINDED-VERDICT.txt.

Open mode prints every differing leaf with both exact tokens. It refuses unless both
records' window_index_sha256 values are listed in equivalence_open_indices.json
(synthetic fixtures and the D-188 engineering window only).
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import stat
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
REPO_ROOT = SELF_PATH.parents[2]
CONFIG_DIR = REPO_ROOT / 'configs' / 'analysis' / 'b5'
TIERS_FILE = 'equivalence_tiers.json'
EXEMPTIONS_FILE = 'equivalence_exemptions.json'
OPEN_INDICES_FILE = 'equivalence_open_indices.json'

TIERS_SCHEMA = 'joulewise.b5_equivalence_tiers.v1'
EXEMPTIONS_SCHEMA = 'joulewise.b5_equivalence_exemptions.v1'
OPEN_INDICES_SCHEMA = 'joulewise.b5_equivalence_open_indices.v1'
REPORT_SCHEMA = 'joulewise.b5_equivalence_report.v1'
STEP_CODES_KEYS = frozenset({'pos', 'step', 'window', 'raw_code', 'exit_status', 'exception_class'})

RUNS = {'blind-dry-run': ('dry-run', 'B5-BLIND-DRY-RUN-RECORD.json'),
        'release': ('release', 'B5-RELEASE-RECORD.json')}
TIER_NAMES = {'P': 'inputs', 'D': 'decisions', 'R': 'registered', 'I': 'intermediate', 'A': 'audit'}
FAILING = 'PDRI'
WINDOWS = ('alpha', 'beta', 'gamma')

HEX64 = re.compile(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')
COMMIT40 = re.compile(r'[0-9a-f]{40}')
SAFE_KEY = re.compile(r'[A-Za-z_][A-Za-z0-9_\-]*')
SAFE_NAME = re.compile(r'[A-Za-z0-9_.@=+\-]+(/[A-Za-z0-9_.@=+\-]+)*')
LOG_NAME = re.compile(r'(\d{4,})-([0-9a-z]+)-(alpha|beta|gamma|block)\.stderr\.log')
VOCAB_NAME = re.compile(r'[a-z][a-z_\-/.]*:[A-Za-z_\-]+')
ROLE_CLASSES = ('attempts', 'brackets', 'custody', 'decisions', 'disclosures', 'finalized', 'kept-units',
                'mint', 'outputs', 'record', 'rereduced', 'step-eleven', 'supply-census')

# ---------------------------------------------------------------------------
# Hard-coded floors. equivalence_tiers.json may only TIGHTEN these: it must list
# every hard-coded P/D/R rule, and its audit rules must be a subset of the
# hard-coded audit allowances. No config or exemption can file a result as audit.
# Rules are (role glob, generic json-path glob); '[*]' stands for every list index.
# ---------------------------------------------------------------------------
HARD_INPUT_RECORD_PATHS = ('$.window_index_sha256', '$.sealed*', '$.windows[*].harvest_pin',
                           '$.windows[*].harvest_record_sha256', '$.mode', '$.schema_version')
HARD_INPUT_ROLES = ('finalized/inputs/*',)
HARD_DECISION = (
    ('decisions', '*'),
    ('record', '$.steps*'), ('record', '$.attempts*'), ('record', '$.windows[*].kept_counts*'),
    ('record', '$.windows[*].pack'), ('record', '$.windows[*].plan_id'),
    ('record', '$.completed_without_tooling_refusal'), ('record', '$.release_difference*'),
    ('attempts/*', '*'),
    ('kept-units/*', '$.cells*'),
    ('brackets/*', '$.evaluation.status'), ('brackets/*', '$.evaluation.acceptance*status*'),
    ('mint/extraction-*', '$.all_cells_extractable'), ('mint/extraction-*', '$.cells[*].extractable'),
    ('mint/extraction-*', '$.cells[*].refusal_reasons*'), ('mint/extraction-*', '$.cells[*].excluded_slots*'),
    ('mint/extraction-*', '$.cells[*].n_admitted'), ('mint/extraction-*', '$.cells[*].members[*].excluded'),
    ('mint/extraction-*', '$.cells[*].members[*].reasons*'), ('mint/extraction-*', '$.idle_admission_refusals*'),
    ('mint/extraction-*', '$.spec_membership_refusals*'),
    ('finalized/analysed-attempt-exclusions*', '*'),
    ('finalized/outputs/closeout.json', '$.branch'), ('finalized/outputs/closeout.json', '$.*_pass'),
    ('finalized/outputs/closeout.json', '$.*_licensed'), ('finalized/outputs/closeout.json', '$.refusal_reason'),
    ('finalized/outputs/closeout.json', '$.*ratios[*].passes'),
    ('finalized/outputs/closeout.json', '$.*ratios[*].status'),
    ('finalized/outputs/closeout.json', '$.*ratios[*].refusal_reason'),
    ('outputs/claim-verdicts.json', '$.contrasts[*].claim_evaluation*'),
    ('outputs/claim-verdicts.json', '$.bundle_audit[*].inclusion_status'),
    ('outputs/claim-verdicts.json', '$.bundle_audit[*].strict_status'),
    ('outputs/claim-verdicts.json', '$.bundle_audit[*].base_reason_codes*'),
    ('outputs/claim-verdicts.json', '$.bundle_audit[*].replacement_classification'),
    ('outputs/claim-verdicts.json', '$.sampling_audit*'),
    ('outputs/claim-verdicts.json', '$.families[*].structural_status'),
    ('outputs/projection-*', '$.refused_cells*'),
)
HARD_REGISTERED = (
    ('outputs/projection-*', '$.cells*'),
    ('*mint/aggregate-floor.json', '$.cells*'), ('*mint/aggregate-floor.json', '$.method*'),
    ('*mint/aggregate-floor.json', '$.transport_groups[*].composed_floor_*'),
    ('finalized/outputs/closeout.json', '*'), ('finalized/outputs/closeout.ratio-table.json', '$.ratios*'),
    ('outputs/claim-verdicts.json', '$.contrasts*'), ('outputs/claim-verdicts.json', '$.families*'),
    ('disclosures/*', '*'), ('outputs/results-fill-input.json', '*'),
    ('step-eleven/sensitivity', '*'), ('step-eleven/window-lines', '*'),
    ('brackets/block.json', '*'), ('mint/single-count.md', '*'),
)
ALLOWED_AUDIT_KEY_SUFFIXES = ('sha256', 'digest')
ALLOWED_AUDIT_KEYS = ('validator_source_sha256', 'binder_source_sha256', 'content_id', 'claim_verdicts_id',
                      'manifest_id', 'runs_root', 'runs_dir', 'relative_path', 'path', 'name', 'timestamp')
ALLOWED_AUDIT_ROLES = ('supply-census/*', 'custody/paper_custody_receipt*', 'custody/paper_custody_inventory*',
                       'step-eleven/index', 'logs/*', 'decisions-audit')
ALLOWED_AUDIT_RECORD_PATHS = ('$.input_census*', '$.steps[*].outputs*', '$.analysis_commit')
TIMING_POLICIES = ('strict', 'truncate')


class ComparatorError(Exception):
    def __init__(self, stage: str, side: str = 'both', detail: str = ''):
        super().__init__(f'{stage} {side} {detail}')
        self.stage, self.side, self.detail = stage, side, detail


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _glob(pattern: str) -> re.Pattern:
    return re.compile(fnmatch.translate(pattern.replace('[', '[[]')))


# ---------------------------------------------------------------------------
# Safe reads: never follow a symlink, regular files only.
# ---------------------------------------------------------------------------

def _open_dir(parent_fd, name, side, stage):
    try:
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except OSError as exc:
        raise ComparatorError(stage, side, f'directory {name!r}: {exc}') from None


def _read_beneath(dir_fd: int, rel: str, side: str, stage: str) -> bytes:
    if not SAFE_NAME.fullmatch(rel) or any(p in ('.', '..') for p in rel.split('/')):
        raise ComparatorError(stage, side, f'unsafe name {rel!r}')
    parts = rel.split('/')
    fd = os.dup(dir_fd)
    try:
        for part in parts[:-1]:
            nfd = _open_dir(fd, part, side, stage)
            os.close(fd)
            fd = nfd
        try:
            ffd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
        except OSError as exc:
            raise ComparatorError(stage, side, f'file {rel!r}: {exc}') from None
    finally:
        os.close(fd)
    try:
        if not stat.S_ISREG(os.fstat(ffd).st_mode):
            raise ComparatorError(stage, side, f'not a regular file {rel!r}')
        chunks = []
        while True:
            chunk = os.read(ffd, 1 << 20)
            if not chunk:
                break
            chunks.append(chunk)
        return b''.join(chunks)
    finally:
        os.close(ffd)


def _exists_beneath(dir_fd: int, rel: str) -> bool:
    parts = rel.split('/')
    fd = os.dup(dir_fd)
    try:
        for part in parts[:-1]:
            try:
                nfd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except OSError:
                return False
            os.close(fd)
            fd = nfd
        try:
            st = os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
        except OSError:
            return False
        return True if st else False
    finally:
        os.close(fd)


def read_own_bytes(path: Path, stage: str) -> bytes:
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        raise ComparatorError(stage, 'both', f'{path.name}: {exc}') from None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ComparatorError(stage, 'both', f'{path.name} is not a regular file')
        with os.fdopen(os.dup(fd), 'rb') as handle:
            return handle.read()
    finally:
        os.close(fd)


# ---------------------------------------------------------------------------
# Exact JSON: numbers keep their source text, so 1.0, 1 and -0.0 all differ.
# ---------------------------------------------------------------------------

def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate key')
        out[key] = value
    return out


def exact_json(raw: bytes):
    return json.loads(raw, parse_float=lambda t: ('#f', t), parse_int=lambda t: ('#i', t),
                      parse_constant=lambda t: ('#c', t), object_pairs_hook=_pairs)


def plain_json(raw: bytes):
    return json.loads(raw, object_pairs_hook=_pairs)


def show(token) -> str:
    if isinstance(token, tuple) and len(token) == 2 and token[0] in ('#f', '#i', '#c'):
        return token[1]
    if token is ABSENT:
        return '<absent>'
    return json.dumps(token, sort_keys=True, default=list)


class _Absent:
    def __repr__(self):
        return '<absent>'


ABSENT = _Absent()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    input_record_paths: list
    input_roles: list
    audit_record_paths: list
    audit_key_suffixes: list
    audit_keys: list
    decision: list
    audit_roles: list
    registered: list
    timing_codes: list
    timing_policy: str
    vocabulary: frozenset
    exemptions: list
    open_indices: frozenset
    digests: dict = field(default_factory=dict)

    def __post_init__(self):
        self._input_record = [_glob(p) for p in self.input_record_paths]
        self._input_roles = [_glob(p) for p in self.input_roles]
        self._audit_record = [_glob(p) for p in self.audit_record_paths]
        self._audit_roles = [_glob(p) for p in self.audit_roles]
        self._decision = [(_glob(r), _glob(p)) for r, p in self.decision]
        self._registered = [(_glob(r), _glob(p)) for r, p in self.registered]
        self._exempt = [(_glob(e['role']), _glob(e['path']), e['action']) for e in self.exemptions]
        suffixes = '|'.join(re.escape(s) for s in self.audit_key_suffixes)
        exact = '|'.join(re.escape(k) for k in self.audit_keys)
        parts = []
        if suffixes:
            parts.append(rf'(?:^|_)(?:{suffixes})$')
        if exact:
            parts.append(rf'^(?:{exact})$')
        self._audit_key = re.compile('|'.join(parts)) if parts else None
        self._cache = {}

    def is_input_role(self, role: str) -> bool:
        return any(g.match(role) for g in self._input_roles)

    def is_audit_role(self, role: str) -> bool:
        return any(g.match(role) for g in self._audit_roles)

    def base_tier(self, role: str, gpath: str, key) -> str:
        if role == 'record':
            if any(g.match(gpath) for g in self._audit_record):
                return 'A'
            if any(g.match(gpath) for g in self._input_record):
                return 'P'
        if self.is_input_role(role):
            return 'P'
        if key is not None and self._audit_key is not None and self._audit_key.search(key):
            return 'A'
        for r, p in self._decision:
            if r.match(role) and p.match(gpath):
                return 'D'
        if self.is_audit_role(role):
            return 'A'
        for r, p in self._registered:
            if r.match(role) and p.match(gpath):
                return 'R'
        return 'I'

    def tier(self, role: str, gpath: str, key) -> str:
        ck = (role, gpath, key)
        hit = self._cache.get(ck)
        if hit is not None:
            return hit
        base = self.base_tier(role, gpath, key)
        result = base
        for r, p, action in self._exempt:
            if action == 'audit' and r.match(role) and p.match(gpath):
                if base in 'PDR':
                    raise ComparatorError('exemptions', 'both', f'exemption touches {base} leaf {role} {gpath}')
                result = 'A'
        self._cache[ck] = result
        return result

    def unordered(self, role: str, gpath: str) -> bool:
        return any(action == 'unordered' and r.match(role) and p.match(gpath) for r, p, action in self._exempt)


def _need(cond, stage, detail):
    if not cond:
        raise ComparatorError(stage, 'both', detail)


def _string_list(value, stage, name):
    _need(isinstance(value, list) and all(isinstance(v, str) and v for v in value), stage, name)
    return list(value)


def _rule_list(value, stage, name):
    _need(isinstance(value, list) and all(isinstance(v, list) and len(v) == 2 and all(isinstance(x, str) and x for x in v)
                                          for v in value), stage, name)
    return [tuple(v) for v in value]


def load_config(config_dir: Path = CONFIG_DIR, *, timing_policy: str | None = None) -> Config:
    tiers_raw = read_own_bytes(config_dir / TIERS_FILE, 'config')
    exempt_raw = read_own_bytes(config_dir / EXEMPTIONS_FILE, 'exemptions')
    open_raw = read_own_bytes(config_dir / OPEN_INDICES_FILE, 'config')
    try:
        tiers, exempt, opened = plain_json(tiers_raw), plain_json(exempt_raw), plain_json(open_raw)
    except ValueError:
        raise ComparatorError('config', 'both', 'config is not strict JSON') from None
    _need(isinstance(tiers, dict) and tiers.get('schema_version') == TIERS_SCHEMA, 'config', 'tiers schema')
    t_keys = {'schema_version', 'description', 'input_record_paths', 'input_roles', 'audit_record_paths',
              'audit_key_suffixes', 'audit_keys', 'decision_rules', 'audit_roles', 'registered_rules',
              'timing_class_codes', 'timing_class_policy', 'vocabulary'}
    _need(set(tiers) == t_keys, 'config', 'tiers keys')
    inp = _string_list(tiers['input_record_paths'], 'config', 'input_record_paths')
    inp_roles = _string_list(tiers['input_roles'], 'config', 'input_roles')
    a_rec = _string_list(tiers['audit_record_paths'], 'config', 'audit_record_paths')
    a_suf = _string_list(tiers['audit_key_suffixes'], 'config', 'audit_key_suffixes')
    a_keys = _string_list(tiers['audit_keys'], 'config', 'audit_keys')
    a_roles = _string_list(tiers['audit_roles'], 'config', 'audit_roles')
    dec = _rule_list(tiers['decision_rules'], 'config', 'decision_rules')
    reg = _rule_list(tiers['registered_rules'], 'config', 'registered_rules')
    # The config may only tighten the hard-coded floors.
    _need(set(HARD_INPUT_RECORD_PATHS) <= set(inp), 'config', 'input_record_paths drop a hard-coded rule')
    _need(set(HARD_INPUT_ROLES) <= set(inp_roles), 'config', 'input_roles drop a hard-coded rule')
    _need(set(HARD_DECISION) <= set(dec), 'config', 'decision_rules drop a hard-coded rule')
    _need(set(HARD_REGISTERED) <= set(reg), 'config', 'registered_rules drop a hard-coded rule')
    _need(set(a_rec) <= set(ALLOWED_AUDIT_RECORD_PATHS), 'config', 'audit_record_paths widen the allowance')
    _need(set(a_suf) <= set(ALLOWED_AUDIT_KEY_SUFFIXES), 'config', 'audit_key_suffixes widen the allowance')
    _need(set(a_keys) <= set(ALLOWED_AUDIT_KEYS), 'config', 'audit_keys widen the allowance')
    _need(set(a_roles) <= set(ALLOWED_AUDIT_ROLES), 'config', 'audit_roles widen the allowance')
    codes = _string_list(tiers['timing_class_codes'], 'config', 'timing_class_codes')
    policy = tiers['timing_class_policy']
    _need(policy in TIMING_POLICIES, 'config', 'timing_class_policy')
    if timing_policy is not None:
        _need(timing_policy in TIMING_POLICIES, 'config', 'timing policy override')
        policy = timing_policy
    vocab = _string_list(tiers['vocabulary'], 'config', 'vocabulary')
    _need(all(VOCAB_NAME.fullmatch(v) and not re.search(r'[0-9]', v) for v in vocab), 'config', 'vocabulary grammar')
    _need(vocab == sorted(set(vocab)), 'config', 'vocabulary must be sorted and unique')
    _need(all(v.split(':', 1)[0].split('/', 1)[0] in ROLE_CLASSES for v in vocab), 'config', 'vocabulary role class')

    _need(isinstance(exempt, dict) and exempt.get('schema_version') == EXEMPTIONS_SCHEMA
          and set(exempt) == {'schema_version', 'description', 'exemptions'}
          and isinstance(exempt['exemptions'], list), 'exemptions', 'exemptions schema')
    rows = []
    for row in exempt['exemptions']:
        _need(isinstance(row, dict) and set(row) == {'role', 'path', 'action', 'reason'}, 'exemptions', 'row keys')
        _need(all(isinstance(row[k], str) and row[k].strip() for k in row), 'exemptions', 'row values')
        _need(row['action'] in ('audit', 'unordered'), 'exemptions', 'action')
        _need(row['role'] != 'record' and not row['role'].startswith('decisions'), 'exemptions', 'record role')
        _need(len(row['reason'].strip()) >= 12, 'exemptions', 'reason too short')
        # Static refusal: an exemption glob overlapping any hard P/D/R rule is refused
        # outright; the dynamic check in Config.tier catches every remaining leaf.
        for r, p in list(HARD_DECISION) + list(HARD_REGISTERED) + [(x, '*') for x in HARD_INPUT_ROLES]:
            if ((_glob(r).match(row['role']) or _glob(row['role']).match(r))
                    and (_glob(p).match(row['path']) or _glob(row['path']).match(p))):
                raise ComparatorError('exemptions', 'both', f'exemption overlaps protected rule {r} {p}')
        rows.append(dict(row))

    _need(isinstance(opened, dict) and opened.get('schema_version') == OPEN_INDICES_SCHEMA
          and set(opened) == {'schema_version', 'description', 'open_indices'}
          and isinstance(opened['open_indices'], list), 'config', 'open indices schema')
    idx = set()
    for row in opened['open_indices']:
        _need(isinstance(row, dict) and set(row) == {'window_index_sha256', 'label', 'reason'}
              and re.fullmatch(r'[0-9a-f]{64}', str(row['window_index_sha256']))
              and all(isinstance(row[k], str) and row[k].strip() for k in ('label', 'reason')), 'config', 'open index row')
        idx.add(row['window_index_sha256'])
    cfg = Config(inp, inp_roles, a_rec, a_suf, a_keys, dec, a_roles, reg, codes, policy, frozenset(vocab), rows,
                 frozenset(idx))
    cfg.digests = {'tiers': sha256(tiers_raw), 'exemptions': sha256(exempt_raw), 'open_indices': sha256(open_raw)}
    return cfg


# ---------------------------------------------------------------------------
# Loading one side: authenticate, assign roles by content and step
# ---------------------------------------------------------------------------

@dataclass
class Artifact:
    key: str           # unique pairing key (role, disambiguated)
    role: str          # rule role
    vocab: str         # printable role (blinded vocabulary)
    name: str          # restricted-relative name as committed
    raw: bytes
    pos: int           # serial position of the producing step


@dataclass
class Side:
    label: str
    root: Path
    record_raw: bytes
    record: dict
    artifacts: dict
    step_keys: list
    dmap: dict
    commit: str | None
    restricted_fd: int | None = None


def _strip_hex_name(name: str) -> str:
    n = HEX64.sub('', name)
    n = re.sub(r'-{2,}', '-', n)
    n = n.replace('/-', '/').replace('-.', '.')
    n = re.sub(r'/\.', '/artifact.', n)
    return n.rstrip('-')


def _window_of(text: str):
    for w in WINDOWS:
        if re.search(rf'(?<![a-z]){w}(?![a-z])', text):
            return w
    return None


def assign_role(step: str, window, name: str, raw: bytes, side: str):
    """Return (role, vocab). Roles never depend on a digest."""
    n = _strip_hex_name(name)
    if name.startswith('rereduced/'):
        parts = name.split('/')
        w = parts[1] if len(parts) == 3 and parts[1] in WINDOWS else (window or 'block')
        return f'rereduced/{w}/{_strip_hex_name(parts[-1])}', f'rereduced/{w}'
    if name.startswith('finalized/inputs/'):
        return n, 'finalized/inputs'
    if name.startswith('custody/registered-inputs/'):
        parts = n.split('/')
        return '/'.join(parts[:4]), '/'.join(parts[:4])
    if name.startswith('custody/') and n in ('custody/artifact.json',):
        try:
            d = plain_json(raw)
        except ValueError:
            raise ComparatorError('roles', side, f'custody artifact is not JSON: {name}') from None
        schema = d.get('schema_version') if isinstance(d, dict) else None
        if not isinstance(schema, str):
            raise ComparatorError('roles', side, f'custody artifact without schema_version: {name}')
        short = re.sub(r'\.v\d+$', '', schema.removeprefix('joulewise.'))
        short = re.sub(r'[^a-z_]', '_', short)
        fam = d.get('family')
        role = f'custody/{short}' + (f'/{re.sub(r"[^a-z_]", "_", fam)}' if isinstance(fam, str) else '')
        return role + (f'@{window}' if window else ''), role
    if step == '11' and n == 'outputs/artifact.json':
        try:
            d = plain_json(raw)
        except ValueError:
            raise ComparatorError('roles', side, 'step-11 output is not JSON') from None
        if isinstance(d, dict) and 'b_max' in d:
            r = 'step-eleven/sensitivity'
        elif isinstance(d, dict) and 'windows' in d and 'no_analysed_window_harvested_twice' in d:
            r = 'step-eleven/window-lines'
        elif isinstance(d, dict) and d and all(isinstance(v, dict) and set(v) == {'path', 'sha256'} for v in d.values()):
            r = 'step-eleven/index'
        else:
            r = 'step-eleven/unrecognised'
        return r, r
    if name.startswith('attempts/'):
        return n, f'attempts/{_window_of(n) or "other"}'
    return n, n


def _open_root(path: Path, side: str) -> int:
    try:
        return os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    except OSError as exc:
        raise ComparatorError('record', side, f'custody root: {exc}') from None


def _validate_record(record, side: str):
    def need(cond, detail):
        if not cond:
            raise ComparatorError('record', side, detail)
    need(isinstance(record, dict), 'record is not an object')
    for key in ('schema_version', 'mode', 'analysis_commit', 'window_index_sha256', 'steps', 'sealed',
                'attempts', 'windows', 'input_census', 'completed_without_tooling_refusal'):
        need(key in record, f'record lacks {key}')
    need(isinstance(record['steps'], list) and record['steps'], 'steps')
    for row in record['steps']:
        need(isinstance(row, dict), 'step row')
        for key in ('step', 'window', 'status', 'exit_status', 'outputs', 'refusal'):
            need(key in row, f'step row lacks {key}')
        need(isinstance(row['outputs'], list), 'outputs')
        for o in row['outputs']:
            need(isinstance(o, dict) and set(o) == {'name', 'sha256'} and isinstance(o['name'], str)
                 and isinstance(o['sha256'], str) and re.fullmatch(r'[0-9a-f]{64}', o['sha256']), 'output row')
    need(isinstance(record['input_census'], list), 'input_census')
    for row in record['input_census']:
        need(isinstance(row, dict) and isinstance(row.get('path'), str) and isinstance(row.get('sha256'), str),
             'census row')
    need(re.fullmatch(r'[0-9a-f]{64}', str(record['window_index_sha256'])), 'window_index_sha256')


def read_record(root: Path, run: str, side: str):
    run_dir, record_name = RUNS[run]
    root_fd = _open_root(root, side)
    try:
        run_fd = _open_dir(root_fd, run_dir, side, 'record')
    finally:
        os.close(root_fd)
    try:
        raw = _read_beneath(run_fd, record_name, side, 'record')
    except BaseException:
        os.close(run_fd)
        raise
    try:
        record = plain_json(raw)
    except ValueError:
        os.close(run_fd)
        raise ComparatorError('record', side, 'record is not strict JSON') from None
    try:
        _validate_record(record, side)
    except BaseException:
        os.close(run_fd)
        raise
    return run_fd, raw, record


def input_universe(record) -> set:
    universe = {row['sha256'] for row in record['input_census']}
    universe.add(record['window_index_sha256'])
    for value in (record.get('sealed') or {}).values():
        if isinstance(value, str):
            universe.add(value)
    for w in record.get('windows') or []:
        if isinstance(w, dict) and isinstance(w.get('harvest_record_sha256'), str):
            universe.add(w['harvest_record_sha256'])
    return universe


def load_side(root: Path, run: str, side: str, cfg: Config, *, run_fd=None, raw=None, record=None) -> Side:
    if run_fd is None:
        run_fd, raw, record = read_record(root, run, side)
    try:
        restricted_fd = _open_dir(run_fd, 'restricted', side, 'authenticate')
    finally:
        os.close(run_fd)
    artifacts, step_keys, dmap = {}, [], {}
    try:
        for pos, row in enumerate(record['steps']):
            keys = []
            for out in row['outputs']:
                name = out['name']
                data = _read_beneath(restricted_fd, name, side, 'authenticate')
                if sha256(data) != out['sha256']:
                    raise ComparatorError('authenticate', side, f'{name} does not match its committed sha256')
                role, vocab = assign_role(str(row['step']), row['window'], name, data, side)
                key = role
                if key in artifacts:
                    if not cfg.is_audit_role(role):
                        raise ComparatorError('roles', side, f'two result artifacts share role {role}')
                    n = 2
                    while f'{role}#{n}' in artifacts:
                        n += 1
                    key = f'{role}#{n}'
                artifacts[key] = Artifact(key, role, vocab, name, data, pos)
                keys.append(key)
                dmap.setdefault(out['sha256'], '@' + key)
            step_keys.append(keys)
    except BaseException:
        os.close(restricted_fd)
        raise
    for digest in input_universe(record):
        dmap.pop(digest, None)
    dmap[sha256(raw)] = '@record'
    commit = record.get('analysis_commit')
    commit = commit if isinstance(commit, str) and COMMIT40.fullmatch(commit) else None
    return Side(side, root, raw, record, artifacts, step_keys, dmap, commit, restricted_fd)


# ---------------------------------------------------------------------------
# Canonical flattening
# ---------------------------------------------------------------------------

class Flattener:
    def __init__(self, cfg: Config, side: Side):
        self.cfg, self.side = cfg, side
        commit = side.commit
        self._commit = re.compile(rf'(?<![0-9a-f]){commit}(?![0-9a-f])') if commit else None

    def canon(self, text: str) -> str:
        dmap = self.side.dmap
        out = HEX64.sub(lambda m: dmap.get(m.group(0), m.group(0)), text)
        if self._commit is not None:
            out = self._commit.sub('@analysis_commit', out)
        return out

    def canon_value(self, value):
        if isinstance(value, dict):
            return {self.canon(k): self.canon_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.canon_value(v) for v in value]
        if isinstance(value, str):
            return self.canon(value)
        return value

    def flatten(self, value, role, out, path='$', gpath='$', key=None, guard=None):
        cfg = self.cfg
        if isinstance(value, dict):
            if not value:
                t = cfg.tier(role, gpath, key)
                self._guard(guard, t, role, gpath)
                self._put(out, path, t, '{}')
            for k, v in value.items():
                ck = self.canon(k)
                seg = '.' + ck if SAFE_KEY.fullmatch(ck) else '[' + json.dumps(ck) + ']'
                self.flatten(v, role, out, path + seg, gpath + seg, k, guard)
        elif isinstance(value, list):
            gl = gpath + '[*]'
            t = cfg.tier(role, gl, key)
            self._guard(guard, t, role, gl)
            self._put(out, path + '[len]', t, ('#i', str(len(value))))
            items = value
            if cfg.unordered(role, gpath):
                base = cfg.base_tier(role, gl, key)
                if base != 'I':
                    raise ComparatorError('exemptions', 'both', f'unordered exemption on a {base} list {role} {gpath}')
                items = sorted(value, key=lambda v: json.dumps(self.canon_value(v), sort_keys=True, default=list))
                guard = (role, gpath)
            for i, v in enumerate(items):
                self.flatten(v, role, out, f'{path}[{i}]', gl, key, guard)
        else:
            t = cfg.tier(role, gpath, key)
            self._guard(guard, t, role, gpath)
            token = self.canon(value) if isinstance(value, str) else value
            self._put(out, path, t, token)
        return out

    def _put(self, out, path, tier, token):
        if path in out:
            # Two raw keys that canonicalize to one path would hide a leaf.
            raise ComparatorError('parse', self.side.label, f'canonical path collision {path}')
        out[path] = (tier, token)

    def _guard(self, guard, tier, role, gpath):
        if guard is not None and tier in 'PDR':
            raise ComparatorError('exemptions', 'both', f'unordered exemption covers a {tier} leaf {role} {gpath}')

    def artifact_leaves(self, art: Artifact):
        cfg = self.cfg
        if cfg.is_input_role(art.role):
            return {'$bytes': ('P', ('#sha256', sha256(art.raw)))}
        if art.name.endswith('.json'):
            try:
                value = exact_json(art.raw)
            except ValueError:
                raise ComparatorError('parse', self.side.label, f'{art.name} is not strict JSON') from None
            return self.flatten(value, art.role, {})
        text = art.raw.decode('utf-8', 'surrogateescape')
        return {'$text': (cfg.tier(art.role, '$text', None), self.canon(text))}


def section_of(path: str) -> str:
    if path in ('$text', '$bytes', '$presence'):
        return path[1:]
    m = re.match(r'\$(?:\.([A-Za-z_][A-Za-z0-9_\-]*)|\[("(?:[^"\\]|\\.)*")\]|\[(\d+|len)\])?', path)
    if not m or (m.group(1) is None and m.group(2) is None and m.group(3) is None):
        return 'value'
    if m.group(1) is not None:
        return m.group(1)
    if m.group(2) is not None:
        return json.loads(m.group(2))
    return 'items'


def field_name(cfg: Config, vocab: str, path: str) -> str:
    name = f'{vocab}:{section_of(path)}'
    if name in cfg.vocabulary:
        return name
    cls = vocab.split('/', 1)[0].split(':', 1)[0]
    return f'{cls if cls in ROLE_CLASSES else "unlisted"}:<unlisted>'


# ---------------------------------------------------------------------------
# Refusal identity
# ---------------------------------------------------------------------------

def _first_non_ok(record):
    for i, row in enumerate(record['steps']):
        if row['status'] not in ('ok', 'not_run'):
            return i, row
    return None, None


def read_step_codes(side: Side):
    if side.restricted_fd is None or not _exists_beneath(side.restricted_fd, 'decisions/step-codes.jsonl'):
        return None
    raw = _read_beneath(side.restricted_fd, 'decisions/step-codes.jsonl', side.label, 'step-codes')
    rows = []
    try:
        for line in raw.decode('utf-8').splitlines():
            if line.strip():
                rows.append(exact_json(line.encode()))
    except (ValueError, UnicodeDecodeError):
        raise ComparatorError('step-codes', side.label, 'step-codes.jsonl is not strict JSONL') from None
    steps = side.record['steps']
    if len(rows) != len(steps):
        raise ComparatorError('step-codes', side.label, 'row count differs from the record')
    for i, (row, st) in enumerate(zip(rows, steps)):
        if not isinstance(row, dict) or set(row) != STEP_CODES_KEYS:
            raise ComparatorError('step-codes', side.label, f'row {i} keys')
        exit_status = row['exit_status'][1] if isinstance(row['exit_status'], tuple) else row['exit_status']
        pos = row['pos'][1] if isinstance(row['pos'], tuple) else None
        if (pos != str(i) or row['step'] != st['step'] or row['window'] != st['window']
                or exit_status != (None if st['exit_status'] is None else str(st['exit_status']))):
            raise ComparatorError('step-codes', side.label, f'row {i} does not match the record')
        code = row['raw_code']
        if code is not None and not isinstance(code, str):
            raise ComparatorError('step-codes', side.label, f'row {i} raw_code')
        if st['status'] == 'tooling_refusal' and code != st['refusal']:
            raise ComparatorError('step-codes', side.label, f'row {i} tooling code differs from the record')
        if st['status'] in ('ok', 'not_run') and st['exit_status'] in (None, 0) and code is not None:
            raise ComparatorError('step-codes', side.label, f'row {i} ok step carries a code')
    return rows


DRIVER_TOKEN = re.compile(r'[A-Za-z][A-Za-z0-9_.]*')   # joulewise/b5_analysis/dry_run.py _TOKEN
MINT_CONSUMPTION_REFUSED = 'mint_consumption_session_refused'
DOMINANCE_ZERO_DENOMINATOR = 'dominance_ratio_zero_denominator'


def _driver_token(text: str):
    """dry_run.refusal_token: last 'error: ' line, else the last line; the part before ':'."""
    lines = text.splitlines()
    errors = [line[len('error: '):] for line in lines if line.startswith('error: ')]
    candidate = errors[-1] if errors else lines[-1] if lines else ''
    token = candidate.split(':', 1)[0]
    return token if DRIVER_TOKEN.fullmatch(token) else None


def _last_json_line(text: str):
    try:
        value = json.loads(text.splitlines()[-1])
    except (ValueError, IndexError):
        return None
    return value if isinstance(value, dict) else None


def legacy_refusal(side: Side, row) -> dict:
    """R1 layout: re-derive the driver's raw code for a refusing step from restricted logs.

    The record redacts outcome-class and unclassified codes (steps.step_record), so
    this replays the driver's own derivation on the step's LAST runner invocation:
    RunnerResult.token (stderr 'error:' line, else last stdout line), plus the step-5
    mint consumption label, the step-8 stdout REFUSE message and the step-6 stdout
    StepRecord. The invocation ordinal within the step pins which program stopped
    (step 5 runs two). A tooling code is public in the record and is taken from it.
    Driver-raised codes outside any runner program are persisted nowhere in R1; for
    those the derived value is whatever the last program left, identically derived
    on both sides.
    """
    if row['status'] == 'tooling_refusal':
        return {'raw_code': row['refusal'], 'invocation': None}
    want = (str(row['step']), row['window'] or 'block')
    try:
        logs_fd = os.open('logs', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=side.restricted_fd)
    except OSError:
        return {'raw_code': None, 'invocation': None}
    try:
        stems = []
        with os.scandir(logs_fd) as it:
            for entry in it:
                m = LOG_NAME.fullmatch(entry.name)
                if m and (m.group(2), m.group(3)) == want and entry.is_file(follow_symlinks=False):
                    stems.append((int(m.group(1)), entry.name[:-len('.stderr.log')]))
        if not stems:
            return {'raw_code': None, 'invocation': None}
        stems.sort()
        stem = stems[-1][1]
        stderr = _read_beneath(logs_fd, stem + '.stderr.log', side.label, 'refusal').decode('utf-8', 'replace')
        try:
            stdout = _read_beneath(logs_fd, stem + '.stdout.log', side.label, 'refusal').decode('utf-8', 'replace')
        except ComparatorError:
            stdout = ''
    finally:
        os.close(logs_fd)
    error_lines = [line for line in stderr.splitlines() if line.startswith('error: ')]
    code = _driver_token(stderr) if error_lines else _driver_token(stdout)
    step = str(row['step'])
    if step == '5' and any('authenticated whole-window consumption refused' in line for line in error_lines):
        code = MINT_CONSUMPTION_REFUSED
    elif step == '8':
        message = _last_json_line(stdout)
        if message is not None and set(message) == {'status', 'reason', 'detail'} and message['status'] == 'REFUSE' \
                and isinstance(message['reason'], str):
            code = _driver_token(message['reason'])
    elif step == '6':
        child = _last_json_line(stdout)
        closeout = sum(1 for o in row['outputs'] if re.fullmatch(r'finalized/outputs/closeout(\.ratio-table)?\.json',
                                                                 o['name']))
        if child is not None and child.get('status') == 'outcome_class' and row['exit_status'] == 3 and closeout == 2:
            code = DOMINANCE_ZERO_DENOMINATOR
        elif child is not None and child.get('status') == 'tooling_refusal' and isinstance(child.get('refusal'), str):
            code = _driver_token(child['refusal'])
    return {'raw_code': code, 'invocation': ('#i', str(len(stems)))}


def decision_structure(ref: Side, cand: Side, cfg: Config, prefix):
    """Derived decision leaves: per-step result outputs and the raw refusal identity."""
    codes_ref, codes_cand = read_step_codes(ref), read_step_codes(cand)
    source = 'step-codes' if codes_ref is not None and codes_cand is not None else 'logs'
    structures = {}
    for side, codes in ((ref, codes_ref), (cand, codes_cand)):
        steps = side.record['steps']
        limit = len(steps) if prefix is None else prefix
        outputs = [sorted(k for k in side.step_keys[i] if not cfg.is_audit_role(side.artifacts[k].role))
                   for i in range(min(limit, len(steps)))]
        d, audit = {'step_outputs': outputs}, {}
        if source == 'step-codes':
            d['step_codes'] = [{k: r[k] for k in ('pos', 'step', 'window', 'raw_code', 'exit_status')}
                               for r in codes[:limit]]
            audit['exception_class'] = [r['exception_class'] for r in codes[:limit]]
        elif prefix is None:
            i, row = _first_non_ok(side.record)
            d['first_refusal'] = None if row is None else {
                'pos': ('#i', str(i)), 'step': row['step'], 'window': row['window'], 'status': row['status'],
                'exit_status': row['exit_status'], 'registered_exit': row.get('registered_exit'),
                **legacy_refusal(side, row)}
        structures[side.label] = (d, audit)
    return structures, source


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

@dataclass
class Result:
    diffs: dict
    scope: str
    refusal_source: str
    sides: tuple

    @property
    def equivalent(self) -> bool:
        return not any(self.diffs[t] for t in FAILING)


def _timing_prefix(ref: Side, cand: Side, cfg: Config):
    if cfg.timing_policy != 'truncate':
        return None
    i, row = _first_non_ok(ref.record)
    if row is None or row['status'] != 'tooling_refusal' or row['refusal'] not in cfg.timing_codes:
        return None
    csteps = cand.record['steps']
    if i < len(csteps) and csteps[i]['status'] == row['status'] and csteps[i]['refusal'] == row['refusal']:
        return None
    return i


def _record_value(side: Side, prefix):
    rec = exact_json(side.record_raw)
    rec.pop('input_census', None)
    if prefix is not None:
        rec['steps'] = rec['steps'][:prefix]
        rec.pop('completed_without_tooling_refusal', None)
    return rec


def _census_map(record):
    m = {}
    for row in record['input_census']:
        m.setdefault((row.get('window'), row['path']), set()).add(row['sha256'])
    return m


def compare(ref: Side, cand: Side, cfg: Config) -> Result:
    diffs = {t: [] for t in 'PDRIA'}

    def add(tier, key, vocab, path, a, b):
        diffs[tier].append({'key': key, 'path': path, 'field': field_name(cfg, vocab, path), 'ref': a, 'cand': b})

    prefix = _timing_prefix(ref, cand, cfg)
    fa, fb = Flattener(cfg, ref), Flattener(cfg, cand)

    # Input preconditions from the census: same (window, path) -> same sha256; membership is audit.
    ca, cb = _census_map(ref.record), _census_map(cand.record)
    for k in sorted(set(ca) | set(cb), key=lambda x: (str(x[0]), x[1])):
        path = '$.input_census[' + json.dumps(f'{k[0]}:{k[1]}') + ']'
        if k in ca and k in cb:
            if ca[k] != cb[k]:
                add('P', 'record', 'record', path, sorted(ca[k]), sorted(cb[k]))
        else:
            add('A', 'record', 'record', path, sorted(ca.get(k, ())) or ABSENT, sorted(cb.get(k, ())) or ABSENT)

    # The analysis commit is canonicalized to @analysis_commit inside every artifact;
    # the record's own value is still reported (audit).
    if ref.record.get('analysis_commit') != cand.record.get('analysis_commit'):
        add('A', 'record', 'record', '$.analysis_commit', ref.record.get('analysis_commit'),
            cand.record.get('analysis_commit'))
    pairs = [('record', 'record', fa.flatten(_record_value(ref, prefix), 'record', {}),
              fb.flatten(_record_value(cand, prefix), 'record', {}))]

    def in_scope(side, key):
        return prefix is None or side.artifacts[key].pos < prefix

    ka = {k for k in ref.artifacts if in_scope(ref, k)}
    kb = {k for k in cand.artifacts if in_scope(cand, k)}
    for key in sorted(ka ^ kb):
        art = ref.artifacts.get(key) or cand.artifacts.get(key)
        # A missing or extra artifact is a decision difference (which step wrote what),
        # also for input copies; differing input-copy BYTES are an input difference.
        tier = 'A' if cfg.is_audit_role(art.role) else 'D'
        add(tier, key, art.vocab, '$presence', 'present' if key in ka else ABSENT, 'present' if key in kb else ABSENT)
    for key in sorted(ka & kb):
        a, b = ref.artifacts[key], cand.artifacts[key]
        pairs.append((key, a.vocab, fa.artifact_leaves(a), fb.artifact_leaves(b)))

    structures, source = decision_structure(ref, cand, cfg, prefix)
    (da, aa), (db, ab) = structures[ref.label], structures[cand.label]
    pairs.append(('decisions', 'decisions', fa.flatten(da, 'decisions', {}), fb.flatten(db, 'decisions', {})))
    pairs.append(('decisions-audit', 'decisions-audit', fa.flatten(aa, 'decisions-audit', {}),
                  fb.flatten(ab, 'decisions-audit', {})))

    for key, vocab, la, lb in pairs:
        for path in sorted(set(la) | set(lb)):
            ta, va = la.get(path, (None, ABSENT))
            tb, vb = lb.get(path, (None, ABSENT))
            if va == vb and ta == tb:
                continue
            tier = _strictest(ta, tb)
            add(tier, key, vocab, path, va, vb)
    return Result(diffs, 'full' if prefix is None else 'prefix', source, (ref, cand))


def _strictest(ta, tb):
    order = 'PDRIA'
    tiers = [t for t in (ta, tb) if t is not None]
    return min(tiers, key=order.index)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def header(mode: str, cfg: Config) -> str:
    return (f'B5-EQUIVALENCE {mode} tiers={cfg.digests["tiers"]} exemptions={cfg.digests["exemptions"]} '
            f'comparator={sha256(read_own_bytes(SELF_PATH, "config"))}')


def blinded_lines(result: Result, cfg: Config) -> list:
    lines = [header('blinded', cfg)]
    inputs_differ = bool(result.diffs['P'])
    for t in 'PDRI':
        name = TIER_NAMES[t]
        if t != 'P' and inputs_differ:
            lines.append(f'{name}: NOT_COMPARED')
            continue
        d = result.diffs[t]
        lines.append(f'{name}: ' + ('DIFFER' if d else 'MATCH'))
        for f in sorted({row['field'] for row in d}):
            lines.append(f'  field {f}')
    if inputs_differ:
        lines.append('audit: NOT_COMPARED')
    else:
        lines.append('audit: ' + ('DIFFER (not printed)' if result.diffs['A'] else 'MATCH'))
    lines.append(f'scope: {result.scope}')
    lines.append('VERDICT: ' + ('EQUIVALENT' if result.equivalent else 'NOT_EQUIVALENT'))
    return lines


def open_lines(result: Result, cfg: Config) -> list:
    lines = [header('open', cfg)]
    for t in 'PDRIA':
        d = result.diffs[t]
        lines.append(f'{TIER_NAMES[t]}: ' + ('DIFFER' if d else 'MATCH'))
        for row in d:
            lines.append(f'  {row["key"]} {row["path"]}: {show(row["ref"])} -> {show(row["cand"])}'
                         f'  [{row["field"]}]')
    lines.append(f'scope: {result.scope}')
    lines.append(f'refusal-source: {result.refusal_source}')
    lines.append('VERDICT: ' + ('EQUIVALENT' if result.equivalent else 'NOT_EQUIVALENT'))
    return lines


def _ensure_private_dir(parent: Path, name: str, mode: int) -> Path:
    path = parent / name
    try:
        os.mkdir(path, mode)
    except FileExistsError:
        pass
    st = os.lstat(path)
    if not stat.S_ISDIR(st.st_mode):
        raise ComparatorError('report', 'cand', f'{name} is not a directory')
    os.chmod(path, mode)
    return path


def _write_exclusive(directory: Path, stem: str, suffix: str, data: bytes, mode: int = 0o600) -> Path:
    for n in range(1, 1000):
        path = directory / (stem + ('' if n == 1 else f'.run{n}') + suffix)
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
        except FileExistsError:
            continue
        try:
            os.fchmod(fd, mode)
            os.write(fd, data)
        finally:
            os.close(fd)
        return path
    raise ComparatorError('report', 'cand', 'too many reports for this pair')


def equivalence_dirs(cand_root: Path):
    eq = _ensure_private_dir(cand_root, 'equivalence', 0o700)
    return eq, _ensure_private_dir(eq, 'restricted', 0o700)


def write_report(result: Result, cfg: Config, mode: str, lines: list) -> Path:
    ref, cand = result.sides
    eq, restricted = equivalence_dirs(cand.root)

    def tok(v):
        return '<absent>' if v is ABSENT else v
    report = {
        'schema_version': REPORT_SCHEMA, 'mode': mode, 'header': lines[0],
        'reference_record_sha256': sha256(ref.record_raw), 'candidate_record_sha256': sha256(cand.record_raw),
        'config_digests': cfg.digests, 'timing_class_policy': cfg.timing_policy,
        'scope': result.scope, 'refusal_source': result.refusal_source,
        'verdict': 'EQUIVALENT' if result.equivalent else 'NOT_EQUIVALENT',
        'stdout': lines,
        'differences': {TIER_NAMES[t]: [{**row, 'ref': tok(row['ref']), 'cand': tok(row['cand'])}
                                       for row in result.diffs[t]] for t in 'PDRIA'},
    }
    data = (json.dumps(report, indent=1, sort_keys=True, default=list) + '\n').encode()
    stem = f'{sha256(ref.record_raw)}-{sha256(cand.record_raw)}.{mode}'
    path = _write_exclusive(restricted, stem, '.json', data)
    if mode == 'blinded':
        tmp = eq / '.BLINDED-VERDICT.txt.tmp'
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
        try:
            os.write(fd, ('\n'.join(lines) + '\n').encode())
        finally:
            os.close(fd)
        os.replace(tmp, eq / 'BLINDED-VERDICT.txt')
    return path


def write_error(cand_root: Path, text: str):
    try:
        _eq, restricted = equivalence_dirs(cand_root)
        _write_exclusive(restricted, 'comparator-error', '.txt', text.encode('utf-8', 'replace'))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ComparatorError('args', 'both', message)


def run(argv, *, cfg: Config | None = None, out=None, err=None) -> int:
    out, err = out or sys.stdout, err or sys.stderr
    parser = _Parser(prog='compare_b5_results.py', add_help=True)
    parser.add_argument('ref', type=Path)
    parser.add_argument('cand', type=Path)
    parser.add_argument('--mode', choices=('blinded', 'open'), default='blinded')
    parser.add_argument('--run', choices=tuple(RUNS), default='blind-dry-run')
    parser.add_argument('--no-report', action='store_true',
                        help='open mode only: do not write <CAND>/equivalence/ (read-only fixtures)')
    mode, cand_root, sides = 'blinded', None, []
    try:
        a = parser.parse_args(argv)
        mode, cand_root = a.mode, a.cand
        if a.no_report and mode != 'open':
            raise ComparatorError('args', 'both', '--no-report is open mode only')
        cfg = cfg or load_config()
        ref_fd, ref_raw, ref_rec = read_record(a.ref, a.run, 'ref')
        sides.append(ref_fd)
        cand_fd, cand_raw, cand_rec = read_record(a.cand, a.run, 'cand')
        sides.append(cand_fd)
        if mode == 'open':
            for label, rec in (('ref', ref_rec), ('cand', cand_rec)):
                if rec['window_index_sha256'] not in cfg.open_indices:
                    raise ComparatorError('open-index', label, 'window index is not listed for open mode')
        sides.remove(ref_fd)  # load_side closes the run directory descriptor
        ref = load_side(a.ref, a.run, 'ref', cfg, run_fd=ref_fd, raw=ref_raw, record=ref_rec)
        sides.append(ref.restricted_fd)
        sides.remove(cand_fd)
        cand = load_side(a.cand, a.run, 'cand', cfg, run_fd=cand_fd, raw=cand_raw, record=cand_rec)
        sides.clear()
        try:
            result = compare(ref, cand, cfg)
        finally:
            for s in (ref, cand):
                os.close(s.restricted_fd)
        lines = blinded_lines(result, cfg) if mode == 'blinded' else open_lines(result, cfg)
        if not a.no_report:
            write_report(result, cfg, mode, lines)
        out.write('\n'.join(lines) + '\n')
        out.flush()
        return 0 if result.equivalent else 1
    except Exception as exc:
        for fd in sides:
            try:
                os.close(fd)
            except OSError:
                pass
        if isinstance(exc, ComparatorError):
            stage, side = exc.stage, exc.side
        else:
            stage, side = 'internal', 'both'
        if not re.fullmatch(r'[a-z\-]+', stage):
            stage = 'internal'
        text = traceback.format_exc()
        if mode == 'open':
            err.write(text)
        elif cand_root is not None and stage not in ('args',):
            write_error(cand_root, text)
        out.write(f'COMPARATOR_ERROR stage={stage} side={side}\n')
        out.flush()
        return 2


def emit_vocabulary(tree: Path, run: str = 'blind-dry-run', cfg: Config | None = None) -> list:
    """Vocabulary candidates (role:section) from one open-listed tree; digit-bearing names are dropped."""
    cfg = cfg or load_config()
    run_fd, raw, record = read_record(tree, run, 'ref')
    if record['window_index_sha256'] not in cfg.open_indices:
        os.close(run_fd)
        raise ComparatorError('open-index', 'ref', 'vocabulary may be drawn only from an open-listed tree')
    side = load_side(tree, run, 'ref', cfg, run_fd=run_fd, raw=raw, record=record)
    try:
        flat = Flattener(cfg, side)
        names = {f'record:{section_of(p)}' for p in flat.flatten(_record_value(side, None), 'record', {})}
        names |= {'record:input_census', 'decisions:step_outputs', 'decisions:first_refusal', 'decisions:step_codes'}
        for art in side.artifacts.values():
            names.add(f'{art.vocab}:presence')
            for p in flat.artifact_leaves(art):
                names.add(f'{art.vocab}:{section_of(p)}')
    finally:
        os.close(side.restricted_fd)
    audit_vocab = {a.vocab for a in side.artifacts.values() if cfg.is_audit_role(a.role)}
    return sorted(n for n in names if VOCAB_NAME.fullmatch(n) and not re.search(r'[0-9]', n)
                  and n.split(':', 1)[0].split('/', 1)[0] in ROLE_CLASSES
                  and n.split(':', 1)[0] not in audit_vocab and n != 'record:analysis_commit')


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ['--emit-vocabulary']:
        try:
            print(json.dumps(emit_vocabulary(Path(argv[1])), indent=1))
            return 0
        except (ComparatorError, IndexError) as exc:
            print(f'COMPARATOR_ERROR stage={getattr(exc, "stage", "args")} side={getattr(exc, "side", "both")}')
            return 2
    return run(argv)


if __name__ == '__main__':
    raise SystemExit(main())
