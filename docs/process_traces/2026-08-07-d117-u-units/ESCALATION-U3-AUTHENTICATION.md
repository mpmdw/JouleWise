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
