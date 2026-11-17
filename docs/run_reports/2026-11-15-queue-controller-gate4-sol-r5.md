# PR #800: gate-4 dispositions, Sol round 5 (2026-11-15)

User-directed repair of PR #799/#800 takes priority over ordinary queue work. This is [AGENT] work only; no phase exit-checklist matrix row exists for this fix round. No MBP contact, native measurement, custody, energy or power files. No merge.

The original worktrees' Git metadata points into an environment-denied directory. Reads were retried; no permission or sandbox bypass was attempted. Both original trees remain untouched. Exact handoff heads were available in the accessible review clone; isolated detached build trees are /Volumes/JW-EXT/scratch/sol-ctl-r5/wt799 and wt800. #799 is pushed at 6b4e32b207628bd4d6e43d53b81947533be942ef; #800 is linearly rebased on it. Final remote head and CI are recorded in the PR body and scratch verification JSON.

## Findings and scope

The complete gate-4 findings table is design section 15.15 (Mythos F1-F12 and Opus 1-12, including every residual). The prior reports remain immutable at /Volumes/JW-EXT/scratch/mythos-gate4-800-799/REPORT.md and /Volumes/JW-EXT/scratch/opus-gate4-800-799/REPORT.md. Both seat exit logs show exit 0. RL-172 and RL-173 extracts were checked as exact substrings of the current origin/audit/2026-11-10-fable decision document. These reports refused/required fixes at the old heads; no fresh seat admission is claimed here.

Fixed controller behavior:
- L002 release time is checked globally against the span's receipt, for every candidate and fallback.
- A proved zero-leg refusal is distinct from absent evidence. Receipt rows merge with packed summaries, so a leg that began with no summary still counts as unreleased. The prior-span reader uses the same rule and refuses symlink/nonregular/oversized receipts.
- Copy debt covers stranded closed outputs without receipts and survives a newer foreign receipt for the newest campaign close.
- Decision time refreshes after long retries and watcher reads; retry completion restarts the close floor. Upload retries wait 5 then 15 minutes. An exit failure cannot be overruled by a marker; a changed recovery marker triggers a recorded synchronous tool replay. The external tool must be idempotent when a verified marker already exists.
- Long steps reserve a full fence timeout plus margin. Every mid-arm lost/lapsed fence halts. Missing own fence has the 30-minute bound; a live foreign run retains 36 hours.
- A disposition names the exact verdict_sha256 values it clears in its optional verdicts map (mbp/offhost). Duplicate disposition plan ids are invalid. Later off-host stops and disagreement cannot inherit an earlier clearance.
- Whole-checkout pin/dirty checks run at arm and desk close; the desk subprocess uses an empty isolated bytecode prefix. A missing public signing key fails closed. Production cannot disable the standing fence.

Deferred owner work is explicit, not claimed fixed: the air-independence tool must prove arbitrary descendants have ended, remove its .failed status before publishing success, and replace free-text private destination/key-copy assertions with a reviewed contract. The controller cannot derive physical key custody or arbitrary process ancestry from those strings. All current kits use span-scope stops; campaign-scope history needs a shared authenticated-history lane. history-empty is now auditable but remains an operator assertion after a full fetch. sample-plan remains a caveated queue-only preview. No new kill/reap path or test was added; existing signal stubs remain in place.

## Research-lead questions (not decided)

1. Does a disposed first executed attempt consume the kit/G0 group's always-drawn place? Count it, or resolve rerun chains; recommend the latter without implementing it before ruling.
2. May rerun/withdrawn release an entirely unknown L002 outcome when there is no readable receipt? Current behavior holds; an explicit non-released outcome always needs the L002 release record.
3. Does A.1's 24 h apply to current judgment time or the marker's written_at? Current behavior is written_at.
4. Does an informational WAIT_STALL page release the continuous fence (gate-3 T13)?
5. N12: reference record hash is bound by capture-run name, because frozen pins record no hash.
6. Confirm Q1 records for hand-armed v1.1 spans counted in line 9, and typed-marker switch-over for the newest hand-armed close.
7. A rerun/withdrawn span with disagreement currently needs a cleared disposition with updated verdict bindings. Should non-counting clearance exist?
8. The deny scan covers JSON keys, not arbitrary value semantics. Current frozen producer outputs remain the supported surface; a stronger value/allowlist projection needs an owner contract.

## Process and verification

A separate desk worker had an exhaustive four-file repository allowlist in wt799 and made no commit; lead reviewed its full diff, applied bookkeeping and committed. Its only deviation was a log placed in the parent scratch directory, with no repository scope violation. A distinct read-only delta reviewer found duplicate-disposition epoch laundering and the prior-receipt rule mismatch; both were corrected and regressed. Focused recovery then exposed deterministic transport's fixed commit date, which rules out timestamp clearance; the final implementation binds exact verdict hashes and preserves the transport. It also found a stale desk draw comment, corrected on #799. Neither worker supplied final verification or merge authority.

The focused regression set verifies later verdicts, duplicate dispositions, global release chronology and exact verdict binding, zero/unknown/partial leg evidence, persistent copy debt, contradictory tool exits, fence lapses/budgets, retry spacing, clock freshness, public-key absence and production fence config. The full cadence suite and standalone synthetic scenarios are required below; host-command inventory must match the changed isolated desk invocation. Full local canonical discovery is not used to run process-kill/reaping integration classes during this agent session under the user's safety constraint; hosted CI supplies the ordinary full-suite shards. The ledger's separate merged-main whole-suite gate remains lead-owned.

- Final cadence discovery: 421 tests, OK with 12 explicit environment skips (296.274 s). The skipped methods are exactly those identified by the first full discovery's /bin/ps failures; no tracked test is marked skipped. The initial full run recorded 418 tests, 3 failures and 13 environment errors. The failures (old copy expectation, offload marker replay, recovery clearance) were corrected and independently rechecked; final all-available discovery passes. Exact IDs: scratch ps-unavailable-tests.json; runner: run_available_cadence.py.
- Final host-command inventory, docs freshness and guard: 48 tests OK (3.979 s). The desk-close locator is 705b4693b4eb1846 after its isolated bytecode-prefix argument.
- Standalone synthetic: all 15 scenarios SYNTHETIC OK, including consumer, recovery, offload, global L002 and fence paths.
- Final #799 checks: 102 tests OK (71 desk + 31 docs freshness, 32.544 s).
- Focused final clearance/recovery/law/fence set: 94 tests OK (6.141 s).
- git diff --check passes. Both extracted rulings exactly match the fetched authority.
- #799 CI run 43788724536 shard 8 failed before tests because apt could not install zsh (no installation candidate). A job rerun requested via the connected GitHub tool was rejected while the workflow remained active; retry after its remaining jobs finish. This is an infrastructure failure, not a passing code result.
- No mechanism caught or changed a scientific number: this run corrected operational arm/hold behavior using synthetic evidence only. No native gate is discharged.

The session-end fixture census could not observe: exit 2, PermissionError from ps. This is not an empty or clean census; no process was signalled. CI and local verification logs are under /Volumes/JW-EXT/scratch/sol-ctl-r5/. Gate-ledger cannot be made green truthfully until fresh independent admission, whole suite on the merged tree and the lead's cold Fable pass exist. No new Claude seat was launched without quota approval; no gate rows were invented.
