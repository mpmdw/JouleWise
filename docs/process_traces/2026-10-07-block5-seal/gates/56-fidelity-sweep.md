# REG_FIDELITY: where the block-5 registration, analysis plan and flag catalog disagree with the code at `9b0c680ed`

Consolidated by Opus 5.5 on 2026-10-07 for the registration writer and the orchestrator, from fifteen fidelity
readers (twelve chunks of the registration, two of the analysis plan, one of the flag catalog) and the refuters who
re-derived their findings. Nothing here was armed, emailed or committed. The consolidator wrote only this file.

## How to read this file

**Code head.** `/Users/edr/code/JouleWise-wt-int5` at `9b0c680ed79d5c7b72b4b39ed04b9fe51dd116d4`, read-only.

**Two copies of each document, with different line numbers.**

- **int5 line**: the copy under `configs/campaigns/v5_claim_25g83/` in the int5 worktree. It is revision 9. Every
  reader and refuter cited these lines.
- **draft line**: the copy in `/Users/edr/code/JouleWise-wt-ia-claim` (branch
  `design/2026-10-05-v5-claim-block-draft`) at head `1d97f0a60`. It is revision 10 and is the copy the writer edits.
  The consolidator located every quoted sentence in that copy by text search. If the draft has moved past
  `1d97f0a60`, search for the quoted words instead of trusting the number.
- `flag_catalog.json` has the same line numbers in both copies. The analysis plan has the same line numbers in both
  copies up to line 468; after that the draft is 13 or 14 lines higher.

**Status words.** CONFIRMED means a refuter reproduced the mismatch from scratch at `9b0c680ed`. "Consolidator
checked" means no refuter saw the item and the consolidator checked it in the text and the code. Bracketed ids are
the readers' ids, so each entry can be traced to its chunk file in this directory.

**Each entry gives:** the text as written, the true fact, the evidence, and the smallest correction as a fact. The
writer writes the sentence.

**Two constraints on the edit, from the reg-prep lane's notes** (`../reg-prep/NOTES.md`):

1. `tests/fixtures/d165_rationale_allowlist.json` in int5 names line 354 of the analysis plan (the "common-time"
   sentence; the consolidator confirmed it is on line 354 in both copies). A correction above that line must leave
   the number of lines above 354 unchanged. This touches B42, B43, R6 and the plan's undefined terms U51 to U55.
2. `scripts/digest_pin_census.py` counts 64-character hexadecimal literals under `configs/`. B3 and B43 add or
   replace such literals, so the census count changes when they are corrected.

## Counts

| Quantity | Count |
|---|---|
| Claims the readers checked | 2,011 |
| Mismatches the readers reported | 143 |
| Sent to a refuter | 73: 73 CONFIRMED, 0 REFUTED |
| Not sent to a refuter | 70: 7 readability mismatches (consolidator checked, all hold) and 63 undefined-term reports |
| Distinct confirmed facts after merging twins | 69 (four pairs merged: H-1 with reg03-M1; H-2 with reg-11-M4; reg-08a-01 with reg-10-M4; reg-06-shape-a-03 with reg-11-M1) |
| List A: bears on a number, an exclusion or collection behaviour | 20 (A0 is already repaired in the draft; A1 to A19 are open) |
| List C: the code disagrees with the registered design, to decide before the seal | 3 (C1 to C3) |
| List B: record-only | 46 (B0 is already repaired in the draft; B1 to B45 are open) |
| List R: readability mismatches no refuter saw | 7 |
| List U: undefined terms | 60 rows from 63 reports (the three "courier" reports and the two "dwell" reports are merged); two further undefined terms were confirmed by a refuter and stop or resize collection, so they sit in list A (A4, A10) |

Catalog and plan sentences that repeat a registration sentence are named under "Twins" in the registration entry and
are not counted again.

## List A. Confirmed mismatches that bear on a number, an exclusion or collection behaviour

Ordered by document, then by the first line the writer must change.

### Registration

#### A0. The census rule for JavaScript runtimes (already repaired in draft revision 10) [H-2, reg-11-M4] CONFIRMED

- **Where.** int5 lines 224-225 (revision 9 list, item 1), 3252 (§13 row "interpreter rule"), 3490-3492 (§16) and
  the §4.5 sentence. In the draft the old wording survives only as dated history (draft 230-232, 3407, 3699-3701),
  each time with a note that revision 10 restates the rule.
- **Text (int5).** "A JavaScript runtime is an agent when any element of its command line names an agent's package
  or install path, with no option parsing (the pending commit)."
