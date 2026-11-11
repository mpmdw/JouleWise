"""Checks every Block 5 value filled into paper1.md against the Block 5 print authority.

RL-24 seat 12 (the Block 5 fill), updated for the RL-52 extended ledger.
The NEW PRINT AUTHORITY SHA is recorded in docs/analysis/b5/REDERIVATION.md.
Ledger rows are physical TSV line numbers (header = row 1), as that document defines them.

For each filled site this script renders the expected text from the ledger rows it cites and requires
that text in paper1.md (whitespace-normalised) exactly as often as stated. It also checks that:

- the full ledger matches the final RL-55 authority hash, and its original 538 rows
  (plus header) are byte-identical to the RL-43 authority at 0b8763f0a;
- every cited row passes the RL-42 gate (check word exact, within-rounding, recorded-judgment or
  single-source; `paper1` column not `not-printed`), and every `print-labelled` row is printed with its label;
- the literal text of a filled site carries no digit of its own: every number comes from a ledger row;
- no filled id, and no id of a deleted branch, is still a placeholder; every pending id still is;
- the deleted branches are gone, and branches 5.4.B and 5.5.1 are each derived twice, once from the
  table and once from the registered rule text, and both derivations agree with the selection.

Run from the repository root: python3 -I docs/paper/paper1/fill_check_b5.py
On a pre-first-fill branch use --paper-ref with the admitted first-fill commit;
the default remains a strict working-tree paper check. --repo-only checks the
full/prefix authority and numeric branch prerequisites without reading a paper.
Exit status 0 when every check passes, 1 otherwise. Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
PAPER = ROOT / 'docs/paper/paper1/paper1.md'
LEDGER = ROOT / 'docs/analysis/b5/rederivation.tsv'
PLAN = ROOT / 'configs/campaigns/v5_claim_25g83/analysis_plan_block5.md'
ORIGINAL_AUTHORITY_COMMIT = '0b8763f0a8291bfa5d47fdc18aa64ef3aa33ec1b'
ORIGINAL_AUTHORITY_SHA256 = '0462f8144388e758ec1461452828309c4968ac39d2f986ef4a15175d07b84343'
AUTHORITY_SHA256 = '2f15d0810ae6123c42871e7101e880440e4c46ad350f707058d3fd5e7a988469'
PASSING = {'exact', 'within-rounding', 'recorded-judgment', 'single-source'}
PRINTABLE = {'print', 'print-labelled'}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


# ---------------------------------------------------------------- ledger

def check_ledger_bytes(raw: bytes, original: bytes) -> None:
    digest = hashlib.sha256(raw).hexdigest()
    if digest != AUTHORITY_SHA256:
        fail(f'ledger SHA-256 {digest} is not the extended print authority {AUTHORITY_SHA256}')
    if hashlib.sha256(original).hexdigest() != ORIGINAL_AUTHORITY_SHA256:
        fail(f'original authority at {ORIGINAL_AUTHORITY_COMMIT} has an unexpected SHA-256')
    if b''.join(raw.splitlines(keepends=True)[:539]) != original:
        fail(f'original 538 rows (plus header) differ from {ORIGINAL_AUTHORITY_COMMIT}')


def load_ledger() -> dict[int, dict[str, str]]:
    raw = LEDGER.read_bytes()
    original = subprocess.run(['git', 'show', f'{ORIGINAL_AUTHORITY_COMMIT}:docs/analysis/b5/rederivation.tsv'],
                              cwd=ROOT, check=True, capture_output=True).stdout
    check_ledger_bytes(raw, original)
    rows = list(csv.reader(raw.decode('utf-8').splitlines(), delimiter='\t', quoting=csv.QUOTE_NONE))
    header = rows[0]
    return {i: dict(zip(header, r)) for i, r in enumerate(rows, start=1) if i > 1}


L: dict[int, dict[str, str]] = {}


def val(n: int) -> str:
    return L[n]['printed_value']


def num(n: int) -> float:
    return float(val(n).replace('−', '-').replace('+', '').replace('%', ''))


SUP = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')


def render_value(n: int, fmt: str | None) -> str:
    v = val(n)
    if fmt is None:
        return v
    if fmt == 'w':  # outcome code printed as words
        return v.replace('_', ' ')
    if fmt == 'sci':  # 1.2033e-15 -> 1.2033 × 10⁻¹⁵
        mant, exp = v.split('e')
        return f'{mant} × 10{str(int(exp)).translate(SUP)}'
    raise ValueError(fmt)


PH = re.compile(r'\{r(\d+)(?::(\w+))?\}')
FILL_RE = re.compile(r'\{\{FILL:.*?\}\}', re.S)
ALLOWED_LITERAL_DIGITS = ['Qwen3-1.7B', 'Qwen3-8B', '1.7B', '8B', '2,048', '95%']


def norm(s: str) -> str:
    return ' '.join(s.split())


# ---------------------------------------------------------------- sites
# (name, ids filled at this site, template, expected count, labels required for print-labelled rows)

T1 = [
    ('Table 1, 1.7B decode', ['P1-B5-NR-1p7B-decode', 'P1-B5-NB-1p7B-decode'], '| 1.7B decode | {r139} | {r140} |'),
    ('Table 1, 1.7B prefill', ['P1-B5-NR-1p7B-prefill', 'P1-B5-NB-1p7B-prefill'], '| 1.7B prefill (2,048) | {r148} | {r149} |'),
    ('Table 1, 8B decode', ['P1-B5-NR-8B-decode', 'P1-B5-NB-8B-decode'], '| 8B decode | {r157} | {r158} |'),
    ('Table 1, 8B prefill', ['P1-B5-NR-8B-prefill', 'P1-B5-NB-8B-prefill'], '| 8B prefill (2,048) | {r166} | {r167} |'),
    ('Table 1, decode contrast', ['P1-B5-NQ-decode'], '| Contrast, decode | — | {r11} |'),
    ('Table 1, prefill contrast', ['P1-B5-NQ-prefill'], '| Contrast, prefill (2,048) | — | {r13} |'),
]

T2 = [
    ('Table 2, 1.7B decode', ['E_1p7B_decode_J_per_request', 'E_1p7B_decode_lower_J', 'E_1p7B_decode_upper_J',
                              'E_1p7B_decode_J_per_token', 'P1-B5-AF-1p7B-decode'],
     '| Qwen3-1.7B | decode | {r133} | [{r134}, {r135}] | {r141} | {r138} |'),
    ('Table 2, 1.7B prefill', ['E_1p7B_prefill_p2048_J_per_request', 'E_1p7B_prefill_p2048_lower_J',
                               'E_1p7B_prefill_p2048_upper_J', 'E_1p7B_prefill_p2048_J_per_token', 'P1-B5-AF-1p7B-prefill'],
     '| Qwen3-1.7B | prefill (2,048) | {r142} | [{r143}, {r144}] | {r150} | {r147} |'),
    ('Table 2, 8B decode', ['E_8B_decode_J_per_request', 'E_8B_decode_lower_J', 'E_8B_decode_upper_J',
                            'E_8B_decode_J_per_token', 'P1-B5-AF-8B-decode'],
     '| Qwen3-8B | decode | {r151} | [{r152}, {r153}] | {r159} | {r156} |'),
    ('Table 2, 8B prefill', ['E_8B_prefill_p2048_J_per_request', 'E_8B_prefill_p2048_lower_J',
                             'E_8B_prefill_p2048_upper_J', 'E_8B_prefill_p2048_J_per_token', 'P1-B5-AF-8B-prefill'],
     '| Qwen3-8B | prefill (2,048) | {r160} | [{r161}, {r162}] | {r168} | {r165} |'),
]

# Absolute floor = the cell's drift-widened guarded absolute floor (hand-check key `.../absolute.minted`;
# rows 290 and 293 name it directly for 8B). Operative floor = the arm's `floor_gate_j` (rows 53-57).
T3 = [
    ('Table 3, 1.7B decode', ['F_1p7B_decode_abs_J', 'F_1p7B_decode_operative_J'],
     '| Qwen3-1.7B | decode | {r53} | {{FILL: F_1p7B_decode_cmp_J \\| comparative operative floor}} | {r53} |'),
    ('Table 3, 1.7B prefill', ['F_1p7B_prefill_p2048_abs_J', 'F_1p7B_prefill_p2048_operative_J'],
     '| Qwen3-1.7B | prefill (2,048) | {r56} | {{FILL: F_1p7B_prefill_p2048_cmp_J \\| comparative}} | {r56} |'),
    ('Table 3, 8B decode', ['F_8B_decode_abs_J', 'F_8B_decode_operative_J'],
     '| Qwen3-8B | decode | {r290} | {{FILL: F_8B_decode_cmp_J \\| comparative}} | {r54} |'),
    ('Table 3, 8B prefill', ['F_8B_prefill_p2048_abs_J', 'F_8B_prefill_p2048_operative_J'],
     '| Qwen3-8B | prefill (2,048) | {r293} | {{FILL: F_8B_prefill_p2048_cmp_J \\| comparative}} | {r57} |'),
]

T4 = [
    ('Table 4, 1.7B decode R_cm', ['R_cm_1p7B_decode_cmp'], '{{FILL: TERM_A_1p7B_decode_cmp_J \\| point}}) | {r276} |'),
    ('Table 4, 1.7B prefill R_cm', ['R_cm_1p7B_prefill_p2048_cmp'], '{{FILL: TERM_A_1p7B_prefill_p2048_cmp_J \\| point}}) | {r277} |'),
    ('Table 4, 8B decode R_cm', ['R_cm_8B_decode_cmp'], '{{FILL: TERM_A_8B_decode_cmp_J \\| point}}) | {r278} |'),
    ('Table 4, 8B prefill R_cm', ['R_cm_8B_prefill_p2048_cmp'], '{{FILL: TERM_A_8B_prefill_p2048_cmp_J \\| point}}) | {r279} |'),
]

T5 = [
    ('Table 5, decode', ['E_decode_contrast_signed_J_per_request', 'P1-B5-CTR-decode-METRO', 'E_decode_contrast_lower_J',
                         'E_decode_contrast_upper_J', 'F_claim_decode_armwise_max_J', 'P1-B5-CTR-decode-PADJ',
                         'P1-B5-CTR-decode-OUTCOME', 'P1-B5-CTR-decode-LEVEL'],
     '| decode | {r11} | {r15} | [{r36}, {r37}] | [{r48}, {r49}] | {r52} | {r60:sci} | {r530:w} | {r532} |'),
    ('Table 5, prefill', ['E_prefill_p2048_contrast_signed_J_per_request', 'P1-B5-CTR-prefill-METRO',
                          'E_prefill_p2048_contrast_lower_J', 'E_prefill_p2048_contrast_upper_J',
                          'F_claim_prefill_p2048_armwise_max_J', 'P1-B5-CTR-prefill-PADJ',
                          'P1-B5-CTR-prefill-OUTCOME', 'P1-B5-CTR-prefill-LEVEL'],
     '| prefill (2,048) | {r13} | {r16} | [{r38}, {r39}] | [{r50}, {r51}] | {r55} | {r61:sci} | {r533:w} | {r535} |'),
]

LABEL_RJ = ['recorded output', 'collection-time records']

PROSE = [
    ('Table 5 caption, claim level (RL-41 b)', [],
     'Both contrasts reach level {r532} under the registered gate; the claim level is the gate\'s recorded output. '
     'The gate\'s eligibility inputs (selection, the absence of top-ups, replacement validity, transport and current '
     'checks) are collection-time records; we did not re-derive them.', LABEL_RJ),
    ('Section 6.1, losses and skew (RL-4 v)', [],
     'The registered exclusion rules removed {r432} of the {r433} planned contrast quads, keeping {r11} of {r12} for '
     'decode and {r13} of {r14} for 2,048-token prefill; the prefill contrast therefore rests on the registered minimum '
     'of {r181} quads. A removed member removes its whole quad, so every removal takes both models\' runs alike, but '
     'the members that triggered removal were not balanced: {r223} of the {r224} were on the 8B side and {r225} on the '
     '1.7B side, and all {r226} decode removals were triggered by an 8B member. Contention (an outside process above '
     '{r182} CPU-s/s in a {r183} s interval overlapping the request) fired on {r227} triggering members on the 8B side '
     'and {r228} on the 1.7B side, an aborted idle admission on {r229} and {r230}, and an unbounded clock anchor on '
     '{r231}, on the 8B side. *Exploratory, derived after release:* one reading is exposure, since an 8B request runs '
     'longer (about {r236} times as long in decode and {r237} times in prefill, from the independent recomputation '
     'only), so a background process at a fixed rate overlaps 8B requests more often. This reading is not '
     'established.', ['from the independent recomputation only']),
    ('Section 6.5, branch 5.5.1, decode', ['P1-B5-CTR-PHASE', 'P1-B5-CTR-DBAR', 'P1-B5-CTR-DI', 'P1-B5-CTR-GATE'],
     'On this stack and boundary, the 8B model\'s decode phase used more gross processor-rail energy per request than '
     'the 1.7B model\'s, by {r15} J (decision interval [{r48}, {r49}] J, whose statistical part is the within-session '
     '95% interval [{r36}, {r37}] J). The estimate exceeds the floor gate of {r52} J, both intervals exclude zero, '
     'Holm\'s correction rejects, and leaving out any one quad changes none of these. This is a comparative ({r532}) '
     'result under the registered claim gate, for this one prompt, this prompt length and this machine, from one '
     'session in which {r11} of {r12} planned quads were kept. Phase attribution is reported without a measured '
     'instrument phase-accounting check.', ['registered claim gate']),
    ('Section 6.5, branch 5.5.1, prefill', ['P1-B5-CTR-PHASE', 'P1-B5-CTR-DBAR', 'P1-B5-CTR-DI', 'P1-B5-CTR-GATE'],
     'On this stack and boundary, the 8B model\'s 2,048-token prefill phase used more gross processor-rail energy per '
     'request than the 1.7B model\'s, by {r16} J (decision interval [{r50}, {r51}] J, whose statistical part is the '
     'within-session 95% interval [{r38}, {r39}] J). The estimate exceeds the floor gate of {r55} J, both intervals '
     'exclude zero, Holm\'s correction rejects, and leaving out any one quad changes none of these. This is a '
     'comparative ({r535}) result under the registered claim gate, for this one prompt, this prompt length and this '
     'machine, from one session in which {r13} of {r14} planned quads were kept, the registered minimum of {r181}. '
     'Phase attribution is reported without a measured instrument phase-accounting check.', ['registered claim gate']),
    ('Section 6.5, leave-one-quad-out', ['P1-B5-CTR-LOO'],
     '**Leave-one-quad-out.** Decode: no single quad changes the verdict; the {r62} leave-one-out estimates run from '
     '{r63} to {r64} J. Prefill: no single quad changes the verdict; the {r65} leave-one-out estimates, each over {r66} '
     'quads, one fewer than the cell minimum of {r505}, run from {r67} to {r68} J.', []),
    ('Section 6.5, decision interval against the floor', ['P1-B5-CTR-DIFLOOR'],
     '**Decision interval against the floor.** In both contrasts the near end of the decision interval lies beyond '
     'the floor gate: {r48} J against {r52} J for decode, and {r50} J against {r55} J for 2,048-token prefill.', []),
    ('Section 6.5, descriptive ratios and per-token differences',
     ['P1-B5-RATIO-decode', 'P1-B5-RATIO-prefill', 'P1-B5-PERTOK-decode', 'P1-B5-PERTOK-prefill'],
     'The 8B-to-1.7B ratio of phase energies was {r114} (the geometric mean over kept quads of the per-quad ratio; '
     't interval [{r115}, {r116}]) for decode and {r117} (same quantity; t interval [{r118}, {r119}]) for 2,048-token '
     'prefill. Per token, the difference was {r120} (metrology interval [{r124}, {r125}]; decision interval '
     '[{r128}, {r129}]) J per output token and {r122} (metrology interval [{r126}, {r127}]; decision interval '
     '[{r130}, {r131}]) J per prompt token.', []),
    ('Section 6.5, battery-assist and load-correlated lines', ['P1-B5-CTR-BATT'],
     '*Without quads holding battery-assisted runs:* no quad held a battery-assisted run ({r341} such quads, from the '
     'collection record\'s battery-assist flags; not re-derived), so this line equals the primary estimate: '
     'd̄ = {r15} J, metrology interval [{r36}, {r37}] J, n = {r11} for decode, and d̄ = {r16} J, metrology interval '
     '[{r38}, {r39}] J, n = {r13} for 2,048-token prefill. *Load-correlated exclusions not applied:* the registered '
     'pipeline could not compute this line; the independent recomputation\'s value, uncompared, is d̄ = {r376} J '
     '(metrology interval [{r377}, {r378}] J, n = {r379}, {r380} quads restored) for decode and {r381} J '
     '([{r382}, {r383}] J, n = {r384}, {r385} restored) for 2,048-token prefill.',
     ['from the collection record', 'not re-derived']),
]

SITES = [(n, ids, t, 1, []) for n, ids, t in T1 + T2 + T3 + T4]
SITES += [(n, ids, t, 1, LABEL_RJ) for n, ids, t in T5]
SITES += [(n, ids, t, 1, lab) for n, ids, t, lab in PROSE]

# A print-labelled row in a table cell carries its label in the table note (RL-42), which is its own site.
LABEL_SITE = {'Table 5, decode': 'Table 5 caption, claim level (RL-41 b)',
              'Table 5, prefill': 'Table 5 caption, claim level (RL-41 b)'}

# Ids whose placeholders this seat replaced (the RL-24 seat-12 report lists each with its rows).
FILLED = sorted({i for _, ids, _, _, _ in SITES for i in ids})

# Ids that left the text with their unselected branch (5.1.a, 5.2.a, 5.5.2 to 5.5.5).
DELETED_WITH_BRANCH = ['P1-B5-NOPACK', 'P1-B5-NOPACK-REASON', 'P1-B5-CELL-REFUSED', 'P1-B5-CELL-REFUSED-REASON',
                       'P1-B5-CTR-L1-REASON', 'P1-B5-CTR-UNRES-REASON', 'P1-B5-CTR-NR-REASON', 'P1-B5-CTR-NE-REASON']

# Block 5 ids left as placeholders (no ledger row, or the id also needs Block 6 or a later ruling).
PENDING = (['P1-B5-METER', 'P1-B5-ATTEMPTS', 'P1-B5-ANALYSED', 'P1-B5-HAZARDS', 'P1-B5-INTERVAL-PARTS',
            'P1-B5-B-SHARE', 'P1-B5-BATT-LINE', 'P1-B5-LOAD-LINE', 'P1-B5-DOM-FAILED', 'P1-B5-DOM-REFUSED',
            'P1-B5-XWIN', 'P1-B5-NEG8', 'P1-B5-MONITOR', 'P1-B5-RM-ctr-decode', 'P1-B5-RM-ctr-prefill',
            'P1-RECOMPUTE-SUMMARY', 'P1-ABS-PART1', 'CP-X01-identity', 'CP-X01-length',
            'CP-X02-conclusion', 'CP-X08-decode-a-conclusion']
           + [f'P1-B5-{k}-{c}' for k in ('RM', 'FN') for c in ('1p7B-decode', '1p7B-prefill', '8B-decode', '8B-prefill')]
           + [f'F_{c}_cmp_J' for c in ('1p7B_decode', '1p7B_prefill_p2048', '8B_decode', '8B_prefill_p2048')]
           + [f'{p}{c}_{f}{s}' for c in ('1p7B_decode', '1p7B_prefill_p2048', '8B_decode', '8B_prefill_p2048')
              for f in ('abs', 'cmp') for p, s in (('R_', ''), ('TERM_A_', '_J'), ('TERM_B_', '_J'))])

GONE = ['[BRANCH 5.1.a', '[END BRANCH 5.1]', '[BRANCH 5.2.a', '[END BRANCH 5.2]', '[BRANCH 5.4.A', '[END BRANCH 5.4.A]',
        '[BRANCH 5.4.B', '[END BRANCH 5.4.B]'] + [f'BRANCH 5.5.{k}' for k in range(1, 6) if k != 1] + \
       ['[BRANCH 5.5.1', '[END BRANCH 5.5.1]']
PRESENT = ['BRANCH 5.1.a not selected', 'BRANCH 5.2.a not selected', 'BRANCH 5.4.B selected',
           'BRANCH 5.5.1 selected for both contrasts', '**[BRANCH 5.4.R', '**[END BRANCH 5.4.R]**']


# ---------------------------------------------------------------- checks

def check_sites(paper: str) -> None:
    npaper = norm(paper)
    for name, ids, template, count, labels in SITES:
        literal = FILL_RE.sub('', PH.sub('', template))
        for tok in ALLOWED_LITERAL_DIGITS:
            literal = literal.replace(tok, '')
        if re.search(r'\d', literal):
            fail(f'{name}: literal text carries a number not taken from a ledger row: {literal!r}')
        for m in PH.finditer(template):
            n = int(m.group(1))
            row = L.get(n)
            if row is None:
                fail(f'{name}: row {n} does not exist')
                continue
            if row['match'] not in PASSING:
                fail(f'{name}: row {n} has check word {row["match"]!r}')
            if row['paper1'] not in PRINTABLE:
                fail(f'{name}: row {n} is {row["paper1"]!r}')
            if row['paper1'] == 'print-labelled':
                where = template + ''.join(t for nm, _, t, _, _ in SITES if nm == LABEL_SITE.get(name))
                if not labels or any(lab not in where for lab in labels):
                    fail(f'{name}: row {n} is print-labelled ({row["match"]}) but the site lacks its label')
        rendered = PH.sub(lambda m: render_value(int(m.group(1)), m.group(2)), template)
        found = npaper.count(norm(rendered))
        if found != count:
            fail(f'{name}: expected {count} occurrence(s) of the ledger-rendered text, found {found}:\n    {rendered}')


def check_placeholders(paper: str) -> None:
    def present(fid: str) -> bool:
        return re.search(r'\{\{FILL:\s*' + re.escape(fid) + r'\s*(?:\\\||\|)', paper) is not None
    for fid in FILLED + DELETED_WITH_BRANCH:
        if present(fid):
            fail(f'{fid}: placeholder still present after the fill')
    for fid in PENDING:
        if not present(fid):
            fail(f'{fid}: listed as pending but no placeholder found (update this check with its ledger row)')
    for s in GONE:
        if s in paper:
            fail(f'deleted branch marker still present: {s!r}')
    for s in PRESENT:
        if s not in paper:
            fail(f'expected selection record missing: {s!r}')


def check_floor_roles() -> None:
    """Rows 53/56 print as the absolute floor: their hand check re-derived the absolute minted floor."""
    for n, key in [(53, 'floor.Qwen3-1.7B-4bit/decode/absolute.minted'), (54, 'floor.Qwen3-8B-4bit/decode/absolute.minted'),
                   (56, 'floor.Qwen3-1.7B-4bit/prefill/absolute.minted'), (57, 'floor.Qwen3-8B-4bit/prefill/absolute.minted'),
                   (290, 'floor.Qwen3-8B-4bit/decode/absolute.minted'), (293, 'floor.Qwen3-8B-4bit/prefill/absolute.minted')]:
        if L[n]['hand_check'] != key:
            fail(f'row {n}: hand-check key {L[n]["hand_check"]!r}, expected {key!r}')
    for a, b in [(54, 290), (57, 293)]:
        if val(a) != val(b):
            fail(f'rows {a} and {b} disagree: {val(a)} vs {val(b)}')
    for n, part in [(53, 'arm_gates[0]'), (54, 'arm_gates[1]'), (56, 'arm_gates[0]'), (57, 'arm_gates[1]')]:
        if f'.floor.{part}.floor_gate_j' not in L[n]['note']:
            fail(f'row {n}: note does not name .floor.{part}.floor_gate_j')


# ---------------------------------------------------------------- branch derivations

def derive_54_table() -> str:
    thr = num(275)
    rcm = {n: num(n) for n in (276, 277, 278, 279)}
    below = [n for n, v in rcm.items() if v < thr]  # equality passes (row 275 note)
    if len(below) != 3 or val(518) != 'three':
        fail(f'5.4 table derivation: {len(below)} R_cm below {thr}; row 518 says {val(518)!r}')
    branch = '5.4.B' if below else 'undetermined (the eight R are not in the table)'
    print(f'5.4, from the table: R_cm rows 276-279 = {[val(n) for n in rcm]}; threshold row 275 = {val(275)}; '
          f'below: rows {below}. Branch condition "at least one of the twelve ratios is below 2" holds -> {branch}.')
    return branch


def derive_54_rule() -> str:
    plan = PLAN.read_text()
    rule = ('**Branch A** (every one of the eight R ≥ 2 and every required R_cm ≥ 2) licenses the dominance sentence '
            'and the contingent subtitle; otherwise **branch B** reports each failed component with null framing.')
    if norm(rule) not in norm(plan):
        fail('5.4 rule derivation: the registered branch rule was not found verbatim in analysis plan §6')
    if 'R ≥ 2 (equality passes)' not in plan:
        fail('5.4 rule derivation: the registered threshold sentence was not found in analysis plan §6')
    required_rcm = [num(n) for n in (276, 277, 278, 279)]  # four required: 2 models x 2 phases, comparative
    eight_r = None  # not in the print authority
    all_rcm = all(v >= 2 for v in required_rcm)
    if not all_rcm:
        branch = '5.4.B'
    elif eight_r is None:
        branch = 'undetermined'
    else:
        branch = '5.4.A' if all(v >= 2 for v in eight_r) else '5.4.B'
    print(f'5.4, from the registered rule (analysis plan §6): branch A needs all eight R >= 2 AND every required '
          f'R_cm >= 2; required R_cm = {required_rcm}; a required R_cm fails, so A cannot hold whatever the eight R '
          f'are -> {branch}.')
    return branch


def holm(ps: list[float], alpha: float) -> list[tuple[float, bool]]:
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    running = 0.0
    for k, i in enumerate(order):
        running = max(running, min(1.0, (m - k) * ps[i]))
        adj[i] = running
    return [(a, a <= alpha) for a in adj]


CONTRASTS = {
    'decode': dict(dbar=15, gate=52, mlo=36, mhi=37, dlo=48, dhi=49, raw=58, adj=60, loo_lo=63, loo_hi=64,
                   outcome=530, direction=531, level=532),
    'prefill': dict(dbar=16, gate=55, mlo=38, mhi=39, dlo=50, dhi=51, raw=59, adj=61, loo_lo=67, loo_hi=68,
                    outcome=533, direction=534, level=535),
}


def derive_551_table(c: str) -> str:
    r = CONTRASTS[c]
    o, d, lv = val(r['outcome']), val(r['direction']), val(r['level'])
    if o == 'direction_supported' and d == 'positive' and lv == 'L2':
        b = '5.5.1'
    elif o == 'direction_supported':
        b = '5.5.2'
    else:
        b = {'unresolved': '5.5.3', 'not_resolvable': '5.5.4', 'not_estimable': '5.5.5'}.get(o, '?')
    print(f'5.5 {c}, from the table: outcome row {r["outcome"]} = {o}, direction row {r["direction"]} = {d}, '
          f'level row {r["level"]} = {lv} -> {b}.')
    return b


def derive_551_rule(c: str) -> str:
    plan = PLAN.read_text()
    for s in ['`effect_not_above_floor` (|dbar| ≤ `floor_gate_j`)', '3. **`unresolved`** if the metrology interval contains 0, or Holm does not reject.',
              'the direction equals the registered direction (positive).']:
        if norm(s) not in norm(plan):
            fail(f'5.5 rule derivation: registered text not found in analysis plan §7.2: {s!r}')
    r = CONTRASTS[c]
    dbar, gate = num(r['dbar']), num(r['gate'])
    mlo, mhi, dlo, dhi = (num(r[k]) for k in ('mlo', 'mhi', 'dlo', 'dhi'))
    alpha, m = num(8), int(num(7))
    adj = holm([num(58), num(59)], alpha)
    ai = 0 if c == 'decode' else 1
    adj_p, rejected = adj[ai]
    if abs(adj_p - num(r['adj'])) > 1e-3 * num(r['adj']) or m != 2:
        fail(f'5.5 {c}: Holm-adjusted p from raw rows {adj_p:.4e} disagrees with row {r["adj"]} {val(r["adj"])}')
    steps = []
    # 1. not_estimable: its codes are recorded judgments (RL-42); an estimate and floor exist, so none is shown.
    # 2. not_resolvable
    effect_not_above = abs(dbar) <= gate
    obscures = (dlo <= 0 <= dhi) and not (mlo <= 0 <= mhi)
    steps.append(f'|dbar| {dbar} > gate {gate}: {not effect_not_above}; decision interval [{dlo}, {dhi}] '
                 f'excludes 0: {not (dlo <= 0 <= dhi)}')
    # 3. unresolved
    metro_has_zero = mlo <= 0 <= mhi
    steps.append(f'metrology interval [{mlo}, {mhi}] excludes 0: {not metro_has_zero}; Holm (m={m}, alpha={alpha}) '
                 f'adjusted p {adj_p:.4e} rejects: {rejected}')
    if effect_not_above or obscures:
        outcome = 'not_resolvable'
    elif metro_has_zero or not rejected:
        outcome = 'unresolved'
    else:
        outcome = 'direction_supported'
    direction = 'positive' if dbar > 0 else 'negative'
    # L2: LOO not verdict-influential (sign and floor status kept by every LOO estimate), registered direction.
    loo_lo, loo_hi = num(r['loo_lo']), num(r['loo_hi'])
    loo_ok = loo_lo > gate and loo_lo > 0
    steps.append(f'LOO estimates [{loo_lo}, {loo_hi}] keep sign and stay above the gate: {loo_ok}')
    mag = max(abs(loo_lo - dbar), abs(loo_hi - dbar))
    if mag > 0.25 * gate:
        fail(f'5.5 {c}: loo_magnitude_influential would be raised ({mag} > {0.25 * gate}); its fixed sentence is owed')
    steps.append(f'largest LOO shift {mag:.4f} J <= 0.25 x gate {0.25 * gate:.4f} J: magnitude concern not raised')
    if not dlo > gate:
        fail(f'5.5 {c}: decision interval near end {dlo} is not beyond the gate {gate}; the fixed sentence is owed')
    rj = all(val(n) == 'none' for n in (525, 526))
    steps.append(f'no top-up and no valid replacement (rows 525, 526, recorded judgments): {rj}')
    l2 = outcome == 'direction_supported' and loo_ok and direction == 'positive' and rj
    b = '5.5.1' if l2 else ('5.5.2' if outcome == 'direction_supported' else outcome)
    print(f'5.5 {c}, from the registered rule (analysis plan §7.2): ' + '; '.join(steps) +
          f' -> outcome {outcome}, direction {direction}, L2 conditions met (given the recorded judgments): {l2} -> {b}.')
    return b


def check_branches() -> None:
    a, b = derive_54_table(), derive_54_rule()
    if not (a == b == '5.4.B'):
        fail(f'branch 5.4: table derivation {a!r}, rule derivation {b!r}, selected 5.4.B')
    for c in CONTRASTS:
        a, b = derive_551_table(c), derive_551_rule(c)
        if not (a == b == '5.5.1'):
            fail(f'branch 5.5 {c}: table derivation {a!r}, rule derivation {b!r}, selected 5.5.1')
    if val(509) != 'one':
        fail('branch 5.1.a: row 509 no longer says one analysed attempt per pack')


def main(argv=()) -> int:
    global L
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--paper-ref', help='local Git commit/ref containing the admitted first fill; no network')
    modes.add_argument('--repo-only', action='store_true', help='check ledger authority and branch arithmetic only')
    args = parser.parse_args(argv)
    FAILURES.clear()
    L = load_ledger()
    if not args.repo_only:
        if args.paper_ref:
            commit = subprocess.run(['git', 'rev-parse', '--verify', '--end-of-options', args.paper_ref+'^{commit}'],
                                    cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
            paper = subprocess.run(['git', 'show', commit+':docs/paper/paper1/paper1.md'],
                                   cwd=ROOT, check=True, capture_output=True, text=True).stdout
            print('Paper input: local Git commit '+commit)
        else:
            paper = PAPER.read_text()
        check_sites(paper)
        check_placeholders(paper)
    check_floor_roles()
    check_branches()
    rows = sorted({int(m.group(1)) for _, _, t, _, _ in SITES for m in PH.finditer(t)})
    print(f'sites: {len(SITES)}; filled ids: {len(FILLED)}; deleted with branch: {len(DELETED_WITH_BRANCH)}; '
          f'pending ids: {len(PENDING)}; ledger rows cited: {len(rows)}')
    if FAILURES:
        print(f'FAIL: {len(FAILURES)} problem(s)')
        for f in FAILURES:
            print('  - ' + f)
        return 1
    print(('PASS: repository ledger/branch checks only; paper not checked; SHA-256 ' if args.repo_only else
           'PASS: every filled Block 5 value equals its row of the extended ledger; SHA-256 ') + AUTHORITY_SHA256)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
