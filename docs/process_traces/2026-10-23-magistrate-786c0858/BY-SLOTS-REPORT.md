# BY-SLOTS-DRAFT — H + BY-H2 pass-1 sizing

Core work implemented, uncommitted. Acceptance is blocked only by the out-of-scope legacy whole-file sizing-copy assertion in `tests/b6/test_plan_inputs.py:31-33`. That file was not changed. HEAD and upstream remain `1c458d71d8a048e24b6c3a6b402fe3c34d9f57c3`; branch `work/2026-10-23-by-slots-draft`. Initial tree was clean. All new scratch artifacts are under `.scratch-SLOTS/by-slots/`.

## Current rows

Seconds are rounded only for display; byte integers are exact. Each name below abbreviates `bytes-sN-p1`. The JSON retains exact rational S, rates, means, margins and disk allowances, plus every input identity/hash. Each row is at `/packs/bytes-sN-p1` in the real sizing document.

| Pack | S (s) | T_stream_max_s | B_s | B_w | B | WAIT | fixed | P | n | q | headroom | smoke share | P + smoke |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bytes-s1-p1 | 19217.679471871 | 96.390694042 | 30,319,753,844 | 21,747,443,215 | 30,319,753,844 | 18,010,999,755 | 4,046,531,103 | 100,708,038,301 | 125 | 161,705,353 | 40,068,530,926 | 1,940,464,247 | 102,648,502,548 |
| bytes-s2-p1 | 20205.635101732 | 102.247239625 | 31,646,393,595 | 23,017,716,103 | 31,646,393,595 | 18,010,999,755 | 4,046,531,103 | 103,361,317,803 | 125 | 168,780,765 | 40,068,530,928 | 2,025,369,191 | 105,386,686,994 |
| bytes-s3-p1 | 21639.346512954 | 112.229906125 | 33,327,461,374 | 24,861,123,518 | 33,327,461,374 | 18,010,999,755 | 4,046,531,103 | 106,723,453,361 | 125 | 177,746,460 | 40,068,530,861 | 2,132,957,528 | 108,856,410,889 |
| bytes-s4-p1 | 23229.354256286 | 142.944862875 | 38,166,208,818 | 26,905,490,356 | 38,166,208,818 | 18,010,999,755 | 4,046,531,103 | 116,400,948,249 | 125 | 203,553,113 | 40,068,530,874 | 2,442,637,365 | 118,843,585,614 |
| bytes-s5-p1 | 19051.636769862 | 201.498298959 | 31,729,055,015 | 21,942,279,904 | 31,729,055,015 | 18,010,999,755 | 4,046,531,103 | 103,526,640,643 | 75 | 282,036,044 | 40,068,530,743 | 2,538,324,402 | 106,064,965,045 |
| bytes-s6-p1 | 14846.686081819 | 111.531242416 | 20,269,084,650 | 16,535,726,522 | 20,269,084,650 | 18,010,999,755 | 4,046,531,103 | 80,606,699,913 | 75 | 180,169,641 | 40,068,530,688 | 1,621,526,772 | 82,228,226,685 |

Largest P + smoke share: **118,843,585,614 bytes (s4)**. Full-session native arm P is **116,400,948,249 bytes** for s4; the additional 2,442,637,365-byte retained smoke share is the existing PRECHECK requirement when smoke is due. No reserve was added.

## Beside the H-only draft

H-only S was labelled a lower bound in BY-PREP-P. The newer specific span text resolves the missing verdict/backup terms as outside S. H-only P and T replay exactly before and after the C5 fix.

| Pack | H S | new S − H S | H T | new T − H T | H P | new P − H P | H P+smoke | new bar − H bar |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bytes-s1-p1 | 19164.709415126 | 52.970056745 | 96.390694042 | 0.000000000 | 73,814,147,037 | 26,893,891,264 | 75,214,718,599 | 27,433,783,949 |
| bytes-s2-p1 | 20152.665044987 | 52.970056745 | 102.247239625 | 0.000000000 | 75,981,813,519 | 27,379,504,284 | 77,451,750,408 | 27,934,936,586 |
| bytes-s3-p1 | 21506.955177326 | 132.391335628 | 112.229906125 | 0.000000000 | 79,464,395,095 | 27,259,058,266 | 81,045,774,595 | 27,810,636,294 |
| bytes-s4-p1 | 23176.384199541 | 52.970056745 | 142.944862875 | 0.000000000 | 85,140,886,637 | 31,260,061,612 | 86,903,913,866 | 31,939,671,748 |
| bytes-s5-p1 | 18854.096009814 | 197.540760048 | 201.498298959 | 0.000000000 | 75,849,013,177 | 27,677,627,466 | 77,681,122,275 | 28,383,842,770 |
| bytes-s6-p1 | 14717.662440631 | 129.023641188 | 111.030780958 | 0.500461458 | 62,811,368,483 | 17,795,331,430 | 64,121,971,793 | 18,106,254,892 |

