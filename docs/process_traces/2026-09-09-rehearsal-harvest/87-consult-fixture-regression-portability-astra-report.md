```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The cadence probe rejects a sparse measured window before the sentinel runs; remove it and retain post-evaluation drift assertions.",
  "workspace": {
    "base_requested": "bdbc9e75",
    "base_mode": "exact",
    "head_start": "bdbc9e7587d13a4b24ca3ab1af6e872072e29dbb",
    "head_end": "bdbc9e7587d13a4b24ca3ab1af6e872072e29dbb",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 1,
      "should_fix": 0,
      "nit": 0
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "path": "tests/test_run_campaign.py",
        "line": 9637,
        "summary": "A non-null cadence ratio requires an internal sample gap that the nominal 112 ms mock workload does not guarantee under a 175 ms stressed sampling interval.",
        "recommendation": "Remove the controller-stage wrapper and assert strict validity, bounded drift, and 100 post samples after evaluate_member."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from joulewise.bundle_read import TracePoint, Window; from joulewise.reduce import _window_gap_stats; result=_window_gap_stats([TracePoint(t, 0.0) for t in (-0.175, 0.0, 0.175, 0.35)], Window(0.02, 0.132)); assert result[\"window_p95_sample_gap_s\"] is None and result[\"bracketing_max_sample_gap_s\"] == 0.175 and result[\"cadence_ratio\"] is None; print(\"BRACKETED_WINDOW_WITHOUT_INTERNAL_GAP=PASS\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "BRACKETED_WINDOW_WITHOUT_INTERNAL_GAP=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "BRACKETED_WINDOW_WITHOUT_INTERNAL_GAP=PASS"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from pathlib import Path; from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter; from joulewise.clock import FakeClock; from joulewise.schemas import BenchmarkConfig; payload=json.loads(Path(\"configs/examples/mock_local.json\").read_text()); payload[\"sampling\"][\"power_hz\"]=20.0; config=BenchmarkConfig.from_mapping(payload); adapter=PowermetricsTelemetryAdapter(FakeClock(), executable=\"/usr/bin/powermetrics\"); values=[adapter._capture_timeout_s(config,n) for n in (100,3,31)]; assert values == [17.5,15.0,15.0]; print(\"CAPTURE_TIMEOUTS_100_3_31=\"+str(values))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CAPTURE_TIMEOUTS_100_3_31=[17.5, 15.0, 15.0]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CAPTURE_TIMEOUTS_100_3_31="
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_member_survives_fixture_sleep_slack tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_real_powermetrics_capture_timeout_is_unchanged tests.test_idle_admission.PowermetricsFixtureTimingTests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/edr/code/JouleWise-wt-ref-308-delta']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import importlib.util, io, os, sys\nfrom pathlib import Path\nfrom unittest.mock import patch\nfrom joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter, parse_powermetrics_records\nfrom joulewise.clock import FakeClock\nfrom joulewise.schemas import BenchmarkConfig, IdleBaseline, TelemetryBackend\nimport json\npath = Path(\"tests/fixtures/fake_powermetrics_process.py\").resolve()\nspec = importlib.util.spec_from_file_location(\"timed_fixture_readonly\", path)\nfixture = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(fixture)\npayloads = []\noriginal_open = Path.open\nclass MemoryOutput(io.BytesIO):\n    def close(self):\n        pass\nfor unpaced in (False, True):\n    output = MemoryOutput()\n    now = [100.0]\n    def sleep(seconds):\n        now[0] += seconds\n    def memory_open(target, *args, **kwargs):\n        if str(target) == \"in-memory-post.plist\":\n            return output\n        return original_open(target, *args, **kwargs)\n    argv = [str(path), \"-n\", \"100\", \"-i\", \"50\", \"-o\", \"in-memory-post.plist\"]\n    if unpaced:\n        argv.append(\"--no-sleep\")\n    with patch.object(sys, \"argv\", argv), patch.dict(os.environ, {\"FAKE_POWERMETRICS_SLEEP_SCALE\": \"3.5\", \"P2038_FAKE_POWERMETRICS_MODE\": \"normal\", \"P2038_FAKE_POWERMETRICS_STATE\": \"\"}), patch.object(fixture.signal, \"signal\"), patch.object(fixture.time, \"monotonic\", lambda: now[0]), patch.object(fixture.time, \"sleep\", side_effect=sleep) as sleeper, patch.object(Path, \"open\", memory_open):\n        assert fixture.main() == 0\n        assert sleeper.call_count == (0 if unpaced else 100)\n    payloads.append(output.getvalue())\npaced, synthetic = map(parse_powermetrics_records, payloads)\nassert len(paced) == len(synthetic) == 100\nassert [r.elapsed_ns for r in synthetic] == [50_000_000] * 100\nspan = synthetic[-1].timestamp_s - synthetic[0].timestamp_s\nassert round(abs(span - 4.95), 7) == 0\nassert [r.combined_power_w for r in paced] == [r.combined_power_w for r in synthetic]\nadapter = PowermetricsTelemetryAdapter(FakeClock())\nadapter._pre_idle_records = paced[:3]\nadapter._pre_idle_quality = {\"idle_window_suspect\": False}\npayload = json.loads(Path(\"configs/examples/mock_local.json\").read_text())\npayload[\"sampling\"][\"power_hz\"] = 20.0\nconfig = BenchmarkConfig.from_mapping(payload)\nbaseline = IdleBaseline(1.0, 0.0, 5.0, 3, TelemetryBackend.POWERMETRICS)\nresults = []\nfor data in payloads:\n    with patch.object(adapter, \"_run_bounded_capture\", return_value=data):\n        results.append(adapter.measure_post_run_idle(config, baseline, None))\nassert results[0][\"idle_drift\"][\"status\"] == \"bounded\"\nassert results[0] == results[1]\nprint(\"IN_MEMORY_FIXTURE_IDENTITY=PASS; counts=100/100; sleep_calls=100/0\")\nprint(f\"SYNTHETIC_SPAN={span!r}; DRIFT_IDENTITY=PASS\")\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "IN_MEMORY_FIXTURE_IDENTITY=PASS; counts=100/100; sleep_calls=100/0",
          "SYNTHETIC_SPAN=4.950000047683716; DRIFT_IDENTITY=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DRIFT_IDENTITY=PASS"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The consult and read-only probes are complete. Full regressions stopped during import because no temporary directory is writable; no Linux replay or end-to-end pass is claimed.",
      "needs": "Lead applies the proposed test-only replacement and replays the affected tests, original four callers, and sleeping-fixture counterfactual in writable Linux and Mac environments."
    }
  ]
}
```

