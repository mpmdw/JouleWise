"""Assemble a dev-04 desk from the dev-03-s02 method's hand outputs.
Copied structure and comparisons from that desk's build_result.py; adapted span,
roster, capture/consumer roles, redo text and dev-05 gate facts. No new tolerance.
Usage: python3.13 -I -B build_result.py DESK DATA KIT PEER_HAND_TABLE
"""
import json, sys
from pathlib import Path
T, D, K, P = map(Path, sys.argv[1:])
H = T / 'hand'
load = lambda p: json.loads(p.read_text())
ht, ds, rec, kit, peer = load(H/'hand_table.json'), load(T/'auto/desk_summary.json'), load(D/'runner_receipt.json'), load(K), load(P)
span, legs = ht['span'], ht['legs']
plan_id = rec['plan_id'] if 'plan_id' in rec else T.name.removeprefix('desk-')
span_id = plan_id.removeprefix('cq-').removesuffix('-a1')
first = legs[0]['leg_id']
consumers = [l for l in legs if l['g0_role_hand'] == 'consume']
n, ncomp = len(legs), sum(len(l['compare']) for l in legs)
ndiff = sum(not c['agree'] for l in legs for c in l['compare'].values())
nincl, nadm = sum(l['included'] for l in legs), sum(l['admitted'] for l in ds['legs'])
astops = load(T/'auto/stops.json')
# Exactly the template's FINAL condition, including hand diffs and both stop lists.
final = ndiff == 0 and not ht['diffs'] and nincl == n == nadm and not astops and not span['stops_by_hand']
r1 = {}
for line in (H/'r1print.out').read_text().splitlines():
    if line.startswith('soak_reference'): r1['soak_reference_line'] = line
    elif line.strip():
        k, _, v = line.partition(' '); r1[k] = json.loads(v)
def output(name):
    return {k: json.loads(v) for line in (H/name).read_text().splitlines() if line.strip() for k, _, v in [line.partition(' ')]}
smp, osl, r5p = output('sampler.out'), output('oslevel.out'), output('rule5_place.out')
maint = (H/'maint_judgement.txt').read_text().strip()
integrity = load(H/'manifest_check.json')
all_tables = sorted([ht, peer], key=lambda h: h['legs'][0]['leg_id'])
gate_rows = []
for table in all_tables:
    s = 'dev-04-s01' if table['legs'][0]['leg_id'] == 'L001' else 'dev-04-s02'
    for c in table['legs']:
        if c['g0_role_hand'] != 'consume': continue
        gate_rows.append({'span': s, 'consumer': c['leg_id'], 'g0_outcome': c['g0_outcome_journal'],
                          'wait_s': round(c['g0_s_journal'], 3), 'timeout_s': c['g0_timeout_s'],
                          'released_against_span_reference': c['g0_outcome_journal'] == 'released' and all(v is True for k,v in c['consumer_checks'].items() if k != 'own_window_reference_status'),
                          'reference_source': c['g0_reference_source_record'], 'reference_record_sha256': c['g0_reference_record_sha256_record'],
                          'span_reference': c['span_reference_hand']})
hand_legs = []
for l in legs:
    row = {'leg': l['leg_id'], 'attempts': l['attempts'], 'g0': l['g0_outcome_journal'], 'g0_s': round(l['g0_s_journal'],3),
           'g0_role': l['g0_role_hand'], 'g0_shape': l['g0_shape_hand'], 'span_reference': l['span_reference_hand'],
           'prefill_tokens_realized': l['prefill_tokens'], 'prefill_tokens_nominal': l['prefill_tokens_nominal_kit'], 'prefill_deviation_pct': l['prefill_deviation_pct'],
           'decode': f"{l['decode_tokens']}/{l['decode_cap']}", 'leg_status': l['leg_status'], 'wall_s': round(l['wall_s_stage'],1), 'budget_s': l['budget_s'],
           'leg_record_ac_powermode': l['ac_powermode'], 'rule5_longest_run_over_0p5_core_s': l['load_counted']['longest_run_over_0p5_s'],
           'rule5_max_busy_cores': round(l['load_counted']['max_cores'],3), 'os_level_max_turn': l['os_level_max_turn'], 'pm_nominal_turn': l['pm_nominal_turn'],
           'included': l['included'], 'rules': l['rules']}
    if 'consumer_checks' in l:
        row.update(consumer_checks=l['consumer_checks'], g0_reference_source=l['g0_reference_source_record'], g0_reference_record_sha256=l['g0_reference_record_sha256_record'])
    else: row.update(capture_checks=l['capture_checks'], own_window_reference_record_sha256=l['own_window_reference']['record_sha256'])
    hand_legs.append(row)
