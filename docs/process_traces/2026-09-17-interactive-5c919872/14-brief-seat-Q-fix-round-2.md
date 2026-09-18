SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/night_gate.py","joulewise/night_plan_writer.py","joulewise/arm_retry.py","joulewise/quiet_admission.py","scripts/run_night.py","scripts/gen_derivation_night.py","tests/test_night_gate.py","tests/test_night_plan_writer.py","tests/test_arm_retry.py","tests/test_run_night.py","tests/test_gen_derivation_night.py","tests/test_quiet_admission.py","tests/night_gate_fixtures/**","docs/process/NIGHT_HANDBACK.md","docs/phase_2/derivation_night_runbook.md","docs/contracts/night_quiet_admission.md","docs/contracts/pack_night_go_receipt.md"]
BASE_HEAD: __BASE__
BASELINE_MANIFEST: __BASELINE_MANIFEST__
BASELINE_DIGEST: __BASELINE_DIGEST__
LEASE_ID: lease-79c5a1766616453fb93e93b7cea20ffd

# Seat Q fix round 2 — refuter findings (contract lens F1–F3, execution lens below)

Branch `feat/2026-09-17-night-gate-quiet-admission` in `/Users/edr/code/JouleWise-wt-gate-quiet`, head `__BASE__` (your fix round 1 `a2671902` plus two lead bench commits: `536fd4db` widens the `top` percentage tolerance to 1.0 because `top` rounds user/sys/idle independently — live lines 100.26 and 99.98 — and `649eefd2` adds the regression that kills the strict mutant; read both with `git show`). Same rules as before: leave every change unstaged (the lead commits by pathspec), do NOT push, nothing outside WRITE_SCOPE, no `launchctl`, no `~/night-custody`, no network, no `sudo`. Do not end your turn before every item is done or a genuine early return is required.

The two refuter reports are tracked at `docs/process_traces/2026-09-17-interactive-5c919872/12-refuter-contract-astra.md` and `13-refuter-execution-astra.md` (read-only, absolute path under `/Users/edr/code/JouleWise/` if your worktree predates them). Each finding below is dispositioned by the lead; apply exactly what the disposition says.

## Contract lens

**C-F3 (BLOCKER, `scripts/run_night.py` ~:126, the write-once record set).** The `quiet_samples.jsonl` entry was added unconditionally to `_WRITE_ONCE_RECORDS`, so an existing v2 plan whose night directory happens to contain that file is refused as a rerun before its legacy evaluator runs (refuter counterexample: valid v2 plan, `quiet_admission=None`, the journal the only existing artifact → head driver exits 3 `rerun_refusal quiet_samples.jsonl`; base guard `None`). Disposition: FIX. The journal joins the write-once set for v4 plans only; the v2 record set is byte-identical to `a90ab4e8` (assert the legacy tuple equals the base tuple in a regression, and add the refuter's counterexample as a regression: a v2 plan with a pre-existing `quiet_samples.jsonl` proceeds to the legacy evaluator).

**C-F2 (SHOULD-FIX, `joulewise/night_gate.py` ~:1392).** In the v4 dynamic hard checks a FAILED boot-identity command (`sysctl -n kern.bootsessionuuid`, exit 2) is classified as `night_refused_boot_clock` ("not a canonical UUID") instead of `night_probe_error`; the other five injected probe failures already return `night_probe_error`. Disposition: FIX in the v4 path only — a non-zero exit or empty stdout from the boot probe is `night_probe_error` (terminal, never quiet); a well-formed but DIFFERENT boot id stays `night_refused_boot_clock`; the legacy v2 path is untouched (regression for all three cases, plus the assertion that the v2 evaluator's behaviour on the same injected failure is unchanged from base).

**C-F1 (SHOULD-FIX, `docs/contracts/night_quiet_admission.md`).** First-use defects: "observer cost" at line 14 before observer is defined at 124; `sample_interval_s` at 58 and "sample interval" at 68 before the definition at 78–79; `consecutive_quiet_samples` at 59 before 82–83; `bind_max_s` at 57 and "bind allocation" at 73 before "bind window" at 77; "GO" at 9 before 153; "t0" at 50 before 184. Disposition: FIX by restructuring, not by footnotes — put a short "Terms" section immediately after the opening paragraph that builds, in this order, t0, GO, the bind window and its allocation, the sample interval, consecutive quiet samples, busy-core equivalents, the observer, terminal vs WAIT, attribution, cutoff authority; then make sure no term appears above that section except in the title. Re-run the refuter's check yourself (`nl -ba` and the first occurrence of each term) and paste the line numbers of definition vs first use for all ten terms.

## Execution lens

__EXEC_FINDINGS__

## Verification you must run and paste

- `TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_night_gate tests.test_quiet_admission tests.test_night_plan_writer tests.test_arm_retry tests.test_run_night tests.test_gen_derivation_night 2>&1 | tail -4`.
- `PYTHONPYCACHEPREFIX=/tmp/jw-compile python3 -m compileall -q scripts joulewise; echo rc=$?`; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_derivation_night.py --check; echo rc=$?`.
- For C-F3 and C-F2: run each new regression against the current head with the fix reverted in a `/tmp` copy and paste the failing assertion.
- The ten-term table for C-F1.
- `git diff --stat` and `git status --short` (unstaged; nothing outside WRITE_SCOPE).

## Report

claude-codex-report/v1 envelope under 8000 bytes: per finding what changed and the test that proves it, the counterfactual assertions, the ten-term table, any early return. No commits.
