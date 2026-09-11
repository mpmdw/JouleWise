# Verdict: FAIL

The corpus is green but not witness-complete. It proves code reachability, yet several families do not prove the declared governed exit, the crash matrix does not execute the production command path, and two of five `internal_invariant` classifications are demonstrably reachable from durable state.

This branch should remain non-merge/non-ARM-eligible.

## P1 findings

### 1. Hard-stop preservation is asserted, not witnessed

All 21 corruption backstops and 18 operational `night_stopped_preserved` cases take the same shortcut: after observing the refusal, the harness runs `explain <code>`, checks its registry-projected `exit_id`, and assigns the terminal result locally. It never hashes or reopens the ledger, lock, journal, custody, or pin bytes to prove preservation.

Evidence: [tests/test_calibration_exits.py:1676](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:1676>).

Broken implementation admitted: a refusal handler that truncates the malformed ledger, deletes custody, or replaces the lock inode while still emitting the correct code would pass all 39 cases.

Family verdicts:

- Corruption construction: PASS — hostile durable bytes are legitimate and generally reach the intended production parser.
- Corruption terminal result: FAIL — preservation is never observed.
- Operational hard-stop/guarded-pin terminal result: FAIL — even rows whose mapped route is `advance-head-pin` execute only `explain`.

### 2. Most `ready_to_arm` exits test an unrelated clean-ledger audit

There are 15 `correct-preflight` witnesses. Only `PRE_RESERVE_NOT_READY` and `PRE_SLOT_NOT_READY` receive state-specific correction. The other 13 run plain `recover ... audit` against the fixture ledger and interpret its `status: ready` as proof that the original writer/reservation defect was corrected.

Evidence: [tests/test_calibration_exits.py:1751](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:1751>).

Affected examples include malformed reservation input, plan unreadability/hash mismatch, terminal readiness, all writer-argument/protocol/rederive refusals, quiet-machine authorization, and power policy.

Broken implementation admitted: `validate_powermetrics_fiducial.py` can remain permanently unusable after adding the missing `--allow-live`, power policy, output, or protocol correction; the unrelated empty-ledger audit still returns ready.

### 3. Three writer-failure witnesses are pre-aborted by their constructor

The display-arm, sampler-never-ready, and rollover-timeout constructors directly append the abort before observing the refusal. The observer is the recovery CLI’s `session-refusal` decoder, not the real writer path. The subsequent `abort-session` is merely idempotent against the already-terminal session.

Evidence: constructors at [tests/test_calibration_exits.py:926](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:926>), observer at [tests/test_calibration_exits.py:1540](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:1540>).

Broken implementation admitted: the real writer can emit the right refusal while failing to append its automatic abort—or never reach the refusal at all—and these tests still pass.

### 4. `abandon-tail-then-repair` never performs the “then repair”

The witness runs `abandon-tail`, checks that its returned inspection says clean, and stops. The runbook explicitly requires `abandon-tail`, then `repair`.

Evidence: [tests/test_calibration_exits.py:1684](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:1684>) versus [window_runbook.md:851](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/docs/phase_2/window_runbook.md:851>).

Broken implementation admitted: repair can fail specifically after a valid abandonment receipt, although the declared composite exit still passes.

### 5. The stage crash matrix patches and manually reenacts the component

The principal stage test launches `python -c`, imports `_CaptureLedgerLifecycle`, replaces `writer._writer_stage`, writes synthetic partial/complete custody, and manually fires several stage markers. It does not launch the runbook’s `validate_powermetrics_fiducial.py` command.

Evidence: [tests/test_calibration_writer_crash_matrix.py:345](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_writer_crash_matrix.py:345>).

The append-boundary matrix likewise replaces `_write_ledger_append_payload` and `_after_ledger_fsync`: [tests/test_calibration_writer_crash_matrix.py:530](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_writer_crash_matrix.py:530>).

Broken implementations admitted:

- The public writer can omit or misorder a supervisor-stage call while the test manually fires it.
- Argument parsing, default paths, preflight ordering, exception handling, and CLI-to-lifecycle wiring can break without the stage matrix noticing.
- The real reservation CLI can diverge because reservation stages call `append_bracket_session_receipt` directly rather than running `reserve_calibration_window_bracket.py`.

### 6. Finalized-stage cases do not execute a fresh governed exit

For `projection == "finalized"`, the test derives a local string from `session_state` and merely asserts that it belongs to a two-value set. No `terminal-pin`, `session-status`-directed dispatch, readiness, or other mapped terminal action is executed.

Evidence: [tests/test_calibration_writer_crash_matrix.py:875](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_writer_crash_matrix.py:875>).

Broken implementation admitted: terminal-pin derivation or post-finalization recovery can be completely broken while these stages remain green.

## Internal-invariant rulings

### `calibration_ledger_snapshot_required` — UPHELD

Strongest attack: corrupt or omit ledger/pin/acceptance bytes so the evaluator receives no usable snapshot.

Why it fails: current production consumers explicitly load a snapshot before evaluation; malformed durable state produces a snapshot carrying refusal reasons, while invalid acceptance bytes refuse earlier. `AuthenticatedConsumptionSession` also loads a snapshot when none is supplied.

Evidence: [whole_window.py:416](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/whole_window.py:416>), [run_campaign.py:4070](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/run_campaign.py:4070>), guard at [calibration_bracketing.py:1116](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_bracketing.py:1116>).

### `calibration_ledger_off_ledger_artifact` — UPHELD

Strongest attack: add a valid-looking custody directory not registered in the ledger, or delete a registered custody member.

