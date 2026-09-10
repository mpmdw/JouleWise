SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Consult — the machine's OS build changed (25F84 → 25G83) and the issued calibration acceptance refuses; what is the governed route to a valid acceptance and to the first G2-a window? (gpt-6-astra, xhigh, genre root_cause, read-only)

## The fact (bench, 2026-09-10 07:52 PDT)

A desk dry run of the G2-a probe producer in a fresh production clone at main `d84da72e` (`/Users/edr/JouleWise-measurement-v5-20260910-d84da72e`, ledger authenticated with custody replay at sequence 76):

```text
build-probes  → PASS built G2-a prompt ladder, configs, and manifests   (idle_seconds 75 present)
bind-window   → REFUSED: calibration_vector_derivation_refused: _AcceptancePreflightError: acceptance_artifact_epoch_mismatch
check         → REFUSED: input_inventory_unreadable (bind never wrote it)
```

`scripts/validate_powermetrics_fiducial.py::_derive_preflight_systematic_screen_s` (lines ~364–405) compares the live identity epoch with
`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` `identity_epoch` = `{os_build 25F84, hardware_model Mac15,9, power_policy
ac_high_power, sampling_interval_ms 100, estimator_revision joint_loss_sublevel_interval_branch_v2, pulse_protocol_id powermetrics_pulse_fiducial_v3}`
and raises with `stale_fields=['os_build']`. The machine today: `sw_vers` macOS 26.6.2 build **25G83**, `hw.model` Mac15,9. Every issued
acceptance artifact under `configs/calibration/` pins `25F84`. The ledger (76 rows) — check which os_build values its rows carry
(`identity_epoch.os_build` per row) and the date of the last row.

## Questions (answer from code, contracts and the decision log; cite file:line; execute `python3 -c` where arithmetic helps)

Q1. Is this refusal a physics/evidence/pre-registration refusal that must stay fail-closed (D-161), i.e. does the doctrine say a
calibration acceptance issued under one OS build does not transfer to another? Find the identity-epoch rule (D-079, D-102, D-138 and the
`identity_epoch` code in `joulewise/calibration_ledger.py` ~100–108, 767–784; `joulewise/calibration_bracketing.py`; contracts
`docs/contracts/calibration_ledger.md`, `powermetrics_fiducial.md`, `measurement_methodology.md`). Quote the sentence that makes os_build part
of the epoch and say what evidence would justify transfer, if any is defined.

Q2. The governed route to a valid acceptance under 25G83: which scripts derive and issue a D-079 acceptance (`ls scripts | grep -i accept`;
`issue_*`, `derive_*`, `validate_powermetrics_fiducial.py` modes), how many fiducial calibration observations it needs (the n=17 in the
artifact name; the 59-pulse census per observation; the ~4–8 min per capture), what quiet-window time that implies, whether the observations
must be collected in a `[QUIET-MAC]` night (they must: agent-free) and by which existing night class / chain (is there a
calibration-only plan class or does it ride the pack chain's pre/post brackets?), what D-138's "atomic successor-family re-freeze" requires
to land the reissue (and that it would also carry the staged R2 patch `docs/process_traces/2026-09-10-activation-96bfeca7/15-r2-coverage-ulp-staged-for-d138.patch`),
and which cold-gate/decision steps the doctrine prescribes. Give the ordered step list with owners (magistrate / Ed-hardware / cold gate) and a
realistic calendar: earliest night for the calibration captures, earliest issuance, earliest first G2-a window.

Q3. Can the first G2-a DIAGNOSTIC_NO_PACK window run WITHOUT a valid acceptance (its chain runs pre/post calibration brackets and the preflight
screen `b_fiducial_s <= 0.032898493715362` derived from the acceptance)? Enumerate every place the G2-a chain / producer / driver consumes the
acceptance artifact (grep `DEFAULT_ACCEPTANCE_BOUND_PATH`, `_derive_preflight_systematic_screen_s`, `calibration_acceptance`, `identity_epoch`
in scripts/ and joulewise/), and say whether a diagnostic-class exemption exists or would be a new rule (which the resident magistrate may not
make; a cold gate or Ed would). Do NOT propose bypassing the refusal; propose only governed routes.

Q4. Since the ledger rows carry their own identity_epoch: were any of the 76 observations captured under 25G83 already (i.e. after the OS
update — find the update date from the ledger rows' timestamps vs os_build, and note `ls -la /System/Library/CoreServices/SystemVersion.plist`
if readable)? If some rows already carry 25G83, does the acceptance-derivation script accept a mixed ledger or require an epoch-pure set?

Q5. Anything else on the G2-a path that pins the OS build or the identity epoch (production policy, environment admission reference
provenance, `configs/campaign_policies/quiet_mac_p2_production.json`, the D-166 registration, the prompt pin, the `arm_readiness_evidence_t0`
identity fields) — each with the consequence of the build change.

Read-only; no edits; no git writes; do not touch `/Users/edr/night-custody` or the rehearsal checkout. Report claude-codex-report/v1, genre root_cause
(verdict.cause / verdict.remediation), header < 8192 bytes; body: Q1–Q5 with the ordered route and calendar as a table.
