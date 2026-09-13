```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Fidelity, placement, focused tests and mutation pass; first-use requirements fail; live process verification is blocked by the sandbox.",
  "workspace": {
    "base_requested": "27957b60",
    "base_mode": "exact",
    "head_start": "cda6b727be41759ab9172e60af78822e12015fef",
    "head_end": "cda6b727be41759ab9172e60af78822e12015fef",
    "upstream_end": "27957b6066104fa470dded61a3db06e723c728f0",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "files": [
          "docs/phase_2/derivation_night_runbook.md:590",
          "docs/process/NIGHT_HANDBACK.md:49"
        ],
        "summary": "Exact installation preserves first-use gaps: several terms lack an earlier or inline definition in their destination document."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 59 tests in 1.263s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 59 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 1.586s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 31 tests[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/night-census-refuter-fhkuf5ti/verify.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["restored: exit=0", ".", "----------------------------------------------------------------------", "Ran 1 test in 0.000s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "A1: whitespace-normalized equality=True[\\s\\S]*narrowed literal: exit=1[\\s\\S]*FAILED \\(failures=1\\)[\\s\\S]*restored: exit=0[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "/usr/bin/pgrep -lf \"codex|claude|t3\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 3,
        "tail": ["sysmon request failed with error: sysmond service not found", "pgrep: Cannot get process list"]
      },
      "expected": {"exit_code": 0, "tail_regex": "/Applications/ChatGPT\\.app/"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "/usr/bin/pgrep -lf ChatGPT.app/Contents/MacOS/ChatGPT",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 3,
        "tail": ["sysmon request failed with error: sysmond service not found", "pgrep: Cannot get process list"]
      },
      "expected": {"exit_code": 0, "tail_regex": "/Applications/ChatGPT\\.app/Contents/MacOS/ChatGPT"}
    },
    {
      "id": "V6",
      "kind": "lint",
      "cmd": "git diff --check 27957b60..HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "Both required pgrep commands exited 3 without a process list. No live helper line or top-level-process exclusion could be verified.",
      "needs": "Lead must repeat both commands where process-list access works and compare the top-level PID against the census output."
    }
  ]
}
```

## Findings

**R1 — should_fix: first-use acceptance fails despite exact fidelity.**

References below use **runbook** = `docs/phase_2/derivation_night_runbook.md` and **handback** = `docs/process/NIGHT_HANDBACK.md`.

| Term | Runbook evidence | Handback evidence |
|---|---|---|
| agent runtime | **Pass:** inline definition, 590–591: “a shipped command-line agent binary that the app runs as a local server”. | Absent from amendment. |
| census | **Fail:** used at 355, reused at 594; explicit meaning appears only at 2374: “The enumerated process inventory proving no foreign or own agent is live.” | Used without definition at 45; absent from amendment itself. |
| plan span | Opening boundary explained at 209–210 and 584–585, before amendment’s 596. | At 51–52 the date/time supplies the required start, but the interval’s meaning is deferred to 127–128. Strict definition requirement fails. |
| t0 | **Fail:** first used at 61; no earlier definition before amendment’s 596. Later examples and arithmetic explain its use. | **Fail:** first used at 45 and in amended sentence at 52; scheduled time is identified at 55. |
| helper process | **Fail:** introduced at 593 without explaining what a helper process is. Identifying its argv does not define its relationship to the app. | “Codex helper” at 46 is also unglossed; absent from amendment itself. |
| refuses the night | **Fail:** 597 states the outcome without explaining that the gate prevents the measurement chain from starting. Earlier generic refusals do not define this night-specific outcome. | **Fail:** 51 has no inline explanation; the concrete “no chain started” consequence appears at 200. |
| arm | **Fail under strict first-use rule:** first used at 4; email-then-arm procedure appears at 231–236, before amendment’s 599, but presupposes “arm”. | Used as “armed” at 4 without definition; absent from amendment itself. |

Several gaps predate this diff; the new paragraphs inherit them. The genuinely new “agent runtime” gloss passes, while “helper processes” remains unbuilt. Also, `argv` at runbook:593 is unglossed.

**What the lead should double-check:** reconcile the first-use requirement with mandatory verbatim A1–A3. Earlier explanatory prose can preserve the mandated replacement bytes; changing those bytes needs an amended instruction.

Fidelity evidence, mechanically extracted from refuter 12, ruling 10 and the installed files:

```text
A1: whitespace-normalized equality=True
A2+A3: whitespace-normalized equality=True
test: whitespace-normalized equality=True
test: exact after class dedent/outer-newline removal=True
```

There are **no normalized differences to paste**. Placement passes: A2 begins immediately after the complete opening paragraph; A3 follows it; both precede the manual census paragraph. Three boundary lines:

```text
588: `t0 − 15 min` (`docs/process/MAGISTRATE_WATCHDOG.md`, §"Fence and deadlines", the boundary table).
590: Desktop apps that bundle an agent runtime — a shipped command-line agent
603: Before the arm census, stop all own seats, delegated tasks and background jobs
```

The intervening A2/A3 paragraphs occupy 590–601, separated by a blank line.

Mutation evidence at `tests/test_night_gate.py:382`, from the isolated `/tmp` copy:

```text
original: exit=0
narrowed literal: exit=1
- ('/usr/bin/pgrep', '-lf', 'codex|claude|t3')
+ ('/usr/bin/pgrep', '-lf', 'codex mcp-server|codex exec|claude|t3')

Ran 1 test in 0.001s

FAILED (failures=1)

restored: exit=0
Ran 1 test in 0.000s

OK
```

The literal assertion kills the specified mutation. The temp module was restored byte-for-byte; tracked files were never changed.

## Residual risk

No added sentence claims that the 09-15 measurement clone contains this documentation update. The unchanged census code also exists at the requested base. The clone’s stated pin at `27957b60` is supplied context, not independently inspected: prohibited directories were untouched.

**What the lead should double-check:** handback:95–102 retains the baseline wording “H is **this commit**” and “detached at H”. Keep its historical measurement pin explicit when presenting the updated notice; this install commit does not itself establish a new measurement head.

Focused suites were appropriate for two documentation changes and one regression test; the canonical full suite was not run. Tests provide fixture evidence, not live process validation.