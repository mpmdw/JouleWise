# Block 5, second seal: consult after BETA attempt 5 (the stale calibration acceptance) and the decision

Magistrate activation bab1c330 (Opus 5.5, headless), 2026-10-11. Brief section 6 rule 1 (same cause twice:
BETA attempts 4 and 5, `calibration.bracket_acceptance_failed`). Structure only.

Clock times in `seal2-beta-a5-window.md` are about twenty minutes late: the harvest ended 07:19 PDT, the
cause was found 07:20, the seats were convened 07:22, the hold was written to RUN_STATE 07:30.

## The seats (blind to each other; brief and both reports are copied under `seal2-beta-a5-consult/`)

- **Sol 6.1**, effort high, through `codex-run-v3`, empty write scope: `sol-consult.md`.
- **Opus 5.5** agent, read-only: `opus-consult.md`.

They agree on every question that decides the next step.

1. **Cause.** `evaluate_calibration_bracket` (`joulewise/calibration_bracketing.py`, near lines 2500 to 2602
   at the harvest pin `0699abbb0`) looks at every ledger capture recorded after the acceptance's cutoff
   (sequence 376), not only the window's own two. One capture of class `systematic-invalid` marks the
   acceptance stale and returns before the window's endpoints are compared. Ledger sequence 456 (the opening
   capture of BETA attempt 3, 44.38 ms against the 36.46 ms screen) is the only such row. Attempts 4 and 5
   contribute nothing; their four captures are valid and inside the range of the 24. A GAMMA window today
   would read stale. Both seats ran their own count: no range-expansion trigger; 41 valid captures counted
   against the doubling trigger's 48.
2. **It is the registered rule, stated in the registration** (section 4.6 item 2, lines 2482 to 2511 of the
   sealed file): "The capture that fired the trigger stays in the ledger, so every later window's bracket
   fails the same way until a new acceptance is issued", and no program stops the next arm: "The lead reads
   the reasons in the harvest's flag (structure, no energy), arms no further window, and takes the question
   of a new acceptance to a cold gate." The lead did not do that after attempt 3 or after attempt 4. Attempt
   3's own harvest could not show the reason (a session never finalized stops at `calibration.no_bracket`);
   attempt 4's was the first that could, and `harvest.json` carries the flag code without the reason.
3. **The registered cure (a new acceptance) is not desk work.** It needs a new calibration pre-registration
   revision, two or three derivation sessions (7,680 s each), an issuance, changes to files a window reads
   (the acceptance file, its registry in `calibration_bracketing.py`, the three packs' plan trees, the
   identity pins), so a third seal, a new clone and a restart at ALPHA (registration 7.5), losing ALPHA's
   claim-usable window. Two to three days. The new acceptance would carry the same triggers.
4. **The rule is out of proportion.** The screen is the sample maximum of 24, so about 1 new capture in 25
   exceeds it with nothing wrong; any valid capture outside the range of the 24 is a second trigger; and the
   doubling trigger fires after seven more valid captures (three whole windows) whatever they read. Opus's
   seat puts the chance that 18 new captures all stay inside the old range at 32 %. The rule was certain to
   fire in a block of back-to-back windows. What a window's own two captures measure (the level now, the
   drift across the window) stays checked by the window's own bracket. Opus's seat adds that row 456 is a
   real excursion (about 4.3 standard deviations, contention journal clean, back to 31.4 ms 46 minutes later)
   and deserves a re-derivation, due before the next block's seal.
5. **Shortest lawful route (both seats):** a prospective cold erratum to registration 4.6 item 2 (line 2600
   allows one before the next arm), implemented in the harvest's desk checkout only, on the pattern of
   Erratum 2. The measurement clone, the seal and the acceptance's bytes do not change.
6. **Attempts 4 and 5 stay not claim-usable**, kept, disclosed, never analysed. A re-harvest may change
   `claim_usable` only for a repaired program (registration 7.2); the program applied the rule as written;
   "prospective" excludes completed attempts. Attempt 4 also slept. Attempt 5 has no physical objection on
   the released records.

One difference, not a disagreement on the route: Opus's seat would have the analysis print every floor of a
window that carries an observed trigger also under the widest capture bound seen in the epoch (44.38 ms
today). Sol's seat proposes no number and leaves the criterion to the gate. The erratum's cold gate rules on
it. No judge is convened for the consult itself.

## Decision (orchestrator)

- No pack is armed until Erratum 3 is admitted and the harvest program that implements it is pinned
  (`B5-ARM-RELEASED: none` on main since 07:30 PDT).
