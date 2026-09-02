# terra 254 — fresh pass 2 (op-loop §5) over 6b6deb2f, at dfe69194 (verbatim; scratchpad paths redacted)

Brief: `fresh5-paper-d.md` (scope = `git diff b6b4013b...dfe69194`; G1 mutant replay incl. two wrong implementations of the seat's own choosing; G2 hash comparison; G3 replay; G4 values). Envelope 3582 bytes, `findings`, `complete`, rc=0.

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Replay and provenance hash are correct, but the revised fixture still admits two plausible wrong path/history lookups plus one fixture-tuned fixed-depth lookup.",
  "workspace": {
    "base_requested": "b6b4013b",
    "base_mode": "exact",
    "head_start": "dfe691948d61e2f85460a52db7591d2f9217baa3",
    "head_end": "dfe691948d61e2f85460a52db7591d2f9217baa3",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 1,
      "nit": 1
    },
    "findings": [
      {
        "id": "G1-SF1",
        "severity": "should_fix",
        "title": "The fixture does not distinguish the script's last modification from an ADD-only or directory-wide history lookup"
      },
      {
        "id": "G1-N1",
        "severity": "nit",
        "title": "A fixture-tuned HEAD~2 lookup survives"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=<scratchpad>/tmp-candidate /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_issue_dg071_dg075_statistics -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 27 tests in 0.514s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 27 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "Run the focused 27-test module in TMPDIR clones with each _git_commit command mutant.",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HEAD, HEAD^, and unscoped log: one failure each",
          "HEAD~2, scripts/ directory pathspec, and --diff-filter=A: all 27 passed"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "mutant results collected"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git show 6b6deb2f:scripts/issue_dg071_dg075_statistics.py | shasum -a 256",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "d657d75fc4bfa36dbfc12249b791a73541ae6e043eb861e4050c297e537f46d9"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "d657d75f"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python scripts/issue_dg071_dg075_statistics.py --repository-root /Users/edr/code/JouleWise-wt-paper-d2 --out <scratchpad>/replay/dg071-dg075-statistics.json && cmp docs/paper/round7/dg071-dg075-statistics.json <scratchpad>/replay/dg071-dg075-statistics.json && cmp docs/paper/round7/dg071-dg075-statistics.md <scratchpad>/replay/dg071-dg075-statistics.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DG-071 median_ms=120.9186 iqr_ms=5.9508",
          "DG-075 median_ms=120.9224 iqr_ms=5.8949",
          "cmp_json_md=pass"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "cmp_json_md=pass"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical discovery suite was not run, as the brief expressly prohibited it; the allowed focused module passed.",
      "needs": ""
    }
  ]
}
```

## Findings

### G1-SF1 — should-fix: last-change semantics remain under-tested

The new root → producer → unrelated → later fixture kills the specified HEAD-relative and unscoped mutations, but it never changes the producer after initially adding it, nor changes another file in `scripts/`.

Thus two plausible wrong implementations survive all 27 tests:

- `git log -1 --format=%H -- scripts/`
- `git log --format=%H --diff-filter=A -1 -- scripts/issue_dg071_dg075_statistics.py`

Both pass `test_producer_commit_is_the_scripts_last_commit_not_head`. The first is a credible directory/pathspec mistake; the second credibly confuses “last changed” with introduction. Extend the fixture with a later producer modification and a later change to another script.

### G1-N1 — nit: fixture-tuned depth constant survives

`git rev-parse HEAD~2` also passes all 27 tests because this exact fixture places the producer two commits below HEAD. That is a fixture-tuned constant, not a plausible general implementation, so it is a nit rather than a separate should-fix.

## G1

| Mutant | Result | Failing test |
|---|---|---|
| `git rev-parse HEAD` | killed | `test_producer_commit_is_the_scripts_last_commit_not_head` |
| `git rev-parse HEAD^` | killed | `test_producer_commit_is_the_scripts_last_commit_not_head` |
| unscoped `git log -1 --format=%H` | killed | `test_producer_commit_is_the_scripts_last_commit_not_head` |
| `git rev-parse HEAD~2` | survives | none |
| directory pathspec `scripts/` | survives | none |
| `--diff-filter=A` lookup | survives | none |

## G2

The sentence is actionable. The committed-script hash is:

`d657d75fc4bfa36dbfc12249b791a73541ae6e043eb861e4050c297e537f46d9`

The artifact’s `producer.script_sha256` is identically:

`d657d75fc4bfa36dbfc12249b791a73541ae6e043eb861e4050c297e537f46d9`

## G3

Replay at `dfe69194` was byte-identical for both JSON and Markdown (`cmp` passed).

## G4

Committed JSON values match the requested record:

- DG-071: n 406; 116.9720 / 120.9186 / 122.9227 / 5.9508
- DG-075: n 405; 117.0321 / 120.9224 / 122.9270 / 5.8949

## Residual risk

No additional residual risk within the bounded diff.

## What this pass did NOT check

It did not re-audit settled prior rounds, run the prohibited canonical discovery suite, or modify any checkout path.