# Results-fill registry audit against `draft-v1.md`

**Audited head.** `impl/r2-s0-mint-resolver` @ `4597ad4`, worktree `wtS0`, read-only.
**Registry under audit.** `docs/paper/results-fill-registry.md` (326 lines), authored at
commit `0e35990` (2026-08-09) and **never revised since**.
**Target under audit.** `docs/paper/draft-v1.md` (409 lines at this head), revised
fourteen times since `0e35990`.

Every registry row was located in the draft **by content**, not by line number. Line
numbers in the registry are known stale and are treated as untrusted throughout.

---

## 0. Verdict vocabulary used here

| Verdict | Meaning |
|---|---|
| `OK` | Target site found; the registry's locator, exact-marker string, and surrounding meaning are all still correct. |
| `STALE-REF` | Target site found and the exact-marker string still matches byte for byte; only locator metadata (line number, section number, table number) is wrong. Mechanically renderable today. |
| `ORPHANED` | The registry's recorded **exact marker string no longer exists anywhere in the draft**. A renderer keyed on that string matches zero sites. A replacement site exists in every case below, but the anchor must be re-bound before the row can render. |
| `SHIFTED` | The site exists but the surrounding draft text changed enough that the row's *binding* — not just its locator — needs a lead ruling. Flagged, never changed. |

A row may carry a secondary verdict; the primary verdict is the one that blocks rendering first.

---

## 1. Summary counts

### 1.1 Draft marker-site registry (34 rows)

| Verdict | Rows | Share |
|---|---|---|
| `OK` | **0** | 0% |
| `STALE-REF` (locator only; marker string intact) | **25** | 74% |
| `ORPHANED` (marker string gone from the draft) | **8** | 24% |
| `SHIFTED` (primary; binding needs a ruling) | **1** | 3% |
| — of which also carry a secondary `SHIFTED` | 2 (rows DS-02, DS-04) | — |
| **Total** | **34** | 100% |

**Not a single draft-site row is clean.** All 34 have at least a stale line reference,
because the draft has grown from 268 to 409 lines and its sections were renumbered.

### 1.2 Exact template-token registry (91 rows)

| Verdict | Rows |
|---|---|
| `OK` | **91** |
| `STALE-REF` / `ORPHANED` / `SHIFTED` | **0** |

These rows key on `DRAFT-RESULTS_PROSE.md`, not on the draft. That file is unchanged
since `0e35990`, and its census reproduces the registry's claim exactly:
**436 token occurrences, 91 distinct tokens.** Every producing output field cited in
the registry's source index was verified present at this head — see §4. Three
*cross-cutting* semantic flags (F1, F2, F5 in §5) nonetheless touch subsets of these
rows without invalidating any individual row's mechanics.

### 1.3 Coverage gap introduced this session

| | At `0e35990` (registry authored) | At `4597ad4` (this head) | Delta |
|---|---|---|---|
| Draft bracket-marker sites | 34 | **41** | +7 |
| Draft semantic fill slots | 35 | **43** | +8 |
| Sites with a registry row | 34 | 34 | 0 |
| **Sites with NO registry row** | **0** | **7** | **+7** |

The entire delta is one row of one table — see `DS-33` below. Seven live `[PENDING]`
sites and eight semantic slots in the draft currently have **no fill authority of any
kind**. That is the single most consequential finding in this audit.

### 1.4 Renderability

| | Rows |
|---|---|
| Mechanically renderable **today** (marker or table cell matches the row key as recorded) | 25 of 34 |
| Renderable **after the anchor refresh** in `registry-refreshed-DRAFT.md` | 33 of 34 |
| Requires a **lead ruling** before it can render at all | 1 of 34 (`DS-33`) + the 7 uncovered sites |

No row's fill shape broke in a way the refresh cannot repair, except `DS-33`.

---

## 2. What changed in the draft this session, and what it cost the registry

Four independent draft changes since `0e35990` account for every finding:

1. **Section renumbering** (`8ac9693`, "renumber figures by order of appearance and
   deduplicate table numbers", plus the later structural passes). Old §2 "Background
   and the gap" was folded into §1, so **every section number below it shifted down by
   one**; old §8 "Discussion" and old §10 "Limitations" merged into the current §7.
   Table numbers moved with them: draft **Table 1 → Table 2**, draft **Table 2 → Table 3**,
   and the characterization objectives table became the new **Table 1**.

   | Registry says | Draft now |
   |---|---|
   | Section 4 (detection-floor composition) | Section 3 |
   | Section 6 (instrument characterization) | Section 5 |
   | Section 7 (demonstration results) | Section 6 |
   | Section 11 (artifact availability) | Section 9 |
   | "Table 1" (phase results) | Table 2 |
   | "Table 2" (contrasts) | Table 3 |

2. **The v3 clock-anchor / era rewrite** (`53e480e`, `2952226`). Added §2 "Estimator
   revision as instrument evidence", the §4 capture-pipeline-era admission passage, and
   the §7 limitation "A corrected clock anchor retires every corpus collected before
   it". This orphaned no marker, but it **adds a fill precondition the registry never
   records** and **introduces two new terminal refusal codes** — flags F1 and F2.

3. **Marker-string rewording.** "CORRECTED ARTIFACTS" became "ISSUED ARTIFACTS" at both
   of its sites, and `[PENDING WINDOW C]` became `[PENDING CHARACTERIZATION CAMPAIGN]`
   at all six of its sites. This is the sole cause of all 8 `ORPHANED` verdicts. The
   rewording is *better* — "Window C" was internal shorthand the plain-language pass
   correctly removed — but a string-keyed renderer now matches nothing.

4. **D-122 compliance landing on the draft side** (`0a216b7`). The prompt-processing
   contrast, which the registry records as unregistered and floors-only, is now a fully
   registered arm with its own nine-column row. This is `DS-33` and the seven uncovered
   sites.

The **plain-language pass** (`2952226`) renamed two characterization rows and narrowed
their claims (flags F3 and DS-02 / DS-04) but moved no marker.

---

## 3. Row-by-row audit — draft marker-site registry

Row IDs `DS-01`…`DS-34` are assigned here in registry table order; the registry itself
has no row IDs.

### 3.1 Section-level holds

| ID | Registry locator (as written) | Registry exact marker | Current anchor (content-located) | Verdict | Exact fix |
|---|---|---|---|---|---|
| DS-01 | `Section 4 operative-floor hold, line 113` | `[RESULT PENDING CORRECTED ARTIFACTS]` | **line 145**, §3 "Measured, never-zero drift allowance", final sentence: "Operative floor values and their full decomposition for each demonstration stack are withheld until issued artifacts are available: **[RESULT PENDING ISSUED ARTIFACTS]**." | **ORPHANED** (+ STALE-REF) | Locator → `Section 3 operative-floor hold ("Measured, never-zero drift allowance"), line 145`. Marker → `` `[RESULT PENDING ISSUED ARTIFACTS]` ``. Supplier, fill rule (DERIVE), freeze status (DRAFT_GENERIC) and sources unchanged. |
| DS-08 | `Section 7 branch hold, line 190` | `[RESULT PENDING CORRECTED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into this draft.]` | **line 230**, §6 "Results", the whole line: `**[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into this draft.]**` | **ORPHANED** (+ STALE-REF) | Locator → `Section 6 branch hold ("Results"), line 230`. Marker → the same string with `CORRECTED` replaced by `ISSUED`; the remainder after the em dash is byte-identical. |
| DS-34 | `Artifact locators, line 264` | `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | **line 316**, §9 "Artifact availability", sentence end: "…and their repository and archive locators are published. **[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]**" | **STALE-REF** | Locator → `Section 9 artifact locators, line 316`. Marker string is byte-identical; do not touch. |

### 3.2 Characterization table (draft Table 1, §5) — six rows

All six sites are the final "Claim-bearing result" cell of the characterization
objectives table, now **draft Table 1** at §5 lines 199–206. All six markers changed
string identically. Two of the six row *labels* were also rewritten by the
plain-language pass, and in one case the rewrite narrows what the row claims.

| ID | Registry locator | Registry marker | Current anchor (row label at line) | Verdict | Exact fix |
|---|---|---|---|---|---|
| DS-02 | `Section 6 linearity row, line 159` | `[PENDING WINDOW C]` | **line 201**, row label **"Within-stack workload-response model"** (was "Linearity") | **ORPHANED** + **SHIFTED** | Locator → `Section 5 Table 1, workload-response row ("Within-stack workload-response model"), line 201`. Marker → `` `[PENDING CHARACTERIZATION CAMPAIGN]` ``. **Meaning flag — do not change:** see F3. |
| DS-03 | `Section 6 null row, line 160` | `[PENDING WINDOW C]` | **line 202**, row label "Null response across magnitudes" (unchanged) | **ORPHANED** | Locator → `Section 5 Table 1, null row, line 202`. Marker → `` `[PENDING CHARACTERIZATION CAMPAIGN]` ``. |
| DS-04 | `Section 6 empirical-floor row, line 161` | `[PENDING WINDOW C]` | **line 203**, row label **"Internal decision-path challenge"** (was "Empirical floor verification") | **ORPHANED** + **SHIFTED** | Locator → `Section 5 Table 1, decision-path row ("Internal decision-path challenge"), line 203`. Marker → `` `[PENDING CHARACTERIZATION CAMPAIGN]` ``. **Meaning flag — do not change:** see F3. |
| DS-05 | `Section 6 phase-attribution row, line 162` | `[PENDING WINDOW C]` | **line 204**, row label "Phase-attribution causal consistency" (unchanged) | **ORPHANED** | Locator → `Section 5 Table 1, phase-attribution row, line 204`. Marker → `` `[PENDING CHARACTERIZATION CAMPAIGN]` ``. |
| DS-06 | `Section 6 drift row, line 163` | `[PENDING WINDOW C]` | **line 205**, row label "Drift and settling" (unchanged) | **ORPHANED** | Locator → `Section 5 Table 1, drift row, line 205`. Marker → `` `[PENDING CHARACTERIZATION CAMPAIGN]` ``. |
| DS-07 | `Section 6 between-session row, line 164` | `[PENDING WINDOW C]` | **line 206**, row label "Between-session stability" (unchanged) | **ORPHANED** | Locator → `Section 5 Table 1, between-session row, line 206`. Marker → `` `[PENDING CHARACTERIZATION CAMPAIGN]` ``. |

**Fill shape confirmation.** The table's column structure is unchanged
(`Property | Planned characterization method | What a passing result would establish | Claim-bearing result`),
the marker still sits alone in the fourth cell of each row, and the row **order** is
unchanged, so the six-row positional mapping above is unambiguous. Each row remains
mechanically renderable once the marker string is re-bound.

### 3.3 Phase-results table (registry "Table 1" → draft **Table 2**, §6) — sixteen rows

Header, column order, em-dash blanks, and the four data rows are **structurally
identical** to `0e35990`. Every cell key still matches its registry row. The only
defects are the table number and the line numbers. The caption's wording changed
("sampler and output policy" → "token-selection and output policy") with no fill impact.

Current header, line 234:
`| Phase | Model | Gross J/request (lower, upper) | J per prompt token | J per output token | Cell floor (labelled) | n |`

| ID | Registry locator | Current anchor row | Verdict | Exact fix |
|---|---|---|---|---|
| DS-09 | `Table 1 prompt/1.5B gross cell, line 196` | line **236** `\| prompt processing \| 1.5B \| [PENDING] \| … ` col 3 | STALE-REF | `Table 2 (Section 6) prompt/1.5B gross cell, line 236` |
| DS-10 | `Table 1 prompt/1.5B per-token cell, line 196` | line **236**, col 4 (`J per prompt token`) | STALE-REF | `Table 2 (Section 6) prompt/1.5B per-token cell, line 236` |
| DS-11 | `Table 1 prompt/1.5B floor cell, line 196` | line **236**, col 6 (`Cell floor (labelled)`) | STALE-REF | `Table 2 (Section 6) prompt/1.5B floor cell, line 236` |
| DS-12 | `Table 1 prompt/1.5B count cell, line 196` | line **236**, col 7 (`n`) | STALE-REF | `Table 2 (Section 6) prompt/1.5B count cell, line 236` |
| DS-13 | `Table 1 prompt/7B gross cell, line 197` | line **237**, col 3 | STALE-REF | `Table 2 (Section 6) prompt/7B gross cell, line 237` |
| DS-14 | `Table 1 prompt/7B per-token cell, line 197` | line **237**, col 4 | STALE-REF | `Table 2 (Section 6) prompt/7B per-token cell, line 237` |
| DS-15 | `Table 1 prompt/7B floor cell, line 197` | line **237**, col 6 | STALE-REF | `Table 2 (Section 6) prompt/7B floor cell, line 237` |
| DS-16 | `Table 1 prompt/7B count cell, line 197` | line **237**, col 7 | STALE-REF | `Table 2 (Section 6) prompt/7B count cell, line 237` |
| DS-17 | `Table 1 decode/1.5B gross cell, line 198` | line **238**, col 3 | STALE-REF | `Table 2 (Section 6) decode/1.5B gross cell, line 238` |
| DS-18 | `Table 1 decode/1.5B per-token cell, line 198` | line **238**, col 5 (`J per output token`) | STALE-REF | `Table 2 (Section 6) decode/1.5B per-token cell, line 238` |
| DS-19 | `Table 1 decode/1.5B floor cell, line 198` | line **238**, col 6 | STALE-REF | `Table 2 (Section 6) decode/1.5B floor cell, line 238` |
| DS-20 | `Table 1 decode/1.5B count cell, line 198` | line **238**, col 7 | STALE-REF | `Table 2 (Section 6) decode/1.5B count cell, line 238` |
| DS-21 | `Table 1 decode/7B gross cell, line 199` | line **239**, col 3 | STALE-REF | `Table 2 (Section 6) decode/7B gross cell, line 239` |
| DS-22 | `Table 1 decode/7B per-token cell, line 199` | line **239**, col 5 | STALE-REF | `Table 2 (Section 6) decode/7B per-token cell, line 239` |
| DS-23 | `Table 1 decode/7B floor cell, line 199` | line **239**, col 6 | STALE-REF | `Table 2 (Section 6) decode/7B floor cell, line 239` |
| DS-24 | `Table 1 decode/7B count cell, line 199` | line **239**, col 7 | STALE-REF | `Table 2 (Section 6) decode/7B count cell, line 239` |

### 3.4 Contrast table (registry "Table 2" → draft **Table 3**, §6)

Current header, line 243:
`| Contrast | Point estimate | Interval [lower, upper] | Cell floor | Clearance (point − floor) | Claim-side bound | Floor-gate outcome | Direction-gate outcome | Verdict |`

**Decode row — line 245, eight markers / nine semantic slots. Unchanged in shape.**

| ID | Registry locator | Current anchor | Verdict | Exact fix |
|---|---|---|---|---|
| DS-25 | `Table 2 decode point estimate, line 205` | line **245**, col 2 `[PENDING]` | STALE-REF | `Table 3 (Section 6) decode point estimate, line 245` |
| DS-26 | `Table 2 decode interval, line 205` | line **245**, col 3 `[PENDING, PENDING]` | STALE-REF | `Table 3 (Section 6) decode interval, line 245`. The "one bracket marker contains two semantic fills" note remains correct. |
| DS-27 | `Table 2 decode floor, line 205` | line **245**, col 4 | STALE-REF | `Table 3 (Section 6) decode floor, line 245` |
| DS-28 | `Table 2 decode clearance, line 205` | line **245**, col 5 | STALE-REF | `Table 3 (Section 6) decode clearance, line 245`. The recorded `DRAFT/TEMPLATE SHAPE MISMATCH` (draft has one unconditional clearance cell; the template branches clearance vs shortfall) is **still live and unrepaired**. |
| DS-29 | `Table 2 decode claim-side bound, line 205` | line **245**, col 6 | STALE-REF | `Table 3 (Section 6) decode claim-side bound, line 245`. Still `SUPPLIER_UNKNOWN` — see F5. |
| DS-30 | `Table 2 decode floor-gate outcome, line 205` | line **245**, col 7 | STALE-REF | `Table 3 (Section 6) decode floor-gate outcome, line 245`. `TOKEN_MISSING` still live. |
| DS-31 | `Table 2 decode direction-gate outcome, line 205` | line **245**, col 8 | STALE-REF | `Table 3 (Section 6) decode direction-gate outcome, line 245`. `TOKEN_MISSING` still live. |
| DS-32 | `Table 2 decode verdict, line 205` | line **245**, col 9 | STALE-REF | `Table 3 (Section 6) decode verdict, line 245`. `TOKEN_MISSING` still live. |

**Prompt row — line 246. This is the one broken row.**

| ID | Registry locator | Registry binding | Current anchor | Verdict |
|---|---|---|---|---|
| DS-33 | `Table 2 prompt floor, line 206` | One `[PENDING]`; "No prompt claim-floor token exists; D-122 now requires a prompt contrast rather than floors-only prose"; `STOP_FILL`; `SUPERSEDED_DRAFT / TOKEN_FAMILY_MISSING` | line **246**: `\| prompt processing, 7B − 1.5B \| [PENDING] \| [PENDING, PENDING] \| [PENDING] \| [PENDING] \| [PENDING] \| [PENDING] \| [PENDING] \| [PENDING] \|` — **eight markers, nine semantic slots** | **SHIFTED (major)** |

**What happened.** At `0e35990` this row read:

```
| prompt processing, 7B − 1.5B | not registered under the adopted default | not registered | [PENDING] | not applicable | not applicable | not evaluated | not evaluated | floors only |
```

— a single floor cell surrounded by prose disclaimers. The registry row correctly
described *that*. Commit `0a216b7` registered the D-122 prompt-processing arm on the
draft side (§6 "Pre-registered design" now reads "The registered demonstration contains
two model-size directional contrasts: one for token generation and one for prompt
processing under a fixed synthetic 256-token prompt", and Table 3's caption became "The
two pre-registered contrasts"). The row is now structurally identical to the decode row.

**Consequences.**

- The registry's `DS-33` row now describes a site that no longer exists as described.
  Its `SUPERSEDED_DRAFT` status is inverted: the *draft* is now current and the
  *template* is the superseded artifact.
- **Seven draft marker sites and eight semantic slots at line 246 have no registry row
  at all** — point estimate, both interval endpoints, clearance, claim-side bound,
  floor-gate outcome, direction-gate outcome, and verdict. Only the floor cell (col 4)
  is arguably covered, and only by a row whose stated binding is "no prompt claim-floor
  token exists".
- No prompt-side token family exists in `DRAFT-RESULTS_PROSE.md` to bind them to. The
  template still carries decode-only contrast tokens; the registry's own discrepancy
  table anticipated exactly this.

**Fix — lead-owned, NOT applied here.** In `registry-refreshed-DRAFT.md` only the
locator is updated to `Table 3 (Section 6) prompt-processing contrast row, line 246`;
every semantic column is left byte-identical. The real repair requires, in order:

1. Add a guarded prompt token family to the template mirroring the decode family
   (`E_prompt_contrast_signed_J_per_request`, `_lower_J`, `_upper_J`,
   `M_prompt_contrast_abs_J_per_request`, `F_claim_prompt_armwise_max_J`,
   `B_prompt_claim_J`, `C_prompt_floor_clearance_J`, `S_prompt_floor_shortfall_J`,
   `R_prompt_effect_x_floor`, `S_prompt_joint_J`) — names illustrative, the lead names them.
2. Add eight new draft-site rows for line 246.
3. Rewrite `DS-33` from `SUPERSEDED_DRAFT / TOKEN_FAMILY_MISSING` to a live binding.
4. Update the census (draft sites 34 → 41, slots 35 → 43; registry rows 125 → 133+).
5. Resolve the same `TOKEN_MISSING` gate/verdict gap that already blocks DS-30 – DS-32,
   now doubled across both arms.

---

## 4. Source-index verification (all `OK`)

Every file and output field the registry names as a supplier was checked at `4597ad4`:

| Registry source | File | Status | Fields verified |
|---|---|---|---|
| `TPL` | `docs/process_traces/2026-08-07-plan-factory/DRAFT-RESULTS_PROSE.md` | present, unchanged | census 436 occurrences / 91 distinct — **matches registry exactly** |
| `LINT` | `.../lint_results_prose_template.py` | present | — |
| `DF` | `joulewise/detection_floor.py` | present | `build_floor_cell` (:1579) emits `floor_abs_j` `floor_cmp_j` `floor_gate_j` (:1638-40), `point_floor_diagnostics` (:1658), `published_claim_floor` (:799) |
| `FX` | `joulewise/floor_extraction.py` | present | `as_row` (:1228, :1304), `refusal_reasons` (:1271, :1369), `terminal_refusal_reasons` (:1288), `all_cells_extractable` (:1439) |
| `WV` | `scripts/run_campaign.py` | present | `member_failures` (:3921), `idle_admission_core` (:3915, :4397) |
| `CV` | `joulewise/analysis_engine/__init__.py`, `claims.py` | present | `_contrast_row` (:1544), `deterministic_bounds` (:1606), `decision_interval` (:1573) |
| `MINT` | `docs/phase_2/floor_mint_contract.md` | present | — |
| `AUTH` | `docs/decision_log.md` | present | D-117, D-119, D-121, D-122, D-123, D-124 all present |
| `PLAN` | `docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md` | present | — |

**No template-token row is broken by a renamed or removed field.** The 91 exact-token
rows are `OK` as written.

---

## 5. Flagged rows and cross-cutting semantic issues — lead ruling required

These are recorded, never repaired. None is applied in `registry-refreshed-DRAFT.md`.

### F1 — New terminal refusal codes are not in the registry's known-code set
**Severity: blocks rendering of up to 6 rows, silently.**

The era work registered two new refusal codes:
`joulewise/floor_extraction.py:190-191` adds `capture_pipeline_absent` and
`capture_pipeline_superseded`; `joulewise/whole_window.py:199` carries the same pair;
`joulewise/uncertainty_evidence.py:1299-1324` defines
`CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})` and returns one of the two
codes for anything else.

These codes flow into `cells[].refusal_reasons`, which is precisely the supplier for
rows `[TERMINAL_REFUSAL_REASON_1p5B_prompt]`, `…_1p5B_decode`, `…_7B_prompt`,
`…_7B_decode` and the two `[REFUSAL_REASON_*_floor_window]` rows. Those rows say
**"STOP_FILL on unknown code"**. Unless the conservative renderer's known-code set is
extended, an era-refused cell — which is the *expected* state for anything not
collected under the current pipeline — will STOP_FILL for the wrong reason: not
"refused because the capture pipeline is superseded", but "refused because the renderer
did not recognise the code". The distinction the code deliberately preserves
(`absent` vs `superseded`, per draft §4: "a missing record is never confused with an
out-of-date one") would be destroyed at the rendering boundary.
**Ruling needed:** extend the renderer's closed code set and the six rows' resolution
notes, or state explicitly that unknown-code STOP_FILL is the intended behaviour here.

### F2 — The registry's historical-evidence preamble is now weaker than the draft
**Severity: registry understates a binding precondition.**

Registry lines 12–16 justify "No historical result is a supplier for this registry" on
**D-117 prospectivity alone**. Draft §7 now states a second, independent, and
*mechanical* exclusion: "the admission check of Section 4 refuses any bundle whose
stored anchor method is not the current one, and there is no path that would go back
and recompute a stored run's claim energies under the new method."

The draft even cites this registry as its authority for the first ground — a live
cross-reference at draft line 260 pointing at `docs/paper/results-fill-registry.md`.
The registry should now record capture-pipeline era as a fill precondition in its own
right, so that a future reader cannot conclude that a re-registered historical corpus
becomes a supplier.
**Ruling needed:** whether to add an era clause to the preamble. Not a locator change,
so not applied.

### F3 — Two characterization row bindings were semantically narrowed
**Severity: token names now overstate what the draft rows claim.**

- `DS-02`: "Linearity" → **"Within-stack workload-response model"**. The old row
  promised "Energy would respond proportionally over the tested dynamic range, and the
  fitted per-token slope could serve as the known-effect [basis]". The new row promises
  only "A good fit would let us interpolate between the output lengths measured on this
  stack, and nothing more. It would not show that the counter itself is linear…". The
  tokens `[S_C_linearity_request_J_per_token]`, `[S_C_linearity_decode_J_per_token]`,
  `[R_C_linearity_limit_J]`, `[PLAIN_LANGUAGE_RESULT_linearity]` still fit mechanically
  — they are slopes and a residual criterion — but the word *linearity* in the token
  family now names something the draft explicitly declines to claim.
- `DS-04`: "Empirical floor verification" → **"Internal decision-path challenge"**. The
  new row states outright: "it would not independently verify the floor in joules.
  Verifying the floor physically needs an input or reference characterized by something
  other than this instrument." The tokens `[R_C_micro_min_x_floor]`,
  `[R_C_micro_max_x_floor]`, `[PLAIN_LANGUAGE_RESULT_floor]`,
  `[D_C_micro_diagnostic_x_floor]` remain mechanically correct (they *are*
  effect-to-floor ratios), but `PLAIN_LANGUAGE_RESULT_floor`'s closed phrase set was
  presumably written for a row that claimed floor *verification*.

**Ruling needed:** whether the closed phrase sets behind
`PLAIN_LANGUAGE_RESULT_linearity` and `PLAIN_LANGUAGE_RESULT_floor` still express only
what the rewritten rows license. Token names are binding vocabulary and must **not** be
renamed to chase the prose.

### F4 — The discrepancy row "Gamma prompt-processing contrast" is now factually wrong
**Severity: recorded conflict misdescribes the current state.**

The row reads: "The draft calls it unregistered and the template contains decode-only
contrast tokens; D-122 requires the prospectively frozen prompt arm in gamma."
The first clause is **false at this head** — the draft registers the arm (§6
"Pre-registered design"; Table 3 caption "The two pre-registered contrasts"; the Holm
`m=2` family). The conflict is now **template-only and one-sided**, which makes it more
urgent, not less: the draft is writing cheques the token vocabulary cannot cash.
**Ruling needed:** rewrite the conflict description. Meaning-bearing, so not applied.

### F5 — The comparative-floor rows have an undeclared estimator dependency
**Severity: a value basis could change without any registry row changing.**

Draft §7 "Validated tighter estimator, registered for the next mint" records that
`d124_two_shared_edge_common_mode.v1` is pre-registered and selected for six shared-edge
comparative cells, and the draft carries a byte-fenced `CONDITIONAL-INSERT-TIGHTER-FLOOR`
swap block (lines 357–409) that rewrites five passages if the estimator lands before
freeze. The registry's `[F_*_cmp_J]` rows and the whole gamma contrast family cite
`DF`, `MINT`, `CV` but **name no estimator**, and the registry has no row or note
recording that the comparative component's basis is estimator-selected.

This is consistent with the draft's own rule that "estimator identity is not accepted
from result or floor-artifact data" — the identity lives in the pre-registration — but
it means a reader of the registry alone cannot tell that two different authenticated
artifacts could legitimately supply two different `floor_cmp_j` values for the same
cell. The figures-plan's cross-figure rule already obliges a D-124 disclosure beside any
consuming contrast.
**Ruling needed:** add an estimator-provenance note to the registry preamble, or rule
that pre-registration is the sole and sufficient home.

### F6 — Discrepancy row "Global work-selection checkpoint" is stale context
**Severity: cosmetic, but it is a governance row.**

The row asks the lead to "confirm this direct delegated branch is intentionally outside
ordinary queue selection before merge review", referring to the branch that existed at
`0e35990`. That branch is long merged; the current head is `impl/r2-s0-mint-resolver`.
**Ruling needed:** retire the row or re-scope it.

### F7 — Template variant names still track the OLD draft section numbers
**Severity: renderer could select against a section number that no longer exists.**

`DRAFT-RESULTS_PROSE.md` names its variants `§7 Variant A`, `§7 Variant B1`, …,
`§6 Variant 0`, `§6 Variant A`, … . Those `§6`/`§7` labels were the *draft's* section
numbers at authoring time; the corresponding draft sections are now **§5**
(characterization) and **§6** (results). The registry inherits the names in its `TPL`
source entry, in the `[CELL_NONPUBLICATION_SUMMARY]` row ("gamma Section 7 variant
selector"), in the `DS-08` supplier ("Exactly one guarded Section 7 template variant"),
and in the lead-checklist bullet "before using any Section 6 token".

These are **frozen template vocabulary** and are deliberately left untouched in the
refresh. But the collision is real: "Section 6" now means the characterization variants
in template-space and the results section in draft-space.
**Ruling needed:** either rename the template variants at the next template revision, or
record explicitly in the registry that `§N Variant X` names are template-internal and
never draft section references. The latter is cheaper and loses nothing.

### F8 — `docs/paper/figures/README.md` section references are stale (out of registry scope)
Not a registry row, but found while reading the figure conventions and worth one line:
the schematic-figures README places `fig1` in "§4", `fig2` in "§3 and §5", and `fig3` in
"§4". At this head the draft embeds `fig2` in **§2** (line 68), `fig1` in **§3**
(line 120), and `fig3` in **§3** (line 161). Same off-by-one as everything else.

---

## 6. What was and was not changed in `registry-refreshed-DRAFT.md`

**Changed — references and anchors only:**

| # | Change | Rationale |
|---|---|---|
| 1 | `DRAFT` source entry: "especially Sections 6 and 7" → "especially Sections 5 and 6" | draft section renumber; this entry describes the *draft* |
| 2 | Draft-site table preamble: line-reference disclaimer now names the audited commit | locator provenance |
| 3 | All 34 `Draft site` locator strings: section numbers, table numbers, line numbers | content-located at `4597ad4` |
| 4 | 8 `Exact marker` strings re-bound (`CORRECTED`→`ISSUED` ×2, `[PENDING WINDOW C]`→`[PENDING CHARACTERIZATION CAMPAIGN]` ×6) | the recorded string matches nothing in the draft; the marker column is a locator |
| 5 | Census bullets: current draft site/slot counts added, **with the original `0e35990` counts retained inline** | factual description of the anchor target |
| 6 | Lead-checklist bullet: "the missing Table 2 outcome tokens" → "Table 3" | draft table renumber |
| 7 | One added `### Anchor-refresh note` block under the draft-site table | records what the refresh did and points at this audit |

