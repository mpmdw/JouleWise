```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The recorded 25G83 pilot argv and the reconstructed r6 and 09-19 fiducial argv have the same sampling flags; the cadence change tracks the OS/binary epoch, but their individual effects remain unresolved.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "bbe475e5c410d9177f41a47101029ff15109523f",
    "head_end": "bbe475e5c410d9177f41a47101029ff15109523f",
    "upstream_end": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "25G83 same-build sampler-subset comparison",
        "action": "wait_for",
        "reason": "Ed-owned sudo and a quiet measurement window"
      },
      {
        "row": "25F84 versus 25G83 matched-state comparison",
        "action": "wait_for",
        "reason": "Access to both OS epochs on comparable hardware"
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
      "cmd": "git blame -L 2275,2288 scripts/validate_powermetrics_fiducial.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["aaе658ac8: -b, -i, --samplers, --format and -o originate on 2026-07-20"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2026-07-20"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Fiducial bundles do not record the spawned powermetrics argv; their argv is reconstructed from capture-era code and binding fields.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Three r6 a9 source directories retain power_trace.csv but lack raw/powermetrics.plist; the 17-member cadence statistic uses trace interval widths.",
      "needs": ""
    }
  ]
}
```

## Q1. Invocation

**No sampler flag or sampler-list change appears in the evidence.** The fiducial command reconstructed for every r6 member and both 09-19 nights is:

```text
sudo -n /usr/bin/powermetrics -b 0 -i 100
  --samplers cpu_power,gpu_power,ane_power,thermal
  --format plist -o <capture-directory>/raw/powermetrics.plist
```

The July capture path constructs that command in `scripts/validate_powermetrics_fiducial.py` at commit `fdb311f4`, lines 332–345. The archived 09-19 n1 and n2 `results-clone/scripts/validate_powermetrics_fiducial.py:2276–2288` constructs the same flags. The 09-19 binary path is also corroborated by each capture’s `instrument_evidence.json → binding_evidence.powermetrics_binary.path`. **The fiducial bundles do not store the spawned argv itself**: their `manifest.json` lists artifact hashes, and `events.jsonl` records sampling and pulse events, not argv. Thus “same actual argv” is a strong code-and-binding reconstruction, not a per-process argv receipt. [July source example](/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/manifest.json), [09-19 n1 source example](/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d01/instrument_evidence.json).

The [r6 acceptance file](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json) names these 17 `derivation_corpus.members` and their `source_directory` values. Each has `bindings.sampling_interval_ms=100`, `bindings.os_build=25F84`, and the same binary SHA:

| Source-directory family | Member IDs | Reconstructed argv |
|---|---|---|
| `runs_window_a_20260722`, `a2`, `a3`, `a4` | `20260722T145535-e941c821`, `20260722T194118-9dc0749d`, `20260722T214220-1acdbbc0`, `20260722T215127-eeef661a` | Command above; `-o` is that member’s `raw/powermetrics.plist` |
| `runs_window_a5_20260723` | `20260722T232509-82642517`, `20260723T023058-8732d1c9`, `20260723T052051-d9358c8a` | Same |
| `runs_window_a6_20260723`, `a7`, `a8` | `20260723T194632-d04e038e`, `20260723T195730-bc4ba14a`, `20260723T221449-e9ae755e`, `20260723T223406-314f6d9e`, `20260724T014109-57844352` | Same |
| `runs_window_a9_20260724`, `a10_20260725` | `20260725T005132-a64711b7`, `20260725T011533-0b5ec77c`, `20260725T022712-0a9534f5`, `20260725T030533-d3f076e5`, `20260725T060617-97c5cba6` | Same |

All 24 09-19 captures, `d01`–`d12` in each of [n1](/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation) and [n2](/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation), have `instrument_evidence.json → bindings.sampling_interval_ms=100`, `bindings.os_build=25G83`, and the same `binding_evidence.powermetrics_binary` identity. Their archived capture code yields the command above, with each `-o` set to its own `raw/powermetrics.plist`.

For qpe01, **the actual argv is recorded** at `night/evidence/envelope-*/session.json → power.argv`. Every envelope from the 09-20 pilot (one short capture), 09-22 02:17 pilot (12), 09-22 21:00 pilot (12), and 09-23 07:00 pilot (12) records:

```text
sudo -n /usr/bin/powermetrics -b 0 -i 100
  --samplers cpu_power,gpu_power,ane_power,thermal
  --format plist -o <envelope>/raw/powermetrics-idle-<repeat>.plist
```