All remaining H-only values and exact differences follow. Fixed bytes and n have zero difference for every pack.

### Basis comparison

| Pack | H B_s | Δ B_s | H B_w | Δ B_w | H B | Δ B | H WAIT | Δ WAIT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bytes-s1-p1 | 21,883,930,645 | 8,435,823,199 | 21,697,490,999 | 49,952,216 | 21,883,930,645 | 8,435,823,199 | 12,999,877,322 | 5,011,122,433 |
| bytes-s2-p1 | 22,841,465,166 | 8,804,928,429 | 22,967,763,886 | 49,952,217 | 22,967,763,886 | 8,678,629,709 | 12,999,877,322 | 5,011,122,433 |
| bytes-s3-p1 | 24,053,464,961 | 9,273,996,413 | 24,709,054,674 | 152,068,844 | 24,709,054,674 | 8,618,406,700 | 12,999,877,322 | 5,011,122,433 |
| bytes-s4-p1 | 27,547,300,445 | 10,618,908,373 | 26,855,538,139 | 49,952,217 | 27,547,300,445 | 10,618,908,373 | 12,999,877,322 | 5,011,122,433 |
| bytes-s5-p1 | 22,901,363,715 | 8,827,691,300 | 21,700,998,244 | 241,281,660 | 22,901,363,715 | 8,827,691,300 | 12,999,877,322 | 5,011,122,433 |
| bytes-s6-p1 | 14,585,071,383 | 5,684,013,267 | 16,382,541,368 | 153,185,154 | 16,382,541,368 | 3,886,543,282 | 12,999,877,322 | 5,011,122,433 |

### Encoding comparison

| Pack | H q | Δ q | H headroom | Δ headroom | H smoke_share | Δ smoke_share |
| --- | --- | --- | --- | --- | --- | --- |
| bytes-s1-p1 | 116,714,296 | 44,991,057 | 30,046,286,037 | 10,022,244,889 | 1,400,571,562 | 539,892,685 |
| bytes-s2-p1 | 122,494,740 | 46,286,025 | 30,046,286,019 | 10,022,244,909 | 1,469,936,889 | 555,432,302 |
| bytes-s3-p1 | 131,781,624 | 45,964,836 | 30,046,286,095 | 10,022,244,766 | 1,581,379,500 | 551,578,028 |
| bytes-s4-p1 | 146,918,935 | 56,634,178 | 30,046,286,012 | 10,022,244,862 | 1,763,027,229 | 679,610,136 |
| bytes-s5-p1 | 203,567,677 | 78,468,367 | 30,046,285,852 | 10,022,244,891 | 1,832,109,098 | 706,215,304 |
| bytes-s6-p1 | 145,622,589 | 34,547,052 | 30,046,285,958 | 10,022,244,730 | 1,310,603,310 | 310,923,462 |

The common primary disk cause is the new r_s maximum: BY-H2 `bytes-mac-check-test7-qwen35-122b-start-r02` has 225,112,064 allocated raw bytes / 89.98983304190915 paired-stream seconds. It is a reference control, as the real kit plan specifies. r_s rises from 1,805,538.5168827055 to 2,501,527.7436414743 B/s; WAIT rises by 5,011,122,433 bytes. r_w stays 1,285,759.0452694688 B/s (H `neg8-refcorpus-r15`). Stream basis now dominates all six packs. The measured margin stays exactly 135722362995148/4081589090824127 = 0.03325233382759357; completion changes, not its value.

S changes because the reference and relevant model means now include every completed timed run belonging to them, including test-7 workloads and controls, and the stage-overhead mean pools both sessions. Small-model means remain H's five checks each. Actual combined receipt counts: llama-70b 34, qwen3-next-80b 11, qwen35-122b 23, reference 65, and five for each of seven other models (168 total). Test-7 controls belong to reference, not to the model named in their stage ID. The pooled stage mean is 45.85902460132326 s rather than 44.44705606997013 s. T changes only for s6: a newly observed maximum of 111.53124241600744 s, versus 111.03078095801175 s. See exact source lexemes in derivation.json; no rounded table input is used in P.

## C5 fix and before/after