## Findings

**F1 — blocker: the regression requires enough scheduler delay to manufacture a non-null cadence ratio.** The reported Linux failure occurs before the bounded sentinel is invoked. Consequently, this CI result does not demonstrate a bounded-capture timeout.

### Mechanism

[`_window_gap_stats`](/Users/edr/code/JouleWise-wt-ref-308-delta/joulewise/reduce.py:1072) computes:

1. Gaps between consecutive points **whose two endpoints both lie inside the measured window**.
2. The gaps bracketing the window’s start and end.
3. `duration / max(internal_gap_p95, bracketing_gap_max)` only when both components exist and the denominator is positive.

An empty internal-gap list makes `_p95([])` return `None`. Having many samples elsewhere, or successfully bracketing both window edges, does not prevent this.

The producer creates exactly the conditions that expose that distinction:

- [`_produce_admission_powermetrics_bundle`](/Users/edr/code/JouleWise-wt-ref-308-delta/tests/test_controller.py:754) loads `mock_local.json`, sets telemetry to 20 Hz with a 1.5-second admission request, and injects **`SystemClock()`**.
- The runtime remains `MockRuntimeAdapter`. Its configured workload requests `32 × 0.001 + 8 × 0.010 = 0.112` seconds of sleeping. Those runtime sleeps do **not** read `FAKE_POWERMETRICS_SLEEP_SCALE`.
- The separate continuous sampler does read that variable. At scale 3.5, each record requires a sleep of at least approximately `0.05 × 3.5 = 0.175` seconds, plus processing overhead.
- On a normally scheduled fast host, a roughly 112 ms measured window cannot contain both endpoints of a 175 ms sample gap. It can contain zero or one sample endpoint while still having samples on both sides.
- On the MacBook, actual runtime sleeps and controller execution take longer. The eight separate 10 ms runtime sleeps can incur substantial scheduling delay. The relative window length and sampler phase sometimes allow an internal gap. The passing Mac run establishes that the required geometry happened there; it does not establish a portable invariant.

