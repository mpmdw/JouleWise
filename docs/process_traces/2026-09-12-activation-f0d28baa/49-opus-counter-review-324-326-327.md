# 49 — Opus counter-review (gate row 6) — PR #324, #326, #327

Diverse lens after the prior records. Read-only. Bases = ace4cc3c.

## PR #324 — A177, 74a547cd (test_controller.py, test_run_campaign.py)

**(a) One clause has no killer:** only `bounded_captures[0]` (:1677) is inspected and nothing pins `len(bounded_captures)` — `assertTrue(...)` (:1673) admits any number, so a mutation adding a *second, paced* bounded capture survives. Fix: `assertEqual(len(bounded_captures), 1)`.

**(b)** Not the CI-red class.
- Continuous pacing: `with patch.dict(os.environ, {"FAKE_POWERMETRICS_SLEEP_SCALE": "1"}):` (:1664).
- Bounded stress: `with patch.dict(os.environ, {"FAKE_POWERMETRICS_SLEEP_SCALE": "12"},)` around `super()._run_bounded_capture(...)` (:1657-1661).
- One production deadline is touched — `_capture_timeout_s` (powermetrics.py:1468-1470) on the bounded path at :1201 — but `--no-sleep` makes the fake skip sleeping (fake_powermetrics_process.py:44,73), so wall time is ~0 and the 12x is never spent. The continuous admission deadline (powermetrics.py:1256) report 31 starved is back at scale 1.
- **New hazard (should-fix):** `assertGreater(nominal_s * capture["scale"], capture["timeout_s"], ...)` (:1690-1693) holds only for a derived post count **>= 26**; `power_hz=20`/`idle_seconds=1.5` (:777-779) with powermetrics.py:1029-1031 gives ~30 — a 4-sample margin. A shorter measured baseline reds this guard rather than the defect.

**(c) No host-dependent pin.** Count, interval and timeout are derived and cross-checked against argv (:1679-1689), and `scale >= 12.0` (:1678) is fixture policy. Only the `count >= 26` floor couples to the host.

## PR #326 — gitfix, 87039749

**(a) False positive CONFIRMED, broad.** The new predicate (:174-176) flags any call carrying the exact literal `"init"` anywhere in its resolved argument tree; the old code also required a co-occurring `"git"` or a runner callee. Flagged when run in memory through `_git_init_violations`: `subprocess.run(["git","status"], cwd=path)` beside `parser.add_argument("--phase", choices=["init","run"])` → `(2,)`; likewise `assertEqual(state["phase"], "init")` and `json.dumps({"phase":"init"})`. Correctly clean: a function literally named `init` (`init(repository)` → `{}`; callees excluded at :194-195). Prospective: the live tree's three `"init"` literals are all exempt. Should-fix: gate the *bare*-`init` rule on a runner callee (subprocess.run, os.system, run, execute, _run); all 13 hygiene fixtures still flag under that gate.

**(b) Airtight.** `_scope_name` (:52-59) yields a fully-qualified `Class.method`, matched exactly at :183, :190, :213, so a rename, a move to another class, or a nested `def` misses the key and gets flagged — fail-closed, as their own rename test proves. Nit: nothing asserts the entries still resolve, so a deleted method leaves a dead one.

**(c) Right home, one stale artifact.** ONE home = maintenance.py; hygiene.py only imports and attacks it — acceptable. **Missed should-fix:** the PR routes test_identity_pins.py through `init_git_fixture(root, "-q")` yet leaves `ESTABLISHED_LOCAL_HELPERS["tests/test_identity_pins.py"] = {"init_git"}` (:29) — dead, no direct `init` call remains, but still a standing exemption; `test_established_local_helpers_retain_the_exact_tuple` (:317-325) stays green only via the new `ImportFrom` clause (:232-241). Drop it.

## PR #327 — armfix, 100dfb2d (test_arm_readiness_dry_run.py)

