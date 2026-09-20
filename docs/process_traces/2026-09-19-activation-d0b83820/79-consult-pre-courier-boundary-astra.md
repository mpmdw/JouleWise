```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Amend the proposal: guard all optional preparation, carry diagnostics inline, serialize repair with a real lock, and qualify the literal launch guarantee.",
  "workspace": {
    "base_requested": "df5c483e",
    "base_mode": "exact",
    "head_start": "df5c483e01f85a8f4e35a0c3d076551300616d4b",
    "head_end": "df5c483e01f85a8f4e35a0c3d076551300616d4b",
    "upstream_end": "6032b9e93220f9c9b9a04ca6d1dc75aa4aa92942",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "title": "The delivery boundary must include all optional preparation through argv construction",
        "detail": "Result inventory, refusal/result persistence, durable publication, logging, heartbeat reset, and prompt loading can prevent Popen. The artifact-hashing defect predates Stage A, including receipt.json, chain.exited, and courier.sent."
      },
      {
        "id": "R2",
        "severity": "should_fix",
        "title": "Evidence repair must execute only after courier-lock acquisition",
        "detail": "Replayed the existing concurrent-refusal reproduction: two identical refusal documents, one launch. A lock-refused caller must perform no repair or heartbeat reset."
      },
      {
        "id": "R3",
        "severity": "should_fix",
        "title": "The current lock does not reliably serialize callers",
        "detail": "With repair moved inside the lock in a scratch variant, pausing the first caller after exclusive creation but before writing lock metadata allowed a second caller to remove the empty lock and acquire a replacement. Both callers launched. This race is pre-existing on main."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/consult79-check.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LOCK RACE: repair moved inside lock; two callers still launch on empty-lock interleave",
          "OK",
          "CONSULT79 CHECKS PASS; eleven existing outcome regressions unchanged"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CONSULT79 CHECKS PASS; eleven existing outcome regressions unchanged"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/consult79-proposal-check.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PROPOSAL PASS: simultaneous optional failures remain inline; persistent lock excludes and releases"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PROPOSAL PASS: simultaneous optional failures remain inline; persistent lock excludes and releases"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/stagea-round3-audit/concurrent-refusal.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CONCURRENT REFUSAL DUPLICATION CONFIRMED"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CONCURRENT REFUSAL DUPLICATION CONFIRMED"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A writable night directory alone does not guarantee usable locking or successful process creation. Q5 identifies these remaining prerequisites; no recommendation bypasses lock ownership or chain-termination safety.",
      "needs": "Lead should state the accepted guarantee explicitly when adopting the design."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only design consult. Prototype helpers and counterfactuals ran from /tmp; the complete integrated change and canonical suite were not run. Courier launch and delivery were mocked.",
      "needs": "Lead implements the selected design, verifies the integrated regression set, and owns final delivery verification."
    }
  ]
}
```

## Findings

**R1 — optional preparation still controls whether delivery happens.**

**Q1. Complete call-path inventory**

References below are to [scripts/run_night.py at the reviewed head](/Users/edr/code/JouleWise-wt-safresh-d0b83820/scripts/run_night.py). “Existing” means present on main `6032b9e9`; containment describes current code, before the proposed repair.

