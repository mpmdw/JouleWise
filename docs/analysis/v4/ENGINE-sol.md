# V4 primary engine (Sol), R23c + R23d

2026-11-08. **PROVISIONAL: synthetic qualification, no live study validation.**
Authority: the lead's engine-r23 brief (A37 and R23-E1/R23-1–4), on
`8eb7982f0`, retaining R21 (`origin/main:RUN_STATE.md`, item 230), adopting A0–A36 of
`origin/align/2026-11-08-v4-interpretation-rulings:docs/analysis/v4/INTERPRETATION-RULINGS-DRAFT.md`.
The amendment is binding: **U5 INCONCLUSIVE never triggers R20; U4 alone can
trigger supplemental sentinels.** This replaces the earlier interpretation
questions here. Scorer validity, exchangeability and the physical D positive
control remain disclosed scientific gates. Exit zero means a fill was produced,
not scientific certification.

No Opus recompute code was read. Only the rulings were used for reconciliation.
No network, model weights, live measurements or Block 5 outcomes were used.
Coordination state is untouched, per the assignment.

R23b applies the 2026-11-08 ADMIT-WITH-FIXES brief on `d3a133cc7`.
The clarification restricts DC **residuals** to GPU rows; DC-in values print
for every captured benign member. The export adapter now accepts window-bound,
series-unique anchor IDs. This remains synthetic software qualification only.

R23c applies the lead's final export-contract rulings on `b11d1fafe`.
W1 must be a window in the common export: selection-only W1 is refused,
including snapshots with full anchor evidence. Native/release anchor IDs must
be series-unique. The σ_w diagnostic explicitly discloses W1 block inclusion,
exclusion or unavailability.

## Ruling → code map

Paths are relative to `joulewise/align/`; engine, acceptance, raw, dc, io and
exclusions mean modules in `v4_analysis/`.

