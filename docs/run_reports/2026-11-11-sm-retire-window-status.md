# sm-retire-window-status — 2026-11-11

Retired the status file and its Git publisher on main only (audit Q8, second half;
section 8.2 item 4). No writer, driver, watchdog, harvest, or registration code changed.
No new tool or classifier was added. The existing custody-isolation test census
needed a small deletion to stop requiring the removed test module.

## Base and authority

Branch: `docs/2026-11-11-sm-retire-window-status` (already checked out and clean).
Base: `origin/main` at `a6c0e6be0d1c83d47f6454fb650bae670a3013f5`.
`git cat-file -e origin/main:scripts/gen_current.py` passed. No fallback was used.
Read audit section 8 and the lane PLAN from their requested refs.
No active stop card was present. This is the explicitly assigned AGENT task;
the current pointer's no-arm instruction remains binding.

Read the three arm-stack sources using `git show` on main and W1 without checkout.
Main has the old `HOLD_UNSAFE` observer. W1 adds named holds,
`night/courier.delivery.json`, and `chain_exit_nonzero:<rc>` in `run_night.py`.
Both drivers retain the historical arm-verdict comment. This retirement adds no
reader and changes no record interpretation. W1 remains at
`b4a6c217f0285a20aff33a8407160dd77af2a8a6`.

## Commits

Implementation: `fa2625161c6a5c4f59d3a83ce0974fee576ea647` — `docs: retire superseded window status publisher on main`.
This handoff report is committed separately as `docs: record window status retirement evidence`.
Both commits are local on the task branch. Nothing was pushed.

## Changes and reference census

Deleted `WINDOW_STATUS.md`, `scripts/window_status.sh`, and
`tests/test_window_status_guard.py`. No tombstone was needed.
`docs/ARCHIVE.md` now gives three offline `git show` commands against the immutable
base commit. `CLAIMS_STATUS.md:35-37` already points to CURRENT.json and
POINTER_RULE.md; it needed no edit. No new tool-map row was required.

The initial bounded `rg` census found 106 occurrences in 37 paths outside the
generated site. Each path is below; line numbers refer to the base tree.
Two generated HTML paths are listed separately. Historical citations remain as
written. The contract's opening notice makes its publisher/code-map material
historical while preserving the helper's liveness contract.

