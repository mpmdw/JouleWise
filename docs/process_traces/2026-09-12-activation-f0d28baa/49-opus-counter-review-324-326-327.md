# 49 — Opus counter-review (gate row 6) — PR #324, #326, #327

Diverse lens on the near-final heads, after records 25/31/33/37/39, 08/18/27,
41/44. Read-only. All four bases = `origin/main` ace4cc3c.

## PR #324 — A177, 74a547cd (`tests/test_controller.py`, `tests/test_run_campaign.py`)

**(a) Shape.** Near-smallest; consult 39's 33 cuts cover clauses 1–21. **One
clause has no killer:** only `capture = bounded_captures[0]`
(test_controller.py:1677) is inspected and nothing pins
`len(bounded_captures)` — `assertTrue(bounded_captures)` (:1673) admits any
number, so a mutation adding a *second, paced* bounded capture survives every
assertion. Fix: `assertEqual(len(bounded_captures), 1)` after :1673, or loop
the argv/timeout block. Nit: `100` in `for count in (None, 3, 7, 100)` (:1614)
is a vestige of the 100-sample pin refuted by delta re-audit 79 F1; no cut
distinguishes it from `7`.

**(b) Wrong-reason pass on hosted Linux.** Not by the CI-red mechanism.
Continuous pacing: `with patch.dict(os.environ,
{"FAKE_POWERMETRICS_SLEEP_SCALE": "1"}):` (:1664) — deterministic even if the
runner exports the variable. Bounded stress: `with patch.dict(os.environ,
{"FAKE_POWERMETRICS_SLEEP_SCALE": "12"},)` around
`super()._run_bounded_capture(...)` (:1657-1661). **Production deadlines
touched:** only `_capture_timeout_s` (powermetrics.py:1468-1470) via the
bounded path at :1201 — and `--no-sleep` means the fake never sleeps
(fake_powermetrics_process.py:44,73), so wall time is ~0 and the 12x is never
spent. The continuous admission deadline `time.monotonic() +
self._capture_timeout_s(config, count + 1)` (powermetrics.py:1256), the one
report 31 starved, is back at scale 1. **No wall-clock exposure added.**
**New hazard (should-fix):** `assertGreater(nominal_s * capture["scale"],
capture["timeout_s"], ...)` (:1690-1693) holds only when the derived post
count is **>= 26**. With `power_hz=20`/`idle_seconds=1.5` (:777-779),
`count = max(3, ceil(min(5.0, baseline.duration_s)/0.05))`
(powermetrics.py:1029-1031) ≈ 30 — a 4-sample / 0.2 s margin. A shorter
measured baseline reds this guard rather than the defect; it fails loudly
with its own message, so brittle, not silent.

**(c) Host-dependent pins: none.** Count/interval/timeout are derived and
cross-checked against argv (:1679-1689); `scale >= 12.0` (:1678) is fixture
policy; the old `post_sample_count == 100` is re-derived
(test_run_campaign.py:9627-9634). Only the implicit `count >= 26` floor
couples to the host. Nit: post-count formula now in 3 homes, timeout formula
in 2 (powermetrics.py:1468-1470 vs test_controller.py:1688-1689).

## PR #326 — gitfix, 87039749

**(a) False positive: CONFIRMED, broad.** The new predicate
(test_git_fixture_maintenance.py:174-176) flags any call with the exact
literal `"init"` anywhere in its resolved argument tree; the old code also
required `"git"` in literals or a runner callee. Constructed in memory against
`_git_init_violations`: `subprocess.run(["git","status"], cwd=path)` +
`parser.add_argument("--phase", choices=["init","run"])` → `(2,)`;
`subprocess.run(["git","status"], env={"PHASE":"init"})` → `(1,)`;
`self.assertEqual(state["phase"], "init")` → `(1,)`;
`json.dumps({"phase":"init"})` → `(1,)`. Correctly clean: a function named
`init` (`init(repository)` → `{}`; callees excluded at :194-195),
`logger.info("init complete")`, `os.system("git status")`. Today only three
`"init"` literals exist (test_calibration_exits.py:2146,3650;
git_fixture.py:26), all legitimately exempt — prospective, not live.
Should-fix: gate the *bare*-`init` rule on the callee resolving to a runner
name (`subprocess.run`, `os.system`, `run`, `execute`, `_run`,
`_run_fixture_command` — the set the hygiene fixtures already use), keeping
the unconditional rule when `"git"` co-occurs or `_shell_git_init` matches;
all 13 hygiene fixtures still flag under that gate.

