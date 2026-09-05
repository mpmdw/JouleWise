# Cold-gate Fable ruling: PAPER-SUPPLY (D-173, seam 84b24686) — 2026-09-04

Judge: cold Fable session, no loop context, foreground only, no subagents.

## 0. Disclosure and trust anchors

Auto-loaded into context before I acted: `~/.claude/CLAUDE.md` (global), the
project `CLAUDE.md`, and the memory index `MEMORY.md`. Not opened: CLAUDE.local.md,
RUN_STATE.md, TASK_QUEUE.md, any narrative state doc, night-custody, LaunchAgents.
No discovery suite ran. No file outside this ruling was modified.

Charter digest: expected `099de884…c95d81` (supplied independently), observed
`099de884…c95d81` via `scripts/validate_gate_packet.py` and its receipt. The
first run with the deliberately typo'd sha (`…5813a880…`) returned
`REFUSE / charter_trusted_observed_mismatch`, rc=2. The rerun with the true sha
returned `PASS`, rc=0, packet sha `418bc576…5775e`, all 44 manifested exhibits
matching their pinned digests. Merits were read only after that PASS.

Evidence I personally read: contract `paper_supply_custody.md` (full), `paper_custody.py`
:75-120, :128-203, :339-390, :1270-1311; `tests/test_paper_custody.py` :600-658;
`whole_window.py` :85-92, :1749-1772, :1820-1834, :3355-3380; `analysis_engine/inputs.py`
:151-163, :1609, :1862-1999 (grep for width/mint calls); `floor_mint_estimator.py`
:683-717; assembly `analysis_manifest_v3.py` :3481-3525, :3810-3822; D-173 and D-161
entries and index rows; 17-Q6 verbatim; 43 Q-17-6 row; 02-F4 verbatim; trace 10 (full);
paper-i 05 §Q-R1-2, 06 §R1, 02 blind-Fable §R1. Execution note: the exhibit copy of
`paper_custody.py` cannot import against this worktree's older `authentication_io`,
so F1 is verified by static reading plus a pure-Python closure-cell check, and trace
10's forgery execution stays attributed to its seat at `f2d35b4f`.

## Q-PS-1 — D-173 as written (five typed refs, no receipt families): AMEND

Verified: exactly five frozen ref dataclasses, each `role: str` + `runs_root: Path`
(`paper_custody.py:91-117`); exactly five family specs (`:339-390`); `floor_artifact`
is `InputRole.FLOOR_ARTIFACT` (`:75`) inside the D-165 and Claims censuses, not a ref;
no receipt reference class is public (contract :75, `_ReceiptRef` private at `:406`;
test `:612-613`). Compatible with 43 Q-17-6: Q6 routes the refusal sentence "through the
seam's whole_window_verdict ref", which is `WholeWindowVerdictRef`. The seam's
unconditional stop at `:1291-1296` is an implementation stop, not a reversal of the
ratified refusal rule (charter §9 honoured).

REJECT (MATERIAL) one D-173 clause: "governed files are authorized through clean Git
blobs, generated files through receipts reached from a registered custody inventory."
This contradicts D-173's own index row ("receipts corroborate, never authorize"),
contract :47-49, and the code, where every input is read against the map-pinned digest
(contract step 3; `:909-918` per trace 10) and the receipt is corroborating. As written
the clause licenses the exact class D-173 exists to close.

AFFIRM replacement text: "governed files are authorized through clean Git blobs;
generated files are authorized only by the Git-anchored supply map's pinned digest, with
the registered custody inventory and validator receipt corroborating and never
authorizing."

Consequential contract amendment (install with the D-173 edit): step 8's last sentence
(:216-217) and the sentence "the governed receipt producer remains mandatory" (:234-235)
are replaced by: "Whole-window issuance, admitted or non-admitted, remains stopped until
a registered per-family issuance gate lands that requires `WholeWindowRowValidation.authentic`
to be true and binds model, window, basis, membership and governing row per ruling 43
Q-17-6; non-admission issuance carries only the fixed Q6 sentence." A receipt producer
may corroborate that gate but is not its unlock, which is what "no receipt families"
means once 43 parked the receipt lanes.

D-173 may move from PROVISIONAL to ADOPTED **as amended above, not verbatim**. Adoption
proves no production supplier implements it; all five map roles remain synthetic.

## Q-PS-2 — landability with F1 cured by contract narrowing (D-161): AMEND

