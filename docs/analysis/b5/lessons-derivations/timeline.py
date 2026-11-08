import json, datetime as dt
from times import win, est, T, PDT
UTC=dt.timezone.utc
def iso(t): return t.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
def loc(t): return t.astimezone(PDT).strftime('%a %Y-%m-%d %H:%M PDT')
req={'1.7B decode':2.08,'1.7B prefill':2.96,'8B decode':6.77,'8B prefill':9.82,'Qwen2.5-1.5B reference':1.6}
losses=[
 # window, unit, trigger member(s), arm, ordinal(s) for timing, codes
 ('alpha','prefill abba b07','(one member, single-model window)','1.7B prefill',(84,87),['contention.request_overlap']),
 ('alpha','prefill abba b10','(one member)','1.7B prefill',(96,99),['contention.request_overlap']),
 ('alpha','prefill abs r08','r08','1.7B prefill',(57,57),['contention.request_overlap']),
 ('alpha','decode abba b05','(one member)','1.7B decode',(26,29),['member.admission_aborted']),
 ('alpha','decode abba b08','(one member)','1.7B decode',(38,41),['member.admission_aborted']),
 ('beta','decode abs r03','r03','8B decode',(2,2),['contention.request_overlap']),
 ('beta','decode abs r06','r06','8B decode',(5,5),['contention.request_overlap']),
 ('beta','decode abs r10','r10','8B decode',(9,9),['contention.request_overlap']),
 ('beta','decode abba b01','(one member)','8B decode',(10,13),['member.admission_aborted']),
 ('beta','decode abba b04','(one member)','8B decode',(22,25),['member.anchor_not_bounded']),
 ('beta','decode abba b10','(one member)','8B decode',(46,49),['contention.request_overlap']),
 ('beta','prefill abs r01','r01','8B prefill',(50,50),['member.admission_aborted']),
 ('beta','prefill abba b03','(one member)','8B prefill',(68,71),['contention.request_overlap']),
 ('beta','prefill abba b07','(one member)','8B prefill',(84,87),['contention.request_overlap']),
 ('beta','prefill abba b08','(one member)','8B prefill',(88,91),['contention.request_overlap']),
 ('beta','prefill abba b09','(one member)','8B prefill',(92,95),['contention.request_overlap']),
 ('gamma','decode b01','b01-b1','8B decode',(1,1),['contention.request_overlap']),
 ('gamma','decode b05','b05-b1','8B decode',(17,17),['contention.request_overlap']),
 ('gamma','decode b06','b06-b2','8B decode',(22,22),['member.anchor_not_bounded','member.whole_window_member_failure']),
 ('gamma','decode b09','b09-b2','8B decode',(34,34),['member.admission_aborted']),
 ('gamma','prefill b01','b01-b1','8B prefill',(41,41),['member.admission_aborted']),
 ('gamma','prefill b01','b01-a2','1.7B prefill',(43,43),['member.admission_aborted']),
 ('gamma','prefill b04','b04-a1','1.7B prefill',(52,52),['contention.request_overlap']),
 ('gamma','prefill b06','b06-b2','8B prefill',(62,62),['contention.request_overlap']),
 ('gamma','prefill b09','b09-b1','8B prefill',(73,73),['contention.request_overlap']),
 ('gamma','prefill b09','b09-a2','1.7B prefill',(75,75),['member.admission_aborted']),
 ('gamma','prefill b10','b10-b1','8B prefill',(77,77),['contention.request_overlap']),
]
rows=[]
for w,unit,trig,arm,(o1,o2),codes in losses:
    n1,t1,per=est(w,o1); n2,t2,_=est(w,o2)
    lo=t1-dt.timedelta(seconds=per/2); hi=t2+dt.timedelta(seconds=per/2)
    rows.append({'window':w,'unit':unit,'trigger':trig,'arm':arm,'stage':n1,'ordinals':[o1,o2],
                 'within_stage_index':[o1-[s for s in win[w] if s[0]==n1][0][3], o2-[s for s in win[w] if s[0]==n1][0][3]],
                 'request_s':req[arm],'codes':codes,
                 'est_window_utc':[iso(lo),iso(hi)],'est_window_local':[loc(lo),loc(hi)]})
refs=[('alpha','neg8-window-end-r2','end reference','~Fri 21:52 PDT'),('beta','neg8-refcorpus-r03/r05/r08/r12/r17','corpus (5 of 18)','corpus block near window start; per-member times not derivable here'),
      ('gamma','neg8-refcorpus-r05','corpus','~Sun 21:41 PDT'),('gamma','neg8-refcorpus-r16','corpus','~Sun 22:16 PDT'),
      ('gamma','neg8-window-start-r2','start reference','~Sun 22:25 PDT'),('gamma','neg8-window-end-r1','end reference','~Mon 02:04 PDT')]
out={'schema':'joulewise.b5_loss_timeline.v1',
 'provenance':'Derived ONLY from /Users/edr/jw-b5-custody/dry-m (disclosure lines 77be1a3e…, released text 1945410f…, EXC a9954365…, supply-census campaign-manifest file NAMES, rereduced window durations) and release-check-final-20261108T0942Z/recompute.json member n_overlap counts. No energy value. No night-* path read.',
 'timing_method':'Stage start = campaign manifest timestamp in the supply census; stage end = next campaign start; member time = uniform interpolation over the stage (members are 144-179 s apart). Error about +-1 member (+-2.5 min) for single members and the whole quad span (~10 min) for ALPHA/BETA quad lines, which do not name the triggering member. Local time is PDT (UTC-7; Block 5 ran before the 2026-11-01 DST change).',
 'stage_schedule':{w:[{'stage':n,'start_utc':iso(s),'end_utc':iso(e),'start_local':loc(s),'end_local':loc(e),'first_ordinal':f,'members':m,'s_per_member':round((e-s).total_seconds()/m)} for n,s,e,f,m in win[w]] for w in win},
 'request_s_by_arm':req,
 'losses':rows,'reference_and_corpus_contention_losses':[{'window':a,'members':b,'role':c,'time':d} for a,b,c,d in refs],
 'flag_counts':{'alpha':{'contention.request_overlap':4,'member.admission_aborted':2},'beta':{'contention.request_overlap':14,'member.admission_aborted':3,'member.anchor_not_bounded':1},'gamma':{'contention.request_overlap':10,'member.admission_aborted':4,'member.anchor_not_bounded':1}},
 'attempt_physics_in_span':{'note':'DISC.block_lines attempt_history: PHYSICS_IN_SPAN family count per attempt (contention.request_overlap plus member.span_unknown)',
   'alpha-a1-20261008T2201Z':18,'alpha-a3-20261009T0644Z':8,'alpha-a1-20261009T2312Z':6,'beta-a1-20261010T0742Z':13,'beta-a2-20261010T1756Z (43 of 125 collected)':12,'beta-a4-20261010T2237Z':12,'beta-a5-20261011T0739Z':14,'beta-a6-20261011T2011Z':17,'gamma-a1-20261012T0420Z':14},
 'labels_note':'These are loss labels for the analysed attempts, not replayable traces. The replayable corpus (contention_interval frames, offender process names, CPU-s/s, episode durations) needs extract_b5_guard_corpus.py run on the harvest archives by an authorized reader; see README.md.'}
json.dump(out,open('../../../ops/guard-replay-corpus/b5/b5-loss-timeline.json','w'),indent=1)
for r in rows: print(r['window'],r['unit'],r['trigger'],r['codes'][0],r['within_stage_index'],r['est_window_local'])
