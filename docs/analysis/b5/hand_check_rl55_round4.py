#!/usr/bin/env python3
"""RL-55 append-only, aggregate-only stdlib hand checks. No analysis imports.

Only RC, DISC and CMP, from the exact RL-38 pins, are needed for the new rows.
The reader hashes before loading, verifies the loaded bytes, and rehashes in
finally. No paths embedded in JSON are followed. --repo-only opens no custody.
Earlier arithmetic is reused from the independent round-2 checker, not from
any producer, comparator or recomputation implementation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[2]
BASE = '60f66800fabe02c574dab41b2a61f38623c47a0c'
RESULTS_SHA256 = 'fb5f81e8741532d79b059b2ca7c44b1c479f0f983c28527ab6e2511d7dfb6f55'
spec = importlib.util.spec_from_file_location('rl55_round2_helpers', HERE/'hand_check_rl52_round2.py')
r2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r2)


class ReleasedReader(r2.ReleasedReader):
    def __init__(self):
        super().__init__()
        with (HERE/'phase2_sources.tsv').open() as stream:
            row = r2.one(list(csv.DictReader(stream, delimiter='\t')), alias='CMP')
        root, relative, pin = r2.h.SOURCES['CMP']
        if row['path'] != str(root/relative) or row['sha256_before'] != pin or row['sha256_after'] != pin:
            raise ValueError('CMP phase-2 pin differs')
        self.sources['CMP'] = (root, relative, pin)
        self.sources = {a:self.sources[a] for a in ('RC','DISC','CMP')}


def prefix_bytes():
    return subprocess.run(['git', 'show', f'{BASE}:docs/analysis/b5/rederivation.tsv'],
                          cwd=REPO, check=True, capture_output=True).stdout


def append_rows(data, fields, sources):
    rc, disc = data['RC'], data['DISC']
    ledger = r2.Ledger(fields, sources)
    add = ledger.add
    for pack in ('alpha', 'beta', 'gamma'):
        rows = disc['window_lines'][pack]
        upper = pack.upper()
        flags = [x for x in rows if x['label'] == 'flag_count']
        counts = r2.one(rows, label='battery_counts')['counts']
        for code, count in counts.items():
            actual = sum(x['count'] for x in flags if x['code'] == code)
            # Independent recompute's retained by-code flags also agree. Zero
            # is absence of this code in the full disclosed flag-count roster.
            if actual != rc['exclusions_rederivation'][upper]['rederived']['flag_counts']['by_code'].get(code, 0):
                raise ValueError('DISC/RC battery flag-count records disagree')
            add(f'DISC.window_lines.{pack}[label=battery_counts].counts.{code}', count, actual,
                f'sum DISC.window_lines.{pack}[label=flag_count,code].count (absent code=0); '
                f'cross-check RC.exclusions_rederivation.{upper}.rederived.flag_counts.by_code; '
                'arithmetic over stored flag-count records; not raw battery re-detection')
        # Empty measurements do not mean UNMEASURED. The registered condition
        # is the module.arm_unmeasured flag, not dictionary length or PASS.
        unread = [x for x in flags if x['code'].endswith('.arm_unmeasured')]
        add(f'DERIVE(DISC.window_lines.{pack}).arm_unmeasured_count',
            sum(x['count'] for x in unread),
            sum(v for k, v in rc['exclusions_rederivation'][upper]['rederived']['flag_counts']['by_code'].items()
                if k.endswith('.arm_unmeasured')),
            f'sum disclosed <module>.arm_unmeasured counts; RC.exclusions_rederivation.{upper}.rederived.flag_counts.by_code; '
            'over stored flags; empty measurement maps alone do not establish unread probes')
        for i, row in enumerate(rows):
            key = f'DISC.window_lines.{pack}[{i}]'
            if row['label'] == 'battery_temperature':
                add(key+'.stage_id', row['stage_id'], row['stage_id'],
                    'exact registered stage name; no temperature reading array serialized')
                if pack == 'gamma':
                    result = r2.temperature_arithmetic(row['readings_centi_c'])
                    for leaf, value in result.items():
                        add(key+'.'+leaf, row[leaf], value,
                            'DISC stage readings_centi_c; readable last-first/100; last-three range<=50; '
                            'flag iff rise>3 and no plateau', digits=2,
                            note='stage_id='+row['stage_id']+'; no reading array serialized')
                    add(key+'.harvest_flag', row['harvest_flag'], row['harvest_flag'],
                        'stored harvest stage flag; not re-derived; '+row['stage_id'], kind='recorded-judgment')
                    add(key+'.differs_from_harvest_flag', row['differs_from_harvest_flag'],
                        result['producer_flag'] != row['harvest_flag'],
                        'computed diagnostic producer flag compared with harvest flag; over stored flags')
            elif pack == 'gamma' and row['label'] == 'arm_hazards':
                for leaf, value in row['measurements'].items():
                    add(key+'.measurements.'+leaf, value, value,
                        'from arm collection record; not re-derived; '+row['module']+'/'+row['phase'],
                        kind='recorded-judgment')
                add(key+'.verdict', row['verdict'], row['verdict'],
                    'stored arm probe verdict; '+row['module']+'/'+row['phase'], kind='recorded-judgment')
            elif pack == 'gamma' and row['label'] == 'physics_counts':
                excluded = rc['exclusions_rederivation'][upper]['rederived']['members_excluded']
                for code, count in row['counts'].items():
                    add(key+'.counts.'+code, count, sum(code in x['codes'] for x in excluded),
                        'RC.exclusions_rederivation.GAMMA.rederived.members_excluded[*].codes; '
                        'count members carrying code; over stored flags')
            elif row['label'] == 'reference_lost':
                for leaf in ('run_id', 'slot'):
                    # Names and slots are registered metadata, not readings.
                    add(f'DISC.window_lines.{pack}[label=reference_lost,run_id={row["run_id"]}].'+leaf,
                        row[leaf], row[leaf], 'exact registered lost-reference identity/slot metadata')
        for row in disc['cells']:
            if row['label'] != 'removed unit' or row['pack'] != pack:
                continue
            key = f'DISC.cells[label=removed unit,cell_id={row["cell_id"]},unit_id={row["unit_id"]}]'
            for leaf in ('stratum', 'stage_ids', 'positions'):
                value = (','.join(map(str, row[leaf])) if isinstance(row[leaf], list) else row[leaf])
                add(key+'.'+leaf, value, value,
                    'exact registered removed-unit position metadata; no member energy serialized')
    # Same member arithmetic and selection/count checks as ALPHA/BETA. This
    # adds both family words, both bound terms, allowance, lost-reference and
    # corpus-drop reasons as well as the overall GAMMA screen word.
    r2.append_neg8(ledger, rc, disc, 'gamma')
    raw = (REPO/'configs/analysis/b5/analysed_windows.json').read_bytes()
    pin = hashlib.sha256(raw).hexdigest()
    if pin != '51b039147192678b04d97ccbd923de04e5704fa783c6d2749c806a1026f917e4':
        raise ValueError('committed attempt index changed')
    index = json.loads(raw)['attempts']
    for i, row in enumerate(disc['block_lines']):
        if row.get('pack') != 'gamma' or row['label'] not in ('attempt_count', 'attempt_history'):
            continue
        key = f'DISC.block_lines[{i}]'
        formula = 'committed configs/analysis/b5/analysed_windows.json; sha256='+pin
        if row['label'] == 'attempt_count':
            attempts = [x for x in index if x['pack']=='gamma' and (x['seal']=='first')==row['superseded']]
            add(key+'.count', row['count'], len(attempts), formula+'; count matching records')
            add(key+'.causes', r2.code_string(str(x) for x in row['causes']),
                r2.code_string(str(x['cause_key']) for x in attempts), formula+'; cause-key set over stored judgments')
            for cause, count in sorted(Counter(str(x) for x in row['causes']).items()):
                add(key+f'.cause_counts[cause={cause}]', count,
                    sum(str(x['cause_key'])==cause for x in attempts), formula+'; cause multiplicity over stored judgments')
        else:
            item = r2.one(index, plan_id=row['plan_id'])
            for leaf in ('attempt', 'verdict', 'cause_key'):
                add(key+'.'+leaf, row[leaf], item[leaf], formula+'; exact record equality; not raw revalidation',
                    kind='recorded-judgment' if leaf in ('verdict', 'cause_key') else None)
            for leaf, actual in [('collected',len(rc['disclosures']['whole_machine']['windows']['GAMMA']['members'])),
                                 ('planned',len(rc['members']['GAMMA']))]:
                add(key+'.'+leaf, row[leaf], actual,
                    'count RC.disclosures.whole_machine.windows.GAMMA.members (succeeded); '
                    'count RC.members.GAMMA (planned roster); over stored records; 107 present/raw-valid, 103 succeeded')
    # The per-block recomputation placeholders also ask for per-family bars,
    # counts, maxima and words. Only family aggregates are serialized, never
    # comparator member values or the key attaining a maximum.
    cmp = data['CMP']
    for family, counts in cmp['counts'].items():
        records = [x for x in cmp['comparisons'] if x['family']==family]
        key = f'CMP.counts.{family}'
        formula = 'CMP.comparisons[family]; independently count and compare issued records; no member values serialized'
        for leaf, word in [('pass','AGREE'), ('fail','DIFFER')]:
            actual = sum(x['verdict']==word for x in records)
            if any(x['verdict'] not in ('AGREE','DIFFER') for x in records):
                raise ValueError('unexpected comparator verdict')
            add(key+'.'+leaf, counts[leaf], actual, formula, alias='CMP')
        add(f'DERIVE(CMP.comparisons[family={family}]).compared', sum(counts.values()), len(records), formula, alias='CMP')
        for leaf in ('absolute','relative') if family in cmp['bars'] else ():
            value = cmp['bars'][family][leaf]
            # Preserve the exact public bar representation, including tiny bars.
            add(f'CMP.bars.{family}.{leaf}', str(value), value,
                'fixed blind recompute bar; exact sourcing of committed bar constants', alias='CMP')
        numeric = [x for x in records if 'difference' in x]
        if numeric:
            largest = max(abs(x['l9']-x['recompute']) for x in numeric)
            stored = max(abs(x['difference']) for x in numeric)
            add(f'DERIVE(CMP.comparisons[family={family}]).largest_absolute_difference',
                format(stored,'.2g'), largest, formula+'; max(abs(l9-recompute)) across family; two significant figures', alias='CMP')
        agrees = all((abs(x['l9']-x['recompute'])<=x['bar'] if 'difference' in x else x['l9']==x['recompute'])
                     for x in records)
        add(f'DERIVE(CMP.comparisons[family={family}]).agreement_word',
            'not-compared' if not records else 'AGREE' if counts['fail']==0 else 'DIFFER',
            'not-compared' if not records else 'AGREE' if agrees else 'DIFFER',
            formula+'; numeric abs(l9-recompute)<=issued row bar; categorical equality; empty family explicitly not-compared', alias='CMP')
    for row in disc['cells']:
        if row['label'] == 'removed unit':
            key = f'DISC.cells[label=removed unit,cell_id={row["cell_id"]},unit_id={row["unit_id"]}]'
            add(key+'.unit_id', row['unit_id'], row['unit_id'], 'exact registered removed-unit name; no member reading')
    for row in disc['contrasts']:
        if row['label'] != 'removed unit':
            continue
        key = f'DISC.contrasts[label=removed unit,cell_id={row["cell_id"]},unit_id={row["unit_id"]}]'
        for leaf in ('unit_id', 'stratum', 'stage_ids', 'positions'):
            value = ','.join(map(str,row[leaf])) if isinstance(row[leaf],list) else row[leaf]
            add(key+'.'+leaf, value, value, 'exact registered removed-quad name/position metadata; no member reading')
    for row in ledger.rows:
        row['note'] = row['note'].replace('RL-52 round 2;', 'RL-55 round 4;')
    return ledger.rows


def serialize(current, prefix, rows, fields):
    if not current.startswith(prefix):
        raise ValueError('existing 1419-row prefix differs; refuse')
    buffer = io.StringIO(newline='')
    csv.DictWriter(buffer, fields, delimiter='\t', lineterminator='\n').writerows(rows)
    result = prefix+buffer.getvalue().encode()
    if not result.startswith(current):
        raise ValueError('round-4 append differs; refuse overwrite')
    return result


def repository_check():
    raw = (HERE/'rederivation.tsv').read_bytes()
    if not raw.startswith(prefix_bytes()):
        raise ValueError('original/round-1/round-2 prefix differs')
    expected = (HERE/'round4_sources.tsv').read_text()
    manifest = list(csv.DictReader(io.StringIO(expected), delimiter='\t'))
    if {r['alias'] for r in manifest} != {'RC','DISC','CMP'}:
        raise ValueError('unexpected round-4 manifest aliases')
    for row in manifest:
        root, relative, pin = r2.h.SOURCES[row['alias']]
        if row['path'] != str(root/relative) or row['sha256_before'] != pin or row['sha256_after'] != pin:
            raise ValueError('round-4 recorded hashes differ from pins')
    # The fill checker owns the final full digest and independently checks the
    # original 1-538 prefix. Importing it performs no reads or custody access.
    s = importlib.util.spec_from_file_location('rl55_fill_gate', REPO/'docs/paper/paper1/fill_check_b5.py')
    fill = importlib.util.module_from_spec(s); s.loader.exec_module(fill)
    fill.load_ledger()
    if fill.FAILURES:
        raise ValueError('; '.join(fill.FAILURES))
    if hashlib.sha256((HERE/'RESULTS.md').read_bytes()).hexdigest() != RESULTS_SHA256:
        raise ValueError('RESULTS bytes changed')
    print(json.dumps({'mode':'repository-only; no custody replay', 'prefix_byte_identical':True,
                      'full_ledger_sha256':hashlib.sha256(raw).hexdigest()}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--repo-only', action='store_true')
    args = parser.parse_args()
    if args.repo_only:
        if args.write:
            parser.error('--repo-only cannot be combined with --write')
        repository_check(); return
    prefix = prefix_bytes()
    target = HERE/'rederivation.tsv'
    current = target.read_bytes()
    if not current.startswith(prefix):
        raise ValueError('prefix changed before custody access')
    fields = next(csv.reader(io.StringIO(prefix.decode()), delimiter='\t'))
    reader = ReleasedReader()
    try:
        data = {a:reader.read(a) for a in ('RC','DISC','CMP')}
        rows = append_rows(data, fields, reader.sources)
    finally:
        opened = reader.finish()
        print(json.dumps({'opened_custody':opened}, sort_keys=True))
    # Replay only round 4's physical rows; a later append is immutable too.
    # --write may finish round 4, but must never truncate a later extension.
    scope = b''.join(current.splitlines(keepends=True)[:len(prefix.splitlines())+len(rows)])
    result = serialize(scope, prefix, rows, fields)
    if args.write:
        if current != scope:
            raise ValueError('later append exists; refuse overwrite')
        target.write_bytes(result)
        with (HERE/'round4_sources.tsv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, ['alias','path','sha256_before','sha256_after'], delimiter='\t', lineterminator='\n')
            writer.writeheader()
            writer.writerows(dict(alias=a, **{k:v for k,v in opened[a].items() if k!='expected_sha256'}) for a in sorted(opened))
    elif scope != result:
        raise ValueError('new rows absent; use --write')
    print(json.dumps({'round4_rows':len(rows), 'round4_counts':dict(Counter(r['match'] for r in rows)),
                      'full_counts':dict(Counter(r['match'] for r in csv.DictReader(io.StringIO(result.decode()),delimiter='\t'))),
                      'ledger_sha256':hashlib.sha256(result).hexdigest()},sort_keys=True))
    if any(r['match'] in ('MISMATCH','source-outside-unseal') for r in rows):
        raise ValueError('new mismatch/outside-unseal; report, do not repair')


if __name__ == '__main__':
    main()
