# Bench proposal — `T0-LIVENESS-BOUND-EMPIRICAL-01`

Proposed insertion under `/tasks/T0-LIVENESS-BOUND-EMPIRICAL-01` in
`docs/process/state_kernel.json`:

```json
{
  "acceptance": {
    "evidence": [
      "Closure route A: at least N >= 3 real T-0 rehearsal receipts carry both r1_batch_finished_monotonic_ns and validity_origin_monotonic_ns; each elapsed is reported; all are < 600 s; and the minimum observed margin below 600 s is stated. Closure route B: a cold-gate ruling re-rules the 600 s number."
    ],
    "pointer": {
      "json_pointer": "/tasks/T0-LIVENESS-BOUND-EMPIRICAL-01/acceptance",
      "label": "T0-LIVENESS-BOUND-EMPIRICAL-01 acceptance",
      "path": "docs/process/state_kernel.json"
    },
    "summary": "At least three real rehearsal receipts establish a stated empirical margin below the 600 s liveness bound, or a cold gate re-rules the number."
  },
  "authority": {
    "label": "T26 cold-gate item 3 plus the 2026-09-02 successful-path limitation",
    "path": "docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md"
  },
  "dependencies": [],
  "fallback": "Convene a cold gate to re-rule the 600 s number if real elapsed values do not retain a defensible stated margin.",
  "fences": [
    {
      "authority": {
        "label": "T26 cold-gate item 3 ruled-number authority",
        "path": "docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md"
      },
      "rule": "Fixture, mock, or synthetic receipts do not satisfy the empirical acceptance route; the 600 s number moves only by cold gate."
    }
  ],
  "flags": [],
  "goal": "Measure R1-finish-to-validity-origin elapsed on real T-0 rehearsals and establish whether the ruled 600 s liveness conjunct has an observed operating margin.",
  "id": "T0-LIVENESS-BOUND-EMPIRICAL-01",
  "lane": "quiet_mac",
  "priority": "p1_phase_gate",
  "rank": 110,
  "status": "queued",
  "status_note": "Proposed 2026-09-02 from the T26 PHYS-1 registered limitation; no retained receipt currently carries both numeric stamps."
}
```
