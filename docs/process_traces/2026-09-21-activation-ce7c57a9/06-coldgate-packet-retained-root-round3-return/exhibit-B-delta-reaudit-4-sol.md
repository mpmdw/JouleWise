# 04b — Sol delta re-audit 4 (high) on the round-3 head cfc56921, verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One should-fix documentation recurrence and one regression-coverage nit; all ruled-text comparisons match, four requested mutants die, and m16 survives.",
  "workspace": {
    "base_requested": "cfc569213f3f4a9b900f73564d1f76c43101a4f7",
    "base_mode": "exact",
    "head_start": "cfc569213f3f4a9b900f73564d1f76c43101a4f7",
    "head_end": "cfc569213f3f4a9b900f73564d1f76c43101a4f7",
    "upstream_end": "ecefd46ab3c3e4529baa4ffd390e98464e127e00",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "docs/phase_2/derivation_night_runbook.md",
        "line": 741,
        "summary": "The verbatim ruled replacement claims a symlink anywhere under a root causes refusal; an unrelated symlink under night/ still yields retained and pass."
      },
      {
        "id": "F2",
        "severity": "nit",
        "file": "tests/test_evidence_night.py",
        "line": 944,
        "summary": "The new regression pins reason wording but not the ruled assignment order: m16 moves the correct reason before parsing/span evaluation and survives all five mutation tests."
      }
    ],
    "merge_recommendation": "Do not merge; F1 is a same-signature recurrence requiring a new cold-gate packet under Q1 item 4."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -B -m unittest tests.test_evidence_night -k retained -k discovery -k span -k realpath -k deep_json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 9 tests in 16.385s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -B /private/tmp/r3-refuter-hqj_bzwo/fidelity.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Q2 handbook MATCH",
          "Q3 naming MATCH",
          "Q3 restored MATCH",
          "Q4 reason MATCH",
          "Q4 certification MATCH",
          "Q5 replacement MATCH"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Q5 replacement MATCH"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /private/tmp/r3-refuter-hqj_bzwo/mutations.py",
      "cwd": "/private/tmp/r3-refuter-hqj_bzwo",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "m8 KILLED rc=1",
          "m12 KILLED rc=1",
          "m14 KILLED rc=1",
          "m15 KILLED rc=1",
          "m16 SURVIVED rc=0",
          "Ran 5 tests in 3.475s",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "m16 KILLED rc=1"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 -B /private/tmp/r3-refuter-hqj_bzwo/probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["runbook one-liner night symlink rc: 1"]
      },
      "expected": {"exit_code": 0, "tail_regex": "runbook one-liner night symlink rc: 1"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3.13 -B /private/tmp/r3-refuter-hqj_bzwo/probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["runbook one-liner night symlink rc: 1"]
      },
      "expected": {"exit_code": 0, "tail_regex": "runbook one-liner night symlink rc: 1"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3 -B /private/tmp/r3-refuter-hqj_bzwo/kernel.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "kernel.json diff rc: 0 ",
          "RUN_STATE.md diff rc: 0 ",
          "TASK_QUEUE.md diff rc: 0 ",
          "gen_state --check rc: 0 stdout='' stderr=''"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "gen_state --check rc: 0"}
    },
    {
      "id": "V8",
      "kind": "smoke",
      "cmd": "zsh -f /private/tmp/r3-refuter-hqj_bzwo/handbook-fixture.zsh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "helper 200: TERM 200,201,202",
          "FIXTURE kill -TERM 200 201 202"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "FIXTURE kill -TERM 200 201 202"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "F1 repeats the ruled-text latent-defect and documentation/code-contradiction signatures.",
      "needs": "Return the lane to the cold gate with a new packet, as Q1 item 4 requires; do not start fix round 4."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Live pgrep returned rc 3: sysmond service not found / Cannot get process list. The recursive handbook probe used an explicitly simulated process tree.",
      "needs": "Lead retains responsibility for live process-tree verification."
    },
    {
      "id": "G3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The first filtered run on the package export passed eight tests but PrepareTests setup failed because the export was not a Git repository. The second and final filtered run in the worktree passed all nine tests.",
      "needs": ""
    }
  ]
}
```

## Findings

**Blocker: none.**

**F1 — Should-fix: the new runbook text overstates symlink rejection.**  
At [derivation_night_runbook.md:741](/Users/edr/code/JouleWise-wt-retention4-ce7c57a9/docs/phase_2/derivation_night_runbook.md:741), “a symlink anywhere under a root” is given as an example of a refusing condition. The classifier checks the plan and specific night-record paths; it does not recursively inspect arbitrary files (`joulewise/evidence_night.py:716–724`).

Executed:

```text
python3 -B /private/tmp/r3-refuter-hqj_bzwo/probes.py
python3.13 -B /private/tmp/r3-refuter-hqj_bzwo/probes.py
```

Both interpreters produced:

- A valid pre-span plan with two refusal markers: `classification="retained"`, `verdict="pass"`.
- The same root with `night/unrelated-link` pointing to one marker: still `retained`, `pass`.
- Replacing `night/` itself with a symlink: exit 1, `joulewise.evidence_night.Refused: symlink/path collision: …/night/courier.sent`.

Thus the original loop defect is fixed, but its replacement contains a new false claim. **Fidelity is MATCH:** the defect was copied from the ruling.

**One-line cure:** obtain a gate-supplied correction limiting the example to symlinks in inspected paths; Q1 item 4 requires a new packet, not another fix round.

**F2 — Nit: the tests do not pin the ruled reason-assignment order.**  
At [test_evidence_night.py:944](/Users/edr/code/JouleWise-wt-retention4-ce7c57a9/tests/test_evidence_night.py:944), the regression checks final classifications and reason strings. My m16 moves the **correct** retained reason to the initial assignment before parsing and removes the post-span assignment.

Executed:

```text
python3 -B /private/tmp/r3-refuter-hqj_bzwo/mutations.py
m16 SURVIVED rc=0
Ran 5 tests in 3.475s
OK
```

The current production code follows the ruling. This is a structural coverage gap, **not an observed output defect**: m16 is observationally equivalent for these cases. m15 dies because it also changes the string, so its kill does not independently establish assignment-order coverage.

**One-line cure:** if the gate retains assignment order as a regression requirement, add a focused order check and kill m16.

**Q1 — Closure table**

All locations refer to `cfc569213f3f4a9b900f73564d1f76c43101a4f7`.

| Finding | Status | Location and executed evidence |
|---|---|---|
| A1-F1 | **REGRESSED** | Runbook `:735` removes the divergent loop; symlinked `night/` now refuses through the binding classifier. New adjacent overclaim at `:741` fails the unrelated-symlink probe: F1. |
| A1-F2 | **CLOSED** | `joulewise/evidence_night.py:741`; test `:960`. Focused run passes; m14 dies with escaping `RecursionError`. Raw deep JSON becomes UNKNOWN on both 3.13.1 and 3.14.7. The regression verifies persisted failing `check.json`. |
| A1-F3 | **CLOSED** | `tests/test_evidence_night.py:976`; realpath comparison at code `:733`. Both spelling cases pass; m8 fails both with `'UNKNOWN' != 'ACTIVE'`. |
| A2-F1 | **CLOSED** | Kernel `:5`, `:1030`, `:3736`; completed rows at `TASK_QUEUE.md:113–114`. `--check` returns 0; regeneration and all three byte comparisons return 0. |
| A2-F2 | **CLOSED** | Code `:738–740`; contract `:241–246`; test `:944`. Pre-span fixture returns the exact new reason; m12/m15 die. F2 separately limits the assignment-order coverage claim. |
| A2-F3 | **CLOSED** | `NIGHT_HANDBACK.md:308–325`: full-argv selection and recursive enumeration installed. Executed simulated tree selects `200,201,202`, excluding unrelated child 900. Live replay unavailable in this sandbox. |
| A2-F4 | **CLOSED** | Contract `:221–234`; runbook `:731–749`. Restored passage and naming sentence both MATCH; old two-digit sentence removed. Executed fixture includes both `refusal-7.json` and `refusal-123.json` as full evidence paths. |

**Q2 — Ruled-text fidelity**

Command: `python3 -B /private/tmp/r3-refuter-hqj_bzwo/fidelity.py`. Blockquote prefixes were removed and whitespace normalized; the Python reason was compared as its parsed string value.

| Passage | Location | Result |
|---|---|---|
| Q2 complete handbook passage | `docs/process/NIGHT_HANDBACK.md:301–326` | **MATCH** |
| Q3 naming sentence | `docs/contracts/evidence_night_entry.md:228–234` | **MATCH** |
| Q3 restored prior ruled passage | Same file `:221–228` | **MATCH** |
| Q4 reason string | `joulewise/evidence_night.py:739–740` | **MATCH** |
| Q4 certification sentence | Contract `:241–246` | **MATCH** |
| Q5 complete replacement, including command and Source | Runbook `:731–749` | **MATCH** |

No differing words.

**Q3 — Mutation table**

Every mutant ran these five `LifecycleTests` methods on the package copy:

```text
test_discovery_span_fence_reuses_the_watchdog_rule
test_retained_reason_names_the_span_rule_and_holds_before_the_span
test_deep_json_plan_is_unknown_and_the_failing_check_record_persists
test_custody_root_spellings_equal_under_realpath_classify_alike
test_discovery_retains_every_harvested_root_and_refuses_unknown
```

Replay: `python3 -B /private/tmp/r3-refuter-hqj_bzwo/mutations.py`.

| Mutation | Result | Failing assertion / output |
|---|---|---|
| m8: replace realpath comparison with string comparison | **KILLED**, rc 1 | Test `:986`, both `/` and `/night/..`: `'UNKNOWN' != 'ACTIVE'`. |
| m12: retained reason `None` | **KILLED**, rc 1 | Test `:953`: `('retained', None)` differs from exact ruled reason. |
| m14: remove `RecursionError` from except tuple | **KILLED**, rc 1 | Test `:969`: uncaught `RecursionError: maximum recursion depth exceeded`. |
| m15: old “plan span over” reason assigned before span rule | **KILLED**, rc 1 | Test `:953`: old reason differs from exact inactive-at-observation reason. |
| m16: correct reason assigned before parsing/span rule; remove later assignment | **SURVIVED**, rc 0 | All five pass; no failing assertion. See F2. |

The copy’s production file was restored and byte-compared equal to the worktree afterward. No repository file was modified.

**Q4 — Kernel and regeneration outputs**

Executed `python3 -B scripts/gen_state.py --check`:

```text
rc=0
stdout=''
stderr=''
```

`kernel.py` checked paths using `git cat-file -e cfc569213f3f4a9b900f73564d1f76c43101a4f7:<path>`:

| Pointer | Result |
|---|---|
| `latest_report` → `docs/process_traces/2026-09-21-activation-ce7c57a9/03-round3-under-the-gate.md` | RESOLVES |
| A264 authority and evidence → `docs/process_traces/2026-09-21-activation-29ea94df/05-coldgate-packet-a230-retained-root-discovery/10-coldgate-fable-ruling.md` | Both RESOLVE |
| A265 authority and evidence → `docs/process_traces/2026-09-21-activation-ce7c57a9/02-coldgate-packet-retained-root-round3/11-opus-contract-refuter.md` | Both RESOLVE |
| Both acceptance pointers → kernel and corresponding JSON objects | RESOLVE |

Additional outputs:

```text
NIGHT-ROOT-RETENTION-DISCOVERY-01 kernel present: False
NIGHT-ROOT-RETENTION-DISCOVERY-01 completed present: True
regenerate rc: 0
kernel.json diff rc: 0
RUN_STATE.md diff rc: 0
TASK_QUEUE.md diff rc: 0
kernel task IDs: 222 test oracle: 222 equal: True
```

Regeneration targeted copies under `/private/tmp/r3-refuter-hqj_bzwo/generated/`. The generated regions contain no differences from generator output.

`git diff --check af85b38a..HEAD` returned 2 for 56 whitespace diagnostics, all within newly custodied historical reports/exhibits. These are not findings against immutable evidence.

**Q5 — Same-signature statement**

| Class | This delta |
|---|---|
| Ruled text copied with a latent defect | **Recurs:** runbook `:741`, F1; exact fidelity does not make the symlink claim true. |
| Evidence asserted by basename | **None found:** complete paths remain asserted, including the harvested-root and ruled-case tests. |
| Documentation contradicting its adjacent executable rule | **Recurs:** runbook `:741` versus its direct classifier call at `:735`, F1. |
| Duplicated constants drifting | **None found:** refusal discovery and span evaluation still call their owning implementations. |

**Q6 — Merge recommendation:** **Do not merge this head; return F1 to the cold gate with a new packet under Q1 item 4.**

## Residual risk

- Live `pgrep -flP $$` failed with rc 3: `sysmond service not found` / `Cannot get process list`. The handbook probe demonstrates shell behavior on a simulated tree, not live process termination.
- The full suite and whole module were not run, as instructed; the sibling replay and separate pedagogy seat remain lead-owned evidence.
- The first filtered run on a package export encountered a Git-fixture setup error after eight passing tests. The second and final filtered run in the actual worktree passed all nine.
- HEAD remained exactly `cfc569213f3f4a9b900f73564d1f76c43101a4f7`; final worktree status was clean.