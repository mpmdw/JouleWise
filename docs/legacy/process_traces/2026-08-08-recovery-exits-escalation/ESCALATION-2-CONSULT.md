```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt five terminating contracts: executed public-surface evidence, dual slot/object lease identity, pre-handler preservation, owned process groups plus double-keyed crash hooks, and receipt-provenance enforcement.",
  "workspace": {
    "base_requested": "721593b",
    "base_mode": "exact",
    "head_start": "721593b52611e79d53f799d96018ce2fa7f6d333",
    "head_end": "721593b52611e79d53f799d96018ce2fa7f6d333",
    "upstream_end": "721593b52611e79d53f799d96018ce2fa7f6d333",
    "branch": "impl/d117-ledger-recovery"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "ADOPT_FIVE_TERMINATING_CONTRACTS",
    "findings": [
      {
        "id": "FIX-14",
        "severity": "blocker",
        "question": "Q1",
        "title": "Corrective witnesses must carry runner-created evidence of the registered public surface"
      },
      {
        "id": "FIX-15",
        "severity": "blocker",
        "question": "Q2",
        "title": "Writer lease identity must conflict on pathname slot or ledger object identity"
      },
      {
        "id": "FIX-16",
        "severity": "blocker",
        "question": "Q3",
        "title": "Every hard-stop fingerprint must precede its first refusal handler"
      },
      {
        "id": "FIX-17",
        "severity": "blocker",
        "question": "Q4+Q6",
        "title": "One owned-process runner must provide reaping and double-keyed real-site crashes"
      },
      {
        "id": "FIX-18",
        "severity": "should_fix",
        "question": "Q5",
        "title": "Receipt indexing must be prohibited by collection provenance, not identifier spelling"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse @{upstream} && git diff --check && git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/d117-ledger-recovery...origin/impl/d117-ledger-recovery",
          "721593b52611e79d53f799d96018ce2fa7f6d333",
          "721593b52611e79d53f799d96018ce2fa7f6d333"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "impl/d117-ledger-recovery.*721593b52611e79d53f799d96018ce2fa7f6d333"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a read-only design consult; the dictated contracts were not implemented or executed.",
      "needs": "The fix session must run the named mutations, focused suites, survivor gate, and canonical suite."
    }
  ]
}
```

## Findings

The five-contract numbering is intentional: Q4 and Q6 are one defect boundary. Crash authorization without process ownership still leaks descendants; process ownership without authorization leaves ambient production crashes armed.

### FIX-14 — Q1: executed corrective-surface evidence

Verdict: adopt a corpus-level execution ledger. An assertion that calls `calibration_readiness()` directly is not evidence that the writer works. Nor is a dictionary saying a subprocess ran. The evidence must be created by the same harness object that actually starts and waits for the public process.

Exact dictated closure:

> **FIX-14 — Corrective witnesses execute the registered public surface.** Extend every registry row with `exit_id == "correct-preflight"` with a machine-readable `correction_surface` and `corrected_success` predicate; do not change any `witness_class`. Each corresponding witness MUST execute that surface through the shared owned-process runner after applying its correction. The runner, not the witness, creates immutable `PublicExecutionEvidence` containing the refusal code, registered surface, resolved entry-point path, exact argv, cwd, PID/PGID, start/end ordering, return code, stdout/stderr digests, parsed structured events, and durable postcondition. Direct construction of this evidence outside the runner is forbidden by AST gate.
>
> For `calibration_writer_bracket_arguments`, `calibration_quiet_mac_auth_required`, and `calibration_power_policy_required`, the corrected surface is the real `scripts/validate_powermetrics_fiducial.py` CLI with the complete corrected session/slot/attempt tuple, `--allow-live`, power policy, and process-level fake sampler/identity fixtures. No writer function may be called directly and no writer decision may be monkeypatched. The writer MUST pass its real enforcing readiness check while holding the lease, emit a structured `calibration_writer_arm_authorized` event before claim/countdown/capture, complete the accelerated fixture capture, exit 0 with `status: valid`, and leave `session-status` reporting the exact slot finalized.
>
> Corrected writer rederive rows MUST first execute the corrected writer rederive CLI to exit 0 with an authenticated valid output. If their registry terminal remains `ready_to_arm`, the witness MUST then execute the real bracket writer and capture its under-lease authorization event; direct readiness is not a substitute. Corrected reservation rows MUST execute the real reservation CLI with `--execute`, capture its under-lease pre-reserve authorization event, and require exit 0 with `status: reserved`. State-readiness rows MUST execute their real public phase surface; `TERMINAL_NOT_READY` additionally executes `terminal-pin`. Public diagnostic readiness may corroborate state but cannot satisfy the surface obligation by itself.
>
> Add `test_every_corrective_witness_executes_registered_public_surface`, enumerating expected rows from `REFUSAL_INVENTORY` and requiring exact key equality with execution evidence. For each row, require at least one runner-created record whose resolved entry point equals `correction_surface` and whose observed outcome satisfies `corrected_success`. Add an AST gate that forbids raw writer/reservation `subprocess.run`/`Popen`, direct `PublicExecutionEvidence(...)`, and direct `calibration_readiness()` as a terminal proof inside the witness executor.
>
> **Discriminating regression:** in a temporary copy, mutate the real writer’s `--allow-live` branch to refuse unconditionally. `calibration_quiet_mac_auth_required` MUST fail because its writer record returns refusal, emits no under-lease authorization event, and never finalizes the slot. A witness that retains the current direct `_enforcing_readiness()` shortcut MUST fail the corpus meta-test with “missing registered writer execution”.

This is enforceable without monkeypatching: the harness already owns subprocess creation. The AST gate closes fabricated records and bypass launches; the runtime exact-set gate closes omissions and renamed helpers.

### FIX-15 — Q2: lease identity

Verdict: reject the premise that one key suffices. Ledger-inode identity closes hard-link aliases but loses replacement continuity; parent/name identity closes replacement continuity but misses hard links. The terminating identity is a pair of independently conflicting identities.

Exact dictated closure:

> **FIX-15 — Writer leases conflict on canonical pathname slot OR ledger object.** Replace `_lease_key` and independently derived lock paths with one `resolve_ledger_lease_identity()` function returning:
>
> 1. `slot_key = (canonical_parent.st_dev, canonical_parent.st_ino, canonical_basename)`, after resolving symlinks, opening the canonical parent directory, and validating the basename through that directory descriptor; and
> 2. `object_key = (ledger_fd.st_dev, ledger_fd.st_ino)` when the ledger exists and is a regular file.
>
> A lease conflicts when either key overlaps a held lease. The in-process registry, nested-lock reuse, on-disk acquisition, diagnostics, and release MUST all consume this same identity object. The lease instance caches its acquired keys and descriptors; release MUST NOT recompute identity from a path that may have been replaced.
>
> Acquire the permanent canonical slot sidecar first. Open it dirfd-relative with `O_NOFOLLOW`, require a dedicated regular inode with link count one, and never delete it. For an existing ledger, also open the ledger itself and take a nonblocking `flock` on that ledger inode. The ledger inode is the object lock; do not synthesize another alias-sensitive object-lock pathname. Consequently, symlink aliases share the slot lock, hard-link aliases share the ledger-inode lock, and replacement at the same pathname remains excluded by the slot lock.
>
> For a not-yet-existing ledger, acquire the slot lock only and do not create a ledger merely to inspect or refuse it. The sole genesis-bootstrap creation path MUST create a temporary inode in the canonical parent, lock its descriptor before publishing it, atomically publish it as the ledger, then add its object key to the held identity before any append. Every first-ledger creation MUST use that upgrade path; ordinary append code may not create the ledger independently.
>
> Before every durable append, verify that the current canonical path still resolves to the cached object key. If the pathname was replaced while the lease was held, hard-stop before writing to the replacement. After release, a new lease may acquire the replacement inode normally.
>
> Refuse network/remote filesystems unless the platform can affirm local advisory-lock and atomic-rename semantics. Do not claim cross-host exclusion from `flock`; unsupported or indeterminate filesystem capability is `calibration_unsafe_lock_inode`.
>
> Add regressions for: symlink alias contention; hard-link alias contention; two distinct ledger inodes acquiring concurrently; acquire-release-reacquire; missing-ledger slot contention plus locked genesis upgrade; and replacement-in-place where the second same-path lease refuses while the first is held, the first refuses to append to the replacement, and the replacement becomes acquirable only after release.
>
> **Discriminating regressions:** the current realpath-only implementation MUST fail the hard-link case; an inode-only replacement MUST fail the replacement-in-place case; the former lexical implementation MUST fail the symlink case. Legitimate distinct ledgers and release-reacquire MUST remain green.

