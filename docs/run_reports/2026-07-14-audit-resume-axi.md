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
| WO-031 docs freshness | impl/audit-integration | high impl | (fill at close) | (fill at close) |
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

## Remaining at draft time

Integration review (fresh Sol xhigh) over the final tree; Sol ULTRA
comparison audit; adoption commit with PA-2's 17 supersession lines;
report §7/§8 synthesis + completeness critic + bounded closure loop;
deferred-roadmap queue promotion; council row (C-034 expected);
RUN_STATE refresh; DRIFT.md refresh (NO deploy, D-068); PR(s) + merge
gates (Ed names merges); then the AXI arc (Sol xhigh consult on the
handoff → S-0 → S-A → S-B/C/D/E rows).
