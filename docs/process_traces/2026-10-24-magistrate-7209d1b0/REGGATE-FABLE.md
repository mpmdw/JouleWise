claude-fable-5-1
SEAL: ADMIT-WITH-CORRECTIONS

Cold judge: blind, executing. Worktree /Users/edr/code/jw-wt/reggate-fable detached at 81c78f79c (clean). Scratch /private/tmp/reggate-fable. Session 01:05–01:20 PDT 2026-10-25. Nothing written outside scratch; no launchctl/sudo/powermetrics/pmset/caffeinate; no model loads; no whole-module run of test_bytes_analysis, test_bytes_agreement or test_bytes_coverage_map.

The single correction is tooling for the flip itself (finding 1): the generator the charge names as the flip mechanism can only write `draft`. It is small and certain. Nothing I executed makes a printed number wrong or untrustworthy.

## Re-derivation table

| Quantity | Registered | Mine | Match |
|---|---|---|---|
| estimator SHA-256 joulewise/bytes_analysis.py (§13, §18) | 18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71 | shasum of the file at 81c78f79c: 18582818c7e0…dffc0a71 | yes; bound in configs/b6/packs/bytes-s{1..6}-p1/registration.json estimators[0..2].version |
| catalog SHA-256 configs/b6/flag_catalog_b6.json (Appendix A) | 01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c | shasum: 01767fe4…1dd0c | yes; flag_catalog_sha256 in each of the six registrations |
| manifest SHA-256 (§4) | 76452108c1a1…356264 | shasum: 76452108c1a1…356264 | yes; also REGISTERED_MANIFEST_SHA256 in bytes_analysis.py:40 |
| §4 table W, KV, R, b for 10 models; b = W+KV | as printed | from configs/bytes/bytes_manifest.json | all 40 integers equal; ranges 32.34→32, 70.96→71 |
| §2 revisions (10) | as printed | roster.json and manifest | all equal |
| catalog counts | 269 = 41/19/209; BYTES 41/18/210 | Counter over catalog; over pack flag_effects | yes; only diff cell.below_minimum→DISCLOSE; all six packs identical |
| Appendix A lists | 18 EXCLUDE_WINDOW, 41 EXCLUDE_MEMBER | set-compare with pack flag_effects | identical sets |
| S programmed span, 6 rows | 19217.679471871463 / 20205.635101731605 / 21639.34651295436 / 23229.354256286348 / 19051.636769862467 / 14846.686081818749 | own code from raw H + BY-H2 (168 receipts) | exact rational = /table/S_exact, diff 0.0 all six |
| T_stream_max_s, 6 rows | 96.39069404196925 / 102.24723962508142 / 112.22990612499416 / 142.9448628750397 / 201.49829895899165 / 111.53124241600744 | max stream_s over the pack's science runs | exact all six (unchanged if references included) |
| B_s / B_w / B / WAIT / fixed / P / smoke / P+smoke, 6 rows | §5 disk table | own code: r_s, r_w, allowances, ceilings | integer-equal all 48 values; WAIT 18,010,999,755; fixed 4,046,531,103 |
| margin | 135722362995148/4081589090824127 | llama-70b soak 23 runs max/min−1 | exact |
| stage overhead | 160506586104631419/3500000000000000 | (16·44.44705606997013 + 12·47.741649309794106)/28 from raw stage_timestamps+run_clock | exact |
| clock holds H = 5000/T − 0.25 ppm | 51.622227394 / 48.651075651 / 44.301404992 / 34.728521784 / 24.564105260 / 44.580487778 | Decimal | match to 9 decimals, all six |
| t quantiles §7/§10 | 4.1786; 3.7586; 3.9467; 7.1849; 4.1048; block-5 2.2622 | student_t_quantile | 4.178622, 3.758586, 3.946684, 7.184869, 4.104812, 2.262157 |
| §9 coverage table, 18 rows × 5 numbers | as printed | FIX416A-COVERAGE.json (36 entries, draws 400) | 0 mismatches; min HC3 plain-95 0.9475 |
| §9 floor | 0.93 | 0.95 − 2√(0.95·0.05/400) = 0.9282 | yes |
| §8 worked example | bytes line 0.016966 + 0.010685·b; intervals [0.036672,0.038672], [0.181187,0.197589], [0.050714,0.052714]; word bytes; ln 0.0087 | freeze_lines/h1_point | all match (time upper 0.052715 at 6 dp, text prints 0.052714: rounding of a synthetic number, no effect) |
| §2 8B-8bit resolvability | 5 succeeded runs, decode 12.02–12.04 s | H export csv | r01–r05 succeeded, unexcluded, 512 tokens, 12.0167–12.0398 s |
| agreement campaigns | 0 above bar | tests run here | bytes: compared 314837, above 0; withheld: compared 219549, above 0 |

