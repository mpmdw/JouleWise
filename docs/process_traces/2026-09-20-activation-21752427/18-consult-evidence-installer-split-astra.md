```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"[read] Prefer staged evidence CLI and shared installer.","workspace":{"base_requested":"5726ba14","base_mode":"exact","head_start":"5726ba14","head_end":"5726ba14","upstream_end":"5726ba14","branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"should_fix"},{"id":"F2","severity":"should_fix"},{"id":"F3","severity":"should_fix"}]},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_evidence_arm_sequence","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}}],"flags":[]}
```

## Findings

**F1 — should_fix — Make preparation resumable without reauthoring.** [read] `gen_evidence_night.generate` refuses existing artifacts, while `write_night_plan` can replace an existing v2 plan. Blindly rerunning steps 1–2 either fails or changes sealed bytes. Idempotence belongs in the new entry point, preserving the original authored time, H, t0 and artifacts.

**F2 — should_fix — Do not promote template conveniences into permanent gates.** [read] Record 17 requires 40 minutes remaining again at publication and exactly four retained roots. `ARM-RETRY-POLICY` instead governs publication by install close and plan age; D-181 rejects artificial spacing. A literal discovery list becomes obsolete after every retained night.

**F3 — should_fix — Resolve the headless lifecycle before promising unattended arming.** [read] `NIGHT_HANDBACK` blocks arming with **any live resident supervisor**; `start_session_guarded` records the headless lead’s own supervisor. A child command cannot satisfy this by exiting after installation. Record 17 also requires an owner-present probe. These are separate obstacles to zero-owner operation; neither disappears through installer refactoring.

**Ranked design**

1. **[read-derived proposal] Build `python -m joulewise.evidence_night prepare --kind quiet_predicate_evidence --t0 next [--head H]`.** These are its only scientific/selection inputs. Resolve omitted H once from freshly fetched `origin/main`; pin the full SHA. Use established root locations and the frozen protocol, rather than exposing path, cadence or threshold overrides. “Next” selects an unambiguous whole minute ≥ preparation-time now + 40 minutes; it cannot predict future quietness.

   Derive identities using t0 **including time** and H, avoiding the current same-day collision. Create a detached clone and locked venv; execute authoring, generator, preflight, schedule and real installer render-only **from that clone**. Keep the plan outside discovery; wrapper/manifest placement follows the existing generator. Return the frozen triple, digests, schedule, staged path and notice draft, then stop.

   Persist the resolved selection before advancing. Resume one matching incomplete preparation before resolving defaults again; ambiguous candidates refuse. Reuse only positively identified owned directories. A sealed candidate is verified byte-for-byte, never regenerated. Incomplete work resumes only where completed outputs can be verified; conflicting files remain untouched. Publication or invocation ends preparation’s reusable state.

2. **[read-derived proposal] Add a thin evidence lifecycle façade, not another installer.** Provide render/probe/install/uninstall/verify operations through the evidence entry point, delegating to existing installer machinery. Do **not** add caller-controlled `--kind evidence` to the calibration installer: wrapper payload identity already selects the correct branch after #369. Require the façade’s asserted kind to match that identity before admission; retain malformed-plan cleanup compatibility for uninstall.

   Reuse `Transaction`, plist rendering, launchd probe, evidence receipt validation and rollback. Initially leave their implementations where they are. Moving them into a plugin framework adds risk without removing bench work. Run the composed sequence through the façade; retain existing calibration compatibility tests.

3. **[read-derived proposal] Automate notice-to-arm only as the second increment.** This needs transport and lifecycle integration, not scientific changes.

**Steps 3–5**

[read-derived proposal] A later `arm --candidate PATH --no-objection-seconds N` can orchestrate the mechanics. Default **N = 0**: the handbook explicitly requires accepted email before publication with **no additional minimum interval**. A supplied positive N is elapsed from recorded service acceptance, never from draft creation.

