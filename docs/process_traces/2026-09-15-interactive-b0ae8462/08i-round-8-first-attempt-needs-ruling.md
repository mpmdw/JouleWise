```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_RULING: Q1's second commit poll contradicts Q4 cell 4; independent F2 outcome-table correction completed.",
  "workspace": {
    "base_requested": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "base_mode": "exact",
    "head_start": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "head_end": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "upstream_end": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "branch": "feat/2026-09-15-install-windows-transactional"
  },
  "pathspec": [
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-r8-txn-20260915.json --expect-digest sha256:0b603b83d9d2a51d08e804c5a452ec3431db542f7fc65a70ee7fb7d767572b39 --scope joulewise/night_agent_install.py tests/test_night_agent_install.py docs/phase_2/derivation_night_runbook.md docs/process/NIGHT_HANDBACK.md --lease-id lease-31ff1578fff14128a7a4ece61c423f28",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"verdict\":\"SCOPE_OK\""
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
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "grep -c pthread_sigmask joulewise/night_agent_install.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["8"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^0$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\nimport subprocess\np = Path('/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/authority/consult-sig-fable-design.md')\ns = p.read_text()\nblocks = [chunk.split('```', 1)[0] for chunk in s.split('```python\\n')[1:]]\nprobe = '''import signal\nfrom types import SimpleNamespace\n'''+blocks[0]+'\\n'+blocks[1]+'''\nclass Probe:\n    _enter = _enter\n    _commit = _commit\n    def __init__(self):\n        self.shield = Shield()\n        self.state = 'VERIFIED'\n    def clock(self):\n        self.shield.signalled = 143\n        return 0\nState = SimpleNamespace(COMMITTED='COMMITTED')\nmin = lambda *args: 1\nmachine = Probe()\ntry:\n    machine._commit()\nexcept Signalled as exc:\n    assert exc.code == 143 and machine.state == 'VERIFIED'\n    print('Q1 clock-hook: Signalled(143), state VERIFIED; Q4 cell 4 requires COMMITTED/0')\nelse:\n    raise AssertionError('Expected the literal Q1 second poll to catch the clock-hook signal')\n'''\nfor interpreter in ('python3', '/usr/bin/python3'):\n    result = subprocess.run([interpreter, '-B', '-c', probe], capture_output=True, text=True)\n    print(interpreter + ': ' + result.stdout.strip())\n    assert result.returncode == 0, result.stderr\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "python3: Q1 clock-hook: Signalled(143), state VERIFIED; Q4 cell 4 requires COMMITTED/0",
          "/usr/bin/python3: Q1 clock-hook: Signalled(143), state VERIFIED; Q4 cell 4 requires COMMITTED/0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Q1 clock-hook: Signalled\\(143\\), state VERIFIED; Q4 cell 4 requires COMMITTED/0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: Q1 makes _enter poll unconditionally, then _commit calls _enter(COMMITTED) after clock(). A signal recorded by that clock hook therefore raises at the second poll. This contradicts the required LAST poll at _commit entry, Q3 item 5, and Q4 cell 4's COMMITTED/0 outcome. Reproduced from the design snippets under both interpreters.",
      "needs": "Authorize direct self.state = State.COMMITTED after the clock gate, replacing the literal Q1 self._enter(State.COMMITTED), or explicitly revise the final-poll semantics and cell 4."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Mechanism and tests remain unchanged pending F1. Neither requested module, the thirteen cells, nor mutation RED/GREEN checks were run. Remaining signal documentation is deferred with implementation. The zero-mask-call acceptance check remains unsatisfied.",
      "needs": "Resume this thread with the commit-boundary ruling."
    }
  ]
}
```

## Change

Runbook §1.3 now says “exactly one of five outcomes” and includes **failed teardown**, state **RETAINED**, exit **1**, with diagnostic `teardown failed; retained: <type>: <message>`. One hunk: two insertions, one deletion. No commit.

## Verification notes

**Question:** May `_commit` assign `self.state = State.COMMITTED` directly after its clock gate?

**Options considered:** Direct assignment preserves the required final poll and cell 4. Keeping the literal `_enter(COMMITTED)` introduces another poll after the clock and requires changing the adopted behavior.

**Recommendation:** Authorize direct assignment; it matches the explicitly required commit-race semantics.

**Blocked work:** Signal implementation, replacement tests, remaining documentation, both module runs, and mutation verification.

The reproduction sets the recorded signal value inside the clock hook; it demonstrates the control-flow contradiction without delivering an OS signal. Scope verification returned `SCOPE_OK`. No real launchctl or protected-path operations occurred.