- The cure is **Erratum 3 (prospective, desk only)**, for attempts whose t0 is later than its admission time:
  the three triggers that range over the whole ledger (`new_systematic_failure_challenges_preflight_screen`
  raised by a capture of another session, `new_valid_same_identity_capture_expands_observed_range`,
  `corpus_doubles_from_24_to_48`) are recorded and named in `harvest.json` and do not fail a bracket; every
  check of the window's own evidence stays as sealed (its own pre capture above the screen, its own drift,
  identity, protocol and estimator bytes, endpoints, ledger integrity). Whether a wider printed bound goes
  with it, and what, is put to the gate as a question. A re-derivation of the acceptance is due before the
  next block is sealed.
- The registered alternative (item 3) is rejected for this block: it costs ALPHA's window and two to three
  days and would go stale again the same way.
- Attempts 4 and 5: not claim-usable, kept, disclosed, never analysed, never harvested by the new program
  for a deciding record.
- Correction recorded: the decision of 2026-10-10 that armed attempt 5 unchanged misread attempt 4's cause.

## Next action (do the first step that is not done)

1. Draft `docs/process_traces/2026-10-block5/trigger-erratum/ERRATUM-draft1.md` (Opus 5.5), terms built
   before use, with the open questions for the judge: the wider-bound question above; that the clone's sealed
   verdict writer will go on recording a failed bracket on governed windows (it surfaces as
   `whole_window.not_passed`, disclosed only: confirm from the catalog and say it in words); which ledger the
   claim consumer reads when it re-evaluates a bracket at analysis time (`joulewise/analysis_engine/claims.py`
   near line 64, `whole_window.py` near 5551).
2. Cold gate, registration section 10: one refuter (Opus 5.5 agent) and one judge (Fable 5.1,
   `claude -p --model fable` from a fresh worktree, foreground probes only). Files `REFUTATION.md`,
   `JUDGE-CHARGE.md`, `RULING.md`, then `ERRATUM.md` with the ruling's corrections. A Fable refusal goes to Ed.
3. Harvest lane, cut from `0699abbb0881ce64b39c46ba07de568cc3848260` (branch
   `lane/2026-10-11-harvest-trigger-scope`, not merged into main): `joulewise/calibration_bracketing.py`,
   `joulewise/b5/harvest.py`, tests. Sol 6.1 implements against the admitted text. Gates as for pin 3
   (`sources-erratum/harvest-pin3-gates.md`): item-by-item check against the text, an independent executing
   review, the lane's tests and the whole suite, a cold Fable pass, the before/after comparison on the
   rehearsal copy (a window with a fresh acceptance must give byte-identical derived output), an exploratory
   labelled run over attempt 5's bytes printing verdict words and reason codes only, findings dispositioned.
   The program under gates is never run over a governed attempt's bytes before it is pinned.
4. Seal record Addendum 4 on main (admission time, `B5-HARVEST-PIN:`, file digests, gate record path);
   canonical root `pull --ff-only` with no night job loaded; desk root moved to the pin.
5. Arming steps gain the pre-arm probe (`opus-consult.md` section 6: `evaluate_calibration_bracket` over
   `discover_calibration_candidates` on the live ledger; print freshness, observed triggers and the doubling
   count) and RUN_STATE item 24 is filled in; `B5-ARM-RELEASED:` back to `beta gamma`.
6. Before the arm, two structure-only counts Opus's seat asked for: whether attempt 4's members that spanned
   a sleep carry a member exclusion (a physics gap if not), and the status reason codes of attempt 5's six
   failed members of its last stage.
7. Arm BETA attempt 6 (brief section 5).

## Added 08:35 PDT: the cold gate ruled; the step list as corrected by the ruling

Erratum 3 went through the gate of registration section 10: draft `trigger-erratum/ERRATUM-draft1.md` (Opus
5.5 drafting seat), refuter `REFUTATION.md` (Opus 5.5 agent: three BLOCKER, six MAJOR findings), judge
`RULING.md` (Fable 5.1, cold, from the fresh worktree `/Users/edr/code/JouleWise-wt-harvest-trigger`; sha256
`becbf587bb84a61954060a19dc54f78517c088c8710e514d73bb31af0cdea260`; charge `JUDGE-CHARGE.md`; launcher and
output under `/Users/edr/night-archive/b5-consults/beta-a5-stale/erratum-judge/`). Last line:
`RULING: ADMIT-WITH-CORRECTIONS`. Every finding of the refuter was upheld, two with the rule modified.

What the ruling fixes, for whoever continues:

- **Admission time** `2026-10-11T17:00:00Z` (epoch 1791738000, 10:00 PDT). An attempt is governed when its
  plan's t0 is later. BETA attempts 4 and 5 are not governed and stay as decided above.
- **Pin before arm.** No governed attempt is armed until the implementing harvest program has passed its
  gates and Addendum 4 step 2 is on main. (The draft allowed an arm on the admitted text alone; rejected:
  under the old pin a window with row 456 in its ledger is lost with certainty.)
