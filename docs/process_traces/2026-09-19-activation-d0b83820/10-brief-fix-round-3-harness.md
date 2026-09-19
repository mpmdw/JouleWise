SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/test_sample_quiet_predicate_evidence.py"]

# Fix round 3 — lane QUIET-PREDICATE-EVIDENCE-01 harness, D5-T1: delete the liveness floor; two deterministic tests (cold gate packet 08, ruling 10 + refuter 11, adjudication 08a)

Cwd is the linked worktree of branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `37ca3c35` (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; scratch under `/tmp` only; no `sudo`, no `powermetrics`, no live `collect`. Nothing is armed; the real-load test may run. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not commit. Do not end your turn before the report is complete.

Read first (absolute paths in another worktree; read as files): `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/08a-adjudication-d5-t1-liveness-floor.md`, and in the same directory `08-coldgate-packet-d5-t1-liveness-floor/10-coldgate-fable-ruling.md` and `11-opus-contract-refuter.md`.

## Do

1. In `test_real_load_tracks_point_one_core_and_guards_worker_budget`, delete exactly this line and nothing else: `self.assertGreater(claimed_s, 0.0, "no CPU burned: the real burn profile did no work")`.
2. Add `test_burn_profiles_advance_their_generator` to `LoadTests`: for `profile in ("scalar", "memory")`: `burn = harness.burn_profile(profile, 1)`; `self.assertNotEqual(burn(1000), burn(1), f"{profile} burn did no work")`; and for scalar additionally assert the first call from a fresh generator equals `(1664525 * 1 + 1013904223) & 0xFFFFFFFF` (= 1015568748) and the second call differs. Verify the constants against `burn_profile` in the script before asserting; if the LCG differs, use the script's constants and report it.
3. Add refuter 11's `test_load_worker_runs_its_window_after_the_rendezvous` verbatim (fake clock; patches `harness.set_qos`, `harness.identity`, `harness.burn_profile`, `harness.Clock`; asserts two sends, no error, > 0 period rows, Σ cpu_used_s ≈ .3 ± .001, clock at 4.0). Verify every patched name exists in the script at `37ca3c35` and that the connection protocol (`recv` returns the rendezvous start, two `send` calls) matches `load_worker`; adapt names only if the script differs, and report the adaptation.

## Bench acceptance (execute; paste tails)

- Module twice under unittest; expect 45 tests OK both times, with wall times.
- Mutations, each on a `/tmp` copy of the tree (the worktree's production script must be byte-identical afterwards): `cores`, `alignment`, `observer` (the `docs/process_traces/2026-09-18-activation-507514d5/02a-refuter-execution-mutations.py` patterns), `clock` (`Clock.cpu → 0`), `catchup-capped`, `burn-noop` (`burn_profile` → `lambda count: None`), and NEW `window-skip` (`clock.sleep_until(start)` → `clock.sleep_until(start + config["duration_s"])` at the rendezvous line, ~:869). Each must produce ≥ 1 failure; paste the failing test names. If `window-skip` survives, that is a finding, not a fix.
- Same-signature statements for BOTH: "real-load assertion fails on correct code under scheduler starvation" and "assertion keyed to a quantity starvation destroys" (expect none found; the zero-service fake-clock probe from ruling 10 is the evidence).
- `git diff --stat`: only the scoped file.

## Report

`claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; commands with outcomes; findings with counterfactual and call site.