Frozen BY-H2 C5 fails at `number(cpu["w_j_per_cpu_s"], ...)`: the stored receipt is null and `Decimal(str(None))` raises `decimal.InvalidOperation` with `ConversionSyntax`. The old parser also fails on a never-ran member's null timing in a zero-run session. The integrated baseline already handled null optional receipts, but still failed on remainder plans (`KeyError: llama-70b`, no check group) and a zero-run empty spread (`max()` on an empty sequence).

The fix distinguishes missing/malformed numerical operands from structural identity errors. Optional diagnostic operands produce only their dependent unavailable lines and `receipt.operand_unavailable` flags. A bad mandatory run operand leaves every candidate unavailable, so it cannot quietly drop a run from a maximum/mean. Missing check groups, empty spreads and absent references remain explicit unavailable results. Identity, roster and membership conflicts are still refused. No gate threshold, tolerance, margin or reserve changed. `request_spread` and `sizing_span` expose the same C5 forms to the pooling script; production valid-input arithmetic reproduces H exactly.

`verify_operands.py` uses the actual exporter and production-shaped synthetic bundles. Before: malformed CPU -> InvalidOperation/ConversionSyntax; zero-run -> empty max ValueError; remainder -> KeyError. After: each CLI writes JSON with unavailable lines and flags; expected computed-status exits 1, 2, 2. The zero-run iCloud tar could not be opened (`OSError: [Errno 11] Resource deadlock avoided`), so no replay of the original offloaded zero-run archive is claimed; the zero-run regression is synthetic. Nothing was restored or written into a session.

BY-H2 alone, frozen original measurements: JSON written, exit 2, status fail; 4 fail, 5 pass, 36 unavailable, 2 flag-only lines. After archive raw-byte augmentation only: JSON written, exit 2; 6 fail, 8 pass, 31 unavailable, 2 flag-only. Its lack of check observations and fixed_desk_s=null remain visible. The latter output derives s5 P=102,189,765,853 and s6 P=79,826,572,991; it is not the pooled registration table. Both outputs and logs are retained.

## Evidence and exact consumers

H data is frozen at JouleWise-data `8db1b40d64d8c543e7a9bee4fd9ced0da63d4b0b`, `bytes-h-desk-20261022`, session `bytes-h-20261021T185555335572Z-calibration`: 95 timed joins. BY-H2 is `bytes-h2-20261023T144711843389Z-calibration`: 73 timed joins. The unchanged H `indep_measure.py` reads an archive-only view for BY-H2. Only stage_dir locators in a scratch copy of the run-clock journal are remapped; clocks and all raw bundle contents are unchanged. Raw bytes are inode-deduplicated st_blocks*512 including directory allocations, not retained_bytes/2. Every raw stat observation, input content hash, original MEASUREMENTS source inventory and archive SHA256 inventory is pinned in derivation.json or its hash-bound h2.raw-provenance.json.

The source block in each row records both session identities, base computing-code commit `1c458d71d8a048e24b6c3a6b402fe3c34d9f57c3`, worktree_changes=true, and exact hashes of changed/uncommitted computing code. There is no invented commit for these uncommitted changes. The lead owns committing them.

All six rows pass real `registration.load_sizing`, `plan_inputs.build`, `valid_disk_terms` and `encode_disk_budget` with the actual pass-1 trees. Every integer P=2(B+WAIT)+fixed and native identity 3nq+headroom=P is exact; q>0. An explicit test enumerates s1..s6; six in-memory deletion mutations each fail it. The two edited test modules passed 37 tests. The final three-module run has 46 tests, 45 pass and one scope-blocked legacy assertion failure. No whole suite or hardware action ran.

## Identity/refit trace (read only)

`joulewise/b5/harvest.py:model_identity` compares the archived member's observed model_artifact_sha256 and runtime_identity_sha256 with the identity pin override (main emission at lines 5847–5851). In all 73 archived mismatch records, the model artifact hash equals its expected hash exactly; the expected runtime hash is null and the observed hash is populated. This flags an unrecorded runtime pin, not a demonstrated model-file difference. `flag-trace.json` retains all compared values and all four model groups. No rehash of current live model files is claimed.

`joulewise/controller.py:_window_calibration_verdict_bound` at lines 570–571 compares the verdict schema with `joulewise.window_calibration_verdict.v1`. The archived verified, unflagged verdict and its producer (`scripts/b5_window_calibration_verdict.py:46`) instead use `joulewise.b5_window_calibration_verdict.v1`. All 73 observed reasons equal `verdict_schema_mismatch`. The check returns before comparing evidence/manifest/plist/events or estimator digests. The controller then calls `verify_stored_evidence_physics` (lines 780–791) and emits `calibration.refit_cache_miss` (lines 415–424); this is a cache-record schema gap and fallback refit, not evidence that model files differ or raw calibration physics failed. Both deployed source files and the archived verdict are hash-bound in flag-trace.json. No repair was made.

