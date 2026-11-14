#!/usr/bin/env python3
"""RL-55 pending Block 5 fill inventory, checked against the merged paper.

No custody or network access. Build an element/row map, or check its exact TSV
serialization. Row numbers are physical TSV lines including the header.
Reasons apply only to the named element, never to an entire composite fill.

The map is of the paper snapshot PAPER_COMMIT, taken before the second fill, and
stays byte-identical. After the second fill the working-tree paper is checked
against it separately (check_working_paper): every mapped id is either filled,
deleted with its branch or dropped, as fill_check_b5.py records, or still pending
there; no Block 5 placeholder outside the map appears.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import importlib.util
import io
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[2]
PAPER_COMMIT = '9fb42569069b4b7f47b020ec794864101410e8c8'
PAPER_PATH = 'docs/paper/paper1/paper1.md'
FIELDS = ['paper_commit','paper_line','placeholder','description','element','ledger_rows','reason','committed_file','instruction']
REASONS = {'not a leaf of a registered output','needs Block 6','a name from a committed file',
           'outside Block 5 (BYTES; sealed)'}
IDENTITY = 'configs/campaigns/v5_claim_25g83/identity_pins.json'
PIN = 'configs/campaigns/d117_floor_qwen3-1p7b_v5/prefill_pin/'
INDEX = 'configs/analysis/b5/analysed_windows.json'
PLAN = 'configs/campaigns/v5_claim_25g83/analysis_plan_block5.md'


# The 57 Block 5 ids pending at PAPER_COMMIT (fill_check_b5.PENDING before the second fill).
PENDING_AT_SNAPSHOT = [
    'P1-B5-METER', 'P1-B5-ATTEMPTS', 'P1-B5-ANALYSED', 'P1-B5-HAZARDS', 'P1-B5-INTERVAL-PARTS', 'P1-B5-B-SHARE',
    'P1-B5-BATT-LINE', 'P1-B5-LOAD-LINE', 'P1-B5-DOM-FAILED', 'P1-B5-DOM-REFUSED', 'P1-B5-XWIN', 'P1-B5-NEG8',
    'P1-B5-MONITOR', 'P1-B5-RM-ctr-decode', 'P1-B5-RM-ctr-prefill', 'P1-RECOMPUTE-SUMMARY', 'P1-ABS-PART1',
    'CP-X01-identity', 'CP-X01-length', 'CP-X02-conclusion', 'CP-X08-decode-a-conclusion']
PENDING_AT_SNAPSHOT += [f'P1-B5-{k}-{c}' for k in ('RM', 'FN') for c in ('1p7B-decode', '1p7B-prefill', '8B-decode', '8B-prefill')]
PENDING_AT_SNAPSHOT += [f'F_{c}_cmp_J' for c in ('1p7B_decode', '1p7B_prefill_p2048', '8B_decode', '8B_prefill_p2048')]
PENDING_AT_SNAPSHOT += [f'{p}{c}_{f}{s}' for c in ('1p7B_decode', '1p7B_prefill_p2048', '8B_decode', '8B_prefill_p2048')
                        for f in ('abs', 'cmp') for p, s in (('R_', ''), ('TERM_A_', '_J'), ('TERM_B_', '_J'))]
MIXED = {'P1-ID-OS','P1-M-RECORD-WIDTH','P1-M-ACCEPT','P1-LEDGER','P1-DEV-LIST','P1-RELEASE','P1-RECOMPUTE','P1-AVAIL'}
# Placeholders the second fill created (RL-52 (4): the Block 6 half of P1-RECOMPUTE-SUMMARY).
NEW_AFTER_SNAPSHOT = {'P1-RECOMPUTE-SUMMARY-B6'}
FILL_ID = re.compile(r'\{\{FILL:\s*([^|]+?)\s*\|')


def paper_text():
    """The paper the coverage map was built from: the pinned pre-second-fill snapshot (local Git only)."""
    return subprocess.run(['git','show',PAPER_COMMIT+':'+PAPER_PATH],cwd=REPO,check=True,capture_output=True,text=True).stdout


def fill_module():
    s = importlib.util.spec_from_file_location('coverage_fill_metadata',REPO/'docs/paper/paper1/fill_check_b5.py')
    fill = importlib.util.module_from_spec(s); s.loader.exec_module(fill)
    return fill


def check_working_paper(current, rows, fill=None):
    """Every mapped id is filled, deleted, dropped or still pending in the working paper; nothing unmapped appears."""
    fill = fill or fill_module()
    mapped = {r['placeholder'] for r in rows}
    present = {m[1].rstrip(' \\') for m in FILL_ID.finditer(current)}
    done = set(fill.FILLED) | set(fill.DELETED_WITH_BRANCH) | set(fill.DROPPED)
    for fid in mapped:
        if fid in present:
            if fid not in set(fill.PENDING) | MIXED:
                raise ValueError('working paper: mapped id still a placeholder but not listed pending: '+fid)
        elif fid not in done:
            raise ValueError('working paper: mapped id gone without a fill, branch or drop record: '+fid)
    for fid in present:
        if (fid.startswith('P1-B5-') or fid in set(fill.PENDING)) and fid not in mapped | NEW_AFTER_SNAPSHOT:
            raise ValueError('working paper: unaccounted Block 5 placeholder: '+fid)
    if not set(fill.PENDING) <= mapped | NEW_AFTER_SNAPSHOT:
        raise ValueError('fill_check_b5.PENDING names an id outside the coverage map')
    return len(mapped - present), len(mapped & present)


def build(paper, ledger):
    placeholders = {}
    for m in re.finditer(r'\{\{FILL:\s*([^|]+?)\s*\|\s*(.*?)\}\}',paper,re.S):
        fid = m[1].rstrip(' \\')
        placeholders[fid] = (paper.count('\n',0,m.start())+1, ' '.join(m[2].split()))
    fill = fill_module()
    pending = set(PENDING_AT_SNAPSHOT)
    # Mixed placeholders remain outside the second fill, but their Block 5
    # elements are also inventoried so none is silently treated as complete.
    mixed = MIXED
    if not pending <= placeholders.keys():
        raise ValueError('pinned main is missing pending ids')
    if {k for k in placeholders if k.startswith('P1-B5-')} - pending:
        raise ValueError('unaccounted Block 5 placeholder')
    out = []

    def add(fid, element, numbers=(), *, reason='', file='', note=''):
        if fid not in pending|mixed:
            raise ValueError('unlisted Block 5 id: '+fid)
        if not numbers and reason not in REASONS:
            raise ValueError('missing row/reason: '+element)
        for n in numbers:
            r = ledger[n]
            if r['match'] not in fill.PASSING or r['paper1'] not in fill.PRINTABLE:
                raise ValueError('coverage cites nonprinting row '+str(n))
        if not note:
            note = ('Apply RL-41/RL-42 print and attribution rules.' if numbers else
                    'Use the named committed metadata file; no outcome estimate is implied.')
        line, desc = placeholders[fid]
        out.append(dict(zip(FIELDS, [PAPER_COMMIT,str(line),fid,desc,element,
                                    ','.join(map(str,numbers)),reason,file,note])))

    def use(fid, numbers, label='', note=''):
        for n in numbers:
            add(fid, (label+': ' if label else '')+ledger[n]['key/leaf'], [n], note=note)

    def select(fid, predicate, label='', note=''):
        ns = [n for n,r in ledger.items() if predicate(r['key/leaf'])]
        if not ns:
            raise ValueError('empty element group: '+fid+' '+label)
        use(fid,ns,label,note)

    def name(fid, element, file, note=''):
        add(fid,element,reason='a name from a committed file',file=file,note=note)

    def later(fid, element):
        add(fid,element,reason='needs Block 6',note='Leave this element pending; no sealed output was read.')

    def nonleaf(fid, element, file='', note=''):
        add(fid,element,reason='not a leaf of a registered output',file=file,note=note)

    def sealed_bytes(fid, element, note):
        add(fid,element,reason='outside Block 5 (BYTES; sealed)',note=note)

    # Explicit element enumeration of each composite description.
    use('P1-B5-METER', range(722,785), 'per pack/model median, range, IQR, spread, hard-band count and consistency',
        'Every outside_hard_band.count is zero: no outside member or meter-flag listing is owed. Includes the reference model.')
    use('P1-B5-METER',[528], 'central band',
        'Zero clean windows: print "no clean session, no central band"; later inside-band counts are inapplicable.')
    use('P1-B5-ATTEMPTS',range(885,950),'ALPHA/BETA and superseded first-seal attempts',
        'Attribute verdict/cause judgments; label earlier non-null counts from the disclosure record, not independently recomputed. Collected means succeeded.')
    use('P1-B5-ATTEMPTS',range(1643,1651),'GAMMA count, causes, attempt, verdict, collected/planned')
    name('P1-B5-ATTEMPTS','pack/attempt identifiers; first-seal separation and inputs to no number',INDEX,
         'Use seal and claim_usable in the committed index; first-seal ALPHA has three attempts, separate from the second seal.')
    for pack in ('alpha','beta','gamma'):
        name('P1-B5-ANALYSED',pack+' analysed plan_id and UTC date from t0_epoch_s',INDEX,
             'RL-52(3): names from the committed index; select second-seal claim_usable record; do not follow any path.')
    for model in ('1p7B','8B'):
        for phase in ('decode','prefill'):
            fid = f'P1-B5-RM-{model}-{phase}'
            tag = 'qwen3-1p7b' if model=='1p7B' else 'qwen3-8b'
            cid = f'd117-reported-mean-ph-{phase}'+('-p2048' if phase=='prefill' else '')+'-'+tag
            select(fid,lambda k,cid=cid:k.startswith('DISC.cells[label=removed unit,cell_id='+cid+','),
                   'removed-unit name, stratum, codes, families, stages and positions')
    for phase, nums in [('decode',range(198,202)),('prefill',range(202,209))]:
        fid = 'P1-B5-RM-ctr-'+phase
        use(fid,nums,'removed contrast quad/member identities and positions')
        select(fid,lambda k,p=phase:k.startswith('EXC.cells[cell_id=ctr-d117-'+p+'-') and '.dropped_units[' in k,
               'per-quad code and family unions')
        select(fid,lambda k,p=phase:k.startswith('EXC.members_excluded[') and '-'+p+'-' in k,
               'triggering member codes/families')
        select(fid,lambda k,p=phase:k.startswith('DISC.contrasts[label=removed unit,cell_id=ctr-d117-'+p+'-'),
               'removed-quad name, stratum, stages and ordinal positions')
    for pack, arm_range, physics_range in [('alpha',range(1163,1181),range(1181,1183)),
                                          ('beta',range(1291,1309),range(1309,1311)),
                                          ('gamma',range(1512,1530),range(1530,1532))]:
        use('P1-B5-HAZARDS',arm_range,pack+' arm readings and verdicts',
            'Recorded collection judgments; empty measurement map is not an unread probe.')
        use('P1-B5-HAZARDS',physics_range,pack+' counts of each physics code')
        select('P1-B5-HAZARDS',lambda k,p=pack:k.startswith(f'DISC.window_lines.{p}[label=battery_counts].'),pack+' window battery counts')
        select('P1-B5-HAZARDS',lambda k,p=pack:k==f'DERIVE(DISC.window_lines.{p}).arm_unmeasured_count',pack+' unread hazard count',
               'Zero stored module.arm_unmeasured flags: no module-name/no-reading sentence is triggered.')
        # stage names plus each diagnostic/harvest flag; never the reading array.
        stage_keys = {k.rsplit('.',1)[0] for r in ledger.values() if (k:=r['key/leaf']).startswith(f'DISC.window_lines.{pack}[') and k.endswith('.stage_id')}
        select('P1-B5-HAZARDS',lambda k,bases=stage_keys:any(k.startswith(b+'.') for b in bases),pack+' per-stage name/rise/plateau/flags',
               'none rise means fewer than two readable readings; temperature_unmeasured means no readable readings; keep these distinct.')
    use('P1-B5-HAZARDS',range(242,245),'original contention totals; counts over stored flags')
    for lo,hi in [(950,955),(980,985),(1022,1027),(1066,1071)]:
        use('P1-B5-INTERVAL-PARTS',range(lo,hi),'three B kinds and attribution-floor argmax/minimum')
    use('P1-B5-INTERVAL-PARTS',[136,137,145,146,154,155,163,164],'per-cell h and B')
    nonleaf('P1-B5-B-SHARE','per-cell B/(h+B)',note='RL-52(5) drops this unregistered derived value and its sentence.')
    select('P1-B5-BATT-LINE',lambda k:k.startswith('DISC.cells[label=battery_assist_cell,'),
           'without-assisted mean/interval, n_r, n_b, per-stratum assisted members',
           'All issued n_r/n_b >=5; below-minimum sentence is not triggered; assist counts remain attributed judgments.')
    select('P1-B5-LOAD-LINE',lambda k:'DISC.cells[label=load_correlated_cell,' in k,
           'line existence, restored units/counts and estimator/refusal',
           'BETA decode requires refusal rows 1064-1065 beside recompute-only rows 647-651; label "recompute only; not compared".')
    use('P1-B5-LOAD-LINE',range(647,652),'BETA decode uncompared recompute numeric line',
        'Mandatory pairing with 1064-1065; recompute only; not compared.')
    for c, phase, token in [('1p7B_decode','decode','Qwen3-1.7B-4bit'),
                            ('1p7B_prefill_p2048','prefill','Qwen3-1.7B-4bit'),
                            ('8B_decode','decode','Qwen3-8B-4bit'),
                            ('8B_prefill_p2048','prefill','Qwen3-8B-4bit')]:
        base = f'RC.dominance.ratios[{token}/{phase}/'
        select('F_'+c+'_cmp_J',lambda k,t=token,p=phase:k==f'RC.floor_cells[{t}/{p}].floor_cmp_j','comparative operative floor')
        fn = 'P1-B5-FN-'+('1p7B' if c.startswith('1p7B') else '8B')+'-'+phase
        select(fn,lambda k,b=base:k.startswith(b) and k.endswith('.n'),'n of each floor form')
        for form,long in [('abs','absolute'),('cmp','comparative')]:
            for pre,suf,leaf in [('R_','','R'),('TERM_A_','_J','denominator_j'),('TERM_B_','_J','numerator_j')]:
                select(pre+c+'_'+form+suf,lambda k,b=base,l=long,z=leaf:k==b+l+'].'+z,
                       'ratio / point denominator / unguarded corner numerator as appropriate')
    use('P1-B5-DOM-FAILED',range(803,865),'all eight R, four R_cm, operands, n and status; branch',
        'Only failed R_cm components print as failures; take the higher precision extension. R_cm 1.7B prefill prints 1.99975 (RL-55).')
    use('P1-B5-DOM-FAILED',range(540,607),'fullest-precision RC dominance/floor operands',
        'RL-55: row 1846 supplies 1.7B prefill R_cm at five decimals, 1.99975; rows 277/502/570/848 are coarser copies.')
    use('P1-B5-DOM-FAILED',[1846],'fullest-precision 1.7B prefill R_cm (RL-55)')
    use('P1-B5-DOM-REFUSED',range(803,863),'component status',
        'All twelve statuses complete and positive denominators: branch 5.4.R is not selected; no refusal code is owed.')
    nonleaf('P1-B5-DOM-REFUSED','refusal component/code in unselected branch 5.4.R',
            note='All twelve issued statuses are complete. No refusal leaf was issued; delete this unselected branch in the second fill.')
    for ns in [range(974,979),range(1006,1011),range(1054,1059),range(1096,1101)]:
        use('P1-B5-XWIN',ns,'per-model/phase delta, widths, boolean and registered word',
            '8B decode differs; the other three agree. RL-55 requires its full registered sentence in results prose.')
    for pack in ('alpha','beta','gamma'):
        select('P1-B5-NEG8',lambda k,p=pack:(f'DISC.window_lines.{p}[' in k and
               any(s in k for s in ('label=neg8_','label=reference_','label=corpus_','label=deciding_membership'))),
               pack+' both family bound terms/screens/allowances; corpus size/drop reasons; realised/planned references; lost names/slots/reasons; spares',
               'No measured/deciding spares and no lost midpoint in these attempts; no lost-midpoint sentence is triggered. Desk-cap and physics-drop IDs are names only.')
    use('P1-B5-MONITOR',range(1160,1163),'ALPHA CPU/reader CPU/probe count',
        'from the registered disclosure record; not independently recomputed')
    use('P1-B5-MONITOR',range(1288,1291),'BETA CPU/reader CPU/probe count',
        'from the registered disclosure record; not independently recomputed')
    use('P1-B5-MONITOR',range(348,351),'GAMMA CPU/reader CPU/probe count',
        'from the registered disclosure record; not independently recomputed')
    def recompute(fid):
        select(fid,lambda k:k.startswith('CMP.counts.') or k.startswith('CMP.bars.') or k.startswith('DERIVE(CMP.comparisons['),
               'Block 5 per-family count, bar, largest difference, agreement',
               'No maximum for categorical families or the empty window_edge_s family. Empty family is not-compared, never agreement.')
        use(fid,[523],'seven uncovered families',
            'Name the uncovered families from RESULTS section 4.2 and their reader labels/checks from REDERIVATION; no claim of complete coverage.')
        name(fid,'Block 5 fixed blind bar-set identity','configs/analysis/b5/recompute_bars.json')
        name(fid,'Block 5 uncovered quantities and reader-check artifact names','docs/analysis/b5/REDERIVATION.md')
        name(fid,'Block 5 disclosed repairs, dates and effect','docs/analysis/b5/DEVIATION-LOG.md',
             'DLE-0 through DLE-10 are committed disclosures; do not claim a repair-free pipeline.')
        later(fid,'Block 6 paragraph: families, counts, bars, largest differences, uncovered quantities, checks and repairs')
    recompute('P1-RECOMPUTE-SUMMARY')
    use('P1-ABS-PART1',list(range(133,169))+list(range(530,536))+[863,864],
        'Block 5 cells/intervals, dominance branch, contrast outcomes/directions/levels',
        'Abstract stays for the freeze under RL-8/RL-47; no single-source support for claim words.')
    later('P1-ABS-PART1','decode and prefill replication words')
    for phase in ('decode','prefill'):
        use('CP-X08-decode-a-conclusion',range(530,533) if phase=='decode' else range(533,536),phase+' outcome/direction/claim level',
            'Conclusion is Ed-owned; this maps available Block 5 inputs only.')
        later('CP-X08-decode-a-conclusion',phase+' replication word')
    use('CP-X02-conclusion',[863,864],'branch-B registered sentence')
    use('CP-X02-conclusion',list(range(843,863)),'failing components with names/ratios/operands/n',
        'Name R_cm 1.7B decode, 1.7B prefill and 8B decode; 8B prefill passes. Do not assert general dominance.')
    use('CP-X02-conclusion',[1846],'fullest-precision 1.7B prefill R_cm (RL-55)')
    for element,file in [('model names/revisions',IDENTITY),('runtime/library version names',IDENTITY),
                         ('1.7B tokenizer identity/digest',PIN+'prefill_prompt_pin.json'),
                         ('8B tokenizer identity/digest','configs/campaigns/d117_floor_qwen3-8b_v5/prefill_pin/prefill_prompt_pin.json'),
                         ('1.7B prompt/chat rendering identity and digest', 'configs/campaigns/d117_floor_qwen3-1p7b_v5/decode_prompt_manifest.json'),
                         ('8B prompt/chat rendering identity and digest', 'configs/campaigns/d117_floor_qwen3-8b_v5/decode_prompt_manifest.json')]:
        name('CP-X01-identity',element,file,
             'Configuration identities, not measured Block 5 outcomes. Follow only committed config files, never absolute source paths.')
    name('CP-X01-length','selection record name and SHA-256',PIN+'selection.json',
         'The committed selection record fixes 2048 tokens; its digest is c694c488...a88222 in registration section 0.3.')
    # Cross-block coordination/publication placeholders are not part of the
    # second-fill assignment; give every Block 5 component a precise reason.
    name('P1-ID-OS','primary-block OS identity',IDENTITY)
    later('P1-ID-OS','per-replication-session OS builds')
    nonleaf('P1-M-RECORD-WIDTH','historical precollection probe record-width median/range',
            file='configs/campaigns/v5_claim_25g83/registration_block5.md',note='Instrument-description input, not a released Block 5 analysis output leaf; outside the RL-52 fill.')
    name('P1-M-ACCEPT','primary pre-capture/bracket/drift constant identities','configs/campaigns/v5_claim_25g83/registration_block5.md')
    later('P1-M-ACCEPT','replication acceptance constants')
    sealed_bytes('P1-M-ACCEPT','BYTES acceptance constants',note='Sealed and outside this Block 5 output ledger; no BYTES source read.')
    use('P1-LEDGER',list(range(885,950))+list(range(1643,1651)),'primary attempts/counts/verdicts/causes')
    later('P1-LEDGER','replication attempts/counting/cause families')
    sealed_bytes('P1-LEDGER','BYTES attempts/counting/cause families',note='Sealed and outside this Block 5 output ledger.')
    name('P1-DEV-LIST','primary errata/deviations/interpretations/repairs, dates, applicability and blind status','docs/analysis/b5/DEVIATION-LOG.md',
         'Also primary SEAL_RECORD.md and decision_log.md D-188 through D-190; disclosure text, not outcome numbers.')
    later('P1-DEV-LIST','replication section 17 disclosures')
    sealed_bytes('P1-DEV-LIST','BYTES addenda',note='Sealed and outside this Block 5 output ledger.')
    name('P1-RELEASE','primary release event date and bound record digests','docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md')
    later('P1-RELEASE','replication release date/digests')
    sealed_bytes('P1-RELEASE','BYTES commitment/release dates/digests',note='Outside the Block 5 output ledger; do not infer from operational text.')
    recompute('P1-RECOMPUTE')
    name('P1-AVAIL','primary registrations/code/seal identities and release binding','docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md')
    nonleaf('P1-AVAIL','authorized public archive locators, released manifest and raw-capture publication scope',
            note='Publication/release decision, not a registered analysis output; never infer a locator or publish custody.')
    later('P1-AVAIL','replication availability/released evidence')
    sealed_bytes('P1-AVAIL','BYTES availability/released evidence',note='Sealed and outside this Block 5 output ledger.')
    if {r['placeholder'] for r in out} != pending|mixed:
        raise ValueError('coverage placeholder set differs')
    pairs = [(r['placeholder'],r['element']) for r in out]
    if len(pairs) != len(set(pairs)):
        raise ValueError('duplicate coverage element')
    return sorted(out,key=lambda r:(int(r['paper_line']),r['placeholder'],r['element']))


def encoded(rows):
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,FIELDS,delimiter='\t',lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return stream.getvalue().encode()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    with (HERE/'rederivation.tsv').open() as stream:
        ledger={n:r for n,r in enumerate(csv.DictReader(stream,delimiter='\t'),2)}
    rows=build(paper_text(),ledger)
    tracked=set(subprocess.run(['git','ls-files'],cwd=REPO,check=True,capture_output=True,text=True).stdout.splitlines())
    for row in rows:
        if row['committed_file'] and row['committed_file'] not in tracked:
            raise ValueError('committed-file reason names an untracked file: '+row['committed_file'])
    raw=encoded(rows);target=HERE/'fill_coverage.tsv'
    if args.write:target.write_bytes(raw)
    elif target.read_bytes()!=raw:raise ValueError('coverage table differs from explicit element/row map')
    gone, left = check_working_paper((REPO/PAPER_PATH).read_text(), rows)
    print('PASS: coverage',len(rows),'elements;',len({r['placeholder'] for r in rows}),'placeholders;',
          dict(Counter(r['reason'] or 'ledger row' for r in rows)))
    print('PASS: working paper:',gone,'mapped placeholders filled, deleted or dropped;',left,'still pending')


if __name__=='__main__':
    main()
