# VERDICT: FAIL

The four ranked elements are present together structurally at `3df8777`, and both focused and canonical suites pass. However, direct probes reproduced four safety failures, and the witness gate contains prohibited false-positive proof shapes.

## P1 — Acceptance-blocking findings

1. **Public audit commands authorize ARM without holding or checking the writer lease.**  
   [`audit`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/recover_calibration_ledger.py:232), [`audit-observations`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/recover_calibration_ledger.py:264), and [`validate-slot`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/recover_calibration_ledger.py:349) emit `terminal_result:"ready_to_arm"` outside the enforcing lease path.  
   **Reproduced scenario:** while another process held `CalibrationWriterLease`, a fresh `audit` returned exit 0 and `ready_to_arm`. This is the expressly prohibited **inspect-as-permission** shape and was introduced in round 3.

2. **Aliased ledger paths can acquire concurrent writer leases.**  
   [`_ledger_lock_path`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:2552) derives the lock filename lexically, while the in-process key uses `.absolute()` rather than resolving ledger identity.  
   **Reproduced scenario:** a real `ledger.jsonl` and a symlink to the same inode simultaneously acquired distinct `CalibrationWriterLease`s. Canonical FDs are non-inheritable, and stale PID metadata is not trusted, but lock-path selection fails the one-lease-per-ledger invariant.

3. **Enforcing POST readiness can authorize ARM after PRE custody corruption.**  
   Readiness loads the snapshot with `verify_custody=False` and checks only the upcoming slot’s custody at [`calibration_ledger.py:4135`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:4135) and [`:4172`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:4172).  
   **Reproduced scenario:** finalize PRE, delete PRE’s manifest, then run enforcing pre-slot readiness for POST under the lease. Result: `authorizes_arm:true`; a custody-verifying load of the same ledger reports `calibration_ledger_custody_invalid`.

4. **Sessionless guarded pin advancement admits an ordinary pending business head.**  
   [`advance_calibration_head_pin`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:4305) checks physical-ahead, exact historical pin membership, and absence of an open bracket, but does not require a recovery-only control tail or reject remaining snapshot refusals.  
   **Reproduced scenario:** append a normal pending reservation after the pinned head; sessionless dry-run advancement accepts its exact head even though the snapshot still reports `ledger_pending` and `ledger_head_mismatch`.

5. **The crash matrix names all required stages but does not execute several real crash boundaries.**  
   The matrix labels trace/evidence/manifest stages partial at [`test_calibration_writer_crash_matrix.py:74`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_writer_crash_matrix.py:74), but its subprocess projection creates one generic partial fixture and manually calls the hook at [`:397`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_writer_crash_matrix.py:397). It therefore does not crash during the corresponding production writes.  
   **Reproduced omitted boundary:** a torn manifest (`"{"`) is reported by `session-status` as complete/resumable; `resume-finalize` then hard-stops with `calibration_custody_unreadable`, while abort refuses because custody is supposedly complete. The state has a named hard-stop, but the mandatory fresh-process “during manifest write” witness is absent and its registry `prior_crash_reachable` classification is inaccurate.

6. **Per-class exact-set gates pass despite unexecuted terminal proofs.**  
   For every `NIGHT_STOPPED_PRESERVED` row, the test runs only `explain`, then assigns the terminal result locally at [`test_calibration_exits.py:1676`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:1676). Most `READY_TO_ARM` rows execute generic `audit`, not their registered correction command, at [`:1751`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:1751). This is the prohibited **unexecuted proof reference** shape.

## P2 — Design/contract defects

- **Round-3 malformed-intent admission is design-ambiguous.**  
  [`_control_state_admits`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:1230) now admits authenticated intents with invalid target schemas so repair can raise a typed refusal. The append contract still says an admitted intent must commit a valid target schema. This is a material parser-policy change beyond witness plumbing and needs an explicit ruling/contract amendment.

- **Historical positional fixtures remain.**  
  [`test_powermetrics_fiducial.py:1017`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_powermetrics_fiducial.py:1017) asserts `receipts[1]`, `receipts[3]`, and a hard-coded count of four rather than selecting receipts semantically.

## Four ranked elements

- **Stable claim ID + lease:** landed together. The durable claim ID is domain-separated and deterministic; no per-process UUID participates in bracket idempotency. The normal writer holds the kernel lease across countdown, capture, finalization, and abort, and `abort-session` refuses under a live holder. **Not complete because aliases defeat lease exclusivity.**
- **Fresh-process recovery:** landed. Night-path `session-status`, `resume-finalize`, and `abort-session` derive state from the ledger, pin, plan, and custody; `PRE_CAL_DIR`/latest-directory discovery is gone.
- **Operation/phase readiness:** landed, including under-lease ENFORCING, `needs_pin_commit`, guarded advancement, and test-only uncommitted-pin bypass. **Not sound because prior-slot custody can be ignored and standalone audit commands authorize ARM.**
- **Registry/executed witnesses/docs:** tri-state registry, coded refusals, AST checks, exact per-class sets, §5/§6/§10 amendments, §13 deletion, and fresh narrowed projection are present. **Not complete because the execution gate proves some exits only by local assignment or unrelated `audit`.**

## Round-3 production-change audit

Design-dictated:

- Open-session refusal now precedes pin mismatch at [`calibration_ledger.py:4151`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:4151).
- Terminal pin derivation discards the stale open-session marker only after reconstructing terminal state at [`:3909`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:3909).
- Conflicting bracket-session corruption is preserved as a hard-stop rather than offered abort; claim/finalization-only impossible public states are classified as internal invariants at [`calibration_exits.py:348`](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_exits.py:348).
- Abandonment failures now map to coded `ABANDON_NOT_CLEAN`.

Beyond or ambiguous relative to witness necessity:

- The three public `ready_to_arm` audit routes introduce unsafe production authorization.
- Malformed-intent admission changes parser semantics without matching contract authority.

## Prohibition-list result

**Not clean.** Present:

- inspect-as-permission;
- unexecuted proof references.

Absent:

- isolated claim-ID patch;
- contract-only table;
- reflection-as-census;
- random-token fail-fast;
- abort under a live lease;
- production uncommitted-pin override;
- §13 not-in-force procedures.

## Same-signature answer

**YES — positional fixtures remain.**

- Ungoverned refusal without registered governed exit: **NO**
- Bare-business-receipt admission: **NO**
- Count-only pin check: **NO**; physical-chain membership compares exact sequence and digest
- Positional fixtures: **YES**, evidence above

Checks performed: `git diff --check` passed; focused recovery/ledger suite **118 passed**; canonical suite **2,765 passed, 90 skipped**; direct fresh-process lease, alias-lock, custody-readiness, pin-advancement, and torn-manifest probes performed. No files were edited; worktree remained clean.