F1 confirmed statically: the token is written onto every authentic object (`:174`,
`:197`); the guard covers only `_CAPABILITY_FIELDS` (`:132-146`), which excludes
`_custody_token`, so `object.__getattribute__(obj, "_custody_token")` recovers it; the
constructors are module-level private names (`:1279`, `:1310`). Additionally the token
is recoverable from the closure cells of `_require_custody_capability` without any
authentic object (pure-Python check: a bare `object()` cell is readable via
`__closure__`). Direct construction refuses (`:128-129`; contract :77-78). Under D-161
(index row: in-process adversary out of the model per D-139 A1 / D-148 (6); operative
test MISTAKE vs DELIBERATE) deliberate introspection is outside scope, so contract
narrowing is a legitimate cure and no residency code change is required. Charter §9:
this is the redesign-not-round-5 outcome; this ruling licenses no further same-shape fix
round.

REJECT the submitted narrowing as incomplete (it names only capability residency).
AFFIRM this replacement for contract :53-56 and :75-81:

"A verified result is one of the five frozen, non-container types minted with a
construction token created inside private seam closures. The token is also stored on
every authentic capability and is recoverable by deliberate private introspection of
those objects or of the closure cells of the private guard functions, and the private
constructors are importable. Direct public construction and tokenless `object.__new__`
instances refuse on guarded access. These guards prevent ordinary caller and operator
mistakes; they do not prevent deliberate token extraction or token-bearing
reconstruction, which D-161 places outside the threat model. Physics/evidence failures,
pre-registration failures and ordinary operator mistakes remain fail-closed. A
dictionary, mapping, bytes object, arbitrary sequence, prevalidated object, or
tokenless `object.__new__` object is never a valid ref or verified capability."

Installation required before landing: the text above in the seam branch, plus the
Q-PS-1 D-173 clause and the step-8/:234 amendment. With those installed the seam at
`84b24686` is **LANDABLE** as fixture-only and non-issuing; no supplier or publication
gate is passed.

F2 (MATERIAL test debt, not a registry defect): I confirmed the 16-code registry
(`:41-60`), the contract table (:277-292, 16 rows) and the test's expected set
(`:615-632`) agree, and that the reachability check is `source.count(f'"{code}"') > 1`
(`:655-658`), which a dead literal satisfies. It does not change landability. Condition:
before the first production role is registered in the supply map, replace the count
with an AST census of `PaperCustodyRefusal("<code>", …)` call sites, one per code.

## Q-PS-3 — fixed sentence + six-case real CLI acceptance: AMEND

Verified: the current binding target cannot render a failed row. The assembly finalizer
raises `analysis_finalization_verdict_not_passed` unless `status == "passed"` and
`claim_licensing is True` (`analysis_manifest_v3.py:3511-3515`), and its attachment
records only the passed verdict (`:3814-3820`). The seam stops the whole-window family
unconditionally (`paper_custody.py:1291-1296`) before `authentic` is consulted.
`WholeWindowRowValidation` already separates `authentic` from `admitted`/`status`/
`reasons` (`whole_window.py:85-92`). So the rule is sufficient as a rule but its six
cases under-specify the gate on two points.

REJECT "six cases" as complete. AFFIRM seven cases: the six as listed plus "Authentic
PASSED production row, correctly bound → no refusal sentence (positive branch only)."
AFFIRM the binding condition: the sentence renders only from a `VerifiedWholeWindowVerdict`
whose row validation has `authentic == True` and `admitted == False`; `reasons` stay
non-renderable; the sentence is fixed and carries no reason text.

Minimum transition work (MATERIAL): (1) replace the seam's unconditional stop with the
per-family issuance gate named in Q-PS-1; (2) the non-admission renderer consumes the
seam ref, never the manifest finalizer, whose `verdict_not_passed` raise remains the
positive-branch gate and is not a renderer; (3) OR-01/DS-32/PG-08 amended to
non-admission as 43 rules; historical verdicts stay as issued. No six/seven-case CLI
completion is claimed by anyone; it remains acceptance work.

## Q-PS-4 — 02-F4 width reconstruction before submission: AMEND

Verified both halves of F4: the mint recomputes comparative operands from authenticated
sources and requires exact `Decimal` equality of every stored width
(`floor_mint_estimator.py:683-717`); the analysis binder (`inputs.py:1609`, loop
:1862-1999) checks bundle/config hashes, identities, order and point metrics and has no
width comparison and no import of the mint reconstruction. Trace 10's "possible but not
drop-in" assessment matches the family censuses (`paper_custody.py:351-379`), which carry
none of the mint's inputs.

