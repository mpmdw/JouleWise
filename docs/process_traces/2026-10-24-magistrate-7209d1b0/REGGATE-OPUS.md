claude-opus-5-5
SEAL: ADMIT-WITH-CORRECTIONS

Registration cold gate, BYTES pass 1 (bytes-s1-p1 … bytes-s6-p1), worktree detached at 81c78f79c (#579).

I re-derived every number the registration copies from the raw data and from the code, and all of them match exactly. I found no defect that would make a printed number wrong or change which data count. Two corrections are needed so the flip can actually be done and so the frozen text is true (C1, C2). There is also one precondition the registration sets itself (§19 and P0 ruling 11), for which I found no evidence: the whole test suite on the final tree. It must be met before the flip commit.

## Re-derivation table

The sizing rows come from my own script, `/private/tmp/reggate-opus/resize.py`. It reads the raw MEASUREMENTS.json run receipts of both sessions with their decimal lexemes kept, and measures raw bundle bytes itself (st_blocks×512, inode-deduplicated, including directories) under `archive/sources/{bound,claim}-runs/<run>`. Run-to-model mapping comes from the kit plan tree (in the test-7 stages, odd-numbered runs are the workload and even-numbered runs are the reference). Stage overhead is computed from `custody/collection/run_clock.jsonl` and `stage_timestamps`. All arithmetic is exact rationals.

| Quantity | Registered | Mine | Match |
|---|---|---|---|
| Timed observations (H + BY-H2) | 168 (95 + 73) | 168 (95 + 73) | yes |
| retained_bytes = 2 × raw | (implied) | 0 of 168 differ | yes |
| r_s (B/s) | 4502241280000000000000/1799796660838183 | same; witness BY-H2 test7-qwen35-122b-start-r02 | exact |
| r_w (B/s) | 16084172800000000000000/12509476685523987 | same; witness H neg8-refcorpus-r15 | exact |
| margin | 135722362995148/4081589090824127 | same (llama-70b soak, 23 runs) | exact |
| stage overhead (s) | 160506586104631419/3500000000000000 = 45.85902460132326 | 45.85902460132326 (16 H + 12 BY-H2 observations from my own run_clock union) | yes |
| Runs per model | 70B 34, Next 11, 122B 23, reference 65, others 5 | same | yes |
| s1 S / T | 19217.679471871463 / 96.39069404196925 | 19217.679471871463 / 96.39069404196925 | exact |
| s2 S / T | 20205.635101731605 / 102.24723962508142 | same | exact |
| s3 S / T | 21639.34651295436 / 112.22990612499416 | same | exact |
| s4 S / T | 23229.354256286348 / 142.9448628750397 | same | exact |
| s5 S / T | 19051.636769862467 / 201.49829895899165 | same | exact |
| s6 S / T | 14846.686081818749 / 111.53124241600744 | same | exact |
| s1 B_s / B_w / B / P / smoke / P+smoke | 30,319,753,844 / 21,747,443,215 / 30,319,753,844 / 100,708,038,301 / 1,940,464,247 / 102,648,502,548 | identical | exact |
| s2 | 31,646,393,595 / 23,017,716,103 / 31,646,393,595 / 103,361,317,803 / 2,025,369,191 / 105,386,686,994 | identical | exact |
| s3 | 33,327,461,374 / 24,861,123,518 / 33,327,461,374 / 106,723,453,361 / 2,132,957,528 / 108,856,410,889 | identical | exact |
| s4 | 38,166,208,818 / 26,905,490,356 / 38,166,208,818 / 116,400,948,249 / 2,442,637,365 / 118,843,585,614 | identical | exact |
| s5 | 31,729,055,015 / 21,942,279,904 / 31,729,055,015 / 103,526,640,643 / 2,538,324,402 / 106,064,965,045 | identical | exact |
| s6 | 20,269,084,650 / 16,535,726,522 / 20,269,084,650 / 80,606,699,913 / 1,621,526,772 / 82,228,226,685 | identical | exact |
| WAIT / fixed | 18,010,999,755 / 4,046,531,103 | 18,010,999,755 / 4,046,531,103 (read from bytes_mac_check sizing_b5.json disk_derivation) | yes |
| Committed configs/b6/registration/sizing_b5.json, six rows S/T/P/B | as above | equal | yes |
| Clock hold H (ppm), s1…s6 | 51.622227394, 48.651075651, 44.301404992, 34.728521784, 24.564105260, 44.580487778 | 51.62222739389, 48.65107565088, 44.30140499210, 34.72852178410, 24.56410525961, 44.58048777804 | yes |
| Hold as implemented (clock.measured_rate_bound via precheck.thresholds_for, h_ms = 0) | equality clears, anything above holds | s1 and s5: H passes, H + 1e-12 fails, −H − 1e-12 fails | yes |
| Estimator sha256 (joulewise/bytes_analysis.py) | 18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71 | same; also bound in all six p1 registrations, p2 null | yes |
| Catalog sha256 (Appendix A) | 01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c | same; BYTES effects 41 / 18 / 210, cell.below_minimum DISCLOSE | yes |
| Manifest sha256 | 76452108c1a10b1f63b48fc95b306b6c4aa936a0d2e94244be65dc067c356264 | same; §4 table 0 mismatches over 10 models × W/KV/R/b | yes |
| b range / R range | 32 / 71 | 32.341 → 32 / 70.961 → 71 | yes |
| §9 coverage table (18 rows × 4 counts and k) | as printed; minimum HC3 379/400 | 0 mismatches against FIX416A-COVERAGE.json; minimum HC3 plain-95 0.9475 | yes |
| t values §7/§10 (subagent, executed) | 4.1786, 3.7586, 3.9467, 7.1849, 4.1048 | same (analysis and twin quantiles) | yes |

## Findings

1. **SHOULD_FIX, correction C1. The flip to `registered` has no code path, and stale draft text would be frozen with it.**
   - **What the generator writes now** (`scripts/bytes_plan_trees.py`): status `draft`, which is hard-coded. `draft_notes` go into registration.json (:198–211) and are copied into plan_tree.json (:256–263, with `draft_status="draft"`). It also writes collection_plan.json with `"status": "draft"` and its own note (:271–274), and extraction_spec.json with `"draft_status": "draft"` (:307).
   - **What the validator and loop require:** `joulewise/b6/pack_registration.py:58` refuses a registered registration that still carries `draft_notes`. The loop (:184) rejects any pack whose status is not `registered`.
   - **Why a hand edit doesn't work:** `--check` would then fail as drift.
   - **Stale text that would be frozen:**
     - :205 "Estimator versions are null until the twin agrees…";
     - :274 "estimator versions remain null until the agreeing SHA";
     - :199 "Addenda 1-8 … a draft … not registered or armable".
     All are false for pass 1. The tree pins collection_plan.json by digest, and the smoke witness keeps the tree's exact bytes, so this text would be frozen.
   - **Exact edit, for pass_number == 1 only:**
     - (a) In the `if pass_number == 1:` block at :184–186, add `value["status"] = "registered"`.
     - (b) After the `value["draft_notes"] = [...]` list, add `if pass_number == 1: del value["draft_notes"]`.
     - (c) At :256 use `draft_status="registered" if pass_number == 1 else "draft"`, and at :263 pass draft notes only when pass_number == 2 (`**({"draft_notes": value["draft_notes"]} if pass_number == 2 else {})`).
     - (d) At :271 use status `"registered"` for pass 1, and drop or replace the :274 note for pass 1.
     - (e) At :307 apply the same conditional to `draft_status`.
     - Then run the generator in write mode, run `--check`, and validate all 12 registrations. The launch, projection and identity pins regenerate in the same run (P0 ruling 10). Smoke fingerprints come after.
   - **Evidence:** the subagent's in-memory flip of bytes-s1-p1 gives validator problems `['draft_notes']` with the notes and `[]` without them; bytes-s1-p2 still fails on null versions, as intended. Repro: `/private/tmp/reggate-opus/agent-text/s/c10.py`. The generator is not on the number-bearing list in `configs/b6/registration/acceptance.json` (16 paths, none of them the generator or the plan trees), so this is a light-tier change.

2. **SHOULD_FIX, correction C2. The registration text still describes a draft, and says "every marked slot", while one slot is soundly deferred.**
   - `docs/registrations/bytes_pack_v1.md:1`: change "version 1 (draft)" to "version 1".
   - Line 3: change "This is the draft of a pre-registration" to "This is the pre-registration".
   - Line 3: replace "It is not yet the registration. It becomes the registration when every marked slot below is filled and its cold gate passes (R8 item 8); the commit that does that is the registration time" with "It became the registration of the six pass-1 packs when every pre-collection slot of §18 was filled and its cold gate passed (R8 item 8); the known-bytes stream test outcome (§1) is filled after pass-1 collection and before stage-1 unblinding (P0 ruling 9). The commit that flips the six pass-1 packs is the registration time".
   - §13 (line 384): change "every pack remains draft until its registration gate" to "pass-2 packs remain draft until their registration gate".
   - §18 B2 SHA row (line 444): change "all packs draft" to "pass-1 packs registered; pass-2 packs draft".

3. **CONDITION, not a correction. The §19 / P0 ruling 11 whole-suite run on the final integrated tree: I found no record.**
   - The lane reports (FIX-416-B, C and E) say the whole suite was not run and is lead-owned.
   - `gh pr checks 579`: the 13 `test (3.13, N)` shards and `calibration-exits-exclusive` are **pending** at 81c78f79c. build, fences, quick, installed-wheel and crash-matrix pass.
   - The flip commit should follow a green whole suite on the tree that is flipped, with the run recorded, as the registration's own order requires. This is the registration's own precondition, not a new gate.

4. **SHOULD_FIX, not blocking. The known-bytes stream test (§1, §19): the deferral is safe, but the reading rule is not written.**
   - **Why the deferral is safe:**
     - No analysis code reads the outcome (`grep known/stream_test` in the analysis and twin: 0 hits).
     - The outcome changes no collected number, exclusion or estimator. It only adds a printed line beside the claim lines.
     - It runs before stage-1 unblinding, so the only BYTES data anyone can see are blinded fit-set and reference rails. Their absolute scale is hidden by the [0.8, 1.25] pack factor, so the test's reading cannot be tuned to the unblinded results.
   - **What is missing:**
     - "A boundary that does not respond as registered" has no registered criterion. Before the test runs (it can be after this flip and still before stage-1 unblinding), the registration should state which quantity is reported (for example, rails and DC-input energy above idle per known byte over the receipt's span, with its bound) and which outcome triggers the printed caveat.
     - `scripts/bytes_stream_test.py`'s receipt records no OS or runtime stack. The test's harvest should carry the same C4 stack fields, so a change in stack between pass 1 and the test is visible.

5. **NIT. fixed_desk_s = 1185 s includes a borrowed number.** It is 1 + 227 + 719 + 238, and the 238 s is "the prior block-6 median post-calibration" (by-slots `fixed-desk-decision.md`), not H's own value. Raw H has no post-calibration stage; BY-H2 measured 236 s (its `stage_timestamps`). The effect on S is about 2 s in roughly 19,000 s. S schedules sessions and prints no science number.

6. **NIT. `cell.below_minimum` is not printed as the code.** §6:170 says an unavailable cell is printed "with its reason, `cell.below_minimum`". The analysis prints the reason "fewer than five kept units per stratum" (`joulewise/bytes_analysis.py:1192`), and the twin prints `refused_below_minimum` (`scripts/bytes_twin.py:421`). It is a label only.

7. **NIT. The analysis prints exception text as NEG-8 meter-drop reasons.** It writes the exception text into `meter_unavailable_reason` (`bytes_analysis.py:~872`), while the twin prints the registered codes. The comparer maps both to codes (`reference_reason_code`, `tests/test_bytes_agreement.py:561`), so agreement is unaffected.

8. **NIT. The held-out release checks only the form of `--stage1-commit`.** `scripts/b6_release_subset.py:22` checks that it is 40 or 64 hex characters; it does not check that the commit exists or contains `predictions.json` / `predictions.sha256`. §11 describes this accurately. Hardening it before held-out release would make "release requires the stage-1 commit" enforced rather than procedural.

9. **NIT. No table formatter exists yet.** §14's decimals are used today only as comparer bars; `scripts/bytes_analyze.py` writes full-precision JSON, which §14:410 allows. The paper-table code must implement §14.

10. **NIT. A `KeyError` is possible but unreachable.** `bytes_analysis.py:1285` indexes `reference["families"][family]` directly. The case is excluded upstream, but if reached it would raise a `KeyError` rather than an `AnalysisError`.

**Doctrine dimension.** No new refusal of collection on a non-physical condition:
- **Precheck refusals** (`joulewise/b6/precheck.py:484–635`): disk, model-hash certain exclusion, acceptance certain exclusion, battery float, thermal, agents present, sleep assertion, instrument cadence, contention dwell, clock. All are the measured-hazard set inherited from block 6.
- **Clock hold:** 5 ms over the measured T, the physical certain-exclusion line.
- **Contention:** flag only. P_limit operands are null in all 13 H and BY-H2 regime receipts, and bytes_gates.py:326–331 produces `unavailable`, never a fail.
- `contention.unmeasured` (an exclusion) comes only from monitor coverage holes in the request (`joulewise/hazards/contention.py:765`), not from P_limit's absence.
- **Disk:** P uses no reserve. It is a measured-free-space stop on the session volume, which the doctrine allows. Its inflation by idle-admission retries (O-S3, dissent recorded) makes the stop conservative and does not change data.
- **Missing withheld file:** disclosed, not refused.
- **Session counting:** the analysis's `counting` gate (`bytes_analysis.py:939`) reads acceptance, which applies the BYTES pack's DISCLOSE override for `cell.below_minimum` (`acceptance.py:163–171`).

**Numbers dimension.** Every bar I checked carries a derivation:
- the 1 % agreement bars, set at about 60× above 10⁶ × float noise;
- G_total · P_max ≤ 0.13 mJ (1 % of 0.013 J);
- the 0.93 coverage floor (0.928, two binomial standard errors at 400 draws);
- the cell minimum of 5 (g(n) is defined only for n ≥ 5);
- the 0.25 ppm frequency margin (block-6 S-7 derivation);
- the 6-decimal drift scale;
- the clock u_j and a_j rules.

## Slot table

| Slot (§18) | Status | My evidence |
|---|---|---|
| Manifest SHA and table | FILLED | sha matches; table 0 mismatches |
| 8B-8bit revision | FILLED | generator `--check`: "verified 500 BYTES science configs" |
| 8B-8bit kept | FILLED | P0 ruling 1; H desk citation (not re-executed) |
| b / R range | FILLED | 32 / 71 recomputed |
| C4 pins | FILLED | `write_b5_identity_pins.py --bytes-observed RUNTIME-OBSERVE.txt --check` gives units 11, source ddd0001b…, consumed 55197f44…, rc 0 |
| P_limit / contention | FILLED (flag only) | all 13 regime receipts null; gate code produces unavailable |
| Clock-gate values | FILLED | six holds recomputed; boundary test passes |
| Disk footprint | FILLED | six P and P + smoke exact |
| C5 sizing | FILLED | six S/T rows exact from raw |
| Test 7 | FILLED (no pass; scale kept) | not re-executed; analysis refuses `test7_passed` anything but false or omitted (subagent c1) |
| Known-bytes stream test | PENDING, explicitly deferred | deferral sound (finding 4); reading rule should be written before the test |
| Coverage table | FILLED | 18/18 rows match the JSON. Estimator diff 76c44759 → 18582818 is confined to `neg8_inputs` reference ingress (git diff 68f5b408b..86a0185da), as §9 says |
| Estimator SHA | FILLED | matches file and six p1 registrations |
| Catalog SHA | FILLED | matches |
| B4 paths, flag, stage1-commit | FILLED | blinding.py:91–111, 172–193; release script :22–32; export withholds held-out rows and strips run_start_utc (export_runs.py:717–748); sidecar has no clock keys (checked on the BY-H2 sidecar) |

Blinding (item 5):
- `PACK_RANGE` is (0.8, 1.25) and `CONFIG_RANGE` is (0.97, 1.03), drawn uniform with `secrets.SystemRandom`.
- The fit set is exactly {1.7B, 4B, 8B}-4bit plus `neg8_reference`.
- Held-out rows go to `<root>/bytes/withheld/<pack>/<session>.runs.csv` before the CSV is published.
- `bind_session_keys` refuses a changed key digest.
- A stage-1 release refuses held-out keys. A stage-2 release requires a 40- or 64-hex commit (form only; finding 8).

## Executed

All runs used `/opt/homebrew/bin/python3.13 -B`, `PYTHONDONTWRITEBYTECODE=1`, `JW_B5_SYNTHETIC_ONLY=1` and `TMPDIR=/private/tmp/reggate-opus/tmp`.

- `shasum -a 256 joulewise/bytes_analysis.py configs/b6/flag_catalog_b6.json configs/bytes/bytes_manifest.json` gives 18582818…, 01767fe4…, 76452108….
- `resize.py` (sizing re-derivation) prints "timed runs 168 {'H': 95, 'BY-H2': 73}"; "retained != 2*raw: 0"; and the six rows quoted above, all equal.
- `-m unittest tests.test_bytes_agreement.AgreementTests.{test_bytes_world, test_withheld_campaign_missing_files_and_uncollected_pass}`: "Ran 2 tests in 84.649s OK".
  - bytes: compared 314837, under the bar 7296, **above the bar 0**.
  - withheld: compared 219549, under the bar 4842, **above the bar 0**.
- `… AgreementTests.{test_time_world, test_resident_world, test_defects_campaign, test_minimum_campaign_one_pass_refused}`: "Ran 4 tests in 167.603s OK". All four campaigns are **0 above the bar**:

  | Campaign | Compared | Under the bar | Above the bar |
  |---|---|---|---|
  | time | 262385 | 5426 | 0 |
  | resident | 262385 | 5443 | 0 |
  | defects | 269281 | 5652 | 0 |
  | minimum | 254966 | 5903 | 0 |

- Coverage-table comparison script: "rows 18 mismatch 0; min HC3 plain 0.9475".
- `scripts/write_b5_identity_pins.py --bytes-observed …/RUNTIME-OBSERVE.txt --check`: rc 0, units 11.
- `configs/campaigns/bytes_v1/generate_configs.py --check`: "verified 500 BYTES science configs (10 models x 50)".
- `scripts/bytes_plan_trees.py --check` (subagent): "verified 12 BYTES draft registrations and 12 fixed pass trees".
- Clock-hold boundary test through `precheck.thresholds_for` and `clock.measured_rate_bound`: s1 and s5 give True / False / False.
- Subagent text-against-code probes c1, c3, c4, c56, c6b, c9 and c10 (in `/private/tmp/reggate-opus/agent-text/s/`). Every probe matched: cell rule, B, scale and test7 validation, u and v with r_max > Δt, the NEG-8 allowance (A = 0.6966841335183247 for analysis, twin and independent recomputation), the flagged-inclusive sets, the t values and family sizes, comparer bars no looser than §12, and plan-tree fields.
- `gh pr checks 579`: test shards pending (finding 3).
- `git status` was clean throughout.

**Fence disclosures:**
- I ran one command as `cd /private/tmp/reggate-opus && python3.13 -B resize.py` (a cd into scratch inside a compound command).
- The subagent ran one command with `cd <worktree>;` before `--check`.
- Neither wrote anything outside scratch.
- I ran no launchctl, sudo, pmset, powermetrics or caffeinate, no live arm or runner, and loaded no model. The raw night-bytes trees were only read (stat and JSON).
