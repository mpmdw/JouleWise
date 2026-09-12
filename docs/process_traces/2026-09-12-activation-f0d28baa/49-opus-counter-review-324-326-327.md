# 49 — Opus counter-review (gate row 6) — PR #324, #326, #327

Diverse lens after records 25/31/33/37/39, 08/18/27, 41/44. Read-only. All bases = `origin/main` ace4cc3c.

## PR #324 — A177, 74a547cd (test_controller.py, test_run_campaign.py)

**(a)** Near-smallest; consult 39's 33 cuts cover clauses 1–21. **One clause has no killer:** only `capture = bounded_captures[0]` (:1677) is inspected and nothing pins `len(bounded_captures)` — `assertTrue(...)` (:1673) admits any number, so a mutation adding a *second, paced* bounded capture survives everything. Fix: `assertEqual(len(bounded_captures), 1)` after :1673.

**(b)** Not the CI-red class.
- Continuous pacing: `with patch.dict(os.environ, {"FAKE_POWERMETRICS_SLEEP_SCALE": "1"}):` (:1664) — ambient runner env cannot leak in.
- Bounded stress: `with patch.dict(os.environ, {"FAKE_POWERMETRICS_SLEEP_SCALE": "12"},)` around `super()._run_bounded_capture(...)` (:1657-1661).
- Only one production deadline is touched: `_capture_timeout_s` (powermetrics.py:1468-1470) via the bounded path at :1201 — and `--no-sleep` makes the fake skip sleeping (fake_powermetrics_process.py:44,73), so that capture's wall time is ~0 and the 12x is never spent. The continuous admission deadline (powermetrics.py:1256), which report 31 starved, is back at scale 1. No wall-clock exposure added.
- **New hazard (should-fix):** `assertGreater(nominal_s * capture["scale"], capture["timeout_s"], ...)` (:1690-1693) holds only for a derived post count **>= 26**; with `power_hz=20`/`idle_seconds=1.5` (:777-779) the derivation at powermetrics.py:1029-1031 gives ~30 — a 4-sample / 0.2 s margin. A shorter measured baseline reds this guard, not the defect; it fails loudly with its own message, so brittle rather than silent.

**(c) No host-dependent pin.** Count, interval and timeout are derived and cross-checked against argv (:1679-1689); `scale >= 12.0` (:1678) is fixture policy; the old `post_sample_count == 100` is re-derived (test_run_campaign.py:9627-9634). Only the `count >= 26` floor couples to the host.

## PR #326 — gitfix, 87039749

**(a) False positive CONFIRMED, broad.** The new predicate (:174-176) flags any call carrying the exact literal `"init"` anywhere in its resolved argument tree; the old code also required `"git"` in literals or a runner callee. Run in memory through `_git_init_violations`, these are flagged: `subprocess.run(["git","status"], cwd=path)` beside `parser.add_argument("--phase", choices=["init","run"])` → `(2,)`; `assertEqual(state["phase"], "init")` and `json.dumps({"phase":"init"})` → `(1,)` each. Correctly clean: a function literally named `init` (`init(repository)` → `{}`; callees excluded at :194-195). Only three `"init"` literals exist today (test_calibration_exits.py:2146,3650; git_fixture.py:26), all legitimately exempt — prospective, not live. Should-fix: gate the *bare*-`init` rule on the callee resolving to a runner name (subprocess.run, os.system, run, execute, _run, _run_fixture_command); all 13 hygiene fixtures still flag under that gate.

**(b) Airtight.** `_scope_name` (:52-59) yields a fully-qualified `Class.method`, matched exactly at :183, :190, :213, so a rename, a move to another class, or a nested `def` all miss the key and get flagged — fail-closed, and `test_named_maintenance_exceptions_do_not_exempt_other_tests` proves it. Nit: nothing asserts the entries still resolve, so a *deleted* method leaves a dead exception.

**(c) Right home, one stale artifact.** ONE home is maintenance.py; hygiene.py only imports it and adds adversarial cuts — acceptable. **Missed should-fix:** the PR routes test_identity_pins.py through `init_git_fixture(root, "-q")` but leaves `ESTABLISHED_LOCAL_HELPERS["tests/test_identity_pins.py"] = {"init_git"}` (:29). That entry is dead — no direct `init` call remains — yet keeps a standing exemption, and `test_established_local_helpers_retain_the_exact_tuple` (:317-325) only stays green because the new `ImportFrom`-following clause (:232-241) resolves the tuple through `tests/git_fixture.py`. Drop it.

## PR #327 — armfix, 100dfb2d (test_arm_readiness_dry_run.py)