REJECT "shared reconstruction required before submission" and REJECT "bare disclosed
limitation". AFFIRM this fallback: before submission, run the mint's existing
`bind_v2_floor_artifact_evidence` once over the actual submission floors as a recorded
desk check (trace 10's half-day arithmetic estimate, no new estimator), and record its
receipt beside the finalized manifest. The full custodied join into the two floor-bearing
families (1–2 engineer-days) is post-submission work and stays queued.

Restricted claim: no submission text may call the widened floors "independently
reproduced at consumption" or "source-reproduced by the analysis loader". Permitted
wording: "Floor widths were reconstructed from authenticated member sources once, at mint
(and re-checked once before submission); at analysis consumption they are validated
against the widths recorded in the floor artifact and byte-sealed by the finalized
manifest, not re-derived." Affected statements: the floor rows of the results table and
the source-reproduction statement of the limitations section (F4 cites draft-v1.md:398,
672). Production issuance for the D-165 and Claims families stays stopped until the
desk-check receipt exists or the shared reconstruction lands, whichever is first.

## Q-PS-5 — Q-R1-2 composition rule: REFUSE (both checks)

Defect: the packet cannot support either an AFFIRM or a complete AMEND. The single-count
proof requires the derivation of the window allowance's inputs, and it is not exhibited.
What the exhibits do show: the allowance is
`max(trajectory_excursion_max_j, derived_repeatability_bound_j)` (`whole_window.py:1831-1834`),
where the derived bound is the floor artifact's
`claim_family_bounds[<family>].estimator.replicated_endpoint_bound_j` (or the
single-member field) (`:1749-1772`), a repeatability bound. The proposed rule adds
`t95·s(point)/√50`, which is also member repeatability. Whenever the max selects the
derived bound, repeatability is charged twice unless that floor bound is proven to
exclude the same 50 members' point scatter. The floor estimator that produces
`replicated_endpoint_bound_j` is not in the packet, nor is the D-102 "allowance once"
rule text the blind Fable seat invoked. Partial finding on exhibited evidence: the member
envelopes are the deterministic clock-anchor term (`inputs.py:151,163`;
`whole_window.py:3360-3369`), so envelopes + t term alone is single-count; the t/allowance
pair is the unproven relation.

Minimum cure: exhibit (a) the estimator source for `replicated_endpoint_bound_j` and
`single_member_endpoint_bound_j` with exact line range, (b) the D-102 allowance-once
text, (c) the exact allowance field/selection rule (`drift_allowances[<family>].allowance_j`
of the governing whole-window verdict is the only candidate I can see, `:2076-2079`), and
(d) a worked numeric counterfactual on synthetic members. Until then
`composed_member_envelope_mean.v1` remains the default and no `_v5` collection may bind
the proposed rule. Severity MATERIAL; REFUSE has no effect on the merits.

## Packet hygiene

1. MATERIAL, affects Q-PS-5: the floor-estimator derivation and D-102 text needed for the
   single-count check are omitted; the question is otherwise well posed.
2. NIT, affects Q-PS-1: the D-173 body/index-row disagreement on receipt authorization is
   not flagged; the packet presents the body as ratifiable "as written".
3. NIT: the packet's AFFIRM/AMEND/REFUSE notation is honoured here as REJECT + AFFIRM
   replacement per its own compatibility clause; the charter is not amended.
4. Neutral assembly otherwise: both 02 seats, the 09 erratum, competing R1 proposals,
   and the F4 counterargument are present; no cherry-picking found.

## Disagreements with the lead's labelled position

Lead: landable with F1 cured by narrowing; F2 test debt. I concur on landability and F2,
but the submitted narrowing text is incomplete (closure-cell and importable-constructor
routes omitted) and D-173 is not adoptable verbatim (receipt-authorization clause).
Elsewhere the lead made no recommendation.

## Summary line

Q-PS-1 AMEND (D-173 adopted as amended, not verbatim); Q-PS-2 AMEND (landable once the
replacement narrowing and D-173/contract edits are installed; no residency code change);
Q-PS-3 AMEND (seven cases, authentic-and-not-admitted gate); Q-PS-4 AMEND (one mint
desk check before submission, restricted wording, full join queued); Q-PS-5 REFUSE
(single-count unprovable from packet; default rule stands).