Why it fails: the public path derives candidates solely from the authenticated snapshot. Extra directories are ignored; missing/invalid registered custody becomes `calibration_ledger_custody_invalid` before the exact-set guard.

Evidence: [calibration_bracketing.py:1693](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_bracketing.py:1693>) and [calibration_bracketing.py:1237](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_bracketing.py:1237>).

### `calibration_ledger_bracket_slot_claimed` — UPHELD

Strongest attack: write a second valid claim receipt for the same slot.

Why it fails: durable duplicates become `calibration_ledger_bracket_session_conflict` during reconstruction; an exact completed operation returns idempotently before `build`; a mismatching completed target takes the configured conflict route. The focused unit test reaches this guard only by replacing `_locked_append`, appropriately demonstrating that it is internal.

Evidence: parser at [calibration_ledger.py:1492](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:1492>), idempotent interception at [calibration_ledger.py:3388](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:3388>), unit injection at [tests/test_calibration_exits.py:378](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:378>).

### `calibration_claim_id_invalid` — MISCLASSIFIED

A valid open session plus an authenticated claim target containing a nonempty but non-policy claim ID is accepted as durable shape. Public pre-slot readiness compares it with the stable ID and emits `calibration_claim_id_invalid`.

Evidence: claim shape validates only nonempty text at [calibration_ledger.py:791](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:791>); durable conflict classification occurs at [calibration_ledger.py:4191](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:4191>).

I constructed that state and invoked the public recovery CLI. It returned exit 2 with:

```json
{"code":"calibration_claim_id_invalid","exit_id":"internal-invariant","next_command":""}
```

Thus durable hostile state reaches a public refusal, but the code has been removed from executed witnesses and operator exits.

### `calibration_finalization_binding_conflict` — MISCLASSIFIED

The public writer reserves planned bindings, then after capture replaces the lifecycle bindings using device metadata parsed from durable powermetrics bytes. A corrupted or discrepant raw record can therefore differ from the reserved binding and reach the finalization guard.

Evidence: runtime binding replacement at [validate_powermetrics_fiducial.py:1047](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/validate_powermetrics_fiducial.py:1047>), public finalization at [validate_powermetrics_fiducial.py:1133](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/validate_powermetrics_fiducial.py:1133>), raise site at [calibration_ledger.py:3773](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:3773>).

The focused unit test supplies wrong in-memory arguments, but does not refute this durable public-writer path: [tests/test_calibration_exits.py:412](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:412>).

## Stage-to-production mapping: FAIL

The real night path is:

- readiness and reservation: [window_runbook.md:509](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/docs/phase_2/window_runbook.md:509>)
- writer invocation: [window_runbook.md:592](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/docs/phase_2/window_runbook.md:592>)
- recovery/status/resume/abort: [window_runbook.md:862](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/docs/phase_2/window_runbook.md:862>)

Divergences:

- The stage matrix never runs the production writer CLI.
- Reservation stage crashes exercise a direct library append, not the reservation CLI.
- `BEFORE_POST_DISPATCH` and the supervisor markers are manually invoked.
- The exact-set cross-product requires impossible stage/slot pairs: “before-post-dispatch/pre,” post-terminal stages on PRE, and pre-finalization supervisor stages on POST. Production guards those markers by slot at [validate_powermetrics_fiducial.py:621](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/validate_powermetrics_fiducial.py:621>) and [validate_powermetrics_fiducial.py:1149](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/validate_powermetrics_fiducial.py:1149>).
- Witness observers `audit`, `audit-observations`, `validate-slot`, and `session-refusal` are not the §5/§6/§10 production command sequence. In particular, `validate-slot` and `session-refusal` can remain correct while the actual writer path is broken.

## End-to-end spot checks

| Witness | Result |
|---|---|
| malformed ledger | Correct durable constructor and public refusal; terminal preservation not checked |
| recovery-required crash | Strong: real failed child, durable intent, public refusal, fresh repair |
| orphaned tail | Correct refusal; declared “then repair” incomplete |
| complete custody | Good fresh `resume-finalize` reachability; durable post-state assertion could be stronger |
| partial custody | Fresh abort succeeds, but custody preservation is trusted from returned JSON |
| live writer contention | Exemplary: live holder, public refusal, SIGKILL, fresh resume |
| pre-reserve-not-ready | Exemplary corrective sequence: abort, guarded pin advancement, commit, fresh readiness |
| quiet-Mac authorization | Exact writer refusal; unrelated audit used as terminal correction |
| display/sampler/rollover | Not valid writer witnesses; exit was pre-armed by constructor |
| claim-ID conflict | Durable public-CLI counterexample proves misclassification |

## Exemplary work

Credit is due for:

- The exact-set gate actually executes cases rather than trusting `witness_id`: [tests/test_calibration_exits.py:180](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:180>).
- Corruption constructors generally use durable bytes without process patching.
- The live-writer two-process case is a genuine public refusal and fresh-process recovery: [test_calibration_writer_crash_matrix.py:669](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_writer_crash_matrix.py:669>).
- The recovery-required witness uses a genuine kernel-enforced failed append rather than a function mock: [tests/test_calibration_exits.py:796](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:796>).

Checks performed: verified clean branch/head; read ruling and adopted consult from `main`; traced registry, constructors, public scripts, ledger guards, runbook commands, and 10 witnesses; ran `python3 -m unittest tests.test_calibration_exits tests.test_calibration_writer_crash_matrix` — 14 tests, 90.380s, OK; executed the durable claim-ID public-CLI counterexample; final worktree remained clean.