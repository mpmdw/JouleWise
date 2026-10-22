# Watchdog block-six running-session fix, round 2

Repository: `mpmdw/JouleWise`; branch: `fix/2026-10-16-watchdog-b6-bindings` (existing PR #500).
Base: `5f4620d71ddba8a27d4e8e577e7482f3d20918db`. Date: 2026-10-16.

## Findings

- **MAJOR-1 confirmed and fixed.** At the original head, installed-only block-six plans reached the separate launch fence but never entered `decide()`'s active-plan list or the resident's plan selection. A live owned session received no request, TERM, or KILL. The final regressions reproduce this against the exact original source.
- **MINOR-1 confirmed and fixed.** Installed-only plans were absent from fenced-checkout triples and armed-plan conflict checks. They now enter both through the same snapshot as custody-scanned plans.
- **MINOR-2 fixed.** Added eight watchdog regression methods using the existing process, clock, storage, and child fakes. Ported the lane's three optional-binding validator tests verbatim from `2b2bea4cc:tests/test_night_gate.py`; the current validator accepts them without a production validator edit.
- A readable installed plan must retain its absolute deadlines when the other installed plist is malformed. Snapshot loading now retains readable siblings while collecting errors. The launch decision remains `HOLD_UNSAFE`, and the existing resident drain uses the readable plan's TERM/KILL deadlines.

## What changed

- `scripts/magistrate_watchdog.py`: `load_plans()` combines scanned plans and installed night/deadman plans. Deduplication uses `(plan_id, resolved source plan path)`. Every installed plist is validated even when its plan is already present. Installed parsing errors join snapshot errors; standalone installed-fence callers still receive the existing exceptions. `decide()`, the resident, launch-boundary checks, and remote-probe suppression consume the combined snapshot through their existing paths. Removed the redundant installed-only launch decisions.
- `tests/test_magistrate_watchdog_b6.py`: production-shaped HAZARD_PACK plans live under temporary `night-b6/sessions/<id>/custody/night_plan.json`, genuinely outside the storage scan. The existing `fake_window.hazard_plan_mapping` supplies the block-five writer shape; the fixture adds the lane's `capture_screen` mapping of three decimal strings and `spare_retries=False`, then parses it through `NightPlan.from_mapping`. No path under `/Users` was accessed or changed.
- `tests/test_magistrate_watchdog.py` and `tests/test_magistrate_watchdog_span.py`: updated installed-only expectations to the common census, plan precedence, stand-down, and unsafe-drain behavior. Existing scanned v2/block-five lifecycle expectations remain intact.
- `tests/test_night_gate.py`: the three lane tests are unchanged copies, covering optional bindings and preserved types, all fourteen required string bindings and unknown keys, and malformed optional values.
- `configs/gates/hazard_refusals.json`: updated four affected rows using `tests.hazards.refusal_census`'s computed counts and guard hashes; reclassified those changed frozen-baseline entries as INTERNAL, with explanations of their supervisory effect. The frozen baseline was not edited.

`joulewise/night_gate.py` and `tests/test_b5_plan.py` needed no changes. All repository writes are within WRITE_SCOPE. No other repository file is needed.

## Decisions I made

1. Unify discovery at the existing plan snapshot instead of widening the custody glob or creating another stand-down implementation. This gives installed plans the existing launch fence, running-session ladder, checkout triples, conflicts, yield notices, terminal release, completion, open-chain, and courier/deadman handling.
2. Use the exact requested identity: plan ID plus resolved source plan path. Symlink aliases and the night/deadman references collapse; the same ID at different paths remains distinct and participates in conflict checks.
3. Validate every installed plist before deduplication, so a duplicate reference cannot conceal a malformed plist. Collect per-plist errors for snapshot callers so valid siblings survive regardless of which plist is malformed; keep standalone fence failures closed.
4. Give installed plans the same census and local-STOP precedence as scanned plans. Thus installed-only empty-census decisions use the common `plan span active and census empty` reason, and a live owner gets `STANDDOWN_*`. The standalone `installed_agent_fence()` reason remains `installed_plan:<id>`, deduplicated.
5. Keep all timing and release predicates unchanged. REQUEST remains t0-180, TERM t0-90, and KILL t0-60; t0-70 is still TERM. No tolerance, threshold, timing constant, or measurement-data/printed-number policy was added or changed. No NEEDS_RULING choice arose.
6. Use focused synthetic tests only, as requested; do not run the full suite or a live measurement. Leave deployment, merging, and hardware validation to the lead. Do not create or merge a PR.

## Original-head regression evidence

The initial seven watchdog methods were run before editing production code: all seven failed (including subtest failures), while all three ported validator tests passed. After adding the readable-sibling case and finalizing test expectations, I replayed **all eight final watchdog methods** against the exact source from `git show 5f4620d71:scripts/magistrate_watchdog.py`, executed into the already-imported watchdog module in a separate Python process. Every method failed by assertion, with no fixture errors:

| Method in `InstalledBlockSixTests` | Failure on original head |
| --- | --- |
| `test_decide_owned_installed_plan_phases_and_completion` | Missing checkout triple at t0-600; `FENCED` instead of REQUEST/TERM/KILL for live owner. |
| `test_resident_requests_terms_and_kills_installed_plan_at_existing_leads` | `standdown.request` absent at the existing REQUEST boundary. |
| `test_resident_first_sees_installed_plan_in_window_and_after_completion` | Resident continues instead of killing the live owner at t0+60. |
| `test_plan_deduplicates_across_scan_night_and_deadman_resolved_paths` | Duplicate `installed_plan:` reasons for the same resolved plan. |
| `test_installed_conflicts_include_same_id_at_distinct_paths_and_scanned_plans` | `LAUNCHING` instead of `HOLD_UNSAFE` for both installed/installed and installed/scanned conflicts. |
| `test_installed_terminal_release_is_census_backed_and_latched` | `FENCED` instead of the census-backed terminal-release path's `HOLD_CENSUS`. |
| `test_unreadable_installed_plist_drains_resident_before_any_span` | `NETWORK_UNCERTAIN` instead of an unsafe-plan resident drain. |
| `test_readable_installed_sibling_keeps_deadlines_when_other_plist_is_torn` | Same missing unsafe-plan drain with either night or deadman plist torn. |

Reproduction of the final original-source replay (the original source is changed only in memory; no checkout files are replaced):

```bash
export TMPDIR=$(mktemp -d)
export JW_B5_SYNTHETIC_ONLY=1
export PYTHONDONTWRITEBYTECODE=1
python3.13 - <<'PY'
import io
import subprocess
import unittest
from scripts import magistrate_watchdog as wd
from tests.test_magistrate_watchdog_b6 import InstalledBlockSixTests
original = subprocess.check_output(
    ['git', 'show', '5f4620d71:scripts/magistrate_watchdog.py'], text=True)
exec(compile(original, wd.__file__, 'exec'), wd.__dict__)
all_failed = True
for name in unittest.defaultTestLoader.getTestCaseNames(InstalledBlockSixTests):
    result = unittest.TextTestRunner(stream=io.StringIO()).run(
        unittest.TestSuite([InstalledBlockSixTests(name)]))
    red = not result.wasSuccessful() and not result.errors
    all_failed &= red
    print(name, 'EXPECTED FAIL' if red else 'UNEXPECTED RESULT')
assert all_failed
PY
```

Outcome: exit 0 from the replay harness; all eight methods report EXPECTED FAIL. The three **ported** validator tests intentionally pass on the original head because that head already includes the validator fix; they are compatibility coverage, not new watchdog regression claims.

The fixed tests exercise a live owned session at t0-600, t0-170, t0-90, t0-70, and t0+60, plus after `plan_completion_epoch`. The resident sequence additionally asserts the exact REQUEST/TERM/KILL boundaries, request payload deadlines, descendant signals, owned-tree removal, the inclusive completion fence, post-completion launch with delivered courier, and one-way census-backed early release. Both installed labels and scanned symlink aliases are covered.

## Commands run and outcomes

Every test invocation exported a newly created `TMPDIR` and `JW_B5_SYNTHETIC_ONLY=1`; `PYTHONDONTWRITEBYTECODE=1` was also set. Interpreter: `/usr/bin/python3.13`, Python 3.13.5.

- Inspected `AGENTS.md`, Mission M0, relevant run-state/queue/orchestration instructions, watchdog code and tests, and the lane's session-path/plan shape. No active stop card or global work-selection gate; the direct bounded task supplies authority. Scope prohibits unrelated bookkeeping updates.
- `git status --short --branch`, `git rev-parse HEAD`, branch/log/remote inspection: initial checkout was clean at `d79e03549`; no pre-existing changes were overwritten.
- `git fetch origin fix/2026-10-16-watchdog-b6-bindings lane/2026-10-16-b6-round2`: passed. Verified `5f4620d71` and switched the clean checkout to the requested task branch at that commit. Remote `git ls-remote` checks confirmed the original branch head before delivery.
- `git show 2b2bea4cc:tests/test_night_gate.py` and targeted lane-source reads: the three tests apply verbatim. Their initial run passed unchanged.
- Initial new-watchdog/ported-validator run: 10 methods, seven watchdog methods red (12 assertion failures including subtests), three validator methods green. Initial fixed-code run identified test expectations needing correction: t0-70 is TERM, clock movement must stay forward, and a released resident needs a deterministic remote observation. Corrected those fixtures; no timing constants changed.
- First required-module run plus the initial new module: 383 tests, 10 reported failures, two skips. Failures were the old installed-only behavioral expectations and the expected refusal-census drift; these were resolved as described above.
- `python3.13 -m unittest -v tests.test_magistrate_watchdog_b6.InstalledBlockSixTests tests.test_magistrate_watchdog_span`: **32 tests, all passed**.
- Original-source replay shown above: **all eight final watchdog regression methods fail on 5f4620d71**, with no fixture errors.
- `python3.13 -m tests.hazards.refusal_census`: initially reported three count changes and one guard change. Updated only those four rows using the census API's computed output. Final result: exit 0; no unlisted, stale, miscounted, guard-changed, or scope-gap entries.
- `python3.13 -m unittest tests.hazards.test_refusal_allowlist`: **23 tests, passed, one existing skip**.

Final required-module command:

```bash
export TMPDIR=$(mktemp -d)
export JW_B5_SYNTHETIC_ONLY=1
export PYTHONDONTWRITEBYTECODE=1
python3.13 -m unittest -v \
  tests.test_magistrate_watchdog \
  tests.test_magistrate_watchdog_cli \
  tests.test_magistrate_watchdog_span \
  tests.test_magistrate_watchdog_yield \
  tests.test_install_magistrate_watchdog \
  tests.test_night_gate \
  tests.test_b5_plan \
  tests.hazards.test_refusal_allowlist \
  tests.test_magistrate_watchdog_b6
```

**Outcome: exit 0; 384 tests in 58.183 seconds, OK (skipped=2).** Existing skips: the temporary filesystem is case-sensitive; the block-five design branch is absent from this clone. No whole-suite run was performed.

Computed allowlist changes:

| Function / site | Count | Census guard |
| --- | --- | --- |
| `_installed_agent_plans` / unreadable installed agent raise | 1 | `c2f249213a47f9d5` |
| `_launch_fence` / FENCED | 2 → 1 | `a6ed3c96a54671ca` |
| `decide` / FENCED | 2 → 1 | `d7c19ddd76f2aea6` |
| `decide` / HOLD_UNSAFE | 9 → 8 | `d629f0b330f96d99` |

`git diff --check`: passed. Final source/diff review: only the authorized production file, tests, allowlist, and this report changed; no lead-owned state or raw evidence was edited.

## Environment limitation and delivery

The requested `/opt/homebrew/bin/python3.13` compatibility symlink was absent. The approved setup command `mkdir -p /opt/homebrew/bin && ln -s /usr/bin/python3.13 /opt/homebrew/bin/python3.13` failed with **Permission denied** because `/opt` is root-owned and the VM runs as the unprivileged `agent` user. No symlink was created and no permission bypass was attempted. All requested modules nevertheless completed with the VM's Python 3.13; no test failed for the missing symlink.

The implementation and this report were committed together as `ddef54e5d1154d5799ab23f32c5a03776a8a3fde`, whose parent is the requested `5f4620d71` head. `git push -u origin HEAD:refs/heads/fix/2026-10-16-watchdog-b6-bindings` **succeeded**, advancing the existing remote branch from `5f4620d71` to `ddef54e5d`. `git ls-remote origin refs/heads/fix/2026-10-16-watchdog-b6-bindings` confirmed the full implementation SHA; `git status --short --branch` showed a clean tree. `git diff HEAD^ HEAD --check` passed. This delivery record is a report-only follow-up on the same branch; the final response identifies the final pushed head. No PR was opened or merged. Validation is synthetic/VM evidence, not live block-six hardware validation.
