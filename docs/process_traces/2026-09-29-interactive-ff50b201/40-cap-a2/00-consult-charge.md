# Consult CAP-COUNCIL-25G83-01-A2: the cap plan after the owner's D-138 choice (a)

You are one of several independent consult seats (Sol 6.1, Astra, Opus 5.5); a cold Fable judge rules afterwards on all seats' answers. Answer independently: do not read other seats' files in this directory. Single non-interactive session, foreground only, no subagents or background tasks. READ-ONLY: modify no repository file; write only your answer file (path given in your launch line) and scratch under `/tmp/cap-a2-ff50b201/<your-seat>/`. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. Plain language: define each term at first use. You have explicit licence to disagree with every premise below, including the owner brief's.

## Background (each fact is checkable; check the ones your answer rests on)

- **What the estimator cap is.** Records root: `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/`. The cap council ruling `20-cap-council/21-coldgate-fable-ruling.md` and its addendum A1 `20-cap-council/31-addendum-ruling.md` chose route R: freeze the estimator code, size the 165k-cell cap from ≥ 24 non-claim captures under a pre-registered rule, then re-issue the 25G83 calibration (an interim "same 12 values" re-issue, then a successor), then the full audit; a claim hold ("H1": no claim-bearing window at build 25G83) lifts at step 16.
- **The owner's choice (Ed, 2026-09-29, "definitely a").** D-138 option (a): the issued 25G83 calibration file `d079_calibration_acceptance_v2_n12_25g83_r1` ("r1", candidate bytes dbad7cc7…) is NOT registered in code now; the build-keyed hold code is dropped; only the disposition-registry loader repair and the promotion tool land. R7 (the 25F84 file) stays the only registered default. Brief: `12-hold-consult/40-owner-brief-2026-09-29.md`.
- **The investigation that prompted this consult:** `/Users/edr/code/JouleWise-wt-bk-ff50b201/docs/process_traces/2026-09-29-interactive-ff50b201/30-r1-need/10-sonnet-r1-need-report.md` (read in full). Its findings: (1) after the cap code change, R7's recorded estimator pins go stale (`scripts/validate_powermetrics_fiducial.py:397-402` on main), so derivation windows need a pin-only re-issue of R7 at 25F84 ("R8") as the default; (2) A1 §5 step 1 and row S6 require r1's issuance first and forbid re-pinning another epoch's file; (3) the cap plan registers 25G83 files (interim at step 9, successor at step 12) before H1 lifts at step 16, so the hold problem the refuters found returns there; (4) the interim's production tool is undecided.
- **Why the hold kept failing:** HOLD-BY-CONSTRUCTION-01 (`12-hold-consult/21-coldgate-fable-ruling.md`, esp. §6.2 and §8); three refuter rounds each found a new route while a 25G83 file was registered.
- Code: main is `9eab16f8` (checkout `/Users/edr/code/JouleWise`; use `git -C /Users/edr/code/JouleWise show origin/main:<path>`).

## Questions

1. **Default during the cap windows.** Is a pin-only R7→R8 re-issue at 25F84 the right default while the cap evidence is gathered? Is it scientifically neutral (same 12 members, same values, only code pins change)? What must it carry and what must be checked for it to be admissible? Is there a better route?
2. **Amending A1 step 1 and S6.** Give the exact amended text you would issue, consistent with the owner's choice (a).
3. **The interim re-issue.** Keep it, or drop it in favour of R8 (for windows) plus the successor only? What scientific job did the interim do, and is anything lost without it?
4. **The hold.** If any 25G83 file is registered before H1 lifts, what enforces H1? Options include: re-sequence so no 25G83 file is registered until the closing ruling (register the successor and lift H1 in one transaction); a build-keyed hold as its own lane before step 9; or something else. Which, and why — weigh the three failed hold rounds.
5. **The promotion/re-issue tool** for whatever 25G83 file is eventually registered: generalize `scripts/promote_calibration_candidate.py` (hard-wired to dbad7cc7/r1 at b953f4b0), use `scripts/reissue_calibration_acceptance.py`, or other?
6. **Anything that would make a measured or published number false** under the plan as it would stand after your amendments.

## Output

Write your answer (≤ 200 lines) to your answer file. First line: `CONSULT ANSWER: <seat>`. For each question: your answer, the one reason that decides it, and the evidence (file:line) you actually read. End with a 5-line plain summary.
