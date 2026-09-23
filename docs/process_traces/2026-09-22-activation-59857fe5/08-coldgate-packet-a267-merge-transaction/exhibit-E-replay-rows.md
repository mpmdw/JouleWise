# Exhibit E — bench-replay raw rows, generated from the raw JSON

Generator: `exhibit-E-generator.py` in this directory. It reads one
`bench-replay.json` and prints, per slot: index, scheduled and actual monotonic
stamps, chain-level `start_drift_s`, session-level `start_drift_s`,
`collector_exit`, `cleanup_proven`, attestation state and wall,
`anchor_status` + `anchor_detail`, `interior_complete_support`, the archived
night's v3.1 anchor CLASS for that envelope with a MATCH/MISMATCH fidelity
verdict, and the feeder's `first_write_delay_s`; then max chain, max session,
the fidelity tally, and the driver's own `verdict.status` /
`verdict.statement` VERBATIM.

The judge reproduces any figure below with:

```
python3 docs/process_traces/2026-09-22-activation-59857fe5/08-coldgate-packet-a267-merge-transaction/exhibit-E-generator.py <bench-replay.json>
```

or directly, `python3 -c "import json;d=json.load(open('<path>'));print(d['slots'])"`.
No bench run is needed and none is authorised.

Three notes on the columns, so nothing is read as more than it is:

1. `archived_v3.1_class` is a CONSTANT in the generator
   (`ARCHIVED_V31_CLASS`), transcribed from the archived night's own v3.1
   forward projection at `447fd6bf` — bounded {02, 05, 06, 08, 09, 11, 12};
   unresolved {01, 03, 04, 10} (`affine_clock_fit_empty`, a real slew inside
   the capture) and {07} (the 15 ms backstop) — recorded at
   `docs/process_traces/2026-09-22-activation-e4b4ead6/01-launch-and-resume-record.md:29`
   and quoted in exhibit F, F9. Because it is a constant, the run cannot bend
   the column that judges it. `fidelity` compares CLASSES only (bounded vs
   anything else), never the `anchor_detail` string: the replay's clock
   relation is the archived labels against live pacing, so a different detail
   under the same class is expected.
2. `first_write_delay_s` is the feeder's, from the sidecar named in each
   envelope's `session.json -> replay.sidecar`. The bench JSON does not carry
   it (the driver copies only four sidecar fields into a row,
   `scripts/bench_replay_start_drift.py:282-285`). Reading it means opening
   files under the run's custody root, so it is behind `--sidecars` and OFF by
   default; the run below was generated with the flag off, while attempt 2 was
   in flight. It reads `n/a (--sidecars off)`, not zero and not missing.
3. `anchor_status`, `interior_complete_support`, `collector_exit` and
   `cleanup_proven` are the driver's ADMISSIBILITY fields (X2, record
   `16-bench-replay-fix-round-1-brief.md:35`), not the ruled bar. The ruled
   bar is the `chain_drift_s` column alone (exhibit F, F1/F2). They are
   printed because Q2 asks what they mean, not because the ruling binds them.

---

## ATTEMPT 1 (ABORTED, 2 slots) — smoke of the generator, run by the packet assembler

Source: `docs/process_traces/2026-09-22-activation-59857fe5/24a-bench-replay-ATTEMPT1-FAIL.json`
(tracked). This run is the one described in record 24a: it was aborted at slot 3
on the feeder first-frame causality defect, which PR #382 (main `4f8bc36d`)
cured. Its two recorded slots are shown ONLY to demonstrate that the generator
reads the schema correctly and to give the judge a worked instance of the
driver's FAIL statement. Attempt 1 is NOT the artifact offered against the
ruled precondition; attempt 2 is.

