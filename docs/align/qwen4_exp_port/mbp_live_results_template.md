# Saturday 2026-11-07 Flash-Next validation: {{RUN_ID}} — {{SYNTHETIC}}

PROVISIONAL — generated from validation evidence, never energy evidence.
Operator: PENDING. Mac/OS/build/ambient conditions: PENDING.
Start/end local and UTC times: PENDING. Measurement jobs stopped: PENDING.
WD SN7100 / OWC Express 1M2 serial, USB4 link and physical disk: PENDING.
Native unit-test outputs and venv identities: PENDING.

Source revision: {{SOURCE}}

```json
{{ARTIFACT}}
```

Receipt timings (UTC, elapsed, bytes and mean decimal MB/s):

```json
{{RECEIPT_TIMINGS}}
```

All GB are decimal; divide by 2^30 for GiB. Metal, RSS and file-cache
residency overlap in unified memory. Never sum them. Converter v2 manifest
digests for large files are chunked; the separate SHA256SUMS are ordinary SHA-256.

## Evidence inventory

{{EVIDENCE}}

## Abort and crash triage (runbook step 4)

The triage classifier and this report consume the same pre-decided action
table. A generated `<stage>.json.triage.json` records the selected row.

{{TRIAGE_ACTIONS}}

## Memory (GOAL 6)

```json
{{MEMORY_SUMMARY}}
```

{{MEMORY_ROWS}}

{{MEMORY_STEP_ROWS}}

Predicted versus observed allocation proxy (Metal, RSS and PLE are never
summed; QSA is file-backed and shown only as a prediction component):

{{ALLOCATION_ROWS}}

```json
{{MEMORY_MONITOR}}
```

Review memory.json + monitor.jsonl for initial swap usage, swapout delta,
minimum memory_pressure free percentage, pressure level, compressor growth
and process maximum RSS; the summary above is populated automatically.
Model 40,960-token peak prediction: 112.7 GB maxfit / 97.6 GB maxfit5.
The generated prediction error uses Metal peak as an allocation proxy.
Lead's interpretation of resident bytes vs prediction within 10%: PENDING.
Abort/fallback reason, fresh-run evidence and profile selection: PENDING.
No hard OS file-cache quota is claimed: the 21.5 GB resident-page cap is
checked at memory-probe checkpoints and after each other probe, with abort.

## Fixed texts and real-template XML (GOAL 7)

{{QUALITY_ROWS}}

Human review of generated coherence text and both tool round trips: PENDING.
NLL per natural/control text, long-tail delta, failures and explanations: PENDING.
Quantization thresholds are provisional screens; measured bf16 recipe drift: PENDING.

## Fixed benchmark and reference

{{BENCHMARK_ROWS}}

```json
{{REFERENCE}}
```

Reference checkpoint/precision/server log provenance independently checked: PENDING.
Per-item answer/pass disagreement review (including truncation): PENDING.
No hosted reference or mismatched identity means the comparison gate stays OPEN.
FP8 or proprietary-family references remain advisory, regardless of verdict.

## Performance (GOAL 8)

{{PERFORMANCE_ROWS}}

Raw repeats, warmup and generated tokens are in each worker/rungs journal.
P5 targets from PR #670: prefill >=400 tok/s (512) / >=550 (2048), decode
>=30 tok/s, stretch 40. These were e3 recipe extrapolations; target applicability
to maxfit and any misses: PENDING. Monitoring overhead and cache state: PENDING.
Efforts are low/medium/xhigh; all emitted reasoning tokens count as decode.
Each cell shows median (minimum-maximum) over non-warmup repeats and a
MEETS/MISSES result. These remain PR #670 e3-recipe extrapolations.

## PLE paging and external disk I/O

{{PAGING_ROWS}}

First pass cache state: UNKNOWN unless a clean restart + observed residency
supports a cold claim. Warm pass follows identical tokens. iostat cumulative
external-physical-disk MB delta and elapsed seconds: PENDING. Other disk I/O:
PENDING. Fault counts and ru_inblock are diagnostic counters, not disk bytes.
PLE gather-seconds delta / lookups and peak resident pages: PENDING.

## Pre-decided next actions

{{NEXT_ACTIONS}}

These actions are generated from the report rule table. They do not edit or
close any GOAL line below.

## Completion and custody

GOAL 6: OPEN pending native no-swap + resident-accounting review.
GOAL 7: OPEN pending all quality, benchmark and reference evidence review.
GOAL 8: OPEN pending native repeats and target comparison.
GOAL 11: OPEN; full gold run is separate PR #680 / lead-owned evidence.
Source + converted manifests, script commit and output checksums retained: PENDING.
External volume ejected, then physically unplugged: PENDING.
Quiet measurement lane resumed only after operator handoff: PENDING.
Lead decision, outstanding risks and next exact action: PENDING.
