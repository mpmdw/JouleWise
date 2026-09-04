# Floor workload sizing (retired)

Status: **RETIRED on 2026-09-04 as superseded by D-166.** This page is an
archival disposition record, not an active design, runbook, acceptance gate,
or source of pending work.

## Disposition

D-166 is the sole workload-sizing authority for the Qwen3 `_v5` campaign. It
fixes decode at 512 generated tokens from the pinned real prompts and assigns
prefill length to the governed G2-a resolvability selector. The historical
`FLOOR-WORKLOAD-SIZING-01` idea does not select, confirm, or amend either
value.

No pilot, separate margin study, configuration change, or further ruling
remains under this retired mission. Any future proposal to change workload
sizing would be new work under D-166's authority, not a continuation of this
row. Frozen Qwen2.5 packs remain unchanged.

## Historical arithmetic boundary

D-078 and D-083 still require two quantities to remain distinguishable when
issued measurement values are reported:

```text
effect-to-floor ratio = |E| / F
effective clearable effect = F + B
effect-to-effective-clearable ratio = |E| / (F + B)
```

Here `E` is a signed measured effect, `F` is the positive operative floor, and
`B` is the non-negative claim-side measurement bound. The general reporting
helper `joulewise.workload_sizing.measured_margin_ratios` computes these
descriptive values. It is not owned by this retired mission, authenticates no
evidence, emits no verdict, and must not be used to select a workload.

The helper refuses inputs or computed ratios that are not finite so its
`to_dict()` output remains compatible with strict JSON serialization. Callers
remain responsible for sourcing all values from issued, hash-bound evidence.
