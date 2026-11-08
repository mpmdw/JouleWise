# Timing reader cold-review fixes — 2026-11-08

Branch: `fix-timing`. Base:
`dfde96979316949350cb01e9a7dcbabd48e9ccf6`
(`origin/perf/2026-11-08-r0-timing`). Implementation/tests:
`58f98632f`. The subsequent documentation commit contains this report and
`docs/perf/TIMING-RECEIPTS.md`; its hash is in the final handoff. Local only.

## Authority and scope

Applied Branch 2 of
`origin/perf/2026-11-08-opus-review-ci-timing:docs/perf/2026-11-08-opus-review-ci-timing.md`.
Read repository AGENTS/CLAUDE conventions, Mission M0, generated stop-card /
restart, current status/workspace/queue and do-not-do sections, orchestration,
the existing reader/report and targeted decision-log authority (including
D-009's stdlib/optional dependency policy). No active stop card. The direct
brief selects this offline engineering task and overrides ordinary state
registration/update and full-suite requirements. Initial tree clean.
No delegation, consult, integration install or network operation.

RUN_STATE, TASK_QUEUE, state kernel, `tests/test_gen_state.py`, capture code,
registration and stored evidence are unchanged. No real records, sealed
outcomes, measurement paths, model weights or analysis pipeline were used.
Embedded absolute data paths were treated as text only. The long-running
analysis job was not inspected, signalled or changed. No process census or
quiet-machine operation ran. Git used the allowed local object store; no
fetch or push.

## Findings, disposition and files

- **HIGH-B1:** `joulewise/align/window_timing.py` retains a valid explicit
  mapping across paired-stamp drift. It preserves recorded uncertainty,
  exposes signed drift/ppm and conservatively adds absolute drift to the
  reader's placement uncertainty. Paired-stamp-only fallback rejects drift
  only above bracket uncertainty plus `max(1 ms, 20 ppm * elapsed)`.
  Conflicting/invalid mappings and out-of-member placement still refuse.
- **MED-B1:** incomplete lifecycles use the minimum/maximum valid event
  timestamps as the member's observed bounds, with an explicit
  `event_envelope_incomplete_run` basis and `member_wall` still unavailable.
  A shifted episode cannot expand that envelope; no events means no episode
  placement.
- **MED-B2:** native G0 epoch entry/exit stamps place `g0_release_wait` under
  gates. Explicit release envelopes and nested `os_batch_wait` measured
  boundaries also place labelled gates activities, with the inner gate
  refining its parent. Chronological gaps include superseded attempts and
  bound wait placement. Duration-only `os_batch_wait_s` remains **requested,
  unmeasured**. With no release, its inferred pre-attempt position is a table
  annotation only, excluded from measured wall and bounds. With a release,
  the request stays unplaced. Bare G0 monotonic stamps never become epoch.
- **LOW-B1:** retained the authorized custodian's unblinded R1/W1/D export
  boundary. Blinding remains procedural; whole source blobs are parsed by
  the existing reader. No new outcome fields are selected.
- **LOW-B2:** driver/chain warnings use the duration-scaled diagnostic
  allowance and report ppm, suppressing ordinary ~9.2 ppm drift noise.
- **LOW-B3:** a lone chain exit (or start) is independently included in the
  observed envelope; an exit's unknown tail remains in the ledger.
- **LOW-B4:** worksheet labels distinguish disjoint decode excluding tools
  from native R1 `phases_s.decode`, which subtracts holds but includes tools.
  Numeric decode accounting remains unchanged.
- `tests/align/test_window_timing_opus_witness.py` promotes the review's two
  Branch-2 witnesses, keeping their test names and original assertions, and
  extends them to 17 synthetic regression tests. Branch 1's CI plan-replay
  script is outside this task and was not promoted.
- `tests/align/test_window_timing.py` updates the prior request-placement
  assertion for the explicitly unmeasured annotation. Its clock-step refusal
  case now exercises the paired-only fallback; the new regression module
  separately proves the requested mapped-step diagnostic behavior.
- `docs/perf/2026-11-08-eng-timing.md` documents current semantics and marks
  its old benchmark/hash as historical.
- `docs/perf/TIMING-RECEIPTS.md` proposes the minimum boundary/event shape and
  checked file:line insertion anchors for arm, each guard wait, cool-down,
  dwell, launcher barriers, stage settle, finalize, offload and push. It
  covers overlap, refusal/crash missingness and the impossibility of a push
  containing its own completion receipt. It is a design note, not capture
  authority or an implemented sidecar reader.
- This report records the handoff instead of modifying lead-owned state.

## Verification

All test invocations ran **one module per process**, sequentially, with
Python 3.13 and `-B`; total test time was far below the 20-minute limit.

| Command/check | Result |
|---|---|
| Baseline `python3.13 -B -m unittest tests.align.test_window_timing` | 25 PASS, 2.308 s |
| Imported original `python3.13 -B -m unittest tests.align.test_window_timing_opus_witness` before fixes | Both original witnesses FAIL as reviewed: `episode_clock` unavailable; 100 s window inflated to 1,058 s |
| Final `python3.13 -B -m unittest tests.align.test_window_timing_opus_witness` | 17 PASS, 0.019 s |
| Final `python3.13 -B -m unittest tests.align.test_window_timing` | 25 PASS, 2.113 s |
| Final `python3.13 -B -m unittest tests.align.test_window_timing_r0` | 14 PASS, 0.774 s |
| Final `python3.13 -B -m unittest tests.align.test_records` | 4 PASS, 0.011 s |
| AST parse of changed reader and two test modules | PASS |
| Receipt-note anchors printed from the unchanged producer source | PASS; corrected draft anchors before commit |
| `git diff --check` and staged diff check | PASS |
| `python3.11 -B -m unittest tests.align.test_window_timing_opus_witness` | NOT RUN: interpreter not installed (`command not found`, exit 127) |

The focused tests cover the two forcing defects, 120 s / 1 h / 16 h ordinary
drift in both mapping paths, fallback uncertainty and large-step refusal,
explicit mapping retention, missing/partial member events, chain tail,
positive/negative ordinary envelope drift versus abnormal drift, tools present
and absent, native G0 clock domains, measured versus requested waits,
superseded-attempt chronology, malformed/reversed/out-of-gap waits and exact
disjoint reconciliation. Existing tests retain the integer-grid partition
oracle, independent scan/report/worksheet equality, synthetic Git/CLI safety
and R0 integration coverage. No live timing or performance benefit is claimed.

No full suite, quick-suite discovery, Block-5 analysis, capture, model
download or hardware test ran. No MLX code/import changed, so **no new native
MLX test is required** for this stdlib reader fix.

## Uncertainty and next exact step

The 20 ppm allowance is an explicit engineering diagnostic choice with margin
over the review's ~9.2 ppm observation, not a calibrated clock bound or a new
measurement acceptance rule. Adding drift to an already bounded mapping is
deliberately conservative and may double-charge drift already covered by the
native uncertainty; both the original and reader uncertainty are exposed.
Incomplete member wall totals describe observed event coverage, not a proven
complete run. Requested sleep positions and missing release pre-roll/startup
cannot establish measured chronology. Non-bracket model attempt interiors
remain unknown unless member bundles supply detail.

Lead next: review these local commits and run the four focused modules above
with Python 3.11, one module per process. Separately review/register the
receipt design before changing capture producers or generated chain bytes.
Only an authorized custodian may subsequently prepare an unblinded timing
export; this session did not do so. No additional user ruling was needed to
complete this reader/design-note scope, and nothing was pushed.
