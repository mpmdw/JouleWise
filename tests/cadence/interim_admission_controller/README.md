# Fixture: the pinned controller's own journal rows

`controller-rows.json.gz` holds three journals written by the pinned `joulewise.controller` and `joulewise.bundle`
serializers with the tree's mock backends and a fake clock: a complete run, a run that fails inside the measured
window, and the timing-boundary rows of an `align_episode` bundle's receipt writer. `generate_controller_rows.py`
made it:

    python3 -I -B generate_controller_rows.py PIN PINNED_SOURCE_TREE OUT_DIR MOCK_CONFIG.json

with `MOCK_CONFIG.json` the revision's own `configs/examples/mock_local.json`. `joulewise/controller.py`,
`bundle.py` and `timing_receipts.py` are byte-identical at `b4b6aeb19`, `2d347f721` and `6e9d42f1d`, and the three
outputs differ only in the generating process's id, which the receipt writer puts in `producer_id` and the span ids.
The committed file is the `6e9d42f1d` output. The mock runtime's own phase rows are in it too; the leg runtime's are
the MLX adapter's, which the frozen admission packet's productions carry. Nothing here is a measurement: the mock
backends invent every value.
