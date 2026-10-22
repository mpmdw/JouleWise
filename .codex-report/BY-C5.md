## PROGRESS

- Slice 5: director replay table imported from replay.json: 0 refusals / 10 available (nine block-6 + H), r2-alpha unavailable; largest pass refuses 0. No real session trees read.
- P PER SUB-PACK now has readable integer terms and per-model allowances; exact fractions stay in director C5.json. R6 carries real P values. Current df available 44,779,048 KiB (~42.7 GiB), above 10 GiB stop gate, below every P.
- Done earlier: exact raw allocated-byte rates; P and native q/headroom; synthetic real DriverLane/planner/disk hazard P-1/P proof; 17 C5 tests including replay.
- Passed this slice: alpha/beta/gamma production regression all 6 subtests (167.493 s), confirming /tmp aliasing only; machine_test 29; lane_adapters 21; round2_review_fixes 8; s3_cold_fixes 6; ColdPassTests 9; ScreenInputsTests 2. hazards clock: 33 pass, one environmental kern.bootsessionuuid probe failure. Exact commands in TESTS RUN.
- Full cold_pass_fixes timed out at 100 s; FullRoundTests still owed separately. capture_screen_reachability timed out at 75 s (recorded below); ChainReachabilityTests still owed separately. b6_loop separately passed 55 tests (23.277 s).
- Currently running: desk_resume_finalize session 97218; capture_screen_reachability.PolicyReadTests + CaptureDispositionTests session 64707. Earlier batches 85156 and 49000 are finished; they stopped on their first timed-out module and did not run later modules. loop_round_desk remains entirely unrun.
- Next: collect running results; run any remaining importer modules/classes split small; extend real writer equality to all twelve real-H terms; final report audit (including clause-map site lines and any NOT PINNED gaps). No new implementation edits in slice 5.
- Open: hazards arm environmental process-group census failures (25 tests, 17 assertions fail; sysmond/pgrep unavailable), clock bootsessionuuid failure; BY-H2 native raw_allocated_bytes producer; known H native-export integration expectation; hazards import-graph GO/NULL failure; CI/director final review. No Git writes attempted.

## SUMMARY

Stopped-session gates fix is already present and reproduced before/after.
C5 now replaces the 150 GiB reserve with H-DISK-RULING exact rational P.
Rates derive from one raw bundle's allocated byte receipts, without altering retained_bytes.
All twelve pass packs print both bases, per-model counts and allowances, WAIT, fixed, c and P.
Missing raw receipts flag disk.raw_bytes_missing; no available rates makes disk unavailable.
All 17 bytes_gates tests pass; H rates agree with disk_h at the required 1e-6 relative bar.
Pack encoding and synthetic end-to-end hazard verification are implemented; byte-only replay CLI is tested on synthetic 9+1 receipts.
Only authorized source/test/report files changed; no hardware operation or Git write ran.
Director real replay: 0 refusals of 10 available sessions, 1 unavailable row; largest pass also refuses 0. CI remains director-owned.

## GATES FIX

Baseline 8386706f2 preserves the author of 66b330b15, as directed. Evidence directory: `/tmp/jwtmp-byc5-evidence.zze_7sty` (temporary, not an enduring source). Both invocations use `/opt/homebrew/bin/python3.13 -B`, identical data-branch MEASUREMENTS and native export, and the repository kit plan. The old script was extracted with `git show bda481d5a:scripts/bytes_gates.py`.

- Before: exit 1, stderr `bytes_gates: [<class 'decimal.ConversionSyntax'>]`, no output JSON.
- After (8386706f2): exit 2, empty stderr, output JSON written. Exit 2 reflects failing computed lines on the stopped session; it is not a program fault.
- Sole production caller: scripts/bytes_h_session.py desk maps 1 to unavailable, 2 to fail, 0 to pass, other codes to program_fault, and its CLI returns gates_exit unchanged. Tests invoke bytes_gates directly; scripts/bytes_mac_kit.py only documents its command. Census: `rg -n 'bytes_gates|gates_exit' --glob '!*.json' --glob '!*.csv' --glob '!*.md' --glob '!*.html' .`.

## P PER SUB-PACK

Slice 2 real-H command (extracted data files only in TMPDIR):

