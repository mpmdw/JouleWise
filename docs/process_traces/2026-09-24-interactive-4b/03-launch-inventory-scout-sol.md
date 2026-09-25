```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The July floor and calibration corpora predate the night LaunchAgent; the September derivation and idle-pilot captures ran through it. No launchd-context MLX claim corpus was found.",
  "workspace": {
    "base_requested": "origin/main f416b64f",
    "base_mode": "exact",
    "head_start": "f416b64fb1ed0f23ae1630a21ee3021aa04e6d02",
    "head_end": "f416b64fb1ed0f23ae1630a21ee3021aa04e6d02",
    "upstream_end": "f416b64fb1ed0f23ae1630a21ee3021aa04e6d02",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "id": "R1",
        "action": "start_now",
        "subject": "Treat launch context as a recorded covariate when interpreting September calibration and idle-pilot results."
      },
      {
        "id": "R2",
        "action": "wait_for",
        "subject": "Any launchd-versus-shell inference comparison",
        "wait_for": "A comparable MLX corpus with established launch context; none was found."
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
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg --files configs/launchd",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "configs/launchd/com.joulewise.night-probe.plist.template",
          "configs/launchd/com.joulewise.night.plist.template",
          "configs/launchd/com.joulewise.magistrate.plist.template"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "configs/launchd/com.joulewise.magistrate.plist.template"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Most July bundles record OS build and workload metrics but not their shell, tmux, or nohup parent. Their non-launchd classification follows the launcher’s later commit date.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Per-cluster telemetry permits a retrospective placement proxy, but no retained record establishes effective QoS or task role for the measured MLX process.",
      "needs": ""
    }
  ]
}
```

## T1. Launchd paths

| Path and line | Label; ProcessType-like keys | Process tree and evidence |
|---|---|---|
| [Night template](/Users/edr/code/wt-4b-osaudit-scout/configs/launchd/com.joulewise.night.plist.template:5), [renderer](/Users/edr/code/wt-4b-osaudit-scout/joulewise/night_agent_install.py:608), [bootstrap](/Users/edr/code/wt-4b-osaudit-scout/joulewise/night_agent_install.py:489) | `com.joulewise.night`; **none** (`ProcessType`, `Nice`, `LowPriorityIO` absent) | `run_night.py run` → generated `chain.zsh` → derivation validator and `powermetrics`, or quiet-predicate campaign and `powermetrics`. The driver starts the chain at [run_night.py:855](/Users/edr/code/wt-4b-osaudit-scout/scripts/run_night.py:855). A future pack chain can reach `launch_window.py` and MLX; no measured pack night was found. |
| [Same template renderer](/Users/edr/code/wt-4b-osaudit-scout/joulewise/night_agent_install.py:616) | `com.joulewise.night.deadman`; **none** | `run_night.py dead-man`; supervises the night, does not itself collect the corpus. |
| [Probe template](/Users/edr/code/wt-4b-osaudit-scout/configs/launchd/com.joulewise.night-probe.plist.template:5), [render/bootstrap](/Users/edr/code/wt-4b-osaudit-scout/joulewise/night_agent_install.py:995) | `com.joulewise.night-probe.<plan-id>`; **none** | Temporary `run_night.py probe` → verify-only `chain.zsh`; the installer records `driver_pid`, `chain_pgid`, and `launchd_label` in [probe receipts](/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/night_probe_receipt.json:20). It is an admission probe, not a production capture. |
| [Magistrate template](/Users/edr/code/wt-4b-osaudit-scout/configs/launchd/com.joulewise.magistrate.plist.template:5), [installer bootstrap](/Users/edr/code/wt-4b-osaudit-scout/scripts/install_magistrate_watchdog.sh:305) | `com.joulewise.magistrate`; **none** | `magistrate_watchdog.py` → headless magistrate process via [Popen](/Users/edr/code/wt-4b-osaudit-scout/scripts/magistrate_watchdog.py:470). It can prepare and install a night; the scheduled night job starts the actual capture tree. |
| [Evidence-night façade](/Users/edr/code/wt-4b-osaudit-scout/joulewise/evidence_night.py:1414) | Delegates to the two night labels; no additional plist | Calls `install_night_agent.sh`; render-only creates staging plists and starts no job. [Installer wrapper](/Users/edr/code/wt-4b-osaudit-scout/scripts/install_night_agent.sh:38) enters the Python installer. |

## T2. Corpus provenance

