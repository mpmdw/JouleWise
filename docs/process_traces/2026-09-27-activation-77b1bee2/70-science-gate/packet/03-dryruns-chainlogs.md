# 03 — Dry runs and chain logs

Primary sources and verbatim byte copies:

- `03-w1-harvest-check.txt` ← `docs/process_traces/2026-09-27-activation-3ba66eeb/10-w1-harvest/check.out` (sha256 `c18f2af494159b321591bdb29cabf96c2aa089c417a734b509d30a34956f7c38`). Copy sha256 `c18f2af494159b321591bdb29cabf96c2aa089c417a734b509d30a34956f7c38`.
- `03-w1-harvest-advance-dryrun.txt` ← `docs/process_traces/2026-09-27-activation-3ba66eeb/10-w1-harvest/advance-dryrun.out` (sha256 `1c9f6ec21a7c498d43b30968bddc0583b41f489ec293b15d885671d86e2a500f`). Copy sha256 `1c9f6ec21a7c498d43b30968bddc0583b41f489ec293b15d885671d86e2a500f`.
- `03-w1-chain.txt` ← `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/operator_logs/derivation-chain.log` (sha256 `5eb3b3600eb1efb4190b8e0896d1171b609f1a790970d55e96961000a6ed36bc`). Copy sha256 `5eb3b3600eb1efb4190b8e0896d1171b609f1a790970d55e96961000a6ed36bc`.
- `03-w2-harvest-check-w2-only.txt` ← `docs/process_traces/2026-09-27-activation-77b1bee2/10-w2-harvest/check.out` (sha256 `ed698dc0794abdb68085055cd6607b2b8364f8560385822145c90b359e85358b`). Copy sha256 `ed698dc0794abdb68085055cd6607b2b8364f8560385822145c90b359e85358b`. This is the W2-only check that returned rc 5 before the combined-session check.
- `03-w2-harvest-check.txt` ← `docs/process_traces/2026-09-27-activation-77b1bee2/10-w2-harvest/check-w1w2.out` (sha256 `7cd4d1969e98e485d7e00c81d649d7f886a08769847ed2a3c8109d95e6e4f14b`). Copy sha256 `7cd4d1969e98e485d7e00c81d649d7f886a08769847ed2a3c8109d95e6e4f14b`.
- `03-w2-harvest-advance-dryrun.txt` ← `docs/process_traces/2026-09-27-activation-77b1bee2/10-w2-harvest/advance-dryrun.out` (sha256 `04cd11b266cb71ead8df73c23da1d8aefbdc19aedf284f24e4e7b959500259da`). Copy sha256 `04cd11b266cb71ead8df73c23da1d8aefbdc19aedf284f24e4e7b959500259da`.
- `03-w2-chain.txt` ← `/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927/operator_logs/derivation-chain.log` (sha256 `af7e96276d2714fb93b2dbf9b926971f6c388615d56974b114d52ebe46a02b30`). Copy sha256 `af7e96276d2714fb93b2dbf9b926971f6c388615d56974b114d52ebe46a02b30`.
- `03-prepare-check10-dryrun.txt` ← `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/20-prechecks/check10-dryrun.txt` (sha256 `4a6e5a625d4eb3647858039220a25b4d62eb3d55b3fd3ea0e7ff6bad2810fa2c`). Copy sha256 `4a6e5a625d4eb3647858039220a25b4d62eb3d55b3fd3ea0e7ff6bad2810fa2c`.

The chain copies include every line in each source log, including `slot_end`, `slot_unused`, and abort lines if present. Harvest-time check outputs and ledger advance dry runs are included separately from the pre-run check10 dry run.
