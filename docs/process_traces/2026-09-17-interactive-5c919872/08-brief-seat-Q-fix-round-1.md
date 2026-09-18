SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/night_gate.py","joulewise/night_plan_writer.py","joulewise/arm_retry.py","joulewise/quiet_admission.py","scripts/run_night.py","scripts/gen_derivation_night.py","tests/test_night_gate.py","tests/test_night_plan_writer.py","tests/test_arm_retry.py","tests/test_run_night.py","tests/test_gen_derivation_night.py","tests/test_quiet_admission.py","tests/night_gate_fixtures/**","docs/process/NIGHT_HANDBACK.md","docs/phase_2/derivation_night_runbook.md","docs/contracts/night_quiet_admission.md","docs/contracts/pack_night_go_receipt.md"]
BASE_HEAD: 6bcd90a3
BASELINE_MANIFEST: .codex-bridge/baselines/mag-5c919872-gate-quiet-fix1-2020.json
BASELINE_DIGEST: sha256:8c38207ff202603d4ec42820348cc6fc61e526888adc6e26b109f92535c8152e
LEASE_ID: lease-79c5a1766616453fb93e93b7cea20ffd

# Seat Q fix round 1 — apply cold-gate ruling 70 (as synthesized), rule F1, cure the live-sampler defect

Your D1–D7 work is committed by the lead as `6bcd90a3` on `feat/2026-09-17-night-gate-quiet-admission` in `/Users/edr/code/JouleWise-wt-gate-quiet` (the sandbox denies git metadata writes in linked worktrees; do not try to commit — leave every change unstaged and the lead commits by pathspec). Do NOT push. Everything else in the original brief stands (worktree, WRITE_SCOPE now plus `docs/contracts/pack_night_go_receipt.md`, no `launchctl`, no `~/night-custody`, no network, no `sudo`). Do not end your turn before every item below is done or a genuine early return is required.

The magistrate's synthesis of the ruling is the authority for this round; read it first (read-only, absolute path): `/Users/edr/code/JouleWise/docs/process_traces/2026-09-17-interactive-5c919872/70-coldgate-packet-quiet-admission/13-magistrate-synthesis-ruling-70-with-opus-amendments.md`. The ruling itself (`10-coldgate-fable-ruling.md`) and the refuter (`12-opus-pairing-refuter-on-ruling-70.md`) are beside it; read them where the synthesis cites them. D-182 (Ed's rule authorising the zero-capture successor route) is MERGED on main (`dfc50f43`, `docs/decision_log.md` D-182), so stage D7 stays; read the D-182 section for the exact terms and make `docs/process/NIGHT_HANDBACK.md` R1 and the `arm_retry` description cite "D-182" by id.

## Items (one unstaged, self-contained change set; the lead commits)

1. **Slot arithmetic.** A capture slot's budget is 480 s (`scripts/gen_derivation_night.py:88`), not 60 s. Every joule sentence in `docs/contracts/night_quiet_admission.md` (and any comment or docstring you wrote) uses 480 s and the ≈1 J attribution limit / ≈5 J claim-side bar of D-078 clause 11 (`docs/decision_log.md` around lines 4745–4760; read them). Show the corrected worked example: at 5 W per core, 0.05 core → 120 J per slot, 0.01 core → 24 J, and a 1 J ceiling → 0.0004 core, below the sampler's own measured cost; say plainly that this is why the cutoff must be measured, not computed.

2. **No candidate cutoff anywhere.** Remove `0.05` (and any other number presented as a candidate or default) from the contract doc, docstrings, generator help text and any generated or fixture plan that could be mistaken for a real plan. Plan-validation fixtures carry `busy_core_max: 0.0` (admits nothing). Tests of the GO path inject their own values inside the test body. The generator's `--quiet-admission-json` has no default value for any key.

3. **Cutoff authority field.** `quiet_admission` gains a REQUIRED non-empty string `cutoff_authority` naming the record path of the gate ruling that affirmed `busy_core_max`; validation refuses an empty or missing string (`night_plan_malformed`); test fixtures use the literal `TEST-ONLY-NOT-A-RULING`; the generator requires it in the JSON input. Document it in the contract doc: no v4 plan can be authored without naming who affirmed its cutoff.

4. **Distinct bind-expiry code.** Bind-window expiry refuses with `night_refused_bind_expired`, registered in `NIGHT_DRIVER_REASON_CODES` (`scripts/run_night.py`), in the gate's refusal codes, and in `arm_retry.COLD_GATE_CODES` with the same class as `night_refused_not_quiet` (the description says: bind window expired with every sample recorded; successor route per D-182). `night_refused_not_quiet` keeps its one-shot meaning for v2 plans and for the non-CPU hard predicates. Regression: expiry yields exactly `night_refused_bind_expired` and `classify_abort` places it on the cold-gate path.

5. **Admission is not capture evidence.** Receipt v3 carries `admission_is_capture_evidence: false` (a required key with that exact value); the contract doc states in one sentence why (after GO the chain reserves first and then runs a 600 s settle before the first slot, `scripts/night_chains/calibration_derivation_only.zsh` lines 187 and 218).

6. **F1 ruling — receipt contract.** Ruled: a prospective packless-v4 exception. Amend `docs/contracts/pack_night_go_receipt.md` at the two clauses (§2 around line 135–137 and §10 S3 around line 1224; read them) with a dated sentence: "For `joulewise.night_plan.v4` (packless) plans the receipt schema is `joulewise.unattended_night_receipt.v3`, validated by the versioned validator; the v2 `_RECEIPT_KEYS` shape and the v2 validation path for every existing class, including every transaction-pack v3 class, are byte-for-byte unchanged (cold-gate ruling 70 Q8 and Q10; magistrate synthesis 13; 2026-09-17)." Change nothing else in that file. If the receipt v3 validator is not yet wired (your F1 says "the contract was preserved"), wire it now per D5 and prove with regression 7 that v2 receipts and every legacy scenario are byte-identical.

7. **Live sampler defect (found by the lead running V5 natively).** `sample_interval` builds `top -l 2 -s 30.0` from a float; `top` rejects a non-integer `-s` (exit 1; `-s 30` works). Pass `str(int(round(interval_s)))` (and validate that `sample_interval_s` is a positive integer number of seconds at plan validation, refusing 30.5). Add a unit regression on the argv builder that kills the float mutant (assert the exact argv tuple) — the injected-sampler tests could not catch this, and that is the lesson: every argv the sampler executes gets an exact-tuple test. Also make the boot-identity read (`sysctl -n kern.bootsessionuuid`) fail soft into the sample as `boot_identity_unavailable: <reason>` rather than aborting the sample; the sample still counts as an ERROR sample for admission (never quiet) when the boot identity is unavailable, and the receipt says so.

8. **Sampler cost including the census.** The sampler smoke (`python3 -B -m joulewise.quiet_admission --sample-interval-s 30`) must report its own cost as `observer_cpu_s` measured over the whole round INCLUDING one census probe (`AGENT_CENSUS_ARGV` pgrep) as the driver's bind loop will run it; print the metrics line with `busy_cores`, `host_busy_cores`, `observer_cpu_s`, top three consumers, and the load diagnostic. You cannot run it (sandbox sysctl denial): the lead runs it natively and records the line.

9. **D7 under D-182.** Keep the successor route; align its conditions to D-182's terms exactly (zero capture = no session, no writer run, empty `runs/instrument_validation`; courier delivered = `courier.sent`; ≥ 60 s; bounded by the successor's install close; never a re-arm; every observed NO stops). The NIGHT_HANDBACK R1 sentence and the `COLD_GATE_CODES` descriptions cite D-182 by id. Fix the stale "85 minutes" at `NIGHT_HANDBACK.md:59` if you have not already.

10. **Generator invariants (Q7 NIT).** `build_spec` validates `window_max_s ≥ bind_max_s + post_bind_budget_s` AND `post_bind_budget_s ≥ 7980` computed from the schedule constants (settle 600 + 11 × 600 + 480 + `PRE_SETTLE_ALLOWANCE_S` 300), never from a literal; regression for both refusals.

## Verification you must run and paste

- `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tail -4`.
- `PYTHONPYCACHEPREFIX=/tmp/jw-compile python3 -m compileall -q scripts joulewise; echo rc=$?`.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check; echo rc=$?`.
- The argv-builder regression run against the float mutant: paste the failing assertion.
- `git diff --stat` and `git status --short` (unstaged, nothing outside WRITE_SCOPE).
- The quick tier failed for you only in `tests.test_axi_controller_events` (sandbox artefact; it passes natively on both trees); do not chase it.

## Report

claude-codex-report/v1 envelope under 8000 bytes: per item 1–10 what changed and which test proves it, the counterfactual assertion for item 7, and any early return. No commits.