**The platform-dependent inputs are the actual measured-window duration, actual inter-record intervals, and their relative phase.** This is not a Linux-specific fake-monotonic/wall-clock mismatch. The retry producer uses real clocks in both processes. Only the separate in-process identity test mocks monotonic time.

The timestamp and lifecycle chain is:

- The fixture records elapsed intervals using real `time.monotonic()` and native dates using `datetime.now(UTC)`.
- The adapter derives the measured anchor from native records and paired controller stamps, then reconstructs record endpoints as the selected first endpoint plus accumulated elapsed intervals.
- [`samples_from_records`](/Users/edr/code/JouleWise-wt-ref-308-delta/joulewise/adapters/powermetrics.py:2009) produces rail samples with those timestamps and interval supports.
- [`_stage_measured_run`](/Users/edr/code/JouleWise-wt-ref-308-delta/joulewise/controller.py:1251) stamps `sampling_started` after the sampling handoff and stamps `sampling_stopped` immediately after the runtime returns.
- The one-second post-window dwell occurs **after the stop stamp**. It provides trailing samples without lengthening the measured window.
- `_stop_sampling_once` assigns `execution._samples` and `_uncertainty_evidence`. Both marker events are present before `_stage_idle_drift_sentinel` is called. This is not an asynchronous population race.
- The test discards interval supports when constructing `TracePoint(t, 0.0)`. Its probe therefore is not even the exact curve representation used by production reduction.

The supplied CI tail proves that `ratio` was `None`; it does not include the actual window and gap statistics needed to distinguish every possible `None` branch. The short-window mechanism above follows directly from the configuration and explains the fast-host failure. I independently demonstrated `None` with both edges bracketed using the real reducer function.

Finally, [`_run_lifecycle`](/Users/edr/code/JouleWise-wt-ref-308-delta/joulewise/controller.py:848) calls the wrapper before the original sentinel method can execute `_begin_stage("idle_drift_sentinel")`. The assertion therefore reaches the outer unexpected-error handler with the current stage still `measured_run`. The clock-evidence producer’s initial `post_idle_unavailable` value remains unchanged, and no post plist exists. That accounts for all three reported observations: `measured_run` failure, unknown drift, and `raw_post == []`.

### Assumption audit

There are **four test methods across the three named areas**. The table distinguishes host-dependent assumptions from deterministic assertions.

Here, “1×” and “7×” mean the inherited fixture multiplier on an otherwise normally scheduled host. The regression floors 1 to 3.5; the identity test forces 3.5; the real-timeout test forces 1. Additional host scheduling delay remains separate.

