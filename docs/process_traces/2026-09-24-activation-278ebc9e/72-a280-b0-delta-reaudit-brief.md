ROLE: DELTA RE-AUDITOR (Astra 6, cross-family) for JouleWise lane A280 PR B0, fix round 1. Read-only with executed probes. Do not call Claude or any other agent.

WRITE_SCOPE: []

OBJECT: `feat/2026-09-24-a280-b0-kind-dispatch` at `bee658c5acc4dd860a382317c40ec4421587a13a`; the fix-round delta is `git diff 7647bb2e bee658c5acc4dd860a382317c40ec4421587a13a` (WIP `f170af7c` plus its completion). Your worktree /Users/edr/code/wt-278ebc9e-b0audit is a detached checkout of `bee658c5acc4dd860a382317c40ec4421587a13a`. Base main `2ea6a7ec`.
The contract is brief 10 (/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-7370d0fb/10-a280-b0-seat-brief.md §1–§2). The lenses' findings and the magistrate's cures are in brief 32 (/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/32-a280-b0-fix1-brief.md, cures C1–C6) and the lens reports 29a/29b in the same directory. The fix report is 47b.
CHECK (execute; paste tails):
 A1. Each cure C1–C6 is implemented as ruled, and each lens witness (Opus w1 ×4 and w2 ×4, Sol F1, Sol F2, Opus mutant M3) now shows the BASE outcome at `2ea6a7ec` and the SAME outcome at the head, except where the brief rules otherwise. Run them.
 A2. Fix rounds introduce defects: hunt for any NEW idle-behaviour change the fix introduced (notice/wrapper/refusal bytes and texts, reporting, cleanup, uninstall/veto/verify, courier), and any remaining kind source that is not the sealed plan/chain source or a validated C5 receipt.
 A3. Same-signature check: does any path still let an unreadable/ambiguous/missing kind change idle behaviour or fall into a non-idle handler?
 A4. `test_base_archive_byte_goldens` and `test_refusal_parity` pass unchanged (`git diff 2ea6a7ec bee658c5acc4dd860a382317c40ec4421587a13a -- tests/test_night_kinds.py` must not touch their expected bytes).
Scratch only under /tmp/278ebc9e/b0audit/. Never launchctl, sudo, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents, /Users/edr/code/JouleWise.
Severity BLOCKER / should_fix / nit with witness and cure. OUTPUT: findings table; A1–A4 verdicts; probe tails.
