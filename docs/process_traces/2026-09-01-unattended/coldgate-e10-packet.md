# COLD GATE PACKET — does E-10 bind a pack-less diagnostic night? (D-169 stage 1, ruling R-10)

You are a cold adjudicator: no loop context, no sunk cost. Rule on the packet
only. Read-only: do not edit any file. All paths are under
`/Users/edr/code/JouleWise` (main; the ruling file is uncommitted there).

## The question

Ruling R-10 in
`docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(§2 R-10 and its "Honesty clause") holds that runbook step E-10 ("Ed
personally invokes the sole reviewed launcher exactly once",
`docs/phase_2/window_runbook.md:1243-1244`) binds only pack-bound
claim-bearing windows, and therefore does NOT bind a `DIAGNOSTIC_NO_PACK`
night (G2-a / G2-b), so stage 1 may run its first unattended night without
an Ed-ratified E-10 amendment.

That narrows a fence on kernel row `UNATTENDED-LAUNCH-01`
(`docs/process/state_kernel.json`, `/tasks/UNATTENDED-LAUNCH-01/fences/0`):
"E-10 amendment is Ed-ratified before any automated launch", authored by
`docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`.

## Evidence to open (all of it)

1. `docs/phase_2/window_runbook.md:800-830` and `:1225-1270` — E-10 in
   context (arm receipt verify with `--pack-root`, step-6 table).
2. `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:225-300`
   — G2-a is diagnostic, pack-less, "no G2-a gate may test `$PACK_ROOT`".
3. `docs/decision_log.md` index rows D-127, D-149, D-167, D-169 (grep
   `^| D-1(27|49|67|69) `), and the D-167 section body (grep `^## D-167`).
   Note D-167 cl.1: readiness evidence for a `_v5` window is G1/G2/G3 "plus
   Ed's authorization (08-28: diagnostic windows at lead discretion; the
   transaction on Ed's go)".
4. `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`
   — the fence's authoring ruling: what did "any automated launch" mean
   there; was a pack-less window in view at all?
5. Ed's words that started this lane (verbatim, 2026-09-01): "why are quiet
   windows still gated by me? why can't you do this? i'm tired of having to
   be at the machine" … "bad. that should be done first. so you can drive
   the experiments entirely."

## Rule on

(a) Does E-10, as written, bind a pack-less diagnostic night? Cite the text
    that decides it.
(b) Is R-10 a permissible narrowing, or a reversal that only Ed can make?
(c) If R-10 stands, name the minimal kernel-row rewording for the fence.
(d) Anything in the stage-1 ruling (§2 R-1..R-12) that you would REFUSE to
    let run a live night — with the cite. Be specific; "looks fine" is not a
    verdict.

Output ≤ 90 lines: VERDICT (UPHELD / UPHELD-WITH-AMENDMENT / REVERSED) on
(a)-(c), then (d) as a numbered list, then one line of confidence.
