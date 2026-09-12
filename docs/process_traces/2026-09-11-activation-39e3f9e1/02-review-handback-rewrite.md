```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Contract checks pass; only first-use terminology nits remain. No repository files modified.",
  "workspace": {
    "base_requested": "944963b99509f0887aa367c21ac695ecd66b565f",
    "base_mode": "exact",
    "head_start": "944963b99509f0887aa367c21ac695ecd66b565f",
    "head_end": "944963b99509f0887aa367c21ac695ecd66b565f",
    "upstream_end": "944963b99509f0887aa367c21ac695ecd66b565f",
    "branch": "feat/2026-09-11-handback-rehearsal-20260912"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "nit",
        "path": "docs/process/NIGHT_HANDBACK.md",
        "line": 64,
        "summary": "Interpreter, .venv and LaunchAgent glosses occur after their use in Purpose."
      },
      {
        "id": "F2",
        "severity": "nit",
        "path": "docs/process/NIGHT_HANDBACK.md",
        "line": 55,
        "summary": "Several night-control terms lack a local gloss, including census, dead-man, cold gate, plan span, TERM/KILL and fixed belt."
      },
      {
        "id": "F3",
        "severity": "nit",
        "path": "docs/process/NIGHT_HANDBACK.md",
        "line": 158,
        "summary": "Acceptance and follow-on terminology needs first-use explanations, notably boot-UUID, epoch/monotonic pair and equivalence night."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 /tmp/handback-944963b-contract-review.py verbatim",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Unexpected byte differences: 0; section separators: one blank line each"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Unexpected byte differences: 0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "sed -n '219,231p' docs/process/NIGHT_HANDBACK.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["naming and the exact locked venv creation commands live in [the runsheet's plan-derived block](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md#plan-derived-measurement-variables)."]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "plan-derived-measurement-variables"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff HEAD^..HEAD --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [" 1 file changed, 97 insertions(+), 32 deletions(-)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1 file changed"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 /tmp/handback-944963b-contract-review.py preserved",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["All bytes outside the three replacements and G2-a routing paragraph: BYTE_IDENTICAL"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "BYTE_IDENTICAL"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 /tmp/handback-944963b-contract-review.py pins",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Epoch mismatches: 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Epoch mismatches: 0"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "grep -n 'rehearsal-20260911' docs/process/NIGHT_HANDBACK.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["127:[record 02](../process_traces/2026-09-11-activation-58a3bcfc/02-rehearsal-20260911-uninstall-and-retirement.md)."]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^127:"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3 /tmp/handback-944963b-contract-review.py terms",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["230:driver import check is `run_night.py preflight --plan PLAN.json`. Future clone"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^230:"
      }
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff HEAD^..HEAD --check",
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
  "flags": []
}
```

## Findings

No **BLOCKER** or **SHOULD_FIX** findings.

- **F1 — NIT — `docs/process/NIGHT_HANDBACK.md:64,80–81`:** `interpreter`, `.venv`, and `LaunchAgent` appear before their glosses at lines 197–198, 193–194, and 205 respectively. Put short explanations at their first use.
- **F2 — NIT — `docs/process/NIGHT_HANDBACK.md:55,66,87–93`:** `census`, `dead-man`, `cold gate`, `plan span`, `TERM`, `KILL`, `fixed … belt`, `powermode`, `timer probe`, and `capture-timeout seam` have no local definition. The role names `driver`, `watchdog`, and `magistrate` also occur earlier without definitions. These omissions are inherited from the prescribed text.
- **F3 — NIT — `docs/process/NIGHT_HANDBACK.md:158–170`:** Explain `boot-UUID`, the `epoch/monotonic pair`, and `equivalence night`. Related shorthand arrives earlier without sufficient explanation: Unix `epoch` at line 45, `pack` at line 48, and acceptance item/row identifiers at lines 59–62. The frozen triple is shown at lines 150–152, but its field names arrive only at line 180.

The following checks supply the commands and evidence. The inspection script is retained at [/tmp/handback-944963b-contract-review.py](/tmp/handback-944963b-contract-review.py).

**1. Verbatim check — PASS**

Command:

```sh
python3 /tmp/handback-944963b-contract-review.py verbatim
```

Output:

```text
BLOCK 1: authority=3218 bytes HEAD=3218 bytes
BYTE_IDENTICAL
BLOCK 2: authority=870 bytes HEAD=870 bytes
BYTE_IDENTICAL
BLOCK 3: authority=2156 bytes HEAD=2133 bytes
--- record13/block3
+++ HEAD/Next lane
@@ -1,4 +1,4 @@
-## Next lane for rehearsal-20260912
+## Next lane
 
 The relaunched magistrate (its prompt carries the frozen triple
 `rehearsal-20260912` / `/private/tmp/joulewise-rehearsal-20260912-checkout`
ONLY DIFFERENCE: heading suffix b' for rehearsal-20260912' removed (23 bytes); body BYTE_IDENTICAL
Unexpected byte differences: 0; section separators: one blank line each
```

Extraction excludes exactly the single blank separator before each following section; it performs no whitespace normalization. The intended heading deletion is the sole byte difference.

**2. Interpreter paragraph — PASS**

Command:

```sh
sed -n '219,231p' docs/process/NIGHT_HANDBACK.md
```

Output:

```text
G2-a routing handoff (2026-09-08; installed):
`scripts/run_night.py::_run_chain_once` derives `MEASUREMENT_ROOT`,
`MEASUREMENT_HEAD`, and `PY` from the parsed v2 plan and overwrites inherited
values in the child environment alongside `NIGHT_PLAN_ID`. There is no v2
interpreter field: the driver always gives the chain
`<measurement_root>/.venv/bin/python`, independently of the driver interpreter
selected at install time. (Since PR #321 the installer also pins the driver's
own interpreter by absolute path; before it, the driver ran under whatever
`python3` the LaunchAgent's PATH resolved to, which is the 2026-09-11 defect.)
The chain and its input preflight (checks before measurements start) verify checkout HEAD against `measurement_head`; that
input preflight's sole argument is the absolute v2 plan filename. The separate
driver import check is `run_night.py preflight --plan PLAN.json`. Future clone
naming and the exact locked venv creation commands live in [the runsheet's plan-derived block](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md#plan-derived-measurement-variables).
```

This distinguishes the existing plan-derived chain interpreter and chain input preflight from the driver’s absolute interpreter pin added in PR #321. Lines 205–212 additionally explain that the driver import preflight runs under the job’s interpreter and PATH. It does **not** imply the driver was pinned before PR #321, satisfying record 13’s closing instruction and ruling 06 §9.

The dated installer addendum introduces no conflicting requirement here; the rewritten uninstall command correctly omits `--python`.

**3. Nothing else changed — PASS**

Parent: `8a1d893bb13c3d1f55e08029ca1a0dcdca97f879`.

Command:

```sh
git diff HEAD^..HEAD --stat
```

Output:

```text
 docs/process/NIGHT_HANDBACK.md | 129 +++++++++++++++++++++++++++++++----------
 1 file changed, 97 insertions(+), 32 deletions(-)
```

Command:

```sh
python3 /tmp/handback-944963b-contract-review.py preserved
```

Output:

```text
## Executed — rehearsal-20260909: BYTE_IDENTICAL (1811 bytes; sha256 1389bce663a5c416f0329aa38d9e1438cdfbc65a4211b4d03f59352e029f7d8b)
## Executed — rehearsal-20260911: BYTE_IDENTICAL (1053 bytes; sha256 9f907445733b22336d38d6c47125ba0c322b75c26dcb979e0f06e801ded8dced)
**Standing rules**: BYTE_IDENTICAL (2230 bytes; sha256 2d71c238e4c71153938884c3bea2dac73647efd3a16ff8961608cc13bad6bc78)
All bytes outside the three replacements and G2-a routing paragraph: BYTE_IDENTICAL
```

The standing-rules comparison covers its marker through the blank line preceding `G2-a routing handoff`, whose edit is separately authorized.

`git diff HEAD^..HEAD --check` also exited 0 with no output.

**4. Pins arithmetic — PASS**

Command:

```sh
python3 /tmp/handback-944963b-contract-review.py pins
```

Output:

```text
t0: 2026-09-12 00:30:00 PDT = 1789198200; PASS; literal in rewritten sections=True
window close: 2026-09-12 00:45:00 PDT = 1789199100; PASS; literal in rewritten sections=False
courier deadline: 2026-09-12 00:50:00 PDT = 1789199400; PASS; literal in rewritten sections=True
plan span / stand-down: 2026-09-12 00:05:00 PDT = 1789196700; PASS; literal in rewritten sections=True
TERM: 2026-09-12 00:14:00 PDT = 1789197240; PASS; literal in rewritten sections=True
KILL: 2026-09-12 00:15:00 PDT = 1789197300; PASS; literal in rewritten sections=True
dead-man: 2026-09-12 07:00:00 PDT = 1789221600; PASS; literal in rewritten sections=False
Rewritten epoch literals: 1789198200, 1789199400, 1789196700, 1789197240, 1789197300
Window close is implied by t0 + 900; dead-man is stated as 07:00 on 09-12. Neither epoch is printed.
Epoch mismatches: 0
```

