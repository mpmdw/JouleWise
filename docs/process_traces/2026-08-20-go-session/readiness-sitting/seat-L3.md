```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "L3 is STILL-OPEN: an executed orphan escape remains undetected, two stable ED rows are non-closed, and coverage is unverified.",
  "workspace": {
    "base_requested": "5bd7acf",
    "base_mode": "exact",
    "head_start": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "head_end": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "upstream_end": "b9e197a61e884ee1040bcbc6f9f1092a7c027282",
    "branch": "HEAD detached at 5bd7acf; main/origin/main advanced during review"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "seat": "L3-CAPTURE-TELEMETRY-xhigh",
    "result": "STILL-OPEN",
    "charter_component_disposition": "NOT-READY",
    "coverage": {
      "numerator": 14,
      "denominator": 21,
      "disposition": "UNVERIFIED"
    },
    "ed_rows": {
      "ED-L3-1": "NOT-READY",
      "ED-L3-2": "READY (narrow SIGTERM-relay observation only)",
      "ED-L3-3": "UNVERIFIED",
      "ED-L3-4": "READY (current build/model observation)"
    },
    "findings": [
      {
        "id": "L3-F1",
        "severity": "blocker",
        "disposition": "NOT-READY",
        "evidence": "_stop_process still SIGKILLs only the relay; executed F-B left the SIGTERM-ignoring grandchild alive."
      },
      {
        "id": "L3-F2",
        "severity": "should_fix",
        "disposition": "NOT-READY",
        "evidence": "Step 2 still points to a checklist-free docstring instead of the repo script."
      },
      {
        "id": "L3-F3",
        "severity": "should_fix",
        "disposition": "NOT-READY",
        "evidence": "Qualification remains 1 Hz; the attached 100 ms evidence is about 113 ms realized and has no planning disposition."
      },
      {
        "id": "L3-F4",
        "severity": "nit",
        "disposition": "open",
        "evidence": "Related-work boundary language remains unchanged."
      },
      {
        "id": "L3-F5",
        "severity": "nit",
        "disposition": "open",
        "evidence": "samplers_available still echoes the requested list."
      },
      {
        "id": "L3-COV",
        "severity": "blocker",
        "disposition": "UNVERIFIED",
        "evidence": "Independent current-head universe is 14/21 examined; the prior 25/29 is self-nominated and misses post-audit surfaces."
      },
      {
        "id": "L3-D146-ERA",
        "severity": "should_fix",
        "disposition": "UNVERIFIED",
        "evidence": "The D-146 v3 capture-era flip is now on main but has no L3 delta re-audit."
      },
      {
        "id": "L3-D149",
        "severity": "blocker",
        "disposition": "NOT-READY",
        "evidence": "No-hands automation removes the assumed observer while the GO evaluator remains unbuilt."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git log --oneline -3 && git rev-parse HEAD main origin/main && git merge-base --is-ancestor b7e5730 HEAD && git merge-base --is-ancestor 0e96dbb HEAD && git merge-base --is-ancestor e22e658 HEAD && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "5bd7acf Merge pull request #160 from mpmdw/integration/phase2-transaction",
          "b9e197a61e884ee1040bcbc6f9f1092a7c027282",
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5bd7acf|HEAD \\(no branch\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "! rg -n 'census|pgrep|orphan' joulewise/adapters/powermetrics.py joulewise/controller.py && sed -n '1664,1671p' joulewise/adapters/powermetrics.py && sed -n '17,21p' docs/phase_2/ed-qualification-session.md && sed -n '106,110p' scripts/ed_session/sampler-checklist.sh",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "process.kill()",
          "its items live in the sampler module docstring",
          "\"-i\", \"1000\", \"-n\", \"5\","
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "process\\.kill|1000"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -c $'import os, signal, subprocess, sys, time\\nfrom joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter\\nchild_code = \"import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)\"\\nrelay_code = \"import os, signal, subprocess, sys, time\\\\nchild = subprocess.Popen([sys.executable, \\'-c\\', \" + repr(child_code) + \"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\\\\ntime.sleep(0.25)\\\\nprint(child.pid, flush=True)\\\\ndef forward(_sig, _frame):\\\\n    os.kill(child.pid, signal.SIGTERM)\\\\nsignal.signal(signal.SIGTERM, forward)\\\\nwhile True: time.sleep(1)\"\\nproc = subprocess.Popen([sys.executable, \"-c\", relay_code], stdout=subprocess.PIPE, text=True)\\nchild_pid = int(proc.stdout.readline().strip())\\ntry:\\n    started = time.monotonic()\\n    PowermetricsTelemetryAdapter._stop_process(proc)\\n    elapsed = time.monotonic() - started\\n    os.kill(child_pid, 0)\\n    print(f\"F-B PASS: relay killed after {elapsed:.1f}s; SIGTERM-ignoring grandchild {child_pid} survived\")\\nfinally:\\n    try: os.kill(child_pid, signal.SIGKILL)\\n    except ProcessLookupError: pass\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "F-B PASS: relay killed after 10.0s; SIGTERM-ignoring grandchild 84831 survived"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "F-B PASS: relay killed after 10\\.0s; SIGTERM-ignoring grandchild [0-9]+ survived"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c $'import glob, json\\nvalues=[]\\nfor path in glob.glob(\"/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/**/instrument_evidence.json\", recursive=True):\\n s=json.load(open(path))[\"clock_anchor\"][\"clock_stamps\"]; values.append(s[\"post_parse\"][\"epoch_s\"]-s[\"sampling_stopped\"][\"epoch_s\"])\\nprint(f\"count={len(values)} min={min(values):.4f} max={max(values):.4f} grace=10.0000\")\\nassert len(values)==10 and max(values)<10\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "count=10 min=0.0047 max=0.0228 grace=10.0000"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "count=10 .* max=0\\.0228 .* grace=10\\.0000"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest -q tests.test_adapters_powermetrics tests.test_audit_powermetrics_parser tests.test_capture_pipeline_era",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 17 tests in 4.102s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 17 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "python3 -c $'from pathlib import Path\\nfrom joulewise.adapters.powermetrics import parse_powermetrics_records\\npath=Path(\"/Users/edr/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/sampler-checklist-20260818T011840Z.plist\")\\nrecords=parse_powermetrics_records(path.read_bytes())\\nprint(f\"current_parser PASS records={len(records)} elapsed_ns={records[0].elapsed_ns}\")\\nassert len(records)==5\\n' && sw_vers -buildVersion && system_profiler SPHardwareDataType | rg 'Model Identifier'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "current_parser PASS records=5 elapsed_ns=1011352000",
          "25F84",
          "Model Identifier: Mac15,9"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "current_parser PASS records=5.*25F84.*Mac15,9"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main/origin/main advanced from 5bd7acf to b9e197a during review; the added commit is RUN_STATE/README only and no enumerated L3 source changed.",
      "needs": "Seal this ruling explicitly to 5bd7acf or repeat the final-head check at b9e197a."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "tests.test_powermetrics_fiducial was started but no terminal result returned through the execution interface; it is excluded from the passing-test claim.",
      "needs": "Run that module in a bounded independent runner if its result is needed."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No L3 credit relies on the _v3 family: D-148.5 ruled its fuse to lapse and compelled a _v4 re-freeze with registry install.",
      "needs": "Apply this seat's open findings to the _v4 transaction and re-audit its final head."
    }
  ]
}
```

