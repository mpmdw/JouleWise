# Fable final pass (gate-ledger row 4): `fix/2026-10-03-g2a-w1-calibration-attach`

Head `7f3953e3`, base `3260e280`. Cold, read-only, one foreground session. Scratch only under `/tmp/adae-fable`.
The launcher script pasted after the charge was not executed (it starts a background Sol seat and a nested session, which the charge forbids).

**Verdict: PASS, with one bookkeeping condition before the re-harvest is recorded and the recovery window is armed (F7). No finding is a code defect.**

## What I ran

| Check | Result |
|---|---|
| The three named test modules | 66 tests, OK |
| `tests.test_revision_five_b_readers`, `tests.test_battery_float_sweep`, `tests.test_controller` | 81 tests, OK |
| `scripts/gen_g2_phase_d.py --check` | PASS; `NIGHT_PROGRAMMED_SPAN_S` still 17248 |
| `git diff --stat` base..head on `reduce.py`, `uncertainty_evidence.py`, `calibration_bracketing.py`, `calibration_ledger.py`, `adapters/`, `powermetrics_fiducial.py`, `configs/`, `run_night.py`, summarizer, selector, input producer | empty |
| New controller checks, predicate by predicate, on the archived real w1 data (`/tmp/a7a0/reharvest-r2`: ledger, pin, frozen plan, pre capture, 24 member configs) | every predicate true: tail past the pin is exactly one open session; session kind `bracket`; plan sha, window, plan id, evidence root match; pre slot `valid`, not an import; `validation_id`, all 5 artifact hashes and all 10 binding fields match; all 24 configs match their plan sha and run id, `repetitions == 1` |
| Same real capture with no opt-in | still refused: `revision_five evidence cannot be attached as instrument calibration` |
| Same real capture through the unchanged later checks | controller's stored-physics check passes; the reducer's attachment verifier (`reduce.py:1171`) returns no refusal, and the extra `g2a_pre_bracket` key does not disturb it |
| 14 mutations in a `/tmp` copy (each condition removed, tests re-run) | 6 killed, 8 survive (F1, F2) |
| My own scratch tests for the surviving conditions | the code refuses in every case (details in F1, F2) |

Not verifiable from here: a real member running end to end. The new attachment test replaces the bundle writer and the run itself with mocks, so the first real member of the next window is the first full exercise.

## Findings

**F1. MEDIUM, test gap, not a defect. `scripts/harvest_g2a_window.py:143-149`, `scripts/recover_calibration_ledger.py:98-101`.**
The harvest's new guards for an unclosed session are not pinned by any test. Three mutations survive `tests.test_harvest_g2a_window`: dropping the committed-pin requirement on the first load, dropping the harvest's "the tail past the pin is exactly this one open session" check, and dropping the same check in `recover_harvest_copy`. The code itself is right: with the crash fixture, an uncommitted pin and a damaged tail both end `REFUSED ledger_authentication_failed`. Add those two cases as tests in a follow-up. Not blocking, because behaviour is correct and the trial re-harvest shows the real path.

**F2. LOW, test gap. `joulewise/controller.py:538-543, 551-552, 569-575`.**
Five secondary bindings survive mutation: member-config equality (the sha check beside it still holds), slot locator equals attached directory, slot artifact hashes, `claim_eligible is False`, and the window-id environment match. My scratch tests show the code refuses a byte-identical copy at another path, a different capture, a closed session, a wrong window id and a claim-eligible plan. The second of these is the original C-2 vector (an operator naming some other Revision-5 directory), so it deserves a committed test.

**F3. LOW, wording. `joulewise/controller.py:528-529`.**
The docstring says the attachment "supplies bindings". It also supplies the bound: `b_fiducial_s` is recorded (`controller.py:508-509`) and the unchanged reducer folds it into the member's clock-anchor bound (`reduce.py:1813-1864`). See question 3 for why this is harmless here. Correct the sentence.

**F4. LOW, stale inventory. `tests/test_battery_float_sweep.py:59-62`.**
The B-reader inventory still describes the controller as "refuses Revision 5". It should name the one exception and its tests.

**F5. LOW, note. `joulewise/controller.py:515`.**
Nothing reads the new `g2a_pre_bracket` field. Keeping these bundles out of claim paths rests on registration §9 and the separate probe root, not on code.

**F6. NIT. `scripts/recover_calibration_ledger.py:104-120`.**
The read-only harvest leaves a zero-byte `terminal-ledger.jsonl.lock` in `derived/` and lists it among the outputs (visible in the trial `harvest.json`).

**F7. CONDITION, bookkeeping. `docs/process_traces/2026-10-02-design-block2/52-seal-record.md`.**
Two files pinned by registration §12 change: `scripts/harvest_g2a_window.py` is now `ac5ebd53cdc36804c2da63a91dcee69647ac452350575a6b00215e27c93d92ff` and `scripts/gen_g2_phase_d.py` is `9bc31627c0cc5da78fe8f091951979a710c069e6dcd2eb66e5a5a9e9dd202cb8`. The registration file is unchanged (`8e45a0e0…`). The seal record needs an "H′ 2" entry with these pins before the re-harvest is taken as w1's record and before the recovery window is armed. This diff does not add it.