**(a) No order-dependence or flakiness found.** The clock is sampled once per call, before the kind loop (:145 `authored_at_monotonic_ns = time.monotonic_ns()`, used at :180), so every receipt in one freeze shares one `now`; only the optional mint receipt (:201 `now_monotonic_ns=None`) reads the live clock, the same instant under a frozen clock. The one clock-freezing class, `ArmReadinessIntegrationTests.setUp` (test_arm_readiness_integration.py:292-318), starts its `mock.patch.object(time, "monotonic_ns", ...)` *before* `install_passing_freeze` (:330, :567) and patches the same shared `time` module the fixture imports, so the fixture reads the frozen anchor. No golden byte comparison exists: digests are recomputed at read time (:139-143, :186-188) and `pack_sha` is derived (test_arm_readiness_evidence_t0.py:445).

**(b) Scoped, context-managed, no leak.** `self.addCleanup(temporary.cleanup)` (:277), then `with mock.patch.object(time, "monotonic_ns", return_value=self.origin):` (:280) and the same `with` form at :298-300 and :312-314.

**(c) Duplicated — should-fix.** `self.origin = 1 + 15 * 86_400_000_000_000 // 2` (:279) and `self.origin + 8 * 86_400_000_000_000` (:313) hardcode 7.5 d / 8 d. ONE home: `configs/arm_readiness/d117_row_registry_v2.json` → `freeze_evidence_lifecycle.evidence_policies[kind].horizon_ns` = `604800000000000` for `ACCEPTANCE_OWNER`, already loaded as `self.lifecycle` (:283). Fix: read `horizon` from `self.lifecycle["evidence_policies"]` for `self.receipt["kind"]`, set `origin = 1 + horizon + horizon // 14`, expire at `origin + horizon + 1`. As written both tests keep passing if that horizon drops below 8 days.

## Merge-ability (#324, #325, #326, #327)

Pairwise **disjoint** (`--name-only ace4cc3c..HEAD`) — #324: test_controller.py, test_run_campaign.py; #325 (43c1ce95): two docs + joulewise/calibration_exits.py, scripts/recover_calibration_ledger.py, tests/test_calibration_exits.py; #326: test_git_fixture_hygiene.py (new), test_git_fixture_maintenance.py, test_identity_pins.py; #327: test_arm_readiness_dry_run.py.

**One real semantic interaction:** #326's census scans the whole tree (`rglob("*.py")`, :251-258) and keys its two exception tables by name on `tests/test_calibration_exits.py` — the file **#325 adds 47 lines to**. A new #325 test calling `git init`, or a rename of either excepted method, would red the merged tree while both PRs are green alone. I ran #326's census over each other worktree's `tests/`: `{}` for a177, a184, armfix, gitfix; the census is per-file, so per-file clean over the union implies union clean — no interaction today. **Integration replay must show** test_git_fixture_maintenance + test_git_fixture_hygiene green on the merged tree (the only cross-PR coupling), plus test_controller, test_run_campaign, test_calibration_exits and the four test_arm_readiness_* modules. No rebase: all four branch from ace4cc3c.

## Verdicts

- **#324 — MERGE.** Non-blocking: add `assertEqual(len(bounded_captures), 1)`; comment the `count >= 26` floor.
- **#326 — MERGE.** Non-blocking: drop the dead `ESTABLISHED_LOCAL_HELPERS["tests/test_identity_pins.py"]` entry; re-gate the bare-`init` rule on a runner callee.
- **#327 — FIX-FIRST.** Read the horizon from `self.lifecycle["evidence_policies"]` instead of hardcoding 7.5 d / 8 d at test_arm_readiness_dry_run.py:279,313. Two lines; rest is clean.

## What I ran (`.venv/bin/python3 -B -m unittest -q`, EXIT=0 each)

- wt-a177 `test_controller` + `test_run_campaign.IdleAdmissionCoreVerdictTests` → `Ran 147 tests in 154.715s` / `OK`
- wt-gitfix `test_git_fixture_maintenance test_git_fixture_hygiene test_identity_pins` → `Ran 54 tests in 16.452s` / `OK`
- wt-armfix `test_arm_readiness_dry_run test_arm_readiness_evidence_t0 test_arm_readiness_lifecycle` → `Ran 152 in 943.659s` / `OK (skipped=1)`; `test_arm_readiness_integration` → `Ran 13 in 256.033s` / `OK`
- census probes (8 cases, §326a) + cross-tree census → `{}` ×4, via `_git_init_violations` imported from wt-gitfix over synthetic trees in a `/tmp` TemporaryDirectory; no worktree written
- `git diff`/`--name-only` ×4, `git status --short` ×4 → empty; reads of powermetrics.py, arm_readiness.py, d117_row_registry_v2.json, fake_powermetrics_process.py, records 25/27/37/39/44
