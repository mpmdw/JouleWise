```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented CI path gating, ungated fences, pr-fast removal, and conditional zsh installation; only ci.yml remains modified.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "1d4045b4a6396f0e76e0128a827544bc1296edea",
    "head_end": "1d4045b4a6396f0e76e0128a827544bc1296edea",
    "upstream_end": "1d4045b4a6396f0e76e0128a827544bc1296edea",
    "branch": "chore/2026-09-10-ci-trim"
  },
  "pathspec": [".github/workflows/ci.yml"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "python3 -c \"import yaml,sys;yaml.safe_load(open('.github/workflows/ci.yml'))\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["ModuleNotFoundError: No module named 'yaml'"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V1-manual",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/ci-trim-01-q8ocpg_6/review_structure.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Manual/textual structural review (not a YAML parse): PASS",
          "jobs: changes, fences, test, calibration-exits-exclusive, calibration-writer-crash-matrix-exclusive, build, installed-wheel",
          "needs/if: three heavy jobs depend only on changes and code == 'true'",
          "fences: no needs or if; changes: fallback output true; installed-wheel: needs build",
          "indentation: jobs 2, job keys 4, steps 6, step keys 8, run bodies 10 spaces",
          "bash -n: 9 run blocks PASS",
          "unchanged: triggers, concurrency, build, installed-wheel, both exclusive job bodies, ordinary unit selection, action versions",
          "discovery: tests.test_docs_freshness present"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "discovery: tests.test_docs_freshness present"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python -m unittest -v tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 31 tests in 0.821s",
          "",
          "OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python scripts/verify_receipt_histsem.py --repository-root . --require-published",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "  \"receipt_count\": 99,",
          "  \"schema_version\": \"joulewise.receipt_histsem_verification.v1\",",
          "  \"status\": \"PASS\"",
          "}"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "\"status\": \"PASS\""}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "export PYTHONDONTWRITEBYTECODE=1\nexport PATH='/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/ci-trim-01-q8ocpg_6/bin':\"$PATH\"\nexport TMPDIR='/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/ci-trim-01-q8ocpg_6'\nbash \"$TMPDIR/smokes.sh\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "valid config: configs/examples/mock_local.json target=mock_target runtime=mock telemetry=mock",
          "valid config: configs/examples/mac_mlx_local.json target=macbook_m3_max runtime=mlx telemetry=powermetrics",
          "bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/ci-trim-01-q8ocpg_6/ci-runs/example-mock-local status=succeeded",
          "valid bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/ci-trim-01-q8ocpg_6/ci-runs/example-mock-local",
          "bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/ci-trim-01-q8ocpg_6/ci-runs/example-mock-local status=succeeded",
          "reduction artifact: /Users/edr/code/JouleWise-wt-ci-trim/example-mock-local.summary_metrics.rereduced.0.5.2.json",
          "valid bundle: /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/ci-trim-01-q8ocpg_6/ci-runs/example-mock-local"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "valid bundle:"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [" M .github/workflows/ci.yml"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^ M \\.github/workflows/ci\\.yml$"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/ci-trim-01-q8ocpg_6/simulate.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "docs bookkeeping: 5d6bc93b^..5d6bc93b => code=false; exit_code=0",
          "suggested code candidate (actually docs): d18bc2b3^..d18bc2b3 => code=false; exit_code=0",
          "code commit: 33f8e586^..33f8e586 => code=true; exit_code=0",
          "docs merge first-parent range: 1d4045b4^1..1d4045b4 => code=false; exit_code=0",
          "code merge first-parent range: 8cbcaf08^1..8cbcaf08 => code=true; exit_code=0",
          "zero before: 0000000000000000000000000000000000000000..HEAD => code=true; exit_code=0",
          "missing before object: ffffffffffffffffffffffffffffffffffffffff..HEAD => code=true; exit_code=0",
          "empty diff: HEAD..HEAD => code=true; exit_code=0",
          "unknown event: ..HEAD => code=true; exit_code=0",
          "PR missing base: ..HEAD => code=true; exit_code=0",
          "PASS: 10 detector simulations"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "PASS: 10 detector simulations"}
    }
  ],
  "flags": [
    {
      "id": "ENV-YAML",
      "kind": "environment",
      "level": "nonblocking",
      "text": "PyYAML is unavailable. Completed the expressly permitted manual structural review and bash syntax checks instead.",
      "needs": "Lead should confirm GitHub accepts the workflow."
    },
    {
      "id": "HOSTED-EVENTS",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Offline simulations passed; live PR fetching, hosted action behavior, and post-change timings were not exercised.",
      "needs": "Review the first docs-only and code-touching hosted runs."
    },
    {
      "id": "CHECKOUT-DEPTH",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Optional T5 depth reduction was not applied because full transitive history independence was not established.",
      "needs": ""
    },
    {
      "id": "UNUSED-TIMING-POLICY",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "scripts/test_timings.json retains the now-unreferenced pr_fast_tier block outside write scope.",
      "needs": "Lead may decide whether to remove this unused configuration separately."
    }
  ]
}
```

## Change

Implemented the requested trim in [ci.yml](/Users/edr/code/JouleWise-wt-ci-trim/.github/workflows/ci.yml).

1. **T1:** Added ungated `fences` with full checkout and Python 3.11. It owns F2–F5, including explicit `tests.test_docs_freshness`. Removed the corresponding commands from `test`; retained per-interpreter compileall and the full shard selection.
2. **T2:** Added Git-only `changes` detection and gated all three heavy job families. Only `docs/**` and top-level `*.md` classify as docs. Empty, failed, missing-base, zero-SHA, and unsupported-event cases run everything. Checkout/detector step failures also default the job output to `true`.
   
   PR fetching explicitly updates `origin/<base>` before the merge-base diff. NUL-delimited paths preserve unusual filenames; `--no-renames` ensures moving code into `docs/` still counts the deleted code path. Successful classifications log every path and the decision.
