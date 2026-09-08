```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "No new defect found; R1/R3/R5/R6 are cured, and R2 implements the ruled sequencing with the pre-existing initial empty-marker window retained.",
  "workspace": {
    "base_requested": "a2cfb644",
    "base_mode": "exact",
    "head_start": "e9579dc2b913ca2e2fe9ee8e42b37e3fe6c7aaff",
    "head_end": "e9579dc2b913ca2e2fe9ee8e42b37e3fe6c7aaff",
    "upstream_end": null,
    "branch": "fix/2026-09-08-window-status-liveness"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "recommendation": "accept delta subject to lead verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff a2cfb644~1 e9579dc2 -- tests/test_run_campaign.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 JOULEWISE_IDENTITY_PROBE=/usr/bin/true python3 -c 'import os; from joulewise.measurement_liveness import observe_identity,Identity; assert observe_identity(os.getpid())==Identity(\"UNKNOWN\"); print(\"R1 UNKNOWN: PASS\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["R1 UNKNOWN: PASS"]},
      "expected": {"exit_code": 0, "tail_regex": "R1 UNKNOWN: PASS"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "bash -n scripts/window_status.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Filesystem-writing regression suites were inspected, not executed, under the read-only sandbox. An initial heredoc command was rejected because zsh required a temporary file; read-only checks were rerun using python -c.",
      "needs": "Lead should run the four-module acceptance suite."
    }
  ]
}
```

## Findings

None introduced by this round.

**R1 — cured.** `joulewise/measurement_liveness.py:60–64` makes rc 0 plus empty output UNKNOWN. The regression explicitly asserts `Identity("UNKNOWN")` at `tests/test_measurement_liveness.py:183`. The shell regression at `tests/test_window_status_guard.py:85–88` invokes `assert_refused`, whose assertions require nonzero exit, unchanged status bytes, and no Git calls (`:65–67`). UNKNOWN raises at `measurement_liveness.py:177–178`, becomes a refusal at `:261–262`, and prevents publication through `scripts/window_status.sh:44–46`. **Counterfactual:** restoring rc 0 → DEAD produces warning-plus-permit and breaks both regressions.

**R2 — ruled sequencing implemented, with qualifications.**

- **(a)** `scripts/run_night.py:375–380` writes pid, pgid, and epoch, fsyncs through `_write_all` (`:106–113`), and closes before `observe_identity` (`:381`).
- **(b)** `:383–385` writes the temporary file in the same directory and atomically replaces the marker. `_write_json` → `_write_bytes_exclusive` → `_write_all` (`:106–125`) fsyncs and closes the replacement bytes. There is **no directory fsync after rename**, so this is not a complete power-loss durability guarantee.
- **(c)** Between writes, census refuses missing `start_time` before probing (`measurement_liveness.py:199–201`), even for a dead PID. Dead-man intentionally retains different semantics: it reads pgid without requiring `start_time` (`run_night.py:1339–1347`), refuses a live/uncertain group (`:1403–1420`), and records exit only after `ProcessLookupError` proves the group absent (`:1421–1422`). It does not falsely infer launch failure from missing `start_time`.
- **(d)** No second claim succeeds: `chain.started` remains present throughout temporary-file creation and replacement; O_EXCL at `:362–368` still fails.
- **(e)** **Yes, an initial empty/partial window remains.** Claim creation precedes spawn (`:431`) and the first write (`:378`); `_write_all` can use multiple writes. Census can read it and refuses malformed JSON. The added identity probe no longer occupies that window. “Complete at every instant” is therefore too strong.

**R3 — restored verbatim.** Ran the requested diff; the restored function does not differ. A separate byte comparison of its decorator and function span also passed. Synthetic coverage remains additional.

**R5/R6 — cured within scope.** Both publication RuntimeError handlers return 2 inside outer cleanup (`run_campaign.py:7282–7288`, `:8255–8261`). Nested finally blocks remove the owned registry entry and release the lock (`:8030–8035`, `:8952–8957`). Identity rejection occurs before entry creation; write-time exceptions remove the partial publication internally (`measurement_liveness.py:109–130`). R6 accumulates each registry attempt separately and appends only after success (`:243–250`); retry adds zero duplicate diagnostics. Regression assertions require exactly one warning and two distinct refusals (`tests/test_measurement_liveness.py:216–219`).

## Residual risk

The retained initial empty-marker crash window can still reach dead-man’s pre-existing launch-failed closure (`run_night.py:1391–1397`). This round removes its probe-induced widening; it does not eliminate that baseline race. Filesystem race regressions await lead execution.