# COLD-GATE FINAL RULING — WO-MINT-ESTIMATOR-VOCAB F1 seam question (revised sitting)

Cold Fable adjudicator, same fresh instance as ruling-1, revised after the paired Opus
contract-lens refuter's brief (`coldgate-mintvocab-refuter-brief.md`). Every load-bearing refuter
claim was **re-verified by this gate's own execution** before adoption — the evidence-root
equality gate (`scripts/mint_floor_artifact_generalized.py:849-854`), the
`isclose`/`Decimal(str())` comparison semantics (executed: both treat `-0.0 == 0.0` as equal;
`_decimal` accepts `str`), main's post-#131 core sha
(`79229aa2757f70a277c870fc50d0672d70952035f982da26ba5211eb7df8ba16`), AST source-segment
comparison of the four seam-dependent core functions between the worktree and `origin/main`
(all IDENTICAL; `bind_floor_artifact_evidence` body DIFFERS per #131 but its component iteration
order and width-refusal message are unchanged), `_CORE_SIGNATURES` coverage, `_fresh_original_core`
per-cell isolation, and the unsorted `rglob` walk in `tests/test_detection_floor.py:1078-1080`.

This document is self-contained. It supersedes ruling-1's condition set in full.

---

## PART A — Disposal of the contested points

**(1) C6 refuted as inert — ADOPT the refutation; ADOPT C6′ as the mandated shape.**
Verified: v2 forces both components onto one producer `evidence_root_id`
(generalized:849-854), so the pinned binder's absolute-width and comparative-width refusals are
the byte-identical string `f"{root_id}: artifact widths differ from authenticated source bytes"`.
Ruling-1's prescribed exact-match-with-comparative-prefix therefore matches the absolute refusal
too and closes nothing — the refuter is right that ruling-1's condition set would have certified
a closure it does not deliver, the same failure shape one layer up. C6′ (width-substituted-copy
binder run, no swallow of any form) is adopted as mandatory — condition F2 below. The refuter's
"minimum acceptable alternative" (keep the swallow, re-verify around it) is **REJECTED as a
standing option**: it re-implements pinned binder checks in a shadow copy, which is exactly the
drift generator F10 exists to prevent, and it retains message-text coupling to a file #131 just
proved is amended mid-cycle by other work orders. If C6′ proves infeasible in implementation,
that is a fresh NEEDS_RULING to this gate, not a fallback.

**(2) C1 refuted as stated — ADOPT C1′, restated as F1.** Verified by this gate: PR #131 is
merged; `origin/main`'s core sha is `79229aa2…`, not `bf628eed…`; #131 amended
`bind_floor_artifact_evidence` itself and added a new refusal inside the binder loop. The
invariant non-negotiable 4 asserts is "this WO changes no byte of the pinned core," not a sha
literal frozen at packet time. I independently re-executed the refuter's function-identity check:
`_verify_report_widths`, `_report_members`, `_target_report_cell`, `_authenticate_component` are
byte-identical between the worktree base and post-#131 main; no seam premise is invalidated.

**(3) Mechanism correction — ADOPT.** Ruling-1 overstated the abort path: the absolute
component's `bundle_sha256s` verification (core :1902-1906) runs and passes *before* the width
raise at :1939, so on the tampered-absolute abort it is the **comparative** component's hashes
(iteration never began) plus the absolute component's known-bad stored widths that go unverified
— not the absolute hashes. Severity unchanged; the corrected mechanism is what F2's regressions
target.

**(4) The -0.0 claim — ADOPT the refutation.** Executed: `math.isclose(-0.0, 0.0, rel_tol=0.0,
abs_tol=0.0)` is True and `Decimal(str(-0.0)) == Decimal(str(0.0))` is True. The replacement
equality at the authentication seam is *equivalent* to the pinned exact-float check, not tighter,
and `_decimal`'s `str` acceptance is looser in one direction (closed by F5(b)). Q1's conclusion
survives on the corrected ground: equivalence plus retained shape/finite/nonnegative validation,
with fail-closed direction if the substitution ever fails to take effect.

**(5) The six weakened conditions — ADOPT all six repairs.**
- **C2 → F3 + F4.** The authentication-seam parity list is closed because the seam substitutes
  exactly one function with exactly one core call site (:1105) — F3 now states that closure
  argument so it can be audited. The symmetric binder-side parity suite the refuter supplies
  becomes F4; under F2 it is structural (the binder runs to completion) and the suite is the
  proof.