**(b) Renamed test vs by-name exception: airtight.** `_scope_name` (:52-59)
yields fully-qualified `Class.method`, matched exactly at :183, :190, :213; a
rename, a move to another class, or a nested `def` all miss the key and get
flagged — fail-closed, and their own
`test_named_maintenance_exceptions_do_not_exempt_other_tests` proves it.
Residual nit: nothing asserts the entries still resolve, so a *deleted* method
leaves a silent dead exception.

**(c) Two files: right home, but one stale artifact.** The mechanism has ONE
home (maintenance.py owns `_CommandLiterals`, `_git_init_violations`,
`MAINTENANCE_ON_EXCEPTIONS`); hygiene.py only imports it and adds adversarial
cuts. Acceptable; the smell is cross-module private imports, curable later by
moving the census to `tests/git_fixture_census.py`. **Missed should-fix:** the
PR routes `tests/test_identity_pins.py` through `init_git_fixture(root, "-q")`
but leaves `ESTABLISHED_LOCAL_HELPERS["tests/test_identity_pins.py"] =
{"init_git"}` (:29). That entry is now dead (no direct `init` call remains)
yet keeps a standing exemption, and
`test_established_local_helpers_retain_the_exact_tuple` (:317-325) only stays
green because the new `ImportFrom`-following clause (:232-241) resolves the
tuple through `tests/git_fixture.py`. Drop the entry.

## PR #327 — armfix, 100dfb2d (`tests/test_arm_readiness_dry_run.py`)

**(a) Order-dependence / flakiness: none found.** Sampled once per call before
the kind loop (:145 `authored_at_monotonic_ns = time.monotonic_ns()`, used at
:180), so all evidence receipts in one freeze share one `now`; only the
optional mint receipt (:201 `now_monotonic_ns=None`) uses the live clock —
identical under a frozen clock, else milliseconds against a 7-day horizon. The
one clock-freezing class, `ArmReadinessIntegrationTests.setUp`
(test_arm_readiness_integration.py:292-318), starts its
`mock.patch.object(time, "monotonic_ns", ...)` *before* `install_passing_freeze`
(:330, :567) and patches the same shared `time` module the fixture imports, so
the fixture reads the frozen anchor. No golden byte comparison exists: digests
are recomputed from bytes at read time (:139-143, :186-188) and `pack_sha =
readiness.committed_pack_tree_sha256(pack)` is derived
(test_arm_readiness_evidence_t0.py:445). Confirmed by running all four
dependent modules.

**(b) Monkeypatch scoping: clean and context-managed.**
`self.addCleanup(temporary.cleanup)` (:277); `with mock.patch.object(time,
"monotonic_ns", return_value=self.origin):` (:280); `with
mock.patch.object(time, "monotonic_ns", return_value=self.origin +
1_000_000_000):` (:298-300); `with mock.patch.object(time, "monotonic_ns",
return_value=self.origin + 8 * 86_400_000_000_000):` (:312-314). Nothing leaks.

**(c) Horizon duplicated: YES — should-fix.** `self.origin = 1 + 15 *
86_400_000_000_000 // 2` (:279) and `self.origin + 8 * 86_400_000_000_000`
(:313) hardcode 7.5 d / 8 d. ONE home:
`configs/arm_readiness/d117_row_registry_v2.json` →
`freeze_evidence_lifecycle.evidence_policies[kind].horizon_ns` =
`604800000000000` for `ACCEPTANCE_OWNER` — already loaded as `self.lifecycle`
(:283). Fix: `horizon = next(p["horizon_ns"] for p in
self.lifecycle["evidence_policies"] if p["kind"] == self.receipt["kind"])`,
then `origin = 1 + horizon + horizon // 14`, expire at `origin + horizon + 1`.
As written both tests keep passing if the registry horizon is retuned below
8 days.

