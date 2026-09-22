# Exhibit A2 — Sol delta re-audit 3 (high) on af85b38a (round-2 head, the merge candidate), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three should-fix findings and one nit; focused tests pass and m11-m13 are killed; checkout unchanged.",
  "workspace": {
    "base_requested": "9e0a4995",
    "base_mode": "exact",
    "head_start": "af85b38a3e45529ec06b283485157def1af5c0ff",
    "head_end": "af85b38a3e45529ec06b283485157def1af5c0ff",
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
        "file": "TASK_QUEUE.md:881",
        "summary": "Generated queue edits have no state-kernel backing; regeneration removes A263/A264 and reopens A230."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "joulewise/evidence_night.py:730",
        "summary": "The new retained reason and contract certify that a span is over even when it has not started."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "docs/process/NIGHT_HANDBACK.md:304",
        "summary": "Copied helper-cleanup procedure does not display the required command lines or recursively enumerate descendants."
      },
      {
        "id": "F4",
        "severity": "nit",
        "file": "docs/phase_2/derivation_night_runbook.md:753",
        "summary": "Two-digit naming claim overstates the allocator convention and understates accepted refusal filenames; ruled contract sentence is no longer verbatim."
      }
    ],
    "merge_recommendation": "FIX FIRST, then obtain lead final verification and the sibling full-suite result."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3.13 -B -m unittest tests.test_evidence_night -k retained -k discovery -k span",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 6 tests in 13.722s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3.13 -B /tmp/retention-audit-af85b38a/import_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Python 3.13.1; import 0.437191 s; write_or_process_events=[]"]},
      "expected": {"exit_code": 0, "tail_regex": "\"write_or_process_events\": \\[\\]"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3.14 -B /tmp/retention-audit-af85b38a/import_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Python 3.14.7; import 0.476678 s; write_or_process_events=[]"]},
      "expected": {"exit_code": 0, "tail_regex": "\"write_or_process_events\": \\[\\]"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "python3.13 -B /tmp/retention-audit-af85b38a/fixture_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["refusal.json True", "refusal-01.json True", "refusal-7.json True", "calibration-refusal.json True", "calibration-refusal.json.3.json True", "rerun.refusal.json False", "refusal.json.bak False"]},
      "expected": {"exit_code": 0, "tail_regex": "refusal.json.bak False"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3.13 -B /tmp/retention-audit-af85b38a/mutations.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["m11: FAILED (failures=4)", "m12: FAILED (failures=1)", "m13: FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3.13 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["DRIFT: /Users/edr/code/JouleWise-wt-retention3-29ea94df/TASK_QUEUE.md generated region differs"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3.13 -B /tmp/retention-audit-af85b38a/doc_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Q1_RULED_SENTENCE_VERBATIM False", "Q1_ONLY_N1_SUBSTITUTION True", "KERNEL_ROW NIGHT-ROOT-RETENTION-DISCOVERY-01 queued", "KERNEL_ROW RETAINED-ROOT-SPAN-ARITHMETIC-01 ABSENT", "KERNEL_ROW MAGISTRATE-LAUNCH-WITHOUT-MCP-01 ABSENT"]},
      "expected": {"exit_code": 0, "tail_regex": "KERNEL_ROW MAGISTRATE-LAUNCH-WITHOUT-MCP-01 ABSENT"}
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check 9e0a4995..af85b38a",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Full suite and whole module were deliberately not run. The requested filter selected six tests, not three.",
      "needs": "Lead must inspect the sibling full-suite replay."
    },
    {
      "id": "R2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Live pgrep probes returned exit 3: Cannot get process list. F3 is supported by the installed macOS manual, not a successful live process-tree replay.",
      "needs": "Lead should verify the corrected helper procedure in its authorized environment."
    }
  ]
}
```

## Findings

**Blocker: none.**

**F1 — should-fix: queue changes disappear on regeneration.**  
`TASK_QUEUE.md:858`, `:881`, `:882`, and their lane-table duplicates contain changes absent from `docs/process/state_kernel.json`.

Executed:

```text
python3.13 -B scripts/gen_state.py --check
→ exit 1
DRIFT: .../TASK_QUEUE.md generated region differs
```

Kernel inspection reports A230’s task as `queued`; A263 and A264 are absent. Comparison against the renderer shows no drift at `9e0a4995`, drift at `bd671744`, and drift at `af85b38a`. Thus this predates round 2, but round 2 adds its N3 residual to the same ephemeral rows.

**Cure:** record closures, the schema-compatibility residual, and A264 in their authoritative state/history locations, then regenerate the queue.

**F2 — should-fix: “span over” is a false certification for future plans.**  
`joulewise/evidence_night.py:730`; `docs/contracts/evidence_night_entry.md:236`.

The watchdog returns false before `t0 − PLAN_LEAD_S` (`scripts/magistrate_watchdog.py:777`). The new reason treats every false result as “over.”

Executed:

```text
python3.13 -B /tmp/retention-audit-af85b38a/fixture_probe.py
```

For a valid plan with `t0=1800000000`, terminal refusal records, and observation at `t0−7200`, output includes:

```json
{"classification":"retained","reason":"terminal record present; plan span over"}
```

The span has not started. The contract’s new certification repeats the same error. This is a round-2 regression in explanatory evidence, rather than a change to classification behavior.

**Cure:** say “terminal record present; plan span inactive under the watchdog rule,” and cover the pre-span case.

**F3 — should-fix: the copied handbook command does not implement its prose.**  
`docs/process/NIGHT_HANDBACK.md:304`.

`pgrep -lP` prints process names, whereas the next instruction requires identifying `codex mcp-server` in command lines. Also, `pkill -TERM -P <child-pid>` selects immediate children; it does not recursively select all descendants.

Executed:

```text
MANPAGER=cat man pgrep | col -b
```

The installed manual says `-l` prints the process name; combined with `-f`, it prints the full argument list. It defines `-P` as matching the parent PID.

The attempted fixture process-list probe returned exit 3, `pgrep: Cannot get process list`; no successful live termination-tree claim is made. This defect is inherited from the ruled text and persists at final head; round 2 did not introduce it.

**Cure:** obtain a lead-approved correction using full argv inspection and explicit recursive descendant enumeration, preserving the session-root boundary.

**F4 — nit: the N1 cure creates an inaccurate naming explanation.**  
`docs/contracts/evidence_night_entry.md:226`; `docs/phase_2/derivation_night_runbook.md:753`.

The fixture proves that `refusal-7.json` counts. The allocator’s `{index:02d}` specifies a **minimum** width, so names also exceed two digits after 99. The runbook’s “names are two-digit” claim is therefore inaccurate.

The ruling comparison, with whitespace normalized, produced:

```text
Q1_RULED_SENTENCE_VERBATIM False
Q1_ONLY_N1_SUBSTITUTION True
```

The sole change inside that sentence is:

```text
`refusal-N.json`
→ `refusal-01.json` and later numbers
```

**Cure:** preserve the ruled sentence and separately explain the allocator’s minimum-two-digit convention and the broader accepted glob.

**Q1 — closure table**

| Item | Disposition | Evidence |
|---|---|---|
| S1 | CLOSED | Shared `_refusal_paths` imported at `joulewise/evidence_night.py:713`, used at `:722`. |
| S2 | REGRESSED | Old contradiction removed, but replacement falsely certifies “over”; contract `:236`, F2. |
| S3 | CLOSED | Immediate “records only… `check` binds” qualification at runbook `:744`. |
| S4 | CLOSED | Entry-checkout timing constants explicit at contract `:231`. |
| N1 | REGRESSED | Concrete example added, but two-digit claim and verbatim drift remain; F4. |
| N2 | REGRESSED | Reason is populated and mutation-pinned, but incorrect before the span; code `:730`, F2. |
| N3 | OPEN | Residual appears at `TASK_QUEUE.md:881` and `:1107`, but regeneration erases it; F1. |

**Q2 — executed refusal fixture**

All entries were regular files in one synthetic, parseable, expired root.

| Filename | Counted |
|---|---|
| `refusal.json` | Yes |
| `refusal-01.json` | Yes |
| `refusal-7.json` | Yes |
| `calibration-refusal.json` | Yes |
| `calibration-refusal.json.3.json` | Yes |
| `rerun.refusal.json` | No |
| `refusal.json.bak` | No |

The inventory contains complete paths and classifies the expired root `retained`.

| Entry-checkout interpreter | Cold import | Writes/process launches |
|---|---:|---|
| Python 3.13.1 | 0.437191 s | None observed |
| Python 3.14.7 | 0.476678 s | None observed |

The import probe installed an audit hook rejecting write opens, filesystem mutations, subprocess launches, and socket connections. Both imports completed with an empty event list.

Strictly, the import is **not entirely side-effect-free**: `scripts/run_night.py:39` prepends/reorders the checkout in `sys.path`. A separate ordinary `python3.13 -B -c` probe confirmed this. No file or log write was observed.

**Q3 — mutation results**

Executed `python3.13 -B /tmp/retention-audit-af85b38a/mutations.py`. Each mutant used an independent package copy under `/private/tmp/retention-audit-af85b38a/`.

Each ran these three `LifecycleTests`:

- `test_discovery_retains_every_harvested_root_and_refuses_unknown`
- `test_retained_root_classification_ruled_cases`
- `test_discovery_span_fence_reuses_the_watchdog_rule`

| Mutation | Result | Failing assertion |
|---|---|---|
| m11: literal `refusal.json` only | KILLED; 4 failures | `tests/test_evidence_night.py:895`: `'UNKNOWN' != 'retained'` for numbered/calibration refusals; full-path evidence also fails at `:896`. |
| m12: retained reason `None` | KILLED; 1 failure | `:911`: actual `reason: None` differs from expected retained reason. |
| m13: remove refusal `is_file` filter | KILLED; 1 failure | `:898`: directory produces `('retained', [path])`, expected `('UNKNOWN', [])`. |

Initial mutation copies lacked the registration fixture and failed during setup; those were **not counted as kills**. After copying `configs`, all three mutants reached the substantive assertions above. Logs and replay scripts remain in the temporary audit directory.

**Q4 — same-signature statement**

Yes: round 2 repeats the “documentation contradicts its governing rule” class through “span over” versus the watchdog’s pre-span inactive branch, and through the two-digit naming claim. The copied-command latent defect persists in the handbook from round 1. Evidence-by-basename does **not** recur: assertions compare complete paths. Duplicated refusal constants do **not** recur: the implementation now calls their owner directly.

**Q5 — final-head recommendation**

Read the full ten-file `9e0a4995..af85b38a` diff, including the merged canonical-fast-forward changes. The concrete refusal points are F1–F3; no additional blocker was established.

**Merge recommendation: FIX FIRST; then require the sibling full-suite result and lead final verification.**

## Residual risk

The review used synthetic fixtures only and did not access the prohibited operational roots. Full-suite verification remains with the sibling runner. Checkout HEAD and clean status were unchanged throughout.