GPT-6 (exact deployment model identifier is not exposed by this runtime)
VERDICT: ACCEPT_WITH_FIXES

Reviewed mpmdw/JouleWise `e23cd1e7b..574f13d2f76cf245621e32a00c9ad7089898b310`, draft PR #598, target `lane/2026-10-28-bytes-pass2-open`. Authority: registration `docs/registrations/bytes_pack_v1.md` §21 item 3 and §7, T1–T7, U1–U4 and V1–V6. Read the entire implementation report, including both fix rounds, both delta reports, the delta, implementation, tests and relevant exporter/analysis paths. Executions used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, synthetic fixtures only; no hardware or real BYTES data. Production code was not edited.

1. **MINOR — An untrusted journal can still certify request-end equality for an undetermined member.** `scripts/bytes_thermal_lines.py:243`. The provenance guard runs only when the candidate code differs from the original. If a science member already has the OS code and the unsealed/mismatched journal reports nonzero inside its request, it is labelled `equals registered line`. With no other science members, the line's `equals_registered_line` is true. The trustworthy journal could instead put the nonzero only after request end, so this equality has not been established. Mark an originally OS-excluded member undefined when journal provenance is unavailable/mismatched, even when the untrusted candidate agrees. An originally code-free member remains determined by the removal-only rule. Keep the sealed would-add stop and existing original-code preservation.

   Repro from repository root (also runs findings 2 and 3):

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python3.13 .codex-report/by-therm-lines-rev-sol-3/independent.py
   ```

   Output excerpt:

   ```text
   NONZERO_UNTRUSTED missing [('a', 'equals registered line')] True []
   NONZERO_UNTRUSTED mismatch [('a', 'equals registered line')] True []
   NONZERO_UNTRUSTED matching [('a', 'equals registered line')] True []
   ```

   The matching case is the positive control. No exclusion code changes in the two faulty cases; severity is capped at MINOR under the brief's representation rule. U2's required protection against unproven restorations is closed, but the broader requested equality property is not complete.

2. **MINOR — Structurally damaged thermal records still crash `verify` and retain a false flag.** `scripts/bytes_thermal_lines.py:487`, `:507`, `:516`. Validation accepts any dict with a list-valued `notices`. A damaged `source_sha256` container or damaged notice entry then raises outside recovery. V3 handles missing/unparsable records but not these ordinary valid-JSON damages. Validate fields used by verification, recover the damaged record, list `thermal_line.json` and finish writing the change flag with exit 0.

   Same repro command. Output excerpt:

   ```text
   DAMAGED_RECORD source-null (1, "AttributeError: 'NoneType' object has no attribute 'items'") flag False
   DAMAGED_RECORD source-list (1, "AttributeError: 'list' object has no attribute 'items'") flag False
   DAMAGED_RECORD notice-null (1, "TypeError: 'NoneType' object is not subscriptable") flag False
   DAMAGED_RECORD notice-empty (1, "KeyError: 'code'") flag False
   DAMAGED_RECORD missing-binding (0, 'withheld/spans.json') flag True
   ```

   These are verification-record failures; no demonstrated change in which members count.

3. **MINOR — Numeric hull exclusion fields pass boolean validation but produce a false determined-equality label.** `scripts/bytes_thermal_lines.py:216`, `:231`. `excluded not in (True, False, None)` accepts JSON integers 0 and 1 through Python equality. The subsequent `is True` does not accept 1, so both numeric values fall through as determined non-additions. A science member without the code should be undefined for a malformed per-member assessment, as for the other unavailable fields. Require an actual bool or null, using type/identity consistently.

   Same repro command. Output excerpt:

   ```text
   INTEGER_EXCLUDED 0 ['equals registered line', 'equals registered line'] True []
   INTEGER_EXCLUDED 1 ['equals registered line', 'equals registered line'] True []
   ```

   The fixture has member `a` already OS-excluded and member `b` without that code. This is malformed-input certification, not evidence that the real boolean-valued harvest drops the wrong members. The requested undefined path would preserve the same original codes, so this finding is also MINOR.

## Prior finding dispositions

| Review finding | Disposition at the pinned head |
|---|---|
| Sol delta 1: output directory link mutates source | Closed by U1. Existing and dangling outputs refuse before writes; nested destination guards refuse links. Independent source snapshots remain identical. |
| Sol delta 2: stale export survives reused output | Closed by U1. The second transform into an existing output refuses; two fresh outputs have identical manifests and serialized change lists. |
| Sol delta 3: absent provenance permits restoration | Closed by U2. Absent/null/missing digest preserves codes and records `records.thermal_journal_provenance_unavailable`. Finding 1 above is a remaining equality-status case, not a restored member. |
| Sol delta 4: damaged manifest crashes verifier | Closed by U3. Missing/unparsable/structurally invalid manifests set the flag and exit 0. Finding 2 concerns the other control file. |
| Opus delta 1: hull unavailable direction and pass mismatch | Original cases closed by V1. Missing assessment, missing member/field, null excluded, journal unavailable keep existing code determined and code-free members undefined. Both pass mismatches make every science member undefined. Additional malformed numeric fields are finding 3. |
| Opus delta 2: empty/column-less CSV, missing hull field, Git failure, mismatch-driven would-add stop | Named cases closed by V2. Records are written with exit 0. A standalone script outside Git records both producer fields null. Mismatched/unsealed would-add records undefined; only a matching seal stops. U1's source-protection refusals remain required. |
| Opus delta 3: missing/unparsable thermal record | Original cases closed by V3; structural damage remains finding 2. |
| Opus delta 4: absent seal file treated as match | Closed by U2/V4 for unproven restorations. |
| Opus delta 5: empty withheld code quoted unlike exporter | Closed by V5. Entire rewritten withheld CSV matches exporter-parameter `DictWriter` output, including CRLF and opaque fields. |
| Opus delta 6: source freshness not verified | Closed by V6. Copied acceptance/export source changes and missing linked sources print `source changed since transform: <path>`, flag true, exit 0. |
| Opus delta 7: test runtime | Knowingly outside this round by the brief. No new runtime requirement is proposed. |

The first-round grouped-blind/model-loss and excluded-boolean findings stay closed by T1/T5. Writable linked files are knowingly superseded by T4's manifest/verification design, and the non-counting real-chain limitation by T7. Producing dirty-tree state remains present (T6). No new estimator or pass-combination policy was applied.

## Executed

Review scripts are under `.codex-report/by-therm-lines-rev-sol-3/`. The nine Sol delta scripts are byte copies from `3e95b69a39`; Opus `probes_delta.py` and `census_t1.py` are byte copies from `9cc245015`. Set `JW` and `PYTHONPATH` to the checkout; `/tmp/jw` links to it for legacy imports. No compound command uses `cd`.

Run originals with:

```sh
JW="$PWD" PYTHONPATH="$PWD" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/by-therm-lines-rev-sol-3/SCRIPT.py
```

| Script | Executed result |
|---|---|
| `sol_campaign.py` | Exit 0, `CAMPAIGN_DONE`; both passes, s2 science census 100/100, s5 50/50. Linked mutation remains possible as T4 permits. |
| `sol_probes.py` | Exit 1 at obsolete unsealed-restoration assertion; `EDGE_CHANGES []`. Separate explicit-seal port: exit 0, `PROBES_PASS`, boundary/duplicate/secondary-code/reference/JSON-sentinel checks pass. |
| `sol_chain.py` | Exit 0; real harvest/acceptance/export cross-pass changes agree. Analysis explicitly remains non-counting/mock-predictor unavailable under T7. |
| `opus_chain_test.py` | Exit 1, `SUMMARY 22 / 24`; only failures are the superseded pass-mismatch-refusal and all-linked-files-read-only expectations (T2/T4). |
| `opus_chain_analysis.py` | Exit 0, `SUMMARY 27 / 30`; three failed target-restoration checks inject unsealed pass-1 journals, now forbidden by U2. Explicit-seal port: `SUMMARY 30 / 30`. Supplied grouped port also 30/30. |
| `opus_probe_postcommit_heldout.py ROOT` | Exit 0, using retained root from original analysis: source and output each 100 records, both Qwen models compute. Unsealed source fit retains 9 quads in both; this is not claimed as a restored fit. The standalone sealed replay additionally preserves both models and 100 records while restoring the fit from 9 to 10 quads. |
| `campaign_delta.py` | Exit 0, `CAMPAIGN_DONE`; assertions pass on census, IDs, codes, models and store-read gate at both stages on both passes. |
| `view_and_gap.py` | Exit 0; 3 real-gap variants × 3 thresholds preserve exact OS tuples; added/deleted view files flag with exit 0. Optional real re-acceptance replay also exits 0: `REAL_REACCEPT_BYTE_IDENTICAL_DETECTED ['derived/b6-flags.jsonl']`. |
| `delta_probes.py` | Exit 1 at U1's required existing-output refusal. Prior lines show missing seal now undefined, zero changes, original OS code retained. Independent safety and damaged-manifest tests exercise the subsequent original repro cases separately. |
| `probes_delta.py` | Exit 0, every probe completes, without any U1 adaptation. Empty/column-less CSV and missing hull field write records; absent/null seal and mismatch preserve codes; matching seal restores; one-byte journal drift does not. All requested original verification faults exit 0 with true flag; baseline prints `view verified`. |
| `census_t1.py` | Exit 0 but prints four failed pass-1 target/status assertions because its injected journals are unsealed. Explicit-seal port: `SUMMARY fails []`. No census/model/store-read assertion fails in the original. |

For the positive-fixture ports, replace `SCRIPT.py` in the command with `replay_sealed.py sol_probes.py`, `replay_sealed.py opus_chain_analysis.py`, or `replay_sealed.py census_t1.py`. This adaptation supplies the synthetic provenance those old positive fixtures lacked; original failure outputs are retained above, not silently counted as passes.

The sealed census checks s2 public+withheld physical rows 63+50=113 and s5 13+50=63 (including references), on each pass. Before the stage-1 commit the science census is s2=50 and s5=0; after it, s2=100 and s5=50. Archive-stage counts match. Both stores' changed codes exactly match acceptance/change lists and all other fields remain equal. The analysis opens the copied withheld store only after the commit. In sealed pass-1 cases the affected models recover 9→10 quads; pass-2 additions give 10→9. These are exact counts.

Regression command (exit 0):

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.test_bytes_thermal_lines tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q
```