- **C3 → F5.** Both repairs adopted. (i) "Never from report or artifact JSON" as literally
  written forbade the contract's own mechanism (non-negotiable 3 recomputes from authenticated
  member rows, which live in the report); corrected to "never from cached floor/width values;
  authenticated member rows, authenticated spec bytes, and evidence bytes are the permitted
  sources." (ii) Verified: the pinned binder's width check uses `rel_tol=1e-12, abs_tol=1e-12`
  (core :1931-1936), so demanding bit-exactness at binding for *every* comparative cell would
  tighten the default path beyond pinned behavior and collide with F6(a)/invariant 12. Corrected:
  bit-exact at postcollection for all comparative cells; bit-exact at binding for spec-selected
  common-mode cells only; default cells at binding keep the pinned check unmodified.
- **C4 → F6.** Output byte-identity is silent on refusal identity, and the tree contains three
  uncovered refusal-identity changes on the default path, including the silently loosened
  assertion at `tests/test_mint_floor_artifact_generalized.py:5651`. The refusal-identity ledger
  (refuter's C4′/C13) is adopted as F6(b).
- **C5 → F7.** Non-negotiable 5's demonstrated-failing requirement is restored verbatim.
- **C8 → F8.** The restoration oracle was self-referential (restoring the entry binding certifies
  a pre-existing leak); adopted the fresh-core `inspect.getsource` oracle. The refuter's
  concurrency attack failed for the right reason (per-cell isolated core via
  `_fresh_original_core`, verified) — that refutation is accepted and recorded.
- **C10 → F12.** Extended to contract non-negotiables 1–6 and to the WO's registered
  prerequisite: the D-133 cl.3 full fresh delta on the FCM head, which nothing in ruling-1
  required and which remains unverified.

**(6) New conditions C11–C14 — ADOPT all four.** C11 becomes F10 (pin `_verify_report_widths`,
`_authenticate_component`, `bind_floor_artifact_evidence` in `_CORE_SIGNATURES` — verified absent
today; #131 proves the core moves mid-cycle, and drift must trip `_assert_core_interface`, not
silently change seam premises; under F2 no message-text pin is needed because no message coupling
survives). C12 is folded into F5(b) (type-parity at the binding comparison — refuter verified it
is not currently exploitable because `validate_floor_artifact` rejects non-numeric widths first;
adopted as cheap hardening, not as a hole). C13 is F6(b). C14 is F11(c).

**(7) Q4 rglob order-dependence — ADOPT.** Verified: the caller inventory is collected in
`rglob` walk order and asserted as an ordered list; with two entries this is filesystem-dependent
and a spurious-failure generator whose predictable "fix" is the exact assertion-loosening pattern
F6(b) exists to catch. Sorted exact comparison mandated — F11(b). The drift-inventory repair
(Q4(d)) is likewise adopted — an unexplained provenance gap on a merge-gating tree is closed by a
mechanical inventory, not a sentence — F11(c).

**Q3 corrections — ADOPT with one remit note.** The primary rejection grounds for option D are
now: (i) the contract's authority rule verbatim ("Do not add estimator fields to the v2 pinset,
extraction report, floor artifact, or artifact provenance" — a registered-widths field is an
estimator field), and (ii) the refuter's shape-incoherence ground, which this gate verifies and
adopts as decisive: option D as stated puts per-member source widths (4N entries) into
`admissible_half_widths_j`, which the pinned `_verify_report_widths` compares against N per-block
reconstructions — a length-mismatch refusal on first authentication, so D cannot work without
also amending the pinned core, i.e., D collapses into B. The D-120/D-133 deletion precedent is
demoted to supporting direction (it targets identity/registration vocabulary, not numeric
arrays). ALT-D120 inertness and semantic corruption of the width field stand as grounds. On the
refuter's remit flag: rejecting "holding the work" was responsive, not volunteered — this
sitting's mandate expressly directed the gate to say plainly if holding were superior. It is not.
Nothing in this ruling pre-authorizes continuation past any future escalation trigger.

---

## PART B — Final dispositions

- **Q1:** Option A **AUTHORIZED** as design. Relocation is sound because the relocated check is
  estimator arithmetic, not member-byte authentication; every byte-authentication surface
  survives unmoved; the authentication-seam replacement is equivalent-plus-retained-validation
  and fails closed if the substitution fails to take effect. The implementation in the worktree
  is NOT yet compliant: the binding-seam swallow admits a common-mode artifact with tampered
  absolute stored widths (comparative hashes unverified on the abort path), cured only by F2.
  Options B (byte-identity law) and C (fabricated admitted data) remain rejected.
