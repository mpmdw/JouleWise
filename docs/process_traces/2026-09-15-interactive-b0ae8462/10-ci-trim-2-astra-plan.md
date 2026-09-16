# CI-TRIM-02 — measured plan and implementation

## Step 3 — restore docs-only skip (current; 2026-09-16 00:20 PDT ruling)

Ed's verbatim ruling: "doc changes don't need to go through ci and clog the queue".
This supersedes cold gate 17 option A's no-path-skipping requirement for
docs-only pushes ([ruling synthesis](../2026-09-13-activation-24b9d3dd/17-coldgate-packet-ci-trim-t2/14-magistrate-synthesis-ruling-10-with-opus-amendments.md)).
The one behaviour change is that proven docs-only ranges skip `quick`, `test`,
`calibration-exits-exclusive`, and `calibration-writer-crash-matrix-exclusive`.
As explicitly delegated, this classifier applies to both pushes and PRs.
`fences`, `build`, and `installed-wheel` remain ungated, retaining the state
kernel and documentation-freshness checks on every push. Existing job IDs,
step names, interpreter selection and dependencies are preserved.

Step-3 base: `bfa105d48064eb434e5b4bb532e0a6c046a682ca`, branch
`feat/2026-09-15-quick-suite-2`. Intake: clean tree, no active stop card;
canonical baseline digest and lease `lease-afd557f37db64aee8c31283661e54f33`
validated. This is the lead-assigned [AGENT] queue-pressure fix; all other
bookkeeping remains lead-owned under the two-path write scope.

`changes` retains `pythons` and adds `code`. Checkout fetches full history;
Bash compares push `before..GITHUB_SHA` or PR `base.sha..head.sha` using
`git diff --name-only --no-renames`. Only a non-empty list consisting entirely
of `docs/**` or top-level `*.md` yields `code=false`. Nested Markdown outside
`docs/` still runs tests. Disabling rename detection exposes both the old and
new paths, so moving code into docs cannot hide the deleted code path.
Missing/zero/malformed SHAs, unavailable commit objects, unsupported events,
empty diffs, checkout failure and Git detector errors yield `code=true`;
missing detector output also defaults to `true`. A runner failure remains a
CI infrastructure failure. Unusual Git-quoted filenames can conservatively
run tests. No third-party path-filter action is used.

Expected effect: a docs-only push runs approximately **4 short jobs instead
of 21/31** in the observed/historical configurations: `changes`, `fences`,
`build`, and `installed-wheel`. The exact current base has 23 jobs on code
pushes (18 matrix jobs + quick + these four) and 14 on code PRs; both docs-only
cases reduce to four. Full-history checkout adds some selector cost. Queue
relief is expected, not yet a measured hosted speedup; measurement 2 below
records the motivating observation.

### Step-3 verification (no local suites)

The replay below parses YAML, checks the unchanged job bodies/names and needs,
and dry-evaluates the exact classifier with synthetic Git responses. The
output sink is redirected to stdout; no checkout, fetch, test body, or suite
runs. It covers docs-only, mixed and empty lists; nested Markdown; push/PR
ranges; missing/zero/invalid/unavailable SHAs; unsupported/missing events;
checkout failure; and Git errors including partial diff output.

Observed: YAML and Bash syntax passed; all 21 dry cases passed; existing job
bodies, names and dependencies were preserved after accounting for the four
requested gates and the detector additions. `git diff --check` passed and
the anchored bridge scope check returned `SCOPE_OK`, with HEAD unchanged and
only the two authorized paths modified. No local suite, commit or push ran.
Next exact step: lead reviews the two-file diff, then validates hosted docs-only
and mixed-change runs through its authorized publication route.

<!-- CHECK:docs-skip -->
```sh
ruby -ryaml -ropen3 - <<'RB'
p = '.github/workflows/ci.yml'
w = YAML.load_file(p)
base, err, status = Open3.capture3('git', 'show', 'bfa105d48064eb434e5b4bb532e0a6c046a682ca:' + p)
raise err unless status.success?
a = YAML.load(base)
raise 'metadata changed' unless a.reject { |k, _| k == 'jobs' } == w.reject { |k, _| k == 'jobs' }
raise 'job IDs changed' unless a['jobs'].keys == w['jobs'].keys
gated = %w[quick test calibration-exits-exclusive calibration-writer-crash-matrix-exclusive]
a['jobs'].each do |id, job|
  current = Marshal.load(Marshal.dump(w['jobs'][id]))
  if gated.include?(id)
    raise 'wrong gate' unless current.delete('if') == "needs.changes.outputs.code == 'true'"
  elsif id == 'changes'
    raise 'wrong output fallback' unless current['outputs'].delete('code') == "${{ steps.paths.outputs.code || 'true' }}"
    added = current['steps'].slice!(job['steps'].length..-1)
    raise 'checkout not fail-open/full-history' unless added[0]['uses'] == 'actions/checkout@v5' && added[0]['with']['fetch-depth'] == 0 && added[0]['continue-on-error'] == true
    raise 'detector not Bash' unless added[1]['id'] == 'paths' && added[1]['shell'] == 'bash'
  end
  raise "existing job body/names/needs changed: #{id}" unless current == job
end
script = w['jobs']['changes']['steps'].find { |s| s['id'] == 'paths' }.fetch('run')
_, err, status = Open3.capture3('bash', '-n', stdin_data: script)
raise err unless status.success?
sink = '>> "$GITHUB_OUTPUT"'
raise 'unexpected output sink' unless script.scan(sink).size == 1
script = script.sub(sink, '>&1')
mock = <<'SH'
git() {
  case "$1" in
    cat-file)
      [[ "$2" == -e ]] || return 98
      [[ "$3" != "${UNAVAILABLE:-}^{commit}" ]] || return 128
      ;;
    diff)
      [[ "$*" == "diff --name-only --no-renames $EXPECTED_RANGE" ]] || return 98
      printf '%s' "$FILES"
      return "${DIFF_RC:-0}"
      ;;
    *) return 98 ;;
  esac
}
SH
env = {
  'CHECKOUT_OUTCOME' => 'success', 'GITHUB_EVENT_NAME' => 'push',
  'GITHUB_EVENT_BEFORE' => 'a' * 40, 'GITHUB_SHA' => 'b' * 40,
  'PR_BASE_SHA' => 'c' * 40, 'PR_HEAD_SHA' => 'd' * 40,
  'EXPECTED_RANGE' => ('a' * 40) + '..' + ('b' * 40),
  'FILES' => "docs/guide.md\ndocs/assets/plot.svg\nREADME.md\n",
  'DIFF_RC' => '0', 'UNAVAILABLE' => ''
}
cases = [
  ['docs-only', {}, 'false'],
  ['mixed', {'FILES' => "docs/guide.md\njoulewise/cli.py\n"}, 'true'],
  ['empty', {'FILES' => ''}, 'true'],
  ['nested-markdown', {'FILES' => "scripts/README.md\n"}, 'true'],
  ['top-level-only', {'FILES' => "README.md\n"}, 'false'],
  ['rename-outside-docs', {'FILES' => "docs/example.py\nexample.py\n"}, 'true'],
  ['pr-docs', {'GITHUB_EVENT_NAME' => 'pull_request', 'EXPECTED_RANGE' => ('c' * 40) + '..' + ('d' * 40)}, 'false'],
  ['missing-before', {'GITHUB_EVENT_BEFORE' => nil}, 'true'],
  ['zero-before', {'GITHUB_EVENT_BEFORE' => '0' * 40}, 'true'],
  ['malformed-before', {'GITHUB_EVENT_BEFORE' => 'bad'}, 'true'],
  ['missing-head', {'GITHUB_SHA' => nil}, 'true'],
  ['zero-head', {'GITHUB_SHA' => '0' * 40}, 'true'],
  ['missing-pr-base', {'GITHUB_EVENT_NAME' => 'pull_request', 'PR_BASE_SHA' => nil}, 'true'],
  ['missing-pr-head', {'GITHUB_EVENT_NAME' => 'pull_request', 'PR_HEAD_SHA' => nil}, 'true'],
  ['unavailable-before', {'UNAVAILABLE' => 'a' * 40}, 'true'],
  ['unavailable-head', {'UNAVAILABLE' => 'b' * 40}, 'true'],
  ['unsupported-event', {'GITHUB_EVENT_NAME' => 'workflow_dispatch'}, 'true'],
  ['missing-event', {'GITHUB_EVENT_NAME' => nil}, 'true'],
  ['checkout-error', {'CHECKOUT_OUTCOME' => 'failure'}, 'true'],
  ['diff-error-empty', {'DIFF_RC' => '128', 'FILES' => ''}, 'true'],
  ['diff-error-partial', {'DIFF_RC' => '128'}, 'true']
]
cases.each do |name, overrides, expected|
  out, err, status = Open3.capture3(env.merge(overrides), 'bash', '--noprofile', '--norc', '-euo', 'pipefail', '-c', mock + script)
  raise "#{name}: #{out} #{err}" unless status.success? && out == "code=#{expected}\n"
end
puts 'YAML PASS; existing job bodies, step names and needs preserved; four gates installed'
puts "CLASSIFIER DRY PASS; #{cases.size} cases; no test bodies executed"
RB
```

## Step 2 — PR interpreter dedupe (historical; 2026-09-15 23:10 PDT ruling)

Ed explicitly ruled that PRs run one interpreter and main pushes keep all
three roles: supported floor 3.11, production nights 3.13 (measurement venv
3.13.1, per the delegation), and local dev 3.14. The system-3.9 uninstall
path retains its own tests. This changes interpreter duplication only: every
selected interpreter still receives all six ordinary shards, the exclusive
calibration-exit module, and both crash-matrix shards. No path-based skipping.

Step-2 base is `b11fdd502d2180c1a28c45348fcae3a839fff115`, branch
`chore/2026-09-15-ci-trim-2`, PR #340. Only `.github/workflows/ci.yml` and
this plan are authorized writes. Intake: no active stop card; baseline clean,
prompt-supplied canonical digest validated, lease
`lease-7bd51d468a9d4c61a1cf5cf07813e342` active. This is the explicitly
assigned [AGENT] task; queue, run-state and decision-log updates are lead-owned.
The sections below this step-2 record describe the prior step-1 implementation
and measurements; their two-interpreter statements are historical.

### Workflow hunks

- Add `changes` (absent at this base), with one Bash step and no checkout,
  setup or third-party action. Default to `["3.11","3.13","3.14"]`; select
  `["3.13"]` only for exact `GITHUB_EVENT_NAME=pull_request`. Missing,
  unknown and non-PR event names retain the full list. The job output also
  defaults to the full list if the step output is empty. A runner/job failure
  still fails CI; this fallback does not mask infrastructure failure.
- Add `needs: changes` to `test`, `calibration-exits-exclusive`, and
  `calibration-writer-crash-matrix-exclusive`; set each `python-version`
  axis to `${{ fromJSON(needs.changes.outputs.pythons) }}`. No matrix-dependent
  job-level `if`. Preserve shard axes, test commands, names, triggers,
  concurrency, fences/build/wheel behavior and timeouts.
- Replace the old Python-role comment and the stale “Both interpreters”
  comment with the production/floor/dev roles and the PR rule.

### Counts and expected wall time

Counts here cover `ci.yml` only, excluding site, gate-ledger and production-proof.

| Job family | Before (PR or main) | After PR | After main push |
|---|---:|---:|---:|
| changes | 0 | 1 | 1 |
| test | 12 | 6 | 18 |
| calibration-exits-exclusive | 2 | 1 | 3 |
| calibration-writer-crash-matrix-exclusive | 4 | 2 | 6 |
| fences / build / installed-wheel | 3 | 3 | 3 |
| **Total** | **21** | **13** | **31** |

PR test jobs halve (18→9); total PR jobs drop by 8 (38%). After the
selector completes, at most 11 jobs from one PR can execute together
(9 test jobs + fences + build-or-wheel), versus 20 before. Two PRs offer
18 long test jobs instead of 36, leaving more room under the observed
20-job occupancy, although short jobs and other workflows still compete.
The added selector costs one runner allocation and serializes test release.

Expected PR wall with runners available remains approximately **19–20 minutes
plus selector latency**, using the existing ~18.62-minute calibration-exit
estimate and ~13.83-minute ordinary shards. Dedupe lowers queue pressure,
not the indivisible critical path; it makes that low-queue envelope more
plausible than the observed 32–40 minutes under contention. Python 3.13
has no hosted timings in this evidence, so this is an estimate, not a
measured speedup. A PR behind saturated main runs can still take ~29–39
minutes or longer. Main now has 27 test jobs (previously 18), exceeding
20-way occupancy itself and potentially worsening main/PR contention.
Actual scheduling, Python-3.13 performance and net wall savings require hosted
measurements; 20 is observed occupancy, not a confirmed concurrency quota.

### Check-name migration for magistrate / branch protection

All six existing job IDs and every existing step NAME are preserved.
`rg` across `.github/workflows/*.yml` found no cross-workflow dependency on
these CI matrix check names. The workflow name remains `ci`. The displayed
matrix checks change as follows (each entry is an exact check name):

| Disappears from PRs (remains on main) | Appears on PRs and main |
|---|---|
| `test (3.11, 1)`, `test (3.14, 1)` | `test (3.13, 1)` |
| `test (3.11, 2)`, `test (3.14, 2)` | `test (3.13, 2)` |
| `test (3.11, 3)`, `test (3.14, 3)` | `test (3.13, 3)` |
| `test (3.11, 4)`, `test (3.14, 4)` | `test (3.13, 4)` |
| `test (3.11, 5)`, `test (3.14, 5)` | `test (3.13, 5)` |
| `test (3.11, 6)`, `test (3.14, 6)` | `test (3.13, 6)` |
| `calibration-exits-exclusive (3.11)`, `calibration-exits-exclusive (3.14)` | `calibration-exits-exclusive (3.13)` |
| `calibration-writer-crash-matrix-exclusive (3.11, 1)`, `calibration-writer-crash-matrix-exclusive (3.14, 1)` | `calibration-writer-crash-matrix-exclusive (3.13, 1)` |
| `calibration-writer-crash-matrix-exclusive (3.11, 2)`, `calibration-writer-crash-matrix-exclusive (3.14, 2)` | `calibration-writer-crash-matrix-exclusive (3.13, 2)` |

