WRITE_SCOPE: []

# CONSULT — D169-STAGE3-01: what does the unattended PACK-BOUND launch path still need, and what is the smallest sound design? (gpt-6-astra, high, read-only)

Context: the first real window is G2-a (DIAGNOSTIC_NO_PACK), which stage 2 of D-169 already supports. Everything
after it (G2-b, ALPHA/BETA/GAMMA campaign nights) is TRANSACTION_PACK and today refuses with
`night_refused_class_unbuilt`. The readiness scout (docs/process_traces/2026-09-08-handoff-redo/27-scout-v5-readiness-astra-report.md
§"Critical path" and row H) says stage 3 requires the GO-receipt consumer and the T-0 rehearsal obligations, and
that the kernel currently gates it behind NIGHT-REHEARSAL-01. Read: docs/process_traces/2026-09-01-unattended/
(MAGISTRATE-RULING-UNATTENDED-STAGE1.md, coldgate-d1-RULING.md, anything naming stage 3), the D-169 rows in
docs/decision_log.md, docs/process/state_kernel.json tasks NIGHT-REHEARSAL-01 and every task whose dependencies name
it or D-169, scripts/run_night.py (the receipt-class branches), joulewise/night_gate.py, joulewise/arm_readiness.py
(GO receipt production: grep "GO" receipts, D-149), scripts/launch_window.py, and the T-0 evidence modules
(joulewise/arm_readiness_evidence_t0.py). Deliver (genre review, `verdict` = {counts, findings}, header < 8192
bytes): (1) the exact list of missing mechanisms for a pack-bound unattended night, each with the file:line where
the refusal or the missing consumer sits and the ruling/decision that fenced it; (2) the smallest design that lets
the night driver consume a D-149 GO receipt and launch the pinned pack chain unattended WITHOUT weakening any
fail-closed fence (T-0 evidence, pre-registration, quiet-Mac census, custody), including which existing seams it
reuses; (3) what a "T0 rehearsal obligation" means concretely and whether G2-a can discharge it; (4) an ordered
implementation plan (seats, scopes, tests, replay obligations) and a ruling packet skeleton with the questions a
cold gate must answer before any code is written. Do not modify files; never the repository-wide suite.
