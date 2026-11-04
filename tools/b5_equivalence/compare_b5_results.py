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

Reference fields: a field that names another artifact by a digest, a content-derived
id, a hex-named path or an embedded copy carries the analysis commit of everything it
covers, so it is compared by VERIFIED REFERENT, not by value (REFERENCE SITES below).
On each side it must be self-consistent with its referent (recomputed canonical-JSON
and file digests, ids derived with the producer's own rule, embedded bytes equal to the
stored artifact, pinset digests recomputed from that side's producers, and the
unstored per-producer component floor artifacts rebuilt from the stored aggregate and
pinset exactly as the mint's own validator rebuilds them, then matched to their pinned
digest). A verified field becomes a fixed '@<kind>:<referent role>' token; its referent
is still compared leaf by leaf under the ordinary rules (a rebuilt component under the
aggregate floor's rules, as part of the pinset field that pins it). A field that is not
self-consistent is 'COMPARATOR_ERROR stage=reference side=<side>', never equivalent.

Blinded mode (default) prints only fixed grammar: tier MATCH/DIFFER lines and
sorted 'field <role>:<section>' names drawn from the tracked vocabulary V. It never
prints values, counts, list indices, ids, refusal codes or exception text. The full
valued report goes only to <CAND>/equivalence/restricted/ (mode 0600); the blinded
stdout is mirrored to <CAND>/equivalence/BLINDED-VERDICT.txt. A blinded run first
replaces that file with 'VERDICT: PENDING' and, on COMPARATOR_ERROR, with the error
line, so the exported file never outlives the run that wrote it.

Refusal identity: 'refusal-source' names where the raw refusal code came from.
'step-codes' is decisions/step-codes.jsonl committed by both records (authenticated);
'step-codes-unauthenticated' and 'logs-unauthenticated' (the R1 fallback) rest on
uncommitted restricted bytes being intact on the candidate side. A step-codes row
carries the refusal's position inside its step as decision fields: 'invocation' (the
refusing runner invocation's ordinal, as the R1 log decoder counts it) and 'member'
(a keyed digest of the refusing bundle, steps 1 and 2); neither is ever printed blinded.
When only one side carries step codes (an R1-format reference), the R1 log decoder
counts the legacy side's ordinal for every refusal, tooling ones included, and the
other side's step-codes ordinal and member are compared against it, never dropped.
R1 records no identity for a refusing step-1/step-2 bundle, so when that member is
all that could still differ the comparison fails closed:
'COMPARATOR_ERROR stage=refusal-member side=<the legacy side>'. Step codes are written
best-effort, so two legacy layouts from different analysis commits (an R1 reference
and a candidate whose sidecar write failed) fail closed the same way (side=ref); R1
against R1 (one commit) does not. A refusal outside any pack window (a driver-level
stop inside a per-window step) also carries 'window_children', the per-window child
log counts of its step, in every layout.
In those same comparisons (mixed, or legacy pairs from different commits) a
step-codes side's raw code is always its authenticated step-codes value, and a
legacy side's raw code is what its record and logs ESTABLISH under the driver's own
rules (_legacy_decode: a public tooling code, the one outcome-class code, an
escaped exception read from the runner's own traceback, or a program's own exit
other than 2). An exit-2 refusal without such a traceback could be a program exit,
a successful program missing a promised output or a driver-raised refusal that R1
records nowhere; when that raw code is all that could still differ the comparison
fails closed: 'COMPARATOR_ERROR stage=refusal-code side=<the legacy side>'.

Open mode prints every differing leaf with both exact tokens. It refuses unless both
records' window_index_sha256 values are listed in equivalence_open_indices.json
(synthetic fixtures and the D-188 engineering window only).
"""
from __future__ import annotations

import argparse
import base64
import binascii
import copy
import fnmatch
import hashlib
import itertools
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
STEP_CODES_NAME = 'decisions/step-codes.jsonl'
STEP_CODES_ROLE = 'decisions-audit/step-codes'
STEP_CODES_KEYS = frozenset({'pos', 'step', 'window', 'raw_code', 'exit_status', 'exception_class',
                             'invocation', 'member'})
# D-188 SHIP-FIX (finding C): the decision fields of a step-codes row. 'invocation'
# (the refusing runner invocation's ordinal within its (step, window), counted as
# legacy_refusal counts restricted logs) and 'member' (a keyed digest of the
# refusing bundle) pin WHERE inside a step a run refused, not only which step.
STEP_CODES_DECISION_KEYS = ('pos', 'step', 'window', 'raw_code', 'exit_status', 'invocation', 'member')
MEMBER_DIGEST = re.compile(r'[0-9a-f]{64}')

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
# Label keys never outrank a decision or registered rule: inside a D/R section a 'name'
# is a result label (contrasts[*].estimator.name, metric.name, bound and variance term
# names), so the audit-key rule applies to it only after the D and R rules have missed.
LABEL_AUDIT_KEYS = frozenset({'name'})
ALLOWED_AUDIT_ROLES = ('supply-census/*', 'custody/paper_custody_receipt*', 'custody/paper_custody_inventory*',
                       'step-eleven/index', 'logs/*', 'decisions-audit', 'decisions-audit/step-codes')
ALLOWED_AUDIT_RECORD_PATHS = ('$.input_census*', '$.steps[*].outputs*', '$.analysis_commit')
TIMING_POLICIES = ('strict', 'truncate')
PROTECTED_EXEMPTION_ROLES = ('record', 'decisions', 'decisions-audit', 'decisions-audit/step-codes')


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


EMPTY_OBJECT = ('#o', '{}')


def show(token) -> str:
    if isinstance(token, tuple) and len(token) == 2 and token[0] in ('#f', '#i', '#c', '#o'):
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
        exact = '|'.join(re.escape(k) for k in self.audit_keys if k not in LABEL_AUDIT_KEYS)
        parts = []
        if suffixes:
            parts.append(rf'(?:^|_)(?:{suffixes})$')
        if exact:
            parts.append(rf'^(?:{exact})$')
        self._audit_key = re.compile('|'.join(parts)) if parts else None
        self._label_keys = frozenset(k for k in self.audit_keys if k in LABEL_AUDIT_KEYS)
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
        if key in self._label_keys:
            return 'A'
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
        # Roles are globs: refuse any that can MATCH the record or the derived decision roles
        # ('reco?d', 'r*', 'decisions*'), not only the literal names.
        _need(not row['role'].startswith('decisions')
              and not any(_glob(row['role']).match(r) for r in PROTECTED_EXEMPTION_ROLES), 'exemptions', 'record role')
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
    if name == STEP_CODES_NAME:
        # Committed step codes are compared through the derived 'decisions' structure;
        # the raw bytes (which also carry the audit-only exception_class) are audit.
        return STEP_CODES_ROLE, STEP_CODES_ROLE
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
        self.references = {}    # referent key -> plain JSON value (resolve_references)
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
                # Tagged like a number, so an empty object never equals the string "{}".
                self._put(out, path, t, EMPTY_OBJECT)
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
            leaves = self.flatten(value, art.role, {})
            resolve_references(self, art, value, leaves)
            return leaves
        text = art.raw.decode('utf-8', 'surrogateescape')
        return {'$text': (cfg.tier(art.role, '$text', None), self.canon(text))}


# ---------------------------------------------------------------------------
# REFERENCE SITES: fields that name another artifact (D-188 result equivalence).
#
# The analysis commit is embedded in the floor artifacts (provenance.implementation),
# so every field that digests, derives an id from, path-names or embeds one of them
# differs between two analysis commits although nothing it covers differs once the
# commit is canonicalized. Such a field is equivalent iff on EACH side it is
# self-consistent with the artifact it references, and the referents compare
# equivalent under the ordinary rules. Each site below is verified on its own side and
# its token replaced by '@<kind>:<referent key>'; anything that does not verify raises
# ComparatorError('reference'). The referents are stored artifacts, compared as such,
# except the per-producer component floor artifacts, which custody does not store:
# those are rebuilt from the stored aggregate floor and pinset by the mint's own
# reconstruction (scripts/mint_floor_artifact_generalized.py
# _validate_v2_artifact_binding), matched to their pinned digest, and compared as
# extra leaves of the pinset field that pins them, under the aggregate floor's rules.
#
# Sites (producer in brackets; every rule is restated here, the judge imports nothing):
#   finalized/outputs/closeout.json $.sources.<name>.canonical_json_sha256 and .identity
#     [joulewise/dominance_closeout.py _validate_source_reference]
#   outputs/claim-verdicts.json $.inputs.analysis_manifest.{manifest_id,file_sha256},
#     $.inputs.floor_artifact.{artifact_id,file_sha256,embedded_bytes_base64}
#     [joulewise/analysis_engine/__init__.py claim-verdict body]
#   finalized/am.finalized.json $.manifest_id, $.evidence.aggregate_floor_artifact.{path,sha256}
#     [joulewise/analysis_manifest_v3.py calculate_manifest_id; the finalizer's evidence rows]
#   *mint/floor-mint-pinset.json $.aggregate.producer_set_sha256,
#     $.aggregate.component_artifacts[*].{sha256,producer_pin_sha256},
#     $.producer_plans[*].component_artifact.sha256 [scripts/emit_floor_mint_pinset.py _aggregate]
#   *mint/aggregate-floor.json (v2) $.provenance.calibration_plan.sha256
#     [scripts/mint_floor_artifact_generalized.py _build_v2_artifacts]
# ---------------------------------------------------------------------------

FINALIZED_MANIFEST_ROLE = 'finalized/am.finalized.json'
FINALIZED_FLOOR_ROLE = 'finalized/mint/aggregate-floor.json'
FINALIZED_REPLAY_ROLE = 'finalized/mint/dominance-replay.json'
CLOSEOUT_ROLE = 'finalized/outputs/closeout.json'
CLAIM_VERDICTS_ROLE = 'outputs/claim-verdicts.json'
PINSET_SUFFIX = 'mint/floor-mint-pinset.json'
AGGREGATE_SUFFIX = 'mint/aggregate-floor.json'
# closeout.sources.<name>: (referent role, the referent's identity key)
CLOSEOUT_SOURCES = {'finalized_manifest': (FINALIZED_MANIFEST_ROLE, 'manifest_id'),
                    'floor_artifact': (FINALIZED_FLOOR_ROLE, 'artifact_id'),
                    'replay_sidecar': (FINALIZED_REPLAY_ROLE, 'sidecar_id')}
CONTAINMENT_KEYS = ('mint_commit_contained_in_origin_main', 'head_pin_commit_contained_in_origin_main')
REBUILT = '<rebuilt>'


def canonical_json_sha256(value) -> str:
    """dominance_closeout.canonical_json_sha256 / mint._canonical_json_sha256 / the v3 manifest's canonical bytes."""
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                             allow_nan=False).encode('utf-8'))