## Findings

Verdict: **STILL-OPEN** — charter component disposition **NOT-READY**. There is no conditional pass.

The strongest reason is F1: the current measured-run stop path still kills only the relay, and the executed falsifier left a SIGTERM-ignoring sampler grandchild alive after the ten-second escalation. With no adapter/controller census, that sampler can contaminate later members without a fail-closed signal. [powermetrics.py:1664](./joulewise/adapters/powermetrics.py:1664)

- `L3-F1` — escalated to blocker. No measured-run census exists; F-B reproduced the orphan. D-149 makes this worse by removing the human observer while its evaluator is absent. [ROW-L3.md:580](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-L3.md:580), [TASK_QUEUE.md:373](./TASK_QUEUE.md:373)

- `L3-F2` — NOT-READY. Step 2 still names a checklist-free module docstring and `/tmp` staging rather than the source script. The live checklist therefore cannot satisfy ED-L3-1’s stated precondition. [ed-qualification-session.md:17](./docs/phase_2/ed-qualification-session.md:17), [30-ED-QUALIFICATION-rows.md:379](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/30-ED-QUALIFICATION-rows.md:379)

- `L3-F3` — NOT-READY. The script still captures only at 1 Hz, while the primary 100 ms bundles show 0.112–0.114 s realized cadence. No rollover, drain-budget, or sample-count re-derivation assesses that variance. [sampler-checklist.sh:108](./scripts/ed_session/sampler-checklist.sh:108), [ROW-L3.md:195](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-L3.md:195)

