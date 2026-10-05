# Executing review: PR #479 live v2 row `clock.network_time_policy` replaces `clock.restore_recipe` (head 3180dafb)

Worktree: /Users/edr/code/JouleWise-wt-dd5-dprev, detached at 3180dafb (main parent 85d67b12). Diff: `git diff 85d67b12 3180dafb`. Non-author reviewer, EXECUTING lens. Background: the throwaway-clone re-proof (`/Users/edr/night-archive/desk-day-v5/clone-proof/REPORT.md` F2) found freeze evidence (`DOCTRINE_PIN`, `joulewise/arm_readiness_evidence.py::_derive_doctrine_pin`) still demanded the retired close-out step that restored network time ON after a window. Current doctrine (runbook §5A): network time stays OFF across windows; resync only in the arm step; one OFF receipt per window reused by `clock-disable`; close-out records identity, no restore. The physical hazard: a time sync during or between windows steps the clock that timestamps power samples.

Check, by running code:
1. A pack frozen against the CURRENT runbook derives `clock.network_time_policy.v1` PASS; a runbook §5A edited to (a) drop any one required sentence, (b) add a restore-ON step after a window/verdict/backups, (c) re-enable "automatic network time", each REFUSES. Try at least three adversarial rewordings of a restore step that the regex might miss (e.g. "turn network time back on", "set network time ON again after close-out", line-wrapped/emphasised variants); report any that slip through.
2. Archival compatibility: receipts bound to the archival v1 registry and historical `clock.restore_recipe.v1` predicates still verify byte-for-byte (histsem tests); no historical pin or receipt bytes changed (`git diff --stat 85d67b12 3180dafb -- tests/fixtures configs docs/process_traces`).
3. No other live consumer still names `clock.restore_recipe` as required for a NEW freeze (grep the repo: scripts, joulewise, configs, docs/phase_2).
4. Run: `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-dprev/pc tests/test_arm_readiness_evidence.py tests/test_arm_readiness_schemas.py tests/test_receipt_histsem.py tests/test_arm_readiness_registry.py tests/test_docs_freshness.py` (TMPDIR=/tmp/dd5-dprev). The full readiness suite is run separately by the lead.

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity (BLOCKER/MAJOR/MINOR/NIT) and evidence.

WRITE_SCOPE: []
Scratch: /tmp/dd5-dprev/ only. No background processes. Finish in this turn.
