# 49 — Opus counter-review (gate row 6) — PR #324, #326, #327

Diverse-model lens on the near-final heads, after records 25/31/33/37/39
(#324), 06/08/18/27 (#326), 41/44 (#327). Read-only; all four bases are
`origin/main` ace4cc3c.

## PR #324 — A177, head 74a547cd (`tests/test_controller.py`, `tests/test_run_campaign.py`)

**(a) Smallest self-protecting shape?** Close, and consult 39's 33-cut table
covers clauses 1–21. **One clause has no visible killer:** the regression
inspects only `capture = bounded_captures[0]` (`tests/test_controller.py:1677`)
and never pins `len(bounded_captures)`. `assertTrue(bounded_captures)` (:1673)
admits any number. A mutation that adds a *second*, paced bounded capture — or
that makes a future second sentinel skip the `--no-sleep` policy — survives
every assertion. Fix if taken: `self.assertEqual(len(bounded_captures), 1)`
after :1673, or loop the argv/timeout block over all captures. Nit: the `100`
in `for count in (None, 3, 7, 100)` (:1614) is a vestige of the 100-sample pin
that delta re-audit 79 F1 refuted; no cut distinguishes it from `7`.

**(b) Can it pass for the wrong reason on hosted Linux?** Not by the CI-red
mechanism, but it carries a new host-shaped hazard.
- Continuous pacing is restored to baseline: the whole producer runs under
  `with patch.dict(os.environ, {"FAKE_POWERMETRICS_SLEEP_SCALE": "1"}):`
  (:1664) — deterministic even if the runner exports the variable.
- Bounded stress is scoped to one method: `with patch.dict(os.environ,
  {"FAKE_POWERMETRICS_SLEEP_SCALE": "12"},)` around
  `super()._run_bounded_capture(...)` (:1657-1661).
- **Production deadlines touched:** only `_capture_timeout_s`
  (`joulewise/adapters/powermetrics.py:1468-1470`) as consumed by the bounded
  path at `:1201`. Because `--no-sleep` is applied, the fake never sleeps
  (`tests/fixtures/fake_powermetrics_process.py:44,73`), so the bounded
  capture's wall time is ~0 and the 12x scale is never spent. The continuous
  admission deadline `deadline = time.monotonic() + self._capture_timeout_s(
  config, count + 1)` (`powermetrics.py:1256`) — the one report 31 starved —
  now runs at scale 1. **No wall-clock exposure added.**
- **New hazard (should-fix):** `assertGreater(nominal_s * capture["scale"],
  capture["timeout_s"], ...)` (:1690-1693) is satisfied only when the derived
  post count is **>= 26**. With `power_hz=20`/`idle_seconds=1.5`
  (`tests/test_controller.py:777-779`) production derives
  `count = max(3, ceil(min(5.0, baseline.duration_s)/0.05))`
  (`powermetrics.py:1029-1031`), i.e. ~30 here. Margin is 4 samples / 0.2 s of
  measured baseline. If a runner ever yields a shorter measured baseline the
  test goes red on this guard, not on the defect. It fails loudly with its own
  message, so it is a diagnosable brittleness, not a silent wrong-reason pass.

**(c) Host-dependent pins?** None. Count, interval and timeout are all derived
and cross-checked against argv (:1679-1689); `scale >= 12.0` (:1678) is a
fixture-policy constant; the removed `assertEqual(post_sample_count, 100)` is
now re-derived in `tests/test_run_campaign.py:9627-9634`. The only
host-dependent coupling is the implicit `count >= 26` floor above. Duplication
nit from record 25 persists: the post-count formula now lives in three places
(production `:1029-1031`, `test_run_campaign.py:9627-9634`) and the timeout
formula in two (`:1468-1470`, `test_controller.py:1688-1689`).

## PR #326 — gitfix, head 87039749

**(a) False positive: CONFIRMED, and it is broad.** The rewritten predicate
(`tests/test_git_fixture_maintenance.py:174-176`) flags a call whenever the
exact literal `"init"` appears *anywhere* in the resolved argument tree; the
old code additionally required `"git"` in the literals or a runner callee.
Constructed in memory against `_git_init_violations` (see "what I ran"):
- `subprocess.run(["git","status"], cwd=path)` + `parser.add_argument("--phase",
  choices=["init","run"])` → `{'support/factory.py': (2,)}`
- `subprocess.run(["git","status"], env={"PHASE": "init"})` → `(1,)`
- `self.assertEqual(state["phase"], "init")` → `(1,)`
- `json.dumps({"phase": "init"})` → `(1,)`
Clean (correctly): a function literally named `init` (`init(repository)` → `{}`,
callee names are excluded at `:194-195`), `logger.info("init complete")`,
`os.system("git status")`. Today's tree has only three `"init"` literals
(`tests/test_calibration_exits.py:2146,3650`, `tests/git_fixture.py:26`), all
legitimately exempted — so this is a prospective hazard, not a live one.
Should-fix (follow-up row, not merge-blocking): gate the *bare*-`init` rule on
the callee resolving to a runner/wrapper name (the set the hygiene fixtures
already exercise: `subprocess.run`, `os.system`, `run`, `execute`, `_run`,
`_run_fixture_command`), keeping the unconditional rule when `"git"`
co-occurs or `_shell_git_init` matches. All 13 hygiene fixtures still flag
under that gate.

**(b) By-name exception vs a renamed test: airtight.** `_scope_name` (:52-59)
builds the fully-qualified `Class.method`, matched exactly at :183, :190 and
:213. A rename, a move to another class, or a nested `def` inside the excepted
method all miss the key and the census flags — fail-closed. Their own
`test_named_maintenance_exceptions_do_not_exempt_other_tests` proves the
rename case. Residual nit: nothing asserts the two entries still *resolve*, so
a deleted method leaves a silent dead exception.

**(c) Two files: right home, one stale artifact.** The mechanism does have ONE
home — `test_git_fixture_maintenance.py` owns `_CommandLiterals`,
`_git_init_violations`, `MAINTENANCE_ON_EXCEPTIONS`; `test_git_fixture_hygiene.py`
only imports it and adds adversarial cuts (tests *of* the checker). Acceptable;
the smell is importing private names across test modules, curable later by
moving the census to `tests/git_fixture_census.py`. **Real should-fix found
here:** the PR converts `tests/test_identity_pins.py` to the shared helper
(`init_git_fixture(root, "-q")`, diff line ~73) but leaves
`ESTABLISHED_LOCAL_HELPERS["tests/test_identity_pins.py"] = {"init_git"}`
(:29). That entry is now dead — the file has no direct `init` call — yet it
keeps a standing local-helper exemption, and
`test_established_local_helpers_retain_the_exact_tuple` (:317-325) only stays
green because the new `ImportFrom`-following clause (:232-241) resolves the
tuple through `tests/git_fixture.py`. Drop the entry.

## PR #327 — armfix, head 100dfb2d (`tests/test_arm_readiness_dry_run.py`)

**(a) Order-dependence / flakiness: none found.** The sample is taken once per
call, before the kind loop (`:145` `authored_at_monotonic_ns =
time.monotonic_ns()`, consumed at `:180`), so every evidence receipt in one
freeze shares one `now`; only the optional mint receipt (`:201`
`now_monotonic_ns=None`) uses the live clock, which under any frozen-clock test
is the same instant and otherwise differs by milliseconds against a 7-day
horizon. The one class that freezes the clock,
`ArmReadinessIntegrationTests.setUp` (`tests/test_arm_readiness_integration.py:
292-318`), starts its `mock.patch.object(time, "monotonic_ns", ...)` *before*
calling `install_passing_freeze` (`:330`, `:567`), and patches the same shared
`time` module object the fixture imports — so the fixture reads the frozen
anchor, not a second instant. No golden byte comparison exists: receipt digests
are recomputed from bytes at read time (`:139-143`, `:186-188`) and
`pack_sha = readiness.committed_pack_tree_sha256(pack)` is derived
(`test_arm_readiness_evidence_t0.py:445`). Verified by running the four
dependent modules (152 + 13 tests, both OK).

**(b) Monkeypatch scoping: clean, context-managed, quoted.**
`self.addCleanup(temporary.cleanup)` (:277); `with mock.patch.object(time,
"monotonic_ns", return_value=self.origin):` (:280); `with mock.patch.object(
time, "monotonic_ns", return_value=self.origin + 1_000_000_000):` (:298-300);
`with mock.patch.object(time, "monotonic_ns", return_value=self.origin + 8 *
86_400_000_000_000):` (:312-314). Nothing leaks past the `with`.

**(c) Seven-day horizon duplicated: YES — should-fix.** `self.origin = 1 + 15 *
86_400_000_000_000 // 2` (:279) and `self.origin + 8 * 86_400_000_000_000`
(:313) hardcode 7.5 d and 8 d. The ONE home is the registry:
`configs/arm_readiness/d117_row_registry_v2.json` →
`freeze_evidence_lifecycle.evidence_policies[kind].horizon_ns`, which is
`604800000000000` for `ACCEPTANCE_OWNER`, and it is *already loaded* as
`self.lifecycle` (:283). Fix: `horizon = next(p["horizon_ns"] for p in
self.lifecycle["evidence_policies"] if p["kind"] == self.receipt["kind"])`,
then `origin = 1 + horizon + horizon // 14` and expire at `origin + horizon +
1`. As written the tests pass if the registry horizon is retuned to anything
under 8 days without noticing.

## Merge-ability across #324, #325, #326, #327

Files are **pairwise disjoint** (`git diff --name-only ace4cc3c..HEAD`):
- #324 (74a547cd): `tests/test_controller.py`, `tests/test_run_campaign.py`
- #325 (43c1ce95): `docs/contracts/calibration_ledger_append.md`,
  `docs/phase_2/derivation_night_runbook.md`, `joulewise/calibration_exits.py`,
  `scripts/recover_calibration_ledger.py`, `tests/test_calibration_exits.py`
- #326 (87039749): `tests/test_git_fixture_hygiene.py` (new),
  `tests/test_git_fixture_maintenance.py`, `tests/test_identity_pins.py`
- #327 (100dfb2d): `tests/test_arm_readiness_dry_run.py`

**One real semantic interaction:** #326's census is a whole-tree scan
(`_git_init_violations` walks `tests_root.rglob("*.py")`, :251-258) and its
`MAINTENANCE_ON_EXCEPTIONS` / `ESTABLISHED_LOCAL_HELPERS` key by *name* on
`tests/test_calibration_exits.py` — the file **#325 adds 47 lines to**. A new
#325 test that called `git init` directly, or a rename of either excepted
method, would turn the merged tree red while both PRs are green alone. I
executed #326's census against each other worktree's `tests/` tree and all
return `{}` (a177, a184, armfix, gitfix); since the census is evaluated
per-file, per-file clean over the union implies union clean, so no interaction
exists today. **The integration replay must still show:**
`tests.test_git_fixture_maintenance` + `tests.test_git_fixture_hygiene` green on
the merged tree (that is the only cross-PR coupling), plus
`tests.test_controller`, `tests.test_run_campaign`, `tests.test_calibration_exits`
and the four `tests.test_arm_readiness_*` modules. No rebase needed: all four
branch from ace4cc3c.

## Verdicts

- **PR #324 — MERGE.** Should-fix is non-blocking; queue `assertEqual(
  len(bounded_captures), 1)` and a comment recording the `count >= 26` floor.
- **PR #326 — MERGE.** Two should-fix follow-ups, neither blocking: drop the
  dead `ESTABLISHED_LOCAL_HELPERS["tests/test_identity_pins.py"]` entry, and
  re-gate the bare-`init` rule on a runner callee to close the false-positive
  class.
- **PR #327 — FIX-FIRST.** Read the horizon from `self.lifecycle`
  (`evidence_policies[kind]["horizon_ns"]`) instead of hardcoding 7.5 d / 8 d
  at `tests/test_arm_readiness_dry_run.py:279,313`. Two-line change; everything
  else is clean.

## What I ran (`/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -q`)

- wt-a177 `tests.test_controller tests.test_run_campaign.IdleAdmissionCoreVerdictTests`
  → `Ran 147 tests in 154.715s` / `OK`, EXIT=0
- wt-gitfix `tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene
  tests.test_identity_pins` → `Ran 54 tests in 16.452s` / `OK`
- wt-armfix `tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence_t0
  tests.test_arm_readiness_lifecycle` → `Ran 152 tests in 943.659s` /
  `OK (skipped=1)`, EXIT=0
- wt-armfix `tests.test_arm_readiness_integration` → `Ran 13 tests in 256.033s`
  / `OK`, EXIT=0
- census probes (import `_git_init_violations` from wt-gitfix, scan synthetic
  trees under a `/tmp` TemporaryDirectory; no worktree written): 8 false-positive
  cases, results quoted in §326(a)
- cross-tree census: `_git_init_violations(<wt>/tests)` for gitfix, a177, a184,
  armfix → `{}` for all four
- `git diff ace4cc3c..<head>` and `--name-only` for all four PRs; reads of
  `joulewise/adapters/powermetrics.py`, `joulewise/arm_readiness.py`,
  `configs/arm_readiness/d117_row_registry_v2.json`,
  `tests/fixtures/fake_powermetrics_process.py`, records 25/27/37/39/44