`/opt/homebrew/bin/python3.13 -B scripts/bytes_gates.py --runs /tmp/jwtmp-byc5-disk-03yxkpvg/bytes-h-20261021T185555335572Z-calibration.runs.csv --measurements /tmp/jwtmp-byc5-disk-03yxkpvg/MEASUREMENTS.raw.json --disk-evidence /tmp/jwtmp-byc5-disk-03yxkpvg/disk_h.json --out /tmp/jwtmp-byc5-disk-03yxkpvg/C5.json`

Exit 2 from stopped completeness gates; empty stderr; no ConversionSyntax. Rates use exact fractions of raw allocated bytes over measured decimal seconds. Agreement bar is 1e-6 relative per director ruling 1: stream 1805538.5168827055 vs disk_h 1805538.5168827053 B/s (relative difference 2.220446049250313e-16), wall 1285759.0452694688 vs 1285759.0452694688 B/s (relative difference 0). Optional --disk-evidence discloses BY-0 c_implied_alloc alongside c=2, hashes the additional source, and changes no P or refusal. With no evidence file, measured_c=null explicitly leaves the measurement unavailable.

All twelve exact fraction records, rates, allowances and source hashes remain in `/Users/edr/night-archive/forward-20261021/BY-C5/replay/C5.json`; the bulky JSON dump is omitted here. All byte cells below are integers. Both p variants have identical terms. c=2 is operative; measured c=0.8020750916018277 is disclosure only.

| pack | members n | stream basis B_s | wall basis B_w | B (winner) | WAIT | fixed | c | measured c | P | q | headroom | encoded requirement == P |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| bytes-s1-p1 | 125 | 21,883,930,645 | 21,697,490,999 | 21,883,930,645 (stream) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 71,034,160,574 | 116,714,296 | 27,266,299,574 | yes |
| bytes-s1-p2 | 125 | 21,883,930,645 | 21,697,490,999 | 21,883,930,645 (stream) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 71,034,160,574 | 116,714,296 | 27,266,299,574 | yes |
| bytes-s2-p1 | 125 | 22,841,465,166 | 22,967,763,886 | 22,967,763,886 (wall) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 73,201,827,056 | 122,494,740 | 27,266,299,556 | yes |
| bytes-s2-p2 | 125 | 22,841,465,166 | 22,967,763,886 | 22,967,763,886 (wall) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 73,201,827,056 | 122,494,740 | 27,266,299,556 | yes |
| bytes-s3-p1 | 125 | 24,053,464,961 | 24,709,054,674 | 24,709,054,674 (wall) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 76,684,408,632 | 131,781,624 | 27,266,299,632 | yes |
| bytes-s3-p2 | 125 | 24,053,464,961 | 24,709,054,674 | 24,709,054,674 (wall) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 76,684,408,632 | 131,781,624 | 27,266,299,632 | yes |
| bytes-s4-p1 | 125 | 27,547,300,445 | 26,855,538,139 | 27,547,300,445 (stream) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 82,360,900,174 | 146,918,935 | 27,266,299,549 | yes |
| bytes-s4-p2 | 125 | 27,547,300,445 | 26,855,538,139 | 27,547,300,445 (stream) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 82,360,900,174 | 146,918,935 | 27,266,299,549 | yes |
| bytes-s5-p1 | 75 | 22,901,363,715 | 21,700,998,244 | 22,901,363,715 (stream) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 73,069,026,714 | 203,567,677 | 27,266,299,389 | yes |
| bytes-s5-p2 | 75 | 22,901,363,715 | 21,700,998,244 | 22,901,363,715 (stream) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 73,069,026,714 | 203,567,677 | 27,266,299,389 | yes |
| bytes-s6-p1 | 75 | 14,585,071,383 | 16,382,541,368 | 16,382,541,368 (wall) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 60,031,382,020 | 145,622,589 | 27,266,299,495 | yes |
| bytes-s6-p2 | 75 | 14,585,071,383 | 16,382,541,368 | 16,382,541,368 (wall) | 12,999,877,322 | 1,266,544,640 | 2 | 0.8020750916018277 | 60,031,382,020 | 145,622,589 | 27,266,299,495 | yes |

Per-model allowances below are seconds, displayed to nine decimals for readability; arithmetic uses the exact fractions in C5.json. The count applies to each p variant. Global r_s=1805538.5168827055 B/s and r_w=1285759.0452694688 B/s apply to every pack.

