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
