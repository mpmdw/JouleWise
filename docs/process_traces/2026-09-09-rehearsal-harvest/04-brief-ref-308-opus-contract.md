# Refuter brief — PR #308 @ 20f95848d5975947dbc5bb1c295e56cb58bb534f, CONTRACT lens (Opus, read-only)

Worktree (read-only; do not edit, do not run git write commands): /Users/edr/code/JouleWise-wt-ref-308-astra (detached at 20f95848d5975947dbc5bb1c295e56cb58bb534f).
Scope of the PR: `git diff --stat main...HEAD` — process-trace docs and byte artifacts only, no code.

Lens: CONTRACT COMPLIANCE. The documents record (a) the arming of the rehearsal-20260909 stub night by headless activation 784a764e,
(b) two pre-window relaunches that did no work, (c) the harvest by activation 628c2eed, the documented uninstall, and the removal of
the stub checkout and plan root, (d) a finding (receipt refused night_probe_error) and its registered cure lane.
Governing texts on this head: docs/process/NIGHT_HANDBACK.md (§Purpose, §Where the results are, §Next lane, standing rules),
docs/process/MAGISTRATE_WATCHDOG.md (relaunch prompt, stand-down, what the magistrate may and may not touch),
docs/process/state_kernel.json /tasks/NIGHT-REHEARSAL-01, D-175 (docs/decision_log.md, line-19 rehearsal authority, eight conditions),
and the relaunch-prompt rules quoted in 00-DURABLE-STATE.md.
Questions to answer with quotes:
1. Did the arm (21h + arm-* artifacts) satisfy every D-175 condition and every NIGHT_HANDBACK §Next lane precondition, in the recorded
   order (email-then-arm, no NO, census clean, both agents installed FROM the measurement_root at measurement_head, frozen triple recorded)?
2. Did the harvest activation stay inside its authority: harvest before uninstall, uninstall from the stub checkout, removal only after
   verifying the results branch on origin, nothing armed, no watchdog-owned file touched, no process rule amended? Cite 21i and the
   *-output.txt artifacts.
3. Is the finding classified correctly under NIGHT_HANDBACK (only night_refused_agent_present acceptable) and is the acceptance table
   in 21i honest about which NIGHT-REHEARSAL-01 items are met, conditional, or open? Does 21i improperly decide anything reserved to
   the cold gate or Ed (rule 11), e.g. whether a second stub night is required?
4. Are the four durable-state sections and 21h/21i mutually consistent (frozen triples, next actions, "nothing armed")?
Output: findings ranked blocker / should-fix / nit, each with exact quote + governing text + proposed correction; then the list of
checks that PASSED. Read-only. No design proposals.
