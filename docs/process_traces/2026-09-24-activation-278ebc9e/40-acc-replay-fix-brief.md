ROLE: IMPLEMENTATION SEAT (Sol 6.0): apply cold ruling 38/20 §3.1, §3.3 and §3.4 to the desk replay trace.

WRITE_SCOPE: ["docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/**"]

Worktree: /Users/edr/code/wt-278ebc9e-accreplay (branch docs/2026-09-24-278ebc9e-accreplay, which already holds the replay trace 34). Fences: never launchctl, sudo, networksetup, powermetrics; never touch /Users/edr/night-custody (reading archived records under ~/night-archive is allowed), /Users/edr/JouleWise-measurement-*, ~/Library/LaunchAgents, /Users/edr/code/JouleWise. Sandbox cannot write .git: leave files uncommitted. Do not call Claude or any other agent.
The ruling (binding, read §3 in full): /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/38-coldgate-packet-acc-replay/20-coldgate-fable-replay-ruling.md. Do exactly: 3.4(a) the three replay.py edits and the fitted/unfitted labelling with verdict per 3.1, re-run, rewrite results.json (expected verdict PASS, rc 0); 3.4(b) the README wording replacement (the synthesis quotation is the magistrate's; do not edit it); 3.3 run ex-26's jittered resampling of r6 (ex-26 = /Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/26-acceptance-seat-opus.md, its D1 / decim.py description) as a diagnostic trace under 34-acc-replay-gate/jitter_r6/, with a README stating it is diagnostic only and changes no rule or count.
VERIFY: paste the new verdict line and per-capture table; the jitter diagnostic's headline; `git status --short`.
OUTPUT: envelope report.
