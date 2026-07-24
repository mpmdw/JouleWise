# DIAGNOSTIC floor summary — NON-CLAIM-BEARING

DIAGNOSTIC ONLY; NON-CLAIM-BEARING. Every source window has a failed whole-window verdict. These values cannot establish a detection floor, claim readiness, or L2/L3 eligibility.

`floor_gate_j` is null unless both absolute and comparative components exist for the same window-local cell. Suite rows are point-only because this wire has no governed per-item/per-level admissible half-width.

| Cell | Metric | Condition | n | floor_abs_j | floor_cmp_j | floor_gate_j | Width coverage | Origin | Window verdict | Caveat |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| A5-RQ-MID-GROSS | `gross_energy_j` | `request_mid` | 10 | 1.983116 | — | — | 10/10 | a5 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A5-RQ-MID-IDLE | `energy_request_j` | `request_mid` | 10 | 1.996585 | — | — | 10/10 | a5 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A5-RQ-SHORT-GROSS | `gross_energy_j` | `request_short` | 10 | 2.174320 | — | — | 10/10 | a5 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A5-RQ-SHORT-IDLE | `energy_request_j` | `request_short` | 10 | 2.188162 | — | — | 10/10 | a5 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A5-PH-PREFILL | `phase_energy_j.prefill` | `phase_prefill` | 10 | 3.628650 | — | — | 10/10 | a5 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A5-PH-DECODE | `phase_energy_j.decode` | `phase_decode` | 10 | 3.109728 | 6.461271 | 6.461271 | 10/10 | a5 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A5-PH-SHORT-PREFILL | `phase_energy_j.prefill` | `phase_short_prefill` | 10 | 2.647187 | — | — | 9/10 | a5 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A7-PH-PREFILL | `phase_energy_j.prefill` | `phase_prefill` | 10 | 11.845879 | — | — | 9/10 | a7 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A7-PH-DECODE | `phase_energy_j.decode` | `phase_decode` | 10 | 3.478120 | — | — | 10/10 | a7 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A7-PH-SHORT-PREFILL | `phase_energy_j.prefill` | `phase_short_prefill` | 10 | 2.296550 | — | — | 10/10 | a7 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A8-SU-ITEM | `suite_item_mean_gross_energy_j` | `suite_sentinel_item_mean` | 10 | 0.180333 | — | — | 0/10 | a8 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A8-SU-LEVEL | `suite_level_gross_energy_j` | `suite_sentinel_level` | 10 | 0.900453 | — | — | 0/10 | a8 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A8-RQ-LONG-PROMPT-GROSS | `gross_energy_j` | `request_long_prompt` | 10 | 1.844221 | — | — | 10/10 | a8 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A8-RQ-LONG-PROMPT-IDLE | `energy_request_j` | `request_long_prompt` | 10 | 1.834897 | — | — | 10/10 | a8 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A8-RQ-LONG-DECODE-GROSS | `gross_energy_j` | `request_long_decode` | 10 | 1.790308 | — | — | 10/10 | a8 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
| A8-RQ-LONG-DECODE-IDLE | `energy_request_j` | `request_long_decode` | 10 | 1.822161 | — | — | 10/10 | a8 | **failed** | DIAGNOSTIC ONLY; NON-CLAIM-BEARING |
