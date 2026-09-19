```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend a dedicated evidence payload through the existing v2 night machinery, with evidence-specific installation verification; no new NightPlan kind and no cutoff activation.",
  "workspace": {
    "base_requested": "0c529f99",
    "base_mode": "exact",
    "head_start": "0c529f99ea95ccee37207057934a2f79a6941c98",
    "head_end": "0c529f99ea95ccee37207057934a2f79a6941c98",
    "upstream_end": "0c529f99ea95ccee37207057934a2f79a6941c98",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "A separate v2 evidence payload is the smallest executor shape, but the existing installation probe requires calibration-ledger semantics and cannot honestly verify it unchanged."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "text": "The harness omits OS build from collected rows and discards per-round hard-probe results; its current summaries cannot establish all requested campaign admissibility conditions."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "text": "Freeze paired, placement-aware sampling and distinguish complete 480-second integrals from the harness's duration-normalized descriptive estimates."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "text": "Stage A may identify a candidate; Stage B and a cold-gate ruling remain required for cutoff activation."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence.FrameTests tests.test_sample_quiet_predicate_evidence.IntegrationTests tests.test_sample_quiet_predicate_evidence.SummaryTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 21 tests in 0.063s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 21 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp /Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'\nfrom tempfile import TemporaryDirectory\nfrom unittest.mock import patch\nfrom scripts import sample_quiet_predicate_evidence as h\nfrom tests.test_sample_quiet_predicate_evidence import FakeClock, collect_args, fake_round\nwith TemporaryDirectory(dir='/tmp') as d, patch.object(h.subprocess, 'Popen', side_effect=AssertionError('no subprocess')):\n    session, rows = h.collect(collect_args(d), clock=FakeClock(), round_runner=fake_round, metadata_reader=lambda: {'boot_id':'fixture-boot','os_build':'25G83'})\n    summary = h.summarize(d, 'idle')\n    assert session['os_build'] == '25G83'\n    assert all('os_build' not in row for row in rows)\n    assert all('os_build' not in group for group in summary['groups'])\n    print('OFFLINE_REPRO: session os_build=25G83; collected rows and summary groups omit os_build')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OFFLINE_REPRO: session os_build=25G83; collected rows and summary groups omit os_build"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OFFLINE_REPRO: session os_build=25G83; collected rows and summary groups omit os_build"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --exit-code && git status --short --branch && git rev-parse HEAD && git rev-parse --verify refs/remotes/origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "0c529f99ea95ccee37207057934a2f79a6941c98",
          "0c529f99ea95ccee37207057934a2f79a6941c98"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)\\n0c529f99ea95ccee37207057934a2f79a6941c98\\n0c529f99ea95ccee37207057934a2f79a6941c98"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Future campaign arming needs an adopted evidence-payload verification contract. This consult proposes it but supplies no activation authority.",
      "needs": "Lead adjudicates the design and routes any changed admission/probe obligations through the cold gate before arming."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only consult completed. No live collection, power sampling, sudo, installation, or full-suite execution; only selected offline tests and fixture inspection.",
      "needs": ""
    }
  ]
}
```

## Findings

**F1 — Blocker: recommend option (a′), a separate evidence payload using an existing v2 `DIAGNOSTIC_NO_PACK` plan.**

This answers **Q1 and Q5**. Reuse the LaunchAgent pair, handback, census, deadlines, courier and dead-man, but make `quiet_predicate_evidence` a **chain payload identity**, not a new `NightPlan` field or receipt class. This route already has explicit lead precedent: the adopted Stage A design names “a diagnostic v2 payload that runs the harness.” Existing v2 plans already select a digest-checked executable through `chain_path`; their exact schema has no `kind` field. (`docs/process_traces/2026-09-18-activation-d8ca3a36/14-magistrate-adjudication-consult-06.md:9`; `joulewise/night_gate.py:120`; `joulewise/night_gate.py:1074`.)

