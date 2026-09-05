# Cold-gate independent contract lens - Opus refuter, PAPER-SUPPLY (2026-09-04)

Contract-lens refuter paired with the cold Fable judge; independent of the
concurrent Fable ruling (not read). Scale: **REFUTED / NOT REFUTED / AMEND**.

## 0. Validation and custody (executed this session)
`scripts/validate_gate_packet.py` with the supplied pins -> `"result":"PASS"`,
42/42 digests observed == expected. Custody re-derived independently: the fetch
of `feat/2026-09-04-paper-custody-seam` **succeeded here** and resolves
`84b24686d4e11b36d2f6fe64e08616ff3ab1c050`; all **19** seam exhibits are
byte-identical to `git show 84b24686:<path>`, and the assembly
`analysis_manifest_v3.py` copy matches `635c5ef0`.

## Q-PS-1 - five typed refs, no receipt families -> **AMEND**

Correct as far as it goes: `_FAMILY_SPECS` (`paper_custody.py:339-395`) has
exactly five entries; `FLOOR_ARTIFACT` is an input role inside `d165_closeout`
and `claim_evidence` (`:351-379`), never a ref; `__all__` (`:1311-1331`) exports
no binding, receipt, payload or verified-result constructor. But the
substitution class is **relocated, not closed**.

**(1) Fixture and production results share a type; only an advisory boolean
separates them.** Fixture mode returns a fully readable `Verified*`
(`:1300-1309`); production raises (`:1297-1299`). `mode` and
`issuance_authorized` sit on `evidence` (`:207-219`), and `_payload` is readable
by any holder because `_capability_getattribute` (`:149-152`) only checks that
the object carries the token, which every authentic fixture object does.
`tests/test_paper_custody.py:645-647` shows the shape: open, then *remember* to
assert `issuance_authorized` is False. A supplier naming `fixture.d165_closeout`
and omitting that assertion renders synthetic numbers as paper - the
D-123/D-165/gamma class with the caller's dict swapped for a map-registered
fixture, and an **ordinary operator mistake** inside D-161's fail-closed zone.
**MATERIAL - blocker before any supplier lands.**

**(2) The Git-blob arm is unexercised.** D-173 and ruling 15 item 2 make
"governed files authorized through clean Git blobs" half the rule, yet
`supply_map.json@84b24686` registers 5 roles and **23 input rows, every one
`"authority":"generated"`**, so the census (`test_paper_custody.py:322-399`)
proves the generated path only.

**(3) No scope census.** D-173 binds "a paper supplier or renderer" but nothing
enumerates which inputs are in scope: `docs/paper/results-fill-registry.md` has
**zero** occurrences of `D-173`/`paper_custody`/`open_paper_input`.

**Replacement text - append to D-173 before ratification:**

> Scope. A `results-fill-registry.md` row is *custody-bound* when its supplier
> column names a `paper_custody` family and role; every claim-bearing row must be
> custody-bound before its value renders, and the bindings are enumerated in the
> contract.
> Non-issuing results. A fixture result must carry a distinct type that no
> renderer accepts, so that omitting an `issuance_authorized` check cannot render
> a fixture value; until that separation is installed, no supplier lands.
> Coverage. A registered production role must carry `"authority":"git_blob"`
> inputs, exercised by the family census.
> Whole window. `WholeWindowVerdictRef` is a registered binding target with no
> producer until `WHOLE-WINDOW-STOP-RECEIPT-01` lands.

That last clause is forced: `paper_custody.py:1291-1296` raises
`paper_custody_blocked_pending_receipt` for the ref **unconditionally**.

## Q-PS-2 - landability under D-161 -> **NOT REFUTED (landing) / AMEND (wording)**

**Landing: NOT REFUTED.** F1 is a documentation overclaim against a threat D-161
prunes. Contract `:53-56, 75-81` asserts a property the code lacks; narrowing the
document to the code cures *that* defect, nothing downstream relies on resistance
to a deliberate insider, and production issuance is blanket-refused
(`:1297-1299`).