- **Q2:** The five provisional conditions are **INSUFFICIENT**, and ruling-1's C1–C10 are also
  insufficient (C6 inert, C1 stale). The complete merge-gating set is F1–F12 below.
- **Q3:** Option D **REJECTED** — shape-incoherent with the pinned core (collapses into B),
  barred by the contract authority rule, inert under ALT-D120, and semantically corrupting.
  Holding the work rejected; option A under F1–F12 is the unique lawful completion.
- **Q4:** F2 widening **ACCEPTED** under F11.

---

## PART C — FINAL MERGE-GATING CONDITION SET (complete, self-contained)

**F1 — Pinned core at the integrated head.** The branch is merged/rebased onto post-#131 `main`
before final verification. At the final integrated head: `git diff origin/main --
scripts/mint_floor_artifact.py` is empty; the head's core sha256 is stated in the WO ledger entry
(`79229aa2757f70a277c870fc50d0672d70952035f982da26ba5211eb7df8ba16` as of this sitting, restated
from the actual head at merge time); and `_verify_report_widths`, `_report_members`,
`_target_report_cell`, `_authenticate_component`, and the binder's component iteration order
`("absolute", "comparative")` are re-verified unchanged at that head.

**F2 — Binding seam rebuilt; no swallow.** The `except core.MintError` catch-and-swallow in
`bind_v2_floor_artifact_evidence` is deleted. The pinned binder is invoked on a deep copy of the
artifact in which exactly one field — the comparative record's `admissible_half_widths_j` — is
substituted with the default-shaped per-block widths derived from authenticated members
(`comparative_component.widths_j`; never from the artifact's or report's cached values), so the
pinned binder runs to completion on every path — absolute widths, comparative bundle hashes,
stack identity, and the both-roots claim-ready assertion all enforced — and returns a genuinely
verified result. The estimator module separately enforces the exact spec-selected width equality
against the REAL artifact's stored comparative widths (per F5). `legacy_result` is always
non-None; `_binding_result_from_provenance` is deleted; the real (unsubstituted) artifact is what
gets written. Regressions, each demonstrated failing against the pre-fix worktree code:
(i) a common-mode artifact with tampered ABSOLUTE stored widths REFUSES at binding;
(ii) a common-mode artifact with a tampered comparative `bundle_sha256s` entry or campaign log
REFUSES at binding; (iii) a multi-cell artifact through the v2 binder REFUSES; (iv) a full
synthetic common-mode mint writes an artifact carrying the registered widths whose
binder-verified hashes equal the `_strict_bundle`-derived hashes.

**F3 — Authentication-seam refusal parity.** A suite proving every pinned
`_authenticate_component` refusal class reachable on the default path refuses identically through
`_authenticate_v2_component`: invalid spec, member order/identity mismatch, width shape mismatch,
nonfinite width, semantics mismatch, and a one-ULP default-width perturbation — each with no
output files. The suite documents why the class list is closed: the seam substitutes exactly one
function with exactly one core call site (`_verify_report_widths`, core :1105); every other
refusal is downstream and untouched.

**F4 — Binder-side refusal parity.** Through `bind_v2_floor_artifact_evidence` on the
common-mode path, every pinned-binder refusal class refuses: invalid artifact, path-dependence,
custody-store provenance, plan resolution/sha/identity, missing evidence-root mapping,
non-directory root, campaign-log sha, component consumption wire, semantics divergence, omitted
members, `_strict_bundle` failure, absolute width mismatch, rebound-hash mismatch, stack-identity
mismatch, #131's "source stack identity fields are unavailable", and the both-roots claim-ready
assertion.

**F5 — The replacement width equality.** (a) Runs unconditionally for every comparative cell at
postcollection; at evidence binding it applies to spec-selected common-mode cells, while default
cells retain the pinned binder's own `1e-12` check unmodified. (b) Where it applies it is
bit-exact, with the postcollection type gate (`not isinstance(x, bool) and isinstance(x,
int | float)`) enforced at BOTH sites — the binding-site `_decimal` `str` acceptance is closed.
(c) Its expected side comes only from `recompute_comparative_estimate` outputs derived from
authenticated member rows, authenticated spec bytes, and evidence bytes — never from the
report's or artifact's cached floor/width values. Tests: one-ULP downward-width attacks on the
report cache (postcollection) and on the artifact's stored widths (binding, common-mode path)
both refuse (D-118 invariant 14 instantiated at both new sites).