- **True.** The rule is merged, not pending (rule commit `2524637ae`, merge `84661ddb3`). A process is a JavaScript
  runtime when the file name of its executable or of its first argument starts with `node`, `bun` or `deno`. It is
  an agent when any argument, the first included, holds a piece that starts with `claude` or `codex`, where each
  argument is lower-cased and cut at `/`, `\`, white space, quotes, back-ticks, brackets and `= , ; : +`. That is
  wider than a package or install path: `node /tmp/codexample.js` and `node app.js --label claudette` are agents; a
  piece such as `.claude` does not match. A runtime that names no agent but carries, after its first argument, one
  of `-`, `-e`, `-p`, `-pe`, `--eval`, `--print`, `eval`, or an argument starting `--eval=` or `--print=`, is
  "undecided" and is kept as a census hit (reason `undecided_launch`), which stops the arm like an agent.
- **Evidence.** `joulewise/agent_identity.py` at `9b0c680ed` (SHA-256 prefix `95a39571c27ea9e6`): `AGENT_PREFIXES`,
  `SCRIPT_INTERPRETERS`, `_COMPONENT_SPLIT`, `UNNAMED_CODE_ARGS`, `identify()`. Two refuters ran `identify()` on
  the cases above.
- **Draft status.** Revision 10 item 1 (draft 256-269), §4.5 (draft 1487 on) and the §13 row of `B5-REV10-SYNC`
  (draft 3441) state both the wider match and the undecided case. Nothing is left for the writer except to recheck
  the file's digest at the final head.

#### A1. §0.14, when a member's clock anchor is `bounded` [reg-02b-M3] CONFIRMED

- **Where.** int5 730-731; draft 776-777.
- **Text.** "A member is **`bounded`** when its stream's summed record time is at least 60 s and its effective bound
  is at most 5 ms."
- **True.** Under the default method (v3) a member is bounded only if all of these hold. (a) The record durations
  after the first record, that is from the first record's end point to the last record's end point, sum to at
  least 60 s, and the controller's own monotonic coverage from before the sampler was spawned to after its output
  was parsed is at least that long. A stream whose records sum to between 60 s and 60 s plus its first record
  passes the sentence and fails the code. (b) The whole-second labels roll over at least twice. (c) The fitted
  clock rate stays within 50 parts per million of 1. (d) The first parse lag is between 0 and 0.25 s. (e) The
  effective bound is at most 5 ms. (f) The records pass their health checks (whole-second, non-decreasing labels;
  energy consistent with power times time) and the fit is not empty. A failure of any of these gives
  `member.anchor_not_bounded`, which removes the member.
- **Evidence.** `joulewise/uncertainty_evidence.py`: 1065-1070 (sum over `exact_elapsed_ns[1:]`, 60 s test), 1081-1086
  (coverage), 1058 (`MIN_NATIVE_ROLLOVERS = 2`), 1260-1267 (50 ppm), 1284-1293 (0.25 s), default method at 882;
  `joulewise/b5/harvest.py:3880-3881` (the flag).
- **Correction (fact).** The 60 s is counted from the end of the first record, not over all records. The two
  conditions written are not the whole test: conditions (b), (c), (d) and (f) also decide. The separate 5 ms cap on
  the wall-minus-monotonic change need not be named, because the 5 ms effective bound already implies it.

#### A2. §0.15 and §9.2 item 4, "any battery current" at the arm [reg-10-M3] CONFIRMED

- **Where.** int5 752 and 3009; draft 798 and 3161.
- **Text.** "at the arm, any battery current while the machine is idle" (§0.15); "the arm still refuses any battery
  current at idle (§4.2)" (§9.2).
- **True.** The arm refuses only when the magnitude of the battery current is above 200 mA, in either direction. A
  current of 200 mA or less passes. The same limit applies to the registry's InstantAmperage when the SMC value
  B0AC cannot be read.
- **Evidence.** `joulewise/hazards/battery.py:437-438` (`abs(current) > limits["limit_ma"]`), `:131`;
  `joulewise/battery_float.py:37` (`LIMIT_MA = 200`). The registration's own §4.2 (int5 1269) and §4.3 (int5 1340,
  `limit_ma` 200) say the same.
- **Correction (fact).** Both sentences: battery current above 200 mA in either direction at idle.

#### A3. §4.2, the clock rules at the arm [reg-04-arm-a-01] CONFIRMED

- **Where.** int5 1199-1206 and 1226-1227; draft 1266-1273 and 1293-1294.
- **Text.** "*Arm, all four must hold:* ... (iii) Each anchor read pair is taken within 1 ms. (iv) f is identical at
  dwell start, dwell end and GO"; and "The arm's dwell samples are re-read the same way against the arm's own
  bound, skew_max_ns = 1 ms, rule iii above".
- **True, part 1.** The code has a fifth refusal: the boot session identifier read at the start of the dwell differs
  from the one read at the end ("boot session changed during the dwell"). The registration's clock rule never
  mentions a boot session.
- **True, part 2.** During the dwell, rule iii cannot refuse. Each one-per-second sample is read up to five times
  against 1 ms. A sample whose five reads all exceed 1 ms has no anchor. One such sample among the dwell's 180 to
  2,700 samples (or any failed sample read, or an unread boot session) makes the verdict of the whole dwell-and-GO
  series UNMEASURED. The arm records `clock.arm_unmeasured` (disclosed) and continues, and rule ii (residual within
  1 ms of its start), rule iv (f identical) and the boot-session check are not judged for that dwell. Rule iii
  refuses only at the arm's instant clock read, where the last of five over-limit reads is kept and judged.
- **Evidence.** `joulewise/hazards/clock.py`: 327-328 (boot session), 189-193 (sample with no anchor), 236-239 (one
  failed sample sets the series error), 291-292 (UNMEASURED before the series is judged), 216-220 and 311-313
  (instant read); `joulewise/hazards/arm.py`: 268-270, 85 (`UNMEASURED_REFUSES = {"instrument"}`), 396-405.
- **Correction (fact).** Five conditions, not four. A dwell sample with no anchor does not refuse: it turns the
  whole dwell's clock verdict to unmeasured, disclosed, with rules ii and iv and the boot check unjudged. Rule iii
  can refuse only at the instant read. See also the second-tier note C5: the orchestrator may prefer the code to
  judge the series on the samples that did read.

#### A4. §4.6 item 2, "a prospective re-derivation trigger of the acceptance" [reg-05-arm-b-U1] CONFIRMED

- **Where.** int5 1431-1432; draft 1583-1584.
- **Text.** "If a prospective re-derivation trigger of the acceptance fires during the block, no further window
  arms; the question goes to a cold gate."
- **True.** The sentence stops arming, and the registration never says which events are triggers. §0.11, to which
  it points, defines the acceptance and never mentions triggers. The events are in the acceptance file itself, key
  `prospective_rederivation.triggers`, five entries: `corpus_doubles_from_24_to_48`; `identity_field_change`;
  `new_systematic_failure_challenges_preflight_screen`;
  `new_valid_same_identity_capture_expands_observed_range`; `protocol_or_estimator_byte_change`. The same key
  carries `trigger_observation_rule` = `judge_under_prior_artifact_never_self_fit` and `calendar_expiry` = null.
  The bracket evaluation records the triggers it observes
  (`acceptance.prospective_rederivation.observed_triggers`).
- **Evidence.** `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json` (read by the consolidator);
  `joulewise/calibration_bracketing.py:2484-2499, 2588-2602`. Not checked: whether any program stops an arm on an
  observed trigger; the sentence reads as a rule for the orchestrator.
- **Correction (fact).** Name the five events where the term is first used (or in §0.11), say that the bracket
  evaluation is what observes them, and say whether "no further window arms" is done by code or by the
  orchestrator.

#### A5. §4.7, which judged epochs the arm reads [reg-05-arm-b-M2] CONFIRMED

- **Where.** int5 1515-1517 and 1525; draft 1667-1669 and 1677.
- **Text.** "the (OS build, machine model) pairs the acceptance's captures were taken on, with any continuation the
  ledger authenticates"; "it moves that same refusal before the dwell, reading the same judged epochs."
- **True.** The arm loads the judged epochs without the calibration ledger: the acceptance's own pair plus every
  registered continuation that passes its registry-pin and file checks. The check of each continuation's session
  against the ledger is skipped. The pre-calibration writer passes its ledger snapshot, so it applies that check as
  well. The arm's set therefore equals the writer's set or contains it. The arm never refuses a pair the writer
  would accept, so "adds no new refusal outcome" stays true. A pair covered only by a continuation the ledger
  rejects passes the arm and is refused by the writer at the pre calibration slot, after the dwell.
- **Evidence.** `joulewise/b5/driver.py:595-599` (comment) and `:612` (`acceptance_judged_epochs(artifact, None)`);
  `joulewise/calibration_epoch_continuation.py:286-325` (`skipped_no_ledger_snapshot`);
  `scripts/validate_powermetrics_fiducial.py:447-455`.
- **Correction (fact).** For the arm: continuations are authenticated by registry pins and file checks only, with
  no ledger. The arm and the writer do not read the same set; the arm's is the same or larger.

#### A6. §5.1 and §10 item 5, the operator countdown [reg-11-M1, reg-06-shape-a-03] CONFIRMED twice

- **Where.** int5 1553-1556 (§5.1) and 3046-3047 (§10 item 5); draft 1705-1708 and 3198-3199.
- **Text.** "Each pack stage passes `--arm-countdown-s 20` ... the chain passes 0 on the ten collection stages and the
  pre slot, saving 11 × 20 = 220 s per window." (§5.1); "The chain passes `--arm-countdown-s 0` on every collection
  stage and on the pre calibration slot in place of the packs' literal 20; the post calibration slot keeps 20 s"
  (§10).
- **True.** In each of the three plan trees (16 stages each) only the ten collection stages (positions 3 and 5 to
  13) carry the literal `--arm-countdown-s 20`. The two calibration capture stages carry no countdown argument, and
  the capture tool's default countdown is 0.0 s. Bracket reservation, bound derivation, the whole-window verdict and
  the backup carry none. The chain replaces 20 with 0 on the ten collection stages. On the calibration captures it
  adds `--arm-countdown-s N --sleep-display-before-capture`, with N = 0 for the pre slot and N = 20 for the post
  slot, and it refuses a calibration template that already carries either argument. The calibration 20 s is the
  block-3 runbook's value for a calibration slot, not a pack literal. Against the runbook, the pre slot drops 20 s
  and the post slot keeps 20 s, and 11 × 20 = 220 s holds. Against pack bytes, the collection stages save
  10 × 20 = 200 s, the pre slot is unchanged at 0 s and the post slot gains 20 s.
- **Evidence.** The three `plan_tree.json` files (30 occurrences of the literal, all in collection stages);
  `joulewise/b5/chain.py:155-162, 248-252, 525-528`; `scripts/validate_powermetrics_fiducial.py:2031-2033`;
  `docs/phase_2/window_runbook.md:1544-1545`.
- **Correction (fact).** §5.1: each collection stage of a pack carries the literal 20, and the 220 s is measured
  against the runbook protocol. §10 item 5: the 0 on the pre slot replaces the runbook's 20, not a pack literal;
  both calibration countdown arguments are additions by the chain (A18 names the second added argument).

#### A7. §5.3 item 3, "Was the bound derived?" [reg-06-shape-a-02] CONFIRMED

- **Where.** int5 1660-1666; draft 1812-1818.
- **Text.** "If the core reader accepts the bound, yes. ... If both checks pass, the bound counts as derived from the
  collected subset. Otherwise `neg8.bound_not_derived` removes the window."
- **True.** On a hazard bound root (the bound's runs root carries the hazard launch-lineage locator, which is every
  block-5 window by the chain's design) a bound accepted by either route counts as derived only if a third check
  also passes. Every corpus member the bound names must be exactly one ordinary bundle, not a symbolic link, in
  the bound root; its file inventory must hash to the member's recorded `bundle_evidence_sha256`; its launch
  lineage must authenticate; its calibration identity must equal the bound's; it must pass the custody-strict and
  current strict-summary checks; its canonical scientific configuration must equal the corpus's; and its gross and
  idle-subtracted energy points must re-derive to the recorded values. Any problem, an empty member list, or an
  exception in the check sets the bound to not derived and emits `neg8.bound_not_derived`, which removes the
  window. `derived/neg8-bound.json` records `members_rederived`.
- **Evidence.** `joulewise/b5/harvest.py:4288-4315` (the third check, both routes), 728-810
  (`neg8_bound_member_problems`), 4327-4337; `tests/test_harvest_b5_window.py:4155-4242`. Neither document mentions
  the check. Not observed on a live bound root; it follows from the chain design.
- **Correction (fact).** Add the third check and its conditions to §5.3 item 3.
- **Twin.** The `flag_catalog.json` note of `neg8.bound_not_derived` (line 939) lists only the two routes and the
  corpus-physics drop; it needs the same addition.

#### A8. §5.3 item 3, the time at which the bound's freshness is judged [reg-06-shape-a-01] CONFIRMED

- **Where.** int5 1673-1674; draft 1825-1826. It contradicts the "bound's age" paragraph of the same section (int5
  1741-1747; draft 1893-1899), which is the passage that matches the code.
- **Text.** "and with the bound's freshness judged at the verdict's completion time".
- **True.** The harvest hands the evaluator the verdict's completion time (`evaluation_scope.completed_at`, else the
  row's time stamp). On a hazard runs root the evaluator replaces it with the end of the latest end reference's
  measured window whenever every end reference's window can be read. If only some can be read, it uses the later of
  the completion time and the latest readable end. If none can be read, the completion time stands.
- **Evidence.** `joulewise/b5/harvest.py:4904-4913, 4944`; `joulewise/whole_window.py:5040-5062`. The harvest's own
  docstring (4862-4863) carries the same stale wording.
- **Correction (fact).** The freshness time is the end of the last end reference's measured window, with the two
  fallbacks above; or point to the "bound's age" paragraph and delete the clause.

#### A9. §5.4, when the watchdog releases a finished window [reg-06-shape-a-05] CONFIRMED

- **Where.** int5 1787-1791; draft 1939-1943.
- **Text.** "when it sees on one tick: `chain.started` and `chain.exited`; the driver's terminal `result.json` with this
  plan's id and a finite end time no later than now; `courier.sent`; and an empty agent census and no driver
  process. The same release applies to a NULL window and to a CHAIN_STOPPED one."
- **True.** The release applies to the `HAZARD_PACK` receipt class only and accepts two shapes of the custody
  directory. Both need `courier.sent` and a `result.json` carrying this plan's id, this plan's receipt class and a
  finite end time no later than now. Shape (a), a collected or CHAIN_STOPPED window: `chain.started` and
  `chain.exited` both present and a known terminal verdict. Shape (b), a NULL window (a refusal before the chain was
  claimed): neither chain file present, verdict REFUSED, `chain_exit_code` null and `chain_sha256` null. A reader
  applying the listed conditions would never release a NULL window. The process half has three conditions on the
  same tick, not two: an empty agent census, no driver process, and no live process whose command line names the
  plan's custody root. An unreadable process table never releases.
- **Evidence.** `joulewise/arm_retry.py:255-306` (`terminal_window_release`); `scripts/magistrate_watchdog.py:1035-1053,
  2021-2041`.
- **Correction (fact).** State the two custody shapes, the receipt-class condition and the third process condition.

#### A10. §5.5, "plus the sizing margin" after a deadline stop [reg-07-shape-b-6] CONFIRMED

- **Where.** int5 1899-1902; draft 2051-2054. §10 (int5 3034) says this resizing rule needs no erratum.
- **Text.** "The next attempt's per-member allowance becomes the larger of the sizing output's and the stopped
  attempt's largest observed member cycle, plus the sizing margin, and `WINDOW_MAX_S` is re-derived by the rule
  above without an erratum".
- **True.** No "sizing margin" for a member exists anywhere: not in the registration, the analysis plan, the
  catalog, `sizing_b5.json` or `scripts/size_b5_window.py`. The quantities a reader could guess (77 s of per-member
  custody, the 600 s inside the collection-deadline reserve, the 3,300 s arm allowance) give three different
  answers. No code re-derives an allowance from an observed cycle: the sizer accepts only `--repo`, `--adapter`,
  `--pack`, `--out` and `--check`, and `--check` reproduces `sizing_b5.json` byte for byte, so a resized allowance
  would produce a sizing file that differs from the sealed one with no registered way to bind it.
- **Evidence.** Search for "margin" in the three documents, `sizing_b5.json` and `scripts/size_b5_window.py`
  (750-755 for the arguments, 562-563 for the only margin, the clock's frequency margin).
- **Correction (fact).** The fact does not exist yet. The orchestrator must supply the margin in seconds, what it is
  added to, and how the re-derived sizing file is produced and bound; or the phrase is deleted and the rule is
  stated as a desk procedure with its formula.

#### A11. §6.4, the span on which contention is judged [reg-08a-08] CONFIRMED

- **Where.** int5 2349-2351; draft 2501-2503.
- **Text.** "in a 10 s interval that overlaps the member's request (request start to request end).
  `contention.unmeasured`: part of the request is covered by no interval."
- **True.** When a member has a member span but no request span, the harvest judges both contention codes over the
  whole member span instead (the hull of the sampler stream and the controller's span from the start of the idle
  baseline to the end of the idle drift sentinel). The request span is absent when the `sampling_started` or
  `sampling_stopped` stamp is missing, and also when both exist but the start is later than the stop. Both codes
  remove the member, so in that case an outside process above the limit, or a gap in the 10 s intervals, anywhere
  in the member span removes a member the written rule would not reach.
- **Evidence.** `joulewise/b5/harvest.py:5886-5901` (`request or member_span`), 1926-1957 (`member_spans`), 2992.
  Not checked: whether such a member is always removed by another code anyway.
- **Correction (fact).** State the fallback span and when it applies.
- **Twin.** Both catalog notes (`contention.request_overlap`, `contention.unmeasured`) say "the member's request".

#### A12. §6.5 and §7.4, what `clock.systematic` counts [reg-08a-01, reg-10-M4] CONFIRMED twice

- **Where.** int5 2439-2440 (§6.5) and 2849-2852 (§7.4); draft 2591-2592 and 3001-3004.
- **Text.** "`clock.systematic`: at least 5 members of the window have a recorded anchor status and more than half of
  them are not `bounded`." (§6.5); "if at least 5 members have a recorded anchor status and more than half of them
  are not `bounded`" (§7.4).
- **True.** The harvest counts the recorded anchor statuses of the window's members and of its finalized
  calibration captures (the pre and post slots, at most two). The flag is raised when at least 5 of those members
  and captures together have a recorded status and more than half of the recorded ones are not `bounded`. So three
  members and two captures reach the minimum, and a capture that is not bounded counts toward the majority. A
  capture whose evidence file is unreadable or carries no status is "not recorded" and is left out of both counts;
  a capture with an unrecognised status string counts as recorded and not bounded. §0.3 defines a member as one run
  of one inference request, so a calibration capture is not a member in the document's own terms.
- **Evidence.** `joulewise/b5/harvest.py:5461-5470` (`clock_systematic`), 4146-4194 (the capture's anchor status);
  threshold `clock_systematic_min_recorded` = 5.
- **Correction (fact).** Members and finalized calibration captures are counted together.
- **Twins.** `flag_catalog.json` line 330 (note of `clock.systematic`: "At least 5 members with a recorded anchor
  status and more than half not bounded"). For §7.4's count across attempts see C8: no block-5 code computes it.

#### A13. §6.5, a window-removing code missing from the list [CAT-5] CONFIRMED

- **Where.** int5 2441; draft 2593.
- **Text.** "- `cell.below_minimum` (§6.6) and `roster.no_science_bundles`." (in the list headed "The window is not
  claim-usable when any of these fired").
- **True.** The catalog also gives `roster.duplicate_run_id` the effect EXCLUDE_WINDOW, and the harvest emits it at
  window level when the plan tree launches or lists one run id more than once. It is the only one of the catalog's
  32 window-removing codes that section 6 neither names nor covers by a wildcard. Its only mention in the
  registration is historical (int5 1086; draft 1153).
- **Evidence.** `flag_catalog.json` line 1179; `joulewise/b5/harvest.py:3797`; scripted comparison of the 32 codes
  against section 6, repeated by the refuter.
- **Correction (fact).** `roster.duplicate_run_id` removes the window and belongs in the §6.5 list.

#### A14. §6.5, what `neg8_bracket_reference_invalid` means [reg-09-M3] CONFIRMED

- **Where.** int5 2459-2460; draft 2611-2612.
- **Text.** "`neg8_bracket_reference_invalid` now means fewer than two survivors at an endpoint or more references
  than planned (§0.12)."
- **True.** The condition has more causes, and each one removes the window through `neg8.screen_failed`. In the
  evaluator: (a) the survivors match no protocol shape, which covers fewer than two at an endpoint, more than three
  at an endpoint or more than one at the midpoint, and a one-and-one pair with a recorded loss; (b) a required
  start, end or present midpoint reference whose gross energy is not a finite, positive point with
  lower ≤ point ≤ upper, or whose idle-subtracted energy is not finite. In the verdict writer: (c) a reference
  whose declared NEG-8 role or position is invalid; (d) surviving references whose scientific-configuration
  identities are missing or not all the same. A fifth branch, gross and idle-subtracted reference counts that
  differ, exists in the evaluator but neither caller can produce it.
- **Evidence.** `joulewise/whole_window.py:2251-2293, 1846-1890`; `scripts/run_campaign.py:7170-7171, 7201-7209,
  7272-7281, 7330-7331`.
- **Correction (fact).** List causes (a) to (d); "fewer than two survivors or more than planned" is cause (a) only.

#### A15. §6.7, the four conditions under which a bundle is ignored [CAT-4] CONFIRMED

- **Where.** int5 2494-2496; draft 2646-2648.
- **Text.** "A bundle that is not in the plan's roster (`roster.not_in_plan`), not bound to this attempt
  (`roster.foreign_attempt`), or created before `chain.started` (`roster.before_chain_started`) is ignored, not
  used; a roster member left without an admissible bundle is `member.bytes_missing`."
- **True.** There is a fourth condition, tested third. When `chain.started` carries a monotonic stamp and the
  bundle has no stamp that places it against that moment (no member-span, controller or run-start stamp), the
  bundle is ignored under the label `roster.creation_unplaced`, and its member becomes `member.bytes_missing` if no
  other bundle is admitted. The catalog classes `roster.creation_unplaced` as EXCLUDE_MEMBER, and neither the
  registration nor the analysis plan names it.
- **Evidence.** `joulewise/flags/exclusions.py:271-290`; `joulewise/b5/harvest.py:6927-6937, 1994`;
  `flag_catalog.json` line 1165; `configs/gates/hazard_refusals.json:268`.
- **Correction (fact).** Four conditions, in the order: not in the roster, another attempt, cannot be placed,
  created early. B33 gives what these four codes do as catalog effects.

#### A16. §6.10 controller table, the auxiliary-configuration row [reg-09-M2] CONFIRMED

- **Where.** int5 2591; draft 2743.
- **Text.** "| the auxiliary-config comparison raised an exception | `records.auxiliary_match_raised` (DISCLOSE), with
  the exception text | the pack-identity check at harvest |" in a table headed "What used to refuse the member |
  Recorded now".
- **True.** The refusal stays. An exception in the comparison still refuses the member's calibration attachment
  with "revision_five evidence cannot be attached as instrument calibration (auxiliary member match raised
  <error>)", when the evidence is revision five or carries the battery-float record and no pre-slot or pre-bracket
  provenance was authenticated. The only change is that the exception, formerly swallowed, is now recorded as the
  flag and named in the refusal message. The catalog note already says so ("The refusal it causes stands").
- **Evidence.** `joulewise/controller.py:944-956` ("The refusal that follows stays; its cause is now on record"),
  693-714; `tests/test_p2_ctl_auxiliary.py`. Not checked: whether a "pack-identity check at harvest" does what the
  third column says.
- **Correction (fact).** The row must say the member is still refused and the flag records why, as its sibling rows
  do with "still refuses".

#### A17. §7.2, when an arm's `pack.identity_unmeasured` is superseded [reg-10-M5] CONFIRMED

- **Where.** int5 2810-2815; draft 2962-2967.
- **Text.** "the harvest itself re-derived every check that collector performs (pack: the pins, the config run ids and
  the registered digests; checkout: ...; executed code: ...)".
- **True.** For the pack collector the three named checks are right but not sufficient. The harvest must also have
  run the checkout's tracked-edits check and its untracked-files check (both possible only when the listing of the
  working tree saved at the arm is present), and every collection stage's member dispatch must have resolved.
  Otherwise the arm's `pack.identity_unmeasured` stays and removes the window. The case that changes an outcome is
  an unresolved dispatch: `roster.dispatch_unresolved` alone is only disclosed, so the text predicts the window is
  kept and the code removes it. When the saved listing is missing, the harvest's own `code.identity_unmeasured`
  normally removes the window anyway. The checkout and executed-code clauses carry no extra condition.
- **Evidence.** `joulewise/b5/harvest.py:521-528` (`IDENTITY_SUPERSESSION_CHECKS`), 6397-6403, 3780, 5640-5642;
  `flag_catalog.json` lines 983-989 and 1172-1177.
- **Correction (fact).** Add the two further conditions for the pack collector.

#### A18. §10, a deviation from pack bytes that is not listed [reg-11-M2] CONFIRMED

- **Where.** int5 3038-3052; draft 3190-3204.
- **Text.** Five numbered deviations, then "The chain's other changes of round 2 ... are not deviations from pack
  bytes".
- **True.** The chain appends two arguments to both calibration capture stages that no pack carries:
  `--arm-countdown-s N` (A6) and `--sleep-display-before-capture`. The second makes the capture tool run
  `pmset displaysleepnow` after the countdown and then wait 5 s. If that command fails, the capture continues and
  the failure is recorded under `calibration.writer_record_flagged` with kind `display_sleep_action_failed`. The
  registration names that kind once (int5 2645; draft 2797) and never says the chain adds the argument that causes
  the call; the string "sleep-display" occurs nowhere in either copy. The chain's own list of deviations carries it
  as entry 2.
- **Evidence.** `joulewise/b5/chain.py:159-162, 248-250, 525-528`; `scripts/validate_powermetrics_fiducial.py:2036-2040,
  2531-2559`; the calibration stages of all plan trees.
- **Correction (fact).** A sixth registered deviation: both calibration captures gain the display-sleep argument
  and what it does.

### Analysis plan

#### A19. Plan §7.1 step 3, §7.2 and §8.1: the metrology term of the GAMMA contrasts [PB-1] CONFIRMED

- **Where.** Plan 389-393 (§7.1 step 3) and 438-442 (§7.2 worked example), same lines in both copies; §8.1
  battery-assist example int5 504-507, draft 517-520; §8.1 "Conservative contrast interval" int5 529, draft 542.
- **Text.** "Metrology term: each member records governed random-error variances. ... Disclosed conservatism: each
  member's random error is already part of s_d, so adding se_met counts it twice; the interval's coverage is above
  95%." The examples use a quad variance of 0.0100 J², se_met 0.033333, se_total 0.072648, interval
  [2.8325, 3.1675], t = 41.3; and for eight quads se_met 0.035355, se_total 0.069276, [2.7987, 3.1263].
- **True.** Both block-5 contrasts use the metrics `phase_energy_j.decode` and `phase_energy_j.prefill`. The engine
  reads a random-error variance only for the metric `energy_request_j`. For the two phase metrics the set of terms
  is empty, se_met is 0 and se_total equals se_rep. There is no double count and no extra coverage from one. The
  only departure from an exact t interval is the three-place rounding of t*. On the §7.2 data (n = 9) the engine
  gives se_total 0.064550, t* 2.306, interval [2.8511, 3.1489] J, decision interval with D = 0.05 J
  [2.8011, 3.1989] J, t = 46.5. The outcome of the example (direction supported, ceiling L2) does not change. For
  the eight-quad example, by hand from the text's own mean and se_rep (not run on the engine): se_total 0.059574,
  t* 2.365, interval about [2.8216, 3.1034] J.
- **Evidence.** `joulewise/analysis_engine/inputs.py:3852-3860` (`if name != "energy_request_j": return (), ()`);
  `ratio.py:307-323`; `__init__.py:524-528, 590-634`; `estimators.py:386-405, 474-475`;
  `joulewise/analysis_manifest_v3.py:3933-3939`; GAMMA's `analysis_manifest_v3.json`. The refuter ran
  `estimate_paired_blocks` on the nine differences.
- **Correction (fact).** For these two contrasts se_met = 0 and se_total = se_rep; the worked numbers become the
  ones above; the §8.1 disclosure names only the rounded t*.
- **For the orchestrator.** This correction narrows the registered interval and removes a registered conservatism.
  If the design wants the metrology term for the phase metrics, the engine must be changed instead, and that is a
  change to claim code. It is listed again as C4.

## List C. Code disagrees with the registered design (the orchestrator decides)

In these entries the text states a rule that was decided, and the code at `9b0c680ed` does something else. The
writer should leave the text alone until the orchestrator rules. Each entry gives the code change that keeps the
text, and the fact to write if the code stays. Any code change here touches an executed file after the frozen head.

### Decide before the seal

#### C1. §5.7: one lost GAMMA diagnostic reference makes the window's yield LOW [reg-07-shape-b-1] CONFIRMED

- **Where.** int5 1947-1955 (the min_valid list) and 1845-1846; draft 2099-2107 and 1997-1998.
- **Registered.** min_valid is 10 for the NEG-8 corpus, 2 of 3 for the start and end triplets, 0 of 1 for the
  midpoint, and ⌈planned × 8 / 10⌉ for science stages; "these trip by chance with probability 1.6 × 10⁻⁴ and
  2.1 × 10⁻³, so a trip means a systematic cause". §5.5 calls each GAMMA diagnostic stage "one auxiliary member of
  the reference class".
- **Code.** `driver._stage_role` classes every stage whose roles are not NEG-8 roles as "science". GAMMA's two
  diagnostic interior-reference stages (`gamma-reference-decode-midpoint` and `gamma-reference-prefill-midpoint`,
  positions 7 and 11, one member each, role `window_interior_reference_diagnostic`) therefore get
  min_valid = ⌈1 × 4/5⌉ = 1 of 1. One lost diagnostic member makes its stage ZERO (no bundle) or LOW (a bundle that
  did not succeed), writes a yield alert, sets the window's yield status to LOW and adds `yield_low` to the fault
  reasons. At the text's own loss rate of 1 in 37 this happens by chance in 1 − (36/37)² = 5.3% of GAMMA windows.
- **Why it matters.** LOW sends a fault email to Ed (§5.7), and the §7.3 process rule tells the orchestrator not to
  arm the next window on unchanged code after a LOW whose lost members share one cause; a single lost member always
  shares one cause with itself. The diagnostic member enters no claim.
- **Evidence.** `joulewise/b5/driver.py:1376-1399, 1495-1506, 1765, 2626-2627` (the role function re-read by the
  consolidator); both `order_manifest.json` files under `configs/campaigns/gamma_interior_references_v5/`, line 16.
  The refuter ran `_stage_role` and `_min_valid` (result: `science`, 1). The path from the fault reasons to the
  email was not traced.
- **If the text stays (code change).** Give the diagnostic role its own minimum, 0 of 1 as the midpoint has.
- **If the code stays (fact for the text).** A fourth case in the min_valid list: GAMMA's two one-member diagnostic
  stages count as science stages with min_valid 1 of 1; one lost diagnostic member gives LOW; the chance rate is
  5.3% of GAMMA windows; for these two stages a trip does not mean a systematic cause.
- **Consolidator's reading.** The text states the intent. The code's result looks like a fall-through of the role
  function for a role it does not name, not a decision.

#### C2. §8 item 2: a RESTRICTED code is written by name into files that may leave custody [reg-10-M6] CONFIRMED

- **Where.** int5 2891-2892; draft 3043-3044. Analysis plan 468-469 (both copies) says the same for a unit.
- **Registered.** "A member removed by a RESTRICTED code is released as "removed (restricted code)", without the
  code."
- **Code.** No program writes that form; the phrase occurs only in the two documents (search repeated by the
  consolidator). No code path filters or redacts on a flag's `blinding` value. The harvest writes every flag
  record, whatever its blinding, to `derived/flags.jsonl`; `derived/exclusions.json` lists each excluded member's
  run id with its full list of codes; `derived/window_flags.json` counts flags by code. The harvest's docstring
  says the `derived/` files "may leave custody", and §6.1 lists them as the harvest's outputs. The catalog's one
  RESTRICTED code, `member.anchor_energy_envelope_exceeded`, would stand by name beside its run id. Two more codes
  are written with a per-flag RESTRICTED mark into the same files (B25).
- **Evidence.** `joulewise/b5/harvest.py:22-26, 1226, 3950-3956, 6902, 7305-7338`;
  `joulewise/flags/exclusions.py:370-384`. Read from the code; the harvest was not run. Not checked: whether any
  program sends `derived/` files off the machine.
- **If the text stays (code change).** The harvest keeps RESTRICTED flag records out of `derived/` (under
  `withheld/`), and redacts the code lists and the per-code counts.
- **If the code stays (fact for the text).** The redaction is a manual step at release. Until the release event,
  `derived/flags.jsonl`, `derived/exclusions.json` and the per-code counts of `derived/window_flags.json` are
  restricted, and `FILL[B5-BLIND-CUSTODY-MAP]` must list them.
- **Consolidator's reading.** Blinding is one of the protections the doctrine keeps, so this needs a ruling and not
  a silent wording change.

#### C3. §5.1, §6.2 and §6.5: `instrument.precal_screen_failed` is registered and never emitted [CAT-1] CONFIRMED

- **Where.** int5 1545 (§5.1), 2145 (INSTRUMENT row of §6.2) and 2438 (§6.5 list); draft 1697, 2297 and 2590.
  `flag_catalog.json` line 528; `configs/gates/hazard_refusals.json:215`.
- **Registered.** "a pre fiducial bound above the pre screen 0.036462861644980 s (`instrument.precal_screen_failed`,
  exit 12)"; the catalog classes the code INSTRUMENT, EXCLUDE_WINDOW; §6.5 lists it among the codes that remove the
  window.
- **Code.** The literal exists only in `joulewise/flags/catalog.py:82` (search repeated by the consolidator) and is
  absent from `harvest.CODES`. A pre fiducial bound above the pre screen stops the chain with stop reason
  `pre_calibration_screen_failed` and exit 12, which is a journal reason and not a flag. The harvest of that
  window emits `calibration.no_bracket` (family CALIBRATION, removes the window) because the bracket session is not
  finalized, and `chain.stopped_before_collection` (disclosed). The window is removed either way, but under
  CALIBRATION and not INSTRUMENT. §6.5's description of `calibration.no_bracket` (int5 2382-2383; draft 2534-2535)
  names only `disk.low`, the census and the deadline as its chain-stop causes and omits the stops at exits 10, 11
  and 12.
- **Evidence.** `joulewise/b5/chain.py:117, 122, 1160`; `joulewise/b5/harvest.py:188, 3947, 4130, 7132`. Read from
  the two emit sites; no failed-screen window was run end to end.
- **If the text stays (code change).** The harvest emits `instrument.precal_screen_failed` when the stage journal
  carries the stop reason `pre_calibration_screen_failed`.
- **If the code stays (fact for the text).** No flag of that name is written. The exclusion is
  `calibration.no_bracket`, whose causes include the chain stops at exits 10, 11 and 12. The catalog entry is a
  reserved code with no emitter and its note should say so.

### Second tier: a text correction is enough, but the orchestrator may prefer the code to change

Each of these is described in full under the entry named. They are listed here so that the choice is made once.

- **C4 (see A19).** The analysis engine adds no metrology term for the two phase metrics; the plan registers one
  and calls it a conservatism. Correcting the text narrows the registered interval.
- **C5 (see A3, part 2).** One dwell sample with no anchor leaves the residual, frequency and boot-session rules
  unjudged for the whole dwell. The code could judge the series on the samples that did read.
- **C6 (see B12).** §3 registers a "deliberately incomplete finalization" among ALPHA-1's structural diagnostics;
  the block-5 harvest does not run it. The step exists only in the block-4 harvest script.
- **C7 (see B31, B32).** Eight catalog codes have no emitter: `records.receipt`, `records.attempt_history`,
  `records.provenance_digest`, `records.naming`, `records.notice`, `clock.sntp_offset`, `monitor.probe_in_phase`,
  `battery.accumulator_diagnostic`. With C3 that is nine. They can stay as reserved codes with a note, or leave the
  catalog.
- **C8 (see A12).** §7.4 counts recorded anchor statuses across every started attempt of the block to reach END
  STATE. The refuter found only the per-window rule in block-5 code. The readers also found no scheduler code
  behind §7.2 and §7.6 ("the scheduler reads only `claim_usable`", the fixed order ALPHA, BETA, GAMMA): 
  `joulewise.flags.exclusions.first_claim_usable` has no caller outside tests. If these are rules for the
  orchestrator, the text should say so, as §7.3 does with "not code".
- **C9 (see B38).** A chain that started and was killed before its first stage journaled gets the verdict COLLECTED,
  not NO_COLLECTION.
- **C10 (see B36).** The allowlist test admits a new refusal classed DEFERRED_REPRESENTATION with an owner; §6.11
  says only PHYSICS, NUMBER_INTEGRITY or INTERNAL can enter. The test could be tightened instead.
- **C11 (see B33).** The catalog gives four roster codes the effect EXCLUDE_MEMBER; only one of them ever removes a
  member under its own name.
- **C12 (see B27).** After a charging-current read above 200 mA the member is removed, and the assist energy is
  still computed and written to the withheld record, although §6.4 says no assist would be computed.

## List B. Confirmed record-only mismatches

No number, exclusion or collection behaviour depends on these. Once sealed, each would still be a sentence that
misdescribes the code. Ordered by document and section. Format: where; the text; the true fact, which is also the
correction; the evidence.

### Registration

**B0. Header and §2: the commits after `fe28e5a0c` (already repaired in draft revision 10) [H-1, reg03-M1].**
int5 22-25, 216-218, 225, 914-917, 931-932, 1050-1051, 1058-1060, also 2941 and 2965. Text: "One commit is still
to be merged after `fe28e5a0c`"; "The interpreter-rule commit changes only the census matcher". True: five commits
follow `fe28e5a0c`, all merged: `2524637ae` (the census rule and its test), `455e59b86` (a docstring-only edit to
`joulewise/b5/harvest.py`, an executed file, whose SHA-256 changes from `d59a916d…3e7582` to `e662333f…05e82b`),
`84661ddb3` (the merge), `763b678a7` (the four seal documents placed in the code tree) and `9b0c680ed` (a test
fixture). The cooldown search repeated at `9b0c680ed` is clean. Draft status: revision 10 says all of this (draft
22-28, 250-284, 960-986, 1114-1116 and the `B5-REV10-SYNC` rows at 3441-3448). Left for the final pass: the final
head adds more commits, and the draft already says the sync is repeated on that difference.

**B1. Revision 6 list, item 3 [H-3].** int5 132-133; draft 136-137. Text: "a clock sample whose three reads took more
than 250 µs is re-read up to five times and is otherwise unmeasured, never a step". True: five reads in all
(`ANCHOR_TRIES = 5`), one first read and at most four re-reads; §4.2 (int5 1218-1219) says it correctly. Evidence:
`joulewise/hazards/clock.py:91, 152-170`.

**B2. §0.3, the spans of 576 and 750 idle records [reg-01-M3].** int5 288-292; draft 331-335. Text: "576 records,
which over those 37 captures would have spanned 75.0–75.9 s (median 75.2 s) ... 750 records spanning 97.7–98.9 s."
True: over the 37 captures the first 576 records span 75.0–76.1 s (exact 75.010–76.082 s, median 75.173 s) and the
750 records span 97.7–99.1 s (exact 97.667–99.055 s). The text's own period range, 130.2–132.1 ms, gives the same
upper ends. The longest capture in both ranges is `g2a-small-p0512-r02` of harvest `20261003T1748Z-r2`. Correct as
written: the period range, 575 records short of 75 s on 11 of 37, 576 short on none. Evidence: the refuter summed
`elapsed_ns` in the 37 block-3 `rich_telemetry_idle.jsonl` files (timing fields only).

**B3. §0.5, the decode prompt hash [reg-01-M2].** int5 324; draft 367. Text: "a 42-token prompt (decode prompt
manifest SHA-256 `31301c9d…6694`)". True: that value is the canonical suite-manifest hash
(`joulewise.suite.suite_manifest_sha256`, stored in member configs as `suite_manifest_sha256`) of the Qwen3-1.7B
floor pack's decode manifest only. It is not a SHA-256 of file bytes and the 8B pack does not share it. The 8B
pack's canonical hash is `6dc7448c3e14ee18383f7904830f96dbc624e37875d3abac2561321669668705`. File bytes: 1.7B
`446c7ef368d34a558d4fd264b0b86c99314b1dc22ec7ac3447d6d0fea93501d7`, 8B
`46887b91cda436c1da90a217b1950d051371b215a0d5bd4ed00636196057206e`. Two further canonical hashes appear in the
contrast pack's member configs, 21 each: `d60a7f4d2e3498947fef630fd3092da59ffb13b52e604894ada065e4e9647b23` and
`c35156575b7c14c9f2271b442f71c9fafa3944363c2f46ae2821731134229185` (the reader assigns them to 1.7B and 8B; the
refuter did not confirm which is which). 42 tokens is right for both models. Evidence: `shasum`, the hash function
and the member configs (54, 54, 21 and 21 occurrences).

**B4. §0.6, the dwell before the first settle [reg-04-arm-a-04].** int5 347-349; draft 390-392. Text: "the
pre-calibration settle starts after a clean dwell of 633–1,477 s at the arm". True: 633–1,477 s is the range under
revision 4's 600 s rule, as §4.2 itself says (int5 1298; draft 1365). The registered `clean_s` is 180, so the settle
starts after a clean dwell of at least 180 s (six consecutive clean 30 s intervals), longer whenever an interval is
not clean, with refusal at the 2,700 s cap. Evidence: `joulewise/hazards/contention.py:104`; the §4.3 block.

**B5. §0.6, the cost of one cooldown reading [reg-01-M4].** int5 350-361; draft 393-404. Text: "(50 records
requested, about 6.5 s of wall time)"; "the next member starts, about 13 s after the cooldown began". True: the 50
records span about 6.5 s of sampled time. A reading costs about 7.5 s of wall time (block 3: 7.46–7.69 s between
readings, median 7.55 s) and the first completes about 8.5 s after the cooldown begins (8.49–8.66 s). A release at
the second reading comes at about 16 s (block-3 trace: 16.18 s), not 13 s. The same paragraph's 8.6 s and 9.1 s are
first-reading releases and agree with this. Evidence: 26 block-3 cooldown traces; `scripts/run_campaign.py:5027-5060`;
the timing judge's record (`max_s` 16.2).

**B6. §0.6, "the 28 block-3 small members that had a cooldown" [reg-01-M5].** int5 362-369; draft 405-412. True:
block 3 has 26 cooldowns, all before small members, so 26 small members had a cooldown (largest gap among them
231 s). The 28 is the timing judge's regression sample. It spans gaps of 79–702 s, so it includes first-in-stage
members that had no cooldown. It cannot be reproduced from `member_timing.csv` (31 small members have a recorded
gap, 30 of them completed). The slope, r, residual SD and gap range match the judge's record. Correction: the 28
are small members with a recorded gap since the previous run's end, not members that had a cooldown. Evidence:
`/Users/edr/night-archive/gate-prune/timing/member_timing.csv`, `timing_analysis.json`, `judge/judge_checks.json`.

**B7. §0.6, the battery-temperature readings [reg-01-M1].** int5 372-384; draft 415-427. Text: "At each cooldown
release the runner reads the battery thermistor ... A one-member stage has no cooldown and no reading." True: the
runner takes one reading before every member, the first member of a stage included (its cooldown result is
`first_run_exempt`, meaning no wait was applied). A stage of N members has N readings and a one-member stage has
one. The rise is the last reading minus the first, where the first is taken before the stage's first member; the
plateau test uses the last three. A stage with fewer than two readable readings gets no rise judgment. A one-member
stage whose single reading is unreadable still raises `thermal.battery_temperature_unmeasured`. Evidence:
`scripts/run_campaign.py:10987-10996, 11095-11103, 4553-4568`; `joulewise/b5/harvest.py:7265-7281`;
`tests/test_run_campaign_p2_rc.py:521-547`. Twins: analysis plan int5 553, draft 567, and `flag_catalog.json` lines
1254 and 1275 say "at each cooldown release" without the false "no reading" sentence.

**B8. §0.12, where the verdict writer runs [reg-02b-M1].** int5 566; draft 609. Text: "The verdict writer runs inside
the window". True: the verdict writer (`scripts/run_campaign.py --whole-window-verdict`) is a desk step. The harvest
runs it after the chain exits and after the pin advance, over the completed runs root. The registration says so
elsewhere (int5 558, 841-842, 1607-1608). The rest of the sentence matches the code. Evidence:
`joulewise/b5/chain.py:147, 278`; `joulewise/b5/harvest.py:5143-5160`.

**B9. §0.12, the citation for `bundle_absent` [reg-02b-M2].** int5 618-622; draft 664-668. Text: "with reason
`bundle_absent` (`whole_window.evaluate_neg8_point_drift`, `run_campaign._idle_admission_core_evaluation`)". True:
those two functions implement only the `references_insufficient` naming for a short planned roster. The
`bundle_absent` rows are added by the harvest, in `harvest._neg8_lost_rows`, from the `neg8_slot` that
`harvest.build_roster` sets. The §13 row (int5 3221) cites it correctly. Evidence: `joulewise/b5/harvest.py:1648,
4814`; `joulewise/whole_window.py:2424-2425`; `scripts/run_campaign.py:7234-7239`.

**B10. §2 item 6, the dry arm's time [reg03-M5].** int5 991; draft 1045. Text: "2026-10-07 20:16:51 UTC". True:
20:16:52 UTC. The hashed record `dry-arm.json` (SHA-256 `0b9b2ad7…`) has `started.wall_s` 1791404212.513914, which
is 20:16:52.51, and the 0.177 s command began at about 20:16:52.34. The `:51` comes from the prose summary
`DRY_RECORDS.md` line 25, which has the same one-second error.

**B11. §2, what lane L10 touched [reg03-M2].** int5 1093-1094; draft 1160-1161. Text: "the change touches only the
retired block-4 writer (...) and tests". True: commit `c6309e1a` also changes the shared pack generator
`configs/campaigns/d117_contrast_v5/generate_configs.py` (173 lines) and the pin registry `configs/pins/registry.json`
(four new reference-file entries and renumbering), besides `sizing_b5.json` and `identity_pins.json`, which the next
sentence names. Evidence: `git show --stat c6309e1a` (21 files) and `7bfd7c2c`.

**B12. §3, ALPHA-1's structural diagnostics [reg03-M3].** int5 1164-1166; draft 1231-1233. Text: "strict validation,
re-reduction and a deliberately incomplete finalization; the p42 precheck counts; the longest and shortest stream
sizes; stage timing outside members". True: the block-5 harvest emits four `diagnostic.s1_structural` checks: the
bundle count with how many passed strict validation and how many re-reduced to an identical summary; the per-cell
precheck counts (RESTRICTED); the shortest and longest stream sizes; the gaps between member spans. No finalization
step, complete or incomplete, is run or recorded. Evidence: `joulewise/b5/harvest.py:6872-6909`; the refusing
finalizer exists only in `scripts/harvest_v5_g2b_window.py`. Correction: drop the clause, or see C6.

**B13. §4.1 step 4, the record-only collectors [reg-04-arm-a-02].** int5 1178-1179; draft 1245-1246. Text: "the
executed-file inventory, the model-identity check, and the checkout identity, each in a subprocess with a timeout".
True: one command (`scripts/collect_window_flags.py --stage arm`, killed as a whole after 120 s) runs five
collectors, each in its own subprocess with its own budget: pack identity (15 s), checkout identity (10 s),
executed-file inventory (15 s), model identity (55 s) and calibration-ledger readiness (15 s). The first four always
run; the fifth runs when the pack holds `calibration_plan.json` (not checked for the block-5 packs). Evidence:
`joulewise/b5/driver.py:704-730, 1927-1938`; `scripts/collect_window_flags.py:35, 106-110`;
`joulewise/flags/collect.py:93-99`.

**B14. §4.1 and §5.5, "4–47 min" [reg-04-arm-a-03].** int5 1185-1186, 1895, 1906; draft 1252-1253, 2047, 2058. True:
the sentence's own parts give 41 + 180 = 221 s = 3.7 min and 41 + 2,700 = 2,741 s = 45.7 min, so 4–46 min. Three
rehearsal arms took 40.3, 59.4 and 43.8 s before the dwell and under 0.1 s after it; the worst is 46.0 min. The 47
is carried over from revision 4 (a code comment at `joulewise/hazards/arm.py:308-309` repeats it). Correction:
4–46 min in all three places, or a stated larger allowance before the dwell.

**B15. §4.2, "Why a quarter" [reg-04-arm-a-06].** int5 1224-1226; draft 1291-1293. Text: "a skew of s can misplace
one sample's residual by at most s; two consecutive samples misplaced in opposite directions by 250 µs each differ
by 500 µs, still half the 1 ms that defines a step". True: the anchor is CLOCK_REALTIME minus the midpoint of the
two CLOCK_MONOTONIC_RAW reads taken around it, so a read with skew s is wrong by at most s/2. At the 250 µs bound
each sample is off by at most 125 µs, two consecutive samples differ by at most 250 µs, a quarter of the step, and
a residual above 1 ms still holds at least 750 µs of real clock movement. The registration never says the anchor
uses the midpoint. Evidence: `joulewise/clock_reference.py:115-121`; `joulewise/hazards/clock.py:36-46, 147-149`.

**B16. §4.2 against §9.2, the −865 mA reading [reg-10-M2].** int5 1254-1255; draft 1321-1322. Text: "A probe earlier
that day saw −865 mA bursts during Qwen3-8B decode while every registry value read 0." True: §9.2 item 3 (int5
3007; draft 3159) is the correct one. The −865 mA burst lasted about 1 s, just after the switch to Qwen3-8B (model
load), about 19 s before the first logged 8B request and outside every request. During the three 8B decode
intervals the lowest readings were −216, −56 and −84 mA. Evidence: the ruling
`RULING_battery_assist_2026-10-06.md` line 28; the refuter joined the probe's `smc.jsonl` to `mlx.jsonl` (a probe
run, not a claim window). "Every registry value read 0" was not rechecked.

**B17. §4.5, what the arm records only [reg-05-arm-b-M3].** int5 1424-1425; draft 1576-1577. Text: "Load average,
process-name lists and the `corecaptured` spawn count, which revision 2 judged, are recorded only." True: the
`corecaptured` spawn count is not read at all in a block-5 window; its only readers serve the legacy gate's
`quiet_predicate_evidence` night kind. The load average is recorded and not judged, but per member and not by the
arm or the census: the 1, 5 and 15 minute values in each member's `per_run_environment_evaluation`, and
`sysctl vm.loadavg` in the member's idle admission. Process names are recorded by the contention dwell. §13 row 5
(int5 3356; draft 3564) is accurate as written. Evidence: `joulewise/night_gate.py:2023-2044`;
`joulewise/night_kinds.py:64, 87`; `joulewise/environment.py:137-142, 391-393`; `joulewise/quiet_admission.py:259-281`.
Read from the call chain, not from a bundle.

**B18. §4.6 item 3, what the earlier pin changes moved [reg-05-arm-b-M1].** int5 1478-1480; draft 1630-1632. Text:
"Each change moved only the packs' plan-tree and config-inventory digests". True: the change from `039d3e3c` to
`9c2ecd89` (timing lane `f4cf9047`) moved the three plan-tree digests and, for all eight science units, both the
config-inventory digest and the configuration-set digest (`config_set_sha256`, the third pinned digest this same
item defines). The L10 change moved only GAMMA's plan-tree digest. No model or runtime pin moved. Evidence:
`git diff` of `identity_pins.json` across those commits.

**B19. §5.4, the order of the stamp and the proof [reg-06-shape-a-04].** int5 1762-1764; draft 1914-1916. Text: "the
chain exits and the driver stamps that moment; the driver proves the chain's process group gone". True: the chain's
direct child exits; inside the same supervision call a no-signal census of the process group runs and, if anything
survives, the termination proof; only after that call returns does the driver take its stamp. The stamp is
therefore no earlier than the exit and follows the proof. The yield count comes next. The 5 s monitor hold is
counted from the stamp, so "at least 5 s after the chain exited" stays true. Evidence:
`joulewise/b5/driver.py:2515-2543, 2691-2713`; `scripts/run_night.py:1321-1370`.

**B20. §5.5, three statistics from two populations [reg-07-shape-b-2].** int5 1865-1867, 1877-1878, 1884-1885; draft
2017-2019, 2029-2030, 2036-2037. Text: "a median of 236.5 s and a maximum of 274.9 s"; "Block 3's mean
start-to-start cycle was 257.1 s (PLAN2 §1.1)". True: one sample cannot have these three values (its mean could not
exceed about 255.7 s). 236.5 s and 274.9 s are the 16 cooled within-stage cycles of the single window `b3w1`, whose
mean is 242.9 s. 257.1 s is PLAN2's mean over 36 members of two windows (`b3w1` and `w2`), for which PLAN2 gives a
median of 234.5 s; the 26 cooled cycles of those two windows reach 406.6 s. PLAN2's 257.1 was not re-derived.
Correction: name the member set of each figure. Planning only. Evidence: the scratch `sizing_v2.json` (SHA-256
`6a82745f…`), `PLAN2.md` lines 63 and 76, `member_timing.csv`.

**B21. §5.7, when a stage is counted [reg-07-shape-b-4].** int5 1958-1962; draft 2110-2114. Text: "After each stage's
journal line, at the start of the next settle ..., the driver checks each planned bundle directory". True: a
collection stage is counted in the window only when the next in-chain stage is a collection stage or the bound
derivation, and its journal line is between 2 s in the future and 30 s old when read. Any other stage is counted
once at the terminal record, after the chain's process group is gone: the last collection stage, which runs
straight into the post calibration, and any stage whose line is stale or has no numeric end time. Its yield line,
flag and alert file are written only then, so the watchdog can pick that alert up only after the chain has ended.
Evidence: `joulewise/b5/driver.py:150, 1439-1446, 1589-1610, 1630-1639`.

**B22. §5.7, reading the campaign log [reg-07-shape-b-5].** int5 1963-1965; draft 2115-2117. Text: "The driver reads
the campaign log as it grows. Three consecutive members that ended without a bundle for one shared cause (the
member's last error line with its digits replaced by `#`, or else its exit code)". True: the log is read
incrementally but only at a stage boundary (in the settle after the stage's journal line) and once in the terminal
pass, never during a stage. The flag is therefore recorded when the stage holding the three members ends, not after
the third member. The cause key is the log row's `child_refusal` (the member's last non-empty error line with digits
replaced by `#`, truncated; for a launch-lineage refusal, the lineage reason code), or else the exit code together
with the `blocked_before_invoke` bit. Evidence: `joulewise/b5/driver.py:1533-1537, 1582-1594, 1638, 1691-1697`;
`scripts/run_campaign.py:4149-4168`.

