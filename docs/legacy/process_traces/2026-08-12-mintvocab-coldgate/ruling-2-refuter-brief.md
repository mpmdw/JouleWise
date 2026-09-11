# PAIRED OPUS CONTRACT-LENS REFUTER BRIEF — WO-MINT-ESTIMATOR-VOCAB cold gate

Adversarial counter-read of `coldgate-mintvocab-ruling-1.md` against
`coldgate-mintvocab-packet.md` and the primary bytes. Read-only. All verification executed
in `wtE-mintvocab @ cbf609f` (uncommitted tree per packet §8) and against `origin/main @ 14879e4`.

**Headline:** the ruling's *diagnosis* is correct and its *direction* survives. Its single most
important new condition, **C6, is REFUTED** — the prescribed remedy is inert against the very
attack it was written to close, because v2 forces both components to carry one `evidence_root_id`,
making the two refusal messages byte-identical. **C1 is REFUTED as literally stated** — PR #131 is
already merged and main's core sha is no longer `bf628eed…`. Six further elements are WEAKENED.
Four new conditions are owed.

---

## PART 0 — The central defect claim, verified independently

### 0.1 Does the suffix-match swallow an ABSOLUTE-component refusal? **YES — STANDS.**

Traced end to end:

- The swallow: `joulewise/floor_mint_estimator.py:556-560`
  ```python
  except core.MintError as exc:
      if path != _COMMON_MODE_PATH or not str(exc).endswith(
          "artifact widths differ from authenticated source bytes"
      ):
          raise
  ```
- The pinned binder iterates components in a fixed literal order, absolute first:
  `scripts/mint_floor_artifact.py:1814` — `for component_name in ("absolute", "comparative"):`
- The message is raised for **either** component, prefixed only by that component's root id:
  `scripts/mint_floor_artifact.py:1939-1941` —
  `raise MintError(f"{root_id}: artifact widths differ from authenticated source bytes")`
- The absolute component's width block is the same code (`:1917-1918` selects
  `rebound_widths = rebound_member_widths` for absolute; the comparison at `:1928-1941` is shared).

`str.endswith` ignores the prefix entirely. An absolute-width mismatch therefore satisfies the
swallow predicate on the common-mode path, execution falls through to `:566`, skips the default
return, recomputes the comparative estimate, checks only the **comparative** stored widths
(`_stored_comparative_widths`, `:482-498`, `:581-602`), and returns at `:603`. A common-mode
artifact with tampered absolute widths binds. **The ruling's core finding is correct.**

### 0.2 Two precision corrections to the ruling's write-up

**(a) The abort-path provenance claim is overstated for `absolute`.** The ruling states the
returned hashes "were never verified against evidence bytes (the verification at :1902-1906 runs
per-component and the comparative iteration never started)." Wrong for half of it: the abort fires
during the **absolute** iteration, at `:1939`, which is *after* `:1902-1906`
(`if rebound != expected_hashes`) has already run and **passed** for absolute. What is unverified
is the **comparative** component's `bundle_sha256s`, whose iteration never began — plus the
absolute component's `stored_widths`, which is known-bad. Severity is unchanged (the returned map
at `_binding_result_from_provenance` `:501-518` is still half-unverified admitted JSON), but the
mechanism in the ruling's text is wrong and would misdirect the fix.

**(b) "strictly tighter … additionally distinguishes -0.0" is FALSE.** Executed:
```
math.isclose(-0.0, 0.0, rel_tol=0.0, abs_tol=0.0)  -> True
Decimal(str(-0.0)) == Decimal(str(0.0))            -> True
```
`Decimal` compares numeric value; the sign of zero is preserved in `repr` but not in `==`. The
replacement at the authentication seam is **exactly equivalent** to the pinned exact-float
equality for float inputs, not tighter. It is *looser* in one direction: `_decimal`
(`:106-117`) accepts `str` input, so `Decimal(str("0.1")) == Decimal(str(0.1))` → `True`
(verified). The ruling's stated ground for accepting the relocation ("strictly tighter") does not
hold; the correct ground is *equivalence* plus the added shape/finite/nonnegative retention. The
conclusion survives on the corrected ground.

### 0.3 Honest severity calibration (offered, not to soften the blocker)