Output tail: `Ran 231 tests in 1187.136s`, `OK (skipped=11)`. This includes the supplied grouped port 30/30 and real-harvest chain 29/29; compressed-journal checks execute with zstd installed. Pass-1, block-5 and alpha byte-identity replays each compare 177 files exactly. Review scripts compile and the pinned copies are byte-identical to their source commits. `git diff --check` passes; fixture orphan census is `[]`, exit 0. The whole repository suite is left to PR-head CI: this review changes no production code or tests.

Independent `independent.py` and `safety.py` additionally exercise the direction matrix, both pass mismatches, the untrusted nonzero equality case, structured control-record damage, malformed boolean fields, an actual standalone non-Git script, existing/linked/dangling/overlapping outputs, nested destination guards, fresh-output determinism, and all three seal states of would-add. Safety output:

```text
REFUSED existing output must be a new directory source_unchanged True
REFUSED symlink output overlaps source archive/export source_unchanged True
REFUSED dangling output must be a new directory source_unchanged True
REFUSED inside output overlaps source archive/export source_unchanged True
FRESH_MANIFEST_AND_CHANGES_BYTE_IDENTICAL True
GUARD_REFUSED False destination directory is a symlink True
GUARD_REFUSED True destination directory is a symlink True
WOULD_ADD mismatched not defined (journal differs from the harvest's)
WOULD_ADD missing not defined (journal provenance unavailable)
WOULD_ADD matched STOP_BEFORE_WRITE request-end would add thermal.os_level_nonzero: a
OUTSIDE_GIT 0 None None
```