For hard links that have already diverged through replacement into two different inodes, they are now different ledgers; historical alias ancestry is neither portable nor observable and must not be invented as identity.

### FIX-16 — Q3: preservation span

Verdict: every hard stop uses the same guard, with no code exclusions. `FINALIZATION_BINDING_CONFLICT` needs a two-invocation construction so legitimate capture writes happen before the preservation boundary and its first refusal happens after it.

Exact dictated closure:

> **FIX-16 — Hard-stop preservation begins before the first target refusal handler.** Define the expected preservation set directly as all non-`internal_invariant` registry rows whose terminal result is `night_stopped_preserved`. Every such witness MUST execute inside one `PreservationGuard`. The guard captures the complete durable fingerprint before launching the target refusal surface, records the runner execution’s start/end ordering, captures the fingerprint again after it exits, and requires byte/identity equality. No code-specific exclusion, deferred baseline, alternate terminal code, or baseline assignment inside a refusal branch is permitted.
>
> The fingerprint MUST cover presence/absence, file type, device/inode/link identity, and bytes for the ledger, head pin, canonical slot lock, current ledger object identity, legacy journals, custody members, and relevant durable directories. The guard’s evidence MUST prove `before_fingerprint < public_process_start < public_process_end < after_fingerprint`.
>
> Rebuild `calibration_finalization_binding_conflict` as a two-invocation witness. Invocation one runs the real writer with corrupted authenticated device metadata and an authorized real-site SIGKILL at `ARTIFACTS_COMPLETE_BEFORE_FINALIZATION`. It must die by SIGKILL and its process group must be reaped. That construction may legitimately create the claim and complete custody, but it emits no target refusal. Capture the preservation baseline only after that crash is fully contained. Invocation two runs the fresh public `resume-finalize` CLI. Distinguish an authenticated evidence-binding mismatch from structurally unreadable custody: the former MUST emit exact `calibration_finalization_binding_conflict` before any claim/finalization append; malformed/hash-invalid custody remains `calibration_custody_unreadable`. Fingerprint again immediately after that refusal.
>
> Add `test_every_hard_stop_has_pre_handler_preservation_evidence`, requiring exact-set equality between the registry-derived preservation set and evidence carrying both fingerprints plus the ordered public execution. The gate MUST fail if any code is excluded, if a baseline is captured after process start, or if the observer’s refusal is replaced by a later alternate code.
>
> **Discriminating mutation:** in a temporary copy, make the fresh `resume-finalize` binding-conflict refusal path overwrite or truncate `manifest.json` immediately before raising/emitting `calibration_finalization_binding_conflict`. The finalization-conflict witness MUST fail its byte fingerprint. The same guard structure means an equivalent refusal-handler mutation in any hard-stop row also fails without another per-code formulation.

This preserves the witness-scope ruling: hostile durable construction remains legitimate, but the first refusal and mapped exit remain real public subprocess actions.

### FIX-17 — Q4 and Q6: process ownership and R-FIX9

Q4 verdict: use one process-owning runner for all writer/crash subprocesses. The writer’s self-SIGKILL is the observed result; descendant cleanup happens afterward.

Q6 verdict: keep `_writer_stage` at every real production boundary, but require an ambient selector and a separately supplied harness capability.

Exact dictated closure:

> **FIX-17 — Owned process groups and double-keyed real-site crash authorization.** Route every writer and reservation subprocess used by the witness corpus or crash matrix through `OwnedPublicProcessRunner`. It MUST use `Popen(..., start_new_session=True)`, record `pgid == child_pid`, register cleanup immediately, communicate/wait for the direct child, preserve its original return code, then tear down the entire group in `finally`: send `SIGTERM`, poll for group disappearance for a bounded grace interval, send `SIGKILL` if needed, and poll until `killpg(pgid, 0)` reports `ESRCH`. Cleanup runs after success, assertion failure, timeout, or real writer SIGKILL.
>
> A real crash-stage case MUST still assert the direct writer/reservation child returned `-SIGKILL`. Group teardown may kill a surviving sampler only after that return code is captured. The production writer is not responsible for reaping descendants after killing itself.
>
> Maintain a module-global registry of every owned PGID. Module cleanup, executed after the witness/crash module’s tests, MUST fail the unittest suite if any owned group remains, while still killing it. Add an AST gate forbidding direct launches of either public writer script outside `OwnedPublicProcessRunner`.
>
> Keep every existing `_writer_stage` call at its real production boundary. Add a hidden, no-default `--test-writer-crash-authorization PATH` argument to both public entry points. The harness creates a one-use mode-0600 regular authorization file under its temporary root, outside production config search paths, containing a schema version, cryptographic nonce, exact stage, resolved entry point and digest. It supplies the path explicitly and supplies a matching nonce as `JOULEWISE_TEST_WRITER_CRASH_TOKEN`. Startup opens the file with `O_NOFOLLOW`, verifies regular-file type, current-user ownership, restrictive mode, stage, entry point, digest, and constant-time nonce equality, consumes/unlinks it, and only then records an authorized crash stage.
>
> `_writer_stage(stage)` sends real `SIGKILL` only when both logical keys agree: `JOULEWISE_TEST_WRITER_CRASH_STAGE == stage.value` AND a validated harness capability authorizes that same stage and entry point. Environment values alone—including both ambient crash environment variables without the explicit capability argument—are inert.
>
> When `JOULEWISE_TEST_WRITER_CRASH_STAGE` is present without valid authorization, the ordinary invocation MUST continue normal behavior without crashing and surface exactly one structured stderr diagnostic: `{"event":"joulewise_test_writer_crash_hook_inert","reason":"missing_or_invalid_harness_authorization","requested_stage":"..."}`. It is a diagnostic event, not a refusal code and not ARM permission. Fresh recovery commands MUST use a sanitized environment with neither crash key.
>
> Add a standing post-module survivor assertion and `test_survivor_guard_detects_spinning_descendant`: an isolated synthetic owned group with a spinning child must be reported as a survivor, then reaped by test cleanup. As mutation acceptance, removing the runner’s group teardown from one crash witness MUST make the focused suite fail with the surviving PGID.
>
> Add R-FIX9 regressions: (a) every applicable matrix stage runs the actual reservation/writer command with both keys, the direct child returns `-SIGKILL`, and fresh recovery reaches the already-registered outcome; (b) a valid ordinary writer fixture with `JOULEWISE_TEST_WRITER_CRASH_STAGE=before-writer-lease` but no capability argument does not return `-SIGKILL`, emits the inert diagnostic, and proceeds to its normal success or governed refusal.
>
> **Discriminating implementations killed:** the current plain-`subprocess.run` harness fails the survivor gate; a witness that leaks a spinning child fails module cleanup; the current environment-only `_writer_stage` fails ambient inertness; moving SIGKILL back into manual harness marker firing fails the real-site matrix.

This is the required composition of R-FIX9, not a compromise between its halves.

### FIX-18 — Q5: positional receipt detection

Verdict: variable-name linting is unsalvageable. Use a receipt-collection type that has no positional access, backed by a provenance gate that prevents raw aliases from escaping it.

Exact dictated closure:

