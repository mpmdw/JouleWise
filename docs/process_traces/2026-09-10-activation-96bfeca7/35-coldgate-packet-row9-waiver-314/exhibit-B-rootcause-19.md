```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Probable bench cause: the controller fixture still sleeps through its post-idle capture; timeout leaves unknown drift plus salvaged raw samples that strict validation derives as bounded.",
  "workspace": {
    "base_requested": "078a13a4",
    "base_mode": "exact",
    "head_start": "078a13a461abd124c29796798da5107fe00190a6",
    "head_end": "078a13a461abd124c29796798da5107fe00190a6",
    "upstream_end": "078a13a461abd124c29796798da5107fe00190a6",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "cause": "probable",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_controller -k retry_promotes",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3.13 -B -m unittest tests.test_controller -k retry_promotes",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -B -c 'import json, math, os, subprocess, sys, time\nfrom pathlib import Path\nfrom unittest.mock import patch\nfrom joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter as Adapter, parse_powermetrics_records as parse, decode_rich_telemetry as rich, idle_window_gpu_quality as quality, duration_weighted_mean_and_sample_variance as moments\nfrom joulewise.clock import FakeClock\nfrom joulewise.schemas import BenchmarkConfig, IdleBaseline, TelemetryBackend\nfrom joulewise.uncertainty_evidence import derive_idle_drift_evidence as derive\nfixture=Path(\"tests/fixtures/fake_powermetrics_process.py\").resolve()\nchild=\"\"\"import runpy,sys\nfrom pathlib import Path\nns=runpy.run_path(sys.argv[1],run_name=\"fixture_pipe\")\noriginal=Path.open\nPath.open=lambda self,*a,**k: sys.stdout.buffer if str(self)==\"PIPE_ONLY\" else original(self,*a,**k)\nsys.argv=[sys.argv[1],*sys.argv[2:]]\nraise SystemExit(ns[\"main\"]())\n\"\"\"\nenv=dict(os.environ,PYTHONDONTWRITEBYTECODE=\"1\",FAKE_POWERMETRICS_SLEEP_SCALE=\"3.5\",P2038_FAKE_POWERMETRICS_MODE=\"normal\")\nenv.pop(\"P2038_FAKE_POWERMETRICS_STATE\",None)\ndef capture(count, unpaced=False, timeout=17.5):\n    argv=[sys.executable,\"-B\",\"-c\",child,str(fixture),\"-n\",str(count),\"-i\",\"50\",\"-o\",\"PIPE_ONLY\"]\n    if unpaced: argv.append(\"--no-sleep\")\n    start=time.monotonic()\n    try:\n        p=subprocess.run(argv,capture_output=True,timeout=timeout,env=env,check=True)\n        return p.stdout,None,time.monotonic()-start\n    except subprocess.TimeoutExpired as exc:\n        return exc.stdout or b\"\",exc,time.monotonic()-start\npre,exc,seconds=capture(30)\nassert exc is None\nrecords=parse(pre)\npowers=[r.combined_power_w for r in records]\nintervals=[r.elapsed_ns/1e9 for r in records]\nmean,var=moments(powers,intervals)\nduration=math.fsum(intervals)\npayload=json.loads(Path(\"configs/examples/mock_local.json\").read_text())\npayload[\"sampling\"].update(power_hz=20.0,idle_seconds=1.5)\nconfig=BenchmarkConfig.from_mapping(payload)\nbaseline=IdleBaseline(power_w_mean=mean,power_w_stddev=math.sqrt(var),duration_s=duration,sample_count=30,telemetry_backend=TelemetryBackend.POWERMETRICS)\nadapter=Adapter(FakeClock(),executable=\"/synthetic\")\nadapter._pre_idle_records=records\nadapter._pre_idle_quality=quality(rich(pre))\ncount=max(3,math.ceil(max(.15,min(5.,duration))/.05))\nprint(json.dumps(dict(python=sys.version.split()[0],baseline_duration=duration,baseline_mean=mean,pre_count=30,post_requested=count,timeout=adapter._capture_timeout_s(config,count),pre_wall_seconds=seconds,epoch_ulp=math.ulp(time.time()))),flush=True)\nfor unpaced in (False,True):\n    data,exc,seconds=capture(count,unpaced,adapter._capture_timeout_s(config,count))\n    def captured(*a,**k):\n        if exc: raise exc\n        return data\n    with patch.object(adapter,\"_run_bounded_capture\",side_effect=captured):\n        stored=adapter.measure_post_run_idle(config,baseline,None)\n    post=parse(data)\n    expected,guard,bound=derive(pre_power_w=powers,post_power_w=[r.combined_power_w for r in post],pre_power_w_mean=mean,pre_idle_window_suspect=quality(rich(pre))[\"idle_window_suspect\"],post_idle_window_suspect=quality(rich(data))[\"idle_window_suspect\"])\n    print(json.dumps(dict(unpaced=unpaced,wall_seconds=seconds,exception=type(exc).__name__ if exc else None,post_count=len(post),stored_idle=stored[\"idle_drift\"],stored_bound=stored.get(\"idle_drift_bound_w\"),expected_idle=expected,expected_bound=bound,mismatch_idle=stored[\"idle_drift\"]!=expected,mismatch_bound=stored.get(\"idle_drift_bound_w\")!=bound)),flush=True)\n'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?s)\"exception\": \"TimeoutExpired\".*\"mismatch_idle\": true, \"mismatch_bound\": true.*\"unpaced\": true.*\"mismatch_idle\": false, \"mismatch_bound\": false"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --exit-code HEAD -- tests/fixtures; git rev-parse HEAD; git rev-parse refs/remotes/origin/main; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Both targeted unittest invocations stopped in setUp because the read-only sandbox cannot create a temporary directory. Pipe-only fixture probes reproduced the timeout/mismatch and unpaced cure under Python 3.14.7 and 3.13.1. The specific failed bench bundle and CI bundle were unavailable; their exact scalar values were not independently recovered.",
      "needs": "Lead captures the targeted test's post-capture exception, stored drift, requested count and salvaged raw count in a writable checkout."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A real timed-out capture with sufficient salvaged samples can reach the same producer/validator disagreement. This does not establish false rejection of a complete healthy bundle or invalidate existing G2-a members merely because they were reduced on this Mac.",
      "needs": "Keep actual incomplete captures non-claim-bearing; separately adjudicate whether capture-outcome custody and strict validation need explicit alignment."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Same broad host-timing-dependent fixture class as reports 87 and 99; immediate mechanism is recurrence of the already diagnosed sleeping-sentinel timeout, whose cure remains confined to the campaign-test helper.",
      "needs": "Lead decides recurrence accounting and escalation."
    }
  ]
}
```