| Row | Implementation / retained contract |
|---|---|
| A0 | `raw.member/window` map an explicit digest-bound manifest over the lead-owned raw export. `io.load` retains the desk-export adapter. Export creation/authentication is lead-owned. |
| A1 | `engine._fit_task`: scored J is `math.fsum` of fitted turn rows; refusal on disagreement with desk owned J at 1e-12 relative. Gross J is printed only. |
| A2 | `apple.reduce_sol.turn_energy_table`: production `attribute_episode`, native prorated supports, tools, overlap ownership and holds. Invalid thermal custody remains excluded by the thermal desk. |
| A3 | `engine._rows/_fit_task`: turn/episode h=0 and standard_uncertainty. Source bounds print under diagnostic_bounds. Missing gross totals/bounds do not select members or affect scores. Frozen fitter boundary flags survive. |
| A4 | Per-window × pair × convention; benign LOTO keyed by run_id; full benign fit for sabotage; T uses its own fits. Only thresholds carry C→T. |
| A5 | Pair × convention, one GPU rail, sample maximum, strict >. |
| A6 | Logged decode includes reasoning; withheld subtracts the logged count exactly; C/P/J equality checked. Withheld prints alongside. |
| A7 | Exact earliest-first sub-turn strip. Unreachable nominal dose has null H/score and dose_unreachable. First-k actual doses, separate council grid, eight-dose H_STAR_GRID. |
| A8 | `apple.v4_estimands.benign_carrier_curve`: per-dose n; crossings on all-carrier prefix; later nonmonotonicity flagged without voiding crossings. Other-carrier untouched thresholds, ≥40 carriers. Engine pins Random(0), choices over sorted window IDs with multiplicity, 1000 replicates, type-1 5/95 order statistics over defined replicates; undefined counts retained. |
| A9 | `exclusions.FLAG_TO_CLASS/CLASSES`; union of re-derived and recorded classes, both component sets, raw reasons and mismatch printed. Compare class sets. |
| A10 | `raw.member` limits registered OS readings to registered_span_ns; production desk derives registered-span X1; episode observations remain visible. |
| A11 | `apple.thermal_desk.member_record/acceptance`: wall spans through tool ends include holds; collector-grid episode/G0 coverage; PM uncovered-gap or wide-support union. G1+H entries/timeouts over captured members with sidecars, including X1–X4. |
| A12 | Journal-matched one-sided release checks; released G0 values only; no G1/H releases → U2(b) not_applicable. |
| A13 | `acceptance.window_checks/u3_pair`: W1 5/17 plus 6/16, 9/13, 7/15, 10/12; C/T 5/22. Tags must agree if present. Equal identity digest AND per-turn C/P/D; divergence is X5. Ineligible replay inconclusive. Decode-owned active-weighted clock and R1 D screen retained. |
| A14 | `acceptance.u4`: cumulative results including T, first evaluation at W≥3; unavailable/ineligible/<3-turn/divergent sentinels skip that window. |
| A15 | `acceptance.u5`: three actual R1 G0 temperatures, energy OLS with intercept, df=1, 90% t interval, replay sample SD floored at 2.97 J. Designed targets printed; triggers_R20=false. |
| A16 | Logged pair-level U6 over pool-entered C benign LOTO residuals only; chronological split with extra in late half, CR0 sandwich, 1.645 interval, point-outside FAIL. Scale √(Σ full-fit RSS / Σ full-fit df). Position means need ≥6 trajectories. |
| A17 | `apple.v4_cadence.calibration_stop` vocabulary/counts; no C6 refusal. Provisional eligibility → pending_final_eligibility. Zero capture does not consume a slot. |
| A18 | `_test_summary`: one-sided 95% Clopper–Pearson via production incomplete beta; missing assignments retained. |
| A19 | Exactly eight eligible token-identical W1 runs, second-stage indicator, admission within 2 s. Recorded G1 waiting is an above-E+δ sidecar sample before release. Numbers print even if treatment was not delivered. |
| A20 | `dc.capture/analyze_windows`: benign DC desk actually runs; whole-member and owned integrals, battery-assist disclosure, own five-term h=0 LOTO model. GPU coefficients never transfer. Non-benign rows sealed; comparison presence/status only. Missing DC never selects GPU. |
| A21 | `raw.member` calls production stamp_mapping over all stamps, anchor widened; optional exported offset_ns checked exactly. SampleColumns preserves adapter float accumulation/rounding order. |
| A22 | U3 heavy-tail trigger uses each difference's zero-centred leave-one-out RMS. |
| A23 | Only U1–U3 FAIL bars pool entry; INCONCLUSIVE prints and counts. |
| A24 | Barred windows have no GPU fits/scores and no U6 contribution. DC residual fits withhold barred/ineligible members. |
| A25 | T fits/scores withheld and thresholds null until calibration_complete; prospective freeze checked before opening T sources. |
| A26 | Undefined eligible C score holds the threshold with nonfinite_calibration_score; m never silently shrinks. |
| A27 | C sabotage enters no GPU fit, score, known-H or carrier curve; DC sealed. |
| A28 | battery.unobserved is retained for GPU; window B bar unavailable. |
| A29 | Actual seed and four-slot cohort/model-stack identity checked; named classes exclude mismatches. |
| A30 | Missing/Unknown PM is not X3; U1(a) inconclusive. |
| A31 | Predeclaration prints as non-veto consequence; arithmetic still runs. |
| A32 | No-rebuild sensitivity remains print-only and comparator-exempt. |
| A33 | Simpson integration in w=√v, 4000 steps. |
| A34 | W1 is a window record in windows[]. Selection-only W1 is refused by analyze and io.load, even with anchor_members. Its screened thermal records supply U1–U3 and contrast; W1 never enters C/T fits or m. |
| A35 | roster(escalated=True) accepts 24 members; 23/24 supplemental W1:5 replays print descriptively, outside U3/U4/fits/m. |
| A36 | B bar, consecutive failures and release presence print; missing operational B release never refuses analysis. Arm enforcement remains external. |
| A37 | `apple.reduce_sol.SampleColumns`: fixed `INTERIOR_SEAM_NS=1000`; snap a later start to the previous end for an interior gap or overlap ≤1000 ns before energy, gap or coverage arithmetic. Power, native PM and mapped columns snap the original record sequence, before power sorting/filtering. Larger seams and all outer edges retain their placement. Power width/variable-support diagnostics are recomputed after snapping. `power/windows.py` documents its separate legacy float-quantum fallback. |
| R23-E1 | `engine._rows/_member_reasons`, `acceptance.window_checks/battery/u4`, v4 thermal acceptance and W1 contrast exclude `captured:false`. Zero-capture final attempts have no pool entry or fits and do not consume a C slot; their retry takes that slot. Missing T assignments use only the last attempt per window, retaining that attempt's member reason/class or pool bar. A zero-capture attempt leaves the consecutive B-failure counter unchanged. |
| R23-1 | W1 window members pass the same `engine._screen_member` / `_member_reasons` and recorded-class union as C/T before `acceptance.anchor_diagnostic`. Runtime failures, charging flags and seed mismatches exclude the whole W1 anchor block. `anchor_sigma_w.W1_anchor_block` prints `included`, `excluded:<reason>` or `unavailable:<reason>`. Complete eligible synthetic C1–C8 + T1–T3 + W1 yields K=12; a missing/excluded W1 block is explicit even when K=11. K≥3 remains required. `sigma_w2_raw_j2=(MS_window−MS_error)/4` may be negative; `sigma_w2_reported_j2=max(0,raw)` and `anchor_sigma_j=sqrt(reported)` print without a veto. |
| R23-2 | Carrier H=0 prints the strict untouched score exceedance fraction against other-carrier thresholds. H50/H90 search the all-carrier prefix at H>0 only. Each crossing prints its own status and `level_reached_at_h0` flag; a level already reached at H=0 remains undefined, including bootstrap replicates. |
| R23-3 | Carrier pair status is `ok` for ≥40 original carriers with defined thresholds, even when later doses/crossings are unreachable. `<40` is `insufficient_calibration`. Per-crossing undefined statuses distinguish `undefined: dose unreachable`, `undefined: level not reached` and `undefined: level reached at h0`. The legacy aggregate `crossing_status` field is removed. |
| R23-4 | `dc.analyze_windows(gpu_fits=...)` prints whole-member DC-in J, turn-owned DC-in J/turn rows and battery-assist disclosure for every captured benign member, including W1, anchors, sentinels, ineligible/barred members and T before calibration completes. Only residual rows and ordered LOTO training IDs come from logged GPU fits. The five-term model is refit at h=0 on DC-in energies; missing training evidence withholds the residual rather than shrinking its training set. Value rows without a GPU row have `residual_status: no_gpu_row`, no residual/model and no training IDs. Non-benign presence seals remain separate. |