| pack family | model | count | stream allowance s | member-wall allowance s |
|---|---|---:|---:|---:|
| bytes-s1-p1/p2 | qwen3-1p7b | 50 | 95.936319909 | 133.421011685 |
| bytes-s1-p1/p2 | qwen3-4b | 50 | 99.592648098 | 138.716749210 |
| bytes-s1-p1/p2 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s2-p1/p2 | qwen3-30b-a3b | 50 | 100.460336724 | 145.758197295 |
| bytes-s2-p1/p2 | qwen3-8b | 50 | 105.675267598 | 146.138676197 |
| bytes-s2-p1/p2 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s3-p1/p2 | qwen3-14b | 50 | 115.960714413 | 158.620031792 |
| bytes-s3-p1/p2 | qwen3-next-80b | 50 | 103.600245103 | 160.362644347 |
| bytes-s3-p1/p2 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s4-p1/p2 | qwen3-32b | 50 | 147.706179398 | 199.223982318 |
| bytes-s4-p1/p2 | qwen3-8b-8bit | 50 | 110.556092239 | 153.147274265 |
| bytes-s4-p1/p2 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s5-p1/p2 | llama-70b | 50 | 206.799102208 | 272.192316153 |
| bytes-s5-p1/p2 | reference | 25 | 93.759871868 | 130.734032387 |
| bytes-s6-p1/p2 | qwen35-122b | 50 | 114.679302444 | 189.463644769 |
| bytes-s6-p1/p2 | reference | 25 | 93.759871868 | 130.734032387 |

The all-twelve encoded requirement column uses actual plan_inputs.encode_disk_budget with real stage_plan counts, checked in slice 4. Real plan.write_window_plan and disk-hazard equality are exercised by the production-shaped synthetic E2E test below; extending that real-writer proof to every real-H term remains a useful final check.

## PACK ENCODING

Slice 3: plan_inputs.build reads disk_derivation from the selected sizing_b5.json pack row (the same source as its time allowances), for bytes-s* only. It uses plan.read_plan_tree and b5_chain.stage_plan to obtain the native member-plus-spares count, then divmod(c*B,3*n); headroom=remainder+c*WAIT+fixed. Integer fields are checked for reconstruction of P, c=2 and WAIT duration=7200. P values remain future BY-SLOTS registration inputs; no generated registration is changed.

DriverLane removes the diagnostic disk_budget property before the closed-schema smoke/planner interface and retains it at session metadata disk_budget and notes. A missing or malformed P records disk.budget_missing in staging/disk-budget.json and returns LaneMissing, not Refused; no disk comparison runs for the absent record. The writer requires positive bytes_per_member, so a zero-budget plan would not parse. Existing alpha/beta/gamma inputs remain unchanged.

The production-shaped synthetic test supplies the omitted launch declaration in its TMPDIR checkout only. Real draft BYTES trees currently have arm_attachments={}, as scripts/bytes_plan_trees.py intentionally generates; their launch authority remains a BY-SLOTS prerequisite.

## REPLAY PROGRAM

Implemented as `scripts/bytes_gates.py replay --c5 <C5.json> --measurements <MEASUREMENTS.raw.json> --out <replay.json> <session-root>...`. It prints one JSON row per session and a final refusal_count/session_count, unavailable_count and largest-pass refusal count. JSON includes an empty refusal_census. Exit codes: 2 any measured free<P, 1 unavailable rows with no refusal, 0 all available rows pass. This desk subcommand never arms a session.

Inputs: B6 free-at-arm is the minimum valid target on the session st_dev (ignoring measurement/target errors and foreign devices), free-at-desk is compression-summary.free_bytes_before, and B is summed compression.jsonl compress/runs size. These logical compressed-file sizes are a lower bound on one raw copy (implied c an upper bound), as BY-0 documents. H uses desk.json disk free values and the sum of timed augmented raw_allocated_bytes; never-ran null receipts enter no sum. WAIT and fixed are the committed terms already disclosed in C5 disk:kit, reused without adding margins. Each row discloses the byte basis, B, WAIT, fixed, c=2, P, both free readings, D, measured c, refusal, largest pass P and its refusal. Missing/malformed inputs remain flagged rows, never dropped or refused.

Synthetic tests exercise nine B6 plus one H with zero refusals, exact P and P-1 boundaries, foreign-device/error filtering, runs-only/event filtering, missing inputs and the executable CLI. All 17 C5 tests pass. Synthetic evidence is separate from the director real replay recorded below.