- **The rule decides by event, not by trigger name**, and both sites of the bracket evaluation that fail on a
  stale acceptance are covered (the refuter executed that a change at the first site alone does not cure it).
- **The harvest lane may also change `joulewise/calibration_bracketing.py`**, desk checkout only, behind a new
  argument `trigger_scope` whose default returns exactly the sealed behaviour; Addendum 4 step 1 carries the
  amendment of registration section 11 item 4.
- **Retention (new pre-arm condition).** The capture directory of every capture recorded after the
  acceptance's cutoff, those of the removed BETA attempts included, stays at the path the ledger records
  until the release event. Moving or offloading one removes every later window. The custody roots are already
  on the never-move list of brief 5.1.
- **The pre-arm run** (ruling section D item 13): from the pinned desk checkout, the bracket evaluation over
  the live ledger for a hypothetical window starting now; the arm record gets the snapshot's refusal reasons
  (must be empty), the candidate count and the count of valid finalized captures (must be equal), the
  observed triggers, the doubling count and the sequences of other sessions' systematic captures. Two or more
  such sequences: two-seat consult before any arm; two consecutive: cold gate.
- **Claim consumers and a sensitivity bound** (items 10 and 14) are admitted as rules now and built in a new
  analysis lane, L9-BRACKET, blind, before the release event. They gate no arm.
- **The exploratory run over attempt 5** is limited to the bracket evaluation over its archived ledger copy,
  printing status words and trigger names only (item 12); never a verdict or `claim_usable`.

The two counts of step 6, both answered from structure-only output:

- Attempt 5's six failed members are six consecutive members of its last science stage, each with
  `admission_decision` `abort` (the idle baseline before the run was not quiet enough and the member was not
  run). Consecutive aborts over about 25 minutes near 05:40 to 06:00 PDT match the system malware scan of
  RUN_STATE item 14, which this t0 was known not to avoid. No `stage.members_refused_pre_bundle_identical`.
  It does not hold an arm; prefer a t0 that avoids the scan hour.
- Attempt 4's members and the sleep (`/Users/edr/night-archive/b5-consults/beta-a4-sleep/member-overlap.txt`,
  made 2026-10-10): five members' run spans overlapped a sleep; four of those failed and one succeeded with a
  four-second sleep in its post-run stage; no member's sampling span overlapped a sleep. So no succeeded
  member measured across a sleep. That members run in dark wake carry no code is the open point already
  recorded as desk lane (a) of RUN_STATE item 22.

Step list from here (replaces steps 2 to 7 above):

2. done (ruling).
3. `trigger-erratum/ERRATUM.md`: the draft's sections 1 to 3 with the ruling's corrections, the ruling's
   section D copied as sections 4 to 6 (assembly seat started 08:33 PDT). Commit it to the records branch and
   merge the records branch into main; its SHA-256 as committed on main goes into Addendum 4 step 1.
4. Harvest lane `lane/2026-10-11-harvest-trigger-scope` (worktree `/Users/edr/code/JouleWise-wt-harvest-trigger`,
   cut from `0699abbb0`): Sol 6.1 at effort xhigh implements section D items 0 to 8 (brief
   `trigger-erratum/BRIEF-sol-impl.md`; report and log under
   `/Users/edr/night-archive/b5-consults/beta-a5-stale/impl/`, started 08:33 PDT). The seat commits nothing:
   read its report, run the lane's test modules yourself, commit on the lane branch, push the branch.
5. Gates, recorded in `trigger-erratum/harvest-pin4-gates.md` (model: `sources-erratum/harvest-pin3-gates.md`):
   item-by-item check against section D; an independent executing review by a seat that did not write the
   code; the lane's modules and the whole suite on the lane's tree (non-venv Homebrew python3.13, the shard
   runner); a cold Fable 5.1 pass; the sealed-scope byte-identity test; the before/after comparison on the
   rehearsal copy against pin `0699abbb0`; the two stale-state fixtures (Erratum 2 recovery; a GAMMA-shaped
   window) with the window-removing codes they print; the limited exploratory run over attempt 5's archived
   ledger copy; the constant checked against Addendum 4; every finding dispositioned. A finding that the
   admitted text cannot be implemented exactly goes back to the cold gate before any arm.
