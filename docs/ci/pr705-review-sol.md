# PR #705 executing review — Sol

**Verdict: ADMIT_WITH_FIXES.** The required fix is applied locally in
`bc0deba7cca72ad3b7554b79a8783ec62634c360` on
`ci/2026-11-08-nightly-optin`. No remaining source-level blocker was found.
Nothing was pushed; the standing no-network/no-push rule takes precedence over
the brief's parenthetical push request.

Review date: 2026-11-08. Original PR head:
`6eea14a3a0cd5698c66a333c6e9b676b830d4159`. Audit source:
`origin/perf/2026-11-08-optin-audit` at
`f7c081e8426b96a2be3977f74a44119d9c5cf0c1`,
`docs/perf/2026-11-08-optin-audit.md`. This is a light-tier CI review; it changes
no estimator, measurement, calibration, registration, model, or study data.

## Finding and disposition

**F1 — dispatch ref interpreted as shell source (fixed).** The header step
interpolated `${{ matrix.ref }}` directly into a double-quoted shell command.
The ref is controlled by the manual `align_ref` input. A local reproduction
using a Git-valid ref of the form `review/$(touch${IFS}<temporary-marker>)`
created the marker while the header step returned zero. This needs no checkout
or network to demonstrate; it is a defect in how the header renders the ref.

The fix binds the expression through the step's `REQUESTED_REF` environment
variable and logs `"requested_ref=$REQUESTED_REF"`. The regression test executes
the actual header script and verifies literal logging and absence of the marker.
The other interpolated header fields are fixed workflow matrix values.

The comment claiming WP22 is currently red was also changed to describe the
audit's historical failure. The inspected ALIGN ref has advanced and contains
the contrast-proof refresh; this review did not rerun a full window and does not
assert its current result.

## Acceptance checks

| Requirement | Evidence and result |
| --- | --- |
| Schedule/dispatch only | Only `schedule` (`17 6 * * *`, UTC) and `workflow_dispatch` are declared. No push, PR, or reusable-workflow trigger. PASS. |
| Non-required nightly | Explicit non-required header; isolated job names `optin (<entry>)`; no edits to existing required workflows. GitHub branch protection/rulesets are remote configuration and were **not verified offline**. Confirm these contexts are absent from required checks before merge. |
| WP22 lane | `JW_WP22_FULL=1`, `tests.align.test_v4_w1_synthetic`, default/scheduled ref `align/2026-11-08-v4-r11`, 60-minute timeout. Dispatch can override the ref. The module exists on the lane, not the reviewed mainline tree. PASS. |
| Full scored corpus | Four separate `JOULEWISE_FULL_CORPUS=1` entries: `tests.test_scored_packer_stress`, `tests.test_scored_packer_fuzz`, `tests.test_scored_ownership_forgery`, `tests.test_scored_reduce`; each checks out `main` with a 240-minute job timeout. PASS. |
| Approved full-size recompute | `JW_B5_FULLSIZE_RECOMPUTE=1`, class selector `tests.independent_recompute.test_member_pool.FullSizeMemberPoolTests`, `main`, 120-minute timeout. This does not select the other member-pool classes. PASS. |
| Non-zero exit fails | No `continue-on-error`; Bash pipeline failure is fatal. Synthetic assertion/import failures, unexpected success, and explicit exit 7 all fail. PASS. |
| ANY skip fails | Every matrix entry has `max_skips: 0`. Actual verbose unittest method, class-setup, and subtest skips all fail the shell step. No skip allowance is used. PASS. |
| Zero tests fails | Empty module fails (Python 3.13 returns 5); an exit-zero probe reporting `Ran 0 tests` also fails the explicit shell guard. Missing summary fails. PASS. |
| Accepted expected failure | WP22's documented `expectedFailure` remains accepted; an unexpected success fails. An expected failure is not counted as a skip. PASS. |
| Logs | Header records requested ref, actual Git head, opt-in, selector and interpreter; `tee` captures combined stdout/stderr. `actions/upload-artifact@v5` uses `if: always()`, unique matrix artifact names and 30-day retention. No-file behavior is `warn` (e.g. setup failure). Runner loss/hard cancellation can still prevent an upload; no hosted upload was exercised. |
| Process isolation | One quoted selector is passed to one `python -B -m unittest -v` process per matrix job. A failing neighboring synthetic module is not discovered. `fail-fast: false` keeps another red matrix job from cancelling its peers. PASS. |
| Actions/dependencies | `checkout@v5`, `setup-python@v6`, `upload-artifact@v5` match existing workflow version conventions. Python 3.13, stdlib tests; zsh explicitly provisioned. `fetch-depth: 0` supports pinned Git provenance replays. PASS by source inspection/YAML parsing. |
| Secrets | No user-configured secrets or external credentials referenced. `permissions: contents: read`; checkout uses the ordinary automatically supplied GitHub token. PASS. |
| Blinding | GitHub-hosted `ubuntu-latest`, no self-hosted runner, measurement-machine connection, data mount, archive input or download of model weights. All entries enable synthetic paths; MLX/live/external/S10 full-chain opt-ins are omitted. PASS for the inspected source, with the limits below. |

