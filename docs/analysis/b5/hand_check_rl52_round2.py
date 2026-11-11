#!/usr/bin/env python3
"""RL-52 round 2: independent stdlib checks, aggregate-only serialization.

Requires the round-2 authority for exact hash-pinned descendants of the two
RL-38 roots. No analysis/recompute imports, directory inventories, reference
path following, raw-stream integration, custody writes or network.
Use --repo-only to check the frozen full ledger without opening custody.
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
ROUND1 = 'b9ea4cd111be1c6faae4f4a990ed1b1121e711da'
ROUND2 = '87a698c0f90aec5c037ed38ced586855be1bdbfa'
spec = importlib.util.spec_from_file_location('rl52_round1_helpers', HERE/'hand_check_rl52.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
h = e.h
ALIASES = ('RC', 'FILL', 'DISC', 'EXC', 'PROJ-A', 'PROJ-B')


class ReleasedReader:
    """Only the six exact files pinned by §0 / seat-4 phase-2's manifest."""
    def __init__(self):
        with (HERE/'phase2_sources.tsv').open() as stream:
            manifest = {r['alias']: r for r in csv.DictReader(stream, delimiter='\t')}
        self.sources = {}
        for alias in ALIASES:
            root, relative, prefix = h.SOURCES[alias]
            row = manifest[alias]
            pin = row['sha256_before']
            if (len(pin) != 64 or pin != row['sha256_after'] or
                    not pin.startswith(prefix) or row['path'] != str(root/relative) or
                    (len(prefix) < 64 and Path(relative).name[:64] != pin)):
                raise ValueError('phase-2 pin configuration changed')
            self.sources[alias] = (root, relative, pin)
        self.opened = {}

    def read(self, alias):
        if alias not in self.sources:
            raise ValueError('not an authorized pinned round-2 source')
        root, relative, pin = self.sources[alias]
        p = h.CustodyReader.checked_path(root, relative)
        raw = p.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        self.opened[alias] = dict(path=str(p), expected_sha256=pin, sha256_before=digest)
        if digest != pin:
            raise ValueError(f'{alias}: hash mismatch before parsing')
        return json.loads(raw)

    def finish(self):
        for alias, row in self.opened.items():
            root, relative, _ = self.sources[alias]
            p = h.CustodyReader.checked_path(root, relative)
            with p.open('rb') as stream:
                row['sha256_after'] = hashlib.file_digest(stream, 'sha256').hexdigest()
            if row['sha256_before'] != row['sha256_after']:
                raise ValueError(f'{alias}: custody changed during read')
        return self.opened


def frozen_bytes():
    return subprocess.run(['git', 'show', f'{ROUND1}:docs/analysis/b5/rederivation.tsv'],
                          cwd=REPO, check=True, capture_output=True).stdout


class Ledger:
    def __init__(self, fields, sources):
        self.fields, self.sources, self.rows = fields, sources, []

    def add(self, key, source, actual, formula, *, alias='DISC', digits=5,
            kind=None, note=''):
        printed = e.display(source, digits)
        value, difference, word = h.printed_compare(printed, actual)
        if kind and word != 'MISMATCH':
            word = kind
        row = dict.fromkeys(self.fields, '')
        pins = {alias, 'RC'} if 'RC.' in formula else {alias}
        row.update(printed_value=printed, **{'key/leaf': key},
                   source='; '.join(f'{a} sha256={self.sources[a][2]}' for a in sorted(pins)),
                   rederived_value=value, match=word, source_value=printed,
                   source_match=h.printed_compare(printed, source)[2],
                   difference=difference, hand_check=formula,
                   paper1='print-labelled' if kind in ('recorded-judgment', 'single-source') else 'print',
                   note='RL-52 round 2; '+note)
        self.rows.append(row)


def one(rows, **keys):
    matches = [x for x in rows if all(x.get(k) == v for k, v in keys.items())]
    if len(matches) != 1:
        raise ValueError(f'missing or ambiguous source selector: {keys}')
    return matches[0]


def code_string(codes):
    return ','.join(sorted({x['code'] if isinstance(x, dict) else x for x in codes}))


def floor_arithmetic(rc, label):
    model, phase, form = label.split('/')
    pack = 'ALPHA' if '1.7B' in model else 'BETA'
    floor, mm = rc['floors'][label], rc['members'][pack]
    absolute = form == 'absolute'
    if absolute:
        values = [mm[u]['E_j'][phase] for u in floor['kept_units']]
        local = [mm[u]['a_bop_j'][phase] for u in floor['kept_units']]
        widths = local
    else:
        quads = [e.quad_ids(mm, phase, u) for u in floor['kept_units']]
        values = [h.quad_difference([mm[u] for u in q], phase) for q in quads]
        local = [math.fsum(mm[u]['r_j'][phase] for u in q)/2 for q in quads]
        widths = [s+l for s, l in zip(floor['shared_j'], local)]
    point = h.point_floor(values, absolute)
    if point <= 0:
        raise ValueError('nonpositive dominance denominator')
    corner = h.widened_floor(values, widths, absolute)
    guard = 1 if len(values) >= 10 else math.sqrt(9/(len(values)-1))
    result = dict(n=len(values), numerator_j=corner, denominator_j=point,
                  ratio=corner/point, minted_j=guard*corner+rc['windows'][pack]['neg8']['allowance_j'])
    if not absolute:
        result['cm_numerator_j'] = h.widened_floor(values, local, False, common=floor['shared_j'])
    return result