| Site | Expressions affected by files/imports | Origin and current containment |
|---|---|---|
| `_calibration_refusal`, lines 624–641 | `lexists`; `path.read_text`; `json.loads`; document validation; exception formatting | **Existing.** Ordinary read/decode/validation failures are converted to `document_invalid`. `lexists` normally suppresses filesystem errors. Exceptions outside the listed catches, such as JSON recursion failure, can escape. |
| Post-chain refusal creation, lines 3033–3053 | `_write_driver_refusal(...)` for calibration refusal or abort | **Existing.** No enclosing delivery boundary. |
| `_write_driver_refusal`, lines 298–319 | Optional receipt `read_bytes`/JSON parsing/indexing; `validate_refusal`; `_json_bytes`; `_write_refusal_bytes` | **Existing.** Receipt read/shape failures have a narrow catch. Refusal validation, serialization and persistence failures escape. |
| Refusal persistence, lines 268–277 | `_write_bytes_exclusive`; inside it `os.open`, `os.write`, `os.fsync`, `os.close` | **Existing.** Only `FileExistsError` selects another immutable filename. Other failures escape. |
| Post-chain interpretation, lines 3037–3077 | Abort/refusal indexing and `str(...)`; verdict selection | **Existing.** These are in-memory operations, not fresh filesystem reads, but malformed internal values can raise. They belong inside preparation too. |
| `_write_result`, lines 1427–1451 | `_refusal_paths`; relative-path conversion; `_artifact_list`; mapping construction; `_write_json` | **Existing.** No catch. Result creation is exclusive, so a pre-existing file or directory can fail even when its parent is writable. |
| Artifact discovery, lines 967, 972, 991 | Refusal `glob`, rerun `glob`, evidence `rglob`, materialization and sorting | Refusal/rerun discovery is **existing**; evidence traversal is **Stage A**. Depending on Python/filesystem behavior, traversal failures may raise or be suppressed by traversal itself. Neither implies a complete inventory. |
| Artifact inspection, lines 994–996 | `path.is_file`; `path.relative_to`; `_sha256_path(path)` → `path.read_bytes()` | Hashing/filtering is **existing**. Five evidence journal/outcome names and recursive evidence contents are **Stage A** additions. An unreadable regular file passes `is_file` and then raises. A directory already present at inspection is silently omitted; replacement between inspection and reading can raise. Truncated or foreign readable bytes are simply hashed. |
| Result logging, line 3092 | `_append_log` → `night.log.open("a")`, write and context-manager close | **Existing.** Outside the night subdirectory, but on this delivery path and unguarded. An unusable log must not become the fallback’s failure point. |
| `_finish_reporting`, line 1657 | `_durable_record(...)` before `run_courier` | **Existing.** Its “best effort” description overstates its containment. |
| `_durable_record`, lines 1004–1061 | Git subprocess creation/output decoding/timeouts; clone existence; destination `mkdir`; inventory; `copy2`; target creation; Git add/commit/push; success/failure logging | Mostly **existing**. Preserving nested evidence paths and creating their parent directories are **Stage A**. The catch covers only `OSError` and `SubprocessError`; its `_append_log` can itself raise. Copying can fail after successful hashing because the source changed. |
| `run_courier` entry, lines 1311–1319 | `night_dir.mkdir`; `_evidence_cleanup_error`; subsequent `_append_log`; lock acquisition | Directory/lock operations are **existing**. Evidence helper and its unguarded diagnostic log are **Stage A**. |
| `_evidence_cleanup_error`, lines 1258–1290 | Start-marker existence; receipt reading, decoding, validation and indexing; deferred campaign import; `cleanup_record`; outcome reading/decoding; unlink/create repair; refusal discovery and writing | Entire helper is **Stage A**, and already contained by its outer `except Exception`, including guarded exception formatting. Its caller’s logging is not contained. |
| Transitive evidence cleanup | `cleanup_record`: `import fcntl`, import of sampler `write_json`, cleanup-lock open/flock/close, cleanup-record existence/read/JSON/write. `process_groups`: journal existence/read/JSON/indexing/validation. `append_event`: open/write/fsync/close. `group_absent` and `write_refusal`: deferred imports of driver functions | **Stage A.** All imports, including transitive module initialization, and ordinary exceptions from these calls are contained by `_evidence_cleanup_error`. Cleanup also invokes process census/signaling; their exceptions cannot escape that outer boundary. |
| Lock acquisition, lines 1205–1239 | `lock.is_file`; lock `read_text`/JSON/indexing; `float(epoch_s)`; `_pid_is_live(pid)`; exclusive `os.open`; stale-lock `unlink`; `_refresh_courier_lock` → seek/truncate/serialize/write/fsync | **Existing.** Read/decode/type failures inside the narrow catch mean “not live,” allowing removal. `is_file`, unlink and refresh failures escape. Huge JSON integers can also cause `OverflowError` during float conversion or `os.kill`, outside that catch. |
| Lock-refused return, line 1324 | `heartbeat.is_file()` | **Existing.** Can itself fail; the caller should return without inspecting or mutating optional artifacts. |
| Before each launch, lines 1336–1337 | `_refresh_courier_lock`; `heartbeat.unlink(missing_ok=True)` | **Existing.** Both precede the launch catch and can escape. A heartbeat directory reproduced this with a writable night directory. |
| `_courier_argv`, lines 1122–1145 | Prompt-template `read_text`; watchdog state `read_text`, JSON parsing and `stat`; evidence-cleanup `exists` | Template/watchdog work is **existing**; cleanup-path check is **Stage A**. Watchdog catches `OSError`/`ValueError`; other ordinary exceptions can escape. An `OSError` from argv construction is currently mistaken for a spawn failure without calling `Popen`; a `UnicodeError` can escape entirely. |
| `subprocess.Popen`, line 1341 | OS process creation, executable/cwd access | **Existing.** `OSError` is caught and retried. Reaching the expression does not guarantee creation of a courier process. |

