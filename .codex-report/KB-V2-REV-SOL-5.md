GPT-6 (Codex; exact deployment model ID is not exposed to this session)
VERDICT: ACCEPT_WITH_FIXES

Executing blind review of `6847502b8..840137268e2c6f49fa369329a27f92de6c56a3f3`, mpmdw/JouleWise draft PR #593. This is a review, not admission of the rule. The session exposes the model family above, not a verifiable exact deployment ID; I have not inferred one from the implementer's brief.

## Numbered findings

1. **MAJOR — four of the 176 dismissed shrink flags are missing-support prerequisites, and a smaller numeric bound survives.** `scripts/bytes_stream_test.py:582` and `:587`. The reducer retains C3's central `x` after its idle support becomes insufficient, but checks uncertainty prerequisites only for S/C1/C2. It then uses that changed C3 mean in the residual and propagates a numeric half-width. An UNDETERMINED class does not remove the smaller printed bound.

   In the literal Opus twelve-row walk, shortening `records[2 or 5].harvest.idle.[pre or post].rails` to one row produces `rails insufficient native samples`, C3 `dx=None`, and rest UNDETERMINED, yet rest half-width decreases from **0.0011851819800064896** to **0.0011851202553169475 J/GB** (pre case). These four cases are deficient collections, not valid changed collections: they fail the reader's own native-support prerequisite.

   Repro:

   ```sh
   python3.13 -B .codex-report/kb-v2-rev-sol-5/short_support.py
   ```

   This also runs fresh CLIs with the full 576-row cadence. Its `jitter` baseline differs from the unchanged worked example only by 12 J of ordinary C3 rails-energy variation; both baseline and fault retain that same variation and all baseline classes are RESOLVED. The sole fault is replacing one C3 rails idle list by its second existing row. The 12 J is a synthetic input, not an acceptance bar. Output tail:

   ```text
   jitter pre calls 8 class UNDETERMINED rest halfwidth 0.0025572074458721024 -> 0.0025186057999666196
     C3 dx None reason idle variance not defined (rails insufficient native samples) native rails insufficient native samples
     printed 0.1262 ± 0.0026 -> 0.1262 ± 0.0025
   ```

   Preserve coefficients from the complete S/C1/C2 arms, but make the residual and propagated widths reasoned undefined when C3's support prerequisite fails. This is not only a label change: the malformed prerequisite shrinks a surviving bound and can move publication digits. The generated test mutates native support only in record 0 (S), so it misses this C3-specific path. The row-thinning change is not its cause; full-cadence input reproduces it. This remaining reducer path predates round 6; its classification among the 176 benign flags is incorrect.

2. **MINOR — a huge but binary64-representable number still aborts the reader and loses the record.** `scripts/bytes_stream_test.py:750`, with the incomplete exception handler at `:753`. Setting only `records[0].harvest.tau_s` to `10**308` (or `1e308`) passes the new accessor: its binary64 conversion is finite and its sign is valid. Multiplication by `1e9` overflows before `round`, and the handler omits `OverflowError`. The CLI exits 1 without its JSON record, including the seven unaffected calls. The input is the prior review's otherwise valid, compact, real-stream fixture.

   Repro from repository root, with the requested environment variables:

   ```sh
   python3.13 -B .codex-report/kb-v2-rev-sol-5/extreme.py
   ```

   Output tail:

   ```text
   tau_s int finite True accessor error None EXIT 1
     File "/workspace/JouleWise/scripts/bytes_stream_test.py", line 750, in read_known_bytes
       trim_ns = round(max(0,h["tau_s"]-receipt["settle_s"])*1e9)
   OverflowError: cannot convert float infinity to integer
   ```

   Route failed trim arithmetic through a reason naming `records[0].harvest.tau_s`, keep all evidence/calls, and leave affected quantities undefined. No replacement measurement or agreement bar is needed. This is a remaining, pre-existing overflow path, not a regression introduced by the delta. The implemented H1 conversion check and idle-statistics overflow handling themselves pass. MINOR reflects the extreme metadata required; this is record loss, not merely an undefined-result label.

## Executed

All commands used Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, from `/workspace/JouleWise`. Let `R=.codex-report/kb-v2-rev-sol-5`. No MLX, Metal, hardware measurement, admission, merge, or subagents.

Read Round 6, both complete prior reports and their scripts, the complete four-file delta, and the accessor, reader, scan, reducer and governing rule paths. The stop card is inactive. Repository changes are confined to this report and its evidence directory.

### Prior finding repros

