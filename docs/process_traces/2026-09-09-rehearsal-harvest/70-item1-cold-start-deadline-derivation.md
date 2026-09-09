```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Located committed cold-start evidence and verified the 300-second derivation; capture-machine and producer-version provenance remain unverified.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "0656bb98bcc8103383b0b65085f5b1e448b5627b",
    "head_end": "0656bb98bcc8103383b0b65085f5b1e448b5627b",
    "upstream_end": "0656bb98bcc8103383b0b65085f5b1e448b5627b",
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-09-rehearsal-harvest/70-item1-cold-start-deadline-derivation.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.NightDriverTests.test_courier_deadline_is_derived_from_the_measured_artifact",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The requested desk report is complete; item 1 remains OPEN-NEEDS-CAPTURE-PROVENANCE because the recorded JSON does not attest the night-driver machine or executing script version.",
      "needs": "Lead locates capture provenance or arranges a fresh traced measurement outside any armed night or quiet window, then updates the kernel evidence pointer."
    }
  ]
}
```

## Change

Item 1 disposition: **OPEN-NEEDS-CAPTURE-PROVENANCE**.

The deadline derivation itself is verified. This report supplies the missing written arithmetic and corrects trace 61's unsuccessful JSON lookup, without treating unrecorded capture provenance as verified. No code, kernel, other acceptance item, or historical evidence was changed. No commit or Claude invocation was performed.

### Located evidence and provenance

The repository contains one `cold_start.json`:
`docs/process_traces/2026-09-01-unattended/cold_start.json` (lines 1–41).
Its recorded values are `durations_ms: [5450, 6300, 5007, 5303, 5250]` and
`median_ms: 5303`. It also contains 29 Gmail tool names, including
`mcp__claude_ai_Gmail__send_message`. The JSON has exactly the three keys
`durations_ms`, `gmail_tool_names`, and `median_ms`.

- Commit custody: introduced by `9a3f2cdc843cc69039486525233ee25985e43956`,
  author/commit date **2026-09-01 22:09:05 -0700**. Its subject says
  “claude -p cold-start evidence (median 5303 ms over 5 runs; Gmail send tool
  available headless) — COURIER_DEADLINE_S = 600 kept”. That last clause is
  historical; the current constant is 300.
- Recorded author identity: `Ed R <edr@Eds-MacBook-Pro.local>`. This is Git
  author metadata, **not proof of the capture host**. The JSON has no machine
  identity or measurement timestamp; the commit date is not an exact capture date.
- The commit trailer records Claude session
  `https://claude.ai/code/session_01YFcyS94GeJxpyFGBjPAHx4`. Its contents were
  not accessed; it is a provenance locator, not verified execution evidence.
- JSON Git blob: `9ca256e9c22112435cfd615bfb6e7e9ff3c5c2e7`.
- Producer implementation: `scripts/measure_claude_cold_start.sh` loops five
  times over `claude -p 'Reply with exactly the word READY.' --output-format text`,
  requires each reply to equal READY, computes elapsed milliseconds, then makes
  a sixth Claude call for Gmail tool names and writes `statistics.median(durations)`.
  Its current Git blob is `c1225c6d873ae8e5720abca98e286428abe5f3c3`, also present
  in implementation commit `5a130d437623432f8ea40fe96f1b6db244c6d6db`
  (2026-09-01 21:40:27 -0700), found through `git log --all`.
  The script entered mainline in `8c802bde083a8d69776930e34394f79e1749f513`.
  The evidence-introduction commit's tree has **no entry** for this script.
  Its availability on another implementation history and matching output shape
  do not prove which script bytes produced the JSON. No producer-version field,
  raw READY replies, or invocation transcript is attached to the JSON.

The broad requested search finds one measurement artifact, its producer,
consumer/test, ruling/brief/review references, and unrelated paper/statistics
`median_ms` matches. Full pre-write search census appears below. The hidden and
ignored filename census also found only this JSON and the producer script;
this conclusion concerns this worktree, not every off-repository custody root.

### Ruled formula and current implementation

Authority: `docs/decision_log.md` D-169 supplies the unattended-loop charter;
the numeric rule is in
`docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`,
R-7, lines 145–149:

> WO-2 measures a cold `claude -p` start on this machine and the deadline constant is set to
> `max(3 × measured, 300)` capped at 600, recorded in the trace.

The explicit unit conversion and correction are in
`docs/process_traces/2026-09-01-unattended/wo2-gauntlet/brief-wo2-fix2.md`,
S-a, lines 114–119:

> `min(600, max(3 × measured, 300))` with `measured` = `median_ms / 1000`

