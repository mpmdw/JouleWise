# Charge: review of the Revision 5 seal (SEAL-R5-01)

Assembled 2026-09-25 ~14:00 PDT by the resident magistrate (Opus 5.5, activation 817355d2). Nothing is armed.

## What you review

- **Merge candidate:** branch `feat/2026-09-25-rev5-seal`, commit **23dd9909** (parent: main `c6814dd8`). Review with `git diff c6814dd8 23dd9909`. The only change is two lines of `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`.
- **What it claims to do:** perform the seal step that Revision 5 of that file prescribes (the paragraph under "## Registered epoch and operating condition", and amendment A-R5a-1 in `docs/decision_log.md`). The three literal placeholders are replaced by the PR #412 merge commit and the sha256 of the two launchd templates read at that commit. The header parenthetical "sealing pending PR-L pins" is replaced by "sealed 2026-09-25 at PR-L merge 9b750bf3".

## Questions (answer each with executed evidence; paste the commands and output)

- **S1. Values.** Is `9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87` the merge commit of PR #412 (`gh pr view 412 --json mergeCommit`)? Are the two digests exactly `git show 9b750bf3:configs/launchd/com.joulewise.night.plist.template | shasum -a 256` and the same for `com.joulewise.night-probe.plist.template`? Is each value in the right slot (night first, probe second)?
- **S2. Procedure conformance.** Does the diff follow the seal procedure as written in the file and in A-R5a-1 exactly: literal tokens replaced without backticks; the header parenthetical in the prescribed form; nothing else changed? Is the placeholder count (`grep -c -E '<PR-L-MERGE[-]SHA>|<TEMPLATE[-]SHA256:'` on the file) 0?
- **S3. Consumers.** Does the issuer (`scripts/issue_calibration_acceptance_generation.py`, the Revision 5 block around "unsealed placeholders") accept the sealed text: no placeholder match, and the `template at commit [0-9a-f]{40}` and `template digests [0-9a-f]{64} and [0-9a-f]{64}` patterns each match? Do the tests that read this file still pass: `python3 -m unittest tests.test_acc_25g83_rev5 tests.test_preregistration_chain_digest` (fast), and if budget allows `tests.test_issue_calibration_acceptance_generation tests.test_night_gate` (~1 min together)? Does any test or production code pin this file's bytes or digest in a way the seal breaks, or become vacuous because it edited the unsealed header by string replacement (e.g. `tests/test_acc_25g83_rev5.py` around line 96)? If a test became vacuous, say whether that matters for the science.
- **S4. Science.** Is there any reason this seal, as done, would let a W1 window run under a launch context different from the one registered (ProcessType=Interactive templates at that commit), or would misdescribe it? Name any gap between "template digest at the merge commit" and "what the installer will actually render and load".
- **Verdict:** MERGE, or FIX-FIRST with exact replacement text, or REFUSE. Classify every finding BLOCKER / MATERIAL / NIT.

## Rules for the reviewer

- Single non-interactive session. Start NO background tasks, watchers or subagents; every probe runs in the foreground. Ending before your report file exists is a protocol failure. Wall budget 25 minutes; mark anything you could not run NOT EXECUTED.
- Do not run the full test discovery suite.
- Read-only on the repository. Write only your report file at the path you are given.
- Do not read `RUN_STATE.md`, `TASK_QUEUE.md`, memory, or activation records; this charge plus the repository at 23dd9909 is your packet.