| Test / assumption | Linux | At 1× | At 7× |
|---|---|---|---|
| **Retry regression: stress is at least 3.5.** `max(3.5, float(env))`. | Portable for ordinary numeric inputs. | Actually runs at 3.5. | Runs at 7. |
| **Retry regression: final baseline contains 30 admission records.** Requested count is `ceil(1.5 / .05)`. | Derived from configuration, provided admission capture completes. | Same. | Same. |
| **Retry regression: post count is 100.** Thirty stressed intervals span at least about 5.25 seconds, activating the five-second cap. | Yes; CI’s 5.338-second baseline confirms it. | Yes because of the floor. | Yes if admission completes. |
| **Shared helper: every bounded capture has 100 records.** Removed in round 2. | **False without the regression’s stress floor.** | Ordinary unstressed callers produce roughly 30–31; actual elapsed time determines the count. | Generally reaches the cap, subject to successful admission. |
| **Retry regression: cadence is non-null.** Requires an internal gap and both edge brackets. | **False on the supplied run.** | Still false/not guaranteed because effective scale is 3.5. | Even less supportable: nominal sampler gap is 350 ms while runtime remains nominally 112 ms. |
| **Retry regression: large total sample count implies an internal measured-window gap.** Implicit in the probe. | False. Admission and trailing samples lie outside the measured window. | False. | False. |
| **Retry regression: endpoint-only probe equals production cadence representation.** Supports are discarded. | Not generally true. | Same discrepancy. | Same discrepancy. |
| **Retry regression: markers and samples exist before sentinel entry.** | Guaranteed by the successful preceding lifecycle path, not Mac timing. Missing markers would raise `KeyError`, not produce this assertion. | Same. | Same if earlier stages finish. |
| **Retry regression: cadence and clock-anchor values remain identical across this one sentinel stage.** | Reasonable same-run invariant; `None == None` is valid. The extra non-null requirement is the defect. | Same. | Same. |
| **Retry regression: exactly one sentinel wrapper completes.** | Deterministic for the successful lifecycle; the current pre-call assertion prevents completion. | Same. | Same. |
| **Retry regression: strict validity and bounded drift.** | Appropriate acceptance assertions after evaluation. Strict validity does not itself require non-null cadence or a succeeded summary. Drift uses fixture power/quality evidence. | Same. | Same, subject to earlier capture deadlines. |
| **Retry producer: continuous admission finishes within its deadline.** Each slice waits for 31 new frames under a 15-second deadline. | Normally ample margin at 3.5: approximately 5.425 seconds of requested sleeping. | Effective 3.5 in the regression; approximately 1.55 seconds in unstressed shared callers. | Approximately 10.85 seconds before overhead; additional host delay can exhaust the margin. |
| **Retry producer: capability/readiness/stop and unpaced serialization finish within existing deadlines.** | Normal process/infrastructure assumptions, not guaranteed under arbitrary starvation. The unpaced sentinel removes per-record sleeping, not all execution cost. | Same. | Continuous stream remains slower; the sentinel still does not sleep. |
| **Retry producer: normal fixture mode and isolated invocation state.** The helper does not clear inherited `P2038_FAKE_POWERMETRICS_MODE`/`STATE`. | Environment assumption, not an OS difference. Non-default settings can change the scenario. | Same. | Same. |
| **Timeout-formula test: results are exactly 17.5 and 15.0.** | Portable arithmetic; independently passed. No elapsed-time observation. | Unaffected by scale. | Unaffected by scale. |
| **Timeout-formula test: `/usr/bin/powermetrics` exists.** | **Not actually required.** The constructor stores the string; the test only calls `_capture_timeout_s`. | Same. | Same. |
| **Identity test: 100 paced sleeps, each `.05 * 3.5`; zero unpaced sleeps.** | Deterministic: `sleep` and monotonic time are mocked. | Inherited scale ignored. | Inherited scale ignored. |
| **Identity test: synthetic count 100 and elapsed intervals exactly 50,000,000 ns.** | Explicit fixture-loop and integer-arithmetic contracts. | Same. | Same. |
| **Identity test: synthetic endpoint span approximately 4.95 seconds at seven decimal places.** | Passes at current epoch magnitudes; observed `4.950000047683716`. It depends on floating-point epoch precision, not Mac scheduling. | Same. | Same. |
| **Identity test: matching power sequences and identical drift dictionaries.** | Portable for these inputs. Drift does not consume sentinel timestamps or elapsed intervals. This is an invariant, not independent proof of timestamp neutrality. | Same. | Same. |
| **Identity test: mocked monotonic time agrees with actual wall time.** | It does not, and this test does not require agreement. Native dates remain real; the drift comparison ignores that relationship. | Same. | Same. |
| **Identity test: fresh fixture state, no signal interruption, output safely overwritten between cases.** | Fresh module, mocked signal registration, and isolated output establish these conditions. The second payload is read before reuse matters. | Same. | Same. |
| **Real-timeout test: sleeping child exceeds 0.75 seconds.** Requests 100 sleeps of 50 ms. | Portable under normal execution: five seconds of requested sleeping exceeds the shortened deadline. | Explicitly forced to 1. | Still explicitly forced to 1. |
| **Real-timeout test: exactly one captured `TimeoutExpired`, exact unknown result, empty pending registry.** | Derived from one direct bounded capture and `context=None` cleanup. No capability probe is invoked on this path. | Same. | Same. |
| **Filesystem/process prerequisites across tests.** Writable temporary directories, readable fixture files, Python subprocess execution, and POSIX signal/process behavior. | Supported by ordinary Linux and Mac test environments. No Mac-specific filename ordering, case behavior, or real powermetrics binary is needed. | Independent of scale. | Independent of scale. |
| **Diagnostic filesystem scan.** Sorted recursive log/post-plist discovery under the test’s isolated runs root. | Diagnostic only; does not establish capture identity or assert an exact file count. | Same. | Same. |

