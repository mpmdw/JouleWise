```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Six consistency findings; generated state and four focused checks pass; no files modified.",
  "workspace": {
    "base_requested": "4203ff59",
    "base_mode": "descendant",
    "head_start": "4203ff599b0e7dfafda73ea7d10fb86ee2efbe71",
    "head_end": "4203ff599b0e7dfafda73ea7d10fb86ee2efbe71",
    "upstream_end": "4203ff599b0e7dfafda73ea7d10fb86ee2efbe71",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 1,
      "should_fix": 2,
      "nit": 3,
      "total": 6
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Adopted second-night ruling remains a pending hard-start dependency"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Current T38d entry still directs already-completed merge and ruling work"
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "Terminal review 80 claims coverage removed in its final fix round"
      },
      {
        "id": "F4",
        "severity": "nit",
        "title": "Terminal review 96 retains pre-final test and fixture counts"
      },
      {
        "id": "F5",
        "severity": "nit",
        "title": "Current night instructions still present acceptance item 1 as outstanding"
      },
      {
        "id": "F6",
        "severity": "nit",
        "title": "Several approximate chronology labels postdate their containing commits"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "python3 -B scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_gen_state.TestRefreshedStateFidelity.test_exact_live_id_set tests.test_gen_state.TestRefreshedStateFidelity.test_terminal_ids_absent_from_kernel_present_in_completed_table tests.test_gen_state.TestKernelValidity.test_kernel_validates tests.test_docs_freshness.DocsFreshnessTests.test_current_sections_do_not_copy_volatile_literals",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 0.033s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in .*\\s+OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git merge-base --is-ancestor a52810c9 57ddad20",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": []
}
```

## Findings

Paths beginning `65-`, `67-`, etc. below are under `docs/process_traces/2026-09-09-rehearsal-harvest/`. `DURABLE` means `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`.

| ID | Severity | Location | Conflicting values and consequence |
|---|---|---|---|
| F1 | blocker | `docs/process/state_kernel.json:3328`, `:3332`, `:3416`; `TASK_QUEUE.md:725`, `:884` | Kernel has **`evidence: null`, `state: pending`, hard start dependency `SECOND-STUB-NIGHT-RULING`**, with `needs_ruling` prose. **`65-magistrate-synthesis-second-stub-night.md:3–8` adopts REQUIRED**, with no material dissent; DURABLE:727 records it ruled. The ruling event is already satisfiable from synthesis 65. Install that evidence and represent remaining night/acceptance work separately; satisfying the ruling does **not** make the rehearsal DONE. |
| F2 | should_fix | `RUN_STATE.md:13`, `:19` | Presented as **Current checkpoint**, activation `628c2eed`: cure **“not merged”**, second night **`needs_ruling`**, next action **cure merge → PR #308 merge**, item 1 **OPEN**. Actual state: #308 **`d7f5d5d9`**, #309 **`a52810c9`**, #310 **`79920ec9`**, #311 **`d2dffe4b`** are merged; synthesis 65 rules the second night; kernel:3416 closes item 1. DURABLE:801–805 gives activation `2145630c`’s operative handoff. Preserve the old checkpoint as history, but replace its current-entry authority. |
| F3 | should_fix | `80-terminal-review-fixture-timeout-wallclock.md:27` | Claims the regression **asserts cadence ratio and clock anchor unchanged across the sentinel stage**. The same review at **:53–54 says that coverage was removed** in `016ac5f0`; `tests/test_run_campaign.py:9614–9644` confirms the final regression contains strict-validity, bounded-drift and sample-count assertions instead. Correct the final-design claim. |
| F4 | nit | `96-terminal-review-arm-integration-load.md:35`, `:43` | Summary says **184 → 187 methods**, **three added tests**, **30-line fixture**. Final content head `9dbacb40` has **184 → 188 methods**, **four added tests**, and `tests/fixtures/arm_clock.py` has **37 lines**. The fourth method is the portability regression at `tests/test_arm_readiness_integration.py:880`, acknowledged in review 96:54. Historical 187-test bench results remain valid for their cited earlier heads. |
| F5 | nit | `docs/process/NIGHT_HANDBACK.md:136`; `67-arm-runbook-rehearsal-20260911.md:414` | Current operational prose says item 1 **“remains desk work.”** Kernel:3416 and DURABLE:801–805 say **CLOSED**, with fresh capture 104: **median 5158 ms → deadline 300 s**. Add a current disposition pointer without changing the frozen H interpretation or presenting this as closure of the whole rehearsal. |
| F6 | nit | DURABLE:727, `:742`; `65-magistrate-synthesis-second-stub-night.md:1`; `67-arm-runbook-rehearsal-20260911.md:470`; `72-dryrun-blockA-rehearsal-20260911.txt:1` | Chronology labels disagree with containing-commit times: DURABLE **~09:35** and synthesis **~09:20** already exist in H `57ddad20`, committed **09:15:04**; runbook addendum **09:20** exists in `0656bb98`, committed **09:16:16**; DURABLE dry-run update **~09:40** and dry-run heading **~09:30** exist in `21e31107`, committed **09:19:37**, while dry-plan `authored_epoch_s` at 72:10 converts to **09:17:14 PDT**. Normalize these approximate labels or identify what time they denote. Future firing epochs are correct. |

