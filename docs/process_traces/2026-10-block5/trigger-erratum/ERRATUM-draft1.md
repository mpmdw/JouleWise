# Block 5, Erratum 3 (prospective), draft 1: which calibration events in the ledger may fail a later window's bracket

## Drafting note

Drafted on 2026-10-11 by an Opus 5.5 seat for the orchestrator, from the decision record
`docs/process_traces/2026-10-block5/seal2-beta-a5-consult.md`. It is a draft for a cold gate under registration
section 10 (one refuter, one judge). Nothing in it is in force. Section 4 is the rule the orchestrator decided,
sharpened in wording only; section 7 holds four questions the judge must rule on, each with what the drafter found
in the code; the drafter's own disagreements are in the last section and nowhere else.

Structure only: no energy, no power, no duration of a workload, no member's name. The times in milliseconds below
are calibration values from the calibration ledger, which the blinding rules release.

Line numbers:

- **REG** is the sealed registration of the second seal,
  `configs/campaigns/v5_claim_25g83/registration_block5.md`, SHA-256
  `c7b3fdf78dde0a403bbc0b63262d1f8b1a697695bdeb2fb737a90cedde1ddb3f`, as it stands in the measurement clone
  `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18`.
- **AP** is the sealed analysis plan beside it, `analysis_plan_block5.md`, SHA-256 `23ef67f5…4859`.
- **BRK** is `joulewise/calibration_bracketing.py`, **H** is `joulewise/b5/harvest.py`, **WW** is
  `joulewise/whole_window.py`, **CL** is `joulewise/calibration_ledger.py`, all at the pinned harvest commit
  `0699abbb0881ce64b39c46ba07de568cc3848260` in the desk checkout `/Users/edr/night-custody/desk/b5-harvest`.
  At that commit BRK has SHA-256 `ddb7db11…4037` and is byte-identical to the measurement clone's copy.
- **RC** is `scripts/run_campaign.py` in the measurement clone (sealed).
- **ADMIT** stands for the admission time of this erratum, a UTC instant that the judge's ruling and Addendum 4 of
  the seal record fix. It is a placeholder everywhere below.

## 1. The terms this erratum uses

Each term is built from the one before it.

- **Member, window, attempt, pack.** A member is one measured run of a workload. A window is one unattended
  stretch of machine time in which about 125 members run in a fixed order. A pack is the
  frozen, hash-pinned list of what one window runs. Block 5 has three packs, called ALPHA, BETA and GAMMA. An
  attempt is one occurrence of one pack, from its arming to its harvest: "BETA attempt 5" is the fifth time the
  BETA pack was armed. Each attempt has a plan file, and the plan records the attempt's scheduled start as
  `t0_epoch_s` (seconds since 1970, UTC).
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
  captures are recorded, **aborted** when it was closed without a post capture.