The important qualification is that **this is not presently a drop-in chain replacement**. Installation requires a probe whose implementation reads `CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN`, requires `calibration_derivation_only.zsh`, and checks finalized observation counts and calibration custody time. A harness-only chain cannot satisfy that contract honestly. Do not fabricate an empty ledger or claim a calibration reservation occurred. (`joulewise/night_agent_install.py:751`; `joulewise/night_agent_install.py:793`; `scripts/run_night.py:3263`.)

Proposed minimum integration:

- Add a sealed evidence manifest and generated chain wrapper, with explicit payload identity covered by the chain digest. Freeze commands, ordering, durations, output locations, protocol and code identities before arming.
- Add a typed **evidence probe receipt** that verifies those bindings, the actual interpreter and non-measuring execution path. Preserve the calibration probe unchanged for calibration payloads. Verification mode must never start `collect`, `load` or power sampling.
- Retain v2 admission, including its legacy load veto. Inject synthetic load **after GO**, inside the dedicated evidence chain. Do not borrow the unapproved v4 predicate to admit the experiment intended to validate it.
- Make teardown account for the collector, load workers, power recorder and sampler groups before starting the agent courier. The existing driver proves absence of its chain process group; sampler workers use separate sessions, so that proof alone is insufficient for this payload. (`joulewise/night_gate.py:1218`; `scripts/run_night.py:461`; `scripts/run_night.py:2069`; `scripts/sample_quiet_predicate_evidence.py:417`.)

**Blast radius:** `night_plan_writer.py` needs **no schema or serialization change**. `run_night.py` needs evidence-probe dispatch, evidence-summary inventory and an outcome/cleanup check before courier launch; its scheduling and v2 admission behavior remain applicable. The installer’s Python implementation needs evidence-specific binding validation. The courier needs descriptive campaign results, exclusions and provenance paths—not scientific decision authority. Its present artifact list does not include the harness outputs. (`joulewise/night_plan_writer.py:18`; `scripts/run_night.py:960`; `scripts/run_night.py:1107`; `docs/process/NIGHT_HANDBACK.md:10`.)

Keep the existing D-166 `registration_path` gate; separately bind the campaign’s scientific protocol through the reviewed head and manifest digest. Calibration nights already distinguish these two registrations. (`joulewise/night_gate.py:1332`; `docs/phase_2/derivation_night_runbook.md:28`.)

Alternatives lose for these reasons:

| Alternative | Assessment |
|---|---|
| **Literal (a): new NightPlan kind/schema** | Unnecessary for selecting a chain. It expands the exact-key parser, writer and associated consumers without fixing the actual calibration-specific probe problem. A new field cannot simply be inserted into v2. (`joulewise/night_gate.py:229`; `joulewise/night_plan_writer.py:37`.) |
| **(b): independent launchd desk job** | A bare job inherits none of the night system’s plan/chain authentication, admission receipt, recurring census/abort, once-only start, bounded shutdown, courier recovery or watchdog-discovered plan span. Recreating these exceeds the payload integration; omitting them changes the operating contract. (`scripts/run_night.py:806`; `scripts/run_night.py:2922`; `docs/process/NIGHT_HANDBACK.md:55`.) |
| **(c): inside calibration settle** | Synthetic load and observation work defeat the registered settle after the last machine action. This would change the calibration experiment. (`scripts/night_chains/calibration_derivation_only.zsh:159`; `scripts/night_chains/calibration_derivation_only.zsh:215`.) |
| **(c): appended after calibration slots** | Requires new frozen duration, protocol and cleanup obligations, couples two outcomes, and inherits a thermally different starting state. It is no longer an unchanged calibration night. Separate plans preserve the existing slot/deadline contract. (`scripts/night_chains/calibration_derivation_only.zsh:237`; `docs/contracts/night_quiet_admission.md:285`.) |

**Exact proposed implementation-seat file list**—new paths are proposals, not writes made here:

1. `joulewise/quiet_predicate_campaign.py` — new manifest, binding, admissibility and paired-reduction helpers.
2. `scripts/run_quiet_predicate_campaign.py` — new author/verify/run/summarize entry point and generated wrapper.
3. `scripts/sample_quiet_predicate_evidence.py` — evidence-retention and termination fixes described below.
4. `joulewise/night_agent_install.py` — evidence-specific probe bindings and validation.
5. `scripts/run_night.py` — probe dispatch, artifact inventory and cleanup outcome integration.
6. `tests/test_quiet_predicate_campaign.py` — new campaign tests.
7. `tests/test_sample_quiet_predicate_evidence.py`.
8. `tests/test_night_agent_install.py`.
9. `tests/test_run_night.py`.
10. `docs/phase_2/quiet_predicate_evidence_campaign.md` — new protocol and operating contract.
11. `docs/phase_2/derivation_night_runbook.md` — link the separate payload route and distinguish its probe.
12. `docs/process/NIGHT_COURIER_PROMPT.md` — descriptive evidence-summary instructions.

Generated per-window artifacts, the actual handback rewrite and kernel/status/report bookkeeping remain lead-owned, outside that proposed seat list. The handback is rewritten for each armed window; delegated scope does not expand to bookkeeping automatically. (`docs/process/NIGHT_HANDBACK.md:3`; `AGENTS.md:11`.)

**F2 — Blocker: current evidence fields do not establish all requested admissibility claims.**

This answers **Q3**, including two concrete corrections to the premise.

| Condition | Existing evidence; required treatment or gap |
|---|---|
| **Census clean throughout** | Rows retain concurrent/sampler `censuses`, `census_errors` and tri-state `census_clean`. Only `true` qualifies for clean comparisons; false/null remain retained controls or exclusions. The outer driver must also have no census abort. (`scripts/sample_quiet_predicate_evidence.py:549`; `scripts/sample_quiet_predicate_evidence.py:572`; `scripts/run_night.py:892`.) |
| **OS build and boot** | `session.json` records both, but collection copies only `boot_id` into rows. Summary grouping reads `row.os_build`, so actual collected rows lack the advertised OS grouping. V2 reproduces this offline. Copy and validate the build, or explicitly authenticate a session-to-row join; missing identity cannot silently qualify. (`scripts/sample_quiet_predicate_evidence.py:605`; `scripts/sample_quiet_predicate_evidence.py:658`; `scripts/sample_quiet_predicate_evidence.py:997`.) |
| **AC and power policy** | Smoke workers execute battery and settings probes, but `smoke_observation_round` discards their returned values; the harness retains census/sample results, not these hard results. Thus initial night admission is evidenced, but per-round AC continuity is not. Persist and evaluate those existing responses, including the intended power policy. (`scripts/run_night.py:2028`; `scripts/run_night.py:2674`; `scripts/sample_quiet_predicate_evidence.py:407`; `joulewise/night_gate.py:1177`.) |
| **Thermal restriction and recovery** | Same retention gap. Native raw power files may contain thermal data, but the harness frame parser exposes power/residency rather than a thermal admissibility field. Retain hard-probe results and thermal diagnostics; a restriction or failed required probe excludes the affected comparison from nominal-machine evidence. The existing predicate accepts absent `CPU_Speed_Limit`, but any reported limit must be 100. (`scripts/sample_quiet_predicate_evidence.py:169`; `joulewise/night_gate.py:1243`.) |
| **Cadence and clock alignment** | Native `elapsed_ns`, timestamps and anchor diagnostics support reconstruction. Report actual cadence distribution, gaps and estimator identity. An unresolved anchor or unbounded coverage makes the affected ΔJ unusable for a finite safety bound. Stable ≈0.245 s cadence alone is not an exclusion. (`scripts/sample_quiet_predicate_evidence.py:169`; `scripts/sample_quiet_predicate_evidence.py:203`; `scripts/sample_quiet_predicate_evidence.py:227`.) |
| **Complete support** | The collector’s deadline includes recorder startup, clips the last round, and summary uses complete rounds only. `delta_j_480` is therefore a normalized estimate from covered durations, not necessarily a complete 480 s integral. Preserve partial/error rows and actual coverage; do not relabel missing seconds as observed. (`scripts/sample_quiet_predicate_evidence.py:622`; `scripts/sample_quiet_predicate_evidence.py:650`; `scripts/sample_quiet_predicate_evidence.py:956`.) |
| **Load delivered and stationary** | Join the separate load log to collection using worker identities and monotonic support. Check actual CPU delivered, calibration exclusion, drift, overruns, error and cleanup. `--load-cores` is supplied metadata, not proof that a generator ran. (`scripts/sample_quiet_predicate_evidence.py:565`; `scripts/sample_quiet_predicate_evidence.py:758`; `scripts/sample_quiet_predicate_evidence.py:818`; `scripts/sample_quiet_predicate_evidence.py:877`.) |
| **Placement represented** | QoS is the control; residency/frequency is the evidence. Do not label every background run “E-placed” or every user-initiated run “P-placed.” If the relevant placement never occurs, that part of the candidate’s evidence is missing. (`scripts/sample_quiet_predicate_evidence.py:836`; `scripts/sample_quiet_predicate_evidence.py:275`; `docs/process_traces/2026-09-18-activation-d8ca3a36/14-magistrate-adjudication-consult-06.md:10`.) |
| **Recorder/worker cleanup** | Errors, incomplete cleanup and missing power remain evidence, not successful slots. Recorder escalation explicitly leaves root-descendant termination needing bench verification. A successful top-level exit alone must not certify cleanup or admissibility. (`scripts/sample_quiet_predicate_evidence.py:433`; `scripts/sample_quiet_predicate_evidence.py:695`; `scripts/sample_quiet_predicate_evidence.py:934`.) |