```
source              ../24a-bench-replay-ATTEMPT1-FAIL.json
schema              joulewise.bench_replay_start_drift.v1
kind                full   label_shift auto
head                4dea946b5a2eb150e58eadc91709d3b0ddd09f70  (expect 4dea946b5a2eb150e58eadc91709d3b0ddd09f70, clean_tree True)
transaction_merge   7eb53effc78b8c90995ca8206df67c0e10ff18e5 (is_ancestor True)
archive             /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922
bench_script_sha256 b11dd00e9116d078d9773355fe1e83beb33fae773289334dbf2a416bbfe911c6
feeder_sha256       45cd8420e1342ea52f9e291b19451ff0ddb25a1586de6266a05bbc0e292b3989
registration_sha256 2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1
chain_source_sha256 568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea
custody_root        /Users/edr/night-bench/bench-replay-20260922T233629Z
outcome             refused  rc 2  summary_status REPLAY_NEVER_EVIDENCE
outcome_error       InterruptedError: evidence chain signal 15; replay_recorder
machine_start       16:36  up 3 days, 22:56, 2 users, load averages: 1.17 1.80 2.98
machine_end         17:10  up 3 days, 23:29, 2 users, load averages: 2.07 1.86 1.78
argv                scripts/bench_replay_start_drift.py --archive /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922 --label-shift auto --expect-sha 4dea946b5a2eb150e58eadc91709d3b0ddd09f70 --transaction-merge 7eb53effc78b8c90995ca8206df67c0e10ff18e5 --artifact /Users/edr/code/JouleWise-wt-mag-59857fe5/docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay-start-drift.md --raw /Users/edr/code/JouleWise-wt-mag-59857fe5/docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay.json

idx  scheduled_mono_s  actual_mono_s     chain_drift_s  sess_drift_s  exit  cleanup  attest_state    attest_wall_s  anchor     anchor_detail                       interior  archived_v3.1_class  fidelity   first_write_delay_s
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1    342350.927083     342351.280843     0.354          0.608         0     True     authenticated   1.089          unknown    clock_stamp_invalid                 False     unresolved           MATCH      n/a (--sidecars off)
2    342970.927083     342971.077146     0.150          0.402         0     True     slew_attested   0.857          unknown    clock_stamp_invalid                 False     bounded              MISMATCH   n/a (--sidecars off)

slots recorded          2 of 12
max chain start_drift   0.354 s   (bar 0.5 s; over the bar: [])
max session start_drift 0.608 s   (over 0.5 s: [1])
tail_s per slot         ['5.570', '5.507']
anchor-class fidelity   1/2 recorded slots match the archived v3.1 class; mismatched slots: [2]
  (archived v3.1 class, constant in this generator: bounded {02,05,06,08,09,11,12}; unresolved {01,03,04,07,10})

DRIVER VERDICT (verbatim, recomputed by nobody):
  status                            FAIL
  statement                         max <= 0.5 s NOT shown: over=[] missing=[] recorded=2/12; slot 1 anchor_status='unknown' (required 'bounded'); slot 1 interior_complete_support=False (required True); slot 2 anchor_status='unknown' (required 'bounded'); slot 2 interior_complete_support=False (required True); the session-level bar is exceeded too (max 0.608 s > 0.5 s on slots [1])
  max_chain_start_drift_s           0.3537601249990985
  max_session_start_drift_s         0.6076677920063958
  slots_over_bar                    []
  session_bar_exceeded              True
  session_slots_over_bar            [1]
  escalate_chain_pass_session_fail  False
  smoke_exempt_fields               []
  slot_defects:
    slot 1  anchor_status = 'unknown'  (required 'bounded')
    slot 1  interior_complete_support = False  (required True)
    slot 2  anchor_status = 'unknown'  (required 'bounded')
    slot 2  interior_complete_support = False  (required True)
```

Three observations on attempt 1, flagged as the assembler's own and not the
magistrate's dictation:

- **The fidelity column has teeth, and attempt 1 fails it.** Attempt 1's slot 2
  is a **MISMATCH**: the archived envelope 02 projects `bounded`, and attempt 1
  replayed it `unresolved`. That is the feeder causality defect showing up as
  infidelity — and it is exactly the mismatch PR #382 cured, since attempt 2's
  slot 2 came back `bounded` (charge §Facts). A fidelity test that attempt 1
  passes would have been worthless; this one does not.
- Attempt 1's `anchor_detail` on both slots is `clock_stamp_invalid`, the
  cured defect — not `wall_minus_monotonic_span_exceeded`. Attempt 1's rows
  therefore say nothing about attempt 2's anchor outcomes in either direction.
- Attempt 1's slot 1 attestation state is `authenticated`, slot 2's is
  `slew_attested`. Both mean the attestation query RAN; see exhibit F, F6 (17b
  S3) for why `slew_attested` is expected on a bench that never disables
  network time, and why Q2 option (a) accepts either state.

## ATTEMPT 2 — filled by the magistrate at run end