Exact director command (do not execute in this worker; C5_JSON is the output generated from augmented H receipts; REPLAY_JSON is the director-chosen output):

```sh
/opt/homebrew/bin/python3.13 -B scripts/bytes_gates.py replay --c5 "$C5_JSON" --measurements /Users/edr/night-archive/forward-20261021/BY-C5/MEASUREMENTS.raw.json --out "$REPLAY_JSON" /Users/edr/night-b6/sessions/r*-alpha /Users/edr/night-b6/sessions/r*-beta /Users/edr/night-b6/sessions/r*-gamma /Users/edr/night-bytes/h-20261021T185555Z
```

The ending alpha/beta/gamma globs exclude -smoke-0 directories. Director owns real replay and committed table; worker accessed no prohibited session tree.

Director real replay at d49f11fb3: source `/Users/edr/night-archive/forward-20261021/BY-C5/replay/replay.json` (byte counts only). L = compression runs-root logical-size sum (one-copy lower bound); A = H timed raw_allocated_bytes sum (allocated). Displayed measured c is rounded to nine decimals; JSON preserves full precision. Largest-pass P is 82,360,900,174 bytes (bytes-s4-p1) for every row.

| session | B basis | B bytes | WAIT | fixed | c | P | free at arm | free at desk start | D | measured c | refused | largest-pass P refused |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| r1-alpha | L | 20,055,016,087 | 12,999,877,322 | 1,266,544,640 | 2 | 67,376,331,458 | 174,331,416,576 | 162,829,508,608 | 11,501,907,968 | 0.573517763 | no | no |
| r2-alpha | L | unavailable | 12,999,877,322 | 1,266,544,640 | 2 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| r3-alpha | L | 20,047,779,056 | 12,999,877,322 | 1,266,544,640 | 2 | 67,361,857,396 | 151,146,446,848 | 140,108,296,192 | 11,038,150,656 | 0.550592194 | no | no |
| r4-alpha | L | 20,108,842,246 | 12,999,877,322 | 1,266,544,640 | 2 | 67,483,983,776 | 133,102,612,480 | 113,618,456,576 | 19,484,155,904 | 0.968934744 | no | no |
| r1-beta | L | 20,447,426,571 | 12,999,877,322 | 1,266,544,640 | 2 | 68,161,152,426 | 169,934,139,392 | 158,655,823,872 | 11,278,315,520 | 0.551576282 | no | no |
| r2-beta | L | 20,546,600,800 | 12,999,877,322 | 1,266,544,640 | 2 | 68,359,500,884 | 162,810,486,784 | 152,628,854,784 | 10,181,632,000 | 0.495538513 | no | no |
| r3-beta | L | 20,493,154,726 | 12,999,877,322 | 1,266,544,640 | 2 | 68,252,608,736 | 147,161,776,128 | 124,931,256,320 | 22,230,519,808 | 1.084777825 | no | no |
| r1-gamma | L | 17,299,704,879 | 12,999,877,322 | 1,266,544,640 | 2 | 61,865,709,042 | 166,263,980,032 | 156,454,031,360 | 9,809,948,672 | 0.567058730 | no | no |
| r2-gamma | L | 17,391,012,615 | 12,999,877,322 | 1,266,544,640 | 2 | 62,048,324,514 | 159,616,585,728 | 150,028,029,952 | 9,588,555,776 | 0.551351206 | no | no |
| r3-gamma | L | 17,307,433,044 | 12,999,877,322 | 1,266,544,640 | 2 | 61,881,165,372 | 154,232,840,192 | 144,652,926,976 | 9,579,913,216 | 0.553514388 | no | no |
| h-20261021T185555Z | A | 16,749,187,072 | 12,999,877,322 | 1,266,544,640 | 2 | 60,764,673,428 | 108,612,526,080 | 95,109,353,472 | 13,503,172,608 | 0.806198686 | no | no |

Refusal count: 0 of 10 available sessions (9 block-6 + H); 1 unavailable (r2-alpha, inputs absent).

Director C5 command: `/opt/homebrew/bin/python3.13 -B scripts/bytes_gates.py --runs <data-branch runs.csv> --measurements /Users/edr/night-archive/forward-20261021/BY-C5/MEASUREMENTS.raw.json --disk-evidence <data-branch disk_h.json> --out /Users/edr/night-archive/forward-20261021/BY-C5/replay/C5.json` — exit 2 (stopped-session completeness), empty stderr.