In the current call graph the tampered artifact is one the mint itself just constructed from
authenticated inputs (`_mint_v2_cell_artifact`), the binder's return value is discarded at the v2
call site (`scripts/mint_floor_artifact_generalized.py:3853` — no assignment), and
`write_outputs_exclusive` runs after binding. So the exposure is a **defense-in-depth regression**,
not a directly-drivable claim forgery. It remains merge-blocking: the binder is the *only*
independent surface designed to catch a construction bug, and this WO's whole purpose is to route
common-mode cells through construction for the first time.

---

## PART 1 — Conditions C1–C10, element by element

### C1 — **REFUTED as stated.** Restatement supplied and verified satisfiable.

C1 requires the core sha to "equal main's `bf628eed4386b69589c9498cd644c0b3b70513f991f5bb223c70d35f1ca55f5c`".

Verified: **PR #131 is already MERGED** (`gh pr view 131` → `"state":"MERGED"`; `origin/main @
14879e4`). At `origin/main`:
```
git show origin/main:scripts/mint_floor_artifact.py | shasum -a 256
79229aa2757f70a277c870fc50d0672d70952035f982da26ba5211eb7df8ba16
git diff --stat cbf609f origin/main -- scripts/mint_floor_artifact.py
 1 file changed, 15 insertions(+), 135 deletions(-)