That brief names this JSON and directs 5303 ms → 300, a source comment and
an artifact-reading test. The prior 600-second defect is recorded in
`wo2-gauntlet/124-opus-wo2-refute.md` S1; the correction is recorded in
`wo2-gauntlet/127-sol-wo2-fix2.md` S-a. These are under the same unattended trace directory.

Arithmetic, independently recomputed from the JSON:

```text
sorted samples (ms): 5007, 5250, 5303, 5450, 6300
median_ms = 5303
median_s = 5303 / 1000 = 5.303
3 * median_s = 15.909
max(15.909, 300) = 300
min(600, 300) = 300 seconds
```

Current `scripts/run_night.py:50–53`:

```python
# R-7: min(600, max(3 * (5303 ms / 1000), 300)) from cold_start.json.
COURIER_DEADLINE_S = 300
COURIER_BACKOFF_S = (60, 180, 600)
COURIER_LOCK_FRESH_S = COURIER_DEADLINE_S + max(COURIER_BACKOFF_S)
```

The 300-second floor dominates. No measured send latency or retry duration
is added to the ruled formula. Trace 62 §Q3's parenthetical “cold start + send +
COURIER_BACKOFF_S retries + margin” is not the numeric rule; backoff is a separate
constant. The derivation does not establish an empirical worst-case email bound.

`tests/test_run_night.py:1184–1190`,
`NightDriverTests.test_courier_deadline_is_derived_from_the_measured_artifact`,
loads this exact committed JSON, divides its median by 1000, calculates
`min(600, max(3 * measured, 300))`, and asserts equality to the driver constant.
The focused test passed here. It does not authenticate the measurement host,
script invocation, READY outputs, or Gmail tool availability today.

### Remaining acceptance evidence and next exact step

`docs/process_traces/2026-09-09-rehearsal-harvest/61-coldgate-ruling-second-stub-night.md`
§Q3 requires a JSON produced by this script **on the night-driver machine**, a
custody/trace path named in the kernel row, and the formula linkage.
`62-coldgate-opus-refuter-second-stub-night.md` §Q3 correctly locates the JSON;
`21i-rehearsal-20260909-harvest-record.md` item 1 under
`docs/process_traces/2026-09-02-hands-free-week/` records NOT re-verified.
The committed JSON and arithmetic are now located and checked, but this desk
search did not establish the capture host or exact executing producer revision.
Thus CLOSED-BY-DERIVATION would overstate the full cold-gate condition.

The lead's next step is to recover a capture transcript/attestation binding the
existing five samples to the night-driver machine and producer revision. If that
cannot be recovered, a lead-controlled fresh capture can use this exact command
from the repository root, after verifying the destination is unused:

```sh
zsh scripts/measure_claude_cold_start.sh docs/process_traces/2026-09-09-rehearsal-harvest/item1-recapture/cold_start.json
```

**NOT RUN.** This command launches Claude agent sessions. It must never run
while a night is armed or a quiet window is open, and must not be run by this
Claude-origin delegated session (zero remaining bridge hops). The proposed
output is outside this session's write scope; only the lead may authorize and
perform that follow-up. Preserve the existing JSON. Trace the actual capture
time, machine identity, producer Git blob and invocation alongside any new JSON,
recompute the deadline, and point the kernel row at the accepted evidence.
No scope expansion is needed to complete this requested report.

## Verification notes

Docs-only task: focused artifact test and read-only arithmetic inspection were
proportionate; the full code suite was not run. All five sample values, median,
formula, constant and 29-name count agree. No live measurement or email was attempted.
`git diff --check` returned exit 0 with no output. Because the report is new and
untracked, a separate report whitespace check also checks its actual bytes.

Command tails (observed):

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night.NightDriverTests.test_courier_deadline_is_derived_from_the_measured_artifact
.
----------------------------------------------------------------------
Ran 1 test in 0.013s

OK

$ git ls-files | rg -i cold_start
docs/process_traces/2026-09-01-unattended/cold_start.json
scripts/measure_claude_cold_start.sh

$ git ls-tree 9a3f2cdc843cc69039486525233ee25985e43956 scripts/measure_claude_cold_start.sh
(no output; exit 0)