## Decisions I made

- Follow the explicit bounded AGENT brief; ACTIVE_STOP_CARD is NONE. Keep all writes within the exhaustive allowlist and preserve all non-claim session evidence read only.
- Include all 168 completed timed observations in their actual model/reference means and both rate maxima, retaining flags. Use kit model_id, not the stage name, for test-7 controls (user Do 3).
- Pool succeeded check/soak request groups by model/purpose: 70B soak 11+12=23, 122B soak 12. Their margin is complete; no clean-only subset or new allowance policy is introduced.
- Pool the 28 completed collection-stage observations by weighting their stored means by 16 and 12, preserving C5's mean form. Retain the measured H 1185-second fixed allowance. The later specific BY-H2 ARM-PACKET.md:73,83 assigns whole-window verdict/backup 0 seconds in S; fixed-desk-decision.md gives the full citation and disjoint 1+227+719+238 breakdown. No fixed term remains unmeasured for this programmed-span definition.
- Keep committed fixed bytes 4,046,531,103, c=2, WAIT budget 7200 seconds, whole-basis ceilings and native q/headroom/smoke encoding. No extra padding. Use exact stored decimal lexemes/Fractions for P. Independent program comparison uses the ruled 1e-6 relative bar; byte identities use equality.
- Add six sizing inputs only. Pack registration status, estimator versions, plan trees, identity pins, and bytes_pack_v1.md are untouched; cold-gate and launch authority remain with the lead.

## NEEDS_SCOPE; NEEDS_RULING

NEEDS_RULING on which data count or printed numbers: none.

NEEDS_SCOPE: `tests/b6/test_plan_inputs.py`, specifically `ClockThresholdTests.test_block5_sizing_copy_remains_identical` at lines 31–33. It requires whole-file equality with the block-5 sizing file, contradicting the requested six B6-only additions. Minimal change: preserve equality for every original top-level field and the ALPHA/BETA/GAMMA rows, allowing added BYTES rows, as already done in the in-scope test module. The six-row explicit consumer/deletion test is already implemented in tests/test_b6_registration.py. Do not edit the block-5 source to satisfy this stale assertion.

Completed authorized work: all seven requested parts, including rows, C5 fix, evidence, trace and patch files. Blocked work: repairing the out-of-scope assertion and delivering a green three-module run. Next exact step: lead grants this path or repairs the assertion, reruns the same three focused modules, then performs registration cold-gate review and commits the patches. No Git metadata was written here.

## Exact replay and tails

All commands use `TMPDIR=/private/tmp/by-slots/20261023-by-slots JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`; Python is `/opt/homebrew/bin/python3.13 -B`. Scripts run from the worktree root. See verification.json for machine-readable commands/results and logs/ for complete tails. H recipe steps 1–4 were executed with their output destination relocated inside the allowlist. Snapshot source staging used `git -C /Users/edr/code/JouleWise-data archive <pinned commit> bytes-h-desk-20261022 | tar -x -C .scratch-SLOTS/by-slots/source` (both processes carried the safety environment).

- verify_h.py: `H-only replay: exact integer/time identities preserved after C5 fix`.
- H raw C5 last sizing line: `sizing:bytes-s6-p2: unavailable`; draft: `sizing:bytes-s6-p2: flag only` (both exit 2 with JSON).
- measure_h2_raw.py: `BY-H2: 73 exact timing joins; raw bytes from unchanged H extractor, archive only`.
- verify_operands.py: `3/3 native-export synthetic before/after and CLI-write regressions passed`.
- derive_slots.py --write: `6/6 exact P and native identities; 168 timed receipts; pooled soaks 23/12`; `largest P+smoke: 118843585614`.
- verify_missing_rows.py: `6/6 missing pass-1 rows caught; no repository file mutated`.
- final targeted modules: `Ran 46 tests ...`, `FAILED (failures=1)`; sole failure is the unmodified out-of-scope whole-file assertion.

Seven numbered patches in patches/ correspond to task parts 1–7; SHA256SUMS binds them. They are uncommitted, use repository-relative paths, and can be applied independently by part (part 3 calls C5 helpers from part 2). The scratch H snapshot is frozen evidence, never a replacement for its pinned source identity.

Patch application verification succeeded for all seven parts and reproduced all four production files exactly. Git reported 124 whitespace warnings for the frozen H CSV's original CRLF lines in part 1; those evidence bytes were preserved without normalization.