```
C1 is therefore already unsatisfiable at any integrated head. Worse for the condition as drafted:
**#131 amended `bind_floor_artifact_evidence` itself** (hunk
`@@ -1887,12 +1769,10 @@ def bind_floor_artifact_evidence`) — it replaced
`_derive_stack_identity`/`canonical_domain_sha256(STACK_IDENTITY_DOMAIN, …)` with
`build_stack_identity`/`stack_identity_sha256` and **added a new refusal**
(`MintError("source stack identity fields are unavailable")`) inside the binder's member loop.
The seam depends on that function's message inventory.

**A restatement is acceptable** — the invariant non-negotiable 4 actually asserts is *this WO
changes no byte of the pinned core*, not a literal sha. Lawful restatement:

> **C1′.** The branch is merged/rebased onto post-#131 `main` **before** final verification. At the
> final integrated head, `git diff origin/main -- scripts/mint_floor_artifact.py` is empty, and the
> head's core sha256 is stated in the WO ledger entry (`79229aa2757f70a277c870fc50d0672d70952035f982da26ba5211eb7df8ba16`
> as of this brief; restated at merge time from the actual head). Additionally — because #131
> proves the "pinned" core moves under other work orders within the same cycle — the four private
> core surfaces the seam depends on are re-verified byte-identical at that head:
> `_verify_report_widths`, `_report_members`, `_target_report_cell`, `_authenticate_component`;
> plus `bind_floor_artifact_evidence`'s component iteration order and the exact width-mismatch
> message string.

I executed that re-verification now, so the restatement is not merely lawful but already met:
```
_verify_report_widths   IDENTICAL (775 bytes)
_report_members         IDENTICAL (3224 bytes)
_target_report_cell     IDENTICAL (881 bytes)
_authenticate_component IDENTICAL (9907 bytes)
binder iteration order  ("absolute", "comparative")  — unchanged on main
width-mismatch message  present and unchanged on main
```
No seam premise is invalidated by #131. **The sequencing fact changes C1's text, not the ruling's
disposition.**

### C2 — **WEAKENED.** Executable and sufficient for the authentication seam; blind to the binder seam.

C2's six-class parity list is executable, and it is sufficient-by-construction for
`_authenticate_v2_component` because that seam substitutes exactly **one** function
(`grep -n "_verify_report_widths"` finds a single core call site, `scripts/mint_floor_artifact.py:1105`)
— every other refusal class is downstream and untouched. C2 should say *why* the list is closed
(one-function substitution), or a later reviewer cannot audit its completeness.

The real gap: **C2 imposes refusal parity on the authentication seam and nothing at all on the
binding seam** — which is the *wider* substitution (it discards an entire pinned refusal). Had C2
been written symmetrically, it would have caught the Q1 fail-open regardless of whether C6 works.

> **Repair — C2′.** Add a binder-side refusal-parity suite: through
> `bind_v2_floor_artifact_evidence` on the **common-mode** path, prove every pinned-binder refusal
> class still refuses — invalid artifact, path-dependence, custody-store provenance, plan
> resolution/sha/identity, missing evidence-root mapping, non-directory root, campaign-log sha,
> component consumption wire, semantics divergence, omitted members, `_strict_bundle` failure,
> **absolute** width mismatch, rebound-hash mismatch, stack-identity mismatch, #131's new
> "source stack identity fields are unavailable", and the both-roots claim-ready assertion at
> `:1943-1944` (which the swallow bypasses unconditionally on the common-mode path).

### C3 — **WEAKENED on two counts.**

**(i) "never from report or artifact JSON" is unsatisfiable as written and contradicts
non-negotiable 3's own mechanism.** On the default path,
`recompute_comparative_estimate` (`floor_mint_estimator.py:404-408`) computes from
`comparative_component.widths_j` and `core._comparative_blocks(component)` — both derived from the
**report's authenticated member rows** (`scripts/mint_floor_artifact.py:713-752`, from each
member's `anchor_shift_bound_j`). That is exactly what non-negotiable 3 prescribes ("RECOMPUTES the
floor itself from **authenticated members**"). Taken literally C3 forbids the contract's own
mechanism.

> **Repair.** "…never from the report's or artifact's **cached floor/width values**; authenticated
> member rows, authenticated spec bytes, and evidence bytes are the permitted sources."

**(ii) "runs unconditionally for every comparative cell at BOTH … evidence binding" collides with
C4 / D-118 invariant 12.** At the binding site the pinned check the seam replaces uses
`rel_tol=1e-12, abs_tol=1e-12` (`scripts/mint_floor_artifact.py:1931-1936`) — **not** exact.
Imposing bit-exactness there for *every* comparative cell tightens the **default** path beyond
pinned behavior. Stored widths there come from report `anchor_shift_bound_j` round-trips while
rebound widths come from bundle-byte round-trips; the 1e-12 window is what absorbs any divergence.
C3(ii) therefore creates a live refusal risk on the production default path that C4 and invariant 12
forbid. (At the *authentication* site there is no tension: the pinned check is already
`rel_tol=0.0, abs_tol=0.0`, so the replacement is equivalence, not tightening.)

> **Repair.** "Bit-exact at postcollection for every comparative cell; bit-exact at binding for
> **spec-selected common-mode** cells only — default cells retain the pinned binder's own check
> unmodified (C4 / invariant 12)."

### C4 — **WEAKENED.** Output byte-identity does not cover refusal identity, and the WO already changed refusal identity on the default path.

C4 pins "byte-identical **output**". Refusals produce no output, so C4 is silent on them — and the
tree contains three uncovered default-path refusal-identity changes:

1. The contract-sanctioned reordering (packet §1c explicitly directs it) moved
   `_v2_gate_postcollection` after `_v2_gate_component`
   (`scripts/mint_floor_artifact_generalized.py` diff, `_build_v2_artifacts`). The observable
   consequence is visible only as a **loosened test expectation**: packet §8b changes
   `"absolute_evaluation_basis_sha256 mismatch"` → `"evaluation basis sha256 mismatch"` at
   `tests/test_mint_floor_artifact_generalized.py:5651`. The new string is the *component* gate's
   message (`scripts/mint_floor_artifact_generalized.py:1908`). A different gate now fires first
   for that mutation.
2. `except ValueError` at `:2388-2392` relabels **any** ValueError from recomputation — including a
   genuine pinned-core `MintError` (a ValueError subclass) — as
   `"postcollection_evidence_mismatch: comparative estimator recomputation refused: …"`.
3. `except (core.MintError, ValueError)` at `:3878` does the same at the binding call site.

All three fail closed, so none is a soundness hole. But a silently relaxed refusal assertion is
precisely the class the gauntlet exists to catch, and nothing in C1–C10 requires it to be justified.

> **Repair — C4′.** For every existing v2 refusal fixture, either the message is unchanged, or the
> change is enumerated and justified in the WO decision-log note with the gate that now fires and
> why. No refusal assertion may be relaxed without such an entry.

### C5 — **WEAKENED.** Drops the contract's demonstration requirement.

C5 requires the two cross-wiring refusals at each of three sites. Contract non-negotiable 5
(`mintvocab-impl-contract.md:29-34`) additionally requires each of the three site regressions be
"demonstrated failing against a deliberately site-limited implementation variant or the pre-WO
code". C6 preserves that discipline for its own tests ("must be demonstrated failing against the
current worktree code before the fix"); C5 does not. Without it, three passing tests prove nothing
about *which* site they exercise — the consult's named failure mode.

> **Repair.** Append to C5: "each site regression demonstrated failing against a site-limited
> variant or pre-WO code, with the demonstration recorded (non-negotiable 5)."

### C6 — **REFUTED.** The prescribed remedy is inert; the collision is structural in v2.

C6 requires the swallow to "match the pinned refusal message **exactly and in full**, including the
**comparative** component's `evidence_root_id` prefix — never `endswith`."

**Proof of refutation.** v2 *requires* both components to carry the producer's single evidence
root — `scripts/mint_floor_artifact_generalized.py:849-854`:
```python
if absolute.evidence_root_id != evidence_root_id or (
    comparative.evidence_root_id != evidence_root_id
):
    raise MintError(
        f"{cell_label}: component evidence_root_id must equal the producer root"
    )