Director replay command is the exact template above with C5_JSON=/Users/edr/night-archive/forward-20261021/BY-C5/replay/C5.json and REPLAY_JSON=/Users/edr/night-archive/forward-20261021/BY-C5/replay/replay.json — exit 1 for the unavailable r2-alpha row. All ten available rows pass; largest-pass refusal count is also 0. Worker read these replay outputs only, never the real session trees.

## END-TO-END

`tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard` passes (1 test, 16.637 s, exit 0). A synthetic bytes-s1-p1 registration sizing row uses B=1000001, WAIT=7200, fixed=19, hence P=2014421 bytes. Only the temporary tree is decorated with the existing fourteen launch bindings; no draft authority is asserted for committed trees. DriverLane.prepare_session/build/launch feeds the real plan.write_window_plan. driver.disk_targets groups its real target copies on one synthetic device; disk.measure stubs statvfs with f_frsize=1 to express both exact byte boundaries. disk.judge reports required_bytes exactly P, REFUSE at P-1 and PASS at P. This is synthetic evidence, not live hardware validation.

## SEALED INVENTORY

Checked the sealed inventory programmatically (all keys of its files mapping):

```python
paths = sorted(json.loads(Path("configs/campaigns/v5_claim_25g83/sealed_inventory.json").read_text())["files"])
subprocess.run(["git", "diff", "--name-only", "bda481d5a", "HEAD", "--", *paths], check=True)
subprocess.run(["git", "diff", "--name-only", "HEAD", "--", *paths], check=True)
```

Both commands exited 0 with empty stdout. No block-five changes.

## TESTS RUN

Slice 5: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_arm` — exit 1, 25 tests, 72.295 s, 17 failure assertions (including five subtests), no skips. Environmental process-group census: `instrument REFUSE: the capture's process group was not proven gone: census_exit_3: sysmon request failed with error: sysmond service not found; pgrep: Cannot get process list`. Later dwell/final/census expectations consequently stop early at instrument. Failures: battery-current-during-dwell, agent-during-dwell, charging-during-dwell, clock-step, contending-daemon, frequency-word-change, clean-census-at-go, smc-cross-check, network-time-output, quiet-float-go, record-only-collectors, unmeasured-arm-only (battery/thermal/disk/clock/contention subtests), no-smc-fallback. No hazard code was changed; this is the process-group environmental lane named in the brief and is not chased. This also offers a likely explanation for the earlier GO/NULL import-graph failure, but that exact earlier run did not print its reasons.


Slice 5: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop` — exit 0, 55 tests, 23.277 s, no skips.


Slice 5: tests.b6.test_capture_screen_reachability bounded run timed out after 75 s; split by class next slice. No result claimed.


Slice 5 production regression rerun: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_each_production_pack_uses_b6_screen_and_no_spares` — exit 0, 1 test / all 6 subtests pass, 167.493 s, no skips. Alpha/beta/gamma each pass for pending and registered states, including their unchanged budget checks and courier reader checks. This confirms the slice-3 failures were environmental macOS /tmp -> /private/tmp aliasing.

- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_s3_cold_fixes` — exit 0, 6 tests, 0.276 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_cold_pass_fixes` — bounded subprocess timeout at 100 s; no result claimed. Follow-up class below passes; FullRoundTests must run separately next slice.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_cold_pass_fixes.ColdPassTests` — exit 0, 9 tests, 1.007 s, no skips.
- Round-two module was also repeated inadvertently while dispatching the remaining checks: exit 0, 8 tests, 0.057 s. Its earlier passing result already sufficed.


Slice 5: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_b6_plan_render.ScreenInputsTests` — exit 0, 2 tests, 0.002 s, no skips.


Slice 5: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_machine_test` — exit 0, 29 tests, 18.182 s, no skips.

Slice 5 sealed-inventory commands in SEALED INVENTORY repeated: both exit 0, empty stdout; `git diff --check` exit 0.


Slice 5 initial checks (each module has its own fresh TMPDIR):

- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_lane_adapters` — exit 0, 21 tests, 1.704 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_round2_review_fixes` — exit 0, 8 tests, 0.634 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_clock` — exit 1, 34 tests, 0.596 s, 1 failure, no skips. LiveReadOnlyTests.test_real_anchor_frequency_and_boot_read_without_privileges fails with `OSError: kern.bootsessionuuid probe failed: exit 1`; other 33 tests pass. Environmental host probe failure in unchanged hazard code; not chased.


