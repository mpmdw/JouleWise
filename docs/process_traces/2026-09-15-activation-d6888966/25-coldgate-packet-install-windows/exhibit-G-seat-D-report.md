```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented D-1 through D-4 against the adjudicated design; D-5 required no change. Historical text preserved; 261 tests passed.",
  "workspace": {
    "base_requested": "3d5b7623",
    "base_mode": "exact",
    "head_start": "3d5b7623a484577c85e07eaefdd217680578bfde",
    "head_end": "3d5b7623a484577c85e07eaefdd217680578bfde",
    "upstream_end": "1d39729c7f4b1dd7b732b9a92f76bad451cadea8",
    "branch": "feat/2026-09-15-install-windows-multi-01-docs"
  },
  "pathspec": [
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/process/NIGHT_COURIER_PROMPT.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 0.554s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 31 tests[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 86 tests in 1.966s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 86 tests[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 59 tests in 0.546s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 59 tests[\\s\\S]*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 85 tests in 10.027s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 85 tests[\\s\\S]*OK"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "rg -n '03:00.*06:30|02:45.*03:30|(^|[^−-])07:00' docs/phase_2/derivation_night_runbook.md docs/process/{NIGHT_HANDBACK,MAGISTRATE_WATCHDOG,NIGHT_COURIER_PROMPT,MAGISTRATE_RELAUNCH_PROMPT}.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["docs/phase_2/derivation_night_runbook.md:73:02:45–03:30 belt is correct rather than forbidden; `Session` is disambiguated"]},
      "expected": {"exit_code": 0, "tail_regex": "02:45–03:30"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Docs target the adjudicated parallel implementation. This worktree still contains predecessor code; new schedule APIs were not executed here. The added print block compiles and worked epoch arithmetic was independently checked.",
      "needs": "Integrate seat A, then verify schedule output, installer diagnostics and installed-plist fence behavior against these docs."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Runbook section 3 retains the pre-registration's distinct-calendar-days requirement for the FAIL route. Installation timing changes do not rewrite that scientific registration.",
      "needs": "Double-check whether D-181 also requires a separately adjudicated change to this registration-specific constraint."
    }
  ]
}
```

## Change

- **D-1 — `docs/phase_2/derivation_night_runbook.md`:** provenance/glossary at 11–21, 198–237; collateral wording at 511; derived arithmetic and install procedure at 1161–1369; notice/arm/recovery at 1377–1533; arm evidence at 1577–1581; harvest at 1662; failures at 2212–2303; fact/glossary rows at 2370–2500. Documents all five refusals and exit codes, rollback, daily dead-man, and a runnable schedule-print block.
- **D-2 — `docs/process/NIGHT_HANDBACK.md`:** provenance and derived completion at 42–74; timeline/procedure/notice at 138–227; harvest/results naming at 341–360; uninstall command at 394–395. One notice per plan; existing email-then-arm and Ed’s NO wording retained.
- **D-3 — `docs/process/MAGISTRATE_WATCHDOG.md`:** 21–35 and 46–74 document discovery or installed-plist fencing, unsafe-read holds, and derived deadlines.
- **D-4 — `docs/process/NIGHT_COURIER_PROMPT.md`:** 16–17 use `night-results/<plan_id>`.
- **D-5:** `MAGISTRATE_RELAUNCH_PROMPT.md` unchanged byte-for-byte; “v2 plan” retained.

## Verification notes

Filename searches identified exactly the three document-referencing test modules reported above, alongside mandatory freshness checks.

The fixed-clock grep found only preserved history:

- Runbook **73**: revision-5 changelog.
- Handback **250, 257**: Executed rehearsal-20260911.
- Handback **309**: Executed 2026-09-14 attempt.
- Handback **327**: prior dated evening-arm addendum.

Excluding those historical regions yielded **zero live matches**. Comparisons against HEAD confirmed unchanged revision history, Executed sections, all subsequent handback addenda, and the relaunch prompt.

No scope expansion, commits, network calls, or machine-state operations. Historical changelog references—including the former cutoff question—remain verbatim under an explicit historical label.

## Residual risk

**What the lead should double-check:** integrate seat A and verify the documented commands against its exact implementation; perform the launchd calendar checks at the bench; review the unchanged registration-specific calendar-day constraint before scheduling same-day FAIL-route captures.