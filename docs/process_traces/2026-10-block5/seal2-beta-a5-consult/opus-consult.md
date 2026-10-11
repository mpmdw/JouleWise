# Seat report (Opus 5.5, blind): BETA attempts 4 and 5 and the stale calibration acceptance

Written 2026-10-11. Read-only. I opened no file of this directory but the brief. Of window products I read only
`harvest.json` (the permitted fields), `night/hazard_result.json`, attempt 3's contention journal, and the
calibration ledger. I ran the pinned bracket evaluation over the ledger with a program that printed status
words, reason codes, counts and calibration bounds only. Nothing was written but this file.

Paths used below:

- CLONE = `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18` (HEAD `a9b11f40c`, the pin-only commit for sequence 478)
- DESK = `/Users/edr/night-custody/desk/b5-harvest` (HEAD `0699abbb0`)
- REG = `CLONE/configs/campaigns/v5_claim_25g83/registration_block5.md`
- PREREG = `CLONE/configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
- BRK = `DESK/joulewise/calibration_bracketing.py`
- SEALREC = `/Users/edr/code/JouleWise/docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`

## Short answer

The lead's reading is right. One ledger row, sequence 456, makes every later bracket fail, and nothing in
attempt 4 or 5 contributes. I disagree with the brief on what comes next. The registered cure ("derive a new
acceptance") is not a desk task and not a one-day task: it needs a new calibration pre-registration revision,
at least two derivation windows, an issuance, a third seal, a new clone and a restart at ALPHA, and it would
go stale again by the same mechanism within a few windows. The shortest lawful route is a prospective cold
erratum that changes what the trigger does to later windows, implemented in the harvest's desk checkout only,
on the pattern of Erratum 2. Attempts 4 and 5 stay not claim-usable on either route.

## 1. Is the lead's reading right?

**Which program decides.** `evaluate_calibration_bracket` (BRK:2103). The harvest reaches it from
`_Harvest.calibration` (`DESK/joulewise/b5/harvest.py:4588`, through `calibration_bracket_for_bundles`,
BRK:2770) and emits `calibration.bracket_acceptance_failed` when the status is not `passed` or any reason is
returned (harvest.py:4595-4597). The catalog makes that code window-removing.

**From which rows.** BRK:2500-2530 builds `new_observations`: every live (not historically imported) ledger
observation whose content id is not in the acceptance's `prior_observation_set`, that is, every capture
recorded after the cutoff, sequence 376. BRK:2577-2584 appends
`new_systematic_failure_challenges_preflight_screen` if any of them has disposition `systematic-invalid` in a
judged epoch. BRK:2589-2602 then returns at once with freshness `stale`, reason
`prospective_rederivation_required`, and bracket reason `calibration_acceptance_bound_stale`. That return is
before the endpoints are selected (BRK:2603 onward), which is why `acceptance.drift` is null. The code comment
at BRK:2585-2588 says this is intended: a pre capture of an aborted session stales the acceptance for windows
it does not bracket.

**Is sequence 456 the trigger?** Yes, and it is the only one. Among the 18 captures finalized after
sequence 376 the ledger holds 17 `valid` and one `systematic-invalid`: sequence 456, pre slot of session
`v5-b5-beta-a3-20261010T2151Z-calibration`, bound 0.04437677892168357 s (44.38 ms) against a pre screen of
36.46 ms. The session was aborted at sequence 458 with reason `pre_capture_systematic-invalid`.

**Any other trigger?** No. I ran the pinned code (DESK at `0699abbb0`, the clone's interpreter, `-B`) on the
live ledger at pin 478 for a hypothetical window starting now. It printed: snapshot valid, no refusals;
status `failed`; reasons `calibration_acceptance_bound_stale`; `observed_triggers`
`["new_systematic_failure_challenges_preflight_screen"]` and nothing else. Checked one by one:

- Range expansion (BRK:2562-2576): the 17 new valid bounds run from 25.26 to 31.86 ms, inside the corpus
  range 21.93 to 36.46 ms. Not fired.
- Corpus doubling (BRK:2544-2554): 41 valid captures of the judged epoch are counted (64 valid, less 23 set
  aside by the two decisions the acceptance names); the threshold is 48. Not fired, but see section 5: seven
  more valid captures fire it.
- Protocol or estimator bytes (BRK:2494-2499) and identity (`stale_fields` empty): not fired.

**Do attempts 4 or 5 contribute?** No. Their four captures (sequences 464, 468, 474, 478) are valid with
bounds 31.41, 31.86, 27.55 and 29.48 ms. Their only effect on the acceptance is to raise the doubling count.

**GAMMA today?** Stale. The probe above is exactly that case: any window of any pack whose harvest reads a
ledger containing row 456 fails the same way. REG:2507-2508 says so in words: "The capture that fired the
trigger stays in the ledger, so every later window's bracket fails the same way until a new acceptance is
issued."

**An ALPHA re-harvest today?** Not stale, if it is run as the magistrate brief requires. The harvest judges
through the window's own terminal pin (harvest.py:4452-4474). I loaded the snapshot four ways:

| Window | Ledger given | Refusals | Post-cutoff systematic rows seen |
|---|---|---|---|
| ALPHA a1 (second seal) | its archived copy, 432 rows | none | none |
| ALPHA a1 (second seal) | live ledger, 478 rows | `calibration_ledger_head_mismatch` | 456 |
| BETA a1 | its archived copy, 442 rows | none | none |
| BETA a1 | live ledger | `calibration_ledger_head_mismatch` | 456 |

So with `--ledger-path` and `--head-pin-path` pointing at the first archive's copies (magistrate brief section 4,
rule HN-1, lines 366-373) ALPHA reads fresh. Given the live ledger it is removed for a different reason (head
mismatch), not for staleness. One open point I could not close: the analysis (the claim consumer) also lists
`calibration_acceptance_bound_stale` as a refusal (`DESK/joulewise/analysis_engine/claims.py:64`) and the desk
`whole_window.py:5551` re-evaluates brackets. If the analysis re-evaluates ALPHA's bracket against the live
ledger at release time, ALPHA attempt 1 would read stale or mismatched too. Whoever builds the cure should
confirm which ledger the claim consumer reads.

**Three refinements to the lead's account.**

1. The outcome is the registered rule, not a surprise of the code. REG:2482-2511 states the trigger, the
   cascade, and that "No program" stops the next arm: "The lead reads the reasons in the harvest's flag
   (structure, no energy), arms no further window, and takes the question of a new acceptance to a cold gate."
2. Attempt 3's own harvest could not show it. A session that was never finalized returns at
   `calibration.no_bracket` (harvest.py:4502-4505) before the bracket evaluation runs. The first harvest that
   could show the stale reason was attempt 4's, and `harvest.json` carries only the flag code, not the reason.
3. Attempt 4 would have been removed with or without the sleep. The 2026-10-10 consult's cause was wrong for
   this reason code.

## 2. What the registered rule requires next

**What the texts say a re-derivation is.**

- REG:2482-2485: after a trigger "a new acceptance must be derived before any further bracket is judged"; the
  rule is `judge_under_prior_artifact_never_self_fit`. REG:2510-2511 sends the question to a cold gate. The
  block-5 registration defines no procedure.
- PREREG:253-259 (Revision 1, "Prospective use"): the new acceptance "judges only subsequent ordinary
  captures"; derivation captures are corpus members and never bracket endpoints; the new cutoff is the ledger
  head after the last derivation row; "a trigger observation is judged under the PRIOR artifact, never
  incorporated into a threshold that judges itself."
- PREREG:668-669 (Revision 6): "It governs only the windows it declares." A new derivation therefore needs a
  new sealed revision, with its cold registration gate. PREREG:1711-1713 says the same of any fix in the
  derivation path.
- Which captures enter: only captures of the new revision's own derivation-kind sessions (PREREG:1484-1489).
  No bracket capture is a member: not row 456, not the 17 valid block-3 and block-5 captures.
- How many: one window is one derivation session of 12 slots at a 600 s pitch, programmed span 7,680 s
  (PREREG:1027-1038). The count rule closes at 24 counted captures and 12 members (PREREG:1151-1174), so at
  least two windows, at most three plus one replacement. Block 1 took two (24 of 24).
- Which program: `scripts/issue_calibration_acceptance_generation.py`. It refuses while valid same-epoch rows
  exist outside the registration (`_foreign_rows`, lines 2113-2125; refusal at 1774-1775). The 17 valid bracket
  captures are such rows, so issuance also needs a new disposing decision in the disposition registry, or an
  issuer change. I read this; I did not run the issuer.
- Which files change, all of them in the clone a window reads: a new
  `configs/calibration/calibration_acceptance_d079_v2_n<N>_25g83_r3.json`; BRK:156-232 (the registry, the pinned
  SHA-256, `ACTIVE_ACCEPTANCE_ID`, `DEFAULT_ACCEPTANCE_BOUND_PATH`) and BRK:442-459 (the generation row); the
  disposition registry; the three packs' plan trees, which pin the acceptance's SHA-256 (harvest.py:4435-4443);
  `identity_pins.json`, which records the plan-tree digests; then the sealed inventory and the seal documents.

**Which of (a), (b), (c).**

- The registered cure as written is (c), and more than (c). The acceptance and BRK are window inputs
  (REG:5409: everything under `joulewise/` and `configs/`). BRK is imported in-window by the pre-capture
  classifier (`CLONE/scripts/validate_powermetrics_fiducial.py:503-541`) and ALPHA attempt 1 executed it. REG
  4801-4803: a cure touching collection code that a completed window executed "supersedes the whole block ...
  and the block restarts at ALPHA". REG:4779-4781 adds that all three windows must share one acceptance. So a
  re-derivation costs ALPHA's claim-usable window.
- It cannot be (a). Desk work alone cannot change a registered rule (REG:2600, REG:5144-5145).
- The shortest lawful route is (b): a prospective cold erratum to REG 4.6 item 2, which REG:2600 expressly
  allows ("A change to any item after the seal needs a prospective cold erratum before the next arm"). Its
  code change is to a desk program only. REG:4777-4779 covers that case in terms: a desk program's change
  "changes no collection code even when the file it changes is also imported inside a window from the
  measurement checkout". No new seal, no new clone. Erratum 2 is the precedent: SEALREC, Addendum 3 (lines
  478-534), a cold-gated erratum that changed only the harvest program, scoped to attempts whose plan
  `t0_epoch_s` is later than the admission time, with the registration's bytes unedited.

**Route B (recommended): Erratum 3, desk only.**

| Step | What | Where the file lives | Gate |
|---|---|---|---|
| 1 | This two-seat consult settles the science question (section 3). If the seats disagree, one cold Fable judge. | records | two-seat council |
| 2 | Write Erratum 3 (text in section 3). Records: `docs/process_traces/2026-10-block5/<name>/ERRATUM.md`, `REFUTATION.md`, `RULING.md`. | main, records only | prospective cold erratum: one judge (Fable, cold), one refuter (REG:5144-5145) |
| 3 | Harvest lane, cut from `0699abbb0`: change `joulewise/calibration_bracketing.py` (BRK:2553-2554, 2573-2576, 2577-2602, 2709-2728) so the three observation triggers are recorded and do not fail the bracket; `joulewise/b5/harvest.py` writes the observed trigger names into `harvest.json`; tests. | DESK only. Never committed, merged, pulled or checked out in CLONE (REG:5312-5316) | merge ledger for number-bearing code: independent executing review, whole suite on the lane's tree, cold Fable final pass, findings dispositioned |
| 4 | Executing check on real bytes: run old and new programs over attempt 5's preserved bytes into a scratch archive; print verdict, `claim_usable` and reason codes only. Labelled exploratory; changes no record. | scratch | part of step 3's review |
| 5 | SEALREC Addendum 4: `ERRATUM-3-ADMITTED-AT`, the new `B5-HARVEST-PIN`, the file list with SHA-256s (now including `calibration_bracketing.py`), written by a seat that has read no claim-window energy. | main, records only | light tier (the Addendum 3 pattern) |
| 6 | Add the freshness probe of section 6 to the arming steps; update the magistrate brief. | records | light tier |
| 7 | Arm BETA attempt 6 from CLONE unchanged (its next commit is the usual pin-only commit). | CLONE: pin only | arm notice; no new pre-arm triple audit, because no frozen window code changed |

Do not add a flag code: the flag catalog is a sealed window input that the harvest reads from the clone, and
a new code would be unclassified until a catalog erratum. A field in `harvest.json` is enough.

Two things the builder must confirm, because I could not open the files that show them. First, the stored
whole-window verdict is written by the clone's sealed `run_campaign.py` (REG:5333-5336), so on every governed
window it will go on reading failed with `calibration_acceptance_bound_stale`. That surfaces as
`whole_window.not_passed`, which the catalog only discloses, and attempts 4 and 5 show it removes nothing by
itself: each has exactly one window reason. The erratum should say this in words. Second, step 4 must show
that nothing downstream of a passing bracket (member checks that need the operative bound, the cell minimum,
the claim consumer) behaves differently from a window that was fresh.

Estimate: 6 to 10 hours of wall clock to an armable attempt 6 (Erratum 2 went from BETA attempt 1's harvest to
the arm of attempt 2 in about ten hours). Zero measurement hours before the arm. The window itself is about
5.7 hours (attempt 5: t0 00:39, post capture 06:22).

**Route C (the registered cure), for comparison.** PREREG Revision 7 and its cold registration gate; two or
three derivation windows, about 2.5 hours each with dwell (5 to 7.5 measurement hours); blind checks; a
disposing decision for the 17 foreign rows; issuance and its gates; the registry and pack changes; third seal
(new H_claim, seal commit, record, Erratum to SEALREC); the pre-arm triple audit, which a frozen code change
does require; a new clone; then ALPHA again (5.7 hours) before BETA can arm. The second seal took about 16
hours without any calibration campaign. I estimate two to three days and 11 to 13 measurement hours before
BETA attempt 6. And the new acceptance has the same five triggers, so it goes stale again as described in
section 5.

## 3. Is the trigger rule proportionate?

**The evidence is real; the remedy is not proportionate.** Keep the two apart.

*The evidence.* Row 456 is not a marginal exceedance. It is 44.38 ms: 7.9 ms above the screen, and about 4.3
standard deviations above the corpus (the thresholds audit gives median 27.9 ms, sd 3.8 ms, line 53). It is
above the 42.6 ms line the same audit named as the edge of "the ordinary tail" (lines 133-136, 232). The
other 41 captures of this epoch (24 corpus, 17 later) top out at 36.46 ms. The contention journal for the
capture's minutes is clean: 28 intervals, every one `clean`, outside CPU at or below 0.26 CPU-seconds per
second until the capture had ended, which is no worse than the first 28 intervals of attempts 4 and 5. The
capture 46 minutes later (sequence 464) read 31.41 ms. So the instrument's alignment error did sit near 44 ms
for some minutes, for no cause the monitor saw, and came back. That is a fact about the instrument and it
deserves a re-derivation.

*What it threatens.* Not a point estimate. A window's timing bound is max(pre, post) + max(|post − pre|,
14.531 ms) (BRK:2749-2750), and it sets the attribution floor printed beside a cell. The question row 456
raises is whether the 14.531 ms padding covers an excursion between the two bracket captures. For attempt 5
the bound would have been 29.48 + 14.531 = 44.01 ms, 0.37 ms short of 44.38; for attempt 4, 46.39 ms, which
covers it. By the audit's figure (1 ms adds 0.047 J to a 2.1 J floor on a 26.1 J prefill, line 76; not
re-derived by me) the shortfall is of order 0.02 J on a floor that is labelled, never added into an interval.

*Why the remedy is wrong.* Removing every later window protects nothing that the later window's own
measurements do not already protect or that a wider printed bound would not protect better:

- The level question (is the alignment normal now?) is measured directly by each window's own pre capture
  against the same screen. An earlier session's capture is a proxy for it.
- The excursion question is a statement about the padding. It is answered by printing the floor under a wider
  bound, not by discarding the window.
- The rule was certain to fire. The screen is the sample maximum of 24, and any valid capture outside the
  24's range is also a trigger (REG:2493-2496). For exchangeable captures, the chance that 18 new captures all
  fall inside the old range is (24 × 23)/(42 × 41) = 32%. So there was about a two-in-three chance that block 5
  would be stale by now with nothing wrong, and the doubling rule makes it certain within seven more captures.
  The rule was written for a regime of three windows on three nights, not for back-to-back windows.

**Must be done now (Erratum 3).** For attempts whose t0 is after the admission time:

1. The three triggers that range over the whole ledger are recorded and do not fail a bracket:
   `new_systematic_failure_challenges_preflight_screen` when raised by a capture of another session,
   `new_valid_same_identity_capture_expands_observed_range`, and `corpus_doubles_from_24_to_48`. The harvest
   writes the names it observed into `harvest.json`.
2. Everything that judges the window's own evidence stays as sealed: its own pre above the pre screen
   (chain exit 12, `calibration.no_bracket`; BRK:2697-2707), its own drift above 15.502 ms (BRK:2746-2747),
   identity change, protocol or estimator byte change, missing, old or invalid endpoints, ledger integrity.
3. The analysis prints, beside every floor of a window that carries an observed trigger, the same floor under
   the wider bound max(operative bound, largest bound of any capture with valid evidence in the judged epoch),
   today 44.38 ms. This is the conservative replacement for what the trigger protected, and it is a number, so
   it goes through the same erratum and the analysis lane's pin before the release event.
4. A re-derivation becomes due before any later block is sealed, not before the next window.

Gate: this consult, then the prospective cold erratum. If the judge prefers a stricter item 3 (for example
adding the wider bound into the reported floor instead of printing it beside), that is a settled-in-one-erratum
choice and does not change the route.

**What I would improve later, not now.** Each needs a new seal because it changes window code, so it belongs
to the next block's registration: a screen with stated coverage instead of the sample maximum (the audit's
two-line proposal: an exceedance widens the bound and is disclosed, a much higher line stops the chain); a
midpoint calibration capture, which would measure an in-window excursion directly instead of padding for it;
and a doubling rule that schedules a re-derivation without failing brackets.

## 4. Status of attempts 4 and 5

They stay collected, not claim-usable, kept and disclosed, their energies never analysed. No lawful re-harvest
changes that.

- REG:4696-4702 allows a re-harvest to change `claim_usable` only "with a repaired program (§7.1, §11 item
  4)". The program was not defective: it applied REG:2507-2508 as written.
- "Prospective" is defined at REG:567: made before the bytes it governs exist. REG:5144: no change "for an
  armed or completed attempt".
- Under a re-derived acceptance the answer is the same: it "judges only subsequent ordinary captures"
  (PREREG:253), and attempts 4 and 5's captures precede it.
- The Erratum 2 precedent already fixes the form (SEALREC, Addendum 3 step 1): an attempt armed before the
  admission time is never harvested by the new program for a deciding record; a run over it is exploratory,
  labelled, and changes no verdict.
- It also keeps re-arming clean of selection. Attempt 5's yield is already known; admitting it afterwards by a
  rule written after its harvest would be a choice made with outcomes in hand.

Attempt 4 has the sleep as a second objection. Attempt 5 has none that I can see from the released records,
and it should be recorded that way in the attempt history: lost to the registered rule, not to its own span.

## 5. What else the next arm should carry

1. **The doubling count.** 41 of 48. Each completed window adds 2, each aborted attempt with a valid pre adds 1.
   Three more complete windows fit; the fourth fails by `corpus_doubles_from_24_to_48`. Erratum 3 item 1 must
   cover it or the block is stale again after GAMMA plus one retry.
2. **Range expansion.** About 8% per capture, by construction. Same cure, same erratum.
3. **A pre capture above the screen** will still stop a chain about 1 time in 25. After Erratum 3 that costs
   ten minutes and a re-arm, with no cascade. Leave the in-window screen alone; changing it is a new seal.
4. **The reasons should be in `harvest.json`.** Bracket reason codes and observed trigger names are structure.
   Their absence is why attempt 4's cause was misread. Same lane as step 3; a representation change.
5. **Sleep left no window reason on attempt 4.** Its only window reason is the calibration one. Before the
   bracket stops masking other causes, confirm by a count-only program that members spanning a sleep carry a
   member exclusion. If they do not, that is a physics gap and needs its own flag before attempt 6 is trusted.
6. **Attempt 5's last science stage** lost 6 of 20 (`yield_low`, flag `yield.stage_low`; no
   `stage.members_refused_pre_bundle_identical`, so the process rule of REG:4725-4734 does not hold the arm).
   Six failures in one stage is still a cluster. Print the failed members' status reason codes, structure only,
   before arming.
7. **Re-harvests** of any window that is no longer the newest in the ledger take the archived ledger and pin
   (section 1's table).

## 6. Could this have been seen earlier?

Yes, from the moment attempt 3's session was aborted, and by the registered rule the lead was to stop arming
then (REG:2509-2511). Two attempts, about twelve measurement hours, were spent after it.

The check, run at the desk before the arm's quiet dwell (it took a little over two minutes here, because
candidate discovery reads every capture):

```python
# run with CLONE/.venv/bin/python -B, PYTHONPATH=DESK
from joulewise import calibration_bracketing as B
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
acc = B.load_calibration_acceptance_bound(CLONE / "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json")
cut = acc["ledger_cutoff"]
snap = load_calibration_ledger_snapshot(
    CLONE / "runs/calibration_observation_ledger.jsonl",
    CLONE / "configs/calibration/calibration_ledger_head.json",
    require_committed_pin=False, verify_custody=False, mode="issuing", repo_root=CLONE,
    baseline_sequence=cut["sequence"], baseline_digest=cut["head_digest"])
