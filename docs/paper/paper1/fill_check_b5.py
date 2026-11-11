"""Checks every Block 5 value filled into paper1.md against the Block 5 print authority.

RL-24 seat 12 (the first Block 5 fill) and the second fill (RL-52 sequence step 2, RL-55).
The NEW PRINT AUTHORITY SHA is recorded in docs/analysis/b5/REDERIVATION.md.
Ledger rows are physical TSV line numbers (header = row 1), as that document defines them.

For each filled site this script renders the expected text from the ledger rows it cites and requires
that text in paper1.md (whitespace-normalised) exactly as often as stated. It also checks that:

- the full ledger matches the final RL-55 authority hash, and its original 538 rows
  (plus header) are byte-identical to the RL-43 authority at 0b8763f0a;
- every cited row passes the RL-42 gate (check word exact, within-rounding, recorded-judgment or
  single-source; `paper1` column not `not-printed`), and every `print-labelled` row is printed with its label;
- (RL-52 print precision, a) every printed value is its row rounded once by the RL-52 rule: each row is
  classed from its key (energy, per-token, R, magnitude ratio, share, p, count, word, or a quantity outside the
  rule's table that prints as issued), the format a site applies must belong to that class, and one row is
  printed with one format everywhere;
- (RL-52 print precision, b) every comparison the paper states and every registered threshold test holds on the
  ledger values and again on the printed (rounded) values;
- the literal text of a filled site carries no digit of its own: every number comes from a ledger row, or is one
  of the few names and registered constants in ALLOWED_LITERALS, each verified against its source;
- the analysed-attempt identifiers and dates equal configs/analysis/b5/analysed_windows.json (RL-52 (3));
- rows 647-651 print only beside the registered refusal rows 1064-1065 with the label "recompute only; not
  compared" (Opus F4);
- no filled id, and no id of a deleted branch or dropped sentence, is still a placeholder; every pending id
  still is;
- the deleted branches are gone, and branches 5.4.B, 5.4.R (not selected), 5.5.1 and 9.D are each derived
  twice, once from the table and once from the registered rule text, and both derivations agree with the
  selection.

Rounding (RL-52): estimates to nearest (ties away from zero), interval and range ends outward, floors up. RL-52
gives no direction for bounds, half-widths and allowances; this check rounds them up, like floors, which keeps
"bound = max(terms)" and "allowance = max(bound, excursion)" true on the printed values.

Run from the repository root: python3 -I docs/paper/paper1/fill_check_b5.py
--paper-ref checks the paper at a local Git commit instead of the working tree; --repo-only checks the
full/prefix authority and the branch and comparison arithmetic without reading a paper.
Exit status 0 when every check passes, 1 otherwise. Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import math
import pathlib
import re
import subprocess
import sys
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal

ROOT = pathlib.Path(__file__).resolve().parents[3]
PAPER = ROOT / 'docs/paper/paper1/paper1.md'
LEDGER = ROOT / 'docs/analysis/b5/rederivation.tsv'
PLAN = ROOT / 'configs/campaigns/v5_claim_25g83/analysis_plan_block5.md'
INDEX = ROOT / 'configs/analysis/b5/analysed_windows.json'
DEVLOG = ROOT / 'docs/analysis/b5/DEVIATION-LOG.md'
ORIGINAL_AUTHORITY_COMMIT = '0b8763f0a8291bfa5d47fdc18aa64ef3aa33ec1b'
ORIGINAL_AUTHORITY_SHA256 = '0462f8144388e758ec1461452828309c4968ac39d2f986ef4a15175d07b84343'
AUTHORITY_SHA256 = '41b7e577a7be494245ed42ba38190da9de860430a75f5dc6d0987a15de79060f'
PASSING = {'exact', 'within-rounding', 'recorded-judgment', 'single-source'}
PRINTABLE = {'print', 'print-labelled'}

FAILURES: list[str] = []
NOTES: list[str] = []


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


def dec(n: int) -> Decimal:
    return Decimal(val(n).replace('−', '-').replace('+', ''))


def num(n: int) -> float:
    return float(dec(n))


# ---------------------------------------------------------------- RL-52 print precision

NUMERIC = re.compile(r'[+\-−]?(\d+(\.\d*)?|\.\d+)([eE][+\-]?\d+)?')
INTEGER = re.compile(r'[+\-−]?\d+')
MODE = {'near': ROUND_HALF_UP, 'down': ROUND_FLOOR, 'up': ROUND_CEILING}

# format -> (kind, digits, direction).  'dp' = decimal places, 'sf' = significant figures.
ROUNDERS = {
    # energies, interval ends, floors, bounds and allowances in J per request: two decimals
    'e': ('dp', 2, 'near'), 'lo': ('dp', 2, 'down'), 'hi': ('dp', 2, 'up'), 'up': ('dp', 2, 'up'),
    # per-token values: four significant figures
    'tok': ('sf', 4, 'near'), 'toklo': ('sf', 4, 'down'), 'tokhi': ('sf', 4, 'up'),
    # magnitude ratios: three decimals
    'mr': ('dp', 3, 'near'), 'mrlo': ('dp', 3, 'down'), 'mrhi': ('dp', 3, 'up'),
    # shares: three decimals in tables, two in running text
    'sh3': ('dp', 3, 'near'), 'sh3lo': ('dp', 3, 'down'), 'sh3hi': ('dp', 3, 'up'),
    'sh2': ('dp', 2, 'near'), 'sh2lo': ('dp', 2, 'down'), 'sh2hi': ('dp', 2, 'up'),
    # p-values: two significant figures (tables only)
    'p': ('sf', 2, 'near'),
}

# Which formats a row of each class may be printed with.
CLASS_FORMATS = {
    'J': {'e', 'lo', 'hi', 'up'},
    'tok': {'tok', 'toklo', 'tokhi'},
    'mr': {'mr', 'mrlo', 'mrhi'},
    'share': {'sh3', 'sh3lo', 'sh3hi', 'sh2', 'sh2lo', 'sh2hi'},
    'R': {'R'},
    'p': {'p'},
    'count': {'n', 'pos'},
    'word': {'w', 'id', 'list', 'pos', 'stage', 'yn', 'runid'},
    'asis': {'asis', 'rise', 'sci', 'runid'},
}

# Quantities outside RL-52's table print as issued: registered constants, CPU seconds, temperature rises in K,
# arm readings, comparator bars and largest differences, and the RL-39 duration ratios (two significant figures).
ASIS_KEY = re.compile(r'(^CMP\.bars\.|largest_absolute_difference|cpu_s|rise_k|\.measurements\.'
                      r'|^contention\.(threshold|interval_seconds)|^duration\.)')

# Rows that must print at ledger precision because a rounding would flip a stated comparison (RL-52). Empty: no
# comparison flips under the rule (see comparisons()); an entry needs a reason and the format 'ledger'.
FORCED_LEDGER: dict[int, str] = {}


def row_class(n: int) -> str:
    k, v = L[n]['key/leaf'], val(n)
    if ASIS_KEY.search(k):
        return 'asis'
    if not NUMERIC.fullmatch(v):
        return 'word'
    if INTEGER.fullmatch(v):
        return 'count'
    if 'adjusted_p' in k:
        return 'p'
    if 'per_token' in k:
        return 'tok'
    if 'magnitude_ratio' in k or 'within_model_spread' in k:
        return 'mr'
    if 'rho_' in k:
        return 'share'
    if re.search(r'(\.R$|\.R_cm$|^Rcm\.|block_lines\[\d+\]\.ratio$)', k):
        return 'R'
    return 'J'


def quantize(d: Decimal, fmt: str) -> Decimal:
    kind, k, direction = ROUNDERS[fmt]
    if kind == 'dp':
        return d.quantize(Decimal(1).scaleb(-k), rounding=MODE[direction])
    if d == 0:
        return d
    q = d.quantize(Decimal(1).scaleb(d.adjusted() - k + 1), rounding=MODE[direction])
    if q.adjusted() != d.adjusted():  # carried into the next decade
        q = q.quantize(Decimal(1).scaleb(q.adjusted() - k + 1), rounding=MODE[direction])
    return q


def is_tie(d: Decimal, fmt: str) -> bool:
    kind, k, direction = ROUNDERS[fmt]
    if direction != 'near' or d == 0:
        return False
    exp = -k if kind == 'dp' else d.adjusted() - k + 1
    rest = (abs(d) * Decimal(10) ** -exp) % 1
    return rest == Decimal('0.5')


SUP = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')


def signed(s: str) -> str:
    return '−' + s[1:] if s.startswith('-') else s


def sci(d: Decimal) -> str:
    if d == 0:
        return '0'
    mant, exp = f'{d:e}'.split('e')
    if '.' in mant:
        mant = mant.rstrip('0').rstrip('.')
    power = f'10{str(int(exp)).translate(SUP)}'
    return power if mant == '1' else f'{mant} × {power}'


def printed_decimal(n: int, fmt: str | None) -> Decimal:
    """The value a reader sees for row n printed with fmt (the ledger value for non-rounding formats)."""
    if fmt in ROUNDERS:
        return quantize(dec(n), fmt)
    return dec(n)


def render_value(n: int, fmt: str | None) -> str:
    v = val(n)
    if fmt in ROUNDERS:
        q = quantize(dec(n), fmt)
        return sci(q) if fmt == 'p' else signed(format(q, 'f'))
    if fmt in (None, 'asis', 'id', 'n', 'R', 'ledger'):
        return signed(v.replace('−', '-')) if NUMERIC.fullmatch(v) else v
    if fmt == 'w':
        return v.replace('_', ' ')
    if fmt == 'list':
        return ', '.join(v.split(','))
    if fmt == 'stage':
        seen: list[str] = []
        for s in v.split(','):
            if s not in seen:
                seen.append(s)
        return ', '.join(seen)
    if fmt == 'pos':
        p = [int(x) for x in v.split(',')]
        if len(p) > 1 and p == list(range(p[0], p[0] + len(p))):
            return f'{p[0]}–{p[-1]}'
        return ', '.join(map(str, p))
    if fmt == 'yn':
        return {'true': 'yes', 'false': 'no'}[v]
    if fmt == 'rise':
        return 'n/a' if v == 'none' else signed(v)
    if fmt == 'sci':
        return sci(Decimal(v))
    if fmt == 'runid':
        m = re.search(r'run_id=([^\],]+)', L[n]['key/leaf'])
        if not m:
            raise ValueError(f'row {n} has no run_id in its key')
        return m.group(1)
    raise ValueError(fmt)


# ---------------------------------------------------------------- analysed attempts (RL-52 (3))

def analysed_attempts() -> dict[str, dict]:
    data = json.loads(INDEX.read_text())
    out: dict[str, dict] = {}
    for a in data['attempts']:
        if a['seal'] == 'second' and a['claim_usable']:
            if a['pack'] in out:
                fail(f'analysed_windows.json: more than one claim-usable second-seal attempt for {a["pack"]}')
            out[a['pack']] = a
    if set(out) != {'alpha', 'beta', 'gamma'}:
        fail(f'analysed_windows.json: claim-usable second-seal attempts are {sorted(out)}')
    return out


def render_attempt(pack: str) -> str:
    a = analysed_attempts()[pack]
    day = datetime.datetime.fromtimestamp(a['t0_epoch_s'], datetime.timezone.utc)
    return f"{a['plan_id']} ({day.day} {day:%B} {day.year})"


# ---------------------------------------------------------------- templates

PH = re.compile(r'\{r(\d+)(?::(\w+))?\}')
AP = re.compile(r'\{a:(alpha|beta|gamma)\}')
FILL_RE = re.compile(r'\{\{FILL:.*?\}\}', re.S)

# Literal digits a site may carry: names, cross-references and three registered constants, each verified below.
ALLOWED_LITERALS = [
    r'Qwen3-1\.7B', r'Qwen3-8B', r'Qwen2\.5-1\.5B', r'1\.7B', r'8B', r'2,048', r'95%',
    r'Table S?\d+', r'Sections? \d+(\.\d+)*( and \d+(\.\d+)*)?', r'DLE-\d', r'\br[34]\b',
    r'configs/analysis/b5/', r'docs/analysis/b5/', r'`p42_status`',
    r'\b24\b',             # the number of comparator families in Table S8 (asserted equal to its rows)
    r'7 November 2026',    # DLE-3 and DLE-4 adoption date (asserted in DEVIATION-LOG.md)
    r'\b0\.2\b',           # the registered "consistent" spread limit (asserted in analysis plan §8)
]


def norm(s: str) -> str:
    return ' '.join(s.split())


D177 = 'Phase attribution is reported without a measured instrument phase-accounting check.'
LBL_RJ = 'not re-derived'
LBL_SS = 'from the registered disclosure record; not independently recomputed'
LBL_RECOMP = 'from the independent recomputation only'


def cells(*xs: str) -> str:
    return '| ' + ' | '.join(xs) + ' |'


# --- Section 3.4: the whole-machine cross-check (P1-B5-METER), Table S1
METER_ROWS = [  # (session, model, n, median, min, max, iqr0, iqr1, spread, outside, word)
    ('1.7B floor', 'Qwen3-1.7B', 737, 731, 732, 733, 734, 735, 736, 738, 739),
    ('1.7B floor', 'Qwen2.5-1.5B (reference)', 728, 722, 723, 724, 725, 726, 727, 729, 730),
    ('8B floor', 'Qwen3-8B', 755, 749, 750, 751, 752, 753, 754, 756, 757),
    ('8B floor', 'Qwen2.5-1.5B (reference)', 746, 740, 741, 742, 743, 744, 745, 747, 748),
    ('Contrast', 'Qwen3-1.7B', 773, 767, 768, 769, 770, 771, 772, 774, 775),
    ('Contrast', 'Qwen3-8B', 782, 776, 777, 778, 779, 780, 781, 783, 784),
    ('Contrast', 'Qwen2.5-1.5B (reference)', 764, 758, 759, 760, 761, 762, 763, 765, 766),
]
METER = '\n'.join([
    'Table S1 gives, for each analysed session and model, the rails\' share ρ = ΔE_rail / ΔE_machine over the '
    'model\'s member windows: its median, range and interquartile range, and the within-model spread '
    '(max ρ − min ρ) ÷ median ρ. No member window fell outside the hard plausibility band, so none is listed; every '
    'spread is at most 0.2 and is described, as registered, as "consistent". No session was clean ({r528:n} clean '
    'sessions): no clean session, no central band.',
    '',
    cells('Session', 'Model', 'Member windows', 'Median ρ', 'Range', 'Interquartile range', 'Spread',
          'Outside hard band', 'Word'),
    cells(*['---'] * 9),
    *[cells(s, m, f'{{r{n}:n}}', f'{{r{md}:sh3}}', f'[{{r{lo}:sh3lo}}, {{r{hi}:sh3hi}}]',
            f'[{{r{q0}:sh3lo}}, {{r{q1}:sh3hi}}]', f'{{r{sp}:mr}}', f'{{r{o}:n}}', f'{{r{w}:id}}')
      for s, m, n, md, lo, hi, q0, q1, sp, o, w in METER_ROWS],
    '',
    '*Table S1. Rails\' share ρ of request energy on the whole-machine boundary, per analysed session and model, '
    'primary block (descriptive; Section 3.2). Ranges and interquartile ranges are rounded outward.*',
])

# --- Section 6.1: attempts, analysed sessions, Table 1, Table S2, hazards, Tables S3 and S4
ATTEMPTS = (
    '**Attempts.** The 1.7B floor pack (session name ALPHA) took {r885:n} attempt under the second seal: attempt '
    '{r888:n}, verdict {r889:id}, cause {r890:id}; {r891:n} of {r892:n} planned runs succeeded. The 8B floor pack '
    '(BETA) took {r893:n} attempts: attempt {r900:n}, {r901:id}, cause {r902:id}, {r903:n} of {r904:n} runs; attempt '
    '{r905:n}, {r906:id}, cause {r907:id}, {r908:n} of {r909:n}; attempt {r910:n}, {r911:id}, cause {r912:id}, '
    '{r913:n} of {r914:n}; attempt {r915:n}, {r916:id}, cause {r917:id}, {r918:n} of {r919:n}; attempt {r920:n}, '
    '{r921:id}, cause {r922:id}, {r923:n} of {r924:n}; and attempt {r925:n}, {r926:id}, cause {r927:id}, the analysed '
    'attempt, in which {r928:n} of {r929:n} planned runs succeeded. The contrast pack (GAMMA) took {r1643:n} attempt: '
    'attempt {r1646:n}, {r1647:id}, cause {r1648:id}; of its {r1650:n} planned runs, all {r217:n} bundles were '
    'present and raw-valid and {r1649:n} succeeded. Listed separately, as inputs to no number: the {r930:n} '
    'first-seal attempts of the 1.7B floor pack, made before the second seal, were attempt {r935:n} ({r936:id}, '
    'cause {r937:id}, {r938:n} of {r939:n} runs), attempt {r940:n} ({r941:id}, cause {r942:id}, run counts '
    '{r943:id}) and attempt {r945:n} ({r946:id}, cause {r947:id}, {r948:n} of {r949:n} runs). Verdicts and cause '
    'families are the collection record\'s and were not re-derived; the run counts of attempts that were not '
    'analysed are from the registered disclosure record; not independently recomputed. A count of runs is of runs '
    'that succeeded.')

ANALYSED = 'The analysed sessions were {a:alpha}, {a:beta} and {a:gamma}, dated in UTC.'

UNITS = {  # (unit_id, stratum, codes, families, stage_ids, positions) per reported cell, in run order
    '1.7B decode': [(1794, 1440, 955, 956, 1441, 1442), (1795, 1443, 957, 958, 1444, 1445)],
    '1.7B prefill (2,048)': [(1798, 1452, 985, 986, 1453, 1454), (1796, 1446, 987, 988, 1447, 1448),
                             (1797, 1449, 989, 990, 1450, 1451)],
    '8B decode': [(1802, 1481, 1027, 1028, 1482, 1483), (1803, 1484, 1029, 1030, 1485, 1486),
                  (1804, 1487, 1031, 1032, 1488, 1489), (1799, 1472, 1033, 1034, 1473, 1474),
                  (1800, 1475, 1035, 1036, 1476, 1477), (1801, 1478, 1037, 1038, 1479, 1480)],
    '8B prefill (2,048)': [(1809, 1502, 1071, 1072, 1503, 1504), (1805, 1490, 1073, 1074, 1491, 1492),
                           (1806, 1493, 1075, 1076, 1494, 1495), (1807, 1496, 1077, 1078, 1497, 1498),
                           (1808, 1499, 1079, 1080, 1500, 1501)],
}
QUADS = {  # (unit_id, stratum, stage_ids, positions, codes, families, [(trigger member, its codes)])
    'Contrast, decode': [(1810, 1811, 1812, 1813, 1112, 1113, [(198, 1130)]),
                         (1814, 1815, 1816, 1817, 1114, 1115, [(199, 1132)]),
                         (1818, 1819, 1820, 1821, 1116, 1117, [(200, 1134)]),
                         (1822, 1823, 1824, 1825, 1118, 1119, [(201, 1136)])],
    'Contrast, prefill (2,048)': [(1826, 1827, 1828, 1829, 1120, 1121, [(202, 1138), (203, 1140)]),
                                  (1830, 1831, 1832, 1833, 1122, 1123, [(204, 1142)]),
                                  (1834, 1835, 1836, 1837, 1124, 1125, [(205, 1144)]),
                                  (1838, 1839, 1840, 1841, 1126, 1127, [(206, 1146), (207, 1148)]),
                                  (1842, 1843, 1844, 1845, 1128, 1129, [(208, 1150)])],
}
KEPT = {'1.7B decode': (139, 140), '1.7B prefill (2,048)': (148, 149), '8B decode': (157, 158),
        '8B prefill (2,048)': (166, 167), 'Contrast, decode': (None, 11), 'Contrast, prefill (2,048)': (None, 13)}
QUAD_STRATA = {1440, 1443, 1446, 1449, 1472, 1475, 1478, 1490, 1493, 1496, 1499,
               1811, 1815, 1819, 1823, 1827, 1831, 1835, 1839, 1843}


def unit_cell(stratum: int, families: int, positions: int) -> str:
    word = 'positions' if stratum in QUAD_STRATA else 'position'
    return f'{{r{stratum}:id}} ({{r{families}:list}}; {word} {{r{positions}:pos}})'


def table1_row(cell: str) -> str:
    nr, nb = KEPT[cell]
    if cell in UNITS:
        removed = '; '.join(unit_cell(s, f, p) for _, s, _, f, _, p in UNITS[cell])
    else:
        removed = '; '.join(unit_cell(s, f, p) for _, s, _, p, _, f, _ in QUADS[cell])
    return cells(cell, f'{{r{nr}:n}}' if nr else '—', f'{{r{nb}:n}}', removed)


TABLE1_IDS = {'1.7B decode': 'P1-B5-RM-1p7B-decode', '1.7B prefill (2,048)': 'P1-B5-RM-1p7B-prefill',
              '8B decode': 'P1-B5-RM-8B-decode', '8B prefill (2,048)': 'P1-B5-RM-8B-prefill',
              'Contrast, decode': 'P1-B5-RM-ctr-decode', 'Contrast, prefill (2,048)': 'P1-B5-RM-ctr-prefill'}
TABLE1_FIRST = {'1.7B decode': ['P1-B5-NR-1p7B-decode', 'P1-B5-NB-1p7B-decode'],
                '1.7B prefill (2,048)': ['P1-B5-NR-1p7B-prefill', 'P1-B5-NB-1p7B-prefill'],
                '8B decode': ['P1-B5-NR-8B-decode', 'P1-B5-NB-8B-decode'],
                '8B prefill (2,048)': ['P1-B5-NR-8B-prefill', 'P1-B5-NB-8B-prefill'],
                'Contrast, decode': ['P1-B5-NQ-decode'], 'Contrast, prefill (2,048)': ['P1-B5-NQ-prefill']}

TABLE1_CAPTION = ('*Table 1. Kept and removed units per target cell in the primary block. Each removed unit is '
                  'given with its stratum, the catalog families of the codes that removed it, and its positions in '
                  'the session\'s sequence of target runs, counted from zero as the disclosure record numbers them; '
                  'Table S2 names each unit, its stage and its codes.*')

TABLE_S2 = '\n'.join([
    cells('Cell', 'Removed unit', 'Stage', 'Codes'),
    cells(*['---'] * 4),
    *[cells(c, f'{{r{u}:id}}', f'{{r{st}:stage}}', f'{{r{co}:list}}')
      for c, us in UNITS.items() for u, _, co, _, st, _ in us],
    *[cells(c, f'{{r{u}:id}}', f'{{r{st}:stage}}',
            f'{{r{co}:list}}; triggered by ' + ' and '.join(f'{{r{m}:id}} ({{r{mc}:list}})' for m, mc in trig))
      for c, qs in QUADS.items() for u, _, st, _, co, _, trig in qs],
    '',
    '*Table S2. Removed units and quads of the primary block, with the stage they ran in and the registered codes '
    'that removed them, from the analysed sessions\' exclusion records. For a contrast quad, the member or members '
    'that triggered the removal are named with their own codes; a removed member removes its whole quad.*',
])

ARM = [  # (probe label, alpha rows, beta rows, gamma rows); readings first, the verdict last
    ('battery, instant: amperage / instant amperage (mA)', (1163, 1164, 1165), (1291, 1292, 1293), (1512, 1513, 1514)),
    ('battery, final: amperage / instant amperage (mA)', (1166, 1167, 1168), (1294, 1295, 1296), (1515, 1516, 1517)),
    ('clock, instant', (1169,), (1297,), (1518,)),
    ('clock, dwell and go', (1170,), (1298,), (1519,)),
    ('contention, dwell: `cpu_s_per_s` / `host_busy_cpu_s_per_s` / `tree_cpu_s_per_s` / '
     '`unattributed_cpu_s_per_s`', (1171, 1172, 1173, 1174, 1175), (1299, 1300, 1301, 1302, 1303),
     (1520, 1521, 1522, 1523, 1524)),
    ('disk, instant: free bytes', (1176, 1177), (1304, 1305), (1525, 1526)),
    ('instrument, probe', (1178,), (1306,), (1527,)),
    ('thermal, instant', (1179,), (1307,), (1528,)),
    ('thermal, final', (1180,), (1308,), (1529,)),
]


def arm_cell(rows: tuple[int, ...]) -> str:
    *readings, verdict = rows
    head = ' / '.join(f'{{r{n}:asis}}' for n in readings)
    return (head + '; ' if head else '') + f'{{r{verdict}:id}}'


HAZARDS = (
    '**Hazards.** At arm every registered hazard probe of each analysed session returned a reading and passed '
    '(Table S3); {r1427:n}, {r1461:n} and {r1511:n} `arm_unmeasured` flags were written in the 1.7B floor, 8B '
    'floor and contrast sessions, so no hazard is named as unread. In the sessions, outside-process overlap with a '
    'request (`contention.request_overlap`) was flagged on {r1181:n}, {r1309:n} and {r1530:n} members, and an unknown '
    'span (`member.span_unknown`) on {r1182:n}, {r1310:n} and {r1531:n}. Battery assist: {r1421:n}, {r1455:n} and '
    '{r1505:n} members carried `battery.assist`; {r1422:n}, {r1456:n} and {r1506:n} carried '
    '`battery.assist_outside_request`; {r1423:n}, {r1457:n} and {r1507:n} `battery.capture_pair_assist`; '
    '{r1424:n}, {r1458:n} and {r1508:n} `battery.smc_unavailable`; and {r1425:n}, {r1459:n} and {r1509:n} '
    'calibration captures carried `calibration.capture_battery_assist`, {r1426:n}, {r1460:n} and {r1510:n} '
    '`calibration.capture_battery_pair_assist`. Table S4 gives the battery-temperature rise of every stage; no stage '
    'was flagged `thermal.stage_battery_rise` or `thermal.battery_temperature_unmeasured`. Arm readings and verdicts '
    'and the stage harvest flags are the collection record\'s and were not re-derived; the counts are arithmetic '
    'over stored flags, not a new detection of the hazards.')

TABLE_S3 = '\n'.join([
    cells('Arm probe', '1.7B floor session', '8B floor session', 'Contrast session'),
    cells(*['---'] * 4),
    *[cells(lab, arm_cell(a), arm_cell(b), arm_cell(g)) for lab, a, b, g in ARM],
    '',
    '*Table S3. Hazard measurements at arm, with each probe\'s verdict, from the arm collection record; not '
    're-derived. Contention readings are in CPU-seconds per second.*',
])

STAGES = {  # (stage_id, rise, plateau, unmeasured, harvest flag, producer flag)
    '1.7B floor': [(1430, 1183, 1184, 1186, 1187, 1185), (1431, 1189, 1190, 1192, 1193, 1191),
                   (1432, 1195, 1196, 1198, 1199, 1197), (1433, 1201, 1202, 1204, 1205, 1203),
                   (1434, 1207, 1208, 1210, 1211, 1209), (1435, 1213, 1214, 1216, 1217, 1215),
                   (1436, 1219, 1220, 1222, 1223, 1221), (1437, 1225, 1226, 1228, 1229, 1227),
                   (1438, 1231, 1232, 1234, 1235, 1233), (1439, 1237, 1238, 1240, 1241, 1239)],
    '8B floor': [(1462, 1311, 1312, 1314, 1315, 1313), (1463, 1317, 1318, 1320, 1321, 1319),
                 (1464, 1323, 1324, 1326, 1327, 1325), (1465, 1329, 1330, 1332, 1333, 1331),
                 (1466, 1335, 1336, 1338, 1339, 1337), (1467, 1341, 1342, 1344, 1345, 1343),
                 (1468, 1347, 1348, 1350, 1351, 1349), (1469, 1353, 1354, 1356, 1357, 1355),
                 (1470, 1359, 1360, 1362, 1363, 1361), (1471, 1365, 1366, 1368, 1369, 1367)],
    'Contrast': [(1536, 1537, 1538, 1540, 1541, 1539), (1543, 1544, 1545, 1547, 1548, 1546),
                 (1550, 1551, 1552, 1554, 1555, 1553), (1557, 1558, 1559, 1561, 1562, 1560),
                 (1564, 1565, 1566, 1568, 1569, 1567), (1571, 1572, 1573, 1575, 1576, 1574),
                 (1578, 1579, 1580, 1582, 1583, 1581), (1585, 1586, 1587, 1589, 1590, 1588),
                 (1592, 1593, 1594, 1596, 1597, 1595), (1599, 1600, 1601, 1603, 1604, 1602)],
}
TABLE_S4 = '\n'.join([
    cells('Session', 'Stage', 'Rise (K)', 'Last three plateau', 'Unmeasured', 'Flagged (harvest / producer)'),
    cells(*['---'] * 6),
    *[cells(s, f'{{r{a}:id}}', f'{{r{b}:rise}}', f'{{r{c}:yn}}', f'{{r{d}:yn}}', f'{{r{e}:yn}} / {{r{f}:yn}}')
      for s, rows in STAGES.items() for a, b, c, d, e, f in rows],
    '',
    '*Table S4. Battery-thermistor rise across each stage of each analysed session (last reading minus first), '
    'whether the last three readings plateau, and the stage flags. n/a: fewer than two readable readings, so no rise '
    'is defined; this is distinct from "unmeasured", which means no readable reading. The harvest flags are the '
    'collection record\'s; not re-derived. A flag changes no number and removes nothing.*',
])

# --- Section 6.2
TABLE2 = [
    ('Table 2, 1.7B decode', ['E_1p7B_decode_J_per_request', 'E_1p7B_decode_lower_J', 'E_1p7B_decode_upper_J',
                              'E_1p7B_decode_J_per_token', 'P1-B5-AF-1p7B-decode'],
     '| Qwen3-1.7B | decode | {r133:e} | [{r134:lo}, {r135:hi}] | {r141:tok} | {r138:up} |'),
    ('Table 2, 1.7B prefill', ['E_1p7B_prefill_p2048_J_per_request', 'E_1p7B_prefill_p2048_lower_J',
                               'E_1p7B_prefill_p2048_upper_J', 'E_1p7B_prefill_p2048_J_per_token',
                               'P1-B5-AF-1p7B-prefill'],
     '| Qwen3-1.7B | prefill (2,048) | {r142:e} | [{r143:lo}, {r144:hi}] | {r150:tok} | {r147:up} |'),
    ('Table 2, 8B decode', ['E_8B_decode_J_per_request', 'E_8B_decode_lower_J', 'E_8B_decode_upper_J',
                            'E_8B_decode_J_per_token', 'P1-B5-AF-8B-decode'],
     '| Qwen3-8B | decode | {r151:e} | [{r152:lo}, {r153:hi}] | {r159:tok} | {r156:up} |'),
    ('Table 2, 8B prefill', ['E_8B_prefill_p2048_J_per_request', 'E_8B_prefill_p2048_lower_J',
                             'E_8B_prefill_p2048_upper_J', 'E_8B_prefill_p2048_J_per_token', 'P1-B5-AF-8B-prefill'],
     '| Qwen3-8B | prefill (2,048) | {r160:e} | [{r161:lo}, {r162:hi}] | {r168:tok} | {r165:up} |'),
]

INTERVAL_PARTS = [  # (model, phase, h, B, kind0, kind1, kind2, attained_by, minimum)
    ('Qwen3-1.7B', 'decode', 136, 137, 950, 951, 952, 953, 954),
    ('Qwen3-1.7B', 'prefill (2,048)', 145, 146, 980, 981, 982, 983, 984),
    ('Qwen3-8B', 'decode', 154, 155, 1022, 1023, 1024, 1025, 1026),
    ('Qwen3-8B', 'prefill (2,048)', 163, 164, 1066, 1067, 1068, 1069, 1070),
]
TABLE_S5 = '\n'.join([
    cells('Model', 'Phase', 'h (J)', 'B (J)', 'First-kind timing bound (J)', 'Interpolation bound (J)',
          'Drift term (J)', 'Attribution floor attained by', 'Smallest first-kind bound (J)'),
    cells(*['---'] * 9),
    *[cells(m, p, f'{{r{h}:up}}', f'{{r{b}:up}}', f'{{r{k0}:up}}', f'{{r{k1}:up}}', f'{{r{k2}:up}}',
            f'{{r{at}:id}}', f'{{r{mn}:up}}') for m, p, h, b, k0, k1, k2, at, mn in INTERVAL_PARTS],
    '',
    '*Table S5. Components of the intervals of Table 2: the half-width h, and B with its three stratified averages '
    '(Section 4.3); the kept run that attains the cell\'s attribution floor (Section 4.4), and the smallest '
    'first-kind bound over the cell\'s kept runs. Each value is rounded up separately, so the three averages need '
    'not sum to B in the last digit. ' + D177 + '*',
])

BATT_LINE = (
    '*Without battery-assisted units:* no kept run of any cell was battery-assisted ({r959:n} and {r960:n} assisted '
    'runs among the repeats and the quads of 1.7B decode, {r991:n} and {r992:n} of 1.7B prefill, {r1039:n} and '
    '{r1040:n} of 8B decode, {r1081:n} and {r1082:n} of 8B prefill, from the collection record\'s battery-assist '
    'flags; not re-derived), so no unit was removed ({r973:n}, {r1005:n}, {r1053:n} and {r1095:n}) and each line '
    'equals its cell: {r966:e} J [{r969:lo}, {r970:hi}] (n_r = {r971:n}, n_b = {r972:n}) for 1.7B decode, '
    '{r998:e} J [{r1001:lo}, {r1002:hi}] (n_r = {r1003:n}, n_b = {r1004:n}) for 1.7B prefill, {r1046:e} J '
    '[{r1049:lo}, {r1050:hi}] (n_r = {r1051:n}, n_b = {r1052:n}) for 8B decode and {r1088:e} J [{r1091:lo}, '
    '{r1092:hi}] (n_r = {r1093:n}, n_b = {r1094:n}) for 8B prefill. ' + D177)

LOAD_LINE = (
    '*Load-correlated exclusions not applied:* 1.7B decode: no such removal ({r979:n} lines). 1.7B prefill, with '
    '{r1012:n} repeat and {r1014:n} quads restored: {r1017:e} J [{r1020:lo}, {r1021:hi}] (n_r = {r1013:n}, '
    'n_b = {r1015:n}). 8B decode: the registered pipeline refused this line ({r1064:id}, `{r1065:id}`); the '
    'independent recomputation\'s value, recompute only; not compared, with {r1060:n} repeats and {r1062:n} quad '
    'restored, is {r649:e} J [{r650:lo}, {r651:hi}] (n_r = {r647:n}, n_b = {r648:n}). 8B prefill, with {r1102:n} '
    'repeats and {r1104:n} quads restored: {r1107:e} J [{r1110:lo}, {r1111:hi}] (n_r = {r1103:n}, '
    'n_b = {r1105:n}). ' + D177)

INTERVAL_PARTS_SENTENCE = ('Each row of Table 2 carries the fixed attribution-floor sentence of Section 4.4 with its '
                           'own value of X, and the interval\'s three components: h, and the average first-kind '
                           'timing bound, interpolation bound and drift term that make up B (Table S5).')

# --- Section 6.3: Table 3. Absolute floor = the cell's drift-widened guarded absolute floor (hand-check key
# `.../absolute.minted`; rows 290 and 293 name it directly for 8B). Operative floor = the arm's `floor_gate_j`
# (rows 53-57). Comparative floor = RC.floor_cells[...].floor_cmp_j (rows 550, 566, 582, 598).
TABLE3 = [
    ('Table 3, 1.7B decode', ['F_1p7B_decode_abs_J', 'F_1p7B_decode_operative_J', 'F_1p7B_decode_cmp_J',
                              'P1-B5-FN-1p7B-decode'],
     '| Qwen3-1.7B | decode | {r53:up} | {r550:up} | {r53:up} | {r543:n} / {r548:n} |'),
    ('Table 3, 1.7B prefill', ['F_1p7B_prefill_p2048_abs_J', 'F_1p7B_prefill_p2048_operative_J',
                               'F_1p7B_prefill_p2048_cmp_J', 'P1-B5-FN-1p7B-prefill'],
     '| Qwen3-1.7B | prefill (2,048) | {r56:up} | {r566:up} | {r56:up} | {r559:n} / {r564:n} |'),
    ('Table 3, 8B decode', ['F_8B_decode_abs_J', 'F_8B_decode_operative_J', 'F_8B_decode_cmp_J', 'P1-B5-FN-8B-decode'],
     '| Qwen3-8B | decode | {r290:up} | {r582:up} | {r54:up} | {r575:n} / {r580:n} |'),
    ('Table 3, 8B prefill', ['F_8B_prefill_p2048_abs_J', 'F_8B_prefill_p2048_operative_J', 'F_8B_prefill_p2048_cmp_J',
                             'P1-B5-FN-8B-prefill'],
     '| Qwen3-8B | prefill (2,048) | {r293:up} | {r598:up} | {r57:up} | {r591:n} / {r596:n} |'),
]

# --- Section 6.4: Table 4 (R = corner / point; TERM_B = corner = numerator_j, TERM_A = point = denominator_j)
DOM = [  # (label, cell token, R abs rows (R, num, den), R cmp rows, R_cm row; RL-55: 1846 is the five-decimal row)
    ('1.7B decode', '1p7B_decode', (540, 541, 542), (545, 546, 547), 276),
    ('1.7B prefill', '1p7B_prefill_p2048', (556, 557, 558), (561, 562, 563), 1846),
    ('8B decode', '8B_decode', (572, 573, 574), (577, 578, 579), 278),
    ('8B prefill', '8B_prefill_p2048', (588, 589, 590), (593, 594, 595), 279),
]
TABLE4 = []
for _label, _tok, (_ra, _na, _da), (_rc, _nc, _dc), _rcm in DOM:
    _model = 'Qwen3-1.7B' if _tok.startswith('1p7B') else 'Qwen3-8B'
    _phase = 'decode' if 'decode' in _tok else 'prefill (2,048)'
    _ids = [f'R_{_tok}_abs', f'TERM_B_{_tok}_abs_J', f'TERM_A_{_tok}_abs_J', f'R_{_tok}_cmp', f'TERM_B_{_tok}_cmp_J',
            f'TERM_A_{_tok}_cmp_J', f'R_cm_{_tok}_cmp']
    TABLE4.append((f'Table 4, {_label}', _ids,
                   f'| {_model} | {_phase} | {{r{_ra}:R}} ({{r{_na}:up}} ÷ {{r{_da}:up}}) | '
                   f'{{r{_rc}:R}} ({{r{_nc}:up}} ÷ {{r{_dc}:up}}) | {{r{_rcm}:R}} |'))

DOM_FAILED = (
    'Timing attribution did not at least double every detection floor. The components where it did not are the '
    'comparative common-mode replays: R_cm = {r843:R} for 1.7B decode ({r844:up} ÷ {r845:up} J, n = {r846:n}), '
    'R_cm = {r1846:R} for 1.7B prefill ({r849:up} ÷ {r850:up} J, n = {r851:n}) and R_cm = {r853:R} for 8B decode '
    '({r854:up} ÷ {r855:up} J, n = {r856:n}).')

# --- Section 6.5
TABLE5 = [
    ('Table 5, decode', ['E_decode_contrast_signed_J_per_request', 'P1-B5-CTR-decode-METRO', 'E_decode_contrast_lower_J',
                         'E_decode_contrast_upper_J', 'F_claim_decode_armwise_max_J', 'P1-B5-CTR-decode-PADJ',
                         'P1-B5-CTR-decode-OUTCOME', 'P1-B5-CTR-decode-LEVEL'],
     '| decode | {r11:n} | {r15:e} | [{r36:lo}, {r37:hi}] | [{r48:lo}, {r49:hi}] | {r52:up} | {r60:p} | {r530:w} | '
     '{r532:id} |'),
    ('Table 5, prefill', ['E_prefill_p2048_contrast_signed_J_per_request', 'P1-B5-CTR-prefill-METRO',
                          'E_prefill_p2048_contrast_lower_J', 'E_prefill_p2048_contrast_upper_J',
                          'F_claim_prefill_p2048_armwise_max_J', 'P1-B5-CTR-prefill-PADJ',
                          'P1-B5-CTR-prefill-OUTCOME', 'P1-B5-CTR-prefill-LEVEL'],
     '| prefill (2,048) | {r13:n} | {r16:e} | [{r38:lo}, {r39:hi}] | [{r50:lo}, {r51:hi}] | {r55:up} | {r61:p} | '
     '{r533:w} | {r535:id} |'),
]
LABEL_T5 = ['recorded output', 'collection-time records']

# --- Section 6.6
XWIN = (
    'For 1.7B decode, the contrast session\'s and the floor session\'s estimates {r978:id} within their '
    'within-session intervals (difference {r974:e} J). For 1.7B prefill, they {r1010:id} within their within-session '
    'intervals (difference {r1006:e} J). For 8B decode, the contrast session\'s and the floor session\'s estimates '
    '{r1058:id} by {r1054:e} J, more than their within-session intervals cover; the reported intervals understate '
    'between-session variation, which includes different interleaving and thermal history. For 8B prefill, they '
    '{r1100:id} within their within-session intervals (difference {r1096:e} J). Each difference is the contrast '
    'session\'s mean minus the floor session\'s cell, Δ = G − F. ' + D177)

NEG8_TEXT = (
    'Each analysed session\'s drift screen passed on both energy families (Table S6), and its reference and corpus '
    'record is in Table S7. No spare reference was measured and no midpoint reference was lost, so neither the '
    'spare listing nor the lost-midpoint sentence applies. The gross allowance is the session\'s drift allowance of '
    'Sections 4.3 and 4.5.')
NEG8_ROWS = [  # (session, family, statistic, envelope, prediction, bound, excursion, allowance, screen)
    ('1.7B floor', 'gross', 1258, 1255, 1256, 1257, 1259, 1260, 1261),
    ('1.7B floor', 'idle-subtracted', 1265, 1262, 1263, 1264, 1266, 1267, 1268),
    ('8B floor', 'gross', 1386, 1383, 1384, 1385, 1387, 1388, 1389),
    ('8B floor', 'idle-subtracted', 1393, 1390, 1391, 1392, 1394, 1395, 1396),
    ('Contrast', 'gross', 1609, 1606, 1607, 1608, 1610, 1611, 1612),
    ('Contrast', 'idle-subtracted', 1616, 1613, 1614, 1615, 1617, 1618, 1619),
]
TABLE_S6 = '\n'.join([
    cells('Session', 'Energy family', 'Screen statistic (J)', 'Envelope term (J)', 'Prediction term (J)',
          'Bound (J)', 'Reference excursion (J)', 'Allowance (J)', 'Screen'),
    cells(*['---'] * 9),
    *[cells(s, f, f'{{r{a}:e}}', f'{{r{b}:up}}', f'{{r{c}:up}}', f'{{r{d}:up}}', f'{{r{e}:up}}', f'{{r{g}:up}}',
            f'{{r{h}:id}}') for s, f, a, b, c, d, e, g, h in NEG8_ROWS],
    '',
    '*Table S6. Drift screen of each analysed session on the reference workload\'s request energy (Section 4.7). The '
    'screen statistic is the difference between the end and start reference means; the screen passes when it is at '
    'most the bound, which is the larger of its envelope and prediction terms. The allowance is the larger of the '
    'bound and the largest excursion of the start, midpoint and end references. Terms, bounds, excursions and '
    'allowances are rounded up, the statistic to nearest. ' + D177 + '*',
])
TABLE_S7 = '\n'.join([
    cells('', '1.7B floor session', '8B floor session', 'Contrast session'),
    cells(*['---'] * 4),
    cells('Corpus runs: ran / in the in-session bound / in the deciding bound', '{r1282:n} / {r1283:n} / {r1284:n}',
          '{r1409:n} / {r1410:n} / {r1411:n}', '{r1634:n} / {r1635:n} / {r1636:n}'),
    cells('Corpus runs left out for status', '{r1287:n}', '{r1415:n}', '{r1640:n}'),
    cells('Corpus runs left out for `contention.request_overlap`', 'none',
          '{r1413:n} ({r1416:runid}, {r1417:runid}, {r1418:runid}, {r1419:runid}, {r1420:runid})',
          '{r1638:n} ({r1641:runid}, {r1642:runid})'),
    cells('Corpus runs left out by the desk cap', '{r1286:n} ({r1285:list})', '{r1414:n}',
          '{r1639:n} ({r1637:list})'),
    cells('References realised of planned: start, midpoint, end',
          '{r1270:n} of {r1271:n}, {r1272:n} of {r1273:n}, {r1274:n} of {r1275:n}',
          '{r1398:n} of {r1399:n}, {r1400:n} of {r1401:n}, {r1402:n} of {r1403:n}',
          '{r1621:n} of {r1622:n}, {r1623:n} of {r1624:n}, {r1625:n} of {r1626:n}'),
    cells('Lost references: count; run (slot, reason)', '{r1279:n}; {r1428:id} ({r1429:id}, {r1281:id})', '{r1407:n}',
          '{r1630:n}; {r1534:id} ({r1535:id}, {r1633:id}) and {r1532:id} ({r1533:id}, {r1632:id})'),
    cells('Midpoint reference lost', '{r1280:yn}', '{r1408:yn}', '{r1631:yn}'),
    cells('Spares measured / in the deciding bound', '{r1278:n} / {r1277:n}', '{r1406:n} / {r1405:n}',
          '{r1629:n} / {r1628:n}'),
    cells('References in the deciding bound', '{r1276:n}', '{r1404:n}', '{r1627:n}'),
    cells('Drift-screen decision', '{r1269:id}', '{r1397:id}', '{r1620:id}'),
    '',
    '*Table S7. Reference and corpus record of each analysed session\'s drift screen (Section 4.7). The deciding '
    '(clean) bound takes the first eligible corpus members in the committed order up to the registered cap; members '
    'after it are left out by the desk cap. Run names are the registered identifiers.*',
])

MONITOR = (
    '({r1160:asis} CPU-s for the hazard monitor, {r1161:asis} CPU-s for the meter reader and {r1162:n} monitor probes '
    'inside target phases in the 1.7B floor session; {r1288:asis}, {r1289:asis} and {r1290:n} in the 8B floor '
    'session; {r348:asis}, {r349:asis} and {r350:asis} in the contrast session; ' + LBL_SS + ')')

# --- Section 6.7: the Block 5 paragraph of P1-RECOMPUTE-SUMMARY (RL-52 (4), RL-4 (vii)), Table S8
CMP_ROWS = [  # (family, bar abs, bar rel, compared, pass, fail, largest difference, word)
    ('b_op_s', 1654, 1655, 1653, 1651, 1652, 1656, 1657), ('battery_term', None, None, 1660, 1658, 1659, None, 1661),
    ('contrast_j', 1665, 1666, 1664, 1662, 1663, 1667, 1668), ('contrast_p', 1672, 1673, 1671, 1669, 1670, 1674, 1675),
    ('count', 1679, 1680, 1678, 1676, 1677, 1681, 1682),
    ('descriptive_ratio', 1686, 1687, 1685, 1683, 1684, 1688, 1689),
    ('dominance_branch', None, None, 1692, 1690, 1691, None, 1693),
    ('dominance_ratio', 1697, 1698, 1696, 1694, 1695, 1699, 1700),
    ('exclusions_rederivation', None, None, 1703, 1701, 1702, None, 1704),
    ('floor_gate_j', 1708, 1709, 1707, 1705, 1706, 1710, 1711), ('floor_j', 1715, 1716, 1714, 1712, 1713, 1717, 1718),
    ('holm_order', None, None, 1721, 1719, 1720, None, 1722), ('kept_units', None, None, 1725, 1723, 1724, None, 1726),
    ('machine_j', 1730, 1731, 1729, 1727, 1728, 1732, 1733), ('meter_j', 1737, 1738, 1736, 1734, 1735, 1739, 1740),
    ('meter_w', 1744, 1745, 1743, 1741, 1742, 1746, 1747), ('outcome_word', None, None, 1750, 1748, 1749, None, 1751),
    ('p42_status', None, None, 1754, 1752, 1753, None, 1755),
    ('per_token_j', 1759, 1760, 1758, 1756, 1757, 1761, 1762),
    ('reported_cell_j', 1766, 1767, 1765, 1763, 1764, 1768, 1769), ('rho', 1773, 1774, 1772, 1770, 1771, 1775, 1776),
    ('routing_id', None, None, 1779, 1777, 1778, None, 1780),
    ('run_phase_energy_j', 1784, 1785, 1783, 1781, 1782, 1786, 1787),
    ('window_edge_s', 1791, 1792, 1790, 1788, 1789, None, 1793),
]
RECOMPUTE_B5 = (
    '**Primary block.** The comparator set the independent recomputation\'s values against the registered '
    'pipeline\'s in 24 families, under the bars fixed blind before release (`configs/analysis/b5/recompute_bars.json`, '
    'DLE-0). Table S8 gives, per family, the bars, the rows compared, agreeing and failing, the largest absolute '
    'difference and the word. Every compared row agreed. One of the 24 comparator families, `window_edge_s`, compared '
    'no rows ({r1790:n}); its word is {r1793:id}, not agreement. What was recomputed is what Table S8 lists: the '
    'per-run phase energies, the reported cells and per-token values, the floors and floor gates, the dominance '
    'ratios and branch, the contrasts with their p-values, Holm order and outcome words, the kept units and the '
    're-derivation of the exclusions from the stored flags, and the whole-machine meter lines. What was not: the '
    '{r523:id} disclosure families named in Section 5.7 are not independently recomputed, and the collection-time '
    'judgments listed there are inputs. Each printed value from those families, and each value that only one program '
    'computed, was checked by a separate reader against the released records (`docs/analysis/b5/REDERIVATION.md`) '
    'and carries its label where it is printed. Two disclosed repairs changed the registered pipeline\'s output '
    'before release, both adopted on 7 November 2026: analysis version r3 corrected a disclosure key and relabelled a '
    'floor-binding refusal (DLE-3), and r4 corrected the floor binder\'s campaign-log parse, without which both '
    'contrasts would have been not estimable (DLE-4); the comparator\'s mapping of the attribution-floor leaves '
    '(DLE-5) changed no output (Section 5.5).')


def cmp_cell(n: int | None) -> str:
    return '—' if n is None else f'{{r{n}:sci}}'


TABLE_S8 = '\n'.join([
    cells('Family', 'Bar: absolute / relative', 'Compared', 'Agreeing', 'Failing', 'Largest absolute difference', 'Word'),
    cells(*['---'] * 7),
    *[cells(f'`{f}`', '—' if ba is None else f'{cmp_cell(ba)} / {cmp_cell(br)}', f'{{r{c}:n}}', f'{{r{p}:n}}',
            f'{{r{x}:n}}', cmp_cell(ld), f'{{r{w}:id}}') for f, ba, br, c, p, x, ld, w in CMP_ROWS],
    '',
    '*Table S8. Agreement of the independent recomputation with the registered pipeline, primary block, per '
    'comparator family. A bar is max(absolute, relative × |value|, half a unit of the printed decimals where a '
    'family specifies them), as fixed blind; "—": a categorical or exact family, with no numerical bar or largest '
    'difference.*',
])

# --- Section 11: branch 9.D (CP-X02-conclusion), branch B sentence with the failing components named
CONCLUSION_9D = ('Timing attribution at least doubled the detection floor for some components and not others (not '
                 'for the common-mode replays R_cm of 1.7B decode, 1.7B prefill and 8B decode), so neither timing nor '
                 'repeatability alone limits these measurements.')

# --- first-fill prose, re-rounded under RL-52
PROSE = [
    ('Table 5 caption, claim level (RL-41 b)', [],
     'Both contrasts reach level {r532:id} under the registered gate; the claim level is the gate\'s recorded output. '
     'The gate\'s eligibility inputs (selection, the absence of top-ups, replacement validity, transport and current '
     'checks) are collection-time records; we did not re-derive them.', LABEL_T5),
    ('Section 6.1, losses and skew (RL-4 v)', [],
     'The registered exclusion rules removed {r432:n} of the {r433:n} planned contrast quads, keeping {r11:n} of '
     '{r12:n} for decode and {r13:n} of {r14:n} for 2,048-token prefill; the prefill contrast therefore rests on the '
     'registered minimum of {r181:n} quads. A removed member removes its whole quad, so every removal takes both '
     'models\' runs alike, but the members that triggered removal were not balanced: {r223:n} of the {r224:n} were on '
     'the 8B side and {r225:n} on the 1.7B side, and all {r226:n} decode removals were triggered by an 8B member. '
     'Contention (an outside process above {r182:asis} CPU-s/s in a {r183:asis} s interval overlapping the request) '
     'fired on {r227:n} triggering members on the 8B side and {r228:n} on the 1.7B side, an aborted idle admission on '
     '{r229:n} and {r230:n}, and an unbounded clock anchor on {r231:n}, on the 8B side. *Exploratory, derived after '
     'release:* one reading is exposure, since an 8B request runs longer (about {r236:asis} times as long in decode '
     'and {r237:asis} times in prefill, from the independent recomputation only), so a background process at a fixed '
     'rate overlaps 8B requests more often. This reading is not established.', [LBL_RECOMP]),
    ('Section 6.5, branch 5.5.1, decode', ['P1-B5-CTR-PHASE', 'P1-B5-CTR-DBAR', 'P1-B5-CTR-DI', 'P1-B5-CTR-GATE'],
     'On this stack and boundary, the 8B model\'s decode phase used more gross processor-rail energy per request than '
     'the 1.7B model\'s, by {r15:e} J (decision interval [{r48:lo}, {r49:hi}] J, whose statistical part is the '
     'within-session 95% interval [{r36:lo}, {r37:hi}] J). The estimate exceeds the floor gate of {r52:up} J, both '
     'intervals exclude zero, Holm\'s correction rejects, and leaving out any one quad changes none of these. This is '
     'a comparative ({r532:id}) result under the registered claim gate, for this one prompt, this prompt length and '
     'this machine, from one session in which {r11:n} of {r12:n} planned quads were kept. ' + D177,
     ['registered claim gate']),
    ('Section 6.5, branch 5.5.1, prefill', ['P1-B5-CTR-PHASE', 'P1-B5-CTR-DBAR', 'P1-B5-CTR-DI', 'P1-B5-CTR-GATE'],
     'On this stack and boundary, the 8B model\'s 2,048-token prefill phase used more gross processor-rail energy per '
     'request than the 1.7B model\'s, by {r16:e} J (decision interval [{r50:lo}, {r51:hi}] J, whose statistical part '
     'is the within-session 95% interval [{r38:lo}, {r39:hi}] J). The estimate exceeds the floor gate of {r55:up} J, '
     'both intervals exclude zero, Holm\'s correction rejects, and leaving out any one quad changes none of these. '
     'This is a comparative ({r535:id}) result under the registered claim gate, for this one prompt, this prompt '
     'length and this machine, from one session in which {r13:n} of {r14:n} planned quads were kept, the registered '
     'minimum of {r181:n}. ' + D177, ['registered claim gate']),
    ('Section 6.5, leave-one-quad-out', ['P1-B5-CTR-LOO'],
     '**Leave-one-quad-out.** Decode: no single quad changes the verdict; the {r62:n} leave-one-out estimates run '
     'from {r63:lo} to {r64:hi} J. Prefill: no single quad changes the verdict; the {r65:n} leave-one-out estimates '
     'run from {r67:lo} to {r68:hi} J, each over {r66:n} quads, one fewer than the cell minimum of {r505:n}; the '
     'registered check recomputes the contrast on the remaining quads and does not re-apply that minimum.', []),
    ('Section 6.5, decision interval against the floor', ['P1-B5-CTR-DIFLOOR'],
     '**Decision interval against the floor.** In both contrasts the near end of the decision interval lies beyond '
     'the floor gate: {r48:lo} J against {r52:up} J for decode, and {r50:lo} J against {r55:up} J for 2,048-token '
     'prefill.', []),
    ('Section 6.5, descriptive ratios and per-token differences',
     ['P1-B5-RATIO-decode', 'P1-B5-RATIO-prefill', 'P1-B5-PERTOK-decode', 'P1-B5-PERTOK-prefill'],
     'The 8B-to-1.7B ratio of phase energies was {r114:mr} (the geometric mean over kept quads of the per-quad ratio; '
     't interval [{r115:mrlo}, {r116:mrhi}]) for decode and {r117:mr} (same quantity; t interval [{r118:mrlo}, '
     '{r119:mrhi}]) for 2,048-token prefill. Per token, the difference was {r120:tok} (metrology interval '
     '[{r124:toklo}, {r125:tokhi}]; decision interval [{r128:toklo}, {r129:tokhi}]) J per output token and '
     '{r122:tok} (metrology interval [{r126:toklo}, {r127:tokhi}]; decision interval [{r130:toklo}, {r131:tokhi}]) J '
     'per prompt token.', []),
    ('Section 6.5, battery-assist and load-correlated lines', ['P1-B5-CTR-BATT'],
     '*Without quads holding battery-assisted runs:* no quad held a battery-assisted run ({r341:n} such quads, from '
     'the collection record\'s battery-assist flags; not re-derived), so this line equals the primary estimate: '
     'd̄ = {r15:e} J, metrology interval [{r36:lo}, {r37:hi}] J, n = {r11:n} for decode, and d̄ = {r16:e} J, '
     'metrology interval [{r38:lo}, {r39:hi}] J, n = {r13:n} for 2,048-token prefill. *Load-correlated exclusions '
     'not applied:* the registered pipeline could not compute this line; the independent recomputation\'s value, '
     'uncompared, is d̄ = {r376:e} J (metrology interval [{r377:lo}, {r378:hi}] J, n = {r379:n}, {r380:n} quads '
     'restored) for decode and {r381:e} J ([{r382:lo}, {r383:hi}] J, n = {r384:n}, {r385:n} restored) for 2,048-token '
     'prefill.', ['from the collection record', LBL_RJ]),
]

# --- the sites: (name, ids, template, expected count, labels for print-labelled rows)
SITES: list[tuple[str, list[str], str, int, list[str]]] = []
SITES.append(('Section 3.4, whole-machine cross-check, Table S1', ['P1-B5-METER'], METER, 1, []))
SITES.append(('Section 6.1, attempts', ['P1-B5-ATTEMPTS'], ATTEMPTS, 1, [LBL_RJ, LBL_SS]))
SITES.append(('Section 6.1, analysed sessions', ['P1-B5-ANALYSED'], ANALYSED, 1, []))
for _c in TABLE1_IDS:
    SITES.append((f'Table 1, {_c}', TABLE1_FIRST[_c] + [TABLE1_IDS[_c]], table1_row(_c), 1, []))
SITES.append(('Table 1 caption', [], TABLE1_CAPTION, 1, []))
SITES.append(('Table S2, removed units and codes', [], TABLE_S2, 1, []))
SITES.append(('Section 6.1, hazards', ['P1-B5-HAZARDS'], HAZARDS, 1, [LBL_RJ]))
SITES.append(('Table S3, arm hazards', [], TABLE_S3, 1, ['from the arm collection record; not re-derived']))
SITES.append(('Table S4, stage battery temperature', [], TABLE_S4, 1, [LBL_RJ]))
SITES += [(n, ids, t, 1, []) for n, ids, t in TABLE2]
SITES.append(('Section 6.2, interval components', ['P1-B5-INTERVAL-PARTS'], INTERVAL_PARTS_SENTENCE, 1, []))
SITES.append(('Table S5, interval components', [], TABLE_S5, 1, []))
SITES.append(('Section 6.2, battery-assist line', ['P1-B5-BATT-LINE'], BATT_LINE, 1,
              ['from the collection record', LBL_RJ]))
SITES.append(('Section 6.2, load-correlated line', ['P1-B5-LOAD-LINE'], LOAD_LINE, 1, []))
SITES += [(n, ids, t, 1, []) for n, ids, t in TABLE3 + TABLE4]
SITES.append(('Section 6.4, branch 5.4.B failed components', ['P1-B5-DOM-FAILED'], DOM_FAILED, 1, []))
SITES += [(n, ids, t, 1, LABEL_T5) for n, ids, t in TABLE5]
SITES += [(n, ids, t, 1, lab) for n, ids, t, lab in PROSE]
SITES.append(('Section 6.6, across sessions (RL-55)', ['P1-B5-XWIN'], XWIN, 1, []))
SITES.append(('Section 6.6, reference drift', ['P1-B5-NEG8'], NEG8_TEXT, 1, []))
SITES.append(('Table S6, drift screen', [], TABLE_S6, 1, []))
SITES.append(('Table S7, references and corpus', [], TABLE_S7, 1, []))
SITES.append(('Section 6.6, monitor cost', ['P1-B5-MONITOR'], MONITOR, 1, [LBL_SS]))
SITES.append(('Section 6.7, primary-block recomputation (RL-4 vii)', ['P1-RECOMPUTE-SUMMARY'], RECOMPUTE_B5, 1, []))
SITES.append(('Table S8, comparator families', [], TABLE_S8, 1, []))
SITES.append(('Section 11, branch 9.D', ['CP-X02-conclusion'], CONCLUSION_9D, 1, []))

# A print-labelled row in a table cell carries its label in the table note (RL-42), which is its own site.
LABEL_SITE = {'Table 5, decode': 'Table 5 caption, claim level (RL-41 b)',
              'Table 5, prefill': 'Table 5 caption, claim level (RL-41 b)'}

# Ids whose placeholders the two fills replaced.
FILLED = sorted({i for _, ids, _, _, _ in SITES for i in ids})

# Ids that left the text with their unselected branch (5.1.a, 5.2.a, 5.4.R, 5.5.2 to 5.5.5), or with their sentence.
DELETED_WITH_BRANCH = ['P1-B5-NOPACK', 'P1-B5-NOPACK-REASON', 'P1-B5-CELL-REFUSED', 'P1-B5-CELL-REFUSED-REASON',
                       'P1-B5-CTR-L1-REASON', 'P1-B5-CTR-UNRES-REASON', 'P1-B5-CTR-NR-REASON', 'P1-B5-CTR-NE-REASON',
                       'P1-B5-DOM-REFUSED']
DROPPED = ['P1-B5-B-SHARE']  # RL-52 (5): dropped with its sentence

# Block 5 ids left as placeholders (reasons in the run report), and the new Block 6 half of the recompute summary.
PENDING = ['P1-ABS-PART1', 'CP-X01-identity', 'CP-X01-length', 'CP-X08-decode-a-conclusion',
           'P1-RECOMPUTE-SUMMARY-B6']

GONE = ['[BRANCH 5.1.a', '[END BRANCH 5.1]', '[BRANCH 5.2.a', '[END BRANCH 5.2]', '[BRANCH 5.4.A', '[END BRANCH 5.4.A]',
        '[BRANCH 5.4.B', '[END BRANCH 5.4.B]', '**[BRANCH 5.4.R', '[END BRANCH 5.4.R]', '[BRANCH 9.D',
        '[END BRANCH 9.D]'] + [f'BRANCH 5.5.{k}' for k in range(1, 6) if k != 1] + \
       ['[BRANCH 5.5.1', '[END BRANCH 5.5.1]', 'share of each interval taken by B']
PRESENT = ['BRANCH 5.1.a not selected', 'BRANCH 5.2.a not selected', 'BRANCH 5.4.B selected',
           'BRANCH 5.4.R not selected', 'BRANCH 5.5.1 selected for both contrasts', 'BRANCH 9.D: branch B selected']


# ---------------------------------------------------------------- checks

def site_formats() -> dict[int, set]:
    used: dict[int, set] = {}
    for _, _, t, _, _ in SITES:
        for m in PH.finditer(t):
            used.setdefault(int(m.group(1)), set()).add(m.group(2))
    return used


def check_formats() -> None:
    """RL-52 (a): every printed value is its row rounded by the rule for its class, one format per row."""
    for n, fmts in sorted(site_formats().items()):
        if n not in L:
            fail(f'row {n} does not exist')
            continue
        if len(fmts) != 1:
            fail(f'row {n} is printed with more than one format: {sorted(map(str, fmts))}')
        cls = row_class(n)
        for f in fmts:
            if f == 'ledger':
                if n not in FORCED_LEDGER:
                    fail(f'row {n} prints at ledger precision without a recorded comparison flip')
                continue
            if f not in CLASS_FORMATS[cls]:
                fail(f'row {n} ({L[n]["key/leaf"][:60]}) is class {cls!r} but printed with format {f!r}')
            if f == 'R' and not (re.fullmatch(r'\d+\.\d{4}', val(n)) or (n == 1846 and val(n) == '1.99975')):
                fail(f'row {n}: an R or R_cm prints at four decimals as issued (1.99975 excepted), found {val(n)}')
            if f in ROUNDERS and is_tie(dec(n), f):
                NOTES.append(f'row {n}: {val(n)} is an exact tie under {f!r}; rounded half away from zero')


def check_literals(name: str, template: str) -> None:
    literal = AP.sub('', FILL_RE.sub('', PH.sub('', template)))
    for pat in ALLOWED_LITERALS:
        literal = re.sub(pat, '', literal)
    if re.search(r'\d', literal):
        fail(f'{name}: literal text carries a number not taken from a ledger row: {literal!r}')


def verify_allowed_literals() -> None:
    if 'a spread of at most 0.2 is described as "consistent"' not in norm(PLAN.read_text()):
        fail('the "consistent" spread limit 0.2 was not found in analysis plan §8')
    log = DEVLOG.read_text()
    for d in ('DLE-3', 'DLE-4'):
        m = re.search(rf'## {d}\..*?\*\*Status\.\*\* ADOPTED, (\d{{4}}-\d{{2}}-\d{{2}})', log, re.S)
        if not m or m.group(1) != '2026-11-07':
            fail(f'{d}: adoption date is not 2026-11-07 in DEVIATION-LOG.md')
    if len(CMP_ROWS) != 24 or sum(1 for r in CMP_ROWS if val(r[3]) == '0') != 1:
        fail('Table S8: expected 24 comparator families, exactly one of which compared no rows')


def rendered(template: str) -> str:
    t = AP.sub(lambda m: render_attempt(m.group(1)), template)
    return PH.sub(lambda m: render_value(int(m.group(1)), m.group(2)), t)


def check_sites(paper: str) -> None:
    npaper = norm(paper)
    for name, ids, template, count, labels in SITES:
        check_literals(name, template)
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
        text = rendered(template)
        found = npaper.count(norm(text))
        if found != count:
            fail(f'{name}: expected {count} occurrence(s) of the ledger-rendered text, found {found}:\n    {text}')


def check_f4_pairing() -> None:
    """Rows 647-651 (bare `print`) only beside refusal rows 1064-1065, labelled recompute only (Opus F4)."""
    for name, _, t, _, _ in SITES:
        rows = {int(m.group(1)) for m in PH.finditer(t)}
        if rows & set(range(647, 652)):
            if not {1064, 1065} <= rows or 'recompute only; not compared' not in t:
                fail(f'{name}: rows 647-651 printed without refusal rows 1064-1065 and the recompute-only label')


def check_placeholders(paper: str) -> None:
    def present(fid: str) -> bool:
        return re.search(r'\{\{FILL:\s*' + re.escape(fid) + r'\s*(?:\\\||\|)', paper) is not None
    for fid in FILLED + DELETED_WITH_BRANCH + DROPPED:
        if present(fid):
            fail(f'{fid}: placeholder still present after the fill')
    for fid in PENDING:
        if not present(fid):
            fail(f'{fid}: listed as pending but no placeholder found (update this check with its ledger row)')
    for s in GONE:
        if s in paper:
            fail(f'deleted branch marker or dropped sentence still present: {s!r}')
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
    for n, tok in [(550, 'Qwen3-1.7B-4bit/decode'), (566, 'Qwen3-1.7B-4bit/prefill'), (582, 'Qwen3-8B-4bit/decode'),
                   (598, 'Qwen3-8B-4bit/prefill')]:
        if L[n]['key/leaf'] != f'RC.floor_cells[{tok}].floor_cmp_j':
            fail(f'row {n}: not the comparative floor of {tok}')
    # RL-55: two rows for 1.7B prefill R_cm; the fill takes the longer one.
    if not (val(277) == '1.9997' and val(1846) == '1.99975'):
        fail('rows 277/1846: the RL-55 pair of 1.7B prefill R_cm changed')


# ---------------------------------------------------------------- RL-52 (b): stated comparisons and thresholds

def hypot(a: Decimal, b: Decimal) -> Decimal:
    return Decimal(math.hypot(float(a), float(b)))


def comparisons(v) -> list[tuple[str, bool]]:
    """Every comparison the Block 5 text states and every registered threshold test it reports, on values v(n)."""
    out = []
    two = Decimal(2)
    gate = {'decode': 52, 'prefill': 55}
    for c, (dbar, mlo, mhi, dlo, dhi, loo_lo, loo_hi, adj) in {
            'decode': (15, 36, 37, 48, 49, 63, 64, 60), 'prefill': (16, 38, 39, 50, 51, 67, 68, 61)}.items():
        g = gate[c]
        out += [(f'{c}: d̄ exceeds the floor gate', abs(v(dbar)) > v(g)),
                (f'{c}: d̄ > 0 (the 8B model used more)', v(dbar) > 0),
                (f'{c}: metrology interval excludes zero', v(mlo) > 0),
                (f'{c}: decision interval excludes zero', v(dlo) > 0),
                (f'{c}: decision interval near end beyond the floor gate', v(dlo) > v(g)),
                (f'{c}: intervals contain d̄', v(dlo) <= v(mlo) <= v(dbar) <= v(mhi) <= v(dhi)),
                (f'{c}: every LOO estimate keeps sign and stays above the gate', v(loo_lo) > v(g) and v(loo_lo) > 0),
                (f'{c}: no LOO shift exceeds a quarter of the gate (magnitude concern not raised)',
                 max(abs(v(loo_lo) - v(dbar)), abs(v(loo_hi) - v(dbar))) <= v(g) / 4),
                (f'{c}: Holm-adjusted p at or below alpha', v(adj) <= v(8))]
    out += [('decode kept quads at or above the minimum', v(11) >= v(181)),
            ('prefill kept quads at or above the minimum', v(13) >= v(181)),
            ('decode gate is the larger arm gate', v(52) == max(v(53), v(54))),
            ('prefill gate is the larger arm gate', v(55) == max(v(56), v(57)))]
    # Table 3: operative = max(absolute, comparative)
    for a, cm, op in [(53, 550, 53), (56, 566, 56), (290, 582, 54), (293, 598, 57)]:
        out.append((f'Table 3: operative floor row {op} is the larger of rows {a} and {cm}', v(op) == max(v(a), v(cm))))
    # Table 4 and branch 5.4.B: each ratio's side of 2, and its printed corner / point on the same side
    for r, nu, de in [(540, 541, 542), (545, 546, 547), (556, 557, 558), (561, 562, 563), (572, 573, 574),
                      (577, 578, 579), (588, 589, 590), (593, 594, 595)]:
        out.append((f'R row {r} at least 2', v(r) >= two))
        out.append((f'R row {r}: printed corner/point on the same side of 2', (v(nu) / v(de) >= two) == (v(r) >= two)))
    for r, below in [(276, True), (1846, True), (278, True), (279, False)]:
        out.append((f'R_cm row {r} {"below" if below else "at least"} 2', (v(r) < two) == below))
    for r, nu, de in [(843, 844, 845), (1846, 849, 850), (853, 854, 855)]:
        out.append((f'failed R_cm row {r}: printed numerator/denominator below 2', v(nu) / v(de) < two))
    # Table S5: the smallest first-kind bound does not exceed the attribution floor
    for mn, af in [(954, 138), (984, 147), (1026, 156), (1070, 165)]:
        out.append((f'Table S5: smallest first-kind bound row {mn} <= attribution floor row {af}', v(mn) <= v(af)))
    # battery-assist and load lines: no "below the registered minimum of 5 units" sentence owed
    for n in (971, 972, 1003, 1004, 1051, 1052, 1093, 1094, 1013, 1015, 1103, 1105, 647, 648):
        out.append((f'row {n}: n at or above the registered minimum of 5', v(n) >= 5))
    # Section 6.6, cross-session rule |Δ| <= hypot(h_G, h_F) gives the printed word (h from the ledger)
    for d, hg, hf, w in [(974, 975, 976, 978), (1006, 1007, 1008, 1010), (1054, 1055, 1056, 1058),
                         (1096, 1097, 1098, 1100)]:
        agree = abs(v(d)) <= hypot(dec(hg), dec(hf))
        out.append((f'cross-session row {d}: |Δ| against hypot(h_G, h_F) gives {val(w)!r}', agree == (val(w) == 'agree')))
    # Table S1: plausibility band and the registered "consistent" spread limit
    for _, _, _, md, lo, hi, q0, q1, sp, _, w in METER_ROWS:
        out += [(f'Table S1 row {md}: 0 < min ρ and max ρ <= 1', v(lo) > 0 and v(hi) <= 1),
                (f'Table S1 row {sp}: spread at most 0.2 gives {val(w)!r}',
                 (v(sp) <= Decimal('0.2')) == (val(w) == 'consistent')),
                (f'Table S1 row {md}: min <= quartiles <= max', v(lo) <= v(q0) <= v(md) <= v(q1) <= v(hi))]
    # Table S6: screen passes (statistic <= bound), bound = max(terms), allowance = max(bound, excursion)
    for _, _, a, b, c, d, e, g, h in NEG8_ROWS:
        out += [(f'Table S6 row {a}: statistic at most the bound gives {val(h)!r}',
                 (v(a) <= v(d)) == (val(h) == 'passed')),
                (f'Table S6 row {d}: bound is the larger term', v(d) == max(v(b), v(c))),
                (f'Table S6 row {g}: allowance is the larger of bound and excursion', v(g) == max(v(d), v(e)))]
    # Table S8: the agreeing and failing counts make up the compared rows
    for f, _, _, c, p, x, _, w in CMP_ROWS:
        out.append((f'Table S8 {f}: agreeing + failing = compared', v(p) + v(x) == v(c)))
        out.append((f'Table S8 {f}: "every compared row agreed" (no failing row; AGREE where rows were compared)',
                    v(x) == 0 and (val(w) == 'AGREE') == (v(c) > 0)))
    return out


def check_comparisons() -> None:
    fmts = site_formats()

    def printed(n: int) -> Decimal:
        return printed_decimal(n, next(iter(fmts.get(n, {None}))))
    for label, ok in comparisons(dec):
        if not ok:
            fail(f'stated comparison false on the ledger values: {label}')
    for label, ok in comparisons(printed):
        if not ok:
            fail(f'stated comparison flips on the printed (rounded) values: {label}; print at ledger precision')


# ---------------------------------------------------------------- branch derivations

EIGHT_R = [540, 545, 556, 561, 572, 577, 588, 593]
FOUR_RCM = [554, 1846, 586, 602]
TWELVE_STATUS = [807, 812, 817, 822, 827, 832, 837, 842, 847, 852, 857, 862]
TWELVE_DEN = [805, 810, 815, 820, 825, 830, 835, 840, 845, 850, 855, 860]


def derive_54_table() -> str:
    thr = num(275)
    rcm = {n: num(n) for n in (276, 1846, 278, 279)}
    below = [n for n, x in rcm.items() if x < thr]  # equality passes (row 275 note)
    eight_ok = all(num(n) >= thr for n in EIGHT_R)
    if len(below) != 3 or val(518) != 'three' or val(606) != '3' or val(605) != '0':
        fail(f'5.4 table derivation: {len(below)} R_cm below {thr}; rows 518/605/606 say {val(518)}/{val(605)}/{val(606)}')
    if val(604) != val(863) or val(864) != 'false':
        fail(f'5.4 table derivation: branch rows 604/863 {val(604)}/{val(863)}, licence row 864 {val(864)}')
    branch = '5.4.A' if (eight_ok and not below and val(863) == 'A') else ('5.4.B' if val(863) == 'B' else '?')
    print(f'5.4, from the table: eight R rows {EIGHT_R} = {[val(n) for n in EIGHT_R]} (all >= {val(275)}: {eight_ok}); '
          f'R_cm rows 276, 1846, 278, 279 = {[val(n) for n in rcm]}; below: rows {below}; issued branch rows 604/863 = '
          f'{val(863)}, sentence licensed row 864 = {val(864)} -> {branch}.')
    return branch


def derive_54_rule() -> str:
    plan = PLAN.read_text()
    rule = ('**Branch A** (every one of the eight R ≥ 2 and every required R_cm ≥ 2) licenses the dominance sentence '
            'and the contingent subtitle; otherwise **branch B** reports each failed component with null framing.')
    if norm(rule) not in norm(plan):
        fail('5.4 rule derivation: the registered branch rule was not found verbatim in analysis plan §6')
    if 'R ≥ 2 (equality passes)' not in plan:
        fail('5.4 rule derivation: the registered threshold sentence was not found in analysis plan §6')
    eight = [num(n) for n in EIGHT_R]
    required_rcm = [num(n) for n in FOUR_RCM]
    branch = '5.4.A' if all(x >= 2 for x in eight) and all(x >= 2 for x in required_rcm) else '5.4.B'
    print(f'5.4, from the registered rule (analysis plan §6): eight R = {eight}, all >= 2: {all(x >= 2 for x in eight)}; '
          f'required R_cm (RC rows {FOUR_RCM}) = {required_rcm}, all >= 2: {all(x >= 2 for x in required_rcm)} -> {branch}.')
    return branch


def derive_54r_table() -> str:
    statuses = [val(n) for n in TWELVE_STATUS]
    sel = '5.4.R' if any(s != 'complete' for s in statuses) else 'not 5.4.R'
    print(f'5.4.R, from the table: the twelve ratio statuses (rows {TWELVE_STATUS[0]}-{TWELVE_STATUS[-1]}) = '
          f'{sorted(set(statuses))} -> {sel}.')
    return sel


def derive_54r_rule() -> str:
    plan = PLAN.read_text()
    if 'A zero denominator refuses (`dominance_ratio_zero_denominator`)' not in plan:
        fail('5.4.R rule derivation: the registered refusal rule was not found in analysis plan §6')
    dens = [num(n) for n in TWELVE_DEN]
    present = all(NUMERIC.fullmatch(val(n)) for n in TWELVE_DEN + EIGHT_R + [843, 1846, 853, 858])
    sel = '5.4.R' if (any(d == 0 for d in dens) or not present) else 'not 5.4.R'
    print(f'5.4.R, from the registered rule (analysis plan §6, "A zero denominator refuses"): denominators '
          f'{dens}, all positive: {all(d > 0 for d in dens)}; every ratio and input numeric: {present} -> {sel}.')
    return sel


def derive_9d_table() -> str:
    b = {'B': '9.D branch B', 'A': '9.D branch A'}.get(val(863), '?')
    print(f'9.D, from the table: DISC dominance branch row 863 = {val(863)}, dominance sentence licensed row 864 = '
          f'{val(864)}; failing components rows 843, 1846, 853 = {val(843)}, {val(1846)}, {val(853)} -> {b}.')
    return b


def derive_9d_rule() -> str:
    plan = PLAN.read_text()
    if 'otherwise **branch B** reports each failed component with null framing' not in norm(plan):
        fail('9.D rule derivation: the registered branch-B rule was not found in analysis plan §6')
    a = all(num(n) >= 2 for n in EIGHT_R) and all(num(n) >= 2 for n in FOUR_RCM)
    b = '9.D branch A' if a else '9.D branch B'
    failed = [n for n in FOUR_RCM if num(n) < 2]
    print(f'9.D, from the registered rule (the conclusion takes the analysis plan §6 branch): failed components '
          f'(RC rows) {failed} -> {b}.')
    return b


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
    effect_not_above = abs(dbar) <= gate
    obscures = (dlo <= 0 <= dhi) and not (mlo <= 0 <= mhi)
    steps.append(f'|dbar| {dbar} > gate {gate}: {not effect_not_above}; decision interval [{dlo}, {dhi}] '
                 f'excludes 0: {not (dlo <= 0 <= dhi)}')
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
    a, b = derive_54r_table(), derive_54r_rule()
    if not (a == b == 'not 5.4.R'):
        fail(f'branch 5.4.R: table derivation {a!r}, rule derivation {b!r}, selected: not 5.4.R (deleted)')
    a, b = derive_9d_table(), derive_9d_rule()
    if not (a == b == '9.D branch B'):
        fail(f'branch 9.D: table derivation {a!r}, rule derivation {b!r}, selected branch B')
    for c in CONTRASTS:
        a, b = derive_551_table(c), derive_551_rule(c)
        if not (a == b == '5.5.1'):
            fail(f'branch 5.5 {c}: table derivation {a!r}, rule derivation {b!r}, selected 5.5.1')
    if val(509) != 'one':
        fail('branch 5.1.a: row 509 no longer says one analysed attempt per pack')
    att = analysed_attempts()
    for pack, n in (('alpha', 888), ('beta', 925), ('gamma', 1646)):
        if pack in att and str(att[pack]['attempt']) != val(n):
            fail(f'analysed_windows.json attempt of {pack} differs from ledger row {n}')


def main(argv=()) -> int:
    global L
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--paper-ref', help='local Git commit/ref containing the paper to check; no network')
    modes.add_argument('--repo-only', action='store_true', help='check ledger authority and branch arithmetic only')
    args = parser.parse_args(argv)
    FAILURES.clear()
    NOTES.clear()
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
    check_formats()
    check_f4_pairing()
    verify_allowed_literals()
    check_comparisons()
    check_floor_roles()
    check_branches()
    for note in NOTES:
        print('note: ' + note)
    rows = sorted(site_formats())
    print(f'sites: {len(SITES)}; filled ids: {len(FILLED)}; deleted with branch: {len(DELETED_WITH_BRANCH)}; '
          f'dropped: {len(DROPPED)}; pending ids: {len(PENDING)}; ledger rows cited: {len(rows)}; '
          f'stated comparisons checked on ledger and printed values: {len(comparisons(dec))}')
    if FAILURES:
        print(f'FAIL: {len(FAILURES)} problem(s)')
        for f in FAILURES:
            print('  - ' + f)
        return 1
    print(('PASS: repository ledger/branch checks only; paper not checked; SHA-256 ' if args.repo_only else
           'PASS: every filled Block 5 value is its row of the extended ledger rounded by the RL-52 rule; SHA-256 ')
          + AUTHORITY_SHA256)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