**F8. INFO, timing. `joulewise/controller.py:555-559`.**
Each member now runs one whole-ledger custody pass before its bundle is created. w1's log shows 4.55 s for 110 observations against a 120 s budget; 24 members add about 2 minutes inside the unchanged 17,248 s span. The pass ends before the member's 75 s idle. If a pass ever exceeded 120 s the member would fail closed and the chain would stop.

**F9. INFO, carried risk.**
The trial verdict means the next window is the only recovery window (question 5). Seal disclosure D2 (no real member has yet shown a `bounded` clock anchor under the current method) is still untested, because w1 produced no member.

## The five questions

**1. Is the change correct? Yes.**
- Controller: with the variable unset, `g2a_context` is `None` and the function is byte-for-byte the old behaviour. With it set, the attachment must pass every check at `controller.py:538-576` or raise before any bundle exists. Every failure mode I could construct fails closed.
- Chain: one export, placed before the first mutation, using a variable the next existing line already reads (`gen_g2_phase_d.py:110-112`). `run_campaign.py:8384` copies the environment to the member process.
- Harvest: the first load is now against the git-committed pin. An open session is accepted only when the snapshot's refusal set is exactly {head mismatch, session open} and every row past the pin belongs to that session. A closed session takes its pin candidate from `terminal_head_pin_for_session`, which is stricter than the old "last physical row".
- `--read-only-sources`: authenticates the source, copies ledger and pin byte-exact, runs the existing abort and pin advance on the copies, then re-checks the source bytes. The trial's `terminal-ledger.jsonl` starts with the 382 source rows and adds only an append-intent row and the abort row; the pin moves 376 → 384. The abort row carries no timestamp, so a repeat harvest reproduces the same digest (confirmed on the fixture).

**2. Does it reopen the hazard C-2 closed? No.**
The hazard (`…/bfg-d/15-parser-esc-ruling-source.md:138`, `19-fix-seat-report-r6.md:83,193`): the bound of a Revision-5 *derivation* capture being used in a decision before its battery verdict, through a directory an operator names. C-2's contract (`20-fix-contract-r6b.md:9-14`) justified a blanket refusal with "Revision 5 derivation observations never bracket endpoints, so no legitimate path is lost". That premise ended when the 25G83 acceptance was issued: an ordinary bracket capture now carries the same two marks (`battery_float` key, Revision-5 epoch), and the registered window needs it attached.
- A derivation session is refused by session kind (`controller.py:562`; mutation killed).
- Any directory other than the open session's own finalized pre slot is refused.
- Without the opt-in the refusal is unchanged, shown on the real capture. The backfill reader is untouched.
- The opt-in cannot serve a claim window: the plan must say `diagnostic: true` and `claim_eligible: false`.
One thing to settle before any claim window on 25G83 gets a similar path: no code checks a battery verdict for an ordinary bracket capture before its bound is used (the "no named owner" item of `19-fix-seat-report-r6.md` F2). It does not matter here, because the bound cannot move this block's output.

**3. Does it alter a captured byte, a measured value, an estimator input, or any other admission? No, with one thing stated plainly.**
- No estimator, adapter, ledger, bracketing or config file changes. No capture is rewritten; the attachment is copied into the bundle unchanged.
- The attached bound does feed the member's reduction through the unchanged ordinary path (F3). It does not reach this block's only output: the overlap count is computed from record time spans alone (`reduce.py:196-206`), and the member's stored `clock_anchor.status` comes from its own telemetry (`controller.py:1703`).
- Admission decisions that change: the controller's refusal for G2-a members only, and the harvest accepting a governed open session (previously REFUSED). The harvest's other changes only tighten. Nothing else moves.

**4. Does any behaviour disagree with the sealed registration? No. No erratum, no cold gate.**
- §3 Chain and §12: the chain differs by one export; the span literal is unchanged. This is §11's "fix that only makes code agree with this text": §4 and §6 require members run under the pre bracket and judged by the existing bracketing decision, which reads each member's attachment, and the code at H made that impossible.
- §3 Ledger: the read-only harvest still yields `derived/terminal-ledger.jsonl` whose head equals the pin to be merged.
- §7: see question 5. §9: no acceptance rule changes. §10: the harvest prints no bound; the new fixture shares no number or hash with the real evidence (0 shared floats, 0 shared digests).
- What §12 does require is F7.

**5. Is RECOVER the registered verdict? Yes.**
- Not NULL: §7 defines NULL by `night/chain.started` being absent. It is present (chain began 01:39:06 PDT).
- RECOVER: the chain started and exited 1; the pre screen passed, stage `small-p512` began, and the first member died in 0.33 s. The causes the trial names (`bracket_incomplete`, `chain_nonzero_or_missing_exit`, `rung_valid_small_members_shortfall`) are §7's.
- It counts against the allowance: §7's "took no data" class requires no `powermetrics*.plist` in any `raw/` under `runs/`. The pre capture's `raw/powermetrics.plist` is there, so `capture_made: true` is the text's own answer, even with zero members.
- Not a re-run of w1: §7 gives one recovery window with its own plan id, session, probe root and regenerated inputs, armed after the cause is removed. If that window also ends RECOVER the block stops and goes to a consult.
- The first harvest's REFUSED was §7's tooling-fault class: fix, then re-run the harvest.

FABLE FINAL PASS: PASS
