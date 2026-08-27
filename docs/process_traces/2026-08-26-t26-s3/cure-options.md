# Cure options and tradeoffs

The immutable constraint is decisive: no sound cure may edit any existing
`configs/campaigns/d117_*_v{1,2,3}/` byte, rewrite a minted receipt, or require
re-minting. The imminent `_v4` sequence must remain U11 projection → generic
evidence authoring → sacrificial preflight → freeze-0004 mint → successor
pinset.

## A93 — stale receipt constant

| Candidate | Files touched by implementation | Frozen bytes / minted receipt impact | New family generation? | `_v4` sequence | New proof |
|---|---|---|---:|---|---|
| Refresh every current generator constant after mint | Nine existing generators and their plan trees/sidecars; receipts/pinsets would also need repair | Changes frozen pack bytes and direct `_v2`/`_v3` generator pins; circular because the receipt digest changes when plan bytes change | **Yes** under D-153 | Breaks §3.6; post-mint edit/remint required | Only makes default-mode selection agree with one receipt; does not cure echo tautology |
| Teach successor emission to substitute the constant | Generator templates and generator regressions | Existing generations cannot be retrofitted; a successor emitted before its own receipt exists cannot embed that future digest | Future-only, and still needs a post-mint repair protocol | Does not solve imminent `_v4` post-mint state | Detects nothing; merely moves the stale point |
| Lead sketch: AST-parse pinned source and hard-refuse when constant is stale and pack is frozen | `arm_readiness_evidence.py`, tests; possibly source/check schema consumers | No old-byte edit if consumer-only | No | **Fails operationally:** at §3.4 there is no current receipt to compare; after §3.6 it would refuse every `_v2`/`_v3` and `_v4` | Detects stale relation, but turns an irrelevant legacy constant into a new authentication dependency |
| External current-receipt mapping/sidecar | New registry/sidecar, loader, tests, docs | Old packs untouched, but introduces an unsigned or separately pinned authority surface | No if separately governed | Adds a new pre-arm transaction dependency | Proves mapping consistency only; redundant with authenticated plan tree |
| **Stop depending on the constant; AST-record it as diagnostic** | `joulewise/arm_readiness_evidence.py`, historical-consumption verifier in `joulewise/arm_readiness.py`, focused tests | No pack/receipt rewrite; frozen source remains readable | **No** | **Unchanged** | Proves auth used an explicit regeneration-capable historical/pre-projection lane; separately records `matches_current`, `names_predecessor`, `absent`, or `no_current_receipt` with `authentication_dependency=false` |

The lead's parse-never-exec instinct is right, but hard refusal is the wrong
use of the parsed value. It is temporally incapable of detecting `_v4` staleness
at authoring (freeze receipt absent) and becomes a mass false refusal after the
mint. The constant should be observable but non-authoritative. New/current
generator invocations should request `--no-preserve-current-frozen-bytes`
explicitly; legacy anchors that predate the flag must first be AST-classified
as having neither a preserve branch nor a current receipt.

## A94 — preserve echo tautology

| Candidate | Files touched by implementation | Frozen bytes / minted receipt impact | New family generation? | `_v4` sequence | New proof |
|---|---|---|---:|---|---|
| Remove echo and regenerate a current frozen pack in place | All family generators and likely generated pack bytes/pins | Direct frozen-byte change; pinned inputs have changed since original generation | **Yes** | Breaks the sequence and may alter science identity | Genuine current derivation, but only by creating a different generation |
| Keep echo and add `derivation_mode: echo` everywhere | Evidence author/consumer, exact-key predicate, registries, schemas, all D3 docs/gates | Adding a required fact key invalidates old receipts; an optional consumer overlay can avoid that | No with overlay | Can remain unchanged | Proves only echo integrity and inventory/freeze binding; honestly abandons regeneration |
| Lead sketch: search history for a pre-freeze regeneration ancestor, replay it, then fence licensed additions | Evidence author/consumer, Git materializer, tests, docs | No old-byte edit | No | Unchanged | Genuine historical regeneration plus custody composition; sound but search introduces ambiguity needlessly |
| **Use the commit already authenticated in the PACK_AUTH source/receipt, replay it, and compose with existing histsem K5/K12/K7** | `joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence.py`, focused tests; no generator/config edits | No old-byte or receipt-schema change | **No** | **Unchanged** | Genuine pre-freeze generator derivation at an exact recorded coordinate; exact historical digest; current digest; source/receipt/freeze/plan binding; closed licensed delta |
| Add a normalized `plan_tree` digest to future freeze/projection schema (WO-L5-2) | Receipt schema/validator, identity projection, mint, runsheet, tests, every future pack | Cannot retrofit v1-v3; changes `_v4` receipt bytes/schema and transaction assumptions | Not inherently, but choosing it now requires D-153 magistrate ruling | Materially changes §3.2/§3.6 and must not be smuggled into this cure | Stronger future plan binding, but does not itself prove generator derivation |
| Use only the S5 table/current pinset | Histsem verifier/tests | No frozen edit | No | Unchanged | Strong current-byte identity, but no generator derivation; useful composition limb, not a complete cure |
| Compare a temporary echo to current pack | None beyond current behavior | None | No | Unchanged | Nothing non-tautological; reject |

The recorded-anchor option is strictly cheaper and more determinate than
history search. The three ordinal-1 source receipts already name the exact
pre-freeze commits, and executed replay shows those generators had no echo path
and reproduce the recorded pack digests. The existing receipt-historical-
semantics machinery already supplies the second half of the proof. Generalize
that composition instead of inventing a second lineage protocol.

## Recommended combined shape

Authentication becomes a two-coordinate statement:

1. **DERIVATION coordinate:** the authenticated source/receipt commit, with no
   current D-134 receipt; run the pinned historical generator. Use explicit
   no-preserve when the historical CLI supports it, or admit a legacy bare call
   only when AST proves no preserve mechanism existed.
2. **CUSTODY coordinate:** authenticate the current committed pack with existing
   histsem K12, exact source/receipt/freeze/plan bindings, and the closed
   historical-to-current delta. For U11-projected new evidence, retain the
   already-landed projection-anchor replay.
3. **DIAGNOSTIC:** AST-parse the current committed generator's receipt constant
   and record its relation to the authenticated current/predecessor receipt.
   Stale is a detected compatibility fact, never a derivation input.
4. **ECHO:** preserve-mode CLI output is classified as `echo_integrity`; it may
   support inventory and freeze-binding diagnostics but may never set or renew
   `pack_generator_check_status=PASS` by itself.

This shape changes neither minted bytes nor receipt schema and therefore does
not trigger the D-153 new-generation consequence. No `lead_ruling` is needed
for the recommended path. Choosing the WO-L5-2 schema path or any generator
rewrite would require that ruling.

