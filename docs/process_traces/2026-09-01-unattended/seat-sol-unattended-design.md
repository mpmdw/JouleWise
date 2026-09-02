```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"T1 is feasible, but Stage 1 additionally needs a frozen G2-a launch capability and email/deadman path omitted from G-1..G-9.","workspace":{"base_requested":"bdf557c9","base_mode":"descendant","head_start":"cd9b22161a43714288966d3260dd42f64aeb8353","head_end":"cd9b22161a43714288966d3260dd42f64aeb8353","upstream_end":"cd9b22161a43714288966d3260dd42f64aeb8353","branch":"main"},"pathspec":[],"unowned_dirty":["docs/process_traces/2026-09-01-unattended/"],"verdict":{"findings":[{"id":"R1","severity":"blocker","title":"Current G2-a has no pack or launch capability"},{"id":"R2","severity":"blocker","title":"No scheduler, email transport, or deadman notification exists"},{"id":"R3","severity":"should_fix","title":"The D-149 v1 receipt cannot represent post-D-167 authority classes"},{"id":"R4","severity":"should_fix","title":"Process-lineage evidence has no real producer and its agent matcher is weaker than production"},{"id":"R5","severity":"should_fix","title":"Prewindow roots remain pinned to retired _v2 packs"}]},"verification":[{"id":"V1","kind":"inspection","cmd":"git merge-base --is-ancestor bdf557c9 HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},{"id":"V2","kind":"inspection","cmd":"git status --short --branch","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## main...origin/main","?? docs/process_traces/2026-09-01-unattended/"]},"expected":{"exit_code":0,"tail_regex":"^## main\\.\\.\\.origin/main"}},{"id":"V3","kind":"inspection","cmd":"rg -n 'go.?receipt|D149_SCHEMA|process_lineage|sendmail|mailx|smtplib|LaunchAgent|LaunchDaemon|launchd|launchctl' scripts/launch_window.py joulewise/t0_rehearsal.py scripts joulewise --glob '*.{py,sh,zsh,mjs,plist}'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["joulewise/t0_rehearsal.py:719:        if set(value) != _D149_KEYS or value.get(\"schema_version\") != D149_SCHEMA or value.get(\"verdict\") != \"GO\":","joulewise/t0_rehearsal.py:809:    artifact, value, error = _json_record(bundle, \"process_lineage\")","joulewise/t0_rehearsal.py:1129:    \"D149_SCHEMA\","]},"expected":{"exit_code":0,"tail_regex":"D149_SCHEMA"}}],"flags":[{"id":"F1","kind":"baseline_drift","level":"nonblocking","text":"The requested bdf557c9 base has advanced to descendant cd9b2216.","needs":"Lead should synthesize against current main."},{"id":"F2","kind":"lead_ruling","level":"blocking","text":"Stage 1 needs the receipt, G2-a capability, process-lineage, staging, and retry rulings listed in Q6.","needs":"Magistrate rulings plus Ed-ratified E-10 amendment."},{"id":"F3","kind":"verification_gap","level":"nonblocking","text":"No tests or live probes were run in this read-only design review.","needs":"Implementation gauntlet and supervised rehearsal."},{"id":"F4","kind":"residual_risk","level":"nonblocking","text":"A concurrent untracked unattended trace directory appeared during review and was preserved.","needs":"Lead ownership review."}]}
```

## Findings

- R1 — blocker: G2-a explicitly runs before the `_v5` pack exists and may not test `PACK_ROOT`, but `launch_window.py` requires a pack, arm receipt, custody root, and launch manifest (`SHAKEDOWN-G2-RUNSHEET.md:225-233`; `scripts/launch_window.py:38-49`).
- R2 — blocker: repository search finds neither launchd nor email-sending machinery; current launch success is a terminal `execve`, with no parent/wait/retry path (`scripts/launch_window.py:239-267`).
- R3 — should-fix: the v1 GO schema is exact-key C1–C5 and carries no receipt class, window identity, or authorization basis (`joulewise/t0_rehearsal.py:86-95,710-738`).
- R4 — should-fix: G8 consumes a synthetic lineage document, while production uses the stricter exact-exit-1 `pgrep` predicate (`joulewise/t0_rehearsal.py:805-856`; `joulewise/arm_readiness_evidence_t0.py:1312-1314,1720-1729`).
- R5 — should-fix: `prewindow_check.sh --window` still maps alpha/beta/gamma to Qwen2.5 `_v2` roots (`scripts/prewindow_check.sh:49-58,116-136`).