**F6 — Default-path identity, outputs AND refusals.** (a) Differential regression: default-path
reports and default-only fixtures authenticate and mint byte-identically to current pinned/v2
behavior (D-118 invariant 12). (b) Refusal-identity ledger: for every existing v2 refusal
fixture, either the refusal message is unchanged, or the change is enumerated and justified in
the WO decision-log note naming the gate that now fires and why — explicitly covering the
loosened assertion at `tests/test_mint_floor_artifact_generalized.py:5651`
(`"absolute_evaluation_basis_sha256 mismatch"` → `"evaluation basis sha256 mismatch"`) and the
two `except ValueError` relabel sites (generalized :2388-2392 and the binding call site). No
refusal assertion may be relaxed without such an entry.

**F7 — Cross-wiring refusals, demonstrated.** Common-mode-shaped widths under a
default-selecting spec REFUSE, and default-shaped widths under a common-mode-selecting spec
REFUSE, at each of the three sites — each site regression demonstrated failing against a
deliberately site-limited implementation variant or pre-WO code, with the demonstration recorded
(contract non-negotiable 5).

**F8 — Patch hygiene with a fresh-core oracle.** Regressions proving: after
`_authenticate_v2_component` returns AND after it raises,
`inspect.getsource(core._verify_report_widths) ==
inspect.getsource(_fresh_original_core()._verify_report_widths)` — the oracle is a freshly
loaded core, never the entry binding; absolute-kind cells are checked by the unmodified pinned
function through the seam (an absolute width mismatch refuses identically); and no other
attribute binding of the pinned module changes across a seam call (`__dict__` delta empty).

**F9 — No output on refusal.** Tests proving a refusal at each of the three sites —
postcollection, construction (via the frozen-object guard), and binding — leaves no output
files, and pinning the write-after-bind ordering (D-118 invariant 13 instantiated).

**F10 — Seam dependency pins.** `_verify_report_widths`, `_authenticate_component`, and
`bind_floor_artifact_evidence` are added to `_CORE_SIGNATURES` so future core amendments trip
`_assert_core_interface` loudly instead of silently changing the seam's premises. Under F2 no
refusal-message text coupling survives, so no message-string pin is required.

**F11 — Scope, inventory, and the F2 widening.** (a) WRITE_SCOPE is formally amended to include
`tests/test_detection_floor.py`, recorded in the WO decision-log note together with the
sequencing fact: the out-of-scope edit existed in the working tree before any scope grant was on
the record; its content is ratified prospectively, the sequencing is not. (b) The caller
inventory in `tests/test_detection_floor.py` is sorted before assertion — an exact comparison
over sorted `(path, owner)` pairs — eliminating the filesystem-order dependence of the two-entry
list. (c) At the final head, a mechanical check asserts every path in
`git diff origin/main --name-only` is a member of the amended WRITE_SCOPE, and the inventory is
recorded in the WO note.

**F12 — Governing gates unnarrowed.** D-118 gauntlet invariants 1–15 AND contract
non-negotiables 1–6 remain owed in full. The worker's outstanding F3 proofs — both focused
matrices plus the full canonical suite on python3 AND python3.11 with exact counts pasted —
remain merge-gating. The WO's registered prerequisite is pinned: the D-133 clause-3 FULL fresh
delta on the FCM branch head is recorded clean before this WO merges (the ALT-D120 deletion is
verified present on the branch; the delta is not yet verified and gates).

---

## Record

Positive findings preserved from ruling-1, all re-verified: estimator identity never enters
admitted JSON (`estimator_path` is in-memory only; records built by the pinned
`build_comparative_record`); the selector is `spec_cell["estimator"]` with pending, non-canonical,
and malformed registrations refusing with no default fallback; the deferral wrapper's
`cell["kind"]` read is authenticated before use (refuter attack 1, refuted); the monkey-patch is
confined by per-cell fresh-core isolation (refuter attack 2, refuted).

For Ed's record, the fact this sitting most needs to surface: **both prior condition sets — the
provisional five and ruling-1's C1–C10 — would have certified the binding-seam fail-open as
closed.** The provisional set never saw it; ruling-1 saw it and prescribed an inert remedy
(byte-identical refusal messages under v2's single producer root). It was caught only because the
cold pairing put a second, adversarial reader on the same primary bytes. That is the
cross-model-diversity mechanism doing exactly what rule 11 built it to do, and it argues for
keeping the paired-refuter shape on every cold sitting that imposes executable conditions.

**FINAL: Option A authorized under F1–F12, all merge-gating, none advisory. Options B, C, D
rejected. Holding the work rejected. The F2 caller-inventory widening accepted under F11.**