| Corpus found | Dates; OS build | Launch context; evidence and limit |
|---|---|---|
| `/Users/edr/code/JouleWise/runs_window_a_20260722`, `_a_probe_20260722`, `_a2_20260722` through `_a10_20260725` | July 22–25; **25F84** in bundle `metadata.device.kern_osversion` | **Non-launchd inferred.** The night launcher first entered Git on **September 2** (`8c802bde`). Bundle metadata does not distinguish interactive shell, tmux, or nohup. The r6 acceptance names 17 retained and two excluded validation members across these roots: [r6 source directories](/Users/edr/code/wt-4b-osaudit-scout/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:52). |
| `/Users/edr/code/JouleWise/runs_recal_20260718`, `runs_recal2_20260719` through `runs_recal6_20260719` | July 18–19; **25F84** | **Non-launchd inferred** from era; exact shell mode unknown. |
| `/Users/edr/code/JouleWise/runs_window_b_20260726`, `_c_20260726`, `_d_20260726`, `_7bfloor_20260729`, `_contrast_20260730`, `_metrologyA_20260731`, `_metrologyB_20260801`, and each matching `_bound` root | July 26–August 1; **25F84** | **Non-launchd inferred** from era; exact shell mode unknown. These include the historical floor and contrast windows. |
| `/Users/edr/code/JouleWise/runs_char_t3appup_20260804_r01`, `_r02` | August 4; **25F84** | **Non-launchd inferred** from era; exact shell mode unknown. |
| `/Users/edr/code/JouleWise/runs/`: example MLX bundles, exploratory July 17, floor/window-A shakedowns, and 15 instrument-validation directories | Example bundles record **24G720**; July validation records are in the 25F84 era | Mixed early diagnostic roots; **non-launchd inferred** for July members. Individual example capture dates and parent mode were not established. Some validation bytes duplicate `runs_window_a*` sources. [Artifact guide](/Users/edr/code/wt-4b-osaudit-scout/docs/paper/artifact-guide.md:7) explains why runs are outside Git. |
| August D-127 unattended-loop **proposal/work orders** | August; no separate measured corpus located | **No launchd collection established.** The August 23 design record explicitly says the relaunch harness and launchd fallback did not yet exist: [design finding](/Users/edr/code/wt-4b-osaudit-scout/docs/process_traces/2026-08-23-t22/t0-unattended/seat-opus-design.md:446). “D-127” also names a clock sudoers rule; that is not a launch context. |
| September 9, 11, 12, and 16c rehearsal/stub archives; September 13, 15, 17 derivation attempts | September 9–17; derivation attempts **25G83** | **Launchd driver**, documented by night plans, `night/launchd.night.err`, and harvest records. Rehearsals have no measured claim corpus; the three listed derivation attempts refused before collecting validation captures. The September 16 derivation attempt started a chain but produced no slot data. |
| `/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919` | September 19; **25G83** | **Launchd**; night plist log, plan, chain and 12 retained raw fiducial captures. Equivalence verdict **INCONCLUSIVE**, four valid of twelve: [harvest](/Users/edr/code/wt-4b-osaudit-scout/docs/process_traces/2026-09-19-activation-b165c535/01-n1-20260919-harvest-record.md:1). |
| `/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919` | September 19; **25G83** | **Launchd**; same evidence shape, 12 captures. Equivalence verdict **FAIL**, seven valid; Ed chose to resolve the instrument before more derivation nights: [ruling record](/Users/edr/code/wt-4b-osaudit-scout/docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md:9). |
| `/Users/edr/night-archive/qpe01-pilot-n1-20260920-harvest-20260920` | September 20; **25G83** in pilot session | **Launchd**; plan and `launchd.night.err`. Aborted after one envelope; raw evidence retained: [harvest](/Users/edr/code/wt-4b-osaudit-scout/docs/process_traces/2026-09-20-activation-21752427/01-qpe01-pilot-n1-20260920-harvest-record.md:24). |
| `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922`, `qpe01-pilot-n1-20260922-2100-harvest-20260922`, `qpe01-pilot-n1-20260923-0700-harvest-20260923` | September 22–23; **25G83** in `night/evidence/envelope-*/session.json` | **Launchd**; each has plan, launchd log and 12 idle envelopes. These are **provisional pilot** evidence, not a qualified idle cutoff. September 23 reports 11 retained envelopes and “no cutoff qualifies”: [harvest](/Users/edr/code/wt-4b-osaudit-scout/docs/process_traces/2026-09-23-activation-5fe5a59b/01-qpe01-pilot-n1-20260923-0700-harvest-record.md:106). |
| `/Users/edr/night-archive/qpe-232/contaminated-2seats-20260918T185907` | September 18; **25G83** | Diagnostic collector session with explicit `argv`; **parent launch context unknown** from the retained session file. It is labelled contaminated. Other `night-archive` plan roots and results clones are copies or staging of the nights above, not additional capture corpora. |

## T3. Where launchd-context numbers travel

