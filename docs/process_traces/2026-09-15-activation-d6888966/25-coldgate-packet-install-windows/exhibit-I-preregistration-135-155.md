# preregistration_d079_epoch_25g83_rev1.md lines 135-155 (main f928a0fb)
The /usr/bin/powermetrics sha256 in force is b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5;
the MLX version in force is 0.31.2. A change to either voids this registration, and so does an
estimator-code rotation mid-campaign.

Ledger baseline. Committed head pin sequence 76 digest 08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7. Each capture night is one derivation-kind ledger
session of 12 declared slots opened at head-equals-pin; the night never commits Git; the terminal pin candidate is
reviewed and committed at the desk before the next night opens.

Sample. Three agent-free [QUIET-MAC] windows on distinct calendar days, DIAGNOSTIC_NO_PACK class, chain digest
b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf. Each window: one 600 s settle after the last operator action, then 12 slots at a 600 s start-to-start
cadence, fixed order, no operator or agent present. Protocol powermetrics_pulse_fiducial_v3 unmodified; no parameter is
tuned between observations. A slot the window cannot reach is recorded unused by the session abort (reason
window_exhausted), never compressed or replaced.

Classification. Each observation is written derivation-only under the active artifact d079_calibration_acceptance_v2_n17_r6
(authenticated bytes, protocol digest, estimator-code digest); the live identity epoch must differ from that artifact's,
and a derivation-kind session slot is required. Its ledger disposition is valid or ordinary-invalid, on every
finalization path including recovery after a crash. No systematic-invalid disposition exists for this epoch, because no
acceptance of this epoch exists. Whether the bound exceeds r6's preflight_level_screen_s 0.032898493715362 is recorded
in the hashed evidence as a diagnostic only.