Not re-verified: fixed_desk_s = 1185 s (ruled H desk input; not recomputable from the trees); the 25-archive replay claims; the AST claim that FIX-416-C changed only neg8 ingress (the coverage table is at 76c44759, agreement at 18582818 is what I ran).

## Findings

1. SHOULD_FIX (correction, small and certain). The flip mechanism does not exist: scripts/bytes_plan_trees.py hardcodes `status="draft"` / `draft_status="draft"` at lines 179, 256, 270, 307, 348 and has only `--check`; tests/test_bytes_plan_trees.py:140-141 asserts `draft`; the pin fence (`scripts/bytes_plan_trees.py --check`, `scripts/repin.py --check`) would fail after a hand edit of the twelve JSON files. Exact edit: add `--register-pass {1,2}` to the generator's argparse; when given, write `status`/`draft_status` = `"registered"` for that pass's six registrations, plan trees and collection plans (leave the other pass `draft`), and in `draft_notes` delete the three stale sentences ("… a draft with Mac and B2 slots open; not registered or armable.", "Estimator versions are null until the twin agrees …", "… full model stacks and frozen projection receipts remain unobserved.") since estimators are bound and identity_pins.json carries 11 stack keys per BYTES unit; change the test to expect `registered` for pass 1 and `draft` for pass 2; regenerate and repin. No arm or loop code reads this status (grep: joulewise/b6/{registration,loop,arm,compose}.py), so the flip is a registration record, not a gate; the arithmetic it freezes is already bound by SHA. Repro:
```
$ grep -n 'status="draft"\|"status": "draft"\|draft_status="draft"' scripts/bytes_plan_trees.py | wc -l   → 5
$ grep -n "register" scripts/bytes_plan_trees.py | grep -v "registration" → (nothing)
$ python3.13 -B scripts/bytes_plan_trees.py --check → verified 12 BYTES draft registrations and 12 fixed pass trees (rc 0)
```
2. NIT (text/metadata). configs/campaigns/bytes_v1/roster.json carries `identity_status: draft_pending_C4` on every model while §18 marks C4 FILLED (identity_pins.json BYTES units have 11 stack keys each, verified). No code consumes the field (grep joulewise/ scripts/: only an unrelated local in doctor.py). Edit: set to `pinned_C4` or drop the field when the generator flips.
3. NIT (doctrine, recorded, no change needed). Arm-time refusals that are not a directly measured physical hazard: precheck `certain_exclusion` → DO_NOT_START on `model.hash_mismatch` (joulewise/b6/precheck.py:241, 386) and `plan.dispatch_unresolved`. Both are block-6 inherited rules that refuse only a session the registered acceptance would exclude whole (`model.files_differ_from_registered` EXCLUDE_WINDOW), so they cannot select data; the §5 sentence "no arm-time projection is derived" is about the stack projection and remains true. The disk WAIT compares physical free bytes with P (precheck.py:92, thresholds `headroom 0` for bytes packs, confirmed) under P0 ruling 5. Everything else that waits is physical (battery float, thermal, agent census, sleep assertion, instrument cadence, contention dwell, clock) and `agents.hid_recent` is flag-only as the code comment derives.
4. NIT (scheduling). DST repeated hour 2026-11-01 01:00–02:00 PDT is handled by "scheduling" (DISPOSITIONS-416) but nothing in configs/b6 or loop.py encodes it; `stopping.end_t0_before` 2026-11-02T00:00-08:00 still permits a t0 on the evening of 10-31. With S up to 23,229 s plus the 7,200 s wait budget, no pass-1 t0 should fall between about 2026-10-31 16:30 PDT and 2026-11-01 02:00 PST. One line in the loop's schedule, or an operator note beside the arm, suffices.
5. INFO. `--stage1-commit` (scripts/bytes_analyze.py:66, scripts/b6_release_subset.py:21) is validated as 40/64 hex only; neither checks that the commit exists or contains predictions.json. Under D-161 this is process, not enforcement; the release record carries the hash. No change.
6. INFO. The sizing receipt `request_s` (168 runs) is the sampler window span `sampling_started → sampling_stopped` in events.jsonl, not the NEG-8 request span (tokenize phase_start → decode phase_end); the two differ by ≤ 3.4 ms. It feeds only the margin and allowances of S and P, never a printed number. The NEG-8 reference span in code is the request (bytes_analysis.py:479 `_request_span`), as §7 says.

## Text against code (sampled claims, each read against the running code)