The only argv difference from the fiducials is the output pathname. Each session has `power_interval_ms=100`. Examples: [09-20 session](/Users/edr/night-archive/qpe01-pilot-n1-20260920-harvest-20260920/night/evidence/envelope-01/session.json), [09-22 02:17 session](/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence/envelope-02/session.json), [09-22 21:00 session](/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence/envelope-01/session.json), [09-23 session](/Users/edr/night-archive/qpe01-pilot-n1-20260923-0700-harvest-20260923/night/evidence/envelope-01/session.json).

| Flag requested | r6 fiducials | 09-19 fiducials | qpe01 pilots |
|---|---|---|---|
| Interval | `-i 100` | `-i 100` | `-i 100` |
| Count | No `-n` | No `-n` | No `-n` |
| Samplers | `cpu_power,gpu_power,ane_power,thermal` | Same | Same |
| Format | `--format plist` | Same | Same |
| Buffer | `-b 0` | Same | Same |
| Show/hide flags | None | None | None |
| Output | `-o …/raw/powermetrics.plist` | Same pattern | `-o …/raw/powermetrics-idle-<repeat>.plist` |

## Q2. Code history

The fiducial flags `-b 0`, `-i`, `--samplers`, `--format plist`, and `-o` blame to the 2026-07-20 fiducial implementation; the sampler constant `cpu_power,gpu_power,ane_power,thermal` blames to the adapter’s 2026-07-06 implementation. The production adapter’s `_command` still builds those flags at [powermetrics.py:1472](/Users/edr/code/wt-278ebc9e-g2a/joulewise/adapters/powermetrics.py:1472), with `-n` only when `count` is supplied. The fiducial command at [validate_powermetrics_fiducial.py:2275](/Users/edr/code/wt-278ebc9e-g2a/scripts/validate_powermetrics_fiducial.py:2275) supplies no `-n`. The qpe01 harness calls that production builder with `count=None`, and its session files preserve the resulting argv; see [sample_quiet_predicate_evidence.py:199](/Users/edr/code/wt-278ebc9e-g2a/scripts/sample_quiet_predicate_evidence.py:199).

The later fiducial code added an injectable sampler binary and a direct-for-test path, but its production flag sequence did not change. The archived n1/n2 code at line 2276 uses `args.sampler_binary`; its binding records identify `/usr/bin/powermetrics`. There is no code-history evidence for a changed sampler set or flag causing the July-to-September cadence gap. The anchor estimator *did* change (`censored_intersection_v1` to `rate_aware_set_membership_v1` in the respective `instrument_evidence.json → anchor_method_version`), but that estimator operates on the delivered records and does not set the powermetrics invocation. [r6 example](/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/instrument_evidence.json), [25G83 example](/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d01/instrument_evidence.json).

## Q3. Delivered `elapsed_ns`

Nearest-rank p95 and maximum below are calculated from positive `<key>elapsed_ns</key><integer>…</integer>` values in each listed raw plist; units are milliseconds. For all 17 r6 members, I used `power_trace.csv` GPU interval widths because three a9 source directories lack their raw plist. The 14 available r6 raw plists agree closely with the trace aggregate. Source directories are given by the r6 acceptance `derivation_corpus.members`; September sources are the archive `runs/instrument_validation/*/raw/powermetrics.plist` and `night/evidence/envelope-*/raw/powermetrics*.plist`.

| Corpus and invocation variant | Samples | Median | p95 | Max | Evidence location |
|---|---:|---:|---:|---:|---|
| r6, 25F84, same fiducial flags; **17 traces** | 28,190 | 120.288 | 124.417 | 144.252 | [r6 member paths](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json), each `power_trace.csv → gpu_power interval_end_s − interval_start_s` |
| r6, **14 retained raw plists** | 23,236 | 120.229 | 124.349 | 144.252 | Same member paths, `raw/powermetrics.plist → elapsed_ns` |
| 09-19 n1, 25G83, fiducial flags | 10,308 | 247.853 | 274.056 | 353.265 | [n1 raw plists](/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation) |
| 09-19 n2, 25G83, fiducial flags | 10,297 | 249.248 | 274.784 | 419.063 | [n2 raw plists](/Users/edr/night-archive/d079-epoch-25g83-derivation-n2-20260919-harvest-20260919/runs/instrument_validation) |
| qpe01 09-20, 25G83, same sampler flags | 3 | 231.041 | 259.901 | 259.901 | [envelope 01 raw](/Users/edr/night-archive/qpe01-pilot-n1-20260920-harvest-20260920/night/evidence/envelope-01/raw/powermetrics-idle-1.plist); interrupted capture |
| qpe01 09-22 02:17, 25G83, same sampler flags | 30,163 | 248.228 | 276.916 | 463.937 | [envelopes](/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence) |
| qpe01 09-22 21:00, 25G83, same sampler flags | 32,436 | 240.134 | 269.608 | 470.845 | [envelopes](/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922/night/evidence) |
| qpe01 09-23 07:00, 25G83, same sampler flags | 30,654 | 248.273 | 277.493 | 427.349 | [envelopes](/Users/edr/night-archive/qpe01-pilot-n1-20260923-0700-harvest-20260923/night/evidence) |

