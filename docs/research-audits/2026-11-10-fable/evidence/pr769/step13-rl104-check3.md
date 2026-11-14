# RL-104 check 3 (item-83 ruling-3 hand check), Block 6 copied disclosures

Reader: Sonnet 5.5 reader seat, for the laptop lead
Time: Fri Nov 13 18:58:48 PST 2026
Block 6 released 2026-11-13 18:54:57 PST (PR #769, merge 66469ccf4); restricted files read after release. Read-only; nothing edited or run beyond head/wc/small python3.13 -I snippets and `zstd -dc` to stdout.

## Result

72 of 72 (family x session) rows PASS; 0 FAIL. 72 of 72 digests match. The R3-table and run-input file names agree for all 8 families in all 9 sessions (no deviation-log line).

## Method

- Files from run-inputs-block-2.json `sessions[*].copied_records` under each session archive. battery.jsonl and thermal.jsonl exist in the archive only as `.jsonl.zst` (archive compression); I decompressed to stdout and hashed the decompressed bytes.
- Digest rule: run-inputs `files` carries digests only for derived/ and withheld/ paths (derived/flags.jsonl, withheld/b6-neg8.json). For sources/ paths there is no per-file digest in the run-input `files` map, so I used `archive/sources/SHA256SUMS` (whose own sha256 equals the run-input `sha256sums_sha256` in all 9 sessions) and, for battery/thermal, also `archive.desk/compression.jsonl` (original sha256, equal to SUMS in all cases). "yes" = `shasum -a 256` of the file equals that digest.
- Program cross-check: for every file, restricted.json `sessions[sid].copied_disclosures.families[fam][i]` has `path`, `sha256`, `record`; the sha256 equals the file digest and the `record` string is byte-identical to the file (decompressed) in all 72 rows. No disagreement.
- Disclosure tests (per family): monitor_cost = monitor.jsonl journal has 1 session_start, 1 session_end and N `kind=cost` records each with cpu_self_s and maxrss; battery_phase = battery.jsonl journal (module battery) with session_start/end and `reading` records; subject_temperature = thermal.jsonl journal (module thermal) with `reading` records carrying `level`; arm_host = arm.json has decision, census, census_at_go, identity and 6 module verdict lists, arm_collectors.json has a results list; reference_history = flags.jsonl parses with code/klass fields (neg8.* flags counted) and b6-neg8.json has verdict, reference_run_ids, survivors; attempt_history = idle_wait.jsonl records have run_id/outcome/wait_s and chain-stages.jsonl records have stage_id/rc; g10_history = hazard_result.json has `g10`, attempt, verdict, stage_reached; block5_codes_carried = flags.jsonl records each with code, klass, scope, flag_id.

## Family summary

| family | files | PASS | FAIL |
|---|---|---|---|
| monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl | 9 | 0 |
| arm_host | sources/night-custody/hazards/arm.json, sources/night-custody/night/arm_collectors.json | 9 | 0 |
| battery_phase | sources/night-custody/hazards/monitor/battery.jsonl | 9 | 0 |
| subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl | 9 | 0 |
| reference_history | derived/flags.jsonl, withheld/b6-neg8.json | 9 | 0 |
| attempt_history | sources/night-custody/collection/idle_wait.jsonl, sources/night-custody/night/chain-stages.jsonl | 9 | 0 |
| g10_history | sources/night-custody/night/hazard_result.json | 9 | 0 |
| block5_codes_carried | derived/flags.jsonl | 9 | 0 |

## 72-row table

| session | family | file(s) (bytes) | digest match | holds disclosure | evidence |
|---|---|---|---|---|---|
| r1-alpha | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (364093) | yes | PASS | 631 recs: {'session_start': 1, 'cost': 628, 'event': 1, 'session_end': 1}; last cost cpu_self_s=68.398082 maxrss=33406976 battery_polls=3759 |
| r1-beta | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (386656) | yes | PASS | 670 recs: {'session_start': 1, 'cost': 667, 'event': 1, 'session_end': 1}; last cost cpu_self_s=71.422908 maxrss=33456128 battery_polls=3992 |
| r1-gamma | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (324163) | yes | PASS | 562 recs: {'session_start': 1, 'cost': 559, 'event': 1, 'session_end': 1}; last cost cpu_self_s=58.879998 maxrss=33341440 battery_polls=3343 |
| r2-beta | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (385798) | yes | PASS | 672 recs: {'session_start': 1, 'cost': 669, 'event': 1, 'session_end': 1}; last cost cpu_self_s=70.56970799999999 maxrss=33193984 battery_polls=4008 |
| r2-gamma | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (328893) | yes | PASS | 570 recs: {'session_start': 1, 'cost': 567, 'event': 1, 'session_end': 1}; last cost cpu_self_s=60.063658000000004 maxrss=33095680 battery_polls=3393 |
| r3-alpha | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (364795) | yes | PASS | 632 recs: {'session_start': 1, 'cost': 629, 'event': 1, 'session_end': 1}; last cost cpu_self_s=67.379216 maxrss=33275904 battery_polls=3765 |
| r3-beta | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (387407) | yes | PASS | 675 recs: {'session_start': 1, 'cost': 672, 'event': 1, 'session_end': 1}; last cost cpu_self_s=71.014957 maxrss=33423360 battery_polls=4025 |
| r3-gamma | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (324762) | yes | PASS | 563 recs: {'session_start': 1, 'cost': 560, 'event': 1, 'session_end': 1}; last cost cpu_self_s=60.056044 maxrss=33210368 battery_polls=3353 |
| r4-alpha | monitor_cost | sources/night-custody/hazards/monitor/monitor.jsonl (366810) | yes | PASS | 636 recs: {'session_start': 1, 'cost': 633, 'event': 1, 'session_end': 1}; last cost cpu_self_s=67.781465 maxrss=33325056 battery_polls=3791 |
| r1-alpha | arm_host | sources/night-custody/hazards/arm.json (180353); sources/night-custody/night/arm_collectors.json (2937) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r1-beta | arm_host | sources/night-custody/hazards/arm.json (180308); sources/night-custody/night/arm_collectors.json (2928) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r1-gamma | arm_host | sources/night-custody/hazards/arm.json (180457); sources/night-custody/night/arm_collectors.json (2967) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r2-beta | arm_host | sources/night-custody/hazards/arm.json (180374); sources/night-custody/night/arm_collectors.json (2928) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r2-gamma | arm_host | sources/night-custody/hazards/arm.json (180405); sources/night-custody/night/arm_collectors.json (2967) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r3-alpha | arm_host | sources/night-custody/hazards/arm.json (178560); sources/night-custody/night/arm_collectors.json (2937) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r3-beta | arm_host | sources/night-custody/hazards/arm.json (180382); sources/night-custody/night/arm_collectors.json (2928) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r3-gamma | arm_host | sources/night-custody/hazards/arm.json (179266); sources/night-custody/night/arm_collectors.json (2967) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r4-alpha | arm_host | sources/night-custody/hazards/arm.json (986941); sources/night-custody/night/arm_collectors.json (2935) | yes | PASS | arm.json decision=GO census.clean=True at_go.clean=True verdicts={'battery': 'PASS', 'clock': 'PASS', 'contention': 'PASS', 'disk': 'PASS', 'instrument': 'PASS', 'thermal': 'PASS'} unmeasured=[]; arm_collectors call=1 ran_by=arm results=1 |
| r1-alpha | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (10371727, zst) | yes | PASS | 19110 recs: {'session_start': 1, 'reading': 19108, 'session_end': 1}; sources {'smc': 18794, None: 314}; span 5.22 h |
| r1-beta | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (11010433, zst) | yes | PASS | 20292 recs: {'session_start': 1, 'reading': 20290, 'session_end': 1}; sources {'smc': 19957, None: 333}; span 5.54 h |
| r1-gamma | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (9221595, zst) | yes | PASS | 16996 recs: {'session_start': 1, 'reading': 16994, 'session_end': 1}; sources {'smc': 16715, None: 279}; span 4.64 h |
| r2-beta | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (11036157, zst) | yes | PASS | 20375 recs: {'session_start': 1, 'reading': 20373, 'session_end': 1}; sources {'smc': 20038, None: 335}; span 5.57 h |
| r2-gamma | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (9359683, zst) | yes | PASS | 17250 recs: {'session_start': 1, 'reading': 17248, 'session_end': 1}; sources {'smc': 16965, None: 283}; span 4.71 h |
| r3-alpha | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (10385469, zst) | yes | PASS | 19137 recs: {'session_start': 1, 'reading': 19135, 'session_end': 1}; sources {'smc': 18821, None: 314}; span 5.23 h |
| r3-beta | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (11081913, zst) | yes | PASS | 20461 recs: {'session_start': 1, 'reading': 20459, 'session_end': 1}; sources {'smc': 20123, None: 336}; span 5.59 h |
| r3-gamma | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (9248763, zst) | yes | PASS | 17045 recs: {'session_start': 1, 'reading': 17043, 'session_end': 1}; sources {'smc': 16763, None: 280}; span 4.66 h |
| r4-alpha | battery_phase | sources/night-custody/hazards/monitor/battery.jsonl (10461534, zst) | yes | PASS | 19273 recs: {'session_start': 1, 'reading': 19271, 'session_end': 1}; sources {'smc': 18954, None: 317}; span 5.26 h |
| r1-alpha | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1541421, zst) | yes | PASS | 3761 recs: {'session_start': 1, 'reading': 3759, 'session_end': 1}; thermal level counts {0: 3759}; span 5.22 h |
| r1-beta | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1636950, zst) | yes | PASS | 3994 recs: {'session_start': 1, 'reading': 3992, 'session_end': 1}; thermal level counts {0: 3992}; span 5.54 h |
| r1-gamma | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1370861, zst) | yes | PASS | 3345 recs: {'session_start': 1, 'reading': 3343, 'session_end': 1}; thermal level counts {0: 3343}; span 4.64 h |
| r2-beta | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1639496, zst) | yes | PASS | 4010 recs: {'session_start': 1, 'reading': 4008, 'session_end': 1}; thermal level counts {0: 4008}; span 5.57 h |
| r2-gamma | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1391361, zst) | yes | PASS | 3395 recs: {'session_start': 1, 'reading': 3393, 'session_end': 1}; thermal level counts {0: 3393}; span 4.71 h |
| r3-alpha | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1543881, zst) | yes | PASS | 3767 recs: {'session_start': 1, 'reading': 3765, 'session_end': 1}; thermal level counts {0: 3765}; span 5.23 h |
| r3-beta | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1646449, zst) | yes | PASS | 4027 recs: {'session_start': 1, 'reading': 4025, 'session_end': 1}; thermal level counts {0: 4025}; span 5.59 h |
| r3-gamma | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1374961, zst) | yes | PASS | 3355 recs: {'session_start': 1, 'reading': 3353, 'session_end': 1}; thermal level counts {0: 3353}; span 4.66 h |
| r4-alpha | subject_temperature | sources/night-custody/hazards/monitor/thermal.jsonl (1554541, zst) | yes | PASS | 3793 recs: {'session_start': 1, 'reading': 3791, 'session_end': 1}; thermal level counts {0: 3791}; span 5.26 h |
| r1-alpha | reference_history | derived/flags.jsonl (153228); withheld/b6-neg8.json (6090) | yes | PASS | flags.jsonl 167 flags, neg8.* flags {'neg8.corpus_member_dropped': 3, 'neg8.reference_lost': 1}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r1-beta | reference_history | derived/flags.jsonl (147269); withheld/b6-neg8.json (6069) | yes | PASS | flags.jsonl 162 flags, neg8.* flags {'neg8.corpus_member_dropped': 2}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r1-gamma | reference_history | derived/flags.jsonl (137913); withheld/b6-neg8.json (6094) | yes | PASS | flags.jsonl 145 flags, neg8.* flags {'neg8.corpus_member_dropped': 1}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r2-beta | reference_history | derived/flags.jsonl (169929); withheld/b6-neg8.json (5867) | yes | PASS | flags.jsonl 183 flags, neg8.* flags {'neg8.screen_failed': 1}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r2-gamma | reference_history | derived/flags.jsonl (143296); withheld/b6-neg8.json (6088) | yes | PASS | flags.jsonl 151 flags, neg8.* flags {'neg8.corpus_member_dropped': 3, 'neg8.midpoint_lost': 1, 'neg8.reference_lost': 1}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r3-alpha | reference_history | derived/flags.jsonl (160351); withheld/b6-neg8.json (6094) | yes | PASS | flags.jsonl 173 flags, neg8.* flags {'neg8.corpus_member_dropped': 3}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r3-beta | reference_history | derived/flags.jsonl (180216); withheld/b6-neg8.json (6075) | yes | PASS | flags.jsonl 190 flags, neg8.* flags {}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r3-gamma | reference_history | derived/flags.jsonl (139595); withheld/b6-neg8.json (6092) | yes | PASS | flags.jsonl 146 flags, neg8.* flags {'neg8.corpus_member_dropped': 1, 'neg8.reference_lost': 1}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r4-alpha | reference_history | derived/flags.jsonl (162954); withheld/b6-neg8.json (6092) | yes | PASS | flags.jsonl 175 flags, neg8.* flags {'neg8.corpus_member_dropped': 2, 'neg8.reference_lost': 1}; b6-neg8.json verdict=passed reference_run_ids=3 survivors=3 corpus_clean_n=12 reason=None |
| r1-alpha | attempt_history | sources/night-custody/collection/idle_wait.jsonl (14548); sources/night-custody/night/chain-stages.jsonl (2607) | yes | PASS | idle_wait 125 recs outcomes {'admitted': 125} budget_exhausted {False: 125}; chain-stages 19 stages rc {0: 17, 1: 2} last=alpha-post-calibration.session-status |
| r1-beta | attempt_history | sources/night-custody/collection/idle_wait.jsonl (14362); sources/night-custody/night/chain-stages.jsonl (2588) | yes | PASS | idle_wait 125 recs outcomes {'admitted': 125} budget_exhausted {False: 125}; chain-stages 19 stages rc {0: 18, 1: 1} last=beta-post-calibration.session-status |
| r1-gamma | attempt_history | sources/night-custody/collection/idle_wait.jsonl (13699); sources/night-custody/night/chain-stages.jsonl (2686) | yes | PASS | idle_wait 107 recs outcomes {'admitted': 107} budget_exhausted {False: 107}; chain-stages 19 stages rc {0: 19} last=gamma-calibration-post.session-status |
| r2-beta | attempt_history | sources/night-custody/collection/idle_wait.jsonl (14376); sources/night-custody/night/chain-stages.jsonl (2588) | yes | PASS | idle_wait 125 recs outcomes {'admitted': 125} budget_exhausted {False: 125}; chain-stages 19 stages rc {0: 16, 1: 3} last=beta-post-calibration.session-status |
| r2-gamma | attempt_history | sources/night-custody/collection/idle_wait.jsonl (13713); sources/night-custody/night/chain-stages.jsonl (2686) | yes | PASS | idle_wait 107 recs outcomes {'admitted': 107} budget_exhausted {False: 107}; chain-stages 19 stages rc {0: 19} last=gamma-calibration-post.session-status |
| r3-alpha | attempt_history | sources/night-custody/collection/idle_wait.jsonl (14548); sources/night-custody/night/chain-stages.jsonl (2607) | yes | PASS | idle_wait 125 recs outcomes {'admitted': 125} budget_exhausted {False: 125}; chain-stages 19 stages rc {0: 18, 1: 1} last=alpha-post-calibration.session-status |
| r3-beta | attempt_history | sources/night-custody/collection/idle_wait.jsonl (14362); sources/night-custody/night/chain-stages.jsonl (2588) | yes | PASS | idle_wait 125 recs outcomes {'admitted': 125} budget_exhausted {False: 125}; chain-stages 19 stages rc {0: 19} last=beta-post-calibration.session-status |
| r3-gamma | attempt_history | sources/night-custody/collection/idle_wait.jsonl (13699); sources/night-custody/night/chain-stages.jsonl (2686) | yes | PASS | idle_wait 107 recs outcomes {'admitted': 107} budget_exhausted {False: 107}; chain-stages 19 stages rc {0: 19} last=gamma-calibration-post.session-status |
| r4-alpha | attempt_history | sources/night-custody/collection/idle_wait.jsonl (14548); sources/night-custody/night/chain-stages.jsonl (2607) | yes | PASS | idle_wait 125 recs outcomes {'admitted': 125} budget_exhausted {False: 125}; chain-stages 19 stages rc {0: 18, 1: 1} last=alpha-post-calibration.session-status |
| r1-alpha | g10_history | sources/night-custody/night/hazard_result.json (13193) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r1-beta | g10_history | sources/night-custody/night/hazard_result.json (13153) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r1-gamma | g10_history | sources/night-custody/night/hazard_result.json (13356) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r2-beta | g10_history | sources/night-custody/night/hazard_result.json (13154) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r2-gamma | g10_history | sources/night-custody/night/hazard_result.json (13357) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r3-alpha | g10_history | sources/night-custody/night/hazard_result.json (13191) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r3-beta | g10_history | sources/night-custody/night/hazard_result.json (13155) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r3-gamma | g10_history | sources/night-custody/night/hazard_result.json (13356) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r4-alpha | g10_history | sources/night-custody/night/hazard_result.json (13193) | yes | PASS | keys 34; attempt=1 verdict=GO stage_reached=chain g10={"ran": false, "reason": "not requested", "requested": false} |
| r1-alpha | block5_codes_carried | derived/flags.jsonl (153228) | yes | PASS | 167 flag records, 18 distinct codes, klass {'REPRESENTATION': 138, 'PHYSICS': 20, 'NUMBER': 9} |
| r1-beta | block5_codes_carried | derived/flags.jsonl (147269) | yes | PASS | 162 flag records, 18 distinct codes, klass {'REPRESENTATION': 138, 'PHYSICS': 19, 'NUMBER': 5} |
| r1-gamma | block5_codes_carried | derived/flags.jsonl (137913) | yes | PASS | 145 flag records, 17 distinct codes, klass {'REPRESENTATION': 117, 'PHYSICS': 18, 'NUMBER': 10} |
| r2-beta | block5_codes_carried | derived/flags.jsonl (169929) | yes | PASS | 183 flag records, 19 distinct codes, klass {'REPRESENTATION': 136, 'PHYSICS': 31, 'NUMBER': 16} |
| r2-gamma | block5_codes_carried | derived/flags.jsonl (143296) | yes | PASS | 151 flag records, 19 distinct codes, klass {'REPRESENTATION': 119, 'PHYSICS': 21, 'NUMBER': 11} |
| r3-alpha | block5_codes_carried | derived/flags.jsonl (160351) | yes | PASS | 173 flag records, 16 distinct codes, klass {'REPRESENTATION': 138, 'NUMBER': 6, 'PHYSICS': 29} |
| r3-beta | block5_codes_carried | derived/flags.jsonl (180216) | yes | PASS | 190 flag records, 14 distinct codes, klass {'REPRESENTATION': 136, 'PHYSICS': 51, 'NUMBER': 3} |
| r3-gamma | block5_codes_carried | derived/flags.jsonl (139595) | yes | PASS | 146 flag records, 15 distinct codes, klass {'REPRESENTATION': 117, 'PHYSICS': 24, 'NUMBER': 5} |
| r4-alpha | block5_codes_carried | derived/flags.jsonl (162954) | yes | PASS | 175 flag records, 16 distinct codes, klass {'REPRESENTATION': 137, 'PHYSICS': 31, 'NUMBER': 7} |

