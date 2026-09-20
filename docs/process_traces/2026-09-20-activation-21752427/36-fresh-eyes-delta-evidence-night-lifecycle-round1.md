# Record 36 — fresh-eyes delta re-audit of B1 fix round 1 (`b678b1dc..472d12c5` + merge `0481bb0b`), 2026-09-20 ≈11:35 PDT

Auditor: Opus 5 subagent (read-only; /tmp copies). Verbatim report:

VERDICT: PASS (4 residual findings, none blocking; no regression introduced by the round)

Read-only; all execution in `/tmp/dre21752427` and `/tmp/dre-mut` (cp -R of the worktree at 0481bb0b). Canonical untouched. Line numbers below are `/Users/edr/code/JouleWise-wt-lifecycle-21752427/joulewise/evidence_night.py` unless noted.

1. Closures B1–B12: all implemented as dictated, none wider. B1 gate 740-746 (liveness≠ABSENT, plists+`.prior` via installer `Target`/`LABELS`, `launchctl list` rc≠0 ⇒ refuse), wired into `check` 797 and repeated pre-publication 989-991; recovery 1023-1039. B2 1061-1068 (validate before any installer call). B3 686-708. B4 364-366 + test_b4_prepare_check_prepare. B5 162-178, 992-995. B6 659-682. B7 891-909, called 938. B8 777/808-809/881/924-927/1009. B9 917 precedes every sealed stat; `sealed_state` 531-537 refuses, never FileNotFoundError. B10 507-509 = prepare's `.locks` domain. B11 974-978 cause, 930-932 age bound, 25-26 + 600-601 records 19/21. B12 648-650.
Mutants (all killed, single-test runs):
(a) `installed = True` → `test_b1_foreign_jobs_preserved_after_installer_refusal` FAIL "AssertionError: True is not false" (`--uninstall` reached).
(b) caller-side `night_gate.AGENT_CENSUS_ARGV` → `test_b6_clone_old_census_literal_is_reported` FAIL "'[c]odex|[c]laude|[t]3' != 'codex|claude|t3'".
(c) skip raw-pid parse → `test_b3_unresolved_raw_pid_reobserved_once` FAIL "Refused not raised".
Replaying the closure tests against the b678b1dc module: 19 failures / 22 errors, 0 closure tests passing.

2. B1 classification is CORRECT. In `night_agent_install.py`: rc 0 only from COMMITTED (416-421) — the sole ownership transfer, and the sole `--uninstall` trigger (1029). rc 2/3 covers `night_agent_already_loaded` at VALIDATED (481, pre-stage), retained-prior (179), plan/timing refusals (589-603), and bootstrap/verify failures (502/508) whose teardown does `verified_bootout` + prior restore (424-448) leaving `result` at 2/3; every retention overrides to 4 (437) or 1 (447/454), and `Refused(1, …)` at write_plist (494) makes rc 1 genuinely ambiguous — correctly "uncertain" (1025-1026, 1035-1036), as are SIGKILL (-9) and everything else. `scripts/install_night_agent.sh:87` `exec`s, so codes pass through; its own exits are 2. The "rc 0 install silently overwrites a foreign plist" hazard is unreachable because step 0 refuses on ANY existing night plist.

3. B6 confirmed: argv and `classify_arm_census` both run as `<clone>/.venv/bin/python -B -c` with cwd=clone (679-682); `test_b6_classification_runs_inside_clone` asserts argv[:3] and cwd; the old-literal fixture clone reports `codex|claude|t3` and `check` refuses (canonical/census-fix lens). No caller-side `night_gate`/`arm_census` import remains in the `check` path.

4. Merge survived: probe at line 110 inside `build_venv`, absent from the prepare path (402-409), asserted both ways. `/opt/homebrew/bin/python3.11` (3.11.15): `Ran 62 tests in 187.094s / OK`. Also 3.13: evidence_night 62 OK; arm_sequence+install_night_agent+arm_census+arm_retry `Ran 118 tests … OK`.

5. Contract crosswalk: `armable` still a pre-arm verdict only (doc:154) and the fake-launchctl "rehearsal, never armable" rule is explicit (doc:300-307). Three code refusals are undocumented: "unresolved raw census row" (693), "malformed attempt journal/inventory" (757, 907), "installer ownership/rollback unknown" (1036, described in prose only). doc:228 reads as if `armable: true` + literal `launchctl` were unconditional; the rehearsal exception appears only 75 lines later. No doc claim lacks code.

FINDINGS
F1 (should-fix, residual of Opus 2's class): `retry_inventory` imports `classify_abort` from the CALLER's checkout (751) while every other evidence lens now runs inside the clone. The route is evidence-bearing — a non-`retry` route fails `check` — so a caller ahead of/behind H silently changes the verdict. Not dictated by brief 35; it is the unclosed remainder of the stale-module signature.
F2 (nit, residual of Opus 1's class): `retry_inventory:752` and `notice_unused:899` read `attempts.json` / root-level `arm-attempts/` at the candidate root, but `prepare`'s `expected_stage` (363-372) admits only `prepare.json`, `lifecycle`, `night_plan.json`, `render` — if the bench or B2 writes those files there, `prepare` reruns refuse "unknown or uncheckpointed staging output".
F3 (nit): recovery treats installer rc 128+n (Shield `Signalled`, 80-99) as uncertain although retention would have overridden it to 1/4; over-conservative only (plan stays published, state named).
F4 (nit): doc gaps in §5 above.

SAME-SIGNATURE STATEMENTS
"Entry point silently diverges from the bench procedure": I find no silent divergence left in the four subcommands. Bench step 0 is now a gate in both `check` and immediately before publication; the step-5 night-directory baseline is declared as deferred (doc:308-311); courier availability is stated as a PATH check, not an invocation. The one undeclared divergence is F1 (verdict computed with the caller's code, not H's).
"An evidence-affecting side effect without a refusal path": every lifecycle write is atomic (162-178) and refuses on a pre-existing `.tmp`, with the leftover cleaned in `finally`; the two new side effects (`.locks/<name>.lock`, `<staging>/lifecycle/`) are declared in the contract, tolerated by `prepare`, and pinned by `test_check_passes_and_writes_only_check_json`'s exact write set. The only unrefused derivation left is `cause` (974-978), a regex over installer stderr with no ambiguity refusal — but the installer prints its refusal line before teardown warnings, and every wrong parse routes to `cold_gate` (only `arm_transport` routes to `retry`, and the installer never emits it), so the failure direction is conservative.

## Magistrate disposition (11:36 PDT) → round 2 (seat 37, in a second worktree while replay 36 runs)
F1 ACCEPT: run `arm_retry.classify_abort` inside the clone's python over the inventory JSON, as B6 does; counterfactual: a fixture clone whose `arm_retry` routes everything to `retry` vs the caller's → the verdict must follow the CLONE. F2 ACCEPT: the attempt inventory and prior-attempt records live under `<staging>/lifecycle/` (single home), and `prepare`'s whitelist stays as is; `attempts.json` at the candidate root is no longer read. F3: no change (conservative). F4 ACCEPT: document the three refusals; move the rehearsal exception next to `armable` in the contract.
