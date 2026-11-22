# Additional bundle cases under RL-202

Freeze 1 contributes 29 cases. Freeze 2 adds 30, for **59 distinct acceptance cases** across both manifests. All additions unpack the original synthetic bundle archive into a new directory. No second archive, embedded traces, alternate arithmetic or candidate implementation is needed. Run the original 29 as well. The separate directory preserves the original in-suite inventory verifier. [Original fixture and driver contract](../suite/README.md) · [RL-202 §6](../../fable-rl202.md)

| Ruling group | Cases and failure they distinguish |
|---|---|
| 1. Mapping width | Original filtered fit gives 24,000,000 ns. A nonzero 625,000 ns anchor spread adds that exact amount. The unfiltered 79 ms RTT gives exactly 100,000,000 ns and a mapping. The 80 ms RTT gives 101,000,000 ns and no mapping. Compare actual stage-1 H, every mapped timestamp, and the actual mapping delivered to the print. |
| 2. Seven non-ok codes | Fourteen cases. An isolated failure in L002, with no disposition, refuses fresh. Its eligible-code partner uses a signed test disposition bound to its exact certificate digest, leaves eleven numeric DC rows and keeps the rail qualifier. An attempted exception for either custody inconsistency must still refuse. The two ineligible-code partners make this an executable assertion. |
| 3. Restart | L002 lies wholly in stream 002 of its span. Use the second stream’s clock pairs, bracket and L002 baseline (12 W). The separate restart-inside-L002 case has two valid fits and no single bracket. |
| 4. Disposition identity | A disposition naming a different code, and one naming a healthy leg, both refuse before reservation. |
| 5. Hidden DC coverage | Removing L002/L005/L008 leaves three hidden legs and three levels. Removing L005/L012 leaves four hidden legs and two levels. Both otherwise-authentic dispositions refuse fresh. |
| 6. Reader contradicts certificate | A synthetic fault alters one interior decoded timestamp by 1 ns, preserving counts, endpoints and file digests. The real comparison fails after durable start. No public file, retry spent. |
| 7. Instrument/private output | G0 ends 1 ns inside the episode and gets exactly `leg_record_invalid`. Changing its verified input bytes at the reader boundary fails the whole look. The native 1.3 s rail-gap mutation retains the planted hidden joules and all fit members, and marks the three printed rails. Healthy cases omit the optional key. Matched zero-duration and zero-SD floors have zero joules, null units and null reason. A gap in the baseline window supplies the null reason on a zero-duration floor. Known and unknown instrument nulls use the pinned ctl list with the original instrument’s open reason field. |

## Inputs and oracles

`cases.json` names every case. `fixtures.py` partitions the native span stream by nonoverlapping monitor lifetimes when an isolated restart or failure is required. It keeps the recorded sample payload format and writes a header, polled batches and trailer for each closed stream. Negative cases can omit the trailer, mark a stream absent, move an anchor, change a poll RTT, split mid-leg, or duplicate a stream under a second receipt-listed name. Every deliberate pre-registration change is incorporated into the synthetic receipt and the independent test Check; mutations intended as damage after registration preserve the old pins. On a missing-meter leg the applicable monitor lifetime has the writer's absent header, zero polls and a trailer. Adjacent legs in that span still have usable streams.

The cutoff and dose oracles use planted times and fixed roster membership. A healthy 50 Hz point grid covers the last sample at/before episode start through the first at/after end. The sign is negative seven seconds. `dc_times_sha256` hashes concatenated signed 64-bit big-endian episode-time nanoseconds over that complete slice. This catches a moved interior sample even when the boundaries match. The synthetic capture uses long **real** durations on a fake clock, and source field projections for control records. Only a copy of the frozen archive is ever mutated.