Two limits deserve explicit separation from the present blocker:

- A 7× fixture multiplier **plus** substantial host oversleep can exceed the unchanged continuous-admission deadline. “Platform-independent” cannot mean success under unlimited scheduler delay.
- The identity test’s seven-decimal epoch subtraction is unnecessarily tied to floating-point magnitude. It passes now on both platforms; a relative elapsed-time assertion would age better.

### Minimal replacement

Replace the entire `test_retry_member_survives_fixture_sleep_slack` method with this. Leave the shared helper’s round-2 derived-count handling and the other three methods unchanged.

```python
def test_retry_member_survives_fixture_sleep_slack(self) -> None:
    # Original defect: the sleeping 100 x 50 ms post-idle fixture exceeds
    # the unchanged 17.5 s capture timeout under >=3.5x simulated slack.
    # Continuous admission/measured sampling remains paced.
    scale = max(
        3.5,
        float(os.environ.get("FAKE_POWERMETRICS_SLEEP_SCALE", "3.5")),
    )
    with patch.dict(
        os.environ,
        {"FAKE_POWERMETRICS_SLEEP_SCALE": str(scale)},
    ):
        evaluation = self._produced_retry_member(
            "timer-slack",
            attempt1_records=_clean_idle_records(),
            attempt2_records=_clean_idle_records(),
        )

    self.assertIs(
        evaluation.strict_valid,
        True,
        evaluation.validation_problems,
    )
    drift = evaluation.metadata["uncertainty_evidence"]["idle_drift"]
    self.assertEqual(
        drift["status"],
        "bounded",
        (drift, evaluation.validation_problems),
    )
    self.assertEqual(drift["post_sample_count"], 100, drift)
```

This removes `checked_sentinel`, its controller patch, `stages_checked`, and the diagnostic scan introduced to explain its failure. It keeps the stress floor, real subprocess deadline, strict validation, bounded-drift requirement, and derived 100-record expectation.

**Defect discrimination remains:** restoring the sleeping bounded fixture while retaining the scale hook requests at least 17.5 seconds of sleeps, plus child startup/serialization, against the unchanged 17.5-second timeout. The resulting `post_idle_unavailable` fails the bounded-drift assertion. At 7× the sleeping sentinel requests 35 seconds. The lead should replay that counterfactual explicitly; I could not execute it here.

