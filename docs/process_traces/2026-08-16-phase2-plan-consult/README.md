# Phase-2 re-freeze transaction plan consult (2026-08-16)

Rule-2 design consult (Sol xhigh, read-only, post-T9 main). **Magistrate
disposition: ADOPTED AS THE PHASE-2 PLANNING INPUT** — Ed's R1-cl.6 reserved
list is untouched (the plan presents options for pack IDs/numbering and
marks every Ed-approval point; it decides nothing reserved).

Shape: ONE marker-gated successor-family transaction. The staged
`impl/wo-detect-pulses-budget` branch lands FIRST inside the transaction;
D-079 gets a genuine successor issuance with complete dual-generation pin
migration; all three successor packs are generated and freshly evidenced
(no grandfathering, per R1); Ed's itemized approval (early choice checkpoint
for IDs/numbering + final exact-byte publication confirmation); the family
marker publishes LAST — the irreversible point is the instant that commit is
reachable from origin/main. Phase-3 baseline supersession and live E-10 stay
OUT of the publication step (F5).

**Sequencing consequence executed same-day:** calibration-side stage-2
stamping (deferred from #156) belongs on the staged estimator branch BEFORE
transaction assembly (F2) — launched onto `impl/wo-detect-pulses-budget`.