New non-matrix check: `changes`. Unchanged: `fences`, `build`,
`installed-wheel`, plus the separate `gate-ledger` workflow. The magistrate
must inspect current branch protection/rulesets and replace any required
3.11/3.14 matrix contexts with the nine PR-emitted 3.13 contexts before
merging. Protection was not queried or modified in this step.

### Step-2 verification and next exact step

The `CHECK:yaml` replay below is updated for step 2: YAML parsing, unchanged
existing job/step names and bodies (except the three matrix axes/dependencies),
Bash syntax, event-to-JSON dry evaluation, and matrix cardinalities. It executes
no test bodies. The first dry attempt could not append to `/dev/stdout` in
this sandbox; the replay now redirects the one output write to the inherited
stdout descriptor without opening a file. GitHub's actual output-file plumbing
remains a hosted check. Step-1 partition/inline replay blocks are historical and were
not rerun for step 2. No local suites, commits, pushes or hosted triggers.

Only hosted runs can verify GitHub's output/fromJSON scheduling and emitted
check contexts, successful full-suite execution on 3.13, the three-interpreter
main matrix, unchanged test census/skip behavior, and real queue/wall savings.
Next: magistrate reviews the two-file diff, adjusts required check contexts as
needed, commits/pushes through its authorized route, and inspects PR #340 CI;
then verifies the full main-push matrix. Final scope/diff checks belong in the
step-2 return envelope; prior scope results below belong to step 1.

---

## Step 1 — historical measured plan and implementation

2026-09-15 PDT; hosted timestamps are 2026-09-16 UTC.
Base: f4d55d664a8df7937a52f807066b42ee01db6a12; branch chore/2026-09-15-ci-trim-2.
Delegated writes limited to ci.yml, test_timings.json, shard_tests.py, and this plan. No commits, local suite, live hardware work, or writes to another worktree. Baseline digest matches the prompt; baseline clean. ACTIVE_STOP_CARD: NONE. This owner-requested [AGENT] tooling lane is selected explicitly; queue/run-state bookkeeping remains lead-owned.

## 1. Measure before editing

### Population and provenance

The requested CI-TRIM-01 resume note is a pre-merge snapshot. The base and decision-log TEST-SPEED-01 addendum (2026-09-13, cold gate 17 option A) deliberately retain the full suite on EVERY push and PR. The changes detector was removed before merge. Do not restore path-based skipping.

Below are the latest three green main/push CI runs at intake, each running the full code matrix. Their triggering commits are process/docs records: they are NOT literally code-changing commits. They form the comparable full-matrix population behind the brief's 32–40 minute figures. The newest run finished after the brief's five-run sample. Tests, runner, timings and ci.yml are identical between that run's head and BASE_HEAD (git diff checked). The literal latest three green code-changing push heads were also selected and harvested before editing; Appendix B records their full tables.

Shell gh cannot connect to api.github.com in this sandbox. The installed GitHub connector fetched live REST run/job records and decoded job logs read-only instead. No local log-cache files written. Replay with:

```sh
gh run list --branch main --workflow ci.yml --status success --event push --limit 12 --json databaseId,headSha,createdAt,startedAt,updatedAt,displayTitle
gh api 'repos/mpmdw/JouleWise/actions/runs/35055941547/jobs?per_page=100'
gh run view 35055941547 --log
gh api 'repos/mpmdw/JouleWise/actions/runs/35055940169/jobs?per_page=100'
gh run view 35055940169 --log
gh api 'repos/mpmdw/JouleWise/actions/runs/35055084831/jobs?per_page=100'
gh run view 35055084831 --log
```

Workflow wall = updated_at - created_at; job wall = completed_at - started_at. Queue/start delay = job start - workflow creation, except installed-wheel uses build completion as its ready time. These APIs do not separate allocation/provisioning from capacity contention before job start. Setup = job start to test-step start. Module seconds are printed MODULE PASS durations, excluding import/discovery/setup. Hosted fixtures are not live hardware evidence.