- Sol `extra.py`: reversed native interval and `10**400` repeat count now exit 0, retain eight calls, and name the invalid prerequisite. Null scan status is reasoned. `extra.log` also retains its supplementary extreme-finite and timing-description probes.
- Sol `partial.py`: lost C3 retains `gamma_c=0.028000195821126284`, `alpha=0.0013999906666666668`, `gamma_d=0.09471662736453161`, `delta=0.06671643154340534`; these equal the independent recomputation from the retained arms. Class remains UNDETERMINED.
- Opus `probes.py`: run literally (`probes-literal.log`), then with a nonnegative equivalent of its real-stream harvest and only the obsolete numeric-bound display lookup adapted (`probes-positive.log`). Huge integers in reader/scan, finite idle `fsum` overflow, reversed/zero native rows, receipt order, fixed signs and malformed containers return reasoned records. The full 576-row rails support was used for the decisive native-order cases. No reader traceback occurs in these old finding scenarios.
- The literal old end-to-end fixture contains negative rails/GPU/adapter power, now correctly refused under H6. Its own display inspector consequently raises `KeyError: 'delta'`; literal `probes.py` also eventually indexes a correctly absent rails bound. Those are harness exceptions, not reader exceptions. The literal results are preserved. `build_fixture.py` repairs the waveform while preserving means and governed variances; the complete end-to-end harness and all targeted probes then finish. The finding above is separate.
- Opus `g2_lost_calls.py`: all 48 lost-call variants, **0 mismatches** (`g2.log`).

### Independent H1–H6 checks

`independent.py`: **5,002 cases, zero failures**, with sampled fresh read CLIs; `stamp_orders.py`: **384 positive reversed-poll cases PASS**. `independent-final.log` is the clean final walk. The extra representable-integer trim probe is the finding above, outside the walk's `10**400` conversion mode.

Complete prior Opus `leafwalk.py` at the exact target: **44,688 cases; 0 crashes, 0 lost calls; 461 sampled CLIs, all exit 0 with matching classes** (`leafwalk.log`). It reproduces exactly **176 shrink flags**. I inspected a representative of every normalized family (`classified-flags.log`), then replayed the deficient cases through fresh CLIs. Classification: **172 valid zero/signed measurements, adequate changed collections or record-index artefacts; 4 invalid short C3 rails-support cases (finding 1)**. Mode counts are deleted 80, zero 46, long 26, negative 18, short 5, empty 1. Four of the five `short` flags are the defect; the fifth shortens a valid gap collection.

I independently reproduced/classified six representative flags (`flag_examples.py`, `flag-examples.log`):

| Mutation | Example bound before → after | Classification |
|---|---|---|
| `r_max_s = 0` | DC half-width 0.0014630515 → 0.0014540357 J/GB | Valid zero synchronization bound; 20 ms term remains. |
| `anchor_shift_j = 0` | Call-0 rails edge 0.5388 → 0 J | Valid zero measured anchor shift. |
| `battery_edge_j[0] = -1` | Call-0 DC bound 31.7466894 → 30.7466894 J | Signed battery measurement expressly allowed by H6. |
| Gap `missing_samples = 0` | Gap bound 14.9527356 → 12.1527356 J | Valid nonnegative count changes the missing-time input. |
| Keep only the stream gap row | Gap bound 14.9527356 → 2.8 J | Changed collection: the pre-idle gap is no longer in the input. |
| Delete record 0 | Index-0 rails bound 1.5476645 → 1.0432395 J | Index artefact: new call 0 is old C1, not old S. All classes UNDETERMINED; compare surviving receipt identities, not list positions. |

None of those six flags is a malformed-prerequisite case.

The independent receipts are regenerated by the real `stream()` with fake arrays, written and reloaded. Eight 7.2 s rows per native idle family cover the same 57.6 s span; this differs from both the builder's four-row walk and Opus's twelve-row walk. Faults cover every retained row in every record, every receipt interval pair, every numeric leaf, every sign-fixed power/integral leaf, scan status null/wrong type, and compared disclosure leaves. Assertions require retained raw evidence and calls, no smaller surviving aggregate/per-call bound, named missing reasons for consumed prerequisites, unchanged disclosure classes/numbers, and sampled real-CLI agreement.

`scan_extra.py /workspace/JouleWise`: **594 cases PASS** across all 66 scan-receipt positions, including huge integers in each numeric prerequisite and nonpositive intervals.

H4: every one of the eight lost-call positions checked across all four boundaries. Losing S preserves `gamma_c`/`alpha`; losing C3 preserves those plus `gamma_d`/Delta. All equal baseline bit for bit. Losing C1/C2 leaves no coefficient whose prerequisites are complete. All classes remain UNDETERMINED and residual/uncertainty remain undefined where required.

Negative battery edge energy, battery stream energy, idle battery power and native battery-poll power remain accepted. Negative rails/GPU/meter powers and rails integral are reasoned missing prerequisites. Bad compared disclosure leaves preserve the valid rail set and all boundary numbers/classes.

### Fixture audit and numerical bars

`fixture_audit.py` builds the **old tests with the old reader** and the **new tests with the new reader**, then compares their actual generated inputs and outputs. The pulse repair changes raw rails waveforms, not receipts, integrals or governed moments: maximum mean discrepancy **1.3877787807814457e-17 W**, maximum governed-variance discrepancy **0**. Rails Delta/width change at most **1.0842021724855044e-19 J/GB**; DC/rest changes **0**. Every worked publication string, including GPU, is identical. Thus these are equivalent moments, not literally identical raw waveform samples.

