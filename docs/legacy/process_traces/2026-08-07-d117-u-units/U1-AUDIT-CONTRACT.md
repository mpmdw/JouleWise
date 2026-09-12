Reading additional input from stdin...
2026-08-07T17:41:03.750696Z ERROR codex_models_manager::cache: failed to load models cache: missing field `base_instructions` at line 94 column 5
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fdd50-70ab-70e0-b1df-b5406eaab399
--------
user
ADVERSARIAL AUDIT, CONTRACT LENS — U1+U1b two-slot ledger bracket session + writer integration (read-only; write no files; final message = report, severity + file:line + concrete failing scenario each). Audit the uncommitted diff in this worktree against docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md (finding F1, ranked decision 1, §5A bookend sequence, live-ledger regression expectations) and RATIFICATION.md rulings 1-3. Named decisions D-109/D-116 win; flag conflicts. Verify the CONTRACT: (a) session open verifies physical-head==committed-pin at open ONLY, two immutable one-use slots, no mid-window pin commits; (b) governed abort is a receipt (never deletion) and partial state is recoverable; (c) exact bracket binding refuses neighbor substitution / cross-window borrowing / open sessions — this MUST close night-hardening finding L5 (docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md: bracket selection borrowing another window's receipts, no runs_root/intended-pair binding) — construct the L5 scenario and prove it now refuses; (d) unfinalized/aborted slots NEVER leak into candidate discovery; import-exclusion unchanged; (e) writer (scripts/validate_powermetrics_fiducial.py) reservation-first path cannot fall back to ordinary reservation silently, refuses wrong session/slot/attempt, and its terminal/failure paths always produce a governed closure; (f) no existing fail-closed refusal weakened anywhere in the diff.
codex
I’ll trace the governing decisions and frozen contract first, then audit each changed hunk and exercise the L5 cross-window scenario plus focused regressions. I’ll keep the worktree untouched and report only actionable findings with severity, exact file:line, and a concrete failure case.
  → Read stop card, queue, playbook M0, orchestration, frozen memo, ratification, and named decisions
  • Inspect the full uncommitted diff and map changes to contract clauses
  • Run read-only/focused regressions and construct the L5 adversarial scenario
  • Report only evidence-backed findings with severity, file:line, and failing scenario
exec
/bin/zsh -lc "git status --short --branch && rg -n \"ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next\" RUN_STATE.md && rg -n \"Current Queue|Do-Not-Do-Yet\" TASK_QUEUE.md && rg -n \"Mission M0|D-109|D-116\" docs/agent_playbook.md AGENT_PLAN.md docs -g '*.md'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
## impl/d117-u1-ledger-session...origin/main [behind 14]
 M joulewise/calibration_bracketing.py
 M joulewise/calibration_ledger.py
 M scripts/validate_powermetrics_fiducial.py
 M tests/test_calibration_bracketing.py
 M tests/test_calibration_ledger.py
 M tests/test_powermetrics_fiducial.py
?? scripts/reserve_calibration_window_bracket.py
2004:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2039:## ACTIVE_STOP_CARD
2178:## Current Project Status
2739:## Known Workspace State
96:Current Queue region is the sole live work-selection view.
213:## Current Do-Not-Do-Yet List
306:## Current Queue
docs/agent_playbook.md:26:1. Run Mission M0 (preflight) — always.
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
docs/agent_playbook.md:26:1. Run Mission M0 (preflight) — always.
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
docs/decision_log.md:134:| D-109 | CAL-BRACKET-D079-01 F3: A-min-with-reservation — writer-enforced receipt ledger (reservation-first pending entry before capture, mandatory finalization, unresolved-pending refusal), ledger-only consumption, repo-committed head pin, single immutable snapshot threading; R1 authority/retention/anti-rollback (7 clauses) + R2 prior-observation set with the 38-total counting rule (8 clauses); Option B recorded as rejected fallback; lands with F1+F2 as the single combined fix round | accepted (Ed 2026-08-03, same deferral; Sol soundness breaks lead-verified and adopted) |
docs/decision_log.md:135:| D-110 | Mint #1 retroactively NON-CLAIM-BEARING (taint-and-remint, Ed ruling on sweep finding RT-1: floors embed zero allowance where D-102 pin 3 mandates +max(drift, 0.010818 s)); re-mint gated on D-109 landing + artifact issuance + validator pin widening; RT-2 dependency edge minted (MINT-GENERALIZE-01 hard-blocked on CAL-BRACKET-D079-01); night-consult 7B-mint license suspended; RT-5 recorded: all four PASSED window verdicts untainted | accepted (Ed 2026-08-03, sweep-triggered) |
docs/decision_log.md:141:| D-116 | D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (seq 76 / head 08456d50…; issued sha 316113960c…; 30/2/6 dispositions); D-110 condition (b) SATISFIED → MINT-GENERALIZE-01 unblocked for re-mint; two-cold-gate history (plan HELD → consumer impl + gauntlet → bytes PROCEED, sequencing HOLD resolved by consumer-first merge); window_metrologyB calibration fiducials in completeness record are NOT a D-113 violation | executed (Fable magistrate, 2026-08-06; Ed pre-authorized) |
docs/decision_log.md:6987:## D-109: CAL-BRACKET-D079-01 F3 — A-min-with-reservation adopted (writer-enforced receipt ledger, reservation-first, repo-committed head pin); R1 ledger-authority and R2 prior-observation-set rulings
docs/decision_log.md:7117:2. RE-MINT CONDITIONS: (a) the D-109 CAL-BRACKET implementation lands
docs/decision_log.md:7159:   the D-108/D-109 debate record, the night-consult rulings memo, the
docs/decision_log.md:7208:## D-109 addendum II: reviewed mint-core interface amendment (integration-collision resolution); D-110 oracle clarification
docs/decision_log.md:7219:1. D-109 R1.4's `calibration_ledger_snapshot` threading is a DELIBERATE
docs/decision_log.md:7488:## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)
docs/decision_log.md:7495:- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
docs/decision_log.md:7501:**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.
docs/council_log.md:75:| C-042 | 2026-08-03 | Ed-requested pre-ruling debate: 2-round adversarial Sol xhigh consult over the D-108/D-109 decision packets (MCP discussion lane, read-only; Sol instructed to bench-verify packet claims; record .desk/2026-08-03-sol-debate-d108-d109.md); Ed then ruled by explicit deferral to the joint position | Both packets materially changed before ruling: Sol caught the overstated three-subject manual-verification claim and broke the original A-min formulation (writer crash-window; prefix-subset is not anti-rollback) — both lead-verified and adopted (reservation-first + repo-committed head pin now D-109 law); Sol's code refutation of the magistrate's two-subject license-surface counter adopted into D-108 clause 2; magistrate context (schedule slack, metrology pivot, shared-R2 marginal cost) flipped Sol's B recommendation to A-min-with-reservation, withdrawn on the record; residual dissents preserved in both decision texts |
docs/council_log.md:80:| C-047 | 2026-08-03 | The 16h runway (Ed-granted; joint Fable+Sol decision authority; concurrent sweep instance mid-flight): D-108/D-109 debate+rulings executed, D-110/D-111 sweep-triggered rulings, winB STOP cold gate -> D-112, two Sol gauntlets, pinned byte-identical mint replay, checkpoint for harness switch | D-108 closed via PR #99 + re-record; CAL-BRACKET held at 2e61ff9 (B1 residual, rule-11 gate owed); winB license exhausted as drawn (r06 disposition parked for Ed); mint chain D-110-blocked; CLAIMS_STATUS section 1 honestly NONE; sweep propagation fixes landed; layer yield in the run report |
docs/council_log.md:82:| C-049 | 2026-08-05/06 | The 12h autonomous marathon: six PRs (#102-#104, #106-#108) + PR #109 issuance gauntlet; two rule-11 escalation consults (CGV F3 closure, QG census Option C); the D-079 issuance cold gate (split verdict, HOLD upheld); D-113/D-115/D-116; then the first re-mint consumption attempt exposed a structural closure -> Sol xhigh fork consult | The cold gate's HOLD prevented an irreversible ledger write paired with a production-refused artifact (F1 no-consumer-path, F2 digest-role coupling — issuance reframed as implementation and re-gauntleted as PRs #108/#109); xhigh delta re-audits again caught introduced defects (QG init-durability F1; CGV live-proved receipt-serialization B1 + phantom-fence B2); historical max-bracket consumption proved structurally closed at main — Option 2 (three fresh prospective windows) recommended by consult + magistrate; Ed's ruling OWED at close |
docs/council_log.md:2667:escalated to Ed (D-109 pending)** — D-102 mandates the triggers but no
docs/council_log.md:2686:## C-042: Ed-requested pre-ruling debate — 2 Sol xhigh rounds over the D-108/D-109 packets, both packets materially changed (2026-08-03)
docs/council_log.md:2692:explicit deferral to the joint position → D-108 + D-109. Full record:
docs/council_log.md:2719:Residual Sol dissents preserved in D-108/D-109 text: three-occurrence
docs/council_log.md:2749:over-drop), D-109 B1/B2 + four weak fences; Opus contract refuter —
docs/council_log.md:2769:beside it; policy: D-109 addendum II.
docs/council_log.md:2822:rounds, exact-bytes dual cold review); (vi) D-116 issued, PR #109
docs/council_log.md:2864:D-113 transcribed (`8e68cde`); D-115 on main (`0941cf5`); D-116 on PR
docs/contracts/calibration_ledger.md:4:`joulewise.calibration_observation_ledger.v1`. D-109 R1 and R2 are controlling.
docs/contracts/calibration_ledger.md:181:pin, preserving D-109 R1.4's anti-rollback boundary.
docs/contracts/calibration_ledger.md:209:   artifact. A later committed live extension is permitted by D-109 R1.4; it
docs/process_traces/2026-08-05-d113-rigor-consult/CONSULT-REPORT.md:160:              "The frozen chain consumes the issued acceptance artifact mechanically. It must not rely solely on the runbook's copied 0.033558756679900 literal if the landed D-109 path now owns that decision.",
docs/process_traces/2026-08-05-d113-rigor-consult/CONSULT-REPORT.md:162:              "Prewrite the post-window ledger procedure: finalize every reservation, update and commit the ledger head pin after measurement, and only then run claim evaluation. D-109 forbids evaluation between ledger advancement and the committed pin."
docs/process_traces/2026-08-05-d113-rigor-consult/CONSULT-REPORT.md:270:        "detail": "Traced D-100, D-106, D-108, D-078, D-109, D-110, D-114, D-115, the refusal-scope specification, and current claim-state consequences."
docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:112:      "text": "CLAIMS_STATUS reflects the earlier D-110 hard block, while later D-116 records the remint prerequisites satisfied and MINT-GENERALIZE-01 unblocked.",
docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:255:- Verify current D-110/D-116 remint state and use newly governed floors, not historical floor literals.
docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md:32:evidence), F3 (CLAIMS_STATUS staleness vs D-116 — check before window
docs/phase_2/window_c_operator_checklist.md:361:- Calibration screens, drift limits, and acceptance-artifact chain: D-079, D-102, D-109, and `configs/calibration/calibration_acceptance_d079_v2.json`.
docs/run_reports/2026-07-11-p2046-load-transition-prep.md:10:- Followed root `AGENTS.md` and Mission M0 before edits.
docs/process_traces/2026-08-03-winB-reeval-stop/PACKET.md:9:D-108 close, and clause-(d) re-record are all landed; Stream B's D-109
docs/specs/c027/p2-040_reducer_gate_correctness.md:911:  status/workspace/next-action sections, Mission M0, source-of-truth map, and
docs/specs/c027/rpt-001_report_vertical_slice.md:1489:- Mission M0 and orchestration guidance;
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-fix1.md:153:git commit -m "D-109: close cal-bracket audit B1/B2/S1" -m "Close independent audit blockers B1 and B2 plus should-fix S1: enforce the ledger snapshot for minted consumption, classify abandoned attempts as unresolved, and make the four regression fences defect-shaped."
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:116:D-116’s issued ledger is the correct trust root, and D-117 correctly requires fresh live pre/post observations. The obstacle is mechanical: the present append path requires the physical ledger head to match the committed pin when reserving an attempt. Once the pre observation is finalized, that equality no longer holds for an ordinary post reservation.
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:472:- Ratify the two-slot ledger capability against D-109/D-116, especially whether an open post slot may exist during the pre-science successor probe.
docs/stream_logs/2026-07-07-doc007-docs.md:154:- Binds: docs/agent_playbook.md gate summary + Mission M0.
docs/stream_logs/2026-07-07-doc007-docs.md:230:Evidence: `docs/agent_playbook.md` sections `Current Gate Summary` and `Mission M0: Preflight (every session)`.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-delta.md:7:  "summary": "One D-109 blocker remains: the new guard breaks legitimate minted consumers while implicit minted rows still bypass it; B2 and S1 repairs hold.",
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-delta.md:23:        "clauses": ["D-109 R1.2", "D-109 R1.4"],
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-delta.md:45:        "question": "B2 / D-109 R2.6",
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-delta.md:57:        "question": "Preserved D-109 clauses",
docs/process_traces/2026-08-07-d117-plan-freeze/CONSULT-PROMPT.md:39:   issued ledger (D-116 regime) — specify the receipt flow and what the synthetic
docs/run_reports/2026-08-03-16h-runway.md:3:Session shape: Ed returned briefly (ruled D-108/D-109 by deferral after
docs/run_reports/2026-08-03-16h-runway.md:14:- **D-109** (Ed deferral): CAL-BRACKET A-min-with-reservation; R1 (7
docs/run_reports/2026-08-03-16h-runway.md:36:2. **D-109 stream:** Sol xhigh impl `8383113` (ledger, reservation-
docs/run_reports/2026-07-11-p2041-vetted-rebuild.md:30:  Do-Not-Do-Yet list, Mission M0, orchestration process, source-of-truth map,
docs/run_reports/2026-07-11-p2041-vetted-rebuild.md:230:- Skills/playbooks used: Mission M0, planning-reflection protocol,
docs/specs/c027/p2-038_production_uncertainty_evidence.md:999:- Read the targeted `RUN_STATE.md` sections, current queue, do-not-do-yet rules, Mission M0, planning protocol, and source-of-truth map.
docs/process_traces/2026-08-03-d111-backfill/debate-d108-d109/2026-08-03-sol-debate-d108-d109.md:1:# Sol xhigh debate on D-108 / D-109 decision packets (2026-08-03, Ed-requested)
docs/process_traces/2026-08-03-d111-backfill/debate-d108-d109/2026-08-03-sol-debate-d108-d109.md:33:## D-109 (CAL-BRACKET F3) — Sol FLIPPED B → A-min-with-reservation
docs/process_traces/2026-08-03-d111-backfill/debate-d108-d109/2026-08-03-sol-debate-d108-d109.md:101:Council-log entry to land with the D-108/D-109 ruling bookkeeping.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/refuter-prompt.md:9:  "OBJECTIVE": "Attempt to refute (a) the delta re-audit's B1-refined finding and (b) the lead's proposed round-2 disposition, against the code at HEAD and the D-109 contract; then rule on packet section 8 items (a)-(e) from the contract lens. Read-only.",
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/refuter-prompt.md:11:    "docs/decision_log.md entry D-109 (R1 clauses 1-7, R2 clauses 1-8) — the governing contract; read the FULL entry, not only the packet's excerpts",
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/refuter-prompt.md:27:    "Cross-check of the six custody inputs and the full D-109 entry against the packet text",
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/refuter-prompt.md:40:- D-109 landed a Sol-delegated implementation (commit 8383113); an independent audit found blockers B1, B2 and should-fix S1; fix round 1 (commit 2e61ff9, this HEAD) claimed to close all three; the delta re-audit closed B2 and S1 but found B1 PERSISTS IN REFINED FORM.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/refuter-prompt.md:48:2. REFUTE THE DISPOSITION. Does the lead's proposed shape (guard after/inside the preparation seam + normalized-semantics comparison + the two named regressions) actually satisfy D-109 R1.2 (reservation-first refusal semantics) and R1.4 (ONE immutable ledger snapshot threaded through EVERY consumer path: session, direct runner, secondary verifier) on every consumer path? Enumerate the consumer paths you checked. Name any path the disposition leaves uncovered (a residual bypass) and any way it introduces a NEW fail-closed break. If the disposition is under-specified in a way that matters (e.g., "after or inside the seam" admits a wrong placement), say exactly what constraint is missing.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/refuter-prompt.md:50:3. PACKET HYGIENE. Compare the packet (PACKET.md) against the six custody inputs and the full D-109 entry. Does the packet omit, soften, or misframe any material evidence? Check in particular that its verbatim quotations are actually verbatim and that section 5's "what is NOT in dispute" list matches the delta re-audit.
docs/process_traces/2026-08-07-d117-plan-freeze/RATIFICATION.md:9:   rejected as the memo argues). U1 implements; ratify-vs-D-109/D-116
docs/specs/c027/doc-008_state_kernel.md:552:- Intake and close-out procedure: `docs/agent_playbook.md`, Mission M0 and
docs/run_reports/2026-07-12-claude-sol-bridge.md:172:- Active stop card at intake: none. Mission M0 and orchestration rules were
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-fix-prompt.md:3:AUTHORITY: D-109 R1/R2 in /Users/edr/code/JouleWise/docs/decision_log.md (absolute path; main is ahead of this worktree); the audit findings B1/B2/S1 with their evidence lines.
docs/run_reports/2026-07-09-meta-process-stop-card-cleanup.md:28:- Updated `docs/agent_playbook.md` Mission M0 so preflight honors active
docs/run_reports/2026-07-11-repro002-publication-privacy.md:14:The run began with Mission M0. I read the active stop card, Current Project
docs/run_reports/2026-07-11-repro002-publication-privacy.md:119:Mission M0 baseline command (unpiped to sandbox file):
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-audit.md:7:  "summary": "Audit found two D-109 blocker-grade fail-open paths and one should-fix regression-discrimination gap; scope and remaining clauses were conformant.",
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-audit.md:23:        "clauses": ["D-109 R1.2", "D-109 R1.4"],
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-audit.md:35:        "clauses": ["D-109 R2.3", "D-109 R2.6"],
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-audit.md:47:        "clauses": ["D-109 R1.3", "D-109 R2.5", "D-109 R2.8", "original F3 regression fence"],
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-audit.md:239:B1 — blocker: minted consumption bypasses D-109’s universal snapshot gate.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-audit.md:243:A read-only probe supplied a snapshot containing `calibration_ledger_pending`; the minted session returned `ready=True` with no refusal. Thus pending, rollback, or stale-head state can be ignored on this consumer route, contrary to D-109 R1.4’s “every consumer path” requirement. Non-minted paths correctly reuse one object—there was no observed double-load TOCTOU.
docs/run_reports/2026-08-03-t3-cutover-night.md:86:3. **Integration collision, correctly stopped.** D-109's required
docs/specs/c027/p2-039_floor_artifact.md:987:- Ran Mission M0 intake from `docs/agent_playbook.md` and inspected the
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-report.md:7:  "summary": "D-109 combined CAL-BRACKET implementation is complete and fully verified, but the sandbox prevented creating the requested commit.",
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-report.md:119:      "needs": "Run V4 with Git-index write access, then commit with a message citing D-109."
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-report.md:134:Implemented all D-109 R1/R2 clauses in code: reservation-first immutable ledger receipts, anti-rollback head pinning, ledger-only evaluation, single-snapshot threading, prior-set trigger semantics, 38-total counting, F1/F2, backfill tooling, and defect-shaped regressions. No D-109 implementation clause was silently narrowed.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-report.md:143:git commit -m "Implement D-109 calibration ledger and bracket acceptance"
docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-RECOMMENDATION-FOR-ED.md:60:CAL-BRACKET fix round after you rule R1+R2, becoming D-109. My lean flips
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-prompt.md:1:OBJECTIVE: Implement Ed's D-109 ruling on branch impl/cal-bracket-d079 as the SINGLE combined CAL-BRACKET fix round (F1 + F2 + F3/A-min + R2 schema), one commit, building on the current uncommitted worktree diff (the accepted first-round implementation + fixes).
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-prompt.md:4:1. D-109 in /Users/edr/code/JouleWise/docs/decision_log.md (near EOF; the main checkout is AHEAD of this worktree — read the full R1 [7 clauses] and R2 [8 clauses] from that absolute path; they are binding law for this commit). Key implementation-bearing points inline:
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-prompt.md:13:2. D-102 (same file) — thresholds/freshness semantics unchanged; D-109 implements it, never weakens it.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-prompt.md:14:3. Row CAL-BRACKET-D079-01 acceptance in /Users/edr/code/JouleWise/docs/process/state_kernel.json (updated for D-109) — the acceptance evidence list is the checklist.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-prompt.md:26:7. One commit on impl/cal-bracket-d079 citing D-109. Do not push.
docs/process_traces/2026-08-03-calbracket-b1-gate/inputs/streamB-prompt.md:31:VERIFICATION before completion: python3 -m unittest tests.test_calibration_ledger tests.test_calibration_bracketing tests.test_whole_window_selection tests.test_reduce -v green; then the FULL suite (python3 -m unittest discover -s tests) green; report the exact counts. State any D-109 clause you could not implement faithfully as a flag, never silently narrow it.
docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md:21:  `PROJECT_STATUS.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, Mission M0,
docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md:107:  protocol; Mission M0; `docs/orchestration.md`.
docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/DISPOSITION-FOR-ED.md:94:On Ed's F3 ruling this + F1/F2 become D-109.
docs/run_reports/2026-08-03-desk-session.md:29:a claim-soundness gap D-102 left open — as **D-109 pending**. Both parked
docs/run_reports/2026-08-03-desk-session.md:94:## 3. CAL-BRACKET-D079-01 — consult over blind round three (F1/F2 ruled; D-109 pending)
docs/run_reports/2026-08-03-desk-session.md:108:**D-109** (build an authenticated calibration-observation registry vs.
docs/run_reports/2026-08-03-desk-session.md:136:  the two parked rows now render BLOCKED (D-108/D-109 dependencies), the
docs/run_reports/2026-08-03-desk-session.md:151:`92da4ad` (CAL-BRACKET F1/F2 / D-109) · `ed845bb` (TEST-SPEED data+design)
docs/run_reports/2026-08-03-desk-session.md:154:**D-109** pending Ed. Council: **C-040 addendum**, **C-041**.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:21:    "recommendation": "Update _CORE_SIGNATURES to the D-109 signature as an explicit reviewed interface revision; do not add an adapter shim, multi-version layer, or core-file digest pin.",
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:38:        "title": "Output parity does not prove D-109's one-snapshot identity invariant",
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:44:      "Q2": "Rename the contract to review-pinned mint-core interface and document the D-109 revision.",
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:147:Treat this as a deliberate D-109 R1.4 interface revision.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:171:- Both compared paths share the same defective core, preserving bytes while silently violating D-109.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:182:- Add a note adjacent to `_CORE_SIGNATURES` stating that the D-109 R1.4 amendment added the immutable ledger snapshot parameter and that future changes require explicit signature-pin review plus parity evidence.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:194:This directly covers D-109 R1.4 (`docs/decision_log.md:7024-7029`). The branch audit covered snapshot identity elsewhere, but no mint-specific executable assertion was found.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:200:  - Add the D-109 review note.
docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.md:236:Checks performed: finding, D-109 synthesis, D-109/D-110 decision text, generalized guard and tests, branch core diff, historical byte-compare record, state-kernel MINT row, run-state handoff, and workspace status inspected; no files modified and no tests executed.
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:51:        "clause": "D-109 R1.4",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:56:        "clause": "D-109 R2.1",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:61:        "clause": "D-109 R2.2",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:66:        "clause": "D-109 R2.3",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:71:        "clause": "D-109 R2.4",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:76:        "clause": "D-109 R2.5",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:81:        "clause": "D-109 R2.6",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:86:        "clause": "D-109 R2.7",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:91:        "clause": "D-109 R2.8",
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:116:        "detail": "calibration_bracketing.py byte-pins the current fixture, requires artifact_role=schema_fixture_unissued, unratified_fixture status, claim_eligible=false, cutoff sequence 0/all-zero digest, and production_issuance_blocked=true. Production evaluation then unconditionally refuses the artifact as an unissued fixture. The packet proposes only ledger execution, head-pin update, artifact edit and D-116; it omits the required reviewed loader/schema/pin transition and supplies no exact final artifact bytes."
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:227:F1 — blocker. The proposed issuance cannot create an artifact accepted by the landed selector. [calibration_bracketing.py](/Users/edr/code/JouleWise/joulewise/calibration_bracketing.py:155) permits only the genesis unissued-fixture shape; the byte pin is the current fixture hash, and production evaluation explicitly refuses it at line 757. Updating only the JSON and head pin therefore fails D-109 R1.4 and leaves D-110(b) unsatisfied.
docs/process_traces/2026-08-06-d079-issuance-coldgate/SOL-CONTRACT-LENS-HOLD.md:233:F4 — should_fix. The reviewed custody manifest contains 38 iCloud-backup locators. This is acceptable authenticated custody under D-109: all primary bytes are rehashed, and content IDs are path-independent. The copies do not need to be moved into the primary checkout first.
docs/process_traces/2026-08-04-calbracket-integration-collision/delta-reaudit.md:34:      "A1": "Partially fails because RUN_STATE.md:49 and :56 retain binding byte-frozen/frozen-expectation framing. The amended code otherwise matches the live D-109 signature; the literal pin exists; the parity test retains read_bytes equality; and the snapshot regression uses assertIs at both authentication seams and rebinding with one loader call.",
docs/process_traces/2026-08-06-d110-remint-fork/CONSULT-PROMPT.md:32:- PR #109 (D-079 issuance, D-116) merged this morning: the calibration
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-PACKET.md:30:acceptance-artifact config. Then D-116 records it.
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-PACKET.md:41:2. **D-109 R2 conformance of the ACTUAL bytes** (not the plan): R2.1
docs/process_traces/2026-08-03-calbracket-b1-gate/ruling-cold-fable.md:42:4. **Legacy-row ruling (tension the lead's §7 does not address):** undeclared legacy rows normalize to minted, so mechanism 2 will refuse session-less legacy replay through the frozen pointwise seam (:3483-3497, comment "Frozen/pre-D-109 row-verifier tests retain their historical pointwise seam"). I rule **fail-closed wins**: D-109 R1.4's "every consumer path" admits no undeclared-row exemption — an exemption for missing declarations recreates the fail-open hole by construction. If frozen tests break, update them to supply prepared sessions or explicit non-minted declarations; if Sol believes a genuinely frozen contract forbids this, the required move is a `NEEDS_RULING` early return, never a weakened guard.
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-PROMPT.md:22:The BINDING issuance requirements are D-109 R1 clause 4 and R2 clauses
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-PROMPT.md:37:1. Transcribe D-109 R2 clauses 1-8 (and R1 cl.4) into your report
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-PROMPT.md:40:   the decision log around D-109, configs/calibration/, and the D-109
docs/process_traces/2026-08-04-calbracket-integration-collision/impl-report.md:109:- FIX-1: Complete. Added the D-109 ledger-snapshot parameter to the signature pin and the required future-review comment.
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:45:      "clause": "D-109 R1.4",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:51:      "clause": "D-109 R2.1",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:57:      "clause": "D-109 R2.2",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:63:      "clause": "D-109 R2.3",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:69:      "clause": "D-109 R2.4",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:75:      "clause": "D-109 R2.5",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:81:      "clause": "D-109 R2.6",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:87:      "clause": "D-109 R2.7",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:93:      "clause": "D-109 R2.8",
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:625:        "warning": "Illustrative only; the assumptions are not authorized by D-109 or an import schema."
docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:637:        "warning": "Illustrative only; differs from D-109 R2.8's stated six-further consequence."
docs/process_traces/2026-08-04-calbracket-integration-collision/FINDING.md:1:# Integration collision: D-109's mint threading vs the byte-frozen generalized-mint interface guard
docs/process_traces/2026-08-04-calbracket-integration-collision/FINDING.md:24:- **Branch side (legitimate):** D-109's implementation commit `8383113`
docs/process_traces/2026-08-04-calbracket-integration-collision/FINDING.md:27:  and `_authenticate_component`). This is REQUIRED by D-109 R1.4 —
docs/process_traces/2026-08-04-calbracket-integration-collision/FINDING.md:70:   the NEW signature and a note recording why it changed (D-109 R1.4
docs/process_traces/2026-08-04-calbracket-integration-collision/RESOLUTION.md:18:   `scripts/mint_floor_artifact_generalized.py` to the D-109 signature
docs/process_traces/2026-08-04-calbracket-integration-collision/RESOLUTION.md:40:   D-109 R1.4's invariant, now executable.
docs/process_traces/2026-08-06-d079-issuance-coldgate/SYNTHESIS.md:77:5. **THEN** D-116, recording: all-38 iCloud custody; R2.8's "six
docs/process_traces/2026-08-03-calbracket-b1-gate/ruling-sol-refuter.md:130:      "cmd": "Static inspection of D-109, PACKET.md, all six custody inputs, and the requested code/test files at HEAD",
docs/process_traces/2026-08-03-calbracket-b1-gate/ruling-sol-refuter.md:136:          "D-109 R1 clauses 1-7 and R2 clauses 1-8 inspected",
docs/process_traces/2026-08-03-calbracket-b1-gate/ruling-sol-refuter.md:215:Finally, §4 omits D-109 R1.1’s sole-ledger authority and the entry’s applicability to every session construction (`docs/decision_log.md:6995-7012`). Those clauses materially explain why an implicit minted secondary-verifier bypass is prohibited. This does not change the gate result because the full D-109 entry was separately supplied as authority.
docs/process_traces/2026-08-03-q1-remint-bytecompare/RESULT.md:51:  re-mint under the landed D-109 selector; the re-mint conditions are
docs/process_traces/2026-08-03-calbracket-b1-gate/SYNTHESIS.md:126:unaffected (full D-109 was supplied as authority). The packet is NOT
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:37:      "D-109 R1.4": "HOLD: cutoff and consumer authentication logic conform, but the packet incorrectly says --execute commits the head pin; the CLI only prints candidate head-pin content.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:38:      "D-109 R2.1": "PASS: both cutoff fields contain the exact 76/08456d50 pair reproduced from the authenticated import.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:39:      "D-109 R2.2": "PASS for the binding decision: derivation_corpus is exactly the unchanged n=19 table. FAIL for the packet's additional 3cece3b2 sub-field requirement.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:40:      "D-109 R2.3": "PASS: all 38 content-distinct observations carry separate attempt_id, epoch_id and disposition; counts are 30/2/6.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:41:      "D-109 R2.4": "PASS: all content IDs recompute solely from canonical manifest.json and instrument_evidence.json byte hashes; no prior-set row contains a path.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:42:      "D-109 R2.5": "PASS: the exact prior set is cutoff-bound and import-marked observations are excluded from later new-observation discovery.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:43:      "D-109 R2.6": "PASS: no unresolved, pending, abandoned or unclassifiable observation appears.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:44:      "D-109 R2.7": "PASS: raw-physics verification supports systematic-invalid for 491995f3 and c76f5d1c.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:45:      "D-109 R2.8": "PASS: 30 valid same-epoch observations are below 38; eight additional valid observations are required, and issuance does not trigger re-derivation.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:47:      "D-110(a)": "PASS: the D-109 implementation merge is an ancestor of the reviewed branch.",
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:64:        "detail": "The exact file contains zero occurrences of 3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d and derivation_corpus has no digest field. Its canonical subobject digest is 9a19b81d94880cd34d8321ce75d06a9222888cd574b00943bdb3d36a38d64e55. The 3cece3b2 value was the unissued artifact's old whole-core digest, not a corpus sub-digest. D-109 R2.2 requires the n=19 membership, which is preserved, but the packet's explicit additional requirement is not satisfied."
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:70:        "detail": "scripts/calibration_ledger_bootstrap.py explicitly states that --execute writes the ledger while the head pin is never written. It prints head_pin_content for a separate lead-controlled update. Without that explicit update and Git commit after ledger advancement, the physical head differs from the committed genesis pin, D-109 R1.4 refuses consumption, and D-110(b) remains incomplete."
docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-SOL-CONTRACT-LENS.md:172:F2 — blocker. The bootstrap command does not update or commit `configs/calibration/calibration_ledger_head.json`; it only prints the proposed pin. The execution procedure must explicitly apply and Git-commit the exact `76/08456d50…` pin before D-116 or any claim evaluation.
docs/process_traces/2026-08-03-calbracket-b1-gate/PACKET.md:24:3. Bench vs delegated: D-109 landed as a Sol-delegated stream;
docs/process_traces/2026-08-03-calbracket-b1-gate/PACKET.md:32:| `streamB-prompt.md` | Implementation prompt (D-109 combined round) | base `a14d1fe` |
docs/process_traces/2026-08-03-calbracket-b1-gate/PACKET.md:42:## 4. Governing clauses (verbatim, `docs/decision_log.md` D-109)
docs/process_traces/2026-08-03-calbracket-b1-gate/PACKET.md:110:D-110 re-mint condition (a): the D-109 CAL-BRACKET implementation must
docs/process_traces/2026-08-06-d079-issuance-coldgate/PACKET.md:22:4. A decision-log entry (D-116) records the issuance.
docs/process_traces/2026-08-06-d079-issuance-coldgate/PACKET.md:49:- Binding requirements: D-109 R1.4 + R2.1-8 (docs/decision_log.md).
docs/process_traces/2026-08-06-d079-issuance-coldgate/PACKET.md:62:3. D-109 R2 conformance of the plan: prior_observation_set completeness

codex
The checkout has no active stop card and the requested audit is in the agent-safe lane. One referenced path is absent at this branch tip, so I’m resolving the night-hardening register by repository search and will treat the user’s quoted L5 behavior as binding if the source exists only on the newer upstream history.
exec
/bin/zsh -lc "rg --files docs/process_traces | rg 'night-hardening|FINDINGS-REGISTER|d117-plan-freeze'; git diff --stat; git diff --name-status; git diff --check; sed -n '50,115p' docs/agent_playbook.md; sed -n '1,240p' docs/orchestration.md; sed -n '6987,7088p' docs/decision_log.md; sed -n '7488,7525p' docs/decision_log.md; sed -n '1,220p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; sed -n '220,520p' docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md; cat docs/process_traces/2026-08-07-d117-plan-freeze/RATIFICATION.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
docs/process_traces/2026-08-07-d117-plan-freeze/CONSULT-PROMPT.md
docs/process_traces/2026-08-07-d117-plan-freeze/RATIFICATION.md
 joulewise/calibration_bracketing.py       | 267 +++++++++-
 joulewise/calibration_ledger.py           | 811 +++++++++++++++++++++++++++++-
 scripts/validate_powermetrics_fiducial.py | 350 ++++++++++---
 tests/test_calibration_bracketing.py      | 286 +++++++++++
 tests/test_calibration_ledger.py          | 315 +++++++++++-
 tests/test_powermetrics_fiducial.py       | 149 ++++++
 6 files changed, 2093 insertions(+), 85 deletions(-)
M	joulewise/calibration_bracketing.py
M	joulewise/calibration_ledger.py
M	scripts/validate_powermetrics_fiducial.py
M	tests/test_calibration_bracketing.py
M	tests/test_calibration_ledger.py
M	tests/test_powermetrics_fiducial.py
## Mission M0: Preflight (every session)

1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
   if present, "Current Project Status", "Known Workspace State", and
   "What Is Next". If the stop card is ACTIVE, it overrides this
   playbook and the task queue until cleared.
2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
3. Read the selected mission's own read-first list. Read `AGENT_PLAN.md`
   only at phase starts or when the project structure changes. Consult
   `docs/decision_log.md` by targeted decision ID, not as a whole-file
   intake step.
   If the session involves delegation, review, or multi-stream work, also
   read `docs/orchestration.md` (the process layer) — not optional for
   landing code.
4. Check workspace state with `git status --short --branch`; inspect
   recent commits only when the handoff or mission needs them.
5. `python3 -m unittest discover -s tests` — expect `Ran <N> tests` (N per `RUN_STATE.md` Current Verification; `, OK
   (skipped=10)` with zero expected failures as of 2026-07-08 after
   P2-013/P2-014 and the C-011 rigor mechanics. The skips are the `[analysis]`-extra chart tests plus one
   optional-jsonschema test. A red suite is itself the mission: stop and fix
   or report.
6. Review `docs/risk_register.md` at phase starts, before hardware tasks,
   when a trigger fires, or if >14 days passed since the last run report
   with no break recorded in `docs/milestones.md`.
7. At session end, always: update `RUN_STATE.md`, update `TASK_QUEUE.md`,
   write a dated run report in `docs/run_reports/`, update the phase exit
   checklist for anything that closed, and `PROJECT_STATUS.md` if
   advisor-visible state changed. Commit when the user asks or has
   standing-approved it.

Environment cautions:

- The repo must stay at a non-iCloud path (`~/code/...`; R-017). If you
  see `Operation not permitted` on reads inside the repo, stop, wait for
  the lock to clear, re-run the suite, and record the incident.
- CI installs no extras; every new test must pass on a bare Python
  (lazy imports, `skipUnless` for optional deps — D-009).
- Schema changes are additive-only until v0.2 (R-015/D-008).

---

## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)

**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
Slice 2N. This mission adds the code-level route for each work item,
sourced from the 2026-07-05 external code review. Line numbers are from
commit `ae48abe` — re-locate by symbol name if the files have moved on.

Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
(skim whole files — they are small and the invariants interlock).

2N is one mission but NOT one sitting: it touches adapter interfaces,
controller timing, reducer behavior, report parsing, CLI, schema export,
and validation policy. Work item-by-item with the suite green after each,
and land it as roughly three commits so a failure bisects cleanly:

- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
  2N.2 (measured-window boundaries). Both touch controller/interfaces.
- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
  contract), 2N.7 (report alignment), and 2N.6's structured read
  failures implemented on top of it. 2N.6's CLI verb rides along.
- **Commit C — schema + metrics:** 2N.5 (schema round-trip), 2N.3
  (token-count fallback), 2N.9 (v0.2 compatibility note).

If a session ends mid-slice, a completed commit group is a clean
# The Orchestration Process

How this project is actually built: a human researcher directing a
multi-model AI system whose workflow is itself a deliberate, versioned,
self-instrumenting piece of engineering. This document is the single
in-repo description of that process. (The executable playbooks live
outside the repository as reusable "skills" so they transfer to future
projects; this page describes what they do and where their evidence
lands in this repo.) Binding role and process changes live in
`docs/decision_log.md`; this page avoids copying volatile model versions.

## Roles: a lead, independent implementers/reviewers, and a human at the top

- **Ed (researcher)** sets research direction, methodology
  non-negotiables (raw-evidence bundles, dual-basis capture with gross-energy
  headlines, named
  measurement boundaries, no unauditable claims), hardware/access
  decisions, and — critically — *process policy*: every rule below
  traces to a standing instruction issued after an observed failure or
  opportunity. External-facing claims and merge authority derive from
  him (he granted the lead conditional self-merge authority on
  2026-07-08 once the review gate had proven itself).
- **The designated lead** owns
  decomposition, triage, design adjudication, every final diff gate,
  all live/hardware verification, merge decisions, bookkeeping, and
  process evolution. Other agents save lead capacity without inheriting
  final authority; all escalation paths terminate at the lead.
- **Independent implementation and review agents** do the heavy reading and
  writing: implementation against pinned specs, adversarial review
  lenses, test writing, test *auditing* (never of its own tests — a
  fresh instance audits), docs drafting, and review of the lead's own
  consequential decisions. Cross-model review is load-bearing by
  design: the attributed per-layer catch record (below) shows the two
  roles consistently catching different classes of defect.
- **Specialist agents** handle bounded sweeps (for example, docs
  consistency) and, when a stream genuinely needs
  mid-stream judgment, as a stream director — a role that is now the
  exception rather than the default (see Topology).
- **Image-heavy analysis uses the designated image-capable review route** per
  C-012, after the site-observatory stream's image-critique rounds.
- **Invited-peer validation is allowed to overturn lead designs**; C-014
  recorded two lead designs overturned by an invited peer before
  implementation.

## The loop, end to end

Every substantial session runs one conductor procedure:

1. **Intake** — read `RUN_STATE.md` (the intake pointer), the task
   queue, the latest run report; never re-decide anything the decision
   log settled.
2. **Decompose** — split work into genuinely independent streams
   (disjoint expected diff footprints), one git worktree + branch each;
   assign each stream a review tier by *cost of being wrong*
   (measurement-semantics and contract-bearing work gets the full
   pipeline; docs get a light tier). Preflight gates: hardware-shaped
   streams require a confirmed device inventory; anything pinned
   without live validation carries a PROVISIONAL label; measurement
   sessions require a no-agent "quiet machine" lock.
3. **Per-stream pipeline** — for each reviewable unit: an invited
   design-argument round (the implementer must argue trade-offs before
   coding), implementation, then a layered review stack:
   2–3 fresh-instance counterreview lenses over the diff → lead triage
   with recorded dispositions → fixes → a dedicated test-amplification
   round (an independent writer adds edge-case tests) → a
   writer≠reviewer test audit (a fresh instance hunts tautological,
   vacuous, or wrong-expectation tests) → the lead's diff gate.
4. **Lead live gates** — never delegated: the lead runs the real flow
   (real corpus, real CLI, real hardware where present). This layer has
   repeatedly caught blockers no other layer saw, including defects
   whose own tests were green because the tests encoded the same wrong
   assumption as the code.
5. **Merge gate** — multi-commit series land as branch + PR. Before any
   merge: a pre-merge oversight pass by 2–3 fresh reviewers with
   distinct angles (deep regression hunt; claim-to-evidence trace;
   merge-order simulation across sibling PRs), lead triage, fixes, CI
   green. **Final-head rule:** any commit that lands after the last
   review round gets one more fresh review before merge — no commit
   merges unreviewed, however small (its first application caught a
   crash path in a "trivial" post-review fix).
6. **Integration review** — after parallel streams merge, one dedicated
   review hunts *interaction* defects no single-stream review can see.
   Its catches are definitionally unique (first outing: two).
7. **Bookkeeping** — a single session record (run report) with a
   verbatim process-trace appendix; the intake pointer and queue
   refreshed; a delegated docs-consistency sweep before the final
   commit (its latest pass found 15 real drift items; earlier passes
   found 5–6). Large documentation batches add the pre-commit
   docs-verify mode; the `consistency-sweep` skill owns that shape,
   including the D-043 supersession check.
8. **Same-session distillation** — lessons fold into the process
   playbooks the same session they are learned. Measured effect: one
   failure mode recurred five times before its fix was distilled, zero
   times after. The current operation-loop also runs its §0
   primary-deliverable check and §8 shipped-check before the session is
   considered done.
9. **Post-landing verification and close-out** — landed work gets the
   matching verification workflow with severity-tiered refuters. Sessions
   that change front-facing state refresh `docs/site/DRIFT.md`; no agent
   regenerates or deploys the site. Automation informs and Ed deploys
   manually, per D-068 and `RUN_STATE.md` end-of-work step 8.
10. **Meta-review (the final step)** — event-driven, not calendar-driven:
    when a review layer stops earning its keep, when an intervention
    repeats despite a folded fix, or when the user asks, the loop is
    reviewed with its own evidence discipline (see Topology for the
    consensus one such review produced). After large workloads the
    post-large-workload meta-reassessment (owned by operation-loop §10)
    always fires, and it runs LAST.

### Stop cards and paused work

When a session stops with live work in progress, the lead creates or
updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
that card is the single restart authority and overrides every lower
"what next" list, queue rank, mission guide, and run-report default.

A stop card must name:

- the resume authority and exact artifact pointer,
- the reason for stopping,
- worktrees, branches, PRs, and off-repo artifacts that must not be
  cleaned accidentally,
- status terms for each paused item,
- the first resume action, and
- the clearance criteria.

Use these status terms for paused work:

| Term | Meaning |
|---|---|
| `APPLIED_UNVERIFIED` | A worker reports code or docs are applied, but the lead has not gated the diff. Not merge-safe. |
| `LEAD_GATED` | The lead has reviewed and run the required local/live checks for the item. |
| `PR_OPEN_CI_GREEN` | A PR exists and CI is green, but merge authority has not yet fired. |
| `MERGED` | The accepted work has landed on main. |
| `UNREAD_UNADJUDICATED` | A report/synthesis exists but has not been consumed into decisions, queue rows, or rejected findings. |
| `ADJUDICATED` | Findings have explicit accept/reject/defer disposition and downstream artifacts are updated. |

Before an intentional pause, do the minimal stop sync even if full
bookkeeping cannot fit: update only `RUN_STATE.md`'s stop card and the
rank-0 queue row. That is enough to prevent accidental bypass.

## The artifact system (where rigor becomes auditable)

Each fact has exactly one home; everything else points at it:

| Artifact | Role |
|---|---|
| `docs/decision_log.md` | Binding design decisions, each with alternatives considered, consequences, and revisit conditions. The log is the count authority; nothing re-decides these silently. |
| `docs/council_log.md` | The deliberation record: review-council positions, reasoning exchanged, who prevailed, overridden dissents — so a future reader can reconstruct *why*, not just *what*. The log is the range/count authority. |
| `docs/contracts/` | Claim/evidence contracts: `claims_ladder.md` (D-037) plus `analysis_plans.md` (D-038) form the claim gate; strict validation is the evidence ticket. |
| `docs/stream_logs/` | Per-stream decision ledgers, committed WITH the code they justify: every non-trivial in-stream decision (`A-1..A-30`, `B-1..B-46`, …) with mandatory evidence pointers; wrong pins are SUPERSEDED in place, never erased. |
| `docs/run_reports/` | One record per working session: outcomes, verification evidence, a per-layer catch/yield table, the delegation-calibration ledger, restart instructions. |
| `docs/process/state_kernel.json` | Source of truth for work selection: active gates, dependencies, and machine-state lanes ([QUIET-MAC] / [AGENT] / [ED-EXTERNAL]). |
| `TASK_QUEUE.md` | Generated detailed queue projection plus dated history; do not hand-copy its live rows into reader docs. |
| `RUN_STATE.md` | Intake pointer with the generated restart projection. History lives in run reports. |
| `docs/risk_register.md` | Live risks with triggers and mitigation states. |

Instrumentation ledgers close the loop on the process itself:

- **Per-layer yield:** every review layer's unique catches are
  attributed and tallied per session under D-061 (C-027; replaces the
  earlier two-zero-sessions auto-drop, which the integration-review
  zero/zero/five sequence falsified): applicability is decided by
  PRE-DECLARED mechanical predicates; outcomes are classified
  accepted-unique-defect / duplicate / clean-verification /
  false-positive-suppression (suppression is not a catch); severity
  weights are fixed before the session; three applicable exposures
  TRIGGER an expected-loss review decision, never automatic deletion;
  safety/final-head/integration layers are never auto-dropped on
  zero-defect streaks. (One layer, the default specialist review lens, was
  dropped under the old rule before D-061.)
- **Delegation calibration:** every delegated unit gets a row — task
  altitude (pinned-spec / design-freedom / judgment-call), outcome
  (assigned by the lead after the gate, never self-labeled), catches,
  and lead rework minutes, with prompt-defects separated from
  model-defects. Delegation boundaries move on this evidence, not
  vibes. Current signal: pinned-spec delegation runs essentially
  defect-free; the serious defects cluster in volunteered additions and
  design-freedom wire contracts — which is exactly where the full lens
- **Invocation manifest:** substantial delegated/tool/skill runs get a
  lightweight manifest row per invocation. Minimum fields:
  `run_id`, `parent_report`, `role_or_lens`, `model`, `wrapper`,
  `session_id`, `prompt_sha256`, `prompt_path`, `output_path`, `status`,
  `consumed_by`, `disposition`, and `commit_or_pr`. Raw logs can stay
  out of git; every ephemeral artifact still needs a committed pointer
  row with `path`, `sha256` or stable id, `promoted_to`, and
  `not_promoted_reason`.

## Council discipline

Councils are expensive instruments. Use a full council for methodology,
measurement validity, schema/contract changes, claim boundaries, hardware
protocols, or explicit user requests. For ordinary implementation, use a
small number of targeted lenses plus lead adjudication.

Every high-impact council must leave a durable scorecard:

- unique catches by severity,
- accepted/rejected/deferred/false-positive counts,
- lead triage and rework time when practical,
- shipped artifacts,
- queue rows created or re-ranked,
- decision-log IDs promoted, and
- a disposition table: finding → ruling → owner → artifact/queue/decision
  target → closure check.

Deferred decision-log promotion is itself a tracked obligation, not
ambient prose in a report.

## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)

The following policy text is the R2-ratified section, landed verbatim per
audit work order WO-022 (`docs/reviews/2026-07-13-comprehensive-audit/`).

SPEND GUARDRAILS (capstone benchmark bands) — provisional calibration constants; review after two completed arcs; sunset at capstone submission.

1. ACCOUNTING SOURCE. Sol spend: `codex-usage` local accounting (the standing snapshot convention), corroborated by codex-run-v3 manifest `token_usage` rows where populated. The extraction window must cover the full arc — sum incremental snapshots for multi-day arcs; a single trailing-24h view is insufficient. Fable spend: estimated from local usage accounting; each snapshot names its method and price-table version. Price table v2026-07 (pinned until amended): GPT-5.6-sol $5/$30 per M in/out, cached input $0.50; Fable 5 $10/$50, cache reads $1. All figures are estimates, not billing truth, and are recorded as such. Missing data is recorded as `accounting_unknown`, never as zero.

2. DENOMINATOR AND CACHED-TOKEN TREATMENT. Token bands count total tokens (cached + uncached, all directions) exactly as codex-usage reports them — cached tokens are never excluded (exclusion invites cache-heavy gaming). Dollar figures apply cached pricing honestly. Cross-family aggregate ceilings bind in combined estimated dollars, because raw cross-family token sums are not commensurable (C-028: Sol ~180x the token volume, Fable ~3.4x the cost).

3. BOUNDARIES AND ATTRIBUTION. An arc = one council-log C-row, opened at its first delegated session, closed at its closeout snapshot. A work order = one WO/task id. Failed calls, retries, resumes, refuters, fix rounds, delta re-audits, lead usage, and subagents all count against the initiating WO and arc. Arcs and WOs may not be split, renamed, or reopened to reset counters.

4. BANDS. Each dimension is independent. SOFT crossing = record-and-continue: flag in the spend snapshot plus a one-line justification in the council row. HARD crossing = pause-and-ask Ed before any NEW delegated work in that category; in-flight sessions finish; quiet-machine measurement is never interrupted.

   | Scope | Soft | Hard |
   |---|---|---|
   | Sol high session | 6M tokens | 12M |
   | Sol xhigh session | 8M | 16M |
   | Sol ultra session | 40M | 60M |
   | Bench-effort WO | 10M / 3 Sol sessions / ~$40 combined | 20M / 6 / ~$80 |
   | Session-effort WO | 30M / 8 Sol sessions / ~$100 combined | 60M / 12 / ~$200 |
   | Arc | 100M / 25 Sol sessions / ~$400 combined / 6 Sol active-hours / 2 elapsed days | 200M / 40 / ~$800 / 12 h / 4 days |

   WO dollar figures are best-effort: when per-WO Fable attribution is accounting_unknown, the token/session pair binds. Ultra: at most 2 INTENDED ultra sessions per arc, each with a pre-run recorded statement of why xhigh is insufficient and what bounded subagent work it will perform; an unintended ultra is recorded as an anomaly and still counts.

   Calibration anchors (recorded so recalibration stays honest): healthy xhigh ≈ 2.3–3.5M tokens/session (C-030 post effort-fix; C-028 average); the recorded broken state averaged ~9M. C-028 (330.6M / 59 sessions / ~$1,050 / ~17.5h) crosses every substantive arc HARD dimension — it is the anti-example. The 2026-07-13 comprehensive audit (~30 Sol sessions + ~70 Fable agents, Ed-authorized) crosses arc SOFT on session count only — the intended "exceptional: justify and continue" outcome.

5. CHECKPOINTS (procedural; owner = the Fable lead). (a) At arc open: predeclare one accepted deliverable increment for the arc — a corpus/measurement result, analysis/figure/report increment, evaluator requirement, or cited advancement of a D-060 gate — and classify planned delegated work as deliverable-facing or process-facing (mixed sessions count as process-facing unless separately attributable). (b) Before each next delegated call: check the completed session against its tier band (a lightweight glance, not a full snapshot); no runtime killing is promised — evaluation happens on completed sessions before any resume, replacement, or new call. (c) At WO close and arc close: take the spend snapshot and evaluate all bands. One missed checkpoint blocks new process-facing delegation until reconciled.

6. DELIVERABLE-PROGRESS TRIPWIRE (binds while ANY D-060 gate is unmet). If process-facing combined estimated cost exceeds 33% of arc cost OR $250 — whichever occurs first — HARD pause-and-ask Ed before further process-facing delegation. Independently, an arc that closes with process-facing spend but NO accepted deliverable increment pauses further non-exempt process work even if the 33% threshold was not crossed.
## D-109: CAL-BRACKET-D079-01 F3 — A-min-with-reservation adopted (writer-enforced receipt ledger, reservation-first, repo-committed head pin); R1 ledger-authority and R2 prior-observation-set rulings

- Date: 2026-08-03
- Status: accepted (Ed ruling 2026-08-03: same explicit deferral to the
  joint magistrate + Sol position, same debate record. Arc: the fix
  investigation recommended A-min; Sol round 1 BROKE that formulation
  as stated (writer crash-window; prefix-subset is not anti-rollback)
  and recommended Option B for the timeline; magistrate round 2
  supplied the low-schedule-pressure record, the metrology-centric
  pivot, and the shared-R2 marginal-cost analysis; Sol WITHDREW B and
  converged on A-min-with-reservation, marginal cost Medium. Both
  soundness holes were lead-verified at the bench before adoption.)
- Applies to: `scripts/validate_powermetrics_fiducial.py` (sole
  production calibration writer), `joulewise/calibration_bracketing.py`,
  `joulewise/whole_window.py`, `scripts/run_campaign.py`,
  `configs/calibration/calibration_acceptance_d079_v2.json`, and every
  consumer construction of `AuthenticatedConsumptionSession`. This is
  a faithful IMPLEMENTATION of D-102 (no threshold/freshness
  amendment); it supplies the authority/universe rulings D-102 left
  silent. Lands with F1 + F2 as the single combined CAL-BRACKET fix
  round. Option B (signed narrowing amendment) is recorded as REJECTED
  fallback — coherent and honest, but it weakens the thesis instrument
  where the project has slack to build the sounder boundary.

**R1 — ledger authority, retention, anti-rollback (7 clauses):**
1. A canonical observation-receipt ledger and its append API are the
   SOLE authority for governed calibration observations. An off-ledger
   calibration artifact is invalid everywhere: as bracket endpoint,
   trigger evidence, derivation member, or claim evidence. Consumers
   enumerate ledger entries only, never caller-supplied directories.
2. RESERVATION-FIRST: every capture appends an authenticated `pending`
   attempt entry BEFORE hardware capture begins, and must finalize it
   as valid / systematic-invalid / ordinary-invalid / abandoned. Any
   unresolved pending, unfinalized, malformed, or conflicting entry
   causes claim evaluation to REFUSE. (Grounds, bench-verified: the
   writer creates capture state pre-receipt and has pre-manifest
   failure exits — a publish-on-return receipt misses exactly the
   crash/interrupt cases a completeness mechanism exists to catch.)
3. Receipts are immutable and hash-chained: sequence, predecessor,
   attempt id, content id, artifact hashes, six-field epoch, full T1,
   capture time, exact bound lexeme, disposition, custody locator.
4. The acceptance artifact pins its baseline ledger head. Evaluation
   ALSO requires the independent current-head pin (clause below),
   verifies one complete non-forked chain extension from baseline to
   current, and threads ONE immutable ledger snapshot through every
   consumer path (session, direct runner path, secondary verifier) —
   repeated independent loads are a refusal-grade defect.
   Anti-rollback authority: a REPO-COMMITTED head-pin file
   `{sequence, head_digest, ledger_schema}` (existing checked-in
   byte-pin trust model; no second trusted latest-sequence store).
   Rotation is epoch-bounded — at most one lead-controlled
   quiet-machine collection session — and NO claim evaluation may
   occur between ledger advancement and pin commit; a physical head
   differing from the committed pin refuses.
5. Ledger history is retained permanently. Referenced evidence remains
   in authenticated custody; missing or unverifiable required bytes
   cause refusal, never silent omission.
6. Version 1 is single-authority, single-machine. Remote/other-machine
   captures are invalid until imported through an authenticated ledger
   transaction; direct multi-machine append requires a new ruling.
7. Threat model, stated honestly and to be stated wherever A-min is
   described: the mechanism closes workflow omission, unregistered
   evidence, and rollback/stale-head consumption. It does NOT defend
   against a malicious trusted writer or an authority that rewrites
   both Git and ledger history. No stronger claim may be made.

**R2 — prior-observation set and prospective triggers (8 clauses):**
1. The issuance cutoff is an exact ledger sequence + head digest.
2. `derivation_corpus` remains exactly the n=19 threshold-producing
   observations.
3. `prior_observation_set` = every content-distinct governed
   observation known at the cutoff — valid, systematic-invalid,
   ordinary-invalid, blind holdout, and unresolved — with epoch and
   disposition recorded separately. (The current artifact's two
   ID-only `blind_exclusions` are insufficient and are superseded.)
4. Content identity is path-independent, derived from canonical
   primary-byte hashes; attempt identity is separate; copies do not
   create new observations.
5. "New" (trigger population) = current authentic content IDs −
   `prior_observation_set`, regardless of capture timestamp or source
   root; a previously unknown historical artifact IS new when
   discovered. Every new observation is judged under the PRIOR
   artifact (D-102's prospective rule).
6. New unresolved or unclassifiable attempts cause refusal; only after
   trigger disposition may a successor artifact absorb them.
7. The 32-valid/6-invalid same-epoch inventory is a backfill
   CANDIDATE, not a ratified classification: identities may seed the
   backfill, but dispositions require raw-physics + hash verification
   before issuance, and any unresolved member blocks issuance.
8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38
   TOTAL authenticated, content-distinct, VALID same-epoch
   observations — including previously blind observations once
   unblinded — not 38 post-cutoff observations. Under the candidate
   inventory, six further valid observations trigger re-derivation.

## D-110: Mint 1 retroactively NON-CLAIM-BEARING (taint-and-remint); RT-2 dependency edge minted; the night consult's 7B-mint license SUSPENDED

> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
> order is SUPERSEDED — structurally unsatisfiable at main (see
> `docs/process_traces/2026-08-06-d110-remint-fork/`); replaced by
> three prospective windows. The taint holding and the never-zero
> allowance correction STAND and bind the D-117 mints.
## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)

**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**

**What was written.**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).

**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.

**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.

**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.

## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired

**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
needed we need 3 more machine quiet nights and a lot of desk work",
with an explicit go to "execute all the deskwork" — read together with
his 2026-08-06 in-thread MVP-scope directive "a little more than just
decode, at least decode/prefill". His ruling moots a cold gate: apex
authority per rule 11.)
**Status:** ADOPTED. Full technical record:
`docs/process_traces/2026-08-06-d110-remint-fork/` (DIAGNOSIS: the
structural closure live-reproduced at `c537386`; Sol xhigh consult run
`20260806T165843Z-10884`; SYNTHESIS: magistrate concurrence).

1. **The D-110 clause-3 re-mint order (historical a10 consumption under
   the corrected selector) is SUPERSEDED.** The issued ledger holds only
   import-marked receipts; candidate discovery excludes imports by
   design; future live receipts cannot causally bracket past windows.
   The order is structurally unsatisfiable at main, not merely
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Complete D-117 freeze design: three prospective windows fit the envelope, but live-ledger sessions, multi-cell minting, and D-102 successor generation must land before any arm.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "dbb9685669ac76ea65bf458b78eeb98d94bc6a80",
    "head_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "upstream_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The current ledger cannot safely reserve both bookend observations under one unchanged committed head",
        "detail": "The append path requires the physical ledger head to equal the committed pin before each reservation. Finalizing the pre observation advances the physical head, so an ordinary post reservation cannot occur without an intervening pin advance or a new bracket-session capability.",
        "recommendation": "Implement an atomic two-slot bracket-session capability plus exact postcollection bracket binding before freezing arm packets."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The generalized mint is still decode-only and single-plan/single-cell",
        "detail": "The current generalized path hard-checks phase_energy_j.decode and a decode phase target. It cannot mint the two prefill riders or D-095's required combined multi-cell, multi-plan floor artifact.",
        "recommendation": "Introduce pinset v2 with per-plan component pins and an aggregate four-cell artifact pinset."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "No usable D-102 successor-artifact path exists for a live-prefixed ledger",
        "detail": "The issued acceptance artifact is exact-byte pinned and prior-set verification assumes the issuance corpus. A valid range-expanding live observation could therefore stop a campaign before member one or prevent its verdict.",
        "recommendation": "Pre-build and cold-gate a deterministic successor builder, registry, live-prefix verification, and trigger-time operator procedure."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "The referenced prefill-feasibility synthesis is absent at the inspected HEAD",
        "detail": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md does not exist in this worktree even though RUN_STATE says the trace was custodied.",
        "recommendation": "Recover or commit the trace before lead ratification; this memo uses D-117's adopted summary as authority."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Current queue rows still encode superseded C/D and D-110 gates",
        "detail": "TASK_QUEUE.md still presents MET-WINDOW-C-01 and MINT-GENERALIZE-01 under terminology and blockers superseded by D-117.",
        "recommendation": "Regenerate queue/state views from the owning state kernel after the plan-freeze decision is ratified."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main",
          "94a24e562290b59f7b40908315bbae7a032ea47e",
          "94a24e562290b59f7b40908315bbae7a032ea47e"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "94a24e562290b59f7b40908315bbae7a032ea47e$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "test -f docs/decision_log.md && test -f docs/process_traces/2026-08-06-d110-remint-fork/CONSULT-RESPONSE.md && test ! -e docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main advanced concurrently from dbb9685 to 94a24e5 during the read-only consult; the final state was re-inspected and remained clean.",
      "needs": "Freeze implementation scopes against 94a24e5 or a later explicitly reviewed head."
    },
    {
      "id": "FLAG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No suites were run because this was a read-only design consult with no implementation.",
      "needs": "Each implementation unit below carries focused and canonical-suite obligations."
    }
  ]
}
```

## Findings

### F1 — Live-ledger bookending is not yet armable (blocker)

D-116’s issued ledger is the correct trust root, and D-117 correctly requires fresh live pre/post observations. The obstacle is mechanical: the present append path requires the physical ledger head to match the committed pin when reserving an attempt. Once the pre observation is finalized, that equality no longer holds for an ordinary post reservation.

The best design is an atomic `calibration_window_bracket_session.v1` capability:

1. At the pre-bookend, under a clean committed head, append one receipt reserving exactly two immutable slots: `pre` and `post`, each with its attempt ID, plan ID/SHA, evidence-root ID, expected time role, and shared session ID.
2. Finalize the pre slot before member one.
3. Leave the post slot prospectively open without treating it as an unresolved candidate or permitting claim evaluation.
4. Finalize or explicitly abort the post slot at the closing bookend.
5. Commit the terminal ledger head once, then issue an exact `calibration_bracket_binding.v1` mapping the frozen plan and evidence root to the two finalized content/receipt digests.
6. Candidate discovery still examines the complete live candidate universe; the binding selects the claimed pair but cannot hide extra candidates.

This is preferable to a source commit after the pre observation: that would mutate the repository and readiness head inside every quiet-window procedure. Two ordinary reservations appended in advance are also inferior because the outstanding post reservation would look unresolved unless ledger semantics were widened anyway.

Base plans should freeze calibration retry count at zero. A failed pre observation aborts before member one and closes the unused post slot; a failed post makes the physical attempt non-claim-bearing. If the lead wants one cause-removal retry, the session capability needs additional prospectively numbered slots and deterministic selection semantics before freeze—never an improvised retry.

Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.

### F2 — The mint path needs a real v2, not another widened literal list (blocker)

The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:

- one plan and one artifact cell;
- `phase_energy_j.decode` only;
- `["phase","decode"]` only;
- no aggregate artifact over independently collected plans.

D-095 requires one multi-cell floor artifact whose 1.5B and 7B cells remain independently stack-scoped. D-117 adds prefill cells to both floor plans. The correct closure is therefore one four-cell artifact, not two loosely associated artifacts:

| Cell | Producer | Metric | Scientific family |
|---|---|---|---|
| 1.5B decode | 1.5B floor plan | `phase_energy_j.decode` | existing `df-ph-decode` |
| 1.5B prefill rider | 1.5B floor plan | `phase_energy_j.prefill` | new exact rider family |
| 7B decode | 7B floor plan | `phase_energy_j.decode` | D-085 `df-ph-decode-qwen25-7b` |
| 7B prefill rider | 7B floor plan | `phase_energy_j.prefill` | new exact rider family |

Each producer gets a component pinset; an aggregate pinset hard-checks both components and mints `d117-qwen25-phase-floor-set-v1`. Gamma consumes the two decode cells through D-095’s predeclared transport groups. It does not relabel contrast configs as floor configs.

### F3 — The D-102 successor packet is a pre-arm dependency (blocker)

A valid pre calibration can expand the observed range or approach the valid-observation limit. The issued artifact cannot absorb that live prefix today. The campaign therefore needs the following on disk and cold-gated before its first §5A arm:

- deterministic successor builder and validator;
- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
- generalized prior-set validation over a complete authenticated import-plus-live prefix;
- exact Decimal arithmetic, rounding, budget, prediction, and screen reproduction from D-079;
- a dry-run fixture that produces exact successor bytes and expected head pin;
- trigger-disposition logic that judges the range-expanding observation under the prior artifact before incorporating it into the successor;
- operator commands for pre-trigger and post-trigger branches.

I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.

At the pre bookend, a range expansion stops the chain before member one: close or preserve the bracket session according to the frozen state machine, commit the current ledger head, build and authenticate the successor, revalidate, then proceed. A post range expansion follows the same process after science but before the verdict. Systematic mismatch is a refusal, never something a successor can launder.

### F4 — Referenced trace missing (should-fix)

The named `docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md` is absent at `94a24e5`. D-117 itself records the adopted conclusion, so this memo treats the following as governing:

- floor prefill cells ride the floor-window decode members;
- gamma remains decode-only;
- the historical 128-token prefill contrast was marginal;
- a prospectively frozen 256-token contrast remains Ed’s option.

The missing trace prevents verification of any additional numerical assumptions it may contain. In particular, this memo does not freeze a 256-token runtime or effect-size target.

### F5 — Queue terminology is superseded (should-fix)

`TASK_QUEUE.md` still carries `MET-WINDOW-C-01`, prospective “C/D” splitting, and an old `MINT-GENERALIZE-01` D-110 blocker. Those rows cannot govern this work. D-117 clause 5 owns the namespace, and the live `RUN_STATE.md` block now recognizes that ruling. The queue should be regenerated after ratification, not manually interpreted during arm readiness.

### Ranked design decisions and rejected alternatives

1. **Use a two-slot ledger session capability and exact bracket binding.** Rejected: implicit reuse of neighboring observations, mid-window Git pin commits, or pre-reserving ordinary unresolved observations.

2. **Mint one four-cell floor artifact through pinset v2.** Rejected: two unrelated floor artifacts, summing arm floors, or weakening D-095’s independently stack-scoped maximum.

3. **Freeze zero calibration retries in the base plans.** Rejected: unbounded cause-removal retries and post hoc choice among observations. A retry-enabled variant requires a different capability state machine before freeze.

4. **Make prefill a metric rider over the exact decode members.** Rejected: copying the old dedicated 4096-prompt/64-output prefill workload, because that would add members and estimate a different condition. Post hoc extraction without a pre-registered cell is also insufficient.

5. **Treat the 256-token contrast as a fourth window plan.** Rejected: appending it to gamma later, which would change gamma’s plan SHA, member universe, order, multiplicity, runtime, and verdict basis.

6. **Use semantic immutable identifiers without dates or letters.** Rejected: `Window D`, C/D, and date-derived identities. Attempt dates belong in custody metadata, not scientific identity.

7. **Use a two-stage pin freeze.** Desk time freezes every knowable identifier, schema, member list, hash, and rule. Six-decimal operative values freeze only after governed collection and extraction. Rejected: placeholder literals presented as valid pins or any mint-time derivation.

### Proven template lineage

The templates are scientific and structural sources, not claim evidence.

| Plan | Files treated as the proven template | What is reused |
|---|---|---|
| 1.5B floor | `configs/campaigns/p2_015_floors/calibration_plan.json`; its SHA sidecar and generator; `02_phase_absolute/p2015-df-ph-decode-abs-r01.json` through `r10.json`; `05_phase_decode_abba/`’s forty decode configs and manifest; root `order_manifest.json`; `configs/floor_mint/a10_extraction_spec.json`; `configs/floor_mint/window_c_extraction_spec.json` | Exact Qwen2.5-1.5B stack identity, 10 absolute members, ten fixed A/B/B/A null blocks, runtime/config conventions, extraction shape |
| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
| Decode contrast | Entire `configs/campaigns/splitwise_decode_v1/`, particularly the plan, generator, forty configs, root/stage manifests, condition families, and `analysis_manifest_v3.json` | A=1.5B, B=7B, ten ABBA blocks, B−A orientation, v3 estimator and cross-stack floor rule |
| Operational references | `configs/campaigns/neg8_reference_corpus/` and the existing start/mid/end reference manifests | Twelve-member same-window NEG8 binding plus 3/1/3 references |

The old `02_phase_absolute/order_manifest.json` contains thirty interleaved decode, prefill, and short-prefill configs. It must not be copied as the new absolute manifest. Only its ten decode configs are the alpha source; the new ten-entry manifest is regenerated and independently hashed.

Historical results are diagnostic inputs only. No old evidence-root ID, calibration bracket, member output, or operative floor literal enters a prospective claim basis.

### Immutable identifier proposal

| Placeholder | Frozen plan ID | Evidence-root ID | Physical root |
|---|---|---|---|
| W-alpha | `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-1p5b-v1` | `runs_d117_floor_qwen25_1p5b_v1` |
| W-beta | `plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-7b-v1` | `runs_d117_floor_qwen25_7b_v1` |
| W-beta | `plan-d117-floor-qwen25-7b-decode-p128-prefill-rider-v1` | `evidence-d117-floor-qwen25-7b-v1` | `runs_d117_floor_qwen25_7b_v1` |
| W-gamma | `plan-d117-contrast-qwen25-1p5b-vs-7b-decode-v1` | `evidence-d117-contrast-qwen25-1p5b-vs-7b-v1` | `runs_d117_contrast_qwen25_1p5b_vs_7b_v1` |

Each also gets a separately named bound root ending in `_bound`. Failed physical attempts receive custody attempt suffixes outside the scientific ID; the clean evidence root is never silently reused.

### Common order-manifest contract

Every root manifest should bind:

- plan ID, exact plan SHA, generator SHA, and model/runtime revisions;
- ordered stage records with exact stage-manifest ID, SHA, expected member count, predecessor, and successor;
- exact relative config paths and config SHAs—no globs or directory discovery;
- ordinal, member ID, ABBA block and slot where applicable;
- fixed reference and NEG8 manifests;
- the prefill rider mapping for floor members;
- frozen attempt policy, including zero calibration retries and no outcome-driven top-ups;
- evidence-root ID and expected fresh physical path;
- hashes of condition families, extraction spec, and analysis manifest;
- arm-time attachment slots for the readiness record, session capability, and actual receipt identifiers without modifying frozen plan bytes.

An ABBA stage manifest records each block as `A1,B1,B2,A2`. Splitting blocks 1–5 and 6–10 around the midpoint reference does not reset block numbering.

### Per-window plans

#### Alpha — 1.5B decode floor plus prefill rider

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize reserved `pre` slot before science |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Absolute floor | 10 | `abs-r01` through `abs-r10` |
| Null half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Null half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize reserved `post` slot |
| Closeout | 0 science members | Terminal head pin, bracket binding, verdict, dual-root backup |

Science count is 50; operational captures are 12 bound, 7 references, and 2 calibrations. The prefill rider adds no member and no runtime.

The rider is a new condition family over the same 128-prompt/512-output decode bundles. It must pre-register `phase_energy_j.prefill`, phase precheck `["phase","prefill"]`, exact tokenizer/model/config identity, the same ten absolute members and forty null members, its estimator, n=10 block basis, and both absolute and comparative floor rules. It is not the old dedicated prefill condition.

The extraction spec contains four cells: decode absolute, decode comparative, prefill absolute, and prefill comparative. It names 100 cell-member references but exactly 50 unique bundles. Each cell supplies an exact member list, config hash list, expected n, condition-family hash, metric key, phase precheck, order-manifest pin, calibration basis, and evidence-root ID. Missing prefill phases, fallback values, or member discovery outside the list are fatal.

#### Beta — 7B decode floor plus prefill rider

The schedule is identical to alpha: pre calibration; 12 NEG8; start 3; absolute 10; ABBA blocks 1–5; midpoint 1; blocks 6–10; end 3; post calibration.

The decode condition remains D-085’s `df-ph-decode-qwen25-7b`; the fresh plan does not rename settled scientific semantics. The new prefill-rider family pins `phase_energy_j.prefill` over the exact 7B decode members and stack revision.

Its extraction contract is the same four-cell/50-unique-bundle shape as alpha. Old 7B values—absolute 6.294380… J and comparative 13.998036… J—are budget/design diagnostics only and are not pre-registered pins.

#### Gamma — 1.5B-versus-7B decode contrast

| Stage | Members | Order |
|---|---:|---|
| Pre calibration | 1 live observation | Finalize `pre` slot |
| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
| Start references | 3 | Frozen triplet |
| Contrast half 1 | 20 | ABBA blocks 1–5 |
| Midpoint reference | 1 | Frozen midpoint |
| Contrast half 2 | 20 | ABBA blocks 6–10 |
| End references | 3 | Frozen triplet |
| Post calibration | 1 live observation | Finalize `post` slot |
| Closeout | 0 science members | Pin, binding, verdict, backup, then analysis |

The frozen manifest remains decode-only:

- A is the exact 1.5B stack; B is the exact 7B stack.
- Metric is exactly `phase_energy_j.decode`.
- Estimand orientation is B−A.
- Design is ten A/B/B/A blocks, n=10 block estimates.
- Estimator is `abba_block_arm_mean_difference_t_v1`.
- Test is two-sided at family alpha 0.05, with the positive direction stated as the scientific hypothesis rather than used to change the test.
- `equivalence_margin` and `mde` remain null unless prospectively ruled otherwise.
- Floor rule remains `cross_stack_armwise_max.v1`: independently resolve the 1.5B and 7B decode cells and take their maximum, never their sum.
- Claim-side anchor bounds remain separate from the detection-floor operation.
- The finalized analysis basis pins the exact forty member paths, config hashes, stack identities, floor artifact bytes, calibration binding, and evidence root.

### Runtime evidence and budgets

Historical evidence in `docs/phase_2/splitwise_decode_campaign.md` §4 supplies:

- 1.5B decode member: 92.7 s, measured n=40;
- 1.5B reference member: 90.5 s, measured n=7;
- 7B decode member: approximately 97 s from the measured/probed anchor;
- 1.5B/7B mixed ABBA half: about 31.6 min raw member time.

The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.

| Component, minutes | Alpha | Beta | Gamma |
|---|---:|---:|---:|
| Pre calibration bracket | 8 | 8 | 8 |
| 12 NEG8 bound members | 22 | 22 | 22 |
| Bound evaluation | 1 | 1 | 1 |
| Start 3 references | 8 | 8 | 8 |
| Absolute 10 | 19 | 20 | — |
| ABBA blocks 1–5 | 34 | 36 | 35 |
| Midpoint reference | 5 | 5 | 5 |
| ABBA blocks 6–10 | 34 | 36 | 35 |
| End 3 references | 8 | 8 | 8 |
| Post calibration bracket | 8 | 8 | 8 |
| Campaign subtotal | 147 | 152 | 130 |
| Untouched pre-arm idle | 10 | 10 | 10 |
| Base occupancy | 157 | 162 | 140 |
| With 20% failure margin | **188.4** | **194.4** | **168.0** |
| Hours | **3.14 h** | **3.24 h** | **2.80 h** |
| 2–4 h envelope | Pass | Pass | Pass |

The margin is time headroom, not authority to add members, replace a cap-hit observation, or top up an unfavorable result. The fixed manifest and frozen failure policy decide scientific validity.

### §5A operator bookends

Before each window:

1. Verify the reviewed plan/readiness record, fresh empty roots, model artifacts, charger/AC state, power policy, OS/tool identity, empty waiver set, and current acceptance artifact.
2. Verify the physical ledger head equals the authenticated committed pin.
3. Correct the clock against the trusted source, record the correction and `usingnetworktime` state, turn network time off, and settle for at least 180 seconds.
4. Establish zero-agent/zero-output-streaming conditions and complete ten untouched minutes of daemon idle.
5. Append the exact two-slot bracket session capability.
6. Capture and finalize the pre observation; run the acceptance and D-102 trigger probe.
7. Only after every gate is green, emit the one-line arm message and walk away.

At the closing bookend:

1. Capture the post observation before changing power, network-time, or workload state.
2. Finalize the post slot or write the governed failure/abort closure.
3. Commit and authenticate the terminal ledger head.
4. Emit the exact bracket binding and whole-window verdict from one immutable ledger snapshot.
5. Back up evidence and bound roots with verified return code and hashes.
6. Restore network time and record the restoration only after measurement completion and custody closeout.

### Prefill floor claim eligibility

A rider is claim-eligible only if desk freeze already binds:

- exact metric and phase path;
- exact workload parameters, model/tokenizer revision, seeds, quantization, runtime, sampling, and telemetry mode;
- absolute and comparative member lists and order manifests;
- exact condition-family ID and hash;
- n and estimator;
- calibration cell, acceptance artifact role, and D-110 allowance rule;
- extraction failure behavior;
- allowed consumer families.

For each metric, the operative floor is the maximum of independently evaluated absolute and comparative components. Apply D-110 once as `A_s = max(observed_drift, 0.010818)`. Never sum components and never borrow a decode floor for prefill.

### Two-stage mint freeze

**Desk-frozen pin requirements**

For each floor plan, freeze:

- plan ID, declared SHA, sidecar SHA, and actual artifact SHA;
- evidence-root ID;
- four intended cell roles across the two plans;
- condition-family IDs/hashes;
- metric and phase-precheck paths;
- absolute and comparative order-manifest IDs/hashes;
- extraction-spec SHA and exact members;
- expected counts;
- model/runtime/config hashes;
- calibration acceptance artifact ID/SHA/derivation rule;
- D-110 never-zero allowance rule;
- aggregate artifact ID and transport allowlists.

These live in a non-mintable `pin_requirements.v2` artifact. Unresolved values must be structurally absent or explicitly marked unresolved; the file cannot satisfy the final pinset schema.

**Postcollection-frozen pins**

After passed verdicts and governed extraction, freeze separately for each of the four cells:

- absolute and comparative evaluation-basis SHA/count;
- exact accepted pre/post receipt and content digests;
- bracket-binding SHA and terminal ledger head;
- observed drift and applied allowance;
- extraction-report SHA;
- absolute, comparative, and operative values;
- the operative literal formatted independently as exactly six decimals using the repository’s `.6f` convention.

The lead independently recomputes each six-decimal literal from primary extraction bytes. The mint only compares supplied literals and hashes; it does not calculate them. The old `7.377086` literal is never reused.

Gamma has no producer mint. Its consumer pinset instead binds the exact combined floor artifact bytes, the two decode-cell IDs, its plan/order/analysis manifests, and its finalized evaluation basis.

### Synthetic three-window live-ledger regression

The fixture begins with the exact issued-ledger semantics: 76 receipts, including 38 historical import observations—30 valid, 2 systematic, 6 ordinary-invalid. Candidate discovery must exclude every import-marked observation.

The no-failure live extension adds three bracket capabilities and six finalized live observations. From one immutable final snapshot, the regression must prove:

- exactly six live candidates and zero imported candidates;
- alpha, beta, and gamma each bind only their own pre/post pair;
- all six are same-epoch, causal, fresh, within protocol and T1 limits;
- no neighboring endpoint can substitute for a bound endpoint;
- all three verdicts use the same complete candidate universe;
- the ideal terminal sequence is 85 under the proposed three-receipt session model;
- the D-110 never-zero allowance remains active.

Required refusal vectors:

- import-marker removal, import leakage, or candidate-discovery regression;
- missing, duplicate, reordered, or conflicting session/finalization receipts;
- open or abandoned session without a governed closure;
- physical-head/pin mismatch, rollback, fork, or uncommitted terminal head;
- omitted, added, duplicated, off-ledger, or content-substituted observations;
- missing, tampered, swapped, or cross-window bracket binding;
- noncausal endpoint, stale endpoint, T1 failure, protocol failure, or epoch mismatch;
- systematic classification;
- one range-expanding live observation requiring a successor;
- the observation-count boundary reaching the D-102 limit;
- a successor whose prior set omits or changes an authenticated prefix.

### Optional 256-token prefill contrast

Clean attachment inside frozen gamma is impossible. Adding the arm changes the workload, metric family, members, order, runtime, multiplicity, plan digest, evidence root, and verdict basis.

If Ed adopts it, create a fourth independently frozen, independently calibrated plan and evidence root. It may attach later only in a higher-level synthesis/claim packet that references gamma and the new prefill result as sibling artifacts. Gamma’s bytes remain unchanged.

The floor riders here use the prefill phase of the 128-prompt decode workload. They do not automatically transport to a prospectively defined 256-token contrast. The fourth plan needs either exact matching prefill floor cells or a separately predeclared and justified transport rule. No placeholder members or plan ID should be added to gamma now.

### Freeze order and lead gates

1. **Ruling gate:** lead accepts the session-capability semantics, zero-retry policy, successor corpus rule, four-cell artifact shape, and fourth-window treatment.
2. **Toolchain gate:** ledger session/binding, successor builder, pinset v2, multi-cell mint, prefill metric support, and three-window regression all land and pass focused plus canonical suites.
3. **Desk freeze gate:** generate all three campaign packs; freeze identifiers, model revisions, configs, manifests, condition families, extraction/analysis specs, budgets, failure policy, and hashes. Six-decimal values do not yet exist.
4. **Per-window arm gate:** attach current clean head, acceptance artifact, physical/committed ledger equality, fresh roots, exact environment preflight, empty waivers, §5A evidence, and bracket-session identifiers.
5. **Pre-science trigger gate:** finalize the pre observation and either accept it, issue a governed successor, or abort before member one.
6. **Post-window gate:** finalize post, commit terminal head, issue bracket binding, verdict, and verified backup.
7. **Floor mint gate:** after alpha and beta pass, run governed four-cell extraction, independently freeze literals, mint the combined artifact, and require `validate_floor_artifact` to return no findings.
8. **Gamma claim gate:** pass the whole-window verdict, finalize the v3 basis, run D-093 root scanning, resolve both decode arm floors from exact combined-artifact bytes, and apply the armwise maximum.

### Work-order list with enforced WRITE_SCOPE units

| Unit | Exact write scope | Invariants and tests | Dependency |
|---|---|---|---|
| U1 — ledger session and binding | `joulewise/calibration_ledger.py`; `joulewise/calibration_bracketing.py`; `scripts/reserve_calibration_window_bracket.py`; `tests/test_calibration_ledger.py`; `tests/test_calibration_bracketing.py` | Two immutable slots, one-use finalization, governed abort, no unresolved-candidate leakage, exact binding, head/pin refusals. Focused ledger/bracketing tests plus full suite. | Foundation; independent of U3 |
| U2 — D-102 successor engine | `joulewise/calibration_bracketing.py`; `scripts/build_calibration_acceptance_successor.py`; `configs/calibration/calibration_acceptance_registry.json`; `tests/test_calibration_acceptance_successor.py` | Complete authenticated live prefix, deterministic bytes, parent ancestry, exact Decimal derivation, range/count triggers, systematic refusal. Focused cold-gate fixtures plus full suite. | Sequential after U1 because of shared bracketing semantics |
| U3 — pinset v2 and multi-cell mint | `scripts/mint_floor_artifact_generalized.py`; `scripts/floor_mint_pinsets/schema_v2.json`; `joulewise/detection_floor.py`; `tests/test_mint_floor_artifact_generalized.py` | Decode and prefill metrics, per-plan component pins, aggregate four-cell pins, no derived literals, no cross-stack sum, v1 compatibility. Focused parity/refusal tests plus full suite. | Independent of U1/U2 |
| U4 — three-window ledger regression | `tests/fixtures/calibration_live_three_window/**`; `tests/test_calibration_live_three_window.py` | Exact issuance fixture, import exclusion, six live candidates, three causal bindings, successor and refusal vectors. | After U1 and U2 |
| U5 — alpha campaign pack | `configs/campaigns/d117_floor_qwen25_1p5b_v1/**`; `configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json`; `tests/test_d117_floor_qwen25_1p5b_plan.py` | Exact 10+40 schedule, split midpoint, two metric riders, 50 unique bundles, fresh IDs, deterministic regeneration. | After U3 schema/IDs freeze; parallel with U6 |
| U6 — beta campaign pack | `configs/campaigns/d117_floor_qwen25_7b_v1/**`; `configs/floor_mint/d117_qwen25_7b_extraction_spec.json`; `tests/test_d117_floor_qwen25_7b_plan.py` | Same as U5, retaining D-085 stack/family identity. | After U3; parallel with U5 |
| U7 — gamma campaign pack | `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/**`; `tests/test_d117_decode_contrast_plan.py` | Forty ABBA members, decode-only metric, B−A orientation, v3 estimator, exact four-cell artifact consumer pins, no prefill placeholder. | After U3 floor cell/transport IDs freeze |
| U8 — operator/readiness packet | `docs/phase_2/window_runbook.md`; `scripts/validate_frozen_plan_readiness.py`; `tests/test_frozen_plan_readiness.py` | §5A sequence, session capability, pre-trigger successor gate, fresh roots, empty waivers, terminal binding/pin/backup. | After U1, U2, U5–U7 |
| U9 — state and custody bookkeeping | `docs/process/state_kernel.json`; `RUN_STATE.md`; `TASK_QUEUE.md`; `CLAIMS_STATUS.md`; `docs/run_reports/2026-08-07-d117-plan-freeze.md` | D-117 vocabulary, no C/D plan references, exact frozen digests, generated-view consistency. | Lead-owned, after all desk artifacts pass |
| U10 — postcollection pin closure | `scripts/floor_mint_pinsets/d117_qwen25_1p5b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_7b_v2.json`; `scripts/floor_mint_pinsets/d117_qwen25_phase_floor_set_v2.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.json`; `results/floor_artifacts/d117_qwen25_phase_floor_set_v1.sha256` | Only postcollection facts; independent literal recomputation; exact receipt/binding/head pins; validator returns no findings. | Sequential after alpha and beta pass |

Every unit should run its focused tests and `python3 -m unittest discover -s tests`. Shared files make U1→U2 sequential; U1 and U3 can proceed independently. U5 and U6 can proceed independently after U3 freezes the vocabulary. U7 waits for final floor-cell and transport identifiers. U10 is deliberately absent from the desk freeze.

### What the lead should double-check

- Recover the missing prefill-feasibility trace and compare its exact 256-token assumptions with this fourth-window conclusion.
- Ratify the two-slot ledger capability against D-109/D-116, especially whether an open post slot may exist during the pre-science successor probe.
- Decide explicitly between zero calibration retries and a prospectively numbered retry-capability variant.
- Ratify the D-102 successor corpus rule: all content-distinct valid same-epoch observations through the cutoff.
- Confirm that D-085’s 7B decode family ID is preserved and contrast transport uses allowlists rather than relabeling configs.
- Confirm pinset v2 supports multiple producer plans while preserving byte-for-byte v1 behavior.
- Verify the 20% allowance does not become permission for member replacement or result-driven top-up.
- Recheck full model revisions, local artifact hashes, runtime version, charger identity, and post-move environment at each arm.
- Independently calculate all four `.6f` operative literals from primary extraction bytes.
- Verify every one of the fifty floor bundles actually contains the registered prefill phase; a missing phase must fail extraction.
- Ensure gamma takes the maximum of the two decode arm floors, never their sum, and retains separate claim-side anchor bounds.
- Ensure the 128-prompt prefill riders are not presented as a floor for a later 256-token contrast without exact transport evidence.
- Regenerate the active queue from the state kernel so superseded C/D and D-110 gates cannot be mistaken for arm authority.
- Freeze against the final reviewed repository head; this consult began at `dbb9685` and ended cleanly at concurrently advanced `94a24e5`.

## Residual risk

No live timings, calibration observations, successor generation, or mint replay were performed. Runtime estimates therefore inherit historical-machine variance; the 20% margin is the current mitigation.

The absent feasibility synthesis limits review of the optional 256-token arm. Its attachment architecture is sound, but its member count, runtime, estimand, and floor transport remain intentionally unfrozen.# D-117 plan-freeze design — magistrate ratification (2026-08-07, ruling gate 1)

Sol xhigh design memo (this directory) ACCEPTED with the following
rulings; the memo's freeze-order gates 1-8 are adopted as the campaign
gate structure.

1. **Two-slot ledger bracket-session capability + exact postcollection
   bracket binding** — ACCEPTED (F1 closure shape; alternatives
   rejected as the memo argues). U1 implements; ratify-vs-D-109/D-116
   check rides U1's review gate.
2. **Zero calibration retries in the base plans** — ACCEPTED. A
   retry-enabled variant is NOT built now; if a night dies on a
   removable cause, the fresh attempt is a new custody attempt of the
   same frozen plan.
3. **D-102 successor engine (U2) is COLD-GATED before first arm** — the
   successor corpus rule (all content-distinct valid same-epoch
   observations through the cutoff) is provisionally accepted, final
   ratification at the U2 rule-11 gate.
4. **One combined four-cell floor artifact via pinset v2** — ACCEPTED
   (decode+prefill × 1.5B+7B; armwise max, never sum; v1 byte-parity
   preserved).
5. **256-token prefill contrast = fourth independent window plan,
   never attached to gamma** — ACCEPTED; remains Ed's open option;
   floor riders do NOT auto-transport (needs exact transport rule).
6. **Identifiers** — ACCEPTED as proposed (plan-d117-*/evidence-d117-*/
   runs_d117_* scheme).
7. **Two-stage pin freeze** — ACCEPTED; the lead independently
   recomputes every six-decimal operative literal from primary
   extraction bytes at U10.

Execution: U1 & U3 launch first (independent), then U2 (after U1),
U4 (after U1+U2), U5-U7 packs (after U3), U8 readiness, U9 lead
bookkeeping, U10 post-collection only. All units: enforced WRITE_SCOPE,
implement→review→delta gauntlet, lead commits.

Deviation note (Ed's fast-mode directive): implementation units run via
codex-run-v3 (standard tier) because WRITE_SCOPE ENFORCEMENT and the
audit envelope outweigh the fast tier for invariant-bearing code;
fast-mode is used for all read-only/ideation work this session.

exec
/bin/zsh -lc "git diff --unified=80 -- joulewise/calibration_ledger.py; nl -ba scripts/reserve_calibration_window_bracket.py | sed -n '1,320p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
diff --git a/joulewise/calibration_ledger.py b/joulewise/calibration_ledger.py
index 7e1da81..00ec8df 100644
--- a/joulewise/calibration_ledger.py
+++ b/joulewise/calibration_ledger.py
@@ -1,441 +1,680 @@
 """Authenticated calibration-observation receipt ledger (D-109).
 
 The ledger closes workflow omission, unregistered evidence, and rollback or
 stale-head consumption.  It does not defend against a malicious trusted
 writer or an authority that rewrites both Git and the complete ledger
 history.  Version 1 is deliberately a single-authority, single-machine
 protocol.
 
 Each capture is represented by two immutable hash-chained receipts: a
 reservation with disposition ``pending`` written before capture state exists,
 then exactly one finalization.  Evaluation consumes one frozen snapshot whose
 physical head must equal the repository-committed head pin.
 """
 
 from __future__ import annotations
 
 import fcntl
 import hashlib
 import json
 import os
 import re
 import stat
 import subprocess
 import tempfile
 from collections.abc import Mapping, Sequence
 from dataclasses import dataclass
 from pathlib import Path
 from types import MappingProxyType
 from typing import Any, BinaryIO
 
 from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
 
 
 LEDGER_SCHEMA = "joulewise.calibration_observation_ledger.v1"
 RECEIPT_SCHEMA = "joulewise.calibration_observation_receipt.v1"
+BRACKET_SESSION_SCHEMA = "joulewise.calibration_window_bracket_session.v1"
+BRACKET_SESSION_OPEN_EVENT = "bracket-session-open"
+BRACKET_SESSION_FINALIZATION_EVENT = "bracket-session-slot-finalization"
+BRACKET_SESSION_ABORT_EVENT = "bracket-session-abort"
+BRACKET_SESSION_SLOTS = ("pre", "post")
 HISTORICAL_IMPORT_TABLE_SCHEMA = (
     "joulewise.calibration_historical_import_table.v1"
 )
 HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA = (
     "joulewise.calibration_historical_import_custody_manifest.v1"
 )
 HISTORICAL_IMPORT_EVENT_PREFIX = "historical-import-v1"
 HISTORICAL_IMPORT_RESERVATION_EVENT = (
     f"{HISTORICAL_IMPORT_EVENT_PREFIX}-reservation"
 )
 HISTORICAL_IMPORT_FINALIZATION_EVENT = (
     f"{HISTORICAL_IMPORT_EVENT_PREFIX}-finalization"
 )
 GENESIS_DIGEST = "0" * 64
 REPO_ROOT = Path(__file__).resolve().parents[1]
 DEFAULT_LEDGER_PATH = REPO_ROOT / "runs" / "calibration_observation_ledger.jsonl"
 DEFAULT_HEAD_PIN_PATH = (
     REPO_ROOT / "configs" / "calibration" / "calibration_ledger_head.json"
 )
 
 IDENTITY_EPOCH_FIELDS = (
     "os_build",
     "hardware_model",
     "power_policy",
     "sampling_interval_ms",
     "estimator_revision",
     "pulse_protocol_id",
 )
 T1_FIELDS = tuple(V2_BINDING_FIELDS)
 FINAL_DISPOSITIONS = frozenset(
     {"valid", "systematic-invalid", "ordinary-invalid", "abandoned"}
 )
 HISTORICAL_IMPORT_DISPOSITIONS = frozenset(
     {"valid", "systematic-invalid", "ordinary-invalid"}
 )
 ALL_DISPOSITIONS = FINAL_DISPOSITIONS | {"pending"}
 CONTENT_ID_ARTIFACTS = (
     "instrument_evidence.json",
     "manifest.json",
 )
 GOVERNED_ARTIFACTS = (
     "raw/powermetrics.plist",
     "events.jsonl",
     "power_trace.csv",
     "instrument_evidence.json",
     "manifest.json",
 )
 MANIFEST_BOUND_ARTIFACTS = tuple(
     name for name in GOVERNED_ARTIFACTS if name != "manifest.json"
 )
 EVIDENCE_BOUND_ARTIFACTS = (
     "raw/powermetrics.plist",
     "events.jsonl",
     "power_trace.csv",
 )
 _SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
 
 # Stable refusal taxonomy.  Consumers propagate these exact spellings into
 # claim barriers; no malformed or unresolved history is silently omitted.
 REFUSAL_TAXONOMY: Mapping[str, str] = MappingProxyType(
     {
         "calibration_ledger_missing": "the pinned non-genesis ledger is absent",
         "calibration_ledger_malformed": "ledger, receipt, or head-pin schema is malformed",
         "calibration_ledger_chain_conflict": "sequence or predecessor linkage is not one linear chain",
         "calibration_ledger_attempt_conflict": "an attempt has duplicate or conflicting state transitions",
+        "calibration_ledger_bracket_session_conflict": "a bracket session has duplicate, reordered, or conflicting state transitions",
+        "calibration_ledger_bracket_session_open": "a bracket session has not finalized both slots or recorded a governed abort",
         "calibration_ledger_content_conflict": "one content identity has conflicting authenticated classifications",
         "calibration_ledger_pending": "at least one reservation is unresolved",
         "calibration_ledger_head_uncommitted": "the head pin differs from the Git HEAD bytes",
         "calibration_ledger_head_mismatch": "the physical head differs from the committed pin",
         "calibration_ledger_rollback": "the physical ledger is a proper prefix of the pinned head",
         "calibration_ledger_baseline_missing": "the acceptance cutoff is not in the current chain",
         "calibration_ledger_custody_invalid": "receipt-bound evidence bytes are absent or hash-invalid",
         "calibration_ledger_snapshot_required": "claim evaluation did not receive one immutable snapshot",
         "calibration_ledger_off_ledger_artifact": "a calibration artifact is not registered in the snapshot",
         "calibration_observation_unclassifiable": "a governed observation has no ruled disposition",
     }
 )
 
 
 class CalibrationLedgerError(ValueError):
     """A writer-side ledger operation cannot preserve the D-109 contract."""
 
 
 def _jsonable(value: Any) -> Any:
     if isinstance(value, Mapping):
         return {key: _jsonable(item) for key, item in value.items()}
     if isinstance(value, (list, tuple)):
         return [_jsonable(item) for item in value]
     return value
 
 
 def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
     return json.dumps(
         _jsonable(value),
         sort_keys=True,
         separators=(",", ":"),
         ensure_ascii=False,
         allow_nan=False,
     ).encode("utf-8")
 
 
 def canonical_sha256(value: Mapping[str, Any]) -> str:
     return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
 
 
 def _is_sha256(value: object) -> bool:
     return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None
 
 
 def _normalized_vector(
     value: Mapping[str, Any] | None,
     fields: Sequence[str],
 ) -> dict[str, Any]:
     source = value if isinstance(value, Mapping) else {}
     return {field: source.get(field) for field in fields}
 
 
 def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
     """Return the path-independent identity of canonical primary bytes.
 
     The authenticated evidence document and its manifest are the canonical
     byte pair.  A copied custody tree therefore retains the same identity.
     Other receipt hashes remain custody checks but do not manufacture a new
     observation when a derived representation is regenerated.
     """
 
     identity = {
         name: artifact_sha256.get(name) for name in CONTENT_ID_ARTIFACTS
     }
     if any(not _is_sha256(value) for value in identity.values()):
         return None
     return canonical_sha256(identity)
 
 
 def artifact_hashes(custody_dir: Path) -> dict[str, str]:
     """Hash every governed artifact present in one finalized custody tree."""
 
     root = Path(custody_dir)
     result: dict[str, str] = {}
     for relative in GOVERNED_ARTIFACTS:
         path = root / relative
         if path.is_file():
             result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
     return result
 
 
 def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
     return {key: value for key, value in receipt.items() if key != "receipt_digest"}
 
 
 def _receipt_digest(receipt: Mapping[str, Any]) -> str:
     return canonical_sha256(receipt_core(receipt))
 
 
 @dataclass(frozen=True)
 class LedgerObservation:
     sequence: int
     receipt_digest: str
     attempt_id: str
     content_id: str | None
     artifact_sha256: Mapping[str, str]
     identity_epoch: Mapping[str, Any]
     t1_bindings: Mapping[str, Any]
     capture_wall_time_s: str | None
     exact_bound_lexeme_s: str | None
     disposition: str
     custody_locator: str
     observation_kind: str = "live-capture"
+    bracket_session_id: str | None = None
+    bracket_slot: str | None = None
+    bracket_window_id: str | None = None
+    bracket_plan_id: str | None = None
+    bracket_plan_sha256: str | None = None
+    bracket_evidence_root_id: str | None = None
 
     @property
     def classification_disposition(self) -> str:
         """Map the writer terminal state onto the R2 observation schema."""
 
         return (
             "unresolved" if self.disposition == "abandoned" else self.disposition
         )
 
     @property
     def is_historical_import(self) -> bool:
         return self.observation_kind == "historical-import"
 
 
 @dataclass(frozen=True)
 class CalibrationLedgerSnapshot:
     """One immutable, fully checked view threaded through an evaluation."""
 
     ledger_schema: str
     ledger_path: Path
     head_sequence: int
     head_digest: str
     receipts: tuple[Mapping[str, Any], ...]
     observations: tuple[LedgerObservation, ...]
     refusal_reasons: tuple[str, ...]
+    bracket_sessions: tuple["CalibrationBracketSession", ...] = ()
     baseline_sequence: int | None = None
     baseline_digest: str | None = None
+    committed_head_sequence: int | None = None
+    committed_head_digest: str | None = None
 
     @property
     def valid(self) -> bool:
         return not self.refusal_reasons
 
     @property
     def observation_by_attempt(self) -> Mapping[str, LedgerObservation]:
         return MappingProxyType(
             {observation.attempt_id: observation for observation in self.observations}
         )
 
+    @property
+    def bracket_session_by_id(self) -> Mapping[str, "CalibrationBracketSession"]:
+        return MappingProxyType(
+            {session.session_id: session for session in self.bracket_sessions}
+        )
+
+    @property
+    def is_governed_open_bracket_extension(self) -> bool:
+        """Whether the physical/pin gap is exactly one reserved open session."""
+
+        allowed = {
+            "calibration_ledger_bracket_session_open",
+            "calibration_ledger_head_mismatch",
+        }
+        if (
+            set(self.refusal_reasons) != allowed
+            or self.committed_head_sequence is None
+            or self.committed_head_digest is None
+        ):
+            return False
+        open_sessions = [
+            session for session in self.bracket_sessions if session.state == "open"
+        ]
+        if len(open_sessions) != 1:
+            return False
+        session = open_sessions[0]
+        if session.capability_sequence != self.committed_head_sequence + 1:
+            return False
+        tail = self.receipts[self.committed_head_sequence :]
+        return bool(
+            tail
+            and tail[0].get("event") == BRACKET_SESSION_OPEN_EVENT
+            and tail[0].get("predecessor_digest") == self.committed_head_digest
+            and all(row.get("session_id") == session.session_id for row in tail)
+        )
+
     @property
     def observations_by_content(self) -> Mapping[str, tuple[LedgerObservation, ...]]:
         grouped: dict[str, list[LedgerObservation]] = {}
         for observation in self.observations:
             if observation.content_id is not None:
                 grouped.setdefault(observation.content_id, []).append(observation)
         return MappingProxyType(
             {key: tuple(value) for key, value in sorted(grouped.items())}
         )
 
     def post_cutoff_live_observations(
         self, cutoff_sequence: int
     ) -> tuple[LedgerObservation, ...]:
         """Return only fresh live-capture observations after ``cutoff_sequence``.
 
         Historical bootstrap finalizations are deliberately excluded even
         when a caller compares them with the genesis sequence-zero cutoff.
         """
 
         if (
             isinstance(cutoff_sequence, bool)
             or not isinstance(cutoff_sequence, int)
             or cutoff_sequence < 0
         ):
             raise CalibrationLedgerError("cutoff_sequence must be nonnegative")
         return tuple(
             observation
             for observation in self.observations
             if observation.sequence > cutoff_sequence
             and not observation.is_historical_import
         )
 
 
+@dataclass(frozen=True)
+class CalibrationBracketSession:
+    """Authenticated state of one prospectively reserved two-slot window."""
+
+    session_id: str
+    window_id: str
+    plan_id: str
+    plan_sha256: str
+    evidence_root_id: str
+    capability_receipt_digest: str
+    capability_sequence: int
+    slot_attempt_ids: Mapping[str, str]
+    state: str
+    finalized_slots: Mapping[str, LedgerObservation]
+    abort_receipt_digest: str | None = None
+    abort_reason: str | None = None
+
+
 @dataclass(frozen=True)
 class HistoricalImportPlan:
     """Deterministic, authenticated genesis bootstrap prepared in memory."""
 
     receipts: tuple[Mapping[str, Any], ...]
     final_sequence: int
     head_digest: str
     head_pin: Mapping[str, Any]
     disposition_table_sha256: str
     custody_manifest_sha256: str
 
     @property
     def ledger_bytes(self) -> bytes:
         return b"".join(canonical_json_bytes(row) + b"\n" for row in self.receipts)
 
 
 class HistoricalImportDurabilityUncertain(CalibrationLedgerError):
     """The import committed, but its parent-directory fsync did not confirm."""
 
     outcome = "committed_durability_uncertain"
 
     def __init__(self, plan: HistoricalImportPlan) -> None:
         super().__init__(
             "historical import committed but parent-directory durability is uncertain"
         )
         self.plan = plan
 
 
 @dataclass(frozen=True)
 class _HistoricalCandidate:
     attempt_id: str
     content_id: str
     artifact_sha256: Mapping[str, str]
     identity_epoch: Mapping[str, Any]
     t1_bindings: Mapping[str, Any]
     capture_wall_time_s: str | None
     exact_bound_lexeme_s: str | None
     custody_sort_key: str
     custody_locator: str
 
 
 def _frozen_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
     frozen: dict[str, Any] = {}
     for key, item in value.items():
         if isinstance(item, Mapping):
             frozen[key] = _frozen_mapping(item)
         elif isinstance(item, list):
             frozen[key] = tuple(
                 _frozen_mapping(child) if isinstance(child, Mapping) else child
                 for child in item
             )
         else:
             frozen[key] = item
     return MappingProxyType(frozen)
 
 
 _RECEIPT_KEYS = frozenset(
     {
         "schema_version",
         "ledger_schema",
         "sequence",
         "predecessor_digest",
         "event",
         "attempt_id",
         "content_id",
         "artifact_sha256",
         "identity_epoch",
         "t1_bindings",
         "capture_wall_time_s",
         "exact_bound_lexeme_s",
         "disposition",
         "custody_locator",
         "receipt_digest",
     }
 )
 _HISTORICAL_IMPORT_INPUT_SHA256_KEY = "historical_import_input_sha256"
 _HISTORICAL_IMPORT_INPUT_SHA256_KEYS = frozenset(
     {"disposition_table", "custody_manifest"}
 )
 _HISTORICAL_IMPORT_RESERVATION_KEYS = (
     _RECEIPT_KEYS | {_HISTORICAL_IMPORT_INPUT_SHA256_KEY}
 )
+_CHAIN_KEYS = frozenset(
+    {
+        "schema_version",
+        "ledger_schema",
+        "sequence",
+        "predecessor_digest",
+        "event",
+        "receipt_digest",
+    }
+)
+_SESSION_IDENTITY_KEYS = frozenset(
+    {"session_id", "window_id", "plan_id", "plan_sha256", "evidence_root_id"}
+)
+_SESSION_OPEN_KEYS = _CHAIN_KEYS | _SESSION_IDENTITY_KEYS | {"slots"}
+_SESSION_FINALIZATION_KEYS = (
+    _CHAIN_KEYS
+    | _SESSION_IDENTITY_KEYS
+    | {
+        "slot",
+        "attempt_id",
+        "content_id",
+        "artifact_sha256",
+        "identity_epoch",
+        "t1_bindings",
+        "capture_wall_time_s",
+        "exact_bound_lexeme_s",
+        "disposition",
+        "custody_locator",
+    }
+)
+_SESSION_ABORT_KEYS = (
+    _CHAIN_KEYS
+    | _SESSION_IDENTITY_KEYS
+    | {"finalized_slots", "unused_slots", "reason"}
+)
+_SESSION_SLOT_KEYS = frozenset(
+    {
+        "attempt_id",
+        "custody_locator",
+        "identity_epoch",
+        "t1_bindings",
+        "expected_time_role",
+    }
+)
+
+
+def _valid_chain_fields(receipt: Mapping[str, Any], schema: str) -> bool:
+    sequence = receipt.get("sequence")
+    return (
+        receipt.get("schema_version") == schema
+        and receipt.get("ledger_schema") == LEDGER_SCHEMA
+        and not isinstance(sequence, bool)
+        and isinstance(sequence, int)
+        and sequence >= 1
+        and _is_sha256(receipt.get("predecessor_digest"))
+        and _is_sha256(receipt.get("receipt_digest"))
+        and receipt.get("receipt_digest") == _receipt_digest(receipt)
+    )
+
+
+def _valid_session_identity(receipt: Mapping[str, Any]) -> bool:
+    return (
+        all(
+            isinstance(receipt.get(field), str) and bool(receipt.get(field))
+            for field in ("session_id", "window_id", "plan_id", "evidence_root_id")
+        )
+        and _is_sha256(receipt.get("plan_sha256"))
+    )
+
+
+def _valid_session_slot_reservation(slot: object, expected_role: str) -> bool:
+    if not isinstance(slot, Mapping) or set(slot) != _SESSION_SLOT_KEYS:
+        return False
+    epoch = slot.get("identity_epoch")
+    t1 = slot.get("t1_bindings")
+    return (
+        isinstance(slot.get("attempt_id"), str)
+        and bool(slot.get("attempt_id"))
+        and isinstance(slot.get("custody_locator"), str)
+        and bool(slot.get("custody_locator"))
+        and slot.get("expected_time_role") == expected_role
+        and isinstance(epoch, Mapping)
+        and set(epoch) == set(IDENTITY_EPOCH_FIELDS)
+        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
+        and isinstance(t1, Mapping)
+        and set(t1) == set(T1_FIELDS)
+        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
+    )
+
+
+def _valid_session_receipt_shape(receipt: Mapping[str, Any]) -> bool:
+    event = receipt.get("event")
+    expected_keys = {
+        BRACKET_SESSION_OPEN_EVENT: _SESSION_OPEN_KEYS,
+        BRACKET_SESSION_FINALIZATION_EVENT: _SESSION_FINALIZATION_KEYS,
+        BRACKET_SESSION_ABORT_EVENT: _SESSION_ABORT_KEYS,
+    }.get(event)
+    if (
+        expected_keys is None
+        or set(receipt) != expected_keys
+        or not _valid_chain_fields(receipt, BRACKET_SESSION_SCHEMA)
+        or not _valid_session_identity(receipt)
+    ):
+        return False
+    if event == BRACKET_SESSION_OPEN_EVENT:
+        slots = receipt.get("slots")
+        return (
+            isinstance(slots, Mapping)
+            and set(slots) == set(BRACKET_SESSION_SLOTS)
+            and all(
+                _valid_session_slot_reservation(slots.get(role), role)
+                for role in BRACKET_SESSION_SLOTS
+            )
+            and slots["pre"]["attempt_id"] != slots["post"]["attempt_id"]
+        )
+    if event == BRACKET_SESSION_ABORT_EVENT:
+        finalized = receipt.get("finalized_slots")
+        unused = receipt.get("unused_slots")
+        reason = receipt.get("reason")
+        return (
+            isinstance(finalized, Sequence)
+            and not isinstance(finalized, (str, bytes))
+            and isinstance(unused, Sequence)
+            and not isinstance(unused, (str, bytes))
+            and all(slot in BRACKET_SESSION_SLOTS for slot in (*finalized, *unused))
+            and len(set((*finalized, *unused))) == len(finalized) + len(unused)
+            and set((*finalized, *unused)) == set(BRACKET_SESSION_SLOTS)
+            and isinstance(reason, str)
+            and bool(reason)
+        )
+    disposition = receipt.get("disposition")
+    artifacts = receipt.get("artifact_sha256")
+    epoch = receipt.get("identity_epoch")
+    t1 = receipt.get("t1_bindings")
+    capture = receipt.get("capture_wall_time_s")
+    bound = receipt.get("exact_bound_lexeme_s")
+    content_id = receipt.get("content_id")
+    if (
+        receipt.get("slot") not in BRACKET_SESSION_SLOTS
+        or not isinstance(receipt.get("attempt_id"), str)
+        or not receipt.get("attempt_id")
+        or disposition not in FINAL_DISPOSITIONS
+        or not isinstance(receipt.get("custody_locator"), str)
+        or not isinstance(artifacts, Mapping)
+        or any(
+            not isinstance(name, str) or not name or not _is_sha256(digest)
+            for name, digest in artifacts.items()
+        )
+        or not isinstance(epoch, Mapping)
+        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
+        or not isinstance(t1, Mapping)
+        or set(t1) != set(T1_FIELDS)
+        or (capture is not None and not isinstance(capture, str))
+        or (bound is not None and not isinstance(bound, str))
+        or (content_id is not None and not _is_sha256(content_id))
+    ):
+        return False
+    if disposition == "abandoned":
+        return content_id == content_id_from_artifact_hashes(artifacts)
+    return (
+        content_id is not None
+        and content_id_from_artifact_hashes(artifacts) == content_id
+        and bool(receipt.get("custody_locator"))
+        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
+        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
+        and capture is not None
+    )
 
 
 def _valid_receipt_shape(receipt: object) -> bool:
     if not isinstance(receipt, Mapping):
         return False
+    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
+        return _valid_session_receipt_shape(receipt)
     sequence = receipt.get("sequence")
     event = receipt.get("event")
     expected_keys = (
         _HISTORICAL_IMPORT_RESERVATION_KEYS
         if event == HISTORICAL_IMPORT_RESERVATION_EVENT
         else _RECEIPT_KEYS
     )
     if set(receipt) != expected_keys:
         return False
     disposition = receipt.get("disposition")
     artifacts = receipt.get("artifact_sha256")
     epoch = receipt.get("identity_epoch")
     t1 = receipt.get("t1_bindings")
     capture = receipt.get("capture_wall_time_s")
     bound = receipt.get("exact_bound_lexeme_s")
     if (
         receipt.get("schema_version") != RECEIPT_SCHEMA
         or receipt.get("ledger_schema") != LEDGER_SCHEMA
         or isinstance(sequence, bool)
         or not isinstance(sequence, int)
         or sequence < 1
         or not _is_sha256(receipt.get("predecessor_digest"))
         or event
         not in {
             "reservation",
             "finalization",
             HISTORICAL_IMPORT_RESERVATION_EVENT,
             HISTORICAL_IMPORT_FINALIZATION_EVENT,
         }
         or not isinstance(receipt.get("attempt_id"), str)
         or not receipt.get("attempt_id")
         or disposition not in ALL_DISPOSITIONS
         or not isinstance(receipt.get("custody_locator"), str)
         or not isinstance(artifacts, Mapping)
         or any(
             not isinstance(name, str) or not name or not _is_sha256(digest)
             for name, digest in artifacts.items()
         )
         or not isinstance(epoch, Mapping)
         or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
         or not isinstance(t1, Mapping)
         or set(t1) != set(T1_FIELDS)
         or (capture is not None and not isinstance(capture, str))
         or (bound is not None and not isinstance(bound, str))
         or not _is_sha256(receipt.get("receipt_digest"))
         or receipt.get("receipt_digest") != _receipt_digest(receipt)
     ):
         return False
     content_id = receipt.get("content_id")
     if content_id is not None and not _is_sha256(content_id):
         return False
     if event in {"reservation", HISTORICAL_IMPORT_RESERVATION_EVENT}:
         historical_input_sha256 = receipt.get(
             _HISTORICAL_IMPORT_INPUT_SHA256_KEY
         )
         return (
             disposition == "pending"
             and content_id is None
             and not artifacts
             and capture is None
             and bound is None
             and all(
                 epoch.get(field) not in (None, "")
                 for field in IDENTITY_EPOCH_FIELDS
             )
             and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
             and (
                 event != HISTORICAL_IMPORT_RESERVATION_EVENT
                 or isinstance(historical_input_sha256, Mapping)
                 and set(historical_input_sha256)
                 == _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
                 and all(
                     _is_sha256(historical_input_sha256.get(name))
                     for name in _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
                 )
             )
         )
     if disposition not in FINAL_DISPOSITIONS:
         return False
     if disposition == "abandoned":
@@ -457,404 +696,626 @@ def _valid_receipt_shape(receipt: object) -> bool:
 
 
 def _head_pin(value: object) -> tuple[int, str] | None:
     if not isinstance(value, Mapping) or set(value) != {
         "sequence",
         "head_digest",
         "ledger_schema",
     }:
         return None
     sequence = value.get("sequence")
     digest = value.get("head_digest")
     if (
         value.get("ledger_schema") != LEDGER_SCHEMA
         or isinstance(sequence, bool)
         or not isinstance(sequence, int)
         or sequence < 0
         or not _is_sha256(digest)
         or (sequence == 0 and digest != GENESIS_DIGEST)
     ):
         return None
     return sequence, str(digest)
 
 
 def _committed_pin_bytes(path: Path, repo_root: Path) -> bytes | None:
     try:
         relative = Path(path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
     except (OSError, ValueError):
         return None
     try:
         completed = subprocess.run(
             ["git", "show", f"HEAD:{relative}"],
             cwd=repo_root,
             check=True,
             stdout=subprocess.PIPE,
             stderr=subprocess.DEVNULL,
         )
     except (OSError, subprocess.CalledProcessError):
         return None
     return completed.stdout
 
 
 def _parse_ledger(raw: bytes) -> tuple[list[Mapping[str, Any]], set[str]]:
     receipts: list[Mapping[str, Any]] = []
     reasons: set[str] = set()
     if not raw:
         return receipts, reasons
     try:
         text = raw.decode("utf-8")
     except UnicodeDecodeError:
         return receipts, {"calibration_ledger_malformed"}
     if not text.endswith("\n"):
         reasons.add("calibration_ledger_malformed")
     predecessor = GENESIS_DIGEST
     expected_sequence = 1
     seen_digests: set[str] = set()
     for line in text.splitlines():
         if not line.strip():
             reasons.add("calibration_ledger_malformed")
             continue
         try:
             value = json.loads(line)
         except json.JSONDecodeError:
             reasons.add("calibration_ledger_malformed")
             continue
         if not _valid_receipt_shape(value):
             reasons.add("calibration_ledger_malformed")
             continue
         if (
             value["sequence"] != expected_sequence
             or value["predecessor_digest"] != predecessor
             or value["receipt_digest"] in seen_digests
         ):
             reasons.add("calibration_ledger_chain_conflict")
         expected_sequence += 1
         predecessor = value["receipt_digest"]
         seen_digests.add(predecessor)
         receipts.append(value)
     return receipts, reasons
 
 
+def _observation_from_receipt(
+    receipt: Mapping[str, Any],
+    *,
+    observation_kind: str,
+    session: Mapping[str, Any] | None = None,
+) -> LedgerObservation:
+    content_id = receipt.get("content_id")
+    return LedgerObservation(
+        sequence=int(receipt["sequence"]),
+        receipt_digest=str(receipt["receipt_digest"]),
+        attempt_id=str(receipt["attempt_id"]),
+        content_id=str(content_id) if isinstance(content_id, str) else None,
+        artifact_sha256=MappingProxyType(dict(receipt["artifact_sha256"])),
+        identity_epoch=MappingProxyType(dict(receipt["identity_epoch"])),
+        t1_bindings=MappingProxyType(dict(receipt["t1_bindings"])),
+        capture_wall_time_s=receipt.get("capture_wall_time_s"),
+        exact_bound_lexeme_s=receipt.get("exact_bound_lexeme_s"),
+        disposition=str(receipt["disposition"]),
+        custody_locator=str(receipt["custody_locator"]),
+        observation_kind=observation_kind,
+        bracket_session_id=(str(session["session_id"]) if session else None),
+        bracket_slot=(str(receipt["slot"]) if session else None),
+        bracket_window_id=(str(session["window_id"]) if session else None),
+        bracket_plan_id=(str(session["plan_id"]) if session else None),
+        bracket_plan_sha256=(str(session["plan_sha256"]) if session else None),
+        bracket_evidence_root_id=(
+            str(session["evidence_root_id"]) if session else None
+        ),
+    )
+
+
+def _session_identity_matches(
+    receipt: Mapping[str, Any], open_receipt: Mapping[str, Any]
+) -> bool:
+    return all(receipt.get(field) == open_receipt.get(field) for field in _SESSION_IDENTITY_KEYS)
+
+
+def _bracket_sessions_and_observations(
+    receipts: Sequence[Mapping[str, Any]],
+) -> tuple[list[CalibrationBracketSession], list[LedgerObservation], set[str]]:
+    states: dict[str, dict[str, Any]] = {}
+    claimed_attempts: set[str] = set()
+    reasons: set[str] = set()
+    for receipt in receipts:
+        if receipt.get("schema_version") != BRACKET_SESSION_SCHEMA:
+            continue
+        event = receipt["event"]
+        session_id = str(receipt["session_id"])
+        if event == BRACKET_SESSION_OPEN_EVENT:
+            slots = receipt["slots"]
+            attempt_ids = {str(slots[role]["attempt_id"]) for role in BRACKET_SESSION_SLOTS}
+            if session_id in states or attempt_ids & claimed_attempts:
+                reasons.add("calibration_ledger_bracket_session_conflict")
+                continue
+            claimed_attempts.update(attempt_ids)
+            states[session_id] = {
+                "open": receipt,
+                "finals": {},
+                "abort": None,
+            }
+            continue
+        state = states.get(session_id)
+        if state is None:
+            reasons.add("calibration_ledger_bracket_session_conflict")
+            continue
+        open_receipt = state["open"]
+        if not _session_identity_matches(receipt, open_receipt):
+            reasons.add("calibration_ledger_bracket_session_conflict")
+            continue
+        finals = state["finals"]
+        if event == BRACKET_SESSION_FINALIZATION_EVENT:
+            slot = str(receipt["slot"])
+            expected_slot = BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
+            reserved = open_receipt["slots"].get(slot)
+            if (
+                state["abort"] is not None
+                or slot != expected_slot
+                or slot in finals
+                or not isinstance(reserved, Mapping)
+                or receipt["attempt_id"] != reserved["attempt_id"]
+                or receipt["custody_locator"] != reserved["custody_locator"]
+                or dict(receipt["identity_epoch"]) != dict(reserved["identity_epoch"])
+                or dict(receipt["t1_bindings"]) != dict(reserved["t1_bindings"])
+            ):
+                reasons.add("calibration_ledger_bracket_session_conflict")
+                continue
+            finals[slot] = receipt
+            continue
+        finalized_slots = list(finals)
+        unused_slots = [slot for slot in BRACKET_SESSION_SLOTS if slot not in finals]
+        if (
+            event != BRACKET_SESSION_ABORT_EVENT
+            or state["abort"] is not None
+            or len(finals) == 2
+            or receipt["finalized_slots"] != finalized_slots
+            or receipt["unused_slots"] != unused_slots
+        ):
+            reasons.add("calibration_ledger_bracket_session_conflict")
+            continue
+        state["abort"] = receipt
+
+    sessions: list[CalibrationBracketSession] = []
+    completed_observations: list[LedgerObservation] = []
+    for session_id, state in sorted(
+        states.items(), key=lambda item: int(item[1]["open"]["sequence"])
+    ):
+        open_receipt = state["open"]
+        finals = state["finals"]
+        abort = state["abort"]
+        if abort is not None:
+            session_state = "aborted"
+        elif len(finals) == 2:
+            session_state = "finalized"
+        else:
+            session_state = "open"
+            reasons.add("calibration_ledger_bracket_session_open")
+        finalized_observations = {
+            slot: _observation_from_receipt(
+                receipt,
+                observation_kind=(
+                    "bracket-session-finalized"
+                    if session_state == "finalized"
+                    else "bracket-session-aborted"
+                ),
+                session=open_receipt,
+            )
+            for slot, receipt in finals.items()
+        }
+        if session_state != "aborted":
+            completed_observations.extend(
+                finalized_observations[slot]
+                for slot in BRACKET_SESSION_SLOTS
+                if slot in finalized_observations
+            )
+        sessions.append(
+            CalibrationBracketSession(
+                session_id=session_id,
+                window_id=str(open_receipt["window_id"]),
+                plan_id=str(open_receipt["plan_id"]),
+                plan_sha256=str(open_receipt["plan_sha256"]),
+                evidence_root_id=str(open_receipt["evidence_root_id"]),
+                capability_receipt_digest=str(open_receipt["receipt_digest"]),
+                capability_sequence=int(open_receipt["sequence"]),
+                slot_attempt_ids=MappingProxyType(
+                    {
+                        slot: str(open_receipt["slots"][slot]["attempt_id"])
+                        for slot in BRACKET_SESSION_SLOTS
+                    }
+                ),
+                state=session_state,
+                finalized_slots=MappingProxyType(finalized_observations),
+                abort_receipt_digest=(
+                    str(abort["receipt_digest"]) if abort is not None else None
+                ),
+                abort_reason=(str(abort["reason"]) if abort is not None else None),
+            )
+        )
+    return sessions, completed_observations, reasons
+
+
 def _attempts_and_observations(
     receipts: Sequence[Mapping[str, Any]],
-) -> tuple[list[LedgerObservation], set[str]]:
+) -> tuple[list[LedgerObservation], list[CalibrationBracketSession], set[str]]:
     pending: dict[str, Mapping[str, Any]] = {}
     finalized: dict[str, Mapping[str, Any]] = {}
     reasons: set[str] = set()
     for receipt in receipts:
+        if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
+            continue
         attempt_id = str(receipt["attempt_id"])
         if receipt["event"] in {
             "reservation",
             HISTORICAL_IMPORT_RESERVATION_EVENT,
         }:
             if attempt_id in pending or attempt_id in finalized:
                 reasons.add("calibration_ledger_attempt_conflict")
             else:
                 pending[attempt_id] = receipt
             continue
         reservation = pending.get(attempt_id)
         expected_final_event = (
             HISTORICAL_IMPORT_FINALIZATION_EVENT
             if reservation is not None
             and reservation["event"] == HISTORICAL_IMPORT_RESERVATION_EVENT
             else "finalization"
         )
         if (
             reservation is None
             or attempt_id in finalized
             or receipt["event"] != expected_final_event
         ):
             reasons.add("calibration_ledger_attempt_conflict")
         else:
             finalized[attempt_id] = receipt
     if set(pending) - set(finalized):
         reasons.add("calibration_ledger_pending")
 
     observations: list[LedgerObservation] = []
     content_classification: dict[str, tuple[str, tuple[tuple[str, Any], ...]]] = {}
     for attempt_id, receipt in sorted(
         finalized.items(), key=lambda item: int(item[1]["sequence"])
     ):
         content_id = receipt.get("content_id")
         epoch = dict(receipt["identity_epoch"])
         if isinstance(content_id, str):
             classification = (
                 (
                     "unresolved"
                     if receipt["disposition"] == "abandoned"
                     else str(receipt["disposition"])
                 ),
                 tuple((field, epoch.get(field)) for field in IDENTITY_EPOCH_FIELDS),
             )
             previous = content_classification.get(content_id)
             if previous is not None and previous != classification:
                 reasons.add("calibration_ledger_content_conflict")
             content_classification[content_id] = classification
         observations.append(
-            LedgerObservation(
-                sequence=int(receipt["sequence"]),
-                receipt_digest=str(receipt["receipt_digest"]),
-                attempt_id=attempt_id,
-                content_id=str(content_id) if isinstance(content_id, str) else None,
-                artifact_sha256=MappingProxyType(dict(receipt["artifact_sha256"])),
-                identity_epoch=MappingProxyType(epoch),
-                t1_bindings=MappingProxyType(dict(receipt["t1_bindings"])),
-                capture_wall_time_s=receipt.get("capture_wall_time_s"),
-                exact_bound_lexeme_s=receipt.get("exact_bound_lexeme_s"),
-                disposition=str(receipt["disposition"]),
-                custody_locator=str(receipt["custody_locator"]),
+            _observation_from_receipt(
+                receipt,
                 observation_kind=(
                     "historical-import"
                     if receipt["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
                     else "live-capture"
                 ),
             )
         )
-    return observations, reasons
+    sessions, session_observations, session_reasons = (
+        _bracket_sessions_and_observations(receipts)
+    )
+    reasons.update(session_reasons)
+    session_attempt_ids = {
+        attempt_id
+        for session in sessions
+        for attempt_id in session.slot_attempt_ids.values()
+    }
+    if set(pending) & session_attempt_ids:
+        reasons.add("calibration_ledger_bracket_session_conflict")
+    observations.extend(session_observations)
+    content_classification.clear()
+    classification_observations = list(observations)
+    visible_attempts = {observation.attempt_id for observation in observations}
+    classification_observations.extend(
+        observation
+        for session in sessions
+        for observation in session.finalized_slots.values()
+        if observation.attempt_id not in visible_attempts
+    )
+    for observation in classification_observations:
+        if observation.content_id is None:
+            continue
+        classification = (
+            observation.classification_disposition,
+            tuple(
+                (field, observation.identity_epoch.get(field))
+                for field in IDENTITY_EPOCH_FIELDS
+            ),
+        )
+        previous = content_classification.get(observation.content_id)
+        if previous is not None and previous != classification:
+            reasons.add("calibration_ledger_content_conflict")
+        content_classification[observation.content_id] = classification
+    observations.sort(key=lambda observation: observation.sequence)
+    return observations, sessions, reasons
 
 
 def _custody_reasons(
     observations: Sequence[LedgerObservation], repo_root: Path
 ) -> set[str]:
     for observation in observations:
         if not observation.artifact_sha256:
             if observation.disposition == "abandoned":
                 continue
             return {"calibration_ledger_custody_invalid"}
         root = Path(observation.custody_locator)
         if not root.is_absolute():
             root = Path(repo_root) / root
         for relative, expected in observation.artifact_sha256.items():
             path = root / relative
             try:
                 actual = hashlib.sha256(path.read_bytes()).hexdigest()
             except OSError:
                 return {"calibration_ledger_custody_invalid"}
             if actual != expected:
                 return {"calibration_ledger_custody_invalid"}
     return set()
 
 
 def load_calibration_ledger_snapshot(
     ledger_path: Path = DEFAULT_LEDGER_PATH,
     head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
     *,
     baseline_sequence: int | None = None,
     baseline_digest: str | None = None,
     require_committed_pin: bool = True,
     verify_custody: bool = True,
     repo_root: Path = REPO_ROOT,
 ) -> CalibrationLedgerSnapshot:
     """Load, authenticate, and freeze exactly one ledger snapshot.
 
     A proper physical prefix of the pin is classified explicitly as rollback;
     any other physical/pinned disagreement is a stale-head mismatch.  The
     baseline must occur at its exact sequence in the same complete chain.
     This closes workflow omission, unregistered evidence, and rollback or
     stale-head consumption; it does not defend against a malicious trusted
     writer or a rewrite of both Git and the full ledger history.
     """
 
     ledger_path = Path(ledger_path)
     head_pin_path = Path(head_pin_path)
     reasons: set[str] = set()
     try:
         pin_raw = head_pin_path.read_bytes()
         pin_value = json.loads(pin_raw)
     except (OSError, UnicodeDecodeError, json.JSONDecodeError):
         pin_raw = b""
         pin_value = None
     pin = _head_pin(pin_value)
     if pin is None:
         reasons.add("calibration_ledger_malformed")
         pinned_sequence, pinned_digest = 0, GENESIS_DIGEST
     else:
         pinned_sequence, pinned_digest = pin
     try:
         raw = ledger_path.read_bytes()
     except OSError:
         raw = b""
         if pinned_sequence > 0:
             reasons.add("calibration_ledger_missing")
     genesis_development_bootstrap = (
         pinned_sequence == 0
         and pinned_digest == GENESIS_DIGEST
         and not raw
         and not ledger_path.exists()
     )
     if (
         require_committed_pin
         # The checked-in fixture starts at genesis.  Before its first commit,
         # an absent physical ledger cannot license a claim (there are no
         # endpoints); permitting this development-only empty view avoids a
         # circular "commit before tests" bootstrap. Any physical byte or any
         # non-genesis pin remains strictly commit-authenticated.
         and not genesis_development_bootstrap
         and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
     ):
         reasons.add("calibration_ledger_head_uncommitted")
     receipts, parse_reasons = _parse_ledger(raw)
     reasons.update(parse_reasons)
     physical_sequence = len(receipts)
     physical_digest = (
         str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
     )
     if (physical_sequence, physical_digest) != (pinned_sequence, pinned_digest):
         if physical_sequence < pinned_sequence:
             reasons.add("calibration_ledger_rollback")
         else:
             reasons.add("calibration_ledger_head_mismatch")
     if baseline_sequence is not None or baseline_digest is not None:
         if (
             isinstance(baseline_sequence, bool)
             or not isinstance(baseline_sequence, int)
             or baseline_sequence < 0
             or not _is_sha256(baseline_digest)
         ):
             reasons.add("calibration_ledger_baseline_missing")
         else:
             in_chain = (
                 baseline_digest == GENESIS_DIGEST
                 if baseline_sequence == 0
                 else baseline_sequence <= len(receipts)
                 and receipts[baseline_sequence - 1]["receipt_digest"]
                 == baseline_digest
             )
             if not in_chain or baseline_sequence > pinned_sequence:
                 reasons.add("calibration_ledger_baseline_missing")
-    observations, state_reasons = _attempts_and_observations(receipts)
+    observations, bracket_sessions, state_reasons = _attempts_and_observations(
+        receipts
+    )
     reasons.update(state_reasons)
     if verify_custody:
-        reasons.update(_custody_reasons(observations, repo_root))
+        custody_observations = list(observations)
+        custody_attempt_ids = {observation.attempt_id for observation in observations}
+        for session in bracket_sessions:
+            custody_observations.extend(
+                observation
+                for observation in session.finalized_slots.values()
+                if observation.attempt_id not in custody_attempt_ids
+            )
+        reasons.update(_custody_reasons(custody_observations, repo_root))
     return CalibrationLedgerSnapshot(
         ledger_schema=LEDGER_SCHEMA,
         ledger_path=ledger_path,
         head_sequence=physical_sequence,
         head_digest=physical_digest,
         receipts=tuple(_frozen_mapping(receipt) for receipt in receipts),
         observations=tuple(observations),
         refusal_reasons=tuple(sorted(reasons)),
+        bracket_sessions=tuple(bracket_sessions),
         baseline_sequence=baseline_sequence,
         baseline_digest=baseline_digest,
+        committed_head_sequence=pinned_sequence,
+        committed_head_digest=pinned_digest,
     )
 
 
 def _new_receipt(
     *,
     sequence: int,
     predecessor_digest: str,
     event: str,
     attempt_id: str,
     content_id: str | None,
     artifacts: Mapping[str, str],
     identity_epoch: Mapping[str, Any] | None,
     t1_bindings: Mapping[str, Any] | None,
     capture_wall_time_s: str | None,
     exact_bound_lexeme_s: str | None,
     disposition: str,
     custody_locator: str,
     historical_import_input_sha256: Mapping[str, str] | None = None,
 ) -> dict[str, Any]:
     receipt: dict[str, Any] = {
         "schema_version": RECEIPT_SCHEMA,
         "ledger_schema": LEDGER_SCHEMA,
         "sequence": sequence,
         "predecessor_digest": predecessor_digest,
         "event": event,
         "attempt_id": attempt_id,
         "content_id": content_id,
         "artifact_sha256": dict(sorted(artifacts.items())),
         "identity_epoch": _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS),
         "t1_bindings": _normalized_vector(t1_bindings, T1_FIELDS),
         "capture_wall_time_s": capture_wall_time_s,
         "exact_bound_lexeme_s": exact_bound_lexeme_s,
         "disposition": disposition,
         "custody_locator": custody_locator,
     }
     if historical_import_input_sha256 is not None:
         receipt[_HISTORICAL_IMPORT_INPUT_SHA256_KEY] = dict(
             sorted(historical_import_input_sha256.items())
         )
     receipt["receipt_digest"] = _receipt_digest(receipt)
     return receipt
 
 
+def _new_bracket_session_record(
+    *,
+    sequence: int,
+    predecessor_digest: str,
+    event: str,
+    session_identity: Mapping[str, Any],
+    fields: Mapping[str, Any],
+) -> dict[str, Any]:
+    receipt = {
+        "schema_version": BRACKET_SESSION_SCHEMA,
+        "ledger_schema": LEDGER_SCHEMA,
+        "sequence": sequence,
+        "predecessor_digest": predecessor_digest,
+        "event": event,
+        **{field: session_identity.get(field) for field in _SESSION_IDENTITY_KEYS},
+        **dict(fields),
+    }
+    receipt["receipt_digest"] = _receipt_digest(receipt)
+    return receipt
+
+
 def _json_object_from_bytes(raw: bytes, source: Path) -> Mapping[str, Any]:
     try:
         value = json.loads(raw)
     except (UnicodeDecodeError, json.JSONDecodeError) as exc:
         raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
     if not isinstance(value, Mapping):
         raise CalibrationLedgerError(f"{source}: expected a JSON object")
     return value
 
 
 def _authenticated_json_object(
     raw: bytes,
     expected_sha256: str,
     *,
     label: str,
 ) -> Mapping[str, Any]:
     if not _is_sha256(expected_sha256):
         raise CalibrationLedgerError(f"expected {label} sha256 is malformed")
     observed = hashlib.sha256(raw).hexdigest()
     if observed != expected_sha256:
         raise CalibrationLedgerError(f"{label} sha256 mismatch")
     return _json_object_from_bytes(raw, Path(label))
 
 
 def _number_lexemes(raw: bytes, source: Path) -> Mapping[str, Any]:
     try:
         value = json.loads(raw, parse_float=str, parse_int=str)
     except (UnicodeDecodeError, json.JSONDecodeError) as exc:
         raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
     if not isinstance(value, Mapping):
         raise CalibrationLedgerError(f"{source}: expected a JSON object")
     return value
 
 
 def _historical_import_table(
     value: Mapping[str, Any],
 ) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
     if set(value) != {
         "schema_version",
         "ledger_schema",
         "identity_epoch",
         "members",
     }:
         raise CalibrationLedgerError("historical import table has invalid keys")
     if (
         value.get("schema_version") != HISTORICAL_IMPORT_TABLE_SCHEMA
         or value.get("ledger_schema") != LEDGER_SCHEMA
     ):
         raise CalibrationLedgerError("historical import table schema mismatch")
     epoch = value.get("identity_epoch")
     members = value.get("members")
     if (
         not isinstance(epoch, Mapping)
         or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
         or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
         or not isinstance(members, list)
         or not members
     ):
         raise CalibrationLedgerError("historical import table is incomplete")
 
     by_content: dict[str, Mapping[str, Any]] = {}
     attempt_ids: set[str] = set()
     for member in members:
         if not isinstance(member, Mapping) or set(member) != {
             "attempt_id",
             "content_id",
             "artifact_sha256",
             "disposition",
         }:
             raise CalibrationLedgerError("historical import member has invalid keys")
         attempt_id = member.get("attempt_id")
         content_id = member.get("content_id")
         artifacts = member.get("artifact_sha256")
         disposition = member.get("disposition")
         if (
             not isinstance(attempt_id, str)
             or not attempt_id
             or not _is_sha256(content_id)
             or not isinstance(artifacts, Mapping)
             or set(artifacts) != set(GOVERNED_ARTIFACTS)
@@ -1271,161 +1732,162 @@ def prepare_historical_import(
         discovered_ids = set(complete)
         if discovered_ids != set(pinned):
             raise CalibrationLedgerError(
                 "discovered hash-complete content set contradicts custody manifest"
             )
         discovered_locators = {
             candidate.custody_locator
             for candidates in complete.values()
             for candidate in candidates
         }
         absent = sorted(
             path.as_posix()
             for path in pinned.values()
             if path.as_posix() not in discovered_locators
         )
         if absent:
             raise CalibrationLedgerError(
                 f"pinned custody locator is absent from root discovery: {absent[0]}"
             )
 
     selected: list[tuple[_HistoricalCandidate, Mapping[str, Any]]] = []
     for content_id, member in table_by_content.items():
         candidate = selected_by_content[content_id]
         if candidate.attempt_id != member["attempt_id"]:
             raise CalibrationLedgerError(
                 f"{content_id}: attempt_id differs from disposition table"
             )
         if dict(candidate.artifact_sha256) != dict(member["artifact_sha256"]):
             raise CalibrationLedgerError(
                 f"{content_id}: artifact hashes differ from disposition table"
             )
         selected.append((candidate, member))
 
     # Attempt ids are contractually unique. content_id is the deterministic
     # secondary key used before the duplicate-attempt refusal above.
     selected.sort(key=lambda item: (item[0].attempt_id, item[0].content_id))
     receipts: list[Mapping[str, Any]] = []
     predecessor = GENESIS_DIGEST
     for candidate, member in selected:
         reservation = _new_receipt(
             sequence=len(receipts) + 1,
             predecessor_digest=predecessor,
             event=HISTORICAL_IMPORT_RESERVATION_EVENT,
             attempt_id=candidate.attempt_id,
             content_id=None,
             artifacts={},
             identity_epoch=candidate.identity_epoch,
             t1_bindings=candidate.t1_bindings,
             capture_wall_time_s=None,
             exact_bound_lexeme_s=None,
             disposition="pending",
             custody_locator=candidate.custody_locator,
             historical_import_input_sha256={
                 "disposition_table": expected_disposition_table_sha256,
                 "custody_manifest": expected_custody_manifest_sha256,
             },
         )
         if not _valid_receipt_shape(reservation):
             raise CalibrationLedgerError("historical reservation is malformed")
         receipts.append(reservation)
         predecessor = str(reservation["receipt_digest"])
         finalization = _new_receipt(
             sequence=len(receipts) + 1,
             predecessor_digest=predecessor,
             event=HISTORICAL_IMPORT_FINALIZATION_EVENT,
             attempt_id=candidate.attempt_id,
             content_id=candidate.content_id,
             artifacts=candidate.artifact_sha256,
             identity_epoch=candidate.identity_epoch,
             t1_bindings=candidate.t1_bindings,
             capture_wall_time_s=candidate.capture_wall_time_s,
             exact_bound_lexeme_s=candidate.exact_bound_lexeme_s,
             disposition=str(member["disposition"]),
             custody_locator=candidate.custody_locator,
         )
         if not _valid_receipt_shape(finalization):
             raise CalibrationLedgerError("historical finalization is malformed")
         receipts.append(finalization)
         predecessor = str(finalization["receipt_digest"])
 
-    observations, reasons = _attempts_and_observations(receipts)
+    observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
+    del bracket_sessions
     if reasons or len(observations) != len(selected):
         raise CalibrationLedgerError(
             ", ".join(sorted(reasons or {"historical import is incomplete"}))
         )
     final = receipts[-1]
     pin = head_pin_for_receipt(final)
     return HistoricalImportPlan(
         receipts=tuple(_frozen_mapping(row) for row in receipts),
         final_sequence=len(receipts),
         head_digest=str(final["receipt_digest"]),
         head_pin=_frozen_mapping(pin),
         disposition_table_sha256=expected_disposition_table_sha256,
         custody_manifest_sha256=expected_custody_manifest_sha256,
     )
 
 
 def _require_genesis_bootstrap_state(
     ledger_path: Path,
     head_pin_path: Path,
     *,
     require_committed_pin: bool,
     repo_root: Path,
     expected_payload: bytes | None = None,
     allow_nonempty_pending_plan: bool = False,
 ) -> bool:
     try:
         pin_raw = Path(head_pin_path).read_bytes()
         pin_value = json.loads(pin_raw)
     except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
         raise CalibrationLedgerError("head pin is unreadable") from exc
     if _head_pin(pin_value) != (0, GENESIS_DIGEST):
         raise CalibrationLedgerError("historical import requires the genesis head pin")
     if (
         require_committed_pin
         and _committed_pin_bytes(Path(head_pin_path), Path(repo_root)) != pin_raw
     ):
         raise CalibrationLedgerError("head pin is not committed at Git HEAD")
     path = Path(ledger_path)
     try:
         raw = path.read_bytes() if path.exists() else b""
     except OSError as exc:
         raise CalibrationLedgerError("physical ledger is unreadable") from exc
     if raw:
         if expected_payload is not None and raw == expected_payload:
             return True
         if allow_nonempty_pending_plan:
             return False
         raise CalibrationLedgerError("historical import requires an empty ledger")
     return False
 
 
 def _ledger_lock_path(ledger_path: Path) -> Path:
     ledger = Path(ledger_path)
     return ledger.with_name(f"{ledger.name}.lock")
 
 
 def _open_ledger_lock(ledger_path: Path) -> int:
     """Open one dedicated, non-aliased regular lock inode for a writer."""
 
     ledger = Path(ledger_path)
     try:
         descriptor = os.open(
             _ledger_lock_path(ledger),
             os.O_NOFOLLOW | os.O_CREAT | os.O_RDWR,
             0o600,
         )
     except OSError as exc:
         raise CalibrationLedgerError("ledger lock cannot be opened safely") from exc
     try:
         lock_stat = os.fstat(descriptor)
         if not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_nlink != 1:
             raise CalibrationLedgerError(
                 "ledger lock must be a dedicated regular file"
             )
         try:
             ledger_stat = os.stat(ledger)
         except FileNotFoundError:
             ledger_stat = None
         except OSError as exc:
             raise CalibrationLedgerError(
@@ -1561,253 +2023,560 @@ def bootstrap_historical_import(
                 raise HistoricalImportDurabilityUncertain(plan) from exc
             return plan
 
         staging_descriptor = -1
         staging_path: Path | None = None
         try:
             try:
                 staging_descriptor, staging_name = tempfile.mkstemp(
                     prefix=f".{ledger.name}.bootstrap-",
                     dir=ledger.parent,
                 )
                 staging_path = Path(staging_name)
                 staging = os.fdopen(staging_descriptor, "wb")
                 staging_descriptor = -1
                 with staging:
                     _write_bootstrap_payload(staging, payload)
                     staging.flush()
                     os.fsync(staging.fileno())
                 os.replace(staging_path, ledger)
                 staging_path = None
             except Exception as exc:
                 raise CalibrationLedgerError(
                     "historical import append failed atomically"
                 ) from exc
             try:
                 _fsync_parent_directory(ledger.parent)
             except OSError as exc:
                 raise HistoricalImportDurabilityUncertain(plan) from exc
         finally:
             if staging_descriptor >= 0:
                 os.close(staging_descriptor)
             if staging_path is not None:
                 try:
                     staging_path.unlink()
                 except FileNotFoundError:
                     pass
     finally:
         try:
             os.close(lock_descriptor)
         except OSError:
             pass
     return plan
 
 
 def _locked_append(
     ledger_path: Path,
     build: Any,
 ) -> Mapping[str, Any]:
     ledger_path = Path(ledger_path)
     ledger_path.parent.mkdir(parents=True, exist_ok=True)
     lock_descriptor = _open_ledger_lock(ledger_path)
     try:
         fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
         descriptor = os.open(
             ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
         )
         try:
             with os.fdopen(descriptor, "r+b", closefd=False) as handle:
                 handle.seek(0)
                 raw = handle.read()
                 receipts, reasons = _parse_ledger(raw)
                 if reasons:
                     raise CalibrationLedgerError(", ".join(sorted(reasons)))
                 receipt = build(receipts)
                 if not _valid_receipt_shape(receipt):
                     raise CalibrationLedgerError(
                         "writer constructed a malformed receipt"
                     )
                 payload = canonical_json_bytes(receipt) + b"\n"
                 handle.seek(0, os.SEEK_END)
                 handle.write(payload)
                 handle.flush()
                 os.fsync(handle.fileno())
                 return _frozen_mapping(receipt)
         finally:
             os.close(descriptor)
     finally:
         os.close(lock_descriptor)
 
 
+def _authenticated_head_pin(
+    head_pin_path: Path,
+    *,
+    require_committed_pin: bool,
+    repo_root: Path,
+) -> tuple[int, str]:
+    pin_path = Path(head_pin_path)
+    try:
+        pin_raw = pin_path.read_bytes()
+        pin_value = json.loads(pin_raw)
+    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
+        raise CalibrationLedgerError("head pin is unreadable") from exc
+    pin = _head_pin(pin_value)
+    if pin is None:
+        raise CalibrationLedgerError("head pin is malformed")
+    if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
+        raise CalibrationLedgerError("head pin is not committed at Git HEAD")
+    return pin
+
+
+def append_bracket_session_receipt(
+    ledger_path: Path,
+    *,
+    session_id: str,
+    window_id: str,
+    plan_id: str,
+    plan_sha256: str,
+    evidence_root_id: str,
+    slots: Mapping[str, Mapping[str, Any]],
+    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
+    require_committed_pin: bool = True,
+    repo_root: Path = REPO_ROOT,
+) -> Mapping[str, Any]:
+    """Atomically reserve exactly one immutable pre/post bracket capability.
+
+    Physical-head equality with the committed pin is checked here, at open,
+    and deliberately not checked again while either already-reserved slot is
+    finalized. Claim evaluation remains impossible until the terminal head
+    pin is emitted, reviewed, and committed.
+    """
+
+    session_identity = {
+        "session_id": session_id,
+        "window_id": window_id,
+        "plan_id": plan_id,
+        "plan_sha256": plan_sha256,
+        "evidence_root_id": evidence_root_id,
+    }
+    normalized_slots: dict[str, dict[str, Any]] = {}
+    if not isinstance(slots, Mapping) or set(slots) != set(BRACKET_SESSION_SLOTS):
+        raise CalibrationLedgerError("bracket session must reserve exactly pre and post")
+    for role in BRACKET_SESSION_SLOTS:
+        source = slots.get(role)
+        if not isinstance(source, Mapping):
+            raise CalibrationLedgerError(f"{role} slot is malformed")
+        normalized_slots[role] = {
+            "attempt_id": source.get("attempt_id"),
+            "custody_locator": source.get("custody_locator"),
+            "identity_epoch": _normalized_vector(
+                source.get("identity_epoch"), IDENTITY_EPOCH_FIELDS
+            ),
+            "t1_bindings": _normalized_vector(source.get("t1_bindings"), T1_FIELDS),
+            "expected_time_role": role,
+        }
+    if not _valid_session_identity(session_identity) or any(
+        not _valid_session_slot_reservation(normalized_slots[role], role)
+        for role in BRACKET_SESSION_SLOTS
+    ):
+        raise CalibrationLedgerError("bracket session reservation is malformed")
+    if (
+        normalized_slots["pre"]["attempt_id"]
+        == normalized_slots["post"]["attempt_id"]
+    ):
+        raise CalibrationLedgerError("bracket session slot attempts must be distinct")
+    pin = _authenticated_head_pin(
+        Path(head_pin_path),
+        require_committed_pin=require_committed_pin,
+        repo_root=Path(repo_root),
+    )
+
+    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
+        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
+        if (len(receipts), predecessor) != pin:
+            raise CalibrationLedgerError(
+                "physical ledger head differs from the committed pin"
+            )
+        observations, sessions, reasons = _attempts_and_observations(receipts)
+        del observations
+        if reasons:
+            raise CalibrationLedgerError(", ".join(sorted(reasons)))
+        reserved_attempts = {
+            attempt_id
+            for session in sessions
+            for attempt_id in session.slot_attempt_ids.values()
+        }
+        ordinary_attempts = {
+            str(receipt["attempt_id"])
+            for receipt in receipts
+            if receipt.get("schema_version") == RECEIPT_SCHEMA
+        }
+        proposed_attempts = {
+            normalized_slots[role]["attempt_id"] for role in BRACKET_SESSION_SLOTS
+        }
+        if (
+            any(session.session_id == session_id for session in sessions)
+            or proposed_attempts & (reserved_attempts | ordinary_attempts)
+        ):
+            raise CalibrationLedgerError("bracket session identity conflicts with ledger")
+        return _new_bracket_session_record(
+            sequence=len(receipts) + 1,
+            predecessor_digest=str(predecessor),
+            event=BRACKET_SESSION_OPEN_EVENT,
+            session_identity=session_identity,
+            fields={"slots": normalized_slots},
+        )
+
+    return _locked_append(Path(ledger_path), build)
+
+
+def finalize_bracket_session_slot(
+    ledger_path: Path,
+    *,
+    session_id: str,
+    slot: str,
+    disposition: str,
+    custody_locator: str,
+    artifact_sha256: Mapping[str, str] | None = None,
+    identity_epoch: Mapping[str, Any] | None = None,
+    t1_bindings: Mapping[str, Any] | None = None,
+    capture_wall_time_s: str | None = None,
+    exact_bound_lexeme_s: str | None = None,
+) -> Mapping[str, Any]:
+    """Fill exactly one reserved session slot in mandatory pre/post order."""
+
+    if slot not in BRACKET_SESSION_SLOTS:
+        raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
+    if disposition not in FINAL_DISPOSITIONS:
+        raise CalibrationLedgerError(f"invalid final disposition: {disposition!r}")
+    artifacts = dict(artifact_sha256 or {})
+    content_id = content_id_from_artifact_hashes(artifacts)
+    normalized_epoch = _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS)
+    normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)
+
+    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
+        observations, sessions, reasons = _attempts_and_observations(receipts)
+        del observations
+        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
+        if non_open_reasons:
+            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
+        by_id = {session.session_id: session for session in sessions}
+        session = by_id.get(session_id)
+        if session is None or session.state != "open":
+            raise CalibrationLedgerError("bracket session is not open")
+        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
+        if slot != expected_slot or slot in session.finalized_slots:
+            raise CalibrationLedgerError(
+                f"bracket session slot must finalize in order: expected {expected_slot}"
+            )
+        open_receipt = next(
+            receipt
+            for receipt in receipts
+            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
+            and receipt.get("session_id") == session_id
+        )
+        reserved = open_receipt["slots"][slot]
+        if (
+            reserved["custody_locator"] != custody_locator
+            or dict(reserved["identity_epoch"]) != normalized_epoch
+            or dict(reserved["t1_bindings"]) != normalized_t1
+        ):
+            raise CalibrationLedgerError(
+                "slot finalization conflicts with the reserved session binding"
+            )
+        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
+        return _new_bracket_session_record(
+            sequence=len(receipts) + 1,
+            predecessor_digest=str(predecessor),
+            event=BRACKET_SESSION_FINALIZATION_EVENT,
+            session_identity={
+                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
+            },
+            fields={
+                "slot": slot,
+                "attempt_id": reserved["attempt_id"],
+                "content_id": content_id,
+                "artifact_sha256": dict(sorted(artifacts.items())),
+                "identity_epoch": normalized_epoch,
+                "t1_bindings": normalized_t1,
+                "capture_wall_time_s": capture_wall_time_s,
+                "exact_bound_lexeme_s": exact_bound_lexeme_s,
+                "disposition": disposition,
+                "custody_locator": custody_locator,
+            },
+        )
+
+    return _locked_append(Path(ledger_path), build)
+
+
+def abort_bracket_session(
+    ledger_path: Path,
+    *,
+    session_id: str,
+    reason: str,
+) -> Mapping[str, Any]:
+    """Append a governed terminal closure without deleting partial receipts."""
+
+    if not isinstance(reason, str) or not reason:
+        raise CalibrationLedgerError("bracket session abort reason must be nonempty")
+
+    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
+        observations, sessions, reasons = _attempts_and_observations(receipts)
+        del observations
+        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
+        if non_open_reasons:
+            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
+        session = next(
+            (item for item in sessions if item.session_id == session_id), None
+        )
+        if session is None or session.state != "open":
+            raise CalibrationLedgerError("bracket session is not open")
+        open_receipt = next(
+            receipt
+            for receipt in receipts
+            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
+            and receipt.get("session_id") == session_id
+        )
+        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
+        finalized_slots = list(session.finalized_slots)
+        return _new_bracket_session_record(
+            sequence=len(receipts) + 1,
+            predecessor_digest=str(predecessor),
+            event=BRACKET_SESSION_ABORT_EVENT,
+            session_identity={
+                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
+            },
+            fields={
+                "finalized_slots": finalized_slots,
+                "unused_slots": [
+                    role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
+                ],
+                "reason": reason,
+            },
+        )
+
+    return _locked_append(Path(ledger_path), build)
+
+
+def terminal_head_pin_for_session(
+    ledger_path: Path,
+    *,
+    session_id: str,
+) -> dict[str, Any]:
+    """Return the sole terminal pin candidate after post or governed abort."""
+
+    try:
+        raw = Path(ledger_path).read_bytes()
+    except OSError as exc:
+        raise CalibrationLedgerError("ledger is unreadable") from exc
+    receipts, parse_reasons = _parse_ledger(raw)
+    observations, sessions, state_reasons = _attempts_and_observations(receipts)
+    del observations
+    reasons = parse_reasons | state_reasons
+    if reasons:
+        raise CalibrationLedgerError(", ".join(sorted(reasons)))
+    session = next((item for item in sessions if item.session_id == session_id), None)
+    if session is None or session.state == "open":
+        raise CalibrationLedgerError("bracket session is not terminal")
+    terminal_digest = (
+        session.finalized_slots["post"].receipt_digest
+        if session.state == "finalized"
+        else session.abort_receipt_digest
+    )
+    final = receipts[-1] if receipts else None
+    if final is None or final["receipt_digest"] != terminal_digest:
+        raise CalibrationLedgerError("session closure is not the terminal ledger head")
+    return head_pin_for_receipt(final)
+
+
 def append_pending_receipt(
     ledger_path: Path,
     *,
     attempt_id: str,
     custody_locator: str,
     identity_epoch: Mapping[str, Any] | None = None,
     t1_bindings: Mapping[str, Any] | None = None,
     head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
     require_committed_pin: bool = True,
     repo_root: Path = REPO_ROOT,
 ) -> Mapping[str, Any]:
     """Reserve an attempt before any capture directory or sampler exists.
 
     This closes workflow omission, unregistered evidence, and rollback or
     stale-head consumption; it does not defend against a malicious trusted
     writer or a rewrite of both Git and the full ledger history.
     """
 
     if not isinstance(attempt_id, str) or not attempt_id:
         raise CalibrationLedgerError("attempt_id must be nonempty")
     pin_path = Path(head_pin_path)
     try:
         pin_raw = pin_path.read_bytes()
         pin_value = json.loads(pin_raw)
     except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
         raise CalibrationLedgerError("head pin is unreadable") from exc
     pin = _head_pin(pin_value)
     if pin is None:
         raise CalibrationLedgerError("head pin is malformed")
     if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
         raise CalibrationLedgerError("head pin is not committed at Git HEAD")
 
     def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
         sequence = len(receipts) + 1
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         if (len(receipts), predecessor) != pin:
             raise CalibrationLedgerError(
                 "physical ledger head differs from the committed pin"
             )
-        observations, reasons = _attempts_and_observations(receipts)
+        observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
         del observations
-        if reasons or any(row["attempt_id"] == attempt_id for row in receipts):
+        del bracket_sessions
+        if reasons or any(
+            row.get("attempt_id") == attempt_id
+            or any(
+                isinstance(slot, Mapping) and slot.get("attempt_id") == attempt_id
+                for slot in (
+                    row.get("slots", {}).values()
+                    if isinstance(row.get("slots"), Mapping)
+                    else ()
+                )
+            )
+            for row in receipts
+        ):
             raise CalibrationLedgerError(
                 ", ".join(sorted(reasons or {"calibration_ledger_attempt_conflict"}))
             )
         return _new_receipt(
             sequence=sequence,
             predecessor_digest=str(predecessor),
             event="reservation",
             attempt_id=attempt_id,
             content_id=None,
             artifacts={},
             identity_epoch=identity_epoch,
             t1_bindings=t1_bindings,
             capture_wall_time_s=None,
             exact_bound_lexeme_s=None,
             disposition="pending",
             custody_locator=custody_locator,
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def finalize_attempt_receipt(
     ledger_path: Path,
     *,
     attempt_id: str,
     disposition: str,
     custody_locator: str,
     artifact_sha256: Mapping[str, str] | None = None,
     identity_epoch: Mapping[str, Any] | None = None,
     t1_bindings: Mapping[str, Any] | None = None,
     capture_wall_time_s: str | None = None,
     exact_bound_lexeme_s: str | None = None,
 ) -> Mapping[str, Any]:
     """Append the sole final state for a previously reserved attempt."""
 
     if disposition not in FINAL_DISPOSITIONS:
         raise CalibrationLedgerError(f"invalid final disposition: {disposition!r}")
     artifacts = dict(artifact_sha256 or {})
     content_id = content_id_from_artifact_hashes(artifacts)
 
     def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
+        observations, bracket_sessions, reasons = _attempts_and_observations(
+            receipts
+        )
+        del observations, bracket_sessions
+        unexpected_reasons = reasons - {"calibration_ledger_pending"}
+        if unexpected_reasons:
+            raise CalibrationLedgerError(", ".join(sorted(unexpected_reasons)))
         reservations = [
             row
             for row in receipts
-            if row["attempt_id"] == attempt_id and row["event"] == "reservation"
+            if row.get("attempt_id") == attempt_id and row["event"] == "reservation"
         ]
         finals = [
             row
             for row in receipts
-            if row["attempt_id"] == attempt_id and row["event"] == "finalization"
+            if row.get("attempt_id") == attempt_id and row["event"] == "finalization"
         ]
         if len(reservations) != 1 or finals:
             raise CalibrationLedgerError("attempt is not uniquely pending")
         reservation = reservations[0]
         normalized_epoch = _normalized_vector(
             identity_epoch, IDENTITY_EPOCH_FIELDS
         )
         normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)
         if (
             dict(reservation["identity_epoch"]) != normalized_epoch
             or dict(reservation["t1_bindings"]) != normalized_t1
             or reservation["custody_locator"] != custody_locator
         ):
             raise CalibrationLedgerError(
                 "finalization conflicts with the reserved attempt binding"
             )
         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
         return _new_receipt(
             sequence=len(receipts) + 1,
             predecessor_digest=str(predecessor),
             event="finalization",
             attempt_id=attempt_id,
             content_id=content_id,
             artifacts=artifacts,
             identity_epoch=identity_epoch,
             t1_bindings=t1_bindings,
             capture_wall_time_s=capture_wall_time_s,
             exact_bound_lexeme_s=exact_bound_lexeme_s,
             disposition=disposition,
             custody_locator=custody_locator,
         )
 
     return _locked_append(Path(ledger_path), build)
 
 
 def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
     """Emit the exact candidate pin that must be reviewed and committed."""
 
     if not _valid_receipt_shape(receipt):
         raise CalibrationLedgerError("cannot pin a malformed receipt")
     return {
         "sequence": int(receipt["sequence"]),
         "head_digest": str(receipt["receipt_digest"]),
         "ledger_schema": LEDGER_SCHEMA,
     }
 
 
 __all__ = [
     "ALL_DISPOSITIONS",
+    "BRACKET_SESSION_ABORT_EVENT",
+    "BRACKET_SESSION_FINALIZATION_EVENT",
+    "BRACKET_SESSION_OPEN_EVENT",
+    "BRACKET_SESSION_SCHEMA",
+    "BRACKET_SESSION_SLOTS",
     "CONTENT_ID_ARTIFACTS",
     "DEFAULT_HEAD_PIN_PATH",
     "DEFAULT_LEDGER_PATH",
     "FINAL_DISPOSITIONS",
     "GENESIS_DIGEST",
     "GOVERNED_ARTIFACTS",
     "HISTORICAL_IMPORT_EVENT_PREFIX",
     "HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA",
     "HISTORICAL_IMPORT_FINALIZATION_EVENT",
     "HISTORICAL_IMPORT_RESERVATION_EVENT",
     "HISTORICAL_IMPORT_TABLE_SCHEMA",
     "IDENTITY_EPOCH_FIELDS",
     "LEDGER_SCHEMA",
     "RECEIPT_SCHEMA",
     "REFUSAL_TAXONOMY",
     "CalibrationLedgerError",
+    "CalibrationBracketSession",
     "CalibrationLedgerSnapshot",
     "HistoricalImportDurabilityUncertain",
     "HistoricalImportPlan",
     "LedgerObservation",
     "append_pending_receipt",
+    "append_bracket_session_receipt",
+    "abort_bracket_session",
     "artifact_hashes",
     "bootstrap_historical_import",
     "custody_manifest_bytes",
     "canonical_sha256",
     "content_id_from_artifact_hashes",
     "finalize_attempt_receipt",
+    "finalize_bracket_session_slot",
     "generate_historical_custody_manifest",
     "head_pin_for_receipt",
     "load_calibration_ledger_snapshot",
     "prepare_historical_import",
+    "terminal_head_pin_for_session",
 ]
     1	#!/usr/bin/env python3
     2	"""Reserve one governed two-slot calibration bracket session.
     3	
     4	The capability advances the physical ledger while deliberately leaving the
     5	committed head pin unchanged until the post slot is finalized. Execution is
     6	explicit so argument validation cannot accidentally arm a quiet window.
     7	"""
     8	
     9	from __future__ import annotations
    10	
    11	import argparse
    12	import json
    13	import sys
    14	from pathlib import Path
    15	from typing import Any, Mapping
    16	
    17	sys.dont_write_bytecode = True
    18	REPO_ROOT = Path(__file__).resolve().parents[1]
    19	sys.path.insert(0, str(REPO_ROOT))
    20	
    21	from joulewise.calibration_ledger import (  # noqa: E402
    22	    BRACKET_SESSION_SCHEMA,
    23	    DEFAULT_HEAD_PIN_PATH,
    24	    DEFAULT_LEDGER_PATH,
    25	    IDENTITY_EPOCH_FIELDS,
    26	    T1_FIELDS,
    27	    CalibrationLedgerError,
    28	    append_bracket_session_receipt,
    29	    canonical_json_bytes,
    30	)
    31	
    32	
    33	OUTPUT_SCHEMA = "joulewise.calibration_window_bracket_reservation.v1"
    34	
    35	
    36	def _json_object(path: Path) -> Mapping[str, Any]:
    37	    value = json.loads(Path(path).read_text(encoding="utf-8"))
    38	    if not isinstance(value, Mapping):
    39	        raise ValueError(f"{path}: expected a JSON object")
    40	    return value
    41	
    42	
    43	def _parser() -> argparse.ArgumentParser:
    44	    parser = argparse.ArgumentParser(description=__doc__)
    45	    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
    46	    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
    47	    parser.add_argument("--session-id", required=True)
    48	    parser.add_argument("--window-id", required=True)
    49	    parser.add_argument("--plan-id", required=True)
    50	    parser.add_argument("--plan-sha256", required=True)
    51	    parser.add_argument("--evidence-root-id", required=True)
    52	    parser.add_argument("--pre-attempt-id", required=True)
    53	    parser.add_argument("--post-attempt-id", required=True)
    54	    parser.add_argument("--pre-custody-locator", required=True)
    55	    parser.add_argument("--post-custody-locator", required=True)
    56	    parser.add_argument("--identity-epoch-json", type=Path, required=True)
    57	    parser.add_argument("--t1-bindings-json", type=Path, required=True)
    58	    parser.add_argument(
    59	        "--execute",
    60	        action="store_true",
    61	        help="append the capability; without this flag only validate inputs",
    62	    )
    63	    parser.add_argument(
    64	        "--allow-uncommitted-pin-for-test",
    65	        action="store_true",
    66	        help=argparse.SUPPRESS,
    67	    )
    68	    return parser
    69	
    70	
    71	def main(argv: list[str] | None = None) -> int:
    72	    args = _parser().parse_args(argv)
    73	    try:
    74	        epoch = _json_object(args.identity_epoch_json)
    75	        t1 = _json_object(args.t1_bindings_json)
    76	        slots = {
    77	            "pre": {
    78	                "attempt_id": args.pre_attempt_id,
    79	                "custody_locator": args.pre_custody_locator,
    80	                "identity_epoch": epoch,
    81	                "t1_bindings": t1,
    82	            },
    83	            "post": {
    84	                "attempt_id": args.post_attempt_id,
    85	                "custody_locator": args.post_custody_locator,
    86	                "identity_epoch": epoch,
    87	                "t1_bindings": t1,
    88	            },
    89	        }
    90	        if (
    91	            len(args.plan_sha256) != 64
    92	            or any(char not in "0123456789abcdef" for char in args.plan_sha256)
    93	            or args.pre_attempt_id == args.post_attempt_id
    94	            or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
    95	            or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
    96	            or set(t1) != set(T1_FIELDS)
    97	            or any(t1.get(field) in (None, "") for field in T1_FIELDS)
    98	        ):
    99	            raise ValueError("bracket session inputs are incomplete or malformed")
   100	        if not args.execute:
   101	            output = {
   102	                "schema_version": OUTPUT_SCHEMA,
   103	                "status": "validated_not_reserved",
   104	                "session_schema": BRACKET_SESSION_SCHEMA,
   105	                "session_id": args.session_id,
   106	                "window_id": args.window_id,
   107	                "plan_id": args.plan_id,
   108	                "plan_sha256": args.plan_sha256,
   109	                "evidence_root_id": args.evidence_root_id,
   110	                "slot_attempt_ids": {
   111	                    role: slot["attempt_id"] for role, slot in slots.items()
   112	                },
   113	            }
   114	        else:
   115	            receipt = append_bracket_session_receipt(
   116	                args.ledger,
   117	                session_id=args.session_id,
   118	                window_id=args.window_id,
   119	                plan_id=args.plan_id,
   120	                plan_sha256=args.plan_sha256,
   121	                evidence_root_id=args.evidence_root_id,
   122	                slots=slots,
   123	                head_pin_path=args.head_pin,
   124	                require_committed_pin=not args.allow_uncommitted_pin_for_test,
   125	                repo_root=REPO_ROOT,
   126	            )
   127	            output = {
   128	                "schema_version": OUTPUT_SCHEMA,
   129	                "status": "reserved",
   130	                "receipt": json.loads(canonical_json_bytes(receipt)),
   131	                "terminal_head_pin": None,
   132	                "terminal_head_pin_status": "deferred_until_post_finalization",
   133	            }
   134	    except (CalibrationLedgerError, OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
   135	        print(f"refusing: {exc}", file=sys.stderr)
   136	        return 2
   137	    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
   138	    return 0
   139	
   140	
   141	if __name__ == "__main__":
   142	    raise SystemExit(main())

exec
/bin/zsh -lc 'rg -n "''^(def|class) |''^@dataclass|BRACKET_SESSION|is_governed|_SESSION_|bracket" joulewise/calibration_ledger.py; nl -ba joulewise/calibration_ledger.py | sed -n '"'120,520p'; nl -ba joulewise/calibration_ledger.py | sed -n '520,940p'; nl -ba joulewise/calibration_ledger.py | sed -n '940,1320p'; nl -ba joulewise/calibration_ledger.py | sed -n '1320,1680p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
36:BRACKET_SESSION_SCHEMA = "joulewise.calibration_window_bracket_session.v1"
37:BRACKET_SESSION_OPEN_EVENT = "bracket-session-open"
38:BRACKET_SESSION_FINALIZATION_EVENT = "bracket-session-slot-finalization"
39:BRACKET_SESSION_ABORT_EVENT = "bracket-session-abort"
40:BRACKET_SESSION_SLOTS = ("pre", "post")
106:        "calibration_ledger_bracket_session_conflict": "a bracket session has duplicate, reordered, or conflicting state transitions",
107:        "calibration_ledger_bracket_session_open": "a bracket session has not finalized both slots or recorded a governed abort",
122:class CalibrationLedgerError(ValueError):
126:def _jsonable(value: Any) -> Any:
134:def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
144:def canonical_sha256(value: Mapping[str, Any]) -> str:
148:def _is_sha256(value: object) -> bool:
152:def _normalized_vector(
160:def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
177:def artifact_hashes(custody_dir: Path) -> dict[str, str]:
189:def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
193:def _receipt_digest(receipt: Mapping[str, Any]) -> str:
197:@dataclass(frozen=True)
198:class LedgerObservation:
211:    bracket_session_id: str | None = None
212:    bracket_slot: str | None = None
213:    bracket_window_id: str | None = None
214:    bracket_plan_id: str | None = None
215:    bracket_plan_sha256: str | None = None
216:    bracket_evidence_root_id: str | None = None
231:@dataclass(frozen=True)
232:class CalibrationLedgerSnapshot:
242:    bracket_sessions: tuple["CalibrationBracketSession", ...] = ()
259:    def bracket_session_by_id(self) -> Mapping[str, "CalibrationBracketSession"]:
261:            {session.session_id: session for session in self.bracket_sessions}
265:    def is_governed_open_bracket_extension(self) -> bool:
269:            "calibration_ledger_bracket_session_open",
279:            session for session in self.bracket_sessions if session.state == "open"
289:            and tail[0].get("event") == BRACKET_SESSION_OPEN_EVENT
327:@dataclass(frozen=True)
328:class CalibrationBracketSession:
345:@dataclass(frozen=True)
346:class HistoricalImportPlan:
361:class HistoricalImportDurabilityUncertain(CalibrationLedgerError):
373:@dataclass(frozen=True)
374:class _HistoricalCandidate:
386:def _frozen_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
437:_SESSION_IDENTITY_KEYS = frozenset(
440:_SESSION_OPEN_KEYS = _CHAIN_KEYS | _SESSION_IDENTITY_KEYS | {"slots"}
441:_SESSION_FINALIZATION_KEYS = (
443:    | _SESSION_IDENTITY_KEYS
457:_SESSION_ABORT_KEYS = (
459:    | _SESSION_IDENTITY_KEYS
462:_SESSION_SLOT_KEYS = frozenset(
473:def _valid_chain_fields(receipt: Mapping[str, Any], schema: str) -> bool:
487:def _valid_session_identity(receipt: Mapping[str, Any]) -> bool:
497:def _valid_session_slot_reservation(slot: object, expected_role: str) -> bool:
498:    if not isinstance(slot, Mapping) or set(slot) != _SESSION_SLOT_KEYS:
517:def _valid_session_receipt_shape(receipt: Mapping[str, Any]) -> bool:
520:        BRACKET_SESSION_OPEN_EVENT: _SESSION_OPEN_KEYS,
521:        BRACKET_SESSION_FINALIZATION_EVENT: _SESSION_FINALIZATION_KEYS,
522:        BRACKET_SESSION_ABORT_EVENT: _SESSION_ABORT_KEYS,
527:        or not _valid_chain_fields(receipt, BRACKET_SESSION_SCHEMA)
531:    if event == BRACKET_SESSION_OPEN_EVENT:
535:            and set(slots) == set(BRACKET_SESSION_SLOTS)
538:                for role in BRACKET_SESSION_SLOTS
542:    if event == BRACKET_SESSION_ABORT_EVENT:
551:            and all(slot in BRACKET_SESSION_SLOTS for slot in (*finalized, *unused))
553:            and set((*finalized, *unused)) == set(BRACKET_SESSION_SLOTS)
565:        receipt.get("slot") not in BRACKET_SESSION_SLOTS
596:def _valid_receipt_shape(receipt: object) -> bool:
599:    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
698:def _head_pin(value: object) -> tuple[int, str] | None:
719:def _committed_pin_bytes(path: Path, repo_root: Path) -> bytes | None:
737:def _parse_ledger(raw: bytes) -> tuple[list[Mapping[str, Any]], set[str]]:
776:def _observation_from_receipt(
796:        bracket_session_id=(str(session["session_id"]) if session else None),
797:        bracket_slot=(str(receipt["slot"]) if session else None),
798:        bracket_window_id=(str(session["window_id"]) if session else None),
799:        bracket_plan_id=(str(session["plan_id"]) if session else None),
800:        bracket_plan_sha256=(str(session["plan_sha256"]) if session else None),
801:        bracket_evidence_root_id=(
807:def _session_identity_matches(
810:    return all(receipt.get(field) == open_receipt.get(field) for field in _SESSION_IDENTITY_KEYS)
813:def _bracket_sessions_and_observations(
820:        if receipt.get("schema_version") != BRACKET_SESSION_SCHEMA:
824:        if event == BRACKET_SESSION_OPEN_EVENT:
826:            attempt_ids = {str(slots[role]["attempt_id"]) for role in BRACKET_SESSION_SLOTS}
828:                reasons.add("calibration_ledger_bracket_session_conflict")
839:            reasons.add("calibration_ledger_bracket_session_conflict")
843:            reasons.add("calibration_ledger_bracket_session_conflict")
846:        if event == BRACKET_SESSION_FINALIZATION_EVENT:
848:            expected_slot = BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
860:                reasons.add("calibration_ledger_bracket_session_conflict")
865:        unused_slots = [slot for slot in BRACKET_SESSION_SLOTS if slot not in finals]
867:            event != BRACKET_SESSION_ABORT_EVENT
873:            reasons.add("calibration_ledger_bracket_session_conflict")
891:            reasons.add("calibration_ledger_bracket_session_open")
896:                    "bracket-session-finalized"
898:                    else "bracket-session-aborted"
907:                for slot in BRACKET_SESSION_SLOTS
922:                        for slot in BRACKET_SESSION_SLOTS
936:def _attempts_and_observations(
943:        if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
1004:        _bracket_sessions_and_observations(receipts)
1013:        reasons.add("calibration_ledger_bracket_session_conflict")
1042:def _custody_reasons(
1064:def load_calibration_ledger_snapshot(
1151:    observations, bracket_sessions, state_reasons = _attempts_and_observations(
1158:        for session in bracket_sessions:
1173:        bracket_sessions=tuple(bracket_sessions),
1181:def _new_receipt(
1221:def _new_bracket_session_record(
1230:        "schema_version": BRACKET_SESSION_SCHEMA,
1235:        **{field: session_identity.get(field) for field in _SESSION_IDENTITY_KEYS},
1242:def _json_object_from_bytes(raw: bytes, source: Path) -> Mapping[str, Any]:
1252:def _authenticated_json_object(
1266:def _number_lexemes(raw: bytes, source: Path) -> Mapping[str, Any]:
1276:def _historical_import_table(
1339:def _historical_import_custody_manifest(
1368:def custody_manifest_bytes(value: Mapping[str, Any]) -> bytes:
1383:def _historical_directories(roots: Sequence[Path]) -> tuple[Path, ...]:
1406:def _assert_absolute_nonsymlink_directory(directory: Path) -> Path:
1427:def _read_contained_nofollow(directory: Path, relative: str) -> bytes:
1474:def _governed_raw_nofollow(directory: Path) -> dict[str, bytes]:
1481:def _inspect_historical_candidate(
1593:def _discover_historical_candidates(
1626:def generate_historical_custody_manifest(
1682:def prepare_historical_import(
1812:    observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
1813:    del bracket_sessions
1830:def _require_genesis_bootstrap_state(
1865:def _ledger_lock_path(ledger_path: Path) -> Path:
1870:def _open_ledger_lock(ledger_path: Path) -> int:
1910:def _fsync_parent_directory(path: Path) -> None:
1935:def _write_bootstrap_payload(handle: BinaryIO, payload: bytes) -> None:
1941:def _reauthenticate_historical_import_plan(plan: HistoricalImportPlan) -> None:
1961:def bootstrap_historical_import(
2067:def _locked_append(
2103:def _authenticated_head_pin(
2123:def append_bracket_session_receipt(
2136:    """Atomically reserve exactly one immutable pre/post bracket capability.
2152:    if not isinstance(slots, Mapping) or set(slots) != set(BRACKET_SESSION_SLOTS):
2153:        raise CalibrationLedgerError("bracket session must reserve exactly pre and post")
2154:    for role in BRACKET_SESSION_SLOTS:
2169:        for role in BRACKET_SESSION_SLOTS
2171:        raise CalibrationLedgerError("bracket session reservation is malformed")
2176:        raise CalibrationLedgerError("bracket session slot attempts must be distinct")
2204:            normalized_slots[role]["attempt_id"] for role in BRACKET_SESSION_SLOTS
2210:            raise CalibrationLedgerError("bracket session identity conflicts with ledger")
2211:        return _new_bracket_session_record(
2214:            event=BRACKET_SESSION_OPEN_EVENT,
2222:def finalize_bracket_session_slot(
2237:    if slot not in BRACKET_SESSION_SLOTS:
2238:        raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
2249:        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
2255:            raise CalibrationLedgerError("bracket session is not open")
2256:        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
2259:                f"bracket session slot must finalize in order: expected {expected_slot}"
2264:            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
2277:        return _new_bracket_session_record(
2280:            event=BRACKET_SESSION_FINALIZATION_EVENT,
2282:                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
2301:def abort_bracket_session(
2310:        raise CalibrationLedgerError("bracket session abort reason must be nonempty")
2315:        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
2322:            raise CalibrationLedgerError("bracket session is not open")
2326:            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
2331:        return _new_bracket_session_record(
2334:            event=BRACKET_SESSION_ABORT_EVENT,
2336:                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
2341:                    role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
2350:def terminal_head_pin_for_session(
2369:        raise CalibrationLedgerError("bracket session is not terminal")
2381:def append_pending_receipt(
2420:        observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
2422:        del bracket_sessions
2456:def finalize_attempt_receipt(
2476:        observations, bracket_sessions, reasons = _attempts_and_observations(
2479:        del observations, bracket_sessions
2527:def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
2541:    "BRACKET_SESSION_ABORT_EVENT",
2542:    "BRACKET_SESSION_FINALIZATION_EVENT",
2543:    "BRACKET_SESSION_OPEN_EVENT",
2544:    "BRACKET_SESSION_SCHEMA",
2545:    "BRACKET_SESSION_SLOTS",
2568:    "append_bracket_session_receipt",
2569:    "abort_bracket_session",
2576:    "finalize_bracket_session_slot",
   120	
   121	
   122	class CalibrationLedgerError(ValueError):
   123	    """A writer-side ledger operation cannot preserve the D-109 contract."""
   124	
   125	
   126	def _jsonable(value: Any) -> Any:
   127	    if isinstance(value, Mapping):
   128	        return {key: _jsonable(item) for key, item in value.items()}
   129	    if isinstance(value, (list, tuple)):
   130	        return [_jsonable(item) for item in value]
   131	    return value
   132	
   133	
   134	def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
   135	    return json.dumps(
   136	        _jsonable(value),
   137	        sort_keys=True,
   138	        separators=(",", ":"),
   139	        ensure_ascii=False,
   140	        allow_nan=False,
   141	    ).encode("utf-8")
   142	
   143	
   144	def canonical_sha256(value: Mapping[str, Any]) -> str:
   145	    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
   146	
   147	
   148	def _is_sha256(value: object) -> bool:
   149	    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None
   150	
   151	
   152	def _normalized_vector(
   153	    value: Mapping[str, Any] | None,
   154	    fields: Sequence[str],
   155	) -> dict[str, Any]:
   156	    source = value if isinstance(value, Mapping) else {}
   157	    return {field: source.get(field) for field in fields}
   158	
   159	
   160	def content_id_from_artifact_hashes(artifact_sha256: Mapping[str, Any]) -> str | None:
   161	    """Return the path-independent identity of canonical primary bytes.
   162	
   163	    The authenticated evidence document and its manifest are the canonical
   164	    byte pair.  A copied custody tree therefore retains the same identity.
   165	    Other receipt hashes remain custody checks but do not manufacture a new
   166	    observation when a derived representation is regenerated.
   167	    """
   168	
   169	    identity = {
   170	        name: artifact_sha256.get(name) for name in CONTENT_ID_ARTIFACTS
   171	    }
   172	    if any(not _is_sha256(value) for value in identity.values()):
   173	        return None
   174	    return canonical_sha256(identity)
   175	
   176	
   177	def artifact_hashes(custody_dir: Path) -> dict[str, str]:
   178	    """Hash every governed artifact present in one finalized custody tree."""
   179	
   180	    root = Path(custody_dir)
   181	    result: dict[str, str] = {}
   182	    for relative in GOVERNED_ARTIFACTS:
   183	        path = root / relative
   184	        if path.is_file():
   185	            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
   186	    return result
   187	
   188	
   189	def receipt_core(receipt: Mapping[str, Any]) -> dict[str, Any]:
   190	    return {key: value for key, value in receipt.items() if key != "receipt_digest"}
   191	
   192	
   193	def _receipt_digest(receipt: Mapping[str, Any]) -> str:
   194	    return canonical_sha256(receipt_core(receipt))
   195	
   196	
   197	@dataclass(frozen=True)
   198	class LedgerObservation:
   199	    sequence: int
   200	    receipt_digest: str
   201	    attempt_id: str
   202	    content_id: str | None
   203	    artifact_sha256: Mapping[str, str]
   204	    identity_epoch: Mapping[str, Any]
   205	    t1_bindings: Mapping[str, Any]
   206	    capture_wall_time_s: str | None
   207	    exact_bound_lexeme_s: str | None
   208	    disposition: str
   209	    custody_locator: str
   210	    observation_kind: str = "live-capture"
   211	    bracket_session_id: str | None = None
   212	    bracket_slot: str | None = None
   213	    bracket_window_id: str | None = None
   214	    bracket_plan_id: str | None = None
   215	    bracket_plan_sha256: str | None = None
   216	    bracket_evidence_root_id: str | None = None
   217	
   218	    @property
   219	    def classification_disposition(self) -> str:
   220	        """Map the writer terminal state onto the R2 observation schema."""
   221	
   222	        return (
   223	            "unresolved" if self.disposition == "abandoned" else self.disposition
   224	        )
   225	
   226	    @property
   227	    def is_historical_import(self) -> bool:
   228	        return self.observation_kind == "historical-import"
   229	
   230	
   231	@dataclass(frozen=True)
   232	class CalibrationLedgerSnapshot:
   233	    """One immutable, fully checked view threaded through an evaluation."""
   234	
   235	    ledger_schema: str
   236	    ledger_path: Path
   237	    head_sequence: int
   238	    head_digest: str
   239	    receipts: tuple[Mapping[str, Any], ...]
   240	    observations: tuple[LedgerObservation, ...]
   241	    refusal_reasons: tuple[str, ...]
   242	    bracket_sessions: tuple["CalibrationBracketSession", ...] = ()
   243	    baseline_sequence: int | None = None
   244	    baseline_digest: str | None = None
   245	    committed_head_sequence: int | None = None
   246	    committed_head_digest: str | None = None
   247	
   248	    @property
   249	    def valid(self) -> bool:
   250	        return not self.refusal_reasons
   251	
   252	    @property
   253	    def observation_by_attempt(self) -> Mapping[str, LedgerObservation]:
   254	        return MappingProxyType(
   255	            {observation.attempt_id: observation for observation in self.observations}
   256	        )
   257	
   258	    @property
   259	    def bracket_session_by_id(self) -> Mapping[str, "CalibrationBracketSession"]:
   260	        return MappingProxyType(
   261	            {session.session_id: session for session in self.bracket_sessions}
   262	        )
   263	
   264	    @property
   265	    def is_governed_open_bracket_extension(self) -> bool:
   266	        """Whether the physical/pin gap is exactly one reserved open session."""
   267	
   268	        allowed = {
   269	            "calibration_ledger_bracket_session_open",
   270	            "calibration_ledger_head_mismatch",
   271	        }
   272	        if (
   273	            set(self.refusal_reasons) != allowed
   274	            or self.committed_head_sequence is None
   275	            or self.committed_head_digest is None
   276	        ):
   277	            return False
   278	        open_sessions = [
   279	            session for session in self.bracket_sessions if session.state == "open"
   280	        ]
   281	        if len(open_sessions) != 1:
   282	            return False
   283	        session = open_sessions[0]
   284	        if session.capability_sequence != self.committed_head_sequence + 1:
   285	            return False
   286	        tail = self.receipts[self.committed_head_sequence :]
   287	        return bool(
   288	            tail
   289	            and tail[0].get("event") == BRACKET_SESSION_OPEN_EVENT
   290	            and tail[0].get("predecessor_digest") == self.committed_head_digest
   291	            and all(row.get("session_id") == session.session_id for row in tail)
   292	        )
   293	
   294	    @property
   295	    def observations_by_content(self) -> Mapping[str, tuple[LedgerObservation, ...]]:
   296	        grouped: dict[str, list[LedgerObservation]] = {}
   297	        for observation in self.observations:
   298	            if observation.content_id is not None:
   299	                grouped.setdefault(observation.content_id, []).append(observation)
   300	        return MappingProxyType(
   301	            {key: tuple(value) for key, value in sorted(grouped.items())}
   302	        )
   303	
   304	    def post_cutoff_live_observations(
   305	        self, cutoff_sequence: int
   306	    ) -> tuple[LedgerObservation, ...]:
   307	        """Return only fresh live-capture observations after ``cutoff_sequence``.
   308	
   309	        Historical bootstrap finalizations are deliberately excluded even
   310	        when a caller compares them with the genesis sequence-zero cutoff.
   311	        """
   312	
   313	        if (
   314	            isinstance(cutoff_sequence, bool)
   315	            or not isinstance(cutoff_sequence, int)
   316	            or cutoff_sequence < 0
   317	        ):
   318	            raise CalibrationLedgerError("cutoff_sequence must be nonnegative")
   319	        return tuple(
   320	            observation
   321	            for observation in self.observations
   322	            if observation.sequence > cutoff_sequence
   323	            and not observation.is_historical_import
   324	        )
   325	
   326	
   327	@dataclass(frozen=True)
   328	class CalibrationBracketSession:
   329	    """Authenticated state of one prospectively reserved two-slot window."""
   330	
   331	    session_id: str
   332	    window_id: str
   333	    plan_id: str
   334	    plan_sha256: str
   335	    evidence_root_id: str
   336	    capability_receipt_digest: str
   337	    capability_sequence: int
   338	    slot_attempt_ids: Mapping[str, str]
   339	    state: str
   340	    finalized_slots: Mapping[str, LedgerObservation]
   341	    abort_receipt_digest: str | None = None
   342	    abort_reason: str | None = None
   343	
   344	
   345	@dataclass(frozen=True)
   346	class HistoricalImportPlan:
   347	    """Deterministic, authenticated genesis bootstrap prepared in memory."""
   348	
   349	    receipts: tuple[Mapping[str, Any], ...]
   350	    final_sequence: int
   351	    head_digest: str
   352	    head_pin: Mapping[str, Any]
   353	    disposition_table_sha256: str
   354	    custody_manifest_sha256: str
   355	
   356	    @property
   357	    def ledger_bytes(self) -> bytes:
   358	        return b"".join(canonical_json_bytes(row) + b"\n" for row in self.receipts)
   359	
   360	
   361	class HistoricalImportDurabilityUncertain(CalibrationLedgerError):
   362	    """The import committed, but its parent-directory fsync did not confirm."""
   363	
   364	    outcome = "committed_durability_uncertain"
   365	
   366	    def __init__(self, plan: HistoricalImportPlan) -> None:
   367	        super().__init__(
   368	            "historical import committed but parent-directory durability is uncertain"
   369	        )
   370	        self.plan = plan
   371	
   372	
   373	@dataclass(frozen=True)
   374	class _HistoricalCandidate:
   375	    attempt_id: str
   376	    content_id: str
   377	    artifact_sha256: Mapping[str, str]
   378	    identity_epoch: Mapping[str, Any]
   379	    t1_bindings: Mapping[str, Any]
   380	    capture_wall_time_s: str | None
   381	    exact_bound_lexeme_s: str | None
   382	    custody_sort_key: str
   383	    custody_locator: str
   384	
   385	
   386	def _frozen_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
   387	    frozen: dict[str, Any] = {}
   388	    for key, item in value.items():
   389	        if isinstance(item, Mapping):
   390	            frozen[key] = _frozen_mapping(item)
   391	        elif isinstance(item, list):
   392	            frozen[key] = tuple(
   393	                _frozen_mapping(child) if isinstance(child, Mapping) else child
   394	                for child in item
   395	            )
   396	        else:
   397	            frozen[key] = item
   398	    return MappingProxyType(frozen)
   399	
   400	
   401	_RECEIPT_KEYS = frozenset(
   402	    {
   403	        "schema_version",
   404	        "ledger_schema",
   405	        "sequence",
   406	        "predecessor_digest",
   407	        "event",
   408	        "attempt_id",
   409	        "content_id",
   410	        "artifact_sha256",
   411	        "identity_epoch",
   412	        "t1_bindings",
   413	        "capture_wall_time_s",
   414	        "exact_bound_lexeme_s",
   415	        "disposition",
   416	        "custody_locator",
   417	        "receipt_digest",
   418	    }
   419	)
   420	_HISTORICAL_IMPORT_INPUT_SHA256_KEY = "historical_import_input_sha256"
   421	_HISTORICAL_IMPORT_INPUT_SHA256_KEYS = frozenset(
   422	    {"disposition_table", "custody_manifest"}
   423	)
   424	_HISTORICAL_IMPORT_RESERVATION_KEYS = (
   425	    _RECEIPT_KEYS | {_HISTORICAL_IMPORT_INPUT_SHA256_KEY}
   426	)
   427	_CHAIN_KEYS = frozenset(
   428	    {
   429	        "schema_version",
   430	        "ledger_schema",
   431	        "sequence",
   432	        "predecessor_digest",
   433	        "event",
   434	        "receipt_digest",
   435	    }
   436	)
   437	_SESSION_IDENTITY_KEYS = frozenset(
   438	    {"session_id", "window_id", "plan_id", "plan_sha256", "evidence_root_id"}
   439	)
   440	_SESSION_OPEN_KEYS = _CHAIN_KEYS | _SESSION_IDENTITY_KEYS | {"slots"}
   441	_SESSION_FINALIZATION_KEYS = (
   442	    _CHAIN_KEYS
   443	    | _SESSION_IDENTITY_KEYS
   444	    | {
   445	        "slot",
   446	        "attempt_id",
   447	        "content_id",
   448	        "artifact_sha256",
   449	        "identity_epoch",
   450	        "t1_bindings",
   451	        "capture_wall_time_s",
   452	        "exact_bound_lexeme_s",
   453	        "disposition",
   454	        "custody_locator",
   455	    }
   456	)
   457	_SESSION_ABORT_KEYS = (
   458	    _CHAIN_KEYS
   459	    | _SESSION_IDENTITY_KEYS
   460	    | {"finalized_slots", "unused_slots", "reason"}
   461	)
   462	_SESSION_SLOT_KEYS = frozenset(
   463	    {
   464	        "attempt_id",
   465	        "custody_locator",
   466	        "identity_epoch",
   467	        "t1_bindings",
   468	        "expected_time_role",
   469	    }
   470	)
   471	
   472	
   473	def _valid_chain_fields(receipt: Mapping[str, Any], schema: str) -> bool:
   474	    sequence = receipt.get("sequence")
   475	    return (
   476	        receipt.get("schema_version") == schema
   477	        and receipt.get("ledger_schema") == LEDGER_SCHEMA
   478	        and not isinstance(sequence, bool)
   479	        and isinstance(sequence, int)
   480	        and sequence >= 1
   481	        and _is_sha256(receipt.get("predecessor_digest"))
   482	        and _is_sha256(receipt.get("receipt_digest"))
   483	        and receipt.get("receipt_digest") == _receipt_digest(receipt)
   484	    )
   485	
   486	
   487	def _valid_session_identity(receipt: Mapping[str, Any]) -> bool:
   488	    return (
   489	        all(
   490	            isinstance(receipt.get(field), str) and bool(receipt.get(field))
   491	            for field in ("session_id", "window_id", "plan_id", "evidence_root_id")
   492	        )
   493	        and _is_sha256(receipt.get("plan_sha256"))
   494	    )
   495	
   496	
   497	def _valid_session_slot_reservation(slot: object, expected_role: str) -> bool:
   498	    if not isinstance(slot, Mapping) or set(slot) != _SESSION_SLOT_KEYS:
   499	        return False
   500	    epoch = slot.get("identity_epoch")
   501	    t1 = slot.get("t1_bindings")
   502	    return (
   503	        isinstance(slot.get("attempt_id"), str)
   504	        and bool(slot.get("attempt_id"))
   505	        and isinstance(slot.get("custody_locator"), str)
   506	        and bool(slot.get("custody_locator"))
   507	        and slot.get("expected_time_role") == expected_role
   508	        and isinstance(epoch, Mapping)
   509	        and set(epoch) == set(IDENTITY_EPOCH_FIELDS)
   510	        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
   511	        and isinstance(t1, Mapping)
   512	        and set(t1) == set(T1_FIELDS)
   513	        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
   514	    )
   515	
   516	
   517	def _valid_session_receipt_shape(receipt: Mapping[str, Any]) -> bool:
   518	    event = receipt.get("event")
   519	    expected_keys = {
   520	        BRACKET_SESSION_OPEN_EVENT: _SESSION_OPEN_KEYS,
   520	        BRACKET_SESSION_OPEN_EVENT: _SESSION_OPEN_KEYS,
   521	        BRACKET_SESSION_FINALIZATION_EVENT: _SESSION_FINALIZATION_KEYS,
   522	        BRACKET_SESSION_ABORT_EVENT: _SESSION_ABORT_KEYS,
   523	    }.get(event)
   524	    if (
   525	        expected_keys is None
   526	        or set(receipt) != expected_keys
   527	        or not _valid_chain_fields(receipt, BRACKET_SESSION_SCHEMA)
   528	        or not _valid_session_identity(receipt)
   529	    ):
   530	        return False
   531	    if event == BRACKET_SESSION_OPEN_EVENT:
   532	        slots = receipt.get("slots")
   533	        return (
   534	            isinstance(slots, Mapping)
   535	            and set(slots) == set(BRACKET_SESSION_SLOTS)
   536	            and all(
   537	                _valid_session_slot_reservation(slots.get(role), role)
   538	                for role in BRACKET_SESSION_SLOTS
   539	            )
   540	            and slots["pre"]["attempt_id"] != slots["post"]["attempt_id"]
   541	        )
   542	    if event == BRACKET_SESSION_ABORT_EVENT:
   543	        finalized = receipt.get("finalized_slots")
   544	        unused = receipt.get("unused_slots")
   545	        reason = receipt.get("reason")
   546	        return (
   547	            isinstance(finalized, Sequence)
   548	            and not isinstance(finalized, (str, bytes))
   549	            and isinstance(unused, Sequence)
   550	            and not isinstance(unused, (str, bytes))
   551	            and all(slot in BRACKET_SESSION_SLOTS for slot in (*finalized, *unused))
   552	            and len(set((*finalized, *unused))) == len(finalized) + len(unused)
   553	            and set((*finalized, *unused)) == set(BRACKET_SESSION_SLOTS)
   554	            and isinstance(reason, str)
   555	            and bool(reason)
   556	        )
   557	    disposition = receipt.get("disposition")
   558	    artifacts = receipt.get("artifact_sha256")
   559	    epoch = receipt.get("identity_epoch")
   560	    t1 = receipt.get("t1_bindings")
   561	    capture = receipt.get("capture_wall_time_s")
   562	    bound = receipt.get("exact_bound_lexeme_s")
   563	    content_id = receipt.get("content_id")
   564	    if (
   565	        receipt.get("slot") not in BRACKET_SESSION_SLOTS
   566	        or not isinstance(receipt.get("attempt_id"), str)
   567	        or not receipt.get("attempt_id")
   568	        or disposition not in FINAL_DISPOSITIONS
   569	        or not isinstance(receipt.get("custody_locator"), str)
   570	        or not isinstance(artifacts, Mapping)
   571	        or any(
   572	            not isinstance(name, str) or not name or not _is_sha256(digest)
   573	            for name, digest in artifacts.items()
   574	        )
   575	        or not isinstance(epoch, Mapping)
   576	        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
   577	        or not isinstance(t1, Mapping)
   578	        or set(t1) != set(T1_FIELDS)
   579	        or (capture is not None and not isinstance(capture, str))
   580	        or (bound is not None and not isinstance(bound, str))
   581	        or (content_id is not None and not _is_sha256(content_id))
   582	    ):
   583	        return False
   584	    if disposition == "abandoned":
   585	        return content_id == content_id_from_artifact_hashes(artifacts)
   586	    return (
   587	        content_id is not None
   588	        and content_id_from_artifact_hashes(artifacts) == content_id
   589	        and bool(receipt.get("custody_locator"))
   590	        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
   591	        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
   592	        and capture is not None
   593	    )
   594	
   595	
   596	def _valid_receipt_shape(receipt: object) -> bool:
   597	    if not isinstance(receipt, Mapping):
   598	        return False
   599	    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
   600	        return _valid_session_receipt_shape(receipt)
   601	    sequence = receipt.get("sequence")
   602	    event = receipt.get("event")
   603	    expected_keys = (
   604	        _HISTORICAL_IMPORT_RESERVATION_KEYS
   605	        if event == HISTORICAL_IMPORT_RESERVATION_EVENT
   606	        else _RECEIPT_KEYS
   607	    )
   608	    if set(receipt) != expected_keys:
   609	        return False
   610	    disposition = receipt.get("disposition")
   611	    artifacts = receipt.get("artifact_sha256")
   612	    epoch = receipt.get("identity_epoch")
   613	    t1 = receipt.get("t1_bindings")
   614	    capture = receipt.get("capture_wall_time_s")
   615	    bound = receipt.get("exact_bound_lexeme_s")
   616	    if (
   617	        receipt.get("schema_version") != RECEIPT_SCHEMA
   618	        or receipt.get("ledger_schema") != LEDGER_SCHEMA
   619	        or isinstance(sequence, bool)
   620	        or not isinstance(sequence, int)
   621	        or sequence < 1
   622	        or not _is_sha256(receipt.get("predecessor_digest"))
   623	        or event
   624	        not in {
   625	            "reservation",
   626	            "finalization",
   627	            HISTORICAL_IMPORT_RESERVATION_EVENT,
   628	            HISTORICAL_IMPORT_FINALIZATION_EVENT,
   629	        }
   630	        or not isinstance(receipt.get("attempt_id"), str)
   631	        or not receipt.get("attempt_id")
   632	        or disposition not in ALL_DISPOSITIONS
   633	        or not isinstance(receipt.get("custody_locator"), str)
   634	        or not isinstance(artifacts, Mapping)
   635	        or any(
   636	            not isinstance(name, str) or not name or not _is_sha256(digest)
   637	            for name, digest in artifacts.items()
   638	        )
   639	        or not isinstance(epoch, Mapping)
   640	        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
   641	        or not isinstance(t1, Mapping)
   642	        or set(t1) != set(T1_FIELDS)
   643	        or (capture is not None and not isinstance(capture, str))
   644	        or (bound is not None and not isinstance(bound, str))
   645	        or not _is_sha256(receipt.get("receipt_digest"))
   646	        or receipt.get("receipt_digest") != _receipt_digest(receipt)
   647	    ):
   648	        return False
   649	    content_id = receipt.get("content_id")
   650	    if content_id is not None and not _is_sha256(content_id):
   651	        return False
   652	    if event in {"reservation", HISTORICAL_IMPORT_RESERVATION_EVENT}:
   653	        historical_input_sha256 = receipt.get(
   654	            _HISTORICAL_IMPORT_INPUT_SHA256_KEY
   655	        )
   656	        return (
   657	            disposition == "pending"
   658	            and content_id is None
   659	            and not artifacts
   660	            and capture is None
   661	            and bound is None
   662	            and all(
   663	                epoch.get(field) not in (None, "")
   664	                for field in IDENTITY_EPOCH_FIELDS
   665	            )
   666	            and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
   667	            and (
   668	                event != HISTORICAL_IMPORT_RESERVATION_EVENT
   669	                or isinstance(historical_input_sha256, Mapping)
   670	                and set(historical_input_sha256)
   671	                == _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
   672	                and all(
   673	                    _is_sha256(historical_input_sha256.get(name))
   674	                    for name in _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
   675	                )
   676	            )
   677	        )
   678	    if disposition not in FINAL_DISPOSITIONS:
   679	        return False
   680	    if disposition == "abandoned":
   681	        # R1 retains the terminal writer state as ``abandoned`` while R2
   682	        # classifies it as unresolved.  When canonical primary bytes exist,
   683	        # preserve their authentic content identity; a partial/no-content
   684	        # attempt remains representable with a null content id.
   685	        return content_id == content_id_from_artifact_hashes(artifacts)
   686	    if (
   687	        content_id is None
   688	        or content_id_from_artifact_hashes(artifacts) != content_id
   689	        or not receipt.get("custody_locator")
   690	        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
   691	        or any(t1.get(field) in (None, "") for field in T1_FIELDS)
   692	        or capture is None
   693	    ):
   694	        return False
   695	    return True
   696	
   697	
   698	def _head_pin(value: object) -> tuple[int, str] | None:
   699	    if not isinstance(value, Mapping) or set(value) != {
   700	        "sequence",
   701	        "head_digest",
   702	        "ledger_schema",
   703	    }:
   704	        return None
   705	    sequence = value.get("sequence")
   706	    digest = value.get("head_digest")
   707	    if (
   708	        value.get("ledger_schema") != LEDGER_SCHEMA
   709	        or isinstance(sequence, bool)
   710	        or not isinstance(sequence, int)
   711	        or sequence < 0
   712	        or not _is_sha256(digest)
   713	        or (sequence == 0 and digest != GENESIS_DIGEST)
   714	    ):
   715	        return None
   716	    return sequence, str(digest)
   717	
   718	
   719	def _committed_pin_bytes(path: Path, repo_root: Path) -> bytes | None:
   720	    try:
   721	        relative = Path(path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
   722	    except (OSError, ValueError):
   723	        return None
   724	    try:
   725	        completed = subprocess.run(
   726	            ["git", "show", f"HEAD:{relative}"],
   727	            cwd=repo_root,
   728	            check=True,
   729	            stdout=subprocess.PIPE,
   730	            stderr=subprocess.DEVNULL,
   731	        )
   732	    except (OSError, subprocess.CalledProcessError):
   733	        return None
   734	    return completed.stdout
   735	
   736	
   737	def _parse_ledger(raw: bytes) -> tuple[list[Mapping[str, Any]], set[str]]:
   738	    receipts: list[Mapping[str, Any]] = []
   739	    reasons: set[str] = set()
   740	    if not raw:
   741	        return receipts, reasons
   742	    try:
   743	        text = raw.decode("utf-8")
   744	    except UnicodeDecodeError:
   745	        return receipts, {"calibration_ledger_malformed"}
   746	    if not text.endswith("\n"):
   747	        reasons.add("calibration_ledger_malformed")
   748	    predecessor = GENESIS_DIGEST
   749	    expected_sequence = 1
   750	    seen_digests: set[str] = set()
   751	    for line in text.splitlines():
   752	        if not line.strip():
   753	            reasons.add("calibration_ledger_malformed")
   754	            continue
   755	        try:
   756	            value = json.loads(line)
   757	        except json.JSONDecodeError:
   758	            reasons.add("calibration_ledger_malformed")
   759	            continue
   760	        if not _valid_receipt_shape(value):
   761	            reasons.add("calibration_ledger_malformed")
   762	            continue
   763	        if (
   764	            value["sequence"] != expected_sequence
   765	            or value["predecessor_digest"] != predecessor
   766	            or value["receipt_digest"] in seen_digests
   767	        ):
   768	            reasons.add("calibration_ledger_chain_conflict")
   769	        expected_sequence += 1
   770	        predecessor = value["receipt_digest"]
   771	        seen_digests.add(predecessor)
   772	        receipts.append(value)
   773	    return receipts, reasons
   774	
   775	
   776	def _observation_from_receipt(
   777	    receipt: Mapping[str, Any],
   778	    *,
   779	    observation_kind: str,
   780	    session: Mapping[str, Any] | None = None,
   781	) -> LedgerObservation:
   782	    content_id = receipt.get("content_id")
   783	    return LedgerObservation(
   784	        sequence=int(receipt["sequence"]),
   785	        receipt_digest=str(receipt["receipt_digest"]),
   786	        attempt_id=str(receipt["attempt_id"]),
   787	        content_id=str(content_id) if isinstance(content_id, str) else None,
   788	        artifact_sha256=MappingProxyType(dict(receipt["artifact_sha256"])),
   789	        identity_epoch=MappingProxyType(dict(receipt["identity_epoch"])),
   790	        t1_bindings=MappingProxyType(dict(receipt["t1_bindings"])),
   791	        capture_wall_time_s=receipt.get("capture_wall_time_s"),
   792	        exact_bound_lexeme_s=receipt.get("exact_bound_lexeme_s"),
   793	        disposition=str(receipt["disposition"]),
   794	        custody_locator=str(receipt["custody_locator"]),
   795	        observation_kind=observation_kind,
   796	        bracket_session_id=(str(session["session_id"]) if session else None),
   797	        bracket_slot=(str(receipt["slot"]) if session else None),
   798	        bracket_window_id=(str(session["window_id"]) if session else None),
   799	        bracket_plan_id=(str(session["plan_id"]) if session else None),
   800	        bracket_plan_sha256=(str(session["plan_sha256"]) if session else None),
   801	        bracket_evidence_root_id=(
   802	            str(session["evidence_root_id"]) if session else None
   803	        ),
   804	    )
   805	
   806	
   807	def _session_identity_matches(
   808	    receipt: Mapping[str, Any], open_receipt: Mapping[str, Any]
   809	) -> bool:
   810	    return all(receipt.get(field) == open_receipt.get(field) for field in _SESSION_IDENTITY_KEYS)
   811	
   812	
   813	def _bracket_sessions_and_observations(
   814	    receipts: Sequence[Mapping[str, Any]],
   815	) -> tuple[list[CalibrationBracketSession], list[LedgerObservation], set[str]]:
   816	    states: dict[str, dict[str, Any]] = {}
   817	    claimed_attempts: set[str] = set()
   818	    reasons: set[str] = set()
   819	    for receipt in receipts:
   820	        if receipt.get("schema_version") != BRACKET_SESSION_SCHEMA:
   821	            continue
   822	        event = receipt["event"]
   823	        session_id = str(receipt["session_id"])
   824	        if event == BRACKET_SESSION_OPEN_EVENT:
   825	            slots = receipt["slots"]
   826	            attempt_ids = {str(slots[role]["attempt_id"]) for role in BRACKET_SESSION_SLOTS}
   827	            if session_id in states or attempt_ids & claimed_attempts:
   828	                reasons.add("calibration_ledger_bracket_session_conflict")
   829	                continue
   830	            claimed_attempts.update(attempt_ids)
   831	            states[session_id] = {
   832	                "open": receipt,
   833	                "finals": {},
   834	                "abort": None,
   835	            }
   836	            continue
   837	        state = states.get(session_id)
   838	        if state is None:
   839	            reasons.add("calibration_ledger_bracket_session_conflict")
   840	            continue
   841	        open_receipt = state["open"]
   842	        if not _session_identity_matches(receipt, open_receipt):
   843	            reasons.add("calibration_ledger_bracket_session_conflict")
   844	            continue
   845	        finals = state["finals"]
   846	        if event == BRACKET_SESSION_FINALIZATION_EVENT:
   847	            slot = str(receipt["slot"])
   848	            expected_slot = BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
   849	            reserved = open_receipt["slots"].get(slot)
   850	            if (
   851	                state["abort"] is not None
   852	                or slot != expected_slot
   853	                or slot in finals
   854	                or not isinstance(reserved, Mapping)
   855	                or receipt["attempt_id"] != reserved["attempt_id"]
   856	                or receipt["custody_locator"] != reserved["custody_locator"]
   857	                or dict(receipt["identity_epoch"]) != dict(reserved["identity_epoch"])
   858	                or dict(receipt["t1_bindings"]) != dict(reserved["t1_bindings"])
   859	            ):
   860	                reasons.add("calibration_ledger_bracket_session_conflict")
   861	                continue
   862	            finals[slot] = receipt
   863	            continue
   864	        finalized_slots = list(finals)
   865	        unused_slots = [slot for slot in BRACKET_SESSION_SLOTS if slot not in finals]
   866	        if (
   867	            event != BRACKET_SESSION_ABORT_EVENT
   868	            or state["abort"] is not None
   869	            or len(finals) == 2
   870	            or receipt["finalized_slots"] != finalized_slots
   871	            or receipt["unused_slots"] != unused_slots
   872	        ):
   873	            reasons.add("calibration_ledger_bracket_session_conflict")
   874	            continue
   875	        state["abort"] = receipt
   876	
   877	    sessions: list[CalibrationBracketSession] = []
   878	    completed_observations: list[LedgerObservation] = []
   879	    for session_id, state in sorted(
   880	        states.items(), key=lambda item: int(item[1]["open"]["sequence"])
   881	    ):
   882	        open_receipt = state["open"]
   883	        finals = state["finals"]
   884	        abort = state["abort"]
   885	        if abort is not None:
   886	            session_state = "aborted"
   887	        elif len(finals) == 2:
   888	            session_state = "finalized"
   889	        else:
   890	            session_state = "open"
   891	            reasons.add("calibration_ledger_bracket_session_open")
   892	        finalized_observations = {
   893	            slot: _observation_from_receipt(
   894	                receipt,
   895	                observation_kind=(
   896	                    "bracket-session-finalized"
   897	                    if session_state == "finalized"
   898	                    else "bracket-session-aborted"
   899	                ),
   900	                session=open_receipt,
   901	            )
   902	            for slot, receipt in finals.items()
   903	        }
   904	        if session_state != "aborted":
   905	            completed_observations.extend(
   906	                finalized_observations[slot]
   907	                for slot in BRACKET_SESSION_SLOTS
   908	                if slot in finalized_observations
   909	            )
   910	        sessions.append(
   911	            CalibrationBracketSession(
   912	                session_id=session_id,
   913	                window_id=str(open_receipt["window_id"]),
   914	                plan_id=str(open_receipt["plan_id"]),
   915	                plan_sha256=str(open_receipt["plan_sha256"]),
   916	                evidence_root_id=str(open_receipt["evidence_root_id"]),
   917	                capability_receipt_digest=str(open_receipt["receipt_digest"]),
   918	                capability_sequence=int(open_receipt["sequence"]),
   919	                slot_attempt_ids=MappingProxyType(
   920	                    {
   921	                        slot: str(open_receipt["slots"][slot]["attempt_id"])
   922	                        for slot in BRACKET_SESSION_SLOTS
   923	                    }
   924	                ),
   925	                state=session_state,
   926	                finalized_slots=MappingProxyType(finalized_observations),
   927	                abort_receipt_digest=(
   928	                    str(abort["receipt_digest"]) if abort is not None else None
   929	                ),
   930	                abort_reason=(str(abort["reason"]) if abort is not None else None),
   931	            )
   932	        )
   933	    return sessions, completed_observations, reasons
   934	
   935	
   936	def _attempts_and_observations(
   937	    receipts: Sequence[Mapping[str, Any]],
   938	) -> tuple[list[LedgerObservation], list[CalibrationBracketSession], set[str]]:
   939	    pending: dict[str, Mapping[str, Any]] = {}
   940	    finalized: dict[str, Mapping[str, Any]] = {}
   940	    finalized: dict[str, Mapping[str, Any]] = {}
   941	    reasons: set[str] = set()
   942	    for receipt in receipts:
   943	        if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
   944	            continue
   945	        attempt_id = str(receipt["attempt_id"])
   946	        if receipt["event"] in {
   947	            "reservation",
   948	            HISTORICAL_IMPORT_RESERVATION_EVENT,
   949	        }:
   950	            if attempt_id in pending or attempt_id in finalized:
   951	                reasons.add("calibration_ledger_attempt_conflict")
   952	            else:
   953	                pending[attempt_id] = receipt
   954	            continue
   955	        reservation = pending.get(attempt_id)
   956	        expected_final_event = (
   957	            HISTORICAL_IMPORT_FINALIZATION_EVENT
   958	            if reservation is not None
   959	            and reservation["event"] == HISTORICAL_IMPORT_RESERVATION_EVENT
   960	            else "finalization"
   961	        )
   962	        if (
   963	            reservation is None
   964	            or attempt_id in finalized
   965	            or receipt["event"] != expected_final_event
   966	        ):
   967	            reasons.add("calibration_ledger_attempt_conflict")
   968	        else:
   969	            finalized[attempt_id] = receipt
   970	    if set(pending) - set(finalized):
   971	        reasons.add("calibration_ledger_pending")
   972	
   973	    observations: list[LedgerObservation] = []
   974	    content_classification: dict[str, tuple[str, tuple[tuple[str, Any], ...]]] = {}
   975	    for attempt_id, receipt in sorted(
   976	        finalized.items(), key=lambda item: int(item[1]["sequence"])
   977	    ):
   978	        content_id = receipt.get("content_id")
   979	        epoch = dict(receipt["identity_epoch"])
   980	        if isinstance(content_id, str):
   981	            classification = (
   982	                (
   983	                    "unresolved"
   984	                    if receipt["disposition"] == "abandoned"
   985	                    else str(receipt["disposition"])
   986	                ),
   987	                tuple((field, epoch.get(field)) for field in IDENTITY_EPOCH_FIELDS),
   988	            )
   989	            previous = content_classification.get(content_id)
   990	            if previous is not None and previous != classification:
   991	                reasons.add("calibration_ledger_content_conflict")
   992	            content_classification[content_id] = classification
   993	        observations.append(
   994	            _observation_from_receipt(
   995	                receipt,
   996	                observation_kind=(
   997	                    "historical-import"
   998	                    if receipt["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
   999	                    else "live-capture"
  1000	                ),
  1001	            )
  1002	        )
  1003	    sessions, session_observations, session_reasons = (
  1004	        _bracket_sessions_and_observations(receipts)
  1005	    )
  1006	    reasons.update(session_reasons)
  1007	    session_attempt_ids = {
  1008	        attempt_id
  1009	        for session in sessions
  1010	        for attempt_id in session.slot_attempt_ids.values()
  1011	    }
  1012	    if set(pending) & session_attempt_ids:
  1013	        reasons.add("calibration_ledger_bracket_session_conflict")
  1014	    observations.extend(session_observations)
  1015	    content_classification.clear()
  1016	    classification_observations = list(observations)
  1017	    visible_attempts = {observation.attempt_id for observation in observations}
  1018	    classification_observations.extend(
  1019	        observation
  1020	        for session in sessions
  1021	        for observation in session.finalized_slots.values()
  1022	        if observation.attempt_id not in visible_attempts
  1023	    )
  1024	    for observation in classification_observations:
  1025	        if observation.content_id is None:
  1026	            continue
  1027	        classification = (
  1028	            observation.classification_disposition,
  1029	            tuple(
  1030	                (field, observation.identity_epoch.get(field))
  1031	                for field in IDENTITY_EPOCH_FIELDS
  1032	            ),
  1033	        )
  1034	        previous = content_classification.get(observation.content_id)
  1035	        if previous is not None and previous != classification:
  1036	            reasons.add("calibration_ledger_content_conflict")
  1037	        content_classification[observation.content_id] = classification
  1038	    observations.sort(key=lambda observation: observation.sequence)
  1039	    return observations, sessions, reasons
  1040	
  1041	
  1042	def _custody_reasons(
  1043	    observations: Sequence[LedgerObservation], repo_root: Path
  1044	) -> set[str]:
  1045	    for observation in observations:
  1046	        if not observation.artifact_sha256:
  1047	            if observation.disposition == "abandoned":
  1048	                continue
  1049	            return {"calibration_ledger_custody_invalid"}
  1050	        root = Path(observation.custody_locator)
  1051	        if not root.is_absolute():
  1052	            root = Path(repo_root) / root
  1053	        for relative, expected in observation.artifact_sha256.items():
  1054	            path = root / relative
  1055	            try:
  1056	                actual = hashlib.sha256(path.read_bytes()).hexdigest()
  1057	            except OSError:
  1058	                return {"calibration_ledger_custody_invalid"}
  1059	            if actual != expected:
  1060	                return {"calibration_ledger_custody_invalid"}
  1061	    return set()
  1062	
  1063	
  1064	def load_calibration_ledger_snapshot(
  1065	    ledger_path: Path = DEFAULT_LEDGER_PATH,
  1066	    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
  1067	    *,
  1068	    baseline_sequence: int | None = None,
  1069	    baseline_digest: str | None = None,
  1070	    require_committed_pin: bool = True,
  1071	    verify_custody: bool = True,
  1072	    repo_root: Path = REPO_ROOT,
  1073	) -> CalibrationLedgerSnapshot:
  1074	    """Load, authenticate, and freeze exactly one ledger snapshot.
  1075	
  1076	    A proper physical prefix of the pin is classified explicitly as rollback;
  1077	    any other physical/pinned disagreement is a stale-head mismatch.  The
  1078	    baseline must occur at its exact sequence in the same complete chain.
  1079	    This closes workflow omission, unregistered evidence, and rollback or
  1080	    stale-head consumption; it does not defend against a malicious trusted
  1081	    writer or a rewrite of both Git and the full ledger history.
  1082	    """
  1083	
  1084	    ledger_path = Path(ledger_path)
  1085	    head_pin_path = Path(head_pin_path)
  1086	    reasons: set[str] = set()
  1087	    try:
  1088	        pin_raw = head_pin_path.read_bytes()
  1089	        pin_value = json.loads(pin_raw)
  1090	    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
  1091	        pin_raw = b""
  1092	        pin_value = None
  1093	    pin = _head_pin(pin_value)
  1094	    if pin is None:
  1095	        reasons.add("calibration_ledger_malformed")
  1096	        pinned_sequence, pinned_digest = 0, GENESIS_DIGEST
  1097	    else:
  1098	        pinned_sequence, pinned_digest = pin
  1099	    try:
  1100	        raw = ledger_path.read_bytes()
  1101	    except OSError:
  1102	        raw = b""
  1103	        if pinned_sequence > 0:
  1104	            reasons.add("calibration_ledger_missing")
  1105	    genesis_development_bootstrap = (
  1106	        pinned_sequence == 0
  1107	        and pinned_digest == GENESIS_DIGEST
  1108	        and not raw
  1109	        and not ledger_path.exists()
  1110	    )
  1111	    if (
  1112	        require_committed_pin
  1113	        # The checked-in fixture starts at genesis.  Before its first commit,
  1114	        # an absent physical ledger cannot license a claim (there are no
  1115	        # endpoints); permitting this development-only empty view avoids a
  1116	        # circular "commit before tests" bootstrap. Any physical byte or any
  1117	        # non-genesis pin remains strictly commit-authenticated.
  1118	        and not genesis_development_bootstrap
  1119	        and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
  1120	    ):
  1121	        reasons.add("calibration_ledger_head_uncommitted")
  1122	    receipts, parse_reasons = _parse_ledger(raw)
  1123	    reasons.update(parse_reasons)
  1124	    physical_sequence = len(receipts)
  1125	    physical_digest = (
  1126	        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
  1127	    )
  1128	    if (physical_sequence, physical_digest) != (pinned_sequence, pinned_digest):
  1129	        if physical_sequence < pinned_sequence:
  1130	            reasons.add("calibration_ledger_rollback")
  1131	        else:
  1132	            reasons.add("calibration_ledger_head_mismatch")
  1133	    if baseline_sequence is not None or baseline_digest is not None:
  1134	        if (
  1135	            isinstance(baseline_sequence, bool)
  1136	            or not isinstance(baseline_sequence, int)
  1137	            or baseline_sequence < 0
  1138	            or not _is_sha256(baseline_digest)
  1139	        ):
  1140	            reasons.add("calibration_ledger_baseline_missing")
  1141	        else:
  1142	            in_chain = (
  1143	                baseline_digest == GENESIS_DIGEST
  1144	                if baseline_sequence == 0
  1145	                else baseline_sequence <= len(receipts)
  1146	                and receipts[baseline_sequence - 1]["receipt_digest"]
  1147	                == baseline_digest
  1148	            )
  1149	            if not in_chain or baseline_sequence > pinned_sequence:
  1150	                reasons.add("calibration_ledger_baseline_missing")
  1151	    observations, bracket_sessions, state_reasons = _attempts_and_observations(
  1152	        receipts
  1153	    )
  1154	    reasons.update(state_reasons)
  1155	    if verify_custody:
  1156	        custody_observations = list(observations)
  1157	        custody_attempt_ids = {observation.attempt_id for observation in observations}
  1158	        for session in bracket_sessions:
  1159	            custody_observations.extend(
  1160	                observation
  1161	                for observation in session.finalized_slots.values()
  1162	                if observation.attempt_id not in custody_attempt_ids
  1163	            )
  1164	        reasons.update(_custody_reasons(custody_observations, repo_root))
  1165	    return CalibrationLedgerSnapshot(
  1166	        ledger_schema=LEDGER_SCHEMA,
  1167	        ledger_path=ledger_path,
  1168	        head_sequence=physical_sequence,
  1169	        head_digest=physical_digest,
  1170	        receipts=tuple(_frozen_mapping(receipt) for receipt in receipts),
  1171	        observations=tuple(observations),
  1172	        refusal_reasons=tuple(sorted(reasons)),
  1173	        bracket_sessions=tuple(bracket_sessions),
  1174	        baseline_sequence=baseline_sequence,
  1175	        baseline_digest=baseline_digest,
  1176	        committed_head_sequence=pinned_sequence,
  1177	        committed_head_digest=pinned_digest,
  1178	    )
  1179	
  1180	
  1181	def _new_receipt(
  1182	    *,
  1183	    sequence: int,
  1184	    predecessor_digest: str,
  1185	    event: str,
  1186	    attempt_id: str,
  1187	    content_id: str | None,
  1188	    artifacts: Mapping[str, str],
  1189	    identity_epoch: Mapping[str, Any] | None,
  1190	    t1_bindings: Mapping[str, Any] | None,
  1191	    capture_wall_time_s: str | None,
  1192	    exact_bound_lexeme_s: str | None,
  1193	    disposition: str,
  1194	    custody_locator: str,
  1195	    historical_import_input_sha256: Mapping[str, str] | None = None,
  1196	) -> dict[str, Any]:
  1197	    receipt: dict[str, Any] = {
  1198	        "schema_version": RECEIPT_SCHEMA,
  1199	        "ledger_schema": LEDGER_SCHEMA,
  1200	        "sequence": sequence,
  1201	        "predecessor_digest": predecessor_digest,
  1202	        "event": event,
  1203	        "attempt_id": attempt_id,
  1204	        "content_id": content_id,
  1205	        "artifact_sha256": dict(sorted(artifacts.items())),
  1206	        "identity_epoch": _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS),
  1207	        "t1_bindings": _normalized_vector(t1_bindings, T1_FIELDS),
  1208	        "capture_wall_time_s": capture_wall_time_s,
  1209	        "exact_bound_lexeme_s": exact_bound_lexeme_s,
  1210	        "disposition": disposition,
  1211	        "custody_locator": custody_locator,
  1212	    }
  1213	    if historical_import_input_sha256 is not None:
  1214	        receipt[_HISTORICAL_IMPORT_INPUT_SHA256_KEY] = dict(
  1215	            sorted(historical_import_input_sha256.items())
  1216	        )
  1217	    receipt["receipt_digest"] = _receipt_digest(receipt)
  1218	    return receipt
  1219	
  1220	
  1221	def _new_bracket_session_record(
  1222	    *,
  1223	    sequence: int,
  1224	    predecessor_digest: str,
  1225	    event: str,
  1226	    session_identity: Mapping[str, Any],
  1227	    fields: Mapping[str, Any],
  1228	) -> dict[str, Any]:
  1229	    receipt = {
  1230	        "schema_version": BRACKET_SESSION_SCHEMA,
  1231	        "ledger_schema": LEDGER_SCHEMA,
  1232	        "sequence": sequence,
  1233	        "predecessor_digest": predecessor_digest,
  1234	        "event": event,
  1235	        **{field: session_identity.get(field) for field in _SESSION_IDENTITY_KEYS},
  1236	        **dict(fields),
  1237	    }
  1238	    receipt["receipt_digest"] = _receipt_digest(receipt)
  1239	    return receipt
  1240	
  1241	
  1242	def _json_object_from_bytes(raw: bytes, source: Path) -> Mapping[str, Any]:
  1243	    try:
  1244	        value = json.loads(raw)
  1245	    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
  1246	        raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
  1247	    if not isinstance(value, Mapping):
  1248	        raise CalibrationLedgerError(f"{source}: expected a JSON object")
  1249	    return value
  1250	
  1251	
  1252	def _authenticated_json_object(
  1253	    raw: bytes,
  1254	    expected_sha256: str,
  1255	    *,
  1256	    label: str,
  1257	) -> Mapping[str, Any]:
  1258	    if not _is_sha256(expected_sha256):
  1259	        raise CalibrationLedgerError(f"expected {label} sha256 is malformed")
  1260	    observed = hashlib.sha256(raw).hexdigest()
  1261	    if observed != expected_sha256:
  1262	        raise CalibrationLedgerError(f"{label} sha256 mismatch")
  1263	    return _json_object_from_bytes(raw, Path(label))
  1264	
  1265	
  1266	def _number_lexemes(raw: bytes, source: Path) -> Mapping[str, Any]:
  1267	    try:
  1268	        value = json.loads(raw, parse_float=str, parse_int=str)
  1269	    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
  1270	        raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
  1271	    if not isinstance(value, Mapping):
  1272	        raise CalibrationLedgerError(f"{source}: expected a JSON object")
  1273	    return value
  1274	
  1275	
  1276	def _historical_import_table(
  1277	    value: Mapping[str, Any],
  1278	) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
  1279	    if set(value) != {
  1280	        "schema_version",
  1281	        "ledger_schema",
  1282	        "identity_epoch",
  1283	        "members",
  1284	    }:
  1285	        raise CalibrationLedgerError("historical import table has invalid keys")
  1286	    if (
  1287	        value.get("schema_version") != HISTORICAL_IMPORT_TABLE_SCHEMA
  1288	        or value.get("ledger_schema") != LEDGER_SCHEMA
  1289	    ):
  1290	        raise CalibrationLedgerError("historical import table schema mismatch")
  1291	    epoch = value.get("identity_epoch")
  1292	    members = value.get("members")
  1293	    if (
  1294	        not isinstance(epoch, Mapping)
  1295	        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
  1296	        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
  1297	        or not isinstance(members, list)
  1298	        or not members
  1299	    ):
  1300	        raise CalibrationLedgerError("historical import table is incomplete")
  1301	
  1302	    by_content: dict[str, Mapping[str, Any]] = {}
  1303	    attempt_ids: set[str] = set()
  1304	    for member in members:
  1305	        if not isinstance(member, Mapping) or set(member) != {
  1306	            "attempt_id",
  1307	            "content_id",
  1308	            "artifact_sha256",
  1309	            "disposition",
  1310	        }:
  1311	            raise CalibrationLedgerError("historical import member has invalid keys")
  1312	        attempt_id = member.get("attempt_id")
  1313	        content_id = member.get("content_id")
  1314	        artifacts = member.get("artifact_sha256")
  1315	        disposition = member.get("disposition")
  1316	        if (
  1317	            not isinstance(attempt_id, str)
  1318	            or not attempt_id
  1319	            or not _is_sha256(content_id)
  1320	            or not isinstance(artifacts, Mapping)
  1320	            or not isinstance(artifacts, Mapping)
  1321	            or set(artifacts) != set(GOVERNED_ARTIFACTS)
  1322	            or any(not _is_sha256(item) for item in artifacts.values())
  1323	            or content_id_from_artifact_hashes(artifacts) != content_id
  1324	            or disposition not in HISTORICAL_IMPORT_DISPOSITIONS
  1325	        ):
  1326	            raise CalibrationLedgerError("historical import member is malformed")
  1327	        if attempt_id in attempt_ids:
  1328	            raise CalibrationLedgerError(
  1329	                "historical import attempt_id collision; content_id tiebreak is "
  1330	                "diagnostic only"
  1331	            )
  1332	        if str(content_id) in by_content:
  1333	            raise CalibrationLedgerError("historical import content_id is duplicated")
  1334	        attempt_ids.add(attempt_id)
  1335	        by_content[str(content_id)] = member
  1336	    return dict(epoch), by_content
  1337	
  1338	
  1339	def _historical_import_custody_manifest(
  1340	    value: Mapping[str, Any],
  1341	    *,
  1342	    expected_content_ids: set[str],
  1343	) -> dict[str, Path]:
  1344	    if set(value) != {"schema_version", "ledger_schema", "members"}:
  1345	        raise CalibrationLedgerError("custody manifest has invalid keys")
  1346	    if (
  1347	        value.get("schema_version") != HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA
  1348	        or value.get("ledger_schema") != LEDGER_SCHEMA
  1349	        or not isinstance(value.get("members"), Mapping)
  1350	    ):
  1351	        raise CalibrationLedgerError("custody manifest schema mismatch")
  1352	    members = value["members"]
  1353	    if set(members) != expected_content_ids:
  1354	        raise CalibrationLedgerError(
  1355	            "custody manifest content set differs from disposition table"
  1356	        )
  1357	    result: dict[str, Path] = {}
  1358	    for content_id, locator in members.items():
  1359	        if not _is_sha256(content_id) or not isinstance(locator, str) or not locator:
  1360	            raise CalibrationLedgerError("custody manifest member is malformed")
  1361	        path = Path(locator)
  1362	        if not path.is_absolute():
  1363	            raise CalibrationLedgerError("custody manifest locator is not absolute")
  1364	        result[str(content_id)] = path
  1365	    return result
  1366	
  1367	
  1368	def custody_manifest_bytes(value: Mapping[str, Any]) -> bytes:
  1369	    """Return the exact reviewable byte representation emitted by the CLI."""
  1370	
  1371	    return (
  1372	        json.dumps(
  1373	            _jsonable(value),
  1374	            sort_keys=True,
  1375	            indent=2,
  1376	            ensure_ascii=False,
  1377	            allow_nan=False,
  1378	        )
  1379	        + "\n"
  1380	    ).encode("utf-8")
  1381	
  1382	
  1383	def _historical_directories(roots: Sequence[Path]) -> tuple[Path, ...]:
  1384	    directories: set[Path] = set()
  1385	    if not roots:
  1386	        raise CalibrationLedgerError("at least one historical import root is required")
  1387	    for supplied in roots:
  1388	        try:
  1389	            root = Path(supplied).resolve(strict=True)
  1390	        except OSError as exc:
  1391	            raise CalibrationLedgerError(
  1392	                f"historical import root is unreadable: {supplied}"
  1393	            ) from exc
  1394	        if (root / "manifest.json").is_file():
  1395	            directories.add(root)
  1396	        directories.update(path.parent for path in root.glob("*/manifest.json"))
  1397	        directories.update(
  1398	            path.parent
  1399	            for path in root.glob("instrument_validation/*/manifest.json")
  1400	        )
  1401	    if not directories:
  1402	        raise CalibrationLedgerError("historical import roots contain no candidates")
  1403	    return tuple(sorted(directories, key=lambda path: path.as_posix()))
  1404	
  1405	
  1406	def _assert_absolute_nonsymlink_directory(directory: Path) -> Path:
  1407	    path = Path(directory)
  1408	    if not path.is_absolute():
  1409	        raise CalibrationLedgerError("custody locator is not absolute")
  1410	    current = Path(path.anchor)
  1411	    try:
  1412	        for component in path.parts[1:]:
  1413	            current /= component
  1414	            if stat.S_ISLNK(os.lstat(current).st_mode):
  1415	                raise CalibrationLedgerError(
  1416	                    f"custody locator resolves through a symlink: {path}"
  1417	                )
  1418	        if not stat.S_ISDIR(os.stat(path, follow_symlinks=False).st_mode):
  1419	            raise CalibrationLedgerError(f"custody locator is not a directory: {path}")
  1420	    except FileNotFoundError as exc:
  1421	        raise CalibrationLedgerError(f"custody locator is missing: {path}") from exc
  1422	    except OSError as exc:
  1423	        raise CalibrationLedgerError(f"custody locator is unreadable: {path}") from exc
  1424	    return path
  1425	
  1426	
  1427	def _read_contained_nofollow(directory: Path, relative: str) -> bytes:
  1428	    root = _assert_absolute_nonsymlink_directory(directory)
  1429	    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
  1430	    nofollow = getattr(os, "O_NOFOLLOW", 0)
  1431	    directory_flags = flags | getattr(os, "O_DIRECTORY", 0) | nofollow
  1432	    descriptor = os.open(root, directory_flags)
  1433	    try:
  1434	        components = Path(relative).parts
  1435	        if not components or any(item in {"", ".", ".."} for item in components):
  1436	            raise CalibrationLedgerError("governed artifact path is not contained")
  1437	        parent = descriptor
  1438	        owned_parent = False
  1439	        try:
  1440	            for component in components[:-1]:
  1441	                child = os.open(component, directory_flags, dir_fd=parent)
  1442	                if owned_parent:
  1443	                    os.close(parent)
  1444	                parent = child
  1445	                owned_parent = True
  1446	            artifact = os.open(components[-1], flags | nofollow, dir_fd=parent)
  1447	            try:
  1448	                if not stat.S_ISREG(os.fstat(artifact).st_mode):
  1449	                    raise CalibrationLedgerError(
  1450	                        f"governed artifact is not a regular file: {root / relative}"
  1451	                    )
  1452	                chunks: list[bytes] = []
  1453	                while True:
  1454	                    chunk = os.read(artifact, 1024 * 1024)
  1455	                    if not chunk:
  1456	                        break
  1457	                    chunks.append(chunk)
  1458	                return b"".join(chunks)
  1459	            finally:
  1460	                os.close(artifact)
  1461	        finally:
  1462	            if owned_parent:
  1463	                os.close(parent)
  1464	    except CalibrationLedgerError:
  1465	        raise
  1466	    except OSError as exc:
  1467	        raise CalibrationLedgerError(
  1468	            f"governed artifact is unreadable without symlink traversal: {root / relative}"
  1469	        ) from exc
  1470	    finally:
  1471	        os.close(descriptor)
  1472	
  1473	
  1474	def _governed_raw_nofollow(directory: Path) -> dict[str, bytes]:
  1475	    return {
  1476	        relative: _read_contained_nofollow(directory, relative)
  1477	        for relative in GOVERNED_ARTIFACTS
  1478	    }
  1479	
  1480	
  1481	def _inspect_historical_candidate(
  1482	    directory: Path,
  1483	    *,
  1484	    checkout_root: Path | None,
  1485	    expected_epoch: Mapping[str, Any],
  1486	) -> tuple[str | None, _HistoricalCandidate | None, str | None]:
  1487	    manifest_path = directory / "manifest.json"
  1488	    evidence_path = directory / "instrument_evidence.json"
  1489	    try:
  1490	        manifest_raw = _read_contained_nofollow(directory, "manifest.json")
  1491	        evidence_raw = _read_contained_nofollow(
  1492	            directory, "instrument_evidence.json"
  1493	        )
  1494	        manifest = _json_object_from_bytes(manifest_raw, manifest_path)
  1495	        evidence = _json_object_from_bytes(evidence_raw, evidence_path)
  1496	    except (OSError, CalibrationLedgerError) as exc:
  1497	        return None, None, f"{directory}: primary evidence is unreadable: {exc}"
  1498	
  1499	    bindings = evidence.get("bindings")
  1500	    if not isinstance(bindings, Mapping):
  1501	        return None, None, f"{directory}: evidence bindings are missing"
  1502	    epoch = _normalized_vector(bindings, IDENTITY_EPOCH_FIELDS)
  1503	    if epoch != dict(expected_epoch):
  1504	        return None, None, None
  1505	
  1506	    primary_hashes = {
  1507	        "instrument_evidence.json": hashlib.sha256(evidence_raw).hexdigest(),
  1508	        "manifest.json": hashlib.sha256(manifest_raw).hexdigest(),
  1509	    }
  1510	    content_id = content_id_from_artifact_hashes(primary_hashes)
  1511	    if content_id is None:
  1512	        return None, None, f"{directory}: content identity is incomplete"
  1513	
  1514	    try:
  1515	        resolved = _assert_absolute_nonsymlink_directory(directory)
  1516	        custody_sort_key = (
  1517	            resolved.relative_to(checkout_root).as_posix()
  1518	            if checkout_root is not None
  1519	            else resolved.as_posix()
  1520	        )
  1521	    except (OSError, ValueError, CalibrationLedgerError) as exc:
  1522	        return content_id, None, f"{directory}: custody is outside checkout root: {exc}"
  1523	
  1524	    try:
  1525	        raw_by_name = _governed_raw_nofollow(directory)
  1526	    except CalibrationLedgerError as exc:
  1527	        return content_id, None, f"{directory}: hash-complete custody is missing: {exc}"
  1528	    hashes = {
  1529	        name: hashlib.sha256(raw_by_name[name]).hexdigest()
  1530	        for name in GOVERNED_ARTIFACTS
  1531	    }
  1532	
  1533	    manifest_artifacts = manifest.get("artifacts")
  1534	    evidence_artifacts = evidence.get("artifact_sha256")
  1535	    if (
  1536	        not isinstance(manifest_artifacts, Mapping)
  1537	        or set(manifest_artifacts) != set(MANIFEST_BOUND_ARTIFACTS)
  1538	        or any(
  1539	            manifest_artifacts.get(name) != hashes[name]
  1540	            for name in MANIFEST_BOUND_ARTIFACTS
  1541	        )
  1542	    ):
  1543	        return content_id, None, f"{directory}: manifest artifact hash mismatch"
  1544	    if (
  1545	        not isinstance(evidence_artifacts, Mapping)
  1546	        or set(evidence_artifacts) != set(EVIDENCE_BOUND_ARTIFACTS)
  1547	        or any(
  1548	            evidence_artifacts.get(name) != hashes[name]
  1549	            for name in EVIDENCE_BOUND_ARTIFACTS
  1550	        )
  1551	    ):
  1552	        return content_id, None, f"{directory}: evidence artifact hash mismatch"
  1553	
  1554	    attempt_id = evidence.get("validation_id")
  1555	    if (
  1556	        not isinstance(attempt_id, str)
  1557	        or not attempt_id
  1558	        or manifest.get("validation_id") != attempt_id
  1559	    ):
  1560	        return content_id, None, f"{directory}: attempt identity mismatch"
  1561	    t1_bindings = _normalized_vector(bindings, T1_FIELDS)
  1562	    if any(t1_bindings.get(field) in (None, "") for field in T1_FIELDS):
  1563	        return content_id, None, f"{directory}: full T1 binding is incomplete"
  1564	    try:
  1565	        lexemes = _number_lexemes(evidence_raw, evidence_path)
  1566	    except CalibrationLedgerError as exc:
  1567	        return content_id, None, str(exc)
  1568	    capture = lexemes.get("capture_wall_time_s")
  1569	    bound = lexemes.get("b_fiducial_s")
  1570	    if capture is not None and not isinstance(capture, str):
  1571	        return content_id, None, f"{directory}: capture time lexeme is invalid"
  1572	    if bound is not None and not isinstance(bound, str):
  1573	        return content_id, None, f"{directory}: bound lexeme is invalid"
  1574	    if capture is None:
  1575	        return content_id, None, f"{directory}: capture time is missing"
  1576	    return (
  1577	        content_id,
  1578	        _HistoricalCandidate(
  1579	            attempt_id=attempt_id,
  1580	            content_id=content_id,
  1581	            artifact_sha256=MappingProxyType(hashes),
  1582	            identity_epoch=MappingProxyType(epoch),
  1583	            t1_bindings=MappingProxyType(t1_bindings),
  1584	            capture_wall_time_s=capture,
  1585	            exact_bound_lexeme_s=bound,
  1586	            custody_sort_key=custody_sort_key,
  1587	            custody_locator=resolved.as_posix(),
  1588	        ),
  1589	        None,
  1590	    )
  1591	
  1592	
  1593	def _discover_historical_candidates(
  1594	    *,
  1595	    roots: Sequence[Path],
  1596	    checkout_root: Path,
  1597	    expected_epoch: Mapping[str, Any],
  1598	) -> tuple[dict[str, list[_HistoricalCandidate]], dict[str, list[str]]]:
  1599	    try:
  1600	        checkout = Path(checkout_root).resolve(strict=True)
  1601	    except OSError as exc:
  1602	        raise CalibrationLedgerError("checkout root is unreadable") from exc
  1603	
  1604	    complete: dict[str, list[_HistoricalCandidate]] = {}
  1605	    incomplete: dict[str, list[str]] = {}
  1606	    unknown_errors: list[str] = []
  1607	    for directory in _historical_directories(roots):
  1608	        content_id, candidate, error = _inspect_historical_candidate(
  1609	            directory,
  1610	            checkout_root=checkout,
  1611	            expected_epoch=expected_epoch,
  1612	        )
  1613	        if candidate is not None:
  1614	            complete.setdefault(candidate.content_id, []).append(candidate)
  1615	        elif error is not None:
  1616	            if content_id is None:
  1617	                unknown_errors.append(error)
  1618	            else:
  1619	                incomplete.setdefault(content_id, []).append(error)
  1620	    if unknown_errors:
  1621	        raise CalibrationLedgerError(sorted(unknown_errors)[0])
  1622	
  1623	    return complete, incomplete
  1624	
  1625	
  1626	def generate_historical_custody_manifest(
  1627	    *,
  1628	    roots: Sequence[Path],
  1629	    checkout_root: Path,
  1630	    disposition_table_raw: bytes,
  1631	    expected_disposition_table_sha256: str,
  1632	) -> Mapping[str, Any]:
  1633	    """Apply the lexicographic selection rule for a lead-reviewed manifest."""
  1634	
  1635	    table = _authenticated_json_object(
  1636	        disposition_table_raw,
  1637	        expected_disposition_table_sha256,
  1638	        label="disposition table",
  1639	    )
  1640	    expected_epoch, table_by_content = _historical_import_table(table)
  1641	    complete, incomplete = _discover_historical_candidates(
  1642	        roots=roots,
  1643	        checkout_root=checkout_root,
  1644	        expected_epoch=expected_epoch,
  1645	    )
  1646	    expected_ids = set(table_by_content)
  1647	    extra_ids = sorted((set(complete) | set(incomplete)) - expected_ids)
  1648	    missing_ids = sorted(expected_ids - set(complete))
  1649	    if extra_ids:
  1650	        raise CalibrationLedgerError(
  1651	            f"historical import table omits authenticated content_id {extra_ids[0]}"
  1652	        )
  1653	    if missing_ids:
  1654	        detail = sorted(incomplete.get(missing_ids[0], []))
  1655	        if detail:
  1656	            raise CalibrationLedgerError(detail[0])
  1657	        raise CalibrationLedgerError(
  1658	            f"historical import content_id is missing: {missing_ids[0]}"
  1659	        )
  1660	    members: dict[str, str] = {}
  1661	    for content_id in sorted(expected_ids):
  1662	        candidate = min(
  1663	            complete[content_id], key=lambda item: item.custody_sort_key
  1664	        )
  1665	        member = table_by_content[content_id]
  1666	        if candidate.attempt_id != member["attempt_id"]:
  1667	            raise CalibrationLedgerError(
  1668	                f"{content_id}: attempt_id differs from disposition table"
  1669	            )
  1670	        if dict(candidate.artifact_sha256) != dict(member["artifact_sha256"]):
  1671	            raise CalibrationLedgerError(
  1672	                f"{content_id}: artifact hashes differ from disposition table"
  1673	            )
  1674	        members[content_id] = candidate.custody_locator
  1675	    return {
  1676	        "schema_version": HISTORICAL_IMPORT_CUSTODY_MANIFEST_SCHEMA,
  1677	        "ledger_schema": LEDGER_SCHEMA,
  1678	        "members": members,
  1679	    }
  1680	

exec
/bin/zsh -lc "nl -ba joulewise/calibration_ledger.py | sed -n '400,650p'; nl -ba joulewise/calibration_ledger.py | sed -n '650,1025p'; nl -ba joulewise/calibration_ledger.py | sed -n '1025,1190p'; nl -ba joulewise/calibration_ledger.py | sed -n '2040,2405p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
   400	
   401	_RECEIPT_KEYS = frozenset(
   402	    {
   403	        "schema_version",
   404	        "ledger_schema",
   405	        "sequence",
   406	        "predecessor_digest",
   407	        "event",
   408	        "attempt_id",
   409	        "content_id",
   410	        "artifact_sha256",
   411	        "identity_epoch",
   412	        "t1_bindings",
   413	        "capture_wall_time_s",
   414	        "exact_bound_lexeme_s",
   415	        "disposition",
   416	        "custody_locator",
   417	        "receipt_digest",
   418	    }
   419	)
   420	_HISTORICAL_IMPORT_INPUT_SHA256_KEY = "historical_import_input_sha256"
   421	_HISTORICAL_IMPORT_INPUT_SHA256_KEYS = frozenset(
   422	    {"disposition_table", "custody_manifest"}
   423	)
   424	_HISTORICAL_IMPORT_RESERVATION_KEYS = (
   425	    _RECEIPT_KEYS | {_HISTORICAL_IMPORT_INPUT_SHA256_KEY}
   426	)
   427	_CHAIN_KEYS = frozenset(
   428	    {
   429	        "schema_version",
   430	        "ledger_schema",
   431	        "sequence",
   432	        "predecessor_digest",
   433	        "event",
   434	        "receipt_digest",
   435	    }
   436	)
   437	_SESSION_IDENTITY_KEYS = frozenset(
   438	    {"session_id", "window_id", "plan_id", "plan_sha256", "evidence_root_id"}
   439	)
   440	_SESSION_OPEN_KEYS = _CHAIN_KEYS | _SESSION_IDENTITY_KEYS | {"slots"}
   441	_SESSION_FINALIZATION_KEYS = (
   442	    _CHAIN_KEYS
   443	    | _SESSION_IDENTITY_KEYS
   444	    | {
   445	        "slot",
   446	        "attempt_id",
   447	        "content_id",
   448	        "artifact_sha256",
   449	        "identity_epoch",
   450	        "t1_bindings",
   451	        "capture_wall_time_s",
   452	        "exact_bound_lexeme_s",
   453	        "disposition",
   454	        "custody_locator",
   455	    }
   456	)
   457	_SESSION_ABORT_KEYS = (
   458	    _CHAIN_KEYS
   459	    | _SESSION_IDENTITY_KEYS
   460	    | {"finalized_slots", "unused_slots", "reason"}
   461	)
   462	_SESSION_SLOT_KEYS = frozenset(
   463	    {
   464	        "attempt_id",
   465	        "custody_locator",
   466	        "identity_epoch",
   467	        "t1_bindings",
   468	        "expected_time_role",
   469	    }
   470	)
   471	
   472	
   473	def _valid_chain_fields(receipt: Mapping[str, Any], schema: str) -> bool:
   474	    sequence = receipt.get("sequence")
   475	    return (
   476	        receipt.get("schema_version") == schema
   477	        and receipt.get("ledger_schema") == LEDGER_SCHEMA
   478	        and not isinstance(sequence, bool)
   479	        and isinstance(sequence, int)
   480	        and sequence >= 1
   481	        and _is_sha256(receipt.get("predecessor_digest"))
   482	        and _is_sha256(receipt.get("receipt_digest"))
   483	        and receipt.get("receipt_digest") == _receipt_digest(receipt)
   484	    )
   485	
   486	
   487	def _valid_session_identity(receipt: Mapping[str, Any]) -> bool:
   488	    return (
   489	        all(
   490	            isinstance(receipt.get(field), str) and bool(receipt.get(field))
   491	            for field in ("session_id", "window_id", "plan_id", "evidence_root_id")
   492	        )
   493	        and _is_sha256(receipt.get("plan_sha256"))
   494	    )
   495	
   496	
   497	def _valid_session_slot_reservation(slot: object, expected_role: str) -> bool:
   498	    if not isinstance(slot, Mapping) or set(slot) != _SESSION_SLOT_KEYS:
   499	        return False
   500	    epoch = slot.get("identity_epoch")
   501	    t1 = slot.get("t1_bindings")
   502	    return (
   503	        isinstance(slot.get("attempt_id"), str)
   504	        and bool(slot.get("attempt_id"))
   505	        and isinstance(slot.get("custody_locator"), str)
   506	        and bool(slot.get("custody_locator"))
   507	        and slot.get("expected_time_role") == expected_role
   508	        and isinstance(epoch, Mapping)
   509	        and set(epoch) == set(IDENTITY_EPOCH_FIELDS)
   510	        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
   511	        and isinstance(t1, Mapping)
   512	        and set(t1) == set(T1_FIELDS)
   513	        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
   514	    )
   515	
   516	
   517	def _valid_session_receipt_shape(receipt: Mapping[str, Any]) -> bool:
   518	    event = receipt.get("event")
   519	    expected_keys = {
   520	        BRACKET_SESSION_OPEN_EVENT: _SESSION_OPEN_KEYS,
   521	        BRACKET_SESSION_FINALIZATION_EVENT: _SESSION_FINALIZATION_KEYS,
   522	        BRACKET_SESSION_ABORT_EVENT: _SESSION_ABORT_KEYS,
   523	    }.get(event)
   524	    if (
   525	        expected_keys is None
   526	        or set(receipt) != expected_keys
   527	        or not _valid_chain_fields(receipt, BRACKET_SESSION_SCHEMA)
   528	        or not _valid_session_identity(receipt)
   529	    ):
   530	        return False
   531	    if event == BRACKET_SESSION_OPEN_EVENT:
   532	        slots = receipt.get("slots")
   533	        return (
   534	            isinstance(slots, Mapping)
   535	            and set(slots) == set(BRACKET_SESSION_SLOTS)
   536	            and all(
   537	                _valid_session_slot_reservation(slots.get(role), role)
   538	                for role in BRACKET_SESSION_SLOTS
   539	            )
   540	            and slots["pre"]["attempt_id"] != slots["post"]["attempt_id"]
   541	        )
   542	    if event == BRACKET_SESSION_ABORT_EVENT:
   543	        finalized = receipt.get("finalized_slots")
   544	        unused = receipt.get("unused_slots")
   545	        reason = receipt.get("reason")
   546	        return (
   547	            isinstance(finalized, Sequence)
   548	            and not isinstance(finalized, (str, bytes))
   549	            and isinstance(unused, Sequence)
   550	            and not isinstance(unused, (str, bytes))
   551	            and all(slot in BRACKET_SESSION_SLOTS for slot in (*finalized, *unused))
   552	            and len(set((*finalized, *unused))) == len(finalized) + len(unused)
   553	            and set((*finalized, *unused)) == set(BRACKET_SESSION_SLOTS)
   554	            and isinstance(reason, str)
   555	            and bool(reason)
   556	        )
   557	    disposition = receipt.get("disposition")
   558	    artifacts = receipt.get("artifact_sha256")
   559	    epoch = receipt.get("identity_epoch")
   560	    t1 = receipt.get("t1_bindings")
   561	    capture = receipt.get("capture_wall_time_s")
   562	    bound = receipt.get("exact_bound_lexeme_s")
   563	    content_id = receipt.get("content_id")
   564	    if (
   565	        receipt.get("slot") not in BRACKET_SESSION_SLOTS
   566	        or not isinstance(receipt.get("attempt_id"), str)
   567	        or not receipt.get("attempt_id")
   568	        or disposition not in FINAL_DISPOSITIONS
   569	        or not isinstance(receipt.get("custody_locator"), str)
   570	        or not isinstance(artifacts, Mapping)
   571	        or any(
   572	            not isinstance(name, str) or not name or not _is_sha256(digest)
   573	            for name, digest in artifacts.items()
   574	        )
   575	        or not isinstance(epoch, Mapping)
   576	        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
   577	        or not isinstance(t1, Mapping)
   578	        or set(t1) != set(T1_FIELDS)
   579	        or (capture is not None and not isinstance(capture, str))
   580	        or (bound is not None and not isinstance(bound, str))
   581	        or (content_id is not None and not _is_sha256(content_id))
   582	    ):
   583	        return False
   584	    if disposition == "abandoned":
   585	        return content_id == content_id_from_artifact_hashes(artifacts)
   586	    return (
   587	        content_id is not None
   588	        and content_id_from_artifact_hashes(artifacts) == content_id
   589	        and bool(receipt.get("custody_locator"))
   590	        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
   591	        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
   592	        and capture is not None
   593	    )
   594	
   595	
   596	def _valid_receipt_shape(receipt: object) -> bool:
   597	    if not isinstance(receipt, Mapping):
   598	        return False
   599	    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
   600	        return _valid_session_receipt_shape(receipt)
   601	    sequence = receipt.get("sequence")
   602	    event = receipt.get("event")
   603	    expected_keys = (
   604	        _HISTORICAL_IMPORT_RESERVATION_KEYS
   605	        if event == HISTORICAL_IMPORT_RESERVATION_EVENT
   606	        else _RECEIPT_KEYS
   607	    )
   608	    if set(receipt) != expected_keys:
   609	        return False
   610	    disposition = receipt.get("disposition")
   611	    artifacts = receipt.get("artifact_sha256")
   612	    epoch = receipt.get("identity_epoch")
   613	    t1 = receipt.get("t1_bindings")
   614	    capture = receipt.get("capture_wall_time_s")
   615	    bound = receipt.get("exact_bound_lexeme_s")
   616	    if (
   617	        receipt.get("schema_version") != RECEIPT_SCHEMA
   618	        or receipt.get("ledger_schema") != LEDGER_SCHEMA
   619	        or isinstance(sequence, bool)
   620	        or not isinstance(sequence, int)
   621	        or sequence < 1
   622	        or not _is_sha256(receipt.get("predecessor_digest"))
   623	        or event
   624	        not in {
   625	            "reservation",
   626	            "finalization",
   627	            HISTORICAL_IMPORT_RESERVATION_EVENT,
   628	            HISTORICAL_IMPORT_FINALIZATION_EVENT,
   629	        }
   630	        or not isinstance(receipt.get("attempt_id"), str)
   631	        or not receipt.get("attempt_id")
   632	        or disposition not in ALL_DISPOSITIONS
   633	        or not isinstance(receipt.get("custody_locator"), str)
   634	        or not isinstance(artifacts, Mapping)
   635	        or any(
   636	            not isinstance(name, str) or not name or not _is_sha256(digest)
   637	            for name, digest in artifacts.items()
   638	        )
   639	        or not isinstance(epoch, Mapping)
   640	        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
   641	        or not isinstance(t1, Mapping)
   642	        or set(t1) != set(T1_FIELDS)
   643	        or (capture is not None and not isinstance(capture, str))
   644	        or (bound is not None and not isinstance(bound, str))
   645	        or not _is_sha256(receipt.get("receipt_digest"))
   646	        or receipt.get("receipt_digest") != _receipt_digest(receipt)
   647	    ):
   648	        return False
   649	    content_id = receipt.get("content_id")
   650	    if content_id is not None and not _is_sha256(content_id):
   650	    if content_id is not None and not _is_sha256(content_id):
   651	        return False
   652	    if event in {"reservation", HISTORICAL_IMPORT_RESERVATION_EVENT}:
   653	        historical_input_sha256 = receipt.get(
   654	            _HISTORICAL_IMPORT_INPUT_SHA256_KEY
   655	        )
   656	        return (
   657	            disposition == "pending"
   658	            and content_id is None
   659	            and not artifacts
   660	            and capture is None
   661	            and bound is None
   662	            and all(
   663	                epoch.get(field) not in (None, "")
   664	                for field in IDENTITY_EPOCH_FIELDS
   665	            )
   666	            and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
   667	            and (
   668	                event != HISTORICAL_IMPORT_RESERVATION_EVENT
   669	                or isinstance(historical_input_sha256, Mapping)
   670	                and set(historical_input_sha256)
   671	                == _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
   672	                and all(
   673	                    _is_sha256(historical_input_sha256.get(name))
   674	                    for name in _HISTORICAL_IMPORT_INPUT_SHA256_KEYS
   675	                )
   676	            )
   677	        )
   678	    if disposition not in FINAL_DISPOSITIONS:
   679	        return False
   680	    if disposition == "abandoned":
   681	        # R1 retains the terminal writer state as ``abandoned`` while R2
   682	        # classifies it as unresolved.  When canonical primary bytes exist,
   683	        # preserve their authentic content identity; a partial/no-content
   684	        # attempt remains representable with a null content id.
   685	        return content_id == content_id_from_artifact_hashes(artifacts)
   686	    if (
   687	        content_id is None
   688	        or content_id_from_artifact_hashes(artifacts) != content_id
   689	        or not receipt.get("custody_locator")
   690	        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
   691	        or any(t1.get(field) in (None, "") for field in T1_FIELDS)
   692	        or capture is None
   693	    ):
   694	        return False
   695	    return True
   696	
   697	
   698	def _head_pin(value: object) -> tuple[int, str] | None:
   699	    if not isinstance(value, Mapping) or set(value) != {
   700	        "sequence",
   701	        "head_digest",
   702	        "ledger_schema",
   703	    }:
   704	        return None
   705	    sequence = value.get("sequence")
   706	    digest = value.get("head_digest")
   707	    if (
   708	        value.get("ledger_schema") != LEDGER_SCHEMA
   709	        or isinstance(sequence, bool)
   710	        or not isinstance(sequence, int)
   711	        or sequence < 0
   712	        or not _is_sha256(digest)
   713	        or (sequence == 0 and digest != GENESIS_DIGEST)
   714	    ):
   715	        return None
   716	    return sequence, str(digest)
   717	
   718	
   719	def _committed_pin_bytes(path: Path, repo_root: Path) -> bytes | None:
   720	    try:
   721	        relative = Path(path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
   722	    except (OSError, ValueError):
   723	        return None
   724	    try:
   725	        completed = subprocess.run(
   726	            ["git", "show", f"HEAD:{relative}"],
   727	            cwd=repo_root,
   728	            check=True,
   729	            stdout=subprocess.PIPE,
   730	            stderr=subprocess.DEVNULL,
   731	        )
   732	    except (OSError, subprocess.CalledProcessError):
   733	        return None
   734	    return completed.stdout
   735	
   736	
   737	def _parse_ledger(raw: bytes) -> tuple[list[Mapping[str, Any]], set[str]]:
   738	    receipts: list[Mapping[str, Any]] = []
   739	    reasons: set[str] = set()
   740	    if not raw:
   741	        return receipts, reasons
   742	    try:
   743	        text = raw.decode("utf-8")
   744	    except UnicodeDecodeError:
   745	        return receipts, {"calibration_ledger_malformed"}
   746	    if not text.endswith("\n"):
   747	        reasons.add("calibration_ledger_malformed")
   748	    predecessor = GENESIS_DIGEST
   749	    expected_sequence = 1
   750	    seen_digests: set[str] = set()
   751	    for line in text.splitlines():
   752	        if not line.strip():
   753	            reasons.add("calibration_ledger_malformed")
   754	            continue
   755	        try:
   756	            value = json.loads(line)
   757	        except json.JSONDecodeError:
   758	            reasons.add("calibration_ledger_malformed")
   759	            continue
   760	        if not _valid_receipt_shape(value):
   761	            reasons.add("calibration_ledger_malformed")
   762	            continue
   763	        if (
   764	            value["sequence"] != expected_sequence
   765	            or value["predecessor_digest"] != predecessor
   766	            or value["receipt_digest"] in seen_digests
   767	        ):
   768	            reasons.add("calibration_ledger_chain_conflict")
   769	        expected_sequence += 1
   770	        predecessor = value["receipt_digest"]
   771	        seen_digests.add(predecessor)
   772	        receipts.append(value)
   773	    return receipts, reasons
   774	
   775	
   776	def _observation_from_receipt(
   777	    receipt: Mapping[str, Any],
   778	    *,
   779	    observation_kind: str,
   780	    session: Mapping[str, Any] | None = None,
   781	) -> LedgerObservation:
   782	    content_id = receipt.get("content_id")
   783	    return LedgerObservation(
   784	        sequence=int(receipt["sequence"]),
   785	        receipt_digest=str(receipt["receipt_digest"]),
   786	        attempt_id=str(receipt["attempt_id"]),
   787	        content_id=str(content_id) if isinstance(content_id, str) else None,
   788	        artifact_sha256=MappingProxyType(dict(receipt["artifact_sha256"])),
   789	        identity_epoch=MappingProxyType(dict(receipt["identity_epoch"])),
   790	        t1_bindings=MappingProxyType(dict(receipt["t1_bindings"])),
   791	        capture_wall_time_s=receipt.get("capture_wall_time_s"),
   792	        exact_bound_lexeme_s=receipt.get("exact_bound_lexeme_s"),
   793	        disposition=str(receipt["disposition"]),
   794	        custody_locator=str(receipt["custody_locator"]),
   795	        observation_kind=observation_kind,
   796	        bracket_session_id=(str(session["session_id"]) if session else None),
   797	        bracket_slot=(str(receipt["slot"]) if session else None),
   798	        bracket_window_id=(str(session["window_id"]) if session else None),
   799	        bracket_plan_id=(str(session["plan_id"]) if session else None),
   800	        bracket_plan_sha256=(str(session["plan_sha256"]) if session else None),
   801	        bracket_evidence_root_id=(
   802	            str(session["evidence_root_id"]) if session else None
   803	        ),
   804	    )
   805	
   806	
   807	def _session_identity_matches(
   808	    receipt: Mapping[str, Any], open_receipt: Mapping[str, Any]
   809	) -> bool:
   810	    return all(receipt.get(field) == open_receipt.get(field) for field in _SESSION_IDENTITY_KEYS)
   811	
   812	
   813	def _bracket_sessions_and_observations(
   814	    receipts: Sequence[Mapping[str, Any]],
   815	) -> tuple[list[CalibrationBracketSession], list[LedgerObservation], set[str]]:
   816	    states: dict[str, dict[str, Any]] = {}
   817	    claimed_attempts: set[str] = set()
   818	    reasons: set[str] = set()
   819	    for receipt in receipts:
   820	        if receipt.get("schema_version") != BRACKET_SESSION_SCHEMA:
   821	            continue
   822	        event = receipt["event"]
   823	        session_id = str(receipt["session_id"])
   824	        if event == BRACKET_SESSION_OPEN_EVENT:
   825	            slots = receipt["slots"]
   826	            attempt_ids = {str(slots[role]["attempt_id"]) for role in BRACKET_SESSION_SLOTS}
   827	            if session_id in states or attempt_ids & claimed_attempts:
   828	                reasons.add("calibration_ledger_bracket_session_conflict")
   829	                continue
   830	            claimed_attempts.update(attempt_ids)
   831	            states[session_id] = {
   832	                "open": receipt,
   833	                "finals": {},
   834	                "abort": None,
   835	            }
   836	            continue
   837	        state = states.get(session_id)
   838	        if state is None:
   839	            reasons.add("calibration_ledger_bracket_session_conflict")
   840	            continue
   841	        open_receipt = state["open"]
   842	        if not _session_identity_matches(receipt, open_receipt):
   843	            reasons.add("calibration_ledger_bracket_session_conflict")
   844	            continue
   845	        finals = state["finals"]
   846	        if event == BRACKET_SESSION_FINALIZATION_EVENT:
   847	            slot = str(receipt["slot"])
   848	            expected_slot = BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
   849	            reserved = open_receipt["slots"].get(slot)
   850	            if (
   851	                state["abort"] is not None
   852	                or slot != expected_slot
   853	                or slot in finals
   854	                or not isinstance(reserved, Mapping)
   855	                or receipt["attempt_id"] != reserved["attempt_id"]
   856	                or receipt["custody_locator"] != reserved["custody_locator"]
   857	                or dict(receipt["identity_epoch"]) != dict(reserved["identity_epoch"])
   858	                or dict(receipt["t1_bindings"]) != dict(reserved["t1_bindings"])
   859	            ):
   860	                reasons.add("calibration_ledger_bracket_session_conflict")
   861	                continue
   862	            finals[slot] = receipt
   863	            continue
   864	        finalized_slots = list(finals)
   865	        unused_slots = [slot for slot in BRACKET_SESSION_SLOTS if slot not in finals]
   866	        if (
   867	            event != BRACKET_SESSION_ABORT_EVENT
   868	            or state["abort"] is not None
   869	            or len(finals) == 2
   870	            or receipt["finalized_slots"] != finalized_slots
   871	            or receipt["unused_slots"] != unused_slots
   872	        ):
   873	            reasons.add("calibration_ledger_bracket_session_conflict")
   874	            continue
   875	        state["abort"] = receipt
   876	
   877	    sessions: list[CalibrationBracketSession] = []
   878	    completed_observations: list[LedgerObservation] = []
   879	    for session_id, state in sorted(
   880	        states.items(), key=lambda item: int(item[1]["open"]["sequence"])
   881	    ):
   882	        open_receipt = state["open"]
   883	        finals = state["finals"]
   884	        abort = state["abort"]
   885	        if abort is not None:
   886	            session_state = "aborted"
   887	        elif len(finals) == 2:
   888	            session_state = "finalized"
   889	        else:
   890	            session_state = "open"
   891	            reasons.add("calibration_ledger_bracket_session_open")
   892	        finalized_observations = {
   893	            slot: _observation_from_receipt(
   894	                receipt,
   895	                observation_kind=(
   896	                    "bracket-session-finalized"
   897	                    if session_state == "finalized"
   898	                    else "bracket-session-aborted"
   899	                ),
   900	                session=open_receipt,
   901	            )
   902	            for slot, receipt in finals.items()
   903	        }
   904	        if session_state != "aborted":
   905	            completed_observations.extend(
   906	                finalized_observations[slot]
   907	                for slot in BRACKET_SESSION_SLOTS
   908	                if slot in finalized_observations
   909	            )
   910	        sessions.append(
   911	            CalibrationBracketSession(
   912	                session_id=session_id,
   913	                window_id=str(open_receipt["window_id"]),
   914	                plan_id=str(open_receipt["plan_id"]),
   915	                plan_sha256=str(open_receipt["plan_sha256"]),
   916	                evidence_root_id=str(open_receipt["evidence_root_id"]),
   917	                capability_receipt_digest=str(open_receipt["receipt_digest"]),
   918	                capability_sequence=int(open_receipt["sequence"]),
   919	                slot_attempt_ids=MappingProxyType(
   920	                    {
   921	                        slot: str(open_receipt["slots"][slot]["attempt_id"])
   922	                        for slot in BRACKET_SESSION_SLOTS
   923	                    }
   924	                ),
   925	                state=session_state,
   926	                finalized_slots=MappingProxyType(finalized_observations),
   927	                abort_receipt_digest=(
   928	                    str(abort["receipt_digest"]) if abort is not None else None
   929	                ),
   930	                abort_reason=(str(abort["reason"]) if abort is not None else None),
   931	            )
   932	        )
   933	    return sessions, completed_observations, reasons
   934	
   935	
   936	def _attempts_and_observations(
   937	    receipts: Sequence[Mapping[str, Any]],
   938	) -> tuple[list[LedgerObservation], list[CalibrationBracketSession], set[str]]:
   939	    pending: dict[str, Mapping[str, Any]] = {}
   940	    finalized: dict[str, Mapping[str, Any]] = {}
   941	    reasons: set[str] = set()
   942	    for receipt in receipts:
   943	        if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
   944	            continue
   945	        attempt_id = str(receipt["attempt_id"])
   946	        if receipt["event"] in {
   947	            "reservation",
   948	            HISTORICAL_IMPORT_RESERVATION_EVENT,
   949	        }:
   950	            if attempt_id in pending or attempt_id in finalized:
   951	                reasons.add("calibration_ledger_attempt_conflict")
   952	            else:
   953	                pending[attempt_id] = receipt
   954	            continue
   955	        reservation = pending.get(attempt_id)
   956	        expected_final_event = (
   957	            HISTORICAL_IMPORT_FINALIZATION_EVENT
   958	            if reservation is not None
   959	            and reservation["event"] == HISTORICAL_IMPORT_RESERVATION_EVENT
   960	            else "finalization"
   961	        )
   962	        if (
   963	            reservation is None
   964	            or attempt_id in finalized
   965	            or receipt["event"] != expected_final_event
   966	        ):
   967	            reasons.add("calibration_ledger_attempt_conflict")
   968	        else:
   969	            finalized[attempt_id] = receipt
   970	    if set(pending) - set(finalized):
   971	        reasons.add("calibration_ledger_pending")
   972	
   973	    observations: list[LedgerObservation] = []
   974	    content_classification: dict[str, tuple[str, tuple[tuple[str, Any], ...]]] = {}
   975	    for attempt_id, receipt in sorted(
   976	        finalized.items(), key=lambda item: int(item[1]["sequence"])
   977	    ):
   978	        content_id = receipt.get("content_id")
   979	        epoch = dict(receipt["identity_epoch"])
   980	        if isinstance(content_id, str):
   981	            classification = (
   982	                (
   983	                    "unresolved"
   984	                    if receipt["disposition"] == "abandoned"
   985	                    else str(receipt["disposition"])
   986	                ),
   987	                tuple((field, epoch.get(field)) for field in IDENTITY_EPOCH_FIELDS),
   988	            )
   989	            previous = content_classification.get(content_id)
   990	            if previous is not None and previous != classification:
   991	                reasons.add("calibration_ledger_content_conflict")
   992	            content_classification[content_id] = classification
   993	        observations.append(
   994	            _observation_from_receipt(
   995	                receipt,
   996	                observation_kind=(
   997	                    "historical-import"
   998	                    if receipt["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
   999	                    else "live-capture"
  1000	                ),
  1001	            )
  1002	        )
  1003	    sessions, session_observations, session_reasons = (
  1004	        _bracket_sessions_and_observations(receipts)
  1005	    )
  1006	    reasons.update(session_reasons)
  1007	    session_attempt_ids = {
  1008	        attempt_id
  1009	        for session in sessions
  1010	        for attempt_id in session.slot_attempt_ids.values()
  1011	    }
  1012	    if set(pending) & session_attempt_ids:
  1013	        reasons.add("calibration_ledger_bracket_session_conflict")
  1014	    observations.extend(session_observations)
  1015	    content_classification.clear()
  1016	    classification_observations = list(observations)
  1017	    visible_attempts = {observation.attempt_id for observation in observations}
  1018	    classification_observations.extend(
  1019	        observation
  1020	        for session in sessions
  1021	        for observation in session.finalized_slots.values()
  1022	        if observation.attempt_id not in visible_attempts
  1023	    )
  1024	    for observation in classification_observations:
  1025	        if observation.content_id is None:
  1025	        if observation.content_id is None:
  1026	            continue
  1027	        classification = (
  1028	            observation.classification_disposition,
  1029	            tuple(
  1030	                (field, observation.identity_epoch.get(field))
  1031	                for field in IDENTITY_EPOCH_FIELDS
  1032	            ),
  1033	        )
  1034	        previous = content_classification.get(observation.content_id)
  1035	        if previous is not None and previous != classification:
  1036	            reasons.add("calibration_ledger_content_conflict")
  1037	        content_classification[observation.content_id] = classification
  1038	    observations.sort(key=lambda observation: observation.sequence)
  1039	    return observations, sessions, reasons
  1040	
  1041	
  1042	def _custody_reasons(
  1043	    observations: Sequence[LedgerObservation], repo_root: Path
  1044	) -> set[str]:
  1045	    for observation in observations:
  1046	        if not observation.artifact_sha256:
  1047	            if observation.disposition == "abandoned":
  1048	                continue
  1049	            return {"calibration_ledger_custody_invalid"}
  1050	        root = Path(observation.custody_locator)
  1051	        if not root.is_absolute():
  1052	            root = Path(repo_root) / root
  1053	        for relative, expected in observation.artifact_sha256.items():
  1054	            path = root / relative
  1055	            try:
  1056	                actual = hashlib.sha256(path.read_bytes()).hexdigest()
  1057	            except OSError:
  1058	                return {"calibration_ledger_custody_invalid"}
  1059	            if actual != expected:
  1060	                return {"calibration_ledger_custody_invalid"}
  1061	    return set()
  1062	
  1063	
  1064	def load_calibration_ledger_snapshot(
  1065	    ledger_path: Path = DEFAULT_LEDGER_PATH,
  1066	    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
  1067	    *,
  1068	    baseline_sequence: int | None = None,
  1069	    baseline_digest: str | None = None,
  1070	    require_committed_pin: bool = True,
  1071	    verify_custody: bool = True,
  1072	    repo_root: Path = REPO_ROOT,
  1073	) -> CalibrationLedgerSnapshot:
  1074	    """Load, authenticate, and freeze exactly one ledger snapshot.
  1075	
  1076	    A proper physical prefix of the pin is classified explicitly as rollback;
  1077	    any other physical/pinned disagreement is a stale-head mismatch.  The
  1078	    baseline must occur at its exact sequence in the same complete chain.
  1079	    This closes workflow omission, unregistered evidence, and rollback or
  1080	    stale-head consumption; it does not defend against a malicious trusted
  1081	    writer or a rewrite of both Git and the full ledger history.
  1082	    """
  1083	
  1084	    ledger_path = Path(ledger_path)
  1085	    head_pin_path = Path(head_pin_path)
  1086	    reasons: set[str] = set()
  1087	    try:
  1088	        pin_raw = head_pin_path.read_bytes()
  1089	        pin_value = json.loads(pin_raw)
  1090	    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
  1091	        pin_raw = b""
  1092	        pin_value = None
  1093	    pin = _head_pin(pin_value)
  1094	    if pin is None:
  1095	        reasons.add("calibration_ledger_malformed")
  1096	        pinned_sequence, pinned_digest = 0, GENESIS_DIGEST
  1097	    else:
  1098	        pinned_sequence, pinned_digest = pin
  1099	    try:
  1100	        raw = ledger_path.read_bytes()
  1101	    except OSError:
  1102	        raw = b""
  1103	        if pinned_sequence > 0:
  1104	            reasons.add("calibration_ledger_missing")
  1105	    genesis_development_bootstrap = (
  1106	        pinned_sequence == 0
  1107	        and pinned_digest == GENESIS_DIGEST
  1108	        and not raw
  1109	        and not ledger_path.exists()
  1110	    )
  1111	    if (
  1112	        require_committed_pin
  1113	        # The checked-in fixture starts at genesis.  Before its first commit,
  1114	        # an absent physical ledger cannot license a claim (there are no
  1115	        # endpoints); permitting this development-only empty view avoids a
  1116	        # circular "commit before tests" bootstrap. Any physical byte or any
  1117	        # non-genesis pin remains strictly commit-authenticated.
  1118	        and not genesis_development_bootstrap
  1119	        and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
  1120	    ):
  1121	        reasons.add("calibration_ledger_head_uncommitted")
  1122	    receipts, parse_reasons = _parse_ledger(raw)
  1123	    reasons.update(parse_reasons)
  1124	    physical_sequence = len(receipts)
  1125	    physical_digest = (
  1126	        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
  1127	    )
  1128	    if (physical_sequence, physical_digest) != (pinned_sequence, pinned_digest):
  1129	        if physical_sequence < pinned_sequence:
  1130	            reasons.add("calibration_ledger_rollback")
  1131	        else:
  1132	            reasons.add("calibration_ledger_head_mismatch")
  1133	    if baseline_sequence is not None or baseline_digest is not None:
  1134	        if (
  1135	            isinstance(baseline_sequence, bool)
  1136	            or not isinstance(baseline_sequence, int)
  1137	            or baseline_sequence < 0
  1138	            or not _is_sha256(baseline_digest)
  1139	        ):
  1140	            reasons.add("calibration_ledger_baseline_missing")
  1141	        else:
  1142	            in_chain = (
  1143	                baseline_digest == GENESIS_DIGEST
  1144	                if baseline_sequence == 0
  1145	                else baseline_sequence <= len(receipts)
  1146	                and receipts[baseline_sequence - 1]["receipt_digest"]
  1147	                == baseline_digest
  1148	            )
  1149	            if not in_chain or baseline_sequence > pinned_sequence:
  1150	                reasons.add("calibration_ledger_baseline_missing")
  1151	    observations, bracket_sessions, state_reasons = _attempts_and_observations(
  1152	        receipts
  1153	    )
  1154	    reasons.update(state_reasons)
  1155	    if verify_custody:
  1156	        custody_observations = list(observations)
  1157	        custody_attempt_ids = {observation.attempt_id for observation in observations}
  1158	        for session in bracket_sessions:
  1159	            custody_observations.extend(
  1160	                observation
  1161	                for observation in session.finalized_slots.values()
  1162	                if observation.attempt_id not in custody_attempt_ids
  1163	            )
  1164	        reasons.update(_custody_reasons(custody_observations, repo_root))
  1165	    return CalibrationLedgerSnapshot(
  1166	        ledger_schema=LEDGER_SCHEMA,
  1167	        ledger_path=ledger_path,
  1168	        head_sequence=physical_sequence,
  1169	        head_digest=physical_digest,
  1170	        receipts=tuple(_frozen_mapping(receipt) for receipt in receipts),
  1171	        observations=tuple(observations),
  1172	        refusal_reasons=tuple(sorted(reasons)),
  1173	        bracket_sessions=tuple(bracket_sessions),
  1174	        baseline_sequence=baseline_sequence,
  1175	        baseline_digest=baseline_digest,
  1176	        committed_head_sequence=pinned_sequence,
  1177	        committed_head_digest=pinned_digest,
  1178	    )
  1179	
  1180	
  1181	def _new_receipt(
  1182	    *,
  1183	    sequence: int,
  1184	    predecessor_digest: str,
  1185	    event: str,
  1186	    attempt_id: str,
  1187	    content_id: str | None,
  1188	    artifacts: Mapping[str, str],
  1189	    identity_epoch: Mapping[str, Any] | None,
  1190	    t1_bindings: Mapping[str, Any] | None,
  2040	                    os.fsync(staging.fileno())
  2041	                os.replace(staging_path, ledger)
  2042	                staging_path = None
  2043	            except Exception as exc:
  2044	                raise CalibrationLedgerError(
  2045	                    "historical import append failed atomically"
  2046	                ) from exc
  2047	            try:
  2048	                _fsync_parent_directory(ledger.parent)
  2049	            except OSError as exc:
  2050	                raise HistoricalImportDurabilityUncertain(plan) from exc
  2051	        finally:
  2052	            if staging_descriptor >= 0:
  2053	                os.close(staging_descriptor)
  2054	            if staging_path is not None:
  2055	                try:
  2056	                    staging_path.unlink()
  2057	                except FileNotFoundError:
  2058	                    pass
  2059	    finally:
  2060	        try:
  2061	            os.close(lock_descriptor)
  2062	        except OSError:
  2063	            pass
  2064	    return plan
  2065	
  2066	
  2067	def _locked_append(
  2068	    ledger_path: Path,
  2069	    build: Any,
  2070	) -> Mapping[str, Any]:
  2071	    ledger_path = Path(ledger_path)
  2072	    ledger_path.parent.mkdir(parents=True, exist_ok=True)
  2073	    lock_descriptor = _open_ledger_lock(ledger_path)
  2074	    try:
  2075	        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
  2076	        descriptor = os.open(
  2077	            ledger_path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600
  2078	        )
  2079	        try:
  2080	            with os.fdopen(descriptor, "r+b", closefd=False) as handle:
  2081	                handle.seek(0)
  2082	                raw = handle.read()
  2083	                receipts, reasons = _parse_ledger(raw)
  2084	                if reasons:
  2085	                    raise CalibrationLedgerError(", ".join(sorted(reasons)))
  2086	                receipt = build(receipts)
  2087	                if not _valid_receipt_shape(receipt):
  2088	                    raise CalibrationLedgerError(
  2089	                        "writer constructed a malformed receipt"
  2090	                    )
  2091	                payload = canonical_json_bytes(receipt) + b"\n"
  2092	                handle.seek(0, os.SEEK_END)
  2093	                handle.write(payload)
  2094	                handle.flush()
  2095	                os.fsync(handle.fileno())
  2096	                return _frozen_mapping(receipt)
  2097	        finally:
  2098	            os.close(descriptor)
  2099	    finally:
  2100	        os.close(lock_descriptor)
  2101	
  2102	
  2103	def _authenticated_head_pin(
  2104	    head_pin_path: Path,
  2105	    *,
  2106	    require_committed_pin: bool,
  2107	    repo_root: Path,
  2108	) -> tuple[int, str]:
  2109	    pin_path = Path(head_pin_path)
  2110	    try:
  2111	        pin_raw = pin_path.read_bytes()
  2112	        pin_value = json.loads(pin_raw)
  2113	    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
  2114	        raise CalibrationLedgerError("head pin is unreadable") from exc
  2115	    pin = _head_pin(pin_value)
  2116	    if pin is None:
  2117	        raise CalibrationLedgerError("head pin is malformed")
  2118	    if require_committed_pin and _committed_pin_bytes(pin_path, repo_root) != pin_raw:
  2119	        raise CalibrationLedgerError("head pin is not committed at Git HEAD")
  2120	    return pin
  2121	
  2122	
  2123	def append_bracket_session_receipt(
  2124	    ledger_path: Path,
  2125	    *,
  2126	    session_id: str,
  2127	    window_id: str,
  2128	    plan_id: str,
  2129	    plan_sha256: str,
  2130	    evidence_root_id: str,
  2131	    slots: Mapping[str, Mapping[str, Any]],
  2132	    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
  2133	    require_committed_pin: bool = True,
  2134	    repo_root: Path = REPO_ROOT,
  2135	) -> Mapping[str, Any]:
  2136	    """Atomically reserve exactly one immutable pre/post bracket capability.
  2137	
  2138	    Physical-head equality with the committed pin is checked here, at open,
  2139	    and deliberately not checked again while either already-reserved slot is
  2140	    finalized. Claim evaluation remains impossible until the terminal head
  2141	    pin is emitted, reviewed, and committed.
  2142	    """
  2143	
  2144	    session_identity = {
  2145	        "session_id": session_id,
  2146	        "window_id": window_id,
  2147	        "plan_id": plan_id,
  2148	        "plan_sha256": plan_sha256,
  2149	        "evidence_root_id": evidence_root_id,
  2150	    }
  2151	    normalized_slots: dict[str, dict[str, Any]] = {}
  2152	    if not isinstance(slots, Mapping) or set(slots) != set(BRACKET_SESSION_SLOTS):
  2153	        raise CalibrationLedgerError("bracket session must reserve exactly pre and post")
  2154	    for role in BRACKET_SESSION_SLOTS:
  2155	        source = slots.get(role)
  2156	        if not isinstance(source, Mapping):
  2157	            raise CalibrationLedgerError(f"{role} slot is malformed")
  2158	        normalized_slots[role] = {
  2159	            "attempt_id": source.get("attempt_id"),
  2160	            "custody_locator": source.get("custody_locator"),
  2161	            "identity_epoch": _normalized_vector(
  2162	                source.get("identity_epoch"), IDENTITY_EPOCH_FIELDS
  2163	            ),
  2164	            "t1_bindings": _normalized_vector(source.get("t1_bindings"), T1_FIELDS),
  2165	            "expected_time_role": role,
  2166	        }
  2167	    if not _valid_session_identity(session_identity) or any(
  2168	        not _valid_session_slot_reservation(normalized_slots[role], role)
  2169	        for role in BRACKET_SESSION_SLOTS
  2170	    ):
  2171	        raise CalibrationLedgerError("bracket session reservation is malformed")
  2172	    if (
  2173	        normalized_slots["pre"]["attempt_id"]
  2174	        == normalized_slots["post"]["attempt_id"]
  2175	    ):
  2176	        raise CalibrationLedgerError("bracket session slot attempts must be distinct")
  2177	    pin = _authenticated_head_pin(
  2178	        Path(head_pin_path),
  2179	        require_committed_pin=require_committed_pin,
  2180	        repo_root=Path(repo_root),
  2181	    )
  2182	
  2183	    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
  2184	        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
  2185	        if (len(receipts), predecessor) != pin:
  2186	            raise CalibrationLedgerError(
  2187	                "physical ledger head differs from the committed pin"
  2188	            )
  2189	        observations, sessions, reasons = _attempts_and_observations(receipts)
  2190	        del observations
  2191	        if reasons:
  2192	            raise CalibrationLedgerError(", ".join(sorted(reasons)))
  2193	        reserved_attempts = {
  2194	            attempt_id
  2195	            for session in sessions
  2196	            for attempt_id in session.slot_attempt_ids.values()
  2197	        }
  2198	        ordinary_attempts = {
  2199	            str(receipt["attempt_id"])
  2200	            for receipt in receipts
  2201	            if receipt.get("schema_version") == RECEIPT_SCHEMA
  2202	        }
  2203	        proposed_attempts = {
  2204	            normalized_slots[role]["attempt_id"] for role in BRACKET_SESSION_SLOTS
  2205	        }
  2206	        if (
  2207	            any(session.session_id == session_id for session in sessions)
  2208	            or proposed_attempts & (reserved_attempts | ordinary_attempts)
  2209	        ):
  2210	            raise CalibrationLedgerError("bracket session identity conflicts with ledger")
  2211	        return _new_bracket_session_record(
  2212	            sequence=len(receipts) + 1,
  2213	            predecessor_digest=str(predecessor),
  2214	            event=BRACKET_SESSION_OPEN_EVENT,
  2215	            session_identity=session_identity,
  2216	            fields={"slots": normalized_slots},
  2217	        )
  2218	
  2219	    return _locked_append(Path(ledger_path), build)
  2220	
  2221	
  2222	def finalize_bracket_session_slot(
  2223	    ledger_path: Path,
  2224	    *,
  2225	    session_id: str,
  2226	    slot: str,
  2227	    disposition: str,
  2228	    custody_locator: str,
  2229	    artifact_sha256: Mapping[str, str] | None = None,
  2230	    identity_epoch: Mapping[str, Any] | None = None,
  2231	    t1_bindings: Mapping[str, Any] | None = None,
  2232	    capture_wall_time_s: str | None = None,
  2233	    exact_bound_lexeme_s: str | None = None,
  2234	) -> Mapping[str, Any]:
  2235	    """Fill exactly one reserved session slot in mandatory pre/post order."""
  2236	
  2237	    if slot not in BRACKET_SESSION_SLOTS:
  2238	        raise CalibrationLedgerError(f"invalid bracket session slot: {slot!r}")
  2239	    if disposition not in FINAL_DISPOSITIONS:
  2240	        raise CalibrationLedgerError(f"invalid final disposition: {disposition!r}")
  2241	    artifacts = dict(artifact_sha256 or {})
  2242	    content_id = content_id_from_artifact_hashes(artifacts)
  2243	    normalized_epoch = _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS)
  2244	    normalized_t1 = _normalized_vector(t1_bindings, T1_FIELDS)
  2245	
  2246	    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
  2247	        observations, sessions, reasons = _attempts_and_observations(receipts)
  2248	        del observations
  2249	        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
  2250	        if non_open_reasons:
  2251	            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
  2252	        by_id = {session.session_id: session for session in sessions}
  2253	        session = by_id.get(session_id)
  2254	        if session is None or session.state != "open":
  2255	            raise CalibrationLedgerError("bracket session is not open")
  2256	        expected_slot = BRACKET_SESSION_SLOTS[len(session.finalized_slots)]
  2257	        if slot != expected_slot or slot in session.finalized_slots:
  2258	            raise CalibrationLedgerError(
  2259	                f"bracket session slot must finalize in order: expected {expected_slot}"
  2260	            )
  2261	        open_receipt = next(
  2262	            receipt
  2263	            for receipt in receipts
  2264	            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
  2265	            and receipt.get("session_id") == session_id
  2266	        )
  2267	        reserved = open_receipt["slots"][slot]
  2268	        if (
  2269	            reserved["custody_locator"] != custody_locator
  2270	            or dict(reserved["identity_epoch"]) != normalized_epoch
  2271	            or dict(reserved["t1_bindings"]) != normalized_t1
  2272	        ):
  2273	            raise CalibrationLedgerError(
  2274	                "slot finalization conflicts with the reserved session binding"
  2275	            )
  2276	        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
  2277	        return _new_bracket_session_record(
  2278	            sequence=len(receipts) + 1,
  2279	            predecessor_digest=str(predecessor),
  2280	            event=BRACKET_SESSION_FINALIZATION_EVENT,
  2281	            session_identity={
  2282	                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
  2283	            },
  2284	            fields={
  2285	                "slot": slot,
  2286	                "attempt_id": reserved["attempt_id"],
  2287	                "content_id": content_id,
  2288	                "artifact_sha256": dict(sorted(artifacts.items())),
  2289	                "identity_epoch": normalized_epoch,
  2290	                "t1_bindings": normalized_t1,
  2291	                "capture_wall_time_s": capture_wall_time_s,
  2292	                "exact_bound_lexeme_s": exact_bound_lexeme_s,
  2293	                "disposition": disposition,
  2294	                "custody_locator": custody_locator,
  2295	            },
  2296	        )
  2297	
  2298	    return _locked_append(Path(ledger_path), build)
  2299	
  2300	
  2301	def abort_bracket_session(
  2302	    ledger_path: Path,
  2303	    *,
  2304	    session_id: str,
  2305	    reason: str,
  2306	) -> Mapping[str, Any]:
  2307	    """Append a governed terminal closure without deleting partial receipts."""
  2308	
  2309	    if not isinstance(reason, str) or not reason:
  2310	        raise CalibrationLedgerError("bracket session abort reason must be nonempty")
  2311	
  2312	    def build(receipts: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
  2313	        observations, sessions, reasons = _attempts_and_observations(receipts)
  2314	        del observations
  2315	        non_open_reasons = reasons - {"calibration_ledger_bracket_session_open"}
  2316	        if non_open_reasons:
  2317	            raise CalibrationLedgerError(", ".join(sorted(non_open_reasons)))
  2318	        session = next(
  2319	            (item for item in sessions if item.session_id == session_id), None
  2320	        )
  2321	        if session is None or session.state != "open":
  2322	            raise CalibrationLedgerError("bracket session is not open")
  2323	        open_receipt = next(
  2324	            receipt
  2325	            for receipt in receipts
  2326	            if receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
  2327	            and receipt.get("session_id") == session_id
  2328	        )
  2329	        predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
  2330	        finalized_slots = list(session.finalized_slots)
  2331	        return _new_bracket_session_record(
  2332	            sequence=len(receipts) + 1,
  2333	            predecessor_digest=str(predecessor),
  2334	            event=BRACKET_SESSION_ABORT_EVENT,
  2335	            session_identity={
  2336	                field: open_receipt[field] for field in _SESSION_IDENTITY_KEYS
  2337	            },
  2338	            fields={
  2339	                "finalized_slots": finalized_slots,
  2340	                "unused_slots": [
  2341	                    role for role in BRACKET_SESSION_SLOTS if role not in finalized_slots
  2342	                ],
  2343	                "reason": reason,
  2344	            },
  2345	        )
  2346	
  2347	    return _locked_append(Path(ledger_path), build)
  2348	
  2349	
  2350	def terminal_head_pin_for_session(
  2351	    ledger_path: Path,
  2352	    *,
  2353	    session_id: str,
  2354	) -> dict[str, Any]:
  2355	    """Return the sole terminal pin candidate after post or governed abort."""
  2356	
  2357	    try:
  2358	        raw = Path(ledger_path).read_bytes()
  2359	    except OSError as exc:
  2360	        raise CalibrationLedgerError("ledger is unreadable") from exc
  2361	    receipts, parse_reasons = _parse_ledger(raw)
  2362	    observations, sessions, state_reasons = _attempts_and_observations(receipts)
  2363	    del observations
  2364	    reasons = parse_reasons | state_reasons
  2365	    if reasons:
  2366	        raise CalibrationLedgerError(", ".join(sorted(reasons)))
  2367	    session = next((item for item in sessions if item.session_id == session_id), None)
  2368	    if session is None or session.state == "open":
  2369	        raise CalibrationLedgerError("bracket session is not terminal")
  2370	    terminal_digest = (
  2371	        session.finalized_slots["post"].receipt_digest
  2372	        if session.state == "finalized"
  2373	        else session.abort_receipt_digest
  2374	    )
  2375	    final = receipts[-1] if receipts else None
  2376	    if final is None or final["receipt_digest"] != terminal_digest:
  2377	        raise CalibrationLedgerError("session closure is not the terminal ledger head")
  2378	    return head_pin_for_receipt(final)
  2379	
  2380	
  2381	def append_pending_receipt(
  2382	    ledger_path: Path,
  2383	    *,
  2384	    attempt_id: str,
  2385	    custody_locator: str,
  2386	    identity_epoch: Mapping[str, Any] | None = None,
  2387	    t1_bindings: Mapping[str, Any] | None = None,
  2388	    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
  2389	    require_committed_pin: bool = True,
  2390	    repo_root: Path = REPO_ROOT,
  2391	) -> Mapping[str, Any]:
  2392	    """Reserve an attempt before any capture directory or sampler exists.
  2393	
  2394	    This closes workflow omission, unregistered evidence, and rollback or
  2395	    stale-head consumption; it does not defend against a malicious trusted
  2396	    writer or a rewrite of both Git and the full ledger history.
  2397	    """
  2398	
  2399	    if not isinstance(attempt_id, str) or not attempt_id:
  2400	        raise CalibrationLedgerError("attempt_id must be nonempty")
  2401	    pin_path = Path(head_pin_path)
  2402	    try:
  2403	        pin_raw = pin_path.read_bytes()
  2404	        pin_value = json.loads(pin_raw)
  2405	    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:

exec
/bin/zsh -lc "nl -ba joulewise/calibration_ledger.py | sed -n '807,1025p'; nl -ba joulewise/calibration_ledger.py | sed -n '1040,1180p'; nl -ba joulewise/calibration_ledger.py | sed -n '1180,1245p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
   807	def _session_identity_matches(
   808	    receipt: Mapping[str, Any], open_receipt: Mapping[str, Any]
   809	) -> bool:
   810	    return all(receipt.get(field) == open_receipt.get(field) for field in _SESSION_IDENTITY_KEYS)
   811	
   812	
   813	def _bracket_sessions_and_observations(
   814	    receipts: Sequence[Mapping[str, Any]],
   815	) -> tuple[list[CalibrationBracketSession], list[LedgerObservation], set[str]]:
   816	    states: dict[str, dict[str, Any]] = {}
   817	    claimed_attempts: set[str] = set()
   818	    reasons: set[str] = set()
   819	    for receipt in receipts:
   820	        if receipt.get("schema_version") != BRACKET_SESSION_SCHEMA:
   821	            continue
   822	        event = receipt["event"]
   823	        session_id = str(receipt["session_id"])
   824	        if event == BRACKET_SESSION_OPEN_EVENT:
   825	            slots = receipt["slots"]
   826	            attempt_ids = {str(slots[role]["attempt_id"]) for role in BRACKET_SESSION_SLOTS}
   827	            if session_id in states or attempt_ids & claimed_attempts:
   828	                reasons.add("calibration_ledger_bracket_session_conflict")
   829	                continue
   830	            claimed_attempts.update(attempt_ids)
   831	            states[session_id] = {
   832	                "open": receipt,
   833	                "finals": {},
   834	                "abort": None,
   835	            }
   836	            continue
   837	        state = states.get(session_id)
   838	        if state is None:
   839	            reasons.add("calibration_ledger_bracket_session_conflict")
   840	            continue
   841	        open_receipt = state["open"]
   842	        if not _session_identity_matches(receipt, open_receipt):
   843	            reasons.add("calibration_ledger_bracket_session_conflict")
   844	            continue
   845	        finals = state["finals"]
   846	        if event == BRACKET_SESSION_FINALIZATION_EVENT:
   847	            slot = str(receipt["slot"])
   848	            expected_slot = BRACKET_SESSION_SLOTS[len(finals)] if len(finals) < 2 else None
   849	            reserved = open_receipt["slots"].get(slot)
   850	            if (
   851	                state["abort"] is not None
   852	                or slot != expected_slot
   853	                or slot in finals
   854	                or not isinstance(reserved, Mapping)
   855	                or receipt["attempt_id"] != reserved["attempt_id"]
   856	                or receipt["custody_locator"] != reserved["custody_locator"]
   857	                or dict(receipt["identity_epoch"]) != dict(reserved["identity_epoch"])
   858	                or dict(receipt["t1_bindings"]) != dict(reserved["t1_bindings"])
   859	            ):
   860	                reasons.add("calibration_ledger_bracket_session_conflict")
   861	                continue
   862	            finals[slot] = receipt
   863	            continue
   864	        finalized_slots = list(finals)
   865	        unused_slots = [slot for slot in BRACKET_SESSION_SLOTS if slot not in finals]
   866	        if (
   867	            event != BRACKET_SESSION_ABORT_EVENT
   868	            or state["abort"] is not None
   869	            or len(finals) == 2
   870	            or receipt["finalized_slots"] != finalized_slots
   871	            or receipt["unused_slots"] != unused_slots
   872	        ):
   873	            reasons.add("calibration_ledger_bracket_session_conflict")
   874	            continue
   875	        state["abort"] = receipt
   876	
   877	    sessions: list[CalibrationBracketSession] = []
   878	    completed_observations: list[LedgerObservation] = []
   879	    for session_id, state in sorted(
   880	        states.items(), key=lambda item: int(item[1]["open"]["sequence"])
   881	    ):
   882	        open_receipt = state["open"]
   883	        finals = state["finals"]
   884	        abort = state["abort"]
   885	        if abort is not None:
   886	            session_state = "aborted"
   887	        elif len(finals) == 2:
   888	            session_state = "finalized"
   889	        else:
   890	            session_state = "open"
   891	            reasons.add("calibration_ledger_bracket_session_open")
   892	        finalized_observations = {
   893	            slot: _observation_from_receipt(
   894	                receipt,
   895	                observation_kind=(
   896	                    "bracket-session-finalized"
   897	                    if session_state == "finalized"
   898	                    else "bracket-session-aborted"
   899	                ),
   900	                session=open_receipt,
   901	            )
   902	            for slot, receipt in finals.items()
   903	        }
   904	        if session_state != "aborted":
   905	            completed_observations.extend(
   906	                finalized_observations[slot]
   907	                for slot in BRACKET_SESSION_SLOTS
   908	                if slot in finalized_observations
   909	            )
   910	        sessions.append(
   911	            CalibrationBracketSession(
   912	                session_id=session_id,
   913	                window_id=str(open_receipt["window_id"]),
   914	                plan_id=str(open_receipt["plan_id"]),
   915	                plan_sha256=str(open_receipt["plan_sha256"]),
   916	                evidence_root_id=str(open_receipt["evidence_root_id"]),
   917	                capability_receipt_digest=str(open_receipt["receipt_digest"]),
   918	                capability_sequence=int(open_receipt["sequence"]),
   919	                slot_attempt_ids=MappingProxyType(
   920	                    {
   921	                        slot: str(open_receipt["slots"][slot]["attempt_id"])
   922	                        for slot in BRACKET_SESSION_SLOTS
   923	                    }
   924	                ),
   925	                state=session_state,
   926	                finalized_slots=MappingProxyType(finalized_observations),
   927	                abort_receipt_digest=(
   928	                    str(abort["receipt_digest"]) if abort is not None else None
   929	                ),
   930	                abort_reason=(str(abort["reason"]) if abort is not None else None),
   931	            )
   932	        )
   933	    return sessions, completed_observations, reasons
   934	
   935	
   936	def _attempts_and_observations(
   937	    receipts: Sequence[Mapping[str, Any]],
   938	) -> tuple[list[LedgerObservation], list[CalibrationBracketSession], set[str]]:
   939	    pending: dict[str, Mapping[str, Any]] = {}
   940	    finalized: dict[str, Mapping[str, Any]] = {}
   941	    reasons: set[str] = set()
   942	    for receipt in receipts:
   943	        if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
   944	            continue
   945	        attempt_id = str(receipt["attempt_id"])
   946	        if receipt["event"] in {
   947	            "reservation",
   948	            HISTORICAL_IMPORT_RESERVATION_EVENT,
   949	        }:
   950	            if attempt_id in pending or attempt_id in finalized:
   951	                reasons.add("calibration_ledger_attempt_conflict")
   952	            else:
   953	                pending[attempt_id] = receipt
   954	            continue
   955	        reservation = pending.get(attempt_id)
   956	        expected_final_event = (
   957	            HISTORICAL_IMPORT_FINALIZATION_EVENT
   958	            if reservation is not None
   959	            and reservation["event"] == HISTORICAL_IMPORT_RESERVATION_EVENT
   960	            else "finalization"
   961	        )
   962	        if (
   963	            reservation is None
   964	            or attempt_id in finalized
   965	            or receipt["event"] != expected_final_event
   966	        ):
   967	            reasons.add("calibration_ledger_attempt_conflict")
   968	        else:
   969	            finalized[attempt_id] = receipt
   970	    if set(pending) - set(finalized):
   971	        reasons.add("calibration_ledger_pending")
   972	
   973	    observations: list[LedgerObservation] = []
   974	    content_classification: dict[str, tuple[str, tuple[tuple[str, Any], ...]]] = {}
   975	    for attempt_id, receipt in sorted(
   976	        finalized.items(), key=lambda item: int(item[1]["sequence"])
   977	    ):
   978	        content_id = receipt.get("content_id")
   979	        epoch = dict(receipt["identity_epoch"])
   980	        if isinstance(content_id, str):
   981	            classification = (
   982	                (
   983	                    "unresolved"
   984	                    if receipt["disposition"] == "abandoned"
   985	                    else str(receipt["disposition"])
   986	                ),
   987	                tuple((field, epoch.get(field)) for field in IDENTITY_EPOCH_FIELDS),
   988	            )
   989	            previous = content_classification.get(content_id)
   990	            if previous is not None and previous != classification:
   991	                reasons.add("calibration_ledger_content_conflict")
   992	            content_classification[content_id] = classification
   993	        observations.append(
   994	            _observation_from_receipt(
   995	                receipt,
   996	                observation_kind=(
   997	                    "historical-import"
   998	                    if receipt["event"] == HISTORICAL_IMPORT_FINALIZATION_EVENT
   999	                    else "live-capture"
  1000	                ),
  1001	            )
  1002	        )
  1003	    sessions, session_observations, session_reasons = (
  1004	        _bracket_sessions_and_observations(receipts)
  1005	    )
  1006	    reasons.update(session_reasons)
  1007	    session_attempt_ids = {
  1008	        attempt_id
  1009	        for session in sessions
  1010	        for attempt_id in session.slot_attempt_ids.values()
  1011	    }
  1012	    if set(pending) & session_attempt_ids:
  1013	        reasons.add("calibration_ledger_bracket_session_conflict")
  1014	    observations.extend(session_observations)
  1015	    content_classification.clear()
  1016	    classification_observations = list(observations)
  1017	    visible_attempts = {observation.attempt_id for observation in observations}
  1018	    classification_observations.extend(
  1019	        observation
  1020	        for session in sessions
  1021	        for observation in session.finalized_slots.values()
  1022	        if observation.attempt_id not in visible_attempts
  1023	    )
  1024	    for observation in classification_observations:
  1025	        if observation.content_id is None:
  1040	
  1041	
  1042	def _custody_reasons(
  1043	    observations: Sequence[LedgerObservation], repo_root: Path
  1044	) -> set[str]:
  1045	    for observation in observations:
  1046	        if not observation.artifact_sha256:
  1047	            if observation.disposition == "abandoned":
  1048	                continue
  1049	            return {"calibration_ledger_custody_invalid"}
  1050	        root = Path(observation.custody_locator)
  1051	        if not root.is_absolute():
  1052	            root = Path(repo_root) / root
  1053	        for relative, expected in observation.artifact_sha256.items():
  1054	            path = root / relative
  1055	            try:
  1056	                actual = hashlib.sha256(path.read_bytes()).hexdigest()
  1057	            except OSError:
  1058	                return {"calibration_ledger_custody_invalid"}
  1059	            if actual != expected:
  1060	                return {"calibration_ledger_custody_invalid"}
  1061	    return set()
  1062	
  1063	
  1064	def load_calibration_ledger_snapshot(
  1065	    ledger_path: Path = DEFAULT_LEDGER_PATH,
  1066	    head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
  1067	    *,
  1068	    baseline_sequence: int | None = None,
  1069	    baseline_digest: str | None = None,
  1070	    require_committed_pin: bool = True,
  1071	    verify_custody: bool = True,
  1072	    repo_root: Path = REPO_ROOT,
  1073	) -> CalibrationLedgerSnapshot:
  1074	    """Load, authenticate, and freeze exactly one ledger snapshot.
  1075	
  1076	    A proper physical prefix of the pin is classified explicitly as rollback;
  1077	    any other physical/pinned disagreement is a stale-head mismatch.  The
  1078	    baseline must occur at its exact sequence in the same complete chain.
  1079	    This closes workflow omission, unregistered evidence, and rollback or
  1080	    stale-head consumption; it does not defend against a malicious trusted
  1081	    writer or a rewrite of both Git and the full ledger history.
  1082	    """
  1083	
  1084	    ledger_path = Path(ledger_path)
  1085	    head_pin_path = Path(head_pin_path)
  1086	    reasons: set[str] = set()
  1087	    try:
  1088	        pin_raw = head_pin_path.read_bytes()
  1089	        pin_value = json.loads(pin_raw)
  1090	    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
  1091	        pin_raw = b""
  1092	        pin_value = None
  1093	    pin = _head_pin(pin_value)
  1094	    if pin is None:
  1095	        reasons.add("calibration_ledger_malformed")
  1096	        pinned_sequence, pinned_digest = 0, GENESIS_DIGEST
  1097	    else:
  1098	        pinned_sequence, pinned_digest = pin
  1099	    try:
  1100	        raw = ledger_path.read_bytes()
  1101	    except OSError:
  1102	        raw = b""
  1103	        if pinned_sequence > 0:
  1104	            reasons.add("calibration_ledger_missing")
  1105	    genesis_development_bootstrap = (
  1106	        pinned_sequence == 0
  1107	        and pinned_digest == GENESIS_DIGEST
  1108	        and not raw
  1109	        and not ledger_path.exists()
  1110	    )
  1111	    if (
  1112	        require_committed_pin
  1113	        # The checked-in fixture starts at genesis.  Before its first commit,
  1114	        # an absent physical ledger cannot license a claim (there are no
  1115	        # endpoints); permitting this development-only empty view avoids a
  1116	        # circular "commit before tests" bootstrap. Any physical byte or any
  1117	        # non-genesis pin remains strictly commit-authenticated.
  1118	        and not genesis_development_bootstrap
  1119	        and _committed_pin_bytes(head_pin_path, repo_root) != pin_raw
  1120	    ):
  1121	        reasons.add("calibration_ledger_head_uncommitted")
  1122	    receipts, parse_reasons = _parse_ledger(raw)
  1123	    reasons.update(parse_reasons)
  1124	    physical_sequence = len(receipts)
  1125	    physical_digest = (
  1126	        str(receipts[-1]["receipt_digest"]) if receipts else GENESIS_DIGEST
  1127	    )
  1128	    if (physical_sequence, physical_digest) != (pinned_sequence, pinned_digest):
  1129	        if physical_sequence < pinned_sequence:
  1130	            reasons.add("calibration_ledger_rollback")
  1131	        else:
  1132	            reasons.add("calibration_ledger_head_mismatch")
  1133	    if baseline_sequence is not None or baseline_digest is not None:
  1134	        if (
  1135	            isinstance(baseline_sequence, bool)
  1136	            or not isinstance(baseline_sequence, int)
  1137	            or baseline_sequence < 0
  1138	            or not _is_sha256(baseline_digest)
  1139	        ):
  1140	            reasons.add("calibration_ledger_baseline_missing")
  1141	        else:
  1142	            in_chain = (
  1143	                baseline_digest == GENESIS_DIGEST
  1144	                if baseline_sequence == 0
  1145	                else baseline_sequence <= len(receipts)
  1146	                and receipts[baseline_sequence - 1]["receipt_digest"]
  1147	                == baseline_digest
  1148	            )
  1149	            if not in_chain or baseline_sequence > pinned_sequence:
  1150	                reasons.add("calibration_ledger_baseline_missing")
  1151	    observations, bracket_sessions, state_reasons = _attempts_and_observations(
  1152	        receipts
  1153	    )
  1154	    reasons.update(state_reasons)
  1155	    if verify_custody:
  1156	        custody_observations = list(observations)
  1157	        custody_attempt_ids = {observation.attempt_id for observation in observations}
  1158	        for session in bracket_sessions:
  1159	            custody_observations.extend(
  1160	                observation
  1161	                for observation in session.finalized_slots.values()
  1162	                if observation.attempt_id not in custody_attempt_ids
  1163	            )
  1164	        reasons.update(_custody_reasons(custody_observations, repo_root))
  1165	    return CalibrationLedgerSnapshot(
  1166	        ledger_schema=LEDGER_SCHEMA,
  1167	        ledger_path=ledger_path,
  1168	        head_sequence=physical_sequence,
  1169	        head_digest=physical_digest,
  1170	        receipts=tuple(_frozen_mapping(receipt) for receipt in receipts),
  1171	        observations=tuple(observations),
  1172	        refusal_reasons=tuple(sorted(reasons)),
  1173	        bracket_sessions=tuple(bracket_sessions),
  1174	        baseline_sequence=baseline_sequence,
  1175	        baseline_digest=baseline_digest,
  1176	        committed_head_sequence=pinned_sequence,
  1177	        committed_head_digest=pinned_digest,
  1178	    )
  1179	
  1180	
  1180	
  1181	def _new_receipt(
  1182	    *,
  1183	    sequence: int,
  1184	    predecessor_digest: str,
  1185	    event: str,
  1186	    attempt_id: str,
  1187	    content_id: str | None,
  1188	    artifacts: Mapping[str, str],
  1189	    identity_epoch: Mapping[str, Any] | None,
  1190	    t1_bindings: Mapping[str, Any] | None,
  1191	    capture_wall_time_s: str | None,
  1192	    exact_bound_lexeme_s: str | None,
  1193	    disposition: str,
  1194	    custody_locator: str,
  1195	    historical_import_input_sha256: Mapping[str, str] | None = None,
  1196	) -> dict[str, Any]:
  1197	    receipt: dict[str, Any] = {
  1198	        "schema_version": RECEIPT_SCHEMA,
  1199	        "ledger_schema": LEDGER_SCHEMA,
  1200	        "sequence": sequence,
  1201	        "predecessor_digest": predecessor_digest,
  1202	        "event": event,
  1203	        "attempt_id": attempt_id,
  1204	        "content_id": content_id,
  1205	        "artifact_sha256": dict(sorted(artifacts.items())),
  1206	        "identity_epoch": _normalized_vector(identity_epoch, IDENTITY_EPOCH_FIELDS),
  1207	        "t1_bindings": _normalized_vector(t1_bindings, T1_FIELDS),
  1208	        "capture_wall_time_s": capture_wall_time_s,
  1209	        "exact_bound_lexeme_s": exact_bound_lexeme_s,
  1210	        "disposition": disposition,
  1211	        "custody_locator": custody_locator,
  1212	    }
  1213	    if historical_import_input_sha256 is not None:
  1214	        receipt[_HISTORICAL_IMPORT_INPUT_SHA256_KEY] = dict(
  1215	            sorted(historical_import_input_sha256.items())
  1216	        )
  1217	    receipt["receipt_digest"] = _receipt_digest(receipt)
  1218	    return receipt
  1219	
  1220	
  1221	def _new_bracket_session_record(
  1222	    *,
  1223	    sequence: int,
  1224	    predecessor_digest: str,
  1225	    event: str,
  1226	    session_identity: Mapping[str, Any],
  1227	    fields: Mapping[str, Any],
  1228	) -> dict[str, Any]:
  1229	    receipt = {
  1230	        "schema_version": BRACKET_SESSION_SCHEMA,
  1231	        "ledger_schema": LEDGER_SCHEMA,
  1232	        "sequence": sequence,
  1233	        "predecessor_digest": predecessor_digest,
  1234	        "event": event,
  1235	        **{field: session_identity.get(field) for field in _SESSION_IDENTITY_KEYS},
  1236	        **dict(fields),
  1237	    }
  1238	    receipt["receipt_digest"] = _receipt_digest(receipt)
  1239	    return receipt
  1240	
  1241	
  1242	def _json_object_from_bytes(raw: bytes, source: Path) -> Mapping[str, Any]:
  1243	    try:
  1244	        value = json.loads(raw)
  1245	    except (UnicodeDecodeError, json.JSONDecodeError) as exc:

exec
/bin/zsh -lc "nl -ba joulewise/calibration_ledger.py | sed -n '1010,1045p'; git diff --unified=60 -- joulewise/calibration_bracketing.py; rg -n \"bracket|candidate|post_cutoff|session\" joulewise/calibration_bracketing.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
  1010	        for attempt_id in session.slot_attempt_ids.values()
  1011	    }
  1012	    if set(pending) & session_attempt_ids:
  1013	        reasons.add("calibration_ledger_bracket_session_conflict")
  1014	    observations.extend(session_observations)
  1015	    content_classification.clear()
  1016	    classification_observations = list(observations)
  1017	    visible_attempts = {observation.attempt_id for observation in observations}
  1018	    classification_observations.extend(
  1019	        observation
  1020	        for session in sessions
  1021	        for observation in session.finalized_slots.values()
  1022	        if observation.attempt_id not in visible_attempts
  1023	    )
  1024	    for observation in classification_observations:
  1025	        if observation.content_id is None:
  1026	            continue
  1027	        classification = (
  1028	            observation.classification_disposition,
  1029	            tuple(
  1030	                (field, observation.identity_epoch.get(field))
  1031	                for field in IDENTITY_EPOCH_FIELDS
  1032	            ),
  1033	        )
  1034	        previous = content_classification.get(observation.content_id)
  1035	        if previous is not None and previous != classification:
  1036	            reasons.add("calibration_ledger_content_conflict")
  1037	        content_classification[observation.content_id] = classification
  1038	    observations.sort(key=lambda observation: observation.sequence)
  1039	    return observations, sessions, reasons
  1040	
  1041	
  1042	def _custody_reasons(
  1043	    observations: Sequence[LedgerObservation], repo_root: Path
  1044	) -> set[str]:
  1045	    for observation in observations:
diff --git a/joulewise/calibration_bracketing.py b/joulewise/calibration_bracketing.py
index c97f244..7439156 100644
--- a/joulewise/calibration_bracketing.py
+++ b/joulewise/calibration_bracketing.py
@@ -1,165 +1,178 @@
 """Claim-time pre/post powermetrics fiducial calibration bracketing.
 
 The bracket carries a nonparametric 95/95 calibration-distribution bound into
 claims only under the registered T1-T3 transfer assumptions; it does not turn
 either finite sample maximum into an unconditional instrument property.
 """
 
 from __future__ import annotations
 
 import hashlib
 import json
 import math
 from dataclasses import dataclass, replace
 from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
 from pathlib import Path
 from typing import Any, Mapping, Sequence
 
 from joulewise.bundle_read import BundleReadError, BundleReader
 from joulewise.calibration_ledger import (
     IDENTITY_EPOCH_FIELDS,
     LEDGER_SCHEMA,
     CalibrationLedgerSnapshot,
     LedgerObservation,
     content_id_from_artifact_hashes,
 )
 from joulewise.powermetrics_fiducial import (
     CAPTURE_TIME_FIELD,
     MAX_AGE_S,
     PROTOCOL_ID,
     PROTOCOL_V2_ID,
     REGION_COVERAGE_RESOLUTION_S,
     RESIDUAL_REGION_METHOD,
     V2_BINDING_FIELDS,
     capture_wall_time_from_events,
     protocol_pulse_count,
     protocol_sha256,
     verify_stored_evidence_physics,
 )
 from joulewise.schemas import CalibrationBracketingPolicy
 
 BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
+BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
 ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
 ACCEPTANCE_FIXTURE_SCHEMA = (
     "joulewise.calibration_acceptance_bound.v2.fixture.v1"
 )
 ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
 DEFAULT_ACCEPTANCE_BOUND_PATH = (
     Path(__file__).resolve().parents[1]
     / "configs"
     / "calibration"
     / "calibration_acceptance_d079_v2.json"
 )
 DEFAULT_ACCEPTANCE_BOUND_SHA256 = (
     "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb"
 )
 ISSUED_ACCEPTANCE_BOUND_SHA256 = (
     "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985"
 )
 _REPO_ROOT = Path(__file__).resolve().parents[1]
 ESTIMATOR_CODE_PATHS = (
     "joulewise/powermetrics_fiducial.py",
     "joulewise/uncertainty_evidence.py",
     "joulewise/adapters/powermetrics.py",
     "joulewise/reduce.py",
 )
 ACCEPTANCE_IDENTITY_FIELDS = IDENTITY_EPOCH_FIELDS
 _D102_OPERATIVE_VALUES = {
     "bracket_screen_s": "0.010818",
     "preflight_level_screen_s": "0.033558756679900",
     "max_budgetable_excess_s": "0.001275166090593858",
     "maximum_budgetable_drift_s": "0.012093166090593858",
 }
 
 
 @dataclass(frozen=True)
 class CalibrationCandidate:
     relative_path: str
     manifest_sha256: str
     evidence_sha256: str
     protocol_id: str
     capture_wall_time_s: float
     # Production authentication stores the source decimal lexeme here.  Float
     # remains accepted only for backwards-compatible synthetic callers; the
     # authenticated loader below never takes that branch.
     b_fiducial_s: Decimal | str | float
     bindings: Mapping[str, Any]
     attempt_id: str | None = None
     content_id: str | None = None
     ledger_receipt_digest: str | None = None
+    bracket_session_id: str | None = None
+    bracket_slot: str | None = None
+    bracket_window_id: str | None = None
+    bracket_plan_id: str | None = None
+    bracket_plan_sha256: str | None = None
+    bracket_evidence_root_id: str | None = None
 
     def descriptor(self) -> dict[str, Any]:
         bound = _candidate_decimal(self)
         return {
             "relative_path": self.relative_path,
             "manifest_sha256": self.manifest_sha256,
             "evidence_sha256": self.evidence_sha256,
             "protocol_id": self.protocol_id,
             "capture_wall_time_s": self.capture_wall_time_s,
             # This descriptor is the recorded reducer boundary.  Keep both the
             # exact acceptance lexeme and its explicit binary64 projection.
             "b_fiducial_s": float(bound) if bound is not None else self.b_fiducial_s,
             "b_fiducial_decimal_s": str(bound) if bound is not None else None,
             "attempt_id": self.attempt_id,
             "content_id": self.content_id,
             "ledger_receipt_digest": self.ledger_receipt_digest,
+            "bracket_session_id": self.bracket_session_id,
+            "bracket_slot": self.bracket_slot,
+            "bracket_window_id": self.bracket_window_id,
+            "bracket_plan_id": self.bracket_plan_id,
+            "bracket_plan_sha256": self.bracket_plan_sha256,
+            "bracket_evidence_root_id": self.bracket_evidence_root_id,
         }
 
 
 def _canonical_sha256(value: Mapping[str, Any]) -> str:
     raw = json.dumps(
         dict(value),
         sort_keys=True,
         separators=(",", ":"),
         ensure_ascii=False,
         allow_nan=False,
     ).encode("utf-8")
     return hashlib.sha256(raw).hexdigest()
 
 
 def _decimal(value: Any) -> Decimal | None:
     if not isinstance(value, str) or not value:
         return None
     try:
         result = Decimal(value)
     except InvalidOperation:
         return None
     return result if result.is_finite() else None
 
 
 def _candidate_decimal(candidate: CalibrationCandidate) -> Decimal | None:
     value = candidate.b_fiducial_s
     if isinstance(value, Decimal):
         result = value
     elif isinstance(value, str):
         result = _decimal(value)
         if result is None:
             return None
     elif (
         isinstance(value, int | float)
         and not isinstance(value, bool)
         and math.isfinite(float(value))
     ):
         # Compatibility for synthetic callers that predate D-102. Production
         # candidates carry strings from authenticated evidence bytes instead.
         result = Decimal(str(value))
     else:
         return None
     return result if result.is_finite() else None
 
 
 def _current_estimator_code_sha256() -> dict[str, str] | None:
     try:
         return {
             relative: hashlib.sha256((_REPO_ROOT / relative).read_bytes()).hexdigest()
             for relative in ESTIMATOR_CODE_PATHS
         }
     except OSError:
         return None
 
 
 def _valid_acceptance_bound(value: Any) -> bool:
     """Validate the D-102 artifact from its decimal-source member table."""
 
     if not isinstance(value, Mapping):
         return False
@@ -436,120 +449,296 @@ def load_calibration_acceptance_bound(
     try:
         raw = Path(path).read_bytes()
     except OSError:
         return None
     return _acceptance_bound_from_authenticated_bytes(raw)
 
 
 def _acceptance_bound_from_authenticated_bytes(
     raw: bytes,
 ) -> dict[str, Any] | None:
     """Parse acceptance bytes only when their role-indexed pin authenticates."""
 
     try:
         value = json.loads(raw)
     except (UnicodeDecodeError, json.JSONDecodeError):
         return None
     # Any file route is authenticated by one of the two reviewed exact-byte
     # states: the genesis fixture retained for pre-issuance tests, or the
     # deterministically emitted issued artifact. A caller cannot turn an
     # alternate self-consistent document into authority by choosing a path.
     expected_sha256 = {
         "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
         "issued": ISSUED_ACCEPTANCE_BOUND_SHA256,
     }.get(value.get("artifact_role") if isinstance(value, Mapping) else None)
     if hashlib.sha256(raw).hexdigest() != expected_sha256:
         return None
     if not _valid_acceptance_bound(value):
         return None
     return dict(value)
 
 
 def _authenticated_explicit_acceptance_bound(
     value: Mapping[str, Any],
 ) -> dict[str, Any] | None:
     """Authenticate an in-memory artifact against the checked-in byte pin."""
 
     pinned = load_calibration_acceptance_bound()
     if pinned is None or dict(value) != pinned:
         return None
     return pinned
 
 
 def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
     """Return the reviewed exact-byte pin for a validated artifact role."""
 
     return (
         ISSUED_ACCEPTANCE_BOUND_SHA256
         if artifact.get("artifact_role") == "issued"
         else DEFAULT_ACCEPTANCE_BOUND_SHA256
     )
 
 
 def _valid_sha256(value: Any) -> bool:
     return (
         isinstance(value, str)
         and len(value) == 64
         and all(char in "0123456789abcdef" for char in value)
     )
 
 
+_BRACKET_BINDING_KEYS = {
+    "schema_version",
+    "ledger_schema",
+    "session_id",
+    "window_id",
+    "plan_id",
+    "plan_sha256",
+    "evidence_root_id",
+    "capability_receipt_digest",
+    "terminal_head",
+    "endpoints",
+    "binding_digest",
+}
+_BRACKET_ENDPOINT_KEYS = {
+    "attempt_id",
+    "receipt_digest",
+    "content_digest",
+}
+
+
+def _binding_core(binding: Mapping[str, Any]) -> dict[str, Any]:
+    return {key: value for key, value in binding.items() if key != "binding_digest"}
+
+
+def build_calibration_bracket_binding(
+    ledger_snapshot: CalibrationLedgerSnapshot,
+    *,
+    session_id: str,
+    window_id: str,
+    plan_id: str,
+    plan_sha256: str,
+    evidence_root_id: str,
+) -> dict[str, Any]:
+    """Bind one frozen window to its exact finalized session endpoints."""
+
+    if not isinstance(ledger_snapshot, CalibrationLedgerSnapshot) or not ledger_snapshot.valid:
+        raise ValueError("bracket binding requires a valid pinned ledger snapshot")
+    session = ledger_snapshot.bracket_session_by_id.get(session_id)
+    expected_identity = (window_id, plan_id, plan_sha256, evidence_root_id)
+    if (
+        session is None
+        or session.state != "finalized"
+        or (
+            session.window_id,
+            session.plan_id,
+            session.plan_sha256,
+            session.evidence_root_id,
+        )
+        != expected_identity
+    ):
+        raise ValueError("bracket session does not match the frozen window identity")
+    pre = session.finalized_slots.get("pre")
+    post = session.finalized_slots.get("post")
+    if (
+        pre is None
+        or post is None
+        or pre.disposition != "valid"
+        or post.disposition != "valid"
+        or pre.content_id is None
+        or post.content_id is None
+        or post.sequence != ledger_snapshot.head_sequence
+        or post.receipt_digest != ledger_snapshot.head_digest
+    ):
+        raise ValueError("bracket session endpoints are not valid at the terminal head")
+    binding: dict[str, Any] = {
+        "schema_version": BRACKET_BINDING_SCHEMA,
+        "ledger_schema": LEDGER_SCHEMA,
+        "session_id": session.session_id,
+        "window_id": session.window_id,
+        "plan_id": session.plan_id,
+        "plan_sha256": session.plan_sha256,
+        "evidence_root_id": session.evidence_root_id,
+        "capability_receipt_digest": session.capability_receipt_digest,
+        "terminal_head": {
+            "sequence": post.sequence,
+            "head_digest": post.receipt_digest,
+            "ledger_schema": LEDGER_SCHEMA,
+        },
+        "endpoints": {
+            role: {
+                "attempt_id": observation.attempt_id,
+                "receipt_digest": observation.receipt_digest,
+                "content_digest": observation.content_id,
+            }
+            for role, observation in (("pre", pre), ("post", post))
+        },
+    }
+    binding["binding_digest"] = _canonical_sha256(binding)
+    return binding
+
+
+def validate_calibration_bracket_binding(
+    binding: Mapping[str, Any],
+    ledger_snapshot: CalibrationLedgerSnapshot,
+    *,
+    window_id: str | None = None,
+    plan_id: str | None = None,
+    plan_sha256: str | None = None,
+    evidence_root_id: str | None = None,
+) -> tuple[LedgerObservation, LedgerObservation] | None:
+    """Return the exact authenticated pair, or ``None`` on any substitution."""
+
+    if (
+        not isinstance(binding, Mapping)
+        or set(binding) != _BRACKET_BINDING_KEYS
+        or binding.get("schema_version") != BRACKET_BINDING_SCHEMA
+        or binding.get("ledger_schema") != LEDGER_SCHEMA
+        or not _valid_sha256(binding.get("plan_sha256"))
+        or not _valid_sha256(binding.get("capability_receipt_digest"))
+        or not _valid_sha256(binding.get("binding_digest"))
+        or binding.get("binding_digest") != _canonical_sha256(_binding_core(binding))
+        or not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
+        or not ledger_snapshot.valid
+    ):
+        return None
+    for field, expected in (
+        ("window_id", window_id),
+        ("plan_id", plan_id),
+        ("plan_sha256", plan_sha256),
+        ("evidence_root_id", evidence_root_id),
+    ):
+        if expected is not None and binding.get(field) != expected:
+            return None
+    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
+    if (
+        session is None
+        or session.state != "finalized"
+        or binding.get("window_id") != session.window_id
+        or binding.get("plan_id") != session.plan_id
+        or binding.get("plan_sha256") != session.plan_sha256
+        or binding.get("evidence_root_id") != session.evidence_root_id
+        or binding.get("capability_receipt_digest")
+        != session.capability_receipt_digest
+    ):
+        return None
+    terminal = binding.get("terminal_head")
+    endpoints = binding.get("endpoints")
+    if (
+        not isinstance(terminal, Mapping)
+        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
+        or terminal.get("ledger_schema") != LEDGER_SCHEMA
+        or isinstance(terminal.get("sequence"), bool)
+        or not isinstance(terminal.get("sequence"), int)
+        or not _valid_sha256(terminal.get("head_digest"))
+        or not isinstance(endpoints, Mapping)
+        or set(endpoints) != {"pre", "post"}
+    ):
+        return None
+    resolved: list[LedgerObservation] = []
+    for role in ("pre", "post"):
+        endpoint = endpoints.get(role)
+        observation = session.finalized_slots.get(role)
+        if (
+            not isinstance(endpoint, Mapping)
+            or set(endpoint) != _BRACKET_ENDPOINT_KEYS
+            or observation is None
+            or observation.disposition != "valid"
+            or observation.content_id is None
+            or endpoint.get("attempt_id") != observation.attempt_id
+            or endpoint.get("receipt_digest") != observation.receipt_digest
+            or endpoint.get("content_digest") != observation.content_id
+        ):
+            return None
+        resolved.append(observation)
+    post = resolved[1]
+    if (
+        terminal.get("sequence") != post.sequence
+        or terminal.get("head_digest") != post.receipt_digest
+        or post.sequence > len(ledger_snapshot.receipts)
+        or ledger_snapshot.receipts[post.sequence - 1].get("receipt_digest")
+        != post.receipt_digest
+    ):
+        return None
+    return resolved[0], resolved[1]
+
+
 def _binding_evidence_authentic(
     evidence: Mapping[str, Any], bindings: Mapping[str, Any]
 ) -> bool:
     binding_evidence = evidence.get("binding_evidence")
     binary = (
         binding_evidence.get("powermetrics_binary")
         if isinstance(binding_evidence, Mapping)
         else None
     )
     power_policy = (
         binding_evidence.get("power_policy")
         if isinstance(binding_evidence, Mapping)
         else None
     )
     # Canonical form MUST match the generation (powermetrics_fiducial) and
     # reduce-side consumers byte-for-byte: ensure_ascii=False (delta-review
     # P2 — the ASCII-default form made authentic non-ASCII binding vectors
     # unmatchable as bracket candidates).
     canonical = json.dumps(
         dict(bindings),
         sort_keys=True,
         separators=(",", ":"),
         ensure_ascii=False,
         allow_nan=False,
     ).encode("utf-8")
     return bool(
         isinstance(binding_evidence, Mapping)
         and binding_evidence.get("schema_version")
         == "joulewise.instrument_binding_evidence.v1"
         and binding_evidence.get("binding_vector_sha256")
         == hashlib.sha256(canonical).hexdigest()
         and isinstance(binary, Mapping)
         and binary.get("sha256") == bindings.get("powermetrics_sha256")
         and isinstance(binary.get("path"), str)
         and bool(binary.get("path"))
         and isinstance(power_policy, Mapping)
         and power_policy.get("id") == bindings.get("power_policy")
     )
 
 
 def load_calibration_candidate(
     directory: Path, *, runs_root: Path
 ) -> CalibrationCandidate | None:
     """Authenticate one standalone validation directory from primary bytes."""
 
     root = Path(runs_root).resolve()
     try:
         directory = Path(directory).resolve(strict=True)
         relative = directory.relative_to(root).as_posix()
         manifest_raw = (directory / "manifest.json").read_bytes()
         manifest = json.loads(manifest_raw)
     except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
         return None
     artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
     if (
         not relative
         or not isinstance(artifacts, Mapping)
         or manifest.get("schema_version")
         != "joulewise.instrument_validation_manifest.v1"
     ):
@@ -649,225 +838,241 @@ def load_calibration_candidate(
         # acceptance comparison converts that value through binary64 again.
         effective_bound_lexeme = str(float(effective_bound))
     return CalibrationCandidate(
         relative_path=relative,
         manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
         evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
         protocol_id=str(protocol_id),
         capture_wall_time_s=float(capture),
         b_fiducial_s=effective_bound_lexeme,
         bindings=dict(bindings),
     )
 
 
 def _candidate_from_observation(
     observation: LedgerObservation,
 ) -> CalibrationCandidate | None:
     """Authenticate one valid ledger observation from its custody locator."""
 
     if observation.disposition != "valid" or observation.content_id is None:
         return None
     custody = Path(observation.custody_locator)
     candidate = load_calibration_candidate(
         custody,
         runs_root=custody.parent.parent,
     )
     if candidate is None:
         return None
     bound = _candidate_decimal(candidate)
     receipt_bound = _decimal(observation.exact_bound_lexeme_s)
     try:
         receipt_capture = float(observation.capture_wall_time_s)
     except (TypeError, ValueError):
         return None
     if (
         candidate.manifest_sha256
         != observation.artifact_sha256.get("manifest.json")
         or candidate.evidence_sha256
         != observation.artifact_sha256.get("instrument_evidence.json")
         or content_id_from_artifact_hashes(observation.artifact_sha256)
         != observation.content_id
         or bound is None
         or receipt_bound is None
         or bound != receipt_bound
         or candidate.capture_wall_time_s != receipt_capture
         or any(
             candidate.bindings.get(field) != observation.t1_bindings.get(field)
             for field in V2_BINDING_FIELDS
         )
         or any(
             candidate.bindings.get(field) != observation.identity_epoch.get(field)
             for field in ACCEPTANCE_IDENTITY_FIELDS
         )
     ):
         return None
     return replace(
         candidate,
         relative_path=observation.custody_locator,
         attempt_id=observation.attempt_id,
         content_id=observation.content_id,
         ledger_receipt_digest=observation.receipt_digest,
+        bracket_session_id=observation.bracket_session_id,
+        bracket_slot=observation.bracket_slot,
+        bracket_window_id=observation.bracket_window_id,
+        bracket_plan_id=observation.bracket_plan_id,
+        bracket_plan_sha256=observation.bracket_plan_sha256,
+        bracket_evidence_root_id=observation.bracket_evidence_root_id,
     )
 
 
 def discover_calibration_candidates(
     ledger_snapshot: CalibrationLedgerSnapshot,
 ) -> tuple[CalibrationCandidate, ...]:
     """Enumerate valid endpoints from the sole ledger authority.
 
     The mechanism closes workflow omission, unregistered evidence, and
     rollback/stale-head consumption; it does not defend against a malicious
     trusted writer or a rewrite of both Git and full ledger history.
     """
 
-    if not isinstance(ledger_snapshot, CalibrationLedgerSnapshot) or not ledger_snapshot.valid:
+    if (
+        not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
+        or not ledger_snapshot.valid
+        and not ledger_snapshot.is_governed_open_bracket_extension
+    ):
         return ()
     candidates: list[CalibrationCandidate] = []
     for observation in ledger_snapshot.observations:
         if observation.disposition != "valid" or observation.is_historical_import:
             continue
         candidate = _candidate_from_observation(observation)
         if candidate is None:
             return ()
         candidates.append(candidate)
     return tuple(candidates)
 
 
 def _prior_set_matches_import_cutoff_prefix(
     artifact: Mapping[str, Any],
     ledger_snapshot: CalibrationLedgerSnapshot,
 ) -> bool:
     """Bind issuance prior-set data to the import-marked cutoff prefix."""
 
     cutoff = artifact["ledger_cutoff"]
     prefix = tuple(
         observation
         for observation in ledger_snapshot.observations
         if observation.sequence <= cutoff["sequence"]
     )
     # The checked-in schema fixture predates issuance and deliberately has a
     # genesis cutoff. Production issuance, or any fixture containing imported
     # prefix rows, must satisfy the exact marker-bound comparison below.
     if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
         return True
     if any(not observation.is_historical_import for observation in prefix):
         return False
     catalog = artifact["prior_observation_set"]["epoch_catalog"]
     expected = {
         (
             row["attempt_id"],
             row["content_id"],
             row["disposition"],
             row["epoch_id"],
         )
         for row in artifact["prior_observation_set"]["observations"]
     }
     observed: set[tuple[str, str, str, str]] = set()
     for observation in prefix:
         epoch_ids = [
             epoch_id
             for epoch_id, epoch in catalog.items()
             if dict(epoch) == dict(observation.identity_epoch)
         ]
         if observation.content_id is None or len(epoch_ids) != 1:
             return False
         observed.add(
             (
                 observation.attempt_id,
                 observation.content_id,
                 observation.classification_disposition,
                 epoch_ids[0],
             )
         )
     return observed == expected and len(observed) == len(prefix)
 
 
 def evaluate_calibration_bracket(
     candidates: Sequence[CalibrationCandidate],
     *,
     window_start_s: float,
     window_end_s: float,
     bindings: Mapping[str, Any],
     policy: CalibrationBracketingPolicy,
     acceptance_bound: Mapping[str, Any] | None = None,
     ledger_snapshot: CalibrationLedgerSnapshot | None = None,
+    bracket_binding: Mapping[str, Any] | None = None,
+    bracket_window_id: str | None = None,
+    bracket_plan_id: str | None = None,
+    bracket_plan_sha256: str | None = None,
+    bracket_evidence_root_id: str | None = None,
     _allow_unissued_fixture: bool = False,
 ) -> tuple[dict[str, Any], tuple[str, ...]]:
     """Select a causal bracket and apply the provenance-bound D-079 budget."""
 
     result: dict[str, Any] = {
         "schema_version": BRACKET_SCHEMA,
         "policy": {
             "require_bracket": policy.require_bracket,
             "calibration_bracket_max_drift_s": (
                 policy.calibration_bracket_max_drift_s
             ),
         },
         "window_start_s": window_start_s,
         "window_end_s": window_end_s,
         "pre": None,
         "post": None,
         "endpoint_max_b_fiducial_s": None,
         "calibration_drift_allowance_s": None,
         "b_fiducial_s": None,
         "drift_s": None,
         "acceptance": None,
+        "bracket_binding": None,
         "status": "not_required" if not policy.require_bracket else "failed",
     }
     if not policy.require_bracket:
         return result, ()
     if (
         not math.isfinite(window_start_s)
         or not math.isfinite(window_end_s)
         or window_start_s >= window_end_s
     ):
         return result, ("instrument_calibration_bracket_missing",)
 
     using_default_bound = acceptance_bound is None
     artifact = (
         load_calibration_acceptance_bound()
         if using_default_bound
         else _authenticated_explicit_acceptance_bound(acceptance_bound)
     )
     if artifact is None:
         result["acceptance"] = {
             "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
             "artifact": None,
             "freshness": {
                 "status": "stale",
                 "reason": "acceptance_artifact_missing_or_invalid",
             },
         }
         return result, ("calibration_acceptance_bound_stale",)
     artifact_role = artifact["artifact_role"]
     artifact_sha256 = _acceptance_artifact_sha256(artifact)
     if artifact_role == "schema_fixture_unissued" and not _allow_unissued_fixture:
         result["acceptance"] = {
             "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
             "artifact": {
                 "acceptance_id": artifact["acceptance_id"],
                 "artifact_sha256": artifact_sha256,
                 "authentication": "checked_in_genesis_fixture_byte_sha256_pin",
                 "artifact_role": artifact_role,
                 "claim_eligible": False,
             },
             "freshness": {
                 "status": "stale",
                 "reason": "acceptance_artifact_unissued_fixture",
             },
         }
         return result, ("calibration_acceptance_bound_stale",)
     cutoff = artifact["ledger_cutoff"]
     result["acceptance"] = {
         "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
         "artifact": {
             "acceptance_id": artifact["acceptance_id"],
             "artifact_sha256": artifact_sha256,
             "authentication": (
                 "checked_in_issued_artifact_byte_sha256_pin"
                 if artifact_role == "issued"
                 else "checked_in_genesis_fixture_byte_sha256_pin"
             ),
             "artifact_role": artifact_role,
             "claim_eligible": False,
         },
         "freshness": {
@@ -950,241 +1155,284 @@ def evaluate_calibration_bracket(
             "global_runs_root_scan": False,
             "mandatory_triggers": list(prospective["triggers"]),
             "observed_triggers": [],
         },
         "numeric_semantics": {
             "comparisons": "decimal",
             "reducer_boundary": "binary64_recorded_below",
         },
         "ledger_snapshot": {
             "ledger_schema": ledger_snapshot.ledger_schema,
             "sequence": ledger_snapshot.head_sequence,
             "head_digest": ledger_snapshot.head_digest,
             "baseline_sequence": ledger_snapshot.baseline_sequence,
             "baseline_digest": ledger_snapshot.baseline_digest,
             "load_count": 1,
         },
         "preflight": None,
         "drift": None,
     }
     if stale_fields:
         return result, ("calibration_acceptance_bound_stale",)
     observations_by_attempt = ledger_snapshot.observation_by_attempt
     registered_valid = {
         (
             observation.attempt_id,
             observation.content_id,
             observation.receipt_digest,
         )
         for observation in ledger_snapshot.observations
         if observation.disposition == "valid"
         and not observation.is_historical_import
     }
     supplied_valid = {
         (
             candidate.attempt_id,
             candidate.content_id,
             candidate.ledger_receipt_digest,
         )
         for candidate in candidates
     }
     # Even the low-level evaluator requires the complete ledger enumeration.
     # This prevents a caller from narrowing the registered universe to a
     # favorable subset while still passing per-candidate membership checks.
     if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
         return result, ("calibration_ledger_off_ledger_artifact",)
     for candidate in candidates:
         observation = (
             observations_by_attempt.get(candidate.attempt_id)
             if isinstance(candidate.attempt_id, str)
             else None
         )
         if (
             observation is None
             or observation.disposition != "valid"
             or candidate.content_id != observation.content_id
             or candidate.ledger_receipt_digest != observation.receipt_digest
             or candidate.manifest_sha256
             != observation.artifact_sha256.get("manifest.json")
             or candidate.evidence_sha256
             != observation.artifact_sha256.get("instrument_evidence.json")
+            or candidate.bracket_session_id != observation.bracket_session_id
+            or candidate.bracket_slot != observation.bracket_slot
+            or candidate.bracket_window_id != observation.bracket_window_id
+            or candidate.bracket_plan_id != observation.bracket_plan_id
+            or candidate.bracket_plan_sha256
+            != observation.bracket_plan_sha256
+            or candidate.bracket_evidence_root_id
+            != observation.bracket_evidence_root_id
         ):
             return result, ("calibration_ledger_off_ledger_artifact",)
+    has_session_candidates = any(
+        candidate.bracket_session_id is not None for candidate in candidates
+    )
+    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
+    if has_session_candidates:
+        if bracket_binding is None:
+            return result, ("calibration_bracket_binding_missing",)
+        bound_observations = validate_calibration_bracket_binding(
+            bracket_binding,
+            ledger_snapshot,
+            window_id=bracket_window_id,
+            plan_id=bracket_plan_id,
+            plan_sha256=bracket_plan_sha256,
+            evidence_root_id=bracket_evidence_root_id,
+        )
+        if bound_observations is None:
+            return result, ("calibration_bracket_binding_invalid",)
+        result["bracket_binding"] = {
+            "schema_version": BRACKET_BINDING_SCHEMA,
+            "binding_digest": bracket_binding["binding_digest"],
+            "session_id": bracket_binding["session_id"],
+            "window_id": bracket_binding["window_id"],
+            "plan_id": bracket_binding["plan_id"],
+            "plan_sha256": bracket_binding["plan_sha256"],
+            "evidence_root_id": bracket_binding["evidence_root_id"],
+        }
     # v2 remains an authenticated validation/reduction artifact, but only the
     # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
     matching = [
         candidate
         for candidate in candidates
         if candidate.protocol_id == PROTOCOL_ID
         and all(
             candidate.bindings.get(field) == bindings.get(field)
             for field in V2_BINDING_FIELDS
         )
     ]
     matching_decimals: dict[int, Decimal] = {}
     for candidate in matching:
         candidate_decimal = _candidate_decimal(candidate)
         if candidate_decimal is None or candidate_decimal < 0:
             return result, ("instrument_calibration_invalid",)
         matching_decimals[id(candidate)] = candidate_decimal
     corpus_members = artifact["derivation_corpus"]["members"]
     observed_triggers = result["acceptance"]["prospective_rederivation"][
         "observed_triggers"
     ]
     if (
         protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
         or _current_estimator_code_sha256()
         != dict(prospective["estimator_code_sha256"])
     ):
         observed_triggers.append("protocol_or_estimator_byte_change")
     prior_ids = {
         observation["content_id"]
         for observation in artifact["prior_observation_set"]["observations"]
     }
     distinct_observations = {
         observation.content_id: observation
         for observation in ledger_snapshot.observations
         if observation.content_id is not None
     }
     distinct_live_observations = {
         content_id: observation
         for content_id, observation in distinct_observations.items()
         if not observation.is_historical_import
     }
     new_observations = [
         observation
         for content_id, observation in sorted(distinct_live_observations.items())
         if content_id not in prior_ids
     ]
     new_observations.extend(
         sorted(
             (
                 observation
                 for observation in ledger_snapshot.post_cutoff_live_observations(
                     cutoff["sequence"]
                 )
                 if observation.content_id is None
             ),
             key=lambda observation: (observation.sequence, observation.attempt_id),
         )
     )
     if any(
         observation.classification_disposition
         not in {"valid", "systematic-invalid", "ordinary-invalid"}
         for observation in new_observations
     ):
         return result, ("calibration_observation_unclassifiable",)
     valid_same_epoch = [
         observation
         for observation in distinct_observations.values()
         if observation.disposition == "valid"
         and dict(observation.identity_epoch) == dict(identity_epoch)
     ]
     if len(valid_same_epoch) >= 38:
         observed_triggers.append("corpus_doubles_from_19_to_38")
     corpus_values = [
         Decimal(member["b_fiducial_s"]) for member in corpus_members
     ]
     new_valid_values = [
         value
         for observation in new_observations
         if observation.disposition == "valid"
         and dict(observation.identity_epoch) == dict(identity_epoch)
         and (value := _decimal(observation.exact_bound_lexeme_s)) is not None
     ]
     if any(value < min(corpus_values) or value > max(corpus_values) for value in new_valid_values):
         observed_triggers.append(
             "new_valid_same_identity_capture_expands_observed_range"
         )
     if any(
         observation.disposition == "systematic-invalid"
         and dict(observation.identity_epoch) == dict(identity_epoch)
         for observation in new_observations
     ):
         observed_triggers.append(
             "new_systematic_failure_challenges_preflight_screen"
         )
     causal_pre = [
         candidate for candidate in matching if candidate.capture_wall_time_s <= window_start_s
     ]
     causal_post = [
         candidate for candidate in matching if candidate.capture_wall_time_s >= window_end_s
     ]
     fresh_pre = [
         candidate
         for candidate in causal_pre
         if window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
     ]
     fresh_post = [
         candidate
         for candidate in causal_post
         if candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
     ]
     if not fresh_pre or not fresh_post:
         reason = (
             "instrument_calibration_stale"
             if (causal_pre and not fresh_pre) or (causal_post and not fresh_post)
             else "instrument_calibration_bracket_missing"
         )
         return result, (reason,)
-    pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
-    post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
+    if bound_observations is None:
+        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
+        post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
+    else:
+        candidate_by_receipt = {
+            candidate.ledger_receipt_digest: candidate for candidate in matching
+        }
+        pre = candidate_by_receipt.get(bound_observations[0].receipt_digest)
+        post = candidate_by_receipt.get(bound_observations[1].receipt_digest)
+        if pre not in fresh_pre or post not in fresh_post:
+            return result, ("calibration_bracket_binding_invalid",)
     pre_decimal = matching_decimals[id(pre)]
     post_decimal = matching_decimals[id(post)]
     if (
         not pre_decimal.is_finite()
         or not post_decimal.is_finite()
         or pre_decimal < 0
         or post_decimal < 0
     ):
         return result, ("instrument_calibration_invalid",)
     if isinstance(pre.b_fiducial_s, float) and isinstance(
         post.b_fiducial_s, float
     ):
         # Old synthetic probes supplied only binary64 endpoints. Preserve their
         # source arithmetic without applying Decimal after a second rounding;
         # authenticated production candidates always use the exact branch.
         drift_decimal = Decimal(
             str(abs(pre.b_fiducial_s - post.b_fiducial_s))
         )
     else:
         drift_decimal = abs(pre_decimal - post_decimal)
     endpoint_max_decimal = max(pre_decimal, post_decimal)
     operatives = artifact["decimal_derivation"]["ratified_operatives"]
     screen = Decimal(operatives["bracket_screen_s"])
     preflight_screen = Decimal(operatives["preflight_level_screen_s"])
     maximum_drift = Decimal(operatives["maximum_budgetable_drift_s"])
     maximum_excess = Decimal(operatives["max_budgetable_excess_s"])
     result.update(
         {
             "pre": pre.descriptor(),
             "post": post.descriptor(),
             "endpoint_max_b_fiducial_s": float(endpoint_max_decimal),
             "drift_s": float(drift_decimal),
         }
     )
     result["acceptance"]["numeric_semantics"].update(
         {
             "pre_b_fiducial_binary64_s": float(pre_decimal),
             "pre_b_fiducial_decimal_s": str(pre_decimal),
             "post_b_fiducial_binary64_s": float(post_decimal),
             "post_b_fiducial_decimal_s": str(post_decimal),
             "observed_drift_decimal_s": str(drift_decimal),
         }
     )
     preflight_status = "passed" if pre_decimal <= preflight_screen else "failed"
     result["acceptance"]["preflight"] = {
         "status": preflight_status,
         "observed_pre_b_fiducial_s": str(pre_decimal),
         "level_screen_s": str(preflight_screen),
         "failure_class": (
             None if preflight_status == "passed" else "systematic_not_budgetable"
         ),
     }
     if pre_decimal > preflight_screen:
         observed_triggers.append(
             "new_systematic_failure_challenges_preflight_screen"
         )
         result["acceptance"]["drift"] = {
             "status": "not_evaluated_systematic_preflight_failure",
             "observed_s": str(drift_decimal),
             "screen_s": str(screen),
@@ -1202,156 +1450,169 @@ def evaluate_calibration_bracket(
             "new_valid_same_identity_capture_expands_observed_range",
             "new_systematic_failure_challenges_preflight_screen",
         }
     ]
     if stale_triggers:
         result["acceptance"]["freshness"].update(
             {
                 "status": "stale",
                 "reason": "prospective_rederivation_required",
                 "stale_triggers": stale_triggers,
             }
         )
         return result, ("calibration_acceptance_bound_stale",)
 
     excess = max(drift_decimal - screen, Decimal(0))
     drift_status = (
         "budget_exceeded"
         if drift_decimal > maximum_drift
         else "passed_budgeted"
         if drift_decimal > screen
         else "passed_screen"
     )
     result["acceptance"]["drift"] = {
         "status": drift_status,
         "observed_s": str(drift_decimal),
         "screen_s": str(screen),
         "excess_s": str(excess),
         "max_budgetable_excess_s": str(maximum_excess),
         "maximum_budgetable_drift_s": str(maximum_drift),
     }
     if drift_decimal > maximum_drift:
         return result, ("instrument_calibration_mismatch",)
 
     allowance = max(drift_decimal, screen)
     operative_bound = endpoint_max_decimal + allowance
     result.update(
         {
             "calibration_drift_allowance_s": float(allowance),
             "b_fiducial_s": float(operative_bound),
         }
     )
     result["acceptance"]["allowance"] = {
         "rule": "max(observed_drift_s,bracket_screen_s)",
         "value_s": str(allowance),
         "embedding_count": 1,
         "embedded_in": "b_fiducial_s",
         "endpoint_max_b_fiducial_s": str(endpoint_max_decimal),
         "operative_b_fiducial_decimal_s": str(operative_bound),
         "operative_b_fiducial_binary64_s": float(operative_bound),
     }
     result["status"] = "passed"
     return result, ()
 
 
 def calibration_bracket_for_bundles(
     runs_root: Path,
     bundle_paths: Sequence[Path],
     policy: CalibrationBracketingPolicy,
     *,
     ledger_snapshot: CalibrationLedgerSnapshot | None = None,
+    bracket_binding: Mapping[str, Any] | None = None,
+    bracket_window_id: str | None = None,
+    bracket_plan_id: str | None = None,
+    bracket_plan_sha256: str | None = None,
+    bracket_evidence_root_id: str | None = None,
     _allow_unissued_fixture: bool = False,
 ) -> tuple[dict[str, Any], tuple[str, ...]]:
     """Use the runs root only for the evaluated window's T1/endpoints."""
 
     if not bundle_paths:
         empty, _ = evaluate_calibration_bracket(
             (),
             window_start_s=0.0,
             window_end_s=0.0,
             bindings={},
             policy=policy,
             ledger_snapshot=ledger_snapshot,
             _allow_unissued_fixture=_allow_unissued_fixture,
         )
         return empty, ("instrument_calibration_bracket_missing",)
     windows = []
     bindings: list[Mapping[str, Any]] = []
     try:
         for path in bundle_paths:
             reader = BundleReader(path)
             window = reader.measured_window()
             metadata = reader.metadata()
             calibration = metadata.get("instrument_calibration")
             binding = calibration.get("bindings") if isinstance(calibration, Mapping) else None
             if window is None or not isinstance(binding, Mapping):
                 raise ValueError("member omits calibration binding evidence")
             windows.append(window)
             bindings.append(binding)
     except (BundleReadError, OSError, TypeError, ValueError):
         empty, _ = evaluate_calibration_bracket(
             (),
             window_start_s=0.0,
             window_end_s=0.0,
             bindings={},
             policy=policy,
             ledger_snapshot=ledger_snapshot,
             _allow_unissued_fixture=_allow_unissued_fixture,
         )
         return empty, ("instrument_calibration_bracket_missing",)
     expected = bindings[0]
     if any(
         any(binding.get(field) != expected.get(field) for field in V2_BINDING_FIELDS)
         for binding in bindings[1:]
     ):
         empty, _ = evaluate_calibration_bracket(
             (),
             window_start_s=min(window.start_s for window in windows),
             window_end_s=max(window.end_s for window in windows),
             bindings=expected,
             policy=policy,
             ledger_snapshot=ledger_snapshot,
             _allow_unissued_fixture=_allow_unissued_fixture,
         )
         return empty, ("instrument_calibration_mismatch",)
     if ledger_snapshot is None:
         candidates: tuple[CalibrationCandidate, ...] = ()
     else:
         candidates = discover_calibration_candidates(ledger_snapshot)
         registered_valid = sum(
             observation.disposition == "valid"
             and not observation.is_historical_import
             for observation in ledger_snapshot.observations
         )
         if ledger_snapshot.valid and len(candidates) != registered_valid:
             empty, _ = evaluate_calibration_bracket(
                 (),
                 window_start_s=min(window.start_s for window in windows),
                 window_end_s=max(window.end_s for window in windows),
                 bindings=expected,
                 policy=policy,
                 ledger_snapshot=ledger_snapshot,
                 _allow_unissued_fixture=_allow_unissued_fixture,
             )
             return empty, ("calibration_ledger_custody_invalid",)
     return evaluate_calibration_bracket(
         candidates,
         window_start_s=min(window.start_s for window in windows),
         window_end_s=max(window.end_s for window in windows),
         bindings=expected,
         policy=policy,
         ledger_snapshot=ledger_snapshot,
+        bracket_binding=bracket_binding,
+        bracket_window_id=bracket_window_id,
+        bracket_plan_id=bracket_plan_id,
+        bracket_plan_sha256=bracket_plan_sha256,
+        bracket_evidence_root_id=bracket_evidence_root_id,
         _allow_unissued_fixture=_allow_unissued_fixture,
     )
 
 
 __all__ = [
     "ACCEPTANCE_BOUND_SCHEMA",
     "ACCEPTANCE_EVALUATION_SCHEMA",
+    "BRACKET_BINDING_SCHEMA",
     "BRACKET_SCHEMA",
     "CalibrationCandidate",
+    "build_calibration_bracket_binding",
     "calibration_bracket_for_bundles",
     "discover_calibration_candidates",
     "evaluate_calibration_bracket",
     "load_calibration_acceptance_bound",
     "load_calibration_candidate",
+    "validate_calibration_bracket_binding",
 ]
1:"""Claim-time pre/post powermetrics fiducial calibration bracketing.
3:The bracket carries a nonparametric 95/95 calibration-distribution bound into
41:BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
42:BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
69:    "bracket_screen_s": "0.010818",
91:    bracket_session_id: str | None = None
92:    bracket_slot: str | None = None
93:    bracket_window_id: str | None = None
94:    bracket_plan_id: str | None = None
95:    bracket_plan_sha256: str | None = None
96:    bracket_evidence_root_id: str | None = None
99:        bound = _candidate_decimal(self)
113:            "bracket_session_id": self.bracket_session_id,
114:            "bracket_slot": self.bracket_slot,
115:            "bracket_window_id": self.bracket_window_id,
116:            "bracket_plan_id": self.bracket_plan_id,
117:            "bracket_plan_sha256": self.bracket_plan_sha256,
118:            "bracket_evidence_root_id": self.bracket_evidence_root_id,
143:def _candidate_decimal(candidate: CalibrationCandidate) -> Decimal | None:
144:    value = candidate.b_fiducial_s
157:        # candidates carry strings from authenticated evidence bytes instead.
186:    backfill = value.get("backfill_candidate")
201:            and backfill.get("status") == "unratified_candidate_only"
347:            or backfill.get("candidate_inventory") != disposition_counts
411:        or not isinstance(rounding.get("operative_bracket_screen"), Mapping)
412:        or rounding["operative_bracket_screen"].get("quantum_s") != "0.000001"
413:        or rounding["operative_bracket_screen"].get("value_s")
414:        != _D102_OPERATIVE_VALUES["bracket_screen_s"]
422:        != "max(observed_drift_s,bracket_screen_s)"
428:    screen = Decimal(_D102_OPERATIVE_VALUES["bracket_screen_s"])
512:    "session_id",
533:def build_calibration_bracket_binding(
536:    session_id: str,
542:    """Bind one frozen window to its exact finalized session endpoints."""
545:        raise ValueError("bracket binding requires a valid pinned ledger snapshot")
546:    session = ledger_snapshot.bracket_session_by_id.get(session_id)
549:        session is None
550:        or session.state != "finalized"
552:            session.window_id,
553:            session.plan_id,
554:            session.plan_sha256,
555:            session.evidence_root_id,
559:        raise ValueError("bracket session does not match the frozen window identity")
560:    pre = session.finalized_slots.get("pre")
561:    post = session.finalized_slots.get("post")
572:        raise ValueError("bracket session endpoints are not valid at the terminal head")
576:        "session_id": session.session_id,
577:        "window_id": session.window_id,
578:        "plan_id": session.plan_id,
579:        "plan_sha256": session.plan_sha256,
580:        "evidence_root_id": session.evidence_root_id,
581:        "capability_receipt_digest": session.capability_receipt_digest,
600:def validate_calibration_bracket_binding(
632:    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
634:        session is None
635:        or session.state != "finalized"
636:        or binding.get("window_id") != session.window_id
637:        or binding.get("plan_id") != session.plan_id
638:        or binding.get("plan_sha256") != session.plan_sha256
639:        or binding.get("evidence_root_id") != session.evidence_root_id
641:        != session.capability_receipt_digest
660:        observation = session.finalized_slots.get(role)
702:    # unmatchable as bracket candidates).
725:def load_calibration_candidate(
851:def _candidate_from_observation(
859:    candidate = load_calibration_candidate(
863:    if candidate is None:
865:    bound = _candidate_decimal(candidate)
872:        candidate.manifest_sha256
874:        or candidate.evidence_sha256
881:        or candidate.capture_wall_time_s != receipt_capture
883:            candidate.bindings.get(field) != observation.t1_bindings.get(field)
887:            candidate.bindings.get(field) != observation.identity_epoch.get(field)
893:        candidate,
898:        bracket_session_id=observation.bracket_session_id,
899:        bracket_slot=observation.bracket_slot,
900:        bracket_window_id=observation.bracket_window_id,
901:        bracket_plan_id=observation.bracket_plan_id,
902:        bracket_plan_sha256=observation.bracket_plan_sha256,
903:        bracket_evidence_root_id=observation.bracket_evidence_root_id,
907:def discover_calibration_candidates(
920:        and not ledger_snapshot.is_governed_open_bracket_extension
923:    candidates: list[CalibrationCandidate] = []
927:        candidate = _candidate_from_observation(observation)
928:        if candidate is None:
930:        candidates.append(candidate)
931:    return tuple(candidates)
983:def evaluate_calibration_bracket(
984:    candidates: Sequence[CalibrationCandidate],
992:    bracket_binding: Mapping[str, Any] | None = None,
993:    bracket_window_id: str | None = None,
994:    bracket_plan_id: str | None = None,
995:    bracket_plan_sha256: str | None = None,
996:    bracket_evidence_root_id: str | None = None,
999:    """Select a causal bracket and apply the provenance-bound D-079 budget."""
1004:            "require_bracket": policy.require_bracket,
1005:            "calibration_bracket_max_drift_s": (
1006:                policy.calibration_bracket_max_drift_s
1018:        "bracket_binding": None,
1019:        "status": "not_required" if not policy.require_bracket else "failed",
1021:    if not policy.require_bracket:
1028:        return result, ("instrument_calibration_bracket_missing",)
1104:            "calibration_bracket_max_drift_s_role": (
1108:            "operative_bracket_screen_decimal_s": (
1110:                    "bracket_screen_s"
1152:            "candidate_set_boundary": (
1189:            candidate.attempt_id,
1190:            candidate.content_id,
1191:            candidate.ledger_receipt_digest,
1193:        for candidate in candidates
1197:    # favorable subset while still passing per-candidate membership checks.
1198:    if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
1200:    for candidate in candidates:
1202:            observations_by_attempt.get(candidate.attempt_id)
1203:            if isinstance(candidate.attempt_id, str)
1209:            or candidate.content_id != observation.content_id
1210:            or candidate.ledger_receipt_digest != observation.receipt_digest
1211:            or candidate.manifest_sha256
1213:            or candidate.evidence_sha256
1215:            or candidate.bracket_session_id != observation.bracket_session_id
1216:            or candidate.bracket_slot != observation.bracket_slot
1217:            or candidate.bracket_window_id != observation.bracket_window_id
1218:            or candidate.bracket_plan_id != observation.bracket_plan_id
1219:            or candidate.bracket_plan_sha256
1220:            != observation.bracket_plan_sha256
1221:            or candidate.bracket_evidence_root_id
1222:            != observation.bracket_evidence_root_id
1225:    has_session_candidates = any(
1226:        candidate.bracket_session_id is not None for candidate in candidates
1229:    if has_session_candidates:
1230:        if bracket_binding is None:
1231:            return result, ("calibration_bracket_binding_missing",)
1232:        bound_observations = validate_calibration_bracket_binding(
1233:            bracket_binding,
1235:            window_id=bracket_window_id,
1236:            plan_id=bracket_plan_id,
1237:            plan_sha256=bracket_plan_sha256,
1238:            evidence_root_id=bracket_evidence_root_id,
1241:            return result, ("calibration_bracket_binding_invalid",)
1242:        result["bracket_binding"] = {
1244:            "binding_digest": bracket_binding["binding_digest"],
1245:            "session_id": bracket_binding["session_id"],
1246:            "window_id": bracket_binding["window_id"],
1247:            "plan_id": bracket_binding["plan_id"],
1248:            "plan_sha256": bracket_binding["plan_sha256"],
1249:            "evidence_root_id": bracket_binding["evidence_root_id"],
1254:        candidate
1255:        for candidate in candidates
1256:        if candidate.protocol_id == PROTOCOL_ID
1258:            candidate.bindings.get(field) == bindings.get(field)
1263:    for candidate in matching:
1264:        candidate_decimal = _candidate_decimal(candidate)
1265:        if candidate_decimal is None or candidate_decimal < 0:
1267:        matching_decimals[id(candidate)] = candidate_decimal
1301:                for observation in ledger_snapshot.post_cutoff_live_observations(
1346:        candidate for candidate in matching if candidate.capture_wall_time_s <= window_start_s
1349:        candidate for candidate in matching if candidate.capture_wall_time_s >= window_end_s
1352:        candidate
1353:        for candidate in causal_pre
1354:        if window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
1357:        candidate
1358:        for candidate in causal_post
1359:        if candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
1365:            else "instrument_calibration_bracket_missing"
1369:        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
1370:        post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
1372:        candidate_by_receipt = {
1373:            candidate.ledger_receipt_digest: candidate for candidate in matching
1375:        pre = candidate_by_receipt.get(bound_observations[0].receipt_digest)
1376:        post = candidate_by_receipt.get(bound_observations[1].receipt_digest)
1378:            return result, ("calibration_bracket_binding_invalid",)
1393:        # authenticated production candidates always use the exact branch.
1401:    screen = Decimal(operatives["bracket_screen_s"])
1492:        "rule": "max(observed_drift_s,bracket_screen_s)",
1504:def calibration_bracket_for_bundles(
1510:    bracket_binding: Mapping[str, Any] | None = None,
1511:    bracket_window_id: str | None = None,
1512:    bracket_plan_id: str | None = None,
1513:    bracket_plan_sha256: str | None = None,
1514:    bracket_evidence_root_id: str | None = None,
1520:        empty, _ = evaluate_calibration_bracket(
1529:        return empty, ("instrument_calibration_bracket_missing",)
1544:        empty, _ = evaluate_calibration_bracket(
1553:        return empty, ("instrument_calibration_bracket_missing",)
1559:        empty, _ = evaluate_calibration_bracket(
1570:        candidates: tuple[CalibrationCandidate, ...] = ()
1572:        candidates = discover_calibration_candidates(ledger_snapshot)
1578:        if ledger_snapshot.valid and len(candidates) != registered_valid:
1579:            empty, _ = evaluate_calibration_bracket(
1589:    return evaluate_calibration_bracket(
1590:        candidates,
1596:        bracket_binding=bracket_binding,
1597:        bracket_window_id=bracket_window_id,
1598:        bracket_plan_id=bracket_plan_id,
1599:        bracket_plan_sha256=bracket_plan_sha256,
1600:        bracket_evidence_root_id=bracket_evidence_root_id,
1611:    "build_calibration_bracket_binding",
1612:    "calibration_bracket_for_bundles",
1613:    "discover_calibration_candidates",
1614:    "evaluate_calibration_bracket",
1616:    "load_calibration_candidate",
1617:    "validate_calibration_bracket_binding",

exec
/bin/zsh -lc "nl -ba joulewise/calibration_bracketing.py | sed -n '830,950p'; nl -ba joulewise/calibration_bracketing.py | sed -n '970,1410p'; rg -n \"calibration_bracket_for_bundles\\(|evaluate_calibration_bracket\\(|bracket_binding|bracket_window_id\" --glob '*.py'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
   830	    if (
   831	        stored_decimal is not None
   832	        and float(stored_decimal) == float(effective_bound)
   833	    ):
   834	        effective_bound_lexeme = stored_lexeme
   835	    else:
   836	        # A physical re-fit can widen beyond the stored scalar. Its returned
   837	        # representation becomes the re-derivation source lexeme; no later
   838	        # acceptance comparison converts that value through binary64 again.
   839	        effective_bound_lexeme = str(float(effective_bound))
   840	    return CalibrationCandidate(
   841	        relative_path=relative,
   842	        manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
   843	        evidence_sha256=hashlib.sha256(evidence_raw).hexdigest(),
   844	        protocol_id=str(protocol_id),
   845	        capture_wall_time_s=float(capture),
   846	        b_fiducial_s=effective_bound_lexeme,
   847	        bindings=dict(bindings),
   848	    )
   849	
   850	
   851	def _candidate_from_observation(
   852	    observation: LedgerObservation,
   853	) -> CalibrationCandidate | None:
   854	    """Authenticate one valid ledger observation from its custody locator."""
   855	
   856	    if observation.disposition != "valid" or observation.content_id is None:
   857	        return None
   858	    custody = Path(observation.custody_locator)
   859	    candidate = load_calibration_candidate(
   860	        custody,
   861	        runs_root=custody.parent.parent,
   862	    )
   863	    if candidate is None:
   864	        return None
   865	    bound = _candidate_decimal(candidate)
   866	    receipt_bound = _decimal(observation.exact_bound_lexeme_s)
   867	    try:
   868	        receipt_capture = float(observation.capture_wall_time_s)
   869	    except (TypeError, ValueError):
   870	        return None
   871	    if (
   872	        candidate.manifest_sha256
   873	        != observation.artifact_sha256.get("manifest.json")
   874	        or candidate.evidence_sha256
   875	        != observation.artifact_sha256.get("instrument_evidence.json")
   876	        or content_id_from_artifact_hashes(observation.artifact_sha256)
   877	        != observation.content_id
   878	        or bound is None
   879	        or receipt_bound is None
   880	        or bound != receipt_bound
   881	        or candidate.capture_wall_time_s != receipt_capture
   882	        or any(
   883	            candidate.bindings.get(field) != observation.t1_bindings.get(field)
   884	            for field in V2_BINDING_FIELDS
   885	        )
   886	        or any(
   887	            candidate.bindings.get(field) != observation.identity_epoch.get(field)
   888	            for field in ACCEPTANCE_IDENTITY_FIELDS
   889	        )
   890	    ):
   891	        return None
   892	    return replace(
   893	        candidate,
   894	        relative_path=observation.custody_locator,
   895	        attempt_id=observation.attempt_id,
   896	        content_id=observation.content_id,
   897	        ledger_receipt_digest=observation.receipt_digest,
   898	        bracket_session_id=observation.bracket_session_id,
   899	        bracket_slot=observation.bracket_slot,
   900	        bracket_window_id=observation.bracket_window_id,
   901	        bracket_plan_id=observation.bracket_plan_id,
   902	        bracket_plan_sha256=observation.bracket_plan_sha256,
   903	        bracket_evidence_root_id=observation.bracket_evidence_root_id,
   904	    )
   905	
   906	
   907	def discover_calibration_candidates(
   908	    ledger_snapshot: CalibrationLedgerSnapshot,
   909	) -> tuple[CalibrationCandidate, ...]:
   910	    """Enumerate valid endpoints from the sole ledger authority.
   911	
   912	    The mechanism closes workflow omission, unregistered evidence, and
   913	    rollback/stale-head consumption; it does not defend against a malicious
   914	    trusted writer or a rewrite of both Git and full ledger history.
   915	    """
   916	
   917	    if (
   918	        not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
   919	        or not ledger_snapshot.valid
   920	        and not ledger_snapshot.is_governed_open_bracket_extension
   921	    ):
   922	        return ()
   923	    candidates: list[CalibrationCandidate] = []
   924	    for observation in ledger_snapshot.observations:
   925	        if observation.disposition != "valid" or observation.is_historical_import:
   926	            continue
   927	        candidate = _candidate_from_observation(observation)
   928	        if candidate is None:
   929	            return ()
   930	        candidates.append(candidate)
   931	    return tuple(candidates)
   932	
   933	
   934	def _prior_set_matches_import_cutoff_prefix(
   935	    artifact: Mapping[str, Any],
   936	    ledger_snapshot: CalibrationLedgerSnapshot,
   937	) -> bool:
   938	    """Bind issuance prior-set data to the import-marked cutoff prefix."""
   939	
   940	    cutoff = artifact["ledger_cutoff"]
   941	    prefix = tuple(
   942	        observation
   943	        for observation in ledger_snapshot.observations
   944	        if observation.sequence <= cutoff["sequence"]
   945	    )
   946	    # The checked-in schema fixture predates issuance and deliberately has a
   947	    # genesis cutoff. Production issuance, or any fixture containing imported
   948	    # prefix rows, must satisfy the exact marker-bound comparison below.
   949	    if not prefix and artifact.get("artifact_role") == "schema_fixture_unissued":
   950	        return True
   970	        if observation.content_id is None or len(epoch_ids) != 1:
   971	            return False
   972	        observed.add(
   973	            (
   974	                observation.attempt_id,
   975	                observation.content_id,
   976	                observation.classification_disposition,
   977	                epoch_ids[0],
   978	            )
   979	        )
   980	    return observed == expected and len(observed) == len(prefix)
   981	
   982	
   983	def evaluate_calibration_bracket(
   984	    candidates: Sequence[CalibrationCandidate],
   985	    *,
   986	    window_start_s: float,
   987	    window_end_s: float,
   988	    bindings: Mapping[str, Any],
   989	    policy: CalibrationBracketingPolicy,
   990	    acceptance_bound: Mapping[str, Any] | None = None,
   991	    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
   992	    bracket_binding: Mapping[str, Any] | None = None,
   993	    bracket_window_id: str | None = None,
   994	    bracket_plan_id: str | None = None,
   995	    bracket_plan_sha256: str | None = None,
   996	    bracket_evidence_root_id: str | None = None,
   997	    _allow_unissued_fixture: bool = False,
   998	) -> tuple[dict[str, Any], tuple[str, ...]]:
   999	    """Select a causal bracket and apply the provenance-bound D-079 budget."""
  1000	
  1001	    result: dict[str, Any] = {
  1002	        "schema_version": BRACKET_SCHEMA,
  1003	        "policy": {
  1004	            "require_bracket": policy.require_bracket,
  1005	            "calibration_bracket_max_drift_s": (
  1006	                policy.calibration_bracket_max_drift_s
  1007	            ),
  1008	        },
  1009	        "window_start_s": window_start_s,
  1010	        "window_end_s": window_end_s,
  1011	        "pre": None,
  1012	        "post": None,
  1013	        "endpoint_max_b_fiducial_s": None,
  1014	        "calibration_drift_allowance_s": None,
  1015	        "b_fiducial_s": None,
  1016	        "drift_s": None,
  1017	        "acceptance": None,
  1018	        "bracket_binding": None,
  1019	        "status": "not_required" if not policy.require_bracket else "failed",
  1020	    }
  1021	    if not policy.require_bracket:
  1022	        return result, ()
  1023	    if (
  1024	        not math.isfinite(window_start_s)
  1025	        or not math.isfinite(window_end_s)
  1026	        or window_start_s >= window_end_s
  1027	    ):
  1028	        return result, ("instrument_calibration_bracket_missing",)
  1029	
  1030	    using_default_bound = acceptance_bound is None
  1031	    artifact = (
  1032	        load_calibration_acceptance_bound()
  1033	        if using_default_bound
  1034	        else _authenticated_explicit_acceptance_bound(acceptance_bound)
  1035	    )
  1036	    if artifact is None:
  1037	        result["acceptance"] = {
  1038	            "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
  1039	            "artifact": None,
  1040	            "freshness": {
  1041	                "status": "stale",
  1042	                "reason": "acceptance_artifact_missing_or_invalid",
  1043	            },
  1044	        }
  1045	        return result, ("calibration_acceptance_bound_stale",)
  1046	    artifact_role = artifact["artifact_role"]
  1047	    artifact_sha256 = _acceptance_artifact_sha256(artifact)
  1048	    if artifact_role == "schema_fixture_unissued" and not _allow_unissued_fixture:
  1049	        result["acceptance"] = {
  1050	            "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
  1051	            "artifact": {
  1052	                "acceptance_id": artifact["acceptance_id"],
  1053	                "artifact_sha256": artifact_sha256,
  1054	                "authentication": "checked_in_genesis_fixture_byte_sha256_pin",
  1055	                "artifact_role": artifact_role,
  1056	                "claim_eligible": False,
  1057	            },
  1058	            "freshness": {
  1059	                "status": "stale",
  1060	                "reason": "acceptance_artifact_unissued_fixture",
  1061	            },
  1062	        }
  1063	        return result, ("calibration_acceptance_bound_stale",)
  1064	    cutoff = artifact["ledger_cutoff"]
  1065	    result["acceptance"] = {
  1066	        "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
  1067	        "artifact": {
  1068	            "acceptance_id": artifact["acceptance_id"],
  1069	            "artifact_sha256": artifact_sha256,
  1070	            "authentication": (
  1071	                "checked_in_issued_artifact_byte_sha256_pin"
  1072	                if artifact_role == "issued"
  1073	                else "checked_in_genesis_fixture_byte_sha256_pin"
  1074	            ),
  1075	            "artifact_role": artifact_role,
  1076	            "claim_eligible": False,
  1077	        },
  1078	        "freshness": {
  1079	            "status": "stale",
  1080	            "reason": "acceptance_artifact_ledger_authentication_pending",
  1081	        },
  1082	    }
  1083	    if ledger_snapshot is None:
  1084	        return result, ("calibration_ledger_snapshot_required",)
  1085	    if ledger_snapshot.refusal_reasons:
  1086	        return result, tuple(ledger_snapshot.refusal_reasons)
  1087	    if (
  1088	        ledger_snapshot.baseline_sequence != cutoff["sequence"]
  1089	        or ledger_snapshot.baseline_digest != cutoff["head_digest"]
  1090	        or ledger_snapshot.ledger_schema != cutoff["ledger_schema"]
  1091	        or artifact_role == "issued"
  1092	        and (
  1093	            ledger_snapshot.head_sequence <= 0
  1094	            or ledger_snapshot.head_digest == "0" * 64
  1095	        )
  1096	    ):
  1097	        return result, ("calibration_ledger_baseline_missing",)
  1098	    if not _prior_set_matches_import_cutoff_prefix(artifact, ledger_snapshot):
  1099	        return result, ("calibration_ledger_baseline_missing",)
  1100	    identity_epoch = artifact["identity_epoch"]
  1101	    prospective = artifact["prospective_rederivation"]
  1102	    result["policy"].update(
  1103	        {
  1104	            "calibration_bracket_max_drift_s_role": (
  1105	                "legacy_obsolete_not_an_acceptance_comparator"
  1106	            ),
  1107	            "acceptance_bound_id": artifact["acceptance_id"],
  1108	            "operative_bracket_screen_decimal_s": (
  1109	                artifact["decimal_derivation"]["ratified_operatives"][
  1110	                    "bracket_screen_s"
  1111	                ]
  1112	            ),
  1113	        }
  1114	    )
  1115	    observed_identity = {
  1116	        field: bindings.get(field) for field in ACCEPTANCE_IDENTITY_FIELDS
  1117	    }
  1118	    stale_fields = [
  1119	        field
  1120	        for field in ACCEPTANCE_IDENTITY_FIELDS
  1121	        if observed_identity.get(field) != identity_epoch.get(field)
  1122	    ]
  1123	    freshness_status = "stale" if stale_fields else "fresh"
  1124	    result["acceptance"] = {
  1125	        "schema_version": ACCEPTANCE_EVALUATION_SCHEMA,
  1126	        "artifact": {
  1127	            "acceptance_id": artifact["acceptance_id"],
  1128	            "artifact_sha256": artifact_sha256,
  1129	            "authentication": (
  1130	                "checked_in_issued_artifact_byte_sha256_pin"
  1131	                if artifact_role == "issued"
  1132	                else "checked_in_genesis_fixture_byte_sha256_pin"
  1133	            ),
  1134	            "artifact_role": artifact_role,
  1135	            "claim_eligible": artifact_role == "issued",
  1136	            "derivation_sha256": artifact["derivation_sha256"],
  1137	        },
  1138	        "freshness": {
  1139	            "status": freshness_status,
  1140	            "basis": "exact_identity_epoch",
  1141	            "expected_identity_epoch": dict(identity_epoch),
  1142	            "observed_identity_epoch": observed_identity,
  1143	            "trigger_guard_protocol_sha256": prospective["protocol_sha256"],
  1144	            "trigger_guard_estimator_code_sha256": dict(
  1145	                prospective["estimator_code_sha256"]
  1146	            ),
  1147	            "stale_fields": stale_fields,
  1148	            "calendar_expiry": None,
  1149	        },
  1150	        "prospective_rederivation": {
  1151	            "observation_rule": prospective["trigger_observation_rule"],
  1152	            "candidate_set_boundary": (
  1153	                "authenticated_calibration_ledger_snapshot_only"
  1154	            ),
  1155	            "global_runs_root_scan": False,
  1156	            "mandatory_triggers": list(prospective["triggers"]),
  1157	            "observed_triggers": [],
  1158	        },
  1159	        "numeric_semantics": {
  1160	            "comparisons": "decimal",
  1161	            "reducer_boundary": "binary64_recorded_below",
  1162	        },
  1163	        "ledger_snapshot": {
  1164	            "ledger_schema": ledger_snapshot.ledger_schema,
  1165	            "sequence": ledger_snapshot.head_sequence,
  1166	            "head_digest": ledger_snapshot.head_digest,
  1167	            "baseline_sequence": ledger_snapshot.baseline_sequence,
  1168	            "baseline_digest": ledger_snapshot.baseline_digest,
  1169	            "load_count": 1,
  1170	        },
  1171	        "preflight": None,
  1172	        "drift": None,
  1173	    }
  1174	    if stale_fields:
  1175	        return result, ("calibration_acceptance_bound_stale",)
  1176	    observations_by_attempt = ledger_snapshot.observation_by_attempt
  1177	    registered_valid = {
  1178	        (
  1179	            observation.attempt_id,
  1180	            observation.content_id,
  1181	            observation.receipt_digest,
  1182	        )
  1183	        for observation in ledger_snapshot.observations
  1184	        if observation.disposition == "valid"
  1185	        and not observation.is_historical_import
  1186	    }
  1187	    supplied_valid = {
  1188	        (
  1189	            candidate.attempt_id,
  1190	            candidate.content_id,
  1191	            candidate.ledger_receipt_digest,
  1192	        )
  1193	        for candidate in candidates
  1194	    }
  1195	    # Even the low-level evaluator requires the complete ledger enumeration.
  1196	    # This prevents a caller from narrowing the registered universe to a
  1197	    # favorable subset while still passing per-candidate membership checks.
  1198	    if supplied_valid != registered_valid or len(candidates) != len(supplied_valid):
  1199	        return result, ("calibration_ledger_off_ledger_artifact",)
  1200	    for candidate in candidates:
  1201	        observation = (
  1202	            observations_by_attempt.get(candidate.attempt_id)
  1203	            if isinstance(candidate.attempt_id, str)
  1204	            else None
  1205	        )
  1206	        if (
  1207	            observation is None
  1208	            or observation.disposition != "valid"
  1209	            or candidate.content_id != observation.content_id
  1210	            or candidate.ledger_receipt_digest != observation.receipt_digest
  1211	            or candidate.manifest_sha256
  1212	            != observation.artifact_sha256.get("manifest.json")
  1213	            or candidate.evidence_sha256
  1214	            != observation.artifact_sha256.get("instrument_evidence.json")
  1215	            or candidate.bracket_session_id != observation.bracket_session_id
  1216	            or candidate.bracket_slot != observation.bracket_slot
  1217	            or candidate.bracket_window_id != observation.bracket_window_id
  1218	            or candidate.bracket_plan_id != observation.bracket_plan_id
  1219	            or candidate.bracket_plan_sha256
  1220	            != observation.bracket_plan_sha256
  1221	            or candidate.bracket_evidence_root_id
  1222	            != observation.bracket_evidence_root_id
  1223	        ):
  1224	            return result, ("calibration_ledger_off_ledger_artifact",)
  1225	    has_session_candidates = any(
  1226	        candidate.bracket_session_id is not None for candidate in candidates
  1227	    )
  1228	    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
  1229	    if has_session_candidates:
  1230	        if bracket_binding is None:
  1231	            return result, ("calibration_bracket_binding_missing",)
  1232	        bound_observations = validate_calibration_bracket_binding(
  1233	            bracket_binding,
  1234	            ledger_snapshot,
  1235	            window_id=bracket_window_id,
  1236	            plan_id=bracket_plan_id,
  1237	            plan_sha256=bracket_plan_sha256,
  1238	            evidence_root_id=bracket_evidence_root_id,
  1239	        )
  1240	        if bound_observations is None:
  1241	            return result, ("calibration_bracket_binding_invalid",)
  1242	        result["bracket_binding"] = {
  1243	            "schema_version": BRACKET_BINDING_SCHEMA,
  1244	            "binding_digest": bracket_binding["binding_digest"],
  1245	            "session_id": bracket_binding["session_id"],
  1246	            "window_id": bracket_binding["window_id"],
  1247	            "plan_id": bracket_binding["plan_id"],
  1248	            "plan_sha256": bracket_binding["plan_sha256"],
  1249	            "evidence_root_id": bracket_binding["evidence_root_id"],
  1250	        }
  1251	    # v2 remains an authenticated validation/reduction artifact, but only the
  1252	    # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
  1253	    matching = [
  1254	        candidate
  1255	        for candidate in candidates
  1256	        if candidate.protocol_id == PROTOCOL_ID
  1257	        and all(
  1258	            candidate.bindings.get(field) == bindings.get(field)
  1259	            for field in V2_BINDING_FIELDS
  1260	        )
  1261	    ]
  1262	    matching_decimals: dict[int, Decimal] = {}
  1263	    for candidate in matching:
  1264	        candidate_decimal = _candidate_decimal(candidate)
  1265	        if candidate_decimal is None or candidate_decimal < 0:
  1266	            return result, ("instrument_calibration_invalid",)
  1267	        matching_decimals[id(candidate)] = candidate_decimal
  1268	    corpus_members = artifact["derivation_corpus"]["members"]
  1269	    observed_triggers = result["acceptance"]["prospective_rederivation"][
  1270	        "observed_triggers"
  1271	    ]
  1272	    if (
  1273	        protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256")
  1274	        or _current_estimator_code_sha256()
  1275	        != dict(prospective["estimator_code_sha256"])
  1276	    ):
  1277	        observed_triggers.append("protocol_or_estimator_byte_change")
  1278	    prior_ids = {
  1279	        observation["content_id"]
  1280	        for observation in artifact["prior_observation_set"]["observations"]
  1281	    }
  1282	    distinct_observations = {
  1283	        observation.content_id: observation
  1284	        for observation in ledger_snapshot.observations
  1285	        if observation.content_id is not None
  1286	    }
  1287	    distinct_live_observations = {
  1288	        content_id: observation
  1289	        for content_id, observation in distinct_observations.items()
  1290	        if not observation.is_historical_import
  1291	    }
  1292	    new_observations = [
  1293	        observation
  1294	        for content_id, observation in sorted(distinct_live_observations.items())
  1295	        if content_id not in prior_ids
  1296	    ]
  1297	    new_observations.extend(
  1298	        sorted(
  1299	            (
  1300	                observation
  1301	                for observation in ledger_snapshot.post_cutoff_live_observations(
  1302	                    cutoff["sequence"]
  1303	                )
  1304	                if observation.content_id is None
  1305	            ),
  1306	            key=lambda observation: (observation.sequence, observation.attempt_id),
  1307	        )
  1308	    )
  1309	    if any(
  1310	        observation.classification_disposition
  1311	        not in {"valid", "systematic-invalid", "ordinary-invalid"}
  1312	        for observation in new_observations
  1313	    ):
  1314	        return result, ("calibration_observation_unclassifiable",)
  1315	    valid_same_epoch = [
  1316	        observation
  1317	        for observation in distinct_observations.values()
  1318	        if observation.disposition == "valid"
  1319	        and dict(observation.identity_epoch) == dict(identity_epoch)
  1320	    ]
  1321	    if len(valid_same_epoch) >= 38:
  1322	        observed_triggers.append("corpus_doubles_from_19_to_38")
  1323	    corpus_values = [
  1324	        Decimal(member["b_fiducial_s"]) for member in corpus_members
  1325	    ]
  1326	    new_valid_values = [
  1327	        value
  1328	        for observation in new_observations
  1329	        if observation.disposition == "valid"
  1330	        and dict(observation.identity_epoch) == dict(identity_epoch)
  1331	        and (value := _decimal(observation.exact_bound_lexeme_s)) is not None
  1332	    ]
  1333	    if any(value < min(corpus_values) or value > max(corpus_values) for value in new_valid_values):
  1334	        observed_triggers.append(
  1335	            "new_valid_same_identity_capture_expands_observed_range"
  1336	        )
  1337	    if any(
  1338	        observation.disposition == "systematic-invalid"
  1339	        and dict(observation.identity_epoch) == dict(identity_epoch)
  1340	        for observation in new_observations
  1341	    ):
  1342	        observed_triggers.append(
  1343	            "new_systematic_failure_challenges_preflight_screen"
  1344	        )
  1345	    causal_pre = [
  1346	        candidate for candidate in matching if candidate.capture_wall_time_s <= window_start_s
  1347	    ]
  1348	    causal_post = [
  1349	        candidate for candidate in matching if candidate.capture_wall_time_s >= window_end_s
  1350	    ]
  1351	    fresh_pre = [
  1352	        candidate
  1353	        for candidate in causal_pre
  1354	        if window_end_s <= candidate.capture_wall_time_s + MAX_AGE_S
  1355	    ]
  1356	    fresh_post = [
  1357	        candidate
  1358	        for candidate in causal_post
  1359	        if candidate.capture_wall_time_s - window_start_s <= MAX_AGE_S
  1360	    ]
  1361	    if not fresh_pre or not fresh_post:
  1362	        reason = (
  1363	            "instrument_calibration_stale"
  1364	            if (causal_pre and not fresh_pre) or (causal_post and not fresh_post)
  1365	            else "instrument_calibration_bracket_missing"
  1366	        )
  1367	        return result, (reason,)
  1368	    if bound_observations is None:
  1369	        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
  1370	        post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
  1371	    else:
  1372	        candidate_by_receipt = {
  1373	            candidate.ledger_receipt_digest: candidate for candidate in matching
  1374	        }
  1375	        pre = candidate_by_receipt.get(bound_observations[0].receipt_digest)
  1376	        post = candidate_by_receipt.get(bound_observations[1].receipt_digest)
  1377	        if pre not in fresh_pre or post not in fresh_post:
  1378	            return result, ("calibration_bracket_binding_invalid",)
  1379	    pre_decimal = matching_decimals[id(pre)]
  1380	    post_decimal = matching_decimals[id(post)]
  1381	    if (
  1382	        not pre_decimal.is_finite()
  1383	        or not post_decimal.is_finite()
  1384	        or pre_decimal < 0
  1385	        or post_decimal < 0
  1386	    ):
  1387	        return result, ("instrument_calibration_invalid",)
  1388	    if isinstance(pre.b_fiducial_s, float) and isinstance(
  1389	        post.b_fiducial_s, float
  1390	    ):
  1391	        # Old synthetic probes supplied only binary64 endpoints. Preserve their
  1392	        # source arithmetic without applying Decimal after a second rounding;
  1393	        # authenticated production candidates always use the exact branch.
  1394	        drift_decimal = Decimal(
  1395	            str(abs(pre.b_fiducial_s - post.b_fiducial_s))
  1396	        )
  1397	    else:
  1398	        drift_decimal = abs(pre_decimal - post_decimal)
  1399	    endpoint_max_decimal = max(pre_decimal, post_decimal)
  1400	    operatives = artifact["decimal_derivation"]["ratified_operatives"]
  1401	    screen = Decimal(operatives["bracket_screen_s"])
  1402	    preflight_screen = Decimal(operatives["preflight_level_screen_s"])
  1403	    maximum_drift = Decimal(operatives["maximum_budgetable_drift_s"])
  1404	    maximum_excess = Decimal(operatives["max_budgetable_excess_s"])
  1405	    result.update(
  1406	        {
  1407	            "pre": pre.descriptor(),
  1408	            "post": post.descriptor(),
  1409	            "endpoint_max_b_fiducial_s": float(endpoint_max_decimal),
  1410	            "drift_s": float(drift_decimal),
joulewise/calibration_ledger.py:213:    bracket_window_id: str | None = None
joulewise/calibration_ledger.py:798:        bracket_window_id=(str(session["window_id"]) if session else None),
joulewise/calibration_bracketing.py:42:BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
joulewise/calibration_bracketing.py:93:    bracket_window_id: str | None = None
joulewise/calibration_bracketing.py:115:            "bracket_window_id": self.bracket_window_id,
joulewise/calibration_bracketing.py:533:def build_calibration_bracket_binding(
joulewise/calibration_bracketing.py:600:def validate_calibration_bracket_binding(
joulewise/calibration_bracketing.py:900:        bracket_window_id=observation.bracket_window_id,
joulewise/calibration_bracketing.py:983:def evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:992:    bracket_binding: Mapping[str, Any] | None = None,
joulewise/calibration_bracketing.py:993:    bracket_window_id: str | None = None,
joulewise/calibration_bracketing.py:1018:        "bracket_binding": None,
joulewise/calibration_bracketing.py:1217:            or candidate.bracket_window_id != observation.bracket_window_id
joulewise/calibration_bracketing.py:1230:        if bracket_binding is None:
joulewise/calibration_bracketing.py:1231:            return result, ("calibration_bracket_binding_missing",)
joulewise/calibration_bracketing.py:1232:        bound_observations = validate_calibration_bracket_binding(
joulewise/calibration_bracketing.py:1233:            bracket_binding,
joulewise/calibration_bracketing.py:1235:            window_id=bracket_window_id,
joulewise/calibration_bracketing.py:1241:            return result, ("calibration_bracket_binding_invalid",)
joulewise/calibration_bracketing.py:1242:        result["bracket_binding"] = {
joulewise/calibration_bracketing.py:1244:            "binding_digest": bracket_binding["binding_digest"],
joulewise/calibration_bracketing.py:1245:            "session_id": bracket_binding["session_id"],
joulewise/calibration_bracketing.py:1246:            "window_id": bracket_binding["window_id"],
joulewise/calibration_bracketing.py:1247:            "plan_id": bracket_binding["plan_id"],
joulewise/calibration_bracketing.py:1248:            "plan_sha256": bracket_binding["plan_sha256"],
joulewise/calibration_bracketing.py:1249:            "evidence_root_id": bracket_binding["evidence_root_id"],
joulewise/calibration_bracketing.py:1378:            return result, ("calibration_bracket_binding_invalid",)
joulewise/calibration_bracketing.py:1504:def calibration_bracket_for_bundles(
joulewise/calibration_bracketing.py:1510:    bracket_binding: Mapping[str, Any] | None = None,
joulewise/calibration_bracketing.py:1511:    bracket_window_id: str | None = None,
joulewise/calibration_bracketing.py:1520:        empty, _ = evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1544:        empty, _ = evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1559:        empty, _ = evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1579:            empty, _ = evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1589:    return evaluate_calibration_bracket(
joulewise/calibration_bracketing.py:1596:        bracket_binding=bracket_binding,
joulewise/calibration_bracketing.py:1597:        bracket_window_id=bracket_window_id,
joulewise/calibration_bracketing.py:1611:    "build_calibration_bracket_binding",
joulewise/calibration_bracketing.py:1617:    "validate_calibration_bracket_binding",
joulewise/whole_window.py:515:        bracket, bracket_reasons = calibration_bracket_for_bundles(
joulewise/whole_window.py:3489:                calibration_bracket_for_bundles(
tests/test_calibration_bracketing.py:26:    build_calibration_bracket_binding,
tests/test_calibration_bracketing.py:32:    validate_calibration_bracket_binding,
tests/test_calibration_bracketing.py:370:        return _evaluate_calibration_bracket(candidates, **kwargs)
tests/test_calibration_bracketing.py:373:def evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:415:            result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:464:            result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:496:            result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:514:            result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:536:            result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:566:            result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:586:            result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:704:                result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:816:            _result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:899:                bracket_window_id="window-alpha" if session_id else None,
tests/test_calibration_bracketing.py:935:                    bracket_window_id="window-alpha" if session_id else None,
tests/test_calibration_bracketing.py:983:        binding = build_calibration_bracket_binding(
tests/test_calibration_bracketing.py:995:        resolved = validate_calibration_bracket_binding(
tests/test_calibration_bracketing.py:1008:            result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1015:                bracket_binding=binding,
tests/test_calibration_bracketing.py:1016:                bracket_window_id="window-alpha",
tests/test_calibration_bracketing.py:1026:            result["bracket_binding"]["binding_digest"],
tests/test_calibration_bracketing.py:1038:            _result, reasons = _evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1047:        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
tests/test_calibration_bracketing.py:1063:            validate_calibration_bracket_binding(substituted, snapshot)
tests/test_calibration_bracketing.py:1076:            validate_calibration_bracket_binding(cross_window, snapshot)
tests/test_calibration_bracketing.py:1157:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1171:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1189:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1203:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1214:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1226:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1246:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1277:                result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1300:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1317:        zero, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1334:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1355:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1378:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1397:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1425:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1448:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1513:            result, reasons = calibration_bracket_for_bundles(
tests/test_calibration_bracketing.py:1586:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1772:        result, reasons = evaluate_calibration_bracket(
tests/test_calibration_bracketing.py:1798:            result, reasons = evaluate_calibration_bracket(
scripts/run_campaign.py:4307:        calibration_bracket, calibration_reasons = calibration_bracket_for_bundles(

exec
/bin/zsh -lc "nl -ba tests/test_calibration_bracketing.py | sed -n '960,1090p'; nl -ba joulewise/whole_window.py | sed -n '485,540p'; nl -ba scripts/run_campaign.py | sed -n '4280,4330p'; git diff --unified=80 -- scripts/validate_powermetrics_fiducial.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
   960	        )
   961	        receipt_digests = [
   962	            observations[0].receipt_digest,
   963	            observations[1].receipt_digest,
   964	            capability_digest,
   965	            by_slot["pre"].receipt_digest,
   966	            by_slot["post"].receipt_digest,
   967	        ]
   968	        snapshot = CalibrationLedgerSnapshot(
   969	            ledger_schema=LEDGER_SCHEMA,
   970	            ledger_path=Path("synthetic-session-ledger.jsonl"),
   971	            head_sequence=5,
   972	            head_digest=by_slot["post"].receipt_digest,
   973	            receipts=tuple(
   974	                MappingProxyType({"receipt_digest": digest})
   975	                for digest in receipt_digests
   976	            ),
   977	            observations=tuple(sorted(observations, key=lambda item: item.sequence)),
   978	            refusal_reasons=(),
   979	            bracket_sessions=(session,),
   980	            baseline_sequence=0,
   981	            baseline_digest=GENESIS_DIGEST,
   982	        )
   983	        binding = build_calibration_bracket_binding(
   984	            snapshot,
   985	            session_id="session-alpha",
   986	            window_id="window-alpha",
   987	            plan_id="plan-alpha",
   988	            plan_sha256="a" * 64,
   989	            evidence_root_id="evidence-alpha",
   990	        )
   991	        return snapshot, candidates, binding
   992	
   993	    def test_exact_session_binding_selects_reserved_pair_not_neighbors(self) -> None:
   994	        snapshot, candidates, binding = self._bound_session_fixture()
   995	        resolved = validate_calibration_bracket_binding(
   996	            binding,
   997	            snapshot,
   998	            window_id="window-alpha",
   999	            plan_id="plan-alpha",
  1000	            plan_sha256="a" * 64,
  1001	            evidence_root_id="evidence-alpha",
  1002	        )
  1003	        self.assertIsNotNone(resolved)
  1004	        with patch(
  1005	            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
  1006	            return_value=_unissued_acceptance_fixture(),
  1007	        ):
  1008	            result, reasons = _evaluate_calibration_bracket(
  1009	                candidates,
  1010	                window_start_s=100.0,
  1011	                window_end_s=110.0,
  1012	                bindings=self.bindings,
  1013	                policy=self.policy,
  1014	                ledger_snapshot=snapshot,
  1015	                bracket_binding=binding,
  1016	                bracket_window_id="window-alpha",
  1017	                bracket_plan_id="plan-alpha",
  1018	                bracket_plan_sha256="a" * 64,
  1019	                bracket_evidence_root_id="evidence-alpha",
  1020	                _allow_unissued_fixture=True,
  1021	            )
  1022	        self.assertEqual(reasons, ())
  1023	        self.assertEqual(result["pre"]["attempt_id"], "attempt-session-pre")
  1024	        self.assertEqual(result["post"]["attempt_id"], "attempt-session-post")
  1025	        self.assertEqual(
  1026	            result["bracket_binding"]["binding_digest"],
  1027	            binding["binding_digest"],
  1028	        )
  1029	
  1030	    def test_session_candidates_refuse_missing_neighbor_substituted_or_cross_window_binding(
  1031	        self,
  1032	    ) -> None:
  1033	        snapshot, candidates, binding = self._bound_session_fixture()
  1034	        with patch(
  1035	            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
  1036	            return_value=_unissued_acceptance_fixture(),
  1037	        ):
  1038	            _result, reasons = _evaluate_calibration_bracket(
  1039	                candidates,
  1040	                window_start_s=100.0,
  1041	                window_end_s=110.0,
  1042	                bindings=self.bindings,
  1043	                policy=self.policy,
  1044	                ledger_snapshot=snapshot,
  1045	                _allow_unissued_fixture=True,
  1046	            )
  1047	        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
  1048	
  1049	        substituted = json.loads(json.dumps(binding))
  1050	        substituted["endpoints"]["pre"] = {
  1051	            "attempt_id": candidates[0].attempt_id,
  1052	            "receipt_digest": candidates[0].ledger_receipt_digest,
  1053	            "content_digest": candidates[0].content_id,
  1054	        }
  1055	        substituted["binding_digest"] = _canonical_sha256(
  1056	            {
  1057	                key: value
  1058	                for key, value in substituted.items()
  1059	                if key != "binding_digest"
  1060	            }
  1061	        )
  1062	        self.assertIsNone(
  1063	            validate_calibration_bracket_binding(substituted, snapshot)
  1064	        )
  1065	
  1066	        cross_window = json.loads(json.dumps(binding))
  1067	        cross_window["window_id"] = "window-beta"
  1068	        cross_window["binding_digest"] = _canonical_sha256(
  1069	            {
  1070	                key: value
  1071	                for key, value in cross_window.items()
  1072	                if key != "binding_digest"
  1073	            }
  1074	        )
  1075	        self.assertIsNone(
  1076	            validate_calibration_bracket_binding(cross_window, snapshot)
  1077	        )
  1078	
  1079	    def test_open_and_aborted_session_observations_never_leak_as_candidates(self) -> None:
  1080	        snapshot, candidates, _binding = self._bound_session_fixture()
  1081	        session = snapshot.bracket_sessions[0]
  1082	        open_session = replace(
  1083	            session,
  1084	            state="open",
  1085	            finalized_slots=MappingProxyType({"pre": session.finalized_slots["pre"]}),
  1086	        )
  1087	        open_snapshot = replace(
  1088	            snapshot,
  1089	            observations=tuple(
  1090	                observation
   485	        self._preparation_identity = identity
   486	        reasons: set[str] = set()
   487	        if self.calibration_ledger_snapshot is None:
   488	            self._fail_global({"calibration_ledger_snapshot_required"})
   489	            return
   490	        if self.calibration_ledger_snapshot.refusal_reasons:
   491	            self._fail_global(
   492	                set(self.calibration_ledger_snapshot.refusal_reasons)
   493	            )
   494	            return
   495	        if (
   496	            not self.referenced_bundle_ids.issubset(bundle_paths)
   497	            or not bundle_paths
   498	        ):
   499	            self._fail_global(
   500	                {"whole_window_verdict_provenance_invalid"}
   501	            )
   502	            return
   503	
   504	        if self.consumption_semantics_id == MINTED_CONSUMPTION_SEMANTICS_ID:
   505	            for bundle_id, path in sorted(bundle_paths.items()):
   506	                stored_summary = _read_json_object(path / "summary_metrics.json")
   507	                if not isinstance(stored_summary, Mapping):
   508	                    reasons.add("whole_window_verdict_provenance_invalid")
   509	                else:
   510	                    self._summaries[bundle_id] = stored_summary
   511	            if reasons:
   512	                self._fail_global(reasons)
   513	            return
   514	
   515	        bracket, bracket_reasons = calibration_bracket_for_bundles(
   516	            self.runs_root,
   517	            [bundle_paths[bundle_id] for bundle_id in sorted(bundle_paths)],
   518	            policy.calibration_bracketing,
   519	            ledger_snapshot=self.calibration_ledger_snapshot,
   520	            _allow_unissued_fixture=self._allow_unissued_calibration_fixture,
   521	        )
   522	        self.calibration_bracket = bracket
   523	        reasons.update(bracket_reasons)
   524	        raw_bound = bracket.get("b_fiducial_s")
   525	        if (
   526	            isinstance(raw_bound, bool)
   527	            or not isinstance(raw_bound, int | float)
   528	            or not math.isfinite(float(raw_bound))
   529	            or float(raw_bound) < 0.0
   530	        ):
   531	            if not reasons:
   532	                reasons.add("instrument_calibration_invalid")
   533	            self._fail_global(reasons)
   534	            return
   535	        operative_bound = float(raw_bound)
   536	        self.operative_fiducial_bound_s = operative_bound
   537	
   538	        physics_cache: dict[str, float] = {}
   539	        pending: list[
   540	            tuple[
  4280	            end_idle_subtracted_j=family_values("end", 1),
  4281	            window_duration_s=duration_s,
  4282	            bound_freshness_observation=freshness_observation,
  4283	        )
  4284	    else:
  4285	        bracket = neg8_bracket_not_evaluated(
  4286	            extension.neg8_bracket,
  4287	            start_gross_j=(
  4288	                neg8_references["start"][0][0]
  4289	                if len(neg8_references["start"]) == 1
  4290	                else None
  4291	            ),
  4292	            end_gross_j=(
  4293	                neg8_references["end"][0][0]
  4294	                if len(neg8_references["end"]) == 1
  4295	                else None
  4296	            ),
  4297	        )
  4298	    conditions.update(bracket["conditions"])
  4299	    section["adapter_wattage_continuity"] = continuity
  4300	    section["neg8_bracket"] = bracket
  4301	    section["neg8_reference_scientific_config_sha256"] = (
  4302	        identities[0]
  4303	        if identities and not identity_invalid and len(set(identities)) == 1
  4304	        else None
  4305	    )
  4306	    if whole_window:
  4307	        calibration_bracket, calibration_reasons = calibration_bracket_for_bundles(
  4308	            runs_root
  4309	            if runs_root is not None
  4310	            else evaluations[0].bundle_path.parent
  4311	            if evaluations
  4312	            else Path("."),
  4313	            [evaluation.bundle_path for evaluation in evaluations],
  4314	            policy_binding.policy.calibration_bracketing,
  4315	            ledger_snapshot=calibration_ledger_snapshot,
  4316	        )
  4317	        section["instrument_calibration_bracket"] = calibration_bracket
  4318	        if extension.claim_bearing:
  4319	            conditions.update(calibration_reasons)
  4320	    section["conditions"] = sorted(conditions)
  4321	    return section
  4322	
  4323	
  4324	def _whole_window_member(
  4325	    source: WholeWindowMemberSource, waivers: WaiverMap
  4326	) -> MemberEvaluation:
  4327	    bundle_path = source.path
  4328	    """Strictly validate an existing bundle before whole-window admission."""
  4329	
  4330	    summary, _summary_problem = _load_json_object(
diff --git a/scripts/validate_powermetrics_fiducial.py b/scripts/validate_powermetrics_fiducial.py
index f7a5686..d34ac52 100644
--- a/scripts/validate_powermetrics_fiducial.py
+++ b/scripts/validate_powermetrics_fiducial.py
@@ -1,134 +1,144 @@
 #!/usr/bin/env python3
 """Lead-owned [QUIET-MAC] pulse-fiducial calibration run (D-078).
 
 The current claim-bearing protocol is frozen in
 configs/calibration/powermetrics_fiducial/protocol_v3.json and documented in
 docs/contracts/powermetrics_fiducial.md. Historical protocol files remain
 byte-frozen validation identities.
 
 - preallocated 4096x4096 FP16 MLX matmuls, mx.eval GPU fencing;
 - 3 warmup pulses, then k=59 pulses of 1.0 s each;
 - deterministic low-discrepancy spacing 1.5 + vanDerCorput_2(j) s
   (avoids 10 Hz phase lock);
 - >= 5 s baseline before and after the pulse train;
 - events pulse_command_on/off carry full paired ClockStamps;
 - primary rail gpu_power; CPU+GPU combined is corroboration only;
 - gates: plateau >= 10 W over baseline, robust SNR >= 10, all pulses
   detected, no spurious plateaus - otherwise the artifact is invalid.
 
 NEVER run this while another agent session is active on the machine
 ([QUIET-MAC] discipline); the run is refused without --allow-live.
 """
 
 from __future__ import annotations
 
 import argparse
 import atexit
 import hashlib
 import json
 import math
 import subprocess
 import sys
 import time
 import uuid
 from dataclasses import asdict, replace
 from decimal import Decimal
 from pathlib import Path
+from typing import Any, Mapping
 
 REPO_ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(REPO_ROOT))
 
 from joulewise.adapters.powermetrics import (  # noqa: E402
     POWER_METRICS,
     SAMPLERS,
     anchor_records_from_powermetrics,
     parse_powermetrics_records,
     samples_from_records,
 )
 from joulewise.clock import SystemClock  # noqa: E402
 from joulewise.calibration_ledger import (  # noqa: E402
+    BRACKET_SESSION_OPEN_EVENT,
+    BRACKET_SESSION_SCHEMA,
+    BRACKET_SESSION_SLOTS,
     DEFAULT_LEDGER_PATH,
+    DEFAULT_HEAD_PIN_PATH,
+    CalibrationLedgerError,
+    abort_bracket_session,
     append_pending_receipt,
     artifact_hashes as ledger_artifact_hashes,
     finalize_attempt_receipt,
+    finalize_bracket_session_slot,
     head_pin_for_receipt,
+    load_calibration_ledger_snapshot,
+    terminal_head_pin_for_session,
 )
 from joulewise.powermetrics_fiducial import (  # noqa: E402
     BASELINE_S,
     LEGACY_PROTOCOL_ID,
     PROTOCOL_ID,
     PROTOCOL_V2_ID,
     PROTOCOL_V2_PULSE_COUNT,
     RESIDUAL_REGION_METHOD,
     PULSE_COUNT,
     PULSE_DURATION_S,
     SAMPLING_INTERVAL_MS,
     CommandedPulse,
     TraceInterval,
     WARMUP_PULSE_COUNT,
     allocate_matmul_buffers,
     capture_wall_time_from_events,
     clock_stamp_half_width_s,
     detect_pulses,
     instrument_evidence,
     protocol_definition_matches,
     pulse_schedule,
     run_matmul_pulse,
     trim_trace_after_pulses,
     rederive_detection_from_artifacts,
 )
 from joulewise.uncertainty_evidence import (  # noqa: E402
     CLOCK_METHOD_V2,
     derive_powermetrics_clock_evidence_v2,
 )
 
 PROTOCOL_PATH = (
     REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v3.json"
 )
 PROTOCOL_V2_PATH = (
     REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v2.json"
 )
 ROLLOVER_GATE_TIMEOUT_REASON = "pulse_calibration_rollover_gate_timeout"
 PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")
 
 
 def sha256_path(path: Path) -> str:
     return hashlib.sha256(path.read_bytes()).hexdigest()
 
 
 def _sysctl_identity(name: str) -> str:
     """Read a reservation-time macOS identity before capture begins."""
 
     value = subprocess.run(
         ["/usr/sbin/sysctl", "-n", name],
         check=True,
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE,
         text=True,
     ).stdout.strip()
     if not value:
         raise RuntimeError(f"empty reservation identity: {name}")
     return value
 
 
 def verify_frozen_protocol(path: Path = PROTOCOL_PATH) -> bool:
     """Load and field-bind the frozen JSON to executable module constants."""
 
     try:
         payload = json.loads(path.read_text(encoding="utf-8"))
     except (OSError, UnicodeDecodeError, json.JSONDecodeError):
         return False
     return protocol_definition_matches(payload)
 
 
 def _terminate_powermetrics(process: subprocess.Popen) -> None:
     """Best-effort bounded termination for a calibration sampler."""
 
     process.terminate()
     try:
         process.communicate(timeout=10.0)
     except subprocess.TimeoutExpired:
         process.kill()
         process.communicate()
 
 
@@ -198,500 +208,726 @@ def rederive_artifact(source_dir: Path, output: Path) -> dict[str, object]:
         stored.get("protocol_id") not in {LEGACY_PROTOCOL_ID, PROTOCOL_V2_ID}
         or stored.get("pulse_count") != PROTOCOL_V2_PULSE_COUNT
     ):
         raise ValueError("re-derivation requires compatible 40-pulse v1/v2 evidence")
     raw_by_name: dict[str, bytes] = {}
     for relative in (
         "raw/powermetrics.plist",
         "events.jsonl",
         "instrument_evidence.json",
     ):
         expected = artifacts.get(relative)
         candidate = source_dir / relative
         try:
             raw = candidate.read_bytes()
         except OSError as exc:
             raise ValueError(f"source artifact missing: {relative}") from exc
         if (
             not isinstance(expected, str)
             or hashlib.sha256(raw).hexdigest() != expected
         ):
             raise ValueError(f"source artifact hash mismatch: {relative}")
         raw_by_name[relative] = raw
     stored_hashes = stored.get("artifact_sha256")
     if not isinstance(stored_hashes, dict):
         raise ValueError("source evidence omits primary artifact hashes")
     for relative in ("raw/powermetrics.plist", "events.jsonl"):
         if hashlib.sha256(raw_by_name[relative]).hexdigest() != stored_hashes.get(
             relative
         ):
             raise ValueError(f"source evidence hash mismatch: {relative}")
     fresh = rederive_detection_from_artifacts(
         raw_by_name["raw/powermetrics.plist"],
         raw_by_name["events.jsonl"],
         stored.get("clock_anchor"),
         protocol_id=str(stored.get("protocol_id")),
     )
     stored_bound = stored.get("b_fiducial_s")
     if (
         isinstance(stored_bound, bool)
         or not isinstance(stored_bound, int | float)
         or fresh.b_fiducial_s is None
     ):
         raise ValueError("source calibration bound is malformed")
     fresh = replace(
         fresh,
         b_fiducial_s=max(float(stored_bound), float(fresh.b_fiducial_s)),
     )
     bindings = dict(stored.get("bindings", {}))
     bindings.update(
         {
             "pulse_protocol_id": PROTOCOL_V2_ID,
             "estimator_revision": RESIDUAL_REGION_METHOD,
             "protocol_sha256": sha256_path(PROTOCOL_V2_PATH),
         }
     )
     validation_id = str(stored.get("validation_id") or source_dir.name) + "-v2"
     payload = instrument_evidence(
         fresh,
         bindings=bindings,
         validation_id=validation_id,
         artifact_sha256={
             relative: hashlib.sha256(raw_by_name[relative]).hexdigest()
             for relative in ("raw/powermetrics.plist", "events.jsonl")
         },
         capture_wall_time_s=capture_wall_time_from_events(
             raw_by_name["events.jsonl"]
         ),
         protocol_id=PROTOCOL_V2_ID,
         protocol_pulse_count=PROTOCOL_V2_PULSE_COUNT,
     )
     payload["clock_anchor"] = stored.get("clock_anchor")
     payload["clock_anchor_resolved"] = True
     output.parent.mkdir(parents=True, exist_ok=True)
     # Exclusive create: re-derivation must never clobber an existing evidence
     # artifact (same rule as the extraction and campaign-log outputs).
     with output.open("x", encoding="utf-8") as handle:
         handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
     return payload
 
 
-def main() -> int:
+def _validate_reserved_bracket_slot(
+    ledger_path: Path,
+    head_pin_path: Path,
+    *,
+    session_id: str,
+    slot: str,
+    attempt_id: str,
+    custody_locator: str,
+    identity_epoch: Mapping[str, Any],
+    t1_bindings: Mapping[str, Any],
+    require_committed_pin: bool = True,
+) -> None:
+    """Authenticate the exact predeclared slot before capture state exists."""
+
+    snapshot = load_calibration_ledger_snapshot(
+        ledger_path,
+        head_pin_path,
+        require_committed_pin=require_committed_pin,
+        verify_custody=True,
+    )
+    session = snapshot.bracket_session_by_id.get(session_id)
+    finalized_slots = set(session.finalized_slots) if session is not None else set()
+    expected_slot = (
+        "pre"
+        if not finalized_slots
+        else "post"
+        if finalized_slots == {"pre"}
+        else None
+    )
+    open_receipt = next(
+        (
+            receipt
+            for receipt in snapshot.receipts
+            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
+            and receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
+            and receipt.get("session_id") == session_id
+        ),
+        None,
+    )
+    reserved = (
+        open_receipt.get("slots", {}).get(slot)
+        if isinstance(open_receipt, Mapping)
+        and isinstance(open_receipt.get("slots"), Mapping)
+        else None
+    )
+    if (
+        not snapshot.is_governed_open_bracket_extension
+        or session is None
+        or session.state != "open"
+        or slot not in BRACKET_SESSION_SLOTS
+        or slot != expected_slot
+        or session.slot_attempt_ids.get(slot) != attempt_id
+        or not isinstance(reserved, Mapping)
+        or reserved.get("attempt_id") != attempt_id
+        or reserved.get("custody_locator") != custody_locator
+        or dict(reserved.get("identity_epoch", {})) != dict(identity_epoch)
+        or dict(reserved.get("t1_bindings", {})) != dict(t1_bindings)
+    ):
+        raise CalibrationLedgerError(
+            "capture does not match the exact reserved bracket session slot"
+        )
+
+
+class _CaptureLedgerLifecycle:
+    """Route one writer attempt through ordinary or bracket-session APIs."""
+
+    def __init__(
+        self,
+        *,
+        ledger_path: Path,
+        head_pin_path: Path,
+        attempt_id: str,
+        custody_locator: str,
+        identity_epoch: Mapping[str, Any],
+        t1_bindings: Mapping[str, Any],
+        session_id: str | None = None,
+        slot: str | None = None,
+        require_committed_pin: bool = True,
+    ) -> None:
+        if (session_id is None) != (slot is None):
+            raise CalibrationLedgerError(
+                "bracket session id and slot must be supplied together"
+            )
+        self.ledger_path = Path(ledger_path)
+        self.head_pin_path = Path(head_pin_path)
+        self.attempt_id = attempt_id
+        self.custody_locator = custody_locator
+        self.identity_epoch: Mapping[str, Any] = identity_epoch
+        self.t1_bindings: Mapping[str, Any] = t1_bindings
+        self.capture_wall_time_s: str | None = None
+        self.exact_bound_lexeme_s: str | None = None
+        self.session_id = session_id
+        self.slot = slot
+        self.require_committed_pin = require_committed_pin
+        self.begun = False
+        self.closed = False
+
+    @property
+    def is_bracket_session(self) -> bool:
+        return self.session_id is not None
+
+    def begin(self) -> None:
+        """Reserve ordinarily, or authenticate a previously reserved slot."""
+
+        if self.begun:
+            raise CalibrationLedgerError("capture ledger lifecycle already began")
+        if self.is_bracket_session:
+            assert self.session_id is not None and self.slot is not None
+            _validate_reserved_bracket_slot(
+                self.ledger_path,
+                self.head_pin_path,
+                session_id=self.session_id,
+                slot=self.slot,
+                attempt_id=self.attempt_id,
+                custody_locator=self.custody_locator,
+                identity_epoch=self.identity_epoch,
+                t1_bindings=self.t1_bindings,
+                require_committed_pin=self.require_committed_pin,
+            )
+        else:
+            append_pending_receipt(
+                self.ledger_path,
+                attempt_id=self.attempt_id,
+                custody_locator=self.custody_locator,
+                identity_epoch=self.identity_epoch,
+                t1_bindings=self.t1_bindings,
+                head_pin_path=self.head_pin_path,
+                require_committed_pin=self.require_committed_pin,
+            )
+        self.begun = True
+
+    def abandon(self, reason: str) -> Mapping[str, Any] | None:
+        """Best-effort governed closure for an interrupted writer."""
+
+        if not self.begun or self.closed:
+            return None
+        if self.is_bracket_session:
+            assert self.session_id is not None
+            receipt = abort_bracket_session(
+                self.ledger_path,
+                session_id=self.session_id,
+                reason=reason,
+            )
+        else:
+            receipt = finalize_attempt_receipt(
+                self.ledger_path,
+                attempt_id=self.attempt_id,
+                disposition="abandoned",
+                custody_locator=self.custody_locator,
+                artifact_sha256=ledger_artifact_hashes(
+                    Path(self.custody_locator)
+                ),
+                identity_epoch=self.identity_epoch,
+                t1_bindings=self.t1_bindings,
+                capture_wall_time_s=self.capture_wall_time_s,
+                exact_bound_lexeme_s=self.exact_bound_lexeme_s,
+            )
+        self.closed = True
+        return receipt
+
+    def finalize(
+        self, disposition: str
+    ) -> tuple[Mapping[str, Any], dict[str, Any] | None]:
+        """Finalize the exact attempt and return any terminal head candidate."""
+
+        if not self.begun or self.closed:
+            raise CalibrationLedgerError("capture ledger lifecycle is not open")
+        artifacts = ledger_artifact_hashes(Path(self.custody_locator))
+        if self.is_bracket_session:
+            assert self.session_id is not None and self.slot is not None
+            receipt = finalize_bracket_session_slot(
+                self.ledger_path,
+                session_id=self.session_id,
+                slot=self.slot,
+                disposition=disposition,
+                custody_locator=self.custody_locator,
+                artifact_sha256=artifacts,
+                identity_epoch=self.identity_epoch,
+                t1_bindings=self.t1_bindings,
+                capture_wall_time_s=self.capture_wall_time_s,
+                exact_bound_lexeme_s=self.exact_bound_lexeme_s,
+            )
+            if self.slot == "pre" and disposition != "valid":
+                receipt = abort_bracket_session(
+                    self.ledger_path,
+                    session_id=self.session_id,
+                    reason=f"pre_capture_{disposition}",
+                )
+            self.closed = True
+            head_pin = (
+                None
+                if self.slot == "pre" and disposition == "valid"
+                else terminal_head_pin_for_session(
+                    self.ledger_path, session_id=self.session_id
+                )
+            )
+            return receipt, head_pin
+        receipt = finalize_attempt_receipt(
+            self.ledger_path,
+            attempt_id=self.attempt_id,
+            disposition=disposition,
+            custody_locator=self.custody_locator,
+            artifact_sha256=artifacts,
+            identity_epoch=self.identity_epoch,
+            t1_bindings=self.t1_bindings,
+            capture_wall_time_s=self.capture_wall_time_s,
+            exact_bound_lexeme_s=self.exact_bound_lexeme_s,
+        )
+        self.closed = True
+        return receipt, head_pin_for_receipt(receipt)
+
+
+def main(argv: list[str] | None = None) -> int:
     parser = argparse.ArgumentParser(description=__doc__)
     parser.add_argument(
         "--allow-live",
         action="store_true",
         help="explicitly confirm a lead-owned quiet-machine live run",
     )
     parser.add_argument(
         "--output-root",
         type=Path,
         default=REPO_ROOT / "runs" / "instrument_validation",
     )
     parser.add_argument("--rederive-from", type=Path)
     parser.add_argument("--output", type=Path)
     parser.add_argument("--pulse-count", type=int, default=PULSE_COUNT)
+    parser.add_argument(
+        "--session-id",
+        help="predeclared two-slot bracket session id (requires --slot and --attempt-id)",
+    )
+    parser.add_argument(
+        "--slot",
+        choices=BRACKET_SESSION_SLOTS,
+        help="exact predeclared bracket slot to capture",
+    )
+    parser.add_argument(
+        "--attempt-id",
+        help="exact attempt id already reserved for the bracket slot",
+    )
     parser.add_argument(
         "--power-policy",
         default=None,
         help="operator-recorded power policy identity (e.g. 'ac_high_power'); required",
     )
-    args = parser.parse_args()
+    args = parser.parse_args(argv)
+    bracket_values = (args.session_id, args.slot, args.attempt_id)
+    bracket_mode = all(value is not None and value != "" for value in bracket_values)
+    if any(value is not None for value in bracket_values) and not bracket_mode:
+        print(
+            "refusing: --session-id, --slot, and --attempt-id must be supplied together",
+            file=sys.stderr,
+        )
+        return 2
+    if bracket_mode and (args.rederive_from is not None or args.output is not None):
+        print(
+            "refusing: bracket session parameters apply only to live capture",
+            file=sys.stderr,
+        )
+        return 2
     if not verify_frozen_protocol():
         print(
             "refusing: frozen powermetrics fiducial protocol is missing, "
             "incomplete, or disagrees with executable constants",
             file=sys.stderr,
         )
         return 2
     if args.rederive_from is not None:
         if args.output is None:
             print("refusing: --rederive-from requires --output", file=sys.stderr)
             return 2
         try:
             payload = rederive_artifact(args.rederive_from, args.output)
         except ValueError as exc:
             print(f"refusing: {exc}", file=sys.stderr)
             return 2
         print(json.dumps({"status": payload["status"], "output": str(args.output)}))
         return 0 if payload["status"] == "valid" else 1
     if args.output is not None:
         print("refusing: --output requires --rederive-from", file=sys.stderr)
         return 2
     if not args.allow_live:
         print(
             "refusing: live [QUIET-MAC] calibration is lead-owned; "
             "pass --allow-live on a quiet machine",
             file=sys.stderr,
         )
         return 77
     if not args.power_policy:
         print("refusing: --power-policy is a binding field", file=sys.stderr)
         return 2
 
     import mlx.core as mx  # noqa: PLC0415
 
     clock = SystemClock()
-    validation_id = time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
+    validation_id = (
+        args.attempt_id
+        if bracket_mode
+        else time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
+    )
     out_dir = args.output_root / validation_id
     custody_locator = str(out_dir.resolve())
     planned_epoch = {
         "os_build": _sysctl_identity("kern.osversion"),
         "hardware_model": _sysctl_identity("hw.model"),
         "power_policy": args.power_policy,
         "sampling_interval_ms": SAMPLING_INTERVAL_MS,
         "estimator_revision": RESIDUAL_REGION_METHOD,
         "pulse_protocol_id": PROTOCOL_ID,
     }
     planned_t1 = {
         **planned_epoch,
         "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
         "anchor_method_version": CLOCK_METHOD_V2,
         "mlx_version": getattr(mx, "__version__", None),
         "protocol_sha256": sha256_path(PROTOCOL_PATH),
     }
-    # D-109 reservation-first: this authenticated receipt precedes directory
-    # creation, sampler launch, and all hardware capture.  The mechanism
-    # closes workflow omission, unregistered evidence, and rollback/stale-head
-    # consumption; it does not resist a malicious trusted writer or a rewrite
-    # of both Git and complete ledger history.
-    append_pending_receipt(
-        DEFAULT_LEDGER_PATH,
+    # D-109 reservation-first: ordinary captures append here; D-117 bracket
+    # captures authenticate the exact slot that the bookend tool already
+    # reserved. Both paths run before directory creation, sampler launch, and
+    # all hardware capture.
+    ledger_lifecycle = _CaptureLedgerLifecycle(
+        ledger_path=DEFAULT_LEDGER_PATH,
+        head_pin_path=DEFAULT_HEAD_PIN_PATH,
         attempt_id=validation_id,
         custody_locator=custody_locator,
         identity_epoch=planned_epoch,
         t1_bindings=planned_t1,
+        session_id=args.session_id if bracket_mode else None,
+        slot=args.slot if bracket_mode else None,
     )
-    finalization_state: dict[str, object] = {
-        "finalized": False,
-        "identity_epoch": planned_epoch,
-        "t1_bindings": planned_t1,
-        "capture_wall_time_s": None,
-        "exact_bound_lexeme_s": None,
-    }
+    try:
+        ledger_lifecycle.begin()
+    except CalibrationLedgerError as exc:
+        print(f"refusing: {exc}", file=sys.stderr)
+        return 2
 
-    def finalize_abandoned() -> None:
-        """Best effort on ruled failures; a failed append leaves pending refusal."""
+    def finalize_abandoned(
+        reason: str = "writer_exit_before_slot_finalization",
+    ) -> None:
+        """Best effort; a failed closure leaves a fail-closed pending/open state."""
 
-        if finalization_state["finalized"]:
-            return
         try:
-            finalize_attempt_receipt(
-                DEFAULT_LEDGER_PATH,
-                attempt_id=validation_id,
-                disposition="abandoned",
-                custody_locator=custody_locator,
-                artifact_sha256=ledger_artifact_hashes(out_dir),
-                identity_epoch=finalization_state["identity_epoch"],
-                t1_bindings=finalization_state["t1_bindings"],
-                capture_wall_time_s=finalization_state["capture_wall_time_s"],
-                exact_bound_lexeme_s=finalization_state[
-                    "exact_bound_lexeme_s"
-                ],
-            )
-        except Exception:  # noqa: BLE001 - pending is the mandatory fail-closed state
+            ledger_lifecycle.abandon(reason)
+        except Exception:  # noqa: BLE001 - pending/open is mandatory fail-closed state
             return
-        finalization_state["finalized"] = True
 
     # An actual interpreter-level uncaught exception/interrupt finalizes when
     # possible. A hard crash between these two appends intentionally leaves
     # ``pending``, which every downstream snapshot refuses.
     atexit.register(finalize_abandoned)
     (out_dir / "raw").mkdir(parents=True, exist_ok=False)
     capture_path = out_dir / "raw" / "powermetrics.plist"
     events_path = out_dir / "events.jsonl"
     events = events_path.open("w", encoding="utf-8")
 
     def emit(event_type: str, metadata: dict) -> None:
         events.write(
             json.dumps(
                 {
                     "timestamp_s": clock.now(),
                     "event_type": event_type,
                     "phase": "instrument_validation",
                     "message": event_type,
                     "metadata": metadata,
                 },
                 sort_keys=True,
             )
             + "\n"
         )
         events.flush()
 
     buffers = allocate_matmul_buffers()
     command = [
         "sudo",
         "-n",
         POWER_METRICS,
         "-b",
         "0",
         "-i",
         str(SAMPLING_INTERVAL_MS),
         "--samplers",
         SAMPLERS,
         "--format",
         "plist",
         "-o",
         str(capture_path),
     ]
     pre_spawn = clock.stamp()
     process = subprocess.Popen(
         command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
     )
     first_parse = None
     deadline = time.monotonic() + 15.0
     while time.monotonic() < deadline:
         if capture_path.exists() and capture_path.stat().st_size > 0:
             first_frame = capture_path.read_bytes().split(b"\0", 1)[0]
             if first_frame.strip():
                 try:
                     parse_powermetrics_records(first_frame)
                 except ValueError:
                     pass
                 else:
                     first_parse = clock.stamp()
                     break
         time.sleep(0.05)
     if first_parse is None:
         process.terminate()
-        finalize_abandoned()
+        finalize_abandoned("powermetrics_never_ready")
         print("powermetrics never became ready", file=sys.stderr)
         return 1
     # D-078: wait for a native whole-second rollover before any workload.
     try:
         wait_for_preworkload_rollover(capture_path, process)
     except RuntimeError as exc:
         events.close()
-        finalize_abandoned()
+        finalize_abandoned(str(exc))
         print(f"refusing: {exc}", file=sys.stderr)
         return 1
     sampling_started = clock.stamp()
     emit("sampling_started", {})
 
     time.sleep(BASELINE_S)
     warmups: list[CommandedPulse] = []
     for warmup_index in range(WARMUP_PULSE_COUNT):
         on_stamp = clock.stamp()
         emit(
             "warmup_command_on",
             {"warmup_index": warmup_index, "clock_stamp": asdict(on_stamp)},
         )
         run_matmul_pulse(PULSE_DURATION_S, buffers)
         off_stamp = clock.stamp()
         emit(
             "warmup_command_off",
             {"warmup_index": warmup_index, "clock_stamp": asdict(off_stamp)},
         )
         warmups.append(
             CommandedPulse(
                 on_s=on_stamp.epoch_s,
                 off_s=off_stamp.epoch_s,
                 on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
                 off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
             )
         )
         time.sleep(1.5)
     time.sleep(BASELINE_S)
 
     # Van der Corput spacing is schedule-relative (offsets start at 0 for the
     # first pulse), so the loop cursor MUST be measured from the pulse-loop
     # start, not from sampling-start (which precedes it by the baseline +
     # warmup + baseline preamble). Measuring elapsed against sampling_started
     # made every gap negative and collapsed the pulses back-to-back.
     pulse_loop_mono0 = time.monotonic()
     pulses: list[CommandedPulse] = []
     for on_offset_s, off_offset_s in pulse_schedule(args.pulse_count):
         if pulses:
             elapsed_s = time.monotonic() - pulse_loop_mono0
             time.sleep(max(0.0, on_offset_s - elapsed_s))
         on_stamp = clock.stamp()
         emit(
             "pulse_command_on",
             {"clock_stamp": asdict(on_stamp), "planned_on_offset_s": on_offset_s},
         )
         run_matmul_pulse(PULSE_DURATION_S, buffers)
         off_stamp = clock.stamp()
         emit(
             "pulse_command_off",
             {"clock_stamp": asdict(off_stamp), "planned_off_offset_s": off_offset_s},
         )
         pulses.append(
             CommandedPulse(
                 on_s=on_stamp.epoch_s,
                 off_s=off_stamp.epoch_s,
                 on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
                 off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
             )
         )
     time.sleep(BASELINE_S)
     sampling_stopped = clock.stamp()
     emit("sampling_stopped", {})
     _terminate_powermetrics(process)
     post_parse = clock.stamp()
 
     data = capture_path.read_bytes()
     native_records = parse_powermetrics_records(data)
     evidence, point_anchor_s = derive_powermetrics_clock_evidence_v2(
         stamps={
             "pre_spawn": pre_spawn,
             "first_parse": first_parse,
             "sampling_started": sampling_started,
             "sampling_stopped": sampling_stopped,
             "post_parse": post_parse,
         },
         records=anchor_records_from_powermetrics(native_records),
     )
     anchor_resolved = point_anchor_s is not None
     if not anchor_resolved:
         print(
             "clock_anchor_unresolved: calibration capture cannot be anchored",
             file=sys.stderr,
         )
         # Fail closed: an unanchored capture can never be a valid calibration.
         # Detection still runs against the 1 s-quantized native stamps so the
         # diagnostic artifact records why, but the evidence is forced invalid
         # and the script exits nonzero below.
         anchored = native_records
     else:
         anchored = parse_powermetrics_records(
             data, first_record_endpoint_s=point_anchor_s
         )
     samples = samples_from_records(anchored)
     trace_path = out_dir / "power_trace.csv"
     with trace_path.open("w", encoding="utf-8") as handle:
         handle.write(
             "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
         )
         for sample in samples:
             handle.write(
                 f"{sample.timestamp_s!r},{sample.power_w!r},{sample.source},"
                 f"{sample.rail},{sample.interval_start_s!r},{sample.interval_end_s!r}\n"
             )
 
     intervals = [
         TraceInterval(
             start_s=record.timestamp_s - record.elapsed_ns / 1e9,
             end_s=record.timestamp_s,
             power_w=record.rail_power_w["gpu_power"],
         )
         for record in anchored
     ]
     detection = detect_pulses(
         trim_trace_after_warmups(intervals, warmups),
         pulses,
         trace_anchor_bound_s=(
             float(evidence["clock_anchor"]["effective_clock_anchor_bound_s"])
             if anchor_resolved
             else 0.0
         ),
     )
     events.close()
 
     device_meta = native_records[0].metadata if native_records else {}
     bindings = {
         "hardware_model": device_meta.get("hw_model"),
         "os_build": device_meta.get("kern_osversion"),
         "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
         "sampling_interval_ms": SAMPLING_INTERVAL_MS,
         "anchor_method_version": evidence["clock_anchor"].get("method"),
         "mlx_version": getattr(mx, "__version__", None),
         "pulse_protocol_id": PROTOCOL_ID,
         "power_policy": args.power_policy,
         "estimator_revision": RESIDUAL_REGION_METHOD,
         "protocol_sha256": sha256_path(PROTOCOL_PATH),
     }
-    finalization_state["identity_epoch"] = {
+    ledger_lifecycle.identity_epoch = {
         field: bindings.get(field)
         for field in (
             "os_build",
             "hardware_model",
             "power_policy",
             "sampling_interval_ms",
             "estimator_revision",
             "pulse_protocol_id",
         )
     }
-    finalization_state["t1_bindings"] = bindings
-    finalization_state["capture_wall_time_s"] = str(sampling_started.epoch_s)
+    ledger_lifecycle.t1_bindings = bindings
+    ledger_lifecycle.capture_wall_time_s = str(sampling_started.epoch_s)
     evidence_payload = instrument_evidence(
         detection,
         bindings=bindings,
         validation_id=validation_id,
         artifact_sha256={
             "raw/powermetrics.plist": sha256_path(capture_path),
             "events.jsonl": sha256_path(events_path),
             "power_trace.csv": sha256_path(trace_path),
         },
         capture_wall_time_s=sampling_started.epoch_s,
     )
     evidence_payload["clock_anchor"] = evidence["clock_anchor"]
     evidence_payload["clock_anchor_resolved"] = anchor_resolved
     if not anchor_resolved:
         evidence_payload["status"] = "invalid"
         evidence_payload["reasons"] = sorted(
             set(evidence_payload.get("reasons", [])) | {"clock_anchor_unresolved"}
         )
     (out_dir / "instrument_evidence.json").write_text(
         json.dumps(evidence_payload, indent=2, sort_keys=True) + "\n",
         encoding="utf-8",
     )
     manifest = {
         "schema_version": "joulewise.instrument_validation_manifest.v1",
         "validation_id": validation_id,
         "protocol_id": PROTOCOL_ID,
         "pulse_count": args.pulse_count,
         "artifacts": {
             name: sha256_path(out_dir / name)
             for name in (
                 "events.jsonl",
                 "power_trace.csv",
                 "instrument_evidence.json",
             )
         }
         | {"raw/powermetrics.plist": sha256_path(capture_path)},
     }
     (out_dir / "manifest.json").write_text(
         json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
     )
     serialized_evidence = json.loads(
         json.dumps(evidence_payload, sort_keys=True),
         parse_float=str,
         parse_int=str,
     )
     bound_lexeme = serialized_evidence.get("b_fiducial_s")
-    finalization_state["exact_bound_lexeme_s"] = (
+    ledger_lifecycle.exact_bound_lexeme_s = (
         bound_lexeme if isinstance(bound_lexeme, str) else None
     )
     disposition = "ordinary-invalid"
     if evidence_payload["status"] == "valid":
         disposition = (
             "systematic-invalid"
             if isinstance(bound_lexeme, str)
             and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
             else "valid"
         )
-    final_receipt = finalize_attempt_receipt(
-        DEFAULT_LEDGER_PATH,
-        attempt_id=validation_id,
-        disposition=disposition,
-        custody_locator=custody_locator,
-        artifact_sha256=ledger_artifact_hashes(out_dir),
-        identity_epoch=finalization_state["identity_epoch"],
-        t1_bindings=finalization_state["t1_bindings"],
-        capture_wall_time_s=finalization_state["capture_wall_time_s"],
-        exact_bound_lexeme_s=finalization_state["exact_bound_lexeme_s"],
-    )
-    finalization_state["finalized"] = True
+    _final_receipt, head_pin_candidate = ledger_lifecycle.finalize(disposition)
     atexit.unregister(finalize_abandoned)
-    print(json.dumps({
+    output = {
         "validation_id": validation_id,
         "status": evidence_payload["status"],
         "b_fiducial_s": evidence_payload["b_fiducial_s"],
         "output": str(out_dir),
-        "ledger_head_pin_candidate": head_pin_for_receipt(final_receipt),
+        "ledger_head_pin_candidate": head_pin_candidate,
         "claim_evaluation_blocked_until_pin_commit": True,
-    }, indent=2))
+    }
+    if bracket_mode:
+        output["bracket_session"] = {
+            "session_id": args.session_id,
+            "slot": args.slot,
+            "attempt_id": args.attempt_id,
+        }
+    print(json.dumps(output, indent=2))
     return 0 if disposition == "valid" else 1
 
 
 if __name__ == "__main__":
     raise SystemExit(main())

exec
/bin/zsh -lc "rg -n \"_validate_reserved|_CaptureLedger|def begin|def abandon|def finalize|append_pending|abort_bracket|terminal_head|main\\(\" scripts/validate_powermetrics_fiducial.py; nl -ba scripts/validate_powermetrics_fiducial.py | sed -n '300,570p'; nl -ba scripts/validate_powermetrics_fiducial.py | sed -n '570,980p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
57:    abort_bracket_session,
58:    append_pending_receipt,
64:    terminal_head_pin_for_session,
288:def _validate_reserved_bracket_slot(
351:class _CaptureLedgerLifecycle:
389:    def begin(self) -> None:
396:            _validate_reserved_bracket_slot(
408:            append_pending_receipt(
419:    def abandon(self, reason: str) -> Mapping[str, Any] | None:
426:            receipt = abort_bracket_session(
448:    def finalize(
471:                receipt = abort_bracket_session(
480:                else terminal_head_pin_for_session(
500:def main(argv: list[str] | None = None) -> int:
609:    ledger_lifecycle = _CaptureLedgerLifecycle(
625:    def finalize_abandoned(
933:    raise SystemExit(main())
   300	    """Authenticate the exact predeclared slot before capture state exists."""
   301	
   302	    snapshot = load_calibration_ledger_snapshot(
   303	        ledger_path,
   304	        head_pin_path,
   305	        require_committed_pin=require_committed_pin,
   306	        verify_custody=True,
   307	    )
   308	    session = snapshot.bracket_session_by_id.get(session_id)
   309	    finalized_slots = set(session.finalized_slots) if session is not None else set()
   310	    expected_slot = (
   311	        "pre"
   312	        if not finalized_slots
   313	        else "post"
   314	        if finalized_slots == {"pre"}
   315	        else None
   316	    )
   317	    open_receipt = next(
   318	        (
   319	            receipt
   320	            for receipt in snapshot.receipts
   321	            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
   322	            and receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
   323	            and receipt.get("session_id") == session_id
   324	        ),
   325	        None,
   326	    )
   327	    reserved = (
   328	        open_receipt.get("slots", {}).get(slot)
   329	        if isinstance(open_receipt, Mapping)
   330	        and isinstance(open_receipt.get("slots"), Mapping)
   331	        else None
   332	    )
   333	    if (
   334	        not snapshot.is_governed_open_bracket_extension
   335	        or session is None
   336	        or session.state != "open"
   337	        or slot not in BRACKET_SESSION_SLOTS
   338	        or slot != expected_slot
   339	        or session.slot_attempt_ids.get(slot) != attempt_id
   340	        or not isinstance(reserved, Mapping)
   341	        or reserved.get("attempt_id") != attempt_id
   342	        or reserved.get("custody_locator") != custody_locator
   343	        or dict(reserved.get("identity_epoch", {})) != dict(identity_epoch)
   344	        or dict(reserved.get("t1_bindings", {})) != dict(t1_bindings)
   345	    ):
   346	        raise CalibrationLedgerError(
   347	            "capture does not match the exact reserved bracket session slot"
   348	        )
   349	
   350	
   351	class _CaptureLedgerLifecycle:
   352	    """Route one writer attempt through ordinary or bracket-session APIs."""
   353	
   354	    def __init__(
   355	        self,
   356	        *,
   357	        ledger_path: Path,
   358	        head_pin_path: Path,
   359	        attempt_id: str,
   360	        custody_locator: str,
   361	        identity_epoch: Mapping[str, Any],
   362	        t1_bindings: Mapping[str, Any],
   363	        session_id: str | None = None,
   364	        slot: str | None = None,
   365	        require_committed_pin: bool = True,
   366	    ) -> None:
   367	        if (session_id is None) != (slot is None):
   368	            raise CalibrationLedgerError(
   369	                "bracket session id and slot must be supplied together"
   370	            )
   371	        self.ledger_path = Path(ledger_path)
   372	        self.head_pin_path = Path(head_pin_path)
   373	        self.attempt_id = attempt_id
   374	        self.custody_locator = custody_locator
   375	        self.identity_epoch: Mapping[str, Any] = identity_epoch
   376	        self.t1_bindings: Mapping[str, Any] = t1_bindings
   377	        self.capture_wall_time_s: str | None = None
   378	        self.exact_bound_lexeme_s: str | None = None
   379	        self.session_id = session_id
   380	        self.slot = slot
   381	        self.require_committed_pin = require_committed_pin
   382	        self.begun = False
   383	        self.closed = False
   384	
   385	    @property
   386	    def is_bracket_session(self) -> bool:
   387	        return self.session_id is not None
   388	
   389	    def begin(self) -> None:
   390	        """Reserve ordinarily, or authenticate a previously reserved slot."""
   391	
   392	        if self.begun:
   393	            raise CalibrationLedgerError("capture ledger lifecycle already began")
   394	        if self.is_bracket_session:
   395	            assert self.session_id is not None and self.slot is not None
   396	            _validate_reserved_bracket_slot(
   397	                self.ledger_path,
   398	                self.head_pin_path,
   399	                session_id=self.session_id,
   400	                slot=self.slot,
   401	                attempt_id=self.attempt_id,
   402	                custody_locator=self.custody_locator,
   403	                identity_epoch=self.identity_epoch,
   404	                t1_bindings=self.t1_bindings,
   405	                require_committed_pin=self.require_committed_pin,
   406	            )
   407	        else:
   408	            append_pending_receipt(
   409	                self.ledger_path,
   410	                attempt_id=self.attempt_id,
   411	                custody_locator=self.custody_locator,
   412	                identity_epoch=self.identity_epoch,
   413	                t1_bindings=self.t1_bindings,
   414	                head_pin_path=self.head_pin_path,
   415	                require_committed_pin=self.require_committed_pin,
   416	            )
   417	        self.begun = True
   418	
   419	    def abandon(self, reason: str) -> Mapping[str, Any] | None:
   420	        """Best-effort governed closure for an interrupted writer."""
   421	
   422	        if not self.begun or self.closed:
   423	            return None
   424	        if self.is_bracket_session:
   425	            assert self.session_id is not None
   426	            receipt = abort_bracket_session(
   427	                self.ledger_path,
   428	                session_id=self.session_id,
   429	                reason=reason,
   430	            )
   431	        else:
   432	            receipt = finalize_attempt_receipt(
   433	                self.ledger_path,
   434	                attempt_id=self.attempt_id,
   435	                disposition="abandoned",
   436	                custody_locator=self.custody_locator,
   437	                artifact_sha256=ledger_artifact_hashes(
   438	                    Path(self.custody_locator)
   439	                ),
   440	                identity_epoch=self.identity_epoch,
   441	                t1_bindings=self.t1_bindings,
   442	                capture_wall_time_s=self.capture_wall_time_s,
   443	                exact_bound_lexeme_s=self.exact_bound_lexeme_s,
   444	            )
   445	        self.closed = True
   446	        return receipt
   447	
   448	    def finalize(
   449	        self, disposition: str
   450	    ) -> tuple[Mapping[str, Any], dict[str, Any] | None]:
   451	        """Finalize the exact attempt and return any terminal head candidate."""
   452	
   453	        if not self.begun or self.closed:
   454	            raise CalibrationLedgerError("capture ledger lifecycle is not open")
   455	        artifacts = ledger_artifact_hashes(Path(self.custody_locator))
   456	        if self.is_bracket_session:
   457	            assert self.session_id is not None and self.slot is not None
   458	            receipt = finalize_bracket_session_slot(
   459	                self.ledger_path,
   460	                session_id=self.session_id,
   461	                slot=self.slot,
   462	                disposition=disposition,
   463	                custody_locator=self.custody_locator,
   464	                artifact_sha256=artifacts,
   465	                identity_epoch=self.identity_epoch,
   466	                t1_bindings=self.t1_bindings,
   467	                capture_wall_time_s=self.capture_wall_time_s,
   468	                exact_bound_lexeme_s=self.exact_bound_lexeme_s,
   469	            )
   470	            if self.slot == "pre" and disposition != "valid":
   471	                receipt = abort_bracket_session(
   472	                    self.ledger_path,
   473	                    session_id=self.session_id,
   474	                    reason=f"pre_capture_{disposition}",
   475	                )
   476	            self.closed = True
   477	            head_pin = (
   478	                None
   479	                if self.slot == "pre" and disposition == "valid"
   480	                else terminal_head_pin_for_session(
   481	                    self.ledger_path, session_id=self.session_id
   482	                )
   483	            )
   484	            return receipt, head_pin
   485	        receipt = finalize_attempt_receipt(
   486	            self.ledger_path,
   487	            attempt_id=self.attempt_id,
   488	            disposition=disposition,
   489	            custody_locator=self.custody_locator,
   490	            artifact_sha256=artifacts,
   491	            identity_epoch=self.identity_epoch,
   492	            t1_bindings=self.t1_bindings,
   493	            capture_wall_time_s=self.capture_wall_time_s,
   494	            exact_bound_lexeme_s=self.exact_bound_lexeme_s,
   495	        )
   496	        self.closed = True
   497	        return receipt, head_pin_for_receipt(receipt)
   498	
   499	
   500	def main(argv: list[str] | None = None) -> int:
   501	    parser = argparse.ArgumentParser(description=__doc__)
   502	    parser.add_argument(
   503	        "--allow-live",
   504	        action="store_true",
   505	        help="explicitly confirm a lead-owned quiet-machine live run",
   506	    )
   507	    parser.add_argument(
   508	        "--output-root",
   509	        type=Path,
   510	        default=REPO_ROOT / "runs" / "instrument_validation",
   511	    )
   512	    parser.add_argument("--rederive-from", type=Path)
   513	    parser.add_argument("--output", type=Path)
   514	    parser.add_argument("--pulse-count", type=int, default=PULSE_COUNT)
   515	    parser.add_argument(
   516	        "--session-id",
   517	        help="predeclared two-slot bracket session id (requires --slot and --attempt-id)",
   518	    )
   519	    parser.add_argument(
   520	        "--slot",
   521	        choices=BRACKET_SESSION_SLOTS,
   522	        help="exact predeclared bracket slot to capture",
   523	    )
   524	    parser.add_argument(
   525	        "--attempt-id",
   526	        help="exact attempt id already reserved for the bracket slot",
   527	    )
   528	    parser.add_argument(
   529	        "--power-policy",
   530	        default=None,
   531	        help="operator-recorded power policy identity (e.g. 'ac_high_power'); required",
   532	    )
   533	    args = parser.parse_args(argv)
   534	    bracket_values = (args.session_id, args.slot, args.attempt_id)
   535	    bracket_mode = all(value is not None and value != "" for value in bracket_values)
   536	    if any(value is not None for value in bracket_values) and not bracket_mode:
   537	        print(
   538	            "refusing: --session-id, --slot, and --attempt-id must be supplied together",
   539	            file=sys.stderr,
   540	        )
   541	        return 2
   542	    if bracket_mode and (args.rederive_from is not None or args.output is not None):
   543	        print(
   544	            "refusing: bracket session parameters apply only to live capture",
   545	            file=sys.stderr,
   546	        )
   547	        return 2
   548	    if not verify_frozen_protocol():
   549	        print(
   550	            "refusing: frozen powermetrics fiducial protocol is missing, "
   551	            "incomplete, or disagrees with executable constants",
   552	            file=sys.stderr,
   553	        )
   554	        return 2
   555	    if args.rederive_from is not None:
   556	        if args.output is None:
   557	            print("refusing: --rederive-from requires --output", file=sys.stderr)
   558	            return 2
   559	        try:
   560	            payload = rederive_artifact(args.rederive_from, args.output)
   561	        except ValueError as exc:
   562	            print(f"refusing: {exc}", file=sys.stderr)
   563	            return 2
   564	        print(json.dumps({"status": payload["status"], "output": str(args.output)}))
   565	        return 0 if payload["status"] == "valid" else 1
   566	    if args.output is not None:
   567	        print("refusing: --output requires --rederive-from", file=sys.stderr)
   568	        return 2
   569	    if not args.allow_live:
   570	        print(
   570	        print(
   571	            "refusing: live [QUIET-MAC] calibration is lead-owned; "
   572	            "pass --allow-live on a quiet machine",
   573	            file=sys.stderr,
   574	        )
   575	        return 77
   576	    if not args.power_policy:
   577	        print("refusing: --power-policy is a binding field", file=sys.stderr)
   578	        return 2
   579	
   580	    import mlx.core as mx  # noqa: PLC0415
   581	
   582	    clock = SystemClock()
   583	    validation_id = (
   584	        args.attempt_id
   585	        if bracket_mode
   586	        else time.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
   587	    )
   588	    out_dir = args.output_root / validation_id
   589	    custody_locator = str(out_dir.resolve())
   590	    planned_epoch = {
   591	        "os_build": _sysctl_identity("kern.osversion"),
   592	        "hardware_model": _sysctl_identity("hw.model"),
   593	        "power_policy": args.power_policy,
   594	        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
   595	        "estimator_revision": RESIDUAL_REGION_METHOD,
   596	        "pulse_protocol_id": PROTOCOL_ID,
   597	    }
   598	    planned_t1 = {
   599	        **planned_epoch,
   600	        "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
   601	        "anchor_method_version": CLOCK_METHOD_V2,
   602	        "mlx_version": getattr(mx, "__version__", None),
   603	        "protocol_sha256": sha256_path(PROTOCOL_PATH),
   604	    }
   605	    # D-109 reservation-first: ordinary captures append here; D-117 bracket
   606	    # captures authenticate the exact slot that the bookend tool already
   607	    # reserved. Both paths run before directory creation, sampler launch, and
   608	    # all hardware capture.
   609	    ledger_lifecycle = _CaptureLedgerLifecycle(
   610	        ledger_path=DEFAULT_LEDGER_PATH,
   611	        head_pin_path=DEFAULT_HEAD_PIN_PATH,
   612	        attempt_id=validation_id,
   613	        custody_locator=custody_locator,
   614	        identity_epoch=planned_epoch,
   615	        t1_bindings=planned_t1,
   616	        session_id=args.session_id if bracket_mode else None,
   617	        slot=args.slot if bracket_mode else None,
   618	    )
   619	    try:
   620	        ledger_lifecycle.begin()
   621	    except CalibrationLedgerError as exc:
   622	        print(f"refusing: {exc}", file=sys.stderr)
   623	        return 2
   624	
   625	    def finalize_abandoned(
   626	        reason: str = "writer_exit_before_slot_finalization",
   627	    ) -> None:
   628	        """Best effort; a failed closure leaves a fail-closed pending/open state."""
   629	
   630	        try:
   631	            ledger_lifecycle.abandon(reason)
   632	        except Exception:  # noqa: BLE001 - pending/open is mandatory fail-closed state
   633	            return
   634	
   635	    # An actual interpreter-level uncaught exception/interrupt finalizes when
   636	    # possible. A hard crash between these two appends intentionally leaves
   637	    # ``pending``, which every downstream snapshot refuses.
   638	    atexit.register(finalize_abandoned)
   639	    (out_dir / "raw").mkdir(parents=True, exist_ok=False)
   640	    capture_path = out_dir / "raw" / "powermetrics.plist"
   641	    events_path = out_dir / "events.jsonl"
   642	    events = events_path.open("w", encoding="utf-8")
   643	
   644	    def emit(event_type: str, metadata: dict) -> None:
   645	        events.write(
   646	            json.dumps(
   647	                {
   648	                    "timestamp_s": clock.now(),
   649	                    "event_type": event_type,
   650	                    "phase": "instrument_validation",
   651	                    "message": event_type,
   652	                    "metadata": metadata,
   653	                },
   654	                sort_keys=True,
   655	            )
   656	            + "\n"
   657	        )
   658	        events.flush()
   659	
   660	    buffers = allocate_matmul_buffers()
   661	    command = [
   662	        "sudo",
   663	        "-n",
   664	        POWER_METRICS,
   665	        "-b",
   666	        "0",
   667	        "-i",
   668	        str(SAMPLING_INTERVAL_MS),
   669	        "--samplers",
   670	        SAMPLERS,
   671	        "--format",
   672	        "plist",
   673	        "-o",
   674	        str(capture_path),
   675	    ]
   676	    pre_spawn = clock.stamp()
   677	    process = subprocess.Popen(
   678	        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
   679	    )
   680	    first_parse = None
   681	    deadline = time.monotonic() + 15.0
   682	    while time.monotonic() < deadline:
   683	        if capture_path.exists() and capture_path.stat().st_size > 0:
   684	            first_frame = capture_path.read_bytes().split(b"\0", 1)[0]
   685	            if first_frame.strip():
   686	                try:
   687	                    parse_powermetrics_records(first_frame)
   688	                except ValueError:
   689	                    pass
   690	                else:
   691	                    first_parse = clock.stamp()
   692	                    break
   693	        time.sleep(0.05)
   694	    if first_parse is None:
   695	        process.terminate()
   696	        finalize_abandoned("powermetrics_never_ready")
   697	        print("powermetrics never became ready", file=sys.stderr)
   698	        return 1
   699	    # D-078: wait for a native whole-second rollover before any workload.
   700	    try:
   701	        wait_for_preworkload_rollover(capture_path, process)
   702	    except RuntimeError as exc:
   703	        events.close()
   704	        finalize_abandoned(str(exc))
   705	        print(f"refusing: {exc}", file=sys.stderr)
   706	        return 1
   707	    sampling_started = clock.stamp()
   708	    emit("sampling_started", {})
   709	
   710	    time.sleep(BASELINE_S)
   711	    warmups: list[CommandedPulse] = []
   712	    for warmup_index in range(WARMUP_PULSE_COUNT):
   713	        on_stamp = clock.stamp()
   714	        emit(
   715	            "warmup_command_on",
   716	            {"warmup_index": warmup_index, "clock_stamp": asdict(on_stamp)},
   717	        )
   718	        run_matmul_pulse(PULSE_DURATION_S, buffers)
   719	        off_stamp = clock.stamp()
   720	        emit(
   721	            "warmup_command_off",
   722	            {"warmup_index": warmup_index, "clock_stamp": asdict(off_stamp)},
   723	        )
   724	        warmups.append(
   725	            CommandedPulse(
   726	                on_s=on_stamp.epoch_s,
   727	                off_s=off_stamp.epoch_s,
   728	                on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
   729	                off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
   730	            )
   731	        )
   732	        time.sleep(1.5)
   733	    time.sleep(BASELINE_S)
   734	
   735	    # Van der Corput spacing is schedule-relative (offsets start at 0 for the
   736	    # first pulse), so the loop cursor MUST be measured from the pulse-loop
   737	    # start, not from sampling-start (which precedes it by the baseline +
   738	    # warmup + baseline preamble). Measuring elapsed against sampling_started
   739	    # made every gap negative and collapsed the pulses back-to-back.
   740	    pulse_loop_mono0 = time.monotonic()
   741	    pulses: list[CommandedPulse] = []
   742	    for on_offset_s, off_offset_s in pulse_schedule(args.pulse_count):
   743	        if pulses:
   744	            elapsed_s = time.monotonic() - pulse_loop_mono0
   745	            time.sleep(max(0.0, on_offset_s - elapsed_s))
   746	        on_stamp = clock.stamp()
   747	        emit(
   748	            "pulse_command_on",
   749	            {"clock_stamp": asdict(on_stamp), "planned_on_offset_s": on_offset_s},
   750	        )
   751	        run_matmul_pulse(PULSE_DURATION_S, buffers)
   752	        off_stamp = clock.stamp()
   753	        emit(
   754	            "pulse_command_off",
   755	            {"clock_stamp": asdict(off_stamp), "planned_off_offset_s": off_offset_s},
   756	        )
   757	        pulses.append(
   758	            CommandedPulse(
   759	                on_s=on_stamp.epoch_s,
   760	                off_s=off_stamp.epoch_s,
   761	                on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
   762	                off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
   763	            )
   764	        )
   765	    time.sleep(BASELINE_S)
   766	    sampling_stopped = clock.stamp()
   767	    emit("sampling_stopped", {})
   768	    _terminate_powermetrics(process)
   769	    post_parse = clock.stamp()
   770	
   771	    data = capture_path.read_bytes()
   772	    native_records = parse_powermetrics_records(data)
   773	    evidence, point_anchor_s = derive_powermetrics_clock_evidence_v2(
   774	        stamps={
   775	            "pre_spawn": pre_spawn,
   776	            "first_parse": first_parse,
   777	            "sampling_started": sampling_started,
   778	            "sampling_stopped": sampling_stopped,
   779	            "post_parse": post_parse,
   780	        },
   781	        records=anchor_records_from_powermetrics(native_records),
   782	    )
   783	    anchor_resolved = point_anchor_s is not None
   784	    if not anchor_resolved:
   785	        print(
   786	            "clock_anchor_unresolved: calibration capture cannot be anchored",
   787	            file=sys.stderr,
   788	        )
   789	        # Fail closed: an unanchored capture can never be a valid calibration.
   790	        # Detection still runs against the 1 s-quantized native stamps so the
   791	        # diagnostic artifact records why, but the evidence is forced invalid
   792	        # and the script exits nonzero below.
   793	        anchored = native_records
   794	    else:
   795	        anchored = parse_powermetrics_records(
   796	            data, first_record_endpoint_s=point_anchor_s
   797	        )
   798	    samples = samples_from_records(anchored)
   799	    trace_path = out_dir / "power_trace.csv"
   800	    with trace_path.open("w", encoding="utf-8") as handle:
   801	        handle.write(
   802	            "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
   803	        )
   804	        for sample in samples:
   805	            handle.write(
   806	                f"{sample.timestamp_s!r},{sample.power_w!r},{sample.source},"
   807	                f"{sample.rail},{sample.interval_start_s!r},{sample.interval_end_s!r}\n"
   808	            )
   809	
   810	    intervals = [
   811	        TraceInterval(
   812	            start_s=record.timestamp_s - record.elapsed_ns / 1e9,
   813	            end_s=record.timestamp_s,
   814	            power_w=record.rail_power_w["gpu_power"],
   815	        )
   816	        for record in anchored
   817	    ]
   818	    detection = detect_pulses(
   819	        trim_trace_after_warmups(intervals, warmups),
   820	        pulses,
   821	        trace_anchor_bound_s=(
   822	            float(evidence["clock_anchor"]["effective_clock_anchor_bound_s"])
   823	            if anchor_resolved
   824	            else 0.0
   825	        ),
   826	    )
   827	    events.close()
   828	
   829	    device_meta = native_records[0].metadata if native_records else {}
   830	    bindings = {
   831	        "hardware_model": device_meta.get("hw_model"),
   832	        "os_build": device_meta.get("kern_osversion"),
   833	        "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
   834	        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
   835	        "anchor_method_version": evidence["clock_anchor"].get("method"),
   836	        "mlx_version": getattr(mx, "__version__", None),
   837	        "pulse_protocol_id": PROTOCOL_ID,
   838	        "power_policy": args.power_policy,
   839	        "estimator_revision": RESIDUAL_REGION_METHOD,
   840	        "protocol_sha256": sha256_path(PROTOCOL_PATH),
   841	    }
   842	    ledger_lifecycle.identity_epoch = {
   843	        field: bindings.get(field)
   844	        for field in (
   845	            "os_build",
   846	            "hardware_model",
   847	            "power_policy",
   848	            "sampling_interval_ms",
   849	            "estimator_revision",
   850	            "pulse_protocol_id",
   851	        )
   852	    }
   853	    ledger_lifecycle.t1_bindings = bindings
   854	    ledger_lifecycle.capture_wall_time_s = str(sampling_started.epoch_s)
   855	    evidence_payload = instrument_evidence(
   856	        detection,
   857	        bindings=bindings,
   858	        validation_id=validation_id,
   859	        artifact_sha256={
   860	            "raw/powermetrics.plist": sha256_path(capture_path),
   861	            "events.jsonl": sha256_path(events_path),
   862	            "power_trace.csv": sha256_path(trace_path),
   863	        },
   864	        capture_wall_time_s=sampling_started.epoch_s,
   865	    )
   866	    evidence_payload["clock_anchor"] = evidence["clock_anchor"]
   867	    evidence_payload["clock_anchor_resolved"] = anchor_resolved
   868	    if not anchor_resolved:
   869	        evidence_payload["status"] = "invalid"
   870	        evidence_payload["reasons"] = sorted(
   871	            set(evidence_payload.get("reasons", [])) | {"clock_anchor_unresolved"}
   872	        )
   873	    (out_dir / "instrument_evidence.json").write_text(
   874	        json.dumps(evidence_payload, indent=2, sort_keys=True) + "\n",
   875	        encoding="utf-8",
   876	    )
   877	    manifest = {
   878	        "schema_version": "joulewise.instrument_validation_manifest.v1",
   879	        "validation_id": validation_id,
   880	        "protocol_id": PROTOCOL_ID,
   881	        "pulse_count": args.pulse_count,
   882	        "artifacts": {
   883	            name: sha256_path(out_dir / name)
   884	            for name in (
   885	                "events.jsonl",
   886	                "power_trace.csv",
   887	                "instrument_evidence.json",
   888	            )
   889	        }
   890	        | {"raw/powermetrics.plist": sha256_path(capture_path)},
   891	    }
   892	    (out_dir / "manifest.json").write_text(
   893	        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
   894	    )
   895	    serialized_evidence = json.loads(
   896	        json.dumps(evidence_payload, sort_keys=True),
   897	        parse_float=str,
   898	        parse_int=str,
   899	    )
   900	    bound_lexeme = serialized_evidence.get("b_fiducial_s")
   901	    ledger_lifecycle.exact_bound_lexeme_s = (
   902	        bound_lexeme if isinstance(bound_lexeme, str) else None
   903	    )
   904	    disposition = "ordinary-invalid"
   905	    if evidence_payload["status"] == "valid":
   906	        disposition = (
   907	            "systematic-invalid"
   908	            if isinstance(bound_lexeme, str)
   909	            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
   910	            else "valid"
   911	        )
   912	    _final_receipt, head_pin_candidate = ledger_lifecycle.finalize(disposition)
   913	    atexit.unregister(finalize_abandoned)
   914	    output = {
   915	        "validation_id": validation_id,
   916	        "status": evidence_payload["status"],
   917	        "b_fiducial_s": evidence_payload["b_fiducial_s"],
   918	        "output": str(out_dir),
   919	        "ledger_head_pin_candidate": head_pin_candidate,
   920	        "claim_evaluation_blocked_until_pin_commit": True,
   921	    }
   922	    if bracket_mode:
   923	        output["bracket_session"] = {
   924	            "session_id": args.session_id,
   925	            "slot": args.slot,
   926	            "attempt_id": args.attempt_id,
   927	        }
   928	    print(json.dumps(output, indent=2))
   929	    return 0 if disposition == "valid" else 1
   930	
   931	
   932	if __name__ == "__main__":
   933	    raise SystemExit(main())

exec
/bin/zsh -lc "nl -ba tests/test_calibration_bracketing.py | sed -n '1078,1155p'; rg -n \"open.*candidate|aborted.*candidate|post_cutoff|governed_open|partial|mid.*pin|terminal_head\" tests/test_calibration_ledger.py tests/test_calibration_bracketing.py tests/test_powermetrics_fiducial.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
  1078	
  1079	    def test_open_and_aborted_session_observations_never_leak_as_candidates(self) -> None:
  1080	        snapshot, candidates, _binding = self._bound_session_fixture()
  1081	        session = snapshot.bracket_sessions[0]
  1082	        open_session = replace(
  1083	            session,
  1084	            state="open",
  1085	            finalized_slots=MappingProxyType({"pre": session.finalized_slots["pre"]}),
  1086	        )
  1087	        open_snapshot = replace(
  1088	            snapshot,
  1089	            observations=tuple(
  1090	                observation
  1091	                for observation in snapshot.observations
  1092	                if observation.bracket_slot != "post"
  1093	            ),
  1094	            bracket_sessions=(open_session,),
  1095	            head_sequence=4,
  1096	            head_digest=session.finalized_slots["pre"].receipt_digest,
  1097	            receipts=(
  1098	                *snapshot.receipts[:2],
  1099	                MappingProxyType(
  1100	                    {
  1101	                        "event": "bracket-session-open",
  1102	                        "session_id": "session-alpha",
  1103	                        "predecessor_digest": snapshot.receipts[1]["receipt_digest"],
  1104	                        "receipt_digest": session.capability_receipt_digest,
  1105	                    }
  1106	                ),
  1107	                MappingProxyType(
  1108	                    {
  1109	                        "event": "bracket-session-slot-finalization",
  1110	                        "session_id": "session-alpha",
  1111	                        "receipt_digest": session.finalized_slots["pre"].receipt_digest,
  1112	                    }
  1113	                ),
  1114	            ),
  1115	            refusal_reasons=(
  1116	                "calibration_ledger_bracket_session_open",
  1117	                "calibration_ledger_head_mismatch",
  1118	            ),
  1119	            committed_head_sequence=2,
  1120	            committed_head_digest=snapshot.receipts[1]["receipt_digest"],
  1121	        )
  1122	        by_attempt = {candidate.attempt_id: candidate for candidate in candidates}
  1123	        with patch(
  1124	            "joulewise.calibration_bracketing._candidate_from_observation",
  1125	            side_effect=lambda observation: by_attempt[observation.attempt_id],
  1126	        ):
  1127	            open_candidates = discover_calibration_candidates(open_snapshot)
  1128	        self.assertEqual(
  1129	            [candidate.bracket_session_id for candidate in open_candidates],
  1130	            [None, None, "session-alpha"],
  1131	        )
  1132	
  1133	        aborted_session = replace(open_session, state="aborted")
  1134	        aborted_snapshot = replace(
  1135	            open_snapshot,
  1136	            observations=tuple(
  1137	                observation
  1138	                for observation in open_snapshot.observations
  1139	                if observation.bracket_session_id is None
  1140	            ),
  1141	            bracket_sessions=(aborted_session,),
  1142	            refusal_reasons=(),
  1143	        )
  1144	        with patch(
  1145	            "joulewise.calibration_bracketing._candidate_from_observation",
  1146	            side_effect=lambda observation: by_attempt[observation.attempt_id],
  1147	        ):
  1148	            discovered = discover_calibration_candidates(aborted_snapshot)
  1149	        self.assertEqual(
  1150	            [candidate.bracket_session_id for candidate in discovered],
  1151	            [None, None],
  1152	        )
  1153	
  1154	    def test_claim_window_passes_and_embeds_never_zero_allowance_once(self) -> None:
  1155	        # Exact H2 defect shape: a single sample maximum used to stand in for
tests/test_powermetrics_fiducial.py:1071:                ledger_module.terminal_head_pin_for_session(
tests/test_calibration_bracketing.py:1079:    def test_open_and_aborted_session_observations_never_leak_as_candidates(self) -> None:
tests/test_calibration_bracketing.py:1127:            open_candidates = discover_calibration_candidates(open_snapshot)
tests/test_calibration_bracketing.py:1129:            [candidate.bracket_session_id for candidate in open_candidates],
tests/test_calibration_ledger.py:59:    terminal_head_pin_for_session,
tests/test_calibration_ledger.py:387:                attempt_id="partial-reservation",
tests/test_calibration_ledger.py:388:                custody_locator=str(self.root / "partial"),
tests/test_calibration_ledger.py:515:        pin = terminal_head_pin_for_session(
tests/test_calibration_ledger.py:569:    def test_open_session_refuses_until_governed_abort_and_never_deletes_partial(
tests/test_calibration_ledger.py:593:            terminal_head_pin_for_session(
tests/test_calibration_ledger.py:661:        self.assertEqual(output["terminal_head_pin"], None)
tests/test_calibration_ledger.py:671:            terminal_head_pin_for_session(
tests/test_calibration_ledger.py:688:            terminal_head_pin_for_session(
tests/test_calibration_ledger.py:1041:        def partial_write_then_fail(handle, raw):
tests/test_calibration_ledger.py:1054:                    side_effect=partial_write_then_fail,
tests/test_calibration_ledger.py:1225:    def test_historical_import_io_failure_rolls_back_partial_append(self) -> None:
tests/test_calibration_ledger.py:1229:        def partial_write_then_fail(handle, payload):
tests/test_calibration_ledger.py:1237:            side_effect=partial_write_then_fail,
tests/test_calibration_ledger.py:1674:    def test_historical_import_marker_is_not_a_post_cutoff_live_observation(
tests/test_calibration_ledger.py:1698:        self.assertEqual(snapshot.post_cutoff_live_observations(0), ())

exec
/bin/zsh -lc "nl -ba tests/test_calibration_bracketing.py | sed -n '330,390p'; nl -ba tests/test_calibration_bracketing.py | sed -n '880,965p'; nl -ba tests/test_calibration_ledger.py | sed -n '430,720p'; nl -ba tests/test_powermetrics_fiducial.py | sed -n '900,1125p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
   330	                t1_bindings=MappingProxyType(
   331	                    {field: candidate.bindings.get(field) for field in V2_BINDING_FIELDS}
   332	                ),
   333	                capture_wall_time_s=str(candidate.capture_wall_time_s),
   334	                exact_bound_lexeme_s=bound,
   335	                disposition="valid",
   336	                custody_locator=candidate.relative_path,
   337	            )
   338	        )
   339	    all_observations = (*observations, *extra_observations)
   340	    return (
   341	        CalibrationLedgerSnapshot(
   342	            ledger_schema=LEDGER_SCHEMA,
   343	            ledger_path=Path("fixture-ledger.jsonl"),
   344	            head_sequence=len(all_observations) * 2,
   345	            head_digest=(
   346	                all_observations[-1].receipt_digest
   347	                if all_observations
   348	                else GENESIS_DIGEST
   349	            ),
   350	            receipts=(),
   351	            observations=tuple(all_observations),
   352	            refusal_reasons=(),
   353	            baseline_sequence=0,
   354	            baseline_digest=GENESIS_DIGEST,
   355	        ),
   356	        normalized,
   357	    )
   358	
   359	
   360	def _evaluate_with_unissued_acceptance(
   361	    candidates: list[CalibrationCandidate] | tuple[CalibrationCandidate, ...],
   362	    **kwargs: object,
   363	) -> tuple[dict, tuple[str, ...]]:
   364	    """Evaluate against the exact genesis fixture, never the live anchor."""
   365	
   366	    with patch(
   367	        "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
   368	        return_value=_unissued_acceptance_fixture(),
   369	    ):
   370	        return _evaluate_calibration_bracket(candidates, **kwargs)
   371	
   372	
   373	def evaluate_calibration_bracket(
   374	    candidates: list[CalibrationCandidate], **kwargs: object
   375	) -> tuple[dict, tuple[str, ...]]:
   376	    snapshot, normalized = _fixture_snapshot(list(candidates))
   377	    return _evaluate_with_unissued_acceptance(
   378	        normalized,
   379	        ledger_snapshot=snapshot,
   380	        _allow_unissued_fixture=True,
   381	        **kwargs,
   382	    )
   383	
   384	
   385	class CalibrationBracketingTests(unittest.TestCase):
   386	    def setUp(self) -> None:
   387	        self.bindings = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
   388	        self.bindings.update(
   389	            {
   390	                "hardware_model": "Mac15,9",
   880	        for name, capture, bound, session_id, slot, sequence in specifications:
   881	            manifest = hashlib.sha256(f"manifest:{name}".encode()).hexdigest()
   882	            evidence = hashlib.sha256(f"evidence:{name}".encode()).hexdigest()
   883	            hashes = {
   884	                "manifest.json": manifest,
   885	                "instrument_evidence.json": evidence,
   886	            }
   887	            content_id = content_id_from_artifact_hashes(hashes)
   888	            receipt_digest = hashlib.sha256(f"receipt:{name}".encode()).hexdigest()
   889	            attempt_id = f"attempt-{name}"
   890	            candidate = replace(
   891	                self.candidate(name, capture, bound),
   892	                manifest_sha256=manifest,
   893	                evidence_sha256=evidence,
   894	                attempt_id=attempt_id,
   895	                content_id=content_id,
   896	                ledger_receipt_digest=receipt_digest,
   897	                bracket_session_id=session_id,
   898	                bracket_slot=slot,
   899	                bracket_window_id="window-alpha" if session_id else None,
   900	                bracket_plan_id="plan-alpha" if session_id else None,
   901	                bracket_plan_sha256="a" * 64 if session_id else None,
   902	                bracket_evidence_root_id="evidence-alpha" if session_id else None,
   903	            )
   904	            candidates.append(candidate)
   905	            observations.append(
   906	                LedgerObservation(
   907	                    sequence=sequence,
   908	                    receipt_digest=receipt_digest,
   909	                    attempt_id=attempt_id,
   910	                    content_id=content_id,
   911	                    artifact_sha256=MappingProxyType(hashes),
   912	                    identity_epoch=MappingProxyType(
   913	                        {
   914	                            field: self.bindings[field]
   915	                            for field in (
   916	                                "os_build",
   917	                                "hardware_model",
   918	                                "power_policy",
   919	                                "sampling_interval_ms",
   920	                                "estimator_revision",
   921	                                "pulse_protocol_id",
   922	                            )
   923	                        }
   924	                    ),
   925	                    t1_bindings=MappingProxyType(dict(self.bindings)),
   926	                    capture_wall_time_s=str(capture),
   927	                    exact_bound_lexeme_s=bound,
   928	                    disposition="valid",
   929	                    custody_locator=f"/synthetic/{name}",
   930	                    observation_kind=(
   931	                        "bracket-session-finalized" if session_id else "live-capture"
   932	                    ),
   933	                    bracket_session_id=session_id,
   934	                    bracket_slot=slot,
   935	                    bracket_window_id="window-alpha" if session_id else None,
   936	                    bracket_plan_id="plan-alpha" if session_id else None,
   937	                    bracket_plan_sha256="a" * 64 if session_id else None,
   938	                    bracket_evidence_root_id="evidence-alpha" if session_id else None,
   939	                )
   940	            )
   941	        by_slot = {
   942	            observation.bracket_slot: observation
   943	            for observation in observations
   944	            if observation.bracket_slot is not None
   945	        }
   946	        capability_digest = hashlib.sha256(b"capability-alpha").hexdigest()
   947	        session = CalibrationBracketSession(
   948	            session_id="session-alpha",
   949	            window_id="window-alpha",
   950	            plan_id="plan-alpha",
   951	            plan_sha256="a" * 64,
   952	            evidence_root_id="evidence-alpha",
   953	            capability_receipt_digest=capability_digest,
   954	            capability_sequence=3,
   955	            slot_attempt_ids=MappingProxyType(
   956	                {slot: observation.attempt_id for slot, observation in by_slot.items()}
   957	            ),
   958	            state="finalized",
   959	            finalized_slots=MappingProxyType(by_slot),
   960	        )
   961	        receipt_digests = [
   962	            observations[0].receipt_digest,
   963	            observations[1].receipt_digest,
   964	            capability_digest,
   965	            by_slot["pre"].receipt_digest,
   430	        self.assertIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)
   431	
   432	    def test_true_sibling_fork_refuses_on_predecessor_conflict(self) -> None:
   433	        custody = self._custody("fork")
   434	        first = self._reserve("fork", custody)
   435	        final = self._finalize("fork", custody)
   436	        sibling = {
   437	            **dict(first),
   438	            "sequence": 3,
   439	            "predecessor_digest": first["receipt_digest"],
   440	            "attempt_id": "fork-sibling",
   441	            "custody_locator": str(self.root / "fork-sibling"),
   442	        }
   443	        sibling["receipt_digest"] = canonical_sha256(
   444	            {key: value for key, value in sibling.items() if key != "receipt_digest"}
   445	        )
   446	        with self.ledger.open("ab") as handle:
   447	            handle.write(canonical_json_bytes(sibling) + b"\n")
   448	        self._write_pin(head_pin_for_receipt(sibling))
   449	        snapshot = self._snapshot(verify_custody=False)
   450	        self.assertIn("calibration_ledger_chain_conflict", snapshot.refusal_reasons)
   451	        self.assertNotIn(
   452	            "calibration_ledger_attempt_conflict", snapshot.refusal_reasons
   453	        )
   454	        self.assertNotIn("calibration_ledger_head_mismatch", snapshot.refusal_reasons)
   455	        self.assertEqual(sibling["receipt_digest"], snapshot.head_digest)
   456	        self.assertNotEqual(final["receipt_digest"], sibling["receipt_digest"])
   457	
   458	    def test_content_bearing_abandoned_receipt_is_unresolved_evidence(self) -> None:
   459	        custody = self._custody("abandoned-content")
   460	        self._reserve("abandoned-content", custody)
   461	        final = self._finalize(
   462	            "abandoned-content", custody, disposition="abandoned"
   463	        )
   464	        self._write_pin(head_pin_for_receipt(final))
   465	        snapshot = self._snapshot()
   466	        observation = snapshot.observation_by_attempt["abandoned-content"]
   467	        self.assertIsNotNone(observation.content_id)
   468	        self.assertEqual(observation.disposition, "abandoned")
   469	        self.assertEqual(observation.classification_disposition, "unresolved")
   470	
   471	    def test_finalization_is_single_transition(self) -> None:
   472	        custody = self._custody("single")
   473	        self._reserve("single", custody)
   474	        self._finalize("single", custody)
   475	        with self.assertRaisesRegex(CalibrationLedgerError, "uniquely pending"):
   476	            self._finalize("single", custody)
   477	
   478	    def test_missing_or_changed_custody_bytes_refuse(self) -> None:
   479	        custody = self._custody("custody")
   480	        self._reserve("custody", custody)
   481	        final = self._finalize("custody", custody)
   482	        self._write_pin(head_pin_for_receipt(final))
   483	        (custody / "instrument_evidence.json").write_text("changed\n")
   484	        snapshot = self._snapshot()
   485	        self.assertEqual(
   486	            snapshot.refusal_reasons,
   487	            ("calibration_ledger_custody_invalid",),
   488	        )
   489	
   490	    def test_baseline_must_be_exact_member_of_current_chain(self) -> None:
   491	        snapshot = load_calibration_ledger_snapshot(
   492	            self.ledger,
   493	            self.pin,
   494	            baseline_sequence=1,
   495	            baseline_digest="f" * 64,
   496	            require_committed_pin=False,
   497	        )
   498	        self.assertIn("calibration_ledger_baseline_missing", snapshot.refusal_reasons)
   499	
   500	    def test_bracket_session_happy_path_reserves_two_slots_under_one_pin(self) -> None:
   501	        capability = self._open_bracket_session()
   502	        self.assertEqual(capability["sequence"], 1)
   503	        self.assertEqual(tuple(capability["slots"]), ("pre", "post"))
   504	        self.assertEqual(
   505	            {slot["expected_time_role"] for slot in capability["slots"].values()},
   506	            {"pre", "post"},
   507	        )
   508	
   509	        pre = self._finalize_bracket_slot("session-alpha", "pre")
   510	        self.assertEqual(pre["sequence"], 2)
   511	        self.assertEqual(pre["event"], BRACKET_SESSION_FINALIZATION_EVENT)
   512	        post = self._finalize_bracket_slot("session-alpha", "post")
   513	        self.assertEqual(post["sequence"], 3)
   514	
   515	        pin = terminal_head_pin_for_session(
   516	            self.ledger, session_id="session-alpha"
   517	        )
   518	        self.assertEqual(pin, head_pin_for_receipt(post))
   519	        self._write_pin(pin)
   520	        snapshot = self._snapshot()
   521	        self.assertEqual(snapshot.refusal_reasons, ())
   522	        self.assertEqual(snapshot.head_sequence, 3)
   523	        self.assertEqual(
   524	            [observation.bracket_slot for observation in snapshot.observations],
   525	            ["pre", "post"],
   526	        )
   527	        session = snapshot.bracket_session_by_id["session-alpha"]
   528	        self.assertEqual(session.state, "finalized")
   529	        self.assertEqual(set(session.finalized_slots), {"pre", "post"})
   530	
   531	    def test_bracket_session_refuses_reordered_duplicate_and_conflicting_slots(
   532	        self,
   533	    ) -> None:
   534	        self._open_bracket_session()
   535	        post_custody = self._custody("session-alpha-post")
   536	        with self.assertRaisesRegex(CalibrationLedgerError, "expected pre"):
   537	            finalize_bracket_session_slot(
   538	                self.ledger,
   539	                session_id="session-alpha",
   540	                slot="post",
   541	                disposition="valid",
   542	                custody_locator=str(post_custody),
   543	                artifact_sha256=artifact_hashes(post_custody),
   544	                identity_epoch=self.epoch,
   545	                t1_bindings=self.t1,
   546	                capture_wall_time_s="111.0",
   547	                exact_bound_lexeme_s="0.025",
   548	            )
   549	        self._finalize_bracket_slot("session-alpha", "pre")
   550	        with self.assertRaisesRegex(CalibrationLedgerError, "expected post"):
   551	            self._finalize_bracket_slot("session-alpha", "pre")
   552	
   553	        conflicting_t1 = dict(self.t1)
   554	        conflicting_t1["power_policy"] = "battery"
   555	        with self.assertRaisesRegex(CalibrationLedgerError, "reserved session binding"):
   556	            finalize_bracket_session_slot(
   557	                self.ledger,
   558	                session_id="session-alpha",
   559	                slot="post",
   560	                disposition="valid",
   561	                custody_locator=str(post_custody),
   562	                artifact_sha256=artifact_hashes(post_custody),
   563	                identity_epoch=self.epoch,
   564	                t1_bindings=conflicting_t1,
   565	                capture_wall_time_s="111.0",
   566	                exact_bound_lexeme_s="0.025",
   567	            )
   568	
   569	    def test_open_session_refuses_until_governed_abort_and_never_deletes_partial(
   570	        self,
   571	    ) -> None:
   572	        self._open_bracket_session()
   573	        pre = self._finalize_bracket_slot("session-alpha", "pre")
   574	        open_snapshot = self._snapshot()
   575	        self.assertIn(
   576	            "calibration_ledger_bracket_session_open",
   577	            open_snapshot.refusal_reasons,
   578	        )
   579	        self.assertEqual(
   580	            [observation.bracket_slot for observation in open_snapshot.observations],
   581	            ["pre"],
   582	        )
   583	
   584	        closure = abort_bracket_session(
   585	            self.ledger,
   586	            session_id="session-alpha",
   587	            reason="science_member_failed_before_post",
   588	        )
   589	        self.assertEqual(closure["event"], BRACKET_SESSION_ABORT_EVENT)
   590	        self.assertEqual(closure["finalized_slots"], ("pre",))
   591	        self.assertEqual(closure["unused_slots"], ("post",))
   592	        self._write_pin(
   593	            terminal_head_pin_for_session(
   594	                self.ledger, session_id="session-alpha"
   595	            )
   596	        )
   597	        snapshot = self._snapshot()
   598	        self.assertEqual(snapshot.refusal_reasons, ())
   599	        self.assertEqual(snapshot.observations, ())
   600	        session = snapshot.bracket_session_by_id["session-alpha"]
   601	        self.assertEqual(session.state, "aborted")
   602	        self.assertEqual(session.finalized_slots["pre"].receipt_digest, pre["receipt_digest"])
   603	        with self.assertRaisesRegex(CalibrationLedgerError, "not open"):
   604	            abort_bracket_session(
   605	                self.ledger,
   606	                session_id="session-alpha",
   607	                reason="duplicate closure",
   608	            )
   609	
   610	    def test_bracket_session_open_requires_exact_committed_physical_head(self) -> None:
   611	        self._open_bracket_session()
   612	        with self.assertRaisesRegex(
   613	            CalibrationLedgerError, "physical ledger head differs from the committed pin"
   614	        ):
   615	            self._open_bracket_session("session-beta")
   616	
   617	    def test_bracket_reservation_cli_is_explicit_and_machine_readable(self) -> None:
   618	        epoch_path = self.root / "epoch.json"
   619	        t1_path = self.root / "t1.json"
   620	        epoch_path.write_text(json.dumps(self.epoch), encoding="utf-8")
   621	        t1_path.write_text(json.dumps(self.t1), encoding="utf-8")
   622	        argv = [
   623	            "--ledger",
   624	            str(self.ledger),
   625	            "--head-pin",
   626	            str(self.pin),
   627	            "--session-id",
   628	            "session-cli",
   629	            "--window-id",
   630	            "window-cli",
   631	            "--plan-id",
   632	            "plan-cli",
   633	            "--plan-sha256",
   634	            "b" * 64,
   635	            "--evidence-root-id",
   636	            "evidence-cli",
   637	            "--pre-attempt-id",
   638	            "session-cli-pre",
   639	            "--post-attempt-id",
   640	            "session-cli-post",
   641	            "--pre-custody-locator",
   642	            str(self.root / "session-cli-pre"),
   643	            "--post-custody-locator",
   644	            str(self.root / "session-cli-post"),
   645	            "--identity-epoch-json",
   646	            str(epoch_path),
   647	            "--t1-bindings-json",
   648	            str(t1_path),
   649	            "--allow-uncommitted-pin-for-test",
   650	        ]
   651	        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
   652	            self.assertEqual(bracket_session_cli.main(argv), 0)
   653	        self.assertEqual(json.loads(stdout.getvalue())["status"], "validated_not_reserved")
   654	        self.assertFalse(self.ledger.exists())
   655	
   656	        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
   657	            self.assertEqual(bracket_session_cli.main([*argv, "--execute"]), 0)
   658	        output = json.loads(stdout.getvalue())
   659	        self.assertEqual(output["status"], "reserved")
   660	        self.assertEqual(output["receipt"]["event"], "bracket-session-open")
   661	        self.assertEqual(output["terminal_head_pin"], None)
   662	        self.assertTrue(self.ledger.is_file())
   663	
   664	    def test_terminal_session_head_refuses_rollback_and_nonterminal_extension(self) -> None:
   665	        self._open_bracket_session()
   666	        self._finalize_bracket_slot("session-alpha", "pre")
   667	        post = self._finalize_bracket_slot("session-alpha", "post")
   668	        lines = self.ledger.read_bytes().splitlines(keepends=True)
   669	        self.ledger.write_bytes(b"".join(lines[:-1]))
   670	        with self.assertRaisesRegex(CalibrationLedgerError, "open"):
   671	            terminal_head_pin_for_session(
   672	                self.ledger, session_id="session-alpha"
   673	            )
   674	        self.ledger.write_bytes(b"".join(lines))
   675	        self._write_pin(head_pin_for_receipt(post))
   676	        ordinary_custody = self._custody("later-ordinary")
   677	        pending = append_pending_receipt(
   678	            self.ledger,
   679	            attempt_id="later-ordinary",
   680	            custody_locator=str(ordinary_custody),
   681	            identity_epoch=self.epoch,
   682	            t1_bindings=self.t1,
   683	            head_pin_path=self.pin,
   684	            require_committed_pin=False,
   685	        )
   686	        self.assertEqual(pending["sequence"], 4)
   687	        with self.assertRaisesRegex(CalibrationLedgerError, "pending"):
   688	            terminal_head_pin_for_session(
   689	                self.ledger, session_id="session-alpha"
   690	            )
   691	
   692	    def test_conflicting_session_identity_and_session_fork_refuse(self) -> None:
   693	        self._open_bracket_session()
   694	        self._finalize_bracket_slot("session-alpha", "pre")
   695	        post = self._finalize_bracket_slot("session-alpha", "post")
   696	        clean_lines = self.ledger.read_bytes().splitlines(keepends=True)
   697	
   698	        conflicting = json.loads(clean_lines[-1])
   699	        conflicting["window_id"] = "window-substituted"
   700	        conflicting["receipt_digest"] = canonical_sha256(
   701	            {
   702	                key: value
   703	                for key, value in conflicting.items()
   704	                if key != "receipt_digest"
   705	            }
   706	        )
   707	        self.ledger.write_bytes(
   708	            b"".join(clean_lines[:-1]) + canonical_json_bytes(conflicting) + b"\n"
   709	        )
   710	        self._write_pin(head_pin_for_receipt(conflicting))
   711	        conflict_snapshot = self._snapshot(verify_custody=False)
   712	        self.assertIn(
   713	            "calibration_ledger_bracket_session_conflict",
   714	            conflict_snapshot.refusal_reasons,
   715	        )
   716	
   717	        forked = json.loads(clean_lines[-1])
   718	        forked["predecessor_digest"] = json.loads(clean_lines[0])[
   719	            "receipt_digest"
   720	        ]
   900	                    "parse_powermetrics_records",
   901	                    return_value=records,
   902	                ),
   903	                patch.object(
   904	                    validation_script.time,
   905	                    "monotonic",
   906	                    side_effect=[0.0, 0.1, 1.0],
   907	                ),
   908	                patch.object(validation_script.time, "sleep"),
   909	            ):
   910	                with self.assertRaisesRegex(
   911	                    RuntimeError,
   912	                    validation_script.ROLLOVER_GATE_TIMEOUT_REASON,
   913	                ):
   914	                    validation_script.wait_for_preworkload_rollover(
   915	                        capture,
   916	                        process,
   917	                        timeout_s=0.5,
   918	                    )
   919	            self.assertTrue(process.terminated)
   920	            self.assertFalse(artifact.exists())
   921	            self.assertIn(
   922	                validation_script.ROLLOVER_GATE_TIMEOUT_REASON,
   923	                __import__(
   924	                    "joulewise.analysis_engine.claims",
   925	                    fromlist=["REDUCER_REASON_CODES"],
   926	                ).REDUCER_REASON_CODES,
   927	            )
   928	
   929	
   930	class WriterLedgerIntegrationTests(unittest.TestCase):
   931	    def _open_session(self, root: Path):
   932	        ledger = root / "ledger.jsonl"
   933	        pin = root / "head.json"
   934	        pin.write_text(
   935	            json.dumps(
   936	                {
   937	                    "sequence": 0,
   938	                    "head_digest": ledger_module.GENESIS_DIGEST,
   939	                    "ledger_schema": ledger_module.LEDGER_SCHEMA,
   940	                }
   941	            )
   942	            + "\n",
   943	            encoding="utf-8",
   944	        )
   945	        epoch = {
   946	            "os_build": "25F84",
   947	            "hardware_model": "Mac15,9",
   948	            "power_policy": "ac_high_power",
   949	            "sampling_interval_ms": 100,
   950	            "estimator_revision": RESIDUAL_REGION_METHOD,
   951	            "pulse_protocol_id": PROTOCOL_ID,
   952	        }
   953	        t1 = {field: f"value-{field}" for field in ledger_module.T1_FIELDS}
   954	        t1.update(epoch)
   955	        custody = {
   956	            slot: root / "instrument_validation" / f"session-writer-{slot}"
   957	            for slot in ledger_module.BRACKET_SESSION_SLOTS
   958	        }
   959	        receipt = ledger_module.append_bracket_session_receipt(
   960	            ledger,
   961	            session_id="session-writer",
   962	            window_id="window-writer",
   963	            plan_id="plan-writer",
   964	            plan_sha256="a" * 64,
   965	            evidence_root_id="evidence-writer",
   966	            slots={
   967	                slot: {
   968	                    "attempt_id": f"session-writer-{slot}",
   969	                    "custody_locator": str(custody[slot]),
   970	                    "identity_epoch": epoch,
   971	                    "t1_bindings": t1,
   972	                }
   973	                for slot in ledger_module.BRACKET_SESSION_SLOTS
   974	            },
   975	            head_pin_path=pin,
   976	            require_committed_pin=False,
   977	        )
   978	        return ledger, pin, epoch, t1, custody, receipt
   979	
   980	    def _lifecycle(
   981	        self,
   982	        ledger: Path,
   983	        pin: Path,
   984	        epoch: dict,
   985	        t1: dict,
   986	        custody: dict[str, Path],
   987	        slot: str,
   988	    ) -> validation_script._CaptureLedgerLifecycle:
   989	        return validation_script._CaptureLedgerLifecycle(
   990	            ledger_path=ledger,
   991	            head_pin_path=pin,
   992	            attempt_id=f"session-writer-{slot}",
   993	            custody_locator=str(custody[slot]),
   994	            identity_epoch=epoch,
   995	            t1_bindings=t1,
   996	            session_id="session-writer",
   997	            slot=slot,
   998	            require_committed_pin=False,
   999	        )
  1000	
  1001	    def test_session_writer_authenticates_reservation_before_capture_without_ordinary_append(
  1002	        self,
  1003	    ) -> None:
  1004	        with tempfile.TemporaryDirectory() as tmp:
  1005	            ledger, pin, epoch, t1, custody, capability = self._open_session(
  1006	                Path(tmp)
  1007	            )
  1008	            lifecycle = self._lifecycle(
  1009	                ledger, pin, epoch, t1, custody, "pre"
  1010	            )
  1011	            with patch.object(validation_script, "append_pending_receipt") as ordinary:
  1012	                lifecycle.begin()
  1013	            ordinary.assert_not_called()
  1014	            receipts = [json.loads(line) for line in ledger.read_text().splitlines()]
  1015	            self.assertEqual(receipts, [capability])
  1016	            self.assertFalse(custody["pre"].exists())
  1017	
  1018	            mismatched = validation_script._CaptureLedgerLifecycle(
  1019	                ledger_path=ledger,
  1020	                head_pin_path=pin,
  1021	                attempt_id="not-the-reserved-attempt",
  1022	                custody_locator=str(custody["pre"]),
  1023	                identity_epoch=epoch,
  1024	                t1_bindings=t1,
  1025	                session_id="session-writer",
  1026	                slot="pre",
  1027	                require_committed_pin=False,
  1028	            )
  1029	            with self.assertRaisesRegex(
  1030	                ledger_module.CalibrationLedgerError, "exact reserved"
  1031	            ):
  1032	                mismatched.begin()
  1033	            self.assertEqual(len(ledger.read_text().splitlines()), 1)
  1034	
  1035	    def test_session_writer_crash_aborts_exact_remaining_slot(self) -> None:
  1036	        with tempfile.TemporaryDirectory() as tmp:
  1037	            ledger, pin, epoch, t1, custody, _capability = self._open_session(
  1038	                Path(tmp)
  1039	            )
  1040	            pre = self._lifecycle(ledger, pin, epoch, t1, custody, "pre")
  1041	            with (
  1042	                patch.object(validation_script, "append_pending_receipt") as reserve,
  1043	                patch.object(validation_script, "finalize_attempt_receipt") as ordinary,
  1044	            ):
  1045	                pre.begin()
  1046	                (custody["pre"] / "raw").mkdir(parents=True)
  1047	                (custody["pre"] / "raw" / "powermetrics.plist").write_bytes(
  1048	                    b"raw"
  1049	                )
  1050	                (custody["pre"] / "events.jsonl").write_text("{}\n")
  1051	                (custody["pre"] / "power_trace.csv").write_text("header\n")
  1052	                (custody["pre"] / "instrument_evidence.json").write_text("{}\n")
  1053	                (custody["pre"] / "manifest.json").write_text("{}\n")
  1054	                pre.capture_wall_time_s = "99.0"
  1055	                pre.exact_bound_lexeme_s = "0.025"
  1056	                _pre_receipt, pre_head = pre.finalize("valid")
  1057	                self.assertIsNone(pre_head)
  1058	
  1059	                post = self._lifecycle(ledger, pin, epoch, t1, custody, "post")
  1060	                post.begin()
  1061	                abort = post.abandon("simulated_writer_crash")
  1062	            reserve.assert_not_called()
  1063	            ordinary.assert_not_called()
  1064	            self.assertIsNotNone(abort)
  1065	            self.assertEqual(abort["event"], ledger_module.BRACKET_SESSION_ABORT_EVENT)
  1066	            self.assertEqual(abort["session_id"], "session-writer")
  1067	            self.assertEqual(tuple(abort["finalized_slots"]), ("pre",))
  1068	            self.assertEqual(tuple(abort["unused_slots"]), ("post",))
  1069	            self.assertEqual(abort["reason"], "simulated_writer_crash")
  1070	            self.assertEqual(
  1071	                ledger_module.terminal_head_pin_for_session(
  1072	                    ledger, session_id="session-writer"
  1073	                )["sequence"],
  1074	                3,
  1075	            )
  1076	
  1077	
  1078	if __name__ == "__main__":
  1079	    unittest.main()

exec
/bin/zsh -lc "nl -ba docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md | sed -n '1,190p'; nl -ba docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md | sed -n '250,410p'; nl -ba docs/process_traces/2026-08-07-d117-plan-freeze/RATIFICATION.md; nl -ba docs/decision_log.md | sed -n '6987,7068p'; nl -ba docs/decision_log.md | sed -n '7488,7512p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
     1	```json
     2	{
     3	  "schema": "claude-codex-report/v1",
     4	  "genre": "review",
     5	  "status": "findings",
     6	  "completion": "complete",
     7	  "summary": "Complete D-117 freeze design: three prospective windows fit the envelope, but live-ledger sessions, multi-cell minting, and D-102 successor generation must land before any arm.",
     8	  "workspace": {
     9	    "base_requested": null,
    10	    "base_mode": "informational",
    11	    "head_start": "dbb9685669ac76ea65bf458b78eeb98d94bc6a80",
    12	    "head_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    13	    "upstream_end": "94a24e562290b59f7b40908315bbae7a032ea47e",
    14	    "branch": "main"
    15	  },
    16	  "pathspec": [],
    17	  "unowned_dirty": [],
    18	  "verdict": {
    19	    "findings": [
    20	      {
    21	        "id": "F1",
    22	        "severity": "blocker",
    23	        "title": "The current ledger cannot safely reserve both bookend observations under one unchanged committed head",
    24	        "detail": "The append path requires the physical ledger head to equal the committed pin before each reservation. Finalizing the pre observation advances the physical head, so an ordinary post reservation cannot occur without an intervening pin advance or a new bracket-session capability.",
    25	        "recommendation": "Implement an atomic two-slot bracket-session capability plus exact postcollection bracket binding before freezing arm packets."
    26	      },
    27	      {
    28	        "id": "F2",
    29	        "severity": "blocker",
    30	        "title": "The generalized mint is still decode-only and single-plan/single-cell",
    31	        "detail": "The current generalized path hard-checks phase_energy_j.decode and a decode phase target. It cannot mint the two prefill riders or D-095's required combined multi-cell, multi-plan floor artifact.",
    32	        "recommendation": "Introduce pinset v2 with per-plan component pins and an aggregate four-cell artifact pinset."
    33	      },
    34	      {
    35	        "id": "F3",
    36	        "severity": "blocker",
    37	        "title": "No usable D-102 successor-artifact path exists for a live-prefixed ledger",
    38	        "detail": "The issued acceptance artifact is exact-byte pinned and prior-set verification assumes the issuance corpus. A valid range-expanding live observation could therefore stop a campaign before member one or prevent its verdict.",
    39	        "recommendation": "Pre-build and cold-gate a deterministic successor builder, registry, live-prefix verification, and trigger-time operator procedure."
    40	      },
    41	      {
    42	        "id": "F4",
    43	        "severity": "should_fix",
    44	        "title": "The referenced prefill-feasibility synthesis is absent at the inspected HEAD",
    45	        "detail": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md does not exist in this worktree even though RUN_STATE says the trace was custodied.",
    46	        "recommendation": "Recover or commit the trace before lead ratification; this memo uses D-117's adopted summary as authority."
    47	      },
    48	      {
    49	        "id": "F5",
    50	        "severity": "should_fix",
    51	        "title": "Current queue rows still encode superseded C/D and D-110 gates",
    52	        "detail": "TASK_QUEUE.md still presents MET-WINDOW-C-01 and MINT-GENERALIZE-01 under terminology and blockers superseded by D-117.",
    53	        "recommendation": "Regenerate queue/state views from the owning state kernel after the plan-freeze decision is ratified."
    54	      }
    55	    ]
    56	  },
    57	  "verification": [
    58	    {
    59	      "id": "V1",
    60	      "kind": "inspection",
    61	      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse '@{upstream}'",
    62	      "cwd": ".",
    63	      "observed": {
    64	        "result": "pass",
    65	        "exit_code": 0,
    66	        "tail": [
    67	          "## main...origin/main",
    68	          "94a24e562290b59f7b40908315bbae7a032ea47e",
    69	          "94a24e562290b59f7b40908315bbae7a032ea47e"
    70	        ]
    71	      },
    72	      "expected": {
    73	        "exit_code": 0,
    74	        "tail_regex": "94a24e562290b59f7b40908315bbae7a032ea47e$"
    75	      }
    76	    },
    77	    {
    78	      "id": "V2",
    79	      "kind": "inspection",
    80	      "cmd": "test -f docs/decision_log.md && test -f docs/process_traces/2026-08-06-d110-remint-fork/CONSULT-RESPONSE.md && test ! -e docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md",
    81	      "cwd": ".",
    82	      "observed": {
    83	        "result": "pass",
    84	        "exit_code": 0,
    85	        "tail": []
    86	      },
    87	      "expected": {
    88	        "exit_code": 0,
    89	        "tail_regex": "^$"
    90	      }
    91	    }
    92	  ],
    93	  "flags": [
    94	    {
    95	      "id": "FLAG1",
    96	      "kind": "baseline_drift",
    97	      "level": "nonblocking",
    98	      "text": "main advanced concurrently from dbb9685 to 94a24e5 during the read-only consult; the final state was re-inspected and remained clean.",
    99	      "needs": "Freeze implementation scopes against 94a24e5 or a later explicitly reviewed head."
   100	    },
   101	    {
   102	      "id": "FLAG2",
   103	      "kind": "verification_gap",
   104	      "level": "nonblocking",
   105	      "text": "No suites were run because this was a read-only design consult with no implementation.",
   106	      "needs": "Each implementation unit below carries focused and canonical-suite obligations."
   107	    }
   108	  ]
   109	}
   110	```
   111	
   112	## Findings
   113	
   114	### F1 — Live-ledger bookending is not yet armable (blocker)
   115	
   116	D-116’s issued ledger is the correct trust root, and D-117 correctly requires fresh live pre/post observations. The obstacle is mechanical: the present append path requires the physical ledger head to match the committed pin when reserving an attempt. Once the pre observation is finalized, that equality no longer holds for an ordinary post reservation.
   117	
   118	The best design is an atomic `calibration_window_bracket_session.v1` capability:
   119	
   120	1. At the pre-bookend, under a clean committed head, append one receipt reserving exactly two immutable slots: `pre` and `post`, each with its attempt ID, plan ID/SHA, evidence-root ID, expected time role, and shared session ID.
   121	2. Finalize the pre slot before member one.
   122	3. Leave the post slot prospectively open without treating it as an unresolved candidate or permitting claim evaluation.
   123	4. Finalize or explicitly abort the post slot at the closing bookend.
   124	5. Commit the terminal ledger head once, then issue an exact `calibration_bracket_binding.v1` mapping the frozen plan and evidence root to the two finalized content/receipt digests.
   125	6. Candidate discovery still examines the complete live candidate universe; the binding selects the claimed pair but cannot hide extra candidates.
   126	
   127	This is preferable to a source commit after the pre observation: that would mutate the repository and readiness head inside every quiet-window procedure. Two ordinary reservations appended in advance are also inferior because the outstanding post reservation would look unresolved unless ledger semantics were widened anyway.
   128	
   129	Base plans should freeze calibration retry count at zero. A failed pre observation aborts before member one and closes the unused post slot; a failed post makes the physical attempt non-claim-bearing. If the lead wants one cause-removal retry, the session capability needs additional prospectively numbered slots and deterministic selection semantics before freeze—never an improvised retry.
   130	
   131	Ideal no-failure receipt evolution from the issued sequence-76 head is three receipts per window—session capability, pre finalization, post finalization—ending at sequence 85 after all three windows. Exact sequence numbers are arm-time facts, not desk-frozen plan literals.
   132	
   133	### F2 — The mint path needs a real v2, not another widened literal list (blocker)
   134	
   135	The current mechanism is `scripts/floor_mint_pinsets/mint1.json` plus `scripts/mint_floor_artifact_generalized.py`. It already embodies the right principle—plans supply hard pins and the mint compares rather than derives—but it remains structurally limited:
   136	
   137	- one plan and one artifact cell;
   138	- `phase_energy_j.decode` only;
   139	- `["phase","decode"]` only;
   140	- no aggregate artifact over independently collected plans.
   141	
   142	D-095 requires one multi-cell floor artifact whose 1.5B and 7B cells remain independently stack-scoped. D-117 adds prefill cells to both floor plans. The correct closure is therefore one four-cell artifact, not two loosely associated artifacts:
   143	
   144	| Cell | Producer | Metric | Scientific family |
   145	|---|---|---|---|
   146	| 1.5B decode | 1.5B floor plan | `phase_energy_j.decode` | existing `df-ph-decode` |
   147	| 1.5B prefill rider | 1.5B floor plan | `phase_energy_j.prefill` | new exact rider family |
   148	| 7B decode | 7B floor plan | `phase_energy_j.decode` | D-085 `df-ph-decode-qwen25-7b` |
   149	| 7B prefill rider | 7B floor plan | `phase_energy_j.prefill` | new exact rider family |
   150	
   151	Each producer gets a component pinset; an aggregate pinset hard-checks both components and mints `d117-qwen25-phase-floor-set-v1`. Gamma consumes the two decode cells through D-095’s predeclared transport groups. It does not relabel contrast configs as floor configs.
   152	
   153	### F3 — The D-102 successor packet is a pre-arm dependency (blocker)
   154	
   155	A valid pre calibration can expand the observed range or approach the valid-observation limit. The issued artifact cannot absorb that live prefix today. The campaign therefore needs the following on disk and cold-gated before its first §5A arm:
   156	
   157	- deterministic successor builder and validator;
   158	- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
   159	- generalized prior-set validation over a complete authenticated import-plus-live prefix;
   160	- exact Decimal arithmetic, rounding, budget, prediction, and screen reproduction from D-079;
   161	- a dry-run fixture that produces exact successor bytes and expected head pin;
   162	- trigger-disposition logic that judges the range-expanding observation under the prior artifact before incorporating it into the successor;
   163	- operator commands for pre-trigger and post-trigger branches.
   164	
   165	I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.
   166	
   167	At the pre bookend, a range expansion stops the chain before member one: close or preserve the bracket session according to the frozen state machine, commit the current ledger head, build and authenticate the successor, revalidate, then proceed. A post range expansion follows the same process after science but before the verdict. Systematic mismatch is a refusal, never something a successor can launder.
   168	
   169	### F4 — Referenced trace missing (should-fix)
   170	
   171	The named `docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md` is absent at `94a24e5`. D-117 itself records the adopted conclusion, so this memo treats the following as governing:
   172	
   173	- floor prefill cells ride the floor-window decode members;
   174	- gamma remains decode-only;
   175	- the historical 128-token prefill contrast was marginal;
   176	- a prospectively frozen 256-token contrast remains Ed’s option.
   177	
   178	The missing trace prevents verification of any additional numerical assumptions it may contain. In particular, this memo does not freeze a 256-token runtime or effect-size target.
   179	
   180	### F5 — Queue terminology is superseded (should-fix)
   181	
   182	`TASK_QUEUE.md` still carries `MET-WINDOW-C-01`, prospective “C/D” splitting, and an old `MINT-GENERALIZE-01` D-110 blocker. Those rows cannot govern this work. D-117 clause 5 owns the namespace, and the live `RUN_STATE.md` block now recognizes that ruling. The queue should be regenerated after ratification, not manually interpreted during arm readiness.
   183	
   184	### Ranked design decisions and rejected alternatives
   185	
   186	1. **Use a two-slot ledger session capability and exact bracket binding.** Rejected: implicit reuse of neighboring observations, mid-window Git pin commits, or pre-reserving ordinary unresolved observations.
   187	
   188	2. **Mint one four-cell floor artifact through pinset v2.** Rejected: two unrelated floor artifacts, summing arm floors, or weakening D-095’s independently stack-scoped maximum.
   189	
   190	3. **Freeze zero calibration retries in the base plans.** Rejected: unbounded cause-removal retries and post hoc choice among observations. A retry-enabled variant requires a different capability state machine before freeze.
   250	| Start references | 3 | Frozen triplet |
   251	| Absolute floor | 10 | `abs-r01` through `abs-r10` |
   252	| Null half 1 | 20 | ABBA blocks 1–5 |
   253	| Midpoint reference | 1 | Frozen midpoint |
   254	| Null half 2 | 20 | ABBA blocks 6–10 |
   255	| End references | 3 | Frozen triplet |
   256	| Post calibration | 1 live observation | Finalize reserved `post` slot |
   257	| Closeout | 0 science members | Terminal head pin, bracket binding, verdict, dual-root backup |
   258	
   259	Science count is 50; operational captures are 12 bound, 7 references, and 2 calibrations. The prefill rider adds no member and no runtime.
   260	
   261	The rider is a new condition family over the same 128-prompt/512-output decode bundles. It must pre-register `phase_energy_j.prefill`, phase precheck `["phase","prefill"]`, exact tokenizer/model/config identity, the same ten absolute members and forty null members, its estimator, n=10 block basis, and both absolute and comparative floor rules. It is not the old dedicated prefill condition.
   262	
   263	The extraction spec contains four cells: decode absolute, decode comparative, prefill absolute, and prefill comparative. It names 100 cell-member references but exactly 50 unique bundles. Each cell supplies an exact member list, config hash list, expected n, condition-family hash, metric key, phase precheck, order-manifest pin, calibration basis, and evidence-root ID. Missing prefill phases, fallback values, or member discovery outside the list are fatal.
   264	
   265	#### Beta — 7B decode floor plus prefill rider
   266	
   267	The schedule is identical to alpha: pre calibration; 12 NEG8; start 3; absolute 10; ABBA blocks 1–5; midpoint 1; blocks 6–10; end 3; post calibration.
   268	
   269	The decode condition remains D-085’s `df-ph-decode-qwen25-7b`; the fresh plan does not rename settled scientific semantics. The new prefill-rider family pins `phase_energy_j.prefill` over the exact 7B decode members and stack revision.
   270	
   271	Its extraction contract is the same four-cell/50-unique-bundle shape as alpha. Old 7B values—absolute 6.294380… J and comparative 13.998036… J—are budget/design diagnostics only and are not pre-registered pins.
   272	
   273	#### Gamma — 1.5B-versus-7B decode contrast
   274	
   275	| Stage | Members | Order |
   276	|---|---:|---|
   277	| Pre calibration | 1 live observation | Finalize `pre` slot |
   278	| Same-window bound corpus | 12 | Frozen NEG8 order, then bound evaluation |
   279	| Start references | 3 | Frozen triplet |
   280	| Contrast half 1 | 20 | ABBA blocks 1–5 |
   281	| Midpoint reference | 1 | Frozen midpoint |
   282	| Contrast half 2 | 20 | ABBA blocks 6–10 |
   283	| End references | 3 | Frozen triplet |
   284	| Post calibration | 1 live observation | Finalize `post` slot |
   285	| Closeout | 0 science members | Pin, binding, verdict, backup, then analysis |
   286	
   287	The frozen manifest remains decode-only:
   288	
   289	- A is the exact 1.5B stack; B is the exact 7B stack.
   290	- Metric is exactly `phase_energy_j.decode`.
   291	- Estimand orientation is B−A.
   292	- Design is ten A/B/B/A blocks, n=10 block estimates.
   293	- Estimator is `abba_block_arm_mean_difference_t_v1`.
   294	- Test is two-sided at family alpha 0.05, with the positive direction stated as the scientific hypothesis rather than used to change the test.
   295	- `equivalence_margin` and `mde` remain null unless prospectively ruled otherwise.
   296	- Floor rule remains `cross_stack_armwise_max.v1`: independently resolve the 1.5B and 7B decode cells and take their maximum, never their sum.
   297	- Claim-side anchor bounds remain separate from the detection-floor operation.
   298	- The finalized analysis basis pins the exact forty member paths, config hashes, stack identities, floor artifact bytes, calibration binding, and evidence root.
   299	
   300	### Runtime evidence and budgets
   301	
   302	Historical evidence in `docs/phase_2/splitwise_decode_campaign.md` §4 supplies:
   303	
   304	- 1.5B decode member: 92.7 s, measured n=40;
   305	- 1.5B reference member: 90.5 s, measured n=7;
   306	- 7B decode member: approximately 97 s from the measured/probed anchor;
   307	- 1.5B/7B mixed ABBA half: about 31.6 min raw member time.
   308	
   309	The stage allowances incorporate the configured 30-second idle, warmup/teardown, stage arm overhead, and cooldown conventions. The pre-calibration allowance includes the required 180-second post-admin settle. The separate ten-minute untouched quiet-idle gate is added before applying the 20% margin.
   310	
   311	| Component, minutes | Alpha | Beta | Gamma |
   312	|---|---:|---:|---:|
   313	| Pre calibration bracket | 8 | 8 | 8 |
   314	| 12 NEG8 bound members | 22 | 22 | 22 |
   315	| Bound evaluation | 1 | 1 | 1 |
   316	| Start 3 references | 8 | 8 | 8 |
   317	| Absolute 10 | 19 | 20 | — |
   318	| ABBA blocks 1–5 | 34 | 36 | 35 |
   319	| Midpoint reference | 5 | 5 | 5 |
   320	| ABBA blocks 6–10 | 34 | 36 | 35 |
   321	| End 3 references | 8 | 8 | 8 |
   322	| Post calibration bracket | 8 | 8 | 8 |
   323	| Campaign subtotal | 147 | 152 | 130 |
   324	| Untouched pre-arm idle | 10 | 10 | 10 |
   325	| Base occupancy | 157 | 162 | 140 |
   326	| With 20% failure margin | **188.4** | **194.4** | **168.0** |
   327	| Hours | **3.14 h** | **3.24 h** | **2.80 h** |
   328	| 2–4 h envelope | Pass | Pass | Pass |
   329	
   330	The margin is time headroom, not authority to add members, replace a cap-hit observation, or top up an unfavorable result. The fixed manifest and frozen failure policy decide scientific validity.
   331	
   332	### §5A operator bookends
   333	
   334	Before each window:
   335	
   336	1. Verify the reviewed plan/readiness record, fresh empty roots, model artifacts, charger/AC state, power policy, OS/tool identity, empty waiver set, and current acceptance artifact.
   337	2. Verify the physical ledger head equals the authenticated committed pin.
   338	3. Correct the clock against the trusted source, record the correction and `usingnetworktime` state, turn network time off, and settle for at least 180 seconds.
   339	4. Establish zero-agent/zero-output-streaming conditions and complete ten untouched minutes of daemon idle.
   340	5. Append the exact two-slot bracket session capability.
   341	6. Capture and finalize the pre observation; run the acceptance and D-102 trigger probe.
   342	7. Only after every gate is green, emit the one-line arm message and walk away.
   343	
   344	At the closing bookend:
   345	
   346	1. Capture the post observation before changing power, network-time, or workload state.
   347	2. Finalize the post slot or write the governed failure/abort closure.
   348	3. Commit and authenticate the terminal ledger head.
   349	4. Emit the exact bracket binding and whole-window verdict from one immutable ledger snapshot.
   350	5. Back up evidence and bound roots with verified return code and hashes.
   351	6. Restore network time and record the restoration only after measurement completion and custody closeout.
   352	
   353	### Prefill floor claim eligibility
   354	
   355	A rider is claim-eligible only if desk freeze already binds:
   356	
   357	- exact metric and phase path;
   358	- exact workload parameters, model/tokenizer revision, seeds, quantization, runtime, sampling, and telemetry mode;
   359	- absolute and comparative member lists and order manifests;
   360	- exact condition-family ID and hash;
   361	- n and estimator;
   362	- calibration cell, acceptance artifact role, and D-110 allowance rule;
   363	- extraction failure behavior;
   364	- allowed consumer families.
   365	
   366	For each metric, the operative floor is the maximum of independently evaluated absolute and comparative components. Apply D-110 once as `A_s = max(observed_drift, 0.010818)`. Never sum components and never borrow a decode floor for prefill.
   367	
   368	### Two-stage mint freeze
   369	
   370	**Desk-frozen pin requirements**
   371	
   372	For each floor plan, freeze:
   373	
   374	- plan ID, declared SHA, sidecar SHA, and actual artifact SHA;
   375	- evidence-root ID;
   376	- four intended cell roles across the two plans;
   377	- condition-family IDs/hashes;
   378	- metric and phase-precheck paths;
   379	- absolute and comparative order-manifest IDs/hashes;
   380	- extraction-spec SHA and exact members;
   381	- expected counts;
   382	- model/runtime/config hashes;
   383	- calibration acceptance artifact ID/SHA/derivation rule;
   384	- D-110 never-zero allowance rule;
   385	- aggregate artifact ID and transport allowlists.
   386	
   387	These live in a non-mintable `pin_requirements.v2` artifact. Unresolved values must be structurally absent or explicitly marked unresolved; the file cannot satisfy the final pinset schema.
   388	
   389	**Postcollection-frozen pins**
   390	
   391	After passed verdicts and governed extraction, freeze separately for each of the four cells:
   392	
   393	- absolute and comparative evaluation-basis SHA/count;
   394	- exact accepted pre/post receipt and content digests;
   395	- bracket-binding SHA and terminal ledger head;
   396	- observed drift and applied allowance;
   397	- extraction-report SHA;
   398	- absolute, comparative, and operative values;
   399	- the operative literal formatted independently as exactly six decimals using the repository’s `.6f` convention.
   400	
   401	The lead independently recomputes each six-decimal literal from primary extraction bytes. The mint only compares supplied literals and hashes; it does not calculate them. The old `7.377086` literal is never reused.
   402	
   403	Gamma has no producer mint. Its consumer pinset instead binds the exact combined floor artifact bytes, the two decode-cell IDs, its plan/order/analysis manifests, and its finalized evaluation basis.
   404	
   405	### Synthetic three-window live-ledger regression
   406	
   407	The fixture begins with the exact issued-ledger semantics: 76 receipts, including 38 historical import observations—30 valid, 2 systematic, 6 ordinary-invalid. Candidate discovery must exclude every import-marked observation.
   408	
   409	The no-failure live extension adds three bracket capabilities and six finalized live observations. From one immutable final snapshot, the regression must prove:
   410	
     1	# D-117 plan-freeze design — magistrate ratification (2026-08-07, ruling gate 1)
     2	
     3	Sol xhigh design memo (this directory) ACCEPTED with the following
     4	rulings; the memo's freeze-order gates 1-8 are adopted as the campaign
     5	gate structure.
     6	
     7	1. **Two-slot ledger bracket-session capability + exact postcollection
     8	   bracket binding** — ACCEPTED (F1 closure shape; alternatives
     9	   rejected as the memo argues). U1 implements; ratify-vs-D-109/D-116
    10	   check rides U1's review gate.
    11	2. **Zero calibration retries in the base plans** — ACCEPTED. A
    12	   retry-enabled variant is NOT built now; if a night dies on a
    13	   removable cause, the fresh attempt is a new custody attempt of the
    14	   same frozen plan.
    15	3. **D-102 successor engine (U2) is COLD-GATED before first arm** — the
    16	   successor corpus rule (all content-distinct valid same-epoch
    17	   observations through the cutoff) is provisionally accepted, final
    18	   ratification at the U2 rule-11 gate.
    19	4. **One combined four-cell floor artifact via pinset v2** — ACCEPTED
    20	   (decode+prefill × 1.5B+7B; armwise max, never sum; v1 byte-parity
    21	   preserved).
    22	5. **256-token prefill contrast = fourth independent window plan,
    23	   never attached to gamma** — ACCEPTED; remains Ed's open option;
    24	   floor riders do NOT auto-transport (needs exact transport rule).
    25	6. **Identifiers** — ACCEPTED as proposed (plan-d117-*/evidence-d117-*/
    26	   runs_d117_* scheme).
    27	7. **Two-stage pin freeze** — ACCEPTED; the lead independently
    28	   recomputes every six-decimal operative literal from primary
    29	   extraction bytes at U10.
    30	
    31	Execution: U1 & U3 launch first (independent), then U2 (after U1),
    32	U4 (after U1+U2), U5-U7 packs (after U3), U8 readiness, U9 lead
    33	bookkeeping, U10 post-collection only. All units: enforced WRITE_SCOPE,
    34	implement→review→delta gauntlet, lead commits.
    35	
    36	Deviation note (Ed's fast-mode directive): implementation units run via
    37	codex-run-v3 (standard tier) because WRITE_SCOPE ENFORCEMENT and the
    38	audit envelope outweigh the fast tier for invariant-bearing code;
    39	fast-mode is used for all read-only/ideation work this session.
  6987	## D-109: CAL-BRACKET-D079-01 F3 — A-min-with-reservation adopted (writer-enforced receipt ledger, reservation-first, repo-committed head pin); R1 ledger-authority and R2 prior-observation-set rulings
  6988	
  6989	- Date: 2026-08-03
  6990	- Status: accepted (Ed ruling 2026-08-03: same explicit deferral to the
  6991	  joint magistrate + Sol position, same debate record. Arc: the fix
  6992	  investigation recommended A-min; Sol round 1 BROKE that formulation
  6993	  as stated (writer crash-window; prefix-subset is not anti-rollback)
  6994	  and recommended Option B for the timeline; magistrate round 2
  6995	  supplied the low-schedule-pressure record, the metrology-centric
  6996	  pivot, and the shared-R2 marginal-cost analysis; Sol WITHDREW B and
  6997	  converged on A-min-with-reservation, marginal cost Medium. Both
  6998	  soundness holes were lead-verified at the bench before adoption.)
  6999	- Applies to: `scripts/validate_powermetrics_fiducial.py` (sole
  7000	  production calibration writer), `joulewise/calibration_bracketing.py`,
  7001	  `joulewise/whole_window.py`, `scripts/run_campaign.py`,
  7002	  `configs/calibration/calibration_acceptance_d079_v2.json`, and every
  7003	  consumer construction of `AuthenticatedConsumptionSession`. This is
  7004	  a faithful IMPLEMENTATION of D-102 (no threshold/freshness
  7005	  amendment); it supplies the authority/universe rulings D-102 left
  7006	  silent. Lands with F1 + F2 as the single combined CAL-BRACKET fix
  7007	  round. Option B (signed narrowing amendment) is recorded as REJECTED
  7008	  fallback — coherent and honest, but it weakens the thesis instrument
  7009	  where the project has slack to build the sounder boundary.
  7010	
  7011	**R1 — ledger authority, retention, anti-rollback (7 clauses):**
  7012	1. A canonical observation-receipt ledger and its append API are the
  7013	   SOLE authority for governed calibration observations. An off-ledger
  7014	   calibration artifact is invalid everywhere: as bracket endpoint,
  7015	   trigger evidence, derivation member, or claim evidence. Consumers
  7016	   enumerate ledger entries only, never caller-supplied directories.
  7017	2. RESERVATION-FIRST: every capture appends an authenticated `pending`
  7018	   attempt entry BEFORE hardware capture begins, and must finalize it
  7019	   as valid / systematic-invalid / ordinary-invalid / abandoned. Any
  7020	   unresolved pending, unfinalized, malformed, or conflicting entry
  7021	   causes claim evaluation to REFUSE. (Grounds, bench-verified: the
  7022	   writer creates capture state pre-receipt and has pre-manifest
  7023	   failure exits — a publish-on-return receipt misses exactly the
  7024	   crash/interrupt cases a completeness mechanism exists to catch.)
  7025	3. Receipts are immutable and hash-chained: sequence, predecessor,
  7026	   attempt id, content id, artifact hashes, six-field epoch, full T1,
  7027	   capture time, exact bound lexeme, disposition, custody locator.
  7028	4. The acceptance artifact pins its baseline ledger head. Evaluation
  7029	   ALSO requires the independent current-head pin (clause below),
  7030	   verifies one complete non-forked chain extension from baseline to
  7031	   current, and threads ONE immutable ledger snapshot through every
  7032	   consumer path (session, direct runner path, secondary verifier) —
  7033	   repeated independent loads are a refusal-grade defect.
  7034	   Anti-rollback authority: a REPO-COMMITTED head-pin file
  7035	   `{sequence, head_digest, ledger_schema}` (existing checked-in
  7036	   byte-pin trust model; no second trusted latest-sequence store).
  7037	   Rotation is epoch-bounded — at most one lead-controlled
  7038	   quiet-machine collection session — and NO claim evaluation may
  7039	   occur between ledger advancement and pin commit; a physical head
  7040	   differing from the committed pin refuses.
  7041	5. Ledger history is retained permanently. Referenced evidence remains
  7042	   in authenticated custody; missing or unverifiable required bytes
  7043	   cause refusal, never silent omission.
  7044	6. Version 1 is single-authority, single-machine. Remote/other-machine
  7045	   captures are invalid until imported through an authenticated ledger
  7046	   transaction; direct multi-machine append requires a new ruling.
  7047	7. Threat model, stated honestly and to be stated wherever A-min is
  7048	   described: the mechanism closes workflow omission, unregistered
  7049	   evidence, and rollback/stale-head consumption. It does NOT defend
  7050	   against a malicious trusted writer or an authority that rewrites
  7051	   both Git and ledger history. No stronger claim may be made.
  7052	
  7053	**R2 — prior-observation set and prospective triggers (8 clauses):**
  7054	1. The issuance cutoff is an exact ledger sequence + head digest.
  7055	2. `derivation_corpus` remains exactly the n=19 threshold-producing
  7056	   observations.
  7057	3. `prior_observation_set` = every content-distinct governed
  7058	   observation known at the cutoff — valid, systematic-invalid,
  7059	   ordinary-invalid, blind holdout, and unresolved — with epoch and
  7060	   disposition recorded separately. (The current artifact's two
  7061	   ID-only `blind_exclusions` are insufficient and are superseded.)
  7062	4. Content identity is path-independent, derived from canonical
  7063	   primary-byte hashes; attempt identity is separate; copies do not
  7064	   create new observations.
  7065	5. "New" (trigger population) = current authentic content IDs −
  7066	   `prior_observation_set`, regardless of capture timestamp or source
  7067	   root; a previously unknown historical artifact IS new when
  7068	   discovered. Every new observation is judged under the PRIOR
  7488	## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)
  7489	
  7490	**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
  7491	**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**
  7492	
  7493	**What was written.**
  7494	- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
  7495	- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
  7496	- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
  7497	- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).
  7498	
  7499	**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).
  7500	
  7501	**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.
  7502	
  7503	**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.
  7504	
  7505	**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.
  7506	
  7507	## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
  7508	
  7509	**Date:** 2026-08-07 (Ed directive, in-thread; transcribed by the Fable
  7510	magistrate. Ed, verbatim: "if i recall for a paper ready at the quality
  7511	needed we need 3 more machine quiet nights and a lot of desk work",
  7512	with an explicit go to "execute all the deskwork" — read together with

codex
The core state machine matches the three-receipt design, but the current tests only mutate a binding inside one session; they do not yet recreate L5’s two-window borrowing attack. I found the referenced register is available from the newer `origin/main` history, so I’m pulling that exact finding read-only and will test its stated victim/neighbor construction against this diff.
exec
/bin/zsh -lc "git show origin/main:docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md | nl -ba | sed -n '1,260p'; git log --oneline --decorate --max-count=20 origin/main -- docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
     1	# Night-hardening findings register (2026-08-07; Sol high/fast lenses 1-2 of 3)
     2	
     3	Charge: defects that would strand one of the three D-117 quiet nights.
     4	Full reports in this directory (lens 3, extraction/mint, pending).
     5	Magistrate triage below; dispositions assigned at the pre-window
     6	readiness gate (memo gate 2/8).
     7	
     8	## Lens 1 — campaign runner/admission (AUDIT-RUNNER.md)
     9	
    10	- R6 MAJOR: relative `--runs-dir` PATH-DOUBLING is STILL LIVE in the
    11	  whole-window verdict (run_campaign.py:5148 / whole_window.py:1876) —
    12	  a relative root collects fine then fails verdict issuance.
    13	  MITIGATION NOW: D-117 plans + operator packet freeze ABSOLUTE runs
    14	  roots. FIX candidate for the night-hardening unit.
    15	- R7 SHOULD-FIX: verdict is unbounded/serial/opaque and empirically
    16	  >2 min — operator kill leaves a stale campaign.lock. MITIGATION:
    17	  operator packet forbids killing verdict; add progress/deadline later.
    18	- R5: cooldown/cap arithmetic uses wall clock, not monotonic — network-
    19	  time-off reduces but does not remove; register for the hardening unit.
    20	- R1-R4 (see report): no unattended retry slot for transient admission
    21	  failures (POLICY, deliberate — zero-retry ruling stands); stale-lock
    22	  on kill; assorted containment boundaries.
    23	
    24	## Lens 2 — calibration/ledger (AUDIT-LEDGER.md)
    25	
    26	- L5 HIGH: bracket selection can BORROW another window's receipts
    27	  (global candidate scan; no runs_root/intended-pair binding) — exactly
    28	  the defect class U1's session capability + exact binding closes.
    29	  U1 review MUST include this scenario as a regression vector.
    30	- L4 HIGH: pre-flight screens only a COPIED SCALAR (0.033558…), not
    31	  the issued artifact/identity epoch/range triggers — science can run
    32	  all night then be rejected at the morning verdict (identity epoch
    33	  change; sub-corpus-minimum lag). Closure = memo §5A step 6 pre-science
    34	  acceptance + D-102 trigger probe (U2) + de-duplicating the hardcoded
    35	  literal. U2 review must include both scenarios.
    36	- Loader itself verified correct at HEAD (issued role, file sha
    37	  316113960c…, estimator hashes match).
    38	
    39	## Disposition
    40	
    41	U1/U3 in flight cover L5 and part of the mint surface. U2 covers L4's
    42	trigger probe. R6 (absolute-paths) + R5 (monotonic time) + lock
    43	staleness need either a small hardening unit (U1.5) or explicit
    44	operator-procedure mitigations — decide when lens 3 lands.
    45	
    46	## Lens 3 — extraction/mint (AUDIT-MINT.md; landed after first commit)
    47	
    48	- Allowance arithmetic CLEAN (Decimal A_s once; component+allowance;
    49	  max-not-sum; armwise max at claims) — no defect in inspected path.
    50	- Confirms U3 scope: multi-cell/multi-plan minting, prefill metric,
    51	  pinset-to-claims handoff, membership validation all missing for the
    52	  D-117 morning chain. Exact required pinset fields documented in the
    53	  report (feed into U3's review as the ground-truth checklist).
    54	- Pinset `drift_allowance_j` (energy trajectory) ≠ D-102 `A_s` (timing)
    55	  — keep the distinction in U3's schema docs.
    56	
    57	## Paper-vs-code fidelity (AUDIT-PAPER-FIDELITY.md)
    58	
    59	Queue for the paper diff gate (B-tier accuracy fixes before advisor
    60	review): B1 "trapezoidal integration" → interval-average integration as
    61	implemented; B2 publish the exact operative bracket formula; B3 narrow
    62	the cryptographic-custody claim to what binds; quarantine is an
    63	OPERATOR action validated by the recorder, not automatic; disclose (or
    64	close) drift-evidence-in-verdict-hash scope; explain the policy JSON
    65	`0.01` vs executable `0.010818` screen.
    66	
    67	## Pre-window evidence-plumbing items (from the portfolio referee corps, 2026-08-07)
    68	
    69	- **URGENT before the three nights (rev-refusal-as-result):** window-verdict
    70	  rows carry no {member_id → reason_code} mapping and 16 of the 20
    71	  window-verdict condition codes live OUTSIDE the ratified
    72	  refusal_scope_spec.md enums (shadow taxonomy). If the D-117 nights run
    73	  before this lands, their member-failure evidence is free-text prose,
    74	  unrecoverable for any later analysis. Candidate small unit (U1.6):
    75	  reason-code field + spec reconciliation. Decide at the readiness gate.
    76	- Also banked: every D-117 member already carries an in-custody idle
    77	  capture (~203 across historical windows) — a zero-night contamination
    78	  desk-study substrate (P(asymmetric burst > 1 J / > 5 J) over real
    79	  member durations).
41ac740 Night-hardening register: pre-window reason-code plumbing flagged URGENT (shadow taxonomy; member-failure evidence otherwise unrecoverable) + idle-capture desk-study substrate noted
89f28bf Night-hardening lens 3 + paper-fidelity audit custodied: allowance arithmetic clean, U3 pinset ground truth documented; paper needs interval-average (not trapezoidal) correction + custody-claim narrowing before advisor review
89b929c Night-hardening lenses 1-2 custodied + triage register: path-doubling still live in verdict (R6), bracket borrowing + scalar-only preflight (L4/L5) confirm U1/U2 blockers; operator-packet draft banked

exec
/bin/zsh -lc "git show origin/main:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md | nl -ba | sed -n '1,260p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
     1	Reading additional input from stdin...
     2	OpenAI Codex v0.146.1
     3	--------
     4	workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
     5	model: gpt-5.6-sol
     6	provider: openai
     7	approval: never
     8	sandbox: workspace-write [workdir, /tmp, $TMPDIR]
     9	reasoning effort: high
    10	reasoning summaries: none
    11	session id: 019fdd09-2b4f-7583-b3d7-3f330eeee5c7
    12	--------
    13	user
    14	NIGHT-STRANDER BUG HUNT, LENS 2 of 3: CALIBRATION BRACKET + LIVE LEDGER PATH (read-only; write no files; final message = report, severity + file:line + concrete failing scenario each). Context: under decision D-117 (end of docs/decision_log.md), three fresh quiet windows will each run PRE and POST pulse-train calibrations whose receipts append LIVE to the issued calibration observation ledger (see the D-116 entry + joulewise calibration_bracketing/ledger code + scripts around calibration acceptance). Your charge: find defects in the live-receipt append path, ledger head-pin verification, acceptance-rule loading of the ISSUED artifact (not the genesis fixture), bracket pairing/drift-screen computation, and pre-flight calibration family screens that could (a) refuse a healthy window at 2am with nobody present, or (b) silently accept evidence the morning verdict then rejects. Also check: what happens if the pre calibration passes, science members run, and the POST calibration process dies — is the partial state recoverable or does it strand the whole window? Rank by night-loss probability.
    15	codex
    16	I’ll trace the issued-ledger lifecycle end to end—from preflight and head pinning through PRE/POST receipt appends, bracket pairing, and acceptance—then rank only concrete, reproducible failure modes. I’ll keep the workspace untouched.
    17	exec
    18	/bin/zsh -lc "pwd && git status --short --branch && rg -n \"ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next\" RUN_STATE.md && rg -n \"Current Queue|Do-Not-Do-Yet|D-117|D-116\" TASK_QUEUE.md docs/decision_log.md && sed -n '1,240p' docs/agent_playbook.md && sed -n '1,240p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
    19	 succeeded in 0ms:
    20	/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
    21	## main...origin/main
    22	2004:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
    23	2039:## ACTIVE_STOP_CARD
    24	2178:## Current Project Status
    25	2739:## Known Workspace State
    26	TASK_QUEUE.md:96:Current Queue region is the sole live work-selection view.
    27	TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
    28	TASK_QUEUE.md:306:## Current Queue
    29	docs/decision_log.md:141:| D-116 | D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (seq 76 / head 08456d50…; issued sha 316113960c…; 30/2/6 dispositions); D-110 condition (b) SATISFIED → MINT-GENERALIZE-01 unblocked for re-mint; two-cold-gate history (plan HELD → consumer impl + gauntlet → bytes PROCEED, sequencing HOLD resolved by consumer-first merge); window_metrologyB calibration fiducials in completeness record are NOT a D-113 violation | executed (Fable magistrate, 2026-08-06; Ed pre-authorized) |
    30	docs/decision_log.md:7084:> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
    31	docs/decision_log.md:7088:> allowance correction STAND and bind the D-117 mints.
    32	docs/decision_log.md:7249:> **2026-08-07 amendment (D-117 cl.4):** the readiness dependency on
    33	docs/decision_log.md:7488:## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)
    34	docs/decision_log.md:7507:## D-117: D-110's historical re-mint order SUPERSEDED — prospective three-window replacement (Option 2) adopted; D-113 readiness rewired
    35	# Agent Playbook: Ordered Missions
    36	
    37	Audience: an agent (or human) told "go do the next step" with no other
    38	context. This file turns the project's plans into self-contained,
    39	executable missions. Each mission says what to read, what to do, how to
    40	verify, and what to update afterward.
    41	
    42	Division of labor (D-023 discipline — do not duplicate):
    43	
    44	- **This file owns:** the operational wrapper per mission (read-first
    45	  lists, execution order, verification commands, handoff checklists) and
    46	  the code-level pointers from the 2026-07-05 external code review that
    47	  exist nowhere else.
    48	- **It points to:** `docs/phase_N/phase_N_plan.md` for objectives, gates,
    49	  acceptance criteria, and fallbacks; `docs/phase_2/
    50	  hardware_slice_implementation_guide.md` for hardware-slice pinned APIs;
    51	  `docs/decision_log.md` for settled decisions; the phase exit checklists
    52	  for current per-item status.
    53	- **No status lives here.** To find out what is already done, read
    54	  `RUN_STATE.md` and the exit checklists. To find out what outranks what,
    55	  read `TASK_QUEUE.md`. If this playbook and a plan disagree, the plan
    56	  wins; fix the drift in the same run.
    57	
    58	## How To Pick A Mission
    59	
    60	1. Run Mission M0 (preflight) — always.
    61	2. Take the highest-ranked task in `TASK_QUEUE.md` whose gate is open.
    62	3. Find its mission below and execute it. One mission per session unless
    63	   the first finishes early and cleanly.
    64	
    65	Gate summary (check the queue/checklists for live status; this is just
    66	the dependency shape):
    67	
    68	```text
    69	ungated, any time:      M1 (Slice 2N), M2 (backup protocol prep), M3 (related work)
    70	needs user/advisor:     M4 (D-016 model selection), and the P1 evidence gates
    71	needs D-016 + install:  M5 (2G MLX)
    72	needs auth session:     M6 (2H powermetrics)
    73	needs M5+M6:            M7 (2I Mac slice — the flagship)
    74	needs P1-006 evidence:  M8 (2K/2L remote-target live validation;
    75	                         2K fixture-first stack merged 2026-07-08 via PR #11)
    76	needs M7:               M9 (2M baselines)
    77	post-docs branch:       M10 Stage 3.0.1 verdict is replay_supported
    78	                         after lead live re-verification
    79	needs 2M baselines:     M10 later pairing-feasibility matrix + split runs
    80	```
    81	
    82	---
    83	
    84	## Mission M0: Preflight (every session)
    85	
    86	1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
    87	   if present, "Current Project Status", "Known Workspace State", and
    88	   "What Is Next". If the stop card is ACTIVE, it overrides this
    89	   playbook and the task queue until cleared.
    90	2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
    91	3. Read the selected mission's own read-first list. Read `AGENT_PLAN.md`
    92	   only at phase starts or when the project structure changes. Consult
    93	   `docs/decision_log.md` by targeted decision ID, not as a whole-file
    94	   intake step.
    95	   If the session involves delegation, review, or multi-stream work, also
    96	   read `docs/orchestration.md` (the process layer) — not optional for
    97	   landing code.
    98	4. Check workspace state with `git status --short --branch`; inspect
    99	   recent commits only when the handoff or mission needs them.
   100	5. `python3 -m unittest discover -s tests` — expect `Ran <N> tests` (N per `RUN_STATE.md` Current Verification; `, OK
   101	   (skipped=10)` with zero expected failures as of 2026-07-08 after
   102	   P2-013/P2-014 and the C-011 rigor mechanics. The skips are the `[analysis]`-extra chart tests plus one
   103	   optional-jsonschema test. A red suite is itself the mission: stop and fix
   104	   or report.
   105	6. Review `docs/risk_register.md` at phase starts, before hardware tasks,
   106	   when a trigger fires, or if >14 days passed since the last run report
   107	   with no break recorded in `docs/milestones.md`.
   108	7. At session end, always: update `RUN_STATE.md`, update `TASK_QUEUE.md`,
   109	   write a dated run report in `docs/run_reports/`, update the phase exit
   110	   checklist for anything that closed, and `PROJECT_STATUS.md` if
   111	   advisor-visible state changed. Commit when the user asks or has
   112	   standing-approved it.
   113	
   114	Environment cautions:
   115	
   116	- The repo must stay at a non-iCloud path (`~/code/...`; R-017). If you
   117	  see `Operation not permitted` on reads inside the repo, stop, wait for
   118	  the lock to clear, re-run the suite, and record the incident.
   119	- CI installs no extras; every new test must pass on a bare Python
   120	  (lazy imports, `skipUnless` for optional deps — D-009).
   121	- Schema changes are additive-only until v0.2 (R-015/D-008).
   122	
   123	---
   124	
   125	## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)
   126	
   127	**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
   128	Slice 2N. This mission adds the code-level route for each work item,
   129	sourced from the 2026-07-05 external code review. Line numbers are from
   130	commit `ae48abe` — re-locate by symbol name if the files have moved on.
   131	
   132	Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
   133	`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
   134	(skim whole files — they are small and the invariants interlock).
   135	
   136	2N is one mission but NOT one sitting: it touches adapter interfaces,
   137	controller timing, reducer behavior, report parsing, CLI, schema export,
   138	and validation policy. Work item-by-item with the suite green after each,
   139	and land it as roughly three commits so a failure bisects cleanly:
   140	
   141	- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
   142	  2N.2 (measured-window boundaries). Both touch controller/interfaces.
   143	- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
   144	  contract), 2N.7 (report alignment), and 2N.6's structured read
   145	  failures implemented on top of it. 2N.6's CLI verb rides along.
   146	- **Commit C — schema + metrics:** 2N.5 (schema round-trip), 2N.3
   147	  (token-count fallback), 2N.9 (v0.2 compatibility note).
   148	
   149	If a session ends mid-slice, a completed commit group is a clean
   150	handoff point — say which group landed in `RUN_STATE.md`.
   151	
   152	Per-item detail (each item = tests green before the next; items 1+2
   153	change the controller/adapter contract and go first):
   154	
   155	### 2N.1 `RunContext` seam + raw evidence
   156	
   157	- Today: `RunBundleWriter._ensure_layout` creates `raw/` (bundle.py
   158	  ~line 160) but no method writes into it, and adapters never see the
   159	  bundle path — so a real telemetry adapter cannot honor D-002 ("raw
   160	  file retained verbatim").
   161	- Change: implement **D-024** (already decided — read it first): an
   162	  immutable `RunContext` dataclass (config, clock, run_id, bundle_path,
   163	  raw_dir, logs_dir, outputs_dir, optional node_role=None) constructed
   164	  by the controller after bundle creation and passed to adapter
   165	  lifecycle methods (exact placement — per-method parameter vs
   166	  construction-time — is yours to pin; record the choice as a D-024
   167	  amendment note). Add `RunBundleWriter.raw_path(name)`/`write_raw` as
   168	  the writer-side counterpart (validated, collision-checked). Update
   169	  `docs/contracts/adapter_contracts.md` in the same run. Do NOT hand
   170	  adapters the writer itself — D-024 rejects that option; context is
   171	  data, not capability.
   172	- Tests: mock telemetry writes a fixture raw file via the context;
   173	  bundle contains it; immutability (no overwrite after finalize); the
   174	  no-raw-output mock path still passes; mocks ignore unused context
   175	  fields (single lifecycle code path preserved).
   176	
   177	### 2N.2 Measured window excludes sampler startup
   178	
   179	- Today: `stage_started(measured_run)` is timestamped before
   180	  `thermal_state` and `start_sampling` (controller.py ~lines 346-357),
   181	  and the reducer integrates from that stage-start. Under `SystemClock`,
   182	  sampler spawn latency (sudo probe, process start, first sample) lands
   183	  inside the measured window — inflating gross energy, idle-subtraction
   184	  duration, and TTFT. `FakeClock` collapses the interval to zero, so the
   185	  existing suite cannot catch it.
   186	- Change: open the measured window only after sampling is confirmed
   187	  started (reorder), or emit explicit `sampling_started`/
   188	  `sampling_stopped` marker events and make the reducer integrate
   189	  between markers. Keep the D-013 quiescent rule intact (controller only
   190	  blocks on the runtime inside the window). Record the choice
   191	  (decision-log entry; it pins reducer semantics).
   192	- Tests: a fake telemetry adapter whose `start_sampling` advances the
   193	  injected clock by a simulated latency; assert the reducer's window
   194	  excludes it (energy and TTFT unchanged vs a zero-latency run).
   195	
   196	### 2N.3 Reducer token-count fallback
   197	
   198	- Today: `energy_token_j` requires `workload_profile.prompt_tokens` from
   199	  config (reduce.py ~lines 302, 511-521); a `prompt_text`-only config
   200	  (like `configs/examples/mac_mlx_local.json`) silently yields `None`
   201	  for the headline per-token metric, even though the runtime's observed
   202	  `token_count`/`output_token_count` are already written to
   203	  `metadata.json` (controller.py ~lines 532-536).
   204	- Change: reducer falls back to observed counts from metadata; record
   205	  which source was used (additive optional summary/quality field, e.g.
   206	  `token_count_source: "config" | "runtime_observed"` — R-015 allows
   207	  additive).
   208	- Tests: prompt_text-only bundle produces non-None `energy_token_j`
   209	  with source `runtime_observed`; config-supplied counts still win;
   210	  neither present → None (unchanged).
   211	
   212	### 2N.4 Rail-summation timestamp contract
   213	
   214	- Today: `_summed_curve` groups rails by exact float `timestamp_s`
   215	  equality (reduce.py ~lines 129-131). A real adapter emitting per-rail
   216	  rows with slightly skewed timestamps silently produces an interleaved
   217	  per-rail curve and badly undersummed energy — wrong number, no error.
   218	- Change: either (a) detect misalignment (per-timestamp rail set !=
   219	  manifest) and return a structured reduction failure naming the rail
   220	  and skew, or (b) bucket timestamps within a tolerance derived from the
   221	  sampling interval. Decide, log the decision, and document the
   222	  contract in `docs/contracts/adapter_contracts.md` (today it is only a
   223	  bundle.py comment).
   224	- Tests: skewed-timestamp fixture → structured failure (or correct
   225	  bucketed sum); aligned fixture unchanged to 9 decimals.
   226	
   227	### 2N.5 Config schema accepts emitted configs
   228	
   229	- Today: `BenchmarkConfig.to_dict()` emits `null` for absent optionals
   230	  (`asdict`), but the hand-written exported JSON Schema declares those
   231	  properties non-nullable (e.g. `quantization.bits`, schemas.py ~line
   232	  379) — a bundle's normalized `config.json` fails validation against
   233	  `print-config-schema` output.
   234	- Change: pick one — (a) omit-None serialization (cleaner artifact;
   235	  changes config bytes and therefore config hashes — acceptable ONLY
   236	  while no real bundles exist, so decide now), or (b) schema declares
   237	  nullable optionals. Either way: decision-log entry, and a round-trip
   238	  test.
   239	- Tests: every emitted normalized example config validates against the
   240	  exported schema. CI has no `jsonschema` package (D-009): either write
   241	  the check against the specific fields (nullability + required keys) or
   242	  gate a full-validator test behind `skipUnless(jsonschema)`. Also
   243	  assert config-hash stability with a pinned expected hash so future
   244	  serialization changes fail loudly.
   245	
   246	### 2N.6 Post-hoc `reduce` verb + structured reducer failures
   247	
   248	- Today: `reduce_bundle` is importable but has no CLI verb, and raises
   249	  uncaught `FileNotFoundError`/`JSONDecodeError` on missing/corrupt
   250	  `config.json`/`metadata.json` (reduce.py ~lines 341-352) despite its
   251	  docstring's "never crashes" claim. The "a reducer bug never re-runs
   252	  hardware" story needs a user-facing path.
   253	- Change: `python3 -m joulewise reduce <bundle-dir>` — re-derives and
   254	  rewrites `summary_metrics.json` (document that this is the one
   255	  sanctioned post-finalize mutation, or write to a versioned name —
   256	  check D-011 and log the choice); degenerate inputs return structured
   257	  failures. Match `run`'s exit-code scheme (0/2/3) and one greppable
   258	  result line.
   259	- Tests: reduce a valid bundle → identical metrics; corrupt/missing
   260	  artifacts → structured failure + correct exit code; CLI help updated.

exec
/bin/zsh -lc 'git show origin/main:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md | rg -n -C 12 "L5|BORROW|runs_root|failing scenario|neighbor|bracket selection"' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
2-OpenAI Codex v0.146.1
3---------
4-workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
5-model: gpt-5.6-sol
6-provider: openai
7-approval: never
8-sandbox: workspace-write [workdir, /tmp, $TMPDIR]
9-reasoning effort: high
10-reasoning summaries: none
11-session id: 019fdd09-2b4f-7583-b3d7-3f330eeee5c7
12---------
13-user
14:NIGHT-STRANDER BUG HUNT, LENS 2 of 3: CALIBRATION BRACKET + LIVE LEDGER PATH (read-only; write no files; final message = report, severity + file:line + concrete failing scenario each). Context: under decision D-117 (end of docs/decision_log.md), three fresh quiet windows will each run PRE and POST pulse-train calibrations whose receipts append LIVE to the issued calibration observation ledger (see the D-116 entry + joulewise calibration_bracketing/ledger code + scripts around calibration acceptance). Your charge: find defects in the live-receipt append path, ledger head-pin verification, acceptance-rule loading of the ISSUED artifact (not the genesis fixture), bracket pairing/drift-screen computation, and pre-flight calibration family screens that could (a) refuse a healthy window at 2am with nobody present, or (b) silently accept evidence the morning verdict then rejects. Also check: what happens if the pre calibration passes, science members run, and the POST calibration process dies — is the partial state recoverable or does it strand the whole window? Rank by night-loss probability.
15-codex
16-I’ll trace the issued-ledger lifecycle end to end—from preflight and head pinning through PRE/POST receipt appends, bracket pairing, and acceptance—then rank only concrete, reproducible failure modes. I’ll keep the workspace untouched.
17-exec
18-/bin/zsh -lc "pwd && git status --short --branch && rg -n \"ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next\" RUN_STATE.md && rg -n \"Current Queue|Do-Not-Do-Yet|D-117|D-116\" TASK_QUEUE.md docs/decision_log.md && sed -n '1,240p' docs/agent_playbook.md && sed -n '1,240p' docs/orchestration.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
19- succeeded in 0ms:
20-/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
21-## main...origin/main
22-2004:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
23-2039:## ACTIVE_STOP_CARD
24-2178:## Current Project Status
25-2739:## Known Workspace State
26-TASK_QUEUE.md:96:Current Queue region is the sole live work-selection view.
--
6331-   525	        and binding_evidence.get("binding_vector_sha256")
6332-   526	        == hashlib.sha256(canonical).hexdigest()
6333-   527	        and isinstance(binary, Mapping)
6334-   528	        and binary.get("sha256") == bindings.get("powermetrics_sha256")
6335-   529	        and isinstance(binary.get("path"), str)
6336-   530	        and bool(binary.get("path"))
6337-   531	        and isinstance(power_policy, Mapping)
6338-   532	        and power_policy.get("id") == bindings.get("power_policy")
6339-   533	    )
6340-   534	
6341-   535	
6342-   536	def load_calibration_candidate(
6343:   537	    directory: Path, *, runs_root: Path
6344-   538	) -> CalibrationCandidate | None:
6345-   539	    """Authenticate one standalone validation directory from primary bytes."""
6346-   540	
6347:   541	    root = Path(runs_root).resolve()
6348-   542	    try:
6349-   543	        directory = Path(directory).resolve(strict=True)
6350-   544	        relative = directory.relative_to(root).as_posix()
6351-   545	        manifest_raw = (directory / "manifest.json").read_bytes()
6352-   546	        manifest = json.loads(manifest_raw)
6353-   547	    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
6354-   548	        return None
6355-   549	    artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
6356-   550	    if (
6357-   551	        not relative
6358-   552	        or not isinstance(artifacts, Mapping)
6359-   553	        or manifest.get("schema_version")
--
6466-   660	
6467-   661	
6468-   662	def _candidate_from_observation(
6469-   663	    observation: LedgerObservation,
6470-   664	) -> CalibrationCandidate | None:
6471-   665	    """Authenticate one valid ledger observation from its custody locator."""
6472-   666	
6473-   667	    if observation.disposition != "valid" or observation.content_id is None:
6474-   668	        return None
6475-   669	    custody = Path(observation.custody_locator)
6476-   670	    candidate = load_calibration_candidate(
6477-   671	        custody,
6478:   672	        runs_root=custody.parent.parent,
6479-   673	    )
6480-   674	    if candidate is None:
6481-   675	        return None
6482-   676	    bound = _candidate_decimal(candidate)
6483-   677	    receipt_bound = _decimal(observation.exact_bound_lexeme_s)
6484-   678	    try:
6485-   679	        receipt_capture = float(observation.capture_wall_time_s)
6486-   680	    except (TypeError, ValueError):
6487-   681	        return None
6488-   682	    if (
6489-   683	        candidate.manifest_sha256
6490-   684	        != observation.artifact_sha256.get("manifest.json")
--
6725-   938	            "trigger_guard_protocol_sha256": prospective["protocol_sha256"],
6726-   939	            "trigger_guard_estimator_code_sha256": dict(
6727-   940	                prospective["estimator_code_sha256"]
6728-   941	            ),
6729-   942	            "stale_fields": stale_fields,
6730-   943	            "calendar_expiry": None,
6731-   944	        },
6732-   945	        "prospective_rederivation": {
6733-   946	            "observation_rule": prospective["trigger_observation_rule"],
6734-   947	            "candidate_set_boundary": (
6735-   948	                "authenticated_calibration_ledger_snapshot_only"
6736-   949	            ),
6737:   950	            "global_runs_root_scan": False,
6738-   951	            "mandatory_triggers": list(prospective["triggers"]),
6739-   952	            "observed_triggers": [],
6740-   953	        },
6741-   954	        "numeric_semantics": {
6742-   955	            "comparisons": "decimal",
6743-   956	            "reducer_boundary": "binary64_recorded_below",
6744-   957	        },
6745-   958	        "ledger_snapshot": {
6746-   959	            "ledger_schema": ledger_snapshot.ledger_schema,
6747-   960	            "sequence": ledger_snapshot.head_sequence,
6748-   961	            "head_digest": ledger_snapshot.head_digest,
6749-   962	            "baseline_sequence": ledger_snapshot.baseline_sequence,
--
7032-  1245	        "value_s": str(allowance),
7033-  1246	        "embedding_count": 1,
7034-  1247	        "embedded_in": "b_fiducial_s",
7035-  1248	        "endpoint_max_b_fiducial_s": str(endpoint_max_decimal),
7036-  1249	        "operative_b_fiducial_decimal_s": str(operative_bound),
7037-  1250	        "operative_b_fiducial_binary64_s": float(operative_bound),
7038-  1251	    }
7039-  1252	    result["status"] = "passed"
7040-  1253	    return result, ()
7041-  1254	
7042-  1255	
7043-  1256	def calibration_bracket_for_bundles(
7044:  1257	    runs_root: Path,
7045-  1258	    bundle_paths: Sequence[Path],
7046-  1259	    policy: CalibrationBracketingPolicy,
7047-  1260	    *,
7048-
7049-exec
7050-/bin/zsh -lc "nl -ba joulewise/calibration_ledger.py | sed -n '1600,1785p'; nl -ba joulewise/calibration_bracketing.py | sed -n '431,735p'; nl -ba joulewise/calibration_bracketing.py | sed -n '784,900p'; nl -ba joulewise/calibration_bracketing.py | sed -n '1256,1350p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
7051- succeeded in 0ms:
7052-  1600	        except OSError:
7053-  1601	            pass
7054-  1602	    return plan
7055-  1603	
7056-  1604	
--
7332-   525	        and binding_evidence.get("binding_vector_sha256")
7333-   526	        == hashlib.sha256(canonical).hexdigest()
7334-   527	        and isinstance(binary, Mapping)
7335-   528	        and binary.get("sha256") == bindings.get("powermetrics_sha256")
7336-   529	        and isinstance(binary.get("path"), str)
7337-   530	        and bool(binary.get("path"))
7338-   531	        and isinstance(power_policy, Mapping)
7339-   532	        and power_policy.get("id") == bindings.get("power_policy")
7340-   533	    )
7341-   534	
7342-   535	
7343-   536	def load_calibration_candidate(
7344:   537	    directory: Path, *, runs_root: Path
7345-   538	) -> CalibrationCandidate | None:
7346-   539	    """Authenticate one standalone validation directory from primary bytes."""
7347-   540	
7348:   541	    root = Path(runs_root).resolve()
7349-   542	    try:
7350-   543	        directory = Path(directory).resolve(strict=True)
7351-   544	        relative = directory.relative_to(root).as_posix()
7352-   545	        manifest_raw = (directory / "manifest.json").read_bytes()
7353-   546	        manifest = json.loads(manifest_raw)
7354-   547	    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
7355-   548	        return None
7356-   549	    artifacts = manifest.get("artifacts") if isinstance(manifest, Mapping) else None
7357-   550	    if (
7358-   551	        not relative
7359-   552	        or not isinstance(artifacts, Mapping)
7360-   553	        or manifest.get("schema_version")
--
7467-   660	
7468-   661	
7469-   662	def _candidate_from_observation(
7470-   663	    observation: LedgerObservation,
7471-   664	) -> CalibrationCandidate | None:
7472-   665	    """Authenticate one valid ledger observation from its custody locator."""
7473-   666	
7474-   667	    if observation.disposition != "valid" or observation.content_id is None:
7475-   668	        return None
7476-   669	    custody = Path(observation.custody_locator)
7477-   670	    candidate = load_calibration_candidate(
7478-   671	        custody,
7479:   672	        runs_root=custody.parent.parent,
7480-   673	    )
7481-   674	    if candidate is None:
7482-   675	        return None
7483-   676	    bound = _candidate_decimal(candidate)
7484-   677	    receipt_bound = _decimal(observation.exact_bound_lexeme_s)
7485-   678	    try:
7486-   679	        receipt_capture = float(observation.capture_wall_time_s)
7487-   680	    except (TypeError, ValueError):
7488-   681	        return None
7489-   682	    if (
7490-   683	        candidate.manifest_sha256
7491-   684	        != observation.artifact_sha256.get("manifest.json")
--
7649-   890	        )
7650-   891	    ):
7651-   892	        return result, ("calibration_ledger_baseline_missing",)
7652-   893	    if not _prior_set_matches_import_cutoff_prefix(artifact, ledger_snapshot):
7653-   894	        return result, ("calibration_ledger_baseline_missing",)
7654-   895	    identity_epoch = artifact["identity_epoch"]
7655-   896	    prospective = artifact["prospective_rederivation"]
7656-   897	    result["policy"].update(
7657-   898	        {
7658-   899	            "calibration_bracket_max_drift_s_role": (
7659-   900	                "legacy_obsolete_not_an_acceptance_comparator"
7660-  1256	def calibration_bracket_for_bundles(
7661:  1257	    runs_root: Path,
7662-  1258	    bundle_paths: Sequence[Path],
7663-  1259	    policy: CalibrationBracketingPolicy,
7664-  1260	    *,
7665-  1261	    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
7666-  1262	    _allow_unissued_fixture: bool = False,
7667-  1263	) -> tuple[dict[str, Any], tuple[str, ...]]:
7668-  1264	    """Use the runs root only for the evaluated window's T1/endpoints."""
7669-  1265	
7670-  1266	    if not bundle_paths:
7671-  1267	        empty, _ = evaluate_calibration_bracket(
7672-  1268	            (),
7673-  1269	            window_start_s=0.0,
--
8183-./docs/process_traces/2026-08-03-d111-backfill/test-speed-consult/summary-20260803.json:66:      "module": "tests.test_powermetrics_fiducial",
8184-./docs/process_traces/2026-08-03-d111-backfill/coldgate_d100_bii/LA-PRIME-BANKED.md:145:{"cardinalities":{"metadata.adapters.runtime.cleanup_metadata.memory_snapshots":[1],"metadata.adapters.runtime.prepare_metadata.memory_snapshots":[1],"metadata.campaign_environment_preflight.arm_quiet_mode.command":[2],"metadata.campaign_environment_preflight.evaluation.findings":[6],"metadata.config_warnings":[0],"metadata.device.powermetrics.samplers_available":[4],"metadata.device.rail_manifest":[3],"metadata.environment_admission.attempts":[2],"metadata.environment_admission.attempts[].cpu_admission.conditions":[1,2],"metadata.environment_admission.guard_observations":[4],"metadata.environment_admission.per_run_environment_evaluation.findings":[6],"metadata.source_provenance.reason_codes":[0,2]},"keys":{"metadata":["adapters","campaign_environment_preflight","campaign_policy","clock","config_sha256","config_warnings","connection","device","environment","environment_admission","git_commit","idle_baseline","instrument_calibration","joulewise_version","machine","model","platform","python_version","quantization","run_id","schema_version","source_provenance","suite"],"metadata.adapters":["runtime","telemetry"],"metadata.adapters.runtime":["cleanup_metadata","name","prepare_metadata"],"metadata.adapters.runtime.cleanup_metadata":["memory_snapshots"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[]":["captured_at_s","label","mlx_metal","process_rss_bytes"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].mlx_metal":["active_memory_bytes","api_available","cache_memory_bytes","peak_memory_bytes"],"metadata.adapters.runtime.prepare_metadata":["adapter","load_wall_time_s","memory_snapshots","mlx_lm_version","mlx_version","model_artifact_identity","model_config_eos_token_id","model_config_name","model_revision","model_source","model_source_is_local_path","quantization","transformers_version","weight_format"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[]":["captured_at_s","label","mlx_metal","process_rss_bytes"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].mlx_metal":["active_memory_bytes","api_available","cache_memory_bytes","peak_memory_bytes"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity":["algorithm","files","folded_sha256","kind","root","status"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.files":["model.safetensors"],"metadata.adapters.telemetry":["name"],"metadata.campaign_environment_preflight":["admitted","arm_quiet_mode","captured_at","enforced","evaluation","initial_findings_sha256","initial_snapshot_sha256","override","policy_sha256","schema_version","snapshot"],"metadata.campaign_environment_preflight.arm_quiet_mode":["command","command_returncode","countdown_s","requested","verified_by_reprobe"],"metadata.campaign_environment_preflight.evaluation":["eligible","findings","findings_sha256","load_average_evidence","schema_version","snapshot_sha256"],"metadata.campaign_environment_preflight.evaluation.findings[]":["actual","code","critical","field","required","status"],"metadata.campaign_environment_preflight.evaluation.load_average_evidence":["admission_gate","load_average_15m","load_average_1m","load_average_5m"],"metadata.campaign_environment_preflight.snapshot":["battery_percent","battery_state","boot_time_s","build_version","clock_sync","cpu_brand","display","display_power_state","display_sleep_prevented","errors","hid_idle_s","hw_model","load_average_15m","load_average_1m","load_average_5m","logical_cpu_count","low_power_mode","memory","memory_free_percent","memory_pressure_percent","power","power_source","product_name","product_version","python_packages","screensaver_delay_s","screensaver_engaged","screensaver_module","thermal_pressure","thermal_probe_reason","uptime_s"],"metadata.campaign_environment_preflight.snapshot.clock_sync":["status","timed_probe_error","timed_running"],"metadata.campaign_environment_preflight.snapshot.display":["active_displays","asleep_display_count","asleep_evidence_count","built_in_display_count","external_display_count","framebuffer_pipes_external_capable","framebuffer_pipes_total","probe","reason","status"],"metadata.campaign_environment_preflight.snapshot.errors":[],"metadata.campaign_environment_preflight.snapshot.memory":["compressor_bytes","page_size_bytes","pageins","pageouts","pages_free","pages_occupied_by_compressor","pages_stored_in_compressor","swap_usage"],"metadata.campaign_environment_preflight.snapshot.memory.swap_usage":["free","total","used"],"metadata.campaign_environment_preflight.snapshot.power":["adapter_description","adapter_watts","external_connected","fully_charged","is_charging"],"metadata.campaign_environment_preflight.snapshot.python_packages":["mlx","mlx-lm","transformers"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx":["present","version"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx-lm":["present","version"],"metadata.campaign_environment_preflight.snapshot.python_packages.transformers":["present","version"],"metadata.campaign_policy":["calibration_bracketing","idle_admission_extension","policy_id","policy_version","profile","schema_version","sha256","source"],"metadata.campaign_policy.calibration_bracketing":["calibration_bracket_max_drift_s","require_bracket"],"metadata.campaign_policy.idle_admission_extension":["claim_bearing","policy_version","schema_version","sha256"],"metadata.clock":["kind","monotonic_minus_wall_s","monotonic_resolution_s","wall_minus_monotonic_end_s","wall_minus_monotonic_start_s","wall_resolution_s"],"metadata.connection":["host","transport"],"metadata.device":["boundary","capability_precheck","device","hw_model","kern_bootargs","kern_boottime","kern_osversion","plist_anchor_offset_s","power_units","powermetrics","rail_manifest","telemetry","timestamp_derivation"],"metadata.device.capability_precheck":["ok"],"metadata.device.powermetrics":["executable_path","executable_sha256","samplers_available","samplers_probe","samplers_requested"],"metadata.device.powermetrics.samplers_probe":["method","ok"],"metadata.environment":["battery_percent","battery_state","boot_time_s","build_version","capture_scope","capture_skipped","captured_at_s","captured_for_rep","clock_sync","cpu_brand","display","display_power_state","display_sleep_prevented","env_capture_duration_s","errors","hid_idle_s","hw_model","load_average_15m","load_average_1m","load_average_5m","logical_cpu_count","low_power_mode","memory","memory_free_percent","memory_pressure_percent","power","power_source","product_name","product_version","python_packages","screensaver_delay_s","screensaver_engaged","screensaver_module","settle_s","thermal_pressure","thermal_probe_reason","uptime_s"],"metadata.environment.clock_sync":["status","timed_probe_error","timed_running"],"metadata.environment.display":["active_displays","asleep_display_count","asleep_evidence_count","built_in_display_count","external_display_count","framebuffer_pipes_external_capable","framebuffer_pipes_total","probe","reason","status"],"metadata.environment.errors":[],"metadata.environment.memory":["compressor_bytes","page_size_bytes","pageins","pageouts","pages_free","pages_occupied_by_compressor","pages_stored_in_compressor","swap_usage"],"metadata.environment.memory.swap_usage":["free","total","used"],"metadata.environment.power":["adapter_description","adapter_watts","external_connected","fully_charged","is_charging"],"metadata.environment.python_packages":["mlx","mlx-lm","transformers"],"metadata.environment.python_packages.mlx":["present","version"],"metadata.environment.python_packages.mlx-lm":["present","version"],"metadata.environment.python_packages.transformers":["present","version"],"metadata.environment_admission":["attempts","claim_reason","critical_environment_passed","decision","failure","guard_observations","idle_admission_extension","on_fail","per_run_environment_evaluation","policy_version","reference_provenance_present","schema_version"],"metadata.environment_admission.attempts[]":["admitted","attempt","baseline","cpu_admission","cpu_admission_enforced","end_s","gpu_admitted","start_s"],"metadata.environment_admission.attempts[].baseline":["duration_s","gpu_freq_hz_mean","gpu_freq_mhz_mean","gpu_idle_ratio_mean","gpu_idle_ratio_min","idle_window_suspect","power_w_mean","power_w_stddev","sample_count","telemetry_backend"],"metadata.environment_admission.attempts[].cpu_admission":["admitted","conditions","cpu_busy_ratio_p95","criteria","decision","gpu_admitted","processor_combined_power_w_p95","sample_count","schema_version"],"metadata.environment_admission.attempts[].cpu_admission.criteria":["cpu_busy_ratio_p95_max","min_samples","on_missing_telemetry","processor_combined_power_w_p95_max"],"metadata.environment_admission.guard_observations[]":["adapter_power_observation","capture_skipped","display","display_power_state","errors","hid_idle_s","phase","power","screensaver_delay_s","screensaver_engaged","screensaver_module"],"metadata.environment_admission.guard_observations[].adapter_power_observation":["adapter_description","adapter_watts","power_source","source"],"metadata.environment_admission.guard_observations[].display":["active_displays","asleep_display_count","asleep_evidence_count","built_in_display_count","external_display_count","probe","reason","status"],"metadata.environment_admission.guard_observations[].errors":[],"metadata.environment_admission.guard_observations[].power":["adapter_description","adapter_watts","external_connected","fully_charged","is_charging"],"metadata.environment_admission.idle_admission_extension":["claim_bearing","policy_version","schema_version","sha256"],"metadata.environment_admission.per_run_environment_evaluation":["eligible","findings","findings_sha256","load_average_evidence","schema_version","snapshot","snapshot_sha256"],"metadata.environment_admission.per_run_environment_evaluation.findings[]":["actual","code","critical","field","required","status"],"metadata.environment_admission.per_run_environment_evaluation.load_average_evidence":["admission_gate","load_average_15m","load_average_1m","load_average_5m"],"metadata.environment_admission.per_run_environment_evaluation.snapshot":["battery_percent","battery_state","boot_time_s","build_version","capture_scope","capture_skipped","captured_at_s","captured_for_rep","clock_sync","cpu_brand","display","display_power_state","display_sleep_prevented","env_capture_duration_s","errors","hid_idle_s","hw_model","load_average_15m","load_average_1m","load_average_5m","logical_cpu_count","low_power_mode","memory","memory_free_percent","memory_pressure_percent","power","power_source","product_name","product_version","python_packages","screensaver_delay_s","screensaver_engaged","screensaver_module","settle_s","thermal_pressure","thermal_probe_reason","uptime_s"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.clock_sync":["status","timed_probe_error","timed_running"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display":["active_displays","asleep_display_count","asleep_evidence_count","built_in_display_count","external_display_count","framebuffer_pipes_external_capable","framebuffer_pipes_total","probe","reason","status"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.errors":[],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory":["compressor_bytes","page_size_bytes","pageins","pageouts","pages_free","pages_occupied_by_compressor","pages_stored_in_compressor","swap_usage"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.swap_usage":["free","total","used"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power":["adapter_description","adapter_watts","external_connected","fully_charged","is_charging"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages":["mlx","mlx-lm","transformers"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx":["present","version"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx-lm":["present","version"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.transformers":["present","version"],"metadata.idle_baseline":["duration_s","gpu_freq_hz_mean","gpu_freq_mhz_mean","gpu_idle_ratio_mean","gpu_idle_ratio_min","idle_window_suspect","power_w_mean","power_w_stddev","sample_count","telemetry_backend"],"metadata.instrument_calibration":["artifact_path","artifact_sha256","b_fiducial_s","binding_observations","bindings","validation_manifest_path","validation_manifest_sha256","verified_effective_b_fiducial_s"],"metadata.instrument_calibration.binding_observations":["power_policy","powermetrics_sha256"],"metadata.instrument_calibration.bindings":["anchor_method_version","estimator_revision","hardware_model","mlx_version","os_build","power_policy","powermetrics_sha256","protocol_sha256","pulse_protocol_id","sampling_interval_ms"],"metadata.model":["context_window","family","name","revision","source","weight_format"],"metadata.quantization":["bits","group_size","name"],"metadata.source_provenance":["changed_during_run","claim_eligible","diff_identity","end","reason_codes","schema","start"],"metadata.source_provenance.diff_identity":["algorithm","version"],"metadata.source_provenance.end":["diff_sha256","git_commit","staged","tracked","untracked"],"metadata.source_provenance.start":["diff_sha256","git_commit","staged","tracked","untracked"],"metadata.suite":["item_count","manifest_sha256","order_policy","order_row","order_seed","source_file_sha256","suite_id","suite_profile","suite_revision"]},"kinds":{"metadata":["map"],"metadata.adapters":["map"],"metadata.adapters.runtime":["map"],"metadata.adapters.runtime.cleanup_metadata":["map"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots":["list"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[]":["map"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].captured_at_s":["float"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].label":["str"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].mlx_metal":["map"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].mlx_metal.active_memory_bytes":["int"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].mlx_metal.api_available":["bool"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].mlx_metal.cache_memory_bytes":["int"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].mlx_metal.peak_memory_bytes":["int"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].process_rss_bytes":["int"],"metadata.adapters.runtime.name":["str"],"metadata.adapters.runtime.prepare_metadata":["map"],"metadata.adapters.runtime.prepare_metadata.adapter":["str"],"metadata.adapters.runtime.prepare_metadata.load_wall_time_s":["float"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots":["list"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[]":["map"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].captured_at_s":["float"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].label":["str"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].mlx_metal":["map"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].mlx_metal.active_memory_bytes":["int"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].mlx_metal.api_available":["bool"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].mlx_metal.cache_memory_bytes":["int"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].mlx_metal.peak_memory_bytes":["int"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].process_rss_bytes":["int"],"metadata.adapters.runtime.prepare_metadata.mlx_lm_version":["str"],"metadata.adapters.runtime.prepare_metadata.mlx_version":["str"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity":["map"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.algorithm":["str"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.files":["map"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.files.model.safetensors":["str"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.folded_sha256":["str"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.kind":["str"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.root":["str"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.status":["str"],"metadata.adapters.runtime.prepare_metadata.model_config_eos_token_id":["int"],"metadata.adapters.runtime.prepare_metadata.model_config_name":["str"],"metadata.adapters.runtime.prepare_metadata.model_revision":["str"],"metadata.adapters.runtime.prepare_metadata.model_source":["str"],"metadata.adapters.runtime.prepare_metadata.model_source_is_local_path":["bool"],"metadata.adapters.runtime.prepare_metadata.quantization":["str"],"metadata.adapters.runtime.prepare_metadata.transformers_version":["str"],"metadata.adapters.runtime.prepare_metadata.weight_format":["str"],"metadata.adapters.telemetry":["map"],"metadata.adapters.telemetry.name":["str"],"metadata.campaign_environment_preflight":["map"],"metadata.campaign_environment_preflight.admitted":["bool"],"metadata.campaign_environment_preflight.arm_quiet_mode":["map"],"metadata.campaign_environment_preflight.arm_quiet_mode.command":["list"],"metadata.campaign_environment_preflight.arm_quiet_mode.command[]":["str"],"metadata.campaign_environment_preflight.arm_quiet_mode.command_returncode":["int"],"metadata.campaign_environment_preflight.arm_quiet_mode.countdown_s":["int"],"metadata.campaign_environment_preflight.arm_quiet_mode.requested":["bool"],"metadata.campaign_environment_preflight.arm_quiet_mode.verified_by_reprobe":["bool"],"metadata.campaign_environment_preflight.captured_at":["str"],"metadata.campaign_environment_preflight.enforced":["bool"],"metadata.campaign_environment_preflight.evaluation":["map"],"metadata.campaign_environment_preflight.evaluation.eligible":["bool"],"metadata.campaign_environment_preflight.evaluation.findings":["list"],"metadata.campaign_environment_preflight.evaluation.findings[]":["map"],"metadata.campaign_environment_preflight.evaluation.findings[].actual":["bool","str"],"metadata.campaign_environment_preflight.evaluation.findings[].code":["str"],"metadata.campaign_environment_preflight.evaluation.findings[].critical":["bool"],"metadata.campaign_environment_preflight.evaluation.findings[].field":["str"],"metadata.campaign_environment_preflight.evaluation.findings[].required":["bool","str"],"metadata.campaign_environment_preflight.evaluation.findings[].status":["str"],"metadata.campaign_environment_preflight.evaluation.findings_sha256":["str"],"metadata.campaign_environment_preflight.evaluation.load_average_evidence":["map"],"metadata.campaign_environment_preflight.evaluation.load_average_evidence.admission_gate":["bool"],"metadata.campaign_environment_preflight.evaluation.load_average_evidence.load_average_15m":["float"],"metadata.campaign_environment_preflight.evaluation.load_average_evidence.load_average_1m":["float"],"metadata.campaign_environment_preflight.evaluation.load_average_evidence.load_average_5m":["float"],"metadata.campaign_environment_preflight.evaluation.schema_version":["str"],"metadata.campaign_environment_preflight.evaluation.snapshot_sha256":["str"],"metadata.campaign_environment_preflight.initial_findings_sha256":["str"],"metadata.campaign_environment_preflight.initial_snapshot_sha256":["str"],"metadata.campaign_environment_preflight.override":["NoneType"],"metadata.campaign_environment_preflight.policy_sha256":["str"],"metadata.campaign_environment_preflight.schema_version":["str"],"metadata.campaign_environment_preflight.snapshot":["map"],"metadata.campaign_environment_preflight.snapshot.battery_percent":["int"],"metadata.campaign_environment_preflight.snapshot.battery_state":["str"],"metadata.campaign_environment_preflight.snapshot.boot_time_s":["int"],"metadata.campaign_environment_preflight.snapshot.build_version":["str"],"metadata.campaign_environment_preflight.snapshot.clock_sync":["map"],"metadata.campaign_environment_preflight.snapshot.clock_sync.status":["str"],"metadata.campaign_environment_preflight.snapshot.clock_sync.timed_probe_error":["NoneType"],"metadata.campaign_environment_preflight.snapshot.clock_sync.timed_running":["bool"],"metadata.campaign_environment_preflight.snapshot.cpu_brand":["str"],"metadata.campaign_environment_preflight.snapshot.display":["map"],"metadata.campaign_environment_preflight.snapshot.display.active_displays":["int"],"metadata.campaign_environment_preflight.snapshot.display.asleep_display_count":["int"],"metadata.campaign_environment_preflight.snapshot.display.asleep_evidence_count":["int"],"metadata.campaign_environment_preflight.snapshot.display.built_in_display_count":["int"],"metadata.campaign_environment_preflight.snapshot.display.external_display_count":["int"],"metadata.campaign_environment_preflight.snapshot.display.framebuffer_pipes_external_capable":["int"],"metadata.campaign_environment_preflight.snapshot.display.framebuffer_pipes_total":["int"],"metadata.campaign_environment_preflight.snapshot.display.probe":["str"],"metadata.campaign_environment_preflight.snapshot.display.reason":["NoneType"],"metadata.campaign_environment_preflight.snapshot.display.status":["str"],"metadata.campaign_environment_preflight.snapshot.display_power_state":["str"],"metadata.campaign_environment_preflight.snapshot.display_sleep_prevented":["bool"],"metadata.campaign_environment_preflight.snapshot.errors":["map"],"metadata.campaign_environment_preflight.snapshot.hid_idle_s":["float"],"metadata.campaign_environment_preflight.snapshot.hw_model":["str"],"metadata.campaign_environment_preflight.snapshot.load_average_15m":["float"],"metadata.campaign_environment_preflight.snapshot.load_average_1m":["float"],"metadata.campaign_environment_preflight.snapshot.load_average_5m":["float"],"metadata.campaign_environment_preflight.snapshot.logical_cpu_count":["int"],"metadata.campaign_environment_preflight.snapshot.low_power_mode":["bool"],"metadata.campaign_environment_preflight.snapshot.memory":["map"],"metadata.campaign_environment_preflight.snapshot.memory.compressor_bytes":["int"],"metadata.campaign_environment_preflight.snapshot.memory.page_size_bytes":["int"],"metadata.campaign_environment_preflight.snapshot.memory.pageins":["int"],"metadata.campaign_environment_preflight.snapshot.memory.pageouts":["int"],"metadata.campaign_environment_preflight.snapshot.memory.pages_free":["int"],"metadata.campaign_environment_preflight.snapshot.memory.pages_occupied_by_compressor":["int"],"metadata.campaign_environment_preflight.snapshot.memory.pages_stored_in_compressor":["int"],"metadata.campaign_environment_preflight.snapshot.memory.swap_usage":["map"],"metadata.campaign_environment_preflight.snapshot.memory.swap_usage.free":["str"],"metadata.campaign_environment_preflight.snapshot.memory.swap_usage.total":["str"],"metadata.campaign_environment_preflight.snapshot.memory.swap_usage.used":["str"],"metadata.campaign_environment_preflight.snapshot.memory_free_percent":["float"],"metadata.campaign_environment_preflight.snapshot.memory_pressure_percent":["float"],"metadata.campaign_environment_preflight.snapshot.power":["map"],"metadata.campaign_environment_preflight.snapshot.power.adapter_description":["str"],"metadata.campaign_environment_preflight.snapshot.power.adapter_watts":["int"],"metadata.campaign_environment_preflight.snapshot.power.external_connected":["bool"],"metadata.campaign_environment_preflight.snapshot.power.fully_charged":["bool"],"metadata.campaign_environment_preflight.snapshot.power.is_charging":["bool"],"metadata.campaign_environment_preflight.snapshot.power_source":["str"],"metadata.campaign_environment_preflight.snapshot.product_name":["str"],"metadata.campaign_environment_preflight.snapshot.product_version":["str"],"metadata.campaign_environment_preflight.snapshot.python_packages":["map"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx":["map"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx-lm":["map"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx-lm.present":["bool"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx-lm.version":["str"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx.present":["bool"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx.version":["str"],"metadata.campaign_environment_preflight.snapshot.python_packages.transformers":["map"],"metadata.campaign_environment_preflight.snapshot.python_packages.transformers.present":["bool"],"metadata.campaign_environment_preflight.snapshot.python_packages.transformers.version":["str"],"metadata.campaign_environment_preflight.snapshot.screensaver_delay_s":["int"],"metadata.campaign_environment_preflight.snapshot.screensaver_engaged":["bool"],"metadata.campaign_environment_preflight.snapshot.screensaver_module":["str"],"metadata.campaign_environment_preflight.snapshot.thermal_pressure":["str"],"metadata.campaign_environment_preflight.snapshot.thermal_probe_reason":["NoneType"],"metadata.campaign_environment_preflight.snapshot.uptime_s":["float"],"metadata.campaign_policy":["map"],"metadata.campaign_policy.calibration_bracketing":["map"],"metadata.campaign_policy.calibration_bracketing.calibration_bracket_max_drift_s":["float"],"metadata.campaign_policy.calibration_bracketing.require_bracket":["bool"],"metadata.campaign_policy.idle_admission_extension":["map"],"metadata.campaign_policy.idle_admission_extension.claim_bearing":["bool"],"metadata.campaign_policy.idle_admission_extension.policy_version":["str"],"metadata.campaign_policy.idle_admission_extension.schema_version":["str"],"metadata.campaign_policy.idle_admission_extension.sha256":["str"],"metadata.campaign_policy.policy_id":["str"],"metadata.campaign_policy.policy_version":["str"],"metadata.campaign_policy.profile":["str"],"metadata.campaign_policy.schema_version":["str"],"metadata.campaign_policy.sha256":["str"],"metadata.campaign_policy.source":["str"],"metadata.clock":["map"],"metadata.clock.kind":["str"],"metadata.clock.monotonic_minus_wall_s":["float"],"metadata.clock.monotonic_resolution_s":["float"],"metadata.clock.wall_minus_monotonic_end_s":["float"],"metadata.clock.wall_minus_monotonic_start_s":["float"],"metadata.clock.wall_resolution_s":["float"],"metadata.config_sha256":["str"],"metadata.config_warnings":["list"],"metadata.connection":["map"],"metadata.connection.host":["str"],"metadata.connection.transport":["str"],"metadata.device":["map"],"metadata.device.boundary":["str"],"metadata.device.capability_precheck":["map"],"metadata.device.capability_precheck.ok":["bool"],"metadata.device.device":["str"],"metadata.device.hw_model":["str"],"metadata.device.kern_bootargs":["str"],"metadata.device.kern_boottime":["int"],"metadata.device.kern_osversion":["str"],"metadata.device.plist_anchor_offset_s":["float"],"metadata.device.power_units":["str"],"metadata.device.powermetrics":["map"],"metadata.device.powermetrics.executable_path":["str"],"metadata.device.powermetrics.executable_sha256":["str"],"metadata.device.powermetrics.samplers_available":["list"],"metadata.device.powermetrics.samplers_available[]":["str"],"metadata.device.powermetrics.samplers_probe":["map"],"metadata.device.powermetrics.samplers_probe.method":["str"],"metadata.device.powermetrics.samplers_probe.ok":["bool"],"metadata.device.powermetrics.samplers_requested":["str"],"metadata.device.rail_manifest":["list"],"metadata.device.rail_manifest[]":["str"],"metadata.device.telemetry":["str"],"metadata.device.timestamp_derivation":["str"],"metadata.environment":["map"],"metadata.environment.battery_percent":["int"],"metadata.environment.battery_state":["str"],"metadata.environment.boot_time_s":["int"],"metadata.environment.build_version":["str"],"metadata.environment.capture_scope":["str"],"metadata.environment.capture_skipped":["bool"],"metadata.environment.captured_at_s":["float"],"metadata.environment.captured_for_rep":["NoneType"],"metadata.environment.clock_sync":["map"],"metadata.environment.clock_sync.status":["str"],"metadata.environment.clock_sync.timed_probe_error":["NoneType"],"metadata.environment.clock_sync.timed_running":["bool"],"metadata.environment.cpu_brand":["str"],"metadata.environment.display":["map"],"metadata.environment.display.active_displays":["int"],"metadata.environment.display.asleep_display_count":["int"],"metadata.environment.display.asleep_evidence_count":["int"],"metadata.environment.display.built_in_display_count":["int"],"metadata.environment.display.external_display_count":["int"],"metadata.environment.display.framebuffer_pipes_external_capable":["int"],"metadata.environment.display.framebuffer_pipes_total":["int"],"metadata.environment.display.probe":["str"],"metadata.environment.display.reason":["NoneType"],"metadata.environment.display.status":["str"],"metadata.environment.display_power_state":["str"],"metadata.environment.display_sleep_prevented":["bool"],"metadata.environment.env_capture_duration_s":["float"],"metadata.environment.errors":["map"],"metadata.environment.hid_idle_s":["float"],"metadata.environment.hw_model":["str"],"metadata.environment.load_average_15m":["float"],"metadata.environment.load_average_1m":["float"],"metadata.environment.load_average_5m":["float"],"metadata.environment.logical_cpu_count":["int"],"metadata.environment.low_power_mode":["bool"],"metadata.environment.memory":["map"],"metadata.environment.memory.compressor_bytes":["int"],"metadata.environment.memory.page_size_bytes":["int"],"metadata.environment.memory.pageins":["int"],"metadata.environment.memory.pageouts":["int"],"metadata.environment.memory.pages_free":["int"],"metadata.environment.memory.pages_occupied_by_compressor":["int"],"metadata.environment.memory.pages_stored_in_compressor":["int"],"metadata.environment.memory.swap_usage":["map"],"metadata.environment.memory.swap_usage.free":["str"],"metadata.environment.memory.swap_usage.total":["str"],"metadata.environment.memory.swap_usage.used":["str"],"metadata.environment.memory_free_percent":["float"],"metadata.environment.memory_pressure_percent":["float"],"metadata.environment.power":["map"],"metadata.environment.power.adapter_description":["str"],"metadata.environment.power.adapter_watts":["int"],"metadata.environment.power.external_connected":["bool"],"metadata.environment.power.fully_charged":["bool"],"metadata.environment.power.is_charging":["bool"],"metadata.environment.power_source":["str"],"metadata.environment.product_name":["str"],"metadata.environment.product_version":["str"],"metadata.environment.python_packages":["map"],"metadata.environment.python_packages.mlx":["map"],"metadata.environment.python_packages.mlx-lm":["map"],"metadata.environment.python_packages.mlx-lm.present":["bool"],"metadata.environment.python_packages.mlx-lm.version":["str"],"metadata.environment.python_packages.mlx.present":["bool"],"metadata.environment.python_packages.mlx.version":["str"],"metadata.environment.python_packages.transformers":["map"],"metadata.environment.python_packages.transformers.present":["bool"],"metadata.environment.python_packages.transformers.version":["str"],"metadata.environment.screensaver_delay_s":["int"],"metadata.environment.screensaver_engaged":["bool"],"metadata.environment.screensaver_module":["str"],"metadata.environment.settle_s":["float"],"metadata.environment.thermal_pressure":["str"],"metadata.environment.thermal_probe_reason":["NoneType"],"metadata.environment.uptime_s":["float"],"metadata.environment_admission":["map"],"metadata.environment_admission.attempts":["list"],"metadata.environment_admission.attempts[]":["map"],"metadata.environment_admission.attempts[].admitted":["bool"],"metadata.environment_admission.attempts[].attempt":["int"],"metadata.environment_admission.attempts[].baseline":["map"],"metadata.environment_admission.attempts[].baseline.duration_s":["float"],"metadata.environment_admission.attempts[].baseline.gpu_freq_hz_mean":["float"],"metadata.environment_admission.attempts[].baseline.gpu_freq_mhz_mean":["float"],"metadata.environment_admission.attempts[].baseline.gpu_idle_ratio_mean":["float"],"metadata.environment_admission.attempts[].baseline.gpu_idle_ratio_min":["float"],"metadata.environment_admission.attempts[].baseline.idle_window_suspect":["bool"],"metadata.environment_admission.attempts[].baseline.power_w_mean":["float"],"metadata.environment_admission.attempts[].baseline.power_w_stddev":["float"],"metadata.environment_admission.attempts[].baseline.sample_count":["int"],"metadata.environment_admission.attempts[].baseline.telemetry_backend":["str"],"metadata.environment_admission.attempts[].cpu_admission":["map"],"metadata.environment_admission.attempts[].cpu_admission.admitted":["bool"],"metadata.environment_admission.attempts[].cpu_admission.conditions":["list"],"metadata.environment_admission.attempts[].cpu_admission.conditions[]":["str"],"metadata.environment_admission.attempts[].cpu_admission.cpu_busy_ratio_p95":["float"],"metadata.environment_admission.attempts[].cpu_admission.criteria":["map"],"metadata.environment_admission.attempts[].cpu_admission.criteria.cpu_busy_ratio_p95_max":["float"],"metadata.environment_admission.attempts[].cpu_admission.criteria.min_samples":["int"],"metadata.environment_admission.attempts[].cpu_admission.criteria.on_missing_telemetry":["str"],"metadata.environment_admission.attempts[].cpu_admission.criteria.processor_combined_power_w_p95_max":["float"],"metadata.environment_admission.attempts[].cpu_admission.decision":["str"],"metadata.environment_admission.attempts[].cpu_admission.gpu_admitted":["bool"],"metadata.environment_admission.attempts[].cpu_admission.processor_combined_power_w_p95":["float"],"metadata.environment_admission.attempts[].cpu_admission.sample_count":["int"],"metadata.environment_admission.attempts[].cpu_admission.schema_version":["str"],"metadata.environment_admission.attempts[].cpu_admission_enforced":["bool"],"metadata.environment_admission.attempts[].end_s":["float"],"metadata.environment_admission.attempts[].gpu_admitted":["bool"],"metadata.environment_admission.attempts[].start_s":["float"],"metadata.environment_admission.claim_reason":["str"],"metadata.environment_admission.critical_environment_passed":["bool"],"metadata.environment_admission.decision":["str"],"metadata.environment_admission.failure":["str"],"metadata.environment_admission.guard_observations":["list"],"metadata.environment_admission.guard_observations[]":["map"],"metadata.environment_admission.guard_observations[].adapter_power_observation":["map"],"metadata.environment_admission.guard_observations[].adapter_power_observation.adapter_description":["str"],"metadata.environment_admission.guard_observations[].adapter_power_observation.adapter_watts":["float"],"metadata.environment_admission.guard_observations[].adapter_power_observation.power_source":["NoneType"],"metadata.environment_admission.guard_observations[].adapter_power_observation.source":["str"],"metadata.environment_admission.guard_observations[].capture_skipped":["bool"],"metadata.environment_admission.guard_observations[].display":["map"],"metadata.environment_admission.guard_observations[].display.active_displays":["int"],"metadata.environment_admission.guard_observations[].display.asleep_display_count":["int"],"metadata.environment_admission.guard_observations[].display.asleep_evidence_count":["int"],"metadata.environment_admission.guard_observations[].display.built_in_display_count":["int"],"metadata.environment_admission.guard_observations[].display.external_display_count":["int"],"metadata.environment_admission.guard_observations[].display.probe":["str"],"metadata.environment_admission.guard_observations[].display.reason":["NoneType"],"metadata.environment_admission.guard_observations[].display.status":["str"],"metadata.environment_admission.guard_observations[].display_power_state":["str"],"metadata.environment_admission.guard_observations[].errors":["map"],"metadata.environment_admission.guard_observations[].hid_idle_s":["float"],"metadata.environment_admission.guard_observations[].phase":["str"],"metadata.environment_admission.guard_observations[].power":["map"],"metadata.environment_admission.guard_observations[].power.adapter_description":["str"],"metadata.environment_admission.guard_observations[].power.adapter_watts":["int"],"metadata.environment_admission.guard_observations[].power.external_connected":["bool"],"metadata.environment_admission.guard_observations[].power.fully_charged":["bool"],"metadata.environment_admission.guard_observations[].power.is_charging":["bool"],"metadata.environment_admission.guard_observations[].screensaver_delay_s":["int"],"metadata.environment_admission.guard_observations[].screensaver_engaged":["bool"],"metadata.environment_admission.guard_observations[].screensaver_module":["str"],"metadata.environment_admission.idle_admission_extension":["map"],"metadata.environment_admission.idle_admission_extension.claim_bearing":["bool"],"metadata.environment_admission.idle_admission_extension.policy_version":["str"],"metadata.environment_admission.idle_admission_extension.schema_version":["str"],"metadata.environment_admission.idle_admission_extension.sha256":["str"],"metadata.environment_admission.on_fail":["str"],"metadata.environment_admission.per_run_environment_evaluation":["map"],"metadata.environment_admission.per_run_environment_evaluation.eligible":["bool"],"metadata.environment_admission.per_run_environment_evaluation.findings":["list"],"metadata.environment_admission.per_run_environment_evaluation.findings[]":["map"],"metadata.environment_admission.per_run_environment_evaluation.findings[].actual":["bool","str"],"metadata.environment_admission.per_run_environment_evaluation.findings[].code":["str"],"metadata.environment_admission.per_run_environment_evaluation.findings[].critical":["bool"],"metadata.environment_admission.per_run_environment_evaluation.findings[].field":["str"],"metadata.environment_admission.per_run_environment_evaluation.findings[].required":["bool","str"],"metadata.environment_admission.per_run_environment_evaluation.findings[].status":["str"],"metadata.environment_admission.per_run_environment_evaluation.findings_sha256":["str"],"metadata.environment_admission.per_run_environment_evaluation.load_average_evidence":["map"],"metadata.environment_admission.per_run_environment_evaluation.load_average_evidence.admission_gate":["bool"],"metadata.environment_admission.per_run_environment_evaluation.load_average_evidence.load_average_15m":["float"],"metadata.environment_admission.per_run_environment_evaluation.load_average_evidence.load_average_1m":["float"],"metadata.environment_admission.per_run_environment_evaluation.load_average_evidence.load_average_5m":["float"],"metadata.environment_admission.per_run_environment_evaluation.schema_version":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.battery_percent":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.battery_state":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.boot_time_s":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.build_version":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.capture_scope":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.capture_skipped":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.captured_at_s":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.captured_for_rep":["NoneType"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.clock_sync":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.clock_sync.status":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.clock_sync.timed_probe_error":["NoneType"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.clock_sync.timed_running":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.cpu_brand":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.active_displays":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.asleep_display_count":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.asleep_evidence_count":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.built_in_display_count":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.external_display_count":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.framebuffer_pipes_external_capable":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.framebuffer_pipes_total":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.probe":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.reason":["NoneType"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.status":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display_power_state":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display_sleep_prevented":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.env_capture_duration_s":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.errors":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.hid_idle_s":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.hw_model":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.load_average_15m":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.load_average_1m":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.load_average_5m":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.logical_cpu_count":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.low_power_mode":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.compressor_bytes":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.page_size_bytes":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.pageins":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.pageouts":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.pages_free":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.pages_occupied_by_compressor":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.pages_stored_in_compressor":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.swap_usage":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.swap_usage.free":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.swap_usage.total":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.swap_usage.used":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory_free_percent":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory_pressure_percent":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.adapter_description":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.adapter_watts":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.external_connected":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.fully_charged":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.is_charging":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power_source":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.product_name":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.product_version":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx-lm":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx-lm.present":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx-lm.version":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx.present":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx.version":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.transformers":["map"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.transformers.present":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.transformers.version":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.screensaver_delay_s":["int"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.screensaver_engaged":["bool"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.screensaver_module":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.settle_s":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.thermal_pressure":["str"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.thermal_probe_reason":["NoneType"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.uptime_s":["float"],"metadata.environment_admission.per_run_environment_evaluation.snapshot_sha256":["str"],"metadata.environment_admission.policy_version":["str"],"metadata.environment_admission.reference_provenance_present":["bool"],"metadata.environment_admission.schema_version":["str"],"metadata.git_commit":["str"],"metadata.idle_baseline":["map"],"metadata.idle_baseline.duration_s":["float"],"metadata.idle_baseline.gpu_freq_hz_mean":["float"],"metadata.idle_baseline.gpu_freq_mhz_mean":["float"],"metadata.idle_baseline.gpu_idle_ratio_mean":["float"],"metadata.idle_baseline.gpu_idle_ratio_min":["float"],"metadata.idle_baseline.idle_window_suspect":["bool"],"metadata.idle_baseline.power_w_mean":["float"],"metadata.idle_baseline.power_w_stddev":["float"],"metadata.idle_baseline.sample_count":["int"],"metadata.idle_baseline.telemetry_backend":["str"],"metadata.instrument_calibration":["map"],"metadata.instrument_calibration.artifact_path":["str"],"metadata.instrument_calibration.artifact_sha256":["str"],"metadata.instrument_calibration.b_fiducial_s":["float"],"metadata.instrument_calibration.binding_observations":["map"],"metadata.instrument_calibration.binding_observations.power_policy":["str"],"metadata.instrument_calibration.binding_observations.powermetrics_sha256":["str"],"metadata.instrument_calibration.bindings":["map"],"metadata.instrument_calibration.bindings.anchor_method_version":["str"],"metadata.instrument_calibration.bindings.estimator_revision":["str"],"metadata.instrument_calibration.bindings.hardware_model":["str"],"metadata.instrument_calibration.bindings.mlx_version":["str"],"metadata.instrument_calibration.bindings.os_build":["str"],"metadata.instrument_calibration.bindings.power_policy":["str"],"metadata.instrument_calibration.bindings.powermetrics_sha256":["str"],"metadata.instrument_calibration.bindings.protocol_sha256":["str"],"metadata.instrument_calibration.bindings.pulse_protocol_id":["str"],"metadata.instrument_calibration.bindings.sampling_interval_ms":["int"],"metadata.instrument_calibration.validation_manifest_path":["str"],"metadata.instrument_calibration.validation_manifest_sha256":["str"],"metadata.instrument_calibration.verified_effective_b_fiducial_s":["float"],"metadata.joulewise_version":["str"],"metadata.machine":["str"],"metadata.model":["map"],"metadata.model.context_window":["int"],"metadata.model.family":["str"],"metadata.model.name":["str"],"metadata.model.revision":["str"],"metadata.model.source":["str"],"metadata.model.weight_format":["str"],"metadata.platform":["str"],"metadata.python_version":["str"],"metadata.quantization":["map"],"metadata.quantization.bits":["int"],"metadata.quantization.group_size":["NoneType"],"metadata.quantization.name":["str"],"metadata.run_id":["str"],"metadata.schema_version":["str"],"metadata.source_provenance":["map"],"metadata.source_provenance.changed_during_run":["bool"],"metadata.source_provenance.claim_eligible":["bool"],"metadata.source_provenance.diff_identity":["map"],"metadata.source_provenance.diff_identity.algorithm":["str"],"metadata.source_provenance.diff_identity.version":["str"],"metadata.source_provenance.end":["map"],"metadata.source_provenance.end.diff_sha256":["str"],"metadata.source_provenance.end.git_commit":["str"],"metadata.source_provenance.end.staged":["str"],"metadata.source_provenance.end.tracked":["str"],"metadata.source_provenance.end.untracked":["str"],"metadata.source_provenance.reason_codes":["list"],"metadata.source_provenance.reason_codes[]":["str"],"metadata.source_provenance.schema":["str"],"metadata.source_provenance.start":["map"],"metadata.source_provenance.start.diff_sha256":["str"],"metadata.source_provenance.start.git_commit":["str"],"metadata.source_provenance.start.staged":["str"],"metadata.source_provenance.start.tracked":["str"],"metadata.source_provenance.start.untracked":["str"],"metadata.suite":["map"],"metadata.suite.item_count":["int"],"metadata.suite.manifest_sha256":["str"],"metadata.suite.order_policy":["str"],"metadata.suite.order_row":["int"],"metadata.suite.order_seed":["str"],"metadata.suite.source_file_sha256":["str"],"metadata.suite.suite_id":["str"],"metadata.suite.suite_profile":["str"],"metadata.suite.suite_revision":["str"]},"values":{"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].label":["cleanup_start"],"metadata.adapters.runtime.cleanup_metadata.memory_snapshots[].mlx_metal.api_available":[true],"metadata.adapters.runtime.name":["mlx"],"metadata.adapters.runtime.prepare_metadata.adapter":["mlx_runtime"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].label":["prepare_end"],"metadata.adapters.runtime.prepare_metadata.memory_snapshots[].mlx_metal.api_available":[true],"metadata.adapters.runtime.prepare_metadata.mlx_lm_version":["0.31.3"],"metadata.adapters.runtime.prepare_metadata.mlx_version":["0.31.2"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.algorithm":["sha256"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.files.model.safetensors":["0979f33d1bc58afcf696d13f57977644e7b11a6f0eec3e631d8e9463d18c0717"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.folded_sha256":["fea4cb940b54448a693c95a0734949cbdca21a39dda990d669b7f615e4a7c712"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.kind":["file_set"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.root":["/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit"],"metadata.adapters.runtime.prepare_metadata.model_artifact_identity.status":["ok"],"metadata.adapters.runtime.prepare_metadata.model_config_name":["qwen2"],"metadata.adapters.runtime.prepare_metadata.model_revision":["8b403126fc14f14cfc99bb4cfa72ecbc129ea677"],"metadata.adapters.runtime.prepare_metadata.model_source":["/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit"],"metadata.adapters.runtime.prepare_metadata.model_source_is_local_path":[true],"metadata.adapters.runtime.prepare_metadata.quantization":["int4"],"metadata.adapters.runtime.prepare_metadata.transformers_version":["5.12.1"],"metadata.adapters.runtime.prepare_metadata.weight_format":["mlx"],"metadata.adapters.telemetry.name":["powermetrics"],"metadata.campaign_environment_preflight.admitted":[true],"metadata.campaign_environment_preflight.arm_quiet_mode.command[]":["displaysleepnow","pmset"],"metadata.campaign_environment_preflight.arm_quiet_mode.requested":[true],"metadata.campaign_environment_preflight.arm_quiet_mode.verified_by_reprobe":[true],"metadata.campaign_environment_preflight.captured_at":["2026-07-23T02:37:06.249678Z","2026-07-23T02:45:09.824989Z","2026-07-23T04:46:11.746695Z","2026-07-23T04:55:18.775134Z","2026-07-23T04:57:54.636205Z","2026-07-23T05:00:30.660312Z","2026-07-23T05:03:06.338007Z","2026-07-23T05:05:42.389882Z","2026-07-23T05:08:17.771972Z","2026-07-23T05:10:53.315236Z","2026-07-23T05:13:28.771549Z","2026-07-23T05:16:05.611153Z","2026-07-23T05:18:41.131619Z","2026-07-23T05:21:17.689577Z","2026-07-23T08:59:43.242395Z","2026-07-23T10:04:48.951463Z","2026-07-23T12:08:31.011175Z","2026-07-23T12:19:08.840564Z","2026-07-24T01:45:23.298828Z","2026-07-24T02:29:34.270028Z","2026-07-24T04:41:32.585962Z","2026-07-24T05:12:36.107517Z","2026-07-24T06:18:38.745550Z","2026-08-01T10:47:19.701837Z","2026-08-01T12:08:56.687048Z","2026-08-01T13:21:44.431008Z"],"metadata.campaign_environment_preflight.enforced":[true],"metadata.campaign_environment_preflight.evaluation.eligible":[true],"metadata.campaign_environment_preflight.evaluation.findings[].actual":[false,true,"AC Power","all_asleep","nominal"],"metadata.campaign_environment_preflight.evaluation.findings[].code":["display_not_all_asleep","external_power_not_connected","low_power_mode_enabled","power_source_not_ac","screensaver_engaged","thermal_not_nominal"],"metadata.campaign_environment_preflight.evaluation.findings[].critical":[true],"metadata.campaign_environment_preflight.evaluation.findings[].field":["display_power_state","low_power_mode","power.external_connected","power_source","screensaver_engaged","thermal_pressure"],"metadata.campaign_environment_preflight.evaluation.findings[].required":[false,true,"AC Power","all_asleep","nominal"],"metadata.campaign_environment_preflight.evaluation.findings[].status":["pass"],"metadata.campaign_environment_preflight.evaluation.findings_sha256":["dd9f19b39b77c0770f62e3abf1a19d9db4b614f2ff6ccae70cc5fcbf404be3e6"],"metadata.campaign_environment_preflight.evaluation.load_average_evidence.admission_gate":[false],"metadata.campaign_environment_preflight.evaluation.schema_version":["joulewise.environment_evaluation.v1"],"metadata.campaign_environment_preflight.evaluation.snapshot_sha256":["22b46548071e0a1abba291f3fc2c17cbe0a3423dce69c5305eda575a820372e7","2906f08de8a56cd66a991bbc682e4cfde4135df83148609fa2e3ba886b8a91a3","2fc3dc22f130ebe6f09c45fd0b24f2514dba13e9e0f65e1f415be014787f00a0","33d433921a12292ccff78c27ec7c909e85e631f7d91739fe93462423ac32bf76","419fed2303679c26684e48cd1731708f3a936b96dab87aea555a2af6b866b356","41a69305b52164def0744d7469da1eea0f44bcbad99381bddb41b9da03997e8a","42c8330602e8c81a4a7b7133b9eb3412e662f85537bbeb264e05bf0bb2593f88","4ad43f955216030d335480a41835a181f2f56d7f451b88b754b633bef50ae0d0","5aea54bb678c623fb7ec76de460d55626dc3938b8e09011f87bf28135762e2fa","5f74d8f0a363b2ef2ceb50cf4009fee70cffa0e5a149b042922cae62128359e0","646fb0770c230dd69c7d57f94134910a3e48c8a5aadc8a584e11c3c4225aa28a","6d8d5ade8acc54823bf1c02c85abfba963ebf87ab20cb79c385904e73aaa26ba","83f9bc8eaefd90830d9a7537e6a0c1411a9d9bd40631abcbbeab05cd9969090b","8c7436b773a011aa1283cd3e346cc896641f4a182cbd5f62041eb96c9fff128e","a06fa0a56f108c1fbd6e122fdbff7717949427724726a3985fe426003c8bca1b","a321393372dac27b6a2702562747234a638e13cb6c8ef3f21633f6afdb342851","a44880bc2727318ea0770aa7fba4ab736880eccd2e45952c455f290719ee16e0","a45a46f6bff79e99fd4700e002a569f9df63765e5e193b8bb4b80ddc9a631f1c","b9d40e7392c9ea22304623f4d18e68ae013b1f4f437bb67b754e0524a4f74b96","bd17700b85e4ac4bc24e68b50956bab2ac388b49fe6e65d891b7d7152129f493","bfeedc748577be0e84a5fd0f09cb762155d67d69a1ec575a06ea2a9a59aa4335","dab4282a63284e3e26a82c84b27d420f944f0ca56a72d9e81fbb52d738f63e15","dd2c6a078511ff432a588b40dc00ad3a39f0e6dee6e00e55e5f9f160d796f4ff","e5787646f8b7d33170ce83761e45bb378df4596f6215272711f047101c0cb738","e8b7bd4efac27f347770a0078cd29dafe2e65e5152030eb1e960764f79421ffb","fb439eab585e2b7cb907d75b7841e9e483451158d129a6a00e424296768f0802"],"metadata.campaign_environment_preflight.initial_findings_sha256":["dd9f19b39b77c0770f62e3abf1a19d9db4b614f2ff6ccae70cc5fcbf404be3e6"],"metadata.campaign_environment_preflight.initial_snapshot_sha256":["0326aaab84bc3708e47de9866b938781ee2b2d5cac0304ccbb3353e3a05fefbf","0a205bf66b6a75a4aa94d9d7515fbd1a2eddb595760c3b5bc3c1685c640aca53","0a9d07f98a48ac367ff97632bf3c85a2560d714997b881181a217de1ef553b83","3116d67b387caab8b2479113327fb24832282ec73fec3ca89d2fd250c00cd5ff","379a3597465e47209ade0e92058a5f1d62f33b2fceec68e74a43977322b9f0b5","3efea46b32a8c6413c213c98d653a157a142140e20b3ce86e557c6076861da9a","4596fbedc227d3b6654a2e7a40831403272ccaf66a14c0bc93da051e30866942","55480f49784080a32956bc5cd8fad0660594ff3ccfdaf4d81edfa3c6241f055a","59b4f0b288fba8c315ba55a5ff8a61b2e622839ae46fde819e1e3f72a5f56930","5d3fdd345634215b2c63cd0de04232ced27a240b4ecf19631800e6b540dfd7c9","6a37a0b0472a0fa85d9e84edba2ffcb45842fd18707c3f468b32cbe9f3e4523b","89d7acf0607a608c36116a7e9b9a8c40f548deb988a7be8e572b934926e10f1a","8cd7e1bf372a483009c7d63569b1f116918e705d8053e7d72a6fb2ebf0f579e8","91a884a9302c5100ce78db7294e7c1fd6f4ab27f14e90270e478ad1f7ea80dba","9dd76a0afc3380651c9470da69ad27ed642f9f71ec32037518f9a390b49a87f7","ab949ee205a4bcb9611ba751708e022c9826020f684018e2308d27c30f0c22bc","ac57f35160e09233c96cca39afa7138ec17c2f42dd4e045f6d6cab12d7a8c460","ac766314aa9e99994d2ff7ec07f8c252e553a4be4828d957768e01970627715d","b25870a2f7c9baf3b6da1db6a2e8f85c840c995720d3a8ab79a2a98bb0844e37","ba2e08eec32260f8a1c4277160fdaaa681678d68fc60d5f79c278de72b20baff","c5cb2e5e337c5d9706b030f35377edab8a2e1cbaf4db312a2466f1d956146bc0","cfe9a6d93cbd296f88aa95df4347b03b52f4b3d071174a3e4524ecc94e985656","e473264cbfeb837b9fed16feefea32850d7370cc876220ca3170daecec42f944","ee93dd5bff66415bc303fcdbfa5ec4e4526d0ca40e794942630c6a8b625e4160","ef96d88075dbbd84afc20dadf9ca6f5cebc5cecbeb5505b3bc400ad93265dfa6","fcf71398a068b3622c67bd7e15eab3ce463ae49bcfb7b38d1aee2764c355e6a7"],"metadata.campaign_environment_preflight.override":[null],"metadata.campaign_environment_preflight.policy_sha256":["b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd"],"metadata.campaign_environment_preflight.schema_version":["joulewise.campaign_environment_preflight.v1"],"metadata.campaign_environment_preflight.snapshot.battery_state":["AC attached","charged"],"metadata.campaign_environment_preflight.snapshot.build_version":["25F84"],"metadata.campaign_environment_preflight.snapshot.clock_sync.status":["limited_without_admin"],"metadata.campaign_environment_preflight.snapshot.clock_sync.timed_probe_error":[null],"metadata.campaign_environment_preflight.snapshot.clock_sync.timed_running":[true],"metadata.campaign_environment_preflight.snapshot.cpu_brand":["Apple M3 Max"],"metadata.campaign_environment_preflight.snapshot.display.probe":["system_profiler_spdisplays"],"metadata.campaign_environment_preflight.snapshot.display.reason":[null],"metadata.campaign_environment_preflight.snapshot.display.status":["ok"],"metadata.campaign_environment_preflight.snapshot.display_power_state":["all_asleep"],"metadata.campaign_environment_preflight.snapshot.display_sleep_prevented":[false],"metadata.campaign_environment_preflight.snapshot.hw_model":["Mac15,9"],"metadata.campaign_environment_preflight.snapshot.low_power_mode":[false],"metadata.campaign_environment_preflight.snapshot.memory.swap_usage.free":["0.00M"],"metadata.campaign_environment_preflight.snapshot.memory.swap_usage.total":["0.00M"],"metadata.campaign_environment_preflight.snapshot.memory.swap_usage.used":["0.00M"],"metadata.campaign_environment_preflight.snapshot.power.adapter_description":["pd charger"],"metadata.campaign_environment_preflight.snapshot.power.external_connected":[true],"metadata.campaign_environment_preflight.snapshot.power.fully_charged":[false,true],"metadata.campaign_environment_preflight.snapshot.power.is_charging":[false],"metadata.campaign_environment_preflight.snapshot.power_source":["AC Power"],"metadata.campaign_environment_preflight.snapshot.product_name":["macOS"],"metadata.campaign_environment_preflight.snapshot.product_version":["26.5.2"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx-lm.present":[true],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx-lm.version":["0.31.3"],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx.present":[true],"metadata.campaign_environment_preflight.snapshot.python_packages.mlx.version":["0.31.2"],"metadata.campaign_environment_preflight.snapshot.python_packages.transformers.present":[true],"metadata.campaign_environment_preflight.snapshot.python_packages.transformers.version":["5.12.1"],"metadata.campaign_environment_preflight.snapshot.screensaver_engaged":[false],"metadata.campaign_environment_preflight.snapshot.screensaver_module":["Ventura"],"metadata.campaign_environment_preflight.snapshot.thermal_pressure":["nominal"],"metadata.campaign_environment_preflight.snapshot.thermal_probe_reason":[null],"metadata.campaign_policy.calibration_bracketing.require_bracket":[true],"metadata.campaign_policy.idle_admission_extension.claim_bearing":[true],"metadata.campaign_policy.idle_admission_extension.policy_version":["idle-admission-core-v1"],"metadata.campaign_policy.idle_admission_extension.schema_version":["joulewise.idle_admission_extension.v1"],"metadata.campaign_policy.idle_admission_extension.sha256":["e664671eb4d39a6cec7c7d28c5f54ebe297bf5e7f0678b346918def7a376c0ad"],"metadata.campaign_policy.policy_id":["quiet-mac-p2-production"],"metadata.campaign_policy.policy_version":["environment-guard-cooldown-v2"],"metadata.campaign_policy.profile":["production"],"metadata.campaign_policy.schema_version":["joulewise.campaign_policy.v1"],"metadata.campaign_policy.sha256":["b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd"],"metadata.campaign_policy.source":["/Users/edr/code/JouleWise/configs/campaign_policies/quiet_mac_p2_production.json","configs/campaign_policies/quiet_mac_p2_production.json"],"metadata.clock.kind":["system"],"metadata.config_sha256":["072d4a718f5bb60148fd0c3967352385eb2d76c46937ba0720b71d6dee895f7e","0988e1b36cd01e947c7ddf28cbfd7edf5aa1405d8526c381fa1901a4eb1f9d44","1e87592aa5fb41e3e1acdd8c1de9d394bc8fa6e6385f1470177d2f2b0fb436ae","32cc7c7f5b7b474886dac01e059297489b497913b98a1aa446d1ef459268edca","39443277e6bc1af9230e0d3eafca8d05c94b4386d498bc5adf4575cd8267e835","3ad211d7d508862dbd6645f5eacab6123acde1a629228f9653a7252aa77f8962","5642d8b9f5f2c0f1caee09d51e47139c5c5c134ead782adefb40156d8da0f982","5dc2d7c06842e9425140a638ad702bd4835502f6bb78b743f103f0302d2823bb","6ae35344540c2f9e09d769f99522b6d26b5fb7327b33c72103d7d814e581fc61","6c803deb71dc22e70ad982f5c6a15123cd4a2ac5c8cc3b2f967f7c557af6c177","a0aaf6c746bd1cf1683165683ba7cf1a9ff09e09d39fa2023a5f47e5d3ef04c6","a57251bc89c5d08cebaf3c1277bead1b8ee5160a42e3fec0a7a9e89b3b41eca1","af5558c80031116e0305dbbc2125ce234bde625aa171abeabae80ad1d0f0efb7","b01949e79eb3e2f40d8b8071ecdee0cec0d6154781b1e28e068962f98d28ae0a","b4899d827116c5e001bfee3e11171aaefaf8664d3397c587c8ced9313e3f6a2e","b9cfe39f5233244e22ab0d3aab9586d10e87847ff098fd9006c1ab84649d6557","c18970dd06ad6858e6efcc034b3415e3dda06e62715d2b17608883123e5ac6df","d6fcc900e9832eed3b23dc022ef38a6bba1933b1aad2adf7eb3ee014e073c1bb","d87d271ed427aec3f24e73a9e3271d14d40fec9a1299ec56905c8513200dae51","d92f9eaf9c9682194f6196a5cb504de8bd21d56b2215aca1867ab7ffd7ca638a"],"metadata.connection.host":["localhost"],"metadata.connection.transport":["local"],"metadata.device.boundary":["Apple SoC CPU + GPU + ANE package power"],"metadata.device.capability_precheck.ok":[true],"metadata.device.device":["macbook_m3_max"],"metadata.device.hw_model":["Mac15,9"],"metadata.device.kern_bootargs":[""],"metadata.device.kern_osversion":["25F84"],"metadata.device.power_units":["powermetrics milliwatts converted to watts"],"metadata.device.powermetrics.executable_path":["/usr/bin/powermetrics"],"metadata.device.powermetrics.executable_sha256":["d1dccad0d0a8016d38bd584bdae283566723096162f06ef663debb4a5762fe69"],"metadata.device.powermetrics.samplers_available[]":["ane_power","cpu_power","gpu_power","thermal"],"metadata.device.powermetrics.samplers_probe.method":["requested_sampler_probe"],"metadata.device.powermetrics.samplers_probe.ok":[true],"metadata.device.powermetrics.samplers_requested":["cpu_power,gpu_power,ane_power,thermal"],"metadata.device.rail_manifest[]":["ane_power","cpu_power","gpu_power"],"metadata.device.telemetry":["powermetrics"],"metadata.device.timestamp_derivation":["current-era timestamp_s anchors record 0's window END to the midpoint of the admissible interval formed by intersecting the censored native whole-second constraints [T_i - q_i, T_i + 1 - q_i) over every record with the causal pre-spawn/first-parse interval mapped through the run wall-minus-monotonic envelope (p2-038.2); records i>0 advance by elapsed_ns for records 1..i. The old spawn bracket is a causal SET constraint, never a midpoint estimate. Exact allowlisted legacy bundles retain plist_anchor_offset_s plus the legacy cumulative-elapsed reconstruction. Each emitted sample carries its [endpoint-elapsed_ns, endpoint) averaging support."],"metadata.environment.battery_state":["AC attached","charged","charging"],"metadata.environment.build_version":["25F84"],"metadata.environment.capture_scope":["run"],"metadata.environment.capture_skipped":[false],"metadata.environment.captured_for_rep":[null],"metadata.environment.clock_sync.status":["limited_without_admin"],"metadata.environment.clock_sync.timed_probe_error":[null],"metadata.environment.clock_sync.timed_running":[true],"metadata.environment.cpu_brand":["Apple M3 Max"],"metadata.environment.display.probe":["system_profiler_spdisplays"],"metadata.environment.display.reason":[null],"metadata.environment.display.status":["ok"],"metadata.environment.display_power_state":["all_asleep"],"metadata.environment.display_sleep_prevented":[false],"metadata.environment.hw_model":["Mac15,9"],"metadata.environment.low_power_mode":[false],"metadata.environment.memory.swap_usage.free":["0.00M"],"metadata.environment.memory.swap_usage.total":["0.00M"],"metadata.environment.memory.swap_usage.used":["0.00M"],"metadata.environment.power.adapter_description":["pd charger"],"metadata.environment.power.external_connected":[true],"metadata.environment.power.fully_charged":[false,true],"metadata.environment.power.is_charging":[false,true],"metadata.environment.power_source":["AC Power"],"metadata.environment.product_name":["macOS"],"metadata.environment.product_version":["26.5.2"],"metadata.environment.python_packages.mlx-lm.present":[true],"metadata.environment.python_packages.mlx-lm.version":["0.31.3"],"metadata.environment.python_packages.mlx.present":[true],"metadata.environment.python_packages.mlx.version":["0.31.2"],"metadata.environment.python_packages.transformers.present":[true],"metadata.environment.python_packages.transformers.version":["5.12.1"],"metadata.environment.screensaver_engaged":[false],"metadata.environment.screensaver_module":["Ventura"],"metadata.environment.thermal_pressure":["nominal"],"metadata.environment.thermal_probe_reason":[null],"metadata.environment_admission.attempts[].admitted":[false],"metadata.environment_admission.attempts[].baseline.idle_window_suspect":[false],"metadata.environment_admission.attempts[].baseline.telemetry_backend":["powermetrics"],"metadata.environment_admission.attempts[].cpu_admission.admitted":[false],"metadata.environment_admission.attempts[].cpu_admission.conditions[]":["cpu_busy_ratio_p95_exceeded","processor_combined_power_w_p95_exceeded"],"metadata.environment_admission.attempts[].cpu_admission.criteria.on_missing_telemetry":["fail"],"metadata.environment_admission.attempts[].cpu_admission.decision":["failed"],"metadata.environment_admission.attempts[].cpu_admission.gpu_admitted":[true],"metadata.environment_admission.attempts[].cpu_admission.schema_version":["joulewise.cpu_idle_admission.v1"],"metadata.environment_admission.attempts[].cpu_admission_enforced":[true],"metadata.environment_admission.attempts[].gpu_admitted":[true],"metadata.environment_admission.claim_reason":["environment_admission_failed"],"metadata.environment_admission.critical_environment_passed":[true],"metadata.environment_admission.decision":["abort"],"metadata.environment_admission.failure":["idle environment admission failed after one retry"],"metadata.environment_admission.guard_observations[].adapter_power_observation.adapter_description":["pd charger"],"metadata.environment_admission.guard_observations[].adapter_power_observation.power_source":[null],"metadata.environment_admission.guard_observations[].adapter_power_observation.source":["admission_guard_observation"],"metadata.environment_admission.guard_observations[].capture_skipped":[false],"metadata.environment_admission.guard_observations[].display.probe":["system_profiler_spdisplays"],"metadata.environment_admission.guard_observations[].display.reason":[null],"metadata.environment_admission.guard_observations[].display.status":["ok"],"metadata.environment_admission.guard_observations[].display_power_state":["all_asleep"],"metadata.environment_admission.guard_observations[].phase":["after_attempt_1","after_attempt_2","before_attempt_1","before_attempt_2"],"metadata.environment_admission.guard_observations[].power.adapter_description":["pd charger"],"metadata.environment_admission.guard_observations[].power.external_connected":[true],"metadata.environment_admission.guard_observations[].power.fully_charged":[false,true],"metadata.environment_admission.guard_observations[].power.is_charging":[false,true],"metadata.environment_admission.guard_observations[].screensaver_engaged":[false],"metadata.environment_admission.guard_observations[].screensaver_module":["Ventura"],"metadata.environment_admission.idle_admission_extension.claim_bearing":[true],"metadata.environment_admission.idle_admission_extension.policy_version":["idle-admission-core-v1"],"metadata.environment_admission.idle_admission_extension.schema_version":["joulewise.idle_admission_extension.v1"],"metadata.environment_admission.idle_admission_extension.sha256":["e664671eb4d39a6cec7c7d28c5f54ebe297bf5e7f0678b346918def7a376c0ad"],"metadata.environment_admission.on_fail":["abort"],"metadata.environment_admission.per_run_environment_evaluation.eligible":[true],"metadata.environment_admission.per_run_environment_evaluation.findings[].actual":[false,true,"AC Power","all_asleep","nominal"],"metadata.environment_admission.per_run_environment_evaluation.findings[].code":["display_not_all_asleep","external_power_not_connected","low_power_mode_enabled","power_source_not_ac","screensaver_engaged","thermal_not_nominal"],"metadata.environment_admission.per_run_environment_evaluation.findings[].critical":[true],"metadata.environment_admission.per_run_environment_evaluation.findings[].field":["display_power_state","low_power_mode","power.external_connected","power_source","screensaver_engaged","thermal_pressure"],"metadata.environment_admission.per_run_environment_evaluation.findings[].required":[false,true,"AC Power","all_asleep","nominal"],"metadata.environment_admission.per_run_environment_evaluation.findings[].status":["pass"],"metadata.environment_admission.per_run_environment_evaluation.findings_sha256":["dd9f19b39b77c0770f62e3abf1a19d9db4b614f2ff6ccae70cc5fcbf404be3e6"],"metadata.environment_admission.per_run_environment_evaluation.load_average_evidence.admission_gate":[false],"metadata.environment_admission.per_run_environment_evaluation.schema_version":["joulewise.environment_evaluation.v1"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.battery_state":["AC attached","charged","charging"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.build_version":["25F84"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.capture_scope":["run"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.capture_skipped":[false],"metadata.environment_admission.per_run_environment_evaluation.snapshot.captured_for_rep":[null],"metadata.environment_admission.per_run_environment_evaluation.snapshot.clock_sync.status":["limited_without_admin"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.clock_sync.timed_probe_error":[null],"metadata.environment_admission.per_run_environment_evaluation.snapshot.clock_sync.timed_running":[true],"metadata.environment_admission.per_run_environment_evaluation.snapshot.cpu_brand":["Apple M3 Max"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.probe":["system_profiler_spdisplays"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.reason":[null],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display.status":["ok"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display_power_state":["all_asleep"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.display_sleep_prevented":[false],"metadata.environment_admission.per_run_environment_evaluation.snapshot.hw_model":["Mac15,9"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.low_power_mode":[false],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.swap_usage.free":["0.00M"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.swap_usage.total":["0.00M"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.memory.swap_usage.used":["0.00M"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.adapter_description":["pd charger"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.external_connected":[true],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.fully_charged":[false,true],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power.is_charging":[false,true],"metadata.environment_admission.per_run_environment_evaluation.snapshot.power_source":["AC Power"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.product_name":["macOS"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.product_version":["26.5.2"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx-lm.present":[true],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx-lm.version":["0.31.3"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx.present":[true],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.mlx.version":["0.31.2"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.transformers.present":[true],"metadata.environment_admission.per_run_environment_evaluation.snapshot.python_packages.transformers.version":["5.12.1"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.screensaver_engaged":[false],"metadata.environment_admission.per_run_environment_evaluation.snapshot.screensaver_module":["Ventura"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.thermal_pressure":["nominal"],"metadata.environment_admission.per_run_environment_evaluation.snapshot.thermal_probe_reason":[null],"metadata.environment_admission.per_run_environment_evaluation.snapshot_sha256":["011058be4dca1d4aceb22355e0eb0111b26f8f2fa7087f32923d7ff714fb73b0","0ce75773f17e5c47ec234a8dbb44c6d7ec3b9c2cdd3aade5b16a404f9f11f49a","0d0f2ad25c75528785ed497779892e791220badd39631b7c833eb9e8d369ac0f","0e28e1a0cc59fb584f8fe2848a467e5a3a525e67cbe279c5c2f5bb0efbd1ae6b","144cf452410f379a16c36252198ee149bd3443502745a0db50458a43ffbda422","15674d6477050d48fd3646625e9ed31d9379f67bd9899e7c3249cb6ca9c68b41","217eed1ea55d3574e78a6e8df251870491cf7fee3ac83b9b48415ee5493738cd","36c2ab49f93f9ef1e6bb47a51a04493eb0cd3abe7bea20d719d658af046a620d","3a9d272ac469d478da90ab60f7edc484a89f541ae7c4e5d16336e31ac1a0b148","6096f72a12a44a64bf95060823dcae14a8a4c7f0969121094056ed4ba39765dc","7ffb59c90fe8e13d650980466281e39629bbcf2419ede3d2854ad9f8786ce49f","8313d532b6ca0ee9e3e14cb615e391b31a35ff5f289dd074900f15bcf6eb140c","98dd00a45419de1bcba08813b4b3964d509c8c13fc3dcefa9e9729cf7f655fe0","9f0645ef2c0d83ae5b6ddb10df0bfd391aee41bcf2f2d60f8746769e5d5a6699","aa768c46ba396770df111d0c855e9aa53999b6593eeca07bbdf345798a3e8f8a","b2b95ca28b1e911fa4fb7ca80ce3d83a7278c2dfafae736c2838dcd380d73ecb","bdb7f0dbabcce69b4a7520bb845785f08b3ee78713f35a20fddbec2d988c24e0","cdcb8c9c394e1e2e59b61fb81ea18b7c0062585d3a428a4c5ea05db7b226cf93","d5584c3ae15d543bd674480e4ac8a5b5599da6645e9d0233fe41eea7e163f23d","d8182bd411e2e0a8acdf047d1b41c7a90d3ff6419f298f1daa784415bf76357e","da0721ecde3cb97d0a5bf69610baad0a0b7e09f5b190fb54ebc3a5b1ba60890c","dcdc5ae46e193605147c0a33a6ca75c4d29d79aff9c93abf7e44b5f01f312f34","e2ff71c515055b535e32a4ac9fc65bd58d7857e1516252fc616d5a6da9ede793","e66d4f728ec05ba1fd38f7f6169eb1d8a4c6573faa9898f317c14fcf6fc2d6c6","e8656e540ef2b3fe69a7d860b2765d00687a812f247a35c74fa3cb4fab067147","ffc091c53539585f116ba59c340aa93bd12824fe26d4ee469bcce2050ad2e458"],"metadata.environment_admission.policy_version":["environment-guard-cooldown-v2"],"metadata.environment_admission.reference_provenance_present":[true],"metadata.environment_admission.schema_version":["joulewise.environment_admission.v1"],"metadata.git_commit":["858b734c8376355f0df49170d3722284539a613a","ba258000f84cef94aa85022609712b75f23952c7","d1498f9ac9e476b4cecc8c40dd93d2b9d6313d39","ee48600ac59a62ab3360225a8576d1b14d0539a8"],"metadata.idle_baseline.idle_window_suspect":[false],"metadata.idle_baseline.telemetry_backend":["powermetrics"],"metadata.instrument_calibration.artifact_path":["instrument_calibration/instrument_evidence.json"],"metadata.instrument_calibration.artifact_sha256":["0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024","148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a","3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea","689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd","71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7","b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f","c1653f369e05e9186d0c6d06231993575ee23c1fd813b96f1094d74dfbaac0ad","e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7","e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803"],"metadata.instrument_calibration.binding_observations.power_policy":["ac_high_power"],"metadata.instrument_calibration.binding_observations.powermetrics_sha256":["d1dccad0d0a8016d38bd584bdae283566723096162f06ef663debb4a5762fe69"],"metadata.instrument_calibration.bindings.anchor_method_version":["powermetrics_native_second_censored_intersection_v1"],"metadata.instrument_calibration.bindings.estimator_revision":["joint_loss_sublevel_interval_branch_v2"],"metadata.instrument_calibration.bindings.hardware_model":["Mac15,9"],"metadata.instrument_calibration.bindings.mlx_version":["0.31.2"],"metadata.instrument_calibration.bindings.os_build":["25F84"],"metadata.instrument_calibration.bindings.power_policy":["ac_high_power"],"metadata.instrument_calibration.bindings.powermetrics_sha256":["d1dccad0d0a8016d38bd584bdae283566723096162f06ef663debb4a5762fe69"],"metadata.instrument_calibration.bindings.protocol_sha256":["9eaf92f85136e234c56ea3ffd34392a73c313d4a092cabf308f5f5aaff9a31b1"],"metadata.instrument_calibration.bindings.pulse_protocol_id":["powermetrics_pulse_fiducial_v3"],"metadata.instrument_calibration.validation_manifest_path":["instrument_calibration/manifest.json"],"metadata.instrument_calibration.validation_manifest_sha256":["0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041","1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005","5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70","7d2967b125324c65e0d57a16950a0e1c2e2946464b7eb89667e8fc2410550149","9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5","baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c","d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe","e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7","ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1"],"metadata.joulewise_version":["0.1.0"],"metadata.machine":["arm64"],"metadata.model.family":["qwen2.5"],"metadata.model.name":["Qwen2.5-1.5B-Instruct-4bit"],"metadata.model.revision":["8b403126fc14f14cfc99bb4cfa72ecbc129ea677"],"metadata.model.source":["/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit"],"metadata.model.weight_format":["mlx"],"metadata.platform":["macOS-26.5.2-arm64-arm-64bit-Mach-O"],"metadata.python_version":["3.13.1"],"metadata.quantization.group_size":[null],"metadata.quantization.name":["int4"],"metadata.run_id":["mtadd-p2048o0128-r08","mtnull-o0512-b04-b2","p2015-df-cmp-abba-ph-decode-b01-a1","p2015-df-cmp-abba-ph-decode-b01-a2","p2015-df-cmp-abba-ph-prefill-b01-a1","p2015-df-cmp-abba-ph-prefill-b01-b2","p2015-df-cmp-abba-ph-prefill-b04-a1","p2015-df-cmp-abba-ph-short-prefill-b01-a1","p2015-df-cmp-abba-rq-b01-a1","p2015-df-cmp-abba-rq-b02-a2","p2015-df-cmp-abba-rq-b03-a1","p2015-df-cmp-abba-su-b01-a1","p2015-df-cmp-abba-su-b07-a2","p2015-df-ph-prefill-abs-r01","p2015-df-rq-long-prompt-abs-r01","p2015-df-rq-mid-abs-r01","p2015-df-su-sentinel-abs-r01","p2015-df-su-sentinel-abs-r04","p2015-neg8-reference-end","p2015-neg8-reference-start"],"metadata.schema_version":["0.1"],"metadata.source_provenance.changed_during_run":[false],"metadata.source_provenance.claim_eligible":[false,true],"metadata.source_provenance.diff_identity.algorithm":["sha256"],"metadata.source_provenance.diff_identity.version":["joulewise.git-diff.nul-v1"],"metadata.source_provenance.end.diff_sha256":["7c9e13b3e28fc9a79a6d5be4981b75ae3eeae4a95becfe879c2af2b77eb0b16a","9db216d2e36733019b90941f0aa339ed1a5d7ed419b2438cc50df61cee5455cb"],"metadata.source_provenance.end.git_commit":["858b734c8376355f0df49170d3722284539a613a","ba258000f84cef94aa85022609712b75f23952c7","d1498f9ac9e476b4cecc8c40dd93d2b9d6313d39","ee48600ac59a62ab3360225a8576d1b14d0539a8"],"metadata.source_provenance.end.staged":["clean"],"metadata.source_provenance.end.tracked":["clean"],"metadata.source_provenance.end.untracked":["clean","dirty"],"metadata.source_provenance.reason_codes[]":["end_untracked_dirty","start_untracked_dirty"],"metadata.source_provenance.schema":["joulewise.source_provenance.v1"],"metadata.source_provenance.start.diff_sha256":["7c9e13b3e28fc9a79a6d5be4981b75ae3eeae4a95becfe879c2af2b77eb0b16a","9db216d2e36733019b90941f0aa339ed1a5d7ed419b2438cc50df61cee5455cb"],"metadata.source_provenance.start.git_commit":["858b734c8376355f0df49170d3722284539a613a","ba258000f84cef94aa85022609712b75f23952c7","d1498f9ac9e476b4cecc8c40dd93d2b9d6313d39","ee48600ac59a62ab3360225a8576d1b14d0539a8"],"metadata.source_provenance.start.staged":["clean"],"metadata.source_provenance.start.tracked":["clean"],"metadata.source_provenance.start.untracked":["clean","dirty"],"metadata.suite.manifest_sha256":["50f7d471300db0a1354a8e7d48f702838fa63f2e359e6738b2259d4389e576d0"],"metadata.suite.order_policy":["manifest_order"],"metadata.suite.order_seed":["9d6a3b26847267711784e5ee074c5cbe9b9ddcadb694716e49da4c5a7a384c77"],"metadata.suite.source_file_sha256":["a97396c29e900058a70d055f3f20255f2959997cfe4843863d63741e476249a1"],"metadata.suite.suite_id":["jw_mixed_v1_sentinel"],"metadata.suite.suite_profile":["jw_mixed_v1_sentinel_512_256"],"metadata.suite.suite_revision":["2026-07-08"]}}
8185-./docs/process_traces/2026-08-03-d111-backfill/test-speed-consult/DESIGN-from-timing-data.md:16:| test_powermetrics_fiducial   |  29.6 |  37 | |
8186-./docs/process_traces/2026-08-03-d111-backfill/test-speed-consult/DESIGN-from-timing-data.md:60:p2038, reduce, bridge, powermetrics_fiducial, controller, cli_run,
8187-./tests/test_p2038_production_path.py:139:    from joulewise.powermetrics_fiducial import (
8188-./tests/test_p2038_production_path.py:200:        "schema_version": "joulewise.instrument_validation_manifest.v1",
8189-./tests/test_schemas.py:225:        # had no required pre/post calibration-bracket declaration.
8190-./docs/process_traces/2026-08-03-d111-backfill/winb_reeval_staged/reeval-evidence.md:85:- Byte-identity replay against that original basis: 70 member occurrences, 210 config/metadata/summary files checked, plus 4 pre/post calibration evidence files; mismatch count **0**.
8191-./docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/COLD-GATE-PACKET-dangling-terminal-semantic.md:43:   only post-calibration retry binds a different T1 power-policy
8192-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:42:        "evidence": "joulewise/calibration_bracketing.py:47-50,317-319; joulewise/powermetrics_fiducial.py:33-38,946-975,1079-1085",
8193-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:149:      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'\nimport shutil,tempfile\nfrom pathlib import Path\nimport joulewise.calibration_bracketing as c\nwith tempfile.TemporaryDirectory() as d:\n root=Path(d)\n for rel in (*c.ESTIMATOR_CODE_PATHS,'joulewise/uncertainty_evidence.py','joulewise/adapters/powermetrics.py'):\n  dst=root/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(Path(rel),dst)\n old=c._REPO_ROOT\n try:\n  c._REPO_ROOT=root\n  print('baseline',c.load_calibration_acceptance_bound() is not None)\n  for rel in ('joulewise/powermetrics_fiducial.py','joulewise/reduce.py','joulewise/uncertainty_evidence.py','joulewise/adapters/powermetrics.py'):\n   p=root/rel; raw=p.read_bytes(); p.write_bytes(raw+b'\\n# byte mutation\\n'); print(rel,c.load_calibration_acceptance_bound() is None); p.write_bytes(raw)\n finally: c._REPO_ROOT=old\nPY",
8194-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:155:          "joulewise/powermetrics_fiducial.py True",
8195:./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:221:F3 — blocker: each production call scans only `runs_root/instrument_validation`. A trigger observed in another window root disappears from all later evaluations unless a human has already rotated the artifact. Recording `"global_runs_root_scan": false` makes the limitation visible but does not satisfy D-102’s mandatory-trigger language. A global filesystem sweep is not the only remedy; an authenticated append-only calibration registry supplied to the selector would also close it.
8196-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/audit-1.md:231:Lines 632–646 test range expansion only for the selected `pre` and `post`. An earlier authenticated same-identity capture outside the n=19 range disappears from trigger evaluation once a newer pre-calibration is selected. The later window then passes under the obsolete artifact as `fresh`.
8197-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-RECOMMENDATION-FOR-ED.md:10:calibration artifacts (scripts/validate_powermetrics_fiducial.py). That
8198-./docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/audit-report-sol-019fbf3c.md:55:  (instrument_validation/20260731T215120-fa1e9cda/instrument_evidence.json:28
8199-./docs/process_traces/2026-08-03-d111-backfill/adjudication_packet_20260801/audit-report-sol-019fbf3c.md:57:  (powermetrics_fiducial.md:77,:109) makes the rejection CORRECT: valid
8200-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/design-consult.md:97:      "cmd": "shasum -a 256 joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py configs/calibration/calibration_acceptance_d079_v2.json; git diff --check",
8201-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/design-consult.md:103:          "21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3  joulewise/powermetrics_fiducial.py",
8202-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/design-consult.md:112:        "tail_regex": "powermetrics_fiducial.py.*uncertainty_evidence.py.*adapters/powermetrics.py.*reduce.py.*calibration_acceptance_d079_v2.json"
8203-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/design-consult.md:243:| `joulewise/powermetrics_fiducial.py` | `rederive_detection_from_artifacts` parses primary evidence and calls the anchor estimator and pulse detector (`931-1085`); `detect_pulses` computes `max(residual edges) + trace_anchor_bound_s` (`825-884`); `verify_stored_evidence_physics` returns `max(stored, freshly rederived)` (`1088-1164`). |
8204-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/design-consult.md:250:`joulewise/powermetrics_fiducial.py`
8205:./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/design-consult.md:285:These requirements do not become optional because a production caller happens to inspect one directory. The artifact itself demonstrates cross-root provenance: its 19 members span `runs_window_a_20260722` through `runs_window_a10_20260725`, while current discovery scans only `runs_root/instrument_validation` at `calibration_bracketing.py:508-519`.
8206-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/impl-report.md:183:      "text": "docs/contracts/powermetrics_fiducial.md still describes the superseded 0.010 hard comparator; D-102 was followed and documentation was explicitly outside WRITE_SCOPE.",
8207-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/impl-report.md:218:The window-A regression still returns both endpoints null because its post-calibration power-policy binding is T1-incompatible.
8208-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:123:      "cmd": "find /Users/edr/code/JouleWise -maxdepth 1 -type d -name 'runs*' -print | wc -l; find /Users/edr/code/JouleWise -maxdepth 4 -type f -path '*/instrument_validation/*/manifest.json' -print | wc -l; find /Users/edr/code/JouleWise -maxdepth 2 -type f -name MANIFEST.sha256 -print | wc -l; find '/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup' -maxdepth 2 -type f -name MANIFEST.sha256 -print 2>/dev/null | wc -l",
8209-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:197:This is not the heavy “registry service threaded through everything” version of A. Repository tracing found exactly one production author of calibration artifacts: [validate_powermetrics_fiducial.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/eaafcc6f-e4c3-4661-b903-3333270ce728/scratchpad/calbracket/scripts/validate_powermetrics_fiducial.py:252). That writer can atomically publish a compact receipt for every valid or failed capture. This makes completeness enforceable at the production boundary and avoids scanning arbitrary runs roots or trusting a caller’s claim that its list is complete.
8210-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:282:2. **Implementation:** New compact ledger/head module and backfill tool; modify `validate_powermetrics_fiducial.py`; update `calibration_bracketing.py`, the acceptance artifact, `whole_window.py`, `run_campaign.py`, and verifier/basis tests. The outer claim consumers can receive a snapshot through `AuthenticatedConsumptionSession`; they do not need individual root lists.
8211-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:290:Ed could instead define one or more custody-parent anchors, require the evaluator to enumerate every matching `instrument_validation/<id>/manifest.json`, and record a digest of the complete directory listings.
8212-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:305:- `runs/instrument_validation` is only a partial aggregation.
8213-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/fix1-report.md:164:      "cmd": "shasum -a 256 configs/calibration/calibration_acceptance_d079_v2.json joulewise/powermetrics_fiducial.py joulewise/reduce.py",
8214-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/fix1-report.md:171:          "21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3  joulewise/powermetrics_fiducial.py",
8215-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/fix1-report.md:239:- FIX-2 — complete. Prospective triggers scan every authenticated same-identity candidate in the supplied set, including unselected range expanders. The acceptance record explicitly identifies that boundary and records that no global runs-root scan occurred. Estimator authentication binds `joulewise/powermetrics_fiducial.py`, which authenticates/rederives `b_fiducial_s`, and `joulewise/reduce.py`, which performs anchor-envelope re-reduction. Those are the code paths D-102 identifies; orchestration and formatting modules were excluded.
8216-./docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/DISPOSITION-FOR-ED.md:27:  joulewise/powermetrics_fiducial.py  (pulse detect + trace-anchor add + physics reverify)
8217-./tests/test_whole_window_selection.py:49:    append_pending_receipt,
8218-./tests/test_whole_window_selection.py:51:    finalize_attempt_receipt,
8219-./tests/test_whole_window_selection.py:52:    head_pin_for_receipt,
8220-./tests/test_whole_window_selection.py:1436:        from joulewise.powermetrics_fiducial import PROTOCOL_ID
8221:./tests/test_whole_window_selection.py:1449:        directory = runs_root / "instrument_validation" / name
8222-./tests/test_whole_window_selection.py:1458:            "schema_version": "joulewise.instrument_validation_manifest.v1",
8223-./tests/test_whole_window_selection.py:2276:        from joulewise.powermetrics_fiducial import PROTOCOL_ID
8224-./tests/test_whole_window_selection.py:2358:                    append_pending_receipt(
8225-./tests/test_whole_window_selection.py:2367:                    final = finalize_attempt_receipt(
8226-./tests/test_whole_window_selection.py:2383:                        json.dumps(head_pin_for_receipt(final)) + "\n",
8227-./tests/test_reduce.py:82:    from joulewise.powermetrics_fiducial import (
8228-./tests/test_reduce.py:186:                    "phase": "instrument_validation",
8229-./tests/test_reduce.py:2760:        from joulewise.powermetrics_fiducial import (
8230-./tests/test_reduce.py:2819:        from joulewise.powermetrics_fiducial import REPLAY_PROTOCOL_V2_SHA256
8231-./tests/test_reduce.py:2850:                    == "powermetrics_pulse_fiducial_v3"
8232-./tests/test_reduce.py:2886:            "schema_version": "joulewise.instrument_validation_manifest.v1",
8233-./tests/test_reduce.py:2906:            evidence.get("protocol_id") == "powermetrics_pulse_fiducial_v2"
--
9674-  4087	        ),
9675-  4088	        baseline_digest=(
9676-  4089	            cutoff.get("head_digest") if isinstance(cutoff, Mapping) else None
9677-  4090	        ),
9678-  4091	    )
9679-  4092	
9680-  4093	
9681-  4094	def idle_admission_core_verdict(
9682-  4095	    evaluations: Sequence[MemberEvaluation],
9683-  4096	    policy_binding: CampaignPolicyBinding,
9684-  4097	    *,
9685-  4098	    whole_window: bool = False,
9686:  4099	    runs_root: Path | None = None,
9687-  4100	    neg8_drift_bound: Mapping[str, Any] | None = None,
9688-  4101	    evaluation_timestamp_s: float | None = None,
9689-  4102	    calibration_ledger_snapshot: CalibrationLedgerSnapshot | None = None,
9690-  4103	) -> dict[str, Any]:
9691-  4104	    """Post-hoc T0.5 idle-admission core surface for the campaign verdict.
9692-  4105	
9693-  4106	    Everything here is recorded data with stable named conditions; the
9694-  4107	    collection verdict and exit code are unchanged by this section.  Live
9695-  4108	    (pre-invoke) enforcement belongs to the controller hookup that follows
9696-  4109	    this core.
9697-  4110	    """
9698-  4111	
--
9774-  4296	            ),
9775-  4297	        )
9776-  4298	    conditions.update(bracket["conditions"])
9777-  4299	    section["adapter_wattage_continuity"] = continuity
9778-  4300	    section["neg8_bracket"] = bracket
9779-  4301	    section["neg8_reference_scientific_config_sha256"] = (
9780-  4302	        identities[0]
9781-  4303	        if identities and not identity_invalid and len(set(identities)) == 1
9782-  4304	        else None
9783-  4305	    )
9784-  4306	    if whole_window:
9785-  4307	        calibration_bracket, calibration_reasons = calibration_bracket_for_bundles(
9786:  4308	            runs_root
9787:  4309	            if runs_root is not None
9788-  4310	            else evaluations[0].bundle_path.parent
9789-  4311	            if evaluations
9790-  4312	            else Path("."),
9791-  4313	            [evaluation.bundle_path for evaluation in evaluations],
9792-  4314	            policy_binding.policy.calibration_bracketing,
9793-  4315	            ledger_snapshot=calibration_ledger_snapshot,
9794-  4316	        )
9795-  4317	        section["instrument_calibration_bracket"] = calibration_bracket
9796-  4318	        if extension.claim_bearing:
9797-  4319	            conditions.update(calibration_reasons)
9798-  4320	    section["conditions"] = sorted(conditions)
9799-  4321	    return section
--
9873-  6749	                )
9874-  6750	                selected_evaluations.append(
9875-  6751	                    replace(evaluation, bundle_id=physical_id)
9876-  6752	                )
9877-  6753	            evaluation_started_at = utc_timestamp()
9878-  6754	            calibration_ledger_snapshot = (
9879-  6755	                _load_calibration_snapshot_for_evaluation()
9880-  6756	            )
9881-  6757	            core = idle_admission_core_verdict(
9882-  6758	                selected_evaluations,
9883-  6759	                policy_binding,
9884-  6760	                whole_window=True,
9885:  6761	                runs_root=runs_dir,
9886-  6762	                neg8_drift_bound=neg8_drift_bound,
9887-  6763	                calibration_ledger_snapshot=calibration_ledger_snapshot,
9888-  6764	            )
9889-  6765	            extension = policy_binding.idle_admission_extension
9890-  6766	            core_reasons = _idle_admission_claim_barrier_reasons(core)
9891-  6767	            whole_status = (
9892-  6768	                "invalid"
9893-  6769	                if extension is None
9894-  6770	                else "passed"
9895-  6771	                if not core_reasons and not core.get("conditions")
9896-  6772	                else "flagged"
9897-  6773	                if policy_binding.policy.profile.value == "exploratory"
--
9904-  6780	            whole_row = {
9905-  6781	                "schema_version": IDLE_ADMISSION_WHOLE_WINDOW_SCHEMA,
9906-  6782	                "timestamp": evaluation_completed_at,
9907-  6783	                "record_type": "idle_admission_whole_window_verdict",
9908-  6784	                "status": whole_status,
9909-  6785	                "claim_licensing": bool(
9910-  6786	                    policy_binding.policy.profile.value == "production"
9911-  6787	                    and extension is not None
9912-  6788	                    and extension.claim_bearing
9913-  6789	                ),
9914-  6790	                "runs_dir": str(runs_dir),
9915-  6791	                "evaluation_scope": {
9916:  6792	                    "runs_root": str(runs_dir.resolve()),
9917-  6793	                    "started_at": evaluation_started_at,
9918-  6794	                    "completed_at": evaluation_completed_at,
9919-  6795	                },
9920-  6796	                "evaluation_basis": build_evaluation_basis(
9921-  6797	                    policy_sha256=policy_binding.sha256,
9922-  6798	                    member_occurrences=_basis_member_occurrences(
9923-  6799	                        selected_evaluations, runs_dir
9924-  6800	                    ),
9925-  6801	                    calibration_bracket=(
9926-  6802	                        core.get("instrument_calibration_bracket")
9927-  6803	                        if isinstance(
9928-  6804	                            core.get("instrument_calibration_bracket"), dict
--
11511-docs/decision_log.md:7499:**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).
11512-docs/decision_log.md:7505:**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.
11513-docs/decision_log.md:7528:   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
11514-docs/decision_log.md:7532:   — each with fresh §5A, live pre/post calibration receipts appended
11515-docs/decision_log.md:7566:   D-102 successor-artifact packet; results/methods prose placeholders.
11516-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:7:  "summary": "FAIL: named fix probes pass, but three D-102 freshness/provenance blockers remain in same-identity filtering, estimator-digest scope, and cross-root trigger observation.",
11517-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:34:        "title": "Freshness scanning confuses D-102 identity equality with full T1 selection eligibility",
11518-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:36:        "scenario": "An authenticated range-expander with the same six-field D-102 identity epoch but a different non-epoch T1 field such as mlx_version is excluded from matching, so a later normal pair passes fresh with no trigger. T1 selection must remain exact, but freshness requires a separate same-identity candidate set."
11519-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:43:        "scenario": "Mutating uncertainty_evidence.py or adapters/powermetrics.py does not stale the artifact, although those modules derive the additive trace-anchor bound and parse raw intervals consumed by the fiducial estimator. D-102 requires protocol/estimator byte changes to trigger re-derivation."
11520-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:187:      "text": "The prompt records global runs-root scanning as out of scope, but D-102 makes same-identity range expansion and corpus doubling mandatory triggers. No external authenticated candidate-registry contract was found.",
11521-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:188:      "needs": "Preserve D-102 by supplying an authenticated complete registry/set or obtain a named decision explicitly narrowing trigger observation."
11522-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:217:F1 — blocker: the fix closes the named V5 only when the unselected candidate also matches every T1 field. D-102 defines the acceptance identity using six fields; `mlx_version`, `powermetrics_sha256`, and `anchor_method_version` are not among them. Selection should continue using exact T1 matching, but trigger observation needs a distinct six-field same-identity set. A second bypass exists because corpus membership is inferred from the directory basename alone: a new authenticated candidate reusing a corpus member ID but carrying different hashes/value also passed fresh.
11523:docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:221:F3 — blocker: each production call scans only `runs_root/instrument_validation`. A trigger observed in another window root disappears from all later evaluations unless a human has already rotated the artifact. Recording `"global_runs_root_scan": false` makes the limitation visible but does not satisfy D-102’s mandatory-trigger language. A global filesystem sweep is not the only remedy; an authenticated append-only calibration registry supplied to the selector would also close it.
11524-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:227:- Production decimal flow retains the evidence lexeme through range, preflight, drift, excess, and allowance comparisons. Binary64 projections do not replace the local Decimal values. The float-only compatibility branch is not reachable from authenticated candidate loading.
11525-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/delta-1.md:228:- File and mapping pinning close F3’s self-rekey attack. A future legitimate re-fit is deliberately blocked until an atomic reviewed update changes the artifact, byte pin, estimator digests, and any D-102-derived validator constants. No runtime self-authorization path exists.
11526-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-RECOMMENDATION-FOR-ED.md:21:unobserved range-expander, and it is a faithful IMPLEMENTATION of D-102
11527-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-RECOMMENDATION-FOR-ED.md:29:- **B (narrow D-102): still needs your signed amendment** and still
11528-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-RECOMMENDATION-FOR-ED.md:35:## Two rulings you still owe under A-min (both claim-soundness; D-102 is silent)
11529-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-RECOMMENDATION-FOR-ED.md:44:   when D-102 was accepted (valid + blind holdouts + authenticated
11530-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-RECOMMENDATION-FOR-ED.md:51:   inventory of what was already known at D-102. (The investigation
11531-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-RECOMMENDATION-FOR-ED.md:62:faithful D-102 implementation (no amendment), and the one-writer choke
11532-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:51:        "collision_surface": "D-102 amendment, artifact scope declaration, verdict provenance.",
11533-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:165:      "text": "D-102 does not define the authoritative observation universe, completeness authority, or anti-rollback head.",
11534-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:166:      "needs": "Ed chooses A-min, A, C-sealed, parent-scan, or explicitly amends D-102 for B."
11535-docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:173:      "needs": "Ratify the issuance cutoff and content-identity inventory for observations already known when D-102 was accepted."
--
12407-   301	- [ ] **Require `status: passed`.** Record the evaluation-basis SHA-256, exact member-occurrence set, calibration bracket, policy hash, both family screens, both drift allowances, admitted CPU state, and stable adapter continuity.
12408-   302	
12409-   303	- [ ] **Back up both immutable roots and require exit code 0 for each.** Record separate source, destination, start/end timestamps, and exit status for the claim root and bound root. Leave both sources unchanged.
12410-   304	
12411-   305	- [ ] **Release any stopped cloud-sync process through the fail-safe cleanup and verify process identity before backup.**
12412-   306	
12413-   307	- [ ] **Restore automatic network time after the verdict and successful backups.** Record restoration time and confirm the state is on.
12414-   308	
12415-   309	- [ ] **Run exact-basis governed extraction.** Use an absolute runs root, the frozen extraction spec, the passing evaluation-basis SHA-256, and bundle hashing:
12416-   310	
12417-
12418-codex
12419:Two high-probability blockers have emerged: the canonical ledger is git-ignored and absent in a clean checkout, and even when restored, the first successful calibration advances the physical ledger without advancing the committed pin—so the same unattended chain cannot reserve its POST calibration. I’m validating the secondary failure modes now, especially whether failed/partial POST attempts can be repaired and whether bracket selection can accidentally borrow another window’s receipt.
12420-exec
12421-/bin/zsh -lc 'tmpdir=$(mktemp -d /tmp/jw-ledger-review.XXXXXX)
12422-python3 -B - "$tmpdir" <<'"'PY'
12423-import json,sys
12424-from pathlib import Path
12425-from joulewise.calibration_ledger import append_pending_receipt, finalize_attempt_receipt, head_pin_for_receipt, CalibrationLedgerError, LEDGER_SCHEMA
12426-root=Path(sys.argv[1]); ledger=root/'ledger.jsonl'; pin=root/'pin.json'
12427-pin.write_text(json.dumps({'sequence':0,'head_digest':'0'*64,'ledger_schema':LEDGER_SCHEMA})+'\\n')
12428-epoch={'os_build':'x','hardware_model':'m','power_policy':'ac','sampling_interval_ms':100,'estimator_revision':'e','pulse_protocol_id':'p'}
12429-t1={**epoch,'powermetrics_sha256':'a'*64,'anchor_method_version':'a','mlx_version':'m','protocol_sha256':'b'*64}
12430-r=append_pending_receipt(ledger,attempt_id='pre',custody_locator='/tmp/pre',identity_epoch=epoch,t1_bindings=t1,head_pin_path=pin,require_committed_pin=False)
12431-f=finalize_attempt_receipt(ledger,attempt_id='pre',disposition='abandoned',custody_locator='/tmp/pre',identity_epoch=epoch,t1_bindings=t1)
12432-print('after_pre',len(ledger.read_text().splitlines()), head_pin_for_receipt(f))
12433-try:
12434- append_pending_receipt(ledger,attempt_id='post',custody_locator='/tmp/post',identity_epoch=epoch,t1_bindings=t1,head_pin_path=pin,require_committed_pin=False)
12435-except Exception as exc:
12436- print('post_reservation',type(exc).__name__,str(exc))
12437-PY
12438-rg -n \"def .*repair|def .*resume|def .*reconcile|abandoned\" joulewise/calibration_ledger.py scripts/validate_powermetrics_fiducial.py scripts/calibration_ledger_* docs/contracts/calibration_ledger.md | sed -n '1,220p'
12439:rg -n \"relative_path|runs_root|custody_locator|causal_pre|causal_post|fresh_pre|fresh_post\" joulewise/calibration_bracketing.py | sed -n '1,220p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
12440- succeeded in 0ms:
12441-after_pre 2 {'sequence': 2, 'head_digest': '3773b528840e3d39cf569974e8756f59a4bd953ce2446e281e8cbc7f6a63bdc3', 'ledger_schema': 'joulewise.calibration_observation_ledger.v1'}
12442-post_reservation CalibrationLedgerError physical ledger head differs from the committed pin
12443-docs/contracts/calibration_ledger.md:97:hashes, and one importable disposition. `abandoned`, `unresolved`, and every
12444-scripts/validate_powermetrics_fiducial.py:372:    def finalize_abandoned() -> None:
12445-scripts/validate_powermetrics_fiducial.py:381:                disposition="abandoned",
12446-scripts/validate_powermetrics_fiducial.py:398:    atexit.register(finalize_abandoned)
12447-scripts/validate_powermetrics_fiducial.py:456:        finalize_abandoned()
12448-scripts/validate_powermetrics_fiducial.py:464:        finalize_abandoned()
12449-scripts/validate_powermetrics_fiducial.py:684:    atexit.unregister(finalize_abandoned)
12450-joulewise/calibration_ledger.py:66:    {"valid", "systematic-invalid", "ordinary-invalid", "abandoned"}
12451-joulewise/calibration_ledger.py:210:            "unresolved" if self.disposition == "abandoned" else self.disposition
12452-joulewise/calibration_ledger.py:441:    if disposition == "abandoned":
12453-joulewise/calibration_ledger.py:442:        # R1 retains the terminal writer state as ``abandoned`` while R2
12454-joulewise/calibration_ledger.py:583:                    if receipt["disposition"] == "abandoned"
12455-joulewise/calibration_ledger.py:620:            if observation.disposition == "abandoned":
12456-77:    relative_path: str
12457-94:            "relative_path": self.relative_path,
12458:537:    directory: Path, *, runs_root: Path
12459:541:    root = Path(runs_root).resolve()
12460-652:        relative_path=relative,
12461-669:    custody = Path(observation.custody_locator)
12462:672:        runs_root=custody.parent.parent,
12463-705:        relative_path=observation.custody_locator,
12464:950:            "global_runs_root_scan": False,
12465-1106:    causal_pre = [
12466-1109:    causal_post = [
12467-1112:    fresh_pre = [
12468-1114:        for candidate in causal_pre
12469-1117:    fresh_post = [
12470-1119:        for candidate in causal_post
12471-1122:    if not fresh_pre or not fresh_post:
12472-1125:            if (causal_pre and not fresh_pre) or (causal_post and not fresh_post)
12473-1129:    pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
12474-1130:    post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
12475:1257:    runs_root: Path,
12476-
12477-exec
12478-/bin/zsh -lc "nl -ba docs/decision_log.md | sed -n '6970,7105p'; rg -n \"pin.*each|after.*capture|before.*next|live.*head|reservation|pending|abandoned|commit\" docs/decision_log.md | tail -n 120" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
12479- succeeded in 0ms:
12480-  6970	   CORROBORATION ONLY and carries no formal load.
12481-  6971	3. The derived content grammar (L-A′) is demoted to non-load-bearing
12482-  6972	   hygiene. Decision-record obligation: bank the EXECUTABLE L-A′
12483-  6973	   derivation + full probe transcript (immutable input hashes for the
12484-  6974	   26 b-ii bundles, generated grammar, 26/26 admission results, every
12485-  6975	   carrier mutation INCLUDING why the seventh carrier survives, tool
12486-  6976	   identity) in `.desk/coldgate_d100_bii/` at or before row close. It
12487-  6977	   must never be described as zero-output or substitution closure.
--
13842-3. **HIGH — a dying POST process is not operationally recoverable and can poison the global ledger.**  
13843-   [validate_powermetrics_fiducial.py:372](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/validate_powermetrics_fiducial.py:372), [calibration_ledger.py:569](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_ledger.py:569), [calibration_bracketing.py:1070](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:1070)  
13844-   SIGKILL, power loss, or a fatal interpreter failure after reservation leaves `pending`, which blocks snapshots and further reservations. If `atexit` runs, the process instead records `abandoned`; that maps to `unresolved`, and every later acceptance evaluation refuses with `calibration_observation_unclassifiable`. There is no resume/reconcile CLI. Only a bespoke direct API finalization can salvage a crash that occurred after all authenticated artifacts were completed. An incomplete POST strands the window and, until a lead-controlled disposition/successor artifact, subsequent claim evaluation too.
13845-
13846-4. **HIGH — the before-science screen does not evaluate the issued acceptance rule, so healthy-looking PRE evidence can burn the whole night and fail only at verdict time.**  
13847-   [validate_powermetrics_fiducial.py:92](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/validate_powermetrics_fiducial.py:92), [window_runbook.md:574](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/phase_2/window_runbook.md:574), [run_campaign.py:4070](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/run_campaign.py:4070), [calibration_bracketing.py:1094](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:1094)  
13848-   PRE checks only a copied scalar `0.033558756679900`. It does not authenticate the issued artifact, ledger baseline/current head, identity epoch, estimator hashes, or prospective triggers. Those run only during the whole-window verdict. Concrete failures:
13849-
13850-   - macOS changes from issued `25F84` to `25F85`; PRE passes the scalar, all science runs, morning verdict rejects the stale identity epoch.
13851-   - PRE yields `0.0220 s`: below the scalar ceiling but below the issued corpus minimum `0.022741007…`; science proceeds, then the range-expansion trigger makes the issued rule stale.
13852-   - A successor artifact changes the screen, but the writer and shell retain their duplicated hardcoded literal, causing either false refusal or late rejection.
13853-
13854:5. **HIGH soundness — bracket selection can borrow another window’s receipts and does not bind the selected PRE to the artifact attached to science bundles.**  
13855-   [calibration_bracketing.py:1281](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:1281), [calibration_bracketing.py:1106](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:1106)  
13856:   Bundle inspection retains only the attached calibration’s binding vector. Candidate selection then considers every matching live receipt globally and chooses the latest temporal PRE and earliest POST; `runs_root`, custody root, attached artifact hash, validation ID, and intended pair are not checked. Concrete scenario: the current POST is absent, but a later same-T1 calibration in another root falls within 24 hours. A delayed verdict uses it as POST and can pass, despite D-117 requiring the window’s own receipts and the operator checklist requiring both endpoints under that claim root. Likewise, science attached to an off-ledger calibration can be laundered through unrelated ledger endpoints with matching bindings.
13857-
13858-The exact-byte acceptance loader itself is correct at current HEAD: it loads role `issued`, file SHA-256 `316113960c…`, and all four estimator hashes match. The Decimal drift calculation and never-zero allowance also appear correct. Workspace remained unchanged.
13859-tokens used
13860-222,305
13861-## Ranked findings
13862-
13863-1. **CRITICAL — every unattended window reaches science but cannot reserve its POST calibration.**  
13864-   [calibration_ledger.py:1676](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_ledger.py:1676), [validate_powermetrics_fiducial.py:672](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/validate_powermetrics_fiducial.py:672), [window_runbook.md:638](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/phase_2/window_runbook.md:638)  
13865-   Each reservation requires the physical ledger head to equal the committed pin exactly. PRE appends reservation and finalization, but only prints a pin candidate; it neither writes nor commits it. After science, POST therefore fails immediately with `physical ledger head differs from the committed pin`. The same defect makes the permitted clock-anchor retry impossible. A temporary two-attempt probe reproduced the error deterministically. D-109 permits one pin rotation per quiet-machine session, but the writer effectively requires rotation between every capture.
13866-
13867-2. **CRITICAL — the documented clean measurement checkout lacks the issued physical ledger, and preflight does not notice.**  
13868-   [calibration_ledger.py:51](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_ledger.py:51), [window_runbook.md:28](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/phase_2/window_runbook.md:28), [prewindow_check.sh:102](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/prewindow_check.sh:102)  
--
13871-3. **HIGH — a dying POST process is not operationally recoverable and can poison the global ledger.**  
13872-   [validate_powermetrics_fiducial.py:372](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/validate_powermetrics_fiducial.py:372), [calibration_ledger.py:569](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_ledger.py:569), [calibration_bracketing.py:1070](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:1070)  
13873-   SIGKILL, power loss, or a fatal interpreter failure after reservation leaves `pending`, which blocks snapshots and further reservations. If `atexit` runs, the process instead records `abandoned`; that maps to `unresolved`, and every later acceptance evaluation refuses with `calibration_observation_unclassifiable`. There is no resume/reconcile CLI. Only a bespoke direct API finalization can salvage a crash that occurred after all authenticated artifacts were completed. An incomplete POST strands the window and, until a lead-controlled disposition/successor artifact, subsequent claim evaluation too.
13874-
13875-4. **HIGH — the before-science screen does not evaluate the issued acceptance rule, so healthy-looking PRE evidence can burn the whole night and fail only at verdict time.**  
13876-   [validate_powermetrics_fiducial.py:92](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/validate_powermetrics_fiducial.py:92), [window_runbook.md:574](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/phase_2/window_runbook.md:574), [run_campaign.py:4070](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/run_campaign.py:4070), [calibration_bracketing.py:1094](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:1094)  
13877-   PRE checks only a copied scalar `0.033558756679900`. It does not authenticate the issued artifact, ledger baseline/current head, identity epoch, estimator hashes, or prospective triggers. Those run only during the whole-window verdict. Concrete failures:
13878-
13879-   - macOS changes from issued `25F84` to `25F85`; PRE passes the scalar, all science runs, morning verdict rejects the stale identity epoch.
13880-   - PRE yields `0.0220 s`: below the scalar ceiling but below the issued corpus minimum `0.022741007…`; science proceeds, then the range-expansion trigger makes the issued rule stale.
13881-   - A successor artifact changes the screen, but the writer and shell retain their duplicated hardcoded literal, causing either false refusal or late rejection.
13882-
13883:5. **HIGH soundness — bracket selection can borrow another window’s receipts and does not bind the selected PRE to the artifact attached to science bundles.**  
13884-   [calibration_bracketing.py:1281](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:1281), [calibration_bracketing.py:1106](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:1106)  
13885:   Bundle inspection retains only the attached calibration’s binding vector. Candidate selection then considers every matching live receipt globally and chooses the latest temporal PRE and earliest POST; `runs_root`, custody root, attached artifact hash, validation ID, and intended pair are not checked. Concrete scenario: the current POST is absent, but a later same-T1 calibration in another root falls within 24 hours. A delayed verdict uses it as POST and can pass, despite D-117 requiring the window’s own receipts and the operator checklist requiring both endpoints under that claim root. Likewise, science attached to an off-ledger calibration can be laundered through unrelated ledger endpoints with matching bindings.
13886-
13887-The exact-byte acceptance loader itself is correct at current HEAD: it loads role `issued`, file SHA-256 `316113960c…`, and all four estimator hashes match. The Decimal drift calculation and never-zero allowance also appear correct. Workspace remained unchanged.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
from unittest.mock import patch
from tests.test_calibration_bracketing import CalibrationBracketingTests, _evaluate_calibration_bracket, _unissued_acceptance_fixture

case = CalibrationBracketingTests(methodName='test_exact_session_binding_selects_reserved_pair_not_neighbors')
case.setUp()
snapshot, candidates, neighbor_binding = case._bound_session_fixture()
with patch('joulewise.calibration_bracketing.load_calibration_acceptance_bound', return_value=_unissued_acceptance_fixture()):
    result, reasons = _evaluate_calibration_bracket(
        candidates,
        window_start_s=100.0,
        window_end_s=110.0,
        bindings=case.bindings,
        policy=case.policy,
        ledger_snapshot=snapshot,
        bracket_binding=neighbor_binding,
        # Victim window identity is intentionally not supplied, matching current production callers.
        _allow_unissued_fixture=True,
    )
print({'reasons': reasons, 'status': result['status'], 'selected_session': result['bracket_binding']['session_id'] if result['bracket_binding'] else None, 'selected_window': result['bracket_binding']['window_id'] if result['bracket_binding'] else None})
PY
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import json, tempfile
from pathlib import Path
from joulewise.calibration_ledger import LEDGER_SCHEMA, GENESIS_DIGEST, append_bracket_session_receipt, finalize_bracket_session_slot, head_pin_for_receipt

with tempfile.TemporaryDirectory() as td:
    root=Path(td); ledger=root/'ledger.jsonl'; pin=root/'pin.json'
    pin.write_text(json.dumps({'sequence':0,'head_digest':GENESIS_DIGEST,'ledger_schema':LEDGER_SCHEMA})+'\\n')
    epoch={'os_build':'x','hardware_model':'m','power_policy':'ac','sampling_interval_ms':100,'estimator_revision':'e','pulse_protocol_id':'p'}
    t1={**epoch,'powermetrics_sha256':'a'*64,'anchor_method_version':'a','mlx_version':'m','protocol_sha256':'b'*64}
    slots={r:{'attempt_id':r,'custody_locator':str(root/r),'identity_epoch':epoch,'t1_bindings':t1} for r in ('pre','post')}
    append_bracket_session_receipt(ledger,session_id='s',window_id='w',plan_id='p',plan_sha256='c'*64,evidence_root_id='e',slots=slots,head_pin_path=pin,require_committed_pin=False)
    pre=finalize_bracket_session_slot(ledger,session_id='s',slot='pre',disposition='valid',custody_locator=str(root/'pre'),artifact_sha256={'manifest.json':'d'*64,'instrument_evidence.json':'e'*64},identity_epoch=epoch,t1_bindings=t1,capture_wall_time_s='1',exact_bound_lexeme_s='0.02')
    print({'mid_window_pin_candidate': head_pin_for_receipt(pre), 'pre_event': pre['event'], 'pre_slot': pre['slot']})
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 15ms:
{'mid_window_pin_candidate': {'sequence': 2, 'head_digest': '62d0c20229d14beca7dfe64ed72b947f6bd73751fc798baa5d4d74888a0dee35', 'ledger_schema': 'joulewise.calibration_observation_ledger.v1'}, 'pre_event': 'bracket-session-slot-finalization', 'pre_slot': 'pre'}

2026-08-07T17:43:39.167959Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
Governing contract and all changed production paths are mapped. Two independent adversarial probes now reproduce an L5-style intended-window bypass and a mid-window pin candidate.
  ✓ Read stop card, queue, playbook M0, orchestration, frozen memo, ratification, and named decisions
  ✓ Inspect the full uncommitted diff and map changes to contract clauses
  → Run read-only/focused regressions and construct the L5 adversarial scenario
  • Report only evidence-backed findings with severity, file:line, and failing scenario
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger tests.test_calibration_bracketing tests.test_powermetrics_fiducial -v' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
2026-08-07T17:43:55.607134Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
codex
The focused ledger, bracketing, and writer suites are running now. The independent L5 probe already false-accepted a neighbor binding when the caller omitted intended-window IDs—the exact shape current production call sites use—and a second probe showed the generic pin helper emits a candidate after only the `pre` slot.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger tests.test_calibration_bracketing tests.test_powermetrics_fiducial -q' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 42838ms:
ok
test_durability_uncertain_cli_emits_full_summary_and_distinct_exit (tests.test_calibration_ledger.CalibrationLedgerTests.test_durability_uncertain_cli_emits_full_summary_and_distinct_exit) ... ok
test_execute_invalid_artifact_source_refuses_without_ledger_write (tests.test_calibration_ledger.CalibrationLedgerTests.test_execute_invalid_artifact_source_refuses_without_ledger_write) ... ok
test_execute_reauthenticates_all_artifacts_after_lock (tests.test_calibration_ledger.CalibrationLedgerTests.test_execute_reauthenticates_all_artifacts_after_lock) ... ok
test_finalization_is_single_transition (tests.test_calibration_ledger.CalibrationLedgerTests.test_finalization_is_single_transition) ... ok
test_historical_import_cli_dry_run_is_byte_stable_and_writes_nothing (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_cli_dry_run_is_byte_stable_and_writes_nothing) ... ok
test_historical_import_fsync_failure_keeps_visible_ledger_empty (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_fsync_failure_keeps_visible_ledger_empty) ... ok
test_historical_import_io_failure_rolls_back_partial_append (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_io_failure_rolls_back_partial_append) ... ok
test_historical_import_manifest_pins_head_and_subset_roots_refuse (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_manifest_pins_head_and_subset_roots_refuse) ... ok
test_historical_import_marker_is_not_a_post_cutoff_live_observation (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_marker_is_not_a_post_cutoff_live_observation) ... ok
test_historical_import_refuses_nonempty_ledger_and_nongenesis_pin (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_refuses_nonempty_ledger_and_nongenesis_pin) ... ok
test_historical_import_refuses_nonimportable_disposition (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_refuses_nonimportable_disposition) ... ok
test_historical_import_refuses_symlinked_pinned_custody (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_refuses_symlinked_pinned_custody) ... ok
test_historical_import_refuses_tampered_evidence_bytes (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_import_refuses_tampered_evidence_bytes) ... ok
test_historical_input_digest_pair_changes_committed_chain (tests.test_calibration_ledger.CalibrationLedgerTests.test_historical_input_digest_pair_changes_committed_chain) ... ok
test_hostile_lock_identity_refuses_and_ordinary_lockfile_proceeds (tests.test_calibration_ledger.CalibrationLedgerTests.test_hostile_lock_identity_refuses_and_ordinary_lockfile_proceeds) ... ok
test_issued_artifact_mid_write_failure_preserves_destination (tests.test_calibration_ledger.CalibrationLedgerTests.test_issued_artifact_mid_write_failure_preserves_destination) ... ok
test_issued_artifact_rejects_self_consistent_unpinned_template (tests.test_calibration_ledger.CalibrationLedgerTests.test_issued_artifact_rejects_self_consistent_unpinned_template) ... ok
test_live_capture_finalization_cannot_carry_import_marker (tests.test_calibration_ledger.CalibrationLedgerTests.test_live_capture_finalization_cannot_carry_import_marker) ... ok
test_missing_or_changed_custody_bytes_refuse (tests.test_calibration_ledger.CalibrationLedgerTests.test_missing_or_changed_custody_bytes_refuse) ... ok
test_open_session_refuses_until_governed_abort_and_never_deletes_partial (tests.test_calibration_ledger.CalibrationLedgerTests.test_open_session_refuses_until_governed_abort_and_never_deletes_partial) ... ok
test_post_replace_dir_fsync_fault_is_committed_and_retry_confirms (tests.test_calibration_ledger.CalibrationLedgerTests.test_post_replace_dir_fsync_fault_is_committed_and_retry_confirms) ... ok
test_production_writer_reserves_or_validates_before_capture_state_or_sampler (tests.test_calibration_ledger.CalibrationLedgerTests.test_production_writer_reserves_or_validates_before_capture_state_or_sampler) ... ok
test_proper_prefix_of_pinned_head_refuses_as_rollback (tests.test_calibration_ledger.CalibrationLedgerTests.test_proper_prefix_of_pinned_head_refuses_as_rollback) ... ok
test_reformatted_table_cannot_confirm_or_execute_existing_chain (tests.test_calibration_ledger.CalibrationLedgerTests.test_reformatted_table_cannot_confirm_or_execute_existing_chain) ... ok
test_reservation_requires_complete_epoch_and_full_t1 (tests.test_calibration_ledger.CalibrationLedgerTests.test_reservation_requires_complete_epoch_and_full_t1) ... ok
test_sigkill_mid_import_leaves_retryable_genesis (tests.test_calibration_ledger.CalibrationLedgerTests.test_sigkill_mid_import_leaves_retryable_genesis) ... ok
test_stable_lock_serializes_replace_against_waiting_old_writer (tests.test_calibration_ledger.CalibrationLedgerTests.test_stable_lock_serializes_replace_against_waiting_old_writer) ... ok
test_tampered_nonempty_ledger_never_enters_confirm_path (tests.test_calibration_ledger.CalibrationLedgerTests.test_tampered_nonempty_ledger_never_enters_confirm_path) ... ok
test_terminal_session_head_refuses_rollback_and_nonterminal_extension (tests.test_calibration_ledger.CalibrationLedgerTests.test_terminal_session_head_refuses_rollback_and_nonterminal_extension) ... ok
test_three_member_historical_import_has_hand_computed_head (tests.test_calibration_ledger.CalibrationLedgerTests.test_three_member_historical_import_has_hand_computed_head) ... ok
test_true_sibling_fork_refuses_on_predecessor_conflict (tests.test_calibration_ledger.CalibrationLedgerTests.test_true_sibling_fork_refuses_on_predecessor_conflict) ... ok
test_unpinned_physical_extension_refuses_stale_head (tests.test_calibration_ledger.CalibrationLedgerTests.test_unpinned_physical_extension_refuses_stale_head) ... ok
test_acceptance_artifact_rederives_from_decimal_member_table (tests.test_calibration_bracketing.CalibrationBracketingTests.test_acceptance_artifact_rederives_from_decimal_member_table) ... ok
test_acceptance_prior_set_must_equal_import_marked_cutoff_prefix (tests.test_calibration_bracketing.CalibrationBracketingTests.test_acceptance_prior_set_must_equal_import_marked_cutoff_prefix) ... ok
test_bracket_drift_over_d079_budget_refuses_claim (tests.test_calibration_bracketing.CalibrationBracketingTests.test_bracket_drift_over_d079_budget_refuses_claim) ... ok
test_claim_bracket_refuses_v2_only_candidates_but_accepts_v3_pair (tests.test_calibration_bracketing.CalibrationBracketingTests.test_claim_bracket_refuses_v2_only_candidates_but_accepts_v3_pair) ... ok
test_claim_window_passes_and_embeds_never_zero_allowance_once (tests.test_calibration_bracketing.CalibrationBracketingTests.test_claim_window_passes_and_embeds_never_zero_allowance_once) ... ok
test_corpus_doubling_counts_38_total_valid_distinct_observations (tests.test_calibration_bracketing.CalibrationBracketingTests.test_corpus_doubling_counts_38_total_valid_distinct_observations) ... ok
test_d079_budgeted_drift_above_obsolete_cliff_passes_with_allowance (tests.test_calibration_bracketing.CalibrationBracketingTests.test_d079_budgeted_drift_above_obsolete_cliff_passes_with_allowance) ... ok
test_d079_drift_beyond_budget_refuses_with_recorded_basis (tests.test_calibration_bracketing.CalibrationBracketingTests.test_d079_drift_beyond_budget_refuses_with_recorded_basis) ... ok
test_d102_decimal_boundary_sweep_is_exact_and_inclusive (tests.test_calibration_bracketing.CalibrationBracketingTests.test_d102_decimal_boundary_sweep_is_exact_and_inclusive) ... ok
test_estimator_module_byte_change_stales_artifact_at_load (tests.test_calibration_bracketing.CalibrationBracketingTests.test_estimator_module_byte_change_stales_artifact_at_load) ... ok
test_exact_session_binding_selects_reserved_pair_not_neighbors (tests.test_calibration_bracketing.CalibrationBracketingTests.test_exact_session_binding_selects_reserved_pair_not_neighbors) ... ok
test_explicit_unissued_fixture_cannot_license_claim_evaluation (tests.test_calibration_bracketing.CalibrationBracketingTests.test_explicit_unissued_fixture_cannot_license_claim_evaluation) ... ok
test_f1_freshness_uses_six_field_epoch_not_full_t1 (tests.test_calibration_bracketing.CalibrationBracketingTests.test_f1_freshness_uses_six_field_epoch_not_full_t1) ... ok
test_f2_estimator_digest_closure_is_exactly_four_modules (tests.test_calibration_bracketing.CalibrationBracketingTests.test_f2_estimator_digest_closure_is_exactly_four_modules) ... ok
test_hash_rekeyed_candidate_cannot_bypass_binding_authentication (tests.test_calibration_bracketing.CalibrationBracketingTests.test_hash_rekeyed_candidate_cannot_bypass_binding_authentication) ... ok
test_identity_epoch_violation_refuses_stale_acceptance_bound (tests.test_calibration_bracketing.CalibrationBracketingTests.test_identity_epoch_violation_refuses_stale_acceptance_bound) ... ok
test_import_marker_is_excluded_by_discovery_and_trigger_paths (tests.test_calibration_bracketing.CalibrationBracketingTests.test_import_marker_is_excluded_by_discovery_and_trigger_paths) ... ok
test_issued_artifact_authenticates_and_becomes_claim_eligible (tests.test_calibration_bracketing.CalibrationBracketingTests.test_issued_artifact_authenticates_and_becomes_claim_eligible) ... ok
test_issued_artifact_committed_head_mismatch_refuses (tests.test_calibration_bracketing.CalibrationBracketingTests.test_issued_artifact_committed_head_mismatch_refuses) ... ok
test_issued_artifact_missing_ledger_refuses (tests.test_calibration_bracketing.CalibrationBracketingTests.test_issued_artifact_missing_ledger_refuses) ... ok
test_issued_artifact_prior_set_divergence_refuses (tests.test_calibration_bracketing.CalibrationBracketingTests.test_issued_artifact_prior_set_divergence_refuses) ... ok
test_issued_artifact_stale_derivation_sha256_refuses (tests.test_calibration_bracketing.CalibrationBracketingTests.test_issued_artifact_stale_derivation_sha256_refuses) ... ok
test_issued_artifact_wrong_head_digest_refuses (tests.test_calibration_bracketing.CalibrationBracketingTests.test_issued_artifact_wrong_head_digest_refuses) ... ok
test_live_issued_anchor_authenticates_and_matches_committed_head_pin (tests.test_calibration_bracketing.CalibrationBracketingTests.test_live_issued_anchor_authenticates_and_matches_committed_head_pin) ... ok
test_missing_post_bracket_refuses_claim (tests.test_calibration_bracketing.CalibrationBracketingTests.test_missing_post_bracket_refuses_claim) ... ok
test_new_abandoned_observation_refuses_with_or_without_content (tests.test_calibration_bracketing.CalibrationBracketingTests.test_new_abandoned_observation_refuses_with_or_without_content) ... ok
test_off_ledger_candidate_refuses_even_beside_registered_pair (tests.test_calibration_bracketing.CalibrationBracketingTests.test_off_ledger_candidate_refuses_even_beside_registered_pair) ... ok
test_open_and_aborted_session_observations_never_leak_as_candidates (tests.test_calibration_bracketing.CalibrationBracketingTests.test_open_and_aborted_session_observations_never_leak_as_candidates) ... ok
test_prior_set_subtraction_does_not_treat_known_holdout_as_new (tests.test_calibration_bracketing.CalibrationBracketingTests.test_prior_set_subtraction_does_not_treat_known_holdout_as_new) ... ok
test_production_path_authenticates_real_76_receipt_import_prefix (tests.test_calibration_bracketing.CalibrationBracketingTests.test_production_path_authenticates_real_76_receipt_import_prefix) ... ok
test_rekeyed_self_consistent_artifact_is_not_authenticated (tests.test_calibration_bracketing.CalibrationBracketingTests.test_rekeyed_self_consistent_artifact_is_not_authenticated) ... ok
test_session_candidates_refuse_missing_neighbor_substituted_or_cross_window_binding (tests.test_calibration_bracketing.CalibrationBracketingTests.test_session_candidates_refuse_missing_neighbor_substituted_or_cross_window_binding) ... ok
test_systematic_preflight_level_failure_is_never_budgeted (tests.test_calibration_bracketing.CalibrationBracketingTests.test_systematic_preflight_level_failure_is_never_budgeted) ... ok
test_t1_mismatched_candidate_remains_ineligible_under_d079_v2 (tests.test_calibration_bracketing.CalibrationBracketingTests.test_t1_mismatched_candidate_remains_ineligible_under_d079_v2) ... ok
test_unknown_acceptance_artifact_role_refuses (tests.test_calibration_bracketing.CalibrationBracketingTests.test_unknown_acceptance_artifact_role_refuses) ... ok
test_unselected_same_identity_range_expander_stales_artifact (tests.test_calibration_bracketing.CalibrationBracketingTests.test_unselected_same_identity_range_expander_stales_artifact) ... ok
test_window_a_t1_mismatch_shape_still_cannot_form_bracket (tests.test_calibration_bracketing.CalibrationBracketingTests.test_window_a_t1_mismatch_shape_still_cannot_form_bracket) ... ok
test_window_b_systematic_failure_precedes_rederivation_staleness (tests.test_calibration_bracketing.CalibrationBracketingTests.test_window_b_systematic_failure_precedes_rederivation_staleness) ... ok
test_bias_recovery_beats_first_threshold_crossing (tests.test_powermetrics_fiducial.DetectorTests.test_bias_recovery_beats_first_threshold_crossing) ... ok
test_cadence_jitter_still_recovers_shift (tests.test_powermetrics_fiducial.DetectorTests.test_cadence_jitter_still_recovers_shift) ... ok
test_event_stamp_uncertainty_widens_residuals (tests.test_powermetrics_fiducial.DetectorTests.test_event_stamp_uncertainty_widens_residuals) ... ok
test_false_positive_plateau_fails_closed (tests.test_powermetrics_fiducial.DetectorTests.test_false_positive_plateau_fails_closed) ... ok
test_full_region_projection_dominates_legacy_directional_scan (tests.test_powermetrics_fiducial.DetectorTests.test_full_region_projection_dominates_legacy_directional_scan) ... ok
test_half_second_delay_fails_closed_outside_validated_region (tests.test_powermetrics_fiducial.DetectorTests.test_half_second_delay_fails_closed_outside_validated_region) ... ok
test_harness_warmups_are_trimmed_but_real_spurious_plateau_remains (tests.test_powermetrics_fiducial.DetectorTests.test_harness_warmups_are_trimmed_but_real_spurious_plateau_remains) ... ok
test_live_shaped_bound_includes_capture_trace_anchor (tests.test_powermetrics_fiducial.DetectorTests.test_live_shaped_bound_includes_capture_trace_anchor) ... ok
test_low_plateau_and_low_snr_fail_closed (tests.test_powermetrics_fiducial.DetectorTests.test_low_plateau_and_low_snr_fail_closed) ... ok
test_missing_edge_fails_closed (tests.test_powermetrics_fiducial.DetectorTests.test_missing_edge_fails_closed) ... ok
test_phase_locked_grid_pulses_still_fit_via_model (tests.test_powermetrics_fiducial.DetectorTests.test_phase_locked_grid_pulses_still_fit_via_model) ... ok
test_trace_anchor_widening_is_monotone_for_clean_inputs (tests.test_powermetrics_fiducial.DetectorTests.test_trace_anchor_widening_is_monotone_for_clean_inputs) ... ok
test_validated_tenth_and_three_tenth_second_delays_are_recovered (tests.test_powermetrics_fiducial.DetectorTests.test_validated_tenth_and_three_tenth_second_delays_are_recovered) ... ok
test_any_detection_reason_forces_invalid_status (tests.test_powermetrics_fiducial.EvidenceTests.test_any_detection_reason_forces_invalid_status) ... ok
test_fitted_bound_below_protocol_pulse_count_is_invalid (tests.test_powermetrics_fiducial.EvidenceTests.test_fitted_bound_below_protocol_pulse_count_is_invalid) ... ok
test_missing_binding_field_fails_closed (tests.test_powermetrics_fiducial.EvidenceTests.test_missing_binding_field_fails_closed) ... ok
test_trace_anchor_component_flips_four_b_window_license (tests.test_powermetrics_fiducial.EvidenceTests.test_trace_anchor_component_flips_four_b_window_license) ... ok
test_trace_anchor_term_flips_four_b_window_license (tests.test_powermetrics_fiducial.EvidenceTests.test_trace_anchor_term_flips_four_b_window_license) ... ok
test_undetected_pulse_forces_invalid_even_when_bound_present (tests.test_powermetrics_fiducial.EvidenceTests.test_undetected_pulse_forces_invalid_even_when_bound_present) ... ok
test_v2_evidence_requires_and_records_capture_wall_time (tests.test_powermetrics_fiducial.EvidenceTests.test_v2_evidence_requires_and_records_capture_wall_time) ... ok
test_valid_evidence_carries_bindings_and_bound (tests.test_powermetrics_fiducial.EvidenceTests.test_valid_evidence_carries_bindings_and_bound) ... ok
test_window_license_scales_with_effective_bound (tests.test_powermetrics_fiducial.EvidenceTests.test_window_license_scales_with_effective_bound) ... ok
test_calibration_entrypoint_refuses_protocol_mismatch_before_live_import (tests.test_powermetrics_fiducial.FrozenProtocolTests.test_calibration_entrypoint_refuses_protocol_mismatch_before_live_import) ... refusing: frozen powermetrics fiducial protocol is missing, incomplete, or disagrees with executable constants
ok
test_consistent_protocol_json_matches_executable_pins (tests.test_powermetrics_fiducial.FrozenProtocolTests.test_consistent_protocol_json_matches_executable_pins) ... ok
test_incomplete_or_tampered_protocol_refuses (tests.test_powermetrics_fiducial.FrozenProtocolTests.test_incomplete_or_tampered_protocol_refuses) ... ok
test_preworkload_rollover_timeout_terminates_and_mints_no_artifact (tests.test_powermetrics_fiducial.FrozenProtocolTests.test_preworkload_rollover_timeout_terminates_and_mints_no_artifact) ... ok
test_protocol_v3_uses_d054_nonparametric_95_95_sample_count (tests.test_powermetrics_fiducial.FrozenProtocolTests.test_protocol_v3_uses_d054_nonparametric_95_95_sample_count) ... ok
test_rederive_only_emits_v2_widened_evidence_and_rejects_hash_mismatch (tests.test_powermetrics_fiducial.FrozenProtocolTests.test_rederive_only_emits_v2_widened_evidence_and_rejects_hash_mismatch) ... ok
test_shared_controller_verifier_rejects_forged_zero_residual_rows (tests.test_powermetrics_fiducial.FrozenProtocolTests.test_shared_controller_verifier_rejects_forged_zero_residual_rows) ... ok
test_v1_v2_protocol_bytes_remain_frozen_and_v3_hash_is_bound (tests.test_powermetrics_fiducial.FrozenProtocolTests.test_v1_v2_protocol_bytes_remain_frozen_and_v3_hash_is_bound) ... ok
test_gaps_avoid_ten_hertz_phase_lock (tests.test_powermetrics_fiducial.ScheduleTests.test_gaps_avoid_ten_hertz_phase_lock) ... ok
test_negative_resolution_stamp_previously_understated_bound_now_refuses (tests.test_powermetrics_fiducial.ScheduleTests.test_negative_resolution_stamp_previously_understated_bound_now_refuses) ... ok
test_phase_locked_uniform_gap_schedule_refuses_authentication (tests.test_powermetrics_fiducial.ScheduleTests.test_phase_locked_uniform_gap_schedule_refuses_authentication) ... ok
test_rederivation_authenticates_executed_schedule (tests.test_powermetrics_fiducial.ScheduleTests.test_rederivation_authenticates_executed_schedule) ... ok
test_schedule_shape (tests.test_powermetrics_fiducial.ScheduleTests.test_schedule_shape) ... ok
test_van_der_corput_prefix (tests.test_powermetrics_fiducial.ScheduleTests.test_van_der_corput_prefix) ... ok
test_vdc_schedule_passes_authentication (tests.test_powermetrics_fiducial.ScheduleTests.test_vdc_schedule_passes_authentication) ... ok
test_session_writer_authenticates_reservation_before_capture_without_ordinary_append (tests.test_powermetrics_fiducial.WriterLedgerIntegrationTests.test_session_writer_authenticates_reservation_before_capture_without_ordinary_append) ... ok
test_session_writer_crash_aborts_exact_remaining_slot (tests.test_powermetrics_fiducial.WriterLedgerIntegrationTests.test_session_writer_crash_aborts_exact_remaining_slot) ... ok

----------------------------------------------------------------------
Ran 118 tests in 42.867s

OK

exec
/bin/zsh -lc "rg -n \"discover_calibration_candidates\\(\" --glob '*.py' --glob '"'!tests/**'"'; git diff --unified=20 -- joulewise/calibration_ledger.py | rg -n -C 8 \"append_pending_receipt|finalize_attempt_receipt|load_calibration_ledger_snapshot|_valid_receipt_shape|discover\"; git diff --unified=20 -- joulewise/calibration_bracketing.py | rg -n -C 10 \"discover_calibration_candidates|ledger_snapshot.refusal|bracket_binding\"" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
joulewise/calibration_bracketing.py:907:def discover_calibration_candidates(
joulewise/calibration_bracketing.py:1572:        candidates = discover_calibration_candidates(ledger_snapshot)
451-+        and content_id_from_artifact_hashes(artifacts) == content_id
452-+        and bool(receipt.get("custody_locator"))
453-+        and all(epoch.get(field) not in (None, "") for field in IDENTITY_EPOCH_FIELDS)
454-+        and all(t1.get(field) not in (None, "") for field in T1_FIELDS)
455-+        and capture is not None
456-+    )
457- 
458- 
459: def _valid_receipt_shape(receipt: object) -> bool:
460-     if not isinstance(receipt, Mapping):
461-         return False
462-+    if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA:
463-+        return _valid_session_receipt_shape(receipt)
464-     sequence = receipt.get("sequence")
465-     event = receipt.get("event")
466-     expected_keys = (
467-         _HISTORICAL_IMPORT_RESERVATION_KEYS
--
481-         or receipt.get("ledger_schema") != LEDGER_SCHEMA
482-         or isinstance(sequence, bool)
483-         or not isinstance(sequence, int)
484-@@ -517,47 +756,209 @@ def _parse_ledger(raw: bytes) -> tuple[list[Mapping[str, Any]], set[str]]:
485-             value = json.loads(line)
486-         except json.JSONDecodeError:
487-             reasons.add("calibration_ledger_malformed")
488-             continue
489:         if not _valid_receipt_shape(value):
490-             reasons.add("calibration_ledger_malformed")
491-             continue
492-         if (
493-             value["sequence"] != expected_sequence
494-             or value["predecessor_digest"] != predecessor
495-             or value["receipt_digest"] in seen_digests
496-         ):
497-             reasons.add("calibration_ledger_chain_conflict")
--
787-             root = Path(repo_root) / root
788-         for relative, expected in observation.artifact_sha256.items():
789-             path = root / relative
790-             try:
791-                 actual = hashlib.sha256(path.read_bytes()).hexdigest()
792-             except OSError:
793-                 return {"calibration_ledger_custody_invalid"}
794-             if actual != expected:
795:@@ -704,54 +1131,67 @@ def load_calibration_ledger_snapshot(
796-         else:
797-             reasons.add("calibration_ledger_head_mismatch")
798-     if baseline_sequence is not None or baseline_digest is not None:
799-         if (
800-             isinstance(baseline_sequence, bool)
801-             or not isinstance(baseline_sequence, int)
802-             or baseline_sequence < 0
803-             or not _is_sha256(baseline_digest)
--
935-             artifacts=candidate.artifact_sha256,
936-             identity_epoch=candidate.identity_epoch,
937-             t1_bindings=candidate.t1_bindings,
938-             capture_wall_time_s=candidate.capture_wall_time_s,
939-             exact_bound_lexeme_s=candidate.exact_bound_lexeme_s,
940-             disposition=str(member["disposition"]),
941-             custody_locator=candidate.custody_locator,
942-         )
943:         if not _valid_receipt_shape(finalization):
944-             raise CalibrationLedgerError("historical finalization is malformed")
945-         receipts.append(finalization)
946-         predecessor = str(finalization["receipt_digest"])
947- 
948--    observations, reasons = _attempts_and_observations(receipts)
949-+    observations, bracket_sessions, reasons = _attempts_and_observations(receipts)
950-+    del bracket_sessions
951-     if reasons or len(observations) != len(selected):
--
968-     ledger_path: Path,
969-     head_pin_path: Path,
970-     *,
971-@@ -1621,82 +2083,372 @@ def _locked_append(
972-                 receipts, reasons = _parse_ledger(raw)
973-                 if reasons:
974-                     raise CalibrationLedgerError(", ".join(sorted(reasons)))
975-                 receipt = build(receipts)
976:                 if not _valid_receipt_shape(receipt):
977-                     raise CalibrationLedgerError(
978-                         "writer constructed a malformed receipt"
979-                     )
980-                 payload = canonical_json_bytes(receipt) + b"\n"
981-                 handle.seek(0, os.SEEK_END)
982-                 handle.write(payload)
983-                 handle.flush()
984-                 os.fsync(handle.fileno())
--
1262-+        else session.abort_receipt_digest
1263-+    )
1264-+    final = receipts[-1] if receipts else None
1265-+    if final is None or final["receipt_digest"] != terminal_digest:
1266-+        raise CalibrationLedgerError("session closure is not the terminal ledger head")
1267-+    return head_pin_for_receipt(final)
1268-+
1269-+
1270: def append_pending_receipt(
1271-     ledger_path: Path,
1272-     *,
1273-     attempt_id: str,
1274-     custody_locator: str,
1275-     identity_epoch: Mapping[str, Any] | None = None,
1276-     t1_bindings: Mapping[str, Any] | None = None,
1277-     head_pin_path: Path = DEFAULT_HEAD_PIN_PATH,
1278-     require_committed_pin: bool = True,
--
1338-             capture_wall_time_s=None,
1339-             exact_bound_lexeme_s=None,
1340-             disposition="pending",
1341-             custody_locator=custody_locator,
1342-         )
1343- 
1344-     return _locked_append(Path(ledger_path), build)
1345- 
1346:@@ -1704,49 +2456,56 @@ def append_pending_receipt(
1347: def finalize_attempt_receipt(
1348-     ledger_path: Path,
1349-     *,
1350-     attempt_id: str,
1351-     disposition: str,
1352-     custody_locator: str,
1353-     artifact_sha256: Mapping[str, str] | None = None,
1354-     identity_epoch: Mapping[str, Any] | None = None,
1355-     t1_bindings: Mapping[str, Any] | None = None,
--
1397-         ):
1398-             raise CalibrationLedgerError(
1399-                 "finalization conflicts with the reserved attempt binding"
1400-             )
1401-         predecessor = receipts[-1]["receipt_digest"] if receipts else GENESIS_DIGEST
1402-         return _new_receipt(
1403-             sequence=len(receipts) + 1,
1404-             predecessor_digest=str(predecessor),
1405:@@ -1762,52 +2521,62 @@ def finalize_attempt_receipt(
1406-             custody_locator=custody_locator,
1407-         )
1408- 
1409-     return _locked_append(Path(ledger_path), build)
1410- 
1411- 
1412- def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
1413-     """Emit the exact candidate pin that must be reviewed and committed."""
1414- 
1415:     if not _valid_receipt_shape(receipt):
1416-         raise CalibrationLedgerError("cannot pin a malformed receipt")
1417-     return {
1418-         "sequence": int(receipt["sequence"]),
1419-         "head_digest": str(receipt["receipt_digest"]),
1420-         "ledger_schema": LEDGER_SCHEMA,
1421-     }
1422- 
1423- 
--
1444-     "RECEIPT_SCHEMA",
1445-     "REFUSAL_TAXONOMY",
1446-     "CalibrationLedgerError",
1447-+    "CalibrationBracketSession",
1448-     "CalibrationLedgerSnapshot",
1449-     "HistoricalImportDurabilityUncertain",
1450-     "HistoricalImportPlan",
1451-     "LedgerObservation",
1452:     "append_pending_receipt",
1453-+    "append_bracket_session_receipt",
1454-+    "abort_bracket_session",
1455-     "artifact_hashes",
1456-     "bootstrap_historical_import",
1457-     "custody_manifest_bytes",
1458-     "canonical_sha256",
1459-     "content_id_from_artifact_hashes",
1460:     "finalize_attempt_receipt",
1461-+    "finalize_bracket_session_slot",
1462-     "generate_historical_custody_manifest",
1463-     "head_pin_for_receipt",
1464:     "load_calibration_ledger_snapshot",
1465-     "prepare_historical_import",
1466-+    "terminal_head_pin_for_session",
1467- ]
16-     RESIDUAL_REGION_METHOD,
17-     V2_BINDING_FIELDS,
18-     capture_wall_time_from_events,
19-     protocol_pulse_count,
20-     protocol_sha256,
21-     verify_stored_evidence_physics,
22- )
23- from joulewise.schemas import CalibrationBracketingPolicy
24- 
25- BRACKET_SCHEMA = "joulewise.instrument_calibration_bracket.v1"
26:+BRACKET_BINDING_SCHEMA = "joulewise.calibration_bracket_binding.v1"
27- ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
28- ACCEPTANCE_FIXTURE_SCHEMA = (
29-     "joulewise.calibration_acceptance_bound.v2.fixture.v1"
30- )
31- ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
32- DEFAULT_ACCEPTANCE_BOUND_PATH = (
33-     Path(__file__).resolve().parents[1]
34-     / "configs"
35-     / "calibration"
36-     / "calibration_acceptance_d079_v2.json"
--
151-+    "attempt_id",
152-+    "receipt_digest",
153-+    "content_digest",
154-+}
155-+
156-+
157-+def _binding_core(binding: Mapping[str, Any]) -> dict[str, Any]:
158-+    return {key: value for key, value in binding.items() if key != "binding_digest"}
159-+
160-+
161:+def build_calibration_bracket_binding(
162-+    ledger_snapshot: CalibrationLedgerSnapshot,
163-+    *,
164-+    session_id: str,
165-+    window_id: str,
166-+    plan_id: str,
167-+    plan_sha256: str,
168-+    evidence_root_id: str,
169-+) -> dict[str, Any]:
170-+    """Bind one frozen window to its exact finalized session endpoints."""
171-+
--
218-+                "receipt_digest": observation.receipt_digest,
219-+                "content_digest": observation.content_id,
220-+            }
221-+            for role, observation in (("pre", pre), ("post", post))
222-+        },
223-+    }
224-+    binding["binding_digest"] = _canonical_sha256(binding)
225-+    return binding
226-+
227-+
228:+def validate_calibration_bracket_binding(
229-+    binding: Mapping[str, Any],
230-+    ledger_snapshot: CalibrationLedgerSnapshot,
231-+    *,
232-+    window_id: str | None = None,
233-+    plan_id: str | None = None,
234-+    plan_sha256: str | None = None,
235-+    evidence_root_id: str | None = None,
236-+) -> tuple[LedgerObservation, LedgerObservation] | None:
237-+    """Return the exact authenticated pair, or ``None`` on any substitution."""
238-+
--
353-         ledger_receipt_digest=observation.receipt_digest,
354-+        bracket_session_id=observation.bracket_session_id,
355-+        bracket_slot=observation.bracket_slot,
356-+        bracket_window_id=observation.bracket_window_id,
357-+        bracket_plan_id=observation.bracket_plan_id,
358-+        bracket_plan_sha256=observation.bracket_plan_sha256,
359-+        bracket_evidence_root_id=observation.bracket_evidence_root_id,
360-     )
361- 
362- 
363: def discover_calibration_candidates(
364-     ledger_snapshot: CalibrationLedgerSnapshot,
365- ) -> tuple[CalibrationCandidate, ...]:
366-     """Enumerate valid endpoints from the sole ledger authority.
367- 
368-     The mechanism closes workflow omission, unregistered evidence, and
369-     rollback/stale-head consumption; it does not defend against a malicious
370-     trusted writer or a rewrite of both Git and full ledger history.
371-     """
372- 
373--    if not isinstance(ledger_snapshot, CalibrationLedgerSnapshot) or not ledger_snapshot.valid:
--
410- 
411- def evaluate_calibration_bracket(
412-     candidates: Sequence[CalibrationCandidate],
413-     *,
414-     window_start_s: float,
415-     window_end_s: float,
416-     bindings: Mapping[str, Any],
417-     policy: CalibrationBracketingPolicy,
418-     acceptance_bound: Mapping[str, Any] | None = None,
419-     ledger_snapshot: CalibrationLedgerSnapshot | None = None,
420:+    bracket_binding: Mapping[str, Any] | None = None,
421-+    bracket_window_id: str | None = None,
422-+    bracket_plan_id: str | None = None,
423-+    bracket_plan_sha256: str | None = None,
424-+    bracket_evidence_root_id: str | None = None,
425-     _allow_unissued_fixture: bool = False,
426- ) -> tuple[dict[str, Any], tuple[str, ...]]:
427-     """Select a causal bracket and apply the provenance-bound D-079 budget."""
428- 
429-     result: dict[str, Any] = {
430-         "schema_version": BRACKET_SCHEMA,
--
436-         },
437-         "window_start_s": window_start_s,
438-         "window_end_s": window_end_s,
439-         "pre": None,
440-         "post": None,
441-         "endpoint_max_b_fiducial_s": None,
442-         "calibration_drift_allowance_s": None,
443-         "b_fiducial_s": None,
444-         "drift_s": None,
445-         "acceptance": None,
446:+        "bracket_binding": None,
447-         "status": "not_required" if not policy.require_bracket else "failed",
448-     }
449-     if not policy.require_bracket:
450-         return result, ()
451-     if (
452-         not math.isfinite(window_start_s)
453-         or not math.isfinite(window_end_s)
454-         or window_start_s >= window_end_s
455-     ):
456-         return result, ("instrument_calibration_bracket_missing",)
--
493-+            != observation.bracket_plan_sha256
494-+            or candidate.bracket_evidence_root_id
495-+            != observation.bracket_evidence_root_id
496-         ):
497-             return result, ("calibration_ledger_off_ledger_artifact",)
498-+    has_session_candidates = any(
499-+        candidate.bracket_session_id is not None for candidate in candidates
500-+    )
501-+    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
502-+    if has_session_candidates:
503:+        if bracket_binding is None:
504:+            return result, ("calibration_bracket_binding_missing",)
505:+        bound_observations = validate_calibration_bracket_binding(
506:+            bracket_binding,
507-+            ledger_snapshot,
508-+            window_id=bracket_window_id,
509-+            plan_id=bracket_plan_id,
510-+            plan_sha256=bracket_plan_sha256,
511-+            evidence_root_id=bracket_evidence_root_id,
512-+        )
513-+        if bound_observations is None:
514:+            return result, ("calibration_bracket_binding_invalid",)
515:+        result["bracket_binding"] = {
516-+            "schema_version": BRACKET_BINDING_SCHEMA,
517:+            "binding_digest": bracket_binding["binding_digest"],
518:+            "session_id": bracket_binding["session_id"],
519:+            "window_id": bracket_binding["window_id"],
520:+            "plan_id": bracket_binding["plan_id"],
521:+            "plan_sha256": bracket_binding["plan_sha256"],
522:+            "evidence_root_id": bracket_binding["evidence_root_id"],
523-+        }
524-     # v2 remains an authenticated validation/reduction artifact, but only the
525-     # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
526-     matching = [
527-         candidate
528-         for candidate in candidates
529-         if candidate.protocol_id == PROTOCOL_ID
530-         and all(
531-             candidate.bindings.get(field) == bindings.get(field)
532-             for field in V2_BINDING_FIELDS
--
567-+    if bound_observations is None:
568-+        pre = max(fresh_pre, key=lambda candidate: candidate.capture_wall_time_s)
569-+        post = min(fresh_post, key=lambda candidate: candidate.capture_wall_time_s)
570-+    else:
571-+        candidate_by_receipt = {
572-+            candidate.ledger_receipt_digest: candidate for candidate in matching
573-+        }
574-+        pre = candidate_by_receipt.get(bound_observations[0].receipt_digest)
575-+        post = candidate_by_receipt.get(bound_observations[1].receipt_digest)
576-+        if pre not in fresh_pre or post not in fresh_post:
577:+            return result, ("calibration_bracket_binding_invalid",)
578-     pre_decimal = matching_decimals[id(pre)]
579-     post_decimal = matching_decimals[id(post)]
580-     if (
581-         not pre_decimal.is_finite()
582-         or not post_decimal.is_finite()
583-         or pre_decimal < 0
584-         or post_decimal < 0
585-     ):
586-         return result, ("instrument_calibration_invalid",)
587-     if isinstance(pre.b_fiducial_s, float) and isinstance(
--
609-     result["status"] = "passed"
610-     return result, ()
611- 
612- 
613- def calibration_bracket_for_bundles(
614-     runs_root: Path,
615-     bundle_paths: Sequence[Path],
616-     policy: CalibrationBracketingPolicy,
617-     *,
618-     ledger_snapshot: CalibrationLedgerSnapshot | None = None,
619:+    bracket_binding: Mapping[str, Any] | None = None,
620-+    bracket_window_id: str | None = None,
621-+    bracket_plan_id: str | None = None,
622-+    bracket_plan_sha256: str | None = None,
623-+    bracket_evidence_root_id: str | None = None,
624-     _allow_unissued_fixture: bool = False,
625- ) -> tuple[dict[str, Any], tuple[str, ...]]:
626-     """Use the runs root only for the evaluated window's T1/endpoints."""
627- 
628-     if not bundle_paths:
629-         empty, _ = evaluate_calibration_bracket(
--
655-                 _allow_unissued_fixture=_allow_unissued_fixture,
656-             )
657-             return empty, ("calibration_ledger_custody_invalid",)
658-     return evaluate_calibration_bracket(
659-         candidates,
660-         window_start_s=min(window.start_s for window in windows),
661-         window_end_s=max(window.end_s for window in windows),
662-         bindings=expected,
663-         policy=policy,
664-         ledger_snapshot=ledger_snapshot,
665:+        bracket_binding=bracket_binding,
666-+        bracket_window_id=bracket_window_id,
667-+        bracket_plan_id=bracket_plan_id,
668-+        bracket_plan_sha256=bracket_plan_sha256,
669-+        bracket_evidence_root_id=bracket_evidence_root_id,
670-         _allow_unissued_fixture=_allow_unissued_fixture,
671-     )
672- 
673- 
674- __all__ = [
675-     "ACCEPTANCE_BOUND_SCHEMA",
676-     "ACCEPTANCE_EVALUATION_SCHEMA",
677-+    "BRACKET_BINDING_SCHEMA",
678-     "BRACKET_SCHEMA",
679-     "CalibrationCandidate",
680:+    "build_calibration_bracket_binding",
681-     "calibration_bracket_for_bundles",
682:     "discover_calibration_candidates",
683-     "evaluate_calibration_bracket",
684-     "load_calibration_acceptance_bound",
685-     "load_calibration_candidate",
686:+    "validate_calibration_bracket_binding",
687- ]

 succeeded in 42411ms:
refusing: frozen powermetrics fiducial protocol is missing, incomplete, or disagrees with executable constants
----------------------------------------------------------------------
Ran 118 tests in 42.440s

OK

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import json, tempfile
from pathlib import Path
from joulewise.calibration_ledger import *

with tempfile.TemporaryDirectory() as td:
    root=Path(td); ledger=root/'ledger.jsonl'; pin=root/'pin.json'
    pin.write_text(json.dumps({'sequence':0,'head_digest':GENESIS_DIGEST,'ledger_schema':LEDGER_SCHEMA})+'\\n')
    epoch={'os_build':'x','hardware_model':'m','power_policy':'ac','sampling_interval_ms':100,'estimator_revision':'e','pulse_protocol_id':'p'}
    t1={**epoch,'powermetrics_sha256':'a'*64,'anchor_method_version':'a','mlx_version':'m','protocol_sha256':'b'*64}
    slots={r:{'attempt_id':r,'custody_locator':str(root/r),'identity_epoch':epoch,'t1_bindings':t1} for r in ('pre','post')}
    append_bracket_session_receipt(ledger,session_id='s',window_id='w',plan_id='p',plan_sha256='c'*64,evidence_root_id='e',slots=slots,head_pin_path=pin,require_committed_pin=False)
    pre=finalize_bracket_session_slot(ledger,session_id='s',slot='pre',disposition='systematic-invalid',custody_locator=str(root/'pre'),artifact_sha256={'manifest.json':'d'*64,'instrument_evidence.json':'e'*64},identity_epoch=epoch,t1_bindings=t1,capture_wall_time_s='1',exact_bound_lexeme_s='0.04')
    abort_bracket_session(ledger,session_id='s',reason='pre_capture_systematic-invalid')
    pin.write_text(json.dumps(terminal_head_pin_for_session(ledger,session_id='s'))+'\\n')
    snap=load_calibration_ledger_snapshot(ledger,pin,baseline_sequence=0,baseline_digest=GENESIS_DIGEST,require_committed_pin=False,verify_custody=False)
    print({'valid':snap.valid,'snapshot_observations':[(o.attempt_id,o.disposition) for o in snap.observations], 'post_cutoff_live':[(o.attempt_id,o.disposition) for o in snap.post_cutoff_live_observations(0)], 'recoverable_session_slots':[(k,v.disposition) for k,v in snap.bracket_sessions[0].finalized_slots.items()], 'pre_receipt':pre['receipt_digest']})
PY" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
{'valid': True, 'snapshot_observations': [], 'post_cutoff_live': [], 'recoverable_session_slots': [('pre', 'systematic-invalid')], 'pre_receipt': 'd7c1539f77818dd8d677f3e62dd03967d7cb16513e7d8698b80a7386677a0dc6'}

exec
/bin/zsh -lc "nl -ba docs/decision_log.md | sed -n '7053,7092p'; nl -ba docs/contracts/calibration_ledger.md | sed -n '1,235p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
  7053	**R2 — prior-observation set and prospective triggers (8 clauses):**
  7054	1. The issuance cutoff is an exact ledger sequence + head digest.
  7055	2. `derivation_corpus` remains exactly the n=19 threshold-producing
  7056	   observations.
  7057	3. `prior_observation_set` = every content-distinct governed
  7058	   observation known at the cutoff — valid, systematic-invalid,
  7059	   ordinary-invalid, blind holdout, and unresolved — with epoch and
  7060	   disposition recorded separately. (The current artifact's two
  7061	   ID-only `blind_exclusions` are insufficient and are superseded.)
  7062	4. Content identity is path-independent, derived from canonical
  7063	   primary-byte hashes; attempt identity is separate; copies do not
  7064	   create new observations.
  7065	5. "New" (trigger population) = current authentic content IDs −
  7066	   `prior_observation_set`, regardless of capture timestamp or source
  7067	   root; a previously unknown historical artifact IS new when
  7068	   discovered. Every new observation is judged under the PRIOR
  7069	   artifact (D-102's prospective rule).
  7070	6. New unresolved or unclassifiable attempts cause refusal; only after
  7071	   trigger disposition may a successor artifact absorb them.
  7072	7. The 32-valid/6-invalid same-epoch inventory is a backfill
  7073	   CANDIDATE, not a ratified classification: identities may seed the
  7074	   backfill, but dispositions require raw-physics + hash verification
  7075	   before issuance, and any unresolved member blocks issuance.
  7076	8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38
  7077	   TOTAL authenticated, content-distinct, VALID same-epoch
  7078	   observations — including previously blind observations once
  7079	   unblinded — not 38 post-cutoff observations. Under the candidate
  7080	   inventory, six further valid observations trigger re-derivation.
  7081	
  7082	## D-110: Mint 1 retroactively NON-CLAIM-BEARING (taint-and-remint); RT-2 dependency edge minted; the night consult's 7B-mint license SUSPENDED
  7083	
  7084	> **2026-08-07 supersession (D-117):** clause 3's historical re-mint
  7085	> order is SUPERSEDED — structurally unsatisfiable at main (see
  7086	> `docs/process_traces/2026-08-06-d110-remint-fork/`); replaced by
  7087	> three prospective windows. The taint holding and the never-zero
  7088	> allowance correction STAND and bind the D-117 mints.
  7089	
  7090	- Date: 2026-08-03 (Ed ruling, present, option "taint-and-remint" selected
  7091	  from the magistrate's three-option packet during the 16h runway)
  7092	- Status: accepted (trigger: the Ed-ordered two-week read-only soundness
     1	# Calibration observation ledger
     2	
     3	The canonical calibration ledger is an immutable SHA-256 receipt chain under
     4	`joulewise.calibration_observation_ledger.v1`. D-109 R1 and R2 are controlling.
     5	The ledger closes workflow omission, unregistered evidence, and rollback or
     6	stale-head consumption; it does not defend against a malicious trusted writer
     7	or an authority that rewrites both Git and the complete ledger history.
     8	
     9	Live capture remains reservation-first: a `reservation` receipt with
    10	`disposition=pending` precedes hardware state, and exactly one `finalization`
    11	receipt closes that attempt. The repository-committed head pin is independent
    12	authority over the physical ledger head. Claim evaluation requires their exact
    13	agreement and one immutable snapshot threaded through every consumer.
    14	
    15	## Historical import
    16	
    17	Historical import is the one genesis-only exception that registers already
    18	captured, hash-authenticated observations. It is not a second writer or an
    19	ordinary capture route. Version 1 has the following fixed decisions.
    20	
    21	1. **Ordering:** members are ordered by ascending `attempt_id`, then ascending
    22	   `content_id`. Attempt IDs are required to be unique; the content-ID
    23	   secondary key only makes collision diagnosis deterministic, after which a
    24	   collision refuses rather than inventing a new attempt identity.
    25	2. **Custody selection:** import authority is a reviewed, raw-byte-SHA-256-
    26	   pinned custody manifest mapping every table content ID to one exact absolute
    27	   locator. The importer uses exactly that locator; invocation roots have no
    28	   selection authority. A missing or hash-incomplete pinned copy, a locator or
    29	   governed artifact reached through a symlink, or a manifest/table content-set
    30	   mismatch refuses. Optional roots are a strict cross-check: every pinned
    31	   locator must be discovered, and the discovered hash-complete content set
    32	   must equal the manifest set. `--emit-custody-manifest` is the only place the
    33	   lexicographically smallest POSIX checkout-relative rule selects locators;
    34	   it prints review bytes and writes nothing.
    35	3. **Transaction representation:** every member has exactly two receipts,
    36	   `historical-import-v1-reservation` immediately followed by
    37	   `historical-import-v1-finalization`. There is no summary receipt. The
    38	   versioned event marker distinguishes these rows from live capture and binds
    39	   this ordering/custody contract into every receipt digest. Every reservation
    40	   also carries `historical_import_input_sha256`, whose exact
    41	   `disposition_table` and `custody_manifest` digests bind the authenticated
    42	   raw input bytes into the chain. The terminal digest therefore transitively
    43	   binds the complete ordered member set and the exact input-digest pair;
    44	   semantically identical reserialization produces a different chain.
    45	   Omitting a summary keeps the existing two-transition attempt model and
    46	   yields sequence `2 * member_count`.
    47	
    48	Consumers must not treat an import-marked finalization as a fresh post-cutoff
    49	observation or bracket endpoint. Production candidate discovery checks the
    50	marker directly, and prospective trigger subtraction uses
    51	`CalibrationLedgerSnapshot.post_cutoff_live_observations()`. At consumption,
    52	the acceptance artifact's `prior_observation_set` must exactly equal the
    53	import-marked ledger prefix at its cutoff (attempt ID, content ID,
    54	classification disposition, and epoch); any omission, addition, or live row in
    55	that prefix refuses.
    56	
    57	### Ruled disposition table
    58	
    59	The bootstrap takes dispositions only from an explicit JSON table; stored
    60	evidence `status` fields have no authority and are not consulted. The table
    61	shape is:
    62	
    63	```json
    64	{
    65	  "schema_version": "joulewise.calibration_historical_import_table.v1",
    66	  "ledger_schema": "joulewise.calibration_observation_ledger.v1",
    67	  "identity_epoch": {
    68	    "os_build": "...",
    69	    "hardware_model": "...",
    70	    "power_policy": "...",
    71	    "sampling_interval_ms": 100,
    72	    "estimator_revision": "...",
    73	    "pulse_protocol_id": "..."
    74	  },
    75	  "members": [
    76	    {
    77	      "attempt_id": "...",
    78	      "content_id": "64 lowercase hex characters",
    79	      "artifact_sha256": {
    80	        "raw/powermetrics.plist": "...",
    81	        "events.jsonl": "...",
    82	        "power_trace.csv": "...",
    83	        "instrument_evidence.json": "...",
    84	        "manifest.json": "..."
    85	      },
    86	      "disposition": "valid | systematic-invalid | ordinary-invalid"
    87	    }
    88	  ]
    89	}
    90	```
    91	
    92	The table's exact raw bytes are authenticated by required
    93	`--expected-table-sha256`, and that digest is recorded in the prepared plan and
    94	bootstrap summary. The table member order is non-authoritative. The importer
    95	requires unique attempt and content IDs, a complete five-artifact hash map, a
    96	content ID that is exactly the canonical hash of the manifest/evidence byte
    97	hashes, and one importable disposition. `abandoned`, `unresolved`, and every
    98	other disposition outside the three values above refuse.
    99	
   100	The reviewed custody manifest shape is:
   101	
   102	```json
   103	{
   104	  "schema_version": "joulewise.calibration_historical_import_custody_manifest.v1",
   105	  "ledger_schema": "joulewise.calibration_observation_ledger.v1",
   106	  "members": {
   107	    "content-id-64-lowercase-hex": "/exact/absolute/custody/locator"
   108	  }
   109	}
   110	```
   111	
   112	Its exact raw-byte digest is authenticated by required
   113	`--expected-custody-manifest-sha256` and reported in the bootstrap summary.
   114	
   115	For every manifest-pinned custody directory the importer opens contained
   116	no-follow descriptors, reads the actual bytes, recomputes all five hashes and
   117	the content ID, verifies the manifest's complete artifact table, verifies the
   118	evidence document's raw/events/trace hashes, extracts the six-field epoch and
   119	full T1 binding from the authenticated evidence, and preserves the source
   120	numeric lexemes for capture time and bound.
   121	The authenticated manifest content set must equal the table exactly. Every
   122	selected attempt ID and artifact hash must equal its table row. Any mismatch,
   123	missing member, extra member, malformed primary document, or absent
   124	hash-complete custody copy refuses.
   125	
   126	### Genesis and atomicity gates
   127	
   128	Dry-run requires:
   129	
   130	- an empty physical ledger (an absent or zero-byte file), and
   131	- a well-formed repository-committed head pin at sequence `0` with the
   132	  all-zero genesis digest.
   133	
   134	Execution requires the same genesis pin. It normally also requires an absent
   135	or empty physical ledger. Its sole nonempty exception is the idempotent
   136	durability-confirm path described below.
   137	
   138	Every ledger writer locks the dedicated adjacent
   139	`<ledger-filename>.lock` file. That lock file is created if absent and is never
   140	replaced. A writer acquires it before opening or re-opening the ledger path,
   141	and holds it through every append or replacement. The replaceable ledger inode
   142	is never the lock object, so a writer that waited during replacement cannot
   143	resume against an old, unlinked ledger inode. Both append and bootstrap open
   144	the lock through the same audited helper with `O_NOFOLLOW|O_CREAT|O_RDWR`, then
   145	`fstat` the descriptor and refuse unless it is a regular file with link count
   146	one. If the ledger exists, the lock's `(st_dev, st_ino)` must also differ from
   147	the ledger's. Symlinked locks and hardlink aliases therefore fail closed.
   148	
   149	Execution prepares and canonicalizes the entire chain in memory, obtains the
   150	stable lock, rechecks the genesis pin and physical ledger by path, and
   151	immediately re-opens all five artifacts for every member through contained
   152	no-follow descriptors. Every hash must still equal the prepared plan. It then
   153	writes and fsyncs the complete payload to a sibling staging file and atomically
   154	replaces the empty ledger. Until replacement, readers see only genesis; after
   155	replacement, readers see only the complete chain. A write, staging-file fsync,
   156	reauthentication, or replacement failure leaves zero reader-visible receipts.
   157	Process death mid-stage likewise leaves a retryable genesis ledger.
   158	
   159	`os.replace` is the transaction commit point. After replacement, the importer
   160	fsyncs the parent directory and retries that directory fsync once if it fails.
   161	If both attempts fail, the chain is **committed with durability uncertain**;
   162	it is never reported as an atomic-append failure. The CLI still emits every
   163	canonical receipt and the full summary, whose machine-readable `outcome` is
   164	`committed_durability_uncertain`, then exits `3`. The operator must rerun the
   165	identical `--execute` invocation before updating the head pin.
   166	
   167	While the committed pin remains genesis, such a rerun recomputes the complete
   168	plan from the authenticated table, manifest, and custody bytes under the same
   169	rules. Under the stable lock, it compares the physical ledger byte-for-byte
   170	with `plan.ledger_bytes`; matching bytes enter the idempotent confirm path,
   171	which re-fsyncs the parent directory without replacing or appending and emits
   172	the same receipt chain and head/input-digest summary with `outcome=committed`.
   173	Because the input-digest pair is inside the reservation bytes, reserializing
   174	either authenticated input makes this byte comparison fail. Any other nonempty
   175	ledger refuses with the ordinary empty-ledger error. Once the reviewed head
   176	pin is updated away from genesis, a further invocation refuses at the normal
   177	genesis-pin gate.
   178	
   179	The importer never writes the head pin. After execution, claim evaluation is
   180	expected to refuse until the lead has reviewed and committed the exact printed
   181	pin, preserving D-109 R1.4's anti-rollback boundary.
   182	
   183	## Issued D-079 acceptance artifact
   184	
   185	The acceptance consumer recognizes two exact-byte roles. The retained genesis
   186	test fixture uses schema
   187	`joulewise.calibration_acceptance_bound.v2.fixture.v1`, role
   188	`schema_fixture_unissued`, and file SHA-256
   189	`9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb`.
   190	It remains useful only to pre-issuance tests and production evaluation always
   191	refuses it. The deterministic issued document uses schema
   192	`joulewise.calibration_acceptance_bound.v2`, role `issued`, and exact emitted
   193	file SHA-256
   194	`316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`.
   195	No other role, schema, or file bytes are accepted, even when its internal
   196	whole-core digest is self-consistent.
   197	
   198	Issued-artifact authentication is conjunctive and fail-closed:
   199	
   200	1. The file must match the issued byte pin and its `derivation_sha256` must be
   201	   the canonical SHA-256 of every top-level key except `derivation_sha256`.
   202	2. The one threaded `CalibrationLedgerSnapshot` must have authenticated the
   203	   physical ledger against the repository-committed current head pin. Missing
   204	   ledger bytes, an uncommitted pin, rollback, a fork, or any physical/pinned
   205	   head mismatch refuses before the artifact can become claim-eligible.
   206	3. The artifact cutoff is passed to the snapshot loader as its baseline. The
   207	   exact digest must occur at the exact sequence in that authenticated chain,
   208	   and the evaluator rechecks the snapshot's baseline fields against the
   209	   artifact. A later committed live extension is permitted by D-109 R1.4; it
   210	   does not change the historical issuance cutoff.
   211	4. `prior_observation_set` must equal the complete import-marked observation
   212	   prefix through the cutoff, member for member by attempt ID, path-independent
   213	   content ID, classification disposition, and identity epoch. Any omission,
   214	   addition, duplicate, non-import row, or epoch divergence refuses.
   215	
   216	The artifact's stored `issuance.claim_eligible=true` is necessary but not
   217	sufficient. The evaluation result reports effective `claim_eligible=true`
   218	only after all four checks pass and a non-genesis ledger head is present.
   219	Before that point it reports false. The issued D-079 state is sequence 76 at
   220	head
   221	`08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`,
   222	with 38 import-marked, content-distinct observations: 30 valid, 2
   223	systematic-invalid, and 6 ordinary-invalid. The threshold-producing
   224	`derivation_corpus` remains n=19. The issued whole-core
   225	`derivation_sha256` is
   226	`4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`.
   227	
   228	### Bootstrap CLI
   229	
   230	`scripts/calibration_ledger_bootstrap.py` is dry-run unless `--execute` is
   231	present. Both dry-run and execution require `--disposition-table`,
   232	`--expected-table-sha256`, `--custody-manifest`, and
   233	`--expected-custody-manifest-sha256`. Zero or more run,
   234	`instrument_validation`, or custody roots may be supplied only as the strict
   235	cross-check described above. `--checkout-root` supplies the relative ordering

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -q' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
2026-08-07T17:46:28.036212Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
2026-08-07T17:46:47.197120Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
codex
Focused and canonical suites completed without test failures, but the green tests encode the two defects: the L5 regression never supplies a different intended victim identity, and the abort test explicitly expects a finalized systematic/valid pre observation to vanish from the snapshot’s observation universe. I’m doing the final fail-closed diff sweep and line-pin pass now.
exec
/bin/zsh -lc "git status --short --branch; git diff --check; nl -ba joulewise/calibration_bracketing.py | sed -n '590,685p'; nl -ba joulewise/calibration_bracketing.py | sed -n '1218,1255p'; nl -ba joulewise/calibration_bracketing.py | sed -n '1498,1605p'; nl -ba joulewise/calibration_ledger.py | sed -n '877,935p'; nl -ba joulewise/calibration_ledger.py | sed -n '1003,1040p'; nl -ba joulewise/calibration_ledger.py | sed -n '2348,2382p'; nl -ba joulewise/calibration_ledger.py | sed -n '2521,2539p'; nl -ba tests/test_calibration_bracketing.py | sed -n '1028,1078p'; nl -ba tests/test_calibration_ledger.py | sed -n '569,605p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
 succeeded in 0ms:
## impl/d117-u1-ledger-session...origin/main [behind 14]
 M joulewise/calibration_bracketing.py
 M joulewise/calibration_ledger.py
 M scripts/validate_powermetrics_fiducial.py
 M tests/test_calibration_bracketing.py
 M tests/test_calibration_ledger.py
 M tests/test_powermetrics_fiducial.py
?? scripts/reserve_calibration_window_bracket.py
   590	                "receipt_digest": observation.receipt_digest,
   591	                "content_digest": observation.content_id,
   592	            }
   593	            for role, observation in (("pre", pre), ("post", post))
   594	        },
   595	    }
   596	    binding["binding_digest"] = _canonical_sha256(binding)
   597	    return binding
   598	
   599	
   600	def validate_calibration_bracket_binding(
   601	    binding: Mapping[str, Any],
   602	    ledger_snapshot: CalibrationLedgerSnapshot,
   603	    *,
   604	    window_id: str | None = None,
   605	    plan_id: str | None = None,
   606	    plan_sha256: str | None = None,
   607	    evidence_root_id: str | None = None,
   608	) -> tuple[LedgerObservation, LedgerObservation] | None:
   609	    """Return the exact authenticated pair, or ``None`` on any substitution."""
   610	
   611	    if (
   612	        not isinstance(binding, Mapping)
   613	        or set(binding) != _BRACKET_BINDING_KEYS
   614	        or binding.get("schema_version") != BRACKET_BINDING_SCHEMA
   615	        or binding.get("ledger_schema") != LEDGER_SCHEMA
   616	        or not _valid_sha256(binding.get("plan_sha256"))
   617	        or not _valid_sha256(binding.get("capability_receipt_digest"))
   618	        or not _valid_sha256(binding.get("binding_digest"))
   619	        or binding.get("binding_digest") != _canonical_sha256(_binding_core(binding))
   620	        or not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
   621	        or not ledger_snapshot.valid
   622	    ):
   623	        return None
   624	    for field, expected in (
   625	        ("window_id", window_id),
   626	        ("plan_id", plan_id),
   627	        ("plan_sha256", plan_sha256),
   628	        ("evidence_root_id", evidence_root_id),
   629	    ):
   630	        if expected is not None and binding.get(field) != expected:
   631	            return None
   632	    session = ledger_snapshot.bracket_session_by_id.get(str(binding.get("session_id")))
   633	    if (
   634	        session is None
   635	        or session.state != "finalized"
   636	        or binding.get("window_id") != session.window_id
   637	        or binding.get("plan_id") != session.plan_id
   638	        or binding.get("plan_sha256") != session.plan_sha256
   639	        or binding.get("evidence_root_id") != session.evidence_root_id
   640	        or binding.get("capability_receipt_digest")
   641	        != session.capability_receipt_digest
   642	    ):
   643	        return None
   644	    terminal = binding.get("terminal_head")
   645	    endpoints = binding.get("endpoints")
   646	    if (
   647	        not isinstance(terminal, Mapping)
   648	        or set(terminal) != {"sequence", "head_digest", "ledger_schema"}
   649	        or terminal.get("ledger_schema") != LEDGER_SCHEMA
   650	        or isinstance(terminal.get("sequence"), bool)
   651	        or not isinstance(terminal.get("sequence"), int)
   652	        or not _valid_sha256(terminal.get("head_digest"))
   653	        or not isinstance(endpoints, Mapping)
   654	        or set(endpoints) != {"pre", "post"}
   655	    ):
   656	        return None
   657	    resolved: list[LedgerObservation] = []
   658	    for role in ("pre", "post"):
   659	        endpoint = endpoints.get(role)
   660	        observation = session.finalized_slots.get(role)
   661	        if (
   662	            not isinstance(endpoint, Mapping)
   663	            or set(endpoint) != _BRACKET_ENDPOINT_KEYS
   664	            or observation is None
   665	            or observation.disposition != "valid"
   666	            or observation.content_id is None
   667	            or endpoint.get("attempt_id") != observation.attempt_id
   668	            or endpoint.get("receipt_digest") != observation.receipt_digest
   669	            or endpoint.get("content_digest") != observation.content_id
   670	        ):
   671	            return None
   672	        resolved.append(observation)
   673	    post = resolved[1]
   674	    if (
   675	        terminal.get("sequence") != post.sequence
   676	        or terminal.get("head_digest") != post.receipt_digest
   677	        or post.sequence > len(ledger_snapshot.receipts)
   678	        or ledger_snapshot.receipts[post.sequence - 1].get("receipt_digest")
   679	        != post.receipt_digest
   680	    ):
   681	        return None
   682	    return resolved[0], resolved[1]
   683	
   684	
   685	def _binding_evidence_authentic(
  1218	            or candidate.bracket_plan_id != observation.bracket_plan_id
  1219	            or candidate.bracket_plan_sha256
  1220	            != observation.bracket_plan_sha256
  1221	            or candidate.bracket_evidence_root_id
  1222	            != observation.bracket_evidence_root_id
  1223	        ):
  1224	            return result, ("calibration_ledger_off_ledger_artifact",)
  1225	    has_session_candidates = any(
  1226	        candidate.bracket_session_id is not None for candidate in candidates
  1227	    )
  1228	    bound_observations: tuple[LedgerObservation, LedgerObservation] | None = None
  1229	    if has_session_candidates:
  1230	        if bracket_binding is None:
  1231	            return result, ("calibration_bracket_binding_missing",)
  1232	        bound_observations = validate_calibration_bracket_binding(
  1233	            bracket_binding,
  1234	            ledger_snapshot,
  1235	            window_id=bracket_window_id,
  1236	            plan_id=bracket_plan_id,
  1237	            plan_sha256=bracket_plan_sha256,
  1238	            evidence_root_id=bracket_evidence_root_id,
  1239	        )
  1240	        if bound_observations is None:
  1241	            return result, ("calibration_bracket_binding_invalid",)
  1242	        result["bracket_binding"] = {
  1243	            "schema_version": BRACKET_BINDING_SCHEMA,
  1244	            "binding_digest": bracket_binding["binding_digest"],
  1245	            "session_id": bracket_binding["session_id"],
  1246	            "window_id": bracket_binding["window_id"],
  1247	            "plan_id": bracket_binding["plan_id"],
  1248	            "plan_sha256": bracket_binding["plan_sha256"],
  1249	            "evidence_root_id": bracket_binding["evidence_root_id"],
  1250	        }
  1251	    # v2 remains an authenticated validation/reduction artifact, but only the
  1252	    # 59-pulse v3 protocol carries the governed 95/95 claim calibration.
  1253	    matching = [
  1254	        candidate
  1255	        for candidate in candidates
  1498	        "operative_b_fiducial_binary64_s": float(operative_bound),
  1499	    }
  1500	    result["status"] = "passed"
  1501	    return result, ()
  1502	
  1503	
  1504	def calibration_bracket_for_bundles(
  1505	    runs_root: Path,
  1506	    bundle_paths: Sequence[Path],
  1507	    policy: CalibrationBracketingPolicy,
  1508	    *,
  1509	    ledger_snapshot: CalibrationLedgerSnapshot | None = None,
  1510	    bracket_binding: Mapping[str, Any] | None = None,
  1511	    bracket_window_id: str | None = None,
  1512	    bracket_plan_id: str | None = None,
  1513	    bracket_plan_sha256: str | None = None,
  1514	    bracket_evidence_root_id: str | None = None,
  1515	    _allow_unissued_fixture: bool = False,
  1516	) -> tuple[dict[str, Any], tuple[str, ...]]:
  1517	    """Use the runs root only for the evaluated window's T1/endpoints."""
  1518	
  1519	    if not bundle_paths:
  1520	        empty, _ = evaluate_calibration_bracket(
  1521	            (),
  1522	            window_start_s=0.0,
  1523	            window_end_s=0.0,
  1524	            bindings={},
  1525	            policy=policy,
  1526	            ledger_snapshot=ledger_snapshot,
  1527	            _allow_unissued_fixture=_allow_unissued_fixture,
  1528	        )
  1529	        return empty, ("instrument_calibration_bracket_missing",)
  1530	    windows = []
  1531	    bindings: list[Mapping[str, Any]] = []
  1532	    try:
  1533	        for path in bundle_paths:
  1534	            reader = BundleReader(path)
  1535	            window = reader.measured_window()
  1536	            metadata = reader.metadata()
  1537	            calibration = metadata.get("instrument_calibration")
  1538	            binding = calibration.get("bindings") if isinstance(calibration, Mapping) else None
  1539	            if window is None or not isinstance(binding, Mapping):
  1540	                raise ValueError("member omits calibration binding evidence")
  1541	            windows.append(window)
  1542	            bindings.append(binding)
  1543	    except (BundleReadError, OSError, TypeError, ValueError):
  1544	        empty, _ = evaluate_calibration_bracket(
  1545	            (),
  1546	            window_start_s=0.0,
  1547	            window_end_s=0.0,
  1548	            bindings={},
  1549	            policy=policy,
  1550	            ledger_snapshot=ledger_snapshot,
  1551	            _allow_unissued_fixture=_allow_unissued_fixture,
  1552	        )
  1553	        return empty, ("instrument_calibration_bracket_missing",)
  1554	    expected = bindings[0]
  1555	    if any(
  1556	        any(binding.get(field) != expected.get(field) for field in V2_BINDING_FIELDS)
  1557	        for binding in bindings[1:]
  1558	    ):
  1559	        empty, _ = evaluate_calibration_bracket(
  1560	            (),
  1561	            window_start_s=min(window.start_s for window in windows),
  1562	            window_end_s=max(window.end_s for window in windows),
  1563	            bindings=expected,
  1564	            policy=policy,
  1565	            ledger_snapshot=ledger_snapshot,
  1566	            _allow_unissued_fixture=_allow_unissued_fixture,
  1567	        )
  1568	        return empty, ("instrument_calibration_mismatch",)
  1569	    if ledger_snapshot is None:
  1570	        candidates: tuple[CalibrationCandidate, ...] = ()
  1571	    else:
  1572	        candidates = discover_calibration_candidates(ledger_snapshot)
  1573	        registered_valid = sum(
  1574	            observation.disposition == "valid"
  1575	            and not observation.is_historical_import
  1576	            for observation in ledger_snapshot.observations
  1577	        )
  1578	        if ledger_snapshot.valid and len(candidates) != registered_valid:
  1579	            empty, _ = evaluate_calibration_bracket(
  1580	                (),
  1581	                window_start_s=min(window.start_s for window in windows),
  1582	                window_end_s=max(window.end_s for window in windows),
  1583	                bindings=expected,
  1584	                policy=policy,
  1585	                ledger_snapshot=ledger_snapshot,
  1586	                _allow_unissued_fixture=_allow_unissued_fixture,
  1587	            )
  1588	            return empty, ("calibration_ledger_custody_invalid",)
  1589	    return evaluate_calibration_bracket(
  1590	        candidates,
  1591	        window_start_s=min(window.start_s for window in windows),
  1592	        window_end_s=max(window.end_s for window in windows),
  1593	        bindings=expected,
  1594	        policy=policy,
  1595	        ledger_snapshot=ledger_snapshot,
  1596	        bracket_binding=bracket_binding,
  1597	        bracket_window_id=bracket_window_id,
  1598	        bracket_plan_id=bracket_plan_id,
  1599	        bracket_plan_sha256=bracket_plan_sha256,
  1600	        bracket_evidence_root_id=bracket_evidence_root_id,
  1601	        _allow_unissued_fixture=_allow_unissued_fixture,
  1602	    )
  1603	
  1604	
  1605	__all__ = [
   877	    sessions: list[CalibrationBracketSession] = []
   878	    completed_observations: list[LedgerObservation] = []
   879	    for session_id, state in sorted(
   880	        states.items(), key=lambda item: int(item[1]["open"]["sequence"])
   881	    ):
   882	        open_receipt = state["open"]
   883	        finals = state["finals"]
   884	        abort = state["abort"]
   885	        if abort is not None:
   886	            session_state = "aborted"
   887	        elif len(finals) == 2:
   888	            session_state = "finalized"
   889	        else:
   890	            session_state = "open"
   891	            reasons.add("calibration_ledger_bracket_session_open")
   892	        finalized_observations = {
   893	            slot: _observation_from_receipt(
   894	                receipt,
   895	                observation_kind=(
   896	                    "bracket-session-finalized"
   897	                    if session_state == "finalized"
   898	                    else "bracket-session-aborted"
   899	                ),
   900	                session=open_receipt,
   901	            )
   902	            for slot, receipt in finals.items()
   903	        }
   904	        if session_state != "aborted":
   905	            completed_observations.extend(
   906	                finalized_observations[slot]
   907	                for slot in BRACKET_SESSION_SLOTS
   908	                if slot in finalized_observations
   909	            )
   910	        sessions.append(
   911	            CalibrationBracketSession(
   912	                session_id=session_id,
   913	                window_id=str(open_receipt["window_id"]),
   914	                plan_id=str(open_receipt["plan_id"]),
   915	                plan_sha256=str(open_receipt["plan_sha256"]),
   916	                evidence_root_id=str(open_receipt["evidence_root_id"]),
   917	                capability_receipt_digest=str(open_receipt["receipt_digest"]),
   918	                capability_sequence=int(open_receipt["sequence"]),
   919	                slot_attempt_ids=MappingProxyType(
   920	                    {
   921	                        slot: str(open_receipt["slots"][slot]["attempt_id"])
   922	                        for slot in BRACKET_SESSION_SLOTS
   923	                    }
   924	                ),
   925	                state=session_state,
   926	                finalized_slots=MappingProxyType(finalized_observations),
   927	                abort_receipt_digest=(
   928	                    str(abort["receipt_digest"]) if abort is not None else None
   929	                ),
   930	                abort_reason=(str(abort["reason"]) if abort is not None else None),
   931	            )
   932	        )
   933	    return sessions, completed_observations, reasons
   934	
   935	
  1003	    sessions, session_observations, session_reasons = (
  1004	        _bracket_sessions_and_observations(receipts)
  1005	    )
  1006	    reasons.update(session_reasons)
  1007	    session_attempt_ids = {
  1008	        attempt_id
  1009	        for session in sessions
  1010	        for attempt_id in session.slot_attempt_ids.values()
  1011	    }
  1012	    if set(pending) & session_attempt_ids:
  1013	        reasons.add("calibration_ledger_bracket_session_conflict")
  1014	    observations.extend(session_observations)
  1015	    content_classification.clear()
  1016	    classification_observations = list(observations)
  1017	    visible_attempts = {observation.attempt_id for observation in observations}
  1018	    classification_observations.extend(
  1019	        observation
  1020	        for session in sessions
  1021	        for observation in session.finalized_slots.values()
  1022	        if observation.attempt_id not in visible_attempts
  1023	    )
  1024	    for observation in classification_observations:
  1025	        if observation.content_id is None:
  1026	            continue
  1027	        classification = (
  1028	            observation.classification_disposition,
  1029	            tuple(
  1030	                (field, observation.identity_epoch.get(field))
  1031	                for field in IDENTITY_EPOCH_FIELDS
  1032	            ),
  1033	        )
  1034	        previous = content_classification.get(observation.content_id)
  1035	        if previous is not None and previous != classification:
  1036	            reasons.add("calibration_ledger_content_conflict")
  1037	        content_classification[observation.content_id] = classification
  1038	    observations.sort(key=lambda observation: observation.sequence)
  1039	    return observations, sessions, reasons
  1040	
  2348	
  2349	
  2350	def terminal_head_pin_for_session(
  2351	    ledger_path: Path,
  2352	    *,
  2353	    session_id: str,
  2354	) -> dict[str, Any]:
  2355	    """Return the sole terminal pin candidate after post or governed abort."""
  2356	
  2357	    try:
  2358	        raw = Path(ledger_path).read_bytes()
  2359	    except OSError as exc:
  2360	        raise CalibrationLedgerError("ledger is unreadable") from exc
  2361	    receipts, parse_reasons = _parse_ledger(raw)
  2362	    observations, sessions, state_reasons = _attempts_and_observations(receipts)
  2363	    del observations
  2364	    reasons = parse_reasons | state_reasons
  2365	    if reasons:
  2366	        raise CalibrationLedgerError(", ".join(sorted(reasons)))
  2367	    session = next((item for item in sessions if item.session_id == session_id), None)
  2368	    if session is None or session.state == "open":
  2369	        raise CalibrationLedgerError("bracket session is not terminal")
  2370	    terminal_digest = (
  2371	        session.finalized_slots["post"].receipt_digest
  2372	        if session.state == "finalized"
  2373	        else session.abort_receipt_digest
  2374	    )
  2375	    final = receipts[-1] if receipts else None
  2376	    if final is None or final["receipt_digest"] != terminal_digest:
  2377	        raise CalibrationLedgerError("session closure is not the terminal ledger head")
  2378	    return head_pin_for_receipt(final)
  2379	
  2380	
  2381	def append_pending_receipt(
  2382	    ledger_path: Path,
  2521	            custody_locator=custody_locator,
  2522	        )
  2523	
  2524	    return _locked_append(Path(ledger_path), build)
  2525	
  2526	
  2527	def head_pin_for_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
  2528	    """Emit the exact candidate pin that must be reviewed and committed."""
  2529	
  2530	    if not _valid_receipt_shape(receipt):
  2531	        raise CalibrationLedgerError("cannot pin a malformed receipt")
  2532	    return {
  2533	        "sequence": int(receipt["sequence"]),
  2534	        "head_digest": str(receipt["receipt_digest"]),
  2535	        "ledger_schema": LEDGER_SCHEMA,
  2536	    }
  2537	
  2538	
  2539	__all__ = [
  1028	        )
  1029	
  1030	    def test_session_candidates_refuse_missing_neighbor_substituted_or_cross_window_binding(
  1031	        self,
  1032	    ) -> None:
  1033	        snapshot, candidates, binding = self._bound_session_fixture()
  1034	        with patch(
  1035	            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
  1036	            return_value=_unissued_acceptance_fixture(),
  1037	        ):
  1038	            _result, reasons = _evaluate_calibration_bracket(
  1039	                candidates,
  1040	                window_start_s=100.0,
  1041	                window_end_s=110.0,
  1042	                bindings=self.bindings,
  1043	                policy=self.policy,
  1044	                ledger_snapshot=snapshot,
  1045	                _allow_unissued_fixture=True,
  1046	            )
  1047	        self.assertEqual(reasons, ("calibration_bracket_binding_missing",))
  1048	
  1049	        substituted = json.loads(json.dumps(binding))
  1050	        substituted["endpoints"]["pre"] = {
  1051	            "attempt_id": candidates[0].attempt_id,
  1052	            "receipt_digest": candidates[0].ledger_receipt_digest,
  1053	            "content_digest": candidates[0].content_id,
  1054	        }
  1055	        substituted["binding_digest"] = _canonical_sha256(
  1056	            {
  1057	                key: value
  1058	                for key, value in substituted.items()
  1059	                if key != "binding_digest"
  1060	            }
  1061	        )
  1062	        self.assertIsNone(
  1063	            validate_calibration_bracket_binding(substituted, snapshot)
  1064	        )
  1065	
  1066	        cross_window = json.loads(json.dumps(binding))
  1067	        cross_window["window_id"] = "window-beta"
  1068	        cross_window["binding_digest"] = _canonical_sha256(
  1069	            {
  1070	                key: value
  1071	                for key, value in cross_window.items()
  1072	                if key != "binding_digest"
  1073	            }
  1074	        )
  1075	        self.assertIsNone(
  1076	            validate_calibration_bracket_binding(cross_window, snapshot)
  1077	        )
  1078	
   569	    def test_open_session_refuses_until_governed_abort_and_never_deletes_partial(
   570	        self,
   571	    ) -> None:
   572	        self._open_bracket_session()
   573	        pre = self._finalize_bracket_slot("session-alpha", "pre")
   574	        open_snapshot = self._snapshot()
   575	        self.assertIn(
   576	            "calibration_ledger_bracket_session_open",
   577	            open_snapshot.refusal_reasons,
   578	        )
   579	        self.assertEqual(
   580	            [observation.bracket_slot for observation in open_snapshot.observations],
   581	            ["pre"],
   582	        )
   583	
   584	        closure = abort_bracket_session(
   585	            self.ledger,
   586	            session_id="session-alpha",
   587	            reason="science_member_failed_before_post",
   588	        )
   589	        self.assertEqual(closure["event"], BRACKET_SESSION_ABORT_EVENT)
   590	        self.assertEqual(closure["finalized_slots"], ("pre",))
   591	        self.assertEqual(closure["unused_slots"], ("post",))
   592	        self._write_pin(
   593	            terminal_head_pin_for_session(
   594	                self.ledger, session_id="session-alpha"
   595	            )
   596	        )
   597	        snapshot = self._snapshot()
   598	        self.assertEqual(snapshot.refusal_reasons, ())
   599	        self.assertEqual(snapshot.observations, ())
   600	        session = snapshot.bracket_session_by_id["session-alpha"]
   601	        self.assertEqual(session.state, "aborted")
   602	        self.assertEqual(session.finalized_slots["pre"].receipt_digest, pre["receipt_digest"])
   603	        with self.assertRaisesRegex(CalibrationLedgerError, "not open"):
   604	            abort_bracket_session(
   605	                self.ledger,

2026-08-07T17:46:58.854855Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "if PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -q; then
  printf 'CANONICAL_SUITE_EXIT=0\\n'
else
  printf 'CANONICAL_SUITE_EXIT=nonzero\\n'
  exit 1
fi" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1
Audit complete. Three contract defects are independently reproduced; focused and canonical suites remain green, demonstrating regression gaps rather than incidental test breakage.
  ✓ Read stop card, queue, playbook M0, orchestration, frozen memo, ratification, and named decisions
  ✓ Inspect the full uncommitted diff and map changes to contract clauses
  ✓ Run read-only/focused regressions and construct the L5 adversarial scenario
  ✓ Report only evidence-backed findings with severity, file:line, and failing scenario
codex
## Audit verdict: HOLD

Three contract defects remain.

1. **BLOCKER — L5 is not closed: intended-window identity and `runs_root` binding are optional.**  
   [calibration_bracketing.py:600](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_bracketing.py:600), [calibration_bracketing.py:1232](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_bracketing.py:1232), [calibration_bracketing.py:1504](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_bracketing.py:1504)

   `window_id`, `plan_id`, plan SHA, and evidence-root ID default to `None`; validation compares them only when supplied. `calibration_bracket_for_bundles()` also never uses `runs_root` to bind the selected session to the evaluated custody root.

   **Failing scenario:** pass a valid binding from another session whose same-T1 endpoints temporally bracket the victim window, while omitting the optional intended-window arguments. My probe returned:

   ```text
   reasons=(), status=passed,
   selected_session=session-alpha, selected_window=window-alpha
   ```

   despite the evaluated window being the conceptual victim. The added regression at [test_calibration_bracketing.py:1030](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/tests/test_calibration_bracketing.py:1030) only tampers a binding so it conflicts with its own session; it does not supply a second, internally valid neighbor binding. Require all intended identity fields and bind the actual evaluated root/bundle provenance.

2. **BLOCKER — aborting a session removes finalized observations from D-109’s authoritative trigger universe.**  
   [calibration_ledger.py:892](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:892), [calibration_ledger.py:904](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:904), [calibration_ledger.py:1014](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:1014)

   Finalized slots from an aborted session remain reachable through `session.finalized_slots`, but are omitted from `snapshot.observations` and therefore from `post_cutoff_live_observations()`. That correctly prevents bracket-candidate use, but incorrectly deletes them from D-109 R2.3/R2.5’s “every governed observation” and “new content ID” population.

   **Failing scenario:** finalize PRE as `systematic-invalid`, append the governed abort, and commit its terminal pin. The resulting snapshot is valid, but my probe produced:

   ```text
   snapshot_observations=[]
   post_cutoff_live=[]
   recoverable_session_slots=[('pre', 'systematic-invalid')]
   ```

   A later evaluation therefore cannot observe the systematic failure or fire `new_systematic_failure_challenges_preflight_screen`. The test at [test_calibration_ledger.py:599](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/tests/test_calibration_ledger.py:599) codifies this wrong empty-universe expectation. Preserve finalized aborted observations in the ledger observation universe and exclude them only in candidate discovery.

3. **HIGH — the generic pin helper permits the explicitly rejected mid-window pin commit.**  
   [calibration_ledger.py:596](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:596), [calibration_ledger.py:2527](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:2527)

   `_valid_receipt_shape()` now accepts every bracket-session receipt, so the legacy public `head_pin_for_receipt()` emits pins for the session-open receipt and PRE finalization—not only terminal POST/abort receipts.

   **Failing scenario:** after finalizing PRE, call the familiar generic helper. My probe successfully produced a sequence-2 pin candidate for `slot=pre`. If committed, the snapshot has `bracket_session_open` but no head mismatch; `is_governed_open_bracket_extension` becomes false and the writer refuses the reserved POST, stranding the night. Reject bracket-open/PRE receipts in the generic helper and make `terminal_head_pin_for_session()` the only session pin route.

The remaining reviewed properties held: physical-head/committed-pin equality is checked atomically at session open; slots are immutable, ordered and one-use; abort is append-only and retains partial custody; imports remain excluded from candidate discovery; and the writer rejects wrong session, slot, attempt, custody, epoch, and T1 values without silently invoking ordinary reservation.

Focused ledger/bracketing/writer tests and the canonical suite completed successfully. The worktree remained unchanged.
tokens used
404,797
## Audit verdict: HOLD

Three contract defects remain.

1. **BLOCKER — L5 is not closed: intended-window identity and `runs_root` binding are optional.**  
   [calibration_bracketing.py:600](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_bracketing.py:600), [calibration_bracketing.py:1232](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_bracketing.py:1232), [calibration_bracketing.py:1504](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_bracketing.py:1504)

   `window_id`, `plan_id`, plan SHA, and evidence-root ID default to `None`; validation compares them only when supplied. `calibration_bracket_for_bundles()` also never uses `runs_root` to bind the selected session to the evaluated custody root.

   **Failing scenario:** pass a valid binding from another session whose same-T1 endpoints temporally bracket the victim window, while omitting the optional intended-window arguments. My probe returned:

   ```text
   reasons=(), status=passed,
   selected_session=session-alpha, selected_window=window-alpha
   ```

   despite the evaluated window being the conceptual victim. The added regression at [test_calibration_bracketing.py:1030](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/tests/test_calibration_bracketing.py:1030) only tampers a binding so it conflicts with its own session; it does not supply a second, internally valid neighbor binding. Require all intended identity fields and bind the actual evaluated root/bundle provenance.

2. **BLOCKER — aborting a session removes finalized observations from D-109’s authoritative trigger universe.**  
   [calibration_ledger.py:892](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:892), [calibration_ledger.py:904](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:904), [calibration_ledger.py:1014](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:1014)

   Finalized slots from an aborted session remain reachable through `session.finalized_slots`, but are omitted from `snapshot.observations` and therefore from `post_cutoff_live_observations()`. That correctly prevents bracket-candidate use, but incorrectly deletes them from D-109 R2.3/R2.5’s “every governed observation” and “new content ID” population.

   **Failing scenario:** finalize PRE as `systematic-invalid`, append the governed abort, and commit its terminal pin. The resulting snapshot is valid, but my probe produced:

   ```text
   snapshot_observations=[]
   post_cutoff_live=[]
   recoverable_session_slots=[('pre', 'systematic-invalid')]
   ```

   A later evaluation therefore cannot observe the systematic failure or fire `new_systematic_failure_challenges_preflight_screen`. The test at [test_calibration_ledger.py:599](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/tests/test_calibration_ledger.py:599) codifies this wrong empty-universe expectation. Preserve finalized aborted observations in the ledger observation universe and exclude them only in candidate discovery.

3. **HIGH — the generic pin helper permits the explicitly rejected mid-window pin commit.**  
   [calibration_ledger.py:596](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:596), [calibration_ledger.py:2527](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/u1/joulewise/calibration_ledger.py:2527)

   `_valid_receipt_shape()` now accepts every bracket-session receipt, so the legacy public `head_pin_for_receipt()` emits pins for the session-open receipt and PRE finalization—not only terminal POST/abort receipts.

   **Failing scenario:** after finalizing PRE, call the familiar generic helper. My probe successfully produced a sequence-2 pin candidate for `slot=pre`. If committed, the snapshot has `bracket_session_open` but no head mismatch; `is_governed_open_bracket_extension` becomes false and the writer refuses the reserved POST, stranding the night. Reject bracket-open/PRE receipts in the generic helper and make `terminal_head_pin_for_session()` the only session pin route.

The remaining reviewed properties held: physical-head/committed-pin equality is checked atomically at session open; slots are immutable, ordered and one-use; abort is append-only and retains partial custody; imports remain excluded from candidate discovery; and the writer rejects wrong session, slot, attempt, custody, epoch, and T1 values without silently invoking ordinary reservation.

Focused ledger/bracketing/writer tests and the canonical suite completed successfully. The worktree remained unchanged.
