```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Register r1 then s1; consolidate desk proof, land runtime changes before qualification, and settle the G10 control before sealing.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "head_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row":"A6","action":"start_now","wait_for":"Land before qualification"},
      {"row":"E166","action":"start_now","wait_for":"Final clone pins await reviewed head"},
      {"row":"A161","action":"wait_for","wait_for":"Desk proof, executable producers, sealed registration, G10 disposition"},
      {"row":"A160","action":"wait_for","wait_for":"A161 harvest; no additional implementation milestone"},
      {"row":"Q3","action":"wait_for","wait_for":"r1 PASS and authenticated unattended block stop"},
      {"row":"A119","action":"wait_for","wait_for":"s1 immutable real telemetry"},
      {"row":"Q4","action":"do_not_start","wait_for":"L10-A, Q110, claim registration, #416, campaign authorization"}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"inspection","cmd":"git status --short --branch","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)"]},
      "expected":{"exit_code":0,"tail_regex":"^## HEAD \\(no branch\\)$"}
    },
    {
      "id":"V2","kind":"inspection","cmd":"python3 -B scripts/gen_g2_phase_d.py --check","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["PASS generated Phase D matches pinned runbook bytes"]},
      "expected":{"exit_code":0,"tail_regex":"^PASS generated Phase D matches pinned runbook bytes$"}
    },
    {
      "id":"V3","kind":"inspection","cmd":"rg -n 'rehearsal flag requires REHEARSAL_STUB|command == \"rehearse\"' scripts/run_night.py","cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["3421:                raise PackNightRefusal(\"receipt_class: rehearsal flag requires REHEARSAL_STUB\")","4393:    if args.command == \"rehearse\":"]},
      "expected":{"exit_code":0,"tail_regex":"4393:.*command == \"rehearse\""}
    }
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"blocking","text":"G10 still requires an Ed-performed forced-resync positive control; zero-owner-input qualification cannot be assumed.","needs":"Authenticate existing evidence or obtain a prospective cold ruling before seal."},
    {"id":"F2","kind":"verification_gap","level":"blocking","text":"Current G2-b chain expects manual SIGINT; pack-plan and rehearsal-record production need executable proof.","needs":"Land and review the unattended recipe and producer mapping."},
    {"id":"F3","kind":"environment","level":"nonblocking","text":"No answer destination was supplied; answer saved outside the repository at /private/tmp/joulewise-v5-next-block-consult-sol.md.","needs":""}
  ]
}
```

## Scheduling matrix

Row | action | wait_for | collision surface
--- | --- | --- | ---
A6 launch recheck | start_now | Reviewed implementation | Launcher identity; frozen source pins
E166 clone preparation | start_now | Final reviewed head | Production ledger versus isolated rehearsal
A161 rehearsal / A160 closure | wait_for | Desk proof, executable recipe, seal | Pack GO, G1–G10, separate custody
Q3 G2-b | wait_for | r1 harvested PASS | Real GAMMA pack, first ABBA block
A119 L10-A / Q110 liveness | wait_for | Real receipt bundles and s1 corpus | Scratch outputs; immutable source
Q4 transaction | do_not_start | Qualification, claim seal, #416, authorization | ALPHA → BETA → GAMMA

## Critical path

**1. The scout gets the live ordering right, but over-serializes desk work.** D-176 makes A161 precede Q3 and supplies Q110’s three receipt bundles through rehearsal, ARM-ABORT and G2-b (`docs/decision_log.md:11538–11542`). These protect pack/attempt identity, single-use launch and clock validity. G2-a discharged none of that pack-specific proof (`:11529–11532`).

Keep desk generation/replay/freeze, E166’s authenticated production ledger and disjoint rehearsal clone, the real-pack shakedown, exact finalizer refusal and per-window physics checks. E166 requires custody authentication, not just copying a ledger (`TASK_QUEUE.md:696`). #421 applies to every window (`docs/decision_log.md:12220`).

Merge Q3’s desk finalizer proof and A119 into one authenticated harvest work unit: validate/reduce once, run the scratch finalizer once, retain the L10-A proof scope and unchanged-source hashes. The required refusal is exactly `analysis_finalization_member_cover_mismatch`; floors remain empty (`docs/process/v5-l10-rehearsal-phase.md:387–423`). This protects the boundary without spending another window. Close A160 from A161’s harvest; its implementation milestone is already recorded (`TASK_QUEUE.md:810`).

Move A6 **before qualification**, ideally before terminal freeze. The scout puts a launcher change after its same-head proof; that creates avoidable requalification. A6 explicitly protects against post-arm tokenizer/model drift (`TASK_QUEUE.md:719`); current launch proceeds from consumed verification to `execve` (`scripts/launch_window.py:272–286`).

Prepare claim registration and #416 during desk intervals, rather than making them wait unnecessarily for L10-A. Finish both before claims. #416 runs once per frozen code/protocol change; calendar gaps, repeated suites without code changes, another stub rehearsal if its existing harvest satisfies acceptance, and a pre-G2-b aggregate floor add no scientific evidence (`docs/orchestration.md:117–125`; `SHAKEDOWN-G2-RUNSHEET.md:156–165`).

