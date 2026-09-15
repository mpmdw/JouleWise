# Seat brief — record cold gate 25 Q5 (kernel acceptance text) and register RUNBOOK-S3-FAIL-ROUTE-CROSSREF-01 (Q6)

SESSION_MODE: delegated
WRITE_SCOPE: ["docs/process/state_kernel.json","tests/test_gen_state.py","TASK_QUEUE.md","RUN_STATE.md"]

Worktree `/Users/edr/code/JouleWise-wt-lanes-d6888966`, branch `chore/2026-09-15-lanes-d6888966` at origin/main (cite `git rev-parse --short HEAD`). Do NOT commit. Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`. No network. `RUN_STATE.md`/`TASK_QUEUE.md` change ONLY inside the generator-owned fences via `python3 scripts/gen_state.py`.

Authority for both tasks: cold gate 25 ruling 10 + Opus pairing 12 + magistrate synthesis 13, `docs/process_traces/2026-09-15-activation-d6888966/25-coldgate-packet-install-windows/` (read 10 §Q5 and §Q6, and 13). These are recordings of a ruling, not rulings.

## Task 1 — INSTALL-WINDOWS-MULTI-01 acceptance text (ruling 10 Q5, verbatim)
In `docs/process/state_kernel.json` task `INSTALL-WINDOWS-MULTI-01`, `acceptance.summary`: replace the phrase "the plan's t0 may be any clock time (launchd hour/minute derived from the plan, not a fixed belt)" with "the plan's t0 may be any clock time launchd can name: any whole minute (`t0_epoch_s % 60 == 0`) whose local wall-clock reading occurs exactly once (refusals `plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time`); launchd Month/Day/Hour/Minute derived from the plan, not a fixed belt"; and replace "the any-clock-time t0" with "the whole-minute unambiguous t0 (both refusals, an ordinary control, and a spring-gap control)". If either phrase is not present verbatim, STOP with NEEDS_RULING quoting the actual text (do not approximate). The `goal` sentence's "at any clock time" stays (Ed's words). Append to `status_note`: " 2026-09-15 (activation d6888966, cold gate 25 Q5): acceptance clause (c) narrowed to the whole-minute unambiguous t0 (FIX-5 affirmed); blocker at int head df86cee6 under fix round 2 per ruling 10 Q1(c)/Q3-as-amended."

## Task 2 — register RUNBOOK-S3-FAIL-ROUTE-CROSSREF-01 (rank 202, lane `ed_external`, status `queued`, priority `p3_hardening_candidates`)
Shape as the rows registered today (`git show 6773df23 -- docs/process/state_kernel.json tests/test_gen_state.py`). Row count 175 + 1 = 176.
Goal: `docs/phase_2/derivation_night_runbook.md` §3 item 3 (lines ~2085–2086, byte-identical, SHA-256 71337a836df21f1f3668bcb46e7ffe6e487a247f7ce51368b459b9516612072b) carries the pre-registered "three FAIL-route windows on distinct calendar days" constraint (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:143`); with INSTALL-WINDOWS-MULTI-01 the machinery can install several plans per day, so the item needs a cross-reference saying that capability does not apply to those three windows — an Ed-visible docs edit to a registration-carrying section, kept OUT of the INSTALL-WINDOWS diff by cold gate 25 (Opus amendment to Q6).
Acceptance summary: Ed sees and approves (or declines) the replacement text for §3 item 3 exactly as ruling 10 Q6 gives it: "**Distinct calendar days.** The registration (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:143`) requires the three FAIL-route windows to fall on distinct calendar days. D-181 cl.1 and `INSTALL_SPANS` let the machinery install and arm several plans on one day; that capability does not apply to these three windows. A same-day FAIL-route successor is refused by this step, not by the installer, unless Ed amends the registration before the first FAIL-route capture."; the registration file itself is untouched; docs-only PR; not night-critical.
Evidence: `docs/process_traces/2026-09-15-activation-d6888966/25-coldgate-packet-install-windows/10-coldgate-fable-ruling.md` (Q6); `12-opus-pairing-refuter-on-ruling-10.md` (Q6 amendment); `13-magistrate-synthesis-ruling-10-with-opus-amendments.md`.
Authority label: cold gate 25 ruling 10 Q6 as amended by pairing 12, synthesis 13 (magistrate registration).

## Verification to paste
`python3 scripts/gen_state.py && python3 scripts/gen_state.py --check; echo rc=$?`; `python3 -m unittest tests.test_gen_state 2>&1 | tail -3`; `git status --short`; `git diff --stat`.

## Report
claude-codex-report/v1 envelope: changed files, the rank, tails, the exact before/after of the two replaced phrases; NEEDS_RULING on any mismatch.