**B23. §5.7, when the harvest command exits 6 [reg-07-shape-b-3].** int5 1988-1990; draft 2140-2142. Text: "exits 6
when a COLLECTED window has nothing present (`collection.zero_yield`)". True: exit 6 when the verdict is COLLECTED or
NO_COLLECTION, members were planned and no bundle is present; `collection.zero_yield` is emitted on the same
condition whatever the verdict. A chain stopped at exit 10, 11 or 12 therefore records the flag and exits 6.
Evidence: `scripts/harvest_b5_window.py:13-14, 103-104`; `joulewise/b5/harvest.py:7163-7165`. Not run on a fixture.
Twin: `flag_catalog.json` line 365 ("The harvest found no bundle present for a COLLECTED window").

**B24. §6.1, how the flag files are written [reg-08a-06].** int5 2106; draft 2258. Text: "All flag files are
append-only, with an fsync per line." True: that holds for `<custody>/flags/*.jsonl`. The monitor journals under
`hazards/monitor/` are append-only and written per line but synced to disk at most every 5 s and at close.
`derived/flags.jsonl` is created once in a single pass and never appended to (it is synced after each line). The
table also lists whole-document JSON files, which have no lines. Evidence: `joulewise/flags/sink.py:62, 106`;
`joulewise/hazards/monitor.py:93, 187-201, 275`; `joulewise/b5/harvest.py:980-992, 7324`.