The fallback vocabulary has SHA-256 `cbbab90b76b235c0d08fd89db0a65d738c74efbed5dd57e646cd169e26437d79`. At instrument commit `321357e43`, `Signals._stream_refusal` supplies rail_manifest, meter_absent and meter_contaminated. `_interval_refusal` supplies coverage and meter_gap. These can reach the hold mean or its dropped-window reasons. `deviation` and `_drift` emit fewer_than_two. The instrument-only catch in `_leg_values` replaces the entire member with interval_ledger_mismatch. The fallback accepts a legal null leaf in the ruled vocabulary under the pinned instrument shape, including the freeze-1 SD examples. A singleton ledger-mismatch member uses its separate form. A reason reachable only in gain, turn or edges has no place in this list. The ctl-only CPU reason belongs to the downstream floor calculation. `leg_record_invalid` belongs to a private ctl leg disposition. [Instrument hold writer](https://github.com/mpmdw/JouleWise/blob/321357e43/joulewise/cadence_looks/description.py#L1833) · [Whole-member branch](https://github.com/mpmdw/JouleWise/blob/321357e43/joulewise/cadence_looks/description.py#L2022) · [Vocabulary](../lm-ctl-01.hold-reasons.v1.json)

## Run

From the delivery root, with the public runner source at 043b972f9 on PYTHONPATH and a local public Git object database containing 321357e43:

```sh
shasum -a 256 -c SUITE.sha256
shasum -a 256 -c SUITE-v2.sha256
PYTHONPATH="$RUNNER_SRC" python3.13 -B suite/check_inputs.py
PYTHONPATH="$RUNNER_SRC" python3.13 -B suite-v2/check_vectors.py --repo "$PUBLIC_REPO"
```

`check_vectors.py` checks the source reason inventory, native receipts and actual decoder behavior on each distinct supplemental fixture profile. It cannot give a candidate an acceptance pass. On the authorized synthetic bench, run the implementation through both complete case sets:

```sh
python3.13 -B suite/run_suite.py --driver "$CTL_TEST_DRIVER"
python3.13 -B suite-v2/run_cases.py --driver "$CTL_TEST_DRIVER"
```

## Test driver extension

Use the original `OP SOURCE BENCH FAULT` interface, registered layouts and independent registrar. `install-v2` provisions the prospective ctl release against the pinned open instrument schema and the exact fallback-list bytes, and supplies the test registrar's identity. It must not derive the list from the fixture. The legacy `install` operation still sets up the precise frozen v1 test world. The suite contains no alternative worker.

- `project` runs the actual pinned time-only projector before stage 1. Store the actual private certificates under `BENCH/private/lm-ctl-01/certificates/Lnnn.json`; required fields for the comparator are `leg_id,dc_code,H_ns` and, when mapped, `stream,dc_times_sha256`. All other source/identity/close bindings from SPEC are still mandatory. A refusal for an unknown instrument hold at stage 1 is valid; the independent post-close timing projection needs no instrument data.
- `attest-disposition` authenticates the test issuer's exact `SOURCE/authority/disposition.json` under a **synthetic** authority established before looking at fixture values. It can sign an intentionally wrong claim. Production validation must reject it. The private inventory at each position includes `certificate.sha256` and `disposition_sha256` (the same document digest, or null). Stage 1 binds these through its existing inventory hash.
- On a successful read a bench-only observer writes `BENCH/joined-observed.json` from the actual DC trace/mapping at the reader-to-analysis handoff, keyed by each mapped leg id. Record the method, signed offset, uncertainty in ns and independently recomputed digest of mapped sample timestamps. Never copy the expected certificate or skip a verified leg because a later local scientific check failed. For disposed legs observe that no mapping is delivered. Probe the value-consuming calls in the time lexer and decoder too, so an accidental call during blind projection fails the inherited event-order oracle.
- `decoder_one_stamp` modifies a single interior fitted sample time on return from the real decoder in the test child, before the production comparison. `reader_corrupt_leg_bytes` returns the actual L002 original episode payload with one byte changed to the stage-2 digest verifier after durable start. The preflight, certificates, original stage-1 commitments and failure handling are real. Faults belong only to the isolated test instrument. A stage-2 stub which fabricates an expected result or exit is invalid.
- The suite reads the real private/public output files. A fresh refusal requires return code 2, the exact blind diagnostic, no claim, no read and no public files. A failure after start requires the inherited two-line notice and a spent retry. A successful exception must preserve the eleven numeric DC baselines, every other channel and the DC fit from the remaining approved hidden legs.

The frozen archive and checksum set cover source shape, channel availability, reported numbers, state and publication. Host registration, real close commitments, executive byte pass and the research lead’s decisions belong to the live release team. [Remaining gates](../OPEN.md)
