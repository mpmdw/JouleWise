# Cold-gate packet: corrupt-lock recovery — revert to fail-closed (prune) or tighten (fix round 2)?

Assembled mechanically by the interactive magistrate at 2026-09-08 ~01:45 PDT. Rule-11 trigger: a second fix round
on the same defect (Opus finding C2 of the WATCHDOG-CENSUS-01 / RESUME-DAEMON-01 landing).

## History
- Landing 898e5305 (exhibit D is the safety model it serves): step-4 lock reconciliation refused any lock that
  did not parse (`read_lock` → `{}` → `handoff_lock_invalid` → `handoff_lock_not_clear`). The installer's exclusive
  seed refuses while any lock file exists, so a corrupt lock blocked reinstall with no documented recovery.
- Opus contract refuter C2 (exhibit C): should-fix — "let step 4 clear a `{}`/corrupt lock when no owned/twin
  process is live (fail-closed if any is), with a regression, OR document an explicit alternative command."
- Fix round 1, commit b3eeee9a (exhibit B): the documented block now clears a corrupt / non-object / `{}` lock using
  the SAVED step-3 inventory (`handoff-NNN.json`), refusing live owned pairs, resumed twins and invalid inventory.
- Delta re-audit (exhibit A, Astra, injected process tables): BLOCKER R1 — with corrupt lock bytes, the saved owned
  pair absent, and a live UNRECORDED headless magistrate (`claude -p` with the resident launch options, e.g. pid
  84232) the block prints HANDOFF_DEAD_LOCK_REMOVED and unlinks; 898e5305 refused the same input. The saved
  inventory does not bind to the corrupt lock's actual owner, so a stale inventory removes ownership protection
  while a headless magistrate is alive — overlapping ownership, the failure the watchdog exists to prevent.

## The two candidate dispositions
P (prune, the interactive magistrate's recommendation): revert the C2 mechanism to 898e5305's fail-closed refusal
and DOCUMENT the recovery as Ed-hands: an operator with an observer Terminal confirms with `handoff-inventory` and
`ps` that no headless resident and no resumed twin is alive, then removes the corrupt lock by hand. Rationale:
D-161 (exhibit E) — operator-only-adversary refusals are over-engineering and fail-closed stays only for
physics/evidence/pre-registration; a corrupt lock is a rare operator-recoverable state, and no mechanism that
reads a possibly-stale inventory can prove the absence of an unrecorded owner. Cost: a corrupt lock during a
hands-free week stalls the loop until Ed acts (the watchdog's own tick already refuses to launch on an invalid
lock, so the stall is safe).
F2 (fix round 2): keep the mechanism but require, in addition to the saved inventory, a live census showing no
`claude -p` resident shape and no resumed twin, refusing otherwise. Rationale: hands-free recovery. Risk: the
census is a command-shape classifier; a third shape (a future binary rename, a test stub like the leaked pid
48645) escapes it, and this is exactly the "another missed call site" signature rule 11 warns about.

## Charge
Rule P or F2 (or a third disposition), with the failure-mode test: can the chosen disposition ever unlink a lock
while a process that could be the owner is alive? Answer also: does D-161 (exhibit E) apply to this refusal?
Executed probes: run `exhibit-A`'s described matrix logic against the exhibit-B block if feasible in the foreground;
otherwise reason from the diff. Write the ruling to ./coldgate-packet-2/10-coldgate-fable-ruling.md.