> **PLACEHOLDER — NOT YET FILLED.** This section is empty at the time the
> charge is issued. The magistrate fills it, at the end of the run, by
> pasting the VERBATIM stdout of
> `python3 exhibit-E-generator.py <activation>/24-bench-replay.json --sidecars`
> between the fences below, adding nothing and removing nothing. Twelve rows
> are expected. If the run recorded fewer than twelve slots, the header line
> `slots recorded N of 12` says so and the judge should treat Q3 and Q4 as
> unanswerable on the rows offered.
>
> The judge must NOT answer Q4 from the magistrate's prose anywhere in this
> packet. Q4 is answered from the `chain_drift_s` column below, or from
> `python3 -c` over `24-bench-replay.json` directly. Q2 option (a) is likewise
> answered from the `fidelity` column below, not from prose.
>
> Eight rows of this section are already executed and quoted in the charge's
> §Facts (slots 1–8 at 19:16 PDT). Every one: `collector_exit` 0,
> `cleanup_proven` True, an attestation that ran. The pasted output must show
> them unchanged; if it does not, the charge's §Facts is wrong and the judge
> should say so.
>
> | slot | chain drift | anchor (replay) | archived class | fidelity |
> |---|---|---|---|---|
> | 1 | 0.352 s | `unknown` / `wall_minus_monotonic_span_exceeded` | unresolved | MATCH |
> | 2 | 0.150 s | `bounded`, interior true | bounded | MATCH |
> | 3 | 0.150 s | unresolved | unresolved | MATCH |
> | 4 | 0.150 s | unresolved | unresolved | MATCH |
> | 5 | 0.150 s | `bounded` | bounded | MATCH |
> | 6 | 0.149 s | `bounded` | bounded | MATCH |
> | 7 | 0.150 s | unresolved | unresolved | MATCH |
> | 8 | 0.150 s | `unknown` / `affine_clock_residual_exceeded` | **bounded** | **MISMATCH** |
>
> Two things the judge should read off this table rather than take on trust.
>
> **The one mismatch is envelope 08, and it refuses in the SAFE direction.**
> The archive's v3.1 projection resolves 08; the replay does not. 08 is the
> marginal envelope of the archived night: unresolved under the night's own
> recorded v3.0 status, `bounded` only once v3.1's rate-aware caps are
> applied, and the largest tail in the archive at 2.291 s (F8). The replay's
> clock relation is archived labels against live pacing and live stamps, so a
> fit that was marginal in the archive can land over the residual cap here.
> A mismatch the other way — the replay resolving an envelope the archive
> refused — would be a different animal entirely, and Q2(d) treats it as
> voiding the run.
>
> **Chain drift does not track the anchor class.** Slots 2–8 are 0.150, 0.150,
> 0.150, 0.150, 0.149, 0.150, 0.150 s — identical to three decimal places
> across slots whose full tail ran (02, 05, 06: derive, integrate, reduce
> interior) and slots whose did not (03, 04, 07, 08). Slot 1's 0.352 s is the
> first-spawn cost, not an anchor effect. This is the executed form of the
> argument that the A269 packet's 0–2.3 s tail measurement (F8) could only
> make as a bound: at this margin, the work an unresolved slot skips does not
> move the ruled quantity at all.