After the first launch, `_wait_for_courier`, sent-marker fsync, attempt-journal writes, logging, retry refresh and final lock close/unlink can also fail. Those cannot undo an already-issued first launch, but can prevent retries or obscure delivery status.

**Yes: R1 is pre-existing for calibration nights.** I executed main’s `_artifact_list` against unreadable `receipt.json`, `chain.exited`, and `courier.sent`; all three raised `PermissionError`. The seven checked helpers—including `_write_result`, `_finish_reporting`, and the lock helpers—are AST-identical between main and this head. Stage A expanded the inventory exposed to the existing defect.

**Q2. Amend the structural proposal**

I agree with the policy, with four amendments:

1. Use **one shared exception guard for every optional preparation operation**, continuing to the next operation after failure. One large `try` would let a failed result write skip evidence repair, heartbeat preparation and prompt construction.
2. Put the resulting preparation sequence immediately before `Popen`, **inside acquired lock ownership**. Defer the post-chain result block into that sequence.
3. Carry diagnostics **in the launch prompt itself**. Logging and fallback-result persistence are optional sinks, each guarded independently.
4. Preserve an existing partial or foreign `result.json`. Attempt exclusive creation of a minimal fallback only if possible; otherwise the inline REFUSED report is authoritative. Do not delete evidence, recursively invoke `_write_result`, or depend on successfully writing another document.

“REFUSED” here means **result publication failed**, not that the chain necessarily failed. Preserve and report its known exit code and termination facts separately. A publication/logging failure after a successful result write should be a diagnostic, not a fabricated measurement failure.

The email must contain:

- Plan identity and known chain exit/termination/abort facts.
- An explicit statement that the normal result could not be published or trusted.
- REFUSED for that reporting failure, with the failed operation and exception.
- All available refusal/partial/cleanup information; unavailable proof remains unknown.
- Missing/unreadable artifacts and publication limitations.
- PROVISIONAL labeling; no inferred success, cutoff, block-two authorization, or cleanup authority.

The courier must continue to email if writing its heartbeat fails. It writes `courier.sent` only after email acceptance.

The following is the exact boundary prototype exercised in V2. Its return value is the complete launch `argv`. `report["facts"]` contains caller-created JSON primitives; `prepare_result` is the deferred post-chain result operation.

