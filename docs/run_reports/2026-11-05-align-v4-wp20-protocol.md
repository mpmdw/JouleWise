# WP20 — protocol v4 skeleton, 2026-11-05

Draft complete; registration and live qualification remain pending. Branch:
`lane/2026-11-05-align-v4-wp20-protocol`, from `c8ef6b2f6`.

## Changes and commits

- [Protocol v4](../align/pilot_protocol_v4.md): follows v3's configuration,
  roster, seeds, instrument checks, analysis and sizing progression. Includes
  the 18-member W1 order, later D-window shape, checkpoint-off/effort API rules,
  three explicit WP14 PENDING-RULING blocks with options and blocked work,
  unfilled slots, proposed desk conventions and reserved Addendum FN fields.
- [answer.md](../../answer.md): concise worker handoff and verification record.
- This dated report: evidence, limits and lead next steps. No coordination
  state, code, config, fixtures or tests changed.

Protocol commit: `a757b52e9c0a4a936d5b8d8d88b01b9420427e72`
(`docs(align): draft WP20 protocol v4 skeleton`). This report and answer.md
are the subsequent local commit, subject
`docs(align): record WP20 validation and handoff`. Resolve both IDs with
`git log --oneline c8ef6b2f6..lane/2026-11-05-align-v4-wp20-protocol`.
Neither commit is pushed.

## Verification and catches

Final offline doc check:

```text
python3.13 -B /private/tmp/jwsol/v4-wp20-doc-check.py docs/align/pilot_protocol_v4.md docs/run_reports/2026-11-05-align-v4-wp20-protocol.md answer.md
```

PASS: 3 Markdown files, 6 local links, 124 source line ranges across 9 pinned
sources, plan digest, heading/fence/table/whitespace checks, exactly 3
PENDING-RULING blocks, exactly 1 Addendum FN section, and the three-file write
scope/protected-file check. Citation checks establish source availability and
line bounds; they do not substitute for a scientific authority review.

`git diff --cached --check` and `git diff c8ef6b2f6..HEAD --check`: PASS.
Final scope/status inspection: only the three documentation files above.
Unit tests: **0 run, 0 skipped**. Native tests: **0 run**. No full suite or
compileall was run: this is documentation only, and the user forbids the full
suite while the 7-worker analysis job is active.

`python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans`: exit **2**;
`PermissionError: [Errno 1] Operation not permitted: 'ps'`. The sandbox prevents
process observation, so the census is **unverified**, not empty. No process
fixtures were launched by this task. The lead can repeat this observational
check outside the sandbox; no escalation or process signalling was attempted.

The first ad hoc citation check caught a changed shared-plan digest. Re-reading
the plan revealed the appended Ed ruling at lines 335–340: High Power A-B-A is
now included in R1 via Ed's narrow sudoers rule. Updated the draft and digest;
the final check passes. The rule's installation/restore checks remain external
work. Manual source/diff review also corrected a seed-source line reference and
the WP12 desk-pin reference. These catches changed documentation, no numbers
or runtime behavior. No independent cold review was performed here.

## Source custody

Read v3, council FINAL-DESIGN and Amendment 1 (`6eb1ff5be`), the earlier
Window-1 survey (`40c569cfd`), and the integrated SMC/thermal/budget/checkpoint
documentation. The protocol's citation table binds their exact commits/paths.
The current execution plan overrides the earlier survey's proposed fresh D
seed indices: WP16 uses D indices 1 and 91–93 as assigned.

Ephemeral source pointer: `/private/tmp/jwsol/v4-plan-synth.md`, SHA-256
`528c5217a5e279192bfc69a055a2db8bd5be2c2427d1a3ff2d136b46872e7b9e`.
Promoted to: the protocol's P citations and explicit pending blocks.
Not vendored: the lead owns promotion of the execution plan and WP14 rulings;
the shared file can change after this handoff, so retain the cited version
before registration.

Ephemeral doc checker: `/private/tmp/jwsol/v4-wp20-doc-check.py`, SHA-256
`9f7783be2c08e4c4084804e34fcce339608bee640a502e68a535bda374128239`.
Not promoted: one-off offline documentation validation, not project tooling.
No child agents or cross-model consults were invoked; invocation capture for
this worker is caller-owned. No network or real measurement-data reads, native
execution, arm, model import, or analysis-pipeline invocation occurred.

## Open rulings, risks and next exact step

The skeleton is the authorized deliverable; the following block registration,
not completion of this drafting package:

1. WP14 chair must reconcile council t63/cooling-τ selection with the fitted
   R0 rule, admit the R custody mechanism (plan recommendation: member-5 file,
   path/digest in later specs, verified at read), and choose the align-local
   registry entry point or cited runner rebind. No alternative was selected.
2. Lead/WP21/cold gate must freeze the U4 moment, heavy β_T fit, U6 early/late
   unit/weighting/CI and missing-data conventions. Library defaults are labelled
   proposals. Bind `cda28a5ef` against `4d54cb47b` per WP12.
3. WP11/WP17/WP18/WP19 must supply authenticated weights, native slots, pilot-7
   turn/token fixtures and cache/RNG identity evidence. No readiness claim is
   made. The 13-second W1 planning slack needs actual R1 sizing and the A1
   drop-17-then-lower-budget rule.
4. Ed's capacity/offload and Q4/Q6 dispositions remain external; Q5 is decided,
   but Ed's narrow rule installation and the driver's restore guarantees still
   need verification. Resolve measured disk reservation plus floor: the plan
   cites both an 80 GB minimum and about 117 GB needed at W1 arm.

Next: lead reviews/cherry-picks the protocol commit and handoff, installs the
three written WP14 rulings, then resumes WP20 finalization with the admitted
kit/desk/slots and blind Fable + Opus registration gate. Do not use this draft
as an arm authorization.

Integration-native checks the lead must run outside this sandbox, one module
at a time on the pinned stack (not executed here; counts are not claimed):

```text
python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
python3.13 -B -m unittest tests.align.test_r0_mlx_native
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx
JW_LIVE_HW=1 python3.13 -B -m unittest tests.align.test_smc_native
python3.13 -B -m unittest tests.align.test_decode_budget.DeadmanTests.test_mlx_evaluated_token_survives_alarm_during_disarm
```

These are the execution plan's integration obligations, not additional runtime
coverage needed to validate a Markdown-only diff. Measurement-Mac R0/R1 work
remains lead/magistrate-owned; fixture checks cannot close that gate.