def derived_manifest_id(value) -> str:
    """analysis_manifest_v3.calculate_manifest_id: 'am-' + canonical sha256 of the body without manifest_id."""
    body = dict(value)
    body.pop('manifest_id', None)
    return 'am-' + canonical_json_sha256(body)


def floor_artifact_sha256(value) -> str:
    """mint._artifact_sha256: the floor-artifact file payload (indent 2, sorted keys, trailing newline)."""
    return sha256((json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8'))


def rebuild_component(aggregate, pinset, index: int):
    """The index-th producer's component floor artifact, as mint._validate_v2_artifact_binding rebuilds it.

    The aggregate is component 0 with its artifact id, scope, provenance, cells and
    transport groups replaced (mint._build_v2_artifacts), so each component is the
    aggregate with that producer's own plan pin, config set and launch lineage, and
    only that producer's cells and groups. The mint-tool and assurance constants are
    taken from the aggregate's provenance (the mint writes the same constants into
    both); any deviation fails the pinned digest. Works on plain and exact JSON values.
    """
    producer = pinset['producer_plans'][index]
    pin = pinset['aggregate']['component_artifacts'][index]
    provenance = aggregate['provenance']
    plan = producer['plan']
    component = copy.deepcopy(aggregate)
    component['artifact_id'] = pin['artifact_id']
    rebuilt = {'calibration_plan': {k: plan[k] for k in ('plan_id', 'declared_calibration_scope', 'relative_path',
                                                          'sha256')},
               'mint_tool_version': provenance['mint_tool_version'],
               'assurance': copy.deepcopy(provenance['assurance']),
               'implementation': copy.deepcopy(provenance['implementation'])}
    cells = producer['cells']
    present = ['scientific_config_identity_sha256' in c for c in cells]
    if any(present):   # detection_floor.floor_mint_producer_config_set
        if not all(present):
            raise ValueError('partial per-cell config pins')
        rebuilt['producer_config_sets'] = [{
            'plan_id': plan['plan_id'], 'config_set_sha256': producer['model_runtime_config']['config_set_sha256'],
            'cells': [{'cell_id': c['cell_id'], 'scientific_config_identity_sha256': c['scientific_config_identity_sha256']}
                      for c in cells]}]
    if provenance.get('calibration_custody_store') is not None:
        rebuilt['calibration_custody_store'] = copy.deepcopy(provenance['calibration_custody_store'])
    lineage = provenance.get('launch_lineage')
    if 'producer_launch_lineages' in provenance:
        inventory = provenance['producer_launch_lineages']
        if [row['plan_id'] for row in inventory] != [p['plan']['plan_id'] for p in pinset['producer_plans']]:
            raise ValueError('producer lineage inventory')
        lineage = inventory[index].get('launch_lineage')
    if lineage is not None:
        rebuilt['launch_lineage'] = copy.deepcopy(lineage)
    component['provenance'] = rebuilt
    by_cell = {c['cell_id']: c for c in aggregate['cells']}
    by_group = {g['transport_group_id']: g for g in aggregate['transport_groups']}
    component['cells'] = [copy.deepcopy(by_cell[c['cell_id']]) for c in cells]
    component['transport_groups'] = [copy.deepcopy(by_group[c['transport_group_id']]) for c in cells]
    return component


def containment_variants(component):
    """mint._artifact_sha256_containment_variants: the two non-gating containment observations, every value."""
    implementation = component.get('provenance', {}).get('implementation')
    if not isinstance(implementation, dict) or any(k not in implementation for k in CONTAINMENT_KEYS):
        yield None
        return
    yield from itertools.product((False, True, None), repeat=len(CONTAINMENT_KEYS))


def _with_variant(component, variant):
    if variant is None:
        return component
    out = copy.deepcopy(component)
    for key, value in zip(CONTAINMENT_KEYS, variant):
        out['provenance']['implementation'][key] = value
    return out


class _References:
    """Verification of one artifact's reference sites against its own side."""

    def __init__(self, flat: 'Flattener', art: Artifact, leaves: dict):
        self.flat, self.side, self.art, self.leaves = flat, flat.side, art, leaves
        self.cache = flat.references

    def fail(self, detail: str):
        raise ComparatorError('reference', self.side.label, f'{self.art.key}: {detail}')

    def referent(self, role: str) -> Artifact:
        art = self.side.artifacts.get(role)
        if art is None or art.role != role:
            self.fail(f'referent {role} is not a committed output')
        return art

    def plain(self, art: Artifact):
        if art.key not in self.cache:
            try:
                self.cache[art.key] = plain_json(art.raw)
            except ValueError:
                self.fail(f'referent {art.key} is not strict JSON')
        return self.cache[art.key]

    def verified(self, path: str, value, expected, kind: str, referent: str):
        """Replace the leaf at ``path`` by '@kind:referent' when ``value`` is the string ``expected``."""
        self.require(isinstance(value, str) and value == expected, path, referent)
        self.token(path, kind, referent)

    def require(self, consistent: bool, path: str, referent: str):
        if not consistent:
            self.fail(f'{path} is not self-consistent with {referent}')

    def token(self, path: str, kind: str, referent: str):
        if path not in self.leaves:
            self.fail(f'{path} is not a scalar reference')
        tier, _token = self.leaves[path]
        self.leaves[path] = (tier, f'@{kind}:{referent}')

    def manifest_id(self, art: Artifact) -> str:
        value = self.plain(art)
        if not isinstance(value, dict) or value.get('manifest_id') != derived_manifest_id(value):
            self.fail(f'referent {art.key} manifest_id is not derived from its content')
        return value['manifest_id']


def _sub(value, *keys):
    for k in keys:
        if not isinstance(value, dict) or k not in value:
            return None
        value = value[k]
    return value


def resolve_references(flat: 'Flattener', art: Artifact, exact, leaves: dict):
    """Verify and canonicalize every reference site of ``art`` (see REFERENCE SITES)."""
    if not isinstance(exact, dict):
        return
    refs = _References(flat, art, leaves)
    try:
        value = refs.plain(art)
        if art.role == CLOSEOUT_ROLE:
            _closeout_sources(refs, value)
        elif art.role == CLAIM_VERDICTS_ROLE:
            _claim_verdict_inputs(refs, value)
        elif art.role == FINALIZED_MANIFEST_ROLE:
            _finalized_manifest(refs, value)
        elif art.role.endswith(PINSET_SUFFIX) and isinstance(_sub(value, 'aggregate', 'component_artifacts'), list):
            _pinset(refs, value, exact)
        elif (art.role.endswith(AGGREGATE_SUFFIX)
              and isinstance(_sub(value, 'provenance', 'producer_calibration_plans'), list)):
            _aggregate_floor(refs, value)
    except ComparatorError:
        raise
    except (KeyError, IndexError, TypeError, ValueError, AttributeError, binascii.Error) as exc:
        refs.fail(f'reference site is malformed: {type(exc).__name__}')


def _closeout_sources(refs: _References, value):
    sources = value.get('sources')
    if sources is None:
        return
    for name, (role, identity_key) in CLOSEOUT_SOURCES.items():
        ref = sources.get(name)
        if ref is None:
            continue
        target = refs.referent(role)
        body = refs.plain(target)
        base = f'$.sources.{name}'
        if 'canonical_json_sha256' in ref:
            refs.verified(f'{base}.canonical_json_sha256', ref['canonical_json_sha256'], canonical_json_sha256(body),
                          'canonical', target.key)
        if 'identity' in ref:
            identity = refs.manifest_id(target) if identity_key == 'manifest_id' else body.get(identity_key)
            refs.verified(f'{base}.identity', ref['identity'], identity, 'identity', target.key)


def _claim_verdict_inputs(refs: _References, value):
    manifest = _sub(value, 'inputs', 'analysis_manifest')
    if manifest is not None:
        target = refs.referent(FINALIZED_MANIFEST_ROLE)
        if 'manifest_id' in manifest:
            refs.verified('$.inputs.analysis_manifest.manifest_id', manifest['manifest_id'], refs.manifest_id(target),
                          'manifest-id', target.key)
        if 'file_sha256' in manifest:
            refs.verified('$.inputs.analysis_manifest.file_sha256', manifest['file_sha256'], sha256(target.raw),
                          'file', target.key)
    floor = _sub(value, 'inputs', 'floor_artifact')
    if floor is not None:
        target = refs.referent(FINALIZED_FLOOR_ROLE)
        base = '$.inputs.floor_artifact'
        if 'artifact_id' in floor:
            refs.verified(f'{base}.artifact_id', floor['artifact_id'], refs.plain(target).get('artifact_id'),
                          'identity', target.key)
        if 'file_sha256' in floor:
            refs.verified(f'{base}.file_sha256', floor['file_sha256'], sha256(target.raw), 'file', target.key)
        if 'embedded_bytes_base64' in floor:
            embedded = floor['embedded_bytes_base64']
            decoded = base64.b64decode(embedded, validate=True) if isinstance(embedded, str) else None
            # The embedded copy IS the referent (equal bytes), so it is compared as that artifact.
            refs.require(decoded == target.raw, f'{base}.embedded_bytes_base64', target.key)
            refs.token(f'{base}.embedded_bytes_base64', 'embedded', target.key)


def _finalized_manifest(refs: _References, value):
    if 'manifest_id' in value:
        refs.verified('$.manifest_id', value['manifest_id'], derived_manifest_id(value), 'manifest-id', refs.art.key)
    floor = _sub(value, 'evidence', 'aggregate_floor_artifact')
    if floor is None:
        return
    target = refs.referent(FINALIZED_FLOOR_ROLE)
    base = '$.evidence.aggregate_floor_artifact'
    if 'path' in floor:
        # Evidence paths are relative to the finalized manifest's own directory.
        directory = refs.art.name.rsplit('/', 1)[0]
        path = floor['path']
        refs.verified(f'{base}.path', f'{directory}/{path}' if isinstance(path, str) else None, target.name,
                      'path', target.key)
    if 'sha256' in floor:
        refs.verified(f'{base}.sha256', floor['sha256'], sha256(target.raw), 'file', target.key)


def _pinset(refs: _References, value, exact):
    producers = value['producer_plans']
    aggregate = value['aggregate']
    pins = aggregate['component_artifacts']
    if not isinstance(producers, list) or len(pins) != len(producers) or not producers:
        refs.fail('component pins do not match the producer plans')
    me = refs.art.key
    if 'producer_set_sha256' in aggregate:
        refs.verified('$.aggregate.producer_set_sha256', aggregate['producer_set_sha256'],
                      canonical_json_sha256(producers), 'producer-set', me)
    target = refs.referent(refs.art.role[:-len(PINSET_SUFFIX)] + AGGREGATE_SUFFIX)
    floor_plain = refs.plain(target)
    floor_exact = exact_json(target.raw)
    for i, (producer, pin) in enumerate(zip(producers, pins)):
        if pin.get('plan_id') != producer['plan']['plan_id']:
            refs.fail('component pin order differs from the producer plans')
        base = f'$.aggregate.component_artifacts[{i}]'
        if 'producer_pin_sha256' in pin:
            refs.verified(f'{base}.producer_pin_sha256', pin['producer_pin_sha256'], canonical_json_sha256(producer),
                          'producer-pin', me)
        component = rebuild_component(floor_plain, value, i)
        matched = [v for v in containment_variants(component)
                   if floor_artifact_sha256(_with_variant(component, v)) == pin['sha256']]
        refs.require(len(matched) == 1, f'{base}.sha256', f'{target.key}{REBUILT}')
        # The token keeps the matched containment observation (the only rebuilt bytes not in the aggregate).
        token = f'{target.key}{REBUILT}' + ('' if matched[0] is None else json.dumps(list(matched[0])))
        refs.token(f'{base}.sha256', 'component', token)
        refs.verified(f'$.producer_plans[{i}].component_artifact.sha256', producer['component_artifact']['sha256'],
                      pin['sha256'], 'component', token)
        # Compare the rebuilt component itself (commit canonicalized), under the aggregate's rules.
        rebuilt = _with_variant(rebuild_component(floor_exact, exact, i), matched[0])
        for path, leaf in refs.flat.flatten(rebuilt, target.role, {}).items():
            refs.leaves[f'{base}.sha256{REBUILT}{path[1:]}'] = leaf


def _aggregate_floor(refs: _References, value):
    plan = _sub(value, 'provenance', 'calibration_plan')
    if plan is None or 'sha256' not in plan:
        refs.fail('v2 aggregate without a plan-set pin')
    pinset = refs.referent(refs.art.role[:-len(AGGREGATE_SUFFIX)] + PINSET_SUFFIX)
    producers = refs.plain(pinset)['producer_plans']
    refs.verified('$.provenance.calibration_plan.sha256', plan['sha256'], canonical_json_sha256(producers),
                  'producer-set', pinset.key)


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
    """Return (rows, authenticated) or (None, False).

    Authenticated when the record commits decisions/step-codes.jsonl as a step output
    (its bytes were checked against the committed sha256 in load_side); otherwise the
    file is read from disk and the refusal source is reported as unauthenticated.
    """
    committed = [a for a in side.artifacts.values() if a.name == STEP_CODES_NAME]
    if committed:
        raw, authenticated = committed[-1].raw, True
    elif side.restricted_fd is None or not _exists_beneath(side.restricted_fd, STEP_CODES_NAME):
        return None, False
    else:
        raw, authenticated = _read_beneath(side.restricted_fd, STEP_CODES_NAME, side.label, 'step-codes'), False
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
        invocation, member = row['invocation'], row['member']
        if invocation is not None and not (isinstance(invocation, tuple) and invocation[0] == '#i'
                                           and re.fullmatch(r'[1-9][0-9]*', invocation[1])):
            raise ComparatorError('step-codes', side.label, f'row {i} invocation')
        if member is not None and not (isinstance(member, str) and MEMBER_DIGEST.fullmatch(member)):
            raise ComparatorError('step-codes', side.label, f'row {i} member')
        if st['status'] in ('ok', 'not_run') and (invocation is not None or member is not None):
            raise ComparatorError('step-codes', side.label, f'row {i} ok step carries a position')
    return rows, authenticated


DRIVER_TOKEN = re.compile(r'[A-Za-z][A-Za-z0-9_.]*')   # joulewise/b5_analysis/dry_run.py _TOKEN
MINT_CONSUMPTION_REFUSED = 'mint_consumption_session_refused'
DOMINANCE_ZERO_DENOMINATOR = 'dominance_ratio_zero_denominator'
# configs/analysis/b5/dry_run_refusal_classes.json 'outcome_class', identical at
# b5/analysis-r1 and on this branch (the two files differ by one tooling code). A
# record row whose status is outcome_class therefore carries exactly this raw code
# (steps.step_record maps a code to outcome_class only when it is listed there).
# Embedded, not read, so the judge depends on no file the analysis may change.
OUTCOME_CODES = (DOMINANCE_ZERO_DENOMINATOR,)
CODE_UNESTABLISHED = '<raw-code-not-established-in-legacy-layout>'
_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
_TRACEBACK_HEAD = re.compile(r'(  \+ )?(?:Exception Group )?Traceback \(most recent call last\):')
_DRIVER_RUN_FRAME = re.compile(r'  File "[^"\n]*[/\\]joulewise[/\\]b5_analysis[/\\]dry_run\.py", line [0-9]+, in run')
# The outermost frame of a traceback printed by dry_run (r1 and this branch alike):
# StepRunner.run's catch of an exception that escaped the program, or the module
# run() loop's exception program (def fail: traceback.print_exc(); return 2).
RUNNER_ESCAPE_SOURCE = 'value = main(list(argv))'
DRIVER_FAIL_SOURCE = 'records=function(s,runner)'


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


def runner_traceback(stderr: str):
    """'escape', 'driver' or None: whether a stderr log carries a traceback printed by dry_run itself.

    traceback.print_exc() starts a traceback at the frame that caught the exception.
    A traceback whose outermost frame is dry_run.StepRunner.run at its
    'value = main(list(argv))' call was printed by the runner's own
    'except BaseException' (the program raised: RunnerResult.exception, so
    RunnerResult.token() is None and RunState.invoke records no code). One whose
    outermost frame is dry_run.run at 'records=function(s,runner)' is the driver's
    exception program (a step function raised; the record carries no code). A
    program that prints its own traceback starts it at its own frame, so neither
    shape can come from a program. The text is identical at b5/analysis-r1 and on
    this branch; the worker pool (parallel.run_child) runs the same StepRunner.run.
    """
    lines = [_ANSI_ESCAPE.sub('', line) for line in stderr.splitlines()]
    found = None
    for i, line in enumerate(lines[:-2]):
        head = _TRACEBACK_HEAD.fullmatch(line)
        if head is None:
            continue
        prefix = '  | ' if head.group(1) else ''
        frame, source = lines[i + 1], lines[i + 2]
        if not (frame.startswith(prefix) and source.startswith(prefix)):
            continue
        if _DRIVER_RUN_FRAME.fullmatch(frame[len(prefix):]):
            text = source[len(prefix):].strip()
            if text == RUNNER_ESCAPE_SOURCE:
                found = 'escape'
            elif text == DRIVER_FAIL_SOURCE:
                found = 'driver'
    return found


# A log the driver reads with Path.read_text(): its text, or why the read raises.
_LOG_MISSING = object()          # OSError (never caught by the rules below except mint's)
_LOG_UNDECODABLE = object()      # UnicodeDecodeError, a ValueError


def _driver_read(data):
    """Path.read_text(encoding='utf-8') of a runner log, as the driver reads it (strict UTF-8).

    step_6 and step_8 call read_text() without an encoding: the locale's, UTF-8 on
    the measurement and analysis hosts (macOS). Universal newlines only rewrite
    line ends, which splitlines() already treats alike.
    """
    if data is None:
        return _LOG_MISSING
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return _LOG_UNDECODABLE


# Steps whose step function is dry_run._internal_step alone (r1 and this branch):
# one guarded helper run through the runner, recorded with code=result.token(),
# and nothing after it can change the code or raise a refusal (s.rehash() runs
# before the program and leaves no log; the run() exception program writes a
# second, driver-traced log).
INTERNAL_STEPS = frozenset({'0', '3', '3b', '9b'})


def _single_program_row(step, row, ordinal, stderr):
    """Whether an untraced refusing row's raw code is token() of its last log (review 3 of PR #640).

    * steps 0, 3, 3b, 9b with exactly one (step, block) log: _internal_step.
    * step 10 per window at ordinal 2: the guarded _reported_open, recorded by
      step_10 itself (every driver-level step-10 row has window None).
    * step 8 at ordinal 1: the guarded staging helper (prepare_finalization), but
      only when it refused, which RunState.guarded always reports as a final
      'error: ' stderr line (prepare_finalization writes nothing else and returns
      0; any other exception escapes and is traced). A staging that succeeded
      followed by a driver refusal before the finalizer ran (a rehash or primary
      context refusal) has the same row and ordinal but no such line: not established.
    Every other program step can still end in a promised-output check or a driver
    check after the program, so an exit-2 row there stays unestablished.
    """
    if step in INTERNAL_STEPS:
        return ordinal == 1 and row['window'] is None
    if step == '10':
        return row['window'] is not None and ordinal == 2
    if step == '8':
        lines = stderr.splitlines()
        return row['window'] is None and ordinal == 1 and bool(lines) and lines[-1].startswith('error: ')
    return False


def _legacy_decode(side: Side, row) -> dict:
    """R1 layout: the refusing step's raw code, replayed and as far as the logs establish it.

    Returns {'raw_code', 'established', 'invocation'}. 'raw_code' replays the
    driver's own derivation on the step's LAST runner invocation (the value an R1
    against R1 comparison uses, where one code ran on both sides). 'established' is
    the raw code only when the record and logs fix it, else CODE_UNESTABLISHED
    (review 2 of PR #640, T1/T2). The rules are the driver's, and they are the same
    at b5/analysis-r1 and on this branch (RunnerResult.token, refusal_token,
    RunState.invoke, mint_refusal_code, step_8, step_6, the run() exception
    program), so one decoder serves every analysis_commit:

    * RunnerResult.token(): an escaped exception is None; else the last stderr
      'error: ' line, else the last stdout line. An escape is read from the
      runner's own traceback (runner_traceback), never guessed from text.
    * RunState.invoke(): a code only for a nonzero exit or an exception; an
      exception or a successful program missing a promised output records no
      code and exit 2.
    * step 5: mint_refusal_code on the second program (the mint) only, never after
      an exception; step 8: the stdout REFUSE message of the second program (the
      finalizer; the first is the staging helper), never after an exception;
      step 6: the stdout StepRecord (also after an exception, as step_6 reads it).
    * Reads (review 3 of PR #640): the driver reads logs with strict UTF-8
      (_driver_read). step_6 and step_8 catch the UnicodeDecodeError (a ValueError)
      and skip their rule; token() and mint_refusal_code do not, and a missing log
      raises everywhere. A rule whose read would have raised means the driver went
      on to its exception program, whose driver-traced log would be the last one:
      such a last log establishes nothing ('established' is CODE_UNESTABLISHED;
      'raw_code' keeps the lenient replay, so an R1 against R1 pair still compares it).

    Establishment: a tooling code is public in the record. An outcome-class row
    carries the one outcome code (OUTCOME_CODES). Otherwise the logs establish the
    code only when no other driver path can have produced the row: a runner
    traceback (escape or driver exception program: no code), or an exit status
    other than 2 (the program's own nonzero exit; every driver-decided code, a
    missing promised output and an exception record exit 2; step 4's exit-1
    classification is a registered tooling or outcome code, so it never decides an
    unclassified row). An exit-2 row without
    a runner traceback is the program's exit 2, a successful program missing a
    promised output (no code), or a driver refusal raised after a successful
    program (a code no restricted R1 file records); its raw code is not
    established, except where the step function admits no other exit-2 source
    once that log exists (_single_program_row: the guarded internal helpers of
    steps 0, 3, 3b, 9b, the refused step-8 staging helper and step 10's per-window
    _reported_open; review 3 of PR #640). So is any refusal with no runner log.
    The invocation ordinal is counted as the runner names its logs
    (dry_run.STEP_CODES_LOG, dry_run._refusal_position): the number of
    <counter>-<step>-<window|block>.stderr.log regular files, None when there are none.
    """
    tooling = row['status'] == 'tooling_refusal'
    want = (str(row['step']), row['window'] or 'block')
    if tooling:
        public = {'raw_code': row['refusal'], 'established': row['refusal'], 'invocation': None}
    else:
        public = {'raw_code': None, 'invocation': None,
                  'established': OUTCOME_CODES[0] if row['status'] == 'outcome_class' and len(OUTCOME_CODES) == 1
                  else CODE_UNESTABLISHED}
    try:
        logs_fd = os.open('logs', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=side.restricted_fd)
    except OSError:
        return public
    try:
        stems = []
        with os.scandir(logs_fd) as it:
            for entry in it:
                m = LOG_NAME.fullmatch(entry.name)
                if m and (m.group(2), m.group(3)) == want and entry.is_file(follow_symlinks=False):
                    stems.append((int(m.group(1)), entry.name[:-len('.stderr.log')]))
        if not stems:
            return public
        invocation = ('#i', str(len(stems)))
        if tooling:
            return {**public, 'invocation': invocation}
        stems.sort()
        stem = stems[-1][1]
        stderr_bytes = _read_beneath(logs_fd, stem + '.stderr.log', side.label, 'refusal')
        try:
            stdout_bytes = _read_beneath(logs_fd, stem + '.stdout.log', side.label, 'refusal')
        except ComparatorError:
            stdout_bytes = None
    finally:
        os.close(logs_fd)
    step, exit_status, ordinal = str(row['step']), row['exit_status'], len(stems)
    # Texts are decoded leniently (the replay stays informative for an R1 against R1
    # comparison); whether the DRIVER's strict read of a log succeeds, is skipped
    # or raises is _driver_read's verdict, and only that decides a rule.
    stderr_text = stderr_bytes.decode('utf-8', 'replace')
    stdout_text = '' if stdout_bytes is None else stdout_bytes.decode('utf-8', 'replace')
    traced = runner_traceback(stderr_text)
    escaped = traced == 'escape'
    stderr, stdout = _driver_read(stderr_bytes), _driver_read(stdout_bytes)
    raised = False     # a read the driver makes here would have raised: not the deciding log
    if traced == 'driver':
        code = None                      # dry_run.run: s.record(step, exit_status=2) after the program
    else:
        code = None                      # RunnerResult.token() / RunState.invoke()
        if not escaped and exit_status:
            error_lines = [line for line in stderr_text.splitlines() if line.startswith('error: ')]
            code = _driver_token(stderr_text) if error_lines else _driver_token(stdout_text)
            if not (isinstance(stderr, str) and isinstance(stdout, str)):
                raised = True            # token() reads both logs strictly
        if step == '5' and ordinal == 2 and exit_status and not escaped:
            # mint_refusal_code: a strict stderr read (only OSError is caught).
            raised = raised or not isinstance(stderr, str)
            if any(line.startswith('error: ') and 'authenticated whole-window consumption refused' in line
                   for line in stderr_text.splitlines()):
                code = MINT_CONSUMPTION_REFUSED
        elif step == '8' and ordinal == 2 and exit_status and not escaped:
            # step_8: stdout.read_text() inside except (ValueError, ...): an
            # undecodable log skips the rule, a missing one raises.
            raised = raised or stdout is _LOG_MISSING
            if stdout is not _LOG_UNDECODABLE:
                message = _last_json_line(stdout_text)
                if message is not None and set(message) == {'status', 'reason', 'detail'} \
                        and message['status'] == 'REFUSE' and isinstance(message['reason'], str):
                    code = _driver_token(message['reason'])
        elif step == '6':
            # step_6: the same read, also after an exception and after a zero exit.
            raised = raised or stdout is _LOG_MISSING
            if stdout is not _LOG_UNDECODABLE:
                child = _last_json_line(stdout_text)
                closeout = sum(1 for o in row['outputs']
                               if re.fullmatch(r'finalized/outputs/closeout(\.ratio-table)?\.json', o['name']))
                if child is not None and child.get('status') == 'outcome_class' and exit_status == 3 \
                        and closeout == 2:
                    code = DOMINANCE_ZERO_DENOMINATOR
                elif child is not None and child.get('status') == 'tooling_refusal' \
                        and isinstance(child.get('refusal'), str):
                    code = _driver_token(child['refusal'])
    established = public['established']
    if row['status'] != 'outcome_class':
        fixed = not raised and (traced is not None or (type(exit_status) is int and exit_status != 2)
                                or _single_program_row(step, row, ordinal, stderr_text))
        established = code if fixed and code not in OUTCOME_CODES else CODE_UNESTABLISHED
    return {'raw_code': code, 'established': established, 'invocation': invocation}


def legacy_refusal(side: Side, row) -> dict:
    """R1 layout: {'raw_code', 'invocation'} of a refusing step, replayed from restricted logs (_legacy_decode).

    'raw_code' is the replayed derivation (R1 against R1, one analysis commit); a
    comparison with any other layout or commit uses _legacy_decode's 'established' value.
    """
    decoded = _legacy_decode(side, row)
    return {'raw_code': decoded['raw_code'], 'invocation': decoded['invocation']}


def _int_token(value):
    # Exact token, so an int never compares equal to a bool (True == 1 in Python).
    return ('#i', str(value)) if type(value) is int else value


# Steps whose refusing runner invocation ran one kept bundle (dry_run.note_member):
# a refusing row of one of these steps, in a pack window, with a runner log, has a
# step-codes 'member'.
MEMBER_STEPS = frozenset({'1', '2'})
MEMBER_UNESTABLISHED = '<member-not-established-in-legacy-layout>'
UNESTABLISHED = {'member': MEMBER_UNESTABLISHED, 'raw_code': CODE_UNESTABLISHED}


def _legacy_member(row, refusal, other_row):
    """The legacy side's 'member' in a mixed legacy/step-codes comparison.

    R1 persists no identity of the bundle a refusing step-1/step-2 invocation ran
    (validate-bundle names its bundle only on success; kept-units are written by
    step 3), so the member of such a refusal cannot be established from an R1
    layout: it is MEMBER_UNESTABLISHED, which never equals a digest or None. A
    refusal with no member (any other step, a driver-level stop with no pack
    window, no runner log) is None, as the runner writes it.
    """
    bearing = (str(row['step']) in MEMBER_STEPS and row['window'] in WINDOWS
               and refusal['invocation'] is not None)
    if other_row is not None and other_row['member'] is not None:
        bearing = True
    return MEMBER_UNESTABLISHED if bearing else None


def window_children(side: Side, row):
    """Per-window runner invocations of a step that stopped outside any pack window.

    Review of PR #640 (LOW finding): a driver-level stop inside a per-window step
    (a re-authentication or custody refusal, or an exception, between bundle
    children) is recorded with window None, so the (step, block) ordinal says
    nothing about how many children of each window ran before it. Both layouts
    name every child's log <counter>-<step>-<window>.stderr.log
    (dry_run.STEP_CODES_LOG), so this is read from restricted logs on either side:
    a sorted tuple of (window, count) over the windows with at least one log.
    None for a row that is not a refusal or that names its own window (its
    position is the invocation ordinal). Log-derived, so it is no stronger than
    the logs; it can only add a difference, never hide one.
    """
    if row is None or row['status'] in ('ok', 'not_run') or row['window'] is not None:
        return None
    step, counts = str(row['step']), {}
    try:
        logs_fd = os.open('logs', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=side.restricted_fd)
    except OSError:
        return ()
    try:
        with os.scandir(logs_fd) as it:
            for entry in it:
                m = LOG_NAME.fullmatch(entry.name)
                if m and m.group(2) == step and m.group(3) in WINDOWS and entry.is_file(follow_symlinks=False):
                    counts[m.group(3)] = counts.get(m.group(3), 0) + 1
    finally:
        os.close(logs_fd)
    return tuple((w, ('#i', str(counts[w]))) for w in WINDOWS if w in counts)


def _first_refusal(side, i, row, *, established=False):
    if row is None:
        return None
    decoded = _legacy_decode(side, row)
    return {
        'pos': ('#i', str(i)), 'step': row['step'], 'window': row['window'], 'status': row['status'],
        'exit_status': _int_token(row['exit_status']), 'registered_exit': row.get('registered_exit'),
        'window_children': window_children(side, row),
        'raw_code': decoded['established' if established else 'raw_code'], 'invocation': decoded['invocation']}


def _fail_closed_if_undecided(legacy_label, legacy, other):
    """Raise when a refusal pair agrees on every established field and the rest is unestablished.

    A legacy field equal to its UNESTABLISHED marker could hold any value, so it is
    left out of the check; the pair then cannot be decided and fails closed with a
    digit-free stage (refusal-member when the member is among the unestablished
    fields, else refusal-code). A side with no refusal never fails closed, and an
    established difference is an ordinary NOT_EQUIVALENT (the marker itself differs
    from every real value, so it is reported as a difference too).
    """
    if legacy is None or other is None:
        return
    open_keys = {k for k, marker in UNESTABLISHED.items() if legacy.get(k) == marker or other.get(k) == marker}
    if not open_keys:
        return
    if {k: v for k, v in legacy.items() if k not in open_keys} == {k: v for k, v in other.items() if k not in open_keys}:
        if 'member' in open_keys:
            raise ComparatorError('refusal-member', legacy_label, 'the legacy layout does not establish the refusing bundle')
        raise ComparatorError('refusal-code', legacy_label, 'the legacy layout does not establish the raw refusal code')


def _mixed_first_refusals(ref: Side, cand: Side, codes_ref, codes_cand):
    """First-refusal leaves when exactly one side carries step codes (an R1 reference).

    The step-codes side's raw code, invocation and member come from its step codes
    (review of PR #640, finding S1; review 2, T1: its authenticated raw code is never
    replaced by a log guess). The legacy side's raw code is _legacy_decode's
    established value, its invocation its log-counted ordinal and its member
    _legacy_member. When everything established agrees and the legacy side cannot
    establish its member or raw code, the comparison cannot be decided: it fails
    closed (ComparatorError, digit-free stage). A side with no refusal never fails closed.
    """
    firsts, legacy_label = {}, None
    for side, codes in ((ref, codes_ref), (cand, codes_cand)):
        i, row = _first_non_ok(side.record)
        first = _first_refusal(side, i, row, established=codes is None)
        if first is not None and codes is not None:
            first['raw_code'] = codes[i]['raw_code']
            first['invocation'], first['member'] = codes[i]['invocation'], codes[i]['member']
        if codes is None:
            legacy_label = side.label
        firsts[side.label] = (first, i, row)
    other_codes = codes_cand if codes_ref is None else codes_ref
    legacy, i, row = firsts[legacy_label]
    if legacy is not None:
        other_row = other_codes[i] if i < len(other_codes) else None
        legacy['member'] = _legacy_member(row, legacy, other_row)
        other = firsts[cand.label if legacy_label == ref.label else ref.label][0]
        _fail_closed_if_undecided(legacy_label, legacy, other)
    return {label: first for label, (first, _, _) in firsts.items()}


def _legacy_pair_first_refusals(ref: Side, cand: Side):
    """First-refusal leaves when NEITHER side carries step codes but the analysis commits differ.

    Review of PR #640 (MEDIUM finding): the runner writes step codes on a
    best-effort basis (dry_run._commit_sidecars never fails a run over them), so a
    candidate whose sidecar write failed is a legacy layout too. Against an R1
    reference that must not silently drop the member or raw-code comparison the
    step codes would have made: unless both trees come from one analysis commit (R1
    against R1, where one code ran the same inputs in the same order), each side's
    raw code is its established value and a refusal pair that agrees on everything
    established fails closed when a member or raw code is unestablished, exactly as
    in a mixed comparison. A side with no refusal never fails closed.
    """
    firsts = {}
    for side in (ref, cand):
        i, row = _first_non_ok(side.record)
        first = _first_refusal(side, i, row, established=True)
        if first is not None:
            first['member'] = _legacy_member(row, first, None)
        firsts[side.label] = first
    _fail_closed_if_undecided(ref.label, firsts[ref.label], firsts[cand.label])
    return firsts


def decision_structure(ref: Side, cand: Side, cfg: Config, prefix):
    """Derived decision leaves: per-step result outputs and the raw refusal identity."""
    (codes_ref, auth_ref), (codes_cand, auth_cand) = read_step_codes(ref), read_step_codes(cand)
    mixed = None
    if prefix is None and (codes_ref is None) != (codes_cand is None):
        mixed = _mixed_first_refusals(ref, cand, codes_ref, codes_cand)
    elif (prefix is None and codes_ref is None and codes_cand is None
          and ref.record.get('analysis_commit') != cand.record.get('analysis_commit')):
        mixed = _legacy_pair_first_refusals(ref, cand)
    if codes_ref is not None and codes_cand is not None:
        source = 'step-codes' if auth_ref and auth_cand else 'step-codes-unauthenticated'
    else:
        # Restricted logs are never committed by the record: a raw code derived from
        # them rests on the logs being intact (R1 references always take this path).
        source = 'logs-unauthenticated'
    structures = {}
    for side, codes in ((ref, codes_ref), (cand, codes_cand)):
        steps = side.record['steps']
        limit = len(steps) if prefix is None else prefix
        outputs = [sorted(k for k in side.step_keys[i] if not cfg.is_audit_role(side.artifacts[k].role))
                   for i in range(min(limit, len(steps)))]
        d, audit = {'step_outputs': outputs}, {}
        if source.startswith('step-codes'):
            d['step_codes'] = [{k: r[k] for k in STEP_CODES_DECISION_KEYS} for r in codes[:limit]]
            audit['exception_class'] = [r['exception_class'] for r in codes[:limit]]
            if prefix is None:
                d['first_refusal'] = {'window_children': window_children(side, _first_non_ok(side.record)[1])}
        elif mixed is not None:
            d['first_refusal'] = mixed[side.label]
        elif prefix is None:
            d['first_refusal'] = _first_refusal(side, *_first_non_ok(side.record))
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
    lines.append(f'refusal-source: {result.refusal_source}')
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
        write_blinded_verdict(eq, lines)
    return path


BLINDED_VERDICT = 'BLINDED-VERDICT.txt'
VERDICT_PENDING = 'VERDICT: PENDING'


def write_blinded_verdict(eq: Path, lines: list):
    """Atomically replace <CAND>/equivalence/BLINDED-VERDICT.txt (the only artifact leaving custody)."""
    tmp = eq / ('.' + BLINDED_VERDICT + '.tmp')
    try:
        os.unlink(tmp)
    except FileNotFoundError:
        pass
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        os.write(fd, ('\n'.join(lines) + '\n').encode())
    finally:
        os.close(fd)
    os.replace(tmp, eq / BLINDED_VERDICT)


def invalidate_blinded_verdict(cand_root: Path):
    """Before a blinded run: no earlier verdict may survive a run that later fails or dies."""
    try:
        if not stat.S_ISDIR(os.lstat(cand_root).st_mode):
            return
    except OSError:
        return
    eq, _restricted = equivalence_dirs(cand_root)
    write_blinded_verdict(eq, [VERDICT_PENDING])


def write_error(cand_root: Path, text: str, line: str | None = None):
    try:
        eq, restricted = equivalence_dirs(cand_root)
        _write_exclusive(restricted, 'comparator-error', '.txt', text.encode('utf-8', 'replace'))
        if line is not None:
            write_blinded_verdict(eq, [line])
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
        if mode == 'blinded':
            invalidate_blinded_verdict(cand_root)
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
        line = f'COMPARATOR_ERROR stage={stage} side={side}'
        if mode == 'open':
            err.write(text)
        elif cand_root is not None and stage not in ('args',):
            write_error(cand_root, text, line)
        out.write(line + '\n')
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
