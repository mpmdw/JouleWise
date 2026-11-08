# Record-only ALIGN timing worksheet — 2026-11-08

Branch: `perf/2026-11-08-eng-timing`; base: `50c99e4f8`
(`origin/align/2026-11-08-v4-r11`). Engineering only; synthetic evidence.

Delivered `python -m joulewise.align.window_timing`: a stdlib-only reader of
explicitly named **committed regular Git blobs**, with worksheet and JSON
output. No capture imports, discovery of run directories, filesystem reads of
record paths, LFS downloads, network, or following paths embedded in records.
It pins the requested local ref to a commit, records input SHA-256/byte counts,
rejects forbidden path components and Git symlinks, and ignores working-tree
edits. Originals remain unchanged; redirect derived output to a new location.

Authority: latency synthesis §4 rank 2 and its rows #3/#8/#13/#14/#23,
D1/D6/D7/D10, read from `origin/perf/2026-11-08-latency-synthesis` and the
four cited Sol audit branches. M0 intake found no active stop card. This brief
selects an offline engineering lane; its explicit state-file and full-suite
prohibitions override normal close-out bookkeeping. No coordination state or
existing files changed. No agent delegation, live operation, scientific rule,
registration, threshold, estimator, capture code, or analysis pipeline changed.

## Inputs and accounting

| Existing record | Interpretation |
|---|---|
| `chain-stages.jsonl` | Native stage start/end, kind, rc; calibration/derivation scaffold, verdict finalize, backup offload. Collection stays unattributed until member detail is supplied. |
| `r1_result.json` | Native epoch-ns attempt envelopes, including superseded attempts; bracket/soak contexts; chronological pre-attempt gaps, measured wait/release boundaries and separately labelled requested `os_batch_wait_s` and overlapping `result.phases_s`. |
| `night/result.json`, `chain.started`, `chain.exited` | Observed driver and supervised chain boundaries; wall/monotonic elapsed cross-check. Last stage end never substitutes for missing chain exit. |
| `night.log` | ISO-stamped driver-start → gate-verdict admission aggregate; more specific timed receipts refine it. Other windows' log rows are rejected when driver bounds are supplied. |
| Each bundle's `metadata.json`, `events.jsonl`, `outputs/align_episode.json` | Member identity; prepare/idle/warmup/measured/cleanup/reduce spans; prefill/decode/tools and G0/G1/H intervals. No power values, energies, correctness outcomes or detector scores enter the calculation. |
| Existing timed JSON via `--span PHASE=PATH` | Explicit phase annotation for arm/dwell/finalize/offload, etc.; requires recorded boundary pairs. A single timestamp or configured duration is insufficient. Native timed `clean_dwell.json` is supported. |
| Frozen plan JSON | `t0_epoch_s` and `window_max_s` define the ceiling, **never** observed wall time. |

Integer-ns, half-open intervals partition the **observed envelope of the named
sources**. Sum of phase durations equals envelope wall exactly; member ledgers
reconcile independently. Parent stage envelopes are refined by controller
stages, turns, tools, and gates/holds. Reference stages require explicit
`--stage-phase STAGE_ID=references`; reference activity still appears as
decode/prefill/gates/etc. in the activity ledger. Equal-priority conflicts and
overlapping member ownership become unattributed wall with source locators.
Unrecorded inter-member gaps remain unknown, never assumed cooling or idle.
Stage/attempt envelopes and raw gate receipts are inclusive diagnostic tables;
do not add them to the disjoint totals. Deadline tail is an overlay only.

After the Opus review, R1's native `g0_release.g0.entry_epoch_s` /
`exit_epoch_s` place the G0 wait as a labelled gates activity. An explicit
outer release envelope additionally places its startup/pre-roll/teardown
context; the inner gate refines it without double counting. Explicit timed
`os_batch_wait` objects are also placed. Bare gate monotonic stamps cannot be
treated as epoch. Each wait must fit the recorded pre-attempt gap, when both
attempts exist. The table includes the gap and recorded G0 wait duration.

`os_batch_wait_s` sums **requested, unmeasured** sleep delays. With no release,
the table shows `[started - requested_wait, started)` as an inferred request
position only; it never enters the measured ledger or extends its envelope.
With an intervening release it remains unplaced. A configured 65 s pre-roll
is never backfilled as a measured interval. Native R1 `phases_s.decode`
subtracts holds but includes tools; the reader's disjoint `decode` excludes
tools and gates/holds. Worksheet labels state the difference explicitly.

Missing first-token stamps do not become decode or prefill. Missing clock
mappings prevent episode placement unless native paired stamps provide a
labelled fallback. A valid explicit mapping is retained across paired-stamp
drift, with its recorded uncertainty preserved separately and absolute drift
added conservatively to the reader's placement uncertainty. Driver/chain
warnings use `max(1 ms, 20 ppm * duration)` and report signed ppm. The 20 ppm
diagnostic allowance accommodates the review's observed ~9.2 ppm ordinary
drift; it is not a measurement acceptance threshold. Paired-only fallback
refuses drift exceeding its bracket uncertainty plus that allowance.
Episode intervals outside member bounds remain unplaced. Without a complete
run start/finalize pair, the member uses its first/last valid event envelope,
labels that basis `event_envelope_incomplete_run` and keeps full `member_wall`
unavailable. No event bounds means no episode placement. A lone chain exit
still extends the observed envelope to include its unknown tail.
Nanosecond bookkeeping is not nanosecond acquisition precision: chain stage
timestamps have whole-second resolution. Future boundary receipts and exact
producer insertion points are proposed in [TIMING-RECEIPTS.md](TIMING-RECEIPTS.md).

