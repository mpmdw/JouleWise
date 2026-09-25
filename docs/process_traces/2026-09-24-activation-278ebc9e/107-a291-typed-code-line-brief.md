ROLE: SEAT K (Sol 6.0), read-only report for JouleWise lane A291 round 3, cold ruling 105/20 §3.4(c). File reads plus at most a few focused unit tests; keep CPU light. Do not call Claude or any other agent.

WRITE_SCOPE: []

Head: `6e2504b1` (worktree /Users/edr/code/wt-278ebc9e-a291p3, read-only). Fences: never launchctl, sudo, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents, /Users/edr/code/JouleWise. Scratch /tmp/278ebc9e/typed/.
TEXT (verbatim): "K's report states, for each of INV-23, INV-36, INV-37, INV-38, INV-52, the witness form actually asserted at the `requeue_overrun` entry path and the refusal code it asserts; where the asserted code is `inv_38`/`inv_39` rather than the row's listed code, the record says so in one line per row. If any of the five has no entry-path witness, that row is an open gate-item (1) defect, not a forger-round matter."
TASK: For each of the five rows: find the existing test(s) in tests/ that drive a violating roster through `requeue_overrun` (the public entry), quote test name and file:line, the witness construction in one sentence, and the asserted refusal code; run each such test once and paste its result line. If none exists for a row, say "NO ENTRY-PATH WITNESS" for it.
OUTPUT: a five-row table (row, test file:line, witness form, asserted code, listed code, note) and the run tails.