Slice 4 commands (all from repository root):

- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates` — exit 0, 17 tests, 7.238 s initially; 5.114 s after adding replay rate disclosure. No skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_bytes_packs` — exit 0, 9 tests, 9.515 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_catalog` — exit 0, 4 tests, 0.673 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.flags.test_flags_catalog` — exit 0, 6 tests, 0.127 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session.DiskRulingTests tests.test_bytes_h_session.ReceiptMathTests` — exit 0, 7 tests from one module, 0.007 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_plan_inputs` — exit 0, 6 tests, 0.009 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_session_wrapper` — exit 0, 6 tests, 0.492 s, no skips.
- An initial combined plan_inputs/session_wrapper invocation passed (12 tests, 0.570 s, exit 0), but shared a TMPDIR between modules. Both were rerun above with separate TMPDIRs to follow the local route.
- All-twelve q/headroom report derivation invoked actual plan_inputs.encode_disk_budget on the already printed H terms. All integer reconstruction assertions pass. No real session tree read.
- Sealed-inventory commands shown above repeated against working tree from bda481d5a and HEAD: exit 0, stdout empty. `git diff --check`: exit 0. No whole suite and no hardware/installer operation.


Slice 3 exact commands (each fresh module TMPDIR, synthetic-only):

- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_plan_inputs` — exit 0, 6 tests, 0.012 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_session_wrapper` — exit 0, 6 tests, 0.431 s, no skips.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_bytes_pack_p_through_real_planner_and_disk_hazard` — exit 0, 1 test, 16.637 s. Earlier attempts failed first on extra disk_budget key (fixed by keeping disclosure in DriverLane metadata), then on the intentionally absent draft launch declaration (synthetic fixture now supplies it in TMPDIR only).
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_b6_plan_render.ProductionPlanRenderTests.test_each_production_pack_uses_b6_screen_and_no_spares` — exit 1, 1 test, 6 failing subtests, 131.197 s. All alpha/beta/gamma budget assertions passed for both registration states; each failed the unchanged check_readers line 142 courier path assertion because actual resolves /private/tmp while expected retains /tmp. Environmental path-alias failure per local route; not chased.
- `git diff --check` — exit 0. Repeated sealed-inventory byte-path diff commands from bda481d5a and HEAD to working tree: both exit 0, stdout empty.

Final slice-2 C5 module run: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates` — exit 0, 14 tests, 4.082 s, no skips. Includes measured-c disclosure invariance. H was rerun with --disk-evidence; exit 2, empty stderr, every P unchanged and measured_c=0.8020750916018277 beside c=2.


Slice 2 additional checks:

- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_import_graph` — exit 1; 6 tests, 5.917 s, one failure: test_a_complete_arm_and_monitor_run_load_no_retired_module expected GO, got NULL. Five static graph tests pass. The failing test imports unchanged hazards/arm and its Rig, not bytes_gates; no hazard implementation was edited. Cause not established; report to director rather than alter hardware paths.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_refusal_allowlist` — exit 0; 23 tests in 69.967 s; OK, one skip.
- `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session` — still running at this checkpoint (one failure marker observed; details pending); tool session 71288. Do not rerun the whole module in the next short slice: select individual classes/tests.
- `git diff --check` — exit 0. Sealed paths diff from both bda481d5a and HEAD — empty, exit 0 (working-tree comparison includes this slice).


