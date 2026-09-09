```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Rebuilt the liveness contract with concrete examples, labeled diagrams, 50 decision combinations, implementation references, and first-use definitions.",
  "workspace": {
    "base_requested": "655b3368",
    "base_mode": "exact",
    "head_start": "655b3368b34d173bda9c5660343c3a2753c0ee97",
    "head_end": "655b3368b34d173bda9c5660343c3a2753c0ee97",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "docs/2026-09-08-window-liveness-docs"
  },
  "pathspec": [
    "docs/contracts/window_liveness.md",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness > /private/tmp/window-liveness-docs-01-rewrite-docs-freshness.log 2>&1; test_result=$?; tail -n 4 /private/tmp/window-liveness-docs-01-rewrite-docs-freshness.log; exit \"$test_result\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_measurement_liveness > /private/tmp/window-liveness-docs-01-rewrite-measurement-liveness.log 2>&1; test_result=$?; tail -n 4 /private/tmp/window-liveness-docs-01-rewrite-measurement-liveness.log; exit \"$test_result\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denied /bin/ps. Used the authorized historical fallback, explicitly distinguishing captured PID/date values from illustrative PGID, state, and registration values.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced during the session; the checkout and Code map remain at the exact requested head.",
      "needs": ""
    }
  ]
}
```

## Change

Rewrote all eight requested sections and the pointer text. Corrected exit-marker precedence, DEAD campaign token handling, and traversal stopping on errors. Added labeled diagrams, exact JSON, operator repair, and a final Code map.

No commit. Next step: lead pedagogy and fidelity review of the four-file diff.

## Verification notes

The 50 documented combinations were checked against the implementing inspectors, including probe reachability and missing-token/reused-PID exceptions. All four JSON examples parse and contract links resolve.

Used targeted checks because this change modifies documentation only. No measurements or status publication ran.

## First-use audit

Mechanically checked 79 marked technical labels for earlier exact occurrences, then reviewed contextual words and code identifiers in reading order. Definition locations below use the contract’s paragraph IDs:

- **P1–P3:** power measurement, status publisher, Git, window, process, `pgrep`, night driver, child process, chain, campaign, measurement runner, test stub, leaked stub, test shard, custody parent, census, liveness, indeterminate, guard, revision.
- **F1–F3:** kernel, process ID/PID, process group/PGID, `/bin/ps`, `lstart`, start token, whitespace, valid date grammar, identity, operator, shell, `$$`, `-p`, `-o`, heading suppression, `LC_ALL`/`LANG`, process state, sandbox, parent PID, historical extract, worked example.
- **C1–C6:** marker, `chain.started`, `chain.exited`, claim, exclusive creation, `O_CREAT`/`O_EXCL`/`O_WRONLY`, file owner, descriptor, `0o600`, JSON, object, key, boolean, null, UTF-8, `epoch_s`, UTC, Unix epoch, spawn, `_write_all`, `fsync`, probe, temporary file, atomic replacement.
- **C7–C10:** dead-man, `os.killpg(pgid, 0)`, signal, `ProcessLookupError`, `PermissionError`, `exit_code`, `reaped_by`, `launch_failed`, exit code, `monotonic_ns`, floating-point number, acceptable exit, exit-read precedence.
- **I1–I8:** timeout, stdout, stderr, rc, `stat`, sleeping state, parser, zombie, LIVE, DEAD, UNKNOWN, empty output, recorded owner, warning, refusal, reused PID, clear, probe override, `/usr/bin/true`, token comparison.
- **R1–R9:** registry, `active-campaigns`, hexadecimal, runs root, `campaign.lock`, acquisition, nonce, schema, filesystem, link, resolved absolute path, `runs_root`, alternate execution function, dry run, `xb`, device number, inode number, Python, buffered output, flush, `finally`, exception, unlink, `SIGTERM`, `SIGKILL`, malformed registration, stale entry.
- **R10–R11:** checkout, `ENTRY`, `env -u`, `PYTHONDONTWRITEBYTECODE`, `os`, `Path`, `RegistryEntry`, `_inspect_campaign`, `Census`, `custody_parent`, `observe_identity`, `remove_campaign`, `quarantine_stale_lock`.
- **D1–D6:** additional-parent setting, array, path expansion, duplicate removal, immediate child, reconciliation, wrapper, `FileNotFoundError`, enclosing retry, traversal order.
- **T1–T8:** refusal precedence, complete start, malformed start, not-run, registry categories, combined decision, `WARN:`/`REFUSING:`, `courier.sent`, commit-freeze sentinel, staging, commit, push, status checkout, `set -e`, snapshot, mutual exclusion.
- **Pointers:** chain, campaign, custody parent/root, and indeterminate are glossed before their contract links; handback’s earlier chain and custody references also received definitions.