Blinding: Opus's wrapped JSON/CSV decoders report `decoded-sentinels []`, and stdout/control-record checks report `sentinels-in-stdout-or-record []`. Its withheld byte check is `(True, 1)`. Supplied tests compare against the exporter's own `DictWriter` parameters. Measurement fields are copied/hashed as opaque bytes, never decoded as energy, power, duration or rail values; no such value is emitted by the tool. Hashing payload bytes is part of the explicitly retained T4 design. The reviewer harness's deliberately printed synthetic sidecar is not a tool disclosure.

Numbers: inspected the delta and searched the implementation/tests for approximate comparisons. Codes, counts, integer-ns boundaries, hashes, sizes and inode/mtime metadata are compared exactly. No float tolerance or numerical agreement bar is introduced. Test-only float construction inserts sentinel lexemes; production's pre-existing discarded gap calculation is not an agreement tolerance. The randomized Opus probe ran 24,000 gap comparisons with 0 OS-decision differences (19,486 comparisons with unmeasured holes). `exact_ns.py` also passes a request-end boundary test above 2**60 ns: shifting the end by exactly 1 ns changes `removed` to unchanged, with exact expected code lists and no tolerance. No bar was chosen, so no new bar derivation is needed; any future bar must obey the supplied project rule.

SHA-256, exact:

```text
18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71  joulewise/bytes_analysis.py
2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744  joulewise/b5/harvest.py
```

PR #598 remains draft with head `574f13d2f76cf245621e32a00c9ad7089898b310`, confirmed through GitHub. CI snapshot at **2026-10-29 14:59:23 UTC**, [run 40892236120](https://github.com/mpmdw/JouleWise/actions/runs/40892236120):

| Job | State |
|---|---|
| changes | success |
| fences | success |
| build | success |
| quick | success |
| installed-wheel | success |
| calibration-exits-exclusive (3.13) | success |
| calibration-writer-crash-matrix-exclusive (3.13, 1) | success |
| calibration-writer-crash-matrix-exclusive (3.13, 2) | success |
| test (3.13, 1) | in progress |
| test (3.13, 2) | success |
| test (3.13, 3) | success |
| test (3.13, 4) | success |
| test (3.13, 5) | success |
| test (3.13, 6) | success |
| test (3.13, 7) | in progress |
| test (3.13, 8) | success |
| test (3.13, 9) | in progress |
| test (3.13, 10) | in progress |
| test (3.13, 11) | in progress |
| test (3.13, 12) | in progress |

Separate gate-ledger run 40892236198 is skipped. There is no red job to attribute at this snapshot. Fourteen jobs succeeded and six are still running; the complete suite is not claimed green.

## Decisions I made

- Apply the brief's severity cap: the three demonstrated defects affect equality certification or verification records, and no demonstrated changed member list follows. Verdict is ACCEPT_WITH_FIXES, not a rejection of the repaired ordinary membership path.
- Treat an untrusted journal's agreement as insufficient evidence of equality for an originally excluded request-end member. Direction alone determines only the originally code-free members there. No new science policy is needed.
- Keep the required U1 output refusals; the statement about two stops does not repeal U1. Do not ask to make reused output supported again.
- Preserve original reviewer scripts. `replay_sealed.py` is a separate, explicit positive-fixture port that seals injected synthetic journals before request-end transforms; it never modifies production code or the fault probes. The original Opus probe requires no U1 adaptation because it already chooses fresh outputs.
- Honor T4/T7 and the exclusion-only scope. Leave analysis/harvest, primary results, thresholds and registration unchanged; write only this report and its script directory. Do not update lead-owned project-state files.
- Report the runtime-exposed model family honestly. An exact deployment id is unavailable; neither the requested filename nor the seat nickname establishes one.