“INADMISSIBLE” should mean **inadmissible for the stated clean, matched comparison**, not permission to delete the observation. High measured ΔJ is a valid adverse result; inadequate precision is inconclusive; neither is a reason to discard a run. Preserve raw evidence and exclusion reasons. (`AGENTS.md:102`; `scripts/sample_quiet_predicate_evidence.py:598`; `scripts/sample_quiet_predicate_evidence.py:1084`.)

I also disagree with “cadence affects resolution, not the integral” as an unconditional assurance. The harness correctly integrates interval-average watts against native elapsed support, but its energy bound depends on alignment and coverage. The changed cadence/anchor regime must be characterized alongside the result; it cannot inherit r6 authority merely because the nominal duration is long. (`scripts/sample_quiet_predicate_evidence.py:21`; `scripts/sample_quiet_predicate_evidence.py:227`; `TASK_QUEUE.md:865`.)

**F3 — Should fix: freeze a paired exploratory campaign, beginning with one short window.**

This answers **Q2 and the remaining part of Q5**. The following counts and timing are **design proposals**, not existing requirements.

Use injected shares **0, 0.05, 0.1, 0.2, 0.5 and 1.0**. Run each nonzero level with both existing profiles, `scalar` and `memory`, and both QoS settings. Begin with **three separated slots per level/profile/QoS combination**. These are exploratory repeats, not a claim that three observations establish a reliable tail bound. Both profiles and QoS settings already exist in the load CLI. (`scripts/sample_quiet_predicate_evidence.py:1122`.)

For each profile/QoS repeat, use an interleaved sweep:

`idle, L1, idle, L2, idle, L3, idle, L4, idle, L5, idle`

Freeze balanced permutations of the five levels across repeats; avoid putting all high loads last. Pair each load with its adjacent idle observations and retain their difference as a drift diagnostic. This implements the already-adopted requirement for fresh, same-session bracketing idle. The stock summarizer pools references across repeats within its identity groups, so its output alone is not this paired analysis. (`docs/process_traces/2026-09-18-activation-d8ca3a36/14-magistrate-adjudication-consult-06.md:11`; `scripts/sample_quiet_predicate_evidence.py:1009`.)

