# Record 126 — Gate ledger row 10, fourth final-head fresh-eyes pass

- **Tree:** `/Users/edr/code/JouleWise-wt-epoch-integration`, HEAD
  `bd22ed19daac584fa2d117a7a55c63aa2acf8f26` (verified), `git status --porcelain`
  empty before and after this pass. Strictly read-only: no edits, no git state
  changes, no other worktree touched. All scratch under `/tmp/magistrate-96bfeca7/`.
- **Scope:** `git diff fa7dd55d..HEAD` — one commit, `bd22ed19`, two files.

## Verdict: CLEAN on the diff — with one out-of-diff SHOULD-FIX that blocks merge

The code change is correct, minimal, and fail-closed-preserving; the new test
pins the inverse and genuinely dies without the fix. One nit on a stale comment.
Separately, the `gate-ledger` required check is **failing on bd22ed19** for a
PR-body reason (rows 11/12 still cite `fa7dd55d`), which must be fixed before merge.

## The change is exactly one token

Comments stripped, `fa7dd55d` and `bd22ed19` differ in a single line:

```
$ diff <(grep -vE '^\s*#' /tmp/.../old_issuer.py) <(grep -vE '^\s*#' scripts/issue_calibration_acceptance_generation.py)
258c258
<         verify_custody=True, mode="read_replay", repo_root=REPO_ROOT,
---
>         verify_custody=False, mode="read_replay", repo_root=REPO_ROOT,
```

Everything else in the diff is the explanatory comment and the new test.

## (1) `verify_custody=False` is safe for BOTH `check` paths

**Epoch watch.** `check` uses the snapshot only for `snapshot.refusal_reasons`,
`snapshot.receipts[-1]["t1_bindings"]`, and (with `--session-ids`) the dry run.
All of these derive from authenticated ledger *rows* — the hash chain, the
committed head pin (`require_committed_pin=True`), receipt shapes and state
reconstruction all still run; `verify_custody` gates only the custody branch at
`joulewise/calibration_ledger.py:2191-2203`. No bundle is opened.

**Blind `--session-ids` dry run.** Confirmed as the brief describes:
`registration_dry_run` (`scripts/issue_calibration_acceptance_generation.py:168-248`)
reads bundles **only** inside `if terminal:` at line 206, via
`_read_member_evidence` (line 874). That function is its own custody authority:
it hashes the bundle with `artifact_hashes(Path(observation.custody_locator))`,
raises `PrepareRefusal("... custody unreadable ...")` on `OSError`, and refuses
unless both `manifest.json` and `instrument_evidence.json` match the row's
`artifact_sha256`. `registration_dry_run` turns every such refusal into a
`blocker`, and blockers force `DRY_RUN_INADMISSIBLE_EXIT`. So on a machine
without the custody roots, the dry run still refuses — it just refuses at the
bytes, where the refusal is specific, instead of at snapshot load, where it
took down the identity table too. **No custody hole is opened.** Note also that
`_read_member_evidence` reads the *original* locator without the `read_replay`
backup-root mapping, so it is strictly no laxer than the snapshot probe.

The comment's claim about `prepare-candidate` checks out: line 1177 loads with
`verify_custody=False, mode="read_replay"` already, and authenticates each
member's bytes through the same `_read_member_evidence` (line 1050). The watch
now loads the ledger exactly as the issuing-adjacent path does.

**Census still truthful.** `tests/fixtures/custody_read_replay_allowlist.json`
row for `check` (line 73-78) reads: "Read-only desk epoch watch and blind
registration dry run replay the existing ledger snapshot once to compare
identity fields... never mints, appends a receipt, publishes a binding, or
finalizes an analysis manifest." That remains accurate — the row never claimed
custody verification, and the call is still a single `mode="read_replay"` load.
The row's pinned `line: 268` is now stale by 11 lines (the call is at 279), but
the census tolerates that by design:

