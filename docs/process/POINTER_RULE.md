# Current pointer and Next activation (Q7)

Read `CANONICAL.md`, RUN_STATE's highest numbered item, then `CURRENT.json`.
The pointer is a shadow declaration, not evidence of an armed or measuring host.
Only the lead sets `owner`, `armed`, `wait` and `next_observable`.
The initial null arm and wait do not assert that a host is idle.

Every **Next activation** states a checkable observable, a deadline, and what
to do on an early result or refusal. Copy those fields into `CURRENT.json` in
the same commit. At the deadline, report a missing observable to the lead;
silence never establishes successful collection or authorizes a new arm.

`schema` is `joulewise.current_pointer.v1`. `run_state_top_item` is an integer;
optional `run_state_top_item_suffix` is one lowercase letter and, when present,
must match the highest heading's suffix. Headings sort by number then letter.
Omitting the suffix tracks the numbered item only. `updated` is an ISO time
with an offset. `owner` and `next_observable` are nonempty single-line text;
the latter is at most 240 characters.

`armed` is null or `{plan_id, t0_epoch_s, latest_end_epoch_s, host}`.
`wait` is null or `{observable, deadline_epoch_s, on_early_or_refused}`.
An arm requires a non-`none` wait, with deadline at least the latest end and
latest end at least t0. Epochs are integers strictly after 2026-01-01 UTC and
before 2030-01-01 UTC. Booleans, strings and millisecond epochs are refused.

The closed vocabulary is `result_json_exists`, `results_branch_exists`,
`watchdog_status_state`, `pr_merged`, `none`. `none` is only for an unarmed
declaration. The lead identifies the exact result, ref, watchdog state or PR
in `next_observable` and the owning item. The checker validates declarations;
it does not probe hosts, Git, custody, results, or network services.
Express a chain-terminal wait as `result_json_exists`; `chain_exited` is refused.

## Worked example: audit item 249

Item 249 waited for `chain.exited`. A pre-chain hazard refusal cannot create
that file. Instead write: "Wait for `result_json_exists` or the declared latest
end. If the results branch appears early, read verdict first. On refusal,
report to the lead for host restoration and a re-arm decision."

Synthetic example of the same rule (these are not the historical arm times):

```json
{
"armed": {"plan_id": "example-item-249", "t0_epoch_s": 1794350000,
          "latest_end_epoch_s": 1794353600, "host": "example-host"},
"wait": {"observable": "result_json_exists", "deadline_epoch_s": 1794353600,
         "on_early_or_refused": "Read verdict first; report refusal to lead."}
}
```

After adding a numbered item, run `python3.13 -B scripts/current_pointer.py bump`.
It changes only `run_state_top_item` and `updated`; all other bytes and key
order stay intact. Correct or remove a stale optional suffix manually first.
Run `python3.13 -B scripts/current_pointer.py check` before committing.
Use `python3.13 -B scripts/current_pointer.py show` for a phone-sized line.
All commands accept `--pointer PATH --run-state PATH` after the command.
Exit codes: 0 valid, 1 failed check/write (with the exact bump command), 2 usage.
Malformed declarations need manual correction; bump never invents an arm.