## Name comparison (R3 table row 150-157 vs run-input copied_records)

Compared file names family by family, in all 9 sessions: identical. Per family: monitor_cost = hazards/monitor/monitor.jsonl; arm_host = hazards/arm.json + night/arm_collectors.json; battery_phase = hazards/monitor/battery.jsonl; subject_temperature = hazards/monitor/thermal.jsonl; reference_history = derived/flags.jsonl + withheld/b6-neg8.json; attempt_history = collection/idle_wait.jsonl + night/chain-stages.jsonl; g10_history = night/hazard_result.json; block5_codes_carried = derived/flags.jsonl (sources/night-custody/ prefix as in the table). No difference, so no would-be deviation-log line is needed.

## FAILs

None. Under RL-134 section 16 item 2 no family's row is withheld from the program's output on account of this check.

## Observations (not failures)

- battery.jsonl has some `reading` records with no `source` value (314 of 19108 in r1-alpha; about 1.6% elsewhere); the journal still holds the battery disclosure.
- r4-alpha hazards/arm.json is 986,941 bytes against about 180 KB in the other sessions (it still has decision GO, all six verdicts PASS, matching digest and program record).
- b6-neg8.json verdict is `passed` in the sessions printed above; every session's reference_run_ids and survivors counts are in the table.
- g10 in hazard_result.json says `ran: false, reason: not requested` in the sessions shown; the g10_history disclosure is that record.

## Could not check

- Which flag codes in derived/flags.jsonl are the block-5 session-removing codes (block5_codes_carried): the code list/policy is not in the rs-main worktree I searched (scripts/b6_r12_verify.py is absent there), so I verified the file holds well-formed flag records and the program's copy is byte-identical, not that the carried-code subset the program prints is the right subset.
- Whether the semantic content is correct beyond structure (e.g. that the cost figures are true); this is a copied-record presence/shape check, not a recompute.
- Per-file digests for sources/ files are not in run-inputs-block-2.json `files`; I bound them via sources/SHA256SUMS (itself bound by the run-input digest) and compression.jsonl instead.
- I did not open the R12 verify script `scripts/b6_r12_verify.py:89` itself; the name comparison used the R3 table's rows 150-157 text.

---
Lead spot check, 2026-11-13 18:59 PST: r4-alpha arm_host: file sha256 33ffe5d3...c8d = SHA256SUMS = restricted.json copied_disclosures sha256 = sha256 of the program record string; arm_collectors.json df254f0f... likewise. Agrees with the reader.