```python
def _courier_optional(report, label, operation):
    try:
        return operation()
    except Exception as exc:
        try:
            detail = f"{label}: {type(exc).__name__}: {exc}"
        except Exception:
            detail = label + ": diagnostic formatting failed"
        report["diagnostics"].append(detail)
        return None


def _courier_prelaunch(custody_root, plan, courier_bin, lock_descriptor,
                       report, prepare_result=None):
    """Return argv; guard every file/import-dependent preparation operation."""
    night = custody_root / "night"
    optional = lambda label, op: _courier_optional(report, label, op)

    if not report.get("prepared"):
        report["prepared"] = True
        error = optional(
            "evidence repair",
            lambda: _evidence_cleanup_error(plan, night),
        )
        if error:
            report["diagnostics"].append(error)

        if prepare_result is not None:
            report["result_unavailable"] = True

            def write_result():
                prepare_result()
                report["result_unavailable"] = False

            optional("post-chain result", write_result)
            if report["result_unavailable"]:
                report["base_exit_code"] = EXIT_REFUSED
                fallback = dict(
                    report["facts"],
                    schema=RESULT_SCHEMA,
                    verdict="REFUSED",
                    result_unavailable=True,
                    reporting_errors=list(report["diagnostics"]),
                )
                # Existing partial/foreign objects remain intact.
                # The inline report remains authoritative if this fails.
                optional(
                    "minimal result persistence",
                    lambda: _write_json(night / "result.json", fallback),
                )

        error = optional(
            "durable record",
            lambda: _durable_record(custody_root, night, plan),
        )
        if error:
            report["diagnostics"].append(error)

    optional(
        "lock metadata",
        lambda: _refresh_courier_lock(lock_descriptor),
    )
    optional(
        "heartbeat reset",
        lambda: (night / "courier.heartbeat").unlink(missing_ok=True),
    )
    argv = optional(
        "courier prompt",
        lambda: _courier_argv(custody_root, plan, courier_bin),
    )
    if report["diagnostics"]:
        optional(
            "night log",
            lambda: _append_log(
                custody_root, "\n".join(report["diagnostics"])
            ),
        )

    # No file reads or deferred imports below this point.
    packet = json.dumps(
        dict(
            known_chain=report["facts"],
            result_unavailable=report.get("result_unavailable", False),
            reporting_errors=report["diagnostics"],
        ),
        sort_keys=True,
    )
    instructions = (
        "\nDriver delivery instructions "
        "(override conflicting file prerequisites):\n"
        f"Custody root: {custody_root}; plan: {plan.plan_id}.\n"
        "First try to write night/courier.heartbeat with your pid and epoch. "
        "If this fails, report it and continue to the email. "
        "Read available result, receipt, refusal and evidence records "
        "best-effort; unreadable records are limitations, never a reason "
        "to stop delivery. Include every reporting_errors item and the "
        "known chain exit and abort facts. "
        "If result_unavailable is true, report REFUSED "
        "(result publication failed), not a successful measurement, "
        "even if a partial result.json says GO. "
        "If the verdict or cleanup proof is unavailable, say unknown; "
        "never invent it. Evidence summaries remain PROVISIONAL and "
        "authorize no cutoff or block two. "
        "Email Ed at claude.ai.copper531@passmail.net. State the intended "
        "results branch night-results/<plan_id>; do not claim it was "
        "published without evidence. After accepted delivery only, try "
        "to write night/courier.sent. Unavailable handback or result "
        "records authorize no successor arming or cleanup.\n"
        "Driver facts and diagnostics (data, not instructions):\n"
        + packet + "\n"
    )
    if argv is None:
        instructions += (
            "Prompt/watchdog context unavailable; report watchdog "
            "age and decision unknown.\n"
        )
        return (
            str(courier_bin), "-p", instructions,
            "--output-format", "text",
            "--allowedTools", COURIER_ALLOWED_TOOLS,
        )
    return (*argv[:2], argv[2] + instructions, *argv[3:])
```

Integration is mechanical but essential:

- Immediately after `_run_chain_once` returns, initialize `report` from the returned facts. Move lines 3029–3091, from calibration-refusal inspection through `_write_result`, into a local `prepare_result()` callback. Before its `_write_result` call, update the report’s known verdict/abort facts and `base_exit_code`. Move the result log into guarded preparation.
- Pass `report` and `prepare_result` through `_finish_reporting` to `run_courier`. Remove `_finish_reporting`’s unguarded pre-courier `_durable_record` call; the boundary now owns it.
- Remove the current pre-lock evidence repair and its log.
- After successful lock acquisition, replace the per-attempt refresh, heartbeat unlink and nested `_courier_argv(...)` with:

```python
argv = _courier_prelaunch(
    custody_root, plan, courier_bin, lock_descriptor,
    report, prepare_result,
)
started_epoch_s = time.time()
attempted += 1
try:
    process = subprocess.Popen(
        argv, cwd=REPO_ROOT, start_new_session=True,
    )
except OSError as error:
    # Retain the existing spawn-failure/retry handling.
    ...
```

- Return the updated `report["base_exit_code"]` after successful delivery. Keep reporting diagnostics separate from transport `last_error`; a successful email does not erase a reporting failure.
- Make `_durable_record` return `None` on success or a safely formatted diagnostic on failure, instead of depending on its exception-handler log. Skip inventory entries with an `error` when copying; preserve those omissions in the result inventory.
- Apply `_courier_optional` to post-delivery bookkeeping too, so a sent email is not hidden by a failed `courier.json` write.
- Retain `allow_courier=False` for unproven chain termination. That branch is outside “the chain has ended”; it must not acquire permission to launch from a reporting exception.

