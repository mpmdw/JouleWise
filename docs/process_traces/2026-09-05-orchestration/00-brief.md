# Orchestration consult brief (magistrate → astra), 2026-09-05

## Ed's instructions (verbatim)
1. "keep spamming astra use it instead of sol in all cases now. use sol where you would have used terra. luna max for simple tasks. astra high for an equal use in all parts for fable 5.1 with 5.1 deciding final merges."
2. "it's a little more complex than that. you should treat astra as a peer that reviews major design specs. think about it logically. if you have an equal fable 5.1 counterpart that has a diverse point of view different from yours, use it smartly like you would integrate it into the orchestration process. i'll leave it to you to see how you think about it. consult astra maybe too about how to organize the orchestration between the available models to get this work done quickly and efficiently."

## Current doctrine (private notes, pasted because they are untracked)
# JouleWise orchestration doctrine (Ed's private, untracked notes)

Moved here from `~/.claude/CLAUDE.md` on 2026-07-27 so it loads in JouleWise and
its worktrees only, instead of in every project on this machine. The delegation
and review playbooks remain global skills.

## Multi-model orchestration (Ed's standing instruction; validated on JouleWise 2026-07-06/07)

Ed wants implementation delegated to the local Codex CLI (current model: gpt-5.6-sol, "Sol"; effort axes in rule 10 — high default for ordinary individual work, xhigh only for named hard-task triggers, ultra ONLY for subagent-spawning sessions), bidirectional cross-model review with discussion, Fable subagents for judgment-dense parallel threads, and the whole loop instrumented and improved over time. Invocation: ~/.local/bin/codex-run-v3 (claude-codex-report/v1 envelope via --genre, WRITE_SCOPE enforcement exit-77, NEEDS_SCOPE/NEEDS_RULING early-return protocols, manifest v3 event stream, codex-usage quota guard); repo-local paths (JouleWise): the repo's CLAUDE.md + `docs/contracts/bridge_protocol.md` in the CURRENT CHECKOUT are authoritative. The playbooks live as global skills — use them, don't re-derive:

- **council** — event-driven review council: when to convene full council vs light review vs solo, roles, discussion protocol, council-log recording, per-layer catch-rate instrumentation.
- **codex-delegation** — Codex invocation, the six-part prompt contract, sandbox limits, and token-efficient consumption (read only the final message + `git diff`, never bridge transcripts).
- **adversarial-review** — review-packet scout → distinct lenses → severity-tiered verification (blockers 2 refuters with DISTINCT lenses / should-fix 1 / nits 0), Sol xhigh refuters by default; delta re-audit after every fix round (§C-028 amendments).
- **multi-stream-worktrees** — parallel streams: worktree + branch per stream, lead-driven Sol pipelines under enforced WRITE_SCOPE, integration tree before any merge wave, separate PRs (§C-028 amendments).
- **consistency-sweep** — end-of-session delegated sweep (Sol xhigh) over process docs before the final bookkeeping commit.

Hard rules that override convenience:

