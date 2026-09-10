# 39 — Lead record: the 2026-09-02 macOS update (25F84 → 25G83) invalidates the issued calibration acceptance; G2-a blocked until a successor is issued (2026-09-10 ~08:05 PDT)

## Bench facts (activation 96bfeca7)

- Dry run in the fresh clone `/Users/edr/JouleWise-measurement-v5-20260910-d84da72e` (main `d84da72e`, clean, lock diff empty, ledger authenticated
  with custody replay at sequence 76): `build-probes` PASS (idle_seconds 75 present in every config); `bind-window` REFUSED
  `calibration_vector_derivation_refused: _AcceptancePreflightError: acceptance_artifact_epoch_mismatch` (stale_fields `['os_build']`);
  `check` refused downstream (`input_inventory_unreadable`). Temporary ledger copy used; the clone's ledger bytes unchanged (sha256 `aa806848…` both).
- `sw_vers`: macOS 26.6.2, BuildVersion **25G83**; `hw.model` Mac15,9. Issued acceptance `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`
  `identity_epoch.os_build` = **25F84**. All 76 ledger rows carry 25F84. `softwareupdate --history`: "macOS Tahoe 26.6.2 — 09/02/2026, 20:30:32";
  reboot 2026-09-02 20:35. The new `/usr/bin/powermetrics` sha256 `b762e5bf…1330c5` differs from the historical binding (consult 38 Q5).
- `validate_plan.py` dry run with the proposed inputs: `PASS NightPlan.from_mapping and canonical writer serialization`; the only FAIL is the expected
  "authorship must precede t0 by no more than 36 hours" (authored 43 h before the 09-12 t0; tomorrow's authoring would satisfy it).

## Doctrine (consult 38, Astra xhigh, `verdict.cause: confirmed`)

D-102 cl.2: freshness = exact identity epoch {os_build, hardware_model, power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id};
any change → stale; mandatory prospective re-derivation; a trigger observation is judged under the PRIOR artifact. `docs/contracts/powermetrics_fiducial.md:77`:
calibration and collection must use the same OS build and powermetrics binary. D-161 keeps this class fail-closed. The G2-a chain consumes the acceptance
at bind-window, check, bracket reservation, pre AND post calibration writers, chain screen, campaign evaluation; `DIAGNOSTIC_NO_PACK` exempts only C2.
A diagnostic exemption would be a new rule (not the resident magistrate's to make).

## The gap (consult 38 F1, blocking)

No installed new-epoch bootstrap: `validate_powermetrics_fiducial.py --allow-live` requires the current matching-epoch acceptance before capturing;
`reissue_calibration_acceptance.py` re-derives the predecessor's members only; historical import is genesis-only; the issued-artifact validator requires
one epoch equal to the acceptance's. Appending 25G83 observations is not sufficient for the existing issuer.

## Route (consult 38 Q2, conditional calendar) and lead disposition

1 rule the bootstrap and rollover (cold gate + Opus; Ed for scientific rules) → 2 implement the derivation-only capture route + generation validation
(gauntlet) → 3 harvest rehearsal-20260911, retire the stub → 4 corpus capture night (agent-free) → 5 derive + cold science gate → 6 D-138 atomic
transaction (successor acceptance + fan-out + staged R2) → 7 bind/arm G2-a → 8 run/harvest. Earliest credible: corpus night 09-12, first G2-a 09-14.

Disposition: G2A-FIRST-WINDOW-01 is BLOCKED on a new p1 lane ACCEPTANCE-EPOCH-25G83-01; runbook 68 / checklist 13's arm steps are SUPERSEDED for
09-11 (harvest + item 5/6 + stub retirement stand; no G2-a arm). Ed emailed 08:05 PDT with the finding, the route, and his two decisions (corpus design
rules; ledger representation), defaults stated. A blind three-seat design consult on the bootstrap mechanism is convened now (records 40–43).