## Q1

For T1, required gaps are G-1, G-2, the initial-scheduler half of G-3, G-4, G-6, G-7, and G-8. G-9’s consumer entry point is already ruled—`launch_window.py`—although its code still needs selection/registration (`reason-code-coverage-delta.md:965-988`). G-5 and G-3’s post-completion fallback half can move to T2 only if the magistrate splits the current all-or-nothing acceptance, which presently requires launch, relaunch, heartbeat, retries, and fallback together (`state_kernel.json:4752-4778`).

Two missing gaps must be added:

- G-10: email outbox, transport, delivery-attempt records, and a morning deadman. D-128 requires a morning surface, but no sender exists (`docs/decision_log.md:8270-8272`).
- G-11: a frozen, armable G2-a diagnostic capability. Today G2-a expressly has no pack, while D-149 condition 2 and `launch_window.py` require one (`SHAKEDOWN-G2-RUNSHEET.md:225-233`; `docs/decision_log.md:172`; `scripts/launch_window.py:40-45`).

Smallest sound shape: one shared `unattended_go_receipt` module owns issue/validate semantics; the supervisor issues, and `launch_window.py` validates and consumes. Do not have the launcher edit an already-issued receipt. The supervisor may perform the final immediate census, but dwell/load evidence and capture-boundary censuses remain producer/chain responsibilities.

Thus Stage 1 is not merely “add launchd”: it must freeze G2-a into a non-claim diagnostic pack/work order, close the real-producer rehearsal blockers, schedule it once, consume a valid GO receipt, and email every terminal outcome.

## Q2

C1 is replaced by nothing. D-167 deliberately preserves D-149 conditions (2)–(5), while D-166 pre-registration remains a separate measurement-design fence—not a readiness verdict (`docs/decision_log.md:193-194,10408-10412`).

Receipt classes:

- `T0_UNATTENDED_DIAGNOSTIC_GO`, `claim_eligible:false`
- later `T0_UNATTENDED_PRODUCTION_GO`
- existing refused class `T0_UNATTENDED_SUPERVISED_REHEARSAL`

The v1 schema does not fit: it requires exactly C1–C5 and lacks class and identity fields (`joulewise/t0_rehearsal.py:86-95,719-738`). Use additive `joulewise.t0_unattended_d149_go_receipt.v2`:

```json
{"schema_version":"joulewise.t0_unattended_d149_go_receipt.v2","receipt_class":"T0_UNATTENDED_DIAGNOSTIC_GO","claim_eligible":false,"schedule_id":"...","window_id":"...","pack_identity":{"path":"...","sha256":"..."},"custody_root":"...","boot_session_id":"...","issued_at_utc":"...","issued_at_monotonic_ns":0,"authorization_basis":[{"kind":"D166_PREREGISTRATION","path":"...","sha256":"..."}],"conditions":[{"condition_id":"C2","status":"PASS","evidence":[]},{"condition_id":"C3","status":"PASS","evidence":[]},{"condition_id":"C4","status":"PASS","evidence":[]},{"condition_id":"C5","status":"PASS","evidence":[]}],"verdict":"GO"}
```

The system supervisor writes it no-clobber at `$WINDOW_CUSTODY_ROOT/control/t0-go/<schedule-id>.json`, with sidecar, before launch; this follows D-149’s before-capture and append-only custody requirements (`docs/process/d149-go-receipt-template.md:3-7,58-62`).

Use new exact refusal `launch_go_receipt_class_refused` for the rehearsal class. Register it additively in D-078’s launch-lineage vocabulary and `LAUNCH_LINEAGE_REASON_CODES`, with emission/exhaustiveness tests. Reusing `launch_consumption_invalid` would be dishonest: that code is defined for malformed/noncanonical lifecycle custody, whereas a rehearsal receipt is valid but lacks production authority (`docs/decision_log.md:9523-9544`).

## Q3

Use a system LaunchDaemon, root-installed once but configured with `UserName=edr`. It survives logout/reboot and does not depend on an Aqua session. Powermetrics needs the existing `sudo -n` authorization, not GUI access; the repo’s readiness probe invokes the binary directly (`scripts/quiet_mac_prep.sh:46-50`). The chain is likewise a shell/caffeinate foreground process (`window_runbook.md:1730-1735`). AppleScript app cleanup is opportunistic and must not be treated as powermetrics authority (`scripts/quiet_mac_prep.sh:16-30`).

Wake layers for T2:

1. Primary: the supervisor directly launches a fresh headless session only after a canonical completion/refusal event.
2. Independent fallback: a separately installed launchd job, separately triggered and state-file-driven, checks the same terminal event plus absence of a valid heartbeat. It never launches solely because a wall-clock deadline expired while capture might still be live.

Heartbeat: `$WINDOW_CUSTODY_ROOT/control/agent-heartbeat-<cycle>.json`, no-clobber, containing schema, cycle/schedule digests, PID plus start identity, boot ID, reviewed HEAD, UTC/monotonic times, and `first_action:"heartbeat_claim"`. “Stand down” means record `heartbeat_verified`, cancel further direct attempts, and let fallback write `fallback_stood_down`.

Recommend one primary attempt and at most two fallback attempts with backoff. The 600-second deadline needs a new ruling: T26’s 600 seconds governs R1-to-validity-origin T-0 issuance, not generic agent startup (`COLD-GATE-RULING.md:196-217`). Reusing 600 seconds is sensible but not already authorized.

A failed night writes an immutable refusal first, then email retries may continue. Measurement launch is never retried after GO/capability consumption; the current launcher already treats consumption as linearization and has no retry (`scripts/launch_window.py:239-267`).

## Q4

At arm time, the on-demand LaunchDaemon starts while the agent still exists, snapshots the agent’s exact `(pid,start_time,executable,argv_digest)` identity, and acknowledges the handoff. Existing Darwin identity machinery already treats disappearance/PID reuse/exec/reparenting as distinct fail-closed states (`joulewise/quiet_guard_process.py:1-8,91-188`).

The agent then exits. Its own “last act” is only intent, never proof. The supervisor observes that exact identity disappear and writes `agent_exit_observed_monotonic_ns`; the magistrate should rename or define the current misleading `agent_exit_monotonic_ns` field accordingly. Immediately before GO it runs the unchanged production predicate: `pgrep -lf "codex|claude|t3"` must exit exactly 1 with empty stdout (`arm_readiness_evidence_t0.py:1312-1314,1720-1729`).

The chain writes censuses at non-metered boundaries: before pre-calibration, before and after each `run_campaign` stage, and after post-calibration. Never run census commands while powermetrics is sampling. The resulting lineage is written by the supervisor/chain, not reconstructed by the returning agent.

An idle interactive `claude` or T3 Code process causes immediate refusal plus email. It is not waited around or killed opportunistically. Yes: on window nights the headless loop should replace the interactive session entirely; otherwise the unchanged name predicate guarantees refusal.

## Q5

Night protocol:

1. Interactive `/loop` finishes all desk decisions and durable bookkeeping.
2. It writes `loop-suspend.json` in custody with cycle ID, reviewed HEAD, schedule/pack digests, agent identity, expected terminal paths, and the exact next queue pointer.
3. LaunchDaemon acknowledges that record and captures the live agent identity.
4. The interactive session exits; only then may the scheduled T-0 sequence begin.
5. After completion/refusal, the headless session’s first scripted action writes the heartbeat. Its first project-file read is `RUN_STATE.md`, the repository’s declared single restart pointer (`RUN_STATE.md:1-11`), followed by the active stop card and queue per Mission M0 (`docs/agent_playbook.md:50-65`).

`loop-suspend.json` verifies the cycle; it does not become a competing source of project truth. The relaunched Fable lead should read only targeted intake plus the terminal summary, then delegate bulk harvest/judgment packets to Sol/Opus. D-128 already assigns the lead harvest, mint, verdict, re-arm, and paper loop (`docs/decision_log.md:8251-8256`).

## Q6

Required before Stage 1 launches:

1. Magistrate: rule G2-a’s packless contradiction—recommended disposition is a frozen, non-claim diagnostic pack/work-order accepted by the ordinary arm/launcher path (`SHAKEDOWN-G2-RUNSHEET.md:225-233`; `launch_window.py:40-45`).
2. Magistrate: adopt v2 receipt classes, C2–C5 exact census, and pre-registration as separate `authorization_basis` (`decision_log.md:194`; `t0_rehearsal.py:86-95`).
3. Magistrate: register `launch_go_receipt_class_refused` under D-078; G7’s consumer itself needs no new ruling because it was already assigned (`reason-code-coverage-delta.md:965-988`).
4. Magistrate: split Stage-1 diagnostic launch acceptance from Stage-2 relaunch acceptance; the current kernel combines them (`state_kernel.json:4752-4778`).
5. Magistrate: rule process-lineage “exit observed” semantics and permitted non-metered census points (`t0_rehearsal.py:96-105,805-856`).
6. Magistrate: rule heartbeat deadline, attempt count/backoff, and fallback stand-down semantics; T26 does not automatically govern this use (`COLD-GATE-RULING.md:196-217`).
7. Ed: ratify and land the E-10 amendment before automation; current runbook explicitly reserves physical launch (`window_runbook.md:813-816,1294-1327`; kernel fence `state_kernel.json:4781-4788`).
8. Ed: execute the one reviewed privileged LaunchDaemon installer command after its gauntlet (`decision_log.md:8223-8231`). No quiet-guard install belongs here.
9. Ed: approve the exact email recipient/from-account and complete any one-time Mail automation prompt; a daytime canary must be received before scheduling the first unattended night.

