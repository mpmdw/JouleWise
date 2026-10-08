<!-- Investigator's return, saved by the orchestrator from the workflow journal at the 2026-10-07 pause. The refuter did not run (usage limit). -->

**`REPORT.md` was not written.** The harness refused the file write for a subagent ("return findings as text, not report files"), so the full report is below for you to save as `/Users/edr/night-archive/gate-prune/wave-1007b/q5-attribution-floor/REPORT.md`. `NOTES.md` and the scripts and data under `work/` are in that directory. No repository file was changed, no test was run, and `git status` in the int5 worktree was empty after the recomputation.

---

# Q5, the attribution floor: what it is, how "about 1 J" was derived, and what the block-5 registration should bind

Investigator: Opus 5.5, 2026-10-07. No block-5 claim byte exists yet and none was read. Section 7 item 7 lists which energies of earlier, non-claim windows were read.

Code and the two block-5 documents are cited at the integration head `9b0c680ed` (worktree `/Users/edr/code/JouleWise-wt-int5`). The decision log is `/Users/edr/code/JouleWise/docs/decision_log.md` (canonical root, main at `e0c738e9c`).

## 0. Answer

**Recommendation: (c). Register the formula and bind no number.** The attribution floor of a reported cell is the largest, over the cell's kept members, of a per-member bound that the frozen reducer already computes. The analysis already reads that bound to build the cell's interval. It is computed at analysis step 10 from the window's own members and calibration bracket. D-078's "about 1 J" is recorded as the lineage of the quantity, not bound as a value.

Four facts support this (each is established below):

1. **"About 1 J" is not a constant of the instrument.** It is one member's value of a per-member bound on window a10 of 2026-07-25: macOS build 25F84, fiducial bound 24.879 ms, model Qwen2.5-1.5B. Its arithmetic is 0.031073829 s × 32.697 W = 1.01601 J.
2. **Every input has changed for block 5.** On the released 25G83 data (block 3, the same two Qwen3 models) the same bound is 1.38 to 2.86 J per member under the timing bound the analysis applies, about twice the D-078 figure. It also depends on each window's own bracket, which is unknown before the window runs.
3. **Nothing in block 5 is decided by the number.** It is printed beside four reported cells and cited once as a rationale. No gate, exclusion, floor, dominance ratio, contrast or claim ceiling reads it.
4. **The average of the same bound is already inside each reported cell's interval.** The analysis plan's sentence that the interval "does not include" it is false as written and must change under any answer.

Option (c) needs text before the seal and a few lines in the lane-L9 reported-energy issuer before the release event. It needs no artifact, no number, and no code that runs during collection.

## 1. What the attribution floor is, physically

### 1.1 The forcing problem

The power sampler reports **records**: consecutive intervals of about 121 ms (a10) or 129 ms (block 3), each carrying the average power over that interval. A **phase** (prefill or decode) is a stretch of one request bounded by two machine-clock stamps, its **start edge** and **end edge**. The reducer assigns energy to a phase by overlap: each record contributes its power times the length of its overlap with the phase (`joulewise/reduce.py` `_integrate`; registration section 0.4, lines 310-315).

Placing records against phase edges is known only within bounds. If an edge really lies a time δ from where it was placed, δ times the power of the record straddling that edge is assigned to the wrong side. That misassigned energy is what the attribution floor bounds.

### 1.2 The three timing bounds

| Symbol | Name | What it bounds | Source | Size |
|---|---|---|---|---|
| b | fiducial bound | how far the sampler's reported power edges sit from commanded edges | pulse calibration, largest delay over 59 pulses (registration section 0.11, lines 458-462) | 24.879 ms on a10; 21.9 to 36.5 ms over the 24 captures of the 25G83 acceptance |
| s | wall-minus-monotonic span | change of (wall clock minus monotonic clock) over the member's sampler stream | the member's clock stamps | 0.02 to 1.31 ms on a10; 0.36 to 0.70 ms in block 3 |
| m | member clock bound (the "effective bound" of registration section 0.14) | placement of the whole record sequence on the wall clock | `joulewise/uncertainty_evidence.py` | 0.60 to 6.07 ms on a10; 0.73 to 4.02 ms in block 3; above 5 ms the member is removed in block 5 |

The reducer treats them differently:

- The **edge bound** g = b + s applies to each phase edge independently.
- The **member clock bound** m applies as one common shift of the whole trace.
- The recorded total is `anchor_bound_s` = b + s + m (`reduce.py:1712-1733` `_compose_causal_anchor_bound_s`; `reduce.py:2264`).

