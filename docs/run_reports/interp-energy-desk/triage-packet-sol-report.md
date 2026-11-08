Committed `0ceb6c86c` on `align/2026-11-08-triage-packet`. Clean tree; no push.

Added the packet builder/template, commit and digest bindings, lead-ruling rows, non-gating historical meter gaps, observation expiry, and exact packet retention by the arm.

Seven files changed: builder, arm consumer, cadence logic, synthetic tests, protocol, input guide, and [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-triage-packet/docs/run_reports/2026-11-08-align-v4-triage-packet.md).

Sequential `python3.13 -B -m unittest <module>` results:

- `tests.align.test_v4_next_arm_packet`: 19 passed
- `tests.align.test_v4_cadence`: 16 passed
- `tests.align.test_v4_registration`: 20 passed
- `tests.align.test_v4_executed_closure`: 2 passed
- `tests.align.test_protocol_v4_doc`: 6 passed

Focused compilation and Git diff checks passed. No full suite, network, real measurements, or MLX execution.

Remaining integration: custody/series tooling must emit the documented source inventories. Real R1/W1 export replay and native guarded-arm validation remain lead-run; native readiness is unverified.