**B25. §6.3, which flags are RESTRICTED [CAT-10].** int5 2166-2168; draft 2318-2320. Text: "the one precheck test
that reads a science energy ... (`member.anchor_energy_envelope_exceeded`, blinding RESTRICTED)". True: the catalog's
blinding field is a per-code default (191 STRUCTURE, 1 RESTRICTED). The harvest overrides it to RESTRICTED on
individual flags in two places: `member.target_phase_precheck_failed` when a remaining precheck reason name contains
"energy" or "effect" or ends in "_metric" (in practice the one reason `anchor_energy_envelope_unrecorded`); and
`diagnostic.s1_structural` for its precheck counts, always. "The one precheck test" is defensible as written; what
is missing is the two per-flag overrides, here or in §8, and in the two catalog notes. Evidence:
`joulewise/b5/harvest.py:612-614, 3950-3956, 6900-6904`; `joulewise/reduce.py:2327-2348`. Related: C2.

**B26. §6.4, the path of the sign-inconsistent marker [reg-08a-05].** int5 2273; draft 2425. Text:
"(`observed.sign_inconsistent`)". True: the marker is on each interval row, `observed.intervals[i].sign_inconsistent`
= true, on `battery.accumulator_excursion`; `observed` itself holds only `rule`, `intervals` (the first 8 rows),
`count` and `watts_per_unit`. Under SMC coverage `battery.accumulator_unavailable` carries the whole interval entry
at the same per-row key. Evidence: `joulewise/b5/harvest.py:2928-2946`; `tests/test_harvest_b5_window.py:2816-2833`.
Twin: `flag_catalog.json` line 22.

