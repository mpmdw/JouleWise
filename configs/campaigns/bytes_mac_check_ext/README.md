# BYTES extension Mac check: non-claim

Generate: `python3.13 -B scripts/bytes_mac_kit.py --extension qwen38-27b-8bit`.
Verify: add `--check`. The original kit is frozen and unchanged.

This separate fixed tree has five extension absolute runs (the exact source
run IDs r01..r05), split 3/2 around the inherited midpoint reference. It reuses
the block-6 corpus (18 planned, stop at 12 valid), start triplet, midpoint and
end triplet, calibration and launch scaffold. R2 is unchanged: 2,048 prompt
and 512 output tokens with existing warm-up and settle.

The original kit's R8.6 rule is "five structural runs per model and twelve
additional soak runs for 70B/122B". Its threshold note §4 row 7 implementation
uses "two large runs at each end" for 70B, 122B and Next-80B (alternating with
references per design §14). This 27B dense model is outside those regimes:
no soak or test-7 stages are added. No new numerical threshold is introduced.

Only the lead runs on the Mac, in a desk worktree with the loop held and no
agent alive. Never register this kit or add it to loop.json/base_order. Dedicated
roots are runs_bytes_mac_check_ext and runs_bytes_mac_check_ext_bound. C4,
calibration, pins and precheck remain lead-owned; do not integrate this change
into the measurement checkout without its fingerprint review.

Mac commands (Python 3.13 measurement venv; JW_B5_SYNTHETIC_ONLY must be unset
for live collection):

```sh
python3.13 -B scripts/bytes_mac_kit.py --extension qwen38-27b-8bit --check
python3.13 -B scripts/check_b5_chain.py --pack-root configs/campaigns/bytes_mac_check_ext --no-live-identity
```

Use the existing desk/chain tooling with fixed campaign
`configs/campaigns/bytes_mac_check_ext/plan_tree.json`, as for the original kit.
The check command validates the fixed tree without launching a measurement. Export explicitly with
`joulewise.b6.export_runs.export(..., non_claim=True)` (or the harvest CLI's
`--non-claim`); the tree label alone is not an export switch. Preserve native
EXPORT.runs.csv and EXPORT.session.json together, including scaffold rows and
failed/skipped rows. No blinding keys are used.

Harvest the lead-prepared session plan (PLAN, ARCHIVE, REGISTRATION and
PACK_RECORDS are the desk's existing session paths, not new pack registrations):

```sh
python3.13 -B scripts/harvest_b6_session.py --plan "$PLAN" --archive-root "$ARCHIVE" --registration-dir "$REGISTRATION" --pack-records-root "$PACK_RECORDS" --export-dir "$EXPORT_DIR" --non-claim
```

Prepare MEASUREMENTS.json with schema_version
joulewise.bytes_mac_measurements.v1, non_claim true, the export session_id,
and a runs map with every exported run_id. As in the original kit, each receipt
has request_s, member_wall_s (whole member including preparation and wind-down)
and stream_s (that run's first/last paired wall/RAW stamps, including idle).
Keep the source journals; do not substitute decode time or whole-session spans.
For step-7 sizing also supply sizing.fixed_desk_s and
sizing.collection_stage_overhead_s, disjoint measured terms as in the original kit.

```sh
python3.13 -B scripts/bytes_mac_kit.py --extension qwen38-27b-8bit --runs EXPORT.runs.csv --measurements MEASUREMENTS.json --out resolvability.json
```

Exit 0 passes, 2 fails the five-run rule, malformed input raises an error.
The checker requires five succeeded, unexcluded, 512-token runs with finite
positive dur_decode_s. It prints no energy result. It records runs_checked,
decode_phase_s_range, verdict, per-member walls and stream spans, and sizing
operands plus S and T_stream_max for the lead. S uses the registered formula
for the eventual 50-science-member single-model pack, 25 references and seven
collections; it is not the duration of this diagnostic kit. Missing scaffold
or sizing receipts leave S unavailable. Only Mac receipts may fill slots;
this checker never writes slots or registrations.