3. **T3:** Deleted both `pr-fast` matrix executions and their header. No executable dependency on that job was found.
4. **T4:** Guarded apt installation with `/bin/zsh` executability and retained the final `test -x /bin/zsh`. The comment explains why `/usr/bin/zsh` alone is insufficient.
5. **T5:** Investigated; retained both exclusive jobs’ full-history checkout. The tests create independent fixture repositories—for example, crash-matrix initialization around line 354 and calibration-exits initialization around line 3650. However, their imported validator reaches `arm_readiness`, which contains historical Git replay. I did not establish exhaustive history independence, so took the permitted conservative option.
6. **T6:** Confirmed existing `ci-${{ github.ref }}` cancellation and the separate gate-ledger group suffice. Neither changed.
7. **T7:** Added no third-party action. Every retained action version is unchanged; new jobs reuse checkout v5 and setup-python v6.

A `docs/**` edit can alter generated views. That risk remains covered by unconditional `gen_state --check` and explicit docs-freshness tests.

**Removed work and retained coverage:**

| Removed | Coverage retained |
|---|---|
| Matrix state-generation check | F2, once in `fences` |
| Matrix historical-receipt check | F4, once in `fences` |
| Matrix CLI config smokes | F5, both configs in `fences` |
| Matrix strict mock chain | F5, unchanged chain in `fences` |
| Entire two-shard `pr-fast`, including compile/install/selected tests | F1, unchanged full matrix on code changes; compileall and conditional zsh remain on all ordinary shards |
| Unconditional apt execution | Same `/bin/zsh` postcondition, installation when needed |

Build, installed-wheel, both Python versions, every ordinary shard, and both exclusive suites remain. Site, proof, and gate-ledger workflows are untouched.

**After-state estimate**

The supplied individual medians sum to:

- Ordinary shards: `130.2` runner-minutes.
- Exclusive jobs: `17 + 12.5 + 11.6 + 5.5 + 8 + 4.1 = 58.7`.
- Build/wheel: `0.3 + 0.2 = 0.5`.
- Listed push jobs: `189.4`; PR adds `12.8 + 19.9 = 32.7`, totaling `222.1`.

The listed `ci.yml` jobs expand to **16 push jobs**, rather than 17; I used the individual figures for arithmetic.

Let `H` be removed fence time per ordinary shard, `Z` the saved apt time per shard, and `F` the new fences-job duration. With approximately one minute for `changes`:

| Event | Jobs running | Runner-minutes | Wall-clock, excluding queues |
|---|---|---|---|
| Docs-only push | `changes`, `fences`, `build`, `installed-wheel` — 4 | `1 + F + 0.3 + 0.2 = 1.5 + F` | `max(1, F, 0.5)` |
| Code PR | Above plus 8 ordinary, 2 exits, 4 crash-matrix — 18 | `222.1 − 32.7 − 8H − 8Z + 1 + F` | Approximately `1 + max(21 − H − Z, 17, 11.6)` |

**Provisional planning estimate:** use `H≈1.3`, `F≈1.6`, and `Z=0–1` minutes. The hoisted commands took roughly 80 seconds locally, inferred from log timestamps; the extra 0.3 minute is an assumed setup allowance. These are not hosted measurements.

- Docs-only: `1.5 + 1.6 ≈ 3.1` runner-minutes; approximately **2 minutes wall-clock**.
- Code PR: `222.1 − 32.7 − 10.4 − (0–8) + 1 + 1.6 = 173.6–181.6` runner-minutes; approximately **20–21 minutes wall-clock**.

## Verification notes

V1–V7 evidence appears verbatim in the envelope. PyYAML was not importable; no package installation was attempted. The fallback review checked all seven job definitions, dependency wiring, indentation, unchanged job bodies, action versions, and Bash syntax for all nine multiline run blocks. `git diff --check` also passed.

The machine has `python3` but no `python` command. For V2–V5, a temporary `python` symlink pointed to the installed `python3`; `PYTHONDONTWRITEBYTECODE=1` prevented repository bytecode writes.

V5 executed the extracted workflow commands, changing only the runs directory to `$TMPDIR/ci-runs`. Both strict validations passed. `reduce` nevertheless writes its default summary artifact into the current directory; that generated artifact was removed immediately, as requested.

Other deviations and findings:

- Optional T5 savings were deferred for correctness.
- Candidate `d18bc2b3` changes only `RUN_STATE.md`; actual code commit `33f8e586` supplied the code-positive simulation.
- `pr_fast_tier` remains untouched and unreferenced. The other discovered `pr-fast` reference is a historical comment in `tests/test_check_gate_ledger.py`.
- No named-decision conflict was found.
- No full suite, network fetch, sudo installation, commit, branch mutation, or push was performed by this session. Final HEAD is unchanged.

## Residual risk

The lead’s next step is to review the diff and validate the first hosted docs-only and code-touching runs, specifically:

- Confirm workflow parsing and that an empty detector output resolves to `true`.
- Confirm PR base fetching and `origin/<base>...HEAD` behavior for ordinary, fork, and reopened PRs.
- Check force pushes with unavailable old objects: the expected result is `code=true`.
- Check a first push with an all-zero `before`: also `code=true`. Existing triggers still admit pushes only to `main`.
- **Merge queue:** the workflow currently has no `merge_group` trigger. The detector’s unsupported-event fallback passed offline, but that does not make this workflow run for merge-queue events.
- Measure actual `fences` duration and whether hosted `/bin/zsh` exists; replace the provisional cost assumptions with those observations.

Only `.github/workflows/ci.yml` remains modified.