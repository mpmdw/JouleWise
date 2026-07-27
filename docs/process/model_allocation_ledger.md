# Model allocation ledger

Structured, cross-session evidence about **which instrument should do
which kind of work**. The project delegates across four instruments:

- **Sol** — `gpt-5.6-sol` via `~/.local/bin/codex-run-v3` (effort tiers
  `high` / `xhigh` / `ultra`).
- **Opus 5 subagents** — Claude-family subagents spawned by the lead.
- **Fable subagents** — Claude-family subagents at the apex-judgment tier.
- **lead-bench** — work the session lead performs itself.

## What this file is for

`docs/council_log.md` records **per-session deliberation**: who argued
what, what was decided, what dissent was overridden. It is narrative, and
the allocation evidence inside it is buried in prose — you cannot read it
and answer "is Opus 5 actually better than Sol at contract refutation?"
without re-reading a hundred paragraphs. `docs/run_reports/*` are the ONE
homes for individual sessions and have the same shape problem.

This ledger is the **structured complement**: one row per delegated
invocation (or per coherent batch, marked as such), so that a later
session can adjudicate instrument assignment on accumulated evidence
rather than on the most recent session's impression. It answers
allocation questions; it does not replace either source, and every row
points back at one.

It is **append-oriented**. Rows are historical records. Correct a row
only by appending a dated correction line beneath it and saying what
changed; do not silently rewrite an entry (same history-vs-live rule the
project applies to ledgers and dated records everywhere else).

## Anti-fabrication rule (binding)

Every field in every row must trace to **primary evidence actually read**
in this repository or in the tracked skill/memory files, and the row must
name that evidence with a file and a section or line. This is not
ceremony: a fabricated-evidence defect was caught at a lead diff gate
during the 2026-07-08 resume+merge session (`docs/council_log.md` index
row C-010, "fabricated-evidence defect caught at lead diff gate (B-44)"),
and the strongest adversarial catch in project history was a fabricated
0.0 W measurement baseline sitting inside a fully green test suite
(`~/.claude/skills/adversarial-review/SKILL.md` §Rules of thumb).

Rules:

- If a field cannot be verified from a source, write `unknown`. Never
  estimate, never infer a plausible number, never carry a number forward
  from a similar row.
- Where two sources disagree, record **both** in §6 Anomalies and evidence
  gaps and leave the ledger field `unknown` or dual-valued. Do not pick one
  silently.
- Token and cost figures in the sources are almost all self-labelled
  estimates, not billing truth. Carry the label with the number.
- Catches are attributed to an instrument only where the source itself
  attributes them. "The session caught X" is not "instrument Y caught X".

## How to add a row

1. Do the work; record the session's ONE home (run report or council
   entry) as usual.
2. Append one row per delegated invocation, or one row per batch where
   the source only reports the batch (mark it `BATCH` in the Task column
   and say what the source does and does not resolve).
3. Fill `Unique catches` only with catches the source attributes to that
   instrument specifically. `0` and `unknown` are different answers and
   both are useful.
4. Fill `Assignment verdict` with a judgment about the *assignment*, not
   the outcome: right instrument / over-powered / under-powered /
   untested / unattributable.
5. Record the session's lead instrument and effort in §2a **as confirmed
   by Ed**, not as inferred by the lead (see §6, anomaly A-10).

---

## 2. Current standing allocation dictate

**Ed, 2026-07-26** (recorded in
`~/.claude/projects/-Users-edr-code-JouleWise/memory/instrument-mix-authority.md`,
"SUPERSEDING DICTATE"), in substance:

> Mainly use Opus 5 on high or xhigh per the lead's dictate, and consult
> Fable mainly when needed. Opus should be the lead's right hand,
> consigliere, where the lead only adjudicates when there are problems or
> decisions the lead should give a read on.

Operationally:

- **Opus 5 subagents are the primary delegated lieutenant** — `high` by
  default, `xhigh` for judgment-dense work. Reviews, audits, contract
  lenses, design consults, triage support.
- **Fable is consulted when genuinely needed** — a real problem, or a
  decision wanting apex judgment. **This supersedes the 2026-07-25 standing
  rule that Fable be consulted in parallel on every major/design-bearing
  question** (that rule is still written into
  `docs/process_traces/RESUME-2026-07-26.md` §7 "Working model", which
  therefore now records a superseded instruction — see §6, anomaly A-9).
- **Sol remains the unlimited execution workhorse** — enforced
  `WRITE_SCOPE` implementation, runnable probes, audited envelopes.
- **The lead adjudicates rather than performing the labor**, while the
  hard rules (final verification never delegated, design-bearing findings
  discussed, `WRITE_SCOPE` discipline) still bind. Only the model
  assignment is lead-discretionary.

