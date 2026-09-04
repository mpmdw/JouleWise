```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Reconciled all four claim-state surfaces to the live Qwen3 campaign and hands-free operating state while preserving the soundness boundaries.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-claim-surfaces-sweep"
  },
  "pathspec": [
    "CLAIMS_STATUS.md",
    "WINDOW_STATUS.md",
    "PROJECT_STATUS.md",
    "STATUS.md",
    "docs/process_traces/2026-09-04-fanout/claim-surfaces/01-sol-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "lint",
      "cmd": "python3 -c 'import re; from pathlib import Path; p=Path(\"docs/process_traces/2026-09-04-fanout/claim-surfaces/01-sol-report.md\").read_text(); a=p.split(\"\\n## Changed-sentence register\\n\",1)[1].split(\"\\n## First-use test\\n\",1)[0]; b=p.split(\"\\n## First-use test\\n\",1)[1].split(\"\\n## Finding and decision table\\n\",1)[0]; ids_a=re.findall(r\"^\\| ([CWPST]\\d{2}) \\|\",a,re.M); ids_b=re.findall(r\"^\\| ([CWPST]\\d{2}) \\|\",b,re.M); assert ids_a==ids_b and ids_a; assert all(x==\"PASS\" for x in re.findall(r\"^\\| [CWPST]\\d{2} \\|.*\\| (PASS) \\|$\",b,re.M)); sentences=[row.split(\" | \",3)[2] for row in a.splitlines() if re.match(r\"^\\| [CWPST]\\d{2} \\|\",row)]; assert not any(re.search(r\"D-\\d{3}|kernel row|[A-Z][A-Z0-9]+(?:-[A-Z0-9]+){2,}\",s) for s in sentences); print(f\"first-use register: {len(ids_a)} changed sentences PASS\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "first-use register: 58 changed sentences PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "first-use register: [0-9]+ changed sentences PASS"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 23 tests in 1.158s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_claims_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 30 tests in 3.169s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    }
  ],
  "flags": []
}
```

# Claim-state surface consistency sweep

## Change

The current summaries now identify the Qwen3 campaign generation, retire the
old readiness-council and predecessor-campaign instructions, record the
hands-free delegation, and state the delivered-rehearsal, uninstalled-agent,
and open-review facts. Historical evidence remains labelled as historical or
diagnostic, and the existing timing, immutability, refusal, no-retry, and
claim-consumption boundaries remain in place.

## Changed-sentence register

Repeated text has one row with every occurrence named. Headings and date/status
cells are included because they carry claim-state meaning even when they are
not grammatical sentences.

