# Cold-gate packet — replay verdict under Low Power Mode; merge of PR #308 (and the shape for PR #309)

Assembled mechanically by magistrate activation 2145630c on 2026-09-09 ~06:00 PDT. Trigger: rule-11 mandatory — treating a
full-suite replay `rc=1` as non-blocking for a merge is a reinterpretation of a gate verdict.

Evidence (absolute paths, all read-only for the judge):
- P1 38-replay-308-5d13d0e6-tail.txt — replay tail and the four FAIL blocks
- P2 39-idle-admission-alone-5d13d0e6.log, 39-idle-admission-alone-5db38b58.log — class alone on both heads
- P3 41-rootcause-idle-admission-local-astra-report.md — Astra xhigh root-cause seat (derivation located; execution blocked by sandbox)
- P4 42-bench-rootcause-low-power-mode.md + 42-bench-diagnostic-idle-admission.out — magistrate bench diagnosis (timeout, timer slack, powermode 1)
- P5 30-ref-308-final-opus-contract-review.md, 33-consult-308-crossdoc-drift-astra-report.md, 36-delta-308-round5-astra-report.md — PR #308 review state (clean after round 5)
- P6 31-terminal-review-night-gate-stub-chain.md, 23b-delta-stub-fix1-astra-report.md — PR #309 review state (clean; replay not yet run)
- P7 GitHub: `gh pr checks 308` / `gh pr checks 309` (test shards SUCCESS at 5d13d0e6 and 5db38b58; only `gate-ledger` red, by design until the ledger is filled)
- P8 Machine: `pmset -g custom` (AC Power powermode 1), `python3 -c` sleep-slack probe (re-runnable), `git diff --stat 83ab38ed..5d13d0e6 -- joulewise scripts tests`

Questions for the judge are in the charge (44-coldgate-charge-replay-verdict.md). The ruling file is 44-coldgate-ruling-replay-verdict.md.
