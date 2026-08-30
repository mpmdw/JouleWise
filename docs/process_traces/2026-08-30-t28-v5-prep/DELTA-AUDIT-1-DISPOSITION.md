# `_v5` prep — delta re-audit 1: magistrate disposition (Fable, 2026-08-30)

Auditor: fresh Sol xhigh, read-only, over `596a7b42..2b0c0aaa` only; custodied
as `02-delta-audit-1-sol-xhigh.md`. Verdicts: D-1 INSTALLED, F2-guard
INSTALLED, D-2/F2-primary DAMAGED (F1), D-3 PARTIAL (F4), D-4 PARTIAL (F3).
The re-audit found exactly the class of defect it exists to find: the fix
round introduced a one-pin bypass and blessed it with a test.

## E-1. F1 (blocker) — ACCEPTED; both-or-neither RULED

The two identity pins are one identity. RULED invariant, enforced at schema
validation: a ModelConfig carries BOTH `tokenizer_json_sha256` and
`chat_template_sha256` or NEITHER; one-pin configs refuse with a named
SchemaError. The runtime keeps its per-pin checks (they now can only run as a
pair). The template-only blessing test becomes the refusal regression; add a
paired-pins happy-path test that verifies BOTH hash checks execute (the
auditor's raise-if-called probe shape).

## E-2. F2 (should-fix) — ACCEPTED

Propagate the two field names to `joulewise/publication_privacy.py`'s closed
model allowlist (a `_v5` config must survive the privacy classifier) and
regenerate `tests/goldens/config_schema.json` by the documented schema-diff
route. No other golden changes bytes (auditor-verified); if one does, stop
and report it.

## E-3. F3 (should-fix) — ACCEPTED with a STRUCTURAL cure, not a third mirror

Two rounds have now approximated the production window predicate by hand
(absent, then weaker). Per the standing escalation doctrine the next spend is
a formulation change: the replay helper IMPORTS and calls the production
predicate itself — `_common_mode_window_is_strictly_noncollapsed`
(`joulewise/floor_extraction.py:362`) — plus the same pre-arithmetic type
strictness (no bool/str coercion), so the accepted-input set is the
production set by construction. The frozen module is imported, never edited.
Add the auditor's `nextafter(2*b, +inf)` counterexample as a regression that
must REFUSE. If the private-name import is judged too fragile, the
alternative is a test that asserts replay-fence and production-predicate
agreement across a boundary-value sweep including the counterexample — but
the import is preferred. If the fence defect survives a THIRD audit, a cold
instance rules before any further round (no discretion).

## E-4. F4 (should-fix) — ALREADY CURED ON MAIN; rebase

The binding decision-log amendment landed on main 2026-08-30 (`7294cb8f`,
"D-165 R-5 completed"): absolute R_cm `not_applicable` with the cancellation
reason; comparative R_cm mandatory with the `< 2` withdrawal; route (ii)
recorded. The branch predates it. FIX: rebase the branch onto current main;
verify the amendment text renders the auditor's cited lines
(`docs/decision_log.md` D-165 body) non-contradictory; no new edit expected.

## E-5. F5 (should-fix) — ACCEPTED; new refusal class RULED

`RUNTIME_UNAVAILABLE` misclassifies an identity mismatch as an unsupported
runtime in campaign records. RULED: add
`MODEL_IDENTITY_MISMATCH = "model_identity_mismatch"` to `FailureReason`,
used by all pin-refusal branches (missing pinned file included), propagated
to every closed consumer vocabulary with tests. New enum values extend the
wire vocabulary without rewriting historical bytes; if any consumer's closed
vocabulary is FROZEN on the evidence side such that extension would break
validation of retained artifacts, do not extend it — early-return
NEEDS_RULING naming the consumer.

## E-6. TOCTOU residual — recorded, not fixed

Mutation of the mirror between hash check and `mlx_lm.load` remains possible.
Single-operator accident within one member-preparation window is the only
actor; D-161 classes this as not worth a mechanism. Recorded in the campaign
pack doc as a known limitation, one sentence.

## Round shape

Fix round 2 (Sol high) implements E-1, E-2, E-3, E-5 and the E-4 rebase;
then DELTA RE-AUDIT 2 (fresh read-only Sol xhigh) over the round-2 diff.
Merge only after a clean delta re-audit 2 and green CI.
