# Seat B fix round 3 — Opus 5 implementation seat (Codex quota exhausted), 2026-09-17 03:36–04:12 PDT

Brief: record 38. Verbatim report:

SEAT B FIX ROUND 3 — F3, F4, F7 landed in /Users/edr/code/JouleWise-wt-rh-transport (branch feat/2026-09-16-reserve-hang-transport, base 2c6bcfdf). No git writes made; working tree left dirty for the lead to commit by pathspec. No NEEDS_SCOPE.

## F3 — PROBE_CODE_PATHS omitted the driver and the writer
Root cause: /Users/edr/code/JouleWise-wt-rh-transport/joulewise/night_agent_install.py:633-637 at base (PROBE_CODE_PATHS bound only the reservation, calibration_ledger.py and calibration_custody_worker.py), so an uncommitted edit to the two programs that do most of the night's custody reading left a minted receipt valid.
Fix: night_agent_install.py:641-648 now binds five paths (added scripts/validate_powermetrics_fiducial.py and scripts/run_night.py), with a comment stating the committed-vs-uncommitted argument.
Installer-side vs receipt-side reconciliation (the point the brief asked me to state): the reservation's verify-only line echoes digests for exactly three files — I confirmed this against the integration branch, `git show int/2026-09-17-reserve-hang-final:scripts/reserve_calibration_window_bracket.py` lines 350-356 — so the old field-equality check `value["code_digests"] != bindings["code_digests"]` would now refuse every probe. scripts/run_night.py:2204-2217 makes the echo a SUBSET check: every entry the reservation echoes must name a bound path and equal the installer-side digest (an unknown key yields None and refuses), and scripts/run_night.py:2236 publishes the installer-side superset into the receipt, which validate_probe_receipt recomputes field by field at install time. The receipt therefore carries five `code_digests`; the reservation still echoes three.
Regression: tests/test_install_night_agent.py:267 `InstallNightAgentTests.test_install_binds_the_driver_and_the_writer_programs` — per file, mint a matching receipt, append one uncommitted byte, assert measurement HEAD unchanged, install exits 2 naming `code_digests`, and no bootstrap happened. At 2c6bcfdf it fails on `self.assertEqual(2, result.returncode, result.stderr)` → `AssertionError: 2 != 0` for scripts/validate_powermetrics_fiducial.py (install admitted). The second subtest (scripts/run_night.py) also fails there, `2 != 3 : night_agent_already_loaded`, because the base run's first subtest actually installed the agents; in the fixed tree both subtests refuse before bootstrap so there is no such pollution.
Fixture work (both in WRITE_SCOPE): tests/test_run_night.py `make_probe_fixture` now creates measurement_root/scripts/run_night.py (the real measurement clone always has it), and `write_matching_probe_receipt`'s oracle binds the five paths.
Residual worth a magistrate eye (not in the brief, not fixed): PROBE_CODE_PATHS resolves against `plan.measurement_root`, so this binds the measurement clone's run_night.py. The LaunchAgent executes the DRIVER checkout's copy (`@@REPO@@`, pinned by plan.repo_head), which remains covered only by the committed-HEAD check.

## F4 — a spurious second fire planted an authoritative refusal.json beside a GO night
Root cause: scripts/run_night.py:1167 at base — `_write_rerun_refusal` wrote `night_dir/"refusal.json"`, reached from run_night (:1616) and _malformed_plan_exit (:1260) whenever any write-once record existed, including a finished GO night.
Fix: scripts/run_night.py:1172-1189. Skip entirely when `result.json` exists (a verdict is published; the rerun says nothing), otherwise write `rerun.refusal.json` through the same `_write_refusal_bytes` O_CREAT|O_EXCL allocator, which numbers concurrent writers `rerun.refusal-01.json`. `_refusal_paths` is deliberately unchanged, so rerun records never enter `result.json.refusal_documents` nor the courier's `refusal*.json` discovery; scripts/run_night.py:618-623 adds them to `_artifact_list` only, as evidence, so the durable results-branch publish keeps them. docs/process/NIGHT_COURIER_PROMPT.md:15-21 tells the courier that `rerun.refusal*.json` is informational, never the verdict, never in `refusal_documents`, never present once result.json exists, and to take the verdict from result.json.
Chosen answer to the brief's "or nothing, per your choice": on a GO night, NOTHING is written (exit stays EXIT_REFUSED 3 for that invocation); the rerun stem is used only while the first night is still running.
Regressions (tests/test_run_night.py): :1411 `test_second_fire_beside_a_go_night_writes_no_refusal_document` — base failure `self.assertEqual([], list(night.glob("refusal*.json")))` → `[] != [PosixPath('…/custody/night/refusal.json')]`; also asserts result.json bytes unchanged, verdict GO, `refusal_documents` empty and no refusal-shaped artifact entry. :1433 `test_second_fire_during_a_running_night_uses_the_rerun_stem` — base failure `self.assertFalse((night / "refusal.json").exists())` → `True is not false`; asserts rerun.refusal.json content/evidence, `_refusal_paths` empty, allocator numbering to rerun.refusal-01.json, and the artifact entry.
Two existing tests amended to the new contract (both first runs publish result.json, so both now expect no document): `test_chain_claim_prevents_a_second_spawn_after_a_failed_chain` and `test_write_once_rerun_preserves_the_first_nights_records`.