cands = B.discover_calibration_candidates(snap, mode="issuing")
res, reasons = B.evaluate_calibration_bracket(
    cands, window_start_s=now, window_end_s=now + 1, bindings=cands[-1].bindings,
    policy=<the pack policy's calibration_bracketing>, ledger_snapshot=snap)
```

Read `snap.refusal_reasons` (must be empty), `res["acceptance"]["freshness"]["status"]` and
`res["acceptance"]["prospective_rederivation"]["observed_triggers"]` (must be empty). A fresh acceptance ends
with a reason about the missing bracket of the hypothetical window (`instrument_calibration_stale` or
`instrument_calibration_bracket_missing`), which is expected. Note that the early return at BRK:2589-2602
lists only the systematic trigger under `stale_triggers`; read `observed_triggers` for the others. Print the
doubling count beside it (valid captures of the judged epoch not set aside, BRK:2544-2552) and require count
+ 2 < 48 until Erratum 3 is in force. After Erratum 3 the same call, run from the new desk pin, reports the
triggers as recorded and the arm goes ahead.

A one-line version that needs no code: any `bracket-session-slot-finalization` row after sequence 376 with
disposition `systematic-invalid` means stop and consult.

## What I did not verify

- Whether a passing bracket changes any member-level or cell-level outcome in the harvest (step 4 tests it).
- Which ledger the claim consumer reads when it re-evaluates a bracket at analysis time.
- The issuer's behaviour on the 17 foreign rows (read, not run).
- The audit's joule figures.
- Why row 456 read 44 ms. The monitor shows no contention; I looked at nothing else.

RECOMMENDATION: cause = ledger row 456 (BETA attempt 3's pre capture, 44.38 ms, class systematic-invalid) fires the registered trigger new_systematic_failure_challenges_preflight_screen, which by REG 4.6 item 2 fails every later bracket whatever the later window does; attempts 4 and 5 contributed nothing ; cure before the next arm = Erratum 3, prospective, desk only: the three whole-ledger triggers (systematic capture of another session, range expansion, corpus doubling at 48, now 41) are recorded in harvest.json and no longer fail a bracket, a window's own pre screen, drift ceiling, identity and byte checks stay, the analysis prints each floor also under the widest observed capture bound (44.38 ms), re-derivation falls due before the next block's seal; code change in the desk harvest checkout only (joulewise/calibration_bracketing.py, joulewise/b5/harvest.py, cut from 0699abbb0), measurement clone unchanged, plus the pre-arm freshness probe ; gates = this two-seat consult (cold Fable judge only if the seats disagree), then a prospective cold erratum with one judge and one refuter, then the harvest lane's merge ledger with an executing review, the whole suite and a cold Fable pass, then seal-record Addendum 4 pinning the new harvest commit, no new seal and no pre-arm triple audit; the registered alternative (new acceptance) needs a new calibration pre-registration revision, two or three derivation windows, a third seal, a new clone and a restart at ALPHA ; attempts 4 and 5 = collected, not claim-usable, kept and disclosed, energies never analysed, no re-harvest changes that (attempt 4 also slept; attempt 5 has no physical objection on the released records)