| Number or assertion | Source → consumer | Launch-context finding |
|---|---|---|
| About **1 J** phase attribution scale; historical ratios **10.92, 5.92, 7.02** | July calibration and floor windows → [paper draft §1](/Users/edr/code/wt-4b-osaudit-scout/docs/paper/draft-v1.md:11) and [§7](/Users/edr/code/wt-4b-osaudit-scout/docs/paper/draft-v1.md:298) | **No launchd source found.** July capture context is non-launchd by launcher chronology; precise shell mode remains unknown. |
| r6 fiducial level screen **0.032898493715362 s** and bracket screen about **9.724 ms** | July `runs_window_a*` validation members → [r6 acceptance](/Users/edr/code/wt-4b-osaudit-scout/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:52) → [paper draft](/Users/edr/code/wt-4b-osaudit-scout/docs/paper/draft-v1.md:164) and D-117 plan trees | **No launchd source found.** The September 19 launchd nights were tested *against* r6; they did not become its source. |
| Historical operative decode floor **7.377086 J** and related a10/C/7B floor figures | July windows → [RUN_STATE historical status](/Users/edr/code/wt-4b-osaudit-scout/RUN_STATE.md:5526) | **No launchd source found.** RUN_STATE also says the old C/D claim plan was retired by D-117. |
| September 19 **≈244–250 ms** sampler cadence, four of twelve and seven of twelve valid fiducials, equivalence **INCONCLUSIVE/FAIL** | Launchd derivation captures → [harvest and instrument decision](/Users/edr/code/wt-4b-osaudit-scout/docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md:9) | **Launchd sourced.** These are diagnostic/acceptance-decision inputs, not an issued replacement calibration. The [September 24 context experiment](/Users/edr/code/wt-4b-osaudit-scout/docs/process_traces/2026-09-24-interactive-4b/01-powermetrics-cadence-launch-context.md:1) changes how the cadence difference should be interpreted. |
| Idle envelope energy and spread: September 23 `pair_sd_j` **0.8710 J**, `s_upper` **1.6892 J**, proposed **23 pairs**, observer floor **0.1784 cores** | Launchd QPE pilot → [pilot summary/harvest](/Users/edr/code/wt-4b-osaudit-scout/docs/process_traces/2026-09-23-activation-5fe5a59b/01-qpe01-pilot-n1-20260923-0700-harvest-record.md:106) → block-two sizing and cutoff discussion | **Launchd sourced, explicitly PROVISIONAL.** The result says `cutoff_authority false` and “no cutoff qualifies.” |
| README statement that the first idle-variance pilot ran unattended and only **2/12** captures passed its timing check | September 22 launchd pilot → [README](/Users/edr/code/wt-4b-osaudit-scout/README.md:15) | **Launchd sourced**, descriptive project status. The nearby “~1 J” reference is the older instrument-scale rule, not a value derived from that pilot. |

## T4. Retrospective comparison fields

| Retained fields/files | What they permit | Limit |
|---|---|---|
| July and September raw `raw/powermetrics.plist`: `processor.clusters[].name`, `freq_hz`, `idle_ratio`, `down_ratio`, `online_ratio`, `dvfm_states`, `cpus`; `elapsed_ns` | Recompute E/P-cluster activity and frequency distributions, and actual sampler cadence, on retained raw captures. The QPE collector also writes parsed `clusters` and `cpus` from these fields: [parser](/Users/edr/code/wt-4b-osaudit-scout/scripts/sample_quiet_predicate_evidence.py:249). | Package-level telemetry is a **placement proxy**. It does not identify which process occupied a cluster. July MLX work and September idle/fiducial work are different workloads. |
| July MLX bundle `metadata.json` `workload_observed.output_token_count`; `summary_metrics.json` `throughput_tokens_s`, `inter_token_throughput_tokens_s`, `decode_latency_s` | Direct retrospective July tokens/s and timing analysis. | No comparable **launchd-context MLX bundle** was found. |
| September night plan, `night/launchd.night.err`, chain records; probe receipt `driver_pid`, `chain_pgid`, `launchd_label` | Establish the night/probe launch path and process identities. | Probe PIDs identify the temporary verify-only job. They are not effective QoS or task-role measurements of the production workload. |
| QPE `session.json` `os_build`, `power_interval_ms`, timing; worker configuration `qos`, set through [pthread QoS call](/Users/edr/code/wt-4b-osaudit-scout/scripts/sample_quiet_predicate_evidence.py:1309) | Compare pilot sampling and requested **synthetic worker** QoS. | Requested worker QoS does not reveal the effective task role of `powermetrics`, the night driver, or MLX. No retained effective `taskpolicy`/process-QoS record was found. |

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Launch-context annotation | start_now | — | September diagnostic and pilot interpretation; no corpus mutation required |
| Retrospective cluster/cadence analysis | start_now | — | Read-only use of retained raw plists; compare like workloads and OS builds |
| Launchd-versus-shell MLX effect | wait_for | Comparable measured MLX captures with established parent context | Energy, latency, tokens/s and cluster-placement claims |

## Critical path

| Dependency | Finding |
|---|---|
| Launch-context claim about inference → matched inference evidence | The inspected launchd nights measured fiducial pulses or idle pilots. Their raw cluster fields cannot by themselves establish how launchd changed MLX inference. |