def neg8_arithmetic(energies, corpus_ids, survivor_ids):
    corpus = sorted(energies[u] for u in corpus_ids)
    slots = {slot: [u for u in survivor_ids if f'-{slot}' in u]
             for slot in ('start', 'midpoint', 'end')}
    ns, ne = len(slots['start']), len(slots['end'])
    if not (2 <= ns <= 3 and 2 <= ne <= 3 and len(slots['midpoint']) <= 1):
        raise ValueError('reference roster outside registered survivor shape')
    envelope = max(st.fmean(corpus[-ns:])-st.fmean(corpus[:ne]),
                   st.fmean(corpus[-ne:])-st.fmean(corpus[:ns]))
    prediction = round(h.t975(len(corpus)-1), 3)*st.stdev(corpus)*math.sqrt(1/ns+1/ne)
    means = {slot: st.fmean(energies[u] for u in ids) for slot, ids in slots.items() if ids}
    bound = max(envelope, prediction)
    statistic = abs(means['end']-means['start'])
    spread = max(means.values())-min(means.values())
    return dict(bound_envelope_j=envelope, bound_prediction_j=prediction,
                derived_repeatability_bound_j=bound, screen_statistic_j=statistic,
                trajectory_excursion_max_j=spread, drift_allowance_j=max(bound, spread),
                decision='passed' if statistic <= bound else 'failed')


def temperature_arithmetic(readings):
    values = [v for v in readings if v is not None]
    rise = (values[-1]-values[0])/100 if len(values) >= 2 else None
    plateau = len(values) >= 3 and max(values[-3:])-min(values[-3:]) <= 50
    return dict(rise_k=rise, plateau=plateau,
                producer_flag=rise is not None and rise > 3 and not plateau,
                temperature_unmeasured=not values)


def rho_arithmetic(members, model):
    rows = [v['phases']['request'] for v in members.values() if v['model'] == model]
    ratios = [x['rail_delta_J']/(x['meter']['delta_J']+x['battery']['delta_J']) for x in rows]
    plausible = [ratio for row, ratio in zip(rows, ratios) if 0 < ratio <= 1 and
                 row['meter']['delta_J']+row['battery']['delta_J']-row['rail_delta_J'] >= 0]
    return dict(median=st.median(ratios), minimum=min(ratios), maximum=max(ratios),
                q25=e.percentile(ratios, .25), q75=e.percentile(ratios, .75),
                spread=(max(plausible)-min(plausible))/st.median(plausible))