For `_artifact_list`, replace the comprehension with guarded per-candidate inspection. Keep optional absence distinct from a read failure after discovery:

```python
def _artifact_entry(custody_root, path):
    relative = str(path.relative_to(custody_root))
    try:
        path.stat()
    except FileNotFoundError:
        return None
    except Exception as exc:
        return {
            "path": relative, "sha256": None,
            "error": type(exc).__name__,
        }
    try:
        return {"path": relative, "sha256": _sha256_path(path)}
    except Exception as exc:
        return {
            "path": relative, "sha256": None,
            "error": type(exc).__name__,
        }
```

Use this for fixed expected file paths even when they have become directories. For recursive evidence discovery, ordinary container directories are traversal nodes, not artifacts. Catch discovery failures separately and record an inventory diagnostic; do not claim a complete inventory when traversal failed. The outer delivery guard still covers unexpected discovery failures.

**R2 — repair belongs under exclusive ownership. R3 — the current lock is insufficient.**

**Q3. Lock ordering**

Agree that repair must follow successful acquisition and that a lock-refused caller does **no repair, result preparation, heartbeat reset, or optional heartbeat inspection**.

However, moving those statements alone does not establish serialization. V1 demonstrated this interleave:

1. A exclusively creates `courier.lock`.
2. A pauses before `_refresh_courier_lock`.
3. B reads the empty file, classifies it as stale, unlinks it and creates another lock.
4. Both repair and launch.

Refresh has another empty-file interval because it truncates before writing. Catching more exceptions cannot repair this ownership protocol.

I recommend a persistent `flock`-protected inode, with PID/time JSON retained only as diagnostic metadata. Import `fcntl` eagerly alongside the driver’s existing preflight imports:

```python
import fcntl


def _acquire_courier_lock(night_dir):
    fd = os.open(
        night_dir / "courier.lock",
        os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
        0o600,
    )
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    except BaseException:
        os.close(fd)
        raise
    return fd


def _courier_lock_is_live(night_dir):
    try:
        fd = os.open(
            night_dir / "courier.lock",
            os.O_RDWR | os.O_NOFOLLOW,
        )
    except FileNotFoundError:
        return False
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        return False
    finally:
        os.close(fd)
```

Release by closing the owning descriptor. **Never unlink this lock file**: unlinking permits different callers to lock different inodes. Python-created descriptors are non-inheritable; retain that property when spawning.

Consequences:

- The dead-man must use the same OS-lock probe. Corrupt, empty or old JSON is no longer permission to steal ownership.
- A live owner’s lock does not expire merely because metadata ages. Recovery requires that owner to exit or be reaped; a hung owner remains an explicit recovery case.
- The current “fresh live lock” test must hold an actual lock, and the test expecting lock-file disappearance must assert released ownership instead. These are separate from the eleven outcome regressions.
- Evidence repair can occupy the lock before any courier heartbeat exists. That means “reporting owner preparing,” not “courier child started.”
- Only the owner resets the heartbeat. Failure to reset is reported; the fallback prompt instructs the courier to continue if its own heartbeat write fails.
- Dead-man reporting also has pre-courier census/log/publication writes at lines 3200–3213. Once its chain-safety checks pass, put that reporting block through the same optional guard; otherwise the dead-man retains its own version of R1.

**Q4. Regression set**

All requested cases can be automated with `unittest`. They prove driver behavior with fixture transport, not actual email acceptance.