**(a) No order-dependence or flakiness found.** The clock is sampled once per call, before the kind loop (:145 `authored_at_monotonic_ns = time.monotonic_ns()`, used at :180), so every receipt in one freeze shares one `now`. The one clock-freezing class, `ArmReadinessIntegrationTests.setUp` (test_arm_readiness_integration.py:292-318), starts its `mock.patch.object(time, "monotonic_ns", ...)` *before* `install_passing_freeze` (:330, :567) on the same shared `time` module the fixture imports. No golden byte comparison exists: digests are recomputed at read time (:139-143, :186-188).

**(b) Scoped, context-managed, no leak.** `self.addCleanup(temporary.cleanup)` (:277), then `with mock.patch.object(time, "monotonic_ns", return_value=self.origin):` (:280); same form at :298-300, :312-314.

**(c) Duplicated — should-fix.** `self.origin = 1 + 15 * 86_400_000_000_000 // 2` (:279) and `self.origin + 8 * 86_400_000_000_000` (:313) hardcode 7.5 d / 8 d. ONE home: `configs/arm_readiness/d117_row_registry_v2.json` → `freeze_evidence_lifecycle.evidence_policies[kind].horizon_ns` = `604800000000000` for `ACCEPTANCE_OWNER`, already loaded as `self.lifecycle` (:283). Fix: read `horizon` for `self.receipt["kind"]`, then `origin = 1 + horizon + horizon // 14`, expiring at `origin + horizon + 1`. As written both tests pass silently if the registry horizon changes.

## Merge-ability (#324, #325, #326, #327)

Pairwise **disjoint** (`--name-only ace4cc3c..HEAD`) — #324: test_controller, test_run_campaign; #325 (43c1ce95): 2 docs + calibration_exits.py, recover_calibration_ledger.py, test_calibration_exits; #326: test_git_fixture_hygiene (new), test_git_fixture_maintenance, test_identity_pins; #327: test_arm_readiness_dry_run.

**One real semantic interaction:** #326's census scans the whole tree (`rglob("*.py")`, :251-258) and keys its two exception tables by name on tests/test_calibration_exits.py — the file **#325 adds 47 lines to**. A new #325 test calling `git init`, or a rename of either excepted method, reds the merged tree while both PRs are green alone. That census over each other worktree's `tests/` returns `{}` (a177, a184, armfix, gitfix); it is per-file, so the union is clean too. **Integration replay must show** the two git-fixture modules green on the merged tree — the only cross-PR coupling — plus test_controller, test_run_campaign, test_calibration_exits and the four test_arm_readiness_* modules. No rebase: all four branch from ace4cc3c.

## Verdicts

- **#324 — MERGE.** Non-blocking: add `assertEqual(len(bounded_captures), 1)`.
- **#326 — MERGE.** Non-blocking: drop the dead `ESTABLISHED_LOCAL_HELPERS["tests/test_identity_pins.py"]` entry; re-gate the bare-`init` rule on a runner callee.
- **#327 — FIX-FIRST.** Read the horizon from the registry instead of hardcoding 7.5 d / 8 d at test_arm_readiness_dry_run.py:279,313.

## What I ran (unittest -q, EXIT=0 each)

- a177 `test_controller` + `test_run_campaign.IdleAdmissionCoreVerdictTests` → `Ran 147 in 154.715s` / `OK`
- gitfix `test_git_fixture_maintenance test_git_fixture_hygiene test_identity_pins` → `Ran 54 in 16.452s` / `OK`
- armfix `test_arm_readiness_dry_run evidence_t0 lifecycle` → `Ran 152 in 943.659s` / `OK (skipped=1)`; `test_arm_readiness_integration` → `Ran 13 in 256.033s` / `OK`
- census probes (8 cases, §326a) + cross-tree census → `{}` ×4, via `_git_init_violations` over synthetic `/tmp` trees
- `git diff`/`--name-only` ×4, `git status --short` ×4 → empty
