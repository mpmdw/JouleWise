# PR #800 gate 5 repairs (2026-11-16)

Explicit user intake outranks ordinary queue work. Mission M0 read the stop-card, status, workspace, queue, playbook, owning design and orchestration; no active stop card or phase-exit checklist row exists for this bounded fix round. Authorities: RL-172 (c)(g)(i) and RL-173, read from origin/audit/2026-11-10-fable; cadence_queue_design 15.13–15.14. No MBP contact, real custody access, measurement, installation or merge. Every executed controller interface is synthetic or stubbed.

Reviewed input heads: #799 6b4e32b20; #800 eb2a2a608. Cold review: /Volumes/JW-EXT/scratch/sol-gate5-800-799/FINAL-MESSAGE.md; detailed report: /Volumes/JW-EXT/tmp/joulewise-cold-799-800.E07fBr/pr800/docs/run_reports/2026-11-15-cold-review-pr799-pr800.md. Earlier handoffs: /Volumes/JW-EXT/scratch/ctl-r4/HANDOFF.md and /Volumes/JW-EXT/scratch/sol-ctl-r5/FINAL-MESSAGE.md. No review seat was launched or final verification delegated.

## Dispositions

| Finding | Disposition |
|---|---|
| F1 HIGH, key exception never expires | FIXED: compare admission now with the absolute RL-173 A.1 deadline; an old marker cannot extend it. Law boundary and full-controller predecessor-copy regressions. The launch lease also expires at the key deadline when the final authority read used the temporary exception; a slow notice cannot cross it. |
| F2 MED, expired fence renewed away | FIXED: preserve expired owned deadlines through startup, refresh and take. Tick and network guard route a lapse to a durable HALT/ARM_INDETERMINATE page; no subsequent admission before acknowledgement and fresh evaluation. Regressions cover tick, guard and restart. |
| F3 MED, informational page drops fence | FIXED under RL-173 E: WAIT_STALL keeps the live queue's fence through later polls and restart. Regression checks the fence on every NOT_BEFORE poll past the stall bound. Actual halt/cede/fallback handoffs retain their explicit behavior. |
| F4 MED, failed session listing treated as empty | FIXED: distinguish successful empty reads from failed session, Q1 and local desk-ref listings. Both authority reads hold as FETCH_FAILED. A failed local history read cannot add --history-empty or run the close desk. Regressions include a committed READY session, all analogous listings, and faults at first/second reads. |
| LOW, valid rerun draw coverage | #799 adds a queue-valid unique-id rerun chain for exact hash and append stability. No hash nondeterminism reproduced. Executed/disposed ancestors' first-place semantics remain NEEDS_RULING. |

The design's current interface, historical dispositions and open-question list point to section 15.16. Previous claims that informational pages release the live queue or marker creation time governs A.1 are superseded, rather than promoted to new policy.

## Verification

Scratch evidence: /Volumes/JW-EXT/scratch/sol-ctl-r6/. The final eight regression tests were copied to a detached scratch tree at eb2a2a608: regressions-before-final.log records 15 assertion failures, including LIVE admission on failed authority reads and old keyless markers, no lapse halt, absent stall fence, and desk launch on unreadable history. All eight original regressions passed in regressions-after-final.log. A ninth regression reproduced LIVE admission when a slow notice crossed the key-copy deadline after the final authority read (key-crossing-before.log), then passed after the lease repair (key-crossing-after.log).

Local cadence execution excludes all 12 tests in test_launch_cadence_span.py because that module signals fixture processes; the harness rejects nonzero parent os.kill/os.killpg. No test was unstubbed and no production host command was added. Repository-wide local discovery is not used because it includes signal/host fixtures; the final-head CI matrix supplies canonical-suite evidence. Host-command inventory, host-command guard and docs freshness passed 48 tests; gen_state --check passed. All 15 synthetic scenarios passed (synthetic-final.log). An initial safe cadence run executed 418 tests and exposed five parked-wait fixtures that skipped renewal polls; those fixtures now model intervening polls through World.advance_wait. The nine final regressions retain direct clock jumps for deliberate lapses. Final safe cadence rerun: cadence800-final.log; its tail and final-head canonical CI are re-read into the current PR table. Fixture census observation failed with PermissionError on ps (exit 2, fixture-census.json), not a clean census; no process was signalled or culled.

## Research-lead questions (no rulings made)

- Rerun draw: does a disposed executed ancestor consume the always-drawn place? Count the ancestor, or resolve rerun chains. Prior recommendation is to preserve first place; this round changes neither behavior nor policy.
- Unknown L002 recovery: may rerun/withdrawn disposition release a span whose receipt is missing? Current conservative hold remains; an explicit owner ruling is needed to relax it.
- Reference binding N12: the frozen reference identity is bound by capture-run name without a pinned record hash. Stronger binding or acceptance of this interface requires the research lead.
- Confirm Q1 completion records for hand-armed counted v1.1 spans and the typed-marker switch-over, and decide whether a separate non-counting clearance is needed for disposed spans with desk disagreement. Existing conservative behavior remains.
- External offload guarantees, stronger key/private-destination attestations and campaign-scope shared history stay with the named offload/shared-history owners before installation or future campaign-scope use. No custody assertion is authored here.

## Process and next action

Both supplied worktrees were clean but stale. #799 fast-forwarded to its reviewed head. Every old local-only #800 commit was patch-equivalent to the remote stack (git cherry); its branch was aligned to eb2a2a608 before edits. #800 is linearly rebased on #799's new head; rebase conflicts in the two running handoff files preserved both dated records. Unrelated files and earlier scratch evidence remain intact. Commits carry the requested coauthor trailer; all rewritten pushes use an explicit force-with-lease.

The supplied independent executing review caught four admission/fencing defects despite green historical tests; final regression and suite checks verify the concrete repairs. The host-command inventory caught the expected changed desk-call locator and was refreshed for the reviewed call. No additional agents/consults were used. Fresh cold admission and the watched native span are still owner gates, not implied by passing CI. Next exact step: inspect both PRs' verified current tables and final-head CI, obtain the research-lead decisions above and fresh gate admission, then handle installation separately. Do not merge.
