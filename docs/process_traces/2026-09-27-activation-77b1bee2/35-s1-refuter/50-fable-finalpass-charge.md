# Cold Fable 5.1 final pass (gate row 7) on S1's merge candidate `c7593edb`, plus erratum S1-A3-ROUTE-01-E1 on amendments 77 and 78

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.**

**Candidate:** `/Users/edr/code/JouleWise-wt-s1-refuter-77b1bee2`, detached at **`c7593edb`**. This is BFG-S stream S1, branch `feat/2026-09-26-bfgs-s1-bundles`: head `204424e6`, merged with main `b69c39eb` as `4aefdd12`, plus the lead's one-line test-only bench fix `c7593edb` (counter-review B-1 option (a)). S1's own diff: `git diff $(git merge-base 204424e6 b69c39eb) 204424e6`.

**Evidence** (verify; do not trust). It is all under `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/`:
- `2026-09-27-activation-77b1bee2/30-s1-steps23/11-seat-report.md`: R72-2 GREEN on the tree; mutants (a), (b) and (c) RED; V1 477 OK; V2 343 OK; builder ×2.
- `2026-09-27-activation-77b1bee2/35-s1-refuter/11-refuter-report.md`: the ONE refuter pass (A1, A2 and A5 hold; A3 F1 and F2).
- `…/35-s1-refuter/20-coldgate/21-coldgate-fable-ruling.md`: cold gate S1-A3-ROUTE-01, **NOT BLOCKED**, amendments 77 and 78.
- `…/35-s1-refuter/20-coldgate/22-opus-refuter.md`: the paired refuter, CONCUR, with **five SHOULD-FIX items against the texts of 77 and 78**.
- `…/35-s1-refuter/30-opus-counter-review.md`: the Opus counter-review (rows 2 and 6) on `4aefdd12`: **FAIL on B-1** (the protected-path fence diffed the working tree against `1417c0c4`, so main's harvest state failed it), plus S-1 to S-3 and N-1. The lead's fix and its RED/GREEN evidence are in record `00-activation-record.md` items 33–35.
- `…/35-s1-refuter/40-a4-*.txt`: the lead's A4 on `4aefdd12` (V2 343 OK; B1 and B2 `byte-identical entries=69`; V1 476/477 with B-1 the only failure; `tests.test_bundle_read` 118 OK at `c7593edb`).
- The earlier rulings that define S1's scope: `2026-09-27-activation-3ba66eeb/30-sweepclass-samesig/` (61, 66–71) and `60-s1-fix3/` (72–76); `2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/` (Final texts v1.1); `2026-09-26-activation-f8d6cab1/10-s0-delta/20-coldgate/` (26, 29–34).

**Rule on:**
0. **Ratify or reject the B-1 fix** at `c7593edb`: the fence becomes `git diff 1417c0c4 204424e6 -- <protected>`. Is that what Final texts v1.1 §E means? Also rule on counter-review **S-3** (`test_raw_capture_lane_files_match_main`, pinned to `97082508`): fix it the same way now, or name it in lane BFGS-RAWCAPTURE-01's brief?
1. **MERGE or DO-NOT-MERGE `c7593edb` to main** (merge commit). Does S1 deliver its ruled scope, with the stop rule 61 (c)/66/77 satisfied (A1–A5)? Anything that blocks?
2. **Erratum on amendments 77 and 78** (S1-A3-ROUTE-01-E1). For each of the refuter's five SHOULD-FIX items (77 (a) form 1 too broad; 77 (a) lacks a refusal-only form; F2's test (i) was relaxed; 77 (b) has no channel for correcting a false premise; the 78 (b) pre-check script exits 1 on the historical exemption): adopt, amend or reject it, and give the replacement text. Does any change alter the S1-A3 outcome?
3. **The refuter's out-of-charge note.** The 69-entry historical pin list has no `202609` bundles. How are post-S1 bundles, and the W1/W2 calibration captures, admitted or exempted? Is anything owed before the first scored campaign?
4. **The same-signature check** of the S1-A3 ruling's Question 4: F1 has been to three gates with no new fact, and F1, F2 and the salvage licence share one shape. Should the lanes BFGS-COOLDOWN-ANCHOR-01 and BFGS-RAWCAPTURE-01 go to one consult now? Which of the ruling's five items should that consult decide?

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground. Use `/opt/homebrew/bin/python3`, never `.venv`. macOS has no `timeout`; use `perl -e 'alarm N; exec @ARGV' …`. Kill any process you start by PID.
- Modify NO file in any repository. Scratch goes under `/tmp/fp-s1-77b1bee2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/51-fable-finalpass-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 40 minutes. Mark anything not run as NOT EXECUTED.
- The first line is `VERDICT: MERGE` or `VERDICT: DO-NOT-MERGE`. End with a 3-line plain summary.
