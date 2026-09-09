WRITE_SCOPE: []

# Refuter brief — WATCHDOG-NITS-01 landing, EXECUTION + CONTRACT lens (gpt-6-astra, read-only)
HEAD = one commit on main. Packet: `git diff HEAD~1 HEAD` (scripts/magistrate_watchdog.py, scripts/install_magistrate_watchdog.sh,
docs/process/MAGISTRATE_WATCHDOG.md, two test modules). Claims: F2 corrupt-lock refusal events and pending notices
deduped per full reason + activation (10 identical ticks → 1 event + 1 notice; changed pid list → a second;
acknowledgement independent; reset on activation); F3 the installer calls the shared `handoff-daemons` CLI instead
of an inline classifier and still refuses before any write on all five daemon shapes; F4 the documented step-4 block
names `handoff_lock_absent` before reading the lock; residual documented. 100 scoped tests pass.
Break it: (1) F2 — the safety model says a corrupt-lock refusal must stay VISIBLE: with dedupe, does the next launch
notice still carry the refusal after a long stall (e.g. 300 ticks), and does an ACKNOWLEDGED refusal that persists
get re-noticed on the next activation? Drive `tick`/`decide` with injected tables and count events/notices; (2) F3 —
run the installer's preflight path with a stub `ps` producing each daemon shape (the existing test does) AND with
`handoff-daemons` itself failing (python missing / rc 3 with garbage stdout): the installer must refuse, never
proceed; (3) F4 — extract the step-4 block per the doc's contract and run it with no lock file, a corrupt lock, and a
valid dead lock: named refusal / corrupt path / reconciliation respectively, `zsh -n` + `compile()`; (4) confirm
`production_census`/`agent_census` are untouched (`git diff HEAD~1 HEAD` must show no hunk there) and that the
night path (`decide` in-span) is byte-identical; (5) mutation: drop the dedupe key's activation component and the
installer's refusal-on-rc≠0, confirm the named regressions fail. Run only the three scoped modules. Report (genre
review): `verdict` = {counts, findings}; header < 8192 bytes; findings with file:line, severity, exact command.