**Idle means the same observer plus power recorder, with no synthetic-load process.** It does not mean zero measured CPU. r6’s 25F84 idle remains historical context, not the subtraction baseline for 25G83. Record whole-round observer cost without subtraction; the harness explicitly excludes recorder CPU from that cost bracket, while total host activity still matters. (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:20`; `scripts/sample_quiet_predicate_evidence.py:620`; `docs/contracts/night_quiet_admission.md:122`.)

For honest 480 s integrals, propose **600 s collection envelopes with a predeclared interior 480 s analysis interval**, for example session-start +60 through +540 s. The campaign reducer must verify complete native support and report the relationship to the predicate’s round/ps/top intervals. If support is missing, exclude the slot from complete-integral analysis; do not slide the interval until it passes. This is a small campaign-level reduction over existing native supports, whose current implementation already exposes overlap integration and span mismatches. (`scripts/sample_quiet_predicate_evidence.py:227`; `scripts/sample_quiet_predicate_evidence.py:667`.)

Propose 600 s initial settle and 120 s stabilization after state changes, with the load established before collection and held through it. These are initial protocol allocations, supported by the earlier consult, and must be reported as such—not represented as measured thermal recovery guarantees. Generator calibration itself occupies the first five seconds. (`docs/process_traces/2026-09-18-activation-d8ca3a36/06-consult-lane-232-astra.md:33`; `scripts/sample_quiet_predicate_evidence.py:758`.)

The resulting arithmetic is:

| Quantity | Proposed count/time |
|---|---:|
| Nonzero slots | 5 levels × 2 profiles × 2 QoS × 3 repeats = **60** |
| Bracketing idle slots | 6 per sweep × 12 sweeps = **72** |
| Total analyzed slots | **132 × 480 s = 17.6 h** |
| Collection envelopes | **132 × 600 s = 22 h** |
| Initial settles | **12 × 600 s = 2 h** |
| State transitions | **12 × 10 × 120 s = 4 h** |
| Nominal campaign allocation | **28 h**, plus measured startup/cleanup/reporting allowances |

This is **twelve approximately 2 h 20 min windows**, not twelve calendar nights. Smaller complete paired blocks can run when shorter windows are available. Several windows per day are authorized when gates pass; each gets a fresh plan and handback after harvest/cleanup, with no invented daily cap. (`docs/decision_log.md:11910`; `docs/process/NIGHT_HANDBACK.md:136`; `joulewise/night_agent_install.py:39`.)

**Smallest real-number first step:** one `idle → 0.2 → idle` block, scalar/user-initiated, with actual placement reported. Three 600 s envelopes +600 s settle +240 s transitions = **44 minutes**, before operational allowances. It can be the opening block of the first sweep. Publish its provisional numbers immediately; do not wait for the full matrix.

Separate repeats across windows and, when available, across at least two authorized boots. **Do not reboot solely to obtain replication during unattended operation:** the standing machine arrangement explicitly avoids reboot because FileVault can require a person. Until another boot is available, report boot-scoped evidence and leave cross-boot robustness unestablished. (`docs/decision_log.md:10955`; `scripts/sample_quiet_predicate_evidence.py:997`.)

For each matched comparison, report:

\[
\Delta E_{480}=\int_{t}^{t+480}(P_{\text{load}}-P_{\text{paired idle}})\,dt
\]

For stationary covered averages, this reduces to `480 × (Pload − Pidle)`, matching the existing descriptive calculation. Use **CPU+GPU+ANE** as the main boundary, with individual rails and combined power as diagnostics. (`scripts/sample_quiet_predicate_evidence.py:189`; `scripts/sample_quiet_predicate_evidence.py:1025`; `docs/process_traces/2026-09-18-activation-d8ca3a36/14-magistrate-adjudication-consult-06.md:11`.)

The instrument-scale arithmetic is:

- **1 J / 480 s = 2.083 mW** mean excess.
- **5 J / 480 s = 10.417 mW**.
- Thus measured excesses of 2 mW and 20 mW correspond to **0.96 J** and **9.6 J**.

These are unit conversions, not a watts-per-core model. The ≈5 J figure is the claim clearance bar, **not a contamination allowance**. (`docs/contracts/night_quiet_admission.md:45`; `docs/decision_log.md:4801`.)

The summary must show paired ΔJ, additive alignment bounds, between-slot/window variation, clean total-busy distributions, observer cost and actual placement. It must not turn “no significant difference” into proof of safety or treat thousands of power frames as independent repeats. Existing summary bounds are systematic sums and contain **no statistical uncertainty estimate**. (`scripts/sample_quiet_predicate_evidence.py:1026`; `scripts/sample_quiet_predicate_evidence.py:1070`.)

A candidate is a **total `busy_cores` threshold**, not an injected share. It must overlap the observed clean distribution and an empirically supported safe range. If no overlap exists, say **no cutoff qualifies**. If the transition lies below 0.05, freeze a new finer exploratory grid before collecting it; do not extrapolate a candidate from this coarse grid. The negative-outcome requirement is already adopted. (`docs/contracts/night_quiet_admission.md:122`; `docs/process_traces/2026-09-18-activation-d8ca3a36/14-magistrate-adjudication-consult-06.md:12`.)

**F4 — Should fix: separate implementation authority from scientific activation.**

This answers **Q4** and states what the memo must establish before proposing a cutoff.

| Owner | Precise boundary |
|---|---|
| **Lead** | Chooses the payload implementation, decomposes work, adopts exploratory ordering/counts, prepares reviewed plans and handbacks, adjudicates findings and owns final verification. A courier summary can describe completed slots, exclusions and provisional estimates. (`docs/orchestration.md:23`; `docs/process/NIGHT_HANDBACK.md:10`.) |
| **Cold gate / rule 11** | Rules a proposed change to admission/probe obligations or other process policy; rules the scientific cutoff and any safety margin. A new NightPlan schema is a contract change, not a seat’s convenience edit. The proposed evidence-probe contract needs explicit adjudication, rather than silently waiving calibration checks. (`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:20`; `docs/process/coldgate_charter.md:29`; `docs/contracts/night_quiet_admission.md:24`.) |
| **Ed** | Retains research/methodology and hardware/access authority and the overriding NO. Existing hands-free and multi-window authorization does not require another reply for every conforming arm. New privilege configuration or a reboot requiring physical intervention returns to Ed. (`docs/orchestration.md:14`; `docs/decision_log.md:10915`; `docs/decision_log.md:10955`; `docs/decision_log.md:11910`.) |

The memo should contain, before naming a candidate:

- **PROVISIONAL / descriptive / no activation authority**, preserving the affine-model and unknown network-time-provenance qualifications.
- Exact dates, commands, reviewed head, machine/boot/build, sampler and estimator identities, plan/manifest/raw hashes, grouping keys and exclusions.
- Actual versus requested cadence, coverage and alignment bounds; load delivery/stationarity and measured placement.
- Fresh bracketing idle, whole-round observer cost, total busy-core distributions and paired joule results with uncertainty.
- The candidate’s supported operating scope, contrary evidence, precision limitations and the “no cutoff qualifies” branch.

The harness supplies some of this provenance and raw hashes, but executable identity, paired statistical analysis and the F2 gaps need explicit campaign support. (`scripts/sample_quiet_predicate_evidence.py:605`; `scripts/sample_quiet_predicate_evidence.py:617`; `scripts/sample_quiet_predicate_evidence.py:727`; `scripts/sample_quiet_predicate_evidence.py:1030`.)

**Stage A cannot authorize activation.** The adopted ruling requires Stage B null ABBA evidence at baseline, candidate and 10× candidate, with controls exposing cancellation, through the actual floor pipeline under current-epoch authority. The proposed 0.5 J bound and 20% headroom remain proposals. A mean-power difference alone does not discharge that requirement. (`docs/process_traces/2026-09-18-activation-d8ca3a36/14-magistrate-adjudication-consult-06.md:3`; `docs/process_traces/2026-09-18-activation-d8ca3a36/14-magistrate-adjudication-consult-06.md:7`; `TASK_QUEUE.md:703`.)

No numerical cutoff is supplied here because no campaign observations or resulting uncertainty bounds were acquired. The exact next step is **lead adoption of the separate v2 payload/probe design, followed by the bounded implementation and its verification, then the 44-minute first block under NIGHT_HANDBACK**.

## Residual risk

The proposed timing is a planning calculation, not measured executor performance. Unattended privilege availability, full descendant teardown and achieved E/P placement remain unverified. The power command uses noninteractive privilege elevation, and the harness explicitly records that it has not probed that policy. (`scripts/sample_quiet_predicate_evidence.py:142`; `scripts/sample_quiet_predicate_evidence.py:616`.)

Repository files remained unchanged. The 21 selected offline tests passed; no live collection or hardware validation was performed.