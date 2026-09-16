# 13 — Magistrate synthesis of cold-gate ruling 10 (packet 06) with the Opus pairing refuter (12), 2026-09-15 21:35 PDT

Both seats ruled independently on the same packet; both AMEND the round-6 F2 dictation and agree on F1, F3, the stop
condition and the need for a real-signal execution lens. Synthesis (binding for round 6b):

**Q1 / F2 — ADOPT ruling 10's dictation in full**: (a) entry mask captured at `run()`/`uninstall()` entry, `__init__`
default kept, no recapture in `_install_handlers`; (b-amended) the handler raises AT MOST ONCE (`raised_once`, decided
inside the handler after its `SIG_BLOCK`), `_unwind`'s block is a `while True: try: SIG_BLOCK; break; except Signalled:
continue` (no call precedes the `try`); (c) `uninstall()` blocks BEFORE installing handlers; (d) restore in the `finally`;
(e) `run()` gains the outer `except Signalled` with the `resolved` flag exactly as ruling 10 prints it. PLUS the pairing
refuter's (d-amended), which ruling 10 did not address and which is a real hole: restore dispositions BEFORE the mask —
`SIG_IGN` all (discards pending) → re-install the saved dispositions → `SIG_SETMASK(entry_mask)` LAST — in both `_unwind`
and `uninstall()`'s `finally`. The pairing refuter's `_run_guarded` rename is NOT adopted (ruling 10's nested try is the
same structure without the rename). Regressions: D's (i)–(iv) + ruling 10's (v)(vi)(vii) + one for the restore order
(a signal delivered between the unblock and the disposition re-install must not escape). Must-die as ruling 10 lists,
plus revert the restore order → RED.

**Q2 / F1 — ADOPT both**: shell `[[ -n "$2" ]] || usage` in every valued case; forward `--render-only` (and every valued
option) by a `_given` flag, never by non-emptiness; module `--render-only` becomes a custom argparse type that raises
`ArgumentTypeError` on empty (exit 2); tests: exit 2, usage line, empty fake-launchctl log, nothing written.

**Q3 — ADOPT**: round 6 is the LAST same-shape round. STOP CONDITION: any further signal-class defect in the delta on
round 6 (teardown skipped, mask left blocked, a handler raise escaping `run()`/`uninstall()`) → NO round 7 → blind
three-seat redesign consult on record-and-poll (handler only blocks + records; `run()` polls at state boundaries).

**Q4 — ADOPT**: F3 folded in-round, with the pairing refuter's added sentence on the retained sidecar making the next
install refuse with exit 3.

**Q5 — ADOPT**: NOT landable until a fresh execution-lens seat drives REAL signals deterministically at every seam
(i)–(vii) plus `uninstall()`, under BOTH python3 3.14 and /usr/bin/python3 3.9, and runs the F1 shell cells; then a
clean delta re-audit and the lead's full-suite replay at the final head.

Dissent: none. The round-6 seat launched under exhibit D is allowed to finish (its F1/F3 work and tests stand); round 6b
applies this synthesis on top of it.
