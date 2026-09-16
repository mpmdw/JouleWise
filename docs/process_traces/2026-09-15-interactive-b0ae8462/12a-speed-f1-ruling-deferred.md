# 12a — TEST-SPEED-01 F1/F2 (fitter loss multiset, parsed-plist cache): DEFERRED behind the source-byte acceptance pins (magistrate b0ae8462, 2026-09-15 22:50 PDT)

The Astra seat (12) refused correctly: `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` pins the SOURCE
BYTES of `joulewise/powermetrics_fiducial.py`, `joulewise/adapters/powermetrics.py` and `joulewise/uncertainty_evidence.py`;
`tests/test_powermetrics_fiducial.py:1588` requires the current hashes to equal the issued pins and
`scripts/validate_powermetrics_fiducial.py:393` refuses changed source as `acceptance_artifact_stale`. Numerical
bit-identity does not preserve source hashes, so ANY edit to the fitter or the plist reader invalidates the issued
calibration acceptance — a physics/evidence fence (D-161 keeps these fail-closed). The local checkout also holds no
hydrated pulse-calibration captures to re-issue against.

Ruling: F1 (3.8× fitter, bit-identical) and F2 (digest-keyed plist cache) are NOT applied now. They are bundled into
the next calibration-acceptance re-issue (the epoch/acceptance campaign that real windows will trigger), where the
source pins are re-issued against the retained corpus anyway; the bit-identity harness the seat was asked for becomes
that campaign's acceptance evidence. Registered for the queue as TEST-SPEED-01-FITTER (blocked on the next acceptance
re-issue). The other TEST-SPEED-01 levers (histsem batch reads, calexits pool, crash-matrix lazy imports, run_campaign
git-probe merge, shard weights) are not pinned and proceed.