```
$ python3 -m unittest tests.test_custody_mode_inventory -v
test_extract_cells_forwards_caller_mode ... ok
test_inventory_counterfactual_escapes ... ok
test_line_shift_does_not_require_allowlist_edit ... ok
test_read_replay_inventory ... ok
test_second_call_requires_its_own_allowlist_row ... ok
test_shared_parameter_replay_is_censused_at_issuing_caller ... ok
test_shared_validators_default_to_issuing ... ok
Ran 7 tests in 38.594s
OK
```

## (2) CI reproduced and cured

`verify_custody=True` reaches `_custody_reasons` (`calibration_ledger.py:1898`),
which resolves each row's absolute `custody_locator` and calls `probe_custody`;
an absent root returns `{"calibration_ledger_custody_invalid"}`. The fixture's
30 custody locators are all absolute iCloud paths
(`/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/...`),
present here, absent anywhere else.

Simulation (`/tmp/magistrate-96bfeca7/sim2.py`) patches
`joulewise.calibration_ledger._custody_probe_paths` to return a non-existent
root **only** for paths under the iCloud prefix — synthetic tmp custody built by
a test's own `setUp` still resolves, so the patch adds no artifact. Suite:
all of `DeskEpochWatchTests` plus the seventh CI casualty,
`PrepareCandidateTest.test_check_compares_the_preregistered_binary_only_when_asked`.

```
--- NEW (HEAD bd22ed19) ---
Ran 19 tests in 10.795s
OK
hidden iCloud custody roots: 0
ran 19 failures 0 errors 0

--- OLD (fa7dd55d verify_custody=True) ---
Ran 19 tests in 10.680s
FAILED (failures=8)
hidden iCloud custody roots: 1
  FAILED: DeskEpochWatchTests.test_binary_hash_alone_refuses_even_when_epoch_matches
  FAILED: DeskEpochWatchTests.test_changed_os_build_refuses_and_names_only_changed_field
  FAILED: DeskEpochWatchTests.test_equal_epoch_and_t1_admit_without_writes
  FAILED: DeskEpochWatchTests.test_hardware_and_mlx_changes_refuse (field='hardware_model')
  FAILED: DeskEpochWatchTests.test_hardware_and_mlx_changes_refuse (field='mlx_version')
  FAILED: DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch
  FAILED: DeskEpochWatchTests.test_the_watch_never_requires_custody_directories
  FAILED: DeskEpochWatchTests.test_unavailable_mlx_is_recorded_and_refuses
```

`hidden iCloud custody roots: 0` under the fix is the strong form of the claim:
with `verify_custody=False`, `check` makes **zero** custody filesystem probes,
so the machine's possession of the corpus is irrelevant to the watch.

Direct single invocation, same simulation (a broader variant that hides every
custody root, `/tmp/magistrate-96bfeca7/sim_ci.py`):

```
NEW: direct `check` rc = 0            (18/18 DeskEpochWatchTests pass)
OLD: direct `check` rc = 3
     OUT: ledger: calibration_ledger_custody_invalid
```

That `ledger: calibration_ledger_custody_invalid` line is byte-for-byte the
failure text in PR #315's first CI run. The failure is reproduced and cured.

**Correction to record 124's wording:** the seven CI failures were not all
`DeskEpochWatchTests`. From the CI log of job 103105820366:
`MODULE FAIL tests.test_issue_calibration_acceptance_generation tests=111 failures=7 errors=0`,
whose named failures are six `DeskEpochWatchTests` (with
`test_hardware_and_mlx_changes_refuse` counted twice, once per subtest field)
plus `PrepareCandidateTest.test_check_compares_the_preregistered_binary_only_when_asked`.
The latter also goes through `check`, i.e. the same single call site, so the one
cure covers it; the in-flight CI run is the confirmation.

The new contract-pin test is real: it fails under the old kwarg (listed above),
and it asserts the kwarg identity (`assertIs(..., False)`) rather than a
downstream symptom, so a future `verify_custody=True` cannot pass it silently on
this machine.

## (3) Other lane fixtures depending on machine-absolute paths

Grepped `tests/` for `/Users/edr`, `Mobile Documents`, `runs/instrument_validation`.

