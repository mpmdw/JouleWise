GPT-6 (Codex; exact deployment model ID is not exposed to this session)
VERDICT: ACCEPT_WITH_FIXES

Executing review of `977a5d2df..6847502b8b6adec1d232bbfce10cb2a2c729498b`, draft PR #593. The original round-4 finding scenarios are corrected. G2's arm reductions, G4, R-G3 and G5 agree with the rulings. G1 substantially improves malformed-input handling, but still has the record-loss cases, scan-input bypass and value-retention gap below. Do not treat this verdict as admission of the reading rule.

Commands run from `/workspace/JouleWise`, with `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, Python 3.13.5. Set `R=.codex-report/kb-v2-rev-sol-4`. The session identifies its model family but exposes no verifiable deployment ID; line 1 records that limitation.

## Numbered findings

1. **MAJOR — a reversed native idle interval escapes G1 and loses the entire record.** `scripts/bytes_stream_test.py:226` validates the two endpoints independently as nonnegative integers, but not their ordering. At `:404` the invalid interval becomes a negative support duration; `:421` passes it to the estimator without handling its `ValueError`. This is an unusable harvest prerequisite, and must take the reasoned missing path instead of aborting all eight calls. It is independent of the fixed null/wrong-type cases.

   Repro: `python3.13 -B "$R/extra.py"` (also writes `reversed_idle.json` for a direct `scripts/bytes_stream_test.py read` invocation). It changes only `records[0].harvest.idle.pre.rails[1].end_ns` to one ns before that row's start. Both endpoints remain ordinary positive integers. Output tail:

   ```text
   reversed_idle EXIT 1 ValueError: idle durations must match samples and be finite and > 0
   ```

   Validate interval duration/support in the shared input validation before estimation, preserve the row as evidence, and mark the affected rails/rest computation undefined with its input path. Do not discard the invalid row and recompute a potentially smaller bound. The compact fixture has four native intervals over the same 57.6 s idle span; it otherwise passes the actual reader. The same crash is independently reproduced with the original uncompressed 10 Hz native streams (`full-interval.log`).

2. **MINOR — the shared accessor itself raises on a JSON integer outside binary64's conversion range.** `scripts/bytes_stream_test.py:210` calls `math.isfinite(value)` before integer-specific handling. Python accepts `10**400` as a JSON integer, but this call raises `OverflowError`; neither `take` nor the reader catches it. Thus even a malformed count in the final call destroys the seven other calls and all output.

   Repro: `python3.13 -B "$R/extra.py"`; the `huge_integer` case sets only `records[7].receipt.repeats = 10**400`. Output tail:

   ```text
   huge_integer EXIT 1 OverflowError: int too large to convert to float
   ```

   Make validation total over JSON numeric inputs, including overflow during conversion, and return a leaf-naming missing reason for values the downstream arithmetic cannot represent. No replacement count or agreement bar is needed.

3. **MINOR — scan status bypasses the shared accessor.** `scripts/bytes_stream_test.py:576` reads `scan.get("status")` directly after validating only that scan is a dict. The key controls the special refusal path but has no presence/type validation. With an otherwise valid worked scan, `status = null` is silently accepted: all four classes remain RESOLVED and there is no missing reason. This fails G1's explicit structural requirement for consumed CLI/scan inputs, even though this particular mutation leaves the numerical sizes intact.

   Repro: `python3.13 -B "$R/extra.py"`; output tail:

   ```text
   bad_scan_status EXIT 0 {'rails': ('RESOLVED', ...), 'gpu': ('RESOLVED', ...), 'dc': ('RESOLVED', ...), 'rest': ('RESOLVED', ...)} []
   ```

   Validate the consumed status through the accessor and preserve the usual reasoned refusal for a legitimate `knee not found` scan. The independent numerical-size walk alone cannot establish the EVERY-value claim.

4. **MINOR — losing C3 still suppresses central coefficients that do not depend on C3.** `scripts/bytes_stream_test.py:520` returns as soon as any arm lacks `x`. G2 correctly retains the other arm summaries, but the G1 requirement to print every still-computable number is not complete. With just the first C3 record replaced by `{}`, S/C1/C2 are complete: §3 steps 4, 6 and 7 define `gamma_c`, `alpha`, `gamma_d` and Delta from those arms alone. Only the residual and its propagated uncertainty require C3. All four central values are nevertheless omitted.

   Repro: `python3.13 -B "$R/partial.py"`. Output tail:

   ```text
   lost C3 class UNDETERMINED printed gamma_c None alpha None gamma_d None delta None
   from retained complete arms: gamma_c 0.028000195821126284 alpha 0.0013999906666666668 gamma_d 0.09471662736453161 delta 0.06671643154340534
   ```

   Keep UNDETERMINED and leave residual/uncertainty undefined, but calculate and print the central coefficients whose prerequisite arms remain complete. This changes no class or valid-input number.

## Executed

Prior evidence refs: Sol `373c23204b922595abd3c8fe2312b644249436f2`; Opus `7343d6031a8f598a80311856f338d4c4871c3d78`. Read both complete prior reports, their scripts, Round 5 including “Outcome after lead ruling R-G3”, the full source delta, the reader/scan/accessor paths and governing rule sections. The stop card is inactive. No subagents, MLX, Metal, live capture, BYTES data, unblinding, admission or merge were used.

### Prior finding replays

- **Sol-3 findings 1–2:** `sol3/reader_edges.py` against the disk-backed real-stream fixture: all eight scenarios exit 0. Null edge elements, empty edge lists, null pre-idle and null receipt give UNDETERMINED with reasons; available arm summaries remain. Missing C1 receipt/count retains the complete S/C3/C2 summaries.
- **Sol-3 findings 3–4 / Opus-2 finding 1:** exact registry checks and whole session/repin test modules are reported below. The old four stale bindings and manifest-path KeyError are corrected.
- **Opus-2 findings 2–5:** `opus2/e2e4_adapted.py` replays empty/one-edge/scalar inputs, malformed gap rows, bad anchor values, negative/string adapter ratings, dropped calls and empty records. All reader calls exit 0; unavailable bounds are undefined, never zero replacements. The script's old display inspector was changed only from indexing an absent `edge_bound_j` to `.get`; scenarios and arithmetic are unchanged. The unmodified script is preserved alongside it. **Literal `e2e4.py` does not complete**: its own display inspector raises `KeyError: 'edge_bound_j'` when the corrected reader leaves that unavailable bound absent (`opus-literal.log`). This is a stale harness assumption, not a reader traceback; the adapted copy completes every scenario.
- **Opus-2 findings 6–8:** the scan reference now matches its final pair entry, `5 ± 150` prints upper limit `160`, and omission of `gpu_power` gives GPU UNDETERMINED. Both registered and harvested rail-set arms were independently exercised in `supplement.py`; DC remains computable.

The earlier repro scripts are copied under `sol3/` and `opus2/`. Sol helpers' repository-root expressions were adjusted for their deeper location. The full production-shaped fixture comes from the prior `sol3/adapted/e2e.py`: real `stream()`, fake arrays, production repeat counts, receipts written and reloaded, then fresh real read CLIs. Its worked numbers and independent arithmetic remain unchanged.

Rebuild and replay the serialized fixtures with:

```sh
python3.13 -B "$R/sol3/adapted/e2e.py" /workspace/JouleWise "$R/e2e"
python3.13 -B "$R/opus2/e2e4_adapted.py" /workspace/JouleWise "$R/e2e" "$R/opus-run"
python3.13 -B "$R/walk.py"
python3.13 -B "$R/scanwalk.py"
```

### Independent structural walk and per-arm checks

`walk.py` uses the serialized real-stream fixture and recursively walks actual values rather than importing the builder's schema or walk. It covers every one of the eight calls, every compact native row, both edge-list elements, every rail-name element, two gap rows per call, and the five consumed scan-size inputs. Native support is compacted to four 14.4 s intervals over 57.6 s to keep thousands of fresh CLI processes practical; baseline results are checked before mutations. Numeric leaves receive deletion/null/object/NaN faults; text leaves receive deletion/null/object faults. Each case checks exit 0, eight retained calls, an affected UNDETERMINED result, leaf reasons where applicable, and no smaller surviving aggregate or per-call bound. Fixed edge-list length mutations are also covered by the builder regression.

Result: **1,133 leaves, 4,356 fresh read CLI faults, zero failures; 32 lost-call variants PASS**.

`scanwalk.py` separately mutates all nine consumed scan prerequisites in all 66 real-stream scan receipts: 2,376 in-process faults, plus real scan CLI refusal at every one of the 66 positions. It checks all receipts survive and reasons name the leaf. The non-Mac clock arm (inapplicable tick numerator/denominator) is independently checked by `supplement.py`. Missing fields that the reader does not consume, such as its receipt clock metadata after scan, are not misreported as reader prerequisites.

Result: **2,376 scan leaf faults, zero failures; 66 real scan CLI positions PASS**.

G2 is independently checked for all eight positions, each as a dropped record, `{}`, null receipt and missing repeat count: exactly the lost arm lacks `x`; every other arm retains its summary for every boundary. Whole-test classification can still be UNDETERMINED under the common DC prerequisite; that does not suppress complete arms.

`mapping.py` separately replays all 4,356 mutations against the real reader function with explicit assertions for the particular affected boundary classes; all pass. `descriptions.py` adds 24 fresh CLI cases for description-only timing/session fields and nested GPU/thermal JSON lists in the first and final calls. These correctly print reasoned unavailable descriptions, rather than imposing a new class gate on the rule's description-only fields. The accessor covers the tested receipt/harvest scalars and nested collections; descriptive timing/GPU/thermal values use the same accessor later in the reader. The independent faults pass for the basic missing/type/finiteness cases. Findings 1–4 identify limits of the claimed structural guarantee beyond that finite basic mutation set.

### Tests, registry and numbers

```sh
python3.13 -B -m unittest -v tests.test_bytes_stream_test tests.test_bytes_mac_kit
python3.13 -B -m unittest -v tests.test_bytes_h_session tests.test_repin
```

```text
Ran 49 tests in 1450.139s
OK
generated real read CLI leaf faults: 945