def append_rows(data, fields, sources):
    rc, disc = data['RC'], data['DISC']
    ledger = Ledger(fields, sources)
    add = ledger.add
    # Replay the round-1 arithmetic as well as its byte prefix. The older rows
    # retain their historical pending notes; these new rows supply primary sources.
    original = e.base_bytes()
    buffer = io.StringIO(newline='')
    csv.DictWriter(buffer, fields, delimiter='\t', lineterminator='\n').writerows(e.append_rows(rc, fields))
    if original+buffer.getvalue().encode() != frozen_bytes():
        raise ValueError('round-1 arithmetic no longer reproduces its frozen table')

    floors = {label: floor_arithmetic(rc, label) for label in rc['floors']}
    floor_formula = ('RC.members[pack][*].{E_j,a_bop_j,r_j}; RC.floors[label].{kept_units,shared_j}; '
                     'point=max(envelope,Student prediction); independent sign corners, or one shared sign and local signs; '
                     'R=unguarded corner/point; guard=1 if n>=10 else sqrt(9/(n-1)); minted=guard*corner+gross allowance')
    # DISC has one independent row and, for comparative forms, a separate R_cm row.
    for i, row in enumerate(disc['block_lines']):
        if row['label'] != 'dominance_ratio':
            continue
        model = 'Qwen3-1.7B-4bit' if '1p7b' in row['cell_id'] else 'Qwen3-8B-4bit'
        phase = 'decode' if '-decode-' in row['cell_id'] else 'prefill'
        actual = dict(floors[f'{model}/{phase}/{row["component"]}'])
        if ': R_cm ' in row['text']:
            actual['numerator_j'] = actual['cm_numerator_j']
            actual['ratio'] = actual['numerator_j']/actual['denominator_j']
        for leaf in ('ratio', 'numerator_j', 'denominator_j', 'n'):
            add(f'DISC.block_lines[{i}].{leaf}', row[leaf], actual[leaf], floor_formula,
                digits=4 if leaf == 'ratio' else 5,
                note='point diagnostic; no interval; counterpart to round-1 RC operand rows')
        add(f'DISC.block_lines[{i}].status', row['status'], 'complete',
            floor_formula+'; complete iff denominator positive and registered n>=5')
    branch_row = one(disc['block_lines'], label='dominance_branch')
    branch_a = all(x['ratio'] >= 2 for x in floors.values()) and all(
        x['cm_numerator_j']/x['denominator_j'] >= 2 for x in floors.values() if 'cm_numerator_j' in x)
    add('DISC.block_lines[label=dominance_branch].branch', branch_row['branch'], 'A' if branch_a else 'B',
        floor_formula+'; branch A iff all eight R and four comparative R_cm>=2, otherwise B')
    add('DISC.block_lines[label=dominance_branch].dominance_sentence_licensed',
        branch_row['dominance_sentence_licensed'], branch_a,
        floor_formula+'; dominance sentence licensed iff branch A')
    for i, row in enumerate(disc['floors']):
        if row['label'] != 'floor_composition' or '-cmp-' not in row['cell_id']:
            continue
        model = 'Qwen3-1.7B-4bit' if '1p7b' in row['cell_id'] else 'Qwen3-8B-4bit'
        phase = 'decode' if '-decode-' in row['cell_id'] else 'prefill'
        value = floors[f'{model}/{phase}/comparative']['minted_j']
        add(f'DISC.floors[{i}].minted_j', row['minted_j'], value, floor_formula)
    for i, contrast in enumerate(data['FILL']['gamma']['contrasts']):
        # Floor condition/class is distinct from the >=2 dominance branch:
        # D-078 retains the attribution label when widening exceeds point scatter.
        for j, resolution in enumerate(contrast['floor']['resolutions']):
            if resolution['reason_codes']:
                raise ValueError('additional floor refusal; do not assign an attribution class')
            for cellid in resolution['source_cell_ids']:
                model = 'Qwen3-1.7B-4bit' if '1p7b' in cellid else 'Qwen3-8B-4bit'
                phase = 'decode' if '-decode-' in cellid else 'prefill'
                forms = [floors[f'{model}/{phase}/{form}'] for form in ('absolute', 'comparative')]
                widened = any(x['numerator_j'] > x['denominator_j'] for x in forms)
                if not widened:
                    raise ValueError('floor class requires a different registered condition')
            for leaf, value in [('floor_limit_class', 'attribution_limited'),
                                ('floor_source', 'E_clock_anchor_shift_bound_j')]:
                add(f'FILL.gamma.contrasts[{i}].floor.resolutions[{j}].{leaf}', resolution[leaf], value,
                    floor_formula+'; D-078 clause 11: corner widening exceeds point scatter; no additional refusal', alias='FILL')
        for container in ('floor', 'claim_evaluation.floor_limit'):
            row = contrast['floor'] if container == 'floor' else contrast['claim_evaluation']['floor_limit']
            for leaf, value in [('floor_limit_class', 'attribution_limited'), ('floor_source', 'E_clock_anchor_shift_bound_j')]:
                add(f'FILL.gamma.contrasts[{i}].{container}.{leaf}', row[leaf], value,
                    floor_formula+'; all contributing same-stack resolutions have the D-078 attribution condition', alias='FILL')

    index_raw = (REPO/'configs/analysis/b5/analysed_windows.json').read_bytes()
    index_hash = hashlib.sha256(index_raw).hexdigest()
    if index_hash != '51b039147192678b04d97ccbd923de04e5704fa783c6d2749c806a1026f917e4':
        raise ValueError('committed attempt index pin changed')
    index = json.loads(index_raw)['attempts']
    # Attempt-level leaves are recorded facts, compared to the committed index;
    # no prior failed attempt is re-analysed and no path in the index is followed.
    for i, row in enumerate(disc['block_lines']):
        if row['label'] not in ('attempt_count', 'attempt_history') or row['pack'] not in ('alpha', 'beta'):
            continue
        key = f'DISC.block_lines[{i}]'
        if row['label'] == 'attempt_count':
            attempts = [x for x in index if x['pack'] == row['pack'] and (x['seal'] == 'first') == row['superseded']]
            add(key+'.count', row['count'], len(attempts),
                'count matching pack and first/second-seal records in committed analysed_windows.json; over stored records',
                note='index sha256='+index_hash)
            add(key+'.causes', code_string(str(x) for x in row['causes']),
                code_string(str(x['cause_key']) for x in attempts),
                'set of cause_key values over matching pack/seal records; over stored judgments', note='index sha256='+index_hash)
            for cause, count in sorted(Counter(str(x) for x in row['causes']).items()):
                add(key+f'.cause_counts[cause={cause}]', count,
                    sum(str(x['cause_key']) == cause for x in attempts),
                    'count cause_key occurrences in matching pack/seal attempt records; over stored judgments',
                    note='index sha256='+index_hash+'; None denotes no exclusion cause')
        else:
            item = one(index, plan_id=row['plan_id'])
            for leaf in ('attempt', 'verdict', 'cause_key'):
                add(key+'.'+leaf, row[leaf], item[leaf],
                    f'analysed_windows.json.attempts[plan_id={row["plan_id"]}].{leaf}; exact record equality; not raw revalidation',
                    kind='recorded-judgment' if leaf in ('verdict', 'cause_key') else None,
                    note='index sha256='+index_hash)
            for leaf in ('collected', 'planned'):
                # For analysed attempts, independently count pinned per-member
                # records. Earlier counts are one disclosure producer's outputs.
                current = item['seal'] == 'second' and item['claim_usable']
                actual = (len(rc['disclosures']['whole_machine']['windows'][row['pack'].upper()]['members'])
                          if leaf == 'collected' else len(rc['members'][row['pack'].upper()])) if current else row[leaf]
                add(key+'.'+leaf, row[leaf], actual,
                    ('count RC.disclosures.whole_machine.windows[pack].members (succeeded); count RC.members[pack] (planned roster); over stored records'
                     if current else 'from the registered disclosure record; not independently recomputed; earlier attempt not analysed'),
                    kind=None if current or row[leaf] is None else 'single-source',
                    note='COLLECTED is the recorded attempt verdict; collected count is succeeded, not bundles absent; '+row['plan_id'])

    for pack, alias in (('ALPHA', 'PROJ-A'), ('BETA', 'PROJ-B')):
        for pcell in data[alias]['cells']:
            cid = pcell['cell_id']
            model = 'Qwen3-1.7B-4bit' if pack == 'ALPHA' else 'Qwen3-8B-4bit'
            cell = one(list(rc['reported_cells'].values()), model=model, phase=pcell['phase'])
            result = e.cell_arithmetic(rc, cell)
            base = f'{alias}.cells[cell_id={cid}]'
            formula = (f'RC.members.{pack}[*].{{E_j,a_bop_j}}.{cell["phase"]}; '+base+'.kept_units; '
                       'fixed .2 repeat/.8 quad-member averages; interpolation=0; drift=gross allowance/2')
            for kind, value in pcell['interval']['kind_averages_j'].items():
                expected = {'E_clock_anchor_shift_bound_j': result['kind_averages_j'][0],
                            'E_interpolation_joint_edge_bound_j': result['kind_averages_j'][1],
                            'E_whole_window_drift_allowance_j': result['kind_averages_j'][2]}[kind]
                add(base+f'.interval.kind_averages_j.{kind}', value, expected, formula, alias=alias)
            for leaf in ('attained_by', 'minimum_j'):
                add(base+'.attribution_floor.'+leaf, pcell['attribution_floor'][leaf], result[leaf],
                    formula+'; argmax/min first-kind width over kept members; only first kind has an attaining-run field', alias=alias)
            # Recount and compare the projected kept and removed unit identities.
            for stratum in ('repeat', 'quad'):
                projected = sorted(u['unit_id'] for u in pcell['kept_units'] if u['stratum'] == stratum)
                if projected != sorted(cell['kept_units'][stratum]):
                    raise ValueError('projection/RC kept membership differs')
            for removed in pcell['removed_units']:
                row = one(disc['cells'], label='removed unit', cell_id=cid, unit_id=removed['unit_id'])
                actual = one(cell['removed_units'], unit_id=removed['unit_id'])
                codes = {c for x in rc['exclusions_rederivation'][pack]['rederived']['members_excluded']
                         if x['run_id'] in actual['run_ids'] for c in x['codes']}
                key = f'DISC.cells[label=removed unit,cell_id={cid},unit_id={removed["unit_id"]}]'
                add(key+'.codes', code_string(row['codes']), code_string(codes),
                    formula+'; union member removal codes within unit; over stored flags')
                add(key+'.families', code_string(row['families']),
                    code_string(c for x in rc['exclusions_rederivation'][pack]['rederived']['members_excluded']
                                if x['run_id'] in actual['run_ids'] for c in x['families']),
                    formula+'; union stored member families by unit; over stored flags')

            battery = one(disc['cells'], label='battery_assist_cell', cell_id=cid)
            bkey = f'DISC.cells[label=battery_assist_cell,cell_id={cid}]'
            if any(battery['assist_members'].values()):
                raise ValueError('nonzero assist requires complete stored member flags')
            for stratum in ('repeat', 'quad'):
                add(bkey+'.assist_members.'+stratum, battery['assist_members'][stratum],
                    rc['disclosures']['battery_assist'][next(k for k,v in rc['reported_cells'].items() if v is cell)]['assist_members_by_stratum'][stratum],
                    'RC.disclosures.battery_assist[cell].assist_members_by_stratum; stored assist judgment; not re-detected', kind='recorded-judgment')
            for side in ('primary', 'without'):
                for leaf, actual in [('mean_j', result['mean']), ('h_j', result['h']), ('B_j', result['B_j']),
                                     ('lower_j', result['lower_j']), ('upper_j', result['upper_j'])]:
                    add(bkey+f'.{side}.{leaf}', battery[side][leaf], actual, formula+'; conditional on stored zero assisted members')
            for stratum, leaf in [('repeat','n_r'), ('quad','n_b')]:
                add(bkey+'.'+leaf, battery[leaf], len(cell['kept_units'][stratum]),
                    formula+'; count without-assist units, conditional on recorded zero assist')
            add(bkey+'.removed_unit_ids.count', len(battery['removed_unit_ids']), 0,
                'stored zero assist in both strata => no assisted units removed; conditional count')

            cross = e.cross_arithmetic(rc, cell)
            row = one(disc['cells'], label='cross_window', cell_id=cid)
            xkey = f'DISC.cells[label=cross_window,cell_id={cid}]'
            for leaf in ('delta_j', 'h_G_j', 'h_F_j', 'agree'):
                add(xkey+'.'+leaf, row[leaf], cross[leaf],
                    formula+'; GAMMA quad-arm means; h_G=t*sampleSD/sqrt(n); abs(delta)<=hypot(h_G,h_F); original rows 169-172 replayed in round 1')
            issued_word = 'agree' if 'estimates agree within' in row['text'] else 'differ' if 'estimates differ by' in row['text'] else None
            if issued_word is None:
                raise ValueError('unrecognized registered cross-session sentence')
            add(xkey+'.agree_or_differ_word', issued_word, 'agree' if cross['agree'] else 'differ',
                formula+'; registered §8.1 rule applied to hand-checked delta and half-widths; word from DISC.text')

            load_rows = [x for x in disc['cells'] if x['label']=='load_correlated_cell' and x['cell_id']==cid]
            loadkey = f'DISC.cells[label=load_correlated_cell,cell_id={cid}]'
            has_load = any(set(x['codes']) & e.LOAD_CODES for x in cell['removed_units'])
            add('count('+loadkey+')', len(load_rows), int(has_load),
                formula+'; registered line exists iff any removed unit has a load-correlated code; over stored flags')
            if load_rows:
                row = one(load_rows)
                restored = e.restored_load_units(cell['removed_units'])
                changed = dict(cell, kept_units={k:list(v) for k,v in cell['kept_units'].items()})
                for unit in restored:
                    changed['kept_units'][unit['stratum']].append(unit['unit_id'])
                for stratum, nkey in [('repeat','n_r'), ('quad','n_b')]:
                    add(loadkey+'.restored_counts.'+stratum, row['restored_counts'].get(stratum,0),
                        sum(u['stratum']==stratum for u in restored),
                        formula+'; restore iff complete nonempty removal code set is load-only; count by stratum; over stored flags')
                    add('DERIVE('+loadkey+').'+nkey, len(cell['kept_units'][stratum])+row['restored_counts'].get(stratum,0),
                        len(changed['kept_units'][stratum]), formula+'; kept plus restored counts; over stored flags')
                values = row['values']
                add(loadkey+'.values.status', values['status'], values['status'],
                    'source check of pinned registered pipeline computation/refusal status; provenance predicate not independently replayed',
                    note='exact sourcing of status metadata, not independent reproduction of pipeline computability')
                if values['status'] == 'refused':
                    add(loadkey+'.values.code', values['code'], values['code'],
                        'source check of pinned registered pipeline refusal code; not repaired or independently reproduced',
                        note='registered pipeline could not compute this line; round-1 RC value is uncompared')
                else:
                    sensitivity = e.cell_arithmetic(rc, changed)
                    for leaf, actual in [('mean_j',sensitivity['mean']), ('h_j',sensitivity['h']), ('B_j',sensitivity['B_j']),
                                         ('lower_j',sensitivity['lower_j']), ('upper_j',sensitivity['upper_j'])]:
                        add(loadkey+'.values.'+leaf, values[leaf], actual,
                            formula+'; restore only load-only units, recompute all stratum means/variances and kind averages')

    # Make contrast removal codes and families printable values, not row notes.
    for cell in data['EXC']['cells']:
        for unit in cell['dropped_units']:
            records = [x for x in data['EXC']['members_excluded'] if x['run_id'] in unit['run_ids']]
            key = f'EXC.cells[cell_id={cell["cell_id"]}].dropped_units[unit_id={unit["unit_id"]}]'
            for leaf in ('codes', 'families'):
                actual = code_string(c for x in records for c in x[leaf])
                # dropped_units carry codes, not families: derive the latter from
                # the separately stored per-member family sets.
                source = code_string(unit['codes']) if leaf=='codes' else actual
                add(key+'.'+leaf, source, actual,
                    'EXC.members_excluded[*].{run_id,codes,families}; union by quad run_ids; over stored flags', alias='EXC')
    for row in data['EXC']['members_excluded']:
        other = one(rc['exclusions_rederivation']['GAMMA']['rederived']['members_excluded'],run_id=row['run_id'])
        for leaf in ('codes','families'):
            add(f'EXC.members_excluded[run_id={row["run_id"]}].{leaf}', code_string(row[leaf]), code_string(other[leaf]),
                'RC.exclusions_rederivation.GAMMA.rederived.members_excluded; exact stored member code/family equality', alias='EXC')

    for pack in ('alpha', 'beta'):
        window_rows = disc['window_lines'][pack]
        mm = rc['members'][pack.upper()]
        excluded = rc['exclusions_rederivation'][pack.upper()]['rederived']['members_excluded']
        # Arm measurements/verdicts are the recorded inputs, as RL-41's GAMMA
        # arm amperage. They are not recreated from live probes.
        for i, row in enumerate(window_rows):
            key = f'DISC.window_lines.{pack}[{i}]'
            if row['label'] == 'arm_hazards':
                for leaf, value in row['measurements'].items():
                    add(key+'.measurements.'+leaf, value, value,
                        'from the arm collection record; not re-derived; '+row['module']+'/'+row['phase'], kind='recorded-judgment')
                add(key+'.verdict', row['verdict'], row['verdict'],
                    'stored arm probe verdict; '+row['module']+'/'+row['phase'], kind='recorded-judgment')
            elif row['label'] == 'monitor_cost':
                for leaf in ('cpu_s','reader_cpu_s','probes_inside_target_phases'):
                    add(key+'.'+leaf, row[leaf], row[leaf],
                        'from the registered disclosure record; not independently recomputed; endpoints/probe overlaps not in pinned summaries',
                        digits=2, kind='single-source')
            elif row['label'] == 'physics_counts':
                for code, count in row['counts'].items():
                    actual = sum(code in x['codes'] for x in excluded)
                    add(key+'.counts.'+code, count, actual,
                        f'RC.exclusions_rederivation.{pack.upper()}.rederived.members_excluded[*].codes; count members carrying code; over stored flags')
            elif row['label'] == 'battery_temperature':
                result = temperature_arithmetic(row['readings_centi_c'])
                for leaf, value in result.items():
                    add(key+'.'+leaf, row[leaf], value,
                        'DISC.window_lines[pack,stage_id].readings_centi_c; readable last-first/100; last-three range<=50; flag iff rise>3 and no plateau',
                        digits=2, note='stage_id='+row['stage_id']+'; no reading array serialized')
                add(key+'.harvest_flag', row['harvest_flag'], row['harvest_flag'],
                    'stored harvest flag, distinct from diagnostic producer arithmetic; '+row['stage_id'], kind='recorded-judgment')
                add(key+'.differs_from_harvest_flag', row['differs_from_harvest_flag'], result['producer_flag'] != row['harvest_flag'],
                    'recomputed diagnostic producer flag compared with stored harvest flag; over stored flags; '+row['stage_id'])

        for i, row in enumerate(window_rows):
            if row['label'] == 'machine_summary':
                models = sorted({v['model'] for v in rc['disclosures']['whole_machine']['windows'][pack.upper()]['members'].values()})
                model = next(m for m in models if m == row['model'] or
                             ('1p7b' in row['model'] and '1.7B' in m) or ('qwen3-8b' == row['model'] and 'Qwen3-8B' in m))
                result = rho_arithmetic(rc['disclosures']['whole_machine']['windows'][pack.upper()]['members'],model)
                for leaf,value in result.items():
                    add(f'DISC.window_lines.{pack}[{i}].{leaf}', row[leaf], value,
                        f'RC.disclosures.whole_machine.windows.{pack.upper()}.members[model={model}].phases.request; rho=rail_delta/(meter_delta+battery_delta); median/range/linear IQR; plausible spread=(max-min)/median', digits=4)

        append_neg8(ledger, rc, disc, pack)
    return ledger.rows


