# Registration-grade series planning sheets

**PROVISIONAL, NOT ARMABLE.** These JSON documents describe proposed allocation,
capture requirements and sizing. Their custom `*_template.v1` schemas,
`execution_enabled: false` and unresolved bindings distinguish them from native
night plans. No runtime currently consumes these fields to enable capture.

| File | Purpose |
|---|---|
| `series_plan.template.json` | Source pins, order, seven D windows, T1–T3, conditional D8/T4, per-pair seed ranges, rank and yield/budget arithmetic |
| `d_window.template.json` | Reusable 22-member calibration frame: 4 exact anchors, 2 sentinels, 14 benign, 2 ordinary v4 sabotage |
| `t_window.template.json` | Reusable 22-member locked-test frame: 4 anchors, 2 sentinels, 4 benign, 10 attacks, 2 real-compute controls |
| `p30b_window.template.json` | Proposed corrected 24-member physics roster: 4 anchors and 4 carrier clusters, each sham + P2/P3/P5/P6 |

The full plan and pending lead questions are in
[SERIES-PLAN.md](../../../../docs/align/squeeze/SERIES-PLAN.md).

For D and T, select the window entry in the series sheet. For every fresh row,
`seed_index = seed_index_start_by_pair[pair] + seed_slot`. `attack_slot` selects
that pair's frozen arm list; `site_slot` selects its window's physical-control
list. Sentinels and controls replay the admitted W1 sentinel rather than taking
fresh seed slots. P-30B carries its explicit separate development seeds. Before
D1, the kit lane must materialize the full ordinal/seed/hash manifest and exact
configs, binding all D rows to the unchanged frozen v4 configuration. References
to `PENDING_*` are requirements to fill under the owning gates, never defaults.

All sheets enable and require KM003C capture, rails alongside DC, and sealed full
transcripts with native reasoning retained. A meter process's exit zero is not
proof of live capture. The separate capture lane must implement and natively
verify this requirement, including R1/W1 capture without altering R1's kit.
Native sizing must include injection, gates, idle and tails inside the same
member cap. The W1-only validator does not validate these new D/T/physics frames;
do not relabel a sheet as a runnable plan or feed it to an installer.

The small synthetic allocation checks read only these files and the four anchor
configs in this clone:

```sh
python3.13 -B -m unittest tests.test_align_v4_series_plan
```

No full suite, measurement command, real-data path or network is needed.
