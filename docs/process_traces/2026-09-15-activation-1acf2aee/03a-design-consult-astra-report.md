# 03a — Design consult, ASTRA seat report (gpt-6-astra xhigh, genre scout, blind, read-only, worktree `3d5b7623`), status OK/findings/complete, harvested 05:58 PDT 2026-09-15 (out-file mtime 05:57:58)

Verbatim out-file of the Astra design seat on brief 02 (`/tmp/magistrate-1acf2aee/03-design-astra.md`). Model output; the magistrate adjudicates in record 06.

---

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend plan-owned epoch install spans, separate installation cutoffs and runtime dead-man, and a versioned schema migration.",
  "workspace": {
    "base_requested": "3d5b7623",
    "base_mode": "exact",
    "head_start": "3d5b7623a484577c85e07eaefdd217680578bfde",
    "head_end": "3d5b7623a484577c85e07eaefdd217680578bfde",
    "upstream_end": "3d5b7623a484577c85e07eaefdd217680578bfde",
    "branch": "feat/2026-09-15-install-windows-multi-01"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "lead_synthesis", "action": "start_now"},
      {"row": "implementation", "action": "wait_for", "wait_for": "adopted design and explicit write scope"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B -m unittest tests.test_night_plan_writer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1; git rev-parse HEAD origin/main; git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["feat/2026-09-15-install-windows-multi-01"]
      },
      "expected": {"exit_code": 0, "tail_regex": "feat/2026-09-15-install-windows-multi-01"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The recommendation distinguishes every install-span cutoff from the plan's runtime dead-man. v3 already means TRANSACTION_PACK.",
      "needs": "Adopt this interpretation and migration policy before implementation."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Synthesis | start_now | — | Deadline semantics, schema |
| Implementation | wait_for | Adopted synthesis | Shared plan parser and scheduling consumers |
| Independent review | wait_for | Integrated diff | Legacy compatibility, installation races, actual CLI |

## Critical path

Adopt deadline semantics → freeze schema/helper API → integrate all consumers and templates → focused regressions and D-172 subprocess/mutation evidence → twelve-row gate. No repository writes, network calls, or hardware measurements were performed.

## Delegation contracts

References below are repository-relative. Abbreviations: **R** `scripts/run_night.py`; **W** `scripts/magistrate_watchdog.py`; **I** `scripts/install_night_agent.sh`; **G** `joulewise/night_gate.py`; **B** `docs/phase_2/derivation_night_runbook.md`.

### Q1. Location and shape

**Recommendation: put the finite schedule in the frozen plan.** Add:

- `install_spans: [{"open_epoch_s": integer, "close_epoch_s": integer}, ...]`
- `deadman_epoch_s: integer`

Require a nonempty, ordered, nonoverlapping list; each interval is half-open, with `open < close <= t0 - PLAN_LEAD_S`. Absolute dated epochs permit midnight crossings and multiple spans on one day without implicit recurrence. Render local dates, offsets and UTC in notices; never infer “tomorrow.”

Use a shared `joulewise/night_schedule.py` for validation, interval membership and deadline arithmetic. Constants describe mechanics, not a fixed daily timetable.

**Deciding reason:** the plan already supplies the frozen coordinates and is atomically published by `joulewise/night_plan_writer.py:45–71`. Putting mutable schedule policy elsewhere creates another binding/discovery problem. D-180:11751–11755 permits several spans; D-181:11867–11883 removes cadence limits.

### Q2. Two deadlines, with different jobs

**Every install span closes irrevocably at its own `close_epoch_s`.** This is the installation dead-man. The runtime fallback is the separate plan-level `deadman_epoch_s = D`.

Preserve:

`C = t0 + window_max_s + COURIER_DEADLINE_S; require C < D`

Author D explicitly before arming. **No automatic added margin.** The notice states `D-C`. Deriving D as `C + margin` would make the existing overrun refusal tautological. Evidence: R:971–972 computes C; R:1470–1481 refuses equality.

Implement:

- I validates membership before side effects, immediately before each bootstrap, and after installation verification. Expiry midway rolls back both jobs and returns nonzero; never claim a successful arm.
- Use `night_plan_malformed` for malformed schedules and retain `night_plan_overruns_deadman` for `C >= D`. Give install expiry a distinct CLI diagnostic, `install_span_closed`, exit 3; it is not a physics refusal.
- Derive each job’s `StartCalendarInterval` Month/Day/Hour/Minute from t0 or D. Keep two labels, `RunAtLoad=false`, no KeepAlive.
- Remove required `--hour/--minute`, or retain them only as equality assertions against the plan.
- R uses shared `deadman_epoch(plan)` for admission and courier handoff. `dead_man()` must no-op before D for new plans.
- The driver must **not** reject normal execution because installation has closed: execution necessarily follows installation.

Today I:109–116 checks freshness, but has no span membership check. The executed check lives in `docs/process_traces/2026-09-13-activation-24b9d3dd/48-arm-evidence/40-arm.zsh:19–24`: `assert start <= now < end`.

### Q3. Watchdog fencing

Remove `local_fixed_fence()` and its decision branch, not merely its constants. Retain the plan-derived closed boundaries and replace `_next_deadman_epoch(t0)` with D throughout W:721–788.

**`plan_span_active` suffices for discoverable plans.** Preserve its ordering: open chain dominates; completion remains fenced; delivery then releases; otherwise D plus `COURIER_LOCK_FRESH_S` bounds the fallback.

The fixed fences additionally protected periods with **no discoverable plan** (W:702–714). Replace that assumption with an installation invariant: the complete plan must exist at the exact `*/night_plan.json` discovery location before either job is bootstrapped. Reject an installation outside that discovery topology. Preserve atomic publication, unreadable/malformed-plan holds, and custody retention.

Evidence: discovery is W:258–259; malformed plans hold at W:1380–1384. B:1267–1269 already orders notice before discovery; B:1378–1389 publishes before installation.

### Q4. Immediate successor after harvest

**Do not shorten the completion fence.** B:1491–1494 explicitly requires completion, courier delivery and process clearance before harvest.

After that harvest:

- `plan_is_armed` already returns false on `courier.sent`, unless the chain remains open (W:739–749).
- `plan_conflicts` receives only armed plans (W:1378–1384). Replace its deadline arithmetic; do not weaken conflict detection.
- `fenced_checkout_rows` already represents multiple triples, with no date restriction (W:797–807).
- Results naming **must change both destinations**: R:574 names the branch by date; R:582 also names the trace directory by date. Use a deterministic safe key such as `<UTC-date>-<sha256(plan_id)>` for both.
- Custody and clone names need unique plan IDs, not unique dates. Adopt a time/nonce suffix in authoring examples; never reuse a consumed root.
- Keep one handback per frozen H. Successor H rewrites its copy; predecessor clone retains its own. `docs/process/NIGHT_HANDBACK.md:238` explicitly demonstrates these different committed versions.
- Uninstall the predecessor before installing the successor. I:260–261 currently blindly boots out both shared labels: change installation to refuse occupied labels, preventing accidental replacement.

### Q5. Schema and migration

An H-pinned tracked schedule could preserve existing plan keys, so a schema bump is **not logically mandatory**. I recommend **v4 for new plans** because the schedule should travel with its authorizing plan.

**v3 is occupied:** G:23–26 defines v2 packless and v3 pack plans. Use v4 with the existing class-specific exact key sets plus the two Q1 fields; `pack_night` remains required only for pack nights.

Retain exact legacy v2/v3 parsing for historical reads, verification, watchdog fencing and uninstall. Legacy deadlines retain their original 07:00 interpretation. New authoring/installation requires v4; never silently upgrade old bytes.

Consumer footprint:

- G:194–245, parser/dataclass; `night_plan_writer.py:18–34`, serializer.
- R:921, 1283, 1430, parsing and fallback-plan construction.
- I:98–119, validation; W:686, parser and deadline consumers.
- `scripts/gen_derivation_night.py:475–477, 528–534, 674–675, 776–786`: parser message, arithmetic, generated examples/text.
- `joulewise/arm_readiness.py:9949,9989`: shared-parser consumers; preserve plan-byte digest binding.
- `docs/process_traces/2026-08-28-live-smoke/preflight.sh:39–40`: overlooked hard v2 assertion.
- `docs/contracts/pack_night_go_receipt.md:152–156`: exact v3 contract; append the adopted successor contract.
- Relaunch prompt line 13 and schema fixtures/tests.

Cost: one coordinated parser/producer migration, legacy fixtures retained, and generated documentation refreshed. Merely changing the schema constant is insufficient.

### Q6. Regression names

Add focused cases in the corresponding existing test modules:

- `test_install_spans_round_trip_and_reject_overlap`
- `test_each_install_close_is_exclusive`
- `test_expiry_during_bootstrap_rolls_back_both_jobs`
- `test_explicit_deadman_rejects_completion_equality`
- `test_deadman_dispatch_uses_plan_epoch`
- `test_afternoon_plan_passes_driver_and_watchdog_boundaries`
- `test_no_plan_has_no_daily_belt`
- `test_undiscoverable_plan_cannot_install`
- `test_harvested_predecessor_allows_same_day_successor`
- `test_same_day_plans_have_distinct_custody_and_results_paths`
- `test_legacy_plan_deadlines_remain_unchanged`

Exercise 13:20, 07:xx, midnight, early/late callbacks and ambiguous local times. Include real installer argv/plist parsing with a fake launchctl. D-172 (`docs/decision_log.md:11180–11187`) also requires a real watchdog subprocess and a named changed-line mutation shown RED.

### Q7. Exact documentation changes

- **B §1.3:** replace calendar-day-before/03:00–06:30/never-07:xx instructions with the complete dated span list, exclusive closes, D and unchanged exit boundary. Remove the inherited 06:05 recommendation.
- Update B §1.2 arithmetic and refusal remedies, §1.4 notice/commands/plist checks, terminology and source map. Those fixed assumptions also occur at B:1150,1245,1330,1411 and 2113.
- **NIGHT_HANDBACK:** replace operative timeline and expected pre-night 07:00 log line. Notice text: “Install spans: [every dated opening and exclusive close]. No installation at or after a span’s close. Runtime dead-man: [D local/UTC/epoch]; courier deadline: [C].” Preserve historical Executed sections verbatim and all notice/NO ordering.
- **MAGISTRATE_WATCHDOG.md:** update lines 21,31,42–54 for schemas, publication invariant and plan-derived D; preserve stand-down ladder.
- **MAGISTRATE_RELAUNCH_PROMPT.md:13:** say “current supported plan schema,” require plan-derived jobs installed from its pinned checkout. Preserve lines 10–12 and 19’s authority boundaries.

### Q8. What stays fixed

Census predicates and cadence; PLAN_LEAD_S and request/TERM/KILL ladder; courier deadline/backoff/lock freshness; window allocation and chain budgets; all unrelated gate refusals; immutable evidence, pre-registration, notice/NO procedure and twelve-row gate.

Evidence: R:62–66; W:67–74; D-181:11871–11875. Installation flexibility supplies no authority to retry physics failures or relax arm census rules.

### Q9. Parcel recommendation

**One implementation seat**, followed by independent review/test amplification. The parser, shared deadline helper, installer, watchdog and generated examples must agree on one schema and one deadline interpretation; splitting their first implementation creates incompatible intermediate contracts. The lead should issue an exhaustive allowlist covering the files above and their focused tests. This consult remains `WRITE_SCOPE: []`.

### What the lead should double-check

Native launchd behavior remains unverified: calendar fields are not a true one-shot epoch timer. Specify guarded dispatch for early/repeated callbacks and sub-minute t0 handling; never silently round t0. Prove sleep/DST behavior before claiming live acceptance. Also inspect installation rollback at the close boundary and legacy plan-byte/GO-receipt compatibility.

### Where I disagree with the brief

“Dead-man per span” conflates installation expiry with runtime recovery. Installation closes before t0; its close cannot also terminate that run. I recommend separate meanings, explicitly adopted by the lead.

Also, G:91 only **registers** the driver refusal; it does not implement that arithmetic. And R:1773–1804 refuses a live chain rather than killing it. Preserve those distinctions in the implementation contract.