def append_neg8(ledger, rc, disc, pack):
    add = ledger.add
    rows = disc['window_lines'][pack]
    upper = pack.upper()
    ng, mm = rc['windows'][upper]['neg8'], rc['members'][upper]
    wm = rc['disclosures']['whole_machine']['windows'][upper]['members']
    values = one(rows, label='neg8_allowance')['values_j']
    base = f'DISC.window_lines.{pack}[label=neg8_allowance].values_j'
    family_results = {}
    for family in ('gross_energy', 'idle_subtracted_energy'):
        needed = set(ng['corpus_ids']) | set(ng['survivor_ids'])
        energies = ({u:mm[u]['E_j']['request'] for u in needed} if family=='gross_energy' else
                    {u:wm[u]['phases']['request']['rail_delta_J'] for u in needed})
        result = neg8_arithmetic(energies, ng['corpus_ids'], ng['survivor_ids'])
        family_results[family] = result
        formula = (f'RC.members.{upper}[*].E_j.request (gross), '
                   f'RC.disclosures.whole_machine.windows.{upper}.members[*].phases.request.rail_delta_J (idle-subtracted); '
                   f'RC.windows.{upper}.neg8.{{corpus_ids,survivor_ids}}; registration §0.12; '
                   'bound=max(U_ns-L_ne,U_ne-L_ns,rounded_t*sampleSD*sqrt(1/ns+1/ne)); '
                   'screen=abs(end_mean-start_mean)<=bound; allowance=max(bound,start/mid/end spread)')
        for leaf, actual in result.items():
            if leaf == 'decision':
                continue
            source_key = f'bracket.claim_families.{family}.{leaf}'
            if source_key not in values:
                # At the nominal (3,3) shape the producer reuses these bound
                # artifact terms, as registration §0.12 explicitly requires.
                source_key = (f'bracket.drift_bound_artifact.claim_family_bounds.{family}.estimator.'+
                              {'bound_envelope_j':'replicated_endpoint_sample_range_j',
                               'bound_prediction_j':'prediction_two_endpoint_means_j'}[leaf])
            add(base+'['+source_key+']', values[source_key], actual, formula)
        bound = values[f'bracket.claim_families.{family}.derived_repeatability_bound_j']
        statistic = values[f'bracket.claim_families.{family}.screen_statistic_j']
        add(f'DERIVE({base}.bracket.claim_families.{family}).screen_decision',
            'passed' if statistic <= bound else 'failed', result['decision'], formula,
            note='per-family word derived from issued statistic/bound; not a copied collection judgment')
    add(f'DISC.window_lines.{pack}[label=neg8_screen].decision', one(rows,label='neg8_screen')['decision'],
        'passed' if all(x['decision']=='passed' for x in family_results.values()) else 'failed',
        'RC member request gross/idle-subtracted energies; registration §0.12: both family screens must pass, at least two surviving references at each endpoint')
    counts = one(rows,label='reference_counts')
    for slot, planned in [('start',3),('midpoint',1),('end',3)]:
        actual = sum(f'-{slot}' in u for u in ng['survivor_ids'])
        add(f'DISC.window_lines.{pack}[label=reference_counts].counts.{slot}', counts['counts'][slot],actual,
            f'count RC.windows.{upper}.neg8.survivor_ids by registered slot; over stored membership')
        add(f'DISC.window_lines.{pack}[label=reference_counts].planned.{slot}',counts['planned'][slot],planned,
            'registration §0.12 planned start/midpoint/end counts 3/1/3')
    membership = one(rows,label='deciding_membership')
    add(f'DISC.window_lines.{pack}[label=deciding_membership].deciding_references',membership['deciding_references'],len(ng['survivor_ids']),
        f'count RC.windows.{upper}.neg8.survivor_ids; over stored membership')
    add(f'DISC.window_lines.{pack}[label=deciding_membership].deciding_spares',membership['deciding_spares'],
        sum('spare' in u for u in ng['survivor_ids']),
        f'count spare identifiers in RC.windows.{upper}.neg8.survivor_ids; deciding spares only, not all attempted retries')
    spares = [x for x in rows if x['label'] == 'reference_spare']
    add(f'count(DISC.window_lines.{pack}[label=reference_spare])',len(spares),
        sum('spare' in u for u in mm),
        f'count disclosed reference_spare records versus spare identifiers in RC.members.{upper}; over recorded roster/retry flags; no raw retry-log replay')
    lost = [x for x in rows if x['label']=='reference_lost']
    add(f'count(DISC.window_lines.{pack}[label=reference_lost])', len(lost),7-len(ng['survivor_ids']),
        f'planned seven references minus count RC.windows.{upper}.neg8.survivor_ids; over stored membership')
    add(f'DERIVE(DISC.window_lines.{pack}[label=reference_counts]).midpoint_lost',counts['counts']['midpoint']==0,
        not any('-midpoint' in u for u in ng['survivor_ids']),
        f'RC.windows.{upper}.neg8.survivor_ids; no surviving midpoint iff midpoint lost; over stored membership')
    for row in lost:
        excluded = one(rc['exclusions_rederivation'][upper]['rederived']['members_excluded'],run_id=row['run_id'])
        add(f'DISC.window_lines.{pack}[label=reference_lost,run_id={row["run_id"]}].reason',row['reason'],code_string(excluded['codes']),
            f'RC.exclusions_rederivation.{upper}.rederived.members_excluded[run_id].codes; over stored flags')
    corpus = one(rows,label='corpus_counts')
    all_ids = {u for u in mm if u.startswith('neg8-refcorpus-')}
    succeeded = {u for u in all_ids if u in wm}
    drops = [x for x in rows if x['label']=='corpus_physics_drop']
    clean = sorted(succeeded-{x['run_id'] for x in drops})
    # Selection is a recorded input. This checks its ID arithmetic/cap, not raw
    # clean-corpus eligibility or any mint refusal against the original archive.
    if clean[:12] != sorted(ng['corpus_ids']):
        raise ValueError('clean-corpus cap membership differs')
    for leaf, actual in [('collected',len(all_ids)), ('in_window',len(succeeded)), ('deciding',len(ng['corpus_ids']))]:
        add(f'DISC.window_lines.{pack}[label=corpus_counts].'+leaf,corpus[leaf],actual,
            f'RC.members.{upper} and RC.disclosures.whole_machine.windows.{upper}.members; count corpus roster/succeeded/deciding IDs; over stored records')
    add(f'DISC.window_lines.{pack}[label=corpus_counts].desk_cap',code_string(corpus['desk_cap']),code_string(clean[12:]),
        f'RC.windows.{upper}.neg8.corpus_ids; sorted succeeded corpus minus recorded physics drops; first twelve deciding, remainder desk cap; over stored flags')
    drop_counts = Counter(c for row in drops for c in row['codes'])
    drop_counts.update(status=len(all_ids-succeeded),desk_cap=len(clean[12:]))
    for code,count in corpus['drop_counts'].items():
        add(f'DISC.window_lines.{pack}[label=corpus_counts].drop_counts.{code}',count,drop_counts[code],
            f'RC member corpus ID census; count DISC corpus_physics_drop codes, status losses and desk cap; over stored records')
    for row in drops:
        excluded = one(rc['exclusions_rederivation'][upper]['rederived']['members_excluded'],run_id=row['run_id'])
        add(f'DISC.window_lines.{pack}[label=corpus_physics_drop,run_id={row["run_id"]}].codes',code_string(row['codes']),code_string(excluded['codes']),
            f'RC.exclusions_rederivation.{upper}.rederived.members_excluded[run_id].codes; over stored flags')