> **FIX-18 — Positional receipt addressing is unrepresentable and provenance-checked.** Introduce a test-fixture `ReceiptCorpus` abstraction for every receipt-bearing collection in calibration tests. It supports iteration, length, semantic filtering, exact semantic selection, and semantic replacement, but defines no integer or slice `__getitem__`. Migrate all fixture producers and helper return values that carry receipt rows to `ReceiptCorpus` or explicitly annotate them as receipt collections before wrapping. Replace positional mutation with semantic selectors such as event/session/slot/attempt/schema predicates.
>
> Add an interprocedural AST provenance gate over `tests/test_calibration*.py` and `tests/test_powermetrics_fiducial.py`. Seed receipt-collection provenance from `.receipts`, annotated receipt-producing helpers, ledger-scan/decoder results, and `ReceiptCorpus`. Propagate it to fixed point through assignment, attributes, `copy`/`deepcopy`, `list`/`tuple`/`sorted`, comprehensions, filtering, helper returns, and aliases. Flag every subscript whose base is a receipt collection, independent of variable name or index spelling. Also fail any helper returning a receipt-bearing collection without the receipt-corpus annotation/wrapper.
>
> The current `business_rows[1:]` MUST be reported because the comprehension derives from receipt rows. The current `marker_removed[1]` MUST be reported because `deepcopy(self.receipts)` preserves receipt provenance. Renaming either variable MUST not change the result.
>
> The gate MUST NOT report string-key access on one receipt row, iteration-order assertions such as `[row["event"] for row in corpus]`, `next(...)` with a semantic predicate, `ReceiptCorpus.one(...)`, or indexing of proven non-receipt sequences. There is no legitimate integer/slice indexing of a receipt collection; legitimate ordering assertions use iteration and derived semantic subsets.
>
> Add analyzer self-tests containing renamed and deep-copied unsafe snippets plus safe row-key, iteration-order, and non-receipt-index snippets; then run the analyzer over the complete calibration-test corpus.
>
> **Discriminating implementation:** the current identifier-substring lint MUST fail its analyzer mutation tests and both delta sites; the new provenance gate must flag both without consulting any identifier spelling.

### Sequencing ruling

Use one implementation session, with one shared harness design. Splitting Q1, Q3, Q4, and Q6 would recreate inconsistent evidence and cleanup paths.

Implement in this order:

1. FIX-17: owned runner, crash capability, survivor guard.
2. FIX-15: dual lease identity.
3. FIX-16: universal preservation guard and two-invocation binding conflict.
4. FIX-14: correction-surface registry fields, real writer executions, corpus meta-gate.
5. FIX-18: receipt corpus and provenance analyzer.

Then run the named mutations, focused witness/crash/ledger/calibration suites, post-suite survivor assertion, and unpiped canonical suite. Internal commits may separate these phases for review, but they remain one dictated fix round followed by one fresh delta.

### What the fix session must not touch

- Any `witness_class` assignment or the operational/corruption-backstop/internal-invariant definitions and per-class exact-set ruling.
- CH-1, including the exact `PREFLIGHT_SYSTEMATIC_SCREEN_S` scalar.
- The D-117 §5/§6/§10 runbook amendments or the deletion of the §13 copy.
- The eleven closures already graded implemented, except strictly necessary adaptation at their shared runner/lease seams.
- Diagnostic-route inertness: `audit`, `audit-observations`, `validate-slot`, and public readiness remain non-authorizing.
- Malformed-intent quarantine, all-finalized-session custody verification, recovery-shaped pin advancement, real writer failure witnesses, composite abandon-then-repair, torn-manifest custody behavior, and existing stage/slot applicability.
- The `WriterStage` real-site boundaries; no return to manual marker firing or monkeypatched writer paths.
- Any production uncommitted-pin override, lock-inode deletion, live-holder abort, claim scalar, or fixture-as-hardware claim.
- `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/decision_log.md`, and `docs/council_log.md`.

Checks performed: full ordered record/contract read; implicated code and historical adopted witness-scope ruling inspected; branch/head/upstream and clean diff verified; no leaking crash suite executed during this read-only consult.

## Residual risk

The proposed local-filesystem rejection needs macOS and CI-specific capability tests; no portable `flock` design should claim distributed network-filesystem exclusion. The contracts themselves remain unexecuted until the dictated fix session and fresh delta.