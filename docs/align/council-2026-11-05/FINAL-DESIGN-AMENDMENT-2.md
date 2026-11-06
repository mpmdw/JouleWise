# FINAL-DESIGN Amendment 2 (laptop lead, 2026-11-06): housekeeping before R0

Recorded by the laptop lead (interactive session 359dce51, Opus 5.5) under ALIGN v4 WP12. It changes no window design, threshold or registered analysis. It records three facts that the R0 directive cites.

## 1. R0 SMC step profile is 300 / 900 / 600 s

Amendment 1 §R0 item 3 and FINAL-DESIGN §R0 describe a 60 s load step. The 2026-11-05 laptop-lead ruling (`docs/align/r0_step_test_ruling.md` on the integration lane) replaces it with 300 s idle, 900 s load and 600 s recovery (30 min). The reason is that a 60 s step cannot separate die-class from heatsink-class keys when the slow time constant is up to 300 s.
- The WP14(a) model-free classifier (`docs/align/council-2026-11-05/WP14-RULINGS.md`) reads that profile.
- The committed R0 config `configs/align/v4/r0_desk.json` sets it.
- The R0 runner refuses any load step below 900 s (`smc_step.load_below_tau_upper_bound`).

## 2. The frozen alternative desk commit is `cda28a5ef`; its implementation is `4d54cb47b`

FINAL-DESIGN cites the frozen alternative desk as `4d54cb47b`. That is the implementation source freeze. What actually runs is the next commit, `cda28a5ef`, which only pins it:
- `scripts/align_pilot_alt_desk.py`: `FROZEN_COMMIT` changes from `'PENDING_SOURCE_FREEZE'` to `'4d54cb47bb7ba0c267138a57de747a7183ca23ff'`, and the comment is updated.
- `docs/align/pilot_protocol_v3.md`: the pilot 7 desk addendum names the freeze commit.
- `.codex-report/desk-attention.md`: the verification report.

Nothing in `cda28a5ef` changes the analysis code, so `4d54cb47b`'s implementation is what runs. Desk invocations name `cda28a5ef`.

## 3. Mac15,9 SMC sensor keys are provisional until R0

Mac15,9 is the expected `hw.model` of the measurement MacBook Pro. The sensor keys the v4 gates read on it, both die class and heatsink class, are **provisional** until R0's SMC enumeration and step test classify them on that Mac:
- R0's host-identity gate refuses model work if `hw.model` differs from the config.
- No R1 or W1 thermal policy may name keys that R0 did not classify.
