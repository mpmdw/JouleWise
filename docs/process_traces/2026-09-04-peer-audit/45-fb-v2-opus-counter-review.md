# 45 — Opus counter-review (CONTRACT lens), FB metadata .v2

Branch `feat/2026-09-04-fb-metadata` @ `c1681066`; `git diff origin/main...HEAD`
(27 files). Evidence below executed this session.

## Evidence

- 7/7 briefed modules pass one at a time under `PYTHONDONTWRITEBYTECODE=1`, in briefed
  order: 4, 11, 161 (skipped=1), 64, 168, 40, 47 tests — all OK.
- Frozen bytes: `git rev-parse HEAD:<p>` == `origin/main:<p>` for all five carriers, and
  recomputed sha256 match the pins in reports 34/40 (mint1 `559ab5ed…1188a8`,
  alpha-extraction `5bd4d748…`, alpha-floor `ecea77fc…`, beta-extraction `06f9b63d…`,
  beta-floor `da611926…`). The only digest pinned outside process traces is
  `559ab5ed…`, in two `docs/strategy/2026-08-07-paper-portfolio/proposals/` files —
  unchanged. All five carry only `.v1`; **no `.v2` object exists anywhere in the repo
  yet** (bears on S1).

## Findings

**S1 (should-fix) — the v2 `note` says two gates; acceptance needs three.**
`joulewise/detection_floor.py:399-401`, mirrored verbatim at `adapter_contracts.md:660`,
`detection_floor.md:155`, `site/adapter_contracts.html:84`. `claims.py:378-380` also
requires `adjusted_rejected`, else `multiplicity_not_rejected`/`unresolved`. The D-083
addendum says "…plus multiplicity and evidence/eligibility requirements" and both docs'
prose carries that clause — only the wire note drops it. These bytes freeze when the
first v2 artifact mints; none exists yet, so the fix is free now, impossible later.
Proposed value at all four sites:
`"Acceptance is separate gates: |estimate| > F, zero-exclusion of both intervals, and
the multiplicity and evidence/eligibility requirements; for symmetric intervals the
first two reduce to |estimate| > max(F, h+B), actual endpoints govern otherwise."`
(rebuild the HTML via `scripts/build_site.py`; the census pin at
`tests/test_single_count_discipline_census.py:992` will confirm, not obstruct).

**S2 (should-fix) — `docs/phase_2/detection_floor.md` v2 block is not pinned to code.**
`tests/test_single_count_discipline_census.py:994` pins only `adapter_contracts.md` and
`site/adapter_contracts.html`; the third v2 copy at `detection_floor.md:144` is
unguarded, as is the frozen v1 block in all three — and v1 is the version whose byte
stability the ruling protects. Proposed at `:993-998`: add
`"docs/phase_2/detection_floor.md"` to the `relative` tuple, and wrap the body in an
inner loop over `("v1", …(SINGLE_COUNT_DISCIPLINE_ID_V1))` and `("v2", …())` that
substitutes the version into the existing `rule_id` regex and asserts exactly one
match equal to that object per (document, version) pair.

**S3 (should-fix) — the census scans only two directories.**
`tests/test_single_count_discipline_census.py:84-85` rglobs `joulewise/` and `scripts/`
only, so a future supplier under any new package (`analysis/`, `site_capsule/`, …)
escapes it entirely — the exact failure class this cure exists to close. No present
miss: the only marker-matching `*.py` outside those roots is a frozen paper-i exhibit
copy. Proposed: keep the pinned roots, add a closed-world test enumerating `git ls-files
'*.py'` and asserting no `MARKERS` hit outside them plus
`EXEMPT_TREES = ("tests", "docs/process_traces")`.

**N1 (nit) — `DisciplineV2` subclasses `DisciplineV1`** (`detection_floor.py:438`), so
`isinstance(v, DisciplineV1)` is True for v2. The one isinstance site
(`mint_floor_artifact.py:1940`) tests `DisciplineV2` first, so it is correct today.
Harden with a private `_DisciplineView` base, or dispatch on `view.rule_id`.

**N2 (nit) — grep backstop pins exact line text** (`:250-253`): a pure reflow in the six
owning files forces a manifest regeneration. Right for the D-174 window; record the cost
so it is a post-submission decision, not a surprise.

**N3 (nit) — headings omit the governing addenda.** `adapter_contracts.md:608`
still reads "(D-078 clause 11, Ed-ratified 2026-07-25)"; append "; amended by the D-078
and D-083 dated addenda, 2026-09-04", and at `detection_floor.md:141` add "as amended by
their 2026-09-04 dated addenda".

## Answers

1. **Docs vs emitted — exact.** I parsed each fenced JSON block and compared it to
   `attribution_single_count_discipline()` / `…(SINGLE_COUNT_DISCIPLINE_ID_V1)`, key
   ORDER included: `adapter_contracts.md:634` v1, `:649` v2; `detection_floor.md:129`
   v1, `:144` v2; `site/adapter_contracts.html:65` v1, `:74` v2. Six of six, zero
   drift. The version rule (`adapter_contracts.md:678-681`,
   `detection_floor.md:168-172`) matches `read_single_count_discipline`
   (`detection_floor.py:445-482`) and `check_single_count_cohort` (`:484-494`): dispatch
   on embedded `rule_id`, exact set+value+`type()` equality (`:474`, so `1`/`True`
   cannot pass), unknown ids and mixtures refuse, never normalize. Gap: S2.