**No drift found**

- Kernel has **156 tasks**; `EXPECTED_IDS` has **156**, with identical membership; count assertion at `tests/test_gen_state.py:726` agrees.
- `NIGHT-GATE-STUB-CHAIN-01`, `FIXTURE-TIMEOUT-WALLCLOCK-01`, and `ARM-INTEGRATION-LOAD-01` are absent from live task keys and present in completed rows `TASK_QUEUE.md:102–104`.
- Generated regions pass `gen_state.py --check`. Their semantic ruling error is F1, despite byte-level consistency.
- All audited Git SHA literals resolve to the expected objects. Merge candidate parents match reviews 80/96 and tails 93/102. Synthesis 65’s cure diffstat matches Git: **5 files, 225 insertions, 100 deletions**.
- H is **`57ddad20226c6921d81a87b9d78e61950c14a74f`**, the handback rewrite and a descendant of `a52810c9`. Notice ID **`1a086f4174733bfb`** and thread **`1a0800cdb282c3f1`** agree across runbook and durable state.
- Synthesis, handback, runbook and dry-plan pins agree: install **09-10 03:00–06:30 PDT**; dead-man **1789048800**; t0 **1789120560**; deadline **1789121760**; exit boundary **1789119060**; window **900 s**.
- Replay shard totals sum correctly: **5646 / 5649 / 5650**, each **0 failures, 0 errors, 108 skips, rc 0**. Waiver 59 correctly preserves the earlier **5642 tests / 5 failures / rc 1** evidence.
- README activity blurb contains no pull-request literals and correctly describes the merged fixture lanes and last three green replays.
- Earlier #310/#311 holds and red replay statements are dated history superseded by the later updates. The final DURABLE:804–805 action remains **runbook 67 in the 09-10 installation window**.
- Activation IDs, recorded spawn epochs, courier IDs, harvest verdict/refusal, uninstall and removal records agree with their primary artifacts. Handback’s 09-09 block explicitly labels its pending-cure language historical.
- Powermode remains queued, with record-only preparation and gating design deferred. Clone readiness retains its preparation/hardware distinction; no clone cut is falsely claimed.
- Cold-start durations, median, deadline arithmetic and script blob match capture 104 and Git. Workspace remained clean and unchanged.

## Residual risk

This was repository evidence review, not a fresh GitHub/Gmail or machine-state audit. CI status, notice delivery and later “NOTHING IS ARMED” claims were checked for consistency with retained records, not independently re-observed. Historical full-suite replays were inspected, not rerun.