### 1.3 The bound itself (the exact rule in the code)

For one member and one phase with recorded edges (t_on, t_off), let E(x, y) be the energy the overlap rule assigns to [x, y]. The member's bound is

    a = max | E(t_on + ε_on + d, t_off + ε_off + d) − E(t_on, t_off) |
        over ε_on in {−g, +g}, ε_off in {−g, +g}, and every d in [−m, +m].

E is piecewise linear in d, so the maximum is found exactly at d = −m, +m and wherever a displaced edge meets a record boundary.

- **Code:** `reduce.py:2148-2273` `_corner_composed_anchor_shift_envelope`, calling `reduce.py:2064-2145` `_anchor_shift_envelope`.
- **Stored field:** `energy_anchor_shift_envelopes["/phase_energy_j/<phase>"].max_abs_delta_j`, method `common_trace_shift_plus_independent_edge_corners_v3` (`reduce.py:114`).
- **Analysis name:** bound kind `E_clock_anchor_shift_bound_j` (`joulewise/analysis_engine/inputs.py:3906-4041` `deterministic_bounds`, phase branch 4002-4020; reader `anchor_shift_envelope` at 3565).

**First-order size.** While displaced edges stay inside the two records straddling the recorded edges, with P_on and P_off the average powers of those records:

    a = g × (P_on + P_off) + m × |P_off − P_on|.

The bound is a timing bound times the power at the phase's edges. It does not depend on phase length.

### 1.4 Diagram and worked example (a10, member `p2015-df-ph-prefill-abs-r01`, prefill phase)

Times are seconds after the recorded prefill start. Each bracketed span is one record with its average power.

```
records:   [ 1.096 W  ][ 30.6 W ][ 52.0 W ] ... [ 52.3 W ][ 32.029 W ][ 28.2 W ][ 22.3 W ]
record     -0.076   +0.045    +0.158  +0.272     +0.951  +1.063     +1.176   +1.289  +1.402
boundaries
                 ^ t_on = 0                                    ^ t_off = +1.114
                 start edge (in the 1.096 W record)            end edge (in the 32.029 W record)
            <-g->|<-g->                                   <-g->|<-g->       g = 25.000 ms: each edge alone
            <---------- both edges moved together by d, |d| <= m ---------->  m = 6.074 ms: common shift
```

Named elements: a *record* is one sampler interval; *t_on* and *t_off* are the recorded edges; *g* is the independent displacement of each edge; *m* is the common shift.

Inputs from the bundle: b = 0.024879191521227362 s, s = 0.000120401 s, m = 0.006074236 s, so g = 0.024999593 s and b + s + m = 0.031073829 s. The start record averages 1.0959 W; the end record averages 32.0292 W.

Worst case: start 25.000 ms early, end 25.000 ms late, both edges a further 6.074 ms late:

    0.024999593 × (1.0959 + 32.0292) + 0.006074236 × (32.0292 − 1.0959)
      = 0.828115 + 0.187896 = 1.016011 J.

The stored value is 1.0160114367034794 J. That member's recorded prefill energy is 50.847 J.

### 1.5 Why repeating the measurement does not shrink it

The fiducial bound b is one number for a whole window, because every member is reduced under the same bracket. If the sampler's edges sit 20 ms late, they sit 20 ms late in every member, and every member's phase energy moves the same way. Member-to-member scatter (0.29 to 0.49 J on a10) averages down; this does not. That is D-078's "attribution-limited, not noise-limited".

### 1.6 What it is not (D-078 addendum of 2026-09-04)

The addendum (`decision_log.md:11271-11286`) says the bound describes how far the overlap allocation moves over the registered timing box, with power taken as constant within a record. It "does not bound physical energy under arbitrary within-record allocations". The addendum also withdrew clause 11's claims that the bound is the largest false effect the instrument can produce and that its dominance is permanent. Any sentence printed beside a cell must carry that condition.

## 2. How D-078 clause 11 derived "about 1 J"

**Text.** `decision_log.md:4749-4822`, commit `09474a131` (2026-07-25 18:05 PDT). Lines 4763-4770: "each member carries a clock-anchor-shift envelope of ~0.7-1.0 J: a +/-31 ms window shift across a phase boundary where power swings ~33 W mis-attributes ~1 J between prefill and decode. The composed bound is additive and measured — fiducial 24.9 ms (80-87%) ... plus bundle-local 3.3-6.1 ms plus edge span."