- `L3-F4` and `L3-F5` — remain open nits: the related-work SoC wording remains, and `samplers_available` remains request-derived. [related_work_draft.md:19](./docs/paper/related_work_draft.md:19), [powermetrics.py:1183](./joulewise/adapters/powermetrics.py:1183)

- Coverage is **14/21, UNVERIFIED**, independently enumerated from current-head implementation, qualification scripts/docs, D-149 state, five focused test surfaces, and four ED primary-evidence sets. Seven units were not examined to full depth: controller lifecycle, production cadence configuration, arm-time census, rail script, runbook, `test_powermetrics`, and terminal `test_powermetrics_fiducial`. The old 25/29 denominator is not reusable; it is mixed-unit and predates the D-146 v3 capture change. [ROW-L3.md:27](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-L3.md:27), [ROW-P-PROGRAM.md:12](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-P-PROGRAM.md:12)

- D-146’s four-site capture-era v3 change is now merged, correcting the packet’s former “branch-only” statement but not supplying an L3 delta re-audit. [powermetrics.py:525](./joulewise/adapters/powermetrics.py:525), [ROW-L3.md:273](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-L3.md:273)

ED-row adjudication:

- `ED-L3-1`: **NOT-READY**. The live run is real, but the row explicitly requires WO-L3-2 and WO-L3-3 first; neither exists. [30-ED-QUALIFICATION-rows.md:369](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/30-ED-QUALIFICATION-rows.md:369)

- `ED-L3-2`: **READY for its narrow normal-relay condition.** I directly checked ten custody bundles: post-parse minus sampling-stop was 4.7–22.8 ms, below the 10 s grace. This does not close F1’s missing post-teardown census or test the SIGKILL branch. [ROW-L3.md:451](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-L3.md:451)

- `ED-L3-3`: **UNVERIFIED**. Four real arms exist, but the CPU differential is negative under concurrent replay plus charge transition, and the explanatory note was lead-restored after the original paste was overwritten. A clean rerun is required. [30-ED-QUALIFICATION-rows.md:445](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/30-ED-QUALIFICATION-rows.md:445)

- `ED-L3-4`: **READY as of this audit.** Current parser accepted the live plist (5 records), primary evidence records `Mac15,9` / `25F84`, and the current host reports the same model/build. It must reopen on a future OS update. [ROW-L3.md:543](./docs/process_traces/2026-08-19-prep-sprint/ready-packet/rows/ROW-L3.md:543)

Sibling-assembly adjudication: the later detailed `ROW-L3.md` wins on ED-L3-2 and ED-L3-4 because it identified primary custody later omitted by `12-ROW-L3-capture-telemetry.md`; direct probes confirm the ten relay bundles and binding data. The sibling remains correct that neither row was formally labelled closed in repository records. Its F2 staging concern is narrowed: the script self-stages, but the incorrect checklist-home pointer remains. The sibling’s branch-only statements are now historical because `5bd7acf` contains D-146/D-149.

P-13 was cured at the requested `5bd7acf`: the Phase-2 transaction is in its ancestry. The subsequent `b9e197a` upstream docs-only move means this report remains attached to `5bd7acf`. The D-148.5 ruling is also accounted for: current registry remains v1; install is deferred to `_v4`, and `_v3` receives no armability credit because the ruling compels lapse and re-freeze. [MAGISTRATE-RULING.md:23](./docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:23)

## Residual risk

I did not perform any new quiet-Mac measurement. The complete 100 ms raw-plist parser replay and terminal fiducial-module test result remain outstanding; neither could reverse the NOT-READY verdict.