$ git diff --check
(no output; exit 0)
```

Pre-write complete content-search path census (exit 0; sorted for readability):

```text
$ rg -l 'median_ms|cold_start' docs scripts joulewise tests configs | sort
docs/paper/figures/fig4-verification.md
docs/paper/results-fill-registry.md
docs/paper/round7/anchor-correction-quantified.json
docs/paper/round7/dg071-dg075-statistics.json
docs/paper/round7/excursion-decomposition.json
docs/process/NIGHT_HANDBACK.md
docs/process/state_kernel.json
docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md
docs/process_traces/2026-09-01-unattended/cold_start.json
docs/process_traces/2026-09-01-unattended/wo2-gauntlet/124-opus-wo2-refute.md
docs/process_traces/2026-09-01-unattended/wo2-gauntlet/brief-wo2-delta2.md
docs/process_traces/2026-09-01-unattended/wo2-gauntlet/brief-wo2-fix2.md
docs/process_traces/2026-09-01-unattended/wo2-gauntlet/brief-wo2-night-driver.md
docs/process_traces/2026-09-02-coldgate-dx-t26a/diff-fence-main-to-3f1677b7.patch
docs/process_traces/2026-09-02-dx-registry/01-landing-brief.md
docs/process_traces/2026-09-02-dx-registry/02-sol-174-landing-report.md
docs/process_traces/2026-09-02-dx-registry/19-opus-counter-review.md
docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md
docs/process_traces/2026-09-02-hands-free-week/11a-exhibit-ruling-unattended-stage1.md
docs/process_traces/2026-09-02-hands-free-week/21i-rehearsal-20260909-harvest-record.md
docs/process_traces/2026-09-02-paper-d-dg071/04-sol-169-landing.md
docs/process_traces/2026-09-02-paper-d-dg071/06-luna-178-contract-refute.md
docs/process_traces/2026-09-02-paper-d-dg071/08-sol-180-fix-round-1.md
docs/process_traces/2026-09-02-paper-d-dg071/13-opus-246-physics-refute.md
docs/process_traces/2026-09-02-paper-d-dg071/18-fix-round-2-disposition-and-reissue.md
docs/process_traces/2026-09-02-paper-d-dg071/20-terra-248-delta-2.md
docs/process_traces/2026-09-02-paper-d-dg071/21-delta-2-disposition.md
docs/process_traces/2026-09-02-paper-d-dg071/22-opus-249-counter-review.md
docs/process_traces/2026-09-02-paper-d-dg071/25-sol-250-coverage-consult.md
docs/process_traces/2026-09-02-paper-d-dg071/30-terra-252-delta-3.md
docs/process_traces/2026-09-02-paper-d-dg071/34-coldgate-synthesis-fix-round-4-and-reissue.md
docs/process_traces/2026-09-02-paper-d-dg071/36-fresh-pass-disposition-and-reissue.md
docs/process_traces/2026-09-02-paper-d-dg071/37-terra-254-fresh-pass-2.md
docs/process_traces/2026-09-02-paper-d-dg071/43-integration-replay-and-terminal-review-e7425eef.md
docs/process_traces/2026-09-02-paper-e/02-refuter-fact-registry.md
docs/process_traces/2026-09-04-fanout/one-name-sweep/010-delta-reaudit-rescope.md
docs/process_traces/2026-09-05-paper-m/02-refuter-fact.md
docs/process_traces/2026-09-05-paper-m/05-counter-review-opus.md
docs/process_traces/2026-09-08-handoff-redo/09-coldgate-packet-rehearsal-authority/exhibit-D-d169-fences.json
docs/process_traces/2026-09-09-rehearsal-harvest/60-excerpt-21i-acceptance.md
docs/process_traces/2026-09-09-rehearsal-harvest/60-excerpt-kernel-night-rehearsal-01.json
docs/process_traces/2026-09-09-rehearsal-harvest/61-coldgate-charge-second-stub-night.md
docs/process_traces/2026-09-09-rehearsal-harvest/61-coldgate-ruling-second-stub-night.md
docs/process_traces/2026-09-09-rehearsal-harvest/62-coldgate-opus-refuter-second-stub-night.md
docs/process_traces/2026-09-09-rehearsal-harvest/65-magistrate-synthesis-second-stub-night.md
docs/process_traces/2026-09-09-rehearsal-harvest/67-arm-runbook-rehearsal-20260911.md
scripts/issue_dg071_dg075_statistics.py
scripts/measure_claude_cold_start.sh
scripts/paper_excursion_decomposition.py
scripts/run_night.py
tests/test_issue_dg071_dg075_statistics.py
tests/test_paper_round7_artifacts.py
tests/test_paper_terms_lint.py
tests/test_run_night.py
```

## Residual risk

Capture provenance and the lead-owned kernel evidence pointer remain to be resolved;
this report closes only the arithmetic/evidence-location gap. It does not close
NIGHT-REHEARSAL-01 overall or authorize any night.
