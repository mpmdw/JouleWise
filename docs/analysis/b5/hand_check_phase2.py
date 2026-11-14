#!/usr/bin/env python3
"""RL-38 reader: stdlib only; no analysis imports, custody writes or path chasing.

The custody mode requires separate authorization for the two RL-38 roots. Each
JSON is authenticated before parsing; references inside JSON are inert text.
Use --repo-only for RL-41/RL-42 dispositions and serialization checks against the
frozen, committed phase-2 tables; this mode never instantiates CustodyReader and
does not repeat custody arithmetic. Residuals emit at two significant figures.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import re
import stat
import statistics as st
import subprocess

ROOT_A = Path('/Users/edr/jw-b5-custody/dry-m')
ROOT_B = Path('/Users/edr/jw-b5-custody/release-check-final-20261108T0942Z')
SOURCES = {
    'FILL': (ROOT_A, 'dry-run/restricted/outputs/a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4-results-fill-input.json', 'a29c6cf296199d70d9154719608ad21c07e08fda077224aa05a914b5ecf1f9b4'),
    'CV': (ROOT_A, 'dry-run/restricted/outputs/67d8c231eeb5df2e1240cd3d0b965555ab39755042a2b9676f939f1543716f27-claim-verdicts.json', '67d8c231eeb5df2e1240cd3d0b965555ab39755042a2b9676f939f1543716f27'),
    'EXC': (ROOT_A, 'dry-run/restricted/finalized/analysed-attempt-exclusions-a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46.json', 'a9954365ef44c1b8a65603dd0ba52140109b45569fc795783ca6663d54586f46'),
    'DISC': (ROOT_A, 'dry-run/restricted/disclosures/77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a.json', '77be1a3ed3a851206a0762334cbdeaab5b40e83e3d9fcdbcf404da5e4d871f6a'),
    'SENS': (ROOT_A, 'dry-run/restricted/outputs/4a7c4315327d29b214e79961d6f991af13dcabc24898368564007ac2e356ff28.json', '4a7c4315327d29b214e79961d6f991af13dcabc24898368564007ac2e356ff28'),
    'STEP': (ROOT_A, 'dry-run/restricted/outputs/b0f80f7265cf84203ded237245ae25cf87adfd987c2265a92b52c96efb1ea5b5.json', 'b0f80f7265cf84203ded237245ae25cf87adfd987c2265a92b52c96efb1ea5b5'),
    # RESULTS §0 prints only these prefixes. Also require equality with the
    # entire content-addressed filename (record this weaker §0 pin explicitly).
    'PROJ-A': (ROOT_A, 'dry-run/restricted/outputs/ed3cadb1f0ac2fc137efab3f4528702c704055ffa5bdf24399c335081570f5bf-projection-alpha.json', 'ed3cadb1f0ac'),
    'PROJ-B': (ROOT_A, 'dry-run/restricted/outputs/db6d525129f90ef24bb46f83ab5e66283424970c743f35d322c8961f9b683e2e-projection-beta.json', 'db6d525129f9'),
    'REC': (ROOT_A, 'dry-run/B5-BLIND-DRY-RUN-RECORD.json', '66adc66e89f1a621009dd2ca98bc7c41b202d5c43a26a82af8a633a54c34aa03'),
    'RC': (ROOT_B, 'recompute.json', 'c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc'),
    'CMP': (ROOT_B, 'comparison.json', 'b12b7e1b32b27159be894221dcde7e334784061314fe91a39166faa36f72f4c9'),
    'VER': (ROOT_B, 'verdict.json', None),
}


class CustodyReader:
    def __init__(self):
        self.opened = {}
        self.projection_pins = set()

    @staticmethod
    def checked_path(root, relative):
        """Check lexical allowlist *before* any filesystem operation.

        Refuse symlink components inside the authorized root; do not resolve
        parents or touch a referenced path outside the allowlist.
        """
        if root not in (ROOT_A, ROOT_B):
            raise ValueError('root outside unseal')
        rel = Path(relative)
        if rel.is_absolute() or '..' in rel.parts or not rel.parts:
            raise ValueError('path outside unseal')
        p = root
        for part in ('', *rel.parts):
            p = p / part if part else p
            mode = p.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError('symlink refused')
        if not stat.S_ISREG(mode):
            raise ValueError('not a regular file')
        return p

    def read(self, alias):
        root, relative, expected = SOURCES[alias]
        p = self.checked_path(root, relative)
        raw = p.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if expected is not None and not digest.startswith(expected):
            raise ValueError(f'{alias}: RESULTS §0 hash mismatch')
        if expected and len(expected) < 64:
            if p.name[:64] != digest:
                raise ValueError(f'{alias}: content-address mismatch')
            if digest not in self.projection_pins:
                raise ValueError(f'{alias}: full digest not authenticated by REC outputs; read REC first')
        self.opened[alias] = {'path': str(p), 'sha256_before': digest,
                              'section0_pin': expected or 'unhashed in RESULTS §0'}
        parsed = json.loads(raw)
        if alias == 'REC':
            self.projection_pins = {x['sha256'] for step in parsed['steps'] for x in step['outputs']}
        return parsed

    def finish(self):
        for alias, record in self.opened.items():
            root, relative, _ = SOURCES[alias]
            p = self.checked_path(root, relative)
            with p.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            record['sha256_after'] = digest
            if digest != record['sha256_before']:
                raise ValueError(f'{alias}: custody changed during read')
        return self.opened


def shape(value, depth=2):
    """Structural inspection only: keys/types/counts, never scalar values."""
    if isinstance(value, dict):
        return {k: shape(v, depth-1) if depth > 0 else type(v).__name__
                for k, v in value.items()}
    if isinstance(value, list):
        return {'length': len(value), 'item_shape': shape(value[0], depth-1)
                if value and depth > 0 else None}
    return type(value).__name__


def student_tail(t, df):
    """Two-sided t tail via the incomplete-beta power series, no libraries."""
    a, b = df / 2, .5
    x = df / (df + t*t)
    term = total = 1.0
    for k in range(1, 10000):
        term *= (a+k-1)*(1-b+k-1)*x / ((a+k)*k)
        total += term
        if abs(term) < abs(total)*1e-16:
            break
    else:
        raise ArithmeticError('beta series did not converge')
    return math.exp(a*math.log(x)-math.log(a)-math.lgamma(a)
                    -math.lgamma(b)+math.lgamma(a+b))*total


def t975(df):
    lo, hi = 1.0, 16.0
    for _ in range(80):
        mid = (lo+hi)/2
        if student_tail(mid, df) > .05:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def contrast_statistics(ds):
    n = len(ds)
    mu, sd = st.fmean(ds), st.stdev(ds)
    se = sd / math.sqrt(n)
    mult = round(t975(n-1), 3)
    return {'mean': mu, 'sd': sd, 'se': se, 'df': n-1, 't': mult,
            'lower': mu-mult*se, 'upper': mu+mult*se,
            'p': student_tail(mu/se, n-1), 'n': n}


def stratified(rs, bs):
    """Registered .2 repeat / .8 quad estimator, exact t for cell h."""
    mu = .2*st.fmean(rs)+.8*st.fmean(bs)
    variance = .04*st.variance(rs)/len(rs)+.64*st.variance(bs)/len(bs)
    df = min(len(rs), len(bs))-1
    # The registration pins df 4/5/6 at nine decimals.
    mult = round(t975(df), 9) if df in (4, 5, 6) else t975(df)
    return {'mean': mu, 'h': mult*math.sqrt(variance), 'df': df,
            'n_r': len(rs), 'n_b': len(bs)}


def point_floor(vs, absolute, mult=None):
    mu, n = st.fmean(vs), len(vs)
    deviations = [x-mu for x in vs] if absolute else vs
    if mult is None:
        mult = round(t975(n-1), 3)
    prediction = mult*st.stdev(vs)*math.sqrt(1+1/n)
    if not absolute:
        prediction += abs(mu)
    return max(max(map(abs, deviations)), prediction)


def widened_floor(vs, widths, absolute, common=None):
    """Enumerate the registered box, or one shared sign plus local signs."""
    mult = round(t975(len(vs)-1), 3)
    best = point_floor(vs, absolute, mult)
    for signs in itertools.product((-1, 1), repeat=len(vs)):
        for shared_sign in (-1, 1) if common is not None else (0,):
            corner = [v+s*w+(shared_sign*common[i] if common is not None else 0)
                      for i,(v,s,w) in enumerate(zip(vs, signs, widths))]
            best = max(best, point_floor(corner, absolute, mult))
    return best


def quad_members(members, phase, unit):
    number = re.search(r'(b\d\d)$', unit)[1]
    result = []
    for position in ('a1', 'b1', 'b2', 'a2'):
        candidates = [v for k,v in members.items()
                      if f'-{phase}-' in k and k.endswith(f'-{number}-{position}')]
        if len(candidates) != 1:
            raise ValueError('quad member identity is ambiguous or missing')
        result.append(candidates[0])
    return result


def quad_difference(ms, phase):
    es = [x['E_j'][phase] for x in ms]
    return (es[1]+es[2]-es[0]-es[3])/2


def printed_compare(printed, value):
    """Classify using the unrounded residual; emit it at two significant figures."""
    cleaned = printed.replace('−', '-').replace(',', '').lstrip('+')
    percent = cleaned.endswith('%')
    try:
        target = Decimal(cleaned.rstrip('%'))
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise ValueError
        actual = Decimal(str(value))*(100 if percent else 1)
    except (ValueError, ArithmeticError):
        normalized = {None: 'none', True: 'true', False: 'false'}.get(value, str(value))
        same = printed == normalized
        return str(normalized), '0' if same else 'different', 'exact' if same else 'MISMATCH'
    quantum = Decimal(1).scaleb(target.as_tuple().exponent)
    rounded = actual.quantize(quantum)
    residual = actual-target
    status = 'exact' if residual == 0 else 'within-rounding' if rounded == target else 'MISMATCH'
    return format(rounded, 'f')+('%' if percent else ''), difference_text(str(residual)), status


def difference_text(text):
    """Round a residual, retaining an optional unit and exact zero."""
    if not text:
        return text
    number, *unit = text.split(' ', 1)
    value = Decimal(number)
    if not value.is_finite():
        raise ValueError('non-finite difference')
    rounded = '0' if value == 0 else format(value, '.2g')
    return rounded + (' ' + unit[0] if unit else '')


def round_differences(rows):
    for row in rows:
        row['difference'] = difference_text(row['difference'])
        if 'note' in row:
            row['note'] = re.sub(
                r'(?<=source difference=)[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',
                lambda m: difference_text(m[0]), row['note'])


def dle5_leaf_counts(contrasts):
    """Return normalized path count and scalar instances in DLE-5's three groups."""
    paths = []

    def visit(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, path + (key,))
        elif isinstance(value, list):
            for child in value:
                visit(child, path + ('*',))
        else:
            paths.append(path)

    for contrast in contrasts:
        visit(contrast['floor']['point_floor_diagnostics'], ('floor', 'point_floor_diagnostics'))
        for resolution in contrast['floor']['resolutions']:
            visit(resolution['point_floor_diagnostics'], ('floor', 'resolutions', '*', 'point_floor_diagnostics'))
        visit(contrast['claim_evaluation']['floor_limit'], ('claim_evaluation', 'floor_limit'))
    return len(set(paths)), len(paths)