- Cell rule §7: weights 0.2/0.8, V = 0.04 s_r²/n_r + 0.64 s_b²/n_b, df = min(n_r,n_b)−1, Bonferroni t at 1−0.05/42 widens h only, B = math.fsum of three stratified kinds, interval not clamped (bytes_analysis.py:1196–1241, 1258–1330). Match.
- Units not runs, minimum 5, DC-only removal for missing meter, flagged-inclusive restores only excluded-with-valid-record (`_kept` 1176–1193; reduce_models 1355–1358). Match; `cell.below_minimum` DISCLOSE override applied by acceptance.py:163–170 for bytes packs pass 1/2.
- u (§7): edge power = max over the two adjacent samples and samples within ±r_max, times (r_max + Δt); Δt = STEP_MS[rate_idx] (20 ms at idx 2); dropped device sample → MeterGapError → `bytes.meter_gap` (508–585; km003c_parse STEP_MS). Match.
- v and battery term (BAT-2): τ = 2·T_SMC + max poll interval, v_edge over [edge, edge+τ), marker by B0AC < 0 in the τ-shifted span (491–506, 541–552). Match.
- NEG-8 (§7): request span tokenize→decode end; corpus first 12, ≥ 6; ≥ 2 start and end; allowance = max(count-adjusted bound, spread of start/mid/end means); each run carries ½A·scale; scale = max(1, E/E_ref, T/T_ref) until test 7; `test7_passed` true refused (831–917, 1270–1274, 427–430). Match.
- Blinding (§11): PACK_RANGE (0.8, 1.25), CONFIG_RANGE (0.97, 1.03); fit set = {1.7B, 4B, 8B-4bit} by name, every other science config withheld to `<keys>/../withheld/<pack>/<session>.runs.csv`, written before the public CSV, count-only locator in the sidecar; keys bound per session by SHA-256 with refusal on a changed digest; exclusive publication by hard link; release of a held-out key requires the stage-1 commit (export_runs.py:586–770; blinding.py:16–17, 60–110, 139–144, 209–223; b6_release_subset.py:21–23). Match.
- Agreement bars (§12): 1 % of (h+B), 1 % of (h+B)/T, 1 % of HC3 half-width, 1 ms durations, half-unit of §14's place for the rest (tests/test_bytes_agreement.py:158–230). Match.
- Clock gate (§5): precheck and arm share measured_rate_bound with h_ms 0, limit 5 ms, margin 0.25 ppm, T from sizing_b5.json; a_j absorption and u_j read-skew test with `clock.step_unmeasured` disclosure (hazards/clock.py:261–273, 386–394; precheck.py:38–61). Match.
- Contention (§5): absent regime receipt → "unavailable" line, no refusal (bytes_gates.py:327–333). Match.

## Known-bytes stream test deferral (P0 ruling 9)

Safe. The probe (scripts/bytes_stream_test.py, README §Known-bytes companion probe) produces a receipt compared against rails and DC input; nothing in joulewise/bytes_analysis.py reads it (no function or constant refers to it), so it cannot change an exclusion, a cell, a line or a word. Its outcome is an annotation printed beside each boundary's claim lines (§1). Pass-1 energies stay blinded by the pack and configuration factors and the withheld store until stage 1, so running it after collection cannot tune anything to seen data. The only real condition is the one the registration already states: it runs from its own non-claim checkout and does not touch the pass-1 measurement pin or its data.

## Slot table (§18)

| Slot | Status | Evidence I executed |
|---|---|---|
| Manifest SHA-256 and table | FILLED | shasum equal; 40 integers and 10 revisions equal; ranges 32/71 recomputed |
| 8B-8bit revision | FILLED | roster, manifest, §2 equal (48a0b75b…); generate_configs.py --check: 500 configs verified |
| 8B-8bit kept | FILLED | H export: 5 succeeded unexcluded 512-token runs, decode 12.0167–12.0398 s |
| b range; R range | FILLED | 32.34→32; 70.96→71 |
| C4 pins | FILLED | identity_pins.json: 10 BYTES units × 11 stack keys; repin.py --check PASS 16 families |
| P_limit / contention | FILLED (unavailable, flag only) | code path bytes_gates.py:327; tests.test_bytes_gates OK (contention lines "unavailable") |
| Clock-gate values | FILLED | six H recomputed, match |
| Disk footprint | FILLED | six P and P+smoke recomputed from raw, integer-equal |
| C5 sizing | FILLED | six S and T recomputed from raw, exact |
| Test 7 | FILLED (no pass established) | TEST7.json structure read; scale formula in code; `test7_passed: true` refused |
| Known-bytes stream test | PENDING, soundly deferred | see section above |
| Coverage table | FILLED | 18 rows × 5 counts equal FIX416A-COVERAGE.json |
| Estimator SHA | FILLED | equal in file and six registrations |
| Catalog SHA | FILLED | equal in file and six registrations |
| B4 paths/flag/--stage1-commit | FILLED | blinding.py:172–179 withheld_path; loop_bytes.json root /Users/edr/night-b6/loop-bytes; flag DISCLOSE in catalog; release requires 40/64-hex commit |