**B27. §6.4, assist after a charging-current read [reg-08a-02].** int5 2292-2293 and 2336-2338; draft 2444-2445 and
2488-2490. Text: "Computed only when no read in the span showed charging or AC loss."; "Had one read in force been
+450 mA, or one registry poll in the span read IsCharging Yes, the member would be removed by
`battery.member_span`, and no assist would be computed." True: assist is skipped only on a state reason, IsCharging
Yes or ExternalConnected No. A B0AC read above +200 mA removes the member by `battery.member_span`, and the assist
flag is still emitted and the discharged energy still written to `withheld/battery-assist.json`; in the worked
example with the 3 s read at +450 mA that energy is 30.02 J. Evidence: `joulewise/b5/harvest.py:2655-2665,
2709-2717, 5894-5896, 5930-5932` (the reader replayed the example; the refuter read the code). See C12.

**B28. §6.4, when a phase is assisted [reg-08a-03].** int5 2296-2301; draft 2448-2453. Text: "A phase is **assisted**
when any of these counts is nonzero" (the list begins with `smc_reads_in_force`). True: a phase is assisted when at
least one of three counts is nonzero: `smc_reads_negative`, `registry_publications_negative` (computed only without
SMC coverage) or `accumulator_intervals_over_limit`. `smc_reads_in_force` is nonzero for every covered phase and
decides nothing. Evidence: `joulewise/b5/harvest.py:2573-2574, 2770-2786`; the refuter's replay (five reads of 0 mA:
in force 5, not assisted).

