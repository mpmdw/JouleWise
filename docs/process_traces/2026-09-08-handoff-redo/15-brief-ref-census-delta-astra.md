WRITE_SCOPE: []

# DELTA RE-AUDIT — fix round 1 on the WATCHDOG-CENSUS-01 / RESUME-DAEMON-01 landing (gpt-6-astra, read-only)

Fix rounds introduce defects (proven twice on this project), so every fix round gets a fresh delta re-audit. HEAD of
this detached worktree is the fix-round commit; HEAD~1 is the reviewed landing (898e5305); HEAD~2 is main d8ad6c15.
Packet: `git diff HEAD~1 HEAD` (3 files: scripts/magistrate_watchdog.py +2, docs/process/MAGISTRATE_WATCHDOG.md
+67/-5, tests/test_magistrate_watchdog.py +79). The fix seat claims: C1 `reused_skipped` preserved when a
changed-token pid disappears before KILL; C2 documented step-4 reconciliation can clear a corrupt / non-object / `{}`
lock using a SAVED ownership inventory, refusing live owned pairs, twins, and invalid inventory; C3 verbatim
inventory + observer-Terminal stop commands that revalidate pid/start token and resumed-twin role before each
signal; C4 the recovery block is marked INTERACTIVE MAGISTRATE / OPERATOR ONLY and cites relaunch-prompt line 19;
C7 step-0 digest deadline moved before step 1. Four regressions written first (failed rc=1 before, pass after);
90+ scoped tests pass.

Break it. Specifically: (1) C2 is the dangerous one: a corrupt lock is exactly the state an attacker-free but
buggy handoff leaves; does the new reconciliation ever unlink a lock while ANY process that could be the owner is
alive (feed it: inventory lists pid P with token T; process table has P with token T; P with token T'; P absent;
an unrelated interactive claude; a `--resume … --reply-on-resume` twin; the headless resident 84232 shape)? Does
"saved ownership inventory" mean the handoff-NNN.json file, and what if it is missing, stale, or names a reused
pid? (2) C3: extract the documented stop block exactly as an operator would and run it against an injected table
(or dry-run) — does it signal only the twin whose token matches, and refuse on mismatch BEFORE any signal?
(3) C1: two-line code change — does it alter any other label path (already_gone / term_exited / kill_exited)?
(4) Doc extraction contract still intact (`watchdog_checkout=` … `   PY`, three-space strip; `zsh -n`, `compile()`)
and step ordinals 0-6 unique and ordered. (5) Mutation probe: revert the C1 change and the C2 refusal conjunct in a
$TMPDIR copy; confirm the named regressions fail. (6) Anything the fix round broke that HEAD~1 had right.
Run only the three scoped modules; never the repository-wide suite. Report (genre review): `verdict` = {counts,
findings} ONLY; header < 8192 bytes; every finding with file:line, severity, the exact demonstrating command.