Slice 2: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates` — exit 0, 13 tests, 3.990 s initially and 8.400 s after adding the cross-basis counterexample, no skips. Tests derive the integer P boundary exactly; unprinted continuous values use the director's 1e-6 relative/absolute bar. No whole suite.


`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byc5.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates`

Exit 0; 11 tests in 1.132 seconds; OK, no skips or environmental failures. This is baseline verification; no implementation is claimed. Whole suite excluded by the task.

## R6 DRAFT

For each BYTES pass session the sole disk refusal is measured session-volume free bytes, statvfs f_bavail multiplied by f_frsize with purgeable bytes excluded, below P. P = 2(B + WAIT) + fixed. B is the larger of ceil(r_s times the sum of model count times that model’s stream allowance) and ceil(r_w times the sum of model count times that model’s member-wall allowance). Rates are maxima over timed H members of one raw bundle tree’s inode-deduplicated POSIX st_blocks times 512 divided by stream seconds or member-wall seconds respectively. Each model uses its own measured allowances including the measured request max/min margin; the stream allowance includes mean request time plus maximum stream-minus-request time. Each full basis rounds up once in exact rational arithmetic. WAIT=ceil(r_s times 7200 seconds), fixed is the committed fixed-artifact allocation, and two copies count raw plus the partitioned rsync backups; the harvest APFS clone adds no copy. No reserve or further margin is added. All terms, P, free bytes and the measured whole-window implied copy count are disclosed; missing inputs are flags. The native three-target budget encodes P exactly with q=floor(2B/(3n)) and headroom=(2B-3nq)+2WAIT+fixed, where n is the writer’s actual members-plus-spares count; disk.budget_encoded_from_p names that encoding. H gives r_s=1,805,538.5168827055 B/s, r_w=1,285,759.0452694688 B/s, WAIT=12,999,877,322 B, and fixed=1,266,544,640 B. With c=2, P for each p1/p2 session is s1=71,034,160,574 B; s2=73,201,827,056 B; s3=76,684,408,632 B; s4=82,360,900,174 B; s5=73,069,026,714 B; s6=60,031,382,020 B. Each B, winning basis, allowance, q and headroom is in the tables above. BY-SLOTS fills these pack-specific values; the stopped-session sizing remains PROVISIONAL.

Lead disk-state fact: the director observed about 67 GiB (~72 GB) free at 07:5x UTC, at which s3/s4 would physically refuse while s1/s2/s5 were within a few GB. This slice re-ran `df -k /Users/edr`: `/dev/disk3s5 971350180 902869204 44779048 96% ... /System/Volumes/Data`. Available=44,779,048 KiB=45,853,745,152 B (~42.7 GiB), above the 10 GiB stop gate but below all six P values, so every sub-pack would physically refuse at this reading. These are correct free<P refusals, not a defect; free space is time-dependent.

## CI

Director creates draft PR and reads CI under the local route. No PR number supplied yet.

## DECISIONS I MADE

Slice 4: replay B is the measured one-copy sum, as the director specifies, rather than pass allowances. The same supplied C5 H stream rate determines WAIT and the same C5 committed fixed-artifact bytes supplies fixed across replay rows, without a new reserve or margin. B6 compressed-file logical bytes retain BY-0's lower-bound label; H uses augmented allocated raw bytes. Desk replay results do not add an arm refusal site; scripts/bytes_gates.py already has the registry not_scanned=desk disposition. No new imports, scan entries or harvested flag codes are needed. Missing/malformed row inputs are caught and flagged, and all rows remain in session_count with separate unavailable_count.


Slice 3: registered disk terms live in sizing_b5.json packs[label].disk_derivation, next to that pack’s own time allowances; BYTES draft registration files remain unchanged. The sealed writer cannot accept diagnostic input keys or zero bytes_per_member. DriverLane keeps disk_budget in session metadata, and an absent P yields a durable disk.budget_missing diagnostic plus LaneMissing before planning, never Refused. The draft pass tree’s deliberately absent launch declaration is supplied only by the synthetic E2E fixture; actual launch readiness belongs to BY-SLOTS. Flags here are preparation metadata, not harvested member flags, so no flag-catalog mutation is required for this step.

Director ruling 1: per-run raw_allocated_bytes is the only disk-rate byte source (allocated st_blocks*512, raw-only tree, inode-deduplicated). Missing raw byte receipts enter no rate, are counted in disk.raw_bytes_missing; no rate makes disk unavailable. Never halve retained_bytes. Rates compare at 1e-6 relative; derived integer bytes compare exactly. BY-H2 owns native producer support. Synthetic never-ran receipts carry raw_allocated_bytes=null.


Applied director precedence: H ruling and committed disk_terms win over the paraphrase; B is the maximum of two summed bases, each rounded once using exact rational arithmetic. c=2; measured c is disclosure. WAIT uses stream rate for registered 7200 seconds; fixed comes unchanged from disk.fixed_retained_bytes. Local route overrides cloud setup, commits and PR operations.

## Clause map

The production/test map below records the governing numerical clauses. Counterfactuals identify one-site changes the named assertions detect; they have not been executed in this worker and remain for executing review.

| clause | production site | biting assertion | counterfactual |
|---|---|---|---|
| H-DISK-RULING.md:16, free below P only | joulewise/hazards/disk.py, existing judge (unchanged); plan_inputs.py:164 native encoding | tests/b6/test_b6_plan_render.py:196 test_bytes_pack_p_through_real_planner_and_disk_hazard | Add one byte to encoded headroom: exact P must pass assertion fails. |
| H-DISK-RULING.md:18, P=c(B+WAIT)+fixed, c=2 | scripts/bytes_gates.py:103 | tests/test_bytes_gates.py:298 test_disk_terms_round_whole_bases_once_and_ignore_retained_copies | Change outer factor 2 to 3: expected 4811 fails. |
| H-DISK-RULING.md:19, maximum of summed bases | scripts/bytes_gates.py:92 | tests/test_bytes_gates.py:298 crossed B assertion | Sum per-model maxima: crossed B becomes 18 instead of 10. |
| H-DISK-RULING.md:22, registered 7200-second WAIT | scripts/bytes_gates.py:95 | tests/test_bytes_gates.py:298 expected P=4811 | Change WAIT constant to 7201: ceil term changes and P fails. |
| H-DISK-RULING.md:23, committed fixed | scripts/bytes_gates.py:103 | tests/test_bytes_gates.py:298 expected P=4811 | Omit fixed_bytes: expected P fails by 7 bytes. |
| H-DISK-RULING.md:27, no reserve | scripts/bytes_gates.py:103 | tests/test_bytes_gates.py:298 expected P=4811 | Add any reserve to the computed P: expected integer P assertion fails. |
| H-DISK-RULING.md:39, measured c disclosure | scripts/bytes_gates.py:101 | tests/test_bytes_gates.py:277 test_measured_copy_factor_is_disclosure_only | Use measured_c instead of 2: unchanged-P assertion fails. |
| Director ruling 1, raw-only byte source | scripts/bytes_gates.py calculate disk rates | tests/test_bytes_gates.py:298 retained_bytes multiplied by 3, derivation unchanged | Derive rates from retained_bytes: invariance assertion fails. |
| Director ruling 1, missing raw flag and unavailable | scripts/bytes_gates.py calculate disk missing-rate path | tests/test_bytes_gates.py:288 test_disk_missing_raw_bytes_is_unavailable_and_flagged | Return fail rather than unavailable: disk status set assertion fails. |
| Addendum 1, native budget exactly P and named flag | joulewise/b6/plan_inputs.py:164; driver_lane.py:91 | tests/b6/test_b6_plan_render.py:196 real writer requirement and metadata flag | Increment q or omit metadata disk_budget: exact required_bytes or metadata assertion fails. |
| Addendum 1, alpha/beta/gamma unchanged | joulewise/b6/plan_inputs.py:124 BYTES-only branch | tests/b6/test_plan_inputs.py:43 test_replication_budgets_keep_existing_path | Apply encoding unconditionally: disk_budget absence assertion fails. |
| Brief rule 8, missing replay row retained as flag | scripts/bytes_gates.py:383 replay_disk | tests/test_bytes_gates.py:138 test_missing_inputs_are_listed_never_refused | Drop missing row: unavailable/session-count assertion fails. |

## OPEN ISSUES

BY-H2 must add raw_allocated_bytes to scripts/bytes_h_session.py measurements(): POSIX st_blocks*512 of that run's raw bundle tree only (one copy, runs-parent/<stage dir>/<run_id>, inode-deduplicated); null for members that never ran. retained_bytes keeps raw plus archive allocations and must not be halved.

The production reader path-alias regression is resolved: all six subtests pass under /private/tmp. No production fix was necessary.

The native producer lacks raw_allocated_bytes, so tests.test_bytes_h_session.test_fully_observed_native_export_extracts_and_clears_c5 currently expects pass where the new contract requires unavailable. BY-H2 producer support must restore that integration; its file and test are outside this write scope.

Remaining: importer regressions and final report audit. Planner/hazard synthetic boundary proof, replay program/tests and R6 draft are done. Real replay is recorded above; CI remains director-owned. Local branch by-c5; intake HEAD d49f11fb3; intended destination lane/2026-10-22-bytes-c5-gates. Proposed slice commit: BY-C5 slice 5: real replay tables, readable P terms, R6 numbers and importer regression evidence.

## NEEDS_RULING

none; director ruling 1 resolved the byte source.