**Artifact.** The clause names and hashes none. The figures trace to window a10's member summaries in `/Users/edr/code/JouleWise/runs_window_a10_20260725/` (untracked, with an iCloud copy): 30 phase members of Qwen2.5-1.5B, 2015-token prompt, 64 output tokens.

- The paper's fill registry records the same trace: `docs/paper/results-fill-registry.md:625` (DG-001) and 677-678 (DG-053, DG-054). All three rows have been RETIRED_FALLBACK and NON_CLAIM_BEARING since 2026-09-05.
- SHA-256 of the headline member's `summary_metrics.json`: `8f9c613418ed4f5423eba85ada6502a67bc02f20b1e44b517bdfc612cb9dfdf2`.

**Conditions.** Build 25F84; reducer 0.5.2; pre-capture fiducial bound 0.024879 s (also in `/Users/edr/JouleWise-window-custody/window_a10_20260725/CLOSE_OUT.md`). The timing bound is the pre-capture bound plus the member's own terms. D-079's bracket allowance did not exist yet (D-079 is dated 2026-07-27).

**Formula.** Section 1.3. "31 ms × 33 W" summarises it; it is not the computation.

**Arithmetic, reproduced from the retained bundles.**

| Clause-11 figure | Reproduced | Match |
|---|---|---|
| "+/-31 ms" | largest `anchor_bound_s` of the 30 members: 0.031073829 s at prefill-abs-r01 = 24.879 + 0.120 + 6.074 ms | yes |
| "fiducial 24.9 ms" | 0.024879191521227362 s, identical in all 30 | yes |
| "(80-87%)" | 80.1% and 87.0% at the cells' largest bounds; over all 30 members 80.1% to 97.1% | partly (the clause's 2026-08-24 note says so) |
| "bundle-local 3.3-6.1 ms" | per-cell maxima of m: 3.308, 5.928, 6.074 ms; over all members 0.603 to 6.074 ms | as per-cell maxima only |
| "~33 W" | 1.0160114 J / 0.031073829 s = 32.697 W for r01; its end-edge record is 32.03 W | yes |
| "~1 J" | r01 prefill phase: 1.0160114 J; in round figures 0.031 × 33 = 1.023 J | yes |
| "~0.7-1.0 J" | 30 members, own cell's phase: 0.571 to 1.468 J, mean 0.969 J | **no**, the retained range is wider |

By cell, the a10 bounds are: prefill 0.976 / 1.158 / 1.468 J; decode 0.748 / 0.989 / 1.133 J; short prefill 0.571 / 0.761 / 0.919 J (minimum / mean / maximum).

"About 1 J" is therefore the bound of the a10 member with the largest timing bound. It is also close to the 30-member mean.

## 3. Where block 5 uses an attribution floor

### 3.1 Every mention

Lines are int5 `9b0c680ed` / design branch `design/2026-10-05-v5-claim-block-draft` at `1d97f0a60`.

| Document, section | Lines | What the text does |
|---|---|---|
| Registration 0.10 | 451-454 / 494-497 | defines it as "D-078's estimate, about 1 J"; printed beside each reported cell, never added; carries `FILL[ATTRIBUTION-FLOOR-BINDING]` |
| Registration 0.14 | 722-724 / 768-770 | rationale for the 5 ms member clock bound: 5 ms "moves at most 0.2 J per phase edge at 40 W, below the roughly 1 J attribution floor" |
| Registration 1, table | 879 / 925 | each reported cell "with ... the attribution floor beside it" |
| Registration 13 | 3122, 3127 / 3274, 3280 | binding register row, due at seal; listed as open |
| Registration 14, Q5 | 3302-3303 / 3492-3493 | the open question |
| Analysis plan 4, step 7 | 255-257 / 255-257 | `binding.attribution_floor_j`, with the sentence "phase-edge timing alone could move this cell's energy by up to about that many joules, which the interval does not include" |
| Analysis plan 8.1 | 563 / 577 | disclosure: the step-7 sentence |
| Analysis plan 9, table | 623 / 637 | printed quantity, field `binding.attribution_floor_j`, site CP-X05-*, status RETIRED_FALLBACK until the placement ruling (section 14 Q4) |
| Analysis plan 10, table | 646 / 660 | "attribution floor printed beside, not a gate" |
| Analysis plan 13 | 697, 700 / 711, 714 | FILL list |

### 3.2 What depends on it

