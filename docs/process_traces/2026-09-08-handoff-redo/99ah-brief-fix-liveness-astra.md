WRITE_SCOPE: ["scripts/window_status.sh","scripts/run_night.py","scripts/run_campaign.py","joulewise/measurement_liveness.py","tests/test_window_status_guard.py","tests/test_measurement_liveness.py","tests/test_run_night.py","tests/test_run_campaign.py"]

# Fix-round brief — window-status liveness census, Opus contract-refuter findings (gpt-6-astra, medium)
HEAD = a2cfb644 (landing). Astra execution refuter: clean (real-ps identity verified at the lead's bench: LIVE with
lstart token, DEAD after kill). Opus contract refuter (read it at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99s-ref-liveness-opus-contract-review.md):
LAND-WITH-FIXES. Cure, with the magistrate's rulings:
R1 (required) `joulewise/measurement_liveness.py:53,60` — classify DEAD ONLY when the probe returns rc 1 with empty
output (real /bin/ps for a dead pid); rc 0 with empty stdout → UNKNOWN (refuse); regression: `JOULEWISE_IDENTITY_PROBE=/usr/bin/true`
must yield UNKNOWN for a live pid, never DEAD.
R2 (RULED) `scripts/run_night.py:375` + `:1387-1394` — the identity probe must NOT run while the O_EXCL
`chain.started` descriptor is held with an empty marker. Design: keep the pre-existing behaviour that writes the
complete pid/pgid/epoch marker immediately after spawn (the empty-marker window returns to microseconds); THEN
observe the child's identity and add `start_time` by an ATOMIC REPLACE (write `chain.started.tmp` in the same
directory, fsync, `os.replace` onto `chain.started`); the marker is complete at every instant. Guard rule: a
`chain.started` marker WITHOUT `start_time` (crash between the two writes) is INDETERMINATE → refuse (fail-closed),
not DEAD; the dead-man path is unchanged and never sees an empty marker. Regressions: (a) kill the driver between
the two writes (mock) → marker complete without start_time → guard refuses; dead-man reconciliation still reads
pid/pgid; (b) normal path → start_time present; (c) the empty-marker window no longer contains a subprocess call
(assert no `observe_identity` call between claim and first write).
R3 (RULED) `tests/test_run_campaign.py` — RESTORE the deleted `test_r7_real_campaign_log_writer_rows_are_complete`
(real-corpus torn-prefix test under its `skipUnless` guard) verbatim from HEAD~1; keep the two synthetic rows as
additions. Coverage of real corpora is out of this lane's remit to remove.
R5 (nit, do it) `joulewise/measurement_liveness.py:110`, `scripts/run_campaign.py:8248` — `publish_campaign`'s
RuntimeError after lock acquisition must surface as the campaign runner's clean refusal (exit 2 with the reason),
lock and entry released; regression with a failing probe.
R6 (nit, do it if trivial) — do not re-append refusals/warnings when re-reconciling the registry.
R4 (docs) is registered as a follow-up (WINDOW-LIVENESS-DOCS-01): registry path, stale semantics, repair owner;
do NOT edit docs here. Acceptance = the four modules to a log with rc + `bash -n`; never the repository-wide
suite; no `git commit`; header < 8192 bytes; genre implementation verdict keys; body = per-finding cure +
counterfactual + tails.