[read-derived proposal] Use durable phases: notice accepted → optional wait → fresh prerequisites/veto observations → `retry_allowed` → atomic publication → launchd probe → receipt validation → install → loaded-plist verification → departure handoff. Preserve attempt directories exclusively. Restart reconciles recorded mail and installation outcomes; a lost response never means “not sent” or “not installed.” After publication failure, retain uninstall-first recovery and require exit 0 before matching-byte unpublication.

[read-derived proposal] Send exactly one event notice to `claude2.glaring610@passmail.net`, without cc. Read authenticated Ed replies on the current and known prior notice threads **when readable**, owner-authored directive issues **including bodies/comments**, local STOP/standdown and other authorized readable NO relays. Preserve every observed NO across attempts and thread changes. An unreadable thread is a recorded limitation, expressly **not a veto** under today’s policy; failed required directive/stop observation cannot be fabricated as clear. An open unresolved directive returns to the lead.

[read] Current code exposes agent Gmail-send tooling, not a demonstrated standalone mail client. [read-derived proposal] Bind a narrow adapter to the already authorized transport; do not invent credentials or silently substitute an issue for mandatory email.

[read-derived proposal] For F3, keep the current refusal until adjudicated. Options are a non-agent arm handoff after the supervisor exits, or an authorized revision distinguishing stale supervisors from current ones. Prefer the former if existing lifecycle controls can prevent a relaunch race; do not build a second scheduler speculatively. A command’s exit cannot certify that its parent agent and MCP children exited.

**Pre-arm checks and observability**

[read-derived proposal] Put host/root/lifecycle checks in the evidence orchestration layer, repeat immediately before publication, and leave `arm_census.py` as the process observer/classifier. Its real-class exit 0 is diagnostic, not clearance. Preparation may report host blockers without withholding safe staged work.

[read] The handbook requires canonical ancestry of the **census fix commit**; record 17’s H happened to be that commit. [read-derived proposal] Preserve that capability requirement rather than requiring the canonical checkout to contain every later records-only H. Never fast-forward a fenced checkout automatically. Preserve the live-supervisor refusal, inspecting `resident_session.supervisor_pid`, process command/start identity and observation errors—not launchctl’s child status.

[read-derived proposal] Add telemetry in a separately reviewed small change: carry actual census argv and producer PID/start identity in `CensusObservation`; record module path and an import-time implementation fingerprint in `append_census_event`. Both ordinary ticks and resident observations use that writer. Do not fingerprint current disk contents on every tick and call that the version already loaded in memory. Telemetry supplements the guard; it does not authorize bypass.

**Refusal inventory**

| Disposition | [read-derived proposal] Requirement and reason |
|---|---|
| Keep | Fenced canonical/other-worktree roots; no overwrite of foreign, retained or invoked candidates; symlink/path collisions; same-filesystem atomic publication. Prevent mistaken writes and lost evidence. |
| Keep | Raw shared bracketed census, ancestry/foreign-workload review, real-night refusal without stub exemption, unknown observations resolved, owned helpers gone before REQUEST. |
| Keep | Discover retained roots and establish harvest/ownership/completion; unknown or active ownership stops. Never delete or hide roots to pass discovery. |
| Keep | Locked environment, pinned checkout, tracked manifest/source equality, ruled registration and chain digest binding, wrapper sidecars and published-plan literal. Keep frozen v2/no-pack protocol and PROVISIONAL status. |
| Keep | Reject unresolved placeholders, invalid kind/schema, stale/future-authored plan, non-minute or ambiguous local t0, existing results, loaded/UNKNOWN jobs, retained prior plists and exclusive install cutoff. Derive timing from `schedule`. |
| Keep | Evidence probe schema, binding/freshness, verify-only/no collect/no load, proven cleanup, consent-repeat requirement and interpreter identity. No probe-success claim of collection. |
| Keep | Use `arm_retry`’s complete refusal inventory. Only `arm_idle_interactive`, `arm_notice_mismatch`, `arm_watchdog_uncertain`, `arm_transport` have its conditional retry exception. Unknown/mixed causes and gate/driver/receipt failures retain their routing. D-182 is a separately evidenced new-plan successor, never same-plan retry. |
| Drop | Calibration ledger/epoch/session inputs, custody-pass arithmetic and calibration receipt-budget fields: no reader or scientific role in this payload. Evidence receipt freshness still applies. |
| Drop | Repeated 40-minute publication gate; keep 40 minutes as default planning runway. No new notice delay, attempt cap, calendar-night restriction or post-harvest spacing. |
| Replace | Exact four-root equality and “only one JouleWise label” with relevant discovery, ownership, conflict and liveness checks. Preserve actual watchdog safety checks. |
| Remove | Per-night script copying, environment placeholders, hand-computed boundaries and separately re-pinned dry-check scripts. Preserve the real composed rehearsal; do not replace it with manufactured plists. |

