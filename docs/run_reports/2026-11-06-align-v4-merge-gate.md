# ALIGN v4 integration (#682): merge gate and finding dispositions, 2026-11-06

Laptop lead (interactive session 359dce51, Opus 5.5).
- Reviews: Opus WP7 executing review of `83e2dac59..cda5716a1` (`docs/align/reviews/2026-11-06-wp7-executing-review-pr682.md`) and Fable WP8 cold pass (`docs/align/reviews/2026-11-06-wp8-fable-cold-pass-pr682.md`).
- This merge authorizes **R0 only**. R1 stays unarmable until a later RUN_STATE item says otherwise, and it waits on the lanes named below.

## Dispositions

| Source | Finding | Disposition |
|---|---|---|
| WP7 | MEDIUM r0.py:165: strict echo call fails B7 and stops R0 | **Fixed** `ba30b2172`, with a test that fails without the fix |
| WP7 | HIGH: the kit's window_reference readiness check can never pass (fails closed, R1 only) | **Deferred** to `lane/2026-11-06-v4-r1-fixes-wp7` (cloud Sol task `task_e_6aed89fff09c83228b30f68dcd51bb9c`) |
| WP7 | MEDIUM workload.py: gate cells without deadman_s | **Deferred**, same lane |
| WP7 | MEDIUM align_r1_rehearsal.zsh: exec drops the High Power restore trap | **Deferred**, same lane |
| WP7 | MEDIUM: stop-label drift (turn_token vs turn budget; runner.error) | **Rejected**: nothing reads the workload labels today, the desk side was fixed in `f40dabe93`, and the reviewer ruled the coded end_state order correct |
| WP7 | LOWs (kit fan_keys, r1_slots path, dead collector in wait(), capture_reference ok, test contamination) | **Deferred**, same lane |
| WP7 | LOWs (xhigh rung kwarg policy hash, smc_source_commit predates the classifier, rank_response order, --timeout vs SMC budget, QuietGuard forking wrappers, drain_decode traversal, persist_interval lock, resealed custody downgrade, runbook fitted-rule text) | **Deferred** to the R0 dispositions after R0's record; none changes an R0 verdict. The launcher uses no forking wrapper |
| WP8 | F1 MEDIUM: a refused XML call is invisible to the desk; F3, F4, F7, F8 LOW | **Deferred** to `lane/2026-11-06-v4-r1-fixes-wp8` (cloud Sol task `task_e_6aed8a6fadec832283a80894a13cac5b`) |
| WP8 | F2 MEDIUM: dead collector not checked in wait() | **Deferred**, merged with WP7's equivalent LOW in the WP7 lane |
| WP8 | F5, F6 LOW (thermal_gates G0 status source; reference after a G0 timeout) | **Deferred** to a follow-up on the WP7 lane once it lands (same file) |
| CI | hazard allowlist: WP14(c) cli.py refusal and registry_select.py unlisted | **Fixed** `d45379dc8` |