2. **Addenda vs code — consistent.** At `claims.py:343`, `:368-380`: `abs(estimate) <=
   floor` refuses (strict `|estimate| > F`) and `interval[0] <= 0 <= interval[1]`
   refuses on EITHER interval (strict zero-exclusion of both), so `max(F, h+B)` is an
   accurate symmetric-case reduction and both docs correctly say endpoints govern
   otherwise. Only the wire note omits the multiplicity/eligibility clause — S1.
3. **Frozen artifacts — clean.** Five byte-identical, digests recomputed, the one
   external pin unchanged. The sixth rehearsal file, `…-gamma-claim-verdicts.json`,
   carries no `floor_limit_class` or discipline object, so
   `_validate_claim_discipline_cohort` admits nothing — not a miss.
4. **Accessor surface — sound.** All seven public names — `read_single_count_discipline`,
   `read_single_count_profile`, `check_single_count_cohort`,
   `attribution_single_count_discipline_is_canonical`, `SingleCountDisciplineError`,
   `DisciplineV1`, `DisciplineV2` — are in `__all__` (import-verified). Views are
   frozen dataclasses whose only wire exit is `copy_wire()`. "No raw reads" is
   mechanical: any new raw `single_count_discipline`/`rule_id` read classifies
   `RAW-UNCLASSIFIED`, proven by five in-memory mutations at `:957-980` plus 19 pinned
   delegate EDGES. Exemptions are exactly — **3 `RAW_EXCEPTIONS`**: two parser reads inside
   `read_single_count_discipline`, plus `resolution.single_count_discipline` inside the
   `read_floor_resolution_discipline` adapter. **6 `EMITTERS`**:
   `detection_floor.{attribution_single_count_discipline,_add_attribution_limit_metadata,
   build_floor_cell,build_transport_group}`, `floor_extraction.{CellReport.as_row,
   extract_cells}`. **2 `VOCABULARY`**: `floor_extraction.{_D117_MINT_REPORT_OPTIONAL_KEYS,
   _D117_MINT_CELL_OPTIONAL_KEYS}`. Plus a fourth the brief did not name —
   **7 `SCHEMA_DECLARATIONS`**, key-name literals inside a `Set`/`Tuple` only:
   `detection_floor.{_ATTRIBUTION_LIMIT_RECORD_KEYS,_ATTRIBUTION_LIMIT_CONTAINER_KEYS}`,
   `artifact.{_ATTRIBUTION_FLOOR_KEYS,_FLOOR_LIMIT_KEYS}`, `claims.evaluate_claim`,
   `inputs.{FloorResolution,resolve_floor}`. All declare key names, none reads a value, and the `isinstance(parent, (ast.Set, ast.Tuple))` guard at `:240`
   stops the exemption stretching to a dict-value read. Residual: S3, N1.
5. **Supersession — nothing further owed.** `.v2` is authorized in terms by text already
   ratified on `main`: D-078 addendum "new disclosures use a versioned rule"
   (`decision_log.md:10948`) and D-083 addendum "New metadata retains
   `both_terms_required:true`, states `gating:false`, and uses a distinct rule version
   with version-aware consumers; legacy objects retain exact bytes" (`:10970-10973`).
   D-083's older body at `:5326-5328` ("effective bar … ≈ 5 J … stays") is superseded by
   its own dated addendum. On the brief's premise: the literal `SUPPLIER_PENDING` occurs
   nowhere in this repo (whole-tree grep), and `results-fill-registry.md:226-267` are the
   D-165 R / R_cm DERIVE rows (`UNRESOLVED-UNTIL-G2A / VALUE_UNISSUED`,
   `REGISTERED_NOT_APPLICABLE`); none binds `single_count_discipline` or a rule version,
   so nothing there is for this branch and no registry addendum is required. Out-of-scope
   cross-lane note: `draft-v1.md:287` keeps Table 3's "Sizing sum F+B; signed clearance"
   column (DS-28 `:881`, PG-04 `:890`) — compatible with prospective-sizing framing;
   paper lane to confirm at fill.
6. **Overbuild — no.** The accessor + census + matrix is the cure consult 42 ruled after
   four rounds each missed a consumer, and is the first mechanism here turning "a consumer
   was missed" into a test failure. Cost sits in the pinned manifest (N2) — a
   maintenance burden, not scope creep. Nothing exceeds the ratified Q-17-3 shape.

## Verdict

**LANDABLE** — with S1 taken before merge: a string change plus a site rebuild, free
today and impossible once the first v2 artifact mints. S2 and S3 close forward-looking
holes in the guard and can land in the same commit; N1–N3 optional. No blocker: every
ratified Q-17-3 requirement — non-gating v2 shape, `both_terms_required: true`,
`gating: false`, version-aware dispatch, frozen v1 bytes, unchanged two-gate rule — is
present, documented exactly as emitted, and mechanically enforced.


