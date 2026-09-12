# COLD-GATE RULING — WO-MINT-ESTIMATOR-VOCAB F1 seam question

Cold Fable adjudicator, fresh session, no loop context. Ruled 2026-08-11 on the mechanically
assembled packet (`coldgate-mintvocab-packet.md`) plus direct read-only verification of the cited
primary sources in the branch worktree
(`wtE-mintvocab @ cbf609f`, uncommitted tree as inventoried in packet §8):
`joulewise/floor_mint_estimator.py` (complete), the full working-tree diff of
`scripts/mint_floor_artifact_generalized.py`, and the pinned
`scripts/mint_floor_artifact.py:1750-1946` (`bind_floor_artifact_evidence`, complete) and
`:755-779` / `:1049-1113`. No deference is owed or given to the provisional magistrate ruling;
where I affirm its direction I do so on independently verified grounds, and I find its condition
set insufficient (Q2).

---

## Q1 — Does option A preserve the contract's integrity guarantees?

**RULING: YES as a design — option A is AUTHORIZED — but the implementation currently in the
worktree does not yet satisfy it. It contains one concrete fail-open at the evidence-binding
site, which must be cured under the conditions in Q2 before any merge.**

**Why relocation does not inherently weaken the trust surface.** The check being relocated
(`_verify_report_widths`, pinned core :755-779) is not member-byte authentication — it is an
*estimator-arithmetic* equality: it compares the report's cached `admissible_half_widths_j`
against a reconstruction that hard-codes the default estimator's shape
(`sum of four anchor bounds / 2`, pinned core :713-752). For a spec-registered common-mode cell
that reconstruction is simply the wrong arithmetic — the packet's F1 evidence (registered width
0.10000000000071085 vs default-shaped 1.0) is the pinned core's *assumption* failing, not the
report lying. Every check that actually authenticates bytes — spec SHA, member identity/order,
bundle verification, semantics, producer pins — is untouched by option A. The seam
(`_authenticate_v2_component`, generalized mint diff) retains shape, length, and
finite/nonnegative validation at authentication time and replaces the elementwise equality with a
*strictly tighter* one (bit-exact `Decimal(str())` comparison vs the pinned
`math.isclose(rel=0, abs=0)`, which additionally distinguishes -0.0) whose expected side is
recomputed from authenticated members under the spec-selected estimator
(`recompute_comparative_estimate`). Fail-safe direction is correct at that site: if the runtime
substitution ever fails to take effect, the pinned check runs and *refuses* — the seam fails
closed, not open.

**The defect the packet's evidence does not surface but the cited code does.** In
`bind_v2_floor_artifact_evidence` (`joulewise/floor_mint_estimator.py:546-564`), the pinned
binder's refusal is swallowed on the common-mode path by **suffix-matching the error message**:

```python
if path != _COMMON_MODE_PATH or not str(exc).endswith(
    "artifact widths differ from authenticated source bytes"
):
    raise
```

The pinned binder (`scripts/mint_floor_artifact.py:1808-1941`) iterates components in the fixed
order `("absolute", "comparative")` and raises this message as
`f"{root_id}: artifact widths differ from authenticated source bytes"` for **either** component.
An artifact whose **absolute** stored widths are tampered raises this message during the absolute
iteration — *before any comparative-component binder check has run* — and the suffix match
swallows it. Execution then proceeds: single-cell check passes, common-mode recomputation passes,
comparative widths match, and the function returns `_binding_result_from_provenance(artifact)` —
bundle hashes read from **admitted artifact JSON** that, on this abort path, were never verified
against evidence bytes (the verification at :1902-1906 runs per-component and the comparative
iteration never started). Net effect: a common-mode artifact with tampered absolute widths
**binds successfully**. That is a refusal surface failing open, in direct violation of the
standing law quoted to this gate, and the in-code comment asserting the message "is reached only
after plan, campaign, bundle, config, stack, semantics, and member-order checks have all passed"
is true only for the component that raised, not for components later in iteration order. The
mitigating facts — the v2 call site discards the binder's return value, and
`write_outputs_exclusive` runs only after binding — reduce but do not eliminate the exposure: the
binder is a defense-in-depth surface whose whole purpose is not trusting the upstream pipeline.

