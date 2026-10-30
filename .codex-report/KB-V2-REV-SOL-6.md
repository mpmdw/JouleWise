MODEL_ID: UNAVAILABLE (runtime exposes Codex / GPT-6 family, not an exact serving-model identifier)
VERDICT: ACCEPT_WITH_FIXES

Reviewed `156f03110..4a63b50b9536928007cbeec2a50d28cf19a2b5b3`, PR #593. K1–K4 work as ruled. Two remaining MINOR defects; neither is introduced by this delta. No BLOCKER or MAJOR found. Evidence below is synthetic execution, not Mac hardware validation. Before replaying scripts, restore the preserved input once with `python3.13 -B .codex-report/kb-v2-rev-sol-6/restore_fixture.py`.

1. **MINOR — oversized integer JSON tokens bypass the reasoned-leaf path and crash the CLI.** `scripts/bytes_stream_test.py:1169`.

   A production-shaped input with just `records[0].harvest.battery_edge_j[0]` replaced by a 5,001-digit integer is valid JSON (independently parsed with `parse_int=str`). The default `json.loads` integer conversion raises before `read_known_bytes` runs. Exit 1, zero stdout, no retained record or calls. The ordinary `10**400` leaf tests do not cross this parser limit. This is the same absurd-magnitude severity as K2, not a practical smaller-bound case. Handle oversized numeric tokens so they reach a reasoned invalid-leaf result without losing the other evidence; do not merely suppress the traceback and discard the record.

   Repro from the review checkout:
   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B .codex-report/kb-v2-rev-sol-6/huge_json.py
   ```
   Output tail:
   ```text
   JSON grammar validated with parse_int=str
   valid JSON 5001-digit numeric battery_edge_j[0]; rc= 1 stdout bytes= 0
   ValueError: Exceeds the limit (4300 digits) for integer string conversion: value has 5001 digits; use sys.set_int_max_str_digits() to increase the limit
   ```
   Complete stderr tail: `kb-v2-rev-sol-6/huge_json.log`. The parser line predates Round 8 (`46c5777bea`).

2. **MINOR — native idle overflow reasons omit the numeric leaf name.** `scripts/bytes_stream_test.py:421`, `:851`.

   Set `records[0].harvest.idle.pre.rails[0].power_w = 1e308`. The input passes the individual finite/non-negative check; variance arithmetic overflows safely. The reason identifies the rails collection but never says `power_w`, failing the requested leaf-naming assertion. Both rails/rest are already undefined, all evidence is retained, and no class or printed number depends on this wording. This is only a label defect.

   Repro:
   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B .codex-report/kb-v2-rev-sol-6/label_overflow.py
   ```
   Output tail:
   ```text
   rc 0
   calls 8 input retained True
   rails UNDETERMINED not defined (idle variance not defined (records[0].harvest.idle.pre.rails: rails idle arithmetic unavailable: (34, 'Numerical result out of range')))
   reasons ["idle variance not defined (records[0].harvest.idle.pre.rails: rails idle arithmetic unavailable: (34, 'Numerical result out of range'))"]
   ```

## Executed