- **Printed numbers:** one beside each of the four paper cells (decode and prefill-p2048 per model). The two p42 cells are registered as expected to refuse.
- **Decisions:** none.
  - The dominance ratio is corner-widened floor over point floor (analysis plan line 344).
  - The contrast gate compares the estimate with `floor_gate_j` (line 418).
  - The ceiling is `claim_ready_for_l2_l3`.
  - The "attribution-limited" subtitle rests on the dominance ratios (D-165).
- **One procedural dependence:** the projection kernel requires the field, so the blind dry run cannot issue a reported cell at step 10 until a value can be supplied (also `wave-1007b/l9/map/02-reported-energy-issuer.md`, item A9).
- **One rationale:** the registration section 0.14 sentence.

### 3.3 The same quantity is already inside the interval

Analysis plan section 4 step 4 (lines 233-246) adds B to both ends of each reported cell's interval. The first of B's three kinds is the stratified average of `E_clock_anchor_shift_bound_j` over the kept members. That is the per-member bound of section 1.3, and D-078's "about 1 J" is that bound on a10.

- **Step 7 is wrong as written.** "Which the interval does not include" is false for the average of the bound. Only the gap between the largest member's bound and the average lies outside the interval.
- **Step 4 under-describes the bound.** It says "the largest change ... when the whole power trace shifts by any common amount within ± its effective clock bound", which is only the common shift m. The code also moves the two edges independently by g = b + s, and that is the larger part: 0.828 J of the 1.016 J in the worked example. The fidelity sweep flagged neighbouring undefined terms (`reg-fidelity/REG_FIDELITY.md` U54, U55) but not this sentence.
- **The floors already use the per-window value.** The same per-member bound is the half-width w_i of the absolute detection floor (`joulewise/floor_extraction.py:2084-2121`) and the anchor term of each contrast's deterministic total. Only the number printed beside the cell is a constant.

D-179 ruling 4 (`decision_log.md:11746-11753`) is the origin of the split. The interval takes "the average of each registered deterministic-bound kind", and "the D-078 approximately 1-J attribution limit" is published "as a labelled floor beside the cell, never composed". The cold judge's ruling behind it (`docs/process_traces/2026-09-08-handoff-redo/99be-coldgate-packet-paper-s2-semantics/10-coldgate-fable-ruling.md`) lists "clock-anchor movement" among the composed kinds. D-179 itself therefore has the average inside and a per-member limit beside; only the limit's value was taken as a constant.

### 3.4 What the code does today

- **Registration string.** `joulewise/paper_reported_energy.py:155`: every cell registration carries `"attribution_floor": "labelled_beside_never_composed"`. It is inside the registration digests the two floor packs bind (ALPHA `5560857668f0…`, BETA `04657a74de83…`; analysis plan lines 209-214), so it is sealed pack content. No candidate changes it.
- **Binding check.** `paper_reported_energy.py:385-391` (`_project_cell`): the binding has exactly seven keys, one being `attribution_floor_j`, a finite non-negative number. Nothing else is checked.
- **Output.** `paper_reported_energy.py:441` copies the binding and sets `"attribution_floor_composed": False`. The value enters no arithmetic; `tests/test_paper_reported_energy.py:458-463` proves it by changing 1.0 to 1000 and requiring identical endpoints.
- **No production caller.** `paper_reported_energy.py:456-457`: only the fixture replay calls it ("No production dispatch exists"). The fixture supplies 1.0 (`tests/test_paper_reported_energy.py:58`).
- **Not printed.** `joulewise/paper_rendering.py:101-130` (`render_reported_energy`) does not print the attribution floor. No code prints it today.
- **Contract text.** `docs/contracts/paper_reported_energy.md:124-125`: "The approximately 1-J D-078 attribution floor is labelled beside the cell and never composed into it."
- **Related names that are different objects:**
  - `ATTRIBUTION_LIMIT_CLASS` and `ATTRIBUTION_FLOOR_SOURCE = "E_clock_anchor_shift_bound_j"` (`joulewise/detection_floor.py:124-127`) label a detection floor dominated by this bound.
  - `attribution_single_count_discipline` (`detection_floor.py:363`) records that the floor and the claim-side bound are both kept.
  - `joulewise/analysis_engine/claim_side_bound.py:21` copies a contrast's anchor term.
  - None holds a 1 J constant.

## 4. Did the inputs change on 25G83? Recomputation

### 4.1 The inputs, then and now

