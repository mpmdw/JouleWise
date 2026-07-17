# Run report — Resumption readiness + no-hardware batch (2026-07-16)

Ed (three directives, in order): (1) "pull from remote... check the status of
the project and see if we're ready for resumption... have sol high do some
audits in a workflow... peep the axi-handoff doc"; (2) "assess the current
task queue and most recent commits... I want the rest of the things I can do
without hardware to start getting worked on/finished as I've got the hardware
now at least the mac"; (3) "handle the merge yourself if all is well — just
get the project ready for my quiet mac. Just be sure for any contentious
decisions to record it appropriately."

## Deliverable check (WO-022 §5a discipline)

Primary deliverable: a verified readiness assessment PLUS the unblocked
no-hardware backlog worked to completion. SHIPPED: readiness audits ran and
their blockers were closed the same session; PR #67 merged (AXI-SA); SPLIT-AP
(PR #69) and SITE-02 (PR #68) landed; AXI-SB implemented, live-probed
`supported`, Mac C5-2.2 leg mint STAGED on `impl/axi-sb` (effective on that
PR's merge; PR pending at report time); AXI-SD
evidence memo captured for Ed's D-016 decision. NOT shipped (correctly): the
D-016 decision itself and the G10 memory-rule ratification (Ed-owned, D-070);
Window A execution (quiet-Mac lane, Ed-owned).

## Merge authority (recorded per Ed's "record it appropriately")

Ed, in-session 2026-07-16: "handle the merge yourself if all is well." All
three merges this session (PRs #67, #68, #69) are self-merges under that
delegation, each with the full D-031-amended gate shape (oversight reviews →
lead triage → fixes → CI green on final head → fresh pass over any
post-review commit). This is a session-scoped exercise of the standing
merge-authority-with-review rule, not a new standing authority.

## Session arc 1 — readiness audits (ultracode workflow, Sol high ×4 + refuters)

Workflow `axi-resumption-readiness-audit` (9 agents, ~475k subagent tokens):

- **State coherence: NOT_READY (confirmed, refuters upheld with one severity
  downgrade).** RUN_STATE header two eras stale; kernel still rendered AXI-SA
  as the READY head though PR #67 was open; kernel `latest_report` pointed at
  the 2026-07-13 bridge report. ALL CLOSED this session (`36b4da1`,
  `dbd8137`).
- **PR #67 merge-readiness: NOT_READY — CI red.** One CI-only failure:
  `test_legacy_golden_provenance_replays_pristine_base_head` runs
  `git archive 9ee8710…` (pinned base) which a shallow `actions/checkout`
  cannot serve; the lead-run 1626 OK was honest but not portable. Bench fix
  `0914374` (fetch-depth: 0, test jobs only; pushed after Ed granted the gh
  `workflow` scope), fresh final-head review CLEAN, CI green 5/5, merged as
  `7593259`.
- **Advisor-question map: READY_WITH_CAVEATS.** Handoff §5 items 1/2/4/5/6
  ANSWERED (D-066..D-070, D-067, D-068); item 3 (D-016 pair) open with
  Ed/advisor. One recorded past deviation: commit `f682af9` (2026-07-15)
  regenerated 14 site HTML files after D-068 was recorded — noted here
  honestly; no agent deploy occurred; content stands, convention now enforced.
- **Resumption blockers: READY_WITH_CAVEATS.** Agent lane blocked only by
  PR #67 (now merged). Window A software-unblocked and strictly ordered:
  P2-038 live closure (Ed + `/usr/bin/powermetrics`) → P2-015-SMOKE → P2-015
  floors → baselines. R-016 summary/body drift found → body addendum landed
  (`dbd8137`). All six ED-EXTERNAL rows ripe (P1-008 first; counters R-012).

## Session arc 2 — no-hardware backlog

- **SPLIT-AP (rank 9) LANDED, PR #69 `9db4546`.** Adjudicated Part I freeze,
  D-067-reconciled. Review arc: xhigh impl → xhigh contract counterreview
  (4 SF + 1 nit, all accepted) → fix → **delta re-audit caught a blocker the
  LEAD's own FIX-1 pin introduced** (predictor dropped serialize/deserialize —
  eighth "fix rounds introduce defects" datum, first lead-authored one) →
  micro-round → focused delta (stage-term source unpinned) → lead bench fix →
  fresh micro-review → closed. Named open gates: OPEN-GATE-SPLITAP-PACK-LINT,
  OPEN-SPLIT-PRED-FIXED-COMPOSITION (composition rule + stage-term source).
- **SITE-02 (rank 20) LANDED, PR #68 `2778ed2`.** D1: loud structured
  discovery (env + OS-path, exact-version refusal, wrong-before-correct PATH
  ordering); D2: the node regression now executes the real emitted `pages.ts`
  via pinned esbuild (the old hand-rewritten JS mirror — exactly what D2
  forbade — is gone). D2 guaranteed in CI (release-chain focused step,
  verified EXECUTED in the CI job log, not merely green).
- **AXI-SB (rank 4, unblocked by #67) verdict: `supported`.** Sol xhigh spike
  found the genuine batched path (`BatchGenerator.next()`, per-UID response
  hooks) in pinned mlx-lm 0.31.3; lead-run live probes on Metal at B=2/B=4:
  configured == realized batch dims on every model call, one insertion, B
  distinct request_ids with token IDs + SHA-256, counts, stop reasons,
  per-token timestamps, all phase hooks. Verdict flipped per the doc's
  closeout procedure; evidence + hashes in
  `docs/process_traces/2026-07-16-axi-sb-live-probes/` (branch); Mac C5-2.2
  leg mint STAGED in the bank row on `impl/axi-sb` — none of this is on main
  until the SB PR merges. Anti-gaming lens + PR pending at report time;
  kernel completion + follow-on adapter row mint ride the SB merge.
- **AXI-SD (rank 6) evidence memo** (Fable web-verification subagent, all
  facts cited to primary sources):
  `docs/process_traces/2026-07-16-axi-sd-web-verification/memo.md`. Headline:
  the OLMo pair (`allenai/OLMo-1B-0724-hf` vs `allenai/OLMoE-1B-7B-0924`) is
  an essentially exact active-param match (d_active 0.0016) and fits the
  8 GiB rule at 4-bit (≈0.95/3.9 GiB) — a D-016-compatible pair may survive,
  which reframes the §7 decision box; main risk is the dense arm's UNVERIFIED
  MLX loadability (gen-1 OLMo format) and base-base-only variants. Qwen3
  pair confirmed-FAILS G10 for cross-target (17.17 GB real 4-bit artifact);
  Qwen1.5 pair fails active-match (0.380) + license burden. §8 ladder viable
  on `Qwen/Qwen2.5-1.5B-Instruct` @ `989aa79…`. Scorecard fold-in is the next
  SD step; D-016 remains Ed's.
- **Integration review (3 streams merged): zero cross-stream defects**;
  merged-main suite 1630 OK (Sol-run, lead-corroborated by the 1626 OK
  pre-closure run + CI). Its one should-fix (kernel reconciliation) was the
  closure batch already held for tree quiescence.

## Verification evidence (lead-run)

- Canonical suite on main pre-merge: 1534 OK (skipped=12).
- Canonical suite on main post-#67: 1626 OK (skipped=14).
- Integration review on merged main (post #68/#69): 1630 OK.
- Kernel/oracle/freshness tests after each closure batch: green
  (46 tests, `test_gen_state` + `test_docs_freshness`).
- SITE-02 D2 gate: PASS locally AND verified executed in the release-chain CI
  log (`Ran 1 test ... OK`).
- AXI-SB live probes: two JSONL evidence files, SHA-256s recorded.

## Ed decision list (batched; nothing here is agent-decidable)

1. **Window A scheduling** — the quiet-Mac chain is fully software-unblocked:
   P2-038 live closure (needs you + sudo powermetrics) → P2-015-SMOKE →
   P2-015 floors → baselines. First action when the quiet window exists.
2. **D-016 pair + G10 memory-rule** — read the §7 decision box
   (`docs/specs/axi/sd_model_pair_scorecard.md`) with the new memo: the OLMo
   pair may make Option A's premise moot IF its MLX loadability verifies;
   memory-rule subdecision (`axi-sd-memory-fit-shape-v1`) still needed before
   G10 scoring.
3. **ED-EXTERNAL heads** — P1-008 (calendar/acceptance bar; counters R-012,
   the top management risk) and P2-027 (external re-reduction) are ripe.
4. **Lease adjudication batch** — the retained ATTRIBUTION_INDETERMINATE
   lease closes from the spec phase (+ the TOOL-01 session-open artifact)
   still await your batch approval.
5. **Stale worktree pile** — ~30 pre-audit worktrees under
   `/Users/edr/code/JouleWise-wt/` (audit-s*, p20xx, …); next session should
   verify clean/pushed and prune. Not touched this session.

## Restart instructions

Kernel lane heads are authoritative (post-SB-merge: AXI-SC and AXI-SD lead the
agent lane; AXI-SE stays blocked on P2-015 floors). The SB merge commit
completes AXI-SB in the kernel and mints the follow-on batch-adapter row.
DRIFT.md refreshed this session; site deploy remains Ed-manual (D-068).

## Process Trace Appendix

**Shape.** Assessment workflow (4 Sol-high audits + severity-tiered refuters)
ran BEFORE work selection; then four streams: SPLIT-AP (xhigh, contract tier),
SITE-02 (high, standard tier), AXI-SB (xhigh spike, contract-adjacent), AXI-SD
(Fable web verification, dictated-evidence tier). Disjoint footprints held;
worktree per stream; lead-driven pipelines, zero orchestrators, zero stalls.

**Catches (unique, by layer).**
- Workflow audits: CI-red on PR #67 (would have blocked Ed's merge); kernel
  READY-head drift; R-016 drift; DRIFT/latest_report pointers.
- Refuters: severity downgrade on the RUN_STATE blocker (intake path
  mitigates); factual corrections (RUN_STATE line numbers).
- Counterreview lenses: SPLIT-AP D-067 recording-vs-reporting distinction
  (F2) + prediction double-count (F1); SITE-02 esbuild bare-CI blocker (both
  lenses convergent).
- Delta re-audits: SPLIT-AP predictor component loss (LEAD-pinned defect);
  SITE-02 D2-not-guaranteed-in-CI.
- Lead gate: release-chain 11s pass → CI job-log verification that the D2
  step actually executed; AXI-SB terminal-UID field-name check before
  accepting `supported`; SPLIT-AP stage-term bench fix.

**Interventions.** codex-run-v3 rc=64 launch failure (strict-scope out-file
must live OUTSIDE the worktree — new datum for codex-delegation field notes);
gh push rejected on workflow-scope (Ed refreshed token in-session); Monitor
sleep-chain block → switched to until-loop watchers.

**Delegation calibration (schema v2).**

| id | to | unit | altitude | outcome | catches | lead-rework |
|---|---|---|---|---|---|---|
| audits ×4 | Sol high (wf) | readiness audits | judgment-call | clean (1 severity overstated) | 8+ | none |
| refuters ×5 | Sol high (wf) | blocker refutation | pinned-spec | clean | 2 narrowings | none |
| splitap-impl | Sol xhigh | Part I freeze | pinned-spec | findings-clean | — | none |
| splitap-fix1 | Sol xhigh | FIX-1..5 | pinned-spec | **introduced R1 (lead prompt-defect)** | — | bench fix |
| site02-impl | Sol high | D1/D2 | design-freedom | clean | — | none |
| site02 rounds ×4 | Sol high | lenses/fix/delta/micro | pinned-spec | clean | 4 | none |
| axi-sa-finalhead | Sol high | ci.yml review | pinned-spec | CLEAN | 0 | none |
| integration | Sol high | merged-main review | judgment-call | clean | 1 (known) | none |
| axi-sb-impl | Sol xhigh | spike+harness+doc | design-freedom | clean | — | none (probes were lead work by design) |
| sd-web-verify | Fable subagent | model-pair evidence | dictated-fills | clean, 5 anomalies vs scorecard recalls | 5 | none |

**Yield + spend (estimated).** ~26 Sol sessions (9 workflow agents ≈ 475k
subagent tokens + ~17 codex-run sessions) + 1 Fable web agent (94k). Every
fix round that ran got a delta re-audit; the doctrine paid for itself once
(R1) and the final-head rule once (CI-log D2 verification was lead-gate, but
MR1 came from the bench-edit fresh pass).

## Addendum (same session): AXI-SB LANDED — PR #70 merged

The anti-gaming lens verified the live evidence genuine and found a
harness trust-chain blocker (controller trusted the child's verdict);
fix round → delta re-audit caught TWO new bypasses in the fix itself
(derivation unanchored to requested B; terminal runtime UIDs unchecked
— NINTH fix-rounds-introduce-defects datum) → closed-set micro-round →
lead termination: post-hardening live re-probe derived `supported` at
stage `controller_evidence_validation` on real Metal; worktree suite
green; CI green 5/5; merged (self-merge per Ed's delegation). Kernel:
AXI-SB completed; AXI-SB-ADAPTER minted at agent rank 4 (batch_size
knob + per-sequence AXI-SA events; authority = the verdict doc). The
"staged" Mac C5-2.2 leg mint wording earlier in this report is now
effective on main. Agent-lane heads after this session: AXI-SB-ADAPTER
(4), AXI-SC (5), AXI-SD (6).