- **Class of a capture.** The word the ledger records for a capture when it is written (CL 6190 to 6201; the
  capture tool's `_classify_capture`): `valid` (its evidence is sound and its bound is at or below the screen),
  `systematic-invalid` (its evidence is sound and its bound is above the screen), or `ordinary-invalid` (its
  evidence is not sound). The same test is applied to a pre and to a post capture.
- **Judged epoch.** The acceptance applies to captures taken under one combination of six identity fields (the
  machine model, the macOS build, the power policy, the sampling interval, the pulse protocol and the estimator
  revision). That combination is the judged epoch. Every capture named below is of the judged epoch.
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
  ADMIT.
- **Claim consumer.** Any analysis program that reads a window's members to compute a number for the paper. None
  has run on block 5: energies stay closed until the block ends (the release event, REG 4842 to 4844).
- **Attribution floor.** A number printed beside each reported cell: how far the energy assigned to one phase of
  one member can move when the phase's edges are displaced by the operative bound (REG 818 to 925). To first
  order it is proportional to the operative bound (REG 895 to 896), so a bound that is 1% wider gives a floor
  about 1% larger.

## 2. What happened

Three attempts of the BETA pack, in order. All three were harvested by pin `0699abbb0`.

**Attempt 3** (`v5-b5-beta-a3-20261010T2151Z`, t0 epoch 1791669060). Its pre capture read 44.38 ms
(0.04437677892168357 s) against the 36.46 ms screen. The ledger recorded it at sequence 456 with class
`systematic-invalid`, the window's chain stopped itself before any member ran, and the session was aborted at
sequence 458. The harvest removed the window for having no bracket (`calibration.no_bracket`). This is the
registered behaviour for a pre capture above the screen. The monitor's contention journal for the capture's
minutes shows no competing process (`seal2-beta-a3-window.md`). The next capture, 46 minutes later, read
31.41 ms.

**Attempt 4** (`v5-b5-beta-a4-20261010T2237Z`, t0 epoch 1791671820). The whole chain ran. Its captures are
sequence 464 (pre, 31.41 ms) and 468 (post, 31.86 ms), both `valid`. The harvest returned `claim_usable` false
with one window-removing code, `calibration.bracket_acceptance_failed`. The Mac had also slept during this
window, and the record of 2026-10-10 took the sleep for the cause.

**Attempt 5** (`v5-b5-beta-a5-20261011T0739Z`, t0 epoch 1791704340). The whole chain ran and the Mac did not
sleep. Its captures are sequence 474 (pre, 27.55 ms) and 478 (post, 29.48 ms), both `valid`. The harvest
returned the same single window-removing code.

The cause of both, proved by two blind seats and by a program that printed status words and reason codes only
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
the question of a new acceptance to a cold gate" (REG 2509 to 2511). The lead did not do that after attempt 3 or
after attempt 4. This erratum is that cold gate, two attempts late.

So the pinned program did what the sealed text says. Changing what a trigger does is a change of rule, not a
repair of a program, and REG 2600 and REG 5144 to 5145 require a prospective cold erratum for it.

### 3.2 Two kinds of check

Triggers 3, 4 and 5 are computed over the whole ledger. Everything else the bracket evaluation checks is computed
from the window's own two captures. The diagram shows the ledger as attempt 5's harvest read it, and which
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
figure.

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
question either. Question Q-A in section 7 puts to the judge whether a number should be printed for it.

### 3.5 Why the registered cure is not taken

The registered cure is a new acceptance. Both seats found that it needs a new calibration pre-registration, two
or three derivation sessions, changes to files that a window reads (the acceptance, its registry in BRK, the
three packs' plan trees, the identity pins), therefore a third seal, a new clone and, by REG 4801 to 4803, a
restart at ALPHA that gives up ALPHA's claim-usable window. The new acceptance would carry the same five
triggers and go stale by the same arithmetic.

## 4. The rule

**Amendment to REG 4.6 item 2 ("When the acceptance stops being usable", "Who observes them") and to REG 6.5
(`calibration.bracket_acceptance_failed`), for governed attempts only.** For an attempt whose plan's
`t0_epoch_s` is later than ADMIT, three trigger events are observed and recorded and do not fail the bracket:
a `systematic-invalid` capture that belongs to another session, a `valid` capture outside the range of the 24,
and the doubling count reaching 48. Every check of the window's own evidence stays as sealed. For every other
attempt nothing changes.

0. **Governing condition.** The harvest carries ADMIT as a constant, `ERRATUM_3_ADMITTED_AT_EPOCH_S`, beside the
   existing `ERRATUM_2_ADMITTED_AT_EPOCH_S` (H 87 to 88). An attempt is governed when its plan's `t0_epoch_s` is
   a finite number, not a boolean, and greater than that constant. Any other value is not governed. The test is
   the one Erratum 2's gate already makes at H 5223 to 5227.

1. **Where the change is made.** `evaluate_calibration_bracket` (BRK 2103) and `calibration_bracket_for_bundles`
   (BRK 2770) gain one keyword argument, `trigger_scope`, with two values: `"sealed"` (the default) and
   `"window_evidence"`. With `"sealed"` both functions return exactly what they return at pin `0699abbb0`, byte
   for byte. The harvest's one call (H 4588 to 4592) passes `"window_evidence"` when, and only when, the attempt
   is governed. No other caller is changed, so every other caller keeps the sealed behaviour.

2. **Which session is the window's own.** The window's own session is the session named by the bracket binding
   the function has validated: `bracket_binding["session_id"]`, after `validate_calibration_bracket_binding`
   returned the session's two entries (BRK 2437 to 2447). A capture is the window's own when its ledger entry's
   `bracket_session_id` equals that session id. Every other capture, including one recorded against no session,
   belongs to another session. If the function reaches the trigger step without a validated binding
   (`bound_observations is None`), it behaves as with `"sealed"`: the harvest always supplies a binding for a
   block-5 window (H 4569 to 4577), and a call without one is not the case this erratum is written for.

3. **The three events that are recorded and no longer fail the bracket** (with `"window_evidence"` only):
   - (a) *A systematic capture of another session.* A post-cutoff capture of the judged epoch with class
     `systematic-invalid` that is not the window's own (BRK 2577 to 2584 finds them). The function appends
     `new_systematic_failure_challenges_preflight_screen` to `observed_triggers` as it does today. It does not
     take the early return at BRK 2589 to 2602. It goes on to select and compare the window's endpoints.
   - (b) *A valid capture outside the range of the 24*, whether it belongs to the window or to another session
     (BRK 2562 to 2576). The function appends `new_valid_same_identity_capture_expands_observed_range` as today.
     The name is no longer in the set that fails the bracket at BRK 2709 to 2728.
   - (c) *The doubling count at or above 48* (BRK 2544 to 2554). The function appends
     `corpus_doubles_from_24_to_48` as today. The name is no longer in the set that fails the bracket at
     BRK 2709 to 2728.

4. **What fails a governed bracket, each exactly as sealed.** The order of the checks is the function's present
   order.
   - An acceptance file that is missing, unauthenticated or not issued (BRK 2157 to 2184). A ledger that fails
     its integrity checks, or whose baseline is not the acceptance's cutoff (BRK 2204 to 2220). An incomplete
     list of candidate captures (BRK 2358 to 2359, 2366 to 2385). A list of set-aside captures that cannot be
     resolved for the doubling count (BRK 2539 to 2543).
   - `identity_field_change`: any of the six identity fields differs (BRK 2257 to 2261, 2317 to 2320).
   - A missing or invalid bracket binding (BRK 2422 to 2475).
   - A post-cutoff capture whose class is none of the three words (BRK 2531 to 2536).
   - *The window's own capture with class `systematic-invalid`.* The function takes the early return at
     BRK 2589 to 2602 with reason `calibration_acceptance_bound_stale`, as today. In practice this can only be
     the window's post capture, because a pre capture of that class stops the chain and aborts the session
     (section 2, attempt 3), so the harvest stops at `calibration.no_bracket` (H 4502 to 4505) and never calls
     the function. A window whose post capture is above the screen is also removed by
     `calibration.capture_invalid` (H 4514 to 4518), which does not depend on the bracket evaluation.
   - Missing or old endpoints (BRK 2619 to 2625), an endpoint that does not belong to the bound session
     (BRK 2643 to 2644), a bound that is not a finite non-negative number (BRK 2647 to 2653).
   - *The window's own pre bound above the screen* (BRK 2697 to 2707), reason
     `instrument_calibration_mismatch`.
   - `protocol_or_estimator_byte_change` (BRK 2494 to 2499), which still fails the bracket at BRK 2709 to 2728
     with reason `calibration_acceptance_bound_stale`.
   - *The window's own drift above the drift ceiling* of 15.502 ms (BRK 2746 to 2747), reason
     `instrument_calibration_mismatch`.

5. **A window's own capture outside the range or above the screen: the complete case list.** Write p for the
   pre bound and q for the post bound of a governed window.
   - p above the screen (36.46 ms): the chain stops before any member. Removed. Unchanged.
   - q above the screen: class `systematic-invalid`, the window's own. Removed (item 4). Unchanged.
   - p or q below 21.93 ms, the bottom of the range: the capture is `valid`; event (b) is recorded; the bracket
     does not fail for it. The drift ceiling still applies, so a window with p = 20.5 ms and q = 36.4 ms fails on
     a drift of 15.9 ms.
   - p or q at or below the screen and above the largest of the 24: the screen's operative value is the largest
     of the 24 rounded up in its seventeenth decimal place (`0.036462861644980` against
     `0.03646286164497997`), so such a capture can exist only in a gap of 3 × 10⁻¹⁷ s. It would be `valid` and
     event (b) would be recorded.
   - p and q both inside the range: no event of the window's own.
   - In every case the window's two captures count toward the doubling count, and event (c) is recorded when
     the count reaches 48.

6. **What the function returns for a governed bracket.** As at pin `0699abbb0`, plus four keys under
   `acceptance.prospective_rederivation`: `trigger_scope` (`"window_evidence"`); `recorded_only_triggers` (the
   names of the events of item 3 that were observed, in the order (c), (b), (a), possibly empty);
   `corpus_doubling` (`{"count": <the largest per-epoch count of BRK 2544 to 2552>, "threshold": 48}`); and
   `other_session_systematic_sequences` (the ledger sequences of the captures of event (a), ascending).
   `observed_triggers` keeps its present meaning and lists every observed name. `acceptance.freshness.status`
   stays `fresh` when the only observed triggers are recorded-only ones. `status` is `passed` and the reasons are
   empty exactly when no check of item 4 failed; the operative bound and the allowance are computed as today
   (BRK 2749 to 2765).

7. **The flag.** The harvest emits `calibration.bracket_acceptance_failed` under the unchanged condition of
   H 4595 to 4597: a status other than `passed`, or any reason. A recorded-only trigger is neither. No flag code
   is added, removed or reclassified: the catalog is a sealed file that a window's plan names, and a new code
   would be unclassified until a catalog erratum.

8. **What the harvest writes into `harvest.json`.** One new top-level object, `calibration_bracket`, written by
   every harvest of the new program:
   ```
   {"erratum_3_governed": true or false,
    "trigger_scope": "window_evidence" or "sealed",
    "evaluated": true or false,
    "status": the function's status word, or null when the function was not called,
    "reasons": the function's reason codes, sorted,
    "freshness": "fresh", "stale" or null,
    "observed_triggers": [...],
    "recorded_only_triggers": [...],
    "corpus_doubling": {"count": N, "threshold": 48} or null,
    "other_session_systematic_sequences": [...]}
   ```
   These are trigger names, reason codes, counts and ledger positions. None is an energy. `evaluated` is false
   when the harvest stopped before the call (for example at `calibration.no_bracket`). Before this erratum
   `harvest.json` carried the flag code without its reason, which is how attempt 4's cause was misread.

9. **The stored verdict of a governed window, and how the harvest treats it.** The verdict writer is the
   measurement clone's sealed program and keeps the sealed rule, so on every governed window whose ledger holds
   row 456 the stored verdict will record a failed bracket with the condition
   `calibration_acceptance_bound_stale`, no endpoints and no operative bound. The harvest decides nothing by
   that part of the stored verdict: REG 4154 to 4155 already says of the calibration bracket that
   `calibration.bracket_acceptance_failed` is the code "which the harvest evaluates itself". The stored verdict's
   failure surfaces as `whole_window.not_passed`, which the catalog classes `DISCLOSE`, with the stale condition
   listed in its `observed.conditions`. Question Q-B in section 7 gives the trace that shows no window-removing
   code follows from it.

10. **Claim consumers** (the form of this item depends on the ruling on Q-C and Q-D). A claim consumer that
    evaluates a window's calibration bracket does so the way that window's harvest did: over the copy of the
    ledger in that window's harvest archive (`sources/ledger/calibration_observation_ledger.jsonl`), through the
    terminal pin in `derived/terminal-pin.json`, with the binding in `derived/bracket-binding.json`, and with
    `trigger_scope` `"window_evidence"` exactly when the attempt is governed. For a governed window it does not
    require the stored verdict's calibration bracket to equal its own (WW 5560 to 5566), does not veto on the
    stored condition `calibration_acceptance_bound_stale`, and authenticates the common launch lineage against
    the bracket it evaluated, because the stored verdict's basis carries none (Q-D). The membership, provenance
    and physics checks stay independent. This is analysis code that never runs during collection; it is assigned
    to lane L9 of AP section 11 as a new row, here called L9-BRACKET, and must land before any claim is
    computed. Until it does, no number of a governed window is claimable, which is already true of every block-5
    window (REG 1241 to 1243).

11. **The re-derivation.** A new acceptance, derived under a new calibration pre-registration, falls due before
    any later measurement block is sealed. It is no longer due before the next window of block 5. The lead
    records each harvest's `recorded_only_triggers` in the block's attempt history.

12. **Attempts that are not governed.** Every attempt with `t0_epoch_s` at or before ADMIT is judged under the
    sealed rule. That includes BETA attempts 4 and 5, which stay collected, not claim-usable
    (`calibration.bracket_acceptance_failed`), kept and disclosed, their energies never analysed. They are never
    harvested by the new program for a deciding record. A run of the new program over one of them is
    exploratory, is labelled so (REG 4844), and changes no verdict, `claim_usable`, cause key or attempt history.
    A re-harvest may change `claim_usable` only "with a repaired program" (REG 4696 to 4697); the program was not
    defective.

**Worked example (the ledger as it stands at sequence 478; the governed window's two bounds are invented).**
A governed BETA attempt opens session S. Its pre capture reads 28.00 ms and its post capture 30.50 ms; both are
`valid`. The harvest reads the ledger up to the session's last entry and calls the function with
`"window_evidence"`.

- Identity: the six fields match the judged epoch. Binding: valid, own session S.
- Protocol and estimator bytes: equal to the acceptance's record. Not observed.
- Doubling: 41 + 2 = 43, below 48. Not observed.
- Range: the 19 valid post-cutoff captures run from 25.26 to 31.86 ms, inside 21.93 to 36.46 ms. Not observed.
- Systematic: row 456 has class `systematic-invalid`; its session is attempt 3's, not S. Observed, recorded
  only. The function goes on. (With `"sealed"` it returns here, stale, and the window is removed.)
- Endpoints: the two captures of S. Pre 28.00 ms is at or below the screen.
- Failing triggers: none.
- Drift: |30.50 − 28.00| = 2.50 ms, below the 15.502 ms ceiling.
- Operative bound: max(28.00, 30.50) + max(2.50, 14.531) = 45.031 ms. Status `passed`, no reasons. No flag.
- `harvest.json`: `observed_triggers` and `recorded_only_triggers` both
  `["new_systematic_failure_challenges_preflight_screen"]`, `corpus_doubling` `{"count": 43, "threshold": 48}`,
  `other_session_systematic_sequences` `[456]`.

Four variants. With a post capture of 37.00 ms the ledger classes it `systematic-invalid`; it is the window's
own; the window is removed as sealed. With pre 21.00 ms and post 24.00 ms event (b) is recorded, the drift is
3.00 ms and the bracket passes with an operative bound of 24.00 + 14.531 = 38.531 ms. With pre 21.00 ms and post
36.40 ms the drift is 15.40 ms, under the ceiling, and the operative bound is 36.40 + 15.40 = 51.80 ms. Three
finished windows later the count is 49, event (c) is recorded, and the bracket still passes.

**Why this cannot let a window with a bad bracket pass.** Every comparison of the window's own two captures with
the screen and with the drift ceiling is untouched, as are the identity, byte, binding and ledger checks. The
operative bound is computed by the same formula from the same two captures. What changes is only whether the
existence of certain other entries in the ledger fails the window.

## 5. What does not change, and mechanics

- **Unchanged.** The acceptance file's bytes and every number in it (the screen, the padding, the drift
  ceiling); the five triggers' names and their definitions; the flag catalog and every code's effect; the
  ledger and how a capture is classed; the in-window pre screen and the chain; the verdict writer; the roster;
  the blinding rules; every file a window reads; the measurement clone, the claim head and the seal commit. The
  registration's bytes are not edited: this is a separate document, and the registration digest every plan
  carries stays `c7b3fdf7…db3f`.
- **Changed.** The desk checkout only: `joulewise/calibration_bracketing.py`, `joulewise/b5/harvest.py`, and
  tests. After the change the desk copy of `calibration_bracketing.py` differs from the measurement clone's.
  REG 4777 to 4779 covers this case: a desk program's change "changes no collection code even when the file it
  changes is also imported inside a window from the measurement checkout". The change is never committed,
  merged, pulled or checked out in the measurement clone.
- **Addendum 4 to the seal record, in two steps**, on the pattern of Addendum 3. *Step 1, before the arm of any
  governed attempt:* this erratum's path and the SHA-256 of its admitted text as committed on main; the line
  `ERRATUM-3-ADMITTED-AT: <UTC time, ISO 8601>`, no earlier than that commit's committer time and earlier than
  the next attempt's t0; the pin-scoping paragraph. *Step 2, before any governed attempt is harvested:* a
  `B5-HARVEST-PIN:` line with the implementing commit, its files and their SHA-256s (now including
  `joulewise/calibration_bracketing.py`), and the path of its gate record.
- **Pin scoping.** Three pins then stand. `224a264c5` for attempts with t0 at or before
  `ERRATUM-2-ADMITTED-AT` (2026-10-10T16:30:00Z). `0699abbb0` for attempts with t0 after that and at or before
  ADMIT, which are BETA attempts 2, 3, 4 and 5. The new pin for governed attempts. The analysis checks each
  attempt's recorded harvest commit against the pin that governs it (AP 2.2).
- **Gates on the implementing program**, as for pin 3 (`sources-erratum/harvest-pin3-gates.md`): an item-by-item
  check against section 4; an independent executing review; the lane's tests and the whole suite; a cold Fable
  5.1 pass; and the before/after comparison on the rehearsal copy, in which a window harvested with `"sealed"`
  must give byte-identical `derived/` output to pin `0699abbb0`.
- **Arm before pin.** A governed attempt may be armed once step 1 is on main. The admitted text is frozen at
  admission. The program under gates is not run over a governed attempt's bytes before step 2 exists. If the
  gates find, from code and text alone, that no program can implement this text exactly, the attempt armed under
  it is harvested by pin `0699abbb0` and judged under the sealed rule, which removes it; a corrected erratum
  governs later attempts.
- **Re-harvest.** A later re-harvest of a governed window is given that window's archived ledger copy and
  terminal pin, as the magistrate brief already requires for any window that is no longer the newest in the
  ledger.
- **Release event.** It ties this erratum's SHA-256 beside those of the registration, the analysis plan, the
  catalog and Erratum 2.

## 6. Registered deviations and disclosures (what the paper must say)

Proposed as item 11 of the list in REG section 10.

1. From ADMIT on, three of the acceptance's five re-derivation triggers were recorded and did not remove a
   window: a capture above the screen in another session, a valid capture outside the range of the 24, and the
   capture count reaching 48. For each analysed window the paper lists which of the three were on record at its
   harvest, the doubling count, and the ledger sequences of the systematic captures.
2. On 2026-10-10 one pre capture read 44.38 ms against a 36.46 ms screen, about 4.2 sample standard deviations
   above the mean of the 24 captures the acceptance rests on, with no competing process in the monitor's journal,
   and the next capture 46 minutes later read 31.41 ms. The cause is not established. The acceptance was not
   re-derived inside block 5; a re-derivation is owed before the next block.
3. A window's operative bound is built from its own two captures and a padding of 14.531 ms. It does not prove
   that the alignment bound stayed below that value between the two captures. Of the seven finalized brackets
   recorded after the cutoff, three have an operative bound of at least 44.38 ms (44.64, 45.67 and 46.40 ms) and
   four fall short of it by 0.33 to 1.90 ms (operative bounds 42.48 to 44.05 ms). What is printed for this
   depends on the ruling on Q-A.
4. BETA attempts 4 and 5 completed their chains and were removed by the registered rule, not by anything
   measured in them. Attempt 4 also spanned a sleep of the machine. Neither is analysed. They are listed in the
   attempt history with this cause, and the paper's count of attempts per pack includes them (REG 4810 to 4822).
5. The registered rule required the lead to stop arming after attempt 3 (REG 2509 to 2511). Two further
   attempts were armed before the rule was applied. The decision of 2026-10-10 that armed attempt 5 unchanged
   misread attempt 4's cause.
6. The rule was changed after attempts 3, 4 and 5 had been collected and their yield counts were known. No
   energy of any block-5 window had been read. The change does not apply to them.
7. ALPHA's analysed window was judged under the sealed rule and BETA's and GAMMA's will be judged under the
   amended one. All three share one acceptance, one screen, one padding and one drift ceiling, and the checks on
   each window's own two captures are identical.
8. The stored verdict of every governed window reads failed with the condition
   `calibration_acceptance_bound_stale`, because its writer is sealed and keeps the sealed rule. The paper states
   that the deciding evaluation is the harvest's.
9. The screen is the largest of 24 captures, so about 1 window in 25 is stopped at its pre capture with nothing
   wrong. That is unchanged and is a cost of the design, to be reconsidered at the next block's registration.

## 7. Questions for the judge

### Q-A. Should a number be printed for an excursion between a window's two captures?

*What was found.* The operative bound is max(pre, post) + max(|post − pre|, 14.531 ms) (BRK 2749 to 2750). Its
smallest possible value is 21.93 + 14.531 = 36.46 ms, which equals the screen by construction. Row 456 is the
largest bound of any capture with sound evidence in the judged epoch: 44.38 ms. The operative bound enters three
quantities, not one. (i) The attribution floor of each cell, printed beside the cell and never added to its
interval (AP 255 to 256; REG 5187 to 5191). (ii) The term B inside each cell's interval, through the stratified
average of the same per-member bound (AP 234, 246; REG 913 to 924). (iii) The comparative detection floor, whose
shared-edge sweep runs over [−b, b] with b the operative bound (AP 312 to 313). To first order (i) and (ii) are
proportional to the operative bound (REG 895 to 896). The figures of section 6 item 3 give the size: against
44.38 ms the seven recorded brackets fall short by 0% to 4.5%, and the worst bracket the rule admits by 21.7%.

*What the trigger protected.* The systematic trigger said: a capture above the screen means the 24 may no longer
describe the instrument, so stop relying on numbers derived from them. Two of those numbers bear on a later
window: the screen and the padding. The screen is re-tested on that window's own captures. The padding is the
range of the 24, and row 456 lies 7.91 ms outside that range, so the padding is the number row 456 calls into
question.

*Options.*

- **A1, print beside (the Opus seat's proposal).** For each governed window that carries an observed trigger,
  the analysis also prints each attribution floor under the wider bound max(operative bound, 44.38 ms), labelled.
  For: it answers the excursion question with a number, costs no window, and leaves every interval as
  registered. Against: it widens only quantity (i); it applies to BETA and GAMMA and not to ALPHA attempt 1,
  whose instrument was the same and whose acceptance read fresh only because the excursion had not yet been
  seen; and it is a change to the analysis plan, which needs its own text and the analysis lane's pin.
- **A1′, print beside for every analysed window of the block**, labelled as a sensitivity value, with the bound
  max(operative bound, largest bound of any capture with sound evidence in the judged epoch at the release
  event). For: one treatment for all three windows; a labelled extra value is not a change of rule for a
  completed attempt (REG 4844 allows analyses not registered when they are labelled). Against: the same
  limitation to quantity (i) unless B and the detection floor are also recomputed as sensitivity values.
- **A2, compose.** Use the wider bound as the operative bound of a window that carries an observed trigger, so
  that (i), (ii) and (iii) all widen. For: it is the only option under which every number that depends on the
  bound is covered against a repeat of the largest excursion seen. Against: it changes reported intervals and
  can turn a contrast `not_resolvable`; it treats one unexplained capture as the instrument's standing bound;
  and it makes a later window's numbers depend on another session's capture, which is the dependence this
  erratum removes.
- **A3, neither.** Disclose row 456 and the shortfalls (section 6 items 2 and 3) and print nothing more. For:
  the operative bound never claimed to cover an excursion between captures, for any window of any block; the
  excursion is one event in 42 captures. Against: the paper would carry a known, measured counter-example to its
  own timing bound with no number beside it.

### Q-B. What does the sealed verdict writer's failed bracket do in the harvest of a governed window?

*Trace.* The harvest starts the clone's writer with the clone's ledger and committed pin and no
consumption-semantics argument (H 5743 to 5750), so the writer runs with its default, minted, semantics
(RC 814 to 821) and builds no consumption session (RC 8419 to 8445): it cannot abort on a failed bracket. The
writer evaluates the bracket last, and adds its reasons to the conditions (RC 7363 to 7398). The row is written
with status `failed`.

The harvest reads the stored verdict in three places.

1. H 4847 to 4850: no verdict file gives `whole_window.verdict_absent` (`EXCLUDE_WINDOW`). The file exists, so
   it does not fire.
2. H 4876 to 4889: a status other than `passed` gives `whole_window.not_passed` (`DISCLOSE`), and, only if the
   row's `member_failures` list is absent or malformed, `whole_window.member_failures_unreadable`
   (`EXCLUDE_WINDOW`). The writer always writes a well-formed list (RC 8483 to 8494, 8572).
3. H 4934 to 5057: `neg8.screen_failed` (`EXCLUDE_WINDOW`) from the stored row's separate drift screen. Since
   the erratum of 2026-10-09 the harvest re-runs that screen itself on every window and its own result decides.
   The writer computes that screen before, and independently of, the calibration bracket.

The harvest also validates the row (H 4867 to 4875) and records `whole_window.verdict_unauthenticated`
(`DISCLOSE`), which the catalog's own note says is recorded on every harvested window.

*Observed.* Attempts 4 and 5 are exactly this state: a stale stored bracket. The drafter printed codes, counts
and status words from their archives and from ALPHA attempt 1's (a fresh bracket) for comparison.

| | BETA attempt 5 | BETA attempt 4 | ALPHA attempt 1 (second seal) |
|---|---|---|---|
| stored verdict status | `failed` | not printed | `failed` |
| stored calibration bracket | `failed`, no endpoints | not printed | `passed` |
| stored conditions | the stale one, two drift-bound ones, `whole_window_bundle_invalid` | not printed | the same without the stale one |
| `member_failures` | a list, well formed | not printed | a list, well formed |
| `whole_window.not_passed` | 1, `DISCLOSE` | 1, `DISCLOSE` | 1, `DISCLOSE` |
| `whole_window.verdict_unauthenticated` | 1, `DISCLOSE` | 1, `DISCLOSE` | 1, `DISCLOSE` |
| harvest's own drift screen | evaluated, `passed` | evaluated, `passed` | evaluated, `passed` |
| window-removing codes | `calibration.bracket_acceptance_failed` only | the same only | none |

*Result in words.* On a governed window the stored verdict will read failed for one more reason than on a fresh
window, and the only flag that follows from that is `whole_window.not_passed`, which removes nothing and is
recorded on every block-5 window already. The one window-removing code that the stale state produces is the
harvest's own `calibration.bracket_acceptance_failed`, and that is the code item 3 of the rule stops. No other
path removes a governed window for this cause. Item 9 of the rule says so.

*For the judge.* Confirm item 9, or name a path the trace missed. Two paths were not exercised and are listed
in section 8: a GAMMA window in this state, and a window in this state that also needs Erratum 2's recovery.

### Q-C. Which ledger does a claim consumer read, and is ALPHA attempt 1 refused there?

*What was found.* The consumption session, the object through which analysis code reads a window's members,
loads the ledger from default paths when it is not handed one (WW 521 to 536): `runs/…ledger.jsonl` and the
committed pin under the root of whichever checkout the code is imported from (CL 107 to 111). The analysis
engine does the same (`joulewise/analysis_engine/inputs.py` 1758 to 1772 and 3282 to 3296). It then re-evaluates
the bracket with the unchanged function (WW 707 to 735) and refuses the whole window when the result carries no
operative bound (WW 736 to 748), which is the case for a stale result; `calibration_acceptance_bound_stale` is in the engine's list of refusals
(`joulewise/analysis_engine/claims.py` 64). The desk checkout has no ledger file of its own, so a consumer run
from it with the defaults refuses for a missing ledger; a consumer pointed at the clone's live ledger reads
row 456.

*Consequence for ALPHA attempt 1 of the second seal* (claim-usable; harvested by pin `224a264c5` from a ledger
of 432 entries, in which the acceptance read fresh). Evaluated at release time against the live ledger, its
bracket is stale under the sealed function, because the check at BRK 2577 to 2602 reads every post-cutoff
capture in the snapshot it is given, whatever the window's date. ALPHA attempt 1 is not governed, so
`"window_evidence"` does not apply to it either. It would be refused. The drafter did not execute this; it
follows from the code as read, and the Opus seat's executed probe shows the same function returning stale on
the live ledger for any window.

*The sealed text does not ask for that.* It says "every later window's bracket fails" (REG 2507 to 2508), it
defines the ledger a window is judged on as "read up to this window's terminal entry" (REG 4011), and it makes
the harvest's evaluation the deciding one (REG 4154 to 4155). An earlier window going stale because of a later
capture is an effect of the consumer's default path, not of the registered rule. The archived ledger copies are
byte prefixes of the live ledger (checked by the drafter: 432, 442 and 478 entries against 478).

*Options.*

- **C1.** Admit item 10 as written: every claim consumer evaluates each window's bracket over that window's
  archived ledger copy and terminal pin. For ALPHA attempt 1 this is the registered rule made explicit and needs
  no change of scope. Lane L9-BRACKET implements it before any claim is computed.
- **C2.** Leave the consumer out of this erratum and name the follow-on only. The risk is that the analysis
  lane is built against the live ledger and refuses ALPHA's window at the release event, when nothing can be
  re-collected.
- **C3.** Have the consumer take the bracket from the harvest's `withheld/bracket-evaluation.json` instead of
  re-evaluating it. Simpler, but it removes an independent re-derivation the analysis now makes.

### Q-D. Does anything downstream of a passing bracket take a different path for a window with recorded triggers?

*In the harvest: no.* The function's result is used in one place: it is written to
`withheld/bracket-evaluation.json` and it decides whether the one flag is emitted (H 4588 to 4597). No other
step of the harvest reads the result or the operative bound (the string `b_fiducial` does not occur in H). The
member checks read each member's own files and flags; the cell minimum is computed from the flags and the
roster by the exclusion function (H 8054 to 8056). A governed window with a passing bracket and recorded
triggers takes the same path through the rest of the harvest as a fresh one.

*In the stored verdict, and so in any claim consumer that reads it: yes, in four ways.* Each comes from the
sealed writer's early return, which leaves the stored bracket without endpoints.

1. The stored verdict's basis records no calibration pair (`calibration_bracket_set.pre` and `.post` are null:
   WW 2557 to 2596; observed on attempt 5). A consumer that recovers the bracket binding from the basis gets
   nothing (WW 557 to 637) and must be handed `derived/bracket-binding.json`.
2. The basis carries no `launch_lineage`, because the writer builds it from the bracket's pre endpoint (WW 2639
   to 2678; observed: attempt 5's basis has no such key, ALPHA attempt 1's has it). A consumer's launch check
   refuses a basis without it (`launch_consumption_missing`, WW 6054 to 6058). Erratum 2 item 7 says the common
   launch lineage "is bound through the basis"; on a window governed by this erratum it is not.
3. A consumer that compares the stored bracket with its own evaluation refuses on any difference
   (`whole_window_verdict_conflict`, WW 5560 to 5566). Under `"window_evidence"` they differ.
4. A consumer that evaluates the bracket with the unchanged function, or with the default scope, gets stale and
   refuses the window (Q-C).

None of the four can print a wrong number; each refuses. Item 10 assigns all four to lane L9-BRACKET.

*For the judge.* Rule whether item 10 is sufficient as a named follow-on, or whether the launch-lineage point
(2) must be settled in this erratum because it touches what Erratum 2 item 7 relies on.

## 8. What was not verified

- The amended function does not exist yet. Nothing in section 4 has been executed.
- The drafter did not run the sealed bracket evaluation. The stale result on the live ledger rests on both
  seats' executed probes, on reading BRK, and on the status words printed from attempt 5's stored verdict and
  flags.
- No GAMMA window has been harvested in the stale state. Q-B's trace for GAMMA is from code that is common to
  the three packs. GAMMA also runs the desk provenance checker, whose codes are all `DISCLOSE` in the catalog;
  its code was not traced.
- A window in the stale state that also needs Erratum 2's recovery (a reference spare that left no bundle) has
  not occurred. Erratum 2 item 7(b) requires the stored basis to validate. That validation is a self-consistency
  check (WW 5898 to 5978), and attempt 5's basis did validate on the recorded-source path, but the combination
  was not exercised.
- What `build_calibration_bracket_binding` does when a window's own post capture is `systematic-invalid` was
  not traced. The window is removed by `calibration.capture_invalid` in any case.
- Attempt 3's chain stopped with exit code 11 (`pre_calibration_capture_failed`). REG 2656 to 2657 and REG 4007 to 4009
  give exit 11 to a failed pre capture and exit 12 to a pre bound above the screen. The window was removed either way; the difference was not
  investigated.
- The capture tool's function that derives the in-window screen was read only as far as its inputs. That it
  returns the acceptance's `preflight_level_screen_s` is inferred from row 456's class.
- The probabilities of section 3.3 assume exchangeable captures. That was not tested.
- Why row 456 read 44.38 ms.
- No analysis code for block 5 exists yet (lane L9). The findings of Q-C and Q-D describe the consumers in the
  desk checkout as they stand.
- The joule figures of the thresholds audit that the Opus seat cites were not used and not checked.

## Drafter's dissent

No dissent from the substance of the decision. Three points where the drafter would go further or differently;
none is written into section 4.

1. **A repeat has no rule.** Under section 4 a second or third capture above the screen in another session is
   recorded like the first, without limit. The drafter would add a process rule for the lead, not a program
   refusal: a second post-cutoff `systematic-invalid` capture of the judged epoch inside block 5 sends the next
   spend to a consult before the next arm. Two such captures in about 20 are still within chance at 4% each
   (about 19%), so this is a prompt to look, not evidence of a fault.
2. **On Q-A the drafter prefers A1′ to A1.** A wider bound printed only for windows that happen to follow
   row 456 presents ALPHA's window as better calibrated than BETA's, when the instrument was the same and only
   the order of events differs. If a number is printed, it should be printed for every analysed window of the
   block. The drafter also notes that the proposal as the Opus seat wrote it covers the attribution floor only,
   while the operative bound also sits inside each interval and inside the comparative detection floor; the
   judge should rule knowing that.
3. **On Q-C the drafter would not leave the consumer to a follow-on alone (option C2).** The failure it guards
   against would be found at the release event, when ALPHA's window can no longer be re-collected under the same
   seal. Item 10 should be admitted as part of this erratum.