The worksheet prints phase seconds/fractions, per-member phase/activity
shares, recorded turns/tokens, raw released/censored gate waits, attempt waits,
stage envelopes, unknown time, tail, ceiling/headroom, missingness, annotations
and provenance. Eligibility is explicitly unavailable: this reader does not
replace harvest or validate useful-turn completeness. A zero phase total
means no interval attributed, not proof that the activity took no time.
Only explicitly supplied members are covered; roster completeness is not
established. Full closure and next-arm turnaround need corresponding records.

## Synthetic timings and verification

The benchmark figures and hash below describe the original reader at
`44fb124cc`, before the review fixes and additional diagnostic fields/labels.
Current regression results are in
[the fix-timing report](../run_reports/2026-11-08-fix-timing.md).

Command: `python3.13 -B -m tests.align.benchmark_window_timing --members 22 --repeats 5`.
Python 3.13.18; 74 invented files, 60,616 input bytes, 338 disjoint window rows.
Single-process, in-memory parsing plus complete window/member accounting:

| Synthetic algorithm | Median, five runs |
|---|---:|
| Before: independent straightforward interval scan | 11.383 ms |
| After: sweep implementation | 6.972 ms |
| JSON rendering, one run | 1.994 ms |
| Worksheet rendering, one run | 0.389 ms |

The **entire report and worksheet are byte-identical** between scan and sweep.
Canonical compact JSON SHA-256:
`16c39b4d290f652d2ae0636a304eb4f072c8bc72b566ad7d60a5e3efec62c7c3`.
This is an algorithm comparison for a new reader, not a historical production
speedup or a capture-time saving. It excludes Git subprocesses, export, and
actual MBP I/O. The existing 8-worker job was neither inspected nor touched.

Failing-first: the initial targeted test failed with the missing module;
additional regressions failed before fixes for gate missingness, unrelated
log windows, R1 bracket classification, clock-step placement, overlapping
member ownership, and a shifted mapping that expanded the window. One initial
hand-counted fixture gap assertion was corrected from 27 to 21 seconds.

- `python3.13 -B -m unittest tests.align.test_window_timing`: 25 tests, PASS.
  Includes native-shape synthetic records, 80 seeded partition comparisons
  against an integer-grid oracle, full report/worksheet scan equality, torn
  and missing records, censoring, deadline-tail non-additivity, committed Git
  reads, unchanged inputs, CLI/library equality, forbidden paths and symlinks.
- `python3.13 -B -m unittest tests.align.test_records`: 4 tests, PASS (0.005 s).
- AST syntax check of all four new Python files and `git diff --cached --check`: PASS.
- No full suite, Block-5 analysis, real measurement reads, network or model
  downloads. No MLX code changed; no new native MLX gate is required for this
  reader. Python 3.11 was not run here; lead/CI must check it.

## Magistrate handoff

After a window closes, the authorized custodian should export only unblinded
R1/W1/D records into a new committed export, preserving originals. Supply all
members and map reference stage IDs from the frozen plan. Example placeholders:

```sh
python3.13 -B -m joulewise.align.window_timing --ref RECORD_COMMIT \
  --plan export/r1/plan.json --night-result export/r1/night/result.json \
  --chain-started export/r1/night/chain.started \
  --chain-exited export/r1/night/chain.exited \
  --chain-journal export/r1/night/chain-stages.jsonl \
  --r1-result export/r1/r1_result.json --bundle export/r1/runs/MEMBER
```

Repeat `--bundle` for each member; optionally add `--night-log`, existing timed
`--span` sources, reference-stage annotations, and `--format json`. Only use
flags for records that exist. Read no sealed Block-5 source. Run analysis on
the Air; **in an MBP gap only**, benchmark export plus Git-backed reader wall
and input size/count, then end all agent work before the next arm.

For D1, compare chain start/exit and all attempts with the assumed R1 bound.
For D6/#14, reconcile actual bracket/corpus/derivation/reference stages; absent
W1 stages in R1 stay unavailable. For #13, compare configured idle with recorded
idle and G0/G1/H; this does not establish a shorter idle's causal effect. For
#23, retain every batch wait and its missing placement. For D7, benchmark the
first recorded finalize/offload pair and next arm. For #3/D10, compare exit to
the **plan's** ceiling and inspect post-last-stage unknown time: an early exit
rules out idling to the ceiling **in that record**; an exit at/after the ceiling
does not establish its cause or prove anything about unobserved code paths.

Outstanding: independent fresh lead review; Python 3.11 targeted check; one
authorized committed-record run and MBP-gap I/O timing. No real R1/W1/D latency,
idle-to-ceiling conclusion, finalized custody baseline, or measurement saving
is claimed. Commit IDs are in the final handoff; nothing is pushed.
