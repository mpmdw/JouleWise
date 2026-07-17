# Stream ledger — advisor-facing refresh (2026-07-16)

Branch: `impl/advisor-refresh`. Source state: `main` at `3736c941db0734fa73f2c73db2dfeff619c24295`.
Scope: refresh `PROJECT_STATUS.md` and `README.md` from facts already landed on
`main`; no contract, device-list, model-family, site-generation, or deployment
work.

## AREF-1 — Present the post-PR #70 landed state without promoting claims

Decision: update the two advisor-facing summaries to say that the comprehensive
audit is closed; AXI-SA, SITE-02 D1/D2, SPLIT-AP Part I, and AXI-SB are landed;
Window A is software-unblocked but still requires Ed plus a quiet Mac; and the
agent heads are AXI-SB-ADAPTER, AXI-SC, and AXI-SD. Describe the AXI-SB probes
as live runtime-feasibility evidence, not energy or claim-bearing campaign
evidence.

Per-claim sources on `main`:

| advisor-facing claim | main commit / report source |
|---|---|
| Comprehensive audit closed (PR #66) | merge `e377f93`; clearance `08fa290`; `docs/run_reports/2026-07-14-audit-resume-axi.md` post-merge addendum |
| AXI-SA burst-decode contract landed (PR #67) | merge `7593259`; closure `36b4da1`; `docs/run_reports/2026-07-16-resumption-nohw-batch.md` |
| SITE-02 D1/D2 closed (PR #68) | merge `2778ed2`; closure `dbd8137`; same 2026-07-16 report |
| SPLIT-AP Part I pre-registration frozen (PR #69) | merge `9db4546`; closure `dbd8137`; same 2026-07-16 report |
| AXI-SB verdict `supported`, Mac C5-2.2 leg minted (PR #70) | merge `6f56bbe`; closure `95af61d`; 2026-07-16 report addendum; `docs/process_traces/2026-07-16-axi-sb-live-probes/` |
| Window A order and Ed + quiet-Mac requirement | `95af61d`; 2026-07-16 report, readiness and Ed decision sections |
| Agent heads AXI-SB-ADAPTER / AXI-SC / AXI-SD | `95af61d`; 2026-07-16 report addendum |

## AREF-2 — Preserve reader-facing contract fences

Decision: retain D-067 dual-basis wording and every existing gross versus
idle-subtracted energy label with its M3 Max / powermetrics SoC-rails boundary;
retain D-069's harness-versus-benchmark terminology; and retain D-070's five
axes, L0 instrument-support posture, floor gates, L2 ceiling, and Window A
priority. D-071's device-list/model-family review remains open, so this refresh
makes no device-list or model-family claim. D-068 remains in force: no
`DRIFT.md` edit, site regeneration, or deployment.

Evidence: D-067/D-069/D-070 in `docs/decision_log.md`; the existing
`PROJECT_STATUS.md` Measurement Methodology Highlights and Q4 agenda; D-071 at
`8a6a0cc` plus index repair `3736c94`. Changed files are exactly
`PROJECT_STATUS.md`, `README.md`, and this ledger. Deviations: none.
