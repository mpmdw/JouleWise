# WP20b — protocol rulings installed, 2026-11-05

**Complete as a documentation task.** The earlier source blocker recorded in
`8c6e9f450` is resolved by the lead's local import of `a17ed96c8`.
Continued `lane/2026-11-05-align-v4-wp20-protocol` from actual HEAD
`8c6e9f450`, preserving the earlier commits after assigned base `262ff28a4`.
No network or push. This report supersedes its earlier blocked handoff;
the earlier evidence remains in Git history.

## Changes and commits

- [Protocol v4](../align/pilot_protocol_v4.md): replaced the three pending
  blocks with WP14 §§(a)–(c), pinning the committed ruling as source W.
  Installed the model-free classifier and R0/R1 distinction; source-config-bound
  capture/consume custody with journal verification and refusal behavior;
  and the ruled CLI selector/rebind with unchanged anchor route and boundary
  requirements. Updated the adjacent stale unresolved/installation wording.
  All section headings remain, including Addendum FN; six unrelated sections
  are byte-identical to `262ff28a4`.
- Ed's R1 High Power A-B-A paragraph from `d93029c7e` is retained unchanged:
  exactly `pmset -c powermode 0` and `pmset -c powermode 2`, installed by Ed
  through the narrow sudoers rule; `sudo -n -l` verification, mode records
  before/after each segment, Automatic restoration on normal/error/signal
  exits, and refusal if restoration is unavailable.
- [answer.md](../../answer.md) and this existing report: replaced the blocked
  handoff with source verification, completed validation and remaining gates.

New protocol commit: `687257f35`,
`docs(align): install WP14 rulings in protocol v4`.
The subsequent handoff commit is named
`docs(align): complete WP20b handoff after source verification`.
Resolve both new commits with `git log --oneline 8c6e9f450..HEAD`.
Earlier `d93029c7e` (power wording) and `8c6e9f450` (source-blocked handoff)
remain intact; no history was rewritten.

Only the three documentation files above changed. RUN_STATE.md, TASK_QUEUE.md,
docs/process/state_kernel.json and tests/test_gen_state.py remain unchanged;
no kernel task was registered. No code, config, fixtures or raw evidence
changed. No child agents or consults were invoked; caller-owned invocation
capture is unchanged.

## Source verification and preservation

Read the execution plan's rulings/WP14/WP20 and appended Ed ruling, the
committed WP14 rulings, and the cited Window-1 survey's integration/R1/slot
and handoff details. The later WP14 and Ed rulings govern the replacements.
No absolute measurement path in those sources was followed.

Verified exact equality between
`a17ed96c8c68e81f3015d2722fc5e7a7ea1d26eb:docs/align/council-2026-11-05/WP14-RULINGS.md`
and `/private/tmp/jwsol/v4-wp14-rulings.md`. SHA-256:
`124d14285d0e42bd384b71336b346a500515b27e85d2f55687dbda95d82a2689`.
The pre-existing prepared patch therefore had committed authority; applied it,
clarified sanitization wording, formatted literal key patterns and registration
prose, and tightened three citation endpoints against the committed lines.
The legacy “Proposed location” / “Nothing was committed or pushed” prose in
that source does not describe its present Git availability; source bytes were
not altered here.

The current shared plan includes a later WP4b wall-time appendix. Verified
that `/private/tmp/jwsol/v4-wp20b-plan-pinned.md` is a byte-identical prefix of
the current `/private/tmp/jwsol/v4-plan-synth.md`, and retains the protocol's
existing SHA-256:
`528c5217a5e279192bfc69a055a2db8bd5be2c2427d1a3ff2d136b46872e7b9e`.
The existing P pin is unchanged. The temporary checker SHA-256 is
`cd6a3a072927a879c04a9baba938f03b12e60aee0478ab9a00a893bdf1298b72`.
These temporary validation artifacts are not promoted as project tooling.

## Verification and exact counts

Final offline document check, using committed sources without draft/candidate
flags:

```text
python3.13 -B /private/tmp/jwsol/v4-wp20b-doc-check.py docs/align/pilot_protocol_v4.md docs/run_reports/2026-11-05-align-v4-wp20b-protocol-rulings.md answer.md
```

PASS: **3 Markdown files; 6 local links; 128 citation ranges across 10 pinned
sources (9 Git sources plus the plan); 2 parsed reference-role forms;
0 PENDING-RULING blocks; 1 reserved Addendum FN; all section headings retained;
6 unrelated sections byte-identical**. Heading/fence/table/whitespace checks,
plan digest, exact gate-semantics preservation except its ruled introduction,
power-rule tokens and protected-file/write-scope checks also pass.

Manual final source/diff review checked the three replacements against WP14.
Citation-range validation checks availability and line bounds; it does not
certify implementation or substitute for the blind registration review.
That review tightened citations for the source-config serialization,
canonical JSON and journal-verification requirements. No numerical result
was produced or changed.

`git diff --check`, `git diff --cached --check` and
`git diff 262ff28a4..HEAD --check`: PASS.

Unit tests: **0 run, 0 skipped**. Native tests: **0 run, 0 skipped**. No full
suite or compileall was run: this is documentation only, and the user
prohibits the full suite while the analysis job is active. No MLX import,
model execution, measurement-data read, block-5 pipeline, hardware collection,
arm or external integration was attempted. The prior sandbox census denial
is historical; no process fixtures or census were launched on this continuation.

## Remaining gates and next exact step

No source blocker or new scientific ruling remains for WP20b. This work does
not close WP4c/WP15–WP17 implementation, R0/R1 native slots or custody tests,
WP21 desk conventions, or the blind Fable + Opus W1 registration gate.
Ed still installs the narrow sudoers rule; the lead verifies the driver's
actual restore guarantees. Existing capacity/Q4/Q6 and disk-reservation
items remain with their owners, as already stated in the protocol.

No native test is needed to validate this Markdown-only diff. The execution
plan's separate integration checks still require a pinned, Metal-visible Mac
outside this sandbox, one module at a time (not run here; no counts claimed):

```text
python3.13 -B -m unittest tests.align.test_cache_checkpoint_native
python3.13 -B -m unittest tests.align.test_r0_mlx_native
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx
JW_LIVE_HW=1 python3.13 -B -m unittest tests.align.test_smc_native
python3.13 -B -m unittest tests.align.test_decode_budget.DeadmanTests.test_mlx_evaluated_token_survives_alarm_during_disarm
```

MLX/Metal cannot execute in this sandbox. Readiness, sensor behavior, native
identity and sudo restoration remain unverified here; no skip is called a
pass. Next: the lead reviews/integrates these new commits with WP14 and the
implementation lanes, runs the applicable native checks outside the sandbox,
and completes registration/live gates before arming the relevant window.