| Path and original lines | Action |
|---|---|
| `.codex-report/CUSTODY-T1.md`:89, 93, 124, 125 | Unchanged historical evidence/report; retained verbatim. |
| `CANONICAL.md`:21 | Marked status file and publisher superseded on main; linked archive retrieval. |
| `RUN_STATE.md`:4191, 4889, 8596, 8684, 8713, 8754, 8910, 8979 | Unchanged lead-owned history. |
| `TASK_QUEUE.md`:211, 808, 1093 | Unchanged lead-owned generated/backlog text. |
| `configs/campaigns/v5_claim_25g83/sealed_inventory.json`:680 | Unchanged sealed era record (RL-51). No current-path requirement was added. |
| `configs/pins/registry.json`:2831, 26896 | Unchanged historical commit pin; default generator requires prohibited measurement-artifact reads. See below. |
| `docs/contracts/window_liveness.md`:670, 675, 739, 759, 760, 761, 799, 800, 801, 802, 803 | Marked publisher descriptions/code map historical on main; replaced executable example and retention paragraph with current pointer guidance. |
| `docs/decision_log.md`:5434 | Unchanged historical Q9 ruling acknowledgement. |
| `docs/legacy/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md`:2738, 4726 | Unchanged historical evidence/report; retained verbatim. |
| `docs/perf/2026-11-08-eng-ci-shards.json`:399, 987 | Unchanged historical CI scheduling observation. |
| `docs/phase_2/splitwise_decode_campaign.md`:185, 555 | Unchanged dated campaign/disk bookkeeping history; superseded by canonical retirement notice. |
| `docs/process/MAGISTRATE_WATCHDOG.md`:11 | Replaced publisher instructions with CURRENT.json and POINTER_RULE.md. |
| `docs/process/NIGHT_HANDBACK.md`:29 | Replaced publisher instructions with CURRENT.json and POINTER_RULE.md. |
| `docs/process/state_kernel.json`:11155, 11162, 11172 | Unchanged lead-owned task text. All three fields and the actual pointer target are detailed below. |
| `docs/process_traces/2026-08-20-go-session/readiness-sitting/VERDICT-PACKET.md`:63 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`:316, 317, 323, 331, 340, 468, 875, 977, 1262, 1325, 2100, 2101 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md`:101 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`:1618 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`:25 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-09-08-handoff-redo/50-bookkeeping-t38-astra.md`:114 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-10-03-design-block3/windows/d117-g2a-prefill-probe-20261004T0526Z/SHA256SUMS`:96, 10854, 11426 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-10-03-design-block3/windows/d117-g2a-prefill-probe-20261004T1305Z/SHA256SUMS`:102, 10867, 11439 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-10-07-block5-seal/gates/20-whole-suite.md`:79 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-10-27-l9-restart/b5-transfer/v5-b5-alpha-a1-20261009T2312Z-harvest.manifest.json`:52433, 110388, 114203 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-10-27-l9-restart/b5-transfer/v5-b5-beta-a6-20261011T2011Z-harvest.manifest.json`:55348, 113653, 117468 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/2026-10-27-l9-restart/b5-transfer/v5-b5-gamma-a1-20261012T0420Z-harvest.manifest.json`:50403, 108718, 112533 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T0617Z/harvest.json`:929, 68716, 72534 | Unchanged historical evidence/report; retained verbatim. |
| `docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T2252Z/harvest.json`:929, 68805, 72634 | Unchanged historical evidence/report; retained verbatim. |
| `docs/run_reports/2026-11-11-sm-current-pointer-fable-review.md`:47, 48 | Unchanged historical evidence/report; retained verbatim. |
| `docs/run_reports/2026-11-11-sm-current-pointer.md`:32, 50, 83, 132, 133, 135, 142, 152, 165 | Unchanged historical evidence/report; retained verbatim. |
| `docs/run_reports/interp-energy-desk/sm-current-pointer-r2-sol-report.md`:5 | Unchanged historical evidence/report; retained verbatim. |
| `docs/run_reports/interp-energy-desk/sm-current-pointer-sol-report.md`:4 | Unchanged historical evidence/report; retained verbatim. |
| `scripts/test_timings.json`:774 | Deleted exactly its one module line; no serialization. |
| `scripts/window_status.sh`:22, 26, 33, 102 | Deleted publisher. |
| `tests/test_custody_isolation_guard.py`:32, 43, 57 | Removed deleted test from observed-module set and updated comment. Kept the general caller-detection regex for custody safety. |
| `tests/test_gen_state.py`:827 | Unchanged historical comment at line 827; module passes after deletion. |
| `tests/test_window_status_guard.py`:11, 50, 75 | Ran its 11 tests before deletion; deleted module. |
| `WINDOW_STATUS.md` | Deleted stale output; no self-reference appeared in the census. |
| `CLAIMS_STATUS.md`:35–37 | Already migrated to CURRENT.json and POINTER_RULE.md; unchanged. |
| `docs/ARCHIVE.md` | Added exact-commit retrieval for all three removed files. |
| `docs/site/readme.html`:1 | Generated HTML still cites the old file; left untouched. |
| `docs/site/run_state.html`:1 | Generated historical rendering still cites the old file; left untouched. |

No matching `automation_history_*.md` reference was found in `docs/process/`.
No process trace, historical run report, generated site, coordination state,
sealed inventory, or pin registry was edited.

### Kernel and pin ownership

`docs/process/state_kernel.json` references the publisher in exactly these fields:

- `/tasks/WINDOW-STATUS-GUARD-CENSUS-01/acceptance/evidence/0` (line 11155).
- `/tasks/WINDOW-STATUS-GUARD-CENSUS-01/acceptance/summary` (line 11162).
- `/tasks/WINDOW-STATUS-GUARD-CENSUS-01/goal` (line 11172).