**B29. §6.4, why the accumulator rule could not run [reg-08a-07].** int5 2315-2316; draft 2467-2468. Text: "(a field
not read at both publications, a counter that went backward, or no voltage)". True: there is a fourth reason: the
accumulated value changed while its tick counter did not. Evidence: `joulewise/hazards/battery.py:506-516`;
`joulewise/b5/harvest.py:2899-2910`. Twin: `flag_catalog.json` line 29.

**B30. §6.5, two NEG-8 condition names [reg-09-M1].** int5 2455-2456; draft 2607-2608. Text:
`neg8_gross_point_drift_exceeded`, `neg8_idle_sub_point_drift_exceeded`. True: no such strings exist; they are
lower-cased constant names. The strings the verdict writes are `neg8_bracket_abs_delta_exceeded` (gross) and
`neg8_bracket_idle_sub_abs_delta_exceeded` (idle-subtracted). The other names in the list are real. Evidence:
`joulewise/whole_window.py:164-169, 2333, 2340`. Twin: `flag_catalog.json` line 967 (note of `neg8.screen_failed`).

**B31. §6.2 and §6.8, five record codes that nothing emits [CAT-2].** int5 2150 and 2509-2511; draft 2302 and
2661-2663. Text: "All REPRESENTATION flags: receipts, ..., attempt history, the pin ledger, provenance digests,
naming, notices". True: `records.receipt`, `records.attempt_history`, `records.provenance_digest`, `records.naming`
and `records.notice` are defined in `joulewise/flags/catalog.py:140-146` and in the catalog and have no emitter. Of
the seven codes in that block only `records.lineage_formality` (`driver.py:2250`) and `records.pin_ledger`
(`controller.py:933, 1007`) can fire. Correction: say so, as the text does for `contention.kernel_task_share`. See C7.

**B32. §6.8, three more codes that nothing emits [CAT-3].** int5 2511-2512; draft 2663-2664. Text: "the OFF action's
output and the time-server offset; monitor probes falling inside phases". True: `clock.sntp_offset`,
`monitor.probe_in_phase` and `battery.accumulator_diagnostic` have no emitter. For the last, the condition it names
(no registered unit scale) now raises an error in the harvest. `network_time.off_output` is emitted
(`driver.py:1919`). Evidence: search of `joulewise/` and `scripts/`; `tests/test_harvest_b5_window.py:2493-2501`.

**B33. §6.2 ROSTER row and §6.7, what the four ignored-bundle codes do [CAT-6].** int5 2149; draft 2301. Text: the
ROSTER row gives EXCLUDE_MEMBER. True: only `roster.before_chain_started` acts as a flag: the harvest emits it on a
roster member whose run started before `chain.started`, and that member is removed under it. `roster.not_in_plan` is
emitted naming a run id outside the roster, is counted as unmatched and removes nothing. `roster.foreign_attempt`
and `roster.creation_unplaced` are never emitted as flags; they exist only as labels in the exclusion record's list
of ignored bundles, and `roster.foreign_attempt` cannot occur in a real harvest. For all four, the label path
removes a member only as `member.bytes_missing`, which is what §6.7 says. Evidence:
`joulewise/flags/exclusions.py:201-239, 264-295`; `joulewise/b5/harvest.py:4004-4010, 6956`. See C11.

**B34. §6.10, what `observed.evicted` counts [reg-09-M4].** int5 2685; draft 2837. Text: "`observed.evicted` counts
the evicted files". True: it counts ledger captures, one for each capture whose outcome is "absent" (at least one
of its files missing, every present file readable and matching). A capture with several missing files counts once.
A capture with a missing file and an unreadable file, or with its whole directory missing, is not counted. Per-file
states are in each entry's `artifacts` map in `derived/historical-custody.json`. Evidence:
`joulewise/b5/harvest.py:6229-6230`; `joulewise/calibration_ledger.py:6592-6776`. Twin: `flag_catalog.json` line 190.

**B35. §6.11, the four BASELINE member exclusions [CAT-7].** int5 2746-2747; draft 2898-2899. Text: "(40: 20
NUMBER_INTEGRITY, 16 PHYSICS, 4 BASELINE), each with the quantity or number it protects". True: the counts are
right. The 36 PHYSICS and NUMBER_INTEGRITY entries carry a `protects` text. The four BASELINE entries
(`member.admission_aborted`, `member.cooldown_evidence_unverified`, `member.strict_validation_failed`,
`member.target_phase_precheck_failed`) carry a `note` and name no protected quantity, and the test admits them by
name. So four live member exclusions are an unreviewed exception to the section's rule that an exclusion is allowed
for exactly two reasons. Evidence: `configs/gates/hazard_refusals.json`;
`tests/hazards/test_refusal_allowlist.py:158-162, 187`.

**B36. §6.11, what the allowlist test admits [CAT-8].** int5 2757-2761; draft 2909-2913. Text: "a new refusal cannot
enter the hazard path without being classed PHYSICS or NUMBER_INTEGRITY (or INTERNAL, which by definition stops
nothing) and saying what it protects". True: the test also admits the category DEFERRED_REPRESENTATION when the
entry names an owner lane and gives a `protects` text of at least 30 characters. That holds for refusal sites and
for excluding codes. The file holds no such entry at this head. Evidence:
`tests/hazards/test_refusal_allowlist.py:74-85, 183-189, 270-278`; `tests/hazards/refusal_census.py:106`. See C10.

**B37. Catalog `klass` against the allowlist's category [CAT-9].** `flag_catalog.json` and
`configs/gates/hazard_refusals.json`. True: of the catalog's 72 excluding codes, 64 agree with the allowlist. Four
carry the opposite reason: `member.cooldown_cap_hit`, `member.idle_window_suspect` and `member.timeout` are NUMBER
in the catalog and PHYSICS in the allowlist; `member.span_unknown` is PHYSICS in the catalog and NUMBER_INTEGRITY in
the allowlist. Four more are NUMBER in the catalog and BASELINE in the allowlist (the four of B35), which is a
placeholder and not a competing reason. The effect is the same either way and no test requires agreement.
Correction: make the four agree, in whichever file the orchestrator names.

**B38. §7.1, the NO_COLLECTION verdict [reg-10-M7].** int5 2784-2785; draft 2936-2937. Text: "**NO_COLLECTION:** the
chain started but no collection stage ran". True: NO_COLLECTION is written only when `night/chain-stages.jsonl`
exists and holds no collection row, which covers the stops at exits 10, 11 and 12; `chain.stopped_before_collection`
is recorded only then. If `chain.started` exists and the chain wrote no stage journal at all (killed before its
first stage ended), the verdict is COLLECTED and that flag is not recorded. Evidence:
`joulewise/b5/harvest.py:7111-7136, 7550, 7581`; `joulewise/b5/chain.py:935-938`. Read, not run. See C9.

**B39. §9.1, a spliced quotation [reg-10-M8].** int5 2972; draft 3124. Text: Fable's cold pass 4 view ("consistent
enough to seal now": ...). True: the report's sentence is "That is consistent enough to seal." (line 139 of
`cold-pass-4/REPORT.md`); "now" comes from the section heading at line 126. Correction: quote "consistent enough to
seal", or paraphrase without quotation marks.

**B40. §9.2, "126 of 170 s" [reg-10-M1].** int5 2994; draft 3146. Text: "B0AC was nonzero in 126 of 170 s under an
8B-plus-CPU-burner load, down to −5,331 mA". True: 126 is a count of SMC publications, not seconds. B0AC was nonzero
at 126 of 536 distinct publications (126 of the 270 inside the 170 s load phase, none at idle or in recovery), which
is about 63 s of the 170 s. The minimum is correct. §4.2 (int5 1261) already says "at 126 of 536 distinct SMC
publications". Evidence: the refuter recomputed from the probe's `smc5hz.jsonl` and `phases.jsonl`.

**B41. §11 item 3, what the import-graph test proves [reg-11-M3].** int5 3075-3076; draft 3227-3228. Text: "an
import-graph test proves the hazard path cannot reach them". True: the test proves it only for the
`joulewise/hazards` package with `scripts/hazard_monitor.py`, and for `joulewise/flags`. The rest of item 2's hazard
path does import retired modules: `scripts/run_night.py` imports `arm_readiness`, `arm_readiness_evidence_t0`,
`t0_rehearsal` and `network_time_off` at module level; `scripts/run_campaign.py` and `joulewise/bundle.py` import
`arm_readiness` at module level; `joulewise/b5/plan.py` and `joulewise/window_lineage.py` import the pack-tree
digest function from `arm_readiness` inside a function. Evidence: `tests/hazards/test_import_graph.py` and the
import lines. The writer of §11 is another pass; this fact is for that pass.

### Analysis plan

**B42. Plan §3.1, the order of close-out and finalization [plan-a-M2].** Plan 154-168, both copies. Text: "Each step
runs on the bytes of the step before it"; row 6 (dominance close-out) stands before row 8 (finalization). True: the
close-out cannot run first. Its program requires `--finalized-manifest`, and the builder rejects a manifest that is
not finalized (schema, freeze status, id) or that lacks the replay-sidecar attachment, which finalization writes.
The executable order is the mint (step 5), then finalization, then the close-out. Evidence:
`scripts/build_d165_dominance_closeout.py:219, 236-249`; `joulewise/dominance_closeout.py:41, 1704-1718, 1939-1958`;
`scripts/finalize_analysis_manifest.py:41-53`. Keep the line count above line 354.