## Doctrine and numbers

- Refusals: see finding 3. No refusal in the analysis or desk path except StorageStop classes (storage/custody, allowed).
- Bars: 1 % of (h+B) (derived §12), 0.93 coverage (derived §9), 5 ms / 0.25 ppm (block-6 S-7 derivation, re-read), 1 ms step (registered block-6), 0.13 mJ gap bound = 1 % of 0.013 J (§6), 1 ms / 1 µJ / 1e-4 W printed places (§14 derivations check arithmetically), smoke share ceil(2·B·m/n). I found no printed bar without a derivation. `hid_idle_min_s` is flag-only with its stated lack of a joule derivation.

## Executed

```
$ git rev-parse HEAD → 81c78f79cf9935cbb678f358e606f32a59b0033b ; git status --short → (clean)
$ shasum -a 256 joulewise/bytes_analysis.py configs/b6/flag_catalog_b6.json configs/bytes/bytes_manifest.json
18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71  joulewise/bytes_analysis.py
01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c  configs/b6/flag_catalog_b6.json
76452108c1a10b1f63b48fc95b306b6c4aa936a0d2e94244be65dc067c356264  configs/bytes/bytes_manifest.json
$ python3.13 -B -m unittest -v tests.test_bytes_agreement.AgreementTests.test_bytes_world tests.test_bytes_agreement.AgreementTests.test_withheld_campaign_missing_files_and_uncollected_pass
Ran 2 tests in 84.372s  OK
agreement bytes: compared 314837, equal 307662, under the bar 7175, above the bar 0; diagnostics 102274, different 622
agreement withheld: compared 219549, equal 214685, under the bar 4864, above the bar 0; diagnostics 68146, different 701
$ python3.13 -B -m unittest tests.test_bytes_plan_trees tests.test_bytes_gates tests.test_bytes_agreement.FenceTests tests.test_bytes_agreement.ComparerRegressionTests.test_registered_BW_and_drift_scale_mutations_are_above_bar
Ran 34 tests in 6.283s  OK
$ python3.13 -B scripts/bytes_plan_trees.py --check → verified 12 BYTES draft registrations and 12 fixed pass trees (rc 0)
$ python3.13 -B configs/campaigns/bytes_v1/generate_configs.py --check → verified 500 BYTES science configs (10 models x 50) (rc 0)
$ python3.13 -B scripts/repin.py --check → PASS 16 pin families current (rc 0)
$ clock holds: Decimal(5000)/T − 0.25 for the six T → 51.6222273938909, 48.6510756508823, 44.3014049921001, 34.7285217841016, 24.5641052596061, 44.5804877780360 (all match the table)
$ coverage check script → 18 rows OK, mismatches 0, min HC3 plain 0.9475
$ student_t_quantile → H1 df9 4.178621925093584; H2 df8 3.758585962035755; df7 3.9466838663208126; df3 7.184868893978148; k11 df7 4.104811556134624; 0.975 df9 2.2621571627982036
$ worked example → bytes line [0.01696577005836904, 0.010685422699013663]; word bytes; bytes [0.036672,0.038672] ln 0.0087; resident [0.181187,0.197589]; time [0.050715,0.052715]
$ raw re-derivation (fork; scripts /private/tmp/reggate-fable/rederive/{extract,compare,derive}.py; report RESULT.md): 168/168 receipts bit-equal; six rows S, T, B_s, B_w, B, WAIT, fixed, P, smoke, P+smoke all exact; run_clock.jsonl digests equal MEASUREMENTS.json
$ catalog/appendix script → catalog 269 {DISCLOSE 209, EXCLUDE_MEMBER 41, EXCLUDE_WINDOW 19}; appendix window 18 == pack 18; member 41 == 41; pack vs catalog diffs {cell.below_minimum: EXCLUDE_WINDOW→DISCLOSE}; six packs identical
$ manifest script → all W/KV/R/b True; b range 32.34127063682461 → 32; R range 70.96138796209513 → 71; roster and manifest revisions match §2
$ H export → qwen3-8b-8bit r01..r05 succeeded, excluded False, dur_decode_s 12.0167/12.0224/12.0315/12.0398/12.0355, 512 tokens
```