1. **The lead never delegates final verification.** Sub-agent or Codex "tests green" is necessary, never sufficient — every hardware/integration bug to date was caught only by lead-side live verification.
2. **Findings are discussed, not silently applied** — but only design-bearing ones (blockers, architecture, conventions), bounded to 1–2 rounds; the lead decides unresolved disagreements and records dissent. Invite the peer's design judgment explicitly; it has out-designed the lead's proposals when asked. AMENDED (Ed-prompted, 2026-07-11): design consultation is the DEFAULT, not the exception — for any design-bearing decision (new schemas/contracts/interfaces, non-trivial architecture, scheduling of interdependent streams, process design), run a bounded PRE-decision Sol consult (xhigh, 1 round, explicit license to disagree) unless the decision is trivial or time-critical. Final say stays with the lead (delegation is economics, not preferred judgment — but the record shows Sol's design input WINS often enough that not soliciting it is the error). Keep score in the codex-delegation field notes: where its design beat the lead's, where it lost; lead-weighted domains so far are cross-session judgment, risk appetite, and process authority.
3. **The loop scales with the cost of being wrong** — full council by trigger (new adapters, contract changes, hardware-adjacent, pre-merge series), not by ritual. Solo is correct for low-risk work.
4. **Multi-commit sessions land as branch + PR** (audit trail); single low-risk commits may go to main where that's repo convention. AMENDED (Ed, 2026-07-08): the lead MAY self-merge its PRs after a thorough lead + Sol review of the FINAL head — the required gate shape lives in operation-loop §5 (oversight reviewers → lead triage → Sol fixes → CI green → fresh pass over any post-review commit).
5. **Instrument the loop:** council-log entries record each layer's unique catches and rough spend; a layer with zero unique catches over two sessions is dropped. Process conventions get decision-log entries so they bind future sessions.
6. **Main-loop context is the scarcest resource:** delegate reading-heavy work, consume sub-agent results as summaries + `git diff`, keep transcripts out of the loop.
7. **Keep the remote current (Ed's standing preference, 2026-07-07):** push green commits promptly — small doc/bookkeeping commits straight to main, code series as branch + PR; never accumulate unpushed local state waiting for a prompt. Refresh the high-level docs (README, status doc, run-state) every session; the remote is the user's and advisor's view of the project.
8. **Token economics are inverted — Sol is basically free, the lead is expensive (Ed, 2026-07-10).** The lead acts as principal engineer/CTO: it owns all workflow/worktree management, direction, review, and final verification, and shells out ANY high-token-usage task (implementation, diagnosis, bulk reading, fix rounds, review lenses, doc sweeps) to codex/Sol per its judgement — use Sol *extremely liberally*. Current model: gpt-5.6-sol via `~/.local/bin/codex-run-v3` (adapter-aware: --genre injects the claude-codex-report/v1 envelope contract; v2 remains as fallback). The lead spending its own tokens on work Sol could do is the failure mode; the lead skipping its own direction/review/verification duties is the other failure mode. Neither is acceptable.
9. **The C-028-validated gauntlet is the default shape for substantial delegated work (2026-07-11, ~57 invocations of evidence):** implement (enforced WRITE_SCOPE) → independent audit whenever a session's report is missing or uncorroborated (never self-grade) → severity-tiered refuters with DISTINCT lenses (contract vs execution; split verdicts are synthesized by the lead, not majority-voted) → fix rounds with defect-shaped regressions → DELTA RE-AUDIT of every fix round (fix rounds introduce defects — proven twice) → integration tree before any multi-PR merge wave. Details live in adversarial-review and multi-stream-worktrees §C-028 amendments — the ONE homes. Bench-vs-session threshold: if the fix is smaller than the contract needed to delegate it (a 4-line wrap, one specified assertion), the lead does it at the bench. Fable subagents excel at evidence-bounded WRITING via the dictated-fills pattern (lead dictates facts, agent verifies each against primary evidence and flags anomalies — it catches the lead's own miscounts); route bookkeeping finalization, web verification, and draft adjudication support there.
10. **Effort tiers are capability-matched, not cost-matched (Ed, updated 2026-07-12):** `--effort high` is the default for ordinary individual work; use `xhigh` only for design-bearing, cross-contract/multi-component, non-local root-cause, adversarial/integration-review, or otherwise judgment-dense tasks where the cost of error is material; use `ultra` ONLY when the Sol session itself must spawn subagents. When uncertain between high and xhigh, start high and escalate only when an xhigh trigger appears. Push the scope given to a single xhigh session ever wider until returned work first falls below prod standards, then record that empirical ceiling in the codex-delegation skill's effort-tier section and back off one notch. Liberal use, quality-guided not cost-dictated; the lead remains orchestrator regardless of delegated scope. (Detail lives in codex-delegation §Effort-tier policy — the ONE home; don't restate.)
11. **Orchestration topology — magistrate, lieutenant, cold gate (Ed-adopted 2026-07-27; supersedes the "lead" framing in rules 1–10 wherever they conflict).** Ed's direct is **Fable, as MAGISTRATE — not conductor.** Fable owns direction, adjudication, briefs, final live verification (rule 1 transfers intact), and accountability for WHEN TO STOP. It does **not** run the turn-by-turn execution loop; altitude discipline is structural, and Fable found three tool-calls deep in a fix round is itself a trigger. **Opus 5 is LIEUTENANT / operational chief:** worktrees and stream topology, Sol pipeline direction and fix rounds, overnight and hardware-window operation, first-pass review triage, adjudication-packet assembly; its subagents keep the contract lens. Sol remains the execution workhorse.
    **The lieutenant is FORBIDDEN to decide alone** (enumerated, not gestured at): ratifying or amending process rules and skill doctrine; dropping any lens or mechanism; changing cadence numbers; self-exempting from any mandatory trigger; merging edits to the meta-process docs themselves; continuing past any escalation trigger; adjudicating blocker severity downward; reinterpreting a stop signal or prior verdict; anything irreversible (deletion, merge waves, window commitments, claim publication).
    **Who adjudicates the magistrate:** a **COLD FABLE INSTANCE** — fresh session, no loop context — ruling on a MECHANICALLY-assembled packet, paired with an Opus contract-lens refuter for cross-model diversity (a fresh Fable shares its own dispositions even without its sunk costs). **Mandatory triggers, not discretion:** any second fix round on the same defect; any reversal or reinterpretation of a stop signal or verdict; any irreversible action; any proposed process rule; any turn ending in a "waiting" state on a scarce open resource. The magistrate may overrule a cold-instance verdict only with written dissent that Ed sees.
    **STANDING ESCALATION TRIGGER (all roles):** two consecutive rounds failing with the SAME SIGNATURE — same defect class, another missed call site, another failed formulation — is evidence of a structural problem, and the next spend is a CONSULT, not round three.
    **Why this shape:** the costliest failures of 2026-07-26/27 happened because escalation triggers were *eaten*. An adjudicator-on-call only works if the continuation-prone agent chooses to consult it, and **sunk-cost continuation** — treating motion as progress — is precisely the disposition that stops choosing. Accountability must therefore sit in the seat that decides when to stop, because stopping is what the loop-immersed agent demonstrably cannot judge from inside. The periodic **standing fresh-eyes sweep** that operationalises non-reactive outside review lives in the `council` skill — the ONE home; do not restate it here.