## Merge-ability (#324, #325, #326, #327)

Pairwise **disjoint** files (`git diff --name-only ace4cc3c..HEAD`):
#324 `tests/test_controller.py`, `tests/test_run_campaign.py` · #325
(43c1ce95) `docs/contracts/calibration_ledger_append.md`,
`docs/phase_2/derivation_night_runbook.md`, `joulewise/calibration_exits.py`,
`scripts/recover_calibration_ledger.py`, `tests/test_calibration_exits.py` ·
#326 `tests/test_git_fixture_hygiene.py` (new),
`tests/test_git_fixture_maintenance.py`, `tests/test_identity_pins.py` · #327
`tests/test_arm_readiness_dry_run.py`.

**One real semantic interaction:** #326's census scans the whole tree
(`_git_init_violations` walks `tests_root.rglob("*.py")`, :251-258) and keys
`MAINTENANCE_ON_EXCEPTIONS` / `ESTABLISHED_LOCAL_HELPERS` by name on
`tests/test_calibration_exits.py` — the file **#325 adds 47 lines to**. A new
#325 test calling `git init` directly, or a rename of either excepted method,
would red the merged tree while both PRs are green alone. I ran #326's census
against each other worktree's `tests/` tree: `{}` for a177, a184, armfix,
gitfix. The census is per-file, so per-file clean over the union implies union
clean — no interaction today. **Integration replay must show:**
`tests.test_git_fixture_maintenance` + `tests.test_git_fixture_hygiene` green
on the merged tree (the only cross-PR coupling), plus `tests.test_controller`,
`tests.test_run_campaign`, `tests.test_calibration_exits`, and the four
`tests.test_arm_readiness_*` modules. No rebase: all four branch from ace4cc3c.

## Verdicts

- **#324 — MERGE.** Queue non-blocking: `assertEqual(len(bounded_captures), 1)`
  and a comment recording the `count >= 26` floor.
- **#326 — MERGE.** Queue non-blocking: drop the dead
  `ESTABLISHED_LOCAL_HELPERS["tests/test_identity_pins.py"]` entry; re-gate the
  bare-`init` rule on a runner callee.
- **#327 — FIX-FIRST.** Read the horizon from
  `self.lifecycle["evidence_policies"]` instead of hardcoding 7.5 d / 8 d at
  `tests/test_arm_readiness_dry_run.py:279,313`. Two lines; rest is clean.

## What I ran (`.venv/bin/python3 -B -m unittest -q`)

- wt-a177 `tests.test_controller tests.test_run_campaign.IdleAdmissionCoreVerdictTests`
  → `Ran 147 tests in 154.715s` / `OK`, EXIT=0
- wt-gitfix `tests.test_git_fixture_maintenance tests.test_git_fixture_hygiene
  tests.test_identity_pins` → `Ran 54 tests in 16.452s` / `OK`
- wt-armfix `tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence_t0
  tests.test_arm_readiness_lifecycle` → `Ran 152 tests in 943.659s` /
  `OK (skipped=1)`, EXIT=0
- wt-armfix `tests.test_arm_readiness_integration` → `Ran 13 tests in 256.033s`
  / `OK`, EXIT=0
- census probes: `_git_init_violations` imported from wt-gitfix, scanning
  synthetic trees in a `/tmp` TemporaryDirectory (no worktree written) — 8
  cases, results in §326(a)
- cross-tree census `_git_init_violations(<wt>/tests)` for gitfix, a177, a184,
  armfix → `{}` ×4
- `git diff ace4cc3c..<head>` / `--name-only` ×4; `git status --short` ×4 →
  all empty; reads of `joulewise/adapters/powermetrics.py`,
  `joulewise/arm_readiness.py`, `configs/arm_readiness/d117_row_registry_v2.json`,
  `tests/fixtures/fake_powermetrics_process.py`, records 25/27/37/39/44
