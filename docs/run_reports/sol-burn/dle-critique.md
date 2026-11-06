# Methodological critique of DLE-0 through DLE-5

2026-11-06. This is a document-only, repository-only review. I opened no experiment-data path and ran no
experiment. The object reviewed is the six draft entries in the care audit, not whether the underlying engineering
ideas are useful.

## Standard of review

A skeptical empirical-systems reviewer should accept a deviation as *principled and blind* only when (1) its scope
and trigger were fixed before outcome access, (2) it preserves the preregistered estimand and refusal semantics, (3)
it replaces the removed check with a check of the same failure class, and (4) the replacement has a prospective,
falsifiable pass/fail rule. The drafts have a useful global attestation: the signer must restate that release has not
happened and that they have seen no energy or outcome.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L241-L247】
That attestation is necessary but not sufficient: a blind change can still weaken validation in a way that favors
clean-looking results.

The central distinction is explicit in the implementation and audit. The lean program treats selection, anchors,
timing bounds, and calibration fits as input judgments rather than deriving them.【F:scripts/independent_recompute_b5.py†L2-L6】
The audit likewise says that the lean path does not re-derive member selection, clock anchors, timing bounds, or
calibration fits, whereas the heavy path re-derives them from bytes.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L141-L143】
Therefore agreement between lean and heavy arithmetic is not evidence that those shared input judgments were
correct. Hashes establish identity, not correctness of the first derivation.

## What each path can detect

| Failure class | Lean recompute | Heavy re-derivation | Proposed heavy audit |
|---|---|---|---|
| Raw-trace energy/statistical arithmetic defect | Yes, independently; the comparison requires every family to agree and zero fields to be unmapped.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L177-L188】 | Yes | Yes, if the audit compares all registered families under the already-fixed bars. |
| Changed custody bytes | Yes, through the census/hash bindings assumed by the design.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L198-L200】 | Yes | Yes, provided it starts from the authenticated raw roots rather than lean-produced intermediates. |
| Incorrect stored clock anchor or timing bound | **No**: these are input judgments.【F:scripts/independent_recompute_b5.py†L2-L6】 | Yes: strict step 1 re-derives clock anchors and environment refusals.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L64-L65】 | Only if strict validation remains enabled and its refusals are compared, not merely the final numeric families. |
| Incorrect stored pulse/calibration fit | **No**: the lean calibration reader consumes stored `b_fiducial_s` values, then checks bracket arithmetic around them.【F:scripts/independent_recompute_b5.py†L812-L855】 | Yes, when candidate physics is refit from capture bytes.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L66-L66】 | Only if candidate refitting remains in the audit and is not itself replaced by hash binding. |
| Stale or incorrectly derived whole-window verdict / environmental refusal | Not comprehensively: the lean path trusts several collection-time judgments, even though it independently re-derives exclusions.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L138-L143】 | Yes; the heavy consumers re-derive the whole-window verdict, and strict validation includes environmental refusals.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L65-L70】 | Only if those checks remain active and audit refusal codes are release-relevant. |
| Host-load-dependent wall deadline | Not applicable; the lean path does not refit.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L72-L72】 | Yes under the old path, but this is nondeterministic operational behavior rather than evidence correctness. | No after DLE-5; that is intentional, but a deterministic resource bound must remain. |

The proposed audit is currently underspecified. It is said to run once per block, *after* the lean result and off the
critical path, while disagreement holds release.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L201-L205】 A run cannot
both be non-gating in schedule and reliably protect a release unless it has a completion deadline before release (or
the paper/publication event), and unless strict refusals—not just numeric comparator families—are part of its
disagreement surface.

## Entry-by-entry judgments

### DLE-0 — replace the results cold gate

**Judgment: not acceptable as written; acceptable after narrowing and adding an independent semantic review.** The
draft replaces a judge-plus-refuter with numeric agreement and justifies this by saying the recompute derives every
printed number in separate code.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L249-L255】 That supports arithmetic
replication, but it does not replace the epistemic role of a human refuter: checking completeness, interpretation,
threshold wording, provenance, or a shared bad stored judgment. The lean program itself labels its tolerance rules
as agreement checks rather than acceptance gates.【F:scripts/independent_recompute_b5.py†L8-L16】

**Required wording/safeguards.** State that the automated comparison replaces only the cold gate's *numeric
recalculation* function. Retain a blinded refuter who receives structure-only records and must attest: zero unmapped
registered fields; all refusal codes and threshold words accounted for; no comparator-family or bar changes; and
paper statements drawn only from the registered output schema. Require the fixed bar-set identifier; the checked-in
bar file says it was fixed before real block-5 values and not widened.【F:configs/analysis/b5/recompute_bars.json†L1-L5】
If the original cold gate had broader duties, enumerate them and map each to a surviving safeguard rather than claim
that “every printed number” exhausts the gate.

### DLE-1 — replace the post-release heavy replay

**Judgment: conditionally acceptable for determinism/custody, but not with an optional heavy audit.** Rechecking
recorded digests is a principled replacement for detecting alteration of already-produced bytes, and independent
recomputation is more informative than replay for arithmetic defects. But the draft makes the heavy run optional
while the lean program cannot expose a wrong stored anchor, timing judgment, fit, or verdict.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L258-L268】
Also, “after the release” and “agreement is the release condition” are temporally inconsistent as drafted: a
condition cannot hold an event that has already happened.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L261-L265】

