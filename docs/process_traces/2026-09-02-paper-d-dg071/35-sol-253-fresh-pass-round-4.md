# Fresh pass (operation-loop §5) — Sol 253 high, execution lens, over fix round 4 (2026-09-02)

Seat: Sol high, read-only (`--write-scope '[]'`), detached worktree at `b6b4013b`; brief = `<scratchpad>/fresh4-paper-d.md` (F1–F6, bounded to the fix-round-4 diff). Report verbatim below; scratchpad paths redacted.

---

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The producer and issued values replay correctly, but the new provenance regression test still admits a plausible HEAD-relative mutant; one prose comparison is also underspecified.",
  "workspace": {
    "base_requested": "6846363dab669149be43307a666f835a811c4e49",
    "base_mode": "descendant",
    "head_start": "b6b4013bf8586cc810412ff75c6b3764fd9e096b",
    "head_end": "b6b4013bf8586cc810412ff75c6b3764fd9e096b",
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
        "id": "SF1",
        "severity": "should_fix",
        "title": "The last-script-commit test still passes a plausible HEAD-parent implementation because of its fixture history"
      },
      {
        "id": "N1",
        "severity": "nit",
        "title": "The provenance paragraph does not define how the producer SHA-256 is compared with the recorded commit"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python scripts/issue_dg071_dg075_statistics.py --repository-root /Users/edr/code/JouleWise-wt-paper-d2 --out <scratchpad>/freshpass4.SFmfvf/replay1/dg071-dg075-statistics.json && cmp docs/paper/round7/dg071-dg075-statistics.json <scratchpad>/freshpass4.SFmfvf/replay1/dg071-dg075-statistics.json && cmp docs/paper/round7/dg071-dg075-statistics.md <scratchpad>/freshpass4.SFmfvf/replay1/dg071-dg075-statistics.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "JSON sha256 210bc591152d563d8e86fac1ffbf0534ac15c043713815638317fbedee6610f3",
          "Markdown sha256 85410cb4d78ca95428f8c774387f43b22a1a327a17501bd6f96b5cff193e28c2",
          "both cmp checks passed"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "both cmp checks passed"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=<scratchpad>/freshpass4.SFmfvf/tmp /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 27 tests in 0.438s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 27 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "patched ISSUER.PINNED_BUNDLE_PATH to <scratchpad>/freshpass4.SFmfvf/absent/power_trace.csv, then ran Dg071Dg075StatisticsTests.test_retained_bundle_values_of_record",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "skipped 'runs_window corpus absent (clean checkout without bundles)'",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "focused 27-test module over TMPDIR copies carrying, respectively, sorted(values[:8]), sorted(values[:400]), sorted(values[:406]), and git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "cap8: failures=2",
          "cap400: failures=2",
          "cap406: failures=1",
          "revparse: failures=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2.*2.*1.*1"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "in a full-history TMPDIR clone at b6b4013b, replace _git_commit command with ['git', 'rev-parse', 'HEAD^'] and run /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 27 tests in 0.394s",
          "OK",
          "mutant recorded ebd947a0879a29c6eb6f790723e0b29603926f63; correct last touch 701471732488b56952beb47393e08c68285a5ea2"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAIL.*test_producer_commit_is_the_scripts_last_commit_not_head"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical repository suite was not run because the review brief expressly prohibited it.",
      "needs": ""
    }
  ]
}
```

## Findings

### SF1 — should-fix: the provenance regression still depends on fixture shape

`test_producer_commit_is_the_scripts_last_commit_not_head` kills the requested `git rev-parse HEAD` mutant and explicitly checks that the recorded value equals the fixture’s script commit and differs from HEAD.

However, each fixture repository contains exactly:

1. The producer commit.
2. One later empty HEAD commit.

Consequently, the plausible wrong implementation `git rev-parse HEAD^` returns the expected producer commit. In a full-history scratch clone of the candidate, I substituted that implementation and all 27 tests passed:

```text
Ran 27 tests in 0.394s
OK
mutant recorded:    ebd947a0879a29c6eb6f790723e0b29603926f63
correct last touch: 701471732488b56952beb47393e08c68285a5ea2
```

Thus the test verifies its name only within a history where “last script commit” happens to equal “parent of HEAD.” This is the same fixture-construction class as its predecessor, though narrower: the old test admitted HEAD itself; this one admits HEAD-relative parent logic.

Smallest repair: construct histories where the producer commit is neither the root nor HEAD’s parent—for example, unrelated commit → producer commit → shared unrelated commit → divergent HEAD—and retain the existing equality and non-HEAD assertions.

### N1 — nit: “mismatch between the two” is not operationally defined

The new paragraph says:

> “The producer SHA-256 is recorded beside it: an uncommitted edit to the producer shows as a mismatch between the two.”

The two displayed strings—the 64-hex SHA-256 and 40-hex Git commit ID—are not directly comparable. What readers must compare is the recorded `script_sha256` with the SHA-256 of the script blob at `git_commit`.

A directly actionable formulation would say to compare against the bytes from:

```text
git show <git_commit>:<script_path>
```

This ambiguity occurs in the Method disclosure and docstring. It does not affect the issued artifact’s correctness.

## Residual risk

The differential remains an arithmetic oracle, not an independent parser or refusal-path implementation. That is suitable for F3’s bounded purpose: `_independent_reference` independently groups records, computes widths/spacings, sorts all 500/499 values, performs its own type-7 interpolation, and renders independently without calling producer helpers.

## F1 — `_git_commit`

The committed artifacts replay byte-identically at `b6b4013b`:

```text
JSON     210bc591152d563d8e86fac1ffbf0534ac15c043713815638317fbedee6610f3
Markdown 85410cb4d78ca95428f8c774387f43b22a1a327a17501bd6f96b5cff193e28c2
```

Two fresh replays also matched each other.

The committed provenance is internally consistent:

```text
producer.git_commit:   701471732488b56952beb47393e08c68285a5ea2
git log last touch:    701471732488b56952beb47393e08c68285a5ea2
producer.script_sha256 404e6a5614619dbb03916016b0284addfff3ce2458a5ea31ce60be834a16b859
current script SHA-256 404e6a5614619dbb03916016b0284addfff3ce2458a5ea31ce60be834a16b859
```

In an established repository with an unrelated commit but a never-committed producer path, real Git returned empty stdout and `_git_commit` refused `git_commit_invalid`; it did not record an empty string. In an entirely unborn repository, `git log` exits 128 and the refusal is instead `git_commit_unavailable`. The latter is outside the requested full-history-checkout condition.

Full-history edge analysis:

- Pure rename: without `--follow`, the rename/introduction commit is recorded. That is the latest commit touching the current path and preserves replay, but it is not necessarily the last content-editing commit if “changed” is read as content-only.
- Worktrees: correct when `repository_root` and `script_path` identify the same worktree. The CLI binds them that way. The lower-level API accepts them separately, so a caller could pair script bytes from one worktree with history from another.
- Historical checkout: Git searches history reachable from that checkout’s HEAD, so a checkout older than a later script change records the historical last touch. That is correct for its bytes, though not the newest change across all repository refs.
- Dirty tracked script: `git log` does not see the edit and still records the prior committed touch. `script_sha256` hashes the current edited bytes, so the difference becomes detectable only by comparing it with the recorded commit’s script blob; it is not automatically refused.
- `script_sha256` covers byte content, including dirty byte edits and content differences in historical checkouts. It does not cover pure renames, executable-mode changes, repository/worktree identity, or whether the recorded commit actually contains those bytes.

## F2 — the two new tests

`test_producer_commit_is_the_scripts_last_commit_not_head` correctly establishes two distinct HEADs, identical producer commits, byte-identical outputs, equality to the fixture script commit, and inequality to HEAD. It kills the requested HEAD mutant. SF1 records the remaining fixture-history weakness.

`test_retained_bundle_values_of_record` does what its name and docstring claim:

- Runs the producer against the absolute retained path.
- Verifies the pinned input SHA-256.
- Pins both sample counts, eight rendered millisecond values, eight exact-second values, maximum tiling gap, 100 nonzero boundaries, and both stdout summaries.
- Skips cleanly when `PINNED_BUNDLE_PATH` is patched to an absent file:

```text
skipped 'runs_window corpus absent (clean checkout without bundles)'
OK (skipped=1)
```

## F3 — widened differential

Two separately executed fixed-seed runs produced identical bundle-0 reference values and identical serialized-reference SHA-256:

```text
04872f4d6d839dae7a11345c5a6d9c1d0d91e4b8fa3c889b40b01e76b92e124a
```

Bundle 0:

```text
DG-071 n=500  Q1=99.8774  median=109.3168  Q3=119.8194  IQR=19.9420 ms
DG-075 n=499  Q1=99.8486  median=109.3452  Q3=119.8222  IQR=19.9735 ms
```

The two differential-only runs took 0.130 and 0.128 seconds. The complete focused module took 0.438 seconds versus the synthesis’s 0.424-second bench result: unchanged in kind and still sub-second.

`_independent_reference` has no shared producer shortcut: it independently parses and groups the CSV, converts literals to `Decimal`, constructs all widths and spacings, sorts the entire lists, and applies a separate quantile/rendering implementation. It handled all 500 records.

## F4 — requested mutant replay

All four outcomes exactly matched file 34:

| Mutant | Failures | Failing tests |
|---|---:|---|
| `sorted(values[:8])` | 2 | `test_differential_against_independent_reference`; `test_retained_bundle_values_of_record` |
| `sorted(values[:400])` | 2 | Same two |
| `sorted(values[:406])` | 1 | `test_differential_against_independent_reference` |
| `_git_commit` → `git rev-parse HEAD` | 1 | `test_producer_commit_is_the_scripts_last_commit_not_head` |

There was no deviation from the expected 2 / 2 / 1 / 1 result. The additional `HEAD^` survivor is reported separately as SF1.

## F5 — new provenance prose

The header bullet’s parenthetical—“last commit that changed the producer”—is sufficient for a reader who does not continue to Method, especially because the preceding bullet identifies the producer path.

The Method paragraph and docstring build or gloss “producer commit,” distinguish it from the checked-out commit/HEAD, provide the exact `git log` command, and explain byte-exact replay as reproducing both files byte for byte. No other newly introduced term fails first use.

The sole actionability weakness is N1: the SHA/commit “mismatch” comparison is implicit rather than defined.

## F6 — values of record

Read directly from the committed JSON:

| Row | n | Q1 (ms) | Median (ms) | Q3 (ms) | IQR (ms) |
|---|---:|---:|---:|---:|---:|
| DG-071 | 406 | 116.9720 | 120.9186 | 122.9227 | 5.9508 |
| DG-075 | 405 | 117.0321 | 120.9224 | 122.9270 | 5.8949 |

Maximum tiling gap is `0.0000004`; nonzero tiling boundaries are `100`. All requested values are unchanged.

## What this pass did NOT check

- Did not rerun the canonical suite, as expressly prohibited.
- Did not re-audit round 3, re-derive the golden, or inspect Method prose outside the new provenance material.
- Did not test shallow-clone behavior; the synthesis already records that limitation.
- Did not assess retained-bundle physics, claim suitability, or any PR file outside the bounded pathspec.
- Wrote nothing under the checkout; final `git status --short --branch` remained `## HEAD (no branch)`.