RECORDED_ROWS = {341, 342, 525, 526, 532, 535}
SINGLE_SOURCE_ROWS = {*range(236, 242), 348, 349, 350, 362, 367, 392, 393, 394}
BOUND_ROWS = {388, 389, 390, 391, 395}
EXPECTED_COUNTS = Counter({'exact': 261, 'within-rounding': 256,
                           'recorded-judgment': 6, 'single-source': 14, 'MISMATCH': 1})
REVIEW_BASE = '9159dbf05'


def apply_print_rulings(rows):
    """Install RL-41(b), as amended by RL-42, preserving historical phase1_match."""
    # Later authorities append rows. These rulings and their count expectation
    # apply only to the original 538 rows; they do not review an extension.
    original_rows = rows[:538]
    for number, row in enumerate(original_rows, 2):
        addition = None
        if number in RECORDED_ROWS:
            row.update(match='recorded-judgment', hand_check='recorded judgment; not re-derived')
            addition = 'from the collection record; not re-derived; attribute the pinned source in the sentence or table note (§4.7)'
        elif number in SINGLE_SOURCE_ROWS:
            row.update(match='single-source', hand_check='single-source; not independently recomputed')
            if number in {348, 349, 350}:
                addition = 'from the registered disclosure record; not independently recomputed'
            else:
                addition = 'from the independent recomputation only'
            if number not in {392, 393, 394}:
                addition += '; never in the abstract or conclusion, never as support for a claim word'
            if number in {236, 237}:
                addition += '; duration ratios print to two significant figures (RL-39)'
            if number in {362, 367}:
                addition += '; print with any whole-machine phase energy, labelled'
            if number in {392, 393, 394}:
                addition += '; prefill duration bound does not decide the scaling factor'
        elif number in BOUND_ROWS:
            # Opus independently confirmed these values at printed precision;
            # RL-42 accepts that check. No new custody read is implied here.
            if row['source_match'] not in ('exact', 'within-rounding'):
                raise ValueError(f'bound row {number}: unexpected source check word')
            row.update(match=row['source_match'], hand_check='hand check: Opus cold review, bound argument')
            addition = 'hand check: Opus cold review, bound argument'
        elif number == 522:
            row.update(rederived_value='84', source_value='84', source_match='exact',
                       match='exact', difference='0', hand_check='normalized path count; Opus cold review')
            row['note'] = ('SOURCED: count distinct normalized leaf paths (list indices collapsed to *) in '
                           'FILL.gamma.contrasts[*].{floor.point_floor_diagnostics,'
                           'floor.resolutions[*].point_floor_diagnostics,claim_evaluation.floor_limit}; '
                           'DLE-5: 14 + 10C + 5R, C=6, R=2; source difference=0')
            addition = '84 normalized leaf paths; 118 scalar leaves'
        elif number in {242, 243, 244, 490, 491, 492, 528}:
            row['match'] = 'exact'
            if number == 528:
                row['hand_check'] = 'count stored clean flags'
            addition = 'over stored flags'
        elif number == 529:
            row.update(match='exact', hand_check='release comparator: 189 sensitivity rows agree')
            addition = "compared by the release comparator; the acceptance record's alignment bounds are inputs"
        elif number in {530, 531, 533, 534}:
            row.update(match='exact', hand_check='registered outcome rule; Opus cold review; comparator agreement')
            addition = ('prerequisites of the not-estimable codes are recorded judgments; '
                        'estimate exceeds floor gate, both intervals exclude zero, Holm rejects, '
                        'leave-one-out keeps sign and floor')
        if addition:
            row['note'] = row['note'].split('; HAND NOT DONE:')[0].split('; RL-41/RL-42:')[0]
            row['note'] += '; RL-41/RL-42: ' + addition
        row['paper1'] = ('not-printed' if 388 <= number <= 395 else
                         'print-labelled' if row['match'] in ('recorded-judgment', 'single-source') else 'print')
    counts = Counter(row['match'] for row in original_rows)
    if counts != EXPECTED_COUNTS:
        raise ValueError(f'STOP: RL-42 counts differ: actual={dict(counts)}, expected={dict(EXPECTED_COUNTS)}')
    return counts


