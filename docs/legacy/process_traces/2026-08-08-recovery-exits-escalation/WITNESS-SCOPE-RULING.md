# Witness-scope ruling (magistrate, 2026-08-08) — the 71-code census

Context: the witness-completion round's census found 71 registered
RefusalCodes, 4 executed durable witnesses, 67 missing; five codes
judged unconstructible under a conservative reading of the
no-internal-injection rule; and the round-1 exact-set gate FALSELY
deriving coverage from witness_id strings (the exact "stable proof_id
alone is not evidence" defect the consult named). The round correctly
made NO changes and early-returned.

## Ruling (interprets the adopted exit-completeness design; does not amend its bar)

1. **Durable-file corruption is legitimate witness construction.** The
   adopted design's witness rule forbids monkeypatching and
   internal-process-state injection; it does NOT forbid constructing
   HOSTILE DURABLE STATE by writing bytes to the ledger/custody files —
   that is the same class as the crash matrix's torn-write
   construction, and the design's own exit-family table lists
   corruption-reached states (malformed ledger, nonconvergent
   recovery) as witnessable hard-stop families.
2. **The registry gains a `witness_class` field** (a schema completion
   in the design's spirit — it already carries per-code reachability
   metadata):
   - `operational` (default): raisable via governed public operations
     and/or crashes — EXECUTED durable public-CLI witness REQUIRED.
   - `corruption_backstop`: raisable only via corrupted/hostile durable
     state — executed witness REQUIRED, constructed via direct
     durable-file corruption (never process patching).
   - `internal_invariant`: guards a programming error with NO durable
     raising state (e.g. a missing in-memory argument). Exempt from
     the executed-witness requirement; REQUIRED instead: a focused
     unit test proving the raise path, registry metadata naming why no
     durable state exists, and exclusion from operator-facing §10 rows
     (these are not operator exits).
   The exact-set gates check equality PER CLASS; reclassifying a code
   to a weaker class is a registry change a delta must always see.
3. **The five contested codes:** `calibration_ledger_snapshot_required`
   → internal_invariant (in-memory argument guard).
   `calibration_intent_target_malformed`,
   `calibration_recovery_nonconvergent`, `calibration_abandon_not_clean`
   → corruption_backstop (construct the malformed/nonconvergent/
   unclean durable bytes directly). `calibration_ledger_bracket_slot_
   claimed` → implementer classifies per the definitions above and
   reports: if no durable byte-state can reach it even by corruption,
   it is internal_invariant; if corruption reaches it, backstop.
4. **The gate is tightened to EXECUTED-witness equality** per class
   (discovered, run, terminal-result-asserted) — witness_id strings
   prove nothing. Witnesses use ONE parameterized harness (constructor
   + expected code + mapped exit + declared terminal result per row),
   not 60+ bespoke ceremonies.
5. The remaining ~62 constructible codes ALL get executed witnesses.
   No sampling, no families-as-proxies: the consult's bar stands.

Arming blocker: stays OPEN until the per-class census is exact-equal
and green, then the gauntlet + merge.