```
(empty — paste the generator's stdout here)

source              docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay.json
schema              joulewise.bench_replay_start_drift.v1
kind                full   label_shift auto
head                4f8bc36d39b71a06d0502016df0ff26f452b7a63  (expect 4f8bc36d39b71a06d0502016df0ff26f452b7a63, clean_tree True)
transaction_merge   7eb53effc78b8c90995ca8206df67c0e10ff18e5 (is_ancestor True)
archive             /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922
bench_script_sha256 b11dd00e9116d078d9773355fe1e83beb33fae773289334dbf2a416bbfe911c6
feeder_sha256       34169b408a4e14f5269c1766a66c1b2f4e5a639d115cddf645992d2afd3e2349
registration_sha256 2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1
chain_source_sha256 568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea
custody_root        /Users/edr/night-bench/bench-replay-20260923T003627Z
outcome             refused  rc 2  summary_status REPLAY_NEVER_EVIDENCE
outcome_error       replay_recorder
machine_start       17:36  up 3 days, 23:56, 2 users, load averages: 1.34 1.64 1.75
machine_end         19:50  up 4 days,  2:09, 2 users, load averages: 1.93 1.90 1.80
argv                scripts/bench_replay_start_drift.py --archive /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922 --label-shift auto --expect-sha 4f8bc36d39b71a06d0502016df0ff26f452b7a63 --transaction-merge 7eb53effc78b8c90995ca8206df67c0e10ff18e5 --artifact /Users/edr/code/JouleWise-wt-mag-59857fe5/docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay-start-drift.md --raw /Users/edr/code/JouleWise-wt-mag-59857fe5/docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay.json

idx  scheduled_mono_s  actual_mono_s     chain_drift_s  sess_drift_s  exit  cleanup  attest_state    attest_wall_s  anchor     anchor_detail                       interior  archived_v3.1_class  fidelity   first_write_delay_s
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1    345949.297606     345949.650006     0.352          0.608         0     True     slew_attested   0.876          unknown    wall_minus_monotonic_span_exceeded  False     unresolved           MATCH      -                  
2    346569.297606     346569.447673     0.150          0.404         0     True     authenticated   0.855          bounded    -                                   True      bounded              MATCH      -                  
3    347189.297606     347189.447657     0.150          0.404         0     True     authenticated   0.862          unknown    affine_clock_residual_exceeded      False     unresolved           MATCH      -                  
4    347809.297606     347809.447698     0.150          0.408         0     True     slew_attested   0.849          unknown    affine_clock_fit_empty              False     unresolved           MATCH      -                  
5    348429.297606     348429.447654     0.150          0.408         0     True     slew_attested   0.822          bounded    -                                   True      bounded              MATCH      -                  
6    349049.297606     349049.446563     0.149          0.411         0     True     authenticated   0.858          bounded    -                                   True      bounded              MATCH      -                  
7    349669.297606     349669.447672     0.150          0.403         0     True     slew_attested   0.864          unknown    rate_aware_native_set_empty         False     unresolved           MATCH      -                  
8    350289.297606     350289.447662     0.150          0.404         0     True     authenticated   0.729          unknown    affine_clock_residual_exceeded      False     bounded              MISMATCH   -                  
9    350909.297606     350909.447683     0.150          0.406         0     True     authenticated   0.856          unknown    affine_clock_residual_exceeded      False     bounded              MISMATCH   -                  
10   351529.297606     351529.447692     0.150          0.408         0     True     slew_attested   0.862          unknown    affine_clock_fit_empty              False     unresolved           MATCH      -                  
11   352149.297606     352149.447681     0.150          0.399         0     True     slew_attested   0.789          bounded    -                                   True      bounded              MATCH      -                  
12   352769.297606     352769.447657     0.150          0.403         0     True     slew_attested   0.839          bounded    -                                   True      bounded              MATCH      -                  
  ! slot 1: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-01/session.json: no replay.sidecar
  ! slot 2: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-02/session.json: no replay.sidecar
  ! slot 3: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-03/session.json: no replay.sidecar
  ! slot 4: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-04/session.json: no replay.sidecar
  ! slot 5: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-05/session.json: no replay.sidecar
  ! slot 6: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-06/session.json: no replay.sidecar
  ! slot 7: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-07/session.json: no replay.sidecar
  ! slot 8: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-08/session.json: no replay.sidecar
  ! slot 9: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-09/session.json: no replay.sidecar
  ! slot 10: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-10/session.json: no replay.sidecar
  ! slot 11: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-11/session.json: no replay.sidecar
  ! slot 12: first_write_delay_s unavailable — /Users/edr/night-bench/bench-replay-20260923T003627Z/night/evidence/envelope-12/session.json: no replay.sidecar

slots recorded          12 of 12
max chain start_drift   0.352 s   (bar 0.5 s; over the bar: [])
max session start_drift 0.608 s   (over 0.5 s: [1])
tail_s per slot         ['5.448', '7.995', '5.497', '5.427', '7.356', '7.690', '5.410', '5.612', '5.537', '5.565', '8.410', '6.923']
anchor-class fidelity   10/12 recorded slots match the archived v3.1 class; mismatched slots: [8, 9]
  (archived v3.1 class, constant in this generator: bounded {02,05,06,08,09,11,12}; unresolved {01,03,04,07,10})

DRIVER VERDICT (verbatim, recomputed by nobody):
  status                            FAIL
  statement                         7/12 slots NOT admissible, so their drift figures are not a measurement of the finalisation tail: slot 1 anchor_status='unknown' (required 'bounded'); slot 1 interior_complete_support=False (required True); slot 3 anchor_status='unknown' (required 'bounded'); … and 11 more; the chain figures themselves are under the bar (max 0.352 s <= 0.5 s); the session-level bar is exceeded too (max 0.608 s > 0.5 s on slots [1])
  max_chain_start_drift_s           0.3523999589961022
  max_session_start_drift_s         0.6078682499937713
  slots_over_bar                    []
  session_bar_exceeded              True
  session_slots_over_bar            [1]
  escalate_chain_pass_session_fail  False
  smoke_exempt_fields               []
  slot_defects:
    slot 1  anchor_status = 'unknown'  (required 'bounded')
    slot 1  interior_complete_support = False  (required True)
    slot 3  anchor_status = 'unknown'  (required 'bounded')
    slot 3  interior_complete_support = False  (required True)
    slot 4  anchor_status = 'unknown'  (required 'bounded')
    slot 4  interior_complete_support = False  (required True)
    slot 7  anchor_status = 'unknown'  (required 'bounded')
    slot 7  interior_complete_support = False  (required True)
    slot 8  anchor_status = 'unknown'  (required 'bounded')
    slot 8  interior_complete_support = False  (required True)
    slot 9  anchor_status = 'unknown'  (required 'bounded')
    slot 9  interior_complete_support = False  (required True)
    slot 10  anchor_status = 'unknown'  (required 'bounded')
    slot 10  interior_complete_support = False  (required True)
```

Raw file the above must have been generated from:
`docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay.json`
(untracked at the time of the charge; the driver writes it at run end).
The driver's own markdown artifact is `…/24-bench-replay-start-drift.md`.