**2. Register (a): one qualification block, separate r1/s1 occurrences.** r1 should be the smallest authentic pack-bound lifecycle satisfying G1–G10, not another floor campaign. It reveals real pack ARM/GO/consumption, clock timing, unattended execution and backup/close-out behavior. G5 actually replays authenticated ARM and one-use consumption (`joulewise/t0_rehearsal.py:717–779`). G7 additionally tests production rejection of rehearsal authority (`docs/contracts/pack_night_go_receipt.md:1361–1384`).

s1 reveals real GAMMA telemetry flowing through bracket binding, strict validation, reduction and the expected incomplete-campaign refusal. Desk proof cannot supply these hardware bytes (`SHAKEDOWN-G2-RUNSHEET.md:28–38`). G2-a’s identical driver proves useful common machinery, but used `DIAGNOSTIC_NO_PACK` and licenses only prefill length, not phase-attribution validation (`registration_block3.md:62–69,323–334`, under `configs/campaigns/g2a_prefill_probe_25g83/`).

G2-b alone could replace r1 only through a prospective D-176 amendment preserving every distinct check; ordinary successful G2-b cannot exercise the rehearsal-purpose branch. Going straight to ALPHA also loses the real consuming contrast-path proof and conflicts with Q3’s no-promotion fence (`TASK_QUEUE.md:703`). These are different failure surfaces, not reasons to insist on separate calendar days.

**3. Before seal, fix the complete state machine.** Following block 3’s separation of validity, outcomes, custody faults and recovery (`registration_block3.md:218–296`), register:

- Exact heads and permitted head changes; pin, pack, freeze, model, workload, acceptance and chain hashes; distinct authorization purposes; roots, backups, ledger provenance and confirmation digest.
- r1’s exact minimal capture roster; s1’s exact first-stage ABBA identities; one consuming launch each; machine-enforced stop before a fifth science member; post-bracket path; finite deadlines derived from the selected prompt length, loads, admission retries, calibration and shutdown. A wall deadline is a safety cap, not the normal four-member stop.
- Mechanical qualification predicates: all G1–G10 for r1; expired, unconsumed ARM-ABORT control; four strict-valid s1 members, battery/clock/bracket acceptance, binding before one authoritative verdict, exact L10-A refusal, unchanged corpus. `physical_ahead` alone is not bracket PASS (`registration_block3.md:220–226`).
- Distinct PASS, NULL, failed-qualification and harvest-REFUSED dispositions. Archive/authentication repair reruns harvest on identical bytes; it never authorizes collection.
- **No automatic capture-bearing recovery**, especially no s2: Q3 permits one governed consuming launch and stops on unexpected results (`TASK_QUEUE.md:703`). Allow at most two pre-consumption NULL arms per occurrence after named remediation; repeated signatures or exhausted allowance go to a consult. A further consuming attempt requires a new prospective registration/ruling, never pooled or substituted members.
- END STATE: qualified evidence hands off automatically to claim prerequisites; otherwise close UNQUALIFIED, retain every attempt, identify the blocking cause and route it to the orchestrator/cold gate. No claim launches, relaxed thresholds or indefinite rearming. Unlike G2-a’s 4096 fallback, failed qualification has no scientifically honest “proceed anyway” fallback.

**4. Code and evidence before arm.** Land the authenticated four-member scheduler boundary, not a polling replacement for the second-terminal SIGINT (`scripts/gen_g2_phase_d.py:529–545`). Add a reproducible pack-plan adapter using the existing canonical writer and exact authorization/confirmation bindings; the serializer already exists (`joulewise/night_plan_writer.py:18–50`; `joulewise/night_gate.py:481–523`). The current CLI writes only new G2-a windows (`scripts/gen_g2_phase_d.py:603–622`).

Correct the scout’s command: pack-bound r1 uses `run_night.py run`. `rehearse` sets a flag expressly refused for transaction packs (`scripts/run_night.py:3420–3421,4391–4394`).

Prove the producer/harvest mapping for every rehearsal record before sealing; `rehearse_t0_unattended.py` judges an already-recorded bundle and expects nine named records, not merely a driver exit code (`:2,22–35`). G7 needs its post-harvest control step (`pack_night_go_receipt.md:1381–1384`, under `docs/contracts/`).

Resolve G10 now: its code requires Ed, forced resync and an observed RAW-anchor shift (`joulewise/t0_rehearsal.py:1187–1212`). Authenticate an existing applicable control, or prospectively rule an automated control outside captures; do not promise zero owner input while retaining an unmet Ed-only requirement. Preserve network time OFF afterward (`docs/decision_log.md:12232`).

Issuer/generators, scheduler, plan bindings, launch recheck and harvest/verdict or qualification-predicate changes all affect measurement validity and need Fable’s final pass. Records-only reconciliation does not (`docs/orchestration.md:61–65,178–184`). Existing runtime checks should be exercised, not rebuilt. Inspection passed the generator consistency check; this is not live qualification.

**5. Biggest scientific risk: transferring G2-a’s permissive environmental assumption into energy claims.** Its registration explicitly leaves background work during inference unchecked because its output is only a count-based protocol parameter (`registration_block3.md:123–130,329–334`). That rationale does not establish unbiased energy in longer production windows. I would pre-register an outcome-independent environmental diagnostic/disposition using retained power, idle/reference and clock evidence, then assess it on r1/s1 before claims. Keep unresolved bias visible; never select “quiet-looking” members after reading their energies or launch another instrument-tightening campaign.

[Saved answer](/private/tmp/joulewise-v5-next-block-consult-sol.md).