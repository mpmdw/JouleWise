# Seat brief — ARM-READINESS-FIXTURE-CLOCK-ORIGIN-01: the arm-readiness test fixture authors evidence at monotonic origin 1 ns, so hosts awake > 7 days read it as expired

WRITE_SCOPE: ["tests/test_arm_readiness_dry_run.py","tests/test_arm_readiness_lifecycle.py","tests/test_arm_readiness_evidence_t0.py","tests/fixtures/**"]

Implementation seat in the linked worktree you were started in (branch
`fix/2026-09-12-arm-readiness-fixture-clock-origin`, from origin/main
`ace4cc3c`). TEST/FIXTURE FILES ONLY: production `joulewise/`, `scripts/`,
`configs/` are out of scope (the defect is the fixture's clock origin, not
production expiry — root-cause report 41 §Remediation). Never move HEAD,
never push, never touch `/Users/edr/code/JouleWise` (read-only use of its
`.venv/bin/python3` allowed), `/Users/edr/JouleWise-measurement-20260913-derivation`
or `/Users/edr/night-custody`. `python3 -m unittest` only; no sudo.

Read first: `../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/41-rootcause-arm-readiness-bench-refusals-astra-report.md`
(Q1 numbers, Q2 mechanism, §Remediation) and its brief 40.

## Defect (bench-verified)
`install_passing_freeze` supplies `now_monotonic_ns=1`
(`tests/test_arm_readiness_dry_run.py:176`); the production assembler adds
the kind's horizon (7 days = 604_800_000_000_000 ns) so the fixture evidence
carries `valid_until_monotonic_ns = 604800000000001`; freeze replay
authenticates against the LIVE host monotonic clock
(`joulewise/arm_readiness.py:7564` → `:6294-6299`), which on this host is
≈ 6.42e14 ns (7.43 days awake) → `readiness_record_expired` /
"evidence item expired". Seven tests fail deterministically at the bench
(list in brief 40); CI (Ubuntu, fresh boots) never sees it. Fourth member
of the host-state fixture family (87, 99, 19 were timing; this one is
uptime).

## Work
1. Cure the shared fixture's clock origin: author at the current host
   monotonic time (as production does, `joulewise/arm_readiness_evidence.py:3395`)
   — ONE helper, every caller routed through it (dry_run, lifecycle,
   evidence_t0 use the same freeze helper per report 41; find every
   `now_monotonic_ns=1` / literal-origin site with grep and route it). Do
   not change any production expiry check or horizon. Do not change any
   test's assertions except where an assertion encodes the literal origin.
2. Defect-shaped regression: a test that authors evidence through the
   helper and authenticates it under a synthetic "now" of origin + 8 days
   must be refused `readiness_record_expired` (proves the production expiry
   still bites), AND a test that authenticates at origin + 1 s must PASS on
   a host of any uptime (monkeypatch `time.monotonic_ns` to origin + 7.5
   days to simulate this host — the pre-fix fixture must FAIL that test;
   paste the killed cut: restore the literal `1` origin → FAIL; cure → PASS;
   sha256 before/after).
3. Run the seven previously failing tests by dotted name (from brief 40)
   → all PASS; then the three modules whole (`tests.test_arm_readiness_dry_run
   tests.test_arm_readiness_lifecycle tests.test_arm_readiness_evidence_t0`,
   ~12 min; the real-boot ACID test may skip in a sandbox — say so);
   `git diff --check`. Do NOT commit; report `git status --short` and
   `git diff --stat`.

## Report (claude-codex-report/v1 envelope per --genre)
Sites routed (file:line), the helper, killed-cut lines, the seven tests'
result line, module results, any NEEDS_SCOPE/NEEDS_RULING. Under 8000 bytes.
