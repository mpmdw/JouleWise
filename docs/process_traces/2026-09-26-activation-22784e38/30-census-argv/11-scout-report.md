```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "partial",
  "summary": "A test-only pgrep -lf PID split crashes on multiline argv; the production t0 census refuses a matching process without parsing its displayed PID.",
  "workspace": {
    "base_requested": "97082508",
    "base_mode": "exact",
    "head_start": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "head_end": "97082508f3648ff8575c94b0cdfcf657ba440142",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {"cause": "confirmed", "remediation": "proposed"},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect -v",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 1.295s", "OK (skipped=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=2\\)"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import subprocess,sys,time; p=subprocess.Popen([\"scripts/run_campaign\",\"-c\",\"import time\\ntime.sleep(5)\"],executable=sys.executable,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.2); r=subprocess.run([\"/usr/bin/pgrep\",\"-lf\",\"[r]un_campaign\"],capture_output=True,text=True); print(\"probe_alive\",p.poll() is None,\"pgrep_rc\",r.returncode,\"pgrep_stderr\",repr(r.stderr.strip())); p.terminate(); p.wait(timeout=3); print(\"probe_reaped\",p.poll() is not None)'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["probe_alive True pgrep_rc 3 pgrep_stderr 'sysmon request failed with error: sysmond service not found\\npgrep: Cannot get process list'", "probe_reaped True"]},
      "expected": {"exit_code": 0, "tail_regex": "probe_reaped True"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from types import SimpleNamespace as S; from joulewise import night_gate as n,arm_readiness_evidence_t0 as t; s=\"42424 python -c run_campaign\\nimport time\\n\"; exec(\"try: {int(x.split(\\\" \\\",1)[0]) for x in s.splitlines()}\\nexcept Exception as e: print(type(e).__name__,str(e))\"); exec(\"try: t._expect_absent(S(exit_code=0,stdout=s),kind=\\\"PROCESS_CENSUS\\\",label=\\\"monitor\\\")\\nexcept Exception as e: print(type(e).__name__,str(e))\"); r=n.ProbeResult(n.AGENT_CENSUS_ARGV,0,s,\"\",1); print(n.agent_census(S(run=lambda argv:r,monotonic_ns=lambda:1))[1].reason)'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ValueError invalid literal for int() with base 10: 'import'", "T0EvidenceAuthoringError fresh monitor census found a forbidden process", "night_refused_agent_present"]},
      "expected": {"exit_code": 0, "tail_regex": "night_refused_agent_present"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Live multiline pgrep/ps parser behavior was NOT EXECUTED: this sandbox returns pgrep exit 3 and denies /bin/ps. V3 and the additional parser probes used synthetic process output.",
      "needs": "Replay the focused test and harmless live probe in a process-table-capable agent session."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The queued lane asks for a pgrep -fl continuation-parser fixture; the proposed PID-only test removes that ambiguous parser while preserving the test's match-set checks.",
      "needs": "Align the lane acceptance text with the chosen fix."
    }
  ]
}
```

## Causal chain

The live-dialect test runs `pgrep -lf`, splits its output into lines, then converts the first space-delimited token of **every** line to an integer at [tests/test_arm_readiness_evidence_t0.py:2769](/Users/edr/code/JouleWise-wt-census-22784e38/tests/test_arm_readiness_evidence_t0.py:2769). An argv newline creates a continuation line without a PID, so that conversion raises `ValueError`. The [recorded full-suite failure](/Users/edr/code/JouleWise-wt-census-22784e38/docs/process_traces/2026-09-23-interactive-7ec32e8b/07-full-suite-replay-pr385.md:18) and executed synthetic probe agree.

That conversion is **test-only**. Production t0 runs the agent, browser, and monitor probes at [arm_readiness_evidence_t0.py:1733](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/arm_readiness_evidence_t0.py:1733) and checks exit status plus whether stdout is empty at [arm_readiness_evidence_t0.py:1325](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/arm_readiness_evidence_t0.py:1325). A matching process with multiline argv produces a nonempty hit and **refuses t0**; no PID is split, skipped, or misattributed there. A process that does not match a census pattern has no effect, regardless of its argv newlines. The night gate likewise refuses a hit at [night_gate.py:686](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/night_gate.py:686). The arm discovery uses PID-only `pgrep -f` at [arm_census.py:24](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/arm_census.py:24), [arm_census.py:247](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/arm_census.py:247).

Other production output consumers found in `joulewise/` and `scripts/`:

| Parser | Multiline argv outcome |
|---|---|
| [night_gate.py:705](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/night_gate.py:705), [magistrate_watchdog.py:402](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/magistrate_watchdog.py:402), [magistrate_watchdog.py:412](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/magistrate_watchdog.py:412), [night_agent_install.py:1046](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/night_agent_install.py:1046) | `pgrep -lf` hit is judged by exit status; matching process causes refusal, with no PID attribution. |
| [run_night.py:3461](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/run_night.py:3461), [run_night.py:3525](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/run_night.py:3525), [run_night.py:3552](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/run_night.py:3552) | Single-group census stays present. Batched census rejects a non-PID continuation and marks **every** group unresolved; its `ps` attribution skips malformed continuations but retains each preceding PID. Executed synthetic probe confirmed these outcomes. This is teardown, not t0. |
| [quiet_admission.py:76](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/quiet_admission.py:76), used at [sample_quiet_predicate_evidence.py:776](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/sample_quiet_predicate_evidence.py:776) | Reads `ps ... comm`, not argv; an argv newline cannot create a continuation. A *synthetic* malformed `comm` continuation raised `ValueError`, but does not model an argv newline from this command. |
| [magistrate_watchdog.py:226](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/magistrate_watchdog.py:226) | Reads `ps ... command`; keeps the first row and silently drops its continuation. The PID is not misattributed, but a role token appearing only after the newline can be missed by watchdog handoff classification. Executed synthetic probe confirmed truncation. The independent t0 `pgrep` gate remains in place. |
| [evidence_night.py:755](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/evidence_night.py:755), [measurement_liveness.py:41](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/measurement_liveness.py:41), [sample_quiet_predicate_evidence.py:206](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/sample_quiet_predicate_evidence.py:206), [mlx_runtime.py:1281](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/adapters/mlx_runtime.py:1281) | Either use one PID with bounded whitespace splitting or request `lstart`, `stat`, or `rss` without argv; no multiline-argv PID split. |
| [node_worker.py:1471](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/adapters/node_worker.py:1471), [node_worker.py:1546](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/adapters/node_worker.py:1546) | The `ps args` fallback flattens whitespace, possibly failing command identity comparison; it does not parse another PID. The second probe requests only `lstart`. |
| [fixture_orphan_census.py:67](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/fixture_orphan_census.py:67), [validate_powermetrics_fiducial.py:1118](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/validate_powermetrics_fiducial.py:1118) | The fixture census raises on a continuation and its CLI returns error 2; executed synthetic probe confirmed the raise. The fiducial snapshot skips a continuation, so text appearing only there may be missed; it is report-only. |
| [environment.py:904](/Users/edr/code/JouleWise-wt-census-22784e38/joulewise/environment.py:904), [bench_replay_start_drift.py:182](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/bench_replay_start_drift.py:182), [install_magistrate_watchdog.sh:111](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/install_magistrate_watchdog.sh:111), [quiet_mac_prep.sh:34](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/quiet_mac_prep.sh:34), [sampler-checklist.sh:41](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/ed_session/sampler-checklist.sh:41), [rail-probe.sh:45](/Users/edr/code/JouleWise-wt-census-22784e38/scripts/ed_session/rail-probe.sh:45) | Status-only, PID-only, single-field, or human-facing shell checks; none performs the failing per-line PID conversion. |

## Remediation

The safest minimal test fix is to ask `pgrep -f` for **PID-only output** while retaining its full-argv matching. The positive and negative decoys still test the real `pgrep` dialect. Existing G1/G2 tests cover the recorded service strings and pattern alternatives at [tests/test_arm_readiness_evidence_t0.py:2627](/Users/edr/code/JouleWise-wt-census-22784e38/tests/test_arm_readiness_evidence_t0.py:2627).

Unapplied diff:

```diff
diff --git a/tests/test_arm_readiness_evidence_t0.py b/tests/test_arm_readiness_evidence_t0.py
--- a/tests/test_arm_readiness_evidence_t0.py
+++ b/tests/test_arm_readiness_evidence_t0.py
@@
                     probes, _source = self._real_probe_source(
-                        "PROCESS_CENSUS", (("/usr/bin/pgrep", "-lf", pattern),)
+                        "PROCESS_CENSUS", (("/usr/bin/pgrep", "-f", pattern),)
                     )
@@
-                    reported = {int(line.split(" ", 1)[0]) for line in lines}
+                    reported = {int(line) for line in lines}
@@
-                    for line in lines:
-                        self.assertIsNotNone(re.search(pattern, line))
-                        for basename in _RECORDED_CENSUS_SERVICE_BASENAMES:
-                            self.assertNotIn(basename, line)
```

Proposed regression rows and counterfactuals:

| Row | Expected after fix | Counterfactual with current code |
|---|---|---|
| Positive decoy with multiline argv, continuation beginning `import` | Its PID appears once; test passes its membership check. | `ValueError` on `import`; **synthetic reproduction executed**. |
| Positive ordinary decoy | PID appears; membership check passes. | Passes. |
| Negative browser, monitor, and recorded-service decoys | PID absent; membership check passes. | Passes unless an unrelated multiline hit crashes the parser first. |
| Unrelated process with multiline argv | No extra output line or PID from `pgrep -f`; cannot affect the parsed match set. | A matched process’s continuation can crash the test. |
| `pgrep` error or no positive hits | Existing exit-code assertion fails the test. | Same failure. |

This changes **test output format only**, not the production census command or match population. It cannot let a matched process escape production t0. A continuation-line parser for `-lf` would satisfy the queue’s literal fixture requirement, but line-oriented text cannot unambiguously distinguish a continuation that begins with `123 ` from a new PID row. PID-only output avoids that ambiguity. The queue acceptance text should be reconciled before implementation.

## Disproved alternatives

The observed `ValueError` is not a production t0 crash: executed synthetic output made production t0 and night-gate consumers refuse, while only the test’s integer conversion raised. The harmless live process was spawned and reaped, but the sandbox denied its process-table census, so a real-output reproduction here is **NOT EXECUTED**.

The lane fix is **test-only, light gate**. Changing the separate watchdog `ps command` truncation or another production parser would be a production census change requiring its full gate; that is outside this read-only proposal.

## Residual risk

A live replay on a process-table-capable machine is still needed. The focused test reported `OK (skipped=2)` here because `/usr/bin/pgrep` could not obtain the process list.