**Diff plan and prospective WRITE_SCOPE**

[read-derived proposal] Grant exactly the paths below per PR; bookkeeping and immutable trace records remain lead-owned. Each row describes a bounded change.

| PR | File → change |
|---|---|
| 1 | `joulewise/evidence_night.py` → preparation, verification/reuse, evidence lifecycle façade, notice draft and guarded publication consuming real lead-supplied notice evidence. |
| 1 | `tests/test_evidence_night.py` → interruption/resume, collisions, same-day identities, frozen defaults, no publication/mail/install during prepare, refusal propagation. |
| 1 | `tests/test_evidence_arm_sequence.py` → exercise the new entry through real render, publication, supervisor probe, receipt and install validation. |
| 1 | `docs/contracts/evidence_night_entry.md` → command contract, refusal inventory and recovery boundaries. |
| 1 | `docs/process/NIGHT_HANDBACK.md`, `docs/phase_2/derivation_night_runbook.md` → generic command checklist replacing copied scripts; preserve process/science authority. |
| 2 | `joulewise/evidence_night.py`, `joulewise/night_notice.py` → notice/wait/veto orchestration and narrow transport adapter, after F3 disposition. |
| 2 | `tests/test_evidence_night.py`, `tests/test_night_notice.py` → NO persistence, unreadable-thread rule, acceptance uncertainty, interruption and cutoff cases. |
| 2 | `scripts/magistrate_watchdog.py`, `tests/test_magistrate_watchdog.py` → additive census provenance, separately reviewed within this PR. |
| 2 | Same three contract/runbook files from PR 1 → document adopted transport and lifecycle behavior. |

[read-derived proposal] **PR 1 first:** removes script copying while notice acceptance, unresolved directives, ownership judgment and actual agent departure remain a bench checklist. Astra **high**, approximately **4–6 seat hours**. **PR 2:** automate those mechanics only after lifecycle/transport decisions; Astra **xhigh**, approximately **6–10 seat hours**, excluding lead review and live verification. Do not expand its scope into a watchdog lifecycle rewrite without a new brief.

[read-derived proposal] Preserve/run `test_install_night_agent`, `test_run_night`, `test_night_plan_writer*`, `test_gen_evidence_night`, `test_arm_census`, `test_arm_retry`, and affected `test_arm_readiness*`; implementation PRs also run the canonical suite. Add regressions proving preparation never invokes chain/mail/launchctl, and repeated prepare preserves every sealed byte.

[read-derived proposal] I would **not** build a second installer, generic executor framework, new scheduler, automatic scientific retries, automatic block-two arming, fresh owner approval per attempt, or a replacement custody system. Night-specific handbook rewrites remain required by R-9 until explicitly changed; they cannot simply disappear as “ceremony.”

## Residual risk

[executed] Composed arm test: **1 passed**. `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_arm_retry`: **32 passed**. HEAD/upstream remained `5726ba14`; workspace clean.

[executed] No repository writes, network, launchctl or collection. The composed test stubs process-group census only; it proves fixture composition, not live host clearance. Full suite and live verification were not run.