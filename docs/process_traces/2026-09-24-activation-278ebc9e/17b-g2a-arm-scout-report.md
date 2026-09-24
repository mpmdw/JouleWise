```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "G2-a has a supported v2 diagnostic arm path, but the tracked 25G83 acceptance dependency and fresh arm gates prevent a defensible arm today.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "21d045ad60aa926756e45c542cf6491dd143c472",
    "head_end": "21d045ad60aa926756e45c542cf6491dd143c472",
    "upstream_end": null,
    "branch": "HEAD"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "G2-a tooling", "action": "start_now", "reason": "Prepare the existing DIAGNOSTIC_NO_PACK v2 path at the desk."},
      {"row": "25G83 acceptance conflict", "action": "needs_ruling", "reason": "Q2 says READY while its arm lane retains an unsatisfied hard dependency."},
      {"row": "Live pins and machine", "action": "wait_for", "reason": "Authenticate ledger, clone, models, privilege, supervisor and quiet state."},
      {"row": "Cold ARM pass", "action": "wait_for", "reason": "Fresh Fable verdict must cover the exact staged plan."},
      {"row": "KM003C rider", "action": "do_not_start", "reason": "No ready whole-window logger or dry census proof; move it to night 2."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B scripts/gen_g2_phase_d.py --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["PASS generated Phase D matches pinned runbook bytes"]},
      "expected": {"exit_code": 0, "tail_regex": "PASS generated Phase D matches pinned runbook bytes"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Q2 is READY, but A159 is blocked on A179; active r7 acceptance names os_build 25F84, not 25G83. COUNCIL-407-01 did not expressly waive epoch acceptance.",
      "needs": "Reconcile the hard dependency against the council's G2-a-first order before selecting a real t0."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "This read-only scout did not inspect live custody, the canonical supervisor, model bytes, sudo authorization, or machine quietness.",
      "needs": "Magistrate performs the governed live checks."
    }
  ]
}
```

## Q1 — Arm path and present answer

**The code can express a G2-a arm, but the current records do not support arming it today.** Use a `DIAGNOSTIC_NO_PACK` **v2** plan with `measurement_root`, `measurement_head`, the generated G2-a chain and its SHA-256 sidecar. The plan is serialized by `joulewise.night_plan_writer.write_night_plan`; the installed driver derives the chain’s checkout and interpreter from that plan. This is the documented G2-a route ([plan draft:27–46](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/README.md:27), [handback:1231–1254](/Users/edr/code/wt-278ebc9e-g2a/docs/process/NIGHT_HANDBACK.md:1231), [handback:1272–1284](/Users/edr/code/wt-278ebc9e-g2a/docs/process/NIGHT_HANDBACK.md:1272)). `python -m joulewise.evidence_night prepare` is **not** its entry point: `prepare` refuses every kind except its hardcoded `quiet_predicate_evidence` ([evidence_night.py:28](/Users/edr/code/wt-278ebc9e-g2a/joulewise/evidence_night.py:28), [evidence_night.py:371–375](/Users/edr/code/wt-278ebc9e-g2a/joulewise/evidence_night.py:371)).

The applicable handback sequence is:

1. **Ready in code; live proof needed:** settle the reviewed head and fresh plan ID, custody root, t0 and window budget; authenticate the clone, ledger and models; build, bind and check all probe inputs ([G2-a procedure:83–123](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/README.md:83)).
2. **Ready in code:** render the G2-a chain, syntax-check it, write the canonical v2 plan **to staging**, and render and inspect both job files ([procedure:125–190](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/README.md:125)). The generator’s read-only `--check` passed here.
3. **Needs a fresh cold verdict and live checks:** obtain Fable’s **ARM** verdict on those exact staged bytes; run governed preflight and arm census. The relaunch instruction requires a cold Fable final pass **before any arm** ([relaunch prompt:21](/Users/edr/code/wt-278ebc9e-g2a/docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:21)).
4. **Needs magistrate; Ed retains veto:** send the plan notice, check for NO, publish the staged plan, install both night jobs, verify installation, then **exit before REQUEST** ([procedure:195–220](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/README.md:195); current timing is install strictly before t0−600 s and exit by t0−480 s, [handback:775–782](/Users/edr/code/wt-278ebc9e-g2a/docs/process/NIGHT_HANDBACK.md:775)). Ed is needed for hardware or missing sudo authorization, not a routine per-window GO ([D-149](/Users/edr/code/wt-278ebc9e-g2a/docs/decision_log.md:191), [D-183](/Users/edr/code/wt-278ebc9e-g2a/docs/decision_log.md:229)).