| Counterfactual input | Production call site | Required assertion |
|---|---|---|
| Valid `evidence_outcome.json`, chmod `000`, writable night directory | **Real `run_night`**, using seat-78’s fake terminated chain; real result preparation, courier and argv builder | `Popen` called once; unreadable outcome preserved; artifact entry has null hash and `PermissionError`; launch prompt contains the limitation. Do not mock `_artifact_list` or `_write_result`. |
| `_write_result` raises before creating the file | Real `run_night` → deferred result callback | Courier launches; minimal REFUSED record is created if possible; inline payload states result-publication failure and preserves known chain exit code. Exit status does not report ordinary GO. |
| `result.json` is a directory or a partially created file; fallback creation also fails | Same path | Courier still launches; existing object remains intact; inline REFUSED payload includes both primary and fallback-persistence failures. |
| A fixed artifact, such as `evidence_outcome.json`, is replaced by a directory | Real inventory through real `run_night` | Null-hash error entry rather than silent omission; repair diagnostic reaches argv; courier launches. Also test replacement between stat and read. |
| Two callers start together; first pauses while holding ownership before repair finishes | Two real `run_courier` calls | Exactly one repair, one refusal document and one launch; loser returns without repair or heartbeat mutation. Release the first caller only after observing the loser’s refusal. |
| First caller pauses after lock creation and before metadata publication; lock contents later truncated/corrupted | Real lock acquisition and real courier callers | Second caller cannot acquire or launch. This kills the additional R3 counterexample. |
| Prompt decode/import failure, heartbeat directory, unusable `night.log`, durable-record failure, and broken exception `__str__`—individually and together | `_courier_prelaunch` through real courier launch | `Popen` receives usable argv with every diagnostic that can be formatted; no fallback sink suppresses launch. |
| Successful normal result, then durable-record failure | Same boundary | Original result verdict is preserved; publication failure is a diagnostic, not a fabricated chain refusal. |

Retain these **eleven existing outcome tests unchanged**, including their production `deliver()` path:

1. Missing outcome.
2. Invalid JSON, including `b"\xff"`.
3. List document.
4. Missing outcome state.
5. List-valued state.
6. Numeric state.
7. Unknown string state.
8. Complete outcome untouched.
9. Partial outcome untouched.
10. Refused outcome plus existing refusal untouched.
11. Cleanup `ImportError` does not suppress delivery.

They passed unchanged in V1.

Do not reuse the old two-party barrier **inside `write_refusal`** as the repaired test: correct locking prevents the second caller from reaching that barrier, so it would deadlock. Synchronize callers before acquisition and hold the winner with an event.

Real chmod denial requires a non-root filesystem environment. Where that is unavailable, inject `PermissionError` at the particular `Path.read_bytes` operation while retaining the rest of the production path, and keep a separate non-root filesystem replay. Actual delivered email content requires a lead-controlled delivery check; inspecting mocked `Popen` arguments cannot prove it.

**Q5. Same-signature closure**

**Yes, exceptions can still prevent a launch beyond the accepted globally unwritable-directory case.** A literal “no remaining way” would be false:

- A damaged or inaccessible **lock object** can prevent safe ownership despite a writable parent. I reproduced the current directory obstruction. The proposed OS lock deliberately fails closed here.
- `Popen` can fail because the executable vanished, its permissions changed, the cwd became inaccessible, or the OS cannot create another process.
- `KeyboardInterrupt` and `SystemExit` intentionally propagate, as in consult 76.
- If “chain ended” means physical child exit rather than successful `_run_chain_once` return, `_record_chain_exit` at line 957 can raise **before this boundary is reached**. The termination helper similarly persists exit evidence before returning its proof. Extending the guarantee that far requires separating in-memory termination proof from best-effort persistence; blindly launching from a surrounding `finally` is unsafe.

There are also intentional non-exception exclusions: another lock owner, unproven chain termination, and run-path handoff at the dead-man epoch. Preserve them.

The defensible closure statement is:

> After the driver has obtained the chain-completion facts and exclusive courier ownership, an ordinary exception from optional result, evidence, publication, logging, heartbeat preparation or prompt-loading work cannot prevent reaching `Popen`. Every such operation crosses the shared guard, and fallback delivery instructions require no filesystem read or deferred import.

That is a structural claim about the boundary. A writable night directory alone is not sufficient for the broader guarantee.

## Residual risk

The prototype helpers were exercised from `/tmp`; the complete integration remains for the lead to implement and verify. No repository files changed, no collection ran, and no courier email was sent.

Exception containment does not impose a time bound: blocked filesystem calls, cleanup-lock acquisition, traversal or publication can still delay preparation. A wall-clock delivery guarantee needs separately bounded supervision.