## Causal chain

**The evidence points to a sleeping-fixture timeout, not an epoch-dependent floating-point disagreement.** The mechanism is reproduced; attribution to the particular 05:05 bench failure remains probable because its bundle was unavailable and filesystem restrictions prevented the original test from reaching its body.

The assertion is [tests/test_controller.py:1675](/Users/edr/code/JouleWise-wt-gate-sweep-b/tests/test_controller.py:1675), inside the method beginning at line 1599:

```python
self.assertEqual(validate_bundle(bundle_path, strict=True), [])
fresh = reduce_bundle(bundle_path)
self.assertEqual(fresh.status, RunStatus.SUCCEEDED)
```

Thus the reported assertion fails **before the explicit fresh reduction**. The two messages originate in [joulewise/cli.py:1405](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/cli.py:1405), rather than `reduce.py`:

```python
if idle != expected_idle:
    problems.append(
        "strict: uncertainty evidence: idle_drift does not match pre/post raw sentinel derivation"
    )
```

```python
if metadata.get("idle_drift_bound_w") != expected_bound:
    problems.append(
        "strict: uncertainty evidence: idle_drift_bound_w does not match effective drift derivation"
    )
```

The fixture supplies:

| Input | Source |
|---|---|
| Pre-idle raw | Thirty consecutive frames from the continuous synthetic sampler’s admitted second attempt, promoted byte-for-byte to `raw/powermetrics_idle.plist`. |
| Power values | Repeating committed five-frame rail sums: approximately `1.47572`, `0.0362467`, `0.537877`, `0.10975163`, `0.1727258` W. The admission slice can start at any cycle position. |
| Baseline mean | Duration-weighted mean of those thirty raw records, using their measured `elapsed_ns`. |
| GPU contamination | Derived from raw GPU idle/frequency fields; the normal repeating fixture is clean. |
| Post-idle request | `ceil(max(0.15, min(5.0, baseline.duration_s)) / 0.05)` samples. This is **host-timing dependent**, not invariably 100. |
| Guard | Interim guard: `n_bundles=0`, `guard_w=None`; effective bound equals the run envelope. |

