WRITE_SCOPE: ["scripts/magistrate_watchdog.py","docs/process/MAGISTRATE_WATCHDOG.md","tests/test_magistrate_watchdog.py"]

# Prune brief — revert the C2 corrupt-lock recovery mechanism to fail-closed; document Ed-hands recovery (gpt-6-astra)

HEAD = b3eeee9a (fix round 1 on top of landing 898e5305). A delta re-audit found a BLOCKER in the C2 cure: the
documented step-4 reconciliation now clears a corrupt / `{}` / non-object `magistrate.lock` using the saved
step-3 inventory, and with a stale inventory it unlinks while an UNRECORDED live headless magistrate (`claude -p`
resident shape, e.g. pid 84232) is alive — overlapping ownership. 898e5305 refused that input.

Do exactly this (a prune, not a new mechanism; a parallel cold gate may still overturn it, so keep the diff minimal
and reversible):
1. Revert the corrupt-lock CLEARING path to 898e5305's behaviour: an unparseable / `{}` / non-object lock is
   `handoff_lock_invalid` → the documented block refuses (`handoff_lock_not_clear`) and leaves the file. Keep every
   other round-1 cure intact (C1 label, C3 verbatim twin-stop commands, C4 authority boundary, C7 ordering).
2. Replace the round-1 C2 regression (the one asserting removal of corrupt forms) with a regression asserting the
   REFUSAL for the three corrupt forms, including the delta's exact counterfactual: corrupt bytes + saved owned pair
   absent + live unrecorded `claude -p` resident in the table → refused, lock still present.
3. In docs/process/MAGISTRATE_WATCHDOG.md step 4, document the recovery as ED-HANDS ONLY, verbatim commands: from
   an observer Terminal, `scripts/magistrate_watchdog.py handoff-inventory` and
   `ps -axo pid,ppid,lstart,command | grep -E "claude|codex"` must show no headless resident (`claude -p` with the
   resident launch options) and no resumed twin; only then `rm` the corrupt lock by hand; state that no mechanism
   removes a corrupt lock because a saved inventory cannot prove the absence of an unrecorded owner (cite the delta
   re-audit finding R1 of 2026-09-08).
4. Keep the reaper-block extraction contract (`watchdog_checkout=` … `   PY`, three-space indent); re-run `zsh -n`
   and `compile()` on the edited block. Acceptance = the three scoped modules to a log with rc (never the
   repository-wide suite). No `git commit`. Envelope header < 8192 bytes; genre implementation verdict keys.
Report body: the exact lines reverted, the new regression's counterfactual, fail-before/pass-after tails, acceptance rc.