## Q7

| Risk | Detector |
|---|---|
| Wrong G2-a bytes launch because today it is an unfrozen generated shell | Diagnostic pack digest, exact manifest argv, arm receipt, GO pack identity, and consumed-launch replay (`launch_window.py:102-167,239-260`) |
| Agent or PID-reused process contaminates capture | Kernel identity snapshot plus exact-exit-1 final census and censuses at every non-metered stage boundary (`quiet_guard_process.py:1-8`; `arm_readiness_evidence_t0.py:1312-1314`) |
| Census instrumentation changes the measured number | Structural test proving census calls occur only outside `run_campaign`/powermetrics intervals; custody timestamps checked against stage boundaries |
| Timer or recovery path launches measurement twice | O_EXCL schedule claim, single-use arm consumption, terminal burned state, and assertion that only agent/email—not measurement—has retry loops (`launch_window.py:262-267`) |
| Failure is silent or email transport wedges | Independent morning deadman, immutable outbox before send, delivery-attempt receipts, bounded email-only retries, and pre-night received canary |

## Residual risk

Mail.app submission proves local handoff, not inbox delivery; the canary is therefore essential. LaunchDaemon execution, sleep/reboot recovery, and the real producer-built ten-gate rehearsal remain live gates, not facts established by this review.

## Stage plan

| Stage | Files touched | New modules | Interfaces | Refusal codes | Tests | Ed-hands residue | Rulings needed | Est. LOC |
|---|---|---|---|---|---|---|---|---:|
| 1 — unattended G2-a | `launch_window.py`, `capture_t0_step.py`, `prewindow_check.sh`, `gen_g2_phase_d.py`, `arm_readiness_evidence_t0.py`, `t0_rehearsal.py`, G2 runsheet, runbook/template, launchd installer/plist, registries/tests | `unattended_supervisor.py`, `unattended_go_receipt.py`, `unattended_process_lineage.py`, `unattended_email.py` | schedule work order → T-0 → GO v2 → launcher → terminal event → email | `launch_go_receipt_{missing,invalid,class_refused}`, scheduler/email codes | schema mutations; double-fire; PID reuse; exact pgrep; stale roots; Mail canary fixture; producer-built ten-gate rehearsal | one installer command, E-10 ratification, Mail prompt/canary, ruled supervised rehearsal sitting | Q6 items 1–9 | 2,400–3,400 |
| 2 — agent returns | supervisor/installer, fallback plist, loop docs/tests | `unattended_relaunch.py`, `agent_cycle_claim.py` | terminal event → direct wake/fallback → heartbeat → bounded retries | `agent_{launch,heartbeat}_failed`, `fallback_terminal_unproven` | duplicate wake, late heartbeat, fallback during live capture, PID claim collision | none per night | heartbeat/retry ruling | 700–1,000 |
| 3 — G2-b/transaction | receipt module, G2/transaction runsheets, email-reply importer, runbook/tests | optional `transaction_go_import.py` | diagnostic/production classes; one-time Ed GO reply → custody authorization | class/authorization-specific production refusals | wrong/replayed email GO, class crossing, G2-b and transaction dry runs | one-time transaction GO email; reboot/non-interference as already ruled | production receipt class and email-GO authentication | 500–800 |

## Where I disagree with the packet or the rulings' ordering

The packet undercounts two Stage-1 blockers: email/deadman delivery and the fact that current G2-a has no pack. I also would not overload `launch_consumption_invalid` for a valid rehearsal-class receipt, nor treat T26’s T-0-specific 600-second bound as automatic agent-relaunch authority. D-169 correctly reverses D-127 §5’s ordering; the remaining necessary change is splitting T1 from T2 acceptance without weakening either.

Confidence: high on the gap analysis and staging; medium on Mail/launchd operational details until the daytime canary and supervised rehearsal execute.