The byte-pinned fitter is unchanged: `_frozen_residual.py` is the
`4d54cb47b` implementation pinned by `cda28a5ef`, SHA-256
`d187698d5cc8a0856ffe730079e16a164a5ac338b9dd0a4b10be8cac6206acef`.
The adapter explicitly selects the five-term sequence design.

## Raw export adapter interface

Input schema remains `joulewise.align_v4.analysis_input.v1`. The lead owns
the common raw-layout export; this interface maps it into Sol. Each window has
its roster, attempt identity/status and either thermal_source + residual_source,
or raw_source. References are
`{"path":"relative/path","sha256":"64 lowercase hex"}`.
A raw-source JSON has members[] exactly matching the roster. Captured rows supply:

- run_id, captured/status, episode (Episode JSON reference), powermetrics
  (NUL-framed plist reference), first_record_endpoint_s, nominal_interval_ns;
- every paired stamp as ClockStamp fields in seconds, clock_evidence including
  anchor bounds, optional independently exported production offset_ns;
- registered_span_ns, registered_os_readings, episode os_readings, journal
  (observed sidecar rows or a JSON reference), optional gate_journal and
  per-turn generation turn_rows;
- authenticated identity_sha256, battery, cohort_identity, frozen four-slot
  configuration, optional cache_statistics, exclusion_codes and replay tag;
- for benign DC, raw JSONL dc_streams references and member_span_ns.
  Production KM003C decoding/clock fit runs on verified bytes. Sabotage
  DC streams are never opened by this adapter.

Reasoning comes from recorded Episode hidden_tokens; the exporter must bind
that count to its reasoning_tokens evidence (A0). U3 evidence includes the
frozen pilot pairs and r1_d_screen. r1_sensitivity.states has three rows:
g0_slow_c, turn_owned_j, designed_target_c, token_identical; plus replay energies
and delta_slow_c. W1 also supplies recorded template/arm/stage and authenticated
token-identity evidence for the existing contrast desk. Missing evidence stays
unavailable.

W1 must be delivered as a window record in the same `windows[]` export as C/T,
with full member records (`slot`, `captured`, `thermal`, `summary`, and any
`source_flags`) through the source-bound adapter above. `selection_desk` or
`selection_source` without a W1 window refuses before export sources are opened;
`selection_desk.anchor_members` does not restore that retired compatibility
route. There is no legacy selection-only input API. If a redundant snapshot is
present with a W1 window, the window supplies all W1 analysis evidence.

