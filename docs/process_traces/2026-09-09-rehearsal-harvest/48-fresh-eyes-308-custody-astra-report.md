```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Four should-fix findings: false green-class claim, widened replay waiver, missing retry logs, and unsupported activation provenance.",
  "workspace": {
    "base_requested": "5d13d0e6",
    "base_mode": "exact",
    "head_start": "0931691e61d50a607b9b296c6f1528d1cc7e7b01",
    "head_end": "0931691e61d50a607b9b296c6f1528d1cc7e7b01",
    "upstream_end": "83ab38edcacd67312171c0051cc31cc70a9be682",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 4, "nit": 0},
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": "docs/process/state_kernel.json",
        "line": 2361,
        "summary": "Fixture status_note falsely claims a green class rerun and substitutes a different addendum obligation."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "path": "docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md",
        "line": 703,
        "summary": "The pointer widens the judge's exactly-four-failures waiver to four-or-fewer."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "path": "docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md",
        "line": 692,
        "summary": "The asserted 4/4/3 retry counts cannot be verified against 39b logs because those logs are absent at this head."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "path": "docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md",
        "line": 671,
        "summary": "New activation, email, and process claims lack corroborating captured artifacts at this head."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff 5d13d0e6..0931691e -- tests/test_gen_state.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "     def test_d176_ruling_installs_build_start_and_live_close_graph(self):",
          "         # 2026-09-08 D-176 §5: this proves the installed scheduling boundary,"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "D-176 §5"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --exit-code 5d13d0e6..0931691e -- docs/process/NIGHT_HANDBACK.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"]
      },
      "expected": {"exit_code": 0, "tail_regex": "using /tmp instead"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": []
}
```

## Findings

1. **F1 — Kernel note contradicts the recorded reruns.** At `state_kernel.json:2361`, the sentence says:

   > “Addendum obligation (44 C3 as synthesized by the magistrate): PR #308's ledger row 9 carries the failing tail AND the green class re-run tail from the same session; when this cure merges, record the four tests green under simulated slack as a dated addendum.”

   Trace 45 records **one test** green and requires a green **71-test class** rerun before merge. Trace 37 and trace 42’s addendum explicitly say that condition was unmet: three class reruns failed **4/4/3**. The durable pointer agrees with those traces. Additionally, 44 C3 requires the class rerun on then-current main; trace 37’s synthesis retains that requirement. Four tests under simulated slack are separate cure acceptance evidence, not the recorded class-rerun obligation. Correct the kernel note and regenerate its two queue projections.

2. **F2 — The pointer broadens the judge’s waiver.** At `00-DURABLE-STATE.md:703`, “exactly-the-four-or-fewer-and-nothing-else is the judge’s door” conflicts with 44 Q2/A1:

   > “failures = **exactly** the set”

   The judge further says:

   > “If the replay for #309 shows anything other than exactly the four, it holds for a green replay or a fixture cure regardless of this ruling.”

   Trace 31’s A6 addendum preserves exactly four. One to three failures are not authorized by that exception. Restore the exact condition; retain the refuter’s separate rc=0 position.

3. **F3 — Retry counts lack their named primary evidence.** The pointer’s **4/4/3** matches traces 37 and 42, but no `39b` retry logs—or original `39` class logs—exist in this checkout or its committed harvest tree. File inventory returned `disk_39_logs= []`. These counts are corroborated narration, not independently verified command tails. Capture the logs or qualify the pointer accordingly.

4. **F4 — Activation provenance is asserted beyond captured evidence.** The committed watchdog excerpt ends before activation 2145630c. It cannot verify seq **24/26–27**, attempt **6**, epoch **1788952084**, pid **93094**, empty pending notices, or acknowledgment. A trace-wide search found no independent matches for email IDs **1a085dce5c24086d**, **1a085cd2a5d5a2d5**, or **1a086405105b8214**. The address anomaly, resend/correction, “every other magistrate email,” and universal child-termination/waiting claims also lack captured supporting records. Preserve these as explicitly lead-reported observations or attach the relevant artifacts.

**Disposition by requested item:**

- **1 — Structural PASS; semantic F1.** Both new rows have the reference row’s keys and acceptance/authority shapes; self-pointers resolve; authority paths exist; fences have valid `authority`/`rule` structure. Exactly two tasks were added, no existing task changed, total **159**. Each note occurs verbatim in both queue tables. Inspection tail: `PASS: 159 tasks; schema, pointers, authorities, fences; each note verbatim twice`. Generator check: **rc 0, empty output**.

  The causal sentence correctly reflects 45:

  > “the failure is a flaky wall-clock coupling, not a machine-state defect — the same test returned OK on the same tree minutes later with pmset powermode 1 still set”

  The recommendation sentence also preserves dissent without installing a gate:

  > “The paired refuter 45 dissents from GATING on powermode (it was shown not to be the cause of the local test failures); the judge's constraint therefore stands as a RECOMMENDATION to Ed, not a gate: prefer powermode 0 for real or pack-bound nights until the calibration corpus's powermode is recorded; REHEARSAL_STUB nights are unaffected.”

  Those passages do not overstate the documents’ stated positions. The green-class/addendum sentence does.

- **2 — PASS.** Test diff contains only the two requested IDs and **157 → 159**, with its accompanying count comment updated.

- **3 — F2–F4.** Git history supports **e348a2c3**, **63a2739f** → cherry-pick **2aae25f6**, **191f4c43**, and **5d13d0e6**. Cure head **5db38b58**, PRs **#308/#309**, historical count **157**, review count **3 should-fix/4 nits**, and replay **5636 tests/4 failures/shard 4** agree with the cited traces. `NIGHT_HANDBACK.md` has no custody-delta change: **rc 0, no diff**.

- **4 — Same signature present.** Pair: kernel/queue **“green class re-run tail”** versus durable pointer and traces 37/42 **“three class re-runs stayed red (4/4/3)”**. A second pair is pointer **four-or-fewer** versus ruling 44/trace 31 **exactly four**.

## Residual risk

Review covered the requested delta and supporting artifacts at the pinned head. No live email, machine-state, or GitHub verification was performed. No files changed; final checkout remained clean.