**Deliberately NOT changed:**

- Any `Intended supplier / binding token`, `Campaign / cell`, `Fill rule`,
  `Freeze status`, or `Sources` value, in any of the 125 rows.
- Any of the 91 exact template tokens or their bindings.
- Any `§6` / `§7` reference that names a **template variant** (`TPL` source entry,
  `[CELL_NONPUBLICATION_SUMMARY]`, the `DS-08` supplier, the "any Section 6 token"
  checklist bullet) — frozen vocabulary, see F7.
- The four authority-discrepancy rows, including the two now factually wrong (F4, F6).
- `DS-33`'s semantics, and no new rows for the seven uncovered sites.
- The `Registry: 91 … plus 34 draft-site rows, for 125 fill rows` total — unchanged
  because no row was added or removed.

---

## 7. Recommended order of repair (for the lead)

1. **Land the refreshed anchors** (`registry-refreshed-DRAFT.md`). Zero-risk; restores
   33 of 34 rows to renderable-as-recorded.
2. **F1** — extend the terminal-refusal known-code set. This is the only flag that can
   cause a *silent wrong refusal reason* in a rendered paper.
3. **DS-33 + F4** — the prompt token family. Largest scope; blocks 8 semantic slots and
   an entire registered arm of the demonstration.
4. **DS-28, DS-30 – DS-32** — the pre-existing clearance-branch mismatch and three
   `TOKEN_MISSING` gate/verdict cells, which DS-33 will double.
5. **F2, F5** — preamble notes on era and estimator provenance.
6. **F3, F6, F7, F8** — vocabulary and stale-context cleanups.