| Site | What it holds | CI verdict |
| --- | --- | --- |
| `tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl` | The 30 absolute iCloud custody locators — the root cause | Safe **only** for loaders that pass `verify_custody=False`; that is now every lane call site |
| `tests/test_arm_readiness_schemas.py` | Only other `Mobile Documents` hit; string-shaped schema fixture, no filesystem dependence | Safe — passed on CI (`MODULE PASS tests.test_arm_readiness_schemas tests=50 failures=0`) |
| `tests/test_issue_calibration_acceptance_generation.py:727` | `f"/tmp/runs/instrument_validation/fixture-session-d{index:02d}"` — synthetic `/tmp` locator, not machine-bound | Safe |
| `tests/test_gen_derivation_night.py:366` | `{self.fixture.night_root}/runs/...` — tmp-rooted | Safe |
| `tests/test_calibration_bracketing.py:2963,2971` | `ledger.BACKUP_ROOTS[0] / "runs/instrument_validation/member"` — exercises the replay mapping with a patched root | Safe — passed on CI |
| Other `/Users/edr` hits (`test_doctor`, `test_run_campaign`, `test_floor_extraction`, `test_magistrate_watchdog*`, `test_paper_round7_artifacts`, …) | Literal strings / doc-path assertions, no probe | Safe — all passed on CI at `fa7dd55d` |

Decisive evidence rather than inference: at `fa7dd55d` the CI run
(34548374647) had exactly **one** failing module across all shards —
`MODULE FAIL tests.test_issue_calibration_acceptance_generation ... failures=7`,
appearing in `test (3.14, 2)` and `pr-fast (1)`. Every other failed shard in
that run was cancelled by the matrix (`The strategy configuration was canceled
because "test._3_14_2" failed`), not failed on its own. So no other test in the
lane depends on machine-absolute custody or `runs/` in a CI-fatal way.

## Findings

**SHOULD-FIX (out of diff, blocks merge) — `gate-ledger` is red on bd22ed19.**
The required `gate-ledger` check fails:
```
PR_HEAD_SHA: bd22ed19daac584fa2d117a7a55c63aa2acf8f26
gate-ledger: item 12: sha is not the PR head
```
The PR body's rows 11 and 12 still cite `RUN fa7dd55dd57b2be6d4cd4aa3cb117e0d5686c619`,
which was the head before this commit. Row 12 (magistrate terminal review of the
exact merge candidate) is not delegable, so this is not merely a text edit: it
needs a terminal review on `bd22ed19` and then the row updated to that sha.
Row 11 (CI green on final head) likewise cannot be closed until the in-flight
run on `bd22ed19` finishes — at report time all ten `test`/`pr-fast` shards are
still `pending`; `build`, `installed-wheel`, and the two completed
`calibration-writer-crash-matrix-exclusive` shards pass.

**NIT — stale comment in the test fixture.** `DeskEpochWatchTests.setUp`
(`tests/test_issue_calibration_acceptance_generation.py:95-96`) still reads:
"The real parser, hash chain, receipt shapes, **custody** and acceptance
authentication run. Only Git's committed-pin byte source is a fixture."
As of this commit `check` performs no custody authentication, so the word
`custody` in that sentence is now false. Removing it (or replacing with a
pointer to the new pin test) keeps the fixture's self-description honest.
Not worth its own commit; fold into any later touch of the file.

## Executed commands

- `git rev-parse HEAD` → `bd22ed19daac584fa2d117a7a55c63aa2acf8f26`; `git status --porcelain` → empty
- `git diff fa7dd55d..HEAD`; `diff` of comment-stripped script versions
- `python3 -m unittest tests.test_custody_mode_inventory -v` → 7 tests, OK
- `python3 /tmp/magistrate-96bfeca7/sim2.py new|old` → 19 tests OK / 8 failures
- `python3 /tmp/magistrate-96bfeca7/sim_ci.py new|old` → rc 0 / rc 3 with `calibration_ledger_custody_invalid`
- `gh pr checks 315`; `gh run view --job 103111678981 --log-failed`;
  `gh run view --job 103105820366 --log-failed`
