# REFUTE-F — fact-and-regression lens (Opus, read-only)

Object: `feat/2026-09-02-paper-f` @ `4cb31a75` in `/Users/edr/code/JouleWise-wt-paper-f`, diffed against main `33290b8b`.
Charge: falsify (1) no cure changed a factual claim, (2) the `U_edge`→`U_corner` unification is complete and altered no formula, (3) the excluded regions are byte-identical, (4) the new regression fixture fails pre-cure / passes cured / bites under mutation, (5) nothing outside WRITE_SCOPE.
Nothing was written under either checkout; all scratch under `…/scratchpad/paper/refute-f-tmp/`. Canonical checkout `/Users/edr/code/JouleWise` and the seat worktree were both `git status --porcelain` clean before and after.

**Counts: 2 blockers, 4 should-fix, 4 nits.** Charge items 2, 3 and 5 could not be falsified (5 with one nit-level exception). Charge 1 is falsified twice. Charge 4 is falsified in part: the fixture is synthetic and the suite does not bind most cures.

---

## BLOCKER B1 — cure 14 deleted a real, implemented check; the paper's sampling-flag sentence is now false

Draft `docs/paper/draft-v2-skeleton.md:324-325` (was main `:292-293`):

> `- of its window, while sampling flags mark cadence below its fixed ratio or too`
> `- few in-window sampler records.`
> `+ of its window, while sampling flags mark too few in-window sampler records.`

and the matching ledger row `:1679` ("Mark too few in-window sampler records."). The seat's stated ground (report row 14) is "no ratio exists in the registry or round7 artifacts".

Falsifying evidence — the ratio and its two fixed thresholds are production code, and two of the **three** conditions that raise the flag are cadence-ratio conditions:

`joulewise/reduce.py:983-988`
```python
    gap_stats = _window_gap_stats(curve, window)
    cadence_ratio = gap_stats["cadence_ratio"]
    if cadence_ratio is None:
        reasons.append("cadence_ratio_unrecorded")
    elif cadence_ratio < cadence_ratio_min:
        reasons.append("cadence_ratio_below_threshold")
```
`joulewise/reduce.py:116-118`
```python
MIN_PHASE_SAMPLES = 3
SHORT_WINDOW_CADENCE_RATIO_MIN = 2.0
REQUEST_WINDOW_CADENCE_RATIO_MIN = 4.0
```
`joulewise/reduce.py:1093-1095` — `cadence_ratio = window.duration_s / denominator` (denominator = `max(window_p95_sample_gap_s, bracketing_max_sample_gap_s)`); call sites pass the fixed minima at `reduce.py:594, 608, 632, 647, 662, 677, 3398, 3414, 3438`. Both reason codes are consumed as sampling flags at `joulewise/whole_window.py:202-203` and `:229-230`, and carried into the receipt schema at `joulewise/window_duration_margins.py:780-781, 1094-1099` (including `"reducer_cadence_ratio_threshold"` and the guard `raise ValueError("receipt cadence threshold is not reducer-derived")`).

Why the ground fails: the deleted clause printed **no number** — "cadence below its fixed ratio" names the predicate without stating 2.0 or 4.0, so the registry rule ("no new number at the desk") never required its deletion. The diff traded an accurate qualitative sentence for an incomplete one, in a methods section whose stated bar is replication. Cheapest cure: restore the original clause verbatim.

## BLOCKER B2 — cure 4 names a custody mechanism that does not exist

Draft `:173-174`: "Its recorded SHA-256 values, which identify exact file bytes, **must match the frozen plan's calibration entry**" (main `:163`: "must match the fixed record").

Falsifying evidence — no plan holds an expected calibration digest; the check runs against the capture's own in-bundle manifest, and the plan's own hash is verified in the *opposite* direction:

`joulewise/reduce.py:1241-1256`
```python
        for relative, expected_sha256 in manifest["artifacts"].items():
            member = contained_file(relative, base=manifest_file.parent)
            ...
            if hashlib.sha256(member_raw).hexdigest() != expected_sha256:
                return None, "instrument_calibration_invalid"
```
with the manifest self-authenticated at `reduce.py:1234-1240` against `calibration.get("validation_manifest_sha256")` — a value recorded in the bundle.