The test’s `0.9/0.1` CPU-busy ratios and `2.0/0.1` W admission values modify rich admission records. They **do not replace the raw rail powers used for drift**.

[Powermetrics capture:1029](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:1029) determines the post count:

```python
interval_s = self._interval_ms(config) / 1000.0
duration_s = max(3.0 * interval_s, min(5.0, baseline.duration_s))
count = max(3, int(math.ceil(duration_s / interval_s)))
```

The timeout is [lines 1468–1470](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:1468):

```python
nominal_s = count * (self._interval_ms(config) / 1000.0)
return max(15.0, nominal_s * 1.5 + 10.0)
```

For 100 samples at 20 Hz, that is **17.5 seconds**. The fixture sleeps once per sample and measures actual elapsed time. Oversleep first inflates baseline duration and hence post count, then lengthens the post capture itself.

When capture raises, [lines 1043–1046](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:1043) return:

```python
except Exception:
    return {
        "idle_drift": unknown_component("post_idle_unavailable"),
    }
```

With a real context, `_run_bounded_capture` retains the pending capture on exception (1198–1217). Controller cleanup calls custody salvage (1392), which persists the partial raw bytes (adapter 885–908). It does **not** recompute the already-unknown drift.

Strict validation subsequently sees both raw files and derives from their complete parseable records. Its normal producer counterpart supplies these same power/quality inputs at [adapter:1063](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:1063):

```python
evidence, guard, bound_w = derive_idle_drift_evidence(
    pre_power_w=[record.combined_power_w for record in self._pre_idle_records],
    post_power_w=[record.combined_power_w for record in records],
    pre_power_w_mean=baseline.power_w_mean,
    pre_idle_window_suspect=pre_quality.get("idle_window_suspect"),
    post_idle_window_suspect=post_quality["idle_window_suspect"],
)
```

[uncertainty_evidence.py:1389](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/uncertainty_evidence.py:1389) requires at least three samples per side, finite values and clean contamination evidence. Then:

```python
run_bound_w = max(abs(value - pre_power_w_mean) for value in values)
...
if n_bundles == 0:
    effective_w = run_bound_w
```

It has no capture-completion input. Consequently, a sufficiently long **partial** sentinel produces bounded expected evidence, disagreeing with the stored unknown evidence and absent scalar.

Actual pipe-only results with the committed fixture and explicit 3.5× sleep stress:

| Python | Baseline duration | Post requested / recovered | Capture result | Stored / expected bound |
|---|---:|---:|---|---|
| 3.14.7 | 7.214152 s | 100 / 79 | `TimeoutExpired`, 17.5 s | absent / `1.0175162684204249` W |
| 3.13.1 | 7.218913 s | 100 / 77 | `TimeoutExpired`, 17.5 s | absent / `1.0094701382508093` W |
| Both, `--no-sleep` | Same respective baseline | 100 / 100 | Completed in under 0.3 s | Exact agreement |

These probes redirected fixture output to pipes and passed its actual output/exception into production `measure_post_run_idle`; they did not exercise filesystem custody or the full validator.