6. Seal record Addendum 4 on main: step 1 (erratum path and SHA-256, `ERRATUM-3-ADMITTED-AT:
   2026-10-11T17:00:00Z`, pin scoping, the section 11 item 4 amendment), step 2 (`B5-HARVEST-PIN:` with the
   lane head, the file digests now including `joulewise/calibration_bracketing.py`, the gate record's path).
   Canonical root `pull --ff-only` with no night job loaded; desk root checked out at the pin; the pin test
   of brief 4.5 prints `HARVEST_PINNED`.
7. RUN_STATE: item 24 filled in with the pre-arm run's command; the three pins and which attempts each
   governs; `B5-ARM-RELEASED: beta gamma`.
8. Arm BETA attempt 6 by brief section 5 with the pre-arm run, t0 after 10:00 PDT on 2026-10-11 and, by
   preference, with the chain clear of 12:45 to 13:10, 00:00 and 05:15 to 06:45 local.

## Progress, 09:30 PDT (activation bab1c330)

- Step 3 done: `trigger-erratum/ERRATUM.md` is on main (merge `89b910230`), SHA-256
  `71deca18d8fbae283afe15dca4f5f36850c22f303077a859800e142577b3ac89`. Its sections 4 to 6 equal the ruling's
  section D (checked by a script, 82 lines); three wrong cross-references in the admitted text are left as
  written and explained in a reading note at the file's end (representation only).
- Step 6, first half, done: seal record Addendum 4 step 1 is on main (`ac8cc51d6`); the canonical root is
  fast-forwarded there.
- Step 4 done: the Sol seat's implementation is committed on the lane as
  `e4b4145a071871c8a3cca85c976433b89b15befd` and pushed (report
  `/Users/edr/night-archive/b5-consults/beta-a5-stale/impl/sol-impl.md`: items 0 to 8 each with tests, 497
  targeted tests OK with 29 skipped). One point it raised: item 6 gives `corpus_doubling` as a count, and
  when an evaluation is refused before an authenticated count exists the program returns null. Ruled by the
  orchestrator: null is right (item 8 types the same field `{...}|null`; no decision reads it; a zero would
  misstate missing evidence); representation only, put to the cold pass and the reviewer to confirm.
- Step 5 in flight since 09:27 PDT, all three on separate worktrees at `e4b4145a0`:
  the whole suite (`/Users/edr/night-archive/b5-consults/beta-a5-stale/suite-e4b4145a0/`, worktree
  `…-wt-harvest-trigger-suite`); the cold Fable 5.1 pass (`…/beta-a5-stale/cold-pass/charge.md`, output
  `FABLE-pass.md`, worktree `…-wt-harvest-trigger-cold`); the independent executing review by an Opus 5.5
  agent (`…/beta-a5-stale/review/REVIEW.md`, worktree `…-wt-harvest-trigger-review`), which also writes the
  working snippet for the pre-arm run. A successor that finds one of the three outputs absent relaunches
  that one from its charge; then dispositions the findings, writes `trigger-erratum/harvest-pin4-gates.md`
  and goes on at step 6's second half.

## Progress, 10:50 PDT (activation bab1c330): steps 3 to 7 are done

- Step 5: the gates passed; record `trigger-erratum/harvest-pin4-gates.md` (cold Fable 5.1 pass `PASS`;
  independent executing review `APPROVE WITH FIXES`, the three test fixes made; whole suite; rehearsal
  comparison byte-identical; the item-12 run over attempt 5's archived ledger copy: the sealed rule fails,
  the amended rule passes with row 456 recorded).
- Step 6: Addendum 4 step 2 is on main (`e3e360c68`): `B5-HARVEST-PIN: b039c0257d1b1d407ee9598222db3f78f6ad7beb`.
  The desk root is checked out there and the pin test prints `HARVEST_PINNED`.
- Step 7: RUN_STATE on main (`46f51d62c`) has items 25 to 27 and `B5-ARM-RELEASED: beta`. The pre-arm helper
  is `/Users/edr/night-plan-staging/b5-bench/b5_prearm_bracket.py` (sha256
  `5c3af0273aa6be7161bd2ef9d97d4590f011c286d100948271258049a37b7f5d`); its first run, 10:44 PDT: exit 0,
  no snapshot refusal, 14 candidates of 14 valid finalized captures, binding validated, observed and
  recorded-only trigger `new_systematic_failure_challenges_preflight_screen`, doubling 41 of 48, sequences
  `[456]`.
- Step 8 (arm BETA attempt 6) waits for a t0 at or after 13:10 PDT, so that the chain clears the 12:53 daily
  maintenance batch (RUN_STATE item 17); the arm starts about 12:35 PDT. A t0 at 11:20 was available and
  would have put the batch inside a science stage; the wait costs two hours and no measurement.
- In the wait: a Sol 6.1 seat (effort high) works on the gate owed before GAMMA (finding F3: the sealed
  verdict writer and the real provenance checker over a GAMMA-shaped window in the stale state); brief and
  report under `/Users/edr/night-archive/b5-consults/beta-a5-stale/f3-gamma/`, worktree
  `/Users/edr/code/JouleWise-wt-harvest-trigger-cold`. It is stopped before the arm whether or not it has
  finished; its report's last line says how far it got.