R23d (lead ruling on the Opus cold review, 2026-11-08): W1 has no engine
roster, so in strict (non-synthetic, and always in `io.load`) mode
`engine.slot_run_id` binds the W1 anchor role to the registered ordinals 1-4:
exactly those slots must carry `series_role: anchor` and the `W1:<run_id>`
prefix. A missing or mismatched role, an anchor role on any other ordinal, a
missing ordinal or a bare anchor ID refuses. The same function serves the
analyze manifest and W1 loops, the `io.load` manifest and roster loops and
`raw.window`. The synthetic API stays lenient. The dead selection seam is
deleted: `io.load` no longer reads or census-records `selection_source` and
no longer writes a thermal-only `selection_desk`, and the CLI no longer copies
one. Selection-only input still refuses. Witnesses:
`tests.align.test_v4_r23d_engine`, including the reviewer's p1-p6 outcomes.

Behaviour change: W1 U1–U3 checks and contrast now see the screened thermal
fields, the same as C/T: `captured`, `analysis_ineligible`, `analysis_classes`
and summary-derived `turn_counts`. They no longer use an unscreened selection
snapshot. For example, a recorded X3 on a W1 replay member reaches U1's thermal
exclusion count, removes that member from U2's temperature range and makes its
U3 pair inconclusive. Contrast receives those same screened records. No seed
or successful runtime is inferred from thermal evidence alone.

Exporter contract check (R23c): Episode thermal policy uses
`hardware.thermal.policy.sensors.s_fast` and `.s_slow`, mapping roles to actual
journal sensor names (for example F/S); journal `sensors` values use those mapped
names. Thermal desk outputs use `fast_c`/`slow_c`. Native/release anchor `run_id`
values MUST be series-unique `<window_id>:<run_id>` (for example
`C1:align-pilot-v3-episodes-a-e01`), including W1. Bare anchors and windows
mixing bare and prefixed anchors refuse. File loading enforces this even if
the document is marked synthetic; only the trusted synthetic in-memory API
retains local anchor IDs. Manifest and observed roster checks strip a matching
prefix only for anchor R15 comparison; the exported ID remains intact in desk
identities and outputs. A wrong window prefix or a prefixed non-anchor refuses.
The raw adapter validates roster and source prefixes before opening member
references. Exported roster/source
IDs must agree. A captured anchor Episode may retain its original local ID:
the adapter verifies the suffix and binds derived rows to the exported ID,
without changing raw bytes. A different Episode ID/prefix refuses. No sensor-key
or input-schema migration was made.

No config paths are followed. Traversal, symlinks, sealed path names and other
/Users/edr checkouts refuse before target reads. Native file mode is source-bound;
inline members are reserved for the synthetic/trusted API. Freezes bind C inputs,
acceptance evidence, cohort, manifest and loaded scorer/reducer. Decisions and
refusals are never cached.

## Streaming reducer and cache

`apple/reduce_sol.py` imports the Sol architecture from
`origin/perf/2026-11-08-reduce-sol` and replaces its whole-XML extractor.
`_reduce_scan.c` validates the conservative common plist grammar, including
ignored subtrees, without constructing a tree. It returns offsets for timing,
thermal state, processor rails/counters and GPU DVFM fields. Unhandled syntax,
encodings, entities, scalar forms, shapes or depth go to plistlib. Both paths
end in one column builder and the same diagnostics.

`_reduce_native.py` builds an optional accelerator locally with system cc and
stdlib facilities, without installation or network. The temporary compiled
artifact is keyed by source, flags, OS and architecture. Without a compiler the
reference route still works, at reference speed. The receipt records
scanner_available; release throughput requires it true. Cache identity covers
loaded Python code and loaded native source/binary.

Cold parsing reads bounded chunks once; a helper hashes those exact chunks in
order while parsing. Frames are released promptly. Observation cache keys are
raw SHA-256 × producer ID; fixed-order little-endian columns have a header,
checksum and atomic replacement. A source/stat index only selects whether to
try a hit; every hit rehashes raw bytes. Changed metadata selects fresh parsing;
a concurrent mutation refuses. Nothing in the cache grants eligibility.
Ownership, clock mapping, energy tables, fits and decisions run fresh.

Workers use spawn and return in input order. Reducer workers=0 selects a
conservative free-core/free-memory ceiling, falling back to one if free memory
is unavailable. Explicit reducer counts are bounded at eight.

## Incremental operation on the Air

As windows land, expand the immutable manifest and recompute its landed prefix.
Old observations reuse columns; all energy tables/decisions rebuild. Use a new
output directory per run.

```sh
python3.13 -B scripts/analyze_align_v4.py --input INPUT.json --output C3-fill --through-window C3 --cache COLUMNS --workers 2
python3.13 -B scripts/analyze_align_v4.py --input INPUT.json --output C8-freeze --calibration-only --cache COLUMNS --workers 2
python3.13 -B scripts/analyze_align_v4.py --input INPUT.json --output T1-fill --through-window T1 --thresholds C8-freeze/thresholds.json --cache COLUMNS --workers 2
```