| Run | Head | Created UTC | Workflow min | Runner-min | Last completion |
|---|---|---|---:|---:|---|
| [35055941547](https://github.com/mpmdw/JouleWise/actions/runs/35055941547) | b3b51a2c | 2026-09-16T04:31:37Z | 39.82 | 190.92 | test (3.11, 4) |
| [35055940169](https://github.com/mpmdw/JouleWise/actions/runs/35055940169) | 95e24386 | 2026-09-16T04:31:36Z | 32.57 | 194.32 | test (3.14, 3) |
| [35055084831](https://github.com/mpmdw/JouleWise/actions/runs/35055084831) | 912d45a2 | 2026-09-16T04:18:24Z | 32.05 | 200.07 | installed-wheel |

### Every job

Each cell: **queue/start delay min / execution min / setup seconds**. R1/R2/R3 = 35055941547 / 35055940169 / 35055084831. Setup dash means no suite step (the whole job duration remains included).

| Job | R1 | R2 | R3 |
|---|---:|---:|---:|
| build | 12.40 / 0.28 / — | 0.97 / 0.27 / — | 13.45 / 0.27 / — |
| calibration-exits-exclusive (3.11) | 12.73 / 18.93 / 15 | 3.98 / 14.80 / 15 | 9.78 / 11.27 / 13 |
| calibration-exits-exclusive (3.14) | 10.63 / 13.97 / 17 | 10.23 / 11.68 / 14 | 4.27 / 13.82 / 18 |
| calibration-writer-crash-matrix-exclusive (3.11, 1) | 13.33 / 6.05 / 12 | 5.60 / 10.78 / 16 | 5.52 / 11.60 / 15 |
| calibration-writer-crash-matrix-exclusive (3.11, 2) | 12.97 / 3.68 / 16 | 7.78 / 5.52 / 17 | 13.75 / 5.02 / 17 |
| calibration-writer-crash-matrix-exclusive (3.14, 1) | 16.70 / 7.82 / 18 | 7.07 / 6.20 / 16 | 6.20 / 7.92 / 17 |
| calibration-writer-crash-matrix-exclusive (3.14, 2) | 11.40 / 4.07 / 16 | 6.57 / 4.08 / 17 | 2.67 / 2.80 / 15 |
| fences | 10.68 / 0.68 / — | 0.83 / 0.73 / — | 3.65 / 0.70 / — |
| installed-wheel | 6.37 / 0.15 / — | 17.60 / 0.20 / — | 18.15 / 0.18 / — |
| test (3.11, 1) | 15.38 / 10.90 / 33 | 5.18 / 11.92 / 26 | 13.68 / 9.72 / 27 |
| test (3.11, 2) | 13.28 / 22.78 / 26 | 7.90 / 19.72 / 24 | 8.55 / 23.27 / 26 |
| test (3.11, 3) | 15.50 / 15.05 / 34 | 1.60 / 11.33 / 26 | 10.68 / 14.88 / 25 |
| test (3.11, 4) | 16.42 / 23.38 / 26 | 5.35 / 24.07 / 32 | 7.12 / 23.57 / 28 |
| test (3.14, 1) | 12.98 / 16.17 / 33 | 4.93 / 16.63 / 30 | 4.38 / 16.55 / 28 |
| test (3.14, 2) | 11.02 / 19.45 / 27 | 1.28 / 18.97 / 26 | 7.68 / 20.87 / 27 |
| test (3.14, 3) | 17.52 / 11.32 / 29 | 18.88 / 13.67 / 33 | 10.77 / 13.43 / 25 |
| test (3.14, 4) | 17.13 / 16.23 / 20 | 7.28 / 23.75 / 27 | 1.93 / 24.22 / 29 |

### Critical paths

- R1: **16.42 min start delay + 23.38 min test (3.11, 4) + 0.02 finalization = 39.82 min**.
- R2: **18.88 + 13.67 + 0.02 = 32.57 min**, ending on test (3.14, 3). The longest execution, test (3.11, 4), was 24.07 min but finished earlier.
- R3: build **13.45 min wait + 0.27 execution**, then wheel **18.15 min ready-queue wait + 0.18 execution = 32.05 min**. Last test ended at 31.82 min. An 11-second smoke is the final job because it queued.
- Job records from the latest twelve green CI runs show peak **20 simultaneously executing CI jobs**. This is observed occupancy, not a verified account quota. Other workflows/repos may also compete. R1 and R2 arrived one second apart. Free billing does not imply unlimited simultaneous starts.
- Ordinary setup is **20–34 s**, including **8–19 s** installing zsh. Logs show /bin/zsh really absent; the existing guard correctly installs it. There is no pip install in ordinary shards. Pip/build is confined to the short build/wheel jobs. Setup is minor beside minutes of queueing and tests.

### Exclusive-module measurements

| Work | R1 3.11 / 3.14 s | R2 3.11 / 3.14 s | R3 3.11 / 3.14 s |
|---|---:|---:|---:|
| Calibration exits | 1117.310 / 817.643 | 869.510 / 684.365 | 659.323 / 807.171 |
| Crash heavy unit | 347.995 / 446.634 | 628.898 / 352.066 | 679.554 / 454.644 |
| Crash remainder | 202.112 / 225.681 | 311.034 / 225.739 | 280.139 / 148.450 |

Exits uses unittest total (48 tests); crash uses MODULE PASS (1 heavy test + 19-test remainder). No test count inferred from historical comments.

The brief's tests.test_night_agent_install does not exist. Actual tests.test_install_night_agent has 25 methods and takes **5.911–8.462 s**, not 600 s / 37 tests. It is not split and needs no split. Actual ordinary monsters: tests.test_p2038_production_path **495.228–649.620 s** (8 tests); tests.test_receipt_histsem **418.759–573.613 s** (68 tests). Neither is declared split. Receipt history was priced at 28.714 s (20× below its maximum); reduce was priced at 1544.460 s versus 739.308 s for this initial latest-run sample (771.704 s after pooling Appendix B) as the sum of unit maxima. Only 140 of 230 discovered modules were measured; 90 additions inherited 29.834 s.

The calibration-exits split warning is still substantively relevant but its old explanation is stale. _WITNESS_RESULTS became WitnessCorpusOwner / _WITNESS_CORPUS_OWNER (test_calibration_exits.py:854–895); RefusalInventoryTests now explicitly requests its corpus (around line 1555). An uncached witness_corpus request still executes the complete ordered witness set (around line 3718). Splitting consumers duplicates that sweep and separates the single-generation registry/execution oracle. Log intervals around the parameterized witness test span roughly 536–932 s on 3.11; these are indicative intervals, not exact test weights because docstrings and CASE output interleave. Keep isolation and the 30-minute ceiling.

## 2. Diagnosis and lever decisions

Final scheduling estimates pool all six runs (latest three full-matrix pushes plus latest three code-changing push heads), twelve interpreter/run observations per ordinary module. Sums of maxima are conservative weights, not measured serial times. Replaying new partitions assumes order/cache effects and hosted speed remain comparable.

| Lever | Arithmetic / expected wall benefit | Risk and oracle | Decision |
|---|---|---|---|
| (a) More ordinary shards | Refreshed total 4978.177 s. K4 max 1244.545 s (20.74 min); K6 max 829.697 s (13.83 min); K8 max 660.313 s (11.01 min). K4→K6 saves 6.91 min ordinary execution; K6→K8 saves 2.82 min there but zero at the 1117.310 s calibration floor + setup (~19 min). | No test/interpreter removed. More jobs cost setup and queue capacity. K6: 20 initially eligible + dependent wheel =21 jobs; K8: 24 initially eligible /25 total, exceeding observed 20-way occupancy. | Implement K6. It is the smallest even count comfortably below the conservative calibration floor. |
| (b) Monster splits | Actual installer ≤8.462 s: possible saving <0.15 min. Splitting P2038/receipt could lower the K8 atomic floor from 660.313 toward 4978.177/8=622.272 s (38.041 s theoretical opportunity); K6 already balances at 829.697 s, so no ordinary or workflow saving there. | New splits require an independence audit; P2038 per-test temp roots alone do not establish cache/fixture equivalence. Splitting calibration consumers duplicates corpus work. | No new declarations needed. Retain existing reduce/crash splits; refresh their unit weights. |
| (c) Exclusive sharding | Crash already K2: heavy max 679.554 s, remainder max 331.860 s. K3 remains ≥679.554 s: zero benefit. Exits' ~536–932 s shared sweep prevents promising 1117/2=559 s from a naive K2 split. | Preserve generation identity, exact registry/witness set, teardown/survivor assertions and complete sweep. Splitting inside the parameterized test requires a separate reviewed test/fixture design. | Keep both exclusive jobs and current crash K2. Propose a later fixture/corpus design task if exits becomes the hosted bottleneck; no test-body change in this patch. |
| (d) Timing refresh | K4 replay max 899.390–1189.352 s versus old observed test steps up to ~1451 s: ~4–5 min ordinary-path saving at the slow end. K6 replay max 634.667–818.148 s: ~10.5 min at the slow end. | Scheduling hints only: live discovery, unknown-module fallback, missing-declaration failure and computed remainder remain authoritative. Order/cache effects need CI verification. | Refresh all 228 ordinary modules, existing split units, current exclusive seconds, and mean fallback; retain historical exclusive evidence ranges. |
| (e) Interpreter dedupe | Removing 3.14 saves roughly 95 runner-min/run; at 20 simultaneous jobs that is ~4.7 min saturated-backlog drain time, but empty-queue critical-path saving can be zero with 3.11/calibration still binding. | Loses full 3.14 behavioral compatibility: subprocess/process groups, filesystem/cleanup, unittest/discovery, imports and other new-interpreter semantics for omitted tests. Compile/import smokes cannot replace this; D-017 requires both. | Proposal only; recommend retaining both unless owner explicitly amends D-017 and defines a reduced-test contract. |
| (f) Setup/queue | Removing ALL setup buys ≤34 s/job but removes prerequisites; apt alone ≤19 s. K6 adds four setups, ~2 runner-min. Contrast 0.8–18.9 min test start delays and 18.15 min wheel ready-queue wait. | Keep /bin/zsh, full git history, per-interpreter compile and isolated wheel behavior. Skipping/canceling main pushes loses per-push evidence and contradicts retained push concurrency. | No setup or concurrency changes. Lead should inspect hosted capacity and batch bookkeeping before pushing where practical; do not cancel already-audited heads. This patch does not guarantee queue relief. |

3.14 runner-min actually measured: 89.02 / 94.98 / 99.60 (R1/R2/R3).

### Final pooled partition replay (ordinary seconds only)

R1–R3 and C1–C3 together; timestamps/queue waits are deliberately not replayed as if they were execution costs.

| Run | Interpreter | Refreshed K4 max | K6 max | K8 max |
|---|---|---:|---:|---:|
| 35055941547 | 3.11 | 1162.686 | 770.878 | 618.628 |
| 35055941547 | 3.14 | 1027.663 | 696.174 | 543.208 |
| 35055940169 | 3.11 | 1086.758 | 753.100 | 583.942 |
| 35055940169 | 3.14 | 1139.240 | 776.945 | 601.578 |
| 35055084831 | 3.11 | 1163.340 | 777.693 | 649.620 |
| 35055084831 | 3.14 | 1189.352 | 818.148 | 614.261 |
| 35051177531 | 3.11 | 1110.192 | 788.267 | 660.313 |
| 35051177531 | 3.14 | 899.390 | 634.667 | 468.249 |
| 35034962874 | 3.11 | 1147.452 | 754.458 | 559.941 |
| 35034962874 | 3.14 | 1124.861 | 771.608 | 607.988 |
| 35006580578 | 3.11 | 1078.485 | 746.413 | 616.423 |
| 35006580578 | 3.14 | 1163.301 | 795.166 | 595.374 |

**Expected end-to-end:** with available runners, move from ~24 min binding execution to **~19–20 min conservatively** (ordinary 13.83 min + setup; calibration maximum 18.62 min + setup). Observation-specific envelopes are ~14–19 min. Comparing observed 32–40 min wall with an empty-queue 19–20 min result suggests 12–21 min saving, but that includes queue removal the patch DOES NOT cause. If 10–19 min start delays persist, **~29–39 min remains plausible**. C3's 32-minute queue could still leave a ~51-minute run. Hosted CI must measure actual wall/runner-minutes; only execution imbalance is addressed here.

The original map estimates 1700.539 s maximum at K4, 1133.693 at K6, and 1002.560 at K8 (the stale reduce remainder). Its apparent perfect K4 balance is misleading: it underprices receipt history, overprices reduce, and guesses 90 modules. Refresh comes before choosing more shards.

## 3. Implementation record

Implemented narrow patch: ordinary K4→K6, one job environment variable for count; update current timing/provenance, mean fallback, existing reduce/crash split weights and current exclusive seconds (exits 1117.310; crash 679.554 + 331.860 = 1011.414 s). Historical evidence ranges and all fail-closed threshold checks remain. New ordinary fallback is 21.834 s, the mean of 228 ordinary module weights; exclusive jobs are excluded from the ordinary mean. Runner execution behavior/test bodies needed no change; scripts/shard_tests.py is unmodified. No interpreter dedupe, path filter, push cancellation, calibration split, new action, timeout change, or setup removal. Retain all job IDs, named steps and existing matrix check names.

## 4. Verification record

PASS: runner --help; Ruby YAML parse; all six job IDs and existing named steps preserved; triggers, concurrency and both interpreters preserved; declared matrix indices match SHARD_COUNT; 230-module timing/discovery coverage; every split test ID scheduled exactly once; six actual inline workflow partitions cover 231 ordinary units; embedded Python heredocs parse and both exclusive timing validators pass. Dry totals: ordinary 829.696,829.696,829.697,829.696,829.696,829.696 s; crash 679.554,331.860 s. No test bodies or suite executed. An initial ad-hoc heredoc parser combined multiple wheel heredocs and raised SyntaxError; corrected the inspection harness to parse each heredoc separately, then passed without a workflow fix. No local test suite permitted by the brief. Branch-protection read: gh cannot connect; GitHub connector returns 403 Resource not accessible by integration. Protection state is unknown, not absent. Gate-ledger.yml and d117-production-proof.yml have no dependency on ci.yml matrix cardinality. PyYAML unavailable; installed Ruby Psych can parse ci.yml (its YAML 1.1 parser treats on as true; structural checks account for this).

## Appendix A — every ordinary shard/module observation

MODULE PASS seconds, columns are 3.11 / 3.14 per run. Shard is the OLD shard index. A split reduce row covers only that unit or remainder, not the whole module. All 228 ordinary modules are covered; reduce has four rows, making 231 rows. Displayed zeros are preserved here and floored to 0.001 only in scheduling hints. These measurements were recorded before modifying timings.

| Module or reduce unit | Shard | R1 s | R2 s | R3 s | Old module hint s |
|---|---:|---:|---:|---:|---:|
| tests.test_2k_amplification | 2 | 0.099 / 0.124 | 0.102 / 0.157 | 0.057 / 0.074 | 0.147 |
| tests.test_adapters_powermetrics | 3 | 3.451 / 3.710 | 2.903 / 4.194 | 3.432 / 4.213 | 4.173 |
| tests.test_admit_model_panel_entry | 2 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 | unmeasured |
| tests.test_aggregate | 3 | 0.033 / 0.026 | 0.019 / 0.037 | 0.034 / 0.038 | 0.038 |
| tests.test_analysis_claims | 2 | 0.371 / 0.435 | 0.348 / 0.352 | 0.374 / 0.372 | 0.369 |
| tests.test_analysis_engine | 3 | 0.029 / 0.025 | 0.019 / 0.033 | 0.029 / 0.027 | 0.618 |
| tests.test_analysis_finalizer | 4 | 24.426 / 14.331 | 21.254 / 26.563 | 24.620 / 26.987 | 17.848 |
| tests.test_analysis_inputs | 4 | 16.155 / 10.920 | 16.388 / 17.445 | 16.328 / 17.610 | unmeasured |
| tests.test_analysis_integration | 2 | 73.679 / 86.429 | 58.483 / 81.623 | 79.981 / 85.758 | 78.189 |
| tests.test_analysis_manifest_v2 | 3 | 0.002 / 0.002 | 0.001 / 0.002 | 0.003 / 0.002 | unmeasured |
| tests.test_analysis_manifest_v3 | 2 | 0.860 / 0.969 | 0.636 / 0.884 | 0.965 / 0.960 | 0.542 |
| tests.test_analysis_manifest | 4 | 3.839 / 2.688 | 3.887 / 4.635 | 3.958 / 4.721 | 4.734 |
| tests.test_analysis_multiplicity | 1 | 0.005 / 0.012 | 0.009 / 0.012 | 0.006 / 0.010 | 0.01 |
| tests.test_analysis_ratio_integration | 2 | 0.038 / 0.038 | 0.034 / 0.036 | 0.038 / 0.039 | 0.039 |
| tests.test_analysis_ratio | 2 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 | unmeasured |
| tests.test_arm_readiness_dry_run | 4 | 27.174 / 19.701 | 28.803 / 30.757 | 27.625 / 31.255 | 1.169 |
| tests.test_arm_readiness_evidence_author | 3 | 50.152 / 44.320 | 36.826 / 52.026 | 49.194 / 52.382 | 35.805 |
| tests.test_arm_readiness_evidence_packauth | 4 | 30.703 / 22.936 | 32.598 / 33.156 | 30.312 / 33.553 | unmeasured |
| tests.test_arm_readiness_evidence_t0 | 2 | 71.328 / 68.121 | 53.083 / 64.708 | 67.238 / 67.398 | 25.563 |
| tests.test_arm_readiness_evidence | 2 | 0.267 / 0.252 | 0.196 / 0.227 | 0.243 / 0.248 | 0.243 |
| tests.test_arm_readiness_integration | 1 | 26.688 / 30.573 | 31.114 / 31.196 | 22.157 / 30.445 | 5.588 |
| tests.test_arm_readiness_lifecycle | 4 | 19.752 / 13.990 | 20.988 / 19.656 | 20.147 / 20.404 | 9.081 |
| tests.test_arm_readiness_pack_digest | 3 | 0.331 / 0.289 | 0.206 / 0.300 | 0.323 / 0.306 | 0.272 |
| tests.test_arm_readiness_registry | 1 | 10.900 / 16.890 | 14.887 / 17.321 | 11.320 / 17.158 | 15.48 |
| tests.test_arm_readiness_schemas | 4 | 0.220 / 0.134 | 0.218 / 0.193 | 0.223 / 0.197 | 0.035 |
| tests.test_arm_readiness | 4 | 8.585 / 6.288 | 9.141 / 9.713 | 8.883 / 9.908 | 0.685 |
| tests.test_audit_amplification | 3 | 5.327 / 5.111 | 4.856 / 5.485 | 5.314 / 5.542 | 5.455 |
| tests.test_audit_bundle_validation | 4 | 1.509 / 1.292 | 1.688 / 1.510 | 1.588 / 1.535 | 20.04 |
| tests.test_audit_cli_examples | 4 | 0.105 / 0.076 | 0.111 / 0.103 | 0.111 / 0.103 | 0.877 |
| tests.test_audit_clock | 3 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.001 |
| tests.test_audit_powermetrics_parser | 2 | 0.001 / 0.002 | 0.001 / 0.001 | 0.001 / 0.001 | 0.002 |
| tests.test_audit_reduce_degenerate | 4 | 0.242 / 0.211 | 0.278 / 0.246 | 0.262 / 0.266 | 3.337 |
| tests.test_audit_report | 1 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.001 |
| tests.test_audit_schema_edges | 3 | 0.005 / 0.004 | 0.003 / 0.005 | 0.004 / 0.005 | 0.005 |
| tests.test_authentication_io | 3 | 1.963 / 1.528 | 1.249 / 1.965 | 1.838 / 1.988 | 1.308 |
| tests.test_axi_analysis_manifest | 4 | 0.184 / 0.130 | 0.182 / 0.204 | 0.189 / 0.205 | 0.217 |
| tests.test_axi_burst_reduce | 4 | 0.674 / 0.514 | 0.666 / 0.752 | 0.684 / 0.782 | 0.774 |
| tests.test_axi_controller_events | 1 | 2.232 / 4.558 | 0.572 / 4.909 | 1.285 / 4.868 | 3.682 |
| tests.test_axi_mock_spec | 2 | 16.050 / 4.240 | 21.561 / 11.971 | 10.138 / 26.614 | 19.058 |
| tests.test_axi_output_identity | 3 | 0.070 / 0.053 | 0.042 / 0.077 | 0.068 / 0.075 | 0.079 |
| tests.test_axi_request_validation | 3 | 0.089 / 0.070 | 0.057 / 0.100 | 0.090 / 0.101 | 0.1 |
| tests.test_axi_sb_spike | 2 | 0.010 / 0.011 | 0.009 / 0.011 | 0.010 / 0.011 | 0.012 |
| tests.test_axi_sc_spike | 2 | 0.027 / 0.030 | 0.022 / 0.028 | 0.029 / 0.030 | 0.03 |
| tests.test_axi_schemas | 4 | 0.011 / 0.005 | 0.011 / 0.009 | 0.011 / 0.010 | 0.012 |
| tests.test_benchmark_import | 3 | 0.113 / 0.063 | 0.082 / 0.084 | 0.116 / 0.084 | unmeasured |
| tests.test_bracket_binding_cli | 2 | 14.677 / 18.230 | 10.780 / 17.552 | 16.648 / 18.119 | unmeasured |
| tests.test_bridge | 4 | 23.362 / 23.555 | 24.910 / 31.856 | 24.480 / 32.417 | 33.525 |
| tests.test_build_capstone | 4 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 | unmeasured |
| tests.test_build_site_parsers | 4 | 0.001 / 0.000 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 |
| tests.test_bundle_read | 4 | 5.018 / 4.145 | 5.599 / 5.197 | 5.436 / 5.214 | 49.094 |
| tests.test_bundle | 3 | 3.637 / 3.082 | 2.522 / 3.506 | 3.522 / 3.479 | 27.809 |
| tests.test_calibration_bracketing | 3 | 0.507 / 0.428 | 0.411 / 0.525 | 0.508 / 0.512 | 0.194 |
| tests.test_calibration_custody_store | 1 | 0.438 / 0.139 | 0.120 / 0.123 | 0.092 / 0.144 | 0.121 |
| tests.test_calibration_ledger_custody | 3 | 0.978 / 1.024 | 0.953 / 1.024 | 0.972 / 1.018 | unmeasured |
| tests.test_calibration_ledger | 4 | 3.348 / 2.420 | 3.240 / 3.839 | 3.440 / 3.945 | 2.681 |
| tests.test_calibration_live_three_window | 3 | 2.451 / 2.031 | 1.907 / 2.735 | 2.454 / 2.708 | 2.717 |
| tests.test_campaign_generator_core | 2 | 1.976 / 2.457 | 1.615 / 2.355 | 2.029 / 2.475 | unmeasured |
| tests.test_capture_pipeline_era | 3 | 2.416 / 2.406 | 2.372 / 2.445 | 2.416 / 2.448 | 2.455 |
| tests.test_capture_t0_step | 2 | 4.976 / 4.743 | 3.645 / 4.598 | 4.661 / 4.695 | 3.051 |
| tests.test_check_gate_ledger | 4 | 1.191 / 1.407 | 1.266 / 1.948 | 1.262 / 2.059 | unmeasured |
| tests.test_check_paper_replay_fence | 3 | 0.169 / 0.171 | 0.149 / 0.187 | 0.166 / 0.197 | unmeasured |
| tests.test_check_window_provenance | 2 | 14.944 / 18.253 | 10.623 / 17.130 | 16.788 / 18.128 | unmeasured |
| tests.test_claim_side_bound | 1 | 0.026 / 0.058 | 0.055 / 0.061 | 0.039 / 0.057 | unmeasured |
| tests.test_claims_index_lint | 3 | 3.368 / 2.908 | 2.465 / 3.648 | 3.292 / 3.654 | 3.391 |
| tests.test_claims_lint | 2 | 3.055 / 3.437 | 2.548 / 3.205 | 2.991 / 3.396 | 3.387 |
| tests.test_claude_bridge_mcp | 3 | 3.527 / 1.411 | 1.045 / 3.475 | 1.385 / 1.446 | 1.523 |
| tests.test_cli_run | 1 | 83.314 / 132.962 | 32.985 / 142.211 | 48.524 / 141.695 | 21.282 |
| tests.test_cli | 4 | 0.625 / 0.455 | 0.643 / 0.629 | 0.652 / 0.664 | 0.495 |
| tests.test_clock_reference | 4 | 0.008 / 0.005 | 0.007 / 0.009 | 0.008 / 0.009 | unmeasured |
| tests.test_clock | 2 | 0.001 / 0.002 | 0.001 / 0.002 | 0.002 / 0.002 | 0.002 |
| tests.test_codex_app_bridge | 2 | 0.761 / 0.830 | 0.768 / 0.770 | 0.851 / 0.824 | 2.601 |
| tests.test_codex_bridge_observer | 1 | 3.360 / 3.934 | 3.991 / 3.973 | 3.313 / 3.899 | 2.846 |
| tests.test_coldgate_charter_v3 | 3 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 | unmeasured |
| tests.test_coldgate_receipt | 2 | 0.008 / 0.014 | 0.009 / 0.014 | 0.009 / 0.016 | unmeasured |
| tests.test_collector_analysis_manifest_id | 1 | 89.358 / 166.242 | 43.301 / 176.753 | 58.425 / 175.955 | unmeasured |
| tests.test_controller | 3 | 49.887 / 43.245 | 39.856 / 50.043 | 49.336 / 52.689 | 107.263 |
| tests.test_corpus_strict_validation | 1 | 0.193 / 0.319 | 0.289 / 0.335 | 0.214 / 0.316 | 0.311 |
| tests.test_custody_mode_inventory | 4 | 67.507 / 45.572 | 71.050 / 80.550 | 73.228 / 84.182 | unmeasured |
| tests.test_d078_reason_registry | 4 | 0.137 / 0.069 | 0.124 / 0.145 | 0.138 / 0.167 | 0.142 |
| tests.test_d117_contrast_v5_pack | 3 | 14.771 / 15.258 | 10.547 / 17.724 | 14.901 / 17.546 | unmeasured |
| tests.test_d117_decode_contrast_plan | 3 | 23.033 / 25.378 | 16.717 / 26.526 | 23.220 / 26.415 | 41.604 |
| tests.test_d117_fixture_transport | 3 | 0.760 / 0.592 | 0.411 / 0.941 | 0.724 / 0.886 | 0.907 |
| tests.test_d117_floor_qwen25_1p5b_plan | 1 | 4.826 / 9.272 | 8.118 / 9.394 | 5.664 / 9.268 | 8.799 |
| tests.test_d117_floor_qwen25_7b_plan | 1 | 5.514 / 7.334 | 6.954 / 7.399 | 4.981 / 7.466 | 6.986 |
| tests.test_d117_floor_qwen3_v5_generate | 2 | 7.108 / 8.757 | 5.804 / 8.274 | 7.192 / 8.667 | unmeasured |
| tests.test_d117_gamma_d139a2_families | 1 | 2.277 / 1.792 | 1.646 / 1.815 | 1.148 / 1.772 | unmeasured |
| tests.test_d117_v3_family | 2 | 6.279 / 6.895 | 5.224 / 6.389 | 6.366 / 6.866 | 6.709 |
| tests.test_d165_dominance_closeout | 4 | 13.654 / 9.252 | 13.124 / 15.313 | 13.977 / 15.888 | unmeasured |
| tests.test_d165_rationale_census | 3 | 11.945 / 9.990 | 9.134 / 12.716 | 11.942 / 12.608 | unmeasured |
| tests.test_decisive_reference_resolution | 3 | 0.132 / 0.108 | 0.074 / 0.125 | 0.125 / 0.134 | 0.138 |
| tests.test_dependence_sensitivity | 2 | 6.454 / 7.254 | 5.301 / 6.698 | 6.157 / 7.111 | unmeasured |
| tests.test_derive_estate_anchors | 1 | 4.518 / 6.715 | 6.361 / 7.087 | 4.231 / 6.993 | unmeasured |
| tests.test_detection_floor | 2 | 8.301 / 8.886 | 6.299 / 8.109 | 7.854 / 8.870 | 3.959 |
| tests.test_determinism_gate | 3 | 16.279 / 11.537 | 10.730 / 15.003 | 16.084 / 14.964 | 14.602 |
| tests.test_docs_freshness | 2 | 0.573 / 0.735 | 0.474 / 0.673 | 0.578 / 0.725 | 0.112 |
| tests.test_doctor | 3 | 0.009 / 0.006 | 0.007 / 0.009 | 0.009 / 0.008 | 0.01 |
| tests.test_dominance_closeout | 4 | 2.102 / 1.074 | 1.853 / 2.222 | 2.138 / 2.282 | unmeasured |
| tests.test_env_locks | 3 | 0.001 / 0.000 | 0.000 / 0.001 | 0.000 / 0.001 | 0.001 |
| tests.test_envelope_gate | 2 | 30.464 / 9.426 | 39.184 / 21.648 | 20.357 / 47.521 | 9.002 |
| tests.test_environment_admission | 3 | 0.583 / 0.330 | 0.432 / 0.481 | 0.582 / 0.454 | 0.605 |
| tests.test_environment | 2 | 0.056 / 0.064 | 0.048 / 0.062 | 0.059 / 0.064 | 0.064 |
| tests.test_epoch_continuation | 3 | 30.736 / 34.311 | 25.166 / 36.299 | 30.599 / 36.107 | unmeasured |
| tests.test_epoch_equivalence_check | 2 | 6.466 / 7.794 | 6.016 / 7.369 | 7.000 / 7.593 | unmeasured |
| tests.test_experiment | 2 | 22.744 / 2.792 | 32.429 / 15.075 | 12.981 / 39.683 | 1.868 |
| tests.test_family_marker | 1 | 1.759 / 1.832 | 1.691 / 1.822 | 1.148 / 1.832 | unmeasured |
| tests.test_floor_extraction | 4 | 10.425 / 6.857 | 10.201 / 10.334 | 10.416 / 10.515 | 6.522 |
| tests.test_floor_mint_estimator | 1 | 1.859 / 3.847 | 3.474 / 3.846 | 2.154 / 3.870 | 3.211 |
| tests.test_floor_mint_pinsets_schema | 1 | 0.000 / 0.001 | 0.001 / 0.000 | 0.000 / 0.001 | 0.001 |
| tests.test_gamma_unit_roster_guard | 4 | 0.397 / 0.251 | 0.373 / 0.449 | 0.384 / 0.461 | unmeasured |
| tests.test_gate_sensibility_rounding | 3 | 0.018 / 0.013 | 0.013 / 0.016 | 0.020 / 0.016 | unmeasured |
| tests.test_gen_derivation_night | 2 | 9.416 / 10.989 | 7.715 / 10.296 | 9.185 / 10.700 | unmeasured |
| tests.test_gen_g2_phase_d | 1 | 0.029 / 0.056 | 0.047 / 0.055 | 0.035 / 0.055 | unmeasured |
| tests.test_gen_state | 4 | 3.040 / 2.125 | 3.087 / 3.282 | 3.051 / 3.343 | 2.244 |
| tests.test_generate_g2a_probe_inputs | 4 | 0.829 / 0.640 | 0.734 / 0.754 | 0.862 / 0.844 | unmeasured |
| tests.test_generate_matrix | 4 | 3.170 / 2.712 | 3.188 / 3.855 | 3.175 / 4.060 | 3.953 |
| tests.test_gensuite | 3 | 16.054 / 11.987 | 12.005 / 16.295 | 16.517 / 15.788 | 16.844 |
| tests.test_git_fixture_hygiene | 3 | 0.016 / 0.014 | 0.009 / 0.019 | 0.016 / 0.019 | unmeasured |
| tests.test_git_fixture_maintenance | 2 | 11.840 / 13.579 | 10.029 / 12.205 | 12.134 / 12.961 | unmeasured |
| tests.test_identity_pins | 1 | 4.494 / 2.024 | 1.940 / 1.965 | 1.266 / 2.148 | 1.34 |
| tests.test_idle_admission | 1 | 3.191 / 5.286 | 4.662 / 5.344 | 3.569 / 5.407 | 0.009 |
| tests.test_idle_dependence | 1 | 0.030 / 0.059 | 0.053 / 0.062 | 0.037 / 0.060 | 0.057 |
| tests.test_install_magistrate_watchdog | 1 | 2.890 / 3.529 | 3.073 / 3.718 | 2.234 / 3.570 | unmeasured |
| tests.test_install_night_agent | 4 | 7.044 / 5.911 | 7.258 / 8.244 | 7.066 / 8.462 | unmeasured |
| tests.test_interfaces | 4 | 0.016 / 0.014 | 0.016 / 0.018 | 0.015 / 0.018 | 0.022 |
| tests.test_issue_calibration_acceptance_generation | 3 | 64.140 / 72.256 | 54.751 / 76.789 | 63.841 / 76.306 | unmeasured |
| tests.test_issue_dg071_dg075_statistics | 2 | 0.548 / 0.526 | 0.442 / 0.496 | 0.518 / 0.522 | unmeasured |
| tests.test_issue_g2a_prefill_prompt_pin | 1 | 0.596 / 0.256 | 0.273 / 0.257 | 0.214 / 0.258 | unmeasured |
| tests.test_kv_size | 4 | 0.017 / 0.008 | 0.014 / 0.016 | 0.017 / 0.016 | 0.018 |
| tests.test_launch_window | 1 | 173.988 / 249.394 | 219.850 / 251.381 | 157.400 / 250.325 | 0.739 |
| tests.test_launcher_argv_regression | 4 | 0.004 / 0.002 | 0.004 / 0.004 | 0.004 / 0.004 | unmeasured |
| tests.test_load_transition_alignment | 4 | 0.343 / 0.294 | 0.353 / 0.441 | 0.343 / 0.437 | 0.456 |
| tests.test_magistrate_watchdog_cli | 2 | 11.373 / 11.519 | 11.402 / 11.947 | 11.589 / 12.041 | unmeasured |
| tests.test_magistrate_watchdog | 3 | 1.434 / 1.439 | 1.177 / 1.699 | 1.348 / 1.564 | unmeasured |
| tests.test_measurement_liveness | 1 | 0.459 / 0.050 | 0.045 / 0.046 | 0.034 / 0.050 | unmeasured |
| tests.test_microdelta_generate_configs | 3 | 0.053 / 0.034 | 0.029 / 0.051 | 0.052 / 0.050 | 0.055 |
| tests.test_midcampaign_cure_generation_docs | 4 | 0.001 / 0.000 | 0.000 / 0.001 | 0.001 / 0.000 | unmeasured |
| tests.test_mint_analysis_admission | 3 | 1.728 / 1.679 | 0.978 / 1.607 | 1.677 / 1.611 | unmeasured |
| tests.test_mint_floor_artifact_generalized | 2 | 45.549 / 52.266 | 36.514 / 48.156 | 50.213 / 51.806 | 36.229 |
| tests.test_mint_floor_artifact | 3 | 0.985 / 0.784 | 0.652 / 1.070 | 1.008 / 1.071 | 0.824 |
| tests.test_mint_policy_resolver_guard | 1 | 0.011 / 0.022 | 0.019 / 0.023 | 0.015 / 0.023 | 0.015 |
| tests.test_mlx_runtime | 3 | 0.043 / 0.034 | 0.031 / 0.047 | 0.040 / 0.040 | 0.025 |
| tests.test_mock_adapters | 2 | 0.122 / 0.125 | 0.115 / 0.121 | 0.120 / 0.124 | 0.128 |
| tests.test_model_panel | 2 | 0.006 / 0.006 | 0.005 / 0.006 | 0.006 / 0.006 | unmeasured |
| tests.test_modularity | 1 | 0.258 / 0.514 | 0.451 / 0.526 | 0.305 / 0.507 | unmeasured |
| tests.test_night_gate | 4 | 0.100 / 0.088 | 0.094 / 0.135 | 0.099 / 0.122 | unmeasured |
| tests.test_night_plan_writer | 3 | 0.018 / 0.104 | 0.014 / 0.020 | 0.018 / 0.019 | unmeasured |
| tests.test_node_client | 3 | 4.726 / 7.041 | 3.607 / 6.388 | 4.658 / 6.350 | 6.716 |
| tests.test_node_worker_subprocess | 1 | 1.585 / 2.505 | 1.983 / 2.529 | 1.490 / 2.734 | 2.674 |
| tests.test_node_worker | 1 | 1.406 / 1.596 | 1.446 / 1.601 | 1.318 / 1.651 | 1.607 |
| tests.test_nvidia_node_integration | 4 | 6.842 / 6.277 | 5.876 / 6.885 | 6.782 / 7.381 | 8.615 |
| tests.test_nvidia_smi | 3 | 0.029 / 0.033 | 0.012 / 0.048 | 0.016 / 0.035 | 0.018 |
| tests.test_p2038_production_path | 2 | 618.628 / 524.064 | 532.279 / 495.228 | 649.620 / 522.365 | 652.084 |
| tests.test_pack_capsule | 4 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 |
| tests.test_package_bundle_pack | 3 | 2.806 / 2.551 | 2.308 / 2.951 | 2.797 / 2.960 | 3.183 |
| tests.test_paper_anchor_correction_quantified | 2 | 0.175 / 0.194 | 0.161 / 0.193 | 0.169 / 0.198 | unmeasured |
| tests.test_paper_build | 1 | 0.317 / 0.313 | 0.267 / 0.316 | 0.185 / 0.323 | unmeasured |
| tests.test_paper_comparison_contract | 4 | 0.005 / 0.003 | 0.004 / 0.005 | 0.005 / 0.005 | unmeasured |
| tests.test_paper_comparison_placements | 3 | 21.026 / 15.616 | 15.193 / 20.305 | 23.185 / 20.308 | unmeasured |
| tests.test_paper_custody | 2 | 44.578 / 17.750 | 35.238 / 16.443 | 43.161 / 18.002 | unmeasured |
| tests.test_paper_excursion_decomposition | 1 | 0.150 / 0.211 | 0.188 / 0.214 | 0.167 / 0.221 | unmeasured |
| tests.test_paper_first_use_ledger | 4 | 3.439 / 1.735 | 3.513 / 2.959 | 3.450 / 3.039 | unmeasured |
| tests.test_paper_rendering | 3 | 2.145 / 0.617 | 1.476 / 0.786 | 2.134 / 0.766 | unmeasured |
| tests.test_paper_renumber_refs | 2 | 0.270 / 0.336 | 0.228 / 0.318 | 0.258 / 0.326 | unmeasured |
| tests.test_paper_replay_fence | 1 | 0.132 / 0.285 | 0.234 / 0.285 | 0.169 / 0.297 | unmeasured |
| tests.test_paper_reported_energy | 4 | 0.771 / 0.381 | 0.790 / 0.577 | 0.769 / 0.591 | unmeasured |
| tests.test_paper_round7_artifacts | 3 | 11.532 / 9.281 | 8.937 / 12.016 | 11.559 / 11.968 | unmeasured |
| tests.test_paper_successor_migration | 2 | 0.601 / 0.660 | 0.537 / 0.616 | 0.560 / 0.648 | unmeasured |
| tests.test_paper_terms_lint | 1 | 0.901 / 1.895 | 1.677 / 1.912 | 1.199 / 1.957 | unmeasured |
| tests.test_partial_record_enclosure | 4 | 14.412 / 10.126 | 13.627 / 16.725 | 14.300 / 16.471 | unmeasured |
| tests.test_phase_share | 3 | 0.009 / 0.007 | 0.006 / 0.010 | 0.009 / 0.010 | unmeasured |
| tests.test_pipeline_smoke_tail | 2 | 4.482 / 5.644 | 3.281 / 5.302 | 5.127 / 5.590 | unmeasured |
| tests.test_powermetrics_fiducial | 4 | 174.094 / 65.399 | 163.511 / 119.808 | 170.775 / 121.369 | 172.03 |
| tests.test_powermetrics | 1 | 14.223 / 20.070 | 16.668 / 20.252 | 13.867 / 20.532 | 18.553 |
| tests.test_preflight | 1 | 0.323 / 0.231 | 0.232 / 0.227 | 0.168 / 0.233 | unmeasured |
| tests.test_prewindow_check | 1 | 0.015 / 0.020 | 0.020 / 0.020 | 0.014 / 0.020 | 0.022 |
| tests.test_publication_privacy | 1 | 0.045 / 0.094 | 0.086 / 0.094 | 0.043 / 0.093 | 0.069 |
| tests.test_quiet_guard_process | 3 | 0.002 / 0.002 | 0.002 / 0.003 | 0.002 / 0.003 | 0.003 |
| tests.test_quiet_guard | 2 | 1.274 / 1.313 | 1.104 / 1.248 | 1.230 / 1.299 | 1.339 |
| tests.test_r4_acceptance_oracle | 1 | 2.727 / 5.022 | 5.172 / 5.102 | 3.648 / 5.106 | 4.709 |
| tests.test_reason_code_partition | 4 | 8.736 / 7.413 | 12.421 / 10.286 | 8.879 / 10.859 | unmeasured |
| tests.test_reauthor_clean | 1 | 0.249 / 0.182 | 0.150 / 0.178 | 0.104 / 0.186 | 0.184 |
| tests.test_receipt_histsem | 4 | 508.953 / 418.759 | 556.721 / 561.330 | 510.892 / 573.613 | 28.714 |
| tests.test_receipt_oracle | 4 | 0.133 / 0.081 | 0.118 / 0.134 | 0.139 / 0.143 | 0.113 |
| tests.test_receipt_provenance_analyzer | 1 | 0.363 / 0.757 | 0.705 / 0.742 | 0.475 / 0.772 | 0.582 |
| tests.test_reduce::remainder | 1 | 163.070 / 243.558 | 264.257 / 249.241 | 194.427 / 251.142 | 1544.46 |
| tests.test_reduce.D078R01RegressionTests.test_052_v3_measurement_stale_calibration_still_refuses_stale | 2 | 83.008 / 68.714 | 70.328 / 65.195 | 87.201 / 67.451 | 1544.46 |
| tests.test_reduce.SelfConsistentCalibrationTests.test_clock_anchor_resolves_around_every_cadence_boundary | 3 | 210.165 / 122.484 | 154.228 / 166.095 | 209.849 / 162.392 | 1544.46 |
| tests.test_reduce.D078R01RegressionTests.test_052_v3_relabelled_capture_time_refuses_its_own_taxonomy | 4 | 177.685 / 78.305 | 167.846 / 138.555 | 175.151 / 139.807 | 1544.46 |
| tests.test_rehearse_t0_unattended | 3 | 0.971 / 0.904 | 0.508 / 0.803 | 0.835 / 0.809 | unmeasured |
| tests.test_reissue_calibration_acceptance | 2 | 0.056 / 0.064 | 0.036 / 0.063 | 0.061 / 0.065 | 0.064 |
| tests.test_render_results_fills | 1 | 0.544 / 1.060 | 0.899 / 1.048 | 0.687 / 1.062 | 0.868 |
| tests.test_report | 2 | 0.581 / 0.551 | 0.381 / 0.519 | 0.543 / 0.535 | 7.283 |
| tests.test_results_prose_template | 2 | 4.660 / 5.299 | 3.925 / 5.138 | 4.665 / 5.492 | 5.269 |
| tests.test_rpt001_report_slice | 1 | 1.396 / 2.158 | 1.657 / 2.127 | 1.547 / 1.668 | 0.254 |
| tests.test_rpt002_related_work | 4 | 0.004 / 0.003 | 0.004 / 0.004 | 0.004 / 0.005 | 0.005 |
| tests.test_run_campaign | 4 | 174.751 / 142.001 | 172.581 / 188.435 | 178.202 / 190.557 | 425.536 |
| tests.test_run_night | 2 | 5.671 / 6.583 | 4.928 / 6.222 | 5.706 / 6.458 | unmeasured |
| tests.test_s0_blocked_enumeration | 1 | 1.686 / 3.265 | 3.088 / 3.213 | 2.261 / 3.274 | unmeasured |
| tests.test_s0_line_audit_guard | 4 | 0.536 / 0.456 | 0.565 / 0.589 | 0.555 / 0.582 | unmeasured |
| tests.test_salvage_dangler | 1 | 0.452 / 0.114 | 0.107 / 0.116 | 0.051 / 0.114 | 0.107 |
| tests.test_sampler_teardown | 4 | 0.081 / 0.068 | 0.082 / 0.082 | 0.082 / 0.080 | 0.095 |
| tests.test_scheduler_gates | 3 | 0.348 / 0.434 | 0.225 / 0.321 | 0.334 / 0.319 | 0.265 |
| tests.test_schemas | 4 | 0.072 / 0.033 | 0.069 / 0.068 | 0.075 / 0.067 | 0.091 |
| tests.test_sealed_bundle_compatibility | 1 | 0.558 / 1.118 | 1.010 / 1.142 | 0.758 / 1.125 | 1.14 |
| tests.test_select_g2a_prefill_length | 3 | 0.013 / 0.010 | 0.008 / 0.013 | 0.013 / 0.013 | unmeasured |
| tests.test_select_outcome_branches | 2 | 0.180 / 0.281 | 0.154 / 0.266 | 0.171 / 0.278 | unmeasured |
| tests.test_shard_split | 1 | 0.039 / 0.084 | 0.071 / 0.085 | 0.049 / 0.084 | unmeasured |
| tests.test_shard_tests | 2 | 0.635 / 0.861 | 0.521 / 1.051 | 0.724 / 0.822 | 0.834 |
| tests.test_single_count_discipline_census | 4 | 17.189 / 10.909 | 17.364 / 20.997 | 17.975 / 21.034 | unmeasured |
| tests.test_single_count_discipline_matrix | 3 | 9.239 / 7.024 | 6.566 / 9.025 | 9.112 / 8.928 | unmeasured |
| tests.test_ssh_transport | 4 | 0.001 / 0.000 | 0.001 / 0.001 | 0.001 / 0.001 | 0.003 |
| tests.test_suite_control_parity | 2 | 0.006 / 0.005 | 0.005 / 0.005 | 0.006 / 0.005 | 0.006 |
| tests.test_suite | 4 | 0.061 / 0.021 | 0.060 / 0.043 | 0.061 / 0.049 | 0.052 |
| tests.test_summarize_g2a_prefill_probe | 2 | 0.333 / 0.393 | 0.222 / 0.390 | 0.375 / 0.400 | unmeasured |
| tests.test_supersession_cross_consumer | 1 | 0.035 / 0.073 | 0.069 / 0.072 | 0.035 / 0.074 | unmeasured |
| tests.test_t0_rehearsal | 4 | 5.631 / 3.808 | 5.571 / 6.281 | 5.672 / 6.377 | unmeasured |
| tests.test_uncertainty_evidence | 2 | 0.885 / 0.683 | 0.748 / 0.670 | 0.933 / 0.674 | 0.93 |
| tests.test_uncertainty_p2029 | 3 | 1.591 / 1.234 | 0.826 / 1.399 | 1.530 / 1.432 | 20.798 |
| tests.test_validate_gate_packet | 4 | 2.126 / 2.087 | 2.219 / 3.277 | 2.140 / 3.192 | 2.94 |
| tests.test_validate_powermetrics_fiducial_derivation_only | 2 | 183.075 / 131.499 | 154.719 / 124.913 | 190.181 / 125.070 | unmeasured |
| tests.test_validate_powermetrics_fiducial | 3 | 5.147 / 9.314 | 4.233 / 5.992 | 5.079 / 5.943 | unmeasured |
| tests.test_vllm_runtime | 2 | 0.012 / 0.015 | 0.011 / 0.014 | 0.013 / 0.013 | 0.011 |
| tests.test_whole_window_selection | 3 | 284.427 / 170.065 | 211.793 / 217.124 | 285.462 / 216.170 | 498.852 |
| tests.test_whole_window | 2 | 4.063 / 3.957 | 3.130 / 3.656 | 3.946 / 3.915 | 0.763 |
| tests.test_window_duration_margins | 2 | 14.274 / 16.687 | 11.673 / 15.213 | 14.628 / 16.180 | 16.633 |
| tests.test_window_env_allowlist | 1 | 0.011 / 0.023 | 0.023 / 0.024 | 0.016 / 0.024 | unmeasured |
| tests.test_window_status_guard | 4 | 0.997 / 0.718 | 1.029 / 1.163 | 0.976 / 1.131 | unmeasured |
| tests.test_workload_profile | 3 | 0.003 / 0.002 | 0.002 / 0.003 | 0.003 / 0.003 | unmeasured |
| tests.test_workload_sizing | 2 | 0.001 / 0.002 | 0.001 / 0.002 | 0.001 / 0.002 | unmeasured |
| tests.test_workloads | 1 | 0.027 / 0.038 | 0.052 / 0.038 | 0.037 / 0.039 | 0.051 |
| tests.test_write_derivation_night_inputs | 1 | 2.520 / 0.576 | 0.546 / 0.565 | 0.473 / 0.575 | unmeasured |

## Appendix B — literal latest three green code-changing push heads

Resolved after the initial latest-run analysis, before workflow/timing edits. Selection: `git log -12 --first-parent --format='%h %s' -- . ':!docs' ':!*.md'`, checked against successful main/push run records and each commit's first-parent diff. The latest three qualifying heads change tests/test_gen_state.py (fidelity pins), alongside bookkeeping. This supplies the literal requested population in addition to the latest full-matrix runs. C1/C2/C3 below are 35051177531 / 35034962874 / 35006580578. They use the same module roster/partition. Timings will conservatively pool **all six runs**, 12 observations per ordinary module, to incorporate both this literal population and the freshest hosted speeds.

| Code run | Head | Workflow min | Runner-min | Critical execution | Wait + execution min |
|---|---|---:|---:|---|---|
| [35051177531](https://github.com/mpmdw/JouleWise/actions/runs/35051177531) | 62131e59 | 24.67 | 182.13 | test (3.11, 2) | 0.07 + 24.60 |
| [35034962874](https://github.com/mpmdw/JouleWise/actions/runs/35034962874) | e055611b | 25.62 | 197.75 | test (3.11, 4) | 2.60 + 23.00 |
| [35006580578](https://github.com/mpmdw/JouleWise/actions/runs/35006580578) | 404ba6b3 | 53.33 | 200.98 | test (3.14, 2) | 32.37 + 20.97 |

C3's 53.33 minutes is dominated by a 32.37-minute start delay; C1 is almost unqueued, showing a 24.60-minute execution ceiling. Thus both the literal code-push population and latest full-matrix population support the same diagnosis.

### Code-push job table

Cells: ready-queue/start delay min / execution min / setup seconds (wheel ready time is build completion).

| Job | C1 | C2 | C3 |
|---|---:|---:|---:|
| build | 0.07 / 0.33 / — | 0.65 / 0.28 / — | 23.43 / 0.30 / — |
| calibration-exits-exclusive (3.11) | 0.07 / 18.20 / 17 | 0.05 / 18.87 / 16 | 27.70 / 13.78 / 15 |
| calibration-exits-exclusive (3.14) | 0.08 / 13.72 / 18 | 0.63 / 11.48 / 17 | 26.10 / 14.18 / 18 |
| calibration-writer-crash-matrix-exclusive (3.11, 1) | 0.05 / 7.57 / 15 | 0.80 / 11.50 / 15 | 32.03 / 9.98 / 17 |
| calibration-writer-crash-matrix-exclusive (3.11, 2) | 0.05 / 5.67 / 16 | 3.25 / 5.82 / 15 | 31.57 / 5.57 / 16 |
| calibration-writer-crash-matrix-exclusive (3.14, 1) | 0.07 / 4.18 / 12 | 6.05 / 7.85 / 16 | 23.50 / 8.02 / 17 |
| calibration-writer-crash-matrix-exclusive (3.14, 2) | 0.05 / 4.10 / 18 | 0.05 / 2.70 / 14 | 30.85 / 4.13 / 18 |
| fences | 0.07 / 0.63 / — | 0.05 / 0.70 / — | 23.80 / 0.68 / — |
| installed-wheel | 0.05 / 0.25 / — | 6.42 / 0.23 / — | 9.92 / 0.15 / — |
| test (3.11, 1) | 0.07 / 13.95 / 26 | 0.05 / 14.70 / 28 | 24.88 / 11.15 / 29 |
| test (3.11, 2) | 0.07 / 24.60 / 28 | 0.05 / 18.32 / 25 | 25.15 / 22.00 / 27 |
| test (3.11, 3) | 0.07 / 15.18 / 25 | 5.88 / 14.73 / 26 | 26.38 / 12.73 / 31 |
| test (3.11, 4) | 0.07 / 16.37 / 22 | 2.60 / 23.00 / 25 | 25.38 / 23.83 / 27 |
| test (3.14, 1) | 0.07 / 9.37 / 26 | 2.80 / 15.83 / 28 | 28.48 / 16.15 / 28 |
| test (3.14, 2) | 0.07 / 16.85 / 27 | 0.98 / 14.90 / 24 | 32.37 / 20.97 / 26 |
| test (3.14, 3) | 0.07 / 13.83 / 32 | 0.07 / 12.53 / 34 | 27.37 / 13.67 / 27 |
| test (3.14, 4) | 0.07 / 17.33 / 25 | 0.05 / 24.30 / 29 | 26.77 / 23.68 / 27 |

| Exclusive work | C1 3.11 / 3.14 s | C2 3.11 / 3.14 s | C3 3.11 / 3.14 s |
|---|---:|---:|---:|
| Calibration exits | 1069.506 / 799.820 | 1112.329 / 669.021 | 810.273 / 830.381 |
| Crash heavy unit | 434.313 / 236.780 | 673.181 / 452.671 | 576.637 / 460.050 |
| Crash remainder | 322.279 / 225.412 | 331.860 / 143.500 | 315.041 / 225.719 |

### Every code-push shard/module observation

| Module or reduce unit | Old shard | C1 s (3.11 / 3.14) | C2 s | C3 s |
|---|---:|---:|---:|---:|
| tests.test_2k_amplification | 2 | 0.065 / 0.116 | 0.057 / 0.107 | 0.106 / 0.116 |
| tests.test_adapters_powermetrics | 3 | 3.561 / 4.252 | 3.453 / 3.831 | 3.223 / 4.233 |
| tests.test_admit_model_panel_entry | 2 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 |
| tests.test_aggregate | 3 | 0.037 / 0.038 | 0.034 / 0.026 | 0.023 / 0.039 |
| tests.test_analysis_claims | 2 | 0.398 / 0.283 | 0.298 / 0.274 | 0.355 / 0.369 |
| tests.test_analysis_engine | 3 | 0.025 / 0.033 | 0.024 / 0.030 | 0.022 / 0.032 |
| tests.test_analysis_finalizer | 4 | 12.059 / 13.911 | 24.041 / 26.496 | 24.524 / 26.087 |
| tests.test_analysis_inputs | 4 | 9.837 / 16.382 | 15.935 / 17.648 | 16.386 / 17.167 |
| tests.test_analysis_integration | 2 | 81.882 / 60.737 | 63.271 / 53.828 | 66.544 / 84.362 |
| tests.test_analysis_manifest_v2 | 3 | 0.002 / 0.002 | 0.002 / 0.002 | 0.002 / 0.003 |
| tests.test_analysis_manifest_v3 | 2 | 0.982 / 0.652 | 0.691 / 0.525 | 0.725 / 0.954 |
| tests.test_analysis_manifest | 4 | 4.077 / 4.879 | 3.804 / 4.728 | 3.971 / 4.495 |
| tests.test_analysis_multiplicity | 1 | 0.010 / 0.008 | 0.009 / 0.010 | 0.007 / 0.010 |
| tests.test_analysis_ratio_integration | 2 | 0.039 / 0.030 | 0.032 / 0.030 | 0.036 / 0.038 |
| tests.test_analysis_ratio | 2 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 |
| tests.test_arm_readiness_dry_run | 4 | 17.833 / 23.940 | 26.716 / 31.751 | 27.375 / 30.600 |
| tests.test_arm_readiness_evidence_author | 3 | 46.653 / 52.572 | 49.441 / 46.164 | 43.888 / 52.273 |
| tests.test_arm_readiness_evidence_packauth | 4 | 21.450 / 27.167 | 30.264 / 34.623 | 30.206 / 32.950 |
| tests.test_arm_readiness_evidence_t0 | 2 | 67.723 / 60.487 | 61.134 / 46.378 | 57.421 / 66.978 |
| tests.test_arm_readiness_evidence | 2 | 0.251 / 0.208 | 0.349 / 0.178 | 0.212 / 0.251 |
| tests.test_arm_readiness_integration | 1 | 30.588 / 26.832 | 30.721 / 30.246 | 28.603 / 29.850 |
| tests.test_arm_readiness_lifecycle | 4 | 16.809 / 24.581 | 19.255 / 20.405 | 20.168 / 19.696 |
| tests.test_arm_readiness_pack_digest | 3 | 0.299 / 0.304 | 0.323 / 0.227 | 0.375 / 0.302 |
| tests.test_arm_readiness_registry | 1 | 14.005 / 13.316 | 14.090 / 16.799 | 12.877 / 16.549 |
| tests.test_arm_readiness_schemas | 4 | 0.269 / 0.293 | 0.215 / 0.199 | 0.220 / 0.199 |
| tests.test_arm_readiness | 4 | 6.915 / 14.999 | 8.475 / 9.972 | 9.083 / 9.405 |
| tests.test_audit_amplification | 3 | 5.306 / 5.520 | 5.291 / 5.344 | 5.359 / 5.521 |
| tests.test_audit_bundle_validation | 4 | 0.836 / 1.072 | 1.474 / 1.578 | 1.543 / 1.584 |
| tests.test_audit_cli_examples | 4 | 0.056 / 0.071 | 0.102 / 0.106 | 0.110 / 0.107 |
| tests.test_audit_clock | 3 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| tests.test_audit_powermetrics_parser | 2 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 |
| tests.test_audit_reduce_degenerate | 4 | 0.125 / 0.181 | 0.239 / 0.263 | 0.261 / 0.258 |
| tests.test_audit_report | 1 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| tests.test_audit_schema_edges | 3 | 0.005 / 0.006 | 0.004 / 0.005 | 0.004 / 0.005 |
| tests.test_authentication_io | 3 | 1.600 / 1.999 | 1.673 / 1.948 | 1.339 / 1.951 |
| tests.test_axi_analysis_manifest | 4 | 0.214 / 0.141 | 0.180 / 0.206 | 0.187 / 0.206 |
| tests.test_axi_burst_reduce | 4 | 0.608 / 1.032 | 0.652 / 0.786 | 0.668 / 0.762 |
| tests.test_axi_controller_events | 1 | 2.627 / 0.460 | 3.112 / 4.324 | 1.300 / 4.751 |
| tests.test_axi_mock_spec | 2 | 23.246 / 22.232 | 6.400 / 19.427 | 15.416 / 26.465 |
| tests.test_axi_output_identity | 3 | 0.072 / 0.076 | 0.066 / 0.056 | 0.047 / 0.076 |
| tests.test_axi_request_validation | 3 | 0.095 / 0.100 | 0.088 / 0.072 | 0.061 / 0.098 |
| tests.test_axi_sb_spike | 2 | 0.011 / 0.009 | 0.009 / 0.008 | 0.010 / 0.010 |
| tests.test_axi_sc_spike | 2 | 0.029 / 0.023 | 0.022 / 0.020 | 0.024 / 0.028 |
| tests.test_axi_schemas | 4 | 0.007 / 0.005 | 0.010 / 0.009 | 0.011 / 0.010 |
| tests.test_benchmark_import | 3 | 0.113 / 0.086 | 0.111 / 0.075 | 0.090 / 0.085 |
| tests.test_bracket_binding_cli | 2 | 16.925 / 12.623 | 12.710 / 10.375 | 12.444 / 17.791 |
| tests.test_bridge | 4 | 20.391 / 24.987 | 23.023 / 33.099 | 24.402 / 32.566 |
| tests.test_build_capstone | 4 | 0.000 / 0.000 | 0.001 / 0.001 | 0.001 / 0.001 |
| tests.test_build_site_parsers | 4 | 0.000 / 0.000 | 0.001 / 0.001 | 0.001 / 0.001 |
| tests.test_bundle_read | 4 | 2.808 / 3.807 | 4.924 / 5.419 | 5.497 / 5.329 |
| tests.test_bundle | 3 | 3.304 / 3.536 | 3.487 / 2.966 | 3.719 / 3.491 |
| tests.test_calibration_bracketing | 3 | 0.499 / 0.526 | 0.502 / 0.496 | 0.446 / 0.515 |
| tests.test_calibration_custody_store | 1 | 0.112 / 0.415 | 0.116 / 0.131 | 0.310 / 0.124 |
| tests.test_calibration_ledger_custody | 3 | 0.972 / 1.017 | 0.970 / 1.006 | 1.080 / 1.014 |
| tests.test_calibration_ledger | 4 | 4.690 / 4.002 | 3.384 / 3.867 | 3.436 / 3.978 |
| tests.test_calibration_live_three_window | 3 | 2.540 / 2.716 | 2.392 / 2.447 | 2.795 / 2.740 |
| tests.test_campaign_generator_core | 2 | 2.070 / 1.885 | 1.633 / 1.715 | 1.838 / 2.423 |
| tests.test_capture_pipeline_era | 3 | 2.418 / 2.447 | 2.413 / 2.430 | 2.381 / 2.447 |
| tests.test_capture_t0_step | 2 | 4.718 / 4.436 | 3.934 / 3.203 | 3.953 / 4.627 |
| tests.test_check_gate_ledger | 4 | 0.854 / 1.219 | 1.177 / 2.061 | 1.299 / 2.020 |
| tests.test_check_paper_replay_fence | 3 | 0.163 / 0.190 | 0.166 / 0.189 | 0.155 / 0.187 |
| tests.test_check_window_provenance | 2 | 16.989 / 13.381 | 12.496 / 10.312 | 12.338 / 17.771 |
| tests.test_claim_side_bound | 1 | 0.051 / 0.041 | 0.051 / 0.057 | 0.036 / 0.057 |
| tests.test_claims_index_lint | 3 | 3.205 / 3.609 | 3.281 / 3.422 | 2.768 / 3.624 |
| tests.test_claims_lint | 2 | 2.987 / 2.890 | 2.447 / 2.766 | 2.779 / 3.368 |
| tests.test_claude_bridge_mcp | 3 | 1.303 / 1.581 | 1.349 / 3.100 | 1.208 / 1.479 |
| tests.test_cli_run | 1 | 83.946 / 29.140 | 96.075 / 127.555 | 50.542 / 138.053 |
| tests.test_cli | 4 | 0.327 / 0.399 | 0.606 / 0.644 | 0.661 / 0.642 |
| tests.test_clock_reference | 4 | 0.005 / 0.004 | 0.008 / 0.009 | 0.009 / 0.009 |
| tests.test_clock | 2 | 0.002 / 0.001 | 0.001 / 0.001 | 0.002 / 0.001 |
| tests.test_codex_app_bridge | 2 | 0.828 / 1.120 | 0.800 / 0.766 | 0.770 / 0.780 |
| tests.test_codex_bridge_observer | 1 | 3.916 / 3.519 | 3.916 / 3.959 | 3.572 / 3.873 |
| tests.test_coldgate_charter_v3 | 3 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.002 |
| tests.test_coldgate_receipt | 2 | 0.009 / 0.013 | 0.008 / 0.013 | 0.008 / 0.014 |
| tests.test_collector_analysis_manifest_id | 1 | 104.087 / 36.665 | 119.493 / 158.711 | 64.626 / 171.625 |
| tests.test_controller | 3 | 49.186 / 52.865 | 44.369 / 48.337 | 40.784 / 51.003 |
| tests.test_corpus_strict_validation | 1 | 0.275 / 0.250 | 0.293 / 0.315 | 0.248 / 0.304 |
| tests.test_custody_mode_inventory | 4 | 42.979 / 41.410 | 66.983 / 87.535 | 72.246 / 86.364 |
| tests.test_d078_reason_registry | 4 | 0.057 / 0.069 | 0.136 / 0.145 | 0.138 / 0.158 |
| tests.test_d117_contrast_v5_pack | 3 | 15.036 / 17.860 | 14.754 / 15.442 | 13.034 / 18.097 |
| tests.test_d117_decode_contrast_plan | 3 | 22.770 / 26.622 | 22.625 / 23.860 | 18.375 / 26.466 |
| tests.test_d117_fixture_transport | 3 | 0.758 / 0.905 | 0.675 / 0.621 | 0.429 / 0.901 |
| tests.test_d117_floor_qwen25_1p5b_plan | 1 | 7.723 / 7.048 | 8.029 / 9.164 | 7.292 / 9.013 |
| tests.test_d117_floor_qwen25_7b_plan | 1 | 6.632 / 5.988 | 6.896 / 7.352 | 6.557 / 7.064 |
| tests.test_d117_floor_qwen3_v5_generate | 2 | 7.235 / 6.756 | 6.129 / 6.261 | 6.548 / 8.635 |
| tests.test_d117_gamma_d139a2_families | 1 | 1.593 / 1.320 | 1.648 / 1.770 | 1.412 / 1.720 |
| tests.test_d117_v3_family | 2 | 6.353 / 5.404 | 5.084 / 5.042 | 5.701 / 6.781 |
| tests.test_d165_dominance_closeout | 4 | 8.037 / 8.291 | 13.512 / 15.660 | 14.201 / 15.042 |
| tests.test_d165_rationale_census | 3 | 11.575 / 12.832 | 11.756 / 11.285 | 9.761 / 12.704 |
| tests.test_decisive_reference_resolution | 3 | 0.092 / 0.132 | 0.121 / 0.130 | 0.094 / 0.125 |
| tests.test_dependence_sensitivity | 2 | 6.202 / 6.190 | 5.178 / 5.813 | 5.799 / 7.072 |
| tests.test_derive_estate_anchors | 1 | 5.413 / 5.170 | 6.067 / 6.588 | 5.975 / 6.324 |
| tests.test_detection_floor | 2 | 7.938 / 7.681 | 8.940 / 6.375 | 7.088 / 8.577 |
| tests.test_determinism_gate | 3 | 15.687 / 15.267 | 15.724 / 12.522 | 11.471 / 15.155 |
| tests.test_docs_freshness | 2 | 0.570 / 0.545 | 0.467 / 0.499 | 0.487 / 0.710 |
| tests.test_doctor | 3 | 0.009 / 0.009 | 0.009 / 0.007 | 0.009 / 0.009 |
| tests.test_dominance_closeout | 4 | 1.337 / 1.095 | 2.102 / 2.249 | 2.124 / 2.197 |
| tests.test_env_locks | 3 | 0.001 / 0.001 | 0.001 / 0.001 | 0.000 / 0.001 |
| tests.test_envelope_gate | 2 | 42.763 / 39.215 | 13.288 / 34.140 | 29.130 / 47.288 |
| tests.test_environment_admission | 3 | 0.613 / 0.469 | 0.592 / 0.404 | 0.488 / 0.472 |
| tests.test_environment | 2 | 0.062 / 0.046 | 0.046 / 0.041 | 0.050 / 0.063 |
| tests.test_epoch_continuation | 3 | 33.112 / 36.685 | 30.466 / 31.620 | 34.675 / 36.737 |
| tests.test_epoch_equivalence_check | 2 | 7.255 / 7.937 | 6.015 / 5.585 | 6.254 / 7.548 |
| tests.test_experiment | 2 | 34.851 / 33.440 | 7.788 / 28.741 | 21.970 / 39.637 |
| tests.test_family_marker | 1 | 1.554 / 1.416 | 1.619 / 1.791 | 1.885 / 1.716 |
| tests.test_floor_extraction | 4 | 10.594 / 7.468 | 10.364 / 10.423 | 10.633 / 10.111 |
| tests.test_floor_mint_estimator | 1 | 3.354 / 2.726 | 3.419 / 3.778 | 2.649 / 3.730 |
| tests.test_floor_mint_pinsets_schema | 1 | 0.001 / 0.000 | 0.001 / 0.001 | 0.000 / 0.001 |
| tests.test_gamma_unit_roster_guard | 4 | 0.252 / 0.249 | 0.380 / 0.454 | 0.384 / 0.444 |
| tests.test_gate_sensibility_rounding | 3 | 0.020 / 0.016 | 0.017 / 0.014 | 0.014 / 0.019 |
| tests.test_gen_derivation_night | 2 | 9.653 / 9.004 | 7.789 / 8.442 | 8.446 / 10.883 |
| tests.test_gen_g2_phase_d | 1 | 0.044 / 0.044 | 0.045 / 0.056 | 0.038 / 0.053 |
| tests.test_gen_state | 4 | 2.040 / 1.935 | 2.987 / 3.321 | 3.042 / 3.199 |
| tests.test_generate_g2a_probe_inputs | 4 | 1.448 / 0.605 | 1.096 / 0.774 | 0.850 / 0.966 |
| tests.test_generate_matrix | 4 | 2.356 / 3.004 | 3.145 / 3.935 | 3.270 / 3.781 |
| tests.test_gensuite | 3 | 16.840 / 16.891 | 16.223 / 14.213 | 13.299 / 16.379 |
| tests.test_git_fixture_hygiene | 3 | 0.016 / 0.019 | 0.016 / 0.013 | 0.009 / 0.019 |
| tests.test_git_fixture_maintenance | 2 | 12.363 / 9.985 | 10.315 / 9.461 | 12.007 / 13.309 |
| tests.test_identity_pins | 1 | 1.839 / 1.560 | 1.889 / 2.033 | 5.906 / 1.865 |
| tests.test_idle_admission | 1 | 4.565 / 4.144 | 4.645 / 5.370 | 3.739 / 5.227 |
| tests.test_idle_dependence | 1 | 0.052 / 0.043 | 0.054 / 0.060 | 0.041 / 0.058 |
| tests.test_install_magistrate_watchdog | 1 | 2.905 / 3.477 | 3.009 / 3.597 | 3.683 / 3.391 |
| tests.test_install_night_agent | 4 | 6.781 / 6.931 | 6.959 / 8.561 | 7.283 / 8.131 |
| tests.test_interfaces | 4 | 0.207 / 0.133 | 0.015 / 0.018 | 0.016 / 0.018 |
| tests.test_issue_calibration_acceptance_generation | 3 | 66.007 / 77.553 | 63.661 / 75.350 | 70.090 / 77.548 |
| tests.test_issue_dg071_dg075_statistics | 2 | 0.515 / 0.444 | 0.586 / 0.382 | 0.471 / 0.513 |
| tests.test_issue_g2a_prefill_prompt_pin | 1 | 0.268 / 0.200 | 0.283 / 0.249 | 0.511 / 0.234 |
| tests.test_kv_size | 4 | 0.010 / 0.008 | 0.017 / 0.015 | 0.020 / 0.015 |
| tests.test_launch_window | 1 | 208.373 / 203.953 | 213.114 / 248.790 | 198.721 / 242.139 |
| tests.test_launcher_argv_regression | 4 | 0.003 / 0.002 | 0.004 / 0.004 | 0.004 / 0.003 |
| tests.test_load_transition_alignment | 4 | 0.309 / 0.318 | 0.344 / 0.457 | 0.356 / 0.427 |
| tests.test_magistrate_watchdog_cli | 2 | 11.688 / 11.349 | 11.893 / 11.652 | 11.891 / 11.988 |
| tests.test_magistrate_watchdog | 3 | 1.404 / 1.684 | 1.320 / 1.401 | 1.287 / 1.635 |
| tests.test_measurement_liveness | 1 | 0.042 / 0.035 | 0.046 / 0.044 | 0.035 / 0.046 |
| tests.test_microdelta_generate_configs | 3 | 0.055 / 0.052 | 0.050 / 0.034 | 0.036 / 0.051 |
| tests.test_midcampaign_cure_generation_docs | 4 | 0.000 / 0.000 | 0.000 / 0.001 | 0.000 / 0.000 |
| tests.test_mint_analysis_admission | 3 | 1.604 / 1.696 | 1.682 / 1.205 | 1.125 / 1.665 |
| tests.test_mint_floor_artifact_generalized | 2 | 51.061 / 36.818 | 37.904 / 31.968 | 41.810 / 51.213 |
| tests.test_mint_floor_artifact | 3 | 1.021 / 1.093 | 0.968 / 0.887 | 0.750 / 1.088 |
| tests.test_mint_policy_resolver_guard | 1 | 0.018 / 0.016 | 0.018 / 0.022 | 0.014 / 0.022 |
| tests.test_mlx_runtime | 3 | 0.040 / 0.047 | 0.041 / 0.044 | 0.030 / 0.042 |
| tests.test_mock_adapters | 2 | 0.122 / 0.116 | 0.115 / 0.116 | 0.119 / 0.123 |
| tests.test_model_panel | 2 | 0.006 / 0.004 | 0.005 / 0.005 | 0.006 / 0.006 |
| tests.test_modularity | 1 | 0.413 / 0.421 | 0.416 / 0.511 | 0.325 / 0.500 |
| tests.test_night_gate | 4 | 0.261 / 0.214 | 0.107 / 0.132 | 0.098 / 0.130 |
| tests.test_night_plan_writer | 3 | 0.020 / 0.020 | 0.018 / 0.016 | 0.014 / 0.020 |
| tests.test_node_client | 3 | 4.452 / 6.509 | 4.665 / 6.019 | 4.213 / 6.347 |
| tests.test_node_worker_subprocess | 1 | 1.846 / 2.446 | 1.850 / 2.541 | 1.853 / 2.340 |
| tests.test_node_worker | 1 | 1.439 / 1.498 | 1.438 / 1.619 | 1.338 / 1.574 |
| tests.test_nvidia_node_integration | 4 | 18.019 / 19.045 | 8.439 / 6.949 | 6.693 / 8.934 |
| tests.test_nvidia_smi | 3 | 0.016 / 0.069 | 0.016 / 0.038 | 0.028 / 0.041 |
| tests.test_p2038_production_path | 2 | 660.313 / 413.175 | 497.613 / 376.630 | 616.423 / 526.025 |
| tests.test_pack_capsule | 4 | 0.001 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 |
| tests.test_package_bundle_pack | 3 | 2.801 / 2.972 | 2.800 / 2.684 | 2.418 / 3.011 |
| tests.test_paper_anchor_correction_quantified | 2 | 0.189 / 0.181 | 0.156 / 0.178 | 0.166 / 0.199 |
| tests.test_paper_build | 1 | 0.261 / 0.269 | 0.259 / 0.365 | 0.200 / 0.305 |
| tests.test_paper_comparison_contract | 4 | 0.003 / 0.002 | 0.004 / 0.007 | 0.005 / 0.005 |
| tests.test_paper_comparison_placements | 3 | 21.718 / 20.126 | 20.919 / 17.394 | 16.608 / 20.103 |
| tests.test_paper_custody | 2 | 48.086 / 17.060 | 39.840 / 12.686 | 39.052 / 18.515 |
| tests.test_paper_excursion_decomposition | 1 | 0.179 / 0.198 | 0.180 / 0.215 | 0.168 / 0.209 |
| tests.test_paper_first_use_ledger | 4 | 2.297 / 1.703 | 3.427 / 3.025 | 3.446 / 2.935 |
| tests.test_paper_rendering | 3 | 2.080 / 0.805 | 2.085 / 0.665 | 1.657 / 0.778 |
| tests.test_paper_renumber_refs | 2 | 0.272 / 0.278 | 0.222 / 0.255 | 0.242 / 0.352 |
| tests.test_paper_replay_fence | 1 | 0.220 / 0.237 | 0.220 / 0.276 | 0.177 / 0.276 |
| tests.test_paper_reported_energy | 4 | 0.485 / 1.098 | 0.754 / 0.586 | 0.810 / 0.563 |
| tests.test_paper_round7_artifacts | 3 | 11.328 / 12.009 | 11.819 / 10.164 | 9.829 / 12.069 |
| tests.test_paper_successor_migration | 2 | 0.584 / 0.534 | 0.501 / 0.530 | 0.564 / 0.689 |
| tests.test_paper_terms_lint | 1 | 1.648 / 1.406 | 1.643 / 1.893 | 1.247 / 1.875 |
| tests.test_partial_record_enclosure | 4 | 8.268 / 9.585 | 13.782 / 16.413 | 14.317 / 16.045 |
| tests.test_phase_share | 3 | 0.010 / 0.010 | 0.012 / 0.007 | 0.006 / 0.010 |
| tests.test_pipeline_smoke_tail | 2 | 5.296 / 3.826 | 3.907 / 3.143 | 3.780 / 5.792 |
| tests.test_powermetrics_fiducial | 4 | 102.821 / 67.368 | 169.950 / 120.455 | 172.027 / 118.905 |
| tests.test_powermetrics | 1 | 17.295 / 15.261 | 17.611 / 20.132 | 14.499 / 19.923 |
| tests.test_preflight | 1 | 0.228 / 0.325 | 0.224 / 0.234 | 0.223 / 0.222 |
| tests.test_prewindow_check | 1 | 0.020 / 0.017 | 0.019 / 0.021 | 0.016 / 0.019 |
| tests.test_publication_privacy | 1 | 0.086 / 0.063 | 0.084 / 0.093 | 0.061 / 0.091 |
| tests.test_quiet_guard_process | 3 | 0.003 / 0.003 | 0.002 / 0.003 | 0.002 / 0.003 |
| tests.test_quiet_guard | 2 | 1.270 / 1.454 | 1.126 / 1.099 | 1.099 / 1.389 |
| tests.test_r4_acceptance_oracle | 1 | 5.015 / 3.305 | 5.125 / 5.002 | 3.278 / 4.932 |
| tests.test_reason_code_partition | 4 | 5.824 / 5.471 | 8.649 / 11.220 | 9.131 / 10.109 |
| tests.test_reauthor_clean | 1 | 0.144 / 0.221 | 0.146 / 0.181 | 0.334 / 0.176 |
| tests.test_receipt_histsem | 4 | 363.130 / 424.974 | 499.809 / 573.022 | 521.478 / 553.397 |
| tests.test_receipt_oracle | 4 | 0.092 / 0.087 | 0.116 / 0.133 | 0.128 / 0.137 |
| tests.test_receipt_provenance_analyzer | 1 | 0.668 / 0.643 | 0.657 / 0.791 | 0.524 / 0.727 |
| tests.test_reduce::remainder | 1 | 284.714 / 151.012 | 294.107 / 241.842 | 204.088 / 245.645 |
| tests.test_reduce.D078R01RegressionTests.test_052_v3_measurement_stale_calibration_still_refuses_stale | 2 | 87.337 / 52.949 | 66.413 / 48.650 | 82.266 / 69.271 |
| tests.test_reduce.SelfConsistentCalibrationTests.test_clock_anchor_resolves_around_every_cadence_boundary | 3 | 212.575 / 168.429 | 212.049 / 152.518 | 171.906 / 168.844 |
| tests.test_reduce.D078R01RegressionTests.test_052_v3_relabelled_capture_time_refuses_its_own_taxonomy | 4 | 106.499 / 78.752 | 174.349 / 139.209 | 176.678 / 137.366 |
| tests.test_rehearse_t0_unattended | 3 | 0.818 / 0.831 | 0.825 / 0.626 | 0.643 / 0.840 |
| tests.test_reissue_calibration_acceptance | 2 | 0.062 / 0.045 | 0.044 / 0.031 | 0.043 / 0.068 |
| tests.test_render_results_fills | 1 | 0.894 / 0.832 | 0.903 / 1.047 | 0.708 / 1.028 |
| tests.test_report | 2 | 0.561 / 0.485 | 0.487 / 0.344 | 0.429 / 0.596 |
| tests.test_results_prose_template | 2 | 4.635 / 4.220 | 3.981 / 3.771 | 4.520 / 5.221 |
| tests.test_rpt001_report_slice | 1 | 1.670 / 1.476 | 1.505 / 2.152 | 1.740 / 1.927 |
| tests.test_rpt002_related_work | 4 | 0.003 / 0.002 | 0.004 / 0.005 | 0.004 / 0.004 |
| tests.test_run_campaign | 4 | 134.390 / 145.391 | 174.152 / 192.628 | 177.762 / 189.150 |
| tests.test_run_night | 2 | 5.833 / 5.622 | 5.022 / 5.160 | 5.312 / 7.149 |
| tests.test_s0_blocked_enumeration | 1 | 2.677 / 2.952 | 2.982 / 3.264 | 3.097 / 3.082 |
| tests.test_s0_line_audit_guard | 4 | 0.365 / 0.422 | 0.522 / 0.591 | 0.562 / 0.560 |
| tests.test_salvage_dangler | 1 | 0.104 / 0.087 | 0.105 / 0.115 | 0.234 / 0.113 |
| tests.test_sampler_teardown | 4 | 0.069 / 0.071 | 0.080 / 0.080 | 0.082 / 0.079 |
| tests.test_scheduler_gates | 3 | 0.316 / 0.327 | 0.331 / 0.256 | 0.291 / 0.328 |
| tests.test_schemas | 4 | 0.041 / 0.045 | 0.070 / 0.067 | 0.069 / 0.071 |
| tests.test_sealed_bundle_compatibility | 1 | 0.952 / 0.969 | 1.012 / 1.112 | 0.833 / 1.091 |
| tests.test_select_g2a_prefill_length | 3 | 0.014 / 0.013 | 0.013 / 0.010 | 0.009 / 0.013 |
| tests.test_select_outcome_branches | 2 | 0.173 / 0.235 | 0.146 / 0.228 | 0.165 / 0.305 |
| tests.test_shard_split | 1 | 0.068 / 0.068 | 0.069 / 0.084 | 0.057 / 0.082 |
| tests.test_shard_tests | 2 | 0.711 / 0.629 | 0.547 / 0.608 | 0.693 / 0.900 |
| tests.test_single_count_discipline_census | 4 | 10.667 / 10.727 | 17.058 / 21.519 | 19.281 / 20.384 |
| tests.test_single_count_discipline_matrix | 3 | 8.640 / 8.937 | 8.874 / 8.480 | 6.912 / 9.086 |
| tests.test_ssh_transport | 4 | 0.000 / 0.001 | 0.001 / 0.001 | 0.001 / 0.001 |
| tests.test_suite_control_parity | 2 | 0.006 / 0.004 | 0.005 / 0.004 | 0.005 / 0.005 |
| tests.test_suite | 4 | 0.041 / 0.022 | 0.060 / 0.042 | 0.065 / 0.042 |
| tests.test_summarize_g2a_prefill_probe | 2 | 0.420 / 0.274 | 0.292 / 0.187 | 0.248 / 0.434 |
| tests.test_supersession_cross_consumer | 1 | 0.069 / 0.049 | 0.070 / 0.074 | 0.048 / 0.071 |
| tests.test_t0_rehearsal | 4 | 4.231 / 6.519 | 5.601 / 6.245 | 6.293 / 6.068 |
| tests.test_uncertainty_evidence | 2 | 0.931 / 0.472 | 0.725 / 0.459 | 0.853 / 0.671 |
| tests.test_uncertainty_p2029 | 3 | 1.389 / 1.456 | 1.506 / 1.060 | 0.917 / 1.428 |
| tests.test_validate_gate_packet | 4 | 1.396 / 2.033 | 2.076 / 3.300 | 2.467 / 3.089 |
| tests.test_validate_powermetrics_fiducial_derivation_only | 2 | 189.851 / 107.624 | 141.035 / 93.968 | 182.321 / 128.042 |
| tests.test_validate_powermetrics_fiducial | 3 | 5.557 / 6.063 | 5.040 / 5.247 | 5.652 / 6.025 |
| tests.test_vllm_runtime | 2 | 0.013 / 0.011 | 0.045 / 0.009 | 0.011 / 0.014 |
| tests.test_whole_window_selection | 3 | 301.633 / 218.013 | 284.654 / 198.041 | 221.902 / 219.639 |
| tests.test_whole_window | 2 | 3.954 / 3.582 | 6.361 / 2.633 | 3.092 / 3.988 |
| tests.test_window_duration_margins | 2 | 15.290 / 12.371 | 12.234 / 11.272 | 13.655 / 16.532 |
| tests.test_window_env_allowlist | 1 | 0.024 / 0.019 | 0.023 / 0.024 | 0.017 / 0.023 |
| tests.test_window_status_guard | 4 | 0.657 / 0.749 | 0.967 / 1.160 | 1.193 / 1.087 |
| tests.test_workload_profile | 3 | 0.003 / 0.003 | 0.003 / 0.002 | 0.002 / 0.003 |
| tests.test_workload_sizing | 2 | 0.002 / 0.001 | 0.001 / 0.001 | 0.001 / 0.002 |
| tests.test_workloads | 1 | 0.064 / 0.029 | 0.052 / 0.038 | 0.043 / 0.038 |
| tests.test_write_derivation_night_inputs | 1 | 0.519 / 0.439 | 0.549 / 0.580 | 0.610 / 0.557 |

## Replay of cheap verification

These commands only inspect/partition; they do not execute test bodies. The workflow dry harness intercepts run_units and executes only the partition code and JSON timing validators.

<!-- CHECK:yaml -->
```sh
ruby -rjson -ryaml -ropen3 - <<'RB'
p = '.github/workflows/ci.yml'
a = YAML.load(`git show b11fdd502d2180c1a28c45348fcae3a839fff115:#{p}`)
b = YAML.load_file(p)
ids = %w[test calibration-exits-exclusive calibration-writer-crash-matrix-exclusive]
expr = '${{ fromJSON(needs.changes.outputs.pythons) }}'
raise 'job IDs changed' unless b['jobs'].keys.sort == (a['jobs'].keys + ['changes']).sort
raise 'workflow metadata changed' unless a.reject { |k, _| k == 'jobs' } == b.reject { |k, _| k == 'jobs' }
a['jobs'].each do |id, job|
  current = Marshal.load(Marshal.dump(b['jobs'][id]))
  if ids.include?(id)
    raise 'dependency changed' unless current.delete('needs') == 'changes'
    raise 'matrix expression changed' unless current['strategy']['matrix']['python-version'] == expr
    current['strategy']['matrix']['python-version'] = job['strategy']['matrix']['python-version']
  end
  raise "existing job body/names changed: #{id}" unless current == job
end
selector = b['jobs']['changes']
full = '["3.11","3.13","3.14"]'
raise 'output fallback changed' unless selector['outputs']['pythons'] == "${{ steps.interpreters.outputs.pythons || '#{full}' }}"
raise 'unexpected selector steps' unless selector['steps'].size == 1
step = selector['steps'].first
raise 'selector not pure Bash' unless step['shell'] == 'bash' && step['id'] == 'interpreters' && !step.key?('uses')
script = step.fetch('run')
_, err, status = Open3.capture3('bash', '-n', stdin_data: script)
raise err unless status.success?
sink = '>> "$GITHUB_OUTPUT"'
raise 'unexpected output sink' unless script.scan(sink).size == 1
dry_script = script.sub(sink, '>&1')
events = ['pull_request', 'push', 'workflow_dispatch', 'pull_request_target', 'unknown', '', nil]
events.each do |event|
  expected = event == 'pull_request' ? ['3.13'] : JSON.parse(full)
  out, err, status = Open3.capture3({'GITHUB_EVENT_NAME' => event}, 'bash', '--noprofile', '--norc', '-euo', 'pipefail', '-c', dry_script)
  raise err unless status.success?
  raise 'invalid output record' unless out.lines.size == 1 && out.start_with?('pythons=')
  versions = JSON.parse(out.delete_prefix('pythons='))
  raise 'wrong interpreter selection' unless versions == expected
  counts = ids.map { |id| versions.size * b['jobs'][id]['strategy']['matrix'].fetch('shard', [1]).size }
  raise 'wrong matrix cardinality' unless counts == (event == 'pull_request' ? [6, 1, 2] : [18, 3, 6])
  raise 'wrong total jobs' unless counts.sum + 4 == (event == 'pull_request' ? 13 : 31)
end
puts 'YAML PASS; six existing jobs and steps preserved; only matrix axes/dependencies changed'
puts 'MATRIX DRY PASS; seven event cases; PR 13 jobs; non-PR 31 jobs; no test bodies executed'
RB
```

<!-- CHECK:partition -->
```sh
python3 -B - <<'PY'
import collections, json, sys
sys.path.insert(0, 'scripts')
import shard_tests as s
p=json.load(open('scripts/test_timings.json'))
mods=s.discover_test_modules(); exclusive=set(p['exclusive_modules'])
assert exclusive <= set(mods)
assert set(p['seconds_by_module']) == set(mods)
splits=s.load_split_declarations(); unknown=s.conservative_unknown_weight()
for label, selected, count in [('ordinary', tuple(m for m in mods if m not in exclusive), 6), ('crash', ('tests.test_calibration_writer_crash_matrix',), 2)]:
 units, weights=s.expand_units(selected, s.load_timing_map(), splits, unknown_weight=unknown)
 parts=s.partition_modules(units, weights, count, unknown_weight=unknown)
 assert collections.Counter(u for part in parts for u in part)==collections.Counter(units)
 for module in set(selected)&set(splits):
  ids=s.discover_test_ids(module); assigned=[]
  for part in parts:
   owned=[u for u in part if u==module+s.REMAINDER_SUFFIX or u.startswith(module+'.')]
   assigned.extend(s.resolve_units_to_test_ids(module, owned, ids, splits[module]['declared']))
  assert collections.Counter(assigned)==collections.Counter(ids)
 print(label, 'units=', len(units), 'totals=', ','.join(f'{x:.3f}' for x in s.partition_totals(parts, weights)))
print('PARTITION PASS; 230 modules covered; split test IDs scheduled exactly once; no tests executed')
PY
```

<!-- CHECK:inline -->
```sh
python3 -B - <<'PY'
import ast, json, os, re, subprocess, sys
sys.path.insert(0, 'scripts')
import shard_tests as s
w=json.loads(subprocess.check_output(['ruby','-rjson','-ryaml','-e',"puts JSON.generate(YAML.load_file('.github/workflows/ci.yml'))"],text=True))
for job in w['jobs'].values():
 for step in job['steps']:
  code=step.get('run','')
  for body in re.findall(r"<<'PY'[^\n]*\n(.*?)^PY\s*$",code,re.M|re.S):
   ast.parse(body)
   if step.get('name')=='Validate exclusive timing declaration':
    exec(compile(body,'<exclusive-declaration>','exec'),{})
job=w['jobs']['test']
step=next(x for x in job['steps'] if x.get('name','').startswith('Unit tests'))
body=step['run'].split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0]
os.environ.update(job['env'])
seen=[]
def record(units,count,index):
 assert count==6 and 1<=index<=count
 seen.extend(units)
 return 0
s.run_units=record
for index in job['strategy']['matrix']['shard']:
 os.environ['SHARD_INDEX']=str(index)
 try: exec(compile(body,'<ordinary-ci>','exec'),{})
 except SystemExit as ex: assert ex.code==0
assert len(seen)==len(set(seen))==231
print('WORKFLOW DRY PASS; Python heredocs parse; exclusive pins pass; six inline partitions cover 231 units')
PY
```

### CI-only acceptance / lead handoff

Only hosted CI can establish that the new distribution passes both interpreters with unchanged test census (including the existing skip profile), no process/cache/order dependency regressions, no dropped exclusive work, and all build/fences/wheel jobs green. Compare created-to-completed wall AND job-ready-to-start delays against both populations, not just max shard duration. A run arriving into an empty queue should conservatively fit ~19–20 minutes; a backlogged run may not improve total wall even when ordinary jobs fall to ~14 minutes. The user prohibited local full-suite execution and this worker has no commit/push/CI-trigger authority; the lead's next step is review the three-file patch, commit/push it through its own authorized route, and inspect that hosted CI run. No new oracle was removed. Branch protection requires the lead's authenticated read because the connector cannot access it.

During inspection origin/main advanced from the requested base to ef05a0fc06ba8817ce24fbaa526f2f2415509b43 through another actor's shared-ref update. This session did not fetch or change HEAD; its worktree HEAD remains exactly BASE_HEAD. Rebase/integration is lead-owned if required.

Final scope check: **SCOPE_OK**, active lease lease-239b475119db449cb1926ebfd884e60f, HEAD unchanged, exactly three persistent modified paths (workflow, timing map, this plan). No unowned dirty paths. git diff --check passed. scripts/shard_tests.py was inspected and its API used unchanged. No test file writes, test-body execution, or scope expansion required.

```sh
python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-ci2-20260915.json --expect-digest sha256:a2f626a87cba9f54533dcf36d093759e011310ef82cf6d399b000fd0e9a0a472 --lease-id lease-239b475119db449cb1926ebfd884e60f --scope .github/workflows/ci.yml scripts/test_timings.json scripts/shard_tests.py docs/process_traces/2026-09-15-interactive-b0ae8462/10-ci-trim-2-astra-plan.md
```

## Measurement 1 (magistrate, run 35060083430 on PR #340 at b11fdd50: 6×2 shards, both interpreters)

success, wall 35.1 min. Shard execution 6.9–15.3 min (was 10–24); queue waits 8–21 min on every job (21 jobs).
Conclusion: execution is now under the calibration-exits floor; the queue is the wall clock. Next commit: PRs run
Python 3.13 only (13 jobs), main pushes 3.11 + 3.13 (Ed's ruling 23:10; 3.14 is exercised by every seat's local
module runs, not by CI).

## Measurement 2 — docs-only queue pressure (lead-reported, 2026-09-16)

Tonight's evidence supplied by the lead: approximately 30 docs-only bookkeeping
pushes to main each triggered the full 21-job matrix and stalled the queue for
30 minutes. This worker did not independently fetch run records or measure
hosted execution. Ed's 00:20 PDT ruling above authorizes the step-3 skip;
expected result is approximately four short jobs per docs-only push instead
of the prior 21/31-job configurations. Hosted confirmation remains lead-owned.

## Measurement 2 (magistrate, rerun 35062628747 of 4685bab8 under GitHub Pro, 13 jobs: PRs on 3.13 only)

The rerun sat 56 minutes behind a pile of docs-only bookkeeping runs on main (each a full 21-job matrix; cancelled at
00:10 PDT, see record ci-queue lesson), then ALL 13 jobs started within 60 s of each other (Pro's 40-job cap) and the
run's execution wall was the longest job: test (3.13, 2) at 14.2 min; calibration-exits 10.7; shards 9.4–14.2.
Conclusion: with the queue clear, a PR's CI ≈ 15 min. Next: measurement 3 on this head (quick gate + docs-only skip).