The default interpreter is GitHub's Bash with `-e`; the script additionally sets
`pipefail`. Consequently a non-zero test process can exit the step before the
explicit `PIPESTATUS` diagnostic is reached. That affects the custom diagnostic,
not the red status or the already-written test log. Simulations used `bash -e`
to match that behavior.

## Synthetic-data boundary

The four scored modules and their fixture generators/checkers build synthetic
Python structures. WP22 replaces telemetry, the thermal transport and task inputs
with synthetic implementations. The full-size class restores only the committed
S10 synthetic archives into a temporary directory and invokes
`scripts/independent_recompute_b5.py` with explicit synthetic roots. The restore
uses `tarfile`'s `filter="data"`. Its custody-shaped archive names refer to
synthetic fixtures, not host study custody. The parent package's discovery hook
is not selected by the explicit class selector.

`JW_B5_SYNTHETIC_ONLY=1` short-circuits external archive availability probes in
the independent-recompute helper before `path.exists()`. It is **not** a general
filesystem sandbox. The assurance here comes from the inspected synthetic
call paths and the fresh hosted runner without study mounts. A future change to
the checked-out branch still needs review; this workflow executes repository
code at the chosen ref.

## Executed verification and limits

```sh
PYTHONNOUSERSITE=1 PYTHONPATH= GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  python3.13 -S -B -m unittest -v tests.test_nightly_optin
```

**PASS: 14 tests, 3.353 seconds.** Each child invocation runs one tiny temporary
module, serially. This directly executes the extracted workflow scripts, rather
than replacing their skip/exit logic with a separate implementation.

Additional checks: PASS for Psych YAML parsing and static assertions covering
triggers, six entries, zero skip ceilings, corpus timeouts, hosted runner,
read-only permissions, action versions and always-upload; PASS for `bash -n`
on all three run blocks; PASS for in-memory Python compilation of the new test;
PASS for `git diff --check`. `actionlint` was not available and was not installed.
GitHub expression evaluation and actual runner/artifact behavior were not tested.

The initial new-test run had 12 passes and one harness failure: the zero-test
witness expected exit 1 but Python 3.13 correctly returned 5. The witness now
accepts any non-zero result and separately tests an exit-zero/zero-count probe.
This was a test expectation repair, not a workflow defect. Total unittest time
for both runs was 6.680 seconds. An initial static-check helper also needed an
old-Ruby compatibility adjustment (`map.compact` instead of `filter_map`).

No full suite, expensive corpus body, full-size extraction, WP22 window,
measurement campaign, block-5 analysis pipeline, native MLX test, or model
download was run. No conclusion about those test bodies' current green status
is implied. No native qualification is needed for this workflow-only fix; native
suites excluded from this workflow retain their separate lead-controlled gates.

Boundary caveat: initial shell/Git inventory calls and one later bare Git diff
check used default configuration. Their implicit shell/global-Git configuration
reads were not traced, so I cannot certify zero out-of-clone metadata/config
access for those calls. No sealed outcome content was intentionally opened.
Hardened calls disabled login startup, Python user-site imports and global/system
Git configuration. All deliberate source reads were confined to the clone and
permitted Git objects; executable probes used temporary synthetic inputs.

Next step: the lead reviews `bc0deba7c`, confirms the nightly's contexts are not
required in GitHub settings, and transfers the local fast-forward fix under its
network authority. Once the workflow is on the default branch, dispatch it and
inspect all six job statuses, counts and uploaded logs. Keep the current local
8-worker analysis job untouched. Coordination-state files were not edited.
