# Block 5, Erratum 3 (prospective): which calibration events in the ledger may fail a later window's bracket

Drafted by the magistrate's drafting seat (Opus 5.5, activation bab1c330) on 2026-10-11 and admitted with
corrections the same day by a cold gate under registration section 10 (one judge, Fable 5.1: `RULING.md` beside
this file; one refuter, Opus 5.5: `REFUTATION.md`). The magistrate is the agent that runs the project's
unattended loop; a seat is one model instance given one task; a cold gate is a ruling by a judge with no prior
involvement, checked by a refuter. Sections 4, 5 and 6 are the judge's admitted text, copied from section D of
the ruling without change; sections 1 to 3 are the draft's with the corrections the ruling orders. The first
draft is kept as `ERRATUM-draft1.md`. Admission time: `2026-10-11T17:00:00Z` (epoch 1791738000); the text calls
it ADMIT. Structure only: no energy, no power, no duration of a workload, no member's name. The times in
milliseconds below are calibration values from the calibration ledger, which the project's blinding rules
release (those rules keep every window's energies unread until the block ends). Line numbers of the
registration are those of the sealed file of the second seal
(`configs/campaigns/v5_claim_25g83/registration_block5.md`, SHA-256
`c7b3fdf78dde0a403bbc0b63262d1f8b1a697695bdeb2fb737a90cedde1ddb3f`); code line numbers are those of the pinned
harvest program's commit `0699abbb0881ce64b39c46ba07de568cc3848260`. Section 1 expands each abbreviation used
for a file.

## 1. The terms this erratum uses

Each term is built from the one before it.

- **Abbreviations for the files that line numbers refer to.** Block 5 is the project's current block of
  measurement windows (a window is defined in the next entry). Two copies of the repository matter: the
  measurement clone, which is the copy windows run from
  (`/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18`), and the desk
  checkout, a second copy at a named commit from which programs that run after collection are run
  (`/Users/edr/night-custody/desk/b5-harvest`). A file is sealed when it is frozen and named by its SHA-256 in
  the project's seal record. The admitted text of sections 4 to 6 uses these abbreviations.
  - **REG**: `configs/campaigns/v5_claim_25g83/registration_block5.md`, the registration, which is the document
    fixed before collection that states how block 5's windows are run and judged. It is cited as sealed the
    second time, SHA-256 `c7b3fdf78dde0a403bbc0b63262d1f8b1a697695bdeb2fb737a90cedde1ddb3f`, as it stands in
    the measurement clone.
  - **AP**: `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`, the sealed analysis plan beside the
    registration, SHA-256 `23ef67f5…4859`.
  - **PRE**: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, the calibration pre-registration,
    which is the document fixed in advance under which the acceptance (defined below) was derived.
  - **BRK**: `joulewise/calibration_bracketing.py`. **H**: `joulewise/b5/harvest.py`. **WW**:
    `joulewise/whole_window.py`. **CL**: `joulewise/calibration_ledger.py`. All four are cited at commit
    `0699abbb0881ce64b39c46ba07de568cc3848260` in the desk checkout. At that commit BRK has SHA-256
    `ddb7db11…4037` and is byte-identical to the measurement clone's copy.
  - **RC**: `scripts/run_campaign.py`, cited in the measurement clone (sealed).
  - **VPF**: `scripts/validate_powermetrics_fiducial.py`, a program that runs inside a window and reads the
    acceptance's screen (defined below). The ruling cites it; sections 1 to 6 do not.
  - The judge read all nine in one worktree at commit `0699abbb0881ce64b39c46ba07de568cc3848260`
    (`RULING.md`, opening paragraph).

- **Member, window, attempt, pack.** A member is one measured run of a workload. A window is one unattended
  stretch of machine time in which about 125 members run in a fixed order. A pack is the
  frozen, hash-pinned list of what one window runs. Block 5 has three packs, called ALPHA, BETA and GAMMA. An
  attempt is one occurrence of one pack, from its arming to its harvest: "BETA attempt 5" is the fifth time the
  BETA pack was armed. Each attempt has a plan file, and the plan records the attempt's scheduled start as
  `t0_epoch_s` (seconds since 1970, UTC). To arm an attempt is to schedule it to start unattended at that time.
  The chain is the sequence of steps a window then runs with no one present, from its pre capture through its
  members to its post capture. The captures and the harvest are defined below.
- **Calibration capture.** The power sampler reports the machine's power in records about a tenth of a second
  long, each with a time stamp. To learn how far those time stamps can sit from the moment the power really
  changed, a capture drives the GPU through 59 commanded on/off pulses and compares each commanded edge with the
  edge seen in the sampler's records.
- **Alignment bound.** The one number a capture yields: the largest timing error, over the 59 pulses, between a
  commanded edge and the observed edge. The registration calls it the fiducial bound (REG 949 to 953). A typical
  value on this machine is 28 ms.
- **Pre capture, post capture, bracket.** Every window takes one capture just before its first member (pre) and
  one just after its last (post). The two together are the window's bracket. They are the only direct
  measurements of the alignment bound that belong to that window.
- **Operative bound.** The single timing bound under which every member of a window is analysed:
  max(pre, post) + max(|post − pre|, 14.531 ms) (REG 832; BRK 2749 to 2750). The second term is an allowance for
  the bound moving between the two captures; it is never smaller than 14.531 ms. This erratum calls the 14.531 ms
  the **padding**.
- **Acceptance, and the 24.** The acceptance is one issued file,
  `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` (SHA-256 `f949f511…b3660`), that holds
  the numbers a bracket is judged against. They were derived from 24 captures taken on two dedicated calibration
  sessions before block 5. The 24 alignment bounds run from 0.02193176218569716 s (21.93 ms) to
  0.03646286164497997 s (36.46 ms); their mean is 28.44 ms and their sample standard deviation 3.80 ms (computed
  by the drafter from the file).
- **Screen.** The largest of the 24, 36.46 ms (the file's operative `preflight_level_screen_s`,
  `0.036462861644980`). A capture whose own evidence is sound but whose alignment bound is above the screen is
  taken as a sign that the instrument is not in the state the acceptance was derived in.
- **Range of the 24.** The interval from 21.93 ms to 36.46 ms. Its width, 14.531 ms, is the padding above.
- **Drift ceiling.** 15.502 ms (`maximum_budgetable_drift_s`, 0.01550217418713139 s): the largest |post − pre| a
  bracket may show.
- **Ledger, sequence, cutoff.** The ledger is the append-only file that records every calibration capture
  (`runs/calibration_observation_ledger.jsonl` in the measurement clone; 478 entries today). An entry's position
  is its sequence. The acceptance was derived from the ledger up to sequence 376, its cutoff. A capture recorded
  after the cutoff is a **post-cutoff capture**.
- **Session.** Before a window's pre capture the window opens a session in the ledger that names the window's
  plan; its pre and post captures are recorded against that session. A session is **finalized** when both
  captures are recorded, **aborted** when it was closed without a post capture. Each capture's ledger entry names its
  session in the field `session_id`.
- **Class of a capture.** The word the ledger records for a capture. The ledger has four final classes
  (CL 122 to 124). Three are given when the capture is written (CL 6190 to 6201; the capture tool's
  `_classify_capture`): `valid` (its evidence is sound and its bound is at or below the screen),
  `systematic-invalid` (its evidence is sound and its bound is above the screen), or `ordinary-invalid` (its
  evidence is not sound). The same test is applied to a pre and to a post capture. The fourth class,
  `abandoned`, reads as unresolved and fails a bracket (BRK 2531 to 2536).
- **Judged epoch.** The acceptance applies to captures taken under one combination of six identity fields (the
  machine model, the macOS build, the power policy, the sampling interval, the pulse protocol and the estimator
  revision). That combination is the judged epoch. Every capture named below is of the judged epoch.
  The estimator is the code that computes a capture's alignment bound from the sampler's records.
- **Trigger.** The acceptance file lists five events, its "prospective re-derivation triggers", after any of
  which a new acceptance has to be derived "before any further bracket is judged" (REG 2482 to 2500). Section 3
  lists all five.
- **Stale.** The word the bracket evaluation writes for an acceptance on which a trigger has been seen
  (`freshness.status` `stale`). A bracket judged against a stale acceptance fails, whatever its two captures
  read.
- **Measurement clone and desk checkout.** The measurement clone is the copy of the repository that windows run
  from; its files are sealed (each is named with its SHA-256 in the seal record) and no file a window reads may
  change during the block. The desk checkout is a second copy, at a named commit, from which programs that run
  after collection are run.
- **Harvest.** The program run at the desk after a window ends. It reads the window's files and writes an
  archive, with one released summary, `harvest.json`. Inside it, the **bracket evaluation** is the function
  `evaluate_calibration_bracket` (BRK 2103), reached through `calibration_bracket_for_bundles` (BRK 2770) from
  `_Harvest.calibration` (H 4588 to 4592).
- **Flag, catalog, window-removing, claim-usable.** The harvest records each finding as a flag with a code. The
  catalog (`flag_catalog.json`, sealed, SHA-256 `5d77c725…ee8d`) gives every code one effect: `EXCLUDE_WINDOW`
  (window-removing), `EXCLUDE_MEMBER`, or `DISCLOSE` (recorded, removes nothing). A window with no window-removing
  flag is claim-usable: its numbers may enter the paper. `harvest.json` lists the window-removing codes that
  fired under `exclude_window_reasons`.
- **Verdict writer and stored verdict.** During the harvest, the measurement clone's own sealed program
  (`scripts/run_campaign.py --whole-window-verdict`) writes `whole-window-verdict.json` into the window's runs
  directory. That file is the stored verdict. It contains, among other things, the writer's own run of the
  bracket evaluation, made with the clone's sealed copy of the function.
- **Pin, seal record, addendum.** The seal record
  (`docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`) names each sealed file by its SHA-256. An
  addendum is a section added to it later. A pin is the line of an addendum that names the one commit of the
  desk checkout that may produce a deciding harvest.
- **Cold gate, erratum, prospective.** A cold gate is a ruling by a judge with no prior involvement, checked by
  a refuter. An erratum is a change to a sealed document made that way. It is prospective "when it is made
  before the bytes it governs exist" (REG 567).
- **Governed attempt.** An attempt to which this erratum applies: one whose plan's `t0_epoch_s` is later than
  ADMIT. ADMIT is the admission time of this erratum, `2026-10-11T17:00:00Z`, epoch 1791738000 (section 4
  item 0).
- **Claim consumer.** Any analysis program that reads a window's members to compute a number for the paper. None
  has run on block 5: energies stay closed until the block ends (the release event, REG 4842 to 4844).
- **Attribution floor.** A number printed beside each reported cell (a cell is one entry of the paper's result
  tables): how far the energy assigned to one phase of
  one member can move when the phase's edges are displaced by the operative bound (REG 818 to 925). To first
  order it is proportional to the operative bound (REG 895 to 896), so a bound that is 1% wider gives a floor
  about 1% larger.

## 2. What happened

Three attempts of the BETA pack, in order. All three were harvested by pin `0699abbb0`.

**Attempt 3** (`v5-b5-beta-a3-20261010T2151Z`, t0 epoch 1791669060). Its pre capture read 44.38 ms
(0.04437677892168357 s) against the 36.46 ms screen. The ledger recorded it at sequence 456 with class
`systematic-invalid`, the window's chain stopped itself before any member ran, and the session was aborted at
sequence 458. The harvest removed the window for having no bracket (`calibration.no_bracket`). This is the
registered behaviour for a pre capture above the screen. The contention journal (the log, kept by the window's monitor program, of other processes
competing for the machine) shows no competing process for the capture's minutes (`seal2-beta-a3-window.md`). The next capture, 46 minutes later, read
31.41 ms.

**Attempt 4** (`v5-b5-beta-a4-20261010T2237Z`, t0 epoch 1791671820). The whole chain ran. Its captures are
sequence 464 (pre, 31.41 ms) and 468 (post, 31.86 ms), both `valid`. The harvest returned `claim_usable` false
with one window-removing code, `calibration.bracket_acceptance_failed`. The Mac had also slept during this
window, and the record of 2026-10-10 took the sleep for the cause.

**Attempt 5** (`v5-b5-beta-a5-20261011T0739Z`, t0 epoch 1791704340). The whole chain ran and the Mac did not
sleep. Its captures are sequence 474 (pre, 27.55 ms) and 478 (post, 29.48 ms), both `valid`. The harvest
returned the same single window-removing code.

The cause of both, proved by two blind seats (a seat is one model instance given one task; blind means that
neither saw the other's work) and by a program that printed status words and reason codes only
(`seal2-beta-a5-window.md`): the bracket evaluation looks at every post-cutoff capture in the ledger, not only at
the window's own two. Row 456 is such a capture. One post-cutoff capture of class `systematic-invalid` makes the
acceptance stale, and the function returns at BRK 2589 to 2602, before it has selected the window's endpoints or
compared them. The reason it returns is `calibration_acceptance_bound_stale`, and the harvest turns any reason
into `calibration.bracket_acceptance_failed` (H 4595 to 4597). The four captures of attempts 4 and 5 were never
looked at. Row 456 stays in the ledger, so an unchanged attempt of BETA or GAMMA would be removed the same way.

Counts on the ledger at sequence 478, recomputed by the drafter: 18 post-cutoff captures of the judged epoch, 17
`valid` (bounds 25.26 to 31.86 ms, all inside the range of the 24) and 1 `systematic-invalid` (row 456).

## 3. Why the registered rule does this, and why it is out of proportion

### 3.1 The rule as sealed

REG 4.6 item 2 (lines 2481 to 2511) lists the acceptance's five triggers:

1. `protocol_or_estimator_byte_change`: the calibration protocol or one of the four estimator files differs from
   what the acceptance recorded.
2. `identity_field_change`: the bracket's captures were taken under an identity that is no judged epoch.
3. `corpus_doubles_from_24_to_48`: "the ledger holds 48 or more captures of one judged epoch that it classes as
   valid, not counting captures set aside by a decision the acceptance names" (REG 2491 to 2492).
4. `new_valid_same_identity_capture_expands_observed_range`: a `valid` post-cutoff capture has a bound "below
   0.02193176218569716 s or above 0.03646286164497997 s. A window's own pre and post captures are captures of
   this kind" (REG 2493 to 2496).
5. `new_systematic_failure_challenges_preflight_screen`: "a capture of a judged epoch recorded after the cutoff
   carries the ledger class `systematic-invalid` …, or the bracket's pre bound is above the pre screen" (REG 2497
   to 2499).

And it states the consequence in words: "The capture that fired the trigger stays in the ledger, so every later
window's bracket fails the same way until a new acceptance is issued" (REG 2507 to 2508). Nothing stops the next
arm: "The lead reads the reasons in the harvest's flag (structure, no energy), arms no further window, and takes
the question of a new acceptance to a cold gate" (REG 2509 to 2511). The lead is the agent that arms windows and decides what runs next. It did not do that after
attempt 3 or after attempt 4. This erratum is that cold gate, two attempts late.

So the pinned program did what the sealed text says. Changing what a trigger does is a change of rule, not a
repair of a program, and REG 2600 and REG 5144 to 5145 require a prospective cold erratum for it.

### 3.2 Two kinds of check

Triggers 3, 4 and 5 are computed over the whole ledger. The completeness check of the candidate list (BRK 2358 to 2385) also reads every earlier valid capture from its
recorded custody path; it stays as sealed. The candidate list is the list of valid captures that the evaluation
must be able to load, and a capture's custody path is the directory the ledger recorded for its files. The
checks of the window's level and drift (section 3.4) read the window's own two captures only; this erratum
calls them the own-evidence checks. The diagram shows the ledger as attempt 5's harvest read it, and which
entries each kind of check reads for a later window W.

```
 sequence:  1 ......... 376 | 382 ........ 448 | 456 | 464  468 | 474  478 | pW   qW
            [ prior set     ] [ 13 valid       ] [ X ] [ a4 pair ] [ a5 pair ] [ W's pair ]
                            ^
                          cutoff
                              <------------- whole-ledger checks read all of these ------------>
                                                                              <- own checks ->
```

- `1 ......... 376`: the ledger entries up to the acceptance's cutoff. `prior set` is the acceptance's list of
  the captures among them; the 24 are in it.
- `cutoff`: sequence 376, marked by the `|` and the `^`.
- `382 ........ 448` and `13 valid`: the thirteen `valid` post-cutoff captures recorded before attempt 3, from
  sequence 382 to sequence 448.
- `456` and `X`: row 456, attempt 3's pre capture, class `systematic-invalid`, 44.38 ms.
- `464 468` and `a4 pair`: attempt 4's pre and post captures. `474 478` and `a5 pair`: attempt 5's.
- `pW qW` and `W's pair`: the pre and post captures of a later window W, at whatever sequences they get.
- The upper arrow: the entries the three whole-ledger triggers are computed from, which is every post-cutoff
  capture including W's own pair.
- The lower arrow: the entries the own-evidence checks are computed from, which is W's pair alone.

### 3.3 The whole-ledger triggers fire with nothing wrong

The arithmetic assumes only that captures taken in an unchanged instrument state are exchangeable, meaning that
no capture is more likely than another to be the largest or the smallest of a set. The drafter verified each
figure. The assumption itself was not tested, so the probabilities below are illustrative.

- *The screen.* The screen is the largest of 24. A 25th capture from the same state is the largest of the 25
  with probability 1/25 = 4%. So about 1 pre capture in 25 stops its own window with nothing wrong. That cost is
  registered and this erratum leaves it alone. Under the sealed rule the same capture also removes every later
  window.
- *The range.* A new capture falls outside the range of the 24 with probability 2/25 = 8% (it is the largest or
  the smallest of the 25). The chance that k new captures all fall inside the range of the 24 is
  (24 × 23) / ((24 + k) × (23 + k)). For one window (k = 2) that is 552/650 = 84.9%, so 15.1% of windows trip a
  trigger by their own two captures alone. For the 18 post-cutoff captures in the ledger today it is
  552/1722 = 32.1%. There was about a two-in-three chance that block 5 would be stale by now with nothing wrong.
- *The doubling.* The ledger holds 64 `valid` captures of the judged epoch. The two decisions the acceptance
  names set aside 23 of them. The count is 41: the 24 plus the 17 valid post-cutoff captures. The trigger fires
  at 48. Each finished window adds 2, so three more finished windows bring the count to 47, and the fourth, with
  its own two captures, to 49. That window fails, and every window after it, whatever any capture reads. Block 5
  still needs a BETA and a GAMMA window.

The rule was written when three windows on three nights were planned. Under back-to-back windows it was certain
to fire inside the block.

### 3.4 What the whole-ledger triggers protect, and what already protects it

A capture from another session is evidence about the instrument at another time. For the window being judged,
the same two questions are answered by its own measurements:

- *Is the alignment bound at its normal level now?* The window's own pre capture is compared with the same
  screen before any member runs, and its post capture is classed against the same screen when it is recorded.
- *Did the bound move during the window?* The window's own |post − pre| is compared with the drift ceiling, and
  the padding of 14.531 ms is added to the larger capture whatever the drift was.

What the own-evidence checks do not answer is whether the bound rose and fell again between the two captures.
Row 456 shows that this can happen: 44.38 ms, about 4.2 sample standard deviations above the mean of the 24,
with a clean contention journal, and 31.41 ms 46 minutes later. Removing later windows does not answer that
question either. Section 4 item 14 prints a labelled number for it beside the registered ones (the sensitivity bound).
The own-evidence checks also do not stop collection when the instrument has left the state the 24 describe;
section 4 item 13 gives the lead a rule for that case in place of the removed windows.

### 3.5 Why the registered cure is not taken

The registered cure is a new acceptance. Both seats found that it needs a new calibration pre-registration, two
or three derivation sessions, changes to files that a window reads (the acceptance, its registry in BRK, the
three packs' plan trees, the identity pins), therefore a third seal, a new clone and, by REG 4801 to 4803, a
restart at ALPHA that gives up ALPHA's claim-usable window. The new acceptance would carry the same five
triggers and go stale by the same arithmetic.

## 4. The rule

**Amendment to REG 4.6 item 2 ("When the acceptance stops being usable", "Who observes them"), to REG 6.5 (`calibration.bracket_acceptance_failed`), to REG §11 item 4 (the harvest lane's files), and to AP §4, §5, §8 and §11 (the sensitivity bound and lane L9-BRACKET), for governed attempts only except where an item says otherwise.** For an attempt whose plan's `t0_epoch_s` is later than ADMIT, three trigger events are observed and recorded and do not fail the bracket: a `systematic-invalid` capture of another session, a `valid` capture outside the range of the 24 (the window's own included), and the doubling count reaching 48. Every other check of the window's own evidence stays as sealed, with one exception stated in item 5: the window's own valid capture below 21.93 ms is recorded and no longer fails the bracket. For every other attempt nothing changes.

0. **Governing condition.** ADMIT is `2026-10-11T17:00:00Z`, epoch `1791738000`. The harvest carries it as the constant `ERRATUM_3_ADMITTED_AT_EPOCH_S` beside `ERRATUM_2_ADMITTED_AT_EPOCH_S` (H 87 to 88), and the gates check the constant against Addendum 4. An attempt is governed when its plan's `t0_epoch_s` is an int or float that is not a bool, is finite, and is greater than 1791738000; any other value, missing included, is not governed (the test of H 5223 to 5227). BETA attempts 4 (t0 1791671820) and 5 (t0 1791704340) are not governed. Because item 5's "pin before arm" forbids arming any attempt until Addendum 4 step 2 exists, no attempt can have a t0 between ADMIT and that step; the ordering of ADMIT against the main commit's committer time therefore does not matter and is not a condition.

1. **Where the change is made.** `evaluate_calibration_bracket` (BRK 2103) and `calibration_bracket_for_bundles` (BRK 2770) each gain one keyword argument, `trigger_scope`, with exactly two values: `"sealed"` (the default) and `"window_evidence"`; any other value raises. The wrapper passes its value through to the function in every call it makes. With `"sealed"` both functions return, for every input, exactly what they return at pin `0699abbb0`, byte for byte, including the absence of the keys item 6 adds. The harvest's one call (H 4588 to 4592) passes `"window_evidence"` when, and only when, the attempt is governed. No other caller is changed, so the verdict writer (the clone's sealed copy), the consumption session (WW 707) and the analysis engine keep the sealed behaviour until lane L9-BRACKET changes the consumer under item 10.

2. **Which session is the window's own.** The window's own session is `bracket_binding["session_id"]` after `validate_calibration_bracket_binding` has returned the session's two entries (BRK 2437 to 2447; the function's `bound_observations` is not None). A ledger observation is the window's own when its `bracket_session_id` (the ledger entry's `session_id`) equals that id; every other observation, including one with no session, belongs to another session. If the function reaches the trigger step with `bound_observations` None, it behaves as with `"sealed"` whatever `trigger_scope` says.

3. **The three events that are recorded and no longer fail the bracket** (with `"window_evidence"` only; failing is decided by event, never by trigger name).
   - (a) *A systematic capture of another session.* An observation that BRK 2577 to 2584 finds (post-cutoff, judged epoch, class `systematic-invalid`) and that is not the window's own by item 2. It is recorded: its ledger sequence is added to `other_session_systematic_sequences` and the name `new_systematic_failure_challenges_preflight_screen` is appended to `observed_triggers` once, as today. It causes neither the return at BRK 2589 to 2602 nor a failure at BRK 2709 to 2728. If any observation BRK 2577 to 2584 finds is the window's own by item 2, the function takes the return at BRK 2589 to 2602 as sealed (unreachable with a validated binding, since both slots must be `valid`; stated so that the program's branch is specified).
   - (b) *A valid capture outside the range of the 24*, whether the window's own or another session's (BRK 2562 to 2576). The name `new_valid_same_identity_capture_expands_observed_range` is appended as today. It does not fail the bracket.
   - (c) *The doubling count at or above 48* (BRK 2544 to 2554). The name `corpus_doubles_from_24_to_48` is appended as today. It does not fail the bracket.
   - With `"window_evidence"` the set of names that fails the bracket at BRK 2709 to 2728 is exactly `{"protocol_or_estimator_byte_change"}`. The window's own pre bound above the screen fails as today through BRK 2697 to 2707, which does not read that set.

4. **What fails a governed bracket, each exactly as sealed, in the function's present order.** Condition, then outcome.
   - The acceptance file missing, unauthenticated or not issued (BRK 2157 to 2184): `calibration_acceptance_bound_stale`. The ledger snapshot absent, refused, or with a baseline that is not the acceptance's cutoff (BRK 2204 to 2220): the snapshot's reasons, or `calibration_ledger_baseline_missing`. An incomplete candidate list (BRK 2358 to 2385): `calibration_ledger_off_ledger_artifact`; a candidate whose custody did not load (BRK 1986 to 1987, 2881 to 2887): `calibration_ledger_custody_invalid`. A set-aside list that cannot be resolved (BRK 2539 to 2543): `calibration_acceptance_bound_stale`.
   - `identity_field_change`: any of the six identity fields differs (BRK 2257 to 2261, 2317 to 2320): `calibration_acceptance_bound_stale`.
   - A missing or invalid bracket binding (BRK 2422 to 2475): `calibration_bracket_binding_missing` or `calibration_bracket_binding_invalid`.
   - A post-cutoff observation whose class is none of `valid`, `systematic-invalid`, `ordinary-invalid` (BRK 2531 to 2536; `abandoned` is such a class): `calibration_observation_unclassifiable`.
   - *The window's own post capture above the screen.* The ledger classes it `systematic-invalid` (CL 6195 to 6201). The harvest records `calibration.capture_invalid` (H 4514 to 4518); `build_calibration_bracket_binding` raises (BRK 1472 to 1488), the harvest records `calibration.binding_failed` and returns before the call (H 4569 to 4577). Both codes are `EXCLUDE_WINDOW`. The function is not called; `harvest.json` records `evaluated` false (item 8).
   - Missing or old endpoints (BRK 2619 to 2625): `instrument_calibration_bracket_missing` or `instrument_calibration_stale`. An endpoint not of the bound session (BRK 2643 to 2644): `calibration_bracket_binding_invalid`. A bound that is not a finite non-negative number (BRK 2647 to 2653): `instrument_calibration_invalid`.
   - *The window's own pre bound above the screen* (BRK 2697 to 2707): `instrument_calibration_mismatch`. (Unreachable with a validated binding; stays as sealed.)
   - `protocol_or_estimator_byte_change` (BRK 2494 to 2499), through BRK 2709 to 2728: `calibration_acceptance_bound_stale`.
   - *The window's own drift above the drift ceiling* 15.502 ms (BRK 2746 to 2747): `instrument_calibration_mismatch`.

5. **A window's own capture outside the range or above the screen: the complete case list.** p the pre bound, q the post bound of a governed window.
   - p above the screen (36.46 ms): the chain stops before any member (exit 12), the session is aborted, the harvest records `calibration.no_bracket`. Removed. Unchanged.
   - q above the screen: removed by `calibration.capture_invalid` and `calibration.binding_failed` (item 4). Unchanged.
   - p or q below 21.93 ms: the capture is `valid`; event (b) is recorded; the bracket does not fail for it. The drift ceiling still applies (p = 20.5 ms, q = 36.4 ms fails on a drift of 15.9 ms). Such a window's operative bound can fall below 36.46 ms, the smallest value the sealed rule could produce; the paper marks it (section 6 item 1).
   - p or q at or below the screen and above 0.03646286164497997 s: possible only in a gap of 3 × 10⁻¹⁷ s; `valid`; event (b) recorded.
   - p and q inside the range: no event of the window's own.
   - In every case the window's two captures count toward the doubling count, and event (c) is recorded when the count reaches 48.

6. **What the function returns for a governed bracket.** As at pin `0699abbb0`, plus four keys under `acceptance.prospective_rederivation`, present with `"window_evidence"` only: `trigger_scope` (`"window_evidence"`); `recorded_only_triggers` (the names of the events of item 3 that were observed, in the fixed order (c), (b), (a), possibly empty); `corpus_doubling` (`{"count": <the largest per-epoch count of BRK 2544 to 2552>, "threshold": 48}`); `other_session_systematic_sequences` (ascending ledger sequences of the observations of event (a), possibly empty). `observed_triggers` keeps its meaning and lists every observed name. `acceptance.freshness.status` is `fresh` when the only observed names are recorded-only ones and no item-4 check failed. `status` is `passed` and the reasons are empty exactly when no check of item 4 failed; the operative bound and allowance are computed as today (BRK 2749 to 2765).

7. **The flag.** The harvest emits `calibration.bracket_acceptance_failed` under the unchanged condition of H 4595 to 4597: a status other than `passed`, or any reason. A recorded-only event is neither. No flag code is added, removed or reclassified.

8. **What the harvest writes into `harvest.json`.** (i) One new top-level object `calibration_bracket`, written by every harvest of the new program: `{"erratum_3_governed": bool, "trigger_scope": "window_evidence"|"sealed", "evaluated": bool, "status": <status word or null>, "reasons": [<sorted reason codes>], "freshness": "fresh"|"stale"|null, "observed_triggers": [...], "recorded_only_triggers": [...], "corpus_doubling": {"count": N, "threshold": 48}|null, "other_session_systematic_sequences": [...]}`. `evaluated` is false when the harvest returned before the call; every list is then empty and every scalar null except the first two. None of these is an energy. (ii) `outputs` gains the key `withheld/bracket-evaluation.json` with that file's SHA-256, recorded as the `derived/` entries are (H 4458, 4497, 4578); the file's content is unchanged. (iii) `HARVEST_PROGRAM_FILES` (H 3929) gains `joulewise/calibration_bracketing.py`, so `harvest_checkout.files` carries its digest.

9. **The stored verdict of a governed window.** The verdict writer is the measurement clone's sealed program and keeps the sealed rule, so on every governed window whose ledger holds row 456 the stored verdict records a failed calibration bracket with the condition `calibration_acceptance_bound_stale`, no endpoints, no operative bound, and an evaluation basis with no calibration pair and no `launch_lineage`. The harvest decides nothing by that part of the stored verdict (REG 4154 to 4155). The failure surfaces as `whole_window.not_passed` (`DISCLOSE`), with the condition in its `observed.conditions`; `whole_window.member_failures_unreadable` fires only on a malformed member-failure list, which the writer never writes. On a window governed by this erratum and by Erratum 2, the last sentence of Erratum 2 item 7 ("the common launch lineage is bound through the basis") does not hold; the lineage is recomputed by the consumer under item 10(ii). On a governed GAMMA window the desk provenance checker runs with the sealed scope and may record `g3.recompute_failed` (`DISCLOSE`); the gates' GAMMA fixture (section 5) shows which codes result, and any window-removing code arising from the stale state is a defect to cure in the lane before a governed GAMMA attempt is armed.

10. **Claim consumers** (a rule now; code in lane L9-BRACKET before the release event). (i) A consumer evaluates each window's calibration bracket over that window's archived ledger copy (`sources/ledger/calibration_observation_ledger.jsonl`) and terminal pin (`derived/terminal-pin.json`), with that window's `derived/bracket-binding.json`, with the acceptance's cutoff as baseline, and with `trigger_scope` `"window_evidence"` exactly when the attempt is governed. A consumer that reads several windows evaluates each against its own archive; one ledger snapshot for several windows is not admissible. Each archived ledger copy must be a byte prefix of the live ledger at the release event, and its SHA-256 must equal the one `harvest.json` records. (ii) For a governed window no consumer takes the calibration pair, the endpoint maximum, the drift, the allowance, the operative bound, the launch lineage or the bracket's conditions from the stored verdict or its evaluation basis. It takes them from its own evaluation of (i), whose `status`, reasons, `pre`, `post`, `endpoint_max_b_fiducial_s`, `drift_s`, `calibration_drift_allowance_s`, `b_fiducial_s`, `bracket_binding`, and `acceptance.freshness`, `acceptance.preflight`, `acceptance.drift`, `acceptance.allowance` and `acceptance.prospective_rederivation` must equal those of the harvest's `withheld/bracket-evaluation.json` assessment, authenticated by the SHA-256 in `harvest.json`; `window_start_s`, `window_end_s` and `members` need not be equal; any other difference refuses the window. It recomputes the common launch lineage from the member bundles, the two capture files and the bound artifact against that bracket. Of the stored verdict's conditions it disregards `calibration_acceptance_bound_stale` and no other; the refusal of WW 5513 to 5515 on a non-empty condition list and the comparison of WW 5560 to 5566 are, for a governed window, made against the condition list and the bracket with that one condition and the stored calibration bracket set aside. (iii) The membership, provenance and physics checks stay independent and unchanged. (iv) For a window that is not governed, nothing changes except (i)'s per-window archive rule, which is the registered rule (REG 4011, "read up to this window's terminal entry") made explicit; ALPHA attempt 1 is evaluated over its own archived copy and reads fresh. (v) Lane L9-BRACKET of AP §11 implements (i) to (iv) and item 14 before any claim is computed; until it lands no number of a governed window is claimable, which is already true of every block-5 window (REG 1241 to 1243).

11. **The re-derivation.** A new acceptance, derived under a new calibration pre-registration revision, falls due before any later measurement block is sealed. It is no longer due before the next window of block 5. The lead records each harvest's `recorded_only_triggers`, `corpus_doubling.count` and `other_session_systematic_sequences` in the block's attempt history.

12. **Attempts that are not governed.** Every attempt with `t0_epoch_s` at or before ADMIT is judged under the sealed rule and harvested, if at all, by the pin that governs it (section 5). BETA attempts 4 and 5 stay collected, not claim-usable (`calibration.bracket_acceptance_failed`), kept and disclosed, their energies never analysed, never harvested by the new program for a deciding record. Before the release event the only run of the new program over either is the bracket evaluation alone, over the attempt's archived ledger copy, pin and binding, printing status words, reason codes, trigger names, the doubling count and sequences, and never a `claim_usable`, a verdict or an energy; it is labelled exploratory (REG 4844) and changes no verdict, `claim_usable`, cause key or attempt history. A full run over either, if ever made, is after the release event and labelled the same way.

13. **A repeat, and the pre-arm run** (a rule for the lead, not a program refusal; applies to every arm of a block-5 attempt from ADMIT on). (a) Before every arm, the lead runs from the pinned desk checkout the pinned bracket evaluation over the live ledger (`load_calibration_ledger_snapshot` with the acceptance's cutoff as baseline, `discover_calibration_candidates`, then `evaluate_calibration_bracket` with `"window_evidence"` for a hypothetical window starting now, with the last finalized session's binding) and records in the arm record: the snapshot's refusal reasons (must be empty); the number of candidates returned and the number of valid, non-derivation, finalized-session observations in the snapshot (must be equal, which proves every capture directory loaded: finding 8); `observed_triggers`; `corpus_doubling`; `other_session_systematic_sequences`. An arm proceeds only when the two "must" conditions hold. (b) When `other_session_systematic_sequences` has two or more entries, the lead arms no attempt until a consult of two blind seats has read those captures' per-pulse evidence (counts and timing diagnostics, no energy), the monitor's contention journals and the ledger, and recorded a decision in the block's records; the consult may authorise arming unchanged. (c) When two of those captures are consecutive captures of the judged epoch (no `valid` capture of the judged epoch recorded between them), the question goes to a cold gate under REG §10 before any arm. (d) Row 456 is the first entry of the list.

14. **Sensitivity bound** (an amendment to AP §4 steps 4 and 7, §5 and §8; applies to every analysed window of block 5, governed or not). Primary numbers are computed under the registered operative bound and are unchanged. For every analysed window W the analysis also computes and prints, labelled "sensitivity" and never composed into a primary number, under b_sens(W) = max(b_op(W), B_max): (i) each reported cell's attribution floor; (ii) each reported cell's interval endpoints, with the first-kind bound of every kept member re-derived under b_sens and B recomputed from it; (iii) each contrast's comparative detection floor and its outcome word, with the shared-edge sweep over [−b_sens, b_sens]. b_op(W) is W's registered operative bound (`b_fiducial_s` of its bracket). B_max is the largest alignment bound over (a) the 24 members' `b_fiducial_s` in the acceptance file and (b) every ledger observation with sequence greater than 376 and at most T, of the judged epoch, with class `valid` or `systematic-invalid`, where T is the largest terminal-pin sequence among the analysed attempts of the three packs. B_max is one number for the block, fixed at T, and later ledger entries cannot move it. The printed line names b_sens, B_max, the ledger sequence that attains B_max, and T. The sensitivity pass alters or constructs no calibration bracket record: it passes b_sens as a number to the reducer and the sweep, and the registered refusals on the bracket record (`registered_common_mode_operative_bound`) stay as they are for the primary pass. Its analysis-plan text and code are lane L9-BRACKET's, written blind before the release event.

**Worked example (the ledger at sequence 478; the governed window's bounds invented).** A governed BETA attempt opens session S; pre 28.00 ms, post 30.50 ms, both `valid`. The harvest calls the function with `"window_evidence"`. Identity matches; binding valid, own session S; protocol and estimator bytes equal. Doubling 41 + 2 = 43: not observed. Range: 19 valid post-cutoff captures, 25.26 to 31.86 ms, inside 21.93 to 36.46: not observed. Systematic: row 456, session of attempt 3, not S: event (a), recorded; the function goes on. Endpoints: S's two captures; pre at or below the screen. Failing names: none. Drift 2.50 ms, below 15.502. Operative bound 30.50 + 14.531 = 45.031 ms. Status `passed`, no reasons, no flag. `harvest.json`: `observed_triggers` and `recorded_only_triggers` both `["new_systematic_failure_challenges_preflight_screen"]`, `corpus_doubling` `{"count": 43, "threshold": 48}`, `other_session_systematic_sequences` `[456]`, `evaluated` true. Sensitivity: B_max today is 44.38 ms (sequence 456), b_sens = max(45.031, 44.38) = 45.031 ms, so the sensitivity values equal the primary ones for this window. Variants: post 37.00 ms, classed `systematic-invalid`, the window's own: `calibration.capture_invalid` and `calibration.binding_failed`, `evaluated` false, removed. Pre 21.00, post 24.00: event (b) recorded, drift 3.00, operative bound 38.531 ms, passed; sensitivity under 44.38 ms. Pre 21.00, post 36.40: drift 15.40 under the ceiling, operative bound 51.80 ms, passed. Three finished windows later the count is 49: event (c) recorded, the bracket still passes.

**Why this cannot let a window with a bad bracket pass.** Every comparison of the window's own two captures with the screen and the drift ceiling is untouched, as are the identity, byte, binding, ledger integrity and custody checks; the operative bound is the same formula over the same two captures. What changes is only whether the existence of certain other entries in the ledger, or a low reading of the window's own, fails the window; and a shifted instrument is caught by item 13, not by losing windows.

## 5. What does not change, and mechanics

- **Unchanged.** The acceptance file's bytes and every number in it (the screen, the padding, the drift ceiling); the five triggers' names and definitions; the flag catalog and every code's effect; the ledger and how a capture is classed; the in-window pre screen and the chain; the verdict writer; the roster; the blinding rules; every file a window reads; the measurement clone, the claim head and the seal commit. The registration's bytes are not edited; the digest every plan carries stays `c7b3fdf7…db3f`. This is a separate document.
- **REG §11 item 4, amended for this lane only.** The lane may also change `joulewise/calibration_bracketing.py`, in the desk checkout only, and only as section 4 item 1 describes. With `trigger_scope` `"sealed"` the desk copy's two functions must return, on every fixture of the lane and on the rehearsal copy, exactly what the clone's copy returns; a test in the lane asserts it. The change is never committed, merged, pulled or checked out in the measurement clone (REG 5312 to 5316).
- **Texts superseded for governed attempts of block 5.** The sentence of PRE 880 to 883 that brackets stop passing after a doubling, and the reading of the acceptance's `prospective_rederivation.triggers` (BRK 2295 `mandatory_triggers`) as events that fail a bracket, for the three events of item 3. The acceptance's rule `judge_under_prior_artifact_never_self_fit` and PRE 253 to 259 stand: row 456 was judged under the prior acceptance, failed its own window, and enters no threshold.
- **Changed.** The desk checkout only: `joulewise/calibration_bracketing.py`, `joulewise/b5/harvest.py`, and tests. REG 4777 to 4779 covers the desk copy differing from the clone's.
- **Addendum 4 to the seal record, in two steps.** *Step 1:* this erratum's path and the SHA-256 of its admitted text as committed on main; the line `ERRATUM-3-ADMITTED-AT: 2026-10-11T17:00:00Z` (epoch 1791738000); the pin-scoping paragraph; the amendment of §11 item 4 above. *Step 2, before any governed attempt is armed:* a `B5-HARVEST-PIN:` line with the implementing commit, its files (now including `joulewise/calibration_bracketing.py`) and their SHA-256s, and the path of its gate record.
- **Pin scoping.** Three pins stand. `224a264c5` for attempts with t0 at or before `ERRATUM-2-ADMITTED-AT` (1791649800). `0699abbb0` for attempts with t0 after that and at or before ADMIT (BETA attempts 2 to 5). The step-2 pin for governed attempts. The analysis checks each attempt's recorded harvest commit against the pin that governs it (AP §2.2, per attempt).
- **Gates on the implementing program**, as for pin 3 (`sources-erratum/harvest-pin3-gates.md`), plus: an item-by-item check against section 4; the sealed-scope byte-identity test above; the before/after comparison on the rehearsal copy (a window harvested with `"sealed"` gives byte-identical `derived/` output and equal flags against pin `0699abbb0`); an executed fixture of a stale ledger with a verdict that records no sources (Erratum 2's recovery in the stale state) and an executed fixture of a GAMMA-shaped window in the stale state, each printing the window-removing codes that result (any such code arising from the stale state is a defect to cure before a governed attempt of that pack is armed); the limited exploratory run of item 12 over BETA attempt 5's archived ledger copy; the constant of item 0 checked against Addendum 4.
- **Pin before arm.** No governed attempt is armed until Addendum 4 step 2 is on main. The admitted text is frozen at admission. If the gates find that the admitted text cannot be implemented exactly, a corrected erratum is admitted under §10 before any governed attempt is armed. The program under gates is never run over a governed attempt's bytes.
- **Retention.** The capture directory of every post-cutoff capture, the removed BETA attempts' included, stays at the path the ledger records, unmoved and unmodified, until the release event. No offload or archive move touches it. The pre-arm run of item 13(a) proves it before each arm.
- **Re-harvest.** A later re-harvest of a governed window is given that window's archived ledger copy and terminal pin.
- **Release event.** It ties this erratum's SHA-256 beside those of the registration, the analysis plan, the catalog and Erratum 2.

## 6. Registered deviations and disclosures (item 11 of the list in REG §10)

1. From ADMIT on, three of the acceptance's five re-derivation triggers were recorded and did not remove a window: a capture above the screen in another session, a valid capture outside the range of the 24 (a governed window's own included; such a window's operative bound can be below 36.46 ms and the paper marks it), and the capture count reaching 48. For each analysed window the paper lists which were on record at its harvest, the doubling count, and the ledger sequences of the systematic captures.
2. On 2026-10-10 one pre capture read 44.38 ms against a 36.46 ms screen, about 4.2 sample standard deviations above the mean of the 24, with no competing process in the monitor's journal; the capture 46 minutes later read 31.41 ms. The cause is not established. The acceptance was not re-derived inside block 5; a re-derivation is owed before the next block. (Per-pulse exceedance counts may be added only after a recount with the estimator's own function.)
3. A window's operative bound is built from its own two captures and a padding of 14.531 ms; it does not prove that the alignment bound stayed below it between the captures. Of the seven finalized brackets after the cutoff, three have an operative bound of at least 44.38 ms and four fall short of it by 0.33 to 1.90 ms. For every analysed window the paper prints the sensitivity values of item 14 beside the primary ones.
4. BETA attempts 4 and 5 completed their chains and were removed by the registered rule, not by anything measured in them; attempt 4 also spanned a sleep. Neither is analysed; both are in the attempt history and the per-pack counts (REG 4810 to 4822).
5. The registered rule required the lead to stop arming after attempt 3 (REG 2509 to 2511); two further attempts were armed first, and the decision of 2026-10-10 misread attempt 4's cause.
6. The rule was changed after attempts 3, 4 and 5 had been collected, with their yield counts and all 18 post-cutoff alignment bounds known. No energy of any block-5 window had been read. The change does not apply to them.
7. ALPHA's analysed window was judged under the sealed rule and BETA's and GAMMA's under the amended one; all three share one acceptance, one screen, one padding, one drift ceiling and identical own-capture checks, and all three carry the sensitivity values.
8. The stored verdict of every governed window reads failed with `calibration_acceptance_bound_stale`, because its writer is sealed; the deciding evaluation is the harvest's, and every claim consumer re-evaluates per item 10. On governed GAMMA windows the desk provenance checker's recompute may be recorded failed for the same reason.
9. The screen is the largest of 24 captures, so about 1 window in 25 is stopped at its pre capture with nothing wrong; unchanged, to be reconsidered at the next block's registration.

## 7. How the questions put to the judge were ruled

The first draft put four questions to the judge (Q-A to Q-D) and recorded three points on which its drafter
would have gone further. Their full text is in `ERRATUM-draft1.md`, section 7 and the last section. "The
ruling" is `RULING.md`; its section A answers the refuter's findings and its section B answers the questions.
Item numbers are those of section 4 above.

- **Q-A.** Should a number be printed for an excursion, meaning the alignment bound rising and falling again
  between a window's two captures (section 3.4)? Ruled yes: for every analysed window of the block, governed or
  not, the analysis prints a second set of values under a sensitivity bound, which is the larger of the
  window's operative bound and the largest alignment bound on record for the block. The values are labelled and
  never replace a registered number. Ruling section B, Q-A, and section A, finding 7; settled by item 14 and by
  section 6 item 3.
- **Q-B.** Does the failed bracket that the sealed verdict writer stores remove a governed window in the
  harvest? Ruled no: it yields only `whole_window.not_passed`, a `DISCLOSE` code. Ruling section B, Q-B;
  settled by item 9, with two executed test cases required by the gates of section 5.
- **Q-C.** Which ledger does a claim consumer read, and would it refuse ALPHA attempt 1? Ruled: each consumer
  evaluates each window's bracket over that window's own archived ledger copy, so ALPHA attempt 1 reads fresh,
  and this is a rule of this erratum now, not a later follow-on. Ruling section B, Q-C, and section A,
  finding 4; settled by item 10, parts (i), (iv) and (v).
- **Q-D.** Does anything after a passing bracket take a different path for a window with recorded triggers,
  and must the launch-lineage point be settled here? The launch lineage is a provenance record that the stored
  verdict's basis normally carries and that Erratum 2 of this block (`../sources-erratum/ERRATUM.md`), item 7,
  relies on; a governed window's stored basis has none. Ruled: settled here. The consumer recomputes the
  lineage. Ruling section B, Q-D, and section A, finding 9; settled by item 10 part (ii) and item 9.
- **Dissent 1: a repeat has no rule.** The drafter wanted a rule for the lead when a second capture above the
  screen appears in another session. Upheld: two or more such captures send the next arm to a consult (a review
  by two blind seats), and two in a row send it to a cold gate. Ruling section A, finding 6; settled by
  item 13.
- **Dissent 2: print the number for every analysed window, not only for governed windows that carry a
  trigger, and for all three quantities the operative bound enters.** The three quantities are each cell's
  attribution floor, each cell's interval, and the comparative detection floor that decides whether a contrast
  between cells is resolved. Upheld. Ruling section B, Q-A, and section E, item 5; settled by item 14.
- **Dissent 3: the claim-consumer rule belongs in this erratum, not in a follow-on alone.** Upheld. Ruling
  section A, finding 4, and section B, Q-C; settled by item 10.

### Reading notes on the admitted text (added by the magistrate; they change nothing in sections 4 to 6)

Three references in the admitted text point at the wrong place or number. The text is left as the judge wrote
it; this is how each is read.

- Item 0 says "item 5's 'pin before arm'". The pin-before-arm rule is the bullet of that name in section 5;
  item 5 of section 4 is the case list.
- Item 13(a) and the Retention bullet of section 5 cite "finding 8". That is finding 8 of the refutation as
  ruled in section A of `RULING.md`: the candidate list reads every earlier valid capture from the path the
  ledger records, and one that does not load fails the bracket.
- Item 5 gives the chain's exit code for a pre capture above the screen as 12, the registration's number.
  BETA attempt 3, which stopped for that cause, exited with 11. No rule of this erratum reads the exit code:
  the outcome is decided by the aborted session and the harvest's `calibration.no_bracket`.
