# ALIGN v4 series — independent Sol seed check

2026-11-08; branch `align/2026-11-08-series-seed-check-sol`, base `25860dcaf`.

**MATCH.** All 260 slots and both supplied SHA-256 pins agree. Original
anchor config bytes also match their historical Git objects. Blind derivation
was committed at `ecbf39e42` before target-manifest inspection. No production
or coordination-state files changed. No network, model weights, measurement
data or full test suite was used.

The authoritative handoff, full differences (none), digest receipts,
reproduction command, verification and unresolved escalation proposal are in
[`series-seed-check-sol.md`](../align/v4/series-seed-check-sol.md).
The independent generator, reconstructed manifest and comparison receipt are
under [`docs/align/v4/seed-check/`](../align/v4/seed-check/).

Focused verification: independent checker MATCH; checker unittest module
8 passed (0.171 s initial / 0.198 s final); existing `tests.align.test_v4_series.ManifestTests`
8 passed (0.701 s). No native MLX tests apply to this stdlib-only addition.

Open ruling: recommend extra W1:5 replays at 23/24 to preserve the ruled
1–22 schedule; late clustering and U4 aggregation need explicit disposition.
Balanced insertion requires an order amendment. The report does not sign
or implement either choice. Lead next: compare Opus receipt, rule, then
freeze/sign the agreed manifest through normal gates.
