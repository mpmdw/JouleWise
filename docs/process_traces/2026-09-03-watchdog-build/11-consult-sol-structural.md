```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repeated green-suite/failed-production outcome is a missing composition boundary: hand-authored fixtures and injected dependencies test local logic, while no test crosses the real plan writer, CLI, and night-gate adapter graph.",
  "workspace": {
    "base_requested": "1e324e3d40ea956610cf0df627fde7e47b93749b",
    "base_mode": "exact",
    "head_start": "1e324e3d40ea956610cf0df627fde7e47b93749b",
    "head_end": "1e324e3d40ea956610cf0df627fde7e47b93749b",
    "upstream_end": "1e324e3d40ea956610cf0df627fde7e47b93749b",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process_traces/2026-09-03-watchdog-build/11-consult-sol-structural.md"
  ],
  "unowned_dirty": [
    "M docs/process_traces/2026-09-03-watchdog-build/01-sol-landing-report.md",
    "?? docs/process_traces/2026-09-03-watchdog-build/09-sol-fix-round-4-report.md",
    "?? docs/process_traces/2026-09-03-watchdog-build/10-delta-reaudit-round-4.md"
  ],
  "verdict": {
    "line": "STRUCTURAL REDESIGN REQUIRED",
    "findings": [
      {
        "id": "Q1",
        "severity": "blocker",
        "title": "The test boundary stops before production composition",
        "evidence": "tests/test_magistrate_watchdog.py:55-84 injects census/git/process/spawn doubles and :99-118 hand-authors the plan; the real-only path is scripts/magistrate_watchdog.py:1587-1603 -> :430-440 -> :334-342, where the merged Probes ABI fails against joulewise/night_gate.py:163-169."
      },
      {
        "id": "Q2",
        "severity": "blocker",
        "title": "One real-CLI producer-to-consumer integration test is missing",
        "evidence": "The watchdog test calls tick with fake dependencies at tests/test_magistrate_watchdog.py:691-697; installer and run-night fixtures independently write JSON at tests/test_install_night_agent.py:76-95 and tests/test_run_night.py:217-244."
      },
      {
        "id": "Q3",
        "severity": "blocker",
        "title": "Current-plan uncertainty must fail closed",
        "evidence": "D-161 keeps physics/evidence, preregistration, and plausible operator mistakes fail-closed at docs/decision_log.md:207 and :10359-10370; load_plans currently converts all exceptions into ignored events at scripts/magistrate_watchdog.py:530-552."
      },
      {
        "id": "Q4",
        "severity": "blocker",
        "title": "Pattern matching is not kill authority and the reaper lacks pair-complete survivor proof",
        "evidence": "scripts/magistrate_watchdog.py:701-722 globally adds PPID-1 lookalikes; docs/process/MAGISTRATE_WATCHDOG.md:145-172 snapshots once before TERM and does not prove every recorded PID/start pair absent after KILL."
      },
      {
        "id": "Q5",
        "severity": "blocker",
        "title": "The spawned prompt must carry the complete armed-root set",
        "evidence": "render_prompt substitutes no plan data at scripts/magistrate_watchdog.py:972-982, the template hard-codes one root at docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:10, and v2 admits any absolute root at joulewise/night_gate.py:238-253."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-03-watchdog-build/11-consult-sol-structural.md\"); s=p.read_text(encoding=\"utf-8\"); b=s[s.index(\"{\"):]; o,n=json.JSONDecoder().raw_decode(b); assert o[\"schema\"]==\"claude-codex-report/v1\" and len(b[:n].encode(\"utf-8\"))<=8192; print(\"report envelope valid\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["report envelope valid"]},
      "expected": {"exit_code": 0, "tail_regex": "^report envelope valid$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 -c 'from pathlib import Path; s=Path(\"docs/process_traces/2026-09-03-watchdog-build/11-consult-sol-structural.md\").read_text(encoding=\"utf-8\"); assert s.endswith(\"\\n\") and all(x == x.rstrip() for x in s.splitlines()); print(\"report whitespace valid\")'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["report whitespace valid"]},
      "expected": {"exit_code": 0, "tail_regex": "^report whitespace valid$"}
    }
  ],
  "flags": [
    {
      "id": "V-GAP",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No test was run: this is a report-only design consult and the preflight allowed tests only to confirm a specific claim; the round-4 execution record already supplies the relevant failures.",
      "needs": "The implementing round must first observe the proposed production-shaped test fail for the named reasons, then pass on the final integrated head."
    }
  ]
}
```

## Findings

Q1 — The structural cause is an unowned composition boundary, not simply too few unit cases and not a claim about who authored the fixtures. The watchdog suite replaces every production dependency—census, Git probe, process table, spawn, and clock—through `Dependencies` (`tests/test_magistrate_watchdog.py:55-84`), hand-builds its own plan mapping (`:99-118`), and the nearest dry-run test calls `tick` directly with that fake graph (`:691-697`). The installer suite authors a second mapping (`tests/test_install_night_agent.py:76-95`); the night-driver suite authors a third and patches `make_probes` (`tests/test_run_night.py:181-200,217-244`). Consequently no test crosses `main` → `real_dependencies` → `production_census` (`scripts/magistrate_watchdog.py:1587-1603,430-440,334-342`). The plan-pin merge added the required `Probes.measurement_head` slot (`joulewise/night_gate.py:163-169`) while the separately green watchdog graph never constructed that real adapter. B-1 had the same shape: its test proved `load_plans` and `decide` under a hand-authored mapping, not the shipped CLI. The primary defect is therefore duplicated contract construction plus absence of a production-shaped composition test; shared authorship can reinforce confirmation bias, but the file evidence establishes seam substitution, not authorship as the cause.