`joulewise/calibration_ledger.py:767-784` (`_valid_session_slot_reservation`) admits exactly `attempt_id`, `custody_locator`, `expected_time_role`, `identity_epoch`, `t1_bindings` — **no digest**; the capture hashes are derived at finalization (`calibration_ledger.py:5101-5110`).
`joulewise/calibration_ledger.py:4626-4647` hashes the *plan file* and compares it to the ledger session's pin (`expected_sha256=session.plan_sha256`, callers `:4697-4701`, `:5078-5082`).
The acceptance file's digest comes from an in-code registry: `joulewise/calibration_bracketing.py:735-741` against constants at `:130-170` (`ISSUED_ACCEPTANCE_BOUND_SHA256`, …).

The pre-cure wording was compatible with both real mechanisms; the cured wording is not. A replicator following `:173-174` would look for a calibration entry in the plan and find none.

---

## SHOULD-FIX S1 — cure 23 asserts a figure the draft never embeds

`:846` now reads "Figure 3 shows three separate paths from the same authenticated evidence…" (main `:803`: "**Figure 3 is required here.**"). But the draft contains **no** image reference for Figure 3: `grep -n "figures/fig"` returns only `:168` (Figure 1) and `:206` (Figure 2). `docs/paper/figures/fig3_decision_gates.svg` exists on disk but nothing in the draft points at it, and the build note at `:881` still instructs "Build Figure 3 from three distinct paths". The cure converted a build instruction into a present-tense claim without adding the embed, so the compiled paper says a figure is shown that is not there, and the build note now contradicts the body. (The seat report's F3 notes the stale build note but records the figure as referenced.)

## SHOULD-FIX S2 — cure 15's deletion orphans "workload level" and leaves §3 self-contradictory

Deleting the "Workload response" and "Identical-condition response" rows (main `:306-307`) has three reader-facing consequences beyond the seat's own F1 note:

1. **The first-use defect survives the cure.** Main `:306` was the *only* gloss of "workload level" ("Complete every registered (fixed-before-collection) workload level"). After deletion the term's surviving uses are `:1211` and `:1213` ("Future work"): "its workload levels, meter synchronization…"; "At each workload level already registered for the campaign…" — no definition anywhere in the draft. Verified: `grep -n "workload level"` on main → `306, 1171, 1173`; on head → `1211, 1213` only. No ledger row covers the term, so the hardened test cannot see it.
2. **§3 promises four questions and answers two.** `:222` still opens "Instrument characterization asks four physical questions", and the prose that serves the two deleted rows survives in full (`:246-251` independent unit / slope / residual; `:253-270` the block-interval and comparator construction), but the specification table now has only the phase-accounting and drift-and-recovery rows.
3. **Registry anchor dangles.** `docs/paper/results-fill-registry.md:822` (`DS-02`) binds the "`**Workload response:**` content anchor", which no longer exists. (Registry is outside seat F's scope — this is a coordination item, not a scope breach.)

## SHOULD-FIX S3 — the §1 corner definition over-specifies and now conflicts with §4's shared-movement numerator

Main `:117-118`: "\(U_{\rm edge}\) its counterpart **after allowed movement**. Any required \(U_{\rm edge}/U_{\rm point}<2\) falsifies the claim, **under either independent or shared movement**."
Head `:124-127`: "\(U_{\rm corner}\) its counterpart **after every allowed lower-or-upper edge choice is evaluated jointly**. Any required \(U_{\rm corner}/U_{\rm point}<2\) falsifies the claim, under either independent or shared movement."

The imported definition is §4's *independent*-corner construction (`:526-532`: "choose either the lower or upper value for every admitted energy, enumerate every joint choice"). The shared-movement numerator is a different object: `:637-650` enumerates one shared sign \(s\) for the whole set of blocks plus one local sign \(e_j\) per block over \(2\times2^n\) choices, replaces \(\delta'_j=\delta_j+s q_j+e_j\ell_j\), and retains \(U_{\mathrm{cmp,shared}}\) — with \(R_{cm}=U_{\mathrm{cmp,shared}}/U_{\mathrm{cmp,point}}\) at `:645-650`. So the sentence now defines its symbol by a construction that the second half of the same sentence does not use. Main's vaguer "after allowed movement" covered both. The lexicon (`round7/built-terms-lexicon.md`, "\(U_{\rm point}\) / \(U_{\rm corner}\)") and ledger row `:1609` repeat the over-specification.

## SHOULD-FIX S4 — the hardened suite binds first-use *location*, not the glosses; deliverable-3's "would have caught these 24" is false and the fixture is synthetic

The ledger test asserts that a ledger term's first occurrence falls in its declared home section. It does not assert that a gloss exists. Mutation probes run against copies of the **cured** draft via `PAPER_FIRST_USE_DRAFT` (all five tests, `tests.test_paper_first_use_ledger`):

| Mutation (revert one cure) | Result |
|---|---|
| M1: delete the package-power gloss at `:316-317` (cure 13) | **OK — not caught** |
| M5: delete the whole retired-calculation gloss at `:399-404` (cure 16) | **OK — not caught** |
| M2: delete the gross/idle-subtracted gloss at `:193-195` (cure 10) | FAILED (1) — caught, via home relocation |
| M3: revert §1 `U_corner`→`U_edge` (cure 21) | FAILED (1) — caught |
| M4: revert one ledger home ("members" → Bracketed pulse-train algorithm) | FAILED (1) — caught |

Matcher mutations in a scratch copy of the module: locator forced to `_occurs_exact` → FAILED (5); `COMPOUND_JOIN` stripped of the hyphen alternation → FAILED (52); possessive group removed → OK, but that is an **equivalent mutant** (the trailing `(?!\w)` already admits an apostrophe), i.e. the possessive branch is dead code, not a test gap.

Real-draft discrimination (independently reproduced): new test on `git show 33290b8b:docs/paper/draft-v2-skeleton.md` → `FAILED (failures=4)` (`members`, `false-difference components / false-difference`, `independent units`, `Commanded pulses`); new test on the cured draft → `OK (5 tests)`. So the hardening catches **4 of the 24** audit rows, and three of those four were "cured" by re-homing the ledger row rather than by moving or building the term. `tests/fixtures/paper_first_use_pre_cure.md` is 24 constructed sentences ("1. The member's edges moved."), not pre-cure draft text — a matcher-coverage fixture, correctly described as such in the seat report's F2 but not in the brief's deliverable 3.

---

## NITS

- **N1 (scope).** The branch diff vs main touches two paths outside the brief's `WRITE_SCOPE: [docs/paper/draft-v2-skeleton.md, docs/paper/round7/built-terms-lexicon.md, tests/]`: `docs/process_traces/2026-09-02-paper-f/00-brief.md` and `…/01-seat-F-landing-report.md`. Both are in the lead's custody commit `4cb31a75`; the seat's own commit `44e22d99` is exactly in scope (`docs/paper/draft-v2-skeleton.md`, `docs/paper/round7/built-terms-lexicon.md`, `tests/fixtures/paper_first_use_pre_cure.md`, `tests/test_paper_first_use_ledger.py`). Flagged for the record only — the brief itself directs a report file to that directory.
- **N2.** Cure 9 glosses reference runs as "repeated at the window's opening, midpoint, and close" (`:184-186`) unconditionally, while `:700` says "opening, midpoint **when present**, and closing" and selects `replicated_endpoint_bound_j` vs `single_member_endpoint_bound_j` on that basis. The unqualified form mirrors pre-existing §3 text (`:327-328`), so this is inherited, not invented — but it is now in a definitional sentence.
- **N3.** Cure 18's "The recorded **energy terms** are …" (`:740-743`) reads exhaustive. It is exact for the frozen AP-2 metric rows (`joulewise/analysis_manifest.py:524-534`, `len(metrics) != 4` → "must contain the four frozen AP-2 metric rows"; only two claim families exist, `whole_window.py:117-118`), but the reducer also emits derived per-token and batch-group energy terms (`reduce.py:2570-2575`, `:3204`). Quotients/aliases, not families — acceptable as written, worth a "recorded claim-bearing" qualifier.
- **N4.** `docs/paper/round7/built-terms-lexicon.md` is a generated artifact (`scripts/paper_terms_lint.py lexicon --draft … --out …`); the seat hand-appended a "Successor-draft first-use additions" table and rewrote the provenance header. No test binds the file's content (`tests/test_paper_terms_lint.py` exercises the script against `round7/retensing-plan.md`), so the next regeneration silently destroys the added section.

---

## Charge items that could NOT be falsified

**(2) Symbol unification — complete, no formula altered.** `git grep` for `U_edge` / `U_{\rm edge}` / `U_\mathrm{edge}` over the whole tree returns hits only inside the seat's own brief and report prose; zero in `docs/paper/**` or `docs/paper/figures/**`. `U_corner` appears at `:124`, `:126`, `:1609` (`\rm`) and `:531-532`, `:538`, `:716-717` (`\mathrm`), plus the lexicon row. No display-math block is touched anywhere in the diff: filtering the draft diff to lines containing `frac|qquad|R_{cm}|U_{` yields only the two §1 inline occurrences, the outcome-sentence A rewrite, and the new ledger row. `R=U_corner/U_point` (`:538`) and `R_{cm}=U_{cmp,shared}/U_{cmp,point}` (`:645-650`) are byte-identical to main. (The definitional mismatch this created is S3, not a formula change.)

**(3) Excluded regions — byte-identical.** Extracting main `:23-80`, `:917-940`, `:998-1004`, `:1222-1230` and searching the head draft: each present verbatim, exactly one occurrence. No diff hunk's old-file range overlaps any of the four (hunks start at old lines 99, 110, 134, 160, 233, 282, 303, 367, 379, 513, 702, 766, 793, 803, 1244, and 1565+).

**(1) Cures corroborated against primary evidence** (22 of 24 rows survive the fact lens; B1 and B2 are the two that do not):
- Cure 10, idle-subtracted energy — `joulewise/reduce.py:2959-2962`: `gross_energy_j - idle_baseline.power_w_mean * window.duration_s`; `power_w_mean`, not p95/median, and the window *is* the measured run (`reduce.py:2914-2916`). Matches "mean idle power multiplied by run duration".
- Cure 13, package power — `joulewise/adapters/powermetrics.py:57` `RAIL_MANIFEST = ["cpu_power", "gpu_power", "ane_power"]`, summed at `:1791-1805` (`combined_power_w=sum(rail_power_w.values())`); boundary string `"Apple SoC CPU + GPU + ANE package power"` at `:1442`. No DRAM term.
- Cure 16, retired predicate direction — `joulewise/detection_floor.py:820-841`: `return uncertainty_max > point_gate`, with the guard factor applied to the **point** side only (`:791-795`, `estimate.guard_factor * point_unguarded`; `small_sample_guard_factor` at `:664-673`) and the corner maximum exact (`_linear_corner_widened_max`, `:735-738`). The paper's "corner maximum exceeded its point-only value after a fixed widening factor" is the right side.
- Cure 16, "equal-rate clock anchor" era — the rate-aware anchor landed 2026-08-18 (`4efea134 Rate-aware clock anchor: exact set-membership estimator + method identity`), after window a10 (2026-07-25). a10's retained anchor bound is 25.6 ms (`runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/summary_metrics.json`, `anchor_bound_s = 0.025619527535021308`), which the current estimator would refuse outright (`B_anchor > 0.005 s` → `effective_clock_anchor_bound_exceeded`, A.3.3). Pilot-era attribution is sound.
- Cure 16, "July 25, 2026 diagnostic window" and "30 phase-energy runs" — registry supplier `A10 = …/runs_window_a10_20260725/{member}/…` (`results-fill-registry.md:555`); `DG-055` "timing-member count | n=30 | sum len(XS#cells[0..2].members)"; the 30 members are the ten `r01…r10` bundles in each of the prefill / decode / short-prefill cells (directory listing confirms 3×10). The date traces to the registry's supplier path rather than a numbered row — acceptable, but it is the one new reader-facing datum without its own row.
- Cure 6, four allowances — A.3.3 "Composing the bound": `B_anchor = roundup(H + span + r_max + 1e-6)` with `H=(A_hi−A_lo)/2` (half the endpoint range), `span` (wall-vs-elapsed/monotonic), `r_max` (largest reported clock resolution), `1e-6 s = NUMERIC_PADDING_S`. Faithful. The "four evidence constraints" also map cleanly onto A.3.3's row families (stamp-bracket pairs, native whole-second rows, `A ≥ g_v(β)+β·k_pre` launch ordering, `A ≤ h_v(β)+β·k_parse` parse ordering).
- Cure 5, appendix pointers — `#### A.3.5 The pulse-fit algorithm` (`:1452`, carries edge coverage / fit / shift-limit checks) and `#### A.3.7 The work budget and the 120 s work clock` (`:1537`, "Two shared limits bound it — a cell budget and a wall-clock budget"). Both pointers resolve.
- Cure 3, reasoning disabled — both conditions are Qwen3 (`:135-137`; `configs/model_panels/qwen3_4bit.json:5-8, 38-40`), `"enable_thinking": "false"` at `:24`/`:57`, pinset `qwen3-real-prompts-v1-thinking-off`, enforced at `configs/campaigns/d117_contrast_v5/generate_configs.py:955, 970`; the Qwen2.5 panel records `"not_applicable"`, so attributing the setting to Qwen3 is correct.
- Cure 18, energy terms — exactly the four frozen AP-2 rows (`analysis_manifest.py:524-534`); no idle-subtracted phase metric exists in production. See N3.
- Cure 19, deterministic-bound kinds — corroborated by the production key names `E_interpolation_joint_edge_bound_j`, `E_drift_bound_j`, `E_clock_anchor_shift_bound_j`, `E_whole_window_drift_allowance_j` (the last three visible in the a10 summary, e.g. `energy_bound_terms_j.E_clock_anchor_shift_bound_j`).
- Cure 17, close-out artifact — `joulewise/dominance_closeout.py:1796-1832` requires exactly eight independent-ratio records (4 absolute + 4 comparative) and four common-mode records, with census totality against the floor artifact (`:1274-1279`). "Checks every required ratio" is accurate, if under-inclusive (it also reauthenticates sources and licenses the outcome sentence).
- Cure 22, the naming bridge — §4 `:679-681` states verbatim "The final resolution bound is called the **cell floor** in the artifacts", and the cell floor is \(g(n)U_{\rm corner}+A\) (`:716-717`), i.e. the value *after* the Section 4 safeguards. The §1 appositive says exactly that.
- Cure 12's re-homing side effect checked: "not resolvable" lost its §3 gloss with the deleted row, and its new first use at `:802` **is** glossed ("means **not resolvable**—the estimate does not clear the cell floor—not zero"), matching the re-homed ledger row `:1726`.

**(5) Scope** — only N1; no source, config, or artifact path outside `docs/paper/**` and `tests/**` is touched.

---

## Executed evidence (verbatim)

```
$ git -C /Users/edr/code/JouleWise-wt-paper-f diff --name-only 33290b8b..4cb31a75
docs/paper/draft-v2-skeleton.md
docs/paper/round7/built-terms-lexicon.md
docs/process_traces/2026-09-02-paper-f/00-brief.md
docs/process_traces/2026-09-02-paper-f/01-seat-F-landing-report.md
tests/fixtures/paper_first_use_pre_cure.md
tests/test_paper_first_use_ledger.py
```

```
Abstract :23-80 present verbatim in head = True; occurrences=1
S6 printed negative result :917-940 present verbatim in head = True; occurrences=1
S7 what the finding changes :998-1004 present verbatim in head = True; occurrences=1
S10 :1222-1230 present verbatim in head = True; occurrences=1
```

```
$ git grep -n 'U_edge\|U_{\\rm edge}\|U_\\mathrm{edge}\|U_{edge}' -- .
docs/process_traces/2026-09-02-paper-f/00-brief.md:13: … (`U_edge` vs `U_corner`, `:115` vs `:486`) …
docs/process_traces/2026-09-02-paper-f/01-seat-F-landing-report.md:13: … "retired U_edge grep: absent" …
docs/process_traces/2026-09-02-paper-f/01-seat-F-landing-report.md:43: | 21 | 115 vs 486 | U_edge vs U_corner | cured | …
(no hits under docs/paper/ or docs/paper/figures/)
```

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger      # cured draft
Ran 5 tests in 1.091s
OK

$ PAPER_FIRST_USE_DRAFT=<git show 33290b8b:docs/paper/draft-v2-skeleton.md> … tests.test_paper_first_use_ledger
Ran 5 tests in 1.053s
FAILED (failures=4)
  'members'  … 'independent units' … 'false-difference components / false-difference' … 'Commanded pulses'

$ mutations against the CURED draft (revert one cure each)
M1 package-power gloss removed          -> OK        (NOT caught)
M5 retired-calculation gloss removed    -> OK        (NOT caught)
M2 gross/idle-subtracted gloss removed  -> FAILED (failures=1)
M3 §1 U_corner -> U_edge                -> FAILED (failures=1)
M4 one ledger home reverted             -> FAILED (failures=1)

$ matcher mutations (scratch copy of the module)
MUT-A locator forced to _occurs_exact   -> FAILED (failures=5)
MUT-B possessive group removed          -> OK   (equivalent mutant: trailing (?!\w) already admits ')
MUT-C COMPOUND_JOIN hyphens removed     -> FAILED (failures=52)
```

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint tests.test_paper_first_use_ledger tests.test_paper_build
Ran 13 tests in 2.300s
OK (skipped=2)
```

```
$ grep -n "workload level" <main draft>        ->  306, 1171, 1173
$ grep -n "workload level" <head draft>        ->  1211, 1213      (the only gloss, main:306, was deleted)
$ grep -n "figures/fig" <head draft>           ->  168 (Figure 1), 206 (Figure 2)   # no Figure 3 embed
$ ls docs/paper/figures/fig3_decision_gates.svg -> exists (unreferenced)
$ grep -n "Figure 3" <head draft>              ->  846 (body claim), 881 (build note "Build Figure 3"), 1734 (ledger)
```