**B43. Plan §4, two stale file digests [plan-a-M1].** Plan 205-214, both copies. Text: ALPHA spec file SHA-256
`8b796985…5c5c`, BETA spec `53e71b38…09c7`, "filled from committed bytes at f8164893". True at `9b0c680ed` (and
already at `fe28e5a0c`): ALPHA `a6498f56469448fd422e6ca2e0787b362a4fd6957bffab7d477ac7f30db38df6`, BETA
`2c0ee7189f9aa7e8f534be3cca3bf6f4125c23b5e7bf7ee1e600c7edf9d81ddc`. Commit `f4cf90472` regenerated both files. The
two `registration_sha256` values in the same passage are correct. Neither digest carries a FILL mark, so the seal
pass will not find them by searching for marks. Evidence: `shasum`; each pack's `producer_contract.json:58` and
`plan_tree.json:3831` carry the head values.

**B44. Plan §7.2, the role condition of the L2 ceiling [PB-2].** Plan 432-434, both copies. Text: "`claim_role`
primary". True: the code accepts primary or secondary. Both block-5 contrasts are primary, so no outcome differs.
The gate also accepts the outcome "equivalent" and tests three sensitivity reason codes, none of which can arise in
block 5. Evidence: `joulewise/analysis_engine/claims.py:388-408`.

**B45. Plan §8.2, which meter flags a member can carry [PB-4].** Plan int5 593, 596-600, 605; draft 607, 610-614,
619. Text: "the first analysed window of the block in which no member carries any `meter.*` flag"; "listed with its
flags (for example `meter.clock_fit_residual`)". True: only `meter.battery_activity` is a member-level flag (it
fires on any nonzero B0AC read inside a member window). `meter.absent`, `meter.drops_excess`, `meter.duplicates`,
`meter.clock_fit_residual`, `meter.pdtr_gain_out_of_band` and `meter.vbus_out_of_contract` are window-level. Read
literally, a window with a bad clock fit or dropped samples would still count as clean. No code implements the
central band at this head; it is descriptive and excludes nothing. Correction: a clean window carries no
window-level meter flag and has no member with `meter.battery_activity`; the example names a member-level flag.
Evidence: `joulewise/b5/harvest.py:6094-6148`; `joulewise/external/km003c_parse.py:80, 518-526`; registration §5.8.

## List R. Readability mismatches no refuter saw (consolidator checked; all seven hold)

**R1. Revision 6 and 7 lists, two paths broken inside a code span [H-4].** int5 116-117 and 161-162; draft 120-121
and 165-166. A line break inside the back-ticks renders as a space, giving `.../gate-prune/ FROZEN_HEAD.md` and
`.../neg8-council/ RULING.md`. The files are `/Users/edr/night-archive/gate-prune/FROZEN_HEAD.md` and
`/Users/edr/night-archive/gate-prune/neg8-council/RULING.md` (both exist). Correction: keep each path on one line.

**R2. §0.12, "13 spares" [reg-01-M6].** int5 546; draft 589. Text: "The 7 references and 13 spares are copies of one
workload". A window has 7 spares (three for each triplet, one for the midpoint), as the rest of the document says.
13 is the number of spare configuration files, because each spare is repeated in the cumulative spare-set
directories; 7 are distinct by SHA-256 (recounted by the consolidator: 13 files, 7 digests). That file count is why
the `neg8_reference` pin has `config_count` 20.

**R3. §3, "now about 125 s" [reg03-M4].** int5 1157-1160; draft 1224-1227. Text: "(revision 4: t0 − 8, −6 and
−5 min, about 450 s of idle; now about 125 s)", and in the next sentence "a request at t0 − 180 s leaves about 150 s
of margin". The arithmetic that gives 450 s for revision 4 (480 s less a 20–31 s exit) gives 149–160 s for the 180 s
lead. The code comment says about 150 s (`scripts/magistrate_watchdog.py:86-87`). No source for 125 was found.

**R4. §4.1, the identity refusal in the refusal list [reg-04-arm-a-05].** int5 1188; draft 1255. Text: "or an OS
build no acceptance judged". The code refuses when the pair (OS build, machine model) is not a judged pair, so a
judged build on an unjudged machine model also refuses (`joulewise/hazards/arm.py:74, 371-378`). Step 2 of the same
section and §4.7's body say both; the refusal list and §4.7's heading drop the model.

**R5. §6.4, the `battery.unmeasured` worked example [reg-08a-04].** int5 2287-2288; draft 2439-2440. Text: "State
reads at 0 s and 62 s and none after: the stretches are 62 s and 130 − 62 = 68 s". By the rule stated three lines
earlier, and by the code, only the last read at or before the span's start (62 s) is in the set, so one stretch is
judged: 68 s. The read at 0 s plays no part. The outcome is the same (`joulewise/b5/harvest.py:2729-2746`).

**R6. Plan §2.4, "the only reference inside the window" [plan-a-M3].** Plan 110-111, both copies. True for ALPHA and
BETA. GAMMA has three interior reference stages: the midpoint at the boundary between its decode and prefill
halves (the NEG-8 midpoint, with a spare) and two diagnostic interior references, whose role
`window_interior_reference_diagnostic` is not a NEG-8 role and does not enter the spread. Correction: the only
NEG-8 reference inside the window. Keep the line count above line 354.

**R7. Plan §8.1 and §14, "the §7.1 data" [PB-3].** Plan int5 504 and 762; draft 517 and 776. §7.1 holds no data. The
series of differences is the worked example of §7.2 (plan 438), which §2.4 cites correctly.

## List U. Undefined terms

None of these was sent to a refuter. The consolidator checked each by listing where the term occurs in the draft.
"First used" gives draft lines, with int5 lines in brackets. Where a reader found the meaning in the code, it is
given as the fact for the gloss. The writing standard's choice for each is: build it before first use, gloss it at
first use, or delete it. Two undefined terms that stop or resize collection are in list A (A4, A10).

### Registration

- **U1. H_claim.** First used draft 7, 26, 110, 121, 193 [int5 7, 24, 106, 117, 189]. Defined at §0.18 (draft 896)
  and §11: "the commit whose code every block-5 window runs". [reg-00 U-1]