The G2-a producer exists: `build-probes` emits four-rung configs and manifests; `bind-window` binds the ledger and acceptance; `check` replays the bindings ([generate_g2a_probe_inputs.py:1–7](/Users/edr/code/wt-278ebc9e-g2a/scripts/generate_g2a_probe_inputs.py:1), [generate_g2a_probe_inputs.py:1297–1324](/Users/edr/code/wt-278ebc9e-g2a/scripts/generate_g2a_probe_inputs.py:1297)). The “no code builds configs” statement in [v5-artifact-flow.md:28](/Users/edr/code/wt-278ebc9e-g2a/docs/process/v5-artifact-flow.md:28) is stale.

## Q2 — Blockers

| Blocker | Evidence | Owner | Size |
|---|---|---|---|
| **Epoch acceptance conflict — hard stop.** Q2 is marked READY, while `G2A-FIRST-WINDOW-01` explicitly waits for `ACCEPTANCE-EPOCH-25G83-01` and rehearsal harvest. The active r7 artifact’s `identity_epoch.os_build` is **25F84**; G2-a’s binder uses that active artifact and derives the live epoch. The council verified Q2’s READY claim only as the magistrate’s representation. | [TASK_QUEUE.md:702](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:702), [TASK_QUEUE.md:1064](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:1064), [calibration_bracketing.py:198–199](/Users/edr/code/wt-278ebc9e-g2a/joulewise/calibration_bracketing.py:198), [generate_g2a_probe_inputs.py:638–674](/Users/edr/code/wt-278ebc9e-g2a/scripts/generate_g2a_probe_inputs.py:638), [r7 acceptance](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json), [council ruling:7](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:7) | **Ruling**, then agent/quiet machine if dependency stands | Potentially multiple calendar days |
| If the successor-acceptance route stands, A179’s gate calls for governed corpus work and a fresh-clone `bind-window`/preflight. A separate queue row says **“No registration night may be armed”** until Ed answers which earlier nights count. | [TASK_QUEUE.md:1075](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:1075), [TASK_QUEUE.md:700](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:700), [D-102 corpus schedule:6632–6649](/Users/edr/code/wt-278ebc9e-g2a/docs/decision_log.md:6632) | Ed ruling, agent preparation, quiet machine collection | Days, if required |
| The old A88 rehearsal row remains ACTIVE in the queue, although its detailed state says all six items acquired evidence by 2026-09-12. Reconcile that bookkeeping against actual harvest and current discovery before treating it as an outstanding rehearsal. | [TASK_QUEUE.md:770](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:770), [state_kernel.json:5003](/Users/edr/code/wt-278ebc9e-g2a/docs/process/state_kernel.json:5003) | Agent | 15–30 min if only reconciliation |
| Fresh clone, authenticated ledger/head pin, model revisions and exact environment are unproved by this scout. The prior G2-a draft records these as outstanding; `bind-window` authenticates the ledger and acceptance before issuing the frozen plan. | [draft:224–233](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/README.md:224), [generate_g2a_probe_inputs.py:921–949](/Users/edr/code/wt-278ebc9e-g2a/scripts/generate_g2a_probe_inputs.py:921) | Agent; Ed only for missing hardware/sudo | 45–120 min if bytes and custody are available |
| Fresh cold Fable ARM verdict on the staged plan, notice/NO check, census, power/thermal/clock gates, and supervisor freshness remain perishable. D-183 allows the magistrate to fast-forward a clean canonical checkout when unloaded, then **exit for a fresh supervisor** if the resident one imported stale code. | [relaunch prompt:10–13,21](/Users/edr/code/wt-278ebc9e-g2a/docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:10), [handback:667–709](/Users/edr/code/wt-278ebc9e-g2a/docs/process/NIGHT_HANDBACK.md:667), [handback:775–782](/Users/edr/code/wt-278ebc9e-g2a/docs/process/NIGHT_HANDBACK.md:775) | Agent; Ed’s NO/hardware/sudo only | 30–75 min plus any restart |
| The KM003C rider has no ready whole-window logger or demonstrated census-safe arm. | [ruling:50–54](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:50), [archived probe:103–142](/Users/edr/night-archive/km003c-tools-20260923/km003c_probe.py:103) | Agent code + Ed hardware or Ed-installed job | 1–3 h and a live dry-check; **not a G2-a blocker** |

**Non-blockers:** The four rungs and count rule are already registered; G2-a collects their selector input, and the actual rung is selected **after** G2-a. The three `_v5` pack hashes, pack freeze and pack ARM receipt likewise follow G2-a ([D-166](/Users/edr/code/wt-278ebc9e-g2a/docs/decision_log.md:212), [TASK_QUEUE.md:1004](/Users/edr/code/wt-278ebc9e-g2a/TASK_QUEUE.md:1004), [G2-a arm draft:239–241](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-08-handoff-redo/99cd-g2a-first-window-plan/README.md:239)). The current D-166 registration file hashes to the gate’s expected `dfe55f8d…c1ac265` ([night_gate.py:45–54](/Users/edr/code/wt-278ebc9e-g2a/joulewise/night_gate.py:45)); its exact digest was reproduced read-only.

