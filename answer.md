# WP20 handoff

Drafted [protocol v4](docs/align/pilot_protocol_v4.md), including the reserved
**Addendum FN**, 18-member W1 roster, pinned source citations, and explicit
**PENDING-RULING** blocks for sensor selection, R custody and ThermalRegistry
reach. All hardware/registration status stays PROVISIONAL.

Branch: `lane/2026-11-05-align-v4-wp20-protocol`, based on `c8ef6b2f6`.
Protocol commit: `a757b52e9c0a4a936d5b8d8d88b01b9420427e72`
(`docs(align): draft WP20 protocol v4 skeleton`). The subsequent documentation
commit, `docs(align): record WP20 validation and handoff`, adds this file and
the [run report](docs/run_reports/2026-11-05-align-v4-wp20-protocol.md).
Both commits are local; no push.

Verification:

- `python3.13 -B /private/tmp/jwsol/v4-wp20-doc-check.py docs/align/pilot_protocol_v4.md docs/run_reports/2026-11-05-align-v4-wp20-protocol.md answer.md`
  — PASS: 3 Markdown files, 6 local links, 124 citation ranges / 9 sources,
  plan digest, formatting, 3 pending rulings, Addendum FN and file scope.
- `git diff --cached --check` and `git diff c8ef6b2f6..HEAD --check` — PASS.
- Unit tests: **0 run, 0 skipped**; native tests: **0 run**. Doc-only work;
  no full suite, model work or compileall. The run report lists exact native
  unittest commands the lead must run outside the MLX/Metal sandbox.
- `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` — exit 2:
  sandbox denied `ps`; census remains unverified. No fixtures were launched.

The source check caught Ed's newly appended High Power ruling (plan lines
335–340). R1 now includes A-B-A via Ed's narrow power-mode sudo rule, with
Automatic restored on every exit; the earlier skip default is superseded.

Lead next: install the three WP14 rulings, freeze the proposed desk conventions,
bind WP11/WP17 native slots and WP18/19 identity fixtures, then complete the
blind Fable + Opus registration gate. Ed's capacity/Q4/Q6 dispositions and Q5
rule installation remain external. The mutable plan's cited snapshot and the
80 GB minimum versus approximately 117 GB W1 reservation need lead custody
and sizing review. No scientific or live-readiness claim was made.

Files touched: the protocol, this answer and the dated run report only.
RUN_STATE.md, TASK_QUEUE.md, the state kernel and tests/test_gen_state.py
remain unchanged; no kernel tasks were registered.
