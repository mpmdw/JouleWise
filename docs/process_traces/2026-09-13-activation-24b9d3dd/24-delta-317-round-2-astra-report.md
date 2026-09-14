```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round 2 matches the ruling exactly; local checks pass. One nit: the five-step relocation claim is inaccurate.",
  "workspace": {
    "base_requested": "a4bb8838",
    "base_mode": "informational",
    "head_start": "8a733f5c8a29644bca88d4dcfbf9efa5f3986880",
    "head_end": "8a733f5c8a29644bca88d4dcfbf9efa5f3986880",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "N1",
        "severity": "nit",
        "file": ".github/workflows/ci.yml",
        "line": 28,
        "summary": "Four fence commands were relocated byte-for-byte; Documentation freshness is an added standalone command, not a fifth relocated step.",
        "recommendation": "Correct the review description. Preserve this step as explicitly required by Q1."
      }
    ],
    "same_signature": "NO: no documentation-asserting test is excluded by workflow path or job/step conditions at HEAD."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff a4bb8838..8a733f5c -- .github/workflows/ci.yml scripts/test_timings.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "  \"exclusive_modules\": {",
          "   \"tests.test_calibration_exits\": {",
          "    \"seconds\": 2036.0,"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "\"seconds\": 2036\\.0,"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 7.495s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 31 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_shard_tests tests.test_shard_split",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 37 tests in 8.175s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 37 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check a4bb8838..8a733f5c",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "rg -n pr_fast_tier --glob '!docs/process_traces/**' .",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 1, "tail": []},
      "expected": {"exit_code": 1, "tail_regex": "^$"}
    },
    {
      "id": "V6",
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
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No network, GitHub API, hosted CI, or full discovery-suite execution. All requested targeted tests passed.",
      "needs": "Lead verifies hosted CI, required checks, PR metadata, and Q2(b) merge bookkeeping."
    }
  ]
}
```

## Findings

**N1 — nit — `.github/workflows/ci.yml:28`: five commands were not relocated.** The base has four matching standalone steps. Their parsed `run` strings are byte-equal at HEAD:

| Command | Base line → HEAD line | Comparison |
|---|---:|---|
| State kernel and generated-view drift | 33 → 26 | Byte-equal |
| Historical receipt semantics | 35 → 30 | Byte-equal |
| CLI smoke — validate example configs | 104 → 32 | Byte-equal |
| Strict mock run, validate, reduce, and revalidate | 108 → 36 | Byte-equal |
| Documentation freshness | absent → 28 | Added |

The added command is `python -m unittest -v tests.test_docs_freshness`. Q1 explicitly preserves `fences`, so this is a description correction, not a requested code removal. No blocker or should-fix implementation defect found.

Mechanical ruling replay used original line numbers against `8819cb5f`, applied all five deletion ranges plus the comment replacement, wrote both images into a temporary directory, and ran `diff -u`:

```text
Q1 mechanical diff rc=0
```

**Difference: empty.** HEAD line 8 exactly matches the ruled sentence, including punctuation.

Net workflow comparison found only FIX-1 concurrency/comment, T1 fences and the four removals described above, T4 zsh guard, T3 deletion, and associated comments. Both exclusive jobs, build, installed-wheel, and retained matrix commands are unchanged. `scripts/shard_tests.py` and tests have no base-to-HEAD changes.

The forbidden executable constructs are absent: no `changes` or `docs-readers` job, no `needs.changes`, no `cancelled()`. Literal `changes` remains in comments, so literal token absence cannot be affirmed:

```text
16:  # ungated on every push and pull request, including docs-only changes.
201:    # which changes test semantics and is out of TEST-SPEED-01's fence.
```

Parsed HEAD scheduling:

| Job | needs | if | Matrix |
|---|---|---|---|
| fences | absent | absent | Python 3.11 |
| test | absent | absent | 4 shards × 3.11, 3.14 |
| calibration-exits-exclusive | absent | absent | 3.11, 3.14 |
| calibration-writer-crash-matrix-exclusive | absent | absent | 2 shards × 3.11, 3.14 |
| build | absent | absent | — |
| installed-wheel | build | absent | — |

No step has `if:` either. Triggers remain pushes **to main** and unrestricted pull requests; neither has path filters.

Additional executed evidence:

```text
YAML parse PASS; bash -n PASS (17 run blocks); no job/step if
Timings JSON: ONLY pr_fast_tier removed, remaining bytes equal; shard_tests.py and tests unchanged
```

PyYAML used the permitted read-only venv interpreter. JSON was parsed and compared structurally, and deleting base lines 6–13 reproduced HEAD byte-for-byte. `rg -l 'test_timings|shard_tests' tests/` selected exactly the two shard-test modules run in V3. Test tails are pasted in V2/V3; all 68 tests passed. V4–V6 confirm whitespace cleanliness, no remaining non-trace `pr_fast_tier` references, and an empty worktree status.

**Same-signature: NO — no documentation-asserting test is skipped by workflow gating on a qualifying push or PR at HEAD.** Evidence: `.github/workflows/ci.yml:96–104` discovers all modules and removes only the two exclusive modules from ordinary scheduling; both exclusive jobs remain unconditional at lines 135 and 169. No path, job, or step condition filters documentation readers.

## Residual risk

This establishes configured coverage, not completion of every hosted run. Superseded PR cancellation remains intentional; existing failure/skip behavior was not changed. The full discovery suite was not executed for this workflow/configuration-only review.

**What the lead should double-check:** final-head hosted CI; required-check names and branch rules; PR title/body removal of T2 and docs-only savings claims; Q2(b)’s addendum and kernel amendment in the same activation’s merge bookkeeping. GitHub API reads would have been used for CI results, branch protection/rulesets, and PR metadata; none were made.