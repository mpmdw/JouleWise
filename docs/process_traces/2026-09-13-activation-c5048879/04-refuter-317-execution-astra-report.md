```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"One concurrency blocker: a docs push can replace a pending code push; detector cases and requested checks pass.",
  "workspace":{"base_requested":"27957b60","base_mode":"exact","head_start":"f5f2403e1807dd9ef25b00fd2b738c42f1875e20","head_end":"f5f2403e1807dd9ef25b00fd2b738c42f1875e20","upstream_end":"27957b6066104fa470dded61a3db06e723c728f0","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[
    {"id":"R1","severity":"blocker","file":".github/workflows/ci.yml","line":12,"summary":"Shared push concurrency can discard a pending code run.","scenario":"Run A occupies ci-refs/heads/main; code push B waits; docs push C replaces pending B. C compares B..C, classifies docs-only, and skips the matrix.","recommendation":"Use a unique concurrency group for each push run while retaining ref-based cancellation for PRs."},
    {"id":"R2","severity":"nit","file":"docs/process_traces/2026-09-10-side-threads/ci-trim-01-seat-astra.md","line":194,"summary":"Trailing whitespace makes git diff --check fail.","scenario":"git diff --check 27957b60..HEAD exits 2."}
  ]},
  "verification":[
    {"id":"V1","kind":"inspection","cmd":"git diff 27957b60..HEAD -- .github/workflows/ci.yml","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":".*"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 /private/tmp/ref317_detector_review.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: 16 concrete diff/event cases + detector-error fallback inspection; all fetches local"]},"expected":{"exit_code":0,"tail_regex":"PASS: 16"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 31 tests in 1.249s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V4","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_state.py --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V5","kind":"lint","cmd":"git diff --check 27957b60..HEAD","cwd":".","observed":{"result":"fail","exit_code":2,"tail":["docs/process_traces/2026-09-10-side-threads/ci-trim-01-seat-astra.md:194: trailing whitespace.","+   "]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V6","kind":"inspection","cmd":"git status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags":[
    {"id":"F1","kind":"baseline_drift","level":"nonblocking","text":"27957b60 is NOT an ancestor of HEAD. Merge-base is a4bb8838619bcee72c088209a9dbf20369310899. Two-dot diff includes six files; three-dot diff includes the stated workflow and two records. Workflow comparison is unaffected.","needs":"Lead must reconcile the baseline and review the final integrated candidate."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"No network or GitHub API access. Hosted concurrency, event execution, check names and branch protection were not queried. actionlint is not on PATH.","needs":"Lead should validate hosted behavior, adjudicate R1 and check required-check configuration."}
  ]
}
```

## Findings

**R1 — blocker, `.github/workflows/ci.yml:12`.** Under GitHub’s default one-pending-run concurrency behavior, a newer run replaces the pending run even when `cancel-in-progress` is false. With A running, code push B pending, and docs push C arriving, B can be canceled before its matrix or fences execute. C’s `B..C` diff contains only documentation, so B’s code receives no replacement full-suite execution. This defeats the every-code-push guarantee. This is a scheduler-semantics finding, not a hosted reproduction.

The exact block is:

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

The expression evaluates to **false for `push`** and **true only for `pull_request`**. It protects an already-running push; it does not establish a lossless push queue. Make push groups unique.

**R2 — nit, `docs/process_traces/2026-09-10-side-threads/ci-trim-01-seat-astra.md:194`.** The whitespace-only line fails `git diff --check`; remove its spaces.

No should-fix findings. No requested detector case misclassified code as documentation.

Checks performed: Python YAML parse, Bash syntax checks, old/new step and matrix equality, 16 concrete offline detector cases, detector-error injection, requested freshness/state checks, Git baseline and cleanliness checks.

**Parse and job wiring.** System `python3` lacks `yaml`; the expressly permitted venv interpreter successfully parsed with PyYAML 6.0.3 `BaseLoader`, preserving the `on` key. All run blocks passed `bash -n`. `actionlint` is not on PATH.

| Job ID | `needs` | `if:` verbatim |
|---|---|---|
| `changes` | absent | absent |
| `fences` | absent | absent |
| `test` | `changes` | `needs.changes.outputs.code == 'true'` |
| `calibration-exits-exclusive` | `changes` | `needs.changes.outputs.code == 'true'` |
| `calibration-writer-crash-matrix-exclusive` | `changes` | `needs.changes.outputs.code == 'true'` |
| `build` | absent | absent |
| `installed-wheel` | `build` | absent |

**Detector traces.** Exact operative lines in `.github/workflows/ci.yml`:

```text
44: docs/*)
45:   case "${1##*/}" in
46:     *.py|*.sh|*.zsh|*.bash|*.json|*.jsonl|*.plist|*.toml|*.yaml|*.yml|*.cfg|*.ini)
47:       echo code ;;
48:     *.) echo code ;;
49:     ?*.*) echo docs ;;
50:     *) echo code ;;
53: */*) echo code ;;
54: *.md) echo docs ;;
55: *) echo code ;;
65: git diff --no-renames --name-only -z "origin/$BASE_REF...HEAD" -- > "$paths"; then
71: [ "$BEFORE_SHA" != 0000000000000000000000000000000000000000 ] &&
72: git diff --no-renames --name-only -z "$BEFORE_SHA" "$HEAD_SHA" -- > "$paths"; then
77: code=true
78: if [ "$diff_ok" = true ] && [ -s "$paths" ]; then
79:   code=false
82:   while IFS= read -r -d '' path; do
83:     kind=$(classify_path "$path")
85:     if [ "$kind" = code ]; then code=true; fi
```

| Case: concrete file list/event | Expected → actual | Trace |
|---|---|---|
| a: `docs/foo/bar.py` | code → code | L44–47 |
| b: `docs/foo/data.json` | code → code | L44–47 |
| c: delete `old.py`, add `docs/legacy/old.py` | code → code | L65 emits both paths; deletion hits L55, addition L46–47 |
| d: `README.md` | docs → docs | L54; L79 remains false |
| e: `tests/test_x.py`, `README.md` | code → code | L53 sets true; README cannot reset it |
| f: push with zero, missing, or unavailable before SHA | full → full | L70–72 fails; `diff_ok=false`; L77 survives |
| g: `workflow_dispatch` / `schedule` | fallback full → full if invoked | Neither matches L61–76; L77 survives |
| h: empty file list | full → full | L78’s `-s` fails |
| i: `docs/process/foo` | code → code | L44–50, extensionless fallback |
| j: `Makefile` or `pyproject.toml` | code → code | L55 |

For g, neither event is actually registered under `on`; no workflow runs for those events today. The fallback itself works.

The simulations used actual commits and extracted shell code, with local-only PR fetches. Injecting `mktemp` failure produced exit 7 and no output. Step `continue-on-error: true` plus L23’s `${{ steps.detect.outputs.code || 'true' }}` supplies the full-run default.

**Fences and suite.** `fences` has neither job-level `needs` nor `if`. Four relocated commands/blocks are byte-identical old `test` → new `fences`; their command diff is empty:

```bash
python scripts/gen_state.py --check
python scripts/verify_receipt_histsem.py --repository-root . --require-published
python -m joulewise validate-config configs/examples/mock_local.json
python -m joulewise validate-config configs/examples/mac_mlx_local.json
set -euo pipefail
line=$(python -m joulewise run configs/examples/mock_local.json --runs-dir ci-runs)
echo "$line"
bundle=${line#bundle: }
bundle=${bundle%% *}
python -m joulewise validate-bundle --strict "$bundle"
python -m joulewise reduce "$bundle"
python -m joulewise validate-bundle --strict "$bundle"
```

The fifth fence is newly explicit:

```bash
python -m unittest -v tests.test_docs_freshness
```

Previously discovery included that module in the ordinary suite; it remains included.

Old/new strategy differences are empty: ordinary matrix **3.11/3.14 × four shards**, calibration-exits **3.11/3.14**, crash-matrix **3.11/3.14 × two shards**, retaining crash-matrix `fail-fast: false`. All retained suite-selection scripts, unittest arguments, and exclusive job steps are identical. The requested no-suite-deletion invariant holds in the workflow. `pr-fast` removes duplicate execution only. Build and installed-wheel jobs are identical. L150 guards apt with `if [ ! -x /bin/zsh ]; then`; L154 retains `test -x /bin/zsh`.

**Check-name delta**, derived from unchanged matrix order and absent custom job names:

- Added: `changes`, `fences`.
- Removed: `pr-fast (1)`, `pr-fast (2)`.
- Retained: `test (3.11, 1)`, `test (3.11, 2)`, `test (3.11, 3)`, `test (3.11, 4)`, `test (3.14, 1)`, `test (3.14, 2)`, `test (3.14, 3)`, `test (3.14, 4)`, `calibration-exits-exclusive (3.11)`, `calibration-exits-exclusive (3.14)`, `calibration-writer-crash-matrix-exclusive (3.11, 1)`, `calibration-writer-crash-matrix-exclusive (3.11, 2)`, `calibration-writer-crash-matrix-exclusive (3.14, 1)`, `calibration-writer-crash-matrix-exclusive (3.14, 2)`, `build`, `installed-wheel`.

No matrix check was renamed.

## Residual risk

The two-dot comparison additionally changes `configs/production_custody_inventory.json`, `docs/process/NIGHT_HANDBACK.md`, and `tests/test_arm_readiness_schemas.py` because HEAD lacks main’s successor-handback commit. These are baseline differences, not session edits or established PR regressions.

Full-suite execution and hosted infrastructure failures were not exercised. A failed/canceled `changes` job can still skip dependents; step-error fallback does not cover whole-job failure. Branch protection requires the lead’s GitHub check.

Requested results: **31 tests, OK**; state generation check **exit 0, no output**; final `git status --short` **empty**. HEAD is unchanged.