def append_only(current, prefix, rows, fields):
    if not current.startswith(prefix):
        raise ValueError('committed 801-row prefix changed; refuse')
    buffer = io.StringIO(newline='')
    csv.DictWriter(buffer, fields, delimiter='\t', lineterminator='\n').writerows(rows)
    result = prefix+buffer.getvalue().encode()
    if current not in (prefix, result):
        raise ValueError('existing appended rows differ; refuse overwrite')
    return result


def repository_check():
    current = (HERE/'rederivation.tsv').read_bytes()
    e.check_round1_bytes(current)
    frozen = subprocess.run(['git', 'show', f'{ROUND2}:docs/analysis/b5/rederivation.tsv'],
                            cwd=REPO, check=True, capture_output=True).stdout
    if current != frozen:
        raise ValueError('round-2 ledger differs from frozen 1419-row authority; refuse')
    print(json.dumps({'mode':'repository-only; no custody arithmetic rerun',
                      'scope':'full 1419-row ledger including both unchanged prefixes',
                      'full_ledger_byte_identical':True, 'opened_custody':[]}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--repo-only',action='store_true',help='check frozen full ledger; never open custody')
    args = parser.parse_args()
    if args.repo_only:
        if args.write:
            parser.error('--repo-only cannot be combined with --write')
        repository_check()
        return
    prefix = frozen_bytes()
    target = HERE/'rederivation.tsv'
    current = target.read_bytes()
    if not current.startswith(prefix):
        raise ValueError('committed 801-row prefix changed; refuse before custody access')
    fields = next(csv.reader(io.StringIO(prefix.decode()),delimiter='\t'))
    reader = ReleasedReader()
    try:
        data = {a:reader.read(a) for a in ALIASES}
        rows = append_rows(data, fields, reader.sources)
    finally:
        print(json.dumps({'opened_custody':reader.finish()},sort_keys=True))
    result = append_only(current,prefix,rows,fields)
    if args.write:
        target.write_bytes(result)
    elif result != current:
        raise ValueError('new rows not appended; use --write')
    complete = list(csv.DictReader(io.StringIO(result.decode()),delimiter='\t'))
    print(json.dumps({'round2_new_rows':len(rows), 'round2_counts':dict(Counter(x['match'] for x in rows)),
                      'full_counts':dict(Counter(x['match'] for x in complete)),
                      'unchanged_round1_prefix':True,
                      'results_sha256':hashlib.sha256((HERE/'RESULTS.md').read_bytes()).hexdigest()},sort_keys=True))


if __name__ == '__main__':
    main()
