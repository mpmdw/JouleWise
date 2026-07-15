# Run report — Audit fix-wave resume + AXI intake (2026-07-14/15)

Lead: Claude Fable (background session). Ed live for parts (batched §5
answers, WO-010 lease adjudication). Volume model: gpt-5.6-sol via the
audited CLI bridge (`scripts/codex-bridge` + direct `codex exec` for
read-only checkers; MCP server unavailable in this headless harness —
CLAUDE.md fallback route). DRAFT until the close-out section is filled.

## Arc summary

Two directives executed in sequence per `docs/axi-handoff.md` (Ed,
2026-07-14, committed as provenance):

1. **AXI intake** (permitted under the audit gate as decision-log work):
   Ed's batched §5 questions asked FIRST per the handoff; answers
   recorded; D-066..D-070 drafted, C-033 Sol coherence council (6
   corrections, all accepted), committed `5fcd1cd` + pushed.
2. **Audit fix-wave resumed and completed** (this report's §Work
   orders): S1 closed (WO-010, WO-011), S4 closed (WO-019, WO-031),
   WO-027, WO-021, WO-022 landed; integration tree built; one
   integration-unique catch fixed.

## Ed's §5 answers (recorded 2026-07-14, this session)

- **Claim commitments:** ALL five architectural axes get quiet-Mac
  characterization commitment (Ed's hardware; maximize flexibility).
  Supersedes the handoff's narrower default. (D-070.)
- **Continuous batching:** static-only for the capstone; deferred
  post-capstone NV-gated, not killed; BINDING continuous-ready schema
  constraint — request-scoped events, `metadata.request_id`,
  per-request lifecycle envelope; reducer may exploit static
  synchronization, schema must not require it. (D-070 clause 3.)
- **Idle D-entry wording:** approved with four amendments
  (reporting-not-recording; Rivoire attribution accuracy; P1-003/Q6
  revisit trigger; Lakebed/status wording fix named as consequence) —
  all incorporated in D-067.
- **Sequencing:** default confirmed — audit first, S-0 immediately
  after clearance, close-out ends with DRIFT.md refresh, never a
  deploy (D-068).

## Work orders landed (implement → fresh checker → fix → lead gate)

| WO | Branch | Sol sessions | Checker verdict arc | Lead gate |
|---|---|---|---|---|
| WO-010 remote protocol hardening | impl/audit-s1 `413e030` | high impl + NEEDS_SCOPE resume | PASS 0 findings | focused 86 OK replay; close-time SCOPE_VIOLATION adjudicated (lead commit-before-close; Ed-approved abandon) |
| WO-011 token evidence policy | impl/audit-s1 `f664d69` (S1 COMPLETE, 12 orders) | high impl + fix round | FAIL (item_type-label bypass, major) → fix keyed to runtime predicate → delta PASS 0 | focused 135 OK replay; SCOPE_OK close pre-commit |
| WO-019 release chain | impl/audit-s4 `7b1299c` | high impl | PASS 0 findings | release_check dry-run replay PASS; SCOPE_OK |
| WO-027 codex-watch disposition | impl/audit-wo027 `3e0e928` | lead bench + checker | FAIL (2 confirmed: live-discovery gap, session_meta fallback; 1 refuted: checker-sandbox env) → fix round | bridge tests 62 OK pre+post |
| WO-021 state-kernel v3 (R1 choice A) | impl/audit-wo021 `c7ee7ca` | xhigh impl, 3 rounds + 8a cross-check + xhigh checker + xhigh delta | BLOCKER (phase-C deleted 4 unmigrated records) → migration + exact 30-ID parity test → delta major REFUTED (one-head-per-lane by design) + accepted residue (projection pinning test) | fidelity 38 OK + gen_state --check + canonical 1400 OK; SCOPE_OK close pre-commit |
| WO-022 spend guardrails (R2) | main `3e9f76b` | lead bench (verbatim paste) | register verification script PASS | exact-substring + receipt assertions |
| WO-031 docs freshness | impl/audit-integration `0de4cea` | high impl + fix round | FAIL 3 majors (mutation probes: uncovered current regions, deploy-only phrasing escape, stale Window-A fact) → all probes rejected post-fix | freshness 5 OK replay; owner-deferred phrasing verified; SCOPE_OK close pre-commit |
| int-budget-fix | impl/audit-integration `e491656` | high impl | lead-gated (bounded) | budget suite replay OK; SCOPE_OK |

Integration-layer unique catch: capsule budget breach (963,360 >
943,718) from stream-union doc growth — every branch green alone.
Fixed by omitting the duplicative generated task-queue payload
(Roadmap aliases preserved); 879,212 bytes, 64.5KB headroom.

## Checker/court yield this session (unique catches)

1. C-033: 6 coherence corrections on D-066..D-070 (incl. D-058 Primary
   Metric supersession that keeps S-0 docs-only, C-012→C-013
   misattribution, `request_id` schema pinning).
2. WO-011 checker: schema-valid `ids_prompt`+`prompt_text` bypass of
   the token-evidence requirement (major; real).
3. WO-021 xhigh checker: phase-C silent deletion of SITE-02, SPLIT-AP,
   P2-050, TOOL-01 (BLOCKER; 8th "fix/phase rounds introduce defects"
   datum) — root cause was PRE-EXISTING kernel↔queue divergence; the
   records were never migrated at DOC-008 time.
4. WO-027 checker: live-run discovery gap in the replacement recipe
   (status files only exist post-exit).
5. Integration suite: capsule budget breach (above).
6. Harness permission layer: refused the lead's self-approved
   WO-010 lease abandonment (independent approval required — Ed
   approved with reason; recorded under D-065).

## Process defects recorded (lead + tooling)

- Lead: WO-010 committed before `session-close` → close-time
  SCOPE_VIOLATION artifact (lesson standing: close precedes commit).
- Lead: WO-011 fix round dispatched via `codex-bridge resume --last`,
  which resolves to the GLOBAL most-recent Codex session — attached to
  the checker's thread (role violation risk). Killed after 1 read-only
  call (rollout-audited, zero writes); re-dispatched by explicit
  session id. TOOL-01 gained this defect + the session-open
  no-per-path-match-specifier gap.
- Lead: WO-021 delta-checker acceptance clause overreached the
  register (demanded all four tasks render in the head view); checker
  finding refuted, residue (projection pinning test) accepted.
- Lead: mistyped full BASE_HEAD in the WO-027 checker header (short
  sha was unambiguous).

## Spend (see WO-022 receipt for the running snapshot)

Snapshot at WO-022 landing: 10 Sol sessions ≈ 45.7M total tokens
(cached-dominated); one honest PRE-POLICY hard-band crossing recorded
(WO-010 impl, 21.8M vs the 12M high-session band). Fable spend
accounting_unknown (no local accounting in this harness). Final
refresh owed at close-out.

## ULTRA pre-run statement (WO-022 §4 requirement; recorded before launch)

Intended ultra session #1 of ≤2 this arc: the checkpoint-queued Sol
ULTRA comparison audit. Why xhigh is insufficient: the audit must
independently verify all ~34 landed work-order landings against their
full register rows (acceptance evidence, non-goals, riders, court
amendments) plus the five stream-close sweeps and the two integration
fixes — per-order verification over a 44-commit tree exceeds one
sequential xhigh context, and the comparisons are independent (no
shared state), which is precisely the subagent-parallel shape. Bounded
subagent work: one verification subagent per landed work order plus one
synthesis pass; no implementation authority (read-only sandbox pinned
at `978e4c6`).

## AXI xhigh consult (Ed-directed; ran at close, pre-clearance)

Sol xhigh consult on the AXI handoff completed read-only; full response
tracked at `docs/process_traces/2026-07-15-axi-xhigh-consult/response.md`.
Headline judgments (all adopted as S-0/S-A/S-E execution inputs): versioned
burst event semantics (never reinterpret existing token events; sibling
manifest version, AP-2 v1 byte-identical); frozen counter contract with
spec.mode discriminator (off/draft_model/native_mtp); matched GROSS
request energy + gross J per committed output token as the spec-on/off
estimand (J-per-accepted-token demoted to spec-only diagnostic);
request-aware reducer rules (union, don't sum, synchronized duplicate
phase windows — pre-empts a ~B-fold overcount; no per-request division of
overlapping traces without an attribution model); S-A/S-E cycle fix
(minimal AP-SPEC freeze moves into S-A's front); S-B structured verdict
(runtime batching without per-sequence observability =
unsupported_for_joulewise, no Mac registry leg); S-D pre-registered
selection scorecard + the D-016 8GB-fit trap (may need a separate AXI
pair — Ed question); AP ownership gaps for quant/variance/MOE-BATCH
(S-E adds AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH); n=5 provisional
pending P2-015 floors per D-062; the S-0 advisor basis paragraph drafted
(gross-headline with boundary labels).

## Close-out record (all complete, 2026-07-15)

Everything queued at draft time DONE on `impl/audit-integration`
(final head `f8f0f92`, canonical suite 1532 OK): integration review
(2 unique catches: capsule budget union breach → fixed `e491656`;
D-068 vacuous-green surfaces → fixed `f682af9`); ULTRA comparison
audit (12 faithful / 22 deviations / 6 deferred-confirmed; 2 blockers
fixed in `913a2a6` after an xhigh checker caught F2/F4 residue; full
triage report §8.5, response preserved in receipts/); D-043
supersession closure (`978e4c6`: 17 surface lines + 6 lead
decision-log amendments); report §7/§8/§9 synthesis; Fable
completeness critic (3 gaps, all closed in `f8f0f92`); queue promotion
(AUD-WO-033..039 + AUD-FOLLOWUPS gated kernel tasks; 46-ID oracle);
WO-022 receipt refreshed as the T09 audit-close anchor — ARC HARD
crossing (251M tokens / 28 Sol sessions) recorded honestly;
DRIFT.md created (no deploy); RUN_STATE header updated; C-034 council
row on main.

POST-MERGE ADDENDUM (2026-07-15): Ed merged PR #66 (`e377f93`); the
audit gate was CLEARED from the kernel same session (`08fa290`,
fidelity tests moved to fixture-driven gate semantics — clearance is
loud by design). AXI stream rows minted (AXI-S0..SE, consult
sequencing; `4683c89`). AXI-S0 LANDED (`e4ca294`): advisor docs carry
basis+boundary on every energy number, the attributed
energy-proportionality rationale, the harness/benchmark split, and the
five-axis Q4 agenda; DRIFT.md is current for Ed's one manual deploy.
AXI-SA (burst-decode contract) is the READY agent head for the next
session. Ed's codex-watch non-use confirmation recorded (report §8.5).
Formerly open at session close: (1) Ed's adoption merge of the
`impl/audit-integration` PR — the audit gate stays ACTIVE until then;
gate removal from the kernel is a one-line follow-up at/after merge.
(2) Ed's explicit codex-watch NON-USE confirmation (ULTRA F18; asked
in-session). (3) The AXI arc (tasks: Sol xhigh handoff consult → S-0 →
S-A → S-B/C/D/E queue rows) launches after clearance.

## AXI spec-design phase (2026-07-15, post-clearance; arc C-035)

Arc-open declaration (WO-022 §5a): predeclared deliverable = three
council-reviewed AXI spec documents (deliverable-facing: predeclared
contract/analysis artifacts the campaigns require). Delivered:

- `docs/specs/axi/sa_burst_decode_contract.md` (2,311 lines, `3b5c4bf`):
  xhigh author -> xhigh counterreview (2 blockers + 4 majors + 2
  moderates) -> fix round -> xhigh delta (1 new blocker: gameable
  attempt ledger) -> closed-set micro-round -> lead-terminated.
- `docs/specs/axi/sd_model_pair_scorecard.md` (`1464c93`): high author
  -> counterreview (1 blocker + 5 majors) -> fix -> delta (2 majors) ->
  micro-round -> lead-verified. Carries the four-option D-016 8GB-fit
  decision box for Ed.
- `docs/specs/axi/se_analysis_plans_draft.md` (`d2bd5ee`): xhigh author
  -> xhigh counterreview (6 HIGH + 3 MED) -> fix -> delta residue ->
  ESTIMAND DEMOTION ruling (AP-REASON-VARIANCE claims only the
  identifiable replay-conditional decomposition; natural-sampling
  variance descriptive L1) -> lead-terminated. 21 PROVISIONAL cells
  with named freeze triggers.

Every spec failed its first counterreview; 30+ substantive findings
were fixed pre-landing (notably: the counterreview refuted the SA
draft's byte-identical frozen-arm claim against actual reducer code —
restated honestly as current-behavior goldens; and the SE floor
transport's max() guard was proven non-conservative under aligned
errors — replaced with union bounds + Markov quantile guards).

Spend (estimated, rollout-derived): ~14 Sol sessions ≈ 71.2M total
tokens post-clearance (S-0 + row minting + three spec pipelines).
Within arc soft bands. Three benign ATTRIBUTION_INDETERMINATE lease
closes (lead commits moving HEAD under long parallel leases — same
adjudicated class; leases retained pending Ed batch approval; every
diff verified + landed).

NEXT HEAD: AXI-SA implementation (the spec is its authority; branch +
PR series per D-031 — gh is now authenticated). Then AXI-SB spike
against the landed contract.
