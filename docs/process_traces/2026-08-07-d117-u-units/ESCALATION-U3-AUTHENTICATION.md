# ESCALATION TRIGGER FIRED — U3 postcollection authentication (2026-08-07)

**Status: the v2 generalized mint is BARRED from issuing any artifact
until this closes. Recorded on main so no successor can miss it.**

## The finding (lead-verified independently)

The v2 mint authenticates every pinned custody value against
`component.report["floor_mint_postcollection"]`
(`scripts/mint_floor_artifact_generalized.py:1715,1722,1742`).

**Nothing in the repository produces that block.** `grep` over
`joulewise/` and `scripts/` finds three READ sites and zero writers;
`floor_extraction.py` does not emit it; no design document specifies it;
no chartered work order — including U10 — owns it. The only writer is the
test fixture. And the v1 core's report check does not close the report's
key set, so the block is an accepted free extra key whose numbers AND
whose hash pin would be authored by the same operator running the mint.

**Therefore the self-attestation defect was RELOCATED one level down, not
eliminated.** The equality checks are real; the thing they compare
against is not independently produced.

## Why this is an escalation, not another fix round

Occurrence count for the self-attestation / presence-only class:
1. Original U3 contract audit — CRITICAL, live-proved (fabricated custody
   hashes with tampered drift/allowance still minted).
2. Delta-1 — class SURVIVES as "presence-only authentication".
3. This post-merge Opus counter-review — class survives as
   "authenticated against a block nobody produces".

Delta-2 returned CLEAN. **It was wrong, and the magistrate accepted it.**
Delta-1 had named the gap precisely; the trigger was met and missed. That
is recorded here as a lead error, not smoothed over.

Rule 11's standing trigger and D-118 item 5 both bind: two consecutive
rounds failing with the same signature means the next spend is a
CONSULT. A third fix round is forbidden.

## Disposition

- **BARRED:** the v2 mint must not issue an artifact until the consult's
  adopted shape lands and a fresh delta accepts it. This costs nothing
  today — no D-117 window has been collected, so no mint is due.
- **NOT unsafe as merged:** the path fails closed. It cannot produce a
  FALSE artifact because it currently cannot produce one at all in
  production (no producer for the block it requires).
- **Consult charge:** what SHOULD authenticate postcollection custody
  evidence; who produces it; is emitting it an extractor obligation
  (U10 scope or a new unit); and can the trust root be placed outside
  the mint operator's reach at all on this system — if not, say so, and
  the paper's custody claims narrow accordingly.

---
# CONSULT RETURNED — SHAPE ADOPTED (magistrate, 2026-08-07)

Full memo: `ESCALATION-CONSULT-RESPONSE.md`. Adopted as the binding
design. It terminates the relocation chain rather than moving it again.

## The adopted shape

**Delete the intermediate document.** `floor_mint_postcollection` is
removed from production AND fixture vocabulary; a D-117 report containing
it must REFUSE as an unknown top-level key. There is no new summary
artifact for anyone to author — that is precisely why the class dies
here instead of relocating a fourth time.

**Each pinned value is REDERIVED from its DOMAIN OWNER**, not read from a
sibling summary: receipts, terminal head and bracket binding come from
the ledger/bracketing domain; cell values come from governed extraction;
six-decimal strings are recomputed as the `.6f` rendering of the verified
full-precision values and compared against the independently frozen
pins. Missing pins refuse; no fallback generation is permitted.

**Rejected alternatives (recorded):** a new local emitter — "an emitter
trusted without rederivation repeats the defect; an emitter whose
results are fully rederived by the mint is redundant." The verdict path
cannot own extraction results that do not yet exist.

## Ownership: a NEW pre-window work order, not U10

`D117-POSTCOLLECTION-TRUST-01`. U10 is a data-finalization unit whose
authorized files are final pinsets and the minted artifact; it cannot
repair producer/consumer semantics without violating its own scope. The
new order is an amendment to the extraction and mint contracts and a
DEPENDENCY of U10. **It must land before any D-117 arm is treated as
mint-ready.** Surface includes `joulewise/floor_extraction.py`,
`joulewise/calibration_bracketing.py`, the generalized mint, and
`tests/test_floor_extraction.py`.

## Relocation checklist (the consult's own test — apply at the next delta)

Ask, every time: does the mint REDERIVE the value, or merely compare two
sibling operator-authored documents? Can the attack succeed by editing
one document plus its own hash? Does any free extra report key become
authority? Does the PRODUCTION CLI — not a fixture builder — exercise the
claimed path? If authority has relocated into another locally authored
summary, the class survived.

## Assurance vocabulary (adopted for artifact AND paper)

The artifact carries an explicit assurance profile naming what it does
and does not establish. Adopted paper language, sharper than the
magistrate's earlier framing and superseding it:

> JouleWise provides single-authority, hash-bound custody. The tools
> rederive hashes and refuse omissions, substitutions, stale inputs, and
> rollback relative to retained commitments. These controls do not prove
> that the experimenter who controls the laptop, repository, and archive
> did not fabricate or coordinately rewrite them before publication; the
> present system has no independent signer, external timestamp, or
> write-once log.

Also adopted: "immutable corpus" becomes "write-once-by-tool, hash-bound,
backed-up corpus"; "tamper-evident" always means "tamper-evident relative
to disclosed or independently retained digests"; §11 states the claims
are "experimenter-verified, fail-closed, and independently reproducible
from released evidence; not independently authenticated against a
malicious experimenter."