All Python commands used Python 3.13, `-B`, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`. Scripts/logs are under `.codex-report/kb-v2-rev-sol-6/`; `README.txt` gives replay commands. The compressed fixture preserves the full original input. No production source was edited.

- Read Round 8 and its replay transcripts, the reading rule and registration, and Opus's report/scripts from JouleWise-data `8970e3b4e414b908ef0be60f1c2d30a94c66c7a1`. Generated the full fixture using the real `stream()` with fake arrays and the supplied clock compatibility shim.
- Re-ran unchanged `probes6.py`: **53 CLI cases, all exit 0, eight calls, zero traceback/shrink flags**. Re-ran `overflow_battery_edge.py`: **nine cases, no exception**. Their outputs match the recorded Round 8 after-transcripts exactly after trimming trailing whitespace (189 and nine lines). Full output: `probes6.log`, `overflow.log`. Every targeted K1–K4 invalid case has a reasoned undefined affected result. None fails. Unaffected boundaries can retain their numbers. Valid zero, signed battery measurements, disclosure differences, and large finite values with finite arithmetic are not all supposed to become undefined.
- K2's `tau_s_1e300_rec0`, `gap_fsum_overflow_rec3`, and `anchor_shift_1e308_all` retain all calls and reasoned undefined affected quantities.
- `targeted.py`: computed negative widths (rails **−0.009011669683539163**, GPU **−0.004501637249556736**, DC **−0.01782000132919857**, rest **−0.009074975257083848 J/GB**) from individually valid leaves are rejected before formatting. These use reversed cache sizes with corresponding receipt sizes, not an injected reducer result. All-zero rails/GPU and signed meter/battery cancellation give zero widths and quantity-naming UNDETERMINED results. Finite-leaf overflow gives undefined results. Formatter spy: **74 calls, every width finite and positive**. Zero-valued edge/anchor bounds and a zero GPU measurement remain accepted; the direct zero-width formatting helper still returns `0.00 ± 0.00`.
- K3: overlapping and exact duplicate native rails/GPU rows refuse the dependent classes in both idle spans; touching intervals retain the baseline result. `order.py`: **136** further receipt-endpoint and battery-poll order cases, exit 0, complete records, no invalid shrink.
- K4: read `knee_scan` itself. Initializer emits `knee not found`; its sole success update emits `knee found`. The reader accepts exactly these two status strings; null/missing/non-string/unknown statuses fail validation, and `knee not found` with numeric K is refused. GPU/meter negative integrals are refused as ruled.
- Independent `walk.py`: **2,320 numeric leaves × 13 modes + 544 native order violations = 30,704 executions** through real `main(['read', file])`, including JSON parsing/serialization and return-code checks. Every execution returned 0 with all eight calls and complete input evidence; zero crashes. Modes include deletion, null, wrong type, non-finite, wrong length, `10**400`, `1e308`, negative, zero, `"NaN"`, both infinities, and bool. Compact native support uses four rows per idle collection; every row and all eight positions are visited, including scan evidence/informational numeric leaves. **No malformed-mode/order shrink**; all 42 shrink flags are valid zeros (meter edges, missing sample counts, anchor, r_max, or receipt start). Ignored informational leaves do not need to affect a result. Leaf-name diagnostics expose finding 2; large finite values that compute finite results need no invented maximum. This walk invokes the CLI entry point in-process; the repository generated test and supplied probes use fresh subprocesses. The separate parser-limit repro exposes finding 1.
- Opus `h4_arms.py`: **1,248 checks, zero failures**, including bit-identical retained coefficients.
- Requested unittest run: **124 tests, OK, 1795.932 s**, including **1,134 generated fresh-process CLI faults**. Command: `python3.13 -B -m unittest tests.test_bytes_stream_test tests.test_bytes_mac_kit tests.test_bytes_h_session tests.test_repin`; complete output in `tests.log`.
- `python3.13 -B scripts/repin.py --check`: **PASS 16 pin families current**. It also prints the existing sealed-inventory divergence warning; this is not a pin-check failure.

Worked output, unchanged (`fixture.log`):

```text
rails 0.06672 ± 0.00057 J/GB
DC    0.1929  ± 0.0025  J/GB
rest  0.1262  ± 0.0024  J/GB
share 0.3458  ± 0.0075
```

Bars are unchanged and used in the right comparisons. **4.5e-7 GB/s = 1% × 0.000045 GB/s** for rational scan agreement. Independently re-executed maximum binary64 discrepancy is **2.8793189825782005e-13 GB/s**; multiplied by 1e6 it is **2.8793189825782006e-7**, below that bar. **5.7e-6 J/GB = 1% × 0.00057 J/GB** for the worked rails/DC/rest comparison; the rule's propagated 1e6-times-float-noise value is **2.5e-10 J/GB**. Program-minus-independent energy discrepancies are at most **2.81e-6 J/GB**, inside the lead's bar. No new agreement bar was chosen; exact comparisons concern retained identity, complete evidence, discrete classes, or prescribed output formatting.

CI **READ** on exact head `4a63b50b9536928007cbeec2a50d28cf19a2b5b3`: [ci run 40985645783](https://github.com/mpmdw/JouleWise/actions/runs/40985645783) completed successfully. All **20 jobs succeeded**: changes, fences, build, quick, installed-wheel, calibration-exits-exclusive (3.13), calibration-writer-crash-matrix-exclusive (3.13, 1/2), and test (3.13, shards 1–12). Separate [gate-ledger run 40985645897](https://github.com/mpmdw/JouleWise/actions/runs/40985645897) and its job were **SKIPPED**, not green. No red job was returned. Raw observations: `ci.json`.

## Decisions I made

- K1's absolute-power edge term is non-negative; battery samples/integrals remain signed. Reject computed nonpositive uncertainty without rejecting legitimate zero measurements or individual bounds.
- Treat touching native intervals as valid. Reject overlap/duplicates without dropping rows.
- Compare scan statuses against the actual producer, including refusal-with-K consistency.
- Classify the parser-limit crash as MINOR, matching K2's absurd-magnitude cases. Classify the reason-only omission as MINOR because it changes no class or printed number.
- Do not count valid zero changes or inert numeric disclosures as malformed-input shrink defects. Preserve the lead's two bars; introduce no physical maximum, epsilon, or replacement uncertainty.

Review branch: `codex/2026-10-30-kb-v2-rev-sol-6`, based directly on `4a63b50b9`. Only the requested report/evidence paths are written. No admission or merge performed.