Six constant 9.6 s rows versus four constant 14.4 s rows: Delta changes **0**; maximum width change **4.9873299934333204e-18 J/GB**. Lag count changes from 1 to 0, which is why the separate eight-row, twelve-row and full-cadence checks matter. Both constant fixtures have zero governed variance. The fixture changes preserve the tested numbers; finding 1 also reproduces with full-cadence support.

Unchanged worked output: **rails 0.06672 ± 0.00057, DC 0.1929 ± 0.0025, rest 0.1262 ± 0.0024 J/GB; share 0.3458 ± 0.0075** (`fixture-audit.log`, `e2e-positive.log`).

No new agreement bar was selected. The tests use the lead's **4.5e-7 GB/s** rational bar and **5.7e-6 J/GB** energy bar. Their derivations remain beside the checks/in the rule: 1% of 0.000045 GB/s and 0.00057 J/GB. The independently executed rational verifier gives **1e6 × float noise = 2.8793189825782006e-7 GB/s < 4.5e-7** (`rational.log`); the rule's propagated energy floor is **2.5e-10 J/GB < 5.7e-6**. Program-minus-independent energy differences remain within the specified bar. Exact equality checks concern output formatting, raw evidence retention, unaffected arm/coefficient identity, or identical native inputs to the same estimator; they do not introduce numerical agreement tolerances.

### Tests and CI

```sh
python3.13 -B -m unittest tests.test_bytes_stream_test tests.test_bytes_mac_kit
python3.13 -B -m unittest tests.test_bytes_h_session tests.test_repin
python3.13 -B scripts/repin.py --check
```

Reader/kit: **50 tests, OK, 2,124.604 s; 900 generated real-CLI faults**. This includes H8's identity-source test. The combined-module duration is about **1.47×** the prior reported 1,450.139 s, under the approximate 1.5× budget even while the independent walks ran concurrently. Generated faults are 900 versus 945; thinning and moment equivalence were independently checked above.

Session/repin: **73 tests, OK, 2,220.561 s** (36 session, 37 repin). Thus **all 123 requested tests pass** (`tests-stream.log`, `tests-session.log`).

`repin.py --check`: **PASS 16 pin families current**. `bytes_mac_kit.py --check`: **verified non-claim Mac kit**. No production files or pins changed. `git diff --check` passes. The whole repository suite was not run for this bounded review.

PR #593 metadata confirms the exact target head. [CI run 40898400381](https://github.com/mpmdw/JouleWise/actions/runs/40898400381), observed **2026-10-29 15:49:44 UTC** through the GitHub connector: **14 success, 6 in progress; no red job to attribute**. Complete CI is **not yet established green**. `ci.json` preserves job IDs and steps. Gate-ledger run 40898400566 is skipped for the draft.

| Job | State |
|---|---|
| changes | success |
| build | success |
| fences | success |
| installed-wheel | success |
| quick | success |
| calibration-exits-exclusive (3.13) | success |
| calibration-writer-crash-matrix-exclusive (3.13, 1) | success |
| calibration-writer-crash-matrix-exclusive (3.13, 2) | success |
| test (3.13, 1) | in_progress |
| test (3.13, 2) | success |
| test (3.13, 3) | success |
| test (3.13, 4) | success |
| test (3.13, 5) | success |
| test (3.13, 6) | success |
| test (3.13, 7) | in_progress |
| test (3.13, 8) | in_progress |
| test (3.13, 9) | in_progress |
| test (3.13, 10) | in_progress |
| test (3.13, 11) | in_progress |
| test (3.13, 12) | success |

## Decisions I made

- ACCEPT_WITH_FIXES for one MAJOR malformed-support bound shrink and one MINOR finite-arithmetic record-loss path; no BLOCKER found. H1–H8's named old scenarios are corrected. I did not promote output wording for already-undefined results to a numerical defect.
- Treat valid zero/signed measurements and adequately supported changed native collections as different inputs, rather than malformed prerequisites. Align records by identity when interpreting record-deletion index flags.
- Preserve literal old-fixture refusals and distinguish harness display exceptions from reader tracebacks. Use a documented nonnegative equivalent only for valid-input worked values and further fault probes.
- Compare fixture moments with measured discrepancies and the existing energy bar, and compare publication strings exactly. Do not claim raw pulse waveforms are identical.
- An early independent run incorrectly demanded disclosure for an unconsumed receipt copy of `telemetry_backend`; another sampled CLI comparison shared a scratch file with a concurrent walk. Corrected those harness errors and isolated scratch filenames before interpreting final results.
- Do not infer an unavailable exact model ID, claim pending CI green, admit the rule, or change production code. The cloud-environment runtime skill was used for environment/network inspection only.