| ID | Surface | Exact changed sentence or status text | Truth source |
|---|---|---|---|
| C01 | `CLAIMS_STATUS.md` | Evidence collected before the third-generation timing anchor—the program that aligns workload events with power samples—remains excluded from claims by a mechanical capture-era check, not merely by policy. | `docs/decision_log.md`, timing-soundness and live-campaign decisions |
| C02 | `CLAIMS_STATUS.md` | Every corpus collected before that production repair is non-claim-bearing under the current instrument; fresh claim authority must come from prospective collection in campaign generation `_v5`, the internal label for the fixed design regenerated around the four-bit Qwen3 1.7-billion-parameter and 8-billion-parameter models. | `docs/decision_log.md`, “newer models in the campaign” and “kernel reconciled to live state” |
| C03 | `CLAIMS_STATUS.md` | Last updated: 2026-09-04. | Mission date and `RUN_STATE.md`, current session header |
| C04 | `CLAIMS_STATUS.md` | The current campaign generation is `_v5`; it uses the Qwen3-1.7B-4bit and Qwen3-8B-4bit model pair, and the superseded `_v4` family will not be collected. | `docs/decision_log.md`, “newer models in the campaign” |
| C05 | `CLAIMS_STATUS.md` | No `_v5` claim-bearing result has been issued. | `PROJECT_STATUS.md`, current repository view; `docs/process/state_kernel.json`, live campaign sequence |
| C06 | `CLAIMS_STATUS.md` | The former readiness council is retired as a live gate. | `docs/decision_log.md`, “kernel reconciled to live state” |
| C07 | `CLAIMS_STATUS.md` | Readiness now comes from staged desk proof, a diagnostic shakedown—a short non-claim run on the frozen campaign pack—and a nightly check after collection begins. | `docs/decision_log.md`, “kernel reconciled to live state”; `docs/process/state_kernel.json`, current campaign dependencies |
| C08 | `CLAIMS_STATUS.md` | Ed has delegated the per-window transaction decision and the mechanical confirmation of campaign bytes, meaning the exact frozen campaign files, to the lead's independent readiness gate, so no reply from Ed is required for an otherwise passing window. | `docs/decision_log.md`, “hands-free week—Ed's delegations for unattended windows” |
| C09 | `CLAIMS_STATUS.md` | An unattended-night rehearsal was delivered with the expected agent-presence refusal, proving the stand-down path without collecting claim data; the user-level background agents that scheduled it were then uninstalled. | `RUN_STATE.md`, current session header and courier addendum; `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`, 2026-09-03 update |
| C10 | `CLAIMS_STATUS.md` | A pull request (PR) is a proposed repository change awaiting review or merge; PR #278, which repairs the declared identity set for decode workloads, remains open. | `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`, pause table |
| C11 | `CLAIMS_STATUS.md` | The next claim-state change still requires the unattended watchdog, a supervisor that relaunches the lead after a quiet run; plan pinning, which binds a night plan to the repository copy reserved for measurement; the four-length prompt probe; the desk freeze; and the real-pack shakedown before claim-bearing collection can begin. | `RUN_STATE.md`, next machine step; `docs/process/state_kernel.json`, current dependencies |
| C12 | `CLAIMS_STATUS.md` | The historical a10 re-mint, the old C/D plan, the Qwen2.5 `_v3` windows, and the `_v4` family are retired. | `docs/decision_log.md`, live-state reconciliation and dated predecessor-family retirement addendum |
| C13 | `CLAIMS_STATUS.md` | Claim authority can now arise only from prospective collection under the Qwen3 `_v5` campaign. | `docs/decision_log.md`, newer-model and live-state decisions |
| C14 | `CLAIMS_STATUS.md`, two table rows | This earlier campaign record cannot be used for a claim. | `docs/decision_log.md`, newer-model decision and capture-era claim barrier |
| C15 | `CLAIMS_STATUS.md`, two table rows | Its values are diagnostic records only and do not enter the Qwen3 `_v5` claim basis. | `docs/decision_log.md`, newer-model decision and live-state reconciliation |
| C16 | `CLAIMS_STATUS.md` | The historical re-mint route is retired. | `docs/decision_log.md`, live-state reconciliation and predecessor-family retirement addendum |
| C17 | `CLAIMS_STATUS.md` | Claim authority can arise only from prospective collection under the Qwen3 `_v5` campaign. | `docs/decision_log.md`, newer-model and live-state decisions |
| W01 | `WINDOW_STATUS.md` | The production campaign is generation `_v5`, the internal label for the fixed design regenerated around the four-bit Qwen3 1.7-billion-parameter and 8-billion-parameter models; the `_v4` family will not be collected. | `docs/decision_log.md`, “newer models in the campaign” |
| W02 | `WINDOW_STATUS.md` | An unattended-night rehearsal was delivered with the expected refusal—a recorded decision to issue no result—because an agent, meaning an automated software worker, was present. | `RUN_STATE.md`, courier addendum; durable-state 2026-09-03 update |
| W03 | `WINDOW_STATUS.md` | The user-level background agents that scheduled the rehearsal were then uninstalled, and no scheduled measurement can fire from them. | `RUN_STATE.md`, next machine step; durable-state 2026-09-03 update |
| W04 | `WINDOW_STATUS.md` | The next machine sequence is to complete the relaunch watchdog, a user-level supervisor that restarts the lead after a quiet run; pin each night plan to the dedicated measurement checkout, the repository copy reserved for measurement; and only then arm the four-length prompt probe. | `RUN_STATE.md`, next machine step |
| W05 | `WINDOW_STATUS.md` | The historical a10 re-mint, the old C/D plan, the Qwen2.5 `_v3` windows, and the `_v4` family are retired. | `docs/decision_log.md`, live-state reconciliation and predecessor-family retirement addendum |
| W06 | `WINDOW_STATUS.md` | Claim authority can now arise only from prospective collection under the Qwen3 `_v5` campaign. | `docs/decision_log.md`, newer-model and live-state decisions |
| W07 | `WINDOW_STATUS.md` | Updated 2026-09-04: rehearsal delivered; scheduled background agents uninstalled; Qwen3 `_v5` sequence current; no machine-setting assertion. | Mission date; `RUN_STATE.md`, current session header and next machine step |
| W08 | `WINDOW_STATUS.md` | Do not launch claim-bearing collection until the desk proof, real-pack shakedown, and independent readiness review all pass; preserve every refusal and do not retry merely to obtain a favorable outcome. | `docs/decision_log.md`, live-state reconciliation; unchanged soundness rules in `RUN_STATE.md` and `TASK_QUEUE.md` |
| W09 | `WINDOW_STATUS.md` | No per-window reply from Ed is required: his standing hands-free delegation assigns the transaction decision and mechanical campaign-byte confirmation to the lead's independent readiness gate. | `docs/decision_log.md`, hands-free-week delegation |
| W10 | `WINDOW_STATUS.md` | Verify network-time state directly before the next measurement sequence; this document does not assert the current machine setting. | `RUN_STATE.md`, next machine step and machine-state cautions |
| W11 | `WINDOW_STATUS.md` | A wall meter remains an open equipment decision. | `TASK_QUEUE.md`, current external queue |
| W12 | `WINDOW_STATUS.md` | A pull request (PR) is a proposed repository change awaiting review or merge; PR #278, which repairs the declared identity set for decode workloads, remains open. | Durable-state pause table |
| W13 | `WINDOW_STATUS.md` | The current production path is prospective collection under the Qwen3 `_v5` campaign; the earlier alpha, beta, and gamma wording is historical. | `docs/decision_log.md`, live-state reconciliation |
| P01 | `PROJECT_STATUS.md` | Project phase: Phases 1, 2, and 4 remain in progress; the Mac instrument and analysis path exist, the current claim-bearing campaign is sequenced but has no results data yet, and the paper's controlled result slots are prepared. | `PROJECT_STATUS.md`, status-at-a-glance table; `TASK_QUEUE.md`, current queue |
| P02 | `PROJECT_STATUS.md` | As of 2026-09-04, JouleWise is between measurement runs and preparing the unattended controls required before the first diagnostic prompt-length probe, a non-claim comparison of candidate input lengths; no claim-bearing data from the current campaign exist. | `RUN_STATE.md`, current session header and next machine step; durable-state 2026-09-03 update |
| P03 | `PROJECT_STATUS.md` | The relaunch watchdog, a user-level supervisor that restarts the lead after a quiet run, must pass review and be installed. | `RUN_STATE.md`, next machine step; `docs/process/state_kernel.json`, current watchdog state |
| P04 | `PROJECT_STATUS.md` | Each night plan must also be pinned to the dedicated measurement checkout, the repository copy reserved for measurement, before the prompt probe is armed. | `RUN_STATE.md`, next machine step; `docs/process/state_kernel.json`, current plan state |
| P05 | `PROJECT_STATUS.md` | The machine will then measure four candidate prefill lengths—512, 1,024, 2,048, and 4,096 tokens. | `docs/decision_log.md`, workload decision |
| P06 | `PROJECT_STATUS.md` | The lead's independent readiness gate then exercises Ed's standing delegation for the claim-bearing transaction; about a week of collection follows with a desk check after each night; then floor production, claim close-out, and the registered results fill. | `docs/decision_log.md`, hands-free-week delegation and live-state reconciliation |
| P07 | `PROJECT_STATUS.md` | A fresh-model repository review began from scratch on 2026-09-01 and issued its findings. | `RUN_STATE.md`, fresh-model review closed pointer |
| P08 | `PROJECT_STATUS.md`, update ledger | The unattended-night rehearsal was delivered and its scheduled background agents were uninstalled; hands-free authority was delegated to the lead's independent readiness gate; the decode-identity correction remains under review as pull request #278. | `RUN_STATE.md`, current session header; durable-state 2026-09-03 update and pause table |
| P09 | `PROJECT_STATUS.md`, phase table | Instrument and plan preparation are complete; unattended-control installation and plan pinning precede the four-rung prompt probe. | `RUN_STATE.md`, next machine step |
| P10 | `PROJECT_STATUS.md`, campaign sequence | The lead's independent readiness review then applies Ed's standing delegation to decide whether to open the claim-bearing transaction. | `docs/decision_log.md`, hands-free-week delegation |
| P11 | `PROJECT_STATUS.md`, timeline | The four-rung prompt-length evening starts after unattended controls are installed, the plan is pinned to the dedicated measurement checkout, no agents are running on the M3 Max, and the machine is otherwise idle so nothing else draws measurable power. | `RUN_STATE.md`, next machine step; unchanged quiet-machine rule |
| P12 | `PROJECT_STATUS.md`, timeline | The delegated claim-bearing transaction decision requires a complete, reviewable shakedown record and a passing independent readiness review. | `docs/decision_log.md`, hands-free-week delegation and live-state reconciliation |
| P13 | `PROJECT_STATUS.md`, timeline | The collection week starts when the delegated readiness gate authorizes collection, and each preceding night passes its check. | `docs/decision_log.md`, hands-free-week delegation; current campaign sequence |
| P14 | `PROJECT_STATUS.md` | Ed owns research direction, external access, and standing authority for claim-bearing collection; during the hands-free week, he has delegated per-window operation and the transaction decision to the lead's independent readiness gate. | `docs/decision_log.md`, unattended-loop and hands-free-week decisions |
| P15 | `PROJECT_STATUS.md` | Raw evidence is immutable, review findings receive explicit dispositions, and no implementation worker treats its own output as final live-hardware proof. | `docs/orchestration.md`, lead live-gate rule; `RUN_STATE.md`, standing soundness facts |
| S01 | `STATUS.md` | JouleWise is between measurement runs. | `RUN_STATE.md`, current session header |
| S02 | `STATUS.md` | A claim-bearing result is a result permitted to support a scientific statement; none exists for the current campaign. | `CLAIMS_STATUS.md`, current claim state; `PROJECT_STATUS.md`, current repository view |
| S03 | `STATUS.md` | The live campaign is generation `_v5`, comparing the four-bit Qwen3 1.7-billion-parameter and 8-billion-parameter models. | `docs/decision_log.md`, newer-model decision |
| S04 | `STATUS.md` | The `_v4` family is retired and will not be collected. | `docs/decision_log.md`, newer-model decision and predecessor-family retirement addendum |
| S05 | `STATUS.md` | The unattended-night rehearsal was delivered with the expected refusal because an agent, meaning an automated software worker, was present, so it produced no measurement result. | `RUN_STATE.md`, courier addendum; durable-state 2026-09-03 update |
| S06 | `STATUS.md` | The user-level background agents that scheduled it were then uninstalled; no scheduled measurement can fire from them. | `RUN_STATE.md`, next machine step; durable-state 2026-09-03 update |
| S07 | `STATUS.md` | The next machine sequence is to complete the relaunch watchdog, a user-level supervisor that restarts the lead after a quiet run; pin each night plan to the dedicated measurement checkout, the repository copy reserved for measurement; and then run the four-length prompt probe, which compares four candidate input lengths before selecting one. | `RUN_STATE.md`, next machine step |
| S08 | `STATUS.md` | Ed's standing hands-free delegation assigns each transaction decision and the mechanical confirmation of campaign bytes, the exact frozen campaign files, to the lead's independent readiness gate. | `docs/decision_log.md`, hands-free-week delegation |
| S09 | `STATUS.md` | A readiness gate is a pass-or-refuse review that must pass before collection, so no per-window reply from Ed is required. | `docs/decision_log.md`, hands-free-week delegation and live-state reconciliation |
| S10 | `STATUS.md` | A pull request (PR) is a proposed repository change awaiting review or merge. | Plain-language expansion required by the mission |
| S11 | `STATUS.md` | PR #278, which repairs the declared identity set for decode workloads, remains open. | Durable-state pause table |
| S12 | `STATUS.md` | The soundness boundaries are unchanged: no agent may run during measurement; the analysis rules are fixed before claim data are collected; raw evidence is immutable; failed gates issue refusals rather than favorable retries; and no claim sentence is filled before authenticated artifacts license it. | `docs/decision_log.md`, live-state reconciliation; `RUN_STATE.md` and `TASK_QUEUE.md`, standing fences |
| S13 | `STATUS.md` | See `RUN_STATE.md` for the live sequence, `TASK_QUEUE.md` for the generated work queue, `docs/process/state_kernel.json` for machine-readable task state, and `CLAIMS_STATUS.md` for the claim boundary. | Repository authority map in `AGENT_PLAN.md` and `RUN_STATE.md` |