**AMEND - the proposition overclaims in the other direction.** It says recovery
needs "deliberate private introspection". `_CAPABILITY_FIELDS` (`:132-146`) does
**not** contain `_custody_token`, so `_capability_getattribute` passes that name
to `object.__getattribute__`: `opened._custody_token` is a plain attribute read,
no `inspect`, no mangling. Replace sentences 2-3 of the narrowing with:

> The token is also stored on every authentic capability and is readable by
> ordinary attribute access, because `_custody_token` is not among the guarded
> `_CAPABILITY_FIELDS`. The guards prevent construction mistakes, not token
> recovery. Forging a result additionally requires importing the module-private
> `_construct_custody_evidence` / `_construct_verified`, a deliberate act outside
> D-161's threat model. Physics/evidence and pre-registration failures and
> ordinary operator mistakes remain fail-closed.

**Install before landing:** that edit **plus** the Q-PS-1 non-issuing-type
clause; without it this proposition's own last sentence is false.

**F2 does not change landability.** `paper_custody.py:41-60`'s 16 codes and the
current conditions agree; the `source.count(code)>1` census at
`tests/test_paper_custody.py:614-658` is test debt a dead literal survives -
a condition on the supplier landing, not on this fixture-only seam.

## Q-PS-3 - fixed sentence + six-case CLI acceptance -> **REFUTED**

**(a) The target cannot carry the required bindings.** The frozen
`attachments["whole_window_verdict"]` (`analysis_manifest_v3.py:3818-3824`) has
exactly five fields: `path`, `sha256`, `schema_version`, `status`,
`evaluation_basis_sha256`. Ruling 43/17-Q6 requires binding to **model, window,
basis, membership, governing row**; only *basis* is present.

**(b) A failed row is structurally unreachable.**
`_authenticate_finalization_inputs` raises
`analysis_finalization_verdict_not_passed` unless `status=="passed"` and
`claim_licensing is True` (`:3510-3515`), and the attachment is built only past
that gate, so its `status` can only ever be `"passed"`.

**(c) No producer exists, in either target.** Grep for the ratified sentence hits
**only** `docs/process_traces/...`; `OR-01`/`OR_01` appears in no Python file.
The seam successor is dead on arrival (`:1291-1296`), and
`WholeWindowRowValidation` (`whole_window.py:85-91`) carries only
`authentic, admitted, status, reasons`. **The six-case acceptance has no
producer.**

**Replacement disposition:**

> The fixed sentence and six-case table are ratified as the *acceptance
> specification*; the binding is NOT well-defined today. Minimum transition work
> before OR-01/DS-32/PG-08 render: a failed-row carrier schema binding model,
> window identity, evaluation basis, membership and governing row; an
> `analysis_manifest_v3` path admitting a non-passed verdict without licensing
> any claim; the `WHOLE-WINDOW-STOP-RECEIPT-01` producer lifting
> `paper_custody.py:1291-1296`; and the CLI renderer plus its six-case test. The
> sentence's exact words and historical verdicts are preserved.

## Q-PS-4 - 02-F4 width recomputation -> **AMEND (disclosable limitation + one mandatory check)**

**Gap confirmed.** The binder (`analysis_engine/inputs.py:1862-1999`) checks
bundle and config sha256, ABBA order tags, scientific-config and stack
identities, and compares the *stored point metric* to the strict summary
(`:1972-1975`) - it never recomputes stored member/block **widths**, which the
mint does (`floor_mint_estimator.py:683-717`: `recompute_comparative_estimate`
then exact `Decimal` equality per width). A coherently-wrong-width artifact with
correct points and hashes passes the binder.

**Not a submission blocker.** Every submission floor is produced by the mint,
which runs that comparison at mint time; the residual is an artifact from an
older or bypassed path, not a live wrong number. The 1-2 engineer-day custodied
join is disproportionate, and trace 10 records the floor-bearing roles carry none
of the mint's input manifest/pinset, component reports, evidence-root locator,
calibration acceptance, ledger/head pin or bracket binding.

**Replacement disposition:**