**Equivalence distinction:** COUNCIL-407-01 says the proposed M1 equivalence-rule replacement and D-102 *calibration-corpus equivalence rule* do **not directly gate G2-a admission**; the night gate does not invoke that rule ([ruling:50–54](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:50)). That finding does **not** authenticate a 25G83 calibration acceptance or erase A159’s explicit hard dependency. This is the decision the magistrate must reconcile, rather than silently using the 25F84 r7 pin.

## Q3 — Shortest supported path

1. **0–30 agent minutes:** Resolve the A159/A179 versus Q2/COUNCIL-407-01 conflict in a recorded ruling. If the 25G83 acceptance remains required, satisfy its Ed registration-night-count decision and governed acceptance route first. **Quiet machine:** any required corpus nights.
2. **20–40 agent minutes:** Reconcile the already-evidenced rehearsal row; inventory retained plans/jobs and choose a fresh identity, root, reviewed head and sufficient window budget. **Quiet machine:** no.
3. **45–120 agent minutes:** Create and authenticate the frozen clone and venv; verify model bytes, ledger/head pin, live acceptance and privilege; run `build-probes → bind-window → check`; render and syntax-check the chain and stage the v2 plan. **Quiet machine:** no; Ed only for hardware or missing sudo authorization.
4. **20–45 agent minutes:** Render both jobs, run governed dry checks, obtain cold Fable **ARM** on the exact staged candidate, and check canonical/resident-supervisor freshness. If D-183 requires a fresh supervisor, allow its relaunch and repeat perishable checks. **Quiet machine:** census-clean bench conditions.
5. **10–20 agent minutes:** Send notice, observe veto, publish and install before t0−10 min, verify both jobs, and exit before t0−8 min. **Quiet machine:** no agent at the acquisition boundary.

**Earliest t0:** There is **no defensible 2026-09-24 t0 on the present acceptance record**. The 24-hour install span permits day or night ([run_night.py:92–100](/Users/edr/code/wt-278ebc9e-g2a/scripts/run_night.py:92)); quiet means a clean machine. At 05:40, the evidence CLI’s 40-minute planning default would suggest **06:20** only as arithmetic, not as an arm authorization ([handback:711–714](/Users/edr/code/wt-278ebc9e-g2a/docs/process/NIGHT_HANDBACK.md:711)). If the existing acceptance dependency is retained and a new three-distinct-day corpus starts today, its calendar floor reaches **September 26**, with G2-a only after issuance, pinning and another arm ceremony. The Ed counting decision and actual retained corpus make even that date conditional.

## Q4 — KM003C rider

The driver already launches one digest-checked zsh chain under its exclusive window; that chain is a possible **payload location**, but there is no meter-specific hook in the generated G2-a chain ([run_night.py:3160–3209](/Users/edr/code/wt-278ebc9e-g2a/scripts/run_night.py:3160), [gen_g2_phase_d.py:118–146](/Users/edr/code/wt-278ebc9e-g2a/scripts/gen_g2_phase_d.py:118)). The archived `km003c_probe.py` reads a fixed number of samples and prints diagnostic text, so it is **not yet** a passive CSV logger for the whole window ([archived probe:103–142](/Users/edr/night-archive/km003c-tools-20260923/km003c_probe.py:103)).

The smallest compliant chain rider would be a pinned, passive reader started and stopped by the generated chain, writing timestamped meter samples to separate diagnostic custody for the **entire** window, without altering probe configs, rung order, schedule, gate or refusal behavior. It would need a desk run with the reader active that passes **both** censuses. The alternative is an **Ed-installed** independent launchd job with the same whole-window logging and dry-check. A Codex or Claude child process is expressly excluded ([ruling:54](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:54)).

**Recommendation: run G2-a without the rider and put it in night 2.** That is explicitly allowed by the ruling, preserves the registered first-night chain, and lets the calibration night register the meter’s alignment, battery accounting and reader overhead together ([ruling:18–24](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md:18)).

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Acceptance reconciliation | `needs_ruling` | A159 versus Q2 and council order | A real G2-a t0 |
| G2-a desk preparation | `start_now` after ruling on its inputs | Authenticated acceptance and ledger | Frozen clone/plan identity |
| Cold ARM and install | `wait_for` | Exact staged plan, machine checks, fresh supervisor | Night agents and census |
| KM003C night-1 rider | `do_not_start` | Whole-window logger and dual-census dry pass | Registered chain and machine load |

## Critical path

Acceptance reconciliation → authenticated clone, ledger and probe inputs → staged v2 plan → cold Fable ARM and live checks → notice/veto → publication and two-job installation → **magistrate exited before REQUEST**. No files were modified and no live night or machine-state measurement was started.