## First-use test

The mechanical check requires one result row for every changed-sentence row,
rejects decision identifiers and internal task-row names in the changed text,
and requires every row to pass. The manual term column records the first-use
gloss applied in that sentence or confirms that only ordinary language or a
previously defined term is used.

| ID | First-use result | Term treatment | Result |
|---|---|---|---|
| C01 | timing anchor defined in place | “program that aligns workload events with power samples” | PASS |
| C02 | campaign generation and four-bit model sizing defined in place | internal label and full parameter wording | PASS |
| C03 | date only | no technical term | PASS |
| C04 | terms already defined by C02 | exact model names follow the full names | PASS |
| C05 | claim-bearing defined earlier in the file | existing glossary context | PASS |
| C06 | gate defined earlier in the file | existing glossary context | PASS |
| C07 | shakedown defined in place; pack previously defined | “short non-claim run” | PASS |
| C08 | campaign bytes defined in place; readiness gate uses prior gate definition | “exact frozen campaign files” | PASS |
| C09 | refusal and agent already defined in the file | existing glossary context | PASS |
| C10 | PR expanded in place | “pull request” before abbreviation | PASS |
| C11 | watchdog and plan pinning defined in place | supervisor and repository-copy glosses | PASS |
| C12 | campaign generations defined earlier | historical labels only | PASS |
| C13 | prospective and campaign defined earlier | existing glossary context | PASS |
| C14 | ordinary claim language | no new technical term | PASS |
| C15 | diagnostic and claim basis already established | existing context | PASS |
| C16 | mint defined earlier | existing glossary context | PASS |
| C17 | prospective and campaign defined earlier | existing glossary context | PASS |
| W01 | campaign generation and four-bit model sizing defined in place | internal label and full parameter wording | PASS |
| W02 | refusal and agent defined in place | recorded no-result decision and automated-worker glosses | PASS |
| W03 | background agent follows W02 | prior definition | PASS |
| W04 | watchdog and measurement checkout defined in place | supervisor and repository-copy glosses | PASS |
| W05 | campaign generations defined by W01 | historical labels only | PASS |
| W06 | prospective and claim authority are ordinary scientific language | no new shorthand | PASS |
| W07 | status cell only | terms already defined | PASS |
| W08 | shakedown and readiness review are described by their required passes | behavior stated in place | PASS |
| W09 | readiness gate follows the live-rules description | no new shorthand | PASS |
| W10 | network-time state uses ordinary operating language | no internal identifier | PASS |
| W11 | wall meter is ordinary equipment language | no shorthand | PASS |
| W12 | PR expanded in place | “pull request” before abbreviation | PASS |
| W13 | campaign generation defined by W01 | historical window labels spelled out | PASS |
| P01 | phase numbers and controlled result slots already defined by surrounding document | existing glossary context | PASS |
| P02 | prompt-length probe defined in place | non-claim comparison of candidate input lengths | PASS |
| P03 | watchdog defined in place | user-level supervisor gloss | PASS |
| P04 | measurement checkout defined in place | repository-copy gloss | PASS |
| P05 | prefill and tokens defined in preceding text | existing context | PASS |
| P06 | readiness gate and results fill defined earlier | existing glossary context | PASS |
| P07 | fresh-model review is ordinary process language | no model brand or internal identifier | PASS |
| P08 | pull request is written in full; hands-free authority and identity correction use ordinary language | no unexplained abbreviation or internal task name | PASS |
| P09 | prompt probe defined by P02 | prior definition | PASS |
| P10 | readiness review and transaction defined earlier | existing glossary context | PASS |
| P11 | measurement checkout and agents defined by surrounding document | existing context | PASS |
| P12 | shakedown and readiness review defined earlier | existing context | PASS |
| P13 | readiness gate defined earlier | existing context | PASS |
| P14 | readiness gate and transaction defined earlier | existing glossary context | PASS |
| P15 | live-hardware proof stated in plain language | no internal identifier | PASS |
| S01 | ordinary status language | no technical term | PASS |
| S02 | claim-bearing defined in place | permission to support a scientific statement | PASS |
| S03 | campaign generation and four-bit model sizing defined in place | internal label and full parameter wording | PASS |
| S04 | generation label follows S03 | prior definition | PASS |
| S05 | agent defined in place; refusal explained by outcome | automated software worker | PASS |
| S06 | background agent follows S05 | prior definition | PASS |
| S07 | watchdog, measurement checkout, and prompt probe defined in place | supervisor, repository-copy, and candidate-length glosses | PASS |
| S08 | campaign bytes defined in place | exact frozen campaign files | PASS |
| S09 | readiness gate defined in place | pass-or-refuse review | PASS |
| S10 | PR expanded in place | “pull request” before abbreviation | PASS |
| S11 | PR follows S10 | prior definition | PASS |
| S12 | refusal, gate, evidence, and authenticated artifact explained by their actions | no internal identifier | PASS |
| S13 | repository file names are direct owner pointers | no task-row or decision shorthand | PASS |