The task's acceptance pointer at lines 11157–11160 targets the kernel's own
`/tasks/WINDOW-STATUS-GUARD-CENSUS-01/acceptance`, not a removed path. Its status
remains `queued`, rank 155 (A155). `tests/test_gen_state.py:827` mentions the removed
test only in a historical comment; line 289 also expects the task ID in its census.
Both `scripts/gen_state.py --check` and the complete state test module pass with
all three files absent. There is no kernel-path blocker and no restored file.
The lead should reconcile the obsolete queued task and regenerate its queue views;
this seat has no authority to do that.

The registry owner is `scripts/digest_pin_census.py`; its documented procedure is
`python3.13 -B scripts/digest_pin_census.py --write`. It is deterministic and local,
but `census()` calls `build_index()` over every tracked file (lines 824–828), which
reads their bytes at lines 641–650, including archived measurement artifacts.
Running that default command would exceed this seat's data-read authority.
No filtered or hand-edited substitute was used. The retained registry target is
`file@c27485347c9629b857df81665b5b1b8d10dcd36a:scripts/window_status.sh` (line 2831);
the inventory row `/files/scripts~1window_status.sh` at line 26896 resolves to that
historical commit, not HEAD. The lead may regenerate in a context authorized for
all tracked bytes. No test required the sealed inventory's paths to exist at HEAD.

## Is it installed anywhere? Repository evidence

These are static repository checks, not an inspection of installed host jobs.
No MBP or live launchd query was made.

| Check on `origin/main` | Evidence and result |
|---|---|
| v4 ARTIFACTS | `git cat-file -e origin/main:joulewise/align/apple/v4_registration.py` reports path absent. Main has no v4 ARTIFACTS module to bind this script. |
| v4 registration receipt | `git cat-file -e origin/main:configs/campaigns/align_v4/registration/registration_receipt.json` reports path absent. No v4 receipt exists on main. |
| launchd templates | `git grep -n -e WINDOW_STATUS -e window_status origin/main -- '*.plist' '*.plist.*' '*launchd*'` returns no matches (exit 1). This includes all three `configs/launchd/*.plist.template` files. |
| magistrate relaunch prompt | The same grep restricted to `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` returns no matches (exit 1). |
| executable callers | `git grep -n -F scripts/window_status.sh origin/main -- scripts joulewise` finds only the publisher's own usage examples (lines 22, 26). `WINDOW_STATUS.md` appears only in its output/staging code (lines 33, 102). |

Also rechecked W1's `v4_registration.py`, registration receipt, launchd templates,
and relaunch prompt with `git show ... | rg` or `git grep` for both names: zero
matches in each. The W1 code and ref were left unchanged. No conclusion about an
untracked host installation is claimed.

## Verification

Only targeted unittest modules were run. The full suite and analysis pipeline
were not run. No model weights, network, real custody, or quiet-window measurement
was used. There are no new MLX paths requiring a native Metal test.