- **U2. G3; floor packs.** Draft 151 [int5 148]. Glossed later at draft 1078-1079 ("`scripts/check_window_provenance.py`
  (G3)") and 2600 ("G3, the desk provenance checker"). [reg-00 U-2]
- **U3. The evidence-manifest ruling.** Draft 196 [int5 191-192]. Never explained. The three numbered items that
  follow describe rulings Q11 and N8 but not this one; the only related text is a table row at draft 3373. [reg-00 U-4]
- **U4. Claim root.** Draft 206 [int5 202]. Never defined. §0.17 later builds "the claim root for science members
  and the bound root for NEG-8 and reference members"; elsewhere the text says "claim runs root". [reg-00 U-3]
- **U5. T3; T3 Code.** Draft 221, 229 [int5 216, 223]. Never said: an agent harness formerly used as a control plane
  on this machine, which the census used to look for. [reg-00 U-5]
- **U6. Sentinel reading.** Draft 390 [int5 347]. Glossed at draft 2390: the short idle reading the controller takes
  right after the request. [reg-01 U3]
- **U7. Clean dwell; dwell.** Draft 391 and 1248 [int5 348, 1181]. Described only at §4.2 (draft 1359 on): the
  period at the arm, in 30 s intervals, that ends after 180 s of consecutive clean intervals or at a 2,700 s cap,
  during which contention and the clock are measured. [reg-01 U2, reg-04-arm-a-07]
- **U8. Arm, in three senses.** Draft 391, 448, 452, 463, 536 [int5 348, 405, 409, 420, 493]. Defined at §0.15
  (draft 804) after three uses, as the decision sequence before the start. It is also the code's word for one side
  of a quad (§0.8), and "decode arm, prefill arm" (§0.12) means the decode stages and the prefill stages of a
  window, which is never defined. [reg-01 U1]
- **U9. Harvest.** Draft 418, 427, 452, 581 [int5 375, 384, 409, 538]. Defined at §0.17 (draft 884):
  `scripts/harvest_b5_window.py`, the desk program run after the chain exits. [reg-01 U4]
- **U10. Science member; the verdict writer.** Draft 536-537, 547, 582 [int5 493-494, 504, 539]. "Science member" is
  never defined: a member of a reported-cell or contrast stage, as opposed to a corpus or reference member. "The
  verdict writer" is first explained at draft 609, after its use. [reg-01 U5]
- **U11. Strict validation; full strict validation; the strict check; the structural bundle check.** Draft 98 and
  607-629 [int5 94, 563-586]. Section 0 never says what strict validation checks or how the structural bundle check
  differs from it; only the custody triangle and the config binding are glossed. [reg-02b U1]
- **U12. Family ("either family", "the idle-subtracted family").** Draft 639, 731 [int5 596, 685]. Never introduced:
  the two NEG-8 claim families are the gross energies and the idle-subtracted energies. [reg-02b U3]
- **U13. Runs root.** Draft 647, 704 [int5 604, 658]. §0.17 (draft 846) says only that the plan carries "two freshly
  created runs roots"; it never says a runs root is the directory under which member bundles are written.
  [reg-02b U2]
- **U14. Evaluation basis.** Draft 698 [int5 652]. Only use. Which bytes the second digest covers is not stated.
  [reg-02b U5]
- **U15. The gate inventory; the classes PHYSICS, NUMBER and REPRESENTATION.** Draft 822 [int5 776]. Only use of
  "gate inventory"; what puts a code in each class is not stated. [reg-02b U4]
- **U16. The claim gate; `claim_ready_for_l2_l3`.** Draft 928 [int5 882]. Only use, with a pointer to analysis plan
  §7.2. [reg03 U4]
- **U17. L2 harness.** Draft 1000 [int5 946]. §0.19 defines L2 as a rung of the claims ladder (a comparative
  result). The test-level meaning is never built, so one label has two meanings. [reg03 U1]
- **U18. Bound bundles (a table column).** Draft 1018 [int5 961-971]. The legend names four numbers for claim bundles
  only. Bound bundles are the 12 NEG-8 corpus members in the bound runs root; their three numbers are expected,
  present and succeeded. [reg03 U5]
- **U19. The courier; the durable record.** Draft 1032, 1942, 1944, 2057, 2090, 2136 [int5 978, 1790, 1792, 1905,
  1938, 1984]. Never defined. The courier is the driver's end-of-window step that launches a headless session to
  email Ed the structural report (`scripts/run_night.py`, the `HAZARD_PACK` instructions at 1849-1860). A release
  condition of the watchdog depends on `courier.sent` (A9). [reg03 U2, reg-06-shape-a-08, reg-07-shape-b-7]
- **U20. "c1, c2 and the d117 magistrate events".** Draft 1226 [int5 1159]. Never defined, so the source of the
  20–31 s figure cannot be found from the text. [reg03 U3]
- **U21. Judged epochs.** Draft 1243 [int5 1176]. "Epoch" as an (OS build, machine model) pair is defined only in
  §4.7 (draft 1667). [reg-04-arm-a-08]
- **U22. Clock linearity; timed slew.** Draft 1248, 1364 [int5 1181, 1297]. Rule ii (the residual stays within 1 ms
  of its start) is the linearity check but is never given that name. A slew is the clock being run fast or slow at a
  set rate for a set time, instead of being stepped. [reg-04-arm-a-10]
- **U23. Anchor fit.** Draft 1264, 1296 [int5 1197, 1229]. §0.14 builds the per-member anchor bound (a set of offset
  and rate pairs) and never calls it a fit. [reg-04-arm-a-09]
- **U24. The `PowerTelemetryData` accumulators.** Draft 1309 [int5 1242]. Running sums of battery charge power and
  discharge power with their sample counts, from which a mean power between two publications is taken
  (`joulewise/hazards/battery.py:154-160, 479-484`). [reg-04-arm-a-11]
- **U25. "Fences the plan's span".** Draft 1575 [int5 1423]. First use of "fence": which sessions the watchdog keeps
  from starting, and over which interval, is not said there. [reg-05 U4]
- **U26. Config-inventory digest.** Draft 1631 [int5 1479]. The item defines three digests for each unit and never
  names this one; `identity_pins.json` carries both `config_inventory_sha256` and `config_set_sha256` (B18).
  [reg-05 U3]
- **U27. Bracket reservation.** Draft 1652 [int5 1500]. First described at §5.1 (draft 1688): the chain's first
  stage. [reg-05 U5]
- **U28. Continuation.** Draft 1669 [int5 1517]. Only use. A record that extends the acceptance to a further (OS
  build, machine model) pair (`joulewise/calibration_epoch_continuation.py`); see A5. [reg-05 U2]
- **U29. Protected core; protected.** Draft 1801, 1808 [int5 1649, 1656]. The nearest definition is at draft 2723:
  "protected measurement code (the controller, the campaign runner, ...)". [reg-06-shape-a-06]
- **U30. The mint.** Draft 1839 [int5 1687-1690]. Section 0 uses it only as a forward pointer. It is the core
  function that builds the bound from the corpus bundles (`whole_window._mint_hazard_neg8_drift_bound`).
  [reg-06-shape-a-07]
- **U31. Calibration identity.** Draft 1857, 1859, 1909 [int5 1705-1707, 1757]. The digest
  `calibration_identity_sha256` that each bundle's metadata records for the calibration it was measured under; the
  text does not say what it is a digest of. [reg-06-shape-a-09]
- **U32. Canonical condition.** Draft 1857 [int5 1705]. A fixed workload test: profile `df_rq_mid`, 1,024 prompt
  tokens, 256 output tokens, no dataset or suite reference, with the config bytes bound to the metadata digest
  (`joulewise/whole_window.py:4513-4516, 4811-4819`). [reg-06-shape-a-10]
- **U33. Plan tag.** Draft 1993 [int5 1841]. Only use; not tied to a named configuration key. [reg-07-shape-b-9]
- **U34. The campaign log; the operator logs.** Draft 2115, 2142 [int5 1963, 1990]. The campaign log is
  `<runs root>/campaign_log.jsonl`, one row for each launched member. The operator logs are
  `<custody>/operator-logs/*.log`, one for each stage, of which only lines starting "error:" are grouped.
  [reg-07-shape-b-8]
- **U35. The sensitivity line; both lines of the sensitivity pair.** Draft 2346, 2454, 2488 [int5 2194, 2302, 2336].
  Only a pointer to analysis plan §8. [reg-08a-09]
- **U36. The pinned reducer's environment barrier.** Draft 2360 [int5 2208]. Not built: where it sits in the reducer
  and what it tests (the code calls it "the pinned reducer's environment claim barrier",
  `joulewise/environment_admission.py:66-68`). [reg-08a-13]
- **U37. The unwritten-flag marker.** Draft 2382 [int5 2230]. Its meaning arrives in §6.10: the prefix a core writer
  prints before a flag it could not write to its file (`JOULEWISE_UNWRITTEN_FLAG `). [reg-08a-12]
- **U38. The extraction spec.** Draft 2515 [int5 2363]. Next appears only in §16. It is each floor pack's
  `extraction_spec.json` (B43). [reg-08a-11]
- **U39. Sidecar.** Draft 2519 [int5 2367]. The file that holds the chain script's recorded SHA-256
  (`joulewise/b5/harvest.py:5558-5564`). [reg-08a-10]
- **U40. n_r and n_b.** Draft 2641 [int5 2489]. Only use. The harvest's cell record names them `n_repeats` and
  `n_quads`. [reg-09 U1]
- **U41. Frozen anchor.** Draft 2767 [int5 2616]. Only use; which records qualify and what makes one eligible is not
  stated. [reg-09 U3]
- **U42. The desk epoch; the desk T1.** Draft 2804 [int5 2652]. "T1 bindings" is glossed nearby; the epoch (the
  identity-epoch file, `--identity-epoch-json`) is never built. [reg-09 U5]
- **U43. A held lease; an unfinished recovery.** Draft 2809 [int5 2657]. Only use of "lease". These are kept
  refusals that stop collection. [reg-09 U4]
- **U44. Governed rows; sequence.** Draft 2827 [int5 2675]. §0.11 does not say which ledger rows are governed or
  what sequence 376 indexes. [reg-09 U2]
- **U45. Float; battery float.** Draft 306, 2982, 3135 [int5 263, 2830, 2983]. Never built. The measured condition
  that ends "wait for float" is IsCharging No with a battery current of 200 mA or less in magnitude, on AC power.
  [reg-10 U1]
- **U46. Collection head.** Draft 3013 [int5 2861]. Only use. The defined term for the sealed commit is H_claim,
  which §11 lets be extended, so which commit is meant is not stated. [reg-10 U4]
- **U47. Changed-path map.** Draft 3016, 3213 [int5 2864, 3061]. The nearest description, a `git diff --name-only`
  list against H_claim, is given for pin-only commits and not tied to the term. [reg-10 U2]
- **U48. R3, with two meanings.** Defined at draft 298-299 as the standing fix route and used so in §7; in §9.1 it
  is also a Sol finding id ("R3 (BLOCKER)"), and "R3-1" and "R3-5" are a third use. [reg-10 U5]
- **U49. The count-adjusted bound; the evaluator; the single strict predicate.** Draft 3124 [int5 2972]. §0.12
  builds the first as bound(n_s, n_e); the other two are not tied to §0.12's names. [reg-10 U3]
- **U50. The governed reader.** Draft 3408 [int5 3253]. Only use: which reader, what governs it and what it refuses
  are not said. [reg-11 U1]

### Analysis plan (U51 to U55 sit above line 354; keep the line count)

- **U51. Multiplicity family.** Plan 29-30. Registration §0.19 glosses only "Holm". It is the set of contrasts
  corrected together. [plan-a U2]
- **U52. Claim ceiling.** Plan 36. "Ceiling" appears nowhere in the registration: the highest ladder level a
  sentence may reach. [plan-a U1]
- **U53. Bracket, in a second meaning; gross-family.** Plan 237-240. Registration §0.11 defines the bracket as the
  pre and post calibration pair. Here it is the NEG-8 screen record that holds the drift allowances
  (`idle_admission_core.neg8_bracket`). [plan-a U5]
- **U54. Operative (floor; fiducial bound).** Plan 308-313. Which of a bracket's bounds is the operative one (the
  code's `registered_common_mode_operative_bound`) is not stated, so the sweep range cannot be rebuilt. [plan-a U3]
- **U55. Anchor-shift energy envelope half-width; residual half-widths.** Plan 309-316. Not built; "envelope" and
  "residual" mean other things in the registration, and the recorded field that supplies w_i is not named.
  [plan-a U4]
- **U56. Metrology term; metrology interval; governed random-error variances.** Plan 389-394. Not built in either
  document. In the code the only such field is `E_idle_mean_j2`, read for the metric `energy_request_j` only (A19).
  [PB-U2]
- **U57. `confirmatory_status`; evidence class "legacy".** Plan 432-434. The text does not say what sets the first,
  or that evidence is legacy when `evidence_class` is `legacy_l1`. [PB-U3]
- **U58. HAZARD root; a HAZARD floor or contrast.** Plan int5 662, draft 676. The code's name for a runs root
  collected by the block-5 hazard-path driver. [PB-U4]
- **U59. "memo 4.1", "memo 4.3", "memo 3.3", "memo 3.7".** Plan int5 664-667, draft 678-681. No memo is named in
  the plan. The registration names a pre-mortem memo only in §16 (`/Users/edr/night-archive/ia-0a40/MEMO.md`).
  [PB-U1]
- **U60. Bracket replay; ledger-cutoff baseline.** Plan int5 666, draft 680. Not built; the only pointer is that
  memo. [PB-U5]

## Refuted

No reported mismatch was refuted as a whole: 73 verdicts, 73 CONFIRMED. The refuters did overturn these parts of
readers' accounts. The reader's version must not be carried into the text.

- **reg-10-M1.** The reader's replacement, "roughly 101 s", is wrong; the nonzero time is about 63 s (B40).
- **reg-08a-06.** The reader implied `derived/flags.jsonl` is not synced after each line; it is. Only "append-only"
  misdescribes it (B24).
- **reg-05-arm-b-M3.** The reader said no block-5 module reads the load average; each member records it. Only the
  `corecaptured` half of the sentence is false (B17).
- **reg-07-shape-b-5.** The reader faulted "the member's last error line with its digits replaced by `#`"; that
  clause is substantially right. What is wrong is "as it grows" and the fallback key (B22).
- **reg-02b-M3.** The reader listed a separate 5 ms cap on the wall-minus-monotonic change as an omitted condition;
  the 5 ms effective bound already implies it (A1).
- **reg-04-arm-a-04.** The reader's "a clean arm dwells about 180 s" is the minimum, not a typical value (B4).
- **reg-01-M5.** Neither of the reader's alternative counts (26, 31) explains the 28; the sample includes members
  with no cooldown (B6).
- **reg-09-M3.** The reader's extra cause "gross and idle-subtracted counts differ" exists in the evaluator but
  neither caller can produce it; two other causes the reader missed are real (A14).
- **reg-11-M2.** The reader said the registration never mentions the display sleep; it names the flag kind
  `display_sleep_action_failed` once. It still never says the chain adds the argument (A18).
- **reg-10-M5.** The reader presented both extra conditions as outcome-changing; only the unresolved dispatch
  changes an outcome (A17).
- **CAT-10.** The reader faulted "the one precheck test that reads a science energy"; the phrase is defensible. The
  defect is the two unstated per-flag overrides (B25).
- **CAT-9.** "The only disagreements" holds only if BASELINE is read as unclassified (B37).
- **CAT-3.** "Not in `harvest.CODES`" does not separate the three codes from `network_time.off_output`, which the
  driver emits; the absence of any emit site does (B32).

## Not confirmed and not counted: reader notes that could hide a mismatch

The readers could not check these. No refuter looked at them. They are listed because each could bear on a number,
a pin or a registered sentence.

1. **§4.6 item 3, the interpreter behind the runtime pin** [reg-05]. The identity-pin generator's default runtime
   Python is `/Users/edr/code/JouleWise/.venv/bin/python` (`scripts/write_b5_identity_pins.py:142`), and the
   measurement clone has no `.venv`. Whether that is "the measurement interpreter" the chain runs was not
   established.
2. **§5.3, the core reader and the v5 corpus manifest** [reg-06]. Whether `load_neg8_drift_bound_artifact`
   authenticates a 12-member block-5 bound was not traced; `REGISTERED_NEG8_REFERENCE_CORPUS_DIR` points at
   `configs/campaigns/neg8_reference_corpus/derivation`, not the `_v5` directory. The harvest's collected-subset
   route is the fallback.
3. **§0.2, "a record actually spanned 127–130 ms (median 128.8 ms)"** [reg-01]. The reader's mean record length for
   each capture gives 127.0–131.7 ms, median 128.9 ms; the statistic meant is not specified.
4. **§7.2, "since Opus audit F5"** [reg-10]. `INTEGRATION_TODO.md` lists Opus findings F1, F2, F3, F4a and F6, and
   no F5.
5. **§2** [reg-03]. Commit `3e2f67fb6` in the quoted cooldown-smoke record does not resolve in the int5 repository.
   "An ALPHA verdict needs about 3,700 s" has no source in code or configs. "The window plan of each attempt sets
   `g10: true` until a G10 record exists": `joulewise/b5/plan.py` only validates a boolean, and no code that
   decides the value was found.
6. **Three window reasons outside the catalog** [catalog]. The harvest can write `window.null`,
   `exclusions.function_unavailable` and `harvest.fault`, which are neither catalog codes nor pack-scoped reasons
   and are spelled in neither document.
7. **§13, "28 open disagreements in all"** [reg-11]. Reproducible only if the documented `g3.recompute_failed`
   disagreement is left out; the counting rule is not stated.
8. **§11, files outside the sealed inventory's roots** [reg-00]. Whether a window executes or reads
   `configs/campaign_policies/quiet_mac_p2_b5.json`, `configs/campaigns/window_reference_spares_v5/` or
   `identity_pins.json`, and how those are pinned, belongs to the pass that writes §11.
9. **Lane L9** [plan-a, plan-b]. The kept-unit behaviour of the reported-energy issuer, the floor extraction and
   the claim gate rests on code that is absent at `9b0c680ed` (`joulewise/paper_reported_energy.py` handles only
   the full count), as the plan itself says.

## Digests marked `FILL[B5-FINAL-HASHES]`

The readers recomputed each at `9b0c680ed`. None differs from the digest written: `identity_pins.json`
`a0865895…`, `configs/pins/registry.json` `a4a2be94…`, `sizing_b5.json` `89e7ea70…`, the three plan trees, and the
`scripts/prewindow_check.sh` prefix `d8458eea588a746f`. The only stale digests found are the two unmarked ones of
B43. `flag_catalog.json` hashes to `2b1595e4…` in the int5 copy; the registration writes no digest for it.