At ordinary pacing, both pipe probes passed: current scheduling produced 93 and 84 requested post samples. That variability reinforces the timing explanation. **The differing value is capture outcome and resulting evidence availability, not a demonstrated Mac-versus-CI ULP difference.** Exact bench/CI means and counts remain unobserved.

The earlier [report 74](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/process_traces/2026-09-09-rehearsal-harvest/74-seat-fixture-timeout-wallclock-astra-report.md) records this exact pair of strict reasons after the same timeout. Crucially, the cure at [tests/test_run_campaign.py:9549](/Users/edr/code/JouleWise-wt-gate-sweep-b/tests/test_run_campaign.py:9549) patches `_command` only around that campaign helper. The controller test calls its producer directly and never receives the patch.

## Remediation

**Minimal test cure:** apply the existing bounded-only `--no-sleep` behavior to this controller fixture path. Prefer sharing the existing fixture command policy so controller and campaign callers cannot diverge again. Continuous admission/measured sampling must retain pacing; derive post count from baseline duration without pinning it universally to 100. Keep production deadlines and strict comparisons unchanged.

The defect-shaped regression should exercise the controller retry producer under the established sleep stress and assert:

- Second-attempt raw promotion remains byte-exact.
- Stored post drift is bounded.
- Strict validation returns no problems.
- Fresh reduction retains the admitted attempt’s source digest.
- Removing bounded `--no-sleep` reproduces the timeout/unknown-drift failure.

**Real bundles:** a complete healthy bundle does not acquire this failure merely by being reduced on this Mac or at today’s epoch. The validator uses stored baseline mean and raw powers; no current clock enters drift derivation.

However, **a real post-idle timeout with sufficient salvaged raw records can reach the same disagreement**. That is a production failure-path inconsistency between capture outcome and raw rederivation, exposed here by a synthetic timing assumption. Such a member is strict-invalid and cannot be treated as usable: [run_campaign.py:445](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/run_campaign.py:445) requires both succeeded status and `strict_valid`.

If that failure path needs repair, the production proposal is to persist an authenticated capture-completion outcome and make strict validation distinguish incomplete salvaged evidence from a completed sentinel. Preserve unknown drift/non-claim-bearing status for incomplete capture. Merely deriving a bound from partial bytes or relaxing equality would conceal the missing completion evidence. No existing G2-a member is invalidated by this diagnosis alone.

**Same signature:** yes, at report 87’s broader host-dependent fixture-assumption level. Counting report 87, report 99’s short-uptime assumption, and this controller occurrence gives a third episode. More precisely, this is **incomplete propagation of the original sleeping-sentinel cure**, not a newly discovered epoch or numerical mechanism. Escalation and recurrence accounting remain with the lead.

## Disproved alternatives

- **Epoch/ULP dependence:** fixture dates are replaced at process execution. Drift consumes powers, a stored mean and contamination flags—not timestamps. An in-memory sweep across epoch `0`, committed fixture epoch `1783394101`, bench epoch `1789040700`, and `2147483648` produced identical drift evidence. Fixture and bench epochs both have ULP `2.384185791015625e-7` seconds.
- **Python 3.14-specific numerics:** both 3.14.7 and 3.13.1 reproduced timeout → unknown/absent versus bounded/positive. Both produced exact agreement when capture completed. Python 3.11 was not executed here.
- **Host uptime, boot UUID, real powermetrics installation, home path or timezone:** these do not enter the implicated drift predicates. The fixture executable runs under `sys.executable`; environment admission facts are supplied synthetically. Host scheduling does matter through sleep and elapsed duration.
- **Locally changed fixture bytes:** the worktree is clean. Both the sampler script and `powermetrics_sample.plist` matched `git show HEAD:<path>` byte-for-byte.

## Residual risk

The two strict messages alone do not uniquely identify a timeout: another caught post-capture exception followed by usable salvaged bytes could produce them. The exact next step is a lead-side targeted replay that records the `_run_bounded_capture` exception, requested count, stored drift and salvaged post count. That closes the remaining bench-attribution gap before applying the fixture cure.

No edits, full suite, or live hardware measurements were performed.