| Input | D-078 clause 11 (a10) | Block 5 (25G83) |
|---|---|---|
| OS build | 25F84 | 25G83 |
| Fiducial bound of one capture | 24.879 ms | 24 captures: 21.932 to 36.463 ms, mean 28.444, median 27.897, SD 3.803 ms |
| Fiducial bound the analysis applies | the pre capture's, alone | the operative bound b_op = max(pre, post) + max(\|post − pre\|, 0.014531 s) |
| Member clock bound m | 0.60 to 6.07 ms | at most 5 ms by rule (`uncertainty_evidence.py:46`); block 3: 0.73 to 4.02 ms, median 1.65 ms |
| Model and workload | Qwen2.5-1.5B, 2015-token prompt, 64 output tokens | Qwen3-1.7B and Qwen3-8B; decode workload (42-token prompt, 512 output tokens) and prefill workload (2048 tokens) |
| Power of the record at the prefill-to-decode edge | 24.6 to 36.3 W (cell means) | block 3: 23.3 to 41.2 W, mean 32.2 W |

The 25G83 captures are from `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, SHA-256 `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660`.

The operative bound is the largest change. Its rule is at `joulewise/calibration_bracketing.py:2664-2665, 2749-2765`. The analysis applies it by re-deriving each member's summary in memory (`joulewise/whole_window.py:479, 707-760, 861`; `reduce.py:2715-2747`). The claim loader substitutes that summary at `analysis_engine/inputs.py:3434-3464`. Stored summaries keep the pre-capture bound.

For the one block-3 window with a passed bracket (`derived/bracket.json`, SHA-256 `803fc5a820fb5e41c8fa7af1f4ae2238259feb47f80a02f2e6a43e804dc37cbc`):

- pre 31.138 ms, post 27.754 ms, drift 3.384 ms, allowance 14.531 ms, operative bound 45.669 ms;
- member timing bounds b_op + s + m are then 46.77 to 50.10 ms, against a10's 25.62 to 31.07 ms.

The operative bound a block-5 window can have follows from the acceptance's rules (a pre capture above 36.463 ms stops the chain; \|post − pre\| may not exceed 15.502 ms):

- smallest capture seen, no drift: 21.932 + 14.531 = 36.46 ms;
- two captures near the mean: about 45 ms;
- at the rules' limit: 36.463 + 15.502 + 15.502 = 67.47 ms, or 51.97 ms if a post capture above the corpus maximum is refused as a stale acceptance (not verified, section 7 item 3).

### 4.2 Recomputed bounds on released 25G83 data

Inputs: block 3, the prefill-length probe of 2026-10-03/04, which is not a claim window (registration line 3403). Two harvest archives under `/Users/edr/night-archive/`, 36 succeeded members:

- `harvest-d117-g2a-prefill-probe-20261003T1748Z-r2`: 12 members; `SHA256SUMS` digest `514b3269c2d3a685079e5bf3a4ef04efc1f95b244f5aab09669af4b853bdebfe`; bracket failed, so it has no operative bound.
- `harvest-d117-g2a-prefill-probe-20261004T1305Z-r2`: 24 members; digest `aeef9c9ae93a8513f1f6e3c7fb11028baecc5042eb0d2b9492b03f7216417977`; bracket passed.

Per-member bound in joules, minimum / mean / maximum:

| Members | n | Timing bound | Prefill phase | Decode phase |
|---|---|---|---|---|
| **a10, 25F84** (basis of D-078), each member's own cell | 30 | 25.62 to 31.07 ms | 0.976 / 1.158 / 1.468 | 0.748 / 0.989 / 1.133 |
| a10, all three cells together | 30 | same | 0.571 / 0.969 / 1.468 | |
| **Block 3, as stored** (pre-capture bound only, D-078's composition), all lengths | 36 | 31.14 to 35.57 ms | 0.943 / 1.218 / 1.569 | 1.081 / 1.518 / 1.945 |
| Block 3 as stored, Qwen3-1.7B at 2048 tokens | 7 | 31.67 to 35.17 ms | 1.053 / 1.328 / 1.569 | 1.442 / 1.588 / 1.710 |
| Block 3 as stored, Qwen3-8B at 2048 tokens | 1 | 35.42 ms | 1.565 | 1.945 |
| **Block 3, under the operative bound 45.669 ms** (what the analysis applies), all lengths | 24 | 46.77 to 50.10 ms | 1.379 / 1.909 / 2.293 | 1.837 / 2.322 / 2.860 |
| Block 3 operative, Qwen3-1.7B at 2048 tokens | 5 | 46.80 to 49.70 ms | 1.882 / 2.056 / 2.273 | 2.127 / 2.325 / 2.473 |
| Block 3 operative, Qwen3-8B at 2048 tokens | 1 | 49.95 ms | 2.293 | 2.860 |

Worked example on 25G83 (`g2a-small-p2048-r04`, decode phase, operative bound): g = 45.669 + 0.369 = 46.038 ms, m = 1.659 ms, start record 41.17 W, end record 9.54 W. Then 0.046038 × (41.17 + 9.54) + 0.001659 × (41.17 − 9.54) = 2.3346 + 0.0525 = 2.387 J. The code gives 2.3868 J; the stored value under the pre-capture bound is 1.650 J.

**How far it moves.** From about 1.0 J (a10 headline 1.016 J, mean 0.969 J) to about 2.1 to 2.9 J for the nearest block-3 analogues of the paper cells, a factor of about 2. Two steps make it up:

- fiducial bound and model power, in D-078's own composition: 1.13 to 1.15 on like-for-like means (prefill 1.158 → 1.328 J; decode after a long prefill 1.407 → 1.588 J);
- the bracket allowance the analysis adds since D-079: a further 1.43 to 1.59 at 2048 tokens.

At the rules' limit of the timing bound (67.47 + 5 ms) and block 3's largest edge power, the bound would exceed 4 J.

**Limits.**

- **Decode workload.** Block 3's decode phases follow a 512 to 4096-token prefill. Block 5's decode cells follow a 42-token prefill, so the record at the decode start holds mostly idle power there. No released quiet-window member of that workload exists on 25G83.
- **Desk runs of that workload are indications only.** Five members (cooldown smoke runs 3 and 4, Qwen3-1.7B, agent sessions alive) show 0.716 to 1.350 J as stored at 29.8 to 32.4 ms. The real-model rehearsal of 2026-10-06 on a loaded machine shows 1.8 to 4.1 J as stored, which shows the bound follows whatever power the edge records hold.
- **Qwen3-8B** has one block-3 member per prompt length.

### 4.3 How the numbers were checked

- **Independent script.** `work/independent_envelope.py` implements section 1.3 from `power_trace.csv`, `events.jsonl` and `metadata.json` without importing the repository. It reproduces all 146 stored phase bounds (a10 and block 3) to a relative difference of at most 6.1e-6.
- **Repository reducer.** `work/rederive_block3.py` and `work/rederive_block3_slice.py` call `reduce_bundle` in memory on the 24 members of the passed block-3 window. With no override it returns the stored bounds exactly.
- **Agreement.** Under the operative bound the two agree on all 48 phase values: to 2.6e-6 on the 30 kept at full precision, to 3.1e-5 on the 18 kept at four decimals.
- **Outputs.** `work/independent_stored_bound.json`, `work/independent_operative_bound.json`, `work/block3_w1305_operative*.log` and `*.json`.

## 5. The candidate answers

No candidate changes a claim outcome, a floor, a dominance ratio or a contrast. They differ in what is printed beside the four reported cells, whether that print is true for its window, and what must exist when.

| | (a) bind D-078 as is | (b) re-derive on 25G83, bind constants | (c) register the formula |
|---|---|---|---|
| Bound | "about 1 J" (1.0160114 J); the a10 member summary | per model and phase from block 3, e.g. 2.27 J (1.7B prefill, largest of 5), 2.29 J (8B prefill, one member), 2.47 and 2.86 J for decode | no number; fact F3 |
| True for the window it sits beside | no | approximately | yes, by construction |
| Before the seal | value, digest, and a ruling that it applies | a committed derivation with input digests and an independent check | text only (section 6) |
| Before the release | issuer passes the constant | issuer passes the constants | issuer computes the value, with a check and one synthetic test |
| Code during collection | none | none | none |

**(a) has no reason that holds.**

- Build, calibration epoch, model, workload and the composition of the timing bound all differ.
- The artifact is an untracked directory.
- Clause 11's "largest false effect" reading was withdrawn on 2026-09-04.
- D-078 clause 10 names OS build and calibration identity changes as re-derivation triggers for the sibling drift-bound artifact (`decision_log.md:4696-4699`).
- Each cell would print "1 J" beside an interval whose own first B term is expected near 2 J.

**(b) is closer but still not the window's own.**

- A block-5 window's operative bound can lie from about 36 to 52 ms or more, so a constant taken at 45.67 ms is off by the ratio of the bounds before any power difference.
- The decode cells have no like-for-like released input.
- It puts a number into a sealed document, which adds derivation and checking to the seal path today. The scripts under `work/` are that derivation in draft.

**(c) is computed at analysis step 10, not at harvest.**

- The L9 issuer computes it from the same per-member rows it already builds for B, and passes it as `binding.attribution_floor_j`.
- The bound under the operative bound needs the authenticated bracket session, which is analysis code. The harvest program is pinned by the seal and is not touched.
- The issuer lane is unbuilt and already due before the release (`FILL[REPORTED-ENERGY-ISSUER]`). It is pinned by the seal-record addendum and exercised by the blind dry run, as analysis plan section 11 already requires.
- No pinned estimator file changes. `_project_cell` and its binding keys stay as they are, so the fixture replay digest is untouched.

## 6. Recommendation, and the facts the two documents must state

**Bind (c).** These are facts for the writer to turn into text.

### Registration section 0.10 (replaces lines 451-454)

- **F1.** The attribution floor belongs to one reported cell of one analysed attempt. It is a bound on single members, in joules.
- **F2.** Per-member bound a_i: section 1.3, with:
  - its three inputs: the window's operative fiducial bound, the member's wall-minus-monotonic span, the member's clock bound of section 0.14;
  - the rule: the two edges move independently by g = b_op + s_i while the trace shifts in common within ±m_i;
  - the first-order form: g × (P_on + P_off) + m × \|P_off − P_on\|;
  - code names: `reduce.py` `_corner_composed_anchor_shift_envelope`; stored field `energy_anchor_shift_envelopes["/phase_energy_j/<phase>"].max_abs_delta_j`; bound kind `E_clock_anchor_shift_bound_j`.
- **F3. Formula.** Attribution floor of the cell = the maximum of a_i over the cell's kept members. Each a_i is taken from the member's summary as re-derived under the window's operative fiducial bound b_op = max(pre, post) + max(\|post − pre\|, 0.014531 s). Recorded with it: the member that attains it, the minimum over kept members, and the stratified average (which is `interval.kind_averages_j` for this kind).
- **F4.** It is computed at analysis step 10 from the window's own bytes. No value is registered. It is an energy of a claim window, so it is restricted until the release event.
- **F5.** The stratified average of a_i is the first kind of B and is inside the interval. The maximum is printed beside the cell and is not added (`attribution_floor_composed` stays false).
- **F6.** Repeats do not reduce it: one bracket, hence one b_op, for every member of the window.
- **F7.** Condition from the 2026-09-04 addendum: it bounds the movement of the overlap allocation with power constant within a record, not physical phase energy.
- **F8.** Lineage: D-078 clause 11's "about 1 J" is this bound on window a10 (2026-07-25, build 25F84, pre-capture fiducial bound 24.879 ms, Qwen2.5-1.5B). It was 0.571 to 1.468 J over 30 members, mean 0.969 J. The quoted figure is the member with the largest timing bound: 0.031073829 s × 32.697 W = 1.016 J. It is not bound here.
- **F9.** Why not: on block 3 (25G83, the two Qwen3 models, not a claim window) the same bound was 1.38 to 2.86 J per member under that window's operative bound of 45.669 ms, and it changes with each window's bracket.

### Registration section 0.14 (lines 722-724)

- **F10.** Replace the comparison with "the roughly 1 J attribution floor". True statements available:
  - 5 ms × 40 W = 0.2 J at one edge;
  - block 3's edge records held up to 41.2 W;
  - the edge-bound part of the same member's bound is about nine times larger (46 ms against 5 ms);
  - block-3 members' whole bound was 1.38 to 2.86 J.

### Registration sections 10, 13 and 14

- **F11.** Section 10, one more registered deviation. D-179 ruling 4 and `docs/contracts/paper_reported_energy.md:124-125` name "the D-078 approximately 1-J attribution limit" as the number beside the cell; block 5 prints the cell's own measured value by F3. The string `labelled_beside_never_composed` is unchanged.
- **F12.** Section 13: `ATTRIBUTION-FLOOR-BINDING` is filled by the formula at the seal; the value is issued per cell at analysis. Section 14 Q5 is closed with the ruling "D-078's derivation applies as a method and not as a number on 25G83".

### Analysis plan

- **F13.** Section 4 step 4: the definition of `E_clock_anchor_shift_bound_j` is F2, including the independent edge displacement. The fiducial bound used is the window's operative bound, from the same summaries the floor extraction and claim gate read.
- **F14.** Section 4 step 7: `binding.attribution_floor_j` = F3. The sentence must not say the interval excludes it. Facts for the sentence:
  - with X the maximum, "phase-edge timing alone could move the energy assigned to this phase of a single request by up to X J";
  - the average of that bound over the kept members is already in the interval as part of B;
  - X is not added.
- **F15.** Section 8.1 follows F14. The section 9 row's field is unchanged.
- **F16.** Section 11, issuer row:
  - the issuer computes F3 from its own per-member rows;
  - the production issuer refuses a binding whose `attribution_floor_j` differs from that maximum (the existing code `paper_reported_energy_binding_mismatch` fits; no new refusal code);
  - a synthetic test covers a cell with one removed member;
  - the check belongs in the production issuer, not in `_project_cell`, because the fixture and the test at `tests/test_paper_reported_energy.py:458-463` set arbitrary values on purpose.
- **F17.** Section 13: `ATTRIBUTION-FLOOR-BINDING` leaves the open list.

### One choice inside (c)

I recommend the maximum over the stratified average for two reasons. The average is already printed inside the interval's record, so printing it again as "never composed" would contradict itself. And D-078's own figure was a single member's bound. If the seal gate prefers the average, F3 becomes "the stratified average" and F5 becomes "the same number that is the first kind of B".

## 7. Not verified, and other open points

1. **Which summaries the L9 issuer reads.** The floor extraction and claim loader read summaries re-derived under the operative bound. The reported-energy issuer does not exist yet. If it read stored summaries, B and the floor of every reported cell would be computed under the pre-capture bound, smaller by a factor near 1.5 than what the floors use. That changes an interval, so it is a number-bearing design point for L9. F13 states the intended rule; `wave-1007b/l9/` had no issuer design file when read.
2. **The statistic** (maximum or stratified average) is a choice for the orchestrator or the seal gate.
3. **Upper limit of the operative bound.** I did not establish whether a post capture above the corpus maximum (36.463 ms) is refused through the acceptance's range-expansion trigger. The limit is 51.97 ms if so, 67.47 ms if not.
4. **Block-5 decode workload on a quiet 25G83 machine.** No released member exists. This is irrelevant under (c); under (b) it leaves two of four cells without a like-for-like input.
5. **Clause-11 figures that do not reproduce.** The "~0.7-1.0 J" range (retained: 0.571 to 1.468 J). The a10 bundles are untracked; I did not compare them with the iCloud copy.
6. **The first block-3 window's bracket failure** was not examined. It only means that window has no operative bound.
7. **Blinding.** I read energies and bounds of a10, of block 3, and the stored bounds of the desk rehearsal and smoke members under `gate-prune/rehearsal-real` and `gate-prune/cooldown-smoke`. None is a claim window. The block-3 bounds here (1.4 to 2.9 J) are close analogues of what the claim cells will show. A writer who must avoid any energy-like preview can work from section 6 alone; only F9 and F10 quote block-3 values, and both can be dropped without changing the rule.
8. **Records to update after the seal (light tier).** `docs/contracts/paper_reported_energy.md:124-125`, and a decision-log note against D-179 ruling 4 and D-078 clause 11. Other documents still say "~1 J attribution floor", for example `docs/contracts/night_quiet_admission.md:49` and `gate-prune/PLAN.md:870`.
9. **Printing.** `render_reported_energy` does not print the floor; the L9 disclosure producer has to. Placement waits on registration section 14 Q4.

## 8. Files (all under `/Users/edr/night-archive/gate-prune/wave-1007b/q5-attribution-floor/`)

| Path | Content |
|---|---|
| `NOTES.md` | running notes, final state recorded |
| `work/independent_envelope.py` | independent implementation of section 1.3 |
| `work/independent_stored_bound.json` | 146 rows: a10 (37 bundles) and block 3 (36 members), recomputed and stored values |
| `work/independent_operative_bound.json` | 48 rows: block 3 window 20261004T1305Z under the operative bound 0.045668641912586815 s |
| `work/rederive_block3.py`, `work/rederive_block3_slice.py` | calls to the repository reducer, in memory |
| `work/block3_w1305_operative.log`, `work/block3_w1305_operative_s09_16.{log,json}`, `work/block3_w1305_operative_s16_24.{log,json}` | their output for the 24 members |

Re-run of the independent check (about one minute, no repository import): `/opt/homebrew/bin/python3.13 -I -B work/independent_envelope.py <out.json> <label>=<runs root>[@<fiducial bound in seconds>]`.