def table_text(rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def repository_tables(write=False):
    """Replay the dispositions/rounding from frozen Git tables, never custody."""
    dest = Path(__file__).absolute().parent
    repo = dest.parents[2]
    tables = {}
    for name in ('rederivation.tsv', 'hand_checks_phase2.tsv'):
        raw = subprocess.run(['git', 'show', f'{REVIEW_BASE}:docs/analysis/b5/{name}'],
                             cwd=repo, check=True, capture_output=True, text=True).stdout
        tables[name] = list(csv.DictReader(io.StringIO(raw), delimiter='\t'))
    counts = apply_print_rulings(tables['rederivation.tsv'])
    for rows in tables.values():
        round_differences(rows)
    rendered = {name: table_text(rows).encode() for name, rows in tables.items()}
    for name, content in rendered.items():
        current = (dest / name).read_bytes()
        extended = name == 'rederivation.tsv' and len(current.splitlines()) > 539
        if extended:
            if not current.startswith(content):
                raise ValueError('original ledger prefix differs; refuse to overwrite an extension')
            # Check/preserve the reviewed prefix only. RL-52 has its own reader.
            rendered[name] = content = current
        if write:
            (dest / name).write_bytes(content)
        elif current != content:
            raise ValueError(f'{name}: committed table differs from repository-only output')
    print(json.dumps({'mode': 'repository-only; no custody arithmetic rerun',
                      'counts': dict(counts), 'total': sum(counts.values()),
                      'tables': list(rendered), 'byte_identical': not write,
                      'scope': 'original 538 ledger rows; appended rows are not checked here'}, indent=2))


def hand_calculations(d):
    """Return independent aggregates; member data never leave this function."""
    rc = d['RC']
    calc, locators = {}, {}
    def save(key, value, source, formula):
        calc[key] = value
        locators[key] = (source, formula)
    for cid, c in rc['contrasts'].items():
        phase = 'decode' if '-decode-' in cid else 'prefill'
        members = rc['members']['GAMMA']
        quads = [quad_members(members, phase, unit) for unit in c['kept_quads']]
        ds = [quad_difference(ms, phase) for ms in quads]
        src = f'RC.members.GAMMA[*].E_j.{phase}; RC.contrasts[{cid}].kept_quads'
        stats = contrast_statistics(ds)
        for k,v in stats.items():
            save(f'{cid}.{k}',v,src,'d=(B1+B2-A1-A2)/2; mean, sample SD, SE=SD/sqrt(n); rounded t; t tail')
        for i,v in enumerate(ds):
            save(f'{cid}.d_k[{i}]',v,src,'(B1+B2-A1-A2)/2')
        loo_means=[st.fmean(ds[:i]+ds[i+1:]) for i in range(len(ds))]
        for k,v in [('loo_min',min(loo_means)),('loo_max',max(loo_means))]:
            save(f'{cid}.{k}',v,src,'drop each kept quad in turn; mean remaining d values')
        clock = st.fmean(sum(x['a_bop_j'][phase] for x in ms)/2 for ms in quads)
        drift = rc['windows']['GAMMA']['neg8']['allowance_j']
        for k,v in [('clock',clock),('drift',drift),('D',clock+drift),
                    ('decision_lower',stats['lower']-clock-drift),
                    ('decision_upper',stats['upper']+clock+drift)]:
            save(f'{cid}.{k}',v,f'{src}; RC.members.GAMMA[*].a_bop_j.{phase}; RC.windows.GAMMA.neg8.allowance_j',
                 'clock=mean(sum four member bounds/2); D=clock+0+allowance; widen CI by D')
        tokens=512 if phase=='decode' else 2048
        for label,base in [('per_token','mean'),('ci_token_lower','lower'),('ci_token_upper','upper'),('di_token_lower','decision_lower'),('di_token_upper','decision_upper')]:
            save(f'{cid}.{label}',calc[f'{cid}.{base}']/tokens,src+'; CV.bundle_audit[*].token_provenance',
                 f'independent {base} divided by registered runtime denominator {tokens}')
        logs = [math.log((ms[1]['E_j'][phase]+ms[2]['E_j'][phase]) /
                         (ms[0]['E_j'][phase]+ms[3]['E_j'][phase])) for ms in quads]
        center = st.fmean(logs)
        h = t975(len(logs)-1)*st.stdev(logs)/math.sqrt(len(logs))
        for k,v in [('ratio',math.exp(center)),('ratio_lower',math.exp(center-h)),('ratio_upper',math.exp(center+h))]:
            save(f'{cid}.{k}',v,src,'exp(mean(log(Bbar/Abar)) +/- exact t*SD(log ratios)/sqrt(n))')
        load_codes = {'contention.request_overlap','thermal.os_level_nonzero','thermal.powermetrics_pressure_elevated'}
        exc = next(x for x in d['EXC']['cells'] if x['cell_id']==cid)
        restored = [x['unit_id'] for x in exc['dropped_units'] if set(x['codes']) <= load_codes]
        load_ds = [quad_difference(quad_members(members,phase,u),phase) for u in c['kept_quads']+restored]
        for k,v in contrast_statistics(load_ds).items():
            save(f'load.{cid}.{k}',v,src+f'; EXC.cells[cell_id={cid}].dropped_units',
                 'ignore only three load-correlated codes; keep all other removals; recompute d/mean/CI')
    for cellid, cell in rc['reported_cells'].items():
        phase, model = cell['phase'], cell['model']
        pack = 'ALPHA' if '1.7B' in model else 'BETA'
        mm = rc['members'][pack]
        rs = [mm[u]['E_j'][phase] for u in cell['kept_units']['repeat']]
        quads = [quad_members(mm,phase,u) for u in cell['kept_units']['quad']]
        bs = [st.fmean(x['E_j'][phase] for x in ms) for ms in quads]
        stats = stratified(rs,bs)
        kept = [mm[u] for u in cell['kept_units']['repeat']]+[x for ms in quads for x in ms]
        average_bound = .2*st.fmean(mm[u]['a_bop_j'][phase] for u in cell['kept_units']['repeat'])+.8*st.fmean(x['a_bop_j'][phase] for ms in quads for x in ms)
        bound = average_bound+rc['windows'][pack]['neg8']['allowance_j']/2
        stats.update(B=bound,attribution=max(x['a_bop_j'][phase] for x in kept))
        stats.update(lower=stats['mean']-stats['h']-bound,upper=stats['mean']+stats['h']+bound)
        src=f'RC.members.{pack}[*].{{E_j,a_bop_j}}.{phase}; RC.reported_cells[{cellid}].kept_units; RC.windows.{pack}.neg8.allowance_j'
        for k,v in stats.items():
            save(f'{cellid}.{k}',v,src,'m=.2*mean(repeats)+.8*mean(quad means); V=.04*var(r)/nr+.64*var(b)/nb; exact registered t*h; B=stratified clock+allowance/2; attribution=max member clock bound')
        save(f'{cellid}.per_token',stats['mean']/(512 if phase=='decode' else 2048),src,'stratified cell mean divided by runtime token denominator')
        gamma=rc['members']['GAMMA']
        cid=next(k for k in rc['contrasts'] if ('decode' in k)==(phase=='decode'))
        side=('a1','a2') if pack=='ALPHA' else ('b1','b2')
        arm=[]
        for unit in rc['contrasts'][cid]['kept_quads']:
            number=re.search(r'b\d\d$',unit)[0]
            arm.extend(x['E_j'][phase] for k,x in gamma.items() if f'-{phase}-' in k and any(k.endswith(f'-{number}-{p}') for p in side))
        save(f'{cellid}.cross_delta',st.fmean(arm)-stats['mean'],src+'; RC.members.GAMMA[*].E_j; RC.contrasts[*].kept_quads',
             'mean matching GAMMA kept arm members minus independent stratified floor-session cell')
        machine = rc['disclosures']['whole_machine']['windows'][pack]['members']
        def machine_member(member):
            return machine[next(k for k,v in mm.items() if v is member)]['phases'][phase]
        mrs = [machine[u]['phases'][phase]['energy_J'] for u in cell['kept_units']['repeat']]
        mbs = [st.fmean(machine_member(x)['energy_J'] for x in ms) for ms in quads]
        machine_stats = stratified(mrs,mbs)
        ratios = [x['E_j'][phase]/machine_member(x)['energy_J'] for x in kept]
        machine_stats['share']=st.median(ratios)
        for k,v in machine_stats.items():
            save(f'machine.{cellid}.{k}',v,
                 f'RC.disclosures.whole_machine.windows.{pack}.members[*].phases.{phase}.energy_J; '+src,
                 'same .2/.8 estimator and h on gross meter-only member energies; share=median(member rail/gross meter energy)')
    for label, f in rc['floors'].items():
        model, phase, form = label.split('/')
        pack='ALPHA' if '1.7B' in model else 'BETA'
        mm=rc['members'][pack]
        absolute=form=='absolute'
        vs=[mm[u]['E_j'][phase] for u in f['kept_units']] if absolute else [quad_difference(quad_members(mm,phase,u),phase) for u in f['kept_units']]
        point=point_floor(vs,absolute)
        corner=widened_floor(vs,f['widths_j'],absolute)
        guard=1 if len(vs)>=10 else math.sqrt(9/(len(vs)-1))
        values={'point_guarded':guard*point,'guarded':guard*corner,'minted':guard*corner+f['allowance_j']}
        if not absolute:
            values['R_cm']=widened_floor(vs,f['local_j'],False,common=f['shared_j'])/point
        for k,v in values.items():
            save(f'floor.{label}.{k}',v,f'RC.members.{pack}[*].E_j.{phase}; RC.floors[{label}].{{kept_units,widths_j,local_j,shared_j,allowance_j}}',
                 'point=max(max|deviation|,Student prediction); enumerate all +/- width corners; guard=sqrt(9/(n-1)) below n=10; minted=guard*corner+allowance; Rcm=shared-sign/local-sign replay divided by point')
    for model in ('Qwen3-1.7B-4bit','Qwen3-8B-4bit','Qwen2.5-1.5B-Instruct-4bit'):
        members=rc['disclosures']['whole_machine']['windows']['GAMMA']['members']
        rows=[v['phases']['request'] for v in members.values() if v['model']==model]
        ratios=[x['rail_delta_J']/(x['meter']['delta_J']+x['battery']['delta_J']) for x in rows]
        for k,v in [('median',st.median(ratios)),('minimum',min(ratios)),('maximum',max(ratios))]:
            save(f'request.{model}.{k}',v,'RC.disclosures.whole_machine.windows.GAMMA.members[*].phases.request',
                 'rho=rail_delta_J/(meter.delta_J+battery.delta_J); median/min/max within model')
    ordered=sorted(rc['contrasts'],key=lambda cid:calc[f'{cid}.p'])
    adjusted=[min(1,2*calc[f'{ordered[0]}.p']),min(1,max(2*calc[f'{ordered[0]}.p'],calc[f'{ordered[1]}.p']))]
    for cid,p in zip(ordered,adjusted):
        save(f'{cid}.adjusted_p',p,'RC.members.GAMMA[*].E_j; RC.contrasts[*].kept_quads',
             'Holm m=2 on independently computed Student tails; cumulative maximum')
    return calc, locators


BASE = '35b0e98d12cde94d3522419c45da9b417613e2d4'
RESULTS_SHA256 = 'fb5f81e8741532d79b059b2ca7c44b1c479f0f983c28527ab6e2511d7dfb6f55'


def source_bindings(d, calc):
    """Explicit phase-1 row -> frozen leaf map. No value-based searching."""
    bindings = {}
    def bind(row, value, key, hand=None, hold=None):
        if not isinstance(value,(str,int,float,bool,Decimal)) and value is not None:
            raise ValueError(f'non-scalar source at ledger row {row}: {key} ({type(value).__name__})')
        bindings[row] = dict(value=value, key=key, hand=hand, hold=hold)
    def batch(rows, values, keys, hands=None, hold=None):
        assert len(rows)==len(values)==len(keys)
        for row,value,key,hand in zip(rows,values,keys,hands or [None]*len(rows)):
            bind(row,value,key,hand,hold)
    cids=list(d['RC']['contrasts'])
    cv=d['CV']['contrasts']; fill=d['FILL']['gamma']['contrasts']; rc=d['RC']
    # RESULTS refers to a release-check exit, not a release_checkout.exit_status
    # leaf (which does not exist); source the two stage exits explicitly.
    exits=[d['VER']['stages'][k]['exit'] for k in ('recompute','comparator')]
    assert exits[0]==exits[1]
    bind(2,exits[0],'VER.stages.{recompute,comparator}.exit')
    batch([15,16],[x['estimate'] for x in fill],
          [f'FILL.gamma.contrasts[{i}].estimate' for i in range(2)],
          [f'{cid}.mean' for cid in cids])
    for i,cid in enumerate(cids):
        batch(list(range(17+i*4,21+i*4)),[cv[i]['estimator'][k] for k in ('s_d','SE_total','df','t_critical_95')],
              [f'CV.contrasts[{i}].estimator.{k}' for k in ('s_d','SE_total','df','t_critical_95')],
              [f'{cid}.{k}' for k in ('sd','se','df','t')])
        for row,term in [(41+i*4,0),(43+i*4,2)]:
            bind(row,cv[i]['deterministic_bounds']['terms'][term]['bound'],
                 f'CV.contrasts[{i}].deterministic_bounds.terms[{term}].bound',f'{cid}.'+('clock' if term==0 else 'drift'))
        for row,arm in [(53+i*3,0),(54+i*3,1)]:
            model='Qwen3-1.7B-4bit' if arm==0 else 'Qwen3-8B-4bit'
            phase='decode' if i==0 else 'prefill'
            bind(row,fill[i]['floor']['arm_gates'][arm]['floor_gate_j'],
                 f'FILL.gamma.contrasts[{i}].floor.arm_gates[{arm}].floor_gate_j',
                 f'floor.{model}/{phase}/absolute.minted')
        for j,v in enumerate(rc['contrasts'][cid]['d_k']):
            bind((71 if i==0 else 77)+j,v,f'RC.contrasts[{cid}].d_k[{j}]',f'{cid}.d_k[{j}]')
        for row,leaf,hand in [(25+i*5,'dbar_j','mean'),(26+i*5,'s_d_j','sd'),(27+i*5,'se_j','se'),(28+i*5,'n','df'),(29+i*5,'t_star','t')]:
            value=rc['contrasts'][cid][leaf]-(1 if hand=='df' else 0)
            bind(row,value,f'RC.contrasts[{cid}].{leaf}'+('-1' if hand=='df' else ''),f'{cid}.{hand}')
        for row,leaf,side,hand in [(36+i*2,'metrology_interval_j',0,'lower'),(37+i*2,'metrology_interval_j',1,'upper'),(48+i*2,'decision_interval_j',0,'decision_lower'),(49+i*2,'decision_interval_j',1,'decision_upper')]:
            bind(row,rc['contrasts'][cid][leaf][side],f'RC.contrasts[{cid}].{leaf}[{side}]',f'{cid}.{hand}')
        bind(40+i*4,rc['contrasts'][cid]['D_j'],f'RC.contrasts[{cid}].D_j',f'{cid}.D')
        bind(58+i,rc['contrasts'][cid]['p'],f'RC.contrasts[{cid}].p',f'{cid}.p')
        bind(60+i,rc['contrasts'][cid]['holm_p'],f'RC.contrasts[{cid}].holm_p',f'{cid}.adjusted_p')
        bind(120+i*2,rc['descriptive'][cid]['per_token_difference_j'],f'RC.descriptive[{cid}].per_token_difference_j',f'{cid}.per_token')
        for row,leaf,side,hand in [(124+i*2,'per_token_metrology_interval_j',0,'ci_token_lower'),(125+i*2,'per_token_metrology_interval_j',1,'ci_token_upper'),(128+i*2,'per_token_decision_interval_j',0,'di_token_lower'),(129+i*2,'per_token_decision_interval_j',1,'di_token_upper')]:
            bind(row,rc['descriptive'][cid][leaf][side],f'RC.descriptive[{cid}].{leaf}[{side}]',f'{cid}.{hand}')
        for row,op,hand in [(63 if i==0 else 67,min,'loo_min'),(64 if i==0 else 68,max,'loo_max')]:
            bind(row,op(x['dbar_j'] for x in rc['contrasts'][cid]['loo']),f'{op.__name__}(RC.contrasts[{cid}].loo[*].dbar_j)',f'{cid}.{hand}')
    counts=Counter(x['family'] for x in d['CMP']['comparisons'])
    for row,family in [(112,'descriptive_ratio'),(113,'per_token_j'),(132,'reported_cell_j')]:
        bind(row,counts[family],f'count(CMP.comparisons[family={family}])')
    mag=[x for x in d['DISC']['contrasts'] if x['label']=='magnitude_ratio']
    for i,cid in enumerate(cids):
        x=next(x for x in mag if x['contrast_id']==cid)
        batch(list(range(114+3*i,117+3*i)),[x[k] for k in ('ratio','lower','upper')],
              [f'DISC.contrasts[label=magnitude_ratio,contrast_id={cid}].{k}' for k in ('ratio','lower','upper')],
              [f'{cid}.{k}' for k in ('ratio','ratio_lower','ratio_upper')])
    cellids=['df-ph-decode-qwen3-1p7b','df-ph-prefill-p2048-qwen3-1p7b','df-ph-decode-qwen3-8b','df-ph-prefill-p2048-qwen3-8b']
    for offset,cellid in enumerate(cellids):
        sens=next(x for x in d['SENS']['reported_cells'] if x['cell_id']==cellid.replace('df-','d117-reported-mean-',1))
        row=133+9*offset
        for delta,leaf,hand in [(0,'mean_j','mean'),(1,'lower_j','lower'),(2,'upper_j','upper'),(3,'h_j','h'),(4,'B_j','B'),(5,'attribution_floor_j','attribution')]:
            bind(row+delta,sens['primary'][leaf],f'SENS.reported_cells[cell_id={sens["cell_id"]}].primary.{leaf}',f'{cellid}.{hand}')
        for delta,leaf in [(6,'n_r'),(7,'n_b')]:
            bind(row+delta,rc['reported_cells'][cellid][leaf],f'RC.reported_cells[{cellid}].{leaf}',f'{cellid}.{leaf}')
        bind(row+8,rc['reported_cells'][cellid]['per_token']['j_per_token'],f'RC.reported_cells[{cellid}].per_token.j_per_token',f'{cellid}.per_token')
    cross=[x for x in d['DISC']['cells'] if x['label']=='cross_window']
    for row,model,phase in [(169,'Qwen3-1.7B-4bit','decode'),(170,'Qwen3-1.7B-4bit','prefill'),(171,'Qwen3-8B-4bit','prefill'),(172,'Qwen3-8B-4bit','decode')]:
        x=next(x for x in cross if x['cell_id'].endswith('qwen3-'+('1p7b' if '1.7B' in model else '8b')) and ('decode' in x['cell_id'])==(phase=='decode'))
        cellid='df-ph-'+('decode' if phase=='decode' else 'prefill-p2048')+'-qwen3-'+('1p7b' if '1.7B' in model else '8b')
        bind(row,x['delta_j'],f'DISC.cells[label=cross_window,cell_id={x["cell_id"]}].delta_j',f'{cellid}.cross_delta')
    removed=[x for x in d['CV']['bundle_audit'] if 'unit_removed_by_exclusion_function' in x['base_reason_codes']]
    bind(176,len(removed),'count(CV.bundle_audit[base_reason_codes contains unit_removed_by_exclusion_function])')
    stages={}
    for x in d['DISC']['contrasts']:
        if x['label']=='removed unit':
            for stage in x['stage_ids']:
                match=re.search(r'science-(\d\d).*blocks-(\d\d)-(\d\d)',stage)
                stages[int(match[1])]=(int(match[2]),int(match[3]))
    for stage in range(1,5):
        batch([190+(stage-1)*2,191+(stage-1)*2],list(stages[stage]),
              [f'DISC.contrasts[label=removed unit].stage_ids[science-{stage:02d}].blocks_{k}' for k in ('first','last')])
    excluded=[x for x in d['EXC']['members_excluded'] if '-contrast-' in x['run_id']]
    for row,x in zip(range(198,209),excluded):
        phase='decode' if '-decode-' in x['run_id'] else 'prefill'
        bind(row,phase+':'+x['run_id'].split('-contrast-')[-1],f'EXC.members_excluded[run_id={x["run_id"]}].codes')
    bind(214,len(rc['windows']['GAMMA']['neg8']['corpus_ids']),'count(RC.windows.GAMMA.neg8.corpus_ids)')
    scaled=rc['disclosures']['scaled_allowance']['contrasts']
    for row,cid in [(236,cids[0]),(237,cids[1])]:
        bind(row,scaled[cid]['T_b_s']/scaled[cid]['T_a_s'],f'RC.disclosures.scaled_allowance.contrasts[{cid}].T_b_s / T_a_s',
             hold='dependent duration ratio: member phase durations for GAMMA are absent in §0 sources')
    for i,cid in enumerate(cids):
        for j,leaf in enumerate(('T_b_s','T_a_s')):
            bind(238+i*2+j,scaled[cid][leaf],f'RC.disclosures.scaled_allowance.contrasts[{cid}].{leaf}',
                 hold='member phase durations for GAMMA are absent from the §0 files; original phase edges/spans remain outside this read')
    for row,pack in [(242,'BETA'),(243,'ALPHA'),(244,'GAMMA'),(490,'ALPHA'),(491,'BETA'),(492,'GAMMA')]:
        x=next(x for x in d['DISC']['window_lines'][pack.lower()] if x['label']=='physics_counts')
        bind(row,x['counts']['contention.request_overlap'],f'DISC.window_lines.{pack.lower()}[label=physics_counts].counts.contention.request_overlap',f'flags.{pack}.contention')
    for row in (250,251):
        bind(row,sum(x['status']=='agrees' and not x['differing_keys'] for x in rc['exclusions_rederivation'].values()),
             'count(RC.exclusions_rederivation[*][status=agrees,differing_keys=[]])')
    for row,(model,phase) in zip(range(276,280),[('Qwen3-1.7B-4bit','decode'),('Qwen3-1.7B-4bit','prefill'),('Qwen3-8B-4bit','decode'),('Qwen3-8B-4bit','prefill')]):
        bind(row,rc['dominance']['common_mode'][model+'/'+phase]['R_cm'],f'RC.dominance.common_mode[{model}/{phase}].R_cm',f'floor.{model}/{phase}/comparative.R_cm')
    points=[v['guarded_floor_j'] for c in fill for forms in c['claim_evaluation']['floor_limit']['point_floor_diagnostics'].values() for v in forms.values()]
    pubs=[x['floor_gate_j'] for c in fill for x in c['floor']['arm_gates']]
    for row,value in [(284,min(points)),(285,max(points)),(286,min(pubs)),(287,max(pubs))]:
        bind(row,value,'range(FILL.gamma.contrasts[*].claim_evaluation.floor_limit.point_floor_diagnostics[*].absolute.guarded_floor_j)' if row<286 else 'range(FILL.gamma.contrasts[*].floor.arm_gates[*].floor_gate_j)')
    for row,phase in [(288,'decode'),(291,'prefill')]:
        key='Qwen3-8B-4bit/'+phase+'/absolute'; f=rc['floors'][key]
        bind(row,f['guarded_floor_j'],f'RC.floors[{key}].guarded_floor_j',f'floor.{key}.guarded')
        bind(row+1,f['allowance_j'],f'RC.floors[{key}].allowance_j')
        bind(row+2,f['drift_widened_guarded_floor_j'],f'RC.floors[{key}].drift_widened_guarded_floor_j',f'floor.{key}.minted')
    for row in (294,295):
        bind(row,len(d['CMP']['limit_undetermined']),'len(CMP.limit_undetermined)')
    ver=d['VER']; cmp=d['CMP']
    metadata={297:(ver['stages']['digests']['outputs_verified'],'VER.stages.digests.outputs_verified'),
              298:(ver['stages']['digests']['input_census_verified'],'VER.stages.digests.input_census_verified'),
              299:(rc['comparison']['summary']['compared_runs'],'RC.comparison.summary.compared_runs'),
              300:(rc['comparison']['summary']['not_compared_runs'],'RC.comparison.summary.not_compared_runs'),
              301:(ver['stages']['recompute']['exit'],'VER.stages.recompute.exit'),
              302:(ver['stages']['recompute']['workers'],'VER.stages.recompute.workers'),
              303:(sum(x['verdict']!='AGREE' for x in cmp['comparisons']),'count(CMP.comparisons[verdict != AGREE])'),
              304:(len(cmp['coverage']['unmapped']),'len(CMP.coverage.unmapped)'),
              305:(11,'RESULTS §4.3: step-11 is a locator, not an evidence count (phase-1 token-inventory correction)'),
              306:(len(cmp['coverage']['nonfinite']),'len(CMP.coverage.nonfinite)'),
              307:(len(cmp['coverage']['absent_sources']),'len(CMP.coverage.absent_sources)'),
              308:(len(cmp['limit_undetermined']),'len(CMP.limit_undetermined)'),
              309:(len(cmp['structure_flags']),'len(CMP.structure_flags)'),
              327:(len(cmp['counts']),'len(CMP.counts)'),
              328:(sum(v>0 for v in counts.values()),'count(nonempty CMP comparison families)'),
              329:(counts['window_edge_s'],'count(CMP.comparisons[family=window_edge_s])'),
              330:(cmp['counts']['window_edge_s']['pass'],'CMP.counts.window_edge_s.pass'),
              331:(cmp['counts']['window_edge_s']['fail'],'CMP.counts.window_edge_s.fail'),
              332:(len(cmp['coverage']['uncovered_numeric']),'len(CMP.coverage.uncovered_numeric)')}
    for row,(v,k) in metadata.items():bind(row,v,k)
    for row,family in zip(range(310,322),['contrast_j','contrast_p','floor_gate_j','floor_j','kept_units','outcome_word','holm_order','per_token_j','descriptive_ratio','reported_cell_j','run_phase_energy_j','exclusions_rederivation']):
        bind(row,counts[family],f'count(CMP.comparisons[family={family}])')
    for row,family in [(322,'contrast_j'),(323,'floor_gate_j'),(324,'run_phase_energy_j'),(325,'per_token_j'),(326,'contrast_p'),(335,'contrast_p')]:
        bind(row,max(abs(x['difference']) for x in cmp['comparisons'] if x['family']==family and 'difference' in x),f'max(abs(CMP.comparisons[family={family}].difference))')
    for row,cid,leaf in [(333,cids[1],'p'),(334,cids[0],'holm_p')]:
        bind(row,10.0**math.floor(math.log10(rc['contrasts'][cid][leaf])),f'10**floor(log10(RC.contrasts[{cid}].{leaf})); RESULTS orders-of-magnitude wording (raw and adjusted p range)')
    battery=next(x for x in d['DISC']['contrasts'] if x['label']=='battery_assist_contrast')
    bind(341,battery['assist_quads'],'DISC.contrasts[label=battery_assist_contrast].assist_quads',
         hold='raw per-member battery.assist flags / fallback qualification not present in §0 sources; activity diagnostics alone do not establish the flag')
    arm=next(x for x in d['DISC']['window_lines']['gamma'] if x['label']=='arm_hazards' and x['module']=='battery' and x['phase']=='instant')
    bind(342,arm['measurements']['amperage_ma'],'DISC.window_lines.gamma[label=arm_hazards,module=battery,phase=instant].measurements.amperage_ma',
         hold='the disclosure carries the arm reading, but no independent arm receipt/current observation in §0 files')
    monitor=next(x for x in d['DISC']['window_lines']['gamma'] if x['label']=='monitor_cost')
    for row,leaf in [(348,'cpu_s'),(349,'reader_cpu_s'),(350,'probes_inside_target_phases')]:
        bind(row,monitor[leaf],f'DISC.window_lines.gamma[label=monitor_cost].{leaf}',hold='monitor cumulative CPU endpoints and probe timestamps/phase overlaps are not present in §0 sources')
    models=['Qwen3-1.7B-4bit','Qwen3-8B-4bit','Qwen2.5-1.5B-Instruct-4bit']
    for i,model in enumerate(models):
        x=next(x for x in d['DISC']['window_lines']['gamma'] if x['label']=='machine_summary' and x['model']==(['qwen3-1p7b','qwen3-8b','Qwen2.5-1.5B-Instruct-4bit'][i]))
        for j,leaf in enumerate(('median','minimum','maximum') if i<2 else ('median',)):
            bind(351+i*3+j,x[leaf],f'DISC.window_lines.gamma[label=machine_summary,model={x["model"]}].{leaf}',f'request.{model}.{leaf}')
    requests=rc['disclosures']['whole_machine']['windows']['GAMMA']['members']
    invalid=0
    for x in requests.values():
        y=x['phases']['request']; machine=y['meter']['delta_J']+y['battery']['delta_J']
        invalid+= not (0<y['rail_delta_J']/machine<=1 and machine-y['rail_delta_J']>=0)
    bind(358,invalid,'count(RC.disclosures.whole_machine.windows.GAMMA.members[*].phases.request outside hard band)')
    bind(359,len(requests),'len(RC.disclosures.whole_machine.windows.GAMMA.members)')
    for cellid,rows,pack in [(cellids[0],[360,361,362,363],'ALPHA'),(cellids[2],[365,366,367,368],'BETA'),(cellids[1],[370,371],'ALPHA'),(cellids[3],[373,374],'BETA')]:
        x=rc['disclosures']['whole_machine']['windows'][pack]['cells'][cellid]
        values=[x['mean_j'],x['h_j'],x['edge_shift_sensitivity']['max_abs_change_j'],x['gross_share']['median']] if len(rows)==4 else [x['mean_j'],x['gross_share']['median']]
        leaves=['mean_j','h_j','edge_shift_sensitivity.max_abs_change_j','gross_share.median'] if len(rows)==4 else ['mean_j','gross_share.median']
        hands=['mean','h',None,'share'] if len(rows)==4 else ['mean','share']
        for row,value,leaf,hand in zip(rows,values,leaves,hands):
            bind(row,value,f'RC.disclosures.whole_machine.windows.{pack}.cells[{cellid}].{leaf}',f'machine.{cellid}.{hand}' if hand else None,
                 hold=None if hand else 'only aggregate shifted-corner means are retained; per-member shifted meter energies/raw stream are not in §0 files')
    for i,cid in enumerate(cids):
        x=rc['disclosures']['load_sensitivity'][cid]
        for row,leaf,hand in [(376+i*5,'dbar_j','mean'),(377+i*5,'metrology_interval_j[0]','lower'),(378+i*5,'metrology_interval_j[1]','upper'),(379+i*5,'n','n')]:
            value=x['metrology_interval_j'][int(leaf[-2])] if '[' in leaf else x[leaf]
            bind(row,value,f'RC.disclosures.load_sensitivity[{cid}].{leaf}',f'load.{cid}.{hand}')
        for row,leaf in [(388+i*4,'D_j'),(389+i*4,'decision_interval_j[0]'),(390+i*4,'decision_interval_j[1]'),(391+i*4,'floor_gate_j')]:
            value=scaled[cid]['decision_interval_j'][int(leaf[-2])] if '[' in leaf else scaled[cid][leaf]
            bind(row,value,f'RC.disclosures.scaled_allowance.contrasts[{cid}].{leaf}',
                 hold='independent scaling factor requires member-level phase durations/reference durations, absent in §0 sources; stored aggregate factors are insufficient')
    included=[x for x in d['CV']['bundle_audit'] if x['inclusion_status']=='included']
    assert len({x['token_provenance']['output_tokens'] for x in included})==1
    bind(396,included[0]['token_provenance']['output_tokens'],'CV.bundle_audit[inclusion_status=included].token_provenance.output_tokens (all 44 rows)')
    bind(496,calc[f'request.{models[0]}.median'],'RC.disclosures.whole_machine.windows.GAMMA.members[*].phases.request; both model medians round to 36%',f'request.{models[0]}.median')
    bind(497,calc[f'machine.{cellids[0]}.share'],'RC.disclosures.whole_machine.windows.{ALPHA,BETA}.members[*].phases.decode; both model medians round to 34%',f'machine.{cellids[0]}.share')
    bind(498,calc[f'machine.{cellids[1]}.share'],'RC.disclosures.whole_machine.windows.{ALPHA,BETA}.members[*].phases.prefill; both model medians round to 45%',f'machine.{cellids[1]}.share')
    key='Qwen3-1.7B-4bit/prefill'
    bind(502,rc['dominance']['common_mode'][key]['R_cm'],f'RC.dominance.common_mode[{key}].R_cm',f'floor.{key}/comparative.R_cm')
    bind(521,calc[f'request.{models[2]}.median'],f'RC.disclosures.whole_machine.windows.GAMMA.members[model={models[2]}].phases.request',f'request.{models[2]}.median')
    # RL-42: DLE-5 counts distinct paths, with all list indices collapsed.
    normalized_paths, scalar_instances = dle5_leaf_counts(fill)
    if (normalized_paths, scalar_instances) != (84, 118):
        raise ValueError(f'STOP: DLE-5 count differs: {(normalized_paths, scalar_instances)}')
    bind(522,normalized_paths,'count distinct normalized paths in FILL.gamma.contrasts[*] DLE-5 three groups; 84 normalized leaf paths; 118 scalar leaves')
    bind(525,'none' if not d['CV']['sampling_audit']['top_up_detected'] else 'detected','CV.sampling_audit.top_up_detected',hold='complete run/config inventory needed to establish absence of unregistered top-ups is outside §0 outputs')
    bind(526,'none' if not d['CV']['sampling_audit']['valid_replacements'] else 'present','CV.sampling_audit.valid_replacements',hold='complete run/config inventory needed to establish absence of replacements is outside §0 outputs')
    failures=sum(x['stored_verdict']['status']=='failed' for x in d['STEP']['windows'].values())
    bind(527,{3:'three'}.get(failures,str(failures)),'count(STEP.windows[*].stored_verdict.status == failed)')
    clean=sum(x['clean'] for x in rc['disclosures']['whole_machine']['request_cross_check']['windows'].values())
    bind(528,clean,'count(RC.disclosures.whole_machine.request_cross_check.windows[*].clean)',hold='raw meter window flags / cleanliness inputs are outside §0 outputs; count of stored clean booleans is sourcing only')
    sens=d['SENS']['contrasts']
    bind(529,'clean' if all(x['outcome_equals_primary'] and x['bound_independent_values_equal_primary'] for x in sens) else 'changed','SENS.contrasts[*].{outcome_equals_primary,bound_independent_values_equal_primary}',
         hold='independent Erratum-3 bound/floor eligibility requires full ledger/acceptance and shared-edge replay inputs outside §0 files')
    for i in range(2):
        for j,leaf in enumerate(('outcome','direction','claim_level_ceiling')):
            bind(530+i*3+j,fill[i]['claim_evaluation'][leaf],f'FILL.gamma.contrasts[{i}].claim_evaluation.{leaf}',
                 hold='numeric direction checks agree; full selection/manifest/current/transport/eligibility inputs needed for an independent ceiling are outside §0 outputs')
    return bindings


def family_checks(d, repo):
    """Counts and equality checks only; never serialize stage/member readings."""
    path=repo/'configs/analysis/b5/analysed_windows.json'
    raw=path.read_bytes()
    index_hash=hashlib.sha256(raw).hexdigest()
    if index_hash != d['REC']['window_index_sha256']:
        raise ValueError('committed attempt index disagrees with REC hash pin')
    index=json.loads(raw)
    selected=next(x for x in index['attempts'] if x['pack']=='gamma' and x['seal']=='second')
    assert selected['plan_id']==d['EXC']['plan_id']
    history=[x for x in d['DISC']['block_lines'] if x['label']=='attempt_history']
    history_diff=0
    for x in index['attempts']:
        y=next(y for y in history if y['plan_id']==x['plan_id'])
        history_diff += x['cause_key']!=y['cause_key'] or x['attempt']!=y['attempt']
    temperature_rows=[x for window in d['DISC']['window_lines'].values() for x in window if x['label']=='battery_temperature']
    temperature_diff=0
    for x in temperature_rows:
        readings=[v for v in x['readings_centi_c'] if v is not None]
        rise=(readings[-1]-readings[0])/100 if len(readings)>=2 else None
        plateau=len(readings)>=3 and max(readings[-3:])-min(readings[-3:])<=50
        flag=rise is not None and rise>3 and not plateau
        same_rise=(rise is None and x['rise_k'] is None) or (rise is not None and x['rise_k'] is not None and abs(rise-x['rise_k'])<1e-12)
        temperature_diff += not (same_rise and plateau==x['plateau'] and flag==x['producer_flag'] and (not readings)==x['temperature_unmeasured'])
    # These counts independently check the recorded retained-ID lists. They do
    # not re-detect contamination or replay the unsealed-external NEG-8 screen.
    neg8=d['RC']['windows']['GAMMA']['neg8']
    counts={'index_attempts':len(index['attempts']),
            'history_disagreements':history_diff,
            'temperature_stages':len(temperature_rows),
            'temperature_arithmetic_disagreements':temperature_diff,
            'gamma_retained_references':len(neg8['survivor_ids']),
            'gamma_retained_corpus':len(neg8['corpus_ids']),
            'included_gamma_token_records':sum(x['inclusion_status']=='included' for x in d['CV']['bundle_audit'])}
    return {'attempt_index_sha256':index_hash,'counts':counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect', nargs='*', choices=SOURCES)
    parser.add_argument('--write', action='store_true', help='write aggregate-only TSVs beside this script')
    parser.add_argument('--repo-only', action='store_true',
                        help='apply rulings/rounding from committed tables; no custody access; default checks byte equality')
    args = parser.parse_args()
    if args.repo_only:
        if args.inspect is not None:
            parser.error('--repo-only cannot be combined with --inspect')
        repository_tables(write=args.write)
        return
    reader = CustodyReader()
    try:
        if args.inspect is not None:
            for alias in args.inspect:
                print(alias, json.dumps(shape(reader.read(alias),0), sort_keys=True))
            return
        d={'REC':reader.read('REC')}
        d.update({alias:reader.read(alias) for alias in SOURCES if alias!='REC'})
        # Complete projection pins are also present in the already hash-bound
        # REC step rows; do not follow any of their output path strings.
        output_pins={x['sha256'] for step in d['REC']['steps'] for x in step['outputs']}
        for alias in ('PROJ-A','PROJ-B'):
            assert reader.opened[alias]['sha256_before'] in output_pins
        calc, locators=hand_calculations(d)
        for pack in ('ALPHA','BETA','GAMMA'):
            key=f'flags.{pack}.contention'
            calc[key]=sum('contention.request_overlap' in x['codes'] for x in d['RC']['exclusions_rederivation'][pack]['rederived']['members_excluded'])
            locators[key]=(f'RC.exclusions_rederivation.{pack}.rederived.members_excluded[*].codes',
                           'count stored member code occurrences; no raw hazard re-detection')
        bindings=source_bindings(d,calc)
        repo=Path(__file__).absolute().parents[3]
        families=family_checks(d,repo)
        source=subprocess.run(['git','show',f'{BASE}:docs/analysis/b5/rederivation.tsv'],cwd=repo,
                              check=True,capture_output=True,text=True).stdout
        rows=list(csv.DictReader(io.StringIO(source),delimiter='\t'))
        assert len(rows)==538
        stopped=[i for i,x in enumerate(rows,2) if x['rederived_value']=='UNAVAILABLE']
        missing=set(stopped)-set(bindings)
        if missing:
            raise ValueError(f'unmapped phase-1 stops: {sorted(missing)}')
        assert hashlib.sha256((repo/'docs/analysis/b5/RESULTS.md').read_bytes()).hexdigest()==RESULTS_SHA256
        hand_rows=[]
        for rowno,x in enumerate(rows,2):
            x.update(phase1_match=x['match'],source_value='',source_match='',difference='',hand_check='not-required / phase-1 scope')
            if rowno not in bindings:
                continue
            b=bindings[rowno]
            sourced,source_diff,source_match=printed_compare(x['printed_value'],b['value'])
            x.update(source_value=sourced,source_match=source_match,difference=source_diff,
                     rederived_value=sourced,match=source_match)
            aliases=[a for a in SOURCES if re.search(r'(?<![\w-])'+re.escape(a)+r'\.',b['key'])]
            x['source']='; '.join(f'{a} sha256={reader.opened[a]["sha256_before"]}' for a in aliases)
            if not x['source']:
                x['source']='RESULTS frozen text / committed definition'
            x['note']='SOURCED: '+b['key']+'; source difference='+source_diff
            if b['hand']:
                key=b['hand'];v=calc[key]
                rendered,diff,status=printed_compare(x['printed_value'],v)
                src,formula=locators[key]
                x.update(rederived_value=rendered,difference=diff,hand_check=key,
                         match='MISMATCH' if source_match=='MISMATCH' or status=='MISMATCH' else status)
                x['note']+='; HAND: '+src+'; '+formula
                hand_rows.append(dict(ledger_row=rowno,printed_value=x['printed_value'],key=key,
                                      source=src,formula=formula,rederived_value=rendered,difference=diff,match=status))
            elif b['hold']:
                x.update(match='MISMATCH' if source_match=='MISMATCH' else 'source-outside-unseal',hand_check='source-outside-unseal')
                x['note']+='; HAND NOT DONE: '+b['hold']
            else:
                x['hand_check']='source check / count; no additional member arithmetic required'
        # Phase 1's one factual mismatch: source the four stage-opening losses
        # from the indexed GAMMA attempt's authenticated exclusion record.
        starts=[]
        for cell in d['EXC']['cells']:
            for number in ('b01','b06'):
                unit=next(x for x in cell['dropped_units'] if x['unit_id'].endswith(number))
                codes=set(unit['codes'])
                cause='contention' if 'contention.request_overlap' in codes else 'anchor failure' if 'member.anchor_not_bounded' in codes else 'admission abort' if 'member.admission_aborted' in codes else 'unknown'
                starts.append(cause)
        assert Counter(starts)==Counter({'contention':2,'anchor failure':1,'admission abort':1})
        for x in rows:
            if x['phase1_match']=='MISMATCH' and x['source_match']=='':
                assert 'different' in x['printed_value'] or 'cause' in x['key/leaf']
                x.update(rederived_value='3 distinct causes in 4 losses',source_value='3 distinct causes in 4 losses',source_match='MISMATCH',difference='-1 distinct cause',hand_check='count(EXC stage-opening cause categories)')
                x['source']='EXC sha256='+reader.opened['EXC']['sha256_before']+'; configs/analysis/b5/analysed_windows.json (indexed second-seal GAMMA attempt)'
                x['note']='DISCREPANCY: indexed GAMMA EXC.cells[*].dropped_units[unit_id ends b01 or b06].codes: contention twice, anchor failure once, admission abort once; RL-39 erratum; RESULTS unchanged'
        apply_print_rulings(rows)
        round_differences(rows)
        round_differences(hand_rows)
        files=reader.finish()
        if args.write:
            dest=Path(__file__).absolute().parent
            fields=list(rows[0])
            with (dest/'rederivation.tsv').open('w',newline='') as f:
                w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
            with (dest/'hand_checks_phase2.tsv').open('w',newline='') as f:
                w=csv.DictWriter(f,list(hand_rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(hand_rows)
            with (dest/'phase2_sources.tsv').open('w',newline='') as f:
                w=csv.DictWriter(f,['alias','path','section0_pin','sha256_before','sha256_after'],delimiter='\t',lineterminator='\n');w.writeheader()
                for alias,record in files.items():w.writerow({'alias':alias,**record})
        print(json.dumps({'rows':len(rows),'stopped_rows_sourced':len(stopped),'counts':dict(Counter(x['match'] for x in rows)),
                          'source_counts':dict(Counter(x['source_match'] for x in rows if x['source_match'])),
                          'hand_rows':len(hand_rows),'files':len(files),
                          'families':families,
                          'mismatches':[{'row':i,'printed':x['printed_value'],'rederived':x['rederived_value'],'key':x['key/leaf']} for i,x in enumerate(rows,2) if x['match']=='MISMATCH'],
                          'outside':[i for i,x in enumerate(rows,2) if x['match']=='source-outside-unseal']},indent=2))
    finally:
        reader.finish()


if __name__ == '__main__':
    main()