Python used `ZoneInfo('America/Los_Angeles')`. All requested values recompute correctly; every printed epoch and its associated time/duration matches. No mismatching numbers found.

**5. Other mentions — PASS**

Command:

```sh
grep -n 'rehearsal-20260911' docs/process/NIGHT_HANDBACK.md
```

Output:

```text
52:`rehearsal-20260911` is RETIRED: its night never ran. At 02:56 PDT on
57:`docs/process_traces/2026-09-11-activation-58a3bcfc/01-rehearsal-20260911-harvest-record.md`
114:## Executed — rehearsal-20260911 (2026-09-11)
123:[record 01](../process_traces/2026-09-11-activation-58a3bcfc/01-rehearsal-20260911-harvest-record.md):
127:[record 02](../process_traces/2026-09-11-activation-58a3bcfc/02-rehearsal-20260911-uninstall-and-retirement.md).
```

All five occurrences fall within the permitted retirement sentence, record pointers, or dated history section.

**6. Writing-standard first-use test — NITS F1–F3**

Command:

```sh
python3 /tmp/handback-944963b-contract-review.py terms
```

Relevant output excerpts:

```text
55:census, gate or stub ran; the 07:00 dead-man then refused on an orphaned
66:first time. Cold-gate ruling
80:carries a `.venv` whose `bin/python` is Python 3.13 — the interpreter the two
81:LaunchAgents name by absolute path. Both night agents are installed from that
87:The arming activation exits after recording the arm. The watchdog's plan span
89:(epoch 1789196700, `t0 − 25 minutes`); TERM is `t0 − 16 minutes`
90:(1789197240) and KILL is `t0 − 15 minutes` (1789197300). The fixed
91:02:45–03:30 belt does not touch this night. Power source, powermode and the
92:timer probe are recorded at arm time. Powermode is recorded, not gated, for
93:this stub; a green stub says nothing about the capture-timeout seam.
158:`load_average_raw` and `thermal_raw`; C4 carrying the boot-UUID and
159:epoch/monotonic pair; C5 recording `chain_stub: built_in_stub_by_design` with
170:After preserving the evidence, and BEFORE the equivalence night's install
193:needs `claude` on PATH or a Python virtual environment (a project-specific
194:Python installation).
197:pass `--python /absolute/path/to/python` to select the interpreter (the
198:executable running the driver). A stub checkout needs that venv or an absolute
205:`datetime.UTC`. A **LaunchAgent** is a macOS launchd job file; each job now names
```

Earlier definitions adequately cover **chain/exit code** (lines 10–12), **custody root** (13–16), **courier.sent** (33), and **chain.exited** (34–35). The new text itself explains the stub’s behavior at lines 47–48 and identifies `t0` through the scheduled start at line 45. Those are not findings.

## Residual risk

This was a read-only documentation review. No installation, live rehearsal, hardware validation, or application test suite was run; targeted byte comparisons and arithmetic checks cover this commit’s scope. HEAD and the clean worktree remained unchanged. Final merge adjudication remains with the lead.

VERDICT: MERGEABLE
## Lead disposition (magistrate 39e3f9e1, 2026-09-11 10:0x PDT)

Checks 1–5 PASS (verbatim modulo the intended heading; interpreter paragraph correct; only NIGHT_HANDBACK.md changed; pins arithmetic matches; `rehearsal-20260911` appears only in the retirement sentence, its record pointers and the dated history section). F1–F3 (first-use glosses) are DECLINED for this commit: the three sections are prescribed verbatim by 58a3bcfc record 13 §Step 0b, which the arm runbook requires to be applied as written; the reviewer notes the omissions are inherited from the prescribed text. A gloss pass over NIGHT_HANDBACK.md under the writing standard is registered as a follow-up lane (`NIGHT-HANDBACK-GLOSS-01`, docs-only, after tonight's night), not a change to H′. Verdict carried: MERGEABLE.