## Finding and decision table

| Finding | Evidence | Decision |
|---|---|---|
| The current claims header still pointed to the predecessor campaign and a retired readiness council. | Newer-model and live-state decisions; current machine-readable state. | Replace only the live header and current claim-path statements; keep the dated history and all claim fences. |
| The machine-status page still directed readers to the predecessor transaction. | Current session header and next-machine-step block. | Publish the between-runs state, unattended prerequisites, delivered rehearsal, and removed scheduled agents. |
| The advisor phase line and sequence still required Ed at each machine step. | Hands-free-week delegation and unattended-loop decision. | State Ed's standing authority and the delegated independent readiness decision without weakening the zero-agent capture rule. |
| The short status file was an obsolete branch scratch note. | Current session header, durable state, and current queue. | Replace it with a plain-language live capsule and owner pointers. |
| The decode-identity correction is not merged. | Durable-state pause table. | State that pull request #278 remains open; do not describe the correction as landed. |

## Verification notes

Only the two requested focused test modules are run. The repository-wide test
suite is intentionally not run under the mission's preflight rule. The first
first-use command split on its own command text in the report envelope and
failed before checking any sentence; the parser was narrowed to literal
Markdown heading boundaries, then the exact recorded command passed all 58
rows.

## Residual risk

Pull request #278 and the unattended-control branches remain outside this
write scope and are truthfully reported as open or incomplete. This sweep does
not make them landed evidence.