**Against the alternatives:** **B** (amend the pinned core) is categorically barred — the pinned
core must remain byte-identical (non-negotiable 4; contract §2 restatement; §5a sha evidence).
**C** (default-shaped widths in a registered report) fabricates admitted data that contradicts
the evidence-bound floor — the report's cached widths would no longer describe the arithmetic
that produced its floor value; it is the worst option on the table. **D** — see Q3. Option A is
the unique completion consistent with all standing law; the conflict itself is a contract-map
omission (the MAP §1 catalogued four default-only surfaces but missed the fifth inside
`_authenticate_component` at :1096-1113/:755), and the worker's NEEDS_RULING was the correct
move under the contract's own "NEEDS_RULING for anything it does not settle."

---

## Q2 — Are the five provisional conditions sufficient?

**RULING: NO.** Provisional conditions (1), (3), (4), (5) are affirmed; condition (2)
("preserve every non-width pinned-core check unweakened") states the right property but is not
executable and, as the Q1 finding shows, the current tree violates it in a way none of the five
conditions would catch. The binding condition set is replaced by the following. All are
merge-gating; none is advisory.

**C1 (affirms prov. 1).** `scripts/mint_floor_artifact.py` byte-identical at the final branch
head; its sha256 stated in the WO ledger entry and equal to main's
`bf628eed4386b69589c9498cd644c0b3b70513f991f5bb223c70d35f1ca55f5c` (packet §5a evidences this for
the current tree; it must be restated at final head).

**C2 (replaces prov. 2 with an executable form).** A refusal-parity regression suite proving
that, through `_authenticate_v2_component`, every pinned-core refusal class of
`_authenticate_component` reachable on the default path refuses identically to the pinned core:
invalid spec, member order/identity mismatch, width-shape mismatch, nonfinite width, semantics
mismatch, and a default-estimator report with one width perturbed by one ULP. Each case must
refuse with no output files.

**C3 (affirms and sharpens prov. 3).** The replacement width equality runs unconditionally for
every comparative cell at BOTH postcollection and evidence binding; is bit-exact (the
`Decimal(str())` form or stricter); and takes its expected side only from
`recompute_comparative_estimate` outputs derived from authenticated members and evidence bytes —
never from report or artifact JSON. Required tests: one-ULP downward-width attacks on the report
cache (postcollection site) and on the artifact widths (binding site), both refusing (D-118
invariant 14 instantiated at both new sites).

**C4 (affirms prov. 4).** Differential regression: default-path reports and default-only
fixtures authenticate and mint byte-identically to current pinned-core/v2 behavior (D-118
invariant 12).

**C5 (affirms prov. 5).** Cross-wiring refusals both ways: common-mode-shaped widths under a
default-selecting spec REFUSE; default-shaped widths under a common-mode-selecting spec REFUSE —
at each of the three sites per contract non-negotiable 5.

**C6 (NEW — cures the Q1 fail-open).** The binder swallow in `bind_v2_floor_artifact_evidence`
must match the pinned refusal message **exactly and in full**, including the **comparative**
component's `evidence_root_id` prefix — never `endswith`. Required regressions: (i) a
common-mode artifact with tampered ABSOLUTE stored widths REFUSES at binding — this test must be
demonstrated failing against the current worktree code before the fix; (ii) a common-mode
artifact with a tampered comparative `bundle_sha256s` entry or campaign log REFUSES at binding;
(iii) a multi-cell artifact through the v2 binder REFUSES (the `_stored_comparative_widths`
single-cell guard, pinned by test).

**C7 (NEW).** `_binding_result_from_provenance` — which sources bundle hashes from admitted
artifact JSON — is deleted, and the common-mode binding path returns no provenance-derived
substitute (return `None` or the verified result only). If any future caller needs the binder's
result on the common-mode path, the hashes must be re-derived from `_strict_bundle` verification,
never read from the artifact. A test must assert the v2 call site treats the binder as
refusal-only (return value unused).

