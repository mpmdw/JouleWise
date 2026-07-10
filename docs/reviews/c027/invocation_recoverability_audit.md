# Invocation recoverability audit — C-022 / C-024 / C-025 / C-026 (MET-001, MET-5)

Date: 2026-07-09. Scope: AUDIT TABLE ONLY (spec MET-5 steps 1-5 at block
granularity). The step-6 marking pass ("reported, independently
unverifiable" addenda on council-log gate claims) is deliberately NOT
executed here — it is deferred to the lead, per the C-027 spec's open
question 5 (the audit runs first and determines whether any markings are
needed at all). Based on the counts below, few or no markings appear
necessary.

## Method

- Claims enumerated from the four run reports (sources cited per row).
- Substrate: the codex-run observer index
  `~/.codex/claude-spawned/index.jsonl` (854 lines; 684 parsed with
  `encoding='utf-8', errors='replace'`; 170 non-JSON/blank lines
  skipped). Events on 2026-07-09: FINISHED rows filtered, grouped into
  session windows by timestamp + run_key naming that matches each run
  report's named streams/lenses/gates.
- "Artifacts survive" = the row's `out` and `log` file paths still
  exist on disk at audit time (checked per row).
- Labels (spec MET-5 step 4, applied per block): **recovered** =
  session ids AND surviving prompt/output artifacts cover the claimed
  count; **partially-recovered** = session ids XOR artifacts;
  **unrecoverable** = neither. Nothing is backfilled: no reconstructed
  session ids, hashes, or timestamps anywhere in this note.

## Summary table

| Session | Claimed invocations (source) | Window (UTC 2026-07-09) | Index FINISHED rows w/ session id | Rows w/ surviving out+log artifacts | Label |
|---|---|---|---|---|---|
| C-022 | ~35 codex sessions (run_reports/2026-07-09-cp5-resume.md:132) | 00:36-06:54 | 50 | 50 | **recovered** (50 rows ≥ ~35 claimed; run_keys match the report's named workstreams: envgate/hashcheck/strictfix/bundlepack, pr22-25 gates, advisor/capture/genwide fan-out, 2 integration reviews, sweep) |
| C-024 | ~20 codex sessions: 4 impl, 4 lenses, 6 fix rounds, 4 final-head, 1 tail verification, 1 integration review (run_reports/2026-07-09-spec-fleshing-wave1.md:88) | 07:29-08:16 | 19 | 19 | **recovered** (19 rows vs "~20" claimed — within the approximate claim; note: the literal sub-breakdown "4 final-head" maps to 3 FH-named rows in the index (FH-scope, FH-p2015, FH2-tails); every recovered row has both session id and artifacts) |
| C-025 (direct) | ~14 direct codex sessions (run_reports/2026-07-09-spec-fleshing-wave2.md:97) | 08:35-10:05 | 30 | 27 | **recovered** (30 rows ≥ ~14 claimed; 27 rows have full artifacts, 3 rows — run_keys `...-84081--C`, `...-85625--C`, `...-91286--C`, truncated names — have session ids but their out/log files no longer exist: those 3 are individually **partially-recovered**) |
| C-025 (workflow) | 46 workflow agents, ~1.87M tokens (run_reports/2026-07-09-spec-fleshing-wave2.md:49) | 08:35-10:05 | 0 attributable | 0 | **unrecoverable from this index** (the observer index records codex-run invocations only, not Workflow-tool subagents; no index rows are attributable to the 46 workflow agents; whether other substrate exists for them is not asserted here) |
| C-026 | ~5 codex sessions: design, implement, 2 lenses, fix, final-head (run_reports/2026-07-09-p2034-broad-packs.md:44) | 16:35-17:22 | 7 | 7 | **recovered** (7 rows ≥ ~5-6 claimed; one-to-one run_key match: P34-design, P34-impl, R34a-exec, R34b-compliance, F34-fixes, FH34, plus WRAP-meeting beyond the listed breakdown) |

Headline: 106 of the ~74-75 individually-claimed codex invocations'
FINISHED rows carry session ids in the index (over-coverage because run
reports rounded down and omitted auxiliary runs); 103 of 106 also have
surviving out+log artifacts; 3 are partially-recovered (session id
only); the one wholly unrecoverable-from-this-index block is C-025's 46
Workflow-tool subagents, which this substrate was never designed to
record.

## Appendix — per-window FINISHED run_keys (verbatim from the index)

Every row below has a session id; artifact survival noted only where it
fails.

### C-022 (50 rows, 00:36-06:54)

ra-project, ra-calibration, ra-direction, ra-closure, ra-critic,
debate-r1, review-doc, bundlepack, strictfix, hashcheck, envgate,
strictfix-r2, methodology-synthesis, envgate-fix, hashcheck-fix,
bundlepack-fix, pr22-finalhead, pr25-finalhead, pr24-finalhead,
pr23-finalhead, advisor-site-review, pr23-fix, pr24-fix, pr25-fix,
pr24-fixreview, pr23-fixreview, pr25-fixreview, pr25-fix3, pr24-fix3,
pr24-fix3review, pr25-fix3review, pr25-fix4, pr24-fix4, genwide-impl,
pr2425-finalpass, advisor-impl, integration-review, capture-impl,
advisor-lens, genwide-lens, capture-lens-tests, capture-lens-bugs,
advisor-fix, capture-fix, pr28-finalhead, pr27-finalhead,
capture-mergefix, pr27-tailpass, integration-review2, sweep.

### C-024 (19 rows, 07:29-08:16)

S1-scope, S3-stats, S2-p2015, S4-rqreg, R1-scope-review,
R3-stats-review, R2-p2015-review, F1-scope-fixes, R4-rqreg-review,
F3-stats-fixes, F4-rqreg-fixes, F2-p2015-fixes, FH-scope, FH-p2015,
F5-p2015-tail, FH2-tails, INT-review, F6-integration-fixes, SWEEP.

### C-025 (30 rows, 08:35-10:05)

84081--C (out/log missing), 85625--C (out/log missing), p2031-redteam,
codex-p2031-review, codex-ap-review, 91286--C (out/log missing),
S10-rqvar, p2032-exec-audit, S9-linter, R9b-linter-tests,
R9a-linter-correctness, F9-linter-fixes, W2F-p2031, W2F-p2029,
W2F-p2032, W2F-p2030, FH2-p2032, FH2-p2029, FH2-p2031, FH2-rqvar,
FH2-p2030, FH2-p2033, W2T-rqvar, W2T-p2029, W2T-p2030, W2T-p2033,
W2-TAILVERIFY, INT2-review, INT2-fixes, SWEEP2.

### C-026 (7 rows, 16:35-17:22)

P34-design, P34-impl, R34a-exec, R34b-compliance, F34-fixes, FH34,
WRAP-meeting.

## Cross-links

- D-031 breach addendum (MET-1): `docs/decision_log.md`, end of the
  D-031 entry.
- D-050 stop-card override addendum (MET-3): `docs/decision_log.md`,
  end of the D-050 entry.
