WRITE_SCOPE: []

# CONSULT (rule-11 same-signature escalation) — the window-status guard cannot tell a measurement from a mention of one; design a liveness-marker census (gpt-6-astra, medium, read-only)

History: `scripts/window_status.sh` refused publication when `ps aux | grep -E "run_campaign|window-chain"` matched
ANY process (false refusals under parallel test shards). Round 1 matched "entry points"; the refuter found under-
inclusion (run_night with other chain names, paths with spaces, `--`). Round 2 matched path components on the whole
command string with a unittest/dry-run/grep/codex exemption list; the delta found (a) editors, `git grep`, `less`
and a codex binary under a spaced path still refuse (mention ≠ execution) and (b) the global `unittest` word
exemption hides a live driver whose plan path contains that word. Two rounds, one signature: classifying a ps argv
string cannot be both sound and complete. Stop patching the classifier.

Your charge (read-only; HEAD of this worktree = the round-2 commit, main is behind): design the guard around
LIVENESS MARKERS the measurement machinery already writes or can trivially write, and specify it precisely enough
to implement in one seat:
1. Inventory what a live measurement leaves on disk: the night driver's custody markers (`night/chain.started`,
   `chain.exited`, `censuses.jsonl`, `courier.sent` under `~/night-custody/<plan>/`), any pid/lock file the driver or
   `scripts/run_campaign.py` / `scripts/launch_window.py` writes (grep for lock, pid, marker, `O_EXCL`), and the
   relaunch watchdog's own lock/state; cite file:line for each writer and its removal/exit semantics.
2. Specify the guard's census as: (a) a plan root with `chain.started` and no `chain.exited` whose recorded pid +
   start token is still alive → REFUSE (the watchdog's `(pid, start_time)` identity pattern; cite it); (b) a campaign
   marker (define one if none exists: `run_campaign.py` writes `<runs_dir>/.campaign.lock` with pid/start token at
   start and removes it at exit, O_EXCL, stale-lock detection by pid liveness) → REFUSE; (c) no argv text matching at
   all, OR argv matching demoted to a WARN line that never refuses. State exactly which processes each rule can
   miss (a chain run by hand from a Terminal with no driver?) and whether that miss matters under D-127's quiet-Mac
   rule and D-161 (operator-only-adversary refusals are over-engineering).
3. Define the regressions that make this deterministic (fixture custody roots, injected liveness function, no ps).
4. Give the implementation seat brief: WRITE_SCOPE (exact paths), deliverables, counterfactuals, acceptance modules.
Report (genre review): `verdict` = {counts, findings}; header < 8192 bytes; body = the inventory table, the census
spec, the miss analysis, and the seat brief verbatim under `## SEAT BRIEF`.