There is **no different sampler invocation within 25G83** among these corpora. The qpe01 harness does run an observer alongside the power recorder, yet its three complete pilots remain near the 09-19 cadence; the 09-22 21:00 pilot’s 240.134 ms median shows some same-binary, same-argv variation without approaching the r6 120 ms regime. The 09-20 three-frame pilot cannot characterize a distribution.

## Q4. Binary and OS identity

| Captures | Recorded OS build | Recorded `/usr/bin/powermetrics` SHA-256 | Where recorded |
|---|---|---|---|
| All 17 r6 members | `25F84` | `d1dccad0d0a8016d38bd584bdae283566723096162f06ef663debb4a5762fe69` | Each `instrument_evidence.json → bindings.os_build`, `binding_evidence.powermetrics_binary.{path,sha256}`; [first member](/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/instrument_evidence.json) |
| All 24 09-19 n1/n2 members | `25G83` | `b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5` | Each `instrument_evidence.json → bindings.os_build`, `binding_evidence.powermetrics_binary`; [n1 example](/Users/edr/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919/runs/instrument_validation/d079-epoch-25g83-derivation-n1-20260919-d01/instrument_evidence.json) |
| All qpe01 envelopes listed above | `25G83` | `b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5` | Each `session.json → os_build`, `powermetrics_identity.{path,sha256}`; [example](/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence/envelope-02/session.json) |

No separate powermetrics version string is present in those records; the SHA-256 is the recorded executable identity. The native plist’s `kern_osversion` also reads `25F84` in the retained r6 raw files and `25G83` in the September raw files.

## Q5. Conclusion and settling experiment

**The flag/sampler hypothesis is not supported by these captures.** The decisive comparison is r6 versus 09-19 n1/n2: reconstructed identical fiducial flags and requested 100 ms, but roughly 120 versus 248–249 ms delivered medians. The qpe01 captures independently record the same sampler flags on 25G83 and remain roughly 240–248 ms despite a different harness and observer. That weakens a fiducial-harness-only or qpe01-observer explanation. It does **not** isolate the changed executable from macOS scheduler or other OS services: OS build and binary SHA changed together, and machine state was not experimentally matched. Attribution between those causes remains **undetermined**.

An Ed-controlled **quiet-window** comparison should hold the binary, build, hardware, power policy, and workload state fixed, then alternate sampler lists. These are proposed commands only; none were run:

```sh
sw_vers -buildVersion
shasum -a 256 /usr/bin/powermetrics

# Ed-only: sudo is required. Run A, B, A sequentially on a quiet machine.
sudo -n /usr/bin/powermetrics -n 1200 -b 0 -i 100 \
  --samplers cpu_power,gpu_power,ane_power,thermal \
  --format plist -o /tmp/pm-all-A.plist
sudo -n /usr/bin/powermetrics -n 1200 -b 0 -i 100 \
  --samplers cpu_power \
  --format plist -o /tmp/pm-cpu-B.plist
sudo -n /usr/bin/powermetrics -n 1200 -b 0 -i 100 \
  --samplers cpu_power,gpu_power,ane_power,thermal \
  --format plist -o /tmp/pm-all-A2.plist
```

Adding `-n 1200` makes these bounded probes a new invocation variant; the first all-sampler arm must therefore be compared with the archived no-`-n` 25G83 baseline before interpreting the subset arm. Record each file’s `elapsed_ns` median, p95, max, actual argv, SHA, OS build, and observer/load census. If CPU-only approaches 120 ms while both all-sampler arms stay near 245 ms, the sampler set is causal *within 25G83*. If all remain near 245 ms, repeat the **same argv and quiet-state protocol** on available 25F84 hardware or boot image. That matched cross-build result would test the OS/binary epoch; separating the executable itself from the OS would additionally require a compatible, authorized cross-binary run on one build.

## Scheduling matrix

| Row | Action | Wait for | Collision surface |
|---|---|---|---|
| Same-build A/B/A probe | `wait_for` | Ed, sudo, quiet machine | Power measurement and agent load |
| Matched 25F84/25G83 probe | `wait_for` | Comparable OS environments | OS, binary, and machine state |

## Critical path

Run the same-build A/B/A probe first. A cross-build probe is needed only if the sampler-list comparison leaves the approximately twofold cadence change unexplained.