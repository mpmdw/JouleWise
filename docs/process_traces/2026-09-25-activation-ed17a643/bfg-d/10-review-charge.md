# BFG-D review charge: exact candidate `df33888f` (branch `feat/2026-09-25-bfg-d`, base `c6814dd8`)

BFG-D implements Ed's binding directive #421 (battery-float gate for measurement windows) for derivation windows, as the cold rulings require. The next measurement window, W1, cannot arm until BFG-D merges. Code that is wrong here either lets a charging or unverified window count as evidence, or blocks honest windows.

**The one source of truth for the requirements** (read these, in this directory):
- `00-final-texts-v1.1-source.md` §5: BATTERY-FLOAT-01 final texts v1.1. The predicate, refusal codes, insertion sites, record schema, consumers, issuer contract, tests 1–11 and W1 prerequisites.
- `06-harvest-final-obligations-v1.1-source.md` §4: HARVEST-VERDICT-FINAL-01 obligations v1.1. The custody rule, the committed per-window verdict file and its authentication, issuer refusal on disagreement, the registry pin, anchoring, A-R5b-1 and items 1–11. It supersedes §5 where they differ.
- `03-lead-rulings-r1.md`: lead rulings R1–R5 on test fixtures, the cadence report CLI, scope, and applicability keyed to the 25G83/Revision-5 generation.
- The seat reports `05-seat-report-r3.md` and `08-seat-report-r4.md` are the implementer's own account. Verify them; do not trust them.

**Lead bench changes to judge as well:** `ab431280` moves the t0 R1 liveness bound from 600 s to 610 s (11 × 45 s + the 10 s ioreg site + 105 s). The literal reading of the older ruled formula gives 645 s; say which is right. `df33888f` adds runbook §1.5 arm-record item 6.

**Review the whole diff** (`git diff c6814dd8 df33888f`, 46 files). Report every finding tiered BLOCKER / MATERIAL / NIT, each with executed evidence (a command and its output, or file:line). Your lens is given in your prompt. For all lenses:
1. Every ruled obligation implemented exactly, at the named production site, with its test exercising the production call site. Name any obligation that is missing, weakened or implemented differently.
2. Bypasses. Can any caller count a charging, stale, missing or custody-failed window, or drop a clean window after seeing B, through any entry point? Entry points include the CLIs, library functions, recovery paths, re-preparation, the registry, env vars and flags.
3. Perturbation. Can any battery observation fall inside the clock-anchor interval, or change a measured number, a pinned digest or the registered protocol? Check the pin proof yourself.
4. Regressions. Was any pre-existing assertion weakened? Diff the tests and list every changed expected value. Is any existing behaviour for other epochs or generations changed?
5. Fail-closed behaviour on probe errors, malformed ioreg output, git errors and missing files.
6. Test quality. Would each defect-shaped test fail if its guarded line were reverted? Run at least three such mutations yourself, in a /tmp copy and never in the worktree.

**Constraints:**
- Read-only in the repository. /tmp is fine.
- Run no full test discovery. Focused modules are fine.
- Never run launchctl, powermetrics, sudo, the installer or model inference. `ioreg` (read-only) is allowed.
- Use one foreground session, with no subagents and no background jobs.

End with a verdict: MERGE or FIX-FIRST.