Future exports are filtered before opening. T requires its prospective freeze.
Calibration-only/full desk loading share verified bytes within the invocation.
The raw-only per-window harvest CLI is also available:
`scripts/reduce_powermetrics_sol.py --jobs WINDOW.json --cache COLUMNS --output WINDOW-columns.json --workers 0`.

Fill output contains numeric diagnostics, null/status pairs and a scalar JSON
pointer inventory. Verdict/stdout contain structure and fixed codes only.
Non-benign DC hashes are not numeric cross-build targets.

## Verification and limits

Failing-first R23 witnesses: `tests.align.test_v4_r23_engine`; retained R21/raw
witnesses: `tests.align.test_v4_r21_engine` and `tests.align.test_v4_raw_engine`.
R23's PM test records are constructed from scratch in `tests.align.v4_synthetic`.
The two reducer cases that read committed captured fixtures or their realistic
template were not run in this session. The executed reducer tests compare columns
and production turn energies byte-for-byte against plistlib on synthetic records,
including malformed/duplicate/unusual XML. The retained suite also has an exact
allowlist of committed small fixtures for lead-controlled verification.
The synthetic tests check a single cold raw open, hit rehash, mutation, checksum damage,
loaded-code identity and serial/parallel CLI equality.

R23 qualification covers ±1000/±1001 ns seams, both tiny edge gaps, exact overlap
energy, epoch-float placement, C3 zero-capture then C3#2 through T3 with eight
counted C windows, K=12 and negative/positive anchor moments, strict H=0 rates,
unreachable and H=0-reached crossings (including bootstrap), and exact GPU/DC
row/training parity. DC numeric scaling uses synthetic capture output; the
separate raw-adapter witness integrates a synthetic KM003C stream and verifies
its independent five-term fit. These establish software behavior only.

`scripts/benchmark_v4_r21.py` generates eleven windows and 242 raw members.
It compares complete fill/verdict bytes for serial/parallel cold/cache modes.
`ENGINE-sol-r21-benchmark.json` records times, digests and same-input parser
comparison with the committed pre-change Sol reducer and plistlib. Cold means
empty derived cache, not flushed OS cache. The machine was contended. Short
synthetic members prove shape/equality, not full-duration or hardware validity.

Lead gates: exporter integration, a quiet Air throughput rerun, independent
comparator/release rehearsal, and live/scientific gates. No MLX code changed;
this diff needs no new Metal test. The full suite was deliberately not run
under the assignment's blinded-job restriction.


Final local receipt (Python 3.13.18, contended machine): 54.43 MB parser input,
40.70 MB/s/core for the old extractor and 548.51 MB/s/core for the scanner.
The 845.24 MB, 242-member rehearsal took 3.06 s serial cold, 3.41 s with two
workers cold, 1.93 s serial cache and 2.86 s with two workers cache. All four
complete fill/verdict byte streams matched; each pair had 56 C calibrators and
T3 was fitted. These short traces favor serial execution. This rehearsal's DC
inputs were absent; separate synthetic DC integration/LOTO witnesses passed.
It does not establish real DC throughput or full-duration scaling. Earlier
before/after JSON receipts are development snapshots; the R21 receipt is final.

R21 baseline verification: 179 tests passed across eight explicitly selected modules;
compileall and git diff --check passed. See the engine-fix run report for commands,
fail-first evidence, changed files and the exact lead handoff.

R23 verification: 125 focused tests passed across six complete synthetic modules
and 21 selected synthetic reducer cases, one module per process. Named-path
compileall and `git diff --check` passed. See
`docs/run_reports/2026-11-08-engine-r23.md` for commands, failing-first witnesses,
the two deliberately unrun captured-template reducer cases, and the export handoff.

R23b verification: **136 targeted tests passed**, one module per process,
including 27 R23 hand witnesses, seven raw-adapter cases and 22 synthetic
reducer cases. The supplied p1/p2b/p3 probes confirm the retry's recorded X3,
W1 K=11 for each bad anchor, and the B-failure sequence 0,1,1,2.
Named-path compileall and `git diff --check` passed. Commands, compatibility
notes and the local-commit handoff are in
`docs/run_reports/2026-11-08-engine-r23b.md`. No MLX code changed or native
Metal test was added; this qualification does not validate live hardware.