Q2 — Define one test, `test_watchdog_cli_consumes_production_authored_plan_set_fail_closed`, with several phases but one producer-to-consumer boundary. It creates a temporary custody parent, watchdog root, and real scratch Git measurement checkout; the sole production arming writer emits an active v2 plan there, and a byte-for-byte golden v1 artifact from the retired writer is copied as its sibling. (Today no such production writer exists: `scripts/install_night_agent.sh:39-56` only reads/validates; extracting a single arming writer is a prerequisite, and reusing any `_write_plan` test helper is forbidden.) Invoke `sys.executable scripts/magistrate_watchdog.py --custody-root <root>/magistrate` as a real subprocess twice. Assert both exits are 0 with no traceback, `state.json.state` is exactly `FENCED` or `HOLD_CENSUS` (never `HOLD_UNSAFE`), no attempt/lock exists, and exactly one `plan_retired_v1` event names the legacy root; this catches B-1 and F1. In isolated custody parents, start from writer-emitted v2 bytes and apply one named mutation—truncate JSON, then delete `measurement_head`—place a local `STOP` sentinel to make an erroneous fail-open incapable of spawning, invoke the same CLI, and assert `HOLD_UNSAFE`, no attempt/lock, and one durable error event per root; `STOPPED` or `LAUNCHING` fails. Fixture rule: no test may contain a v2 mapping literal or call `json.dump` for a plan; every v2 positive is emitted by the production writer, and every negative is a single declared mutation of bytes first round-tripped successfully through `NightPlan.from_mapping`. This is one integration test because all assertions share the same real writer/CLI/import boundary, not separate helper tests.

Q3 — A directory is not evidence merely because it is called custody, but a `*/night_plan.json` discovered at the watchdog's authoritative plan location is a preregistration-evidence candidate: until it is positively classified, it may define the no-agent interval that protects a physical measurement. D-161 explicitly retains fail-closed behavior for evidence, preregistration, plausible operator mistakes, and tool bugs (`docs/decision_log.md:207,10359-10370`; ruling `04-MAGISTRATE-RULING.md:8-16`). Recommend: IGNORE-and-record exactly once only for a plan that passes a strict legacy-v1 recognizer (not merely `raw.get("schema") == v1`) and is therefore positively retired; HOLD_UNSAFE for unreadable JSON because its authority and span are unknowable; HOLD_UNSAFE for a claimed v2 missing any required field because it is malformed current evidence; HOLD_UNSAFE for a structurally valid v2 with future `authored_epoch_s` because authorship time is part of prospective validity and the condition is either an operator mistake or a clock fault. None of the latter three is a deliberate-only adversary guard, so D-161 does not license IGNORE.

Q4 — Ancestry from the recorded interactive twin is sufficient as signal authority, but not as a completeness claim: inventory only the root and descendants reachable by PPID edges in repeated stable snapshots; never add a PID because its command resembles Claude. A legitimate child already orphaned to PID 1 will be omitted from the kill set, which is safe; the final production census then keeps the handoff failed until it is separately and explicitly attributed. Freeze the authorized inventory as `(pid,start_time,depth)` records. Before each TERM, refresh the process table and signal only an identical pair, deepest descendants first and root last; disappearance is success for that pair, while a changed start token aborts without signaling it. After the grace interval, refresh again and KILL only still-identical pairs in the same order, with an immediate pair check before each signal. Then poll fresh snapshots to a deadline and require every recorded pair absent; any identical survivor is failure. Only after pair absence may the production census run, and any census hit or census error is also failure. This removes global kill authority, bounds PID reuse, and makes “empty census” an additional safety gate rather than a substitute for recorded-survivor proof.

Q5 — Yes: render the prompt at spawn from the same successfully parsed armed-plan snapshot that governs the tick, not from a repository literal. Embed a deterministic JSON list of `(plan_id, measurement_root, measurement_head)` for every unretired, unfinished valid v2 plan, then issue one fixed instruction forbidding HEAD-moving operations in every listed root; JSON encoding avoids treating path bytes as prompt syntax. `render_prompt` currently knows only activation/custody/time/notices (`scripts/magistrate_watchdog.py:972-982`), while the schema permits any absolute root (`joulewise/night_gate.py:238-253`), so the literal at `MAGISTRATE_RELAUNCH_PROMPT.md:10` is intrinsically incomplete. Two plans with different roots are not themselves contradictory: the prompt must fence the union, and both checkouts remain frozen. What breaks is any singular-root design—choosing the earliest or last plan silently leaves the other movable, so its measurement pin can stale while the session continues. If two armed plans name different heads for the same canonical root, no checkout can satisfy both; that is `HOLD_UNSAFE` before spawn until one plan is retired or re-authored. A plan added after spawn must either trigger prompt regeneration/relaunch or be covered by an explicit runtime obligation to refresh the armed-root set before any Git operation; spawn-time capture alone cannot safely cover concurrent arming.

## Residual risk

The proposed integration test deliberately does not exercise launchd installation, a real handoff kill, or a quiet-machine night. Those remain lead-controlled gates; its purpose is narrower and structural: make the writer/CLI/night-gate composition fail in CI before those gates can be reached.