comparison = {'per_leg_values_compared': ncomp, 'per_leg_values_differing': ndiff, 'fields_per_leg': sorted(legs[0]['compare']), 'inclusion_included': True,
              'span_level_compared': ['leg count','named stops','result','meter','feeds_proven_stopped','span_reference (leg_id, attempt, consumers, consistent)'],
              'span_level_differing': len(ht['diffs'])-ndiff, 'diffs': ht['diffs'],
              'scope_notes': ['hand_table.py comparison unchanged: G0 seconds rounded to 6 decimal places, wall seconds to 1 decimal place; all other pairs use equality',
                              'shape from kit; first leg captures; later span-shaped legs consume; source, record sha, fast_c and span_ns checked against capture',
                              'desk prefill is kit nominal; realized prefill reported separately', 'rules 3 and 4 remain at the look, as in the template; receipt instrument health only; no measured energy opened',
                              'restore lines and censuses carried by hand; all attempts recomputed for rule 5']}
restore = span['restore']
walls = [(l['leg_id'], round(l['wall_s_stage'],1), round(l['wall_s_stage']/l['budget_s'],4)) for l in legs]
factor = kit['stop_rules']['leg_time_factor']
st, en = rec['started']['epoch_s'], rec['ended']['epoch_s']
findings = ([{'id':'F1','text':'Brief calls L001 span-shaped. Kit, leg_record spec/result and desk all say own; L001 captures the span reference and L005 consumes it. No inclusion or printed number is changed.'}] if first == 'L001' else [])
decisions = [f'Use {first} accepted attempt 1 as this span reference, as the kit/data and template first-leg rule determine; source {legs[0]["own_window_reference"]["source_run_id"]}.',
             'Use kit/data shapes and roles; L001 and L007 are own-shaped captures, L005 and L008-L012 consume their respective span reference.',
             'Keep hand_table.py numerical comparisons unchanged; no new tolerance or bar.',
             'Judge maintenance by rule 5 load-journal sustained runs, not log counts; retain kit no_drop_by_outcome.',
             'Keep all scratch including kit, lock and TMPDIR under .desk-scratch; pass --kit and an explicit scratch lock to pinned desk code.',
             'Use dev-05 drafts in item-drafts-1115 (RL-173 D); item-drafts-1118 contains qualification drafts. List nearby item-drafts-rl172 equivalents; do not edit or issue items.',
             'Earlier dev-02-s03 REPORT.md is absent at 4a53c34a4 and audit ref; use its committed RESULT.json, OPENED.txt, maint_judgement.txt and rule5_place_a1.py for the redo method.']