```
Reinforced at `:3594-3602` ("evidence-root id … maps to multiple paths" / "components map to
multiple evidence roots"), and confirmed in the production-shaped fixture, where **both**
provenance components assert the same id (`tests/test_mint_floor_artifact_generalized.py:8554-8560`,
both `SEVEN_B_EVIDENCE_ROOT_ID`).

Therefore, for any v2 artifact, the absolute component's message and the comparative component's
message are **the identical string**:
`f"{root_id}: artifact widths differ from authenticated source bytes"`.

Exact-and-in-full matching on the comparative root id matches the absolute refusal byte-for-byte.
**C6's remedy closes nothing.** An implementer who applies C6's prescription verbatim and then runs
C6(i) will find the test still failing — which is the one thing that saves this condition: C6's
*diagnosis and required regressions are correct and must be kept*; only its prescribed fix is void.

**Secondary refutation of the whole message-matching approach.** C6 couples a merge-gating guard
to a private message string in a file the ruling itself calls immutable. #131 has just
demonstrated that file is *not* immutable across the cycle: it amended the binder body and **added
a new refusal message** inside the same loop. Most drift directions fail closed (a reworded message
breaks the feature; a renamed function raises `AttributeError`), but the one direction that fails
**open** — any future refusal whose text ends with the same suffix, or a third component in the
iteration — is unguarded and invisible.

> **Repair — C6′ (structural; eliminates the swallow rather than narrowing it).** Delete the
> catch-and-swallow. Instead apply the *same* authorized technique already used at the
> authentication seam: call the pinned binder on a copy of the artifact in which **only** the
> comparative record's `admissible_half_widths_j` is substituted with the default-shaped widths the
> pinned binder itself would rebind (derived from authenticated members, not from the artifact).
> The pinned binder then runs to completion — absolute widths checked, comparative bundle hashes
> checked, stack identity checked, `:1943-1944` both-roots assertion enforced — and returns a
> genuinely verified result. The estimator module separately enforces the exact spec-selected
> equality against the **real** artifact's stored comparative widths. No refusal is ever swallowed,
> `legacy_result` is always non-None, and `_binding_result_from_provenance` becomes dead code
> (satisfying C7 by construction).
>
> **Minimum acceptable alternative if C6′ is judged too invasive:** keep the swallow, but after
> swallowing, the module must independently (a) verify the **absolute** component's stored widths
> against `_strict_bundle`-derived member widths, (b) verify the **comparative** component's
> `bundle_sha256s` against `_strict_bundle`, (c) assert both provenance roots present, and (d)
> derive the returned hashes from (a)/(b). C6's three regressions are retained unchanged under
> either shape.

### C7 — **STANDS**, with two notes; it addresses the lesser half of the defect.

- It does **not** break a legitimate default-path use: on the default path the function returns
  `legacy_result` at `floor_mint_estimator.py:566-568` and never reaches
  `_binding_result_from_provenance`. That helper is reachable only via the common-mode swallow at
  `:603`. Deletion is safe. **Attempted refutation failed.**
- Typing nit: "return `None`" contradicts the declared return type `Mapping[str, tuple[str, ...]]`
  (`:536`). Prefer narrowing the annotation, or adopt C6′, under which the helper is simply dead.
- Framing: C7 removes the *unverified return value*; the *swallowed refusal* is the live harm and
  is C6's job. With C6 refuted, C7 alone leaves the hole open. These must not be scored
  independently.

### C8 — **STANDS on the exception path; concurrency attack REFUTED by me; WEAKENED on the restoration oracle.**

- Exception path: covered by C8's own wording and satisfied by the code —
  `scripts/mint_floor_artifact_generalized.py:3341-3344` uses `try/finally`.
- **Concurrency attack tried and failed.** I expected a shared-module global mutation. It is not:
  `_configured_core` (`:1459-1467`) calls `_fresh_original_core` (`:1425-1439`), which loads an
  **isolated module instance per cell** via `spec_from_file_location` under a unique name and pops
  it from `sys.modules`. The patched attribute is never visible to any other caller, and
  `_verify_report_widths` has exactly one core call site (`:1105`), inside the patched window. The
  patch is not called by the binder at all. **No concurrent/observability defect found.**
- **Real gap — the restoration oracle is self-referential.** `:3317` captures
  `pinned_width_verifier = core._verify_report_widths` and `:3344` restores *that*. C8's test
  ("is the original function object after return AND after raise") compares against whatever was
  bound at entry, so a pre-existing leak restores and certifies the leaked function. The existing
  test at `tests/test_mint_floor_artifact_generalized.py:5793-5795` already has the right oracle
  (`inspect.getsource(...)` vs `generalized._fresh_original_core()._verify_report_widths`).

> **Repair.** C8's oracle must be a **freshly loaded** core, not the entry state:
> `inspect.getsource(core._verify_report_widths) == inspect.getsource(_fresh_original_core()._verify_report_widths)`,
> asserted post-return and post-raise.

C8's `__dict__`-delta clause is executable as written (it compares attribute *bindings*; in-place
cache mutation such as `_BINDING_SUMMARY_CACHE` does not rebind and so does not false-positive).

### C9 — **STANDS.** Executable at all three sites; no refutation found.

Construction-site refusal is reachable and testable via the frozen-object guard
(`"frozen v2 comparative recomputation changed before construction"`); ordering support is real
(`write_outputs_exclusive` after binding). Pinning it with a test is correct.

### C10 — **WEAKENED.** Preserves D-118 1–15 but drops two other governing gates.

1. It preserves D-118 invariants 1–15 but **not the contract's non-negotiables 1–6**. That is how
   non-negotiable 5's demonstration requirement fell out of C5 (above). Fix: "…and contract
   non-negotiables 1–6 remain owed unnarrowed."
2. It does not pin the WO's own registered **prerequisite**: `TASK_QUEUE.md:212-213` —
   "Prerequisites: FCM-01 ALT-D120 round + full fresh delta land clean." I verified ALT-D120's
   deletion is present on the branch (`estimator_registration` is a *forbidden* closed-profile key
   at `joulewise/floor_extraction.py:1543-1547` and `:1727-1732`, and absent from
   `_D117_MINT_FLOOR_OPTIONAL_KEYS` at `:1470-1475`). I could **not** verify D-133 cl.3's **full
   fresh delta** on the FCM branch head from the tree; nothing in C1–C10 requires it. Fix: add
   "…and the D-133 cl.3 full fresh delta on the FCM head is recorded clean before merge."

---

## PART 2 — Q3 (option D rejected)

**Overall: STANDS.** No contract contradiction found; one ground is over-cited, and a stronger
ground was missed.

- **Ground 1 (ALT-D120 inertness): STANDS.** Non-negotiable 3 and D-118 invariant 7 do force
  recomputation from authenticated members regardless, making the field inert to the mint. Verified
  against the code path: the mint's authority is `AuthenticatedComponent.spec_cell["estimator"]`
  (`floor_mint_estimator.py:396-402`), and no artifact/report field feeds the estimator selection.
- **Ground 2 (reverses D-133/D-120): WEAKENED as doctrine, RESCUED by the contract.** D-120 and
  D-133 cl.2 target **serialized identity/registration vocabulary** (`estimator_registration`), not
  numeric arrays; a "registered per-block widths" field is forgeable *numbers*, which the mint
  recomputes and would never trust. So the D-120/D-133 precedent is a looser fit than the ruling
  claims. It is rescued verbatim by the contract's own authority rule
  (`mintvocab-impl-contract.md:228`): "Do not add estimator fields to the v2 pinset, extraction
  report, floor artifact, or artifact provenance." A registered-widths field is an estimator field.
  **Cite the authority rule, not the precedent.**
- **Ground 3 (semantic corruption): STANDS.** Correct, and it is the load-bearing ground.
- **Ground missed — option D as *literally stated* is incoherent with the pinned core.** Option D
  says the report carries "per-member source widths in `admissible_half_widths_j`". The pinned
  `_verify_report_widths` compares that field against **per-BLOCK** widths
  (`math.fsum(4 anchor bounds)/2.0`, one per block — `scripts/mint_floor_artifact.py:713-752`,
  `:755-779`). Per-member values would be 4N entries against N expected: option D breaks the
  default path by length mismatch on the very first authentication. This is a cleaner and more
  decisive rejection than any of the three offered, and does not require doctrine.
- **Rejecting "holding the work": STANDS but is beyond Q3's question.** Q3 asked only whether D
  should be preferred. Volunteering the hold rejection is within an adjudicator's remit; I flag it
  because rule 11 reserves stop/continue judgment to the magistrate seat and the cold instance
  should not be read as pre-authorizing continuation past a future trigger.

---

## PART 3 — Q4 (F2 caller-inventory widening)

**Merits: STANDS.** The guard's purpose is exhaustiveness over production callers of
`_common_mode_floor_from_block_inputs`; the contract requires the mint to become one; the diff
keeps an exact-list `assertEqual`. No contradiction with the standing rule that WRITE_SCOPE is
exhaustive — a cold-gate scope grant is the correct venue (rule 11 reserves scope/process rulings
away from the lieutenant, not away from the gate).

**Two defects the ruling missed:**

**(1) The widened assertion is order-dependent over an unsorted filesystem walk — NEW.**
`tests/test_detection_floor.py:1078-1080` collects callers via
`for path in (repository_root / root_name).rglob("*.py")`, appending in walk order, and the
assertion at `:1104-1112` is a list `assertEqual`. With one entry, order was irrelevant. With two
(`joulewise/floor_mint_estimator.py`, `joulewise/floor_extraction.py`), the expected order now
depends on `os.scandir` ordering, which is filesystem/platform dependent and unspecified. This is
a spurious-failure generator on any other machine or CI filesystem — and the predictable "fix" is
to relax the assertion, which is the exact loosening pattern already visible at
`tests/test_mint_floor_artifact_generalized.py:5651`.

> **Repair — Q4(c).** Sort the collected inventory (or the `rglob`) before asserting, keeping the
> comparison an exact multiset of `(path, owner)` pairs. `tests/test_detection_floor.py` is inside
> the amended WRITE_SCOPE, so this is in scope.

**(2) Q4(b) closes an unexplained state drift with narrative instead of a check — WEAKENED.**
The ruling records that someone applied an out-of-scope edit between the Sol report and packet
assembly, ratifies its *content*, and requires the WO note to disclaim ratifying the *act*. It does
not require anyone to establish that **no other** undisclosed drift entered the tree. Packet §8's
own state-drift note says the tree "has advanced" beyond the report's recorded `--stat`
("2 files changed, 87 insertions(+), 40 deletions(-)" → "5 files changed, 1231 insertions(+),
41 deletions(-)"). An unexplained provenance gap on a merge-gating tree is closed by an inventory,
not by a sentence.

> **Repair — Q4(d).** At the final head, assert mechanically that every path in
> `git diff origin/main --name-only` is a member of the amended WRITE_SCOPE list, and record the
> inventory in the WO note.

---

## PART 4 — New conditions owed (not present in C1–C10)

**C11 — pin the seam's private-core dependencies so future core amendments fail loudly.**
`_CORE_SIGNATURES` (`scripts/mint_floor_artifact_generalized.py:125-158`) pins only
`ComponentPaths`, `pre_registration_gate`, `mint_authenticated_artifact`,
`validate_floor_artifact`, `mint_floor_artifact`. It does **not** pin `_verify_report_widths`,
`_authenticate_component`, or `bind_floor_artifact_evidence` — the three surfaces this WO now
depends on by name, signature, and (under C6) message text. #131 has just proven the core is
amended by other work orders mid-cycle. Add `_verify_report_widths` (and `_authenticate_component`,
`bind_floor_artifact_evidence`) to `_CORE_SIGNATURES`, and — if any message-text coupling survives
C6′ — pin the exact refusal string as a compared constant, so drift trips
`_assert_core_interface` (`:1382-1422`) instead of silently changing the seam's premises. In
WRITE_SCOPE.

**C12 — type-parity at the binding-site width comparison (hardening, not a hole).**
Postcollection type-gates (`:2398-2401`: `not isinstance(observed, bool) and isinstance(observed,
int | float)`); the binding site does not — `_decimal` (`floor_mint_estimator.py:106-117`) accepts
`str`, and `Decimal(str("0.1")) == Decimal(str(0.1))` is `True` (verified). **I checked and this is
not currently exploitable**: `core.bind_floor_artifact_evidence` runs
`validate_floor_artifact` first (`scripts/mint_floor_artifact.py:1781-1783`) and the artifact
validator rejects non-numeric widths (`joulewise/detection_floor.py:3063-3070`, `_is_number`). It is
still an asymmetry between two copies of "the same" exact check, and cheap to close.

**C13 — refusal-identity parity ledger.** See C4′ above.

**C14 — scope re-inventory at final head.** See Q4(d) above.

---

## PART 5 — What I tried and could not refute

Recorded per the refuter's duty, so the gate can see where adversarial effort was spent and failed:

1. **"The deferral wrapper takes its dispatch from admitted JSON."** The wrapper branches on
   `cell.get("kind") != "comparative"` (`:3322`), which looked like an ALT-D120 violation — a
   control decision read from report data. **Refuted:** `_target_report_cell`
   (`scripts/mint_floor_artifact.py:650-672`) has already enforced `cell["kind"] == expected_kind`
   against the **pinned** `ComponentPaths.expected_kind` at `:1098`, before `_verify_report_widths`
   is reached at `:1105`. The value is authenticated by the time it is read.
2. **"The monkeypatch leaks across cells / is concurrency-unsafe."** Refuted by
   `_fresh_original_core` per-cell module isolation — see C8.
3. **"C7 breaks a default-path caller."** Refuted — see C7.
4. **"The reordering of `_v2_gate_postcollection` after `_v2_gate_component` drops a check."**
   Refuted: both gates still run for every cell; the move is two loops, not a deletion, and the
   packet's MAP (§1c) explicitly directs the reversal. Only *refusal ordering* changed (→ C4′).
5. **"#131 invalidates a seam premise."** Refuted by direct byte comparison — all four dependent
   functions, the binder's iteration order, and the width message are identical between `cbf609f`
   and post-#131 `origin/main`. Only C1's literal sha is stale.
6. **"The binding-site string-typed width is exploitable."** Refuted by the artifact validator
   ordering — downgraded to C12 hardening.
7. **Q1's core direction, and conditions C2/C4/C5/C9/C10's substance.** I tried to find a reading
   under which option A is unsound rather than merely unfinished, and could not: every byte
   authentication survives the relocation, and B/C/D each fail on an independent standing
   invariant. **Option A stands.**

---

## Disposition

| Element | Verdict |
|---|---|
| Q1 central defect claim | **STANDS** (2 precision corrections: absolute hashes *were* verified; "-0.0 / strictly tighter" is false) |
| C1 | **REFUTED as stated** — restatement C1′ supplied and already verified satisfiable |
| C2 | **WEAKENED** — add binder-side parity suite C2′ |
| C3 | **WEAKENED ×2** — "never from report JSON" unsatisfiable; bit-exact-at-binding collides with C4/inv.12 |
| C4 | **WEAKENED** — output parity ≠ refusal parity; three uncovered refusal-identity changes |
| C5 | **WEAKENED** — restore non-negotiable 5's demonstration requirement |
| C6 | **REFUTED** — message collision is structural (`generalized:849-854`); C6′ repair supplied; keep C6's regressions |
| C7 | **STANDS** (subordinate to C6; typing nit) |
| C8 | **STANDS** on exceptions; **WEAKENED** on the restoration oracle; concurrency attack refuted |
| C9 | **STANDS** |
| C10 | **WEAKENED** — extend to non-negotiables 1–6 and the D-133 cl.3 full-delta prerequisite |
| Q3 | **STANDS** — ground 2 over-cited (use the authority rule); stronger shape-incoherence ground missed |
| Q4 | **STANDS** on merits; **WEAKENED** — order-dependent assertion (new); drift needs an inventory, not a sentence |

**Bottom line for the magistrate.** Adopt the ruling's direction and its condition set with C1
restated (C1′), C6 replaced (C6′), C2/C3/C4/C5/C8/C10 repaired as above, and C11–C14 added. The
single fact that most needs to reach Ed: **had the work merged under the ruling's C6 as written,
the absolute-width fail-open would have shipped anyway** — the condition set would have certified a
closure it does not deliver. That is the same failure shape the ruling itself identified in the
five provisional conditions, one layer up.