**Required wording/safeguards.** Define two events: an outcome-unblinding event and a public/claim release event.
Run digest verification plus lean comparison after the former and before the latter. Make the heavy strict audit
mandatory before public release for block 5, or explicitly carry a preregistered “provisional pending heavy audit”
label. Require the audit to begin from authenticated raw bytes, re-derive input judgments, compare strict refusal
sets as well as numbers, and hold release on failure, non-completion, or disagreement. Preserve the already-fixed
zero-unmapped rule.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L181-L190】

### DLE-2 — lean production path for blocks 6+

**Judgment: plausible prospective design, not yet acceptable as a signed deviation.** It is genuinely prospective
for later blocks and explicitly preserves registered arithmetic, but the rationale overclaims that deterministic
re-derivation protects against nothing beyond hashing.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L272-L286】
Re-derivation detects an incorrect first computation on unchanged bytes; hashing cannot. The proposed audit does
catch this *only if* it remains independent, strict, mandatory, and timely. Running it after the lean result is not
a blindness problem if outputs remain inaccessible, but “off the critical path” creates a completion loophole.

**Required wording/safeguards.** Replace the quoted rationale with: “Hash binding prevents substitution; the
mandatory heavy audit tests correctness of the stored input judgments.” Require successful block-5 and first
block-6 concordance, already proposed by the audit.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L192-L205】 Freeze
the lean commit, schema, member-pool determinism, bars, threshold-tie policy, and disagreement adjudication before
block 6. Specify that heavy audit non-completion is disagreement, that its strict/refit checks cannot consume
lean-derived anchors or fits, and that both numeric differences and refusal-set differences hold release.

### DLE-3 — replace step-1 strict re-validation with hash binding

**Judgment: not acceptable as written.** The draft removes anchor LP, fit-physics, and environment-refusal
re-derivation and moves them to an unspecified audit run.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L288-L295】
This is exactly the domain where identity is not correctness. The audit records that the original rule arose from a
P0 involving stale calibration relabelled fresh, which makes a bare hash argument especially weak.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L91-L96】
The phrase “one reduction per bundle” is also ambiguous: it does not say whether that reduction independently
recomputes anchors, fits, and all environment refusals.

**Required wording/safeguards.** Enumerate fields trusted by hash and fields re-derived. Keep at least one strict
raw-byte re-derivation per unique bundle before claim release, either in production or in a mandatory heavy audit;
make any missing audit result a hold. Compare the complete strict refusal set and derived input-judgment digests,
not only final paper numbers. State that the optimization removes duplicate derivations, not the last independent
derivation. If the intent really is zero pre-release re-derivation, label the resulting risk explicitly and do not
claim equivalence to D-078.

### DLE-4 — calibration candidate verification

**Judgment: reject because it is not a single deviation; the memo alternative is acceptable, hash-only is not.** A
signed deviation cannot contain “memoize, **or** trust the recorded fit”: those choices remove different safeguards
and save different amounts.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L297-L305】 Run-scoped memoization by
distinct capture digest preserves one raw-byte physics refit and removes duplicate work. Hash binding removes the
only check that the stored fit was computed correctly. The heavy audit would catch that only if DLE-4 does not also
remove its refit.

**Required wording/safeguards.** Choose the memo alternative: census unique capture digests, refit each exactly once,
cache only successful complete results, and fail closed on digest collision/mismatch, partial computation, or
different governing code identity. Record cache hit/miss counts structure-only. Rebind the seal pin prospectively as
the draft already notes.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L301-L304】 If hash-only is desired later,
write a separate DLE requiring a mandatory raw-byte refit audit before release and explicitly acknowledge that the
production path no longer detects an erroneous collection-time fit.

### DLE-5 — remove the analysis-path wall deadline

**Judgment: acceptable in principle, with stronger operational and semantic bounds.** Removing a host-load-dependent
deadline improves reproducibility; the audit documents that a firing can change uncertainty/envelope availability
and that forced-deadline handling previously let four changed keys slip through.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L72-L72】
The draft appropriately keeps a reproducible cell budget and requires a new calibration identity.【F:docs/run_reports/2026-11-06-b5-care-audit.md†L309-L318】
However, “no estimand change” is too absolute: for executions that formerly refused, the set of admitted outputs
changes. That is a refusal/admissibility change even if the mathematical estimand conditional on completion is the
same.

**Required wording/safeguards.** Say: “The mathematical estimator is unchanged; the operational refusal rule is
prospectively changed so host load cannot select whether an estimate exists.” Define the deterministic cell budget,
prove that exceeding it always refuses without partial output, retain an outer operator watchdog that cannot admit
results, reissue every governed digest/acceptance before use, and add synthetic tests for forced wall delay, cell
budget exhaustion, and byte-identical successful outputs with the wall observer enabled versus disabled. The heavy
audit need not reproduce the removed wall timeout; it must still reproduce the fit under the cell budget.

## Recommended disposition

| Entry | Disposition before signing |
|---|---|
| DLE-0 | Revise: automated numeric gate plus a scoped blinded semantic refuter. |
| DLE-1 | Revise: resolve release chronology and make strict heavy coverage mandatory or label results provisional. |
| DLE-2 | Revise and defer activation until the two prospective concordance gates pass. |
| DLE-3 | Reject as hash-only; accept only removal of duplicate work with one mandatory raw-byte strict derivation. |
| DLE-4 | Split alternatives; accept digest-keyed memoization, reject hash-only without mandatory refit audit. |
| DLE-5 | Accept prospectively after identity reissue, deterministic resource safeguards, and equivalence/refusal tests. |

The overarching repair is simple: do not describe hashes as substitutes for re-derivation. Use hashes for identity,
the lean path for independent arithmetic, and one mandatory heavy raw-byte audit for the collection-time judgments
the lean path deliberately cannot test.
