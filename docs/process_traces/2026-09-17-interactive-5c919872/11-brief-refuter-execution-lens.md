# Refuter (execution lens) — NIGHT-GATE-QUIET-ADMISSION-01 (seat Q, after fix round 1)

Branch `feat/2026-09-17-night-gate-quiet-admission`, head `__HEAD__`, base `a90ab4e8`. Diff: `git diff a90ab4e8..__HEAD__ -- joulewise scripts tests docs/contracts docs/process docs/phase_2`. You are in a detached worktree at that head; WRITE_SCOPE is EMPTY — you may not edit, commit, stash, or checkout anything here. For every mutant, `cp -R <this worktree>/. /tmp/refute-exec/` and edit the copy only (use `git show`/`git diff`, never checkout/stash). Never touch `/Users/edr/code/JouleWise`, any other worktree, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`, or `launchctl`; no network; no `sudo`; no `[QUIET-MAC]` work. Run tests as `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest <module>`; `sysctl` and `top` are denied in your sandbox, so skip the live sampler (the lead ran it natively).

Read first: the seat brief `docs/process_traces/2026-09-17-interactive-5c919872/01-brief-seat-quiet-admission.md` (the eleven regressions and the mutants each must kill), the fix-round brief `08-brief-seat-Q-fix-round-1.md` (items 4, 7, 10 add regressions), and the magistrate synthesis `70-coldgate-packet-quiet-admission/13-magistrate-synthesis-ruling-70-with-opus-amendments.md` (verdicts in force). Do not read the seat reports; the worktree is the ground truth.

Severity: BLOCKER = a named mutant survives the test that must kill it; a regression passes on the base for a reason other than the defect (vacuous); a test sleeps for real interval lengths or depends on the live machine; the driver's bind loop can be blocked by a hung sampler; a v2 fixture's bytes or verdict change. SHOULD-FIX = wrong but bounded. NIT = cosmetic. Every finding: severity, file:line, the brief line you hold it against (quoted), the exact mutant (diff or one-line description), the command, observed output. Do not predict; "still pending" if a run has not finished. Final message: the review envelope under 8000 bytes.

## Your lens: execution — run, mutate, measure

Run the six named modules and paste the tail. Then build and run EACH mutant below against the test the brief names; report kill or SURVIVE with the assertion text:

1. First-pass GO (admit on the first quiet sample) → regression 1.
2. Non-consecutive GO (do not reset the run on a busy sample) → regression 1.
3. Continue polling after GO → regression 1.
4. Journal keeps only the last sample; receipt digest/count from a truncated journal → regression 2.
5. Deadline reset on each sample (bind window restarts) → regression 2 and 8.
6. Load average authorises admission (retain `LOAD_MAX` veto or use load as a pass) → regressions 3 and 4.
7. Name exemption: subtract `fseventsd`/`mds_stores` from the aggregate → regression 3 and 6.
8. Use the decaying `%CPU` column instead of interval deltas → regression 4 (construct the counterexample: a process with a high `%CPU` but zero delta).
9. Census replay: reuse the driver's first census in the bind loop → regression 5.
10. PID reuse aliasing (identity by pid alone) and exited-process loss → regression 6.
11. Observer subtracted or unlabelled → regression 6.
12. v2 default insertion: `from_mapping` fills `quiet_admission` for a v2 plan; generator emits v4 without the flag → regression 7 and `gen_derivation_night.py --check`.
13. GO shifts `E`, completion, courier boundary or dead-man → regression 8.
14. Wall-clock rollback extends the bind deadline → regression 8.
15. Successor allowed on a bare refusal file, or on a started/reserved night, or reusing the predecessor's digest → regression 9.
16. Sampler hang blocks the census or the expiry (sequential blocking call) → regression 10.
17. Malformed sampler output treated as quiet → regression 10.
18. `top -s` argv built from a float (fix item 7) → the argv exact-tuple test; also the mutant that drops the integer validation of `sample_interval_s`.
19. Bind expiry emits `night_refused_not_quiet` instead of `night_refused_bind_expired`; `classify_abort` places the new code off the cold-gate path (fix item 4).
20. `cutoff_authority` empty string accepted; `busy_core_max` defaulted when absent (fix items 2–3).
21. Generator accepts `post_bind_budget_s` 7979 or `window_max_s` = bind + runway − 1 (fix item 10).

Also: run `PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check` and `python3 -m compileall -q scripts joulewise`; time the six modules and flag any test over 10 s; grep the tests for `time.sleep(` with a literal ≥ 5 and for any `subprocess` call that reaches a real `ps`/`top`/`sysctl` inside a unit test. Report the mutant table (21 rows: mutant, test, KILLED/SURVIVED, assertion) as the core of the envelope.
