ERRATUM: REV6-25G83-01-E1 ISSUED

# Cold erratum REV6-25G83-01-E1: the paired refuter's findings F1–F8, ruled and applied

Judge: Fable 5.1, fresh session, 2026-09-30. This one erratum settles all eight findings of the
paired Opus refuter (`23-opus-refuter.md`, sha256 `a9cd5eb57c33472401004eb892a6bff69e2514cbefdb787ac1bda921e6d9d6a7`) on the sealable Revision 6. The
refuter's verdict was CONCUR: no defect in the text can make a reported number false. I agree,
and nothing below changes a number rule other than by making a false sentence true (F1).

- Input text: `22-revision6-sealable.md`, sha256 `3fe5153fcd254a048f2462ddeaa7ff9cf591b088595f06eb07dbd70335b37bb3` (unchanged, kept for the record).
- Output text: `32-revision6-sealable-e1.md`, sha256 `9cf155fea9bb8ac8b6508bed7fa2c0765661d0e527d95c7a1b1666ccdc1bfb9c`. This is the text to seal.
- Code read at main `0009b976`.

## 0. Contamination disclosure

I opened none of RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, any memory file or any
skill file. The session harness, however, placed three things in my context before the charge,
and I could not decline them:

1. the owner's global instruction file (pointers to orchestration playbooks, and a writing
   standard for explainer prose, which I followed for the new registration text);
2. this worktree's CLAUDE.md (notes on the Codex bridge; not used);
3. the index of the memory directory: one line per entry, titles only. Those titles include
   owner-rule headlines that overlap the charge ("paper threat = hallucination, not forgery";
   "quiet windows any time"; a pause that was lifted) and several model-assignment notes.

I opened no memory entry. Every ruling below rests on the four gate files, the sealed
registration, the decision log entry D-182, cap addendum A1, and the code lines cited. No
ruling rests on anything from items 1–3.

## 1. What I read and ran

- Read in full: the sealable text (910 lines), the refuter report, the refuter's simulation,
  `scripts/prewindow_check.sh` (203 lines, sha256 `12db61a1b09a48ff828cfa6d79fa78f3fc9d997455824a68c61669224e398bd7`).