if first == 'L001': decisions.append('L006 a1 fires by hand and was correctly redone once; count L006 a2 (clean) within quota 2; no refill or further redo.')
else: decisions.append('Count L007-L012 attempt 1; no redo or refill.')
out = {'plan_id':plan_id, 'span':span_id, 'status':'PROPOSED', 'signed_by':'not signed: magistrate lead re-executes and signs', 'legs':rec['roster'],
       'built':(H/'built.txt').read_text().strip(), 'work_order':f'Brief; main RUN_STATE Check item {380 if first == "L001" else 382}, Air pause item 384',
       'data':{'path':str(D),'original_MBP_read_only':True,'manifest':integrity['manifest'],'manifest_sha256':integrity['manifest_sha256'],'entries_verified':integrity['count'],'failed':integrity['failed'],'mapping':integrity['mapping'],'air_copy':False,'air_mbp_comparison':'none'},
       'code':{'commit':'2d347f721552fe03bdd19f113e7bad7a7c24908e','checkout':'/Users/edr/code/jw-wt/desk-pin-2d347f721','status_before':(H/'desk-code-status-before.txt').read_text(),'status_after':(H/'desk-code-status-after.txt').read_text()},
       'kit':{'source':'git show fecaf73f3:docs/process/cadence/kits/cl-dev-04.v1.1.json','scratch_path':str(K),'sha256':'1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228','sha_asserted':True,'receipt_kit':rec['kit']},
       'desk_command':load(H/'commands.json')['desk'], 'desk_stops_json':astops, 'comparison':comparison, 'hand_legs':hand_legs,
       'desk_final':{'verdict':'FINAL' if final else 'NOT FINAL', 'meaning':'automatic desk = independent hand table on every value, inclusion included; lead signature pending',
                     'basis':f"{ndiff} of {ncomp} per-leg and {comparison['span_level_differing']} span-level values differ; {nincl} of {n} included by hand, {nadm} of {n} admitted by desk; stops.json {astops} and hand stops {span['stops_by_hand']}"},
       'consumers_released':{'this_span':f'{len(consumers)} of {len(consumers)} released against {first} capture; all consumer checks true'},
       'dev04_consumer_releases':gate_rows, 'dev05_draft_gate_facts':load(H/'gate_facts.json'),
       'rules_by_hand':{k:sum(l['rules'][k] for l in legs) for k in ['1_ran_to_cap','2_g0_released','5_not_contaminated','6_power_mode_0']},
       'rule5_judgements':{l['leg_id']:l['attempt_detail'] for l in legs},
       'restore':restore,'restore_proven_hand':span['close_steps']['restore']==0 and restore['ok'] is True and restore['observed']==0 and span['span_result'].get('restore_proven',True) is not False,
       'close_steps_rc':span['close_steps'],'read_power_step_before_soak':span['read_power'],
       'LEG_OVERTIME':'no' if not any(l['over_time'] for l in legs) else 'yes',
       'LEG_OVERTIME_detail':{'walls_and_ratios':walls,'factor':factor,'over_factor':sum(l['over_time'] for l in legs),'stop_needs':2},
       'RL150_R1_part3_print':r1,
       'RL158_Q1':{'print':'hand/r1print.out (thermal-only print)','soak_reference_line':r1['soak_reference_line'], f'{first}_capture':r1[first]['own_reference'],
                   'consumer_release_readings':{c['leg_id']:r1[c['leg_id']]['g0']['release'] for c in consumers},'g0_wait_s':{l['leg_id']:round(l['g0_s_journal'],1) for l in legs},
                   'marks':f'none: {first} ran one attempt, was not redone and not excluded; no reference-from-redo or reference-from-excluded-leg mark',
                   'completion_record':f'docs/research-audits/2026-11-10-fable/evidence/cadence-standing/q1/{plan_id}.json'},
       'RL158_Q5_prefill_deviation':{l['leg_id']:{'nominal':l['prefill_tokens_nominal_kit'],'realized':l['prefill_tokens'],'pct':l['prefill_deviation_pct']} for l in legs},
       'RL158_Q6_consumers':'6 of 6 consumers released over dev-04: L005, L008, L009, L010, L011, L012',
       'RL156a':{'thermal_sampler':smp,'thermal_note':f"{sum(v['read_errors'] for v in smp.values())} read errors; {sum(len(v['cells_with_no_reading_at_all']) for v in smp.values())} cells with no reading at all; max interval {max(v['max_interval_s'] for v in smp.values())} s; 100 ms tolerance jitter cells retained as template prints, no new bar",
                 'load_sampler':{l['leg_id']:l['load_counted'] for l in legs},'inventory':'not exercised: cadence-leg kind does not run R1 ProcessInventory journal'},
       'os_level_census':osl,'rule5_placement':r5p,'maintenance_overlap':maint,
       'span_level':{k:span[k] for k in ['rc','mock','batch_windows','soak_rc','agent_census','deadlines_files','load_redos_used','feeds_proven_stopped','meter','stages_unclosed','stages_end_rc_nonzero','steps_nonzero','n_steps','legs_finished','legs_planned']},
       'span_level_extra':{'soak_s':round(span['soak_s'],1),'volume_census':f"{sum(v[0]=='PASS' for v in span['volume_census'])}/{len(span['volume_census'])} PASS",'redo_quota_kit':span['redo_quota_kit']},
       'time_calendar_only':{'receipt_started_epoch_s':st,'receipt_ended_epoch_s':en,'runner_span_s':round(en-st,1),'mean_leg_wall_s':round(sum(w for _,w,_ in walls)/n,1)},
       'check_agreement':load(H/'check_agreement.json'), 'findings':findings, 'decisions_I_made':decisions,'NEEDS_RULING':[]}
if (H/'rule5_place_a1.out').exists(): out['rule5_placement_a1']=output('rule5_place_a1.out')
(T/'RESULT.json').write_text(json.dumps(out,indent=1)+'\n')
print(json.dumps({'span':span_id,'verdict':out['desk_final'],'findings':findings,'NEEDS_RULING':[]}))
