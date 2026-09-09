WRITE_SCOPE: []

# Scout brief — what stands between the live watchdog and the FIRST REAL v5 measurement window? (gpt-6-astra, read-only)

Context (verified facts, 2026-09-08 02:10 PDT): the magistrate relaunch watchdog is installed and live (headless
activation 784a764e resident); a REHEARSAL_STUB night (rehearsal-20260909, t0 2026-09-09 02:56 PDT) is being
prepared by that headless magistrate under NIGHT_HANDBACK; the paper on main is the fallback methods/diagnostic
paper (docs/paper/draft-v2-skeleton.md) because the pre-registered v5 comparison was never collected. Ed's new
standing order: work steadily with Astra to RUN THE EXPERIMENTS and finish the comparison paper, no deadline.

Your job: produce the exact, ordered, command-level runbook from "rehearsal stub succeeded" to "first real v5
window armed and collected", and the desk work that can start NOW in parallel with the rehearsal. Read:
docs/process/MAGISTRATE_WATCHDOG.md (the "first real window" paragraph), docs/process/NIGHT_HANDBACK.md,
docs/process_traces/2026-09-05-readiness/ (the readiness ruling that selected the fallback — what was missing),
docs/paper/protocol/prospective-comparison-protocol.md, configs/campaigns/d117_contrast_v5/ and the v5 floor
packs (generate_configs.py, registrations), scripts/generate_arm_readiness.py, scripts/author_arm_readiness_evidence.py,
scripts/author_arm_evidence_t0.py, scripts/prewindow_check.sh, scripts/launch_window.py, scripts/run_night.py,
scripts/install_night_agent.sh, TASK_QUEUE.md rows mentioning v5 / floor / window / T0 / NIGHT, and
docs/process/state_kernel.json tasks NIGHT-REHEARSAL-01 and its dependents. The measurement checkout of record is
/Users/edr/JouleWise-measurement-20260813 at eeb4e133 (pre-v2; do not modify anything).

Deliver (genre scout, `verdict.rows` with start_now / wait_for / needs_ruling / do_not_start): (1) the ordered
runbook with the exact commands and the artifact each produces, and which gate (D-169 stage, T-0 evidence, pack
freeze, floors-before-contrast, quiet-Mac census) each satisfies; (2) what a v2 plan must pin and where the
measurement checkout must be re-created (a fresh detached checkout of main at a named head?) and by whom (Ed-hands
items separated: sudo/powermetrics privilege, physical machine state); (3) which desk items Astra seats can start
NOW (pack generation, readiness evidence authoring dry runs, prewindow checks) without colliding with the armed
rehearsal or the live watchdog; (4) the open defects/unknowns that would refuse the first real arm, ranked;
(5) what the comparison paper needs from the first window (which figures/tables/refusal sentences in the
prospective protocol bind to which artifacts). Envelope header < 8192 bytes; file:line evidence in the body.