> 02-F4 is a **disclosed limitation** on two conditions. (1) Before submission,
> `bind_v2_floor_artifact_evidence` is run once over each actual submission floor
> artifact and its authenticated sources and the pass recorded as a pinned
> acceptance artifact - no new module, and it closes the live residual.
> (2) The source-reproduction statement is bounded to: "Floor artifacts are bound
> to their sources by bundle and configuration digests, member identity and
> order, and per-member point metrics; the stored interval widths are verified by
> the minting path that produced them, not independently recomputed by the
> consuming binder." Issuance stays stopped for any floor-bearing output whose
> acceptance run is absent.

## Q-PS-5 - Q-R1-2 composition rule -> **REFUTED (not preregisterable as written)**

**`t95` is ambiguous by ~20%.** Computed this session by numerical inversion of
the Student-t CDF: `t(0.95,49)=1.6766`, `t(0.975,49)=2.0096`, ratio **1.1986**.
The name selects neither tail, and ruling 06 R1 Q-R1-2 fixes neither it nor `df`.
The variance convention is unstated (`ddof=1` vs `0`, factor 1.0102), and the
window allowance has no field, source or selection rule anywhere.

**Estimand mismatch - the deciding defect.** Averaging the 50 member endpoints
yields a half-width equal to the *mean member half-width*, which does not shrink
with `n`. Adding `t*s/sqrt(50)`, which does, sums terms belonging to two
different estimands (the average member interval vs the interval for the member
mean), so "lower endpoint" has no defined meaning until the rule names its
estimand. Opus's preserved alternative in packet 05 - no arithmetic until a
separately registered rule and term list exist - is what the evidence supports.

## Q-R1-2 - single-count check -> **REFUTED (unanswerable; no field exists)**

The question demands "the exact source field or derivation". None exists at the
assembly HEAD: `joulewise/reported_phase_energy.py` **does not exist** and
`grep -rn "reported_energy_cells" joulewise scripts` returns **zero hits**, so
the generator-frozen member universe has no producer and no registered
member-envelope term list exists.

Packet 05's claim that the recommendation "adds repeatability once and avoids
Fable's second anchor charge" is therefore **unsupported by any artifact**. Two
double-count risks cannot be excluded: a run-to-run repeatability term inside the
member envelope would make `t*s(point)/sqrt(50)` charge dispersion twice; an
idle/window allowance already inside it would be charged twice by the added
allowance - the likelier, since member energies are floor-referenced.

**Replacement text:**

> The single-count check cannot be answered until
> `joulewise.reported_phase_energy.v1` registers, per member, the closed term
> list composing `interval.{lower_j,upper_j}` with each term's authenticated
> source. Preregistration then requires, in one document: the estimand; the
> critical value as `t(1-alpha/2, df)` with alpha and df numeric; the variance
> convention with `ddof`; the allowance's schema field, source and selection
> rule; and a term-by-term disjointness table against the member term list.
> Until then `composed_member_envelope_mean.v1` remains the bound default.

## Packet hygiene (separate finding)

1. **MATERIAL** - the contract's Closed public wire cites the TR-01 row as
   `../paper/results-fill-registry.md#L920`; line 920 is TR-01 today (verified),
   but a raw line anchor breaks on any insertion above. Cure: row-ID anchor.
2. **MATERIAL** - Q-PS-3 asks to ratify the fixed sentence while
   `results-fill-registry.md:885, 894, 921` register *different* REFUSAL
   renderings for DS-32, PG-08, OR-01; the packet nowhere discloses that adopting
   Q6 supersedes them.


## Supersession / re-pin forced by adopting D-173

- Every claim-bearing `results-fill-registry.md` row gains a custody family+role
  in its supplier column; zero rows name one today. Unbound rows stay STOP_FILL.
- **OR-01 (:921), DS-32 (:885), PG-08 (:894)** - registered REFUSAL renderings
  superseded by the ratified Q6 sentence; re-pinned to `whole_window_verdict`,
  blocked on `WHOLE-WINDOW-STOP-RECEIPT-01`.
- **TR-01 (:920)** -> `transfer_projection`; **OB-01** and the D-165 close-out
  rows -> `d165_closeout`. Statuses unchanged; authority moves.
- **DS-09..DS-24** -> `reported_energy_parents`, also blocked on the Q-R1-2 rule
  ID, which ruling 06 requires each placement to name and no row does.
- D-173's index row must carry the scope-census and non-issuing-type clauses, or
  it overstates what the code enforces.
