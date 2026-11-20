# Current pointer and Next activation (Q7)

Read `CANONICAL.md`, RUN_STATE's highest numbered item, then `CURRENT.json`.
The pointer is a shadow declaration, not evidence of an armed or measuring host.
Only the lead sets the source block. A null arm does not establish host idleness.
An active stop card still overrides every other restart pointer.

Every **Next activation** states an observable, a deadline, and an early-result
or refusal branch. At the deadline, report a missing observable to the lead.
Silence never establishes collection or authorizes another arm. Express a
chain-terminal wait as `result_json_exists`: a pre-chain refusal never creates
`chain.exited`. Read the verdict first when a result or results branch arrives early.

## Source block

Write an exact, unindented ` ```pointer ` fence (without the surrounding spaces)
directly below the numbered item's heading, allowing only blank lines between.
Close it with an exact, unindented ` ``` ` line. The PLAN §5.1 example uses made-up
values; it is not an arm record:

````markdown
262. **Laptop lead (...), 2026-11-11 04:10 PST: R1 re-armed.**

```pointer
owner: magistrate
armed: align-r1-20261111T0453Z
host: mbp
t0: 2026-11-10T20:53:00-08:00
latest_end: 2026-11-11T19:03:00-08:00
wait: result_json_exists
deadline: 2026-11-11T19:33:00-08:00
on_early_or_refused: read verdict first; REFUSED means unstrand, restore network time, re-plan
next_observable: branch night-results/align-r1-20261111T0453Z carrying result.json
```
````

`owner`, `wait`, and `next_observable` are required. `armed`, `host`, `t0`, and
`latest_end` appear together or are all omitted. `wait` is exactly one of
`result_json_exists`, `results_branch_exists`, `watchdog_status_state`,
`pr_merged`, `ruling_recorded`, `none`. Name the exact record, ref, state, PR or
ruling in `next_observable` and the owning item. `chain_exited` and every unknown
wait are refused. `deadline` and `on_early_or_refused` are required unless
`wait: none`. An armed block always needs a deadline, including with `none`.
The times must satisfy `t0 < latest_end <= deadline` when armed.

Time values use ISO 8601 with an explicit offset or `Z` (UTC). They must fall
within 2026-01-01 through 2030-01-01 UTC, including the endpoints. Naive times,
bare epochs and impossible dates/offsets are refused. They become numeric epoch
seconds; fractional seconds use Python datetime's microsecond precision.

Each body line is `key: value`; the first colon separates the key from the
value. Surrounding whitespace is stripped. Values must be nonempty printable
single-line text. Unknown keys, duplicate keys, empty values, malformed body
lines, a second block in one item, an unterminated block, and a misplaced block
are named errors with RUN_STATE line numbers. Every block is validated, even
when an item with a higher number also carries one.

The highest numbered item **carrying a block** wins, regardless of file order.
Sort the numeric part first, then the optional lowercase letter (`256b > 256`,
`257 > 256b`). Items without a block do not affect pointer selection. Ordinary
legacy text needs no regeneration. After cutover, `run_state_add.py` regenerates
the file for each typed item. Headings inside other fenced examples are ignored.
Quoted or indented pointer fences are examples and ignored; indented fenced
examples also suppress recognition until their matching closing fence. Other
Markdown fences close with the same character and at least the opening length.
A declaration's own closing line must be exactly three backticks.
A typed item block (TYPED-ITEMS, `docs/process/run_state_item.schema.json`) may
follow the pointer block.

## Generated file and commands

`CURRENT.json` has exactly `schema`, `source_item`, `source_item_heading_date`,
`owner`, `armed`, `wait`, `next_observable`, `open_items`. The schema is
`joulewise.current_pointer.v2`. The source item is a string such as `256b`;
its date is the first `YYYY-MM-DD` in that heading or null. There is no clock field.
`armed` is null or `{plan_id, host, t0_epoch_s, latest_end_epoch_s}`.
A block's `wait` is `{observable, deadline_epoch_s, on_early_or_refused}`;
optional omitted fields for `none` become null. If no item has a block, the
declaration fields are null, including `source_item`, `armed` and `wait`.
`open_items` lists `{item, status, owner, expires_epoch_s}` for recorded DRAFT,
ISSUED and ARMED items in descending item order. It is empty before cutover.
Readers compare expiry against their own clock.

Run `python3.13 -B scripts/gen_current.py` after editing a block. It atomically
writes deterministic UTF-8 JSON with sorted keys, two-space indentation, literal
Unicode and a final newline. Use `--check` for a read-only byte comparison and
`--show` for a checked phone line including the open item count. Fixture paths
are `--run-state PATH --out PATH`.
Exit codes: 0 agreement/success, 1 generated-byte drift, 2 invalid block/file or
usage. Drift prints the umbrella command `python3 scripts/gen_state.py`.

The umbrella commands `python3 scripts/gen_state.py` and
`python3 scripts/gen_state.py --check` also generate and check the live pointer.
The generator evaluates no observable and probes no hosts, Git refs, custody,
results, or network service.