| Command/check | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_window_status_guard` | PASS before deletion: 11 tests, 13.191 s. |
| `python3.13 -B -m unittest tests.test_custody_isolation_guard.StaticCustodyIsolationTests` | Expected FAIL after deletion and before census repair: 2 tests, 1 failure, 12.579 s. Missing retired module was the only failure. |
| `python3.13 -B scripts/gen_state.py --check` | PASS after all three deletions; no tombstone. |
| `python3.13 -B -m unittest tests.test_gen_state` | PASS: 44 tests, 32.664 s; below the 3-minute limit. |
| `python3.13 -B scripts/gen_current.py --check` | PASS. |
| `python3.13 -B -m unittest tests.test_gen_current` | PASS: 49 tests, 1.628 s. |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | PASS: 14 tests, 2 skips, 1.761 s; below the 3-minute limit. Both live process checks were sandbox skips. |
| `python3.13 -B -m unittest tests.test_docs_freshness` | PASS: 31 tests, 7.392 s. |
| `PYTHONPATH=. python3.13 -B /private/tmp/sm-retire-custody-tests.py` | PASS initially: 6 tests, 16.646 s. Final tree rerun PASS: 6 tests, 12.399 s. |
| `python3.13 -B -m unittest tests.test_digest_pin_census` | PASS: 22 tests, 276.678 s. Historical inventory digests resolve without a HEAD-path requirement. |
| `PYTHONPYCACHEPREFIX=/private/tmp/sm-retire-pycache python3.13 -m compileall -q joulewise tests scripts` | PASS. Cache files stay outside the repo. Recompiled the touched custody-guard module after final review; PASS. |
| Inline Python byte/retention check | PASS: timings differ by exactly one deleted line; JSON parses; protected files match base; all deleted paths are absent and retrievable at the documented commit. |
| Inline Markdown link check on changed lines | PASS: all 15 local link targets exist. |
| `git diff --check` | PASS. |

The custody wrapper patches only `Path.expanduser`: a result under `/Users/edr`
is mapped into a fresh `TemporaryDirectory`; other expansions are unchanged.
This prevents the existing assertion from resolving the real home. It does not
change HOME, production source, test assertions, or fixture expectations.
Reproduce the wrapper at the temporary path named in the command above:

```python
"""Run the custody guard without resolving the operator's real home."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

original_expanduser = Path.expanduser
with tempfile.TemporaryDirectory(prefix='sm-retire-home-') as temporary:
    synthetic_home = Path(temporary)
    forbidden_home = Path('/Users/edr')

    def isolated_expanduser(path):
        expanded = original_expanduser(path)
        if expanded.is_relative_to(forbidden_home):
            return synthetic_home / expanded.relative_to(forbidden_home)
        return expanded

    with patch.object(Path, 'expanduser', isolated_expanduser):
        unittest.main(module='tests.test_custody_isolation_guard')
```

The general liveness-script detection regex was retained on final review; only
the obsolete observed-module entry and its comment changed.

One process-rule deviation: the 1.628-second pointer module briefly overlapped
the state module. Remaining unittest modules ran sequentially. Total targeted
test time was 374.938 s (including the expected failure and final rerun), below the requested 20-minute budget.

The filename grep in `tests/` found no direct `CLAIMS_STATUS.md`, `CANONICAL.md`,
or `ARCHIVE.md` document-path assertion. Broader keyword hits were unrelated
constants/task names. The general documentation-freshness module and pin census
were run as additional relevant checks.

## Left for the lead / uncertainty

- Review and admit this main-only diff. No push or merge was performed.
- Reconcile kernel task `WINDOW-STATUS-GUARD-CENSUS-01` and its generated A155
  queue rows. Preserve the sealed inventory as an era record (RL-51).
- Run the documented registry generator only in a context authorized to read
  all tracked artifact bytes. Its historical publisher target may remain;
  this seat did not claim a full regeneration or byte-identical registry output.
- Rebuild generated site pages through their owner if current renderings need
  refresh. The historical RUN_STATE citations themselves were left intact.
- Run `python3.13 -B -m unittest tests.test_fixture_orphan_census` outside this
  sandbox on an authorized AGENT host to cover the two live process checks.
  Neither skip is hardware or measurement validation.
- Possible fixture leftover: `test_live_an_orphaned_fake_meter_is_reported`
  launches its synthetic meter before encountering the sandbox's denied `ps`.
  Its cleanup also enumerates processes and returns no rows when denied, so
  cleanup could not be verified. A fixture-only `/usr/bin/pgrep -f` query for
  `orphan-census-[^ ]+/hazards/meter/stream-001[.]jsonl` returned 3 with
  `Cannot get process list`. The lead should check that exact temporary-fixture
  signature outside the sandbox and reap only a confirmed matching fake meter.
  No broad process kill or action against the blinded analysis job was attempted.

No retirement contract question remains. Static repository evidence does not
establish whether an untracked publisher is installed on a host.