## Global skills that encode the loop (names + one-line summaries)
### council
name: council
description: Event-driven multi-model review council — decide when work needs full cross-model review (Claude lead + Codex peer + Opus sweeps), run the session shape, record it in the project's council log. Use when landing adapters/contract changes/multi-commit series, when a sub-agent's work needs counterreview, or when the user asks for council/cross-model review.

# Event-driven multi-model council

A council is cross-model review with discussion — not ceremony. Its value is
uncorrelated blind spots (validated: in one JouleWise session, live hardware
verification, a same-model adversarial workflow, a Codex reverse-review, and
Opus sweeps EACH caught a real issue every other layer missed). Convene it by
trigger, never by ritual; the loop must scale with the cost of being wrong.

## Triggers (event-driven — pick the LIGHTEST tier that covers the risk)

**Full council** (implement → verify → adversarial review → counterreview → discussion):
- New adapter/backend, or any change to shared contract-bearing code
- Anything hardware-adjacent (sub-agent "tests green" is never sufficient there)
- Pre-merge review of a multi-commit series (include a REVERSE review: the peer
  reviews the lead's commits and orchestration decisions — that direction caught
### codex-delegation
name: codex-delegation
description: Delegate implementation and peer review to the local OpenAI Codex CLI (gpt-5.6-sol via codex-run-v3; envelope contract, WRITE_SCOPE enforcement, effort tiers) — invocation, prompt contract, sandbox limits, and token-efficient output consumption. Use when handing a scoped implementation or counterreview task to Codex, in any repo.

# Delegating to Codex (gpt-5.6-sol era; see §Effort-tier policy + ADAPTER.md)

> Model history: gpt-5.5 through 2026-07-09; gpt-5.6-sol ("Sol") since.
> Older sections say "5.5" where history-accurate; doctrine sections are current.

Binary: `codex` on PATH (symlinked from
`/Applications/Codex.app/Contents/Resources/codex`); auth in `~/.codex`.
Repo-local bridge when present (`scripts/codex-bridge new|resume --last|review`)
must be wrapped the same way or bypassed; direct shape:
`codex-run <outfile> -C <repo> -s workspace-write "<prompt>"`.
Sandbox: repo + /tmp writes only, NO network, NO sudo, NO GPU/Metal,
`approval: never`. Treat Codex as a near-peer colleague, not a code generator.

## Invoke (the procedure)

### adversarial-review
name: adversarial-review
description: Token-tiered adversarial review workflow — scout a review packet, fan out review lenses, verify findings proportionally to severity (blockers get 2 refuters, nits get none), with fresh read-only Codex refuters by default (Opus on demand for judgment-heavy verification). Use when reviewing a diff, an adapter, or a sub-agent's implementation before landing it.

# Tiered adversarial review

Findings that haven't survived a refutation attempt are opinions. But
verifying everything equally is the token hog (an untired 22-agent review ran
~700k tokens, mostly 12 verifiers re-reading identical files). Tier the
verification to the cost of being wrong.

## Shape

1. **Scout (one agent, or inline if trivial):** build a review packet ONCE —
   the diff, the relevant contract/spec excerpts, the seam files' key
   sections. Hand the packet to every reviewer; don't let N agents rediscover
   identical context.
2. **Lenses (parallel; default executor: fresh read-only Codex 5.5
   instances** — `codex exec -C <repo> -s read-only -o <outfile> "<prompt>"
### multi-stream-worktrees
name: multi-stream-worktrees
description: Run 2+ independent workstreams in parallel — one git worktree + branch per stream, lead-driven codex-run pipelines by default (subagent directors only for judgment-heavy streams), landing as separate PRs. Use when a session has multiple independent implementation tasks that would otherwise run sequentially or collide in one tree.

# Multi-stream worktree orchestration

Sequential delegation is the wall-clock bottleneck once implementation is
outsourced (~15 min per adapter-sized Codex round). When a session has ≥2
INDEPENDENT streams, parallelize with isolation. Skip all of this for
single-stream sessions — it's pure overhead there.

## THE SUBAGENT WAKE GAP (structural; discovered 2026-07-07, JouleWise 4-stream session)

codex-run's "bounded exit re-invokes you" guarantee holds for the MAIN
LOOP ONLY. A subagent orchestrator that backgrounds a codex-run and ends
its turn is NOT re-invoked when the child exits — it stalls at every
round boundary until something external wakes it. Twice in one session
the whole 4-stream fleet sat dormant 20-30 min with completed Codex work
on disk (detection: orchestrator transcript mtimes vs worktree write
### consistency-sweep
name: consistency-sweep
description: End-of-session docs-consistency sweep — delegate a sweep agent to find stale counts, gate-state contradictions, and cross-referenced numbers that drifted across process docs (and across the global skills), before the final bookkeeping commit. Use at the end of any session that updated status/queue/checklist docs or edited multiple skills, or when docs are suspected stale.

# Docs-consistency sweep

Process-heavy repos duplicate state (test counts, gate status, headline
numbers) across README, status docs, run-state, queues, checklists, and
reports — and prose summaries drift the moment work moves fast. One delegated
sweep (Opus, ~50–80k tokens, a few minutes) has repeatedly found 5–10 real
inconsistencies that both the lead and a peer reviewer then independently
confirmed. Run it BEFORE the final bookkeeping commit, not after.

## Delegation prompt shape

Executor: the council skill §Roles sweeper default is a read-only Codex
lens UNLESS the sweep needs harness access — this sweep usually does (it
must RUN the test suite and git commands for ground truth), so a
Claude-family agent (Agent tool, `model: "opus"`) is the justified default

## Available models and observed roles this week
- Fable 5.1 (Claude): magistrate — direction, adjudication, briefs, final live verification, merges. Expensive.
- Opus 5 (Claude): lieutenant / contract-lens counter-reviews and refuters; Agent tool; ~150-200k tokens per review.
- gpt-6-astra (Codex): three peer audits found the estimand defect that ~100 Sol/Opus/Fable rounds missed; as peer magistrate it won two design points (prompt-0 contrast, desk-script enclosure) with executable arithmetic. Effort high/xhigh.
- gpt-5.6-sol: execution workhorse until today (implementation, refuters, deltas, packets); basically free.
- gpt-5.6-terra, gpt-5.6-luna, gpt-5.5, gpt-5.4-mini: available; luna at max effort now designated for simple tasks.
- Cold Fable gate: fresh claude -p session judging a validated packet, paired with an Opus refuter (rule 11).

## Constraints
- Submission-bound: readiness by 6 Sep, last acquisition night 8 Sep, freeze 9 Sep 18:00 PT; D-174 scope freeze (docs/decision_log.md).
- Ed away; hardware only via the unattended watchdog; Fable tokens are the scarce resource; Codex seats are cheap; one codex runner per worktree; seats cannot commit.
- The C-028 gauntlet (refuter pairs → fix rounds → delta re-audits → same-signature rule → counter-review → apex read → replay → ledger) is the merge shape.
