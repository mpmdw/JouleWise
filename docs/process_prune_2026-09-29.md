# Process prune, 2026-09-29

**Authority.** Ed, 2026-09-29: "yes, obviously i cosign fixing all this ridiculous overengineering", including thinning the twelve-row merge ledger (D-118) and the four-model councils (D-184). His decision of the same day ("Gates are anti-spiral, never a bar on refinement; network time stays OFF; the 09-29 team") lands in the decision log with the 2026-09-29 records PR.

**Evidence.** Two independent read-only sweeps, one per model, in `docs/process_traces/2026-09-29-interactive-ff50b201/80-prune/` (landing with the same records PR): `20-process-sonnet.md` (40 mechanisms) and `21-process-opus.md` (27 mechanisms). Each asked of every rule: which number does it protect, and what has it caught? Their headline: from 09-22 to 09-29, about 82% of commits and 87% of changed lines were records, rulings and bookkeeping; 116 cold rulings were written, 39 of them errata or addenda of earlier ones; no calibration was issued and no published number changed.

## What changed

1. **Merge ledger: twelve rows to six keys** (`.github/pull_request_template.md`, `scripts/check_gate_ledger.py`). The keys: (1) independent review by a non-author with a lens that runs the code; (2) the whole test suite on the merged tree; (3) CI green on the final head; (4) a cold final pass on merge code that touches measurement, calibration or claims; (5) every finding dispositioned (fixed, deferred to a named lane, or rejected with a reason), with no counting of fix rounds; (6) the Impact statement. Why: 18 of 40 full ledgers pointed all twelve rows at one file, and the "prune" row had no traceable catch (Sonnet rows 8 and 14).
2. **Light tier** (docs, records, tests): Impact statement, CI, and the whole suite when tests changed. No audit rounds. Why: one records-only PR took 26.7 hours and three audit rounds, and none of its findings touched a number (Sonnet row 15; Opus row 8). The checker now refuses a light tier whose Impact statement answers Yes to any line, so a PR that can change a number cannot slip into the light tier.
3. **Cold gates only for** registrations, claim-bearing results, irreversible acts (deleting evidence, committing a measurement window, publishing) and choices Ed reserved. A ruling and its refuter that disagree settle in one erratum. Why: many of the week's cold rulings judged the process's own machinery, and 39 of 116 were follow-ons to earlier rulings (Opus rows 4-5).
4. **No fixed round caps.** "Same defect twice in a row, then a consult" stays; every round limit names where the question goes. Why: "stops for good" wording idled a lane for about a day (Sonnet row 19; Opus row 2).
5. **Councils:** two blind seats from different model families; a cold judge only when they disagree on a science question; four models only when Ed asks. Why: seats often agreed, and the week's one high-yield council catch came from a single seat (Opus row 6).
6. **Records:** one running record per session, one `RUN_STATE.md` top block per session, nothing written by a relaunch that has nothing to do, verbatim quotes for Ed's words only. Why: 16 of 28 activation records were 31 lines or shorter (Sonnet row 24).
7. **Emails only on a change of state** (`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`): arm, stand-down, a question, a verdict, a fault. Why: about 45 launch emails a week (estimate) protected no number (Opus row 16).
8. **Forger seats retired** (deliberate-adversary review): the one composed forgery they produced was already refused by a replay check (Opus row 24); D-161 already retires deliberate-only guards.
9. **Writing standard** (explainer pedagogy) scoped to the paper and owner-facing prose; internal records get no pedagogy pass (Sonnet row 23; Opus row 10).
10. **Dead pruning rules replaced by one live rule.** The two-sessions drop, the per-layer yield tally, the standing sweep cadence, the spend guardrails and the post-workload reassessment were written and never applied. The replacement: at each session's end the orchestrator lists each gate or check that ran and what it caught that touched a number; any mechanism with no such catch in its last three sessions is proposed to Ed for deletion.

## What stays, and why

- The arm notice with Ed's NO, the STOP file, and the stand-down fence: they keep agents off the machine during a capture.
- The pre-arm triple audit (GitHub issue #416): it re-derives the calibration from raw files before any claim run.
- The cold science gate's re-derivation of a calibration from raw bytes.
- The Impact statement, which routes number-changing PRs to the full tier.
- Write-scope fences on the pinned estimator files.
- The whole suite on the merged tree: it found 115 failures and 418 errors on one integration tree after every lens and the final pass had said merge (Sonnet row 9).

## Not changed here

- The cold-gate charter's bytes are hash-pinned and Ed-ratified; a note in `docs/process/coldgate_charter_registry.md` records that its §3 trigger list no longer decides when a gate is convened.
- Skills outside the repository and Ed's private doctrine file are the orchestrator's to update.