**Coverage removed:** the explicit same-stage cadence/clock-anchor immutability check and the exact wrapper-completion count. The non-null cadence assertion never represented this lane’s acceptance. The removed same-stage checks were additional coverage, so the ledger should stop claiming that this regression provides them.

**Coverage retained:** real controller/adapter execution, raw sentinel persistence and strict re-derivation, drift evidence identity, production timeout arithmetic, and deliberate real-`TimeoutExpired` handling. Strict validation already re-derives the stored clock anchor from paired stamps and measured raw records at [`cli.py`](/Users/edr/code/JouleWise-wt-ref-308-delta/joulewise/cli.py:1290). Sentinel drift re-derivation reads power values and GPU quality at [`cli.py`](/Users/edr/code/JouleWise-wt-ref-308-delta/joulewise/cli.py:1369).

I would **not** compare exact cadence/clock fields with a separately executed paced control run. Independent runs have different epochs, anchors, scheduling, and sample phases; even cadence nullability can differ. Such equality would introduce another timing assumption. A paired replay of identical measured bytes could support that comparison, but it is unnecessary for this fix.

### Same-signature statement and ledger note

**Same signature: repeated.** Both failures promote a host-dependent property into a fixed test invariant and then turn the assertion into sentinel unavailability. Round 1 assumed every shared-helper sentinel had 100 records; the surviving regression assumes every stressed measured window contains an internal sample gap. The cadence assertion originated in the initial implementation and survived round 2—it was not introduced by round 2’s count correction.

Suggested ledger paragraph:

> Round 3 escalated to a read-only Astra consult under the standing two-consecutive-round same-signature rule. Round 1’s unconditional 100-record pin was refuted by delta 79 because unstressed baseline duration is host-dependent. Round 2 removed that pin, but Linux CI then exposed the same class of assumption in the original cadence probe: a nominal 112 ms mock workload need not contain an internal gap from the sampler paced at 175 ms or slower. The assertion ran before the sentinel stage, causing a measured_run failure and leaving the initial post_idle_unavailable evidence with no post plist. Delta 82 established closure of the count-pin defect statically, not portability of the inherited cadence assertion. The consult recommends removing that probe and retaining post-evaluation strict validity, bounded drift, and 100 post samples under the existing stress floor, alongside the timeout and drift-identity tests. Production timeouts and strict comparisons remain unchanged; lead replay on writable Linux/Mac environments and the sleeping-fixture counterfactual remain required.

### Command tails

Exact replay commands appear in the envelope.

- **V1 — reducer counterexample, exit 0:** `BRACKETED_WINDOW_WITHOUT_INTERNAL_GAP=PASS`
- **V2 — actual timeout implementation, exit 0:** `CAPTURE_TIMEOUTS_100_3_31=[17.5, 15.0, 15.0]`
- **V3 — four targeted methods, exit 1 during import:** `FileNotFoundError: [Errno 2] No usable temporary directory found ...`
- **V4 — actual fixture and drift consumer, with output redirected to memory, exit 0:** `IN_MEMORY_FIXTURE_IDENTITY=PASS; counts=100/100; sleep_calls=100/0` and `SYNTHETIC_SPAN=4.950000047683716; DRIFT_IDENTITY=PASS`

`git diff --stat 21e31107..HEAD -- joulewise scripts` produced no production diff. The detached worktree remained clean at `bdbc9e7587d13a4b24ca3ab1af6e872072e29dbb`. No files were modified.

## Residual risk

The proposed replacement has not received an end-to-end replay here. The next exact step is for the lead to apply it, run the affected methods and four original shared-helper callers at scales 1, 3.5, and 7 in writable environments, and confirm that restoring sleeping bounded captures fails specifically through the post-idle timeout. No hardware validation or claim-eligibility result is implied.