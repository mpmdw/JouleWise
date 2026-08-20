# S0 — CONTRACT LENS (C-028 gauntlet)

Diff `7d4454e..6771924` on `impl/r2-s0-mint-resolver`, worktree
`.../scratchpad/wtS0`. Read-only; no edits, no repo writes, no test execution
(left to the execution lens). All line numbers are **post-diff HEAD** numbers
unless marked `(old)`.

Two commits: `cef3306` (kernel) + `6771924` (regressions). 8 files, +411/−42.

**VERDICT: BLOCK.** One blocker (spec-inverting fixture crosswire), three
should-fix, six nits. Everything else in the S0 scope is conformant, and the
severability requirement (item 6) is fully met.

---

## 1. Clause → implementation ledger

| Clause | Requirement | Implementing hunk | Status |
|---|---|---|---|
| S1(i) | Mint policy generation-resolved; **no literal screen scalar or screen-substituted rule string anywhere in the mint lane** | resolver `calibration_bracketing.py:191-247`; consumers `detection_floor.py:2354-2357, 2452-2456, 2498-2501`; `floor_mint_estimator.py:147-166, 187, 213-226`; `mint_floor_artifact_generalized.py:66-89, 650-660, 674, 822, 922-928` | **MET.** Verified by grep: `0.010818`/`0.009724` occur **zero** times in all three consumer files at HEAD; at `7d4454e` they occurred at `floor_mint_estimator.py:39,40,204`, `detection_floor.py:2447,2448,2491`, `mint_floor_artifact_generalized.py:64,65`. |
| S1(ii) | `_v3` pack family | — | Correctly ABSENT (S3 work). |
| S2 | Authority = registered D-102 entry keyed by the acceptance's own `acceptance_id` | `calibration_bracketing.py:196-198` (`_D102_GENERATION_DERIVATIONS.get(acceptance_id)`) | **MET.** |
| S2 | Unregistered id ⇒ refusal, never a default | accessor returns `None` (`:198`, `:234`, `:246`); consumers refuse: estimator raises `unregistered acceptance generation` `floor_mint_estimator.py:161-165`; mint raises `MintError` `:651-653`; projector returns `None` `detection_floor.py:2356-2357` | **MET.** `return None` is the established refusal idiom of `_project_floor_mint_pinset_v2` (every other validation failure in that function does the same). |
| S2 | HYBRID guard: cross-check **only when** `decimal_derivation.ratified_operatives` is present | `calibration_bracketing.py:200-221` — optional `acceptance=` kwarg, `decimal_derivation` read at `:203-205`, `ratified_operatives` at `:206-210`, screen comparison + refusal at `:211-221` | **MET** as worded (compares `bracket_screen_s` only, exactly the amendment's scope). See nit N1 for the one hole. |
| S2 | Stubs served from registry (n=19 replay 37/37) | kwarg defaults to `None` ⇒ registry-only path; `tests/test_floor_mint_estimator.py` **untouched** (not in the diff) | **MET** structurally. Guard is genuinely live on the estimator path: I confirmed `configs/calibration/calibration_acceptance_d079_v2_n17_r4.json` carries `decimal_derivation.ratified_operatives.bracket_screen_s = "0.009724"`, and `floor_mint_estimator.py:153-158` passes `acceptance=calibration_acceptance` (the full artifact). |
| S3 | Frozen `_v2` roots read-only, generators included | — | **MET.** No `configs/` path in `git diff --name-only`. |
| S4 | New code limited to resolver + call-site rewiring + schema conditional + genesis rename + guard test | all four present; **but** see SF1 (extra shim layer) | **PARTIAL.** |
| S4 | Tracked golden-regeneration CLI stays BARRED | no new script; `tests/.../:1276-1298 (old)` bar untouched | **MET.** |
| S5 / C1 | Accessors adjacent to `_D102_GENERATION_DERIVATIONS`; derivation table unchanged | inserted at `:191-247`, immediately after the table's close at `:188` | **MET.** Table rows byte-identical (diff shows context only). |
| S5 / C2 | Delete `_BRACKET_SCREEN`/`_ALLOWANCE_RULE`; resolve at top of `_validate_calibration_basis`; rewire `:166`, `:192-195`, `:204` (old) | deletions in hunk `@@ -36,8 +40,6`; resolution `floor_mint_estimator.py:147-166`; comparisons `:187`, `:213-216`; message `:224-226` | **MET.** |
| S5 / C2 | `_ACCEPTANCE_SELECTION` **untouched** | `floor_mint_estimator.py:43` — appears only as diff context, value `"issued_d116_artifact_only"` unchanged | **MET** (task item 2). |
| S5 / C3 | `detection_floor` `:2446-2448`, `:2491` (old) resolved from `acceptance["acceptance_id"]` already in scope | `:2354-2357` resolves once per producer; used at `:2455-2456`, `:2499-2500` | **MET.** |
| S5 / C3 | Symbolic forms at `:517`/`:641` (old) **untouched** | now at `detection_floor.py:521` and `:645`, both still `"max(observed_drift_s,bracket_screen_s)"`; no diff hunk within 1000 lines of either | **MET** (task item 2). |
| S5 / C3 | `_V2_POSTCOLLECTION_KEYS` / `_V2_ACCEPTANCE_KEYS` unchanged | `:2118-2131` / `:2102-2104`, context only | **MET.** |
| S5 / C4 | `V2_ALLOWANCE_RULE`/`V2_BRACKET_SCREEN_S` **replaced with** `allowance_rule_for` / `bracket_screen_s_for` | `:68-77` defines the two specified wrappers; `:80-89` **retains both constant names as callables** | **DEVIATION — SF1.** |
| S5 / C4 | `_parse_v2_postcollection` gains `acceptance_id` kwarg; sole caller already has it | signature `:596-601`; caller `:922-928` threads `acceptance_id` captured at `:822` | **MET.** |
| S5 / C4 | `_v2_allowance_projection` **unchanged** | zero occurrences in the diff for that file | **MET** (task item 2). |
| S5 | `arm_readiness_evidence.py` UNEDITED | not in `--name-only` | **MET** (task item 2). |
| S6 | `DEFAULT_ACCEPTANCE_BOUND_SHA256` → `GENESIS_FIXTURE_ACCEPTANCE_SHA256`, **rename only** | `calibration_bracketing.py:140-142` | **MET.** Value `9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb` byte-identical (diff shows the literal line as unchanged context inside the hunk). |
| S6 | Both call sites renamed | `:690` (fixture-role branch of `_acceptance_bound_from_authenticated_bytes`) and `:783` (`_acceptance_artifact_sha256` fallback) — exactly the `:629`/`:722` pair the debate named | **MET.** Repo-wide grep: zero live references to the old name remain (only process-trace docs). |
| S6 | Comment as specified | `:140-141`: "Authenticates the retained ``schema_fixture_unissued`` genesis bytes; this is not the digest of ``DEFAULT_ACCEPTANCE_BOUND_PATH``." | **MET** — matches the amendment's wording. |
| S6 | Regression test closing the silent-coverage gap (fixture bytes authenticate + `_acceptance_artifact_sha256` returns the genesis digest for a fixture-role doc) | `tests/test_calibration_bracketing.py:616-628` — asserts all three: raw sha == constant, `load_calibration_acceptance_bound(path)` round-trips, `_acceptance_artifact_sha256(fixture)` == constant | **MET.** Both required assertions from the amendment are present. |
| S7 | Schema conditional written over the **n17 generation set**, not per-id, so a science-neutral r5 is one list entry | `schema_v2.json:743-762` (finalProducer n17 branch) and `:1022-1041` (pinRequirements n17 branch), each `enum: [..._n17_r3, ..._n17_r4]` | **PARTIAL — SF2** (written over the set ✔, but the set is inlined twice ⇒ two edits, not one). |
| S7 | Value enums unchanged by r5 (two screens only) | `:189-199`, `:470-480` — each widened `const`→`enum` of exactly the two registered screens | **MET.** |
| S8 | S0 is r5-neutral and cleanly severable | see §3 | **MET.** |

**Every hunk is licensed.** Hunk-by-hunk reverse map:

| Hunk | Licensing clause |
|---|---|
| `calibration_bracketing.py` @135, @626, @719 | S6 |
| `calibration_bracketing.py` @184 (resolver), @1983 (`__all__`) | S2 / C1 |
| `detection_floor.py` @35, @2347, @2444, @2488 | C3 |
| `floor_mint_estimator.py` @18, @36, @142, @163, @189 | C2 |
| `schema_v2.json` @187, @462, @683, @883 | C5 / S7 |
| `mint_floor_artifact_generalized.py` @45, @61, @567, @616, @636, @784, @887 | C4 |
| `tests/test_calibration_bracketing.py` @21, @33, @611 | S6 regression test |
| `tests/test_mint_policy_resolver_guard.py` (new) | S4 no-copied-scalar guard |
| `tests/test_mint_floor_artifact_generalized.py` ×10 hunks | C9 call-shape follow-through — licensed in kind, **defective in execution** (B1) |

No SCOPE CREEP found: nothing touches `configs/`, `arm_readiness*.py`, `_ACCEPTANCE_SELECTION`, `_v2_allowance_projection`, the symbolic forms, or the golden block.

---

## 2. Findings

### BLOCKER

**B1 — `_live_acceptance_id()` inverts R2-SPEC-1: fixtures resolve the policy from the LIVE default instead of the acceptance the fixture itself declares, producing a real crosswire.**

`tests/test_mint_floor_artifact_generalized.py:848-852` adds

```python
def _live_acceptance_id() -> str:
    acceptance = load_calibration_acceptance_bound()   # no path -> LIVE default (= r4)
    ...
```

and all ten rewritten fixture sites key off it. But R2-SPEC-1 (`06-r2-design-opus.md:61-69`) is explicit: every site "resolves the pair from the **acceptance generation the artifact under validation itself names** (`acceptance_id`)". The production code was changed to do exactly that (`_parse_v2_postcollection(..., acceptance_id=acceptance_id)` at `:596-601`/`:922-928`); the fixtures were changed to do the opposite — they swapped one hardcoded generation (n19) for a different one (whatever is live), rather than for the declaring acceptance.

This is not theoretical. Demonstrated instance:

- `build_d117_production_fixture` loads its acceptance from the **n19** file at `:4370-4371`
  (`configs/calibration/calibration_acceptance_d079_v2.json`; I confirmed its `acceptance_id` is `d079_calibration_acceptance_v2_n19`, screen `0.010818`).
- It declares that id on the producer at `:5003-5008`:
  `producer["calibration_acceptance"] = {"acceptance_id": acceptance["acceptance_id"], ...}`.
- Its postcollection now carries the **r4** rule at `:5085-5087` and `:5217-5219`
  (`generalized.V2_ALLOWANCE_RULE(_live_acceptance_id())` → `max(observed_drift_s,0.009724)`),
  while `bracket_screen_s` at `:5088` / `:5220-5222` still comes from the n19 bracket artifact.

So the fixture emits `acceptance_id = …_n19` with `allowance_rule = max(…,0.009724)` and `bracket_screen_s = 0.010818` — mutually inconsistent, and the resolver will resolve n19 → `0.010818` and refuse the rule. Before this diff that fixture was self-consistent (n19 declaration + n19 rule + n19 validator).

Second instance, same class: `_mixed_calibration_basis` at `:1347-1364` binds `issued_acceptance` from the acceptance it holds (`acceptance = inputs.calibration_acceptance`, `:1350`, fields at `:1354-1358`) but takes `allowance_rule` from the live id at `:1361`. The helper has the correct key in hand and ignores it.

Root cause: `_v2_postcollection` (`:782-846`) hardwires the live id for all ten of its callers instead of taking an `acceptance_id` keyword — the mirror image of the production change it is supposed to track.

Required fix: thread the declaring acceptance id. `_v2_postcollection(..., *, acceptance_id)`; `_mixed_calibration_basis` → `acceptance["acceptance_id"]`; `build_d117_production_fixture` → the id it already binds at `:5004`. Where a fixture genuinely *is* the live acceptance, `load_calibration_acceptance_bound()` may stay, but as the fixture's own declared acceptance, not as an ambient default.

Why blocker and not should-fix: (a) it contradicts the ratified spec's central sentence at the exact layer the spec was written to fix; (b) it silently re-introduces a single-generation coupling in the test corpus, which is the coupling S0 exists to delete; (c) it makes the n19-declared fixture untestable against its own generation, so the regression corpus can no longer prove the resolver discriminates generations — which is the only property S0 adds. Execution lens should confirm the resulting red; contract-wise the shape is wrong regardless of colour.

### SHOULD-FIX

**SF1 — C4's "replace" was implemented as "re-type", leaving a four-function stack where the spec asked for two.**
`mint_floor_artifact_generalized.py:68-77` defines the two specified wrappers `allowance_rule_for` / `bracket_screen_s_for`; `:80-89` then defines `V2_ALLOWANCE_RULE(acceptance_id)` and `V2_BRACKET_SCREEN_S(acceptance_id)` as "compatibility wrapper[s]" that just call them. Every call site — `:650-651`, `:654`, `:658`, `:674` and all thirteen test references — uses the SCREAMING_CASE forms, so the two functions C4 actually named have **zero** callers outside the shims. The compatibility argument is void: the only consumers (`tests/test_mint_floor_artifact_generalized.py`) were edited in the same commit anyway, and repo-wide grep finds no other live reference. Net effect is a module-level name that still *reads* as the copied constant the spec deleted, now shadowing it with a call. Delete `:80-89` and use `allowance_rule_for` / `bracket_screen_s_for` at all call sites.

**SF2 — The schema's acceptance-id branch list is inlined twice, so a science-neutral r5 is two edits, not S7's "one list entry".**
The n17 set appears at `schema_v2.json:753-758` (finalProducer allOf) and `:1032-1037` (pinRequirements allOf); the n19 set at `:717-722` and `:996-1001`. The two conditionals necessarily constrain different subtrees (`cells[].postcollection` via `finalPostcollection` vs `cells[].allowance_contract` via `allowanceContract` — I verified those are the sole `$ref` sites of each `$def`), so the *branches* can't merge, but the **id sets** can: hoist `$defs.n19AcceptanceIds` / `$defs.n17AcceptanceIds` and `$ref` them, restoring the single-edit reissue property S7 is explicitly buying.

**SF3 — The public accessor hands out the live, mutable ONE-home mapping.**
`calibration_bracketing.py:222` returns `derivation["operatives"]` — the actual `_D102_N19_DERIVATION` / `_D102_N17_DERIVATION` sub-dict. Any caller of the new **public** API can mutate the authoritative derivation table in place for the whole process. In a lane whose entire premise is a single unforgeable authority, the accessor should return `MappingProxyType(operatives)` (the pattern is already used elsewhere in this test corpus) or a copy.

### NITS

- **N1 — Guard hole on a malformed `ratified_operatives`.** `calibration_bracketing.py:211-213` fires only when `supplied_operatives` is a `Mapping`. If `decimal_derivation.ratified_operatives` is present but is a list/string, the guard silently passes, whereas S2 says a supplied `ratified_operatives` whose `bracket_screen_s` does not equal the registered value refuses. Honest inputs are already authenticated upstream, so risk is low; a `not isinstance(..., Mapping)` refusal branch would close it.
- **N2 — Refusal message wording.** The amendment specifies `supplied acceptance operatives disagree with the registered generation` (`12-r2-debate-opus.md:46`); the implementation emits `supplied acceptance bracket_screen_s '…' disagrees with registered bracket_screen_s '…' for acceptance_id '…'` (`calibration_bracketing.py:215-221`). More informative, but if any downstream doc or test pins the ruled string, it will miss.
- **N3 — Crosswire guard not wired at two of three consumers.** `detection_floor.py:2354-2355` and `mint_floor_artifact_generalized.py:68-77` call the accessors without `acceptance=`. Behaviourally a no-op today — both sites only ever hold the 4-key pinset summary (`detection_floor.py:2102-2104` `_V2_ACCEPTANCE_KEYS`; `mint_floor_artifact_generalized.py:812-820`), which has no `decimal_derivation` — so the amendment's "identity stub ⇒ served from registry" clause is satisfied. Worth a comment so a future shape change doesn't silently drop the guard.
- **N4 — Message/check mismatch.** `floor_mint_estimator.py:148-151` says "must be a nonempty string" but only checks `isinstance(..., str)`; an empty id falls through to the (correct) unregistered refusal.
- **N5 — `if` blocks lack `required`.** The four `if` clauses (e.g. `schema_v2.json:699-714`) match on `properties.calibration_acceptance.properties.acceptance_id` with no `required`, so an instance missing `calibration_acceptance` vacuously satisfies **both** branches and must then satisfy two contradictory `const` pairs. Harmless in practice — `finalProducer.required` and `deskProducer.required` both list `calibration_acceptance`, and `$defs.calibrationAcceptance.required` lists `acceptance_id`, so such an instance already fails — but the conditional reads as fail-open until you check three other places.
- **N6 — Guard test file list is hardcoded.** `tests/test_mint_policy_resolver_guard.py:11-15` enumerates the three files literally, so a fourth mint-lane kernel file would be unguarded. This matches the ruling's wording ("kernel sources", three consumers) and the repo's own precedent (`tests/test_d117_floor_qwen25_7b_plan.py:1658`, `tests/test_d117_decode_contrast_plan.py:2189` use the same forbidden-list-over-fixed-source shape), so it is recorded, not charged.

---

## 3. Directed verifications (task items 1–6)

1. **Registry-authoritative / refuses unregistered / hybrid guard exactly as worded** — YES on all three. `calibration_bracketing.py:196-198` (sole authority), `:198`+consumer refusals (unregistered), `:200-221` (guard fires only when `decimal_derivation.ratified_operatives` is present; stubs served from registry). Guard is live on the estimator path (full artifact carries the operatives) and inert-by-shape on the other two. One hole: N1.
2. **Untouched surfaces** — ALL CONFIRMED. `_ACCEPTANCE_SELECTION` (`floor_mint_estimator.py:43`, literal `"issued_d116_artifact_only"` unchanged); `_v2_allowance_projection` (zero diff hits); symbolic forms (`detection_floor.py:521`, `:645`, unchanged text, no nearby hunk); golden block (old `:1276-1298`, now `:1284-1306` — the file's hunk boundaries are `@@ -1225` and `@@ -1350`, so the block lies strictly between and is untouched; I read the block and its constants are the same `8ac980a5…`/`a8c19555…`/`6fb779c2…`/`e795a3ea…`/`9f00ff35…`/`6325b71a…`/`258b512b…`); no `configs/`, no `arm_readiness*`.
3. **Genesis rename is rename-only** — YES. Value byte-identical; both call sites (`:690`, `:783`); comment matches S6's dictated content; no live reference to the old name survives anywhere in the repo. The three new accessors were added to `__all__` (`:2046-2048`); the renamed constant was never in `__all__`, before or after, so no export drift.
4. **Schema conditional over the n17 generation set** — YES in form (enum over the generation's ids, not a per-id branch), with the two-site duplication charged as SF2. The widened `enum`s at `:189-199` and `:470-480` are re-narrowed to a single value per generation by the conditionals, so no document can now assert a screen its own acceptance does not license — which is the property C5 was for.
5. **Guard-test scope matches the ruling** — YES. Three consumer files guarded (`tests/test_mint_policy_resolver_guard.py:11-15`); the ONE-home registry `joulewise/calibration_bracketing.py` correctly exempt (it must carry the literals); frozen pack content correctly out of scope; `scripts/floor_mint_pinsets/schema_v2.json` correctly out of scope (a JSON Schema cannot resolve at runtime, and S4 scopes the guard to "kernel sources").
6. **No anticipation of S1/S2/S3** — CONFIRMED. Zero occurrences of `r5`, `_v3`, `d117_*_v3`, or `freeze-0003` in the entire diff; no golden re-derivation; no pack emission; no acceptance-registry row added; `ACTIVE_ACCEPTANCE_ID`/`DEFAULT_ACCEPTANCE_BOUND_PATH` untouched. S0 is cleanly severable and genuinely r5-neutral: the schema branch already covers the n17 set that r5 joins, and `_live_acceptance_id()` tracks whatever the live default becomes (that automatic tracking is *itself* the defect in B1, but it does not encode r4 or r5).

**Sequencing note for the lead (not a finding):** per S8/S2 the goldens are re-derived ONCE against r5 at stage S2, so `tests/test_mint_floor_artifact_generalized.py` is expected to remain partially red after S0 — the golden block was correctly left alone. Any S0 report claiming that module green should be treated as suspect.
