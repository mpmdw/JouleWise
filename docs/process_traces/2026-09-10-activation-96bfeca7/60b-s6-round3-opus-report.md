# Seat S6 — fix round 3 (Opus) — contract docs for F2 / F3

Worktree: `/Users/edr/code/JouleWise-wt-s6-docs-prereg`, branch
`feat/2026-09-10-epoch-s6-docs-prereg`, base HEAD `39e813ff`. Diff left
uncommitted in the working tree. WRITE_SCOPE respected: only
`docs/contracts/calibration_ledger.md` and
`docs/contracts/powermetrics_fiducial.md` touched (`git diff --stat`:
2 files, +41 -1 before reflow; +41 -1 after).

## F2 — receipt encoding of the session kind

`docs/contracts/calibration_ledger.md:68-77` (inside the **Session kinds**
paragraph, under the section's unchanged "Ruled by cold gate 46 ... NOT YET
LANDED" status line). Added the ruled sentences verbatim:

> A bracket session records no `session_kind` and no `declared_slots`; the
> absence of both fields IS the bracket kind, which is why every receipt
> written before derivation kinds existed reads back unchanged. An explicit
> `session_kind: "bracket"` in an open receipt refuses, so one session shape
> has exactly one byte representation. A derivation session records both
> fields.

plus one sentence separating the receipt surface from the CLI surface (F1's
tension): the reservation tool run without `--execute` — glossed at first use
as a dry run that validates inputs and writes nothing — prints a JSON summary
rather than a receipt, and that summary reports `session_kind` and
`declared_slots` explicitly for BOTH kinds
(`reserve_calibration_window_bracket.py:243-244`). The following clause was
re-anchored from "It opens at head-equals-pin" to "A derivation session opens
at head-equals-pin" so the referent survives the insertion, and the paragraph
was reflowed.

## F3 — the three implemented refusals, each built at first use

(b) `docs/contracts/calibration_ledger.md:90-98`, new paragraph
**"Recovery finalizes a declared slot, never a free string."** — placed in the
ledger contract because declared slot lists are kind-agnostic session
mechanism, not derivation-only mechanism. States the forcing problem (slot
names are no longer the fixed `pre`/`post` pair, so argparse cannot enumerate
them), the mechanism (the tool reads the ordered list from the session's open
receipt), and the refusal by name: `RESERVED_SLOT_MISMATCH`, reason
`slot_not_declared`, carrying the offered slot and the declared list.
Source: `recover_calibration_ledger.py:237-256`, wired at `:395, :449, :489`.

(a) `docs/contracts/powermetrics_fiducial.md:143-151`, new paragraph on the
bidirectional screen/kind check. Both directions are given their own physical
reason: derivation-kind WITH a screen refuses because the retired epoch's
threshold must not judge a new-epoch capture; bracket-kind with NO screen
refuses because an ordinary capture that skipped the comparison would be
recorded `valid` without ever having been tested. Names
`systematic_screen_kind_mismatch` and notes the refusal carries the session
kind. Source: `calibration_ledger.py:5477-5487`.

(c) `docs/contracts/powermetrics_fiducial.md:153-162`, new paragraph on CH-1
ordering. "Unauthenticatable" is glossed at first use (bytes missing or not
matching the pinned SHA-256, so no `preflight_level_screen_s` can be derived),
then the refusal `FROZEN_PROTOCOL_INVALID` (reason
`acceptance_artifact_underivable`) is stated as firing BEFORE the ledger path
is opened, including on a derivation resume-finalize that will not consult the
screen at all, with the reason the ordering matters (an artifact fault is
never surfaced later as a ledger fault). Source:
`recover_calibration_ledger.py:479-496`.

Both sections keep their existing status lines unchanged: ruled by cold gate
46 + addendum 11, NOT YET LANDED until S1-S4 land.

## Tests

`python3 -m unittest tests.test_docs_freshness tests.test_gen_state`
→ **RC=0**, 75 tests, OK (rc captured in a shell variable; run twice, once
after the reflow pass).
