# Readiness before the MBP needs it

The lead updates [`next_steps.json`](../../configs/readiness/next_steps.json)
**whenever a step is planned**, its lane changes, or a prerequisite/ruling
changes. Keep the ordered queue R1 → R1-to-W1 chain → W1 smoke → W1 → D1
current, and remove completed steps. The first two entries run every time.
This list is a readiness projection; it does not replace project coordination
state or grant launch authority.

A step **may not be scheduled on the MBP while RED**. UNKNOWN also requires
resolution before scheduling. **RED within 24 hours of the earliest time the
MBP could reach that step is a critical-path alarm**: the lead prioritizes
repair or a ruled alternative immediately. Silence, stale status, skipped
tests and a green upstream step do not establish downstream readiness.

Run off the measurement host, from the canonical gate checkout:

```sh
python3.13 -B scripts/readiness_next2.py --output tmp/readiness/status.json
```

The default is offline and resolves cached `origin/<branch>` refs. The GitHub
[workflow](../../.github/workflows/readiness.yml) adds `--fetch`, every three
hours and on pushes to `lane/**`, `align/**`, `fix/**` and `main`. It always
uses the gate/list from `main`, fetches the named step branches, checks out
detached temporary worktrees and removes them afterward. No dependency
installation or model download is performed. RED exits 1, UNKNOWN exits 2,
GREEN exits 0. The job stays visibly failed and uploads JSON/Markdown even
on RED; do not make this advisory check required in branch protection.
Push triggers take effect on branches carrying this workflow after it lands.
Hourly local scheduling uses the [Air plist template](../ops/readiness-air.plist.md).

The status lists each prerequisite, exact checkout SHA, command, stdout,
stderr, unittest result, earliest MBP hour and UTC timestamp, plus the
critical-path alarm. A checkout failure marks its remaining prerequisites
UNKNOWN, individually; it also reports `no arm route: checkout unavailable`.
Malformed configuration is RED. A status file older than four hours is
UNKNOWN. Only trust results for the exact code the magistrate will run.
Commands share a 20-minute budget (`--budget-seconds` overrides it); each
also has its own timeout. Expired budgets and timed-out required checks are
RED, with their reasons retained. Commands and their subprocess groups are
killed on timeout; subsequent independent presence checks still run. Git
operations have separate 120-second timeouts, so the workflow's 45-minute
limit leaves time to publish the final artifact.

## What each entry must say

`defaults` holds shared step fields to keep the five-entry list small.
Step dictionaries merge recursively into those defaults; arrays and explicit
nulls replace them. Review the effective entry, particularly stage-specific
kit fields and commands, when changing an override.

- `id`, `branch` (without `origin/`) and `commit`: branch tip is used when
  commit is null, and the resolved full SHA is always recorded. To freeze a
  reviewed implementation, supply its full 40-character commit. It must be
  an ancestor of the named branch. No fallback to another branch is allowed.
- `arm.live_command`: the exact live argv for the magistrate, for review
  only. **The gate never executes it.** A null command is `no arm route` RED.
- `arm.route_files`, `arm.exercises` and `arm.synthetic`: the repository
  files that must exist, and the reviewed seam that goes through
  the real arm/launch path end to end using FakeWorld, `--dry-arm` or a
  synthetic runtime. A driver-only rehearsal or a WP22 controller run does
  not prove installer, night-driver or launcher admission. The lead must
  verify that these paths are exercised before entering a seam.
- `arm.synthetic.argv`, `timeout_s`, and `assert_json`: synthetic argv can
  use `{python}`, `{tree}` and `{scratch}`. It must create its success record
  under scratch. `assert_json.path` is relative to scratch; `equals` maps
  dotted JSON fields to required values. Both a zero exit and matching
  assertions are required; a zero-exit refusal is RED. Nonzero exits retain
  the exact refusal. The seam owns mapping intentional negative controls to
  a positive, machine-readable completion verdict.
- `kit.path`, `required_fields` (dotted JSON leaves), and `check` (an argv
  command, normally `scripts/align_v4_kit.py --check`). Empty, missing and
  `PENDING*`/`TODO*`/`TBD*` values are RED. Values are not echoed. Select the
  kit/check for the current stage: R1's own future outputs must not become
  prerequisites to arming R1. At this baseline the R1-specific interface is
  absent, explicitly RED; W1's full `--check` runs on the chain entry.
- `evidence`: every ruling/receipt with `name` and repository-relative
  `path`; optionally `sha256` and required `contains` strings. Null, absent,
  empty or mismatched evidence is RED. Include the independent Sol/Opus
  design agreement and lead ruling required by RUN_STATE 220. The lead
  supplies code-only attestations for real receipts; the gate never follows
  host paths embedded in configuration. Presence alone does not authenticate
  or rule on a receipt: pin its hash/contents when that is required.
- `prequal.stage` and `checks`: explicitly list applicable **offline**
  `align_v4_prequal.py` checks. The runner calls that script with `--offline`
  and `--only`. Its overall exit 3 is expected for a selected subset;
  **each selected check must be present and `pass`**. A passing row stays
  GREEN when the script exits 1 for a failing sibling. `fail`, `not_run`, a
  missing script, an unknown check, or any other exit is RED. Network,
  downloaded-model and native Metal checks stay in separate lead-owned
  qualification; they are not silently counted as passing here.
- `tests`: exact unittest modules/classes/methods, optional `env`, and
  timeout in seconds. List both default selectors and every required opt-in
  selector with its enabling environment. The initial list includes
  `tests.align.test_v4_w1_synthetic` with **`JW_WP22_FULL=1`**. Each runs in
  a fresh interpreter against the selected branch. Any required skip,
  expected failure, unexpected success, zero-test selection, error, failure
  or timeout is RED. All skipped identities and reasons are retained.
- `mbp_available_at`: a timezone-bearing timestamp at list level. Null
  conservatively means available now. `minimum_duration_hours` for each
  step supplies a **lower bound**, not a typical duration or an upper cap;
  cumulative lower bounds determine the earliest hours. Use zero when no
  defensible lower bound exists. Do not reset availability into the future
  to clear an alarm.

The manifest is trusted executable configuration, reviewed like code. Enter
only synthetic commands that operate on code and their own temporary
fixtures. No shell is used. Children get isolated HOME/cache/TMPDIR locations
and HF/transformers offline settings. These are hygiene controls, not an OS
sandbox: the seam must not load real models, read real data, install a
LaunchAgent or collect hardware evidence. Repository-relative checks refuse
external, traversal, symlink and `restricted/` receipt/config paths.

## Baseline gaps intentionally visible

The initial list records the state at `origin/main` `dcfa4c593`: R1 has no
agreed arm route or lead ruling; the R1-to-W1 synthetic arm chain is not
specified; the native smoke lane is still being built. Null fields record
these gaps and keep the relevant rows RED. They are not executable guesses.
The integrated R1 branch is a candidate source for downstream checks, not
an assertion that the magistrate will run it unchanged. The lead fills each
exact branch, commit, command and receipt as the agreement lands.

WP22 runs the real controller and desk with synthetic native streams; its
default quick tests previously left the full window behind an opt-in.
Running those quick tests alone can no longer satisfy this gate. Native
MLX/Metal, pinned stack/model qualification, and the ≤45-minute native W1
smoke still need the lead's separate checks outside this sandbox. Synthetic
GREEN proves software prerequisites only and preserves PROVISIONAL hardware
labels.