**Standing cost hierarchy (Ed, 2026-07-24; same memory file, "Cost
hierarchy"):** Fable = most scarce; Opus 5 ≈ half Fable's cost, use
liberally; Sol ≈ near-infinite / free. Therefore anything Opus 5 can carry
instead of Fable moves to Opus 5, and anything Sol can carry never burns
Fable tokens. Ed records this as "the ONLY non-logic factor in
allocation"; everything else is capability-matched.

Measured corroboration of the inversion, from one arc (`docs/council_log.md`
§C-028 "Spend snapshot addendum", 2026-07-11, self-labelled estimates at
API list price): Sol ≈ $240 vs Fable-lead ≈ $810 for the same arc — Sol
carried ~180× the token volume at ~1/3.4 the cost, because cache reads
dominate the lead's footprint.

### 2a. Per-session lead-instrument header

Required going forward. The lead must not infer its own identity from the
TUI startup banner, which has been observed showing the wrong model family
(see §6, anomaly A-10). The authoritative source is the
interactive `/model` command, which only Ed can run. Capture it at session
start and record it here.

| Session date | Lead instrument (Ed-confirmed) | Effort (Ed-confirmed) | Confirmed how |
|---|---|---|---|
| 2026-07-26 | **Opus 5 (1M context)** | `high` | Ed ran `/model`; output "Kept model as Opus 5 (1M context)" |
| all sessions before 2026-07-26 | `unknown` | `unknown` | not captured at the time; historical `lead-bench` rows carry unverified attribution (A-10) |

---

## 3. The invocation ledger

Columns: Date | Arc/ID | Task | Instrument | Effort | Task class | Outcome |
Unique catches attributable to THIS instrument | Assignment verdict |
Evidence pointer.

`BATCH` rows mean the source reports an aggregate and does not resolve
per-invocation detail; the row says so.

| # | Date | Arc/ID | Task | Instrument | Effort | Task class | Outcome | Unique catches (this instrument) | Assignment verdict | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| L-001 | 2026-07-07 | C-006 | Refuter/verifier tier across the six-stream parallel batch | Opus subagents | `unknown` | blocker refutation | tier DROPPED from the default roster | **0** unique catches, and none since C-001 | over-powered/redundant *as a redundant lens*; later re-scoped, not reversed, by C-033 | `docs/council_log.md` §C-006 "Layer yield + spend" (l.562-563) and "Meta-review C-006 verdicts adopted" (l.590-593) |
| L-002 | 2026-07-07 | C-006 | 5 gen-1 stream orchestrators silently inherited Opus (session started on Opus by accident) | Opus subagents | `unknown` | multi-stream orchestration | relaunched; explicit `model:` pin made mandatory | n/a — intervention I-2, not an assignment | accident, not evidence about Opus | `docs/council_log.md` §C-006 Interventions, row I-2 (l.544) |
| L-003 | 2026-07-08 | C-017 / suite-build | One fresh-eyes review lens run as a substitute during a Codex quota outage | Opus subagent | `unknown` | code review lens | 1 major catch | **1 major**: tokenize-window bracketing, FakeClock-blind refactor regression | right instrument under outage; the only pre-C-033 datum of Opus as a *distinct* (not redundant) lens | `docs/council_log.md` §C-017 "Layer yield" (l.1116-1117); `~/.claude/skills/skill-usage-log.md` "Suite-build session (2026-07-08)" |
| L-004 | 2026-07-08 | C-020 | 2 independent position papers + a recorded Fable-vs-Codex merit debate (owner-directed) | Fable subagents | `unknown` | severity/merit adjudication support | merit verdict recorded | `unknown` — the entry records session outcomes, not per-instrument catches | unattributable from the record | `docs/council_log.md` index row C-020 (l.54) |
| L-005 | 2026-07-09/11 | C-028 | **BATCH** — ~57 recorded invocations spanning implementation, review lenses, refuters, post-hoc audits, delta re-audits, design consults. Source gives arc aggregates, not per-invocation rows | Sol | 55 xhigh / 2 ultra / 2 high (high both FAILED rc=1) per the arc-close snapshot | mixed | PRs #41–#58 merged; suite 1,220 OK | merge-review layer caught the **lead's own** `--theirs` whole-file merge-resolution loss (only layer to see it); refuter tier narrowed 2 blockers via contradictory paired verdicts; delta re-audits found 2 fresh blockers in newly-reachable paths | right instrument; the 2 ultra sessions predate rule-10 and would be xhigh today | `docs/council_log.md` §C-028 Participants (l.1527-1530), "Unique catches per layer" (l.1565-1601), spend (l.1610-1632) |
| L-006 | 2026-07-09/11 | C-028 | Lead gates over the same arc (live runs, arithmetic, final heads, CI) | lead-bench | `unknown` (see A-10) | live/hardware verification | 3 lead-live-only catches | **3**: P2-044 cadence arithmetic verified exactly (median 0.1199250625, ratio 1.0581313969); live NV-5 localhost gate 3/3; live doctor run — "no static layer could produce them" | fixed constant (hard rule 1); not an open allocation question | `docs/council_log.md` §C-028 "Lead gates" (l.1587-1592) |
| L-007 | 2026-07-11/12 | C-029 | **BATCH** — 3 Sol pipelines (SITE-01 / P2-049 / P2-028): impl, lenses, fix rounds. Index row says 13 invocations; the run report's calibration table lists 10 (see A-6) | Sol | **ultra, unintended** (config passthrough; all invocations) | implementation + review + fix | PRs #61/#62/#63 opened at lead-gated heads | implementer caught a stale kernel authority pointer (half-right); lenses 3-for-3 sessions with unique catches | **over-powered**: ultra was a config accident; 13 invocations ≈ 118M tokens vs 3 xhigh ≈ 7.0M for the equivalent role next session | `docs/council_log.md` index rows C-029/C-030 (l.1501-1502); `docs/run_reports/2026-07-12-agent-lane-triple.md` §Delegation calibration |
| L-008 | 2026-07-11/12 | C-029 | Lead gate on the fix round | lead-bench | `unknown` | severity adjudication / gate | 1 doctrine-grade catch | **1**: the fix round's `succeeded`-only rule would refuse legitimate `capped` cells (FIX-14; third "fix rounds introduce defects" datum) | fixed constant | `docs/council_log.md` index row C-029 (l.1501) |
| L-009 | 2026-07-13 | C-030 | 2 delta re-audits + 1 post-merge integration review | Sol | xhigh (explicit) | delta re-audit + integration review | #61–#63 merged | **2**: DRA-001 (equal-but-malformed identity hashes counted as identity evidence — survived TWO earlier review layers); XSI-1 (installed-wheel CI ran only `--help`) | right instrument, right effort; 3 sessions ≈ 7.0M tokens for the role that cost ≈ 118M the day before | `docs/council_log.md` index row C-030 (l.1502); `docs/run_reports/2026-07-13-restart-merge-deploy.md` §Delegation calibration |
| L-010 | 2026-07-13 | C-031 (bridge v1) | 3-round design discussion held over the MCP bridge itself | Sol | `unknown` (entry does not state) | design consult | 5 draft-choices lead-adjudicated; PR #64 merged | **3 design wins over the lead**, all accepted: hard-block leases vs warn-only; path-level baseline manifests vs status digest; split event logs | design consult to Sol: strong | `docs/council_log.md` index row C-031/bridge (l.1503) |
| L-011 | 2026-07-13 | C-032 (bridge v1.1) | Single design consult over the bridge contract before implementation | Sol | xhigh (MCP discussion lane) | design consult | 5 amendments accepted; spec then implemented | **5 accepted design amendments + 1 CONFIRMED adapter bug** (duplicate `BRIDGE_REPORT_V1` sentinel) that the lead's own full read had missed | strong; highest-yield layer of that session alongside delta re-audits | `~/.claude/skills/codex-delegation/SKILL.md` §Appendix "Bridge-v1.1 design consult scorecard" (l.525-533); `docs/run_reports/2026-07-13-bridge-v11.md` §Delegation calibration |
| L-012 | 2026-07-13 | C-032 (bridge v1.1) | 3 review lenses → 3 fix rounds → 3 delta re-audits | Sol | lenses xhigh/xhigh/high; fixes xhigh/xhigh/high; delta audits xhigh | review + fix + delta re-audit | finding convergence 13→6→2→1; PR #65 merged | lenses **8 unique**; delta re-audits **9**, including **2 corrections of the lead** (a lead-graded nit upgraded by auditor repro; a vacuity the lead's own check missed) | right instrument; the drop to `high` on the last fix round when triggers lapsed was recorded as correct | `docs/run_reports/2026-07-13-bridge-v11.md` §Delegation calibration; `~/.claude/skills/skill-usage-log.md` 2026-07-13 bridge v1.1 entry |
| L-013 | 2026-07-14 | C-033 (AXI intake) | Short read-only coherence review of drafted D-066..D-070 over the audited CLI path | Sol | high | contract/coherence review | verdict DISCUSSION; outcomes authorized | **6 coherence corrections**, all lead-accepted before commit (D-058 supersession; dual-basis bundle-state; D-032 gross-only semantics; C-012→C-013 re-attribution; registry source homes; `request_id` pinning; D-064 index cleanup) | `high` sufficient for a bounded coherence pass | `docs/council_log.md` index row C-033/AXI-intake (l.1507) |
| L-014 | 2026-07-14/15 | C-034 | **BATCH** — 28 Sol sessions ≈ 251M tokens (estimate) across per-order implement → fresh checker → fix rounds | Sol | high and xhigh (mix not resolved per-session) | enforced-scope implementation + checking | S1 and S4 closed; WO-021/WO-022 landed; suite 1532 OK | `unknown` per-session; arc-level: checker-FAIL→fix→delta-PASS on WO-011; 4-record-loss BLOCKER migration found in WO-021 | right instrument at arc level; effort mix unresolved | `docs/council_log.md` index row C-034 (l.1506) |
| L-015 | 2026-07-14/15 | C-034 | ULTRA comparison audit (intended, pre-declared) | Sol | ultra | independent audit (comparison arm) | 2 blockers / 20 findings, triaged per Ed's substance-over-ceremony ruling (7 fixed, 4 bench, 5 queued, rest dispositioned) | 2 blockers | **comparison verdict never recorded** — the entry states the audit ran and what it found, but not whether ultra beat xhigh; see §5 Q4 | `docs/council_log.md` index row C-034 (l.1506) |
| L-016 | 2026-07-14/15 | C-034 | Completeness critic over the arc's close-out | Fable subagent | `unknown` | evidence-bounded critique | 3 gaps closed same session | **3 gaps** | provisional: positive but a single datum with no cost record | `docs/council_log.md` index row C-034 (l.1506) |
| L-017 | 2026-07-15 | C-035 | **BATCH** — ~14 Sol sessions ≈ 71.2M tokens (estimate) across 3 spec pipelines (SA xhigh / SD high / SE xhigh), each author → fresh counterreview → fix → delta | Sol | xhigh / high / xhigh by stream | spec authoring + counterreview | 3 specs landed (`1464c93`, `d2bd5ee`, `3b5c4bf`) | **30+ counterreview findings fixed pre-landing**; the counterreview refuted byte-identical frozen-arm goldens vs actual code | right instrument; per-stream effort assignment recorded and unchallenged | `docs/council_log.md` index row C-035 (l.1505) |
| L-018 | 2026-07-16 | C-036 | 4 readiness audits, workflow-wrapped, run BEFORE work selection | Sol | high | independent audit | clean (1 severity overstated) | **8+**, incl. CI-red on PR #67 that would have blocked Ed's merge; kernel READY-head drift; R-016 drift; DRIFT/latest_report pointers | `high` sufficient for readiness audits | `docs/run_reports/2026-07-16-resumption-nohw-batch.md` §Delegation calibration (row `audits ×4`) |
| L-019 | 2026-07-16 | C-036 | 5 refuters, workflow-wrapped | Sol | high | blocker refutation | clean | **2 narrowings** + 1 severity downgrade (RUN_STATE blocker mitigated by intake path) + factual corrections | `high` sufficient; worth their cost | same file, row `refuters ×5`; `~/.claude/skills/skill-usage-log.md` 2026-07-16 entry |
| L-020 | 2026-07-16 | C-036 | SPLIT-AP fix round FIX-1..5 | Sol | xhigh | pinned-spec fix round | **introduced R1** — but the defect was a lead prompt-defect (the lead's own FIX-1 pin dropped predictor components) | n/a; the delta re-audit caught it (8th "fix rounds introduce defects" datum, first lead-authored) | instrument correct; the *prompt* was the defect — a lead-side failure mode, not a Sol one | `docs/run_reports/2026-07-16-resumption-nohw-batch.md` §Delegation calibration (row `splitap-fix1`) + §Catches |
| L-021 | 2026-07-16 | C-036 | AXI-SD model-pair evidence memo, web verification, dictated-fills pattern | **Fable subagent** | `unknown` (recorded as "dictated-evidence tier"); ~94k tokens | evidence-bounded writing / web verification | clean | **5 anomalies vs scorecard recalls**; zero lead rework | strong for dictated-fills; the only Fable row in the record with a per-invocation catch count *and* a token figure | `docs/run_reports/2026-07-16-resumption-nohw-batch.md` §Delegation calibration (row `sd-web-verify`) and "Yield + spend" |
| L-022 | 2026-07-16 | C-036 | Integration review over merged main (3 streams) | Sol | high | integration review | clean | **0 unique catches — first zero-catch datum for this layer**, tallied against the drop rule | layer on watch; contrast L-005 (38 catches) and L-009 (1) | `~/.claude/skills/skill-usage-log.md` 2026-07-16 entry §6; `docs/run_reports/2026-07-16-resumption-nohw-batch.md` §Delegation calibration (row `integration`) |
| L-023 | 2026-07-16 | C-036 | AXI-SB live probes (B∈{2,4}) and the field-name check before accepting `supported` | lead-bench | `unknown` | live/hardware verification | verdict `supported` accepted only after lead field-name verification | **1**: terminal-UID field-name check before accepting the delegated `supported` verdict | fixed constant; the calibration table explicitly notes "probes were lead work by design" | `docs/run_reports/2026-07-16-resumption-nohw-batch.md` §Catches (lead gate) and §Delegation calibration (row `axi-sb-impl`) |
| L-024 | 2026-07-17 | C-037 | 248-line / 222-bundle floor campaign verified by an "8-agent ultracode extraction" | **`unknown` instrument** | `unknown` | evidence extraction/verification | campaign verified | `unknown` | **unattributable** — the entry names the agent count but not the model; see A-4 | `docs/council_log.md` index row C-037 (l.1508) |
| L-025 | 2026-07-19 | D-078 arc | Three recompute-lens audits vs one causality/physics-framed audit over the same instrument code | Sol | xhigh | independent audit (lens-framing comparison) | recompute lenses passed; physics lens found the defect | **decisive datum**: 3 recompute audits reproduced every number to 1e-13 while the instrument was misattributing 8 J windows; **1 causality-framed audit found it immediately** | instrument was not the variable — **lens framing was**. Ed-confirmed: physics lenses beat recalculation lenses on measurement code | `~/.claude/skills/skill-usage-log.md` 2026-07-19 "LENS DOCTRINE UPDATE" |
| L-026 | 2026-07-22 | C-031 (D-078 close-out) | 3 fresh read-only lenses over a shared packet → 8 refuter verdicts (blockers get 2 distinct lenses) | Sol | xhigh | independent audit + refutation | round-8b delta re-audit caught what two audited rounds missed | lenses: **A1** (v3 claim-eligibility contract divergence), **B1** (ClockStamp physical-sanity gap → understated `B_fiducial` ~3 µs), C1/C2, C3/C4. Refuters: killed A2 and B2 outright (both plausible, both wrong), narrowed C1 to a nit, split A1 | right instrument; **3 of 8 refuters were killed mid-run by an upstream content filter** on adversarial phrasing — recovered by data-quality rephrasing | `docs/council_log.md` §C-031 (2026-07-22) "Layer catches (unique)" and "Failure modes recorded" (l.1676-1699) |
| L-027 | 2026-07-22 | C-031 (D-078 close-out) | Triage of the 8b audit's two "blockers"; L1 adjudication | lead-bench | `unknown` | severity adjudication | both "blockers" were the lead's own authorized bench edits | **2 false-attribution triages + the L1 registered-limitation adjudication** | fixed constant; a lens structurally cannot see edit provenance | `docs/council_log.md` §C-031 "Lead unique" (l.1688-1689) |
| L-028 | 2026-07-24 | C-032 (NEG-8 estimand debate) | One peer round on the clause-10 ruling, under an invited-disagreement debate brief (steelman each option, demand failure modes + examiner view) | Sol | xhigh | design consult / adjudication debate | peer's position adjudicated CORRECT; Ed ratified the amended design | **1 structural correction adopted** (the anomaly screen must not erase drift from the claim budget) — **second recorded case of invited peer design judgment beating a lead ruling** | strong. Calibration note in the entry: invited-disagreement briefs produced markedly higher design yield than review-shaped prompts | `docs/council_log.md` §C-032 (2026-07-24), l.1707-1723 |
| L-029 | 2026-07-24 | collection arc | **BATCH** — 9 xhigh sessions: 3 forensics, 4 implementation waves, 2 rulings-driven resumes | Sol | xhigh | forensics + enforced-scope implementation | PRs #80/#81/#82 landed; NEEDS_SCOPE / NEEDS_RULING fired correctly 4× | delta re-audit **killed a live estimand-biasing design** (two-process idle overlap) pre-merge | right instrument; **the lead violated its own field notes twice** (bench edit during an enforced-scope run; `pkill` without lock cleanup) | `~/.claude/skills/skill-usage-log.md` 2026-07-24 collection-arc entry; `docs/run_reports/2026-07-23-window-a-collection-arc.md` §Arc summary |
| L-030 | 2026-07-24/25 | C-033 | 4 adversarial audit rounds, fresh read-only session per round | Sol | rounds 1–3 xhigh, round 4 high | independent adversarial audit | real mechanisms found in **every** round; ran until dry | r1: estimand-dispatch downgrade, allowance fail-open, anchor-gate bypass, refusal-registry gap (a live test failure). r2: coordinated-downgrade v2, mock-label seam. r3: TypeError on malformed basis, telemetry-triangle downgrade into the frozen arm, lost positive-path coverage. r4: 2 omitted assertions | right instrument, but **severity calibration is not trustworthy**: of 7 blocker-tier claims in rounds 1–2 only 3–4 sustained at tier; rounds 3–4 produced no blockers. Round 4 at `high` still found real residue | `docs/council_log.md` §C-033 "Auditor (fresh Sol, per round)" (l.1743-1759); `docs/run_reports/2026-07-24-screen-budget-gauntlet.md` §The gauntlet |
| L-031 | 2026-07-24/25 | C-033 | **Contract/design refuter lens** in the Ed-directed A/B pairing — 3 agents (~96k / 120k / 144k tokens) | **Opus 5 subagents** | `unknown` — the entry records token sizes, not effort; the session's `high` effort ruling covers the *Sol execution* refuters only (see A-7) | contract-lens refutation | changed the triage outcome in every round it ran | **F2 collapse** (the "broken frozen replay" blocker rested on a misread of the freshness addendum's scoping → landed as a documented superseded wire, not a code fix); **F6 refutation** (already contract-discharged at the consumer boundary); **G1 re-price** (subclass of registered limitation L1); **G2 re-price**; **blast-radius refutation of the auditor's proposed G2 fixture fix**; **A1 terminal-mock-bar — the session's best catch**, an *honest* mock member reaching claim evidence with all mock-exempted barriers disabled, no attacker required, which no auditor saw; the NEG-8 sentinel route on round-3 F2; the F3 fixture-fix refutation | **strong on a single session, n=1 arc.** Never compared head-to-head against a second Sol refuter on the same packet (see §5 Q1) | `docs/council_log.md` §C-033 "Opus-contract refuter (unique)" (l.1760-1776); `docs/run_reports/2026-07-24-screen-budget-gauntlet.md` §The gauntlet |
| L-032 | 2026-07-24/25 | C-033 | **Execution refuter lens** in the same pairing — 2 sessions | Sol | **high** (deliberate: Ed's A/B spec named "sol high" in round 1, carried into round 2 for comparability) | execution-lens refutation with runnable probes | changed triage; supplied the runnable proofs | discovery of the **coordinated-downgrade variants** reproduced on the repo fixture (gate `20.799350577898302 → 20.399350577898304`, exactly the fixture's 0.4 J allowance; asymmetric removal also validates clean); **G2A adjacent blocker** (the reduce layer independently trusts metadata/summary mockness, so fresh re-reduction reproduces the forged exemption); identification of the authoritative mockness source (custody-bound `config().hardware_target.telemetry_backend`); the `mock:*` tagged-source class caveat that saved the fixtures; the estimand-flip demonstration | **`high` sufficient, and the lead ruled this the STRONGER form of the A/B result** — paired distinct-lens refuters at `high` changed triage outcomes that single-lens `xhigh` refuters have historically missed | `docs/council_log.md` §C-033 "Sol-execution refuter (unique)" (l.1778-1794) and "Effort-tier ruling" (l.1845-1855) |
| L-033 | 2026-07-24/25 | C-033 | Dictated-fills drafting/verification agent over this very council entry (~115k tokens) | **Opus 5 subagent** | `unknown` | evidence-bounded writing / bookkeeping finalization | clean | **5 material errors in the lead's own dictation**, including the effort-tier discrepancy that forced the session's effort ruling | strong; per Ed's cost order this is exactly the work that should move off Fable onto Opus 5 | `docs/council_log.md` §C-033 "Rough spend" (l.1814-1818); `~/.claude/skills/adversarial-review/SKILL.md` §C-033 final bullet |
| L-034 | 2026-07-24/25 | C-033 | Severity synthesis on split verdicts, two decision-log addenda, capsule budget/pagination rulings, bench fixes | lead-bench | `unknown` (see A-10) | severity adjudication + rulings | lead synthesized rather than majority-voted where the two lenses split (G1, G2) | **the two D-078 clause-10 addenda** (anchor-fallback gate ruling derived from the a7-vs-a5 prefill-scatter root cause — a7's 11.85 J "floor" was one fallback-anchored member, true floor ≈ 3.3–3.7 J; and the terminal mock bar); severity synthesis keeping F4 at blocker against the contract refuter's downgrade; the capsule shard-budget trim and pagination ruling; the battery-flake adjudications; the bench fixes | fixed constant | `docs/council_log.md` §C-033 "Lead (unique)" (l.1795-1806) and "Dissent recorded" (l.1832-1837) |
| L-035 | 2026-07-24/25 | C-033 | Full-suite gate at each commit head, on the lead bench | lead-bench | n/a | live verification | 5 gated heads | **1**: the D-078 registry test failing at `e7cbf35` (2113 passed / 1 failed), fixed by addendum 2 — the auditor had reported the registry gap, the lead gate is what proved it live | fixed constant; note the intermediate heads have no CI, only lead-bench receipts | `docs/run_reports/2026-07-24-screen-budget-gauntlet.md` §Lead gates |

| L-036 | 2026-07-25/26 | C-038 (FLOOR-LABEL-01) | End-to-end contract lens over the labelled attribution-limited floor path for comparative (ABBA) cells: extraction → canonical floor record → transport group → resolution → claim evaluation → final artifact (~164k tokens, 50 tool uses, ~11 min) | **Opus 5 subagent** | `unknown` — the session records tokens/tool-uses/wall-clock, not an effort tier (same gap as A-5) | contract-lens review of a whole path | verdict **"COMPARATIVE COVERAGE: COMPLETE"**; 4 should-fix + 4 nits | **4**: (a) `_combined_floor` key-sniffing misattributes point-floor diagnostics for a *partially* attribution-limited transport group — publishing one cell's repeatability numbers under another cell's ID — and the heuristic is mirrored bug-for-bug in `artifact.py`, so validation recomputes the same wrong answer and it ships; (b) `floor_conditions` proxies soleness through a stale field that post-construction mutation does not clear; (c) ratio-unit floors publish a J/token claim floor beside joule-valued diagnostics, making the diagnostic read ~150× larger than the floor and **inverting the very relationship the label exists to communicate**; (d) no assertion pins the labelled fields on a comparative extraction row, with 80 ABBA members about to be collected against that path. Plus: `scripts/build_site.py` and `scripts/build_capstone.py` contain **zero** references to the new fields (lead-verified on `impl/floor-label`) | **strong; second trial of the contract lens.** Found a cross-cell *attribution* defect that a validate-or-not probe structurally cannot see — the complement of L-037's catch on the same artifact | `docs/council_log.md` §C-038 "Opus 5 contract lens"; `joulewise/analysis_engine/__init__.py:192` (`_combined_floor`, on `main`); `joulewise/floor_extraction.py` (`floor_conditions`, on `impl/floor-label`) |
| L-037 | 2026-07-25/26 | C-038 (FLOOR-LABEL-01) | Fresh read-only independent audit of the FLOOR-LABEL-01 head (~23 min) | Sol | xhigh | independent adversarial audit | 1 blocker + 1 should_fix; blocker **adjudicated down to registered limitation L1** by the lead | **1, and it is a first**: a runnable probe (V3) showing that the same comparative blocks minted **without** admissible half-widths validate clean via `validate_floor_artifact` and yield `floor_gate` **5e-324 J** vs **2.6484 J** with widths — an artifact that licenses any effect. Sol had no knowledge of L1, so independent rediscovery was **correct reviewer behaviour**, and this is the **first executable demonstration** of a limitation previously argued only on paper | right instrument. Note the pattern: the *audit* was correct-as-found and the *severity* was still the lead's to price against `docs/decision_log.md` — consistent with L-030's severity-calibration finding | `docs/council_log.md` §C-038 "Sol xhigh independent audit"; `docs/decision_log.md` clause 8 (l.4407) and L1 registration (l.4421) |
| L-038 | 2026-07-25/26 | C-038 (window C) | Root-cause diagnosis of the repeated window-C collection failure (~17 min) | Sol | xhigh | non-local root-cause diagnosis | root cause at **high confidence**, with an explicit UNKNOWN preserved | **3**: (1) transient **wall-clock-vs-monotonic slew exceeding the governed 5 ms anchor ceiling** — `MAX_WALL_MINUS_MONOTONIC_SPAN_S = 0.005`, gate `joulewise/uncertainty_evidence.py:367`, detail `wall_minus_monotonic_span_exceeded` l.369; 5.544 ms (≈ +110 ppm) and 7.769 ms (≈ −158 ppm); (2) **corrected the lead's hypothesis** — the failing members' shorter duration was a *consequence* of reduction, not a cause; (3) **correctly refused** to attribute the adjustment to macOS `timed`, marking it UNKNOWN because `joulewise/environment.py:908` assigns `limited_without_admin` unconditionally (the field cannot distinguish "not synchronising" from "no privilege to see it") | **strong.** Refusing to over-attribute is itself the catch — the disciplined UNKNOWN is what keeps a plausible-but-unevidenced cause out of the record | `docs/council_log.md` §C-038 "Sol xhigh diagnosis"; `runs_window_c_20260726_bound/neg8-refcorpus-r11/metadata.json` (`wall_minus_monotonic_span_s` = 0.007769107818603516) |
| L-039 | 2026-07-25/26 | C-038 (process) | Adjudication of the lead's own process failure (the lost quiet window), question pre-assembled by the lead: 21k tokens, **zero tool uses**, 108 s | **Fable subagent** | `unknown` | severity/merit adjudication of a pre-assembled question | decisive; **overturned the lead's own self-diagnosis** and replaced its draft rule with a better-shaped set | **4**: (1) the lead's proposed "act-anyway deadline" rule was **not** the generalization — with a working wake mechanism the information-block would have cost **17 minutes**, so the 10-hour loss is fully explained mechanically; (2) named the underlying disposition — *the lead applies rigorous verification to WORK PRODUCTS but exempts its own PREMISES ABOUT THE ENVIRONMENT*; (3) rules R1 (turn-end invariant: end only with work complete or a harness-registered wake source named explicitly), R2 (quiet-window dominance with stop-loss + a heartbeat that checks for an in-flight measurement before acting), R3 (premise labeling); (4) identified failure modes the lead's own rules missed, incl. that **more wakeups can contaminate a live measurement**. It recommended **no demotion**, explicitly arguing against its own promotion because it would operate the same harness with the same wake semantics | **strong — the best-supported Fable datum in this ledger.** Zero retrieval, pure judgment on an assembled question, 108 s, and it beat the lead on the lead's own failure. Distinguishes the task class **"adjudicate a pre-assembled question"** (Fable: strong) from **"gather then judge"** (untested) | `docs/council_log.md` §C-038 "Fable adjudication" and "Verdict and calibration" |
| L-040 | 2026-07-25/26 | C-038 | Lead adjudication + gates: severity re-pricing, restart-vs-resume ruling, gate-integrity refusals, predicate verification | lead-bench | `high` (**Ed-confirmed**, §2a) | severity adjudication + gate integrity | 5 catches, 2 of them refusals to weaken a gate | **5**: (1) detected its **own** suite verification was worthless because it piped output through `tail`, discarding the summary line and masking the real exit code behind tail's; (2) adjudicated Sol's blocker to L1 by **reading the primary source** rather than accepting the delivered severity, and recorded that FLOOR-LABEL-01 **modestly WIDENS L1's blast radius** (attribution-limited cells that previously refused, and were therefore sterile, now publish); (3) chose **full restart over resume** for window C because resuming would mint a second pre-calibration and `latest_calibration()` would select it, silently breaking the pre/post bracket; (4) **refused to raise `--max-failures`**, which would have "fixed" the failures by accepting corrupted members; (5) hand-verified that the refactored dominance predicate reproduces both prior inline gates for absolute and comparative **before either reviewer reported** | fixed constant. Catches (3) and (4) are the shape no delegated layer produces: **refusing a change that would make the run succeed** | `docs/council_log.md` §C-038 "Lead (Opus 5) bench catches" |
| L-041 | 2026-07-25/26 | C-038 (collection) | Live quiet-Mac collection of measurement windows B, C, D | lead-bench | `high` (**Ed-confirmed**, §2a) | live / hardware verification | **Window B**: 59/59 members, zero failures/waivers/missing; fresh NEG-8 dual-family drift bound minted in-window (gross single-member endpoint 0.750924420078 J; replicated-endpoint n=3 0.570267900616 J). **Whole-window verdict PENDING at time of writing — no result asserted.** **Window C**: two attempts, both failed on the clock slew, both preserved in custody quarantine (attempt 1 at ABBA member 7/40; attempt 2 at the dual-family bound mint, refusing `neg8-refcorpus-r11`). **Window D**: not started | n/a — this is the instrument layer, not a review layer; the catches it fed are L-038 and L-040 | fixed constant (global hard rule 1). Recorded here because **~10 hours of this window were lost to a lead process error** (L-042), not to hardware | `docs/council_log.md` §C-038 "Collection outcomes"; `runs_window_b_20260726*/campaign_log.jsonl`; `runs_window_b_20260726_bound/neg8-drift-bound.json` |
| L-042 | 2026-07-25/26 | C-038 | **Lead-side invocation and turn-management defects** (recorded as an allocation datum in the L-020 sense: the instrument was fine, the lead's operation of it was not) | lead-bench | `high` (**Ed-confirmed**, §2a) | delegation operation | 5 recorded errors; ~10 h of open quiet window lost | **n/a — these are errors, not catches.** (1) Launched the Sol diagnosis with `nohup … &`, **outside harness tracking**, then ended the turn "holding until the diagnosis lands" — no wake could fire; the Mac never slept (`pmset -g log`) and **~10 hours of quiet window were lost, enough for both remaining collection windows**. THE most expensive process error of the campaign. (2) Over-read run-book §1 to mean the lead must not launch measurement windows; corrected by Ed. (3) Asserted Ed's session model as fact against the TUI banner; `/model` resolved it (A-10) — the banner was wrong, but the lead's certainty was unwarranted. (4) Three failed `codex-run-v3` invocations from guessing at the interface instead of reading the error; actual cause: the literal in-prompt `WRITE_SCOPE:` line **must be valid JSON**. (5) Launched the FLOOR-LABEL-01 fix round **without a sandbox flag**, defaulting to a read-only workspace: `apply_patch` rejected, **no work done, wrapper still exited 0** — only the report envelope (`status: blocked, completion: none`) revealed it | **lead-side failure mode, not an instrument verdict.** Errors 1 and 5 are the expensive ones; error 5 plus the `tail` catch in L-040 are the two data points behind **A-14 (exit status is not evidence of work done)** | `docs/council_log.md` §C-038 "Lead errors (recorded plainly)"; §6 A-14 below |

**Row count: 42.** Fully evidenced (no `unknown` field): **24**. Rows
carrying at least one `unknown` field: **18** (L-001, L-002, L-003,
L-004, L-006, L-008, L-010, L-014, L-016, L-021, L-023, L-024, L-027,
L-031, L-033, L-034, L-036, L-039) — see §6 for what drives
them (mostly missing effort records, unattributed catches in index-row
entries, and the lead-instrument gap). One row (L-024) has an `unknown`
*instrument*, which makes it unusable for allocation until resolved.

---

## 4. Task-class → instrument findings so far

Confidence: **strong** = repeated across ≥3 sessions with attributed
catches; **provisional** = 1–2 sessions, or attributed but uncontrolled;
**untested** = assigned by doctrine or dictate with no attributed evidence
in this repo.

| Task class | Instrument currently assigned | Evidence | Confidence |
|---|---|---|---|
| Enforced-`WRITE_SCOPE` implementation | **Sol** (`high` default, `xhigh` for design-bearing rounds) | L-005, L-014, L-017, L-020, L-029; the enforcement machinery itself (exit-77 scope backstop, `NEEDS_SCOPE` early return, v3 manifests) exists only on the Sol path — `docs/council_log.md` §C-028 "Process artifacts adopted this arc" | **strong** |
| Independent adversarial audit | **Sol**, fresh read-only session per round | L-018, L-026, L-030, L-037; C-033 records real mechanisms in all four rounds, and C-038's single audit produced a first-ever executable demonstration of registered limitation L1 | **strong on yield, weak on severity** — auditor severity inflation is recorded as systematic, not incidental (`~/.claude/skills/adversarial-review/SKILL.md` §C-033). L-037 refines this: the *finding* was correct-as-found and the *pricing* was still the lead's, against the primary source |
| Contract-lens refutation / whole-path contract review | **Opus 5** | L-031, L-036 | **provisional, strengthened** — two arcs, both decisive, still **never run against a control** (see §5 Q1). In both, the Opus lens found defects of *attribution and contract semantics* that a validate-or-not probe cannot reach |
| Non-local root-cause diagnosis of a live failure | **Sol** `xhigh` | L-038 (clock-anchor slew; corrected the lead's hypothesis and preserved a disciplined UNKNOWN rather than over-attributing) | **provisional** — one strong datum, but note it also produced the session's *unique* value: an explicit refusal to name a cause the evidence could not support |
| Execution-lens refutation with runnable probes | **Sol** at `high` | L-032, plus the C-028 refuter distribution (~16 refuters: ~70% confirmed / ~15% narrowed / ~15% refuted, narrowings highest-value) | **strong** |
| Delta re-audit after every fix round | **Sol** | L-009 (DRA-001), L-012 (9 catches, 2 lead corrections), L-020 (8th datum), L-026, L-029, L-030; ten-plus "fix rounds introduce defects" data points across arcs | **strong** |
| Integration review over a merged tree | **Sol** (`high`/`xhigh`) | L-005 (38 pre-merge cross-stream failures), L-009 (XSI-1), L-022 (**0** catches) | **provisional** — yield is real but bursty; the zero-catch datum is tallied against the drop rule |
| Design consult (pre-decision) | historically **Sol** `xhigh`; per the 2026-07-26 dictate the default lieutenant is now **Opus 5**, with **Fable** on genuinely major calls | Sol side: L-010 (3 design wins over the lead), L-011 (5 amendments + 1 bug), L-028 (structural correction adopted). Opus 5 side: **no attributed design-consult catch in the repo record** | Sol: **strong**. Opus 5 as design consult: **untested**. Fable as design consult: **untested in-repo** (see A-9) |
| Evidence-bounded writing / bookkeeping finalization (dictated fills) | **Fable** historically; **Opus 5** per the cost order | L-021 (Fable: 5 anomalies, ~94k tokens), L-033 (Opus 5: 5 errors in the lead's dictation, ~115k), L-016 (Fable critic: 3 gaps); the C-028 close also records the Fable dictated-fills pattern catching lead miscounts | **provisional** for both; the two instruments have one comparable datum each and have never been run on the same artifact |
| Live / hardware verification | **lead-bench only** | L-006, L-023, L-035; global rule 1; `~/.claude/skills/codex-delegation/SKILL.md` §Delegate vs keep ("final verification, always") | **strong — and a fixed constant, not an allocation question** |
| Severity adjudication and split-verdict synthesis | **lead-bench** | L-027, L-034, L-040; the split-verdict rule ("synthesize from both evidence chains, never majority-vote") is doctrine from `~/.claude/skills/adversarial-review/SKILL.md` §C-028 | **strong** |
| **Adjudicating a PRE-ASSEMBLED question** (the facts are gathered; what is wanted is judgment) | **Fable** | L-039: 21k tokens, **zero tool uses**, 108 s, overturned the lead's own self-diagnosis of the lead's own failure, produced a better rule set than the lead had drafted, found failure modes the lead missed, and declined its own promotion | **provisional but strong for a single datum** — and it isolates the variable: with zero retrieval, the entire yield is judgment. Distinct from "gather then judge", which remains **untested** for Fable |
| Refusing to weaken a gate to make a run succeed | **lead-bench only** | L-040 catches (3) and (4): full restart over resume because resuming would mint a second pre-calibration that `latest_calibration()` would silently select; refusal to raise `--max-failures` when that would have "fixed" failures by accepting corrupted members | **strong — and structurally undelegatable.** A delegated layer asked to make a run succeed has no standing to decide the run should not |
| Merge decision | **lead** under D-072 (full gate shape), with Ed naming the merge when the harness declines agent self-merge | `docs/process_traces/RESUME-2026-07-26.md` §6 (D-072); C-032/bridge (Ed named PR #65 after the harness declined); C-036 (3 self-merges under Ed's in-session delegation) | **strong** |
| Multi-stream orchestration by subagent directors | **retired** — lead-driven pipelines are the default | C-010 ("lead-driven pipelines validated, zero stalls, no subagent directors"); C-006 interventions I-1/I-2 | **strong (negative result)** |
| Redundant same-lens refutation by Opus | **retired at C-006, re-scoped at C-033** | L-001 (0 unique catches) vs L-031; the C-033 amendment states plainly that C-006 measured Opus as a *redundant* lens, not a *distinct* one | **provisional** — the reconciliation is an argument, not a measurement |
| Visual / image analysis | **Sol (Codex)** by Ed's standing doctrine (C-012, 2026-07-08) | `~/.claude/skills/codex-delegation/SKILL.md` §Specialties "Visual/image analysis is a Codex specialty" | **untested in this ledger** — doctrine recorded, no attributed catch ledger |
| Failed-test triage | **Sol first**, escalate to apex only after two Sol failures (Ed, 2026-07-07) | `~/.claude/skills/codex-delegation/SKILL.md` §Test doctrine item 0 | **untested in this ledger** — no session records a triage escalation count |
| Adversarial / security-shaped work | **Sol**, with mechanism-neutral brief phrasing | `~/.claude/skills/codex-delegation/SKILL.md` §Security; L-026 (3/8 refuters killed mid-run by a content filter, all recovered by data-quality rephrasing) | **strong for the routing, strong for the phrasing rule** |

---

## 5. Open questions for adjudication

Each is phrased so a future session can design a test.

**Q1 — Does the Opus-contract + Sol-execution pairing actually outperform
2× Sol at equal cost?** C-033 was a **single-arm** result: the pairing ran,
it changed triage in every round, and it was promoted to default. No
control arm was run — nobody gave the same review packet to two Sol
refuters with distinct lenses and compared.

**Update, C-038 (2026-07-25/26): a second informal trial, still no
control.** Over the FLOOR-LABEL-01 head the two lenses again found
things the other structurally could not: the Opus contract lens (L-036)
traced the *whole labelled path* and found a cross-cell **attribution**
defect mirrored bug-for-bug into the validator — invisible to a probe
that only asks "does this validate?" — while Sol (L-037) produced a
**runnable artifact-substitution probe** with concrete gate numbers
(`floor_gate` 5e-324 J vs 2.6484 J), invisible to a reader tracing
intended semantics. Two trials, two complementary yields, **zero
control arms**. Under the project's own "≥2 trials before roster change"
protocol the trial *count* is now met and the *design* still is not
(see A-8). The relevant comparison is
also not free: Ed's cost order puts Opus 5 at roughly half Fable and Sol
at ~free, so 2× Sol is strictly cheaper and the pairing must beat it, not
merely work. *Test:* the sealed same-packet A/B protocol already defined
at C-019 (`docs/council_log.md` l.1174-1176, "≥2 trials before roster
change") applied to a blocker set — classify each arm's findings as
unique / overlap / false-positive with fix cost.

**Q2 — Is `xhigh` justified over `high` for audits?** C-033 ran rounds
1–3 at `xhigh` and round 4 at `high`; round 4 still found real residue,
but by then the diff had been through three fix rounds, so the comparison
is confounded by convergence. Separately, C-036's four `high` audits
produced 8+ catches including a CI-red blocker. *Test:* two fresh
sessions, same packet, `high` vs `xhigh`, same rubric; count sustained
findings after refutation, not raw findings.

**Q3 — Is Fable's scarcity premium repaid on non-decision work?** The two
comparable rows are L-021 (Fable, ~94k tokens, 5 anomalies, zero rework)
and L-033 (Opus 5, ~115k tokens, 5 material errors in the lead's own
dictation). Similar shape, similar yield, roughly 2× cost difference by
Ed's order. Nothing in the record shows Fable outperforming Opus 5 on
evidence-bounded writing. *Test:* run both on the same bookkeeping
artifact, blind-score the returned fills against primary evidence, count
anomalies each catches that the other misses.

**Q4 — What did the ULTRA comparison audit actually show?** L-015 records
an intended, pre-declared ultra audit and its findings, but no comparison
verdict. Rule 10 restricts `ultra` to sessions that must spawn subagents;
if the C-034 comparison produced evidence either way it was not written
down. *Test:* recover it from the C-034 run report, or treat the question
as open and re-run under the rule-10 constraint.

**Q5 — Which layer should own severity pricing?** C-033 shows the auditor
tier systematically inflates severity while its mechanisms are real, and
the refuter tier is what converts that into correct triage. It is not
established whether a cheaper fix (a severity rubric in the audit prompt,
say) captures most of that value. *Test:* run one arc with a
rubric-hardened audit prompt and measure the sustained-at-tier rate
against C-033's 3–4 of 7 baseline.

*(A sixth question — "which model is actually the lead?" — was open when
this file was drafted and is now answered for 2026-07-26 and procedurally
fixed for future sessions: see §2a and anomaly A-10. Historical
`lead-bench` rows stay flagged as unverified attribution.)*

### Fixed constant — not an open question

**The lead's own final-verification layer has never been ablated, and
must not be.** It is global hard rule 1: "the lead never delegates final
verification — sub-agent or Codex 'tests green' is necessary, never
sufficient; every hardware/integration bug to date was caught only by
lead-side live verification." The record is consistent with it (L-006:
three lead-live-only catches no static layer could produce; L-023: a
delegated `supported` verdict accepted only after a lead field-name
check; L-035: a live suite failure at the first gated head). Do not
design a test that removes this layer. Record its catches so the
*constant* is instrumented; never so the constant can be questioned.

---

## 6. Anomalies and evidence gaps

**A-1 — Council IDs C-031, C-032 and C-033 are each used twice, for
different sessions.** `docs/council_log.md` carries C-031 = "Bridge v1"
(2026-07-13, l.1503) *and* C-031 = "D-078 P0 instrument-repair close-out"
(2026-07-22, l.65 and l.1663); C-032 = "Bridge v1.1" (2026-07-13, l.1504)
*and* C-032 = "NEG-8 estimand debate" (2026-07-24, l.66 and l.1707);
C-033 = "AXI intake council" (2026-07-14, l.1507) *and* C-033 = "NEG-8
screen+budget audit gauntlet" (2026-07-24/25, l.1725). The top index
(l.36-66) and the second index block (l.1498-1509) therefore hold
contradictory rows for the same IDs. This ledger cites collided IDs with a
disambiguating parenthetical. Next free ID is **C-038**.

**A-2 — The council log has two index blocks and non-monotonic ordering.**
The main `## Index` ends at C-032/2026-07-24; a second block headed
`## Index row` (l.1498) carries C-028 through C-037, with C-035 listed
before C-034 and C-037 before C-036. Nothing is lost, but no reader can
enumerate the entries from one place.

**A-3 — C-028's two spend snapshots disagree.** The "Rough spend"
paragraph (l.1610-1618) gives 53 recorded xhigh invocations, "local 24h
accounting shows 50 xhigh sessions ≈ 171M tokens", 2 ultra ≈ 100M, 2 high
≈ 40M. The "Spend snapshot addendum" (l.1620-1632) gives 59 Sol sessions /
330.6M total — xhigh 55 ≈ 190.4M, ultra 2 ≈ 100.3M, high 2 ≈ 40.0M. Both
are self-labelled estimates taken at different times; L-005 records the
arc-close figures and flags the disagreement rather than averaging.

**A-4 — C-037's "8-agent ultracode extraction" does not name an
instrument.** `docs/council_log.md` l.1508. The ultracode workflow shape
used `agentType: 'codex'` agents at C-025, but nothing in the C-037 record
states that, so L-024 carries `unknown` and is unusable for allocation
until someone resolves it from the 2026-07-17 run reports.

**A-5 — The C-033 Opus refuters' effort tier is unrecorded.** The entry
gives token sizes (~96k / 120k / 144k) but no effort. The session's effort
*ruling* — "`high` is the default refuter tier" — is explicitly about the
*Sol execution* refuters (l.1845-1855). Do not read the ruling as evidence
about what effort the Opus contract lens ran at.

**A-6 — C-029's invocation count is inconsistent between sources.** The
index row (l.1501) says "unintended ULTRA effort on all 13 invocations";
the run report's calibration table lists 10 rows. The likely reconciliation
is that the table omits retries and resumes, but neither source says so.
L-007 records both numbers.

**A-7 — Refuter effort doctrine is stated three different ways across live
sources.** Global `CLAUDE.md` rule 9 says "Sol xhigh refuters by default";
`~/.claude/skills/adversarial-review/SKILL.md` §C-033 rules that `high` is
the default *in the paired-lens shape*, reserving `xhigh` for
single-refuter verification; the same skill's §Shape step 2 and its
frontmatter still say "fresh read-only **Codex 5.5** instances" while the
model has been gpt-5.6-sol since 2026-07-09. The rules are reconcilable in
principle (different shapes, stale model string) but a fresh session
reading them in a different order will pick a different default.

**A-8 — The pairing was promoted to default without the sealed A/B that
doctrine requires.** `~/.claude/skills/codex-delegation/SKILL.md`
§Model-version scoping and the C-028 calibration note (l.1657-1661) both
say a pre-registered sealed A/B is the gate before any
delegation-boundary change; C-019 even defines the protocol ("≥2 trials
before roster change"). C-033 changed the default refuter roster on one
unsealed session. The memory file
`codex-delegation-growth.md` still records "sealed A/B pending before
doctrine promotion". The promotion may well be right — this ledger notes
only that it is not the evidence standard the project wrote for itself.
See §5 Q1.

**A-8 update (2026-07-26): now at two informal trials, still unsealed.**
C-038 ran the pairing a second time (L-036 Opus contract lens + L-037
Sol execution audit on the FLOOR-LABEL-01 head) and each lens again
caught what the other structurally could not. That satisfies the
*count* in C-019's "≥2 trials before roster change" but not its
*design*: **there is still no pre-registered sealed A/B**, no control
arm, and no blind scoring of unique / overlap / false-positive findings.
By the project's own protocol the pairing therefore **remains
unpromoted** — it is the working default on argument and accumulating
informal evidence, not on the evidence standard the project wrote for
itself. Do not record it as doctrine-promoted until the sealed A/B in
§5 Q1 has actually been run.

**A-9 — `docs/process_traces/RESUME-2026-07-26.md` §7 records a
superseded instruction, and two Fable claims the repo does not
corroborate.** §7 states Ed's 2026-07-25 standing instruction to consult
Fable "on any major problem or decision… not only as a final check" — the
2026-07-26 dictate in §2 above supersedes that. §7 also credits Fable with
two decisive contributions ("it killed the persisted-artifact design, and
it found the duration-independence lever"). Neither is corroborated
anywhere else in the repo: there is no run report after
`2026-07-24-screen-budget-gauntlet.md`, no council entry for the
2026-07-25 sessions, and a repository-wide search for
"duration-independence" returns nothing outside that sentence. The claims
are recorded here as **uncorroborated**, not as false; the missing
artifact is the 2026-07-25 run report.

**A-10 — RESOLVED (2026-07-26): the TUI startup banner misreported the
session model; the lead is Opus 5 (1M context).** Three sources disagreed
during this session:

1. `~/.claude/settings.json` on disk: `"model": "opus[1m]"`,
   `"effortLevel": "high"`.
2. The lead's own system prompt: "powered by the model named Opus 5
   (1M context)", model ID `claude-opus-5[1m]`.
3. The Claude Code TUI startup banner, in a screenshot Ed provided:
   "Fable 5 with high effort · Claude Max", alongside the upsell "Tackle
   your toughest work with Opus 5. Switch anytime with /model".

Ed then ran the interactive `/model` command: **"Kept model as Opus 5
(1M context)"**. Sources 1 and 2 were correct; **the banner was wrong**,
and so was its upsell.

Standing caution:

- **The TUI startup banner is NOT a reliable indicator of the session
  model** — it has been observed displaying a different model family than
  the one actually running.
- **The authoritative source is the interactive `/model` command, which
  only Ed can run.**
- `~/.claude/settings.json` and the lead's system prompt both agreed with
  `/model` here, so they are reasonable **secondary** evidence — but the
  lead should still have Ed confirm rather than asserting its own
  identity.

Cost of getting this wrong, already paid once this session: Ed read the
banner and concluded the lead was Fable; the lead then over-corrected and
told Ed it could not determine its own identity, when two of three sources
were in fact correct. Neither the assertion nor the retreat was warranted.

**Consequence for this ledger:** `lead-bench` rows from **this session
(2026-07-26) are attributable to Opus 5 (1M, `high`) with confidence**.
`lead-bench` rows from **earlier sessions (L-006, L-008, L-023, L-027,
L-034, L-035) remain unverified attribution** — the lead instrument was
not captured at the time — and stay flagged as such. Do not back-fill them
by inference. Going forward the §2a header row carries the answer.

**A-11 — Sol spend telemetry is unreliable.** `codex-usage` read all zeros
across both the 5h and 24h windows on a ~15-invocation day
(`docs/run_reports/2026-07-24-screen-budget-gauntlet.md` §Environmental
notes; `~/.claude/skills/codex-delegation/SKILL.md` C-033 field notes).
The wrapper→ledger feed is suspected broken; Ed was notified 2026-07-24.
Treat a silent ledger as **unknown quota, never as headroom**, and expect
no spend figures for arcs after 2026-07-24 until it is fixed.

**A-12 — Anthropic-side usage is not programmatically visible.** Fable and
Opus 5 limits cannot be polled by the lead (`/usage` is user-TUI only);
Ed flags pressure when he sees it
(`instrument-mix-authority.md` §Polling). Cost-side reasoning about the
Claude instruments therefore rests on Ed's stated hierarchy plus the one
measured C-028 snapshot, not on live accounting.

**A-13 — Catch attribution is prose-only in index-row entries.** Pointer
entries (C-029, C-030, C-034, C-035, C-036, C-037) compress a whole arc
into one cell; per-instrument catches survive only where the run report
carries a `Delegation calibration (schema v2)` table. Those tables exist
for 2026-07-08 (×2), 2026-07-09 (×3), 2026-07-12, 2026-07-13 (×2) and
2026-07-16 — and are the single most useful source for this ledger.
Sessions that skip the table cannot be back-filled without re-reading
transcripts that are deliberately not kept.

**A-14 — EXIT STATUS IS NOT EVIDENCE OF WORK DONE.** Twice in the single
session C-038 (2026-07-25/26) an exit code masked a non-result:

1. The lead launched the FLOOR-LABEL-01 fix round via `codex-run-v3`
   **without a sandbox flag**, so it defaulted to a **read-only
   workspace**. `apply_patch` was rejected and the session **did no
   work whatsoever**. The wrapper nevertheless **exited 0**. Only the
   governed report envelope — `status: blocked, completion: none` —
   revealed it.
2. The lead verified its own test suite by piping the run through
   `tail`, which **discarded the summary line** and returned **tail's**
   exit status rather than the suite's. The verification was worthless
   and looked green.

Both are lead-side operation defects (L-042, L-040), not instrument
defects, and both would have been caught by the same rule:

> **The evidence of work done is the governed report envelope
> (`status` / `completion`) for a delegated run, and the suite's own
> summary line for a local run. Never a shell exit code. Never a
> truncated stream.**

This bears directly on how delegated work must be verified, which is
why it lives here and not only in the council entry: a ledger row
recording "Outcome: clean, rc=0" is **not** evidence that an
instrument did anything. Every future row's `Outcome` field must trace
to an envelope or a summary line, per the §Anti-fabrication rule. The
generalization is recorded in `docs/council_log.md` §C-038
("Generalization adopted this session").
