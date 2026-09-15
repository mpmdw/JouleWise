# lt-01 — Docs↔code reconciliation seat (Astra high), INSTALL-WINDOWS-MULTI-01

Launched 06:58:21 PDT, reported 07:08 PDT (clock reads), detached pid 77125,
`codex-run-v3`, `-s workspace-write`, `-m gpt-6-astra --effort high --genre
implementation`, worktree `wt-integ-install-windows` at `5124de47`.
Brief: `/tmp/magistrate-d6888966/brief-01-reconcile.md`. Seat output:
`/tmp/magistrate-d6888966/lt-01-reconcile.md`.

`WRITE_SCOPE` exactly the four documents. Envelope: `status: findings`,
`completion: complete`, `unowned_dirty: []`.

## Why the seat existed

Seats A (code) and D (docs) ran in parallel from the same base; seat D wrote
its text from the adjudicated design BEFORE seat A's code existed (seat D flag
F1). The docs therefore described an intended implementation, not the shipped
one. The brief fixed the direction of truth: **the code in the tree is truth,
the docs are corrected to match it, never the reverse** — and required any place
where the code looked wrong against the design to be raised as a flag instead of
being documented as intended behaviour.

## Landed as `7a512827` on `int/2026-09-15-install-windows` (pushed)

Three documents changed, +120 / −48; `docs/process/NIGHT_COURIER_PROMPT.md`
already named `night-results/<plan_id>` correctly and is byte-identical.

Corrections, each carrying the code file:line that is its authority: `FENCED`
distinguishing launch-prevention from drain-adoption
(`magistrate_watchdog.py:1463,1477`); the installed-plist fence and the complete
`decide()` evaluation order (`:1396,1460`); the chain-marker extension applying
only from the plan-span start (`:757`); the kill-switch probe's real position in
the tick (`:1444`); same-day install timing replacing "installs on the day
BEFORE t0" (`run_night.py:962`, `install_night_agent.sh:183`); removal of the
separate fixed-D 12599 s maximum and the `−1` explanation in favour of the
direct `completion < deadman_epoch(plan)` comparison (`run_night.py:954,1540`,
`gen_derivation_night.py:514,516`); `PLAN_LEAD_S`'s real import home
(`magistrate_watchdog.py:69`, NOT `run_night`); the installer's five accepted
flags, unknown-flag usage exit 2, verbatim diagnostics and verbatim rollback
messages with exits 2/3 (`install_night_agent.sh:4,173,312`); dictionary-exact
launchd calendar verification that rejects extra keys (`run_night.py:1034`,
`install_night_agent.sh:235`, template `:24`); the results branch AND the trace
directory both keyed by the full `plan_id` (`run_night.py:570,578`); the
complete overrun diagnostic template and the `measurement_root` refusal prefixes
(`gen_derivation_night.py:517,331`); and a NIGHT_HANDBACK notice that names the
whole shipped span pair from observed output (`run_night.py:1028`).

**The runbook's `schedule --plan` print block, as seat D wrote it, did not
run**: `ImportError: cannot import name 'PLAN_LEAD_S' from 'scripts.run_night'`.
Repaired, executed, and its real output pasted into the document. This is the
concrete vindication of running the reconciliation step at all.

## Preservation (the part that could not be allowed to fail)

Seat verification V7 asserts BYTE_IDENTICAL for the historical revision notes,
every `Executed`/addendum record, the courier prompt, the handback standing
addenda, the watchdog install/rehearsal sections, and — explicitly — **runbook
§3's FAIL-route distinct-calendar-days pre-registration constraint**, which the
brief named as untouchable. The lead re-checks this at the gate; it is ledger
row 8's evidence.

## Verification the seat ran (tails in its report)

`tests.test_docs_freshness` Ran 31 OK; `tests.test_night_gate` Ran 59 OK;
`run_night.py schedule --plan` on a synthetic v2 plan, exit 0, real JSON;
the repaired print block, exit 0; `install_night_agent.sh --help` usage exit 2
(expected); `git diff --check` clean. Single modules only; no full suite, no
network, no launchd, no commits by the seat.

## Flag F1 — `defect_in_code`, blocking (LEAD-CONFIRMED BY READING, not taken on trust)

`scripts/install_night_agent.sh` enforces recurring-span MEMBERSHIP only in
`initial` mode (the `install_outside_span` refusal sits inside
`if sys.argv[4] == "initial"` at `:192`). The three `close`-mode rechecks —
before the dead-man bootout, before the night bootstrap, and after it
(`:305,:307,:312`) — evaluate ONLY `now >= install_close_epoch_s`. An
installation can therefore begin inside a custom span and complete its
bootstrap after that span has closed, while still being before the plan cutoff.
The kernel acceptance says every listed span carries "the never-install-after-
close dead-man rule"; the adjudicated ruling says the installer refuses unless
BOTH bounds hold. Only the plan bound is re-checked.

The lead read `install_night_agent.sh:186-198` and `:300-320` directly and
confirms the control flow. The seat's V8 reproduces it with the extracted
`SCHEDULE_CHECK` code on synthetic times and no launchctl call.

It is LATENT under the shipped default, whose single whole-day span
`(("00:00","24:00"),)` has no daily gap — so no currently reachable arm is
wrong. It becomes live the moment Ed populates a narrowed span list, which is
exactly the capability this lane ships.

**The lieutenant does not set this severity.** It was deliberately NOT disclosed
to either refuter, so that an independent finding of the same defect counts as
genuine corroboration under the two-refuter rule rather than an echo. Disposition
is recorded in the refuter synthesis record.
