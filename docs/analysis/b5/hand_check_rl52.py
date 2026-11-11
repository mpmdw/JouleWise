#!/usr/bin/env python3
"""Independent, aggregate-only RL-52 checks from the pinned release recompute.

No analysis/recompute imports, raw-stream integration, path chasing or network.
Only RC is opened: the prompt's separate real-restricted-directory prohibition
needs a ruling before the dry-m disclosure/projection files can be accessed.
The phase-2 module supplies only its stdlib reader and arithmetic helpers.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import statistics as st
import subprocess

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[2]
BASE = '0b8763f0a8291bfa5d47fdc18aa64ef3aa33ec1b'
RC_HASH = 'c06ee7c8cbf85a68dcebc24a73e0372fd6f8d825fc3acf30ec352304dd93cacc'
spec = importlib.util.spec_from_file_location('rl52_phase2_helpers', HERE/'hand_check_phase2.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
LOAD_CODES = {'contention.request_overlap', 'thermal.os_level_nonzero',
              'thermal.powermetrics_pressure_elevated'}


class ReleasedReader(h.CustodyReader):
    """This partial pass cannot open any dry-m or restricted descendant."""
    @staticmethod
    def checked_path(root, relative):
        if root != h.ROOT_B or relative != 'recompute.json':
            raise ValueError('RL-52 partial pass permits only RC; access ruling pending')
        return h.CustodyReader.checked_path(root, relative)

    def read(self, alias):
        if alias != 'RC':
            raise ValueError('RL-52 partial pass permits only RC; access ruling pending')
        if h.SOURCES.get('RC') != (h.ROOT_B, 'recompute.json', RC_HASH):
            raise ValueError('RC pin configuration changed')
        return super().read(alias)


def base_bytes():
    return subprocess.run(['git', 'show', f'{BASE}:docs/analysis/b5/rederivation.tsv'],
                          cwd=REPO, check=True, capture_output=True).stdout


def display(value, digits=5):
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return 'none'
    return f'{value:.{digits}f}' if isinstance(value, float) else str(value)


class Ledger:
    def __init__(self, fields):
        self.fields = fields
        self.rows = []

    def add(self, key, source, actual, formula, digits=5, kind=None, note=''):
        printed = display(source, digits)
        value, difference, word = h.printed_compare(printed, actual)
        _, _, source_word = h.printed_compare(printed, source)
        if kind and word != 'MISMATCH':
            word = kind
        if kind == 'recorded-judgment':
            formula = 'stored judgment; not re-derived; ' + formula
        row = dict.fromkeys(self.fields, '')
        row.update(printed_value=printed, **{'key/leaf': key},
                   source=f'RC sha256={RC_HASH}', rederived_value=value,
                   match=word, source_value=printed, source_match=source_word,
                   difference=difference, hand_check=formula,
                   paper1='print-labelled' if kind in {'recorded-judgment', 'single-source'} else 'print',
                   note='RL-52; from the independent recomputation; disclosure-source cross-check pending access ruling. ' + note)
        self.rows.append(row)


def quad_ids(members, phase, unit):
    suffix = unit[-3:]
    ids = []
    for position in ('a1', 'b1', 'b2', 'a2'):
        matches = [k for k in members if f'-{phase}-' in k and k.endswith(f'-{suffix}-{position}')]
        if len(matches) != 1:
            raise ValueError('missing or ambiguous quad member')
        ids.append(matches[0])
    return ids


def cell_inputs(rc, cell):
    pack = 'ALPHA' if '1.7B' in cell['model'] else 'BETA'
    mm = rc['members'][pack]
    repeats = cell['kept_units']['repeat']
    quads = [quad_ids(mm, cell['phase'], u) for u in cell['kept_units']['quad']]
    return pack, mm, repeats, quads


def cell_arithmetic(rc, cell):
    pack, mm, repeats, quads = cell_inputs(rc, cell)
    phase = cell['phase']
    result = h.stratified([mm[u]['E_j'][phase] for u in repeats],
                         [st.fmean(mm[u]['E_j'][phase] for u in q) for q in quads])
    clock = .2*st.fmean(mm[u]['a_bop_j'][phase] for u in repeats) + .8*st.fmean(
        mm[u]['a_bop_j'][phase] for q in quads for u in q)
    kinds = [clock, 0.0, rc['windows'][pack]['neg8']['allowance_j']/2]
    result.update(kind_averages_j=kinds, B_j=math.fsum(kinds))
    result.update(lower_j=result['mean']-result['h']-result['B_j'],
                  upper_j=result['mean']+result['h']+result['B_j'])
    kept = [*repeats, *(u for q in quads for u in q)]
    result['attained_by'] = max(kept, key=lambda u: mm[u]['a_bop_j'][phase])
    result['minimum_j'] = min(mm[u]['a_bop_j'][phase] for u in kept)
    return result


def cross_arithmetic(rc, cell):
    floor = cell_arithmetic(rc, cell)
    phase = cell['phase']
    contrast = next(c for cid, c in rc['contrasts'].items() if ('-decode-' in cid) == (phase == 'decode'))
    mm = rc['members']['GAMMA']
    positions = (0, 3) if '1.7B' in cell['model'] else (1, 2)
    means = [st.fmean(mm[quad_ids(mm, phase, u)[i]]['E_j'][phase] for i in positions)
             for u in contrast['kept_quads']]
    # Registered reported-energy quantiles at full precision, not the paired
    # contrast engine's three-decimal t. See analysis plan §4 and §9.
    hg = h.t975(len(means)-1)*st.stdev(means)/math.sqrt(len(means))
    delta = st.fmean(means)-floor['mean']
    return dict(delta_j=delta, h_G_j=hg, h_F_j=floor['h'],
                agree=abs(delta) <= math.hypot(hg, floor['h']))


def percentile(values, proportion):
    xs = sorted(values)
    pos = (len(xs)-1)*proportion
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo]+(xs[hi]-xs[lo])*(pos-lo)


def restored_load_units(units):
    """Restore a unit only if every removal code is load-correlated."""
    return [u for u in units if u['codes'] and set(u['codes']) <= LOAD_CODES]


def append_rows(rc, fields):
    ledger = Ledger(fields)
    add = ledger.add
    # D-165: reconstruct operands before division, without cached decisions.
    independent_pass, common_pass = [], []
    for label, floor in rc['floors'].items():
        model, phase, form = label.split('/')
        pack = 'ALPHA' if '1.7B' in model else 'BETA'
        mm = rc['members'][pack]
        absolute = form == 'absolute'
        if absolute:
            vs = [mm[u]['E_j'][phase] for u in floor['kept_units']]
            widths = [mm[u]['a_bop_j'][phase] for u in floor['kept_units']]
        else:
            quads = [quad_ids(mm, phase, u) for u in floor['kept_units']]
            vs = [h.quad_difference([mm[u] for u in q], phase) for q in quads]
            local = [math.fsum(mm[u]['r_j'][phase] for u in q)/2 for q in quads]
            # Shared trace-sweep widths are pinned inputs. They cannot be
            # reconstructed from scalar member energies; no raw trace is read.
            shared = floor['shared_j']
            widths = [s+l for s, l in zip(shared, local)]
        point = h.point_floor(vs, absolute)
        corner = h.widened_floor(vs, widths, absolute)
        if point <= 0:
            raise ValueError('dominance denominator nonpositive; ruling needed')
        ratio = corner/point
        independent_pass.append(ratio >= 2)
        prefix = f'RC.dominance.ratios[{label}]'
        source = rc['dominance']['ratios'][label]
        formula = (f'RC.members.{pack}[*].{{E_j,a_bop_j,r_j}}.{phase}; '
                   f'RC.floors[{label}].{{kept_units,shared_j}}; '
                   'point=max(abs envelope, Student prediction); enumerate independent +/- width corners; R=corner/point')
        for key, actual, digits in [('R', ratio, 4), ('numerator_j', corner, 5),
                                    ('denominator_j', point, 5), ('n', len(vs), 0)]:
            add(prefix+'.'+key, source[key], actual, formula, digits)
        add(prefix+'.pass', source['pass'], ratio >= 2, formula)
        if not absolute:
            guard = 1 if len(vs) >= 10 else math.sqrt(9/(len(vs)-1))
            floor_j = guard*corner + rc['windows'][pack]['neg8']['allowance_j']
            add(f'RC.floor_cells[{model}/{phase}].floor_cmp_j',
                rc['floor_cells'][model+'/'+phase]['floor_cmp_j'], floor_j,
                formula+'; comparative floor=guard*corner+gross NEG8 allowance')
            cm = h.widened_floor(vs, local, False, common=shared)
            common_pass.append(cm/point >= 2)
            cmprefix = f'RC.dominance.common_mode[{model}/{phase}]'
            # Common-mode operand leaves also live on the floor object.
            cm_source = rc['dominance']['common_mode'][model+'/'+phase]
            for leaf, actual, digits in [('numerator_j', cm, 5), ('denominator_j', point, 5),
                                         ('n', len(vs), 0), ('R_cm', cm/point, 4), ('pass', cm/point >= 2, 0)]:
                add(cmprefix+'.'+leaf, cm_source[leaf], actual,
                    formula+'; one shared sign and independent local signs; common corner/point', digits)
    branch = 'A' if all(independent_pass) and all(common_pass) else 'B'
    add('RC.dominance.branch', rc['dominance']['branch'], branch,
        'A iff every eight R and every four comparative R_cm >=2; otherwise B; no denominator refusal')
    add('count(RC.dominance.ratios[*].pass=false)', sum(not x['pass'] for x in rc['dominance']['ratios'].values()),
        sum(not x for x in independent_pass), 'count independently recomputed R<2')
    add('RL52.dominance.failed_common_mode_n', len(rc['dominance']['failed']),
        sum(not x for x in common_pass), 'count independently recomputed comparative R_cm<2')

    for cid, cell in rc['reported_cells'].items():
        pack, mm, repeats, quads = cell_inputs(rc, cell)
        result = cell_arithmetic(rc, cell)
        prefix = f'RC.reported_cells[{cid}]'
        formula = (f'RC.members.{pack}[*].{{E_j,a_bop_j}}.{cell["phase"]}; '+prefix+'.kept_units; '
                   'fixed .2 repeat/.8 quad-member averages; interval-support interpolation=0; drift=gross allowance/2')
        for i, actual in enumerate(result['kind_averages_j']):
            add(prefix+f'.interval.kind_averages_j[{i}]', cell['interval']['kind_averages_j'][i], actual, formula)
        for key in ('attained_by', 'minimum_j'):
            add(prefix+'.attribution_floor.'+key, cell['attribution_floor'][key], result[key],
                formula+'; argmax and min of first-kind bounds over kept members')
        for removed in cell['removed_units']:
            records = [x for x in rc['exclusions_rederivation'][pack]['rederived']['members_excluded']
                       if x['run_id'] in removed['run_ids']]
            codes = sorted({c for x in records for c in x['codes']})
            add(prefix+f'.removed_units[unit_id={removed["unit_id"]}].codes',
                ','.join(sorted(removed['codes'])), ','.join(codes),
                f'RC.exclusions_rederivation.{pack}.rederived.members_excluded[*]; union stored codes by removed unit; over stored flags')
        add(prefix+'.removed_units.count', len(cell['removed_units']), len(cell['removed_units']),
            'count stored removed-unit records; over stored flags')

        # Battery flags are collection judgments. Membership is rebuilt from
        # the stored flag code, and all numeric lines are recalculated.
        assisted = {x['run_id'] for x in rc['exclusions_rederivation'][pack]['rederived']['members_excluded']
                    if 'battery.assist' in x['codes']}
        # RC retains the authoritative per-stratum counts, including assisted
        # runs which are disclosure-only and hence absent from excluded lists.
        battery = rc['disclosures']['battery_assist'][cid]
        for stratum, count in battery['assist_members_by_stratum'].items():
            add(f'RC.disclosures.battery_assist[{cid}].assist_members_by_stratum.{stratum}', count, count,
                'assist flags themselves not independently reconstructed from raw current; attribute collection record',
                kind='recorded-judgment')
        if assisted or any(battery['assist_members_by_stratum'].values()):
            raise ValueError('nonzero battery assist needs complete stored flags before selecting without-assist units')
        # Zero assist is an explicit recorded input, not inferred from an empty
        # exclusion list. Check membership as well as the resulting energies.
        for stratum in ('repeat', 'quad'):
            add(f'RC.disclosures.battery_assist[{cid}].kept_units.{stratum}.count',
                len(battery['kept_units'][stratum]), len(cell['kept_units'][stratum]),
                'without equals with given recorded zero assist; count retained stored unit ids')
        for leaf, actual in [('mean_j', result['mean']), ('lower_j', result['lower_j']), ('upper_j', result['upper_j'])]:
            add(f'RC.disclosures.battery_assist[{cid}].{leaf}', battery[leaf], actual, formula+'; no assisted members recorded')

        dropped = cell['removed_units']
        restore = restored_load_units(dropped)
        load = rc['disclosures']['load_sensitivity'].get(cid)
        load_removed = [x for x in dropped if set(x['codes']) & LOAD_CODES]
        add(prefix+'.removed_units.load_trigger_count', len(load_removed), len(load_removed),
            'count dropped units with any load code; over stored flags; zero means no such removal')
        changed = dict(cell, kept_units={k:list(v) for k,v in cell['kept_units'].items()})
        for unit in restore:
            changed['kept_units'][unit['stratum']].append(unit['unit_id'])
        changed_result = cell_arithmetic(rc, changed)
        if load is not None:
            for stratum, nkey in [('repeat', 'n_r'), ('quad', 'n_b')]:
                add(f'RC.disclosures.load_sensitivity[{cid}].{nkey}', load[nkey],
                    len(changed['kept_units'][stratum]), 'restore only units whose complete nonempty code set is load-only; count units; over stored flags')
            for leaf, actual in [('mean_j', changed_result['mean']), ('lower_j', changed_result['lower_j']), ('upper_j', changed_result['upper_j'])]:
                add(f'RC.disclosures.load_sensitivity[{cid}].{leaf}', load[leaf], actual,
                    formula+'; restore only load-only dropped units; preserve fixed .2/.8 weighting')
            add(f'RC.disclosures.load_sensitivity[{cid}].restored_count', load['restored_count'], len(restore),
                'count dropped units whose complete nonempty code set is load-only; over stored flags')

        cross = cross_arithmetic(rc, cell)
        crosskey = cell['model']+'/'+cell['phase']
        for leaf in ('delta_j', 'h_G_j', 'h_F_j', 'agree'):
            add(f'RC.disclosures.cross_window[{crosskey}].{leaf}', rc['disclosures']['cross_window'][crosskey][leaf], cross[leaf],
                formula+'; GAMMA arm mean and t*SD(quad-arm means)/sqrt(n); agree iff abs(delta)<=hypot(h_G,h_F)')
        # Check the previously hand-checked physical rows without changing them.
        rownum = {('ALPHA','decode'):169, ('ALPHA','prefill'):170,
                  ('BETA','prefill'):171, ('BETA','decode'):172}[(pack, cell['phase'])]
        old = list(csv.DictReader(io.StringIO(base_bytes().decode()), delimiter='\t'))[rownum-2]
        if h.printed_compare(old['printed_value'], cross['delta_j'])[2] == 'MISMATCH':
            raise ValueError(f'cross delta disagrees with frozen ledger row {rownum}')

    for phase in ('decode', 'prefill'):
        cid = next(k for k in rc['contrasts'] if ('-decode-' in k) == (phase == 'decode'))
        removed = rc['exclusions_rederivation']['GAMMA']['rederived']['cells']
        # Contrast IDs in the exclusion record are the registered ids.
        exc = next(x for x in removed if x['cell_id'] == cid)
        members = rc['exclusions_rederivation']['GAMMA']['rederived']['members_excluded']
        for unit in exc['dropped_units']:
            ids = set(quad_ids(rc['members']['GAMMA'], phase, unit['unit_id']))
            codes = sorted({c for x in members if x['run_id'] in ids for c in x['codes']})
            add(f'RC.exclusions_rederivation.GAMMA.rederived.cells[cell_id={cid}].dropped_units[unit_id={unit["unit_id"]}].codes',
                ','.join(sorted(unit['codes'])), ','.join(codes),
                'union member code sets over this quad; over stored flags; no raw hazard re-detection')

    for pack in ('ALPHA', 'BETA', 'GAMMA'):
        wm = rc['disclosures']['whole_machine']['windows'][pack]['members']
        cross = rc['disclosures']['whole_machine']['request_cross_check']['windows'][pack]['models']
        for model in sorted({v['model'] for v in wm.values()}):
            rows = [v['phases']['request'] for v in wm.values() if v['model'] == model]
            ratios = [x['rail_delta_J']/(x['meter']['delta_J']+x['battery']['delta_J']) for x in rows]
            source = cross[model]
            # Available source keys are checked explicitly; no value-based leaf search.
            for leaf, value in [('rho_median', st.median(ratios)), ('rho_min', min(ratios)), ('rho_max', max(ratios)),
                                 ('rho_iqr[0]', percentile(ratios,.25)), ('rho_iqr[1]', percentile(ratios,.75))]:
                stored = source['rho_iqr'][int(leaf[-2])] if leaf.startswith('rho_iqr') else source[leaf]
                add(f'RC.disclosures.whole_machine.request_cross_check.windows.{pack}.models[{model}].{leaf}', stored, value,
                    f'RC.disclosures.whole_machine.windows.{pack}.members[model={model}].phases.request; rho=rail/(meter+battery); linear interpolated quantiles', 4)
            plausible = [x for x in rows if 0 < x['rail_delta_J']/(x['meter']['delta_J']+x['battery']['delta_J']) <= 1
                         and x['meter']['delta_J']+x['battery']['delta_J']-x['rail_delta_J'] >= 0]
            ps = [x['rail_delta_J']/(x['meter']['delta_J']+x['battery']['delta_J']) for x in plausible]
            spread = (max(ps)-min(ps))/st.median(ps)
            for leaf, stored, actual in [('within_model_spread', source['within_model_spread'], spread),
                                         ('n_members', source['n_members'], len(rows)),
                                         ('outside_hard_band.count', len(source['outside_hard_band']), len(rows)-len(ps)),
                                         ('consistency', source['consistency'], 'consistent' if spread <= .2 else 'not_consistent')]:
                add(f'RC.disclosures.whole_machine.request_cross_check.windows.{pack}.models[{model}].{leaf}', stored, actual,
                    'rho=rail/(meter+battery); hard band 0<rho<=1 and machine>=rail; plausible spread=(max-min)/median <=.2', 4)

    # Gross-family NEG-8 arithmetic only; idle-subtracted records and loss
    # histories require the unopened pinned disclosure, and remain blocked.
    for pack in ('ALPHA', 'BETA'):
        ng = rc['windows'][pack]['neg8']
        mm = rc['members'][pack]
        corpus = sorted(mm[u]['E_j']['request'] for u in ng['corpus_ids'])
        refs = {slot:[u for u in ng['survivor_ids'] if f'-{slot}' in u]
                for slot in ('start', 'end', 'midpoint')}
        ns, ne = len(refs['start']), len(refs['end'])
        envelope = max(st.fmean(corpus[-ns:])-st.fmean(corpus[:ne]),
                       st.fmean(corpus[-ne:])-st.fmean(corpus[:ns]))
        prediction = round(h.t975(len(corpus)-1),3)*st.stdev(corpus)*math.sqrt(1/ns+1/ne)
        means = [st.fmean(mm[u]['E_j']['request'] for u in refs[slot])
                 for slot in ('start', 'end', 'midpoint') if refs[slot]]
        spread = max(means)-min(means)
        bound = max(envelope, prediction)
        for leaf, actual in [('corpus_n',len(corpus)), ('n_start',ns), ('n_mid',len(refs['midpoint'])),
                              ('n_end',ne), ('bound_envelope_j',envelope), ('bound_prediction_j',prediction),
                              ('bound_j',bound), ('spread_j',spread), ('allowance_j',max(spread,bound))]:
            add(f'RC.windows.{pack}.neg8.{leaf}', ng[leaf], actual,
                f'RC.members.{pack}[*].E_j.request; RC.windows.{pack}.neg8.{{corpus_ids,survivor_ids}}; '
                'registration §0.12: max(U_ns-L_ne,U_ne-L_ns,t*sampleSD*sqrt(1/ns+1/ne)); allowance=max(bound,spread)',
                note='gross family only; does not independently establish the idle-subtracted family verdict')
    return ledger.rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    original = base_bytes()
    current = (HERE/'rederivation.tsv').read_bytes()
    if not current.startswith(original):
        raise ValueError('original 538 rows changed; refuse')
    fields = next(csv.reader(io.StringIO(original.decode()), delimiter='\t'))
    reader = ReleasedReader()
    try:
        rc = reader.read('RC')
        rows = append_rows(rc, fields)
    finally:
        opened = reader.finish()
        print(json.dumps({'opened_custody': opened}, sort_keys=True))
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fields, delimiter='\t', lineterminator='\n')
    writer.writerows(rows)
    result = original+buffer.getvalue().encode()
    if args.write:
        if current not in (original, result):
            raise ValueError('different extension already present; refuse overwrite')
        (HERE/'rederivation.tsv').write_bytes(result)
    elif current != result:
        raise ValueError('extension differs; use --write only for initial append')
    print(json.dumps({'new_rows':len(rows), 'counts':dict(Counter(r['match'] for r in rows)),
                      'original_prefix_byte_identical':True, 'results_sha256':hashlib.sha256((HERE/'RESULTS.md').read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == '__main__':
    main()
