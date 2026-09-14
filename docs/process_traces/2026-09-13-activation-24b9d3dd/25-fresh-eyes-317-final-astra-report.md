```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Structural, merge-provenance and syntax checks pass; the replacement comment overstates the historical fence coverage.",
  "workspace": {
    "base_requested": "8a733f5c",
    "base_mode": "exact",
    "head_start": "71b87e54bfc911d5a7c23617a4db997804705ed9",
    "head_end": "71b87e54bfc911d5a7c23617a4db997804705ed9",
    "upstream_end": "27957b6066104fa470dded61a3db06e723c728f0",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "nit",
        "file": ".github/workflows/ci.yml",
        "line": 15,
        "summary": "The historical claim includes newly explicit documentation freshness and says every matrix job, although the four moved steps existed only in the ordinary test matrix."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python3 -B /private/tmp/pr317-fresh-eyes-71b87e54.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS: bash -n on all 17 run blocks",
          "PASS: git diff --check a4bb8838..71b87e54 (empty)",
          "PASS: git status --short (empty)",
          "PASS: HEAD unchanged at 71b87e54bfc911d5a7c23617a4db997804705ed9"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS: HEAD unchanged at 71b87e54bfc911d5a7c23617a4db997804705ed9"
      }
    }
  ],
  "flags": []
}
```

## Findings

**R1 — nit — `.github/workflows/ci.yml:15`.** The new historical sentence is not fully true. At `a4bb8838`, state generation, historical receipts, CLI validation and strict mock validation were identical steps inside each of the eight ordinary `test` matrix instances. They were absent from the other matrix jobs. Explicit documentation freshness is newly added, not relocated. Each of these five explicit steps now appears once, in `fences`.

Pasted comparison output:

```text
State kernel and generated-view drift: identical run before=['test']; now=['fences']
Documentation freshness: identical run before=[]; now=['fences']
Historical receipt semantics: identical run before=['test']; now=['fences']
CLI smoke - validate example configs: identical run before=['test']; now=['fences']
Strict mock run, validate, reduce, and revalidate: identical run before=['test']; now=['fences']
BASE matrix job: test
BASE matrix job: calibration-exits-exclusive
BASE matrix job: calibration-writer-crash-matrix-exclusive
BASE matrix job: pr-fast
```

Suggested correction: distinguish the four steps moved from the ordinary `test` matrix from the newly explicit documentation check.

The trigger sentence accurately describes event eligibility: push targets `main`, `pull_request` has no branch/path filter, and no job has an explicit `if`. It does not guarantee execution: `installed-wheel` depends on successful `build`, and superseded PR runs can be canceled.

**Post-review workflow diff**, exactly as requested (`git diff 8a733f5c..71b87e54 -- .github/workflows/ci.yml`): only comment lines changed—two removed, three added, with the first comment line retained.

```diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 3934cf98..b4ec2765 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -12,8 +12,9 @@ concurrency:
 
 jobs:
   # F2 state generation, F3 explicit docs freshness, F4 historical receipt
-  # semantics, and F5 CLI/strict mock smokes run once here, deliberately
-  # ungated on every push and pull request, including docs-only changes.
+  # semantics, and F5 CLI/strict mock smokes ran identically inside every
+  # matrix job; they run once here instead. Every job below runs on every
+  # push to main and every pull request.
   fences:
     runs-on: ubuntu-latest
     steps:
```

The entire parsed YAML is unchanged from `8a733f5c`, including these six jobs:

```text
fences: needs=absent; if=absent
test: needs=absent; if=absent
calibration-exits-exclusive: needs=absent; if=absent
calibration-writer-crash-matrix-exclusive: needs=absent; if=absent
build: needs=absent; if=absent
installed-wheel: needs=build; if=absent
```

**Merge provenance:** both diffstats and the complete patches are byte-identical. Merge parents are `8a733f5c` and `27957b60`.

`git diff 8a733f5c..80d0c110 --stat`:

```text
 configs/production_custody_inventory.json |  9 +++++-
 docs/process/NIGHT_HANDBACK.md            | 50 ++++++++++++++++++-------------
 tests/test_arm_readiness_schemas.py       |  5 +++-
 3 files changed, 41 insertions(+), 23 deletions(-)
```

`git diff 8a733f5c...27957b60 --stat`:

```text
 configs/production_custody_inventory.json |  9 +++++-
 docs/process/NIGHT_HANDBACK.md            | 50 ++++++++++++++++++-------------
 tests/test_arm_readiness_schemas.py       |  5 +++-
 3 files changed, 41 insertions(+), 23 deletions(-)
```

**Net PR diff**, from `git diff a4bb8838..71b87e54 -- .github/workflows/ci.yml scripts/test_timings.json`, one line per hunk with exact hunk headers:

```text
.github/workflows/ci.yml @@ -5,15 +5,46 @@ on: — Change concurrency to unique push groups/PR-only cancellation; add fences with five explicit check steps.
.github/workflows/ci.yml @@ -30,16 +61,16 @@ jobs: — Remove state/receipt steps from test; add relocation comment; install zsh only when /bin/zsh is not executable.
.github/workflows/ci.yml @@ -101,20 +132,6 @@ jobs: — Remove CLI validation and strict mock steps from test; identical commands now reside in fences.
.github/workflows/ci.yml @@ -251,114 +268,6 @@ jobs: — Delete the entire additive pr-fast job.
scripts/test_timings.json @@ -3,14 +3,6 @@ — Delete pr_fast_tier policy and explanatory metadata; retain timing weights and exclusive declarations.
```

All 17 current `run:` blocks pass `bash -n`. `git diff --check a4bb8838..71b87e54` and final `git status --short` produce no output. No repository files changed.

## Residual risk

What the lead should double-check: correct or explicitly disposition R1, and compare the five hunk summaries with the PR body. This offline review did not inspect the remote PR body, required-check settings, or hosted execution. No full suite was run; verification covered the requested comment delta, merge provenance, workflow structure and shell syntax.