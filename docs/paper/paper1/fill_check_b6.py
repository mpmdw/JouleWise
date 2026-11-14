"""Renders and checks every Block 6 value filled into paper1.md from the released Block 6 outputs.

Runbook steps 14 to 16 after the Block 6 release (PR #769, merged 66469ccf4, 2026-11-13 18:54:57 PST;
RUN_STATE item 312). The Block 5 counterpart is fill_check_b5.py; this script follows its form: every number is
rendered from a named key of a released output, never typed by hand, and the paper must hold the rendered text.

Sources (the dry run at r2 is the run of record; RL-134 item 16.1: the numbers that print are its numbers):

- restricted.json, public.json and structure.json in the dry-run directory (default
  /Volumes/JW-EXT/b6-custody-run/dry-r2). Before anything is read, each file's SHA-256 must equal the digest that
  docs/registrations/block6_release_record.md gives it (the "Output digests" table for restricted and public).
  The record does not digest structure.json; its condition 4 records that the structure probe ran on these bytes,
  and structure.json is pinned here by the SHA-256 the fill seat read. Runbook step 14: structure.json's digests.restricted_file and
  public.json's restricted_sha256 must equal the restricted file's SHA-256, so the scripted term 7 check ran on
  these bytes.
- The loop's attempts.jsonl (pinned by the run-input document's external.loop_attempts digest), for the count of
  attempts per pack only.
- RL-104 check 3's reader file (runbook step 13). Under RL-134 item 16.2 a family that fails there does not print
  from the program output. The copied-family rows printed here are conditional on that file reporting no failing
  family; the script checks that line and the file's SHA-256.

Modes (run from the repository root, python3.13 -I docs/paper/paper1/fill_check_b6.py):

- default: check. Every rendered fill must appear in paper1.md exactly as rendered, no placeholder of a filled id may
  remain, every pending id must still be a placeholder, and the deleted branches must be gone.
- --apply: substitute the rendered fills for their placeholders in paper1.md (used once, by the fill seat).
- --manifest PATH: write the key manifest (one row per printed number: marker, element, file, key path, raw value,
  printed text, rounding format, R3 label). The reader seat re-reads each row by key.

Rounding follows RL-52 and RL-60 as applied to Block 5 (fill_check_b5.py): a quantity in joules prints with two
decimals or three significant figures, whichever shows more digits; per-token values four significant figures;
dominance ratios four decimals, with more digits where four would put a ratio on the other side of the
registered threshold 2; magnitude ratios (energy ratio, scaling factor) three decimals; shares two decimals in
running text. Estimates and every operand of a difference printed beside it (Table 6) round to nearest; interval
ends outward; uncertainties and limits (half-widths, standard deviations, floors outside Table 6) up.

RL-147 (2026-11-13 19:22 PST) amended the fill: the largest-difference sentence (§1); the carried primary-block
codes, derived here from the copied flag records against Block 5's catalog (§2); the whole-machine definition and
edge-shift sensitivities (§3); the P1-RELEASE split (§4); R_cm 1.99975 and the floor caption sentence (§5); the
floor-gate rows, the 8a sentence and three amended sentences (§6); the reader report pinned (§7); the load-correlated
and battery-assist lines and the paragraph on what the replication shows (§10). The template edits that carry the new
markers were made once, on main's paper, before --apply.

Standard library only (and `git show` for two pinned files). Exit status 0 when every check passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal

ROOT = pathlib.Path(__file__).resolve().parents[3]
PAPER = ROOT / 'docs/paper/paper1/paper1.md'
RELEASE_RECORD = ROOT / 'docs/registrations/block6_release_record.md'
DEFAULT_OUTPUTS = pathlib.Path('/Volumes/JW-EXT/b6-custody-run/dry-r2')
RUN_INPUTS = pathlib.Path('/Volumes/JW-EXT/b6-custody-run/run-inputs-block-2.json')
RUN_INPUTS_SHA256 = '0a1a149cc9403e956121eec2daaf7c852eae1a83ea1c079562c80c4e4cc66a8e'  # D_block, release record
ATTEMPTS = pathlib.Path('/Volumes/JW-EXT/b6-custody/attempts.jsonl')
STRUCTURE_SHA256 = '18a129f218d002516cc2bbf2a13243ea7e977ce90328e63c29a46bb78132d8e5'
CHECK3 = pathlib.Path('/Volumes/JW-EXT/scratch/b6-rr3/step13-rl104-check3.md')
CHECK3_SHA256 = 'bc0fce5608b7d9fad707295202ac9e2864d9400476318f18f6fd2a9014a4a0be'
CHECK3_RESULT = '72 of 72 (family x session) rows PASS; 0 FAIL.'
# RL-147 §7 item 2: the separate reader's report on head a2563016e, committed by the lead to the audit branch.
READER_COMMIT = '9611d5fd13d3b8d843f09144b91cc56c17359135'
READER_PATH = 'docs/research-audits/2026-11-10-fable/evidence/pr772/reader-pr772.md'
READER_SHA256 = '4239c9146ff06ae180f2d67ba090db3509a7e140df7daa3e07908cfdc7af4a63'
# RL-147 §2: Block 5's catalog; its 32 session-removing codes are those with effect EXCLUDE_WINDOW.
B5_CATALOG = ROOT / 'configs/campaigns/v5_claim_25g83/flag_catalog.json'
B5_CATALOG_SHA256 = '5d77c725d4bf482bd667ca4c3a926e2f6471d55d196cd4b4addee435da01ee8d'
# Block 5's released output, the run's pinned --block5 input (release record row "Block 5 released output").
B5_OUTPUT = pathlib.Path('/Volumes/JW-EXT/air-home/jw-b5-custody/release-check-final-20261108T0942Z/recompute.json')
# The definition's constants (RL-147 §3), read from the pinned Block 5 functions the Block 6 program loads.
B5_PROGRAM = 'scripts/independent_recompute_b5.py'
B5_PROGRAM_SHA256 = 'd49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0'
S14_COMMIT = '6e6d1b18a9dffbba675c3abd28db2e4c6a484fde'

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- binding the outputs (runbook step 14)

def expected_digests() -> dict[str, str]:
    text = RELEASE_RECORD.read_text()
    out = {}
    for stem in ('public', 'restricted'):
        m = re.search(rf'^\| dry \| {stem} \| `([0-9a-f]{{64}})` \|$', text, re.M)
        if not m:
            raise SystemExit(f'release record: no dry {stem} digest')
        out[stem] = m.group(1)
    # The release record does not digest structure.json. Its condition 4 records that the structure probe ran on
    # these output bytes; the probe's own file is pinned here as the fill seat read it (written 16:50 PST, before
    # the release), and its digests block must name the restricted file's SHA-256 (checked in load_outputs).
    record_json = json.loads(RELEASE_RECORD.with_suffix('.json').read_text())
    if '"probe_ran_on_these_bytes": true' not in json.dumps(record_json):
        raise SystemExit('release record: condition 4 does not record probe_ran_on_these_bytes true')
    out['structure'] = STRUCTURE_SHA256
    return out


def load_outputs(outputs: pathlib.Path) -> tuple[dict, dict, dict]:
    want = expected_digests()
    got = {stem: sha256(outputs / f'{stem}.json') for stem in want}
    for stem in want:
        if got[stem] != want[stem]:
            raise SystemExit(f'{stem}.json SHA-256 {got[stem]} is not the release record\'s {want[stem]}')
    restricted = json.loads((outputs / 'restricted.json').read_text())
    public = json.loads((outputs / 'public.json').read_text())
    structure = json.loads((outputs / 'structure.json').read_text())
    # Step 14 (RL-134 item 8): the scripted term 7 check ran on these bytes.
    if structure['digests']['restricted_file'] != got['restricted']:
        fail('structure.json digests.restricted_file is not the restricted file\'s SHA-256')
    if public['restricted_sha256'] != got['restricted']:
        fail('public.json restricted_sha256 is not the restricted file\'s SHA-256')
    if structure['term7']['result'] != 'pass' or structure['term7']['stop_classes']:
        fail('structure.json term7 is not a pass with no stop class')
    if structure['stage'] != 'dry_run':
        fail('structure.json is not the dry run\'s')
    return restricted, public, structure


def check_side_inputs() -> list[dict]:
    if sha256(RUN_INPUTS) != RUN_INPUTS_SHA256:
        fail('run-input document SHA-256 differs from the release record\'s D_block')
    pinned = json.loads(RUN_INPUTS.read_text())['external']['loop_attempts']
    if sha256(ATTEMPTS) != pinned:
        fail('attempts.jsonl SHA-256 differs from the run-input document\'s external.loop_attempts')
    if sha256(CHECK3) != CHECK3_SHA256 or CHECK3_RESULT not in CHECK3.read_text():
        fail('RL-104 check 3 file differs, or does not report every copied family passing (RL-134 item 16.2)')
    return [json.loads(line) for line in ATTEMPTS.read_text().splitlines() if line.strip()]


def load_extras() -> dict:
    """The reader report, Block 5's catalog, Block 5's released output and the pinned Block 5 program text."""
    report = subprocess.run(['git', 'show', f'{READER_COMMIT}:{READER_PATH}'], cwd=ROOT, check=True,
                            capture_output=True).stdout
    if hashlib.sha256(report).hexdigest() != READER_SHA256:
        fail('reader report SHA-256 differs from the pinned one (RL-147 §7 item 2)')
    m_rows = re.search(r'^- Rows checked: ([0-9,]+)$', report.decode(), re.M)
    m_agree = re.search(r'^- Agree: ([0-9,]+)$', report.decode(), re.M)
    m_dis = re.search(r'^- Disagree: ([0-9,]+)$', report.decode(), re.M)
    if not (m_rows and m_agree and m_dis) or m_dis.group(1) != '0':
        fail('reader report result lines missing, or a disagreement reported')
    if sha256(B5_CATALOG) != B5_CATALOG_SHA256:
        fail('Block 5 catalog SHA-256 differs')
    want = re.search(r'^\| Block 5 released output \| `([0-9a-f]{64})` \|$', RELEASE_RECORD.read_text(), re.M)
    if not want or sha256(B5_OUTPUT) != want.group(1):
        fail('Block 5 released output differs from the release record\'s digest')
    program = subprocess.run(['git', 'show', f'{S14_COMMIT}:{B5_PROGRAM}'], cwd=ROOT, check=True,
                             capture_output=True).stdout
    if hashlib.sha256(program).hexdigest() != B5_PROGRAM_SHA256:
        fail('pinned Block 5 program SHA-256 differs')
    return {'reader': {'rows': m_rows.group(1), 'agree': m_agree.group(1)},
            'catalog': json.loads(B5_CATALOG.read_text()), 'b5': json.loads(B5_OUTPUT.read_text()),
            'program': program.decode()}


# ---------------------------------------------------------------- rounding (RL-52, RL-60)

MODE = {'near': ROUND_HALF_UP, 'down': ROUND_FLOOR, 'up': ROUND_CEILING}
# format -> (kind, digits, direction); 'J' = two decimals or three significant figures, whichever shows more.
ROUNDERS = {
    'e': ('J', 0, 'near'), 'lo': ('J', 0, 'down'), 'hi': ('J', 0, 'up'), 'up': ('J', 0, 'up'),
    'tok': ('sf', 4, 'near'), 'tokup': ('sf', 4, 'up'), 'R5': ('dp', 5, 'near'),
    'R': ('dp', 4, 'near'), 'Rd': ('dp', 4, 'near'), 'Rup': ('dp', 4, 'up'),
    'mr': ('dp', 3, 'near'), 'mrlo': ('dp', 3, 'down'), 'mrhi': ('dp', 3, 'up'), 'mrup': ('dp', 3, 'up'),
    'sh2': ('dp', 2, 'near'),
}
SUP = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')
R_THRESHOLD = Decimal(2)


def exponent(d: Decimal, kind: str, k: int) -> int:
    if kind == 'dp':
        return -k
    if kind == 'sf':
        return d.adjusted() - k + 1 if d != 0 else -k
    return -2 if d == 0 else min(-2, d.adjusted() - 2)


def quantize(x: float, fmt: str) -> Decimal:
    kind, k, direction = ROUNDERS[fmt]
    d = Decimal(repr(float(x)))
    exp = exponent(d, kind, k)
    q = d.quantize(Decimal(1).scaleb(exp), rounding=MODE[direction])
    if kind == 'sf' and q != 0 and q.adjusted() != d.adjusted():
        q = q.quantize(Decimal(1).scaleb(q.adjusted() - k + 1), rounding=MODE[direction])
    if fmt == 'R':
        # RL-52: never print a ratio on the other side of the threshold from its unrounded value.
        places = k
        while (d < R_THRESHOLD) != (q < R_THRESHOLD):
            places += 1
            q = d.quantize(Decimal(1).scaleb(-places), rounding=MODE[direction])
    return q


def text(q: Decimal) -> str:
    s = format(q, 'f')
    return '−' + s[1:] if s.startswith('-') else s


def signed_text(q: Decimal) -> str:
    s = text(q)
    return s if s.startswith('−') else ('+' + s if q != 0 else s)


# ---------------------------------------------------------------- the manifest: every printed number by key

MANIFEST: list[dict] = []
CURRENT = {'marker': ''}


class Src:
    def __init__(self, name: str, data: dict):
        self.name, self.data = name, data
        self.file = {'attempts': 'attempts.jsonl', 'block5': 'Block 5 recompute.json (c06ee7c8…)',
                     'catalog': 'configs/campaigns/v5_claim_25g83/flag_catalog.json',
                     'reader': READER_PATH + '@' + READER_COMMIT[:9],
                     'program': B5_PROGRAM + '@' + S14_COMMIT[:9]}.get(name, name + '.json')

    def get(self, path: str):
        o = self.data
        for p in path.split('|'):
            o = o[int(p)] if isinstance(o, list) else o[p]
        return o


def record(src: Src, path: str, raw, printed: str, fmt: str, label: str = '') -> str:
    MANIFEST.append({'marker': CURRENT['marker'], 'file': src.file, 'key_path': path,
                     'raw': json.dumps(raw), 'printed': printed, 'format': fmt, 'label': label})
    return printed


def num(src: Src, path: str, fmt: str, label: str = '', sign: bool = False) -> str:
    raw = src.get(path)
    if not isinstance(raw, (int, float)) or isinstance(raw, bool):
        raise SystemExit(f'{src.name}:{path} is not a number ({raw!r})')
    if fmt == 'n':
        if raw != int(raw):
            raise SystemExit(f'{src.name}:{path} is not an integer')
        printed = str(int(raw))
    else:
        q = quantize(raw, fmt)
        printed = signed_text(q) if sign else text(q)
    return record(src, path, raw, printed, fmt, label)


def word(src: Src, path: str, label: str = '', mapping: dict | None = None) -> str:
    raw = src.get(path)
    printed = (mapping or {}).get(raw, str(raw).replace('_', ' '))
    return record(src, path, raw, printed, 'word', label)


# ---------------------------------------------------------------- names

PACK_MODEL = {'ALPHA': ('qwen3-1p7b', 'Qwen3-1.7B', '1.7B', 'Qwen3-1.7B-4bit'),
              'BETA': ('qwen3-8b', 'Qwen3-8B', '8B', 'Qwen3-8B-4bit')}
PHASES = (('decode', 'decode', 'decode'), ('prefill-p2048', 'prefill (2,048)', 'prefill'))
CONTRASTS = (('decode', 'decode', 'ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b'),
             ('prefill-p2048', '2,048-token prefill', 'ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b'))
CELL = {('ALPHA', 'decode'): 'df-ph-decode-qwen3-1p7b', ('ALPHA', 'prefill-p2048'): 'df-ph-prefill-p2048-qwen3-1p7b',
        ('BETA', 'decode'): 'df-ph-decode-qwen3-8b', ('BETA', 'prefill-p2048'): 'df-ph-prefill-p2048-qwen3-8b'}
LABEL_SS = 'single-source'
LABEL_NIR = 'not independently recomputed'
LABEL_R8 = 'single implementation; not independently recomputed'
LABEL_CC = 'computed and compared'  # RL-147 §9: the internal name "decision 6 (a)" is dropped
LABEL_COPIED = 'copied from the harvest or acceptance record, bound by digest, not recomputed'
LABEL_BLOCK = '§10-§11 arithmetic computed and compared'


def sessions_of(R: Src, pack: str) -> list[str]:
    rows = [(s['round'], sid) for sid, s in R.data['sessions'].items() if s['pack'] == pack and s['counting']]
    return [sid for _, sid in sorted(rows)]


def join(items: list[str], last: str = 'and') -> str:
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + f' {last} ' + items[-1]


# ---------------------------------------------------------------- the fills

def fill_count(R: Src, attempts: list[dict]) -> str:
    A = Src('attempts', {'rows': attempts})
    parts = []
    for pack in ('ALPHA', 'BETA', 'GAMMA'):
        made = [i for i, a in enumerate(attempts) if a['packs'] == [pack.lower()]]
        for i in made:
            if A.get(f'rows|{i}|outcomes|{pack.lower()}|status') != 'counting':
                raise SystemExit(f'attempt {i} of {pack} did not count: its cause family is owed')
        record(A, f'rows with packs == ["{pack.lower()}"] (count)', len(made), str(len(made)), 'n')
        if R.get(f'block|short|{pack}|short') or R.get(f'block|short|{pack}|below_commitment'):
            raise SystemExit(f'{pack} is short: the registered "short" sentence is owed, not this fill')
        counting = num(R, f'block|short|{pack}|counting', 'n')
        if int(counting) != len(made):
            fail(f'{pack}: counting sessions differ from attempts that counted')
        parts.append(f'{pack}: {counting} counting sessions of the 3 targeted, from {len(made)} attempts')
    if len(attempts) != len(R.data['sessions']) or any(not s['counting'] for s in R.data['sessions'].values()):
        raise SystemExit('a non-counting attempt exists: its cause family is owed')
    return (f'{"; ".join(parts)}. Every attempt counted, so no non-counting attempt '
            'and no cause family is listed, and no pack is short.')


def fill_rep(R: Src, phase: str) -> dict[str, str]:
    base = f'block|replication|{phase}'
    rep = R.get(base)
    if rep['word'] != 'replicated' or rep['short']:
        raise SystemExit(f'{phase}: the selected branch is not 5.7.1')
    for i, s in enumerate(rep['sessions']):
        word(R, f'{base}|sessions|{i}|outcome')
        word(R, f'{base}|sessions|{i}|direction')
    word(R, f'{base}|block5_outcome')
    word(R, f'{base}|block5_direction')
    return {'word': '"' + word(R, f'{base}|word') + '"', 'n': record(R, f'{base}|sessions', len(rep['sessions']),
                                                          str(len(rep['sessions'])), 'n'),
            'outcome': word(R, f'{base}|sessions|0|outcome')}


def fill_flaginc(R: Src) -> str:
    out = []
    for phase, name, _ in CONTRASTS:
        base = f'block|replication|{phase}'
        added = R.get(f'{base}|flagged_inclusive_sessions')
        record(R, f'{base}|flagged_inclusive_sessions', added, 'none', 'list')
        if added:
            raise SystemExit('flagged-inclusive sessions exist: their words and flags are owed')
        out.append(f'"{word(R, f"{base}|word")}" for {name}')
    n_added = 0
    for pack in ('ALPHA', 'BETA', 'GAMMA'):
        added = R.get(f'block|flagged_inclusive|{pack}|added_sessions')
        record(R, f'block|flagged_inclusive|{pack}|added_sessions', added, 'none', 'list')
        n_added += len(added)
        if added:
            raise SystemExit('flagged-inclusive sessions exist')
    return (f'Including sessions that did not count (n = {n_added}): every attempt counted, so no session is added and '
            f'the flagged-inclusive words are the registered ones, {join(out)}; they do not enter the registered word.')


def r_short(R: Src, sid: str, key: str) -> str:
    return num(R, f'sessions|{sid}|quantities|{key}', 'R', LABEL_SS)


def fill_dom(R: Src) -> str:
    sentences = []
    for pack in ('ALPHA', 'BETA'):
        tag, _, short, _ = PACK_MODEL[pack]
        for sid in sessions_of(R, pack):
            d, p = f'dominance/{tag}/decode', f'dominance/{tag}/prefill-p2048'
            sentences.append(
                f'{sid} ({short}): R = {r_short(R, sid, d + "/absolute/R")} and {r_short(R, sid, d + "/comparative/R")} '
                f'for decode (absolute, comparative) and {r_short(R, sid, p + "/absolute/R")} and '
                f'{r_short(R, sid, p + "/comparative/R")} for prefill (2,048); R_cm = '
                f'{r_short(R, sid, d + "/comparative/R_cm")} and {r_short(R, sid, p + "/comparative/R_cm")}')
    pairings = []
    names = {'Qwen3-1.7B-4bit': '1.7B', 'Qwen3-8B-4bit': '8B'}
    modes = {'common_mode': 'R_cm', 'comparative': 'comparative R', 'absolute': 'absolute R'}
    for sid in sessions_of(R, 'GAMMA'):
        branch = word(R, f'sessions|{sid}|pairing_dominance|branch', LABEL_NIR)
        if branch != 'B':
            raise SystemExit(f'{sid}: branch {branch}; only branch B\'s sentence is written here')
        pair = [word(R, f'sessions|{sid}|pairing|{pk}|session_id') for pk in ('ALPHA', 'BETA')]
        failed = R.get(f'sessions|{sid}|pairing_dominance|failed')
        items = []
        for f in failed:
            model, phase, mode = f.split('/')
            items.append(f'{names[model]} {"prefill (2,048)" if phase == "prefill" else phase} {modes[mode]}')
        record(R, f'sessions|{sid}|pairing_dominance|failed', failed, '; '.join(items), 'list', LABEL_NIR)
        pairings.append(f'{sid} (floors from {pair[0]} and {pair[1]}): {join(items)}')
    # RL-147 §10 (c), placed here by §6 ("with the sentence of §10 item (c) added").
    b5 = [R.get(f'block|side_by_side|{pk}|dominance/{PACK_MODEL[pk][0]}/{ph}/{mode}/R|block5')
          for pk in ('ALPHA', 'BETA') for ph, _, _ in PHASES for mode in ('absolute', 'comparative')]
    b5_all = record(R, 'block|side_by_side|<ALPHA,BETA>|dominance/<m>/<phase>/<absolute,comparative>/R|block5 (count >= 2)',
                    sum(v >= 2 for v in b5), 'eight' if len(b5) == 8 and all(v >= 2 for v in b5) else '?', 'n')
    if b5_all != 'eight':
        fail('not every primary-block independent-corner R is at least 2')
    below = [(sid, key) for pk in ('ALPHA', 'BETA') for sid in sessions_of(R, pk)
             for key, v in R.get(f'sessions|{sid}|quantities').items()
             if key.startswith('dominance/') and key.endswith('/R') and v < 2]
    if {k for _, k in below} != {'dominance/qwen3-8b/decode/comparative/R'}:
        fail(f'replication R below 2 is not only the 8B decode comparative R: {below}')
    beta = sessions_of(R, 'BETA')
    vals = [r_short(R, sid, 'dominance/qwen3-8b/decode/comparative/R') for sid, _ in below]
    count = {2: 'two', 1: 'one', 3: 'three'}[len(below)]
    failed_sets = {json.dumps(sorted(R.get(f'sessions|{g}|pairing_dominance|failed'))) for g in sessions_of(R, 'GAMMA')}
    if len(failed_sets) < 2:
        fail('the failed components are the same in every pairing; "not stable" does not hold')
    c_text = (f'In the primary block all {b5_all} independent-corner ratios R were at least 2. In the replication the 8B '
              f'decode comparative R is below 2 in {count} of the {"three" if len(beta) == 3 else len(beta)} 8B floor '
              f'sessions ({join(vals)}). The '
              'branch is B in the primary block and in all three replication pairings; which components fail is not '
              'stable from session to session.')
    return ('Per floor session, the four R per model and its two R_cm: ' + '; '.join(sentences) + '. '
            'Every contrast pairing is branch B: timing movement did not at least double every detection floor. '
            'The failed components were, per pairing, ' + '; '.join(pairings) + '. Each ratio is a point '
            'diagnostic with no interval, labelled single-source; the branch is labelled not independently '
            'recomputed. ' + c_text)


def cell_line(R: Src, sid: str, pack: str, phase: str, line: str, label: str) -> str:
    _, _, short, _ = PACK_MODEL[pack]
    pname = dict((p, n) for p, n, _ in PHASES)[phase]
    base = f'sessions|{sid}|lines|{CELL[(pack, phase)]}|{line}'
    row = R.get(base)
    if row['status'] != 'computed':
        n_r, n_b = num(R, base + '|n_r', 'n', label), num(R, base + '|n_b', 'n', label)
        reason = word(R, base + ('|reason' if 'reason' in row else '|status'), label)
        return f'{sid} {short} {pname}: not computed ({reason}; n_r = {n_r}, n_b = {n_b})'
    return (f'{sid} {short} {pname}: {num(R, base + "|mean_j", "e", label)} J '
            f'[{num(R, base + "|lower_j", "lo", label)}, {num(R, base + "|upper_j", "hi", label)}] '
            f'(n_r = {num(R, base + "|n_r", "n", label)}, n_b = {num(R, base + "|n_b", "n", label)})')


def contrast_line(R: Src, sid: str, cname: str, cid: str, line: str, label: str) -> str:
    base = f'sessions|{sid}|lines|{cid}|{line}'
    row = R.get(base)
    status = row['status']
    if status not in ('computed', 'below_registered_minimum'):
        raise SystemExit(f'{base}: status {status}')
    if row.get('dbar_j') is None:
        return (f'{sid} {cname}: not computed ({word(R, base + "|status", label)}; '
                f'n = {num(R, base + "|n", "n", label)})')
    tail = '' if status == 'computed' else ', below the registered minimum of 5 quads'
    return (f'{sid} {cname}: d̄ = {num(R, base + "|dbar_j", "e", label)} J '
            f'[{num(R, base + "|metrology_interval_j|0", "lo", label)}, '
            f'{num(R, base + "|metrology_interval_j|1", "hi", label)}] (n = {num(R, base + "|n", "n", label)}{tail})')


def fill_floor_and_contrast_lines(R: Src, line: str, label: str) -> str:
    parts = []
    for pack in ('ALPHA', 'BETA'):
        for sid in sessions_of(R, pack):
            for phase, _, _ in PHASES:
                parts.append(cell_line(R, sid, pack, phase, line, label))
    for sid in sessions_of(R, 'GAMMA'):
        for phase, cname, cid in CONTRASTS:
            parts.append(contrast_line(R, sid, cname, cid, line, label))
    return '; '.join(parts)


def fill_waited(R: Src) -> str:
    removed = 0
    for pack in ('ALPHA', 'BETA'):
        for sid in sessions_of(R, pack):
            for phase, _, _ in PHASES:
                base = f'sessions|{sid}|lines|{CELL[(pack, phase)]}|waited_runs|removed_by_stratum'
                removed += sum(R.get(base).values())
    for sid in sessions_of(R, 'GAMMA'):
        for _, _, cid in CONTRASTS:
            removed += sum(R.get(f'sessions|{sid}|lines|{cid}|waited_runs|removed_by_stratum').values())
    lead = ('no kept unit held a run whose idle admission waited, so each line equals its cell: '
            if removed == 0 else '')
    return lead + fill_floor_and_contrast_lines(R, 'waited_runs', LABEL_NIR)


def fill_contention(R: Src) -> str:
    lbl = word(R, 'sessions|r1-alpha|lines|df-ph-decode-qwen3-1p7b|outside_processor_alternative|label', LABEL_NIR,
               mapping={'registered outside-processor rule (w = 5.432 J per CPU-s, c_q = 0.54 CPU-s)':
                        'registered outside-processor rule (w = 5.432 J per CPU-s, c_q = 0.54 CPU-s)'})
    cells = [(sid, CELL[(pk, ph)]) for pk in ('ALPHA', 'BETA') for sid in sessions_of(R, pk) for ph, _, _ in PHASES]
    computed = sum(R.get(f'sessions|{sid}|lines|{c}|outside_processor_alternative|status') == 'computed'
                   for sid, c in cells)
    if computed:
        fail('a floor cell is computable under the registered contention rule; §10 (d) does not hold')
    ns = [R.get(f'sessions|{sid}|lines|{cid}|outside_processor_alternative|n')
          for sid in sessions_of(R, 'GAMMA') for _, _, cid in CONTRASTS]
    record(R, 'sessions|<sid>|lines|<cell>|outside_processor_alternative|status (computed, of 12 floor cells)',
           computed, 'none', 'n', LABEL_NIR)
    record(R, 'sessions|<gamma sid>|lines|<cid>|outside_processor_alternative|n (min, max over 6 contrasts)',
           [min(ns), max(ns)], f'{min(ns)} to {max(ns)}', 'n', LABEL_NIR)
    if max(ns) >= 5:
        fail('a contrast keeps 5 quads under the registered contention rule')
    d_text = (f'Applied as registered, the outside-processor exclusion leaves none of the {len(cells)} floor cells with '
              f'the registered minimum of units, and leaves the {len(ns)} contrasts {min(ns)} to {max(ns)} quads of the 5 '
              'required. It was not adopted for this block for that reason, as registered, and the replication\'s '
              'sessions confirm it would have removed most of the data. ')
    d_text = d_text.replace(f'the {len(ns)} contrasts', 'the six contrasts' if len(ns) == 6 else f'the {len(ns)} contrasts')
    return d_text + f'{lbl[0].upper() + lbl[1:]}: ' + fill_floor_and_contrast_lines(R, 'outside_processor_alternative', LABEL_NIR)


def fill_step(R: Src) -> str:
    parts = []
    for pack in ('ALPHA', 'BETA'):
        _, _, short, _ = PACK_MODEL[pack]
        for sid in sessions_of(R, pack):
            for phase, pname, _ in PHASES:
                base = f'sessions|{sid}|lines|{CELL[(pack, phase)]}|single_step_reconstruction'
                if R.get(base + '|status') != 'computed':
                    raise SystemExit(f'{base}: not computed')
                parts.append(f'{sid} {short} {pname}: {num(R, base + "|mean_j", "e", LABEL_NIR)} ± '
                             f'{num(R, base + "|h_j", "up", LABEL_NIR)} J beside '
                             f'{num(R, f"sessions|{sid}|quantities|reported/{PACK_MODEL[pack][0]}/{phase}/mean_j", "e", LABEL_SS)} J')
    return '; '.join(parts) + '; not given for the contrast sessions'


def fill_wm(R: Src) -> str:
    parts = []
    for pack in ('ALPHA', 'BETA'):
        _, _, short, _ = PACK_MODEL[pack]
        for sid in sessions_of(R, pack):
            for phase, pname, _ in PHASES:
                base = f'sessions|{sid}|whole_machine|windows|{pack}|cells|{CELL[(pack, phase)]}'
                if R.get(base + '|status') != 'computed':
                    raise SystemExit(f'{base}: not computed')
                assisted = num(R, base + '|battery_assist_count', 'n', LABEL_R8)
                parts.append(f'{sid} {short} {pname}: {num(R, base + "|mean_j", "e", LABEL_R8)} J '
                             f'[{num(R, base + "|lower_j", "lo", LABEL_R8)}, {num(R, base + "|upper_j", "hi", LABEL_R8)}], '
                             f'edge-shift sensitivity ± {num(R, base + "|edge_shift_sensitivity|max_abs_change_j", "up", LABEL_R8)} J, '
                             f'rails\' share {num(R, base + "|gross_share|median", "sh2", LABEL_R8)} (median over '
                             f'{num(R, base + "|gross_share|n", "n", LABEL_R8)} kept runs), '
                             f'{assisted} battery-assisted')
    return ('intervals are statistical half-widths only; the timing sensitivity is printed beside each: '
            + '; '.join(parts) + f', each labelled "{LABEL_R8}"')


def fill_scaled(R: Src) -> str:
    parts = []
    for pack in ('ALPHA', 'BETA'):
        tag, _, short, _ = PACK_MODEL[pack]
        for sid in sessions_of(R, pack):
            for phase, pname, _ in PHASES:
                base = f'sessions|{sid}|quantities|lines/scaled_allowance/{tag}/{phase}'
                parts.append(f'{sid} {short} {pname}: factor {num(R, base + "/factor", "mr", LABEL_NIR)}, '
                             f'[{num(R, base + "/lower_j", "lo", LABEL_NIR)}, {num(R, base + "/upper_j", "hi", LABEL_NIR)}] J')
    for sid in sessions_of(R, 'GAMMA'):
        for phase, cname, cid in CONTRASTS:
            base = f'sessions|{sid}|scaled_allowance|contrasts|{cid}'
            same = R.get(base + '|outcome_equals_primary')
            record(R, base + '|outcome_equals_primary', same, 'unchanged' if same else 'changed', 'word', LABEL_NIR)
            changed = 'unchanged' if same else 'changed'
            parts.append(f'{sid} {cname}: factor {num(R, base + "|factor", "mr", LABEL_NIR)}, decision interval '
                         f'[{num(R, base + "|decision_interval_j|0", "lo", LABEL_NIR)}, '
                         f'{num(R, base + "|decision_interval_j|1", "hi", LABEL_NIR)}] J, outcome word '
                         f'{word(R, base + "|outcome", LABEL_NIR)} ({changed})')
    return ('; '.join(parts) + '. The plain-mean factor, registered to print beside this one where a cell lost '
            'unequal numbers of units, is not in the released output and is not printed')


def fill_xsess(R: Src) -> str:
    parts = []
    for sid in sessions_of(R, 'GAMMA'):
        for pack in ('ALPHA', 'BETA'):
            tag, _, short, _ = PACK_MODEL[pack]
            for phase, pname, _ in PHASES:
                base = f'sessions|{sid}|quantities|cross_session/{tag}/{phase}'
                agree = R.get(base + '/agree')
                record(R, base + '/agree', agree, 'agree' if agree else 'differ', 'word', LABEL_NIR)
                if agree:
                    parts.append(f'{sid} {short} {pname}: agree within the statistical half-widths; timing bounds B '
                                 'not included')
                else:
                    parts.append(f'{sid} {short} {pname}: G − F = {num(R, base + "/delta_j", "e", LABEL_NIR, sign=True)} J, '
                                 f'beyond √(h_G² + h_F²) with h_G = {num(R, base + "/h_G_j", "up", LABEL_NIR)} J and '
                                 f'h_F = {num(R, base + "/h_F_j", "up", LABEL_NIR)} J (between-session variation the '
                                 'intervals do not cover; timing bounds B not included)')
    return '; '.join(parts)


# ---------------------------------------------------------------- RL-147 §2: the carried primary-block codes

def carried(R: Src, X: dict) -> dict[str, dict]:
    """RL-147 §2 rule: each session's copied flags.jsonl codes, intersected with Block 5's 32 EXCLUDE_WINDOW codes;
    neg8.screen_failed goes to a disclosure; neg8.midpoint_lost (GAMMA only) is the dropped lost-midpoint rule."""
    C = Src('catalog', X['catalog'])
    ex32 = sorted(code for code, v in X['catalog']['codes'].items() if v.get('effect') == 'EXCLUDE_WINDOW')
    record(C, 'codes|<code>|effect == EXCLUDE_WINDOW (count)', len(ex32), str(len(ex32)), 'n')
    out = {}
    for sid, s in R.data['sessions'].items():
        path = f'sessions|{sid}|copied_disclosures|families|block5_codes_carried|0|record'
        rows = [json.loads(line) for line in R.get(path).splitlines() if line.strip()]
        codes = {r['code'] for r in rows}
        hit = codes & set(ex32)
        out[sid] = {'carried': sorted(hit - {'neg8.screen_failed'}), 'disclosed': sorted(hit & {'neg8.screen_failed'}),
                    'dropped_rule': s['pack'] == 'GAMMA' and 'neg8.midpoint_lost' in codes, 'rows': rows,
                    'n32': len(ex32)}
        record(R, path + ' (codes in the 32, carried)', out[sid]['carried'], ', '.join(out[sid]['carried']), 'list',
               LABEL_COPIED)
    return out


def fill_carried(R: Src, X: dict) -> str:
    c = carried(R, X)
    expected = {sid: ['code.executed_differs_from_sealed'] for sid in R.data['sessions']}
    if {sid: v['carried'] for sid, v in c.items()} != expected:
        fail('carried codes differ from RL-147 §2\'s derivation')
    if [sid for sid, v in c.items() if v['disclosed']] != ['r2-beta']:
        fail('neg8.screen_failed is not in r2-beta alone')
    if [sid for sid, v in c.items() if v['dropped_rule']] != ['r2-gamma']:
        fail('neg8.midpoint_lost is not in r2-gamma alone')
    rec = next(r for r in c['r2-beta']['rows'] if r['code'] == 'neg8.screen_failed')
    if rec['observed']['decision'] != 'failed':
        fail('r2-beta bracket decision is not "failed"')
    conds = rec['observed']['conditions']
    record(R, 'sessions|r2-beta|copied_disclosures|families|block5_codes_carried|0|record (neg8.screen_failed observed.conditions)',
           conds, ', '.join(conds), 'list', LABEL_COPIED)
    mid = next(r for r in c['r2-gamma']['rows'] if r['code'] == 'neg8.midpoint_lost')
    lost = mid['observed']['lost']
    if [x['reason'] for x in lost] != ['contention.request_overlap']:
        fail('r2-gamma midpoint was not lost to contention.request_overlap')
    record(R, 'sessions|r2-gamma|copied_disclosures|families|block5_codes_carried|0|record (neg8.midpoint_lost observed.lost[0].reason)',
           lost[0]['reason'], 'overlapped outside processor work', 'word', LABEL_COPIED)
    n_mid = num(R, 'sessions|r2-gamma|neg8|n_mid', 'n', LABEL_CC)
    if n_mid != '1':
        fail('the r2-gamma drift screen did not use its midpoint')
    verdicts = [R.get(f'sessions|{sid}|quantities|neg8/verdict') for sid in R.data['sessions']]
    if set(verdicts) != {'passed'}:
        fail('a registered drift screen did not pass')
    record(R, 'sessions|<sid>|quantities|neg8/verdict (all nine)', verdicts, 'passed', 'word', LABEL_CC)
    nine = {9: 'nine'}[len(c)]
    return (f'Of the primary block\'s {c["r1-alpha"]["n32"]} session-removing codes, one is carried, by all {nine} '
            'replication sessions: `code.executed_differs_from_sealed`. The comparison it records is against the '
            'primary block\'s sealed file inventory, and the replication was collected from its own registered '
            'checkout, so the code fires by construction and is a flag in this block. One primary-block session rule '
            'that the replication dropped would have applied: r2-gamma\'s midpoint reference run overlapped outside '
            'processor work, which the primary block\'s rules would have removed, and on the contrast pack a lost '
            'midpoint removed the session (`neg8.midpoint_lost`); under the replication\'s rules the run is kept and '
            'the drift screen used it. Disclosed and, as registered, not listed as carried: r2-beta\'s stored bracket '
            'decision of the old drift screen is "failed" (`neg8.screen_failed`; conditions '
            + ', '.join(f'`{x}`' for x in conds) + f'); the registered drift screen passed in that session, as in all '
            f'{nine}.')


# ---------------------------------------------------------------- RL-147 §3: the whole-machine definition

WM_DEF = ('For each run and phase, the phase\'s two edges are placed on the meter\'s clock by the meter stream\'s '
          'clock fit, and the phase\'s whole-machine energy is the mean of the meter\'s power samples (50 a second) '
          'that fall between the edges, multiplied by the phase length. It is gross: no idle baseline is subtracted '
          'and the battery term is not added. Per model and phase the runs are summarised with estimator 1\'s '
          'arithmetic (0.2 × the mean over repeats + 0.8 × the mean over quad means), and the interval printed is '
          'that estimator\'s statistical half-width only, with no timing bound. The rails\' share is the median, '
          'over the kept runs, of the run\'s gross rail energy over the same phase divided by its whole-machine '
          'energy. The meter\'s clock-fit residual and the alignment bound do not enter the interval. They enter one '
          'labelled sensitivity: each edge is moved by ±(b_op + the stream\'s largest clock-fit residual), in the '
          'four sign combinations, and the largest change of the cell\'s mean is printed as the edge-shift '
          'sensitivity.')


def fill_wm_def(X: dict) -> str:
    Pg = Src('program', {})
    prog = X['program']
    checks = {'50 a second': '+/-2 samples at 50 Hz', '0.2': '.2 * statistics.fmean(repeats) + .8 * statistics.fmean(quad_means)',
              '0.8': '.2 * statistics.fmean(repeats) + .8 * statistics.fmean(quad_means)'}
    for printed, needle in checks.items():
        if needle not in prog:
            fail(f'WM-DEF constant {printed!r}: {needle!r} not in the pinned program')
        record(Pg, f'text "{needle}"', needle, printed, 'constant', LABEL_R8)
    return WM_DEF


# ---------------------------------------------------------------- RL-147 §10: the two missing lines and the paragraph

def fill_equal_line(R: Src, line: str, lead: str) -> str:
    n_cells = 0
    for pack in ('ALPHA', 'BETA'):
        tag = PACK_MODEL[pack][0]
        for sid in sessions_of(R, pack):
            for phase, _, _ in PHASES:
                base = f'sessions|{sid}|lines|{CELL[(pack, phase)]}|{line}'
                row = R.get(base)
                moved = row.get('restored_by_stratum') or row.get('removed_by_stratum')
                same = all(row[k] == R.get(f'sessions|{sid}|quantities|reported/{tag}/{phase}/{k}')
                           for k in ('mean_j', 'lower_j', 'upper_j', 'n_r', 'n_b'))
                if row['status'] != 'computed' or any(moved.values()) or not same:
                    raise SystemExit(f'{base}: differs from the cell; the per-cell form is owed')
                record(R, base + ' (equals the cell; units moved 0)', row['mean_j'], 'equal', 'equal', LABEL_NIR)
                n_cells += 1
    n_ctr = 0
    for sid in sessions_of(R, 'GAMMA'):
        for phase, _, cid in CONTRASTS:
            base = f'sessions|{sid}|lines|{cid}|{line}'
            row = R.get(base)
            moved = row.get('restored_by_stratum') or row.get('removed_by_stratum')
            same = (row['dbar_j'] == R.get(f'sessions|{sid}|quantities|contrast/{phase}/dbar_j')
                    and row['n'] == R.get(f'sessions|{sid}|quantities|contrast/{phase}/n'))
            if row['status'] != 'computed' or any(moved.values()) or not same:
                raise SystemExit(f'{base}: differs from the contrast; the per-contrast form is owed')
            record(R, base + ' (equals the contrast; units moved 0)', row['dbar_j'], 'equal', 'equal', LABEL_NIR)
            n_ctr += 1
    return (f'{lead} and the line equals the registered estimate in each of the {n_cells} floor cells and the {n_ctr} '
            'contrasts')


def fill_shows(R: Src, X: dict) -> str:
    B = Src('block5', X['b5'])
    rows = []
    for sid in sessions_of(R, 'GAMMA'):
        for pack in ('ALPHA', 'BETA'):
            tag = PACK_MODEL[pack][0]
            for phase, _, _ in PHASES:
                q = R.get(f'sessions|{sid}|quantities')
                k = f'cross_session/{tag}/{phase}'
                rows.append((sid, pack, phase, q[k + '/agree'], q[k + '/delta_j'], q[k + '/F_j'], k))
    differ = [r for r in rows if not r[3]]
    b8 = [r for r in rows if r[1] == 'BETA']
    a17 = [r for r in rows if r[1] == 'ALPHA']
    if not all(not r[3] and r[4] < 0 for r in b8) or sum(not r[3] for r in a17) != 1:
        fail('§10 (a) does not hold: every 8B comparison differs and reads lower, one 1.7B comparison differs')
    words = {12: '12', 6: 'six', 1: 'one', 7: '7'}
    n_diff = record(R, 'sessions|<gamma sid>|quantities|cross_session/<m>/<phase>/agree (count false)', len(differ),
                    str(len(differ)), 'n', LABEL_NIR)
    mags = sorted(abs(r[4]) for r in b8)
    lo8 = record(R, 'min |cross_session/qwen3-8b/<phase>/delta_j| over GAMMA sessions', mags[0],
                 text(quantize(mags[0], 'e')), 'e', LABEL_NIR)
    hi8 = record(R, 'max |cross_session/qwen3-8b/<phase>/delta_j| over GAMMA sessions', mags[-1],
                 text(quantize(mags[-1], 'e')), 'e', LABEL_NIR)
    a_diff = next(r for r in a17 if not r[3])
    a_val = num(R, f'sessions|{a_diff[0]}|quantities|{a_diff[6]}/delta_j', 'e', LABEL_NIR, sign=True)
    b5 = {}
    for ph, b5ph in (('decode', 'decode'), ('prefill-p2048', 'prefill')):
        base = f'disclosures|cross_window|Qwen3-8B-4bit/{b5ph}'
        b5[ph] = (num(B, base + '|delta_j', 'e', 'Block 5 released output', sign=True),
                  record(B, base + '|agree', B.get(base + '|agree'), 'agreed' if B.get(base + '|agree') else 'differed',
                         'word', 'Block 5 released output'))
        if B.get(base + '|delta_j') >= 0:
            fail('a primary-block 8B cross-window difference is not negative')
    pct8 = [abs(r[4]) / r[5] * 100 for r in b8]
    pct = lambda x: text(Decimal(repr(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    p8lo = record(R, 'min over 8B comparisons of |delta_j| / F_j × 100 (percent, one decimal, nearest)', min(pct8),
                  pct(min(pct8)), 'pct')
    p8hi = record(R, 'max over 8B comparisons of |delta_j| / F_j × 100 (percent, one decimal, nearest)', max(pct8),
                  pct(max(pct8)), 'pct')
    p17 = record(R, f'{a_diff[0]} {a_diff[6]}: |delta_j| / F_j × 100 (percent, one decimal, nearest)',
                 abs(a_diff[4]) / a_diff[5] * 100, pct(abs(a_diff[4]) / a_diff[5] * 100), 'pct')
    half = min(min(R.get(f'sessions|{g}|quantities|contrast/{ph}/dbar_j') - R.get(f'sessions|{g}|quantities|contrast/{ph}/decision_lower_j'),
                   R.get(f'sessions|{g}|quantities|contrast/{ph}/decision_upper_j') - R.get(f'sessions|{g}|quantities|contrast/{ph}/dbar_j'))
               for g in sessions_of(R, 'GAMMA') for ph, _, _ in CONTRASTS)
    if max(abs(r[4]) for r in rows) >= half:
        fail('a cross-session difference is not inside every decision interval')
    a_text = (f'*Between sessions.* In {n_diff} of the {len(rows)} cross-session comparisons the contrast session and its '
              f'paired floor session differ by more than their statistical half-widths. All {words[len(b8)]} comparisons '
              f'for the 8B model do, and in each the contrast session reads lower, by {lo8} to {hi8} J (primary block: '
              f'{b5["decode"][0]} J for decode, which {b5["decode"][1]}, and {b5["prefill-p2048"][0]} J for prefill, which '
              f'{b5["prefill-p2048"][1]}); {words[1]} of the {words[len(a17)]} for the 1.7B model does ({a_val} J). The sign '
              'is the same in every 8B comparison of both blocks, so this is a systematic difference between a model '
              'measured alone and the same model measured in alternation, not scatter; we did not test a cause. The 8B '
              f'differences are {p8lo}% to {p8hi}% of the phase energy and the 1.7B one {p17}%; all are far inside every '
              'decision interval, and the two separately collected cells are not differenced into any claim.')
    # (b) floors
    side = 'block|side_by_side|BETA'
    ranges, deltas, prim = [], [], []
    for ph, _, _ in PHASES:
        key = f'floor/qwen3-8b/{ph}/absolute/floor_j'
        vals = [R.get(f'{side}|{key}|sessions|{sid}') for sid in sessions_of(R, 'BETA')]
        ranges.append((record(R, f'min {side}|{key}|sessions', min(vals), text(quantize(min(vals), 'e')), 'e', LABEL_SS),
                       record(R, f'max {side}|{key}|sessions', max(vals), text(quantize(max(vals), 'e')), 'e', LABEL_SS)))
        deltas += [R.get(f'{side}|{key}|session_deltas|{sid}') for sid in sessions_of(R, 'BETA')]
        prim.append(num(R, f'{side}|{key}|block5', 'e', 'Block 5 released output'))
    if max(deltas) >= 0:
        fail('an 8B absolute floor is not below the primary block\'s')
    dlo = record(R, f'min |{side}|floor/qwen3-8b/<phase>/absolute/floor_j|session_deltas|<sid>|', min(abs(x) for x in deltas),
                 text(quantize(min(abs(x) for x in deltas), 'e')), 'e', LABEL_BLOCK)
    dhi = record(R, f'max |{side}|floor/qwen3-8b/<phase>/absolute/floor_j|session_deltas|<sid>|', max(abs(x) for x in deltas),
                 text(quantize(max(abs(x) for x in deltas), 'e')), 'e', LABEL_BLOCK)
    label = R.get('block|between_session|BETA|values|floor/qwen3-8b/decode/absolute/floor_j|timing_regime_label')
    bound = re.search(r'up to ([0-9.]+) J of floor', label).group(1)
    record(R, 'block|between_session|BETA|values|floor/qwen3-8b/decode/absolute/floor_j|timing_regime_label ("up to x J of floor")',
           bound, bound, 'text')
    b_text = (f'*Floors.* The replication\'s 8B absolute floors ({ranges[0][0]} to {ranges[0][1]} J for decode, '
              f'{ranges[1][0]} to {ranges[1][1]} J for prefill) are {dlo} to {dhi} J below the primary block\'s '
              f'({prim[0]} and {prim[1]} J). The calibration-acceptance difference between the blocks accounts for at '
              f'most {bound} J of that. The rest is a difference between sessions that the registered rule does not '
              'explain, and it is the reason the between-session summary is printed for the replication sessions alone '
              'as well.')
    return '**What the replication shows.** ' + a_text + '\n\n' + b_text


# ---------------------------------------------------------------- Table 6 and Table 6a

ROWS = {  # quantity key suffix -> (row name, format family, label)
    'reported/{m}/{p}/mean_j': ('Mean energy, {pn} (J)', 'J', LABEL_SS),
    'reported/{m}/{p}/per_token_j': ('Per token, {pn} (J/token)', 'tok', LABEL_SS),
    'reported/{m}/{p}/attribution_floor_j': ('Attribution floor, {pn} (J)', 'J', LABEL_SS),
    'floor/{m}/{p}/absolute/floor_j': ('Absolute floor, {pn} (J)', 'J', LABEL_SS),
    'floor/{m}/{p}/comparative/floor_j': ('Comparative floor, {pn} (J)', 'J', LABEL_SS),
    'floor/{m}/{p}/absolute/operative_j': ('Absolute corner (R numerator), {pn} (J)', 'J', LABEL_SS),
    'floor/{m}/{p}/comparative/operative_j': ('Comparative corner (R numerator), {pn} (J)', 'J', LABEL_SS),
    'dominance/{m}/{p}/absolute/R': ('R, absolute, {pn}', 'R', LABEL_SS),
    'dominance/{m}/{p}/comparative/R': ('R, comparative, {pn}', 'R', LABEL_SS),
    'dominance/{m}/{p}/comparative/R_cm': ('R_cm, comparative, {pn}', 'R', LABEL_SS),
    'lines/whole_machine/{m}/{p}/mean_j': ('Whole-machine energy per phase, {pn} (J)', 'J', LABEL_R8),
}
GAMMA_ROWS = {
    'contrast/{p}/dbar_j': ('d̄, {pn} (J)', 'J', LABEL_CC),
    'contrast/{p}/energy_ratio': ('Energy ratio 8B ÷ 1.7B, {pn}', 'mr', LABEL_NIR),
}
FAMILY_FMT = {'J': ('e', 'lo', 'hi', 'up'), 'tok': ('tok', 'tok', 'tok', 'tokup'), 'R': ('R', 'R', 'R', 'Rup'),
              'mr': ('mr', 'mrlo', 'mrhi', 'mrup')}
DELTA_FMT = {'e': 'e', 'tok': 'tok', 'R': 'Rd', 'mr': 'mr'}  # a difference is not tested against R's threshold
INTERVALS = {'reported/{m}/{p}/mean_j': ('reported/{m}/{p}/lower_j', 'reported/{m}/{p}/upper_j'),
             'lines/whole_machine/{m}/{p}/mean_j': ('lines/whole_machine/{m}/{p}/lower_j',
                                                    'lines/whole_machine/{m}/{p}/upper_j'),
             'contrast/{p}/dbar_j': ('contrast/{p}/metrology_lower_j', 'contrast/{p}/metrology_upper_j'),
             'contrast/{p}/energy_ratio': ('contrast/{p}/energy_ratio_lower', 'contrast/{p}/energy_ratio_upper')}


R5_KEYS = {'dominance/qwen3-1p7b/prefill-p2048/comparative/R_cm'}  # RL-147 §5 item 2: five decimals for its Block 5 value


def table6(R: Src, pack: str, X: dict) -> str:
    sids = sessions_of(R, pack)
    rows_def = GAMMA_ROWS if pack == 'GAMMA' else ROWS
    m = PACK_MODEL.get(pack, ('', '', '', ''))[0]
    phases = [(p, n) for p, n, _ in PHASES]
    head = ['Quantity', 'Primary'] + sids + ['Δ (each session)', 'Between-session summary (n sessions): mean, '
                                               'standard deviation', 'Label']
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    side = f'block|side_by_side|{pack}'
    for tmpl, (name, fam, label) in rows_def.items():
        for phase, pn in phases:
            key = tmpl.format(m=m, p=phase)
            est, lo, hi, up = FAMILY_FMT[fam]
            cells = [name.format(pn=pn), num(R, f'{side}|{key}|block5', 'R5' if key in R5_KEYS else est,
                                             'Block 5 released output')]
            for sid in sids:
                v = num(R, f'{side}|{key}|sessions|{sid}', est, label)
                same = num(R, f'sessions|{sid}|quantities|{key}', est, label)
                if same != v:
                    fail(f'{key} {sid}: side-by-side value differs from the session quantity')
                if tmpl in INTERVALS:
                    lk, uk = (t.format(m=m, p=phase) for t in INTERVALS[tmpl])
                    v += (f' [{num(R, f"sessions|{sid}|quantities|{lk}", lo, label)}, '
                          f'{num(R, f"sessions|{sid}|quantities|{uk}", hi, label)}]')
                    if tmpl == 'contrast/{p}/dbar_j':
                        v += (f'; decision [{num(R, f"sessions|{sid}|quantities|contrast/{phase}/decision_lower_j", lo, label)}, '
                              f'{num(R, f"sessions|{sid}|quantities|contrast/{phase}/decision_upper_j", hi, label)}]')
                cells.append(v)
            dfmt = DELTA_FMT[est]
            deltas = ', '.join(f'{num(R, f"{side}|{key}|session_deltas|{sid}", dfmt, LABEL_BLOCK, sign=True)}'
                               for sid in sids)
            cells.append(f'{num(R, f"{side}|{key}|delta", dfmt, LABEL_BLOCK, sign=True)} ({deltas})')
            bs = f'block|between_session|{pack}|values|{key}'
            if not R.get(bs + '|block5_included') or R.get(bs + '|noncomputable_sessions'):
                fail(f'{key}: Block 5 not included, or a session not computable')
            summ = (f'{num(R, bs + "|n", "n", LABEL_BLOCK)} sessions: {num(R, bs + "|mean", est, LABEL_BLOCK)}, '
                    f'{num(R, bs + "|sd", up, LABEL_BLOCK)}')
            if R.get(bs).get('timing_regime_label'):
                b6 = f'block|block6_only|{pack}|{key}'
                summ += (f'; Block 6 only, {num(R, b6 + "|n", "n", LABEL_BLOCK)} sessions: '
                         f'{num(R, b6 + "|mean", est, LABEL_BLOCK)}, {num(R, b6 + "|sd", up, LABEL_BLOCK)}')
            cells.append(summ)
            cells.append(label)
            out.append('| ' + ' | '.join(cells) + ' |')
    if pack == 'GAMMA':
        # RL-147 §6: the floor gate (§9.4) rows; not a §10 quantity, so no Δ or summary.
        B = Src('block5', X['b5'])
        for phase, cname, cid in CONTRASTS:
            cells = [f'Floor gate, {cname} (J)', num(B, f'contrasts|{cid}|floor_gate_j', 'up', 'Block 5 released output')]
            cells += [num(R, f'sessions|{sid}|quantities|contrast/{phase}/floor_gate_j', 'up', LABEL_NIR) for sid in sids]
            cells += ['—', '—', LABEL_NIR]
            out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)


def table6a(R: Src, P: Src, X: dict) -> str:
    head = ['Session', 'Pack', 'Round', 'Kept units (n_r / n_b, or quads)', 'Program flags', 'Drift screen',
            'Floor pairing', 'Primary-block codes carried']
    c = carried(R, X)
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    flags = R.get('flags')
    for pack in ('ALPHA', 'BETA', 'GAMMA'):
        for sid in sessions_of(R, pack):
            if pack == 'GAMMA':
                kept = '; '.join(f'{cn}: {num(R, f"sessions|{sid}|quantities|contrast/{p}/n", "n", LABEL_CC)} quads'
                                 for p, cn, _ in CONTRASTS)
                pairing = ', '.join(f'{word(R, f"sessions|{sid}|pairing|{pk}|session_id")} '
                                    f'({word(R, f"sessions|{sid}|pairing|{pk}|rule", mapping={"1_same_round": "same round", "2_next_counting": "next counting session"})})'
                                    for pk in ('ALPHA', 'BETA'))
                for pk in ('ALPHA', 'BETA'):
                    if R.get(f'sessions|{sid}|pairing|{pk}|provisional'):
                        fail(f'{sid}: provisional pairing')
            else:
                tag = PACK_MODEL[pack][0]
                kept = '; '.join(f'{pn}: {num(R, f"sessions|{sid}|quantities|reported/{tag}/{p}/n_r", "n", LABEL_SS)} / '
                                 f'{num(R, f"sessions|{sid}|quantities|reported/{tag}/{p}/n_b", "n", LABEL_SS)}'
                                 for p, pn, _ in PHASES)
                pairing = '—'
            mine = [i for i, f in enumerate(flags) if f['session'] == sid]
            codes: dict[str, int] = {}
            for i in mine:
                codes[flags[i]['code']] = codes.get(flags[i]['code'], 0) + 1
                record(R, f'flags|{i}|code', flags[i]['code'], flags[i]['code'], 'word')
            flagtext = ', '.join(f'`{c}` × {n}' for c, n in sorted(codes.items())) or 'none'
            screen = word(R, f'sessions|{sid}|quantities|neg8/verdict', LABEL_CC)
            car = ', '.join(f'`{x}`' for x in c[sid]['carried']) + ('; lost-midpoint rule (dropped)'
                                                                     if c[sid]['dropped_rule'] else '')
            out.append(f'| {sid} | {pack} | {num(R, f"sessions|{sid}|round", "n")} | {kept} | {flagtext} | '
                       f'{screen} | {pairing} | {car} |')
    return '\n'.join(out)


def fill_sidebyside(R: Src, P: Src, X: dict) -> str:
    regime = R.get('block|between_session|ALPHA|values|floor/qwen3-1p7b/decode/absolute/floor_j|timing_regime_label')
    record(R, 'block|between_session|ALPHA|values|floor/qwen3-1p7b/decode/absolute/floor_j|timing_regime_label',
           regime, regime, 'text')
    parts = []
    for pack, model in (('ALPHA', 'Qwen3-1.7B'), ('BETA', 'Qwen3-8B'), ('GAMMA', 'contrast, Qwen3-8B − Qwen3-1.7B')):
        parts.append(f'**{pack} ({model}).**\n\n' + table6(R, pack, X))
    es = [(f'sessions|{sid}|whole_machine|windows|{pk}|cells|{CELL[(pk, ph)]}|edge_shift_sensitivity|max_abs_change_j')
          for pk in ('ALPHA', 'BETA') for sid in sessions_of(R, pk) for ph, _, _ in PHASES]
    ev = [R.get(k) for k in es]
    es_lo = record(R, 'min ' + '|'.join(es[0].split('|')[:1]) + '|<sid>|whole_machine|...|edge_shift_sensitivity|max_abs_change_j (12 cells)',
                   min(ev), text(quantize(min(ev), 'lo')), 'lo', LABEL_R8)
    es_hi = record(R, 'max sessions|<sid>|whole_machine|...|edge_shift_sensitivity|max_abs_change_j (12 cells)',
                   max(ev), text(quantize(max(ev), 'hi')), 'hi', LABEL_R8)
    B = Src('block5', X['b5'])
    b5k = [f'disclosures|whole_machine|windows|{pk}|cells|{CELL[(pk, ph)]}|edge_shift_sensitivity|max_abs_change_j'
           for pk in ('ALPHA', 'BETA') for ph, _, _ in PHASES]
    bv = [B.get(k) for k in b5k]
    b5_lo = record(B, 'min disclosures|whole_machine|...|edge_shift_sensitivity|max_abs_change_j (4 cells)', min(bv),
                   text(quantize(min(bv), 'lo')), 'lo', 'Block 5 released output')
    b5_hi = record(B, 'max disclosures|whole_machine|...|edge_shift_sensitivity|max_abs_change_j (4 cells)', max(bv),
                   text(quantize(max(bv), 'hi')), 'hi', 'Block 5 released output')
    caption = (
        '*Table 6. The primary block\'s value of every Part 1 quantity beside each counting replication session\'s '
        'value, M3 Max / MLX / powermetrics SoC rails, under the same estimators. Intervals: the mean\'s interval, '
        'the whole-machine interval, and for d̄ the metrology interval and the decision interval, as in Tables 2 '
        'and 5; the energy ratio\'s t interval; floors and ratios are point values with no interval. Δ is the mean '
        'over the counting replication sessions minus the primary value, then each session\'s own difference. The '
        'between-session summary is over the primary session and the counting replication sessions. Values, '
        'differences and means round to nearest, interval ends outward, standard deviations up. A floor printed here '
        'to nearest can be one unit in its last digit below the same floor in Tables 2 to 4, where it stands as a limit '
        'and rounds up. The whole-machine interval is the statistical half-width only; its edge-shift sensitivity, '
        f'{es_lo} to {es_hi} J per cell (primary block: {b5_lo} to {b5_hi} J), is in the labelled lines. The floor-gate '
        'rows are not a §10 quantity and carry no Δ or summary; they round up. Label: each '
        'session value\'s producer label from the registered printed-quantity table (§17-R3); for d̄ the first '
        'clause of the conditional label applied in every session (drift screen passed, the twin estimated, and '
        'every contrast kept 5 or more quads); Δ and the summaries are labelled "' + LABEL_BLOCK + '". Floors: '
        + regime + ' That bound is small beside several of the floor differences in the table; see the text.*')
    return '\n\n'.join(parts) + '\n\n' + caption + '\n\n' + table6a(R, P, X) + (
        '\n\n*Table 6a. The counting replication sessions: kept units per cell, the program\'s flags (none stops '
        'the comparison), the drift-screen verdict, for each contrast session its floor sessions with the pairing '
        'rule, and the primary block\'s session-removing codes each session carries (derived from the copied flag '
        'record against the primary block\'s catalog; see the text). Every pairing is final, none provisional.*')


# ---------------------------------------------------------------- the agreement sentence (runbook step 15)

CLASS_BARS = {  # the S-13 bar per class: 1 mJ per run phase energy, otherwise half a unit of the ratified
    # print precision's last digit (configs/b6/recompute/precision.json at the S-14 commit, decimals_for()).
    'calibration': 'b_op: 5 × 10⁻⁷ s',
    'contrast': 'n exact; d̄ and D: 5 × 10⁻⁶ J; p and Holm p: 5 × 10⁻⁵',
    'inclusive': 'as its quantity: J 5 × 10⁻⁶; R, R_cm and energy ratio 5 × 10⁻⁵; per token 5 × 10⁻⁹; n exact',
    'neg8': 'bound and allowance 5 × 10⁻⁶ J; verdict exact',
    'replication': 'word exact',
    'run_phase_energy': '10⁻³ J',
    'side_by_side': 'as its quantity: J 5 × 10⁻⁶; R and energy ratio 5 × 10⁻⁵; per token 5 × 10⁻⁹',
    'summary': 'as its quantity: J 5 × 10⁻⁶; R, R_cm and energy ratio 5 × 10⁻⁵; per token 5 × 10⁻⁹; n exact',
}


MAXDIFF_SENTENCE = ('The largest observed difference per class is not printed: the pinned program computed it and did '
                    'not write it to its output, and the run was not repeated after the release. What the released '
                    'output shows is that every compared row passed, so in each class the largest difference is no '
                    'larger than that class\'s bar. This departs from the registration\'s §12.3 item 4, which says the '
                    'observed agreement is printed beside the tolerance; the counts are printed and the largest '
                    'difference is not.')


def fill_summary_b6(R: Src, S: Src, X: dict) -> str:
    classes = R.get('block|option_c|comparator|classes')
    probe = S.get('option_c|comparator|classes')
    for cls, c in classes.items():
        mine = {k: v for k, v in probe.get(cls, {}).items() if k != 'extra_fields'}
        if mine != c:
            fail(f'{cls}: the structure probe\'s comparator record differs from the restricted one')
    t7 = S.get('term7|totals')
    tot = {k: sum(c[k] for c in classes.values()) for k in ('compared', 'both_null', 'first_program_only',
                                                           'failed', 'unmatched', 'passed')}
    for k in ('compared', 'both_null', 'first_program_only'):
        if tot[k] != t7[k]:
            fail(f'term7 totals {k} {t7[k]} differ from the restricted comparator\'s {tot[k]}')
    if tot['compared'] - tot['both_null'] != t7['agreeing_on_a_value']:
        fail('agreeing on a value differs from term 7')
    if tot['failed'] or tot['unmatched'] or not R.get('block|option_c|pass'):
        raise SystemExit('the comparator did not pass: no agreement sentence is written')
    if len(R.get('block|option_c|first_program_only')) != tot['first_program_only']:
        fail('first_program_only list length differs from the class counts')
    rows = ['| Class | Bar | Compared | Failed | Unmatched | Null on both sides | Agreeing on a value | '
            'First-program-only |', '|---|---|---|---|---|---|---|---|']
    base = 'block|option_c|comparator|classes'
    no_rows = []
    for cls in sorted(classes):
        c = classes[cls]
        compared = num(R, f'{base}|{cls}|compared', 'n')
        bn = num(R, f'{base}|{cls}|both_null', 'n')
        fpo = num(R, f'{base}|{cls}|first_program_only', 'n')
        if c['compared'] == 0:
            no_rows.append(f'`{cls}`')
            rows.append(f'| `{cls}` | — | 0 | — | — | — | — | {fpo} |')
            continue
        if c['both_null'] > c['passed'] or not c.get('pass'):
            fail(f'{cls}: both_null above passed, or no pass')
        agree = record(R, f'{base}|{cls}|compared minus both_null', c['compared'] - c['both_null'],
                       str(c['compared'] - c['both_null']), 'n')
        rows.append(f'| `{cls}` | {CLASS_BARS[cls]} | {compared} | {num(R, f"{base}|{cls}|failed", "n")} | '
                    f'{num(R, f"{base}|{cls}|unmatched", "n")} | {bn} | {agree} | {fpo} |')
    fmt = lambda n: f'{n:,}'
    totals = (f'| Total | | {fmt(tot["compared"])} | {tot["failed"]} | {tot["unmatched"]} | {tot["both_null"]} | '
              f'{fmt(tot["compared"] - tot["both_null"])} | {tot["first_program_only"]} |')
    for k in ('compared', 'both_null', 'first_program_only', 'failed', 'unmatched'):
        record(S, f'term7|totals ({k}, summed over restricted block|option_c|comparator|classes)', tot[k],
               fmt(tot[k]) if k == 'compared' else str(tot[k]), 'n')
    kinds = S.get('term7|distinct_keys_by_label_kind')
    for k, v in kinds.items():
        record(S, f'term7|distinct_keys_by_label_kind|{k}', v, str(v), 'n')
    fam = R.get('block|option_c|families')
    n_classes = record(R, base, len(classes), str(len(classes)), 'n')
    restricted_sha = S.get('digests|restricted_file')
    record(S, 'digests|restricted_file', restricted_sha, restricted_sha, 'sha256')
    Rd = Src('reader', {})
    agreed = record(Rd, '"- Agree: N" line', X['reader']['agree'], X['reader']['agree'], 'n')
    checked = record(Rd, '"- Rows checked: N" line', X['reader']['rows'], X['reader']['rows'], 'n')
    para = (
        f'**Replication block.** The comparator set the first program\'s values against the second side\'s in '
        f'{n_classes} classes, under the replication registration\'s S-13 bars (Block 6 §12.3 item 4): each run\'s '
        f'phase energy within 1 mJ, and every printed quantity, compared unrounded, within half a unit of its last '
        f'digit in the ratified print specification, which carries more digits than the paper prints. Table S9 '
        f'gives, per class, the bar and the counts. Agreement is stated over compared rows only: '
        f'{fmt(tot["compared"])} rows were compared and every one agreed ({tot["failed"]} failed, '
        f'{tot["unmatched"]} unmatched); {tot["both_null"]} of them held no value on either side, so '
        f'{fmt(tot["compared"] - tot["both_null"])} rows agreed on a value; {tot["first_program_only"]} rows were '
        f'printed by the first program only and were not compared. The {len(no_rows)} classes with no compared row '
        f'({join(no_rows)}) carry no verdict. What was compared: each run\'s phase energy, the calibration timing '
        f'bound, each session\'s drift-screen verdict, bound and allowance, each contrast\'s count, d̄, D, p and '
        f'Holm p, the between-session summaries, the flagged-inclusive summaries, the side-by-side differences and '
        f'the two replication words. What was not: the first-program-only rows are the cell, per-token, '
        f'attribution-floor and floor estimators and the dominance ratios of the two floor packs (single-source: one '
        f'producer in this block, the same pinned functions that agreed with the registered analysis on the primary '
        f'block), the per-phase whole-machine line (single implementation; not independently recomputed), and the '
        f'labelled lines, the cross-session lines and a contrast\'s direction, ceiling, energy ratio, per-token value, '
        f't, metrology bounds and floor gate (not independently recomputed); a contrast\'s outcome word, spread and '
        f'decision bounds are checked by the second side\'s gate, outside the comparison table. A scripted check (RL-113 term 7) found every first-program-only key under a label that allows '
        f'non-comparison: {kinds["single_source"]} distinct keys single-source, {kinds["not_independently_recomputed"]} '
        f'not independently recomputed, {kinds["r8_single_implementation"]} single implementation and '
        f'{kinds["gate"]} compared in the gate only; it ran on the released restricted output, SHA-256 '
        f'`{restricted_sha}`, the digest that the release record and the check\'s own record '
        f'(`structure.json`) both give. The eight copied disclosure families were read against their source files '
        f'by a separate reader (8 families in 9 sessions: 72 of 72 rows hold their disclosure), and every printed value '
        f'of Section 6.8 is rendered by key from the released output by `docs/paper/paper1/fill_check_b6.py` and '
        f're-read by key by a separate reader ({agreed} of {checked} printed elements agreed). One disclosed repair changed printed numbers before the release, '
        f'adopted on 13 November 2026 (registration §17-R13, analysis revision r2): the first program had dropped the '
        f'primary block\'s four released whole-machine per-phase values from the side-by-side rows and printed them '
        f'as not computed; the repaired program includes them, which changes, for those four quantities only, the '
        f'primary value and the differences of Table 6 and the between-session and flagged-inclusive summaries.')
    record(R, 'block|option_c|families', fam, json.dumps(fam), 'list')
    table = '\n'.join(rows + [totals])
    caption = ('*Table S9. Agreement of the first program with the second side, replication block, per comparator '
               'class (dry run at r2). Bar: the S-13 bar from the ratified print specification; "—": a class with no '
               'compared row, which carries no verdict. Agreeing on a value = compared − null on both sides.*')
    return para + '\n\n' + table + '\n\n' + caption + '\n\n' + MAXDIFF_SENTENCE


# ---------------------------------------------------------------- assembly

PENDING = {'P1-RELEASE', 'P1-RELEASE-BYTES', 'P1-B6-DISCLOSURES'}

# RL-147 §8: the research lead's text for the stale "blinded" sentences, P1-RECOMPUTE and the abstract's replication
# clause. Each new text must be present once and each old one gone. The Block 5 numbers of P1-ABS-PART1 are
# fill_check_b5.py's (site "Abstract, Part 1 summary").
S8_NEW = [
    'A registered replication, nine further sessions on later days, was collected and analysed blind and released '
    'after the primary block.',
    '**A pre-registered, blinded measurement with a registered replication**',
    'The replication\'s results are reported beside the primary block\'s (Section 6.8).',
    'The replication stayed blinded until its own release, which required its closure and the prior primary release, '
    'because reading replication values first would have unblinded the same quantities.',
    'in the registered replication, nine further sessions, both contrasts gave the primary session\'s outcome word and '
    'sign, and the sessions differed from one another by more than their within-session intervals cover.',
    'The bars, the counts and the agreement are given per family for the primary block in Table S8 and per class for '
    'the replication block in Table S9 (Section 6.7), with the quantities not covered and their separate reader checks.',
    'must be printed beside the applicable bars (for the replication block the largest difference was not retained; '
    'Section 6.7), never used to choose them.',
]
S8_GONE = ['remains blinded', 'The replication results remain sealed', 'with a collected, blinded replication',
           'no replication result is asserted']


def abstract_clause(R: Src) -> str:
    """RL-147 §8's fixed replication clause, printed only if the program's words support it."""
    CURRENT['marker'] = 'P1-ABS-PART1 (replication clause, RL-147 §8)'
    n = set()
    for phase, _, _ in CONTRASTS:
        if word(R, f'block|replication|{phase}|word') != 'replicated':
            raise SystemExit('the abstract\'s replication clause does not hold')
        n.add(len(R.get(f'block|replication|{phase}|sessions')))
    if n != {3}:
        raise SystemExit('the replication rests on other than three contrast sessions')
    three = record(R, 'block|replication|<phase>|sessions (count)', 3, 'three', 'n')
    return (f'Both contrasts replicated under the registered definition: each of the {three} replication contrast '
            'sessions gave the primary session\'s outcome word and sign.')
END_574 = '**[END BRANCH 5.7.4]**'


def render_all(R: Src, P: Src, S: Src, attempts: list[dict], X: dict) -> tuple[dict[str, str], str]:
    fills: dict[str, str] = {}
    for marker, fn in (('P1-RECOMPUTE-SUMMARY-B6', lambda: fill_summary_b6(R, S, X)),
                       ('P1-B6-SIDEBYSIDE', lambda: fill_sidebyside(R, P, X)),
                       ('P1-B6-CARRIED', lambda: fill_carried(R, X)),
                       ('P1-B6-WM-DEF', lambda: fill_wm_def(X)),
                       ('P1-B6-SHOWS', lambda: fill_shows(R, X)),
                       ('P1-B6-LOADSENS', lambda: fill_equal_line(
                           R, 'load_sensitivity', 'no kept unit was removed only by thermal or contention codes, so '
                           'no unit is restored')),
                       ('P1-B6-BATT', lambda: fill_equal_line(
                           R, 'battery_assist', 'no kept unit held a battery-assisted run, so no unit is removed')),
                       ('P1-B6-COUNT', lambda: fill_count(R, attempts)),
                       ('P1-B6-FLAGINC-WORDS', lambda: fill_flaginc(R)),
                       ('P1-B6-DOM', lambda: fill_dom(R)),
                       ('P1-B6-SCALED', lambda: fill_scaled(R)),
                       ('P1-B6-STEP', lambda: fill_step(R)),
                       ('P1-B6-WM', lambda: fill_wm(R)),
                       ('P1-B6-CONTENTION', lambda: fill_contention(R)),
                       ('P1-B6-WAITED', lambda: fill_waited(R)),
                       ('P1-B6-XSESS', lambda: fill_xsess(R))):
        CURRENT['marker'] = marker
        fills[marker] = fn()
    words = {}
    for phase, name, _ in CONTRASTS:
        CURRENT['marker'] = f'P1-B6-REPWORD-{"decode" if phase == "decode" else "prefill"} / branch 5.7.1'
        words[phase] = fill_rep(R, phase)
    fills['P1-ABS-PART1-CLAUSE'] = abstract_clause(R)
    fills['P1-B6-REPWORD-decode'] = words['decode']['word']
    fills['P1-B6-REPWORD-prefill'] = words['prefill-p2048']['word']
    branch = ('<!-- BRANCH 5.7.1 selected for both contrasts (fill seat, 2026-11-13), from the released dry run at r2 '
              '(fill_check_b6.py): block.replication.<phase>.word is "replicated" and short is false for decode and '
              'prefill-p2048; each of the 3 counting GAMMA sessions gave direction_supported and positive, as the '
              'primary block did. From the registered rule (registration §11.2): every counting session has the '
              'primary block\'s outcome word and sign of d̄. Branches 5.7.2 to 5.7.4 are deleted. The template asks '
              'for the branch once per contrast; it is written once per contrast below. -->\n\n')
    for phase, name, _ in CONTRASTS:
        w = words[phase]
        branch += (f'The {name} contrast **replicated**: every one of the {w["n"]} counting replication sessions '
                   f'gave the same outcome word as the primary block, *{w["outcome"]}*, and the same sign of d̄. ')
        branch += ('"Replicated" describes agreement of outcome words and signs across sessions; it is not a new '
                   'test and carries no new interval. Any claim level is still that reached in each session '
                   'separately.\n\n')
    return fills, branch.rstrip('\n')


PAT = re.compile(r'\{\{FILL:\s*([^|\\}]+?)\s*(?:\\\||\|)\s*(.*?)\}\}', re.S)


def apply(paper: str, fills: dict[str, str], branch: str) -> str:
    start, end = paper.find('**[BRANCH 5.7.1'), paper.find(END_574)
    if start < 0 or end < start:
        raise SystemExit('the 5.7 branches are not in paper1.md; nothing applied')
    paper = paper[:start] + branch + paper[end + len(END_574):]

    def sub(m: re.Match) -> str:
        fid = m.group(1).strip()
        return fills[fid] if fid in fills else m.group(0)
    return PAT.sub(sub, paper)


def check(paper: str, fills: dict[str, str], branch: str) -> None:
    norm = lambda s: re.sub(r'\s+', ' ', s)
    flat = norm(paper)
    for fid, txt in fills.items():
        if fid in ('P1-B6-REPWORD-decode', 'P1-B6-REPWORD-prefill', 'P1-ABS-PART1-CLAUSE'):
            continue
        if flat.count(norm(txt)) != 1:
            fail(f'{fid}: rendered text appears {flat.count(norm(txt))} times in paper1.md, not once')
    sentence = (f'The replication words were {fills["P1-B6-REPWORD-decode"]} for decode and '
                f'{fills["P1-B6-REPWORD-prefill"]} for 2,048-token prefill.')
    if flat.count(norm(sentence)) != 1:
        fail('the replication-word sentence is not in paper1.md once')
    if flat.count(norm(branch)) != 1:
        fail('branch 5.7.1 as rendered is not in paper1.md once')
    for gone in ('[BRANCH 5.7.2', '[BRANCH 5.7.3', '[BRANCH 5.7.4', '[BRANCH 5.7.1'):
        if gone in paper:
            fail(f'{gone} is still in paper1.md')
    ids = {m.group(1).strip() for m in PAT.finditer(paper)}
    for fid in list(fills) + ['P1-B6-REP-PHASE', 'P1-B6-REP-N', 'P1-B6-REPWORD-WORD', 'P1-B6-REP-LIST']:
        if fid in ids:
            fail(f'{fid} is still a placeholder')
    for fid in PENDING:
        if fid not in ids:
            fail(f'{fid} is pending but not a placeholder')
    for fid in sorted(i for i in ids if i.startswith('P1-B6-')):
        if fid not in PENDING:
            fail(f'{fid} is a placeholder but neither filled nor pending')
    for fid in ('P1-ABS-PART1', 'P1-RECOMPUTE'):
        if fid in ids:
            fail(f'{fid} is still a placeholder (RL-147 §8)')
    for t in S8_NEW + [fills['P1-ABS-PART1-CLAUSE']]:
        if flat.count(norm(t)) != 1:
            fail(f'RL-147 §8 text not in paper1.md once: {t[:70]!r}')
    for t in S8_GONE:
        if t in flat:
            fail(f'stale text still in paper1.md: {t!r}')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--outputs', type=pathlib.Path, default=DEFAULT_OUTPUTS)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--manifest', type=pathlib.Path)
    args = ap.parse_args()
    restricted, public, structure = load_outputs(args.outputs)
    attempts = check_side_inputs()
    X = load_extras()
    R, P, S = Src('restricted', restricted), Src('public', public), Src('structure', structure)
    fills, branch = render_all(R, P, S, attempts, X)
    paper = PAPER.read_text()
    if args.apply:
        paper = apply(paper, fills, branch)
        PAPER.write_text(paper)
    if args.manifest:
        with args.manifest.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['marker', 'file', 'key_path', 'raw', 'printed', 'format', 'label'],
                               delimiter='\t', lineterminator='\n')
            w.writeheader()
            w.writerows(MANIFEST)
    check(paper, fills, branch)
    for msg in FAILURES:
        print('FAIL', msg)
    print(f'{len(fills)} fills rendered; {len(MANIFEST)} printed elements by key; '
          f'{"PASS" if not FAILURES else f"{len(FAILURES)} failures"}')
    return 0 if not FAILURES else 1


if __name__ == '__main__':
    sys.exit(main())
