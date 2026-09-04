```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "L1 ADOPT: GFM splits raw pipes inside code spans; use a backslash-only splitter but retain exact three-cell refusal, with a structural spec-table test cure.",
  "workspace": {
    "base_requested": "2983cdd4",
    "base_mode": "exact",
    "head_start": "2983cdd4e2c9d9ad81ba5d66707911e90c6312fe",
    "head_end": "2983cdd4e2c9d9ad81ba5d66707911e90c6312fe",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "L1",
        "severity": "blocker",
        "ruling": "AFFIRM (ADOPT)",
        "text": "GFM treats an unescaped pipe inside a backtick code span as a table-cell separator; the current scanner can therefore accept evidence GitHub does not render in the Evidence cell."
      },
      {
        "id": "L2",
        "severity": "blocker",
        "ruling": "AFFIRM option (c)",
        "text": "Delete code-span state and split on every unescaped pipe, but retain len(cells) != 3 so surplus cells are refused rather than silently truncated."
      },
      {
        "id": "L3",
        "severity": "should_fix",
        "ruling": "AFFIRM",
        "text": "All rounds share the signature that the checker cell model differs from GitHub's; the structural cure is a minimal GFM table-boundary tokenizer plus table-driven spec examples."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "shasum -a 256 docs/process/coldgate_charter.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter[.]md$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "curl -fsSL --max-time 20 https://github.github.com/gfm/ >/dev/null",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 6,
        "tail": [
          "curl: (6) Could not resolve host: github.github.com"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=\"$TMPDIR/sol-coldgate.RycnD3/tmp\" PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python \"$TMPDIR/sol-coldgate.RycnD3/tests/test_check_gate_ledger.py\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 16 tests in 2.093s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 16 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD\ngit status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "2983cdd4e2c9d9ad81ba5d66707911e90c6312fe",
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2983cdd4e2c9d9ad81ba5d66707911e90c6312fe\\n## HEAD [(]no branch[)]"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The sandbox could neither fetch the normative GFM page nor render the counterexample on GitHub; L1 therefore uses the packet-permitted remembered specification text and local mutation probes.",
      "needs": "Before adoption, paste the exact counterexample table into a GitHub PR body and confirm the third rendered cell contains literal b plus a backtick, not RUN evidence.txt."
    }
  ]
}
```

## Disclosure

Charter SHA-256 was verified before reading it and matched `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. I then read only §§3–5 and §8.

No material contamination: I saw no other cold-seat output and opened no prohibited narrative source. The runner injected repository bridge instructions before the packet, but they contained no prior ruling on L1–L3. The GFM fetch failed before returning content, so the specification citation below is from memory, as expressly permitted. Scratch-only copies and mutations were made under exported `TMPDIR`; the detached worktree remained clean.

No separately labeled lead disposition was supplied. I agree with Opus on L1 and removal of code-span state; I disagree with its proposed `< 3` truncation policy.

## Findings

### L1 — BLOCKER

**Verdict:** AFFIRM (ADOPT). GitHub splits on an unescaped `|` inside a backtick code span.

**Operative text/code shape:** The controlling remembered sentence from GFM §6.7, “Tables (extension),” is: “Include a pipe in a cell’s content by escaping it, including inside other inline spans:”

The accompanying example places `\|` inside a code span. That explicit requirement would be unnecessary if backticks protected a raw pipe from table splitting.

The current implementation instead tracks backtick runs and splits only when `code_ticks is None` ([scripts/check_gate_ledger.py:23](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:23), [scripts/check_gate_ledger.py:35](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:35), [scripts/check_gate_ledger.py:48](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:48)). The current regression test consequently pins the non-GFM result ([tests/test_check_gate_ledger.py:121](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:121)).

**Counterfactual:** A backslash-only scratch splitter produced:

- Raw: `| 1 | gate \`a | b\` | RUN evidence.txt |` → four cells: `1`, `gate \`a`, `b\``, `RUN evidence.txt`.
- Escaped: `| 1 | gate \`a \| b\` | RUN evidence.txt |` → three cells, retaining `RUN evidence.txt` as Evidence.

The current scanner instead treats the raw form as three cells and can pass hidden evidence.

**Not decided:** L1 determines table boundaries, not whether a checker should accept GitHub’s truncation of surplus cells. That is L2. It also does not require implementing general inline Markdown parsing.

### L2 — BLOCKER

**Verdict:** AFFIRM option (c). Delete code-span machinery and use the backslash-only splitter from (a), but retain exact arity:

```python
for char in line:
    if char == "|" and backslashes % 2 == 0:
        cells.append("".join(cell).strip())
        cell = []
    else:
        cell.append(char)
    backslashes = backslashes + 1 if char == "\\" else 0
```

Keep:

```python
if len(cells) != 3 or not cells[0].isdigit():
    continue
```

The existing exact-arity guard is at [scripts/check_gate_ledger.py:76](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:76).

Invert the raw-pipe test using the isolated form ``gate `a | b` ``, and add the passing companion ``gate `a \| b` ``. The scratch version ran 16/16 tests successfully.

**Counterfactual:** Option (b) leaves the permissive divergence intact because the scanner still suppresses the raw separator. Option (a)’s `< 3` rule would accept a four-cell source row whenever its first three cells look valid, even though the surplus cell proves the authored ledger row is malformed. Exact-three refusal makes the checker fail closed; GitHub’s display truncation does not make the source mistake acceptable.

**Not decided:** This does not reject GitHub’s rendering behavior or require the checker to reproduce rendered HTML. It decides only that the ledger contract is stricter than GitHub’s permissive surplus-cell truncation.

### L3 — SHOULD_FIX

**Verdict:** AFFIRM. Rounds 0, 1, 2, and this review have the same signature: the checker’s table-cell model differs from GitHub’s.

**Operative text/code shape:** The structural cure is to make `_split_table_row` a table-boundary tokenizer, not an inline-span parser:

1. An odd backslash escape makes a pipe literal.
2. Every other pipe splits.
3. Backticks, emphasis, links, and other inline syntax receive no special state.
4. `_ledger_rows` requires exactly three cells.
5. A table-driven test covers the GFM escaped-pipe examples plus raw/escaped pipes inside code spans and ordinary surplus cells.

Round 2’s escaped-backtick defect then disappears structurally because backticks cannot open any splitter state.

**Counterfactual:** Any future exception that lets inline syntax suppress a raw pipe recreates the same mismatch and permits a fourth round. A splitter containing no inline-span state has no such branch to regress.

**Not decided:** Same-signature classification does not criticize the historical fixes in isolation and does not decide unrelated ledger validation, evidence syntax, or full Markdown conformance.

## Residual risk

The magistrate should perform the live GitHub check with this exact PR-body table:

```markdown
| ID | Gate | Evidence |
| --- | --- | --- |
| 1 | gate `a | b` | RUN evidence.txt |
```

GitHub must render three columns with the Evidence cell containing the literal characters `b` and a trailing backtick; `RUN evidence.txt` must be absent because it is the ignored fourth source cell. This live observation and a direct reread of GFM §6.7 are the only unavailable coverage.