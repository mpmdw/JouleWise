# Post-merge cross-unit integration review — NIGHT-GATE-QUIET-ADMISSION-01 at main `b55909e3` (PR #358 ledger row 11, second half)

Read-only. Cwd is a detached worktree at `bookkeeping/2026-09-18-activation-d8ca3a36` (main `422cdebb`, which contains `b55909e3`). Never touch `/Users/edr/code/JouleWise` (the canonical root) or any other worktree. Do not run `[QUIET-MAC]` work. Do not write files; `/tmp` is fine for test scratch. Do not commit. Report only in the envelope.

## What "cross-unit" means here

Every earlier gate on this lane read one unit at a time (the sampler, the driver loop, the generator, the retry route) or read the diff. Your job is the seams: does each unit's OUTPUT match the next unit's INPUT contract by name, key, type, unit and timing, and is each seam covered by a test that crosses it? Range: `git diff dfc50f43..b55909e3 -- joulewise scripts tests docs/contracts docs/process/NIGHT_HANDBACK.md docs/phase_2/derivation_night_runbook.md`. Context to read first: `docs/contracts/night_quiet_admission.md` (the contract), `docs/process_traces/2026-09-17-interactive-5c919872/30-magistrate-diff-gate-13d53ce2.md` (the per-unit gate; its eight answers are claims for you to re-trace, not facts), and `docs/process_traces/2026-09-17-interactive-5c919872/29-opus-counter-review-13d53ce2.md` (S1/S2 deferred with record; lanes 235 and 236 in `docs/process/state_kernel.json`).

## Seams to trace (say "traced, no finding" per seam only after tracing, citing file:line you read)

1. Generator → plan: `scripts/gen_derivation_night.py --quiet-admission-json` → `joulewise/night_plan_writer.py` v4 mapping → `NightPlan.from_mapping` validation. Key set, integer types, the `window_max_s ≥ bind_max_s + post_bind_budget_s` and `post_bind_budget_s ≥ 7980` invariants, `cutoff_authority` non-empty, `busy_core_max` zero admits nothing. Confirm v2 output is byte-identical without the flag (run `--check` if it exists; read the path anyway).
2. Plan → driver: `scripts/run_night.py` bind loop reads exactly the sealed `quiet_admission` block; no default, no derived value, no environment override; the bind window's fixed end and every downstream deadline are functions of the plan only.
3. Driver → sampler worker: the `--observation --job-id --result-fd` worker entry in `joulewise/quiet_admission.py`; framed transport (frame size cap, partial reads, EOF, malformed frame), exec, cancel/reap; what the parent does on each failure class; the S1 uncapped `--request` payload (lane 235) is a known deferral — state whether it is reachable from a sealed plan.
4. Sampler → receipt v3: field names and units carried into `quiet_samples.jsonl`, attribution rows, `observer: true` labelling, `admission_is_capture_evidence: false`, `supervision_residue`; the journal replay seeding (lane 236) — reachable or not.
5. Refusal codes → retry route: `night_refused_bind_expired` and `night_refused_not_quiet` in `NIGHT_DRIVER_REASON_CODES`, `arm_retry.COLD_GATE_CODES`/`DISPOSITIONS`, the D-182 `zero_capture_successor_allowed` / `successor_arm_allowed` positive-evidence checks, and NIGHT_HANDBACK R1's sentence — same vocabulary end to end?
6. Census inside the bind window: the fresh census per sample, `night_refused_agent_present` terminal on any sample, the sampler's own census hit; consistency with the watchdog's census hold (`scripts/magistrate_watchdog.py`) so the two censuses cannot disagree about what counts as an agent.
7. Tests across seams: name the test that exercises each seam 1–6 end to end (generator output fed to the driver, driver fed by a real worker over a real pipe, receipt read back by the retry route). A seam with only unit tests on both sides is a finding.
8. CI: `gh run list --branch main --limit 5 --json headSha,conclusion` and `gh run view` for the run on `b55909e3` (or the first main run containing it); report the conclusion and any failed job by name. Do not re-run CI.

## Severity

BLOCKER: a seam where a value changes meaning, unit or name between units, or a sealed-plan input can be bypassed, or a refusal code is dropped or reclassified on the way to the retry route. SHOULD-FIX: a seam without a crossing test; a documented behaviour the code does not implement. NIT: everything else. For every finding give the counterfactual input and the production call site. Keep the report under 8000 bytes.