Ran 73 tests in 1583.748s
OK
```

All **122 tests pass**: 49 reader/kit, 36 session, 37 repin. The whole repository suite was not run for this bounded review. `git diff --check` passes.

`repin.py --check` prints `PASS 16 pin families current`; `bytes_mac_kit.py --check` prints `verified non-claim Mac kit`.

`supplement.py` compares the parsed registries against `977a5d2df`: exactly `/stage_graph/{2,4,18,24}/input/sha256` change in the kit-plan entry, to bound-collection/reference-start/reference-midpoint/reference-end under `configs/campaigns/bytes-s1-p1/members/`. After replacing those four rows in memory, the entire registry equals the baseline, including targets, metadata and summaries. Kind-P stays 32,556. The six sizing bindings and other-lane census omissions are preserved. History contains the explicit revert `013a8e99d` followed by narrow repair `0c513a7c3`.

G4's diff keys and looks up `external_ids` by the existing `manifest_id`, with no new IDs or fallback. G5's source rule is present in §2 at lines 220–222 and §4 at lines 369–370, and implemented in the reader's registered/harvested comparison.

The lead's bars remain **4.5e-7 GB/s** and **5.7e-6 J/GB**. Their derivations remain 1% of the smallest printed uncertainties (0.000045 GB/s and 0.00057 J/GB). The independent rational verifier and focused tests check the millionfold floating-noise floor against the scan bar; the documented energy floor is 2.5e-10 J/GB. No new agreement bar is selected. Exact comparisons in the new tests concern identities, retention or the requirement that a bound not shrink, not approximate numerical agreement.

The real-stream worked output remains **rails 0.06672 ± 0.00057, DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024 J/GB**, share 0.3458 ± 0.0075. Production-minus-independent energy differences remain within the existing bar. `replay.py` records additional prior scan, refusal and formatting runs in numbered logs. The first relocated rational-verifier invocation failed to import `scripts`; after correcting its copied harness root, `rational.log` records a passing independent verifier and 400 worked-phase confirmations per conversion. No production arithmetic was patched.

### CI at the requested head

PR metadata confirms draft #593 has exact head `6847502b8b6adec1d232bbfce10cb2a2c729498b`. Read through the GitHub connector: [ci run 40823591370](https://github.com/mpmdw/JouleWise/actions/runs/40823591370), gate-ledger run 40823591406.

Observed **2026-10-29 05:58:28 UTC**. No red job is present to attribute. The two previous causes are corrected locally; fences and quick also pass on this exact head. Seven ordinary shards remain in progress, so the complete CI run is **not yet established green**.

| Job | Observed state |
|---|---|
| changes | success |
| build | success |
| fences | success |
| calibration-writer-crash-matrix-exclusive (3.13, 2) | success |
| calibration-writer-crash-matrix-exclusive (3.13, 1) | success |
| calibration-exits-exclusive (3.13) | success |
| quick | success |
| test (3.13, 5) | success |
| test (3.13, 4) | success |
| test (3.13, 1) | in_progress |
| test (3.13, 9) | in_progress |
| test (3.13, 2) | in_progress |
| test (3.13, 3) | success |
| test (3.13, 12) | success |
| test (3.13, 6) | success |
| test (3.13, 11) | in_progress |
| test (3.13, 7) | in_progress |
| test (3.13, 10) | in_progress |
| test (3.13, 8) | in_progress |
| installed-wheel | success |
| gate-ledger | skipped (draft) |

Job IDs and states are preserved in `ci.json`. No workflow was rerun or modified.

## Decisions I made

- ACCEPT_WITH_FIXES: normal worked inputs and all old finding scenarios are corrected; the remaining malformed-input record-loss defects still prevent calling G1 complete. These are defects, not requests for a different rule or review process.
- Rated the physically malformed interval MAJOR; rated the extreme integer case MINOR because ordinary receipts cannot produce it, and the scan-status bypass and partial-value omission MINOR because they do not change valid-input numbers. No BLOCKER identified.
- Did not promote fractional timestamp acceptance or ignored read-side clock metadata to findings: the former has negligible demonstrated numerical effect, and the latter is not consumed by this reader. The extra script records these probes transparently.
- Preserved the specified estimators, source rules, bars and worked values. Used synthetic compact support only for fault coverage, never as hardware evidence.
- Wrote only this report and its authorized script/evidence directory. No production fixes or other bookkeeping edits; no delegation or permission request was needed.