## F7 — Refused raised in launchd_probe's finally masked the in-flight failure
Root cause: joulewise/night_agent_install.py:866-894 at base — the cleanup proofs raise inside `finally`, replacing e.g. "probe receipt timeout" with "probe bootout absence unproven".
Fix: night_agent_install.py:845-899. `in_flight` captures the propagating exception (`except BaseException … raise`); the whole cleanup body is wrapped so a `Refused` from it re-raises as `Refused(cleanup.code, "<cleanup> (raised while handling <Type>: <message>)") from in_flight`. Fail-closed behaviour and exit code 2 are unchanged; only the diagnostic is added, with `__cause__` set.
Regression: tests/test_night_agent_install.py:1849 `LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted` — wire-level via the fake launchctl (bootstrap publishes no receipt → receipt timeout; `bootout` directive `loaded=True` → absence unproven), with a counting monotonic stub so the test runs in ~0.7 s. Base failure: `AssertionError: 'probe receipt timeout' not found in 'probe bootout absence unproven: com.joulewise.night-probe.probe-fixture'`.

## Verification
Counterfactual tree: /tmp/rh-base — `cp -R` of the worktree, the six WRITE_SCOPE files restored with read-only `git show 2c6bcfdf:<path>` (run from the worktree; `git diff --stat` there showed only the three overlaid test files), only the four new test methods overlaid, .git pointer since removed. All three regressions fail there as quoted above; the real worktree's git admin files are intact (`git status --short` and `rev-parse --abbrev-ref HEAD` verified).

Tails (TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest …):
- tests.test_run_night — Ran 122 tests in 33.034s — OK (baseline at 2c6bcfdf: 120 OK)
- tests.test_night_agent_install — Ran 57 tests in 603.334s — OK (baseline: 56 OK)
- tests.test_install_night_agent — Ran 60 tests in 48.236s — OK (baseline: 59 OK)

compileall (`PYTHONPYCACHEPREFIX=/tmp/rh-transport-pycache python3 -m compileall -q scripts joulewise`): rc=0.

git status --short / git diff --stat (WRITE_SCOPE paths only):
```
 M docs/process/NIGHT_COURIER_PROMPT.md
 M joulewise/night_agent_install.py
 M scripts/run_night.py
 M tests/test_install_night_agent.py
 M tests/test_night_agent_install.py
 M tests/test_run_night.py
 docs/process/NIGHT_COURIER_PROMPT.md |  8 +++-
 joulewise/night_agent_install.py     | 82 +++++++++++++++++++++++-------------
 scripts/run_night.py                 | 42 ++++++++++++++++--
 tests/test_install_night_agent.py    | 23 ++++++++++
 tests/test_night_agent_install.py    | 20 +++++++++
 tests/test_run_night.py              | 61 ++++++++++++++++++++++-----
 6 files changed, 192 insertions(+), 44 deletions(-)
```
(The night_agent_install.py line count is inflated by re-indenting the finally body; the only logic added there is PROBE_CODE_PATHS plus the in_flight capture/chain.) No bytecode added to the tree (`find . -name '*.pyc' -newermt '2026-09-17 03:00'` → 0); the gitignored scripts/__pycache__ and joulewise/__pycache__ directories predate this seat (timestamps 00:18) and were left alone. No launchctl, custody root, measurement root, canonical root or network touched.
