# Process-rules cold gate — 2026-09-02

This directory holds the packet, sealed outputs 196/197, and magistrate ruling for two process rules.

Q1: delegated ruling-install briefs and reports carry a clause map; installed at `docs/contracts/bridge_protocol.md` §1 (`ACCEPTANCE`/`VERIFICATION` bullets; `grep -n 'ACCEPTANCE' docs/contracts/bridge_protocol.md`), `docs/agent_playbook.md` M0 (`grep -n 'clause map' docs/agent_playbook.md`), and `tests/test_docs_freshness.py` (`test_custodied_impl_reports_carry_clause_map`, `test_bridge_protocol_clause_map_pins_s1_and_s2`). Line numbers are not cited: they drifted within one day (Sol 241 fresh pass, 2026-09-02) and drift again at every merge.
Q2: cross-artifact equality premises require a named-pair exhibit; installed in `docs/decision_log.md` as the D-160 paragraph beginning `**AMENDED (cross-artifact equality, cold gate 2026-09-02):**` (D-170 summary: the paragraph beginning `**Cold gate 2026-09-02 (process rules Q1/Q2, …**`).

The magistrate redacted the sealed outputs' scratchpad absolute paths to `<scratchpad>/` on custody.
Committed sha256: `196-coldfable-process.md` `11bccddc6498283fe0d372c036c526b9415bb130d92cf1a83e90dab0c66a5bc8`.
Committed sha256: `197-opus-refute-process.md` `f8352a9cbbb09e051934edadfd5bf8eb3a9f880fdd2add380a6f039efbf92f69`.