**C8 (NEW — patch hygiene).** Regressions proving: `core._verify_report_widths` is the original
function object after `_authenticate_v2_component` returns AND after it raises; the deferral
wrapper leaves absolute-kind cells checked by the unmodified pinned function (absolute width
mismatch refuses identically through the seam); and no other attribute of the pinned module is
mutated by the seam (assert the module's `__dict__` delta is empty post-call).

**C9 (NEW).** No-output-on-refusal tests at each of the three sites — postcollection,
construction, binding (D-118 invariant 13 instantiated). The current ordering
(`write_outputs_exclusive` after binding) supports this; pin it with a test.

**C10.** The full D-118 gauntlet invariants 1–15 as enumerated in the contract remain owed
unnarrowed, and F3's outstanding proofs — both focused matrices plus the full canonical suite on
python3 AND python3.11 with exact counts pasted — remain merge-gating.

One verified positive to record: the module keeps estimator identity out of admitted JSON —
`estimator_path` lives only in the in-memory dataclass, `comparative_record` is built by the
pinned `build_comparative_record`, and the selector is `spec_cell["estimator"]` with pending,
non-canonical, and malformed registrations all refusing with no default fallback
(`selection_from_authenticated_spec`), satisfying the contract's authority rule and ALT-D120 as
written.

---

## Q3 — Should option D be preferred despite its scope/lineage cost?

**RULING: NO — option D is rejected on doctrine, not merely on cost, and holding the work is
also rejected.**

Three independent grounds, any one sufficient:

1. **ALT-D120 makes the new field useless to the mint.** The mint must recompute widths from
   authenticated members regardless (contract non-negotiable 3; D-118 invariant 7); a
   registered-widths field in the report is admitted JSON the mint is forbidden to treat as
   authority. The field would be either dead weight or a standing temptation to authenticate
   admitted data — the exact failure class D-120 and D-133 exist to kill.
2. **It reverses the D-133/D-120 direction.** The governing disposition is DELETE serialized
   estimator vocabulary from admitted surfaces so forgeries die as closed-profile unknown-key
   refusals (D-133 §2; contract authority rule: "Do not add estimator fields to the v2 pinset,
   extraction report, floor artifact, or artifact provenance"). Option D adds
   estimator-shaped vocabulary back into the report schema.
3. **It corrupts the semantics of `admissible_half_widths_j`.** Carrying default-shaped
   per-member source widths there for a common-mode cell makes the report's cached widths
   describe arithmetic that did NOT produce the cell's floor — admitted data that is
   systematically misleading about its own floor value. That is option C's defect wearing a
   schema change.

The scope facts (outside WRITE_SCOPE, outside non-negotiable 4, reopens the D-124/FCM lineage
mid-ALT-D120) are real but secondary; D would be wrong even in scope. Holding the work entirely
is likewise rejected: the conflict is structural and pre-existing (D-133's bench-verified fact —
the mint carries zero estimator vocabulary, so a common-mode cell cannot be minted today), the
adopted design necessarily collides with the fifth default surface the contract's MAP missed, and
option A under C1–C10 is the completion consistent with every standing invariant.

---

## Q4 — Is the F2 caller-inventory widening acceptable?

**RULING: YES, with two conditions — and one sequencing fact placed on the record.**

The `tests/test_detection_floor.py` guard exists to keep the production caller inventory of
`_common_mode_floor_from_block_inputs` exhaustive. The adopted contract *requires* the mint to
recompute through the governed arithmetic (non-negotiable 1), so
`joulewise/floor_mint_estimator.py:recompute_comparative_estimate` is precisely the caller the
guard should now admit. The diff (packet §8a) keeps the assertion an exact-list equality — the
guard's exhaustiveness is preserved, and the guard correctly detecting the new caller is the
guard working. The new module's own signature pins on the two `floor_extraction` helpers add a
deliberate drift tripwire in the right direction.

Conditions: **(a)** WRITE_SCOPE is formally amended to include `tests/test_detection_floor.py`,
recorded in the WO's decision-log note. **(b)** The record must state the sequencing fact the
packet establishes: the out-of-scope edit already exists in the working tree (packet §8/§8a)
although the worker's report correctly stopped at NEEDS_SCOPE with that file unmodified (packet
§8 state-drift note) — someone applied the edit between the report and packet assembly, before
any scope grant was on the record. This ruling ratifies the edit's content prospectively; it does
not ratify editing outside granted scope ahead of the ruling, and the WO note must say so.

---

## Disposition summary

- **Q1:** Option A AUTHORIZED as design; current implementation NOT yet compliant — one
  fail-open at the binding seam (suffix-matched swallow can eat an absolute-width refusal and
  return provenance-sourced hashes).
- **Q2:** Provisional conditions insufficient; superseded by C1–C10 above, all merge-gating.
- **Q3:** Option D rejected on doctrine (ALT-D120 inertness, D-120/D-133 deletion precedent,
  semantic corruption of the width field); holding the work rejected.
- **Q4:** F2 widening accepted under scope-amendment recording, with the pre-ruling out-of-scope
  edit sequencing noted on the record.

The provisional magistrate authorization of option A is **affirmed in direction and superseded in
conditions**: had the work merged under the five provisional conditions alone, the absolute-width
fail-open would have shipped.
