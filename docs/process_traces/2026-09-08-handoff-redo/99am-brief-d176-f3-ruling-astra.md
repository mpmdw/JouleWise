WRITE_SCOPE: ["docs/contracts/pack_night_go_receipt.md","docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"]

# D-176 seat-1 contract — install the F3 ruling (gpt-6-astra, medium, genre implementation)
Head 07dfd03a (branch feat/2026-09-08-d176-stage3-ruling). The previous seat installed §10.1 (F1–F11) and returned
NEEDS_RULING on F3 because lineage verification forwards require_current_boot and its live caller passes True at
arm_readiness.py:10539. RULING (magistrate): the extended v2/v3 consumption reader FORWARDS the caller mode. Install
this text as the F3 entry of §10.1: "_read_v2_consumption (and its v3 successor) forwards require_current_boot
unchanged; each caller fixes its own value: the live consumer path and verify_consumed_launch's live replay = True;
the lifecycle-receipt append = False (historical); lineage verification forwards its own caller — the live check
passes True, historical lineage replays pass False." List the four _read_v2_consumption call sites with their
per-site values and the live lineage caller, each line number VERIFIED by reading joulewise/arm_readiness.py at
this checkout (never inherit numbers from this brief or the refutation); propagate to §3 (replace "including" with
the exhaustive list); add a §9 clause-map row whose counterfactual is "lineage reader hardcodes False and accepts a
stale-boot record on the live path"; append the F3 evidence to report 85's third-pass section. Acceptance:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness` rc 0 to a log; `git diff --check`; no
commit; header < 8192 bytes.
