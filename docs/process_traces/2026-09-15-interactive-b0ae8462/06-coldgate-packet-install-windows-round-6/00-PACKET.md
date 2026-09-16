# Cold-gate packet 06 — INSTALL-WINDOWS-MULTI-01 transactional installer at `ccce8a61`: the row-10 fresh-eyes review finds a residual signal sliver after the round-5 signal cure (second fix round on the same defect) and an empty `--render-only ""` blocker; round-6 dictation to be judged

Convened under rule 11 (mandatory trigger: a second fix round on the same defect — the teardown-entry signal sliver first fixed in round 5 from exhibit B F3, found residual by exhibit A F2) by the interactive magistrate b0ae8462 on 2026-09-15 ~21:20 PDT. The fix-round-6 seat is ALREADY RUNNING under exhibit D's dictation; the judge's rulings amend or confirm that dictation before its delta re-audit and before any merge. Nothing is armed.

## What was found (exhibit A; the judge verifies on this checkout at `ccce8a61`)

- **F1 (blocker):** `scripts/install_night_agent.sh` (~:20, ~:79) reconstructs argv from variables, so a supplied-but-EMPTY `--render-only ""` vanishes and the invocation performs a REAL install (probe: rc 0, both fixture labels loaded); `--uninstall --render-only ""` performs real bootouts.
- **F2 (should-fix per the reviewer; the magistrate ruled it MUST for round 6):** after round 5 (exhibit C) the handler blocks INT/TERM/HUP before raising `Signalled`, and `entry_mask` is captured in `Transaction.__init__` and re-captured in `_install_handlers`. Residual: a signal delivered between the exception leaving `run()`'s try and `_unwind`'s first `pthread_sigmask(SIG_BLOCK)` raises `Signalled` INSIDE `_unwind`, which escapes `run()`'s `finally` — teardown does not run and the signals are now left BLOCKED for an in-process caller; same at `uninstall()` between `_install_handlers()` and its block; and an `entry_mask` captured at construction is stale if the caller changed its mask before `run()`.
- **F3 (docs):** NIGHT_HANDBACK ~:204 promises pre-bootstrap close checks that no longer exist; runbook ~:1438 promises sidecar removal on commit while cleanup failure only warns and returns 0 (`night_agent_install.py` ~:379).

## Q1 — Is F2 the same defect as exhibit B F3, and does exhibit D's dictated cure close it completely?

Exhibit D §F2 dictates: (a) capture `entry_mask` at the start of `run()` and `uninstall()`, keep the `__init__` default, remove the `_install_handlers` recapture; (b) in `_unwind`, `for _ in range(2): try: pthread_sigmask(SIG_BLOCK, SIGNALS); break; except Signalled: continue` (the handler has already blocked before raising, so the second iteration cannot be interrupted; a `Signalled` swallowed here never replaces the transaction's result); (c) in `uninstall()`, block FIRST, then install handlers; (d) restore `entry_mask` and dispositions in the `finally`. Rule: SOUND AS DICTATED / AMEND (exact text) / REJECT (write the better cure). Specifically: is there any remaining instruction boundary where a handler-raised `Signalled` can escape `run()` or `uninstall()`, or leave signals blocked for an in-process caller? Is swallowing the sliver `Signalled` (keeping the original exception or the COMMITTED result as the exit) consistent with adjudication 34 D6 (exhibit E)? Execute a probe if it fits the budget (single snippet against the fake adapter in `tests/test_night_agent_install.py`).

## Q2 — F1 severity and cure shape

Rule: BLOCKER / SHOULD-FIX, and whether exhibit D §F1's cure (shell refuses any valued option with an empty value with exit 2 and a usage line; option presence preserved verbatim into the exec'd argv, never rebuilt from possibly-empty variables; module also refuses an empty `--render-only` with exit 2; tests assert exit 2 + zero launchctl invocations + nothing written) is the right shape, or dictate a better one.

## Q3 — Authorization and STOP CONDITION

Charter §9: is round 6 justified (dictated cures only, no new structure)? State the STOP CONDITION for this lane now: if the delta re-audit of round 6 finds ANY further signal-class defect (a path where teardown is skipped or the mask is left blocked), what follows — no round 7 and what instead?

## Q4 — F3 docs drifts

Fold into round 6 as dictated (exhibit D §F3), or register as a lane. Which, and why.

## Q5 — Landability after round 6

Subject to a CLEAN delta re-audit of round 6 (isolated reversions, the ruled same-signature predicates NO/NO, module suites foreground and under inherited SIG_IGN) and the lead's full-suite replay at the final head: is the lane LANDABLE, or does the judge require one more independent lens (name it: e.g. an execution-lens seat driving real signals at every seam) before merge?

## Constraints on the judge

Rule only the questions above; do not amend any rule, decision-log entry or skill doctrine (name text changes as text for the magistrate to record). Cite exhibits by name; code by file:line only if you read it in this checkout. The checkout is the installer branch at `ccce8a61` with this packet directory added as untracked files; the round-6 seat's edits are NOT in this checkout.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
6d1da034bad631246acc92d6be6bccabe005aa8ecc235482b3a9ea7ed8c894db  exhibit-A-row10-fresh-eyes-ccce8a61.md
00c9dcc06d34fd135abfaebad8623c2dbb2bffadee9c8c57c7303b7b9e5a6788  exhibit-B-lt31-opus-counter-review.md
eff63b731c2e14546a5473091bffee1bf5aee8a7a74f22d1e53d208c80d3b07c  exhibit-C-fix-round-5-f3.md
23fc8d3cbe9862fbb1c7aed759f0709c6fe52ce46a43469bc19e6a6a0a05dd37  exhibit-D-fix-round-6-dictation.md
eafe9d86643c75313edee4b156cf20e1eb64518c08159463069af0eababad775  exhibit-E-design-adjudication-34.md
```