- Read in part: the ruling `21-…` (its checks and its "not established" list); A1 rules R0,
  R7–R10 (`…/20-cap-council/31-addendum-ruling.md:149–177`); the sealed A-R5b "Window verdict"
  paragraph (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:658`); D-182
  (`docs/decision_log.md:11961–11990`); `joulewise/night_gate.py:616–630, :1468, :1552–1582,
  :1840`; `scripts/run_night.py:3084–3110`; `joulewise/quiet_admission.py:1–6`;
  `scripts/issue_calibration_acceptance_generation.py:567–570, :996–1018`;
  `tests/test_preregistration_chain_digest.py:1–60`.
- Ran (scratch `/tmp/cg-rev6e1-ff50b201/`): `f1.py` (the F1 arithmetic, below), `patch.py`
  (31 exact-match replacements, each asserted to match once), `check.py` (§4). No sudo, no
  systemsetup, no powermetrics, no test suite, no write outside the two output files.

## 2. Rulings

| # | Finding | Ruling | Change in `32-…-e1.md` |
|---|---|---|---|
| F1 | §9 said Q99_within "exceeds Q99 only when the windows are more alike than chance would make them". False. | **Upheld.** I recomputed it. Q99_within is the larger exactly when F < (r² − 1)(n − K)/(K − 1), where F is the between-window mean square divided by the within-window one and r is the bound already in the text. Chance alone puts F near 1, below every such limit, so with no window effect Q99_within is the larger in about 70 % of campaigns. The direction of the rule is untouched: C can only rise, by at most r. | §9: the false sentence is replaced by a new paragraph, "Which of the two is the larger", which builds MSB, MSW and F before using them and gives the exact limit. "A few percent at most" becomes "15.7 % at n = 12 in three windows, at most 5.6 % when n is 24 or more". The three worked examples now state their F. The second invented example is relabelled "windows whose means nearly coincide". JSON: `q99_within_window.which_is_larger`. |
| F2 | The clean dwell of §6.2(g) does not run on the derivation arm path today, and the issuer had no check for start-condition evidence. | **Upheld. (g) is kept.** The dwell is the only registered load condition that holds on both gate paths (F6), and it supplies half of the 1,200 s rest that §6.2 relies on. Striking it to match today's wiring would weaken the experiment to fit the code. The text now makes a window without the dwell unissuable, so the gap cannot pass silently. | §6.2: a per-window **start-condition record** (one committed file naming the evidence file and sha256 for each of (a)–(g)). §7 issuer checks: a new refusal if any window lacks the record, an entry, a file, a matching digest, or a (g) entry showing the pinned script, exit 0 and 600 s clean. JSON: `start_condition_evidence`. Wiring is a precondition for arming C1 (§5 below). |
| F3 | R9's clause "every median frame reported" had no stop line and no count-rule outcome. | **Upheld. Ruled: a stop to review, R9 *not passed*; not a void.** A void says the cap removed a capture. A capture whose bytes are missing or fail their digest shows a storage fault; its cell count is unknown, so neither "the cap stopped it" nor "it did not" can be shown. Nothing issues and B stays unread until a review rules. A slot with no recording at all has no frame to report and does not fire the line, because such a capture never reached the estimator. | §4: the fifth clause is made exact ("every capture that has a recording") and a paragraph "When a median frame cannot be reported" is added. §7: the R9-stops sentence and a worked example. §8: a bullet. §11: the stop. JSON `stop_lines`: **STOP-R9-FRAME**, every window, adverse included. The count rule's clause 1 now catches the case before CLOSE_AND_DERIVE can be reached, which removes the undefined state. |
| F4 | A session that opens and aborts before any slot is finalized: a counting window with zero counted, or not a window? | **Upheld. Ruled: not a window** (the D-182 reading). No pulse ran and no sample exists, so the session carries no information about the cap or about B, and nothing can be selected by setting it aside. Read as a window it would fire the futility stop or silently spend one of three counting windows on a chain fault. One such session is followed by the next; two in a row go to review, as D-182 allows one successor. It must still be named at issuance, and the issuer decides from the ledger whether a session is null. | §0: **null session** defined. §7: clause [0] in the diagram, a paragraph giving the reason, the caps sentence, a worked example, two issuer checks. §11: **STOP-NULL-REPEAT**. JSON: `sessions.null_session` (definition, who decides, what it counts toward, maximum in a row), `sessions.sessions_of_this_registration`, clause 0 in `decision_order`, the stop line. Two JSON keys are renamed from "window" to "session" so that the naming duty covers null sessions. |
| F5 | §6.2(g) said "all three of these hold … the constants of prewindow_check.sh". The script blocks on five conditions and has a 45-minute limit. | **Upheld.** Confirmed at `prewindow_check.sh:72–100, :137–155, :174–203`. | §6.2(g) rewritten: the exact command (`--wait`, no `--window`), the five conditions (named daemons above 5.0 % CPU; load above 2.0; not on AC; under 20 GB free; any process line containing `codex`, `claude`, `t3`, `mcp-server`, `run_campaign` or `window-chain`), the 600 s rule, the 45-minute limit and what a timeout does, the two notes that test nothing, and what the evidence is. §5: "states its checks and constants". JSON `clean_dwell` carries all of them. |
| F6 | "The night gate repeats the load-average limit of 2.0 at t0" is true on one gate path only. | **Upheld.** `night_gate.py:1558` applies the limit only when `legacy_load` is true; `:1840` calls with it false; `run_night.py:3095–3096` sends a plan with a quiet-admission policy down that path; `quiet_admission.py:5` says "Load is diagnostic". | §6.2(g): the sentence now names both paths, glosses each, and says (g) is the registered load condition on both because the revision does not fix the path. JSON: `load_limit_at_t0_by_night_gate`. |
| F7 | §9 said a bracket's captures are "a few minutes apart (§0)". §0 does not say so, and the ruling lists it as not established. | **Upheld. Dropped, not sourced.** I found no source in the time I had. | §9, two places. The first keeps "the same window (§0)", which §0 does say. The second now ties the statement to what ρ1 measures (adjacent slots, 600 s start to start) and says plainly that the spacing of a bracket's captures is not established, with the direction of the consequence (toward none, never a reversal). |
| F8 | Q99_within needs its own recorded rule string; the sealed one says "t(p, n-1)". | **Upheld.** The sealed string is at `issue_calibration_acceptance_generation.py:567–570` and does say `t(p, n-1)`. | §9: "rule string" is glossed, and the new string is given verbatim: `prediction_p_within_window_two_draw_s = t(p, n-K) * s_within_presentation_s * sqrt(2), evaluated in binary64 and recorded as its shortest round-tripping decimal`. §12 says the sealed string goes on describing Q99 alone. JSON: `rule_string` on both values. |

**One change beyond F1–F8, forced by them.** The authority list now cites this erratum beside
the ruling, with its own digest slot. The text therefore has 20 pin slots, not 19 (15 of them
in the JSON block, as before). Nothing else was changed; `diff` of the two files shows only
the edits above.

## 3. The F1 arithmetic, so it can be redone

With SST the total sum of squares of the n member values and SSW the sum inside windows,
Q99² ∝ t(0.995, n − 1)² × SST/(n − 1) and Q99_within² ∝ t(0.995, n − K)² × SSW/(n − K).
Since SST = SSW × (1 + (K − 1)F/(n − K)), Q99_within > Q99 exactly when
F < (r² − 1)(n − K)/(K − 1), with r = √((n − 1)/(n − K)) × t(0.995, n − K)/t(0.995, n − 1).

| n | K | r | limit on F | share of no-effect campaigns in which Q99_within is larger |
|---|---|---|---|---|
| 12 | 2 | 1.0702 | 1.454 | 74.2 % |
| 12 | 3 | 1.1568 | 1.522 | 73.1 % |
| 18 | 2 | 1.0388 | 1.266 | 72.3 % |
| 18 | 3 | 1.0824 | 1.287 | 69.7 % |
| 24 | 2 | 1.0266 | 1.188 | 71.7 % |
| 24 | 3 | 1.0555 | 1.198 | 68.0 % |
| 30 | 3 | 1.0418 | 1.151 | 66.6 % |
| 36 | 2 | 1.0163 | 1.118 | 70.3 % |
| 36 | 3 | 1.0334 | 1.122 | 66.8 % |

Source: `/tmp/cg-rev6e1-ff50b201/f1.py`, seed 20260930, 20,000 campaigns of invented
independent normal data per row, equal window sizes, t quantiles from the repository's
`joulewise/analysis_engine/distributions.py`. In every one of the 180,000 campaigns the
inequality and the direct comparison agreed, and the largest simulated ratio equalled r to four
places. These match the refuter's figures (1.454, 1.188, 1.122, 1.522; 67–75 %). The worked
examples: F = 2.05 (the 12 real set-aside values), 14.6 and 0.157 (the two invented ones).

## 4. Checks re-run on `32-revision6-sealable-e1.md`

| Check | Result |
|---|---|
| Fenced `json` blocks in the file | 1 |
| The block parses | yes; 8 stop lines; clauses 0–6 |
| Issuer's pin reader `preregistration_epoch_pins` on Revisions 1–5 with this text appended | returns (`25G83`, `b762e5bf…330c5`); `os_build` pattern 1 match; powermetrics pattern 1 match |
| Chain-pin regex `\bchain digest\s+([0-9a-f]{64})\b` on the same | 1 match |
| Revision 3 line regex on the same | 1 match |
| "# Revision 5 (" occurrences | 1 |
| Pin slots (the §13 grep) | 20, of which 15 in the JSON block |
| Set-aside identifiers in the JSON | 12, all distinct, untouched by the patch |

## 5. Notes for the lead (not registration text)

1. **Before C1 is armed, the dwell must be wired.** The derivation driver must run
   `scripts/prewindow_check.sh --wait` before t0, refuse to start on a non-zero exit, and save
   the output, exit status and times as the (g) evidence. It must also write the per-window
   start-condition record. Until then the issuer check added under F2 refuses every window,
   which is the intended fail-closed behaviour.
2. **The wiring hazard the refuter named is real.** The script's eighth check blocks when any
   line of `ps aux` contains `codex`, `claude`, `t3`, `mcp-server`, `run_campaign` or
   `window-chain`. It matches anywhere in the line, including paths and arguments, and it does
   not exempt the driver. Two things to test on the real launch: that the driver's own process
   line and its children's (paths included, for example a home directory holding `.claude`)
   match none of the six strings, and that no ordinary system process does (`t3` is two
   characters and can match by accident). A false match cannot make a number false; it makes
   the dwell time out after 45 minutes and the window not start. If the script has to change,
   change it **before** the seal: its digest is a pin, and the registration's description in
   §6.2(g) and the JSON must be corrected to match in the same edit.
3. **WI-13 must implement**: null-session detection from the ledger; clause 0; STOP-R9-FRAME;
   STOP-NULL-REPEAT; the start-condition record check; the new rule string for Q99_within. The
   validator's exact-equation check of C (ruling V3) still has to learn the fourth term, as the
   ruling already said.
4. The seal now fills 20 slots, one of them this file's sha256.

## 6. Not verified, stated plainly

- NOT EXECUTED: the issuer, the validator, the night gate, the chain, the dwell script, any
  test suite, any capture. My statements about their behaviour come from reading the lines
  cited, except the pin reader and the regexes, which I ran.
- NOT VERIFIED: the exact ledger field that records a capture's raw-bytes digest, and the
  exact ledger state of a slot after a session abort with no capture. The text defines
  "has a recording" and "null session" in words ("a finalized ledger row that records a digest
  for the raw sampler bytes"; "no slot has a finalized ledger row"), following the sealed
  A-R5b wording. WI-13 must map those words to fields and should return to review if the
  ledger cannot tell the cases apart.
- NOT VERIFIED: the refuter's statement that the derivation path never calls the dwell
  script, beyond one search that found it referenced only by `scripts/capture_t0_step.py`,
  `joulewise/arm_readiness_evidence_t0.py` and `joulewise/arm_readiness.py`. The ruling
  holds either way: the issuer check makes the evidence mandatory.
- NOT ESTABLISHED: how far apart a claim bracket's two captures are (F7). The text now says so.
- The refuter's other simulation rows (serial dependence, unequal spread) were not re-run;
  none of them is cited by the corrected text.

## 7. Summary

1. All eight refuter findings are upheld and settled in this one erratum; the corrected text is `32-revision6-sealable-e1.md`, it parses, and the issuer's pin reader and the chain-pin regex each still match exactly once.
2. Decisions made: a capture whose median frame cannot be reported stops the campaign for review without voiding it; a session that aborts before any capture is not a window (two in a row go to review); the clean dwell stays, and the issuer now refuses any window without its start-condition evidence.
3. One thing must happen before window C1 is armed: wire the dwell script into the derivation driver and test that its process-name check does not match the driver itself.
