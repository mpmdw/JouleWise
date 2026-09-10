```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The 60-second rate-fit requirement is materially under-sized for fast G2-a members; the idle-count gate passes observed cadence but fails the exact nominal boundary.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "078a13a461abd124c29796798da5107fe00190a6",
    "head_end": "078a13a461abd124c29796798da5107fe00190a6",
    "upstream_end": "078a13a461abd124c29796798da5107fe00190a6",
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "Q1",
        "action": "needs_ruling",
        "finding": "At risk, with likely failure for fast small-model members: a historical continuous 512-token capture supplies only 48.159784529 seconds against 60 required.",
        "remedy": "Approve sampling.idle_seconds 30 to 75 in scripts/generate_g2a_probe_inputs.py; regenerate and rebind prospective inputs before the first window."
      },
      {
        "row": "Q2",
        "action": "needs_ruling",
        "finding": "Exactly 300 idle records are collected. Observed cadence passes; median intervals of 100 ms or less fail. No physical lower-cadence guarantee was established.",
        "remedy": "The Q1 idle-duration increase also removes this count-boundary risk; no estimator threshold change is needed."
      },
      {
        "row": "Q3",
        "action": "start_now",
        "finding": "No additional fixed capture-sizing defect established. Exact member/pulse censuses and independently enforced dwell requirements have no spare count or planned time."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "awk '/<key>elapsed_ns<\\/key>/{v=$0; sub(/^.*<integer>/,\"\",v); sub(/<\\/integer>.*$/,\"\",v); n++; s+=v; if(n==1)z=v} END{printf \"records=%d baseline_s=%.9f\\n\",n,(s-z)/1000000000}' /Users/edr/code/JouleWise/runs_window_metrologyB_20260801/mtnull-o0512-b02-b2/raw/powermetrics.plist",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["records=403 baseline_s=48.159784529"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^records=403 baseline_s=48\\.159784529$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -a -c '<key>elapsed_ns</key>' /Users/edr/code/JouleWise/runs_window_metrologyB_20260801/mtnull-o0512-b02-b2/raw/powermetrics_idle.plist",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["300"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^300$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Current configuration does not assure sufficient rate-fit span. Recommended prospective remedy changes generated configuration and inventory bindings.",
      "needs": "Rule on increasing idle_seconds to 75 before the first window, then regenerate, rebind, and verify the prospective supply."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The named Seat B report, workspace runs directory, and /Users/edr/JouleWise-shakedown-g2 are absent. Historical physical bundles were inspected in the main checkout. No current Qwen3 G2-a capture was available.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Historical timings substantiate sizing risk but do not establish the future Qwen3 member duration or prove that exact 100 ms physical cadence is impossible.",
      "needs": "Retain historical-versus-prospective qualification."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Q1 | needs_ruling | Prospective capture-duration ruling and rebuilt input bindings | Config producer, generated configs/manifests, frozen plan, inventory, measurement-head pins |
| Q2 | needs_ruling | Same ruling; no separate implementation needed | Same `sampling.idle_seconds` setting |
| Q3 | start_now | Existing live gates remain mandatory | Independent cooldown, clean dwell, bracket calibration and selector census |

**Q1 — The fit covers one member’s continuous sampler, including idle and warmup.**

With production idle admission enabled, [controller.py:1013](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/controller.py:1013) calls `begin_admission_window_sampling()` before collecting the idle baseline. The adapter starts an unbounded sampler; idle admission extracts a byte-verbatim slice from that stream. At measured-window handoff, `start_sampling()` reuses the process instead of restarting it. See [powermetrics.py:358](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:358) and [powermetrics.py:452](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:452).

Its lifetime includes:

- Sampler readiness and native-second rollover.
- Idle admission, including a second attempt if required.
- Runtime warmup, then the configured five-second settling wait.
- The measured workload.
- The production one-second post-window dwell and bounded drain.

The runtime warmup generates **at most four tokens**, not 512: [mlx_runtime.py:351](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/mlx_runtime.py:351). Model loading and pre-idle settling occur before sampler startup. Stage-level 600-second settles, inter-member cooldown captures, and the separate post-run idle sentinel do not contribute to this fit.

The authoritative quantity is `sum(elapsed_ns[1:])` from that member’s retained `raw/powermetrics.plist`, not controller wall time or stage duration. Stop processing can retain a bracketing prefix, and the estimator is then rerun on that prefix. See [uncertainty_evidence.py:972](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/uncertainty_evidence.py:972) and [powermetrics.py:799](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:799).

At uniform 115 ms cadence, idle contributes 34.5 seconds. Adding five seconds settling and one second tail gives approximately **40.5 seconds plus warmup, workload, readiness and controller overhead**. Therefore another approximately 19.5 seconds is needed. A 512-token cap supplies no minimum runtime.

The historical physical bundle [mtnull-o0512-b02-b2](/Users/edr/code/JouleWise/runs_window_metrologyB_20260801/mtnull-o0512-b02-b2/metadata.json) confirms the continuous-capture scale:

| Quantity | Observed |
|---|---:|
| Configuration | Qwen2.5-1.5B, 512 output tokens, one repetition, one warmup, 30/5-second sampling settings |
| Primary raw records | 403 |
| Accumulated intervals excluding record zero | **48.159784529 s** |
| Deficit against current 60-second gate | **11.840215471 s; 19.73%** |
| Spawn stamp to measured-start stamp | 44.500103 s |
| Measured workload | 2.048627 s |
| Spawn stamp to post-parse stamp | 50.016402 s |

This bundle predates the August 19 v3 activation; its historical success does **not** establish current-gate success. Its raw interval total fails the current span predicate. Future Qwen3 duration is unmeasured, so the prospective verdict is **at risk, likely failing for fast small members**, rather than a claim that every future member necessarily fails.

**Recommended remedy:** change `sampling.idle_seconds` from 30 to **75** in [generate_g2a_probe_inputs.py:498](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/generate_g2a_probe_inputs.py:498). This obtains genuine additional instrument observations without changing workload size or weakening the estimator. At nominal cadence, the idle plus settling and tail terms alone become approximately **81 seconds**, 35% above the fit minimum; at 115 ms, approximately 92.25 seconds. Startup records and workload add further time.

**Must land first:** yes, to enter the first window with a defensible expectation of satisfying this evidence gate. Increasing repetitions does not pool separate member clocks. Increasing output tokens would alter the intended workload and still would not guarantee a duration.

**Q2 — The idle baseline contains exactly 300 records, including its own record zero.**

[The adapter](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:1460) computes:

`count = ceil(idle_seconds / rounded_nominal_interval_seconds) = ceil(30 / 0.1) = 300`.

The continuous-stream slice skips already completed records and one boundary-straddling record, then waits for **300 new complete records**. Those exclusions do not reduce the returned count. It is sample-count bounded, with an operational timeout of **55.15 seconds** for this slice, rather than a 30-second wall-clock cutoff. See [powermetrics.py:1219](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/adapters/powermetrics.py:1219).

[The idle estimator](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/idle_dependence.py:214) uses every returned record and every elapsed interval:

`L = floor(10 / median_interval_s)`; required count `= 3(L+1)`.

| Cadence | Records | Evidenced idle duration | L | Required | Count margin |
|---|---:|---:|---:|---:|---:|
| Exactly 100 ms throughout | 300 | 30 s | 100 | 303 | **−3; fails** |
| Uniform 115 ms | 300 | 34.5 s | 86 | 261 | **+39; 14.94%** |
| Historical bundle above | 300 | 36.211533687 s | 82 | 249 | **+51; 20.48%** |

The historical median was **120.755166 ms**, with p95/p05 **1.07342**, below the separate 1.25 cadence-irregularity ceiling.

**Exact-100 ms physical reachability:** it was **not observed**. That bundle’s smallest idle interval was 114.948541 ms, and none equaled 100 ms. An additional historical 300-record idle capture likewise had no exact-100 ms intervals. These observations do not prove that powermetrics *never* delivers exactly 100 ms, or establish a physical impossibility theorem for an entire capture. The adapter requests 100 ms but supplies no guaranteed observed lower bound.

The relevant boundary is actually the **median**, not all 300 intervals being identical: with 300 samples, this count gate passes whenever the median is strictly greater than 100 ms and fails at or below 100 ms.

Thus the verdict is **observed pass with margin, configuration-level boundary risk**. Q1’s 75-second idle setting produces 750 records, comfortably exceeding even the nominal 303 requirement. No change to `L`, the bandwidth, or record inclusion is justified. The shared remedy should land before the first window; Q2 alone has substantially weaker empirical urgency than Q1.

**Q3 — Additional nearby gates and margins.**

- **Member census:** the default five small members per rung and one large member per rung exactly meet the minima—**zero spare members**; repetitions within a member are not substitutes. [Producer check](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/generate_g2a_probe_inputs.py:1063).
- **Prefill overlap census:** selector threshold is five overlapping intervals; counts four/five/six are −20%/0%/+20%. Actual rung margins require G2-a measurements; short-rung failure is an intended selector outcome. The reducer’s separate phase minimum is three. [Summarizer constants](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/summarize_g2a_prefill_probe.py:19).
- **Window duration:** request duration must cover four cadence gaps; phase duration two, with clock bound ≤one-quarter window. At 115 ms these cadence minima are approximately 0.460/0.230 seconds. The historical 2.049-second request is comfortably clear; prospective prefill margins remain unknown. [Reducer](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/reduce.py:975).
- **Clean dwell:** 600 continuous clean seconds are required; release occurs only after reaching them, with approximately zero minimum margin. Contamination resets the clock. This is independently enforced and contributes nothing to member sampler duration. [Prewindow loop](/Users/edr/code/JouleWise-wt-gate-sweep-b/scripts/prewindow_check.sh:176).
- **Stage settling:** emitted chain requests exactly 600 seconds before the pre-calibration and each stage—zero planned excess. This sleep is distinct from proving a continuous clean dwell. [Runsheet](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:477).
- **Cooldown coverage:** independent captures must establish a full 30-second span and ≥24 seconds coverage, within a 300-second cap. Full coverage allows six seconds of missing support—20% of the window; actual margin is live-dependent. The five-second member settling wait does not satisfy this gate. [Controller](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/controller.py:2552).
- **Fiducial census:** 59 commanded measured pulses, all 59 required—**zero loss allowance**; three warmup pulses are separate. [Protocol](/Users/edr/code/JouleWise-wt-gate-sweep-b/docs/contracts/powermetrics_fiducial.md:27).
- **Fiducial quiet support:** planned five seconds versus authenticated minimum 4.5 seconds gives **0.5 seconds, 11.11% margin**. One-second pulses must remain within 0.8–1.2 seconds: ±0.2-second tolerance. [Authentication](/Users/edr/code/JouleWise-wt-gate-sweep-b/joulewise/powermetrics_fiducial.py:410).
- **Other sample minima are distant:** CPU idle admission 300/30; post-idle sentinel 50/3; pre-idle drift evidence 300/3. No additional near-minimum count defect appears there.

## Critical path

**Lead ruling:** approve the proposed 75-second idle setting, or explicitly retain the current setting with its unresolved rate-fit risk. Increasing only `warmup_seconds` is an alternative for Q1, but leaves Q2’s nominal boundary; increasing idle duration addresses both with one setting.

A producer-only sampling change does **not directly change emitted chain shell bytes**, provided the runsheet, date and paths remain identical: the emitter excludes the desk producer and invokes the existing generated config directories. It **does** change every generated config hash, its order-manifest entry and manifest hash, the frozen plan, and inventory bindings. The producer’s checker compares configs against `_config_for()`, so hand-editing already generated configs is insufficient.

Regenerate prospective inputs, rerun `bind-window`, refresh affected measurement-head and supply pins, and verify before arming. Preserve existing evidence. For 24 members, the proposed increase adds approximately **20.7 minutes at 115 ms cadence**.

Finally, these are evidence gates, not necessarily immediate shell aborts: ordinary member failure classification separates claim-evidence flags, and the G2-a summarizer reads overlap counts without requiring energy eligibility. A completed chain therefore cannot substitute for inspecting the fit and idle-estimator results.

No files were modified, no captures were started, and no tests or repository Python modules were executed; verification used source inspection, historical raw records, and arithmetic.